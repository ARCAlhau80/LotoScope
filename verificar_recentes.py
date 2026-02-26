"""
Verificar último concurso onde a combinação vencedora teve 11+ acertos
"""
import pyodbc

# Combinação vencedora
vencedora = set([1,2,7,8,10,11,13,14,16,18,19,20,23,24,25])
print(f'Combinação vencedora: {sorted(vencedora)}')

# Carregar histórico
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Pegar todos os resultados (do mais recente para o mais antigo)
cursor.execute('''
    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    WHERE Concurso < 3619
    ORDER BY Concurso DESC
''')

resultados = []
for row in cursor.fetchall():
    resultados.append({
        'concurso': row[0],
        'numeros': set(row[1:16])
    })
conn.close()

# Encontrar último concurso com 11+ acertos
ultimo_11_mais = None
concursos_sem_11 = 0

for r in resultados:
    acertos = len(vencedora & r['numeros'])
    if acertos >= 11:
        ultimo_11_mais = r['concurso']
        break
    concursos_sem_11 += 1

print(f'\n📊 ANÁLISE DE RECENTES:')
print(f'   Último concurso analisado: {resultados[0]["concurso"]}')
print(f'   Último concurso com 11+ acertos: {ultimo_11_mais}')
print(f'   Concursos sem 11+ (desde o último): {concursos_sem_11}')

# Mostrar os últimos 10 concursos e seus acertos
print(f'\n📋 ÚLTIMOS 10 CONCURSOS:')
for r in resultados[:10]:
    acertos = len(vencedora & r['numeros'])
    status = "✅ 11+" if acertos >= 11 else ""
    print(f'   {r["concurso"]}: {acertos} acertos {status}')

# Verificar se passaria nos filtros de recentes
print(f'\n🔍 PASSARIA EM FILTRO "RECENTES"?')
for max_sem_11 in [5, 10, 15, 20, 30, 50]:
    passa = "PASSA ✅" if concursos_sem_11 <= max_sem_11 else f"FALHA ❌ ({concursos_sem_11} > {max_sem_11})"
    print(f'   Máx {max_sem_11} concursos sem 11+: {passa}')
