#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 ANALISADOR PREDITIVO AVANÇADO
Sistema de análise com aprendizado contínuo que:
- Testa combinações fixas contra todos os concursos históricos
- Conta acertos de 10 a 15 números para cada combinação
- Usa IA + pirâmide para prever acertos futuros
- Propõe combinações otimizadas para 15 acertos
- Controla ranges de treino e teste com estado persistente

Autor: AR CALHAU
Data: 24 de Agosto de 2025
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
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

from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
import pickle
from datetime import datetime
from database_config import db_config
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class AnalisadorPreditivoAvancado:
    """Sistema completo de análise preditiva com aprendizado contínuo"""
    
    def __init__(self):
        # 🎯 COMBINAÇÕES FIXAS PARA TESTE
        self.jogo_1 = [1, 2, 3, 4, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 25]
        self.jogo_2 = [1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 23, 24, 25]  # Corrigido: adicionado 24 para completar 20 números
        
        # 📊 HISTÓRICO DE PERFORMANCE
        self.historico_jogo_1 = {}  # {concurso: {10: 0, 11: 0, 12: 1, 13: 0, 14: 0, 15: 0}}
        self.historico_jogo_2 = {}  # {concurso: {10: 0, 11: 1, 12: 0, 13: 0, 14: 0, 15: 0}}
        
        # 🧠 MODELOS DE IA
        self.modelo_acertos_jogo1 = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        self.modelo_acertos_jogo2 = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        self.modelo_otimizacao = MLPClassifier(hidden_layer_sizes=(150, 100, 50), max_iter=2000, random_state=42)
        
        # 🔧 SCALERS E ENCODERS
        self.scaler_features = StandardScaler()
        self.scaler_targets = StandardScaler()
        
        # 📁 CONTROLE DE ESTADO
        self.arquivo_estado = "estado_analisador_preditivo.pkl"
        self.ultimo_concurso_treinado = 0
        self.ultimo_concurso_testado = 0
        self.ranges_processados = []  # [(inicio, fim, tipo)]
        
        # 🔺 INTEGRAÇÃO COM SISTEMAS EXISTENTES
        try:
            from piramide_invertida_dinamica import PiramideInvertidaDinamica
            self.piramide_sistema = PiramideInvertidaDinamica()
            self.usar_piramide = True
            print("🔺 Sistema Pirâmide Invertida integrado!")
        except ImportError:
            self.piramide_sistema = None
            self.usar_piramide = False
        
        # 📊 DADOS CARREGADOS
        self.dados_concursos = None
        self.dados_carregados = False
        
        # Carrega estado anterior se existir
        self._carregar_estado()
    
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
    
    def _carregar_estado(self):
        """Carrega estado anterior do sistema"""
        if os.path.exists(self.arquivo_estado):
            try:
                with open(self.arquivo_estado, 'rb') as f:
                    estado = pickle.load(f)
                    
                self.ultimo_concurso_treinado = estado.get('ultimo_concurso_treinado', 0)
                self.ultimo_concurso_testado = estado.get('ultimo_concurso_testado', 0)
                self.ranges_processados = estado.get('ranges_processados', [])
                self.historico_jogo_1 = estado.get('historico_jogo_1', {})
                self.historico_jogo_2 = estado.get('historico_jogo_2', {})
                
                print(f"📁 Estado carregado - Último treino: {self.ultimo_concurso_treinado}, Último teste: {self.ultimo_concurso_testado}")
                print(f"📊 Ranges processados: {len(self.ranges_processados)}")
                
            except Exception as e:
                print(f"⚠️ Erro ao carregar estado: {e}")
    
    def _salvar_estado(self):
        """Salva estado atual do sistema"""
        try:
            estado = {
                'ultimo_concurso_treinado': self.ultimo_concurso_treinado,
                'ultimo_concurso_testado': self.ultimo_concurso_testado,
                'ranges_processados': self.ranges_processados,
                'historico_jogo_1': self.historico_jogo_1,
                'historico_jogo_2': self.historico_jogo_2,
                'data_ultima_atualizacao': datetime.now().isoformat()
            }
            
            with open(self.arquivo_estado, 'wb') as f:
                pickle.dump(estado, f)
                
            print(f"💾 Estado salvo em {self.arquivo_estado}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar estado: {e}")
    
    def carregar_dados_concursos(self) -> bool:
        """Carrega todos os dados de concursos da base"""
        print("🔍 Carregando dados históricos de concursos...")
        
        conn = self.conectar_base()
        if not conn:
            return False
        
        try:
            # Query para buscar todos os concursos com números sorteados
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT 
            ORDER BY Concurso
            """
            
            self.dados_concursos = pd.read_sql(query, conn)
            
            print(f"✅ Carregados {len(self.dados_concursos)} concursos da base")
            print(f"📊 Range disponível: {self.dados_concursos['Concurso'].min()} a {self.dados_concursos['Concurso'].max()}")
            
            self.dados_carregados = True
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
        finally:
            conn.close()
    
    def calcular_acertos(self, numeros_jogo: List[int], numeros_sorteados: List[int]) -> Dict[int, int]:
        """Calcula quantos acertos de 10-15 números o jogo teve"""
        acertos_total = len(set(numeros_jogo) & set(numeros_sorteados))
        
        # Retorna dicionário com flags de acerto para cada faixa
        result = {}
        for faixa in range(10, 16:  # 10), int(11, 12, 13, 14, 15
            result[faixa] = 1 if acertos_total == faixa else 0
            
        result['total_acertos'] = acertos_total
        return result
    
    def analisar_historico_completo(self, concurso_inicio: int, concurso_fim: int)) -> bool:
        """Analisa histórico completo no range especificado"""
        if not self.dados_carregados:
            if not self.carregar_dados_concursos():
                return False
        
        print(f"\n🔍 ANÁLISE HISTÓRICA COMPLETA: Concursos {concurso_inicio} a {concurso_fim}")
        print("=" * 70)
        
        # Filtra dados no range
        dados_range = self.dados_concursos[
            (self.dados_concursos['Concurso'] >= concurso_inicio) & 
            (self.dados_concursos['Concurso'] <= concurso_fim)
        ]
        
        if len(dados_range) == 0:
            print(f"❌ Nenhum concurso encontrado no range {concurso_inicio}-{concurso_fim}")
            return False
        
        print(f"📊 Processando {len(dados_range)} concursos...")
        
        # Contadores de acertos por jogo
        contador_jogo1 = Counter()
        contador_jogo2 = Counter()
        
        for _, row in dados_range.iterrows():
            concurso = int(row['Concurso'])
            
            # Extrai números sorteados
            numeros_sorteados = [
                int(row[f'N{i}']) for i in range(1, 16
            ]
            
            # Calcula acertos para cada jogo
            acertos_j1 = self.calcular_acertos(self.jogo_1), int(numeros_sorteados))
            acertos_j2 = self.calcular_acertos(self.jogo_2, numeros_sorteados)
            
            # Armazena histórico detalhado
            self.historico_jogo_1[concurso] = acertos_j1
            self.historico_jogo_2[concurso] = acertos_j2
            
            # Conta total de acertos por faixa
            contador_jogo1[acertos_j1['total_acertos']] += 1
            contador_jogo2[acertos_j2['total_acertos']] += 1
        
        # Mostra estatísticas
        self._mostrar_estatisticas_historico(contador_jogo1, contador_jogo2, concurso_inicio, concurso_fim)
        
        # Atualiza controle de estado
        if concurso_fim > self.ultimo_concurso_treinado:
            self.ultimo_concurso_treinado = concurso_fim
        
        self.ranges_processados.append((concurso_inicio, concurso_fim, 'analise_historica'))
        self._salvar_estado()
        
        return True
    
    def _mostrar_estatisticas_historico(self, contador_j1: Counter, contador_j2: Counter, inicio: int, fim: int):
        """Mostra estatísticas do histórico analisado"""
        print(f"\n📈 ESTATÍSTICAS DO HISTÓRICO (Concursos {inicio} a {fim}):")
        print("-" * 60)
        
        total_concursos = sum(contador_j1.values())
        
        print(f"🎯 JOGO 1: {self.jogo_1}")
        for acertos in range(7, 16:
            count = contador_j1.get(acertos, 0)
            percent = (count / total_concursos * 100) if total_concursos > 0 else 0
            if count > 0:
                print(f"   {acertos:2d} acertos: {count:3d}x ({percent:5.2f}%)")
        
        print(f"\n🎯 JOGO 2: {self.jogo_2}")
        for acertos in range(7, 16:
            count = contador_j2.get(acertos, 0)
            percent = (count / total_concursos * 100) if total_concursos > 0 else 0
            if count > 0:
                print(f"   {acertos:2d} acertos: {count:3d}x ({percent:5.2f}%)")
        
        # Destaque para 15 acertos (meta principal)
        acertos_15_j1 = contador_j1.get(15, 0)
        acertos_15_j2 = contador_j2.get(15, 0)
        
        print(f"\n🏆 META PRINCIPAL - 15 ACERTOS:")
        print(f"   Jogo 1: {acertos_15_j1} vezes ({acertos_15_j1/total_concursos*100:.4f}%)")
        print(f"   Jogo 2: {acertos_15_j2} vezes ({acertos_15_j2/total_concursos*100:.4f}%)")
    
    def preparar_features_ml(self, concurso_base: int, janela: int = 10) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepara features para machine learning baseadas em janela móvel"""
        features = []
        target_j1 = []
        target_j2 = []
        
        concursos_disponiveis = sorted([c for c in self.historico_jogo_1.keys() if c >= concurso_base])
        
        for i in range(int(int(janela)), int(int(len(concursos_disponiveis)):
            # Janela de histórico
            concursos_janela = concursos_disponiveis[i-janela:i]
            concurso_atual = concursos_disponiveis[i]
            
            # Features: padrão de acertos nos últimos N concursos
            feature_row = []
            
            # Histórico de acertos para jogo 1
            for c in concursos_janela:
                if c in self.historico_jogo_1:
                    feature_row.append(self.historico_jogo_1[c]['total_acertos'])
                else:
                    feature_row.append(11)  # Valor médio padrão
            
            # Histórico de acertos para jogo 2  
            for c in concursos_janela:
                if c in self.historico_jogo_2:
                    feature_row.append(self.historico_jogo_2[c]['total_acertos'])
                else:
                    feature_row.append(11)  # Valor médio padrão
            
            # Features adicionais: tendências
            if len(concursos_janela) >= 3:
                # Tendência jogo 1
                acertos_j1_recentes = [self.historico_jogo_1.get(c), int({})).get('total_acertos', 11) for c in concursos_janela[-3:]]
                tendencia_j1 = np.mean(np.diff(acertos_j1_recentes))
                feature_row.append(tendencia_j1)
                
                # Tendência jogo 2
                acertos_j2_recentes = [self.historico_jogo_2.get(c, {}).get('total_acertos', 11) for c in concursos_janela[-3:]]
                tendencia_j2 = np.mean(np.diff(acertos_j2_recentes))
                feature_row.append(tendencia_j2)
            else:
                feature_row.extend([0.0, 0.0])
            
            # Integração com pirâmide se disponível
            if self.usar_piramide and self.piramide_sistema:
                try:
                    # Simulação de insights da pirâmide (você pode implementar uma versão específica)
                    feature_row.extend([0.5, 0.3, 0.7])  # Placeholder para features da pirâmide
                except:
                    feature_row.extend([0.5, 0.5, 0.5])
            else:
                feature_row.extend([0.5, 0.5, 0.5])
            
            features.append(feature_row)
            
            # Targets: acertos reais no concurso atual
            if concurso_atual in self.historico_jogo_1:
                target_j1.append(self.historico_jogo_1[concurso_atual]['total_acertos'])
            else:
                target_j1.append(11)
                
            if concurso_atual in self.historico_jogo_2:
                target_j2.append(self.historico_jogo_2[concurso_atual]['total_acertos'])
            else:
                target_j2.append(11)
        
        return np.array(features), np.array(target_j1), np.array(target_j2)
    
    def treinar_modelos_predicao(self, concurso_inicio: int, concurso_fim: int) -> bool:
        """Treina modelos de IA para predição de acertos"""
        print(f"\n🧠 TREINANDO MODELOS DE IA: Dados {concurso_inicio} a {concurso_fim}")
        print("=" * 70)
        
        # Prepara dados de treino
        try:
            X, y1, y2 = self.preparar_features_ml(concurso_inicio, janela=8)
            
            if len(X) < 20:
                print(f"⚠️ Poucos dados para treino: {len(X)} amostras. Mínimo recomendado: 20")
                return False
            
            print(f"📊 Preparados {len(X)} amostras de treino")
            print(f"📈 Features por amostra: {X.shape[1]}")
            
            # Normaliza features
            X_scaled = self.scaler_features.fit_transform(X)
            
            # Treina modelo para Jogo 1
            print("🎯 Treinando modelo para Jogo 1...")
            self.modelo_acertos_jogo1.fit(X_scaled, y1)
            score_j1 = self.modelo_acertos_jogo1.score(X_scaled, y1)
            
            # Treina modelo para Jogo 2
            print("🎯 Treinando modelo para Jogo 2...")
            self.modelo_acertos_jogo2.fit(X_scaled, y2)
            score_j2 = self.modelo_acertos_jogo2.score(X_scaled, y2)
            
            print(f"✅ Modelo Jogo 1 - Score: {score_j1:.3f}")
            print(f"✅ Modelo Jogo 2 - Score: {score_j2:.3f}")
            
            # Avaliação com dados de teste
            if len(X) > 40:
                X_train, X_test, y1_train, y1_test, y2_train, y2_test = train_test_split(
                    X_scaled, y1, y2, test_size=0.2, random_state=42
                )
                
                # Retreina com dados de treino
                self.modelo_acertos_jogo1.fit(X_train, y1_train)
                self.modelo_acertos_jogo2.fit(X_train, y2_train)
                
                # Testa
                pred_j1 = self.modelo_acertos_jogo1.predict(X_test)
                pred_j2 = self.modelo_acertos_jogo2.predict(X_test)
                
                mse_j1 = mean_squared_error(y1_test, pred_j1)
                mse_j2 = mean_squared_error(y2_test, pred_j2)
                
                print(f"📊 MSE Teste Jogo 1: {mse_j1:.3f}")
                print(f"📊 MSE Teste Jogo 2: {mse_j2:.3f}")
            
            # Atualiza estado
            self.ultimo_concurso_treinado = concurso_fim
            self._salvar_estado()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao treinar modelos: {e}")
            return False
    
    def prever_acertos_futuros(self, concurso_alvo: int) -> Dict[str, Any]:
        """Prevê quantos acertos cada jogo deve ter no concurso futuro"""
        print(f"\n🔮 PREDIZENDO ACERTOS PARA CONCURSO {concurso_alvo}")
        print("=" * 50)
        
        try:
            # Prepara features para predição
            concursos_recentes = sorted([c for c in self.historico_jogo_1.keys() if c < concurso_alvo])[-8:]
            
            if len(concursos_recentes) < 8:
                print("⚠️ Histórico insuficiente para predição robusta")
                concursos_recentes = sorted(self.historico_jogo_1.keys())[-8:]
            
            feature_row = []
            
            # Histórico recente jogo 1
            for c in concursos_recentes:
                feature_row.append(self.historico_jogo_1.get(c, {}).get('total_acertos', 11))
            
            # Histórico recente jogo 2
            for c in concursos_recentes:
                feature_row.append(self.historico_jogo_2.get(c, {}).get('total_acertos', 11))
            
            # Tendências
            if len(concursos_recentes) >= 3:
                acertos_j1_recentes = [self.historico_jogo_1.get(c, {}).get('total_acertos', 11) for c in concursos_recentes[-3:]]
                acertos_j2_recentes = [self.historico_jogo_2.get(c, {}).get('total_acertos', 11) for c in concursos_recentes[-3:]]
                
                tendencia_j1 = np.mean(np.diff(acertos_j1_recentes))
                tendencia_j2 = np.mean(np.diff(acertos_j2_recentes))
            else:
                tendencia_j1, tendencia_j2 = 0.0, 0.0
            
            feature_row.extend([tendencia_j1, tendencia_j2])
            
            # Features da pirâmide (placeholder)
            feature_row.extend([0.5, 0.5, 0.5])
            
            # Normaliza
            X_pred = self.scaler_features.transform([feature_row])
            
            # Predições
            pred_acertos_j1 = self.modelo_acertos_jogo1.predict(X_pred)[0]
            pred_acertos_j2 = self.modelo_acertos_jogo2.predict(X_pred)[0]
            
            # Arredonda para inteiros válidos
            pred_acertos_j1 = max(7, min(15, round(pred_acertos_j1)))
            pred_acertos_j2 = max(7, min(15, round(pred_acertos_j2)))
            
            resultado = {
                'concurso_alvo': concurso_alvo,
                'predicao_jogo1': pred_acertos_j1,
                'predicao_jogo2': pred_acertos_j2,
                'confianca_jogo1': min(0.95, 0.5 + abs(pred_acertos_j1 - 11) * 0.1),
                'confianca_jogo2': min(0.95, 0.5 + abs(pred_acertos_j2 - 11) * 0.1),
                'tendencia_j1': tendencia_j1,
                'tendencia_j2': tendencia_j2
            }
            
            print(f"🎯 PREDIÇÕES:")
            print(f"   Jogo 1: {pred_acertos_j1:.0f} acertos (confiança: {resultado['confianca_jogo1']:.1%})")
            print(f"   Jogo 2: {pred_acertos_j2:.0f} acertos (confiança: {resultado['confianca_jogo2']:.1%})")
            print(f"📊 Tendências: J1={tendencia_j1:+.2f}, J2={tendencia_j2:+.2f}")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Erro na predição: {e}")
            return {}
    
    def gerar_combinacao_otimizada(self, foco_15_acertos: bool = True) -> List[int]:
        """Gera combinação de 20 números otimizada para maximizar 15 acertos"""
        print(f"\n🎯 GERANDO COMBINAÇÃO OTIMIZADA (Foco: {'15 acertos' if foco_15_acertos else 'múltiplos acertos'})")
        print("=" * 70)
        
        try:
            # Integração com sistemas existentes
            combinacao_base = []
            
            # 1. Se disponível, usa insights da pirâmide
            if self.usar_piramide and self.piramide_sistema:
                try:
                    # Análise atual da pirâmide
                    piramide_atual = self.piramide_sistema.analisar_piramide_atual()
                    
                    # Números saindo de faixas baixas (alta prioridade para 15 acertos)
                    if '0_acertos' in piramide_atual:
                        combinacao_base.extend(piramide_atual['0_acertos'][:2])
                    
                    if '1_acerto' in piramide_atual:
                        combinacao_base.extend(piramide_atual['1_acerto'][:3])
                    
                    print(f"🔺 Pirâmide contribuiu com {len(combinacao_base)} números prioritários")
                    
                except Exception as e:
                    print(f"⚠️ Erro na integração com pirâmide: {e}")
            
            # 2. Análise dos jogos históricos para identificar padrões
            numeros_mais_eficazes = self._analisar_numeros_eficazes_15_acertos()
            
            # 3. Combina estratégias
            combinacao_final = list(set(combinacao_base))
            
            # Adiciona números mais eficazes até completar 20
            for numero in numeros_mais_eficazes:
                if len(combinacao_final) >= 20:
                    break
                if numero not in combinacao_final:
                    combinacao_final.append(numero)
            
            # Completa com números estratégicos se necessário
            if len(combinacao_final) < 20:
                numeros_complementares = [n for n in range(1, 26 if n not in combinacao_final]
                # Prioriza números do meio (estatisticamente mais frequentes)
                numeros_complementares.sort(key=lambda x: abs(x - 13))
                combinacao_final.extend(numeros_complementares[:20-len(combinacao_final)])
            
            combinacao_final = sorted(combinacao_final[:20])
            
            print(f"✅ Combinação otimizada gerada: {combinacao_final}")
            print(f"📊 Estratégia: {'Foco máximo em 15 acertos' if foco_15_acertos else 'Balanceada para múltiplos acertos'}")
            
            return combinacao_final
            
        except Exception as e:
            print(f"❌ Erro ao gerar combinação: {e}")
            # Fallback: combinação estratégica básica
            return [1), int(2, 3, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 25]
    
    def _analisar_numeros_eficazes_15_acertos(self)) -> List[int]:
        """Analisa quais números são mais eficazes para conseguir 15 acertos"""
        # Conta frequência de cada número nos concursos onde houve 15 acertos
        contador_15_acertos = Counter()
        
        if not self.dados_carregados or self.dados_concursos is None:
            # Retorna distribuição teórica
            return [1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 25]
        
        # Busca concursos com 15 acertos para os jogos
        concursos_15_acertos = []
        
        for concurso, hist_j1 in self.historico_jogo_1.items():
            if hist_j1.get('total_acertos', 0) == 15:
                concursos_15_acertos.append(concurso)
        
        for concurso, hist_j2 in self.historico_jogo_2.items():
            if hist_j2.get('total_acertos', 0) == 15:
                if concurso not in concursos_15_acertos:
                    concursos_15_acertos.append(concurso)
        
        # Analisa frequência nos concursos de 15 acertos
        for concurso in concursos_15_acertos:
            concurso_data = self.dados_concursos[self.dados_concursos['Concurso'] == concurso]
            if len(concurso_data) > 0:
                numeros_sorteados = [
                    int(concurso_data.iloc[0][f'N{i}']) for i in range(1, 16
                ]
                contador_15_acertos.update(numeros_sorteados)
        
        # Retorna números mais frequentes nos 15 acertos
        numeros_eficazes = [n for n), int(_ in contador_15_acertos.most_common(20))]
        
        if len(numeros_eficazes) < 20:
            # Completa com números estatisticamente balanceados
            faltantes = [n for n in range(1, 26 if n not in numeros_eficazes]
            numeros_eficazes.extend(faltantes[:20-len(numeros_eficazes)])
        
        return numeros_eficazes[:20]
    
    def executar_ciclo_completo(self, int(range_treino_inicio: int, range_treino_fim: int, 
                              range_teste_inicio: int, range_teste_fim: int)) -> bool:
        """Executa ciclo completo: análise -> treino -> teste -> predição"""
        print(f"\n🚀 EXECUTANDO CICLO COMPLETO DE ANÁLISE PREDITIVA")
        print("=" * 80)
        print(f"📚 Treino: Concursos {range_treino_inicio} a {range_treino_fim}")
        print(f"🧪 Teste: Concursos {range_teste_inicio} a {range_teste_fim}")
        
        # Verifica se já foi processado
        for inicio, fim, tipo in self.ranges_processados:
            if (inicio == range_treino_inicio and fim == range_treino_fim and 
                tipo in ['ciclo_completo', 'analise_historica']):
                print(f"⚠️ Range de treino {inicio}-{fim} já foi processado!")
                resposta = input("Continuar mesmo assim? (s/n): ").lower()
                if not resposta.startswith('s'):
                    return False
                break
        
        # 1. Análise do histórico de treino
        print(f"\n📊 ETAPA 1: Análise histórica de treino")
        if not self.analisar_historico_completo(range_treino_inicio, range_treino_fim):
            print("❌ Falha na análise histórica")
            return False
        
        # 2. Análise do range de teste
        print(f"\n📊 ETAPA 2: Análise histórica de teste")
        if not self.analisar_historico_completo(range_teste_inicio, range_teste_fim):
            print("❌ Falha na análise do range de teste")
            return False
        
        # 3. Treinamento dos modelos
        print(f"\n🧠 ETAPA 3: Treinamento de IA")
        if not self.treinar_modelos_predicao(range_treino_inicio, range_treino_fim):
            print("❌ Falha no treinamento")
            return False
        
        # 4. Validação no range de teste
        print(f"\n🧪 ETAPA 4: Validação nos dados de teste")
        acuracia_validacao = self._validar_predicoes(range_teste_inicio, range_teste_fim)
        
        # 5. Predições para o futuro
        proximo_concurso = range_teste_fim + 1
        print(f"\n🔮 ETAPA 5: Predição para concurso {proximo_concurso}")
        predicoes = self.prever_acertos_futuros(proximo_concurso)
        
        # 6. Gera combinação otimizada
        print(f"\n🎯 ETAPA 6: Geração de combinação otimizada")
        combinacao_otimizada = self.gerar_combinacao_otimizada(foco_15_acertos=True)
        
        # 7. Relatório final
        self._gerar_relatorio_final(range_treino_inicio, range_treino_fim, 
                                  range_teste_inicio, range_teste_fim,
                                  acuracia_validacao, predicoes, combinacao_otimizada)
        
        # Atualiza estado
        self.ranges_processados.append((range_treino_inicio, range_treino_fim, 'ciclo_completo'))
        self.ultimo_concurso_testado = range_teste_fim
        self._salvar_estado()
        
        return True
    
    def _validar_predicoes(self, inicio: int, fim: int) -> Dict[str, float]:
        """Valida acurácia das predições no range de teste"""
        print("🔍 Validando predições...")
        
        predicoes_j1 = []
        predicoes_j2 = []
        reais_j1 = []
        reais_j2 = []
        
        for concurso in range(int(int(inicio)), int(int(fim + 1):
            if concurso in self.historico_jogo_1 and concurso in self.historico_jogo_2:
                # Simula predição para este concurso
                try:
                    resultado = self.prever_acertos_futuros(concurso)
                    if resultado:
                        predicoes_j1.append(resultado['predicao_jogo1'])
                        predicoes_j2.append(resultado['predicao_jogo2'])
                        
                        reais_j1.append(self.historico_jogo_1[concurso]['total_acertos'])
                        reais_j2.append(self.historico_jogo_2[concurso]['total_acertos'])
                except:
                    continue
        
        if len(predicoes_j1) == 0:
            return {'mse_jogo1': 999), int('mse_jogo2': 999}
        
        mse_j1 = mean_squared_error(reais_j1, predicoes_j1))
        mse_j2 = mean_squared_error(reais_j2, predicoes_j2)
        
        print(f"📊 Validação - MSE Jogo 1: {mse_j1:.3f}, MSE Jogo 2: {mse_j2:.3f}")
        
        return {'mse_jogo1': mse_j1, 'mse_jogo2': mse_j2, 'amostras': len(predicoes_j1)}
    
    def _gerar_relatorio_final(self, treino_i: int, treino_f: int, teste_i: int, teste_f: int,
                              validacao: Dict, predicoes: Dict, combinacao: List[int]):
        """Gera relatório final do ciclo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_analisador_preditivo_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🧠 RELATÓRIO ANALISADOR PREDITIVO AVANÇADO\n")
                f.write("=" * 70 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                f.write("📊 CONFIGURAÇÃO DO CICLO:\n")
                f.write("-" * 30 + "\n")
                f.write(f"• Range de Treino: Concursos {treino_i} a {treino_f}\n")
                f.write(f"• Range de Teste: Concursos {teste_i} a {teste_f}\n")
                f.write(f"• Total Concursos Analisados: {(treino_f-treino_i+1) + (teste_f-teste_i+1)}\n\n")
                
                f.write("🎯 JOGOS TESTADOS:\n")
                f.write("-" * 20 + "\n")
                f.write(f"• Jogo 1: {self.jogo_1}\n")
                f.write(f"• Jogo 2: {self.jogo_2}\n\n")
                
                f.write("📈 RESULTADOS DA VALIDAÇÃO:\n")
                f.write("-" * 30 + "\n")
                f.write(f"• MSE Jogo 1: {validacao.get('mse_jogo1', 'N/A'):.3f}\n")
                f.write(f"• MSE Jogo 2: {validacao.get('mse_jogo2', 'N/A'):.3f}\n")
                f.write(f"• Amostras de Validação: {validacao.get('amostras', 'N/A')}\n\n")
                
                if predicoes:
                    f.write("🔮 PREDIÇÕES PARA O FUTURO:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"• Concurso Alvo: {predicoes.get('concurso_alvo', 'N/A')}\n")
                    f.write(f"• Predição Jogo 1: {predicoes.get('predicao_jogo1', 'N/A')} acertos\n")
                    f.write(f"• Predição Jogo 2: {predicoes.get('predicao_jogo2', 'N/A')} acertos\n")
                    f.write(f"• Confiança J1: {predicoes.get('confianca_jogo1', 0):.1%}\n")
                    f.write(f"• Confiança J2: {predicoes.get('confianca_jogo2', 0):.1%}\n\n")
                
                f.write("🎯 COMBINAÇÃO OTIMIZADA GERADA:\n")
                f.write("-" * 35 + "\n")
                f.write(f"• Números: {combinacao}\n")
                f.write(f"• Estratégia: Foco máximo em 15 acertos\n")
                f.write(f"• Base: IA + Pirâmide Invertida + Análise Histórica\n\n")
                
                f.write("💾 CONTROLE DE ESTADO:\n")
                f.write("-" * 25 + "\n")
                f.write(f"• Último Treino: Concurso {self.ultimo_concurso_treinado}\n")
                f.write(f"• Último Teste: Concurso {self.ultimo_concurso_testado}\n")
                f.write(f"• Ranges Processados: {len(self.ranges_processados)}\n")
                
            print(f"📄 Relatório salvo: {nome_arquivo}")
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
    
    def mostrar_status_sistema(self):
        """Mostra status atual do sistema"""
        print("\n📊 STATUS DO ANALISADOR PREDITIVO AVANÇADO")
        print("=" * 60)
        print(f"🔄 Último Treino: Concurso {self.ultimo_concurso_treinado}")
        print(f"🧪 Último Teste: Concurso {self.ultimo_concurso_testado}")
        print(f"📚 Ranges Processados: {len(self.ranges_processados)}")
        print(f"📊 Histórico Jogo 1: {len(self.historico_jogo_1)} concursos")
        print(f"📊 Histórico Jogo 2: {len(self.historico_jogo_2)} concursos")
        print(f"🔺 Pirâmide Integrada: {'✅ Sim' if self.usar_piramide else '❌ Não'}")
        print(f"💾 Dados Carregados: {'✅ Sim' if self.dados_carregados else '❌ Não'}")
        
        if self.ranges_processados:
            print(f"\n📋 HISTÓRICO DE RANGES PROCESSADOS:")
            for i, (inicio, fim, tipo) in enumerate(self.ranges_processados[-5:], 1):
                print(f"   {i}. {inicio}-{fim} ({tipo})")

def main():
    """Função principal - Interface do usuário"""
    print("🧠 ANALISADOR PREDITIVO AVANÇADO")
    print("=" * 50)
    
    analisador = AnalisadorPreditivoAvancado()
    
    while True:
        print(f"\n📋 MENU DE OPÇÕES:")
        print("1. Executar ciclo completo (treino + teste + predição)")
        print("2. Análise histórica apenas")
        print("3. Predizer acertos para concurso específico")
        print("4. Gerar combinação otimizada")
        print("5. Mostrar status do sistema")
        print("6. Sair")
        
        try:
            opcao = input("\nEscolha uma opção (1-6): ").strip()
            
            if opcao == "1":
                print(f"\n🚀 CICLO COMPLETO")
                treino_i = int(input("Concurso inicial para treino: "))
                treino_f = int(input("Concurso final para treino: "))
                teste_i = int(input("Concurso inicial para teste: "))
                teste_f = int(input("Concurso final para teste: "))
                
                analisador.executar_ciclo_completo(treino_i, treino_f, teste_i, teste_f)
            
            elif opcao == "2":
                print(f"\n📊 ANÁLISE HISTÓRICA")
                inicio = int(input("Concurso inicial: "))
                fim = int(input("Concurso final: "))
                
                analisador.analisar_historico_completo(inicio, fim)
            
            elif opcao == "3":
                print(f"\n🔮 PREDIÇÃO")
                concurso = int(input("Concurso para predição: "))
                
                resultado = analisador.prever_acertos_futuros(concurso)
                if not resultado:
                    print("❌ Falha na predição. Verifique se há dados suficientes.")
            
            elif opcao == "4":
                print(f"\n🎯 COMBINAÇÃO OTIMIZADA")
                combinacao = analisador.gerar_combinacao_otimizada()
                print(f"✅ Sugestão: {combinacao}")
            
            elif opcao == "5":
                analisador.mostrar_status_sistema()
            
            elif opcao == "6":
                print("👋 Saindo do sistema...")
                break
            
            else:
                print("❌ Opção inválida!")
                
        except ValueError:
            print("❌ Valor inválido! Digite apenas números.")
        except KeyboardInterrupt:
            print("\n⏹️ Processo cancelado pelo usuário")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
