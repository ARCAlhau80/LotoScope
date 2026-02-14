# -*- coding: utf-8 -*-
"""
ANÁLISE: TOP N NÚMEROS COM MAIOR FREQUÊNCIA QUE NÃO SAEM
=========================================================
Hipótese do usuário: "Dos 5 números com maior Média%, 4 não saíram"
Isso é frequente? Previsível? Acontece em Curta% e Longa% também?

Análise estatística completa.
"""

import pyodbc
from collections import Counter
import statistics

print("="*78)
print("🔬 ANÁLISE: NÚMEROS 'QUENTES' QUE NÃO SAEM")
print("="*78)
print("   Hipótese: Números com alta frequência recente tendem a NÃO sair?")
print("="*78)

# Conexão
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    ORDER BY Concurso DESC
""")

resultados = []
for row in cursor.fetchall():
    resultados.append({
        'concurso': row[0],
        'numeros': list(row[1:16]),
        'set': set(row[1:16])
    })

conn.close()
print(f"\n✅ {len(resultados)} concursos carregados")

# ═══════════════════════════════════════════════════════════════════
# FUNÇÃO: Calcular frequência por janela
# ═══════════════════════════════════════════════════════════════════
def calcular_frequencias(resultados_anteriores, janela):
    """Calcula frequência de cada número na janela."""
    freq = Counter()
    for r in resultados_anteriores[:min(janela, len(resultados_anteriores))]:
        freq.update(r['numeros'])
    return {n: freq.get(n, 0) / min(janela, len(resultados_anteriores)) * 100 for n in range(1, 26)}

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE PRINCIPAL: Quantos do TOP 5 NÃO saem?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*78)
print("📊 ANÁLISE 1: QUANTOS DO TOP 5 (MAIS FREQUENTES) NÃO SAEM?")
print("="*78)

N_TESTES = 500  # Últimos 500 concursos
TOP_N = 5       # Top 5 mais frequentes

# Janelas a testar
JANELAS = {
    'Curta (5)': 5,
    'Média (15)': 15,
    'Longa (50)': 50,
}

resultados_analise = {janela: [] for janela in JANELAS}

for i in range(N_TESTES):
    if i >= len(resultados) - 60:
        break
    
    resultado_real = resultados[i]
    resultados_anteriores = resultados[i + 1:]
    
    for nome_janela, tamanho in JANELAS.items():
        freq = calcular_frequencias(resultados_anteriores, tamanho)
        
        # Top N mais frequentes
        ranking = sorted(freq.items(), key=lambda x: -x[1])
        top_n = [n for n, f in ranking[:TOP_N]]
        
        # Quantos do top NÃO saíram?
        nao_sairam = sum(1 for n in top_n if n not in resultado_real['set'])
        
        resultados_analise[nome_janela].append({
            'concurso': resultado_real['concurso'],
            'top_n': top_n,
            'nao_sairam': nao_sairam,
            'sairam': TOP_N - nao_sairam
        })

# Estatísticas
print(f"\n   Análise de {N_TESTES} concursos, TOP {TOP_N} mais frequentes\n")

print(f"   {'Janela':<15} {'Média Não Saem':>15} {'Desvio':>10} {'4+ Não Saem':>15} {'Todos Saem':>12}")
print("   " + "-"*70)

for nome_janela, dados in resultados_analise.items():
    nao_sairam_lista = [d['nao_sairam'] for d in dados]
    media = statistics.mean(nao_sairam_lista)
    desvio = statistics.stdev(nao_sairam_lista)
    
    # Probabilidade de 4+ não saírem
    prob_4_mais = sum(1 for n in nao_sairam_lista if n >= 4) / len(nao_sairam_lista) * 100
    
    # Probabilidade de todos saírem (0 não saem)
    prob_todos_saem = sum(1 for n in nao_sairam_lista if n == 0) / len(nao_sairam_lista) * 100
    
    print(f"   {nome_janela:<15} {media:>15.2f} {desvio:>10.2f} {prob_4_mais:>14.1f}% {prob_todos_saem:>11.1f}%")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE 2: Distribuição detalhada
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*78)
print("📊 ANÁLISE 2: DISTRIBUIÇÃO - QUANTOS DO TOP 5 SAEM?")
print("="*78)

for nome_janela, dados in resultados_analise.items():
    print(f"\n   📈 {nome_janela}:")
    
    # Distribuição
    dist = Counter(d['nao_sairam'] for d in dados)
    total = len(dados)
    
    print(f"   {'Não Saem':<12} {'Qtd':>8} {'%':>10} {'Barra':<30}")
    print("   " + "-"*60)
    
    for nao_saem in range(6):
        qtd = dist.get(nao_saem, 0)
        pct = qtd / total * 100
        barra = "█" * int(pct / 2)
        sairam = TOP_N - nao_saem
        
        label = f"{nao_saem} ({sairam} saem)"
        print(f"   {label:<12} {qtd:>8} {pct:>9.1f}% {barra}")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE 3: Valor esperado vs real
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*78)
print("📊 ANÁLISE 3: VALOR ESPERADO vs REAL")
print("="*78)

# Valor esperado: Se a loteria fosse puramente aleatória
# Prob de um número específico sair = 15/25 = 60%
# Prob de um número NÃO sair = 10/25 = 40%
# Esperado de 5 números não saírem = 5 * 0.4 = 2

prob_nao_sair = 10/25  # 40%
esperado_nao_saem = TOP_N * prob_nao_sair

print(f"\n   Se loteria fosse 100% aleatória:")
print(f"   • Prob de cada número NÃO sair: {prob_nao_sair*100:.1f}%")
print(f"   • Esperado: {esperado_nao_saem:.2f} de {TOP_N} não saem")

print(f"\n   {'Janela':<15} {'Esperado':>10} {'Real':>10} {'Diferença':>12} {'Conclusão':<25}")
print("   " + "-"*75)

for nome_janela, dados in resultados_analise.items():
    media_real = statistics.mean([d['nao_sairam'] for d in dados])
    diferenca = media_real - esperado_nao_saem
    
    if diferenca > 0.2:
        conclusao = "⬆️ Mais não saem que esperado"
    elif diferenca < -0.2:
        conclusao = "⬇️ Menos não saem que esperado"
    else:
        conclusao = "≈ Próximo do esperado"
    
    print(f"   {nome_janela:<15} {esperado_nao_saem:>10.2f} {media_real:>10.2f} {diferenca:>+11.2f} {conclusao:<25}")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE 4: Padrão de "reversão à média" - quentes esfriam?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*78)
print("📊 ANÁLISE 4: REVERSÃO À MÉDIA - QUENTES ESFRIAM?")
print("="*78)

# Vamos verificar: números muito frequentes (>80%) tendem a não sair mais que a média?
print("\n   Comparando números com frequência >80% vs <40%:\n")

muito_quentes_nao_saem = []
muito_frios_nao_saem = []

for i in range(N_TESTES):
    if i >= len(resultados) - 60:
        break
    
    resultado_real = resultados[i]
    resultados_anteriores = resultados[i + 1:]
    
    freq = calcular_frequencias(resultados_anteriores, 15)  # Janela média
    
    # Números muito quentes (>80%)
    muito_quentes = [n for n, f in freq.items() if f > 80]
    if muito_quentes:
        nao_saem_quentes = sum(1 for n in muito_quentes if n not in resultado_real['set'])
        taxa_nao_saem = nao_saem_quentes / len(muito_quentes)
        muito_quentes_nao_saem.append(taxa_nao_saem)
    
    # Números muito frios (<40%)
    muito_frios = [n for n, f in freq.items() if f < 40]
    if muito_frios:
        nao_saem_frios = sum(1 for n in muito_frios if n not in resultado_real['set'])
        taxa_nao_saem = nao_saem_frios / len(muito_frios)
        muito_frios_nao_saem.append(taxa_nao_saem)

media_quentes = statistics.mean(muito_quentes_nao_saem) * 100 if muito_quentes_nao_saem else 0
media_frios = statistics.mean(muito_frios_nao_saem) * 100 if muito_frios_nao_saem else 0

print(f"   Números MUITO QUENTES (>80% freq):")
print(f"   • Taxa de NÃO sair: {media_quentes:.1f}%")
print(f"   • Esperado aleatório: 40%")
print(f"   • Diferença: {media_quentes - 40:+.1f}%")

print(f"\n   Números MUITO FRIOS (<40% freq):")
print(f"   • Taxa de NÃO sair: {media_frios:.1f}%")
print(f"   • Esperado aleatório: 40%")
print(f"   • Diferença: {media_frios - 40:+.1f}%")

if media_quentes > 45:
    print(f"\n   ⚠️ CONFIRMADO: Números muito quentes tendem a NÃO sair mais que o esperado!")
    print(f"   📈 Isso sugere um padrão de 'reversão à média'")
elif media_quentes < 35:
    print(f"\n   ⚠️ CONTRÁRIO: Números muito quentes tendem a SAIR mais que o esperado!")
    print(f"   📈 Isso sugere um padrão de 'momento' (quentes continuam quentes)")
else:
    print(f"\n   ✅ NEUTRO: Não há padrão claro, comportamento próximo do aleatório")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE 5: Frequência do evento "4+ do TOP 5 não saem"
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*78)
print("📊 ANÁLISE 5: FREQUÊNCIA DO EVENTO '4+ DO TOP 5 NÃO SAEM'")
print("="*78)

for nome_janela, dados in resultados_analise.items():
    eventos_4_mais = [d for d in dados if d['nao_sairam'] >= 4]
    total = len(dados)
    freq_evento = len(eventos_4_mais) / total * 100
    
    print(f"\n   📈 {nome_janela}:")
    print(f"   • Ocorrências: {len(eventos_4_mais)}/{total}")
    print(f"   • Frequência: {freq_evento:.1f}%")
    print(f"   • Ou seja: acontece a cada {100/freq_evento:.0f} concursos" if freq_evento > 0 else "")
    
    # Mostrar últimas 10 ocorrências
    if eventos_4_mais:
        print(f"\n   Últimas 5 ocorrências:")
        for e in eventos_4_mais[:5]:
            print(f"      • Concurso {e['concurso']}: TOP5={e['top_n']}, {e['nao_sairam']} não saíram")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE 6: Isso é PREVISÍVEL?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*78)
print("📊 ANÁLISE 6: ISSO É PREVISÍVEL?")
print("="*78)

# Vamos ver se conseguimos prever quando "4+ do TOP 5 não saem"
# Hipótese: acontece mais quando os TOP 5 são MUITO mais frequentes que a média

print("\n   Testando se a 'intensidade' dos quentes prevê o evento...")

eventos_previsao = {'acertou': 0, 'errou': 0, 'total_previsoes': 0}

for nome_janela, dados in resultados_analise.items():
    if nome_janela != 'Média (15)':
        continue
    
    for i, d in enumerate(dados):
        if i >= len(dados) - 1:
            break
        
        # Dados do concurso anterior
        resultado_anterior = resultados[i + 1]
        resultados_antes = resultados[i + 2:]
        
        freq_antes = calcular_frequencias(resultados_antes, 15)
        ranking = sorted(freq_antes.items(), key=lambda x: -x[1])
        top_5 = [n for n, f in ranking[:5]]
        freq_top_5 = [f for n, f in ranking[:5]]
        
        # Se média do TOP 5 > 75%, prever que muitos não vão sair
        media_top_5 = statistics.mean(freq_top_5)
        
        previsao = media_top_5 > 75  # Prevê 4+ não saem
        real = d['nao_sairam'] >= 4
        
        if previsao:
            eventos_previsao['total_previsoes'] += 1
            if real:
                eventos_previsao['acertou'] += 1
            else:
                eventos_previsao['errou'] += 1

if eventos_previsao['total_previsoes'] > 0:
    taxa_acerto = eventos_previsao['acertou'] / eventos_previsao['total_previsoes'] * 100
    print(f"\n   Regra: Se média do TOP 5 > 75%, prever que 4+ não saem")
    print(f"   • Total de previsões: {eventos_previsao['total_previsoes']}")
    print(f"   • Acertos: {eventos_previsao['acertou']} ({taxa_acerto:.1f}%)")
    print(f"   • Erros: {eventos_previsao['errou']}")
    
    if taxa_acerto > 50:
        print(f"\n   ⚠️ PADRÃO DETECTADO! A regra funciona melhor que o acaso.")
    else:
        print(f"\n   ❌ Regra não é melhor que o acaso.")
else:
    print("\n   Não houve previsões com a regra testada.")

# ═══════════════════════════════════════════════════════════════════
# CONCLUSÕES
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*78)
print("🎯 CONCLUSÕES")
print("="*78)

media_real_media = statistics.mean([d['nao_sairam'] for d in resultados_analise['Média (15)']])

print(f"""
   1. FREQUÊNCIA DO EVENTO:
      • "4+ do TOP 5 não saem" acontece em ~{sum(1 for d in resultados_analise['Média (15)'] if d['nao_sairam'] >= 4)/len(resultados_analise['Média (15)'])*100:.0f}% dos concursos
      • Não é raro, mas também não é a norma

   2. COMPARAÇÃO COM ESPERADO:
      • Esperado aleatório: 2.0 de 5 não saem
      • Real observado: {media_real_media:.2f} de 5 não saem
      • Diferença: {media_real_media - 2:+.2f}

   3. REVERSÃO À MÉDIA:
      • Números muito quentes: {media_quentes:.1f}% não saem (vs 40% esperado)
      • Números muito frios: {media_frios:.1f}% não saem (vs 40% esperado)
""")

if media_quentes > 42 and media_frios < 42:
    print("   4. IMPLICAÇÃO PARA ESTRATÉGIA:")
    print("      ⚠️ HÁ EVIDÊNCIA de reversão à média!")
    print("      • Evitar confiar demais em números 'muito quentes'")
    print("      • Números frios podem ser mais promissores que parecem")
    print("      • Considerar excluir números com freq >80% no curto prazo")
elif media_quentes < 38:
    print("   4. IMPLICAÇÃO PARA ESTRATÉGIA:")
    print("      ✅ Não há evidência de reversão à média")
    print("      • Números quentes continuam sendo boas apostas")
    print("      • A estratégia atual está alinhada com os dados")
else:
    print("   4. IMPLICAÇÃO PARA ESTRATÉGIA:")
    print("      ≈ Comportamento próximo do aleatório")
    print("      • Não há vantagem clara em evitar números quentes")
    print("      • Nem em preferir números frios")

print("\n" + "="*78)
print("✅ ANÁLISE CONCLUÍDA!")
print("="*78)
