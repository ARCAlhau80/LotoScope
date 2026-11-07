#!/usr/bin/env python3
"""Extrai um cover específico do covers.json do Zenodo usando HTTP Range.

O arquivo tem ~4,19 GB e é ordenado por (t, k, v). O script faz busca binária
por offset, baixa apenas alguns MB e extrai o array de blocos desejado.

Uso:
  python scripts/extract_zenodo_cover.py --v 25 --k 15 --t 8 --out cover.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import List

import requests

URL = "https://zenodo.org/api/records/19735294/files/covers.json/content"
SIZE = 4_191_522_340
CHUNK = 8 * 1024 * 1024


def fetch(session: requests.Session, start: int, end: int) -> bytes:
    end = min(end, SIZE - 1)
    resp = session.get(URL, headers={"Range": f"bytes={start}-{end}"}, timeout=120)
    if resp.status_code not in (200, 206):
        raise RuntimeError(f"HTTP {resp.status_code} ao baixar range {start}-{end}")
    return resp.content


def keys_in(chunk: bytes):
    out = []
    for m in re.finditer(rb'"C\((\d+),(\d+),(\d+)\)"\s*:', chunk):
        v, k, t = int(m.group(1)), int(m.group(2)), int(m.group(3))
        out.append(((t, k, v), m.start()))
    return out


def find_key(session: requests.Session, target: tuple[int, int, int]) -> int:
    target_order = (target[2], target[1], target[0])
    key_literal = f'"C({target[0]},{target[1]},{target[2]})"'.encode()
    low, high = 0, SIZE - 1
    while low <= high:
        mid = (low + high) // 2
        start = max(0, mid - CHUNK // 2)
        end = min(SIZE - 1, mid + CHUNK // 2)
        chunk = fetch(session, start, end)
        keys = keys_in(chunk)
        if not keys:
            for factor in (2, 4, 8, 16):
                start2 = max(0, mid - (CHUNK * factor) // 2)
                end2 = min(SIZE - 1, mid + (CHUNK * factor) // 2)
                chunk = fetch(session, start2, end2)
                keys = keys_in(chunk)
                if keys:
                    start, end = start2, end2
                    break
        if not keys:
            raise RuntimeError("Nenhuma chave encontrada no chunk")
        first, last = keys[0][0], keys[-1][0]
        print(f"range {start}-{end} keys {first}..{last}", file=sys.stderr)
        if first <= target_order <= last:
            for key, pos in keys:
                if key == target_order:
                    return start + pos
            m = re.search(re.escape(key_literal) + rb"\s*:", chunk)
            if m:
                return start + m.start()
            raise RuntimeError("Alvo entre chaves, mas não encontrado no chunk")
        if target_order < first:
            high = start - 1
        else:
            low = end + 1
    raise RuntimeError("Chave não encontrada no arquivo")


def extract_value(session: requests.Session, key_pos: int, target: tuple[int, int, int]) -> List[List[int]]:
    key_literal = f'"C({target[0]},{target[1]},{target[2]})"'.encode()
    size = 2 * 1024 * 1024
    for _ in range(6):
        chunk = fetch(session, key_pos, key_pos + size)
        text = chunk.decode("utf-8", errors="ignore")
        m = re.search(re.escape(key_literal.decode()) + r"\s*:\s*", text)
        if not m:
            raise RuntimeError("Chave não encontrada no chunk de extração")
        try:
            value, _ = json.JSONDecoder().raw_decode(text[m.end():])
            return value
        except json.JSONDecodeError:
            size *= 2
    raise RuntimeError("Não foi possível extrair o valor completo")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--t", type=int, required=True)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    target = (args.v, args.k, args.t)
    session = requests.Session()
    pos = find_key(session, target)
    print(f"key_pos={pos}", file=sys.stderr)
    blocks = extract_value(session, pos, target)
    print(f"blocks={len(blocks)}", file=sys.stderr)
    out = args.out or f"c({args.v},{args.k},{args.t}).json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(blocks, f, separators=(",", ":"))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
