#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 VERIFICADOR DE FAIXAS - TABELA RESULTADOS_INT
===============================================
Script para verificar como são definidas as faixas
Baixa, Média e Alta na tabela Resultados_INT.
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


def verificar_definicao_faixas():
    """Verifica como são calculadas as faixas na tabela"""
    print("🔍 VERIFICANDO DEFINIÇÃO DAS FAIXAS")
    print("="*50)
    
    try:
        if not db_config.test_connection():
            print("❌ Erro na conexão com banco")
            return
        
        # Buscar alguns exemplos de sorteios com suas faixas
        query = """
        SELECT TOP 10 
            Concurso, 
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
            Faixa_Baixa, Faixa_Media, Faixa_Alta
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        
        resultados = db_config.execute_query(query)
        
        if resultados:
            print("📊 ÚLTIMOS 10 CONCURSOS - ANÁLISE DAS FAIXAS:")
            print("-"*80)
            print(f"{'Concurso':<8} {'Números Sorteados':<45} {'B':>2} {'M':>2} {'A':>2}")
            print("-"*80)
            
            for row in resultados:
                concurso = row[0]
                numeros = [row[i] for i in range(1, 16)]  # N1 a N15
                faixa_baixa = row[16]
                faixa_media = row[17] 
                faixa_alta = row[18]
                
                numeros_str = str(numeros).replace('[', '').replace(']', '')
                print(f"{concurso:<8} {numeros_str:<45} {faixa_baixa:>2} {faixa_media:>2} {faixa_alta:>2}")
                
                # Verificar a lógica manualmente para o primeiro caso
                if concurso == resultados[0][0]:  # Primeiro (mais recente)
                    print(f"\n🔍 ANÁLISE DETALHADA DO CONCURSO {concurso}:")
                    
                    # Contar manualmente as faixas
                    baixos = sum(1 for n in numeros if 1 <= n <= 8)
                    medios = sum(1 for n in numeros if 9 <= n <= 17) 
                    altos = sum(1 for n in numeros if 18 <= n <= 25)
                    
                    print(f"   📍 Números baixos (1-8):    {[n for n in numeros if 1 <= n <= 8]} = {baixos}")
                    print(f"   📍 Números médios (9-17):   {[n for n in numeros if 9 <= n <= 17]} = {medios}")
                    print(f"   📍 Números altos (18-25):   {[n for n in numeros if 18 <= n <= 25]} = {altos}")
                    
                    print(f"\n   🎯 COMPARAÇÃO:")
                    print(f"   📊 Tabela: Baixa={faixa_baixa}, Média={faixa_media}, Alta={faixa_alta}")
                    print(f"   🧮 Cálculo: Baixa={baixos}, Média={medios}, Alta={altos}")
                    
                    if baixos == faixa_baixa and medios == faixa_media and altos == faixa_alta:
                        print("   ✅ CONFIRMADO: Faixas calculadas corretamente!")
                    else:
                        print("   ❌ DIVERGÊNCIA: Cálculo não confere!")
            
            print("\n" + "="*50)
            print("📋 DEFINIÇÃO DAS FAIXAS:")
            print("   🔵 FAIXA BAIXA:  números de 1 a 8")
            print("   🟡 FAIXA MÉDIA:  números de 9 a 17") 
            print("   🔴 FAIXA ALTA:   números de 18 a 25")
            print("\n   📊 Cada faixa conta quantos números da combinação")
            print("      estão dentro daquela faixa específica.")
            
        else:
            print("❌ Nenhum resultado encontrado")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_definicao_faixas()