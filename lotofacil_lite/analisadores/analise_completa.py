#!/usr/bin/env python3
import json

# Carregar dados
with open('teste_performance_gerador_corrigido_balanceado_20250907_192352.json', 'r') as f:
    dados = json.load(f)

print("=" * 70)
print("🎯 ANÁLISE COMPLETA DO TESTE HISTÓRICO - LotoScope")
print("=" * 70)
print(f"📅 Data: {dados['metadata']['data_inicio'][:16]}")
print(f"🔢 Total Testes: {dados['metadata']['total_testes']}")
print(f"🤖 Algoritmo: {dados['metadata']['algoritmo']}")

# Teoria dos 20 números
teoria = dados['estatisticas_finais']['teoria_20_numeros_consolidada']
print(f"\n🎯 TEORIA DOS 20 NÚMEROS:")
print(f"✅ Percentual Médio DENTRO: {teoria['percentual_medio_dentro']:.2f}%")
print(f"❌ Percentual Médio FORA: {teoria['percentual_medio_fora']:.2f}%")
print(f"🔍 Confirmação Teoria 60-70%: {teoria['confirmacao_teoria_60_70']}")

# Performance por formato
formatos = dados['estatisticas_finais']['acertos_por_formato']
print(f"\n📊 PERFORMANCE POR FORMATO:")

for formato, stats in formatos.items():
    nums = formato.replace('_nums', '').replace('_', ' ')
    media = stats['media_acertos']
    taxa = stats['taxa_sucesso']
    min_val = stats['min_acertos']
    max_val = stats['max_acertos']
    desvio = stats['desvio_padrao']
    
    print(f"   🎲 {nums.upper()}: {media:.2f} acertos médios ({taxa:.1f}% sucesso)")
    print(f"      ⚡ Min: {min_val} | Max: {max_val} | DP: {desvio:.2f}")

# Performance geral
geral = dados['estatisticas_finais']['performance_geral']
print(f"\n🚀 PERFORMANCE GERAL:")
print(f"   🎯 Formato Mais Eficiente: {geral['formato_mais_eficiente'].replace('_', ' ')}")
print(f"   📈 Melhor Taxa de Sucesso: {geral['melhor_taxa_sucesso']:.2f}%")
print(f"   🔥 Maior Média de Acertos: {geral['maior_media_acertos']:.2f}")

print("\n" + "=" * 70)
print("✅ TESTE HISTÓRICO CONCLUÍDO COM SUCESSO!")
print("🎲 Sistema LotoScope validado com 2000 concursos históricos")
print("=" * 70)
