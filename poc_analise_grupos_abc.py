#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import pyodbc
from collections import Counter
from typing import List, Set

A = {2, 5, 6, 8, 11, 13, 17, 20}
B = {3, 7, 9, 12, 14, 18, 19, 21}
C = {4, 10, 15, 16, 22, 23, 24, 25}
ALL_NUMBERS = list(range(1, 26))

CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
)


def conectar():
    return pyodbc.connect(CONN_STR)


def carregar_historico() -> List[Set[int]]:
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 '
            'FROM Resultados_INT ORDER BY Concurso ASC'
        )
        dados = [set(row) for row in cursor.fetchall()]
    return dados


def distribucao_por_grupo(historico: List[Set[int]], grupo: Set[int]):
    contagem = Counter()
    for sorteio in historico:
        contagem[len(grupo & sorteio)] += 1
    return contagem


def resumir_distribuicao(name: str, dist: Counter, total: int) -> str:
    linhas = [f'== {name} ==']
    media = sum(k * v for k, v in dist.items()) / total
    linhas.append(f'Total concursos: {total}')
    linhas.append(f'Média de acertos no grupo: {media:.3f}')
    for k in sorted(dist.keys(), reverse=True):
        linhas.append(f'  {k:>2}: {dist[k]:>5} ({dist[k] / total * 100:6.2f}%)')
    return '\n'.join(linhas)


def gerar_grupos_aleatorios(n_grupos: int = 500, tamanho: int = 8):
    return [set(random.sample(ALL_NUMBERS, tamanho)) for _ in range(n_grupos)]


def avaliar_grupos_aleatorios(historico: List[Set[int]], n_sim: int = 500):
    if n_sim <= 0:
        raise ValueError('n_sim must be positive')
    somas = Counter()
    soma_totais = 0
    for grupo in gerar_grupos_aleatorios(n_sim):
        dist = distribucao_por_grupo(historico, grupo)
        for k, v in dist.items():
            somas[k] += v
        soma_totais += len(historico)
    media_por_k = {k: somas[k] / soma_totais for k in sorted(somas)}
    return {
        'media_acertos': sum(k * media_por_k[k] for k in media_por_k),
        'percentual': media_por_k,
        'total_concursos': soma_totais,
        'simulacoes': n_sim
    }


def top_n_da_janela(janela, n: int = 8):
    freq = Counter()
    for sorteio in janela:
        freq.update(sorteio)
    ordens = sorted(freq.items(), key=lambda item: (-item[1], item[0]))
    return {num for num, _ in ordens[:n]}


def avaliar_melhores_janelas(historico: List[Set[int]], janela_tamanho: int = 10, n_melhores: int = 8):
    dist = Counter()
    if janela_tamanho < 1 or janela_tamanho >= len(historico):
        raise ValueError('janela_tamanho inválido')
    for i in range(janela_tamanho, len(historico)):
        janela = historico[i - janela_tamanho:i]
        melhores = top_n_da_janela(janela, n=n_melhores)
        dist[len(melhores & historico[i])] += 1
    return dist


def imprimir_relatorio(historico: List[Set[int]]):
    total = len(historico)
    print('=== POC ANÁLISE GRUPOS A/B/C ===')
    print('Concursos usados:', total)
    print()

    distA = distribucao_por_grupo(historico, A)
    distB = distribucao_por_grupo(historico, B)
    distC = distribucao_por_grupo(historico, C)

    print(resumir_distribuicao('Grupo A fixo', distA, total))
    print()
    print(resumir_distribuicao('Grupo B fixo', distB, total))
    print()
    print(resumir_distribuicao('Grupo C fixo', distC, total))
    print()

    random_result = avaliar_grupos_aleatorios(historico, n_sim=800)
    print('== Baseline Aleatório ==')
    print(f"Simulações: {random_result['simulacoes']} grupos aleatórios de 8 números")
    print(f"Média de acertos por grupo: {random_result['media_acertos']:.3f}")
    for k, pct in random_result['percentual'].items():
        print(f'  {k:>2}: {pct * 100:6.2f}%')
    print()

    for janela_tamanho in [5, 10, 15, 30]:
        dist_window = avaliar_melhores_janelas(historico, janela_tamanho=janela_tamanho, n_melhores=8)
        total_window = sum(dist_window.values())
        media = sum(k * v for k, v in dist_window.items()) / total_window
        print(f'== Top-8 das janelas anteriores ({janela_tamanho}) ==')
        print(f'Concursos avaliados: {total_window}')
        print(f'Média de acertos no próximo concurso: {media:.3f}')
        for k in sorted(dist_window.keys(), reverse=True):
            print(f'  {k:>2}: {dist_window[k]:>5} ({dist_window[k] / total_window * 100:6.2f}%)')
        print()

    print('=== Comparação de médias de acerto para grupos de 8 números ===')
    print(f'  Fixo A: {sum(k*v for k,v in distA.items()) / total:.3f}')
    print(f'  Fixo B: {sum(k*v for k,v in distB.items()) / total:.3f}')
    print(f'  Fixo C: {sum(k*v for k,v in distC.items()) / total:.3f}')
    print(f'  Aleatório: {random_result['media_acertos']:.3f}')
    for janela_tamanho in [5, 10, 15, 30]:
        dist_window = avaliar_melhores_janelas(historico, janela_tamanho=janela_tamanho, n_melhores=8)
        media = sum(k * v for k, v in dist_window.items()) / sum(dist_window.values())
        print(f'  Top-8 janela {janela_tamanho}: {media:.3f}')


if __name__ == '__main__':
    historico = carregar_historico()
    imprimir_relatorio(historico)
