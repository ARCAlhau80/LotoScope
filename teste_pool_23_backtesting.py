# -*- coding: utf-8 -*-
"""
BACKTESTING POOL 23 - MÚLTIPLOS CONCURSOS
==========================================
Testa a estratégia em N concursos para ver taxa de sucesso
"""

import pyodbc
from itertools import combinations
from math import comb
from collections import Counter

print("="*70)
print("🧪 BACKTESTING POOL 23 - MÚLTIPLOS CONCURSOS")
print("="*70)

# Conexão
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 FROM Resultados_INT ORDER BY Concurso DESC")
rows = cursor.fetchall()

todos_resultados = []
for row in rows:
    nums = [row[i] for i in range(1, 16)]
    todos_resultados.append({
        'concurso': row[0],
        'numeros': nums,
        'set': set(nums)
    })

print(f"✅ {len(todos_resultados)} concursos carregados")

# Configuração
N_TESTES = 100  # Testar últimos 100 concursos
JANELAS = {'ultra_curta': 3, 'curta': 5, 'media': 10, 'media_longa': 15, 'longa': 30, 'ultra_longa': 100}
PESOS = {'ultra_curta': 3.0, 'curta': 2.5, 'media': 2.0, 'media_longa': 1.5, 'longa': 1.0, 'ultra_longa': 0.5}

print(f"\n📊 Testando últimos {N_TESTES} concursos...")

# Estatísticas
acertos_pool_dist = Counter()  # Quantos do resultado estão no pool
sucessos_jackpot = 0  # Vezes que pool capturou 15/15
erros_piores = []  # Quando os "piores" saíram

for i in range(N_TESTES):
    if i >= len(todos_resultados) - 130:  # Precisa de 100 anteriores + margem
        break
    
    concurso_alvo = todos_resultados[i]['concurso']
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    # Calcular frequência multi-janela
    freq_por_janela = {}
    for nome, tamanho in JANELAS.items():
        freq = Counter()
        for r in resultados_anteriores[:tamanho]:
            freq.update(r['numeros'])
        for n in freq:
            freq[n] = freq[n] / tamanho * 100
        freq_por_janela[nome] = freq
    
    # Calcular score
    scores = {}
    for n in range(1, 26):
        score = 0
        for nome, peso in PESOS.items():
            freq_pct = freq_por_janela[nome].get(n, 0)
            score += freq_pct * peso
        scores[n] = score
    
    # Identificar 2 piores
    ranking = sorted(scores.items(), key=lambda x: x[1])
    piores_2 = [ranking[0][0], ranking[1][0]]
    pool_23 = sorted([n for n in range(1, 26) if n not in piores_2])
    
    # Verificar acertos
    acertos = len(resultado_real['set'] & set(pool_23))
    acertos_pool_dist[acertos] += 1
    
    if acertos == 15:
        sucessos_jackpot += 1
    
    # Verificar se piores saíram
    piores_que_sairam = [n for n in piores_2 if n in resultado_real['set']]
    if piores_que_sairam:
        erros_piores.append({
            'concurso': concurso_alvo,
            'piores': piores_2,
            'sairam': piores_que_sairam
        })
    
    if (i + 1) % 20 == 0:
        print(f"   ... {i + 1}/{N_TESTES} concursos testados")

# ═══════════════════════════════════════════════════════════════════
# RESULTADOS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 RESULTADOS DO BACKTESTING")
print("="*70)

print(f"\n📈 DISTRIBUIÇÃO DE ACERTOS DO POOL 23:")
for ac in sorted(acertos_pool_dist.keys(), reverse=True):
    qtd = acertos_pool_dist[ac]
    pct = qtd / N_TESTES * 100
    barra = "█" * int(pct)
    status = ""
    if ac == 15: status = " ← JACKPOT GARANTIDO!"
    elif ac >= 13: status = " ← Muito bom"
    elif ac >= 11: status = " ← Bom"
    print(f"   {ac:2d}/15: {qtd:3d} ({pct:5.1f}%) {barra}{status}")

media_acertos = sum(ac * qtd for ac, qtd in acertos_pool_dist.items()) / N_TESTES
print(f"\n📊 ESTATÍSTICAS:")
print(f"   Média de acertos do Pool 23: {media_acertos:.2f}/15")
print(f"   Taxa de JACKPOT garantido (15/15): {sucessos_jackpot}/{N_TESTES} ({100*sucessos_jackpot/N_TESTES:.1f}%)")
print(f"   Taxa de 13+ acertos: {sum(qtd for ac, qtd in acertos_pool_dist.items() if ac >= 13)}/{N_TESTES}")
print(f"   Taxa de 11+ acertos: {sum(qtd for ac, qtd in acertos_pool_dist.items() if ac >= 11)}/{N_TESTES}")

print(f"\n⚠️ ERROS (piores que saíram): {len(erros_piores)}/{N_TESTES}")
if erros_piores:
    print(f"\n   Últimos 5 erros:")
    for erro in erros_piores[:5]:
        print(f"   • #{erro['concurso']}: Excluídos {erro['piores']} → Saíram {erro['sairam']}")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE COMPARATIVA: Pool 20 vs Pool 23 vs Pool 25
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 COMPARATIVO: Pool 20 vs Pool 23 vs Pool 25")
print("="*70)

# Pool 25 (todos) = sempre 15/15
# Pool 23 = calculado acima
# Pool 20 = excluir 5 piores

acertos_pool_20 = Counter()
for i in range(N_TESTES):
    if i >= len(todos_resultados) - 130:
        break
    
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    # Recalcular score
    freq_por_janela = {}
    for nome, tamanho in JANELAS.items():
        freq = Counter()
        for r in resultados_anteriores[:tamanho]:
            freq.update(r['numeros'])
        for n in freq:
            freq[n] = freq[n] / tamanho * 100
        freq_por_janela[nome] = freq
    
    scores = {}
    for n in range(1, 26):
        score = sum(freq_por_janela[nome].get(n, 0) * peso for nome, peso in PESOS.items())
        scores[n] = score
    
    ranking = sorted(scores.items(), key=lambda x: x[1])
    piores_5 = [ranking[j][0] for j in range(5)]
    pool_20 = sorted([n for n in range(1, 26) if n not in piores_5])
    
    acertos = len(resultado_real['set'] & set(pool_20))
    acertos_pool_20[acertos] += 1

media_20 = sum(ac * qtd for ac, qtd in acertos_pool_20.items()) / N_TESTES
media_23 = sum(ac * qtd for ac, qtd in acertos_pool_dist.items()) / N_TESTES
media_25 = 15.0  # Sempre 15/15

print(f"\n{'Pool':<10} {'Média':>10} {'15/15':>10} {'13+':>10} {'11+':>10} {'C(n,15)':>15}")
print("-"*65)
print(f"{'Pool 20':<10} {media_20:>10.2f} {sum(1 for ac in acertos_pool_20 if ac == 15):>10} {sum(qtd for ac, qtd in acertos_pool_20.items() if ac >= 13):>10} {sum(qtd for ac, qtd in acertos_pool_20.items() if ac >= 11):>10} {comb(20,15):>15,}")
print(f"{'Pool 23':<10} {media_23:>10.2f} {sucessos_jackpot:>10} {sum(qtd for ac, qtd in acertos_pool_dist.items() if ac >= 13):>10} {sum(qtd for ac, qtd in acertos_pool_dist.items() if ac >= 11):>10} {comb(23,15):>15,}")
print(f"{'Pool 25':<10} {media_25:>10.2f} {N_TESTES:>10} {N_TESTES:>10} {N_TESTES:>10} {comb(25,15):>15,}")

print("\n💡 CONCLUSÃO:")
print(f"   • Pool 25: Sempre garante jackpot, mas {comb(25,15):,} combinações")
print(f"   • Pool 23: {100*sucessos_jackpot/N_TESTES:.1f}% chance de jackpot, {comb(23,15):,} combinações")
print(f"   • Pool 20: {100*sum(1 for ac in acertos_pool_20 if ac == 15)/N_TESTES:.1f}% chance de jackpot, {comb(20,15):,} combinações")

cursor.close()
conn.close()

print("\n" + "="*70)
print("✅ BACKTESTING CONCLUÍDO!")
print("="*70)
