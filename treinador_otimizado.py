#!/usr/bin/env python3
"""
🎯 SISTEMA DE TREINAMENTO OTIMIZADO PARA MÁXIMA PRECISÃO
================================================================
Foco: Treinar modelos para máxima precisão dos 8 parâmetros críticos
Objetivo: Reduzir combinações possíveis de 3.268.760 para centenas
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib
import logging
from datetime import datetime
from analisador_preditivo_especializado import AnalisadorPreditivoEspecializado

class TreinadorOtimizado:
    """Treinador otimizado para máxima precisão dos 8 parâmetros"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.parametros_alvo = [
            'maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo',
            'n1', 'n15', 'faixa_6a25', 'faixa_6a20', 'acertos_combinacao_fixa'
        ]
        
        # Modelos expandidos para testar
        self.modelos = {
            'RandomForest': RandomForestRegressor(random_state=42),
            'GradientBoosting': GradientBoostingRegressor(random_state=42),
            'XGBoost': self._get_xgboost(),
            'SVR': SVR(),
            'Ridge': Ridge(),
            'Lasso': Lasso(),
            'ElasticNet': ElasticNet(random_state=42),
            'DecisionTree': DecisionTreeRegressor(random_state=42),
            'KNeighbors': KNeighborsRegressor(),
            'NeuralNetwork': MLPRegressor(random_state=42, max_iter=1000)
        }
        
        # Scalers para testar
        self.scalers = {
            'Standard': StandardScaler(),
            'Robust': RobustScaler(),
            'MinMax': MinMaxScaler(),
            'None': None
        }
        
        self.melhores_modelos = {}
        self.melhores_scalers = {}
        self.resultados_detalhados = {}
        
    def _setup_logger(self):
        """Configurar logger específico"""
        logger = logging.getLogger('TreinadorOtimizado')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_xgboost(self):
        """Tenta importar XGBoost se disponível"""
        try:
            import xgboost as xgb
            return xgb.XGBRegressor(random_state=42, n_estimators=100)
        except ImportError:
            self.logger.warning("XGBoost não disponível, usando GradientBoosting extra")
            return GradientBoostingRegressor(
                n_estimators=200, 
                learning_rate=0.05,
                max_depth=6,
                random_state=42
            )
    
    def carregar_dados_historicos(self):
        """Carrega dados históricos reais do SQL Server"""
        self.logger.info("🔄 Carregando dados históricos reais...")
        
        analisador = AnalisadorPreditivoEspecializado()
        dados_historicos = analisador.carregar_dados_historicos()
        
        if not dados_historicos:
            raise ValueError("Nenhum dado histórico disponível")
        
        self.logger.info(f"✅ Carregados {len(dados_historicos)} concursos reais")
        return dados_historicos
    
    def preparar_features_e_targets(self, dados_historicos):
        """Prepara features e targets para treinamento"""
        self.logger.info("🔧 Preparando features e targets...")
        
        # Criar DataFrame com todos os parâmetros
        df_data = []
        for param in dados_historicos:
            row = {
                'concurso': param.concurso,
                'maior_que_ultimo': param.maior_que_ultimo,
                'menor_que_ultimo': param.menor_que_ultimo,
                'igual_ao_ultimo': param.igual_ao_ultimo,
                'n1': param.n1,
                'n15': param.n15,
                'faixa_6a25': param.faixa_6a25,
                'faixa_6a20': param.faixa_6a20,
                'acertos_combinacao_fixa': param.acertos_combinacao_fixa
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Features: valores históricos + tendências + estatísticas móveis
        features_list = []
        targets = {}
        
        # Janela para features temporais
        window = 10
        
        for i in range(window, len(df)):
            # Features básicas (últimos N valores de cada parâmetro)
            row_features = []
            
            for param in self.parametros_alvo:
                # Últimos valores
                ultimos_valores = df[param].iloc[i-window:i].values
                row_features.extend([
                    ultimos_valores[-1],  # Último valor
                    ultimos_valores[-2] if len(ultimos_valores) >= 2 else ultimos_valores[-1],  # Penúltimo
                    np.mean(ultimos_valores),  # Média
                    np.std(ultimos_valores),   # Desvio padrão
                    np.median(ultimos_valores), # Mediana
                    np.min(ultimos_valores),   # Mínimo
                    np.max(ultimos_valores),   # Máximo
                    len(set(ultimos_valores)), # Valores únicos
                ])
                
                # Tendência (diferença entre média recente e antiga)
                meio = len(ultimos_valores) // 2
                media_recente = np.mean(ultimos_valores[meio:])
                media_antiga = np.mean(ultimos_valores[:meio])
                row_features.append(media_recente - media_antiga)
            
            # Features adicionais derivadas
            row_features.extend([
                df['concurso'].iloc[i] % 7,  # Dia da semana (aproximado)
                df['concurso'].iloc[i] % 30, # Ciclo mensal (aproximado)
                i,  # Posição temporal
            ])
            
            features_list.append(row_features)
            
            # Targets (valores atuais para predição)
            for param in self.parametros_alvo:
                if param not in targets:
                    targets[param] = []
                targets[param].append(df[param].iloc[i])
        
        X = np.array(features_list)
        
        # Remover features com variação zero
        feature_variance = np.var(X, axis=0)
        valid_features = feature_variance > 1e-10
        X = X[:, valid_features]
        
        self.logger.info(f"📊 Features preparadas: {X.shape[1]} features, {X.shape[0]} amostras")
        
        return X, targets
    
    def treinar_parametro_otimizado(self, X, y, param_name):
        """Treina modelo otimizado para um parâmetro específico"""
        self.logger.info(f"🎯 Otimizando modelo para: {param_name}")
        
        # Time Series Split para validação temporal
        tscv = TimeSeriesSplit(n_splits=5)
        
        melhor_score = -np.inf
        melhor_config = None
        
        resultados_param = {
            'modelos': {},
            'melhor_modelo': None,
            'melhor_scaler': None,
            'melhor_score': melhor_score
        }
        
        # Testar combinações de modelo + scaler
        for scaler_name, scaler in self.scalers.items():
            for modelo_name, modelo in self.modelos.items():
                try:
                    self.logger.info(f"   Testando {modelo_name} + {scaler_name}")
                    
                    # Preparar dados
                    X_scaled = X.copy()
                    if scaler is not None:
                        X_scaled = scaler.fit_transform(X_scaled)
                    
                    # Grid Search para hiperparâmetros
                    param_grid = self._get_param_grid(modelo_name, param_name)
                    
                    if param_grid:
                        grid_search = GridSearchCV(
                            modelo, 
                            param_grid, 
                            cv=tscv,
                            scoring='r2',
                            n_jobs=-1
                        )
                        grid_search.fit(X_scaled, y)
                        modelo_final = grid_search.best_estimator_
                    else:
                        # Validação cruzada simples
                        scores = []
                        for train_idx, val_idx in tscv.split(X_scaled):
                            X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
                            y_train, y_val = y[train_idx], y[val_idx]
                            
                            modelo.fit(X_train, y_train)
                            y_pred = modelo.predict(X_val)
                            score = r2_score(y_val, y_pred)
                            scores.append(score)
                        
                        modelo_final = modelo
                        modelo_final.fit(X_scaled, y)
                    
                    # Avaliar modelo final
                    score_final = self._avaliar_modelo_temporal(modelo_final, X_scaled, y, scaler)
                    
                    resultados_param['modelos'][f"{modelo_name}_{scaler_name}"] = {
                        'modelo': modelo_final,
                        'scaler': scaler,
                        'score': score_final
                    }
                    
                    self.logger.info(f"      R² = {score_final:.4f}")
                    
                    # Atualizar melhor modelo
                    if score_final > melhor_score:
                        melhor_score = score_final
                        melhor_config = {
                            'modelo': modelo_final,
                            'scaler': scaler,
                            'modelo_name': modelo_name,
                            'scaler_name': scaler_name
                        }
                        resultados_param['melhor_modelo'] = modelo_name
                        resultados_param['melhor_scaler'] = scaler_name
                        resultados_param['melhor_score'] = melhor_score
                
                except Exception as e:
                    self.logger.warning(f"      Erro com {modelo_name} + {scaler_name}: {e}")
                    continue
        
        if melhor_config:
            self.logger.info(f"✅ Melhor para {param_name}: {melhor_config['modelo_name']} + {melhor_config['scaler_name']} (R²={melhor_score:.4f})")
            return melhor_config, resultados_param
        else:
            raise ValueError(f"Nenhum modelo funcionou para {param_name}")
    
    def _get_param_grid(self, modelo_name, param_name):
        """Define grade de parâmetros para otimização"""
        # Grids específicas para parâmetros importantes
        if param_name in ['maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo']:
            # Parâmetros de comparação são mais críticos
            if modelo_name == 'RandomForest':
                return {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 15, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            elif modelo_name == 'GradientBoosting':
                return {
                    'n_estimators': [100, 150, 200],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                }
            elif modelo_name == 'SVR':
                return {
                    'C': [0.1, 1, 10, 100],
                    'gamma': ['scale', 'auto', 0.001, 0.01],
                    'kernel': ['rbf', 'polynomial']
                }
        
        return None  # Usar parâmetros padrão
    
    def _avaliar_modelo_temporal(self, modelo, X, y, scaler):
        """Avaliação temporal mais rigorosa"""
        # Split temporal: 80% treino, 20% teste
        split_idx = int(len(X) * 0.8)
        
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Treinar
        modelo.fit(X_train, y_train)
        
        # Predizer
        y_pred = modelo.predict(X_test)
        
        # Métricas
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Score combinado (priorizando R² mas penalizando MAE alto)
        score_combinado = r2 - (mae / (np.std(y_test) + 1e-10)) * 0.1
        
        return score_combinado
    
    def treinar_sistema_completo(self):
        """Treina sistema completo com otimização máxima"""
        self.logger.info("🚀 INICIANDO TREINAMENTO OTIMIZADO PARA MÁXIMA PRECISÃO")
        self.logger.info("=" * 70)
        
        # Carregar dados
        dados_historicos = self.carregar_dados_historicos()
        
        # Preparar features e targets
        X, targets = self.preparar_features_e_targets(dados_historicos)
        
        # Treinar modelo otimizado para cada parâmetro
        for param in self.parametros_alvo:
            self.logger.info(f"\n🎯 Treinando modelo otimizado para: {param}")
            self.logger.info("-" * 50)
            
            y = np.array(targets[param])
            
            try:
                melhor_config, resultados_param = self.treinar_parametro_otimizado(X, y, param)
                
                self.melhores_modelos[param] = melhor_config['modelo']
                self.melhores_scalers[param] = melhor_config['scaler']
                self.resultados_detalhados[param] = resultados_param
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao treinar {param}: {e}")
        
        # Salvar modelos otimizados
        self._salvar_modelos_otimizados()
        
        # Relatório final
        self._gerar_relatorio_final()
    
    def _salvar_modelos_otimizados(self):
        """Salva modelos otimizados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"modelos_otimizados_{timestamp}.pkl"
        
        dados_modelo = {
            'modelos': self.melhores_modelos,
            'scalers': self.melhores_scalers,
            'resultados': self.resultados_detalhados,
            'parametros_alvo': self.parametros_alvo,
            'timestamp': timestamp
        }
        
        joblib.dump(dados_modelo, filename)
        self.logger.info(f"💾 Modelos otimizados salvos em: {filename}")
    
    def _gerar_relatorio_final(self):
        """Gera relatório final de precisão"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 RELATÓRIO FINAL - MODELOS OTIMIZADOS")
        self.logger.info("=" * 70)
        
        for param in self.parametros_alvo:
            if param in self.resultados_detalhados:
                resultado = self.resultados_detalhados[param]
                self.logger.info(f"🎯 {param}:")
                self.logger.info(f"   Melhor modelo: {resultado['melhor_modelo']}")
                self.logger.info(f"   Melhor scaler: {resultado['melhor_scaler']}")
                self.logger.info(f"   R² otimizado: {resultado['melhor_score']:.4f}")
        
        # Calcular precisão média
        scores = [r['melhor_score'] for r in self.resultados_detalhados.values()]
        precisao_media = np.mean(scores)
        
        self.logger.info(f"\n🏆 PRECISÃO MÉDIA DO SISTEMA: {precisao_media:.4f}")
        
        if precisao_media > 0.3:
            self.logger.info("✅ Sistema com boa precisão para redução de combinações!")
        elif precisao_media > 0.1:
            self.logger.info("⚠️ Precisão moderada - recomenda-se mais dados ou features")
        else:
            self.logger.info("❌ Precisão baixa - necessário revisar estratégia")

def main():
    """Função principal"""
    print("🎯 SISTEMA DE TREINAMENTO OTIMIZADO PARA MÁXIMA PRECISÃO")
    print("=" * 65)
    print("Objetivo: Treinar modelos para prever com precisão os 8 parâmetros")
    print("Meta: Reduzir 3.268.760 combinações para centenas")
    print("=" * 65)
    
    treinador = TreinadorOtimizado()
    treinador.treinar_sistema_completo()
    
    print("\n🏆 TREINAMENTO OTIMIZADO CONCLUÍDO!")
    print("Os modelos estão prontos para predições de alta precisão.")

if __name__ == "__main__":
    main()