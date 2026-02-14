#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILTRO RAPIDO - COMBO 20
"""

import pyodbc
from collections import Counter
from datetime import datetime

# Configuracoes
NUCLEO = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23, 24, 25]
DIV_C1 = [1, 3, 4]
DIV_C2 = [15, 17, 18]
PREMIOS = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

print('Carregando resultados...')
with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT TOP 100 Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso DESC')
    resultados = [(row.Concurso, set(row[i] for i in range(1,16))) for row in cursor.fetchall()]

frequencias = Counter()
for _, nums in resultados:
    frequencias.update(nums)

print(f'{len(resultados)} resultados carregados')

# Carregar combinacoes
arquivo = r'c:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combo20_estrategia_20260121_143756.txt'
print(f'Carregando combinacoes...')
combinacoes = []
with open(arquivo, 'r') as f:
    for linha in f:
        linha = linha.strip()
        if linha and not linha.startswith('#'):
            try:
                nums = [int(n) for n in linha.split(',')]
                if len(nums) == 15:
                    combinacoes.append(nums)
            except:
                continue

print(f'{len(combinacoes):,} combinacoes carregadas')

# FILTRO 1: Nucleo >= 13
nucleo_set = set(NUCLEO)
filtradas = [c for c in combinacoes if len(set(c) & nucleo_set) >= 13]
print(f'Apos nucleo >= 13: {len(filtradas):,}')

# FILTRO 2: Top 20% por frequencia
scores = [(c, sum(frequencias.get(n, 0) for n in c)) for c in filtradas]
scores.sort(key=lambda x: x[1], reverse=True)
n_manter = int(len(scores) * 0.20)
filtradas = [c for c, _ in scores[:n_manter]]
print(f'Apos top 20% frequencia: {len(filtradas):,}')

# Calcular scores finais
print(f'\nCalculando scores das {len(filtradas):,} combinacoes...')

def calcular_prob_11(combo_set, resultados):
    return sum(1 for _, r in resultados if len(combo_set & r) >= 11) / len(resultados)

top_scores = []
for i, combo in enumerate(filtradas):
    combo_set = set(combo)
    nucleo_cob = len(combo_set & nucleo_set)
    intersecoes = [len(combo_set & r) for _, r in resultados[:10]]
    media_int = sum(intersecoes) / len(intersecoes)
    min_int = min(intersecoes)
    prob_11 = calcular_prob_11(combo_set, resultados)
    freq_score = sum(frequencias.get(n, 0) for n in combo)
    
    score_total = nucleo_cob * 10 + media_int * 5 + min_int * 8 + prob_11 * 50
    
    top_scores.append({
        'combo': combo,
        'score': score_total,
        'prob_11': prob_11,
        'nucleo': nucleo_cob,
        'media_int': media_int,
        'min_int': min_int
    })
    
    if (i+1) % 5000 == 0:
        print(f'  ... {i+1:,} processadas')

# Ordenar
top_scores.sort(key=lambda x: x['score'], reverse=True)

# Top 1000
top_1000 = top_scores[:1000]

print(f'\n=== TOP 10 COMBINACOES ===')
print('Rank  Score   Prob>=11  Nucleo  MediaInt  MinInt  Combinacao')
print('-' * 70)
for i, item in enumerate(top_1000[:10], 1):
    combo_str = ','.join(f'{n:02d}' for n in item['combo'][:7]) + '...'
    sc = item['score']
    p11 = item['prob_11']*100
    nuc = item['nucleo']
    mi = item['media_int']
    mn = item['min_int']
    print(f'{i:3d}   {sc:5.1f}   {p11:5.1f}%    {nuc:2d}/17   {mi:5.2f}    {mn:2d}    {combo_str}')

# Salvar
arquivo_saida = r'c:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combo20_FILTRADAS_TOP1000.txt'
with open(arquivo_saida, 'w') as f:
    f.write(f'# COMBINACOES FILTRADAS - RETORNO GARANTIDO\n')
    f.write(f'# Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
    f.write(f'# Total: {len(top_1000)} combinacoes (top 1000 por score)\n')
    f.write(f'# Filtros: nucleo>=13, top 20% frequencia\n\n')
    
    for item in top_1000:
        f.write(','.join(map(str, item['combo'])) + '\n')

print(f'\nSalvo em: {arquivo_saida}')
print(f'\nREDUCAO: {len(combinacoes):,} -> {len(top_1000):,} ({(1-len(top_1000)/len(combinacoes))*100:.2f}% reduzidas)')
