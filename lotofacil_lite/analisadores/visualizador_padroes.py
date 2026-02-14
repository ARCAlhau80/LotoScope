"""
📊 VISUALIZADOR DE PADRÕES LOTOFÁCIL
====================================
Sistema de visualização acadêmica para os padrões descobertos
"""


# 🚀 LAZY LOADING SYSTEM
def lazy_load(module_name):
    try:
        return __import__(module_name)
    except ImportError as e:
        print(f'⚠️ Lazy load failed {module_name}: {e}')
        return None

# import matplotlib.pyplot as plt  # LAZY LOAD
# import numpy as np  # LAZY LOAD
# import pandas as pd  # LAZY LOAD
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Tentar importar seaborn, mas continuar sem ele se não estiver disponível
try:
# import seaborn as sns  # LAZY LOAD
    SEABORN_DISPONIVEL = True
    sns.set_palette("husl")
except ImportError:
    SEABORN_DISPONIVEL = False
    print("⚠️ Seaborn não encontrado. Usando matplotlib puro.")

class VisualizadorPadroes:
    """
    Visualizador acadêmico para padrões da Lotofácil
    Gera gráficos científicos e relatórios visuais
    Funciona com ou sem Seaborn
    """
    
    def __init__(self, dados=None, resultados_analise=None):
        self.dados = dados
        self.resultados_analise = resultados_analise
        
        # Configurar estilo baseado na disponibilidade do seaborn
        if SEABORN_DISPONIVEL:
            plt.style.use('seaborn-v0_8')
        else:
            plt.style.use('default')
            # Configurar cores manualmente
            plt.rcParams['figure.facecolor'] = 'white'
            plt.rcParams['axes.facecolor'] = 'white'
            plt.rcParams['axes.grid'] = True
            plt.rcParams['grid.alpha'] = 0.3
        
    def carregar_relatorio(self, arquivo_json):
        """Carrega relatório de análise de um arquivo JSON"""
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                relatorio = json.load(f)
            self.resultados_analise = relatorio.get('analises_realizadas', {})
            print(f"OK Relatorio carregado: {arquivo_json}")
            return True
        except Exception as e:
            print(f"ERRO ao carregar relatorio: {e}")
            return False
    
    def plot_frequencias_numeros(self, salvar=True):
        """📊 Gráfico de frequências dos números"""
        if 'frequencias_numeros' not in self.resultados_analise:
            print("❌ Dados de frequência não encontrados")
            return
        
        freq_data = self.resultados_analise['frequencias_numeros']
        frequencias = freq_data['frequencias']
        freq_esperada = freq_data['freq_esperada']
        
        # Preparar dados
        numeros = list(range(1, 26))
        freqs = [frequencias[str(num)] for num in numeros]
        
        # Criar gráfico
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Gráfico de barras principal
        bars = ax1.bar(numeros, freqs, alpha=0.7, color='steelblue')
        ax1.axhline(y=freq_esperada, color='red', linestyle='--', 
                   label=f'Frequência Esperada: {freq_esperada:.1f}')
        
        # Destacar números quentes e frios
        quentes = freq_data.get('numeros_quentes', [])
        frios = freq_data.get('numeros_frios', [])
        
        for i, bar in enumerate(bars):
            numero = i + 1
            if numero in quentes:
                bar.set_color('red')
                bar.set_alpha(0.8)
            elif numero in frios:
                bar.set_color('blue')
                bar.set_alpha(0.8)
        
        ax1.set_xlabel('Números')
        ax1.set_ylabel('Frequência Observada')
        ax1.set_title('📊 Frequência de Sorteio dos Números (1-25)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico de desvios
        desvios = [(freq - freq_esperada) for freq in freqs]
        colors = ['red' if d > 0 else 'blue' for d in desvios]
        
        ax2.bar(numeros, desvios, alpha=0.7, color=colors)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_xlabel('Números')
        ax2.set_ylabel('Desvio da Frequência Esperada')
        ax2.set_title('📈 Desvios em Relação à Frequência Esperada')
        ax2.grid(True, alpha=0.3)
        
        # Adicionar estatísticas
        chi2_info = freq_data.get('chi2_uniformidade', {})
        fig.suptitle(f'Análise de Frequências | Chi²={chi2_info.get("estatistica", 0):.2f}, p={chi2_info.get("p_valor", 0):.4f}', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if salvar:
            plt.savefig('frequencias_numeros.png', dpi=300, bbox_inches='tight')
            print("✅ Gráfico salvo: frequencias_numeros.png")
        
        plt.show()
        return fig
    
    def plot_correlacoes_temporais(self, salvar=True):
        """📈 Heatmap de correlações entre campos"""
        if 'correlacoes_temporais' not in self.resultados_analise:
            print("❌ Dados de correlação não encontrados")
            return
        
        corr_data = self.resultados_analise['correlacoes_temporais']
        matriz_corr = pd.DataFrame(corr_data['matriz_correlacao'])
        
        # Criar heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        if SEABORN_DISPONIVEL:
            # Máscara para triangular superior
            mask = np.triu(np.ones_like(matriz_corr, dtype=bool))
            
            # Heatmap com seaborn
            sns.heatmap(matriz_corr, mask=mask, annot=True, cmap='RdBu_r', center=0,
                       square=True, fmt='.3f', cbar_kws={"shrink": .8})
        else:
            # Heatmap com matplotlib puro
            im = ax.imshow(matriz_corr.values, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
            
            # Adicionar colorbar
            cbar = plt.colorbar(im, shrink=0.8)
            cbar.set_label('Correlação')
            
            # Adicionar anotações
            for i in range(len(matriz_corr.columns)):
                for j in range(len(matriz_corr.columns)):
                    if i <= j:  # Máscara triangular superior
                        text = ax.text(j, i, f'{matriz_corr.iloc[i, j]:.3f}',
                                     ha="center", va="center", color="black" if abs(matriz_corr.iloc[i, j]) < 0.5 else "white")
            
            # Configurar eixos
            ax.set_xticks(range(len(matriz_corr.columns)))
            ax.set_yticks(range(len(matriz_corr.columns)))
            ax.set_xticklabels(matriz_corr.columns, rotation=45)
            ax.set_yticklabels(matriz_corr.columns)
        
        ax.set_title('🔗 Matriz de Correlação entre Campos Analíticos', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if salvar:
            plt.savefig('correlacoes_temporais.png', dpi=300, bbox_inches='tight')
            print("✅ Gráfico salvo: correlacoes_temporais.png")
        
        plt.show()
        return fig
    
    def plot_clustering_padroes(self, salvar=True):
        """🎯 Visualização dos clusters identificados"""
        if 'clustering_padroes' not in self.resultados_analise:
            print("❌ Dados de clustering não encontrados")
            return
        
        cluster_data = self.resultados_analise['clustering_padroes']
        analise_clusters = cluster_data['analise_clusters']
        
        # Gráfico de distribuição dos clusters
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Tamanhos dos clusters
        cluster_ids = list(analise_clusters.keys())
        tamanhos = [analise_clusters[str(cid)]['tamanho'] for cid in cluster_ids]
        
        ax1.pie(tamanhos, labels=[f'Cluster {cid}' for cid in cluster_ids], 
               autopct='%1.1f%%', startangle=90)
        ax1.set_title('📊 Distribuição dos Clusters')
        
        # 2. Características médias por cluster (SomaTotal)
        clusters_soma = []
        for cid in cluster_ids:
            caracteristicas = analise_clusters[str(cid)]['caracteristicas']
            soma_media = caracteristicas.get('SomaTotal', {}).get('media', 0)
            clusters_soma.append(soma_media)
        
        ax2.bar([f'C{cid}' for cid in cluster_ids], clusters_soma, 
               color=plt.cm.Set3(np.linspace(0, 1, len(cluster_ids))))
        ax2.set_title('📈 SomaTotal Média por Cluster')
        ax2.set_ylabel('SomaTotal Média')
        
        # 3. QtdePrimos por cluster
        clusters_primos = []
        for cid in cluster_ids:
            caracteristicas = analise_clusters[str(cid)]['caracteristicas']
            primos_media = caracteristicas.get('QtdePrimos', {}).get('media', 0)
            clusters_primos.append(primos_media)
        
        ax3.bar([f'C{cid}' for cid in cluster_ids], clusters_primos,
               color=plt.cm.Set2(np.linspace(0, 1, len(cluster_ids))))
        ax3.set_title('🔢 QtdePrimos Média por Cluster')
        ax3.set_ylabel('QtdePrimos Média')
        
        # 4. Comparação multi-dimensional
        campos_comparacao = ['SomaTotal', 'QtdePrimos', 'QtdeImpares', 'QtdeGaps']
        dados_radar = []
        
        for cid in cluster_ids:
            caracteristicas = analise_clusters[str(cid)]['caracteristicas']
            valores = []
            for campo in campos_comparacao:
                valor = caracteristicas.get(campo, {}).get('media', 0)
                valores.append(valor)
            dados_radar.append(valores)
        
        # Normalizar para radar chart
        dados_radar = np.array(dados_radar)
        dados_norm = (dados_radar - dados_radar.min(axis=0)) / (dados_radar.max(axis=0) - dados_radar.min(axis=0))
        
        x = np.arange(len(campos_comparacao))
        width = 0.8 / len(cluster_ids)
        
        for i, cid in enumerate(cluster_ids):
            ax4.bar(x + i * width, dados_norm[i], width, 
                   label=f'Cluster {cid}', alpha=0.7)
        
        ax4.set_xlabel('Campos')
        ax4.set_ylabel('Valores Normalizados')
        ax4.set_title('📊 Perfil Multidimensional dos Clusters')
        ax4.set_xticks(x + width * (len(cluster_ids) - 1) / 2)
        ax4.set_xticklabels(campos_comparacao, rotation=45)
        ax4.legend()
        
        plt.suptitle(f'🎯 Análise de Clusters | {len(cluster_ids)} Padrões Identificados', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if salvar:
            plt.savefig('clustering_padroes.png', dpi=300, bbox_inches='tight')
            print("✅ Gráfico salvo: clustering_padroes.png")
        
        plt.show()
        return fig
    
    def plot_anomalias_deteccao(self, salvar=True):
        """🚨 Visualização das anomalias detectadas"""
        if 'deteccao_anomalias' not in self.resultados_analise:
            print("❌ Dados de anomalias não encontrados")
            return
        
        anomalias_data = self.resultados_analise['deteccao_anomalias']
        anomalias_campos = anomalias_data['anomalias_por_campo']
        
        # Preparar dados
        campos = list(anomalias_campos.keys())
        percentuais = [anomalias_campos[campo]['percentual'] for campo in campos]
        quantidades = [anomalias_campos[campo]['quantidade_outliers'] for campo in campos]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Percentual de outliers por campo
        bars1 = ax1.barh(campos, percentuais, color='red', alpha=0.7)
        ax1.set_xlabel('Percentual de Outliers (%)')
        ax1.set_title('🚨 Percentual de Anomalias por Campo')
        ax1.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for i, (bar, val) in enumerate(zip(bars1, percentuais)):
            ax1.text(val + 0.1, i, f'{val:.1f}%', va='center')
        
        # 2. Quantidade absoluta de outliers
        bars2 = ax2.barh(campos, quantidades, color='orange', alpha=0.7)
        ax2.set_xlabel('Quantidade de Outliers')
        ax2.set_title('📊 Quantidade Absoluta de Anomalias')
        ax2.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for i, (bar, val) in enumerate(zip(bars2, quantidades)):
            ax2.text(val + 0.5, i, str(val), va='center')
        
        plt.suptitle('🔍 Análise de Detecção de Anomalias', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if salvar:
            plt.savefig('anomalias_deteccao.png', dpi=300, bbox_inches='tight')
            print("✅ Gráfico salvo: anomalias_deteccao.png")
        
        plt.show()
        return fig
    
    def plot_entropia_aleatoriedade(self, salvar=True):
        """🎲 Visualização da análise de aleatoriedade"""
        if 'entropia_aleatoriedade' not in self.resultados_analise:
            print("❌ Dados de aleatoriedade não encontrados")
            return
        
        entropia_data = self.resultados_analise['entropia_aleatoriedade']
        entropias_posicao = entropia_data.get('entropias_posicao', {})
        testes_runs = entropia_data.get('testes_runs', {})
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Entropias por posição
        if entropias_posicao:
            posicoes = list(range(1, 16))
            entropias = [entropias_posicao[f'posicao_{i}']['entropia_normalizada'] 
                        for i in posicoes]
            
            bars = ax1.bar(posicoes, entropias, color='green', alpha=0.7)
            ax1.axhline(y=1.0, color='red', linestyle='--', 
                       label='Entropia Máxima (Aleatório Perfeito)')
            ax1.axhline(y=0.9, color='orange', linestyle='--', 
                       label='Limiar Alta Aleatoriedade')
            
            ax1.set_xlabel('Posição do Número')
            ax1.set_ylabel('Entropia Normalizada')
            ax1.set_title('🎲 Entropia por Posição')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 1.1)
        
        # 2. Resultados dos testes de runs
        if testes_runs:
            campos_runs = list(testes_runs.keys())
            p_valores = [testes_runs[campo]['p_valor'] for campo in campos_runs]
            colors = ['green' if p > 0.05 else 'red' for p in p_valores]
            
            bars = ax2.bar(range(len(campos_runs)), p_valores, color=colors, alpha=0.7)
            ax2.axhline(y=0.05, color='red', linestyle='--', 
                       label='p = 0.05 (Limiar Significância)')
            
            ax2.set_xlabel('Campos')
            ax2.set_ylabel('p-valor (Teste de Runs)')
            ax2.set_title('📊 Testes de Aleatoriedade (Runs Test)')
            ax2.set_xticks(range(len(campos_runs)))
            ax2.set_xticklabels(campos_runs, rotation=45)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Adicionar rótulos
            for i, (bar, p_val) in enumerate(zip(bars, p_valores)):
                ax2.text(i, p_val + 0.01, f'{p_val:.3f}', ha='center', va='bottom')
        
        plt.suptitle('🔬 Análise de Aleatoriedade e Entropia', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if salvar:
            plt.savefig('entropia_aleatoriedade.png', dpi=300, bbox_inches='tight')
            print("✅ Gráfico salvo: entropia_aleatoriedade.png")
        
        plt.show()
        return fig
    
    def gerar_dashboard_completo(self, salvar=True):
        """📊 Gera dashboard completo com todas as visualizações"""
        print("📊 GERANDO DASHBOARD COMPLETO...")
        
        graficos_gerados = []
        
        try:
            # Gerar todos os gráficos
            fig1 = self.plot_frequencias_numeros(salvar=False)
            if fig1: graficos_gerados.append("Frequências")
            
            fig2 = self.plot_correlacoes_temporais(salvar=False)  
            if fig2: graficos_gerados.append("Correlações")
            
            fig3 = self.plot_clustering_padroes(salvar=False)
            if fig3: graficos_gerados.append("Clustering")
            
            fig4 = self.plot_anomalias_deteccao(salvar=False)
            if fig4: graficos_gerados.append("Anomalias")
            
            fig5 = self.plot_entropia_aleatoriedade(salvar=False)
            if fig5: graficos_gerados.append("Aleatoriedade")
            
            if salvar:
                # Salvar dashboard combinado
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_dashboard = f"dashboard_analise_academica_{timestamp}.html"
                
                # Criar HTML simples
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Dashboard Análise Acadêmica Lotofácil</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; color: #2c3e50; }}
                        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; }}
                        .graficos {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                        .grafico {{ text-align: center; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>🔬 Dashboard Análise Acadêmica Lotofácil</h1>
                        <p>Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                    </div>
                    
                    <div class="summary">
                        <h2>📋 Resumo das Análises</h2>
                        <p><strong>Gráficos gerados:</strong> {', '.join(graficos_gerados)}</p>
                        <p><strong>Total de análises:</strong> {len(graficos_gerados)}</p>
                    </div>
                    
                    <div class="graficos">
                        <div class="grafico">
                            <h3>📊 Frequências dos Números</h3>
                            <img src="frequencias_numeros.png" style="max-width: 100%;">
                        </div>
                        <div class="grafico">
                            <h3>🔗 Correlações Temporais</h3>
                            <img src="correlacoes_temporais.png" style="max-width: 100%;">
                        </div>
                        <div class="grafico">
                            <h3>🎯 Análise de Clusters</h3>
                            <img src="clustering_padroes.png" style="max-width: 100%;">
                        </div>
                        <div class="grafico">
                            <h3>🚨 Detecção de Anomalias</h3>
                            <img src="anomalias_deteccao.png" style="max-width: 100%;">
                        </div>
                        <div class="grafico">
                            <h3>🎲 Análise de Aleatoriedade</h3>
                            <img src="entropia_aleatoriedade.png" style="max-width: 100%;">
                        </div>
                    </div>
                </body>
                </html>
                """
                
                with open(nome_dashboard, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"✅ Dashboard salvo: {nome_dashboard}")
                
                # Salvar gráficos individuais também
                if fig1: fig1.savefig('frequencias_numeros.png', dpi=300, bbox_inches='tight')
                if fig2: fig2.savefig('correlacoes_temporais.png', dpi=300, bbox_inches='tight')
                if fig3: fig3.savefig('clustering_padroes.png', dpi=300, bbox_inches='tight')
                if fig4: fig4.savefig('anomalias_deteccao.png', dpi=300, bbox_inches='tight')
                if fig5: fig5.savefig('entropia_aleatoriedade.png', dpi=300, bbox_inches='tight')
                
                return nome_dashboard
        
        except Exception as e:
            print(f"❌ Erro ao gerar dashboard: {e}")
            return None
    
    def relatorio_texto_executivo(self):
        """📝 Gera relatório executivo em texto"""
        if not self.resultados_analise:
            print("❌ Nenhum resultado de análise carregado")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_relatorio = f"relatorio_executivo_{timestamp}.txt"
        
        with open(nome_relatorio, 'w', encoding='utf-8') as f:
            f.write("🔬 RELATÓRIO EXECUTIVO - ANÁLISE ACADÊMICA LOTOFÁCIL\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            # Resumo das análises
            f.write("📊 ANÁLISES REALIZADAS:\n")
            f.write("-" * 30 + "\n")
            for tipo_analise in self.resultados_analise.keys():
                f.write(f"✅ {tipo_analise.replace('_', ' ').title()}\n")
            
            f.write(f"\nTotal de análises: {len(self.resultados_analise)}\n\n")
            
            # Principais descobertas
            f.write("🔍 PRINCIPAIS DESCOBERTAS:\n")
            f.write("-" * 30 + "\n")
            
            for tipo_analise, resultado in self.resultados_analise.items():
                if 'interpretacao' in resultado:
                    f.write(f"\n{tipo_analise.replace('_', ' ').title()}:\n")
                    for interpretacao in resultado['interpretacao']:
                        f.write(f"  • {interpretacao}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("📋 Relatório gerado automaticamente pelo Sistema de Análise Acadêmica\n")
        
        print(f"✅ Relatório executivo salvo: {nome_relatorio}")
        return nome_relatorio

if __name__ == "__main__":
    # Exemplo de uso
    visualizador = VisualizadorPadroes()
    
    # Para usar, primeiro execute o analisador para gerar os dados
    print("📊 Para usar o visualizador:")
    print("1. Execute o analisador_academico_padroes.py primeiro")
    print("2. Carregue o arquivo JSON gerado com visualizador.carregar_relatorio('arquivo.json')")
    print("3. Execute visualizador.gerar_dashboard_completo()")