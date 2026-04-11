# -*- coding: utf-8 -*-
"""
POC: Estratégia de 14 fixos rotativos

Conceito operacional adotado para o teste:
1. Escolher os 14 melhores números pelo ranking recente
2. Os demais formam o pool complementar
3. Gerar um lote com todos os jogos: 14 fixos + 1 número do pool
4. Rotacionar o núcleo:
   - remover 1 número do núcleo inicial (não protegido)
   - promover 1 número do pool para o núcleo
   - gerar novo lote com o pool restante
5. Repetir até o pool zerar

Se o núcleo começa com 14 e o pool com 11, o total é:
11 + 10 + 9 + ... + 1 = 66 jogos

Esta POC usa ranking simples por frequência recente para definir os 14 melhores.
"""

import sys
from collections import Counter

import numpy as np
import pyodbc

sys.stdout.reconfigure(encoding='utf-8')

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
WINDOW = 30
MIN_HISTORY = 100
FIXED_TARGET = 14
RANDOM_PACKS = 20
LOCKED_FIXED = set()
LOCKED_REMOVED = set()

PREMIOS = {
    11: 7.0,
    12: 14.0,
    13: 35.0,
    14: 1000.0,
    15: 1800000.0,
}
CUSTO = 3.50


def carregar_resultados():
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
        )
        return [
            {"concurso": row[0], "numeros": tuple(sorted(int(x) for x in row[1:16]))}
            for row in cursor.fetchall()
        ]


def build_recent_ranking(history):
    counter = Counter()
    for draw in history[-WINDOW:]:
        counter.update(draw['numeros'])
    # desempate por menor número para estabilidade
    ranked = sorted(range(1, 26), key=lambda n: (-counter[n], n))
    return ranked, counter


def choose_initial_core(ranked, locked_fixed=None, locked_removed=None, fixed_target=FIXED_TARGET):
    locked_fixed = set(locked_fixed or [])
    locked_removed = set(locked_removed or [])
    available = [n for n in ranked if n not in locked_removed]
    core = []
    for n in sorted(locked_fixed):
        if n in available and n not in core:
            core.append(n)
    for n in available:
        if len(core) >= fixed_target:
            break
        if n not in core:
            core.append(n)
    pool = [n for n in available if n not in core]
    return core, pool


def choose_removal(core, locked_fixed=None, score_map=None):
    locked_fixed = set(locked_fixed or [])
    candidates = [n for n in core if n not in locked_fixed]
    if not candidates:
        return None
    # Remove o pior ranqueado do núcleo para maximizar chance da rotação ajudar.
    return sorted(candidates, key=lambda n: (score_map.get(n, 0), n))[0]


def choose_promotion(pool, score_map=None):
    if not pool:
        return None
    # Promove o melhor ranqueado restante.
    return sorted(pool, key=lambda n: (-score_map.get(n, 0), n))[0]


def generate_rotating_games(ranked, locked_fixed=None, locked_removed=None):
    score_map = {n: len(ranked) - idx for idx, n in enumerate(ranked)}
    core, pool = choose_initial_core(ranked, locked_fixed, locked_removed)

    games = []
    removed_forever = set(locked_removed or [])
    current_core = list(core)
    current_pool = list(pool)

    while current_pool:
        # Lote: 14 fixos + cada número ainda no pool
        for n in current_pool:
            game = tuple(sorted(current_core + [n]))
            games.append(game)

        # Rotação para o próximo lote
        promoted = choose_promotion(current_pool, score_map)
        removed = choose_removal(current_core, locked_fixed, score_map)

        if promoted is None or removed is None:
            break

        current_core.remove(removed)
        removed_forever.add(removed)

        current_pool.remove(promoted)
        current_core.append(promoted)

        current_pool = [n for n in current_pool if n not in removed_forever]

    # Remover duplicatas preservando ordem
    seen = set()
    unique_games = []
    for game in games:
        if game not in seen:
            seen.add(game)
            unique_games.append(game)
    return unique_games, core, pool


def evaluate_pack(games, result_set):
    hits = [len(result_set.intersection(game)) for game in games]
    faixa = Counter(hit for hit in hits if hit >= 11)
    payout = sum(PREMIOS[hit] for hit in hits if hit >= 11)
    cost = len(games) * CUSTO
    return {
        'best': max(hits) if hits else 0,
        'mean_hits': float(np.mean(hits)) if hits else 0.0,
        'faixa': faixa,
        'payout': payout,
        'roi': (payout - cost) / cost * 100 if cost else 0.0,
    }


def evaluate_random_baseline(n_games, result_set, rng):
    all_numbers = np.arange(1, 26)
    best_list = []
    mean_hits_list = []
    payout_list = []
    faixa_total = Counter()
    for _ in range(RANDOM_PACKS):
        games = [tuple(sorted(rng.choice(all_numbers, 15, replace=False).tolist())) for _ in range(n_games)]
        ev = evaluate_pack(games, result_set)
        best_list.append(ev['best'])
        mean_hits_list.append(ev['mean_hits'])
        payout_list.append(ev['payout'])
        faixa_total.update(ev['faixa'])
    avg_payout = float(np.mean(payout_list)) if payout_list else 0.0
    avg_roi = (avg_payout - n_games * CUSTO) / (n_games * CUSTO) * 100 if n_games else 0.0
    return {
        'best_mean': float(np.mean(best_list)) if best_list else 0.0,
        'mean_hits_mean': float(np.mean(mean_hits_list)) if mean_hits_list else 0.0,
        'payout_mean': avg_payout,
        'roi_mean': avg_roi,
        'faixa_mean': {k: v / RANDOM_PACKS for k, v in faixa_total.items()},
    }


def main():
    print('=' * 78)
    print('POC — 14 FIXOS ROTATIVOS')
    print('=' * 78)
    print(f'Janela ranking: últimos {WINDOW} concursos')
    print(f'Histórico mínimo: {MIN_HISTORY}')
    print(f'Fixos protegidos: {sorted(LOCKED_FIXED)}')
    print(f'Removidos protegidos: {sorted(LOCKED_REMOVED)}')

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

    sample_snapshots = []

    for idx in range(MIN_HISTORY, len(draws)):
        history = draws[:idx]
        target = draws[idx]
        ranked, score_counter = build_recent_ranking(history)
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
            sample_snapshots.append({
                'concurso': target['concurso'],
                'core': core,
                'pool': pool,
                'resultado': list(target['numeros']),
                'best_rot': rot['best'],
                'best_rand': rnd['best_mean'],
                'top14_hits': len(result_set.intersection(core)),
            })

    contests = metrics['contests']
    avg_games = float(np.mean(metrics['games_per_contest'])) if metrics['games_per_contest'] else 0.0
    print('\n1) Estrutura do método')
    print(f'Jogos médios por concurso: {avg_games:.1f}')
    print('Teórico sem travas: 66 jogos (11+10+...+1)')

    print('\n2) Desempenho histórico')
    rot_best = float(np.mean(metrics['best_rot'])) if metrics['best_rot'] else 0.0
    rnd_best = float(np.mean(metrics['best_rand'])) if metrics['best_rand'] else 0.0
    rot_mean = float(np.mean(metrics['mean_rot'])) if metrics['mean_rot'] else 0.0
    rnd_mean = float(np.mean(metrics['mean_rand'])) if metrics['mean_rand'] else 0.0
    rot_payout = float(np.mean(metrics['payout_rot'])) if metrics['payout_rot'] else 0.0
    rnd_payout = float(np.mean(metrics['payout_rand'])) if metrics['payout_rand'] else 0.0
    rot_roi = float(np.mean(metrics['roi_rot'])) if metrics['roi_rot'] else 0.0
    rnd_roi = float(np.mean(metrics['roi_rand'])) if metrics['roi_rand'] else 0.0
    print(f'Melhor acerto | Rotativo={rot_best:.3f} | Random={rnd_best:.3f} | delta={rot_best-rnd_best:+.3f}')
    print(f'Acerto médio  | Rotativo={rot_mean:.3f} | Random={rnd_mean:.3f} | delta={rot_mean-rnd_mean:+.3f}')
    print(f'Prêmio médio  | Rotativo=R$ {rot_payout:,.2f} | Random=R$ {rnd_payout:,.2f} | delta=R$ {rot_payout-rnd_payout:+,.2f}')
    print(f'ROI médio     | Rotativo={rot_roi:+.2f}% | Random={rnd_roi:+.2f}% | delta={rot_roi-rnd_roi:+.2f} pp')

    print('\n3) Faixas 11+')
    total_games = sum(metrics['games_per_contest'])
    print(f"{'Faixa':<8} {'Rotativo':>14} {'Random':>14} {'Selet':>9}")
    for hit in [11, 12, 13, 14, 15]:
        rot_count = metrics['faixa_rot'].get(hit, 0.0)
        rnd_count = metrics['faixa_rand'].get(hit, 0.0)
        rot_rate = rot_count / total_games * 100 if total_games else 0.0
        rnd_rate = rnd_count / total_games * 100 if total_games else 0.0
        sel = rot_rate / rnd_rate if rnd_rate > 0 else 0.0
        print(f'{hit:<8} {rot_rate:>11.3f}% {rnd_rate:>11.3f}% {sel:>8.3f}x')

    print('\n4) Quantos acertos já vêm nos 14 fixos')
    top14_hits_mean = float(np.mean(metrics['top14_hits'])) if metrics['top14_hits'] else 0.0
    top14_hits_ge11 = sum(1 for x in metrics['top14_hits'] if x >= 11) / contests * 100 if contests else 0.0
    print(f'Média de acertos dentro do núcleo de 14: {top14_hits_mean:.3f}')
    print(f'% concursos com 11+ já dentro do 14-base: {top14_hits_ge11:.2f}%')

    print('\n5) Exemplos rápidos')
    for sample in sample_snapshots:
        print(f"Concurso {sample['concurso']}: top14_hits={sample['top14_hits']} | best_rot={sample['best_rot']} | best_rand={sample['best_rand']:.2f}")
        print(f"  Núcleo14: {sample['core']}")
        print(f"  Pool11:   {sample['pool']}")
        print(f"  Resultado:{sample['resultado']}")

    print('\n6) Leitura do conceito')
    print('- A estratégia não tenta adivinhar diretamente os 15, mas faz uma varredura controlada em torno de um núcleo de 14.')
    print('- Se o núcleo inicial contiver muitos acertos, a rotação pode recuperar cedo o 15º número correto.')
    print('- Se o ranking dos 14 melhores estiver enviesado, o método colapsa porque todos os 66 jogos herdam esse erro inicial.')


if __name__ == '__main__':
    main()