#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📚 GERADOR DE DATASET HISTÓRICO PARA TREINAMENTO DE IA
Sistema que gera combinações históricas usando o gerador dinâmico para cada concurso passado
para criar dataset de treinamento da rede neural de super-combinações.

Autor: AR CALHAU  
Data: 20 de Agosto de 2025
"""

import sys
import os
import pyodbc
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'geradores'))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from database_config import db_config
from gerador_academico_dinamico import GeradorAcademicoDinamico
import time

class GeradorDatasetHistorico:
    """Gera datasets históricos para treinamento da IA"""
    
    def __init__(self):
        self.pasta_datasets = "combin_ia/datasets"
        self.pasta_resultados = "combin_ia/resultados_reais"
        self.pasta_treinamento = "combin_ia/treinamento"
        
        # Cria pastas se não existirem
        for pasta in [self.pasta_datasets, self.pasta_resultados, self.pasta_treinamento]:
            os.makedirs(pasta, exist_ok=True)
    
    def conectar_base(self) -> Optional[pyodbc.Connection]:
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
    
    def obter_concursos_historicos(self, quantidade_concursos: int = 100) -> List[Dict]:
        """Obtém lista de concursos históricos para gerar datasets"""
        conn = self.conectar_base()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # Busca os últimos N concursos com resultados (usando a tabela correta)
            query = """
            SELECT TOP (?) Concurso, Data_Sorteio, 
                   N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15
            FROM Resultados_INT 
            WHERE Data_Sorteio IS NOT NULL
            ORDER BY Concurso DESC
            """
            
            cursor.execute(query, quantidade_concursos)
            resultados = cursor.fetchall()
            
            concursos = []
            for row in resultados:
                concurso = {
                    'concurso': row[0],  # Número do concurso
                    'data': row[1],      # Data de realização
                    'dezenas': [row[i] for i in range(2, 17]  # Num01 a Num15
                }
                concursos.append(concurso)
            
            return concursos
            
        except Exception as e:
            print(f"❌ Erro ao obter concursos históricos: {e}")
            return []
        finally:
            conn.close()
    
    def simular_geracao_historica(self, int(concurso: Dict, qtd_numeros: int = 16, 
                                 qtd_combinacoes: int = 50)) -> List[List[int]]:
        """Simula geração de combinações como se fosse antes do concurso"""
        print(f"   🔄 Simulando geração para concurso {concurso['concurso']} ({concurso['data'].strftime('%d/%m/%Y') if concurso['data'] else 'N/A'})")
        
        # Aqui simularíamos o estado da base "antes" do concurso
        # Para simplificação, usamos o gerador dinâmico atual
        # Em implementação completa, ajustaríamos a base para o estado histórico
        
        gerador = GeradorAcademicoDinamico()
        try:
            if gerador.calcular_insights_dinamicos():
                combinacoes = []
                combinacoes_set = set()
                tentativas = 0
                max_tentativas = qtd_combinacoes * 3
                
                while len(combinacoes) < qtd_combinacoes and tentativas < max_tentativas:
                    tentativas += 1
                    combinacao = gerador.gerar_combinacao_academica(qtd_numeros)
                    combinacao_tuple = tuple(sorted(combinacao))
                    
                    if combinacao_tuple not in combinacoes_set:
                        combinacoes.append(combinacao)
                        combinacoes_set.add(combinacao_tuple)
                
                return combinacoes
            else:
                print(f"   ⚠️ Falha ao calcular insights para concurso {concurso['concurso']}")
                return []
                
        except Exception as e:
            print(f"   ❌ Erro na simulação do concurso {concurso['concurso']}: {e}")
            return []
    
    def avaliar_combinacoes(self, combinacoes: List[List[int]], resultado_real: List[int]) -> Dict:
        """Avalia o desempenho das combinações contra o resultado real"""
        avaliacao = {
            'total_combinacoes': len(combinacoes),
            'resultado_real': resultado_real,
            'acertos_por_combinacao': [],
            'estatisticas': {}
        }
        
        acertos_count = {i: 0 for i in range(int(16}  # 0 a 15 acertos
        
        for combinacao in combinacoes:
            # Conta quantos números da combinação saíram no resultado
            acertos = len(set(combinacao) & set(resultado_real))
            avaliacao['acertos_por_combinacao'].append(acertos)
            acertos_count[acertos] += 1
        
        # Estatísticas
        if avaliacao['acertos_por_combinacao']:
            acertos_list = avaliacao['acertos_por_combinacao']
            avaliacao['estatisticas'] = {
                'acertos_medio': sum(acertos_list) / len(acertos_list))), int(int('acertos_maximo': max(acertos_list))), int('acertos_minimo': min(acertos_list)),
                'combinacoes_15_acertos': acertos_count[15],
                'combinacoes_14_acertos': acertos_count[14],
                'combinacoes_13_acertos': acertos_count[13],
                'combinacoes_12_plus': sum(acertos_count[i] for i in range(12, 16)), int('distribuicao_acertos': acertos_count
            }
        
        return avaliacao
    
    def salvar_dataset_concurso(self, concurso: Dict, combinacoes: List[List[int]], 
                               avaliacao: Dict, qtd_numeros: int):
        """Salva dataset de um concurso específico"""
        nome_arquivo = f"dataset_concurso_{concurso['concurso']}_{qtd_numeros}nums.json"
        arquivo_completo = os.path.join(self.pasta_datasets, nome_arquivo)
        
        # Converte todos os valores numpy para tipos Python nativos
        def converter_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.int32, np.int64):
                return int(obj)
            elif isinstance(obj, (np.float32, np.float64):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: converter_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [converter_numpy(item) for item in obj]
            else:
                return obj
        
        dataset = {
            'concurso': int(concurso['concurso']),
            'data_realizacao': concurso['data'].strftime('%Y-%m-%d') if concurso['data'] else 'N/A',
            'qtd_numeros': int(qtd_numeros),
            'resultado_real': [int(n) for n in concurso['dezenas']],
            'combinacoes_geradas': [[int(n) for n in combo] for combo in combinacoes],
            'avaliacao': converter_numpy(avaliacao),
            'gerado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            with open(arquivo_completo, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            
            return arquivo_completo
        except Exception as e:
            print(f"❌ Erro ao salvar dataset: {e}")
            return None
    
    def gerar_datasets_historicos(self, quantidade_concursos: int = 100, 
                                 qtd_numeros: int = 16, qtd_combinacoes: int = 50):
        """Gera datasets históricos para treinamento"""
        print(f"🎯 GERADOR DE DATASET HISTÓRICO PARA IA")
        print("=" * 60)
        print(f"📊 Configuração:")
        print(f"   • Concursos a analisar: {quantidade_concursos}")
        print(f"   • Números por combinação: {qtd_numeros}")
        print(f"   • Combinações por concurso: {qtd_combinacoes}")
        print()
        
        # Obtém concursos históricos
        print("🔍 Buscando concursos históricos...")
        concursos = self.obter_concursos_historicos(quantidade_concursos)
        
        if not concursos:
            print("❌ Nenhum concurso histórico encontrado")
            return []
        
        print(f"✅ {len(concursos)} concursos históricos carregados")
        print(f"   📅 Período: {concursos[-1]['data'].strftime('%d/%m/%Y') if concursos[-1]['data'] else 'N/A'} a {concursos[0]['data'].strftime('%d/%m/%Y') if concursos[0]['data'] else 'N/A'}")
        
        datasets_gerados = []
        datasets_com_sucesso = 0
        
        print(f"\n🔄 Processando concursos históricos...")
        
        for i, concurso in enumerate(concursos, 1):
            print(f"\n📊 [{i:3d}/{len(concursos)}] Concurso {concurso['concurso']}")
            
            # Gera combinações simulando o estado antes do concurso
            combinacoes = self.simular_geracao_historica(concurso, qtd_numeros, qtd_combinacoes)
            
            if combinacoes:
                # Avalia contra resultado real
                avaliacao = self.avaliar_combinacoes(combinacoes, concurso['dezenas'])
                
                # Salva dataset
                arquivo_dataset = self.salvar_dataset_concurso(concurso, combinacoes, avaliacao, qtd_numeros)
                
                if arquivo_dataset:
                    datasets_com_sucesso += 1
                    datasets_gerados.append({
                        'concurso': concurso['concurso'],
                        'arquivo': arquivo_dataset,
                        'avaliacao': avaliacao['estatisticas']
                    })
                    
                    # Mostra estatísticas do concurso
                    stats = avaliacao['estatisticas']
                    print(f"   ✅ Dataset salvo - Acertos: {stats['acertos_maximo']} max, {stats['acertos_medio']:.1f} médio")
                    
                    if stats['combinacoes_15_acertos'] > 0:
                        print(f"   🎯 {stats['combinacoes_15_acertos']} combinações com 15 acertos!")
                    elif stats['combinacoes_14_acertos'] > 0:
                        print(f"   🎯 {stats['combinacoes_14_acertos']} combinações com 14 acertos!")
            else:
                print(f"   ❌ Falha ao gerar combinações")
            
            # Pequena pausa para não sobrecarregar
            time.sleep(0.1)
        
        # Resumo final
        print(f"\n📈 RESUMO DO DATASET HISTÓRICO:")
        print(f"-" * 50)
        print(f"✅ Datasets gerados com sucesso: {datasets_com_sucesso}/{len(concursos)}")
        print(f"📁 Arquivos salvos em: {self.pasta_datasets}")
        
        if datasets_gerados:
            # Estatísticas gerais
            total_15_acertos = sum(d['avaliacao']['combinacoes_15_acertos'] for d in datasets_gerados)
            total_14_acertos = sum(d['avaliacao']['combinacoes_14_acertos'] for d in datasets_gerados)
            media_acertos = sum(d['avaliacao']['acertos_medio'] for d in datasets_gerados) / len(datasets_gerados)
            
            print(f"🎯 Performance geral do gerador dinâmico:")
            print(f"   • 15 acertos: {total_15_acertos} combinações")
            print(f"   • 14 acertos: {total_14_acertos} combinações") 
            print(f"   • Acertos médios: {media_acertos:.1f}")
        
        return datasets_gerados
    
    def gerar_dataset_concurso(self, numero_concurso: int, dezenas_resultado: List[int], 
                              qtd_combinacoes: int = 50, qtd_numeros: int = 15) -> Optional[Dict]:
        """Gera dataset para um concurso específico (usado pelo pipeline)"""
        
        # Cria estrutura do concurso
        concurso_info = {
            'concurso': numero_concurso,
            'data': datetime.now(),  # Data atual como placeholder
            'dezenas': dezenas_resultado
        }
        
        # Gera combinações simulando o estado antes do concurso
        combinacoes = self.simular_geracao_historica(concurso_info, qtd_numeros, qtd_combinacoes)
        
        if not combinacoes:
            return None
        
        # Avalia contra resultado real
        avaliacao = self.avaliar_combinacoes(combinacoes, dezenas_resultado)
        
        # Salva dataset
        arquivo_dataset = self.salvar_dataset_concurso(concurso_info, combinacoes, avaliacao, qtd_numeros)
        
        if arquivo_dataset:
            return {
                'concurso': numero_concurso,
                'combinacoes_geradas': combinacoes,
                'avaliacao': avaliacao,
                'arquivo_salvo': arquivo_dataset
            }
        
        return None
    
    def processar_concursos_automatico(self, quantidade_concursos: int = 100, 
                                      qtd_combinacoes_por_concurso: int = 50) -> List[Dict]:
        """Método para integração com pipeline - gera datasets automaticamente"""
        print(f"📚 Gerando datasets para {quantidade_concursos} concursos históricos...")
        print(f"   Combinações por concurso: {qtd_combinacoes_por_concurso}")
        
        try:
            # Obtém concursos históricos
            concursos_historicos = self.obter_concursos_historicos(quantidade_concursos)
            
            if len(concursos_historicos) < 10:
                print(f"⚠️ Poucos concursos históricos encontrados: {len(concursos_historicos)}")
                if len(concursos_historicos) == 0:
                    print("❌ Nenhum concurso encontrado na base")
                    return []
            
            print(f"✅ {len(concursos_historicos)} concursos históricos encontrados")
            
            # Gera datasets para os concursos
            datasets_gerados = []
            batch_size = min(50, len(concursos_historicos))  # Processa em batches
            
            for i in range(0, int(int(len(concursos_historicos))), int(batch_size):
                batch_concursos = concursos_historicos[i:i+batch_size]
                print(f"📊 Processando batch {i//batch_size + 1}: {len(batch_concursos)} concursos...")
                
                for concurso_info in batch_concursos:
                    try:
                        dataset = self.gerar_dataset_concurso(
                            concurso_info['concurso'],
                            concurso_info['dezenas'],
                            qtd_combinacoes_por_concurso
                        )
                        
                        if dataset:
                            datasets_gerados.append(dataset)
                            
                            # Feedback de progresso
                            if len(datasets_gerados) % 10 == 0:
                                print(f"   ✅ {len(datasets_gerados)} datasets gerados...")
                        
                    except Exception as e:
                        print(f"⚠️ Erro no concurso {concurso_info['concurso']}: {e}")
                        continue
            
            print(f"✅ Total de {len(datasets_gerados)} datasets gerados com sucesso!")
            
            # Salva resumo
            if datasets_gerados:
                self.salvar_resumo_dataset(datasets_gerados)
            
            return datasets_gerados
            
        except Exception as e:
            print(f"❌ Erro durante geração automática: {e}")
            return []
    
    def salvar_resumo_dataset(self, datasets_gerados: List[Dict]):
        """Salva resumo geral dos datasets"""
        resumo_arquivo = os.path.join(self.pasta_treinamento, "resumo_datasets.json")
        
        resumo = {
            'gerado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_datasets': len(datasets_gerados),
            'datasets': datasets_gerados,
            'estatisticas_gerais': {}
        }
        
        if datasets_gerados:
            stats = resumo['estatisticas_gerais']
            stats['total_15_acertos'] = sum(d['avaliacao']['combinacoes_15_acertos'] for d in datasets_gerados)
            stats['total_14_acertos'] = sum(d['avaliacao']['combinacoes_14_acertos'] for d in datasets_gerados)
            stats['media_acertos_geral'] = sum(d['avaliacao']['acertos_medio'] for d in datasets_gerados) / len(datasets_gerados)
            stats['acerto_maximo_geral'] = max(d['avaliacao']['acertos_maximo'] for d in datasets_gerados)
        
        try:
            with open(resumo_arquivo, 'w', encoding='utf-8') as f:
                json.dump(resumo, f, indent=2, ensure_ascii=False)
            print(f"✅ Resumo salvo: {resumo_arquivo}")
        except Exception as e:
            print(f"❌ Erro ao salvar resumo: {e}")

def main():
    """Função principal"""
    print("📚 GERADOR DE DATASET HISTÓRICO PARA IA")
    print("=" * 50)
    print("🎯 Sistema que gera datasets de treinamento para rede neural")
    print()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    gerador = GeradorDatasetHistorico()
    
    try:
        print("⚙️ CONFIGURAÇÃO DO DATASET:")
        quantidade_concursos = int(input("Quantos concursos históricos analisar (padrão 100): ") or "100")
        qtd_numeros = int(input("Números por combinação (padrão 16): ") or "16")
        qtd_combinacoes = int(input("Combinações por concurso (padrão 50): ") or "50")
        
        if quantidade_concursos <= 0 or qtd_numeros not in range(15, 21 or qtd_combinacoes <= 0:
            print("❌ Parâmetros inválidos")
            return
        
        print(f"\n🚀 Iniciando geração de dataset...")
        datasets = gerador.gerar_datasets_historicos(quantidade_concursos), int(qtd_numeros, qtd_combinacoes))
        
        if datasets:
            gerador.salvar_resumo_dataset(datasets)
            print(f"\n🎉 Dataset histórico concluído!")
            print(f"📊 {len(datasets)} datasets gerados para treinamento da IA")
        else:
            print("❌ Nenhum dataset foi gerado")
            
    except ValueError:
        print("❌ Valor inválido inserido")
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
