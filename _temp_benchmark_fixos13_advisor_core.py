# -*- coding: utf-8 -*-
import sys
from collections import Counter

import numpy as np

from _temp_benchmark_fixos13_rotativos import (
    LOCKED_FIXED,
    evaluate_pack,
    evaluate_random_baseline_custom,
    generate_rotating_games_13,
)
from poc_fixos14_rotativos import carregar_resultados
from poc_regime_3_bandas_pool23 import ALL_LEVELS, pick_band
from poc_vizinhanca_historica_pool23 import (
    FEATURE_WINDOW,
    K_NEIGHBORS,
    MIN_HISTORY,
    build_context_features,
    choose_best_level,
    random_combos,
    standardize_matrix,
)
from poc_incompatibilidade_filtros_pool23 import RANDOM_SAMPLES, build_filters_for_level

sys.stdout.reconfigure(encoding='utf-8')

REMOVED_PAIR = (7, 17)
START_IDX = max(MIN_HISTORY, FEATURE_WINDOW + 1)


def package_predicates(levels):
    predicates = {}
    for level in levels:
        filters = build_filters_for_level(level)
        predicates[level] = lambda combo, fns=list(filters.values()): all(fn(combo) for fn in fns)
    return predicates


def build_window_ranking(history, window):
    counter = Counter()
    for draw in history[-window:]:
        counter.update(draw['numeros'])
    ranked = sorted(range(1, 26), key=lambda n: (-counter[n], n))
    return ranked


def build_aggressive_ranking(history):
    c06 = Counter()
    c12 = Counter()
    c30 = Counter()
    for draw in history[-6:]:
        c06.update(draw['numeros'])
    for draw in history[-12:]:
        c12.update(draw['numeros'])
    for draw in history[-30:]:
        c30.update(draw['numeros'])

    scores = {}
    for n in range(1, 26):
        scores[n] = 3.0 * c06[n] + 2.0 * c12[n] + 1.0 * c30[n]
    ranked = sorted(range(1, 26), key=lambda n: (-scores[n], n))
    return ranked


def build_ranked_for_band(history, band_name):
    if band_name == 'CONS':
        return build_window_ranking(history, 60)
    if band_name == 'AGGR':
        return build_aggressive_ranking(history)
    return build_window_ranking(history, 30)


def build_band_selector(draws):
    contexts = build_context_features(draws)
    valid_idx = [idx for idx, ctx in enumerate(contexts) if ctx is not None]
    raw_matrix = np.vstack([contexts[idx] for idx in valid_idx])
    std_matrix = standardize_matrix(raw_matrix)
    idx_to_row = {idx: pos for pos, idx in enumerate(valid_idx)}

    predicates = package_predicates(ALL_LEVELS)
    rng = np.random.default_rng(42)
    random_draws = [tuple(sorted(combo)) for combo in random_combos(RANDOM_SAMPLES, rng)]
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

    def choose_band_for_idx(idx):
        if idx < START_IDX or idx not in idx_to_row:
            return 'MID'
        target = std_matrix[idx_to_row[idx]]
        candidates = [j for j in valid_idx if j < idx]
        candidate_rows = np.vstack([std_matrix[idx_to_row[j]] for j in candidates])
        dists = np.linalg.norm(candidate_rows - target, axis=1)
        nearest_order = np.argsort(dists)[:K_NEIGHBORS]
        neighbors = [candidates[pos] for pos in nearest_order]
        neighbor_scores_6 = {level: float(np.mean([utility_matrix[level][j] for j in neighbors])) for level in ALL_LEVELS}
        band_name, _, _ = pick_band(neighbor_scores_6)
        return band_name

    return choose_band_for_idx


def summarize(name, rows):
    contests = len(rows['best'])
    return {
        'name': name,
        'contests': contests,
        'best': float(np.mean(rows['best'])),
        'mean': float(np.mean(rows['mean'])),
        'roi': float(np.mean(rows['roi'])),
        'median_roi': float(np.median(rows['roi'])),
        'payout': float(np.mean(rows['payout'])),
        'median_payout': float(np.median(rows['payout'])),
        'p95_payout': float(np.percentile(rows['payout'], 95)),
        'hit13_pct': rows['hit13'] / contests * 100 if contests else 0.0,
        'hit14_pct': rows['hit14'] / contests * 100 if contests else 0.0,
        'hit15_pct': rows['hit15'] / contests * 100 if contests else 0.0,
        'top13': float(np.mean(rows['top13'])),
        'games': float(np.mean(rows['games'])),
    }


def main():
    draws = carregar_resultados()
    choose_band_for_idx = build_band_selector(draws)
    rng = np.random.default_rng(123)

    baseline = {'best': [], 'mean': [], 'roi': [], 'payout': [], 'top13': [], 'games': [], 'hit13': 0, 'hit14': 0, 'hit15': 0}
    advisor = {'best': [], 'mean': [], 'roi': [], 'payout': [], 'top13': [], 'games': [], 'hit13': 0, 'hit14': 0, 'hit15': 0}
    random_rows = {'best': [], 'mean': [], 'roi': [], 'payout': [], 'games': []}
    bands = Counter()

    print('=' * 78)
    print('BENCHMARK — 13 FIXOS COM NUCLEO VIA ADVISOR')
    print('=' * 78)
    print(f'Par removido fixo para comparacao justa: {REMOVED_PAIR}')

    for idx in range(START_IDX, len(draws)):
        history = draws[:idx]
        result_set = set(draws[idx]['numeros'])

        ranked_base = build_window_ranking(history, 30)
        games_base, core_base = generate_rotating_games_13(ranked_base, LOCKED_FIXED, set(REMOVED_PAIR))
        ev_base = evaluate_pack(games_base, result_set)
        baseline['best'].append(ev_base['best'])
        baseline['mean'].append(ev_base['mean_hits'])
        baseline['roi'].append(ev_base['roi'])
        baseline['payout'].append(ev_base['payout'])
        baseline['top13'].append(len(result_set.intersection(core_base)))
        baseline['games'].append(len(games_base))
        baseline['hit13'] += int(ev_base['best'] >= 13)
        baseline['hit14'] += int(ev_base['best'] >= 14)
        baseline['hit15'] += int(ev_base['best'] >= 15)

        band_name = choose_band_for_idx(idx)
        bands[band_name] += 1
        ranked_adv = build_ranked_for_band(history, band_name)
        games_adv, core_adv = generate_rotating_games_13(ranked_adv, LOCKED_FIXED, set(REMOVED_PAIR))
        ev_adv = evaluate_pack(games_adv, result_set)
        advisor['best'].append(ev_adv['best'])
        advisor['mean'].append(ev_adv['mean_hits'])
        advisor['roi'].append(ev_adv['roi'])
        advisor['payout'].append(ev_adv['payout'])
        advisor['top13'].append(len(result_set.intersection(core_adv)))
        advisor['games'].append(len(games_adv))
        advisor['hit13'] += int(ev_adv['best'] >= 13)
        advisor['hit14'] += int(ev_adv['best'] >= 14)
        advisor['hit15'] += int(ev_adv['best'] >= 15)

        random_ev = evaluate_random_baseline_custom(len(games_base), result_set, rng)
        random_rows['best'].append(random_ev['best_mean'])
        random_rows['mean'].append(random_ev['mean_hits_mean'])
        random_rows['roi'].append(random_ev['roi_mean'])
        random_rows['payout'].append(random_ev['payout_mean'])
        random_rows['games'].append(len(games_base))

        if (idx - START_IDX + 1) % 500 == 0:
            print(f'Processado {idx - START_IDX + 1}/{len(draws) - START_IDX}')

    rows = [
        summarize('Base freq30', baseline),
        summarize('Advisor core', advisor),
        {
            'name': 'Aleatorio',
            'contests': len(random_rows['best']),
            'best': float(np.mean(random_rows['best'])),
            'mean': float(np.mean(random_rows['mean'])),
            'roi': float(np.mean(random_rows['roi'])),
            'median_roi': float(np.median(random_rows['roi'])),
            'payout': float(np.mean(random_rows['payout'])),
            'median_payout': float(np.median(random_rows['payout'])),
            'p95_payout': float(np.percentile(random_rows['payout'], 95)),
            'hit13_pct': 0.0,
            'hit14_pct': 0.0,
            'hit15_pct': 0.0,
            'top13': 0.0,
            'games': float(np.mean(random_rows['games'])),
        },
    ]

    print('\nDistribuicao das bandas usadas no advisor')
    total_bands = sum(bands.values())
    for band in ['CONS', 'MID', 'AGGR']:
        qtd = bands[band]
        pct = qtd / total_bands * 100 if total_bands else 0.0
        print(f'{band:<5}: {qtd:>4} ({pct:5.1f}%)')

    print('\nComparativo')
    print(f"{'Metodo':<14} {'Jogos':>7} {'Best':>7} {'Mean':>7} {'ROI':>9} {'MedROI':>9} {'13+':>7} {'14+':>7} {'15':>6} {'Top13':>7}")
    for row in rows:
        print(
            f"{row['name']:<14} {row['games']:>7.1f} {row['best']:>7.3f} {row['mean']:>7.3f} {row['roi']:>8.2f}%"
            f" {row['median_roi']:>8.2f}% {row['hit13_pct']:>6.2f}% {row['hit14_pct']:>6.2f}% {row['hit15_pct']:>5.2f}% {row['top13']:>7.3f}"
        )

    base = rows[0]
    adv = rows[1]
    print('\nDelta advisor vs base freq30')
    print(f"Best:   {adv['best'] - base['best']:+.3f}")
    print(f"Mean:   {adv['mean'] - base['mean']:+.3f}")
    print(f"ROI:    {adv['roi'] - base['roi']:+.2f} pp")
    print(f"MedROI: {adv['median_roi'] - base['median_roi']:+.2f} pp")
    print(f"13+:    {adv['hit13_pct'] - base['hit13_pct']:+.2f} pp")
    print(f"14+:    {adv['hit14_pct'] - base['hit14_pct']:+.2f} pp")
    print(f"Top13:  {adv['top13'] - base['top13']:+.3f}")


if __name__ == '__main__':
    main()
