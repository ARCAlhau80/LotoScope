# -*- coding: utf-8 -*-
"""Get proc definition and verify current state"""
import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

# Full proc definition
cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('PROC_ATUALIZAR_COMBIN_10'))")
proc = cursor.fetchone()[0]
print("=== PROC DEFINITION ===")
print(proc)
print(f"\n--- Length: {len(proc)} chars ---")

# Current state
print("\n=== CURRENT STATE ===")
cursor.execute("SELECT MAX(CONCURSO) FROM COMBIN_10")
print(f"COMBIN_10 MAX(CONCURSO): {cursor.fetchone()[0]}")

cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
print(f"Resultados_INT MAX(Concurso): {cursor.fetchone()[0]}")

# Verify the 2x issue with a few samples
print("\n=== MANUAL VERIFICATION (5 samples) ===")
cursor.execute("SELECT TOP 5 N1,N2,N3,N4,N5,N6,N7,N8,N9,N10, QTDE_ACERTOS FROM COMBIN_10 WHERE QTDE_ACERTOS > 0 ORDER BY ID_COMBIN")
for row in cursor.fetchall():
    nums = list(row[:10])
    tabela_acertos = row[10]
    
    # Count manually
    conditions = ' AND '.join([f'{n} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)' for n in nums])
    cursor.execute(f"SELECT COUNT(*) FROM Resultados_INT WHERE {conditions}")
    real = cursor.fetchone()[0]
    
    ratio = tabela_acertos / real if real > 0 else 'N/A'
    print(f"  {nums} → tabela={tabela_acertos}, real={real}, ratio={ratio}")

conn.close()
