#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 INVESTIGAÇÃO: POR QUE CONCURSO 3489 NÃO APARECE?
==================================================
Se o concurso 3489 tem metadados específicos, uma query com esses
mesmos metadados deveria incluí-lo. Vamos descobrir o que está acontecendo.

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


def investigar_exclusao_3489():
    """Investiga por que o concurso 3489 não aparece nas queries"""
    
    print("🔍 INVESTIGAÇÃO: POR QUE CONCURSO 3489 NÃO APARECE?")
    print("="*60)
    
    db_config = DatabaseConfig()
    
    # 1. Primeiro, vamos pegar os metadados EXATOS do concurso 3489
    print("📊 PASSO 1: METADADOS REAIS DO CONCURSO 3489")
    print("-"*40)
    
    query_3489 = "SELECT * FROM Resultados_INT WHERE Concurso = 3489"
    
    try:
        resultado_3489 = db_config.execute_query(query_3489)
        if len(resultado_3489) > 0:
            dados = resultado_3489[0]
            metadados_reais = {
                'Concurso': dados[0],
                'QtdePrimos': dados[17],
                'QtdeFibonacci': dados[18], 
                'QtdeImpares': dados[19],
                'SomaTotal': dados[20],
                'Quintil1': dados[21],
                'Quintil2': dados[22],
                'Quintil3': dados[23],
                'Quintil4': dados[24],
                'Quintil5': dados[25],
                'QtdeGaps': dados[26],
                'QtdeRepetidos': dados[27],
                'SEQ': dados[28],
                'DistanciaExtremos': dados[29],
                'ParesSequencia': dados[30],
                'QtdeMultiplos3': dados[31],
                'ParesSaltados': dados[32],
                'Faixa_Baixa': dados[33],
                'Faixa_Media': dados[34],
                'Faixa_Alta': dados[35],
                'RepetidosMesmaPosicao': dados[36]
            }
            
            print("✅ Metadados REAIS do concurso 3489:")
            for campo, valor in metadados_reais.items():
                print(f"   • {campo}: {valor}")
                
        else:
            print("❌ Concurso 3489 não encontrado!")
            return
            
    except Exception as e:
        print(f"❌ Erro ao buscar concurso 3489: {e}")
        return
    
    # 2. Agora vamos testar cada condição da sua query
    print(f"\n🔍 PASSO 2: TESTANDO CADA CONDIÇÃO DA SUA QUERY")
    print("-"*40)
    
    suas_condicoes = [
        ("QtdePrimos BETWEEN 4 AND 5", metadados_reais['QtdePrimos'], "4-5"),
        ("QtdeFibonacci BETWEEN 3 AND 5", metadados_reais['QtdeFibonacci'], "3-5"),
        ("QtdeImpares BETWEEN 7 AND 9", metadados_reais['QtdeImpares'], "7-9"),
        ("SomaTotal BETWEEN 184 AND 218", metadados_reais['SomaTotal'], "184-218"),
        ("Quintil1 BETWEEN 2 AND 4", metadados_reais['Quintil1'], "2-4"),
        ("Quintil2 BETWEEN 2 AND 4", metadados_reais['Quintil2'], "2-4"),
        ("Quintil3 BETWEEN 2 AND 3", metadados_reais['Quintil3'], "2-3"),
        ("Quintil4 BETWEEN 2 AND 3", metadados_reais['Quintil4'], "2-3"),
        ("Quintil5 BETWEEN 3 AND 5", metadados_reais['Quintil5'], "3-5"),
        ("QtdeGaps BETWEEN 5 AND 6", metadados_reais['QtdeGaps'], "5-6"),
        ("QtdeRepetidos BETWEEN 8 AND 9", metadados_reais['QtdeRepetidos'], "8-9"),
        ("SEQ BETWEEN 7 AND 8", metadados_reais['SEQ'], "7-8"),
        ("DistanciaExtremos BETWEEN 22 AND 24", metadados_reais['DistanciaExtremos'], "22-24"),
        ("ParesSequencia BETWEEN 3 AND 4", metadados_reais['ParesSequencia'], "3-4"),
        ("QtdeMultiplos3 BETWEEN 3 AND 6", metadados_reais['QtdeMultiplos3'], "3-6"),
        ("ParesSaltados BETWEEN 0 AND 1", metadados_reais['ParesSaltados'], "0-1"),
        ("Faixa_Baixa BETWEEN 4 AND 6", metadados_reais['Faixa_Baixa'], "4-6"),
        ("Faixa_Media BETWEEN 4 AND 6", metadados_reais['Faixa_Media'], "4-6"),
        ("Faixa_Alta BETWEEN 2 AND 5", metadados_reais['Faixa_Alta'], "2-5"),
        ("RepetidosMesmaPosicao BETWEEN 1 AND 4", metadados_reais['RepetidosMesmaPosicao'], "1-4")
    ]
    
    condicoes_falharam = []
    
    for condicao, valor_real, faixa in suas_condicoes:
        # Extrair campo e faixa
        campo = condicao.split(' BETWEEN')[0]
        faixa_split = faixa.split('-')
        min_val = int(faixa_split[0])
        max_val = int(faixa_split[1])
        
        if min_val <= valor_real <= max_val:
            status = "✅ PASSA"
        else:
            status = "❌ FALHA"
            condicoes_falharam.append((campo, valor_real, faixa))
            
        print(f"   {status} | {campo}: {valor_real} (faixa: {faixa})")
    
    # 3. Mostrar condições que falharam
    if condicoes_falharam:
        print(f"\n❌ CONDIÇÕES QUE FALHARAM:")
        print("-"*40)
        for campo, valor, faixa in condicoes_falharam:
            print(f"   • {campo}: valor {valor} NÃO está na faixa {faixa}")
            
        print(f"\n💡 ESTA É A RAZÃO! O concurso 3489 não atende a TODAS as condições.")
        print(f"   Para incluí-lo, você precisa ajustar as faixas das condições que falharam.")
            
    else:
        print(f"\n✅ TODAS AS CONDIÇÕES PASSARAM!")
        print(f"   O concurso 3489 DEVERIA aparecer na query.")
        print(f"   Vamos investigar mais...")
        
        # Teste direto da query completa
        print(f"\n🔍 PASSO 3: TESTE DIRETO DA QUERY COMPLETA")
        print("-"*40)
        
        sua_query_completa = """SELECT Concurso FROM Resultados_INT 
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
        
        try:
            resultados = db_config.execute_query(sua_query_completa)
            concursos_encontrados = [r[0] for r in resultados]
            
            print(f"Concursos encontrados: {concursos_encontrados}")
            
            if 3489 in concursos_encontrados:
                print(f"✅ Concurso 3489 ESTÁ na lista!")
            else:
                print(f"❌ Concurso 3489 NÃO está na lista")
                print(f"   Isso indica erro nos dados ou na query.")
                
        except Exception as e:
            print(f"❌ Erro na query: {e}")
    
    # 4. Sugestão de query corrigida
    print(f"\n🔧 PASSO 4: QUERY CORRIGIDA PARA INCLUIR 3489")
    print("-"*40)
    
    # Criar faixas baseadas nos valores reais +/- margem
    query_corrigida_condicoes = []
    for campo, valor_real, _ in suas_condicoes:
        campo_nome = campo.split(' BETWEEN')[0]
        if campo_nome == 'SEQ':  # SEQ pode ser decimal
            margem = 1
        else:
            margem = 1
            
        min_corrigido = max(0, valor_real - margem)
        max_corrigido = valor_real + margem
        
        query_corrigida_condicoes.append(f"{campo_nome} BETWEEN {min_corrigido} AND {max_corrigido}")
    
    query_corrigida = "SELECT COUNT_BIG(*) FROM Resultados_INT WHERE " + " AND ".join(query_corrigida_condicoes)
    
    print(f"Query corrigida (com margens ±1):")
    print(f"{query_corrigida[:200]}...")
    
    try:
        resultado_corrigido = db_config.execute_query(query_corrigida)
        total_corrigido = resultado_corrigido[0][0]
        print(f"\n✅ Com query corrigida: {total_corrigido} concursos encontrados")
        
        # Verificar se 3489 está incluído
        query_verificacao = query_corrigida.replace("COUNT(*)", "Concurso")
        resultados_verificacao = db_config.execute_query(query_verificacao)
        concursos_corrigidos = [r[0] for r in resultados_verificacao]
        
        if 3489 in concursos_corrigidos:
            print(f"✅ Concurso 3489 INCLUÍDO na query corrigida!")
        else:
            print(f"❌ Ainda assim não inclui 3489")
            
    except Exception as e:
        print(f"❌ Erro na query corrigida: {e}")

if __name__ == "__main__":
    investigar_exclusao_3489()