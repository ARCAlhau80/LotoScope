# -*- coding: utf-8 -*-
"""
POC: previsibilidade dos números 1 e 25 na base histórica

Objetivos:
- Medir frequência histórica de: ambos, apenas 1, apenas 25, nenhum
- Medir transições entre estados para detectar persistência/reversão
- Testar previsibilidade out-of-sample com modelos simples:
  * baseline global
  * Markov de 1 passo
  * janela recente

O alvo principal é o estado conjunto entre 1 e 25:
  B = ambos saem
  O = só 1 sai
  T = só 25 sai
  N = nenhum sai
"""

import math
import sys
from collections import Counter, defaultdict

import numpy as np
import pyodbc

sys.stdout.reconfigure(encoding='utf-8')

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
WINDOW = 30
MIN_TRAIN = 100


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
            {
                "concurso": row[0],
                "numeros": tuple(sorted(int(x) for x in row[1:16])),
            }
            for row in cursor.fetchall()
        ]


def classificar_estado(numeros):
    tem_1 = 1 in numeros
    tem_25 = 25 in numeros
    if tem_1 and tem_25:
        return 'B'
    if tem_1:
        return 'O'
    if tem_25:
        return 'T'
    return 'N'


def state_name(state):
    return {
        'B': 'Ambos',
        'O': 'So 1',
        'T': 'So 25',
        'N': 'Nenhum',
    }[state]


def soft_prob(counter, states=('B', 'O', 'T', 'N')):
    total = sum(counter.values())
    alpha = 1.0
    denom = total + alpha * len(states)
    return {state: (counter.get(state, 0) + alpha) / denom for state in states}


def one_hot_hit(pred_state, real_state):
    return 1.0 if pred_state == real_state else 0.0


def log_loss(prob_map, real_state):
    p = max(prob_map[real_state], 1e-12)
    return -math.log(p)


def brier_score(prob_map, real_state, states=('B', 'O', 'T', 'N')):
    score = 0.0
    for state in states:
        y = 1.0 if state == real_state else 0.0
        score += (prob_map[state] - y) ** 2
    return score / len(states)


def longest_streak(values):
    best = 0
    current = 0
    for value in values:
        if value:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def main():
    resultados = carregar_resultados()
    estados = [classificar_estado(r['numeros']) for r in resultados]
    total = len(estados)

    print('=' * 78)
    print('ANALISE HISTORICA 1 E 25')
    print('=' * 78)
    print(f'Concursos analisados: {total:,}')

    counts = Counter(estados)
    count_1 = sum(1 for r in resultados if 1 in r['numeros'])
    count_25 = sum(1 for r in resultados if 25 in r['numeros'])
    both = counts['B']
    only_1 = counts['O']
    only_25 = counts['T']
    none = counts['N']

    print('\n1) Frequencia historica')
    print(f'1 saiu:                 {count_1:>5,d} ({count_1 / total * 100:6.2f}%)')
    print(f'25 saiu:                {count_25:>5,d} ({count_25 / total * 100:6.2f}%)')
    print(f'Ambos (1 e 25):         {both:>5,d} ({both / total * 100:6.2f}%)')
    print(f'Apenas 1:               {only_1:>5,d} ({only_1 / total * 100:6.2f}%)')
    print(f'Apenas 25:              {only_25:>5,d} ({only_25 / total * 100:6.2f}%)')
    print(f'Nenhum:                 {none:>5,d} ({none / total * 100:6.2f}%)')
    print(f'Pelo menos um dos dois: {total - none:>5,d} ({(total - none) / total * 100:6.2f}%)')
    print(f'Exatamente um dos dois: {only_1 + only_25:>5,d} ({(only_1 + only_25) / total * 100:6.2f}%)')

    p_num = 15 / 25
    p_both_ind = p_num * p_num
    p_none_ind = (1 - p_num) * (1 - p_num)
    p_exactly_one_ind = 2 * p_num * (1 - p_num)
    print('\n2) Comparacao com expectativa neutra (independencia simplificada)')
    print(f'Ambos esperado ~ {p_both_ind * 100:6.2f}% | observado {both / total * 100:6.2f}% | delta {(both / total - p_both_ind) * 100:+6.2f} pp')
    print(f'Exatamente um esperado ~ {p_exactly_one_ind * 100:6.2f}% | observado {(only_1 + only_25) / total * 100:6.2f}% | delta {((only_1 + only_25) / total - p_exactly_one_ind) * 100:+6.2f} pp')
    print(f'Nenhum esperado ~ {p_none_ind * 100:6.2f}% | observado {none / total * 100:6.2f}% | delta {(none / total - p_none_ind) * 100:+6.2f} pp')

    print('\n3) Matriz de transicao entre estados')
    transitions = defaultdict(Counter)
    for prev_state, next_state in zip(estados[:-1], estados[1:]):
        transitions[prev_state][next_state] += 1
    print(f"{'Origem':>10s} {'Ambos':>10s} {'So 1':>10s} {'So 25':>10s} {'Nenhum':>10s}")
    for prev in ('B', 'O', 'T', 'N'):
        row_total = sum(transitions[prev].values())
        probs = {state: transitions[prev][state] / row_total * 100 if row_total else 0.0 for state in ('B', 'O', 'T', 'N')}
        print(f"{state_name(prev):>10s} {probs['B']:>9.2f}% {probs['O']:>9.2f}% {probs['T']:>9.2f}% {probs['N']:>9.2f}%")

    print('\n4) Persistencia simples')
    for target in ('B', 'O', 'T', 'N'):
        base = counts[target] / total
        next_same = transitions[target][target] / sum(transitions[target].values()) if sum(transitions[target].values()) else 0.0
        print(f'{state_name(target):>10s}: base={base * 100:6.2f}% | repetir no concurso seguinte={next_same * 100:6.2f}% | delta={(next_same - base) * 100:+6.2f} pp')

    tem_1_series = [1 in r['numeros'] for r in resultados]
    tem_25_series = [25 in r['numeros'] for r in resultados]
    ambos_series = [state == 'B' for state in estados]
    nenhum_series = [state == 'N' for state in estados]
    print('\n5) Sequencias maximas')
    print(f'Maior sequencia com 1 saindo:        {longest_streak(tem_1_series)}')
    print(f'Maior sequencia com 25 saindo:       {longest_streak(tem_25_series)}')
    print(f'Maior sequencia com ambos saindo:    {longest_streak(ambos_series)}')
    print(f'Maior sequencia com nenhum saindo:   {longest_streak(nenhum_series)}')

    print('\n6) Teste de previsibilidade out-of-sample')
    global_counter = Counter(estados[:MIN_TRAIN])
    by_prev_counter = defaultdict(Counter)
    for prev_state, next_state in zip(estados[:MIN_TRAIN - 1], estados[1:MIN_TRAIN]):
        by_prev_counter[prev_state][next_state] += 1

    scores = {
        'global': {'acc': 0.0, 'll': 0.0, 'brier': 0.0},
        'markov1': {'acc': 0.0, 'll': 0.0, 'brier': 0.0},
        'janela30': {'acc': 0.0, 'll': 0.0, 'brier': 0.0},
    }
    n_eval = 0

    for idx in range(MIN_TRAIN, total):
        real_state = estados[idx]
        prev_state = estados[idx - 1]

        prob_global = soft_prob(global_counter)
        pred_global = max(prob_global, key=prob_global.get)

        markov_counter = by_prev_counter[prev_state]
        if sum(markov_counter.values()) == 0:
            prob_markov = prob_global
        else:
            prob_markov = soft_prob(markov_counter)
        pred_markov = max(prob_markov, key=prob_markov.get)

        recent_states = estados[max(0, idx - WINDOW):idx]
        prob_window = soft_prob(Counter(recent_states))
        pred_window = max(prob_window, key=prob_window.get)

        for name, pred, prob_map in (
            ('global', pred_global, prob_global),
            ('markov1', pred_markov, prob_markov),
            ('janela30', pred_window, prob_window),
        ):
            scores[name]['acc'] += one_hot_hit(pred, real_state)
            scores[name]['ll'] += log_loss(prob_map, real_state)
            scores[name]['brier'] += brier_score(prob_map, real_state)

        n_eval += 1
        global_counter[real_state] += 1
        by_prev_counter[prev_state][real_state] += 1

    print(f"{'Modelo':>10s} {'Acuracia':>10s} {'LogLoss':>10s} {'Brier':>10s}")
    for name in ('global', 'markov1', 'janela30'):
        print(f"{name:>10s} {scores[name]['acc'] / n_eval * 100:>9.2f}% {scores[name]['ll'] / n_eval:>9.4f} {scores[name]['brier'] / n_eval:>9.4f}")

    print('\n7) Sinal por alvo binario para rede neural')
    bin_targets = {
        '1_sai': tem_1_series,
        '25_sai': tem_25_series,
        'ambos': ambos_series,
        'nenhum': nenhum_series,
    }
    for label, series in bin_targets.items():
        base_rate = np.mean(series)
        repeat = np.mean([a == b for a, b in zip(series[:-1], series[1:])])
        persistence_if_true = np.mean([b for a, b in zip(series[:-1], series[1:]) if a]) if any(series[:-1]) else 0.0
        persistence_if_false = np.mean([not b for a, b in zip(series[:-1], series[1:]) if not a]) if any(not x for x in series[:-1]) else 0.0
        print(f'{label:>8s}: base={base_rate * 100:6.2f}% | repeticao bruta={repeat * 100:6.2f}% | P(1 no t+1 | 1 no t)={persistence_if_true * 100:6.2f}% | P(0 no t+1 | 0 no t)={persistence_if_false * 100:6.2f}%')

    print('\n8) Leitura pratica')
    best_model = min(scores.items(), key=lambda x: x[1]['ll'])
    worst_model = max(scores.items(), key=lambda x: x[1]['ll'])
    print(f'Melhor modelo probabilistico simples: {best_model[0]} (logloss={best_model[1]["ll"] / n_eval:.4f})')
    print(f'Pior modelo probabilistico simples:   {worst_model[0]} (logloss={worst_model[1]["ll"] / n_eval:.4f})')
    print('Se o ganho do Markov/janela sobre o baseline global for pequeno, o padrao existe mas e fraco.')
    print('Se houver ganho consistente, vale testar esses alvos como features/heads auxiliares da rede neural.')


if __name__ == '__main__':
    main()