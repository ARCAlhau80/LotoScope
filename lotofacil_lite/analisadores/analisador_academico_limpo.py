"""
ANALISADOR ACADEMICO DE PADROES LOTOFACIL
==========================================
Sistema de analise estatistica academica avancada para Lotofacil
Versao sem emojis para compatibilidade com Windows
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import scipy.signal as signal
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Imports para machine learning
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Database connection
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class AnalisadorAcademico:
    """
    Analisador academico para identificacao de padroes na Lotofacil
    Implementa 6 metodologias estatisticas avancadas
    """
    
    def __init__(self, servidor="DESKTOP-K6JPBDS", database="LOTOFACIL"):
        """
        Inicializa o analisador com conexao ao banco
        
        Args:
            servidor: Nome do servidor SQL Server
            database: Nome do banco de dados
        """
        self.servidor = servidor
        self.database = database
        self.dados = None
        self.resultados_analise = {}
        
        print(f"Inicializando Analisador Academico...")
        print(f"Servidor: {servidor}")
        print(f"Database: {database}")
        
    def conectar_banco(self):
        """
        Estabelece conexao com o banco de dados
        """
        try:
            # Tentar diferentes strings de conexao
            conn_strings = [
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.servidor};DATABASE={self.database};Trusted_Connection=yes',
                f'DRIVER={{SQL Server}};SERVER={self.servidor};DATABASE={self.database};Trusted_Connection=yes',
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.servidor};DATABASE={self.database};Integrated Security=SSPI'
            ]
            
            for conn_str in conn_strings:
                try:
                    # Conexão otimizada para performance
                    if _db_optimizer:
                        conn = _db_optimizer.create_optimized_connection()
                    else:
                        connection = pyodbc.connect(conn_str)
                    print("OK Conexao estabelecida com o banco")
                    return connection
                except:
                    continue
            
            raise Exception("Nenhuma string de conexao funcionou")
            
        except Exception as e:
            print(f"ERRO ao conectar com banco: {e}")
            return None
    
    def carregar_dados(self):
        """
        Carrega dados historicos da Lotofacil
        """
        connection = self.conectar_banco()
        if not connection:
            return False
        
        try:
            query = """
            SELECT 
                Concurso,
                Data_Sorteio,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15,
                QtdeImpares,
                QtdePrimos,
                SomaTotal,
                Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                QtdeGaps,
                QtdeRepetidos,
                Faixa_Baixa, Faixa_Media, Faixa_Alta
            FROM RESULTADOS_INT
            ORDER BY Concurso DESC
            """
            
            self.dados = pd.read_sql(query, connection)
            print(f"OK Dados carregados: {len(self.dados)} registros")
            
            # Converter Data_Sorteio para datetime
            self.dados['Data_Sorteio'] = pd.to_datetime(self.dados['Data_Sorteio'])
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"ERRO ao carregar dados: {e}")
            if connection:
                connection.close()
            return False
    
    def analise_frequencias_avancada(self):
        """
        ANALISE 1: Frequencias e Distribuicoes de Numeros
        
        Implementa:
        - Teste Chi-quadrado para uniformidade
        - Analise de desvios padronizados
        - Identificacao de numeros quentes/frios
        - Calculo de coeficientes de variacao
        """
        print("Executando analise de frequencias avancada...")
        
        # Extrair todas as dezenas sorteadas
        colunas_dezenas = [f'N{i}' for i in range(1, 16)]
        todas_dezenas = []
        
        for _, row in self.dados.iterrows():
            for col in colunas_dezenas:
                todas_dezenas.append(row[col])
        
        # Calcular frequencias observadas
        freq_observadas = {}
        for num in range(1, 26):
            freq_observadas[num] = todas_dezenas.count(num)
        
        # Frequencia esperada (distribuicao uniforme)
        total_sorteios = len(todas_dezenas)
        freq_esperada = total_sorteios / 25
        
        # Teste Chi-quadrado para uniformidade
        frequencias_obs = list(freq_observadas.values())
        chi2_stat, p_valor = stats.chisquare(frequencias_obs)
        
        # Desvios padronizados
        desvios_padronizados = {}
        for num in range(1, 26):
            desvio = (freq_observadas[num] - freq_esperada) / np.sqrt(freq_esperada)
            desvios_padronizados[num] = desvio
        
        # Classificacao de numeros
        numeros_quentes = [num for num, desvio in desvios_padronizados.items() if desvio > 1.96]
        numeros_frios = [num for num, desvio in desvios_padronizados.items() if desvio < -1.96]
        
        # Coeficiente de variacao
        cv = np.std(frequencias_obs) / np.mean(frequencias_obs)
        
        # Interpretacao academica
        interpretacao = []
        
        if p_valor < 0.05:
            interpretacao.append(f"Distribuicao significativamente nao-uniforme (p={p_valor:.4f})")
        else:
            interpretacao.append(f"Distribuicao compativel com uniformidade (p={p_valor:.4f})")
        
        if cv > 0.1:
            interpretacao.append(f"Alta variabilidade nas frequencias (CV={cv:.3f})")
        else:
            interpretacao.append(f"Baixa variabilidade nas frequencias (CV={cv:.3f})")
        
        if numeros_quentes:
            interpretacao.append(f"Numeros com frequencia acima do esperado: {numeros_quentes}")
        
        if numeros_frios:
            interpretacao.append(f"Numeros com frequencia abaixo do esperado: {numeros_frios}")
        
        resultado = {
            'frequencias': freq_observadas,
            'freq_esperada': freq_esperada,
            'chi2_estatistica': chi2_stat,
            'p_valor': p_valor,
            'desvios_padronizados': desvios_padronizados,
            'numeros_quentes': numeros_quentes,
            'numeros_frios': numeros_frios,
            'coef_variacao': cv,
            'interpretacao': interpretacao
        }
        
        self.resultados_analise['frequencias_numeros'] = resultado
        print("OK Analise de frequencias concluida")
        return resultado
    
    def analise_correlacoes_temporais(self):
        """
        ANALISE 2: Correlacoes Temporais e Tendencias
        
        Implementa:
        - Autocorrelacao de series temporais
        - Analise de tendencias com regressao linear
        - Deteccao de sazonalidade
        - Correlacoes cruzadas entre variaveis
        """
        print("Executando analise de correlacoes temporais...")
        
        # Preparar series temporais
        dados_temp = self.dados.sort_values('Concurso').copy()
        
        # Calcular autocorrelacoes para variaveis principais
        campos_analise = ['QtdeImpares', 'QtdePrimos', 'SomaTotal', 'QtdeGaps']
        autocorrelacoes = {}
        
        for campo in campos_analise:
            if campo in dados_temp.columns:
                serie = dados_temp[campo].values
                # Autocorrelacao com lag 1
                if len(serie) > 1:
                    autocorr = np.corrcoef(serie[:-1], serie[1:])[0, 1]
                    autocorrelacoes[campo] = autocorr
        
        # Analise de tendencias
        tendencias = {}
        for campo in campos_analise:
            if campo in dados_temp.columns:
                x = np.arange(len(dados_temp))
                y = dados_temp[campo].values
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                tendencias[campo] = {
                    'slope': slope,
                    'r_squared': r_value**2,
                    'p_valor': p_value,
                    'significativa': p_value < 0.05
                }
        
        # Correlacoes cruzadas
        correlacoes_cruzadas = {}
        for i, campo1 in enumerate(campos_analise):
            for campo2 in campos_analise[i+1:]:
                if campo1 in dados_temp.columns and campo2 in dados_temp.columns:
                    corr = dados_temp[campo1].corr(dados_temp[campo2])
                    correlacoes_cruzadas[f"{campo1}_vs_{campo2}"] = corr
        
        # Interpretacao
        interpretacao = []
        
        # Autocorrelacoes significativas
        autocorr_sig = [campo for campo, corr in autocorrelacoes.items() if abs(corr) > 0.1]
        if autocorr_sig:
            interpretacao.append(f"Autocorrelacao detectada em: {autocorr_sig}")
        
        # Tendencias significativas
        tendencias_sig = [campo for campo, t in tendencias.items() if t['significativa']]
        if tendencias_sig:
            interpretacao.append(f"Tendencias temporais em: {tendencias_sig}")
        
        # Correlacoes fortes
        corr_fortes = [par for par, corr in correlacoes_cruzadas.items() if abs(corr) > 0.3]
        if corr_fortes:
            interpretacao.append(f"Correlacoes fortes entre: {corr_fortes}")
        
        resultado = {
            'autocorrelacoes': autocorrelacoes,
            'tendencias': tendencias,
            'correlacoes_cruzadas': correlacoes_cruzadas,
            'interpretacao': interpretacao
        }
        
        self.resultados_analise['correlacoes_temporais'] = resultado
        print("OK Analise de correlacoes concluida")
        return resultado
    
    def analise_sazonalidade_fourier(self):
        """
        ANALISE 3: Analise de Sazonalidade com FFT
        
        Implementa:
        - Transformada rapida de Fourier (FFT)
        - Deteccao de periodicidades
        - Analise espectral de potencia
        - Identificacao de ciclos dominantes
        """
        print("Executando analise de sazonalidade com FFT...")
        
        # Preparar dados temporais
        dados_temp = self.dados.sort_values('Concurso').copy()
        
        # Analise FFT para diferentes variaveis
        campos_fft = ['QtdeImpares', 'QtdePrimos', 'SomaTotal', 'QtdeGaps']
        resultados_fft = {}
        
        for campo in campos_fft:
            if campo in dados_temp.columns and len(dados_temp) > 10:
                serie = dados_temp[campo].values
                
                # Remover tendencia (detrend)
                serie_detrend = signal.detrend(serie)
                
                # FFT
                fft_valores = np.fft.fft(serie_detrend)
                fft_freq = np.fft.fftfreq(len(serie_detrend))
                fft_power = np.abs(fft_valores)**2
                
                # Encontrar frequencias dominantes (excluindo DC component)
                indices_pos = np.where(fft_freq > 0)[0]
                if len(indices_pos) > 0:
                    idx_max = indices_pos[np.argmax(fft_power[indices_pos])]
                    freq_dominante = fft_freq[idx_max]
                    periodo_dominante = 1 / freq_dominante if freq_dominante != 0 else np.inf
                    
                    resultados_fft[campo] = {
                        'freq_dominante': freq_dominante,
                        'periodo_dominante': periodo_dominante,
                        'potencia_maxima': fft_power[idx_max],
                        'potencia_total': np.sum(fft_power)
                    }
        
        # Interpretacao
        interpretacao = []
        
        for campo, resultado in resultados_fft.items():
            periodo = resultado['periodo_dominante']
            if 7 <= periodo <= 14:
                interpretacao.append(f"Ciclo semanal/quinzenal detectado em {campo} (periodo: {periodo:.1f})")
            elif 20 <= periodo <= 40:
                interpretacao.append(f"Ciclo mensal detectado em {campo} (periodo: {periodo:.1f})")
            elif periodo > 50:
                interpretacao.append(f"Ciclo de longo prazo em {campo} (periodo: {periodo:.1f})")
        
        resultado_final = {
            'analise_fft': resultados_fft,
            'interpretacao': interpretacao
        }
        
        self.resultados_analise['sazonalidade_fft'] = resultado_final
        print("OK Analise de sazonalidade concluida")
        return resultado_final
    
    def analise_anomalias_isolation_forest(self):
        """
        ANALISE 4: Deteccao de Anomalias com Isolation Forest
        
        Implementa:
        - Isolation Forest para deteccao de outliers
        - Scoring de anomalias
        - Identificacao de concursos atipicos
        - Analise multivariada de padroes
        """
        print("Executando analise de anomalias...")
        
        # Preparar features para analise
        features = ['QtdeImpares', 'QtdePrimos', 'SomaTotal', 'QtdeGaps',
                   'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
                   'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta']
        
        # Filtrar apenas features que existem nos dados
        features_disponiveis = [f for f in features if f in self.dados.columns]
        
        if len(features_disponiveis) < 3:
            interpretacao = ["Insuficientes features para analise de anomalias"]
            resultado = {
                'anomalias_detectadas': [],
                'scores_anomalia': {},
                'interpretacao': interpretacao
            }
            self.resultados_analise['anomalias'] = resultado
            return resultado
        
        # Extrair dados para analise
        X = self.dados[features_disponiveis].values
        
        # Normalizar dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Aplicar Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomalias = iso_forest.fit_predict(X_scaled)
        scores = iso_forest.decision_function(X_scaled)
        
        # Identificar concursos anomalos
        indices_anomalos = np.where(anomalias == -1)[0]
        concursos_anomalos = []
        scores_anomalia = {}
        
        for idx in indices_anomalos:
            concurso = self.dados.iloc[idx]['Concurso']
            score = scores[idx]
            concursos_anomalos.append({
                'concurso': int(concurso),
                'score_anomalia': float(score),
                'data': self.dados.iloc[idx]['Data_Sorteio'].strftime('%Y-%m-%d')
            })
            scores_anomalia[int(concurso)] = float(score)
        
        # Interpretacao
        interpretacao = []
        interpretacao.append(f"Detectadas {len(concursos_anomalos)} anomalias em {len(self.dados)} concursos")
        
        if concursos_anomalos:
            concurso_mais_anomalo = min(concursos_anomalos, key=lambda x: x['score_anomalia'])
            interpretacao.append(f"Concurso mais atipico: {concurso_mais_anomalo['concurso']} (score: {concurso_mais_anomalo['score_anomalia']:.3f})")
        
        resultado = {
            'anomalias_detectadas': concursos_anomalos,
            'scores_anomalia': scores_anomalia,
            'total_anomalias': len(concursos_anomalos),
            'percentual_anomalias': (len(concursos_anomalos) / len(self.dados)) * 100,
            'interpretacao': interpretacao
        }
        
        self.resultados_analise['anomalias'] = resultado
        print("OK Analise de anomalias concluida")
        return resultado
    
    def analise_clustering_padroes(self):
        """
        ANALISE 5: Clustering e Agrupamento de Padroes
        
        Implementa:
        - K-means clustering
        - Determinacao otima do numero de clusters
        - Analise de padroes por cluster
        - Caracterizacao de grupos
        """
        print("Executando analise de clustering...")
        
        # Preparar features
        features = ['QtdeImpares', 'QtdePrimos', 'SomaTotal', 'QtdeGaps',
                   'Quintil1', 'Quintil2', 'Quintil3']
        
        features_disponiveis = [f for f in features if f in self.dados.columns]
        
        if len(features_disponiveis) < 3:
            interpretacao = ["Insuficientes features para clustering"]
            resultado = {
                'clusters': {},
                'k_otimo': 0,
                'interpretacao': interpretacao
            }
            self.resultados_analise['clustering'] = resultado
            return resultado
        
        X = self.dados[features_disponiveis].values
        
        # Normalizar dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determinar numero otimo de clusters (metodo do cotovelo)
        max_k = min(10, len(self.dados) // 10)
        if max_k < 2:
            max_k = 2
        
        inertias = []
        K_range = range(2, max_k + 1)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
        
        # Escolher k otimo (metodo simplificado)
        k_otimo = K_range[0]  # Default
        if len(inertias) > 1:
            # Procurar maior reducao na inercia
            reducoes = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
            if reducoes:
                idx_max_reducao = np.argmax(reducoes)
                k_otimo = K_range[idx_max_reducao]
        
        # Clustering final
        kmeans_final = KMeans(n_clusters=k_otimo, random_state=42, n_init=10)
        clusters = kmeans_final.fit_predict(X_scaled)
        
        # Analisar clusters
        analise_clusters = {}
        for cluster_id in range(k_otimo):
            mask = clusters == cluster_id
            cluster_data = self.dados[mask]
            
            analise_clusters[cluster_id] = {
                'tamanho': int(np.sum(mask)),
                'percentual': float(np.sum(mask) / len(self.dados) * 100),
                'concursos': [int(c) for c in cluster_data['Concurso'].tolist()[:10]],  # Primeiros 10
                'caracteristicas': {}
            }
            
            # Caracteristicas medias do cluster
            for feature in features_disponiveis:
                analise_clusters[cluster_id]['caracteristicas'][feature] = float(cluster_data[feature].mean())
        
        # Interpretacao
        interpretacao = []
        interpretacao.append(f"{k_otimo} padroes distintos identificados")
        
        # Cluster dominante
        cluster_maior = max(analise_clusters.items(), key=lambda x: x[1]['tamanho'])
        interpretacao.append(f"Padrao dominante: Cluster {cluster_maior[0]} ({cluster_maior[1]['percentual']:.1f}%)")
        
        resultado = {
            'k_otimo': k_otimo,
            'clusters': analise_clusters,
            'inertias': inertias,
            'interpretacao': interpretacao
        }
        
        self.resultados_analise['clustering'] = resultado
        print("OK Analise de clustering concluida")
        return resultado
    
    def analise_entropia_complexidade(self):
        """
        ANALISE 6: Analise de Entropia e Complexidade
        
        Implementa:
        - Entropia de Shannon
        - Complexidade de Lempel-Ziv
        - Medidas de aleatoriedade
        - Analise de previsibilidade
        """
        print("Executando analise de entropia...")
        
        # Calcular entropia para diferentes aspectos
        aspectos = ['QtdeImpares', 'QtdePrimos', 'SomaTotal', 'QtdeGaps']
        entropias = {}
        
        for aspecto in aspectos:
            if aspecto in self.dados.columns:
                valores = self.dados[aspecto].values
                
                # Calcular entropia de Shannon
                valores_unicos, contagens = np.unique(valores, return_counts=True)
                probabilidades = contagens / len(valores)
                entropia = -np.sum(probabilidades * np.log2(probabilidades + 1e-10))
                
                entropias[aspecto] = entropia
        
        # Entropia das sequencias de numeros sorteados
        colunas_dezenas = [f'N{i}' for i in range(1, 16)]
        if all(col in self.dados.columns for col in colunas_dezenas):
            # Concatenar todas as dezenas em uma sequencia
            sequencia_completa = []
            for _, row in self.dados.iterrows():
                for col in colunas_dezenas:
                    sequencia_completa.append(row[col])
            
            # Entropia da sequencia completa
            valores_unicos, contagens = np.unique(sequencia_completa, return_counts=True)
            probabilidades = contagens / len(sequencia_completa)
            entropia_sequencia = -np.sum(probabilidades * np.log2(probabilidades + 1e-10))
            
            entropias['sequencia_numeros'] = entropia_sequencia
        
        # Interpretacao
        interpretacao = []
        
        if entropias:
            entropia_media = np.mean(list(entropias.values()))
            
            if entropia_media > 2.0:
                interpretacao.append(f"Alta aleatoriedade: entropia media = {entropia_media:.3f}")
            elif entropia_media > 1.0:
                interpretacao.append(f"Aleatoriedade moderada: entropia media = {entropia_media:.3f}")
            else:
                interpretacao.append(f"Baixa aleatoriedade: entropia media = {entropia_media:.3f}")
            
            # Aspecto com maior/menor entropia
            aspecto_max_entropia = max(entropias.items(), key=lambda x: x[1])
            aspecto_min_entropia = min(entropias.items(), key=lambda x: x[1])
            
            interpretacao.append(f"Maior aleatoriedade em: {aspecto_max_entropia[0]} ({aspecto_max_entropia[1]:.3f})")
            interpretacao.append(f"Menor aleatoriedade em: {aspecto_min_entropia[0]} ({aspecto_min_entropia[1]:.3f})")
        
        resultado = {
            'entropias': entropias,
            'entropia_media': float(np.mean(list(entropias.values()))) if entropias else 0.0,
            'interpretacao': interpretacao
        }
        
        self.resultados_analise['entropia'] = resultado
        print("OK Analise de entropia concluida")
        return resultado
    
    def gerar_relatorio_json(self):
        """
        Gera relatorio completo em formato JSON
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        relatorio = {
            'metadata': {
                'timestamp': timestamp,
                'data_analise': datetime.now().isoformat(),
                'total_registros': len(self.dados) if self.dados is not None else 0,
                'servidor': self.servidor,
                'database': self.database
            },
            'analises_realizadas': self.resultados_analise,
            'resumo_executivo': self._gerar_resumo_executivo()
        }
        
        nome_arquivo = f"relatorio_analise_academica_{timestamp}.json"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"OK Relatorio JSON salvo: {nome_arquivo}")
            return nome_arquivo
        except Exception as e:
            print(f"ERRO ao salvar relatorio: {e}")
            return None
    
    def _gerar_resumo_executivo(self):
        """Gera resumo executivo das analises"""
        resumo = {
            'total_analises': len(self.resultados_analise),
            'analises_concluidas': list(self.resultados_analise.keys()),
            'principais_descobertas': []
        }
        
        # Extrair principais descobertas de cada analise
        for tipo_analise, resultado in self.resultados_analise.items():
            if 'interpretacao' in resultado and resultado['interpretacao']:
                resumo['principais_descobertas'].extend(resultado['interpretacao'][:2])  # Primeiras 2 de cada
        
        return resumo
    
    def executar_analise_completa(self):
        """
        Executa todas as analises academicas disponveis
        """
        print("INICIANDO ANALISE ACADEMICA COMPLETA...")
        print("=" * 50)
        
        # Carregar dados
        if not self.carregar_dados():
            print("ERRO: Nao foi possivel carregar os dados")
            return False
        
        # Lista de analises a executar
        analises = [
            ('Frequencias e Distribuicoes', self.analise_frequencias_avancada),
            ('Correlacoes Temporais', self.analise_correlacoes_temporais),
            ('Sazonalidade FFT', self.analise_sazonalidade_fourier),
            ('Deteccao de Anomalias', self.analise_anomalias_isolation_forest),
            ('Clustering de Padroes', self.analise_clustering_padroes),
            ('Entropia e Complexidade', self.analise_entropia_complexidade)
        ]
        
        # Executar cada analise
        analises_concluidas = 0
        
        for i, (nome, funcao) in enumerate(analises, 1):
            try:
                print(f"\nExecutando analise {i}/{len(analises)}...")
                print(f"Tipo: {nome}")
                
                resultado = funcao()
                if resultado:
                    analises_concluidas += 1
                    print(f"OK {nome} concluida")
                else:
                    print(f"AVISO Problemas na analise: {nome}")
                    
            except Exception as e:
                print(f"ERRO na analise {nome}: {e}")
        
        # Gerar relatorio final
        print(f"\nGerando relatorio final...")
        arquivo_relatorio = self.gerar_relatorio_json()
        
        # Resumo final
        print("\n" + "=" * 50)
        print("ANALISE ACADEMICA CONCLUIDA")
        print("=" * 50)
        print(f"Analises executadas: {analises_concluidas}/{len(analises)}")
        print(f"Registros analisados: {len(self.dados)}")
        print(f"Relatorio gerado: {arquivo_relatorio}")
        print("=" * 50)
        
        return analises_concluidas > 0

def main():
    """Funcao principal para execucao do analisador"""
    analisador = AnalisadorAcademico()
    analisador.executar_analise_completa()

if __name__ == "__main__":
    main()