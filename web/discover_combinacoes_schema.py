#!/usr/bin/env python3
"""
Descobrir esquema da tabela COMBINACOES_LOTOFACIL20_COMPLETO
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lotofacil_lite'))

from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


def discover_combinacoes_schema():
    """Descobrir esquema da tabela COMBINACOES_LOTOFACIL20_COMPLETO"""
    print("🔍 DESCOBRINDO ESQUEMA DA TABELA COMBINACOES_LOTOFACIL20_COMPLETO...")
    
    try:
        # Conectar ao banco
        config = DatabaseConfig()
        conn = config.get_connection()
        cursor = conn.cursor()
        
        # Descobrir colunas
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        print(f"\n✅ ESQUEMA DA TABELA COMBINACOES_LOTOFACIL20_COMPLETO:")
        print(f"📊 Total de colunas: {len(columns)}")
        print("\n" + "="*80)
        print(f"{'COLUNA':<30} {'TIPO':<15} {'NULO':<8} {'PADRÃO':<15}")
        print("="*80)
        
        for col in columns:
            col_name = col[0] or ""
            data_type = col[1] or ""
            nullable = col[2] or ""
            default = str(col[3]) if col[3] else ""
            print(f"{col_name:<30} {data_type:<15} {nullable:<8} {default:<15}")
        
        # Testar uma query simples
        print(f"\n🧪 TESTANDO QUERY SIMPLES...")
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT TOP 1 * FROM COMBINACOES_LOTOFACIL20_COMPLETO")
        row = cursor.fetchone()
        
        if row:
            print(f"✅ Primeira linha encontrada com {len(row)} colunas")
            # Mostrar alguns valores de exemplo
            print("\n📋 VALORES DE EXEMPLO:")
            col_names = [desc[0] for desc in cursor.description]
            for i, (name, value) in enumerate(zip(col_names[:10], row[:10])):
                print(f"  {name}: {value}")
            if len(col_names) > 10:
                print(f"  ... e mais {len(col_names) - 10} colunas")
        
        # Contar total de registros
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL20_COMPLETO")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE COMBINAÇÕES: {total:,}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    discover_combinacoes_schema()