#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 VERIFICADOR DO ÚLTIMO CONCURSO - LOTOFÁCIL
============================================
Script para verificar qual é realmente o último concurso 
analisado pela query híbrida neural.
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    from database_config import db_config
    
    print("🔍 VERIFICANDO ÚLTIMO CONCURSO DA BASE LOTOFÁCIL")
    print("=" * 50)
    
    if not db_config.test_connection():
        print("❌ Erro na conexão com banco")
        exit(1)
    
    # Verificar último concurso
    query_ultimo = "SELECT MAX(Concurso) FROM Resultados_INT"
    resultado = db_config.execute_query(query_ultimo)
    
    if resultado:
        ultimo_concurso = resultado[0][0]
        print(f"🎯 ÚLTIMO CONCURSO NA BASE: {ultimo_concurso}")
        
        # Verificar total de concursos
        query_total = "SELECT COUNT_BIG(*) FROM Resultados_INT"
        resultado_total = db_config.execute_query(query_total)
        total_concursos = resultado_total[0][0] if resultado_total else 0
        print(f"📊 TOTAL DE CONCURSOS: {total_concursos}")
        
        # Verificar se concurso 3489 existe
        query_3489 = "SELECT COUNT_BIG(*) FROM Resultados_INT WHERE Concurso = 3489"
        resultado_3489 = db_config.execute_query(query_3489)
        existe_3489 = resultado_3489[0][0] > 0 if resultado_3489 else False
        print(f"❓ CONCURSO 3489 EXISTE: {'SIM' if existe_3489 else 'NÃO'}")
        
        # Verificar se concurso 3488 existe
        query_3488 = "SELECT COUNT_BIG(*) FROM Resultados_INT WHERE Concurso = 3488"
        resultado_3488 = db_config.execute_query(query_3488)
        existe_3488 = resultado_3488[0][0] > 0 if resultado_3488 else False
        print(f"❓ CONCURSO 3488 EXISTE: {'SIM' if existe_3488 else 'NÃO'}")
        
        print("\n" + "="*50)
        print("📋 RESUMO DA SITUAÇÃO:")
        print(f"   • Base analisou até concurso: {ultimo_concurso}")
        print(f"   • Query diz 'Gerada em: 3488'")
        print(f"   • Arquivo salvo como: concurso_3489.sql")
        
        if ultimo_concurso == 3488:
            print("✅ CORRETO: Query analisou até 3488, prediz 3489")
        elif ultimo_concurso < 3488:
            print(f"⚠️  ATENÇÃO: Base só tem até {ultimo_concurso}, mas query fala em 3488")
        else:
            print(f"� ATUALIZADO: Base tem até {ultimo_concurso}, query pode estar desatualizada")
            
        # Verificar últimos 5 concursos
        print(f"\n📊 ÚLTIMOS 5 CONCURSOS NA BASE:")
        query_ultimos = """
        SELECT TOP 5 Concurso, Data_Sorteio 
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        resultado_ultimos = db_config.execute_query(query_ultimos)
        if resultado_ultimos:
            for row in resultado_ultimos:
                print(f"   Concurso {row[0]}: {row[1]}")
            
    else:
        print("❌ Erro ao consultar último concurso")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
