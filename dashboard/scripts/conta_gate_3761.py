# -*- coding: utf-8 -*-
"""
Contagem exata: combinações de 15 números (C(25,15)) com N posições
MAIORES/MENORES que a referência (concurso 3761), posição a posição.

Contagem via DP de prefixos ordenados, exata (sem amostragem).
"""
import sys
import numpy as np
import pyodbc

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

cs = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;UID=sa;PWD=LotoScope@2024;TrustServerCertificate=yes"
conn = pyodbc.connect(cs, timeout=30)
cur = conn.cursor()
cur.execute("SELECT Concurso,N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT WHERE Concurso BETWEEN 3758 AND 3762 ORDER BY Concurso")
rows = cur.fetchall()
conn.close()

data = {int(r.Concurso): [int(getattr(r, f"N{i}")) for i in range(1, 16)] for r in rows}
C25_15 = 3_268_760

for c in [3758, 3759, 3760, 3761, 3762]:
    if c in data:
        print(f"Concurso {c}: {data[c]}")

# tabela H (maiores por posição vs anterior)
print("\nH (posições maiores que o concurso anterior):")
for t in [3759, 3760, 3761, 3762]:
    H = sum(a > b for a, b in zip(data[t], data[t - 1]))
    L = sum(a < b for a, b in zip(data[t], data[t - 1]))
    E = sum(a == b for a, b in zip(data[t], data[t - 1]))
    print(f"  {t}: {H} maiores, {L} menores, {E} iguais")


def contar_por_limiar(ref, compara="menores"):
    """
    Conta combinações ordenadas de 15 de {1..25} com 'k' posições onde
    C_i < ref_i (menores) ou C_i > ref_i (maiores).
    DP[i][v][k]: prefixos de tamanho i terminando em v, com k hits.
    """
    ref = np.array(ref)
    TOTAL = 25
    M = 15
    # dp[v][k] = formas de terminar prefixo no valor v com k hits
    INF = 0
    dp = {0: {0: 1}}  # v -> {k: count} ; valor 0 = estado inicial (nenhum número escolhido)
    for i in range(1, M + 1):
        ndp = {}
        for v_prev, k_map in dp.items():
            for v in range(v_prev + 1, TOTAL - (M - i) + 1):  # espaço p/ completar
                hit = (v < ref[i - 1]) if compara == "menores" else (v > ref[i - 1])
                base = ndp.setdefault(v, {})
                for k, cnt in k_map.items():
                    nk = k + (1 if hit else 0)
                    base[nk] = base.get(nk, 0) + cnt
        dp = ndp
    total = {}
    for k_map in dp.values():
        for k, cnt in k_map.items():
            total[k] = total.get(k, 0) + cnt
    return total


ref = data[3761]
print(f"\nReferência = Concurso 3761: {ref}")
print(f"Total de combinações: {C25_15}")

for comp, label in [("menores", "MENORES que a ref. (inversão p/ baixo)"), ("maiores", "MAIORES que a ref.")]:
    dist = contar_por_limiar(ref, comp)
    print(f"\n=== {label} (posição a posição vs 3761) ===")
    print(f"{'k':>3} {'combinações':>12} {'% total':>8} {'acumulado':>10}")
    acc = 0
    for k in sorted(dist.keys()):
        acc += dist[k]
        print(f"{k:>3} {dist[k]:>12} {dist[k]/C25_15*100:>7.2f}% {acc/C25_15*100:>9.2f}%")

# thresholds específicos pedidos
print("\n=== REDUÇÃO POR GATE (ex: 11+) ===")
for comp in ["menores", "maiores"]:
    dist = contar_por_limiar(ref, comp)
    for k_lim in [8, 10, 11, 12, 13, 14]:
        n = sum(cnt for k, cnt in dist.items() if k >= k_lim)
        print(f"  {k_lim}+ {comp}: {n:>10,} combos ({n/C25_15*100:.2f}% do total)")

# o vencedor 3762 está no conjunto 11+ menores?
for comp in ["menores", "maiores"]:
    dist = contar_por_limiar(ref, comp)
    vencedor = data[3762]
    k_real = sum(a < b for a, b in zip(vencedor, ref)) if comp == "menores" else sum(a > b for a, b in zip(vencedor, ref))
    in_11 = k_real >= 11
    print(f"\n3762 vs 3761: {k_real} {comp} → gate 11+ {'CONTÉM o vencedor' if in_11 else 'NÃO contém'}")
