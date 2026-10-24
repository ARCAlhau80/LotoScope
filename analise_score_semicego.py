# -*- coding: utf-8 -*-
"""
Experimento semi-cego: o ranking por score tem sinal preditivo?

Desenho
-------
Para cada concurso alvo T (sorteio real) e seu anterior P ("se fosse o atual"):
  1. Sorteiam-se 5 dezenas de T (5 acertos garantidos, so para reduzir o espaco).
  2. Universo = todas as C(20,10) = 184.756 combinacoes que contem essas 5 fixas.
  3. Cada combinacao e pontuada usando SOMENTE informacao ate P (nunca T).
  4. Ordena-se o universo por score (melhor primeiro).
  5. Mede-se onde os premios (11/12/13/14/15 acertos) caem no ranking.

Nulo correto
------------
Fixar 5 dezenas de T induz, por flutuacao amostral, uma relacao artificial entre
"repeticao de P" e acerto (as 5 fixas removem mais/menos dezenas de T que estavam em P).
Para separar sinal de artefato, o MESMO pipeline roda com um alvo embaralhado T'
(um outro concurso qualquer, independente de P), preservando marginais e o look-ahead
dos 5 fixos. Se o observado nao bate o nulo, nao ha sinal.

Uso:
  python analise_score_semicego.py --contests 1200
  python analise_score_semicego.py --contests 3700 --json dados/analise_score_semicego.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Lotofacil;"
    "Trusted_Connection=yes;"
)

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
N_NUM = 25
N_FIXOS = 5
N_ESCOLHA = 10
N_HITS_MIN = N_FIXOS
N_UNIVERSO = 184756

VARIANTS = ("aleatorio", "repeticao", "quentes50", "frios50", "estrutural", "combinado")
W_HOT = 50
W_ESTRUT = 200


def load_draws() -> tuple[list[int], np.ndarray]:
    with pyodbc.connect(CONN_STR, timeout=15) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
        )
        concursos: list[int] = []
        rows: list[list[int]] = []
        for row in cur.fetchall():
            concursos.append(int(row[0]))
            rows.append([int(x) for x in row[1:16]])
    presence = np.zeros((len(rows), N_NUM), dtype=np.int8)
    for i, dezenas in enumerate(rows):
        presence[i, np.asarray(dezenas) - 1] = 1
    return concursos, presence


def build_universe() -> np.ndarray:
    combos = np.asarray(list(itertools.combinations(range(20), N_ESCOLHA)), dtype=np.int16)
    mat = np.zeros((combos.shape[0], 20), dtype=np.float32)
    mat[np.arange(combos.shape[0])[:, None], combos] = 1.0
    assert mat.shape == (N_UNIVERSO, 20)
    return mat


def longest_true_run(mask: np.ndarray) -> int:
    if not mask.any():
        return 0
    d = np.diff(np.concatenate(([0], mask.astype(np.int8), [0])))
    starts = np.flatnonzero(d == 1)
    ends = np.flatnonzero(d == -1)
    return int((ends - starts).max())


def max_window(prize_mask: np.ndarray, width: int = 10) -> tuple[int, int]:
    win = np.convolve(prize_mask.astype(np.int32), np.ones(width, dtype=np.int32), "valid")
    pos = int(win.argmax())
    return int(win[pos]), pos


def rolling_stats(x: np.ndarray, i: int, w: int) -> tuple[float, float]:
    lo = max(0, i - w)
    chunk = x[lo:i]
    if chunk.size == 0:
        return 0.0, 1.0
    return float(chunk.mean()), float(chunk.std() + 1e-9)


def new_acc() -> dict[str, list]:
    return {
        "top10": [], "top25": [], "top50": [], "top100": [], "top500": [], "top1000": [],
        "bottom10": [], "bottom100": [],
        "p11_top10": [], "p12_top10": [], "p13_top10": [], "p11_top100": [], "p12_top100": [],
        "max10_11": [], "max10_12": [], "max10_13": [],
        "argmax10_11": [], "run11": [],
        "win_ge7": [], "win_ge8": [],
        "pct15": [], "pct14": [], "pct13": [],
        "corr": [],
        "dec_mean": [], "dec_p11": [], "dec_p12": [],
        "block_mean": [], "block_p11": [],
    }


def analyze_target(
    M: np.ndarray,
    target: np.ndarray,
    prev: np.ndarray,
    fixed_seed: int,
    sample: np.ndarray,
    *,
    hot_full: np.ndarray,
    mu_s: float, sd_s: float,
    mu_p: float, sd_p: float,
    mu_pr: float, sd_pr: float,
    even: np.ndarray,
    prime: np.ndarray,
    jitter: np.ndarray,
) -> dict[str, dict[str, float]]:
    fixed = np.random.default_rng(fixed_seed).choice(np.flatnonzero(target), N_FIXOS, replace=False)
    rest = np.setdiff1d(np.arange(N_NUM), fixed)
    t_ind = target[rest].astype(np.float32)
    prev_ind = prev[rest].astype(np.float32)

    hot = hot_full[rest].astype(np.float32)
    hot_z = (hot - hot.mean()) / (hot.std() + 1e-9)
    rest_f = rest.astype(np.float32)
    estrutural = -(
        np.abs(M @ rest_f - mu_s) / sd_s
        + np.abs(M @ even[rest] - mu_p) / sd_p
        + np.abs(M @ prime[rest] - mu_pr) / sd_pr
    )

    hits = N_HITS_MIN + np.rint(M @ t_ind).astype(np.int8)
    n = hits.size

    scores = {
        "aleatorio": jitter,
        "repeticao": (M @ prev_ind) + jitter,
        "quentes50": (M @ hot) + jitter,
        "frios50": -(M @ hot) + jitter,
        "estrutural": estrutural + jitter,
        "combinado": (M @ (0.6 * hot_z + 0.8 * prev_ind)) + 0.25 * estrutural + jitter,
    }

    out: dict[str, dict[str, float]] = {}
    for variant, score in scores.items():
        order = np.argsort(-score, kind="stable")
        h = hits[order]
        r: dict[str, float] = {}

        for k in (10, 25, 50, 100, 500, 1000):
            r[f"top{k}"] = float(h[:k].mean())
        r["bottom10"] = float(h[-10:].mean())
        r["bottom100"] = float(h[-100:].mean())

        for lvl in (11, 12, 13):
            b = h >= lvl
            r[f"p{lvl}_top10"] = int(b[:10].sum())
            if lvl in (11, 12):
                r[f"p{lvl}_top100"] = int(b[:100].sum())
            if lvl == 11:
                m, pos = max_window(b)
                r["max10_11"] = m
                r["argmax10_11"] = pos / max(1, b.size - 10)
                r["run11"] = longest_true_run(b)
                r["win_ge7"] = int((np.convolve(b.astype(np.int32), np.ones(10, np.int32), "valid") >= 7).sum())
                r["win_ge8"] = int((np.convolve(b.astype(np.int32), np.ones(10, np.int32), "valid") >= 8).sum())
            elif lvl == 12:
                r["max10_12"] = max_window(b)[0]
            else:
                r["max10_13"] = max_window(b)[0]

        r["pct15"] = float(np.flatnonzero(h == 15)[0]) / (n - 1)
        r["pct14"] = float(np.flatnonzero(h >= 14).mean()) / (n - 1)
        r["pct13"] = float(np.flatnonzero(h >= 13).mean()) / (n - 1)

        rank = np.empty(n, dtype=np.float32)
        rank[order] = np.arange(n, dtype=np.float32)
        r["corr"] = float(-np.corrcoef(rank[sample], hits[sample].astype(np.float32))[0, 1])

        decs = np.array_split(h, 10)
        r["dec_mean"] = [float(d.mean()) for d in decs]
        r["dec_p11"] = [float((d >= 11).mean()) for d in decs]
        r["dec_p12"] = [float((d >= 12).mean()) for d in decs]

        blocks = np.array_split(h, 19)
        r["block_mean"] = [float(b.mean()) for b in blocks]
        r["block_p11"] = [float((b >= 11).mean()) for b in blocks]
        out[variant] = r
    return out


def aggregate(acc: dict[str, dict[str, list]], variant: str, n_tests: int) -> dict:
    def a(key):
        return np.asarray(acc[variant][key], dtype=np.float64)

    r = {
        "top10": float(a("top10").mean()),
        "top10_se": float(a("top10").std(ddof=1) / math.sqrt(n_tests)),
        "top25": float(a("top25").mean()),
        "top50": float(a("top50").mean()),
        "top100": float(a("top100").mean()),
        "top500": float(a("top500").mean()),
        "top1000": float(a("top1000").mean()),
        "bottom10": float(a("bottom10").mean()),
        "bottom100": float(a("bottom100").mean()),
        "p11_top10": float(a("p11_top10").mean()),
        "p12_top10": float(a("p12_top10").mean()),
        "p13_top10": float(a("p13_top10").mean()),
        "p11_top100": float(a("p11_top100").mean()),
        "p12_top100": float(a("p12_top100").mean()),
        "max10_11": float(a("max10_11").mean()),
        "max10_12": float(a("max10_12").mean()),
        "max10_13": float(a("max10_13").mean()),
        "argmax10_11": float(a("argmax10_11").mean()),
        "run11": float(a("run11").mean()),
        "win_ge7": float(a("win_ge7").mean()),
        "win_ge8": float(a("win_ge8").mean()),
        "pct15": float(a("pct15").mean()),
        "pct15_z": float((a("pct15").mean() - 0.5) / (a("pct15").std(ddof=1) / math.sqrt(n_tests))),
        "pct14": float(a("pct14").mean()),
        "pct14_z": float((a("pct14").mean() - 0.5) / (a("pct14").std(ddof=1) / math.sqrt(n_tests))),
        "pct13": float(a("pct13").mean()),
        "pct13_z": float((a("pct13").mean() - 0.5) / (a("pct13").std(ddof=1) / math.sqrt(n_tests))),
        "corr": float(a("corr").mean()),
        "corr_z": float(a("corr").mean() / (a("corr").std(ddof=1) / math.sqrt(n_tests))),
        "dec_mean": np.asarray(acc[variant]["dec_mean"]).mean(axis=0).round(4).tolist(),
        "dec_p11": np.asarray(acc[variant]["dec_p11"]).mean(axis=0).round(4).tolist(),
        "dec_p12": np.asarray(acc[variant]["dec_p12"]).mean(axis=0).round(4).tolist(),
        "block_mean": np.asarray(acc[variant]["block_mean"]).mean(axis=0).round(4).tolist(),
        "block_p11": np.asarray(acc[variant]["block_p11"]).mean(axis=0).round(4).tolist(),
    }
    return r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contests", type=int, default=1200)
    ap.add_argument("--start", type=int, default=250)
    ap.add_argument("--json", type=str, default="")
    ap.add_argument("--seed", type=int, default=20261024)
    ap.add_argument("--no-null", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    concursos, draws = load_draws()
    n_total = len(draws)
    print(f"Base: {n_total} concursos ({concursos[0]}..{concursos[-1]})")

    print("Construindo universo C(20,10)...")
    M = build_universe()

    freq_cum = np.vstack([np.zeros((1, N_NUM), dtype=np.int32), np.cumsum(draws, axis=0, dtype=np.int32)])
    valores = np.arange(1, N_NUM + 1, dtype=np.float32)
    even = (valores % 2 == 0).astype(np.float32)
    prime = np.isin(valores.astype(int), list(PRIMOS)).astype(np.float32)
    soma_draw = draws.astype(np.float32) @ valores
    pares_draw = draws.astype(np.float32) @ even
    primos_draw = draws.astype(np.float32) @ prime

    k = np.arange(11)
    contagens_k = np.array([math.comb(10, kk) * math.comb(10, 10 - kk) for kk in k], dtype=np.int64)
    assert contagens_k.sum() == N_UNIVERSO
    hits_universo = np.repeat((N_HITS_MIN + k).astype(np.int8), contagens_k)
    p11 = float((hits_universo >= 11).mean())
    p12 = float((hits_universo >= 12).mean())
    p13 = float((hits_universo >= 13).mean())
    print(f"Universo: p(>=11)={p11:.4f}  p(>=12)={p12:.4f}  p(>=13)={p13:.4f}")

    start = max(args.start, W_ESTRUT + 1)
    stop = min(n_total, start + args.contests)
    n_tests = stop - start
    idxs = list(range(start, stop))
    print(f"Rodando {n_tests} concursos alvo ({concursos[start]}..{concursos[stop-1]}) x {len(VARIANTS)} scores")

    rng_null = np.random.default_rng(args.seed + 12345)
    null_targets: dict[int, int] = {}
    for idx in idxs:
        while True:
            cand = int(rng_null.integers(0, n_total))
            if abs(cand - idx) > 300:
                null_targets[idx] = cand
                break
    print("Nulo: alvo embaralhado (outro concurso independente de P), mesmo pipeline.")

    sample = np.random.default_rng(args.seed + 999).choice(N_UNIVERSO, 20000, replace=False)
    acc_obs = {v: new_acc() for v in VARIANTS}
    acc_null = {v: new_acc() for v in VARIANTS}

    t_loop = time.time()
    for pos, idx in enumerate(idxs):
        prev = draws[idx - 1] > 0
        target = draws[idx] > 0
        target_null = draws[null_targets[idx]] > 0

        hot_full = (freq_cum[idx] - freq_cum[max(0, idx - W_HOT)]).astype(np.float32)
        mu_s, sd_s = rolling_stats(soma_draw, idx, W_ESTRUT)
        mu_p, sd_p = rolling_stats(pares_draw, idx, W_ESTRUT)
        mu_pr, sd_pr = rolling_stats(primos_draw, idx, W_ESTRUT)
        jitter = np.random.default_rng(args.seed * 31 + idx).random(N_UNIVERSO, dtype=np.float32)

        for seed_off, tgt, acc in ((0, target, acc_obs), (777777, target_null, acc_null)):
            res = analyze_target(
                M, tgt, prev, args.seed + idx + seed_off, sample,
                hot_full=hot_full, mu_s=mu_s, sd_s=sd_s, mu_p=mu_p, sd_p=sd_p,
                mu_pr=mu_pr, sd_pr=sd_pr, even=even, prime=prime, jitter=jitter,
            )
            for v in VARIANTS:
                for key, val in res[v].items():
                    acc[v][key].append(val)

        if (pos + 1) % 100 == 0 or pos + 1 == n_tests:
            el = time.time() - t_loop
            eta = el / (pos + 1) * (n_tests - pos - 1)
            print(f"  {pos+1}/{n_tests}  {concursos[idx]}  {el:.0f}s  ETA {eta:.0f}s")

    report: dict = {
        "meta": {
            "n_concursos": n_tests,
            "concurso_ini": int(concursos[start]),
            "concurso_fim": int(concursos[stop - 1]),
            "universo": N_UNIVERSO,
            "fixos": N_FIXOS,
            "p11": p11, "p12": p12, "p13": p13,
            "null": "alvo embaralhado (outro concurso), mesmo pipeline",
            "elapsed_s": round(time.time() - t0, 1),
        },
        "observed": {}, "null": {}, "delta": {},
    }

    for v in VARIANTS:
        o = aggregate(acc_obs, v, n_tests)
        nu = {} if args.no_null else aggregate(acc_null, v, n_tests)
        report["observed"][v] = o
        report["null"][v] = nu
        if not args.no_null:
            d = {}
            for key in ("top10", "top25", "top50", "top100", "top500", "top1000",
                        "bottom10", "bottom100", "p11_top10", "p12_top10", "p13_top10",
                        "p11_top100", "p12_top100", "max10_11", "run11",
                        "win_ge7", "win_ge8", "pct15", "pct14", "pct13", "corr",
                        "argmax10_11"):
                d[key] = float(o[key] - nu[key])
            dv = float((np.asarray(acc_obs[v]["top10"]) - np.asarray(acc_null[v]["top10"])).mean())
            ds = float((np.asarray(acc_obs[v]["top10"]) - np.asarray(acc_null[v]["top10"])).std(ddof=1) / math.sqrt(n_tests))
            d["top10_delta"] = dv
            d["top10_delta_se"] = ds
            d["top10_delta_z"] = float(dv / ds) if ds > 0 else 0.0
            pair15 = np.asarray(acc_obs[v]["pct15"]) - np.asarray(acc_null[v]["pct15"])
            d["pct15_delta"] = float(pair15.mean())
            d["pct15_delta_se"] = float(pair15.std(ddof=1) / math.sqrt(n_tests))
            d["pct15_delta_z"] = float(pair15.mean() / d["pct15_delta_se"]) if d["pct15_delta_se"] else 0.0
            paircorr = np.asarray(acc_obs[v]["corr"]) - np.asarray(acc_null[v]["corr"])
            d["corr_delta"] = float(paircorr.mean())
            d["corr_delta_z"] = float(paircorr.mean() / (paircorr.std(ddof=1) / math.sqrt(n_tests)))
            report["delta"][v] = d

    # ---------------- relatorio ----------------
    print("\n" + "=" * 96)
    print("OBSERVADO vs NULO (nulo = mesmo pipeline com alvo de outro concurso)")
    print("Nulo teorico de acertos por faixa = 10.000 | p(>=11) = 0.328")
    print("=" * 96)
    hdr = (f"{'variante':<12} {'top10':>7} {'nulo':>7} {'z_delta':>8} | "
           f"{'top100':>7} {'top1k':>7} {'bottom10':>8} | {'p11/10':>7} {'p12/10':>7} | "
           f"{'corr':>7} {'z':>6} | {'%15':>6} {'z':>6}")
    print(hdr)
    for v in VARIANTS:
        o = report["observed"][v]
        nv = report["null"][v]
        d = report["delta"][v]
        print(f"{v:<12} {o['top10']:7.3f} {nv['top10']:7.3f} {d['top10_delta_z']:8.2f} | "
              f"{o['top100']:7.3f} {o['top1000']:7.3f} {o['bottom10']:8.3f} | "
              f"{o['p11_top10']:7.3f} {o['p12_top10']:7.3f} | "
              f"{o['corr']:7.4f} {o['corr_z']:6.2f} | {o['pct15']:6.3f} {o['pct15_z']:6.2f}")

    print("\nNulo - mesmas colunas (para comparar):")
    for v in VARIANTS:
        nv = report["null"][v]
        print(f"{v:<12} {nv['top10']:7.3f} {'':7} {'':8} | {nv['top100']:7.3f} {nv['top1000']:7.3f} "
              f"{nv['bottom10']:8.3f} | {nv['p11_top10']:7.3f} {nv['p12_top10']:7.3f} | "
              f"{nv['corr']:7.4f} {nv['corr_z']:6.2f} | {nv['pct15']:6.3f} {nv['pct15_z']:6.2f}")

    print("\nPercentil do premio de 15 acertos (0=topo, 1=fim) - obs vs nulo:")
    for v in VARIANTS:
        o, nv, d = report["observed"][v], report["null"][v], report["delta"][v]
        print(f"  {v:<12} obs={o['pct15']:.4f} nulo={nv['pct15']:.4f} "
              f"delta={d['pct15_delta']:+.4f} (z={d['pct15_delta_z']:+.2f}) | "
              f"pct14 obs={o['pct14']:.4f} nulo={nv['pct14']:.4f} | "
              f"pct13 obs={o['pct13']:.4f} nulo={nv['pct13']:.4f}")

    print("\nDecis (media de acertos 1o..10o decil) - obs | nulo:")
    for v in VARIANTS:
        o, nv = report["observed"][v]["dec_mean"], report["null"][v]["dec_mean"]
        print(f"  {v:<12} obs " + " ".join(f"{x:5.2f}" for x in o))
        print(f"  {'':<12} nul " + " ".join(f"{x:5.2f}" for x in nv))

    print("\nBlocos de 10 nao sobrepostos (19 blocos) - media de acertos obs | nulo:")
    for v in VARIANTS:
        o, nv = report["observed"][v]["block_mean"], report["null"][v]["block_mean"]
        print(f"  {v:<12} obs " + " ".join(f"{x:5.2f}" for x in o))
        print(f"  {'':<12} nul " + " ".join(f"{x:5.2f}" for x in nv))

    print("\nClustering (por concurso): max janela 10 | run de premios | janelas com >=7/10:")
    for v in VARIANTS:
        o, nv = report["observed"][v], report["null"][v]
        print(f"  {v:<12} obs max10={o['max10_11']:.2f} run11={o['run11']:.1f} "
              f"win7={o['win_ge7']:.1f} win8={o['win_ge8']:.1f} | "
              f"nulo max10={nv['max10_11']:.2f} run11={nv['run11']:.1f} "
              f"win7={nv['win_ge7']:.1f} win8={nv['win_ge8']:.1f}")

    print(f"\nTempo total: {time.time()-t0:.1f}s")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON salvo em {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
