#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import random
from collections import Counter
from typing import List, Set

A = set(range(2,10))
B = set(range(10,18))
C = set(range(18,26))
ALL = set(range(1,26))

CONN_STR = ('DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;')

# Parameters
WINDOW_RECENT = 5
WINDOW_LARGE = 30
START_BACKTEST_LAST_N = 200  # analyze last N contests
RANDOM_COMBOS_PER_STEP = 40  # random 15-number combos per step (baseline)
PCT_VARIANTES = 0.2
GROUP_TARGET = {'A': (4,1), 'B': (5,1), 'C': (4,1)}  # target,count_tolerance (base,tol)
MIN_MENORES = (6,9)  # min..max


def conectar():
    return pyodbc.connect(CONN_STR)


def carregar_historico():
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute('SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso ASC')
        rows = cur.fetchall()
    concursos = [r[0] for r in rows]
    resultados = [set(r[1:16]) for r in rows]
    return concursos, resultados


def freq_in_window(resultados, until_idx, window):
    # count frequency of numbers in resultados[until_idx-window:until_idx]
    start = max(0, until_idx - window)
    freq = Counter()
    for s in resultados[start:until_idx]:
        freq.update(s)
    return freq


def consecutive_absence(resultados, until_idx, numero=1):
    # count how many consecutive draws before until_idx that number was absent
    cnt = 0
    for i in range(until_idx-1, -1, -1):
        if numero not in resultados[i]:
            cnt += 1
        else:
            break
    return cnt


def grupo_counts(comb: Set[int]):
    a = len(comb & A)
    b = len(comb & B)
    c = len(comb & C)
    return a,b,c


def menores_count(comb: Set[int]):
    # menores defined as 1..12
    return len([n for n in comb if n <= 12])


def choose_worst_number(combo: Set[int], score_map: Counter):
    # choose number in combo with lowest score_map (if tie choose highest number)
    best = None
    worst_score = None
    for n in combo:
        if n == 1:
            continue
        s = score_map.get(n, 0)
        if worst_score is None or s < worst_score or (s==worst_score and n>best):
            worst_score = s
            best = n
    return best


def validate_variant(combo: Set[int]):
    a,b,c = grupo_counts(combo)
    ta,ta_tol = GROUP_TARGET['A']
    tb,tb_tol = GROUP_TARGET['B']
    tc,tc_tol = GROUP_TARGET['C']
    if abs(a-ta) > ta_tol or abs(b-tb) > tb_tol or abs(c-tc) > tc_tol:
        return False
    menores = menores_count(combo)
    if menores < MIN_MENORES[0] or menores > MIN_MENORES[1]:
        return False
    return True


def poc_backtest():
    concursos, resultados = carregar_historico()
    n = len(resultados)
    start_idx = max(WINDOW_LARGE, n - START_BACKTEST_LAST_N)

    stats = {
        'baseline_hits': 0.0,
        'variant_hits': 0.0,
        'baseline_total': 0,
        'variant_total': 0,
        'variants_created': 0,
        'variants_accepted': 0
    }

    rnd = random.Random(42)

    for idx in range(start_idx, n):
        # history up to idx (next contest is resultados[idx])
        # compute score_map based on freq in large window
        freq30 = freq_in_window(resultados, idx, WINDOW_LARGE)
        score_map = freq30  # higher freq => higher score

        absence1 = consecutive_absence(resultados, idx, 1)
        freq5_1 = freq_in_window(resultados, idx, WINDOW_RECENT).get(1,0)
        # trigger rules
        trigger = (absence1 >= 4) or (freq5_1 >= 1)

        # generate random baseline combos
        baseline_combos = []
        for _ in range(RANDOM_COMBOS_PER_STEP):
            comb = set(rnd.sample(range(1,26), 15))
            baseline_combos.append(comb)

        # sample subset to try variants
        n_try = int(RANDOM_COMBOS_PER_STEP * PCT_VARIANTES)
        variants = []
        for comb in rnd.sample(baseline_combos, n_try):
            stats['variants_created'] += 1
            if not trigger:
                continue
            # choose worst number and substitute with 1
            worst = choose_worst_number(comb, score_map)
            if worst is None:
                continue
            variant = set(comb)
            if 1 in variant:
                continue
            variant.remove(worst)
            variant.add(1)
            # validate balance
            if validate_variant(variant):
                variants.append((comb, variant))
                stats['variants_accepted'] += 1

        # evaluate baseline and variants against real result
        real = resultados[idx]
        for comb in baseline_combos:
            hits = len(comb & real)
            stats['baseline_hits'] += hits
            stats['baseline_total'] += 1
        for base, var in variants:
            hits = len(var & real)
            stats['variant_hits'] += hits
            stats['variant_total'] += 1

    # summarize
    avg_base = stats['baseline_hits'] / stats['baseline_total'] if stats['baseline_total']>0 else 0
    avg_var = stats['variant_hits'] / stats['variant_total'] if stats['variant_total']>0 else 0
    print('POC Coringa 1 - resultados')
    print('Backtest período:', START_BACKTEST_LAST_N, 'concursos (aprox)')
    print('Random combos per step:', RANDOM_COMBOS_PER_STEP)
    print('Variantes criadas (tentativas):', stats['variants_created'])
    print('Variantes aceitas (aplicar):', stats['variants_accepted'])
    print('Média acertos baseline (por combo):', round(avg_base,4))
    print('Média acertos variante (por combo):', round(avg_var,4))
    if stats['variant_total']>0:
        print('Delta média (var - base):', round(avg_var-avg_base,6))

if __name__ == "__main__":
    poc_backtest()
