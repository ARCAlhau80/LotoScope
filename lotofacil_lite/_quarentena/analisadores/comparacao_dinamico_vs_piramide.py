#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 COMPARAÇÃO: GERADOR DINÂMICO vs PIRÂMIDE DIRETA
Analisa as diferenças entre os dois métodos de geração
"""

from collections import Counter
import numpy as np

def analisar_combinacoes_gerador_dinamico():
    """Combinações do Gerador Acadêmico Dinâmico (20 números, 20 jogos)"""
    return [
        [1,3,5,6,8,9,10,13,14,15,16,17,18,19,20,21,22,23,24,25],
        [1,3,4,5,6,8,11,12,14,15,16,17,18,19,20,21,22,23,24,25],
        [1,2,3,5,6,8,9,10,11,13,14,16,17,18,19,20,21,22,24,25],
        [1,2,3,5,6,8,9,12,13,15,16,17,18,19,20,21,22,23,24,25],
        [1,2,3,5,6,8,9,10,12,13,16,17,18,19,20,21,22,23,24,25],
        [1,2,3,5,6,8,9,10,11,13,14,16,17,18,20,21,22,23,24,25],
        [1,2,3,4,5,6,7,8,9,12,13,14,15,16,18,19,21,22,23,25],
        [1,2,3,4,5,6,8,9,11,13,14,16,17,18,19,21,22,23,24,25],
        [1,2,3,4,5,6,8,9,10,11,13,14,15,16,17,18,20,21,22,25],
        [1,3,4,5,6,7,8,9,12,13,14,16,17,18,19,20,21,23,24,25],
        [1,2,3,4,5,6,7,8,9,13,14,15,16,17,18,19,20,21,23,25],
        [1,2,3,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21,22,25],
        [1,3,4,5,6,8,9,12,13,14,15,16,17,18,19,21,22,23,24,25],
        [1,2,3,4,5,6,7,8,9,10,13,14,15,17,18,19,21,22,23,25],
        [1,2,3,4,5,6,8,9,10,11,13,14,16,17,18,19,20,21,22,25],
        [1,2,3,5,6,7,8,9,13,14,15,16,17,18,19,21,22,23,24,25],
        [1,2,3,5,6,8,9,10,11,13,14,15,16,17,18,19,20,21,22,25],
        [1,3,5,6,7,8,9,10,11,13,14,15,16,17,18,19,21,22,23,25],
        [1,2,3,4,5,6,7,8,9,10,13,14,15,16,18,19,22,23,24,25],
        [1,2,3,5,6,8,9,10,11,13,14,16,17,18,19,20,21,22,23,25]
    ]

def analisar_combinacoes_piramide_direta():
    """Combinações da Pirâmide Direta (20 números, 20 jogos)"""
    return [
        [1,2,3,4,5,6,7,8,9,10,11,14,15,16,17,18,19,23,24,25],
        [1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,18,19,21,23,25],
        [1,2,3,4,6,7,8,9,10,11,12,13,15,16,17,18,19,20,22,25],
        [1,3,4,5,6,7,8,9,11,12,13,14,16,17,18,19,21,23,24,25],
        [1,2,3,4,5,6,7,8,9,10,11,12,14,17,18,20,22,23,24,25],
        [1,2,4,5,7,8,10,11,12,13,15,16,17,18,20,21,22,23,24,25],
        [1,2,3,4,5,6,7,8,9,10,11,12,17,18,20,21,22,23,24,25],
        [1,2,3,4,5,6,7,8,9,10,11,14,16,17,18,20,22,23,24,25],
        [1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,20,22,25],
        [1,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,22,23,24,25],
        [1,2,3,4,5,7,8,9,10,11,12,14,15,17,18,19,20,21,23,25],
        [1,2,3,4,5,6,7,10,11,12,13,14,16,17,18,19,21,22,23,25],
        [1,2,3,4,6,7,8,9,10,11,12,13,17,18,19,20,22,23,24,25],
        [1,2,3,4,5,6,8,9,10,11,12,14,16,17,18,19,20,22,24,25],
        [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,22,23,25],
        [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,18,19,20,24,25],
        [1,2,3,4,7,9,10,12,13,14,15,16,17,18,20,21,22,23,24,25],
        [1,2,3,4,5,6,9,10,11,13,14,15,16,18,19,21,22,23,24,25],
        [1,4,5,6,8,9,10,11,12,13,14,15,16,18,19,21,22,23,24,25],
        [1,2,3,4,5,7,8,9,10,11,12,13,15,17,18,20,21,22,24,25]
    ]

def comparar_metodos():
    """Compara os dois métodos de geração"""
    print("🔍 ANÁLISE COMPARATIVA: GERADOR DINÂMICO vs PIRÂMIDE DIRETA")
    print("=" * 80)
    
    # Carrega as combinações
    dinamico = analisar_combinacoes_gerador_dinamico()
    piramide = analisar_combinacoes_piramide_direta()
    
    # Configuração da pirâmide atual
    piramide_config = {
        '0_acertos': [16],
        '1_acerto': [8, 17, 22],
        '2_acertos': [1, 2, 7, 9, 10, 11, 20, 24],
        '3_acertos': [3, 4, 5, 6, 12, 13, 14, 15, 19, 21, 23],
        '4_ou_mais': [18, 25]
    }
    
    print("📊 CONFIGURAÇÃO ATUAL DA PIRÂMIDE:")
    for faixa, numeros in piramide_config.items():
        print(f"   {faixa.replace('_', ' ').title()}: {numeros} ({len(numeros)} números)")
    
    print("\n" + "="*80)
    
    # 1. FREQUÊNCIA DE USO DOS NÚMEROS
    print("\n1️⃣ FREQUÊNCIA DE USO DOS NÚMEROS:")
    print("-" * 50)
    
    contador_dinamico = Counter()
    contador_piramide = Counter()
    
    for comb in dinamico:
        contador_dinamico.update(comb)
    
    for comb in piramide:
        contador_piramide.update(comb)
    
    print("🔥 TOP 10 NÚMEROS MAIS USADOS:")
    print(f"{'Pos':<3} {'Nº':<3} {'Dinâmico':<10} {'Pirâmide':<10} {'Diferença':<10}")
    print("-" * 45)
    
    numeros_ordenados = range(int(int(1)), int(int(26))
    comparacao_uso = []
    
    for num in numeros_ordenados:
        freq_din = contador_dinamico.get(num), int(0))
        freq_pir = contador_piramide.get(num, 0)
        diff = freq_din - freq_pir
        comparacao_uso.append((num, freq_din, freq_pir, diff))
    
    # Ordena por uso no dinâmico
    comparacao_uso.sort(key=lambda x: x[1], reverse=True)
    
    for i, (num, freq_din, freq_pir, diff) in enumerate(comparacao_uso[:15], 1):
        sinal = "+" if diff > 0 else ""
        print(f"{i:<3} {num:<3} {freq_din:<10} {freq_pir:<10} {sinal}{diff:<10}")
    
    # 2. ANÁLISE POR FAIXAS DA PIRÂMIDE
    print(f"\n2️⃣ USO POR FAIXAS DA PIRÂMIDE:")
    print("-" * 50)
    
    for faixa, numeros_faixa in piramide_config.items():
        if not numeros_faixa:
            continue
            
        # Calcula uso total da faixa em cada método
        uso_dinamico = sum(contador_dinamico.get(n, 0) for n in numeros_faixa)
        uso_piramide = sum(contador_piramide.get(n, 0) for n in numeros_faixa)
        
        # Média por jogo
        media_din = uso_dinamico / 20
        media_pir = uso_piramide / 20
        
        faixa_nome = faixa.replace('_', ' ').title()
        print(f"📊 {faixa_nome:12}: Dinâmico={media_din:.1f}/jogo | Pirâmide={media_pir:.1f}/jogo | Diff={media_din-media_pir:+.1f}")
    
    # 3. DIVERSIDADE E VARIAÇÃO
    print(f"\n3️⃣ DIVERSIDADE E VARIAÇÃO:")
    print("-" * 50)
    
    # Números únicos utilizados
    numeros_unicos_din = len([n for n in range(int(int(1)), int(int(26)) if contador_dinamico.get(n), int(0)) > 0])
    numeros_unicos_pir = len([n for n in range(int(int(1)), int(int(26)) if contador_piramide.get(n), int(0)) > 0])
    
    print(f"📈 Números únicos utilizados:")
    print(f"   Dinâmico: {numeros_unicos_din}/25 números")
    print(f"   Pirâmide: {numeros_unicos_pir}/25 números")
    
    # Números sempre presentes (100%)
    sempre_din = [n for n in range(int(int(1)), int(int(26)) if contador_dinamico.get(n), int(0)) == 20]
    sempre_pir = [n for n in range(int(int(1)), int(int(26)) if contador_piramide.get(n), int(0)) == 20]
    
    print(f"\n🔒 Números SEMPRE presentes (100%):")
    print(f"   Dinâmico: {sempre_din} ({len(sempre_din)} números)")
    print(f"   Pirâmide: {sempre_pir} ({len(sempre_pir)} números)")
    
    # Números nunca usados
    nunca_din = [n for n in range(int(int(1)), int(int(26)) if contador_dinamico.get(n), int(0)) == 0]
    nunca_pir = [n for n in range(int(int(1)), int(int(26)) if contador_piramide.get(n), int(0)) == 0]
    
    print(f"\n❌ Números NUNCA usados:")
    print(f"   Dinâmico: {nunca_din} ({len(nunca_din)} números)")
    print(f"   Pirâmide: {nunca_pir} ({len(nunca_pir)} números)")
    
    # 4. ESTATÍSTICAS DAS SOMAS
    print(f"\n4️⃣ ESTATÍSTICAS DAS SOMAS:")
    print("-" * 50)
    
    somas_din = [sum(comb) for comb in dinamico]
    somas_pir = [sum(comb) for comb in piramide]
    
    print(f"📊 Soma das combinações:")
    print(f"   Dinâmico: Média={np.mean(somas_din):.1f} | Min={min(somas_din)} | Max={max(somas_din)} | Desvio={np.std(somas_din):.1f}")
    print(f"   Pirâmide: Média={np.mean(somas_pir):.1f} | Min={min(somas_pir)} | Max={max(somas_pir)} | Desvio={np.std(somas_pir):.1f}")
    
    # 5. ANÁLISE DE ESTRATÉGIAS
    print(f"\n5️⃣ DIFERENÇAS ESTRATÉGICAS:")
    print("-" * 50)
    
    # Números das faixas baixas (0 e 1 acerto)
    faixas_baixas = piramide_config['0_acertos'] + piramide_config['1_acerto']
    uso_baixas_din = sum(contador_dinamico.get(n, 0) for n in faixas_baixas)
    uso_baixas_pir = sum(contador_piramide.get(n, 0) for n in faixas_baixas)
    
    print(f"🚀 Foco em faixas baixas (0+1 acertos):")
    print(f"   Dinâmico: {uso_baixas_din} usos ({uso_baixas_din/400*100:.1f}% do total)")
    print(f"   Pirâmide: {uso_baixas_pir} usos ({uso_baixas_pir/400*100:.1f}% do total)")
    
    # Números das faixas altas (4+ acertos)
    faixas_altas = piramide_config['4_ou_mais']
    uso_altas_din = sum(contador_dinamico.get(n, 0) for n in faixas_altas)
    uso_altas_pir = sum(contador_piramide.get(n, 0) for n in faixas_altas)
    
    print(f"\n⚡ Foco em faixas altas (4+ acertos):")
    print(f"   Dinâmico: {uso_altas_din} usos ({uso_altas_din/400*100:.1f}% do total)")
    print(f"   Pirâmide: {uso_altas_pir} usos ({uso_altas_pir/400*100:.1f}% do total)")
    
    # 6. CONCLUSÕES
    print(f"\n6️⃣ PRINCIPAIS DIFERENÇAS:")
    print("-" * 50)
    
    print("🔍 GERADOR ACADÊMICO DINÂMICO:")
    print("   ✅ Integra múltiplos insights (correlações, tendências, estados)")
    print("   ✅ Aplica pesos acadêmicos calculados dinamicamente")
    print("   ✅ Usa pirâmide como UM dos fatores (33% do tempo)")
    print("   ✅ Balanceamento mais conservador das faixas")
    print("   ✅ Maior diversidade na seleção")
    
    print(f"\n🔺 PIRÂMIDE DIRETA:")
    print("   ✅ Foco total nas transições previstas pela pirâmide")
    print("   ✅ Prioriza números saindo das faixas baixas")
    print("   ✅ Estratégia mais agressiva com faixas específicas")
    print("   ✅ Menor variação - mais determinística")
    print("   ✅ Seguimento rigoroso das predições da IA")
    
    # Números mais divergentes
    print(f"\n🎯 NÚMEROS COM MAIOR DIVERGÊNCIA DE USO:")
    print("-" * 45)
    
    divergencias = [(num, abs(freq_din - freq_pir), freq_din, freq_pir) 
                   for num, freq_din, freq_pir, _ in comparacao_uso]
    divergencias.sort(key=lambda x: x[1], reverse=True)
    
    for num, div, freq_din, freq_pir in divergencias[:8]:
        if div > 0:
            if freq_din > freq_pir:
                print(f"   Nº {num:2d}: Dinâmico favorece (+{div}) - {freq_din} vs {freq_pir}")
            else:
                print(f"   Nº {num:2d}: Pirâmide favorece (+{div}) - {freq_pir} vs {freq_din}")

if __name__ == "__main__":
    comparar_metodos()
