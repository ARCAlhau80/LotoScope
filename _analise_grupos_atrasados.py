"""
Análise Estatística: "Grupos Atrasados" — Poder Preditivo Real
==============================================================
Grupos analisados:
  C1+C5 = colunas 1+5 do grid 5x5 → {1,6,11,16,21,5,10,15,20,25}
  L1+L5 = linhas 1+5 do grid 5x5  → {1,2,3,4,5,21,22,23,24,25}

Metodologia rigorosa: walk-forward (dados até T → prediz T+1).
"""

import pyodbc
import numpy as np
from collections import defaultdict, deque
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ─── Conexão ────────────────────────────────────────────────────────────────
CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
)

# ─── Definição dos grupos ────────────────────────────────────────────────────
# Grid 5x5: 
#   L1: 1  2  3  4  5
#   L2: 6  7  8  9  10
#   L3: 11 12 13 14 15
#   L4: 16 17 18 19 20
#   L5: 21 22 23 24 25
#   C1: 1  6  11 16 21
#   C5: 5  10 15 20 25
GRUPOS = {
    'C1+C5': frozenset([1,6,11,16,21, 5,10,15,20,25]),   # 10 números
    'L1+L5': frozenset([1,2,3,4,5, 21,22,23,24,25]),     # 10 números
}

def carregar_resultados():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("""
        SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
        FROM Resultados_INT
        ORDER BY Concurso
    """)
    rows = cur.fetchall()
    conn.close()
    resultados = []
    for row in rows:
        concurso = row[0]
        numeros = frozenset(row[1:16])
        resultados.append((concurso, numeros))
    print(f"✅ Carregados {len(resultados)} concursos (#{resultados[0][0]} → #{resultados[-1][0]})")
    return resultados

# ─── Análise walk-forward ─────────────────────────────────────────────────────
def calcular_acertos(grupo: frozenset, numeros_sorteio: frozenset) -> int:
    return len(grupo & numeros_sorteio)

def analisar_grupo_walk_forward(grupo_nome: str, grupo: frozenset, resultados: list, inicio_test: int = 3000):
    """
    Para cada draw t >= inicio_test:
      - Conhece histórico até (t-1)
      - Identifica quais hit_counts estão "atrasados" (overdue)
      - Verifica se o sorteio T cai em alguma dessas faixas atrasadas
    """
    print(f"\n{'='*60}")
    print(f"  GRUPO: {grupo_nome}  |  Números: {sorted(grupo)}")
    print(f"{'='*60}")

    # 1. Construir série histórica completa de hit counts
    serie_acertos = []
    for concurso, numeros in resultados:
        serie_acertos.append((concurso, calcular_acertos(grupo, numeros)))

    # 2. Distribuição global REAL (para referência)
    hit_counts_todos = [h for _, h in serie_acertos]
    freq_global = defaultdict(int)
    for h in hit_counts_todos:
        freq_global[h] += 1
    total_global = len(hit_counts_todos)
    
    print("\n📊 Distribuição Global (todos os concursos):")
    print(f"  {'Hit':>4}  {'Count':>6}  {'%':>7}  {'Esperado Hiper':>15}")
    # Esperado pela distribuição hipergeométrica: C(10,k)*C(15,15-k)/C(25,15)
    from math import comb
    total_combos = comb(25, 15)
    grupo_size = len(grupo)
    fora_size = 25 - grupo_size
    for hval in sorted(freq_global.keys()):
        obs_pct = freq_global[hval] / total_global * 100
        # hipergeométrica
        k_min = max(0, 15 - fora_size)
        k_max = min(grupo_size, 15)
        if k_min <= hval <= k_max:
            hip_prob = comb(grupo_size, hval) * comb(fora_size, 15 - hval) / total_combos * 100
        else:
            hip_prob = 0.0
        print(f"  {hval:>4}  {freq_global[hval]:>6}  {obs_pct:>6.2f}%  {hip_prob:>14.2f}%")

    # 3. Top-3 hit counts mais comuns (baseline)
    top3 = sorted(freq_global.keys(), key=lambda x: -freq_global[x])[:3]
    top3_cobertura = sum(freq_global[h] for h in top3) / total_global
    print(f"\n  Top-3 mais frequentes: {top3}  →  cobertura: {top3_cobertura*100:.1f}%")

    # 4. Walk-forward: para cada concurso de teste, verificar predição "atrasado"
    # Indexar para busca rápida
    idx_inicio = next(i for i, (c, _) in enumerate(serie_acertos) if c >= inicio_test)
    
    resultados_predicao = []  # (concurso, hit_count_real, atrasado_acertou, top3_acertou)
    
    for t in range(idx_inicio, len(serie_acertos)):
        concurso_t, hit_real = serie_acertos[t]
        
        # Histórico disponível: indices 0..t-1
        hist = [h for _, h in serie_acertos[:t]]
        if len(hist) < 50:
            continue
        
        # ─── Calcular "atrasado" ────────────────────────────────────────────
        # Para cada hit_count no top3, calcular o intervalo médio entre ocorrências
        # e quantos sorteios se passaram desde a última ocorrência
        
        atrasado_set = set()
        for hval in top3:
            # Posições onde esse hit_count apareceu
            posicoes = [i for i, h in enumerate(hist) if h == hval]
            if len(posicoes) < 2:
                continue
            # Intervalos entre ocorrências consecutivas
            intervalos = [posicoes[i+1] - posicoes[i] for i in range(len(posicoes)-1)]
            media_intervalo = np.mean(intervalos)
            std_intervalo = np.std(intervalos)
            # Atraso atual: sorteios desde a última ocorrência
            ultima_pos = posicoes[-1]
            atraso_atual = (t - 1) - ultima_pos  # quanto se passou desde a última vez
            # Critério: atrasado se atraso_atual > media + 0.5*std
            limiar = media_intervalo + 0.5 * std_intervalo
            if atraso_atual >= media_intervalo:
                atrasado_set.add(hval)
        
        # Estratégia A: top3 → acertou?
        top3_acertou = 1 if hit_real in top3 else 0
        
        # Estratégia B: atrasados dentro do top3 → acertou?
        if len(atrasado_set) > 0:
            atrasado_acertou = 1 if hit_real in atrasado_set else 0
            n_atrasados = len(atrasado_set)
        else:
            atrasado_acertou = None  # sem sinal
            n_atrasados = 0
        
        resultados_predicao.append({
            'concurso': concurso_t,
            'hit_real': hit_real,
            'top3_acertou': top3_acertou,
            'atrasado_acertou': atrasado_acertou,
            'n_atrasados': n_atrasados,
            'atrasado_set': frozenset(atrasado_set),
        })
    
    # 5. Calcular métricas
    n_total = len(resultados_predicao)
    n_top3_certo = sum(r['top3_acertou'] for r in resultados_predicao)
    
    pred_com_sinal = [r for r in resultados_predicao if r['atrasado_acertou'] is not None]
    n_sinal = len(pred_com_sinal)
    n_atrasado_certo = sum(r['atrasado_acertou'] for r in pred_com_sinal)
    
    taxa_top3 = n_top3_certo / n_total if n_total else 0
    taxa_atrasado = n_atrasado_certo / n_sinal if n_sinal else 0
    
    # Baseline random: se apostamos em X hit_counts de forma aleatória (igual ao top3 coverage)
    baseline_random = top3_cobertura
    
    print(f"\n📈 RESULTADOS WALK-FORWARD (concursos {inicio_test}+, n={n_total}):")
    print(f"  {'Estratégia':<35}  {'Acertos':>8}  {'Total':>8}  {'Taxa':>8}  {'vs Random':>10}")
    print(f"  {'-'*35}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*10}")
    print(f"  {'[A] Top-3 sempre':<35}  {n_top3_certo:>8}  {n_total:>8}  {taxa_top3*100:>7.1f}%  {(taxa_top3-baseline_random)*100:>+9.1f}pp")
    print(f"  {'[B] Atrasados (com sinal, n='+str(n_sinal)+')':<35}  {n_atrasado_certo:>8}  {n_sinal:>8}  {taxa_atrasado*100:>7.1f}%  {(taxa_atrasado-baseline_random)*100:>+9.1f}pp")
    print(f"  {'[C] Baseline random (top3 coverage)':<35}  {'':>8}  {'':>8}  {baseline_random*100:>7.1f}%  {'0.0pp':>10}")
    
    # 6. Tamanho médio do sinal (quantos atrasados por vez)
    tamanho_medio_sinal = np.mean([r['n_atrasados'] for r in pred_com_sinal]) if pred_com_sinal else 0
    baseline_sinal = tamanho_medio_sinal / 3 * top3_cobertura  # baseline proporcional
    
    print(f"\n  Tamanho médio do sinal: {tamanho_medio_sinal:.2f} hit_counts por vez")
    print(f"  Baseline proporcional (sinal): {baseline_sinal*100:.1f}%")
    
    # 7. Teste qui-quadrado: atrasado vs not-atrasado para o próximo sorteio
    # Tabela de contingência
    # Queremos testar: P(hit_real in atrasado | atrasado_set) vs P(hit_real in atrasado | não_atrasado)
    if pred_com_sinal:
        # Construir tabela 2x2
        # Célula [0,0]: tem sinal E acertou
        # Célula [0,1]: tem sinal E errou
        # Célula [1,0]: sem sinal mas o hit seria "atrasado" (não aplicável diretamente)
        # Usar teste binomial
        from scipy.stats import binomtest, chi2_contingency
        
        # Teste: taxa_atrasado vs baseline_random
        result_binom = binomtest(n_atrasado_certo, n_sinal, baseline_random, alternative='greater')
        p_value_binom = result_binom.pvalue
        
        print(f"\n🔬 SIGNIFICÂNCIA ESTATÍSTICA:")
        print(f"  H0: taxa_atrasado = baseline_random = {baseline_random*100:.1f}%")
        print(f"  H1: taxa_atrasado > baseline_random")
        print(f"  p-value (binomial one-sided): {p_value_binom:.4f}")
        if p_value_binom < 0.01:
            print(f"  → 🟢 SIGNIFICATIVO (p<0.01): o sinal TEM poder preditivo real!")
        elif p_value_binom < 0.05:
            print(f"  → 🟡 MARGINALMENTE SIGNIFICATIVO (0.01<p<0.05)")
        else:
            print(f"  → 🔴 NÃO SIGNIFICATIVO (p>0.05): sinal sem poder preditivo")
    
    # 8. Análise temporal: sinal dura quantos sorteios?
    # Verificar se o sinal t=0 ainda vale para t+1, t+2, ..., t+k
    print(f"\n⏰ PERSISTÊNCIA DO SINAL (quantos sorteios à frente é válido?):")
    print(f"  {'Horizonte':>10}  {'Taxa':>8}  {'vs Baseline':>12}")
    
    for horizonte in [1, 2, 3, 5, 10]:
        acertos_h = 0
        total_h = 0
        for i, r in enumerate(resultados_predicao):
            # Só quando há sinal no momento t
            if r['atrasado_acertou'] is None:
                continue
            # Verificar se o sorteio t+horizonte cai no atrasado_set definido em t
            idx_futuro = resultados_predicao.index(r) + horizonte
            if idx_futuro >= len(resultados_predicao):
                continue
            future = resultados_predicao[idx_futuro]
            if future['hit_real'] in r['atrasado_set']:
                acertos_h += 1
            total_h += 1
        
        if total_h > 0:
            taxa_h = acertos_h / total_h
            print(f"  {'+'+str(horizonte)+' sorteio(s)':>10}  {taxa_h*100:>7.1f}%  {(taxa_h-baseline_random)*100:>+11.1f}pp")
    
    return {
        'grupo': grupo_nome,
        'n_total': n_total,
        'n_sinal': n_sinal,
        'taxa_top3': taxa_top3,
        'taxa_atrasado': taxa_atrasado,
        'baseline': baseline_random,
        'edge': taxa_atrasado - baseline_random,
        'top3': top3,
        'top3_cobertura': top3_cobertura,
    }

# ─── Análise extra: C2+C4 e L2+L4 (colunas/linhas centrais) ─────────────────
GRUPOS_EXTRA = {
    'C2+C4': frozenset([2,7,12,17,22, 4,9,14,19,24]),
    'L2+L4': frozenset([6,7,8,9,10, 16,17,18,19,20]),
    'C3':    frozenset([3,8,13,18,23]),  # coluna central (5 números)
    'L3':    frozenset([11,12,13,14,15]), # linha central (5 números)
}

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   ANÁLISE: PODER PREDITIVO DE GRUPOS ATRASADOS - LOTOFÁCIL  ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    resultados = carregar_resultados()
    
    sumario = []
    
    # Grupos principais
    for nome, grupo in GRUPOS.items():
        res = analisar_grupo_walk_forward(nome, grupo, resultados, inicio_test=3000)
        sumario.append(res)
    
    # ─── Sumário Final ───────────────────────────────────────────────────────
    print(f"\n\n{'='*65}")
    print("  SUMÁRIO FINAL — PODER PREDITIVO 'GRUPOS ATRASADOS'")
    print(f"{'='*65}")
    print(f"  {'Grupo':<10}  {'A:Top3':>8}  {'B:Atras':>8}  {'Random':>8}  {'Edge':>8}  {'Veredicto'}")
    print(f"  {'-'*10}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*15}")
    for r in sumario:
        edge = r['edge']
        if edge > 0.05:
            veredicto = "✅ REAL"
        elif edge > 0.02:
            veredicto = "⚠️ MARGINAL"
        else:
            veredicto = "❌ NENHUM"
        print(f"  {r['grupo']:<10}  {r['taxa_top3']*100:>7.1f}%  {r['taxa_atrasado']*100:>7.1f}%  {r['baseline']*100:>7.1f}%  {edge*100:>+7.1f}pp  {veredicto}")
    
    print(f"\n{'='*65}")
    print("  RECOMENDAÇÃO PARA REDE NEURAL:")
    
    has_real_edge = any(r['edge'] > 0.03 for r in sumario)
    has_significant = any(r['edge'] > 0.02 for r in sumario)
    
    if has_real_edge:
        print("""
  ✅ INCLUIR como feature na rede neural.
  
  Feature sugerida por grupo:
    - 'atraso_normalizado_C1C5':  (atraso_atual - media_intervalo) / std_intervalo
    - 'atraso_normalizado_L1L5':  idem para L1+L5
    
  Edge real encontrado → features de atraso têm sinal preditivo > 3pp acima random.
  Recomendação: adicionar ao vetor de 6 features por número no modelo neural.
""")
    elif has_significant:
        print("""
  ⚠️ EDGE MARGINAL: incluir com cautela.
  
  O edge está entre 2-3pp — estatisticamente fraco mas pode combinar com outros.
  Testar: adicionar como feature auxiliar e medir impacto no out-of-sample do modelo.
""")
    else:
        print("""
  ❌ NÃO INCLUIR na rede neural.
  
  O conceito de "grupos atrasados" não demonstrou poder preditivo estatístico.
  O sinal é ruído — não melhora previsões acima do baseline aleatório.
  Não vale adicionar complexidade ao modelo por um ganho inexistente.
""")
    
    print("═"*65)

if __name__ == '__main__':
    main()
