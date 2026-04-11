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
LOCKED_REMOVED = {8}


def main():
    draws = carregar_resultados()
    rng = np.random.default_rng(42)

    metrics = {
        'contests': 0,
        'games_per_contest': [],
        'best_rot': [],
        'best_rand': [],
        'mean_rot': [],
        'mean_rand': [],
        'payout_rot': [],
        'payout_rand': [],
        'roi_rot': [],
        'roi_rand': [],
        'faixa_rot': Counter(),
        'faixa_rand': Counter(),
        'top14_hits': [],
    }

    samples = []
    for idx in range(MIN_HISTORY, len(draws)):
        history = draws[:idx]
        target = draws[idx]
        ranked, _ = build_recent_ranking(history)
        games, core, pool = generate_rotating_games(ranked, LOCKED_FIXED, LOCKED_REMOVED)
        result_set = set(target['numeros'])

        rot = evaluate_pack(games, result_set)
        rnd = evaluate_random_baseline(len(games), result_set, rng)

        metrics['contests'] += 1
        metrics['games_per_contest'].append(len(games))
        metrics['best_rot'].append(rot['best'])
        metrics['best_rand'].append(rnd['best_mean'])
        metrics['mean_rot'].append(rot['mean_hits'])
        metrics['mean_rand'].append(rnd['mean_hits_mean'])
        metrics['payout_rot'].append(rot['payout'])
        metrics['payout_rand'].append(rnd['payout_mean'])
        metrics['roi_rot'].append(rot['roi'])
        metrics['roi_rand'].append(rnd['roi_mean'])
        metrics['faixa_rot'].update(rot['faixa'])
        for hit, avg_count in rnd['faixa_mean'].items():
            metrics['faixa_rand'][hit] += avg_count
        metrics['top14_hits'].append(len(result_set.intersection(core)))

        if idx in [MIN_HISTORY, len(draws) - 2, len(draws) - 1]:
            samples.append((target['concurso'], core, pool, list(target['numeros']), len(result_set.intersection(core)), rot['best'], rnd['best_mean']))

    contests = metrics['contests']
    avg_games = float(np.mean(metrics['games_per_contest']))
    rot_best = float(np.mean(metrics['best_rot']))
    rnd_best = float(np.mean(metrics['best_rand']))
    rot_mean = float(np.mean(metrics['mean_rot']))
    rnd_mean = float(np.mean(metrics['mean_rand']))
    rot_payout = float(np.mean(metrics['payout_rot']))
    rnd_payout = float(np.mean(metrics['payout_rand']))
    rot_roi = float(np.mean(metrics['roi_rot']))
    rnd_roi = float(np.mean(metrics['roi_rand']))
    total_games = sum(metrics['games_per_contest'])
    top14_hits_mean = float(np.mean(metrics['top14_hits']))
    top14_hits_ge11 = sum(1 for x in metrics['top14_hits'] if x >= 11) / contests * 100 if contests else 0.0

    print('=' * 78)
    print('TESTE RAPIDO — 14 FIXOS ROTATIVOS COM FIXOS {1,25} E REMOVENDO 8')
    print('=' * 78)
    print(f'Jogos médios por concurso: {avg_games:.1f}')
    print(f'Melhor acerto | Rotativo={rot_best:.3f} | Random={rnd_best:.3f} | delta={rot_best-rnd_best:+.3f}')
    print(f'Acerto médio  | Rotativo={rot_mean:.3f} | Random={rnd_mean:.3f} | delta={rot_mean-rnd_mean:+.3f}')
    print(f'Prêmio médio  | Rotativo=R$ {rot_payout:,.2f} | Random=R$ {rnd_payout:,.2f} | delta=R$ {rot_payout-rnd_payout:+,.2f}')
    print(f'ROI médio     | Rotativo={rot_roi:+.2f}% | Random={rnd_roi:+.2f}% | delta={rot_roi-rnd_roi:+.2f} pp')
    print('\nFaixas 11+:')
    print(f"{'Faixa':<8} {'Rotativo':>14} {'Random':>14} {'Selet':>9}")
    for hit in [11, 12, 13, 14, 15]:
        rot_count = metrics['faixa_rot'].get(hit, 0.0)
        rnd_count = metrics['faixa_rand'].get(hit, 0.0)
        rot_rate = rot_count / total_games * 100 if total_games else 0.0
        rnd_rate = rnd_count / total_games * 100 if total_games else 0.0
        sel = rot_rate / rnd_rate if rnd_rate > 0 else 0.0
        print(f'{hit:<8} {rot_rate:>11.3f}% {rnd_rate:>11.3f}% {sel:>8.3f}x')
    print('\nNúcleo de 14:')
    print(f'Média de acertos dentro do núcleo: {top14_hits_mean:.3f}')
    print(f'% concursos com 11+ já dentro do 14-base: {top14_hits_ge11:.2f}%')
    print('\nExemplos:')
    for concurso, core, pool, resultado, top14_hits, best_rot, best_rand in samples:
        print(f'Concurso {concurso}: top14_hits={top14_hits} | best_rot={best_rot} | best_rand={best_rand:.2f}')
        print(f'  Núcleo14: {core}')
        print(f'  Pool:     {pool}')
        print(f'  Resultado:{resultado}')


if __name__ == '__main__':
    main()
