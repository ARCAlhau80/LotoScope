#!/usr/bin/env python3
"""
Analise de insights para melhorar a precisao da exclusao na Coluna 1 (N1).

Testa heuristicas simples + variacoes de features para entender
o que realmente funciona.
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
from sklearn.inspection import permutation_importance

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

COLUNA_ALVO = 0
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
    return [[int(r[i]) for i in range(7)] for r in rows]


def testar_heuristica(
    resultados: List[List[int]],
    fn_escolher_top3,
    inicio: int,
    fim: int,
) -> Dict:
    """
    Testa uma funcao heuristica que recebe (historico_col1, pos_atual)
    e retorna uma lista de 3 digitos (os mantidos/preditos).
    """
    hits, total = 0, 0
    col1 = [r[COLUNA_ALVO] for r in resultados]

    for pos in range(inicio, fim):
        historico = col1[:pos]
        top3 = fn_escolher_top3(historico, pos)
        if col1[pos] in top3:
            hits += 1
        total += 1

    return {"hits": hits, "total": total, "taxa": hits / total * 100 if total > 0 else 0.0}


# ── Heuristicas ─────────────────────────────────────────────

def top3_mais_frequentes(hist: List[int], pos: int, janela: int) -> List[int]:
    """Pega os 3 digitos MAIS frequentes na janela."""
    recentes = hist[-janela:]
    freq = Counter(recentes)
    return [d for d, _ in freq.most_common(3)]


def top3_menos_frequentes(hist: List[int], pos: int, janela: int) -> List[int]:
    """Pega os 3 digitos MENOS frequentes (contrarian)."""
    recentes = hist[-janela:]
    freq = Counter(recentes)
    return sorted(DIGITOS, key=lambda d: freq.get(d, 0))[:3]


def top3_maior_gap(hist: List[int], pos: int, janela: int = 0) -> List[int]:
    """Pega os 3 digitos com maior gap (ha mais tempo sem sair)."""
    n = len(hist)
    gaps = {}
    for d in DIGITOS:
        gap = n
        for j in range(n - 1, -1, -1):
            if hist[j] == d:
                gap = n - 1 - j
                break
        gaps[d] = gap
    return sorted(DIGITOS, key=lambda d: gaps[d], reverse=True)[:3]


def top3_ultimo_repetido(hist: List[int], pos: int, janela: int = 0) -> List[int]:
    """Chuta que o ultimo digito se repete + 2 aleatorios."""
    ultimo = hist[-1] if hist else 0
    outros = [d for d in DIGITOS if d != ultimo]
    rng = random.Random(pos)
    return [ultimo] + rng.sample(outros, 2)


def top3_alternancia(hist: List[int], pos: int, janela: int) -> List[int]:
    """
    Se um digito saiu no ultimo concurso, PROXIMA iteracao
    dificilmente repete (alternancia).
    Pega os 3 que NAO sairam no ultimo e sao mais frequentes na janela.
    """
    ultimo = hist[-1] if hist else -1
    recentes = hist[-janela:]
    freq = Counter(recentes)
    candidatos = [d for d in DIGITOS if d != ultimo]
    return sorted(candidatos, key=lambda d: freq.get(d, 0), reverse=True)[:3]


def top3_media_movel_ponderada(hist: List[int], pos: int, janela: int) -> List[int]:
    """
    Media movel com peso exponencial: concursos mais recentes pesam mais.
    """
    recentes = hist[-janela:]
    n = len(recentes)
    pesos = [1 + (i / n) * 2 for i in range(n)]
    score = {d: 0.0 for d in DIGITOS}
    for i, d in enumerate(recentes):
        score[d] += pesos[i]
    return sorted(DIGITOS, key=lambda d: score[d], reverse=True)[:3]


# ── Runner ──────────────────────────────────────────────────

def executar_todas_heuristicas(resultados: List[List[int]], janela_padrao: int = 100):
    """Testa todas as heuristicas em varias janelas e compara."""
    heuristicas = [
        ("Frequencia (mais comuns)", top3_mais_frequentes),
        ("Frequencia (menos comuns)", top3_menos_frequentes),
        ("Maior gap (ausentes ha mais tempo)", top3_maior_gap),
        ("Alternancia (evita ultimo)", top3_alternancia),
        ("Media movel ponderada", top3_media_movel_ponderada),
    ]

    print(f"\n{'='*90}")
    print("COMPARATIVO DE HEURISTICAS vs RANDOM FOREST")
    print(f"{'='*90}")

    from collections import OrderedDict

    resultados_dict = OrderedDict()
    n_total = len(resultados)

    for nome, fn in heuristicas:
        resultados_dict[nome] = {}
        for janela_rec in [5, 10, 15, 20, 30]:
            def make_fn(f=fn, j=janela_rec):
                return lambda h, p, j=j: f(h, p, j)
            r = testar_heuristica(resultados, make_fn(), janela_padrao, n_total)
            resultados_dict[nome][janela_rec] = r["taxa"]

    # Monta tabela
    print(f"\nHeuristica vs Janela de observacao (taxa % de acerto em manter top 3):")
    print(f"  {'Heuristica':<35}", end="")
    for j in [5, 10, 15, 20, 30]:
        print(f" {'Jan{j}':>8}", end="")
    print()

    for nome, dados in resultados_dict.items():
        print(f"  {nome:<35}", end="")
        for j in [5, 10, 15, 20, 30]:
            print(f" {dados[j]:>8.1f}", end="")
        print()

    # Melhor heuristica
    melhor_nome, melhor_valor = "", 0
    for nome, dados in resultados_dict.items():
        melhor_janela = max(dados, key=dados.get)
        if dados[melhor_janela] > melhor_valor:
            melhor_valor = dados[melhor_janela]
            melhor_nome = f"{nome} (jan={melhor_janela})"

    print(f"\n  Melhor heuristica: {melhor_nome} = {melhor_valor:.1f}%")


def analisar_feature_importance(resultados: List[List[int]], janela: int = 100):
    """Feature importance do RandomForest para entender o que mais importa."""
    print(f"\n{'='*90}")
    print("FEATURE IMPORTANCE (RandomForest, janela=100)")
    print(f"{'='*90}")

    n = len(resultados)
    col1 = [r[COLUNA_ALVO] for r in resultados]

    # Pre-computa features
    F = np.zeros((n, 40), dtype=np.float32)
    for idx in range(1, n):
        h = col1[:idx]

        freq = Counter(h)
        for d in DIGITOS:
            F[idx, d] = freq.get(d, 0) / idx

        rec = h[-20:]
        n_rec = len(rec)
        for d in DIGITOS:
            F[idx, 10 + d] = sum(1 for x in rec if x == d) / max(n_rec, 1)

        for d in DIGITOS:
            gap = idx
            for j in range(idx - 1, -1, -1):
                if h[j] == d:
                    gap = idx - 1 - j
                    break
            F[idx, 20 + d] = min(gap, idx) / idx

        F[idx, 30 + col1[idx - 1]] = 1.0

    y = np.array(col1)

    # Treina modelo final em todas as posicoes
    m = RandomForestClassifier(n_estimators=100, random_state=42)
    X_todas = F[janela:]
    y_todas = y[janela:]
    m.fit(X_todas, y_todas)

    # Feature importance nativa
    imp = m.feature_importances_
    grupos = {
        "Freq Global (0-9)": (0, 10),
        "Freq Recente 20 (10-19)": (10, 20),
        "Gap desde ultima (20-29)": (20, 30),
        "Ultimo concurso (30-39)": (30, 40),
    }

    print(f"\n  Importancia por grupo de features:")
    print(f"  {'Grupo':<35} {'Importancia':<15} {'%':<10}")
    print(f"  {'-'*60}")
    for nome, (inicio, fim) in grupos.items():
        soma = sum(imp[inicio:fim])
        print(f"  {nome:<35} {soma:.4f}        {soma*100:.1f}%")

    # Top 5 digitos individuais mais importantes (por feature)
    print(f"\n  Top 5 features individuais mais importantes:")
    idxs = np.argsort(imp)[-5:][::-1]
    nomes_feat = (
        [f"freq_global_{d}" for d in DIGITOS] +
        [f"freq_recente_{d}" for d in DIGITOS] +
        [f"gap_{d}" for d in DIGITOS] +
        [f"ultimo_{d}" for d in DIGITOS]
    )
    for i, idx in enumerate(idxs):
        print(f"    {i+1}. {nomes_feat[idx]:<20} = {imp[idx]:.4f}")


def analisar_recencia_vs_acerto(resultados: List[List[int]], janela_padrao: int = 100):
    """
    Analisa: se um digito aparece muitas vezes nos ultimos N concursos,
    qual a chance de aparecer no proximo?
    """
    print(f"\n{'='*90}")
    print("ANALISE DE RECENCIA: frequencia recente vs probabilidade de saida")
    print(f"{'='*90}")

    col1 = [r[COLUNA_ALVO] for r in resultados]
    n = len(col1)

    for janela in [3, 5, 10, 15, 20, 30]:
        acertos_por_freq: Dict[int, List[int]] = {f: [] for f in range(janela + 1)}
        acertos_por_freq_bool: Dict[int, int] = {f: 0 for f in range(janela + 1)}
        total_por_freq: Dict[int, int] = {f: 0 for f in range(janela + 1)}

        for pos in range(janela_padrao, n):
            recentes = col1[pos - janela:pos]
            digitos_futuro = col1[pos]

            for d in DIGITOS:
                freq_d = sum(1 for x in recentes if x == d)
                total_por_freq[freq_d] = total_por_freq.get(freq_d, 0) + 1
                if d == digitos_futuro:
                    acertos_por_freq_bool[freq_d] = acertos_por_freq_bool.get(freq_d, 0) + 1

        print(f"\n  Janela de recencia: {janela} concursos")
        print(f"  {'Freq':<6} {'Acertos':<10} {'Total':<10} {'Taxa':<10} {'Info':<15}")
        print(f"  {'-'*50}")
        for f in sorted(total_por_freq.keys()):
            if total_por_freq[f] == 0:
                continue
            taxa = acertos_por_freq_bool.get(f, 0) / total_por_freq[f] * 100
            baseline = 10.0  # cada digito tem 10% de chance de aparecer
            info = taxa / baseline if baseline > 0 else 0
            print(f"  {f:<6d} {acertos_por_freq_bool.get(f, 0):<10d} {total_por_freq[f]:<10d} {taxa:<10.2f} {info:<15.2f}x")


def main():
    t0 = time.time()
    resultados = carregar_resultados()
    print(f"{len(resultados)} sorteios carregados")

    col1 = [r[COLUNA_ALVO] for r in resultados]
    freq_total = Counter(col1)
    print(f"Distribuicao N1: {dict(sorted(freq_total.items()))}")
    print(f"Uniforme esperado: {len(resultados)/10:.0f}x por digito")

    JANELA_PADRAO = 100
    n = len(resultados)

    # ── 1. Comparativo heuristicas ──
    executar_todas_heuristicas(resultados, JANELA_PADRAO)

    # ── 2. Feature importance ──
    analisar_feature_importance(resultados, JANELA_PADRAO)

    # ── 3. Analise de recencia ──
    analisar_recencia_vs_acerto(resultados, JANELA_PADRAO)

    # ── 4. Teste: melhor combinação de features ──
    print(f"\n{'='*90}")
    print("TESTE: MELHOR COMBINACAO DE FEATURES")
    print(f"{'='*90}")

    configs = [
        ("So freq global (10)", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
        ("So freq recente 20 (10)", list(range(10, 20))),
        ("So gap (10)", list(range(20, 30))),
        ("So ultimo (10)", list(range(30, 40))),
        ("Global + Recente (20)", list(range(0, 20))),
        ("Global + Gap (20)", list(range(0, 10)) + list(range(20, 30))),
        ("Recente + Gap (20)", list(range(10, 30))),
        ("Todas (40)", list(range(0, 40))),
    ]

    # Pre-computa features
    F = np.zeros((n, 40), dtype=np.float32)
    for idx in range(1, n):
        h = col1[:idx]

        freq = Counter(h)
        for d in DIGITOS:
            F[idx, d] = freq.get(d, 0) / idx

        rec = h[-20:]
        n_rec = len(rec)
        for d in DIGITOS:
            F[idx, 10 + d] = sum(1 for x in rec if x == d) / max(n_rec, 1)

        for d in DIGITOS:
            gap = idx
            for j in range(idx - 1, -1, -1):
                if h[j] == d:
                    gap = idx - 1 - j
                    break
            F[idx, 20 + d] = min(gap, idx) / idx

        F[idx, 30 + col1[idx - 1]] = 1.0

    y = np.array(col1, dtype=np.int32)

    print(f"\n  {'Config':<30} {'Acertos':<10} {'Total':<10} {'Taxa':<10}")
    print(f"  {'-'*60}")
    for nome, cols in configs:
        m = RandomForestClassifier(n_estimators=100, random_state=42)
        hits, total = 0, 0
        for pos in range(JANELA_PADRAO, n):
            ti = pos - JANELA_PADRAO
            X_t = F[ti:pos][:, cols]
            y_t = y[ti:pos]
            if len(np.unique(y_t)) < 2:
                continue
            m.fit(X_t, y_t)
            probas = m.predict_proba(F[pos, cols].reshape(1, -1))[0]
            probas_c = np.zeros(10, dtype=np.float32)
            for i, cls in enumerate(m.classes_):
                if cls < 10:
                    probas_c[cls] = probas[i]
            top3 = np.argsort(probas_c)[-3:][::-1]
            if y[pos] in top3:
                hits += 1
            total += 1
        taxa = hits / total * 100 if total > 0 else 0
        print(f"  {nome:<30} {hits:<10d} {total:<10d} {taxa:<10.1f}")

    print(f"\n  Tempo total: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
