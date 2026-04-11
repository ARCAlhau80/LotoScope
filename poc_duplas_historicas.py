# -*- coding: utf-8 -*-
"""
POC: Duplas Históricas → Combinações Estruturadas vs Aleatório
===============================================================
Conceito: Top duplas (co-ocorrência) até concurso de corte.
Regra: {1, 25} fixos + 13 números das duplas (alternando elementos)
       Jogo A pega 1º elemento, Jogo B pega 2º elemento.
       
Lotofácil: 25 números, 15 sorteados, C(25,15) = 3.268.760
"""

import pyodbc
import numpy as np
from itertools import combinations
from collections import Counter
import time

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def carregar_resultados():
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


def calcular_ranking_duplas(resultados_treino):
    """Conta co-ocorrência de todas as C(25,2)=300 duplas."""
    pair_count = Counter()
    for r in resultados_treino:
        nums = r['numeros']
        for pair in combinations(nums, 2):
            pair_count[pair] += 1
    return pair_count


def gerar_combos_duplas(pair_ranking, fixos={1, 25}, target_size=15):
    """
    Gera combinações usando duplas rankeadas.
    
    Regra:
    - {1, 25} são sempre fixos
    - Percorre duplas em ordem de ranking
    - Jogo A recebe 1º elemento, Jogo B recebe 2º
    - Quando um jogo atinge 15, fecha e começa outro
    - Duplas que contenham 1 ou 25 são usadas (o outro elemento entra no jogo)
    
    Retorna lista de combos (sets de 15 números)
    """
    need = target_size - len(fixos)  # 13 números extras
    
    # Filtrar duplas: remover onde ambos são fixos
    pairs_usaveis = []
    for (a, b), freq in pair_ranking.most_common():
        if a in fixos and b in fixos:
            continue
        pairs_usaveis.append((a, b, freq))
    
    combos = []
    idx = 0
    
    while idx < len(pairs_usaveis):
        # Construir par de jogos (A e B)
        jogo_a = set(fixos)
        jogo_b = set(fixos)
        
        scan_idx = idx
        pairs_usadas = 0
        
        while scan_idx < len(pairs_usaveis):
            a, b, _ = pairs_usaveis[scan_idx]
            scan_idx += 1
            
            # Para duplas com fixo: o não-fixo vai para ambos os jogos
            if a in fixos:
                if b not in jogo_a and len(jogo_a) < target_size:
                    jogo_a.add(b)
                if b not in jogo_b and len(jogo_b) < target_size:
                    jogo_b.add(b)
                pairs_usadas += 1
            elif b in fixos:
                if a not in jogo_a and len(jogo_a) < target_size:
                    jogo_a.add(a)
                if a not in jogo_b and len(jogo_b) < target_size:
                    jogo_b.add(a)
                pairs_usadas += 1
            else:
                # Dupla normal: A pega 1º, B pega 2º
                added = False
                if a not in jogo_a and len(jogo_a) < target_size:
                    jogo_a.add(a)
                    added = True
                if b not in jogo_b and len(jogo_b) < target_size:
                    jogo_b.add(b)
                    added = True
                if added:
                    pairs_usadas += 1
            
            # Ambos cheios? 
            if len(jogo_a) >= target_size and len(jogo_b) >= target_size:
                break
        
        # Se um jogo não encheu, completar com números mais frequentes disponíveis
        all_numbers = list(range(1, 26))
        for jogo in [jogo_a, jogo_b]:
            if len(jogo) < target_size:
                for n in all_numbers:
                    if n not in jogo:
                        jogo.add(n)
                        if len(jogo) >= target_size:
                            break
        
        if len(jogo_a) == target_size:
            combos.append(frozenset(jogo_a))
        if len(jogo_b) == target_size:
            combos.append(frozenset(jogo_b))
        
        # Avançar para próximas duplas não usadas
        idx = scan_idx
        
        if pairs_usadas == 0:
            break  # Não conseguiu usar nenhuma dupla nova
    
    # Remover duplicatas
    combos = list(set(combos))
    return [set(c) for c in combos]


def gerar_combos_duplas_v2(pair_ranking, fixos={1, 25}, target_size=15, max_combos=500):
    """
    V2: Abordagem mais agressiva — para cada TOP dupla, gerar um jogo.
    
    Para dupla (a,b), jogo = {1, 25, a, b} + top 11 números restantes por frequência individual.
    Garante que a dupla está presente na combinação.
    """
    # Frequência individual
    freq_individual = Counter()
    for (a, b), f in pair_ranking.items():
        freq_individual[a] += f
        freq_individual[b] += f
    
    # Top números ordenados
    nums_ranked = [n for n, _ in freq_individual.most_common()]
    
    combos = []
    seen = set()
    
    for (a, b), freq in pair_ranking.most_common(max_combos * 2):
        jogo = set(fixos) | {a, b}
        
        # Completar com top números
        for n in nums_ranked:
            if n not in jogo:
                jogo.add(n)
                if len(jogo) >= target_size:
                    break
        
        key = frozenset(jogo)
        if key not in seen and len(jogo) == target_size:
            seen.add(key)
            combos.append(jogo)
        
        if len(combos) >= max_combos:
            break
    
    return combos


def gerar_combos_duplas_v3(pair_ranking, fixos={1, 25}, target_size=15, max_combos=200):
    """
    V3: Caminhar pela cadeia de duplas — cada jogo é construído
    encadeando duplas correlacionadas.
    
    Jogo 1: pega dupla #1 (a,b) → depois dupla #2 que contém a ou b → ...
    Jogo 2: começa com dupla que não foi usada no jogo 1
    """
    need = target_size - len(fixos)
    pairs_list = [(a, b) for (a, b), _ in pair_ranking.most_common()]
    
    combos = []
    used_starts = set()
    
    for start_idx in range(min(len(pairs_list), max_combos)):
        a0, b0 = pairs_list[start_idx]
        
        jogo = set(fixos)
        jogo.add(a0)
        jogo.add(b0)
        
        # Encadear: procurar próxima dupla que intersecta com o jogo atual
        for (a, b), _ in pair_ranking.most_common():
            if len(jogo) >= target_size:
                break
            # Pelo menos um elemento já no jogo (cadeia)
            if a in jogo or b in jogo:
                if a not in jogo and len(jogo) < target_size:
                    jogo.add(a)
                if b not in jogo and len(jogo) < target_size:
                    jogo.add(b)
        
        if len(jogo) == target_size:
            key = frozenset(jogo)
            if key not in {frozenset(c) for c in combos}:
                combos.append(jogo)
        
        if len(combos) >= max_combos:
            break
    
    return combos


def avaliar_combos(combos, resultados_teste, rng, label=""):
    """Avalia combos vs mesma quantidade de combos aleatórios."""
    n_combos = len(combos)
    n_testes = len(resultados_teste)
    all_25 = np.arange(1, 26)
    
    # Acumuladores
    strat_faixa = Counter()
    rand_faixa = Counter()
    strat_best_per_contest = []
    rand_best_per_contest = []
    
    for r in resultados_teste:
        result_set = set(r['numeros'])
        
        # Estratégia
        best_s = 0
        for combo in combos:
            acerto = len(combo & result_set)
            if acerto >= 11:
                strat_faixa[acerto] += 1
            best_s = max(best_s, acerto)
        strat_best_per_contest.append(best_s)
        
        # Aleatório (mesma quantidade)
        best_r = 0
        for _ in range(n_combos):
            combo_r = set(rng.choice(all_25, 15, replace=False).tolist())
            acerto_r = len(combo_r & result_set)
            if acerto_r >= 11:
                rand_faixa[acerto_r] += 1
            best_r = max(best_r, acerto_r)
        rand_best_per_contest.append(best_r)
    
    total_combos = n_combos * n_testes
    
    # Taxa 11+
    s_11 = sum(strat_faixa.values())
    r_11 = sum(rand_faixa.values())
    s_tx = s_11 / total_combos * 100 if total_combos > 0 else 0
    r_tx = r_11 / total_combos * 100 if total_combos > 0 else 0
    seletiv = s_tx / r_tx if r_tx > 0 else 0
    
    # Melhor por concurso
    s_best_mean = np.mean(strat_best_per_contest)
    r_best_mean = np.mean(rand_best_per_contest)
    s_ge13 = sum(1 for x in strat_best_per_contest if x >= 13) / n_testes * 100
    r_ge13 = sum(1 for x in rand_best_per_contest if x >= 13) / n_testes * 100
    s_ge14 = sum(1 for x in strat_best_per_contest if x >= 14) / n_testes * 100
    r_ge14 = sum(1 for x in rand_best_per_contest if x >= 14) / n_testes * 100
    s_15 = sum(1 for x in strat_best_per_contest if x == 15) / n_testes * 100
    r_15 = sum(1 for x in rand_best_per_contest if x == 15) / n_testes * 100
    
    return {
        'label': label,
        'n_combos': n_combos,
        'seletividade': seletiv,
        'strat_faixa': strat_faixa,
        'rand_faixa': rand_faixa,
        's_tx': s_tx, 'r_tx': r_tx,
        's_best_mean': s_best_mean, 'r_best_mean': r_best_mean,
        's_ge13': s_ge13, 'r_ge13': r_ge13,
        's_ge14': s_ge14, 'r_ge14': r_ge14,
        's_15': s_15, 'r_15': r_15,
        'total_combos': total_combos,
    }


def imprimir_resultado(res):
    label = res['label']
    print(f"\n   {'─'*70}")
    print(f"   📊 {label} — {res['n_combos']} combos")
    print(f"   {'─'*70}")
    
    print(f"\n   TAXA 11+ sobre TODAS combos×concursos ({res['total_combos']:,}):")
    print(f"   {'':>15s} {'Taxa':>10s}")
    print(f"   {'Estratégia':>15s} {res['s_tx']:>9.4f}%")
    print(f"   {'Aleatório':>15s} {res['r_tx']:>9.4f}%")
    print(f"   {'Seletividade':>15s} {res['seletividade']:>9.3f}x")
    
    print(f"\n   Detalhamento 11+:")
    print(f"   {'Faixa':>10s} {'Estratégia':>12s} {'Aleatório':>12s} {'Selet':>8s}")
    print(f"   {'─'*46}")
    for faixa in [11, 12, 13, 14, 15]:
        s_f = res['strat_faixa'].get(faixa, 0)
        r_f = res['rand_faixa'].get(faixa, 0)
        s_pf = s_f / res['total_combos'] * 100 if res['total_combos'] > 0 else 0
        r_pf = r_f / res['total_combos'] * 100 if res['total_combos'] > 0 else 0
        sel = s_pf / r_pf if r_pf > 0 else float('inf')
        marker = " ⭐" if sel > 1.10 else " ✅" if sel > 1.02 else ""
        print(f"   {faixa:>10d} {s_f:>7,d} ({s_pf:.4f}%) {r_f:>7,d} ({r_pf:.4f}%) {sel:>7.3f}x{marker}")
    
    print(f"\n   MELHOR ACERTO por concurso:")
    print(f"   {'':>15s} {'Estratégia':>12s} {'Aleatório':>12s} {'Δ':>8s}")
    print(f"   {'Média':>15s} {res['s_best_mean']:>12.2f} {res['r_best_mean']:>12.2f} {res['s_best_mean']-res['r_best_mean']:>+8.2f}")
    print(f"   {'≥13':>15s} {res['s_ge13']:>11.1f}% {res['r_ge13']:>11.1f}% {res['s_ge13']-res['r_ge13']:>+7.1f}%")
    print(f"   {'≥14':>15s} {res['s_ge14']:>11.1f}% {res['r_ge14']:>11.1f}% {res['s_ge14']-res['r_ge14']:>+7.1f}%")
    print(f"   {'=15':>15s} {res['s_15']:>11.1f}% {res['r_15']:>11.1f}% {res['s_15']-res['r_15']:>+7.1f}%")
    
    if res['seletividade'] > 1.05:
        print(f"\n   ⭐ VANTAGEM! Seletividade {res['seletividade']:.3f}x")
    elif res['seletividade'] > 1.00:
        print(f"\n   ✅ Vantagem marginal: {res['seletividade']:.3f}x")
    else:
        print(f"\n   ⚠️ Sem vantagem: {res['seletividade']:.3f}x")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   POC: DUPLAS HISTÓRICAS → COMBINAÇÕES ESTRUTURADAS                ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    print("\n⏳ Carregando resultados...")
    resultados = carregar_resultados()
    print(f"✅ {len(resultados)} concursos ({resultados[0]['concurso']} a {resultados[-1]['concurso']})")
    
    rng = np.random.default_rng(42)
    
    # ═══════════════════════════════════════════════════════════════════
    # SLIDING WINDOW para robustez
    # Treino: 200 concursos | Teste: 200 concursos | 10 janelas
    # ═══════════════════════════════════════════════════════════════════
    TREINO_SIZE = 200
    TESTE_SIZE = 200
    TOTAL_NEEDED = TREINO_SIZE + TESTE_SIZE
    
    total_windows = len(resultados) - TOTAL_NEEDED
    N_WINDOWS = min(10, total_windows // 100)
    window_step = max(1, total_windows // N_WINDOWS) if N_WINDOWS > 0 else 1
    
    print(f"\n📐 Config: treino={TREINO_SIZE}, teste={TESTE_SIZE}, janelas={N_WINDOWS}, step={window_step}")
    
    # ═══════════════════════════════════════════════════════════════════
    # FASE 0: Análise das duplas
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "═"*78)
    print("📊 FASE 0: Análise das Duplas (primeira janela)")
    print("═"*78)
    
    treino_0 = resultados[:TREINO_SIZE]
    pair_ranking_0 = calcular_ranking_duplas(treino_0)
    
    # Top 20 duplas
    print(f"\n   TOP 20 DUPLAS (co-ocorrência em {TREINO_SIZE} concursos):")
    print(f"   {'#':>4s} {'Dupla':>10s} {'Freq':>6s} {'%':>7s} {'Esperado':>10s} {'Lift':>6s}")
    print(f"   {'─'*48}")
    
    from math import comb
    p_esperada = comb(23, 13) / comb(25, 15)  # P(ambos presentes) = C(23,13)/C(25,15)
    freq_esperada = TREINO_SIZE * p_esperada
    
    for i, ((a, b), freq) in enumerate(pair_ranking_0.most_common(20)):
        pct = freq / TREINO_SIZE * 100
        lift = freq / freq_esperada
        print(f"   {i+1:>4d} ({a:>2d},{b:>2d})    {freq:>5d} {pct:>6.1f}%  {freq_esperada:>9.1f}  {lift:>5.2f}x")
    
    # Distribuição geral
    freqs = [f for _, f in pair_ranking_0.items()]
    print(f"\n   Média: {np.mean(freqs):.1f} | Mediana: {np.median(freqs):.1f} | Max: {max(freqs)} | Min: {min(freqs)}")
    print(f"   Esperado (teórico): {freq_esperada:.1f} por dupla em {TREINO_SIZE} concursos")
    print(f"   P(ambos num resultado) = C(23,13)/C(25,15) = {p_esperada*100:.1f}%")
    
    # Verificar fixos {1, 25}
    duplas_com_1 = [(a, b, f) for (a, b), f in pair_ranking_0.most_common() if a == 1 or b == 1]
    duplas_com_25 = [(a, b, f) for (a, b), f in pair_ranking_0.most_common() if a == 25 or b == 25]
    
    freq_1 = sum(1 for r in treino_0 if 1 in r['numeros']) / TREINO_SIZE * 100
    freq_25 = sum(1 for r in treino_0 if 25 in r['numeros']) / TREINO_SIZE * 100
    print(f"\n   Fixos: freq(1) = {freq_1:.1f}% | freq(25) = {freq_25:.1f}%")
    print(f"   Duplas com 1: {len(duplas_com_1)} | Duplas com 25: {len(duplas_com_25)}")
    
    # ═══════════════════════════════════════════════════════════════════
    # FASE 1: Gerar e testar combos — 3 variantes
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "═"*78)
    print("🔬 FASE 1: Geração e Teste — 3 Variantes × {} janelas".format(N_WINDOWS))
    print("═"*78)
    
    # Acumuladores globais por variante
    acum = {
        'V1': {'strat_faixa': Counter(), 'rand_faixa': Counter(), 
               'best_s': [], 'best_r': [], 'total': 0, 'n_combos': []},
        'V2': {'strat_faixa': Counter(), 'rand_faixa': Counter(), 
               'best_s': [], 'best_r': [], 'total': 0, 'n_combos': []},
        'V3': {'strat_faixa': Counter(), 'rand_faixa': Counter(), 
               'best_s': [], 'best_r': [], 'total': 0, 'n_combos': []},
    }
    
    t0 = time.time()
    all_25 = np.arange(1, 26)
    
    for w in range(N_WINDOWS):
        idx_start = w * window_step
        treino = resultados[idx_start:idx_start + TREINO_SIZE]
        teste = resultados[idx_start + TREINO_SIZE:idx_start + TOTAL_NEEDED]
        
        if len(teste) < TESTE_SIZE:
            break
        
        pair_ranking = calcular_ranking_duplas(treino)
        
        # Gerar combos com 3 variantes
        combos_v1 = gerar_combos_duplas(pair_ranking, fixos={1, 25})
        combos_v2 = gerar_combos_duplas_v2(pair_ranking, fixos={1, 25}, max_combos=100)
        combos_v3 = gerar_combos_duplas_v3(pair_ranking, fixos={1, 25}, max_combos=100)
        
        variants = {
            'V1': combos_v1,
            'V2': combos_v2[:len(combos_v1)] if len(combos_v1) > 0 else combos_v2[:50],
            'V3': combos_v3[:len(combos_v1)] if len(combos_v1) > 0 else combos_v3[:50],
        }
        
        for vname, combos in variants.items():
            if not combos:
                continue
            
            n_c = len(combos)
            acum[vname]['n_combos'].append(n_c)
            
            for r in teste:
                result_set = set(r['numeros'])
                
                best_s = 0
                for combo in combos:
                    acerto = len(combo & result_set)
                    if acerto >= 11:
                        acum[vname]['strat_faixa'][acerto] += 1
                    best_s = max(best_s, acerto)
                acum[vname]['best_s'].append(best_s)
                
                best_r = 0
                for _ in range(n_c):
                    combo_r = set(rng.choice(all_25, 15, replace=False).tolist())
                    acerto_r = len(combo_r & result_set)
                    if acerto_r >= 11:
                        acum[vname]['rand_faixa'][acerto_r] += 1
                    best_r = max(best_r, acerto_r)
                acum[vname]['best_r'].append(best_r)
                
                acum[vname]['total'] += n_c
        
        elapsed = time.time() - t0
        conc_treino = f"{treino[0]['concurso']}-{treino[-1]['concurso']}"
        conc_teste = f"{teste[0]['concurso']}-{teste[-1]['concurso']}"
        n1 = len(combos_v1)
        n2 = len(variants['V2'])
        n3 = len(variants['V3'])
        print(f"   Janela {w+1}/{N_WINDOWS}: treino={conc_treino} teste={conc_teste} "
              f"V1={n1} V2={n2} V3={n3} ({elapsed:.1f}s)")
    
    elapsed_total = time.time() - t0
    
    # ═══════════════════════════════════════════════════════════════════
    # RESULTADOS
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n{'═'*78}")
    print(f"📊 RESULTADOS CONSOLIDADOS — {N_WINDOWS} janelas × {TESTE_SIZE} concursos ({elapsed_total:.1f}s)")
    print(f"{'═'*78}")
    
    for vname, label in [
        ('V1', 'V1: Alternância A/B (regra original)'),
        ('V2', 'V2: Top dupla + completar com melhores individuais'),
        ('V3', 'V3: Cadeia encadeada de duplas'),
    ]:
        d = acum[vname]
        if d['total'] == 0:
            print(f"\n   {label}: SEM DADOS")
            continue
        
        avg_combos = np.mean(d['n_combos']) if d['n_combos'] else 0
        s_11 = sum(d['strat_faixa'].values())
        r_11 = sum(d['rand_faixa'].values())
        s_tx = s_11 / d['total'] * 100
        r_tx = r_11 / d['total'] * 100
        seletiv = s_tx / r_tx if r_tx > 0 else 0
        
        s_best = np.mean(d['best_s'])
        r_best = np.mean(d['best_r'])
        
        n_contests = len(d['best_s'])
        s_ge13 = sum(1 for x in d['best_s'] if x >= 13) / n_contests * 100
        r_ge13 = sum(1 for x in d['best_r'] if x >= 13) / n_contests * 100
        s_ge14 = sum(1 for x in d['best_s'] if x >= 14) / n_contests * 100
        r_ge14 = sum(1 for x in d['best_r'] if x >= 14) / n_contests * 100
        s_15 = sum(1 for x in d['best_s'] if x == 15) / n_contests * 100
        r_15 = sum(1 for x in d['best_r'] if x == 15) / n_contests * 100
        
        print(f"\n   {'─'*70}")
        print(f"   📊 {label}")
        print(f"   Combos médio: {avg_combos:.0f} | Total medições: {d['total']:,}")
        print(f"   {'─'*70}")
        
        print(f"\n   TAXA 11+ (todas combos×concursos):")
        print(f"   {'':>15s} {'Qtde':>10s} {'Taxa':>10s}")
        print(f"   {'Estratégia':>15s} {s_11:>10,d} {s_tx:>9.4f}%")
        print(f"   {'Aleatório':>15s} {r_11:>10,d} {r_tx:>9.4f}%")
        print(f"   {'Seletividade':>15s} {'':>10s} {seletiv:>9.3f}x")
        
        print(f"\n   Detalhamento:")
        print(f"   {'Faixa':>8s} {'Estrat':>10s} {'Aleat':>10s} {'Selet':>8s}")
        for faixa in [11, 12, 13, 14, 15]:
            sf = d['strat_faixa'].get(faixa, 0)
            rf = d['rand_faixa'].get(faixa, 0)
            sp = sf / d['total'] * 100
            rp = rf / d['total'] * 100
            sel = sp / rp if rp > 0 else float('inf')
            marker = " ⭐" if sel > 1.10 else " ✅" if sel > 1.02 else ""
            print(f"   {faixa:>8d} {sf:>7,d} ({sp:.3f}%) {rf:>7,d} ({rp:.3f}%) {sel:>7.3f}x{marker}")
        
        print(f"\n   MELHOR por concurso ({n_contests}):")
        print(f"   {'':>15s} {'Estrat':>10s} {'Aleat':>10s} {'Δ':>8s}")
        print(f"   {'Média melhor':>15s} {s_best:>10.2f} {r_best:>10.2f} {s_best-r_best:>+8.2f}")
        print(f"   {'≥13':>15s} {s_ge13:>9.1f}% {r_ge13:>9.1f}% {s_ge13-r_ge13:>+7.1f}%")
        print(f"   {'≥14':>15s} {s_ge14:>9.1f}% {r_ge14:>9.1f}% {s_ge14-r_ge14:>+7.1f}%")
        print(f"   {'=15':>15s} {s_15:>9.1f}% {r_15:>9.1f}% {s_15-r_15:>+7.1f}%")
        
        if seletiv > 1.05:
            print(f"\n   ⭐ VANTAGEM: {seletiv:.3f}x")
        elif seletiv > 1.00:
            print(f"\n   ✅ Marginal: {seletiv:.3f}x")
        else:
            print(f"\n   ⚠️ Sem vantagem: {seletiv:.3f}x")
    
    # ═══════════════════════════════════════════════════════════════════
    # ANÁLISE TEÓRICA
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n{'═'*78}")
    print(f"🧮 ANÁLISE TEÓRICA")
    print(f"{'═'*78}")
    
    print(f"\n   Lotofácil: 25 números, 15 sorteados")
    print(f"   P(dupla co-ocorre) = C(23,13)/C(25,15) = {p_esperada*100:.1f}%")
    print(f"   P(número sai) = 15/25 = 60%")
    print(f"   P(número NÃO sai) = 40%")
    print(f"\n   Para fixos {{1, 25}}:")
    print(f"   • P(1 sai E 25 sai) = C(23,13)/C(25,15) = {p_esperada*100:.1f}%")
    print(f"   • Num concurso com ambos: combo já tem 2/15 corretos")
    print(f"   • Num concurso sem um: máximo 14 acertos possíveis")
    pct_both = sum(1 for r in resultados if 1 in r['numeros'] and 25 in r['numeros']) / len(resultados) * 100
    pct_none = sum(1 for r in resultados if 1 not in r['numeros'] and 25 not in r['numeros']) / len(resultados) * 100
    pct_one = 100 - pct_both - pct_none
    print(f"\n   Histórico real:")
    print(f"   • 1 E 25 presentes: {pct_both:.1f}%")
    print(f"   • Só um dos dois:   {pct_one:.1f}%")
    print(f"   • Nenhum:           {pct_none:.1f}%")
    print(f"   • ⚠️ Em {100-pct_both:.1f}% dos concursos, fixar {{1,25}} LIMITA o acerto máximo!")
    
    print(f"\n{'═'*78}")
    print(f"✅ POC COMPLETO!")
