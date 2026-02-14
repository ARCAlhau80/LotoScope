#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 MAPEAMENTO VISUAL DAS FAIXAS - LOTOFÁCIL
==========================================
Visualização das faixas da tabela Resultados_INT
"""

def mostrar_faixas_visuais():
    """Mostra as faixas de forma visual"""
    print("🎯 DEFINIÇÃO DAS FAIXAS NA TABELA RESULTADOS_INT")
    print("="*60)
    
    print("\n📊 DIVISÃO DOS 25 NÚMEROS DA LOTOFÁCIL:")
    print("-"*60)
    
    # Faixa Baixa
    print("🔵 FAIXA BAIXA (Faixa_Baixa):")
    print("   📍 Números: 1, 2, 3, 4, 5, 6, 7, 8")
    print("   📊 Total: 8 números")
    print("   💡 Campo: conta quantos números de 1 a 8 estão na combinação")
    
    print("\n🟡 FAIXA MÉDIA (Faixa_Media):")
    print("   📍 Números: 9, 10, 11, 12, 13, 14, 15, 16, 17")
    print("   📊 Total: 9 números")
    print("   💡 Campo: conta quantos números de 9 a 17 estão na combinação")
    
    print("\n🔴 FAIXA ALTA (Faixa_Alta):")
    print("   📍 Números: 18, 19, 20, 21, 22, 23, 24, 25")
    print("   📊 Total: 8 números")
    print("   💡 Campo: conta quantos números de 18 a 25 estão na combinação")
    
    print("\n" + "="*60)
    print("🧮 COMO CALCULAR:")
    print("-"*60)
    print("Para qualquer combinação de 15 números:")
    print("• Faixa_Baixa = quantidade de números entre 1 e 8")
    print("• Faixa_Media = quantidade de números entre 9 e 17") 
    print("• Faixa_Alta = quantidade de números entre 18 e 25")
    print("• Soma sempre = 15 (total de números na combinação)")
    
    print("\n📈 EXEMPLO PRÁTICO (Concurso 3489):")
    print("-"*60)
    numeros_3489 = [1, 2, 5, 8, 9, 11, 14, 16, 17, 20, 21, 22, 23, 24, 25]
    
    baixos = [n for n in numeros_3489 if 1 <= n <= 8]
    medios = [n for n in numeros_3489 if 9 <= n <= 17]
    altos = [n for n in numeros_3489 if 18 <= n <= 25]
    
    print(f"🎲 Números sorteados: {numeros_3489}")
    print(f"🔵 Baixos (1-8):   {baixos} = {len(baixos)} números")
    print(f"🟡 Médios (9-17):  {medios} = {len(medios)} números") 
    print(f"🔴 Altos (18-25):  {altos} = {len(altos)} números")
    print(f"✅ Total: {len(baixos)} + {len(medios)} + {len(altos)} = {len(baixos) + len(medios) + len(altos)}")
    
    print("\n💾 VALORES NA TABELA:")
    print(f"   Faixa_Baixa = {len(baixos)}")
    print(f"   Faixa_Media = {len(medios)}")
    print(f"   Faixa_Alta = {len(altos)}")

if __name__ == "__main__":
    mostrar_faixas_visuais()