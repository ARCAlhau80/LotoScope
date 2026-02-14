#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE COMBINAÇÕES C2 REAIS
================================
Gera combinações a partir do pool COMBO2 (não apenas filtra C1)

Autor: LotoScope AI
Data: Janeiro 2026
"""

from itertools import combinations
from collections import Counter
from datetime import datetime
import pyodbc


COMBO1 = [1,3,4,6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
COMBO2 = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

DIV_C1 = [1, 3, 4]
DIV_C2 = [15, 17, 18]
NUCLEO = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23, 24, 25]

PREMIOS = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}
CUSTO = 3.00

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def main():
    print('=' * 70)
    print('   GERADOR DE COMBINAÇÕES C2 REAIS (POOL COMBO2)')
    print('=' * 70)
    
    # Carregar frequências
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT TOP 100 N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 
            FROM Resultados_INT ORDER BY Concurso DESC
        ''')
        frequencias = Counter()
        for row in cursor.fetchall():
            frequencias.update([row[i] for i in range(15)])
    
    print(f'   Frequências dos últimos 100 concursos calculadas')
    
    # Gerar combinações C2
    print(f'\n   Gerando combinações COMBO2 (tendência C2)...')
    
    div_c2_set = set(DIV_C2)
    nucleo_set = set(NUCLEO)
    
    combos_c2 = []
    total = 0
    
    for combo in combinations(COMBO2, 15):
        total += 1
        combo_set = set(combo)
        
        div2_count = len(combo_set & div_c2_set)
        nucleo_count = len(combo_set & nucleo_set)
        
        if div2_count >= 1 and nucleo_count >= 13:
            score = sum(frequencias.get(n, 0) for n in combo)
            combos_c2.append((list(combo), score))
    
    print(f'   Total teórico C(20,15): {total:,}')
    print(f'   Após filtros: {len(combos_c2):,}')
    
    combos_c2.sort(key=lambda x: x[1], reverse=True)
    top_c2 = [c[0] for c in combos_c2[:1000]]
    
    print(f'   TOP 1000 selecionadas')
    
    # Salvar
    arquivo_c2 = 'combo20_C2_tendencia.txt'
    with open(arquivo_c2, 'w') as f:
        f.write('# COMBINACOES COMBO2 - TENDENCIA C2 [15,17,18]\n')
        f.write(f'# Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
        f.write(f'# Pool: {COMBO2}\n')
        f.write(f'# Divergentes: {DIV_C2}\n')
        f.write(f'# Total: {len(top_c2)} combinacoes\n')
        f.write('# Filtros: nucleo>=13, div_c2>=1, top score freq\n\n')
        for c in top_c2:
            f.write(','.join(map(str, c)) + '\n')
    
    print(f'   Salvo: {arquivo_c2}')
    
    # Comparar C1 vs C2
    print('\n' + '=' * 70)
    print('   ANÁLISE COMPLEMENTARIDADE COM HISTÓRICO')
    print('=' * 70)
    
    # Carregar C1
    with open('combo20_FILTRADAS_TOP1000.txt', 'r') as f:
        combos_c1 = []
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                try:
                    nums = [int(n) for n in linha.split(',')]
                    if len(nums) == 15:
                        combos_c1.append(set(nums))
                except:
                    continue
    
    combos_c2_sets = [set(c) for c in top_c2]
    
    # Carregar resultados
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT TOP 100 Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 
            FROM Resultados_INT ORDER BY Concurso DESC
        ''')
        resultados = [(row.Concurso, set(row[i] for i in range(1,16))) for row in cursor.fetchall()]
    
    print(f'\n   Analisando últimos {len(resultados)} concursos...')
    print(f'   C1: {len(combos_c1)} combos | C2: {len(combos_c2_sets)} combos')
    
    div_c1_set = set(DIV_C1)
    div_c2_set = set(DIV_C2)
    
    print('\n   Conc  Fav   Div1 Div2  MaxC1 MaxC2  Premio C1    Premio C2    Lucro C1      Lucro C2')
    print('   ' + '-' * 90)
    
    stats = []
    for concurso, resultado in resultados[:50]:
        div1 = len(resultado & div_c1_set)
        div2 = len(resultado & div_c2_set)
        
        if div1 > div2:
            fav = 'C1'
        elif div2 > div1:
            fav = 'C2'
        else:
            fav = '=='
        
        acertos_c1 = [len(c & resultado) for c in combos_c1]
        acertos_c2 = [len(c & resultado) for c in combos_c2_sets]
        
        premio_c1 = sum(PREMIOS.get(a, 0) for a in acertos_c1 if a >= 11)
        premio_c2 = sum(PREMIOS.get(a, 0) for a in acertos_c2 if a >= 11)
        
        custo = len(combos_c1) * CUSTO
        lucro_c1 = premio_c1 - custo
        lucro_c2 = premio_c2 - custo
        
        print(f'   {concurso:5} [{fav:^3}]  {div1}/3  {div2}/3   {max(acertos_c1):2}    {max(acertos_c2):2}    '
              f'R${premio_c1:>8,}   R${premio_c2:>8,}   R${lucro_c1:>+10,.0f}  R${lucro_c2:>+10,.0f}')
        
        stats.append({
            'concurso': concurso,
            'fav': fav,
            'lucro_c1': lucro_c1,
            'lucro_c2': lucro_c2,
            'max_c1': max(acertos_c1),
            'max_c2': max(acertos_c2),
        })
    
    # Resumo
    print('\n' + '=' * 70)
    print('   RESUMO COMPLEMENTARIDADE')
    print('=' * 70)
    
    c1_fav = [s for s in stats if s['fav'] == 'C1']
    c2_fav = [s for s in stats if s['fav'] == 'C2']
    neutros = [s for s in stats if s['fav'] == '==']
    
    print(f'\n   Distribuição de favoráveis (últimos {len(stats)}):')
    print(f'   C1 favorável: {len(c1_fav)} ({len(c1_fav)*100/len(stats):.1f}%)')
    print(f'   C2 favorável: {len(c2_fav)} ({len(c2_fav)*100/len(stats):.1f}%)')
    print(f'   Neutro:       {len(neutros)} ({len(neutros)*100/len(stats):.1f}%)')
    
    print('\n   Quando C1 favorável:')
    if c1_fav:
        lucro_c1_em_c1 = sum(s['lucro_c1'] for s in c1_fav)
        lucro_c2_em_c1 = sum(s['lucro_c2'] for s in c1_fav)
        print(f'   -> Jogando C1: R$ {lucro_c1_em_c1:>+12,.2f}')
        print(f'   -> Jogando C2: R$ {lucro_c2_em_c1:>+12,.2f}')
    
    print('\n   Quando C2 favorável:')
    if c2_fav:
        lucro_c1_em_c2 = sum(s['lucro_c1'] for s in c2_fav)
        lucro_c2_em_c2 = sum(s['lucro_c2'] for s in c2_fav)
        print(f'   -> Jogando C1: R$ {lucro_c1_em_c2:>+12,.2f}')
        print(f'   -> Jogando C2: R$ {lucro_c2_em_c2:>+12,.2f}')
    
    total_c1 = sum(s['lucro_c1'] for s in stats)
    total_c2 = sum(s['lucro_c2'] for s in stats)
    
    print('\n   LUCRO TOTAL:')
    print(f'   C1 sozinho: R$ {total_c1:>+12,.2f}')
    print(f'   C2 sozinho: R$ {total_c2:>+12,.2f}')
    print(f'   AMBOS:      R$ {total_c1 + total_c2:>+12,.2f}')
    
    # Complementaridade
    c1_lucra = sum(1 for s in stats if s['lucro_c1'] > 0)
    c2_lucra = sum(1 for s in stats if s['lucro_c2'] > 0)
    algum_lucra = sum(1 for s in stats if s['lucro_c1'] > 0 or s['lucro_c2'] > 0)
    ambos_lucram = sum(1 for s in stats if s['lucro_c1'] > 0 and s['lucro_c2'] > 0)
    
    print(f'\n   COBERTURA:')
    print(f'   C1 lucra em: {c1_lucra}/{len(stats)} concursos ({c1_lucra*100/len(stats):.1f}%)')
    print(f'   C2 lucra em: {c2_lucra}/{len(stats)} concursos ({c2_lucra*100/len(stats):.1f}%)')
    print(f'   Pelo menos 1 lucra: {algum_lucra}/{len(stats)} ({algum_lucra*100/len(stats):.1f}%)')
    print(f'   Ambos lucram: {ambos_lucram}/{len(stats)} ({ambos_lucram*100/len(stats):.1f}%)')
    
    # Quando exatamente um lucra
    c1_lucra_c2_perde = sum(1 for s in stats if s['lucro_c1'] > 0 and s['lucro_c2'] <= 0)
    c2_lucra_c1_perde = sum(1 for s in stats if s['lucro_c2'] > 0 and s['lucro_c1'] <= 0)
    
    print(f'\n   COMPLEMENTARIDADE PERFEITA:')
    print(f'   C1 lucra quando C2 perde: {c1_lucra_c2_perde} vezes')
    print(f'   C2 lucra quando C1 perde: {c2_lucra_c1_perde} vezes')
    
    complementar = c1_lucra_c2_perde + c2_lucra_c1_perde
    print(f'\n   => {complementar} concursos com complementaridade real!')


if __name__ == '__main__':
    main()
