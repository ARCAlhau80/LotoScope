"""
VERIFICADOR DE ESTRUTURA DO BANCO
==================================
Script para verificar as colunas disponiveis na tabela
"""

import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


def verificar_estrutura_banco():
    """Verifica a estrutura da tabela RESULTADOS_INT"""
    servidor = "DESKTOP-K6JPBDS"
    database = "LOTOFACIL"
    
    # Strings de conexao para tentar
    conn_strings = [
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={servidor};DATABASE={database};Trusted_Connection=yes',
        f'DRIVER={{SQL Server}};SERVER={servidor};DATABASE={database};Trusted_Connection=yes',
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={servidor};DATABASE={database};Integrated Security=SSPI'
    ]
    
    connection = None
    for conn_str in conn_strings:
        try:
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                connection = pyodbc.connect(conn_str)
            print("OK Conectado ao banco")
            break
        except:
            continue
    
    if not connection:
        print("ERRO Nao foi possivel conectar")
        return
    
    try:
        cursor = connection.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        tabelas = cursor.fetchall()
        print(f"\nTabelas encontradas ({len(tabelas)}):")
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        
        # Verificar colunas da tabela RESULTADOS_INT
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'RESULTADOS_INT'
            ORDER BY ORDINAL_POSITION
        """)
        
        colunas = cursor.fetchall()
        print(f"\nColunas da tabela RESULTADOS_INT ({len(colunas)}):")
        for coluna in colunas:
            print(f"  - {coluna[0]} ({coluna[1]})")
        
        # Fazer uma consulta simples para testar
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT TOP 5 * FROM RESULTADOS_INT")
        rows = cursor.fetchall()
        
        print(f"\nPrimeiros 5 registros:")
        for i, row in enumerate(rows):
            print(f"  Registro {i+1}: {len(row)} colunas")
        
        # Contar total de registros
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT COUNT(*) FROM RESULTADOS_INT")
        total = cursor.fetchone()[0]
        print(f"\nTotal de registros: {total}")
        
    except Exception as e:
        print(f"ERRO ao consultar estrutura: {e}")
    
    finally:
        connection.close()

if __name__ == "__main__":
    verificar_estrutura_banco()
    input("\nPressione ENTER para continuar...")
