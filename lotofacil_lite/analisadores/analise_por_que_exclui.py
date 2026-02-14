#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANÁLISE: POR QUE CLÁUSULAS EXCLUEM COMBINAÇÕES?
=================================================
Demonstra como metadados podem variar entre combinações similares,
explicando por que cláusulas "perfeitas" não capturam tudo.

Concurso 3489: [1, 2, 5, 8, 9, 11, 14, 16, 17, 20, 21, 22, 23, 24, 25]

Autor: AR CALHAU
Data: 18/09/2025
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


def calcular_metadados_3489():
    """Calcula os metadados do concurso 3489 manualmente"""
    
    numeros_3489 = [1, 2, 5, 8, 9, 11, 14, 16, 17, 20, 21, 22, 23, 24, 25]
    
    print("🎯 ANÁLISE DETALHADA: CONCURSO 3489")
    print("="*60)
    print(f"📋 Números: {numeros_3489}")
    print("="*60)
    
    # Calculando metadados manualmente
    metadados = {}
    
    # 1. QtdePrimos
    primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    qtde_primos = sum(1 for n in numeros_3489 if n in primos)
    metadados['QtdePrimos'] = qtde_primos
    
    # 2. QtdeFibonacci  
    fibonacci = [1, 2, 3, 5, 8, 13, 21]
    qtde_fibonacci = sum(1 for n in numeros_3489 if n in fibonacci)
    metadados['QtdeFibonacci'] = qtde_fibonacci
    
    # 3. QtdeImpares
    qtde_impares = sum(1 for n in numeros_3489 if n % 2 == 1)
    metadados['QtdeImpares'] = qtde_impares
    
    # 4. SomaTotal
    soma_total = sum(numeros_3489)
    metadados['SomaTotal'] = soma_total
    
    # 5. Quintis (1-5, 6-10, 11-15, 16-20, 21-25)
    quintil1 = sum(1 for n in numeros_3489 if 1 <= n <= 5)
    quintil2 = sum(1 for n in numeros_3489 if 6 <= n <= 10)
    quintil3 = sum(1 for n in numeros_3489 if 11 <= n <= 15)
    quintil4 = sum(1 for n in numeros_3489 if 16 <= n <= 20)
    quintil5 = sum(1 for n in numeros_3489 if 21 <= n <= 25)
    
    metadados.update({
        'Quintil1': quintil1,
        'Quintil2': quintil2, 
        'Quintil3': quintil3,
        'Quintil4': quintil4,
        'Quintil5': quintil5
    })
    
    # 6. DistanciaExtremos
    distancia_extremos = max(numeros_3489) - min(numeros_3489)
    metadados['DistanciaExtremos'] = distancia_extremos
    
    # 7. QtdeMultiplos3
    qtde_multiplos3 = sum(1 for n in numeros_3489 if n % 3 == 0)
    metadados['QtdeMultiplos3'] = qtde_multiplos3
    
    # 8. Faixas (1-8=Baixa, 9-17=Média, 18-25=Alta)
    faixa_baixa = sum(1 for n in numeros_3489 if 1 <= n <= 8)
    faixa_media = sum(1 for n in numeros_3489 if 9 <= n <= 17)
    faixa_alta = sum(1 for n in numeros_3489 if 18 <= n <= 25)
    
    metadados.update({
        'Faixa_Baixa': faixa_baixa,
        'Faixa_Media': faixa_media,
        'Faixa_Alta': faixa_alta
    })
    
    print("📊 METADADOS CALCULADOS DO CONCURSO 3489:")
    for campo, valor in metadados.items():
        print(f"   • {campo}: {valor}")
    
    return metadados

def comparar_com_suas_clausulas():
    """Compara os metadados reais com suas cláusulas"""
    
    metadados_3489 = calcular_metadados_3489()
    
    print(f"\n🔍 COMPARAÇÃO COM SUAS CLÁUSULAS:")
    print("-"*60)
    
    # Suas cláusulas originais
    suas_clausulas = {
        'QtdePrimos': (4, 5),
        'QtdeFibonacci': (3, 5),
        'QtdeImpares': (7, 9),
        'SomaTotal': (184, 218),
        'Quintil1': (2, 4),
        'Quintil2': (2, 4),  # ERRO: você colocou 2-4, mas 3489 tem 1!
        'Quintil3': (2, 3),
        'Quintil4': (2, 3),
        'Quintil5': (3, 5),
        'DistanciaExtremos': (22, 24),
        'QtdeMultiplos3': (3, 6),
        'Faixa_Baixa': (4, 6),
        'Faixa_Media': (4, 6),
        'Faixa_Alta': (2, 5),
    }
    
    clausulas_que_falharam = []
    
    for campo, (min_val, max_val) in suas_clausulas.items():
        if campo in metadados_3489:
            valor_real = metadados_3489[campo]
            
            if min_val <= valor_real <= max_val:
                status = "✅ PASSA"
            else:
                status = "❌ FALHA"
                clausulas_que_falharam.append((campo, valor_real, min_val, max_val))
                
            print(f"   {status} | {campo}: {valor_real} (faixa: {min_val}-{max_val})")
    
    print(f"\n" + "="*60)
    if clausulas_que_falharam:
        print("❌ CLÁUSULAS QUE EXCLUEM O CONCURSO 3489:")
        print("="*60)
        for campo, valor, min_val, max_val in clausulas_que_falharam:
            print(f"🚫 {campo}: valor {valor} NÃO está na faixa {min_val}-{max_val}")
            
        print(f"\n💡 ESTA É A RESPOSTA À SUA PERGUNTA!")
        print(f"   Suas cláusulas são muito RESTRITIVAS para alguns campos.")
        print(f"   Para incluir o 3489, precisa ajustar essas faixas.")
        
    else:
        print("✅ TODAS AS CLÁUSULAS PASSARAM!")
        print("   O concurso 3489 DEVERIA ser incluído.")

def demonstrar_variacao_metadados():
    """Demonstra como metadados podem variar entre combinações similares"""
    
    print(f"\n🎲 DEMONSTRAÇÃO: VARIAÇÃO DE METADADOS")
    print("="*60)
    
    db_config = DatabaseConfig()
    
    # Buscar algumas combinações com SomaTotal próxima ao 3489 (204)
    query = """SELECT TOP 5 N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
    QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal, 
    Quintil1, Quintil2, Quintil3, Quintil4, Quintil5
    FROM COMBINACOES_LOTOFACIL 
    WHERE SomaTotal BETWEEN 200 AND 208
    ORDER BY SomaTotal"""
    
    try:
        resultados = db_config.execute_query(query)
        
        print(f"📊 COMBINAÇÕES COM SOMA PRÓXIMA A 204:")
        print(f"    (Mostrando como metadados variam mesmo com somas similares)")
        print()
        
        for i, combo in enumerate(resultados, 1):
            numeros = combo[:15]
            metadados = combo[15:]
            
            numeros_str = " ".join([f"{n:2d}" for n in numeros])
            print(f"   {i}. [{numeros_str}]")
            print(f"      Primos:{metadados[0]} Fib:{metadados[1]} Ímp:{metadados[2]} Soma:{metadados[3]}")
            print(f"      Q1:{metadados[4]} Q2:{metadados[5]} Q3:{metadados[6]} Q4:{metadados[7]} Q5:{metadados[8]}")
            print()
            
        print(f"💡 OBSERVE: Mesmo com somas similares (200-208),")
        print(f"   os outros metadados variam significativamente!")
        print(f"   É por isso que cláusulas muito restritivas excluem combinações.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    calcular_metadados_3489()
    comparar_com_suas_clausulas() 
    demonstrar_variacao_metadados()