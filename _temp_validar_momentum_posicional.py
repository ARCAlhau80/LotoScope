# -*- coding: utf-8 -*-
"""
=============================================================================
VALIDAÇÃO HISTÓRICA — FILTRO MOMENTUM POSICIONAL (TENDÊNCIA DIRECIONAL)
=============================================================================
Lógica real do filtro (super_menu.py linha ~15277):
  Para posições com momentum FORTE (≥4/5 na mesma direção):
    - UP   forte → rejeitar combo se combo[pos] < ultimo_resultado[pos]
    - DOWN forte → rejeitar combo se combo[pos] > ultimo_resultado[pos]

Hipótese a validar:
  "Quando a posição P tem momentum UP ≥4/5, o sorteio seguinte tende a
   manter ou subir o valor nessa posição (resultado >= valor_anterior)"

Métricas:
  - Acurácia direcional: % de vezes que o real continuou na direção do momentum
  - Por força (3/5, 4/5, 5/5) e por posição (N1-N15)
  - Preservação de jackpot: % concursos reais que passam pelo filtro (tol X)
  - Comparação com baseline (≈50% esperado para direção aleatória)
=============================================================================
"""

import sys
import os
import pyodbc
from collections import defaultdict

# ── Path setup ───────────────────────────────────────────────────────────────
_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_dir, 'lotofacil_lite', 'utils'))
sys.path.insert(0, os.path.join(_dir, 'lotofacil_lite', 'interfaces'))

try:
    from database_config import DatabaseConfig
    db = DatabaseConfig()
    conn = db.get_connection()
except Exception:
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    )
    conn = pyodbc.connect(conn_str)

# ── Parâmetros ────────────────────────────────────────────────────────────────
JANELA        = 5    # transições para calcular momentum
FORCA_FORTE   = 4    # limiar "FORTE" (padrão do filtro nos níveis 3-6)
JANELA_INICIO = 7    # concursos iniciais descartados (precisa histórico mínimo)

# ── 1. Carregar resultados do banco ──────────────────────────────────────────
print("⏳ Carregando resultados históricos...")
cursor = conn.cursor()
cursor.execute("""
    SELECT Concurso,
           N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT
    ORDER BY Concurso ASC
""")

resultados_brutos = []
for row in cursor:
    nums = sorted([row[i] for i in range(1, 16)])
    resultados_brutos.append({'concurso': row[0], 'nums': nums})

conn.close()
total = len(resultados_brutos)
print(f"✅ {total:,} concursos carregados ({resultados_brutos[0]['concurso']} → {resultados_brutos[-1]['concurso']})")

# ── 2. Função: calcular momentum — replica _calcular_tendencia_direcao_posicional ─
def calcular_momentum(hist_desc, janela=5):
    """
    hist_desc: lista de listas ordenadas, índice 0 = mais recente.
    Retorna lista de 15 dicts com up/down/equal/dominante/forca.
    """
    n_pares = min(janela, len(hist_desc) - 1)
    result = []
    for pos in range(15):
        up = down = equal = 0
        for i in range(n_pares):
            v_novo = hist_desc[i][pos]
            v_ant  = hist_desc[i + 1][pos]
            if v_novo > v_ant:
                up += 1
            elif v_novo < v_ant:
                down += 1
            else:
                equal += 1
        if up > down and up >= 3:
            dominante = 'UP'
        elif down > up and down >= 3:
            dominante = 'DOWN'
        else:
            dominante = 'NEUTRAL'
        result.append({'pos': pos, 'up': up, 'down': down, 'equal': equal,
                        'dominante': dominante, 'forca': max(up, down)})
    return result

# ── 3. Estruturas de acumulação ───────────────────────────────────────────────
# Acurácia direcional: "result[pos] continua na mesma direção do momentum?"
acu_acertos  = defaultdict(int)   # {forca: acertos}
acu_total    = defaultdict(int)   # {forca: total}
acu_por_pos  = defaultdict(int)   # {(pos, forca): acertos}
acu_pos_tot  = defaultdict(int)   # {(pos, forca): total}

# Baseline: proporção de posições sem momentum que VÃO NA MESMA DIREÇÃO que o concurso anterior
baseline_subiu  = 0   # neutras com val_real >= val_ant (subiu ou igual)
baseline_total  = 0

# Violações no filtro real (combo = resultado real): mesmo check do super_menu
# "violação" = resultado vai contra a direção do momentum FORTE
viols_por_draw  = defaultdict(int)   # {n_viols: count_draws}
total_draws     = 0

# Por direção (UP vs DOWN separados)
dir_acu_ac = {'UP': defaultdict(int), 'DOWN': defaultdict(int)}
dir_acu_to = {'UP': defaultdict(int), 'DOWN': defaultdict(int)}

# ── 4. Loop principal ─────────────────────────────────────────────────────────
print(f"\n⏳ Analisando {total - JANELA_INICIO} concursos (janela={JANELA}, forte≥{FORCA_FORTE}/5)...")

for idx in range(JANELA_INICIO, total):
    # Histórico ANTES do concurso atual (mais recente primeiro)
    hist = [resultados_brutos[idx - 1 - k]['nums']
            for k in range(min(JANELA + 1, idx))]
    if len(hist) < 2:
        continue

    tendencias       = calcular_momentum(hist, janela=JANELA)
    val_anterior     = hist[0]   # concurso imediatamente anterior
    resultado_real   = resultados_brutos[idx]['nums']

    total_draws += 1
    n_viols_forte = 0

    for t in tendencias:
        pos     = t['pos']
        dom     = t['dominante']
        forca   = t['forca']
        v_ant   = val_anterior[pos]
        v_real  = resultado_real[pos]

        # ── Acurácia direcional ─────────────────────────────────────────────
        if dom == 'UP':
            acertou = (v_real >= v_ant)   # momentum UP → espera que suba ou fique
        elif dom == 'DOWN':
            acertou = (v_real <= v_ant)   # momentum DOWN → espera que desça ou fique
        else:
            # Baseline: posições neutras
            baseline_total += 1
            if v_real >= v_ant:
                baseline_subiu += 1
            continue

        acu_acertos[forca] += int(acertou)
        acu_total[forca]   += 1
        acu_por_pos[(pos, forca)] += int(acertou)
        acu_pos_tot[(pos, forca)] += 1
        dir_acu_ac[dom][forca] += int(acertou)
        dir_acu_to[dom][forca] += 1

        # ── Violação no filtro real (forca ≥ FORCA_FORTE) ──────────────────
        if forca >= FORCA_FORTE:
            if dom == 'UP'   and v_real < v_ant:
                n_viols_forte += 1
            elif dom == 'DOWN' and v_real > v_ant:
                n_viols_forte += 1

    viols_por_draw[n_viols_forte] += 1

# ── 5. Relatório ─────────────────────────────────────────────────────────────
print("\n" + "═"*72)
print("📊 VALIDAÇÃO HISTÓRICA — MOMENTUM POSICIONAL (TENDÊNCIA DIRECIONAL)")
print(f"   Concursos: {total_draws:,}  |  Janela: {JANELA}  |  Forte ≥{FORCA_FORTE}/5")
print("═"*72)

# Baseline (posições neutras)
bl_pct = baseline_subiu / baseline_total * 100 if baseline_total else 0
print(f"\n  Baseline (posições NEUTRAS): valor subiu ou ficou igual em {bl_pct:.1f}% dos casos")
print(f"  (esperado ≈50% se random; {baseline_total:,} eventos)")

print("\n┌─ ACURÁCIA DIRECIONAL: o sorteio seguiu o momentum? ──────────────────┐")
print(f"  {'Força':>6}  {'Eventos':>10}  {'Acertos':>9}  {'Acurácia':>10}  vs baseline")
print("  " + "─"*55)

for forca in sorted(acu_total.keys()):
    tot = acu_total[forca]
    ac  = acu_acertos[forca]
    hr  = ac / tot * 100
    delta = hr - bl_pct
    sinal = "+" if delta >= 0 else ""
    stars = ""
    if abs(delta) >= 10: stars = "  ⭐⭐⭐"
    elif abs(delta) >= 5: stars = "  ⭐⭐"
    elif abs(delta) >= 2: stars = "  ⭐"
    print(f"  {forca:>6}/5  {tot:>10,}  {ac:>9,}  {hr:>9.1f}%  {sinal}{delta:.1f}pp{stars}")

print("└" + "─"*55 + "┘")

print("\n┌─ ACURÁCIA POR DIREÇÃO (UP vs DOWN) ──────────────────────────────────┐")
for dom, label in (('UP', '⬆️  SUBINDO'), ('DOWN', '⬇️  DESCENDO')):
    print(f"  {label}")
    for forca in sorted(dir_acu_to[dom].keys()):
        tot = dir_acu_to[dom][forca]
        ac  = dir_acu_ac[dom][forca]
        hr  = ac / tot * 100
        delta = hr - bl_pct
        sinal = "+" if delta >= 0 else ""
        print(f"    forca={forca}/5  {tot:>8,} eventos  {hr:>7.1f}%  ({sinal}{delta:.1f}pp vs baseline)")
print("└" + "─"*55 + "┘")

print("\n┌─ ACURÁCIA POR POSIÇÃO (força ≥4/5) ──────────────────────────────────┐")
print(f"  {'Pos':>4}  {'F=4 events':>11}  {'F=4 rate':>9}  {'F=5 events':>11}  {'F=5 rate':>9}")
print("  " + "─"*54)
for p in range(15):
    row = [f"  N{p+1:02d}"]
    for f in (4, 5):
        tot = acu_pos_tot.get((p, f), 0)
        ac  = acu_por_pos.get((p, f), 0)
        if tot >= 5:
            hr  = ac / tot * 100
            row.append(f"  {tot:>11,}  {hr:>8.1f}%")
        else:
            row.append(f"  {'—':>11}  {'—':>9}")
    print("".join(row))
print("└" + "─"*54 + "┘")

print(f"\n┌─ PRESERVAÇÃO DE JACKPOT (filtro aplicado ao sorteio real) ───────────┐")
print(f"  Lógica: UP forte→ result>=prev | DOWN forte→ result<=prev")
print(f"  Violação: result vai CONTRA a direção, conta como 1 violação")
print()
print(f"  {'Tolerância':>12}  {'Concursos OK':>14}  {'% Preservados':>15}")
print("  " + "─"*48)
cumsum = 0
for tol in range(0, 12):
    q = viols_por_draw.get(tol, 0)
    cumsum += q
    pct = cumsum / total_draws * 100
    marcador = ""
    if tol == 0: marcador = "  ← máximo filtro"
    elif tol == 1: marcador = "  ← Nível 6"
    elif tol == 2: marcador = "  ← Nível 4/5"
    elif tol == 3: marcador = "  ← Nível 3"
    print(f"  tol ≤ {tol:>2}       {cumsum:>12,}       {pct:>12.1f}%{marcador}")
    if cumsum >= total_draws:
        break
print("└" + "─"*48 + "┘")

print(f"\n┌─ DISTRIBUIÇÃO DE VIOLAÇÕES POR CONCURSO ─────────────────────────────┐")
print(f"  {'Viols':>6}  {'Concursos':>10}  {'%':>7}  Histograma")
print("  " + "─"*50)
for v in sorted(viols_por_draw.keys()):
    q   = viols_por_draw[v]
    pct = q / total_draws * 100
    bar = "█" * max(1, int(pct / 1.5))
    print(f"  {v:>6}  {q:>10,}  {pct:>6.1f}%  {bar}")
print("└" + "─"*50 + "┘")

# ── 6. Resumo executivo ───────────────────────────────────────────────────────
print("\n" + "═"*72)
print("💡 RESUMO EXECUTIVO")
print("═"*72)

forte_tot = sum(acu_total.get(f, 0) for f in range(FORCA_FORTE, 6))
forte_ac  = sum(acu_acertos.get(f, 0) for f in range(FORCA_FORTE, 6))
hr_forte  = forte_ac / forte_tot * 100 if forte_tot else 0
delta_forte = hr_forte - bl_pct

pct_tol1 = (viols_por_draw.get(0, 0) + viols_por_draw.get(1, 0)) / total_draws * 100
pct_tol2 = sum(viols_por_draw.get(i, 0) for i in range(3)) / total_draws * 100

print(f"\n  Acurácia direcional (forte ≥{FORCA_FORTE}/5): {hr_forte:.1f}%  ({delta_forte:+.1f}pp vs baseline {bl_pct:.1f}%)")
print(f"  Preservação tol≤1 (Nível 6):    {pct_tol1:.1f}%")
print(f"  Preservação tol≤2 (Nível 4/5):  {pct_tol2:.1f}%")

if delta_forte >= 10:
    print(f"\n  ✅ HIPÓTESE CONFIRMADA FORTEMENTE (+{delta_forte:.1f}pp acima do baseline)")
    print(f"     O momentum direcional é um predictor FORTE e o filtro é justificado.")
elif delta_forte >= 5:
    print(f"\n  ✅ HIPÓTESE CONFIRMADA MODERADAMENTE (+{delta_forte:.1f}pp acima do baseline)")
    print(f"     O momentum direcional tem valor preditivo real.")
elif delta_forte >= 2:
    print(f"\n  ⚠️  HIPÓTESE FRACA (+{delta_forte:.1f}pp): sinal marginal, pode ser ruído.")
elif delta_forte >= 0:
    print(f"\n  ❌ SEM SINAL: {delta_forte:+.1f}pp vs baseline. Filtro pode não ter valor preditivo.")
else:
    print(f"\n  ❌ SINAL INVERTIDO ({delta_forte:.1f}pp): momentum PIORA a previsão!")
    print(f"     Considere desativar o filtro ou revisá-lo.")

print()
