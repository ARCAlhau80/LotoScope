# -*- coding: utf-8 -*-
"""
Correção do double-counting em COMBINACOES_LOTOFACIL.
Causa: Trigger ATIVO + Procedure executada manualmente = Acertos_* 2x o valor real.
Solução:
  1. Desabilitar o trigger para evitar futuros double-counts
  2. Dividir Acertos_11..15 por 2
"""
import sys, pyodbc, time
sys.stdout.reconfigure(encoding='utf-8')

CONN = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(CONN)
conn.autocommit = True
cur = conn.cursor()

print("=== CORREÇÃO DE DOUBLE-COUNTING EM COMBINACOES_LOTOFACIL ===\n")

# PASSO 1: Desabilitar o trigger
print("PASSO 1: Desabilitando trigger trg_AtualizarAcertos_LF15_AfterInsert...")
try:
    cur.execute("DISABLE TRIGGER trg_AtualizarAcertos_LF15_AfterInsert ON Resultados_INT")
    print("  ✅ Trigger DESABILITADO com sucesso!\n")
except Exception as e:
    print(f"  ⚠️ Erro ao desabilitar trigger: {e}\n")

# PASSO 2: Verificar estado atual antes da correção
print("PASSO 2: Estado ANTES da correção:")
cur.execute("SELECT AVG(CAST(Acertos_11 AS FLOAT)), AVG(CAST(Acertos_12 AS FLOAT)), AVG(CAST(Acertos_13 AS FLOAT)) FROM COMBINACOES_LOTOFACIL")
row = cur.fetchone()
print(f"  AVG Acertos_11={row[0]:.2f}, Acertos_12={row[1]:.2f}, Acertos_13={row[2]:.2f}")
print(f"  (Esperado correto: A11≈322, A12≈61, A13≈5.3)\n")

# PASSO 3: Dividir por 2 (corrigir double-counting)
print("PASSO 3: Dividindo Acertos_* por 2 (3.2M linhas, pode demorar 1-3 min)...")
t0 = time.time()

# Usar UPDATE em lotes para evitar lock timeout
# SQL Server pode travar em UPDATE de 3.2M linhas sem lote
BATCH = 500_000
cur.execute("SELECT MIN(ID), MAX(ID) FROM COMBINACOES_LOTOFACIL")
min_id, max_id = cur.fetchone()
print(f"  Range de IDs: {min_id} até {max_id}")

total_atualizado = 0
id_atual = min_id
while id_atual <= max_id:
    id_fim = min(id_atual + BATCH - 1, max_id)
    cur.execute(f"""
        UPDATE COMBINACOES_LOTOFACIL
        SET 
            Acertos_11 = Acertos_11 / 2,
            Acertos_12 = Acertos_12 / 2,
            Acertos_13 = Acertos_13 / 2,
            Acertos_14 = Acertos_14 / 2,
            Acertos_15 = Acertos_15 / 2
        WHERE ID BETWEEN {id_atual} AND {id_fim}
    """)
    affected = cur.rowcount
    total_atualizado += affected
    pct = (id_fim - min_id + 1) / (max_id - min_id + 1) * 100
    elapsed = time.time() - t0
    print(f"  IDs {id_atual}-{id_fim}: {affected:,} linhas atualizadas ({pct:.1f}%, {elapsed:.1f}s)")
    id_atual = id_fim + 1

elapsed_total = time.time() - t0
print(f"\n  ✅ Total atualizado: {total_atualizado:,} linhas em {elapsed_total:.1f}s")

# PASSO 4: Verificar resultado
print("\nPASSO 4: Estado DEPOIS da correção:")
cur.execute("SELECT AVG(CAST(Acertos_11 AS FLOAT)), AVG(CAST(Acertos_12 AS FLOAT)), AVG(CAST(Acertos_13 AS FLOAT)) FROM COMBINACOES_LOTOFACIL")
row = cur.fetchone()
print(f"  AVG Acertos_11={row[0]:.2f}, Acertos_12={row[1]:.2f}, Acertos_13={row[2]:.2f}")
print(f"  (Esperado correto: A11≈322, A12≈61, A13≈5.3)")

# Verificar combo ID=1
cur.execute("SELECT Acertos_11, Acertos_12, Acertos_13 FROM COMBINACOES_LOTOFACIL WHERE ID=1")
row = cur.fetchone()
print(f"\n  Combo ID=1: A11={row[0]}, A12={row[1]}, A13={row[2]}")
print(f"  (CALC real: A11=334, A12=55, A13=5 → após /2: ~334, 55, 5)")

# Status do trigger
print("\nPASSO 5: Status dos triggers:")
cur.execute("SELECT name, is_disabled FROM sys.triggers WHERE name LIKE '%AtualizarAcertos%'")
for r in cur.fetchall():
    status = "✅ DESABILITADO" if r[1] else "⚠️ ATIVO"
    print(f"  {r[0]}: {status}")

conn.close()
print("\n=== CORREÇÃO CONCLUÍDA ===")
