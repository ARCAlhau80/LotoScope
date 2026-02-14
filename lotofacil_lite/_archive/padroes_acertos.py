#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
import random

# Carregar dados do teste
with open('teste_performance_gerador_corrigido_balanceado_20250907_192352.json', 'r') as f:
    dados = json.load(f)

print("=" * 80)
print("🎯 ANÁLISE DE PADRÕES DE ACERTOS - EXEMPLOS ESPECÍFICOS")
print("=" * 80)

# Analisar padrões por concurso
padroes_concurso = []
exemplos_detalhados = []

contador = 0
for registro in dados['historico_acertos'][:100]:  # Primeiros 100 concursos para análise
    contador += 1
    concurso = registro['concurso_previsto']
    
    # Coletar acertos de todas as combinações do concurso
    acertos_concurso = []
    detalhes_concurso = {'concurso': concurso, 'combinacoes': []}
    
    for formato, combinacoes in registro['acertos_por_formato'].items():
        for combinacao in combinacoes:
            acertos = combinacao['acertos']
            acertos_concurso.append(acertos)
            
            # Guardar exemplo detalhado
            if len(detalhes_concurso['combinacoes']) < 3:  # Só os 3 primeiros por concurso
                detalhes_concurso['combinacoes'].append({
                    'formato': formato,
                    'acertos': acertos,
                    'numeros': combinacao['combinacao'][:5]  # Primeiros 5 números
                })
    
    # Contar padrão de acertos
    contador_acertos = Counter(acertos_concurso)
    padrao = []
    for acerto in sorted(contador_acertos.keys(), reverse=True):
        qtd = contador_acertos[acerto]
        padrao.append(f"{qtd}x{acerto}")
    
    padroes_concurso.append({
        'concurso': concurso,
        'padrao': ' + '.join(padrao),
        'total_combinacoes': len(acertos_concurso),
        'melhor_acerto': max(acertos_concurso),
        'acertos_detalhados': contador_acertos
    })
    
    if contador <= 10:  # Primeiros 10 para exemplos detalhados
        exemplos_detalhados.append(detalhes_concurso)

print("🔍 EXEMPLOS DE PADRÕES DE ACERTOS POR CONCURSO:")
print("=" * 80)

# Mostrar exemplos específicos
for i, padrao in enumerate(padroes_concurso[:15]):
    concurso = padrao['concurso']
    padrao_txt = padrao['padrao']
    melhor = padrao['melhor_acerto']
    
    # Emoji baseado no melhor acerto
    if melhor >= 14:
        emoji = "🔥"
        status = "EXCELENTE"
    elif melhor >= 12:
        emoji = "✅" 
        status = "MUITO BOM"
    elif melhor >= 10:
        emoji = "⚡"
        status = "BOM"
    else:
        emoji = "📊"
        status = "REGULAR"
    
    print(f"{emoji} Concurso {concurso}: {padrao_txt} (Melhor: {melhor} - {status})")

print("\n" + "=" * 80)
print("📊 ANÁLISE DE PADRÕES MAIS COMUNS")
print("=" * 80)

# Contar padrões mais comuns
padroes_comuns = Counter()
for padrao in padroes_concurso:
    # Simplificar padrão (pegar só os 3 principais)
    acertos_det = padrao['acertos_detalhados']
    top_3 = sorted(acertos_det.items(), key=lambda x: (-x[1], -x[0]))[:3]
    padrao_simples = ' + '.join([f"{qtd}x{acerto}" for acerto, qtd in top_3 if qtd > 0])
    padroes_comuns[padrao_simples] += 1

print("🎯 TOP 20 PADRÕES DE ACERTOS MAIS FREQUENTES:")
for i, (padrao, freq) in enumerate(padroes_comuns.most_common(20), 1):
    percentual = (freq / len(padroes_concurso)) * 100
    print(f"   {i:2d}. {padrao} → {freq} vezes ({percentual:.1f}%)")

print("\n" + "=" * 80)
print("🔍 EXEMPLOS DETALHADOS DE COMBINAÇÕES")
print("=" * 80)

# Mostrar exemplos detalhados de combinações
for i, exemplo in enumerate(exemplos_detalhados[:5], 1):
    print(f"\n📋 EXEMPLO {i} - Concurso {exemplo['concurso']}:")
    for comb in exemplo['combinacoes']:
        formato = comb['formato'].replace('_nums', '').replace('_', ' ')
        acertos = comb['acertos']
        nums = ', '.join(map(str, comb['numeros']))
        
        if acertos >= 13:
            emoji = "🔥"
        elif acertos >= 11:
            emoji = "✅"
        elif acertos >= 9:
            emoji = "⚡"
        else:
            emoji = "📊"
            
        print(f"   {emoji} {formato} números: {acertos} acertos [{nums}...]")

print("\n" + "=" * 80)
print("📈 ESTATÍSTICAS DE DISTRIBUIÇÃO")
print("=" * 80)

# Análise de distribuição de melhor acerto por concurso
melhores_acertos = [p['melhor_acerto'] for p in padroes_concurso]
dist_melhores = Counter(melhores_acertos)

print("🏆 DISTRIBUIÇÃO DOS MELHORES ACERTOS POR CONCURSO:")
for acerto in sorted(dist_melhores.keys(), reverse=True):
    qtd = dist_melhores[acerto]
    percentual = (qtd / len(padroes_concurso)) * 100
    
    if acerto >= 14:
        emoji = "🔥"
        nivel = "EXCELENTE"
    elif acerto >= 12:
        emoji = "✅"
        nivel = "MUITO BOM"  
    elif acerto >= 10:
        emoji = "⚡"
        nivel = "BOM"
    else:
        emoji = "📊"
        nivel = "REGULAR"
        
    print(f"   {emoji} {acerto} acertos: {qtd:2d} concursos ({percentual:4.1f}%) - {nivel}")

# Calcular estatísticas finais
media_melhor = sum(melhores_acertos) / len(melhores_acertos)
concursos_excelentes = sum(1 for x in melhores_acertos if x >= 13)
concursos_muito_bons = sum(1 for x in melhores_acertos if x >= 11)

print(f"\n📊 RESUMO:")
print(f"   🎯 Média do melhor acerto: {media_melhor:.2f}")
print(f"   🔥 Concursos com 13+ acertos: {concursos_excelentes} ({(concursos_excelentes/len(melhores_acertos))*100:.1f}%)")
print(f"   ✅ Concursos com 11+ acertos: {concursos_muito_bons} ({(concursos_muito_bons/len(melhores_acertos))*100:.1f}%)")

print("\n" + "=" * 80)
print("✅ ANÁLISE COMPLEMENTAR CONCLUÍDA!")
print("🎯 Padrões identificados em 100 concursos de teste")
print("=" * 80)
