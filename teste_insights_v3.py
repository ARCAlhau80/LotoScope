#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste rápido dos novos insights v3.0"""

from lotofacil_lite.geradores.analisador_combinacoes_geradas import AnalisadorCombinacoesGeradas

print("=" * 70)
print("🧪 TESTE DOS INSIGHTS v3.0")
print("=" * 70)

# Criar analisador
a = AnalisadorCombinacoesGeradas()

# Testar uma combinação
comb = [1, 3, 4, 5, 10, 11, 13, 14, 18, 20, 21, 22, 24, 25]
print(f"\n📋 Combinação de teste: {comb}")

# Analisar insights
insights = a._analisar_insights_combinacao(comb)

print("\n🧠 INSIGHTS AVANÇADOS:")
print(f"   💰 Trios com Dívida: {insights['trios_divida']}")
print(f"   🚀 Trios com Momentum: {insights['trios_momentum']}")
print(f"   🔗 Números Pivô: {insights['numeros_pivo']}")
print(f"   ⚖️ Score Paridade: {insights['score_paridade']:.3f}")
print(f"   📊 Índice Dívida Total: {insights['indice_divida_total']:.2f}")
print(f"   🔄 Ciclo Esperado: {insights['ciclo_esperado']:.2f}")

# Testar avaliação completa
print("\n📊 AVALIAÇÃO COMPLETA:")
aval = a._avaliar_combinacao(comb, validar_hist=True)
print(f"   Score Total: {aval['score']}")
print(f"   Passou Dívida: {aval['passou_divida']}")
print(f"   Passou Pivô: {aval['passou_pivo']}")
print(f"   Passou Momentum: {aval['passou_momentum']}")
print(f"   Passou Paridade: {aval['passou_paridade']}")
print(f"   Passou TODOS: {aval['passou_todos']}")

# Mostrar ciclos de recorrência
print("\n🔄 CICLOS DE RECORRÊNCIA POR CATEGORIA:")
for cat, dados in a.ciclos_recorrencia.items():
    print(f"   {cat}: atraso médio {dados['atraso_medio']:.1f} ({dados['count']} trios)")

print("\n✅ Teste concluído!")
