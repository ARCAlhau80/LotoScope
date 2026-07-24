import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()

for row in cur.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL'
    ORDER BY ORDINAL_POSITION
"""):
    print(f"{row[0]:25} {row[1]:15} nullable={row[2]} len={row[3]}")

print("\n--- sample rows ---")
for row in cur.execute("SELECT TOP 5 * FROM COMBINACOES_LOTOFACIL"):
    print(row)

print("\n--- total rows ---")
for row in cur.execute("SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL"):
    print(row[0])
