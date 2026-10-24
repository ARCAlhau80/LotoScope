#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ANALISADOR MACHINE LEARNING EXPLORATÓRIO
=========================================
Aplicação de algoritmos não supervisionados para descobrir clusters,
anomalias ocultas e padrões latentes nos dados da Lotofácil
"""

import pyodbc
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, FastICA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from collections import Counter, defaultdict
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# Importa configuração de banco existente
try:
    from database_optimizer import get_optimized_connection
    USE_OPTIMIZER = True
except ImportError:
    USE_OPTIMIZER = None

class AnalisadorMLExploratorio:
    """🤖 Analisador com Machine Learning para descobertas automáticas"""
    
    def __init__(self):
        self.conexao = None
        self.dados = None
        self.matriz_features = None
        self.descobertas_ml = []
        self.modelos_treinados = {}
        
    def conectar_banco(self) -> bool:
        """🔌 Conecta ao banco ou gera dados sintéticos"""
        try:
            if USE_OPTIMIZER:
                self.conexao = get_optimized_connection()
                print("✅ ML Analisador conectado via optimizer")
                return True
        except Exception as e:
            print(f"⚠️ Optimizer falhou: {e}")
        
        try:
            connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=VADER\\SQLEXPRESS;"
                "DATABASE=LotofacilDB;"
                "Trusted_Connection=yes;"
                "MARS_Connection=Yes;"
            )
            self.conexao = pyodbc.connect(connection_string)
            print("✅ ML Analisador conectado diretamente")
            return True
        except Exception as e:
            print(f"⚠️ Conexão direta falhou: {e}")
            return self._gerar_dados_sinteticos_inteligentes()
    
    def _gerar_dados_sinteticos_inteligentes(self) -> bool:
        """🧠 Gera dados sintéticos com padrões ocultos para ML descobrir"""
        try:
            import random
            
            print("🔄 Gerando dados sintéticos com padrões ocultos...")
            
            dados_sinteticos = []
            
            # Gera 3 "épocas" com comportamentos diferentes
            for epoca in range(3):
                inicio_epoca = epoca * 400 + 1
                fim_epoca = (epoca + 1) * 400
                
                for concurso in range(inicio_epoca, fim_epoca + 1):
                    if epoca == 0:  # Época 1: Favorece números baixos
                        candidatos = list(range(1, 16)) * 3 + list(range(16, 26))
                    elif epoca == 1:  # Época 2: Padrão par/ímpar alternado
                        if concurso % 2 == 0:
                            candidatos = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24] * 2 + list(range(1, 26))
                        else:
                            candidatos = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25] * 2 + list(range(1, 26))
                    else:  # Época 3: Favorece extremos
                        candidatos = list(range(1, 6)) * 2 + list(range(21, 26)) * 2 + list(range(1, 26))
                    
                    # Adiciona ruído aleatório (30% dos casos)
                    if random.random() < 0.3:
                        candidatos = list(range(1, 26))
                    
                    numeros = sorted(random.sample(candidatos, 15))
                    while len(set(numeros)) < 15:
                        numeros = sorted(random.sample(candidatos, 15))
                    numeros = sorted(list(set(numeros))[:15])
                    
                    row = {'Concurso': concurso}
                    for i, num in enumerate(numeros):
                        row[f'N{i+1}'] = num
                    
                    dados_sinteticos.append(row)
            
            self.dados = pd.DataFrame(dados_sinteticos)
            print(f"✅ Dados sintéticos gerados: {len(self.dados)} concursos com 3 épocas")
            print("⚠️ ATENÇÃO: Dados SINTÉTICOS com padrões ocultos para ML descobrir")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar dados sintéticos: {e}")
            return False
    
    def carregar_dados(self) -> bool:
        """📊 Carrega e prepara dados"""
        if hasattr(self, 'dados') and self.dados is not None:
            return self._preparar_features()  # Dados sintéticos já carregados
            
        if not self.conexao:
            return False
        
        try:
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15
            FROM resultados_int 
            WHERE Concurso IS NOT NULL 
            ORDER BY Concurso
            """
            
            self.dados = pd.read_sql(query, self.conexao)
            print(f"📊 Carregados {len(self.dados)} concursos reais")
            return self._preparar_features()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def _preparar_features(self) -> bool:
        """🔧 Prepara features para machine learning"""
        try:
            numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                           'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
            
            features = []
            
            for idx, row in self.dados.iterrows():
                numeros = [int(row[col]) for col in numeros_cols if pd.notna(row[col])]
                
                if len(numeros) == 15:
                    # Feature engineering: extrai características
                    feature_row = []
                    
                    # 1. Presença de cada número (25 features binárias)
                    presenca = [0] * 25
                    for num in numeros:
                        presenca[num-1] = 1
                    feature_row.extend(presenca)
                    
                    # 2. Estatísticas agregadas (10 features)
                    feature_row.extend([
                        np.sum(numeros),           # Soma
                        np.mean(numeros),          # Média
                        np.std(numeros),           # Desvio padrão
                        np.min(numeros),           # Mínimo
                        np.max(numeros),           # Máximo
                        sum(1 for n in numeros if n % 2 == 0),  # Quantidade pares
                        sum(1 for n in numeros if n <= 12),     # Quantidade baixos
                        len([n for i, n in enumerate(sorted(numeros)[:-1]) 
                            if sorted(numeros)[i+1] - n == 1]),  # Sequências
                        np.max(np.diff(sorted(numeros))),       # Maior gap
                        row['Concurso'] % 365                   # Posição no ano
                    ])
                    
                    features.append(feature_row)
            
            self.matriz_features = np.array(features)
            print(f"✅ Features preparadas: {self.matriz_features.shape}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao preparar features: {e}")
            return False
    
    def aplicar_reducao_dimensionalidade(self):
        """📉 Aplica técnicas de redução de dimensionalidade"""
        print("\n📉 REDUÇÃO DE DIMENSIONALIDADE")
        print("=" * 32)
        
        # Normaliza os dados
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(self.matriz_features)
        
        # PCA - Análise de Componentes Principais
        print("   🎯 Aplicando PCA...")
        pca = PCA(n_components=10)
        features_pca = pca.fit_transform(features_scaled)
        
        variancia_explicada = pca.explained_variance_ratio_
        variancia_acumulada = np.cumsum(variancia_explicada)
        
        print(f"      • Primeiros 3 componentes: {variancia_acumulada[2]:.1%} da variância")
        print(f"      • Primeiros 5 componentes: {variancia_acumulada[4]:.1%} da variância")
        print(f"      • Todos 10 componentes: {variancia_acumulada[9]:.1%} da variância")
        
        # t-SNE - Para visualização
        print("   🎯 Aplicando t-SNE...")
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        features_tsne = tsne.fit_transform(features_scaled[:500])  # Limita para performance
        
        # ICA - Análise de Componentes Independentes
        print("   🎯 Aplicando ICA...")
        ica = FastICA(n_components=5, random_state=42)
        features_ica = ica.fit_transform(features_scaled)
        
        self.modelos_treinados.update({
            'pca': pca,
            'scaler': scaler,
            'features_pca': features_pca,
            'features_tsne': features_tsne,
            'features_ica': features_ica,
            'variancia_pca': variancia_explicada
        })
        
        return features_pca, features_tsne
    
    def detectar_clusters(self):
        """🎯 Detecção automática de clusters"""
        print("\n🎯 DETECÇÃO DE CLUSTERS")
        print("=" * 23)
        
        features_pca = self.modelos_treinados['features_pca']
        
        # K-Means com diferentes números de clusters
        print("   🔍 K-Means Clustering...")
        melhor_k = 2
        melhor_score = -1
        
        for k in range(2, 8):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_pca)
            score = silhouette_score(features_pca, labels)
            
            if score > melhor_score:
                melhor_score = score
                melhor_k = k
            
            print(f"      • K={k}: Silhouette Score = {score:.3f}")
        
        # Aplica melhor K-Means
        kmeans_final = KMeans(n_clusters=melhor_k, random_state=42, n_init=10)
        labels_kmeans = kmeans_final.fit_predict(features_pca)
        
        print(f"   ✅ Melhor K-Means: {melhor_k} clusters (score: {melhor_score:.3f})")
        
        # DBSCAN - Densidade
        print("\n   🔍 DBSCAN Clustering...")
        dbscan = DBSCAN(eps=1.5, min_samples=10)
        labels_dbscan = dbscan.fit_predict(features_pca)
        
        n_clusters_dbscan = len(set(labels_dbscan)) - (1 if -1 in labels_dbscan else 0)
        n_noise = list(labels_dbscan).count(-1)
        
        print(f"      • {n_clusters_dbscan} clusters encontrados")
        print(f"      • {n_noise} pontos considerados ruído ({n_noise/len(labels_dbscan):.1%})")
        
        # Hierarchical Clustering
        print("\n   🔍 Hierarchical Clustering...")
        hierarchical = AgglomerativeClustering(n_clusters=melhor_k)
        labels_hierarchical = hierarchical.fit_predict(features_pca)
        
        self.modelos_treinados.update({
            'kmeans': kmeans_final,
            'dbscan': dbscan,
            'hierarchical': hierarchical,
            'labels_kmeans': labels_kmeans,
            'labels_dbscan': labels_dbscan,
            'labels_hierarchical': labels_hierarchical,
            'melhor_k': melhor_k
        })
        
        return labels_kmeans, labels_dbscan, labels_hierarchical
    
    def detectar_anomalias(self):
        """🚨 Detecção de anomalias e outliers"""
        print("\n🚨 DETECÇÃO DE ANOMALIAS")
        print("=" * 24)
        
        features_pca = self.modelos_treinados['features_pca']
        
        # Isolation Forest
        print("   🔍 Isolation Forest...")
        iso_forest = IsolationForest(contamination=0.05, random_state=42)  # 5% anomalias
        anomalias = iso_forest.fit_predict(features_pca)
        
        n_anomalias = (anomalias == -1).sum()
        pct_anomalias = (n_anomalias / len(anomalias)) * 100
        
        print(f"      • {n_anomalias} anomalias detectadas ({pct_anomalias:.1f}%)")
        
        # Identifica concursos anômalos
        indices_anomalias = np.where(anomalias == -1)[0]
        concursos_anomalos = [self.dados.iloc[i]['Concurso'] for i in indices_anomalias[:5]]
        
        print(f"      • Primeiros concursos anômalos: {concursos_anomalos}")
        
        # Análise estatística das anomalias
        print("\n   📊 Características das anomalias:")
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        for i in indices_anomalias[:3]:  # Analisa top 3
            row = self.dados.iloc[i]
            numeros = [int(row[col]) for col in numeros_cols if pd.notna(row[col])]
            
            print(f"      • Concurso {row['Concurso']}: {numeros}")
            print(f"        Soma: {sum(numeros)}, Pares: {sum(1 for n in numeros if n % 2 == 0)}")
        
        self.modelos_treinados.update({
            'iso_forest': iso_forest,
            'anomalias': anomalias,
            'indices_anomalias': indices_anomalias
        })
        
        if n_anomalias > 0:
            self.descobertas_ml.append({
                'tipo': 'anomalias_detectadas',
                'quantidade': int(n_anomalias),
                'porcentagem': float(pct_anomalias),
                'concursos_exemplo': concursos_anomalos
            })
        
        return anomalias
    
    def analisar_padroes_temporais_ml(self):
        """⏰ Análise de padrões temporais com ML"""
        print("\n⏰ PADRÕES TEMPORAIS COM ML")
        print("=" * 27)
        
        labels_kmeans = self.modelos_treinados['labels_kmeans']
        
        # Analisa como clusters mudam ao longo do tempo
        clusters_por_periodo = defaultdict(list)
        
        for i, label in enumerate(labels_kmeans):
            concurso = self.dados.iloc[i]['Concurso']
            periodo = concurso // 100  # Agrupa por centenas
            clusters_por_periodo[periodo].append(label)
        
        print("   📊 Distribuição de clusters por período:")
        for periodo in sorted(clusters_por_periodo.keys()):
            cluster_counts = Counter(clusters_por_periodo[periodo])
            total = len(clusters_por_periodo[periodo])
            
            print(f"      • Período {periodo}00-{periodo}99:")
            for cluster, count in cluster_counts.most_common():
                pct = (count / total) * 100
                print(f"        Cluster {cluster}: {count} ({pct:.1f}%)")
        
        # Detecta mudanças significativas
        mudancas_significativas = []
        
        periodos = sorted(clusters_por_periodo.keys())
        for i in range(1, len(periodos)):
            periodo_atual = periodos[i]
            periodo_anterior = periodos[i-1]
            
            dist_atual = Counter(clusters_por_periodo[periodo_atual])
            dist_anterior = Counter(clusters_por_periodo[periodo_anterior])
            
            # Calcula diferença na distribuição
            diferenca_total = 0
            for cluster in range(self.modelos_treinados['melhor_k']):
                pct_atual = (dist_atual[cluster] / len(clusters_por_periodo[periodo_atual])) * 100
                pct_anterior = (dist_anterior[cluster] / len(clusters_por_periodo[periodo_anterior])) * 100
                diferenca_total += abs(pct_atual - pct_anterior)
            
            if diferenca_total > 20:  # Mudança > 20%
                mudancas_significativas.append({
                    'de_periodo': periodo_anterior,
                    'para_periodo': periodo_atual,
                    'diferenca': diferenca_total
                })
        
        if mudancas_significativas:
            print(f"\n   🚨 {len(mudancas_significativas)} mudanças significativas detectadas:")
            for mudanca in mudancas_significativas:
                print(f"      • Período {mudanca['de_periodo']} → {mudanca['para_periodo']}: "
                      f"{mudanca['diferenca']:.1f}% mudança")
            
            self.descobertas_ml.append({
                'tipo': 'mudancas_temporais',
                'quantidade': len(mudancas_significativas),
                'mudancas': mudancas_significativas
            })
    
    def extrair_regras_clusters(self):
        """📏 Extrai regras interpretáveis dos clusters"""
        print("\n📏 EXTRAÇÃO DE REGRAS DOS CLUSTERS")
        print("=" * 38)
        
        labels_kmeans = self.modelos_treinados['labels_kmeans']
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        regras_clusters = {}
        
        for cluster in range(self.modelos_treinados['melhor_k']):
            indices_cluster = np.where(labels_kmeans == cluster)[0]
            
            if len(indices_cluster) > 0:
                print(f"\n   🎯 CLUSTER {cluster} ({len(indices_cluster)} concursos):")
                
                # Calcula estatísticas do cluster
                somas = []
                qtd_pares = []
                qtd_baixos = []
                
                for idx in indices_cluster:
                    row = self.dados.iloc[idx]
                    numeros = [int(row[col]) for col in numeros_cols if pd.notna(row[col])]
                    
                    if len(numeros) == 15:
                        somas.append(sum(numeros))
                        qtd_pares.append(sum(1 for n in numeros if n % 2 == 0))
                        qtd_baixos.append(sum(1 for n in numeros if n <= 12))
                
                # Características do cluster
                caracteristicas = {
                    'soma_media': np.mean(somas),
                    'soma_std': np.std(somas),
                    'pares_media': np.mean(qtd_pares),
                    'baixos_media': np.mean(qtd_baixos),
                    'tamanho': len(indices_cluster)
                }
                
                print(f"      • Soma média: {caracteristicas['soma_media']:.1f} ± {caracteristicas['soma_std']:.1f}")
                print(f"      • Pares médios: {caracteristicas['pares_media']:.1f}")
                print(f"      • Baixos médios: {caracteristicas['baixos_media']:.1f}")
                
                # Gera regra interpretável
                if caracteristicas['soma_media'] > 200:
                    tipo_cluster = "Somas Altas"
                elif caracteristicas['soma_media'] < 180:
                    tipo_cluster = "Somas Baixas"
                elif caracteristicas['pares_media'] > 8:
                    tipo_cluster = "Muitos Pares"
                elif caracteristicas['pares_media'] < 6:
                    tipo_cluster = "Poucos Pares"
                else:
                    tipo_cluster = "Equilibrado"
                
                print(f"      📋 Regra: {tipo_cluster}")
                
                regras_clusters[cluster] = {
                    'tipo': tipo_cluster,
                    'caracteristicas': caracteristicas
                }
        
        self.modelos_treinados['regras_clusters'] = regras_clusters
        
        if len(regras_clusters) > 1:
            self.descobertas_ml.append({
                'tipo': 'clusters_identificados',
                'quantidade': len(regras_clusters),
                'regras': {k: v['tipo'] for k, v in regras_clusters.items()}
            })
    
    def gerar_relatorio_ml(self):
        """📋 Gera relatório final de Machine Learning"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE MACHINE LEARNING EXPLORATÓRIO")
        print("="*60)
        
        print(f"\n📊 RESUMO DAS DESCOBERTAS:")
        print(f"   • {len(self.descobertas_ml)} tipos de descobertas automáticas")
        print(f"   • {len(self.modelos_treinados)} modelos/técnicas aplicados")
        
        if self.descobertas_ml:
            print(f"\n🤖 DESCOBERTAS AUTOMÁTICAS:")
            for i, descoberta in enumerate(self.descobertas_ml, 1):
                print(f"   {i}. {descoberta['tipo'].replace('_', ' ').title()}")
                if 'quantidade' in descoberta:
                    print(f"      Quantidade detectada: {descoberta['quantidade']}")
        
        # Salva resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Converte numpy types para JSON serializable
        descobertas_json = []
        for descoberta in self.descobertas_ml:
            descoberta_clean = {}
            for k, v in descoberta.items():
                if isinstance(v, (np.integer, np.floating)):
                    descoberta_clean[k] = float(v)
                elif isinstance(v, np.ndarray):
                    descoberta_clean[k] = v.tolist()
                elif isinstance(v, list) and len(v) > 0 and hasattr(v[0], 'item'):
                    descoberta_clean[k] = [x.item() if hasattr(x, 'item') else x for x in v]
                else:
                    descoberta_clean[k] = v
            descobertas_json.append(descoberta_clean)
        
        resultado = {
            'timestamp': timestamp,
            'descobertas_ml': descobertas_json,
            'modelos_aplicados': list(self.modelos_treinados.keys()),
            'matriz_features_shape': list(self.matriz_features.shape),
            'variancia_pca': self.modelos_treinados.get('variancia_pca', []).tolist() if 'variancia_pca' in self.modelos_treinados else []
        }
        
        nome_arquivo = f"ml_exploratorio_{timestamp}.json"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {nome_arquivo}")
        
        # Avaliação final
        if len(self.descobertas_ml) >= 3:
            print(f"\n🚀 RECOMENDAÇÃO: ML encontrou padrões SIGNIFICATIVOS - Implementar!")
            return True
        elif len(self.descobertas_ml) >= 1:
            print(f"\n📈 RECOMENDAÇÃO: Alguns padrões ML interessantes - Refinar")
            return True
        else:
            print(f"\n⚪ RECOMENDAÇÃO: Padrões ML limitados - Tentar outras abordagens")
            return False
    
    def executar_analise_ml_completa(self):
        """🚀 Executa análise completa com Machine Learning"""
        print("🤖 ANALISADOR MACHINE LEARNING EXPLORATÓRIO")
        print("="*44)
        
        if not self.conectar_banco() or not self.carregar_dados():
            return False
        
        # Executa pipeline de ML
        self.aplicar_reducao_dimensionalidade()
        self.detectar_clusters()
        self.detectar_anomalias()
        self.analisar_padroes_temporais_ml()
        self.extrair_regras_clusters()
        
        # Gera relatório final
        return self.gerar_relatorio_ml()

def main():
    """Função principal"""
    analisador = AnalisadorMLExploratorio()
    return analisador.executar_analise_ml_completa()

if __name__ == "__main__":
    main()