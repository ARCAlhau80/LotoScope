"""
Análise Estatística CORRIGIDA: "Grupos Atrasados" — Poder Preditivo Real
=========================================================================
CORREÇÃO CRÍTICA: a comparação correta é:

Para cada draw t com sinal "atrasado":
  - atrasado_set = {hit_counts selecionados como atrasados dentro top-3}
  - expected_rate = Σ global_freq[v] para v em atrasado_set  (baseline sem predição)
  - observed:  1 se hit_real in atrasado_set, 0 caso contrário

H0:  P(observed) = expected_rate   (sinal = distribuição histórica)
H1:  P(observed) > expected_rate   (sinal MELHORA a previsão)

Grupos:
  C1+C5 = {1,6,11,16,21,5,10,15,20,25}  (10 números)
  L1+L5 = {1,2,3,4,5,21,22,23,24,25}    (10 números)
"""

import pyodbc
import numpy as np
from collections import defaultdict
from scipy.stats import binomtest, chi2_contingency
import warnings
warnings.filterwarnings('ignore')

CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
)

GRUPOS = {
    'C1+C5': frozenset([1,6,11,16,21, 5,10,15,20,25]),
    'L1+L5': frozenset([1,2,3,4,5, 21,22,23,24,25]),
}

def carregar_resultados():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("""
        SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
        FROM Resultados_INT ORDER BY Concurso
    """)
    rows = cur.fetchall()
    conn.close()
    resultados = [(row[0], frozenset(row[1:16])) for row in rows]
    print(f"✅ Carregados {len(resultados)} concursos (#{resultados[0][0]} → #{resultados[-1][0]})")
    return resultados


def analisar_grupo(grupo_nome: str, grupo: frozenset, resultados: list, inicio_test: int = 3000):
    print(f"\n{'='*65}")
    print(f"  GRUPO: {grupo_nome}  |  {len(grupo)} números: {sorted(grupo)}")
    print(f"{'='*65}")

    # Série de hit counts
    serie = [(c, len(grupo & nums)) for c, nums in resultados]

    # Distribuição global (frequências relativas)
    todos_hits = [h for _, h in serie]
    freq_global = defaultdict(int)
    for h in todos_hits:
        freq_global[h] += 1
    N_total = len(todos_hits)
    prob_global = {k: v/N_total for k, v in freq_global.items()}

    # Top-3 valores mais frequentes
    top3 = sorted(freq_global.keys(), key=lambda x: -freq_global[x])[:3]
    top3_set = set(top3)
    top3_prob = sum(prob_global[h] for h in top3)

    print(f"\n📊 Distribuição Global:")
    print(f"  {'Hit':>4}  {'Freq':>7}  {'P(hit)':>8}")
    for hval in sorted(prob_global.keys()):
        marker = " ◀ top3" if hval in top3_set else ""
        print(f"  {hval:>4}  {freq_global[hval]:>7}  {prob_global[hval]*100:>7.2f}%{marker}")
    print(f"\n  Top-3: {top3}  (cobertura {top3_prob*100:.1f}%)")

    # Índice de início dos testes
    idx_inicio = next(i for i, (c, _) in enumerate(serie) if c >= inicio_test)
    n_test = len(serie) - idx_inicio
    print(f"  Janela de teste: concursos {inicio_test}+ → {n_test} draws")

    # ─── Walk-forward ─────────────────────────────────────────────────────────
    # Para cada draw t (teste), usando dados até t-1:
    #   → identificar atrasado_set ⊆ top3
    #   → verificar se hit_real ∈ atrasado_set
    #   → comparar com expected_rate = Σ prob_global[v] para v em atrasado_set

    registros = []   # (hit_real, atrasado_set, expected_rate)
    
    for t in range(idx_inicio, len(serie)):
        concurso_t, hit_real = serie[t]
        hist = [h for _, h in serie[:t]]  # dados até t-1

        atrasado_set = set()
        for hval in top3:
            posicoes = [i for i, h in enumerate(hist) if h == hval]
            if len(posicoes) < 3:
                continue
            intervalos = [posicoes[i+1] - posicoes[i] for i in range(len(posicoes)-1)]
            media = np.mean(intervalos)
            ultima_pos = posicoes[-1]
            atraso_atual = (t - 1) - ultima_pos
            if atraso_atual >= media:
                atrasado_set.add(hval)
        
        if not atrasado_set:
            continue

        expected_rate = sum(prob_global.get(v, 0) for v in atrasado_set)
        hit_in_atrasado = 1 if hit_real in atrasado_set else 0
        registros.append((concurso_t, hit_real, frozenset(atrasado_set), expected_rate, hit_in_atrasado))

    # ─── Métricas Gerais ──────────────────────────────────────────────────────
    n_sinal = len(registros)
    n_acertou = sum(r[4] for r in registros)
    observed_rate = n_acertou / n_sinal
    # Baseline correto: média das expected_rates (varia porque atrasado_set muda)
    avg_expected = np.mean([r[3] for r in registros])
    edge = observed_rate - avg_expected

    print(f"\n📈 RESULTADO CORRETO (sinal vs baseline proporcional):")
    print(f"  Concursos com sinal:   {n_sinal} de {n_test} ({n_sinal/n_test*100:.1f}% dos draws)")
    print(f"  Tamanho médio do sinal:{np.mean([len(r[2]) for r in registros]):.2f} hit_counts/vez")
    print(f"  Taxa observada:        {observed_rate*100:.2f}%  (acertou {n_acertou} de {n_sinal})")
    print(f"  Baseline esperado:     {avg_expected*100:.2f}%  (distribuição histórica)")
    print(f"  EDGE:                  {edge*100:+.2f}pp")

    # ─── Teste estatístico correto ─────────────────────────────────────────────
    # Teste binomial: H0: P(hit ∈ atrasado_set) = avg_expected
    # (approx — baseline varia, usamos a média como H0)
    bt = binomtest(n_acertou, n_sinal, avg_expected, alternative='greater')
    p_value = bt.pvalue

    print(f"\n🔬 SIGNIFICÂNCIA ESTATÍSTICA:")
    print(f"  Teste binomial one-sided (H1: observed > baseline)")
    print(f"  H0: P = {avg_expected*100:.2f}%  → H1: P > {avg_expected*100:.2f}%")
    print(f"  p-value: {p_value:.4f}")
    if p_value < 0.01:
        sig = "🟢 SIGNIFICATIVO (p<0.01) — o sinal tem poder preditivo real!"
    elif p_value < 0.05:
        sig = "🟡 MARGINAL (0.01<p<0.05)"
    else:
        sig = "🔴 NÃO SIGNIFICATIVO (p>0.05) — sinal é ruído"
    print(f"  → {sig}")

    # ─── Análise por hit_count individual ──────────────────────────────────────
    print(f"\n🔍 POR HIT COUNT (dentro dos registros com sinal):")
    print(f"  {'HitCount':>9}  {'N_sinal':>8}  {'Obs%':>8}  {'Exp%':>8}  {'Edge':>8}")
    for hval in TOP3 if (TOP3 := top3) else top3:
        subs = [r for r in registros if hval in r[2]]
        if not subs:
            continue
        obs = sum(1 for r in subs if r[1] == hval) / len(subs)
        exp = prob_global.get(hval, 0)
        print(f"  {hval:>9}  {len(subs):>8}  {obs*100:>7.2f}%  {exp*100:>7.2f}%  {(obs-exp)*100:>+7.2f}pp")

    # ─── Persistência temporal ────────────────────────────────────────────────
    print(f"\n⏰ PERSISTÊNCIA DO SINAL (t+k sorteios à frente):")
    print(f"  {'Horizonte':>12}  {'Obs%':>8}  {'Exp%':>8}  {'Edge':>9}  {'p-value':>9}")
    reg_indexed = {r[0]: r for r in registros}
    conc_list = [r[0] for r in registros]
    
    for k in [1, 2, 3, 5, 10]:
        acertos_k = 0
        total_k = 0
        exp_rates_k = []
        for i, r in enumerate(registros):
            conc_atual = r[0]
            # Encontrar concurso t+k na série original
            idx_atual = next((j for j, (c, _) in enumerate(serie) if c == conc_atual), None)
            if idx_atual is None or idx_atual + k >= len(serie):
                continue
            hit_futuro = serie[idx_atual + k][1]
            if hit_futuro in r[2]:
                acertos_k += 1
            total_k += 1
            exp_rates_k.append(r[3])
        
        if total_k == 0:
            continue
        obs_k = acertos_k / total_k
        exp_k = np.mean(exp_rates_k)
        edge_k = obs_k - exp_k
        bt_k = binomtest(acertos_k, total_k, exp_k, alternative='greater')
        print(f"  {'+'+str(k)+' draw(s)':>12}  {obs_k*100:>7.2f}%  {exp_k*100:>7.2f}%  {edge_k*100:>+8.2f}pp  {bt_k.pvalue:>9.4f}")

    # ─── Análise por subperíodo ───────────────────────────────────────────────
    print(f"\n📅 ANÁLISE POR SUBPERÍODO (degrada ao longo do tempo?):")
    periodos = [
        ("3000–3200", 3000, 3200),
        ("3201–3400", 3201, 3400),
        ("3401–3657", 3401, 9999),
    ]
    print(f"  {'Período':>14}  {'N_sinal':>8}  {'Obs%':>8}  {'Exp%':>8}  {'Edge':>9}")
    for nome_p, p_min, p_max in periodos:
        subs = [r for r in registros if p_min <= r[0] <= p_max]
        if not subs:
            continue
        obs_p = np.mean([r[4] for r in subs])
        exp_p = np.mean([r[3] for r in subs])
        print(f"  {nome_p:>14}  {len(subs):>8}  {obs_p*100:>7.2f}%  {exp_p*100:>7.2f}%  {(obs_p-exp_p)*100:>+8.2f}pp")

    return {
        'grupo': grupo_nome,
        'n_sinal': n_sinal,
        'n_test': n_test,
        'observed_rate': observed_rate,
        'avg_expected': avg_expected,
        'edge': edge,
        'p_value': p_value,
        'top3_prob': top3_prob,
        'top3': top3,
    }


def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   ANÁLISE RIGOROSA: PODER PREDITIVO 'GRUPOS ATRASADOS'          ║")
    print("║   Metodologia: Walk-forward + Comparison Correta                ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    resultados = carregar_resultados()

    sumario = []
    for nome, grupo in GRUPOS.items():
        res = analisar_grupo(nome, grupo, resultados, inicio_test=3000)
        sumario.append(res)

    print(f"\n\n{'='*65}")
    print("  SUMÁRIO FINAL — ANÁLISE RIGOROSA")
    print(f"{'='*65}")
    print(f"  {'Grupo':<10}  {'N_sinal':>8}  {'Obs%':>7}  {'Exp%':>7}  {'Edge':>8}  {'p-val':>8}  {'Veredicto'}")
    print(f"  {'-'*10}  {'-'*8}  {'-'*7}  {'-'*7}  {'-'*8}  {'-'*8}  {'-'*15}")
    for r in sumario:
        if r['p_value'] < 0.01 and r['edge'] > 0.02:
            v = "✅ REAL (p<0.01)"
        elif r['p_value'] < 0.05 and r['edge'] > 0.01:
            v = "⚠️ MARGINAL"
        else:
            v = "❌ RUÍDO"
        print(f"  {r['grupo']:<10}  {r['n_sinal']:>8}  {r['observed_rate']*100:>6.2f}%  {r['avg_expected']*100:>6.2f}%  {r['edge']*100:>7.2f}pp  {r['p_value']:>8.4f}  {v}")

    print(f"\n{'='*65}")
    print("  VEREDICTO FINAL:")
    
    real_edges = [r for r in sumario if r['p_value'] < 0.05 and r['edge'] > 0.01]
    if real_edges:
        best = max(real_edges, key=lambda r: r['edge'])
        print(f"""
  ⚠️/✅ EDGE DETECTADO em {best['grupo']}: +{best['edge']*100:.2f}pp (p={best['p_value']:.4f})
  
  Recomendação para rede neural:
  → INCLUIR como feature experimental: 'atraso_norm_{best['grupo'].replace('+','')}'
  → Calcular: (atraso_atual - media_intervalo) / std_intervalo  para cada hit_count no top3
  → Impacto esperado: pequeno (+{best['edge']*100:.1f}pp sobre baseline estático)
  → Prioridade: BAIXA — não justifica mudar arquitetura atual
""")
    else:
        print("""
  ❌ NÃO INCLUIR na rede neural.
  
  Conclusão: O conceito "grupos atrasados" NÃO tem poder preditivo estatístico.
  - Sinal observado é consistente com distribuição histórica estática
  - p-value > 0.05 para todos os grupos testados
  - Edge próximo de zero em todos os horizontes testados
  
  A lei dos grandes números se aplica aqui: saber que um hit_count está "atrasado"
  NÃO aumenta a probabilidade de ocorrer no PRÓXIMO sorteio.
  Cada sorteio é independente — o passado não influencia o futuro.
""")
    
    print("═"*65)


if __name__ == '__main__':
    main()
