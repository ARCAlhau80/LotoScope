# -*- coding: utf-8 -*-
"""
HIPOTESE: AMPLITUDE POSICIONAL LIMITADA E PREVISIVEL - MEGA-SENA
=================================================================
Versao Mega-Sena (6 dezenas de 1..60) do backtest de janelas de 30 concursos.
Fonte: Resultados_MegaSenaFechado (mesmo banco da Lotofacil).

Diferencas para a versao Lotofacil:
  - POSICOES = N1..N6, NUMEROS = 1..60
  - Previsao Combinada com thresholds de "calor" reescalados pela taxa de
    inclusao do jogo (p = 6/60 = 0.10 vs 15/25 = 0.60 da Lotofacil),
    preservando a semantica de quente/frio relativa
  - Frequencia esperada por numero em 30 concursos = 30*6/60 = 3.0
  - Baselines: persistencia (concurso anterior) e modo historico da posicao

Uso:
  python hipotese_amplitude_posicional_megasena.py
"""

import math
from collections import Counter, defaultdict

import numpy as np
import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
TABELA = 'Resultados_MegaSenaFechado'
POSICOES = [f'N{i}' for i in range(1, 7)]
NUMEROS = list(range(1, 61))
NUM_POR_JOGO = 6
TAM_JANELA = 30
WINDOW_LAMBDA = 50
ALPHA = 0.6
COBERTURAS = (0.60, 0.90)
CENTRO = (1 + 60) / 2
FREQ_ESPERADA_30 = TAM_JANELA * NUM_POR_JOGO / len(NUMEROS)
ESCALA_CALOR = (NUM_POR_JOGO / len(NUMEROS)) / 0.6


def carregar_resultados():
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT Concurso, N1,N2,N3,N4,N5,N6 '
            f'FROM {TABELA} ORDER BY Concurso ASC'
        )
        return [
            {'concurso': row[0], 'numeros': [int(x) for x in row[1:7]]}
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
            if WINDOW_LAMBDA > 0 and total_draws >= WINDOW_LAMBDA:
                cutoff = total_draws - WINDOW_LAMBDA
                count_recent = sum(1 for i in occ if i >= cutoff)
                lambda_recent = count_recent / WINDOW_LAMBDA
            else:
                lambda_recent = 0.0
            dados[pos][num] = ALPHA * lambda_hist + (1 - ALPHA) * lambda_recent
    return dados


def previsao_poisson(dados):
    """Top-1 por posicao (= palpite 'Previsao para o Proximo Sorteio')."""
    return {
        pos: max(NUMEROS, key=lambda n: (dados[pos][n], -n))
        for pos in POSICOES
    }


def previsao_modo(ocorrencias):
    """Baseline: numero mais frequente da posicao em todo o historico."""
    return {
        pos: max(NUMEROS, key=lambda n: (len(ocorrencias[pos][n]), -n))
        for pos in POSICOES
    }


def previsao_combinada(resultados, dados):
    """Espelho de gerarPrevisaoCombinada, com calor reescalado para 6/60."""
    total = len(resultados)
    freq5 = Counter(n for r in resultados[-5:] for n in r['numeros'])
    freq15 = Counter(n for r in resultados[-15:] for n in r['numeros'])
    freq30 = Counter(n for r in resultados[-30:] for n in r['numeros'])

    ultimo = resultados[-1]['numeros']
    penultimo = resultados[-2]['numeros'] if total > 1 else []
    antepenultimo = resultados[-3]['numeros'] if total > 2 else []
    rep_ultimo = set(penultimo) & set(ultimo)
    rep_cadeia = set(antepenultimo) & set(penultimo) & set(ultimo)

    t_quente, t_muito_quente, t_sempre = 70 * ESCALA_CALOR, 80 * ESCALA_CALOR, 100 * ESCALA_CALOR
    t_frio = 50 * ESCALA_CALOR

    scores = {}
    for n in NUMEROS:
        f5 = freq5.get(n, 0) / 5 * 100
        fm = freq15.get(n, 0) / 15 * 100
        f30 = freq30.get(n, 0) / 30 * 100
        consec = 0
        for r in reversed(resultados[-15:]):
            if n in r['numeros']:
                consec += 1
            else:
                break
        score = 0
        if consec >= 10:
            score -= 5
        elif consec >= 5:
            score += 6
        elif consec >= 4:
            score += 5
        elif consec >= 3 and f5 >= t_muito_quente:
            score += 4
        elif consec >= 3:
            score += 3
        elif f5 >= t_sempre:
            score += 4
        elif f5 >= t_muito_quente:
            score += 3

        j5q, j15q, j30q = f5 >= t_quente, fm >= t_quente, f30 >= t_quente
        j5f, j30f = f5 < t_frio, f30 < t_frio
        if j5q and j15q and j30q:
            score += 2
        elif j5q and not j30q:
            score -= 2
        elif not j5q and j30q:
            score += 3
        elif j5f and j30f:
            score -= 1

        diff = freq30.get(n, 0) - FREQ_ESPERADA_30
        if diff > 1.5:
            score += 1.5
        elif diff < -1.5:
            score -= 1

        if n in rep_cadeia:
            score -= 8
        elif n in rep_ultimo:
            score -= 3
        scores[n] = score

    excluir = {n for n, _ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:2]}
    pool = [n for n in NUMEROS if n not in excluir]

    somas10 = [sum(r['numeros']) for r in resultados[-10:]]
    media_soma_recente = sum(somas10) / len(somas10)
    soma_hist = sum(sum(r['numeros']) for r in resultados) / total
    soma_target = round((media_soma_recente + soma_hist) / 2)
    direcao = soma_target - soma_hist

    def bias(n):
        return (n - CENTRO) * (direcao / 30)

    usados = set()
    por_posicao = {}
    for pos in POSICOES:
        top3 = sorted(NUMEROS, key=lambda n: -dados[pos][n])[:3]
        candidatos = [n for n in top3 if n in pool and n not in usados]
        candidatos.sort(key=lambda n: -(dados[pos][n] + bias(n)))
        if candidatos:
            por_posicao[pos] = candidatos[0]
            usados.add(candidatos[0])

    agg = {n: sum(dados[pos][n] for pos in POSICOES) for n in NUMEROS}
    restantes = sorted(
        (n for n in pool if n not in usados),
        key=lambda n: -(agg[n] + bias(n))
    )
    for n in restantes:
        if len(por_posicao) >= len(POSICOES):
            break
        pos_vaga = next(p for p in POSICOES if p not in por_posicao)
        por_posicao[pos_vaga] = n
        usados.add(n)

    conjunto = sorted(por_posicao.values())
    return {POSICOES[i]: conjunto[i] for i in range(len(POSICOES))}


def banda_minima(desvios, cobertura):
    """Menor intervalo [a, b] de desvios que cobre >= cobertura dos casos."""
    if not desvios:
        return None, None
    s = sorted(desvios)
    n = len(s)
    k = max(1, math.ceil(cobertura * n))
    melhor = None
    for i in range(n - k + 1):
        largura = s[i + k - 1] - s[i]
        if melhor is None or largura < melhor[1] - melhor[0]:
            melhor = (s[i], s[i + k - 1])
    return melhor


def backtest(resultados):
    total = len(resultados)
    metodos = ('poisson', 'combinada', 'persistencia', 'modo')
    desvios = {m: {p: [] for p in POSICOES} for m in metodos}
    por_previsto = {m: {p: defaultdict(list) for p in POSICOES} for m in ('poisson', 'combinada')}
    janelas = 0

    for w0 in range(0, total, TAM_JANELA):
        fim = min(w0 + TAM_JANELA, total)
        if w0 < 60 or fim - w0 < TAM_JANELA // 2:
            continue
        janelas += 1

        historico = resultados[:w0]
        ocorrencias = build_matriz_ocorrencias(historico)
        dados = calcular_lambdas(ocorrencias, len(historico))
        prev_poisson = previsao_poisson(dados)
        prev_combinada = previsao_combinada(historico, dados)
        prev_modo = previsao_modo(ocorrencias)

        for idx in range(w0, fim):
            real = resultados[idx]['numeros']
            anterior = resultados[idx - 1]['numeros']
            for pi, pos in enumerate(POSICOES):
                r = real[pi]
                desvios['poisson'][pos].append(r - prev_poisson[pos])
                desvios['combinada'][pos].append(r - prev_combinada[pos])
                desvios['persistencia'][pos].append(r - anterior[pi])
                desvios['modo'][pos].append(r - prev_modo[pos])
                por_previsto['poisson'][pos][prev_poisson[pos]].append(r)
                por_previsto['combinada'][pos][prev_combinada[pos]].append(r)

    return desvios, por_previsto, janelas


def resumir_posicao(desv):
    d = np.array(desv)
    acerto = int(np.sum(d == 0))
    out = {
        'n': len(d),
        'acerto_pct': acerto / len(d) * 100,
        'amp_media': float(np.mean(np.abs(d))),
        'desvio_medio': float(np.mean(d)),
    }
    for cov in COBERTURAS:
        lo, hi = banda_minima(d.tolist(), cov)
        out[f'b{int(cov * 100)}'] = (lo, hi)
    return out


def separador(titulo):
    print(f"\n{'=' * 90}")
    print(f"  {titulo}")
    print('=' * 90)


def main():
    print('HIPOTESE: AMPLITUDE POSICIONAL LIMITADA - MEGA-SENA (janelas de 30)')
    print('Carregando resultados...')
    resultados = carregar_resultados()
    print(f'  {len(resultados)} concursos ({resultados[0]["concurso"]} a {resultados[-1]["concurso"]})')

    print('Executando backtest em janelas de 30...')
    desvios, por_previsto, janelas = backtest(resultados)

    separador(f'BLOCO 1 - BACKTEST POR POSICAO ({janelas} janelas x {TAM_JANELA} concursos)')
    print('  Acerto%  = real == previsto | Amp media = |real - previsto|')
    print('  Banda 60/90 = menor intervalo de desvio que cobre X% dos casos (previsto + [lo,hi])')
    for metodo, rotulo in (('poisson', 'POISSON (top-1)'),
                           ('combinada', 'COMBINADA'),
                           ('persistencia', 'BASELINE (concurso anterior)'),
                           ('modo', 'BASELINE (modo historico)')):
        print(f'\n  --- Metodo: {rotulo} ---')
        print(f'  {"Pos":<5}{"Acerto%":>9}{"Amp.med":>9}{"Desvio":>8}'
              f'{"B60":>15}{"B90":>15}{"Larg60":>8}{"Larg90":>8}')
        for pos in POSICOES:
            r = resumir_posicao(desvios[metodo][pos])
            b60, b90 = r['b60'], r['b90']
            print(f'  {pos:<5}{r["acerto_pct"]:>9.1f}{r["amp_media"]:>9.2f}{r["desvio_medio"]:>+8.2f}'
                  f'{f"[{b60[0]:+d},{b60[1]:+d}]":>15}{f"[{b90[0]:+d},{b90[1]:+d}]":>15}'
                  f'{b60[1] - b60[0]:>8d}{b90[1] - b90[0]:>8d}')

    separador('BLOCO 2 - VERIFICACAO DA HIPOTESE: AMPLITUDE DECRESCENTE POR POSICAO')
    for metodo, rotulo in (('poisson', 'POISSON'), ('combinada', 'COMBINADA')):
        amps = [resumir_posicao(desvios[metodo][pos])['amp_media'] for pos in POSICOES]
        corr = np.corrcoef(range(len(POSICOES)), amps)[0, 1]
        print(f'\n  {rotulo}:')
        print('  ' + '  '.join(f'{pos}:{a:.2f}' for pos, a in zip(POSICOES, amps)))
        primeira = np.mean(amps[:2])
        ultima = np.mean(amps[-2:])
        print(f'  Correlacao posicao x amplitude : {corr:+.3f}')
        print(f'  Media N1-N2 = {primeira:.2f} | Media N5-N6 = {ultima:.2f} | '
              f'razao = {primeira / ultima if ultima else float("inf"):.2f}x')
        print(f'  Hipotese "amplitude decresce com a posicao": '
              f'{"CONFIRMADA" if corr < -0.5 and primeira > ultima else "NAO CONFIRMADA"}')

    separador('BLOCO 3 - ESTATISTICA CONDICIONAL POR VALOR PREVISTO (top previsoes)')
    print('  Quando o sistema preve X nesta posicao: quantas vezes saiu X,')
    print('  qual amplitude media e as bandas 60%/90% (X + desvio).')
    for metodo, rotulo in (('poisson', 'POISSON'), ('combinada', 'COMBINADA')):
        print(f'\n  --- Metodo: {rotulo} ---')
        for pos in POSICOES:
            grupos = por_previsto[metodo][pos]
            top = sorted(grupos.items(), key=lambda kv: -len(kv[1]))[:3]
            print(f'  {pos}:')
            for prev, reals in top:
                arr = np.array(reals)
                d = (arr - prev).tolist()
                b60 = banda_minima(d, 0.60)
                b90 = banda_minima(d, 0.90)
                acerto = int(np.sum(arr == prev))
                print(f'      prev={prev:2d}: n={len(arr):4d} acerto={acerto / len(arr) * 100:5.1f}% '
                      f'amp={np.mean(np.abs(arr - prev)):.2f} '
                      f'60%[{prev + b60[0]:2d}..{prev + b60[1]:2d}] '
                      f'90%[{prev + b90[0]:2d}..{prev + b90[1]:2d}]')

    separador('BLOCO 4 - PODER DE FILTRO: BANDA 90% vs FAIXA REAL DA POSICAO')
    print('  Quantas dezenas a banda 90% elimina da faixa observada da posicao?')
    for pos in POSICOES:
        valores = [r['numeros'][POSICOES.index(pos)] for r in resultados]
        faixa = max(valores) - min(valores) + 1
        larg90 = resumir_posicao(desvios['poisson'][pos])['b90']
        larg90 = larg90[1] - larg90[0] + 1
        print(f'  {pos}: faixa real={faixa:2d} dezenas | banda90={larg90:2d} | '
              f'reducao={100 * (1 - larg90 / faixa):.0f}% do espaco eliminado')

    separador('BLOCO 5 - PREVISAO ATUAL PARA O PROXIMO SORTEIO COM BANDAS')
    ocorrencias = build_matriz_ocorrencias(resultados)
    dados = calcular_lambdas(ocorrencias, len(resultados))
    prev_poisson = previsao_poisson(dados)
    prev_combinada = previsao_combinada(resultados, dados)
    print(f'  Previsao Poisson  : {[prev_poisson[p] for p in POSICOES]}')
    print(f'  Previsao Combinada: {[prev_combinada[p] for p in POSICOES]}')
    print('\n  Bandas empiricas (backtest) aplicadas a previsao atual:')
    print(f'  {"Pos":<5}{"Poisson":>8}{"60%":>15}{"90%":>15}{"Combinada":>10}{"60%":>15}{"90%":>15}')
    for pos in POSICOES:
        linhas = []
        for metodo, prev in (('poisson', prev_poisson[pos]), ('combinada', prev_combinada[pos])):
            r = resumir_posicao(desvios[metodo][pos])
            b60, b90 = r['b60'], r['b90']
            linhas.append((prev,
                           f'[{max(1, prev + b60[0]):2d}..{min(60, prev + b60[1]):2d}]',
                           f'[{max(1, prev + b90[0]):2d}..{min(60, prev + b90[1]):2d}]'))
        (p1, p60, p90), (c1, c60, c90) = linhas
        print(f'  {pos:<5}{p1:>8}{p60:>15}{p90:>15}{c1:>10}{c60:>15}{c90:>15}')

    separador('RESUMO EXECUTIVO')
    amps_p = [resumir_posicao(desvios['poisson'][p])['amp_media'] for p in POSICOES]
    amps_c = [resumir_posicao(desvios['combinada'][p])['amp_media'] for p in POSICOES]
    amps_b = [resumir_posicao(desvios['persistencia'][p])['amp_media'] for p in POSICOES]
    amps_m = [resumir_posicao(desvios['modo'][p])['amp_media'] for p in POSICOES]
    print(f'  Amplitude media global: Poisson={np.mean(amps_p):.2f} | Combinada={np.mean(amps_c):.2f} | '
          f'Persistencia={np.mean(amps_b):.2f} | Modo={np.mean(amps_m):.2f}')
    acertos_p = np.mean([resumir_posicao(desvios['poisson'][p])['acerto_pct'] for p in POSICOES])
    acertos_m = np.mean([resumir_posicao(desvios['modo'][p])['acerto_pct'] for p in POSICOES])
    print(f'  Acerto exato medio: Poisson={acertos_p:.1f}% | Modo historico={acertos_m:.1f}%')
    print('  Nota: se Poisson ~ Modo historico, o "sinal" e apenas a distribuicao')
    print('  marginal da posicao (frequencia estatica), sem ganho temporal.')


if __name__ == '__main__':
    main()
