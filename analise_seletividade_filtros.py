# -*- coding: utf-8 -*-
"""
ANÁLISE DE SELETIVIDADE DOS FILTROS
====================================
Objetivo: Encontrar filtros INTELIGENTES que:
- Rejeitam MUITAS combinações aleatórias (redução)
- Preservam MUITOS sorteios reais (não perdem jackpots)

Métrica: Seletividade = Taxa_Real / Taxa_Random
- Se > 1: Filtro INTELIGENTE (rejeita mais lixo que jackpots)
- Se = 1: Filtro NEUTRO (não discrimina)
- Se < 1: Filtro BURRO (rejeita mais jackpots que lixo)

Data: 28/03/2026
"""

import pyodbc
import random
from collections import defaultdict
from itertools import combinations

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def obter_concursos(n=300):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {n} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def gerar_combinacoes_aleatorias(n=5000):
    """Gera N combinações aleatórias de 15 números"""
    combos = []
    for _ in range(n):
        combo = sorted(random.sample(range(1, 26), 15))
        combos.append(combo)
    return combos

# ============== FILTROS ==============

def filtro_soma(nums, min_val, max_val):
    return min_val <= sum(nums) <= max_val

def filtro_pares(nums, min_val, max_val):
    pares = sum(1 for n in nums if n % 2 == 0)
    return min_val <= pares <= max_val

def filtro_primos(nums, min_val, max_val):
    primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    qtde = sum(1 for n in nums if n in primos)
    return min_val <= qtde <= max_val

def filtro_fibonacci(nums, min_val, max_val):
    fib = {1, 2, 3, 5, 8, 13, 21}
    qtde = sum(1 for n in nums if n in fib)
    return min_val <= qtde <= max_val

def filtro_consecutivos(nums, max_cons):
    nums_sorted = sorted(nums)
    max_seq = 1
    seq_atual = 1
    for i in range(1, len(nums_sorted)):
        if nums_sorted[i] == nums_sorted[i-1] + 1:
            seq_atual += 1
            max_seq = max(max_seq, seq_atual)
        else:
            seq_atual = 1
    return max_seq <= max_cons

def filtro_qtde_6_25(nums, min_val, max_val):
    qtde = sum(1 for n in nums if 6 <= n <= 25)
    return min_val <= qtde <= max_val

def filtro_extremos(nums, min_val, max_val):
    extremos = sum(1 for n in nums if n <= 5 or n >= 21)
    return min_val <= extremos <= max_val

def filtro_linhas(nums, min_por_linha, max_por_linha):
    linhas = [0, 0, 0, 0, 0]
    for n in nums:
        linhas[(n-1) // 5] += 1
    return all(min_por_linha <= l <= max_por_linha for l in linhas)

def filtro_colunas(nums, min_por_col, max_por_col):
    colunas = [0, 0, 0, 0, 0]
    for n in nums:
        colunas[(n-1) % 5] += 1
    return all(min_por_col <= c <= max_por_col for c in colunas)

# Configurações de filtros para testar
FILTROS_CONFIG = {
    # Soma
    'Soma 160-245 (relaxado)': lambda n: filtro_soma(n, 160, 245),
    'Soma 170-235': lambda n: filtro_soma(n, 170, 235),
    'Soma 180-220 (restrito)': lambda n: filtro_soma(n, 180, 220),
    'Soma 185-215 (muito restrito)': lambda n: filtro_soma(n, 185, 215),
    
    # Pares
    'Pares 5-10 (relaxado)': lambda n: filtro_pares(n, 5, 10),
    'Pares 6-9': lambda n: filtro_pares(n, 6, 9),
    'Pares 7-8 (restrito)': lambda n: filtro_pares(n, 7, 8),
    
    # Primos
    'Primos 3-8 (relaxado)': lambda n: filtro_primos(n, 3, 8),
    'Primos 4-7': lambda n: filtro_primos(n, 4, 7),
    'Primos 5-6 (restrito)': lambda n: filtro_primos(n, 5, 6),
    
    # Consecutivos
    'Consecutivos max 7': lambda n: filtro_consecutivos(n, 7),
    'Consecutivos max 6': lambda n: filtro_consecutivos(n, 6),
    'Consecutivos max 5': lambda n: filtro_consecutivos(n, 5),
    'Consecutivos max 4': lambda n: filtro_consecutivos(n, 4),
    'Consecutivos max 3': lambda n: filtro_consecutivos(n, 3),
    
    # Qtde 6-25
    'Qtde 6-25: 9-14': lambda n: filtro_qtde_6_25(n, 9, 14),
    'Qtde 6-25: 10-13': lambda n: filtro_qtde_6_25(n, 10, 13),
    'Qtde 6-25: 11-12': lambda n: filtro_qtde_6_25(n, 11, 12),
    
    # Extremos
    'Extremos 1-7': lambda n: filtro_extremos(n, 1, 7),
    'Extremos 2-6': lambda n: filtro_extremos(n, 2, 6),
    'Extremos 3-5': lambda n: filtro_extremos(n, 3, 5),
    'Extremos 2-4': lambda n: filtro_extremos(n, 2, 4),
    
    # Linhas/Colunas
    'Linhas 1-5 cada': lambda n: filtro_linhas(n, 1, 5),
    'Linhas 2-4 cada': lambda n: filtro_linhas(n, 2, 4),
    'Colunas 1-5 cada': lambda n: filtro_colunas(n, 1, 5),
    'Colunas 2-4 cada': lambda n: filtro_colunas(n, 2, 4),
}

def main():
    print("=" * 85)
    print("🔬 ANÁLISE DE SELETIVIDADE DOS FILTROS")
    print("=" * 85)
    
    # Dados
    concursos = obter_concursos(300)
    sorteios_reais = [[row[i] for i in range(1, 16)] for row in concursos]
    
    print(f"\n📊 Gerando combinações aleatórias...")
    combos_random = gerar_combinacoes_aleatorias(10000)
    
    print(f"   {len(sorteios_reais)} sorteios reais")
    print(f"   {len(combos_random)} combinações aleatórias")
    
    # Analisa cada filtro
    resultados = []
    
    for nome, filtro_func in FILTROS_CONFIG.items():
        # Taxa em sorteios reais
        aprovados_real = sum(1 for s in sorteios_reais if filtro_func(s))
        taxa_real = aprovados_real / len(sorteios_reais) * 100
        
        # Taxa em combinações aleatórias
        aprovados_random = sum(1 for c in combos_random if filtro_func(c))
        taxa_random = aprovados_random / len(combos_random) * 100
        
        # Seletividade (quanto maior, melhor)
        if taxa_random > 0:
            seletividade = taxa_real / taxa_random
        else:
            seletividade = float('inf')
        
        # Redução estimada (baseado em pool de 490k)
        reducao_pct = 100 - taxa_random
        combos_restantes = int(490000 * taxa_random / 100)
        
        resultados.append({
            'nome': nome,
            'taxa_real': taxa_real,
            'taxa_random': taxa_random,
            'seletividade': seletividade,
            'reducao': reducao_pct,
            'restantes': combos_restantes
        })
    
    # Ordena por seletividade (melhor primeiro)
    resultados.sort(key=lambda x: x['seletividade'], reverse=True)
    
    print("\n" + "=" * 85)
    print("📊 RANKING DE FILTROS POR SELETIVIDADE:")
    print("=" * 85)
    
    print(f"\n{'Filtro':<28} {'Real%':>7} {'Random%':>8} {'Selet.':>7} {'Redução':>8} {'Restam':>10}")
    print("-" * 85)
    
    for r in resultados:
        # Classificação
        if r['seletividade'] >= 1.5:
            emoji = "⭐"  # Excelente
        elif r['seletividade'] >= 1.1:
            emoji = "✅"  # Bom
        elif r['seletividade'] >= 0.9:
            emoji = "🟡"  # Neutro
        else:
            emoji = "❌"  # Ruim
        
        selet_str = f"{r['seletividade']:.2f}" if r['seletividade'] < 100 else "∞"
        
        print(f"{r['nome']:<28} {r['taxa_real']:>6.1f}% {r['taxa_random']:>7.1f}% {selet_str:>7} {r['reducao']:>7.1f}% {r['restantes']:>9,} {emoji}")
    
    # Análise: filtros ideais (alta seletividade + boa redução)
    print("\n" + "=" * 85)
    print("🎯 FILTROS IDEAIS (Seletividade ≥ 1.1 E Redução ≥ 10%):")
    print("=" * 85)
    
    ideais = [r for r in resultados if r['seletividade'] >= 1.1 and r['reducao'] >= 10]
    
    if ideais:
        print(f"\n{'Filtro':<28} {'Real%':>7} {'Redução':>8} {'Seletividade':>12}")
        print("-" * 60)
        for r in ideais:
            print(f"{r['nome']:<28} {r['taxa_real']:>6.1f}% {r['reducao']:>7.1f}% {r['seletividade']:>11.2f}x")
    else:
        print("\n   Nenhum filtro atende os critérios")
    
    # Simulação de combinações de filtros
    print("\n" + "=" * 85)
    print("📊 SIMULAÇÃO DE COMBINAÇÕES DE FILTROS:")
    print("=" * 85)
    
    # Combinação sugerida: filtros com melhor custo-benefício
    combinacoes_filtros = {
        'Level 1 (mínimo)': [
            ('Soma 170-235', lambda n: filtro_soma(n, 170, 235)),
        ],
        'Level 2 (básico)': [
            ('Soma 170-235', lambda n: filtro_soma(n, 170, 235)),
            ('Pares 6-9', lambda n: filtro_pares(n, 6, 9)),
        ],
        'Level 3 (balanceado)': [
            ('Soma 170-235', lambda n: filtro_soma(n, 170, 235)),
            ('Pares 6-9', lambda n: filtro_pares(n, 6, 9)),
            ('Primos 4-7', lambda n: filtro_primos(n, 4, 7)),
            ('Consecutivos max 6', lambda n: filtro_consecutivos(n, 6)),
        ],
        'Level 4 (moderado)': [
            ('Soma 180-220', lambda n: filtro_soma(n, 180, 220)),
            ('Pares 6-9', lambda n: filtro_pares(n, 6, 9)),
            ('Primos 4-7', lambda n: filtro_primos(n, 4, 7)),
            ('Consecutivos max 5', lambda n: filtro_consecutivos(n, 5)),
            ('Linhas 1-5', lambda n: filtro_linhas(n, 1, 5)),
        ],
        'Level 5 (agressivo)': [
            ('Soma 180-220', lambda n: filtro_soma(n, 180, 220)),
            ('Pares 6-9', lambda n: filtro_pares(n, 6, 9)),
            ('Primos 4-7', lambda n: filtro_primos(n, 4, 7)),
            ('Consecutivos max 5', lambda n: filtro_consecutivos(n, 5)),
            ('Linhas 2-4', lambda n: filtro_linhas(n, 2, 4)),
            ('Colunas 2-4', lambda n: filtro_colunas(n, 2, 4)),
        ],
        'Level 6 (ultra)': [
            ('Soma 185-215', lambda n: filtro_soma(n, 185, 215)),
            ('Pares 7-8', lambda n: filtro_pares(n, 7, 8)),
            ('Primos 5-6', lambda n: filtro_primos(n, 5, 6)),
            ('Consecutivos max 4', lambda n: filtro_consecutivos(n, 4)),
            ('Linhas 2-4', lambda n: filtro_linhas(n, 2, 4)),
            ('Colunas 2-4', lambda n: filtro_colunas(n, 2, 4)),
        ],
    }
    
    print(f"\n{'Level':<20} {'Real%':>8} {'Random%':>9} {'Restam':>12} {'Seletiv.':>10}")
    print("-" * 65)
    
    for level_nome, filtros in combinacoes_filtros.items():
        # Aplica todos os filtros da combinação
        aprovados_real = 0
        for s in sorteios_reais:
            if all(f[1](s) for f in filtros):
                aprovados_real += 1
        taxa_real = aprovados_real / len(sorteios_reais) * 100
        
        aprovados_random = 0
        for c in combos_random:
            if all(f[1](c) for f in filtros):
                aprovados_random += 1
        taxa_random = aprovados_random / len(combos_random) * 100
        
        restantes = int(490000 * taxa_random / 100)
        selet = taxa_real / taxa_random if taxa_random > 0 else float('inf')
        
        # Emoji baseado em equilíbrio
        if taxa_real >= 70 and restantes <= 100000:
            emoji = "⭐ IDEAL"
        elif taxa_real >= 50:
            emoji = "✅ BOM"
        elif taxa_real >= 30:
            emoji = "🟡 OK"
        else:
            emoji = "❌ AGRESSIVO"
        
        print(f"{level_nome:<20} {taxa_real:>7.1f}% {taxa_random:>8.2f}% {restantes:>11,} {selet:>9.2f}x {emoji}")
    
    # Recomendações finais
    print("\n" + "=" * 85)
    print("💡 RECOMENDAÇÕES PARA OS LEVELS DO POOL 23:")
    print("=" * 85)
    
    print("""
    📋 AJUSTES SUGERIDOS:
    
    Level 1-2 (mínimo):
    - Soma: 170-235 (em vez de 160-245)
    - Pares: 6-9 (em vez de 5-10)
    → Mantém ~95% dos jackpots, reduz ~30-40%
    
    Level 3-4 (balanceado):
    - Soma: 180-220
    - Pares: 6-9
    - Primos: 4-7
    - Consecutivos: max 5-6 (em vez de max 3)
    → Mantém ~65-75% dos jackpots
    
    Level 5-6 (agressivo):
    - Adicionar Linhas 2-4 e Colunas 2-4
    - NÃO usar Extremos 2-4 (muito assassino!)
    - Consecutivos: max 4-5 (em vez de max 3)
    → Reduz muito, mas preserva ~40-50% dos jackpots
    
    ⚠️ FILTROS A EVITAR:
    - Extremos 2-4: mata 90% dos jackpots!
    - Consecutivos max 3: mata 85% dos jackpots!
    """)
    
    print("\n✅ Análise concluída!")

if __name__ == '__main__':
    main()
