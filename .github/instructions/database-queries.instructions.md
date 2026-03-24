---
description: "Use when writing SQL queries against the Lotofacil SQL Server database, building pyodbc queries for Resultados_INT table, fetching draw results, calculating frequencies or patterns from historical data, or working with the COMBINACOES_LOTOFACIL table. Covers table schema, safe query patterns, and performance tips for the 3.2M row combinations table."
name: "Database Queries — LotoScope"
---

# Database Queries — LotoScope SQL Server

## Conexão (Sempre Usar Este Padrão)

```python
import pyodbc

CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Lotofacil;'
    'Trusted_Connection=yes;'
)

# Forma segura (com context manager):
with pyodbc.connect(CONN_STR) as conn:
    conn.autocommit = False  # Para operações de escrita
    cursor = conn.cursor()
    # ...
    conn.commit()
```

## Schema: Tabela Resultados_INT

```sql
CREATE TABLE Resultados_INT (
    Concurso        INT PRIMARY KEY,   -- 1 a ~3640
    N1              INT,               -- Números por posição (1-25)
    N2              INT,
    N3              INT,
    N4              INT,
    N5              INT,
    N6              INT,
    N7              INT,
    N8              INT,
    N9              INT,
    N10             INT,
    N11             INT,
    N12             INT,
    N13             INT,
    N14             INT,
    N15             INT,
    Data_Sorteio    VARCHAR(20),
    -- 21+ campos estatísticos (ex: QtdeGaps, SomaNumeros, QtdePares, etc.)
)
```

## Queries Frequentes

### Último concurso
```python
cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
ultimo = cursor.fetchone()[0]
```

### Resultado de um concurso específico
```python
cursor.execute("""
    SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT WHERE Concurso = ?
""", (numero_concurso,))
row = cursor.fetchone()
numeros = list(row) if row else None
```

### Últimos N concursos (mais recentes primeiro)
```python
cursor.execute("""
    SELECT TOP (?) Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT
    ORDER BY Concurso DESC
""", (n,))
resultados = cursor.fetchall()
```

### Range de concursos
```python
cursor.execute("""
    SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT
    WHERE Concurso BETWEEN ? AND ?
    ORDER BY Concurso ASC
""", (inicio, fim))
```

### Frequência de números (últimos N concursos)
```python
cursor.execute("""
    SELECT num, COUNT(*) AS freq
    FROM (
        SELECT N1 AS num FROM Resultados_INT WHERE Concurso > ?
        UNION ALL SELECT N2 FROM Resultados_INT WHERE Concurso > ?
        -- ... N3 a N15
    ) t
    GROUP BY num
    ORDER BY freq DESC
""", (limite, limite, ...))
```

## Tabela COMBINACOES_LOTOFACIL (3.2M registros)

```sql
-- Atenção: queries sem índice = LENTÍSSIMAS
-- SEMPRE usar WHERE com campos indexados ou TOP para limitar resultado

-- Busca de combinação específica (use parâmetros, nunca string format):
cursor.execute("""
    SELECT Acertos_11, Acertos_12, Acertos_13, Acertos_14, Acertos_15
    FROM COMBINACOES_LOTOFACIL
    WHERE N1=? AND N2=? AND N3=? AND N4=? AND N5=?
      AND N6=? AND N7=? AND N8=? AND N9=? AND N10=?
      AND N11=? AND N12=? AND N13=? AND N14=? AND N15=?
""", tuple(sorted(combo)))
```

## Padrões de Segurança

```python
# ✅ SEMPRE usar parâmetros (previne SQL injection):
cursor.execute("SELECT * FROM Resultados_INT WHERE Concurso = ?", (num,))

# ❌ NUNCA concatenar strings para queries:
# cursor.execute(f"SELECT * FROM Resultados_INT WHERE Concurso = {num}")

# ✅ Fechar conexão após uso (ou usar context manager):
conn.close()

# ✅ Tratar erro de conexão:
try:
    conn = pyodbc.connect(CONN_STR)
except pyodbc.Error as e:
    print(f"❌ Erro ao conectar ao banco: {e}")
    return None
```

## Performance

```python
# Para leituras em bulk (ex: todos os 3640 concursos):
cursor.fast_executemany = True  # Para inserts em batch

# Fetchall vs fetchmany para grandes volumes:
cursor.execute("SELECT ... FROM Resultados_INT")
while True:
    rows = cursor.fetchmany(1000)  # 1000 por vez
    if not rows:
        break
    # processar rows

# Converter resultado para lista de sets rapidamente:
resultados = [set(row[1:16]) for row in cursor.fetchall()]
```
