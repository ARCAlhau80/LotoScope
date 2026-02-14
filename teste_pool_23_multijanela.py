# -*- coding: utf-8 -*-
"""
ESTRATÉGIA POOL 23 COM ANÁLISE MULTI-JANELA
============================================
Objetivo: Encontrar os 2 PIORES números para excluir

Janelas:
- Ultra curta: 3 sorteios
- Curta: 5 sorteios
- Média: 10 sorteios
- Média-longa: 15 sorteios
- Longa: 30 sorteios
- Ultra longa: 100 sorteios

Pool 23 → C(23,15) = 490.314 combinações
Se os 15 sorteados estiverem nos 23 → JACKPOT GARANTIDO!
"""

import pyodbc
from itertools import combinations
from math import comb
from collections import Counter
from datetime import datetime

print("="*70)
print("🧪 ESTRATÉGIA POOL 23 - ANÁLISE MULTI-JANELA")
print("="*70)

# ═══════════════════════════════════════════════════════════════════
# CONEXÃO COM BANCO
# ═══════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════════
CONCURSO_ALVO = 3609  # Concurso a prever

# Encontrar índice
idx_alvo = None
for i, r in enumerate(todos_resultados):
    if r['concurso'] == CONCURSO_ALVO:
        idx_alvo = i
        break

if idx_alvo is None:
    print(f"❌ Concurso {CONCURSO_ALVO} não encontrado!")
    exit()

resultado_real = todos_resultados[idx_alvo]
resultados_anteriores = todos_resultados[idx_alvo + 1:]

print(f"\n📋 CONCURSO ALVO: {CONCURSO_ALVO}")
print(f"   Resultado REAL: {sorted(resultado_real['numeros'])}")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE MULTI-JANELA
# ═══════════════════════════════════════════════════════════════════
JANELAS = {
    'ultra_curta': 3,
    'curta': 5,
    'media': 10,
    'media_longa': 15,
    'longa': 30,
    'ultra_longa': 100
}

# Pesos para cada janela (janelas curtas = mais peso para tendência recente)
PESOS = {
    'ultra_curta': 3.0,
    'curta': 2.5,
    'media': 2.0,
    'media_longa': 1.5,
    'longa': 1.0,
    'ultra_longa': 0.5
}

print("\n" + "="*70)
print("📊 ANÁLISE MULTI-JANELA")
print("="*70)

# Calcular frequência por janela
freq_por_janela = {}
for nome, tamanho in JANELAS.items():
    freq = Counter()
    for r in resultados_anteriores[:tamanho]:
        freq.update(r['numeros'])
    freq_por_janela[nome] = freq
    
    # Normalizar para % (frequência / tamanho)
    for n in freq:
        freq[n] = freq[n] / tamanho * 100  # % de aparição

# Mostrar análise
print(f"\n{'Num':<4}", end="")
for nome in JANELAS:
    print(f"{nome[:8]:>10}", end="")
print(f"{'SCORE':>10}")
print("-" * 74)

# Calcular score ponderado para cada número
scores = {}
for n in range(1, 26):
    score = 0
    for nome, peso in PESOS.items():
        freq_pct = freq_por_janela[nome].get(n, 0)
        score += freq_pct * peso
    scores[n] = score

# Ordenar por score (menor = pior)
ranking = sorted(scores.items(), key=lambda x: x[1])

# Mostrar todos os números
for n, score in sorted(scores.items(), key=lambda x: x[0]):
    print(f"{n:3d} ", end="")
    for nome in JANELAS:
        freq_pct = freq_por_janela[nome].get(n, 0)
        print(f"{freq_pct:>9.1f}%", end="")
    
    # Marcar piores e melhores
    if n in [ranking[0][0], ranking[1][0]]:
        marca = " ❌ PIOR"
    elif n in [ranking[-1][0], ranking[-2][0]]:
        marca = " ✅ TOP"
    else:
        marca = ""
    print(f"{score:>10.1f}{marca}")

# ═══════════════════════════════════════════════════════════════════
# IDENTIFICAR OS 2 PIORES
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("🎯 RESULTADO DA ANÁLISE")
print("="*70)

piores_2 = [ranking[0][0], ranking[1][0]]
melhores_23 = sorted([n for n in range(1, 26) if n not in piores_2])

print(f"\n❌ 2 PIORES números (excluir): {sorted(piores_2)}")
print(f"   Scores: {ranking[0][0]}={ranking[0][1]:.1f}, {ranking[1][0]}={ranking[1][1]:.1f}")

print(f"\n✅ POOL 23 (melhores): {melhores_23}")

# Verificar quantos do resultado real estão no pool
acertos_pool = len(resultado_real['set'] & set(melhores_23))
print(f"\n🎯 VALIDAÇÃO: Resultado real tem {acertos_pool}/15 no Pool 23")

if acertos_pool == 15:
    print("   🏆 JACKPOT GARANTIDO! Todos os 15 estão no pool!")
else:
    fora_pool = sorted(resultado_real['set'] - set(melhores_23))
    print(f"   ⚠️ Números do resultado FORA do pool: {fora_pool}")

# ═══════════════════════════════════════════════════════════════════
# GERAR COMBINAÇÕES COM DIFERENTES NÍVEIS DE FILTRO
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("🎰 GERAÇÃO DE COMBINAÇÕES")
print("="*70)

pool_23 = melhores_23
total_possivel = comb(23, 15)
print(f"\n📊 Pool 23 → C(23,15) = {total_possivel:,} combinações possíveis")

# Calcular parâmetros para filtros
ultimo_sorteio = resultados_anteriores[0]
ultimo_set = ultimo_sorteio['set']

# Parâmetros históricos
ultimos_30 = resultados_anteriores[:30]
somas = [sum(r['numeros']) for r in ultimos_30]
soma_media = sum(somas) / len(somas)
soma_min = min(somas)
soma_max = max(somas)

pares_hist = [sum(1 for n in r['numeros'] if n % 2 == 0) for r in ultimos_30]
primos_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
primos_hist = [len(set(r['numeros']) & primos_set) for r in ultimos_30]

# Frequências para favorecidos
freq_30 = Counter()
for r in ultimos_30:
    freq_30.update(r['numeros'])
top_15_freq = set(sorted(freq_30.keys(), key=lambda x: -freq_30[x])[:15])

# NÚCLEO C1/C2
NUCLEO = {2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 22, 24, 25}

# Repetição histórica
rep_hist = []
for i in range(min(50, len(resultados_anteriores)-1)):
    atual = resultados_anteriores[i]['set']
    anterior = resultados_anteriores[i+1]['set']
    rep_hist.append(len(atual & anterior))
rep_media = sum(rep_hist) / len(rep_hist)

print(f"\n📊 PARÂMETROS HISTÓRICOS:")
print(f"   Soma: média={soma_media:.0f}, range={soma_min}-{soma_max}")
print(f"   Pares: média={sum(pares_hist)/len(pares_hist):.1f}, range={min(pares_hist)}-{max(pares_hist)}")
print(f"   Primos: média={sum(primos_hist)/len(primos_hist):.1f}, range={min(primos_hist)}-{max(primos_hist)}")
print(f"   Repetição: média={rep_media:.1f}")

# ═══════════════════════════════════════════════════════════════════
# DEFINIR FILTROS
# ═══════════════════════════════════════════════════════════════════
FILTROS = {
    'SEM_FILTRO': {
        'soma': (0, 999),
        'pares': (0, 15),
        'primos': (0, 15),
        'nucleo': 0,
        'repetidos': (0, 15),
        'favorecidos': (0, 15)
    },
    'MODERADO': {
        'soma': (soma_min - 10, soma_max + 10),
        'pares': (5, 10),
        'primos': (3, 8),
        'nucleo': 8,
        'repetidos': (6, 11),
        'favorecidos': (6, 12)
    },
    'AGRESSIVO': {
        'soma': (soma_min, soma_max),
        'pares': (6, 9),
        'primos': (4, 7),
        'nucleo': 10,
        'repetidos': (7, 10),
        'favorecidos': (8, 11)
    },
    'ULTRA_AGRESSIVO': {
        'soma': (int(soma_media - 15), int(soma_media + 15)),
        'pares': (6, 8),
        'primos': (4, 6),
        'nucleo': 11,
        'repetidos': (8, 10),
        'favorecidos': (9, 11)
    }
}

# ═══════════════════════════════════════════════════════════════════
# GERAR E TESTAR CADA NÍVEL DE FILTRO
# ═══════════════════════════════════════════════════════════════════
import time

resultados_filtros = {}

for nome_filtro, params in FILTROS.items():
    print(f"\n{'─'*70}")
    print(f"🔧 FILTRO: {nome_filtro}")
    print(f"{'─'*70}")
    print(f"   Soma: {params['soma'][0]}-{params['soma'][1]}")
    print(f"   Pares: {params['pares'][0]}-{params['pares'][1]}")
    print(f"   Primos: {params['primos'][0]}-{params['primos'][1]}")
    print(f"   Núcleo: ≥{params['nucleo']}")
    print(f"   Repetição: {params['repetidos'][0]}-{params['repetidos'][1]}")
    print(f"   Favorecidos: {params['favorecidos'][0]}-{params['favorecidos'][1]}")
    
    inicio = time.time()
    combinacoes = []
    
    for combo in combinations(pool_23, 15):
        combo_set = set(combo)
        
        # Filtro SOMA
        soma = sum(combo)
        if soma < params['soma'][0] or soma > params['soma'][1]:
            continue
        
        # Filtro PARES
        qtd_pares = sum(1 for n in combo if n % 2 == 0)
        if qtd_pares < params['pares'][0] or qtd_pares > params['pares'][1]:
            continue
        
        # Filtro PRIMOS
        qtd_primos = len(combo_set & primos_set)
        if qtd_primos < params['primos'][0] or qtd_primos > params['primos'][1]:
            continue
        
        # Filtro NÚCLEO
        qtd_nucleo = len(combo_set & NUCLEO)
        if qtd_nucleo < params['nucleo']:
            continue
        
        # Filtro REPETIÇÃO
        qtd_rep = len(combo_set & ultimo_set)
        if qtd_rep < params['repetidos'][0] or qtd_rep > params['repetidos'][1]:
            continue
        
        # Filtro FAVORECIDOS
        qtd_fav = len(combo_set & top_15_freq)
        if qtd_fav < params['favorecidos'][0] or qtd_fav > params['favorecidos'][1]:
            continue
        
        combinacoes.append(list(combo))
    
    tempo = time.time() - inicio
    print(f"\n   ✅ {len(combinacoes):,} combinações em {tempo:.1f}s")
    
    # Validar contra resultado real
    acertos_dist = Counter()
    melhores = []
    
    for combo in combinacoes:
        acertos = len(set(combo) & resultado_real['set'])
        acertos_dist[acertos] += 1
        if acertos >= 13:
            melhores.append((combo, acertos))
    
    if len(combinacoes) > 0:
        media = sum(ac * qtd for ac, qtd in acertos_dist.items()) / len(combinacoes)
        max_acertos = max(acertos_dist.keys()) if acertos_dist else 0
        acertos_11_mais = sum(qtd for ac, qtd in acertos_dist.items() if ac >= 11)
        
        print(f"\n   📈 RESULTADOS:")
        for ac in sorted(acertos_dist.keys(), reverse=True):
            if ac >= 10:
                qtd = acertos_dist[ac]
                pct = qtd / len(combinacoes) * 100
                premio = ""
                if ac == 15: premio = " ← JACKPOT!"
                elif ac == 14: premio = " ← R$1.000+"
                elif ac == 13: premio = " ← R$35"
                elif ac == 12: premio = " ← R$14"
                elif ac == 11: premio = " ← R$7"
                print(f"      {ac} acertos: {qtd:,} ({pct:.1f}%){premio}")
        
        print(f"\n   📊 Média: {media:.2f} | Max: {max_acertos} | 11+: {acertos_11_mais:,} ({100*acertos_11_mais/len(combinacoes):.1f}%)")
        
        # Financeiro
        custo = len(combinacoes) * 3.50
        premio_total = 0
        for ac, qtd in acertos_dist.items():
            if ac == 11: premio_total += 7 * qtd
            elif ac == 12: premio_total += 14 * qtd
            elif ac == 13: premio_total += 35 * qtd
            elif ac == 14: premio_total += 1000 * qtd
            elif ac == 15: premio_total += 1800000 * qtd
        
        lucro = premio_total - custo
        roi = (premio_total / custo - 1) * 100 if custo > 0 else 0
        
        print(f"\n   💰 Custo: R${custo:,.2f} | Prêmio: R${premio_total:,.2f} | ROI: {roi:+.1f}%")
        
        resultados_filtros[nome_filtro] = {
            'combinacoes': len(combinacoes),
            'media': media,
            'max': max_acertos,
            'pct_11': 100*acertos_11_mais/len(combinacoes) if len(combinacoes) > 0 else 0,
            'roi': roi,
            'custo': custo,
            'premio': premio_total
        }
    else:
        print(f"   ❌ Nenhuma combinação passou nos filtros!")
        resultados_filtros[nome_filtro] = None

# ═══════════════════════════════════════════════════════════════════
# RESUMO COMPARATIVO
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 RESUMO COMPARATIVO")
print("="*70)

print(f"\n{'Filtro':<18} {'Combos':>12} {'Média':>8} {'Max':>5} {'11+%':>8} {'ROI':>10}")
print("-"*70)

for nome, res in resultados_filtros.items():
    if res:
        print(f"{nome:<18} {res['combinacoes']:>12,} {res['media']:>8.2f} {res['max']:>5} {res['pct_11']:>7.1f}% {res['roi']:>+9.1f}%")
    else:
        print(f"{nome:<18} {'---':>12} {'---':>8} {'---':>5} {'---':>8} {'---':>10}")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE: O POOL CAPTUROU O JACKPOT?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("🎯 ANÁLISE FINAL")
print("="*70)

if acertos_pool == 15:
    print("\n🏆 SUCESSO! O Pool 23 continha TODOS os 15 números do resultado!")
    print("   → Com filtro SEM_FILTRO, teríamos o JACKPOT!")
else:
    print(f"\n⚠️ Pool 23 capturou {acertos_pool}/15 números.")
    print(f"   → Números do resultado FORA do pool: {fora_pool}")
    print(f"   → Estes números foram identificados como 'piores': {sorted(piores_2)}")
    
    # Verificar se os fora do pool estão entre os piores
    fora_nos_piores = [n for n in fora_pool if n in piores_2]
    if fora_nos_piores:
        print(f"   ❌ ERRO: {fora_nos_piores} foram excluídos mas saíram no resultado!")
    else:
        print(f"   ⚠️ Os números excluídos ({sorted(piores_2)}) não saíram, mas outros sim.")

cursor.close()
conn.close()

print("\n" + "="*70)
print("✅ ANÁLISE CONCLUÍDA!")
print("="*70)
