# -*- coding: utf-8 -*-
"""
POC: Vizinhança histórica para escolha de nível estrutural do Pool 23

Ideia:
- Representar o contexto pré-concurso por um vetor de features simples
- Buscar concursos anteriores mais parecidos
- Ver, nesses vizinhos, quais níveis estruturais preservaram melhor o sorteio real
- Comparar política de recomendação por vizinhança vs baseline global acumulado

Observação:
- Esta POC usa apenas o pacote estrutural por nível (níveis 1-6)
- O objetivo não é prever números, mas recomendar o perfil de pacote mais compatível
  com o contexto recente
"""

import sys
from collections import Counter, defaultdict

import numpy as np

from poc_incompatibilidade_filtros_pool23 import (
    RANDOM_SAMPLES,
    build_filters_for_level,
    carregar_resultados,
    random_combos,
)

sys.stdout.reconfigure(encoding='utf-8')

LEVELS = [1, 2, 3, 4, 5, 6]
FEATURE_WINDOW = 12
K_NEIGHBORS = 40
MIN_HISTORY = 200

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}


def package_predicates():
    predicates = {}
    for level in LEVELS:
        filters = build_filters_for_level(level)
        predicates[level] = lambda combo, fns=list(filters.values()): all(fn(combo) for fn in fns)
    return predicates


def combo_stats(combo):
    nums = list(combo)
    pares = sum(1 for n in nums if n % 2 == 0)
    primos = sum(1 for n in nums if n in PRIMOS)
    fib = sum(1 for n in nums if n in FIBONACCI)
    faixa_6_20 = sum(1 for n in nums if 6 <= n <= 20)
    moldura = sum(1 for n in nums if n in {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25})
    centro = 15 - moldura
    linhas = [0, 0, 0, 0, 0]
    cols = [0, 0, 0, 0, 0]
    for n in nums:
        linhas[(n - 1) // 5] += 1
        cols[(n - 1) % 5] += 1
    seq_max = 1
    seq = 1
    nums_sorted = sorted(nums)
    for idx in range(1, len(nums_sorted)):
        if nums_sorted[idx] == nums_sorted[idx - 1] + 1:
            seq += 1
            seq_max = max(seq_max, seq)
        else:
            seq = 1
    return {
        'sum': sum(nums),
        'pares': pares,
        'primos': primos,
        'fib': fib,
        'faixa_6_20': faixa_6_20,
        'moldura': moldura,
        'centro': centro,
        'linha_spread': max(linhas) - min(linhas),
        'col_spread': max(cols) - min(cols),
        'seq_max': seq_max,
        'count_1_25': int(1 in nums) + int(25 in nums),
    }


def build_context_features(draws):
    contexts = []
    for idx in range(len(draws)):
        if idx < FEATURE_WINDOW:
            contexts.append(None)
            continue

        recent = draws[idx - FEATURE_WINDOW:idx]
        recent_stats = [combo_stats(d['numeros']) for d in recent]
        last_stats = recent_stats[-1]
        prev_draw = set(draws[idx - 2]['numeros']) if idx >= 2 else set()
        last_draw = set(draws[idx - 1]['numeros'])
        repeats_last = len(last_draw & prev_draw) if prev_draw else 0

        freq_counter = Counter()
        for draw in recent:
            freq_counter.update(draw['numeros'])

        hot_12 = sum(1 for _, f in freq_counter.items() if f >= 8)
        warm_12 = sum(1 for _, f in freq_counter.items() if f >= 6)
        cold_12 = sum(1 for n in range(1, 26) if freq_counter[n] <= 2)
        absent_12 = sum(1 for n in range(1, 26) if freq_counter[n] == 0)

        vec = np.array([
            last_stats['sum'],
            last_stats['pares'],
            last_stats['primos'],
            last_stats['fib'],
            last_stats['faixa_6_20'],
            last_stats['moldura'],
            last_stats['linha_spread'],
            last_stats['col_spread'],
            last_stats['seq_max'],
            last_stats['count_1_25'],
            repeats_last,
            np.mean([s['sum'] for s in recent_stats]),
            np.std([s['sum'] for s in recent_stats]),
            np.mean([s['pares'] for s in recent_stats]),
            np.mean([s['primos'] for s in recent_stats]),
            np.mean([s['fib'] for s in recent_stats]),
            np.mean([s['faixa_6_20'] for s in recent_stats]),
            np.mean([s['seq_max'] for s in recent_stats]),
            hot_12,
            warm_12,
            cold_12,
            absent_12,
            freq_counter[1],
            freq_counter[25],
        ], dtype=float)
        contexts.append(vec)
    return contexts


def standardize_matrix(matrix):
    mu = np.mean(matrix, axis=0)
    sigma = np.std(matrix, axis=0)
    sigma[sigma == 0] = 1.0
    return (matrix - mu) / sigma


def choose_best_level(scores_by_level):
    return sorted(scores_by_level.items(), key=lambda x: (-x[1], x[0]))[0][0]


def main():
    print('=' * 78)
    print('POC — VIZINHANCA HISTORICA PARA ESCOLHA DE NIVEL')
    print('=' * 78)
    print(f'Janela de features: {FEATURE_WINDOW}')
    print(f'K vizinhos: {K_NEIGHBORS}')
    print(f'Histórico mínimo: {MIN_HISTORY}')

    draws = carregar_resultados()
    predicates = package_predicates()
    rng = np.random.default_rng(42)
    random_draws = random_combos(RANDOM_SAMPLES, rng)

    random_pass_rate = {}
    for level in LEVELS:
        pred = predicates[level]
        random_pass_rate[level] = sum(1 for combo in random_draws if pred(combo)) / len(random_draws)

    contexts = build_context_features(draws)
    pass_matrix = {level: [] for level in LEVELS}
    utility_matrix = {level: [] for level in LEVELS}
    for draw in draws:
        combo = draw['numeros']
        for level in LEVELS:
            passed = 1 if predicates[level](combo) else 0
            pass_matrix[level].append(passed)
            utility_matrix[level].append(passed / random_pass_rate[level] if random_pass_rate[level] > 0 else 0.0)

    all_valid_idx = [idx for idx, ctx in enumerate(contexts) if ctx is not None]
    context_matrix = np.vstack([contexts[idx] for idx in all_valid_idx])
    context_matrix = standardize_matrix(context_matrix)
    idx_to_row = {idx: pos for pos, idx in enumerate(all_valid_idx)}

    results = {
        'neighbor_hit': 0,
        'global_hit': 0,
        'static_hit': 0,
        'neighbor_utility': [],
        'global_utility': [],
        'static_utility': [],
        'neighbor_levels': Counter(),
        'global_levels': Counter(),
        'neighbor_when_better': 0,
        'global_when_better': 0,
        'equal': 0,
    }

    static_scores = {
        level: np.mean(utility_matrix[level][MIN_HISTORY:])
        for level in LEVELS
    }
    static_best_level = choose_best_level(static_scores)

    eval_count = 0
    for idx in all_valid_idx:
        if idx < max(MIN_HISTORY, FEATURE_WINDOW + 1):
            continue

        target_row = context_matrix[idx_to_row[idx]]
        candidate_idx = [j for j in all_valid_idx if j < idx]
        candidate_rows = np.vstack([context_matrix[idx_to_row[j]] for j in candidate_idx])
        dists = np.linalg.norm(candidate_rows - target_row, axis=1)
        nearest_order = np.argsort(dists)[:K_NEIGHBORS]
        neighbors = [candidate_idx[pos] for pos in nearest_order]

        neighbor_scores = {}
        global_scores = {}
        for level in LEVELS:
            neighbor_scores[level] = float(np.mean([utility_matrix[level][j] for j in neighbors]))
            global_scores[level] = float(np.mean(utility_matrix[level][:idx]))

        neighbor_level = choose_best_level(neighbor_scores)
        global_level = choose_best_level(global_scores)

        n_util = utility_matrix[neighbor_level][idx]
        g_util = utility_matrix[global_level][idx]
        s_util = utility_matrix[static_best_level][idx]

        results['neighbor_levels'][neighbor_level] += 1
        results['global_levels'][global_level] += 1
        results['neighbor_utility'].append(n_util)
        results['global_utility'].append(g_util)
        results['static_utility'].append(s_util)
        results['neighbor_hit'] += pass_matrix[neighbor_level][idx]
        results['global_hit'] += pass_matrix[global_level][idx]
        results['static_hit'] += pass_matrix[static_best_level][idx]

        if n_util > g_util:
            results['neighbor_when_better'] += 1
        elif g_util > n_util:
            results['global_when_better'] += 1
        else:
            results['equal'] += 1
        eval_count += 1

    print('\n1) Pass rate estrutural random por nivel')
    print(f"{'Nivel':<8} {'RandomPass':>12} {'Utility se passar':>18}")
    for level in LEVELS:
        rp = random_pass_rate[level]
        utility_if_pass = 1 / rp if rp > 0 else 0.0
        print(f"N{level:<7} {rp*100:>10.2f}% {utility_if_pass:>17.2f}")

    print('\n2) Politicas de recomendacao')
    n_hit = results['neighbor_hit'] / eval_count if eval_count else 0.0
    g_hit = results['global_hit'] / eval_count if eval_count else 0.0
    s_hit = results['static_hit'] / eval_count if eval_count else 0.0
    n_utility = float(np.mean(results['neighbor_utility'])) if results['neighbor_utility'] else 0.0
    g_utility = float(np.mean(results['global_utility'])) if results['global_utility'] else 0.0
    s_utility = float(np.mean(results['static_utility'])) if results['static_utility'] else 0.0
    print(f"Concursos avaliados: {eval_count:,}")
    print(f"Vizinhanca  | hit={n_hit*100:6.2f}% | utility media={n_utility:7.3f}")
    print(f"Global      | hit={g_hit*100:6.2f}% | utility media={g_utility:7.3f}")
    print(f"Static N{static_best_level}   | hit={s_hit*100:6.2f}% | utility media={s_utility:7.3f}")
    print(f"Delta vizinhanca - global: hit={(n_hit-g_hit)*100:+.2f} pp | utility={n_utility-g_utility:+.3f}")

    print('\n3) Distribuicao de niveis recomendados')
    print('Vizinhanca:')
    for level, qtd in sorted(results['neighbor_levels'].items()):
        print(f"  N{level}: {qtd:>4,d} ({qtd / eval_count * 100:5.1f}%)")
    print('Global:')
    for level, qtd in sorted(results['global_levels'].items()):
        print(f"  N{level}: {qtd:>4,d} ({qtd / eval_count * 100:5.1f}%)")

    print('\n4) Vizinhanca vs Global concurso a concurso')
    print(f"Vizinhanca melhor: {results['neighbor_when_better']:>5,d} ({results['neighbor_when_better'] / eval_count * 100:5.1f}%)")
    print(f"Global melhor:     {results['global_when_better']:>5,d} ({results['global_when_better'] / eval_count * 100:5.1f}%)")
    print(f"Empate:            {results['equal']:>5,d} ({results['equal'] / eval_count * 100:5.1f}%)")

    print('\n5) Leitura pratica')
    if n_utility > g_utility:
        print('- O contexto local pelos vizinhos agrega informacao util para escolher o nivel estrutural.')
    else:
        print('- A vizinhanca nao melhorou o baseline global; o regime estrutural parece estavel ou o vetor de contexto ainda esta fraco.')
    print('- Se a distribuicao de niveis pela vizinhanca variar bastante, existe sinal de regime.')
    print('- Se quase tudo cair no mesmo nivel, o problema pede outro criterio de escolha ou features mais informativas.')


if __name__ == '__main__':
    main()