# -*- coding: utf-8 -*-
import sys
from collections import Counter

import numpy as np

from poc_fixos14_rotativos import (
    carregar_resultados,
    build_recent_ranking,
    generate_rotating_games,
    evaluate_pack,
    evaluate_random_baseline,
)

sys.stdout.reconfigure(encoding='utf-8')

MIN_HISTORY = 100
LOCKED_FIXED = {1, 25}
PAIRS = [
    (7, 16),
    (7, 17),
    (18, 23),
    (8, 16),
    (7, 18),
    (5, 7),
    (4, 7),
    (7, 8),
    (7, 9),
    (8, 9),
    (8,),  # baseline anterior
]


def normalize_removed(item):
    return tuple(item)


def main():
    draws = carregar_resultados()
    rng = np.random.default_rng(42)

    metrics = {}
    for removed in PAIRS:
        key = normalize_removed(removed)
        metrics[key] = {
            'best': [],
            'mean': [],
            'payout': [],
            'roi': [],
            'faixa': Counter(),
            'games': [],
            'hit13': 0,
            'hit14': 0,
        }

    random_metrics = {
        'best': [],
        'mean': [],
        'payout': [],
        'roi': [],
        'faixa': Counter(),
    }

    total_games = {normalize_removed(removed): 0 for removed in PAIRS}

    print('=' * 78)
    print('BENCHMARK — FIXOS {1,25} COM PARES ESTÁVEIS DE REMOÇÃO')
    print('=' * 78)
    print(f'Configurações testadas: {len(PAIRS)}')

    for idx in range(MIN_HISTORY, len(draws)):
        history = draws[:idx]
        target = draws[idx]
        ranked, _ = build_recent_ranking(history)
        result_set = set(target['numeros'])

        # Como todos os pares removem 2 números, o pacote fica com 45 jogos.
        random_ev = evaluate_random_baseline(45, result_set, rng)
        random_metrics['best'].append(random_ev['best_mean'])
        random_metrics['mean'].append(random_ev['mean_hits_mean'])
        random_metrics['payout'].append(random_ev['payout_mean'])
        random_metrics['roi'].append(random_ev['roi_mean'])
        for hit, avg_count in random_ev['faixa_mean'].items():
            random_metrics['faixa'][hit] += avg_count

        for removed in PAIRS:
            key = normalize_removed(removed)
            games, _, _ = generate_rotating_games(ranked, LOCKED_FIXED, set(key))
            ev = evaluate_pack(games, result_set)
            metrics[key]['best'].append(ev['best'])
            metrics[key]['mean'].append(ev['mean_hits'])
            metrics[key]['payout'].append(ev['payout'])
            metrics[key]['roi'].append(ev['roi'])
            metrics[key]['games'].append(len(games))
            metrics[key]['faixa'].update(ev['faixa'])
            total_games[key] += len(games)
            if ev['best'] >= 13:
                metrics[key]['hit13'] += 1
            if ev['best'] >= 14:
                metrics[key]['hit14'] += 1

        if (idx - MIN_HISTORY + 1) % 500 == 0:
            print(f'Processado {idx - MIN_HISTORY + 1}/{len(draws) - MIN_HISTORY}')

    rnd_best = float(np.mean(random_metrics['best']))
    rnd_mean = float(np.mean(random_metrics['mean']))
    rnd_payout = float(np.mean(random_metrics['payout']))
    rnd_roi = float(np.mean(random_metrics['roi']))
    rnd_total_games = 45 * (len(draws) - MIN_HISTORY)

    print('\nBaseline aleatório (45 jogos)')
    print(f'Melhor={rnd_best:.3f} | Média={rnd_mean:.3f} | Payout=R$ {rnd_payout:,.2f} | ROI={rnd_roi:+.2f}%')

    rows = []
    for key, data in metrics.items():
        row = {
            'removed': key,
            'best': float(np.mean(data['best'])),
            'mean': float(np.mean(data['mean'])),
            'payout': float(np.mean(data['payout'])),
            'roi': float(np.mean(data['roi'])),
            'hit13_pct': data['hit13'] / len(data['best']) * 100,
            'hit14_pct': data['hit14'] / len(data['best']) * 100,
            'g11': data['faixa'].get(11, 0.0) / total_games[key] * 100 if total_games[key] else 0.0,
            'g12': data['faixa'].get(12, 0.0) / total_games[key] * 100 if total_games[key] else 0.0,
            'g13': data['faixa'].get(13, 0.0) / total_games[key] * 100 if total_games[key] else 0.0,
            'g14': data['faixa'].get(14, 0.0) / total_games[key] * 100 if total_games[key] else 0.0,
        }
        rows.append(row)

    def robust_rank(row):
        return (
            (row['roi'] - rnd_roi) * 0.5
            + (row['best'] - rnd_best) * 5.0
            + (row['mean'] - rnd_mean) * 20.0
            + row['hit13_pct'] * 2.0
            + row['hit14_pct'] * 4.0
        )

    rows.sort(key=robust_rank, reverse=True)

    print('\nRanking final vs baseline aleatório')
    print(f"{'Removidos':<12} {'Best':>7} {'Mean':>7} {'Payout':>10} {'ROI':>9} {'13+':>7} {'14+':>7}")
    for row in rows:
        removed = ','.join(str(x) for x in row['removed'])
        print(
            f"{removed:<12} {row['best']:>7.3f} {row['mean']:>7.3f} {row['payout']:>10.2f} {row['roi']:>8.2f}%"
            f" {row['hit13_pct']:>6.2f}% {row['hit14_pct']:>6.2f}%"
        )

    best = rows[0]
    print('\nMelhor configuração estável')
    print(f"Removidos: {best['removed']}")
    print(f"Delta best:   {best['best'] - rnd_best:+.3f}")
    print(f"Delta mean:   {best['mean'] - rnd_mean:+.3f}")
    print(f"Delta payout: {best['payout'] - rnd_payout:+.2f}")
    print(f"Delta ROI:    {best['roi'] - rnd_roi:+.2f} pp")
    print(f"Delta 13+:    {best['hit13_pct']:+.2f}% absolutos")
    print(f"Delta 14+:    {best['hit14_pct']:+.2f}% absolutos")


if __name__ == '__main__':
    main()
