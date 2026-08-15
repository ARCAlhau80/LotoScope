import json
from collections import Counter
from statistics import mean

# Resultado manual do concurso 3745 conforme usuario
CONCURSO_3744 = {1, 2, 3, 5, 7, 10, 14, 16, 17, 18, 20, 21, 22, 23, 24}
CONCURSO_3745 = {1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13, 19, 21, 22, 24}

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}


def pares(nums): return {n for n in nums if n % 2 == 0}
def impares(nums): return {n for n in nums if n % 2 == 1}
def consecutivos(nums):
    s = set(nums)
    return {(a, a+1) for a in s if (a+1) in s}

# Carga do historico completo
import pyodbc
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()
cur.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
rows = cur.fetchall()
sorteios = [(r[0], set(r[1:16])) for r in rows]

# Historico de repeticoes
hist_repeticoes_geral = []
hist_repeticoes_pares = []
hist_repeticoes_impares = []
hist_repeticoes_primos = []
hist_repeticoes_fib = []
hist_repeticoes_cons = []

for i in range(1, len(sorteios)):
    ant, atu = sorteios[i-1][1], sorteios[i][1]
    hist_repeticoes_geral.append(len(ant & atu))
    hist_repeticoes_pares.append(len(pares(ant) & pares(atu)))
    hist_repeticoes_impares.append(len(impares(ant) & impares(atu)))
    hist_repeticoes_primos.append(len((ant & PRIMOS) & (atu & PRIMOS)))
    hist_repeticoes_fib.append(len((ant & FIBONACCI) & (atu & FIBONACCI)))
    hist_repeticoes_cons.append(len(consecutivos(ant) & consecutivos(atu)))

# Calcular caso 3744->3745
r_geral = len(CONCURSO_3744 & CONCURSO_3745)
r_pares = len(pares(CONCURSO_3744) & pares(CONCURSO_3745))
r_impares = len(impares(CONCURSO_3744) & impares(CONCURSO_3745))
r_primos = len((CONCURSO_3744 & PRIMOS) & (CONCURSO_3745 & PRIMOS))
r_fib = len((CONCURSO_3744 & FIBONACCI) & (CONCURSO_3745 & FIBONACCI))
r_cons = len(consecutivos(CONCURSO_3744) & consecutivos(CONCURSO_3745))

print(f"=== Caso 3744 -> 3745 ===")
print(f"Concurso 3744: {sorted(CONCURSO_3744)}")
print(f"Concurso 3745: {sorted(CONCURSO_3745)}")
print(f"Repetidos geral: {r_geral} | historico mean: {mean(hist_repeticoes_geral):.2f}")
print(f"Repetidos pares: {r_pares} | historico mean: {mean(hist_repeticoes_pares):.2f}")
print(f"Repetidos impares: {r_impares} | historico mean: {mean(hist_repeticoes_impares):.2f}")
print(f"Repetidos primos: {r_primos} | historico mean: {mean(hist_repeticoes_primos):.2f}")
print(f"Repetidos fibonacci: {r_fib} | historico mean: {mean(hist_repeticoes_fib):.2f}")
print(f"Repetidos consecutivos (pares): {r_cons} | historico mean: {mean(hist_repeticoes_cons):.2f}")


def pct_atleast_or_equal(arr, value):
    return sum(1 for x in arr if x >= value) / len(arr) * 100


def pct_exact(arr, value):
    return sum(1 for x in arr if x == value) / len(arr) * 100


def show(name, val, hist):
    c = Counter(hist)
    print(f"\n--- {name}: valor={val} ---")
    print(f"  exatamente {val}: {pct_exact(hist, val):.2f}%")
    print(f"  pelo menos {val}: {pct_atleast_or_equal(hist, val):.2f}%")
    print(f"  distribuicao: {dict(sorted(c.items()))}")

show("Geral", r_geral, hist_repeticoes_geral)
show("Pares", r_pares, hist_repeticoes_pares)
show("Impares", r_impares, hist_repeticoes_impares)
show("Primos", r_primos, hist_repeticoes_primos)
show("Fibonacci", r_fib, hist_repeticoes_fib)
show("Consecutivos", r_cons, hist_repeticoes_cons)

# Analise cruzada: quando repetem 4 pares, quantos impares repetem?
print("\n=== Cruzamento: quando pares repetem 4, distribuicao de impares repetidos ===")
cruz_pares_4 = Counter()
for i in range(1, len(sorteios)):
    ant, atu = sorteios[i-1][1], sorteios[i][1]
    if len(pares(ant) & pares(atu)) == 4:
        cruz_pares_4[len(impares(ant) & impares(atu))] += 1
print(dict(sorted(cruz_pares_4.items())))

# Cruzamento: quando impares repetem 4, quantos primos repetem?
print("\n=== Cruzamento: quando impares repetem 4, distribuicao de primos repetidos ===")
cruz_imp_4 = Counter()
for i in range(1, len(sorteios)):
    ant, atu = sorteios[i-1][1], sorteios[i][1]
    if len(impares(ant) & impares(atu)) == 4:
        cruz_imp_4[len((ant & PRIMOS) & (atu & PRIMOS))] += 1
print(dict(sorted(cruz_imp_4.items())))
