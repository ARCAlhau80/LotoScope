"""
Verificar Acertos_11 da combinação vencedora do concurso 3619
"""
import pyodbc

# Combinação vencedora
vencedora = tuple(sorted([1,2,7,8,10,11,13,14,16,18,19,20,23,24,25]))
print(f'Combinação vencedora: {vencedora}')

# Carregar histórico
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Pegar todos os resultados (exceto o atual 3619)
cursor.execute('''
    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    WHERE Concurso < 3619
    ORDER BY Concurso DESC
''')

resultados = []
for row in cursor.fetchall():
    resultados.append(set(row[1:16]))
conn.close()

print(f'Total de concursos para análise: {len(resultados)}')

# Calcular Acertos_11 (quantas vezes teve 11+ acertos)
acertos_11_mais = 0
detalhes = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}

for resultado in resultados:
    acertos = len(set(vencedora) & resultado)
    if acertos >= 11:
        acertos_11_mais += 1
        detalhes[acertos] += 1

print(f'\n📊 HISTÓRICO DA COMBINAÇÃO VENCEDORA:')
print(f'   Acertos_11 (total 11+ hits): {acertos_11_mais}')
print(f'   Detalhes:')
for ac, qtd in detalhes.items():
    if qtd > 0:
        print(f'      {ac} acertos: {qtd} vezes')

# Comparar com threshold
print(f'\n🔍 COMPARAÇÃO COM THRESHOLDS:')
if acertos_11_mais >= 313:
    print(f'   [1] Conservador (>=313): PASSA ✅')
else:
    print(f'   [1] Conservador (>=313): FALHA ❌ ({acertos_11_mais} < 313)')

if acertos_11_mais >= 320:
    print(f'   [2] Moderado (>=320): PASSA ✅')
else:
    print(f'   [2] Moderado (>=320): FALHA ❌ ({acertos_11_mais} < 320)')

if acertos_11_mais >= 330:
    print(f'   [3] Agressivo (>=330): PASSA ✅')
else:
    print(f'   [3] Agressivo (>=330): FALHA ❌ ({acertos_11_mais} < 330)')

# Verificar qual threshold foi usado (baseado em 75,582 combos = ~15.4% de 490,314)
print(f'\n💡 DIAGNÓSTICO:')
print(f'   Nível 0 tinha 75,582 combinações (15.4% de 490,314)')
print(f'   Isso indica que o filtro probabilístico estava MUITO AGRESSIVO')
print(f'   Provavelmente threshold >= 350+ foi usado!')

# Verificar se passaria com threshold mais baixo
for threshold in [300, 310, 320, 330, 340, 350, 360]:
    passa = 'PASSA' if acertos_11_mais >= threshold else 'FALHA'
    print(f'   Threshold {threshold}: {passa}')
