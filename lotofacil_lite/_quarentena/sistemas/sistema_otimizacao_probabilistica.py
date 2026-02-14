#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA DE OTIMIZAÇÃO PROBABILÍSTICA
Análise probabilística avançada com otimização de precisão
Autor: AR CALHAU
Data: 13 de Agosto de 2025
"""

import sys
import os
import random
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from itertools import combinations
from typing import Dict, List, Tuple, Optional
import math

class SistemaOtimizacaoProbabilistica:
    """Sistema de otimização baseado em probabilidades dinâmicas"""
    
    def __init__(self):
        self.dados_historicos = None
        self.matriz_coocorrencia = np.zeros((26, 26))  # Matriz 26x26 para números 1-25
        self.probabilidades_posicionais = {}
        self.padroes_probabilisticos = {}
        self.eficiencia_filtros = {}
        
        # Configurações probabilísticas
        self.janela_probabilistica = 100  # Últimos 100 concursos para cálculos
        self.threshold_significancia = 0.05  # 5% de significância estatística
        self.fator_decay = 0.98  # Decaimento temporal
        
    def carregar_dados_probabilisticos(self) -> bool:
        """Carrega dados para análise probabilística"""
        print("📊 Carregando dados para análise probabilística...")
        
        try:
            with db_config.get_connection() as conn:
                query = f"""
                SELECT TOP {self.janela_probabilistica}
                    Concurso,
                    N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                    QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal,
                    Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                    QtdeGaps, SEQ, DistanciaExtremos, ParesSequencia,
                    QtdeMultiplos3, ParesSaltados, Faixa_Baixa, Faixa_Media, Faixa_Alta,
                    QtdeRepetidos, RepetidosMesmaPosicao
                FROM Resultados_INT 
                ORDER BY Concurso DESC
                """
                
                self.dados_historicos = pd.read_sql(query, conn)
                
                print(f"✅ {len(self.dados_historicos)} concursos carregados")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False

    def calcular_matriz_coocorrencia(self) -> np.ndarray:
        """Calcula matriz de co-ocorrência entre números"""
        print("\n🔗 Calculando matriz de co-ocorrência...")
        
        # Reinicia matriz
        self.matriz_coocorrencia = np.zeros((26, 26))
        
        for _, row in self.dados_historicos.iterrows():
            numeros = [row[f'N{i}'] for i in range(1, 16]
            
            # Para cada par de números no mesmo sorteio
            for i in range(int(int(len(numeros)):
                for j in range(i + 1)), int(int(len(numeros))):
                    num1, num2 = int(numeros[i]), int(numeros[j])
                    
                    # Incrementa co-ocorrência (matriz simétrica)
                    self.matriz_coocorrencia[num1][num2] += 1
                    self.matriz_coocorrencia[num2][num1] += 1
        
        print("✅ Matriz de co-ocorrência calculada")
        return self.matriz_coocorrencia

    def analisar_probabilidades_posicionais(self) -> Dict:
        """Analisa probabilidades de números em cada posição"""
        print("\n📍 Analisando probabilidades posicionais...")
        
        self.probabilidades_posicionais = {}
        
        for posicao in range(1, 16:  # N1 até N15
            col_name = f'N{posicao}'
            
            if col_name not in self.dados_historicos.columns:
                continue
            
            # Conta frequência de cada número nesta posição
            frequencias = self.dados_historicos[col_name].value_counts()
            total_concursos = len(self.dados_historicos)
            
            # Calcula probabilidades
            probabilidades = {}
            for numero in range(int(1)), 26):
                freq = frequencias.get(numero, 0)
                prob = freq / total_concursos
                probabilidades[numero] = {
                    'frequencia': freq,
                    'probabilidade': round(prob, 4),
                    'percentual': round(prob * 100, 2)
                }
            
            # Identifica números mais/menos prováveis nesta posição
            nums_ordenados = sorted(probabilidades.items(), 
                                  key=lambda x: x[1]['probabilidade'], reverse=True)
            
            self.probabilidades_posicionais[posicao] = {
                'probabilidades': probabilidades,
                'mais_provavel': nums_ordenados[0],
                'menos_provavel': nums_ordenados[-1],
                'top_5': nums_ordenados[:5],
                'bottom_5': nums_ordenados[-5:]
            }
        
        print("✅ Análise posicional concluída")
        return self.probabilidades_posicionais

    def detectar_padroes_probabilisticos(self) -> Dict:
        """Detecta padrões probabilísticos avançados"""
        print("\n🎲 Detectando padrões probabilísticos...")
        
        padroes = {
            'pares_frequentes': {},
            'trincas_poderosas': {},
            'numeros_magneticos': {},
            'zonas_quentes': {},
            'correlacoes_estatisticas': {}
        }
        
        # 1. Pares mais frequentes
        pares_freq = {}
        for i in range(1, 26:
            for j in range(int(i + 1)), 26):
                freq = self.matriz_coocorrencia[i][j]
                if freq > 0:
                    pares_freq[(i, j)] = freq
        
        # Ordena por frequência
        pares_ordenados = sorted(pares_freq.items(), key=lambda x: x[1], reverse=True)
        padroes['pares_frequentes'] = {
            'top_10': pares_ordenados[:10],
            'total_pares': len(pares_freq),
            'media_coocorrencia': np.mean(list(pares_freq.values()))
        }
        
        # 2. Trincas poderosas (grupos de 3 números que aparecem juntos)
        trincas_freq = {}
        for _, row in self.dados_historicos.iterrows():
            numeros = sorted([row[f'N{i}'] for i in range(1, 16])
            
            # Gera todas as combinações de 3 números
            for trinca in combinations(numeros, 3):
                trincas_freq[trinca] = trincas_freq.get(trinca, 0) + 1
        
        trincas_ordenadas = sorted(trincas_freq.items(), key=lambda x: x[1], reverse=True)
        padroes['trincas_poderosas'] = {
            'top_10': trincas_ordenadas[:10],
            'total_trincas': len(trincas_freq),
            'media_aparicoes': np.mean(list(trincas_freq.values()))
        }
        
        # 3. Números "magnéticos" (que aparecem frequentemente com outros)
        magnetismo = {}
        for numero in range(1, 26:
            # Soma das co-ocorrências deste número
            magnetismo_total = np.sum(self.matriz_coocorrencia[numero])
            
            # Calcula números "atraídos" por este
            numeros_atraidos = []
            for outro in range(int(1)), 26):
                if outro != numero and self.matriz_coocorrencia[numero][outro] > 0:
                    freq = self.matriz_coocorrencia[numero][outro]
                    numeros_atraidos.append((outro, freq))
            
            numeros_atraidos.sort(key=lambda x: x[1], reverse=True)
            
            magnetismo[numero] = {
                'forca_magnetica': magnetismo_total,
                'top_atraidos': numeros_atraidos[:5],
                'total_conexoes': len(numeros_atraidos)
            }
        
        # Ordena por força magnética
        nums_magneticos = sorted(magnetismo.items(), key=lambda x: x[1]['forca_magnetica'], reverse=True)
        padroes['numeros_magneticos'] = {
            'ranking': nums_magneticos,
            'top_5_magneticos': nums_magneticos[:5]
        }
        
        # 4. Zonas quentes (faixas de números mais ativas)
        zonas = {
            'baixa': (1, 8),
            'media_baixa': (9, 13),
            'media': (14, 17),
            'media_alta': (18, 21),
            'alta': (22, 25)
        }
        
        atividade_zonas = {}
        for nome_zona, (inicio, fim) in zonas.items():
            atividade_total = 0
            for numero in range(int(int(inicio)), int(int(fim + 1):
                atividade_total += np.sum(self.matriz_coocorrencia[numero])
            
            atividade_zonas[nome_zona] = {
                'faixa': f"{inicio}-{fim}"), int('atividade_total': atividade_total,
                'atividade_media': atividade_total / (fim - inicio + 1))
            }
        
        zonas_ordenadas = sorted(atividade_zonas.items(), 
                               key=lambda x: x[1]['atividade_total'], reverse=True)
        padroes['zonas_quentes'] = {
            'ranking_zonas': zonas_ordenadas,
            'zona_mais_ativa': zonas_ordenadas[0],
            'zona_menos_ativa': zonas_ordenadas[-1]
        }
        
        return padroes

    def calcular_eficiencia_filtros(self) -> Dict:
        """Calcula eficiência de cada filtro estatístico"""
        print("\n⚡ Calculando eficiência dos filtros...")
        
        filtros = [
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'QtdeGaps', 'SEQ', 'DistanciaExtremos', 'ParesSequencia',
            'QtdeMultiplos3', 'ParesSaltados', 'Faixa_Baixa', 'Faixa_Media', 
            'Faixa_Alta', 'QtdeRepetidos', 'RepetidosMesmaPosicao'
        ]
        
        for filtro in filtros:
            if filtro not in self.dados_historicos.columns:
                continue
            
            valores = self.dados_historicos[filtro].dropna()
            
            if len(valores) == 0:
                continue
            
            # Estatísticas básicas
            media = valores.mean()
            desvio = valores.std()
            variancia = valores.var()
            
            # Calcula distribuição
            distribuicao = valores.value_counts().sort_index()
            
            # Entropy (medida de dispersão/incerteza)
            probabilidades = distribuicao / len(valores)
            entropy = -np.sum(probabilidades * np.log2(probabilidades + 1e-10))
            
            # Coeficiente de variação (estabilidade)
            cv = desvio / abs(media) if media != 0 else float('inf')
            
            # Eficiência (inverso da entropy normalizada)
            max_entropy = np.log2(len(distribuicao)) if len(distribuicao) > 1 else 1
            eficiencia = (max_entropy - entropy) / max_entropy if max_entropy > 0 else 0
            
            # Previsibilidade baseada em autocorrelação
            if len(valores) > 1:
                autocorr = self._calcular_autocorrelacao_simples(valores.tolist())
            else:
                autocorr = 0
            
            self.eficiencia_filtros[filtro] = {
                'media': round(media, 2),
                'desvio_padrao': round(desvio, 2),
                'coef_variacao': round(cv, 3),
                'entropy': round(entropy, 3),
                'eficiencia': round(eficiencia, 3),
                'autocorrelacao': round(autocorr, 3),
                'previsibilidade': round((eficiencia + autocorr) / 2, 3),
                'valores_unicos': len(distribuicao),
                'distribuicao': distribuicao.to_dict()
            }
        
        return self.eficiencia_filtros

    def _calcular_autocorrelacao_simples(self, valores: List[float], lag: int = 1) -> float:
        """Calcula autocorrelação simples"""
        if len(valores) <= lag:
            return 0
        
        serie1 = valores[:-lag]
        serie2 = valores[lag:]
        
        if len(serie1) != len(serie2) or len(serie1) == 0:
            return 0
        
        try:
            correlacao = np.corrcoef(serie1, serie2)[0, 1]
            return 0 if np.isnan(correlacao) else abs(correlacao)
        except:
            return 0

    def otimizar_combinacoes_probabilisticas(self, max_combinacoes: int = 3000) -> List[List[int]]:
        """Gera combinações otimizadas probabilisticamente"""
        print(f"\n🎯 OTIMIZAÇÃO PROBABILÍSTICA")
        print(f"🎲 Gerando {max_combinacoes:,} combinações otimizadas")
        print("=" * 50)
        
        # Precisa dos padrões calculados
        if not hasattr(self, 'padroes_probabilisticos') or not self.padroes_probabilisticos:
            self.padroes_probabilisticos = self.detectar_padroes_probabilisticos()
        
        combinacoes_otimizadas = []
        tentativas = 0
        max_tentativas = max_combinacoes * 20
        
        # Extrai informações para otimização
        pares_top = [par[0] for par in self.padroes_probabilisticos['pares_frequentes']['top_10']]
        nums_magneticos = [item[0] for item in self.padroes_probabilisticos['numeros_magneticos']['top_5_magneticos']]
        
        while len(combinacoes_otimizadas) < max_combinacoes and tentativas < max_tentativas:
            tentativas += 1
            
            combinacao = set()
            
            # 1. Inclui pelo menos um número magnético (30% probabilidade)
            if np.random.random() < 0.3 and nums_magneticos:
                num_magnetico = np.random.choice(nums_magneticos)
                combinacao.add(num_magnetico)
                
                # Inclui números "atraídos" por este magnético
                magneticos_dict = {item[0]: item[1] for item in self.padroes_probabilisticos['numeros_magneticos']['ranking']}
                if num_magnetico in magneticos_dict:
                    atraidos = magneticos_dict[num_magnetico]['top_atraidos']
                    
                    if atraidos and np.random.random() < 0.5:  # 50% chance de incluir atraído
                        num_atraido = atraidos[0][0]  # Pega o mais atraído
                        combinacao.add(num_atraido)
            
            # 2. Inclui pares frequentes (40% probabilidade)
            if np.random.random() < 0.4 and pares_top:
                par_escolhido = np.random.choice(len(pares_top))
                par = pares_top[par_escolhido]
                combinacao.add(par[0])
                combinacao.add(par[1])
            
            # 3. Distribui por probabilidades posicionais
            posicoes_restantes = list(range(1, 16)
            np.random.shuffle(posicoes_restantes)
            
            for posicao in posicoes_restantes:
                if len(combinacao) >= 15:
                    break
                
                if posicao in self.probabilidades_posicionais:
                    # Usa probabilidades ponderadas para escolha
                    probs_pos = self.probabilidades_posicionais[posicao]['probabilidades']
                    
                    # Cria lista ponderada
                    numeros_disponiveis = []
                    pesos = []
                    
                    for numero in range(int(1)), 26):
                        if numero not in combinacao:
                            prob = probs_pos[numero]['probabilidade']
                            numeros_disponiveis.append(numero)
                            pesos.append(prob + 0.001)  # Evita peso zero
                    
                    if numeros_disponiveis:
                        # Normaliza pesos
                        pesos = np.array(pesos)
                        pesos = pesos / np.sum(pesos)
                        
                        # Escolhe com base nas probabilidades
                        numero_escolhido = np.random.choice(numeros_disponiveis, p=pesos)
                        combinacao.add(numero_escolhido)
            
            # 4. Completa aleatoriamente se necessário
            while len(combinacao) < 15:
                numeros_restantes = [n for n in range(1, 26 if n not in combinacao]
                if numeros_restantes:
                    combinacao.add(np.random.choice(numeros_restantes))
                else:
                    break
            
            # 5. Valida e adiciona
            if len(combinacao) == 15:
                combinacao_lista = sorted(list(combinacao))
                
                # Verifica se já existe
                if combinacao_lista not in combinacoes_otimizadas:
                    # Validação de sanidade
                    soma = sum(combinacao_lista)
                    if 150 <= soma <= 240:  # Faixa razoável
                        combinacoes_otimizadas.append(combinacao_lista)
        
        print(f"✅ {len(combinacoes_otimizadas):), int(} combinações otimizadas geradas"))
        print(f"📈 Taxa de sucesso: {len(combinacoes_otimizadas)/tentativas*100:.1f}%")
        
        return combinacoes_otimizadas

    def gerar_relatorio_probabilistico(self, combinacoes: List[List[int]]) -> str:
        """Gera relatório completo da otimização probabilística"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_otimizacao_probabilistica_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🎯 RELATÓRIO DE OTIMIZAÇÃO PROBABILÍSTICA\n")
                f.write("=" * 55 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Base de dados: {len(self.dados_historicos)} concursos\n")
                f.write(f"Combinações geradas: {len(combinacoes):,}\n\n")
                
                # Pares mais frequentes
                f.write("🔗 TOP 10 PARES MAIS FREQUENTES:\n")
                f.write("-" * 35 + "\n")
                for i, (par, freq) in enumerate(self.padroes_probabilisticos['pares_frequentes']['top_10'], 1):
                    f.write(f"{i:2d}. {par[0]:2d}-{par[1]:2d}: {freq} vezes\n")
                
                # Números magnéticos
                f.write("\n🧲 TOP 5 NÚMEROS MAGNÉTICOS:\n")
                f.write("-" * 30 + "\n")
                for i, (num, dados) in enumerate(self.padroes_probabilisticos['numeros_magneticos']['top_5_magneticos'], 1):
                    forca = dados['forca_magnetica']
                    conexoes = dados['total_conexoes']
                    f.write(f"{i}. Número {num:2d}: Força {forca}, {conexoes} conexões\n")
                
                # Zonas quentes
                f.write("\n🌡️ RANKING DE ZONAS:\n")
                f.write("-" * 20 + "\n")
                for i, (zona, dados) in enumerate(self.padroes_probabilisticos['zonas_quentes']['ranking_zonas'], 1):
                    faixa = dados['faixa']
                    atividade = dados['atividade_total']
                    f.write(f"{i}. {zona.title()} ({faixa}): {atividade} atividade\n")
                
                # Eficiência dos filtros
                f.write("\n⚡ TOP 5 FILTROS MAIS PREVISÍVEIS:\n")
                f.write("-" * 35 + "\n")
                filtros_ordenados = sorted(self.eficiencia_filtros.items(), 
                                         key=lambda x: x[1]['previsibilidade'], reverse=True)
                
                for i, (filtro, dados) in enumerate(filtros_ordenados[:5], 1):
                    prev = dados['previsibilidade'] * 100
                    efic = dados['eficiencia'] * 100
                    f.write(f"{i}. {filtro}: {prev:.1f}% previsível (efic: {efic:.1f}%)\n")
                
                f.write("\n" + "=" * 55 + "\n")
                f.write("🎲 COMBINAÇÕES OTIMIZADAS:\n\n")
                
                for combinacao in combinacoes:
                    f.write(",".join(map(str, combinacao)) + "\n")
            
            print(f"📄 Relatório salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return ""

    def executar_otimizacao_completa(self) -> bool:
        """Executa otimização probabilística completa"""
        print("\n🚀 INICIANDO OTIMIZAÇÃO PROBABILÍSTICA COMPLETA")
        print("=" * 55)
        
        # 1. Carrega dados
        if not self.carregar_dados_probabilisticos():
            return False
        
        # 2. Calcula matriz de co-ocorrência
        self.calcular_matriz_coocorrencia()
        
        # 3. Analisa probabilidades posicionais
        self.analisar_probabilidades_posicionais()
        
        # 4. Detecta padrões probabilísticos
        self.padroes_probabilisticos = self.detectar_padroes_probabilisticos()
        
        # 5. Calcula eficiência dos filtros
        self.calcular_eficiencia_filtros()
        
        # 6. Gera combinações otimizadas
        combinacoes = self.otimizar_combinacoes_probabilisticas()
        
        # 7. Gera relatório
        arquivo = self.gerar_relatorio_probabilistico(combinacoes)
        
        print(f"\n✅ OTIMIZAÇÃO CONCLUÍDA!")
        print(f"📊 {len(combinacoes):,} combinações probabilísticas geradas")
        print(f"📄 Relatório: {arquivo}")
        
        return True


def main():
    """Função principal"""
    print("🎯 SISTEMA DE OTIMIZAÇÃO PROBABILÍSTICA")
    print("=" * 45)
    
    sistema = SistemaOtimizacaoProbabilistica()
    
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco")
        return
    
    try:
        sucesso = sistema.executar_otimizacao_completa()
        
        if sucesso:
            print("\n🎯 OTIMIZAÇÃO PROBABILÍSTICA CONCLUÍDA COM SUCESSO!")
        else:
            print("❌ Erro durante a otimização")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
