# -*- coding: utf-8 -*-
"""Análise exploratória PROFUNDA da tabela COMBIN_10 - Parte 2"""
import pyodbc
from math import comb
from itertools import combinations

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

C25_10 = comb(25, 10)  # 3,268,760
C15_10 = comb(15, 10)  # 3,003

# ═══════════════════════════════════════════════════
# 1. VERIFICAR DISCREPÂNCIA NA SOMA
# ═══════════════════════════════════════════════════
print('═' * 60)
print('1. DIAGNÓSTICO: DISCREPÂNCIA SOMA QTDE_ACERTOS')
print('═' * 60)

cursor.execute("SELECT SUM(CAST(QTDE_ACERTOS AS BIGINT)) FROM COMBIN_10")
soma_real = cursor.fetchone()[0]
cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
ultimo_conc = cursor.fetchone()[0]
soma_esperada = ultimo_conc * C15_10

print(f'  Soma real:     {soma_real:>15,}')
print(f'  Soma esperada: {soma_esperada:>15,} ({ultimo_conc} × {C15_10})')
print(f'  Ratio:         {soma_real / soma_esperada:.4f}x')

# Verificar se distribuição é bimodal (evens vs odds)
cursor.execute("""
    SELECT QTDE_ACERTOS, COUNT(*) as QTD
    FROM COMBIN_10
    GROUP BY QTDE_ACERTOS
    ORDER BY QTDE_ACERTOS
""")
dist = cursor.fetchall()
evens = sum(r[1] for r in dist if r[0] % 2 == 0)
odds = sum(r[1] for r in dist if r[0] % 2 == 1)
print(f'\n  Combos com acertos PARES:   {evens:>10,} ({evens/C25_10*100:.1f}%)')
print(f'  Combos com acertos ÍMPARES: {odds:>10,} ({odds/C25_10*100:.1f}%)')
print(f'  Ratio even/odd:             {evens/odds:.1f}x')

# Verificar combos com QTDE_ACERTOS=0 e CONCURSO != NULL
cursor.execute("""
    SELECT COUNT(*) FROM COMBIN_10 WHERE QTDE_ACERTOS = 0 AND CONCURSO IS NOT NULL
""")
zero_com_conc = cursor.fetchone()[0]
cursor.execute("""
    SELECT COUNT(*) FROM COMBIN_10 WHERE QTDE_ACERTOS = 0 AND CONCURSO IS NULL
""")
zero_sem_conc = cursor.fetchone()[0]
cursor.execute("""
    SELECT COUNT(*) FROM COMBIN_10 WHERE CONCURSO IS NULL
""")
total_null_conc = cursor.fetchone()[0]
print(f'\n  QTDE_ACERTOS=0 com CONCURSO preenchido: {zero_com_conc:,}')
print(f'  QTDE_ACERTOS=0 com CONCURSO NULL:       {zero_sem_conc:,}')
print(f'  Total com CONCURSO NULL:                {total_null_conc:,}')

# Verificação manual: pegar uma combo com muitos acertos e conferir
cursor.execute("""
    SELECT TOP 1 N1,N2,N3,N4,N5,N6,N7,N8,N9,N10, QTDE_ACERTOS
    FROM COMBIN_10 ORDER BY QTDE_ACERTOS DESC
""")
top = cursor.fetchone()
top_nums = set(top[:10])
top_acertos = top[10]
print(f'\n  Top combo: {sorted(top_nums)} → QTDE_ACERTOS = {top_acertos}')

# Contar manualmente quantos concursos contêm TODOS os 10 números
nums = sorted(top_nums)
conditions = ' AND '.join([f'R.N{j} = ANY_VAL' for j in range(1, 16)])
# Melhor abordagem: usar UNPIVOT ou checagem direta
sql = f"""
    SELECT COUNT(*) FROM Resultados_INT R
    WHERE {nums[0]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[1]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[2]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[3]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[4]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[5]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[6]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[7]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[8]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
      AND {nums[9]} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)
"""
cursor.execute(sql)
real_count = cursor.fetchone()[0]
print(f'  Contagem manual (Resultados_INT): {real_count}')
print(f'  QTDE_ACERTOS na tabela:           {top_acertos}')
if real_count != top_acertos:
    print(f'  ⚠️  DISCREPÂNCIA! Diferença: {top_acertos - real_count}')
    print(f'  CONCLUSÃO: Proc provavelmente rodou {top_acertos / real_count:.1f}x para algum período')


# ═══════════════════════════════════════════════════
# 2. VALIDAÇÃO MULTI-CONCURSO DO LIFT
# ═══════════════════════════════════════════════════
print(f'\n{"═" * 60}')
print('2. VALIDAÇÃO: LIFT POR FAIXA DE QTDE_ACERTOS')
print('   (Últimos 20 concursos)')
print('═' * 60)

cursor.execute("""
    SELECT TOP 20 Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT ORDER BY Concurso DESC
""")
concursos = cursor.fetchall()

# Thresholds para testar
thresholds = [0, 3, 5, 8, 10, 15, 20]

# Para cada threshold, calcular lift médio em 20 concursos
print(f'\n  {"Threshold":>10s} {"Combos":>10s} {"Lift Médio":>12s} {"Min":>8s} {"Max":>8s} {"StdDev":>8s}')
print(f'  {"-"*10} {"-"*10} {"-"*12} {"-"*8} {"-"*8} {"-"*8}')

baseline = C15_10 / C25_10  # P(combo aleatória estar no sorteio)

for th in thresholds:
    cursor.execute(f"SELECT COUNT(*) FROM COMBIN_10 WHERE QTDE_ACERTOS >= {th}")
    total_th = cursor.fetchone()[0]
    
    lifts = []
    for conc_row in concursos:
        nums = sorted(set(conc_row[1:16]))
        nums_str = ','.join(str(n) for n in nums)
        where_in = ' AND '.join([f'N{i} IN ({nums_str})' for i in range(1, 11)])
        
        cursor.execute(f"""
            SELECT COUNT(*) FROM COMBIN_10 
            WHERE {where_in} AND QTDE_ACERTOS >= {th}
        """)
        acertou = cursor.fetchone()[0]
        
        pct = acertou / total_th if total_th > 0 else 0
        lift = pct / baseline if baseline > 0 else 0
        lifts.append(lift)
    
    import statistics
    avg_lift = statistics.mean(lifts)
    min_lift = min(lifts)
    max_lift = max(lifts)
    std_lift = statistics.stdev(lifts) if len(lifts) > 1 else 0
    
    print(f'  >= {th:>5d}  {total_th:>10,}  {avg_lift:>11.3f}x  {min_lift:>7.3f}  {max_lift:>7.3f}  {std_lift:>7.3f}')


# ═══════════════════════════════════════════════════
# 3. ANÁLISE: OVERLAP DE COMBOS-10 ENTRE SORTEIOS CONSECUTIVOS
# ═══════════════════════════════════════════════════
print(f'\n{"═" * 60}')
print('3. OVERLAP DE COMBOS-10 ENTRE SORTEIOS CONSECUTIVOS')
print('═' * 60)

cursor.execute("""
    SELECT TOP 51 Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT ORDER BY Concurso DESC
""")
all_concs = cursor.fetchall()

overlaps = []
for i in range(len(all_concs) - 1):
    nums_a = set(all_concs[i][1:16])
    nums_b = set(all_concs[i+1][1:16])
    
    combos_a = set(combinations(sorted(nums_a), 10))
    combos_b = set(combinations(sorted(nums_b), 10))
    
    overlap = len(combos_a & combos_b)
    overlaps.append(overlap)

avg_overlap = sum(overlaps) / len(overlaps)
print(f'  Últimos 50 pares consecutivos:')
print(f'  Média de combos-10 compartilhadas: {avg_overlap:.1f} de {C15_10}')
print(f'  Min: {min(overlaps)}, Max: {max(overlaps)}')
print(f'  % médio de overlap: {avg_overlap/C15_10*100:.1f}%')

# Distribuição por repetições de números
print(f'\n  Overlap por repetições de números (15 vs 15):')
rep_overlaps = {}
for i in range(len(all_concs) - 1):
    nums_a = set(all_concs[i][1:16])
    nums_b = set(all_concs[i+1][1:16])
    rep = len(nums_a & nums_b)
    
    combos_a = set(combinations(sorted(nums_a), 10))
    combos_b = set(combinations(sorted(nums_b), 10))
    overlap = len(combos_a & combos_b)
    
    if rep not in rep_overlaps:
        rep_overlaps[rep] = []
    rep_overlaps[rep].append(overlap)

for rep in sorted(rep_overlaps.keys()):
    vals = rep_overlaps[rep]
    avg = sum(vals) / len(vals)
    print(f'    {rep:2d} números em comum → {avg:>6.0f} combos-10 compartilhadas ({avg/C15_10*100:.1f}%) [{len(vals)} casos]')


# ═══════════════════════════════════════════════════
# 4. ANÁLISE: TOP COMBOS QUE MAIS SAEM vs BASELINE
# ═══════════════════════════════════════════════════
print(f'\n{"═" * 60}')
print('4. TOP COMBOS: PERSISTÊNCIA vs ACASO')
print('═' * 60)

# Quantas combos com QTDE_ACERTOS >= 15 acertaram nos últimos 50 concursos?
cursor.execute("""
    SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10, QTDE_ACERTOS
    FROM COMBIN_10 WHERE QTDE_ACERTOS >= 15
""")
hot_combos = cursor.fetchall()
print(f'  Total de combos com QTDE_ACERTOS >= 15: {len(hot_combos):,}')

# Para últimos 20 concursos, verificar quantas hot combos acertam
hot_sets = [set(row[:10]) for row in hot_combos]

acertos_por_conc = []
for conc_row in all_concs[:20]:
    conc_nums = set(conc_row[1:16])
    acertou = sum(1 for hs in hot_sets if hs.issubset(conc_nums))
    acertos_por_conc.append((conc_row[0], acertou))

print(f'\n  Hot combos (≥15) que acertam por sorteio (últimos 20):')
for conc, ac in acertos_por_conc:
    esperado = len(hot_combos) * C15_10 / C25_10
    lift = ac / esperado if esperado > 0 else 0
    print(f'    Conc {conc}: {ac:>5d} acertaram (esperado: {esperado:.1f}, lift: {lift:.2f}x)')

media_acertos = sum(a for _, a in acertos_por_conc) / len(acertos_por_conc)
esperado_medio = len(hot_combos) * C15_10 / C25_10
lift_medio = media_acertos / esperado_medio if esperado_medio > 0 else 0
print(f'\n  Média: {media_acertos:.1f} acertaram por sorteio (esperado: {esperado_medio:.1f}, lift médio: {lift_medio:.2f}x)')


# ═══════════════════════════════════════════════════
# 5. POTENCIAL COMO FILTRO PARA POOL 23
# ═══════════════════════════════════════════════════
print(f'\n{"═" * 60}')
print('5. POTENCIAL COMO FILTRO PARA COMBINAÇÕES DE 15')
print('═' * 60)

# Para uma combinação de 15 números, ela contém C(15,10) = 3003 sub-combos de 10
# Ideia: score de uma combo-15 = soma dos QTDE_ACERTOS de suas 3003 sub-combos
# Combos-15 com score mais alto = mais "aquecidas" historicamente

# Testar com últimos 10 resultados
print(f'\n  Score das sub-combos-10 para resultados reais:')
scores_reais = []
for conc_row in all_concs[:10]:
    nums = sorted(set(conc_row[1:16]))
    sub_combos = list(combinations(nums, 10))
    
    # Consultar QTDE_ACERTOS para cada sub-combo
    total_score = 0
    for sc in sub_combos:
        cursor.execute(f"""
            SELECT QTDE_ACERTOS FROM COMBIN_10
            WHERE N1={sc[0]} AND N2={sc[1]} AND N3={sc[2]} AND N4={sc[3]} AND N5={sc[4]}
              AND N6={sc[5]} AND N7={sc[6]} AND N8={sc[7]} AND N9={sc[8]} AND N10={sc[9]}
        """)
        row = cursor.fetchone()
        if row:
            total_score += row[0]
    
    avg_score = total_score / len(sub_combos)
    scores_reais.append((conc_row[0], total_score, avg_score))
    print(f'    Conc {conc_row[0]}: score_total={total_score:,}, média_sub={avg_score:.2f}')

# Gerar 5 combos aleatórias para comparar
import random
random.seed(42)
print(f'\n  Score de 5 combinações ALEATÓRIAS de 15:')
scores_aleatorios = []
for i in range(5):
    nums = sorted(random.sample(range(1, 26), 15))
    sub_combos = list(combinations(nums, 10))
    
    total_score = 0
    for sc in sub_combos:
        cursor.execute(f"""
            SELECT QTDE_ACERTOS FROM COMBIN_10
            WHERE N1={sc[0]} AND N2={sc[1]} AND N3={sc[2]} AND N4={sc[3]} AND N5={sc[4]}
              AND N6={sc[5]} AND N7={sc[6]} AND N8={sc[7]} AND N9={sc[8]} AND N10={sc[9]}
        """)
        row = cursor.fetchone()
        if row:
            total_score += row[0]
    
    avg_score = total_score / len(sub_combos)
    scores_aleatorios.append(total_score)
    print(f'    Aleatória {i+1} {nums}: score_total={total_score:,}, média_sub={avg_score:.2f}')

avg_real = sum(s[1] for s in scores_reais) / len(scores_reais)
avg_rand = sum(scores_aleatorios) / len(scores_aleatorios)
print(f'\n  COMPARAÇÃO:')
print(f'    Score médio RESULTADOS REAIS:  {avg_real:>10,.0f}')
print(f'    Score médio ALEATÓRIAS:        {avg_rand:>10,.0f}')
print(f'    Diferença: {((avg_real/avg_rand - 1)*100):+.1f}%')

conn.close()
print('\n✅ Análise Parte 2 completa!')

