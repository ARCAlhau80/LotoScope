#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 CLÁUSULA CORRIGIDA PARA INCLUIR CONCURSO 3489
===============================================
Ajusta as faixas para incluir o concurso 3489 e testa o resultado.

Autor: AR CALHAU
Data: 18/09/2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


def testar_clausula_corrigida():
    """Testa cláusula corrigida que inclui 3489"""
    
    print("🔧 CLÁUSULA CORRIGIDA PARA INCLUIR CONCURSO 3489")
    print("="*60)
    
    db_config = DatabaseConfig()
    
    # Sua cláusula ORIGINAL (que exclui 3489)
    clausula_original = """SELECT COUNT_BIG(*) FROM COMBINACOES_LOTOFACIL 
WHERE QtdePrimos BETWEEN 4 AND 5 
AND QtdeFibonacci BETWEEN 3 AND 5
AND QtdeImpares BETWEEN 7 AND 9
AND SomaTotal BETWEEN 184 AND 218 
AND Quintil1 BETWEEN 2 AND 4 
AND Quintil2 BETWEEN 2 AND 4 
AND Quintil3 BETWEEN 2 AND 3 
AND Quintil4 BETWEEN 2 AND 3 
AND Quintil5 BETWEEN 3 AND 5 
AND QtdeGaps BETWEEN 5 AND 6 
AND QtdeRepetidos BETWEEN 8 AND 9 
AND SEQ BETWEEN 7 AND 8 
AND DistanciaExtremos BETWEEN 22 AND 24 
AND ParesSequencia BETWEEN 3 AND 4 
AND QtdeMultiplos3 BETWEEN 3 AND 6
AND ParesSaltados BETWEEN 0 AND 1 
AND Faixa_Baixa BETWEEN 4 AND 6 
AND Faixa_Media BETWEEN 4 AND 6 
AND Faixa_Alta BETWEEN 2 AND 5
AND RepetidosMesmaPosicao BETWEEN 1 AND 4"""

    # Cláusula CORRIGIDA (ajustando Faixa_Alta para 2-6)
    clausula_corrigida = """SELECT COUNT_BIG(*) FROM COMBINACOES_LOTOFACIL 
WHERE QtdePrimos BETWEEN 4 AND 5 
AND QtdeFibonacci BETWEEN 3 AND 5
AND QtdeImpares BETWEEN 7 AND 9
AND SomaTotal BETWEEN 184 AND 218 
AND Quintil1 BETWEEN 2 AND 4 
AND Quintil2 BETWEEN 2 AND 4 
AND Quintil3 BETWEEN 2 AND 3 
AND Quintil4 BETWEEN 2 AND 3 
AND Quintil5 BETWEEN 3 AND 5 
AND QtdeGaps BETWEEN 5 AND 6 
AND QtdeRepetidos BETWEEN 8 AND 9 
AND SEQ BETWEEN 7 AND 8 
AND DistanciaExtremos BETWEEN 22 AND 24 
AND ParesSequencia BETWEEN 3 AND 4 
AND QtdeMultiplos3 BETWEEN 3 AND 6
AND ParesSaltados BETWEEN 0 AND 1 
AND Faixa_Baixa BETWEEN 4 AND 6 
AND Faixa_Media BETWEEN 4 AND 6 
AND Faixa_Alta BETWEEN 2 AND 6
AND RepetidosMesmaPosicao BETWEEN 1 AND 4"""

    print("📊 TESTE 1: CLÁUSULA ORIGINAL")
    print("-"*30)
    try:
        resultado_original = db_config.execute_query(clausula_original)
        total_original = resultado_original[0][0]
        print(f"✅ Combinações encontradas: {total_original:,}")
        print(f"🎯 Probabilidade: 1/{total_original:,} = {(1/total_original)*100:.6f}%")
    except Exception as e:
        print(f"❌ Erro: {e}")

    print(f"\n📊 TESTE 2: CLÁUSULA CORRIGIDA (Faixa_Alta 2-5 → 2-6)")
    print("-"*30)
    try:
        resultado_corrigido = db_config.execute_query(clausula_corrigida)
        total_corrigido = resultado_corrigido[0][0]
        print(f"✅ Combinações encontradas: {total_corrigido:,}")
        print(f"🎯 Probabilidade: 1/{total_corrigido:,} = {(1/total_corrigido)*100:.6f}%")
        
        # Comparar
        if total_original > 0:
            aumento = total_corrigido - total_original
            percentual = (aumento / total_original) * 100
            print(f"📈 Aumento: +{aumento:,} combinações (+{percentual:.1f}%)")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

    # Cláusula MAIS FLEXÍVEL (ajustando vários campos)
    clausula_flexivel = """SELECT COUNT_BIG(*) FROM COMBINACOES_LOTOFACIL 
WHERE QtdePrimos BETWEEN 4 AND 5 
AND QtdeFibonacci BETWEEN 3 AND 5
AND QtdeImpares BETWEEN 7 AND 9
AND SomaTotal BETWEEN 180 AND 220 
AND Quintil1 BETWEEN 2 AND 4 
AND Quintil2 BETWEEN 1 AND 4 
AND Quintil3 BETWEEN 1 AND 3 
AND Quintil4 BETWEEN 2 AND 4 
AND Quintil5 BETWEEN 3 AND 6 
AND QtdeGaps BETWEEN 4 AND 7 
AND QtdeRepetidos BETWEEN 7 AND 10 
AND SEQ BETWEEN 6 AND 9 
AND DistanciaExtremos BETWEEN 20 AND 25 
AND ParesSequencia BETWEEN 2 AND 5 
AND QtdeMultiplos3 BETWEEN 2 AND 7
AND ParesSaltados BETWEEN 0 AND 2 
AND Faixa_Baixa BETWEEN 3 AND 7 
AND Faixa_Media BETWEEN 3 AND 7 
AND Faixa_Alta BETWEEN 2 AND 7
AND RepetidosMesmaPosicao BETWEEN 0 AND 5"""

    print(f"\n📊 TESTE 3: CLÁUSULA MAIS FLEXÍVEL")
    print("-"*30)
    try:
        resultado_flexivel = db_config.execute_query(clausula_flexivel)
        total_flexivel = resultado_flexivel[0][0]
        print(f"✅ Combinações encontradas: {total_flexivel:,}")
        print(f"🎯 Probabilidade: 1/{total_flexivel:,} = {(1/total_flexivel)*100:.6f}%")
        
        if total_original > 0:
            melhoria = (1/total_flexivel) / (1/3268760)
            print(f"🚀 Melhoria vs aleatório: {melhoria:.1f}x")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print(f"\n" + "="*60)
    print("💡 CONCLUSÕES:")
    print("="*60)
    print("1. 🎯 PROBLEMA IDENTIFICADO:")
    print("   • Faixa_Alta BETWEEN 2 AND 5 excluía 3489 (que tem 6)")
    print("")
    print("2. 🔧 SOLUÇÃO SIMPLES:")
    print("   • Ajustar para Faixa_Alta BETWEEN 2 AND 6")
    print("   • Isso incluirá o padrão do 3489")
    print("")
    print("3. ⚖️ TRADE-OFF:")
    print("   • Faixas mais restritivas = menos combinações, mais precisão")
    print("   • Faixas mais flexíveis = mais combinações, menos precisão")
    print("")
    print("4. 🎲 RECOMENDAÇÃO:")
    print("   • Use cláusula corrigida para incluir padrões como 3489")
    print("   • Combine com sistema neural para escolha final")
    print("="*60)

if __name__ == "__main__":
    testar_clausula_corrigida()