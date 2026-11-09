#!/usr/bin/env python3
"""Importa covering designs do La Jolla Coverings Repository (Zenodo).

O `covers.json` oficial tem ~4,19 GB. Baixamos em chunks paralelos (Range),
extraímos localmente apenas os designs desejados, validamos a cobertura e
mesclamos em `dashboard/src/data/covers-lotofacil.json`.

Famílias:
  --familia kuser15 (padrão)  v<=25, k<=15, v-k<=10, t<=8  -> qualquer
                              combinação de fixos/excluídos com aposta de 15.
  --all                       todo v<=25, k<=25, t<=8.

Uso:
  python dashboard/scripts/import_zenodo_covers.py --dry-run
  python dashboard/scripts/import_zenodo_covers.py
  python dashboard/scripts/import_zenodo_covers.py --all
"""
from __future__ import annotations

import argparse
import json
import mmap
import os
import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations
from math import comb
from pathlib import Path

import requests

URL = "https://zenodo.org/api/records/19735294/files/covers.json/content"
COVERDATA_URL = "https://zenodo.org/api/records/19735294/files/coverdata.json/content"
SIZE = 4_191_522_340
FONTE = "La Jolla Covering Repository (Zenodo 19735294)"

ROOT = Path(__file__).resolve().parents[2]
COVERS_TS = ROOT / "dashboard" / "src" / "data" / "covers-lotofacil.json"
TEMP = Path(os.environ.get("TEMP", "/tmp")) / "lotoscope-covers"
CACHE = TEMP / "covers.json"
META = TEMP / "coverdata.json"
PARTS = TEMP / "parts"

KEY_RE = re.compile(rb'"C\((\d+),(\d+),(\d+)\)"\s*:')


def ensure_download(url: str, dest: Path, expected: int | None, chunk_mb: int, workers: int) -> None:
    if dest.exists() and (expected is None or dest.stat().st_size == expected):
        print(f"[cache] {dest.name} ({dest.stat().st_size:,} bytes)")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    PARTS.mkdir(parents=True, exist_ok=True)
    for old in PARTS.glob("part_*"):
        old.unlink()

    if expected is None:
        # tamanho desconhecido: baixa direto (coverdata.json é pequeno)
        r = requests.get(url, timeout=300)
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"[ok] {dest.name} ({dest.stat().st_size:,} bytes)")
        return

    chunk = chunk_mb * 1024 * 1024
    ranges = [(i, min(i + chunk, expected) - 1) for i in range(0, expected, chunk)]
    print(f"[download] {dest.name}: {expected:,} bytes em {len(ranges)} chunks de {chunk_mb} MB ({workers} threads)")
    inicio = time.time()

    def baixar(idx: int) -> tuple[int, str]:
        ini, fim = ranges[idx]
        part = PARTS / f"part_{idx:05d}.bin"
        for tentativa in range(1, 4):
            try:
                resp = requests.get(
                    url,
                    headers={"Range": f"bytes={ini}-{fim}"},
                    timeout=600,
                )
                if resp.status_code not in (200, 206):
                    raise RuntimeError(f"HTTP {resp.status_code}")
                if len(resp.content) != fim - ini + 1:
                    raise RuntimeError(f"tamanho {len(resp.content)} != {fim - ini + 1}")
                part.write_bytes(resp.content)
                return idx, str(part)
            except Exception as exc:  # noqa: BLE001
                if tentativa == 3:
                    raise
                time.sleep(2 * tentativa)
        raise AssertionError("inalcançável")

    concluidos = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futuros = [pool.submit(baixar, i) for i in range(len(ranges))]
        for fut in as_completed(futuros):
            fut.result()
            concluidos += 1
            if concluidos % 10 == 0 or concluidos == len(ranges):
                pct = 100 * concluidos / len(ranges)
                vel = concluidos * chunk / max(time.time() - inicio, 1e-9) / 1024 / 1024
                print(f"  {concluidos}/{len(ranges)} chunks ({pct:5.1f}%) ~{vel:.1f} MB/s")

    with open(dest, "wb") as out:
        for idx in range(len(ranges)):
            with open(PARTS / f"part_{idx:05d}.bin", "rb") as part:
                shutil.copyfileobj(part, out, 1024 * 1024)
    for old in PARTS.glob("part_*"):
        old.unlink()
    if dest.stat().st_size != expected:
        raise RuntimeError(f"{dest} tem {dest.stat().st_size} bytes, esperado {expected}")
    print(f"[ok] {dest.name} ({dest.stat().st_size:,} bytes) em {time.time() - inicio:.0f}s")


def indexar(mm) -> dict[tuple[int, int, int], int]:
    pos: dict[tuple[int, int, int], int] = {}
    for m in KEY_RE.finditer(mm):
        v, k, t = int(m.group(1)), int(m.group(2)), int(m.group(3))
        pos[(v, k, t)] = m.end()
    return pos


def extrair_blocos(mm, inicio: int) -> list[list[int]]:
    abre = mm.find(b"[", inicio)
    if abre < 0:
        raise RuntimeError("valor sem colchete")
    depth = 0
    i = abre
    n = len(mm)
    while i < n:
        c = mm[i]
        if c == 0x5B:  # [
            depth += 1
        elif c == 0x5D:  # ]
            depth -= 1
            if depth == 0:
                return json.loads(mm[abre : i + 1])
        i += 1
    raise RuntimeError("colchete não fechado")


def validar(v: int, k: int, t: int, blocos: list[list[int]]) -> tuple[bool, int, str]:
    if len(blocos) != len({tuple(b) for b in blocos}):
        return False, 0, "blocos duplicados"
    cobertos: set[int] = set()
    for bloco in blocos:
        idx = [p - 1 for p in bloco]
        if len(idx) != k or len(set(idx)) != k or any(i < 0 or i >= v for i in idx):
            return False, 0, "bloco inválido"
        for sub in combinations(idx, t):
            mask = 0
            for x in sub:
                mask |= 1 << x
            cobertos.add(mask)
    total = comb(v, t)
    return len(cobertos) == total, len(cobertos), f"{len(cobertos)}/{total}"


def pertence_familia(v: int, k: int, t: int, todas: bool) -> bool:
    if v > 25 or k > v or k < t or t > 8:
        return False
    if todas:
        return True
    return k <= 15 and (v - k) <= 10 and t >= 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="importa todo v<=25,k<=25,t<=8")
    parser.add_argument("--dry-run", action="store_true", help="não grava o JSON")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--chunk-mb", type=int, default=32)
    args = parser.parse_args()

    ensure_download(URL, CACHE, SIZE, args.chunk_mb, args.workers)
    ensure_download(COVERDATA_URL, META, None, args.chunk_mb, args.workers)

    meta = json.loads(META.read_text(encoding="utf-8", errors="replace"))
    existentes: dict[str, dict] = json.loads(COVERS_TS.read_text(encoding="utf-8"))
    # t=3 de k=v-10 já vive em COVERS_CONHECIDOS (fechamento-combinatorio.ts)
    ts3 = {f"{v},{v - 10},3" for v in range(19, 26)}

    adicionados = 0
    blocos_total = 0
    with open(CACHE, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            posicoes = indexar(mm)
            print(f"[index] {len(posicoes)} covers no catálogo")
            for (v, k, t), inicio in sorted(posicoes.items()):
                if not pertence_familia(v, k, t, args.all):
                    continue
                chave = f"{v},{k},{t}"
                if chave in existentes or chave in ts3:
                    continue
                blocos = extrair_blocos(mm, inicio)
                if not blocos:
                    continue
                ok, _cobertos, detalhe = validar(v, k, t, blocos)
                if not ok:
                    print(f"[FALHA] C({v},{k},{t}) não cobre: {detalhe}")
                    continue
                info = meta.get(f"C({v},{k},{t})", {})
                existentes[chave] = {
                    "v": v,
                    "k": k,
                    "t": t,
                    "blocos": blocos,
                    "fonte": FONTE,
                    "limiteInferior": info.get("low_bd", 1),
                }
                adicionados += 1
                blocos_total += len(blocos)
        finally:
            mm.close()

    print(f"[resumo] +{adicionados} covers, {blocos_total:,} blocos, total {len(existentes)}")
    if args.dry_run:
        print("[dry-run] nada foi gravado")
        return 0

    with open(COVERS_TS, "w", encoding="utf-8") as out:
        json.dump(existentes, out, ensure_ascii=False)
    print(f"[ok] gravado {COVERS_TS} ({COVERS_TS.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
