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

from pool23_hub import (
    BANDS, pick_band,
    FEATURE_WINDOW, K_NEIGHBORS, MIN_HISTORY,
    build_context_features, carregar_resultados, random_combos,
    standardize_matrix,
    RANDOM_SAMPLES, build_filters_for_level,
    ALL_LEVELS, FEATURE_NAMES,
    package_predicates, top_feature_deltas, summarize_context,
)

sys.stdout.reconfigure(encoding='utf-8')


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