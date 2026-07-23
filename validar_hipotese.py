import pyodbc, statistics, json

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

hipotese = [1, 2, 4, 6, 7, 10, 11, 13, 15, 18, 19, 20, 22, 24, 25]
cols = [f"N{i}" for i in range(1, 16)]

conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()
cur.execute("SELECT Concurso, " + ",".join(cols) + " FROM Resultados_INT ORDER BY Concurso")

acertos_por_sorteio = []
linhas = []
for row in cur.fetchall():
    nums = [int(row[i + 1]) for i in range(15)]
    acertos = sum(1 for i in range(15) if nums[i] == hipotese[i])
    acertos_por_sorteio.append(acertos)
    linhas.append(nums)

total = len(acertos_por_sorteio)
min_a = min(acertos_por_sorteio)
max_a = max(acertos_por_sorteio)
media = statistics.mean(acertos_por_sorteio)
mediana = statistics.median(acertos_por_sorteio)
stdev = statistics.stdev(acertos_por_sorteio) if total > 1 else 0.0

dist = {i: 0 for i in range(16)}
for a in acertos_por_sorteio:
    dist[a] += 1

print("=" * 70)
print("HIPOTESE: acertos posicionais exatos N1..N15")
print("Combinacao:", hipotese)
print("=" * 70)
print(f"Total de sorteios analisados: {total}")
print(f"Minimo de acertos posicionais: {min_a}")
print(f"Maximo de acertos posicionais: {max_a}")
print(f"Media: {media:.2f}")
print(f"Mediana: {mediana}")
print(f"Desvio padrao: {stdev:.2f}")
print("-" * 70)
print("Distribuicao de acertos POSICIONAIS:")
for k, v in sorted(dist.items()):
    pct = 100.0 * v / total
    bar = "#" * int(round(pct / 1.5))
    print(f"  {k:2d} acertos: {v:4d} ({pct:5.2f}%) {bar}")

print("\n" + "=" * 70)
print("Se voce jogasse essa combinacao fixa em todos os sorteios:")
print("=" * 70)
pontuacao = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
for nums in linhas:
    acertos_set = len(set(nums) & set(hipotese))
    if acertos_set >= 11:
        pontuacao[acertos_set] += 1

for p, q in sorted(pontuacao.items()):
    pct = 100.0 * q / total
    print(f"  {p:2d} acertos: {q:4d} ({pct:5.2f}%)")

premios_estimados = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
# estimativas aproximadas da Lotofacil (valores medios historicos)
premios_medios = {11: 5, 12: 10, 13: 25, 14: 1200, 15: 1500000}
print("\nEstimativa de retorno (valores aproximados, R$):")
for p, q in sorted(pontuacao.items()):
    total_rs = q * premios_medios[p]
    premios_estimados[p] = total_rs
    print(f"  {p:2d} acertos x ~R$ {premios_medios[p]:>12,} = R$ {total_rs:>15,.0f}")

print(f"  Investimento total: R$ {total * 2.50:,.2f} (R$ 2,50 por jogo)")
print(f"  Retorno estimado:   R$ {sum(premios_estimados.values()):,.2f}")
print(f"  Saldo estimado:     R$ {sum(premios_estimados.values()) - total * 2.50:,.2f}")
