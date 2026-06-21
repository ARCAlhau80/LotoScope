"""Modulo de analise completa para o dashboard Lotoscopio"""

import sys
from collections import defaultdict
from datetime import datetime
import pyodbc
import numpy as np

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
POSICOES = [f'N{i}' for i in range(1, 16)]
NUMEROS = list(range(1, 26))
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
WINDOW = 50
ALPHA = 0.6


def carregar_resultados():
    with pyodbc.connect(CONN_STR) as conn:
        c = conn.cursor()
        c.execute('SELECT Concurso,N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso')
        return [{'concurso': r[0], 'numeros': [int(x) for x in r[1:16]]} for r in c.fetchall()]


def build_ocorrencias(resultados):
    occ = {p: defaultdict(list) for p in POSICOES}
    for idx, r in enumerate(resultados):
        for pi, p in enumerate(POSICOES):
            occ[p][r['numeros'][pi]].append(idx)
    return occ


def calcular_lambdas(ocorrencias, total_draws):
    dados = {}
    for pos in POSICOES:
        dados[pos] = {}
        for num in NUMEROS:
            o = ocorrencias[pos][num]
            ch = len(o)
            lh = ch / total_draws if total_draws > 0 else 0.0
            cutoff = total_draws - WINDOW
            o_rec = [i for i in o if i >= cutoff]
            cr = len(o_rec)
            lr = cr / WINDOW if total_draws >= WINDOW and WINDOW > 0 else 0.0
            lb = ALPHA * lh + (1 - ALPHA) * lr
            ui = max(o) if o else None
            gap = (total_draws - 1 - ui) if ui is not None else total_draws
            dados[pos][num] = {
                'lambda_hist': round(lh, 4), 'lambda_recent': round(lr, 4), 'lambda_blend': round(lb, 4),
                'count_hist': ch, 'count_recent': cr, 'gap': gap,
            }
    return dados


def classificar_qmf(freq_30_window, freq_total_window):
    """Classifica numeros em quentes/mornos/frios baseado em freq dos ultimos 30."""
    s = sorted(freq_30_window.items(), key=lambda x: -x[1])
    q_set = {n for n, _ in s[:10]}
    f_set = {n for n, _ in sorted(freq_30_window.items(), key=lambda x: (x[1], freq_total_window.get(x[0], 0)))[:10]}
    m_set = {n for n in range(1, 26) if n not in q_set and n not in f_set}
    return q_set, m_set, f_set


def analisar_transicao_quentes_frios(resultados, janela_class=30, ultimos_n=100):
    """
    Para cada sorteio, classifica os numeros em Q/M/F com base nos `janela_class`
    sorteios anteriores, depois ve quantos de cada categoria sairam no sorteio.
    Retorna medias e tendencia dos ultimos `ultimos_n` sorteios.
    """
    total = len(resultados)
    n = min(ultimos_n, total - janela_class - 1)

    registros = []
    for idx in range(janela_class, total):
        window = resultados[idx - janela_class:idx]
        freq_w = {nu: 0 for nu in NUMEROS}
        freq_t = {nu: 0 for nu in NUMEROS}
        for r in resultados[:idx]:
            for nu in r['numeros']:
                freq_t[nu] += 1
        for r in window:
            for nu in r['numeros']:
                freq_w[nu] += 1

        q_set, m_set, f_set = classificar_qmf(freq_w, freq_t)
        nums_saidos = resultados[idx]['numeros']
        qtd_q = sum(1 for n in nums_saidos if n in q_set)
        qtd_m = sum(1 for n in nums_saidos if n in m_set)
        qtd_f = sum(1 for n in nums_saidos if n in f_set)

        registros.append({
            'concurso': resultados[idx]['concurso'],
            'quentes': qtd_q, 'mornos': qtd_m, 'frios': qtd_f,
            'pct_q': round(qtd_q / 15 * 100, 1),
            'pct_m': round(qtd_m / 15 * 100, 1),
            'pct_f': round(qtd_f / 15 * 100, 1),
            'q_set': sorted(q_set), 'm_set': sorted(m_set), 'f_set': sorted(f_set),
        })

    # Medias gerais
    medias = {
        'quentes': round(sum(r['quentes'] for r in registros) / len(registros), 2),
        'mornos': round(sum(r['mornos'] for r in registros) / len(registros), 2),
        'frios': round(sum(r['frios'] for r in registros) / len(registros), 2),
        'pct_q': round(sum(r['pct_q'] for r in registros) / len(registros), 1),
        'pct_m': round(sum(r['pct_m'] for r in registros) / len(registros), 1),
        'pct_f': round(sum(r['pct_f'] for r in registros) / len(registros), 1),
        'total_sorteios': len(registros),
    }

    # Ultimos 20 registros para o grafico
    recentes = registros[-20:]

    # Tendencia: comparar metade recente vs metade antiga
    meio = len(registros) // 2
    antiga = registros[:meio]
    recente = registros[-meio:]
    tendencia = {
        'quentes': round(sum(r['quentes'] for r in recente) / len(recente) - sum(r['quentes'] for r in antiga) / len(antiga), 2),
        'mornos': round(sum(r['mornos'] for r in recente) / len(recente) - sum(r['mornos'] for r in antiga) / len(antiga), 2),
        'frios': round(sum(r['frios'] for r in recente) / len(recente) - sum(r['frios'] for r in antiga) / len(antiga), 2),
    }

    return {
        'medias': medias,
        'recentes': recentes,
        'tendencia': tendencia,
    }


def analise_completa():
    resultados = carregar_resultados()
    total = len(resultados)
    occ = build_ocorrencias(resultados)
    dados = calcular_lambdas(occ, total)
    ultimo = resultados[-1]

    # Frequencia total
    freq_total = {n: 0 for n in NUMEROS}
    for r in resultados:
        for n in r['numeros']:
            freq_total[n] += 1

    # Frequencia ultimos 30
    freq_30 = {n: 0 for n in NUMEROS}
    for r in resultados[-30:]:
        for n in r['numeros']:
            freq_30[n] += 1

    # Gaps
    gaps = {}
    for n in NUMEROS:
        last = max(idx for idx, r in enumerate(resultados) if n in r['numeros'])
        gaps[n] = total - 1 - last

    # Numeros quentes (top 10 por frequencia nos ultimos 30)
    sorted_freq = sorted(freq_30.items(), key=lambda x: -x[1])
    quentes = sorted_freq[:10]
    frios = sorted(freq_30.items(), key=lambda x: (x[1], freq_total[x[0]]))[:10]
    quentes_set = {n for n, _ in quentes}
    frios_set = {n for n, _ in frios}
    mornos = [(n, f) for n, f in sorted_freq if n not in quentes_set and n not in frios_set]

    # Previsao posicional (top-3 por posicao)
    previsao = {}
    for pos in POSICOES:
        nums = dados[pos]
        top3 = sorted(
            [(n, nums[n]['lambda_blend']) for n in NUMEROS if nums[n]['lambda_blend'] > 0],
            key=lambda x: -x[1]
        )[:3]
        previsao[pos] = [{'numero': n, 'prob': round(p, 4)} for n, p in top3]

    # Palpite completo (top-1 de cada posicao)
    palpite = [previsao[p][0]['numero'] for p in POSICOES]

    # Numeros atrasados por posicao (P(gap) < 5%)
    atrasados_pos = {}
    for pos in POSICOES:
        atr = []
        for n in NUMEROS:
            gap = dados[pos][n]['gap']
            lb = dados[pos][n]['lambda_blend']
            p_gap = np.exp(-lb * gap) if lb > 0 else 1.0
            if p_gap < 0.05 and gap > 0:
                atr.append({'numero': n, 'p_gap': round(p_gap, 4), 'gap': gap, 'lambda_blend': lb})
        atrasados_pos[pos] = sorted(atr, key=lambda x: x['p_gap'])

    # Ciclos: compare freq_30 vs freq_historica_esperada
    freq_historica = {n: freq_total[n] / total * 30 for n in NUMEROS}
    ciclos = {}
    for n in NUMEROS:
        diff = freq_30[n] - freq_historica[n]
        if diff > 1.5:
            estado = 'aquecendo'
        elif diff < -1.5:
            estado = 'esfriando'
        else:
            estado = 'estavel'
        ciclos[n] = {'freq_30': freq_30[n], 'freq_esperada': round(freq_historica[n], 1), 'diferenca': round(diff, 1), 'estado': estado}

    # Estatisticas do ultimo sorteio
    nums_ultimo = ultimo['numeros']
    ultimo_stats = {
        'concurso': ultimo['concurso'],
        'numeros': nums_ultimo,
        'soma': sum(nums_ultimo),
        'pares': sum(1 for n in nums_ultimo if n % 2 == 0),
        'impares': sum(1 for n in nums_ultimo if n % 2 == 1),
        'primos': sum(1 for n in nums_ultimo if n in PRIMOS),
    }

    # Analise de transicao: quantos numeros de cada categoria saem no sorteio seguinte
    transicao = analisar_transicao_quentes_frios(resultados)

    return {
        'ultimo_concurso': ultimo['concurso'],
        'total_sorteios': total,
        'ultimo_sorteio': ultimo_stats,
        'frequencia_total': freq_total,
        'frequencia_30': freq_30,
        'gaps': gaps,
        'numeros_quentes': quentes,
        'numeros_frios': frios,
        'numeros_mornos': mornos,
        'previsao_posicional': previsao,
        'palpite': palpite,
        'atrasados_posicionais': {k: v for k, v in atrasados_pos.items() if v},
        'ciclos': ciclos,
        'transicao_qmf': transicao,
        'timestamp': datetime.now().isoformat(),
    }
