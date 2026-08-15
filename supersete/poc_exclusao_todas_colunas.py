#!/usr/bin/env python3
"""
Replicacao rapida para TODAS as 7 colunas.
Usa apenas heuristicas rapidas (sem ML) + 1 coluna com RF para confirmacao.
"""

from typing import List, Dict
from collections import Counter
import sys
from pathlib import Path
import random
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from sklearn.ensemble import RandomForestClassifier

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

NUM_COLUNAS = 7
DIGITOS = list(range(10))
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)


def carregar_resultados() -> List[List[int]]:
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("SELECT N1, N2, N3, N4, N5, N6, N7 FROM Resultados_SuperSete ORDER BY Concurso")
    rows = cursor.fetchall()
    conn.close()
    return [[int(r[i]) for i in range(NUM_COLUNAS)] for r in rows]


def testar_media_ponderada(col: List[int], inicio: int, janela_rec: int = 5) -> Dict:
    hits, total = 0, 0
    for pos in range(inicio, len(col)):
        hist = col[max(0, pos - janela_rec):pos]
        n_hist = len(hist)
        if n_hist == 0:
            total += 1
            continue
        pesos = [1 + (i / n_hist) * 2 for i in range(n_hist)]
        score = {d: 0.0 for d in DIGITOS}
        for i, d in enumerate(hist):
            score[d] += pesos[i]
        top3 = sorted(DIGITOS, key=lambda d: score[d], reverse=True)[:3]
        if col[pos] in top3:
            hits += 1
        total += 1
    return {"hits": hits, "total": total, "taxa": hits / total * 100 if total > 0 else 0.0}


def testar_alternancia_freq(col: List[int], inicio: int, janela_rec: int = 15) -> Dict:
    hits, total = 0, 0
    for pos in range(inicio, len(col)):
        hist = col[:pos]
        if not hist:
            total += 1
            continue
        ultimo = hist[-1]
        recentes = hist[-janela_rec:]
        freq = Counter(recentes)
        candidatos = [d for d in DIGITOS if d != ultimo]
        top3 = sorted(candidatos, key=lambda d: freq.get(d, 0), reverse=True)[:3]
        if col[pos] in top3:
            hits += 1
        total += 1
    return {"hits": hits, "total": total, "taxa": hits / total * 100 if total > 0 else 0.0}


def testar_mais_frequentes(col: List[int], inicio: int, janela_rec: int = 5) -> Dict:
    hits, total = 0, 0
    for pos in range(inicio, len(col)):
        hist = col[max(0, pos - janela_rec):pos]
        freq = Counter(hist)
        top3 = [d for d, _ in freq.most_common(3)]
        if len(top3) < 3:
            extras = [d for d in DIGITOS if d not in top3]
            top3 += extras[:3 - len(top3)]
        if col[pos] in top3:
            hits += 1
        total += 1
    return {"hits": hits, "total": total, "taxa": hits / total * 100 if total > 0 else 0.0}


def testar_aleatorio(col: List[int], inicio: int) -> Dict:
    rng = random.Random(42)
    hits, total = 0, 0
    for pos in range(inicio, len(col)):
        if col[pos] in rng.sample(DIGITOS, 3):
            hits += 1
        total += 1
    return {"hits": hits, "total": total, "taxa": hits / total * 100 if total > 0 else 0.0}


def testar_rf_recente_rapido(col: List[int], inicio: int, janela_rec: int = 20, janela_treino: int = 100) -> Dict:
    """RF com freq recente - mais rapido com array pre-alocado."""
    n = len(col)
    hits, total = 0, 0
    m = RandomForestClassifier(n_estimators=100, random_state=42)

    for pos in range(inicio, n):
        ti = pos - janela_treino
        if ti < 0:
            continue

        X_t = np.zeros((pos - ti, 10), dtype=np.float32)
        y_t = np.zeros(pos - ti, dtype=np.int32)

        for i, t in enumerate(range(ti, pos)):
            hist = col[max(0, t - janela_rec):t]
            n_hist = len(hist)
            for d in DIGITOS:
                X_t[i, d] = sum(1 for x in hist if x == d) / max(n_hist, 1)
            y_t[i] = col[t]

        if len(np.unique(y_t)) < 2:
            continue

        m.fit(X_t, y_t)

        hist = col[max(0, pos - janela_rec):pos]
        n_hist = len(hist)
        feats = np.zeros((1, 10), dtype=np.float32)
        for d in DIGITOS:
            feats[0, d] = sum(1 for x in hist if x == d) / max(n_hist, 1)

        probas = m.predict_proba(feats)[0]
        probas_c = np.zeros(10, dtype=np.float32)
        for i, cls in enumerate(m.classes_):
            if cls < 10:
                probas_c[cls] = probas[i]
        top3 = np.argsort(probas_c)[-3:][::-1]
        if col[pos] in top3:
            hits += 1
        total += 1

    return {"hits": hits, "total": total, "taxa": hits / total * 100 if total > 0 else 0.0}


def main():
    t0 = time.time()
    resultados = carregar_resultados()
    n = len(resultados)
    inicio = 100
    print(f"{n} sorteios | Testando concursos {inicio+1}-{n} ({n-inicio} janelas)")

    cols = [([r[c] for r in resultados], f"N{c+1}") for c in range(NUM_COLUNAS)]

    estrategias_rapidas = [
        ("MediaPond(5)", lambda c, i: testar_media_ponderada(c, i, 5)),
        ("Altern+Fre(15)", lambda c, i: testar_alternancia_freq(c, i, 15)),
        ("TopFreq(5)", lambda c, i: testar_mais_frequentes(c, i, 5)),
        ("Aleatorio", lambda c, i: testar_aleatorio(c, i)),
    ]

    # ── Heuristicas rapidas ──
    print(f"\n{'Estrategia':<20}", end="")
    for _, nc in cols:
        print(f" {nc:>8}", end="")
    print(f" {'MEDIA':>8}")
    print("-" * 70)

    todos_res = {}
    for nome_est, fn in estrategias_rapidas:
        taxas = []
        for col, _ in cols:
            r = fn(col, inicio)
            taxas.append(r["taxa"])
        media = sum(taxas) / len(taxas)
        print(f"{nome_est:<20}", end="")
        for t in taxas:
            print(f" {t:>8.1f}", end="")
        print(f" {media:>8.1f}")
        todos_res[nome_est] = {"taxas": taxas, "media": media}

    # ── RF apenas na melhor coluna ──
    aleatorio_taxas = todos_res["Aleatorio"]["taxas"]
    print(f"\n--- RF FreqRecente(20) na melhor coluna (heuristicas) ---")
    melhor_col_idx = max(range(NUM_COLUNAS),
                         key=lambda i: max(t["taxas"][i] for _, t in todos_res.items() if _ != "Aleatorio") - aleatorio_taxas[i])
    melhor_col_nome = f"N{melhor_col_idx+1}"
    print(f"Coluna mais promissora: {melhor_col_nome}")

    t_rf = time.time()
    r_rf = testar_rf_recente_rapido(cols[melhor_col_idx][0], inicio)
    r_rd = testar_aleatorio(cols[melhor_col_idx][0], inicio)
    print(f"  RF FreqRecente(20): {r_rf['taxa']:.1f}% ({r_rf['hits']}/{r_rf['total']}) - {time.time()-t_rf:.1f}s")
    print(f"  Aleatorio:          {r_rd['taxa']:.1f}% ({r_rd['hits']}/{r_rd['total']})")
    print(f"  Ganho: {r_rf['taxa'] - r_rd['taxa']:+.1f}pp")

    # ── Distribuicao ──
    print(f"\nDistribuicao por coluna:")
    print(f"{'Col':<6} {'Min':<6} {'Max':<6} {'Std':<8} {'Mais freq':<20} {'Menos freq':<20}")
    print("-" * 66)
    for col, nc in cols:
        freq = Counter(col)
        mais = [d for d, _ in freq.most_common(3)]
        menos = sorted(DIGITOS, key=lambda d: freq.get(d, 0))[:3]
        std = np.std(list(freq.values()))
        print(f"{nc:<6} {min(freq.values()):<6} {max(freq.values()):<6} {std:<8.1f} {str(mais):<20} {str(menos):<20}")

    # ── Melhoria vs aleatorio ──
    print(f"\nGanho vs Aleatorio:")
    for nome_est, dados in todos_res.items():
        if nome_est == "Aleatorio":
            continue
        ganhos = [dados["taxas"][i] - aleatorio_taxas[i] for i in range(NUM_COLUNAS)]
        ganho_total = sum(ganhos) / len(ganhos)
        melhor = max(range(NUM_COLUNAS), key=lambda i: ganhos[i])
        pior = min(range(NUM_COLUNAS), key=lambda i: ganhos[i])
        print(f"  {nome_est:<20} media={ganho_total:+.1f}pp  melhor=N{melhor+1}({ganhos[melhor]:+.1f}pp)  pior=N{pior+1}({ganhos[pior]:+.1f}pp)")

    print(f"\nTempo total: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
