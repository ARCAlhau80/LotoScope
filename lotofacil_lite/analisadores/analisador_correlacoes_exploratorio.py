#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔗 ANALISADOR DE CORRELAÇÕES EXPLORATÓRIO
=========================================
Análise profunda de correlações entre números, posições e sequências históricas
Busca por padrões não-óbvios e interdependências ocultas
"""

import pyodbc
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr, chi2_contingency
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from itertools import combinations, permutations
from datetime import datetime
import json
import networkx as nx

# Importa configuração de banco existente
try:
    from database_optimizer import get_optimized_connection
    USE_OPTIMIZER = True
except ImportError:
    USE_OPTIMIZER = None

class AnalisadorCorrelacoes:
    """🔗 Analisador avançado de correlações"""
    
    def __init__(self):
        self.conexao = None
        self.dados = None
        self.correlacoes_encontradas = []
        self.redes_descobertas = []
        
    def conectar_banco(self) -> bool:
        """🔌 Conecta ao banco"""
        try:
            if USE_OPTIMIZER:
                self.conexao = get_optimized_connection()
                print("✅ Analisador de correlações conectado via optimizer")
                return True
        except Exception as e:
            print(f"⚠️ Optimizer falhou: {e}")
        
        # Fallback para conexão direta
        try:
            connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=VADER\\SQLEXPRESS;"
                "DATABASE=LotofacilDB;"
                "Trusted_Connection=yes;"
                "MARS_Connection=Yes;"
            )
            self.conexao = pyodbc.connect(connection_string)
            print("✅ Analisador de correlações conectado diretamente")
            return True
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            
            # Teste com dados sintéticos se não conseguir conectar
            print("🔄 Gerando dados sintéticos para demonstração...")
            return self._gerar_dados_sinteticos()
    
    def _gerar_dados_sinteticos(self) -> bool:
        """🎲 Gera dados sintéticos para demonstração"""
        try:
            import random
            
            # Simula 500 concursos
            dados_sinteticos = []
            for concurso in range(1, 501):
                # Gera 15 números aleatórios únicos entre 1 e 25
                numeros = sorted(random.sample(range(1, 26), 15))
                
                row = {'Concurso': concurso}
                for i, num in enumerate(numeros):
                    row[f'N{i+1}'] = num
                
                dados_sinteticos.append(row)
            
            self.dados = pd.DataFrame(dados_sinteticos)
            print(f"✅ Dados sintéticos gerados: {len(self.dados)} concursos")
            
            # Cria matriz de presença sintética
            self.matriz_presenca = np.zeros((len(self.dados), 25))
            numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                           'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
            
            for idx, row in self.dados.iterrows():
                for col in numeros_cols:
                    if pd.notna(row[col]):
                        numero = int(row[col]) - 1
                        if 0 <= numero < 25:
                            self.matriz_presenca[idx][numero] = 1
            
            print("⚠️ ATENÇÃO: Usando dados SINTÉTICOS para demonstração")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar dados sintéticos: {e}")
            return False
    
    def carregar_dados_completos(self) -> bool:
        """📊 Carrega dados completos para análise"""
        # Se já temos matriz de presença (dados sintéticos), pula
        if hasattr(self, 'matriz_presenca') and self.matriz_presenca is not None:
            return True
            
        if not self.conexao:
            return False
        
        try:
            # Carrega todos os dados históricos
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15
            FROM resultados_int 
            WHERE Concurso IS NOT NULL 
                AND N1 IS NOT NULL 
                AND N15 IS NOT NULL
            ORDER BY Concurso
            """
            
            self.dados = pd.read_sql(query, self.conexao)
            print(f"📊 Carregados {len(self.dados)} concursos completos")
            
            # Cria matriz de presença (0/1) para cada número
            self.matriz_presenca = np.zeros((len(self.dados), 25))  # 25 números possíveis
            
            numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                           'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
            
            for idx, row in self.dados.iterrows():
                for col in numeros_cols:
                    if pd.notna(row[col]):
                        numero = int(row[col]) - 1  # Ajusta para índice 0-based
                        if 0 <= numero < 25:
                            self.matriz_presenca[idx][numero] = 1
            
            print(f"✅ Matriz de presença criada: {self.matriz_presenca.shape}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analisar_correlacoes_par_a_par(self):
        """🔗 Análise de correlações entre pares de números"""
        print("\n🔗 ANÁLISE DE CORRELAÇÕES PAR-A-PAR")
        print("=" * 45)
        
        # Calcula correlações entre todos os pares de números
        correlacoes_fortes = []
        
        for i in range(25):
            for j in range(i + 1, 25):
                # Correlação de Pearson (linear)
                corr_pearson, p_pearson = pearsonr(self.matriz_presenca[:, i], 
                                                 self.matriz_presenca[:, j])
                
                # Correlação de Spearman (monotônica)
                corr_spearman, p_spearman = spearmanr(self.matriz_presenca[:, i], 
                                                    self.matriz_presenca[:, j])
                
                # Considera significativo se p < 0.05 e |corr| > 0.1
                if (p_pearson < 0.05 and abs(corr_pearson) > 0.1) or \
                   (p_spearman < 0.05 and abs(corr_spearman) > 0.1):
                    
                    correlacoes_fortes.append({
                        'numero1': i + 1,
                        'numero2': j + 1,
                        'pearson': corr_pearson,
                        'p_pearson': p_pearson,
                        'spearman': corr_spearman,
                        'p_spearman': p_spearman,
                        'tipo': 'positiva' if max(corr_pearson, corr_spearman) > 0 else 'negativa'
                    })
        
        # Ordena por força da correlação
        correlacoes_fortes.sort(key=lambda x: max(abs(x['pearson']), abs(x['spearman'])), reverse=True)
        
        print(f"✅ Encontradas {len(correlacoes_fortes)} correlações significativas:")
        
        for i, corr in enumerate(correlacoes_fortes[:10]):  # Top 10
            print(f"   {i+1:2d}. Números {corr['numero1']:2d} ↔ {corr['numero2']:2d}: "
                  f"r={corr['pearson']:+.3f} (p={corr['p_pearson']:.3f}) | "
                  f"ρ={corr['spearman']:+.3f} ({corr['tipo']})")
        
        if len(correlacoes_fortes) > 10:
            print(f"   ... e mais {len(correlacoes_fortes) - 10} correlações")
        
        self.correlacoes_encontradas.extend(correlacoes_fortes)
        return correlacoes_fortes
    
    def analisar_clusters_de_numeros(self):
        """📊 Análise de clusters usando hierarchical clustering"""
        print("\n📊 ANÁLISE DE CLUSTERS DE NÚMEROS")
        print("=" * 37)
        
        # Calcula matriz de correlação completa
        matriz_corr = np.corrcoef(self.matriz_presenca.T)
        
        # Converte correlação em distância (1 - |corr|)
        matriz_distancia = 1 - np.abs(matriz_corr)
        
        # Clustering hierárquico
        linkage_matrix = linkage(matriz_distancia, method='ward')
        
        # Forma clusters
        n_clusters = 5  # Tenta 5 clusters
        clusters = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
        
        # Organiza números por cluster
        clusters_organizados = defaultdict(list)
        for numero, cluster in enumerate(clusters):
            clusters_organizados[cluster].append(numero + 1)
        
        print(f"✅ {len(clusters_organizados)} clusters identificados:")
        
        for cluster_id, numeros in clusters_organizados.items():
            # Calcula estatísticas do cluster
            frequencia_media = np.mean([np.sum(self.matriz_presenca[:, n-1]) for n in numeros])
            
            print(f"   🎯 Cluster {cluster_id}: {numeros}")
            print(f"      Frequência média: {frequencia_media:.1f} aparições")
            
            # Analisa co-ocorrência dentro do cluster
            if len(numeros) > 1:
                co_ocorrencias = []
                for i, num1 in enumerate(numeros):
                    for num2 in numeros[i+1:]:
                        # Conta quantas vezes aparecem juntos
                        juntos = np.sum(self.matriz_presenca[:, num1-1] * self.matriz_presenca[:, num2-1])
                        total_jogos = len(self.dados)
                        co_ocorrencias.append((num1, num2, juntos, juntos/total_jogos))
                
                # Mostra as co-ocorrências mais altas
                co_ocorrencias.sort(key=lambda x: x[3], reverse=True)
                if co_ocorrencias:
                    print(f"      Co-ocorrência forte: {co_ocorrencias[0][0]} & {co_ocorrencias[0][1]} "
                          f"({co_ocorrencias[0][2]} vezes, {co_ocorrencias[0][3]:.1%})")
        
        self.redes_descobertas.append({
            'tipo': 'clusters_hierarquicos',
            'clusters': dict(clusters_organizados),
            'linkage_matrix': linkage_matrix.tolist()  # Para JSON
        })
        
        return clusters_organizados
    
    def analisar_sequencias_temporais(self):
        """⏰ Análise de padrões em sequências temporais"""
        print("\n⏰ ANÁLISE DE SEQUÊNCIAS TEMPORAIS")
        print("=" * 38)
        
        # Analisa tendências por janelas deslizantes
        tamanhos_janela = [5, 10, 20, 50]
        padroes_temporais = []
        
        for janela in tamanhos_janela:
            print(f"\n📊 Analisando janela de {janela} concursos:")
            
            # Para cada número, verifica tendências
            tendencias_significativas = []
            
            for numero in range(1, 26):
                serie_temporal = self.matriz_presenca[:, numero-1]
                
                # Calcula médias móveis
                if len(serie_temporal) >= janela * 2:
                    medias_moveis = []
                    for i in range(janela, len(serie_temporal) - janela):
                        janela_antes = np.mean(serie_temporal[i-janela:i])
                        janela_depois = np.mean(serie_temporal[i:i+janela])
                        medias_moveis.append(janela_depois - janela_antes)
                    
                    # Verifica se há tendência consistente
                    if medias_moveis:
                        tendencia_media = np.mean(medias_moveis)
                        variabilidade = np.std(medias_moveis)
                        
                        # Considera significativo se tendência > 2 * variabilidade
                        if abs(tendencia_media) > 2 * variabilidade and variabilidade > 0:
                            tendencias_significativas.append({
                                'numero': numero,
                                'tendencia': tendencia_media,
                                'confianca': abs(tendencia_media) / variabilidade,
                                'direcao': 'crescente' if tendencia_media > 0 else 'decrescente'
                            })
            
            # Ordena por confiança
            tendencias_significativas.sort(key=lambda x: x['confianca'], reverse=True)
            
            if tendencias_significativas:
                print(f"   ✅ {len(tendencias_significativas)} tendências detectadas:")
                for tend in tendencias_significativas[:5]:  # Top 5
                    print(f"      • Número {tend['numero']:2d}: {tend['direcao']} "
                          f"(força: {tend['confianca']:.1f})")
                
                padroes_temporais.append({
                    'janela': janela,
                    'tendencias': tendencias_significativas
                })
            else:
                print("   ⚪ Nenhuma tendência significativa")
        
        return padroes_temporais
    
    def analisar_redes_de_influencia(self):
        """🕸️ Análise de redes de influência entre números"""
        print("\n🕸️ ANÁLISE DE REDES DE INFLUÊNCIA")
        print("=" * 37)
        
        # Cria grafo de influências baseado em correlações
        G = nx.Graph()
        
        # Adiciona nós (números)
        for i in range(1, 26):
            freq = np.sum(self.matriz_presenca[:, i-1])
            G.add_node(i, frequencia=freq)
        
        # Adiciona arestas baseadas em correlações significativas
        for corr in self.correlacoes_encontradas:
            if max(abs(corr['pearson']), abs(corr['spearman'])) > 0.15:  # Limiar mais alto
                peso = max(abs(corr['pearson']), abs(corr['spearman']))
                G.add_edge(corr['numero1'], corr['numero2'], peso=peso)
        
        # Calcula métricas de centralidade
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        
        # Identifica números mais "influentes"
        numeros_influentes = []
        for numero in range(1, 26):
            if numero in G.nodes():
                influencia = (degree_centrality.get(numero, 0) + 
                            betweenness_centrality.get(numero, 0) + 
                            closeness_centrality.get(numero, 0)) / 3
                numeros_influentes.append((numero, influencia))
        
        numeros_influentes.sort(key=lambda x: x[1], reverse=True)
        
        print(f"✅ Rede de {G.number_of_nodes()} nós e {G.number_of_edges()} conexões:")
        print("   🎯 Números mais influentes:")
        for i, (numero, influencia) in enumerate(numeros_influentes[:8]):
            grau = G.degree(numero) if numero in G.nodes() else 0
            print(f"      {i+1}. Número {numero:2d}: influência {influencia:.3f} "
                  f"({grau} conexões)")
        
        # Detecta comunidades
        try:
            import networkx.algorithms.community as nx_comm
            comunidades = nx_comm.greedy_modularity_communities(G)
            
            print(f"\n   🏘️ {len(comunidades)} comunidades detectadas:")
            for i, comunidade in enumerate(comunidades):
                nums = sorted(list(comunidade))
                if len(nums) > 1:
                    print(f"      Comunidade {i+1}: {nums}")
            
            self.redes_descobertas.append({
                'tipo': 'rede_influencia',
                'nos': len(G.nodes()),
                'arestas': len(G.edges()),
                'comunidades': [list(c) for c in comunidades],
                'centralidade': dict(numeros_influentes)
            })
        except ImportError:
            print("   ⚠️ Detecção de comunidades não disponível")
        
        return numeros_influentes, G
    
    def analisar_padroes_posicionais(self):
        """📍 Análise de padrões posicionais"""
        print("\n📍 ANÁLISE DE PADRÕES POSICIONAIS")
        print("=" * 38)
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        padroes_posicionais = {}
        
        # Analisa cada posição
        for pos, col in enumerate(numeros_cols, 1):
            numeros_nesta_posicao = self.dados[col].dropna().astype(int)
            
            # Estatísticas da posição
            media = numeros_nesta_posicao.mean()
            desvio = numeros_nesta_posicao.std()
            moda = numeros_nesta_posicao.mode().iloc[0] if len(numeros_nesta_posicao.mode()) > 0 else None
            
            # Números que aparecem frequentemente nesta posição
            freq_posicao = Counter(numeros_nesta_posicao)
            total_aparicoes = len(numeros_nesta_posicao)
            
            # Identifica números "especiais" para esta posição
            numeros_frequentes = []
            for numero, freq in freq_posicao.most_common(5):
                prob_esperada = 1/25  # 4% se fosse aleatório
                prob_observada = freq / total_aparicoes
                if prob_observada > prob_esperada * 1.5:  # 50% acima do esperado
                    numeros_frequentes.append({
                        'numero': numero,
                        'frequencia': freq,
                        'probabilidade': prob_observada,
                        'excesso': prob_observada / prob_esperada
                    })
            
            if numeros_frequentes:
                padroes_posicionais[pos] = {
                    'media': media,
                    'desvio': desvio,
                    'moda': moda,
                    'numeros_frequentes': numeros_frequentes
                }
        
        # Exibe resultados
        print("✅ Padrões posicionais detectados:")
        for pos, dados in padroes_posicionais.items():
            print(f"\n   📍 Posição {pos:2d} (média: {dados['media']:.1f}):")
            for nf in dados['numeros_frequentes'][:3]:  # Top 3
                print(f"      • Número {nf['numero']:2d}: {nf['probabilidade']:.1%} "
                      f"({nf['excesso']:.1f}x esperado)")
        
        return padroes_posicionais
    
    def gerar_relatorio_correlacoes(self):
        """📋 Gera relatório final de correlações"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE CORRELAÇÕES EXPLORATÓRIAS")
        print("="*60)
        
        # Resumo das descobertas
        total_correlacoes = len(self.correlacoes_encontradas)
        total_redes = len(self.redes_descobertas)
        
        print(f"\n📊 RESUMO DAS DESCOBERTAS:")
        print(f"   • {total_correlacoes} correlações significativas detectadas")
        print(f"   • {total_redes} estruturas de rede identificadas")
        
        # Salva resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        resultado = {
            'timestamp': timestamp,
            'correlacoes_par_a_par': [
                {k: (float(v) if isinstance(v, np.floating) else v) for k, v in corr.items()}
                for corr in self.correlacoes_encontradas
            ],
            'redes_descobertas': [
                {k: (v if k != 'clusters' else {str(ck): cv for ck, cv in v.items()}) 
                 for k, v in rede.items()}
                for rede in self.redes_descobertas
            ],
            'estatisticas': {
                'total_concursos_analisados': int(len(self.dados)),
                'total_correlacoes': int(total_correlacoes),
                'total_redes': int(total_redes)
            }
        }
        
        nome_arquivo = f"correlacoes_exploratoria_{timestamp}.json"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {nome_arquivo}")
        
        # Recomendação final
        if total_correlacoes > 20:
            print("\n🎯 RECOMENDAÇÃO: Correlações abundantes - Implementar sistema!")
            return True
        elif total_correlacoes > 10:
            print("\n📈 RECOMENDAÇÃO: Correlações moderadas - Explorar mais")
            return True
        else:
            print("\n⚪ RECOMENDAÇÃO: Correlações limitadas - Continuar pesquisa")
            return False
    
    def executar_analise_completa(self):
        """🚀 Executa análise completa de correlações"""
        print("🔗 ANALISADOR DE CORRELAÇÕES EXPLORATÓRIO")
        print("="*45)
        
        if not self.conectar_banco() or not self.carregar_dados_completos():
            return False
        
        # Executa todas as análises
        self.analisar_correlacoes_par_a_par()
        self.analisar_clusters_de_numeros()
        self.analisar_sequencias_temporais()
        self.analisar_redes_de_influencia()
        self.analisar_padroes_posicionais()
        
        # Gera relatório final
        return self.gerar_relatorio_correlacoes()

def main():
    """Função principal"""
    analisador = AnalisadorCorrelacoes()
    return analisador.executar_analise_completa()

if __name__ == "__main__":
    main()