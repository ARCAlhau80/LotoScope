"""
BACKTEST REALISTA - Agente Neurônios v2.0
==========================================
Simula uso REAL: gera N combinações e verifica quantas teriam premiação

Diferença do teste atual:
- Teste atual: 100k combinações, pega a melhor (sempre acha 12-13)
- Este teste: 50 combinações, conta quantas acertam 11+ (uso real)
"""
import sys
sys.path.insert(0, 'lotofacil_lite/ia')

from agente_completo_v2 import AgenteNeuroniosEvolutivo
from collections import Counter
import numpy as np

print("=" * 70)
print("🔬 BACKTEST REALISTA - AGENTE NEURÔNIOS v2.0")
print("=" * 70)

agente = AgenteNeuroniosEvolutivo()
resultados_db = agente._carregar_resultados()

# Configuração REALISTA
COMBINACOES_POR_CONCURSO = 50  # O que você realmente jogaria
CONCURSOS_TESTAR = 50          # Últimos 50 concursos

print(f"\n📊 Configuração REALISTA:")
print(f"   • Combinações por concurso: {COMBINACOES_POR_CONCURSO}")
print(f"   • Concursos a testar: {CONCURSOS_TESTAR}")
print(f"   • Total combinações: {COMBINACOES_POR_CONCURSO * CONCURSOS_TESTAR:,}")

# Estatísticas globais
todos_acertos = []
concursos_com_11_mais = 0
concursos_com_13_mais = 0
concursos_com_14_mais = 0
jackpots = 0

# Comparação com random
acertos_random = []

print(f"\n🔄 Testando...")

for idx in range(CONCURSOS_TESTAR):
    concurso_alvo = resultados_db[idx]
    dados_antes = resultados_db[idx + 1:]
    
    # Calcular exclusões (INVERTIDA v3.0)
    scores = agente._calcular_score_exclusao(dados_antes)
    excluidos = {scores[0]['num'], scores[1]['num']}
    
    # Gerar combinações com estratégias evolutivas
    acertos_concurso = []
    for _ in range(COMBINACOES_POR_CONCURSO):
        comb, _ = agente._gerar_combinacao_evolutiva(dados_antes, excluidos)
        ac = agente._verificar_acertos(comb, concurso_alvo['numeros'])
        acertos_concurso.append(ac)
        todos_acertos.append(ac)
    
    # Gerar combinações RANDOM para comparação
    import random
    for _ in range(COMBINACOES_POR_CONCURSO):
        comb_random = sorted(random.sample(range(1, 26), 15))
        ac_random = agente._verificar_acertos(comb_random, concurso_alvo['numeros'])
        acertos_random.append(ac_random)
    
    # Estatísticas do concurso
    max_acerto = max(acertos_concurso)
    tem_11_mais = any(a >= 11 for a in acertos_concurso)
    tem_13_mais = any(a >= 13 for a in acertos_concurso)
    tem_14_mais = any(a >= 14 for a in acertos_concurso)
    tem_jackpot = any(a == 15 for a in acertos_concurso)
    
    if tem_11_mais:
        concursos_com_11_mais += 1
    if tem_13_mais:
        concursos_com_13_mais += 1
    if tem_14_mais:
        concursos_com_14_mais += 1
    if tem_jackpot:
        jackpots += 1
    
    # Log a cada 10
    if (idx + 1) % 10 == 0:
        print(f"   Progresso: {idx+1}/{CONCURSOS_TESTAR} | Max este: {max_acerto}")

# ═══════════════════════════════════════════════════════════════════
# RELATÓRIO FINAL
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 RELATÓRIO - BACKTEST REALISTA")
print("=" * 70)

print(f"\n📈 ESTATÍSTICAS DAS {len(todos_acertos):,} COMBINAÇÕES:")
print(f"   • Média de acertos: {np.mean(todos_acertos):.2f}")
print(f"   • Máximo: {max(todos_acertos)}")
print(f"   • Mínimo: {min(todos_acertos)}")
print(f"   • Desvio padrão: {np.std(todos_acertos):.2f}")

print(f"\n✅ TAXA DE SUCESSO POR CONCURSO ({COMBINACOES_POR_CONCURSO} combos):")
print(f"   • Concursos com ≥11: {concursos_com_11_mais}/{CONCURSOS_TESTAR} ({concursos_com_11_mais/CONCURSOS_TESTAR*100:.1f}%)")
print(f"   • Concursos com ≥13: {concursos_com_13_mais}/{CONCURSOS_TESTAR} ({concursos_com_13_mais/CONCURSOS_TESTAR*100:.1f}%)")
print(f"   • Concursos com ≥14: {concursos_com_14_mais}/{CONCURSOS_TESTAR} ({concursos_com_14_mais/CONCURSOS_TESTAR*100:.1f}%)")
print(f"   • JACKPOTS (15): {jackpots}/{CONCURSOS_TESTAR}")

# Distribuição
print(f"\n📊 DISTRIBUIÇÃO DE ACERTOS (Agente v2.0):")
dist = Counter(todos_acertos)
for a in range(15, 7, -1):
    qtd = dist.get(a, 0)
    pct = qtd / len(todos_acertos) * 100
    barra = "█" * int(pct * 2)
    print(f"   {a:2d} acertos: {qtd:5d} ({pct:5.2f}%) {barra}")

# Comparação com random
print(f"\n🎲 COMPARAÇÃO COM RANDOM:")
print(f"   Agente v2.0:")
print(f"      Média: {np.mean(todos_acertos):.2f}")
print(f"      Taxa ≥11: {sum(1 for a in todos_acertos if a >= 11)/len(todos_acertos)*100:.2f}%")
print(f"      Taxa ≥13: {sum(1 for a in todos_acertos if a >= 13)/len(todos_acertos)*100:.2f}%")

print(f"\n   Random (baseline):")
print(f"      Média: {np.mean(acertos_random):.2f}")
print(f"      Taxa ≥11: {sum(1 for a in acertos_random if a >= 11)/len(acertos_random)*100:.2f}%")
print(f"      Taxa ≥13: {sum(1 for a in acertos_random if a >= 13)/len(acertos_random)*100:.2f}%")

# Vantagem
vantagem_media = np.mean(todos_acertos) - np.mean(acertos_random)
vantagem_11 = (sum(1 for a in todos_acertos if a >= 11)/len(todos_acertos) - 
               sum(1 for a in acertos_random if a >= 11)/len(acertos_random)) * 100

print(f"\n🎯 VANTAGEM DO AGENTE vs RANDOM:")
print(f"   • Média: {vantagem_media:+.2f} acertos")
print(f"   • Taxa ≥11: {vantagem_11:+.2f}pp")

if vantagem_11 > 0:
    print(f"\n   ✅ Agente tem vantagem de {vantagem_11:.1f}pp sobre random!")
else:
    print(f"\n   ❌ Agente não supera random significativamente")

print("\n" + "=" * 70)
