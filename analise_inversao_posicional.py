"""
Análise do padrão de INVERSÃO POSICIONAL
Hipótese: Quando menor_que_ultimo é extremo (>=12), o próximo concurso tende a inverter (maior_que_ultimo alto)
"""
import pyodbc
import statistics
from collections import Counter

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;')
cursor = conn.cursor()

cursor.execute('''
    SELECT Concurso, menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
    FROM Resultados_INT
    WHERE Concurso > 1
    ORDER BY Concurso
''')
rows = [(r[0], r[1], r[2], r[3]) for r in cursor.fetchall()]
conn.close()

print(f'Total concursos analisados: {len(rows)}')
print()

# ═══════════════════════════════════════════════════════════════
# 1. DISTRIBUIÇÃO GERAL
# ═══════════════════════════════════════════════════════════════
menor_vals = [r[1] for r in rows if r[1] is not None]
maior_vals = [r[2] for r in rows if r[2] is not None]

print("=" * 60)
print("1. DISTRIBUIÇÃO menor_que_ultimo")
print("=" * 60)
dist_menor = Counter(r[1] for r in rows)
for k in sorted(dist_menor.keys()):
    pct = dist_menor[k] / len(rows) * 100
    bar = "#" * int(pct)
    print(f"  {k:>2}: {dist_menor[k]:>5} ({pct:5.1f}%) {bar}")

print(f"\n  Média: {statistics.mean(menor_vals):.2f}, Desvio: {statistics.stdev(menor_vals):.2f}")

print()
print("=" * 60)
print("2. DISTRIBUIÇÃO maior_que_ultimo")
print("=" * 60)
dist_maior = Counter(r[2] for r in rows)
for k in sorted(dist_maior.keys()):
    pct = dist_maior[k] / len(rows) * 100
    bar = "#" * int(pct)
    print(f"  {k:>2}: {dist_maior[k]:>5} ({pct:5.1f}%) {bar}")

print(f"\n  Média: {statistics.mean(maior_vals):.2f}, Desvio: {statistics.stdev(maior_vals):.2f}")

# ═══════════════════════════════════════════════════════════════
# 3. ANÁLISE DE INVERSÃO: Quando menor>=LIMIAR, o que acontece no próximo?
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("3. ANÁLISE DE INVERSÃO POSICIONAL")
print("   Quando concurso N tem menor_que_ultimo >= LIMIAR,")
print("   qual o maior_que_ultimo do concurso N+1?")
print("=" * 60)

for limiar in [10, 11, 12, 13, 14]:
    casos_extremo = []
    for i in range(len(rows) - 1):
        if rows[i][1] is not None and rows[i][1] >= limiar:
            prox_maior = rows[i+1][2]
            prox_menor = rows[i+1][1]
            if prox_maior is not None:
                casos_extremo.append({
                    'concurso': rows[i][0],
                    'menor_atual': rows[i][1],
                    'prox_concurso': rows[i+1][0],
                    'prox_maior': prox_maior,
                    'prox_menor': prox_menor,
                    'inverteu': prox_maior >= limiar  # inversão forte
                })
    
    if casos_extremo:
        prox_maiores = [c['prox_maior'] for c in casos_extremo]
        prox_menores = [c['prox_menor'] for c in casos_extremo]
        inverteu_count = sum(1 for c in casos_extremo if c['inverteu'])
        
        # Alta inversão = prox_maior >= 10
        alta_inv = sum(1 for c in casos_extremo if c['prox_maior'] >= 10)
        
        print(f"\n  LIMIAR = {limiar} (menor_que_ultimo >= {limiar})")
        print(f"  Ocorrências: {len(casos_extremo)}")
        print(f"  Próx maior_que_ultimo: média={statistics.mean(prox_maiores):.1f}, "
              f"mediana={statistics.median(prox_maiores):.0f}, "
              f"min={min(prox_maiores)}, max={max(prox_maiores)}")
        print(f"  Próx menor_que_ultimo: média={statistics.mean(prox_menores):.1f}")
        print(f"  Inversão forte (prox_maior>={limiar}): {inverteu_count}/{len(casos_extremo)} = {inverteu_count/len(casos_extremo)*100:.1f}%")
        print(f"  Inversão moderada (prox_maior>=10): {alta_inv}/{len(casos_extremo)} = {alta_inv/len(casos_extremo)*100:.1f}%")
    else:
        print(f"\n  LIMIAR = {limiar}: Nenhuma ocorrência")

# ═══════════════════════════════════════════════════════════════
# 4. ANÁLISE INVERSA: Quando maior>=LIMIAR, o que acontece no próximo?
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("4. ANÁLISE INVERSA")
print("   Quando concurso N tem maior_que_ultimo >= LIMIAR,")
print("   qual o menor_que_ultimo do concurso N+1?")
print("=" * 60)

for limiar in [10, 11, 12, 13, 14]:
    casos = []
    for i in range(len(rows) - 1):
        if rows[i][2] is not None and rows[i][2] >= limiar:
            prox_menor = rows[i+1][1]
            prox_maior = rows[i+1][2]
            if prox_menor is not None:
                casos.append({
                    'concurso': rows[i][0],
                    'maior_atual': rows[i][2],
                    'prox_menor': prox_menor,
                    'prox_maior': prox_maior,
                })
    
    if casos:
        prox_menores = [c['prox_menor'] for c in casos]
        prox_maiores = [c['prox_maior'] for c in casos]
        alta_inv = sum(1 for c in casos if c['prox_menor'] >= 10)
        
        print(f"\n  LIMIAR = {limiar} (maior_que_ultimo >= {limiar})")
        print(f"  Ocorrências: {len(casos)}")
        print(f"  Próx menor_que_ultimo: média={statistics.mean(prox_menores):.1f}, "
              f"mediana={statistics.median(prox_menores):.0f}, "
              f"min={min(prox_menores)}, max={max(prox_menores)}")
        print(f"  Próx maior_que_ultimo: média={statistics.mean(prox_maiores):.1f}")
        print(f"  Inversão forte (prox_menor>={limiar}): {alta_inv}/{len(casos)} = {alta_inv/len(casos)*100:.1f}%")

# ═══════════════════════════════════════════════════════════════
# 5. BASELINE: Distribuição normal (sem condicionar a extremo)
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("5. BASELINE (todos os concursos, sem filtro)")
print("=" * 60)
print(f"  menor_que_ultimo >= 10: {sum(1 for r in rows if r[1] and r[1] >= 10)}/{len(rows)} = {sum(1 for r in rows if r[1] and r[1] >= 10)/len(rows)*100:.1f}%")
print(f"  menor_que_ultimo >= 12: {sum(1 for r in rows if r[1] and r[1] >= 12)}/{len(rows)} = {sum(1 for r in rows if r[1] and r[1] >= 12)/len(rows)*100:.1f}%")
print(f"  menor_que_ultimo >= 13: {sum(1 for r in rows if r[1] and r[1] >= 13)}/{len(rows)} = {sum(1 for r in rows if r[1] and r[1] >= 13)/len(rows)*100:.1f}%")
print(f"  maior_que_ultimo >= 10: {sum(1 for r in rows if r[2] and r[2] >= 10)}/{len(rows)} = {sum(1 for r in rows if r[2] and r[2] >= 10)/len(rows)*100:.1f}%")
print(f"  maior_que_ultimo >= 12: {sum(1 for r in rows if r[2] and r[2] >= 12)}/{len(rows)} = {sum(1 for r in rows if r[2] and r[2] >= 12)/len(rows)*100:.1f}%")
print(f"  maior_que_ultimo >= 13: {sum(1 for r in rows if r[2] and r[2] >= 13)}/{len(rows)} = {sum(1 for r in rows if r[2] and r[2] >= 13)/len(rows)*100:.1f}%")

# ═══════════════════════════════════════════════════════════════
# 6. DETALHADO: Listar últimos 20 casos extremos (menor>=12)
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("6. ÚLTIMOS 20 CASOS: menor_que_ultimo >= 12 + PRÓXIMO")
print("=" * 60)
print(f"  {'Conc':>5} {'Men':>4} {'Mai':>4} {'Igu':>4} | {'ProxConc':>8} {'ProxMen':>7} {'ProxMai':>7} {'ProxIgu':>7} | Inversão?")
print("  " + "-" * 80)

casos_det = []
for i in range(len(rows) - 1):
    if rows[i][1] is not None and rows[i][1] >= 12:
        casos_det.append((rows[i], rows[i+1]))

for curr, prox in casos_det[-20:]:
    inv = "✅ SIM" if prox[2] >= 10 else "❌ NÃO"
    print(f"  {curr[0]:>5} {curr[1]:>4} {curr[2]:>4} {curr[3]:>4} | {prox[0]:>8} {prox[1]:>7} {prox[2]:>7} {prox[3]:>7} | {inv}")

# ═══════════════════════════════════════════════════════════════
# 7. CORRELAÇÃO: Pearson entre menor_atual e prox_maior
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("7. CORRELAÇÃO SERIAL (Pearson)")
print("=" * 60)

pares_men_mai = []
pares_mai_men = []
for i in range(len(rows) - 1):
    if rows[i][1] is not None and rows[i+1][2] is not None:
        pares_men_mai.append((rows[i][1], rows[i+1][2]))
    if rows[i][2] is not None and rows[i+1][1] is not None:
        pares_mai_men.append((rows[i][2], rows[i+1][1]))

def pearson(pairs):
    n = len(pairs)
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n
    sx = (sum((xi - mx)**2 for xi in x) / n) ** 0.5
    sy = (sum((yi - my)**2 for yi in y) / n) ** 0.5
    if sx == 0 or sy == 0:
        return 0
    return cov / (sx * sy)

r1 = pearson(pares_men_mai)
r2 = pearson(pares_mai_men)
print(f"  Corr(menor[N], maior[N+1]) = {r1:.4f}")
print(f"  Corr(maior[N], menor[N+1]) = {r2:.4f}")
print()
if abs(r1) > 0.1:
    print(f"  ⚡ Correlação SIGNIFICATIVA! r={r1:.4f}")
else:
    print(f"  📊 Correlação fraca (r={r1:.4f})")
