# -*- coding: utf-8 -*-
import sys
from collections import Counter

import numpy as np

from _temp_benchmark_fixos13_rotativos import (
    CORE_SIZE,
    LOCKED_FIXED,
    REMOVED_CONFIGS,
    build_recent_ranking,
    carregar_resultados,
    evaluate_pack,
    generate_rotating_games_13,
)

sys.stdout.reconfigure(encoding='utf-8')

MIN_HISTORY = 100


def main():
    draws = carregar_resultados()
    results = {}
    for removed in REMOVED_CONFIGS:
        results[removed] = {
            'best': [],
            'mean': [],
            'roi': [],
            'payout': [],
            'hit13': 0,
            'hit14': 0,
            'hit15': 0,
            'top13': [],
            'games': [],
        }

    print('=' * 78)
    print('BENCHMARK ROBUSTO — 13 FIXOS ROTATIVOS')
    print('=' * 78)

    for idx in range(MIN_HISTORY, len(draws)):
        history = draws[:idx]
        target = draws[idx]
        result_set = set(target['numeros'])
        ranked, _ = build_recent_ranking(history)

        for removed in REMOVED_CONFIGS:
            games, core = generate_rotating_games_13(ranked, LOCKED_FIXED, set(removed))
            ev = evaluate_pack(games, result_set)
            data = results[removed]
            data['best'].append(ev['best'])
            data['mean'].append(ev['mean_hits'])
            data['roi'].append(ev['roi'])
            data['payout'].append(ev['payout'])
            data['top13'].append(len(result_set.intersection(core)))
            data['games'].append(len(games))
            if ev['best'] >= 13:
                data['hit13'] += 1
            if ev['best'] >= 14:
                data['hit14'] += 1
            if ev['best'] >= 15:
                data['hit15'] += 1

        if (idx - MIN_HISTORY + 1) % 500 == 0:
            print(f'Processado {idx - MIN_HISTORY + 1}/{len(draws) - MIN_HISTORY}')

    rows = []
    contests = len(draws) - MIN_HISTORY
    for removed, data in results.items():
        rows.append({
            'removed': removed,
            'best': float(np.mean(data['best'])),
            'mean': float(np.mean(data['mean'])),
            'roi': float(np.mean(data['roi'])),
            'median_roi': float(np.median(data['roi'])),
            'median_payout': float(np.median(data['payout'])),
            'p95_payout': float(np.percentile(data['payout'], 95)),
            'hit13_pct': data['hit13'] / contests * 100,
            'hit14_pct': data['hit14'] / contests * 100,
            'hit15_pct': data['hit15'] / contests * 100,
            'top13': float(np.mean(data['top13'])),
            'games': float(np.mean(data['games'])),
        })

    def robust_score(row):
        return (
            row['mean'] * 20
            + row['best'] * 5
            + row['median_roi'] * 0.5
            + row['hit13_pct'] * 2
            + row['hit14_pct'] * 5
            + row['hit15_pct'] * 10
        )

    rows.sort(key=robust_score, reverse=True)

    print('\nRanking robusto')
    print(f"{'Removidos':<12} {'Jogos':>7} {'Best':>7} {'Mean':>7} {'ROI':>9} {'MedROI':>9} {'13+':>7} {'14+':>7} {'15':>6} {'MedPay':>9} {'P95':>9}")
    for row in rows:
        removed = ','.join(str(x) for x in row['removed'])
        print(
            f"{removed:<12} {row['games']:>7.1f} {row['best']:>7.3f} {row['mean']:>7.3f} {row['roi']:>8.2f}%"
            f" {row['median_roi']:>8.2f}% {row['hit13_pct']:>6.2f}% {row['hit14_pct']:>6.2f}% {row['hit15_pct']:>5.2f}%"
            f" {row['median_payout']:>8.2f} {row['p95_payout']:>8.2f}"
        )

    print('\nLeitura:')
    print('- Median ROI e Median Payout ajudam a ver se o ganho vem de comportamento consistente ou de jackpot isolado.')
    print('- Se median payout = 0 em todos, o método ainda depende demais de outliers.')


if __name__ == '__main__':
    main()
