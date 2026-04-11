# -*- coding: utf-8 -*-
"""
POC: Quinas Frequentes & Ausentes — Análise de Vantagem
========================================================
Conceito 1: Top 5 quinas frequentes do treino → validar persistência no teste
Conceito 2: 10 ausentes → C(10,5)=252 combos completos (15 nums) vs aleatório

Lotofácil: 25 números, 15 sorteados
Scoring: comparação direta estratégia vs aleatório sobre base histórica real
"""

import pyodbc
import numpy as np
from itertools import combinations
from collections import Counter
import time
import sys

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def carregar_resultados():
    """Carrega todos os resultados ordenados por concurso ASC."""
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT ORDER BY Concurso ASC
        """)
        return [
            {'concurso': row[0], 'numeros': sorted([int(x) for x in row[1:16]])}
            for row in cursor.fetchall()
        ]


# ══════════════════════════════════════════════════════════════════════════════
# CONCEITO 1: TOP QUINAS FREQUENTES
# ══════════════════════════════════════════════════════════════════════════════

def poc_conceito1_quinas(resultados, treino_size=99, teste_size=200, top_n=5):
    """
    Top Quinas: as 5-tuplas mais frequentes nos concursos de treino.
    
    Teste: para cada concurso seguinte, contar quantos números de cada top quina
    aparecem no resultado. Comparar com quinas aleatórias.
    
    Premissa "acertar 3 de 5": validar se top quinas têm taxa de ≥3 acertos
    superior ao baseline.
    """
    print("\n" + "═"*78)
    print("🎯 CONCEITO 1: TOP QUINAS FREQUENTES")
    print("═"*78)
    print(f"   Treino: {treino_size} concursos | Teste: {teste_size} concursos | Top: {top_n}")
    
    rng = np.random.default_rng(42)
    
    # Sliding window para robustez
    total_windows = len(resultados) - treino_size - teste_size
    n_windows = min(total_windows, 15)
    if n_windows < 1:
        print("   ❌ Dados insuficientes!")
        return
    window_step = max(1, total_windows // n_windows)
    
    print(f"   Janelas deslizantes: {n_windows} (step={window_step})")
    
    # Acumuladores
    acertos_strat = {k: 0 for k in range(6)}   # 0,1,2,3,4,5 acertos
    acertos_rand = {k: 0 for k in range(6)}
    total_amostras = 0
    
    t0 = time.time()
    
    for w in range(n_windows):
        idx_start = w * window_step
        treino = resultados[idx_start:idx_start + treino_size]
        teste = resultados[idx_start + treino_size:idx_start + treino_size + teste_size]
        
        if len(teste) < teste_size:
            break
        
        # ─── Contar todas as quinas no treino ───
        quina_counter = Counter()
        for r in treino:
            nums = tuple(r['numeros'])  # já sorted
            for q in combinations(nums, 5):
                quina_counter[q] += 1
        
        # Top N quinas
        top_quinas = [set(q) for q, _ in quina_counter.most_common(top_n)]
        
        # Quinas aleatórias para comparação (mesma quantidade)
        random_quinas = []
        for _ in range(top_n):
            rq = set(rng.choice(range(1, 26), 5, replace=False).tolist())
            random_quinas.append(rq)
        
        # ─── Scoring no período de teste ───
        for r_teste in teste:
            resultado_set = set(r_teste['numeros'])
            
            for q in top_quinas:
                score = len(q & resultado_set)
                acertos_strat[score] += 1
            
            for q in random_quinas:
                score = len(q & resultado_set)
                acertos_rand[score] += 1
            
            total_amostras += top_n
        
        if (w + 1) % 5 == 0 or w == 0:
            elapsed = time.time() - t0
            print(f"   Janela {w+1}/{n_windows} ({elapsed:.1f}s)")
    
    # ─── Resultados ───
    print(f"\n   📊 RESULTADOS — {total_amostras:,} medições por método")
    print(f"   {'─'*70}")
    print(f"   {'Acertos na quina':>20s} {'Estratégia':>12s} {'Aleatório':>12s} {'Δ':>8s}  {'Esperado':>10s}")
    print(f"   {'─'*70}")
    
    # Distribuição esperada (hipergeométrica): quina=5, resultado=15, universo=25
    # P(k acertos) = C(5,k) * C(20,15-k) / C(25,15)
    from math import comb
    total_c = comb(25, 15)
    
    for k in range(6):
        s_pct = acertos_strat[k] / total_amostras * 100
        r_pct = acertos_rand[k] / total_amostras * 100
        esperado = comb(5, k) * comb(20, 15 - k) / total_c * 100
        delta = s_pct - r_pct
        marker = " ⭐" if delta > 1 and k >= 3 else ""
        print(f"   {'= ' + str(k):>20s} {s_pct:>11.2f}% {r_pct:>11.2f}% {delta:>+7.2f}%  {esperado:>9.2f}%{marker}")
    
    # Probabilidade de ≥3 acertos
    s_ge3 = sum(acertos_strat[k] for k in range(3, 6)) / total_amostras * 100
    r_ge3 = sum(acertos_rand[k] for k in range(3, 6)) / total_amostras * 100
    e_ge3 = sum(comb(5, k) * comb(20, 15 - k) for k in range(3, 6)) / total_c * 100
    
    print(f"   {'─'*70}")
    print(f"   {'≥3 acertos':>20s} {s_ge3:>11.2f}% {r_ge3:>11.2f}% {s_ge3-r_ge3:>+7.2f}%  {e_ge3:>9.2f}%")
    
    s_mean = sum(k * acertos_strat[k] for k in range(6)) / total_amostras
    r_mean = sum(k * acertos_rand[k] for k in range(6)) / total_amostras
    e_mean = 5 * 15 / 25  # = 3.0
    print(f"   {'Média acertos':>20s} {s_mean:>12.3f} {r_mean:>12.3f} {s_mean-r_mean:>+8.3f}  {e_mean:>10.3f}")
    
    # ─── Diagnóstico da premissa "acertar 3 de 5" ───
    print(f"\n   🔍 PREMISSA 'acertar exatamente 3 de 5':")
    print(f"   • Probabilidade teórica (hipergeom): {comb(5,3)*comb(20,12)/total_c*100:.1f}%")
    print(f"   • Observada (top quinas):            {acertos_strat[3]/total_amostras*100:.1f}%")
    print(f"   • Observada (aleatório):             {acertos_rand[3]/total_amostras*100:.1f}%")
    
    if s_ge3 > r_ge3 + 0.5:
        print(f"\n   ⭐ VANTAGEM para ≥3 acertos: +{s_ge3-r_ge3:.2f}pp acima do aleatório!")
    elif s_ge3 > r_ge3:
        print(f"\n   ✅ Vantagem marginal: +{s_ge3-r_ge3:.2f}pp")
    else:
        print(f"\n   ⚠️ Sem vantagem: {s_ge3-r_ge3:+.2f}pp")
    
    # ─── Quantas combos geraria a premissa "3 de 5"? ───
    print(f"\n   📐 EXPANSÃO: se fixamos 3 de uma top quina (C(5,3)=10 trios):")
    print(f"   • Cada trio → C(20,12) = {comb(20,12):,} combos para completar 15")
    print(f"   • Por quina: 10 × {comb(20,12):,} = {10*comb(20,12):,} combos")
    print(f"   • 5 quinas: 5 × {10*comb(20,12):,} = {5*10*comb(20,12):,} (com sobreposições)")
    print(f"   • Pool total C(25,15) = {total_c:,}")
    print(f"   • Redução teórica: {10*comb(20,12)/total_c*100:.1f}% por quina")
    
    return {'strat_ge3': s_ge3, 'rand_ge3': r_ge3, 'strat_mean': s_mean, 'rand_mean': r_mean}


# ══════════════════════════════════════════════════════════════════════════════
# CONCEITO 2: 10 AUSENTES → 5 VOLTAM → 252 COMBOS
# ══════════════════════════════════════════════════════════════════════════════

def poc_conceito2_ausentes(resultados, teste_inicio_idx=100, teste_size=500, mc_random=252):
    """
    10 Ausentes: números não sorteados no concurso anterior.
    
    Premissa: exatamente 5 dos 10 ausentes aparecem no próximo concurso.
    
    Estratégia:
    - Selecionar 10 "melhores" do anterior para manter (por freq últimos 30)
    - C(10,5)=252 combos: keep_10 ∪ {5 de absent_10}
    - Cada combo tem exatamente 15 números
    
    Comparação: 252 combos aleatórios de 15 números
    """
    print("\n" + "═"*78)
    print("🎯 CONCEITO 2: 10 AUSENTES → 5 VOLTAM → 252 COMBOS")
    print("═"*78)
    
    # ─── Fase 0: Distribuição histórica do K (quantos ausentes voltam) ───
    print("\n   📊 FASE 0: Distribuição de K (quantos dos 10 ausentes aparecem)")
    K_dist = Counter()
    rep_dist = Counter()
    for i in range(1, len(resultados)):
        prev = set(resultados[i-1]['numeros'])
        curr = set(resultados[i]['numeros'])
        absent = set(range(1, 26)) - prev
        K = len(curr & absent)
        rep = len(curr & prev)
        K_dist[K] += 1
        rep_dist[rep] += 1
    
    total = sum(K_dist.values())
    print(f"\n   {'K (novos)':>12s} {'Rep':>5s} {'Qtde':>7s} {'%':>7s} {'Acum':>7s}")
    acum = 0
    for k in sorted(K_dist.keys()):
        pct = K_dist[k] / total * 100
        acum += pct
        rep_k = 15 - k
        bar = "█" * int(pct / 2)
        print(f"   {k:>12d} {rep_k:>5d} {K_dist[k]:>7d} {pct:>6.1f}% {acum:>6.1f}% {bar}")
    
    media_K = sum(k * v for k, v in K_dist.items()) / total
    pct_K5 = K_dist.get(5, 0) / total * 100
    pct_K4a6 = sum(K_dist.get(k, 0) for k in [4, 5, 6]) / total * 100
    print(f"\n   📐 Média novos: {media_K:.2f} | K=5: {pct_K5:.1f}% | K∈[4,6]: {pct_K4a6:.1f}%")
    
    # ─── Fase 1: Teste com combos completos (15 números) ───
    print(f"\n   {'─'*70}")
    print(f"   🔬 FASE 1: 252 combos de 15 números (keep_10 + 5_from_absent)")
    
    actual_end = min(teste_inicio_idx + teste_size, len(resultados))
    n_testes = actual_end - teste_inicio_idx
    
    print(f"   Concursos: {resultados[teste_inicio_idx]['concurso']} a {resultados[actual_end-1]['concurso']} ({n_testes})")
    
    rng = np.random.default_rng(42)
    all_25 = np.arange(1, 26)
    
    # Acumuladores
    strat_acertos_dist = Counter()  # distribuição de melhor acerto por concurso
    rand_acertos_dist = Counter()
    strat_11_total = 0
    rand_11_total = 0
    strat_combos_total = 0
    rand_combos_total = 0
    
    # Detalhado por faixa de acerto (11,12,13,14,15) sobre TODAS as combos
    strat_faixa = Counter()
    rand_faixa = Counter()
    
    # Tracking para K real
    K_real_tracking = Counter()
    
    t0 = time.time()
    
    for i in range(teste_inicio_idx, actual_end):
        prev_set = set(resultados[i-1]['numeros'])
        result_set = set(resultados[i]['numeros'])
        absent = sorted(set(range(1, 26)) - prev_set)  # 10 números
        
        K_real = len(result_set & set(absent))
        K_real_tracking[K_real] += 1
        
        # ─── Selecionar keep_10: 10 mais frequentes do anterior ───
        # Frequência nos últimos 30 concursos antes deste
        freq = Counter()
        window_start = max(0, i - 31)
        for j in range(window_start, i - 1):
            for n in resultados[j]['numeros']:
                freq[n] += 1
        
        prev_list = sorted(prev_set)
        prev_by_freq = sorted(prev_list, key=lambda n: freq.get(n, 0), reverse=True)
        keep_10 = set(prev_by_freq[:10])
        
        # ─── ESTRATÉGIA: C(10,5) = 252 combos ───
        best_strat = 0
        n_combos_strat = 0
        for five in combinations(absent, 5):
            combo = keep_10 | set(five)
            acerto = len(combo & result_set)
            if acerto > best_strat:
                best_strat = acerto
            if acerto >= 11:
                strat_11_total += 1
                strat_faixa[acerto] += 1
            n_combos_strat += 1
        
        strat_acertos_dist[best_strat] += 1
        strat_combos_total += n_combos_strat
        
        # ─── ALEATÓRIO: 252 combos ───
        best_rand = 0
        for _ in range(mc_random):
            combo = set(rng.choice(all_25, 15, replace=False).tolist())
            acerto = len(combo & result_set)
            if acerto > best_rand:
                best_rand = acerto
            if acerto >= 11:
                rand_11_total += 1
                rand_faixa[acerto] += 1
        
        rand_acertos_dist[best_rand] += 1
        rand_combos_total += mc_random
        
        idx_rel = i - teste_inicio_idx + 1
        if idx_rel % 100 == 0 or idx_rel == 1:
            elapsed = time.time() - t0
            print(f"   Progresso: {idx_rel}/{n_testes} ({elapsed:.1f}s)")
    
    elapsed_total = time.time() - t0
    
    # ─── Resultados ───
    print(f"\n   {'═'*70}")
    print(f"   📊 RESULTADOS — {n_testes} concursos | 252 combos cada | {elapsed_total:.1f}s")
    print(f"   {'═'*70}")
    
    # Melhor acerto por concurso
    print(f"\n   MELHOR ACERTO por concurso (de 252 combos):")
    print(f"   {'Acertos':>12s} {'Estratégia':>12s} {'Aleatório':>12s} {'Δ':>8s}")
    print(f"   {'─'*48}")
    
    for k in sorted(set(list(strat_acertos_dist.keys()) + list(rand_acertos_dist.keys()))):
        if k < 11:
            continue
        s_n = strat_acertos_dist.get(k, 0)
        r_n = rand_acertos_dist.get(k, 0)
        s_pct = s_n / n_testes * 100
        r_pct = r_n / n_testes * 100
        delta = s_pct - r_pct
        marker = " ⭐" if delta > 2 else " ✅" if delta > 0 else ""
        print(f"   {k:>12d} {s_pct:>11.1f}% {r_pct:>11.1f}% {delta:>+7.1f}%{marker}")
    
    # Melhor ≥ 13
    s_ge13 = sum(strat_acertos_dist.get(k, 0) for k in range(13, 16)) / n_testes * 100
    r_ge13 = sum(rand_acertos_dist.get(k, 0) for k in range(13, 16)) / n_testes * 100
    print(f"   {'─'*48}")
    print(f"   {'≥13':>12s} {s_ge13:>11.1f}% {r_ge13:>11.1f}% {s_ge13-r_ge13:>+7.1f}%")
    
    s_ge14 = sum(strat_acertos_dist.get(k, 0) for k in range(14, 16)) / n_testes * 100
    r_ge14 = sum(rand_acertos_dist.get(k, 0) for k in range(14, 16)) / n_testes * 100
    print(f"   {'≥14':>12s} {s_ge14:>11.1f}% {r_ge14:>11.1f}% {s_ge14-r_ge14:>+7.1f}%")
    
    # Total 11+ sobre TODAS as combos
    print(f"\n   TAXA 11+ sobre TODAS as {strat_combos_total:,} combos:")
    s_tx = strat_11_total / strat_combos_total * 100
    r_tx = rand_11_total / rand_combos_total * 100
    seletiv = s_tx / r_tx if r_tx > 0 else 0
    
    print(f"   {'':>15s} {'Qtde':>10s} {'Taxa':>10s}")
    print(f"   {'Estratégia':>15s} {strat_11_total:>10,} {s_tx:>9.4f}%")
    print(f"   {'Aleatório':>15s} {rand_11_total:>10,} {r_tx:>9.4f}%")
    print(f"   {'Seletividade':>15s} {f'{seletiv:.3f}x':>10s}")
    
    # Detalhamento por faixa
    print(f"\n   Detalhamento 11+ (todas combos):")
    print(f"   {'Faixa':>10s} {'Estratégia':>12s} {'Aleatório':>12s} {'Selet':>8s}")
    print(f"   {'─'*46}")
    for faixa in [11, 12, 13, 14, 15]:
        s_f = strat_faixa.get(faixa, 0)
        r_f = rand_faixa.get(faixa, 0)
        s_pf = s_f / strat_combos_total * 100
        r_pf = r_f / rand_combos_total * 100
        sel_f = s_pf / r_pf if r_pf > 0 else float('inf')
        marker = " ⭐" if sel_f > 1.1 else ""
        print(f"   {faixa:>10d} {s_f:>10,d} ({s_pf:.4f}%) {r_f:>5,d} ({r_pf:.4f}%) {sel_f:>7.2f}x{marker}")
    
    # Qualidade da seleção keep_10
    print(f"\n   🔍 DIAGNÓSTICO keep_10 (freq-based):")
    print(f"   K real no período de teste:")
    for k in sorted(K_real_tracking.keys()):
        pct = K_real_tracking[k] / n_testes * 100
        print(f"     K={k}: {K_real_tracking[k]} ({pct:.1f}%)")
    
    if seletiv > 1.05:
        print(f"\n   ⭐ VANTAGEM! Seletividade {seletiv:.3f}x acima do aleatório")
    elif seletiv > 1.00:
        print(f"\n   ✅ Vantagem marginal: {seletiv:.3f}x")
    else:
        print(f"\n   ⚠️ Sem vantagem: {seletiv:.3f}x")
    
    return {'seletividade': seletiv, 'strat_11': strat_11_total, 'rand_11': rand_11_total}


# ══════════════════════════════════════════════════════════════════════════════
# CONCEITO 2B: VARIANTE — CONSTRAINT SAMPLING
# ══════════════════════════════════════════════════════════════════════════════

def poc_conceito2b_constraint_sampling(resultados, teste_inicio_idx=100, teste_size=500, n_samples=500):
    """
    Variante mais justa: amostrar combos COM e SEM a restrição "5 from absent".
    
    COM restrição: 5 random from absent_10 + 10 random from previous_15
    SEM restrição: 15 random from {1..25}
    
    Mesma quantidade de amostras para cada. Sem viés de "keep_10 fixo".
    """
    print("\n" + "═"*78)
    print("🎯 CONCEITO 2B: CONSTRAINT SAMPLING (5 absent + 10 repeat) vs RANDOM")
    print("═"*78)
    
    actual_end = min(teste_inicio_idx + teste_size, len(resultados))
    n_testes = actual_end - teste_inicio_idx
    
    print(f"   Concursos: {n_testes} | Amostras/concurso: {n_samples}")
    
    rng = np.random.default_rng(42)
    all_25 = np.arange(1, 26)
    
    strat_faixa = Counter()
    rand_faixa = Counter()
    total_combos = 0
    
    t0 = time.time()
    
    for i in range(teste_inicio_idx, actual_end):
        prev_nums = np.array(resultados[i-1]['numeros'])
        result_set = set(resultados[i]['numeros'])
        absent_nums = np.array(sorted(set(range(1, 26)) - set(prev_nums.tolist())))
        
        for _ in range(n_samples):
            # COM restrição: 5 random from absent + 10 random from previous
            five_new = set(rng.choice(absent_nums, 5, replace=False).tolist())
            ten_keep = set(rng.choice(prev_nums, 10, replace=False).tolist())
            combo_strat = five_new | ten_keep
            acerto_s = len(combo_strat & result_set)
            if acerto_s >= 11:
                strat_faixa[acerto_s] += 1
            
            # SEM restrição: 15 random from 25
            combo_rand = set(rng.choice(all_25, 15, replace=False).tolist())
            acerto_r = len(combo_rand & result_set)
            if acerto_r >= 11:
                rand_faixa[acerto_r] += 1
        
        total_combos += n_samples
        
        idx_rel = i - teste_inicio_idx + 1
        if idx_rel % 100 == 0 or idx_rel == 1:
            print(f"   Progresso: {idx_rel}/{n_testes} ({time.time()-t0:.1f}s)")
    
    elapsed = time.time() - t0
    
    # ─── Resultados ───
    print(f"\n   📊 RESULTADOS — {total_combos:,} combos cada | {elapsed:.1f}s")
    print(f"   {'Faixa':>10s} {'Constrained':>14s} {'Random':>14s} {'Selet':>8s}")
    print(f"   {'─'*50}")
    
    total_s = sum(strat_faixa.values())
    total_r = sum(rand_faixa.values())
    
    for faixa in [11, 12, 13, 14, 15]:
        s_f = strat_faixa.get(faixa, 0)
        r_f = rand_faixa.get(faixa, 0)
        s_pf = s_f / total_combos * 100
        r_pf = r_f / total_combos * 100
        sel = s_pf / r_pf if r_pf > 0 else float('inf')
        marker = " ⭐" if sel > 1.05 else ""
        print(f"   {faixa:>10d} {s_f:>8,d} ({s_pf:.4f}%) {r_f:>8,d} ({r_pf:.4f}%) {sel:>7.3f}x{marker}")
    
    s_total_tx = total_s / total_combos * 100
    r_total_tx = total_r / total_combos * 100
    seletiv = s_total_tx / r_total_tx if r_total_tx > 0 else 0
    
    print(f"   {'─'*50}")
    print(f"   {'11+ total':>10s} {total_s:>8,d} ({s_total_tx:.4f}%) {total_r:>8,d} ({r_total_tx:.4f}%) {seletiv:>7.3f}x")
    
    if seletiv > 1.05:
        print(f"\n   ⭐ CONSTRAINT TEM VANTAGEM! Seletividade {seletiv:.3f}x")
    elif seletiv > 1.00:
        print(f"\n   ✅ Vantagem marginal: {seletiv:.3f}x")
    else:
        print(f"\n   ⚠️ Sem vantagem: {seletiv:.3f}x")
    
    return {'seletividade': seletiv}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   POC: QUINAS FREQUENTES & AUSENTES — Análise de Vantagem          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    print("\n⏳ Carregando resultados...")
    resultados = carregar_resultados()
    print(f"✅ {len(resultados)} concursos carregados ({resultados[0]['concurso']} a {resultados[-1]['concurso']})")
    
    # ─── CONCEITO 1: Top Quinas ───
    t0 = time.time()
    r1 = poc_conceito1_quinas(resultados, treino_size=99, teste_size=200, top_n=5)
    print(f"\n⏱️ Conceito 1: {time.time()-t0:.1f}s")
    
    # ─── CONCEITO 2: Ausentes → 252 combos ───
    t0 = time.time()
    r2 = poc_conceito2_ausentes(resultados, teste_inicio_idx=100, teste_size=500, mc_random=252)
    print(f"\n⏱️ Conceito 2: {time.time()-t0:.1f}s")
    
    # ─── CONCEITO 2B: Constraint Sampling ───
    t0 = time.time()
    r2b = poc_conceito2b_constraint_sampling(resultados, teste_inicio_idx=100, teste_size=500, n_samples=500)
    print(f"\n⏱️ Conceito 2B: {time.time()-t0:.1f}s")
    
    # ─── RESUMO FINAL ───
    print("\n" + "═"*78)
    print("📋 RESUMO FINAL")
    print("═"*78)
    
    if r1:
        delta_q = r1['strat_ge3'] - r1['rand_ge3']
        status_q = "⭐ VANTAGEM" if delta_q > 0.5 else "✅ Marginal" if delta_q > 0 else "❌ Sem vantagem"
        print(f"   Conceito 1 (Top Quinas):    ≥3 acertos → {status_q} ({delta_q:+.2f}pp)")
    
    if r2:
        sel_2 = r2['seletividade']
        status_a = "⭐ VANTAGEM" if sel_2 > 1.05 else "✅ Marginal" if sel_2 > 1.0 else "❌ Sem vantagem"
        print(f"   Conceito 2 (Ausentes 252):  Seletividade → {status_a} ({sel_2:.3f}x)")
    
    if r2b:
        sel_2b = r2b['seletividade']
        status_b = "⭐ VANTAGEM" if sel_2b > 1.05 else "✅ Marginal" if sel_2b > 1.0 else "❌ Sem vantagem"
        print(f"   Conceito 2B (Constraint):   Seletividade → {status_b} ({sel_2b:.3f}x)")
    
    print(f"\n{'═'*78}")
    print("✅ POC COMPLETO!")
