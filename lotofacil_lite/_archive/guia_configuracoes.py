#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📋 GUIA RÁPIDO - CONFIGURAÇÕES DE RANGES

Copie e cole qualquer configuração abaixo no arquivo principal
teste_sobreposicao_simplificado.py na linha ~337

Autor: AR CALHAU
Data: 25 de Agosto de 2025
"""

# 🚀 CONFIGURAÇÕES PRONTAS PARA USAR:

# ⚡ TESTE SUPER RÁPIDO (apenas validação)
num_concursos = 3   # ~15 segundos

# 🚀 TESTE RÁPIDO (padrão anterior)
num_concursos = 5   # ~30 segundos

# 📊 TESTE MÉDIO (boa precisão)
num_concursos = 10  # ~1-2 minutos

# 📈 TESTE EXTENSO (alta precisão)  
num_concursos = 15  # ~2-3 minutos

# 🔬 TESTE APROFUNDADO
num_concursos = 20  # ~3-4 minutos

# 🏆 TESTE MUITO DETALHADO
num_concursos = 30  # ~5-7 minutos

# 💎 TESTE COMPLETO (máxima precisão)
num_concursos = 50  # ~10-15 minutos

# 🎯 RECOMENDAÇÕES POR CASO DE USO:

"""
🔍 PARA ANÁLISE RÁPIDA:
num_concursos = 5
num_combinacoes = 3

📊 PARA ANÁLISE CONFIÁVEL:  
num_concursos = 15
num_combinacoes = 3

🎯 PARA ANÁLISE CIENTÍFICA:
num_concursos = 30
num_combinacoes = 5

💎 PARA ANÁLISE DEFINITIVA:
num_concursos = 50
num_combinacoes = 5
"""

# 📈 RESULTADOS COMPARATIVOS JÁ OBTIDOS:
"""
🔬 RESULTADOS DOS TESTES REALIZADOS:

5 CONCURSOS:
• Baixa Sobreposição: 148.13 pontos
• 12.5 acertos médios, 100% taxa 11+, 40% taxa 13+

10 CONCURSOS:  
• Baixa Sobreposição: 160.80 pontos
• 12.2 acertos médios, 97% taxa 11+, 50% taxa 13+

15 CONCURSOS:
• Baixa Sobreposição: 120.93 pontos  
• 11.9 acertos médios, 96% taxa 11+, 24% taxa 13+

💡 CONCLUSÃO: Baixa Sobreposição SEMPRE vence!
"""

def configuracao_atual():
    """
    Mostra a configuração atualmente definida
    """
    print("⚙️ CONFIGURAÇÃO ATUAL:")
    print(f"   📊 Concursos: {num_concursos}")
    print(f"   🎲 Combinações: {num_combinacoes}")
    
    tempo_estimado = {
        3: "15 segundos",
        5: "30 segundos", 
        10: "1-2 minutos",
        15: "2-3 minutos",
        20: "3-4 minutos",
        30: "5-7 minutos",
        50: "10-15 minutos"
    }
    
    tempo = tempo_estimado.get(num_concursos, f"{num_concursos//5} minutos aprox.")
    print(f"   ⏰ Tempo estimado: {tempo}")

if __name__ == "__main__":
    # Use uma das configurações acima
    num_concursos = 15  # 📊 CONFIGURAÇÃO ATUAL
    num_combinacoes = 3
    
    configuracao_atual()
    
    print("\n📝 PARA ALTERAR:")
    print("1. Modifique a variável num_concursos acima")
    print("2. Execute: python teste_sobreposicao_simplificado.py")
