#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPARADOR DE GERADORES - LotoScope
Teste A/B entre gerador atual e gerador otimizado
"""

import json
import random
import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'geradores'))

from gerador_isolado import GeradorIsolado
from gerador_hibrido_otimizado import GeradorHibridoOtimizado

def teste_comparativo_geradores(num_testes=50):
    """Compara performance entre gerador atual e otimizado"""
    print("=" * 80)
    print("🔬 TESTE COMPARATIVO DE GERADORES - A/B TESTING")
    print(f"📊 Executando {num_testes} testes comparativos")
    print("=" * 80)
    
    # Inicializar geradores
    gerador_atual = GeradorIsolado(concurso_limite=3479)
    gerador_otimizado = GeradorHibridoOtimizado()
    
    # Métricas para comparação
    scores_atual = []
    scores_otimizado = []
    
    print("🔄 Executando testes...")
    
    for i in range(num_testes):
        concurso_teste = 3480 + i
        formato_teste = random.choice([17, 18, 19, 20])
        
        # Gerador atual
        try:
            comb_atual = gerador_atual.gerar_combinacao_historica(formato_teste, variacao=i+1)
            score_atual = gerador_otimizado.avaliar_qualidade_combinacao(comb_atual)
            scores_atual.append(score_atual)
        except:
            # Se falhar, usar score baixo
            scores_atual.append(50)
        
        # Gerador otimizado
        comb_otimizada = gerador_otimizado.gerar_combinacao_otimizada(concurso_teste, formato_teste)
        score_otimizado = gerador_otimizado.avaliar_qualidade_combinacao(comb_otimizada)
        scores_otimizado.append(score_otimizado)
        
        if (i + 1) % 10 == 0:
            print(f"   ✅ Completados: {i + 1}/{num_testes}")
    
    # Calcular estatísticas
    media_atual = sum(scores_atual) / len(scores_atual)
    media_otimizado = sum(scores_otimizado) / len(scores_otimizado)
    
    melhoria_percentual = ((media_otimizado - media_atual) / media_atual) * 100
    
    vitorias_otimizado = sum(1 for i in range(len(scores_atual)) if scores_otimizado[i] > scores_atual[i])
    taxa_vitoria = (vitorias_otimizado / num_testes) * 100
    
    print("\n" + "=" * 80)
    print("📊 RESULTADOS DO TESTE COMPARATIVO")
    print("=" * 80)
    
    print(f"🎯 GERADOR ATUAL:")
    print(f"   📊 Score médio: {media_atual:.2f}")
    print(f"   ⚡ Score mínimo: {min(scores_atual)}")
    print(f"   🔥 Score máximo: {max(scores_atual)}")
    
    print(f"\n🚀 GERADOR OTIMIZADO:")
    print(f"   📊 Score médio: {media_otimizado:.2f}")
    print(f"   ⚡ Score mínimo: {min(scores_otimizado)}")
    print(f"   🔥 Score máximo: {max(scores_otimizado)}")
    
    print(f"\n📈 COMPARAÇÃO:")
    print(f"   🎯 Melhoria no score: {melhoria_percentual:.1f}%")
    print(f"   🏆 Taxa de vitória: {taxa_vitoria:.1f}%")
    
    if melhoria_percentual > 0:
        status = "✅ GERADOR OTIMIZADO É SUPERIOR"
        recomendacao = "🚀 RECOMENDA-SE USAR O GERADOR OTIMIZADO"
    else:
        status = "⚠️ GERADOR ATUAL MANTÉM VANTAGEM"  
        recomendacao = "🔄 NECESSÁRIO MAIS AJUSTES NO OTIMIZADO"
    
    print(f"\n🏁 CONCLUSÃO:")
    print(f"   {status}")
    print(f"   {recomendacao}")
    
    # Exemplo prático
    print(f"\n📋 EXEMPLO PRÁTICO - CONCURSO 3480:")
    print("=" * 50)
    
    # Gerar uma combinação de cada
    comb_atual = gerador_atual.gerar_combinacao_historica(18, variacao=1)
    comb_otimizada = gerador_otimizado.gerar_combinacao_otimizada(3480, 18)
    
    score_ex_atual = gerador_otimizado.avaliar_qualidade_combinacao(comb_atual)
    score_ex_otimizado = gerador_otimizado.avaliar_qualidade_combinacao(comb_otimizada)
    
    print(f"🎲 ATUAL (18 números):")
    nums_atual = ', '.join(f"{n:02d}" for n in comb_atual)
    print(f"   [{nums_atual}]")
    print(f"   Score: {score_ex_atual}")
    
    print(f"\n🚀 OTIMIZADO (18 números):")
    nums_otimizado = ', '.join(f"{n:02d}" for n in comb_otimizada)
    print(f"   [{nums_otimizado}]")
    print(f"   Score: {score_ex_otimizado}")
    
    if score_ex_otimizado > score_ex_atual:
        print(f"   ✅ Otimizado é {score_ex_otimizado - score_ex_atual} pontos melhor!")
    else:
        print(f"   ⚡ Atual mantém vantagem de {score_ex_atual - score_ex_otimizado} pontos")
    
    return {
        'media_atual': media_atual,
        'media_otimizado': media_otimizado,
        'melhoria_percentual': melhoria_percentual,
        'taxa_vitoria': taxa_vitoria
    }

def demonstrar_melhorias_implementadas():
    """Demonstra as melhorias específicas implementadas"""
    print("\n" + "=" * 80)
    print("🔧 MELHORIAS IMPLEMENTADAS NO GERADOR OTIMIZADO")
    print("=" * 80)
    
    melhorias = [
        "✅ PESOS DINÂMICOS TEMPORAIS: Ajuste automático por período do concurso",
        "✅ MÚLTIPLAS ESTRATÉGIAS: Combinação de frequência, distribuição e padrões",
        "✅ AVALIAÇÃO DE QUALIDADE: Sistema de score para selecionar melhores combinações",
        "✅ OTIMIZAÇÃO POR FORMATO: Estratégias específicas para cada tamanho de aposta",
        "✅ BALANCEAMENTO INTELIGENTE: Distribuição otimizada por grupos numéricos",
        "✅ PADRÕES SEQUENCIAIS: Inclusão controlada de sequências baseadas em dados",
        "✅ DIVERSIFICAÇÃO: Sistema de variações para evitar combinações repetidas"
    ]
    
    for melhoria in melhorias:
        print(f"   {melhoria}")
    
    print(f"\n🎯 OBJETIVO: Aumentar taxa de acertos de 9.29% para 15%+ (13+ acertos)")
    print(f"📊 META: Elevar precisão geral de 80.17% para 85%+")
    print(f"🚀 FOCO: Otimizar especialmente formatos 15-17 números")

if __name__ == "__main__":
    # Executar teste comparativo
    resultados = teste_comparativo_geradores(50)
    
    # Mostrar melhorias implementadas
    demonstrar_melhorias_implementadas()
    
    print(f"\n" + "=" * 80)
    print("🏆 TESTE COMPARATIVO CONCLUÍDO!")
    print("📊 Dados coletados para validação das melhorias propostas")
    print("=" * 80)
