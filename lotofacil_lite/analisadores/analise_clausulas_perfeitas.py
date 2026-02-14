#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANÁLISE DE CLAUSULAS PERFEITAS - CONCURSO 3489
=================================================
Teste: Se ajustarmos todas as cláusulas para os valores EXATOS do concurso 3489,
quantas combinações seriam geradas e qual seria a probabilidade de acerto?

Valores reais do concurso 3489:
QtdePrimos=4, QtdeFibonacci=4, QtdeImpares=8, SomaTotal=204,
Quintil1=2, Quintil2=4, Quintil3=3, Quintil4=3, Quintil5=3,
QtdeGaps=6, QtdeRepetidos=9, SEQ=8, DistanciaExtremos=24,
ParesSequencia=4, QtdeMultiplos3=6, ParesSaltados=1,
Faixa_Baixa=4, Faixa_Media=6, Faixa_Alta=5, RepetidosMesmaPosicao=1

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


def analisar_clausulas_perfeitas():
    """Analisa o que acontece com cláusulas ajustadas aos valores exatos"""
    
    print("🔍 ANÁLISE DE CLÁUSULAS PERFEITAS - CONCURSO 3489")
    print("="*60)
    print("❓ PERGUNTA: Se ajustarmos TODAS as cláusulas para os valores")
    print("   EXATOS do concurso 3489, quantas combinações encontraríamos?")
    print("="*60)
    
    # Conectar ao banco
    db_config = DatabaseConfig()
    
    # Valores EXATOS do concurso 3489
    valores_reais = {
        'QtdePrimos': 4,
        'QtdeFibonacci': 4, 
        'QtdeImpares': 8,
        'SomaTotal': 204,
        'Quintil1': 2,
        'Quintil2': 4,
        'Quintil3': 3,
        'Quintil4': 3,
        'Quintil5': 3,
        'QtdeGaps': 6,
        'QtdeRepetidos': 9,
        'SEQ': 8,
        'DistanciaExtremos': 24,
        'ParesSequencia': 4,
        'QtdeMultiplos3': 6,
        'ParesSaltados': 1,
        'Faixa_Baixa': 4,
        'Faixa_Media': 6,
        'Faixa_Alta': 5,
        'RepetidosMesmaPosicao': 1
    }
    
    print("📊 VALORES REAIS DO CONCURSO 3489:")
    for campo, valor in valores_reais.items():
        print(f"   • {campo}: {valor}")
    
    # Teste 1: Cláusulas EXATAS (valores únicos)
    print(f"\n🎯 TESTE 1: CLÁUSULAS EXATAS (valores únicos)")
    query_exata = "SELECT * FROM Resultados_INT WHERE "
    condicoes_exatas = []
    for campo, valor in valores_reais.items():
        condicoes_exatas.append(f"{campo} = {valor}")
    
    query_exata += " AND ".join(condicoes_exatas)
    
    print(f"Query: {query_exata}")
    
    try:
        resultados_exatos = db_config.execute_query(query_exata)
        print(f"✅ Resultado: {len(resultados_exatos)} concursos históricos")
        
        if len(resultados_exatos) > 0:
            print(f"📋 Concursos encontrados:")
            for resultado in resultados_exatos:
                print(f"   • Concurso {resultado[0]}")
        else:
            print(f"❌ NENHUM concurso histórico atende a TODOS os critérios exatos!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Cláusulas com MARGEM (±1)
    print(f"\n🎯 TESTE 2: CLÁUSULAS COM MARGEM (±1)")
    query_margem = "SELECT * FROM Resultados_INT WHERE "
    condicoes_margem = []
    for campo, valor in valores_reais.items():
        if campo == 'SEQ':  # SEQ pode ser decimal
            condicoes_margem.append(f"{campo} BETWEEN {valor-1} AND {valor+1}")
        else:
            margem_baixa = max(0, valor - 1)
            margem_alta = valor + 1
            condicoes_margem.append(f"{campo} BETWEEN {margem_baixa} AND {margem_alta}")
    
    query_margem += " AND ".join(condicoes_margem)
    
    print(f"Query com margem: (primeiros 200 caracteres)")
    print(f"{query_margem[:200]}...")
    
    try:
        resultados_margem = db_config.execute_query(query_margem)
        print(f"✅ Resultado: {len(resultados_margem)} concursos históricos")
        
        if len(resultados_margem) > 0:
            print(f"📋 Primeiros 5 concursos encontrados:")
            for i, resultado in enumerate(resultados_margem[:5], 1):
                print(f"   {i}. Concurso {resultado[0]}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Sua query ajustada
    print(f"\n🎯 TESTE 3: SUA QUERY AJUSTADA")
    sua_query = """SELECT * FROM Resultados_INT 
WHERE QtdePrimos BETWEEN 4 AND 5 
AND QtdeFibonacci BETWEEN 3 AND 5
AND QtdeImpares BETWEEN 7 AND 9
AND SomaTotal BETWEEN 184 AND 218 
AND Quintil1 BETWEEN 2 AND 4 AND Quintil2 BETWEEN 2 AND 4 AND Quintil3 BETWEEN 2 AND 3 
AND Quintil4 BETWEEN 2 AND 3 AND Quintil5 BETWEEN 3 AND 5 AND 
QtdeGaps BETWEEN 5 AND 6 AND QtdeRepetidos BETWEEN 8 AND 9 AND
SEQ BETWEEN 7 AND 8 AND DistanciaExtremos BETWEEN 22 AND 24 
AND ParesSequencia BETWEEN 3 AND 4 AND QtdeMultiplos3 BETWEEN 3 AND 6
AND ParesSaltados BETWEEN 0 AND 1 AND Faixa_Baixa BETWEEN 4 AND 6 
AND Faixa_Media BETWEEN 4 AND 6 AND Faixa_Alta BETWEEN 2 AND 5
AND RepetidosMesmaPosicao BETWEEN 1 AND 4"""
    
    try:
        resultados_sua = db_config.execute_query(sua_query)
        print(f"✅ Resultado: {len(resultados_sua)} concursos históricos")
        
        if len(resultados_sua) > 0:
            print(f"📋 Primeiros 10 concursos encontrados:")
            for i, resultado in enumerate(resultados_sua[:10], 1):
                print(f"   {i}. Concurso {resultado[0]}")
                
            # Verificar se 3489 está na lista
            concursos_encontrados = [r[0] for r in resultados_sua]
            if 3489 in concursos_encontrados:
                print(f"✅ CONCURSO 3489 ESTÁ NA LISTA!")
            else:
                print(f"❌ Concurso 3489 NÃO está na lista")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print(f"\n" + "="*60)
    print("💡 CONCLUSÕES IMPORTANTES:")
    print("="*60)
    print("1. 🎯 METADADOS NÃO GARANTEM OS NÚMEROS:")
    print("   • Mesmo com metadados perfeitos, pode haver centenas")
    print("     de combinações diferentes que atendem aos critérios")
    print("")
    print("2. 🔢 METADADOS ≠ NÚMEROS EXATOS:")
    print("   • Metadados filtram o 'TIPO' de combinação")
    print("   • Mas não determinam os números específicos")
    print("")
    print("3. 🎲 PROBABILIDADE AINDA EXISTE:")
    print("   • Se encontrar 100 combinações que atendem aos metadados")
    print("   • Ainda é 1/100 chance de acertar a combinação exata")
    print("")
    print("4. ✅ VALOR DOS METADADOS:")
    print("   • Reduzem drasticamente o espaço de busca")
    print("   • De 3.268.760 para algumas centenas/milhares")
    print("   • Aumentam significativamente as chances")
    print("="*60)

if __name__ == "__main__":
    analisar_clausulas_perfeitas()