import itertools
import math
import statistics

hipotese = (1, 2, 4, 6, 7, 10, 11, 13, 15, 18, 19, 20, 22, 24, 25)
N = 25  # numeros de 1 a 25
K = 15  # escolhe 15

total_combinacoes = math.comb(N, K)
print(f"Total de combinacoes da Lotofacil: {total_combinacoes:,}")
print(f"Hipotese de referencia: {hipotese}")
print("Analisando 2-7 acertos posicionais como redutor...")

dist = {i: 0 for i in range(16)}
validas = 0

for comb in itertools.combinations(range(1, N + 1), K):
    acertos = sum(1 for i in range(K) if comb[i] == hipotese[i])
    dist[acertos] += 1
    if 2 <= acertos <= 7:
        validas += 1

print("\nDistribuicao absoluta no universo total:")
for k, v in sorted(dist.items()):
    pct = 100.0 * v / total_combinacoes
    bar = "#" * int(round(pct / 0.5))
    print(f"  {k:2d} acertos: {v:>9,} ({pct:6.2f}%) {bar}")

print(f"\nCombinacoes dentro da faixa 2-7 acertos: {validas:,}")
print(f"Reducao: {100.0 * validas / total_combinacoes:.2f}% do universo total")
print(f"Fator de reducao: {total_combinacoes / validas:.1f}x")

# verificar: 90% dos sorteios historicos caiam nessa faixa
print("\n--- Validacao contra sorteios historicos ---")
import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

cols = [f"N{i}" for i in range(1, 16)]
conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()
cur.execute("SELECT " + ",".join(cols) + " FROM Resultados_INT")

hist_dentro = 0
hist_fora = 0
for row in cur.fetchall():
    nums = tuple(int(row[i]) for i in range(15))
    acertos = sum(1 for i in range(15) if nums[i] == hipotese[i])
    if 2 <= acertos <= 7:
        hist_dentro += 1
    else:
        hist_fora += 1

hist_total = hist_dentro + hist_fora
print(f"Sorteios historicos dentro da faixa 2-7: {hist_dentro}/{hist_total} ({100.0*hist_dentro/hist_total:.2f}%)")
print(f"Sorteios historicos FORA da faixa: {hist_fora} ({100.0*hist_fora/hist_total:.2f}%)")

# simular: se usassemos esse filtro, quantas combinacoes teriamos apostado e quantas acertariam
print("\n--- Simulacao de aplicacao do filtro em todos os sorteios ---")
# Probabilidade de acertar com o filtro (reducao mantem proporcionalidade se o filtro for neutro)
prob_15 = 1 / validas
prob_14 = math.comb(15, 14) * (25 - 15) / validas
prob_13 = math.comb(15, 13) * math.comb(10, 2) / validas

print(f"Chance de acertar 15 com reducao: 1 em {validas:,}")
print(f"Chance de acertar 14 com reducao: 1 em {int(1/prob_14) if prob_14 else 'infinito'}")
print(f"Chance de acertar 13 com reducao: 1 em {int(1/prob_13) if prob_13 else 'infinito'}")

print("\nConclusao:")
if validas < total_combinacoes:
    print(f"O filtro reduz o universo de {total_combinacoes:,} para {validas:,} ({total_combinacoes/validas:.1f}x).")
    print(f"Ele cobre {100.0*hist_dentro/hist_total:.2f}% dos sorteios historicos.")
else:
    print("O filtro nao reduz nada.")
