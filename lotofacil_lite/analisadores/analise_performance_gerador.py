#!/usr/bin/env python3
"""
Análise de Performance do Gerador Dinâmico
Investigando a queda de performance no último concurso
"""

def analisar_combinacoes_geradas():
    """Analisa as combinações que tiveram baixa performance"""
    
    # Combinações geradas que tiveram baixo desempenho
    combinacoes = [
        [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 14, 15, 18, 19, 22, 24, 25],
        [1, 2, 3, 5, 6, 8, 10, 12, 14, 15, 18, 19, 20, 22, 24, 25],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 15, 18, 19, 21, 24, 25],
        [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 18, 20, 25],
        [1, 2, 4, 5, 6, 7, 9, 11, 12, 13, 15, 18, 20, 22, 23, 25],
        [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 18, 19, 20, 25],
        [1, 2, 3, 4, 5, 6, 7, 9, 12, 13, 14, 15, 18, 20, 22, 25],
        [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 18, 19, 21, 25],
        [1, 2, 3, 4, 5, 6, 12, 14, 15, 16, 18, 19, 20, 21, 23, 25],
        [1, 3, 4, 5, 6, 11, 12, 13, 14, 15, 18, 19, 21, 23, 24, 25],
        [1, 3, 4, 5, 6, 7, 10, 11, 12, 14, 15, 18, 19, 20, 21, 23, 25],  # 17 números
        [1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 20, 23, 25],
        [1, 2, 5, 6, 9, 11, 12, 13, 14, 15, 18, 20, 21, 22, 24, 25]
    ]
    
    print("🔍 ANÁLISE DE COMBINAÇÕES - GERADOR DINÂMICO")
    print("="*60)
    
    # Análise de frequência dos números
    frequencia = {}
    total_jogos = len(combinacoes)
    
    for combo in combinacoes:
        for num in combo:
            frequencia[num] = frequencia.get(num, 0) + 1
    
    print(f"📊 Total de jogos analisados: {total_jogos}")
    print(f"📊 Números mais frequentes:")
    
    # Ordenar por frequência
    nums_ordenados = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)
    
    for num, freq in nums_ordenados[:10]:
        percentual = (freq / total_jogos) * 100
        print(f"   {num:2d}: {freq:2d} vezes ({percentual:.1f}%)")
    
    # Análise de padrões
    print(f"\n🎯 ANÁLISE DE PADRÕES:")
    
    # Números que aparecem em TODOS os jogos
    nums_sempre = set(combinacoes[0])
    for combo in combinacoes[1:]:
        nums_sempre = nums_sempre.intersection(set(combo))
    
    if nums_sempre:
        print(f"   Números em TODOS os jogos: {sorted(nums_sempre)}")
    else:
        print(f"   Nenhum número aparece em todos os jogos")
    
    # Números que aparecem em mais de 80% dos jogos
    nums_frequentes = []
    for num, freq in nums_ordenados:
        if freq >= total_jogos * 0.8:
            nums_frequentes.append(num)
    
    print(f"   Números em 80%+ dos jogos: {nums_frequentes}")
    
    # Análise de sequências
    print(f"\n🔢 ANÁLISE DE SEQUÊNCIAS:")
    sequencias_encontradas = []
    
    for combo in combinacoes:
        combo_sorted = sorted(combo)
        sequencia_atual = []
        
        for i in range(len(combo_sorted) - 1):
            if combo_sorted[i+1] - combo_sorted[i] == 1:
                if not sequencia_atual:
                    sequencia_atual = [combo_sorted[i], combo_sorted[i+1]]
                else:
                    sequencia_atual.append(combo_sorted[i+1])
            else:
                if len(sequencia_atual) >= 3:
                    sequencias_encontradas.append(sequencia_atual.copy())
                sequencia_atual = []
        
        # Verificar última sequência
        if len(sequencia_atual) >= 3:
            sequencias_encontradas.append(sequencia_atual.copy())
    
    if sequencias_encontradas:
        print(f"   Sequências de 3+ números consecutivos encontradas:")
        for seq in sequencias_encontradas:
            print(f"      {seq}")
    else:
        print(f"   Poucas sequências consecutivas longas")
    
    # Análise de distribuição por faixas
    print(f"\n📈 DISTRIBUIÇÃO POR FAIXAS:")
    
    faixas = {
        "1-5": 0,
        "6-10": 0, 
        "11-15": 0,
        "16-20": 0,
        "21-25": 0
    }
    
    for combo in combinacoes:
        for num in combo:
            if 1 <= num <= 5:
                faixas["1-5"] += 1
            elif 6 <= num <= 10:
                faixas["6-10"] += 1
            elif 11 <= num <= 15:
                faixas["11-15"] += 1
            elif 16 <= num <= 20:
                faixas["16-20"] += 1
            elif 21 <= num <= 25:
                faixas["21-25"] += 1
    
    total_nums = sum(len(combo) for combo in combinacoes)
    
    for faixa, count in faixas.items():
        percentual = (count / total_nums) * 100
        print(f"   {faixa}: {count:3d} números ({percentual:.1f}%)")
    
    return combinacoes, frequencia, nums_frequentes

def sugerir_melhorias(combinacoes, frequencia, nums_frequentes):
    """Sugere melhorias baseadas na análise"""
    
    print(f"\n💡 SUGESTÕES DE MELHORIA:")
    print("="*40)
    
    # Análise do último resultado da Lotofácil (precisa ser fornecido)
    print("1. 🎯 COMPARAÇÃO COM RESULTADO REAL:")
    print("   ⚠️  Para análise completa, preciso do resultado do último concurso")
    print("   💡 Adicione: resultado_ultimo_concurso = [x, y, z, ...]")
    
    print(f"\n2. 🔄 DIVERSIFICAÇÃO DE ESTRATÉGIAS:")
    print(f"   • Muito foco nos números: {nums_frequentes[:5]}")
    print(f"   • Considere reduzir frequência destes números")
    print(f"   • Experimente mais números das faixas 16-20 e 21-25")
    
    print(f"\n3. ⚖️  BALANCEAMENTO:")
    print(f"   • Distribua melhor entre faixas numéricas")
    print(f"   • Evite muitas sequências consecutivas")
    print(f"   • Varie padrões de pares/ímpares")
    
    print(f"\n4. 🧪 TESTE DE HIPÓTESES:")
    print(f"   • O algoritmo pode estar 'viciado' em padrões recentes")
    print(f"   • Considere expandir janela histórica de análise")
    print(f"   • Teste com diferentes pesos para dados históricos")
    
    print(f"\n5. 🎲 ELEMENTO ALEATÓRIO:")
    print(f"   • Adicione 10-20% de aleatoriedade às escolhas")
    print(f"   • Evite determinismo excessivo")
    
def main():
    """Função principal de análise"""
    print("🚀 INICIANDO ANÁLISE DE PERFORMANCE")
    print("="*60)
    
    combinacoes, frequencia, nums_frequentes = analisar_combinacoes_geradas()
    sugerir_melhorias(combinacoes, frequencia, nums_frequentes)
    
    print(f"\n📋 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("1. Forneça o resultado do último concurso para análise detalhada")
    print("2. Execute: python gerador_academico_dinamico_megasena.py")
    print("3. Ajuste parâmetros baseado nas sugestões acima")
    print("4. Teste com janela histórica maior")
    
    print(f"\n✅ Análise concluída!")

if __name__ == "__main__":
    main()
