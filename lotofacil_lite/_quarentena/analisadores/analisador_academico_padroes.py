"""
🔬 ANALISADOR ACADÊMICO DE PADRÕES LOTOFÁCIL
=============================================
Sistema completo para descoberta de padrões estatísticos usando métodos acadêmicos
"""

import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.stats import chi2_contingency, pearsonr, spearmanr
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
import os

  # Usa conexão cached para performance
  self.conn = _conn_cache.get_connection()
class AnalisadorPadroesAcademico:
    """
    Analisador acadêmico para descoberta de padrões na Lotofácil
    Implementa métodos estatísticos rigorosos para análise de dados
    """
    
    def __init__(self):
        self.conn = None
        self.dados = None
        self.resultados_analise = {}
        
    def conectar_banco(self):
        """Conecta ao banco SQL Server"""
        try:
            server = 'VADER'
            database = 'LOTOFACIL'
            trusted_connection = 'yes'
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection};'
            # Usa conexão cached para performance
            self.conn = _conn_cache.get_connection()
            print("✅ Conexão estabelecida com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def carregar_dados_completos(self):
        """Carrega todos os dados históricos para análise"""
        if not self.conn:
            print("❌ Conexão não estabelecida")
            return False
            
        try:
            query = """
            SELECT 
                Concurso, Data_Sorteio,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal,
                Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                QtdeGaps, QtdeRepetidos, SEQ, DistanciaExtremos, ParesSequencia,
                QtdeMultiplos3, ParesSaltados, Faixa_Baixa, Faixa_Media, Faixa_Alta,
                RepetidosMesmaPosicao, menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
            FROM RESULTADOS_INT
            ORDER BY Concurso
            """
            
            self.dados = pd.read_sql(query, self.conn)
            print(f"✅ Carregados {len(self.dados)} concursos para análise")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analise_frequencias_numeros(self):
        """
        📊 ANÁLISE 1: Frequências e Distribuições de Números
        """
        print("\n🔍 ANÁLISE DE FREQUÊNCIAS DE NÚMEROS...")
        
        # Coletar todos os números sorteados
        numeros_colunas = [f'N{i}' for i in range(1, 16)]
        todos_numeros = []
        
        for _, row in self.dados.iterrows():
            for col in numeros_colunas:
                todos_numeros.append(row[col])
        
        # Análise de frequência
        freq_numeros = Counter(todos_numeros)
        freq_esperada = len(todos_numeros) / 25  # Frequência esperada se fosse uniforme
        
        # Teste chi-quadrado para uniformidade
        frequencias_observadas = [freq_numeros[i] for i in range(1, 26)]
        chi2_stat, p_value = stats.chisquare(frequencias_observadas)
        
        # Identificar números "quentes" e "frios"
        freq_media = np.mean(frequencias_observadas)
        freq_std = np.std(frequencias_observadas)
        
        numeros_quentes = [i for i in range(1, 26) if freq_numeros[i] > freq_media + freq_std]
        numeros_frios = [i for i in range(1, 26) if freq_numeros[i] < freq_media - freq_std]
        
        # Coeficiente de variação
        cv = freq_std / freq_media
        
        resultado = {
            'frequencias': dict(freq_numeros),
            'freq_esperada': freq_esperada,
            'chi2_uniformidade': {'estatistica': chi2_stat, 'p_valor': p_value},
            'numeros_quentes': numeros_quentes,
            'numeros_frios': numeros_frios,
            'coeficiente_variacao': cv,
            'interpretacao': self._interpretar_frequencias(p_value, cv, numeros_quentes, numeros_frios)
        }
        
        self.resultados_analise['frequencias_numeros'] = resultado
        return resultado
    
    def analise_correlacoes_temporais(self):
        """
        📈 ANÁLISE 2: Correlações Temporais e Tendências
        """
        print("\n🔍 ANÁLISE DE CORRELAÇÕES TEMPORAIS...")
        
        # Análise de autocorrelação para cada campo
        campos_numericos = ['SomaTotal', 'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 
                           'QtdeGaps', 'QtdeRepetidos', 'SEQ', 'DistanciaExtremos']
        
        correlacoes = {}
        tendencias = {}
        
        for campo in campos_numericos:
            serie = self.dados[campo].values
            
            # Autocorrelação com lag 1
            if len(serie) > 1:
                autocorr = pearsonr(serie[:-1], serie[1:])[0]
                correlacoes[campo] = autocorr
            
            # Tendência temporal usando regressão linear
            x = np.arange(len(serie))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, serie)
            
            tendencias[campo] = {
                'slope': slope,
                'r_squared': r_value**2,
                'p_valor': p_value,
                'significativa': p_value < 0.05
            }
        
        # Matriz de correlação entre diferentes campos
        df_campos = self.dados[campos_numericos]
        matriz_correlacao = df_campos.corr()
        
        # Identificar correlações fortes (|r| > 0.5)
        correlacoes_fortes = []
        for i in range(len(matriz_correlacao.columns)):
            for j in range(i+1, len(matriz_correlacao.columns)):
                corr_val = matriz_correlacao.iloc[i, j]
                if abs(corr_val) > 0.5:
                    correlacoes_fortes.append({
                        'campo1': matriz_correlacao.columns[i],
                        'campo2': matriz_correlacao.columns[j],
                        'correlacao': corr_val
                    })
        
        resultado = {
            'autocorrelacoes': correlacoes,
            'tendencias_temporais': tendencias,
            'matriz_correlacao': matriz_correlacao.to_dict(),
            'correlacoes_fortes': correlacoes_fortes,
            'interpretacao': self._interpretar_correlacoes(correlacoes, tendencias, correlacoes_fortes)
        }
        
        self.resultados_analise['correlacoes_temporais'] = resultado
        return resultado
    
    def analise_sazonalidade_ciclos(self):
        """
        🔄 ANÁLISE 3: Sazonalidade e Detecção de Ciclos
        """
        print("\n🔍 ANÁLISE DE SAZONALIDADE E CICLOS...")
        
        # Converter data para datetime se necessário
        self.dados['Data_Sorteio'] = pd.to_datetime(self.dados['Data_Sorteio'])
        self.dados['DiaSemana'] = self.dados['Data_Sorteio'].dt.dayofweek
        self.dados['Mes'] = self.dados['Data_Sorteio'].dt.month
        self.dados['Ano'] = self.dados['Data_Sorteio'].dt.year
        
        # Análise por dia da semana
        analise_dia_semana = {}
        for campo in ['SomaTotal', 'QtdePrimos', 'QtdeImpares']:
            dados_por_dia = self.dados.groupby('DiaSemana')[campo].agg(['mean', 'std', 'count'])
            
            # Teste ANOVA para diferenças significativas
            grupos = [self.dados[self.dados['DiaSemana'] == dia][campo].values 
                     for dia in range(7)]
            f_stat, p_value = stats.f_oneway(*grupos)
            
            analise_dia_semana[campo] = {
                'estatisticas_por_dia': dados_por_dia.to_dict(),
                'anova': {'f_estatistica': f_stat, 'p_valor': p_value}
            }
        
        # Análise por mês
        analise_mensal = {}
        for campo in ['SomaTotal', 'QtdePrimos', 'QtdeImpares']:
            dados_por_mes = self.dados.groupby('Mes')[campo].agg(['mean', 'std', 'count'])
            
            # Teste ANOVA para diferenças mensais
            grupos = [self.dados[self.dados['Mes'] == mes][campo].values 
                     for mes in range(1, 13)]
            f_stat, p_value = stats.f_oneway(*grupos)
            
            analise_mensal[campo] = {
                'estatisticas_por_mes': dados_por_mes.to_dict(),
                'anova': {'f_estatistica': f_stat, 'p_valor': p_value}
            }
        
        # Detecção de ciclos usando FFT
        ciclos_detectados = {}
        for campo in ['SomaTotal', 'QtdePrimos', 'QtdeImpares']:
            serie = self.dados[campo].values
            
            # Remover tendência
            detrended = stats.detrend(serie)
            
            # FFT para detectar periodicidades
            fft = np.fft.fft(detrended)
            freqs = np.fft.fftfreq(len(detrended))
            
            # Encontrar picos significativos
            magnitude = np.abs(fft)
            picos_indices = np.where(magnitude > np.percentile(magnitude, 95))[0]
            
            ciclos = []
            for idx in picos_indices:
                if freqs[idx] > 0:  # Apenas frequências positivas
                    periodo = 1 / freqs[idx]
                    if 2 <= periodo <= len(serie) / 4:  # Períodos razoáveis
                        ciclos.append({
                            'periodo': periodo,
                            'intensidade': magnitude[idx]
                        })
            
            ciclos_detectados[campo] = sorted(ciclos, key=lambda x: x['intensidade'], reverse=True)[:5]
        
        resultado = {
            'analise_dia_semana': analise_dia_semana,
            'analise_mensal': analise_mensal,
            'ciclos_detectados': ciclos_detectados,
            'interpretacao': self._interpretar_sazonalidade(analise_dia_semana, analise_mensal, ciclos_detectados)
        }
        
        self.resultados_analise['sazonalidade_ciclos'] = resultado
        return resultado
    
    def analise_deteccao_anomalias(self):
        """
        🚨 ANÁLISE 4: Detecção de Anomalias e Outliers
        """
        print("\n🔍 ANÁLISE DE DETECÇÃO DE ANOMALIAS...")
        
        campos_analise = ['SomaTotal', 'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 
                         'QtdeGaps', 'QtdeRepetidos', 'SEQ', 'DistanciaExtremos']
        
        anomalias_detectadas = {}
        
        for campo in campos_analise:
            valores = self.dados[campo].values
            
            # Método 1: Z-Score
            z_scores = np.abs(stats.zscore(valores))
            outliers_zscore = np.where(z_scores > 3)[0]
            
            # Método 2: IQR (Interquartile Range)
            Q1 = np.percentile(valores, 25)
            Q3 = np.percentile(valores, 75)
            IQR = Q3 - Q1
            limite_inferior = Q1 - 1.5 * IQR
            limite_superior = Q3 + 1.5 * IQR
            outliers_iqr = np.where((valores < limite_inferior) | (valores > limite_superior))[0]
            
            # Método 3: Isolation Forest (algoritmo de ML)
            from sklearn.ensemble import IsolationForest
            iso_forest = IsolationForest(contamination=0.05, random_state=42)
            outliers_iso = np.where(iso_forest.fit_predict(valores.reshape(-1, 1)) == -1)[0]
            
            # Combinar detecções
            outliers_combinados = list(set(outliers_zscore) | set(outliers_iqr) | set(outliers_iso))
            
            # Detalhes dos outliers
            outliers_detalhes = []
            for idx in outliers_combinados:
                outliers_detalhes.append({
                    'concurso': self.dados.iloc[idx]['Concurso'],
                    'valor': valores[idx],
                    'z_score': z_scores[idx],
                    'metodos_detectaram': {
                        'zscore': idx in outliers_zscore,
                        'iqr': idx in outliers_iqr,
                        'isolation_forest': idx in outliers_iso
                    }
                })
            
            anomalias_detectadas[campo] = {
                'quantidade_outliers': len(outliers_combinados),
                'percentual': len(outliers_combinados) / len(valores) * 100,
                'limites_iqr': {'inferior': limite_inferior, 'superior': limite_superior},
                'outliers_detalhes': outliers_detalhes[:10]  # Top 10 outliers
            }
        
        # Análise de concursos com múltiplas anomalias
        concursos_anomalos = defaultdict(list)
        for campo, info in anomalias_detectadas.items():
            for outlier in info['outliers_detalhes']:
                concursos_anomalos[outlier['concurso']].append(campo)
        
        concursos_multiplas_anomalias = {
            concurso: campos for concurso, campos in concursos_anomalos.items() 
            if len(campos) > 1
        }
        
        resultado = {
            'anomalias_por_campo': anomalias_detectadas,
            'concursos_multiplas_anomalias': concursos_multiplas_anomalias,
            'interpretacao': self._interpretar_anomalias(anomalias_detectadas, concursos_multiplas_anomalias)
        }
        
        self.resultados_analise['deteccao_anomalias'] = resultado
        return resultado
    
    def analise_clustering_padroes(self):
        """
        🎯 ANÁLISE 5: Clustering e Agrupamento de Padrões
        """
        print("\n🔍 ANÁLISE DE CLUSTERING E PADRÕES...")
        
        # Preparar dados para clustering
        campos_clustering = ['SomaTotal', 'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 
                           'QtdeGaps', 'QtdeRepetidos', 'SEQ', 'DistanciaExtremos',
                           'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta']
        
        dados_clustering = self.dados[campos_clustering].copy()
        
        # Normalização dos dados
        scaler = StandardScaler()
        dados_normalizados = scaler.fit_transform(dados_clustering)
        
        # Determinar número ótimo de clusters usando método do cotovelo
        inercias = []
        K_range = range(2, 11)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(dados_normalizados)
            inercias.append(kmeans.inertia_)
        
        # Encontrar o "cotovelo" 
        # Método simples: maior redução percentual
        reducoes = []
        for i in range(1, len(inercias)):
            reducao = (inercias[i-1] - inercias[i]) / inercias[i-1] * 100
            reducoes.append(reducao)
        
        k_otimo = K_range[np.argmax(reducoes) + 1]
        
        # Clustering final
        kmeans_final = KMeans(n_clusters=k_otimo, random_state=42, n_init=10)
        clusters = kmeans_final.fit_predict(dados_normalizados)
        
        # Análise dos clusters
        self.dados['Cluster'] = clusters
        analise_clusters = {}
        
        for cluster_id in range(k_otimo):
            mask = clusters == cluster_id
            cluster_data = dados_clustering[mask]
            
            analise_clusters[cluster_id] = {
                'tamanho': int(np.sum(mask)),
                'percentual': float(np.sum(mask) / len(dados_clustering) * 100),
                'caracteristicas': {
                    campo: {
                        'media': float(cluster_data[campo].mean()),
                        'std': float(cluster_data[campo].std()),
                        'min': float(cluster_data[campo].min()),
                        'max': float(cluster_data[campo].max())
                    } for campo in campos_clustering
                },
                'concursos_exemplo': self.dados[mask]['Concurso'].head(5).tolist()
            }
        
        # PCA para visualização
        pca = PCA(n_components=2)
        dados_pca = pca.fit_transform(dados_normalizados)
        
        variancia_explicada = pca.explained_variance_ratio_
        
        resultado = {
            'k_otimo': k_otimo,
            'inercias_por_k': dict(zip(K_range, inercias)),
            'analise_clusters': analise_clusters,
            'pca_variancia_explicada': variancia_explicada.tolist(),
            'silhueta_score': float(self._calcular_silhueta(dados_normalizados, clusters)),
            'interpretacao': self._interpretar_clustering(analise_clusters, k_otimo)
        }
        
        self.resultados_analise['clustering_padroes'] = resultado
        return resultado
    
    def analise_entropia_aleatoriedade(self):
        """
        🎲 ANÁLISE 6: Entropia e Medidas de Aleatoriedade
        """
        print("\n🔍 ANÁLISE DE ENTROPIA E ALEATORIEDADE...")
        
        # Análise de entropia para sequências de números
        numeros_colunas = [f'N{i}' for i in range(1, 16)]
        
        # Entropia de Shannon para cada posição
        entropias_posicao = {}
        for i, col in enumerate(numeros_colunas, 1):
            valores = self.dados[col].values
            valor_counts = Counter(valores)
            total = len(valores)
            
            # Calcular entropia de Shannon
            entropia = -sum((count/total) * np.log2(count/total) for count in valor_counts.values())
            entropia_maxima = np.log2(25)  # Máxima entropia possível (25 números)
            entropia_normalizada = entropia / entropia_maxima
            
            entropias_posicao[f'posicao_{i}'] = {
                'entropia': entropia,
                'entropia_normalizada': entropia_normalizada,
                'uniformidade': entropia_normalizada  # Quanto mais próximo de 1, mais uniforme
            }
        
        # Análise de runs (sequências)
        def calcular_runs_test(sequencia):
            """Teste de runs para aleatoriedade"""
            # Converter para binário baseado na mediana
            mediana = np.median(sequencia)
            binario = [1 if x > mediana else 0 for x in sequencia]
            
            # Contar runs
            runs = 1
            for i in range(1, len(binario)):
                if binario[i] != binario[i-1]:
                    runs += 1
            
            # Calcular estatística do teste
            n1 = sum(binario)
            n2 = len(binario) - n1
            
            if n1 == 0 or n2 == 0:
                return None
            
            media_runs = (2 * n1 * n2) / (n1 + n2) + 1
            var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
            
            if var_runs <= 0:
                return None
            
            z_score = (runs - media_runs) / np.sqrt(var_runs)
            p_valor = 2 * (1 - stats.norm.cdf(abs(z_score)))
            
            return {
                'runs_observados': runs,
                'runs_esperados': media_runs,
                'z_score': z_score,
                'p_valor': p_valor,
                'aleatorio': p_valor > 0.05
            }
        
        # Aplicar teste de runs em diferentes campos
        testes_runs = {}
        campos_teste = ['SomaTotal', 'QtdePrimos', 'QtdeImpares', 'QtdeGaps']
        
        for campo in campos_teste:
            resultado_runs = calcular_runs_test(self.dados[campo].values)
            if resultado_runs:
                testes_runs[campo] = resultado_runs
        
        # Análise de autocorrelação para detectar padrões
        autocorrelacoes = {}
        for campo in campos_teste:
            serie = self.dados[campo].values
            autocorr_lags = []
            
            for lag in range(1, min(20, len(serie)//4)):
                if len(serie) > lag:
                    corr, p_val = pearsonr(serie[:-lag], serie[lag:])
                    autocorr_lags.append({
                        'lag': lag,
                        'correlacao': corr,
                        'p_valor': p_val,
                        'significativa': p_val < 0.05
                    })
            
            autocorrelacoes[campo] = autocorr_lags
        
        # Teste de Ljung-Box para autocorrelação serial
        ljung_box_resultados = {}
        for campo in campos_teste:
            try:
                from statsmodels.stats.diagnostic import acorr_ljungbox
                resultado_lb = acorr_ljungbox(self.dados[campo].values, lags=10, return_df=True)
                ljung_box_resultados[campo] = {
                    'estatistica': resultado_lb['lb_stat'].iloc[-1],
                    'p_valor': resultado_lb['lb_pvalue'].iloc[-1],
                    'aleatorio': resultado_lb['lb_pvalue'].iloc[-1] > 0.05
                }
            except:
                ljung_box_resultados[campo] = None
        
        resultado = {
            'entropias_posicao': entropias_posicao,
            'testes_runs': testes_runs,
            'autocorrelacoes': autocorrelacoes,
            'ljung_box': ljung_box_resultados,
            'interpretacao': self._interpretar_aleatoriedade(entropias_posicao, testes_runs, ljung_box_resultados)
        }
        
        self.resultados_analise['entropia_aleatoriedade'] = resultado
        return resultado
    
    def _calcular_silhueta(self, dados, labels):
        """Calcula o coeficiente de silhueta para avaliar qualidade do clustering"""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(dados, labels)
        except:
            return 0.0
    
    def _interpretar_frequencias(self, p_value, cv, numeros_quentes, numeros_frios):
        """Interpreta os resultados da análise de frequências"""
        interpretacao = []
        
        if p_value < 0.05:
            interpretacao.append("🔥 DESVIO SIGNIFICATIVO da distribuição uniforme detectado")
        else:
            interpretacao.append("✅ Distribuição próxima do esperado para sorteio aleatório")
        
        if cv > 0.1:
            interpretacao.append(f"📊 Alta variabilidade nas frequências (CV={cv:.3f})")
        else:
            interpretacao.append(f"📊 Baixa variabilidade nas frequências (CV={cv:.3f})")
        
        if numeros_quentes:
            interpretacao.append(f"🔥 Números 'quentes': {numeros_quentes}")
        
        if numeros_frios:
            interpretacao.append(f"❄️ Números 'frios': {numeros_frios}")
        
        return interpretacao
    
    def _interpretar_correlacoes(self, autocorr, tendencias, corr_fortes):
        """Interpreta os resultados da análise de correlações"""
        interpretacao = []
        
        # Autocorrelações significativas
        autocorr_significativas = [campo for campo, valor in autocorr.items() if abs(valor) > 0.1]
        if autocorr_significativas:
            interpretacao.append(f"🔄 Autocorrelação detectada em: {autocorr_significativas}")
        
        # Tendências significativas
        tendencias_sig = [campo for campo, info in tendencias.items() if info['significativa']]
        if tendencias_sig:
            interpretacao.append(f"📈 Tendências temporais em: {tendencias_sig}")
        
        # Correlações fortes
        if corr_fortes:
            interpretacao.append(f"🔗 {len(corr_fortes)} correlações fortes detectadas")
            for corr in corr_fortes[:3]:
                interpretacao.append(f"   • {corr['campo1']} ↔ {corr['campo2']}: r={corr['correlacao']:.3f}")
        
        return interpretacao
    
    def _interpretar_sazonalidade(self, dia_semana, mensal, ciclos):
        """Interpreta os resultados da análise de sazonalidade"""
        interpretacao = []
        
        # Verificar significância nos dias da semana
        sig_dia = [campo for campo, info in dia_semana.items() if info['anova']['p_valor'] < 0.05]
        if sig_dia:
            interpretacao.append(f"📅 Efeito dia da semana significativo em: {sig_dia}")
        
        # Verificar significância mensal
        sig_mes = [campo for campo, info in mensal.items() if info['anova']['p_valor'] < 0.05]
        if sig_mes:
            interpretacao.append(f"🗓️ Efeito sazonal mensal em: {sig_mes}")
        
        # Ciclos detectados
        for campo, ciclos_campo in ciclos.items():
            if ciclos_campo:
                ciclo_principal = ciclos_campo[0]
                interpretacao.append(f"🔄 {campo}: ciclo de {ciclo_principal['periodo']:.1f} sorteios")
        
        return interpretacao
    
    def _interpretar_anomalias(self, anomalias, multiplas):
        """Interpreta os resultados da detecção de anomalias"""
        interpretacao = []
        
        # Campos com mais anomalias
        campos_ordenados = sorted(anomalias.items(), 
                                key=lambda x: x[1]['percentual'], reverse=True)
        
        campo_mais_anomalo = campos_ordenados[0]
        interpretacao.append(f"🚨 {campo_mais_anomalo[0]}: {campo_mais_anomalo[1]['percentual']:.1f}% de outliers")
        
        # Concursos com múltiplas anomalias
        if multiplas:
            interpretacao.append(f"⚠️ {len(multiplas)} concursos com múltiplas anomalias")
            concurso_mais_anomalo = max(multiplas.items(), key=lambda x: len(x[1]))
            interpretacao.append(f"   • Concurso {concurso_mais_anomalo[0]}: anomalias em {len(concurso_mais_anomalo[1])} campos")
        
        return interpretacao
    
    def _interpretar_clustering(self, clusters, k_otimo):
        """Interpreta os resultados do clustering"""
        interpretacao = []
        
        interpretacao.append(f"🎯 {k_otimo} padrões distintos identificados")
        
        # Cluster maior
        cluster_maior = max(clusters.items(), key=lambda x: x[1]['tamanho'])
        interpretacao.append(f"📊 Padrão dominante: Cluster {cluster_maior[0]} ({cluster_maior[1]['percentual']:.1f}%)")
        
        # Características distintivas
        for cluster_id, info in clusters.items():
            if info['percentual'] > 20:  # Clusters significativos
                caracteristicas = []
                for campo, stats in info['caracteristicas'].items():
                    if stats['std'] > 0:  # Evitar divisão por zero
                        cv = stats['std'] / abs(stats['media'])
                        if cv < 0.3:  # Baixa variabilidade = característica distintiva
                            caracteristicas.append(campo)
                
                if caracteristicas:
                    interpretacao.append(f"   • Cluster {cluster_id}: caracterizado por {caracteristicas[:2]}")
        
        return interpretacao
    
    def _interpretar_aleatoriedade(self, entropias, runs, ljung_box):
        """Interpreta os resultados da análise de aleatoriedade"""
        interpretacao = []
        
        # Entropia média
        entropias_valores = [info['entropia_normalizada'] for info in entropias.values()]
        entropia_media = np.mean(entropias_valores)
        
        if entropia_media > 0.9:
            interpretacao.append(f"🎲 Alta aleatoriedade: entropia média = {entropia_media:.3f}")
        elif entropia_media > 0.7:
            interpretacao.append(f"📊 Aleatoriedade moderada: entropia média = {entropia_media:.3f}")
        else:
            interpretacao.append(f"⚠️ Baixa aleatoriedade: entropia média = {entropia_media:.3f}")
        
        # Testes de runs
        runs_aleatorios = [campo for campo, info in runs.items() if info and info['aleatorio']]
        if runs_aleatorios:
            interpretacao.append(f"✅ Teste de runs: {len(runs_aleatorios)}/{len(runs)} campos aleatórios")
        
        # Ljung-Box
        if ljung_box:
            lb_aleatorios = [campo for campo, info in ljung_box.items() 
                           if info and info['aleatorio']]
            interpretacao.append(f"✅ Ljung-Box: {len(lb_aleatorios)}/{len(ljung_box)} campos sem autocorrelação")
        
        return interpretacao
    
    def gerar_relatorio_completo(self):
        """
        📋 Gera relatório completo de todas as análises
        """
        print("\n📋 GERANDO RELATÓRIO COMPLETO...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_analise_academica_{timestamp}.json"
        
        relatorio = {
            'timestamp': timestamp,
            'total_concursos_analisados': len(self.dados),
            'periodo': {
                'inicio': int(self.dados['Concurso'].min()),
                'fim': int(self.dados['Concurso'].max())
            },
            'analises_realizadas': self.resultados_analise,
            'resumo_executivo': self._gerar_resumo_executivo()
        }
        
        # Salvar JSON
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Relatório salvo: {nome_arquivo}")
        return nome_arquivo
    
    def _gerar_resumo_executivo(self):
        """Gera resumo executivo das descobertas principais"""
        resumo = {
            'principais_descobertas': [],
            'recomendacoes': [],
            'nivel_aleatoriedade': 'desconhecido',
            'padroes_significativos': []
        }
        
        # Analisar cada resultado
        for tipo_analise, resultado in self.resultados_analise.items():
            if 'interpretacao' in resultado:
                resumo['principais_descobertas'].extend(resultado['interpretacao'])
        
        # Classificar nível de aleatoriedade geral
        if 'entropia_aleatoriedade' in self.resultados_analise:
            entropia_info = self.resultados_analise['entropia_aleatoriedade']
            if entropia_info.get('entropias_posicao'):
                entropias = [info['entropia_normalizada'] 
                           for info in entropia_info['entropias_posicao'].values()]
                entropia_media = np.mean(entropias)
                
                if entropia_media > 0.9:
                    resumo['nivel_aleatoriedade'] = 'alto'
                elif entropia_media > 0.7:
                    resumo['nivel_aleatoriedade'] = 'moderado'
                else:
                    resumo['nivel_aleatoriedade'] = 'baixo'
        
        # Recomendações baseadas nos achados
        resumo['recomendacoes'] = [
            "Monitorar continuamente os padrões identificados",
            "Validar descobertas com análises futuras",
            "Considerar fatores externos não mensurados",
            "Aplicar métodos de validação cruzada"
        ]
        
        return resumo
    
    def executar_analise_completa(self):
        """
        🚀 Executa toda a suíte de análises acadêmicas
        """
        print("🔬 INICIANDO ANÁLISE ACADÊMICA COMPLETA...")
        print("=" * 60)
        
        if not self.conectar_banco():
            return False
        
        if not self.carregar_dados_completos():
            return False
        
        # Executar todas as análises
        analises = [
            self.analise_frequencias_numeros,
            self.analise_correlacoes_temporais,
            self.analise_sazonalidade_ciclos,
            self.analise_deteccao_anomalias,
            self.analise_clustering_padroes,
            self.analise_entropia_aleatoriedade
        ]
        
        for i, analise in enumerate(analises, 1):
            try:
                print(f"\n📊 Executando análise {i}/{len(analises)}...")
                analise()
                print(f"✅ Análise {i} concluída")
            except Exception as e:
                print(f"❌ Erro na análise {i}: {e}")
        
        # Gerar relatório
        arquivo_relatorio = self.gerar_relatorio_completo()
        
        print("\n" + "=" * 60)
        print("🎉 ANÁLISE ACADÊMICA COMPLETA FINALIZADA!")
        print(f"📄 Relatório: {arquivo_relatorio}")
        
        return arquivo_relatorio

if __name__ == "__main__":
    analisador = AnalisadorPadroesAcademico()
    analisador.executar_analise_completa()