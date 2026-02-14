#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from database_config import db_config

def analisar_estrutura():
    try:
        conn_str = f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={db_config.server};
        DATABASE={db_config.database};
        Trusted_Connection=yes;
        """
        # Conexão otimizada para performance
        if _db_optimizer:
            conn = _db_optimizer.create_optimized_connection()
        else:
            conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("ESTRUTURA DA TABELA COMBINACOES_LOTOFACIL:")
        print("="*60)
        
        # Estrutura
        cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL'
        ORDER BY ORDINAL_POSITION
        """)
        
        colunas = cursor.fetchall()
        
        for col in colunas:
            print(f"{col[0]:25} | {col[1]}")
        
        print(f"\nAMOSTRA DE DADOS:")
        print("="*60)
        
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT TOP 3 * FROM COMBINACOES_LOTOFACIL")
        rows = cursor.fetchall()
        
        # Cabecalho
        column_names = [desc[0] for desc in cursor.description]
        print(" | ".join(name[:8] for name in column_names))
        print("-" * 80)
        
        # Dados
        for row in rows:
            print(" | ".join(f"{str(val)[:8]:8}" for val in row))
        
        # Campos estatisticos
        print(f"\nCAMPOS ESTATISTICOS:")
        print("="*40)
        
        campos_estatisticos = []
        for col in colunas:
            col_name = col[0]
            if col_name not in ['ID', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15', 'DATA_CRIACAO', 'QTDE_NUMEROS']:
                campos_estatisticos.append(col_name)
                print(f"  {col_name}")
        
        conn.close()
        return campos_estatisticos
        
    except Exception as e:
        print(f"Erro: {e}")
        return []

if __name__ == "__main__":
    campos = analisar_estrutura()
    print(f"\nTotal campos estatisticos: {len(campos)}")
