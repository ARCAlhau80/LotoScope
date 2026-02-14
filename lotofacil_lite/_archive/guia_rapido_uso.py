#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GUIA RÁPIDO: GERADOR ACADÊMICO DINÂMICO COM FILTRO VALIDADO

COMO USAR O SISTEMA COMPLETO - REFERÊNCIA RÁPIDA
"""

# ============================================================
# 📚 IMPORTAÇÃO E CRIAÇÃO
# ============================================================

from gerador_academico_dinamico import GeradorAcademicoDinamico

# Cria o gerador (já vem com filtro ativado)
gerador = GeradorAcademicoDinamico()

# ============================================================
# 🎲 GERAÇÃO DE COMBINAÇÕES - MÉTODOS PRINCIPAIS
# ============================================================

# MÉTODO 1: Uma combinação simples
combinacao = gerador.gerar_combinacao_academica(qtd_numeros=15)
print(f"Combinação: {combinacao}")

# MÉTODO 2: Múltiplas combinações
combinacoes = gerador.gerar_multiplas_combinacoes(quantidade=5, qtd_numeros=15)
for i, comb in enumerate(combinacoes, 1):
    print(f"Jogo {i}: {comb}")

# MÉTODO 3: Usando pirâmide invertida (se disponível)
if gerador.usar_piramide:
    comb_piramide = gerador.gerar_combinacao_piramide(qtd_numeros=15)
    print(f"Pirâmide: {comb_piramide}")

# ============================================================
# ⚙️ CONFIGURAÇÃO DO FILTRO VALIDADO
# ============================================================

# Configuração padrão (recomendada) - 11 a 13 acertos
gerador.configurar_filtro_validado()

# Desativar filtro
gerador.configurar_filtro_validado(usar_filtro=False)

# Ativar com configuração personalizada
gerador.configurar_filtro_validado(
    usar_filtro=True,
    min_acertos=10,  # Mínimo de acertos
    max_acertos=14   # Máximo de acertos
)

# ============================================================
# 📊 VALIDAÇÃO E ANÁLISE DE COMBINAÇÕES
# ============================================================

# Verificar se uma combinação passa no filtro
combinacao_teste = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
valido = gerador.validar_combinacao_filtro(combinacao_teste)
print(f"Passou no filtro: {valido}")

# Calcular acertos com os jogos validados
acertos = gerador.calcular_acertos_filtros(combinacao_teste)
print(f"Acertos Jogo 1: {acertos['jogo_1']}")
print(f"Acertos Jogo 2: {acertos['jogo_2']}")

# Analisar eficiência do filtro
resultado = gerador.analisar_eficiencia_filtro(num_amostras=100)
print(f"Taxa de aprovação: {resultado['taxa_aprovacao']:.1f}%")

# ============================================================
# 💰 INFORMAÇÕES DE CUSTO E APOSTAS
# ============================================================

# Custos por quantidade de números
custos = {
    15: 3.50,    # R$ 3,50
    16: 56.00,   # R$ 56,00  
    17: 476.00,  # R$ 476,00
    18: 2856.00, # R$ 2.856,00
    19: 13566.00, # R$ 13.566,00
    20: 54264.00  # R$ 54.264,00
}

# Calcular custo total
qtd_jogos = 5
qtd_numeros = 15
custo_total = custos[qtd_numeros] * qtd_jogos
print(f"Custo para {qtd_jogos} jogos de {qtd_numeros} números: R$ {custo_total:.2f}")

# ============================================================
# 🔥 EXEMPLOS PRÁTICOS DE USO
# ============================================================

def exemplo_cartela_basica():
    """Cartela básica de 5 jogos"""
    gerador = GeradorAcademicoDinamico()
    
    # Gera 5 combinações de 15 números
    combinacoes = gerador.gerar_multiplas_combinacoes(quantidade=5, qtd_numeros=15)
    
    print("🎲 CARTELA BÁSICA - 5 JOGOS DE 15 NÚMEROS")
    print("=" * 50)
    
    for i, comb in enumerate(combinacoes, 1):
        acertos = gerador.calcular_acertos_filtros(comb)
        valido = "✅" if gerador.validar_combinacao_filtro(comb) else "❌"
        print(f"Jogo {i}: {comb} [{valido}] J1:{acertos['jogo_1']} J2:{acertos['jogo_2']}")
    
    print(f"\n💰 Custo total: R$ {len(combinacoes) * 3.50:.2f}")

def exemplo_cartela_diversificada():
    """Cartela com diferentes quantidades"""
    gerador = GeradorAcademicoDinamico()
    
    apostas = [
        (15, 3),  # 3 jogos de 15 números
        (16, 2),  # 2 jogos de 16 números  
        (17, 1)   # 1 jogo de 17 números
    ]
    
    custo_total = 0
    print("🎲 CARTELA DIVERSIFICADA")
    print("=" * 40)
    
    for qtd_nums, qtd_jogos in apostas:
        combinacoes = gerador.gerar_multiplas_combinacoes(qtd_jogos, qtd_nums)
        custo_grupo = custos[qtd_nums] * qtd_jogos
        custo_total += custo_grupo
        
        print(f"\n{qtd_nums} números ({qtd_jogos} jogos) - R$ {custo_grupo:.2f}:")
        for i, comb in enumerate(combinacoes, 1):
            acertos = gerador.calcular_acertos_filtros(comb)
            print(f"   {comb} [J1:{acertos['jogo_1']} J2:{acertos['jogo_2']}]")
    
    print(f"\n💰 Custo total: R$ {custo_total:.2f}")

# ============================================================
# 🔧 CONFIGURAÇÕES AVANÇADAS
# ============================================================

def configuracoes_avancadas():
    """Exemplos de configurações avançadas"""
    gerador = GeradorAcademicoDinamico()
    
    # 1. Filtro mais rigoroso (somente 12-13 acertos)
    gerador.configurar_filtro_validado(usar_filtro=True, min_acertos=12, max_acertos=13)
    
    # 2. Filtro mais flexível (10-14 acertos)
    gerador.configurar_filtro_validado(usar_filtro=True, min_acertos=10, max_acertos=14)
    
    # 3. Sem filtro (máxima diversidade)
    gerador.configurar_filtro_validado(usar_filtro=False)
    
    # 4. Volta ao padrão recomendado
    gerador.configurar_filtro_validado()  # 11-13 acertos

# ============================================================
# 📋 CHECKLIST DE USO
# ============================================================

"""
✅ CHECKLIST PARA USAR O GERADOR:

1. Importar: from gerador_academico_dinamico import GeradorAcademicoDinamico
2. Criar: gerador = GeradorAcademicoDinamico()
3. Configurar filtro (opcional): gerador.configurar_filtro_validado()
4. Gerar combinações: gerador.gerar_multiplas_combinacoes()
5. Verificar resultados: usar calcular_acertos_filtros() e validar_combinacao_filtro()

🎯 DICAS IMPORTANTES:
- O filtro já vem ativado por padrão (11-13 acertos)
- Todas as combinações geradas passam pelo filtro automaticamente
- Use analisar_eficiencia_filtro() para ver estatísticas do filtro
- O sistema integra dados da base em tempo real
- Suporta de 15 a 20 números por jogo
"""

if __name__ == "__main__":
    print(__doc__)
    print("\n🎲 Executando exemplos práticos...")
    
    try:
        exemplo_cartela_basica()
        print("\n" + "="*60)
        exemplo_cartela_diversificada()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Certifique-se de que a base de dados está acessível")
