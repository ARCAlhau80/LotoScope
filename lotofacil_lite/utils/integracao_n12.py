#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔗 MÓDULO DE INTEGRAÇÃO N12 PARA GERADORES EXISTENTES
=====================================================
Sistema de integração fácil para aplicar inteligência N12
em qualquer gerador existente do LotoScope.

COMO USAR:
1. Importe este módulo
2. Use o decorador @aplicar_inteligencia_n12
3. Ou chame diretamente otimizar_com_n12(combinacoes)

EXEMPLO DE USO:
```python
from integracao_n12 import aplicar_inteligencia_n12, otimizar_com_n12

@aplicar_inteligencia_n12
def meu_gerador():
    # Seu gerador original aqui
    return combinacoes

# Ou usar diretamente:
combinacoes_otimizadas = otimizar_com_n12(combinacoes_originais)
```

Autor: AR CALHAU
Data: 19/09/2025
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from adaptador_universal_n12 import AdaptadorUniversalN12
from functools import wraps

# Instância global do adaptador
_adaptador_global = None

def inicializar_inteligencia_n12():
    """Inicializa a inteligência N12 (chamada automática)"""
    global _adaptador_global
    if _adaptador_global is None:
        _adaptador_global = AdaptadorUniversalN12()
        _adaptador_global.inicializar_inteligencia()
        _adaptador_global.aplicar_estrategia_pos_equilibrio()
    return _adaptador_global

def obter_estrategia_atual():
    """Obtém a estratégia atual baseada no N12"""
    adaptador = inicializar_inteligencia_n12()
    return adaptador.sistema_n12.predicao_proxima

def aplicar_inteligencia_n12(func):
    """
    Decorador para aplicar inteligência N12 automaticamente
    
    COMO USAR:
    @aplicar_inteligencia_n12
    def meu_gerador():
        return minhas_combinacoes
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\n🧠 APLICANDO INTELIGÊNCIA N12 EM: {func.__name__}")
        print("="*60)
        
        # Inicializar inteligência
        adaptador = inicializar_inteligencia_n12()
        
        # Executar função original
        resultado_original = func(*args, **kwargs)
        
        # Se o resultado são combinações, otimizar
        if isinstance(resultado_original, list) and len(resultado_original) > 0:
            # Verificar se são combinações válidas
            primeiro_item = resultado_original[0]
            if isinstance(primeiro_item, (list, tuple)) and len(primeiro_item) == 15:
                print(f"📦 Resultado original: {len(resultado_original)} combinações")
                
                # Aplicar otimização N12
                combinacoes_otimizadas = adaptador.sistema_n12.aplicar_filtro_inteligente_n12(resultado_original)
                
                if combinacoes_otimizadas:
                    print(f"✨ Resultado otimizado: {len(combinacoes_otimizadas)} combinações")
                    return [item['combinacao'] for item in combinacoes_otimizadas]
                else:
                    print("⚠️ Nenhuma combinação passou no filtro N12. Retornando originais.")
                    return resultado_original
            else:
                print("🔄 Resultado não são combinações. Retornando sem modificação.")
                return resultado_original
        else:
            print("🔄 Resultado vazio ou inválido. Retornando sem modificação.")
            return resultado_original
    
    return wrapper

def otimizar_com_n12(combinacoes_originais, max_resultado=None):
    """
    Otimiza uma lista de combinações com inteligência N12
    
    Args:
        combinacoes_originais: Lista de combinações (cada uma com 15 números)
        max_resultado: Máximo de combinações a retornar (None = todas)
        
    Returns:
        Lista de combinações otimizadas
    """
    print(f"\n🎯 OTIMIZANDO {len(combinacoes_originais)} COMBINAÇÕES COM N12")
    print("-"*50)
    
    # Inicializar inteligência
    adaptador = inicializar_inteligencia_n12()
    
    # Aplicar filtro N12
    combinacoes_otimizadas = adaptador.sistema_n12.aplicar_filtro_inteligente_n12(combinacoes_originais)
    
    if combinacoes_otimizadas:
        # Extrair apenas as combinações (remover metadados)
        resultado = [item['combinacao'] for item in combinacoes_otimizadas]
        
        # Limitar resultado se solicitado
        if max_resultado and len(resultado) > max_resultado:
            resultado = resultado[:max_resultado]
            
        print(f"✅ Otimização concluída: {len(resultado)} combinações selecionadas")
        return resultado
    else:
        print("⚠️ Nenhuma combinação passou no filtro. Retornando amostra das originais.")
        return combinacoes_originais[:max_resultado] if max_resultado else combinacoes_originais

def gerar_combinacoes_inteligentes_n12(quantidade=50):
    """
    Gera combinações completamente novas usando inteligência N12
    
    Args:
        quantidade: Número de combinações a gerar
        
    Returns:
        Lista de combinações otimizadas para a situação atual
    """
    print(f"\n🎲 GERANDO {quantidade} COMBINAÇÕES COM INTELIGÊNCIA N12")
    print("-"*50)
    
    # Inicializar inteligência
    adaptador = inicializar_inteligencia_n12()
    
    # Gerar combinações inteligentes
    combinacoes = adaptador.gerar_combinacoes_inteligentes(quantidade)
    
    print(f"✅ Geradas {len(combinacoes)} combinações inteligentes")
    return combinacoes

def mostrar_status_n12():
    """Mostra o status atual da inteligência N12"""
    print("\n📊 STATUS DA INTELIGÊNCIA N12")
    print("="*50)
    
    adaptador = inicializar_inteligencia_n12()
    
    print(f"🎯 Último concurso: {adaptador.sistema_n12.ultimo_concurso}")
    print(f"📍 N12 atual: {adaptador.sistema_n12.ultimo_n12}")
    print(f"📊 Distribuição atual: {adaptador.sistema_n12.distribuicao_atual}")
    
    if adaptador.sistema_n12.predicao_proxima:
        pred = adaptador.sistema_n12.predicao_proxima
        print(f"\n🔮 PREVISÃO PRÓXIMO CONCURSO:")
        print(f"🔧 Estratégia: {pred['estrategia']}")
        print(f"🎲 Tipo: {pred['tipo']}")
        
        if 'n12_ideais' in pred:
            print(f"📍 N12 ideais: {pred['n12_ideais']}")
            
        print(f"🎯 Distribuições alvo: {pred.get('distribuicoes_alvo', pred['opcoes'])}")

def exemplo_integracao():
    """Exemplo de como integrar N12 em um gerador"""
    print("\n💡 EXEMPLO DE INTEGRAÇÃO")
    print("="*50)
    
    # Simular um gerador existente
    def gerador_exemplo():
        """Gerador de exemplo (simulado)"""
        import random
        combinacoes = []
        for _ in range(20):
            comb = sorted(random.sample(range(1, 26), 15))
            combinacoes.append(comb)
        return combinacoes
    
    # Aplicar decorador
    @aplicar_inteligencia_n12
    def gerador_otimizado():
        return gerador_exemplo()
    
    # Executar
    resultado = gerador_otimizado()
    
    print(f"\n📋 RESULTADO DO EXEMPLO:")
    print(f"   Total de combinações: {len(resultado)}")
    
    # Mostrar primeiras 3
    for i, comb in enumerate(resultado[:3]):
        n12 = comb[11]
        baixos = len([n for n in comb if 1 <= n <= 8])
        medios = len([n for n in comb if 9 <= n <= 17])
        altos = len([n for n in comb if 18 <= n <= 25])
        print(f"   Jogo {i+1}: {comb}")
        print(f"           N12={n12}, B={baixos}, M={medios}, A={altos}")

if __name__ == "__main__":
    # Demonstração do módulo
    print("🔗 MÓDULO DE INTEGRAÇÃO N12 - DEMONSTRAÇÃO")
    print("="*60)
    
    # Mostrar status atual
    mostrar_status_n12()
    
    # Exemplo de integração
    exemplo_integracao()
    
    print(f"\n📚 INSTRUÇÕES DE USO:")
    print("="*30)
    print("1. Import: from integracao_n12 import aplicar_inteligencia_n12")
    print("2. Decorador: @aplicar_inteligencia_n12")
    print("3. Ou direto: otimizar_com_n12(combinacoes)")
    print("4. Novo: gerar_combinacoes_inteligentes_n12(50)")
    print("\n✅ Sistema pronto para uso em qualquer gerador!")