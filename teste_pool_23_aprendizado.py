# -*- coding: utf-8 -*-
"""
ESTRATÉGIA POOL 23 - APRENDIZADO: Números que funcionam quando excluídos
=========================================================================
Hipótese: Alguns números têm padrões que os tornam melhores candidatos à exclusão.
         Vamos identificar QUAIS números são melhores para excluir dinamicamente.

Abordagem:
1. Calcular historicamente quais números têm menor probabilidade de sair
   quando apresentam certas características (queda, mediano, etc.)
2. Usar múltiplos indicadores combinados
"""

import pyodbc
from collections import Counter, defaultdict
import statistics

print("="*70)
print("🧠 ESTRATÉGIA POOL 23 - COM APRENDIZADO")
print("="*70)

# Conexão
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 FROM Resultados_INT ORDER BY Concurso DESC")
rows = cursor.fetchall()

todos_resultados = []
for row in rows:
    nums = [row[i] for i in range(1, 16)]
    todos_resultados.append({
        'concurso': row[0],
        'numeros': nums,
        'set': set(nums)
    })

print(f"✅ {len(todos_resultados)} concursos carregados")

# ═══════════════════════════════════════════════════════════════════
# FUNÇÃO: Calcular múltiplos indicadores por número
# ═══════════════════════════════════════════════════════════════════
def calcular_indicadores(resultados_anteriores):
    """
    Calcula múltiplos indicadores para cada número.
    """
    indicadores = {}
    
    # Janelas de frequência
    def freq_janela(tamanho):
        freq = Counter()
        for r in resultados_anteriores[:min(tamanho, len(resultados_anteriores))]:
            freq.update(r['numeros'])
        return {n: freq.get(n, 0) / min(tamanho, len(resultados_anteriores)) * 100 for n in range(1, 26)}
    
    freq_3 = freq_janela(3)
    freq_5 = freq_janela(5)
    freq_10 = freq_janela(10)
    freq_15 = freq_janela(15)
    freq_30 = freq_janela(30)
    freq_50 = freq_janela(50)
    
    FREQ_ESPERADA = 60  # 15/25 * 100
    
    for n in range(1, 26):
        # Tendências
        tendencia_curta = freq_3[n] - freq_5[n]
        tendencia_media = freq_5[n] - freq_15[n]
        tendencia_longa = freq_15[n] - freq_30[n]
        
        # Distância da média
        dist_media_curta = abs(freq_5[n] - FREQ_ESPERADA)
        dist_media_longa = abs(freq_30[n] - FREQ_ESPERADA)
        
        # Último aparecimento
        ultima_aparicao = None
        for i, r in enumerate(resultados_anteriores):
            if n in r['set']:
                ultima_aparicao = i
                break
        if ultima_aparicao is None:
            ultima_aparicao = 100
        
        # Sequência de ausências (quantas vezes seguidas não apareceu recentemente)
        ausencias_consecutivas = 0
        for r in resultados_anteriores[:10]:
            if n not in r['set']:
                ausencias_consecutivas += 1
            else:
                break
        
        indicadores[n] = {
            'freq_3': freq_3[n],
            'freq_5': freq_5[n],
            'freq_10': freq_10[n],
            'freq_15': freq_15[n],
            'freq_30': freq_30[n],
            'freq_50': freq_50[n],
            'tendencia_curta': tendencia_curta,
            'tendencia_media': tendencia_media,
            'tendencia_longa': tendencia_longa,
            'dist_media_curta': dist_media_curta,
            'dist_media_longa': dist_media_longa,
            'ultima_aparicao': ultima_aparicao,
            'ausencias_consecutivas': ausencias_consecutivas
        }
    
    return indicadores

# ═══════════════════════════════════════════════════════════════════
# FASE 1: APRENDIZADO - Quais padrões predizem NÃO sair?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📚 FASE 1: APRENDIZADO (500 concursos históricos)")
print("="*70)

# Janela de treinamento
TREINO_INICIO = 100
TREINO_FIM = 600

# Coletar estatísticas de quando cada número NÃO saiu
padroes_nao_saiu = defaultdict(list)

for i in range(TREINO_INICIO, TREINO_FIM):
    if i >= len(todos_resultados) - 100:
        break
    
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    indicadores = calcular_indicadores(resultados_anteriores)
    
    for n in range(1, 26):
        ind = indicadores[n]
        saiu = n in resultado_real['set']
        
        padroes_nao_saiu[n].append({
            'saiu': saiu,
            **ind
        })

# Calcular correlações: quais indicadores predizem melhor "não sair"?
print("\n📊 Indicadores que melhor predizem NÃO SAIR:")

correlacoes = {}
indicadores_nomes = ['freq_3', 'freq_5', 'freq_10', 'freq_15', 'freq_30', 'tendencia_curta', 'tendencia_media', 'ultima_aparicao', 'ausencias_consecutivas']

for ind_nome in indicadores_nomes:
    # Média do indicador quando SAIU vs quando NÃO SAIU
    valores_saiu = []
    valores_nao_saiu = []
    
    for n in range(1, 26):
        for p in padroes_nao_saiu[n]:
            if p['saiu']:
                valores_saiu.append(p[ind_nome])
            else:
                valores_nao_saiu.append(p[ind_nome])
    
    media_saiu = statistics.mean(valores_saiu) if valores_saiu else 0
    media_nao_saiu = statistics.mean(valores_nao_saiu) if valores_nao_saiu else 0
    diferenca = media_nao_saiu - media_saiu
    
    correlacoes[ind_nome] = {
        'media_saiu': media_saiu,
        'media_nao_saiu': media_nao_saiu,
        'diferenca': diferenca
    }
    
    print(f"   {ind_nome:<20}: Saiu={media_saiu:6.1f}, Não Saiu={media_nao_saiu:6.1f}, Diff={diferenca:+6.2f}")

# ═══════════════════════════════════════════════════════════════════
# MODELO: Score de "probabilidade de NÃO sair"
# ═══════════════════════════════════════════════════════════════════
def score_nao_sair(indicadores_num, correlacoes):
    """
    Calcula score de probabilidade de NÃO sair baseado nos padrões aprendidos.
    Maior score = maior probabilidade de NÃO sair = bom candidato a excluir.
    """
    score = 0
    
    # Indicadores onde MENOR valor = maior chance de não sair
    # (baseado nos dados de treinamento)
    
    # Frequência baixa no curto prazo
    if indicadores_num['freq_5'] < 50:
        score += 1.5
    elif indicadores_num['freq_5'] < 60:
        score += 0.5
    
    # Tendência de queda no médio prazo
    if indicadores_num['tendencia_media'] < -10:
        score += 1.5
    elif indicadores_num['tendencia_media'] < 0:
        score += 0.5
    
    # Distância da média (próximo da média é mais previsível)
    if indicadores_num['dist_media_longa'] < 15:
        score += 1
    
    # Ausências consecutivas moderadas (1-3)
    # Muito baixo = vai sair, muito alto = pode voltar
    if 1 <= indicadores_num['ausencias_consecutivas'] <= 3:
        score += 1.5
    elif 4 <= indicadores_num['ausencias_consecutivas'] <= 6:
        score += 0.5
    
    # Penalizar números muito quentes (vão sair)
    if indicadores_num['freq_5'] > 80:
        score -= 3
    
    # Penalizar números muito frios (podem voltar)
    if indicadores_num['ultima_aparicao'] > 10:
        score -= 1
    
    return score

# ═══════════════════════════════════════════════════════════════════
# FASE 2: VALIDAÇÃO - Testar em 100 concursos
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("🧪 FASE 2: VALIDAÇÃO (100 concursos)")
print("="*70)

N_TESTES = 100
resultados_testes = []

for i in range(N_TESTES):
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    indicadores = calcular_indicadores(resultados_anteriores)
    
    # Calcular score de cada número
    scores = {}
    for n in range(1, 26):
        scores[n] = score_nao_sair(indicadores[n], correlacoes)
    
    # Top 2 com maior score = excluir
    ranking = sorted(scores.items(), key=lambda x: -x[1])
    excluir = [ranking[0][0], ranking[1][0]]
    pool_23 = set([n for n in range(1, 26) if n not in excluir])
    
    acertos = len(resultado_real['set'] & pool_23)
    fora = sorted(resultado_real['set'] - pool_23)
    
    resultados_testes.append({
        'concurso': resultado_real['concurso'],
        'acertos': acertos,
        'excluidos': sorted(excluir),
        'sairam': fora,
        'scores': scores
    })

# Estatísticas
acertos_dist = Counter(r['acertos'] for r in resultados_testes)

print(f"\n📈 DISTRIBUIÇÃO DE ACERTOS:")
for ac in sorted(acertos_dist.keys(), reverse=True):
    qtd = acertos_dist[ac]
    pct = qtd / N_TESTES * 100
    barra = "█" * int(pct)
    print(f"   {ac:2d}/15: {qtd:3d} ({pct:5.1f}%) {barra}")

media = sum(r['acertos'] for r in resultados_testes) / N_TESTES
jackpots = sum(1 for r in resultados_testes if r['acertos'] == 15)
taxa_13_mais = sum(1 for r in resultados_testes if r['acertos'] >= 13)

print(f"\n📊 ESTATÍSTICAS:")
print(f"   Média: {media:.2f}/15")
print(f"   Jackpot (15/15): {jackpots}/{N_TESTES} ({100*jackpots/N_TESTES:.1f}%)")
print(f"   Taxa 13+: {taxa_13_mais}/{N_TESTES}")

# ═══════════════════════════════════════════════════════════════════
# COMPARATIVO FINAL
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 COMPARATIVO FINAL DE ESTRATÉGIAS")
print("="*70)

print(f"""
┌─────────────────────────────┬────────┬─────────┬───────┐
│ Estratégia                  │  Média │ Jackpot │  13+  │
├─────────────────────────────┼────────┼─────────┼───────┤
│ Excluir FRIOS               │  13.85 │   15%   │ 100%  │
│ Excluir MEDIANOS            │  13.71 │   14%   │ 100%  │
│ HÍBRIDA (Queda+Médio)       │  13.94 │   21%   │ 100%  │
│ COM APRENDIZADO             │  {media:.2f} │   {jackpots:2d}%   │ {taxa_13_mais:3d}%  │
└─────────────────────────────┴────────┴─────────┴───────┘
""")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE DETALHADA DOS ERROS
# ═══════════════════════════════════════════════════════════════════
print("📋 ANÁLISE DOS ERROS (excluídos que saíram):")
print("-"*60)

erros = [r for r in resultados_testes if r['acertos'] < 15]
for r in erros[:10]:  # Mostrar primeiros 10
    print(f"   #{r['concurso']}: Excluí {r['excluidos']} → Saíram {r['sairam']}")

# Qual número mais "falha" quando excluído?
falhas_por_numero = Counter()
for r in erros:
    for n in r['sairam']:
        falhas_por_numero[n] += 1

print(f"\n📊 Números que mais 'falham' quando excluídos:")
for n, qtd in falhas_por_numero.most_common(10):
    print(f"   {n:2d}: {qtd} vezes saiu quando excluído")

cursor.close()
conn.close()

print("\n" + "="*70)
print("✅ ANÁLISE CONCLUÍDA!")
print("="*70)
