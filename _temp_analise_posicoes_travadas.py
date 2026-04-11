#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análise temporária: Posições Travadas - insight do heatmap"""

import pyodbc
import numpy as np
from collections import Counter

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()
cursor.execute('SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso ASC')
rows = cursor.fetchall()
conn.close()

concursos = [r[0] for r in rows]
data = []
for r in rows:
    data.append([r[p] for p in range(1, 16)])
data = np.array(data)
T = len(data)

# ============================================
# ANÁLISE 8: Estabilidade temporal do sinal
# ============================================
print("ANALISE 8: ESTABILIDADE DO SINAL — Recente vs Antigo")
print("=" * 65)
print(f"{'Pos':>4} | {'Ult 500':>8} | {'Ant 500':>8} | {'Total':>8} | {'Ganho':>6} | Estável?")
print("-" * 65)

for pos in range(15):
    results = {}
    for label, start, end in [('ult500', T - 500, T), ('ant500', T - 1000, T - 500), ('total', 3, T)]:
        locked_c, locked_h = 0, 0
        for i in range(max(3, start), end):
            w = [data[i - 1, pos], data[i - 2, pos], data[i - 3, pos]]
            c = Counter(w)
            best, bcnt = c.most_common(1)[0]
            if bcnt == 3:
                locked_c += 1
                if best == data[i, pos]:
                    locked_h += 1
        results[label] = locked_h / locked_c * 100 if locked_c > 0 else 0

    diff = abs(results['ult500'] - results['ant500'])
    stab = "SIM" if diff < 8 else "NAO"

    # Baseline sem lock
    bl_c, bl_h = 0, 0
    for i in range(3, T):
        w = [data[i - 1, pos], data[i - 2, pos], data[i - 3, pos]]
        c = Counter(w)
        best, bcnt = c.most_common(1)[0]
        if bcnt < 3:
            bl_c += 1
            if best == data[i, pos]:
                bl_h += 1
    bl = bl_h / bl_c * 100 if bl_c > 0 else 0
    gain = results['total'] - bl
    print(f"N{pos+1:2d}  | {results['ult500']:6.1f}%  | {results['ant500']:6.1f}%  | {results['total']:6.1f}%  | {gain:+5.1f}pp | {stab}")

# ============================================
# ANÁLISE 9: Estado atual para C3658
# ============================================
print()
print("=" * 65)
print(f"ESTADO ATUAL: Posições para C{concursos[-1]+1} (baseado nos 3 últimos)")
print("=" * 65)
print(f"Concursos: C{concursos[-3]}, C{concursos[-2]}, C{concursos[-1]}")
print()

for pos in range(15):
    w = [data[-1, pos], data[-2, pos], data[-3, pos]]
    c = Counter(w)
    best, bcnt = c.most_common(1)[0]
    if bcnt == 3:
        status = f"TRAVADA 100% → {best}"
        emoji = " <=== FORTE"
    elif bcnt == 2:
        other = [x for x in w if x != best][0]
        status = f"SEMI 67% → {best} (ou {other})"
        emoji = ""
    else:
        status = f"DISPERSA ({w[0]}, {w[1]}, {w[2]})"
        emoji = ""
    print(f"N{pos+1:2d}: {str(w):20s}  {status}{emoji}")

# ============================================
# ANÁLISE 10: Impacto como FILTRO no Pool 23
# ============================================
print()
print("=" * 65)
print("ANALISE 10: SIMULAÇÃO DE FILTRO 'POSIÇÕES TRAVADAS' NO POOL 23")
print("=" * 65)

# Para cada concurso nos últimos 200, simular:
# 1. Gerar template das 3 anteriores
# 2. Para cada resultado real: contar violações nas posições com ganho > 5pp
# 3. Comparar: com filtro tol=2 vs sem filtro → muda taxa de jackpot?

# Posições "fortes" (ganho > 5pp na análise 3): N1, N2, N6, N9, N12, N14, N15
POS_FORTES = [0, 1, 5, 8, 11, 13, 14]  # 0-indexed

print(f"Posições monitoradas: {['N'+str(p+1) for p in POS_FORTES]}")

# Teste: últimos 500 concursos
violacoes_hist = []
for i in range(max(3, T - 500), T):
    v_count = 0
    for pos in POS_FORTES:
        w = [data[i - 1, pos], data[i - 2, pos], data[i - 3, pos]]
        c = Counter(w)
        best, bcnt = c.most_common(1)[0]
        if bcnt >= 2 and best != data[i, pos]:
            v_count += 1
    violacoes_hist.append(v_count)

violacoes_hist = np.array(violacoes_hist)
print(f"\nDistribuição de violações (últimos 500 concursos):")
for v in range(8):
    cnt = np.sum(violacoes_hist == v)
    pct = cnt / len(violacoes_hist) * 100
    if cnt > 0:
        print(f"  {v} violações: {cnt:4d} ({pct:5.1f}%)")

print(f"\nCobertura por tolerância:")
for tol in range(8):
    pct = np.sum(violacoes_hist <= tol) / len(violacoes_hist) * 100
    tag = " ← RECOMENDADO" if tol == 3 else ""
    print(f"  Tolerância {tol}: {pct:5.1f}% dos concursos reais passam{tag}")

# Comparar com tolerância fixa para ver se melhora overlap
print(f"\nCorrelação: violações baixas → mais acertos posicionais?")
for v_max in [0, 1, 2, 3, 4, 5, 6, 7]:
    mask = violacoes_hist == v_max
    if mask.sum() == 0:
        continue
    # Para esses concursos, calcular overlap do template
    idx_list = [i for i in range(max(3, T - 500), T) if violacoes_hist[i - max(3, T - 500)] == v_max]
    ov_list = []
    for i in idx_list:
        templ = []
        for pos in range(15):
            w = [data[i - 1, pos], data[i - 2, pos], data[i - 3, pos]]
            c = Counter(w)
            templ.append(c.most_common(1)[0][0])
        ov = sum(1 for p in range(15) if data[i, p] == templ[p])
        ov_list.append(ov)
    print(f"  {v_max} violações: overlap médio = {np.mean(ov_list):.2f}/15 (n={len(ov_list)})")
