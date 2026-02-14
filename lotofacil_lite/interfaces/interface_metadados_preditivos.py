#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 INTERFACE ANALISADOR METADADOS PREDITIVOS - SUPER MENU
=========================================================
Interface otimizada para integração com Super Menu
Foco na geração de cláusula WHERE preditiva para próximo concurso

Autor: AR CALHAU
Data: 18/09/2025
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'analisadores'))

from analisador_metadados_preditivos import AnalisadorMetadadosPreditivos

def executar_analise_preditiva_interface():
    """Interface otimizada para Super Menu"""
    print("🔍 ANALISADOR DE METADADOS PREDITIVOS")
    print("="*60)
    print("🎯 Gera cláusula WHERE preditiva para próximo concurso")
    print("📊 Baseado em análise de padrões de reversão estatística")
    print("="*60)
    
    try:
        # Criar e executar analisador
        analisador = AnalisadorMetadadosPreditivos()
        
        print("🔍 Carregando dados históricos...")
        if not analisador.carregar_dados_metadados():
            return None
        
        print("📊 Analisando situação atual...")
        ultimo_concurso = analisador.analisar_situacao_atual()
        
        print("🧠 Gerando condições preditivas...")
        clausulas, justificativas = analisador.gerar_clausulas_where_preditivas()
        
        if clausulas:
            print("\n" + "="*60)
            print("🔮 QUERY PREDITIVA GERADA")
            print("="*60)
            
            # Query completa
            query_completa = "SELECT * FROM Resultados_INT WHERE " + " AND ".join(clausulas)
            
            print("🔍 CONDIÇÕES PARA O PRÓXIMO CONCURSO:")
            for i, (clausula, justificativa) in enumerate(zip(clausulas, justificativas), 1):
                print(f"   {i:2}. {clausula}")
            
            print(f"\n💡 RESUMO DAS PREDIÇÕES:")
            print(f"   • Total de condições: {len(clausulas)}")
            print(f"   • Baseado no concurso: {ultimo_concurso['concurso']}")
            print(f"   • Princípio: Reversão estatística (75-80% dos campos)")
            
            # Testar a query
            print(f"\n🧪 VALIDAÇÃO DA QUERY:")
            try:
                resultados_teste = analisador.db_config.execute_query(query_completa)
                print(f"   ✅ {len(resultados_teste)} concursos históricos atendem às condições")
                
                if len(resultados_teste) > 0:
                    # Mostrar alguns exemplos
                    print(f"   📋 Exemplos de concursos similares:")
                    for i, resultado in enumerate(resultados_teste[-3:], 1):  # Últimos 3
                        concurso = resultado[0]
                        print(f"      {i}. Concurso {concurso}")
                
            except Exception as e:
                print(f"   ⚠️ Erro no teste: {e}")
            
            print(f"\n🎲 COMO USAR:")
            print(f"   1. Execute a query na base de dados")
            print(f"   2. Analise os números sorteados nos concursos encontrados")
            print(f"   3. Identifique padrões nos números para suas apostas")
            print(f"   4. Use como filtro adicional em seus geradores")
            
            print("\n" + "="*60)
            print("✅ ANÁLISE PREDITIVA CONCLUÍDA!")
            print("="*60)
            
            return {
                'clausulas': clausulas,
                'justificativas': justificativas,
                'query_completa': query_completa,
                'ultimo_concurso': ultimo_concurso['concurso']
            }
        else:
            print("❌ Nenhuma condição preditiva gerada")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    executar_analise_preditiva_interface()