# -*- coding: utf-8 -*-
import sys
from itertools import combinations

import numpy as np

from poc_fixos14_rotativos import (
    carregar_resultados,
    build_recent_ranking,
    generate_rotating_games,
    evaluate_pack,
)

sys.stdout.reconfigure(encoding='utf-8')

MIN_HISTORY = 100
LOCKED_FIXED = {1, 25}
CANDIDATES_REMOVE = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
BASELINE = {'best': 9.811, 'mean': 9.013, 'roi': -73.57}


def evaluate_removed_pair(removed_pair, draws):
    best_list = []
    mean_list = []
    roi_list = []
    payout_list = []
    hits14 = 0
    hits13 = 0

    for idx in range(MIN_HISTORY, len(draws)):
        history = draws[:idx]
        target = draws[idx]
        ranked, _ = build_recent_ranking(history)
        games, core, _ = generate_rotating_games(ranked, LOCKED_FIXED, set(removed_pair))
        result_set = set(target['numeros'])
        rot = evaluate_pack(games, result_set)

        best_list.append(rot['best'])
        mean_list.append(rot['mean_hits'])
        roi_list.append(rot['roi'])
        payout_list.append(rot['payout'])
        if rot['best'] >= 14:
            hits14 += 1
        if rot['best'] >= 13:
            hits13 += 1

    return {
        'removed': removed_pair,
        'best': float(np.mean(best_list)),
        'mean': float(np.mean(mean_list)),
        'roi': float(np.mean(roi_list)),
        'median_payout': float(np.median(payout_list)),
        'p95_payout': float(np.percentile(payout_list, 95)),
        'hit13_pct': hits13 / len(best_list) * 100,
        'hit14_pct': hits14 / len(best_list) * 100,
    }


def robust_score(row):
    return row['best'] * 5 + row['mean'] * 20 + row['roi'] * 0.5 + row['hit13_pct'] * 2 + row['hit14_pct'] * 4


def main():
    draws = carregar_resultados()
    results = []
    all_pairs = list(combinations(CANDIDATES_REMOVE, 2))

    print('=' * 78)
    print('SCAN ROBUSTO — FIXOS {1,25} E REMOVENDO 2')
    print('=' * 78)
    print(f'Pares avaliados: {len(all_pairs)}')

    for idx, pair in enumerate(all_pairs, start=1):
        results.append(evaluate_removed_pair(pair, draws))
        if idx % 50 == 0 or idx == len(all_pairs):
            print(f'Processado {idx}/{len(all_pairs)}')

    results.sort(key=robust_score, reverse=True)

    print('\nTop 15 robustos')
    print(f"{'Removidos':<12} {'Best':>7} {'Mean':>7} {'ROI':>9} {'13+':>7} {'14+':>7} {'MedPay':>9} {'P95':>9}")
    for row in results[:15]:
        removed = f"{row['removed'][0]},{row['removed'][1]}"
        print(
            f"{removed:<12} {row['best']:>7.3f} {row['mean']:>7.3f} {row['roi']:>8.2f}%"
            f" {row['hit13_pct']:>6.2f}% {row['hit14_pct']:>6.2f}% {row['median_payout']:>8.2f} {row['p95_payout']:>8.2f}"
        )

    best = results[0]
    print('\nMelhor robusto vs baseline remove {8}')
    print(f"Par: {best['removed']}")
    print(f"Delta best: {best['best'] - BASELINE['best']:+.3f}")
    print(f"Delta mean: {best['mean'] - BASELINE['mean']:+.3f}")
    print(f"Delta ROI:  {best['roi'] - BASELINE['roi']:+.2f} pp")


if __name__ == '__main__':
    main()
