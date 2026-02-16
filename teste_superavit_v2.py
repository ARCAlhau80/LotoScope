# -*- coding: utf-8 -*-
"""
Teste da Nova Estratégia SUPERÁVIT v2.0
"""

ranking_data = {
    15: {'curta': 40.0, 'media': 46.7, 'longa': 62.0},
    12: {'curta': 40.0, 'media': 46.7, 'longa': 56.0},
    1:  {'curta': 40.0, 'media': 53.3, 'longa': 68.0},
    4:  {'curta': 40.0, 'media': 66.7, 'longa': 76.0},
    23: {'curta': 40.0, 'media': 66.7, 'longa': 60.0},
    13: {'curta': 40.0, 'media': 40.0, 'longa': 58.0},
    24: {'curta': 40.0, 'media': 66.7, 'longa': 58.0},
    21: {'curta': 40.0, 'media': 66.7, 'longa': 64.0},
    7:  {'curta': 20.0, 'media': 53.3, 'longa': 52.0},
    10: {'curta': 60.0, 'media': 33.3, 'longa': 60.0},
    16: {'curta': 40.0, 'media': 53.3, 'longa': 50.0},
    3:  {'curta': 40.0, 'media': 60.0, 'longa': 48.0},
    9:  {'curta': 60.0, 'media': 73.3, 'longa': 54.0},
    2:  {'curta': 60.0, 'media': 60.0, 'longa': 68.0},
    18: {'curta': 60.0, 'media': 40.0, 'longa': 50.0},
    25: {'curta': 100.0,'media': 53.3, 'longa': 60.0},
    6:  {'curta': 80.0, 'media': 80.0, 'longa': 62.0},
    19: {'curta': 80.0, 'media': 73.3, 'longa': 62.0},
    22: {'curta': 80.0, 'media': 66.7, 'longa': 62.0},
    5:  {'curta': 80.0, 'media': 60.0, 'longa': 58.0},
    11: {'curta': 80.0, 'media': 73.3, 'longa': 58.0},
    17: {'curta': 100.0,'media': 60.0, 'longa': 58.0},
    8:  {'curta': 80.0, 'media': 73.3, 'longa': 72.0},
    14: {'curta': 80.0, 'media': 53.3, 'longa': 48.0},
    20: {'curta': 80.0, 'media': 80.0, 'longa': 76.0},
}

resultado_3613 = {1,3,4,7,9,10,11,12,15,16,18,20,21,22,23}

print('=' * 75)
print('🧪 TESTE DA NOVA ESTRATÉGIA SUPERÁVIT v2.0')
print('=' * 75)
print()

candidatos = []
for n, d in ranking_data.items():
    fc = d['curta']
    fm = d['media']
    fl = d['longa']
    
    indice_debito = fl - fc
    queda_forte = fc < fm < fl
    tendencia_queda = (fc < fm) or (fm < fl)
    
    score = 0
    
    # NOVA LÓGICA: Excluir SUPERÁVIT, não DÉBITO!
    if indice_debito < -30:
        score += 5
        status = '💰 SUPERÁVIT ALTO'
    elif indice_debito < -15:
        score += 4
        status = '💰 SUPERÁVIT'
    elif indice_debito < 0:
        score += 2
        status = 'superávit leve'
    elif indice_debito < 15:
        score += 0
        status = 'equilibrado'
    else:
        score -= 3
        status = '⚠️ DÉBITO ALTO'
    
    # Bônus para curta muito alta
    if fc >= 100:
        score += 3
    elif fc >= 80:
        score += 2
    
    # Penalizar números em débito
    if fc <= 40 and fl >= 55:
        score -= 4
    
    candidatos.append({
        'num': n,
        'freq_curta': fc,
        'freq_longa': fl,
        'indice_debito': indice_debito,
        'status': status,
        'score': score
    })

candidatos.sort(key=lambda x: -x['score'])

print('📊 RANKING DE EXCLUSÃO (SUPERÁVIT v2.0):')
print('-' * 75)
print(f'   Num   Curta%  Longa%  Déb/Sup   Status              Score   Saiu?')
print('-' * 75)

for i, c in enumerate(candidatos):
    marker = '❌' if i < 2 else '  '
    saiu = '✅SIM' if c['num'] in resultado_3613 else '  ---'
    print(f'{marker} {c["num"]:3d}   {c["freq_curta"]:5.1f}   {c["freq_longa"]:5.1f}   {c["indice_debito"]:+6.1f}   {c["status"]:18}  {c["score"]:5.2f}   {saiu}')

excluir_novo = [candidatos[0]['num'], candidatos[1]['num']]
print()
print(f'🆕 NOVA ESTRATÉGIA excluiria: {excluir_novo}')
erros_novo = len(set(excluir_novo) & resultado_3613)
print(f'   Erros (excluídos que saíram): {erros_novo}')
print()
print(f'🔴 ESTRATÉGIA ANTIGA excluía: [12, 15]')
print(f'   Erros: 2 (AMBOS saíram!)')
print()
if erros_novo < 2:
    print('✅ MELHORIA CONFIRMADA: Nova estratégia teria funcionado MELHOR!')
else:
    print('⚠️ Precisa refinar mais')

# Pool 23 resultante
pool_23_novo = sorted([n for n in range(1,26) if n not in excluir_novo])
print()
print(f'📦 POOL 23 com nova estratégia: {pool_23_novo}')

# Verificar cobertura
cobertura = len(resultado_3613 & set(pool_23_novo))
print(f'   Cobertura do resultado: {cobertura}/15 números')
