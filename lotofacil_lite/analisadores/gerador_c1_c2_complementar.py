#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE COMBINAÇÕES C1 E C2 COMPLEMENTARES
==============================================
Gera dois conjuntos de combinações filtradas:
- C1: Prioriza números de COMBO1 (divergentes [1,3,4])
- C2: Prioriza números de COMBO2 (divergentes [15,17,18])

Analisa a complementaridade para hedge perfeito.

Autor: LotoScope AI
Data: Janeiro 2026
"""

import pyodbc
from collections import Counter
from datetime import datetime
from typing import List, Set, Tuple, Dict


# Configurações
COMBO1 = [1,3,4,6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
COMBO2 = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

DIV_C1 = [1, 3, 4]      # Apenas na Combo 1
DIV_C2 = [15, 17, 18]   # Apenas na Combo 2

NUCLEO = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23, 24, 25]

PREMIOS = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}
CUSTO = 3.00

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def carregar_resultados(n: int = 100) -> List[Tuple[int, Set[int]]]:
    """Carrega os últimos N resultados."""
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT TOP {n} Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 
            FROM Resultados_INT 
            ORDER BY Concurso DESC
        ''')
        return [(row.Concurso, set(row[i] for i in range(1,16))) for row in cursor.fetchall()]


def carregar_combinacoes(arquivo: str) -> List[Set[int]]:
    """Carrega combinações de arquivo."""
    combinacoes = []
    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                try:
                    nums = [int(n) for n in linha.split(',')]
                    if len(nums) == 15:
                        combinacoes.append(set(nums))
                except:
                    continue
    return combinacoes


def filtrar_por_tendencia(combinacoes: List[List[int]], 
                          tendencia: str,
                          frequencias: Counter,
                          min_nucleo: int = 13,
                          top_freq_pct: float = 0.20,
                          top_final: int = 1000) -> List[List[int]]:
    """
    Filtra combinações priorizando uma tendência.
    
    tendencia: 'C1' ou 'C2'
    """
    nucleo_set = set(NUCLEO)
    div_c1_set = set(DIV_C1)
    div_c2_set = set(DIV_C2)
    
    print(f'\n   Filtrando para tendência {tendencia}...')
    print(f'   Original: {len(combinacoes):,}')
    
    # Filtro 1: Núcleo mínimo
    filtradas = [c for c in combinacoes if len(set(c) & nucleo_set) >= min_nucleo]
    print(f'   Após núcleo >= {min_nucleo}: {len(filtradas):,}')
    
    # Filtro 2: Priorizar divergentes da tendência
    if tendencia == 'C1':
        # Manter combos que têm MAIS divergentes de C1 que C2
        filtradas_tend = []
        for c in filtradas:
            c_set = set(c)
            div1 = len(c_set & div_c1_set)
            div2 = len(c_set & div_c2_set)
            if div1 >= div2 and div1 >= 1:  # Pelo menos 1 de C1 e mais que C2
                filtradas_tend.append(c)
        filtradas = filtradas_tend
    else:  # C2
        # Manter combos que têm MAIS divergentes de C2 que C1
        filtradas_tend = []
        for c in filtradas:
            c_set = set(c)
            div1 = len(c_set & div_c1_set)
            div2 = len(c_set & div_c2_set)
            if div2 >= div1 and div2 >= 1:  # Pelo menos 1 de C2 e mais que C1
                filtradas_tend.append(c)
        filtradas = filtradas_tend
    
    print(f'   Após filtro tendência {tendencia}: {len(filtradas):,}')
    
    # Filtro 3: Top por frequência
    scores = [(c, sum(frequencias.get(n, 0) for n in c)) for c in filtradas]
    scores.sort(key=lambda x: x[1], reverse=True)
    n_manter = int(len(scores) * top_freq_pct)
    filtradas = [c for c, _ in scores[:n_manter]]
    print(f'   Após top {top_freq_pct*100:.0f}% frequência: {len(filtradas):,}')
    
    # Retornar top N
    return filtradas[:top_final]


def analisar_complementaridade(combos_c1: List[Set[int]], 
                                combos_c2: List[Set[int]], 
                                resultados: List[Tuple[int, Set[int]]]) -> Dict:
    """
    Analisa se C1 e C2 são realmente complementares.
    """
    print('\n' + '=' * 70)
    print('   ANÁLISE DE COMPLEMENTARIDADE C1 vs C2')
    print('=' * 70)
    
    div_c1_set = set(DIV_C1)
    div_c2_set = set(DIV_C2)
    
    stats = []
    
    for concurso, resultado in resultados:
        # Classificar resultado como C1 ou C2 favorável
        div1_no_res = len(resultado & div_c1_set)
        div2_no_res = len(resultado & div_c2_set)
        
        if div1_no_res > div2_no_res:
            favoravel = 'C1'
        elif div2_no_res > div1_no_res:
            favoravel = 'C2'
        else:
            favoravel = 'NEUTRO'
        
        # Calcular acertos de cada conjunto
        acertos_c1 = [len(c & resultado) for c in combos_c1]
        acertos_c2 = [len(c & resultado) for c in combos_c2]
        
        # Prêmios
        premios_c1 = sum(PREMIOS.get(a, 0) for a in acertos_c1 if a >= 11)
        premios_c2 = sum(PREMIOS.get(a, 0) for a in acertos_c2 if a >= 11)
        
        # Custos
        custo_c1 = len(combos_c1) * CUSTO
        custo_c2 = len(combos_c2) * CUSTO
        
        stats.append({
            'concurso': concurso,
            'div1': div1_no_res,
            'div2': div2_no_res,
            'favoravel': favoravel,
            'max_c1': max(acertos_c1),
            'max_c2': max(acertos_c2),
            'premios_11+_c1': sum(1 for a in acertos_c1 if a >= 11),
            'premios_11+_c2': sum(1 for a in acertos_c2 if a >= 11),
            'valor_c1': premios_c1,
            'valor_c2': premios_c2,
            'lucro_c1': premios_c1 - custo_c1,
            'lucro_c2': premios_c2 - custo_c2,
        })
    
    # Exibir últimos 30
    print('\n   Conc    Fav    Div1  Div2   MaxC1  MaxC2   Lucro C1      Lucro C2')
    print('   ' + '-' * 70)
    
    for s in stats[:30]:
        fav_mark = f'[{s["favoravel"]:^6}]'
        print(f'   {s["concurso"]:5}  {fav_mark}  {s["div1"]}/3   {s["div2"]}/3    '
              f'{s["max_c1"]:2}     {s["max_c2"]:2}    R$ {s["lucro_c1"]:>8,.0f}   R$ {s["lucro_c2"]:>8,.0f}')
    
    # Resumo estatístico
    print('\n' + '=' * 70)
    print('   RESUMO ESTATÍSTICO')
    print('=' * 70)
    
    # Por tipo de resultado
    c1_favoraveis = [s for s in stats if s['favoravel'] == 'C1']
    c2_favoraveis = [s for s in stats if s['favoravel'] == 'C2']
    neutros = [s for s in stats if s['favoravel'] == 'NEUTRO']
    
    print(f'\n   Concursos favoráveis C1: {len(c1_favoraveis)} ({len(c1_favoraveis)*100/len(stats):.1f}%)')
    print(f'   Concursos favoráveis C2: {len(c2_favoraveis)} ({len(c2_favoraveis)*100/len(stats):.1f}%)')
    print(f'   Concursos neutros:       {len(neutros)} ({len(neutros)*100/len(stats):.1f}%)')
    
    # Lucro por cenário
    print('\n   LUCRO QUANDO FAVORÁVEL:')
    if c1_favoraveis:
        lucro_c1_em_c1 = sum(s['lucro_c1'] for s in c1_favoraveis)
        lucro_c2_em_c1 = sum(s['lucro_c2'] for s in c1_favoraveis)
        print(f'   Quando C1 favorável: C1 lucra R$ {lucro_c1_em_c1:>12,.2f} | C2 lucra R$ {lucro_c2_em_c1:>12,.2f}')
    
    if c2_favoraveis:
        lucro_c1_em_c2 = sum(s['lucro_c1'] for s in c2_favoraveis)
        lucro_c2_em_c2 = sum(s['lucro_c2'] for s in c2_favoraveis)
        print(f'   Quando C2 favorável: C1 lucra R$ {lucro_c1_em_c2:>12,.2f} | C2 lucra R$ {lucro_c2_em_c2:>12,.2f}')
    
    if neutros:
        lucro_c1_neutro = sum(s['lucro_c1'] for s in neutros)
        lucro_c2_neutro = sum(s['lucro_c2'] for s in neutros)
        print(f'   Quando neutro:       C1 lucra R$ {lucro_c1_neutro:>12,.2f} | C2 lucra R$ {lucro_c2_neutro:>12,.2f}')
    
    # Totais
    total_c1 = sum(s['lucro_c1'] for s in stats)
    total_c2 = sum(s['lucro_c2'] for s in stats)
    total_combinado = total_c1 + total_c2
    custo_total = (len(combos_c1) + len(combos_c2)) * CUSTO * len(stats)
    
    print(f'\n   LUCRO TOTAL ({len(stats)} concursos):')
    print(f'   Apenas C1:  R$ {total_c1:>12,.2f}')
    print(f'   Apenas C2:  R$ {total_c2:>12,.2f}')
    print(f'   COMBINADO:  R$ {total_combinado:>12,.2f}')
    print(f'   Custo combinado: R$ {custo_total:>12,.2f}')
    print(f'   Retorno combinado: {(total_combinado + custo_total) / custo_total * 100 - 100:>+.2f}%')
    
    # Verificar complementaridade
    print('\n   ANÁLISE DE COMPLEMENTARIDADE:')
    
    # Em quantos concursos pelo menos um lucra?
    algum_lucra = sum(1 for s in stats if s['lucro_c1'] > 0 or s['lucro_c2'] > 0)
    ambos_lucram = sum(1 for s in stats if s['lucro_c1'] > 0 and s['lucro_c2'] > 0)
    nenhum_lucra = sum(1 for s in stats if s['lucro_c1'] <= 0 and s['lucro_c2'] <= 0)
    
    print(f'   Pelo menos um lucra: {algum_lucra} ({algum_lucra*100/len(stats):.1f}%)')
    print(f'   Ambos lucram:        {ambos_lucram} ({ambos_lucram*100/len(stats):.1f}%)')
    print(f'   Nenhum lucra:        {nenhum_lucra} ({nenhum_lucra*100/len(stats):.1f}%)')
    
    # Correlação inversa?
    c1_lucra_c2_perde = sum(1 for s in stats if s['lucro_c1'] > 0 and s['lucro_c2'] <= 0)
    c2_lucra_c1_perde = sum(1 for s in stats if s['lucro_c2'] > 0 and s['lucro_c1'] <= 0)
    
    print(f'\n   Complementaridade real:')
    print(f'   C1 lucra e C2 perde: {c1_lucra_c2_perde} concursos')
    print(f'   C2 lucra e C1 perde: {c2_lucra_c1_perde} concursos')
    
    return {
        'stats': stats,
        'total_c1': total_c1,
        'total_c2': total_c2,
        'total_combinado': total_combinado,
        'complementaridade': {
            'algum_lucra': algum_lucra,
            'ambos_lucram': ambos_lucram,
            'nenhum_lucra': nenhum_lucra
        }
    }


def main():
    print('\n' + '=' * 70)
    print('   GERADOR DE COMBINAÇÕES C1 E C2 COMPLEMENTARES')
    print('   ' + datetime.now().strftime('%d/%m/%Y %H:%M'))
    print('=' * 70)
    
    # Carregar resultados
    print('\n   Carregando resultados...')
    resultados = carregar_resultados(100)
    print(f'   {len(resultados)} resultados carregados')
    
    # Calcular frequências
    frequencias = Counter()
    for _, nums in resultados:
        frequencias.update(nums)
    
    # Carregar arquivo original
    arquivo_original = r'c:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combo20_estrategia_20260121_143756.txt'
    print(f'\n   Carregando combinações originais...')
    combinacoes_originais = []
    with open(arquivo_original, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                try:
                    nums = [int(n) for n in linha.split(',')]
                    if len(nums) == 15:
                        combinacoes_originais.append(nums)
                except:
                    continue
    print(f'   {len(combinacoes_originais):,} combinações carregadas')
    
    # Filtrar C1
    print('\n' + '-' * 70)
    combos_c1 = filtrar_por_tendencia(
        combinacoes_originais, 'C1', frequencias,
        min_nucleo=13, top_freq_pct=0.20, top_final=1000
    )
    
    # Filtrar C2
    print('\n' + '-' * 70)
    combos_c2 = filtrar_por_tendencia(
        combinacoes_originais, 'C2', frequencias,
        min_nucleo=13, top_freq_pct=0.20, top_final=1000
    )
    
    # Converter para sets para análise
    combos_c1_sets = [set(c) for c in combos_c1]
    combos_c2_sets = [set(c) for c in combos_c2]
    
    # Salvar arquivos
    arquivo_c1 = r'c:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combo20_FILTRADAS_C1.txt'
    arquivo_c2 = r'c:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combo20_FILTRADAS_C2.txt'
    
    with open(arquivo_c1, 'w') as f:
        f.write(f'# COMBINACOES FILTRADAS - TENDENCIA C1 [1,3,4]\n')
        f.write(f'# Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
        f.write(f'# Total: {len(combos_c1)} combinacoes\n')
        f.write(f'# Criterios: nucleo>=13, mais divergentes C1 que C2, top 20% freq\n\n')
        for c in combos_c1:
            f.write(','.join(map(str, c)) + '\n')
    
    with open(arquivo_c2, 'w') as f:
        f.write(f'# COMBINACOES FILTRADAS - TENDENCIA C2 [15,17,18]\n')
        f.write(f'# Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
        f.write(f'# Total: {len(combos_c2)} combinacoes\n')
        f.write(f'# Criterios: nucleo>=13, mais divergentes C2 que C1, top 20% freq\n\n')
        for c in combos_c2:
            f.write(','.join(map(str, c)) + '\n')
    
    print(f'\n   Salvo: {arquivo_c1}')
    print(f'   Salvo: {arquivo_c2}')
    
    # Analisar complementaridade
    resultado_analise = analisar_complementaridade(combos_c1_sets, combos_c2_sets, resultados)
    
    print('\n' + '=' * 70)
    print('   FIM DA ANÁLISE')
    print('=' * 70)
    
    return resultado_analise


if __name__ == '__main__':
    main()
