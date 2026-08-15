import sys; sys.path.insert(0, '.')
from lotofacil_lite.utils.database_config import db_config
conn = db_config.get_connection()
cursor = conn.cursor()

print('=== Resultados_Lotomania schema ===')
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Resultados_Lotomania' ORDER BY ORDINAL_POSITION")
for r in cursor.fetchall():
    print(f'  {r[0]:30s} {r[1]}')

print()
print('=== TOP 1 row ===')
cursor.execute("SELECT TOP 1 * FROM Resultados_Lotomania ORDER BY Concurso DESC")
cols = [d[0] for d in cursor.description]
row = cursor.fetchone()
if row:
    for k, v in zip(cols, row):
        print(f'  {k:30s} = {v}')

cursor.close()
conn.close()
