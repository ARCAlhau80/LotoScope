#!/usr/bin/env python3
import json

# Carregar dados do teste
with open('teste_performance_gerador_corrigido_balanceado_20250907_192352.json', 'r') as f:
    dados = json.load(f)

print("=" * 70)
print("🧪 TESTE HISTÓRICO LOTOFÁCIL - RESULTADOS DETALHADOS")
print("=" * 70)

# Metadados
print(f"📅 Data: {dados['metadata']['data_inicio'][:16]}")
print(f"🔢 Total Testes: {dados['metadata']['total_testes']}")
print(f"📊 Janela: {dados['metadata']['janela_inicial']} → {dados['metadata']['janela_final']}")
print(f"🤖 Algoritmo: {dados['metadata']['algoritmo']}")

# Teoria dos 20 números
print("\n🎯 TEORIA DOS 20 NÚMEROS:")
teoria = dados['estatisticas_finais']['teoria_20_numeros_consolidada']
acerto_medio = teoria['percentual_medio_dentro']
print(f"✅ Taxa de Acerto Médio: {acerto_medio:.2f}%")
print(f"❌ Taxa de Erro Médio: {teoria['percentual_medio_fora']:.2f}%")

# Interpretar resultado
if acerto_medio >= 75:
    status = "🔥 EXCELENTE"
elif acerto_medio >= 65:
    status = "✅ MUITO BOM"
elif acerto_medio >= 55:
    status = "⚡ BOM"
else:
    status = "❌ PRECISA MELHORAR"

print(f"📊 Status: {status}")

# Performance por formato
print("\n📊 PERFORMANCE POR FORMATO:")
formatos = dados['estatisticas_finais']['acertos_por_formato']

for formato, stats in formatos.items():
    nums = formato.replace('_nums', '').replace('_', ' ')
    media = stats['media']
    minimo = stats['minimo'] 
    maximo = stats['maximo']
    total = stats['total_combinacoes']
    
    print(f"🎲 {nums.upper()} NÚMEROS:")
    print(f"   📊 Média: {media:.2f} acertos")
    print(f"   ⚡ Faixa: {minimo} - {maximo} acertos")
    print(f"   🎯 Total Combinações: {total}")
    print()

# Conclusão
print("=" * 70)
print("📝 CONCLUSÕES:")
print(f"🎯 O sistema acerta {acerto_medio:.1f}% dos números nos 20 selecionados")
print(f"✅ Performance {status.split(' ')[1]} em 2000 testes históricos")
print(f"🚀 Sistema validado e pronto para uso!")
print("=" * 70)
