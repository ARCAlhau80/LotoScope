# -*- coding: utf-8 -*-
"""Analise completa de repeticao de somas — Lotofacil"""

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

# Carregar todos os concursos com soma
cursor.execute("""
    SELECT Concurso, N1+N2+N3+N4+N5+N6+N7+N8+N9+N10+N11+N12+N13+N14+N15 AS Soma
    FROM Resultados_INT
    ORDER BY Concurso
""")
rows = cursor.fetchall()
concursos = [(r[0], r[1]) for r in rows]
somas = [r[1] for r in concursos]
total = len(somas)
TOTAL_COMBIN = 3268760

print("=" * 65)
print("  ANALISE DE REPETICAO DE SOMAS -- LOTOFACIL")
print(f"  Total de concursos analisados: {total}")
print("=" * 65)

# 1. Distribuicao de somas
soma_min = min(somas)
soma_max = max(somas)
soma_media = statistics.mean(somas)
soma_mediana = statistics.median(somas)
soma_std = statistics.stdev(somas)
freq_somas = Counter(somas)
somas_distintas = len(freq_somas)

print(f"\n--- 1. DISTRIBUICAO DE SOMAS ---")
print(f"  Minima         : {soma_min}")
print(f"  Maxima         : {soma_max}")
print(f"  Media          : {soma_media:.2f}")
print(f"  Mediana        : {soma_mediana:.1f}")
print(f"  Desvio Padrao  : {soma_std:.2f}")
print(f"  Somas distintas: {somas_distintas}")
print(f"  Range ocupado  : {somas_distintas}/{soma_max - soma_min + 1} = {somas_distintas/(soma_max-soma_min+1)*100:.1f}%")

print(f"\n  Top 15 somas mais frequentes:")
print(f"  {'Soma':>6} | {'Freq':>5} | {'%':>6}")
print(f"  {'-'*25}")
for soma, cnt in freq_somas.most_common(15):
    print(f"  {soma:>6} | {cnt:>5} | {cnt/total*100:>5.2f}%")

print(f"\n  Distribuicao por faixas:")
print(f"  {'Faixa':>12} | {'Count':>6} | {'%':>6}")
print(f"  {'-'*32}")
faixas = [(150,169),(170,179),(180,184),(185,189),(190,194),
          (195,199),(200,204),(205,209),(210,219),(220,239),(240,280)]
for fa, fb in faixas:
    cnt = sum(1 for s in somas if fa <= s <= fb)
    print(f"  {fa:>5}-{fb:<3}     | {cnt:>6} | {cnt/total*100:>5.2f}%")

# 2. Repeticao consecutiva N -> N+1
print(f"\n--- 2. REPETICAO CONSECUTIVA (N -> N+1) ---")
repeticoes_consec = []
for i in range(1, len(concursos)):
    if concursos[i][1] == concursos[i-1][1]:
        repeticoes_consec.append((concursos[i][0], concursos[i-1][0], concursos[i][1]))

pct_consec = len(repeticoes_consec) / (total - 1) * 100
esperado = 100.0 / somas_distintas
print(f"  Total de pares consecutivos    : {total - 1}")
print(f"  Repeticoes exatas (N = N+1)    : {len(repeticoes_consec)}")
print(f"  Porcentagem real               : {pct_consec:.3f}%")
print(f"  Frequencia esperada (aleatoria): ~{esperado:.3f}%  (1/{somas_distintas} somas distintas)")
print(f"  Razao real/esperado            : {pct_consec/esperado:.2f}x")

print(f"\n  Ultimos 15 casos de repeticao consecutiva:")
print(f"  {'Conc. N-1':>10} | {'Conc. N':>8} | {'Soma':>6}")
print(f"  {'-'*35}")
for c_atual, c_prev, s in repeticoes_consec[-15:]:
    print(f"  {c_prev:>10} | {c_atual:>8} | {s:>6}")

if len(repeticoes_consec) > 1:
    concurso_nums = [r[0] for r in concursos]
    idxs = [concurso_nums.index(c) for c, _, _ in repeticoes_consec]
    intervalos = [idxs[k] - idxs[k-1] for k in range(1, len(idxs))]
    print(f"\n  Intervalo medio entre repeticoes: {statistics.mean(intervalos):.1f} concursos")
    print(f"  Intervalo minimo: {min(intervalos)} | maximo: {max(intervalos)}")

# 3. Janelas
print(f"\n--- 3. REPETICAO EM JANELAS ---")
print(f"  {'Janela':>8} | {'Repeticoes':>11} | {'% real':>8} | {'% teorico':>10}")
print(f"  {'-'*50}")
for janela in [2, 3, 5, 7, 10, 15, 20]:
    repet = 0
    validos = total - janela
    for i in range(janela, len(concursos)):
        soma_atual = concursos[i][1]
        if soma_atual in [concursos[j][1] for j in range(i-janela, i)]:
            repet += 1
    pct = repet / validos * 100
    teo = (1 - (1 - 1/somas_distintas)**janela) * 100
    print(f"  {janela:>8} | {repet:>11} | {pct:>7.2f}% | {teo:>9.2f}%")

# 4. Ultimos 20 concursos
print(f"\n--- 4. ULTIMOS 20 CONCURSOS ---")
print(f"  {'Concurso':>10} | {'Soma':>6} | {'Delta':>6} | Nota")
print(f"  {'-'*60}")
ultimos20 = concursos[-20:]
for i, (c, s) in enumerate(ultimos20):
    if i == 0:
        print(f"  {c:>10} | {s:>6} | {'---':>6} | (inicio da janela)")
    else:
        delta = s - ultimos20[i-1][1]
        somas_prev4 = [ultimos20[j][1] for j in range(max(0,i-4), i)]
        if s == ultimos20[i-1][1]:
            nota = "*** IGUAL AO ANTERIOR! ***"
        elif s in somas_prev4:
            idxs_prev = [ultimos20[j][0] for j in range(max(0,i-4), i) if ultimos20[j][1] == s]
            nota = f"Ja em {idxs_prev} (ult.5)"
        else:
            nota = ""
        print(f"  {c:>10} | {s:>6} | {'+' if delta>0 else ''}{delta:>5} | {nota}")

# 5. Analise teorica
print(f"\n--- 5. ANALISE TEORICA (COMBINACOES POR SOMA) ---")
has_combin = False
dist_soma_db = {}
try:
    cursor.execute("SELECT TOP 1 Soma FROM COMBINACOES_LOTOFACIL")
    has_combin = True
    print("  Tabela COMBINACOES_LOTOFACIL disponivel (coluna Soma)")
    cursor.execute("""
        SELECT Soma, COUNT(*) as Qtd
        FROM COMBINACOES_LOTOFACIL
        GROUP BY Soma
        ORDER BY Soma
    """)
    dist_soma_db = {r[0]: r[1] for r in cursor.fetchall()}
    total_tab = sum(dist_soma_db.values())
    print(f"  Total de combinacoes na tabela: {total_tab:,}")
except Exception as e:
    print(f"  COMBINACOES_LOTOFACIL NAO disponivel: {e}")
    print("  Calculando por iteracao combinatoria...")
    from itertools import combinations
    soma_counter = Counter()
    for combo in combinations(range(1,26), 15):
        soma_counter[sum(combo)] += 1
    dist_soma_db = dict(soma_counter)
    print(f"  Total calculado: {sum(dist_soma_db.values()):,}")

somas_interesse = [175, 180, 185, 190, 195, 200, 205, 210, 215, 220]
print(f"\n  {'Soma':>6} | {'Combinacoes':>13} | {'% do total':>12}")
print(f"  {'-'*40}")
for s in somas_interesse:
    q = dist_soma_db.get(s, 0)
    print(f"  {s:>6} | {q:>13,} | {q/TOTAL_COMBIN*100:>11.4f}%")

ultimo_c, ultimo_soma = concursos[-1]
q_ult = dist_soma_db.get(ultimo_soma, 0)
print(f"\n  Ultimo concurso {ultimo_c}: soma={ultimo_soma}")
print(f"  Combinacoes com soma {ultimo_soma}: {q_ult:,} ({q_ult/TOTAL_COMBIN*100:.4f}%)")

# 6. Viabilidade como filtro
print(f"\n--- 6. VIABILIDADE COMO FILTRO ---")
somas_ult1 = [somas[-1]]
somas_ult3 = list(set(somas[-3:]))
somas_ult5 = list(set(somas[-5:]))

q_1so = sum(dist_soma_db.get(s,0) for s in somas_ult1)
q_3cons = sum(dist_soma_db.get(s,0) for s in somas_ult3)
q_5cons = sum(dist_soma_db.get(s,0) for s in somas_ult5)

pct_1so = q_1so / TOTAL_COMBIN * 100
pct_3cons = q_3cons / TOTAL_COMBIN * 100
pct_5cons = q_5cons / TOTAL_COMBIN * 100

print(f"  Ultimo concurso ({ultimo_c}): soma = {ultimo_soma}")
print(f"  Somas ultimos 3 concursos : {sorted(somas_ult3)}")
print(f"  Somas ultimos 5 concursos : {sorted(somas_ult5)}")
print(f"\n  {'Filtro':<40} | {'Combos elim.':>13} | {'%':>7}")
print(f"  {'-'*68}")
print(f"  {'Excluir soma do ultimo concurso':<40} | {q_1so:>13,} | {pct_1so:>6.3f}%")
print(f"  {'Excluir somas ultimos 3 concursos':<40} | {q_3cons:>13,} | {pct_3cons:>6.3f}%")
print(f"  {'Excluir somas ultimos 5 concursos':<40} | {q_5cons:>13,} | {pct_5cons:>6.3f}%")

print(f"\n  Impacto nos pools (estimativa):")
for pool_name, pool_size in [("Level 3 (~100k)", 100000), ("Level 5 (~42k)", 42000), ("Level 6 (~18k)", 18000)]:
    elim_1so = int(pool_size * pct_1so / 100)
    elim_3c  = int(pool_size * pct_3cons / 100)
    print(f"  {pool_name}: excluir soma ult. = -{elim_1so:,} | excluir ult. 3 = -{elim_3c:,}")

# Jackpots perdidos historicamente
perdidos_1 = 0
perdidos_3 = 0
perdidos_5 = 0
for i in range(1, len(concursos)):
    s = concursos[i][1]
    if s in [concursos[j][1] for j in range(max(0,i-1), i)]:
        perdidos_1 += 1
    if s in [concursos[j][1] for j in range(max(0,i-3), i)]:
        perdidos_3 += 1
    if s in [concursos[j][1] for j in range(max(0,i-5), i)]:
        perdidos_5 += 1

print(f"\n  JACKPOTS HISTORICOS PERDIDOS (concursos em que a soma repetiria):")
print(f"  {'Filtro':<40} | {'Jackpots perdidos':>17} | {'%':>7}")
print(f"  {'-'*72}")
print(f"  {'Excluir soma do concurso anterior':<40} | {perdidos_1:>17} | {perdidos_1/(total-1)*100:>6.2f}%")
print(f"  {'Excluir somas dos 3 anteriores':<40} | {perdidos_3:>17} | {perdidos_3/(total-3)*100:>6.2f}%")
print(f"  {'Excluir somas dos 5 anteriores':<40} | {perdidos_5:>17} | {perdidos_5/(total-5)*100:>6.2f}%")

print(f"\n  Distancia para excluir faixas em torno da ultima soma ({ultimo_soma}):")
print(f"  {'Distancia':>10} | {'Combos excluidas':>17} | {'% excluido':>11}")
print(f"  {'-'*46}")
for dist in [0, 1, 2, 3, 5, 10]:
    soms = [s for s in dist_soma_db if abs(s - ultimo_soma) <= dist]
    qtd = sum(dist_soma_db.get(s,0) for s in soms)
    print(f"  {'+/-'+str(dist):>10} | {qtd:>17,} | {qtd/TOTAL_COMBIN*100:>10.2f}%")

# 7. Conclusao
print(f"\n--- 7. CONCLUSAO E RECOMENDACAO ---")
print(f"""
  SINTESE DOS RESULTADOS:

  a) Repeticao exata consecutiva: {pct_consec:.2f}%  (esperado aleatorio: {esperado:.2f}%)
     Razao: {pct_consec/esperado:.2f}x -> comportamento ALEATORIO, sem padrao.

  b) Impacto do filtro (excluir soma do ultimo):
     -> Elimina apenas {pct_1so:.2f}% das combinacoes totais
     -> Para 100k combos: elimina ~{int(100000*pct_1so/100):,} combos
     -> Muito FRACO como filtro de reducao de escopo.

  c) Custo em jackpots: {perdidos_1/(total-1)*100:.2f}% dos sorteios TEM soma igual ao anterior.
     -> Aplicar esse filtro causaria perda REAL de jackpots.

  d) Janela de 3: {perdidos_3/(total-3)*100:.2f}% dos sorteios repetem soma dos 3 anteriores.
     -> Filtro ult. 3 excluiria {pct_3cons:.2f}% das combos mas perderia {perdidos_3/(total-3)*100:.2f}% jackpots.

  VEREDICTO:
  NAO RECOMENDADO como filtro hard de exclusao.

  Razoes:
  1. A repeticao ocorre com frequencia ALEATORIA.
  2. Elimina POUCO (~{pct_1so:.1f}% vs ~50% do subir/descer).
  3. Causa perda REAL de jackpots ({perdidos_1/(total-1)*100:.2f}% dos sorteios).
  4. Relacao custo-beneficio desfavoravel.

  USO RECOMENDADO (alternativo):
  -> Diagnostico situacional: verificar se a soma gerada e muito proxima da ultima.
  -> Faixa de somas (ex: +/-10) pode ser informativa sem ser excludente.
  -> Combinar com analise de distribuicao para sanity-check de combos geradas.
""")

conn.close()
print("Analise concluida com sucesso.")
