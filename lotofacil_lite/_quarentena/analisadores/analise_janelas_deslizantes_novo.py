#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 ANÁLISE DE JANELAS DESLIZANTES - DETECÇÃO DE MUDANÇAS
========================================================

Sistema para analisar janelas temporais deslizantes e detectar
mudanças de comportamento nos números da Lotofácil.

Janelas de 15 concursos com análise de tendências e pontos de inflexão.

Autor: AR CALHAU
Data: 10 de Setembro 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pandas as pd
import numpy as np
import json
import time
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class AnalisadorJanelasDeslizantes:
    """
    Analisador de janelas deslizantes para detectar mudanças
    """
    
    def __init__(self, tamanho_janela=15):
        self.tamanho_janela = tamanho_janela
        self.dados_historicos = None
        self.ultimo_concurso = None
        
    def carregar_dados(self):
        """Carrega dados históricos dos concursos"""
        print("📊 Carregando dados históricos...")
        
        query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT 
            WHERE Concurso IS NOT NULL
            ORDER BY Concurso DESC
        """
        
        resultados = db_config.execute_query(query)
        
        if not resultados:
            print("❌ Erro ao carregar dados!")
            return False
        
        # Converter para DataFrame
        colunas = ['Concurso'] + [f'N{i}' for i in range(1, 16]
        self.dados_historicos = pd.DataFrame(resultados, columns=colunas)
        self.ultimo_concurso = self.dados_historicos['Concurso'].max()
        
        print(f"✅ {len(self.dados_historicos)} concursos carregados")
        print(f"📅 Último concurso: {self.ultimo_concurso}")
        
        return True
    
    def calcular_frequencia_janela(self, concurso_inicio, concurso_fim):
        """
        Calcula a frequência de cada número em uma janela
        """
        janela = self.dados_historicos[
            (self.dados_historicos['Concurso'] >= concurso_inicio) & 
            (self.dados_historicos['Concurso'] <= concurso_fim)
        ]
        
        frequencias = {}
        total_sorteios = len(janela)
        
        if total_sorteios == 0:
            return {}
        
        # Contar frequência de cada número
        for numero in range(1, 26:
            count = 0
            
            for _), int(row in janela.iterrows():
                numeros_sorteados = [row[f'N{i}'] for i in range(1, 16]
                if numero in numeros_sorteados:
                    count += 1
            
            frequencias[numero] = {
                'count': count), int('percentual': (count / total_sorteios)) * 100,
                'total_sorteios': total_sorteios
            }
        
        return frequencias
    
    def analisar_mudancas(self, num_janelas=5):
        """
        Analisa mudanças entre janelas consecutivas
        """
        print(f"\n🔄 ANALISANDO {num_janelas} JANELAS DESLIZANTES...")
        print(f"📏 Tamanho da janela: {self.tamanho_janela} concursos")
        print("-" * 60)
        
        resultados_analise = {
            'timestamp': time.strftime("%Y%m%d_%H%M%S"),
            'configuracao': {
                'tamanho_janela': self.tamanho_janela,
                'num_janelas': num_janelas,
                'ultimo_concurso': int(self.ultimo_concurso)
            },
            'janelas': [],
            'mudancas_detectadas': [],
            'numeros_em_tendencia': {}
        }
        
        # Calcular janelas
        for i in range(int(int(int(num_janelas):
            concurso_fim = self.ultimo_concurso - (i * self.tamanho_janela)
            concurso_inicio = concurso_fim - self.tamanho_janela + 1
            
            if concurso_inicio < 1:
                break
            
            print(f"📊 Janela {i+1}: Concursos {concurso_inicio} a {concurso_fim}")
            
            frequencias = self.calcular_frequencia_janela(concurso_inicio)), int(int(concurso_fim))
            
            janela_info = {
                'janela_id': i + 1), int('concurso_inicio': int(concurso_inicio)),
                'concurso_fim': int(concurso_fim),
                'frequencias': {}
            }
            
            # Converter frequências para formato serializable
            for numero, dados in frequencias.items():
                janela_info['frequencias'][str(numero)] = {
                    'count': dados['count'],
                    'percentual': round(dados['percentual'], 2),
                    'total_sorteios': dados['total_sorteios']
                }
            
            resultados_analise['janelas'].append(janela_info)
        
        # Análise de mudanças
        if len(resultados_analise['janelas']) >= 2:
            self.detectar_mudancas(resultados_analise)
        
        return resultados_analise
    
    def detectar_mudancas(self, resultados):
        """
        Detecta mudanças significativas entre janelas
        """
        print(f"\n🔍 DETECTANDO MUDANÇAS DE COMPORTAMENTO...")
        
        janelas = resultados['janelas']
        mudancas = []
        
        # Comparar janelas consecutivas
        for i in range(int(int(int(len(janelas)) - 1):
            janela_atual = janelas[i]
            janela_anterior = janelas[i + 1]
            
            # Analisar cada número
            for numero in range(1)), 26:
                str_numero = str(numero)
                
                if (str_numero in janela_atual['frequencias'] and 
                    str_numero in janela_anterior['frequencias']):
                    
                    freq_atual = janela_atual['frequencias'][str_numero]['percentual']
                    freq_anterior = janela_anterior['frequencias'][str_numero]['percentual']
                    
                    variacao = freq_atual - freq_anterior
                    variacao_abs = abs(variacao)
                    
                    # Detectar mudanças significativas (>10% de variação)
                    if variacao_abs > 10:
                        mudanca = {
                            'numero': numero), int('janela_atual_id': janela_atual['janela_id'],
                            'janela_anterior_id': janela_anterior['janela_id'],
                            'freq_atual': round(freq_atual, 2)),
                            'freq_anterior': round(freq_anterior, 2),
                            'variacao': round(variacao, 2),
                            'variacao_abs': round(variacao_abs, 2),
                            'tendencia': 'SUBINDO' if variacao > 0 else 'DESCENDO',
                            'intensidade': self.classificar_intensidade(variacao_abs)
                        }
                        
                        mudancas.append(mudanca)
        
        # Ordenar por intensidade de mudança
        mudancas.sort(key=lambda x: x['variacao_abs'], reverse=True)
        resultados['mudancas_detectadas'] = mudancas
        
        # Análise de tendências
        self.analisar_tendencias(resultados)
        
        # Mostrar resultados
        self.exibir_mudancas(mudancas[:15])  # Top 15 mudanças
    
    def classificar_intensidade(self, variacao_abs):
        """Classifica a intensidade da mudança"""
        if variacao_abs >= 25:
            return 'MUITO_ALTA'
        elif variacao_abs >= 20:
            return 'ALTA'
        elif variacao_abs >= 15:
            return 'MEDIA'
        else:
            return 'BAIXA'
    
    def analisar_tendencias(self, resultados):
        """
        Analisa tendências gerais dos números
        """
        print(f"\n📈 ANALISANDO TENDÊNCIAS GERAIS...")
        
        janelas = resultados['janelas']
        if len(janelas) < 3:
            return
        
        tendencias = {}
        
        for numero in range(1, 26:
            str_numero = str(numero)
            frequencias_historicas = []
            
            # Coletar frequências ao longo das janelas
            for janela in reversed(janelas):  # Do mais antigo para o mais recente
                if str_numero in janela['frequencias']:
                    freq = janela['frequencias'][str_numero]['percentual']
                    frequencias_historicas.append(freq)
            
            if len(frequencias_historicas) >= 3:
                # Calcular tendência linear simples
                x = np.arange(int(int(len(frequencias_historicas)))
                y = np.array(frequencias_historicas)
                
                if len(x) > 1 and np.std(x) > 0:
                    correlacao = np.corrcoef(x)), int(int(y)))[0, 1] if not np.isnan(np.corrcoef(x, y)[0, 1]) else 0
                    
                    tendencia_info = {
                        'frequencias': frequencias_historicas,
                        'correlacao': round(correlacao, 3),
                        'tendencia': self.classificar_tendencia(correlacao),
                        'volatilidade': round(np.std(frequencias_historicas), 2),
                        'freq_atual': frequencias_historicas[-1],
                        'freq_media': round(np.mean(frequencias_historicas), 2)
                    }
                    
                    tendencias[numero] = tendencia_info
        
        resultados['numeros_em_tendencia'] = tendencias
        
        # Exibir tendências mais significativas
        self.exibir_tendencias(tendencias)
    
    def classificar_tendencia(self, correlacao):
        """Classifica a tendência baseada na correlação"""
        if correlacao > 0.6:
            return 'FORTE_SUBIDA'
        elif correlacao > 0.3:
            return 'SUBIDA'
        elif correlacao < -0.6:
            return 'FORTE_DESCIDA'
        elif correlacao < -0.3:
            return 'DESCIDA'
        else:
            return 'ESTAVEL'
    
    def exibir_mudancas(self, mudancas):
        """
        Exibe as mudanças mais significativas
        """
        if not mudancas:
            print("⚠️ Nenhuma mudança significativa detectada")
            return
        
        print(f"\n🎯 TOP MUDANÇAS DETECTADAS:")
        print("-" * 70)
        print("NUM  TENDÊNCIA     FREQ.ATUAL  FREQ.ANTERIOR  VARIAÇÃO  INTENSIDADE")
        print("-" * 70)
        
        for mudanca in mudancas:
            print(f"{mudanca['numero']:2d}   {mudanca['tendencia']:10s}  "
                  f"{mudanca['freq_atual']:8.1f}%   {mudanca['freq_anterior']:8.1f}%      "
                  f"{mudanca['variacao']:+5.1f}%   {mudanca['intensidade']}")
    
    def exibir_tendencias(self, tendencias):
        """
        Exibe as tendências mais significativas
        """
        if not tendencias:
            print("⚠️ Nenhuma tendência detectada")
            return
        
        # Filtrar e ordenar tendências significativas
        tendencias_significativas = []
        
        for numero, info in tendencias.items():
            if abs(info['correlacao']) > 0.3:  # Correlação significativa
                tendencias_significativas.append((numero, info))
        
        tendencias_significativas.sort(key=lambda x: abs(x[1]['correlacao']), reverse=True)
        
        if tendencias_significativas:
            print(f"\n📊 TENDÊNCIAS MAIS SIGNIFICATIVAS:")
            print("-" * 80)
            print("NUM  TENDÊNCIA        CORREL.  FREQ.ATUAL  FREQ.MÉDIA  VOLATILIDADE")
            print("-" * 80)
            
            for numero, info in tendencias_significativas[:10]:  # Top 10
                print(f"{numero:2d}   {info['tendencia']:13s}  "
                      f"{info['correlacao']:6.3f}   {info['freq_atual']:7.1f}%   "
                      f"{info['freq_media']:7.1f}%      {info['volatilidade']:5.1f}")
        else:
            print("\n📊 Nenhuma tendência significativa detectada (correlação < 0.3)")
    
    def salvar_resultados(self, resultados):
        """
        Salva os resultados da análise
        """
        timestamp = resultados['timestamp']
        nome_arquivo = f"analise_janelas_deslizantes_{timestamp}.json"
        caminho_arquivo = Path(__file__).parent / nome_arquivo
        
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Resultados salvos: {nome_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return None
    
    def executar_analise_completa(self, num_janelas=5):
        """
        Executa análise completa de janelas deslizantes
        """
        print("🔄" * 25)
        print("🔄 ANÁLISE DE JANELAS DESLIZANTES - DETECÇÃO DE MUDANÇAS")
        print("🔄" * 25)
        
        if not self.carregar_dados():
            return None
        
        resultados = self.analisar_mudancas(num_janelas)
        
        arquivo_salvo = self.salvar_resultados(resultados)
        
        print("\n" + "=" * 60)
        print("🎉 ANÁLISE DE JANELAS CONCLUÍDA!")
        print("=" * 60)
        
        return resultados

def menu_principal():
    """
    Menu principal para análise de janelas
    """
    analisador = AnalisadorJanelasDeslizantes()
    
    while True:
        print("\n🔄 ANÁLISE DE JANELAS DESLIZANTES - MENU")
        print("=" * 50)
        print("1️⃣  📊 Análise com 3 Janelas (Rápida)")
        print("2️⃣  📈 Análise com 5 Janelas (Padrão)")
        print("3️⃣  🔍 Análise com 8 Janelas (Detalhada)")
        print("4️⃣  ⚙️ Análise Personalizada")
        print("5️⃣  📋 Ver Status da Base")
        print("0️⃣  🚪 Sair")
        print("=" * 50)
        
        escolha = input("🎯 Escolha uma opção (0-5): ").strip()
        
        if escolha == "1":
            print("📊 Executando análise rápida (3 janelas)...")
            analisador.executar_analise_completa(3)
        
        elif escolha == "2":
            print("📈 Executando análise padrão (5 janelas)...")
            analisador.executar_analise_completa(5)
        
        elif escolha == "3":
            print("🔍 Executando análise detalhada (8 janelas)...")
            analisador.executar_analise_completa(8)
        
        elif escolha == "4":
            try:
                num_janelas = int(input("Quantas janelas analisar (2-15): "))
                if 2 <= num_janelas <= 15:
                    analisador.executar_analise_completa(num_janelas)
                else:
                    print("❌ Número deve estar entre 2 e 15")
            except ValueError:
                print("❌ Digite um número válido")
        
        elif escolha == "5":
            if analisador.carregar_dados():
                print("✅ Base de dados OK")
        
        elif escolha == "0":
            print("👋 Encerrando análise...")
            break
        
        else:
            print("❌ Opção inválida!")
        
        if escolha != "0":
            input("\n⏸️ Pressione ENTER para continuar...")

def main():
    """
    Função principal
    """
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n⏹️ Análise interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
