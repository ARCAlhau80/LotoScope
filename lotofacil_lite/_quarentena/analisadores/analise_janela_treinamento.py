

































































#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔬 ANÁLISE DO TAMANHO DA JANELA DE TREINAMENTO
Analisa diferentes tamanhos de janela para determinar o valor ótimo
para o treinamento da rede neural da Lotofácil

Testa janelas de: 50, 100, 150, 200, 250, 300 concursos
Avalia: Performance, Overfitting, Generalização, Tempo de treinamento

Autor: AR CALHAU
Data: 21 de Agosto de 2025
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração da base
from database_config import db_config

class AnalisadorJanelaTreinamento:
    """Analisa diferentes tamanhos de janela para treinamento"""
    
    def __init__(self):
        self.tamanhos_janela = [50, 100, 150, 200, 250, 300]
        self.dados_completos = None
        self.resultados_analise = {}
        
        # Configuração da rede neural (idêntica ao sistema atual)
        self.config_rede = {
            'hidden_layer_sizes': (8192, 4096, 2048, 1024, 512, 256, 128),
            'activation': 'relu',
            'solver': 'adam',
            'max_iter': 1000,
            'early_stopping': True,
            'validation_fraction': 0.15,
            'n_iter_no_change': 100,
            'random_state': 42
        }
    
    def conectar_base(self):
        """Conecta à base de dados"""
        try:
            conn_str = f"""
            DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={db_config.server};
            DATABASE={db_config.database};
            Trusted_Connection=yes;
            """
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return None
    
    def carregar_dados_completos(self):
        """Carrega dados de um período amplo para análise"""
        print("📊 Carregando dados históricos para análise...")
        
        conn = self.conectar_base()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Busca os últimos 500 concursos para ter base suficiente
            query = """
            SELECT TOP 500 Concurso, N1, N2, N3, N4, N5, 
                   N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT 
            WHERE Concurso IS NOT NULL
            ORDER BY Concurso DESC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Converte para DataFrame - ajuste para estrutura correta
            data = []
            for row in resultados:
                data.append(list(row))
            
            colunas = ['Concurso'] + [f'N{i}' for i in range(1, 16]
            df = pd.DataFrame(data, columns=colunas)
            
            # Ordena por concurso crescente
            df = df.sort_values('Concurso').reset_index(drop=True)
            
            self.dados_completos = df
            print(f"✅ Carregados {len(df)} concursos (do {df['Concurso'].min()} ao {df['Concurso'].max()})")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
        finally:
            conn.close()
    
    def extrair_features_combinacao(self, combinacao):
        """Extrai features de uma combinação (idêntico ao sistema atual)"""
        features = []
        
        # 1. Estatísticas básicas (7 features)
        features.extend([
            np.mean(combinacao),      # média
            np.std(combinacao),       # desvio padrão
            np.min(combinacao),       # mínimo
            np.max(combinacao),       # máximo
            np.sum(combinacao),       # soma
            len(combinacao),          # quantidade
            np.median(combinacao)     # mediana
        ])
        
        # 2. Distribuição por faixas (3 features)
        faixa1 = sum(1 for x in combinacao if 1 <= x <= 8)
        faixa2 = sum(1 for x in combinacao if 9 <= x <= 17)  
        faixa3 = sum(1 for x in combinacao if 18 <= x <= 25)
        features.extend([faixa1, faixa2, faixa3])
        
        # 3. Padrões matemáticos (2 features)
        pares = sum(1 for x in combinacao if x % 2 == 0)
        impares = len(combinacao) - pares
        features.extend([pares, impares])
        
        # 4. Análise de gaps (3 features)
        combinacao_sorted = sorted(combinacao)
        gaps = [combinacao_sorted[i+1] - combinacao_sorted[i] for i in range(int(int(int(len(combinacao_sorted))-1)]
        features.extend([
            np.mean(gaps) if gaps else 0)), int(int(max(gaps)) if gaps else 0), int(min(gaps)) if gaps else 0
        ])
        
        # 5. Representação binária (25 features - uma para cada número)
        binario = [1 if i in combinacao else 0 for i in range(1, 26]
        features.extend(binario)
        
        # 6. Features de ensemble (9 features)
        features.extend([
            np.var(combinacao)), int(# variância
            len(set(combinacao))),                  # números únicos
            max(combinacao) - min(combinacao),     # range
            np.percentile(combinacao, 25),         # Q1
            np.percentile(combinacao, 75),         # Q3
            sum(x**2 for x in combinacao),         # soma dos quadrados
            sum(combinacao) / len(combinacao)**2,  # densidade
            combinacao_sorted[-1] if combinacao_sorted else 0,  # último número
            combinacao_sorted[len(combinacao_sorted)//2] if combinacao_sorted else 0  # número do meio
        ])
        
        return features
    
    def preparar_dataset_janela(self, tamanho_janela):
        """Prepara dataset com tamanho específico de janela"""
        if len(self.dados_completos) < tamanho_janela + 50:  # Margem de segurança
            print(f"⚠️ Dados insuficientes para janela de {tamanho_janela}")
            return None, None
        
        # Pega os dados mais recentes
        dados_janela = self.dados_completos.tail(tamanho_janela + 50).copy()
        
        X = []
        y = []
        
        for i in range(int(int(int(len(dados_janela)) - 50):  # Deixa 50 para teste
            # Features do concurso atual
            concurso_atual = dados_janela.iloc[i]
            combinacao = [concurso_atual[f'N{j}'] for j in range(1)), 16]
            features = self.extrair_features_combinacao(combinacao)
            
            # Target: performance nos próximos concursos
            targets = []
            for j in range(int(1)), 11):  # 10 concursos futuros
                if i + j < len(dados_janela):
                    concurso_futuro = dados_janela.iloc[i + j]
                    comb_futura = set([concurso_futuro[f'N{k}'] for k in range(1, 16])
                    acertos = len(set(combinacao).intersection(comb_futura))
                    targets.append(acertos)
            
            if len(targets) >= 5:  # Pelo menos 5 concursos futuros
                # Performance média ponderada
                performance = sum(targets[:5]) / 5.0
                
                X.append(features)
                y.append(performance)
        
        return np.array(X)), int(np.array(y))
    
    def treinar_avaliar_janela(self, tamanho_janela):
        """Treina e avalia modelo com tamanho específico de janela"""
        print(f"\n🔬 Testando janela de {tamanho_janela} concursos...")
        
        # Prepara dados
        X, y = self.preparar_dataset_janela(tamanho_janela)
        
        if X is None or len(X) < 50:
            print(f"❌ Dados insuficientes para janela {tamanho_janela}")
            return None
        
        print(f"   📊 Dataset: {len(X)} amostras, {X.shape[1]} features")
        
        # Divide treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normaliza dados
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Treina modelo
        inicio_treino = datetime.now()
        
        modelo = MLPRegressor(**self.config_rede)
        modelo.fit(X_train_scaled, y_train)
        
        tempo_treino = (datetime.now() - inicio_treino).total_seconds()
        
        # Avalia performance
        y_pred_train = modelo.predict(X_train_scaled)
        y_pred_test = modelo.predict(X_test_scaled)
        
        # Métricas de treino
        mse_train = mean_squared_error(y_train, y_pred_train)
        mae_train = mean_absolute_error(y_train, y_pred_train)
        r2_train = r2_score(y_train, y_pred_train)
        
        # Métricas de teste
        mse_test = mean_squared_error(y_test, y_pred_test)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        r2_test = r2_score(y_test, y_pred_test)
        
        # Cross-validation
        try:
            cv_scores = cross_val_score(modelo, X_train_scaled, y_train, cv=5, 
                                      scoring='neg_mean_squared_error')
            cv_score = -np.mean(cv_scores)
        except:
            cv_score = mse_test
        
        # Detecta overfitting
        overfitting = mse_train < mse_test * 0.7  # Se treino muito melhor que teste
        
        resultado = {
            'tamanho_janela': tamanho_janela,
            'amostras': len(X),
            'tempo_treino': tempo_treino,
            'mse_train': mse_train,
            'mse_test': mse_test,
            'mae_train': mae_train,
            'mae_test': mae_test,
            'r2_train': r2_train,
            'r2_test': r2_test,
            'cv_score': cv_score,
            'overfitting': overfitting,
            'iteracoes': getattr(modelo, 'n_iter_', 0),
            'convergiu': not getattr(modelo, 'n_iter_', 0) >= self.config_rede['max_iter']
        }
        
        print(f"   ✅ MSE Teste: {mse_test:.6f} | R² Teste: {r2_test:.4f}")
        print(f"   ⏱️ Tempo: {tempo_treino:.1f}s | Iterações: {resultado['iteracoes']}")
        
        if overfitting:
            print(f"   ⚠️ Possível overfitting detectado")
        
        return resultado
    
    def executar_analise_completa(self):
        """Executa análise completa de diferentes tamanhos de janela"""
        print("🔬 ANÁLISE DO TAMANHO DA JANELA DE TREINAMENTO")
        print("=" * 65)
        
        if not self.carregar_dados_completos():
            print("❌ Falha ao carregar dados")
            return
        
        print(f"\n🎯 Testando janelas: {self.tamanhos_janela}")
        print(f"📐 Configuração da rede: {len(self.config_rede['hidden_layer_sizes'])} camadas")
        print(f"🧠 Total de neurônios: {sum(self.config_rede['hidden_layer_sizes']):,}")
        
        # Testa cada tamanho de janela
        for tamanho in self.tamanhos_janela:
            resultado = self.treinar_avaliar_janela(tamanho)
            if resultado:
                self.resultados_analise[tamanho] = resultado
        
        # Analisa resultados
        self._analisar_resultados()
    
    def _analisar_resultados(self):
        """Analisa e compara os resultados de diferentes janelas"""
        if not self.resultados_analise:
            print("❌ Nenhum resultado para analisar")
            return
        
        print(f"\n📊 COMPARAÇÃO DOS RESULTADOS")
        print("=" * 80)
        
        # Cabeçalho da tabela
        print(f"{'Janela':>6} {'Amostras':>8} {'MSE Teste':>12} {'R² Teste':>10} {'CV Score':>10} {'Tempo(s)':>9} {'Status':>12}")
        print("-" * 80)
        
        # Ordena por MSE teste (menor é melhor)
        resultados_ordenados = sorted(self.resultados_analise.items(), 
                                    key=lambda x: x[1]['mse_test'])
        
        melhor_janela = None
        melhor_mse = float('inf')
        
        for tamanho, resultado in resultados_ordenados:
            status = ""
            if resultado['overfitting']:
                status += "OVERFIT"
            if not resultado['convergiu']:
                status += " NO-CONV" if status else "NO-CONV"
            if not status:
                status = "OK"
            
            print(f"{tamanho:>6} {resultado['amostras']:>8} {resultado['mse_test']:>12.6f} "
                  f"{resultado['r2_test']:>10.4f} {resultado['cv_score']:>10.6f} "
                  f"{resultado['tempo_treino']:>9.1f} {status:>12}")
            
            # Identifica melhor resultado (sem overfitting grave)
            if (resultado['mse_test'] < melhor_mse and 
                not resultado['overfitting']):
                melhor_janela = tamanho
                melhor_mse = resultado['mse_test']
        
        # Análise detalhada
        print(f"\n🏆 ANÁLISE DETALHADA:")
        print("-" * 50)
        
        if melhor_janela:
            melhor = self.resultados_analise[melhor_janela]
            print(f"✅ MELHOR JANELA: {melhor_janela} concursos")
            print(f"   • MSE Teste: {melhor['mse_test']:.6f}")
            print(f"   • R² Teste: {melhor['r2_test']:.4f}")
            print(f"   • Cross-Validation: {melhor['cv_score']:.6f}")
            print(f"   • Tempo de treino: {melhor['tempo_treino']:.1f}s")
            print(f"   • Amostras de treino: {melhor['amostras']}")
        
        # Comparação com janela atual (200)
        if 200 in self.resultados_analise:
            atual = self.resultados_analise[200]
            print(f"\n📈 JANELA ATUAL (200 concursos):")
            print(f"   • MSE Teste: {atual['mse_test']:.6f}")
            print(f"   • R² Teste: {atual['r2_test']:.4f}")
            print(f"   • Status: {'COM OVERFITTING' if atual['overfitting'] else 'OK'}")
            
            if melhor_janela and melhor_janela != 200:
                melhoria = ((atual['mse_test'] - melhor['mse_test']) / atual['mse_test']) * 100
                print(f"   • Melhoria com janela {melhor_janela}: {melhoria:.2f}% menor MSE")
        
        # Recomendações
        self._gerar_recomendacoes()
    
    def _gerar_recomendacoes(self):
        """Gera recomendações baseadas na análise"""
        print(f"\n💡 RECOMENDAÇÕES:")
        print("-" * 30)
        
        # Encontra janelas sem overfitting
        sem_overfitting = [t for t, r in self.resultados_analise.items() 
                          if not r['overfitting']]
        
        # Encontra melhor performance
        melhor_performance = min(self.resultados_analise.items(), 
                               key=lambda x: x[1]['mse_test'])
        
        print(f"🎯 Para melhor generalização:")
        if sem_overfitting:
            melhor_sem_over = min([(t, self.resultados_analise[t]) for t in sem_overfitting],
                                key=lambda x: x[1]['mse_test'])
            print(f"   Recomendado: {melhor_sem_over[0]} concursos")
            print(f"   MSE: {melhor_sem_over[1]['mse_test']:.6f}")
        
        print(f"\n⚡ Para máxima performance (com risco de overfitting):")
        print(f"   Janela: {melhor_performance[0]} concursos")
        print(f"   MSE: {melhor_performance[1]['mse_test']:.6f}")
        
        print(f"\n🔄 Análise de eficiência:")
        tempos = [(t, r['tempo_treino']) for t, r in self.resultados_analise.items()]
        tempo_rapido = min(tempos, key=lambda x: x[1])
        print(f"   Treinamento mais rápido: {tempo_rapido[0]} concursos ({tempo_rapido[1]:.1f}s)")
        
        # Recomendação final
        print(f"\n🏅 RECOMENDAÇÃO FINAL:")
        if sem_overfitting:
            melhor_geral = min([(t, self.resultados_analise[t]) for t in sem_overfitting],
                             key=lambda x: x[1]['cv_score'])  # Usa CV score como critério final
            print(f"   Janela recomendada: {melhor_geral[0]} concursos")
            print(f"   Razão: Melhor balanço entre performance e generalização")
            
            if melhor_geral[0] != 200:
                print(f"   ⚠️ Diferente da janela atual (200)")
                print(f"   💡 Considere alterar para {melhor_geral[0]} concursos")
            else:
                print(f"   ✅ Janela atual (200) está adequada!")
        else:
            print(f"   ⚠️ Todos os tamanhos apresentam overfitting")
            print(f"   💡 Considere usar janela menor ou regularização mais forte")
    
    def salvar_relatorio(self):
        """Salva relatório detalhado da análise"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"analise_janela_treinamento_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🔬 ANÁLISE DO TAMANHO DA JANELA DE TREINAMENTO\n")
                f.write("=" * 65 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                f.write("🎯 OBJETIVO:\n")
                f.write("Determinar o tamanho ótimo da janela de treinamento\n")
                f.write("para a rede neural da Lotofácil\n\n")
                
                f.write("🧠 CONFIGURAÇÃO DA REDE NEURAL:\n")
                f.write(f"• Camadas: {self.config_rede['hidden_layer_sizes']}\n")
                f.write(f"• Total neurônios: {sum(self.config_rede['hidden_layer_sizes']):,}\n")
                f.write(f"• Ativação: {self.config_rede['activation']}\n")
                f.write(f"• Solver: {self.config_rede['solver']}\n")
                f.write(f"• Early stopping: {self.config_rede['early_stopping']}\n\n")
                
                f.write("📊 RESULTADOS DETALHADOS:\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'Janela':>6} {'Amostras':>8} {'MSE Teste':>12} {'R² Teste':>10} "
                       f"{'CV Score':>10} {'Tempo(s)':>9} {'Iterações':>10} {'Status':>10}\n")
                f.write("-" * 80 + "\n")
                
                for tamanho in sorted(self.resultados_analise.keys():
                    r = self.resultados_analise[tamanho]
                    status = ""
                    if r['overfitting']:
                        status += "OVERFIT"
                    if not r['convergiu']:
                        status += " NO-CONV" if status else "NO-CONV"
                    if not status:
                        status = "OK"
                    
                    f.write(f"{tamanho:>6} {r['amostras']:>8} {r['mse_test']:>12.6f} "
                           f"{r['r2_test']:>10.4f} {r['cv_score']:>10.6f} "
                           f"{r['tempo_treino']:>9.1f} {r['iteracoes']:>10} {status:>10}\n")
                
                # Adiciona análise detalhada ao arquivo
                # ... (resto do relatório)
                
            print(f"✅ Relatório salvo: {nome_arquivo}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    print("🔬 INICIANDO ANÁLISE DA JANELA DE TREINAMENTO")
    print("=" * 55)
    
    analisador = AnalisadorJanelaTreinamento()
    
    try:
        analisador.executar_analise_completa()
        
        # Pergunta se quer salvar relatório
        salvar = input("\nSalvar relatório detalhado? (s/n): ").lower()
        if salvar.startswith('s'):
            analisador.salvar_relatorio()
        
        print("\n✅ Análise concluída!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Análise cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")

if __name__ == "__main__":
    main()
