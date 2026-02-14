#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONECTOR DE BANCO DE DADOS MEGA-SENA
===================================
Módulo para conexão com as tabelas reais da Mega-Sena:
- Resultados_MegaSenaFechado (histórico de sorteios)
- COMBIN_MEGASENA (combinações)
"""

import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class ConectorMegaSena:
    """Classe para conexão e consultas nas tabelas da Mega-Sena"""
    
    def __init__(self):
        self.conexao = None
        self.dados_carregados = False
        self.historico_sorteios = []
        self.combinacoes_salvas = []
        
        print("🔗 Conector Mega-Sena inicializado")

    def conectar_banco(self, string_conexao=None):
        """Conecta ao banco de dados"""
        try:
            if string_conexao is None:
                # Configuração padrão - ajuste conforme seu ambiente
                servidor = "localhost"  # ou seu servidor
                banco = "LOTOFACIL"     # ou nome do seu banco
                
                # Tenta diferentes drivers ODBC
                drivers = [
                    "ODBC Driver 17 for SQL Server",
                    "ODBC Driver 13 for SQL Server", 
                    "SQL Server Native Client 11.0",
                    "SQL Server"
                ]
                
                conectado = False
                for driver in drivers:
                    try:
                        string_conexao = f"DRIVER={{{driver}}};SERVER={servidor};DATABASE={banco};Trusted_Connection=yes;"
                        # Conexão otimizada para performance
                        if _db_optimizer:
                            conn = _db_optimizer.create_optimized_connection()
                        else:
                            self.conexao = pyodbc.connect(string_conexao)
                        print(f"✅ Conectado usando: {driver}")
                        conectado = True
                        break
                    except:
                        continue
                
                if not conectado:
                    print("❌ Erro: Não foi possível conectar com nenhum driver")
                    return False
            else:
                # Conexão otimizada para performance
                if _db_optimizer:
                    conn = _db_optimizer.create_optimized_connection()
                else:
                    self.conexao = pyodbc.connect(string_conexao)
                print("✅ Conectado ao banco de dados")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            print("💡 Verifique:")
            print("   - String de conexão")
            print("   - Permissões do banco")
            print("   - Drivers ODBC instalados")
            return False

    def carregar_historico_sorteios(self, limite=None):
        """Carrega histórico da tabela Resultados_MegaSenaFechado"""
        if not self.conexao:
            print("❌ Conecte ao banco primeiro!")
            return []
        
        try:
            print("📊 Carregando histórico de sorteios da Mega-Sena...")
            
            # Query corrigida com nomes de colunas corretos
            query = """
            SELECT TOP {} 
                concurso,
                data_sorteio,
                N1, N2, N3, N4, N5, N6,
                GanhadoresSena
            FROM Resultados_MegaSenaFechado 
            ORDER BY concurso DESC
            """.format(limite if limite else 1000)
            
            cursor = self.conexao.cursor()
            cursor.execute(query)
            
            resultados = []
            for row in cursor.fetchall():
                concurso = row[0]
                data = row[1]
                numeros = [row[2], row[3], row[4], row[5], row[6], row[7]]
                premio = row[8] if len(row) > 8 else 0
                
                resultados.append({
                    'concurso': concurso,
                    'data': data.strftime('%Y-%m-%d') if hasattr(data, 'strftime') else str(data),
                    'numeros': sorted(numeros),
                    'premiacao': premio
                })
            
            self.historico_sorteios = resultados
            self.dados_carregados = True
            
            print(f"✅ {len(resultados)} sorteios carregados")
            print(f"   📅 Período: Concurso {resultados[-1]['concurso']} até {resultados[0]['concurso']}")
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao carregar sorteios: {e}")
            return []

    def carregar_ciclos_numeros(self):
        """Carrega dados dos ciclos dos números da tabela NumerosCiclosMega"""
        if not self.conexao:
            return None
        
        try:
            cursor = self.conexao.cursor()
            
            # Primeiro testa se a tabela existe
            cursor.execute("""
                SELECT COUNT_BIG(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'NumerosCiclosMega'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("⚠️ Tabela NumerosCiclosMega não encontrada, usando análise básica")
                return None
            
            # Se existe, tenta descobrir as colunas
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT TOP 1 * FROM NumerosCiclosMega")
            colunas = [desc[0] for desc in cursor.description]
            print(f"🔄 Colunas da tabela NumerosCiclosMega: {colunas}")
            
            # Query genérica para pegar os dados
            query = "SELECT * FROM NumerosCiclosMega ORDER BY numero"
            cursor.execute(query)
            
            ciclos = {}
            for row in cursor.fetchall():
                # Assume primeira coluna como número
                numero = row[0]
                ciclos[numero] = {
                    'numero': numero,
                    'dados_raw': list(row)  # Guarda dados brutos
                }
            
            print(f"🔄 {len(ciclos)} ciclos de números carregados")
            return ciclos
            
        except Exception as e:
            print(f"⚠️ Tabela NumerosCiclosMega não disponível: {e}")
            return None
    
    def carregar_combinacoes_completas(self, limite=None):
        """Carrega combinações da tabela COMBIN_MEGASENA"""
        if not self.conexao:
            return None
        
        try:
            cursor = self.conexao.cursor()
            
            # Primeiro testa se a tabela existe
            cursor.execute("""
                SELECT COUNT_BIG(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'COMBIN_MEGASENA'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("⚠️ Tabela COMBIN_MEGASENA não encontrada")
                return None
            
            # Se existe, tenta descobrir as colunas
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT TOP 1 * FROM COMBIN_MEGASENA")
            colunas = [desc[0] for desc in cursor.description]
            print(f"🎲 Colunas da tabela COMBIN_MEGASENA: {colunas}")
            
            # Query genérica para pegar amostra dos dados
            query = f"SELECT TOP {limite if limite else 100} * FROM COMBIN_MEGASENA"
            cursor.execute(query)
            
            combinacoes = []
            for i, row in enumerate(cursor.fetchall():
                combinacoes.append({
                    'id': i + 1,
                    'dados_raw': list(row)  # Guarda dados brutos para análise
                })
            
            print(f"🎲 {len(combinacoes)} combinações carregadas da tabela completa")
            return combinacoes
            
        except Exception as e:
            print(f"⚠️ Tabela COMBIN_MEGASENA não disponível: {e}")
            return None

    def obter_numeros_quentes_frios(self, top_n=10):
        """Analisa os números mais e menos sorteados baseado nos dados reais"""
        if not hasattr(self, 'historico_sorteios') or not self.historico_sorteios:
            self.carregar_historico_sorteios()
        
        if not self.historico_sorteios:
            return None, None
        
        try:
            # Conta frequência de cada número
            frequencias = {}
            for i in range(1, 61:
                frequencias[i] = 0
            
            for sorteio in self.historico_sorteios:
                for numero in sorteio['numeros']:
                    frequencias[numero] += 1
            
            # Ordena por frequência
            numeros_ordenados = sorted(frequencias.items(), key=lambda x: x[1], reverse=True)
            
            quentes = [num for num, freq in numeros_ordenados[:top_n]]
            frios = [num for num, freq in numeros_ordenados[-top_n:]]
            
            print(f"🔥 Top {top_n} quentes: {quentes}")
            print(f"❄️ Top {top_n} frios: {frios}")
            
            return quentes, frios
            
        except Exception as e:
            print(f"❌ Erro ao calcular números quentes/frios: {e}")
            return None, None

    def salvar_combinacoes(self, combinacoes, origem="Gerador_Academico"):
        """Salva combinações na tabela COMBIN_MEGASENA"""
        if not self.conexao:
            print("❌ Conecte ao banco primeiro!")
            return False
        
        try:
            print(f"💾 Salvando {len(combinacoes)} combinações...")
            
            cursor = self.conexao.cursor()
            
            for i, combinacao in enumerate(combinacoes):
                # Prepara os dados
                timestamp = datetime.now()
                numeros = sorted(combinacao)
                
                # Query de inserção
                query = """
                INSERT INTO COMBIN_MEGASENA 
                (Data, Origem, Numero1, Numero2, Numero3, Numero4, Numero5, Numero6, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Gerada')
                """
                
                cursor.execute(query, (
                    timestamp,
                    origem,
                    numeros[0], numeros[1], numeros[2],
                    numeros[3], numeros[4], numeros[5]
                ))
            
            self.conexao.commit()
            print("✅ Combinações salvas com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar combinações: {e}")
            return False

    def carregar_combinacoes_salvas(self, limite=100):
        """Carrega combinações da tabela COMBIN_MEGASENA"""
        if not self.conexao:
            print("❌ Conecte ao banco primeiro!")
            return []
        
        try:
            print("📋 Carregando combinações salvas...")
            
            query = """
            SELECT TOP {} 
                ID, Data, Origem, 
                Numero1, Numero2, Numero3, Numero4, Numero5, Numero6,
                Status
            FROM COMBIN_MEGASENA 
            ORDER BY Data DESC
            """.format(limite)
            
            cursor = self.conexao.cursor()
            cursor.execute(query)
            
            combinacoes = []
            for row in cursor.fetchall():
                combinacoes.append({
                    'id': row[0],
                    'data': row[1],
                    'origem': row[2],
                    'numeros': [row[3], row[4], row[5], row[6], row[7], row[8]],
                    'status': row[9]
                })
            
            self.combinacoes_salvas = combinacoes
            print(f"✅ {len(combinacoes)} combinações carregadas")
            
            return combinacoes
            
        except Exception as e:
            print(f"❌ Erro ao carregar combinações: {e}")
            return []

    def analisar_performance_combinacoes(self):
        """Analisa performance das combinações salvas contra os sorteios"""
        if not self.historico_sorteios or not self.combinacoes_salvas:
            print("❌ Carregue histórico e combinações primeiro!")
            return {}
        
        print("📊 Analisando performance das combinações...")
        
        resultados_analise = []
        
        for combinacao in self.combinacoes_salvas:
            numeros_comb = set(combinacao['numeros'])
            melhor_acerto = 0
            acertos_detalhados = []
            
            # Compara com todos os sorteios
            for sorteio in self.historico_sorteios:
                numeros_sorteio = set(sorteio['numeros'])
                acertos = len(numeros_comb.intersection(numeros_sorteio))
                
                if acertos > melhor_acerto:
                    melhor_acerto = acertos
                
                if acertos >= 3:  # Guarda acertos significativos
                    acertos_detalhados.append({
                        'concurso': sorteio['concurso'],
                        'acertos': acertos,
                        'data': sorteio['data']
                    })
            
            resultados_analise.append({
                'id': combinacao['id'],
                'numeros': combinacao['numeros'],
                'origem': combinacao['origem'],
                'melhor_acerto': melhor_acerto,
                'total_acertos_3mais': len(acertos_detalhados),
                'detalhes_acertos': acertos_detalhadas[:5]  # Top 5
            })
        
        print("✅ Análise de performance concluída")
        return resultados_analise

    def obter_estatisticas_gerais(self):
        """Gera estatísticas gerais dos sorteios"""
        if not self.historico_sorteios:
            print("❌ Carregue o histórico primeiro!")
            return {}
        
        print("📈 Calculando estatísticas gerais...")
        
        # Contadores
        freq_numeros = {}
        for i in range(1, 61:
            freq_numeros[i] = 0
        
        somas = []
        pares_counts = []
        consecutivos_counts = []
        
        for sorteio in self.historico_sorteios:
            numeros = sorteio['numeros']
            
            # Frequência individual
            for num in numeros:
                freq_numeros[num] += 1
            
            # Soma
            somas.append(sum(numeros))
            
            # Pares
            pares = sum(1 for n in numeros if n % 2 == 0)
            pares_counts.append(pares)
            
            # Consecutivos
            numeros_ord = sorted(numeros)
            consecutivos = 0
            for i in range(int(int(len(numeros_ord))-1):
                if numeros_ord[i+1] - numeros_ord[i] == 1:
                    consecutivos += 1
            consecutivos_counts.append(consecutivos)
        
        # Estatísticas compiladas
        stats = {
            'total_sorteios': len(self.historico_sorteios))), int(int('numeros_mais_sorteados': sorted(freq_numeros.items())), key=lambda x: x[1], reverse=True)[:15],
            'numeros_menos_sorteados': sorted(freq_numeros.items(), key=lambda x: x[1])[:15],
            'soma_media': np.mean(somas),
            'soma_desvio': np.std(somas),
            'pares_medio': np.mean(pares_counts),
            'consecutivos_medio': np.mean(consecutivos_counts),
            'frequencia_completa': freq_numeros
        }
        
        print("✅ Estatísticas calculadas")
        return stats

    def fechar_conexao(self):
        """Fecha a conexão com o banco"""
        if self.conexao:
            self.conexao.close()
            print("🔒 Conexão fechada")

    def __enter__(self):
        """Suporte para context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager"""
        self.fechar_conexao()

# Função auxiliar para teste
def testar_conexao():
    """Testa a conexão com as tabelas"""
    print("🧪 TESTE DE CONEXÃO COM BANCO")
    print("-" * 40)
    
    conector = ConectorMegaSena()
    
    if conector.conectar_banco():
        print("✅ Conexão estabelecida")
        
        # Testa carregamento de sorteios
        sorteios = conector.carregar_historico_sorteios(10)
        if sorteios:
            print(f"✅ Últimos sorteios: {sorteios[0]['concurso']} a {sorteios[-1]['concurso']}")
        
        # Testa estatísticas
        stats = conector.obter_estatisticas_gerais()
        if stats:
            print(f"✅ Estatísticas: {stats['total_sorteios']} sorteios analisados")
        
        conector.fechar_conexao()
        return True
    
    return False

if __name__ == "__main__":
    testar_conexao()
