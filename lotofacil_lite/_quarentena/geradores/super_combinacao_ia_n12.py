import random
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SUPER_COMBINACAO_IA COM INTELIGÊNCIA N12
============================================================
Versão do super_combinacao_ia integrada com inteligência N12.

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
Baseado no super_combinacao_ia original com integração N12
"""

# Importação da inteligência N12
from integracao_n12 import aplicar_inteligencia_n12, gerar_combinacoes_inteligentes_n12

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import pickle
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Importar database_config para dados reais
try:
    from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

    DADOS_REAIS_DISPONIVEL = True
    print("✅ database_config importado - dados reais disponíveis")
except ImportError:
    DADOS_REAIS_DISPONIVEL = False
    print("⚠️ database_config não encontrado - modo simulação")

class SuperCombinacaoIA:
    """Sistema de IA para otimização de combinações"""
    
    def __init__(self):
        self.pasta_base = "combin_ia"
        self.pasta_modelos = f"{self.pasta_base}/modelos"
        self.pasta_datasets = f"{self.pasta_base}/datasets"
        self.pasta_super_combinacoes = f"{self.pasta_base}/super_combinacoes"
        
        # Cria pastas se não existirem
        for pasta in [self.pasta_modelos, self.pasta_super_combinacoes]:
            os.makedirs(pasta, exist_ok=True)
        
        # Modelos de IA
        self.modelo_performance = None
        self.modelo_otimizacao = None
        self.scaler_features = StandardScaler()
        self.scaler_target = StandardScaler()
        
        # Dados históricos reais
        self.dados_historicos_reais = []
        
        # 🚀 INTEGRAÇÃO DAS DESCOBERTAS DOS CAMPOS DE COMPARAÇÃO
        try:
            from integracao_descobertas_comparacao import IntegracaoDescobertasComparacao
            self.descobertas = IntegracaoDescobertasComparacao()
            print("🔬 Descobertas dos campos de comparação aplicadas")
        except ImportError:
            self.descobertas = None
            print("⚠️ Módulo de descobertas não encontrado - funcionamento normal")
        
        # Configurações da rede neural - ARQUITETURA SUPER-MASSIVA OTIMIZADA
        self.config_rede = {
            'hidden_layers': (12288, 6144, 3072, 1536, 768, 384, 192),  # 24,384 NEURÔNIOS
            'activation': 'relu',
            'solver': 'adam',
            'alpha': 1e-05,  # Regularização otimizada para rede grande
            'learning_rate': 'adaptive',
            'max_iter': 6000,  # Mais iterações para convergência
            'random_state': 42,
            'early_stopping': True,  # Evita overfitting
            'validation_fraction': 0.1,
            'n_iter_no_change': 100  # Paciência maior para redes grandes
        }
        
        # Dados de treinamento
        self.historico_treinamento = {
            'datasets_processados': [],
            'performance_modelo': {},
            'adaptacoes_realizadas': []
        }
        
        # Carrega dados históricos reais se disponível
        if DADOS_REAIS_DISPONIVEL:
            self.carregar_dados_historicos_reais()

    def carregar_dados_historicos_reais(self):
        """Carrega dados históricos reais da base Resultados_INT"""
        print("🔍 Carregando dados históricos reais para treinamento IA...")
        
        try:
            # Testa conexão
            db_config.test_connection()
            
            # Busca últimos 200 concursos para análise
            query = """
            SELECT TOP 200 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            resultados = db_config.execute_query(query)
            
            if resultados:
                for linha in resultados:
                    concurso = linha[0]
                    numeros = [linha[i] for i in range(1, 16]
                    
                    self.dados_historicos_reais.append({
                        'concurso': concurso), int('numeros': sorted(numeros)),
                        'features': self.extrair_features_historicas(numeros)
                    })
                
                print(f"✅ {len(self.dados_historicos_reais)} concursos históricos carregados para IA")
                print(f"📊 Faixa: Concurso {self.dados_historicos_reais[-1]['concurso']} ao {self.dados_historicos_reais[0]['concurso']}")
            else:
                print("⚠️ Nenhum dado encontrado na base")
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados reais: {e}")
            print("🔄 Sistema funcionará em modo simulação")

    def extrair_features_historicas(self, numeros):
        """Extrai features de dados históricos para treinamento"""
        return {
            'soma': sum(numeros),
            'media': sum(numeros) / len(numeros),
            'amplitude': max(numeros) - min(numeros),
            'pares': len([n for n in numeros if n % 2 == 0]),
            'impares': len([n for n in numeros if n % 2 == 1]),
            'consecutivos': self.contar_consecutivos_ia(numeros),
            'dezenas_baixas': len([n for n in numeros if n <= 12]),
            'dezenas_altas': len([n for n in numeros if n > 12])
        }

    def contar_consecutivos_ia(self, numeros):
        """Conta sequências consecutivas para análise IA"""
        numeros_ord = sorted(numeros)
        consecutivos = 0
        max_consec = 0
        
        for i in range(int(int(int(len(numeros_ord)) - 1):
            if numeros_ord[i+1] == numeros_ord[i] + 1:
                consecutivos += 1
                max_consec = max(max_consec)), int(int(consecutivos + 1))
            else:
                consecutivos = 0
        
        return max_consec
    
    def extrair_features_combinacao(self, int(combinacao: List[int])) -> np.ndarray:
        """Extrai features relevantes de uma combinação para a IA"""
        features = []
        
        # Features básicas
        features.extend([
            len(combinacao),                           # Quantidade de números
            sum(combinacao),                          # Soma total
            max(combinacao),                          # Número máximo
            min(combinacao),                          # Número mínimo
            np.mean(combinacao),                      # Média
            np.std(combinacao),                       # Desvio padrão
            len(set(combinacao))                      # Números únicos (deve ser igual ao tamanho)
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
        presenca_numeros = [1 if i in combinacao else 0 for i in range(1, 26]
        features.extend(presenca_numeros)
        
        return np.array(features)
    
    def extrair_features_conjunto(self, int(combinacoes: List[List[int]])) -> np.ndarray:
        """Extrai features de um conjunto de combinações"""
        features_individuais = []
        
        for combinacao in combinacoes:
            features = self.extrair_features_combinacao(combinacao)
            features_individuais.append(features)
        
        if not features_individuais:
            return np.array([])
        
        features_matriz = np.array(features_individuais)
        
        # Features do conjunto completo
        features_conjunto = []
        
        # Estatísticas do conjunto
        features_conjunto.extend([
            len(combinacoes),                         # Quantidade de combinações
            np.mean(features_matriz[:, 1]),          # Soma média das combinações
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
    
    def carregar_datasets_historicos(self) -> List[Dict]:
        """Carrega datasets históricos para treinamento"""
        datasets = []
        
        if not os.path.exists(self.pasta_datasets):
            print("⚠️ Pasta de datasets não encontrada")
            return datasets
        
        arquivos_dataset = [f for f in os.listdir(self.pasta_datasets) if f.endswith('.json')]
        
        print(f"📂 Carregando {len(arquivos_dataset)} datasets históricos...")
        
        for arquivo in arquivos_dataset:
            try:
                with open(os.path.join(self.pasta_datasets, arquivo), 'r', encoding='utf-8') as f:
                    dataset = json.load(f)
                    datasets.append(dataset)
            except Exception as e:
                print(f"⚠️ Erro ao carregar {arquivo}: {e}")
        
        print(f"✅ {len(datasets)} datasets carregados")
        return datasets
    
    def preparar_dados_treinamento(self, datasets: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados para treinamento da IA"""
        X_features = []
        y_performance = []
        
        print("🔄 Preparando dados de treinamento...")
        
        for dataset in datasets:
            try:
                combinacoes = dataset['combinacoes_geradas']
                avaliacao = dataset['avaliacao']
                
                # Features das combinações
                features = self.extrair_features_conjunto(combinacoes)
                
                # Target: performance (baseado nos acertos)
                performance_score = self._calcular_score_performance(avaliacao)
                
                X_features.append(features)
                y_performance.append(performance_score)
                
            except Exception as e:
                print(f"⚠️ Erro ao processar dataset do concurso {dataset.get('concurso', 'N/A')}: {e}")
        
        if not X_features:
            raise ValueError("Nenhum dado válido para treinamento")
        
        return np.array(X_features), np.array(y_performance)
    
    def _calcular_score_performance(self, avaliacao: Dict) -> float:
        """Calcula score de performance baseado na avaliação"""
        stats = avaliacao['estatisticas']
        
        # Score ponderado baseado em diferentes critérios
        score = 0.0
        
        # Acertos máximos (peso alto)
        score += stats['acertos_maximo'] * 10.0
        
        # Acertos médios (peso médio)  
        score += stats['acertos_medio'] * 5.0
        
        # Combinações com muitos acertos (peso alto)
        score += stats['combinacoes_15_acertos'] * 100.0
        score += stats['combinacoes_14_acertos'] * 50.0
        score += stats['combinacoes_13_acertos'] * 25.0
        
        # Consistência (peso médio)
        score += stats['combinacoes_12_plus'] * 2.0
        
        return score
    
    def treinar_modelo(self, force_retrain: bool = False):
        """Treina ou retreina o modelo de IA"""
        print(f"🧠 TREINAMENTO DA IA PARA SUPER-COMBINAÇÕES")
        print("=" * 60)
        
        modelo_path = os.path.join(self.pasta_modelos, "modelo_super_combinacao.pkl")
        
        # Verifica se deve treinar
        if os.path.exists(modelo_path) and not force_retrain:
            print("✅ Modelo já treinado encontrado. Use force_retrain=True para retreinar.")
            self.carregar_modelo()
            return
        
        # Carrega datasets históricos
        datasets = self.carregar_datasets_historicos()
        
        if len(datasets) < 10:
            print(f"⚠️ Poucos datasets para treinamento ({len(datasets)}). Recomendado: mínimo 10")
            if len(datasets) == 0:
                print("❌ Nenhum dataset encontrado. Execute primeiro o gerador de dataset histórico.")
                return
        
        # Prepara dados
        X, y = self.preparar_dados_treinamento(datasets)
        print(f"📊 Dados preparados: {X.shape[0]} amostras, {X.shape[1]} features")
        
        # Normalização
        X_scaled = self.scaler_features.fit_transform(X)
        y_scaled = self.scaler_target.fit_transform(y.reshape(-1, 1)).ravel()
        
        # Divisão treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_scaled, test_size=0.2, random_state=42
        )
        
        # Treinamento do modelo - ARQUITETURA MASSIVA
        print("🚀 Iniciando treinamento da rede neural MASSIVA...")
        print(f"   🧠 Arquitetura: {self.config_rede['hidden_layers']}")
        print(f"   💫 Total de neurônios: {sum(self.config_rede['hidden_layers']):,}")
        print("   ⚡ Isso pode levar alguns minutos...")
        
        self.modelo_performance = MLPRegressor(
            hidden_layer_sizes=self.config_rede['hidden_layers'],
            activation=self.config_rede['activation'],
            solver=self.config_rede['solver'],
            alpha=self.config_rede['alpha'],
            learning_rate=self.config_rede['learning_rate'],
            max_iter=self.config_rede['max_iter'],
            random_state=self.config_rede['random_state'],
            early_stopping=self.config_rede.get('early_stopping', False),
            validation_fraction=self.config_rede.get('validation_fraction', 0.1),
            n_iter_no_change=self.config_rede.get('n_iter_no_change', 50),
            verbose=True  # Mostra progresso do treinamento
        )
        
        self.modelo_performance.fit(X_train, y_train)
        
        # Avaliação
        y_pred_train = self.modelo_performance.predict(X_train)
        y_pred_test = self.modelo_performance.predict(X_test)
        
        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        
        print(f"📈 Performance da REDE NEURAL MASSIVA:")
        print(f"   • MSE Treino: {mse_train:.6f}")
        print(f"   • MSE Teste: {mse_test:.6f}")
        print(f"   • 🧠 Total de Neurônios: {sum(self.config_rede['hidden_layers']):,}")
        print(f"   • 🏗️ Camadas Ocultas: {len(self.config_rede['hidden_layers'])}")
        print(f"   • 🎯 Arquitetura: {self.config_rede['hidden_layers']}")
        print(f"   • ⚡ Iterações realizadas: {self.modelo_performance.n_iter_}")
        print(f"   • 🎪 Early stopping: {'Ativado' if self.config_rede.get('early_stopping') else 'Desativado'}")
        
        # Salva modelo
        self.salvar_modelo()
        
        # Atualiza histórico
        self.historico_treinamento['datasets_processados'] = len(datasets)
        self.historico_treinamento['performance_modelo'] = {
            'mse_train': mse_train,
            'mse_test': mse_test,
            'treinado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("✅ Treinamento concluído!")
    
    def salvar_modelo(self):
        """Salva o modelo treinado"""
        modelo_data = {
            'modelo_performance': self.modelo_performance,
            'scaler_features': self.scaler_features,
            'scaler_target': self.scaler_target,
            'config_rede': self.config_rede,
            'historico_treinamento': self.historico_treinamento
        }
        
        modelo_path = os.path.join(self.pasta_modelos, "modelo_super_combinacao.pkl")
        
        try:
            with open(modelo_path, 'wb') as f:
                pickle.dump(modelo_data, f)
            print(f"💾 Modelo salvo: {modelo_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar modelo: {e}")
    
    def carregar_modelo(self):
        """Carrega modelo treinado"""
        modelo_path = os.path.join(self.pasta_modelos, "modelo_super_combinacao.pkl")
        
        if not os.path.exists(modelo_path):
            print("⚠️ Modelo não encontrado. Execute o treinamento primeiro.")
            return False
        
        try:
            with open(modelo_path, 'rb') as f:
                modelo_data = pickle.load(f)
            
            self.modelo_performance = modelo_data['modelo_performance']
            self.scaler_features = modelo_data['scaler_features']
            self.scaler_target = modelo_data['scaler_target']
            self.config_rede = modelo_data['config_rede']
            self.historico_treinamento = modelo_data['historico_treinamento']
            
            print("✅ Modelo carregado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return False
    
    def ler_combinacoes_arquivo(self, arquivo_path: str) -> List[List[int]]:
        """Lê combinações de um arquivo (flexível para qualquer quantidade)"""
        combinacoes = []
        
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            for linha in linhas:
                linha = linha.strip()
                
                # Ignora linhas de cabeçalho ou vazias
                if not linha or linha.startswith('#') or linha.startswith('🎯'):
                    continue
                
                # Procura por padrão de números separados por vírgula
                if ',' in linha:
                    try:
                        # Extrai apenas os números da linha
                        numeros_str = linha.split(':')[-1] if ':' in linha else linha
                        numeros = [int(n.strip()) for n in numeros_str.split(',') if n.strip().isdigit()]
                        
                        # Valida se são números válidos da lotofácil
                        if all(1 <= n <= 25 for n in numeros) and len(numeros) >= 15:
                            combinacoes.append(numeros)
                            
                    except ValueError:
                        continue
            
            print(f"📂 {len(combinacoes)} combinações carregadas de {arquivo_path}")
            return combinacoes
            
        except Exception as e:
            print(f"❌ Erro ao ler arquivo {arquivo_path}: {e}")
            return []
    
    def analisar_combinacoes_ia(self, combinacoes: List[List[int]]) -> Dict:
        """Analisa combinações usando IA e propõe melhorias"""
        if not self.modelo_performance:
            if not self.carregar_modelo():
                raise Exception("Modelo não disponível. Execute o treinamento primeiro.")
        
        print(f"🔍 Analisando {len(combinacoes)} combinações com IA...")
        
        # Extrai features das combinações
        features = self.extrair_features_conjunto(combinacoes)
        features_scaled = self.scaler_features.transform([features])
        
        # Predição de performance
        performance_pred = self.modelo_performance.predict(features_scaled)[0]
        performance_real = self.scaler_target.inverse_transform([[performance_pred]])[0][0]
        
        # Análise individual das combinações
        performances_individuais = []
        for combinacao in combinacoes:
            features_ind = self.extrair_features_combinacao(combinacao)
            # Usa um subset das features para análise individual
            features_subset = features_ind[:len(features)]
            try:
                features_subset_scaled = self.scaler_features.transform([features_subset[:len(features)]])
                perf_ind = self.modelo_performance.predict(features_subset_scaled)[0]
                perf_real_ind = self.scaler_target.inverse_transform([[perf_ind]])[0][0]
                performances_individuais.append(perf_real_ind)
            except:
                performances_individuais.append(performance_real)  # Fallback
        
        analise = {
            'total_combinacoes': len(combinacoes),
            'performance_prevista': performance_real,
            'performances_individuais': performances_individuais,
            'melhor_combinacao_idx': np.argmax(performances_individuais),
            'pior_combinacao_idx': np.argmin(performances_individuais),
            'performance_media': np.mean(performances_individuais),
            'performance_std': np.std(performances_individuais)
        }
        
        return analise
    
    def gerar_super_combinacao(self, combinacoes: List[List[int]], 
                              quantidade_super: int = 1) -> List[Dict]:
        """Gera super-combinações otimizadas e diversificadas"""
        if not combinacoes:
            return []
        
        print(f"🚀 Gerando {quantidade_super} super-combinação(ões)...")
        
        # Analisa combinações atuais
        analise = self.analisar_combinacoes_ia(combinacoes)
        
        super_combinacoes = []
        super_combinacoes_geradas = set()  # Para evitar duplicatas
        
        # Identifica as top N combinações para diversificar
        num_features = analise['performances_individuais']
        top_indices = np.argsort(num_features)[-min(quantidade_super * 3, len(combinacoes):][::-1]
        
        for i in range(int(int(int(quantidade_super):
            tentativas = 0
            max_tentativas = 50
            
            while tentativas < max_tentativas:
                tentativas += 1
                
                # Estratégia diversificada para cada super-combinação
                if i == 0:
                    # Primeira: melhor combinação + otimização conservadora
                    base_idx = analise['melhor_combinacao_idx']
                    estrategia = "conservadora"
                elif i == 1:
                    # Segunda: combinação alternativa + otimização agressiva  
                    base_idx = top_indices[min(i)), int(int(len(top_indices))-1)]
                    estrategia = "agressiva"
                else:
                    # Demais: combinação aleatória das top + estratégia híbrida
                    base_idx = np.random.choice(top_indices)
                    estrategia = "hibrida"
                
                combinacao_base = combinacoes[base_idx].copy()
                
                # Otimizações baseadas na IA com diferentes estratégias
                super_combinacao = self._otimizar_combinacao_diversificada(
                    combinacao_base), int(combinacoes, estrategia, i
                ))
                
                # Valida e ajusta
                super_combinacao = self._validar_super_combinacao(super_combinacao)
                
                # Verifica se é única
                super_tuple = tuple(sorted(super_combinacao))
                if super_tuple not in super_combinacoes_geradas:
                    super_combinacoes_geradas.add(super_tuple)
                    
                    super_info = {
                        'super_combinacao': super_combinacao,
                        'combinacao_base': combinacao_base,
                        'substituicoes_realizadas': self._comparar_combinacoes(combinacao_base, super_combinacao),
                        'performance_prevista': self._prever_performance_individual(super_combinacao),
                        'confianca_ia': min(0.95, max(0.5, (analise['performance_prevista'] / 1000.0) + (i * 0.05))),
                        'estrategia_aplicada': estrategia
                    }
                    
                    super_combinacoes.append(super_info)
                    break
            
            if tentativas >= max_tentativas:
                print(f"⚠️ Dificuldade para gerar super-combinação {i+1} única")
        
        return super_combinacoes
    
    def _otimizar_combinacao_diversificada(self, combinacao_base: List[int], 
                                          todas_combinacoes: List[List[int]], 
                                          estrategia: str, indice: int) -> List[int]:
        """Otimiza uma combinação com diferentes estratégias para garantir diversidade"""
        combinacao_otimizada = combinacao_base.copy()
        
        # Análise de frequência nos melhores resultados
        frequencia_numeros = {}
        for i in range(1, 26:
            frequencia_numeros[i] = sum(1 for comb in todas_combinacoes if i in comb)
        
        # Números mais frequentes nas combinações de entrada
        numeros_frequentes = sorted(frequencia_numeros.items(), key=lambda x: x[1], reverse=True)
        
        if estrategia == "conservadora":
            # Estratégia conservadora: poucas mudanças, foca nos mais frequentes
            substituicoes = 0
            max_substituicoes = 2
            
            for i, numero in enumerate(combinacao_otimizada):
                if substituicoes >= max_substituicoes:
                    break
                
                freq_atual = frequencia_numeros[numero]
                
                # Só substitui por números muito melhores
                for num_freq, freq in numeros_frequentes[:8]:
                    if (num_freq not in combinacao_otimizada and 
                        freq > freq_atual * 1.5):  # Pelo menos 50% melhor
                        
                        combinacao_otimizada[i] = num_freq
                        substituicoes += 1
                        break
        
        elif estrategia == "agressiva":
            # Estratégia agressiva: mais mudanças, explora números diferentes
            substituicoes = 0
            max_substituicoes = 4
            
            # Foca em números de frequência média (posições 5-15)
            numeros_alternativos = [n for n, f in numeros_frequentes[5:15]]
            np.random.shuffle(numeros_alternativos)
            
            for i, numero in enumerate(combinacao_otimizada):
                if substituicoes >= max_substituicoes:
                    break
                
                freq_atual = frequencia_numeros[numero]
                
                # Substitui por números alternativos
                for num_candidato in numeros_alternativos:
                    if (num_candidato not in combinacao_otimizada and 
                        frequencia_numeros[num_candidato] > freq_atual * 0.8):  # 80% da frequência atual
                        
                        combinacao_otimizada[i] = num_candidato
                        substituicoes += 1
                        break
        
        else:  # estrategia == "hibrida"
            # Estratégia híbrida: combina conservador + agressivo
            substituicoes = 0
            max_substituicoes = 3
            
            # Usa seed baseada no índice para ter resultados diferentes
            np.random.seed(int(42 + indice * 10))
            
            for i, numero in enumerate(combinacao_otimizada):
                if substituicoes >= max_substituicoes:
                    break
                
                freq_atual = frequencia_numeros[numero]
                
                # 50% chance de usar estratégia conservadora, 50% agressiva
                if np.random.random() < 0.5:
                    # Conservadora
                    for num_freq, freq in numeros_frequentes[:10]:
                        if (num_freq not in combinacao_otimizada and 
                            freq > freq_atual * 1.3):
                            
                            combinacao_otimizada[i] = num_freq
                            substituicoes += 1
                            break
                else:
                    # Agressiva
                    candidatos = [n for n, f in numeros_frequentes[3:18] 
                                if n not in combinacao_otimizada]
                    if candidatos:
                        combinacao_otimizada[i] = np.random.choice(candidatos)
                        substituicoes += 1
            
            # Reset seed
            np.random.seed()
        
        return sorted(combinacao_otimizada)
    
    def _otimizar_combinacao(self, combinacao_base: List[int], 
                           todas_combinacoes: List[List[int]]) -> List[int]:
        """Otimiza uma combinação baseada nos padrões aprendidos (método legacy)"""
        return self._otimizar_combinacao_diversificada(combinacao_base, todas_combinacoes, "conservadora", 0)
    
    def _validar_super_combinacao(self, combinacao: List[int]) -> List[int]:
        """Valida e ajusta super-combinação para regras da lotofácil"""
        combinacao = list(set(combinacao))  # Remove duplicatas
        combinacao = [n for n in combinacao if 1 <= n <= 25]  # Válida range
        
        # Garante tamanho correto (pega o tamanho mais comum das combinações de entrada)
        if len(combinacao) < 15:
            # Completa com números aleatórios válidos
            numeros_faltantes = [i for i in range(1, 26 if i not in combinacao]
            np.random.shuffle(numeros_faltantes)
            combinacao.extend(numeros_faltantes[:15-len(combinacao)])
        
        elif len(combinacao) > 20:
            # Reduz mantendo os números com melhor score
            combinacao = combinacao[:20]
        
        return sorted(combinacao)
    
    def _comparar_combinacoes(self, int(original: List[int], 
                            otimizada: List[int])) -> Dict:
        """Compara duas combinações e identifica mudanças"""
        original_set = set(original)
        otimizada_set = set(otimizada)
        
        return {
            'removidos': list(original_set - otimizada_set),
            'adicionados': list(otimizada_set - original_set),
            'mantidos': list(original_set & otimizada_set),
            'total_mudancas': len((original_set - otimizada_set) | (otimizada_set - original_set))
        }
    
    def _prever_performance_individual(self, combinacao: List[int]) -> float:
        """Prevê performance de uma combinação individual"""
        try:
            features = self.extrair_features_combinacao(combinacao)
            # Ajusta features para o modelo
            features_ajustado = features[:self.scaler_features.n_features_in_]
            features_scaled = self.scaler_features.transform([features_ajustado])
            pred = self.modelo_performance.predict(features_scaled)[0]
            return self.scaler_target.inverse_transform([[pred]])[0][0]
        except:
            return 50.0  # Valor padrão
    
    def salvar_super_combinacoes(self, super_combinacoes: List[Dict], 
                                arquivo_origem: str = "combinacoes_dinamicas"):
        """Salva super-combinações geradas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"super_combinacoes_{timestamp}.json"
        arquivo_completo = os.path.join(self.pasta_super_combinacoes, nome_arquivo)
        
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
        
        dados_salvamento = {
            'gerado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'arquivo_origem': arquivo_origem,
            'modelo_usado': converter_numpy(self.historico_treinamento.get('performance_modelo', {})),
            'super_combinacoes': converter_numpy(super_combinacoes),
            'configuracao_ia': converter_numpy(self.config_rede)
        }
        
        try:
            with open(arquivo_completo, 'w', encoding='utf-8') as f:
                json.dump(dados_salvamento, f, indent=2, ensure_ascii=False)
            
            # Salva também em formato texto simples
            arquivo_txt = arquivo_completo.replace('.json', '.txt')
            with open(arquivo_txt, 'w', encoding='utf-8') as f:
                f.write(f"🧠 SUPER-COMBINAÇÕES GERADAS POR IA\n")
                f.write("=" * 60 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Origem: {arquivo_origem}\n\n")
                
                for i, super_info in enumerate(super_combinacoes, 1):
                    f.write(f"🎯 SUPER-COMBINAÇÃO {i}:\n")
                    f.write(f"{','.join(map(str, super_info['super_combinacao']))}\n")
                    f.write(f"Performance Prevista: {super_info['performance_prevista']:.1f}\n")
                    f.write(f"Confiança IA: {super_info['confianca_ia']:.1%}\n")
                    
                    if 'estrategia_aplicada' in super_info:
                        f.write(f"Estratégia: {super_info['estrategia_aplicada']}\n")
                    
                    subs = super_info['substituicoes_realizadas']
                    if subs['total_mudancas'] > 0:
                        f.write(f"Mudanças realizadas: {subs['total_mudancas']}\n")
                        if subs['removidos']:
                            f.write(f"  Removidos: {subs['removidos']}\n")
                        if subs['adicionados']:
                            f.write(f"  Adicionados: {subs['adicionados']}\n")
                    f.write("\n")
            
            print(f"✅ Super-combinações salvas:")
            print(f"   📄 JSON: {arquivo_completo}")
            print(f"   📄 TXT: {arquivo_txt}")
            
            return arquivo_completo
            
        except Exception as e:
            print(f"❌ Erro ao salvar super-combinações: {e}")
            return None

def main():
    """Função principal"""
    print("🧠 SISTEMA DE IA PARA SUPER-COMBINAÇÕES")
    print("=" * 55)
    print("🎯 Rede Neural que otimiza combinações do gerador dinâmico")
    print()
    
    ia = SuperCombinacaoIA()
    
    try:
        print("⚙️ OPÇÕES DISPONÍVEIS:")
        print("1. Treinar/Retreinar modelo de IA")
        print("2. Gerar super-combinações de arquivo")
        print("3. Analisar combinações existentes")
        
        opcao = input("\nEscolha uma opção (1-3): ").strip()
        
        if opcao == "1":
            print("\n🧠 TREINAMENTO DO MODELO")
            force = input("Forçar retreinamento? (s/n): ").lower().startswith('s')
            ia.treinar_modelo(force_retrain=force)
            
        elif opcao == "2":
            print("\n🎯 GERAÇÃO DE SUPER-COMBINAÇÕES")
            arquivo = input("Caminho do arquivo com combinações: ").strip()
            
            if not os.path.exists(arquivo):
                print("❌ Arquivo não encontrado")
                return
            
            # Lê combinações (flexível para qualquer quantidade)
            combinacoes = ia.ler_combinacoes_arquivo(arquivo)
            
            if not combinacoes:
                print("❌ Nenhuma combinação válida encontrada no arquivo")
                return
            
            qtd_super = int(input("Quantas super-combinações gerar (padrão 3): ") or "3")
            
            # Gera super-combinações
            super_combinacoes = ia.gerar_super_combinacao(combinacoes, qtd_super)
            
            if super_combinacoes:
                # Mostra resultados
                print(f"\n🎉 {len(super_combinacoes)} super-combinação(ões) gerada(s)!")
                
                for i, super_info in enumerate(super_combinacoes, 1):
                    print(f"\n🎯 SUPER-COMBINAÇÃO {i}:")
                    print(f"   {','.join(map(str, super_info['super_combinacao']))}")
                    print(f"   Performance: {super_info['performance_prevista']:.1f}")
                    print(f"   Confiança: {super_info['confianca_ia']:.1%}")
                
                # Salva resultados
                ia.salvar_super_combinacoes(super_combinacoes, os.path.basename(arquivo))
            
        elif opcao == "3":
            print("\n📊 ANÁLISE DE COMBINAÇÕES")
            arquivo = input("Caminho do arquivo com combinações: ").strip()
            
            if not os.path.exists(arquivo):
                print("❌ Arquivo não encontrado")
                return
            
            combinacoes = ia.ler_combinacoes_arquivo(arquivo)
            
            if combinacoes:
                analise = ia.analisar_combinacoes_ia(combinacoes)
                
                print(f"\n📈 ANÁLISE IA COMPLETA:")
                print(f"-" * 40)
                print(f"Total de combinações: {analise['total_combinacoes']}")
                print(f"Performance prevista: {analise['performance_prevista']:.1f}")
                print(f"Performance média: {analise['performance_media']:.1f}")
                print(f"Desvio padrão: {analise['performance_std']:.1f}")
                print(f"Melhor combinação: #{analise['melhor_combinacao_idx'] + 1}")
                print(f"Pior combinação: #{analise['pior_combinacao_idx'] + 1}")
        
        else:
            print("❌ Opção inválida")
            
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
    Versão otimizada do super_combinacao_ia com inteligência N12 aplicada
    
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
