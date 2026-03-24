# -*- coding: utf-8 -*-
"""Análise específica: Frequência do número 1 na posição N1 por final do concurso"""

import pyodbc
import pandas as pd

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

with pyodbc.connect(CONN_STR) as conn:
    df = pd.read_sql('SELECT Concurso, N1 FROM Resultados_INT ORDER BY Concurso', conn)

df['Final'] = df['Concurso'] % 10

FINAIS_TESTE = [4, 5, 9, 8]  # Finais a analisar

print('='*70)
print('ANÁLISE: FREQUÊNCIA DO NÚMERO 1 NA POSIÇÃO N1 POR FINAL DO CONCURSO')
print(f'Testando finais: {FINAIS_TESTE}')
print('='*70)

# Análise histórico completo
print('\n📊 HISTÓRICO COMPLETO (3.632 concursos):')
print('-'*60)

stats = []
for final in range(10):
    df_f = df[df['Final'] == final]
    total = len(df_f)
    n1_count = (df_f['N1'] == 1).sum()
    pct = (n1_count / total) * 100
    outros = total - n1_count
    outros_pct = (outros / total) * 100
    stats.append({'final': final, 'total': total, 'n1': n1_count, 'pct': pct, 'outros': outros, 'outros_pct': outros_pct})

print(f"{'Final':^6} | {'Total':^7} | {'Num 1':^6} | {'% Num 1':^8} | {'Outros':^6} | {'% Outros':^9}")
print('-'*62)
for s in stats:
    marker = ' <--' if s['final'] in FINAIS_TESTE else ''
    print(f"{s['final']:^6} | {s['total']:^7} | {s['n1']:^6} | {s['pct']:^7.1f}% | {s['outros']:^6} | {s['outros_pct']:^8.1f}%{marker}")

# Média geral
media = sum(s['pct'] for s in stats) / 10
print('-'*62)
print(f"{'MÉDIA':^6} |    -    |   -    | {media:^7.1f}% |")

# Análise específica para finais testados
print(f'\n📊 COMPARAÇÃO ESPECÍFICA (finais {FINAIS_TESTE}):')
print('-'*60)
finais_grupo = [s for s in stats if s['final'] in FINAIS_TESTE]
finais_outros = [s for s in stats if s['final'] not in FINAIS_TESTE]

media_grupo = sum(s['pct'] for s in finais_grupo) / len(FINAIS_TESTE)
media_outros = sum(s['pct'] for s in finais_outros) / (10 - len(FINAIS_TESTE))

print(f'  Finais {FINAIS_TESTE}: Número 1 aparece em {media_grupo:.2f}% dos concursos')
print(f'  Outros finais: Número 1 aparece em {media_outros:.2f}% dos concursos')
print(f'  Diferença: {abs(media_grupo - media_outros):.2f} pontos percentuais')

if media_grupo < media_outros:
    print(f'\n  ✅ Finais {FINAIS_TESTE} têm MENOS número 1 (= mais números diferentes)')
else:
    print(f'\n  ❌ Finais {FINAIS_TESTE} têm MAIS ou IGUAL número 1')

# Ranking
print('\n📊 RANKING: FINAIS COM MENOS NÚMERO 1 (mais diversidade em N1):')
print('-'*60)
stats_sorted = sorted(stats, key=lambda x: x['pct'])
for i, s in enumerate(stats_sorted, 1):
    marker = ' ⭐' if s['final'] in FINAIS_TESTE else ''
    print(f"  {i}º lugar: Final {s['final']} = {s['pct']:.1f}% de número 1{marker}")

# Últimos 50 concursos
print('\n📊 ÚLTIMOS 50 CONCURSOS (janela recente):')
print('-'*60)
df_50 = df.tail(50)

stats_50 = []
for final in range(10):
    df_f = df_50[df_50['Final'] == final]
    total = len(df_f)
    if total > 0:
        n1_count = (df_f['N1'] == 1).sum()
        pct = (n1_count / total) * 100
    else:
        n1_count = 0
        pct = 0
    stats_50.append({'final': final, 'total': total, 'n1': n1_count, 'pct': pct})

print(f"{'Final':^6} | {'N conc':^7} | {'Num 1':^6} | {'% Num 1':^8}")
print('-'*40)
for s in stats_50:
    marker = ' <--' if s['final'] in FINAIS_TESTE else ''
    if s['total'] > 0:
        print(f"{s['final']:^6} | {s['total']:^7} | {s['n1']:^6} | {s['pct']:^7.1f}%{marker}")
    else:
        print(f"{s['final']:^6} | {s['total']:^7} | {'-':^6} | {'-':^8}{marker}")

finais_grupo_50 = [s for s in stats_50 if s['final'] in FINAIS_TESTE and s['total'] > 0]
finais_outros_50 = [s for s in stats_50 if s['final'] not in FINAIS_TESTE and s['total'] > 0]

if finais_grupo_50 and finais_outros_50:
    media_grupo_50 = sum(s['pct'] for s in finais_grupo_50) / len(finais_grupo_50)
    media_outros_50 = sum(s['pct'] for s in finais_outros_50) / len(finais_outros_50)
    print(f'\n  Finais {FINAIS_TESTE} (últ.50): Número 1 = {media_grupo_50:.1f}%')
    print(f'  Outros finais (últ.50): Número 1 = {media_outros_50:.1f}%')
    print(f'  Diferença: {abs(media_grupo_50 - media_outros_50):.1f} pp')

# Teste estatístico simples
from scipy import stats as scipy_stats

print('\n📊 TESTE ESTATÍSTICO (Chi-quadrado):')
print('-'*60)

# Criar tabela de contingência: Final (grupo vs outros) x N1 (1 vs outros)
grupo_teste = df[df['Final'].isin(FINAIS_TESTE)]
grupo_outros = df[~df['Final'].isin(FINAIS_TESTE)]

tabela = [
    [(grupo_teste['N1'] == 1).sum(), (grupo_teste['N1'] != 1).sum()],
    [(grupo_outros['N1'] == 1).sum(), (grupo_outros['N1'] != 1).sum()]
]

chi2, p_value, dof, expected = scipy_stats.chi2_contingency(tabela)

print(f'  Chi² = {chi2:.4f}')
print(f'  p-value = {p_value:.6f}')
print(f'  Significativo (p < 0.05)? {"✅ SIM" if p_value < 0.05 else "❌ NÃO"}')

print('\n' + '='*70)
print('CONCLUSÃO')
print('='*70)
