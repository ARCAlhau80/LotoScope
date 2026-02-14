# -*- coding: utf-8 -*-
"""
ESTRATÉGIA POOL 23 - EXCLUIR OS MAIS MEDIANOS/PREVISÍVEIS
==========================================================
Hipótese: Números muito frios são IMPREVISÍVEIS (podem voltar)
         Números muito quentes VÃO sair
         Números MEDIANOS são os mais seguros para excluir

Métricas:
- Desvio padrão da frequência (estabilidade)
- Distância da média global
- Coeficiente de variação
"""

import pyodbc
from collections import Counter
import statistics

print("="*70)
print("🧪 ESTRATÉGIA: EXCLUIR OS MAIS MEDIANOS/PREVISÍVEIS")
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
# FUNÇÃO: Calcular métrica de "medianidade" para cada número
# ═══════════════════════════════════════════════════════════════════
def calcular_metricas_medianidade(resultados_anteriores, janela=30):
    """
    Calcula quão "mediano" cada número é.
    Números medianos = frequência próxima da média + baixa variação
    
    Retorna score onde MAIOR = mais mediano = candidato a excluir
    """
    # Frequência geral na janela
    freq_total = Counter()
    for r in resultados_anteriores[:janela]:
        freq_total.update(r['numeros'])
    
    # Média esperada: 15 números por sorteio, 25 possíveis
    # Em 30 sorteios: esperado = 30 * 15 / 25 = 18 aparições por número
    freq_esperada = janela * 15 / 25
    
    # Calcular frequência por mini-janelas para ver variação
    mini_janelas = 5
    tamanho_mini = janela // mini_janelas
    
    freq_por_mini = {n: [] for n in range(1, 26)}
    for j in range(mini_janelas):
        inicio = j * tamanho_mini
        fim = (j + 1) * tamanho_mini
        freq_mini = Counter()
        for r in resultados_anteriores[inicio:fim]:
            freq_mini.update(r['numeros'])
        for n in range(1, 26):
            freq_por_mini[n].append(freq_mini.get(n, 0))
    
    # Calcular métricas por número
    metricas = {}
    for n in range(1, 26):
        freq_n = freq_total.get(n, 0)
        
        # Distância da média (normalizada)
        distancia_media = abs(freq_n - freq_esperada) / freq_esperada
        
        # Variação entre mini-janelas (estabilidade)
        valores_mini = freq_por_mini[n]
        if len(set(valores_mini)) > 1:
            desvio = statistics.stdev(valores_mini)
            media_mini = statistics.mean(valores_mini)
            coef_variacao = desvio / media_mini if media_mini > 0 else 1
        else:
            desvio = 0
            coef_variacao = 0
        
        # Score de "medianidade"
        # MAIOR score = mais mediano = candidato a excluir
        # Queremos: próximo da média (baixa distância) + baixa variação
        score_medianidade = (1 - distancia_media) * (1 - min(coef_variacao, 1))
        
        # Penalizar números muito frequentes (vão sair) ou muito raros (imprevisíveis)
        if freq_n > freq_esperada * 1.3:  # Muito quente
            score_medianidade *= 0.3  # Não excluir
        if freq_n < freq_esperada * 0.5:  # Muito frio
            score_medianidade *= 0.5  # Risco de voltar
        
        metricas[n] = {
            'freq': freq_n,
            'freq_esperada': freq_esperada,
            'distancia_media': distancia_media,
            'desvio': desvio,
            'coef_variacao': coef_variacao,
            'score': score_medianidade
        }
    
    return metricas

# ═══════════════════════════════════════════════════════════════════
# TESTE EM UM CONCURSO
# ═══════════════════════════════════════════════════════════════════
CONCURSO_ALVO = 3609

idx_alvo = None
for i, r in enumerate(todos_resultados):
    if r['concurso'] == CONCURSO_ALVO:
        idx_alvo = i
        break

resultado_real = todos_resultados[idx_alvo]
resultados_anteriores = todos_resultados[idx_alvo + 1:]

print(f"\n📋 CONCURSO ALVO: {CONCURSO_ALVO}")
print(f"   Resultado REAL: {sorted(resultado_real['numeros'])}")

metricas = calcular_metricas_medianidade(resultados_anteriores, 30)

print("\n" + "="*70)
print("📊 ANÁLISE DE MEDIANIDADE (janela 30)")
print("="*70)

print(f"\n{'Num':<4} {'Freq':>6} {'Esp':>6} {'Dist%':>8} {'Desvio':>8} {'CV':>8} {'Score':>8} {'Status':<15}")
print("-"*75)

# Ordenar por score (maior = mais mediano)
ranking = sorted(metricas.items(), key=lambda x: -x[1]['score'])

for n, m in sorted(metricas.items(), key=lambda x: x[0]):
    status = ""
    if n == ranking[0][0] or n == ranking[1][0]:
        status = "❌ EXCLUIR"
    elif m['freq'] > m['freq_esperada'] * 1.2:
        status = "🔥 Quente"
    elif m['freq'] < m['freq_esperada'] * 0.7:
        status = "❄️ Frio"
    else:
        status = "⚖️ Médio"
    
    # Marcar se saiu no resultado
    if n in resultado_real['set']:
        status += " ✓SAIU"
    
    print(f"{n:3d} {m['freq']:>6.0f} {m['freq_esperada']:>6.1f} {m['distancia_media']*100:>7.1f}% {m['desvio']:>8.2f} {m['coef_variacao']:>8.2f} {m['score']:>8.3f} {status:<15}")

# Identificar os 2 mais medianos
mais_medianos = [ranking[0][0], ranking[1][0]]
pool_23 = sorted([n for n in range(1, 26) if n not in mais_medianos])

print(f"\n{'='*70}")
print(f"🎯 RESULTADO")
print(f"{'='*70}")
print(f"\n❌ 2 MAIS MEDIANOS (excluir): {sorted(mais_medianos)}")
print(f"✅ POOL 23: {pool_23}")

acertos = len(resultado_real['set'] & set(pool_23))
print(f"\n🎯 Resultado real tem {acertos}/15 no Pool 23")

if acertos == 15:
    print("   🏆 JACKPOT GARANTIDO!")
else:
    fora = sorted(resultado_real['set'] - set(pool_23))
    print(f"   ⚠️ Fora do pool: {fora}")

# ═══════════════════════════════════════════════════════════════════
# BACKTESTING: 100 CONCURSOS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 BACKTESTING: 100 CONCURSOS")
print("="*70)

N_TESTES = 100
acertos_dist = Counter()
sucessos_15 = 0
erros = []

for i in range(N_TESTES):
    if i >= len(todos_resultados) - 50:
        break
    
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    metricas = calcular_metricas_medianidade(resultados_anteriores, 30)
    ranking = sorted(metricas.items(), key=lambda x: -x[1]['score'])
    mais_medianos = [ranking[0][0], ranking[1][0]]
    pool_23 = sorted([n for n in range(1, 26) if n not in mais_medianos])
    
    acertos = len(resultado_real['set'] & set(pool_23))
    acertos_dist[acertos] += 1
    
    if acertos == 15:
        sucessos_15 += 1
    else:
        fora = sorted(resultado_real['set'] - set(pool_23))
        if any(n in mais_medianos for n in fora):
            erros.append({
                'concurso': resultado_real['concurso'],
                'excluidos': mais_medianos,
                'sairam': [n for n in fora if n in mais_medianos]
            })

print(f"\n📈 DISTRIBUIÇÃO DE ACERTOS:")
for ac in sorted(acertos_dist.keys(), reverse=True):
    qtd = acertos_dist[ac]
    pct = qtd / N_TESTES * 100
    barra = "█" * int(pct)
    print(f"   {ac:2d}/15: {qtd:3d} ({pct:5.1f}%) {barra}")

media = sum(ac * qtd for ac, qtd in acertos_dist.items()) / N_TESTES
print(f"\n📊 ESTATÍSTICAS:")
print(f"   Média: {media:.2f}/15")
print(f"   Jackpot (15/15): {sucessos_15}/{N_TESTES} ({100*sucessos_15/N_TESTES:.1f}%)")
print(f"   Taxa 13+: {sum(qtd for ac, qtd in acertos_dist.items() if ac >= 13)}/{N_TESTES}")
print(f"   Erros (medianos saíram): {len(erros)}/{N_TESTES}")

# ═══════════════════════════════════════════════════════════════════
# COMPARATIVO COM ESTRATÉGIA ANTERIOR (excluir frios)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 COMPARATIVO: MEDIANOS vs FRIOS")
print("="*70)

# Recalcular para estratégia de frios (código anterior)
JANELAS = {'ultra_curta': 3, 'curta': 5, 'media': 10, 'media_longa': 15, 'longa': 30, 'ultra_longa': 100}
PESOS = {'ultra_curta': 3.0, 'curta': 2.5, 'media': 2.0, 'media_longa': 1.5, 'longa': 1.0, 'ultra_longa': 0.5}

acertos_frios = Counter()
sucessos_frios = 0

for i in range(N_TESTES):
    if i >= len(todos_resultados) - 130:
        break
    
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    # Estratégia frios
    freq_por_janela = {}
    for nome, tamanho in JANELAS.items():
        freq = Counter()
        for r in resultados_anteriores[:tamanho]:
            freq.update(r['numeros'])
        for n in freq:
            freq[n] = freq[n] / tamanho * 100
        freq_por_janela[nome] = freq
    
    scores = {}
    for n in range(1, 26):
        score = sum(freq_por_janela[nome].get(n, 0) * peso for nome, peso in PESOS.items())
        scores[n] = score
    
    ranking = sorted(scores.items(), key=lambda x: x[1])
    piores_2 = [ranking[0][0], ranking[1][0]]
    pool_23 = sorted([n for n in range(1, 26) if n not in piores_2])
    
    acertos = len(resultado_real['set'] & set(pool_23))
    acertos_frios[acertos] += 1
    if acertos == 15:
        sucessos_frios += 1

media_frios = sum(ac * qtd for ac, qtd in acertos_frios.items()) / N_TESTES
media_medianos = sum(ac * qtd for ac, qtd in acertos_dist.items()) / N_TESTES

print(f"\n{'Estratégia':<20} {'Média':>10} {'Jackpot':>12} {'13+':>8} {'Erros':>8}")
print("-"*60)
print(f"{'Excluir FRIOS':<20} {media_frios:>10.2f} {sucessos_frios:>10}/{N_TESTES} {sum(qtd for ac, qtd in acertos_frios.items() if ac >= 13):>8} {N_TESTES-sucessos_frios:>8}")
print(f"{'Excluir MEDIANOS':<20} {media_medianos:>10.2f} {sucessos_15:>10}/{N_TESTES} {sum(qtd for ac, qtd in acertos_dist.items() if ac >= 13):>8} {len(erros):>8}")

if media_medianos > media_frios:
    diff = media_medianos - media_frios
    print(f"\n✅ MEDIANOS é MELHOR (+{diff:.2f} média)")
elif media_frios > media_medianos:
    diff = media_frios - media_medianos
    print(f"\n✅ FRIOS é MELHOR (+{diff:.2f} média)")
else:
    print(f"\n⚖️ Empate!")

cursor.close()
conn.close()

print("\n" + "="*70)
print("✅ ANÁLISE CONCLUÍDA!")
print("="*70)
