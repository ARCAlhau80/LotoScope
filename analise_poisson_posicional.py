# -*- coding: utf-8 -*-
"""
analise_poisson_posicional - Modelagem Poisson para previsao posicional

Para cada posicao (N1..N15) e cada numero (1..25), calcula:
  - lambda_hist   = taxa historica total (ocorrencias / total sorteios)
  - lambda_recent = taxa na janela recente (ocorrencias / tam_janela)
  - lambda_blend  = alpha * lambda_hist + (1-alpha) * lambda_recent
  - gap atual = sorteios desde ultima ocorrencia na posicao
  - gap esperado = 1 / lambda_blend
  - P(proximo) = lambda_blend
  - P(gap >= atual) = e^(-lambda * gap) -> se < 5%, numero atrasado
"""

import sys
from collections import defaultdict
import pyodbc
import numpy as np

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
POSICOES = [f'N{i}' for i in range(1, 16)]
NUMEROS = list(range(1, 26))
DEFAULT_WINDOW = 50
DEFAULT_ALPHA = 0.6
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}


def carregar_resultados():
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 '
            'FROM Resultados_INT ORDER BY Concurso ASC'
        )
        return [
            {'concurso': row[0], 'numeros': list(int(x) for x in row[1:16])}
            for row in cursor.fetchall()
        ]


def build_matriz_ocorrencias(resultados):
    ocorrencias = {p: defaultdict(list) for p in POSICOES}
    for idx, r in enumerate(resultados):
        for pos_idx, pos in enumerate(POSICOES):
            num = r['numeros'][pos_idx]
            ocorrencias[pos][num].append(idx)
    return ocorrencias


def calcular_lambdas(ocorrencias, total_draws, window=DEFAULT_WINDOW):
    dados = {}
    for pos in POSICOES:
        dados[pos] = {}
        for num in NUMEROS:
            occ = ocorrencias[pos][num]
            count_hist = len(occ)
            lambda_hist = count_hist / total_draws if total_draws > 0 else 0.0

            if window > 0 and total_draws >= window:
                cutoff = total_draws - window
                occ_recent = [i for i in occ if i >= cutoff]
                count_recent = len(occ_recent)
                lambda_recent = count_recent / window
            else:
                count_recent = 0
                lambda_recent = 0.0

            lambda_blend = DEFAULT_ALPHA * lambda_hist + (1 - DEFAULT_ALPHA) * lambda_recent

            ultimo_idx = max(occ) if occ else None
            gap = (total_draws - 1 - ultimo_idx) if ultimo_idx is not None else total_draws

            dados[pos][num] = {
                'lambda_hist': lambda_hist,
                'lambda_recent': lambda_recent,
                'lambda_blend': lambda_blend,
                'count_hist': count_hist,
                'count_recent': count_recent,
                'ultimo_idx': ultimo_idx,
                'gap': gap,
            }
    return dados


def prob_gap_atual(lambda_val, gap):
    return np.exp(-lambda_val * gap) if lambda_val > 0 else 1.0


def analisar_posicao(pos, resultados, dados, top_n=5):
    total = len(resultados)
    nums = dados[pos]
    linhas = []

    for num, info in nums.items():
        p_proximo = info['lambda_blend']
        p_gap = prob_gap_atual(info['lambda_blend'], info['gap'])
        linhas.append({
            'numero': num,
            'lambda_hist': info['lambda_hist'],
            'lambda_recent': info['lambda_recent'],
            'lambda_blend': info['lambda_blend'],
            'p_proximo': p_proximo,
            'p_gap': p_gap,
            'gap': info['gap'],
            'gap_esperado': 1.0 / info['lambda_blend'] if info['lambda_blend'] > 0 else float('inf'),
            'count_hist': info['count_hist'],
            'count_recent': info['count_recent'],
            'atrasado': p_gap < 0.05,
        })

    por_prob = sorted(linhas, key=lambda x: -x['p_proximo'])
    por_atraso = sorted(linhas, key=lambda x: x['p_gap'])
    por_gap = sorted(linhas, key=lambda x: -x['gap'])

    ultimos = []
    for idx in range(total - 1, max(total - 11, -1), -1):
        num = resultados[idx]['numeros'][POSICOES.index(pos)]
        ultimos.append({'concurso': resultados[idx]['concurso'], 'numero': num})

    return {
        'posicao': pos,
        'top_prob': por_prob[:top_n],
        'bottom_prob': por_prob[-top_n:],
        'top_atraso': por_atraso[:top_n],
        'top_gap': por_gap[:top_n],
        'ultimos_10': ultimos,
        'qtd_atrasados': sum(1 for l in linhas if l['atrasado']),
    }


def resumo_geral(resultados, dados, top_n=5):
    total = len(resultados)
    saida = []
    saida.append('=' * 80)
    saida.append('  ANALISE POISSON POSICIONAL')
    saida.append(f'  Total de sorteios: {total}')
    saida.append(f'  Janela recente: {DEFAULT_WINDOW}  |  alpha (peso historico): {DEFAULT_ALPHA}')
    saida.append('=' * 80)

    tabela_geral = []
    cabecalhos = ['Pos', 'Num', 'L_hist', 'L_rec', 'L_blend', 'P(prox)', 'Gap', 'Gap_esp', 'P(gap)', 'Atras?']

    for pos in POSICOES:
        analise = analisar_posicao(pos, resultados, dados, top_n)
        saida.append('')
        saida.append('-' * 80)
        ultimos_str = ' | '.join(f'#{u["concurso"]}:{u["numero"]}' for u in analise['ultimos_10'])
        saida.append(f'  >> {pos} - Ultimos 10: {ultimos_str}')
        saida.append(f'     Atrasados: {analise["qtd_atrasados"]} numeros')
        saida.append(f'     Top {top_n} mais provaveis:')
        for item in analise['top_prob']:
            atr = '*' if item['atrasado'] else ' '
            saida.append(f'       N{item["numero"]:>2}  '
                         f'Lh={item["lambda_hist"]:.4f}  '
                         f'Lr={item["lambda_recent"]:.4f}  '
                         f'Lb={item["lambda_blend"]:.4f}  '
                         f'P={item["p_proximo"]:.4f}  '
                         f'gap={item["gap"]:>3}  '
                         f'exp={item["gap_esperado"]:>5.1f}  '
                         f'P(gap)={item["p_gap"]:.3f} {atr}')
        saida.append(f'     Top {top_n} menos provaveis:')
        for item in analise['bottom_prob']:
            saida.append(f'       N{item["numero"]:>2}  '
                         f'Lb={item["lambda_blend"]:.4f}  '
                         f'P={item["p_proximo"]:.4f}  '
                         f'gap={item["gap"]:>3}')
        saida.append('     Mais atrasados (P(gap) menor):')
        for item in analise['top_atraso'][:3]:
            saida.append(f'       N{item["numero"]:>2}  '
                         f'P(gap)={item["p_gap"]:.4f}  '
                         f'gap={item["gap"]:>3}  '
                         f'Lb={item["lambda_blend"]:.4f}  '
                         f'P(prox)={item["p_proximo"]:.4f}')

        for item in analise['top_prob'][:3]:
            tabela_geral.append([
                pos, item['numero'],
                f'{item["lambda_hist"]:.4f}',
                f'{item["lambda_recent"]:.4f}',
                f'{item["lambda_blend"]:.4f}',
                f'{item["p_proximo"]:.4f}',
                item['gap'],
                f'{item["gap_esperado"]:.1f}',
                f'{item["p_gap"]:.3f}',
                '*' if item['atrasado'] else ''
            ])

    saida.append('')
    saida.append('=' * 80)
    saida.append('  RESUMO - Top 3 mais provaveis por posicao')
    saida.append('=' * 80)
    saida.append('  ' + '|'.join(f'{h:>10}' for h in cabecalhos))
    saida.append('  ' + '-+-' * (len(cabecalhos) - 1) + '-')
    for linha in tabela_geral:
        saida.append('  ' + '|'.join(f'{str(v):>10}' for v in linha))

    return '\n'.join(saida)


def validar_recentes(resultados, dados, ultimos_n=10):
    total = len(resultados)
    n = min(ultimos_n, total)

    saida = []
    saida.append('')
    saida.append('=' * 80)
    saida.append('  VALIDACAO - Acertos do modelo nos ultimos sorteios')
    saida.append('=' * 80)

    total_acertos = 0
    total_previstos = 0

    for offset in range(n):
        idx = total - 1 - offset
        concurso = resultados[idx]['concurso']
        nums_reais = resultados[idx]['numeros']

        # Recria lambdas usando apenas dados ate idx-1 (walk-forward)
        sub_ocorrencias = build_matriz_ocorrencias(resultados[:idx])
        sub_dados = calcular_lambdas(sub_ocorrencias, idx)

        previstos = {}
        for pos_idx, pos in enumerate(POSICOES):
            num_real = nums_reais[pos_idx]
            top3 = sorted(
                [(n, sub_dados[pos][n]['lambda_blend']) for n in NUMEROS],
                key=lambda x: -x[1]
            )[:3]
            previstos[pos] = [n for n, _ in top3]
            if num_real in previstos[pos]:
                total_acertos += 1
            total_previstos += 1

        saida.append(f'  Concurso #{concurso}: numeros reais = {nums_reais}')
        saida.append('    Top-3 previstos por posicao:')
        for pos in POSICOES:
            num_real = nums_reais[POSICOES.index(pos)]
            marcador = '+' if num_real in previstos[pos] else '-'
            saida.append(f'      {pos}: previstos={previstos[pos]}  real={num_real}  {marcador}')

    taxa = total_acertos / total_previstos * 100 if total_previstos > 0 else 0
    saida.append('')
    saida.append(f'  Taxa de acerto (top-3 por posicao): {total_acertos}/{total_previstos} = {taxa:.1f}%')

    return '\n'.join(saida), taxa


def prever_proximo_sorteio(resultados, dados):
    saida = []
    saida.append('')
    saida.append('=' * 80)
    saida.append('  PREVISAO PROXIMO SORTEIO')
    saida.append('=' * 80)

    palpite_completo = []
    for pos in POSICOES:
        nums = dados[pos]
        top3 = sorted(
            [(n, nums[n]['lambda_blend']) for n in NUMEROS if nums[n]['lambda_blend'] > 0],
            key=lambda x: -x[1]
        )[:3]
        top3nums = [n for n, _ in top3]
        
        # Numeros atrasados nesta posicao
        atrasados = [n for n in NUMEROS if nums[n]['gap'] > 0 and prob_gap_atual(nums[n]['lambda_blend'], nums[n]['gap']) < 0.05]
        
        saida.append(f'  {pos}: top 3 = {top3nums}')
        if atrasados:
            saida.append(f'       atrasados (P(gap)<5%): {atrasados}')
        palpite_completo.append(top3nums[0])

    saida.append('')
    saida.append('-' * 80)
    saida.append(f'  Palpite (top-1 de cada posicao): {palpite_completo}')
    saida.append(f'  Soma: {sum(palpite_completo)}')
    saida.append(f'  Pares: {sum(1 for n in palpite_completo if n%2==0)}')
    saida.append(f'  Impares: {sum(1 for n in palpite_completo if n%2==1)}')
    saida.append(f'  Primos: {sum(1 for n in palpite_completo if n in PRIMOS)}')
    saida.append('=' * 80)
    return '\n'.join(saida)


def main():
    print('Carregando resultados do banco...')
    resultados = carregar_resultados()
    print(f'  {len(resultados)} sorteios carregados.')

    print('Construindo matriz de ocorrencias...')
    ocorrencias = build_matriz_ocorrencias(resultados)

    print('Calculando lambdas Poisson...')
    dados = calcular_lambdas(ocorrencias, len(resultados))

    print(resumo_geral(resultados, dados))
    print(prever_proximo_sorteio(resultados, dados))
    val_output, taxa = validar_recentes(resultados, dados, 10)
    print(val_output)

    print(f'\nConcluido. Taxa de acerto global: {taxa:.1f}%')


if __name__ == '__main__':
    main()
