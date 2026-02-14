#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 GERADOR DE GRÁFICOS POSICIONAIS - LOTOFÁCIL
==============================================
Gera gráficos comparativos de análise posicional para diferentes períodos
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configuração de estilo
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

class GeradorGraficoPosicional:
    """Gerador de gráficos para análise posicional"""
    
    def __init__(self, analisador):
        self.analisador = analisador
        self.output_dir = "graficos_posicionais"
        
        # Cria diretório se não existir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Diretório criado: {self.output_dir}")
    
    def gerar_heatmap_comparativo(self):
        """Gera heatmap comparativo das frequências posicionais"""
        if not hasattr(self.analisador, 'analises_comparativas'):
            print("❌ Análises comparativas não disponíveis")
            return None
        
        print("📊 Gerando heatmap comparativo...")
        
        periodos = [30, 15, 10, 5, 3]
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        axes = axes.flatten()
        
        for i, periodo in enumerate(periodos):
            key = f'{periodo}_sorteios'
            if key in self.analisador.analises_comparativas:
                freq_df = self.analisador.analises_comparativas[key]['frequencias']
                
                # Converte índices para int se necessário
                if isinstance(freq_df.index[0], str):
                    freq_df.index = [int(x) for x in freq_df.index]
                
                # Heatmap
                ax = axes[i]
                sns.heatmap(
                    freq_df, 
                    annot=True, 
                    fmt='.1f', 
                    cmap='YlOrRd',
                    ax=ax,
                    cbar_kws={'label': 'Frequência (%)'},
                    annot_kws={'size': 8}
                )
                
                ax.set_title(f'Últimos {periodo} Sorteios', fontsize=14, fontweight='bold')
                ax.set_xlabel('Posições')
                ax.set_ylabel('Números')
        
        # Remove eixo extra
        if len(periodos) < len(axes):
            fig.delaxes(axes[-1])
        
        plt.tight_layout()
        
        # Salva gráfico
        filename = f"{self.output_dir}/heatmap_comparativo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 Heatmap salvo: {filename}")
        
        return filename
    
    def gerar_grafico_melhores_numeros(self):
        """Gera gráfico dos melhores números por posição em diferentes períodos"""
        if not hasattr(self.analisador, 'analises_comparativas'):
            print("❌ Análises comparativas não disponíveis")
            return None
        
        print("📊 Gerando gráfico de melhores números...")
        
        # Prepara dados
        periodos = [30, 15, 10, 5, 3]
        posicoes = [f'N{i}' for i in range(1, 16)]
        
        data_for_plot = []
        
        for periodo in periodos:
            key = f'{periodo}_sorteios'
            if key in self.analisador.analises_comparativas:
                melhores = self.analisador.analises_comparativas[key]['melhores_por_posicao']
                
                for posicao in posicoes:
                    if posicao in melhores:
                        melhor_num = melhores[posicao]['melhor']
                        frequencia = melhores[posicao]['frequencia']
                        
                        data_for_plot.append({
                            'Período': f'{periodo} sorteios',
                            'Posição': posicao,
                            'Melhor_Número': melhor_num,
                            'Frequência': frequencia
                        })
        
        if not data_for_plot:
            print("❌ Nenhum dado disponível para gráfico")
            return None
        
        df_plot = pd.DataFrame(data_for_plot)
        
        # Cria gráfico
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
        
        # Gráfico 1: Heatmap dos melhores números
        pivot_nums = df_plot.pivot(index='Período', columns='Posição', values='Melhor_Número')
        sns.heatmap(
            pivot_nums, 
            annot=True, 
            fmt='d', 
            cmap='viridis',
            ax=ax1,
            cbar_kws={'label': 'Melhor Número'}
        )
        ax1.set_title('Melhores Números por Posição em Diferentes Períodos', fontsize=14, fontweight='bold')
        
        # Gráfico 2: Heatmap das frequências
        pivot_freq = df_plot.pivot(index='Período', columns='Posição', values='Frequência')
        sns.heatmap(
            pivot_freq, 
            annot=True, 
            fmt='.1f', 
            cmap='plasma',
            ax=ax2,
            cbar_kws={'label': 'Frequência (%)'}
        )
        ax2.set_title('Frequências dos Melhores Números por Posição', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Salva gráfico
        filename = f"{self.output_dir}/melhores_numeros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 Gráfico salvo: {filename}")
        
        return filename
    
    def gerar_grafico_concentracao(self):
        """Gera gráfico de concentração de frequências por período"""
        if not hasattr(self.analisador, 'analises_comparativas'):
            print("❌ Análises comparativas não disponíveis")
            return None
        
        print("📊 Gerando gráfico de concentração...")
        
        # Prepara dados de concentração
        periodos = []
        concentracoes_media = []
        concentracoes_max = []
        
        for periodo in [30, 15, 10, 5, 3]:
            key = f'{periodo}_sorteios'
            if key in self.analisador.analises_comparativas:
                stats = self.analisador.analises_comparativas[key]['estatisticas']
                
                concentracoes = [stats[pos]['concentracao'] for pos in stats.keys()]
                
                periodos.append(f'{periodo} sorteios')
                concentracoes_media.append(np.mean(concentracoes))
                concentracoes_max.append(np.max(concentracoes))
        
        if not periodos:
            print("❌ Nenhum dado de concentração disponível")
            return None
        
        # Cria gráfico
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        x = np.arange(len(periodos))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, concentracoes_media, width, label='Concentração Média', alpha=0.8)
        bars2 = ax.bar(x + width/2, concentracoes_max, width, label='Concentração Máxima', alpha=0.8)
        
        ax.set_xlabel('Períodos Analisados')
        ax.set_ylabel('Concentração de Frequência (%)')
        ax.set_title('Concentração de Frequências por Período\n(Diferença entre maior e menor frequência)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(periodos)
        ax.legend()
        
        # Adiciona valores nas barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Salva gráfico
        filename = f"{self.output_dir}/concentracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 Gráfico salvo: {filename}")
        
        return filename
    
    def gerar_grafico_predicao(self):
        """Gera gráfico da predição atual"""
        if not hasattr(self.analisador, 'ultima_predicao'):
            print("❌ Predição não disponível")
            return None
        
        print("📊 Gerando gráfico de predição...")
        
        predicao = self.analisador.ultima_predicao
        predicoes = predicao['predicoes']
        confiancas = predicao['confiancas']
        
        # Prepara dados
        posicoes = list(predicoes.keys())
        numeros_preditos = [predicoes[pos] for pos in posicoes]
        confiancas_valores = [confiancas[pos] for pos in posicoes]
        
        # Cria gráfico
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
        
        # Gráfico 1: Números preditos por posição
        colors = plt.cm.viridis(np.array(confiancas_valores))
        bars = ax1.bar(posicoes, numeros_preditos, color=colors, alpha=0.8)
        
        ax1.set_xlabel('Posições')
        ax1.set_ylabel('Número Predito')
        ax1.set_title('Predição para Próximo Sorteio por Posição', fontsize=14, fontweight='bold')
        ax1.set_ylim(0, 26)
        
        # Adiciona valores nas barras
        for i, (bar, conf) in enumerate(zip(bars, confiancas_valores)):
            height = bar.get_height()
            ax1.annotate(f'{int(height)}\n({conf:.1%})',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9)
        
        # Gráfico 2: Confiança por posição
        bars2 = ax2.bar(posicoes, confiancas_valores, color='orange', alpha=0.7)
        
        ax2.set_xlabel('Posições')
        ax2.set_ylabel('Confiança')
        ax2.set_title('Confiança da Predição por Posição', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 1)
        
        # Adiciona linha da confiança média
        confianca_media = np.mean(confiancas_valores)
        ax2.axhline(y=confianca_media, color='red', linestyle='--', alpha=0.7, 
                   label=f'Média: {confianca_media:.1%}')
        ax2.legend()
        
        # Adiciona valores nas barras
        for bar in bars2:
            height = bar.get_height()
            ax2.annotate(f'{height:.1%}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Salva gráfico
        filename = f"{self.output_dir}/predicao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 Gráfico salvo: {filename}")
        
        return filename
    
    def gerar_todos_graficos(self):
        """Gera todos os gráficos disponíveis"""
        print("\n📊 GERANDO TODOS OS GRÁFICOS")
        print("=" * 60)
        
        graficos_gerados = []
        
        # Heatmap comparativo
        try:
            arquivo = self.gerar_heatmap_comparativo()
            if arquivo:
                graficos_gerados.append(arquivo)
        except Exception as e:
            print(f"❌ Erro ao gerar heatmap: {e}")
        
        # Melhores números
        try:
            arquivo = self.gerar_grafico_melhores_numeros()
            if arquivo:
                graficos_gerados.append(arquivo)
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de melhores números: {e}")
        
        # Concentração
        try:
            arquivo = self.gerar_grafico_concentracao()
            if arquivo:
                graficos_gerados.append(arquivo)
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de concentração: {e}")
        
        # Predição
        try:
            arquivo = self.gerar_grafico_predicao()
            if arquivo:
                graficos_gerados.append(arquivo)
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de predição: {e}")
        
        print(f"\n✅ {len(graficos_gerados)} gráficos gerados com sucesso!")
        print(f"📁 Pasta: {self.output_dir}")
        
        return graficos_gerados

def main():
    """Função principal para testar geração de gráficos"""
    print("📊 TESTANDO GERADOR DE GRÁFICOS POSICIONAIS")
    print("=" * 80)
    
    # Aqui você importaria o analisador após executá-lo
    print("⚠️ Para usar este módulo:")
    print("1. Execute primeiro o analisador_posicional_avancado.py")
    print("2. Importe esta classe no seu script")
    print("3. Passe o analisador como parâmetro")
    
    print("\nExemplo de uso:")
    print("```python")
    print("from analisador_posicional_avancado import AnalisadorPosicionalAvancado")
    print("from gerador_graficos_posicionais import GeradorGraficoPosicional")
    print("")
    print("# Executa análise")
    print("analisador = AnalisadorPosicionalAvancado()")
    print("analisador.carregar_dados_historicos()")
    print("analisador.gerar_analise_comparativa()")
    print("")
    print("# Gera gráficos")
    print("gerador = GeradorGraficoPosicional(analisador)")
    print("gerador.gerar_todos_graficos()")
    print("```")

if __name__ == "__main__":
    main()