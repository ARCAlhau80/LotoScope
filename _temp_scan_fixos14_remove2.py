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

# Baseline do teste anterior com {1,25} fixos e removendo {8}
BASELINE = {
    'best_rot': 9.811,
    'mean_rot': 9.013,
    'roi_rot': -73.57,
    'payout_rot': 50.87,
}


def evaluate_removed_pair(removed_pair, draws):
    best_list = []
    mean_list = []
    payout_list = []
    roi_list = []
    games_list = []
    top14_hits = []

    for idx in range(MIN_HISTORY, len(draws)):
        history = draws[:idx]
        target = draws[idx]
        ranked, _ = build_recent_ranking(history)
        games, core, _ = generate_rotating_games(ranked, LOCKED_FIXED, set(removed_pair))
        result_set = set(target['numeros'])
        rot = evaluate_pack(games, result_set)

        best_list.append(rot['best'])
        mean_list.append(rot['mean_hits'])
        payout_list.append(rot['payout'])
        roi_list.append(rot['roi'])
        games_list.append(len(games))
        top14_hits.append(len(result_set.intersection(core)))

    return {
        'removed': removed_pair,
        'best_rot': float(np.mean(best_list)),
        'mean_rot': float(np.mean(mean_list)),
        'payout_rot': float(np.mean(payout_list)),
        'roi_rot': float(np.mean(roi_list)),
        'games_avg': float(np.mean(games_list)),
        'top14_hits': float(np.mean(top14_hits)),
    }


def score_result(row):
    # score simples para ordenar candidatos: ROI pesa mais, depois prêmio, melhor acerto e média
    return (
        row['roi_rot'] * 2.0
        + row['payout_rot'] * 0.05
        + row['best_rot'] * 5.0
        + row['mean_rot'] * 20.0
    )


def main():
    draws = carregar_resultados()
    results = []

    all_pairs = list(combinations(CANDIDATES_REMOVE, 2))
    total = len(all_pairs)
    print('=' * 78)
    print('SCAN RAPIDO — 14 FIXOS ROTATIVOS COM FIXOS {1,25} E REMOVENDO 2')
    print('=' * 78)
    print(f'Pares avaliados: {total}')

    for idx, pair in enumerate(all_pairs, start=1):
        results.append(evaluate_removed_pair(pair, draws))
        if idx % 50 == 0 or idx == total:
            print(f'Processado {idx}/{total}')

    results.sort(key=score_result, reverse=True)

    print('\nTop 15 pares de remoção')
    print(f"{'Removidos':<14} {'Best':>7} {'Mean':>7} {'Payout':>10} {'ROI':>9} {'Jogos':>7} {'Top14':>7}")
    for row in results[:15]:
        removed = f"{row['removed'][0]},{row['removed'][1]}"
        print(
            f"{removed:<14} {row['best_rot']:>7.3f} {row['mean_rot']:>7.3f} {row['payout_rot']:>10.2f}"
            f" {row['roi_rot']:>8.2f}% {row['games_avg']:>7.1f} {row['top14_hits']:>7.3f}"
        )

    print('\nComparação contra baseline {1,25 fixos; remove 8}')
    best = results[0]
    print(f"Melhor par: {best['removed']}")
    print(f"Delta best:   {best['best_rot'] - BASELINE['best_rot']:+.3f}")
    print(f"Delta mean:   {best['mean_rot'] - BASELINE['mean_rot']:+.3f}")
    print(f"Delta payout: {best['payout_rot'] - BASELINE['payout_rot']:+.2f}")
    print(f"Delta ROI:    {best['roi_rot'] - BASELINE['roi_rot']:+.2f} pp")


if __name__ == '__main__':
    main()
