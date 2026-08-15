# -*- coding: utf-8 -*-
"""
BACKTEST DE RETENCAO - FILTRO BANDAS POSICIONAIS POISSON (Pool 23)
===================================================================
Walk-forward honesto: para cada janela de 30 concursos, o template
(previsto + banda) e derivado APENAS do passado:
  - previsto por posicao = top-1 lambda_blend (historico ate a janela)
  - banda 60%/90% = menor intervalo de desvio das janelas ANTERIORES

Mede:
  1. Retencao real de jackpots por tolerancia (0..5 violacoes) e cobertura
  2. Distribuicao do numero de violacoes por concurso
  3. Comparacao com o modelo binomial teorico (independencia)
  4. Seletividade: % de combos aleatorios que passam no filtro
     (template atual, 200k amostras, como random_combos do pool23_hub)

Resultado: recomendacao de tolerancia por nivel do Pool 23.

Uso:
  python backtest_bandas_posicionais_pool23.py
"""

import math
from collections import defaultdict

import numpy as np
import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
POSICOES = [f'N{i}' for i in range(1, 16)]
NUMEROS = list(range(1, 26))
TAM_JANELA = 30
WINDOW_LAMBDA = 50
ALPHA = 0.6
COBERTURAS = (0.60, 0.90)
TOLERANCIAS = list(range(0, 6))
MIN_DESVIOS_BANDA = 240
RANDOM_SAMPLES = 200_000
RNG_SEED = 42


def carregar_resultados():
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 '
            'FROM Resultados_INT ORDER BY Concurso ASC'
        )
        return [
            {'concurso': row[0], 'numeros': [int(x) for x in row[1:16]]}
            for row in cursor.fetchall()
        ]


def build_matriz_ocorrencias(resultados):
    ocorrencias = {p: defaultdict(list) for p in POSICOES}
    for idx, r in enumerate(resultados):
        for pos_idx, pos in enumerate(POSICOES):
            ocorrencias[pos][r['numeros'][pos_idx]].append(idx)
    return ocorrencias


def calcular_lambdas(ocorrencias, total_draws):
    dados = {}
    for pos in POSICOES:
        dados[pos] = {}
        for num in NUMEROS:
            occ = ocorrencias[pos][num]
            lambda_hist = len(occ) / total_draws if total_draws > 0 else 0.0
            if total_draws >= WINDOW_LAMBDA:
                cutoff = total_draws - WINDOW_LAMBDA
                count_recent = sum(1 for i in occ if i >= cutoff)
                lambda_recent = count_recent / WINDOW_LAMBDA
            else:
                lambda_recent = 0.0
            dados[pos][num] = ALPHA * lambda_hist + (1 - ALPHA) * lambda_recent
    return dados


def previsao_poisson(dados):
    return {
        pos: max(NUMEROS, key=lambda n: (dados[pos][n], -n))
        for pos in POSICOES
    }


def banda_minima(desvios, cobertura):
    """Menor intervalo [a, b] de desvios que cobre >= cobertura dos casos."""
    s = np.sort(np.asarray(desvios))
    n = len(s)
    k = max(1, math.ceil(cobertura * n))
    larguras = s[k - 1:] - s[:n - k + 1]
    i = int(np.argmin(larguras))
    return int(s[i]), int(s[i + k - 1])


def walk_forward(resultados):
    """Retorna janelas com previsto, desvios e violacoes por concurso."""
    total = len(resultados)
    janelas = []
    acumulado = {p: [] for p in POSICOES}

    for w0 in range(0, total, TAM_JANELA):
        fim = min(w0 + TAM_JANELA, total)
        if w0 < 60 or fim - w0 < TAM_JANELA // 2:
            continue

        historico = resultados[:w0]
        dados = calcular_lambdas(build_matriz_ocorrencias(historico), len(historico))
        previsto = previsao_poisson(dados)

        bandas_ok = all(len(acumulado[p]) >= MIN_DESVIOS_BANDA for p in POSICOES)
        bandas = None
        if bandas_ok:
            bandas = {
                cov: {p: banda_minima(acumulado[p], cov) for p in POSICOES}
                for cov in COBERTURAS
            }

        desvios_janela = {p: [] for p in POSICOES}
        violacoes_por_concurso = []
        for idx in range(w0, fim):
            real = resultados[idx]['numeros']
            viol = {cov: 0 for cov in COBERTURAS} if bandas_ok else None
            for pi, pos in enumerate(POSICOES):
                d = real[pi] - previsto[pos]
                desvios_janela[pos].append(d)
                if bandas_ok:
                    for cov in COBERTURAS:
                        lo, hi = bandas[cov][pos]
                        if not (lo <= d <= hi):
                            viol[cov] += 1
            if bandas_ok:
                violacoes_por_concurso.append({
                    'concurso': resultados[idx]['concurso'],
                    **{f'v{int(cov * 100)}': viol[cov] for cov in COBERTURAS},
                })

        for pos in POSICOES:
            acumulado[pos].extend(desvios_janela[pos])

        janelas.append({
            'w0': w0,
            'previsto': previsto,
            'bandas_validas': bandas_ok,
            'violacoes': violacoes_por_concurso,
        })

    return janelas, acumulado


def separador(titulo):
    print(f"\n{'=' * 92}")
    print(f"  {titulo}")
    print('=' * 92)


def main():
    print('BACKTEST DE RETENCAO - FILTRO BANDAS POSICIONAIS POISSON')
    resultados = carregar_resultados()
    print(f'  {len(resultados)} concursos carregados')

    print('Executando walk-forward...')
    janelas, acumulado = walk_forward(resultados)
    concursos_avaliados = [v for j in janelas if j['bandas_validas'] for v in j['violacoes']]
    n = len(concursos_avaliados)
    print(f'  {len(janelas)} janelas, {n} concursos avaliados com bandas walk-forward')

    separador('BLOCO 1 - RETENCAO REAL DE JACKPOTS POR TOLERANCIA')
    print('  Retencao = % dos concursos reais que PASSARIAM no filtro')
    print('  Binomial = modelo teorico assumindo independencia entre posicoes')
    for cov in COBERTURAS:
        chave = f'v{int(cov * 100)}'
        viol = np.array([c[chave] for c in concursos_avaliados])
        print(f'\n  --- Cobertura {int(cov * 100)}% ---')
        print(f'  {"Tolerancia":<12}{"Retencao real":>15}{"Binomial teor.":>16}{"Diferenca":>11}')
        for tol in TOLERANCIAS:
            real = float(np.mean(viol <= tol)) * 100
            teoria = sum(
                math.comb(15, k) * (1 - cov) ** k * cov ** (15 - k)
                for k in range(tol + 1)
            ) * 100
            print(f'  <= {tol:<9}{real:>14.1f}%{teoria:>15.1f}%{real - teoria:>+10.1f}pp')
        print(f'  Violacoes por concurso: media={np.mean(viol):.2f} '
              f'mediana={np.median(viol):.0f} max={np.max(viol)}')

    separador('BLOCO 2 - SELETIVIDADE (200k combos aleatorios, template atual)')
    ocorrencias = build_matriz_ocorrencias(resultados)
    dados = calcular_lambdas(ocorrencias, len(resultados))
    previsto = previsao_poisson(dados)
    bandas_full = {
        cov: {p: banda_minima(acumulado[p], cov) for p in POSICOES}
        for cov in COBERTURAS
    }
    print(f'  Template atual: {[previsto[p] for p in POSICOES]}')

    rng = np.random.default_rng(RNG_SEED)
    amostra = np.sort(rng.random((RANDOM_SAMPLES, 25)).argsort(axis=1)[:, :15] + 1, axis=1)

    for cov in COBERTURAS:
        viol = np.zeros(RANDOM_SAMPLES, dtype=np.int32)
        for pi, pos in enumerate(POSICOES):
            lo, hi = bandas_full[cov][pos]
            alvo = previsto[pos]
            fora = (amostra[:, pi] < alvo + lo) | (amostra[:, pi] > alvo + hi)
            viol += fora
        print(f'\n  --- Cobertura {int(cov * 100)}% ---')
        print(f'  {"Tolerancia":<12}{"% combos passam":>17}{"Reducao do espaco":>19}')
        for tol in TOLERANCIAS:
            passa = float(np.mean(viol <= tol)) * 100
            print(f'  <= {tol:<9}{passa:>16.2f}%{100 - passa:>18.2f}%')

    separador('BLOCO 3 - RECOMENDACAO POR NIVEL (meta: preservacao de jackpots)')
    print('  Criterio: maior reducao de espaco mantendo a meta de retencao do nivel.')
    metas = [(1, 95, 'Conservador'), (2, 85, 'Basico'), (3, 80, 'Balanceado'),
             (4, 70, 'Agressivo'), (5, 60, 'Muito agressivo'), (6, 50, 'Extremo')]
    for cov in COBERTURAS:
        chave = f'v{int(cov * 100)}'
        viol = np.array([c[chave] for c in concursos_avaliados])
        print(f'\n  --- Cobertura {int(cov * 100)}% ---')
        print(f'  {"Nivel":<7}{"Meta retencao":>14}{"Tol sugerida":>14}{"Retencao":>10}')
        for nivel, meta, nome in metas:
            escolhido = None
            for tol in range(0, 6):
                if float(np.mean(viol <= tol)) * 100 >= meta:
                    escolhido = tol
                    break
            if escolhido is None:
                escolhido = 5
            retencao = float(np.mean(viol <= escolhido)) * 100
            print(f'  {nivel} {nome:<13}{meta:>6}%{escolhido:>13}{retencao:>9.1f}%')

    separador('RESUMO')
    print('  Se retencao real < binomial: violacoes sao correlacionadas (soma/distribuicao')
    print('  conjunta) -> tolerancias devem ser calibradas pela retencao REAL, nao teorica.')


if __name__ == '__main__':
    main()
