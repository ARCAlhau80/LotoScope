# -*- coding: utf-8 -*-
"""
pool23_hub — Módulo consolidado do Pool 23

Substitui a cadeia de 5 POCs interdependentes:
  poc_incompatibilidade_filtros_pool23.py  (base)
  poc_vizinhanca_historica_pool23.py       (contexto + vizinhança)
  poc_regime_3_bandas_pool23.py            (advisor 3 bandas)
  poc_exemplos_regime_3_bandas.py          (exemplos reais)
  poc_regimes_vizinhanca_pool23.py         (interpretação de regimes)

Uso:
  from pool23_hub import (
      build_filters_for_level, carregar_resultados, random_combos,
      build_context_features, choose_best_level, pick_band, BANDS,
      FEATURE_NAMES, RANDOM_SAMPLES, LEVELS, ...
  )
"""

import sys
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
import pyodbc

from lotofacil_lite.configuracao_filtros_pool23 import FILTROS_POR_NIVEL

sys.stdout.reconfigure(encoding='utf-8')

# ── Constantes ────────────────────────────────────────────────────────────────

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
RANDOM_SAMPLES = 200_000

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
NUCLEO_C1C2 = {2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 22, 24, 25}

LEVELS = [1, 2, 3, 4, 5, 6]
FEATURE_WINDOW = 12
K_NEIGHBORS = 40
MIN_HISTORY = 200

ALL_LEVELS = [1, 2, 3, 4, 5, 6]
BANDS = {'CONS': [1, 2], 'MID': [3], 'AGGR': [6]}

FEATURE_NAMES = [
    'sum_last', 'pares_last', 'primos_last', 'fib_last', 'faixa_6_20_last',
    'moldura_last', 'linha_spread_last', 'col_spread_last', 'seq_max_last',
    'count_1_25_last', 'repeats_last', 'sum_mean_12', 'sum_std_12',
    'pares_mean_12', 'primos_mean_12', 'fib_mean_12', 'faixa_6_20_mean_12',
    'seq_max_mean_12', 'hot_12', 'warm_12', 'cold_12', 'absent_12',
    'freq_1_12', 'freq_25_12',
]

# ── Filtros estruturais ──────────────────────────────────────────────────────


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


def random_combos(n_samples, rng):
    base = np.arange(1, 26)
    return [tuple(sorted(rng.choice(base, 15, replace=False).tolist())) for _ in range(n_samples)]


def filtro_soma(combo, config):
    return config['soma_min'] <= sum(combo) <= config['soma_max']


def filtro_pares(combo, config):
    if 'pares_min' not in config:
        return True
    qtde = sum(1 for n in combo if n % 2 == 0)
    return config['pares_min'] <= qtde <= config['pares_max']


def filtro_primos(combo, config):
    if 'primos_min' not in config:
        return True
    qtde = sum(1 for n in combo if n in PRIMOS)
    return config['primos_min'] <= qtde <= config['primos_max']


def filtro_seq_max(combo, config):
    if 'seq_max' not in config:
        return True
    nums = sorted(combo)
    max_seq = 1
    seq = 1
    for idx in range(1, len(nums)):
        if nums[idx] == nums[idx - 1] + 1:
            seq += 1
            max_seq = max(max_seq, seq)
        else:
            seq = 1
    return max_seq <= config['seq_max']


def filtro_linhas(combo, config):
    if not config.get('usar_filtro_linhas'):
        return True
    linhas = [0, 0, 0, 0, 0]
    for n in combo:
        linhas[(n - 1) // 5] += 1
    return all(config['linhas_min'] <= x <= config['linhas_max'] for x in linhas)


def filtro_colunas(combo, config):
    if not config.get('usar_filtro_colunas'):
        return True
    colunas = [0, 0, 0, 0, 0]
    for n in combo:
        colunas[(n - 1) % 5] += 1
    return all(config['colunas_min'] <= x <= config['colunas_max'] for x in colunas)


def filtro_qtde_6_25(combo, config):
    if not config.get('usar_filtro_qtde_6_25'):
        return True
    qtde = sum(1 for n in combo if 6 <= n <= 25)
    return qtde in set(config['qtde_6_25_valores'])


def filtro_fibonacci(combo, config):
    if not config.get('usar_filtro_fibonacci'):
        return True
    qtde = sum(1 for n in combo if n in FIBONACCI)
    return config['fibonacci_min'] <= qtde <= config['fibonacci_max']


def filtro_quintis(combo, config):
    if not config.get('usar_filtro_quintis'):
        return True
    quintis = [0, 0, 0, 0, 0]
    for n in combo:
        quintis[(n - 1) // 5] += 1
    return all(config['quintis_min'] <= x <= config['quintis_max'] for x in quintis)


def filtro_faixa_6_20(combo, config):
    if not config.get('usar_filtro_faixa_6_20'):
        return True
    qtde = sum(1 for n in combo if 6 <= n <= 20)
    return config['faixa_6_20_min'] <= qtde <= config['faixa_6_20_max']


def filtro_nucleo(combo, config):
    if 'nucleo_min' not in config:
        return True
    qtde = sum(1 for n in combo if n in NUCLEO_C1C2)
    return qtde >= config['nucleo_min']


def build_filters_for_level(level):
    config = FILTROS_POR_NIVEL[level]
    filters = {}
    if 'soma_min' in config:
        filters['soma'] = lambda c, cfg=config: filtro_soma(c, cfg)
    if 'pares_min' in config:
        filters['pares'] = lambda c, cfg=config: filtro_pares(c, cfg)
    if 'primos_min' in config:
        filters['primos'] = lambda c, cfg=config: filtro_primos(c, cfg)
    if 'seq_max' in config:
        filters['seq_max'] = lambda c, cfg=config: filtro_seq_max(c, cfg)
    if config.get('usar_filtro_linhas'):
        filters['linhas'] = lambda c, cfg=config: filtro_linhas(c, cfg)
    if config.get('usar_filtro_colunas'):
        filters['colunas'] = lambda c, cfg=config: filtro_colunas(c, cfg)
    if config.get('usar_filtro_qtde_6_25'):
        filters['qtde_6_25'] = lambda c, cfg=config: filtro_qtde_6_25(c, cfg)
    if config.get('usar_filtro_fibonacci'):
        filters['fibonacci'] = lambda c, cfg=config: filtro_fibonacci(c, cfg)
    if config.get('usar_filtro_quintis'):
        filters['quintis'] = lambda c, cfg=config: filtro_quintis(c, cfg)
    if config.get('usar_filtro_faixa_6_20'):
        filters['faixa_6_20'] = lambda c, cfg=config: filtro_faixa_6_20(c, cfg)
    if 'nucleo_min' in config:
        filters['nucleo'] = lambda c, cfg=config: filtro_nucleo(c, cfg)
    return filters


# ── Utilitários de análise ───────────────────────────────────────────────────


def pass_rate(combos, predicate):
    passed = sum(1 for combo in combos if predicate(combo))
    total = len(combos)
    return passed, passed / total if total else 0.0


def toxicity_index(real_rate, random_rate):
    if random_rate <= 0:
        return 0.0
    seletividade = real_rate / random_rate
    kill = 1.0 - real_rate
    return kill * max(0.0, 1.0 - seletividade)


def format_pct(value):
    return f'{value * 100:6.2f}%'


# ── Análise de nível (incompatibilidade) ────────────────────────────────────


def analyze_level(level, real_draws, random_draws):
    filters = build_filters_for_level(level)
    if not filters:
        return None

    results = {}
    for name, fn in filters.items():
        _, rr = pass_rate(real_draws, fn)
        _, pr = pass_rate(random_draws, fn)
        sel = rr / pr if pr > 0 else 0.0
        tox = toxicity_index(rr, pr)
        results[name] = {
            'real_rate': rr,
            'random_rate': pr,
            'selectivity': sel,
            'toxicity': tox,
        }

    pair_results = []
    names = sorted(filters.keys())
    for a, b in combinations(names, 2):
        fn = lambda combo, f1=filters[a], f2=filters[b]: f1(combo) and f2(combo)
        _, rr = pass_rate(real_draws, fn)
        _, pr = pass_rate(random_draws, fn)
        sel = rr / pr if pr > 0 else 0.0
        tox = toxicity_index(rr, pr)
        expected_ind = results[a]['real_rate'] * results[b]['real_rate']
        incompat = max(0.0, expected_ind - rr)
        pair_results.append({
            'combo': f'{a}+{b}',
            'real_rate': rr,
            'random_rate': pr,
            'selectivity': sel,
            'toxicity': tox,
            'incompatibility': incompat,
        })

    triplet_results = []
    if len(names) >= 3:
        for a, b, c in combinations(names, 3):
            fn = lambda combo, f1=filters[a], f2=filters[b], f3=filters[c]: f1(combo) and f2(combo) and f3(combo)
            _, rr = pass_rate(real_draws, fn)
            _, pr = pass_rate(random_draws, fn)
            sel = rr / pr if pr > 0 else 0.0
            tox = toxicity_index(rr, pr)
            triplet_results.append({
                'combo': f'{a}+{b}+{c}',
                'real_rate': rr,
                'random_rate': pr,
                'selectivity': sel,
                'toxicity': tox,
            })

    package_fn = lambda combo: all(fn(combo) for fn in filters.values())
    _, pkg_real = pass_rate(real_draws, package_fn)
    _, pkg_rand = pass_rate(random_draws, package_fn)
    package = {
        'real_rate': pkg_real,
        'random_rate': pkg_rand,
        'selectivity': pkg_real / pkg_rand if pkg_rand > 0 else 0.0,
        'toxicity': toxicity_index(pkg_real, pkg_rand),
        'count_filters': len(filters),
    }

    return {
        'level': level,
        'descricao': FILTROS_POR_NIVEL[level]['descricao'],
        'filters': results,
        'pairs': pair_results,
        'triplets': triplet_results,
        'package': package,
    }


# ── Contexto de vizinhança ──────────────────────────────────────────────────


def package_predicates(levels=None):
    if levels is None:
        levels = ALL_LEVELS
    predicates = {}
    for level in levels:
        filters = build_filters_for_level(level)
        predicates[level] = lambda combo, fns=list(filters.values()): all(fn(combo) for fn in fns)
    return predicates


def combo_stats(combo):
    nums = list(combo)
    pares = sum(1 for n in nums if n % 2 == 0)
    primos = sum(1 for n in nums if n in PRIMOS)
    fib = sum(1 for n in nums if n in FIBONACCI)
    faixa_6_20 = sum(1 for n in nums if 6 <= n <= 20)
    moldura = sum(1 for n in nums if n in {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25})
    centro = 15 - moldura
    linhas = [0, 0, 0, 0, 0]
    cols = [0, 0, 0, 0, 0]
    for n in nums:
        linhas[(n - 1) // 5] += 1
        cols[(n - 1) % 5] += 1
    seq_max = 1
    seq = 1
    nums_sorted = sorted(nums)
    for idx in range(1, len(nums_sorted)):
        if nums_sorted[idx] == nums_sorted[idx - 1] + 1:
            seq += 1
            seq_max = max(seq_max, seq)
        else:
            seq = 1
    return {
        'sum': sum(nums),
        'pares': pares,
        'primos': primos,
        'fib': fib,
        'faixa_6_20': faixa_6_20,
        'moldura': moldura,
        'centro': centro,
        'linha_spread': max(linhas) - min(linhas),
        'col_spread': max(cols) - min(cols),
        'seq_max': seq_max,
        'count_1_25': int(1 in nums) + int(25 in nums),
    }


def build_context_features(draws):
    contexts = []
    for idx in range(len(draws)):
        if idx < FEATURE_WINDOW:
            contexts.append(None)
            continue

        recent = draws[idx - FEATURE_WINDOW:idx]
        recent_stats = [combo_stats(d['numeros']) for d in recent]
        last_stats = recent_stats[-1]
        prev_draw = set(draws[idx - 2]['numeros']) if idx >= 2 else set()
        last_draw = set(draws[idx - 1]['numeros'])
        repeats_last = len(last_draw & prev_draw) if prev_draw else 0

        freq_counter = Counter()
        for draw in recent:
            freq_counter.update(draw['numeros'])

        hot_12 = sum(1 for _, f in freq_counter.items() if f >= 8)
        warm_12 = sum(1 for _, f in freq_counter.items() if f >= 6)
        cold_12 = sum(1 for n in range(1, 26) if freq_counter[n] <= 2)
        absent_12 = sum(1 for n in range(1, 26) if freq_counter[n] == 0)

        vec = np.array([
            last_stats['sum'],
            last_stats['pares'],
            last_stats['primos'],
            last_stats['fib'],
            last_stats['faixa_6_20'],
            last_stats['moldura'],
            last_stats['linha_spread'],
            last_stats['col_spread'],
            last_stats['seq_max'],
            last_stats['count_1_25'],
            repeats_last,
            np.mean([s['sum'] for s in recent_stats]),
            np.std([s['sum'] for s in recent_stats]),
            np.mean([s['pares'] for s in recent_stats]),
            np.mean([s['primos'] for s in recent_stats]),
            np.mean([s['fib'] for s in recent_stats]),
            np.mean([s['faixa_6_20'] for s in recent_stats]),
            np.mean([s['seq_max'] for s in recent_stats]),
            hot_12,
            warm_12,
            cold_12,
            absent_12,
            freq_counter[1],
            freq_counter[25],
        ], dtype=float)
        contexts.append(vec)
    return contexts


def standardize_matrix(matrix):
    mu = np.mean(matrix, axis=0)
    sigma = np.std(matrix, axis=0)
    sigma[sigma == 0] = 1.0
    return (matrix - mu) / sigma


def choose_best_level(scores_by_level):
    return sorted(scores_by_level.items(), key=lambda x: (-x[1], x[0]))[0][0]


# ── Advisor 3 bandas ─────────────────────────────────────────────────────────


def pick_band(scores_by_level):
    cons_level = choose_best_level({level: scores_by_level[level] for level in BANDS['CONS']})
    cons_score = scores_by_level[cons_level]
    mid_level = 3
    mid_score = scores_by_level[mid_level]
    aggr_level = 6
    aggr_score = scores_by_level[aggr_level]

    options = {
        'CONS': (cons_level, cons_score),
        'MID': (mid_level, mid_score),
        'AGGR': (aggr_level, aggr_score),
    }
    best_band = sorted(options.items(), key=lambda x: (-x[1][1], x[1][0]))[0]
    return best_band[0], best_band[1][0], options


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


def top_feature_deltas(target_vec, neighbor_matrix, top_n=5):
    mean_neighbors = np.mean(neighbor_matrix, axis=0)
    deltas = target_vec - mean_neighbors
    order = np.argsort(np.abs(deltas))[::-1][:top_n]
    return [(FEATURE_NAMES[idx], deltas[idx]) for idx in order]
