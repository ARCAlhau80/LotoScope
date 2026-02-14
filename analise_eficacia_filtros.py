"""
ANÁLISE HISTÓRICA DE EFICÁCIA DOS FILTROS
Analisa todos os concursos para identificar quais filtros são mais eficientes
e quais funcionam bem em conjunto.
"""

import sys
sys.path.insert(0, '.')
import pyodbc
from collections import Counter, defaultdict
from itertools import combinations
import random

def main():
    print('=' * 80)
    print('🔬 ANÁLISE HISTÓRICA DE EFICÁCIA DOS FILTROS')
    print('=' * 80)

    # Conectar ao banco
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-K6JPBDS;'
        'DATABASE=LOTOFACIL;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()

    # Buscar últimos 100 concursos para análise
    cursor.execute('''
        SELECT TOP 100 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT 
        ORDER BY Concurso DESC
    ''')
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            'concurso': row[0],
            'numeros': sorted([row[i] for i in range(1, 16)])
        })
    conn.close()

    primeiro = resultados[-1]['concurso']
    ultimo = resultados[0]['concurso']
    print(f'\n📊 Analisando {len(resultados)} concursos (do {primeiro} ao {ultimo})')

    # Importar analisador
    from lotofacil_lite.geradores.analisador_combinacoes_geradas import AnalisadorCombinacoesGeradas

    # Estatísticas por filtro
    filtros_stats = defaultdict(lambda: {'eliminou_boas': 0, 'manteve_boas': 0, 'total_boas': 0})
    filtros_pares = defaultdict(lambda: {'ambos_eliminaram': 0, 'total': 0})

    # Lista de filtros
    FILTROS = [
        'soma', 'pares', 'primos', 'fibonacci', 'sequencias', 'faixas',
        'linhas', 'colunas', 'quentes', 'frios', 'repeticoes', 'historico',
        'trios_quentes', 'trios_frios', 'quintetos_quentes', 'quintetos_frios',
        'divida_trios', 'numeros_pivo', 'momentum', 'paridade_trios'
    ]

    # Mapeamento de chaves
    CHAVE_MAP = {
        'divida_trios': 'passou_divida',
        'numeros_pivo': 'passou_pivo',
        'paridade_trios': 'passou_paridade',
        'momentum': 'passou_momentum',
    }

    print('\n🔄 Processando concursos...')
    
    total_boas_encontradas = 0

    # Para cada concurso (exceto o primeiro), simular
    for i in range(len(resultados) - 1):
        concurso_validar = resultados[i]  # Concurso atual (para validar)
        
        # Gerar 500 combinações aleatórias (simulando arquivo gerado)
        combinacoes_teste = []
        for _ in range(500):
            comb = sorted(random.sample(range(1, 26), 15))
            combinacoes_teste.append(comb)
        
        # Criar analisador silencioso
        analisador = AnalisadorCombinacoesGeradas()
        analisador.combinacoes = combinacoes_teste
        
        # Analisar todas
        avaliacoes = analisador.analisar_todas(validar_hist=True)
        
        # Calcular acertos de cada combinação no concurso
        nums_resultado = set(concurso_validar['numeros'])
        for aval in avaliacoes:
            aval['acertos'] = len(set(aval['combinacao']) & nums_resultado)
        
        # Identificar boas combinações (11+ acertos)
        boas = [a for a in avaliacoes if a['acertos'] >= 11]
        total_boas_encontradas += len(boas)
        
        if boas:
            for boa in boas:
                # Verificar cada filtro
                filtros_falharam = []
                
                for filtro in FILTROS:
                    # Determinar chave
                    if filtro in CHAVE_MAP:
                        chave = CHAVE_MAP[filtro]
                    else:
                        chave = f'passou_{filtro}'
                    
                    passou = boa.get(chave, True)
                    
                    filtros_stats[filtro]['total_boas'] += 1
                    if passou:
                        filtros_stats[filtro]['manteve_boas'] += 1
                    else:
                        filtros_stats[filtro]['eliminou_boas'] += 1
                        filtros_falharam.append(filtro)
                
                # Contar pares que falharam juntos
                for par in combinations(filtros_falharam, 2):
                    par_key = tuple(sorted(par))
                    filtros_pares[par_key]['ambos_eliminaram'] += 1
                    filtros_pares[par_key]['total'] += 1
        
        if (i + 1) % 20 == 0:
            print(f'   Processados {i + 1}/{len(resultados) - 1} concursos... ({total_boas_encontradas} boas combinações encontradas)')

    print(f'\n   ✅ Total de combinações com 11+ acertos analisadas: {total_boas_encontradas}')

    # ========== RESULTADO INDIVIDUAL ==========
    print('\n' + '=' * 80)
    print('📊 RESULTADO: EFICÁCIA INDIVIDUAL DOS FILTROS')
    print('=' * 80)
    print(f'\n{"Filtro":<20} | {"Manteve":>8} | {"Eliminou":>8} | {"Taxa Mant.":>10} | Status')
    print('-' * 70)

    # Ordenar por taxa de manutenção (melhor = mantém mais boas combinações)
    filtros_ordenados = sorted(
        filtros_stats.items(),
        key=lambda x: x[1]['manteve_boas'] / max(x[1]['total_boas'], 1),
        reverse=True
    )

    excelentes = []
    bons = []
    moderados = []
    ruins = []

    for filtro, stats in filtros_ordenados:
        total = stats['total_boas']
        manteve = stats['manteve_boas']
        eliminou = stats['eliminou_boas']
        taxa = (manteve / total * 100) if total > 0 else 0
        
        if taxa >= 90:
            status = '✅ EXCELENTE'
            excelentes.append(filtro)
        elif taxa >= 70:
            status = '🟢 BOM'
            bons.append(filtro)
        elif taxa >= 50:
            status = '🟡 MODERADO'
            moderados.append(filtro)
        else:
            status = '🔴 RUIM'
            ruins.append(filtro)
        
        print(f'{filtro:<20} | {manteve:>8} | {eliminou:>8} | {taxa:>9.1f}% | {status}')

    # ========== PARES PROBLEMÁTICOS ==========
    print('\n' + '=' * 80)
    print('🔗 TOP 15 PARES DE FILTROS QUE ELIMINAM JUNTOS (CORRELAÇÃO NEGATIVA)')
    print('=' * 80)
    print('\nPares que frequentemente eliminam boas combinações JUNTOS:')
    print('(Isso indica redundância ou conflito - considere desativar um deles)')
    print()

    # Top 15 pares que mais eliminam juntos
    pares_ordenados = sorted(
        filtros_pares.items(),
        key=lambda x: x[1]['ambos_eliminaram'],
        reverse=True
    )[:15]

    for par, stats in pares_ordenados:
        if stats['ambos_eliminaram'] > 0:
            print(f'   {par[0]:<20} + {par[1]:<20}: {stats["ambos_eliminaram"]:>5} eliminações conjuntas')

    # ========== RECOMENDAÇÕES ==========
    print('\n' + '=' * 80)
    print('💡 RECOMENDAÇÕES BASEADAS NA ANÁLISE')
    print('=' * 80)
    
    print('\n✅ FILTROS EXCELENTES (manter sempre ativos):')
    for f in excelentes:
        print(f'   • {f}')
    
    print('\n🟢 FILTROS BONS (recomendado manter):')
    for f in bons:
        print(f'   • {f}')
    
    print('\n🟡 FILTROS MODERADOS (considerar relaxar):')
    for f in moderados:
        print(f'   • {f}')
    
    print('\n🔴 FILTROS RUINS (considerar desativar ou relaxar muito):')
    for f in ruins:
        print(f'   • {f}')

    # ========== COMBINAÇÃO IDEAL ==========
    print('\n' + '=' * 80)
    print('🎯 COMBINAÇÃO IDEAL DE FILTROS SUGERIDA')
    print('=' * 80)
    
    # Filtros recomendados = excelentes + bons
    recomendados = excelentes + bons
    print(f'\nFiltros recomendados ({len(recomendados)}):')
    for f in recomendados:
        stats = filtros_stats[f]
        taxa = stats['manteve_boas'] / max(stats['total_boas'], 1) * 100
        print(f'   ✅ {f}: {taxa:.1f}% de manutenção')
    
    print('\nFiltros a relaxar ou desativar:')
    for f in moderados + ruins:
        stats = filtros_stats[f]
        taxa = stats['manteve_boas'] / max(stats['total_boas'], 1) * 100
        print(f'   ⚠️ {f}: {taxa:.1f}% de manutenção')

    print('\n' + '=' * 80)


if __name__ == '__main__':
    main()
