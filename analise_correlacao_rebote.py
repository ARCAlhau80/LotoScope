# -*- coding: utf-8 -*-
"""
Análise de Correlação: Padrão de Rebote Estatístico
Concurso 3613 - Identificando erro na estratégia de exclusão
"""

import numpy as np

print('=' * 75)
print('🔬 ANÁLISE DE CORRELAÇÃO: PADRÃO DE REBOTE ESTATÍSTICO')
print('=' * 75)

# Dados fornecidos pelo ranking do Pool 23 Híbrido
ranking_data = {
    15: {'curta': 40.0, 'media': 46.7, 'longa': 62.0, 'tend': 'QUEDA FORTE', 'score': 8.80},
    12: {'curta': 40.0, 'media': 46.7, 'longa': 56.0, 'tend': 'QUEDA FORTE', 'score': 8.60},
    1:  {'curta': 40.0, 'media': 53.3, 'longa': 68.0, 'tend': 'QUEDA FORTE', 'score': 8.20},
    4:  {'curta': 40.0, 'media': 66.7, 'longa': 76.0, 'tend': 'QUEDA FORTE', 'score': 7.40},
    23: {'curta': 40.0, 'media': 66.7, 'longa': 60.0, 'tend': 'queda', 'score': 7.00},
    13: {'curta': 40.0, 'media': 40.0, 'longa': 58.0, 'tend': 'queda', 'score': 6.80},
    24: {'curta': 40.0, 'media': 66.7, 'longa': 58.0, 'tend': 'queda', 'score': 6.80},
    21: {'curta': 40.0, 'media': 66.7, 'longa': 64.0, 'tend': 'queda', 'score': 6.60},
    7:  {'curta': 20.0, 'media': 53.3, 'longa': 52.0, 'tend': 'queda', 'score': 6.20},
    10: {'curta': 60.0, 'media': 33.3, 'longa': 60.0, 'tend': 'queda', 'score': 6.00},
    16: {'curta': 40.0, 'media': 53.3, 'longa': 50.0, 'tend': 'queda', 'score': 6.00},
    3:  {'curta': 40.0, 'media': 60.0, 'longa': 48.0, 'tend': 'queda', 'score': 5.80},
    9:  {'curta': 60.0, 'media': 73.3, 'longa': 54.0, 'tend': 'queda', 'score': 5.40},
    2:  {'curta': 60.0, 'media': 60.0, 'longa': 68.0, 'tend': 'queda', 'score': 5.20},
    18: {'curta': 60.0, 'media': 40.0, 'longa': 50.0, 'tend': 'queda', 'score': 5.00},
    25: {'curta': 100.0,'media': 53.3, 'longa': 60.0, 'tend': 'queda', 'score': 1.80},
    6:  {'curta': 80.0, 'media': 80.0, 'longa': 62.0, 'tend': 'alta', 'score': 1.44},
    19: {'curta': 80.0, 'media': 73.3, 'longa': 62.0, 'tend': 'alta', 'score': 1.44},
    22: {'curta': 80.0, 'media': 66.7, 'longa': 62.0, 'tend': 'alta', 'score': 1.44},
    5:  {'curta': 80.0, 'media': 60.0, 'longa': 58.0, 'tend': 'alta', 'score': 1.44},
    11: {'curta': 80.0, 'media': 73.3, 'longa': 58.0, 'tend': 'alta', 'score': 1.44},
    17: {'curta': 100.0,'media': 60.0, 'longa': 58.0, 'tend': 'alta', 'score': 1.44},
    8:  {'curta': 80.0, 'media': 73.3, 'longa': 72.0, 'tend': 'alta', 'score': 1.14},
    14: {'curta': 80.0, 'media': 53.3, 'longa': 48.0, 'tend': 'alta', 'score': 1.14},
    20: {'curta': 80.0, 'media': 80.0, 'longa': 76.0, 'tend': 'alta', 'score': 1.02},
}

resultado_3613 = {1,3,4,7,9,10,11,12,15,16,18,20,21,22,23}

print()
print('📊 RESULTADO DO CONCURSO 3613:')
print(f'   Números sorteados: {sorted(resultado_3613)}')
print(f'   Excluídos pelo Pool 23: [12, 15]')
print(f'   ❌ ERRO: Ambos 12 e 15 SAÍRAM!')
print()

print('=' * 75)
print('🔍 PADRÃO DESCOBERTO: DIFERENÇA (LONGA - CURTA) = DÉBITO')
print('=' * 75)
print()
print('Hipótese: Números com ALTA diferença estão em DÉBITO')
print('         e tendem a VOLTAR, não a continuar ausentes!')
print()
print('Num   Curta%  Longa%   Dif    Saiu?   Situação')
print('-' * 60)

analise = []
for num, data in ranking_data.items():
    diff = data['longa'] - data['curta']
    saiu = num in resultado_3613
    analise.append((num, data['curta'], data['longa'], diff, saiu, data['tend']))

# Ordenar por diferença (maior diferença = maior débito)
analise.sort(key=lambda x: -x[3])

acertos_debito = 0
total_debito = 0
acertos_superavit = 0
total_superavit = 0

for num, curta, longa, diff, saiu, tend in analise:
    if diff >= 15:
        situacao = '⚠️ ALTO DÉBITO'
        total_debito += 1
        if saiu:
            acertos_debito += 1
    elif diff >= 5:
        situacao = 'débito mod.'
    elif diff >= 0:
        situacao = 'equilibrado'
    else:
        situacao = '💰 SUPERÁVIT'
        total_superavit += 1
        if not saiu:
            acertos_superavit += 1
    
    marca = '✅SIM' if saiu else '  ---'
    print(f'{num:>3}   {curta:>5.1f}   {longa:>5.1f}   {diff:>+5.1f}   {marca}    {situacao}')

print()
print('=' * 75)
print('📈 ESTATÍSTICAS DO PADRÃO')
print('=' * 75)
print()
print(f'Números com ALTO DÉBITO (dif >= 15): {total_debito}')
print(f'  → Quantos SAÍRAM: {acertos_debito} ({acertos_debito/total_debito*100:.1f}%)')
print()
print(f'Números em SUPERÁVIT (dif < 0): {total_superavit}')
print(f'  → Quantos NÃO saíram: {acertos_superavit} ({acertos_superavit/total_superavit*100:.1f}% de acerto)')
print()

# Números que NÃO saíram
nao_sorteados = set(range(1,26)) - resultado_3613
print(f'🚫 NÚMEROS QUE NÃO SAÍRAM: {sorted(nao_sorteados)}')
print()
print('Análise dos não sorteados:')
print('Num   Curta%  Longa%   Dif    Tendência')
print('-' * 50)
for num in sorted(nao_sorteados):
    d = ranking_data[num]
    diff = d['longa'] - d['curta']
    print(f'{num:>3}   {d["curta"]:>5.1f}   {d["longa"]:>5.1f}   {diff:>+5.1f}   {d["tend"]}')

print()
print('=' * 75)
print('💡 CONCLUSÃO E NOVA REGRA PROPOSTA')
print('=' * 75)
print()
print('PROBLEMA ATUAL:')
print('  A estratégia exclui números com "QUEDA FORTE" (curta << longa)')
print('  Mas esses números estão em DÉBITO e tendem a VOLTAR!')
print()
print('REGRA CORRIGIDA:')
print('  1. Calcular DÉBITO = Longa% - Curta%')
print('  2. Se DÉBITO >= 15%: NÃO EXCLUIR (número vai voltar)')
print('  3. Excluir números em SUPERÁVIT (Curta > Longa) com Curta alta')
print()

# Simular nova estratégia
print('=' * 75)
print('🧪 SIMULAÇÃO: ESTRATÉGIA CORRIGIDA')
print('=' * 75)
print()

# Candidatos à exclusão: superávit + curta alta
candidatos_exclusao = []
for num, data in ranking_data.items():
    diff = data['longa'] - data['curta']
    # Superávit (curta > longa) OU curta muito alta com baixo débito
    if diff < 0:  # Superávit
        candidatos_exclusao.append((num, diff, data['curta'], 'SUPERÁVIT'))
    elif data['curta'] >= 100 and diff < 20:  # Muito quente sem débito alto
        candidatos_exclusao.append((num, diff, data['curta'], 'MUITO QUENTE'))

# Ordenar: primeiro superávit (mais negativo), depois curta mais alta
candidatos_exclusao.sort(key=lambda x: (x[1], -x[2]))

print('Candidatos à exclusão (ordem de prioridade):')
print('Num   Dif    Curta%   Motivo')
print('-' * 40)
for num, diff, curta, motivo in candidatos_exclusao[:5]:
    saiu = '❌SAIU' if num in resultado_3613 else '✅OK'
    print(f'{num:>3}   {diff:>+5.1f}   {curta:>5.1f}   {motivo}  {saiu}')

novos_excluidos = set([c[0] for c in candidatos_exclusao[:2]])
print()
print(f'NOVA ESTRATÉGIA excluiria: {sorted(novos_excluidos)}')
erros_nova = len(novos_excluidos & resultado_3613)
print(f'Erros (excluídos que saíram): {erros_nova}')
print()

print('ESTRATÉGIA ATUAL excluiu: [12, 15]')
print('Erros: 2 (ambos saíram!)')
print()

if erros_nova < 2:
    print('✅ A NOVA ESTRATÉGIA TERIA FUNCIONADO MELHOR!')
else:
    print('⚠️ Precisa refinar mais a estratégia')
