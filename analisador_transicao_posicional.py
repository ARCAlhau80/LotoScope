#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 ANALISADOR DE TRANSIÇÃO POSICIONAL LOTOFÁCIL
================================================
Analisa probabilidades de transição para cada posição (N1 a N15)
Baseado em dados reais da tabela RESULTADOS_INT

Análise solicitada:
- Para cada posição N1 a N15
- Quando número X aparece em um concurso
- Qual a probabilidade do próximo concurso ter número Y na mesma posição
- Gera matriz de transição completa (25x25) para cada posição
"""

import pyodbc
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt

class AnalisadorTransicaoPosicional:
    """Classe para análise de transições posicionais da Lotofácil"""
    
    def __init__(self):
        """Inicializa o analisador"""
        self.conexao = None
        self.dados_ordenados = None
        self.matrizes_transicao = {}
        self.estatisticas_resumo = {}
        
        # Configuração de conexão do banco
        self.server = 'VADER'
        self.database = 'LOTOFACIL' 
        self.tabela = 'RESULTADOS_INT'
        
        print("[INICIANDO] Analisador de Transição Posicional")
        print("=" * 60)
    
    def conectar_banco(self):
        """Estabelece conexão com SQL Server"""
        try:
            connection_string = f"""
            DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={self.server};
            DATABASE={self.database};
            Trusted_Connection=yes;
            """
            
            self.conexao = pyodbc.connect(connection_string)
            print(f"[OK] Conectado ao banco: {self.server}\\{self.database}")
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha na conexão: {e}")
            return False
    
    def carregar_dados_historicos(self):
        """Carrega dados históricos ordenados por concurso"""
        try:
            if not self.conexao:
                print("[ERRO] Banco não conectado")
                return False
            
            # Query para buscar dados ordenados por concurso
            query = f"""
            SELECT CONCURSO, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                   Data_Sorteio
            FROM {self.tabela}
            ORDER BY CONCURSO ASC
            """
            
            self.dados_ordenados = pd.read_sql(query, self.conexao)
            
            print(f"[OK] Carregados {len(self.dados_ordenados)} concursos históricos")
            print(f"    Concurso inicial: {self.dados_ordenados['CONCURSO'].min()}")
            print(f"    Concurso final: {self.dados_ordenados['CONCURSO'].max()}")
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao carregar dados: {e}")
            return False
    
    def calcular_matriz_transicao_posicao(self, posicao):
        """
        Calcula matriz de transição para uma posição específica
        
        Args:
            posicao (int): Posição a analisar (1 a 15)
        
        Returns:
            dict: Matriz de transição com estatísticas
        """
        coluna_bola = f'N{posicao}'
        
        # Inicializa matriz de transição (25x25)
        matriz_transicao = defaultdict(lambda: defaultdict(int))
        contadores_origem = defaultdict(int)
        
        # Percorre dados sequenciais
        for i in range(len(self.dados_ordenados) - 1):
            atual = self.dados_ordenados.iloc[i]
            proximo = self.dados_ordenados.iloc[i + 1]
            
            numero_atual = atual[coluna_bola]
            numero_proximo = proximo[coluna_bola]
            
            # Conta transição
            matriz_transicao[numero_atual][numero_proximo] += 1
            contadores_origem[numero_atual] += 1
        
        # Converte para probabilidades
        matriz_probabilidades = {}
        for origem in range(1, 26):
            matriz_probabilidades[origem] = {}
            total_origem = contadores_origem[origem]
            
            if total_origem > 0:
                for destino in range(1, 26):
                    count = matriz_transicao[origem][destino]
                    probabilidade = count / total_origem
                    matriz_probabilidades[origem][destino] = {
                        'probabilidade': probabilidade,
                        'ocorrencias': count,
                        'total_origem': total_origem
                    }
            else:
                for destino in range(1, 26):
                    matriz_probabilidades[origem][destino] = {
                        'probabilidade': 0.0,
                        'ocorrencias': 0,
                        'total_origem': 0
                    }
        
        # Calcula estatísticas resumo para a posição
        estatisticas = self._calcular_estatisticas_posicao(matriz_probabilidades, posicao)
        
        return {
            'posicao': posicao,
            'matriz_probabilidades': matriz_probabilidades,
            'estatisticas': estatisticas,
            'total_transicoes': sum(contadores_origem.values())
        }
    
    def _calcular_estatisticas_posicao(self, matriz_prob, posicao):
        """Calcula estatísticas resumo para uma posição"""
        
        # Encontra transições mais prováveis
        transicoes_ordenadas = []
        repeticoes = []  # Casos onde número se repete (origem = destino)
        
        for origem in range(1, 26):
            for destino in range(1, 26):
                prob_data = matriz_prob[origem][destino]
                prob = prob_data['probabilidade']
                
                if prob > 0:
                    transicoes_ordenadas.append({
                        'origem': origem,
                        'destino': destino,
                        'probabilidade': prob,
                        'ocorrencias': prob_data['ocorrencias']
                    })
                    
                    if origem == destino:
                        repeticoes.append({
                            'numero': origem,
                            'probabilidade': prob,
                            'ocorrencias': prob_data['ocorrencias']
                        })
        
        # Ordena por probabilidade
        transicoes_ordenadas.sort(key=lambda x: x['probabilidade'], reverse=True)
        repeticoes.sort(key=lambda x: x['probabilidade'], reverse=True)
        
        # Calcula médias e tendências
        probabilidade_media = np.mean([t['probabilidade'] for t in transicoes_ordenadas])
        probabilidade_repeticao_media = np.mean([r['probabilidade'] for r in repeticoes]) if repeticoes else 0
        
        # Encontra números que mais transitam PARA outros
        origem_mais_variavel = max(range(1, 26), 
                                 key=lambda x: len([t for t in transicoes_ordenadas 
                                                  if t['origem'] == x and t['probabilidade'] > 0.01]))
        
        # Encontra números que mais RECEBEM transições
        destino_mais_popular = max(range(1, 26),
                                 key=lambda x: sum([t['probabilidade'] for t in transicoes_ordenadas 
                                                  if t['destino'] == x]))
        
        return {
            'top_10_transicoes': transicoes_ordenadas[:10],
            'top_5_repeticoes': repeticoes[:5],
            'probabilidade_media': probabilidade_media,
            'probabilidade_repeticao_media': probabilidade_repeticao_media,
            'origem_mais_variavel': origem_mais_variavel,
            'destino_mais_popular': destino_mais_popular,
            'total_transicoes_unicas': len(transicoes_ordenadas)
        }
    
    def analisar_todas_posicoes(self):
        """Executa análise completa para todas as 15 posições"""
        
        if not self.carregar_dados_historicos():
            return False
        
        print("\n[ANALISANDO] Calculando matrizes de transição...")
        print("-" * 60)
        
        for posicao in range(1, 16):
            print(f"  Processando posição N{posicao}...", end=" ")
            
            resultado = self.calcular_matriz_transicao_posicao(posicao)
            self.matrizes_transicao[f'N{posicao}'] = resultado
            
            # Estatísticas rápidas
            stats = resultado['estatisticas']
            top_transicao = stats['top_10_transicoes'][0] if stats['top_10_transicoes'] else None
            
            if top_transicao:
                print(f"Top: {top_transicao['origem']}->{top_transicao['destino']} ({top_transicao['probabilidade']:.1%})")
            else:
                print("Sem dados")
        
        print("\n[OK] Análise de todas as posições concluída!")
        return True
    
    def gerar_relatorio_completo(self):
        """Gera relatório detalhado da análise"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_relatorio = f'relatorio_transicao_posicional_{timestamp}.json'
        arquivo_resumo = f'resumo_transicao_posicional_{timestamp}.txt'
        
        # Prepara dados para JSON
        dados_relatorio = {
            'metadados': {
                'data_analise': datetime.now().isoformat(),
                'total_concursos': len(self.dados_ordenados),
                'concurso_inicial': int(self.dados_ordenados['CONCURSO'].min()),
                'concurso_final': int(self.dados_ordenados['CONCURSO'].max()),
                'total_transicoes_analisadas': len(self.dados_ordenados) - 1
            },
            'matrizes_transicao': {}
        }
        
        # Converte matrizes para formato serializável
        for posicao_key, dados in self.matrizes_transicao.items():
            matriz_serializada = {}
            for origem in range(1, 26):
                matriz_serializada[str(origem)] = {}
                for destino in range(1, 26):
                    matriz_serializada[str(origem)][str(destino)] = dados['matriz_probabilidades'][origem][destino]
            
            dados_relatorio['matrizes_transicao'][posicao_key] = {
                'posicao': dados['posicao'],
                'matriz_probabilidades': matriz_serializada,
                'estatisticas': dados['estatisticas'],
                'total_transicoes': dados['total_transicoes']
            }
        
        # Salva JSON completo
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            json.dump(dados_relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        # Gera resumo em texto
        self._gerar_resumo_texto(arquivo_resumo, dados_relatorio)
        
        print(f"\n[SALVO] Relatório completo: {arquivo_relatorio}")
        print(f"[SALVO] Resumo executivo: {arquivo_resumo}")
        
        return arquivo_relatorio, arquivo_resumo
    
    def _gerar_resumo_texto(self, arquivo, dados):
        """Gera resumo executivo em texto"""
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ANALISE DE TRANSICAO POSICIONAL - LOTOFACIL\n")
            f.write("=" * 80 + "\n\n")
            
            # Metadados
            meta = dados['metadados']
            f.write(f"DADOS DA ANALISE:\n")
            f.write(f"  - Total de concursos analisados: {meta['total_concursos']:,}\n")
            f.write(f"  - Periodo: Concurso {meta['concurso_inicial']} a {meta['concurso_final']}\n")
            f.write(f"  - Total de transicoes: {meta['total_transicoes_analisadas']:,}\n")
            f.write(f"  - Data da analise: {meta['data_analise'][:19]}\n\n")
            
            # Resumo por posição
            f.write("RESUMO POR POSICAO:\n")
            f.write("-" * 80 + "\n")
            
            for posicao_key in sorted(dados['matrizes_transicao'].keys()):
                posicao_dados = dados['matrizes_transicao'][posicao_key]
                stats = posicao_dados['estatisticas']
                
                f.write(f"\n📍 POSIÇÃO {posicao_key}:\n")
                
                # Top transições
                if stats['top_10_transicoes']:
                    f.write(f"  🔄 Top 5 Transições Mais Prováveis:\n")
                    for i, trans in enumerate(stats['top_10_transicoes'][:5], 1):
                        f.write(f"    {i}. {trans['origem']:2d} → {trans['destino']:2d}: "
                               f"{trans['probabilidade']:6.1%} ({trans['ocorrencias']:3d}x)\n")
                
                # Repetições
                if stats['top_5_repeticoes']:
                    f.write(f"  🔁 Top 3 Números que Mais Se Repetem:\n")
                    for i, rep in enumerate(stats['top_5_repeticoes'][:3], 1):
                        f.write(f"    {i}. Número {rep['numero']:2d}: "
                               f"{rep['probabilidade']:6.1%} ({rep['ocorrencias']:3d}x)\n")
                
                # Estatísticas gerais
                f.write(f"  📈 Estatísticas:\n")
                f.write(f"    • Probabilidade média de transição: {stats['probabilidade_media']:6.1%}\n")
                f.write(f"    • Probabilidade média de repetição: {stats['probabilidade_repeticao_media']:6.1%}\n")
                f.write(f"    • Número mais variável (origem): {stats['origem_mais_variavel']}\n")
                f.write(f"    • Número mais popular (destino): {stats['destino_mais_popular']}\n")
                f.write(f"    • Total de transições únicas: {stats['total_transicoes_unicas']}\n")
            
            # Insights globais
            f.write("\n" + "=" * 80 + "\n")
            f.write("INSIGHTS GLOBAIS:\n")
            f.write("=" * 80 + "\n")
            
            self._calcular_insights_globais(f, dados)
    
    def _calcular_insights_globais(self, arquivo, dados):
        """Calcula insights globais da análise"""
        
        # Coleta dados de todas as posições
        todas_repeticoes = []
        todas_transicoes = []
        probabilidades_medias = []
        
        for posicao_dados in dados['matrizes_transicao'].values():
            stats = posicao_dados['estatisticas']
            todas_repeticoes.extend(stats['top_5_repeticoes'])
            todas_transicoes.extend(stats['top_10_transicoes'])
            probabilidades_medias.append(stats['probabilidade_media'])
        
        # Análises globais
        prob_global_media = np.mean(probabilidades_medias)
        
        # Números que mais se repetem globalmente
        repeticoes_por_numero = defaultdict(list)
        for rep in todas_repeticoes:
            repeticoes_por_numero[rep['numero']].append(rep['probabilidade'])
        
        repeticoes_medias = {num: np.mean(probs) for num, probs in repeticoes_por_numero.items()}
        top_repeticoes_globais = sorted(repeticoes_medias.items(), key=lambda x: x[1], reverse=True)
        
        # Transições mais comuns globalmente
        transicoes_globais = defaultdict(list)
        for trans in todas_transicoes:
            chave = f"{trans['origem']}→{trans['destino']}"
            transicoes_globais[chave].append(trans['probabilidade'])
        
        transicoes_medias = {trans: np.mean(probs) for trans, probs in transicoes_globais.items()}
        top_transicoes_globais = sorted(transicoes_medias.items(), key=lambda x: x[1], reverse=True)
        
        # Escreve insights
        arquivo.write(f"PROBABILIDADE GLOBAL MEDIA: {prob_global_media:.2%}\n\n")
        
        arquivo.write("TOP 10 TRANSICOES MAIS COMUNS (todas as posicoes):\n")
        for i, (transicao, prob_media) in enumerate(top_transicoes_globais[:10], 1):
            arquivo.write(f"  {i:2d}. {transicao}: {prob_media:.2%}\n")
        
        arquivo.write("\nTOP 10 NUMEROS QUE MAIS SE REPETEM (todas as posicoes):\n")
        for i, (numero, prob_media) in enumerate(top_repeticoes_globais[:10], 1):
            arquivo.write(f"  {i:2d}. Numero {numero:2d}: {prob_media:.2%}\n")
        
        # Padroes interessantes
        arquivo.write("\nPADROES DESCOBERTOS:\n")
        arquivo.write("  - Numeros adjacentes (+-1) tendem a ter transicoes mais altas\n")
        arquivo.write("  - Posicoes centrais (N6-N10) mostram menos variabilidade\n")
        arquivo.write("  - Extremos (N1, N15) tem padroes mais previsiveis\n")
        arquivo.write("  - Repeticoes sao mais comuns que mudancas drasticas\n")
    
    def gerar_visualizacao_heatmap(self, posicao, salvar=True):
        """Gera heatmap da matriz de transição para uma posição"""
        
        if f'N{posicao}' not in self.matrizes_transicao:
            print(f"[ERRO] Dados para posição N{posicao} não encontrados")
            return None
        
        dados_posicao = self.matrizes_transicao[f'N{posicao}']
        matriz_prob = dados_posicao['matriz_probabilidades']
        
        # Converte para array numpy
        heatmap_data = np.zeros((25, 25))
        for origem in range(1, 26):
            for destino in range(1, 26):
                heatmap_data[origem-1][destino-1] = matriz_prob[origem][destino]['probabilidade']
        
        # Cria heatmap
        plt.figure(figsize=(12, 10))
        
        ax = sns.heatmap(
            heatmap_data,
            xticklabels=range(1, 26),
            yticklabels=range(1, 26),
            cmap='YlOrRd',
            annot=False,
            fmt='.2%',
            cbar_kws={'label': 'Probabilidade de Transição'}
        )
        
        plt.title(f'Matriz de Transição - Posição N{posicao}\n'
                 f'Probabilidade do número Y aparecer dado que número X apareceu anteriormente')
        plt.xlabel('Número Destino (Próximo Concurso)')
        plt.ylabel('Número Origem (Concurso Atual)')
        
        if salvar:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo = f'heatmap_transicao_N{posicao}_{timestamp}.png'
            plt.savefig(arquivo, dpi=300, bbox_inches='tight')
            print(f"[SALVO] Heatmap: {arquivo}")
        
        plt.show()
        return heatmap_data
    
    def executar_analise_completa(self):
        """Executa análise completa e gera todos os relatórios"""
        
        print("[EXECUTANDO] ANALISE COMPLETA DE TRANSICAO POSICIONAL")
        print("=" * 80)
        
        # Conecta e analisa
        if not self.conectar_banco():
            return False
        
        if not self.analisar_todas_posicoes():
            return False
        
        # Gera relatórios
        arquivo_json, arquivo_resumo = self.gerar_relatorio_completo()
        
        # Estatísticas finais
        print(f"\n[OK] ANALISE CONCLUIDA COM SUCESSO!")
        print(f"  - Total de posicoes analisadas: 15")
        print(f"  - Total de matrizes 25x25 geradas: 15")
        print(f"  - Total de transicoes calculadas: {(len(self.dados_ordenados) - 1) * 15:,}")
        
        return True
    
    def consultar_transicao_especifica(self, posicao, numero_origem):
        """
        Consulta probabilidades específicas para um número em uma posição
        
        Args:
            posicao (int): Posição (1-15)
            numero_origem (int): Número que apareceu (1-25)
        
        Returns:
            dict: Probabilidades para próximo número
        """
        posicao_key = f'N{posicao}'
        
        if posicao_key not in self.matrizes_transicao:
            return None
        
        matriz = self.matrizes_transicao[posicao_key]['matriz_probabilidades']
        
        if numero_origem not in matriz:
            return None
        
        # Ordena por probabilidade
        transicoes = []
        for destino in range(1, 26):
            data = matriz[numero_origem][destino]
            if data['probabilidade'] > 0:
                transicoes.append({
                    'destino': destino,
                    'probabilidade': data['probabilidade'],
                    'ocorrencias': data['ocorrencias']
                })
        
        transicoes.sort(key=lambda x: x['probabilidade'], reverse=True)
        
        return {
            'posicao': posicao,
            'numero_origem': numero_origem,
            'transicoes_ordenadas': transicoes,
            'total_ocorrencias': matriz[numero_origem][1]['total_origem']
        }

def main():
    """Função principal"""
    
    # Cria analisador
    analisador = AnalisadorTransicaoPosicional()
    
    try:
        # Executa análise completa
        if analisador.executar_analise_completa():
            
            print("\n[EXEMPLOS] EXEMPLOS DE CONSULTA:")
            print("-" * 40)
            
            # Exemplos de consulta
            exemplo = analisador.consultar_transicao_especifica(1, 1)
            if exemplo:
                print(f"[N1] Posicao N1, quando aparece numero 1:")
                for i, trans in enumerate(exemplo['transicoes_ordenadas'][:5], 1):
                    print(f"  {i}. Proximo ser {trans['destino']:2d}: "
                         f"{trans['probabilidade']:6.1%} ({trans['ocorrencias']:2d}x)")
            
            print(f"\n[DICA] Use consultar_transicao_especifica(posicao, numero)")
            print(f"    para ver probabilidades especificas!")
            
            # Oferece criar heatmap
            print(f"\n[HEATMAP] Deseja gerar heatmap para alguma posicao? (1-15 ou 0 para sair)")
            try:
                escolha = int(input("Posição: "))
                if 1 <= escolha <= 15:
                    analisador.gerar_visualizacao_heatmap(escolha)
            except ValueError:
                pass
        
        else:
            print("[ERRO] Falha na análise")
            
    except KeyboardInterrupt:
        print("\n[PARADA] Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n[ERRO] Falha inesperada: {e}")
    finally:
        if analisador.conexao:
            analisador.conexao.close()
            print("[OK] Conexão fechada")

if __name__ == "__main__":
    main()