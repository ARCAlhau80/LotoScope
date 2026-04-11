# -*- coding: utf-8 -*-
"""
POC: Advisor de regime em 3 bandas para Pool 23

Bandas:
- CONSERVADOR: escolhe melhor entre N1 e N2
- INTERMEDIARIO: N3
- AGRESSIVO: N6

Objetivo:
- Ver se a simplificação para 3 bandas preserva boa parte do ganho da vizinhança
- Produzir uma política mais operacional do que o seletor de 6 níveis
"""

import sys
from collections import Counter

import numpy as np

from poc_vizinhanca_historica_pool23 import (
    FEATURE_WINDOW,
    K_NEIGHBORS,
    MIN_HISTORY,
    build_context_features,
    carregar_resultados,
    choose_best_level,
    random_combos,
    standardize_matrix,
)
from poc_incompatibilidade_filtros_pool23 import RANDOM_SAMPLES, build_filters_for_level

sys.stdout.reconfigure(encoding='utf-8')

ALL_LEVELS = [1, 2, 3, 4, 5, 6]
BANDS = {
    'CONS': [1, 2],
    'MID': [3],
    'AGGR': [6],
}


def package_predicates(levels):
    predicates = {}
    for level in levels:
        filters = build_filters_for_level(level)
        predicates[level] = lambda combo, fns=list(filters.values()): all(fn(combo) for fn in fns)
    return predicates


def pick_band(scores_by_level):
    cons_level = choose_best_level({level: scores_by_level[level] for level in BANDS['CONS']})
    cons_score = scores_by_level[cons_level]
    mid_level = 3
    mid_score = scores_by_level[mid_level]
    aggr_level = 6
    aggr_score = scores_by_level[aggr_level]

    options = {
        'CONS': (cons_level, cons_score),
        'MID': (mid_level, mid_score),
        'AGGR': (aggr_level, aggr_score),
    }
    best_band = sorted(options.items(), key=lambda x: (-x[1][1], x[1][0]))[0]
    return best_band[0], best_band[1][0], options


def main():
    print('=' * 78)
    print('POC — ADVISOR DE REGIME EM 3 BANDAS')
    print('=' * 78)
    print(f'Janela de features: {FEATURE_WINDOW}')
    print(f'K vizinhos: {K_NEIGHBORS}')
    print(f'Histórico mínimo: {MIN_HISTORY}')

    draws = carregar_resultados()
    contexts = build_context_features(draws)
    predicates = package_predicates(ALL_LEVELS)

    rng = np.random.default_rng(42)
    random_draws = random_combos(RANDOM_SAMPLES, rng)
    random_pass = {
        level: sum(1 for combo in random_draws if predicates[level](combo)) / len(random_draws)
        for level in ALL_LEVELS
    }

    utility_matrix = {level: [] for level in ALL_LEVELS}
    pass_matrix = {level: [] for level in ALL_LEVELS}
    for draw in draws:
        combo = draw['numeros']
        for level in ALL_LEVELS:
            passed = 1 if predicates[level](combo) else 0
            pass_matrix[level].append(passed)
            utility_matrix[level].append(passed / random_pass[level] if random_pass[level] > 0 else 0.0)

    valid_idx = [idx for idx, ctx in enumerate(contexts) if ctx is not None]
    raw_matrix = np.vstack([contexts[idx] for idx in valid_idx])
    std_matrix = standardize_matrix(raw_matrix)
    idx_to_row = {idx: pos for pos, idx in enumerate(valid_idx)}

    static_best_6 = choose_best_level({level: np.mean(utility_matrix[level][MIN_HISTORY:]) for level in ALL_LEVELS})
    static_best_3 = choose_best_level({level: np.mean(utility_matrix[level][MIN_HISTORY:]) for level in [1, 2, 3, 6]})

    stats = {
        'neighbor6_hit': 0,
        'neighbor6_util': [],
        'neighbor3_hit': 0,
        'neighbor3_util': [],
        'global6_hit': 0,
        'global6_util': [],
        'global3_hit': 0,
        'global3_util': [],
        'static6_hit': 0,
        'static6_util': [],
        'static3_hit': 0,
        'static3_util': [],
        'bands': Counter(),
        'levels3': Counter(),
        'kept_gain_vs_global6': 0,
        'lost_vs_neighbor6': 0,
        'equal_neighbor6': 0,
    }

    eval_count = 0
    for idx in valid_idx:
        if idx < max(MIN_HISTORY, FEATURE_WINDOW + 1):
            continue

        target = std_matrix[idx_to_row[idx]]
        candidates = [j for j in valid_idx if j < idx]
        candidate_rows = np.vstack([std_matrix[idx_to_row[j]] for j in candidates])
        dists = np.linalg.norm(candidate_rows - target, axis=1)
        nearest_order = np.argsort(dists)[:K_NEIGHBORS]
        neighbors = [candidates[pos] for pos in nearest_order]

        neighbor_scores_6 = {level: float(np.mean([utility_matrix[level][j] for j in neighbors])) for level in ALL_LEVELS}
        global_scores_6 = {level: float(np.mean(utility_matrix[level][:idx])) for level in ALL_LEVELS}

        neighbor6_level = choose_best_level(neighbor_scores_6)
        global6_level = choose_best_level(global_scores_6)

        band_name, neighbor3_level, _ = pick_band(neighbor_scores_6)
        _, global3_level, _ = pick_band(global_scores_6)

        n6_util = utility_matrix[neighbor6_level][idx]
        n3_util = utility_matrix[neighbor3_level][idx]
        g6_util = utility_matrix[global6_level][idx]
        g3_util = utility_matrix[global3_level][idx]
        s6_util = utility_matrix[static_best_6][idx]
        s3_util = utility_matrix[static_best_3][idx]

        stats['neighbor6_hit'] += pass_matrix[neighbor6_level][idx]
        stats['neighbor6_util'].append(n6_util)
        stats['neighbor3_hit'] += pass_matrix[neighbor3_level][idx]
        stats['neighbor3_util'].append(n3_util)
        stats['global6_hit'] += pass_matrix[global6_level][idx]
        stats['global6_util'].append(g6_util)
        stats['global3_hit'] += pass_matrix[global3_level][idx]
        stats['global3_util'].append(g3_util)
        stats['static6_hit'] += pass_matrix[static_best_6][idx]
        stats['static6_util'].append(s6_util)
        stats['static3_hit'] += pass_matrix[static_best_3][idx]
        stats['static3_util'].append(s3_util)

        stats['bands'][band_name] += 1
        stats['levels3'][neighbor3_level] += 1

        if n3_util >= g6_util:
            stats['kept_gain_vs_global6'] += 1
        if n3_util < n6_util:
            stats['lost_vs_neighbor6'] += 1
        if abs(n3_util - n6_util) < 1e-12:
            stats['equal_neighbor6'] += 1

        eval_count += 1

    print('\n1) Comparativo de políticas')
    policies = [
        ('Vizinhanca 6 niveis', stats['neighbor6_hit'], stats['neighbor6_util']),
        ('Vizinhanca 3 bandas', stats['neighbor3_hit'], stats['neighbor3_util']),
        ('Global 6 niveis', stats['global6_hit'], stats['global6_util']),
        ('Global 3 bandas', stats['global3_hit'], stats['global3_util']),
        (f'Static N{static_best_6}', stats['static6_hit'], stats['static6_util']),
        (f'Static N{static_best_3}', stats['static3_hit'], stats['static3_util']),
    ]
    print(f"{'Politica':<22} {'Hit':>10} {'Utility':>10}")
    for name, hit_sum, util_list in policies:
        hit = hit_sum / eval_count * 100 if eval_count else 0.0
        util = float(np.mean(util_list)) if util_list else 0.0
        print(f"{name:<22} {hit:>9.2f}% {util:>9.3f}")

    n6_hit = stats['neighbor6_hit'] / eval_count * 100 if eval_count else 0.0
    n3_hit = stats['neighbor3_hit'] / eval_count * 100 if eval_count else 0.0
    n6_util = float(np.mean(stats['neighbor6_util'])) if stats['neighbor6_util'] else 0.0
    n3_util = float(np.mean(stats['neighbor3_util'])) if stats['neighbor3_util'] else 0.0

    print('\n2) Custo da simplificação 3 bandas')
    print(f'Delta hit (3 bandas - 6 níveis): {n3_hit - n6_hit:+.2f} pp')
    print(f'Delta utility (3 bandas - 6 níveis): {n3_util - n6_util:+.3f}')
    print(f'Manteve ou superou global 6 níveis em: {stats["kept_gain_vs_global6"]:>4,d} ({stats["kept_gain_vs_global6"] / eval_count * 100:5.1f}%)')
    print(f'Perdeu para a política 6 níveis em:    {stats["lost_vs_neighbor6"]:>4,d} ({stats["lost_vs_neighbor6"] / eval_count * 100:5.1f}%)')
    print(f'Empatou com 6 níveis em:               {stats["equal_neighbor6"]:>4,d} ({stats["equal_neighbor6"] / eval_count * 100:5.1f}%)')

    print('\n3) Distribuição das bandas e níveis escolhidos')
    for band in ['CONS', 'MID', 'AGGR']:
        qtd = stats['bands'][band]
        print(f'{band:<5}: {qtd:>4,d} ({qtd / eval_count * 100:5.1f}%)')
    print('Detalhe dos níveis efetivos:')
    for level in sorted(stats['levels3']):
        qtd = stats['levels3'][level]
        print(f'  N{level}: {qtd:>4,d} ({qtd / eval_count * 100:5.1f}%)')

    print('\n4) Leitura operacional')
    if n3_util >= n6_util - 0.02:
        print('- A simplificação para 3 bandas preserva a maior parte do ganho e é operacionalmente atraente.')
    else:
        print('- A simplificação perde informação relevante; ainda vale manter o advisor em 6 níveis.')
    print('- Se AGGR dominar, o sistema pode começar com triagem binária agressivo vs não agressivo.')
    print('- Se CONS aparecer com frequência razoável, o advisor já tem valor prático para evitar overcompression desnecessária.')


if __name__ == '__main__':
    main()