# -*- coding: utf-8 -*-
"""
Teste de Estratégia por Quadrantes
Analisa se escolher 3 quadrantes (15 números) pode gerar bons resultados
"""

import pyodbc
from itertools import combinations

# Definição dos 5 quadrantes (baseado nos scores do sistema)
QUADRANTES = {
    'Q1': [1, 5, 13, 19, 25],   # score +5.2 (PIOR - excluir)
    'Q2': [3, 9, 10, 20, 23],   # score +2.2 (quente)
    'Q3': [2, 4, 8, 18, 24],    # score -1.4 (neutro)
    'Q4': [6, 7, 11, 12, 14],   # score -2.0 (frio)
    'Q5': [15, 16, 17, 21, 22], # score -2.0 (MELHOR)
}

def main():
    # Todas as combinações de 3 quadrantes (10 possíveis)
    combos_3q = list(combinations(['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], 3))
    
    # Conectar ao banco
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;')
    cursor = conn.cursor()
    
    # Buscar últimos 100 concursos
    cursor.execute('''
        SELECT TOP 100 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    ''')
    resultados = cursor.fetchall()
    conn.close()
    
    print('='*80)
    print('🎯 ANÁLISE DE ESTRATÉGIA POR QUADRANTES')
    print('='*80)
    print(f'Analisando últimos {len(resultados)} concursos')
    print()
    
    # Estatísticas por combinação de quadrantes
    stats = {}
    
    for combo_q in combos_3q:
        # Números do pool (3 quadrantes = 15 números)
        pool = []
        for q in combo_q:
            pool.extend(QUADRANTES[q])
        pool_set = set(pool)
        
        acertos_lista = []
        acertos_11_plus = 0
        acertos_12_plus = 0
        acertos_13_plus = 0
        acertos_14_plus = 0
        acertos_15 = 0
        
        for row in resultados:
            resultado = set(row[1:16])
            acertos = len(pool_set & resultado)
            acertos_lista.append(acertos)
            
            if acertos >= 11: acertos_11_plus += 1
            if acertos >= 12: acertos_12_plus += 1
            if acertos >= 13: acertos_13_plus += 1
            if acertos >= 14: acertos_14_plus += 1
            if acertos == 15: acertos_15 += 1
        
        media = sum(acertos_lista) / len(acertos_lista)
        stats[combo_q] = {
            'media': media,
            'min': min(acertos_lista),
            'max': max(acertos_lista),
            '11+': acertos_11_plus,
            '12+': acertos_12_plus,
            '13+': acertos_13_plus,
            '14+': acertos_14_plus,
            '15': acertos_15,
        }
    
    # Ordenar por taxa de 11+
    stats_ordenado = sorted(stats.items(), key=lambda x: x[1]['11+'], reverse=True)
    
    print('📊 RANKING DE COMBINAÇÕES DE 3 QUADRANTES (por taxa de ≥11 acertos):')
    print('-'*80)
    print(f"{'Quadrantes':<20} {'Media':>8} {'Min':>5} {'Max':>5} {'>=11':>6} {'>=12':>6} {'>=13':>6} {'>=14':>6} {'=15':>5}")
    print('-'*80)
    
    for combo_q, s in stats_ordenado:
        nome = '+'.join(combo_q)
        pct_11 = s['11+']/len(resultados)*100
        print(f"{nome:<20} {s['media']:>8.1f} {s['min']:>5} {s['max']:>5} {s['11+']:>5}({pct_11:>3.0f}%) {s['12+']:>5} {s['13+']:>5} {s['14+']:>5} {s['15']:>5}")
    
    print()
    print('='*80)
    print('🏆 MELHOR ESTRATÉGIA:', '+'.join(stats_ordenado[0][0]))
    print('   Taxa >=11:', f"{stats_ordenado[0][1]['11+']/len(resultados)*100:.1f}%")
    print()
    
    # Comparar com baseline (escolha aleatória de 15 números)
    print('📈 COMPARAÇÃO COM BASELINE:')
    print('   Random (15 de 25): ~60% taxa de >=11')
    melhor_taxa = stats_ordenado[0][1]['11+']/len(resultados)*100
    print(f'   Melhor quadrante: {melhor_taxa:.1f}% taxa de >=11')
    if melhor_taxa > 60:
        print(f'   ✅ SUPERA baseline em {melhor_taxa-60:.1f}pp')
    else:
        print(f'   ❌ Abaixo do baseline em {60-melhor_taxa:.1f}pp')
    
    print()
    print('='*80)
    print('💡 ANÁLISE DA LÓGICA DOS QUADRANTES:')
    print('='*80)
    
    # Verificar se excluir Q1 (PIOR) ajuda
    print('\n📍 Estratégias que EXCLUEM Q1 (score +5.2 = PIOR):')
    for combo_q, s in stats_ordenado:
        if 'Q1' not in combo_q:
            nome = '+'.join(combo_q)
            pct = s['11+']/len(resultados)*100
            print(f"   {nome}: {pct:.1f}% taxa >=11")
    
    print('\n📍 Estratégias que INCLUEM Q5 (score -2.0 = MELHOR):')
    for combo_q, s in stats_ordenado:
        if 'Q5' in combo_q:
            nome = '+'.join(combo_q)
            pct = s['11+']/len(resultados)*100
            print(f"   {nome}: {pct:.1f}% taxa >=11")
    
    print('\n📍 Melhor estratégia TEÓRICA (Q3+Q4+Q5 - exclui Q1 e Q2 mais quentes):')
    for combo_q, s in stats_ordenado:
        if combo_q == ('Q3', 'Q4', 'Q5'):
            pct = s['11+']/len(resultados)*100
            print(f"   Q3+Q4+Q5: {pct:.1f}% taxa >=11")
            print(f"   Números: {QUADRANTES['Q3']} + {QUADRANTES['Q4']} + {QUADRANTES['Q5']}")

if __name__ == '__main__':
    main()
