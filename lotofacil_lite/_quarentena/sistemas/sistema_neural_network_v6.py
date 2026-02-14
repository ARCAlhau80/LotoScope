import random
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
from datetime import d        # ENSEMBLE DE MODELOS (Multi-output para classificação de múltiplas labels)
        self.modelo_ensemble = {
            'random_forest': MultiOutputClassifier(
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    min_samples_leaf=2,
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
        }a
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

class SistemaNeuralNetworkV6:
    def __init__(self):
        self.meta_acertos = 11  # 74% = 11/15 acertos
        self.resultado_teste = [3,5,6,8,9,12,13,14,15,16,17,20,21,22,23]
        
        # Dados carregados
        self.dados_historicos = None
        self.dados_ciclos = None
        
        # Modelos de IA
        self.modelo_neural_basico = None
        self.modelo_deep_learning = None
        self.modelo_ensemble = None
        self.scaler = StandardScaler()
        
        # Features processadas
        self.features_matrix = None
        self.targets_matrix = None
        
        print("🧠 SISTEMA NEURAL NETWORK V6.0 - LOTOFÁCIL")
        print("=" * 50)
        print("🎯 META: 11/15 acertos (74%+)")
        print("📊 Base: 100% REAL (Resultados_INT + NumerosCiclos)")
        print("🤖 IA: Rede Neural + Deep Learning + Ensemble")
        print()
        
    def carregar_dados_reais(self):
        """Carrega dados 100% reais do banco SQL Server"""
        print("📊 CARREGANDO DADOS 100% REAIS...")
        
        try:
            # Usa a conexão SQL Server ao invés de SQLite
            from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

            
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
                SELECT TOP 25 Numero, QtdSorteados, ConcursoInicio, 
                       ConcursoFechamento, Ciclo
                FROM NumerosCiclos
                ORDER BY Numero
                """
                
                resultado_ciclos = db_config.execute_query(query_ciclos)
                if resultado_ciclos:
                    colunas_ciclos = ['numero', 'qtd_sorteados', 'concurso_inicio', 
                                    'concurso_fechamento', 'ciclo']
                    self.dados_ciclos = pd.DataFrame(resultado_ciclos, columns=colunas_ciclos)
                    print(f"✅ Análise de ciclos: {len(self.dados_ciclos)} números")
                else:
                    print("⚠️ Tabela NumerosCiclos não encontrada, usando análise básica")
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
            
            # 6. CORRELAÇÕES (co-aparições frequentes)
            correlacoes = []
            for num1 in range(int(int(1)), int(int(26)):
                for num2 in range(int(num1+1)), int(int(26))):
                    if len(correlacoes) < 50:  # Limita a 50 correlações principais
                        coocorrencia = 0
                        for j in range(int(int(i-janela)), int(int(i)):
                            if num1 in numeros_matrix[j] and num2 in numeros_matrix[j]:
                                coocorrencia += 1
                        correlacoes.append(coocorrencia / janela)
            features_concurso.extend(correlacoes[:50])
            
            # 7. FEATURES ESTATÍSTICAS REAIS DA TABELA
            if i < len(self.dados_historicos):
                row = self.dados_historicos.iloc[i]
                features_estatisticas = [
                    row['SomaTotal'] / 300), int(# Normalizado (soma típica ~200))
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
            
            # 8. FEATURES DOS CICLOS (se disponível)
            if self.dados_ciclos is not None:
                features_ciclos = []
                for num in range(int(int(1)), int(int(26)):
                    ciclo_info = self.dados_ciclos[self.dados_ciclos['numero'] == num]
                    if len(ciclo_info) > 0:
                        features_ciclos.extend([
                            ciclo_info.iloc[0]['qtd_sorteados'] / 100), int(# Normalizado
                            ciclo_info.iloc[0]['concurso_inicio'] / 3000,   # Normalizado
                            ciclo_info.iloc[0]['ciclo'] / 10                # Normalizado
                        ]))
                    else:
                        features_ciclos.extend([0.5, 0.5, 0.5])  # Valores neutros
                features_concurso.extend(features_ciclos)
            
            features_list.append(features_concurso)
        
        self.features_matrix = np.array(features_list)
        self.targets_matrix = np.array(targets_list)
        
        print(f"✅ Features processadas: {self.features_matrix.shape}")
        print(f"✅ Targets processados: {self.targets_matrix.shape}")
        print(f"📊 Dimensões por amostra: {len(features_list[0])} features")
        
        return True
    
    def criar_modelo_neural_basico(self):
        """Cria modelo neural network básico"""
        print("🧠 CRIANDO MODELO NEURAL BÁSICO...")
        
        # Modelo para classificação multi-label (cada número é uma classe binária)
        self.modelo_neural_basico = MLPClassifier(
            hidden_layer_sizes=(256, 128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            batch_size=32,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        
        print("✅ Modelo Neural Básico criado")
    
    def criar_modelo_deep_learning(self):
        """Cria modelo Deep Learning com TensorFlow"""
        print("🤖 CRIANDO MODELO DEEP LEARNING...")
        
        input_dim = self.features_matrix.shape[1]
        
        # Arquitetura Deep Learning especializada
        self.modelo_deep_learning = keras.Sequential([
            # Camada de entrada
            layers.Dense(512, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Camadas ocultas profundas
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(), 
            layers.Dropout(0.2),
            
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
        """Cria ensemble de modelos"""
        print("🎭 CRIANDO ENSEMBLE DE MODELOS...")
        
        # Combinação de algoritmos diferentes (Multi-output para classificação multi-label)
        self.modelo_ensemble = {
            'random_forest': MultiOutputClassifier(
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    min_samples_leaf=2,
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
        
        print("✅ Ensemble criado (Random Forest + Gradient Boosting)")
    
    def treinar_modelos(self):
        """Treina todos os modelos"""
        print("🏋️ TREINANDO MODELOS COM DADOS 100% REAIS...")
        
        # Divide dados em treino e validação
        X_train, X_val, y_train, y_val = train_test_split(
            self.features_matrix, 
            self.targets_matrix,
            test_size=0.2,
            random_state=42,
            shuffle=True
        )
        
        # Normaliza features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        print(f"📊 Treino: {X_train.shape[0]} amostras")
        print(f"📊 Validação: {X_val.shape[0]} amostras")
        
        # 1. TREINA MODELO NEURAL BÁSICO
        print("🧠 Treinando Neural Básico...")
        self.modelo_neural_basico.fit(X_train_scaled, y_train)
        
        # Avaliação Neural Básico
        pred_neural = self.modelo_neural_basico.predict(X_val_scaled)
        acc_neural = accuracy_score(y_val, pred_neural)
        print(f"   ✅ Acurácia Neural Básico: {acc_neural:.3f}")
        
        # 2. TREINA DEEP LEARNING
        print("🤖 Treinando Deep Learning...")
        
        # Callbacks para otimização
        callbacks = [
            keras.callbacks.EarlyStopping(patience=20, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=10),
        ]
        
        history = self.modelo_deep_learning.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=200,
            batch_size=32,
            callbacks=callbacks,
            verbose=0
        )
        
        # Avaliação Deep Learning
        loss, acc_deep, prec_deep, rec_deep = self.modelo_deep_learning.evaluate(X_val_scaled, y_val, verbose=0)
        print(f"   ✅ Deep Learning - Loss: {loss:.3f}, Acc: {acc_deep:.3f}, Prec: {prec_deep:.3f}")
        
        # 3. TREINA ENSEMBLE
        print("🎭 Treinando Ensemble...")
        
        for nome, modelo in self.modelo_ensemble.items():
            print(f"   🔧 Treinando {nome}...")
            modelo.fit(X_train_scaled, y_train)
            pred = modelo.predict(X_val_scaled)
            acc = accuracy_score(y_val, pred)
            print(f"   ✅ {nome}: {acc:.3f}")
        
        print("🏆 TODOS OS MODELOS TREINADOS!")
        
        # Salva histórico do Deep Learning
        return {
            'neural_basico': acc_neural,
            'deep_learning': acc_deep,
            'historia_deep': history.history
        }
    
    def prever_proximos_numeros_ia(self):
        """Usa todos os modelos para prever próximos números"""
        print("🔮 PREVENDO PRÓXIMOS NÚMEROS COM IA...")
        
        # Features da janela mais recente
        ultimos_concursos = self.features_matrix[-1:] # Última amostra
        ultimos_concursos_scaled = self.scaler.transform(ultimos_concursos)
        
        # PREDIÇÕES DOS MODELOS
        predicoes = {}
        
        # 1. Neural Básico
        pred_neural = self.modelo_neural_basico.predict_proba(ultimos_concursos_scaled)[0]
        predicoes['neural_basico'] = pred_neural
        
        # 2. Deep Learning  
        pred_deep = self.modelo_deep_learning.predict(ultimos_concursos_scaled)[0]
        predicoes['deep_learning'] = pred_deep
        
        # 3. Ensemble
        pred_ensemble = []
        for nome, modelo in self.modelo_ensemble.items():
            pred = modelo.predict_proba(ultimos_concursos_scaled)[0]
            # Pega probabilidade da classe positiva (coluna 1)
            if len(pred.shape) > 1:
                pred = pred[:, 1]  # Probabilidade de aparecer
            pred_ensemble.append(pred)
        
        pred_ensemble_media = np.mean(pred_ensemble, axis=0)
        predicoes['ensemble'] = pred_ensemble_media
        
        # COMBINAÇÃO INTELIGENTE
        # Pesos baseados na performance esperada
        pesos = {
            'neural_basico': 0.2,
            'deep_learning': 0.5,  # Maior peso para Deep Learning
            'ensemble': 0.3
        }
        
        # Predição final ponderada
        predicao_final = np.zeros(25)
        for modelo, pred in predicoes.items():
            # Garante que pred tem shape correto
            if len(pred.shape) > 1:
                pred = pred[:, 1] if pred.shape[1] > 1 else pred.flatten()
            
            predicao_final += pesos[modelo] * pred
        
        # Converte probabilidades em rankings
        numeros_com_prob = [(i+1, prob) for i, prob in enumerate(predicao_final)]
        numeros_com_prob.sort(key=lambda x: x[1], reverse=True)
        
        print("🎯 RANKINGS DE PROBABILIDADE:")
        for i, (num, prob) in enumerate(numeros_com_prob[:20]):
            print(f"   {i+1:2d}. Número {num:2d}: {prob:.4f}")
        
        return numeros_com_prob, predicoes
    
    def gerar_combinacao_ia_ultra_precisa(self, rankings):
        """Gera combinação ultra-precisa usando IA"""
        print("🚀 GERANDO COMBINAÇÃO IA ULTRA-PRECISA...")
        
        # ESTRATÉGIA MULTI-CAMADA
        
        # Camada 1: Top números por probabilidade (70% da seleção)
        top_probabilidades = [num for num, prob in rankings[:18]]
        selecao_top = np.random.choice(top_probabilidades, size=10, replace=False)
        
        # Camada 2: Números com boa probabilidade (20% da seleção)  
        meio_probabilidades = [num for num, prob in rankings[18:35]]
        if meio_probabilidades:
            selecao_meio = np.random.choice(meio_probabilidades, 
                                          size=min(3, len(meio_probabilidades)), 
                                          replace=False)
        else:
            selecao_meio = []
        
        # Camada 3: Surpresas controladas (10% da seleção)
        baixa_probabilidades = [num for num, prob in rankings[35:]]
        if baixa_probabilidades:
            selecao_baixa = np.random.choice(baixa_probabilidades, 
                                           size=min(2, len(baixa_probabilidades)), 
                                           replace=False)
        else:
            selecao_baixa = []
        
        # Combina seleções
        combinacao_inicial = list(selecao_top) + list(selecao_meio) + list(selecao_baixa)
        combinacao_inicial = list(set(combinacao_inicial))  # Remove duplicatas
        
        # Ajusta para exatamente 15 números
        if len(combinacao_inicial) < 15:
            faltam = 15 - len(combinacao_inicial)
            candidatos = [num for num in range(int(int(1)), int(int(26)) if num not in combinacao_inicial]
            extras = np.random.choice(candidatos), int(size=min(faltam, len(candidatos))), replace=False)
            combinacao_inicial.extend(extras)
        elif len(combinacao_inicial) > 15:
            combinacao_inicial = sorted(combinacao_inicial, 
                                      key=lambda x: dict(rankings)[x], 
                                      reverse=True)[:15]
        
        combinacao_final = sorted(combinacao_inicial)
        
        print(f"🎯 Combinação IA: {combinacao_final}")
        
        return combinacao_final
    
    def validar_contra_resultado_real(self, combinacao):
        """Valida contra resultado real"""
        numeros_comb = set(combinacao)
        numeros_teste = set(self.resultado_teste)
        
        acertos = len(numeros_comb & numeros_teste)
        taxa = (acertos / 15) * 100
        
        status = "✅ SUCESSO META 74%" if acertos >= self.meta_acertos else "❌ FALHA"
        
        return {
            'acertos': acertos,
            'taxa': taxa,
            'status': status,
            'meta_atingida': acertos >= self.meta_acertos,
            'numeros_acertados': sorted(list(numeros_comb & numeros_teste)),
            'numeros_errados': sorted(list(numeros_comb - numeros_teste))
        }
    
    def salvar_resultado_neural(self, combinacao, validacao, rankings, metricas):
        """Salva resultado do sistema neural"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"NEURAL_NETWORK_V6_{timestamp}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("🧠 SISTEMA NEURAL NETWORK V6.0 - LOTOFÁCIL\n")
            f.write("=" * 50 + "\n")
            f.write("✅ Base: 100% REAL (Resultados_INT + NumerosCiclos)\n")
            f.write("✅ IA: Neural + Deep Learning + Ensemble\n")
            f.write(f"✅ META: {self.meta_acertos}/15 acertos (74%+)\n")
            f.write(f"\nGerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            f.write("COMBINAÇÃO IA ULTRA-PRECISA:\n")
            f.write(f"{','.join([str(n) for n in combinacao])}\n\n")
            
            f.write("VALIDAÇÃO CONTRA RESULTADO REAL:\n")
            f.write(f"Resultado teste: {','.join([str(n) for n in self.resultado_teste])}\n")
            f.write(f"Acertos: {validacao['acertos']}/15 ({validacao['taxa']:.1f}%)\n")
            f.write(f"Status: {validacao['status']}\n")
            f.write(f"Meta 74% atingida: {'SIM' if validacao['meta_atingida'] else 'NÃO'}\n\n")
            
            f.write(f"Números acertados: {','.join([str(n) for n in validacao['numeros_acertados']])}\n")
            f.write(f"Números errados: {','.join([str(n) for n in validacao['numeros_errados']])}\n\n")
            
            f.write("PERFORMANCE DOS MODELOS IA:\n")
            f.write(f"Neural Básico: {metricas.get('neural_basico', 0):.3f}\n")
            f.write(f"Deep Learning: {metricas.get('deep_learning', 0):.3f}\n\n")
            
            f.write("TOP 15 PROBABILIDADES IA:\n")
            for i, (num, prob) in enumerate(rankings[:15]):
                f.write(f"{i+1:2d}. Número {num:2d}: {prob:.4f}\n")
        
        print(f"💾 Resultado salvo: {nome_arquivo}")
    
    def executar_sistema_completo(self):
        """Executa sistema neural network completo"""
        print("🚀 INICIANDO SISTEMA NEURAL NETWORK V6.0 COMPLETO")
        print("=" * 60)
        
        # 1. Carrega dados reais
        if not self.carregar_dados_reais():
            print("❌ FALHA: Não foi possível carregar dados reais")
            return False
        
        # 2. Processa features
        if not self.processar_features_avancadas():
            print("❌ FALHA: Não foi possível processar features")
            return False
        
        # 3. Cria modelos
        self.criar_modelo_neural_basico()
        self.criar_modelo_deep_learning()
        self.criar_modelo_ensemble()
        
        # 4. Treina modelos
        metricas = self.treinar_modelos()
        
        # 5. Faz predições
        rankings, predicoes = self.prever_proximos_numeros_ia()
        
        # 6. Gera combinação
        combinacao = self.gerar_combinacao_ia_ultra_precisa(rankings)
        
        # 7. Valida resultado
        validacao = self.validar_contra_resultado_real(combinacao)
        
        # 8. Mostra resultados
        print("\n🎯 RESULTADO FINAL NEURAL NETWORK V6.0:")
        print("=" * 45)
        print(f"🤖 Combinação IA: {','.join([str(n) for n in combinacao])}")
        print(f"📊 Acertos: {validacao['acertos']}/15 ({validacao['taxa']:.1f}%)")
        print(f"🎯 Status: {validacao['status']}")
        
        if validacao['meta_atingida']:
            print("🏆 PARABÉNS! META 74% ATINGIDA!")
        else:
            print(f"💔 Meta não atingida. Faltaram {self.meta_acertos - validacao['acertos']} acertos")
        
        print(f"✅ Acertados: {','.join([str(n) for n in validacao['numeros_acertados']])}")
        print(f"❌ Errados: {','.join([str(n) for n in validacao['numeros_errados']])}")
        
        # 9. Salva resultado
        self.salvar_resultado_neural(combinacao, validacao, rankings, metricas)
        
        return validacao['meta_atingida']

def main():
    sistema = SistemaNeuralNetworkV6()
    sucesso = sistema.executar_sistema_completo()
    
    if sucesso:
        print(f"\n🏆 MISSÃO CUMPRIDA! Sistema Neural atingiu 74%+!")
    else:
        print(f"\n🔬 Sistema Neural executado. Resultado registrado para análise.")

if __name__ == "__main__":
    main()
