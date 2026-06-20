import pyodbc
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

total = len(rows)
dados = []
for r in rows:
    dados.append((r[0], list(r[1:]), set(r[1:])))

print(f"Total de sorteios: {total}")
print()

JANELA = 30
THRESHOLD = 1.5

# Pre-computar freq total cumulativa e freq em janela deslizante
freq30 = [Counter() for _ in range(total)]
freq_total_cum = Counter()

for idx in range(total):
    if idx == 0:
        freq30[idx] = Counter(dados[idx][1])
    elif idx < JANELA:
        freq30[idx] = freq30[idx-1] + Counter(dados[idx][1])
    else:
        freq30[idx] = freq30[idx-1] + Counter(dados[idx][1]) - Counter(dados[idx - JANELA][1])

    if idx < total:
        freq_total_cum.update(dados[idx][1])

# Detectar eventos aquecendo
# otimizacao: so calcular nos ultimos 500 concursos + amostra
TOTAL_ANALISE = min(500, total - JANELA)
START_IDX = total - TOTAL_ANALISE

eventos_aquecendo = []
for idx in range(START_IDX, total):
    f30 = freq30[idx]
    freq_esp = {n: freq_total_cum.get(n, 0) / total * JANELA for n in range(1, 26)}

    for n in range(1, 26):
        diff = f30.get(n, 0) - freq_esp[n]
        if diff > THRESHOLD:
            eventos_aquecendo.append((idx, n, f30.get(n, 0), diff))

print(f"Total de eventos 'aquecendo' (ultimos {TOTAL_ANALISE} concursos): {len(eventos_aquecendo)}")
print()

if not eventos_aquecendo:
    print("Nenhum evento aquecendo encontrado no periodo.")
    exit()

# Analisar aparicao nos proximos 10 sorteios
max_futuro = 10
analise = []
for idx, n, freq, diff in eventos_aquecendo:
    contagens = []
    for offset in range(1, max_futuro + 1):
        if idx + offset < total:
            contagens.append(1 if n in dados[idx + offset][2] else 0)
        else:
            contagens.append(None)
    analise.append({
        'concurso': dados[idx][0],
        'numero': n,
        'diff': diff,
        'total_10': sum(c for c in contagens if c is not None),
    })

# Distribuicao de aparicoes nos proximos 10
dist = Counter(r['total_10'] for r in analise)
print("=== QUANTAS VEZES UM NUMERO 'AQUECENDO' APARECE NOS PROXIMOS 10 SORTEIOS ===")
print()
for k in sorted(dist):
    pct = dist[k] / len(analise) * 100
    print(f"  {k:2d}/10: {dist[k]:5d} casos ({pct:5.1f}%)")

media_geral = sum(r['total_10'] for r in analise) / len(analise)
print(f"\nMedia de aparicoes nos 10 seguintes: {media_geral:.2f}/10")
print()

# Probabilidade por offset
print("=== PROBABILIDADE DE APARECER EM CADA SORTEIO FUTURO ===")
print()
for offset in range(1, max_futuro + 1):
    col = [r for r in analise if r.get(f'offset_{offset}') is not None]
    apareceu = sum(1 for r in analise if True)  # recalc
apareceu_counts = {offset: 0 for offset in range(1, max_futuro + 1)}
total_counts = {offset: 0 for offset in range(1, max_futuro + 1)}

for idx, n, freq, diff in eventos_aquecendo:
    for offset in range(1, max_futuro + 1):
        if idx + offset < total:
            total_counts[offset] += 1
            if n in dados[idx + offset][2]:
                apareceu_counts[offset] += 1

for offset in range(1, max_futuro + 1):
    pct = apareceu_counts[offset] / total_counts[offset] * 100
    bar = '#' * int(pct / 2)
    print(f"  +{offset:2d}: {apareceu_counts[offset]:5d}/{total_counts[offset]:5d} = {pct:5.1f}% {bar}")

print()

# Quantos numeros aquecendo por concurso
aq_por_concurso = Counter()
for idx in range(START_IDX, total):
    qtd = sum(1 for e in eventos_aquecendo if e[0] == idx)
    if qtd > 0:
        aq_por_concurso[qtd] += 1

print("=== NUMEROS AQUECENDO SIMULTANEAMENTE ===")
print()
for k in sorted(aq_por_concurso):
    pct = aq_por_concurso[k] / sum(aq_por_concurso.values()) * 100
    print(f"  {k:2d} nums: {aq_por_concurso[k]:4d} concursos ({pct:5.1f}%)")

print()

# Diff: quem aparece vs nao aparece
aparecem_diff = []
nao_aparecem_diff = []
for idx, n, f, diff in eventos_aquecendo:
    if idx + 1 < total and n in dados[idx + 1][2]:
        aparecem_diff.append(diff)
    elif idx + 1 < total:
        nao_aparecem_diff.append(diff)

if aparecem_diff:
    print(f"Media diff dos que aparecem no seguinte: {sum(aparecem_diff)/len(aparecem_diff):.2f}")
if nao_aparecem_diff:
    print(f"Media diff dos que NAO aparecem no seguinte: {sum(nao_aparecem_diff)/len(nao_aparecem_diff):.2f}")
print()
print(f"Aparecem no sorteio seguinte: {len(aparecem_diff)}/{len(aparecem_diff) + len(nao_aparecem_diff)} ({len(aparecem_diff)/(len(aparecem_diff) + len(nao_aparecem_diff))*100:.1f}%)")
