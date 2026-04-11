# -*- coding: utf-8 -*-
import sys
from collections import Counter
from itertools import combinations

import numpy as np

from poc_fixos14_rotativos import (
    carregar_resultados,
    build_recent_ranking,
    evaluate_pack,
    evaluate_random_baseline,
)

sys.stdout.reconfigure(encoding='utf-8')

MIN_HISTORY = 100
CORE_SIZE = 13
LOCKED_FIXED = {1, 25}
REMOVED_CONFIGS = [
    (7, 17),
    (7, 16),
    (18, 23),
    (8, 16),
    (7, 18),
]
RANDOM_PACKS = 10


def choose_initial_core(ranked, locked_fixed, locked_removed, core_size=CORE_SIZE):
    available = [n for n in ranked if n not in locked_removed]
    core = []
    for n in sorted(locked_fixed):
        if n in available and n not in core:
            core.append(n)
    for n in available:
        if len(core) >= core_size:
            break
        if n not in core:
            core.append(n)
    pool = [n for n in available if n not in core]
    return core, pool


def choose_removal(core, locked_fixed, score_map):
    candidates = [n for n in core if n not in locked_fixed]
    if not candidates:
        return None
    return sorted(candidates, key=lambda n: (score_map.get(n, 0), n))[0]


def choose_promotion(pool, score_map):
    if not pool:
        return None
    return sorted(pool, key=lambda n: (-score_map.get(n, 0), n))[0]


def generate_rotating_games_13(ranked, locked_fixed, locked_removed):
    score_map = {n: len(ranked) - idx for idx, n in enumerate(ranked)}
    core, pool = choose_initial_core(ranked, locked_fixed, locked_removed, CORE_SIZE)

    games = []
    removed_forever = set(locked_removed)
    current_core = list(core)
    current_pool = list(pool)

    while len(current_pool) >= 2:
        for pair in combinations(current_pool, 2):
            game = tuple(sorted(current_core + list(pair)))
            games.append(game)

        promoted = choose_promotion(current_pool, score_map)
        removed = choose_removal(current_core, locked_fixed, score_map)
        if promoted is None or removed is None:
            break

        current_core.remove(removed)
        removed_forever.add(removed)
        current_pool.remove(promoted)
        current_core.append(promoted)
        current_pool = [n for n in current_pool if n not in removed_forever]

    unique_games = []
    seen = set()
    for game in games:
        if game not in seen:
            seen.add(game)
            unique_games.append(game)
    return unique_games, core


def evaluate_random_baseline_custom(n_games, result_set, rng):
    all_numbers = np.arange(1, 26)
    best_list = []
    mean_list = []
    payout_list = []
    roi_list = []
    faixa_total = Counter()
    for _ in range(RANDOM_PACKS):
        games = [tuple(sorted(rng.choice(all_numbers, 15, replace=False).tolist())) for _ in range(n_games)]
        ev = evaluate_pack(games, result_set)
        best_list.append(ev['best'])
        mean_list.append(ev['mean_hits'])
        payout_list.append(ev['payout'])
        roi_list.append(ev['roi'])
        faixa_total.update(ev['faixa'])
    return {
        'best_mean': float(np.mean(best_list)) if best_list else 0.0,
        'mean_hits_mean': float(np.mean(mean_list)) if mean_list else 0.0,
        'payout_mean': float(np.mean(payout_list)) if payout_list else 0.0,
        'roi_mean': float(np.mean(roi_list)) if roi_list else 0.0,
        'faixa_mean': {k: v / RANDOM_PACKS for k, v in faixa_total.items()},
    }


def main():
    draws = carregar_resultados()
    rng = np.random.default_rng(42)

    print('=' * 78)
    print('BENCHMARK — 13 FIXOS ROTATIVOS COM FIXOS {1,25}')
    print('=' * 78)
    print(f'Configurações testadas: {len(REMOVED_CONFIGS)}')

    results = {}
    random_metrics = {
        'best': [], 'mean': [], 'payout': [], 'roi': [], 'faixa': Counter(), 'games': []
    }

    for removed in REMOVED_CONFIGS:
        results[removed] = {
            'best': [], 'mean': [], 'payout': [], 'roi': [], 'faixa': Counter(),
            'games': [], 'top13_hits': [], 'hit13': 0, 'hit14': 0,
        }

    for idx in range(MIN_HISTORY, len(draws)):
        history = draws[:idx]
        target = draws[idx]
        ranked, _ = build_recent_ranking(history)
        result_set = set(target['numeros'])

        # Usa o tamanho de jogos da primeira config como baseline do concurso.
        first_games, _ = generate_rotating_games_13(ranked, LOCKED_FIXED, set(REMOVED_CONFIGS[0]))
        random_ev = evaluate_random_baseline_custom(len(first_games), result_set, rng)
        random_metrics['best'].append(random_ev['best_mean'])
        random_metrics['mean'].append(random_ev['mean_hits_mean'])
        random_metrics['payout'].append(random_ev['payout_mean'])
        random_metrics['roi'].append(random_ev['roi_mean'])
        random_metrics['games'].append(len(first_games))
        for hit, avg_count in random_ev['faixa_mean'].items():
            random_metrics['faixa'][hit] += avg_count

        for removed in REMOVED_CONFIGS:
            games, core = generate_rotating_games_13(ranked, LOCKED_FIXED, set(removed))
            ev = evaluate_pack(games, result_set)
            data = results[removed]
            data['best'].append(ev['best'])
            data['mean'].append(ev['mean_hits'])
            data['payout'].append(ev['payout'])
            data['roi'].append(ev['roi'])
            data['games'].append(len(games))
            data['faixa'].update(ev['faixa'])
            data['top13_hits'].append(len(result_set.intersection(core)))
            if ev['best'] >= 13:
                data['hit13'] += 1
            if ev['best'] >= 14:
                data['hit14'] += 1

        if (idx - MIN_HISTORY + 1) % 500 == 0:
            print(f'Processado {idx - MIN_HISTORY + 1}/{len(draws) - MIN_HISTORY}')

    rnd_best = float(np.mean(random_metrics['best']))
    rnd_mean = float(np.mean(random_metrics['mean']))
    rnd_payout = float(np.mean(random_metrics['payout']))
    rnd_roi = float(np.mean(random_metrics['roi']))

    print('\nBaseline aleatório')
    print(f'Jogos médios: {float(np.mean(random_metrics["games"])):.1f}')
    print(f'Melhor={rnd_best:.3f} | Média={rnd_mean:.3f} | Payout=R$ {rnd_payout:,.2f} | ROI={rnd_roi:+.2f}%')

    rows = []
    for removed, data in results.items():
        total_games = sum(data['games'])
        rows.append({
            'removed': removed,
            'best': float(np.mean(data['best'])),
            'mean': float(np.mean(data['mean'])),
            'payout': float(np.mean(data['payout'])),
            'roi': float(np.mean(data['roi'])),
            'games': float(np.mean(data['games'])),
            'top13': float(np.mean(data['top13_hits'])),
            'hit13_pct': data['hit13'] / len(data['best']) * 100,
            'hit14_pct': data['hit14'] / len(data['best']) * 100,
            'g13': data['faixa'].get(13, 0.0) / total_games * 100 if total_games else 0.0,
            'g14': data['faixa'].get(14, 0.0) / total_games * 100 if total_games else 0.0,
        })

    def rank_score(row):
        return (
            (row['mean'] - rnd_mean) * 20.0
            + (row['best'] - rnd_best) * 5.0
            + (row['roi'] - rnd_roi) * 0.5
            + row['hit13_pct'] * 2.0
            + row['hit14_pct'] * 4.0
        )

    rows.sort(key=rank_score, reverse=True)

    print('\nRanking 13 fixos vs baseline')
    print(f"{'Removidos':<12} {'Jogos':>7} {'Best':>7} {'Mean':>7} {'Payout':>10} {'ROI':>9} {'13+':>7} {'14+':>7} {'Top13':>7}")
    for row in rows:
        removed = ','.join(str(x) for x in row['removed'])
        print(
            f"{removed:<12} {row['games']:>7.1f} {row['best']:>7.3f} {row['mean']:>7.3f} {row['payout']:>10.2f}"
            f" {row['roi']:>8.2f}% {row['hit13_pct']:>6.2f}% {row['hit14_pct']:>6.2f}% {row['top13']:>7.3f}"
        )

    best = rows[0]
    print('\nMelhor configuração 13 fixos')
    print(f"Removidos: {best['removed']}")
    print(f"Delta best:   {best['best'] - rnd_best:+.3f}")
    print(f"Delta mean:   {best['mean'] - rnd_mean:+.3f}")
    print(f"Delta payout: {best['payout'] - rnd_payout:+.2f}")
    print(f"Delta ROI:    {best['roi'] - rnd_roi:+.2f} pp")
    print(f"Delta 13+:    {best['hit13_pct']:+.2f}% absolutos")
    print(f"Delta 14+:    {best['hit14_pct']:+.2f}% absolutos")


if __name__ == '__main__':
    main()
