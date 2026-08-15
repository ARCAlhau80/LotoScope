# -*- coding: utf-8 -*-
"""
HIPOTESE: AMPLITUDE POSICIONAL LIMITADA E PREVISIVEL (janelas de 30 concursos)
===============================================================================
Hipotese: os numeros sorteados em cada posicao variam com distancia limitada
em torno do numero previsto. A amplitude tende a ser MAIOR nas posicoes
iniciais (N1, N2) e MENOR nas posicoes finais (N14, N15).

Metodo:
  1. Varrer a base historica em janelas de 30 concursos (nao sobrepostas).
  2. Para cada janela, gerar a previsao usando apenas o historico ANTERIOR:
     - Previsao Poisson (top-1 lambda_blend por posicao = "Previsao para o
       Proximo Sorteio")
     - Previsao Combinada (espelho do gerarPrevisaoCombinada do dashboard:
       Poisson + exclusao por score invertido + bias de soma + unicidade)
     - Baseline persistencia: numero real do concurso anterior na posicao
  3. Avaliar nos 30 concursos da janela, para cada posicao:
     - Taxa de acerto exato (previsto == real)
     - Amplitude media = media(|real - previsto|) e desvio medio signed
     - Bandas de confianca empiricas 60% e 90% (menor intervalo de desvio
       que cobre X% dos casos) -> ex.: "previu 1 -> 60% entre 1 e 7"
  4. Verificar se a amplitude decresce com a posicao (correlacao).

Uso:
  python hipotese_amplitude_posicional_janelas30.py
"""

import math
from collections import Counter, defaultdict

import numpy as np
import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
POSICOES = [f'N{i}' for i in range(1, 16)]
NUMEROS = list(range(1, 26))
TAM_JANELA = 30
WINDOW_LAMBDA = 50
ALPHA = 0.6
COBERTURAS = (0.60, 0.90)


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


def previsao_combinada(resultados, dados):
    """Espelho de gerarPrevisaoCombinada (dashboard/src/lib/analise-completa.ts)."""
    total = len(resultados)
    freq5 = Counter(n for r in resultados[-5:] for n in r['numeros'])
    freq15 = Counter(n for r in resultados[-15:] for n in r['numeros'])
    freq30 = Counter(n for r in resultados[-30:] for n in r['numeros'])

    ultimo = resultados[-1]['numeros']
    penultimo = resultados[-2]['numeros'] if total > 1 else []
    antepenultimo = resultados[-3]['numeros'] if total > 2 else []
    rep_ultimo = set(penultimo) & set(ultimo)
    rep_cadeia = set(antepenultimo) & set(penultimo) & set(ultimo)

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
        elif consec >= 3 and f5 >= 80:
            score += 4
        elif consec >= 3:
            score += 3
        elif f5 >= 100:
            score += 4
        elif f5 >= 80:
            score += 3

        j5q, j15q, j30q = f5 >= 70, fm >= 70, f30 >= 70
        j5f, j30f = f5 < 50, f30 < 50
        if j5q and j15q and j30q:
            score += 2
        elif j5q and not j30q:
            score -= 2
        elif not j5q and j30q:
            score += 3
        elif j5f and j30f:
            score -= 1

        diff = freq30.get(n, 0) - 18.0
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
        return (n - 13) * (direcao / 30)

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
        if len(por_posicao) >= 15:
            break
        pos_vaga = next(p for p in POSICOES if p not in por_posicao)
        por_posicao[pos_vaga] = n
        usados.add(n)

    conjunto = sorted(por_posicao.values())
    return {POSICOES[i]: conjunto[i] for i in range(15)}


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
    desvios = {m: {p: [] for p in POSICOES} for m in ('poisson', 'combinada', 'persistencia')}
    por_previsto = {m: {p: defaultdict(list) for p in POSICOES} for m in ('poisson', 'combinada')}
    janelas = 0

    for w0 in range(0, total, TAM_JANELA):
        fim = min(w0 + TAM_JANELA, total)
        if w0 < 60 or fim - w0 < TAM_JANELA // 2:
            continue
        janelas += 1

        historico = resultados[:w0]
        dados = calcular_lambdas(build_matriz_ocorrencias(historico), len(historico))
        prev_poisson = previsao_poisson(dados)
        prev_combinada = previsao_combinada(historico, dados)

        for idx in range(w0, fim):
            real = resultados[idx]['numeros']
            anterior = resultados[idx - 1]['numeros']
            for pi, pos in enumerate(POSICOES):
                r = real[pi]
                desvios['poisson'][pos].append(r - prev_poisson[pos])
                desvios['combinada'][pos].append(r - prev_combinada[pos])
                desvios['persistencia'][pos].append(r - anterior[pi])
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
    print('HIPOTESE: AMPLITUDE POSICIONAL LIMITADA (janelas de 30 concursos)')
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
                           ('persistencia', 'BASELINE (concurso anterior)')):
        print(f'\n  --- Metodo: {rotulo} ---')
        print(f'  {"Pos":<5}{"Acerto%":>9}{"Amp.med":>9}{"Desvio":>8}'
              f'{"B60":>13}{"B90":>13}{"Larg60":>8}{"Larg90":>8}')
        for pos in POSICOES:
            r = resumir_posicao(desvios[metodo][pos])
            b60, b90 = r['b60'], r['b90']
            print(f'  {pos:<5}{r["acerto_pct"]:>9.1f}{r["amp_media"]:>9.2f}{r["desvio_medio"]:>+8.2f}'
                  f'{f"[{b60[0]:+d},{b60[1]:+d}]":>13}{f"[{b90[0]:+d},{b90[1]:+d}]":>13}'
                  f'{b60[1] - b60[0]:>8d}{b90[1] - b90[0]:>8d}')

    separador('BLOCO 2 - VERIFICACAO DA HIPOTESE: AMPLITUDE DECRESCENTE POR POSICAO')
    for metodo, rotulo in (('poisson', 'POISSON'), ('combinada', 'COMBINADA')):
        amps = [resumir_posicao(desvios[metodo][pos])['amp_media'] for pos in POSICOES]
        corr = np.corrcoef(range(15), amps)[0, 1]
        print(f'\n  {rotulo}:')
        print('  ' + '  '.join(f'{pos}:{a:.2f}' for pos, a in zip(POSICOES, amps)))
        monotona = all(amps[i] >= amps[i + 1] - 0.05 for i in range(14))
        n1n2 = np.mean(amps[:2])
        n14n15 = np.mean(amps[-2:])
        print(f'  Correlacao posicao x amplitude : {corr:+.3f} '
              f'({"decrescente" if corr < -0.5 else "fraca/nula"})')
        print(f'  Media N1-N2 = {n1n2:.2f} | Media N14-N15 = {n14n15:.2f} | '
              f'razao = {n1n2 / n14n15 if n14n15 else float("inf"):.2f}x')
        print(f'  Hipotese "amplitude decresce com a posicao": '
              f'{"CONFIRMADA" if corr < -0.5 and n1n2 > n14n15 else "NAO CONFIRMADA"}')

    separador('BLOCO 3 - ESTATISTICA CONDICIONAL POR VALOR PREVISTO (top previsoes)')
    print('  Quando o sistema preve X nesta posicao: quantas vezes saiu X,')
    print('  qual amplitude media e as bandas 60%/90% (X + desvio).')
    for metodo, rotulo in (('poisson', 'POISSON'), ('combinada', 'COMBINADA')):
        print(f'\n  --- Metodo: {rotulo} ---')
        for pos in POSICOES:
            grupos = por_previsto[metodo][pos]
            top = sorted(grupos.items(), key=lambda kv: -len(kv[1]))[:3]
            partes = []
            for prev, reals in top:
                arr = np.array(reals)
                d = (arr - prev).tolist()
                b60 = banda_minima(d, 0.60)
                b90 = banda_minima(d, 0.90)
                acerto = int(np.sum(arr == prev))
                partes.append(
                    f'prev={prev:2d}: n={len(arr):4d} acerto={acerto / len(arr) * 100:5.1f}% '
                    f'amp={np.mean(np.abs(arr - prev)):.2f} '
                    f'60%[{prev + b60[0]:2d}..{prev + b60[1]:2d}] '
                    f'90%[{prev + b90[0]:2d}..{prev + b90[1]:2d}]'
                )
            print(f'  {pos}: ' + ' | '.join(partes))

    separador('BLOCO 4 - PREVISAO ATUAL PARA O PROXIMO SORTEIO COM BANDAS')
    dados = calcular_lambdas(build_matriz_ocorrencias(resultados), len(resultados))
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
                           f'[{prev + b60[0]:2d}..{prev + b60[1]:2d}]',
                           f'[{prev + b90[0]:2d}..{prev + b90[1]:2d}]'))
        (p1, p60, p90), (c1, c60, c90) = linhas
        print(f'  {pos:<5}{p1:>8}{p60:>15}{p90:>15}{c1:>10}{c60:>15}{c90:>15}')

    separador('RESUMO EXECUTIVO')
    amps_p = [resumir_posicao(desvios['poisson'][p])['amp_media'] for p in POSICOES]
    amps_c = [resumir_posicao(desvios['combinada'][p])['amp_media'] for p in POSICOES]
    amps_b = [resumir_posicao(desvios['persistencia'][p])['amp_media'] for p in POSICOES]
    print(f'  Amplitude media global: Poisson={np.mean(amps_p):.2f} | '
          f'Combinada={np.mean(amps_c):.2f} | Baseline={np.mean(amps_b):.2f}')
    print(f'  N1/N2 (Poisson): {np.mean(amps_p[:2]):.2f} | N14/N15: {np.mean(amps_p[-2:]):.2f}')
    print('  Interpretacao: banda 60% = faixa onde o real cai em ~60% dos casos;')
    print('  banda 90% = faixa de seguranca. Quanto menor a largura, mais')
    print('  "limitada" e a variacao da posicao em torno do previsto.')


if __name__ == '__main__':
    main()
