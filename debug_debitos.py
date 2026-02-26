"""
DEBUG: Análise de frequência por posição vs frequência geral
"""
import pyodbc
from collections import defaultdict

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute('''
    SELECT TOP 5 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    ORDER BY Concurso DESC
''')

resultados = []
for row in cursor.fetchall():
    resultados.append({
        'concurso': row[0],
        'numeros': list(row[1:16])
    })
conn.close()

print('ÚLTIMOS 5 CONCURSOS:')
print('='*80)

# Contar frequência GERAL do número
freq_geral = defaultdict(int)
# Contar frequência POR POSIÇÃO
freq_posicao = defaultdict(lambda: defaultdict(int))

for r in resultados:
    print(f"Concurso {r['concurso']}:")
    for pos in range(15):
        num = r['numeros'][pos]
        freq_geral[num] += 1
        freq_posicao[num][pos+1] += 1
    
    # Mostrar números ordenados
    nums_sorted = sorted(r['numeros'])
    print(f"  Números: {nums_sorted}")
    
    # Mostrar por posição
    posicoes = [f"N{i+1}:{r['numeros'][i]:02d}" for i in range(15)]
    print(f"  Posições: {posicoes}")
    print()

print('='*80)
print('\n🔍 ANÁLISE DO NÚMERO 24:')
print(f"  Frequência GERAL (saiu em {freq_geral[24]} dos 5 concursos): {freq_geral[24]/5*100:.1f}%")
print(f"  Frequência por POSIÇÃO:")
for pos in range(1, 16):
    f = freq_posicao[24][pos]
    if f > 0:
        print(f"    N{pos:02d}: {f}x = {f/5*100:.1f}%")
    else:
        # Verificar se a média histórica é alta para esta posição
        pass
print(f"  Posições onde NÃO saiu (freq_recente = 0%):")
for pos in range(1, 16):
    if freq_posicao[24][pos] == 0:
        print(f"    N{pos:02d}: 0x = 0.0%")

print()
print('🔍 ANÁLISE DO NÚMERO 20:')
print(f"  Frequência GERAL (saiu em {freq_geral[20]} dos 5 concursos): {freq_geral[20]/5*100:.1f}%")
print(f"  Frequência por POSIÇÃO:")
for pos in range(1, 16):
    f = freq_posicao[20][pos]
    if f > 0:
        print(f"    N{pos:02d}: {f}x = {f/5*100:.1f}%")

print('\n' + '='*80)
print('💡 EXPLICAÇÃO:')
print('='*80)
print('''
O DÉBITO POSICIONAL analisa POSIÇÃO ESPECÍFICA, não frequência geral!

Exemplo: Número 24 pode ter saído 2x nos últimos 5 concursos, MAS:
  - Se saiu na posição N12 (1x) e N13 (1x)
  - Na posição N14, saiu 0 vezes = 0.0% freq_recente
  - Se a média histórica de 24 em N14 é 36.9%
  - Então o DÉFICIT é 36.9% - 0% = +36.9%

Isso significa que o número 24 "costuma aparecer" na posição N14 em 36.9% 
dos sorteios históricos, mas nos últimos 5 não apareceu NENHUMA VEZ nessa 
posição específica. Por isso está em "débito" para essa posição.
''')
