import pyodbc
import math
import statistics

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

# Conexao
conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()

# Ultimo concurso atualizado
for row in cur.execute("SELECT MAX(UltimoConcursoAtualizado) FROM COMBINACOES_LOTOFACIL"):
    ultimo_concurso = row[0]

# Total de sorteios historicos
for row in cur.execute("SELECT COUNT(*) FROM Resultados_INT"):
    total_sorteios = row[0]

print(f"Ultimo concurso atualizado: {ultimo_concurso}")
print(f"Total de sorteios historicos: {total_sorteios}")
print(f"Total de combinacoes: {3_268_760}")
print(f"Frequencia media esperada de 11 acertos: {total_sorteios / 3_268_760:.4f} por combinacao")

# metricas globais
print("\n--- Ranking por tendencia de acerto 11 ---")
print("Score = (Acertos_11 / media) + (Atraso / media_atraso)")
print("Quanto maior, mais 'devida' e historicamente frequente.\n")

# Carregar combinacoes com Acertos_11 > 0 (so as que ja acertaram 11 pelo menos 1x)
# Ordenar por score combinado
query = """
SELECT TOP 200
    ID,
    N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
    Acertos_11,
    Acertos_12,
    Acertos_13,
    Acertos_14,
    Acertos_15,
    Ultimo_Acertos_11,
    Ultimo_Acertos_12,
    Ultimo_Acertos_13,
    Ultimo_Acertos_14,
    Ultimo_Acertos_15,
    QtdePrimos, QtdeImpares, SomaTotal
FROM COMBINACOES_LOTOFACIL
WHERE Acertos_11 > 0
ORDER BY Acertos_11 DESC
"""

# Primeiro: calcular media de Acertos_11 e atraso para normalizar
print("Calculando medias...")
for row in cur.execute("""
    SELECT AVG(CAST(Acertos_11 AS FLOAT)), AVG(CAST(UltimoConcursoAtualizado - Ultimo_Acertos_11 AS FLOAT))
    FROM COMBINACOES_LOTOFACIL
    WHERE Acertos_11 > 0
"""):
    media_acertos_11 = row[0]
    media_atraso_11 = row[1]

print(f"Media Acertos_11 (combinacoes que ja acertaram): {media_acertos_11:.2f}")
print(f"Media de atraso (concursos desde ultimo 11): {media_atraso_11:.2f}")

# Ranking combinado: frequencia + atraso normalizado
score_query = """
SELECT TOP 50
    ID,
    N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
    Acertos_11,
    Acertos_12,
    Acertos_13,
    Acertos_14,
    Acertos_15,
    Ultimo_Acertos_11,
    Ultimo_Acertos_12,
    Ultimo_Acertos_13,
    Ultimo_Acertos_14,
    Ultimo_Acertos_15,
    QtdePrimos, QtdeImpares, SomaTotal,
    (CAST(Acertos_11 AS FLOAT) / ?) + (CAST(? - Ultimo_Acertos_11 AS FLOAT) / ?) AS score
FROM COMBINACOES_LOTOFACIL
WHERE Acertos_11 > 0
ORDER BY score DESC
"""

print("\n=== TOP 50 COMBINACOES COM MAIOR TENDENCIA (Score combinado) ===")
print(f"{'ID':>8} {'Combinacao':<50} {'11':>4} {'12':>4} {'13':>4} {'14':>4} {'15':>4} {'Atraso':>7} {'Score':>7}")
print("-" * 95)

for row in cur.execute(score_query, (media_acertos_11, ultimo_concurso, media_atraso_11)):
    idc = row[0]
    nums = row[1:16]
    a11, a12, a13, a14, a15 = row[16], row[17], row[18], row[19], row[20]
    u11, u12, u13, u14, u15 = row[21], row[22], row[23], row[24], row[25]
    score = row[29]
    nums_str = " ".join(f"{n:02d}" for n in nums)
    atraso = ultimo_concurso - u11
    print(f"{idc:>8} {nums_str:<50} {a11:>4} {a12:>4} {a13:>4} {a14:>4} {a15:>4} {atraso:>7} {score:>7.2f}")

# Analise: combinacoes com mais de 300 acertos de 11
print("\n=== COMBINACOES COM > 300 ACERTOS DE 11 ===")
for row in cur.execute("SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL WHERE Acertos_11 > 300"):
    qtd = row[0]
print(f"Quantidade: {qtd}")

print("\n=== TOP 20 MAIS FREQUENTES (11 acertos) ===")
print(f"{'ID':>8} {'Combinacao':<50} {'11':>4} {'12':>4} {'13':>4} {'14':>4} {'15':>4} {'Ultimo 11':>10}")
print("-" * 95)
for row in cur.execute("""
    SELECT TOP 20
        ID, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
        Acertos_11, Acertos_12, Acertos_13, Acertos_14, Acertos_15,
        Ultimo_Acertos_11
    FROM COMBINACOES_LOTOFACIL
    ORDER BY Acertos_11 DESC
"""):
    idc = row[0]
    nums = row[1:16]
    a11, a12, a13, a14, a15 = row[16], row[17], row[18], row[19], row[20]
    u11 = row[21]
    nums_str = " ".join(f"{n:02d}" for n in nums)
    print(f"{idc:>8} {nums_str:<50} {a11:>4} {a12:>4} {a13:>4} {a14:>4} {a15:>4} {u11:>10}")

# Estatisticas descritivas
print("\n=== ESTATISTICAS DESCRITIVAS ===")
for row in cur.execute("""
    SELECT
        MIN(Acertos_11), MAX(Acertos_11), AVG(CAST(Acertos_11 AS FLOAT)),
        MIN(Ultimo_Acertos_11), MAX(Ultimo_Acertos_11)
    FROM COMBINACOES_LOTOFACIL
    WHERE Acertos_11 > 0
"""):
    print(f"Acertos_11 (min/max/media): {row[0]} / {row[1]} / {row[2]:.2f}")
    print(f"Ultimo_Acertos_11 (min/max): {row[3]} / {row[4]}")

print("\n=== CUIDADO ===")
print("Loteria e independente entre sorteios. Atraso alto NAO garante que a combinacao saira.")
print("Este ranking mede padroes historicos, nao probabilidade futura garantida.")
