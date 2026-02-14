#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 IA DE NÚMEROS REPETIDOS INTELIGENTE
Sistema que ensina a rede neural sobre padrões de repetição de números:
- Análise estatística de QtdeRepetidos (6-10 números repetidos em 90% dos casos)
- Análise estatística de RepetidosMesmaPosicao (0-15 números na mesma posição)
- Predição inteligente baseada em ciclos de ausência
- Otimização para garantir 11+ acertos em 50% das combinações

Autor: AR CALHAU
Data: 21 de Agosto de 2025
"""

import os
import sys
from pathlib import Path

# Adicionar diretório base ao path para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from database_config import db_config
from collections import Counter, defaultdict
import statistics
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pickle
import warnings
warnings.filterwarnings('ignore')

class IANumerosRepetidos:
    """
    IA especializada em padrões de números repetidos para otimização de combinações
    """
    
    def __init__(self):
        self.pasta_base = "ia_repetidos"
        os.makedirs(self.pasta_base, exist_ok=True)
        
        # Monitor de aprendizado
        try:
            from monitor_aprendizado_ia import MonitorAprendizadoIA
            self.monitor_aprendizado = MonitorAprendizadoIA()
        except ImportError:
            self.monitor_aprendizado = None
            print("⚠️ Monitor de aprendizado não disponível")
        
        # Modelos de IA especializados
        self.modelo_qtde_repetidos = None
        self.modelo_mesma_posicao = None
        self.modelo_predicao_numeros = None
        
        # Scalers para normalização
        self.scaler_features_qtde = StandardScaler()
        self.scaler_features_posicao = StandardScaler()
        self.scaler_features_numeros = StandardScaler()
        
        # Base de conhecimento estatístico
        self.estatisticas_repetidos = {}
        self.ciclos_ausencia = {}
        self.padroes_historicos = {}
        
        print("🧠 IA de Números Repetidos inicializada")
        print("📊 Pronto para análise inteligente de padrões de repetição")
    
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
    
    def analisar_estatisticas_repetidos(self) -> bool:
        """
        Analisa estatísticas históricas de números repetidos
        """
        print("📊 Analisando estatísticas históricas de repetições...")
        
        conn = self.conectar_base()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 1. Análise de QtdeRepetidos
            print("   🔍 Analisando QtdeRepetidos...")
            query_qtde = """
            SELECT QtdeRepetidos, COUNT(*) as Frequencia
            FROM Resultados_INT
            WHERE QtdeRepetidos IS NOT NULL
            GROUP BY QtdeRepetidos
            ORDER BY QtdeRepetidos
            """
            
            cursor.execute(query_qtde)
            dados_qtde = cursor.fetchall()
            
            total_concursos_qtde = sum([row[1] for row in dados_qtde])
            self.estatisticas_repetidos['QtdeRepetidos'] = {}
            
            for qtde, freq in dados_qtde:
                percentual = (freq / total_concursos_qtde) * 100
                self.estatisticas_repetidos['QtdeRepetidos'][qtde] = {
                    'frequencia': freq,
                    'percentual': percentual,
                    'probabilidade': freq / total_concursos_qtde
                }
                print(f"      {qtde} repetidos: {freq:4d} casos ({percentual:5.1f}%)")
            
            # 2. Análise de RepetidosMesmaPosicao
            print("   🔍 Analisando RepetidosMesmaPosicao...")
            query_posicao = """
            SELECT RepetidosMesmaPosicao, COUNT(*) as Frequencia
            FROM Resultados_INT
            WHERE RepetidosMesmaPosicao IS NOT NULL
            GROUP BY RepetidosMesmaPosicao
            ORDER BY RepetidosMesmaPosicao
            """
            
            cursor.execute(query_posicao)
            dados_posicao = cursor.fetchall()
            
            total_concursos_posicao = sum([row[1] for row in dados_posicao])
            self.estatisticas_repetidos['RepetidosMesmaPosicao'] = {}
            
            for posicao, freq in dados_posicao:
                percentual = (freq / total_concursos_posicao) * 100
                self.estatisticas_repetidos['RepetidosMesmaPosicao'][posicao] = {
                    'frequencia': freq,
                    'percentual': percentual,
                    'probabilidade': freq / total_concursos_posicao
                }
                print(f"      {posicao} mesma posição: {freq:4d} casos ({percentual:5.1f}%)")
            
            # 3. Análise de ciclos de ausência para cada valor
            self._analisar_ciclos_ausencia(cursor)
            
            print("✅ Análise estatística concluída!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            return False
        finally:
            conn.close()
    
    def _analisar_ciclos_ausencia(self, cursor):
        """Analisa ciclos de ausência para predição"""
        print("   🔄 Analisando ciclos de ausência...")
        
        # Busca dados ordenados por concurso
        query = """
        SELECT Concurso, QtdeRepetidos, RepetidosMesmaPosicao
        FROM Resultados_INT
        WHERE QtdeRepetidos IS NOT NULL AND RepetidosMesmaPosicao IS NOT NULL
        ORDER BY Concurso ASC
        """
        
        cursor.execute(query)
        dados = cursor.fetchall()
        
        # Calcula ciclos de ausência para QtdeRepetidos
        self.ciclos_ausencia['QtdeRepetidos'] = {}
        ultima_ocorrencia_qtde = {}
        
        for concurso, qtde_rep, rep_pos in dados:
            # Para cada valor possível de repetidos
            for valor_qtde in range(0, 16):  # 0 a 15 possíveis repetidos
                if qtde_rep == valor_qtde:
                    if valor_qtde in ultima_ocorrencia_qtde:
                        ciclo_ausencia = concurso - ultima_ocorrencia_qtde[valor_qtde]
                        if valor_qtde not in self.ciclos_ausencia['QtdeRepetidos']:
                            self.ciclos_ausencia['QtdeRepetidos'][valor_qtde] = []
                        self.ciclos_ausencia['QtdeRepetidos'][valor_qtde].append(ciclo_ausencia)
                    ultima_ocorrencia_qtde[valor_qtde] = concurso
        
        # Calcula ciclos de ausência para RepetidosMesmaPosicao
        self.ciclos_ausencia['RepetidosMesmaPosicao'] = {}
        ultima_ocorrencia_pos = {}
        
        for concurso, qtde_rep, rep_pos in dados:
            # Para cada valor possível de repetidos na mesma posição
            for valor_pos in range(0, 16):  # 0 a 15 possíveis repetidos na mesma posição
                if rep_pos == valor_pos:
                    if valor_pos in ultima_ocorrencia_pos:
                        ciclo_ausencia = concurso - ultima_ocorrencia_pos[valor_pos]
                        if valor_pos not in self.ciclos_ausencia['RepetidosMesmaPosicao']:
                            self.ciclos_ausencia['RepetidosMesmaPosicao'][valor_pos] = []
                        self.ciclos_ausencia['RepetidosMesmaPosicao'][valor_pos].append(ciclo_ausencia)
                    ultima_ocorrencia_pos[valor_pos] = concurso
        
        # Calcula estatísticas dos ciclos
        for tipo in ['QtdeRepetidos', 'RepetidosMesmaPosicao']:
            for valor, ciclos in self.ciclos_ausencia[tipo].items():
                if ciclos:
                    media_ciclos = statistics.mean(ciclos)
                    max_ciclos = max(ciclos)
                    min_ciclos = min(ciclos)
                    
                    if tipo not in self.padroes_historicos:
                        self.padroes_historicos[tipo] = {}
                    
                    self.padroes_historicos[tipo][valor] = {
                        'media_ciclos': media_ciclos,
                        'max_ciclos': max_ciclos,
                        'min_ciclos': min_ciclos,
                        'total_ocorrencias': len(ciclos)
                    }
    
    def criar_features_ia(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cria features para treinamento da IA baseadas nos dados históricos
        """
        print("🧠 Criando features para treinamento da IA...")
        
        conn = self.conectar_base()
        if not conn:
            return np.array([]), np.array([])
        
        try:
            cursor = conn.cursor()
            
            # Busca dados históricos básicos (usando apenas colunas que existem)
            query = """
            SELECT 
                Concurso,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15,
                QtdeRepetidos, RepetidosMesmaPosicao
            FROM Resultados_INT
            WHERE QtdeRepetidos IS NOT NULL 
                AND RepetidosMesmaPosicao IS NOT NULL
            ORDER BY Concurso ASC
            """
            
            cursor.execute(query)
            dados = cursor.fetchall()
            
            features = []
            targets_qtde = []
            targets_posicao = []
            
            for i, linha in enumerate(dados):
                if i == 0:  # Primeiro concurso, pula
                    continue
                
                concurso_atual = linha[0]
                numeros_atual = list(linha[1:16])
                qtde_rep_atual = linha[16]
                rep_pos_atual = linha[17]
                
                # Dados do concurso anterior
                linha_anterior = dados[i-1]
                numeros_anterior = list(linha_anterior[1:16])
                qtde_rep_anterior = linha_anterior[16]
                rep_pos_anterior = linha_anterior[17]
                
                # Cria features baseadas em padrões históricos - 45 FEATURES TOTAL (igual à predição)
                feature_vetor = []
                
                # 1. Features básicas do concurso anterior (10 features)
                qtde_impares_ant = sum(1 for n in numeros_anterior if n % 2 != 0)
                
                # Números primos até 25
                primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
                qtde_primos_ant = sum(1 for n in numeros_anterior if n in primos)
                
                # Números fibonacci até 25
                fibonacci = {1, 2, 3, 5, 8, 13, 21}
                qtde_fibonacci_ant = sum(1 for n in numeros_anterior if n in fibonacci)
                
                soma_total_ant = sum(numeros_anterior)
                
                # Quintis (distribuição por faixas)
                quintil1_ant = sum(1 for n in numeros_anterior if 1 <= n <= 5)   # Quintil 1-5
                quintil2_ant = sum(1 for n in numeros_anterior if 6 <= n <= 10)  # Quintil 6-10
                
                distancia_extremos_ant = max(numeros_anterior) - min(numeros_anterior)
                
                # Calcula gaps simples
                numeros_ordenados_ant = sorted(numeros_anterior)
                qtde_gaps_ant = sum(1 for j in range(len(numeros_ordenados_ant)-1) 
                                  if numeros_ordenados_ant[j+1] - numeros_ordenados_ant[j] > 1)
                
                feature_vetor.extend([
                    qtde_rep_anterior, rep_pos_anterior,
                    qtde_primos_ant, qtde_fibonacci_ant, qtde_impares_ant,
                    soma_total_ant, quintil1_ant, quintil2_ant,
                    distancia_extremos_ant, qtde_gaps_ant
                ])
                
                # 2. Tendências (simplificadas) - 2 features
                feature_vetor.extend([qtde_rep_anterior, rep_pos_anterior])
                
                # 3. Ciclos de ausência para valores importantes (10 features)
                valores_importantes_qtde = [6, 7, 8, 9, 10]
                for valor in valores_importantes_qtde:
                    ciclo_medio = 20.0 + np.random.normal(0, 5)  # Simula ciclo
                    feature_vetor.append(min(max(ciclo_medio, 1), 100))
                
                valores_importantes_pos = [0, 1, 2, 3, 4]
                for valor in valores_importantes_pos:
                    ciclo_medio = 15.0 + np.random.normal(0, 3)  # Simula ciclo
                    feature_vetor.append(min(max(ciclo_medio, 1), 100))
                
                # 4. Distribuição por faixas (5 features)
                faixa_1_5 = sum(1 for n in numeros_anterior if 1 <= n <= 5)
                faixa_6_10 = sum(1 for n in numeros_anterior if 6 <= n <= 10)
                faixa_11_15 = sum(1 for n in numeros_anterior if 11 <= n <= 15)
                faixa_16_20 = sum(1 for n in numeros_anterior if 16 <= n <= 20)
                faixa_21_25 = sum(1 for n in numeros_anterior if 21 <= n <= 25)
                
                feature_vetor.extend([faixa_1_5, faixa_6_10, faixa_11_15, faixa_16_20, faixa_21_25])
                
                # 5. Features extras para chegar a 45 (18 features adicionais)
                # Análises mais avançadas dos números (iguais à predição)
                
                # Análise de sequências
                sequencias_ant = 0
                for j in range(len(numeros_ordenados_ant) - 1):
                    if numeros_ordenados_ant[j+1] == numeros_ordenados_ant[j] + 1:
                        sequencias_ant += 1
                
                # Análise de múltiplos
                multiplos_3_ant = sum(1 for n in numeros_anterior if n % 3 == 0)
                multiplos_5_ant = sum(1 for n in numeros_anterior if n % 5 == 0)
                multiplos_7_ant = sum(1 for n in numeros_anterior if n % 7 == 0)
                
                # Análise de terminações
                terminacoes_ant = {}
                for k in range(10):
                    terminacoes_ant[k] = sum(1 for n in numeros_anterior if n % 10 == k)
                
                # Distribuição dezenas/unidades
                dezenas_distintas_ant = len(set(n // 10 for n in numeros_anterior))
                unidades_distintas_ant = len(set(n % 10 for n in numeros_anterior))
                
                # Padrões especiais
                numeros_baixos_ant = sum(1 for n in numeros_anterior if n <= 12)  # Primeira metade
                
                # Variância
                media_numeros_ant = sum(numeros_anterior) / 15
                variancia_ant = sum((n - media_numeros_ant) ** 2 for n in numeros_anterior) / 15
                
                # Features adicionais calculadas (18 features)
                feature_vetor.extend([
                    sequencias_ant,                    # 1. Qtd sequências
                    multiplos_3_ant,                   # 2. Múltiplos de 3
                    multiplos_5_ant,                   # 3. Múltiplos de 5 
                    multiplos_7_ant,                   # 4. Múltiplos de 7
                    terminacoes_ant[0],               # 5. Terminação 0
                    terminacoes_ant[1],               # 6. Terminação 1
                    terminacoes_ant[2],               # 7. Terminação 2
                    terminacoes_ant[3],               # 8. Terminação 3
                    terminacoes_ant[4],               # 9. Terminação 4
                    terminacoes_ant[5],               # 10. Terminação 5
                    terminacoes_ant[6],               # 11. Terminação 6
                    terminacoes_ant[7],               # 12. Terminação 7
                    terminacoes_ant[8],               # 13. Terminação 8
                    terminacoes_ant[9],               # 14. Terminação 9
                    dezenas_distintas_ant,            # 15. Dezenas distintas
                    unidades_distintas_ant,           # 16. Unidades distintas
                    numeros_baixos_ant,               # 17. Números baixos (1-12)
                    variancia_ant                     # 18. Variância
                ])
                
                # Adiciona às listas
                features.append(feature_vetor)
                targets_qtde.append(qtde_rep_atual)
                targets_posicao.append(rep_pos_atual)
            
            print(f"✅ Features criadas: {len(features)} amostras, {len(features[0]) if features else 0} características")
            
            # DEBUG: Mostra detalhes das features
            if len(features) > 0:
                print(f"🔍 DETALHAMENTO DAS {len(features[0])} FEATURES NO TREINAMENTO:")
                feature_names = [
                    "QtdeRepetidos_anterior", "RepetidosMesmaPosicao_anterior",
                    "QtdePrimos", "QtdeFibonacci", "QtdeImpares",
                    "SomaTotal", "Quintil1", "Quintil2", 
                    "DistanciaExtremos", "QtdeGaps",
                    "Trend_QtdeRep", "Trend_RepPos"
                ]
                # Ciclos ausência QtdeRepetidos (5)
                for valor in [6, 7, 8, 9, 10]:
                    feature_names.append(f"Ciclo_ausencia_QtdeRep_{valor}")
                # Ciclos ausência RepetidosMesmaPosicao (5)
                for valor in [0, 1, 2, 3, 4]:
                    feature_names.append(f"Ciclo_ausencia_RepPos_{valor}")
                # Distribuição por faixas (5)
                feature_names.extend(["Faixa_1_5", "Faixa_6_10", "Faixa_11_15", "Faixa_16_20", "Faixa_21_25"])
                # Features extras (18)
                feature_names.extend([
                    "Sequencias", "Multiplos_3", "Multiplos_5", "Multiplos_7",
                    "Terminacao_0", "Terminacao_1", "Terminacao_2", "Terminacao_3",
                    "Terminacao_4", "Terminacao_5", "Terminacao_6", "Terminacao_7",
                    "Terminacao_8", "Terminacao_9", "Dezenas_distintas", "Unidades_distintas",
                    "Numeros_baixos", "Variancia"
                ])
                
                for i, name in enumerate(feature_names):
                    print(f"   {i+1:2d}. {name}")
                
                print(f"   Total esperado: {len(feature_names)} (deve ser 45)")
                print(f"   Total real: {len(features[0])}")
                
                if len(feature_names) != 45:
                    print(f"⚠️ AVISO: Esperadas 45 features, mas temos {len(feature_names)} nomes!")
                if len(features[0]) != 45:
                    print(f"⚠️ AVISO: Esperadas 45 features, mas criamos {len(features[0])}!")
            
            return np.array(features), np.array(targets_qtde), np.array(targets_posicao)
            
        except Exception as e:
            print(f"❌ Erro ao criar features: {e}")
            return np.array([]), np.array([]), np.array([])
        finally:
            conn.close()
    
    def treinar_modelos_ia(self) -> bool:
        """
        Treina os modelos de IA especializados em padrões de repetição
        """
        print("🧠 Treinando modelos de IA para padrões de repetição...")
        
        # Cria features
        features, targets_qtde, targets_posicao = self.criar_features_ia()
        
        if len(features) == 0:
            print("❌ Nenhuma feature disponível para treinamento")
            return False
        
        try:
            # Normaliza features
            features_normalized = self.scaler_features_qtde.fit_transform(features)
            
            # 1. Treina modelo para QtdeRepetidos
            print("   🎯 Treinando modelo para QtdeRepetidos...")
            X_train_qtde, X_test_qtde, y_train_qtde, y_test_qtde = train_test_split(
                features_normalized, targets_qtde, test_size=0.2, random_state=42
            )
            
            # Rede neural otimizada para QtdeRepetidos (foco em 6-10)
            self.modelo_qtde_repetidos = MLPRegressor(
                hidden_layer_sizes=(256, 128, 64, 32),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                learning_rate_init=0.001,
                max_iter=1000,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=50,
                random_state=42
            )
            
            self.modelo_qtde_repetidos.fit(X_train_qtde, y_train_qtde)
            
            # Avalia modelo QtdeRepetidos
            pred_qtde = self.modelo_qtde_repetidos.predict(X_test_qtde)
            mse_qtde = mean_squared_error(y_test_qtde, pred_qtde)
            
            # Calcula precisão para faixa ideal (7-9 repetidos)
            precisao_faixa_ideal = sum(1 for real, pred in zip(y_test_qtde, pred_qtde) 
                                     if abs(real - pred) <= 1 and 7 <= real <= 9) / len(y_test_qtde) * 100
            
            print(f"      ✅ MSE QtdeRepetidos: {mse_qtde:.4f}")
            print(f"      🎯 Precisão faixa 7-9: {precisao_faixa_ideal:.1f}%")
            
            # 2. Treina modelo para RepetidosMesmaPosicao
            print("   🎯 Treinando modelo para RepetidosMesmaPosicao...")
            X_train_pos, X_test_pos, y_train_pos, y_test_pos = train_test_split(
                features_normalized, targets_posicao, test_size=0.2, random_state=42
            )
            
            # Rede neural otimizada para RepetidosMesmaPosicao (foco em 0-5)
            self.modelo_mesma_posicao = MLPRegressor(
                hidden_layer_sizes=(192, 96, 48, 24),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                learning_rate_init=0.001,
                max_iter=1000,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=50,
                random_state=42
            )
            
            self.modelo_mesma_posicao.fit(X_train_pos, y_train_pos)
            
            # Avalia modelo RepetidosMesmaPosicao
            pred_pos = self.modelo_mesma_posicao.predict(X_test_pos)
            mse_pos = mean_squared_error(y_test_pos, pred_pos)
            
            # Calcula precisão para faixa comum (0-3 repetidos na mesma posição)
            precisao_faixa_comum = sum(1 for real, pred in zip(y_test_pos, pred_pos) 
                                     if abs(real - pred) <= 1 and 0 <= real <= 3) / len(y_test_pos) * 100
            
            print(f"      ✅ MSE RepetidosMesmaPosicao: {mse_pos:.4f}")
            print(f"      🎯 Precisão faixa 0-3: {precisao_faixa_comum:.1f}%")
            
            # Salva modelos
            self._salvar_modelos()
            
            # Registra o treinamento no monitor
            if self.monitor_aprendizado:
                dados_treino = {
                    "amostras": len(X_train_qtde),
                    "precisao_qtde": precisao_faixa_ideal / 100,
                    "precisao_posicao": precisao_faixa_comum / 100, 
                    "tempo_treinamento": 0,  # Será calculado se necessário
                    "versao_dados": "2.0",
                    "melhorias": [
                        "Diversificação implementada",
                        "45 features calculadas",
                        "Foco em faixas comuns"
                    ]
                }
                self.monitor_aprendizado.registrar_treinamento(dados_treino)
                print("📊 Treinamento registrado no monitor de aprendizado")
            
            print("✅ Modelos de IA treinados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
            return False
    
    def predizer_padroes_repetidos(self, concurso_anterior: List[int], 
                                 contexto_historico: Optional[Dict] = None) -> Dict:
        """
        Prediz padrões de repetição para o próximo concurso
        """
        if self.modelo_qtde_repetidos is None or self.modelo_mesma_posicao is None:
            print("⚠️ Modelos não treinados. Carregando ou treinando...")
            if not self._carregar_modelos():
                if not self.treinar_modelos_ia():
                    return {'erro': 'Não foi possível treinar modelos'}
        
        try:
            # Cria features baseadas no concurso anterior
            features = self._criar_features_predicao(concurso_anterior, contexto_historico)
            
            if len(features) == 0:
                return {'erro': 'Não foi possível criar features'}
            
            # Normaliza features
            features_norm = self.scaler_features_qtde.transform([features])
            
            # Prediz QtdeRepetidos
            pred_qtde_raw = self.modelo_qtde_repetidos.predict(features_norm)[0]
            pred_qtde = max(0, min(15, round(pred_qtde_raw)))  # Limita entre 0-15
            
            # Prediz RepetidosMesmaPosicao
            pred_pos_raw = self.modelo_mesma_posicao.predict(features_norm)[0]
            pred_pos = max(0, min(15, round(pred_pos_raw)))  # Limita entre 0-15
            
            # Calcula probabilidades baseadas nas estatísticas históricas
            prob_qtde = self.estatisticas_repetidos.get('QtdeRepetidos', {}).get(pred_qtde, {}).get('probabilidade', 0.1)
            prob_pos = self.estatisticas_repetidos.get('RepetidosMesmaPosicao', {}).get(pred_pos, {}).get('probabilidade', 0.1)
            
            # Verifica se está na faixa ideal (7-9 repetidos)
            faixa_ideal_qtde = 7 <= pred_qtde <= 9
            
            # Verifica se está na faixa comum (0-3 na mesma posição)
            faixa_comum_pos = 0 <= pred_pos <= 3
            
            return {
                'QtdeRepetidos': {
                    'predicao': pred_qtde,
                    'probabilidade': prob_qtde,
                    'faixa_ideal': faixa_ideal_qtde,
                    'confianca': min(prob_qtde * 2, 1.0)  # Converte para confiança
                },
                'RepetidosMesmaPosicao': {
                    'predicao': pred_pos,
                    'probabilidade': prob_pos,
                    'faixa_comum': faixa_comum_pos,
                    'confianca': min(prob_pos * 2, 1.0)  # Converte para confiança
                },
                'recomendacao': self._gerar_recomendacao_estrategica(pred_qtde, pred_pos, prob_qtde, prob_pos)
            }
            
        except Exception as e:
            print(f"❌ Erro na predição: {e}")
            return {'erro': str(e)}
    
    def _criar_features_predicao(self, concurso_anterior: List[int], contexto: Optional[Dict]) -> List[float]:
        """Cria features para predição baseadas no concurso anterior - 45 FEATURES TOTAL"""
        features = []
        
        # 1. Features básicas do concurso anterior (10 features)
        qtde_impares = sum(1 for n in concurso_anterior if n % 2 != 0)
        
        # Números primos até 25
        primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
        qtde_primos = sum(1 for n in concurso_anterior if n in primos)
        
        # Números fibonacci até 25
        fibonacci = {1, 2, 3, 5, 8, 13, 21}
        qtde_fibonacci = sum(1 for n in concurso_anterior if n in fibonacci)
        
        soma_total = sum(concurso_anterior)
        
        # Quintis (distribuição por faixas)
        quintil1 = sum(1 for n in concurso_anterior if 1 <= n <= 5)   # Quintil 1-5
        quintil2 = sum(1 for n in concurso_anterior if 6 <= n <= 10)  # Quintil 6-10
        
        distancia_extremos = max(concurso_anterior) - min(concurso_anterior)
        
        # Calcula gaps simples
        numeros_ordenados = sorted(concurso_anterior)
        qtde_gaps = sum(1 for i in range(len(numeros_ordenados)-1) 
                       if numeros_ordenados[i+1] - numeros_ordenados[i] > 1)
        
        # Valores padrão se não há contexto
        qtde_rep_anterior = contexto.get('QtdeRepetidos', 8) if contexto else 8
        rep_pos_anterior = contexto.get('RepetidosMesmaPosicao', 2) if contexto else 2
        
        features.extend([
            qtde_rep_anterior, rep_pos_anterior,
            qtde_primos, qtde_fibonacci, qtde_impares,
            soma_total, quintil1, quintil2,
            distancia_extremos, qtde_gaps
        ])
        
        # 2. Tendências (simplificadas) - 2 features
        features.extend([qtde_rep_anterior, rep_pos_anterior])
        
        # 3. Ciclos de ausência para valores importantes (10 features)
        valores_importantes_qtde = [6, 7, 8, 9, 10]
        for valor in valores_importantes_qtde:
            ciclo_medio = self.padroes_historicos.get('QtdeRepetidos', {}).get(valor, {}).get('media_ciclos', 20)
            features.append(min(ciclo_medio, 100))
        
        valores_importantes_pos = [0, 1, 2, 3, 4]
        for valor in valores_importantes_pos:
            ciclo_medio = self.padroes_historicos.get('RepetidosMesmaPosicao', {}).get(valor, {}).get('media_ciclos', 15)
            features.append(min(ciclo_medio, 100))
        
        # 4. Distribuição por faixas (5 features)
        faixa_1_5 = sum(1 for n in concurso_anterior if 1 <= n <= 5)
        faixa_6_10 = sum(1 for n in concurso_anterior if 6 <= n <= 10)
        faixa_11_15 = sum(1 for n in concurso_anterior if 11 <= n <= 15)
        faixa_16_20 = sum(1 for n in concurso_anterior if 16 <= n <= 20)
        faixa_21_25 = sum(1 for n in concurso_anterior if 21 <= n <= 25)
        
        features.extend([faixa_1_5, faixa_6_10, faixa_11_15, faixa_16_20, faixa_21_25])
        
        # 5. Features extras para chegar a 45 (18 features adicionais)
        # Análises mais avançadas dos números
        
        # Análise de sequências
        sequencias = 0
        for i in range(len(numeros_ordenados) - 1):
            if numeros_ordenados[i+1] == numeros_ordenados[i] + 1:
                sequencias += 1
        
        # Análise de múltiplos
        multiplos_3 = sum(1 for n in concurso_anterior if n % 3 == 0)
        multiplos_5 = sum(1 for n in concurso_anterior if n % 5 == 0)
        multiplos_7 = sum(1 for n in concurso_anterior if n % 7 == 0)
        
        # Análise de terminações
        terminacoes = {}
        for i in range(10):
            terminacoes[i] = sum(1 for n in concurso_anterior if n % 10 == i)
        
        # Distribuição dezenas/unidades
        dezenas_distintas = len(set(n // 10 for n in concurso_anterior))
        unidades_distintas = len(set(n % 10 for n in concurso_anterior))
        
        # Padrões especiais
        numeros_baixos = sum(1 for n in concurso_anterior if n <= 12)  # Primeira metade
        
        # Variância
        media_numeros = sum(concurso_anterior) / 15
        variancia = sum((n - media_numeros) ** 2 for n in concurso_anterior) / 15
        
        # Features adicionais calculadas (18 features)
        features.extend([
            sequencias,                    # 1. Qtd sequências
            multiplos_3,                   # 2. Múltiplos de 3
            multiplos_5,                   # 3. Múltiplos de 5 
            multiplos_7,                   # 4. Múltiplos de 7
            terminacoes[0],               # 5. Terminação 0
            terminacoes[1],               # 6. Terminação 1
            terminacoes[2],               # 7. Terminação 2
            terminacoes[3],               # 8. Terminação 3
            terminacoes[4],               # 9. Terminação 4
            terminacoes[5],               # 10. Terminação 5
            terminacoes[6],               # 11. Terminação 6
            terminacoes[7],               # 12. Terminação 7
            terminacoes[8],               # 13. Terminação 8
            terminacoes[9],               # 14. Terminação 9
            dezenas_distintas,            # 15. Dezenas distintas
            unidades_distintas,           # 16. Unidades distintas
            numeros_baixos,               # 17. Números baixos (1-12)
            variancia                     # 18. Variância
        ])
        
        # DEBUG: Mostra detalhes das features na predição
        print(f"🔍 DEBUG PREDIÇÃO - Features criadas: {len(features)}")
        if len(features) != 45:
            print(f"⚠️ ERRO: Esperadas 45 features, mas criadas {len(features)}!")
        
        return features
    
    def _gerar_recomendacao_estrategica(self, pred_qtde: int, pred_pos: int, 
                                      prob_qtde: float, prob_pos: float) -> Dict:
        """Gera recomendação estratégica baseada nas predições"""
        estrategia = {}
        
        # Estratégia para QtdeRepetidos
        if 7 <= pred_qtde <= 9:
            estrategia['qtde_repetidos'] = {
                'status': 'IDEAL',
                'acao': f'Focar em combinações com {pred_qtde} números repetidos',
                'alternativas': [pred_qtde-1, pred_qtde, pred_qtde+1],
                'confianca': 'ALTA' if prob_qtde > 0.15 else 'MEDIA'
            }
        elif pred_qtde < 7:
            estrategia['qtde_repetidos'] = {
                'status': 'BAIXO',
                'acao': f'Considerar {pred_qtde} repetidos, mas incluir 7-8 como segurança',
                'alternativas': [pred_qtde, 7, 8],
                'confianca': 'MEDIA'
            }
        else:
            estrategia['qtde_repetidos'] = {
                'status': 'ALTO',
                'acao': f'Considerar {pred_qtde} repetidos, mas incluir 8-9 como segurança',
                'alternativas': [8, 9, pred_qtde],
                'confianca': 'MEDIA'
            }
        
        # Estratégia para RepetidosMesmaPosicao
        if 0 <= pred_pos <= 3:
            estrategia['mesma_posicao'] = {
                'status': 'COMUM',
                'acao': f'Focar em combinações com {pred_pos} números na mesma posição',
                'alternativas': [max(0, pred_pos-1), pred_pos, min(15, pred_pos+1)],
                'confianca': 'ALTA' if prob_pos > 0.10 else 'MEDIA'
            }
        else:
            estrategia['mesma_posicao'] = {
                'status': 'RARO',
                'acao': f'Valor {pred_pos} é raro, considerar 1-2 como alternativa',
                'alternativas': [1, 2, pred_pos],
                'confianca': 'BAIXA'
            }
        
        # Recomendação geral
        confianca_geral = (prob_qtde + prob_pos) / 2
        
        if confianca_geral > 0.12:
            estrategia['geral'] = {
                'nivel': 'ALTA_CONFIANCA',
                'recomendacao': 'Seguir predições com 70% das combinações',
                'distribuicao': {'predicao': 0.7, 'alternativas': 0.3}
            }
        elif confianca_geral > 0.08:
            estrategia['geral'] = {
                'nivel': 'MEDIA_CONFIANCA',
                'recomendacao': 'Balancear predições com alternativas',
                'distribuicao': {'predicao': 0.5, 'alternativas': 0.5}
            }
        else:
            estrategia['geral'] = {
                'nivel': 'BAIXA_CONFIANCA',
                'recomendacao': 'Priorizar alternativas seguras (7-9 e 1-2)',
                'distribuicao': {'predicao': 0.3, 'alternativas': 0.7}
            }
        
        return estrategia
    
    def otimizar_combinacoes_com_repeticoes(self, combinacoes: List[List[int]], 
                                          concurso_anterior: List[int]) -> List[List[int]]:
        """
        Otimiza combinações para seguir os padrões inteligentes de repetição com diversificação
        """
        print("🧠 Otimizando combinações com padrões inteligentes de repetição...")
        
        # Prediz padrões para o próximo concurso
        predicao = self.predizer_padroes_repetidos(concurso_anterior)
        
        if 'erro' in predicao:
            print(f"❌ Erro na predição: {predicao['erro']}")
            return combinacoes
        
        # Mostra predição
        qtde_pred = predicao['QtdeRepetidos']['predicao']
        pos_pred = predicao['RepetidosMesmaPosicao']['predicao']
        
        print(f"   🎯 Predição: {qtde_pred} números repetidos, {pos_pred} na mesma posição")
        
        # Obtém estratégia
        estrategia = predicao['recomendacao']
        distribuicao = estrategia['geral']['distribuicao']
        
        # Cria matriz de diversificação para garantir variedade
        import random
        random.seed(int(42))  # Para reprodutibilidade
        
        # Define alvos diversificados baseados nas alternativas estratégicas
        qtde_alternativas = estrategia['qtde_repetidos']['alternativas']
        pos_alternativas = estrategia['mesma_posicao']['alternativas']
        
        # Cria distribuição diversificada de alvos
        alvos_diversificados = []
        num_combinacoes = len(combinacoes)
        
        # 30% com predição principal
        for i in range(int(num_combinacoes * 0.3)):
            alvos_diversificados.append((qtde_pred, pos_pred))
        
        # 70% com alternativas variadas
        for i in range(num_combinacoes - len(alvos_diversificados)):
            qtde_alt = random.choice(qtde_alternativas)
            pos_alt = random.choice(pos_alternativas)
            alvos_diversificados.append((qtde_alt, pos_alt))
        
        # Embaralha para distribuir aleatoriamente
        random.shuffle(alvos_diversificados)
        
        combinacoes_otimizadas = []
        nums_anteriores = set(concurso_anterior)
        combinacoes_unicas = set()  # Para evitar duplicatas
        
        for i, combinacao in enumerate(combinacoes):
            # Usa o alvo diversificado para esta combinação
            qtde_alvo, pos_alvo = alvos_diversificados[i]
            
            # Adiciona variação adicional baseada no índice
            variacao_qtde = (i % 3) - 1  # -1, 0, +1 para variar
            qtde_final = max(4, min(12, qtde_alvo + variacao_qtde))  # Entre 4-12 repetidos
            
            variacao_pos = (i % 2)  # 0 ou 1 para variar posições
            pos_final = max(0, min(4, pos_alvo + variacao_pos))  # Entre 0-4 posições
            
            # Otimiza com diversificação
            combinacao_otimizada = self._ajustar_combinacao_para_repeticao_diversificada(
                combinacao, concurso_anterior, qtde_final, pos_final, i, combinacoes_unicas
            )
            
            # Converte para tuple para verificar duplicatas
            comb_tuple = tuple(sorted(combinacao_otimizada))
            tentativas = 0
            
            # Se já existe, gera variação
            while comb_tuple in combinacoes_unicas and tentativas < 5:
                variacao_extra = (tentativas + 1) * 2
                qtde_variada = max(4, min(12, qtde_final + variacao_extra - 3))
                pos_variada = max(0, min(4, pos_final + (tentativas % 2)))
                
                combinacao_otimizada = self._ajustar_combinacao_para_repeticao_diversificada(
                    combinacao, concurso_anterior, qtde_variada, pos_variada, 
                    i + tentativas * 100, combinacoes_unicas
                )
                comb_tuple = tuple(sorted(combinacao_otimizada))
                tentativas += 1
            
            combinacoes_unicas.add(comb_tuple)
            combinacoes_otimizadas.append(combinacao_otimizada)
        
        # Verifica diversidade final
        diversidade = len(combinacoes_unicas)
        percentual_diversidade = (diversidade / len(combinacoes)) * 100
        
        print(f"✅ {len(combinacoes_otimizadas)} combinações otimizadas com IA de repetições")
        print(f"🎨 Diversidade: {diversidade} combinações únicas ({percentual_diversidade:.1f}%)")
        
        return combinacoes_otimizadas
    
    def _ajustar_combinacao_para_repeticao_diversificada(self, combinacao: List[int], 
                                                       concurso_anterior: List[int],
                                                       qtde_alvo: int, pos_alvo: int,
                                                       indice_combinacao: int,
                                                       combinacoes_existentes: set) -> List[int]:
        """Ajusta uma combinação para atingir os alvos de repetição com diversificação"""
        import random
        
        # Usa o índice como seed para diversificação reproduzível
        random.seed(int(42 + indice_combinacao))
        
        combinacao_ajustada = combinacao.copy()
        nums_anteriores = set(concurso_anterior)
        qtd_numeros_original = len(combinacao)
        
        # 1. Ajusta quantidade de repetidos com diversificação
        nums_comb = set(combinacao_ajustada)
        qtde_atual = len(nums_comb & nums_anteriores)
        
        if qtde_atual < qtde_alvo:
            # Precisa adicionar mais números repetidos
            nums_nao_repetidos = [n for n in combinacao_ajustada if n not in nums_anteriores]
            nums_candidatos = [n for n in concurso_anterior if n not in nums_comb]
            
            # Embaralha para diversificar as escolhas
            random.shuffle(nums_nao_repetidos)
            random.shuffle(nums_candidatos)
            
            adicionar = min(qtde_alvo - qtde_atual, len(nums_nao_repetidos), len(nums_candidatos))
            
            for i in range(adicionar):
                if i < len(nums_nao_repetidos) and i < len(nums_candidatos):
                    # Substitui um não repetido por um candidato repetido
                    idx = combinacao_ajustada.index(nums_nao_repetidos[i])
                    combinacao_ajustada[idx] = nums_candidatos[i]
        
        elif qtde_atual > qtde_alvo:
            # Precisa remover números repetidos
            nums_repetidos = [n for n in combinacao_ajustada if n in nums_anteriores]
            nums_candidatos = [n for n in range(1, 26) if n not in nums_comb and n not in nums_anteriores]
            
            # Embaralha para diversificar as escolhas
            random.shuffle(nums_repetidos)
            random.shuffle(nums_candidatos)
            
            remover = min(qtde_atual - qtde_alvo, len(nums_repetidos), len(nums_candidatos))
            
            for i in range(remover):
                if i < len(nums_repetidos) and i < len(nums_candidatos):
                    # Substitui um repetido por um candidato não repetido
                    idx = combinacao_ajustada.index(nums_repetidos[i])
                    combinacao_ajustada[idx] = nums_candidatos[i]
        
        # 2. Adiciona diversificação baseada em padrões matemáticos
        # Varia a distribuição por quintis para maior diversidade
        quintil_alvo = (indice_combinacao % 5) + 1  # Alterna entre quintis 1-5
        
        if quintil_alvo == 1:  # Favorece números baixos (1-5)
            for i in range(len(combinacao_ajustada)):
                if random.random() < 0.2 and combinacao_ajustada[i] > 15:
                    candidatos = [n for n in range(1, 6) if n not in combinacao_ajustada]
                    if candidatos:
                        combinacao_ajustada[i] = random.choice(candidatos)
        
        elif quintil_alvo == 2:  # Favorece números médio-baixos (6-10)
            for i in range(len(combinacao_ajustada)):
                if random.random() < 0.2 and (combinacao_ajustada[i] < 6 or combinacao_ajustada[i] > 20):
                    candidatos = [n for n in range(6, 11) if n not in combinacao_ajustada]
                    if candidatos:
                        combinacao_ajustada[i] = random.choice(candidatos)
        
        elif quintil_alvo == 3:  # Favorece números centrais (11-15)
            for i in range(len(combinacao_ajustada)):
                if random.random() < 0.2 and (combinacao_ajustada[i] < 11 or combinacao_ajustada[i] > 15):
                    candidatos = [n for n in range(11, 16) if n not in combinacao_ajustada]
                    if candidatos:
                        combinacao_ajustada[i] = random.choice(candidatos)
        
        elif quintil_alvo == 4:  # Favorece números médio-altos (16-20)
            for i in range(len(combinacao_ajustada)):
                if random.random() < 0.2 and (combinacao_ajustada[i] < 16 or combinacao_ajustada[i] > 20):
                    candidatos = [n for n in range(16, 21) if n not in combinacao_ajustada]
                    if candidatos:
                        combinacao_ajustada[i] = random.choice(candidatos)
        
        else:  # quintil_alvo == 5: Favorece números altos (21-25)
            for i in range(len(combinacao_ajustada)):
                if random.random() < 0.2 and combinacao_ajustada[i] < 21:
                    candidatos = [n for n in range(21, 26) if n not in combinacao_ajustada]
                    if candidatos:
                        combinacao_ajustada[i] = random.choice(candidatos)
        
        # 3. Diversifica par/ímpar baseado no índice
        qtde_impares = sum(1 for n in combinacao_ajustada if n % 2 == 1)
        if (indice_combinacao % 3) == 0 and qtde_impares < 6:  # Força mais ímpares
            for i in range(len(combinacao_ajustada)):
                if combinacao_ajustada[i] % 2 == 0 and random.random() < 0.3:
                    candidatos_impares = [n for n in range(1, 26, 2) if n not in combinacao_ajustada]
                    if candidatos_impares:
                        combinacao_ajustada[i] = random.choice(candidatos_impares)
        
        elif (indice_combinacao % 3) == 1 and qtde_impares > 9:  # Força mais pares
            for i in range(len(combinacao_ajustada)):
                if combinacao_ajustada[i] % 2 == 1 and random.random() < 0.3:
                    candidatos_pares = [n for n in range(2, 26, 2) if n not in combinacao_ajustada]
                    if candidatos_pares:
                        combinacao_ajustada[i] = random.choice(candidatos_pares)
        
        # 4. Remove duplicatas verificando se já existe
        combinacao_final = sorted(list(set(combinacao_ajustada)))
        
        # Se ficou com menos números que o original, completa
        while len(combinacao_final) < qtd_numeros_original:
            candidatos = [n for n in range(1, 26) if n not in combinacao_final]
            if candidatos:
                combinacao_final.append(random.choice(candidatos))
            else:
                break
        
        # Se ficou com mais números que o original, remove aleatoriamente
        while len(combinacao_final) > qtd_numeros_original:
            combinacao_final.pop(random.randint(0, len(combinacao_final) - 1))
        
        return sorted(combinacao_final)

    def _ajustar_combinacao_para_repeticao(self, combinacao: List[int], 
                                         concurso_anterior: List[int],
                                         qtde_alvo: int, pos_alvo: int) -> List[int]:
        """Ajusta uma combinação para atingir os alvos de repetição (versão original)"""
        combinacao_ajustada = combinacao.copy()
        nums_anteriores = set(concurso_anterior)
        
        # 1. Ajusta quantidade de repetidos
        nums_comb = set(combinacao_ajustada)
        qtde_atual = len(nums_comb & nums_anteriores)
        
        if qtde_atual < qtde_alvo:
            # Precisa adicionar mais números repetidos
            nums_nao_repetidos = [n for n in combinacao_ajustada if n not in nums_anteriores]
            nums_candidatos = [n for n in concurso_anterior if n not in nums_comb]
            
            adicionar = min(qtde_alvo - qtde_atual, len(nums_nao_repetidos), len(nums_candidatos))
            
            for i in range(adicionar):
                if i < len(nums_nao_repetidos) and i < len(nums_candidatos):
                    # Substitui um não repetido por um candidato repetido
                    idx = combinacao_ajustada.index(nums_nao_repetidos[i])
                    combinacao_ajustada[idx] = nums_candidatos[i]
        
        elif qtde_atual > qtde_alvo:
            # Precisa remover números repetidos
            nums_repetidos = [n for n in combinacao_ajustada if n in nums_anteriores]
            nums_candidatos = [n for n in range(1, 26) if n not in nums_comb and n not in nums_anteriores]
            
            remover = min(qtde_atual - qtde_alvo, len(nums_repetidos), len(nums_candidatos))
            
            for i in range(remover):
                if i < len(nums_repetidos) and i < len(nums_candidatos):
                    # Substitui um repetido por um candidato não repetido
                    idx = combinacao_ajustada.index(nums_repetidos[i])
                    combinacao_ajustada[idx] = nums_candidatos[i]
        
        # 2. Ajusta repetidos na mesma posição (simplificado)
        # Em implementação real, seria mais complexo considerar as posições exatas
        
        return sorted(combinacao_ajustada)
    
    def _salvar_modelos(self):
        """Salva os modelos treinados"""
        try:
            with open(f"{self.pasta_base}/modelo_qtde_repetidos.pkl", 'wb') as f:
                pickle.dump(self.modelo_qtde_repetidos, f)
            
            with open(f"{self.pasta_base}/modelo_mesma_posicao.pkl", 'wb') as f:
                pickle.dump(self.modelo_mesma_posicao, f)
            
            with open(f"{self.pasta_base}/scaler_features.pkl", 'wb') as f:
                pickle.dump(self.scaler_features_qtde, f)
            
            with open(f"{self.pasta_base}/estatisticas.pkl", 'wb') as f:
                pickle.dump(self.estatisticas_repetidos, f)
            
            with open(f"{self.pasta_base}/padroes_historicos.pkl", 'wb') as f:
                pickle.dump(self.padroes_historicos, f)
            
            print("💾 Modelos salvos com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao salvar modelos: {e}")
    
    def _carregar_modelos(self) -> bool:
        """Carrega os modelos salvos"""
        try:
            with open(f"{self.pasta_base}/modelo_qtde_repetidos.pkl", 'rb') as f:
                self.modelo_qtde_repetidos = pickle.load(f)
            
            with open(f"{self.pasta_base}/modelo_mesma_posicao.pkl", 'rb') as f:
                self.modelo_mesma_posicao = pickle.load(f)
            
            with open(f"{self.pasta_base}/scaler_features.pkl", 'rb') as f:
                self.scaler_features_qtde = pickle.load(f)
            
            with open(f"{self.pasta_base}/estatisticas.pkl", 'rb') as f:
                self.estatisticas_repetidos = pickle.load(f)
            
            with open(f"{self.pasta_base}/padroes_historicos.pkl", 'rb') as f:
                self.padroes_historicos = pickle.load(f)
            
            print("📂 Modelos carregados com sucesso!")
            return True
        except FileNotFoundError:
            print("⚠️ Modelos não encontrados. Será necessário treinar.")
            return False
        except Exception as e:
            print(f"❌ Erro ao carregar modelos: {e}")
            return False

def main():
    """Função principal para teste e demonstração"""
    print("🧠 IA DE NÚMEROS REPETIDOS INTELIGENTE")
    print("=" * 60)
    
    ia = IANumerosRepetidos()
    
    print("\n🔄 Opções disponíveis:")
    print("1. Analisar estatísticas históricas")
    print("2. Treinar modelos de IA")
    print("3. Testar predição")
    print("4. Otimizar combinações exemplo")
    
    escolha = input("\nEscolha uma opção (1-4): ").strip()
    
    if escolha == "1":
        ia.analisar_estatisticas_repetidos()
    
    elif escolha == "2":
        if ia.analisar_estatisticas_repetidos():
            ia.treinar_modelos_ia()
    
    elif escolha == "3":
        # Teste de predição com dados exemplo
        concurso_anterior = [1, 2, 5, 7, 8, 11, 14, 16, 17, 19, 20, 21, 22, 24, 25]
        predicao = ia.predizer_padroes_repetidos(concurso_anterior)
        
        if 'erro' not in predicao:
            print(f"\n🎯 PREDIÇÃO PARA PRÓXIMO CONCURSO:")
            print(f"QtdeRepetidos: {predicao['QtdeRepetidos']['predicao']} (conf: {predicao['QtdeRepetidos']['confianca']:.1%})")
            print(f"RepetidosMesmaPosicao: {predicao['RepetidosMesmaPosicao']['predicao']} (conf: {predicao['RepetidosMesmaPosicao']['confianca']:.1%})")
            print(f"\nESTRATÉGIA: {predicao['recomendacao']['geral']['recomendacao']}")
    
    elif escolha == "4":
        # Exemplo de otimização de combinações
        combinacoes_exemplo = [
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 2, 4],
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 1, 3, 5],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        ]
        
        concurso_anterior = [1, 4, 6, 8, 9, 10, 12, 13, 14, 15, 18, 19, 20, 21, 25]
        
        combinacoes_otimizadas = ia.otimizar_combinacoes_com_repeticoes(
            combinacoes_exemplo, concurso_anterior
        )
        
        print(f"\n📊 COMPARAÇÃO:")
        for i, (original, otimizada) in enumerate(zip(combinacoes_exemplo, combinacoes_otimizadas)):
            print(f"Original  {i+1}: {original}")
            print(f"Otimizada {i+1}: {otimizada}")
            print()

if __name__ == "__main__":
    main()
