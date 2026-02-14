#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR DE COMBINAÇÕES LOTOFÁCIL 16 NÚMEROS
Sistema que gera todas as 2.042.975 combinações únicas de 16 números (1-25)
e cria tabela com os mesmos campos e cálculos da tabela COMBINACOES_LOTOFACIL

Autor: AR CALHAU
Data: 24 de Agosto de 2025
"""

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

import itertools
from datetime import datetime
from database_config import db_config
from typing import List, Tuple
import time

class GeradorCombinacoes16:
    """Gera todas as combinações de 16 números e popula tabela no banco"""
    
    def __init__(self):
        self.total_combinacoes = 2042975  # C(25,16)
        self.batch_size = 10000  # Processa em lotes para não sobrecarregar
        
    def conectar_base(self) -> pyodbc.Connection:
        """Conecta à base de dados"""
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
                return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return None
    
    def criar_tabela_combinacoes16(self, conn: pyodbc.Connection) -> bool:
        """Cria a tabela COMBINACOES_LOTOFACIL16 com mesma estrutura da original"""
        try:
            cursor = conn.cursor()
            
            # Verifica se a tabela já existe
            cursor.execute("""
            SELECT COUNT_BIG(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'COMBINACOES_LOTOFACIL16'
            """)
            
            if cursor.fetchone()[0] > 0:
                print("⚠️ Tabela COMBINACOES_LOTOFACIL16 já existe!")
                resposta = input("Deseja recriar a tabela? (s/n): ").lower()
                if not resposta.startswith('s'):
                    return False
                    
                print("🗑️ Removendo tabela existente...")
                cursor.execute("DROP TABLE [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16]")
                conn.commit()
            
            # Cria a nova tabela baseada na estrutura da original
            print("🔧 Criando tabela COMBINACOES_LOTOFACIL16...")
            
            create_table_sql = """
            CREATE TABLE [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16] (
                ID bigint IDENTITY(1,1) PRIMARY KEY,
                
                -- Números da combinação (16 números)
                N1 tinyint NOT NULL,
                N2 tinyint NOT NULL,
                N3 tinyint NOT NULL,
                N4 tinyint NOT NULL,
                N5 tinyint NOT NULL,
                N6 tinyint NOT NULL,
                N7 tinyint NOT NULL,
                N8 tinyint NOT NULL,
                N9 tinyint NOT NULL,
                N10 tinyint NOT NULL,
                N11 tinyint NOT NULL,
                N12 tinyint NOT NULL,
                N13 tinyint NOT NULL,
                N14 tinyint NOT NULL,
                N15 tinyint NOT NULL,
                N16 tinyint NOT NULL,
                
                -- Soma dos números
                SOMA int NOT NULL,
                
                -- Análise de paridade
                PARES tinyint NOT NULL,
                IMPARES tinyint NOT NULL,
                
                -- Análise por faixas
                FAIXA_01_05 tinyint NOT NULL,
                FAIXA_06_10 tinyint NOT NULL,
                FAIXA_11_15 tinyint NOT NULL,
                FAIXA_16_20 tinyint NOT NULL,
                FAIXA_21_25 tinyint NOT NULL,
                
                -- Análise de sequências
                SEQ_MAX tinyint NOT NULL,
                
                -- Análise de números primos
                PRIMOS tinyint NOT NULL,
                
                -- Análise Fibonacci
                FIBONACCI tinyint NOT NULL,
                
                -- Metadados
                DATA_CRIACAO datetime DEFAULT GETDATE(),
                QTDE_NUMEROS tinyint DEFAULT 16
            )
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            
            print("✅ Tabela criada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    def calcular_propriedades_combinacao(self, combinacao: List[int]) -> dict:
        """Calcula todas as propriedades de uma combinação"""
        # Soma
        soma = sum(combinacao)
        
        # Paridade
        pares = sum(1 for n in combinacao if n % 2 == 0)
        impares = 16 - pares
        
        # Análise por faixas
        faixa_01_05 = sum(1 for n in combinacao if 1 <= n <= 5)
        faixa_06_10 = sum(1 for n in combinacao if 6 <= n <= 10)
        faixa_11_15 = sum(1 for n in combinacao if 11 <= n <= 15)
        faixa_16_20 = sum(1 for n in combinacao if 16 <= n <= 20)
        faixa_21_25 = sum(1 for n in combinacao if 21 <= n <= 25)
        
        # Sequência máxima
        seq_max = self._calcular_sequencia_maxima(combinacao)
        
        # Números primos
        primos_lista = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        primos = sum(1 for n in combinacao if n in primos_lista)
        
        # Números Fibonacci
        fibonacci_lista = [1, 2, 3, 5, 8, 13, 21]
        fibonacci = sum(1 for n in combinacao if n in fibonacci_lista)
        
        return {
            'soma': soma,
            'pares': pares,
            'impares': impares,
            'faixa_01_05': faixa_01_05,
            'faixa_06_10': faixa_06_10,
            'faixa_11_15': faixa_11_15,
            'faixa_16_20': faixa_16_20,
            'faixa_21_25': faixa_21_25,
            'seq_max': seq_max,
            'primos': primos,
            'fibonacci': fibonacci
        }
    
    def _calcular_sequencia_maxima(self, combinacao: List[int]) -> int:
        """Calcula a maior sequência consecutiva na combinação"""
        if not combinacao:
            return 0
            
        combinacao_ordenada = sorted(combinacao)
        seq_atual = 1
        seq_max = 1
        
        for i in range(1, len(combinacao_ordenada)):
            if combinacao_ordenada[i] == combinacao_ordenada[i-1] + 1:
                seq_atual += 1
                seq_max = max(seq_max, seq_atual)
            else:
                seq_atual = 1
                
        return seq_max
    
    def inserir_lote_combinacoes(self, conn: pyodbc.Connection, lote: List[Tuple]) -> bool:
        """Insere um lote de combinações na tabela"""
        try:
            cursor = conn.cursor()
            
            # SQL de inserção
            insert_sql = """
            INSERT INTO [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16] 
            (N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16,
             SOMA, PARES, IMPARES, FAIXA_01_05, FAIXA_06_10, FAIXA_11_15, 
             FAIXA_16_20, FAIXA_21_25, SEQ_MAX, PRIMOS, FIBONACCI)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.executemany(insert_sql, lote)
            conn.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inserir lote: {e}")
            return False
    
    def gerar_todas_combinacoes(self) -> bool:
        """Gera todas as 2.042.975 combinações de 16 números"""
        print(f"🎯 GERADOR DE COMBINAÇÕES LOTOFÁCIL 16 NÚMEROS")
        print("=" * 60)
        print(f"📊 Total de combinações: {self.total_combinacoes:,}")
        print(f"⚙️ Processamento em lotes de: {self.batch_size:,}")
        print()
        
        # Conecta ao banco
        conn = self.conectar_base()
        if not conn:
            return False
        
        try:
            # Cria a tabela
            if not self.criar_tabela_combinacoes16(conn):
                return False
            
            # Gera e processa as combinações
            print("🔄 Iniciando geração das combinações...")
            inicio_tempo = time.time()
            
            numeros = list(range(1, 26))  # 1 a 25
            combinacoes_processadas = 0
            lote_atual = []
            
            # Gera todas as combinações de 16 números
            for combinacao in itertools.combinations(numeros, 16):
                # Calcula propriedades da combinação
                props = self.calcular_propriedades_combinacao(list(combinacao))
                
                # Monta tuple para inserção
                dados_combinacao = (
                    # Números da combinação (16 números)
                    combinacao[0], combinacao[1], combinacao[2], combinacao[3],
                    combinacao[4], combinacao[5], combinacao[6], combinacao[7],
                    combinacao[8], combinacao[9], combinacao[10], combinacao[11],
                    combinacao[12], combinacao[13], combinacao[14], combinacao[15],
                    # Propriedades calculadas
                    props['soma'], props['pares'], props['impares'],
                    props['faixa_01_05'], props['faixa_06_10'], props['faixa_11_15'],
                    props['faixa_16_20'], props['faixa_21_25'], props['seq_max'],
                    props['primos'], props['fibonacci']
                )
                
                lote_atual.append(dados_combinacao)
                combinacoes_processadas += 1
                
                # Insere lote quando atinge o tamanho definido
                if len(lote_atual) >= self.batch_size:
                    if self.inserir_lote_combinacoes(conn, lote_atual):
                        percent = (combinacoes_processadas / self.total_combinacoes) * 100
                        print(f"   ✅ {combinacoes_processadas:,} combinações processadas ({percent:.1f}%)")
                    else:
                        print(f"   ❌ Erro no lote {combinacoes_processadas//self.batch_size}")
                        return False
                    
                    lote_atual = []
                
                # Mostra progresso a cada 50k
                if combinacoes_processadas % 50000 == 0:
                    tempo_decorrido = time.time() - inicio_tempo
                    taxa = combinacoes_processadas / tempo_decorrido
                    tempo_restante = (self.total_combinacoes - combinacoes_processadas) / taxa
                    
                    print(f"📈 {combinacoes_processadas:,}/{self.total_combinacoes:,} "
                          f"({combinacoes_processadas/self.total_combinacoes*100:.1f}%) - "
                          f"ETA: {tempo_restante/60:.1f} min")
            
            # Insere último lote se houver
            if lote_atual:
                if self.inserir_lote_combinacoes(conn, lote_atual):
                    print(f"   ✅ Último lote: {len(lote_atual)} combinações")
                
            # Estatísticas finais
            tempo_total = time.time() - inicio_tempo
            print(f"\n🎉 PROCESSO CONCLUÍDO!")
            print(f"   • Total processado: {combinacoes_processadas:,} combinações")
            print(f"   • Tempo total: {tempo_total/60:.1f} minutos")
            print(f"   • Taxa média: {combinacoes_processadas/tempo_total:.0f} comb/seg")
            
            # Cria índices para performance
            print(f"\n🔧 Criando índices para otimização...")
            self._criar_indices(conn)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante geração: {e}")
            return False
        finally:
            conn.close()
    
    def _criar_indices(self, conn: pyodbc.Connection):
        """Cria índices na tabela para melhorar performance das consultas"""
        try:
            cursor = conn.cursor()
            
            indices = [
                "CREATE INDEX IX_COMBINACOES16_SOMA ON [COMBINACOES_LOTOFACIL16] (SOMA)",
                "CREATE INDEX IX_COMBINACOES16_PARES ON [COMBINACOES_LOTOFACIL16] (PARES)",
                "CREATE INDEX IX_COMBINACOES16_SEQ_MAX ON [COMBINACOES_LOTOFACIL16] (SEQ_MAX)",
                "CREATE INDEX IX_COMBINACOES16_PRIMOS ON [COMBINACOES_LOTOFACIL16] (PRIMOS)",
                "CREATE INDEX IX_COMBINACOES16_FIBONACCI ON [COMBINACOES_LOTOFACIL16] (FIBONACCI)",
                "CREATE INDEX IX_COMBINACOES16_FAIXAS ON [COMBINACOES_LOTOFACIL16] (FAIXA_01_05, FAIXA_06_10, FAIXA_11_15, FAIXA_16_20, FAIXA_21_25)"
            ]
            
            for i, sql_index in enumerate(indices, 1):
                try:
                    cursor.execute(sql_index)
                    conn.commit()
                    print(f"   ✅ Índice {i}/6 criado")
                except Exception as e:
                    print(f"   ⚠️ Erro no índice {i}: {e}")
            
            print("✅ Índices criados!")
            
        except Exception as e:
            print(f"⚠️ Erro ao criar índices: {e}")
    
    def validar_tabela_criada(self) -> bool:
        """Valida se a tabela foi criada corretamente"""
        try:
            conn = self.conectar_base()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Conta total de registros
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT COUNT(*) FROM [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16]")
            total = cursor.fetchone()[0]
            
            print(f"\n📊 VALIDAÇÃO DA TABELA:")
            print(f"   • Total de registros: {total:,}")
            
            if total == self.total_combinacoes:
                print(f"   ✅ Quantidade correta! ({self.total_combinacoes:,} esperadas)")
            else:
                print(f"   ❌ Quantidade incorreta! ({self.total_combinacoes:,} esperadas)")
                return False
            
            # Testa algumas consultas de exemplo
            print(f"\n🔍 TESTES DE CONSULTA:")
            
            # Soma mínima e máxima
            cursor.execute("""
            SELECT MIN(SOMA) as soma_min, MAX(SOMA) as soma_max 
            FROM [COMBINACOES_LOTOFACIL16]
            """)
            soma_min, soma_max = cursor.fetchone()
            print(f"   • Soma: Min={soma_min}, Max={soma_max}")
            
            # Distribuição de pares/ímpares
            cursor.execute("""
            SELECT PARES, COUNT(*) as qtd 
            FROM [COMBINACOES_LOTOFACIL16] 
            GROUP BY PARES 
            ORDER BY PARES
            """)
            
            print(f"   • Distribuição Pares:")
            for pares, qtd in cursor.fetchall():
                print(f"      {pares} pares: {qtd:,} combinações")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False

def main():
    """Função principal"""
    print("🎯 GERADOR DE TABELA COMBINAÇÕES LOTOFÁCIL 16 NÚMEROS")
    print("=" * 65)
    print("📊 Este script gerará TODAS as 2.042.975 combinações únicas")
    print("⚠️  ATENÇÃO: Processo pode levar várias horas!")
    print()
    
    # Confirmação do usuário
    resposta = input("Deseja continuar? (s/n): ").lower()
    if not resposta.startswith('s'):
        print("⏹️ Processo cancelado pelo usuário")
        return
    
    # Testa conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    # Inicia geração
    gerador = GeradorCombinacoes16()
    
    try:
        if gerador.gerar_todas_combinacoes():
            print("\n🎉 SUCESSO! Tabela COMBINACOES_LOTOFACIL16 criada!")
            
            # Valida resultado
            if gerador.validar_tabela_criada():
                print("\n✅ Validação concluída - Tabela pronta para uso!")
                print("\n📋 PRÓXIMOS PASSOS:")
                print("   • Use a tabela para análises estatísticas")
                print("   • Compare padrões entre combinações de 15 e 16 números")
                print("   • Execute consultas otimizadas com os índices criados")
            else:
                print("\n⚠️ Validação encontrou problemas")
        else:
            print("\n❌ Falha na geração da tabela")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
