# -*- coding: utf-8 -*-
"""
POC: Avaliar Seletividade dos Filtros Fibonacci, Quintis e Faixa 6-20
======================================================================
Metodologia:
  Para cada concurso C (dos últimos 500):
    1. Gerar TODAS as C(23,15) = 490.314 combinações (Pool 23, excluindo 2 piores)
    2. Contar quantas passam no filtro candidato (taxa_random)
    3. Verificar se o resultado REAL passa no filtro candidato (taxa_jackpot)
    4. Seletividade = taxa_jackpot / taxa_random
       - >1.0 = INTELIGENTE (preserva jackpots mais que random)
       - =1.0 = NEUTRO (só reduz volume)
       - <1.0 = BURRO (rejeita jackpots mais que random)

OTIMIZAÇÃO CRÍTICA:
  Gerar 490k combinações de 15 números é muito pesado. Em vez disso:
  - Para SELETIVIDADE: Usar amostragem Monte Carlo de 50.000 combinações aleatórias
    e comparar contra o resultado real. Isso dá erro <0.5% vs enumerar todas.
  - O resultado real é DETERMINÍSTICO (passa ou não), então avaliamos em 100% dos concursos.

Filtros candidatos:
  [F1] Fibonacci: QtdeFibonacci IN (2,3,4,5,6)  → 98.4% dos sorteios reais
  [F2] Fibonacci restrito: IN (3,4,5,6)          → 93.4%
  [F3] Fibonacci agressivo: IN (3,4,5)           → 81.8%
  [F4] Quintis equilibrados: Cada Quintil IN (1,2,3,4) → 100-0.4% extremos rejeitados
  [F5] Quintis restrito: Cada Quintil IN (2,3,4) → rejeita Q=0,1,5
  [F6] Faixa 6-20: IN (7,8,9,10,11)             → 96.6%
  [F7] Faixa 6-20 restrito: IN (8,9,10)          → 77.6%
  [F8] Faixa 6-20 agressivo: IN (8,9,10,11)      → 86.7%
"""

import sys
import os
import random
import time
from math import comb
from itertools import combinations
from collections import Counter, defaultdict

import pyodbc
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

# ═══════════════════════════════════════════════════════════════════════════════
# DEFINIÇÃO DOS FILTROS CANDIDATOS
# ═══════════════════════════════════════════════════════════════════════════════

def qtde_fibonacci(combo):
    """Conta números Fibonacci na combinação"""
    return sum(1 for n in combo if n in FIBONACCI)

def qtde_faixa_6_20(combo):
    """Conta números na faixa 6-20"""
    return sum(1 for n in combo if 6 <= n <= 20)

def quintis(combo):
    """Retorna (q1, q2, q3, q4, q5) — qtde por quintil"""
    q = [0, 0, 0, 0, 0]
    for n in combo:
        q[(n - 1) // 5] += 1
    return tuple(q)


FILTROS = {
    # ═══ FIBONACCI ═══
    'Fib_2-6': lambda c: qtde_fibonacci(c) in {2, 3, 4, 5, 6},
    'Fib_3-6': lambda c: qtde_fibonacci(c) in {3, 4, 5, 6},
    'Fib_3-5': lambda c: qtde_fibonacci(c) in {3, 4, 5},
    'Fib_4-5': lambda c: qtde_fibonacci(c) in {4, 5},
    
    # ═══ QUINTIS ═══
    'Quintis_1-4': lambda c: all(1 <= q <= 4 for q in quintis(c)),
    'Quintis_2-4': lambda c: all(2 <= q <= 4 for q in quintis(c)),
    'Quintis_1-5_bal': lambda c: max(quintis(c)) - min(quintis(c)) <= 3,  # Equilíbrio
    'Quintis_spread<=2': lambda c: max(quintis(c)) - min(quintis(c)) <= 2,
    
    # ═══ FAIXA 6-20 ═══
    'F6-20_7-11': lambda c: qtde_faixa_6_20(c) in {7, 8, 9, 10, 11},
    'F6-20_8-10': lambda c: qtde_faixa_6_20(c) in {8, 9, 10},
    'F6-20_8-11': lambda c: qtde_faixa_6_20(c) in {8, 9, 10, 11},
    'F6-20_7-10': lambda c: qtde_faixa_6_20(c) in {7, 8, 9, 10},
}


# ═══════════════════════════════════════════════════════════════════════════════
# CARREGAR DADOS HISTÓRICOS
# ═══════════════════════════════════════════════════════════════════════════════

def carregar_resultados(n_concursos=500):
    """Carrega últimos N concursos do banco"""
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP (?) Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """, (n_concursos,))
    rows = cursor.fetchall()
    conn.close()
    # Retorna do mais antigo ao mais recente
    return [(r[0], sorted(list(r[1:16]))) for r in reversed(rows)]


# ═══════════════════════════════════════════════════════════════════════════════
# MÉTODO 1: SELETIVIDADE VIA AMOSTRA MONTE CARLO
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_amostra_pool23(numeros_disponiveis, n_amostras=50000):
    """
    Gera amostra aleatória de combinações C(23,15) sem enumerar todas.
    Para C(23,15)=490.314, amostra de 50k dá erro estatístico <0.5%.
    """
    nums = sorted(numeros_disponiveis)
    amostras = []
    for _ in range(n_amostras):
        combo = sorted(random.sample(nums, 15))
        amostras.append(tuple(combo))
    return amostras


def calcular_seletividade(resultados, n_amostras=50000, concurso_inicio=None):
    """
    Calcula seletividade de cada filtro via Monte Carlo.
    
    seletividade = P(jackpot passa) / P(random passa)
    
    - P(jackpot passa)  = % dos sorteios reais que passam no filtro
    - P(random passa)   = % das combinações aleatórias que passam (média sobre todos os concursos)
    
    Se seletividade > 1.0, o filtro é INTELIGENTE.
    """
    
    print(f"\n{'='*80}")
    print(f"  POC: SELETIVIDADE DE FILTROS CANDIDATOS")
    print(f"  {len(resultados)} concursos | {n_amostras:,} amostras Monte Carlo por concurso")
    print(f"{'='*80}")
    
    # Inicializar contadores
    filtro_names = list(FILTROS.keys())
    jackpot_passa = {f: 0 for f in filtro_names}     # Quantos sorteios reais passam
    jackpot_total = 0                                   # Total de sorteios com exclusão correta
    random_passa_pct = {f: [] for f in filtro_names}  # % de aleatórias que passam por concurso
    
    t0 = time.time()
    
    for idx, (concurso, resultado) in enumerate(resultados):
        resultado_set = set(resultado)
        
        # Para esta POC, precisamos saber quais 2 números excluir.
        # Simulamos "exclusão perfeita" (os 2 que NÃO estão no resultado).
        # Isso nos dá a taxa de seletividade NO CENÁRIO ÓTIMO.
        numeros_fora = [n for n in range(1, 26) if n not in resultado_set]
        
        if len(numeros_fora) != 10:
            continue  # Deve ser sempre 10 = 25 - 15
            
        # Simular excluir 2 dos 10 que estão fora (exclusão sempre correta)
        # Para o test mais realista, usamos apenas os 2 primeiros
        excluidos = numeros_fora[:2]
        pool_23 = [n for n in range(1, 26) if n not in excluidos]
        
        jackpot_total += 1
        
        # Verificar se resultado real passa em cada filtro
        for f_name, f_func in FILTROS.items():
            if f_func(resultado):
                jackpot_passa[f_name] += 1
        
        # Gerar amostra Monte Carlo e verificar taxa de passagem
        amostra = gerar_amostra_pool23(pool_23, n_amostras)
        for f_name, f_func in FILTROS.items():
            passa = sum(1 for c in amostra if f_func(c))
            random_passa_pct[f_name].append(passa / n_amostras * 100)
        
        if (idx + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed
            remaining = (len(resultados) - idx - 1) / rate
            print(f"  📊 {idx+1}/{len(resultados)} concursos processados "
                  f"({elapsed:.0f}s, ~{remaining:.0f}s restante)")
    
    elapsed_total = time.time() - t0
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RESULTADOS
    # ═══════════════════════════════════════════════════════════════════════════
    print(f"\n{'─'*80}")
    print(f"  RESULTADOS ({elapsed_total:.1f}s total)")
    print(f"{'─'*80}")
    print(f"\n  Concursos analisados: {jackpot_total}")
    print(f"  Amostras Monte Carlo: {n_amostras:,} por concurso\n")
    
    # Header
    print(f"  {'Filtro':<20} {'Jackpot%':>10} {'Random%':>10} {'Seletiv.':>10} {'Redução%':>10} {'Veredicto':<18}")
    print(f"  {'─'*20} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*18}")
    
    resultados_filtros = []
    
    for f_name in filtro_names:
        jp_pct = jackpot_passa[f_name] / jackpot_total * 100 if jackpot_total > 0 else 0
        rnd_pct = np.mean(random_passa_pct[f_name]) if random_passa_pct[f_name] else 0
        
        seletividade = jp_pct / rnd_pct if rnd_pct > 0 else float('inf')
        reducao = 100 - rnd_pct  # % de combos eliminadas
        
        if seletividade >= 1.10:
            veredicto = "⭐ INTELIGENTE"
        elif seletividade >= 1.02:
            veredicto = "✅ Bom"
        elif seletividade >= 0.98:
            veredicto = "⚪ Neutro"
        elif seletividade >= 0.90:
            veredicto = "⚠️ Fraco"
        else:
            veredicto = "❌ BURRO"
        
        print(f"  {f_name:<20} {jp_pct:>9.1f}% {rnd_pct:>9.1f}% {seletividade:>10.3f} {reducao:>9.1f}% {veredicto:<18}")
        
        resultados_filtros.append({
            'filtro': f_name,
            'jackpot_pct': jp_pct,
            'random_pct': rnd_pct,
            'seletividade': seletividade,
            'reducao': reducao,
            'veredicto': veredicto,
        })
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RANKING
    # ═══════════════════════════════════════════════════════════════════════════
    print(f"\n{'─'*80}")
    print(f"  RANKING POR SELETIVIDADE (melhores candidatos para inclusão no Pool 23)")
    print(f"{'─'*80}\n")
    
    ranking = sorted(resultados_filtros, key=lambda x: x['seletividade'], reverse=True)
    for i, r in enumerate(ranking):
        emoji = "🏆" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(f"  {emoji} #{i+1} {r['filtro']:<20} "
              f"Seletiv={r['seletividade']:.3f}  "
              f"Jackpot={r['jackpot_pct']:.1f}%  "
              f"Redução={r['reducao']:.1f}%  "
              f"{r['veredicto']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RECOMENDAÇÃO
    # ═══════════════════════════════════════════════════════════════════════════
    inteligentes = [r for r in ranking if r['seletividade'] >= 1.02]
    neutros = [r for r in ranking if 0.98 <= r['seletividade'] < 1.02]
    burros = [r for r in ranking if r['seletividade'] < 0.98]
    
    print(f"\n{'─'*80}")
    print(f"  RECOMENDAÇÃO")
    print(f"{'─'*80}")
    print(f"\n  ✅ Candidatos a incluir ({len(inteligentes)}):")
    for r in inteligentes:
        print(f"     → {r['filtro']}: seletividade {r['seletividade']:.3f}, redução {r['reducao']:.1f}%")
    
    if neutros:
        print(f"\n  ⚪ Neutros - só reduzem volume ({len(neutros)}):")
        for r in neutros:
            print(f"     → {r['filtro']}: seletividade {r['seletividade']:.3f}")
    
    if burros:
        print(f"\n  ❌ NÃO incluir - rejeitam jackpots ({len(burros)}):")
        for r in burros:
            print(f"     → {r['filtro']}: seletividade {r['seletividade']:.3f}")
    
    return resultados_filtros


# ═══════════════════════════════════════════════════════════════════════════════
# MÉTODO 2: ANÁLISE DE IMPACTO COMBINADO (os 3 filtros juntos)
# ═══════════════════════════════════════════════════════════════════════════════

def analisar_impacto_combinado(resultados, n_amostras=50000):
    """
    Testa combinações dos 3 filtros:
    - Fibonacci + Quintis
    - Fibonacci + Faixa 6-20
    - Quintis + Faixa 6-20
    - Todos os 3
    
    Usando os ranges mais promissores da análise individual.
    """
    print(f"\n{'='*80}")
    print(f"  ANÁLISE DE IMPACTO COMBINADO")
    print(f"{'='*80}")
    
    # Definir combos de filtros (ranges moderados)
    combos_filtro = {
        'Fib_3-6 ONLY': lambda c: qtde_fibonacci(c) in {3, 4, 5, 6},
        'Quintis_1-4 ONLY': lambda c: all(1 <= q <= 4 for q in quintis(c)),
        'F6-20_7-11 ONLY': lambda c: qtde_faixa_6_20(c) in {7, 8, 9, 10, 11},
        'Fib + Quintis': lambda c: (qtde_fibonacci(c) in {3, 4, 5, 6} and 
                                      all(1 <= q <= 4 for q in quintis(c))),
        'Fib + F6-20': lambda c: (qtde_fibonacci(c) in {3, 4, 5, 6} and 
                                    qtde_faixa_6_20(c) in {7, 8, 9, 10, 11}),
        'Quintis + F6-20': lambda c: (all(1 <= q <= 4 for q in quintis(c)) and 
                                        qtde_faixa_6_20(c) in {7, 8, 9, 10, 11}),
        'TODOS_3': lambda c: (qtde_fibonacci(c) in {3, 4, 5, 6} and 
                               all(1 <= q <= 4 for q in quintis(c)) and 
                               qtde_faixa_6_20(c) in {7, 8, 9, 10, 11}),
    }
    
    jackpot_passa = {f: 0 for f in combos_filtro}
    jackpot_total = 0
    random_passa_pct = {f: [] for f in combos_filtro}
    
    t0 = time.time()
    
    for idx, (concurso, resultado) in enumerate(resultados):
        resultado_set = set(resultado)
        numeros_fora = [n for n in range(1, 26) if n not in resultado_set]
        if len(numeros_fora) != 10:
            continue
        
        excluidos = numeros_fora[:2]
        pool_23 = [n for n in range(1, 26) if n not in excluidos]
        jackpot_total += 1
        
        for f_name, f_func in combos_filtro.items():
            if f_func(resultado):
                jackpot_passa[f_name] += 1
        
        amostra = gerar_amostra_pool23(pool_23, n_amostras)
        for f_name, f_func in combos_filtro.items():
            passa = sum(1 for c in amostra if f_func(c))
            random_passa_pct[f_name].append(passa / n_amostras * 100)
        
        if (idx + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed
            remaining = (len(resultados) - idx - 1) / rate
            print(f"  📊 {idx+1}/{len(resultados)} processados ({elapsed:.0f}s, ~{remaining:.0f}s restante)")
    
    elapsed_total = time.time() - t0
    
    print(f"\n  {'Combo Filtros':<22} {'Jackpot%':>10} {'Random%':>10} {'Seletiv.':>10} {'Redução%':>10} {'Veredicto':<18}")
    print(f"  {'─'*22} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*18}")
    
    for f_name in combos_filtro:
        jp_pct = jackpot_passa[f_name] / jackpot_total * 100 if jackpot_total > 0 else 0
        rnd_pct = np.mean(random_passa_pct[f_name]) if random_passa_pct[f_name] else 0
        seletividade = jp_pct / rnd_pct if rnd_pct > 0 else float('inf')
        reducao = 100 - rnd_pct
        
        if seletividade >= 1.10:
            veredicto = "⭐ INTELIGENTE"
        elif seletividade >= 1.02:
            veredicto = "✅ Bom"
        elif seletividade >= 0.98:
            veredicto = "⚪ Neutro"
        elif seletividade >= 0.90:
            veredicto = "⚠️ Fraco"
        else:
            veredicto = "❌ BURRO"
        
        print(f"  {f_name:<22} {jp_pct:>9.1f}% {rnd_pct:>9.1f}% {seletividade:>10.3f} {reducao:>9.1f}% {veredicto:<18}")
    
    print(f"\n  ⏱️ Tempo: {elapsed_total:.1f}s")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Seed para reprodutibilidade
    random.seed(42)
    np.random.seed(42)
    
    # Configuração
    N_CONCURSOS = 500        # Últimos 500 concursos para análise
    N_AMOSTRAS = 30000       # Monte Carlo (30k = bom equilíbrio velocidade/precisão)
    
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║  POC: AVALIAÇÃO DE FILTROS CANDIDATOS — Fibonacci, Quintis, Faixa 6-20     ║")
    print("║  Método: Seletividade via Monte Carlo sobre dados históricos reais          ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    
    print(f"\n  Carregando últimos {N_CONCURSOS} concursos...")
    resultados = carregar_resultados(N_CONCURSOS)
    print(f"  ✅ {len(resultados)} concursos carregados (#{resultados[0][0]} a #{resultados[-1][0]})")
    
    # Fase 1: Análise individual de cada filtro
    resultados_filtros = calcular_seletividade(resultados, N_AMOSTRAS)
    
    # Fase 2: Análise de combos dos melhores filtros
    print("\n")
    analisar_impacto_combinado(resultados, N_AMOSTRAS)
    
    print(f"\n{'='*80}")
    print(f"  FIM DA POC")
    print(f"{'='*80}")
