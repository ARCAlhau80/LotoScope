#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALISADOR POSICIONAL AVANÇADO - LOTOFÁCIL
=============================================
Sistema de análise posicional com aprendizado de máquina para predição
de números por posição baseado em padrões temporais e teste regressivo.

Baseado na análise de frequências posicionais dos últimos sorteios.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Conexão com banco
try:
    from lotofacil_lite.database_config import db_config
    BANCO_DISPONIVEL = True
except ImportError:
    BANCO_DISPONIVEL = False

class AnalisadorPosicionalAvancado:
    """
    Analisador avançado de padrões posicionais da Lotofácil
    """
    
    def __init__(self):
        self.dados_historicos = None
        self.periodos = [30, 15, 10, 5, 3]
        self.posicoes = [f'N{i}' for i in range(1, 16)]
        self.numeros_lotofacil = list(range(1, 26))
        
        # Modelos de ML
        self.modelos = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        self.scaler = StandardScaler()
        self.resultados_predicao = {}
        self.historico_teste_regressivo = []
        
        print("🎯 Analisador Posicional Avançado inicializado")
    
    def carregar_dados_historicos(self, limite=500):
        """Carrega dados históricos dos sorteios"""
        if not BANCO_DISPONIVEL:
            print("❌ Banco de dados não disponível")
            return False
        
        try:
            if not db_config.test_connection():
                print("❌ Erro na conexão com banco")
                return False
            
            # Query otimizada para carregar histórico
            query = f"""
            SELECT TOP {limite} 
                Concurso, Data_Sorteio,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15
            FROM Resultados_INT 
            ORDER BY Concurso DESC
            """
            
            resultado = db_config.execute_query(query)
            
            if not resultado:
                print("❌ Nenhum dado encontrado")
                return False
            
            # Converte para DataFrame
            colunas = ['Concurso', 'Data_Sorteio'] + self.posicoes
            self.dados_historicos = pd.DataFrame(resultado, columns=colunas)
            
            # Ordena por concurso crescente para análise temporal
            self.dados_historicos = self.dados_historicos.sort_values('Concurso').reset_index(drop=True)
            
            print(f"✅ {len(self.dados_historicos)} sorteios carregados")
            print(f"📊 Range: Concurso {self.dados_historicos['Concurso'].min()} até {self.dados_historicos['Concurso'].max()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def calcular_frequencias_posicionais(self, periodo_dias):
        """Calcula frequências posicionais para um período específico"""
        if self.dados_historicos is None or len(self.dados_historicos) == 0:
            return None
        
        # Pega os últimos N sorteios
        dados_periodo = self.dados_historicos.tail(periodo_dias).copy()
        
        # Matriz de frequências posicionais
        freq_matriz = np.zeros((25, 15))  # 25 números x 15 posições
        
        for idx, row in dados_periodo.iterrows():
            for pos_idx, posicao in enumerate(self.posicoes):
                numero = int(row[posicao])
                if 1 <= numero <= 25:
                    freq_matriz[numero-1, pos_idx] += 1
        
        # Converte para percentuais
        total_sorteios = len(dados_periodo)
        if total_sorteios > 0:
            freq_percentual = (freq_matriz / total_sorteios) * 100
        else:
            freq_percentual = freq_matriz
        
        # Converte para DataFrame para facilitar manipulação
        df_freq = pd.DataFrame(
            freq_percentual,
            index=[f'{i}' for i in range(1, 26)],
            columns=self.posicoes
        )
        
        return df_freq
    
    def gerar_analise_comparativa(self):
        """Gera análise comparativa de todos os períodos"""
        print("\n🔍 GERANDO ANÁLISE COMPARATIVA DE PERÍODOS")
        print("=" * 60)
        
        analises = {}
        
        for periodo in self.periodos:
            print(f"📊 Analisando últimos {periodo} sorteios...")
            freq_df = self.calcular_frequencias_posicionais(periodo)
            
            if freq_df is not None:
                analises[f'{periodo}_sorteios'] = {
                    'frequencias': freq_df,
                    'periodo': periodo,
                    'melhores_por_posicao': self._obter_melhores_por_posicao(freq_df),
                    'estatisticas': self._calcular_estatisticas_periodo(freq_df)
                }
        
        self.analises_comparativas = analises
        print("✅ Análise comparativa concluída")
        return analises
    
    def _obter_melhores_por_posicao(self, freq_df):
        """Obtém os melhores números para cada posição"""
        melhores = {}
        
        for posicao in self.posicoes:
            # Top 3 números com maior frequência na posição
            top_numeros = freq_df[posicao].nlargest(3)
            melhores[posicao] = {
                'melhor': int(top_numeros.index[0]),
                'frequencia': round(top_numeros.iloc[0], 2),
                'top3': [(int(idx), round(val, 2)) for idx, val in top_numeros.items()]
            }
        
        return melhores
    
    def _calcular_estatisticas_periodo(self, freq_df):
        """Calcula estatísticas do período"""
        stats = {}
        
        for posicao in self.posicoes:
            serie = freq_df[posicao]
            stats[posicao] = {
                'media': round(serie.mean(), 2),
                'std': round(serie.std(), 2),
                'max': round(serie.max(), 2),
                'min': round(serie.min(), 2),
                'concentracao': round((serie.max() - serie.min()), 2)
            }
        
        return stats
    
    def preparar_dados_ml(self, janela_historico=50):
        """Prepara dados para machine learning"""
        print("\n🤖 PREPARANDO DADOS PARA MACHINE LEARNING")
        print("=" * 60)
        
        if self.dados_historicos is None or len(self.dados_historicos) < janela_historico + 10:
            print("❌ Dados insuficientes para ML")
            return False
        
        # Preparar features e targets para cada posição
        self.dados_ml = {}
        
        for pos_idx, posicao in enumerate(self.posicoes):
            print(f"📊 Preparando dados para {posicao}...")
            
            X = []  # Features
            y = []  # Target (número que saiu na posição)
            
            # Criar janelas deslizantes
            for i in range(janela_historico, len(self.dados_historicos) - 1):
                # Features: frequências posicionais dos últimos N sorteios
                janela_dados = self.dados_historicos.iloc[i-janela_historico:i]
                
                # Calcula frequências da janela atual
                freq_posicao = np.zeros(25)
                for _, row in janela_dados.iterrows():
                    numero = int(row[posicao])
                    if 1 <= numero <= 25:
                        freq_posicao[numero-1] += 1
                
                # Normaliza frequências
                freq_posicao = freq_posicao / len(janela_dados)
                
                # Adiciona features extras
                features = list(freq_posicao)
                features.extend([
                    pos_idx + 1,  # Índice da posição
                    len(janela_dados),  # Tamanho da janela
                    np.mean(freq_posicao),  # Média das frequências
                    np.std(freq_posicao),   # Desvio padrão
                ])
                
                X.append(features)
                
                # Target: número que saiu na posição no próximo sorteio
                proximo_numero = int(self.dados_historicos.iloc[i][posicao])
                y.append(proximo_numero)
            
            self.dados_ml[posicao] = {
                'X': np.array(X),
                'y': np.array(y),
                'feature_names': [f'freq_{i}' for i in range(1, 26)] + 
                               ['pos_idx', 'janela_size', 'freq_mean', 'freq_std']
            }
        
        print("✅ Dados ML preparados para todas as posições")
        return True
    
    def treinar_modelos_predicao(self, test_size=0.2):
        """Treina modelos de predição para cada posição"""
        print("\n🎯 TREINANDO MODELOS DE PREDIÇÃO")
        print("=" * 60)
        
        if not hasattr(self, 'dados_ml'):
            print("❌ Dados ML não preparados")
            return False
        
        self.modelos_treinados = {}
        self.metricas_modelos = {}
        
        for posicao in self.posicoes:
            print(f"🔧 Treinando modelos para {posicao}...")
            
            dados = self.dados_ml[posicao]
            X, y = dados['X'], dados['y']
            
            # Split treino/teste
            split_idx = int(len(X) * (1 - test_size))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Normaliza features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Treina modelos
            modelos_pos = {}
            metricas_pos = {}
            
            for nome_modelo, modelo in self.modelos.items():
                try:
                    # Treina modelo
                    modelo_clone = modelo.__class__(**modelo.get_params())
                    modelo_clone.fit(X_train_scaled, y_train)
                    
                    # Predições
                    y_pred = modelo_clone.predict(X_test_scaled)
                    
                    # Métricas
                    mae = mean_absolute_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    modelos_pos[nome_modelo] = {
                        'modelo': modelo_clone,
                        'scaler': scaler
                    }
                    
                    metricas_pos[nome_modelo] = {
                        'mae': round(mae, 3),
                        'r2': round(r2, 3),
                        'pred_media': round(np.mean(y_pred), 2)
                    }
                    
                except Exception as e:
                    print(f"❌ Erro ao treinar {nome_modelo} para {posicao}: {e}")
            
            self.modelos_treinados[posicao] = modelos_pos
            self.metricas_modelos[posicao] = metricas_pos
        
        print("✅ Modelos treinados para todas as posições")
        return True
    
    def realizar_predicao_proximo_sorteio(self, janela_predicao=30):
        """Realiza predição para o próximo sorteio"""
        print("\n🔮 PREDIÇÃO PARA PRÓXIMO SORTEIO")
        print("=" * 60)
        
        if not hasattr(self, 'modelos_treinados'):
            print("❌ Modelos não treinados")
            return None
        
        # Pega os últimos sorteios para fazer a predição
        ultimos_dados = self.dados_historicos.tail(janela_predicao)
        
        predicoes = {}
        confiancas = {}
        
        for posicao in self.posicoes:
            print(f"🎯 Predizendo {posicao}...")
            
            # Calcula frequências dos últimos sorteios para esta posição
            freq_posicao = np.zeros(25)
            for _, row in ultimos_dados.iterrows():
                numero = int(row[posicao])
                if 1 <= numero <= 25:
                    freq_posicao[numero-1] += 1
            
            # Normaliza frequências
            freq_posicao = freq_posicao / len(ultimos_dados)
            
            # Prepara features
            pos_idx = self.posicoes.index(posicao)
            features = list(freq_posicao)
            features.extend([
                pos_idx + 1,
                len(ultimos_dados),
                np.mean(freq_posicao),
                np.std(freq_posicao)
            ])
            
            features_array = np.array(features).reshape(1, -1)
            
            # Predições de todos os modelos
            predicoes_modelos = {}
            pesos_modelos = {}
            
            for nome_modelo, modelo_info in self.modelos_treinados[posicao].items():
                modelo = modelo_info['modelo']
                scaler = modelo_info['scaler']
                
                # Normaliza features
                features_scaled = scaler.transform(features_array)
                
                # Predição
                pred = modelo.predict(features_scaled)[0]
                
                # Peso baseado no R² do modelo
                r2 = self.metricas_modelos[posicao][nome_modelo]['r2']
                peso = max(0.1, r2)  # Peso mínimo de 0.1
                
                predicoes_modelos[nome_modelo] = pred
                pesos_modelos[nome_modelo] = peso
            
            # Predição final ponderada
            soma_pesos = sum(pesos_modelos.values())
            predicao_final = sum(pred * peso for pred, peso in 
                               zip(predicoes_modelos.values(), pesos_modelos.values())) / soma_pesos
            
            # Arredonda para número inteiro válido
            predicao_final = max(1, min(25, round(predicao_final)))
            
            # Calcula confiança baseada na concordância dos modelos
            desvio_predicoes = np.std(list(predicoes_modelos.values()))
            confianca = max(0.1, min(1.0, 1 - (desvio_predicoes / 25)))
            
            predicoes[posicao] = int(predicao_final)
            confiancas[posicao] = round(confianca, 3)
        
        self.ultima_predicao = {
            'predicoes': predicoes,
            'confiancas': confiancas,
            'timestamp': datetime.now().isoformat(),
            'janela_predicao': janela_predicao
        }
        
        return self.ultima_predicao
    
    def gerar_relatorio_completo(self):
        """Gera relatório completo da análise"""
        print("\n📊 RELATÓRIO COMPLETO DE ANÁLISE POSICIONAL")
        print("=" * 80)
        
        # 1. Análise comparativa de períodos
        if hasattr(self, 'analises_comparativas'):
            print("\n🔍 ANÁLISE COMPARATIVA DE PERÍODOS:")
            print("-" * 50)
            
            for periodo_nome, analise in self.analises_comparativas.items():
                periodo = analise['periodo']
                melhores = analise['melhores_por_posicao']
                
                print(f"\n📅 ÚLTIMOS {periodo} SORTEIOS:")
                print("Melhores números por posição:")
                
                for i, (posicao, dados) in enumerate(melhores.items()):
                    melhor_num = dados['melhor']
                    freq = dados['frequencia']
                    print(f"  {posicao}: Número {melhor_num:2d} ({freq:5.1f}%)")
                    
                    if (i + 1) % 5 == 0:  # Quebra linha a cada 5 posições
                        print()
        
        # 2. Métricas dos modelos ML
        if hasattr(self, 'metricas_modelos'):
            print("\n🤖 PERFORMANCE DOS MODELOS ML:")
            print("-" * 50)
            
            for nome_modelo in ['random_forest', 'gradient_boost', 'linear_regression']:
                print(f"\n🔧 {nome_modelo.upper()}:")
                
                mae_total = []
                r2_total = []
                
                for posicao in self.posicoes:
                    if posicao in self.metricas_modelos and nome_modelo in self.metricas_modelos[posicao]:
                        metricas = self.metricas_modelos[posicao][nome_modelo]
                        mae_total.append(metricas['mae'])
                        r2_total.append(metricas['r2'])
                
                if mae_total:
                    print(f"  MAE médio: {np.mean(mae_total):.3f}")
                    print(f"  R² médio: {np.mean(r2_total):.3f}")
                    print(f"  Posições treinadas: {len(mae_total)}")
        
        # 3. Predição atual
        if hasattr(self, 'ultima_predicao'):
            print("\n🔮 PREDIÇÃO PARA PRÓXIMO SORTEIO:")
            print("-" * 50)
            
            predicoes = self.ultima_predicao['predicoes']
            confiancas = self.ultima_predicao['confiancas']
            
            combinacao_predita = []
            for posicao in self.posicoes:
                numero = predicoes[posicao]
                confianca = confiancas[posicao]
                combinacao_predita.append(numero)
                print(f"  {posicao}: {numero:2d} (confiança: {confianca:.1%})")
            
            print(f"\n🎯 COMBINAÇÃO PREDITA: {sorted(set(combinacao_predita))}")
            print(f"📊 Números únicos: {len(set(combinacao_predita))}/15")
            
            # Análise da predição
            confianca_media = np.mean(list(confiancas.values()))
            print(f"🎲 Confiança média: {confianca_media:.1%}")
        
        # 4. Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        print("-" * 50)
        print("  1. Use a predição como referência, não como garantia")
        print("  2. Combine com outras análises para maior assertividade")
        print("  3. Monitore o teste regressivo para avaliar precisão")
        print("  4. Considere a confiança de cada posição")
        
        print("\n✅ Relatório completo gerado!")
    
    def executar_teste_regressivo(self, n_testes=10):
        """Executa teste regressivo para validar eficácia das predições"""
        print("\n🧪 EXECUTANDO TESTE REGRESSIVO")
        print("=" * 60)
        
        if self.dados_historicos is None or len(self.dados_historicos) < 100:
            print("❌ Dados insuficientes para teste regressivo")
            return False
        
        acertos_por_posicao = {posicao: [] for posicao in self.posicoes}
        acertos_totais = []
        
        # Simula predições nos últimos N sorteios
        for i in range(n_testes):
            print(f"🧪 Teste {i+1}/{n_testes}...")
            
            # Pega dados até um ponto no passado
            indice_teste = len(self.dados_historicos) - n_testes + i
            
            # Dados para treinamento (até o ponto de teste)
            dados_treino = self.dados_historicos.iloc[:indice_teste].copy()
            
            # Dado real do teste (próximo sorteio)
            sorteio_real = self.dados_historicos.iloc[indice_teste]
            
            # Temporariamente substitui dados históricos
            dados_originais = self.dados_historicos
            self.dados_historicos = dados_treino
            
            # Prepara dados e treina modelos para este teste
            if self.preparar_dados_ml(janela_historico=30):
                if self.treinar_modelos_predicao(test_size=0.3):
                    predicao = self.realizar_predicao_proximo_sorteio(janela_predicao=20)
                    
                    if predicao:
                        acertos_teste = 0
                        for posicao in self.posicoes:
                            numero_predito = predicao['predicoes'][posicao]
                            numero_real = int(sorteio_real[posicao])
                            
                            acerto = 1 if numero_predito == numero_real else 0
                            acertos_por_posicao[posicao].append(acerto)
                            acertos_teste += acerto
                        
                        acertos_totais.append(acertos_teste)
                        print(f"  ✅ Acertos: {acertos_teste}/15 posições")
            
            # Restaura dados originais
            self.dados_historicos = dados_originais
        
        # Calcula estatísticas do teste regressivo
        if acertos_totais:
            print(f"\n📊 RESULTADOS DO TESTE REGRESSIVO:")
            print(f"  • Acertos médios por teste: {np.mean(acertos_totais):.2f}/15")
            print(f"  • Melhor teste: {max(acertos_totais)}/15 acertos")
            print(f"  • Taxa de acerto geral: {np.mean(acertos_totais)/15:.1%}")
            
            print(f"\n📈 ACERTOS POR POSIÇÃO:")
            for posicao in self.posicoes:
                if acertos_por_posicao[posicao]:
                    taxa = np.mean(acertos_por_posicao[posicao])
                    print(f"  {posicao}: {taxa:.1%}")
            
            self.resultados_teste_regressivo = {
                'acertos_totais': acertos_totais,
                'acertos_por_posicao': acertos_por_posicao,
                'taxa_acerto_geral': np.mean(acertos_totais) / 15,
                'n_testes': n_testes
            }
            
            return True
        
        return False
    
    def salvar_resultados(self, nome_arquivo=None):
        """Salva resultados da análise"""
        if nome_arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"analise_posicional_{timestamp}.json"
        
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'analises_comparativas': getattr(self, 'analises_comparativas', {}),
            'ultima_predicao': getattr(self, 'ultima_predicao', {}),
            'resultados_teste_regressivo': getattr(self, 'resultados_teste_regressivo', {}),
            'metricas_modelos': getattr(self, 'metricas_modelos', {})
        }
        
        # Converte DataFrames para dict para serialização JSON
        for periodo, dados in resultados['analises_comparativas'].items():
            if 'frequencias' in dados and hasattr(dados['frequencias'], 'to_dict'):
                dados['frequencias'] = dados['frequencias'].to_dict()
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Resultados salvos em: {nome_arquivo}")
            return nome_arquivo
        
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return None

def main():
    """Função principal para executar análise completa"""
    print("🎯 ANALISADOR POSICIONAL AVANÇADO - LOTOFÁCIL")
    print("=" * 80)
    
    # Inicializa analisador
    analisador = AnalisadorPosicionalAvancado()
    
    # Carrega dados
    if not analisador.carregar_dados_historicos(limite=300):
        print("❌ Falha ao carregar dados")
        return
    
    # Executa análise comparativa
    analisador.gerar_analise_comparativa()
    
    # Prepara dados para ML
    if analisador.preparar_dados_ml(janela_historico=50):
        
        # Treina modelos
        if analisador.treinar_modelos_predicao():
            
            # Realiza predição
            analisador.realizar_predicao_proximo_sorteio()
            
            # Executa teste regressivo
            analisador.executar_teste_regressivo(n_testes=8)
    
    # Gera relatório completo
    analisador.gerar_relatorio_completo()
    
    # Salva resultados
    analisador.salvar_resultados()
    
    print("\n✅ Análise completa finalizada!")

if __name__ == "__main__":
    main()