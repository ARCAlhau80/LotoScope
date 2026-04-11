# -*- coding: utf-8 -*-
"""
POC: interpretação dos regimes da vizinhança histórica do Pool 23

Objetivo:
- Entender quando a política por vizinhança recomenda N1/N3/N4/N5/N6
- Extrair diferenças médias de contexto entre níveis recomendados
- Traduzir a recomendação em leitura humana de regime
"""

import sys
from collections import Counter, defaultdict

import numpy as np

from poc_vizinhanca_historica_pool23 import (
    FEATURE_WINDOW,
    K_NEIGHBORS,
    LEVELS,
    MIN_HISTORY,
    build_context_features,
    build_filters_for_level,
    carregar_resultados,
    choose_best_level,
    random_combos,
    standardize_matrix,
)
from poc_incompatibilidade_filtros_pool23 import RANDOM_SAMPLES

sys.stdout.reconfigure(encoding='utf-8')

FEATURE_NAMES = [
    'sum_last',
    'pares_last',
    'primos_last',
    'fib_last',
    'faixa_6_20_last',
    'moldura_last',
    'linha_spread_last',
    'col_spread_last',
    'seq_max_last',
    'count_1_25_last',
    'repeats_last',
    'sum_mean_12',
    'sum_std_12',
    'pares_mean_12',
    'primos_mean_12',
    'fib_mean_12',
    'faixa_6_20_mean_12',
    'seq_max_mean_12',
    'hot_12',
    'warm_12',
    'cold_12',
    'absent_12',
    'freq_1_12',
    'freq_25_12',
]


def package_predicates():
    predicates = {}
    for level in LEVELS:
        filters = build_filters_for_level(level)
        predicates[level] = lambda combo, fns=list(filters.values()): all(fn(combo) for fn in fns)
    return predicates


def main():
    print('=' * 78)
    print('POC — REGIMES DA VIZINHANCA HISTORICA')
    print('=' * 78)
    print(f'Janela de features: {FEATURE_WINDOW}')
    print(f'K vizinhos: {K_NEIGHBORS}')

    draws = carregar_resultados()
    contexts = build_context_features(draws)
    predicates = package_predicates()

    rng = np.random.default_rng(42)
    random_draws = random_combos(RANDOM_SAMPLES, rng)
    random_pass_rate = {
        level: sum(1 for combo in random_draws if predicates[level](combo)) / len(random_draws)
        for level in LEVELS
    }

    utility_matrix = {level: [] for level in LEVELS}
    for draw in draws:
        combo = draw['numeros']
        for level in LEVELS:
            passed = 1 if predicates[level](combo) else 0
            utility_matrix[level].append(passed / random_pass_rate[level] if random_pass_rate[level] > 0 else 0.0)

    valid_idx = [idx for idx, ctx in enumerate(contexts) if ctx is not None]
    raw_matrix = np.vstack([contexts[idx] for idx in valid_idx])
    std_matrix = standardize_matrix(raw_matrix)
    idx_to_row = {idx: pos for pos, idx in enumerate(valid_idx)}

    recommended_levels = {}
    level_contexts_raw = defaultdict(list)
    level_contexts_std = defaultdict(list)
    level_utilities = defaultdict(list)
    conservative_contexts = []
    aggressive_contexts = []

    for idx in valid_idx:
        if idx < max(MIN_HISTORY, FEATURE_WINDOW + 1):
            continue

        target = std_matrix[idx_to_row[idx]]
        candidates = [j for j in valid_idx if j < idx]
        candidate_rows = np.vstack([std_matrix[idx_to_row[j]] for j in candidates])
        dists = np.linalg.norm(candidate_rows - target, axis=1)
        nearest_order = np.argsort(dists)[:K_NEIGHBORS]
        neighbors = [candidates[pos] for pos in nearest_order]

        scores = {
            level: float(np.mean([utility_matrix[level][j] for j in neighbors]))
            for level in LEVELS
        }
        best_level = choose_best_level(scores)
        recommended_levels[idx] = best_level
        level_contexts_raw[best_level].append(raw_matrix[idx_to_row[idx]])
        level_contexts_std[best_level].append(std_matrix[idx_to_row[idx]])
        level_utilities[best_level].append(utility_matrix[best_level][idx])

        if best_level <= 3:
            conservative_contexts.append(std_matrix[idx_to_row[idx]])
        else:
            aggressive_contexts.append(std_matrix[idx_to_row[idx]])

    total = len(recommended_levels)
    print('\n1) Distribuicao dos regimes recomendados')
    for level in LEVELS:
        qtd = len(level_contexts_raw[level])
        if qtd == 0:
            continue
        util = float(np.mean(level_utilities[level]))
        print(f'N{level}: {qtd:>4,d} ({qtd / total * 100:5.1f}%) | utility media real={util:6.3f}')

    print('\n2) Perfil medio por nivel recomendado (features brutas)')
    key_features = [
        'sum_last', 'pares_last', 'primos_last', 'fib_last', 'faixa_6_20_last',
        'moldura_last', 'linha_spread_last', 'col_spread_last', 'seq_max_last',
        'sum_mean_12', 'sum_std_12', 'hot_12', 'cold_12', 'absent_12',
        'freq_1_12', 'freq_25_12'
    ]
    key_idx = [FEATURE_NAMES.index(name) for name in key_features]
    print(f"{'Nivel':<8} {'sum':>7} {'pares':>7} {'fib':>7} {'F6-20':>7} {'spreadL':>8} {'spreadC':>8} {'seq':>6} {'hot12':>7} {'cold12':>8} {'f1':>6} {'f25':>6}")
    for level in LEVELS:
        rows = level_contexts_raw[level]
        if not rows:
            continue
        mean_vec = np.mean(rows, axis=0)
        print(
            f"N{level:<7} {mean_vec[FEATURE_NAMES.index('sum_last')]:>7.1f}"
            f" {mean_vec[FEATURE_NAMES.index('pares_last')]:>7.2f}"
            f" {mean_vec[FEATURE_NAMES.index('fib_last')]:>7.2f}"
            f" {mean_vec[FEATURE_NAMES.index('faixa_6_20_last')]:>7.2f}"
            f" {mean_vec[FEATURE_NAMES.index('linha_spread_last')]:>8.2f}"
            f" {mean_vec[FEATURE_NAMES.index('col_spread_last')]:>8.2f}"
            f" {mean_vec[FEATURE_NAMES.index('seq_max_last')]:>6.2f}"
            f" {mean_vec[FEATURE_NAMES.index('hot_12')]:>7.2f}"
            f" {mean_vec[FEATURE_NAMES.index('cold_12')]:>8.2f}"
            f" {mean_vec[FEATURE_NAMES.index('freq_1_12')]:>6.2f}"
            f" {mean_vec[FEATURE_NAMES.index('freq_25_12')]:>6.2f}"
        )

    print('\n3) Principais discriminantes: N6 versus N1-3')
    n6_rows = np.array(level_contexts_std[6]) if level_contexts_std[6] else np.empty((0, len(FEATURE_NAMES)))
    n13_rows = np.array([row for level in (1, 2, 3) for row in level_contexts_std[level]])
    if len(n6_rows) > 0 and len(n13_rows) > 0:
        diff = np.mean(n6_rows, axis=0) - np.mean(n13_rows, axis=0)
        top = np.argsort(np.abs(diff))[::-1][:10]
        for idx in top:
            direction = 'maior em N6' if diff[idx] > 0 else 'maior em N1-3'
            print(f'{FEATURE_NAMES[idx]:<18} delta_z={diff[idx]:+6.3f} | {direction}')

    print('\n4) Principais discriminantes: conservador (N1-3) versus agressivo (N4-6)')
    cons = np.array(conservative_contexts) if conservative_contexts else np.empty((0, len(FEATURE_NAMES)))
    aggr = np.array(aggressive_contexts) if aggressive_contexts else np.empty((0, len(FEATURE_NAMES)))
    if len(cons) > 0 and len(aggr) > 0:
        diff = np.mean(aggr, axis=0) - np.mean(cons, axis=0)
        top = np.argsort(np.abs(diff))[::-1][:10]
        for idx in top:
            direction = 'maior em N4-6' if diff[idx] > 0 else 'maior em N1-3'
            print(f'{FEATURE_NAMES[idx]:<18} delta_z={diff[idx]:+6.3f} | {direction}')

    print('\n5) Leitura operacional sugerida')
    print('- Features com delta_z alto sao os melhores candidatos a explicar o regime.')
    print('- Se N6 aparecer ligado a baixa dispersao e baixa variabilidade recente, o contexto favorece compressao agressiva.')
    print('- Se N1-3 aparecerem ligados a maior instabilidade/espalhamento, o contexto pede preservacao.')


if __name__ == '__main__':
    main()