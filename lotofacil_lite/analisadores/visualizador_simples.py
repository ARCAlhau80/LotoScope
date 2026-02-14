"""
VISUALIZADOR SIMPLES DE PADROES LOTOFACIL
==========================================
Versao sem emojis para evitar problemas de encoding
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class VisualizadorSimples:
    """
    Visualizador simples para padroes da Lotofacil
    Sem emojis para evitar problemas de encoding
    """
    
    def __init__(self, dados=None, resultados_analise=None):
        self.dados = dados
        self.resultados_analise = resultados_analise
        plt.style.use('default')
        
    def carregar_relatorio(self, arquivo_json):
        """Carrega relatorio de analise de um arquivo JSON"""
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
        """Grafico de frequencias dos numeros"""
        if 'frequencias_numeros' not in self.resultados_analise:
            print("ERRO Dados de frequencia nao encontrados")
            return None
        
        freq_data = self.resultados_analise['frequencias_numeros']
        frequencias = freq_data['frequencias']
        freq_esperada = freq_data.get('freq_esperada', 2000)
        
        # Preparar dados
        numeros = list(range(1, 26))
        freqs = [int(frequencias.get(str(num), freq_esperada)) for num in numeros]
        
        # Criar grafico
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars = ax.bar(numeros, freqs, alpha=0.7, color='steelblue')
        ax.axhline(y=freq_esperada, color='red', linestyle='--', 
                   label=f'Frequencia Esperada: {freq_esperada:.1f}')
        
        ax.set_xlabel('Numeros')
        ax.set_ylabel('Frequencia Observada')
        ax.set_title('Frequencia de Sorteio dos Numeros (1-25)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if salvar:
            plt.savefig('frequencias_numeros_simples.png', dpi=300, bbox_inches='tight')
            print("OK Grafico salvo: frequencias_numeros_simples.png")
        
        return fig
    
    def plot_correlacoes_temporais(self, salvar=True):
        """Visualizacao simples de correlacoes"""
        if 'correlacoes_temporais' not in self.resultados_analise:
            print("ERRO Dados de correlacao nao encontrados")
            return None
        
        corr_data = self.resultados_analise['correlacoes_temporais']
        autocorr = corr_data.get('autocorrelacoes', {})
        
        if not autocorr:
            print("AVISO Nenhuma autocorrelacao encontrada")
            return None
        
        # Criar grafico simples
        fig, ax = plt.subplots(figsize=(10, 6))
        
        campos = list(autocorr.keys())
        valores = list(autocorr.values())
        
        bars = ax.bar(campos, valores, alpha=0.7, color='green')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        ax.set_xlabel('Campos')
        ax.set_ylabel('Autocorrelacao')
        ax.set_title('Autocorrelacoes Temporais')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if salvar:
            plt.savefig('correlacoes_simples.png', dpi=300, bbox_inches='tight')
            print("OK Grafico salvo: correlacoes_simples.png")
        
        return fig
    
    def gerar_relatorio_texto(self):
        """Gera relatorio executivo em texto simples"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_relatorio = f"relatorio_simples_{timestamp}.txt"
        
        with open(nome_relatorio, 'w', encoding='utf-8') as f:
            f.write("RELATORIO EXECUTIVO - ANALISE ACADEMICA LOTOFACIL\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Data de Geracao: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            # Resumo das analises
            f.write("ANALISES REALIZADAS:\n")
            f.write("-" * 30 + "\n")
            for tipo_analise in self.resultados_analise.keys():
                f.write(f"OK {tipo_analise.replace('_', ' ').title()}\n")
            
            f.write(f"\nTotal de analises: {len(self.resultados_analise)}\n\n")
            
            # Principais descobertas
            f.write("PRINCIPAIS DESCOBERTAS:\n")
            f.write("-" * 30 + "\n")
            
            for tipo_analise, resultado in self.resultados_analise.items():
                if 'interpretacao' in resultado:
                    f.write(f"\n{tipo_analise.replace('_', ' ').title()}:\n")
                    for interpretacao in resultado['interpretacao']:
                        # Remover emojis da interpretacao
                        texto_limpo = interpretacao.encode('ascii', errors='ignore').decode('ascii')
                        f.write(f"  • {texto_limpo}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Relatorio gerado automaticamente pelo Sistema de Analise Academica\n")
        
        print(f"OK Relatorio executivo salvo: {nome_relatorio}")
        return nome_relatorio
    
    def testar_visualizacoes(self):
        """Testa todas as visualizacoes disponiveis"""
        print("TESTANDO VISUALIZACOES...")
        
        graficos_ok = 0
        
        # Testar frequencias
        try:
            fig1 = self.plot_frequencias_numeros(salvar=True)
            if fig1:
                graficos_ok += 1
                print("OK Grafico de frequencias gerado")
                plt.close(fig1)
        except Exception as e:
            print(f"ERRO ao gerar frequencias: {e}")
        
        # Testar correlacoes
        try:
            fig2 = self.plot_correlacoes_temporais(salvar=True)
            if fig2:
                graficos_ok += 1
                print("OK Grafico de correlacoes gerado")
                plt.close(fig2)
        except Exception as e:
            print(f"ERRO ao gerar correlacoes: {e}")
        
        # Testar relatorio
        try:
            relatorio = self.gerar_relatorio_texto()
            if relatorio:
                graficos_ok += 1
                print("OK Relatorio texto gerado")
        except Exception as e:
            print(f"ERRO ao gerar relatorio: {e}")
        
        print(f"\nRESULTADO: {graficos_ok} visualizacoes geradas com sucesso")
        return graficos_ok > 0

def main():
    """Funcao principal para teste"""
    import glob
    
    print("VISUALIZADOR SIMPLES - TESTE")
    print("=" * 40)
    
    # Procurar arquivos JSON
    arquivos_json = glob.glob("*_basico.json") + glob.glob("relatorio_analise_*.json")
    
    if not arquivos_json:
        print("ERRO Nenhum arquivo JSON encontrado")
        return
    
    print(f"Encontrados {len(arquivos_json)} arquivo(s):")
    for arquivo in arquivos_json:
        print(f"  - {arquivo}")
    
    # Usar primeiro arquivo encontrado
    arquivo_escolhido = arquivos_json[0]
    print(f"\nUsando: {arquivo_escolhido}")
    
    # Testar visualizador
    visualizador = VisualizadorSimples()
    
    if visualizador.carregar_relatorio(arquivo_escolhido):
        resultado = visualizador.testar_visualizacoes()
        
        if resultado:
            print("\nSUCESSO! Visualizacoes geradas.")
            print("Arquivos criados:")
            print("  - frequencias_numeros_simples.png")
            print("  - correlacoes_simples.png")
            print("  - relatorio_simples_YYYYMMDD_HHMMSS.txt")
        else:
            print("\nFALHA ao gerar visualizacoes")
    else:
        print("\nFALHA ao carregar relatorio")

if __name__ == "__main__":
    main()
    input("\nPressione ENTER para continuar...")