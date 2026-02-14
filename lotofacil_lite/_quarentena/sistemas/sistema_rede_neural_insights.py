#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA DE REDE NEURAL PARA ANÁLISE DE INSIGHTS
=================================================
Rede neural especializada em analisar resultados de testes históricos
do núcleo comportamental e identificar padrões, tendências e insights
para melhoria do sistema.

Autor: AR CALHAU
Data: 26 de Agosto de 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
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

class SistemaRedeNeuralInsights:
    """Sistema de IA para análise de insights em testes históricos"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.modelo_predicao = RandomForestRegressor(n_estimators=100, random_state=42)
        self.detector_anomalias = IsolationForest(contamination=0.1, random_state=42)
        self.clusters_modelo = KMeans(n_clusters=5, random_state=42)
        
        self.insights_identificados = []
        self.padroes_encontrados = {}
        self.recomendacoes = []
        self.dados_historicos_reais = []
        
        # Carrega dados reais se disponível
        if DADOS_REAIS_DISPONIVEL:
            self.carregar_dados_historicos_reais()
        
        print("🧠 Sistema de Rede Neural para Insights inicializado")

    def carregar_dados_historicos_reais(self):
        """Carrega dados históricos reais da base Resultados_INT"""
        print("🔍 Carregando dados históricos reais...")
        
        try:
            # Testa conexão
            db_config.test_connection()
            
            # Busca últimos 300 concursos para análise robusta
            query = """
            SELECT TOP 300 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            resultados = db_config.execute_query(query)
            
            if resultados:
                for linha in resultados:
                    concurso = linha[0]
                    numeros = [linha[i] for i in range(1, 16]
                    
                    self.dados_historicos_reais.append({
                        'concurso': concurso), int('numeros': numeros,
                        'soma': sum(numeros)),
                        'pares': len([n for n in numeros if n % 2 == 0]),
                        'impares': len([n for n in numeros if n % 2 == 1]),
                        'consecutivos': self.contar_consecutivos(numeros),
                        'amplitude': max(numeros) - min(numeros)
                    })
                
                print(f"✅ {len(self.dados_historicos_reais)} concursos históricos carregados")
                print(f"📊 Faixa: Concurso {self.dados_historicos_reais[-1]['concurso']} ao {self.dados_historicos_reais[0]['concurso']}")
            else:
                print("⚠️ Nenhum dado encontrado na base")
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados reais: {e}")
            print("🔄 Sistema funcionará em modo simulação")

    def contar_consecutivos(self, numeros):
        """Conta números consecutivos em uma lista"""
        numeros_ordenados = sorted(numeros)
        consecutivos = 0
        max_consecutivos = 0
        
        for i in range(int(int(int(len(numeros_ordenados)) - 1):
            if numeros_ordenados[i+1] == numeros_ordenados[i] + 1:
                consecutivos += 1
                max_consecutivos = max(max_consecutivos)), int(int(consecutivos + 1))
            else:
                consecutivos = 0
        
        return max_consecutivos

    def gerar_ensemble_recomendacao(self, int(dados_teste: Dict)) -> Dict:
        """Gera recomendação combinando RandomForest, clusters e regras comportamentais"""
        print("\n🧠 Gerando recomendação ENSEMBLE combinada...")
        df = self.estruturar_dados_teste(dados_teste)
        if df.empty:
            print("❌ Dados insuficientes para ensemble.")
            return {}

        # 1. Previsão RandomForest
        predicoes = self.gerar_predicoes_performance(df)
        rf_pred = predicoes.get('configuracao_otima', {}).get('acertos_preditos', 0)
        rf_features = predicoes.get('configuracao_otima', {}).get('caracteristicas', {})

        # 2. Cluster de alta performance
        clusters = self.analisar_clusters_performance(df)
        melhor_cluster = None
        melhor_media = 0
        for cid, cinfo in clusters.items():
            if cinfo['media_acertos'] > melhor_media:
                melhor_media = cinfo['media_acertos']
                melhor_cluster = cinfo

        # 3. Regras comportamentais (faixa mais correlacionada)
        correlacoes = self.calcular_correlacoes_avancadas(df, dados_teste)
        faixas = correlacoes.get('distribuicao_vs_acertos', {})
        if faixas:
            melhor_faixa = max(faixas.items(), key=lambda x: abs(x[1]))
        else:
            melhor_faixa = (None, 0)

        # 4. Padrões cíclicos
        padroes = self.analisar_padroes_temporais(df)
        ciclos = [p for p in padroes if p.get('tipo') == 'padrao_ciclico']

        # 5. Combinação ponderada
        recomendacao = {
            'ensemble_score': round((rf_pred + melhor_media) / 2, 2),
            'randomforest_predicao': rf_pred,
            'cluster_alto_performance': melhor_media,
            'caracteristicas_rf': rf_features,
            'caracteristicas_cluster': melhor_cluster['caracteristicas'] if melhor_cluster else {},
            'faixa_mais_correlacionada': melhor_faixa[0],
            'correlacao_faixa': melhor_faixa[1],
            'padroes_ciclicos': ciclos,
            'sugestao_final': self._gerar_sugestao_final(rf_features, melhor_cluster, melhor_faixa)
        }
        print(f"   🏅 ENSEMBLE SCORE: {recomendacao['ensemble_score']}")
        print(f"   🎯 Faixa mais correlacionada: {recomendacao['faixa_mais_correlacionada']} ({recomendacao['correlacao_faixa']:.2f})")
        if ciclos:
            print(f"   🔄 Padrões cíclicos detectados: {[c['parametro'] for c in ciclos]}")
        print(f"   Sugestão final: {recomendacao['sugestao_final']}")
        return recomendacao

    def _gerar_sugestao_final(self, rf_features, melhor_cluster, melhor_faixa):
        """Gera texto de sugestão final combinando os critérios"""
        sugestao = []
        if melhor_faixa[0]:
            faixa_nome = melhor_faixa[0].replace('nucleo_faixa_', '').replace('_', ' ')
            if melhor_faixa[1] > 0:
                sugestao.append(f"Priorize números da {faixa_nome} (correlação positiva)")
            else:
                sugestao.append(f"Evite concentração excessiva na {faixa_nome} (correlação negativa)")
        if melhor_cluster:
            sugestao.append(f"Replicar características do cluster de alta performance: {melhor_cluster['caracteristicas']}")
        if rf_features:
            sugestao.append(f"Configuração ideal RandomForest: {rf_features}")
        return ' | '.join(sugestao)

    def estruturar_dados_teste(self, dados_teste: Dict) -> pd.DataFrame:
        """Estrutura os dados do teste em formato adequado para análise"""
        try:
            resultados = dados_teste['resultados_teste']
            
            # Extrai features dos testes
            dados_estruturados = []
            
            for resultado in resultados:
                # Features básicas
                features = {
                    'teste_numero': resultado['teste_numero'],
                    'janela_inicio': resultado['janela_inicio'],
                    'janela_fim': resultado['janela_fim'],
                    'concurso_validacao': resultado['concurso_validacao'],
                    'acertos': resultado['acertos'],
                    'taxa_acerto': resultado['taxa_acerto'],
                }
                
                # Features do núcleo
                nucleo = resultado['nucleo_comportamental']
                features['nucleo_soma'] = sum(nucleo)
                features['nucleo_media'] = np.mean(nucleo)
                features['nucleo_std'] = np.std(nucleo)
                features['nucleo_min'] = min(nucleo)
                features['nucleo_max'] = max(nucleo)
                features['nucleo_amplitude'] = max(nucleo) - min(nucleo)
                
                # Features de distribuição do núcleo
                features['nucleo_faixa_baixa'] = len([n for n in nucleo if 1 <= n <= 8])
                features['nucleo_faixa_media'] = len([n for n in nucleo if 9 <= n <= 17])
                features['nucleo_faixa_alta'] = len([n for n in nucleo if 18 <= n <= 25])
                
                # Features dos números acertados
                acertados = resultado['numeros_acertados']
                if acertados:
                    features['acertados_soma'] = sum(acertados)
                    features['acertados_media'] = np.mean(acertados)
                    features['acertados_faixa_baixa'] = len([n for n in acertados if 1 <= n <= 8])
                    features['acertados_faixa_media'] = len([n for n in acertados if 9 <= n <= 17])
                    features['acertados_faixa_alta'] = len([n for n in acertados if 18 <= n <= 25])
                else:
                    features['acertados_soma'] = 0
                    features['acertados_media'] = 0
                    features['acertados_faixa_baixa'] = 0
                    features['acertados_faixa_media'] = 0
                    features['acertados_faixa_alta'] = 0
                
                # Features de análise comportamental (se disponível)
                if 'analise_detalhada' in resultado:
                    scores = resultado['analise_detalhada'].get('scores_nucleo', {})
                    if scores:
                        scores_valores = list(scores.values())
                        features['scores_media'] = np.mean(scores_valores)
                        features['scores_std'] = np.std(scores_valores) if len(scores_valores) > 1 else 0
                        features['scores_max'] = max(scores_valores)
                        features['scores_min'] = min(scores_valores)
                    else:
                        features['scores_media'] = 0
                        features['scores_std'] = 0
                        features['scores_max'] = 0
                        features['scores_min'] = 0
                
                dados_estruturados.append(features)
            
            df = pd.DataFrame(dados_estruturados)
            print(f"   📊 Dados estruturados: {len(df)} testes com {len(df.columns)} features")
            
            return df
            
        except Exception as e:
            print(f"   ❌ Erro ao estruturar dados: {e}")
            return pd.DataFrame()
    
    def analisar_padroes_temporais(self, df: pd.DataFrame) -> List[Dict]:
        """Analisa padrões temporais nos resultados"""
        padroes = []
        
        try:
            # Tendência temporal geral
            correlacao_tempo = df['teste_numero'].corr(df['acertos'])
            
            if abs(correlacao_tempo) > 0.3:
                if correlacao_tempo > 0:
                    padroes.append({
                        'tipo': 'tendencia_temporal_positiva',
                        'descricao': f"Performance melhora ao longo do tempo (r={correlacao_tempo:.3f})",
                        'confianca': min(abs(correlacao_tempo), 0.95),
                        'valor': correlacao_tempo
                    })
                else:
                    padroes.append({
                        'tipo': 'tendencia_temporal_negativa',
                        'descricao': f"Performance piora ao longo do tempo (r={correlacao_tempo:.3f})",
                        'confianca': min(abs(correlacao_tempo), 0.95),
                        'valor': correlacao_tempo
                    })
            
            # Análise de ciclos
            if len(df) > 10:
                # Procura por ciclos de 5, 7, 10 testes
                for ciclo in [5, 7, 10]:
                    if len(df) > ciclo * 2:
                        grupos = df.groupby(df.index // ciclo)['acertos'].mean()
                        variancia_ciclos = grupos.var()
                        
                        if variancia_ciclos < df['acertos'].var() * 0.5:  # Menos variância nos grupos
                            padroes.append({
                                'tipo': 'padrao_ciclico',
                                'descricao': f"Padrão cíclico identificado a cada {ciclo} testes",
                                'confianca': 0.75,
                                'parametro': ciclo
                            })
        
        except Exception as e:
            print(f"     ⚠️ Erro na análise temporal: {e}")
        
        return padroes
    
    def analisar_clusters_performance(self, df: pd.DataFrame) -> Dict:
        """Analisa clusters de performance similares"""
        clusters_info = {}
        
        try:
            # Features para clustering
            features_clustering = ['acertos', 'nucleo_soma', 'nucleo_media', 'nucleo_std', 
                                 'nucleo_faixa_baixa', 'nucleo_faixa_media', 'nucleo_faixa_alta']
            
            # Filtra apenas colunas que existem
            features_existentes = [col for col in features_clustering if col in df.columns]
            
            if len(features_existentes) < 3:
                return clusters_info
            
            dados_clustering = df[features_existentes].fillna(0)
            dados_scaled = self.scaler.fit_transform(dados_clustering)
            
            # Executa clustering
            clusters = self.clusters_modelo.fit_predict(dados_scaled)
            df_com_clusters = df.copy()
            df_com_clusters['cluster'] = clusters
            
            # Analisa cada cluster
            for cluster_id in np.unique(clusters):
                cluster_data = df_com_clusters[df_com_clusters['cluster'] == cluster_id]
                
                clusters_info[f'cluster_{cluster_id}'] = {
                    'quantidade_testes': len(cluster_data),
                    'media_acertos': float(cluster_data['acertos'].mean()),
                    'std_acertos': float(cluster_data['acertos'].std()),
                    'caracteristicas': {
                        'nucleo_media': float(cluster_data['nucleo_media'].mean()) if 'nucleo_media' in cluster_data else 0,
                        'nucleo_faixa_baixa_media': float(cluster_data['nucleo_faixa_baixa'].mean()) if 'nucleo_faixa_baixa' in cluster_data else 0,
                        'nucleo_faixa_media_media': float(cluster_data['nucleo_faixa_media'].mean()) if 'nucleo_faixa_media' in cluster_data else 0,
                        'nucleo_faixa_alta_media': float(cluster_data['nucleo_faixa_alta'].mean()) if 'nucleo_faixa_alta' in cluster_data else 0,
                    },
                    'performance_relativa': 'alta' if cluster_data['acertos'].mean() > df['acertos'].mean() else 'baixa',
                    'testes_exemplo': cluster_data['teste_numero'].head(3).tolist()
                }
        
        except Exception as e:
            print(f"     ⚠️ Erro na análise de clusters: {e}")
        
        return clusters_info
    
    def calcular_correlacoes_avancadas(self, df: pd.DataFrame, dados_teste: Dict) -> Dict:
        """Calcula correlações avançadas entre diferentes variáveis"""
        correlacoes = {}
        
        try:
            # Correlação entre características do núcleo e performance
            correlacoes['nucleo_vs_performance'] = {}
            
            for col in ['nucleo_soma', 'nucleo_media', 'nucleo_std', 'nucleo_amplitude']:
                if col in df.columns:
                    corr = df[col].corr(df['acertos'])
                    if abs(corr) > 0.2:
                        correlacoes['nucleo_vs_performance'][col] = {
                            'correlacao': float(corr),
                            'significancia': 'alta' if abs(corr) > 0.5 else 'media' if abs(corr) > 0.3 else 'baixa'
                        }
            
            # Correlação entre distribuição do núcleo e acertos
            correlacoes['distribuicao_vs_acertos'] = {}
            
            for faixa in ['nucleo_faixa_baixa', 'nucleo_faixa_media', 'nucleo_faixa_alta']:
                if faixa in df.columns:
                    corr = df[faixa].corr(df['acertos'])
                    correlacoes['distribuicao_vs_acertos'][faixa] = float(corr)
            
            # Análise de números mais efetivos
            if 'estatisticas' in dados_teste:
                stats = dados_teste['estatisticas']
                if 'numeros_mais_acertados' in stats and 'numeros_mais_frequentes_nucleo' in stats:
                    # Compara números mais frequentes no núcleo vs mais acertados
                    frequentes = set(list(stats['numeros_mais_frequentes_nucleo'].keys())[:5])
                    acertados = set(list(stats['numeros_mais_acertados'].keys())[:5])
                    
                    sobreposicao = len(frequentes.intersection(acertados))
                    correlacoes['efetividade_nucleo'] = {
                        'sobreposicao_top5': sobreposicao,
                        'efetividade': sobreposicao / 5.0,
                        'numeros_frequentes_mas_nao_efetivos': list(frequentes - acertados),
                        'numeros_efetivos_mas_raros_no_nucleo': list(acertados - frequentes)
                    }
        
        except Exception as e:
            print(f"     ⚠️ Erro no cálculo de correlações: {e}")
        
        return correlacoes
    
    def gerar_predicoes_performance(self, df: pd.DataFrame) -> Dict:
        """Gera predições de performance baseadas nos padrões identificados"""
        predicoes = {}
        
        try:
            if len(df) < 5:
                return predicoes
            
            # Features para predição
            features_predicao = ['nucleo_soma', 'nucleo_media', 'nucleo_std', 
                               'nucleo_faixa_baixa', 'nucleo_faixa_media', 'nucleo_faixa_alta']
            
            features_existentes = [col for col in features_predicao if col in df.columns]
            
            if len(features_existentes) < 2:
                return predicoes
            
            X = df[features_existentes].fillna(0)
            y = df['acertos']
            
            # Treina modelo
            self.modelo_predicao.fit(X, y)
            
            # Feature importance
            importancias = dict(zip(features_existentes, self.modelo_predicao.feature_importances_))
            predicoes['feature_importance'] = {k: float(v) for k, v in 
                                             sorted(importancias.items(), key=lambda x: x[1], reverse=True)}
            
            # Predição para configuração "ideal"
            # Baseia-se nas melhores características dos top 20% testes
            top_20_pct = int(len(df) * 0.2) + 1
            melhores_testes = df.nlargest(top_20_pct, 'acertos')
            
            configuracao_ideal = {}
            for feature in features_existentes:
                configuracao_ideal[feature] = melhores_testes[feature].mean()
            
            pred_ideal = self.modelo_predicao.predict([list(configuracao_ideal.values())])[0]
            
            predicoes['configuracao_otima'] = {
                'caracteristicas': configuracao_ideal,
                'acertos_preditos': float(pred_ideal),
                'confianca': float(self.modelo_predicao.score(X, y)) if len(X) > 2 else 0.5
            }
            
        except Exception as e:
            print(f"     ⚠️ Erro na geração de predições: {e}")
        
        return predicoes
