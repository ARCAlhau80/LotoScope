#!/usr/bin/env python3
"""
PoC: Exclusao Inteligente de Digitos - Coluna 1 do Super Sete
Versao otimizada: pre-computa features, usa RandomForest.
"""

from typing import List, Dict
from collections import Counter
import sys
from pathlib import Path
import random
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    HAS_SKLEARN = True
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn", "numpy"])
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    HAS_SKLEARN = True

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
    if not HAS_PYODBC:
        print("pyodbc nao disponivel")
        return []
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT N1, N2, N3, N4, N5, N6, N7 "
        "FROM Resultados_SuperSete ORDER BY Concurso"
    )
    rows = cursor.fetchall()
    conn.close()
    return [[int(r[i]) for i in range(7)] for r in rows]


def precomputar_features(resultados: List[List[int]]) -> np.ndarray:
    """
    Pre-computa features para cada indice (1 ate n-1).
    Feature vector: 40 floats por posicao.
    Retorna: (n, 40) onde n = len(resultados)
    """
    n = len(resultados)
    F = np.zeros((n, 40), dtype=np.float32)

    for idx in range(1, n):
        col1 = [r[COLUNA_ALVO] for r in resultados[:idx]]

        # freq global
        freq = Counter(col1)
        for d in DIGITOS:
            F[idx, d] = freq.get(d, 0) / idx

        # freq ultimos 20
        rec = col1[-20:]
        n_rec = len(rec)
        for d in DIGITOS:
            F[idx, 10 + d] = sum(1 for x in rec if x == d) / max(n_rec, 1)

        # gap
        for d in DIGITOS:
            gap = idx
            for j in range(idx - 1, -1, -1):
                if col1[j] == d:
                    gap = idx - 1 - j
                    break
            F[idx, 20 + d] = min(gap, idx) / idx

        # ultimo concurso
        F[idx, 30 + col1[-1]] = 1.0

    return F


def testar_janela(F: np.ndarray, y: np.ndarray, inicio: int, fim: int, janela: int) -> Dict:
    hits = 0
    total = 0
    historico = []

    for pos in range(inicio, fim):
        ti = pos - janela
        if ti < 0:
            continue

        X_t = F[ti:pos]
        y_t = y[ti:pos]

        if len(np.unique(y_t)) < 2:
            continue

        m = RandomForestClassifier(n_estimators=100, random_state=42)
        m.fit(X_t, y_t)

        probas = m.predict_proba(F[pos].reshape(1, -1))[0]
        probas_c = np.zeros(10, dtype=np.float32)
        for i, cls in enumerate(m.classes_):
            if cls < 10:
                probas_c[cls] = probas[i]

        top3 = np.argsort(probas_c)[-3:][::-1]
        acertou = y[pos] in top3
        if acertou:
            hits += 1
        total += 1
        historico.append(1 if acertou else 0)

    return {"hits": hits, "total": total, "taxa_acerto": hits / total * 100 if total > 0 else 0.0, "historico": historico}


def testar_aleatorio(y: np.ndarray, inicio: int, fim: int) -> Dict:
    rng = random.Random(42)
    hits, total = 0, 0
    for pos in range(inicio, fim):
        excluidos = set(rng.sample(DIGITOS, 7))
        mantidos = [d for d in DIGITOS if d not in excluidos]
        if y[pos] in mantidos:
            hits += 1
        total += 1
    return {"hits": hits, "total": total, "taxa_acerto": hits / total * 100 if total > 0 else 0.0}


def main():
    print("=" * 80)
    print("PoC: Exclusao Inteligente de Digitos - Coluna 1 (N1)")
    print("=" * 80)

    t0 = time.time()
    resultados = carregar_resultados()
    if not resultados:
        print("Nenhum resultado carregado")
        return
    print(f"\n{len(resultados)} sorteios carregados ({time.time()-t0:.1f}s)")

    t0 = time.time()
    print("Pre-computando features...")
    F = precomputar_features(resultados)
    y = np.array([r[COLUNA_ALVO] for r in resultados], dtype=np.int32)
    print(f"Features: {F.shape} ({time.time()-t0:.1f}s)")

    n = len(resultados)
    JANELAS = [50, 75, 100, 125, 150]
    JANELA_PADRAO = 100

    print(f"\nConfig:")
    print(f"  Coluna: N1 | Digitos: 0-9 | Excluir 7 -> manter top 3")
    print(f"  Modelo: RandomForest (100 arvores)")
    print(f"  Testes: concurso {JANELA_PADRAO+1} a {n} ({n - JANELA_PADRAO} janelas)\n")

    # --- Principal ---
    print("Testando RandomForest...")
    t0 = time.time()
    r_rf = testar_janela(F, y, JANELA_PADRAO, n, JANELA_PADRAO)
    print(f"  OK ({time.time()-t0:.1f}s)")

    print("Testando Aleatorio...")
    r_rd = testar_aleatorio(y, JANELA_PADRAO, n)

    # --- Resultados ---
    print(f"\n{'='*80}")
    print("RESULTADOS")
    print(f"{'='*80}")
    print(f"\n{'Estrategia':<30} {'Acertos':<10} {'Total':<10} {'Taxa':<10}")
    print(f"{'-'*60}")
    print(f"{'RandomForest':<30}{r_rf['hits']:<10}{r_rf['total']:<10}{r_rf['taxa_acerto']:.1f}%")
    print(f"{'Aleatorio':<30}{r_rd['hits']:<10}{r_rd['total']:<10}{r_rd['taxa_acerto']:.1f}%")

    bt = 30.0
    print(f"\n  Baseline teorico (3/10): {bt:.1f}%")
    print(f"  RF vs teorico:  {r_rf['taxa_acerto'] - bt:+.1f}pp")
    print(f"  Rand vs teorico: {r_rd['taxa_acerto'] - bt:+.1f}pp")

    diff = r_rf['taxa_acerto'] - r_rd['taxa_acerto']
    print(f"\n  Diferenca RF - Rand: {diff:+.1f}pp")

    # --- Multi-janela (limitado) ---
    print(f"\nAnalise multi-janela:")
    print(f"  {'Janela':<10} {'RF Acertos':<12} {'RF Taxa':<12} {'Rand Taxa':<12} {'Dif':<10}")
    print(f"  {'-'*56}")
    for j in [75, 100]:
        t0 = time.time()
        r = testar_janela(F, y, j, n, j)
        rnd = testar_aleatorio(y, j, n)
        print(f"  {j:<10d}{r['hits']:<12d}{r['taxa_acerto']:<12.1f}{rnd['taxa_acerto']:<12.1f}{r['taxa_acerto'] - rnd['taxa_acerto']:<+10.1f}  ({time.time()-t0:.1f}s)")

    # --- Detalhe final (20 concursos, usa modelo ja treinado no principal) ---
    print(f"\nDetalhe ultimos 20 concursos:")
    m_final = RandomForestClassifier(n_estimators=100, random_state=42)
    topo = n - 1
    for pos in range(max(JANELA_PADRAO, n - 20), n):
        m_final.fit(F[pos-100:pos], y[pos-100:pos])
        probas = m_final.predict_proba(F[pos].reshape(1, -1))[0]
        probas_c = np.zeros(10, dtype=np.float32)
        for i, cls in enumerate(m_final.classes_):
            if cls < 10:
                probas_c[cls] = probas[i]
        top3 = sorted(np.argsort(probas_c)[-3:][::-1])
        excluidos = [d for d in DIGITOS if d not in top3]
        acerto = "+" if y[pos] in top3 else "-"
        print(f"  Conc {pos+1:3d} | N1={y[pos]} | Top3={top3} | Excluidos={excluidos} | {acerto}")

    print(f"\n{'='*80}")
    if r_rf['taxa_acerto'] > max(r_rd['taxa_acerto'] + 1, bt + 1):
        print(">> Conclusao: Modelo CONSEGUE excluir melhor que aleatorio")
    else:
        print(">> Conclusao: Modelo NAO supera o aleatorio para coluna 1")
        print("   Sugestoes: testar outras colunas, LSTM, mais features")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
