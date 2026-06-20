import pyodbc
import json
from collections import Counter

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;Connection Timeout=15;"
    "Query Timeout=30;MARS_Connection=yes;APP=LotoScope;"
)

conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

cursor.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
rows = cursor.fetchall()
conn.close()

dados = []
for r in rows:
    concurso = r[0]
    nums = set(r[1:])
    dados.append((concurso, nums))

print(f"Total de sorteios: {len(dados)}")
print()

#
# Analise: dos numeros que repetiram no sorteio anterior,
# quantos continuam repetindo no sorteio atual?
#
resultados = []
for i in range(2, len(dados)):
    conc_atual, nums_atual = dados[i]
    conc_ant, nums_ant = dados[i-1]
    conc_ant2, nums_ant2 = dados[i-2]

    # Numeros que repetiram do sorteio anterior para o atual
    repetiram_agora = nums_atual & nums_ant

    # Numeros que ja tinham repetido no sorteio anterior (ant2 -> ant)
    repetiram_antes = nums_ant & nums_ant2

    # Destes, quantos repetiram de novo?
    repetiram_de_novo = repetiram_antes & nums_atual

    resultados.append({
        'concurso': conc_atual,
        'num_rep_atuais': len(repetiram_agora),
        'num_rep_anteriores': len(repetiram_antes),
        'rep_que_continuaram': len(repetiram_de_novo),
        'pct': round(len(repetiram_de_novo) / len(repetiram_antes) * 100, 1) if repetiram_antes else 0,
        'nums_rep_ant': sorted(repetiram_antes),
        'nums_rep_continuaram': sorted(repetiram_de_novo),
    })

print("=== ANALISE: REPETICAO DOS REPETIDOS ===")
print()
print(f"Total de amostras (sorteios analisados): {len(resultados)}")
print()

# Distribuicao de quantos repetidos continuam
cont_continuaram = Counter(r['rep_que_continuaram'] for r in resultados)
print("Quantos numeros (dos que repetiram no anterior) continuam repetindo:")
for k in sorted(cont_continuaram):
    bar = '#' * cont_continuaram[k]
    print(f"  {k:2d} numeros: {cont_continuaram[k]:4d} sorteios ({cont_continuaram[k]/len(resultados)*100:5.1f}%) {bar}")

print()

# Media
media = sum(r['rep_que_continuaram'] for r in resultados) / len(resultados)
print(f"Media de repetidos-que-continuam: {media:.2f}")
print()

# Cruzamento: total de repetidos atuais x repetidos que continuaram
print("=== TABELA CRUZADA: Repetidos Anteriores x Continuaram ===")
print()
cab = "RepAnt |", [f"{i:2d}" for i in range(0, 16)]
print("RepAnt \\ Continuam", "  ".join(f"{i:2d}" for i in range(16)))
print("-" * 60)
cruzada = Counter()
for r in resultados:
    cruzada[(r['num_rep_anteriores'], r['rep_que_continuaram'])] += 1
for ra in sorted(set(k[0] for k in cruzada)):
    linha = [f"{ra:2d}    |"]
    for c in range(16):
        linha.append(f"{cruzada.get((ra, c), 0):2d}")
    print("  ".join(linha))

print()
print("=== EXEMPLOS ===")
for r in resultados[-10:]:
    print(f"  Conc {r['concurso']}: {r['num_rep_anteriores']} repetidos no anterior -> {r['rep_que_continuaram']} continuaram em {r['concurso']}")
    print(f"    Repetidos no anterior: {r['nums_rep_ant']}")
    print(f"    Continuaram:           {r['nums_rep_continuaram']}")
    print()

# Ultimo analise: dado que X numeros repetiram no anterior,
# qual a chance de pelo menos Y deles continuarem?
print("=== PROBABILIDADE CONDICIONAL ===")
print()
for n_rep_ant in sorted(set(r['num_rep_anteriores'] for r in resultados)):
    sub = [r for r in resultados if r['num_rep_anteriores'] == n_rep_ant]
    if len(sub) < 5:
        continue
    media_cond = sum(r['rep_que_continuaram'] for r in sub) / len(sub)
    p_metade = sum(1 for r in sub if r['rep_que_continuaram'] >= n_rep_ant / 2) / len(sub) * 100
    print(f"  Quando {n_rep_ant:2d} repetiram no anterior ({len(sub):3d} casos):")
    print(f"    Media que continuam: {media_cond:.2f}")
    print(f"    Chance de >= metade continuar: {p_metade:.0f}%")
    print()
