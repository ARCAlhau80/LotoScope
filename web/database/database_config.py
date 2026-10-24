#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔗 DATABASE CONFIG - LOTOFÁCIL LITE
Configuração centralizada do banco de dados baseada na classe funcional
Autor: AR CALHAU
Data: 04 de Agosto de 2025
"""

import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import pandas as pd
import time
from typing import Optional, Dict, List, Any, Tuple

class DatabaseConfig:
    """Configuração centralizada do banco de dados"""
    
    def __init__(self, server: str = "VADER", 
                 database: str = "LOTOFACIL", 
                 driver: str = "ODBC Driver 17 for SQL Server"):
        """
        Inicializa configuração de conexão baseada na classe funcional
        
        Args:
            server: Nome do servidor SQL Server
            database: Nome do banco de dados
            driver: Driver ODBC a ser usado
        """
        self.server = server
        self.database = database
        self.driver = driver
        
        # String de conexão testada e funcional
        self.connection_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            "Trusted_Connection=yes;"
        )
        
        # Configurações de retry
        self.max_retries = 3
        self.retry_delay = 2
        self._conexao_ok = None
        
    def get_connection(self) -> Optional[pyodbc.Connection]:
        """
        Obtém uma conexão com o banco de dados com retry automático
        
        Returns:
            pyodbc.Connection: Conexão ativa ou None se falhar
        """
        for attempt in range(self.max_retries):
            try:
                # Conexão otimizada para performance
                if _db_optimizer:
                    conn = _db_optimizer.create_optimized_connection()
                else:
                    conn = pyodbc.connect(self.connection_string)
                if attempt == 0:  # Só mostra na primeira tentativa bem-sucedida
                    print(f"✅ Conexão estabelecida - {self.server} / {self.database}")
                return conn
                
            except pyodbc.Error as e:
                print(f"❌ Erro na conexão (tentativa {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    print(f"🔄 Tentando novamente em {self.retry_delay} segundos...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ Falha ao conectar após todas as tentativas")
                    self._conexao_ok = False
                    return None
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados
        
        Returns:
            bool: True se conexão bem-sucedida
        """
        print("🔍 Testando conexão com o banco de dados...")
        
        try:
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            self._conexao_ok = True
            print(f"✅ Conexão SQL Server OK - {self.server} / {self.database}")
            return True
        except Exception as e:
            self._conexao_ok = False
            print(f"❌ Erro na conexão SQL Server: {e}")
            return False
    
    def execute_query(self, query: str, params: Tuple = None) -> Optional[List[List]]:
        """
        Executa uma query SELECT e retorna os resultados como lista
        
        Args:
            query (str): Query SQL
            params (tuple): Parâmetros para a query
            
        Returns:
            list: Resultados da query ou None se erro
        """
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return [list(row) for row in results]
            
        except Exception as e:
            print(f"❌ Erro ao executar query: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def execute_query_dataframe(self, query: str, params: Optional[Tuple] = None) -> Optional[pd.DataFrame]:
        """
        Executa uma query SELECT e retorna DataFrame (para compatibilidade)
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros para a query
            
        Returns:
            DataFrame com os resultados ou None se erro
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            if params:
                df = pd.read_sql(query, conn, params=params)
            else:
                df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print(f"❌ Erro ao executar query: {e}")
            return None
        finally:
            conn.close()
    
    def execute_command(self, command: str, params: Tuple = None) -> bool:
        """
        Executa um comando SQL (INSERT, UPDATE, DELETE)
        
        Args:
            command (str): Comando SQL
            params (tuple): Parâmetros para o comando
            
        Returns:
            bool: True se executado com sucesso
        """
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(command, params)
            else:
                cursor.execute(command)
            
            conn.commit()
            print(f"✅ Comando executado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao executar comando: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def verificar_tabela_existe(self, nome_tabela: str) -> bool:
        """
        Verifica se uma tabela existe no banco
        
        Args:
            nome_tabela: Nome da tabela
            
        Returns:
            bool: True se existe, False caso contrário
        """
        query = """
        SELECT COUNT_BIG(*) as count FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
        """
        
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, (nome_tabela,))
            existe = cursor.fetchone()[0] > 0
            return existe
        except Exception as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def contar_registros(self, nome_tabela: str, condicao: str = "") -> int:
        """
        Conta registros em uma tabela
        
        Args:
            nome_tabela: Nome da tabela
            condicao: Condição WHERE opcional
            
        Returns:
            int: Número de registros (0 se erro)
        """
        query = f"SELECT COUNT_BIG(*) FROM {nome_tabela}"
        if condicao:
            query += f" WHERE {condicao}"
        
        conn = self.get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"❌ Erro ao contar registros: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
    
    def inserir_lote(self, tabela: str, dados: List[Tuple], colunas: Optional[List[str]] = None) -> bool:
        """
        Insere múltiplos registros em lote
        
        Args:
            tabela: Nome da tabela
            dados: Lista de tuplas com os dados
            colunas: Lista com nomes das colunas (opcional)
            
        Returns:
            bool: True se inseriu com sucesso
        """
        if not dados:
            return True
        
        # Construir SQL de inserção
        if colunas:
            cols_str = f"({', '.join(colunas)})"
            placeholders = f"({', '.join(['?' for _ in colunas])})"
        else:
            cols_str = ""
            placeholders = f"({', '.join(['?' for _ in dados[0]])})"
        
        sql = f"INSERT INTO {tabela} {cols_str} VALUES {placeholders}"
        
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.executemany(sql, dados)
            conn.commit()
            print(f"✅ {len(dados)} registros inseridos em {tabela}")
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir lote: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @property
    def conexao_ok(self) -> Optional[bool]:
        """
        Retorna status da última tentativa de conexão
        
        Returns:
            bool: True/False se testado, None se nunca testado
        """
        return self._conexao_ok
    
    def get_info_conexao(self) -> Dict[str, Any]:
        """
        Retorna informações sobre a configuração de conexão
        
        Returns:
            dict: Informações da conexão
        """
        return {
            'server': self.server,
            'database': self.database,
            'driver': self.driver,
            'conexao_ok': self._conexao_ok,
            'connection_string': self.connection_string
        }

# Instância global para uso em todo o sistema
db_config = DatabaseConfig()

def testar_conexao_sistema():
    """Função para testar a conexão do sistema Lotofácil"""
    print("� TESTANDO CONEXÃO SQL SERVER - LOTOFÁCIL LITE")
    print("=" * 60)
    
    # Testar conexão
    if db_config.test_connection():
        print(f"📊 Servidor: {db_config.server}")
        print(f"🗄️ Database: {db_config.database}")
        
        # Verificar tabelas principais baseadas na arquitetura técnica
        tabelas_principais = [
            ('Combin_Quinze', '3,268,760 registros - Todas as combinações de 15 números'),
            ('Combin_Quinas', '33,649 registros - Todas as combinações de 5 números'),
            ('Combin_Duplas', '300 registros - Todas as combinações de 2 números'),
            ('Combin_Ternos', '2,300 registros - Todas as combinações de 3 números'),
            ('NumerosCiclos', 'Análise de ciclos por número (1-25)'),
            ('Resultados_INT', 'Histórico oficial dos sorteios')
        ]
        
        print(f"\n📋 VERIFICANDO TABELAS PRINCIPAIS:")
        tabelas_encontradas = 0
        
        for tabela, descricao in tabelas_principais:
            if db_config.verificar_tabela_existe(tabela):
                count = db_config.contar_registros(tabela)
                print(f"✅ {tabela}: {count:,} registros")
                tabelas_encontradas += 1
            else:
                print(f"⚠️ {tabela}: Não encontrada")
        
        # Verifica tabela de resultados oficial
        if db_config.verificar_tabela_existe('Resultados_INT'):
            count = db_config.contar_registros('Resultados_INT')
            print(f"✅ Resultados_INT (Oficial): {count:,} registros")
            
            # Se tem dados, mostra range de concursos
            if count > 0:
                resultado = db_config.execute_query("SELECT MIN(Concurso), MAX(Concurso) FROM Resultados_INT")
                if resultado and resultado[0][0]:
                    min_conc, max_conc = resultado[0]
                    print(f"   📈 Range: Concurso {min_conc} até {max_conc}")
        
        # Verifica procedures importantes
        print(f"\n🔧 VERIFICANDO PROCEDURES:")
        procedures = ['AtualizaNumerosCiclos', 'CalculaCamposApoio', 'AtualizaCombinacoes']
        
        for proc in procedures:
            query = """
            SELECT COUNT_BIG(*) FROM INFORMATION_SCHEMA.ROUTINES 
            WHERE ROUTINE_TYPE = 'PROCEDURE' AND ROUTINE_NAME = ?
            """
            resultado = db_config.execute_query(query, (proc,))
            if resultado and resultado[0][0] > 0:
                print(f"✅ {proc}: Disponível")
            else:
                print(f"⚠️ {proc}: Não encontrada")
        
        print(f"\n📊 RESUMO:")
        print(f"   • Tabelas principais encontradas: {tabelas_encontradas}/{len(tabelas_principais)}")
        
        if tabelas_encontradas >= 4:
            print(f"   🎯 Sistema compatível com arquitetura completa!")
        elif db_config.verificar_tabela_existe('Resultados_INT'):
            print(f"   💡 Sistema funcional (usando Resultados_INT)")
        else:
            print(f"   ⚠️ Execute setup_banco.py para criar estrutura básica")
    
    else:
        print("❌ Falha na conexão com SQL Server")
        print("💡 Dicas para resolver:")
        print(f"   • Verifique se o SQL Server está rodando em {db_config.server}")
        print(f"   • Confirme se o banco LOTOFACIL existe")
        print("   • Teste a autenticação Windows")
        print("   • Verifique se o serviço SQL Server está ativo")
    
    return db_config.conexao_ok

if __name__ == "__main__":
    # Teste da configuração
    print("🔗 TESTE DA CONFIGURAÇÃO DO BANCO DE DADOS")
    print("=" * 50)
    
    if testar_conexao_sistema():
        print("\n🎯 Sistema pronto para uso!")
        print("💡 Execute 'python main.py' para usar o sistema completo")
    else:
        print("\n⚠️ Configure a conexão antes de usar o sistema")
        print("📝 Ajuste os parâmetros no início do arquivo se necessário")
