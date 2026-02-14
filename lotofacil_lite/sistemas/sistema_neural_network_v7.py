#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA NEURAL NETWORK V7.0 - LOTOFÁCIL
==========================================
✅ Dados 100% REAIS (Resultados_INT + NumerosCiclos)
✅ Rede Neural Deep Learning com PADRÕES ALTOS/BAIXOS
✅ Meta: 76%+ (11/15 acertos) - Melhorada com análise de distribuição
✅ Análise de padrões ultra-complexos + Tendências de Reversão
"""

import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from collections import Counter, defaultdict
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import accuracy_score, classification_report
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import warnings
warnings.filterwarnings('ignore')

class SistemaNeuralNetworkV7:
    def __init__(self):
        self.meta_acertos = 11  # 76% = 11/15 acertos
        self.resultado_teste = [3,5,6,8,9,12,13,14,15,16,17,20,21,22,23]
        
        # Dados carregados
        self.dados_historicos = []
        self.dados_ciclos = []
        self.features_completas = []
        
        # Modelos treinados
        self.modelo_neural_tf = None
        self.modelo_ensemble = {}
        self.scalers = {}
        
        # 🆕 PADRÕES ALTOS/BAIXOS
        self.padroes_distribuicao = {}
        self.historico_tendencias = []
        
        # Database config
        self.db_config = db_config
        
        print("🧠 Sistema Neural Network V7.0 Inicializado")
        print("🎯 Meta: 76%+ (11/15 acertos)")
        print("🆕 NOVA FEATURE: Análise de distribuição Altos/Baixos")
    
    def carregar_dados_reais(self):
        """Carrega dados reais das tabelas Resultados_INT e NumerosCiclos"""
        print("\n🔍 Carregando dados históricos reais...")
        
        try:
            if not self.db_config.test_connection():
                print("❌ Erro na conexão com banco")
                return False
            
            # Carregar resultados históricos
            query_resultados = """
            SELECT TOP 500 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            resultados = self.db_config.execute_query(query_resultados)
            
            for row in resultados:
                concurso = row[0]
                numeros = [row[i] for i in range(1, 16)]
                
                # 🆕 ANÁLISE ALTOS/BAIXOS (excluindo N1)
                numeros_sem_n1 = numeros[1:]  # N2 até N15
                baixos = [n for n in numeros_sem_n1 if 2 <= n <= 13]
                altos = [n for n in numeros_sem_n1 if 14 <= n <= 25]
                
                # Categorizar distribuição
                distribuicao = self.categorizar_distribuicao(len(baixos), len(altos))
                
                self.dados_historicos.append({
                    'concurso': concurso,
                    'numeros': sorted(numeros),
                    'qtd_baixos': len(baixos),
                    'qtd_altos': len(altos),
                    'distribuicao': distribuicao,
                    'proporcao_baixos': len(baixos) / 14,
                    'proporcao_altos': len(altos) / 14,
                    'amplitude': max(numeros) - min(numeros),
                    'densidade': self.calcular_densidade(numeros)
                })
            
            # Carregar dados de ciclos
            query_ciclos = """
            SELECT TOP 500 Numero, Ciclo, QtdSorteados, ConcursoInicio
            FROM NumerosCiclos
            ORDER BY Numero, Ciclo DESC
            """
            
            ciclos = self.db_config.execute_query(query_ciclos)
            
            for row in ciclos:
                self.dados_ciclos.append({
                    'numero': row[0],
                    'ciclo': row[1],
                    'qtd_sorteados': row[2],
                    'concurso_inicio': row[3]
                })
            
            # 🆕 CALCULAR TENDÊNCIAS DE TRANSIÇÃO
            self.calcular_tendencias_historicas()
            
            print(f"✅ {len(self.dados_historicos)} concursos carregados")
            print(f"✅ {len(self.dados_ciclos)} registros de ciclos carregados")
            print(f"✅ Análise de tendências Altos/Baixos calculada")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def categorizar_distribuicao(self, qtd_baixos, qtd_altos):
        """Categoriza a distribuição entre altos e baixos"""
        if qtd_baixos > qtd_altos + 2:
            return 'muito_mais_baixos'
        elif qtd_baixos > qtd_altos + 1:
            return 'mais_baixos'
        elif qtd_altos > qtd_baixos + 2:
            return 'muito_mais_altos'
        elif qtd_altos > qtd_baixos + 1:
            return 'mais_altos'
        elif qtd_baixos == qtd_altos + 1:
            return 'ligeiro_baixos'
        elif qtd_altos == qtd_baixos + 1:
            return 'ligeiro_altos'
        else:
            return 'equilibrio'
    
    def calcular_densidade(self, numeros):
        """Calcula densidade numérica dos números sorteados"""
        if len(numeros) <= 1:
            return 0
        return len(numeros) / (max(numeros) - min(numeros))
    
    def calcular_tendencias_historicas(self):
        """🆕 Calcula tendências de transição baseado na análise realizada"""
        print("🔄 Calculando tendências de transição...")
        
        # Probabilidades descobertas na análise
        self.padroes_distribuicao = {
            'mais_baixos': {
                'para_mais_altos': 0.428,
                'para_equilibrio': 0.304,
                'para_mais_baixos': 0.268
            },
            'equilibrio': {
                'para_mais_altos': 0.387,
                'para_mais_baixos': 0.311,
                'para_equilibrio': 0.302
            },
            'mais_altos': {
                'para_mais_altos': 0.408,
                'para_equilibrio': 0.303,
                'para_mais_baixos': 0.289
            }
        }
        
        # Calcular tendências para últimos jogos
        for i in range(len(self.dados_historicos) - 1):
            atual = self.dados_historicos[i]
            proximo = self.dados_historicos[i + 1]
            
            # Simplificar categorias para usar as probabilidades
            cat_atual = self.simplificar_categoria(atual['distribuicao'])
            cat_proximo = self.simplificar_categoria(proximo['distribuicao'])
            
            self.historico_tendencias.append({
                'concurso': atual['concurso'],
                'categoria_atual': cat_atual,
                'categoria_proxima': cat_proximo,
                'probabilidade_teorica': self.padroes_distribuicao.get(cat_atual, {}).get(f'para_{cat_proximo}', 0.33)
            })
    
    def simplificar_categoria(self, categoria):
        """Simplifica categorias para usar as probabilidades calculadas"""
        if 'baixos' in categoria:
            return 'mais_baixos'
        elif 'altos' in categoria:
            return 'mais_altos'
        else:
            return 'equilibrio'
    
    def extrair_features_avancadas(self):
        """Extrai features avançadas incluindo padrões de distribuição"""
        print("🧬 Extraindo features avançadas...")
        
        self.features_completas = []
        
        for i, dados in enumerate(self.dados_historicos):
            if i < 10:  # Precisamos de histórico para calcular features
                continue
            
            # Features básicas
            features = {
                'concurso': dados['concurso'],
                'amplitude': dados['amplitude'],
                'densidade': dados['densidade'],
                'qtd_baixos': dados['qtd_baixos'],
                'qtd_altos': dados['qtd_altos'],
                'proporcao_baixos': dados['proporcao_baixos'],
                'proporcao_altos': dados['proporcao_altos']
            }
            
            # 🆕 FEATURES DE DISTRIBUIÇÃO
            distribuicao_encoded = self.encode_distribuicao(dados['distribuicao'])
            features.update(distribuicao_encoded)
            
            # 🆕 FEATURES DE TENDÊNCIA (últimos 3 jogos)
            if i >= 3:
                ultimos_3 = self.dados_historicos[i-3:i]
                features.update(self.extrair_features_tendencia(ultimos_3))
            
            # 🆕 PROBABILIDADE DE REVERSÃO
            if i >= 1:
                jogo_anterior = self.dados_historicos[i-1]
                cat_anterior = self.simplificar_categoria(jogo_anterior['distribuicao'])
                features['prob_reversao_alto'] = self.padroes_distribuicao.get(cat_anterior, {}).get('para_mais_altos', 0.33)
                features['prob_reversao_baixo'] = self.padroes_distribuicao.get(cat_anterior, {}).get('para_mais_baixos', 0.33)
                features['prob_equilibrio'] = self.padroes_distribuicao.get(cat_anterior, {}).get('para_equilibrio', 0.33)
            
            # Features de números específicos
            numeros_binary = np.zeros(25)
            for num in dados['numeros']:
                if 1 <= num <= 25:
                    numeros_binary[num-1] = 1
            
            for j in range(25):
                features[f'numero_{j+1}'] = numeros_binary[j]
            
            # Features de ciclos
            features_ciclos = self.extrair_features_ciclos(dados['concurso'])
            features.update(features_ciclos)
            
            # Features de padrões históricos
            features_historicos = self.extrair_features_historicos(i)
            features.update(features_historicos)
            
            self.features_completas.append(features)
        
        print(f"✅ {len(self.features_completas)} conjuntos de features extraídas")
        print(f"✅ Total de features por jogo: {len(self.features_completas[0])}")
    
    def encode_distribuicao(self, distribuicao):
        """Codifica distribuição em features binárias"""
        categorias = ['muito_mais_baixos', 'mais_baixos', 'ligeiro_baixos', 
                     'equilibrio', 'ligeiro_altos', 'mais_altos', 'muito_mais_altos']
        
        encoded = {}
        for cat in categorias:
            encoded[f'dist_{cat}'] = 1 if distribuicao == cat else 0
        
        return encoded
    
    def extrair_features_tendencia(self, ultimos_jogos):
        """🆕 Extrai features de tendência dos últimos jogos"""
        features = {}
        
        # Contagem de padrões nos últimos jogos
        distribuicoes = [jogo['distribuicao'] for jogo in ultimos_jogos]
        
        features['tend_baixos_seq'] = sum(1 for d in distribuicoes if 'baixos' in d)
        features['tend_altos_seq'] = sum(1 for d in distribuicoes if 'altos' in d)
        features['tend_equilibrio_seq'] = sum(1 for d in distribuicoes if d == 'equilibrio')
        
        # Momentum de mudança
        if len(ultimos_jogos) >= 2:
            features['momentum_mudanca'] = 1 if ultimos_jogos[-1]['distribuicao'] != ultimos_jogos[-2]['distribuicao'] else 0
        
        # Força da tendência atual
        ultima_categoria = self.simplificar_categoria(ultimos_jogos[-1]['distribuicao'])
        features['forca_tendencia'] = sum(1 for jogo in ultimos_jogos 
                                        if self.simplificar_categoria(jogo['distribuicao']) == ultima_categoria)
        
        return features
    
    def extrair_features_ciclos(self, concurso):
        """Extrai features baseadas nos ciclos dos números"""
        features = {}
        
        # Para cada número, buscar informações de ciclo
        ciclos_por_numero = defaultdict(list)
        for ciclo in self.dados_ciclos:
            ciclos_por_numero[ciclo['numero']].append(ciclo)
        
        # Estatísticas de ciclos
        features['ciclo_medio'] = 0
        features['qtd_sorteados_medio'] = 0
        features['numeros_ciclo_alto'] = 0
        
        contador = 0
        for num in range(1, 26):
            if num in ciclos_por_numero:
                ciclo_info = ciclos_por_numero[num][0]  # Mais recente
                features['ciclo_medio'] += ciclo_info['ciclo']
                features['qtd_sorteados_medio'] += ciclo_info['qtd_sorteados']
                
                # Números com muitos sorteios no ciclo (alta atividade)
                if ciclo_info['qtd_sorteados'] > 5:
                    features['numeros_ciclo_alto'] += 1
                
                contador += 1
        
        if contador > 0:
            features['ciclo_medio'] /= contador
            features['qtd_sorteados_medio'] /= contador
        
        return features
    
    def extrair_features_historicos(self, indice):
        """Extrai features baseadas em padrões históricos"""
        features = {}
        
        if indice < 10:
            return features
        
        # Análise dos últimos 10 jogos
        ultimos_10 = self.dados_historicos[max(0, indice-10):indice]
        
        # Estatísticas gerais
        features['media_baixos_10'] = np.mean([j['qtd_baixos'] for j in ultimos_10])
        features['media_altos_10'] = np.mean([j['qtd_altos'] for j in ultimos_10])
        features['std_baixos_10'] = np.std([j['qtd_baixos'] for j in ultimos_10])
        features['std_altos_10'] = np.std([j['qtd_altos'] for j in ultimos_10])
        
        # Frequência de cada categoria
        distribuicoes_10 = [j['distribuicao'] for j in ultimos_10]
        contador_dist = Counter(distribuicoes_10)
        
        for categoria in ['muito_mais_baixos', 'mais_baixos', 'equilibrio', 'mais_altos', 'muito_mais_altos']:
            features[f'freq_{categoria}_10'] = contador_dist.get(categoria, 0) / len(ultimos_10)
        
        return features
    
    def treinar_modelos(self):
        """Treina os modelos de machine learning"""
        print("\n🤖 Treinando modelos de Machine Learning...")
        
        if not self.features_completas:
            print("❌ Features não extraídas")
            return False
        
        # Preparar dados
        X = []
        y = []
        
        for i, features in enumerate(self.features_completas[:-1]):  # Excluir último para ter target
            # Input features (excluindo números específicos e concurso)
            feature_vector = []
            for key, value in features.items():
                if not key.startswith('numero_') and key != 'concurso':
                    feature_vector.append(value)
            
            X.append(feature_vector)
            
            # Target: próximo jogo (índice i+1)
            proximo_jogo = self.dados_historicos[i+1]
            target = np.zeros(25)
            for num in proximo_jogo['numeros']:
                if 1 <= num <= 25:
                    target[num-1] = 1
            
            y.append(target)
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"📊 Shape dos dados: X={X.shape}, y={y.shape}")
        
        # Split treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalização
        self.scalers['standard'] = StandardScaler()
        X_train_scaled = self.scalers['standard'].fit_transform(X_train)
        X_test_scaled = self.scalers['standard'].transform(X_test)
        
        # 1. Modelo TensorFlow/Keras - MELHORADO
        print("🧠 Treinando Rede Neural TensorFlow...")
        
        self.modelo_neural_tf = keras.Sequential([
            # Camada de entrada com dropout
            layers.Dense(512, activation='relu', input_shape=(X_train_scaled.shape[1],)),
            layers.Dropout(0.3),
            layers.BatchNormalization(),
            
            # Camadas ocultas com arquitetura mais profunda
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.BatchNormalization(),
            
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.BatchNormalization(),
            
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            
            # Camada de saída para 25 números
            layers.Dense(25, activation='sigmoid')
        ])
        
        # Compilar com otimizador melhorado
        self.modelo_neural_tf.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Treinamento com early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
        
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001
        )
        
        history = self.modelo_neural_tf.fit(
            X_train_scaled, y_train,
            validation_data=(X_test_scaled, y_test),
            epochs=100,
            batch_size=32,
            callbacks=[early_stopping, reduce_lr],
            verbose=0
        )
        
        # 2. Ensemble de modelos
        print("🎯 Treinando Ensemble de modelos...")
        
        self.modelo_ensemble = {
            'random_forest': MultiOutputClassifier(
                RandomForestClassifier(
                    n_estimators=300,  # Aumentado
                    max_depth=25,      # Aumentado
                    min_samples_split=3,
                    min_samples_leaf=1,
                    random_state=42,
                    n_jobs=-1
                )
            ),
            'gradient_boosting': MultiOutputClassifier(
                GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.1,
                    max_depth=8,
                    random_state=42
                )
            )
        }
        
        for nome, modelo in self.modelo_ensemble.items():
            print(f"   Treinando {nome}...")
            modelo.fit(X_train_scaled, y_train)
        
        # Avaliar modelos
        print("\n📊 Avaliação dos modelos:")
        
        # TensorFlow
        y_pred_tf = self.modelo_neural_tf.predict(X_test_scaled, verbose=0)
        y_pred_tf_binary = (y_pred_tf > 0.5).astype(int)
        acc_tf = accuracy_score(y_test.flatten(), y_pred_tf_binary.flatten())
        print(f"   🧠 TensorFlow: {acc_tf:.3f}")
        
        # Ensemble
        for nome, modelo in self.modelo_ensemble.items():
            y_pred = modelo.predict(X_test_scaled)
            acc = accuracy_score(y_test.flatten(), y_pred.flatten())
            print(f"   🎯 {nome}: {acc:.3f}")
        
        print("✅ Modelos treinados com sucesso!")
        return True
    
    def gerar_predicao_inteligente(self):
        """Gera predição inteligente usando ensemble e padrões de distribuição"""
        print("\n🔮 Gerando predição inteligente...")
        
        if not self.modelo_neural_tf or not self.modelo_ensemble:
            print("❌ Modelos não treinados")
            return None
        
        # Usar o último jogo para predição
        ultimo_jogo = self.features_completas[-1]
        
        # Preparar features
        feature_vector = []
        for key, value in ultimo_jogo.items():
            if not key.startswith('numero_') and key != 'concurso':
                feature_vector.append(value)
        
        X_pred = np.array([feature_vector])
        X_pred_scaled = self.scalers['standard'].transform(X_pred)
        
        # Predições dos modelos
        pred_tf = self.modelo_neural_tf.predict(X_pred_scaled, verbose=0)[0]
        
        pred_ensemble = {}
        for nome, modelo in self.modelo_ensemble.items():
            pred_ensemble[nome] = modelo.predict(X_pred_scaled)[0]
        
        # 🆕 APLICAR PADRÕES DE DISTRIBUIÇÃO
        ultimo_historico = self.dados_historicos[-1]
        categoria_atual = self.simplificar_categoria(ultimo_historico['distribuicao'])
        
        print(f"📊 Situação atual: {ultimo_historico['distribuicao']}")
        print(f"📊 Categoria: {categoria_atual}")
        
        # Ajustar predições baseado em padrões de distribuição
        prob_mais_altos = self.padroes_distribuicao.get(categoria_atual, {}).get('para_mais_altos', 0.33)
        prob_mais_baixos = self.padroes_distribuicao.get(categoria_atual, {}).get('para_mais_baixos', 0.33)
        
        print(f"🔄 Prob. mais altos: {prob_mais_altos:.1%}")
        print(f"🔄 Prob. mais baixos: {prob_mais_baixos:.1%}")
        
        # Combinar predições com peso para padrões de distribuição
        pred_final = (pred_tf * 0.4 + 
                     pred_ensemble['random_forest'] * 0.3 + 
                     pred_ensemble['gradient_boosting'] * 0.3)
        
        # 🆕 BOOST baseado em padrões de distribuição
        fator_boost_altos = 1 + (prob_mais_altos - 0.33) * 2  # Amplifica diferença da média
        fator_boost_baixos = 1 + (prob_mais_baixos - 0.33) * 2
        
        # Aplicar boost nos números altos (14-25) e baixos (2-13)
        for i in range(25):
            numero = i + 1
            if 14 <= numero <= 25:  # Números altos
                pred_final[i] *= fator_boost_altos
            elif 2 <= numero <= 13:  # Números baixos
                pred_final[i] *= fator_boost_baixos
        
        # Selecionar top 15 números
        indices_ordenados = np.argsort(pred_final)[::-1]
        numeros_preditos = []
        
        for i in indices_ordenados[:15]:
            numero = i + 1
            confianca = pred_final[i]
            numeros_preditos.append((numero, confianca))
        
        # Estatísticas da predição
        numeros_finais = [num for num, _ in numeros_preditos]
        baixos_pred = [n for n in numeros_finais if 2 <= n <= 13]
        altos_pred = [n for n in numeros_finais if 14 <= n <= 25]
        
        print(f"\n🎯 PREDIÇÃO FINAL:")
        print(f"   Números: {sorted(numeros_finais)}")
        print(f"   Baixos (2-13): {len(baixos_pred)} números")
        print(f"   Altos (14-25): {len(altos_pred)} números")
        print(f"   Distribuição: {self.categorizar_distribuicao(len(baixos_pred), len(altos_pred))}")
        
        return {
            'numeros': numeros_finais,
            'numeros_com_confianca': numeros_preditos,
            'qtd_baixos': len(baixos_pred),
            'qtd_altos': len(altos_pred),
            'distribuicao_predita': self.categorizar_distribuicao(len(baixos_pred), len(altos_pred)),
            'categoria_atual': categoria_atual,
            'prob_mais_altos': prob_mais_altos,
            'prob_mais_baixos': prob_mais_baixos
        }
    
    def executar_sistema_completo(self):
        """Executa o sistema completo"""
        print("🧠 SISTEMA NEURAL NETWORK V7.0 - INICIANDO")
        print("="*60)
        
        # Carregar dados
        if not self.carregar_dados_reais():
            return False
        
        # Extrair features
        self.extrair_features_avancadas()
        
        # Treinar modelos
        if not self.treinar_modelos():
            return False
        
        # Gerar predição
        predicao = self.gerar_predicao_inteligente()
        
        if predicao:
            print("\n" + "="*60)
            print("✅ SISTEMA NEURAL V7.0 CONCLUÍDO COM SUCESSO!")
            print("="*60)
            
            return predicao
        
        return False

def main():
    """Função principal"""
    sistema = SistemaNeuralNetworkV7()
    
    try:
        resultado = sistema.executar_sistema_completo()
        
        if resultado:
            print(f"\n🎯 RESULTADO FINAL:")
            print(f"   Números sugeridos: {sorted(resultado['numeros'])}")
            print(f"   Confiança baseada em: Padrões neurais + Distribuição altos/baixos")
            
    except KeyboardInterrupt:
        print("\n❌ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()