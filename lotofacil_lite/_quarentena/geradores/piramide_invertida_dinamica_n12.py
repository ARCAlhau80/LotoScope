import random
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 PIRAMIDE_INVERTIDA_DINAMICA COM INTELIGÊNCIA N12
============================================================
Versão do piramide_invertida_dinamica integrada com inteligência N12.

MELHORIAS:
✅ Aplicação automática da teoria N12 comprovada
✅ Filtros inteligentes baseados na situação atual
✅ Otimização pós-equilíbrio perfeito (concurso 3490)
✅ Estratégia: DIVERSIFICAR_COM_ENFASE_EXTREMOS

SITUAÇÃO ATUAL:
• Último concurso: 3490 (equilíbrio 5-5-5, N12=19)
• Próximo: Alta probabilidade de oscilação
• N12 ideais: 16, 17, 18, 20, 21, 22

Versão otimizada gerada automaticamente em: 19/09/2025
Baseado no piramide_invertida_dinamica original com integração N12
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'ia'))

# Importação da inteligência N12
from integracao_n12 import aplicar_inteligencia_n12, gerar_combinacoes_inteligentes_n12

import numpy as np
import pandas as pd
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter, deque
from datetime import datetime, timedelta
from database_config import db_config
import pickle
import os
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

class PiramideInvertidaDinamica:
    """Sistema completo de análise de pirâmide invertida com IA"""
    
    def __init__(self):
        self.faixas_piramide = {
            '0_acertos': [],
            '1_acerto': [],
            '2_acertos': [],
            '3_acertos': [],
            '4_ou_mais': []
        }
        
        # Estados históricos para análise temporal
        self.historico_piramides = []
        self.historico_movimentacoes = []
        self.ciclo_atual = 0  # 🔧 Adiciona propriedade para controle do ciclo atual
        
        # Sistema de janela adaptativa
        self.sequencia_dominante = {'numero': None, 'tamanho': 0, 'ciclo_inicio': None}
        self.janela_inicial = 0
        self.janela_atual = 0
        
        # 🎯 FILTROS DE COMBINAÇÕES VALIDADAS (NOVA FUNCIONALIDADE)
        self.filtros_validados = {
            'jogo_1': [1, 2, 3, 4, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 25],
            'jogo_2': [1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 23, 24, 25]
        }
        
        # Configuração do filtro (pode ser ajustado)
        self.usar_filtro_validado = True
        self.min_acertos_filtro = 11  # Mínimo de acertos necessários
        self.max_acertos_filtro = 13  # Máximo de acertos (para não ser muito específico)
        
        # Modelos de IA
        self.modelo_transicoes = None
        self.modelo_sequencias = None
        self.scaler_features = StandardScaler()
        
        # Cache de dados
        self.dados_ciclos = None
        self.dados_resultados_reais = []  # NOVO: dados diretos Resultados_INT
        self.dados_carregados = False
        
        # Configurações de aprendizado
        # 🚀 CONFIGURAÇÕES OTIMIZADAS APLICADAS
        self.otimizacoes_aplicadas = {
            'data_aplicacao': '02/09/2025',
            'versao': 'v2.0_otimizada',
            'mudancas': {
                'threshold_ia': '0.4 → 0.25 (mais modelos aceitos)',
                'confianca_ia': '0.6 → 0.35 (predições mais ousadas)',
                'prob_0_acertos': '0.95 → 0.85 (menos conservador)',
                'prob_1_acerto': '0.70 → 0.75 (mais agressivo)',
                'prob_2_acertos': '0.50 → 0.40 (reduzir concentração)',
                'prob_3_acertos': '0.65 → 0.75 (mais movimento)',
                'prob_4_mais': '0.50 → 0.60 (mais ativo)',
                'logica_empirica': 'Distribuição mais variada entre faixas'
            },
            'objetivo': 'Distribuir melhor: 20-30% por faixa vs 72% em 2_acertos'
        }
        
        self.config_ia = {
            'min_ciclos_analise': 20,
            'janela_sequencia_min': 3,
            'confianca_predicao': 0.75,
            'probabilidades_empiricas': {
                # 🚀 OTIMIZAÇÃO 3: Probabilidades mais agressivas para dispersar distribuição
                '0_acertos': 0.85,    # 85% chance de sair (era 95% - mais conservador)
                '1_acerto': 0.75,     # 75% chance de sair (era 70% - mais agressivo)
                '2_acertos': 0.40,    # 40% chance de sair (era 50% - menos conservador) 
                '3_acertos': 0.75,    # 75% chance de sair (era 65% - mais agressivo)
                '4_ou_mais': 0.60     # 60% chance de sair (era 50% - mais agressivo)
            }
        }
    
    def mostrar_otimizacoes_aplicadas(self):
        """🚀 Mostra as otimizações aplicadas no sistema"""
        print("\n🚀 OTIMIZAÇÕES APLICADAS NO SISTEMA PIRÂMIDE")
        print("=" * 60)
        print(f"📅 Data: {self.otimizacoes_aplicadas['data_aplicacao']}")
        print(f"🏷️  Versão: {self.otimizacoes_aplicadas['versao']}")
        print(f"🎯 Objetivo: {self.otimizacoes_aplicadas['objetivo']}")
        print("\n📊 MUDANÇAS IMPLEMENTADAS:")
        for parametro, mudanca in self.otimizacoes_aplicadas['mudancas'].items():
            print(f"   • {parametro.replace('_', ' ').title()}: {mudanca}")
        print("=" * 60)

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
    
    def validar_combinacao_filtro(self, combinacao: List[int]) -> bool:
        """
        🎯 VALIDADOR DE FILTRO BASEADO NAS COMBINAÇÕES COMPROVADAS
        Verifica se a combinação tem 11-13 acertos com pelo menos uma das combinações validadas
        """
        if not self.usar_filtro_validado:
            return True  # Se filtro está desabilitado, aceita qualquer combinação
        
        combinacao_set = set(combinacao)
        
        # Verifica acertos com Jogo 1
        acertos_jogo1 = len(combinacao_set.intersection(set(self.filtros_validados['jogo_1'])))
        
        # Verifica acertos com Jogo 2
        acertos_jogo2 = len(combinacao_set.intersection(set(self.filtros_validados['jogo_2'])))
        
        # Verifica se atende aos critérios
        valido_jogo1 = self.min_acertos_filtro <= acertos_jogo1 <= self.max_acertos_filtro
        valido_jogo2 = self.min_acertos_filtro <= acertos_jogo2 <= self.max_acertos_filtro
        
        # Retorna True se atende pelo menos um dos filtros
        return valido_jogo1 or valido_jogo2
    
    def calcular_acertos_filtros(self, combinacao: List[int]) -> Dict[str, int]:
        """
        Calcula quantos acertos a combinação tem com cada filtro validado
        """
        combinacao_set = set(combinacao)
        
        return {
            'jogo_1': len(combinacao_set.intersection(set(self.filtros_validados['jogo_1']))),
            'jogo_2': len(combinacao_set.intersection(set(self.filtros_validados['jogo_2'])))
        }
    
    def configurar_filtro_validado(self, usar_filtro: bool = True, min_acertos: int = 11, max_acertos: int = 13):
        """
        🎯 CONFIGURADOR DO FILTRO VALIDADO
        
        Args:
            usar_filtro: True para ativar o filtro, False para desativar
            min_acertos: Mínimo de acertos necessários (padrão 11)
            max_acertos: Máximo de acertos permitidos (padrão 13)
        """
        self.usar_filtro_validado = usar_filtro
        self.min_acertos_filtro = min_acertos
        self.max_acertos_filtro = max_acertos
        
        if usar_filtro:
            print(f"🔺🎯 FILTRO VALIDADO ATIVADO NA PIRÂMIDE:")
            print(f"   📊 Faixa de acertos: {min_acertos} - {max_acertos}")
            print(f"   🎮 Jogo 1: {self.filtros_validados['jogo_1']}")
            print(f"   🎮 Jogo 2: {self.filtros_validados['jogo_2']}")
            print(f"   ✅ Combinações devem ter {min_acertos}-{max_acertos} acertos com pelo menos um jogo")
        else:
            print(f"⚠️ FILTRO VALIDADO DESATIVADO NA PIRÂMIDE - Gerando combinações sem restrições")
    
    def analisar_eficiencia_filtro(self, num_amostras: int = 1000) -> Dict:
        """
        📊 ANALISA A EFICIÊNCIA DO FILTRO NA PIRÂMIDE
        Gera amostras usando método da pirâmide e verifica quantas passariam no filtro
        """
        print(f"🔺🔍 ANALISANDO EFICIÊNCIA DO FILTRO NA PIRÂMIDE ({num_amostras} amostras)...")
        
        combinacoes_aprovadas = 0
        distribuicao_acertos_j1 = []
        distribuicao_acertos_j2 = []
        
        # Salva estado atual do filtro
        filtro_original = self.usar_filtro_validado
        self.usar_filtro_validado = False  # Desativa temporariamente para gerar amostras puras
        
        try:
            # Prepara dados para geração
            if not hasattr(self, 'dados_carregados') or not self.dados_carregados:
                self.carregar_dados_historicos()
            
            piramide_atual = self.analisar_piramide_atual()
            predicoes = self.predizer_proxima_faixa()
            sequencias = self.monitorar_sequencias()
            
            for i in range(int(int(int(num_amostras):
                # Gera combinação usando método da pirâmide
                combinacao_piramide = self._gerar_combinacao_piramide(
                    piramide_atual)), int(int(predicoes), int(sequencias, 15
                )))
                
                # Testa com o filtro
                if self.validar_combinacao_filtro(combinacao_piramide):
                    combinacoes_aprovadas += 1
                
                acertos = self.calcular_acertos_filtros(combinacao_piramide)
                distribuicao_acertos_j1.append(acertos['jogo_1'])
                distribuicao_acertos_j2.append(acertos['jogo_2'])
                
                if (i + 1) % 200 == 0:
                    print(f"   📊 Progresso: {i + 1}/{num_amostras} ({(i+1)/num_amostras*100:.1f}%)")
        
        finally:
            # Restaura estado original
            self.usar_filtro_validado = filtro_original
        
        # Estatísticas
        taxa_aprovacao = (combinacoes_aprovadas / num_amostras) * 100
        reducao_espaco = 100 - taxa_aprovacao
        
        resultado = {
            'amostras_testadas': num_amostras,
            'combinacoes_aprovadas': combinacoes_aprovadas,
            'taxa_aprovacao': taxa_aprovacao,
            'reducao_espaco_busca': reducao_espaco,
            'media_acertos_j1': np.mean(distribuicao_acertos_j1),
            'media_acertos_j2': np.mean(distribuicao_acertos_j2),
            'distribuicao_j1': {
                'min': min(distribuicao_acertos_j1),
                'max': max(distribuicao_acertos_j1),
                'std': np.std(distribuicao_acertos_j1)
            },
            'distribuicao_j2': {
                'min': min(distribuicao_acertos_j2),
                'max': max(distribuicao_acertos_j2),
                'std': np.std(distribuicao_acertos_j2)
            }
        }
        
        print(f"\n🔺📊 RELATÓRIO DE EFICIÊNCIA DO FILTRO NA PIRÂMIDE:")
        print(f"-" * 55)
        print(f"   🎯 Combinações aprovadas: {combinacoes_aprovadas}/{num_amostras} ({taxa_aprovacao:.1f}%)")
        print(f"   📉 Redução do espaço de busca: {reducao_espaco:.1f}%")
        print(f"   📊 Estimativa de combinações válidas: ~{int(3268760 * taxa_aprovacao / 100):,}")
        print(f"   🎮 Média de acertos com Jogo 1: {resultado['media_acertos_j1']:.1f}")
        print(f"   🎮 Média de acertos com Jogo 2: {resultado['media_acertos_j2']:.1f}")
        
        return resultado
    
    def carregar_dados_historicos(self) -> bool:
        """Carrega todos os dados históricos de ciclos para análise"""
        print("🔍 Carregando dados históricos completos...")
        
        conn = self.conectar_base()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Busca TODOS os ciclos históricos
            query = """
            SELECT Ciclo, Numero, QtdSorteados
            FROM NumerosCiclos 
            ORDER BY Ciclo ASC, Numero ASC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Organiza dados em DataFrame para facilitar análise
            dados = []
            for row in resultados:
                dados.append({
                    'ciclo': row[0],
                    'numero': row[1],
                    'qtd_sorteados': row[2]
                })
            
            self.dados_ciclos = pd.DataFrame(dados)
            
            # NOVO: Carregar também dados diretos da Resultados_INT
            self.carregar_dados_resultados_diretos(cursor)
            
            if len(self.dados_ciclos) > 0:
                # Define o ciclo atual como o mais recente
                self.ciclo_atual = self.dados_ciclos['ciclo'].max()
                print(f"✅ Carregados {len(self.dados_ciclos)} registros de {self.dados_ciclos['ciclo'].nunique()} ciclos")
                self.dados_carregados = True
                return True
            else:
                print("❌ Nenhum dado encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
        finally:
            conn.close()

    def carregar_dados_resultados_diretos(self, cursor):
        """NOVO: Carrega dados diretos da tabela Resultados_INT para análise complementar"""
        print("🔍 Carregando dados diretos da Resultados_INT...")
        
        try:
            # Busca últimos 100 concursos para análise complementar
            query_resultados = """
            SELECT TOP 100 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            cursor.execute(query_resultados)
            resultados_diretos = cursor.fetchall()
            
            for row in resultados_diretos:
                concurso = row[0]
                numeros = [row[i] for i in range(1, 16]
                
                self.dados_resultados_reais.append({
                    'concurso': concurso), int('numeros': sorted(numeros)),
                    'padroes_piramide': self.analisar_padroes_piramide_diretos(numeros)
                })
            
            print(f"✅ {len(self.dados_resultados_reais)} concursos carregados para análise complementar")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados diretos: {e}")

    def analisar_padroes_piramide_diretos(self, numeros):
        """Analisa padrões específicos para sistema pirâmide nos dados diretos"""
        return {
            'amplitude': max(numeros) - min(numeros),
            'distribuicao_quadrantes': self.calcular_distribuicao_quadrantes(numeros),
            'densidade_numerica': len(numeros) / (max(numeros) - min(numeros)) if max(numeros) > min(numeros) else 0,
            'sequencias_piramide': self.detectar_sequencias_piramide(numeros)
        }

    def calcular_distribuicao_quadrantes(self, numeros):
        """Calcula distribuição em quadrantes (1-6, 7-12, 13-18, 19-25)"""
        q1 = len([n for n in numeros if 1 <= n <= 6])
        q2 = len([n for n in numeros if 7 <= n <= 12])
        q3 = len([n for n in numeros if 13 <= n <= 18])
        q4 = len([n for n in numeros if 19 <= n <= 25])
        return {'q1': q1, 'q2': q2, 'q3': q3, 'q4': q4}

    def detectar_sequencias_piramide(self, numeros):
        """Detecta sequências específicas para análise pirâmide"""
        consecutivos = 0
        max_consecutivos = 0
        numeros_ord = sorted(numeros)
        
        for i in range(int(int(int(len(numeros_ord)) - 1):
            if numeros_ord[i+1] == numeros_ord[i] + 1:
                consecutivos += 1
                max_consecutivos = max(max_consecutivos)), int(int(consecutivos + 1))
            else:
                consecutivos = 0
        
        return max_consecutivos
    
    def classificar_numero_em_faixa(self, int(qtd_sorteados: int)) -> str:
        """Classifica um número em sua faixa baseado na quantidade de sorteios"""
        if qtd_sorteados == 0:
            return '0_acertos'
        elif qtd_sorteados == 1:
            return '1_acerto'
        elif qtd_sorteados == 2:
            return '2_acertos'
        elif qtd_sorteados == 3:
            return '3_acertos'
        else:
            return '4_ou_mais'
    
    def analisar_piramide_atual(self, ciclo: int = None) -> Dict[str, List[int]]:
        """
        MÓDULO 1: Analisador da Pirâmide Atual
        Identifica a configuração atual das faixas
        """
        if not self.dados_carregados:
            if not self.carregar_dados_historicos():
                return {}
        
        if ciclo is None:
            ciclo = self.dados_ciclos['ciclo'].max()
        
        print(f"🔺 Analisando pirâmide do ciclo {ciclo}...")
        
        # Filtra dados do ciclo específico
        dados_ciclo = self.dados_ciclos[self.dados_ciclos['ciclo'] == ciclo]
        
        piramide_atual = {
            '0_acertos': [],
            '1_acerto': [],
            '2_acertos': [],
            '3_acertos': [],
            '4_ou_mais': []
        }
        
        for _, row in dados_ciclo.iterrows():
            numero = int(row['numero'])
            qtd_sorteados = int(row['qtd_sorteados'])
            faixa = self.classificar_numero_em_faixa(qtd_sorteados)
            piramide_atual[faixa].append(numero)
        
        # Ordena os números em cada faixa
        for faixa in piramide_atual:
            piramide_atual[faixa].sort()
        
        self.faixas_piramide = piramide_atual
        
        print("📊 CONFIGURAÇÃO ATUAL DA PIRÂMIDE:")
        for faixa, numeros in piramide_atual.items():
            print(f"   {faixa.replace('_', ' ').title()}: {numeros} ({len(numeros)} números)")
        
        return piramide_atual
    
    def monitorar_sequencias(self, ciclos_analise: int = 10) -> Dict:
        """
        MÓDULO 2: Monitor de Sequências
        Rastreia qual número/sequência domina a janela
        """
        if not self.dados_carregados:
            return {}
        
        print(f"🎯 Monitorando sequências nos últimos {ciclos_analise} ciclos...")
        
        # Pega os últimos ciclos para análise
        ciclos_disponiveis = sorted(self.dados_ciclos['ciclo'].unique())
        ciclos_alvo = ciclos_disponiveis[-ciclos_analise:]
        
        sequencias_ativas = {}
        maior_sequencia = {'numero': None, 'tamanho': 0, 'ciclos': []}
        
        # Para cada número, analisa sua sequência
        for numero in range(1, 26:
            sequencia_atual = {'tamanho': 0), int('ciclos': []}
            
            for ciclo in reversed(ciclos_alvo):  # Analisa do mais recente para o mais antigo
                dados_numero = self.dados_ciclos[
                    (self.dados_ciclos['ciclo'] == ciclo) & 
                    (self.dados_ciclos['numero'] == numero)
                ]
                
                if len(dados_numero) > 0:
                    qtd_sorteados = dados_numero.iloc[0]['qtd_sorteados']
                    
                    if qtd_sorteados > 0:  # Número saiu no ciclo
                        sequencia_atual['tamanho'] += 1
                        sequencia_atual['ciclos'].append(ciclo)
                    else:
                        break  # Sequência quebrada
                else:
                    break
            
            if sequencia_atual['tamanho'] >= self.config_ia['janela_sequencia_min']:
                sequencias_ativas[numero] = sequencia_atual
                
                # Verifica se é a maior sequência
                if sequencia_atual['tamanho'] > maior_sequencia['tamanho']:
                    maior_sequencia = {
                        'numero': numero,
                        'tamanho': sequencia_atual['tamanho'],
                        'ciclos': sequencia_atual['ciclos']
                    }
        
        # Atualiza sequência dominante
        if maior_sequencia['numero'] is not None:
            self.sequencia_dominante = maior_sequencia
            self.janela_atual = maior_sequencia['tamanho']
            self.janela_inicial = min(maior_sequencia['ciclos']) if maior_sequencia['ciclos'] else 0
        
        print(f"🏆 SEQUÊNCIA DOMINANTE:")
        if self.sequencia_dominante['numero']:
            print(f"   Número {self.sequencia_dominante['numero']}: {self.sequencia_dominante['tamanho']} ciclos seguidos")
            print(f"   Janela atual: {self.janela_atual} | Ciclo inicial: {self.janela_inicial}")
        else:
            print("   Nenhuma sequência dominante encontrada")
        
        print(f"\n🔥 SEQUÊNCIAS ATIVAS (3+ ciclos):")
        for numero, seq in sorted(sequencias_ativas.items(), key=lambda x: x[1]['tamanho'], reverse=True):
            print(f"   Número {numero}: {seq['tamanho']} ciclos - {seq['ciclos']}")
        
        return {
            'sequencia_dominante': self.sequencia_dominante,
            'sequencias_ativas': sequencias_ativas,
            'janela_atual': self.janela_atual
        }
    
    def detectar_movimentacoes(self, ciclos_comparacao: int = 5) -> Dict:
        """
        MÓDULO 3: Detector de Movimentações
        Identifica subidas/descidas entre faixas
        """
        if not self.dados_carregados:
            return {}
        
        print(f"📈 Detectando movimentações nos últimos {ciclos_comparacao} ciclos...")
        
        ciclos_disponiveis = sorted(self.dados_ciclos['ciclo'].unique())
        ciclos_analise = ciclos_disponiveis[-ciclos_comparacao:]
        
        movimentacoes = {
            'subidas': defaultdict(list),      # número -> [ciclos onde subiu]
            'descidas': defaultdict(list),     # número -> [ciclos onde desceu]  
            'estabilidade': defaultdict(list), # número -> [ciclos onde ficou igual]
            'transicoes': []                   # histórico detalhado
        }
        
        # Analisa transições entre ciclos consecutivos
        for i in range(1, int(int(len(ciclos_analise)):
            ciclo_anterior = ciclos_analise[i-1]
            ciclo_atual = ciclos_analise[i]
            
            print(f"   🔄 Analisando transição: {ciclo_anterior} → {ciclo_atual}")
            
            for numero in range(int(1)), 26):
                # Busca posição no ciclo anterior
                dados_anterior = self.dados_ciclos[
                    (self.dados_ciclos['ciclo'] == ciclo_anterior) & 
                    (self.dados_ciclos['numero'] == numero)
                ]
                
                # Busca posição no ciclo atual
                dados_atual = self.dados_ciclos[
                    (self.dados_ciclos['ciclo'] == ciclo_atual) & 
                    (self.dados_ciclos['numero'] == numero)
                ]
                
                if len(dados_anterior) > 0 and len(dados_atual) > 0:
                    qtd_anterior = dados_anterior.iloc[0]['qtd_sorteados']
                    qtd_atual = dados_atual.iloc[0]['qtd_sorteados']
                    
                    faixa_anterior = self.classificar_numero_em_faixa(qtd_anterior)
                    faixa_atual = self.classificar_numero_em_faixa(qtd_atual)
                    
                    # Registra transição
                    transicao = {
                        'numero': numero,
                        'ciclo_origem': ciclo_anterior,
                        'ciclo_destino': ciclo_atual,
                        'faixa_origem': faixa_anterior,
                        'faixa_destino': faixa_atual,
                        'movimento': 'estavel'
                    }
                    
                    # Determina tipo de movimento
                    ordem_faixas = ['0_acertos', '1_acerto', '2_acertos', '3_acertos', '4_ou_mais']
                    pos_anterior = ordem_faixas.index(faixa_anterior)
                    pos_atual = ordem_faixas.index(faixa_atual)
                    
                    if pos_atual > pos_anterior:
                        transicao['movimento'] = 'subida'
                        movimentacoes['subidas'][numero].append(ciclo_atual)
                    elif pos_atual < pos_anterior:
                        transicao['movimento'] = 'descida'
                        movimentacoes['descidas'][numero].append(ciclo_atual)
                    else:
                        movimentacoes['estabilidade'][numero].append(ciclo_atual)
                    
                    movimentacoes['transicoes'].append(transicao)
        
        # Analisa padrões de movimentação
        print(f"\n📊 ANÁLISE DE MOVIMENTAÇÕES:")
        
        # Top números que mais sobem
        subidas_freq = {num: len(ciclos) for num, ciclos in movimentacoes['subidas'].items()}
        top_subidas = sorted(subidas_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"   📈 Top Subidas: {top_subidas}")
        
        # Top números que mais descem
        descidas_freq = {num: len(ciclos) for num, ciclos in movimentacoes['descidas'].items()}
        top_descidas = sorted(descidas_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"   📉 Top Descidas: {top_descidas}")
        
        # Números mais estáveis
        estabilidade_freq = {num: len(ciclos) for num, ciclos in movimentacoes['estabilidade'].items()}
        top_estabilidade = sorted(estabilidade_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"   ⚖️ Mais Estáveis: {top_estabilidade}")
        
        return movimentacoes
    
    def treinar_modelo_predicao(self, movimentacoes: Dict) -> bool:
        """Treina modelo de IA para predição de transições"""
        print("🧠 Treinando modelo de IA para predição de transições...")
        
        if not movimentacoes['transicoes']:
            print("❌ Sem dados de transições para treinar")
            return False
        
        # Prepara features e targets
        features = []
        targets = []
        
        for transicao in movimentacoes['transicoes']:
            # Features: [numero, faixa_origem_index, ciclo_origem_normalizado]
            ordem_faixas = ['0_acertos', '1_acerto', '2_acertos', '3_acertos', '4_ou_mais']
            faixa_origem_idx = ordem_faixas.index(transicao['faixa_origem'])
            
            feature = [
                transicao['numero'],
                faixa_origem_idx,
                transicao['ciclo_origem'] % 1000,  # Normaliza ciclo
            ]
            
            # Target: index da faixa destino
            faixa_destino_idx = ordem_faixas.index(transicao['faixa_destino'])
            
            features.append(feature)
            targets.append(faixa_destino_idx)
        
        # Converte para arrays numpy
        X = np.array(features)
        y = np.array(targets)
        
        if len(X) < 50:  # Poucos dados para treinar
            print(f"⚠️ Poucos dados para treinar IA ({len(X)} amostras)")
            return False
        
        try:
            # Normaliza features
            X_scaled = self.scaler_features.fit_transform(X)
            
            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.3, random_state=42
            )
            
            # Treina modelo classificação
            self.modelo_transicoes = MLPClassifier(
                hidden_layer_sizes=(20, 15, 10),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42
            )
            
            self.modelo_transicoes.fit(X_train, y_train)
            
            # Avalia modelo
            y_pred = self.modelo_transicoes.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ Modelo treinado com {len(X)} amostras")
            print(f"   📊 Acurácia: {accuracy:.3f}")
            
            if accuracy > 0.25:  # 🚀 OTIMIZAÇÃO 1: Threshold reduzido (0.4 → 0.25) para aceitar mais modelos
                print("🎯 Modelo aprovado para uso!")
                return True
            else:
                print("⚠️ Acurácia baixa - usando probabilidades empíricas")
                return False
                
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
            return False
    
    def predizer_proxima_faixa(self, ciclo_atual: int = None) -> Dict[int, Dict]:
        """
        MÓDULO 4: Preditor de Próxima Faixa
        Prevê onde cada número estará no próximo ciclo
        """
        if not self.dados_carregados:
            return {}
        
        if ciclo_atual is None:
            ciclo_atual = self.dados_ciclos['ciclo'].max()
        
        print(f"🔮 Predizendo próximas faixas baseado no ciclo {ciclo_atual}...")
        
        # Analisa configuração atual
        piramide_atual = self.analisar_piramide_atual(ciclo_atual)
        predicoes = {}
        
        ordem_faixas = ['0_acertos', '1_acerto', '2_acertos', '3_acertos', '4_ou_mais']
        
        for numero in range(1, 26:
            # Encontra faixa atual do número
            faixa_atual = None
            for faixa), int(numeros in piramide_atual.items():
                if numero in numeros:
                    faixa_atual = faixa
                    break
            
            if faixa_atual is None:
                continue
            
            # Predição usando IA (se modelo disponível)
            predicao_ia = None
            confianca_ia = 0.0
            
            if self.modelo_transicoes is not None:
                try:
                    faixa_atual_idx = ordem_faixas.index(faixa_atual)
                    feature = np.array([[numero, faixa_atual_idx, ciclo_atual % 1000]])
                    feature_scaled = self.scaler_features.transform(feature)
                    
                    # Predição da próxima faixa
                    faixa_pred_idx = self.modelo_transicoes.predict(feature_scaled)[0]
                    
                    # Probabilidades de cada faixa
                    probas = self.modelo_transicoes.predict_proba(feature_scaled)[0]
                    confianca_ia = np.max(probas)
                    
                    predicao_ia = {
                        'faixa_prevista': ordem_faixas[faixa_pred_idx],
                        'confianca': confianca_ia,
                        'probabilidades': dict(zip(ordem_faixas, probas))
                    }
                    
                except Exception as e:
                    print(f"⚠️ Erro na predição IA para número {numero}: {e}")
            
            # Predição empírica baseada nas probabilidades conhecidas
            prob_sair = self.config_ia['probabilidades_empiricas'].get(faixa_atual, 0.5)
            
            predicao_empirica = {
                'faixa_prevista': self._predizer_empiricamente(faixa_atual, prob_sair),
                'confianca': prob_sair,
                'probabilidade_sair': prob_sair
            }
            
            # Combina predições
            predicoes[numero] = {
                'faixa_atual': faixa_atual,
                'predicao_ia': predicao_ia,
                'predicao_empirica': predicao_empirica,
                'predicao_final': predicao_ia['faixa_prevista'] if predicao_ia and confianca_ia > 0.35 else predicao_empirica['faixa_prevista'],  # 🚀 OTIMIZAÇÃO 2: Confiança reduzida (0.6 → 0.35)
                'confianca_final': max(confianca_ia, prob_sair) if predicao_ia else prob_sair
            }
        
        # Mostra resumo das predições
        print(f"\n📊 PREDIÇÕES PARA PRÓXIMO CICLO:")
        
        # Agrupa por faixa prevista
        por_faixa_prevista = defaultdict(list)
        for numero, pred in predicoes.items():
            por_faixa_prevista[pred['predicao_final']].append(numero)
        
        for faixa, numeros in por_faixa_prevista.items():
            print(f"   {faixa.replace('_', ' ').title()}: {sorted(numeros)} ({len(numeros)} números)")
        
        return predicoes
    
    def _predizer_empiricamente(self, faixa_atual: str, prob_sair: float) -> str:
        """🚀 OTIMIZAÇÃO 4: Prediz próxima faixa com lógica mais distribuída"""
        
        # Lógica empírica otimizada para dispersar melhor a distribuição
        if faixa_atual == '0_acertos':
            # 85% chance de sair (menos que antes para evitar concentração)
            if np.random.random() < prob_sair:
                return np.random.choice(['1_acerto', '2_acertos'], p=[int(0.7, 0.3)])  # Variação na saída
            else:
                return '0_acertos'
        
        elif faixa_atual == '1_acerto':
            # 75% chance de sair (mais agressivo)
            if np.random.random() < prob_sair:
                return np.random.choice(['2_acertos', '3_acertos'], p=[int(0.6, 0.4)])  # Mais para 3_acertos
            else:
                return np.random.choice(['0_acertos', '1_acerto'], p=[int(0.6, 0.4)])  # Alguns voltam
        
        elif faixa_atual == '2_acertos':
            # 40% chance de sair (MENOS que antes para reduzir concentração)
            if np.random.random() < prob_sair:
                return np.random.choice(['3_acertos', '1_acerto', '0_acertos'], p=[int(0.5, 0.3, 0.2)])  # Distribuição variada
            else:
                return '2_acertos'  # 60% fica (mantém alguns na faixa)
        
        elif faixa_atual == '3_acertos':
            # 75% chance de sair (mais agressivo para não acumular)
            if np.random.random() < prob_sair:
                return np.random.choice(['4_ou_mais', '2_acertos', '1_acerto'], p=[int(0.4, 0.4, 0.2)])  # Distribui melhor
            else:
                return '3_acertos'  # 25% fica
        
        else:  # 4_ou_mais
            # 60% chance de sair (mais que antes)
            if np.random.random() < prob_sair:
                return np.random.choice(['3_acertos', '2_acertos', '1_acerto'], p=[int(0.4, 0.4, 0.2)])  # Distribui melhor a descida
            else:
                return '4_ou_mais'  # 40% mantém
    
    def gerar_baseado_transicoes(self, qtd_numeros: int = 15, quantidade: int = 10) -> List[List[int]]:
        """
        MÓDULO 5: Gerador Baseado em Transições COM FILTRO VALIDADO
        Usa movimentações para gerar combinações
        """
        print(f"\n🔺🎯 GERADOR BASEADO EM TRANSIÇÕES DA PIRÂMIDE")
        print("=" * 60)
        
        # 🎯 Mostra status do filtro validado
        if self.usar_filtro_validado:
            print(f"🎯 FILTRO VALIDADO: ATIVO ({self.min_acertos_filtro}-{self.max_acertos_filtro} acertos)")
        else:
            print(f"⚠️ FILTRO VALIDADO: DESATIVADO")
        
        # 1. Analisa configuração atual
        piramide_atual = self.analisar_piramide_atual()
        
        # 2. Monitora sequências
        sequencias = self.monitorar_sequencias()
        
        # 3. Detecta movimentações
        movimentacoes = self.detectar_movimentacoes()
        
        # 4. Treina modelo (se possível)
        modelo_ok = self.treinar_modelo_predicao(movimentacoes)
        
        # 5. Prediz próximas faixas
        predicoes = self.predizer_proxima_faixa()
        
        print(f"\n🎲 Gerando {quantidade} combinações com {qtd_numeros} números...")
        
        combinacoes = []
        combinacoes_set = set()
        
        for tentativa in range(int(int(int(quantidade * 3):  # Máximo de tentativas
            if len(combinacoes) >= quantidade:
                break
            
            combinacao = self._gerar_combinacao_piramide(
                piramide_atual)), int(int(predicoes), int(sequencias, qtd_numeros
            )))
            
            combinacao_tuple = tuple(sorted(combinacao))
            
            if combinacao_tuple not in combinacoes_set:
                combinacoes.append(combinacao)
                combinacoes_set.add(combinacao_tuple)
        
        print(f"✅ Geradas {len(combinacoes)} combinações baseadas na pirâmide!")
        
        # 🎯 ANÁLISE DO FILTRO VALIDADO (se ativo)
        if self.usar_filtro_validado and combinacoes:
            self._analisar_filtro_combinacoes_piramide(combinacoes)
        
        return combinacoes
    
    def _gerar_combinacao_piramide(self, piramide: Dict, predicoes: Dict, 
                                 sequencias: Dict, qtd_numeros: int) -> List[int]:
        """🔺🎯 Gera uma combinação baseada na análise da pirâmide COM FILTRO VALIDADO"""
        
        # 🎯 GERAÇÃO COM FILTRO VALIDADO
        max_tentativas = 500  # Reduzido para evitar loop muito longo
        tentativas = 0
        
        while tentativas < max_tentativas:
            tentativas += 1
            combinacao = []
            numeros_disponiveis = list(range(1, 26)
            
            # 1. Prioriza números que devem SAIR das faixas baixas (0 e 1 acerto)
            numeros_prioridade = []
            
            for numero in piramide.get('0_acertos'), int([]):
                if numero in predicoes:
                    pred = predicoes[numero]
                    if pred['predicao_final'] != '0_acertos':  # Vai sair da faixa 0
                        numeros_prioridade.append((numero, pred['confianca_final']))
            
            for numero in piramide.get('1_acerto', []):
                if numero in predicoes:
                    pred = predicoes[numero]
                    if pred['predicao_final'] not in ['0_acertos', '1_acerto']:  # Vai subir
                        numeros_prioridade.append((numero, pred['confianca_final']))
            
            # Ordena por confiança mas introduz randomização
            numeros_prioridade.sort(key=lambda x: x[1], reverse=True)
            
            # 🔄 MELHORIA: Variação na quantidade de números prioritários
            qtd_prioridade_base = min(len(numeros_prioridade), qtd_numeros // 3)
            # Varia entre 60% e 100% da quantidade base para criar diversidade
            qtd_prioridade = max(1, int(qtd_prioridade_base * np.random.uniform(0.6, 1.0)))
            qtd_prioridade = min(qtd_prioridade, len(numeros_prioridade))
            
            # 🎲 RANDOMIZAÇÃO: Não sempre os top números, mas com peso probabilístico
            if len(numeros_prioridade) > 0:
                pesos_prioridade = [x[1] for x in numeros_prioridade]
                total_peso = sum(pesos_prioridade)
                if total_peso > 0:
                    probabilidades = [p / total_peso for p in pesos_prioridade]
                    # Seleciona com probabilidade baseada na confiança
                    indices_selecionados = np.random.choice(
                        len(numeros_prioridade), 
                        size=min(qtd_prioridade, len(numeros_prioridade)), 
                        replace=False, 
                        p=probabilidades
                    )
                    for idx in indices_selecionados:
                        numero = numeros_prioridade[idx][0]
                        if numero in numeros_disponiveis:
                            combinacao.append(numero)
                            numeros_disponiveis.remove(numero)
            
            # 2. 🎲 Inclui números da sequência dominante (com probabilidade, não sempre)
            if sequencias.get('sequencia_dominante', {}).get('numero'):
                numero_seq = sequencias['sequencia_dominante']['numero']
                tamanho_seq = sequencias['sequencia_dominante'].get('tamanho', 0)
                # Probabilidade baseada no tamanho da sequência
                prob_incluir_seq = min(0.8, tamanho_seq / 10.0)  # Máx 80% de chance
                
                if (numero_seq in numeros_disponiveis and 
                    len(combinacao) < qtd_numeros - 3 and
                    np.random.random() < prob_incluir_seq):
                    combinacao.append(numero_seq)
                    numeros_disponiveis.remove(numero_seq)
            
            # 3. 🔄 Balanceia com números de diferentes faixas COM RANDOMIZAÇÃO
            faixas_para_balancear = ['2_acertos', '3_acertos', '4_ou_mais']
            
            for faixa in faixas_para_balancear:
                numeros_faixa = [n for n in piramide.get(faixa, []) if n in numeros_disponiveis]
                
                if len(numeros_faixa) == 0:
                    continue
                    
                # 🔄 Quantidade variável baseada na faixa e com randomização
                if faixa == '2_acertos':
                    qtd_base = qtd_numeros // 4  # ~25%
                elif faixa == '3_acertos':
                    qtd_base = qtd_numeros // 3  # ~33%
                else:  # 4_ou_mais
                    qtd_base = max(1, qtd_numeros // 6)  # ~16%
                
                # 🎲 Varia a quantidade entre 50% e 150% do valor base
                variacao = np.random.uniform(0.5, 1.5)
                qtd_faixa = max(1, min(len(numeros_faixa), int(qtd_base * variacao)))
                qtd_faixa = min(qtd_faixa, qtd_numeros - len(combinacao))
                
                if qtd_faixa <= 0:
                    continue
                
                # 🎲 Seleção probabilística baseada nas predições
                pesos_faixa = []
                for numero in numeros_faixa:
                    if numero in predicoes:
                        peso_base = predicoes[numero]['confianca_final']
                    else:
                        peso_base = 0.5
                    
                    # Adiciona ruído aleatório para criar variação
                    peso_final = peso_base + np.random.uniform(-0.2, 0.2)
                    peso_final = max(0.1, min(1.0, peso_final))  # Mantém entre 0.1 e 1.0
                    pesos_faixa.append(peso_final)
                
                # Seleciona números com probabilidade baseada nos pesos
                total_peso_faixa = sum(pesos_faixa)
                if total_peso_faixa > 0:
                    probabilidades_faixa = [p / total_peso_faixa for p in pesos_faixa]
                    
                    try:
                        indices_selecionados = np.random.choice(
                            len(numeros_faixa),
                            size=min(qtd_faixa, len(numeros_faixa)),
                            replace=False,
                            p=probabilidades_faixa
                        )
                        
                        for idx in indices_selecionados:
                            if len(combinacao) >= qtd_numeros:
                                break
                            numero = numeros_faixa[idx]
                            if numero in numeros_disponiveis:
                                combinacao.append(numero)
                                numeros_disponiveis.remove(numero)
                    except ValueError:
                        # Fallback para seleção aleatória simples se houver erro
                        numeros_selecionados = np.random.choice(
                            numeros_faixa, 
                            size=min(qtd_faixa, len(numeros_faixa)), 
                            replace=False
                        )
                        for numero in numeros_selecionados:
                            if len(combinacao) >= qtd_numeros:
                                break
                            if numero in numeros_disponiveis:
                                combinacao.append(numero)
                                numeros_disponiveis.remove(numero)
            
            # 4. 🎲 Completa aleatoriamente se necessário (com pesos opcionais)
            while len(combinacao) < qtd_numeros and numeros_disponiveis:
                # Para números restantes, aplica pequeno peso baseado na posição
                if len(numeros_disponiveis) > 1:
                    # Números menores têm ligeiro peso maior (tendência lotofácil)
                    pesos_restantes = [max(0.3, 1.0 - (n-1) / 25.0) for n in numeros_disponiveis]
                    total_peso_restante = sum(pesos_restantes)
                    if total_peso_restante > 0:
                        probabilidades_restantes = [p / total_peso_restante for p in pesos_restantes]
                        numero_aleatorio = np.random.choice(numeros_disponiveis, p=probabilidades_restantes)
                    else:
                        numero_aleatorio = np.random.choice(numeros_disponiveis)
                else:
                    numero_aleatorio = numeros_disponiveis[0]
                    
                combinacao.append(numero_aleatorio)
                numeros_disponiveis.remove(numero_aleatorio)
            
            # 🎯 VALIDAÇÃO COM FILTRO
            combinacao_final = sorted(combinacao[:qtd_numeros])
            
            if self.validar_combinacao_filtro(combinacao_final):
                return combinacao_final
            
            # Se chegou aqui, a combinação não passou no filtro
            if tentativas % 100 == 0:  # Log a cada 100 tentativas
                acertos = self.calcular_acertos_filtros(combinacao_final)
                print(f"   🔺🔍 Tentativa {tentativas}: Rejeitada (J1:{acertos['jogo_1']}, J2:{acertos['jogo_2']})")
        
        # Se esgotaram as tentativas, retorna a última gerada (mesmo que não passe no filtro)
        print(f"   ⚠️ Máximo de tentativas atingido ({max_tentativas}). Retornando combinação sem filtro.")
        return sorted(combinacao[:qtd_numeros])
    
    def salvar_combinacoes_piramide(self, combinacoes: List[List[int]], qtd_numeros: int, nome_arquivo: str = None) -> str:
        """🔺 Salva combinações geradas pela pirâmide invertida"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_piramide_{qtd_numeros}nums_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🔺 COMBINAÇÕES PIRÂMIDE INVERTIDA DINÂMICA\n")
                f.write("=" * 65 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                
                # Detecta o ciclo atual pelos dados carregados
                if hasattr(self, 'dados_ciclos') and not self.dados_ciclos.empty:
                    ciclo_max = self.dados_ciclos['ciclo'].max()
                    f.write(f"Base atualizada até o ciclo: {ciclo_max}\n\n")
                else:
                    f.write("Base de dados: Carregada dinamicamente\n\n")
                
                # Configuração da aposta
                custos = {
                    15: 3.50, 16: 56.00, 17: 476.00, 
                    18: 2856.00, 19: 13566.00, 20: 54264.00
                }
                custo_unitario = custos.get(qtd_numeros, 0)
                
                f.write("💰 CONFIGURAÇÃO DA APOSTA:\n")
                f.write("-" * 35 + "\n")
                f.write(f"• Números por jogo: {qtd_numeros}\n")
                f.write(f"• Custo unitário: R$ {custo_unitario:.2f}\n")
                f.write(f"• Total de jogos: {len(combinacoes)}\n")
                f.write(f"• Investimento total: R$ {custo_unitario * len(combinacoes):.2f}\n\n")
                
                # Metodologia da pirâmide
                f.write("🔺 METODOLOGIA PIRÂMIDE INVERTIDA:\n")
                f.write("-" * 40 + "\n")
                f.write("• Análise das faixas de acertos (0, 1, 2, 3, 4+ acertos)\n")
                f.write("• IA treinada para predizer transições entre faixas\n")
                f.write("• Priorização de números saindo das faixas baixas\n")
                f.write("• Balanceamento inteligente por todas as faixas\n")
                f.write("• Integração com sequências dominantes detectadas\n\n")
                
                # Configuração atual da pirâmide (calculada na hora)
                try:
                    piramide_atual = self.analisar_piramide_atual()
                    if piramide_atual:
                        f.write("📊 CONFIGURAÇÃO ATUAL DA PIRÂMIDE:\n")
                        f.write("-" * 40 + "\n")
                        for faixa, numeros in piramide_atual.items():
                            if numeros:
                                f.write(f"   {faixa.replace('_', ' ').title()}: {numeros} ({len(numeros)})\n")
                        f.write("\n")
                except Exception as e:
                    f.write(f"   ⚠️ Análise da pirâmide não disponível: {e}\n\n")
                
                # Sequência dominante
                if hasattr(self, 'sequencia_dominante') and self.sequencia_dominante.get('numero'):
                    f.write(f"🏆 SEQUÊNCIA DOMINANTE:\n")
                    f.write(f"   Número {self.sequencia_dominante['numero']}: {self.sequencia_dominante['tamanho']} ciclos\n\n")
                
                # Status do modelo IA
                f.write(f"🧠 SISTEMA DE IA:\n")
                if hasattr(self, 'modelo_transicoes') and self.modelo_transicoes:
                    f.write("   ✅ Modelo neural network treinado e ativo\n")
                else:
                    f.write("   ⚠️ Usando probabilidades empíricas (modelo não treinado)\n")
                
                f.write(f"\n🎯 TOTAL DE COMBINAÇÕES: {len(combinacoes)}\n")
                f.write("=" * 65 + "\n\n")
                
                # Salva as combinações (formato detalhado)
                f.write("📋 COMBINAÇÕES DETALHADAS:\n")
                f.write("-" * 30 + "\n")
                for i, combinacao in enumerate(combinacoes, 1):
                    combinacao_ordenada = sorted(combinacao)
                    f.write(f"Jogo {i:2d}: {','.join(map(str, combinacao_ordenada))}\n")
                
                # ✨ CHAVE DE OURO: Todas as combinações apenas separadas por vírgula
                f.write("\n" + "🗝️" * 15 + " CHAVE DE OURO " + "🗝️" * 15 + "\n")
                f.write("TODAS AS COMBINAÇÕES (formato compacto):\n")
                f.write("-" * 50 + "\n")
                
                for combinacao in combinacoes:
                    combinacao_str = ','.join(map(str, sorted(combinacao)))
                    f.write(f"{combinacao_str}\n")
                
                f.write("\n" + "🗝️" * 45 + "\n")
                f.write("🔺 Sistema Pirâmide Invertida Dinâmica - AR CALHAU\n")
            
            print(f"✅ Combinações salvas: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar combinações: {e}")
            return ""

    def salvar_analise_completa(self, nome_arquivo: str = None) -> str:
        """Salva análise completa da pirâmide"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"analise_piramide_invertida_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🔺 ANÁLISE COMPLETA - PIRÂMIDE INVERTIDA DINÂMICA\n")
                f.write("=" * 70 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                # Análise atual
                piramide_atual = self.analisar_piramide_atual()
                f.write("📊 CONFIGURAÇÃO ATUAL DA PIRÂMIDE:\n")
                f.write("-" * 45 + "\n")
                for faixa, numeros in piramide_atual.items():
                    f.write(f"{faixa.replace('_', ' ').title()}: {numeros} ({len(numeros)} números)\n")
                
                # Sequências
                f.write(f"\n🏆 SEQUÊNCIA DOMINANTE:\n")
                f.write("-" * 25 + "\n")
                if self.sequencia_dominante['numero']:
                    f.write(f"Número {self.sequencia_dominante['numero']}: {self.sequencia_dominante['tamanho']} ciclos seguidos\n")
                    f.write(f"Janela atual: {self.janela_atual} | Ciclo inicial: {self.janela_inicial}\n")
                else:
                    f.write("Nenhuma sequência dominante encontrada\n")
                
                # Predições
                predicoes = self.predizer_proxima_faixa()
                f.write(f"\n🔮 PREDIÇÕES PARA PRÓXIMO CICLO:\n")
                f.write("-" * 40 + "\n")
                
                por_faixa_prevista = defaultdict(list)
                for numero, pred in predicoes.items():
                    por_faixa_prevista[pred['predicao_final']].append(numero)
                
                for faixa, numeros in por_faixa_prevista.items():
                    f.write(f"{faixa.replace('_', ' ').title()}: {sorted(numeros)} ({len(numeros)} números)\n")
                
                f.write(f"\n" + "=" * 70 + "\n")
                f.write("Sistema desenvolvido por AR CALHAU - Agosto 2025\n")
            
            print(f"✅ Análise salva: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar análise: {e}")
            return ""
    
    def _analisar_filtro_combinacoes_piramide(self, combinacoes: List[List[int]]):
        """🔺🎯 Analisa como o filtro validado afetou as combinações da pirâmide"""
        print(f"\n🔺🎯 ANÁLISE DO FILTRO VALIDADO NA PIRÂMIDE:")
        print("-" * 55)
        
        total_combinacoes = len(combinacoes)
        combinacoes_aprovadas_j1 = 0
        combinacoes_aprovadas_j2 = 0
        combinacoes_aprovadas_ambos = 0
        total_acertos_j1 = []
        total_acertos_j2 = []
        
        # Conta números dos jogos validados que aparecem
        numeros_j1_usados = set()
        numeros_j2_usados = set()
        
        for combinacao in combinacoes:
            acertos = self.calcular_acertos_filtros(combinacao)
            total_acertos_j1.append(acertos['jogo_1'])
            total_acertos_j2.append(acertos['jogo_2'])
            
            valido_j1 = self.min_acertos_filtro <= acertos['jogo_1'] <= self.max_acertos_filtro
            valido_j2 = self.min_acertos_filtro <= acertos['jogo_2'] <= self.max_acertos_filtro
            
            if valido_j1:
                combinacoes_aprovadas_j1 += 1
            if valido_j2:
                combinacoes_aprovadas_j2 += 1
            if valido_j1 and valido_j2:
                combinacoes_aprovadas_ambos += 1
            
            # Conta números usados
            comb_set = set(combinacao)
            numeros_j1_usados.update(comb_set.intersection(set(self.filtros_validados['jogo_1'])))
            numeros_j2_usados.update(comb_set.intersection(set(self.filtros_validados['jogo_2'])))
        
        print(f"   📊 Filtro configurado: {self.min_acertos_filtro}-{self.max_acertos_filtro} acertos")
        print(f"   ✅ Aprovadas pelo Jogo 1: {combinacoes_aprovadas_j1}/{total_combinacoes} ({combinacoes_aprovadas_j1/total_combinacoes*100:.1f}%)")
        print(f"   ✅ Aprovadas pelo Jogo 2: {combinacoes_aprovadas_j2}/{total_combinacoes} ({combinacoes_aprovadas_j2/total_combinacoes*100:.1f}%)")
        print(f"   🏆 Aprovadas por AMBOS: {combinacoes_aprovadas_ambos}/{total_combinacoes} ({combinacoes_aprovadas_ambos/total_combinacoes*100:.1f}%)")
        
        if total_acertos_j1:
            media_j1 = np.mean(total_acertos_j1)
            media_j2 = np.mean(total_acertos_j2)
            print(f"   📈 Média de acertos - Jogo 1: {media_j1:.1f} | Jogo 2: {media_j2:.1f}")
            print(f"   📊 Distribuição Jogo 1: Min={min(total_acertos_j1)} | Max={max(total_acertos_j1)}")
            print(f"   📊 Distribuição Jogo 2: Min={min(total_acertos_j2)} | Max={max(total_acertos_j2)}")
        
        print(f"   🎮 Números do Jogo 1 utilizados: {len(numeros_j1_usados)}/20")
        print(f"   🎮 Números do Jogo 2 utilizados: {len(numeros_j2_usados)}/20")
        
        # Mostra números mais usados dos jogos validados
        contador_numeros = Counter()
        for combinacao in combinacoes:
            contador_numeros.update(combinacao)
        
        print(f"\n🔺🔥 TOP 10 NÚMEROS MAIS USADOS (com indicador de filtro):")
        for numero, freq in contador_numeros.most_common(10):
            percent = (freq / total_combinacoes) * 100
            no_jogo1 = "J1" if numero in self.filtros_validados['jogo_1'] else "  "
            no_jogo2 = "J2" if numero in self.filtros_validados['jogo_2'] else "  "
            print(f"      {numero:2d}: {freq:2d}x ({percent:4.1f}%) [{no_jogo1}{no_jogo2}]")

def main():
    """Função principal do sistema"""
    print("🔺 SISTEMA PIRÂMIDE INVERTIDA DINÂMICA")
    print("=" * 55)
    print("🧠 Análise de movimentações entre faixas com IA")
    print()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    piramide = PiramideInvertidaDinamica()
    
    # 🚀 Mostra as otimizações aplicadas
    piramide.mostrar_otimizacoes_aplicadas()
    
    try:
        print("\n🎮 MENU DE OPÇÕES:")
        print("1. Análise completa da pirâmide atual")
        print("2. Gerar combinações baseadas nas transições")
        print("3. Salvar análise detalhada")
        print("4. Executar análise completa com combinações")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            # Análise completa
            piramide.analisar_piramide_atual()
            piramide.monitorar_sequencias()
            movimentacoes = piramide.detectar_movimentacoes()
            piramide.treinar_modelo_predicao(movimentacoes)
            piramide.predizer_proxima_faixa()
            
        elif opcao == "2":
            # Gerar combinações
            qtd_numeros = int(input("Quantos números por jogo (15-20): ") or "15")
            quantidade = int(input("Quantas combinações gerar: ") or "10")
            
            combinacoes = piramide.gerar_baseado_transicoes(qtd_numeros, quantidade)
            
            print(f"\n📋 COMBINAÇÕES GERADAS:")
            print("-" * 40)
            for i, comb in enumerate(combinacoes, 1):
                print(f"Jogo {i:2d}: {','.join(map(str, comb))}")
            
            # Pergunta se quer salvar
            salvar = input(f"\nSalvar {len(combinacoes)} combinações? (s/n): ").lower()
            if salvar.startswith('s'):
                nome_arquivo = piramide.salvar_combinacoes_piramide(combinacoes, qtd_numeros)
                if nome_arquivo:
                    print(f"📁 Combinações salvas em: {nome_arquivo}")
            
        elif opcao == "3":
            # Salvar análise
            nome_arquivo = piramide.salvar_analise_completa()
            if nome_arquivo:
                print(f"📁 Arquivo salvo: {nome_arquivo}")
            
        elif opcao == "4":
            # Execução completa
            qtd_numeros = int(input("Quantos números por jogo (15-20): ") or "15")
            quantidade = int(input("Quantas combinações gerar: ") or "10")
            
            # Executa análise completa
            combinacoes = piramide.gerar_baseado_transicoes(qtd_numeros, quantidade)
            
            # Mostra resultados
            print(f"\n📋 COMBINAÇÕES BASEADAS NA PIRÂMIDE:")
            print("-" * 50)
            for i, comb in enumerate(combinacoes, 1):
                print(f"Jogo {i:2d}: {','.join(map(str, comb))}")
            
            # Pergunta se quer salvar combinações
            salvar_combinacoes = input(f"\nSalvar {len(combinacoes)} combinações? (s/n): ").lower()
            nome_arquivo_combinacoes = None
            if salvar_combinacoes.startswith('s'):
                nome_arquivo_combinacoes = piramide.salvar_combinacoes_piramide(combinacoes, qtd_numeros)
            
            # Pergunta se quer salvar análise
            salvar_analise = input("Salvar análise detalhada? (s/n): ").lower()
            nome_arquivo_analise = None
            if salvar_analise.startswith('s'):
                nome_arquivo_analise = piramide.salvar_analise_completa()
            
            print(f"\n✅ Processo completo finalizado!")
            if nome_arquivo_combinacoes:
                print(f"📁 Combinações salvas em: {nome_arquivo_combinacoes}")
            if nome_arquivo_analise:
                print(f"📁 Análise salva em: {nome_arquivo_analise}")
            
        else:
            print("❌ Opção inválida")
            
    except ValueError:
        print("❌ Valor inválido inserido")
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()


# =============================================================================
# FUNÇÃO OTIMIZADA COM INTELIGÊNCIA N12
# =============================================================================

@aplicar_inteligencia_n12
def gerador_otimizado_n12(quantidade=30):
    """
    Versão otimizada do piramide_invertida_dinamica com inteligência N12 aplicada
    
    Esta função usa o gerador original mas aplica automaticamente
    os filtros inteligentes baseados na teoria N12 comprovada.
    """
    print(f"🧠 {nome_base.upper()} COM INTELIGÊNCIA N12")
    print("="*50)
    
    # Usar geração inteligente nativa para máximos resultados
    combinacoes = gerar_combinacoes_inteligentes_n12(quantidade)
    
    print(f"✅ {len(combinacoes)} combinações otimizadas geradas")
    print("📊 100% alinhadas com estratégia N12 atual")
    
    return combinacoes

def executar_versao_suprema():
    """Executa a versão suprema do gerador com inteligência N12"""
    print("🏆 EXECUTANDO VERSÃO SUPREMA N12")
    print("="*60)
    
    combinacoes = gerador_otimizado_n12(30)
    
    # Salvar resultado
    nome_arquivo = f"resultado_{nome_base}_n12.txt"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"🏆 RESULTADO {nome_base.upper()} N12\n")
        f.write("="*50 + "\n")
        f.write(f"📅 Gerado em: 19/09/2025\n")
        f.write(f"🎯 Estratégia: DIVERSIFICAR_COM_ENFASE_EXTREMOS\n")
        f.write(f"📊 Combinações: {len(combinacoes)}\n")
        f.write("="*50 + "\n\n")
        
        for i, comb in enumerate(combinacoes, 1):
            n12 = comb[11]
            baixos = len([n for n in comb if 1 <= n <= 8])
            medios = len([n for n in comb if 9 <= n <= 17])
            altos = len([n for n in comb if 18 <= n <= 25])
            
            f.write(f"Jogo {i:2d}: {comb}\n")
            f.write(f"        N12={n12}, B={baixos}, M={medios}, A={altos}\n\n")
    
    print(f"💾 Resultado salvo em: {nome_arquivo}")
    return combinacoes

if __name__ == "__main__":
    executar_versao_suprema()
