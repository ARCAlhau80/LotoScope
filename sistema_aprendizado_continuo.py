#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA DE APRENDIZADO CONTÍNUO AUTOMATIZADO
==============================================
Inspirado em "Automated Continual Learning" - AutoGen Framework
Sistema que aprende e se adapta continuamente aos novos padrões da Lotofácil
"""

import pyodbc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import pickle
import os
import time
import threading
from collections import defaultdict, deque
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

class SistemaAprendizadoContinuo:
    """🧠 Sistema de aprendizado contínuo automatizado"""
    
    def __init__(self):
        self.conexao = None
        self.dados_historicos = None
        self.modelos_ativos = {}
        self.pipeline_aprendizado = {}
        self.conhecimento_base = {}
        self.memoria_adaptativa = deque(maxlen=1000)
        self.metricas_evolucao = defaultdict(list)
        
        # Configuração do sistema de aprendizado
        self.config = {
            'batch_size': 50,               # Tamanho do lote para retreino
            'threshold_mudanca': 0.15,      # 15% de mudança para retreino
            'intervalo_avaliacao': 10,      # Avaliações a cada N concursos
            'memoria_maxima': 1000,         # Máximo na memória adaptativa
            'taxa_esquecimento': 0.05,      # 5% de esquecimento por ciclo
            'modelos_ensemble': 5,          # Número de modelos no ensemble
        }
        
        # Métricas de adaptação
        self.adaptation_metrics = {
            'concept_drift_detected': 0,
            'successful_adaptations': 0,
            'learning_cycles': 0,
            'knowledge_retention': 1.0,
            'adaptation_speed': 0.0
        }
        
        # Tipos de conhecimento rastreados
        self.knowledge_types = [
            'frequency_patterns',
            'sequence_patterns', 
            'distribution_patterns',
            'temporal_patterns',
            'correlation_patterns'
        ]
    
    def conectar_banco(self) -> bool:
        """🔌 Conecta ao banco de dados"""
        # Para demonstração, não tenta conectar
        print("✅ Sistema de Aprendizado Contínuo inicializado (modo demonstração)")
        return True
    
    def carregar_dados_historicos(self) -> bool:
        """📊 Carrega dados históricos para aprendizado inicial"""
        # Força uso de dados simulados
        print("⚠️ Usando dados simulados para demonstração")
        return self._gerar_dados_simulados()
    
    def _gerar_dados_simulados(self) -> bool:
        """🎲 Gera dados simulados para demonstração"""
        import random
        
        print("🔄 Gerando dados simulados para aprendizado...")
        
        dados_simulados = []
        for i in range(1000):
            concurso = 3000 + i
            
            # Simula mudanças de padrão ao longo do tempo
            if i < 300:  # Período 1
                bias = [1, 2, 3, 4, 5]  # Favorece números baixos
            elif i < 600:  # Período 2  
                bias = [20, 21, 22, 23, 24, 25]  # Favorece números altos
            else:  # Período 3
                bias = list(range(1, 26))  # Distribuição uniforme
            
            # Gera números com bias
            numeros = set()
            while len(numeros) < 15:
                if random.random() < 0.3:  # 30% chance de usar bias
                    num = random.choice(bias)
                else:
                    num = random.randint(1, 25)
                numeros.add(num)
            
            numeros = sorted(list(numeros))
            
            row = {'Concurso': concurso}
            for j, num in enumerate(numeros):
                row[f'N{j+1}'] = num
            row['SomaTotal'] = sum(numeros)
            
            dados_simulados.append(row)
        
        self.dados_historicos = pd.DataFrame(dados_simulados)
        self._processar_features_aprendizado()
        print("✅ Dados simulados com concept drift gerados")
        return True
    
    def _processar_features_aprendizado(self):
        """🔧 Processa features para o sistema de aprendizado"""
        if self.dados_historicos is None or len(self.dados_historicos) == 0:
            return
        
        print("🔧 Processando features para aprendizado...")
        
        features_dados = []
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        for idx, row in self.dados_historicos.iterrows():
            numeros = [row[col] for col in numeros_cols if pd.notna(row[col])]
            
            if len(numeros) == 15:
                features = {}
                
                # Features básicas
                features['soma_total'] = sum(numeros)
                features['numero_min'] = min(numeros)
                features['numero_max'] = max(numeros)
                features['amplitude'] = max(numeros) - min(numeros)
                
                # Distribuição por dezenas
                features['dezena_1'] = sum(1 for n in numeros if 1 <= n <= 5)
                features['dezena_2'] = sum(1 for n in numeros if 6 <= n <= 10)
                features['dezena_3'] = sum(1 for n in numeros if 11 <= n <= 15)
                features['dezena_4'] = sum(1 for n in numeros if 16 <= n <= 20)
                features['dezena_5'] = sum(1 for n in numeros if 21 <= n <= 25)
                
                # Padrões especiais
                features['numeros_consecutivos'] = self._contar_consecutivos(numeros)
                features['gaps_medios'] = np.mean(np.diff(sorted(numeros)))
                features['paridade'] = sum(1 for n in numeros if n % 2 == 0)
                
                # Features temporais (baseadas no índice)
                features['periodo'] = idx // 100  # Período de 100 concursos
                features['ciclo_semanal'] = idx % 7
                features['tendencia'] = idx / len(self.dados_historicos)
                
                # Adiciona o concurso e timestamp
                features['concurso'] = row['Concurso']
                features['timestamp_idx'] = idx
                
                features_dados.append(features)
        
        self.features_df = pd.DataFrame(features_dados)
        print(f"✅ Features processadas: {len(self.features_df)} registros, {len(self.features_df.columns)} features")
    
    def _contar_consecutivos(self, numeros):
        """Conta sequências consecutivas nos números"""
        numeros_sorted = sorted(numeros)
        consecutivos = 0
        atual = 1
        
        for i in range(1, len(numeros_sorted)):
            if numeros_sorted[i] == numeros_sorted[i-1] + 1:
                atual += 1
            else:
                if atual > consecutivos:
                    consecutivos = atual
                atual = 1
        
        return max(consecutivos, atual) - 1  # -1 porque conta pares
    
    def inicializar_modelos_base(self):
        """🏗️ Inicializa modelos base para aprendizado contínuo"""
        
        print("\n🏗️ INICIALIZANDO MODELOS BASE")
        print("=" * 35)
        
        if not hasattr(self, 'features_df') or len(self.features_df) < 100:
            print("❌ Dados insuficientes para inicialização")
            return False
        
        # Separa dados de treino (80%) e validação (20%)
        split_idx = int(len(self.features_df) * 0.8)
        train_data = self.features_df.iloc[:split_idx]
        val_data = self.features_df.iloc[split_idx:]
        
        # Features para treinamento
        feature_cols = [col for col in self.features_df.columns 
                       if col not in ['concurso', 'timestamp_idx']]
        
        X_train = train_data[feature_cols].fillna(0)
        X_val = val_data[feature_cols].fillna(0)
        
        # Cria labels sintéticas baseadas em padrões
        y_train = self._criar_labels_padrao(train_data)
        y_val = self._criar_labels_padrao(val_data)
        
        # Modelo 1: Detector de Padrões Frequentes
        self.modelos_ativos['frequency_detector'] = {
            'modelo': RandomForestClassifier(n_estimators=100, random_state=42),
            'tipo': 'classification',
            'performance': {'accuracy': 0.0, 'last_update': datetime.now()},
            'drift_score': 0.0
        }
        
        # Modelo 2: Detector de Anomalias
        self.modelos_ativos['anomaly_detector'] = {
            'modelo': IsolationForest(contamination=0.1, random_state=42),
            'tipo': 'anomaly',
            'performance': {'accuracy': 0.0, 'last_update': datetime.now()},
            'drift_score': 0.0
        }
        
        # Modelo 3: Clustering Adaptativo
        self.modelos_ativos['pattern_cluster'] = {
            'modelo': KMeans(n_clusters=5, random_state=42),
            'tipo': 'clustering',
            'performance': {'inertia': 0.0, 'last_update': datetime.now()},
            'drift_score': 0.0
        }
        
        # Treina modelos iniciais
        try:
            # Frequency Detector
            freq_model = self.modelos_ativos['frequency_detector']['modelo']
            freq_model.fit(X_train, y_train)
            y_pred = freq_model.predict(X_val)
            accuracy = accuracy_score(y_val, y_pred)
            self.modelos_ativos['frequency_detector']['performance']['accuracy'] = accuracy
            
            # Anomaly Detector
            anom_model = self.modelos_ativos['anomaly_detector']['modelo']
            anom_model.fit(X_train)
            anomaly_pred = anom_model.predict(X_val)
            accuracy_anom = (anomaly_pred == 1).mean()  # % de normais
            self.modelos_ativos['anomaly_detector']['performance']['accuracy'] = accuracy_anom
            
            # Pattern Cluster
            cluster_model = self.modelos_ativos['pattern_cluster']['modelo']
            cluster_model.fit(X_train)
            inertia = cluster_model.inertia_
            self.modelos_ativos['pattern_cluster']['performance']['inertia'] = inertia
            
            print(f"   ✅ Frequency Detector: {accuracy:.1%} accuracy")
            print(f"   ✅ Anomaly Detector: {accuracy_anom:.1%} normais")
            print(f"   ✅ Pattern Cluster: {inertia:.0f} inertia")
            
            # Inicializa conhecimento base
            self._inicializar_conhecimento_base(train_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
            return False
    
    def _criar_labels_padrao(self, data):
        """Cria labels baseadas em padrões conhecidos"""
        labels = []
        
        for _, row in data.iterrows():
            # Label baseada na distribuição das dezenas
            dezenas = [row['dezena_1'], row['dezena_2'], row['dezena_3'], 
                      row['dezena_4'], row['dezena_5']]
            
            # Classifica padrão de distribuição
            if max(dezenas) >= 5:  # Concentração alta
                label = 0
            elif min(dezenas) == 0:  # Dezena vazia
                label = 1
            elif abs(max(dezenas) - min(dezenas)) <= 1:  # Distribuição uniforme
                label = 2
            else:  # Padrão misto
                label = 3
            
            labels.append(label)
        
        return labels
    
    def _inicializar_conhecimento_base(self, data):
        """📚 Inicializa base de conhecimento"""
        
        print("📚 Inicializando base de conhecimento...")
        
        # Padrões de frequência
        self.conhecimento_base['frequency_patterns'] = {
            'numeros_frequentes': [],
            'numeros_raros': [],
            'media_frequencia': 0.0,
            'desvio_frequencia': 0.0
        }
        
        # Padrões de distribuição
        self.conhecimento_base['distribution_patterns'] = {
            'distribuicao_dezenas': [0, 0, 0, 0, 0],
            'soma_media': data['soma_total'].mean(),
            'soma_desvio': data['soma_total'].std()
        }
        
        # Padrões temporais
        self.conhecimento_base['temporal_patterns'] = {
            'ciclos_detectados': [],
            'tendencias': {},
            'sazonalidade': {}
        }
        
        # Padrões de correlação
        feature_cols = ['soma_total', 'amplitude', 'paridade', 'numeros_consecutivos']
        correlations = data[feature_cols].corr()
        self.conhecimento_base['correlation_patterns'] = correlations.to_dict()
        
        print("✅ Base de conhecimento inicializada")
    
    def detectar_concept_drift(self, novos_dados):
        """🔄 Detecta mudanças conceituais nos dados"""
        
        if len(novos_dados) < 10:
            return False, 0.0
        
        # Compara distribuições com conhecimento base
        drift_scores = []
        
        # 1. Drift na soma total
        nova_soma_media = novos_dados['soma_total'].mean()
        base_soma_media = self.conhecimento_base['distribution_patterns']['soma_media']
        soma_drift = abs(nova_soma_media - base_soma_media) / base_soma_media
        drift_scores.append(soma_drift)
        
        # 2. Drift na paridade
        nova_paridade = novos_dados['paridade'].mean()
        base_paridade = 7.5  # Esperado para 15 números
        paridade_drift = abs(nova_paridade - base_paridade) / base_paridade
        drift_scores.append(paridade_drift)
        
        # 3. Drift na amplitude
        nova_amplitude = novos_dados['amplitude'].mean()
        amplitude_esperada = 20  # Amplitude típica
        amplitude_drift = abs(nova_amplitude - amplitude_esperada) / amplitude_esperada
        drift_scores.append(amplitude_drift)
        
        # Score de drift médio
        drift_score = np.mean(drift_scores)
        
        # Detecta drift se score > threshold
        drift_detectado = drift_score > self.config['threshold_mudanca']
        
        if drift_detectado:
            self.adaptation_metrics['concept_drift_detected'] += 1
            print(f"🔄 Concept drift detectado! Score: {drift_score:.3f}")
        
        return drift_detectado, drift_score
    
    def adaptar_modelos(self, novos_dados):
        """🎯 Adapta modelos aos novos padrões"""
        
        print(f"\n🎯 ADAPTANDO MODELOS ({len(novos_dados)} novos dados)")
        print("=" * 45)
        
        if len(novos_dados) < 10:
            print("❌ Dados insuficientes para adaptação")
            return False
        
        start_time = datetime.now()
        adaptacoes_sucesso = 0
        
        try:
            # Prepara features
            feature_cols = [col for col in novos_dados.columns 
                           if col not in ['concurso', 'timestamp_idx']]
            X_new = novos_dados[feature_cols].fillna(0)
            y_new = self._criar_labels_padrao(novos_dados)
            
            # Adapta cada modelo
            for nome, modelo_info in self.modelos_ativos.items():
                try:
                    modelo = modelo_info['modelo']
                    tipo = modelo_info['tipo']
                    
                    if tipo == 'classification':
                        # Retreina incrementalmente
                        modelo.fit(X_new, y_new)
                        
                        # Avalia performance
                        y_pred = modelo.predict(X_new)
                        accuracy = accuracy_score(y_new, y_pred)
                        modelo_info['performance']['accuracy'] = accuracy
                        
                        print(f"   ✅ {nome}: {accuracy:.1%} accuracy")
                        adaptacoes_sucesso += 1
                        
                    elif tipo == 'anomaly':
                        # Retreina detector de anomalias
                        modelo.fit(X_new)
                        anomaly_pred = modelo.predict(X_new)
                        accuracy = (anomaly_pred == 1).mean()
                        modelo_info['performance']['accuracy'] = accuracy
                        
                        print(f"   ✅ {nome}: {accuracy:.1%} normais")
                        adaptacoes_sucesso += 1
                        
                    elif tipo == 'clustering':
                        # Retreina clustering
                        modelo.fit(X_new)
                        inertia = modelo.inertia_
                        modelo_info['performance']['inertia'] = inertia
                        
                        print(f"   ✅ {nome}: {inertia:.0f} inertia")
                        adaptacoes_sucesso += 1
                    
                    modelo_info['performance']['last_update'] = datetime.now()
                    
                except Exception as e:
                    print(f"   ❌ Erro em {nome}: {e}")
            
            # Atualiza conhecimento base
            self._atualizar_conhecimento_base(novos_dados)
            
            # Atualiza métricas
            self.adaptation_metrics['successful_adaptations'] += adaptacoes_sucesso
            self.adaptation_metrics['learning_cycles'] += 1
            
            adaptation_time = (datetime.now() - start_time).total_seconds()
            self.adaptation_metrics['adaptation_speed'] = adaptation_time
            
            print(f"\n   📊 {adaptacoes_sucesso}/{len(self.modelos_ativos)} modelos adaptados")
            print(f"   ⏱️ Tempo de adaptação: {adaptation_time:.2f}s")
            
            return adaptacoes_sucesso > 0
            
        except Exception as e:
            print(f"❌ Erro na adaptação: {e}")
            return False
    
    def _atualizar_conhecimento_base(self, novos_dados):
        """📚 Atualiza base de conhecimento com novos padrões"""
        
        # Taxa de esquecimento para conhecimento antigo
        taxa_esquecimento = self.config['taxa_esquecimento']
        taxa_aprendizado = 1 - taxa_esquecimento
        
        # Atualiza padrões de distribuição
        nova_soma_media = novos_dados['soma_total'].mean()
        soma_atual = self.conhecimento_base['distribution_patterns']['soma_media']
        self.conhecimento_base['distribution_patterns']['soma_media'] = (
            soma_atual * taxa_aprendizado + nova_soma_media * taxa_esquecimento
        )
        
        novo_desvio = novos_dados['soma_total'].std()
        desvio_atual = self.conhecimento_base['distribution_patterns']['soma_desvio']
        self.conhecimento_base['distribution_patterns']['soma_desvio'] = (
            desvio_atual * taxa_aprendizado + novo_desvio * taxa_esquecimento
        )
        
        # Atualiza correlações
        feature_cols = ['soma_total', 'amplitude', 'paridade', 'numeros_consecutivos']
        if all(col in novos_dados.columns for col in feature_cols):
            novas_correlacoes = novos_dados[feature_cols].corr()
            
            # Mistura correlações antigas com novas
            for i, col1 in enumerate(feature_cols):
                for j, col2 in enumerate(feature_cols):
                    if col1 in self.conhecimento_base['correlation_patterns']:
                        if col2 in self.conhecimento_base['correlation_patterns'][col1]:
                            valor_antigo = self.conhecimento_base['correlation_patterns'][col1][col2]
                            valor_novo = novas_correlacoes.iloc[i, j]
                            self.conhecimento_base['correlation_patterns'][col1][col2] = (
                                valor_antigo * taxa_aprendizado + valor_novo * taxa_esquecimento
                            )
    
    def executar_ciclo_aprendizado(self):
        """🔄 Executa um ciclo completo de aprendizado contínuo"""
        
        print(f"\n🔄 CICLO DE APRENDIZADO CONTÍNUO - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 55)
        
        if not hasattr(self, 'features_df') or len(self.features_df) == 0:
            print("❌ Sem dados para aprendizado")
            return False
        
        # Simula chegada de novos dados (últimos N registros)
        batch_size = self.config['batch_size']
        novos_dados = self.features_df.tail(batch_size).copy()
        
        # Adiciona à memória adaptativa
        for _, row in novos_dados.iterrows():
            self.memoria_adaptativa.append(row.to_dict())
        
        # Detecta concept drift
        drift_detectado, drift_score = self.detectar_concept_drift(novos_dados)
        
        # Atualiza drift score dos modelos
        for modelo_info in self.modelos_ativos.values():
            modelo_info['drift_score'] = drift_score
        
        # Se drift detectado ou ciclo regular de avaliação
        if drift_detectado or len(self.memoria_adaptativa) % self.config['intervalo_avaliacao'] == 0:
            sucesso = self.adaptar_modelos(novos_dados)
            
            if sucesso:
                print("✅ Adaptação concluída com sucesso")
            else:
                print("⚠️ Adaptação parcialmente bem-sucedida")
        else:
            print("📊 Sem necessidade de adaptação neste ciclo")
        
        # Atualiza métricas de retenção de conhecimento
        self._atualizar_retencao_conhecimento()
        
        return True
    
    def _atualizar_retencao_conhecimento(self):
        """📊 Atualiza métricas de retenção de conhecimento"""
        
        # Calcula retenção baseada na consistência dos padrões
        consistencia_scores = []
        
        # Verifica consistência da soma média
        if 'distribution_patterns' in self.conhecimento_base:
            soma_base = self.conhecimento_base['distribution_patterns']['soma_media']
            # Compara com expectativa teórica (195 para 15 números de 1-25)
            expectativa = 195
            consistencia = 1 - abs(soma_base - expectativa) / expectativa
            consistencia_scores.append(max(0, consistencia))
        
        # Verifica consistência das correlações
        if 'correlation_patterns' in self.conhecimento_base:
            correlacoes = self.conhecimento_base['correlation_patterns']
            valores_correlacao = []
            for col1 in correlacoes:
                for col2 in correlacoes[col1]:
                    if col1 != col2:
                        valores_correlacao.append(abs(correlacoes[col1][col2]))
            
            if valores_correlacao:
                media_correlacao = np.mean(valores_correlacao)
                # Penaliza correlações muito altas (overfitting) ou muito baixas
                consistencia = 1 - abs(media_correlacao - 0.3)  # Esperamos ~30% correlação
                consistencia_scores.append(max(0, consistencia))
        
        # Calcula retenção média
        if consistencia_scores:
            self.adaptation_metrics['knowledge_retention'] = np.mean(consistencia_scores)
        else:
            self.adaptation_metrics['knowledge_retention'] = 0.5
    
    def gerar_predicoes_adaptativas(self, n_predicoes=5):
        """🎯 Gera predições usando conhecimento adaptativo"""
        
        print(f"\n🎯 GERANDO PREDIÇÕES ADAPTATIVAS")
        print("=" * 35)
        
        if not self.modelos_ativos or not hasattr(self, 'features_df'):
            print("❌ Modelos não inicializados")
            return []
        
        predicoes = []
        
        try:
            # Usa dados mais recentes como base
            dados_base = self.features_df.tail(10).mean()
            feature_cols = [col for col in self.features_df.columns 
                           if col not in ['concurso', 'timestamp_idx']]
            
            for i in range(n_predicoes):
                predicao = {}
                
                # Adiciona variação baseada no conhecimento adaptativo
                soma_base = self.conhecimento_base['distribution_patterns']['soma_media']
                desvio_base = self.conhecimento_base['distribution_patterns']['soma_desvio']
                
                # Gera soma com variação adaptativa
                soma_prevista = np.random.normal(soma_base, desvio_base * 0.5)
                soma_prevista = max(120, min(270, soma_prevista))  # Limita valores
                
                # Usa modelo de clustering para determinar padrão
                if 'pattern_cluster' in self.modelos_ativos:
                    cluster_model = self.modelos_ativos['pattern_cluster']['modelo']
                    features_predicao = dados_base[feature_cols].values.reshape(1, -1)
                    cluster = cluster_model.predict(features_predicao)[0]
                    
                    predicao['cluster_padrao'] = cluster
                    predicao['soma_prevista'] = soma_prevista
                    
                    # Ajusta distribuição baseada no cluster
                    if cluster == 0:  # Concentração
                        dezenas = [4, 4, 3, 2, 2]
                    elif cluster == 1:  # Dispersão
                        dezenas = [2, 3, 3, 3, 4]
                    else:  # Balanceado
                        dezenas = [3, 3, 3, 3, 3]
                    
                    predicao['distribuicao_dezenas'] = dezenas
                
                # Usa detector de anomalias para ajustar confiança
                if 'anomaly_detector' in self.modelos_ativos:
                    anom_model = self.modelos_ativos['anomaly_detector']['modelo']
                    anomalia = anom_model.predict(features_predicao)[0]
                    predicao['confianca'] = 0.8 if anomalia == 1 else 0.4
                else:
                    predicao['confianca'] = 0.7
                
                # Adiciona timestamp e ID
                predicao['id'] = f"PRED_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}"
                predicao['timestamp'] = datetime.now()
                predicao['metodo'] = 'aprendizado_continuo'
                
                predicoes.append(predicao)
            
            print(f"✅ {len(predicoes)} predições geradas")
            
            # Exibe resumo das predições
            for pred in predicoes[:3]:
                print(f"   • Predição {pred['id'][-1]}: Soma={pred['soma_prevista']:.0f}, "
                      f"Confiança={pred['confianca']:.1%}")
            
            return predicoes
            
        except Exception as e:
            print(f"❌ Erro na geração de predições: {e}")
            return []
    
    def exibir_status_aprendizado(self):
        """📊 Exibe status completo do sistema de aprendizado"""
        
        print(f"\n📊 STATUS DO SISTEMA DE APRENDIZADO")
        print("=" * 40)
        print(f"🕐 Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Status dos modelos
        print(f"\n🤖 MODELOS ATIVOS ({len(self.modelos_ativos)}):")
        for nome, info in self.modelos_ativos.items():
            # Obtém performance baseada no tipo do modelo
            if 'accuracy' in info['performance']:
                performance = info['performance']['accuracy']
                status = "🟢" if performance > 0.5 else "🟡"
                print(f"   {status} {nome}")
                print(f"      Performance: {performance:.1%}")
            elif 'inertia' in info['performance']:
                inertia = info['performance']['inertia']
                status = "🟢"
                print(f"   {status} {nome}")
                print(f"      Inertia: {inertia:.0f}")
            else:
                status = "🟡"
                print(f"   {status} {nome}")
                print(f"      Performance: N/A")
            
            print(f"      Drift Score: {info['drift_score']:.3f}")
            print(f"      Última atualização: {info['performance']['last_update'].strftime('%H:%M:%S')}")
        
        # Métricas de adaptação
        print(f"\n📈 MÉTRICAS DE ADAPTAÇÃO:")
        metrics = self.adaptation_metrics
        print(f"   • Concept drifts detectados: {metrics['concept_drift_detected']}")
        print(f"   • Adaptações bem-sucedidas: {metrics['successful_adaptations']}")
        print(f"   • Ciclos de aprendizado: {metrics['learning_cycles']}")
        print(f"   • Retenção de conhecimento: {metrics['knowledge_retention']:.1%}")
        print(f"   • Velocidade de adaptação: {metrics['adaptation_speed']:.2f}s")
        
        # Status da memória
        print(f"\n🧠 MEMÓRIA ADAPTATIVA:")
        print(f"   • Registros na memória: {len(self.memoria_adaptativa)}")
        print(f"   • Capacidade máxima: {self.config['memoria_maxima']}")
        print(f"   • Taxa de utilização: {len(self.memoria_adaptativa)/self.config['memoria_maxima']:.1%}")
        
        # Conhecimento base
        print(f"\n📚 BASE DE CONHECIMENTO:")
        if self.conhecimento_base:
            for tipo in self.knowledge_types:
                status = "✅" if tipo in self.conhecimento_base else "❌"
                print(f"   {status} {tipo}")
        
        # Configuração atual
        print(f"\n⚙️ CONFIGURAÇÃO:")
        config = self.config
        print(f"   • Batch size: {config['batch_size']}")
        print(f"   • Threshold mudança: {config['threshold_mudanca']:.1%}")
        print(f"   • Intervalo avaliação: {config['intervalo_avaliacao']}")
        print(f"   • Taxa esquecimento: {config['taxa_esquecimento']:.1%}")
    
    def modo_demonstracao_completo(self):
        """🎭 Demonstração completa do sistema de aprendizado"""
        
        print("🧠 DEMONSTRAÇÃO - SISTEMA DE APRENDIZADO CONTÍNUO")
        print("=" * 52)
        
        # Fase 1: Inicialização
        print("\n📋 FASE 1: INICIALIZAÇÃO")
        if not self.conectar_banco() or not self.carregar_dados_historicos():
            print("❌ Falha na inicialização")
            return
        
        # Fase 2: Treinamento inicial
        print("\n📋 FASE 2: TREINAMENTO INICIAL")
        if not self.inicializar_modelos_base():
            print("❌ Falha no treinamento inicial")
            return
        
        # Fase 3: Simulação de ciclos de aprendizado
        print("\n📋 FASE 3: SIMULAÇÃO DE CICLOS")
        for ciclo in range(3):
            print(f"\n   🔄 Ciclo {ciclo + 1}/3")
            self.executar_ciclo_aprendizado()
            time.sleep(1)  # Pausa para visualização
        
        # Fase 4: Geração de predições
        print("\n📋 FASE 4: GERAÇÃO DE PREDIÇÕES")
        predicoes = self.gerar_predicoes_adaptativas(3)
        
        # Fase 5: Status final
        print("\n📋 FASE 5: STATUS FINAL")
        self.exibir_status_aprendizado()
        
        print(f"\n✅ DEMONSTRAÇÃO CONCLUÍDA!")
        print(f"   📊 {len(predicoes)} predições geradas")
        print(f"   🧠 Sistema adaptativo operacional")

def main():
    """Função principal"""
    sistema = SistemaAprendizadoContinuo()
    
    print("🧠 SISTEMA DE APRENDIZADO CONTÍNUO AUTOMATIZADO")
    print("Inspirado em 'Automated Continual Learning'")
    print("=" * 50)
    print("1. 🎭 Demonstração completa")
    print("2. 🔄 Executar ciclo único")
    print("3. 🎯 Gerar predições")
    print("4. 📊 Exibir status")
    print("0. 🚪 Sair")
    
    try:
        opcao = input("\n👉 Escolha uma opção: ").strip()
        
        if opcao == "1":
            sistema.modo_demonstracao_completo()
        elif opcao == "2":
            if sistema.conectar_banco() and sistema.carregar_dados_historicos():
                if sistema.inicializar_modelos_base():
                    sistema.executar_ciclo_aprendizado()
        elif opcao == "3":
            if sistema.conectar_banco() and sistema.carregar_dados_historicos():
                if sistema.inicializar_modelos_base():
                    predicoes = sistema.gerar_predicoes_adaptativas(5)
                    print(f"📊 {len(predicoes)} predições geradas")
        elif opcao == "4":
            sistema.exibir_status_aprendizado()
        elif opcao == "0":
            print("👋 Saindo...")
        else:
            print("❌ Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n👋 Programa interrompido")

if __name__ == "__main__":
    main()