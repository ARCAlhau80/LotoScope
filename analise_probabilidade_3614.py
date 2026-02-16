# -*- coding: utf-8 -*-
"""
Análise de Probabilidade - Concurso 3614
"""
import sys
sys.path.insert(0, 'lotofacil_lite/utils')
from database_config import DatabaseConfig
import pandas as pd

RESULTADO_3614 = {2, 4, 5, 6, 9, 10, 11, 12, 14, 15, 16, 17, 20, 23, 25}

db = DatabaseConfig()
conn = db.get_connection()

print('='*70)
print('ANALISE DE COMBINACOES ENCALHADAS - CONCURSO 3614')
print('='*70)

query = '''
SELECT 
    ID, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
    Acertos_11, Ultimo_Acertos_11, UltimoConcursoAtualizado
FROM COMBINACOES_LOTOFACIL
'''
df = pd.read_sql(query, conn)
print(f'Total: {len(df):,}')

def calcular_acertos(row):
    nums = {row['N1'], row['N2'], row['N3'], row['N4'], row['N5'],
            row['N6'], row['N7'], row['N8'], row['N9'], row['N10'],
            row['N11'], row['N12'], row['N13'], row['N14'], row['N15']}
    return len(nums & RESULTADO_3614)

print('Calculando acertos...')
df['Acertos_3614'] = df.apply(calcular_acertos, axis=1)

# Calcular concursos desde ultimo acerto de 11
ultimo = df['UltimoConcursoAtualizado'].max()
df['Concursos_Sem_11'] = ultimo - df['Ultimo_Acertos_11'].fillna(0)

# Estatisticas de encalhamento
col = 'Concursos_Sem_11'
print(f'\nDistribuicao de {col}:')
print(f'  Min: {df[col].min():.0f}')
print(f'  Max: {df[col].max():.0f}')
print(f'  Media: {df[col].mean():.1f}')
print(f'  Mediana: {df[col].median():.0f}')

# === FILTRO: Encalhadas ===
print('\n' + '='*70)
print('FILTRO: ENCALHADAS (concursos sem acertar 11)')
print('='*70)

pct_total_11plus = len(df[df['Acertos_3614'] >= 11]) / len(df) * 100

for limite in [50, 100, 200, 500, 1000]:
    encalhadas = df[df['Concursos_Sem_11'] > limite]
    if len(encalhadas) > 0:
        count_11plus = len(encalhadas[encalhadas['Acertos_3614'] >= 11])
        pct_11 = count_11plus / len(encalhadas) * 100
        melhoria = pct_11 / pct_total_11plus
        print(f'  >{limite:>4} concursos: {len(encalhadas):>8,} comb | 11+: {pct_11:.2f}% | Melhoria: {melhoria:.2f}x')

# === FILTRO: Recentes (acertaram 11 recentemente) ===
print('\n' + '='*70)
print('FILTRO: RECENTES (acertaram 11 nos ultimos X concursos)')
print('='*70)

for limite in [10, 20, 50, 100]:
    recentes = df[df['Concursos_Sem_11'] <= limite]
    if len(recentes) > 0:
        count_11plus = len(recentes[recentes['Acertos_3614'] >= 11])
        pct_11 = count_11plus / len(recentes) * 100
        melhoria = pct_11 / pct_total_11plus
        print(f'  <={limite:>3} concursos: {len(recentes):>8,} comb | 11+: {pct_11:.2f}% | Melhoria: {melhoria:.2f}x')

# === FILTRO COMBINADO: Acertos_11 >= 313 E Encalhadas ===
print('\n' + '='*70)
print('FILTRO COMBINADO: Acertos_11 >= 313 E >50 concursos encalhada')
print('='*70)

filtro_comb = df[(df['Acertos_11'] >= 313) & (df['Concursos_Sem_11'] > 50)]
print(f'Combinacoes no filtro: {len(filtro_comb):,}')

for acertos in [11, 12, 13, 14, 15]:
    count_filtro = len(filtro_comb[filtro_comb['Acertos_3614'] == acertos])
    count_total = len(df[df['Acertos_3614'] == acertos])
    pct_filtro = count_filtro / len(filtro_comb) * 100 if len(filtro_comb) > 0 else 0
    pct_total = count_total / len(df) * 100
    melhoria = pct_filtro / pct_total if pct_total > 0 else 0
    print(f'  {acertos} acertos: {count_filtro:>7,} ({pct_filtro:.4f}%) | Melhoria: {melhoria:.2f}x')

# === FILTRO COMBINADO 2: Acertos_11 >= 330 E Recentes ===
print('\n' + '='*70)
print('FILTRO COMBINADO 2: Acertos_11 >= 330 E <=20 concursos recente')
print('='*70)

filtro_comb2 = df[(df['Acertos_11'] >= 330) & (df['Concursos_Sem_11'] <= 20)]
print(f'Combinacoes no filtro: {len(filtro_comb2):,}')

for acertos in [11, 12, 13, 14, 15]:
    count_filtro = len(filtro_comb2[filtro_comb2['Acertos_3614'] == acertos])
    count_total = len(df[df['Acertos_3614'] == acertos])
    pct_filtro = count_filtro / len(filtro_comb2) * 100 if len(filtro_comb2) > 0 else 0
    pct_total = count_total / len(df) * 100
    melhoria = pct_filtro / pct_total if pct_total > 0 else 0
    print(f'  {acertos} acertos: {count_filtro:>7,} ({pct_filtro:.4f}%) | Melhoria: {melhoria:.2f}x')

# === A COMBINACAO VENCEDORA ===
print('\n' + '='*70)
print('A COMBINACAO VENCEDORA DO 3614')
print('='*70)

vencedora = df[df['Acertos_3614'] == 15]
if len(vencedora) > 0:
    v = vencedora.iloc[0]
    print(f'ID: {int(v["ID"])}')
    nums = [int(v[f"N{i}"]) for i in range(1, 16)]
    print(f'Numeros: {nums}')
    print(f'Acertos_11 historico: {int(v["Acertos_11"])}')
    u11 = v["Ultimo_Acertos_11"]
    print(f'Ultimo_Acertos_11: {int(u11) if pd.notna(u11) else "N/A"}')
    print(f'Concursos sem acertar 11: {int(v["Concursos_Sem_11"])}')
    
    # Verificar em qual grupo ela estava
    print('\n>> Verificacao de filtros:')
    if v['Acertos_11'] >= 313:
        print('   [X] PASSOU no filtro Acertos_11 >= 313')
    else:
        print('   [ ] NAO passou no filtro Acertos_11 >= 313')
    
    if v['Acertos_11'] >= 330:
        print('   [X] PASSOU no filtro Acertos_11 >= 330')
    else:
        print('   [ ] NAO passou no filtro Acertos_11 >= 330')
    
    if v['Concursos_Sem_11'] > 50:
        print('   [X] PASSOU no filtro Encalhadas > 50')
    else:
        print('   [ ] NAO passou no filtro Encalhadas > 50')
    
    if v['Concursos_Sem_11'] <= 20:
        print('   [X] PASSOU no filtro Recentes <= 20')
    else:
        print('   [ ] NAO passou no filtro Recentes <= 20')

# === RESUMO ESTATISTICO ===
print('\n' + '='*70)
print('RESUMO: MELHOR FILTRO PARA ACERTOS 11+')
print('='*70)

# Testar varios filtros
filtros = [
    ('Sem filtro', df),
    ('Acertos_11 >= 313', df[df['Acertos_11'] >= 313]),
    ('Acertos_11 >= 330', df[df['Acertos_11'] >= 330]),
    ('Acertos_11 >= 350', df[df['Acertos_11'] >= 350]),
    ('Encalhadas > 50', df[df['Concursos_Sem_11'] > 50]),
    ('Encalhadas > 100', df[df['Concursos_Sem_11'] > 100]),
    ('Recentes <= 20', df[df['Concursos_Sem_11'] <= 20]),
    ('A11>=313 E Enc>50', df[(df['Acertos_11'] >= 313) & (df['Concursos_Sem_11'] > 50)]),
    ('A11>=330 E Rec<=20', df[(df['Acertos_11'] >= 330) & (df['Concursos_Sem_11'] <= 20)]),
]

print(f'\n{"Filtro":<25} | {"Combinacoes":>12} | {"11+ %":>8} | {"Melhoria":>8}')
print('-'*60)

base_pct = len(df[df['Acertos_3614'] >= 11]) / len(df) * 100

for nome, subset in filtros:
    if len(subset) > 0:
        count = len(subset[subset['Acertos_3614'] >= 11])
        pct = count / len(subset) * 100
        melhoria = pct / base_pct
        print(f'{nome:<25} | {len(subset):>12,} | {pct:>7.2f}% | {melhoria:>7.2f}x')

print('\n' + '='*70)
print('CONCLUSAO')
print('='*70)
print('''
1. O filtro Acertos_11 >= 313 oferece ~10% de melhoria nos acertos de 11+
2. O filtro Acertos_11 >= 330 oferece ~17% de melhoria
3. Combinacoes ENCALHADAS nao mostram melhoria significativa
4. Combinacoes RECENTES (acertaram 11 recentemente) mostram MELHOR performance!
5. O filtro combinado A11>=330 E Recentes<=20 pode ser interessante

A logica das "encalhadas" nao funciona porque cada sorteio eh independente.
Ja as "quentes" (muitos acertos de 11 E recentes) podem indicar combinacoes
que estao "proximas" aos padroes de numeros sorteados recentemente.
''')
