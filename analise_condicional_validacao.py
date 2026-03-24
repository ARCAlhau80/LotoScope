"""
Validação estatística da análise condicional de padrões Q/F
Executar ANTES de manter o código no menu.
"""
import pyodbc
from collections import Counter
import math

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("""
    SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT ORDER BY Concurso DESC
""")
resultados = [{'concurso': r[0], 'numeros': list(r[1:16]), 'set': set(r[1:16])} for r in cursor.fetchall()]
conn.close()
print(f"Base: {len(resultados)} concursos  |  Último: {resultados[0]['concurso']}")

# ─── ALGORITMO INVERTIDA v3.0 ────────────────────────────────────────────────
def calcular_top2(res_anteriores):
    freq5  = Counter()
    for r in res_anteriores[:min(5,  len(res_anteriores))]: freq5.update(r['set'])
    freq50 = Counter()
    for r in res_anteriores[:min(50, len(res_anteriores))]: freq50.update(r['set'])
    n5  = min(5,  len(res_anteriores))
    n50 = min(50, len(res_anteriores))

    cands = []
    for n in range(1, 26):
        fc = freq5.get(n, 0) / n5  * 100
        fl = freq50.get(n, 0) / n50 * 100
        ideb = fl - fc
        cons, apare = 0, any(n in r['set'] for r in res_anteriores[:3])
        for r in res_anteriores[:15]:
            if n in r['set']: cons += 1
            else: break
        s = 0
        if   cons >= 10: s -= 5
        elif cons >= 5:  s += 6
        elif cons >= 4:  s += 5
        elif cons >= 3 and fc >= 80: s += 4
        elif cons >= 3:  s += 3
        elif fc >= 100:  s += 4
        elif fc >= 80 and apare: s += 3
        elif ideb < -35: s += 2
        elif ideb < -25: s += 1
        elif ideb >= 0:  s -= 2
        else:            s -= 1
        if fc > 80: s += 1
        cands.append({'num': n, 'score': s, 'cons': cons, 'fc': fc})

    quentes = sorted(cands, key=lambda x: (-x['score'], -x['cons'], -x['fc']))
    frios   = sorted(cands, key=lambda x:  (x['score'],  x['cons'],  x['fc']))
    return [quentes[0]['num'], quentes[1]['num']], [frios[0]['num'], frios[1]['num']]

# ─── CALCULAR HISTÓRICO ───────────────────────────────────────────────────────
N_ANALISE = 200
dados = []
for i in range(N_ANALISE):
    if i + 51 >= len(resultados): break
    sorteados = resultados[i]['set']
    res_ant   = resultados[i+1:i+51]
    top2_q, top2_f = calcular_top2(res_ant)
    qa = sum(1 for n in top2_q if n not in sorteados)
    fa = sum(1 for n in top2_f if n not in sorteados)
    dados.append({
        'c': resultados[i]['concurso'],
        'qa': qa, 'fa': fa,
        'q_ok': qa==2, 'q_p': qa==1, 'q_e': qa==0,
        'f_ok': fa==2, 'f_p': fa==1, 'f_e': fa==0,
        'top2_q': top2_q, 'top2_f': top2_f,
    })

N = len(dados)
print(f"\n{'='*70}")
print(f"ANÁLISE CONDICIONAL — {N} concursos")
print(f"{'='*70}\n")

# ─── 1. DISTRIBUIÇÃO GERAL ───────────────────────────────────────────────────
q_ok = sum(1 for d in dados if d['q_ok'])
q_p  = sum(1 for d in dados if d['q_p'])
q_e  = sum(1 for d in dados if d['q_e'])
f_ok = sum(1 for d in dados if d['f_ok'])
f_p  = sum(1 for d in dados if d['f_p'])
f_e  = sum(1 for d in dados if d['f_e'])

print("1. DISTRIBUIÇÃO DE ESTADOS (2/2 excluídos ficaram fora do sorteio)")
print(f"   {'':5} {'OK(2/2)':>12} {'P(1/2)':>10} {'E(0/2)':>10}   N")
print(f"   {'Q🔥':5} {q_ok:>5}({q_ok/N*100:4.0f}%) {q_p:>5}({q_p/N*100:4.0f}%) {q_e:>5}({q_e/N*100:4.0f}%) {N}")
print(f"   {'F❄️':5} {f_ok:>5}({f_ok/N*100:4.0f}%) {f_p:>5}({f_p/N*100:4.0f}%) {f_e:>5}({f_e/N*100:4.0f}%) {N}")
# Baseline aleatório: escolher 2 de 25, sorteiam 15 → P(ambos fora) = C(10,2)/C(25,2) ≈ 15%
p_base_ok = (10*9)/(25*24)
p_base_p  = 2*(15*10)/(25*24)
p_base_e  = (15*14)/(25*24)
print(f"   {'Random':8} {p_base_ok*100:>8.1f}%   {p_base_p*100:>8.1f}%   {p_base_e*100:>8.1f}%")
print(f"   → Q supera random em OK: +{(q_ok/N - p_base_ok)*100:.1f}pp")

# ─── 2. COMPLEMENTARIDADE ─────────────────────────────────────────────────────
print("\n2. COMPLEMENTARIDADE Q × F (mesmo concurso)")
qe_fok = sum(1 for d in dados if d['q_e'] and d['f_ok'])
qe_fp  = sum(1 for d in dados if d['q_e'] and d['f_p'])
qe_fe  = sum(1 for d in dados if d['q_e'] and d['f_e'])
qok_fe = sum(1 for d in dados if d['q_ok'] and d['f_e'])
amb_ok = sum(1 for d in dados if d['q_ok'] and d['f_ok'])
amb_e  = sum(1 for d in dados if d['q_e'] and d['f_e'])

if q_e:
    print(f"   Quando Q errou(0/2):")
    print(f"     → F perfeito : {qe_fok:3d}/{q_e} = {qe_fok/q_e*100:.0f}%  (esperado aleatório: {p_base_ok*100:.0f}%)")
    print(f"     → F parcial  : {qe_fp:3d}/{q_e} = {qe_fp/q_e*100:.0f}%")
    print(f"     → Ambos erram: {qe_fe:3d}/{q_e} = {qe_fe/q_e*100:.0f}%")
    diff_comp = qe_fok/q_e - p_base_ok
    print(f"     → GANHO vs random: {diff_comp*100:+.1f}pp  {'✅ VÁLIDO' if diff_comp > 0.05 else '⚠️ FRACO' if diff_comp > 0 else '❌ INVÁLIDO'}")
if q_ok:
    print(f"   Quando Q acertou(2/2): F errou = {qok_fe}/{q_ok} = {qok_fe/q_ok*100:.0f}%  (esperado: {p_base_e*100:.0f}%)")
print(f"   Ambos OK: {amb_ok}/{N}={amb_ok/N*100:.0f}%  |  Ambos ERRAM: {amb_e}/{N}={amb_e/N*100:.0f}%")

# ─── 3. MATRIZ DE TRANSIÇÃO ───────────────────────────────────────────────────
print("\n3. MATRIZ DE TRANSIÇÃO Q (estado atual → próximo concurso)")
def est(d):
    if d['q_ok']: return 'OK'
    if d['q_p']:  return 'P'
    return 'E'

trans  = {'OK':{'OK':0,'P':0,'E':0},'P':{'OK':0,'P':0,'E':0},'E':{'OK':0,'P':0,'E':0}}
totais = {'OK':0,'P':0,'E':0}
for i in range(N-1):
    e_ant  = est(dados[i+1])  # lista DESC: dados[i+1] é concurso ANTERIOR no tempo
    e_prox = est(dados[i])    # dados[i] é o PRÓXIMO (mais recente)
    trans[e_ant][e_prox] += 1
    totais[e_ant] += 1

print(f"   {'Est.Atual':>10}  {'→OK':>8}  {'→P':>8}  {'→E':>8}   N  |  Baseline OK={q_ok/N*100:.0f}%")
print("   " + "─"*60)
for e, lbl in [('OK','✅ OK'), ('P','⚠️  P'), ('E','❌ E')]:
    t = totais[e]
    if t == 0: continue
    p_ok_cond = trans[e]['OK']/t
    diff = p_ok_cond - q_ok/N
    sinal = f"{'↑+' if diff > 0.05 else '↓' if diff < -0.05 else '='}{abs(diff)*100:.0f}pp"
    print(f"   {lbl:>10}  {trans[e]['OK']:3d}({p_ok_cond*100:4.0f}%) {trans[e]['P']:3d}({trans[e]['P']/t*100:4.0f}%) {trans[e]['E']:3d}({trans[e]['E']/t*100:4.0f}%)  {t:3d}  | vs base: {sinal}")

# ─── 4. TESTES DE SIGNIFICÂNCIA (chi-quadrado aproximado) ─────────────────────
print("\n4. SIGNIFICÂNCIA ESTATÍSTICA (chi-quadrado nas transições)")
for e_from in ['OK', 'E']:
    t = totais[e_from]
    if t < 10: continue
    # Esperado: distribuição marginal
    chi2 = 0
    for e_to in ['OK', 'P', 'E']:
        obs = trans[e_from][e_to]
        esp = t * {'OK': q_ok/N, 'P': q_p/N, 'E': q_e/N}[e_to]
        chi2 += (obs - esp)**2 / max(esp, 0.001)
    # chi2 com 2 graus de liberdade: p<0.05 se chi2>5.99, p<0.10 se chi2>4.61
    sig = "p<0.05 ✅" if chi2 > 5.99 else ("p<0.10 ⚠️" if chi2 > 4.61 else "n.s. ❌ (não significativo)")
    print(f"   Após {e_from}: chi2={chi2:.2f}  →  {sig}")

# ─── 5. SEQUÊNCIAS ───────────────────────────────────────────────────────────
print("\n5. SEQUÊNCIAS CONSECUTIVAS DO MESMO ESTADO")
estados_cron = [est(d) for d in reversed(dados)]

def runs(estados, tipo):
    lens, cur = [], 0
    for e in estados:
        if e == tipo: cur += 1
        elif cur > 0: lens.append(cur); cur = 0
    if cur > 0: lens.append(cur)
    return lens

ro = runs(estados_cron, 'OK')
re = runs(estados_cron, 'E')
rp = runs(estados_cron, 'P')
print(f"   OK: ocorrências={len(ro)}  média={sum(ro)/len(ro):.1f}  max={max(ro) if ro else 0}  dist: {sorted(ro,reverse=True)[:8]}")
print(f"   E:  ocorrências={len(re)}  média={sum(re)/len(re):.1f}  max={max(re) if re else 0}  dist: {sorted(re,reverse=True)[:8]}")

# ─── 6. RESUMO / VEREDITO ────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("VEREDITO")
print(f"{'='*70}")

# Complementaridade: válida se F cobre Q em muito mais de 15% dos erros de Q
comp_valida = q_e > 0 and (qe_fok/q_e) > (p_base_ok + 0.05)
# Transição E→OK: válida se P(OK | prev=E) > P(OK) + 5pp
trans_e_ok_valida = totais['E'] > 5 and (trans['E']['OK']/totais['E']) > (q_ok/N + 0.05)
# Transição OK→OK: válida se P(OK | prev=OK) > P(OK) + 5pp
trans_ok_ok_valida = totais['OK'] > 5 and (trans['OK']['OK']/totais['OK']) > (q_ok/N + 0.05)

print(f"  Complementaridade F cobre Q: {'✅ VÁLIDA — F supera random quando Q erra' if comp_valida else '❌ INVÁLIDA — F não adiciona informação útil'}")
print(f"  Transição E→OK (recupera após erro): {'✅ VÁLIDA — P(recuperar) > baseline' if trans_e_ok_valida else '❌ INVÁLIDA — não há efeito de recuperação'}")
print(f"  Transição OK→OK (mantém após acerto): {'✅ VÁLIDA — acerto atual prevê próximo' if trans_ok_ok_valida else '❌ INVÁLIDA — acerto atual não prevê nada'}")

if not (comp_valida or trans_e_ok_valida or trans_ok_ok_valida):
    print("\n  ⛔ CONCLUSÃO: Nenhum padrão condicional válido — REMOVER o bloco do menu.")
elif sum([comp_valida, trans_e_ok_valida, trans_ok_ok_valida]) >= 2:
    print("\n  ✅ CONCLUSÃO: Padrões suficientemente válidos — MANTER o bloco no menu.")
else:
    print("\n  ⚠️  CONCLUSÃO: Resultados parciais — manter com ressalva explícita de baixa confiança.")
