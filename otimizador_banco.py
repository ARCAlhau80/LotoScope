#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💾 OTIMIZADOR DE BANCO DE DADOS - LOTOSCOPE
==========================================
Sistema específico para otimizar queries SQL e conexões de banco
"""

import os
import re
import time
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from typing import Dict, List, Optional
from datetime import datetime, timedelta

class DatabaseOptimizer:
    """
    Otimizador específico para operações de banco de dados
    """
    
    def __init__(self):
        self.connection_pool = {}
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutos
        
    def create_optimized_connection(self) -> Optional[pyodbc.Connection]:
        """
        🚀 CONEXÃO OTIMIZADA com configurações de performance
        """
        try:
            server = 'VADER'
            database = 'LOTOFACIL'
            
            # String de conexão otimizada para performance
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
                # Configurações de performance
                "Connection Timeout=15;"      # Timeout de conexão reduzido
                "Query Timeout=30;"           # Timeout de query reduzido
                "MARS_Connection=yes;"        # Multiple Active Result Sets
                "APP=LotoScope_Optimized;"    # Nome da aplicação para monitoramento
                "Pooling=yes;"                # Connection pooling
            )
            
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                conn = pyodbc.connect(connection_string)
            
            # Configurações adicionais de performance
            conn.autocommit = True  # Auto-commit para queries de leitura
            
            print("⚡ Conexão otimizada criada")
            return conn
            
        except Exception as e:
            print(f"❌ Erro na conexão otimizada: {e}")
            return None
    
    def optimize_query(self, query: str) -> str:
        """
        🔧 OTIMIZA QUERIES SQL para melhor performance
        """
        # Remove espaços desnecessários
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Adiciona hints de performance quando apropriado
        if query.upper().startswith('SELECT'):
            # Para queries grandes de seleção
            if 'COUNT(*)' in query.upper():
                # Otimização para COUNT
                query = query.replace('SELECT COUNT_BIG(*)', 'SELECT COUNT_BIG(*)')
            
            # Adiciona NOLOCK para queries de leitura (cuidado com consistência)
            if 'WHERE' in query.upper() and 'NOLOCK' not in query.upper():
                # Identifica tabelas e adiciona NOLOCK
                tables = re.findall(r'FROM\s+(\w+)', query, re.IGNORECASE)
                for table in tables:
                    query = query.replace(f'FROM {table}', f'FROM {table} WITH (NOLOCK)')
        
        return query
    
    def cached_query(self, query: str, params: tuple = None) -> List:
        """
        📊 EXECUTA QUERY COM CACHE para evitar execuções repetidas
        """
        # Cria chave do cache
        cache_key = hash(query + str(params) if params else query)
        now = time.time()
        
        # Verifica cache
        if cache_key in self.query_cache:
            result, timestamp = self.query_cache[cache_key]
            if now - timestamp < self.cache_ttl:
                print(f"📊 Query do cache ({len(result)} resultados)")
                return result
        
        # Executa query otimizada
        conn = self.create_optimized_connection()
        if not conn:
            return []
        
        try:
            optimized_query = self.optimize_query(query)
            cursor = conn.cursor()
            
            start_time = time.time()
            if params:
                cursor.execute(optimized_query, params)
            else:
                cursor.execute(optimized_query)
            
            result = cursor.fetchall()
            end_time = time.time()
            
            cursor.close()
            conn.close()
            
            # Armazena no cache
            self.query_cache[cache_key] = (result, now)
            
            execution_time = end_time - start_time
            print(f"⚡ Query executada: {len(result)} resultados em {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro na query cached: {e}")
            conn.close()
            return []
    
    def optimize_database_files(self):
        """
        🔧 OTIMIZA ARQUIVOS QUE FAZEM ACESSO AO BANCO
        """
        print("🔧 Otimizando arquivos de banco de dados...")
        
        # Encontra arquivos que fazem acesso ao banco
        db_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Verifica se o arquivo faz acesso ao banco
                        if ('pyodbc.connect' in content or 
                            'SQL' in content.upper() or
                            'SELECT' in content.upper() or
                            'database' in content.lower()):
                            db_files.append(file_path)
                    except:
                        continue
        
        print(f"📁 Encontrados {len(db_files)} arquivos de banco")
        
        # Otimiza cada arquivo
        for file_path in db_files:
            self._optimize_db_file(file_path)
    
    def _optimize_db_file(self, file_path: str):
        """
        Otimiza um arquivo específico de banco
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Backup
            backup_path = file_path + '.backup_db'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Aplicar otimizações
            optimized_content = self._apply_db_optimizations(content)
            
            # Salva apenas se houve mudanças
            if optimized_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)
                
                print(f"✅ DB otimizado: {os.path.basename(file_path)}")
            else:
                # Remove backup se não houve mudanças
                os.remove(backup_path)
                
        except Exception as e:
            print(f"❌ Erro ao otimizar {file_path}: {e}")
    
    def _apply_db_optimizations(self, content: str) -> str:
        """
        Aplica otimizações específicas de banco
        """
        lines = content.split('\n')
        optimized_lines = []
        added_optimizer = False
        
        for line in lines:
            # Adiciona sistema de otimização após imports
            if (not added_optimizer and 
                ('import pyodbc' in line or 'from database' in line)):
                optimized_lines.append(line)
                optimized_lines.append("")
                optimized_lines.append("# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO")
                optimized_lines.append("try:")
                optimized_lines.append("    from database_optimizer import DatabaseOptimizer")
                optimized_lines.append("    _db_optimizer = DatabaseOptimizer()")
                optimized_lines.append("except ImportError:")
                optimized_lines.append("    _db_optimizer = None")
                optimized_lines.append("")
                added_optimizer = True
                continue
            
            # Otimiza conexões diretas
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                if 'pyodbc.connect(' in line:
                # Substitui por conexão otimizada
                indent = len(line) - len(line.lstrip())
                space = ' ' * indent
                optimized_lines.append(f"{space}# Conexão otimizada para performance")
                optimized_lines.append(f"{space}if _db_optimizer:")
                optimized_lines.append(f"{space}    conn = _db_optimizer.create_optimized_connection()")
                optimized_lines.append(f"{space}else:")
                optimized_lines.append(f"{space}    {line.strip()}")
                continue
            
            # Otimiza execução de queries
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            if ('.execute(' in line and 'SELECT' in line.upper()):
                # Sugere uso de cached_query
                optimized_lines.append(f"        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance")
                optimized_lines.append(line)
                continue
            
            # Otimiza queries grandes
            if 'SELECT COUNT_BIG(*)' in line:
                line = line.replace('SELECT COUNT_BIG(*)', 'SELECT COUNT_BIG(*)')
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def create_database_optimization_module(self):
        """
        🔧 CRIA MÓDULO DE OTIMIZAÇÃO para ser importado pelos outros arquivos
        """
        module_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ MÓDULO DE OTIMIZAÇÃO DE BANCO - LOTOSCOPE
Módulo para ser importado pelos arquivos que fazem acesso ao banco
"""

import pyodbc
import time
from typing import List, Dict, Any, Optional

class DatabaseOptimizer:
    """Otimizador singleton para operações de banco"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection_pool = {}
            cls._instance.query_cache = {}
            cls._instance.cache_ttl = 300
        return cls._instance
    
    def create_optimized_connection(self) -> Optional[pyodbc.Connection]:
        """Cria conexão otimizada com configurações de performance"""
        try:
            server = 'VADER'
            database = 'LOTOFACIL'
            
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
                "Connection Timeout=15;"
                "Query Timeout=30;"
                "MARS_Connection=yes;"
                "APP=LotoScope_Optimized;"
                "Pooling=yes;"
            )
            
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                conn = pyodbc.connect(connection_string)
            conn.autocommit = True
            return conn
            
        except Exception as e:
            print(f"❌ Erro na conexão otimizada: {e}")
            return None
    
    def cached_query(self, query: str, params: tuple = None) -> List:
        """Executa query com cache"""
        cache_key = hash(query + str(params) if params else query)
        now = time.time()
        
        # Verifica cache
        if cache_key in self.query_cache:
            result, timestamp = self.query_cache[cache_key]
            if now - timestamp < self.cache_ttl:
                return result
        
        # Executa query
        conn = self.create_optimized_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Armazena no cache
            self.query_cache[cache_key] = (result, now)
            return result
            
        except Exception as e:
            print(f"❌ Erro na query cached: {e}")
            if conn:
                conn.close()
            return []

# Instância global
_optimizer = DatabaseOptimizer()

def get_optimized_connection():
    """Helper para obter conexão otimizada"""
    return _optimizer.create_optimized_connection()

def cached_query(query: str, params: tuple = None):
    """Helper para query com cache"""
    return _optimizer.cached_query(query, params)
'''
        
        with open('database_optimizer.py', 'w', encoding='utf-8') as f:
            f.write(module_content)
        
        print("✅ Módulo database_optimizer.py criado!")
    
    def test_optimizations(self):
        """
        🧪 TESTA AS OTIMIZAÇÕES implementadas
        """
        print("🧪 Testando otimizações de banco...")
        
        # Teste 1: Conexão otimizada
        print("\n1️⃣ Testando conexão otimizada...")
        start_time = time.time()
        conn = self.create_optimized_connection()
        connection_time = time.time() - start_time
        
        if conn:
            print(f"✅ Conexão criada em {connection_time:.2f}s")
            conn.close()
        else:
            print("❌ Falha na conexão")
            return
        
        # Teste 2: Query simples
        print("\n2️⃣ Testando query simples...")
        start_time = time.time()
        result = self.cached_query("SELECT COUNT_BIG(*) FROM RESULTADOS_INT")
        query_time = time.time() - start_time
        
        if result:
            print(f"✅ Query executada em {query_time:.2f}s - {len(result)} resultados")
        else:
            print("❌ Falha na query")
        
        # Teste 3: Cache de query
        print("\n3️⃣ Testando cache de query...")
        start_time = time.time()
        result2 = self.cached_query("SELECT COUNT_BIG(*) FROM RESULTADOS_INT")
        cache_time = time.time() - start_time
        
        if result2:
            print(f"✅ Query do cache em {cache_time:.2f}s")
            if cache_time < query_time:
                print(f"🚀 Cache {query_time/cache_time:.1f}x mais rápido!")
        
        print(f"\n📊 RESULTADO DOS TESTES:")
        print(f"   • Conexão: {connection_time:.2f}s")
        print(f"   • Query inicial: {query_time:.2f}s")
        print(f"   • Query cached: {cache_time:.2f}s")
        print(f"   • Melhoria: {query_time/cache_time:.1f}x")

def main():
    """
    Função principal do otimizador de banco
    """
    print("💾 OTIMIZADOR DE BANCO DE DADOS - LOTOSCOPE")
    print("=" * 60)
    
    optimizer = DatabaseOptimizer()
    
    print("1️⃣  🔧 Otimizar arquivos de banco")
    print("2️⃣  ⚡ Criar módulo de otimização")
    print("3️⃣  🧪 Testar otimizações")
    print("4️⃣  🚀 Aplicar todas as otimizações")
    print("0️⃣  🚪 Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == "1":
        optimizer.optimize_database_files()
    elif opcao == "2":
        optimizer.create_database_optimization_module()
    elif opcao == "3":
        optimizer.test_optimizations()
    elif opcao == "4":
        print("🚀 Aplicando todas as otimizações...")
        optimizer.create_database_optimization_module()
        optimizer.optimize_database_files()
        optimizer.test_optimizations()
        print("✅ Todas as otimizações aplicadas!")
    elif opcao == "0":
        print("🚪 Saindo...")
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()