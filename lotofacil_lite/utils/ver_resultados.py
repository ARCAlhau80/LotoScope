#!/usr/bin/env python3
import json

# Carregar dados
with open('teste_performance_gerador_corrigido_balanceado_20250907_192352.json', 'r') as f:
    dados = json.load(f)

print("=" * 60)
print("🧪 RESULTADO DO TESTE HISTÓRICO")
print("=" * 60)
print(f"📅 Data: {dados['metadata']['data_inicio'][:16]}")
print(f"🔢 Total Testes: {dados['metadata']['total_testes']}")
print(f"🤖 Algoritmo: {dados['metadata']['algoritmo']}")

# Verificar estrutura
print("\n🔍 Estrutura disponível:")
for key in dados['estatisticas_finais'].keys():
    print(f"   - {key}")

# Tentar extrair dados da teoria dos 20 números
if 'teoria_20_numeros_consolidada' in dados['estatisticas_finais']:
    teoria = dados['estatisticas_finais']['teoria_20_numeros_consolidada']
    print(f"\n🎯 TEORIA DOS 20 NÚMEROS:")
    
    # Verificar subchaves
    for subkey in teoria.keys():
        print(f"   - {subkey}: {teoria[subkey]}")

print("\n" + "=" * 60)
