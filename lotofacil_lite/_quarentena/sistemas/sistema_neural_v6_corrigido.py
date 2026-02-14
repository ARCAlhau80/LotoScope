import random
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA NEURAL NETWORK V6.0 - LOTOFÁCIL
==========================================
✅ Dados 100% REAIS (Resultados_INT + NumerosCiclos)
✅ Rede Neural Deep Learning
✅ Meta: 74%+ (11/15 acertos)
✅ Análise de padrões ultra-complexos
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import accuracy_score, classification_report
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import warnings
warnings.filterwarnings('ignore')

class SistemaNeuralNetworkV6:
    def __init__(self):
        self.meta_acertos = 11  # 74% = 11/15 acertos
        self.resultado_teste = [3,5,6,8,9,12,13,14,15,16,17,20,21,22,23]
        
        # Dados carregados
        self.dados_historicos = None
        self.dados_ciclos = None
        
        # Features processadas
        self.features_matrix = None
        self.targets_matrix = None
        self.scaler = None
        
        # Modelos
        self.modelo_neural_basico = None
        self.modelo_deep_learning = None
        self.modelo_ensemble = None
        
        print("🧠 SISTEMA NEURAL NETWORK V6.0 - LOTOFÁCIL")
        print("=" * 60)
        print("🎯 META: 11/15 acertos (74%+)")
        print("📊 Base: 100% REAL (Resultados_INT + NumerosCiclos)")
        print("🤖 IA: Rede Neural + Deep Learning + Ensemble")
        print("")
        print("🚀 INICIANDO SISTEMA NEURAL NETWORK V6.0 COMPLETO")
        print("=" * 60)
        
    def carregar_dados_reais(self):
        """Carrega dados 100% reais do banco SQL Server"""
        print("📊 CARREGANDO DADOS 100% REAIS...")
        
        try:
            # Usa a conexão SQL Server ao invés de SQLite
            from database_config import DatabaseConfig
            
            db_config = DatabaseConfig()
            if not db_config.test_connection():
                print("❌ Erro: Não foi possível conectar ao banco SQL Server")
                return False
            
            # Carrega Resultados_INT (dados históricos completos)
            query_resultados = """
            SELECT TOP 500 Concurso, N1, N2, N3, N4, N5,
                   N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15,
                   Data_Sorteio, SomaTotal, QtdePrimos, QtdeFibonacci, 
                   QtdeImpares, Quintil1, Quintil2, Quintil3, Quintil4, Quintil5
            FROM Resultados_INT 
            ORDER BY Concurso DESC
            """
            
            resultado_query = db_config.execute_query(query_resultados)
            if resultado_query:
                colunas = ['Concurso', 'N1', 'N2', 'N3', 'N4', 'N5',
                          'N6', 'N7', 'N8', 'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15',
                          'Data_Sorteio', 'SomaTotal', 'QtdePrimos', 'QtdeFibonacci', 
                          'QtdeImpares', 'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5']
                self.dados_historicos = pd.DataFrame(resultado_query, columns=colunas)
            else:
                print("❌ Nenhum dado encontrado na tabela Resultados_INT")
                return False
            
            # Carrega NumerosCiclos (análise de ciclos) - se existir
            try:
                query_ciclos = """
                SELECT TOP 25 Ciclo, Numero, QtdSorteados, 
                       ConcursoInicio, ConcursoFechamento
                FROM NumerosCiclos
                ORDER BY Numero
                """
                
                resultado_ciclos = db_config.execute_query(query_ciclos)
                if resultado_ciclos:
                    colunas_ciclos = ['Ciclo', 'Numero', 'QtdSorteados', 
                                    'ConcursoInicio', 'ConcursoFechamento']
                    self.dados_ciclos = pd.DataFrame(resultado_ciclos, columns=colunas_ciclos)
                    print(f"✅ Análise de ciclos: {len(self.dados_ciclos)} números")
                else:
                    print("⚠️ Tabela NumerosCiclos vazia, usando análise básica")
                    self.dados_ciclos = None
            except:
                print("⚠️ NumerosCiclos não disponível, usando análise básica")
                self.dados_ciclos = None
            
            print(f"✅ Resultados históricos: {len(self.dados_historicos)} concursos")
            print(f"📅 Período: Concurso {self.dados_historicos['Concurso'].max()} até {self.dados_historicos['Concurso'].min()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def processar_features_avancadas(self):
        """Processa features avançadas para IA"""
        print("🔬 PROCESSANDO FEATURES AVANÇADAS PARA IA...")
        
        if self.dados_historicos is None:
            return False
        
        # Converte dados históricos para matriz de números
        colunas_numeros = [f'N{i}' for i in range(int(int(1)), int(int(16))]
        numeros_matrix = self.dados_historicos[colunas_numeros].values
        
        # FEATURE ENGINEERING AVANÇADO
        features_list = []
        targets_list = []
        
        # Janela deslizante para análise temporal
        janela = 10  # Analisa últimos 10 concursos
        
        for i in range(int(janela)), int(int(len(numeros_matrix)))):
            # Features do concurso atual (target)
            target_atual = np.zeros(25)  # One-hot encoding para números 1-25
            for num in numeros_matrix[i]:
                if 1 <= num <= 25:
                    target_atual[num-1] = 1
            
            targets_list.append(target_atual)
            
            # Features baseadas na janela anterior
            features_concurso = []
            
            # 1. FREQUÊNCIA NA JANELA
            freq_janela = np.zeros(25)
            for j in range(int(int(i-janela)), int(int(i)):
                for num in numeros_matrix[j]:
                    if 1 <= num <= 25:
                        freq_janela[num-1] += 1
            freq_janela = freq_janela / janela  # Normaliza
            features_concurso.extend(freq_janela)
            
            # 2. ÚLTIMAS APARIÇÕES
            ultima_aparicao = np.full(25), int(janela))  # Default: não apareceu na janela
            for k in range(int(int(int(janela)):
                for num in numeros_matrix[i-1-k]:  # Vai do mais recente ao mais antigo
                    if 1 <= num <= 25 and ultima_aparicao[num-1] == janela:
                        ultima_aparicao[num-1] = k
            features_concurso.extend(ultima_aparicao)
            
            # 3. PADRÕES DE SEQUÊNCIA (números consecutivos)
            sequencias = np.zeros(24)  # Pares consecutivos (1-2)), int(int(2-3), int(..., 24-25)))
            for j in range(int(int(i-janela)), int(int(i)):
                nums_ordenados = sorted(numeros_matrix[j])
                for k in range(int(int(len(nums_ordenados))-1):
                    if nums_ordenados[k+1] == nums_ordenados[k] + 1:
                        if 1 <= nums_ordenados[k] <= 24:
                            sequencias[nums_ordenados[k]-1] += 1
            sequencias = sequencias / janela
            features_concurso.extend(sequencias)
            
            # 4. PADRÕES DE PARIDADE
            paridade_janela = np.zeros(2)  # [pares)), int(int(ímpares]
            for j in range(i-janela, i))):
                for num in numeros_matrix[j]:
                    if 1 <= num <= 25:
                        paridade_janela[num % 2] += 1
            paridade_janela = paridade_janela / (janela * 15)  # Normaliza por total de números
            features_concurso.extend(paridade_janela)
            
            # 5. DISTRIBUIÇÃO POR FAIXAS
            faixas = np.zeros(5)  # [1-5, 6-10, 11-15, 16-20, 21-25]
            for j in range(int(int(i-janela)), int(int(i)):
                for num in numeros_matrix[j]:
                    if 1 <= num <= 25:
                        faixa_idx = min(4), int((num-1)) // 5)
                        faixas[faixa_idx] += 1
            faixas = faixas / (janela * 15)
            features_concurso.extend(faixas)
            
            # 6. FEATURES ESTATÍSTICAS REAIS DA TABELA
            if i < len(self.dados_historicos):
                row = self.dados_historicos.iloc[i]
                features_estatisticas = [
                    row['SomaTotal'] / 300,          # Normalizado (soma típica ~200)
                    row['QtdePrimos'] / 15,          # Normalizado (máx 15 números)
                    row['QtdeFibonacci'] / 15,       # Normalizado
                    row['QtdeImpares'] / 15,         # Normalizado
                    row['Quintil1'] / 15,            # Normalizado
                    row['Quintil2'] / 15,
                    row['Quintil3'] / 15,
                    row['Quintil4'] / 15,
                    row['Quintil5'] / 15,
                ]
                features_concurso.extend(features_estatisticas)
            
            features_list.append(features_concurso)
        
        self.features_matrix = np.array(features_list)
        self.targets_matrix = np.array(targets_list)
        
        print(f"✅ Features processadas: {self.features_matrix.shape}")
        print(f"✅ Targets processados: {self.targets_matrix.shape}")
        print(f"📊 Dimensões por amostra: {len(features_list[0])} features")
        
        return True
    
    def criar_modelo_deep_learning(self):
        """Cria modelo Deep Learning com TensorFlow/Keras"""
        print("🤖 CRIANDO MODELO DEEP LEARNING...")
        
        input_dim = self.features_matrix.shape[1]
        
        # Arquitetura otimizada para Lotofácil
        self.modelo_deep_learning = keras.Sequential([
            # Camada de entrada
            layers.Dense(512, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Camadas ocultas
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.1),
            
            layers.Dense(32, activation='relu'),
            
            # Camada de saída (25 neurônios para números 1-25)
            layers.Dense(25, activation='sigmoid')  # Sigmoid para probabilidades [0,1]
        ])
        
        # Compilação otimizada para este problema
        self.modelo_deep_learning.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        print("✅ Modelo Deep Learning criado")
        print(f"📊 Arquitetura: {input_dim} → 512 → 256 → 128 → 64 → 32 → 25")
    
    def criar_modelo_ensemble(self):
        """Cria ensemble simplificado"""
        print("🎭 CRIANDO ENSEMBLE DE MODELOS...")
        
        # Só Random Forest para este teste
        self.modelo_ensemble = {
            'random_forest': MultiOutputClassifier(
                RandomForestClassifier(
                    n_estimators=100,  # Reduzido para teste
                    max_depth=15,
                    random_state=42,
                    n_jobs=-1
                )
            )
        }
        
        print("✅ Ensemble criado (Random Forest)")
    
    def treinar_modelos(self):
        """Treina todos os modelos"""
        print("🏋️ TREINANDO MODELOS COM DADOS 100% REAIS...")
        
        # Divisão treino/validação
        X_train, X_val, y_train, y_val = train_test_split(
            self.features_matrix, self.targets_matrix,
            test_size=0.2, random_state=42
        )
        
        print(f"📊 Treino: {len(X_train)} amostras")
        print(f"📊 Validação: {len(X_val)} amostras")
        
        # Normalização
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # 1. TREINA DEEP LEARNING
        print("🤖 Treinando Deep Learning...")
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(patience=20, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(patience=10, factor=0.5)
        ]
        
        history = self.modelo_deep_learning.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=50,  # Reduzido para teste
            batch_size=32,
            callbacks=callbacks,
            verbose=0
        )
        
        # Avaliação Deep Learning
        loss, acc_deep, prec_deep, rec_deep = self.modelo_deep_learning.evaluate(X_val_scaled, y_val, verbose=0)
        print(f"   ✅ Deep Learning - Loss: {loss:.3f}, Acc: {acc_deep:.3f}, Prec: {prec_deep:.3f}")
        
        # 2. TREINA ENSEMBLE
        print("🎭 Treinando Ensemble...")
        
        for nome, modelo in self.modelo_ensemble.items():
            print(f"   🔧 Treinando {nome}...")
            modelo.fit(X_train_scaled, y_train)
            pred = modelo.predict(X_val_scaled)
            # Acurácia para multi-output é mais complexa, vamos simplificar
            print(f"   ✅ {nome}: Treinado")
        
        print("🏆 TODOS OS MODELOS TREINADOS!")
        
        return {
            'deep_learning': acc_deep,
            'historia_deep': history.history
        }
    
    def gerar_predicoes(self):
        """Gera 6 predições diferentes incluindo estratégia híbrida inteligente"""
        print("🔮 GERANDO 6 PREDIÇÕES INTELIGENTES...")
        
        if self.features_matrix is None:
            return []
        
        predicoes_multiplas = []
        
        # PREDIÇÃO 1: Baseada no último concurso
        ultima_feature = self.features_matrix[-1:] 
        ultima_feature_scaled = self.scaler.transform(ultima_feature)
        pred_deep1 = self.modelo_deep_learning.predict(ultima_feature_scaled, verbose=0)
        numeros_pred1 = np.argsort(pred_deep1[0])[-15:] + 1
        predicoes_multiplas.append(sorted(numeros_pred1.tolist()))
        
        # PREDIÇÃO 2: Baseada na média dos últimos 3 concursos
        if len(self.features_matrix) >= 3:
            media_feature = np.mean(self.features_matrix[-3:], axis=0).reshape(1, -1)
            media_feature_scaled = self.scaler.transform(media_feature)
            pred_deep2 = self.modelo_deep_learning.predict(media_feature_scaled, verbose=0)
            numeros_pred2 = np.argsort(pred_deep2[0])[-15:] + 1
            predicoes_multiplas.append(sorted(numeros_pred2.tolist()))
        
        # PREDIÇÃO 3: Top 18 → 15
        pred_deep3 = self.modelo_deep_learning.predict(ultima_feature_scaled, verbose=0)
        top_18 = np.argsort(pred_deep3[0])[-18:] + 1
        np.random.seed(42))
        numeros_pred3 = sorted(np.random.choice(top_18, 15, replace=False).tolist())
        predicoes_multiplas.append(numeros_pred3)
        
        # PREDIÇÃO 4: Média dos últimos 5 concursos
        if len(self.features_matrix) >= 5:
            media5_feature = np.mean(self.features_matrix[-5:], axis=0).reshape(1, -1)
            media5_feature_scaled = self.scaler.transform(media5_feature)
            pred_deep4 = self.modelo_deep_learning.predict(media5_feature_scaled, verbose=0)
            numeros_pred4 = np.argsort(pred_deep4[0])[-15:] + 1
            predicoes_multiplas.append(sorted(numeros_pred4.tolist()))
        
        # PREDIÇÃO 5: Top 20 → 15 híbrida
        pred_deep5 = self.modelo_deep_learning.predict(ultima_feature_scaled, verbose=0)
        top_20 = np.argsort(pred_deep5[0])[-20:] + 1
        np.random.seed(123))
        numeros_pred5 = sorted(np.random.choice(top_20, 15, replace=False).tolist())
        predicoes_multiplas.append(numeros_pred5)
        
        # PREDIÇÃO 6: HÍBRIDA INTELIGENTE 100% DINÂMICA (CORRIGIDA)
        pred_deep6 = self.modelo_deep_learning.predict(ultima_feature_scaled, verbose=0)
        
        # Pega os TOP 15 números únicos da IA
        probabilidades = pred_deep6[0]
        indices_ordenados = np.argsort(probabilidades)[-15:]  # Top 15 índices
        top_15_ia = (indices_ordenados + 1).tolist()  # Converte para números 1-25
        
        # Garante que são únicos e ordenados
        numeros_pred6 = sorted(list(set(top_15_ia)))
        
        # Se por algum motivo temos menos de 15, completa com os próximos melhores
        if len(numeros_pred6) < 15:
            todos_indices = np.argsort(probabilidades)  # Todos ordenados
            for idx in reversed(todos_indices):
                numero = idx + 1
                if numero not in numeros_pred6:
                    numeros_pred6.append(numero)
                if len(numeros_pred6) >= 15:
                    break
            numeros_pred6 = sorted(numeros_pred6[:15])
        
        # Se temos dados de ciclos, ajusta os 5 números com menor probabilidade
        if self.dados_ciclos is not None and len(numeros_pred6) == 15:
            # Pega os 5 números com menor probabilidade da nossa lista
            probs_nossa_lista = [(num, probabilidades[num-1]) for num in numeros_pred6]
            probs_nossa_lista.sort(key=lambda x: x[1])  # Ordena por probabilidade
            
            # Números dos ciclos mais promissores
            ciclos_promissores = self.dados_ciclos.sort_values('ConcursoInicio', ascending=False)
            top_ciclos = ciclos_promissores['Numero'].head(10).tolist()
            
            # Substitui os 3 piores por números promissores dos ciclos
            numeros_finais = [x[0] for x in probs_nossa_lista[3:]]  # Mantém os 12 melhores
            
            # Adiciona 3 dos ciclos que não estão na lista
            for num_ciclo in top_ciclos:
                if num_ciclo not in numeros_finais and len(numeros_finais) < 15:
                    numeros_finais.append(num_ciclo)
            
            numeros_pred6 = sorted(numeros_finais[:15])
        
        predicoes_multiplas.append(numeros_pred6)
        
        # Exibe as predições
        for i, pred in enumerate(predicoes_multiplas, 1):
            nome_estrategia = [
                "Último", "Média 3", "Top18→15", "Média 5", "Top20→15", "Híbrida Inteligente"
            ][i-1]
            print(f"🤖 Predição {i} ({nome_estrategia}): {pred}")
        
        return predicoes_multiplas
    
    def validar_predicoes(self, predicoes_multiplas):
        """Valida as 5 predições contra resultado real"""
        if not predicoes_multiplas:
            return False
        
        print(f"🎯 VALIDAÇÃO DAS {len(predicoes_multiplas)} PREDIÇÕES CONTRA RESULTADO REAL:")
        print(f"   ✅ Resultado Real: {self.resultado_teste}")
        print("   " + "="*50)
        
        melhor_resultado = False
        melhor_acertos = 0
        
        for i, predicao in enumerate(predicoes_multiplas, 1):
            acertos = len(set(predicao) & set(self.resultado_teste))
            precisao = (acertos / 15) * 100
            
            print(f"   🎲 Predição {i}: {predicao}")
            print(f"   📊 Acertos {i}: {acertos}/15 ({precisao:.1f}%)")
            
            if acertos >= self.meta_acertos:
                print(f"   🏆 SUCESSO {i}! Meta atingida ({acertos}/15 ≥ {self.meta_acertos}/15)")
                melhor_resultado = True
            else:
                print(f"   ❌ Meta não atingida {i} ({acertos}/15 < {self.meta_acertos}/15)")
            
            if acertos > melhor_acertos:
                melhor_acertos = acertos
            
            print("   " + "-"*30)
        
        print(f"🏆 RESULTADO FINAL: Melhor = {melhor_acertos}/15 ({(melhor_acertos/15)*100:.1f}%)")
        
        return melhor_resultado
    
    def executar_sistema_completo(self):
        """Executa sistema completo"""
        # Carrega dados
        if not self.carregar_dados_reais():
            print("❌ FALHA: Não foi possível carregar dados reais")
            return False
        
        # Processa features
        if not self.processar_features_avancadas():
            print("❌ FALHA: Não foi possível processar features")
            return False
        
        # Cria modelos
        self.criar_modelo_deep_learning()
        self.criar_modelo_ensemble()
        
        # Treina modelos
        metricas = self.treinar_modelos()
        
        # Gera predições
        predicoes = self.gerar_predicoes()
        
        # Valida predições
        sucesso = self.validar_predicoes(predicoes)
        
        print("🔬 Sistema Neural executado. Resultado registrado para análise.")
        return sucesso

def main():
    """Função principal"""
    sistema = SistemaNeuralNetworkV6()
    sucesso = sistema.executar_sistema_completo()
    
    if sucesso:
        print("🎉 SISTEMA NEURAL NETWORK V6.0: SUCESSO!")
    else:
        print("📊 SISTEMA NEURAL NETWORK V6.0: Executado para análise")

if __name__ == "__main__":
    main()
