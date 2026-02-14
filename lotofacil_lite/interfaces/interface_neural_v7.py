#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 INTERFACE SISTEMA NEURAL V7 - LOTOFÁCIL
==========================================
Interface para integração com Super Menu
Inclui análise de distribuição Altos/Baixos
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'sistemas'))

from sistema_neural_network_v7 import SistemaNeuralNetworkV7

def executar_neural_v7_interface():
    """Interface para o Super Menu"""
    print("🧠 SISTEMA NEURAL NETWORK V7.0")
    print("="*50)
    print("🆕 Incorpora padrões de distribuição Altos/Baixos")
    print("🎯 Meta: 76%+ (11/15 acertos)")
    print("="*50)
    
    try:
        # Criar e executar sistema
        sistema = SistemaNeuralNetworkV7()
        resultado = sistema.executar_sistema_completo()
        
        if resultado:
            print("\n" + "="*50)
            print("🎯 PREDIÇÃO NEURAL V7.0")
            print("="*50)
            
            numeros = sorted(resultado['numeros'])
            print(f"📋 Números sugeridos: {numeros}")
            print(f"🔢 Baixos (2-13): {resultado['qtd_baixos']} números")
            print(f"🔢 Altos (14-25): {resultado['qtd_altos']} números")
            print(f"📊 Distribuição predita: {resultado['distribuicao_predita']}")
            print(f"📈 Situação atual: {resultado['categoria_atual']}")
            print(f"🔄 Prob. reversão para altos: {resultado['prob_mais_altos']:.1%}")
            print(f"🔄 Prob. reversão para baixos: {resultado['prob_mais_baixos']:.1%}")
            
            print("\n📊 ANÁLISE INTELIGENTE:")
            if resultado['prob_mais_altos'] > 0.4:
                print("   ✅ Alto potencial para números altos (14-25)")
            if resultado['prob_mais_baixos'] > 0.4:
                print("   ✅ Alto potencial para números baixos (2-13)")
            
            print(f"\n🎲 JOGO RECOMENDADO:")
            # Formatar em linha
            numeros_formatados = " - ".join([f"{num:02d}" for num in numeros])
            print(f"   {numeros_formatados}")
            
            print("\n" + "="*50)
            print("✅ SISTEMA NEURAL V7.0 CONCLUÍDO!")
            print("="*50)
            
            return numeros
        else:
            print("❌ Erro na execução do sistema")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    executar_neural_v7_interface()