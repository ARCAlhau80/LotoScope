import pyodbc
import statistics
from collections import Counter

CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Lotofacil;'
    'Trusted_Connection=yes;'
)

conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

# ============================================================
# PARTE 1: Distribuicao de somas
# ============================================================
print("=" * 65)
print("ANÁLISE DE REPETIÇÃO DE SOMAS — LOTOFÁCIL")
print("=" * 65)

cursor.execute("""
    SELECT Concurso, N1+N2+N3+N4+N5+N6+N7+N8+N9+N10+N11+N12+N13+N14+N15 AS Soma
    FROM Resultados_INT
    ORDER BY Concurso
""")
rows = cursor.fetchall()
concursos = [(r[0], r[1]) for r in rows]
somas = [r[1] for r in concursos]
total = len(somas)

somas_distintas = len(set(somas))
soma_min = min(somas)
soma_max = max(somas)
soma_media = statistics.mean(somas)
soma_mediana = statistics.median(somas)
soma_std = statistics.stdev(somas)

print(f"\n### 1. DISTRIBUIÇÃO DE SOMAS ({total} concursos)")
print(f"   Mínima  : {soma_min}")
print(f"   Máxima  : {soma_max}")
print(f"   Média   : {soma_media:.2f}")
print(f"   Mediana : {soma_mediana:.1f}")
print(f"   Desvio  : {soma_std:.2f}")
print(f"   Somas distintas: {somas_distintas}")
print(f"   Range teórico: {min(range(1,26))+(min(range(2,26)))+(min(range(3,26)))} a aprox 360")

# Top 10 somas mais frequentes
freq_somas = Counter(somas)
print(f"\n   Top 10 somas mais frequentes:")
print(f"   {'Soma':>6} | {'Freq':>5} | {'%':>6}")
print(f"   {'-'*25}")
for soma, cnt in freq_somas.most_common(10):
    print(f"   {soma:>6} | {cnt:>5} | {cnt/total*100:>5.2f}%")

# ============================================================
# PARTE 2: Repeticao consecutiva N -> N+1
# ============================================================
print(f"\n### 2. REPETIÇÃO CONSECUTIVA (N → N+1)")
repeticoes_consec = []
for i in range(1, len(concursos)):
    if concursos[i][1] == concursos[i-1][1]:
        repeticoes_consec.append((concursos[i][0], concursos[i][1]))

pct_consec = len(repeticoes_consec) / (total - 1) * 100
print(f"   Total de pares consecutivos: {total - 1}")
print(f"   Repeticoes exatas: {len(repeticoes_consec)}")
print(f"   Porcentagem: {pct_consec:.2f}%")
print(f"   Frequência esperada (aleatória): ~{100/somas_distintas:.2f}% (1/{somas_distintas} somas distintas)")

print(f"\n   Últimos 10 casos de repetição consecutiva:")
print(f"   {'Concurso N':>12} | {'Concurso N-1':>12} | {'Soma':>6}")
print(f"   {'-'*40}")
for c, s in repeticoes_consec[-10:]:
    idx = next(i for i, (cc, _) in enumerate(concursos) if cc == c)
    print(f"   {c:>12} | {concursos[idx-1][0]:>12} | {s:>6}")

# ============================================================
# PARTE 3: Janelas de 3, 5, 10
# ============================================================
print(f"\n### 3. REPETIÇÃO EM JANELAS (3, 5, 10 concursos anteriores)")
for janela in [3, 5, 10]:
    repet = 0
    for i in range(janela, len(concursos)):
        soma_atual = concursos[i][1]
        somas_janela = [concursos[j][1] for j in range(i-janela, i)]
        if soma_atual in somas_janela:
            repet += 1
    pct = repet / (total - janela) * 100
    print(f"   Janela {janela:2d}: {repet:5d} concursos repetiram | {pct:.2f}%")

# ============================================================
# PARTE 4: Ultimos 20 concursos
# ============================================================
print(f"\n### 4. ÚLTIMOS 20 CONCURSOS — SOMAS")
ultimos20 = concursos[-20:]
print(f"   {'Concurso':>10} | {'Soma':>6} | {'Repetiu anterior?':>18}")
print(f"   {'-'*42}")
for i, (c, s) in enumerate(ultimos20):
    repetiu = ""
    if i > 0 and s == ultimos20[i-1][1]:
        repetiu = "✓ IGUAL ao anterior"
    elif i > 0:
        delta = s - ultimos20[i-1][1]
        sinal = "+" if delta > 0 else ""
        repetiu = f"delta {sinal}{delta}"
    print(f"   {c:>10} | {s:>6} | {repetiu}")

# Verificar quantas somas aparecem na janela de 5 nos ultimos 20
print(f"\n   Legenda: para cada concurso, se a soma aparece nos 4 anteriores:")
for i in range(4, 20):
    c, s = ultimos20[i]
    somas_prev = [ultimos20[j][1] for j in range(i-4, i)]
    if s in somas_prev:
        prev_conc = [ultimos20[j][0] for j in range(i-4, i) if ultimos20[j][1] == s]
        print(f"   Concurso {c}: soma {s} JÁ APARECEU em {prev_conc}")

conn.close()
