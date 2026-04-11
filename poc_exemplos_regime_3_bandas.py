# -*- coding: utf-8 -*-
"""
POC: exemplos reais do advisor em 3 bandas

Objetivo:
- Selecionar concursos representativos de cada banda (CONS, MID, AGGR)
- Mostrar contexto, nível escolhido, utilidade realizada e vizinhos mais próximos
- Facilitar validação humana do advisor
"""

import sys
from collections import defaultdict

import numpy as np

from poc_regime_3_bandas_pool23 import BANDS, pick_band
from poc_vizinhanca_historica_pool23 import (
    FEATURE_WINDOW,
    K_NEIGHBORS,
    MIN_HISTORY,
    build_context_features,
    carregar_resultados,
    random_combos,
    standardize_matrix,
)
from poc_incompatibilidade_filtros_pool23 import RANDOM_SAMPLES, build_filters_for_level

sys.stdout.reconfigure(encoding='utf-8')

ALL_LEVELS = [1, 2, 3, 4, 5, 6]
FEATURE_NAMES = [
    'sum_last', 'pares_last', 'primos_last', 'fib_last', 'faixa_6_20_last',
    'moldura_last', 'linha_spread_last', 'col_spread_last', 'seq_max_last',
    'count_1_25_last', 'repeats_last', 'sum_mean_12', 'sum_std_12',
    'pares_mean_12', 'primos_mean_12', 'fib_mean_12', 'faixa_6_20_mean_12',
    'seq_max_mean_12', 'hot_12', 'warm_12', 'cold_12', 'absent_12',
    'freq_1_12', 'freq_25_12'
]


def package_predicates(levels):
    predicates = {}
    for level in levels:
        filters = build_filters_for_level(level)
        predicates[level] = lambda combo, fns=list(filters.values()): all(fn(combo) for fn in fns)
    return predicates


def top_feature_deltas(target_vec, neighbor_matrix, top_n=5):
    mean_neighbors = np.mean(neighbor_matrix, axis=0)
    deltas = target_vec - mean_neighbors
    order = np.argsort(np.abs(deltas))[::-1][:top_n]
    return [(FEATURE_NAMES[idx], deltas[idx]) for idx in order]


def summarize_context(raw_vec):
    return {
        'sum_last': raw_vec[0],
        'pares_last': raw_vec[1],
        'fib_last': raw_vec[3],
        'faixa_6_20_last': raw_vec[4],
        'moldura_last': raw_vec[5],
        'linha_spread_last': raw_vec[6],
        'col_spread_last': raw_vec[7],
        'seq_max_last': raw_vec[8],
        'sum_mean_12': raw_vec[11],
        'sum_std_12': raw_vec[12],
        'hot_12': raw_vec[18],
        'cold_12': raw_vec[20],
        'freq_1_12': raw_vec[22],
        'freq_25_12': raw_vec[23],
    }


def main():
    print('=' * 78)
    print('POC — EXEMPLOS REAIS DO ADVISOR 3 BANDAS')
    print('=' * 78)

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
    for draw in draws:
        combo = draw['numeros']
        for level in ALL_LEVELS:
            passed = 1 if predicates[level](combo) else 0
            utility_matrix[level].append(passed / random_pass[level] if random_pass[level] > 0 else 0.0)

    valid_idx = [idx for idx, ctx in enumerate(contexts) if ctx is not None]
    raw_matrix = np.vstack([contexts[idx] for idx in valid_idx])
    std_matrix = standardize_matrix(raw_matrix)
    idx_to_row = {idx: pos for pos, idx in enumerate(valid_idx)}

    examples = defaultdict(list)

    for idx in valid_idx:
        if idx < max(MIN_HISTORY, FEATURE_WINDOW + 1):
            continue

        target_std = std_matrix[idx_to_row[idx]]
        target_raw = raw_matrix[idx_to_row[idx]]
        candidates = [j for j in valid_idx if j < idx]
        candidate_rows = np.vstack([std_matrix[idx_to_row[j]] for j in candidates])
        dists = np.linalg.norm(candidate_rows - target_std, axis=1)
        nearest_order = np.argsort(dists)[:K_NEIGHBORS]
        neighbors = [candidates[pos] for pos in nearest_order]
        neighbor_matrix = np.vstack([std_matrix[idx_to_row[j]] for j in neighbors])

        scores = {
            level: float(np.mean([utility_matrix[level][j] for j in neighbors]))
            for level in ALL_LEVELS
        }
        band_name, chosen_level, options = pick_band(scores)
        realized_utility = utility_matrix[chosen_level][idx]

        examples[band_name].append({
            'idx': idx,
            'concurso': draws[idx]['concurso'],
            'nivel': chosen_level,
            'utility': realized_utility,
            'scores': options,
            'context': summarize_context(target_raw),
            'neighbors': [draws[j]['concurso'] for j in neighbors[:8]],
            'feature_deltas': top_feature_deltas(target_std, neighbor_matrix),
        })

    print('\n1) Exemplos representativos por banda')
    for band in ['CONS', 'MID', 'AGGR']:
        rows = examples[band]
        if not rows:
            continue
        rows_sorted = sorted(rows, key=lambda x: (-x['utility'], x['concurso']))
        chosen = []
        chosen.append(rows_sorted[0])
        chosen.append(rows_sorted[len(rows_sorted) // 2])
        chosen.append(rows_sorted[-1])

        print('\n' + '=' * 78)
        print(f'BANDA {band}')
        print('=' * 78)
        for sample in chosen:
            print(f"\nConcurso {sample['concurso']} | Nivel escolhido: N{sample['nivel']} | Utility real: {sample['utility']:.3f}")
            print('Scores por banda:')
            for key in ['CONS', 'MID', 'AGGR']:
                level, score = sample['scores'][key]
                print(f"  {key}: N{level} -> {score:.3f}")
            ctx = sample['context']
            print('Contexto resumido:')
            print(
                f"  sum={ctx['sum_last']:.1f} | pares={ctx['pares_last']:.1f} | fib={ctx['fib_last']:.1f} | "
                f"F6-20={ctx['faixa_6_20_last']:.1f} | moldura={ctx['moldura_last']:.1f} | seq={ctx['seq_max_last']:.1f}"
            )
            print(
                f"  spreadL={ctx['linha_spread_last']:.1f} | spreadC={ctx['col_spread_last']:.1f} | "
                f"sum_mean12={ctx['sum_mean_12']:.1f} | sum_std12={ctx['sum_std_12']:.2f}"
            )
            print(
                f"  hot12={ctx['hot_12']:.1f} | cold12={ctx['cold_12']:.1f} | "
                f"freq1_12={ctx['freq_1_12']:.1f} | freq25_12={ctx['freq_25_12']:.1f}"
            )
            print(f"Vizinhos mais próximos: {sample['neighbors']}")
            print('Features que mais diferem da média dos vizinhos:')
            for name, delta in sample['feature_deltas']:
                direction = 'acima' if delta > 0 else 'abaixo'
                print(f"  {name}: {abs(delta):.3f}σ {direction}")

    print('\n2) Leitura sugerida')
    print('- O primeiro exemplo de cada banda mostra um caso onde o advisor acertou com força.')
    print('- O exemplo do meio mostra um caso típico.')
    print('- O último mostra um caso marginal, onde a banda foi escolhida mas o resultado não confirmou bem.')


if __name__ == '__main__':
    main()