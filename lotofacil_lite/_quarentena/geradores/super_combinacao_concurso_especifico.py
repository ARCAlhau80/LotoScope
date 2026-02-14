#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SUPER COMBINAÇÃO IA - CONCURSO ESPECÍFICO
Sistema híbrido que combina:
- Insights acadêmicos dinâmicos (dados atuais da base)
- Neural Network treinada (padrões históricos)
- Diversificação estratégica (conservative/aggressive/hybrid)
- Predição para concurso específico ainda não sorteado

Autor: AR CALHAU
Data: 20 de Agosto de 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import numpy as np
import pandas as pd
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import json
import pickle
import os
from datetime import datetime
from database_config import db_config
import tensorflow as tf
from tensorflow import keras
from scipy.stats import pearsonr
import statistics
import random

class SuperCombinacaoConcursoEspecifico:
    """Gerador de super-combinações para concurso específico usando IA + Insights dinâmicos"""
    
    def __init__(self):
        self.modelo_ia = None
        self.insights_dinamicos = {}
        self.pesos_academicos = {}
        self.dados_carregados = False
        self.modelo_carregado = False
        
        # Configurações por quantidade de números (igual ao sistema dinâmico)
        self.configuracoes_aposta = {
            15: {'custo': 3.50, 'prob_15_acertos': 1/3268760, 'garantia_min': 11},
            16: {'custo': 56.00, 'prob_15_acertos': 16/3268760, 'garantia_min': 12},
            17: {'custo': 476.00, 'prob_15_acertos': 136/3268760, 'garantia_min': 13},
            18: {'custo': 2856.00, 'prob_15_acertos': 816/3268760, 'garantia_min': 13},
            19: {'custo': 13566.00, 'prob_15_acertos': 4368/3268760, 'garantia_min': 14},
            20: {'custo': 54264.00, 'prob_15_acertos': 21504/3268760, 'garantia_min': 14}
        }
        
        # Configurações de diversificação
        self.estrategias_diversificacao = {
            'conservative': {'peso_ia': 0.7, 'peso_academico': 0.3, 'randomness': 0.1},
            'aggressive': {'peso_ia': 0.4, 'peso_academico': 0.6, 'randomness': 0.3},
            'hybrid': {'peso_ia': 0.5, 'peso_academico': 0.5, 'randomness': 0.2}
        }
    
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
    
    def carregar_modelo_ia(self, caminho_modelo: str = "combin_ia/modelos/modelo_super_combinacao.pkl") -> bool:
        """Carrega o modelo neural MASSIVO treinado (16.256 neurônios)"""
        try:
            if os.path.exists(caminho_modelo):
                # Carrega modelo pickle do super_combinacao_ia.py
                with open(caminho_modelo, 'rb') as f:
                    modelo_data = pickle.load(f)
                
                self.modelo_ia = modelo_data['modelo_performance']
                self.scaler_features = modelo_data['scaler_features'] 
                self.scaler_target = modelo_data['scaler_target']
                self.config_rede = modelo_data['config_rede']
                
                total_neuronios = sum(self.config_rede['hidden_layers'])
                camadas = len(self.config_rede['hidden_layers'])
                
                print(f"✅ MODELO IA MASSIVO CARREGADO:")
                print(f"   🧠 Neurônios: {total_neuronios:,}")
                print(f"   🏗️ Camadas: {camadas}")
                print(f"   🎯 Arquitetura: {self.config_rede['hidden_layers']}")
                
                self.modelo_carregado = True
                return True
            else:
                print(f"⚠️ Modelo não encontrado em {caminho_modelo}")
                print("   Execute primeiro: python super_combinacao_ia.py -> Opção 1")
                return False
        except Exception as e:
            print(f"❌ Erro ao carregar modelo IA massivo: {e}")
            return False
    
    def calcular_insights_dinamicos_completos(self) -> bool:
        """Calcula insights acadêmicos completos e atualizados"""
        print("🔍 Calculando insights acadêmicos dinâmicos completos...")
        
        conn = self.conectar_base()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 1. Busca informações do último concurso
            print("   📅 Identificando próximo concurso...")
            proximo_concurso = self._obter_proximo_concurso(cursor)
            
            # 2. Análise de padrões recentes (últimos 20 concursos)
            print("   📊 Analisando padrões dos últimos 20 concursos...")
            padroes_recentes = self._analisar_padroes_recentes(cursor, 20)
            
            # 3. Correlações temporais avançadas
            print("   📈 Calculando correlações temporais avançadas...")
            correlacoes_avancadas = self._calcular_correlacoes_avancadas(cursor)
            
            # 4. Análise de ciclos e sazonalidade
            print("   🔄 Analisando ciclos e sazonalidade...")
            analise_ciclos = self._analisar_ciclos_sazonais(cursor)
            
            # 5. Tendências de médio prazo
            print("   📊 Calculando tendências de médio prazo...")
            tendencias_medio_prazo = self._calcular_tendencias_medio_prazo(cursor)
            
            # 6. Padrões de posições
            print("   🎯 Analisando padrões de posições...")
            padroes_posicoes = self._analisar_padroes_posicoes(cursor)
            
            # Compila todos os insights
            self.insights_dinamicos = {
                'proximo_concurso': proximo_concurso,
                'padroes_recentes': padroes_recentes,
                'correlacoes_avancadas': correlacoes_avancadas,
                'analise_ciclos': analise_ciclos,
                'tendencias_medio_prazo': tendencias_medio_prazo,
                'padroes_posicoes': padroes_posicoes
            }
            
            # Calcula pesos acadêmicos finais
            self.pesos_academicos = self._calcular_pesos_academicos_avancados()
            
            self.dados_carregados = True
            print("✅ Insights dinâmicos completos calculados!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao calcular insights: {e}")
            return False
        finally:
            conn.close()
    
    def _obter_proximo_concurso(self, cursor) -> Dict:
        """Obtém informações do próximo concurso"""
        # Busca o último concurso
        query = """
        SELECT TOP 1 Concurso, Data_Sorteio
        FROM Resultados_INT
        ORDER BY Concurso DESC
        """
        
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado:
            ultimo_concurso, ultima_data = resultado
            proximo_concurso = ultimo_concurso + 1
            
            return {
                'numero': proximo_concurso,
                'ultimo_sorteado': ultimo_concurso,
                'ultima_data': ultima_data
            }
        
        return {'numero': 3200, 'ultimo_sorteado': 3199, 'ultima_data': None}
    
    def _analisar_padroes_recentes(self, cursor, qtd_concursos: int) -> Dict:
        """Analisa padrões dos últimos N concursos"""
        query = f"""
        SELECT TOP {qtd_concursos} N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        if not resultados:
            return {}
        
        # Análise de frequências
        contador_numeros = Counter()
        somas = []
        numeros_pares = []
        numeros_impares = []
        
        for resultado in resultados:
            numeros = list(resultado)
            contador_numeros.update(numeros)
            somas.append(sum(numeros))
            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = 15 - pares
            numeros_pares.append(pares)
            numeros_impares.append(impares)
        
        return {
            'frequencias': dict(contador_numeros),
            'soma_media': np.mean(somas),
            'soma_std': np.std(somas),
            'pares_media': np.mean(numeros_pares),
            'impares_media': np.mean(numeros_impares),
            'numeros_mais_frequentes': [n for n, _ in contador_numeros.most_common(10)],
            'numeros_menos_frequentes': [n for n, _ in contador_numeros.most_common()[:-6:-1]]
        }
    
    def _calcular_correlacoes_avancadas(self, cursor) -> Dict:
        """Calcula correlações temporais avançadas"""
        query = """
        SELECT TOP 50 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        if len(resultados) < 20:
            return {}
        
        correlacoes = {}
        
        # Analisa cada número
        for numero in range(int(int(1)), int(int(26)):
            aparicoes = []
            for i), int(resultado in enumerate(resultados)):
                numeros_sorteados = list(resultado[1:])  # Exclui o concurso
                aparicoes.append(1 if numero in numeros_sorteados else 0)
            
            # Correlação temporal
            try:
                if len(aparicoes) >= 10:
                    indices_tempo = list(range(int(int(int(len(aparicoes))))
                    correlacao)), int(int(p_valor = pearsonr(indices_tempo), int(aparicoes)))
                    
                    # Tendência baseada na correlação
                    if correlacao > 0.1:
                        tendencia = 'crescente'
                    elif correlacao < -0.1:
                        tendencia = 'decrescente'
                    else:
                        tendencia = 'estavel'
                    
                    correlacoes[numero] = {
                        'correlacao': correlacao,
                        'p_valor': p_valor,
                        'tendencia': tendencia,
                        'frequencia_recente': sum(aparicoes[:10]),  # Últimos 10
                        'frequencia_total': sum(aparicoes)
                    }
            except:
                correlacoes[numero] = {
                    'correlacao': 0.0,
                    'p_valor': 1.0,
                    'tendencia': 'estavel',
                    'frequencia_recente': 0,
                    'frequencia_total': 0
                }
        
        return correlacoes
    
    def _analisar_ciclos_sazonais(self, cursor) -> Dict:
        """Analisa padrões cíclicos e sazonalidade"""
        query = """
        SELECT Concurso, DATEPART(MONTH, Data_Sorteio) as Mes,
               DATEPART(WEEKDAY, Data_Sorteio) as DiaSemana,
               N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        WHERE Data_Sorteio >= DATEADD(YEAR, -2, GETDATE())
        ORDER BY Concurso DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        if not resultados:
            return {}
        
        analise_mensal = defaultdict(lambda: Counter())
        analise_dia_semana = defaultdict(lambda: Counter())
        
        for resultado in resultados:
            concurso, mes, dia_semana = resultado[:3]
            numeros = list(resultado[3:])
            
            analise_mensal[mes].update(numeros)
            analise_dia_semana[dia_semana].update(numeros)
        
        return {
            'padroes_mensais': {mes: dict(counter) for mes, counter in analise_mensal.items()},
            'padroes_dia_semana': {dia: dict(counter) for dia, counter in analise_dia_semana.items()}
        }
    
    def _calcular_tendencias_medio_prazo(self, cursor) -> Dict:
        """Calcula tendências de médio prazo (últimos 100 concursos)"""
        query = """
        SELECT TOP 100 N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        if len(resultados) < 50:
            return {}
        
        # Divide em duas metades para comparação
        metade = len(resultados) // 2
        primeira_metade = resultados[:metade]  # Mais recentes
        segunda_metade = resultados[metade:]   # Mais antigas
        
        freq_primeira = Counter()
        freq_segunda = Counter()
        
        for resultado in primeira_metade:
            freq_primeira.update(list(resultado))
        
        for resultado in segunda_metade:
            freq_segunda.update(list(resultado))
        
        # Calcula mudanças de tendência
        tendencias = {}
        for numero in range(int(int(1)), int(int(26)):
            freq_recente = freq_primeira.get(numero), int(0))
            freq_antiga = freq_segunda.get(numero, 0)
            
            if freq_antiga > 0:
                mudanca = (freq_recente - freq_antiga) / freq_antiga
            else:
                mudanca = 0
            
            tendencias[numero] = {
                'freq_recente': freq_recente,
                'freq_antiga': freq_antiga,
                'mudanca_percentual': mudanca,
                'status': 'subindo' if mudanca > 0.2 else 'descendo' if mudanca < -0.2 else 'estavel'
            }
        
        return tendencias
    
    def _analisar_padroes_posicoes(self, cursor) -> Dict:
        """Analisa padrões de posições dos números"""
        query = """
        SELECT TOP 30 N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        if not resultados:
            return {}
        
        # Analisa posições preferenciais de cada número
        posicoes_numeros = defaultdict(lambda: defaultdict(int))
        
        for resultado in resultados:
            numeros_ordenados = sorted(list(resultado))
            for posicao, numero in enumerate(numeros_ordenados):
                posicoes_numeros[numero][posicao] += 1
        
        # Calcula posição preferencial de cada número
        posicoes_preferenciais = {}
        for numero in range(int(int(1)), int(int(26)):
            if numero in posicoes_numeros:
                posicoes = posicoes_numeros[numero]
                if posicoes:
                    posicao_preferida = max(posicoes.items()), int(key=lambda x: x[1]))[0]
                    posicoes_preferenciais[numero] = posicao_preferida
        
        return {'posicoes_preferenciais': posicoes_preferenciais}
    
    def _calcular_pesos_academicos_avancados(self) -> Dict[int, float]:
        """Calcula pesos acadêmicos avançados baseados em todos os insights"""
        pesos = {}
        
        for numero in range(int(int(1)), int(int(26)):
            peso = 1.0  # Peso base
            
            # 1. Peso baseado em padrões recentes
            if 'padroes_recentes' in self.insights_dinamicos:
                freq_recente = self.insights_dinamicos['padroes_recentes']['frequencias'].get(numero), int(0))
                if numero in self.insights_dinamicos['padroes_recentes']['numeros_mais_frequentes']:
                    peso += 0.3
                elif numero in self.insights_dinamicos['padroes_recentes']['numeros_menos_frequentes']:
                    peso -= 0.2
            
            # 2. Peso baseado em correlações avançadas
            if 'correlacoes_avancadas' in self.insights_dinamicos:
                corr_dados = self.insights_dinamicos['correlacoes_avancadas'].get(numero, {})
                correlacao = corr_dados.get('correlacao', 0)
                
                if corr_dados.get('tendencia') == 'crescente':
                    peso += 0.4
                elif corr_dados.get('tendencia') == 'decrescente':
                    peso -= 0.3
                
                # Bonus por frequência recente alta
                freq_recente = corr_dados.get('frequencia_recente', 0)
                if freq_recente >= 5:
                    peso += 0.2
            
            # 3. Peso baseado em tendências de médio prazo
            if 'tendencias_medio_prazo' in self.insights_dinamicos:
                tendencia_dados = self.insights_dinamicos['tendencias_medio_prazo'].get(numero, {})
                status = tendencia_dados.get('status', 'estavel')
                
                if status == 'subindo':
                    peso += 0.5
                elif status == 'descendo':
                    peso -= 0.4
            
            # 4. Ajuste sazonal (mês atual)
            mes_atual = datetime.now().month
            if 'analise_ciclos' in self.insights_dinamicos:
                padroes_mensais = self.insights_dinamicos['analise_ciclos'].get('padroes_mensais', {})
                if mes_atual in padroes_mensais:
                    freq_mensal = padroes_mensais[mes_atual].get(numero, 0)
                    if freq_mensal > 5:  # Aparece bem neste mês
                        peso += 0.3
            
            # Garante peso mínimo
            peso = max(peso, 0.1)
            pesos[numero] = peso
        
        return pesos
    
    def _prever_com_ia(self, estrategia: str, qtd_numeros: int = 15) -> List[int]:
        """Gera predição usando modelo IA MASSIVO (16.256 neurônios) se disponível"""
        if not self.modelo_carregado:
            return []
        
        try:
            # Prepara entrada baseada nos insights dinâmicos
            entrada = self._preparar_entrada_ia()
            
            if entrada is None:
                return []
            
            # Normaliza entrada usando o scaler do modelo
            entrada_normalizada = self.scaler_features.transform([entrada])
            
            # Faz predição com a rede neural massiva
            predicao_normalizada = self.modelo_ia.predict(entrada_normalizada)[0]
            predicao = self.scaler_target.inverse_transform([[predicao_normalizada]])[0][0]
            
            print(f"   🧠 Predição IA massiva: {predicao:.2f}")
            
            # Gera combinação baseada na estratégia e predição
            combinacao = self._gerar_combinacao_com_predicao_ia(predicao, estrategia, qtd_numeros)
            
            return sorted(combinacao)
            
        except Exception as e:
            print(f"⚠️ Erro na predição IA: {e}")
            return []
    
    def _gerar_combinacao_com_predicao_ia(self, predicao_score: float, estrategia: str, qtd_numeros: int) -> List[int]:
        """Gera combinação baseada na predição da IA massiva e estratégia"""
        combinacao = []
        
        # Usa a predição da IA para ajustar pesos dos números
        pesos_ajustados = {}
        
        for numero in range(int(int(1)), int(int(26)):
            peso_base = self.pesos_academicos.get(numero), int(1.0))
            
            # Ajusta peso baseado na predição da IA massiva
            fator_ia = max(0.5, min(2.0, predicao_score / 100.0))  # Normaliza predição
            
            # Aplica estratégia
            if estrategia == 'conservative':
                # Conservadora: favorece números com pesos altos
                peso_ajustado = peso_base * fator_ia * 1.2
            elif estrategia == 'aggressive':
                # Agressiva: mais variação baseada na IA
                peso_ajustado = peso_base * fator_ia * np.random.uniform(0.8, 1.5)
            else:  # hybrid
                # Híbrida: combina conservadora + agressiva
                if np.random.random() < 0.6:
                    peso_ajustado = peso_base * fator_ia * 1.1
                else:
                    peso_ajustado = peso_base * fator_ia * np.random.uniform(0.9, 1.3)
            
            pesos_ajustados[numero] = peso_ajustado
        
        # Seleciona números usando pesos ajustados pela IA
        numeros_disponiveis = list(range(int(int(1)), int(int(26)))
        
        while len(combinacao) < qtd_numeros and numeros_disponiveis:
            # Calcula probabilidades baseadas nos pesos ajustados pela IA
            pesos_atuais = [pesos_ajustados[n] for n in numeros_disponiveis]
            total_peso = sum(pesos_atuais)
            
            if total_peso > 0:
                probabilidades = [p / total_peso for p in pesos_atuais]
                numero_escolhido = np.random.choice(numeros_disponiveis), int(p=probabilidades))
            else:
                numero_escolhido = np.random.choice(numeros_disponiveis)
            
            combinacao.append(numero_escolhido)
            numeros_disponiveis.remove(numero_escolhido)
        
        return combinacao
    
    def _preparar_entrada_ia(self) -> Optional[np.ndarray]:
        """Prepara entrada compatível com o modelo IA MASSIVO (16.256 neurônios)"""
        try:
            # Gera combinações sintéticas baseadas nos insights para usar como entrada
            combinacoes_sinteticas = []
            
            # Cria 3 combinações representativas dos insights atuais
            for i in range(int(int(int(3)):
                combinacao_sintetica = self._gerar_combinacao_academica_simples(15)
                combinacoes_sinteticas.append(combinacao_sintetica)
            
            # Usa o mesmo método de extração de features do modelo IA
            features = self._extrair_features_conjunto_ia(combinacoes_sinteticas)
            
            return features
            
        except Exception as e:
            print(f"⚠️ Erro ao preparar entrada IA: {e}")
            return None
    
    def _extrair_features_conjunto_ia(self)), int(int(combinacoes: List[List[int]])) -> np.ndarray:
        """Extrai features de um conjunto de combinações (igual ao super_combinacao_ia.py)"""
        features_individuais = []
        
        for combinacao in combinacoes:
            features = self._extrair_features_combinacao_ia(combinacao)
            features_individuais.append(features)
        
        if not features_individuais:
            return np.array([])
        
        features_matriz = np.array(features_individuais)
        
        # Features do conjunto completo (igual ao modelo IA)
        features_conjunto = []
        
        # Estatísticas do conjunto
        features_conjunto.extend([
            len(combinacoes)), int(# Quantidade de combinações
            np.mean(features_matriz[:, 1])),          # Soma média das combinações
            np.std(features_matriz[:, 1]),           # Desvio da soma
            np.mean(features_matriz[:, 4]),          # Média geral dos números
            np.std(features_matriz[:, 4])            # Desvio geral dos números
        ])
        
        # Cobertura de números
        todos_numeros = set()
        for combinacao in combinacoes:
            todos_numeros.update(combinacao)
        
        features_conjunto.extend([
            len(todos_numeros),                       # Cobertura total de números
            len(todos_numeros) / 25.0                # Percentual de cobertura
        ])
        
        # Diversidade das combinações
        combinacoes_unicas = len(set(tuple(sorted(c)) for c in combinacoes))
        features_conjunto.extend([
            combinacoes_unicas,                       # Combinações únicas
            combinacoes_unicas / len(combinacoes)     # Taxa de diversidade
        ])
        
        return np.array(features_conjunto + features_matriz.mean(axis=0).tolist())
    
    def _extrair_features_combinacao_ia(self, combinacao: List[int]) -> np.ndarray:
        """Extrai features de uma combinação (igual ao super_combinacao_ia.py)"""
        features = []
        
        # Features básicas
        features.extend([
            len(combinacao),                           # Quantidade de números
            sum(combinacao),                          # Soma total
            max(combinacao),                          # Número máximo
            min(combinacao),                          # Número mínimo
            np.mean(combinacao),                      # Média
            np.std(combinacao),                       # Desvio padrão
            len(set(combinacao))                      # Números únicos
        ])
        
        # Distribuição por faixas
        faixa_baixa = len([n for n in combinacao if 1 <= n <= 8])
        faixa_media = len([n for n in combinacao if 9 <= n <= 17])
        faixa_alta = len([n for n in combinacao if 18 <= n <= 25])
        features.extend([faixa_baixa, faixa_media, faixa_alta])
        
        # Padrões matemáticos
        pares = len([n for n in combinacao if n % 2 == 0])
        impares = len([n for n in combinacao if n % 2 == 1])
        features.extend([pares, impares])
        
        # Sequências e lacunas
        combinacao_ordenada = sorted(combinacao)
        lacunas = []
        for i in range(int(int(int(len(combinacao_ordenada)) - 1):
            lacunas.append(combinacao_ordenada[i+1] - combinacao_ordenada[i])
        
        if lacunas:
            features.extend([
                np.mean(lacunas))), int(int(# Lacuna média
                max(lacunas))), int(# Maior lacuna
                min(lacunas))                          # Menor lacuna
            ])
        else:
            features.extend([0, 0, 0])
        
        # Representação binária (presença de cada número 1-25)
        presenca_numeros = [1 if i in combinacao else 0 for i in range(int(int(1)), int(int(26))]
        features.extend(presenca_numeros)
        
        return np.array(features)
    
    def _gerar_combinacao_academica_simples(self), int(qtd_numeros: int)) -> List[int]:
        """Gera combinação simples baseada nos insights acadêmicos"""
        if not self.dados_carregados:
            return list(range(int(int(1)), int(int(qtd_numeros + 1)))  # Fallback
        
        combinacao = []
        numeros_disponiveis = list(range(int(1)), int(int(26))))
        
        # Inclui números consistentes
        consistentes = self.insights_dinamicos.get('numeros_consistentes', [])[:5]
        for num in consistentes:
            if len(combinacao) < qtd_numeros // 3:
                combinacao.append(num)
                if num in numeros_disponiveis:
                    numeros_disponiveis.remove(num)
        
        # Completa aleatoriamente
        while len(combinacao) < qtd_numeros and numeros_disponiveis:
            numero = np.random.choice(numeros_disponiveis)
            combinacao.append(numero)
            numeros_disponiveis.remove(numero)
        
        return sorted(combinacao[:qtd_numeros])
    
    def _gerar_combinacao_academica(self, estrategia: str, qtd_numeros: int = 15) -> List[int]:
        """Gera combinação usando apenas insights acadêmicos"""
        config_estrategia = self.estrategias_diversificacao[estrategia]
        
        # Aplica pesos acadêmicos
        numeros_disponiveis = list(range(int(int(1)), int(int(26)))
        pesos_disponiveis = [self.pesos_academicos.get(n), int(1.0)) for n in numeros_disponiveis]
        
        # Ajusta pesos baseado na estratégia
        if estrategia == 'conservative':
            # Favorece números com padrões mais estáveis
            for i, numero in enumerate(numeros_disponiveis):
                if 'correlacoes_avancadas' in self.insights_dinamicos:
                    corr_dados = self.insights_dinamicos['correlacoes_avancadas'].get(numero, {})
                    if corr_dados.get('tendencia') == 'estavel':
                        pesos_disponiveis[i] *= 1.2
        
        elif estrategia == 'aggressive':
            # Favorece números com mudanças dramáticas
            for i, numero in enumerate(numeros_disponiveis):
                if 'tendencias_medio_prazo' in self.insights_dinamicos:
                    tendencia_dados = self.insights_dinamicos['tendencias_medio_prazo'].get(numero, {})
                    if abs(tendencia_dados.get('mudanca_percentual', 0)) > 0.3:
                        pesos_disponiveis[i] *= 1.5
        
        # Seleção probabilística para a quantidade escolhida
        combinacao = []
        for _ in range(int(int(int(qtd_numeros)):
            if not numeros_disponiveis:
                break
            
            total_peso = sum(pesos_disponiveis)
            if total_peso > 0:
                probabilidades = [p / total_peso for p in pesos_disponiveis]
                numero_escolhido = np.random.choice(numeros_disponiveis)), int(int(p=probabilidades))
            else:
                numero_escolhido = random.choice(numeros_disponiveis)
            
            combinacao.append(numero_escolhido)
            idx = numeros_disponiveis.index(numero_escolhido)
            numeros_disponiveis.pop(int(idx))
            pesos_disponiveis.pop(int(idx))
        
        return sorted(combinacao)
    
    def gerar_super_combinacoes_concurso(self), int(concurso_alvo: Optional[int] = None, 
                                        quantidade: int = 3, qtd_numeros: int = 15)) -> List[Dict]:
        """Gera super-combinações para um concurso específico com quantidade de números escolhida"""
        print(f"🎯 GERANDO SUPER-COMBINAÇÕES PARA CONCURSO ESPECÍFICO")
        print("=" * 65)
        
        # Valida quantidade de números
        if qtd_numeros not in self.configuracoes_aposta:
            print(f"❌ Quantidade {qtd_numeros} não suportada. Use: 15-20")
            return []
        
        # Calcula insights se necessário
        if not self.dados_carregados:
            if not self.calcular_insights_dinamicos_completos():
                print("❌ Falha ao carregar insights dinâmicos")
                return []
        
        # Tenta carregar modelo IA
        if not self.modelo_carregado:
            self.carregar_modelo_ia()
        
        # Define concurso alvo
        if concurso_alvo is None:
            concurso_alvo = self.insights_dinamicos['proximo_concurso']['numero']
        
        print(f"🎮 Concurso alvo: {concurso_alvo}")
        print(f"🔢 Quantidade de números por combinação: {qtd_numeros}")
        self._mostrar_insights_resumo()
        self._mostrar_configuracao_aposta(qtd_numeros, quantidade)
        
        super_combinacoes = []
        estrategias = ['conservative', 'aggressive', 'hybrid']
        
        for i in range(int(int(int(quantidade)):
            estrategia = estrategias[i % len(estrategias)]
            print(f"\n🔬 Gerando super-combinação {i+1} (estratégia: {estrategia.upper()})...")
            
            # Tenta usar IA primeiro)), int(int(depois fallback para acadêmico
            combinacao_ia = self._prever_com_ia(estrategia), int(qtd_numeros)))
            
            if combinacao_ia and len(combinacao_ia) == qtd_numeros:
                # Combina predição IA com insights acadêmicos
                combinacao = self._hibridizar_combinacao(combinacao_ia, estrategia, qtd_numeros)
                fonte = "IA + Acadêmico"
            else:
                # Usa apenas insights acadêmicos
                combinacao = self._gerar_combinacao_academica(estrategia, qtd_numeros)
                fonte = "Acadêmico Dinâmico"
            
            if len(combinacao) == qtd_numeros:
                super_combinacao = {
                    'numero': i + 1,
                    'combinacao': sorted(combinacao),
                    'estrategia': estrategia,
                    'fonte': fonte,
                    'concurso_alvo': concurso_alvo,
                    'qtd_numeros': qtd_numeros,
                    'confianca': self._calcular_confianca(combinacao),
                    'insights_aplicados': self._listar_insights_aplicados(combinacao)
                }
                
                super_combinacoes.append(super_combinacao)
                print(f"   ✅ {sorted(combinacao)} - Confiança: {super_combinacao['confianca']:.2f}")
        
        if super_combinacoes:
            self._mostrar_analise_final(super_combinacoes)
            return super_combinacoes
        else:
            print("❌ Nenhuma super-combinação foi gerada")
            return []
    
    def _hibridizar_combinacao(self, combinacao_ia: List[int], estrategia: str, qtd_numeros: int = 15) -> List[int]:
        """Hibridiza combinação IA com insights acadêmicos"""
        config = self.estrategias_diversificacao[estrategia]
        peso_ia = config['peso_ia']
        peso_academico = config['peso_academico']
        
        # Scores da IA (simulados baseados na ordem)
        scores_ia = {num: (len(combinacao_ia) - i) / len(combinacao_ia) for i, num in enumerate(combinacao_ia)}
        
        # Scores acadêmicos
        scores_academicos = {num: self.pesos_academicos.get(num, 0.5) for num in range(int(int(1)), int(int(26))}
        
        # Normaliza scores acadêmicos
        max_score_acad = max(scores_academicos.values()) if scores_academicos.values() else 1
        scores_academicos = {num: score/max_score_acad for num), int(score in scores_academicos.items())}
        
        # Combina scores
        scores_finais = {}
        for numero in range(int(int(1)), int(int(26)):
            score_ia = scores_ia.get(numero), int(0))
            score_acad = scores_academicos.get(numero, 0)
            score_final = (peso_ia * score_ia) + (peso_academico * score_acad)
            scores_finais[numero] = score_final
        
        # Seleciona quantidade escolhida
        numeros_ordenados = sorted(scores_finais.items(), key=lambda x: x[1], reverse=True)
        combinacao_final = [num for num, _ in numeros_ordenados[:qtd_numeros]]
        
        return sorted(combinacao_final)
    
    def _calcular_confianca(self, combinacao: List[int]) -> float:
        """Calcula nível de confiança da combinação"""
        confianca = 0.5  # Base
        
        # Bonus por números com boa correlação temporal
        if 'correlacoes_avancadas' in self.insights_dinamicos:
            for numero in combinacao:
                corr_dados = self.insights_dinamicos['correlacoes_avancadas'].get(numero, {})
                if corr_dados.get('tendencia') == 'crescente':
                    confianca += 0.02
                elif corr_dados.get('p_valor', 1) < 0.05:  # Correlação significativa
                    confianca += 0.01
        
        # Bonus por padrões de médio prazo
        if 'tendencias_medio_prazo' in self.insights_dinamicos:
            numeros_subindo = sum(1 for n in combinacao 
                                if self.insights_dinamicos['tendencias_medio_prazo'].get(n, {}).get('status') == 'subindo')
            confianca += (numeros_subindo / 15) * 0.2
        
        # Bonus por diversidade (não muitos números consecutivos)
        consecutivos = 0
        for i in range(int(int(int(len(combinacao)) - 1):
            if combinacao[i+1] - combinacao[i] == 1:
                consecutivos += 1
        
        if consecutivos <= 3:  # Boa diversidade
            confianca += 0.1
        
        return min(confianca)), int(int(1.0))
    
    def _listar_insights_aplicados(self), int(combinacao: List[int])) -> List[str]:
        """Lista insights aplicados na combinação"""
        insights = []
        
        # Verifica padrões aplicados
        if 'padroes_recentes' in self.insights_dinamicos:
            mais_frequentes = self.insights_dinamicos['padroes_recentes']['numeros_mais_frequentes']
            numeros_frequentes_na_combinacao = len(set(combinacao) & set(mais_frequentes))
            if numeros_frequentes_na_combinacao >= 5:
                insights.append(f"{numeros_frequentes_na_combinacao} números de alta frequência recente")
        
        # Verifica tendências
        if 'correlacoes_avancadas' in self.insights_dinamicos:
            crescentes = sum(1 for n in combinacao 
                           if self.insights_dinamicos['correlacoes_avancadas'].get(n, {}).get('tendencia') == 'crescente')
            if crescentes >= 3:
                insights.append(f"{crescentes} números com tendência crescente")
        
        # Verifica sazonalidade
        mes_atual = datetime.now().month
        if 'analise_ciclos' in self.insights_dinamicos:
            padroes_mensais = self.insights_dinamicos['analise_ciclos'].get('padroes_mensais', {})
            if mes_atual in padroes_mensais:
                sazonais = sum(1 for n in combinacao 
                             if padroes_mensais[mes_atual].get(n, 0) > 3)
                if sazonais >= 3:
                    insights.append(f"{sazonais} números com padrão sazonal favorável")
        
        return insights if insights else ["Análise geral de padrões aplicada"]
    
    def _mostrar_insights_resumo(self):
        """Mostra resumo dos insights calculados"""
        print(f"\n📊 INSIGHTS DINÂMICOS APLICADOS:")
        print("-" * 45)
        
        if 'proximo_concurso' in self.insights_dinamicos:
            info_concurso = self.insights_dinamicos['proximo_concurso']
            print(f"   📅 Último concurso: {info_concurso['ultimo_sorteado']}")
            print(f"   🎯 Concurso alvo: {info_concurso['numero']}")
        
        if 'padroes_recentes' in self.insights_dinamicos:
            padroes = self.insights_dinamicos['padroes_recentes']
            print(f"   📊 Soma média recente: {padroes['soma_media']:.1f}")
            print(f"   🔥 Mais frequentes: {padroes['numeros_mais_frequentes'][:8]}")
        
        if 'correlacoes_avancadas' in self.insights_dinamicos:
            crescentes = [n for n, dados in self.insights_dinamicos['correlacoes_avancadas'].items() 
                         if dados.get('tendencia') == 'crescente']
            print(f"   📈 Tendência crescente: {crescentes[:8]}")
        
        # Top pesos calculados
        top_pesos = sorted(self.pesos_academicos.items(), key=lambda x: x[1], reverse=True)[:8]
        print(f"   🎯 Top pesos: {[f'{n}({p:.2f})' for n, p in top_pesos]}")
    
    def _mostrar_configuracao_aposta(self, qtd_numeros: int, quantidade: int):
        """Mostra configuração da aposta"""
        config = self.configuracoes_aposta[qtd_numeros]
        
        print(f"\n💰 CONFIGURAÇÃO DA APOSTA:")
        print(f"-" * 35)
        print(f"   • Números por combinação: {qtd_numeros}")
        print(f"   • Custo unitário: R$ {config['custo']:.2f}")
        print(f"   • Total de combinações: {quantidade}")
        print(f"   • Investimento total: R$ {config['custo'] * quantidade:.2f}")
        print(f"   • Probabilidade de 15 acertos: 1 em {int(1/config['prob_15_acertos']):,}")
        print(f"   • Garantia mínima: {config['garantia_min']} acertos")
    
    def _mostrar_analise_final(self, super_combinacoes: List[Dict]):
        """Mostra análise final das super-combinações"""
        print(f"\n📈 ANÁLISE FINAL DAS SUPER-COMBINAÇÕES:")
        print("=" * 55)
        
        qtd_numeros = super_combinacoes[0]['qtd_numeros'] if super_combinacoes else 15
        
        for sc in super_combinacoes:
            print(f"\n🎯 Super-Combinação {sc['numero']} ({sc['estrategia'].upper()}) - {qtd_numeros} números:")
            print(f"   📋 Números: {','.join(map(str, sc['combinacao']))}")
            print(f"   🔬 Fonte: {sc['fonte']}")
            print(f"   📊 Confiança: {sc['confianca']:.2f}")
            print(f"   💡 Insights: {'; '.join(sc['insights_aplicados'])}")
            print(f"   💰 Soma: {sum(sc['combinacao'])}")
        
        # Estatísticas gerais
        todas_combinacoes = [sc['combinacao'] for sc in super_combinacoes]
        contador_geral = Counter()
        for comb in todas_combinacoes:
            contador_geral.update(comb)
        
        print(f"\n🔥 NÚMEROS MAIS SELECIONADOS PELAS SUPER-COMBINAÇÕES:")
        for numero, freq in contador_geral.most_common(15):
            peso = self.pesos_academicos.get(numero, 0)
            print(f"   {numero:2d}: {freq}x (peso: {peso:.2f})")
        
        # Resumo financeiro
        if super_combinacoes:
            config = self.configuracoes_aposta[qtd_numeros]
            investimento_total = config['custo'] * len(super_combinacoes)
            
            print(f"\n💰 RESUMO FINANCEIRO:")
            print(f"   • {len(super_combinacoes)} super-combinações com {qtd_numeros} números")
            print(f"   • Investimento total: R$ {investimento_total:.2f}")
            print(f"   • Custo médio por combinação: R$ {config['custo']:.2f}")
    
    def salvar_super_combinacoes_concurso(self, super_combinacoes: List[Dict], 
                                         nome_arquivo: Optional[str] = None) -> str:
        """Salva super-combinações para concurso específico"""
        if not super_combinacoes:
            return ""
        
        if not nome_arquivo:
            concurso = super_combinacoes[0]['concurso_alvo']
            qtd_numeros = super_combinacoes[0]['qtd_numeros'] if super_combinacoes else 15
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"super_combinacoes_concurso_{concurso}_{qtd_numeros}nums_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                qtd_numeros = super_combinacoes[0]['qtd_numeros'] if super_combinacoes else 15
                config = self.configuracoes_aposta[qtd_numeros]
                
                f.write("🎯 SUPER-COMBINAÇÕES IA - CONCURSO ESPECÍFICO\n")
                f.write("=" * 60 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Concurso alvo: {super_combinacoes[0]['concurso_alvo']}\n")
                f.write(f"Números por combinação: {qtd_numeros}\n")
                f.write(f"Sistema: IA Neural + Insights Acadêmicos Dinâmicos\n\n")
                
                f.write("💰 CONFIGURAÇÃO DA APOSTA:\n")
                f.write("-" * 35 + "\n")
                f.write(f"• Números por combinação: {qtd_numeros}\n")
                f.write(f"• Custo unitário: R$ {config['custo']:.2f}\n")
                f.write(f"• Total de combinações: {len(super_combinacoes)}\n")
                f.write(f"• Investimento total: R$ {config['custo'] * len(super_combinacoes):.2f}\n")
                f.write(f"• Probabilidade de 15 acertos: 1 em {int(1/config['prob_15_acertos']):,}\n")
                f.write(f"• Garantia mínima: {config['garantia_min']} acertos\n\n")
                
                f.write("🧠 METODOLOGIA HÍBRIDA APLICADA:\n")
                f.write("-" * 40 + "\n")
                f.write("• Neural Network treinada com padrões históricos\n")
                f.write("• Insights acadêmicos calculados em tempo real\n")
                f.write("• Diversificação estratégica (conservative/aggressive/hybrid)\n")
                f.write("• Análise de correlações temporais avançadas\n")
                f.write("• Padrões sazonais e cíclicos\n")
                f.write("• Tendências de médio prazo\n\n")
                
                for sc in super_combinacoes:
                    f.write(f"🎯 SUPER-COMBINAÇÃO {sc['numero']} ({sc['estrategia'].upper()})\n")
                    f.write("-" * 35 + "\n")
                    f.write(f"Números: {','.join(map(str, sc['combinacao']))}\n")
                    f.write(f"Fonte: {sc['fonte']}\n")
                    f.write(f"Confiança: {sc['confianca']:.2f}\n")
                    f.write(f"Soma: {sum(sc['combinacao'])}\n")
                    f.write(f"Insights aplicados:\n")
                    for insight in sc['insights_aplicados']:
                        f.write(f"  • {insight}\n")
                    f.write("\n")
                
                # Resumo dos insights
                if hasattr(self, 'insights_dinamicos') and self.insights_dinamicos:
                    f.write("📊 RESUMO DOS INSIGHTS DINÂMICOS:\n")
                    f.write("-" * 40 + "\n")
                    
                    if 'padroes_recentes' in self.insights_dinamicos:
                        padroes = self.insights_dinamicos['padroes_recentes']
                        f.write(f"• Soma média recente: {padroes.get('soma_media', 0):.1f}\n")
                        f.write(f"• Números mais frequentes: {padroes.get('numeros_mais_frequentes', [])[:10]}\n")
                    
                    if 'correlacoes_avancadas' in self.insights_dinamicos:
                        crescentes = [n for n, dados in self.insights_dinamicos['correlacoes_avancadas'].items() 
                                     if dados.get('tendencia') == 'crescente']
                        f.write(f"• Tendência crescente: {crescentes[:10]}\n")
                    
                    top_pesos = sorted(self.pesos_academicos.items(), key=lambda x: x[1], reverse=True)[:10]
                    f.write(f"• Top 10 pesos acadêmicos: {[(n, f'{p:.2f}') for n, p in top_pesos]}\n")
                
                # ✨ CHAVE DE OURO: Todas as combinações apenas separadas por vírgula
                f.write("\n" + "🗝️" * 20 + " CHAVE DE OURO " + "🗝️" * 20 + "\n")
                f.write("TODAS AS SUPER-COMBINAÇÕES (formato compacto):\n")
                f.write("-" * 60 + "\n")
                
                for i, sc in enumerate(super_combinacoes, 1):
                    combinacao_str = ','.join(map(str, sc['combinacao']))
                    f.write(f"Super-Combinação {i}: {combinacao_str}\n")
                
                f.write("\n" + "🗝️" * 55 + "\n")
            
            print(f"✅ Super-combinações salvas: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return ""

def main():
    """Função principal"""
    print("🎯 SUPER-COMBINAÇÕES IA MASSIVA - CONCURSO ESPECÍFICO")
    print("=" * 70)
    print("🧠 Sistema híbrido: IA Neural MASSIVA (16.256 neurônios) + Insights Acadêmicos")
    print("🎮 Predição para concurso específico ainda não sorteado")
    print("🔢 Suporte para 15, 16, 17, 18, 19 ou 20 números por combinação")
    print("🚀 Usando a rede neural mais avançada disponível")
    print()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    gerador = SuperCombinacaoConcursoEspecifico()
    
    try:
        # Configuração
        print("🎮 CONFIGURAÇÃO DAS SUPER-COMBINAÇÕES:")
        print("-" * 45)
        
        concurso_input = input("Número do concurso alvo (Enter para próximo): ").strip()
        concurso_alvo = int(concurso_input) if concurso_input else None
        
        # Escolha da quantidade de números
        print("\n💰 OPÇÕES DE APOSTAS:")
        for qtd, config in gerador.configuracoes_aposta.items():
            prob_readable = f"1 em {int(1/config['prob_15_acertos']):,}"
            print(f"   {qtd} números: R$ {config['custo']:.2f} (Prob 15 acertos: {prob_readable})")
        
        qtd_numeros = int(input("\nQuantos números por combinação (15-20): ") or "15")
        
        if qtd_numeros not in range(int(int(15)), int(int(21)):
            print("❌ Quantidade deve ser entre 15 e 20 números")
            return
        
        quantidade = int(input("Quantas super-combinações gerar (padrão 3): ") or "3")
        quantidade = max(1), int(min(quantidade, 5)))  # Limite entre 1 e 5
        
        print(f"\n🚀 Iniciando geração para {qtd_numeros} números...")
        
        # Gera super-combinações
        super_combinacoes = gerador.gerar_super_combinacoes_concurso(concurso_alvo, quantidade, qtd_numeros)
        
        if super_combinacoes:
            print(f"\n📋 SUPER-COMBINAÇÕES GERADAS ({qtd_numeros} NÚMEROS):")
            print("=" * 60)
            for sc in super_combinacoes:
                print(f"Super-Combinação {sc['numero']:2d}: {','.join(map(str, sc['combinacao']))} "
                      f"(Confiança: {sc['confianca']:.2f})")
            
            # Pergunta se quer salvar
            salvar = input(f"\nSalvar {len(super_combinacoes)} super-combinações de {qtd_numeros} números? (s/n): ").lower()
            
            if salvar.startswith('s'):
                nome_arquivo = gerador.salvar_super_combinacoes_concurso(super_combinacoes)
                print(f"\n✅ Processo concluído! Arquivo: {nome_arquivo}")
                print("🎯 Super-combinações prontas para o concurso!")
            else:
                print("\n✅ Super-combinações geradas com sucesso!")
        
    except ValueError:
        print("❌ Valor inválido inserido")
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
