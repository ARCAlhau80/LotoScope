#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA DE ANÁLISE PREDITIVA ESPECIALIZADO - LOTOSCOPE
=========================================================
Sistema especializado para análise e predição de 8 parâmetros específicos:
1. maior_que_ultimo - Números maiores que o último concurso
2. menor_que_ultimo - Números menores que o último concurso  
3. igual_ao_ultimo - Números iguais ao último concurso
4. N1 - Primeiro número sorteado (menor)
5. N15 - Último número sorteado (maior)
6. 6a25 - Quantidade de números na faixa de 6 a 25
7. 6a20 - Quantidade de números na faixa de 6 a 20
8. Acertos da combinação: (1,2,4,6,8,9,11,13,15,16,19,20,22,24,25)

Autor: AR CALHAU
Data: 12/11/2025
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass, asdict
import pickle
from pathlib import Path

# Importações para ML
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.neural_network import MLPRegressor
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    import warnings
    warnings.filterwarnings('ignore')
    ML_DISPONIVEL = True
except ImportError:
    print("⚠️ Bibliotecas de ML não disponíveis. Usando análise estatística.")
    ML_DISPONIVEL = False

@dataclass
class ParametrosConcurso:
    """Parâmetros extraídos de um concurso"""
    numero_concurso: int
    concurso: int
    data_sorteio: str
    numeros: List[int]
    
    # Parâmetros alvo
    maior_que_ultimo: int
    menor_que_ultimo: int
    igual_ao_ultimo: int
    n1: int
    n15: int
    faixa_6a25: int
    faixa_6a20: int
    acertos_combinacao_fixa: int

@dataclass
class PredicaoParametros:
    """Predição dos 8 parâmetros"""
    concurso_alvo: int
    maior_que_ultimo: float
    menor_que_ultimo: float
    igual_ao_ultimo: float
    n1: float
    n15: float
    faixa_6a25: float
    faixa_6a20: float
    acertos_combinacao_fixa: float
    confianca: float
    timestamp: str

class AnalisadorPreditivoEspecializado:
    """Sistema de análise preditiva para os 8 parâmetros específicos"""
    
    def __init__(self, config_db=None):
        self.logger = self._configurar_logging()
        self.combinacao_fixa = [1,2,4,6,8,9,11,13,15,16,19,20,22,24,25]
        self.dados_historicos = []
        self.modelos_treinados = {}
        self.scalers = {}
        
        # Configuração de database
        self.config_db = config_db
        
        # Arquivos de persistência
        self.arquivo_dados = "dados_parametros_especializados.json"
        self.arquivo_modelos = "modelos_preditivos_especializados.pkl"
        
        self.logger.info("Sistema de Análise Preditiva Especializado inicializado")
    
    def _configurar_logging(self):
        """Configura sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('analise_preditiva_especializada.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def carregar_dados_historicos(self):
        """Carrega dados históricos da Lotofácil"""
        try:
            # Sempre tenta carregar do SQL Server primeiro
            self.logger.info("Tentando carregar dados do SQL Server...")
            dados = self._carregar_do_sql_server()
            if dados and len(dados) > 0:
                self.logger.info(f"Carregados {len(dados)} concursos do SQL Server")
                return self._processar_dados_sql(dados)
            
            # Fallback: dados simulados
            self.logger.info("SQL Server indisponível. Gerando dados simulados para teste...")
            return self._gerar_dados_simulados()
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            return self._gerar_dados_simulados()
    
    def _carregar_do_sql_server(self):
        """Carrega dados reais do SQL Server incluindo parâmetros de comparação"""
        try:
            from lotofacil_lite.database_config import db_config
            
            if not db_config.test_connection():
                self.logger.warning("Conexão com banco não disponível")
                return None

            # Query para buscar dados reais com parâmetros de comparação
            query = """
            SELECT TOP 1000
                Concurso, Data_Sorteio,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                maior_que_ultimo, menor_que_ultimo, igual_ao_ultimo
            FROM Resultados_INT
            WHERE maior_que_ultimo IS NOT NULL 
              AND menor_que_ultimo IS NOT NULL 
              AND igual_ao_ultimo IS NOT NULL
            ORDER BY Concurso DESC
            """
            
            resultado = db_config.execute_query(query)
            
            if not resultado:
                self.logger.warning("Nenhum dado encontrado na tabela Resultados_INT")
                return None
            
            dados = []
            for row in resultado:
                concurso = row[0]
                data_sorteio = row[1].strftime('%Y-%m-%d') if row[1] else f'2024-{concurso%12+1:02d}-01'
                numeros = sorted([row[i] for i in range(2, 17)])
                
                # Parâmetros de comparação já calculados na tabela
                maior_que_ultimo = row[17] 
                menor_que_ultimo = row[18]  
                igual_ao_ultimo = row[19]
                
                dados.append({
                    'concurso': concurso,
                    'data_sorteio': data_sorteio,
                    'numeros': numeros,
                    'maior_que_ultimo': maior_que_ultimo,
                    'menor_que_ultimo': menor_que_ultimo,
                    'igual_ao_ultimo': igual_ao_ultimo
                })
            
            # Ordenar cronologicamente  
            dados.sort(key=lambda x: x['concurso'])
            self.logger.info(f"Carregados {len(dados)} concursos reais do SQL Server")
            return dados
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar com SQL Server: {e}")
            return None
    
    def _processar_dados_sql(self, dados_sql):
        """Processa dados do SQL Server convertendo para ParametrosConcurso"""
        parametros_lista = []
        
        for dados in dados_sql:
            concurso = dados['concurso']
            numeros = dados['numeros']
            data_sorteio = dados['data_sorteio']
            
            # Calcular parâmetros básicos
            n1 = min(numeros)
            n15 = max(numeros)
            faixa_6a20 = len([n for n in numeros if 6 <= n <= 20])
            faixa_6a25 = len([n for n in numeros if 6 <= n <= 25])
            acertos_combinacao_fixa = len(set(numeros) & set(self.combinacao_fixa))
            
            # Usar parâmetros de comparação já calculados na tabela
            maior_que_ultimo = dados.get('maior_que_ultimo', 0)
            menor_que_ultimo = dados.get('menor_que_ultimo', 0)
            igual_ao_ultimo = dados.get('igual_ao_ultimo', 0)
            
            # Validação da regra dos 15
            soma_comparacao = maior_que_ultimo + menor_que_ultimo + igual_ao_ultimo
            if soma_comparacao != 15:
                igual_ao_ultimo = 15 - maior_que_ultimo - menor_que_ultimo
            
            parametros = ParametrosConcurso(
                numero_concurso=concurso,
                concurso=concurso,
                data_sorteio=data_sorteio,
                numeros=numeros,
                maior_que_ultimo=maior_que_ultimo,
                menor_que_ultimo=menor_que_ultimo,
                igual_ao_ultimo=igual_ao_ultimo,
                n1=n1,
                n15=n15,
                faixa_6a25=faixa_6a25,
                faixa_6a20=faixa_6a20,
                acertos_combinacao_fixa=acertos_combinacao_fixa
            )
            
            parametros_lista.append(parametros)
        
        self.logger.info(f"Processados {len(parametros_lista)} registros do SQL Server")
        return parametros_lista
    
    def _gerar_dados_simulados(self):
        """Gera dados simulados baseados em padrões realísticos"""
        dados = []
        base_date = datetime(2020, 1, 1)
        
        for i in range(1, 3528):  # Até concurso atual aproximado
            # Gera combinação realística
            numeros = self._gerar_combinacao_realistica()
            
            # Data do sorteio
            data_sorteio = (base_date + timedelta(days=i*3)).strftime('%Y-%m-%d')
            
            dados.append({
                'concurso': i,
                'data_sorteio': data_sorteio,
                'numeros': numeros
            })
        
        return dados
    
    def _gerar_combinacao_realistica(self):
        """Gera combinação de números realística"""
        numeros = []
        
        # Garante distribuição mais realística
        faixas = [
            (1, 5, 2),    # Baixos: 2 números
            (6, 10, 3),   # Médio-baixos: 3 números
            (11, 15, 4),  # Médios: 4 números
            (16, 20, 3),  # Médio-altos: 3 números
            (21, 25, 3)   # Altos: 3 números
        ]
        
        for inicio, fim, quantidade in faixas:
            candidatos = list(range(inicio, fim + 1))
            selecionados = np.random.choice(candidatos, 
                                          size=min(quantidade, len(candidatos)), 
                                          replace=False)
            numeros.extend(selecionados)
        
        # Garante exatamente 15 números
        while len(numeros) < 15:
            novo = np.random.randint(1, 26)
            if novo not in numeros:
                numeros.append(novo)
        
        # Remove excesso se houver
        numeros = numeros[:15]
        
        return sorted(numeros)
    
    def extrair_parametros_concurso(self, dados_concurso: Dict, ultimo_concurso: Dict = None) -> ParametrosConcurso:
        """Extrai os 8 parâmetros específicos de um concurso"""
        numeros = dados_concurso['numeros']
        concurso = dados_concurso['concurso']
        
        # N1 e N15
        n1 = min(numeros)
        n15 = max(numeros)
        
        # Faixas 6a20 e 6a25
        faixa_6a20 = len([n for n in numeros if 6 <= n <= 20])
        faixa_6a25 = len([n for n in numeros if 6 <= n <= 25])
        
        # Acertos da combinação fixa
        acertos_combinacao_fixa = len(set(numeros) & set(self.combinacao_fixa))
        
        # Usar parâmetros de comparação da tabela se disponíveis
        if ('maior_que_ultimo' in dados_concurso and dados_concurso['maior_que_ultimo'] is not None and
            'menor_que_ultimo' in dados_concurso and dados_concurso['menor_que_ultimo'] is not None and
            'igual_ao_ultimo' in dados_concurso and dados_concurso['igual_ao_ultimo'] is not None):
            
            # Usar dados já calculados da tabela
            maior_que_ultimo = dados_concurso['maior_que_ultimo']
            menor_que_ultimo = dados_concurso['menor_que_ultimo'] 
            igual_ao_ultimo = dados_concurso['igual_ao_ultimo']
            
            self.logger.debug(f"Concurso {concurso}: Usando parâmetros da tabela - maior={maior_que_ultimo}, menor={menor_que_ultimo}, igual={igual_ao_ultimo}")
            
        else:
            # Calcular comparação com último concurso (números vs números)
            if ultimo_concurso:
                numeros_anteriores = set(ultimo_concurso['numeros'])
                numeros_atuais = set(numeros)
                
                # Comparação número a número
                maior_que_ultimo = 0
                menor_que_ultimo = 0
                igual_ao_ultimo = 0
                
                for num_atual in numeros_atuais:
                    # Verifica quantos números anteriores são menores que este número atual
                    menores_que_atual = sum(1 for num_ant in numeros_anteriores if num_ant < num_atual)
                    # Verifica quantos números anteriores são maiores que este número atual  
                    maiores_que_atual = sum(1 for num_ant in numeros_anteriores if num_ant > num_atual)
                    # Verifica se este número atual existe no concurso anterior
                    igual_anterior = 1 if num_atual in numeros_anteriores else 0
                    
                    if menores_que_atual > 0:
                        maior_que_ultimo += 1
                    elif maiores_que_atual > 0:
                        menor_que_ultimo += 1
                    elif igual_anterior > 0:
                        igual_ao_ultimo += 1
                    else:
                        # Número não tem comparação direta - conta como "igual" (faixa)
                        igual_ao_ultimo += 1
            else:
                # Primeiro concurso: valores padrão
                maior_que_ultimo = 0
                menor_que_ultimo = 0
                igual_ao_ultimo = 15
        
        # Validação da regra dos 15
        soma_comparacao = maior_que_ultimo + menor_que_ultimo + igual_ao_ultimo
        if soma_comparacao != 15:
            # Ajuste automático para garantir soma = 15
            igual_ao_ultimo = 15 - maior_que_ultimo - menor_que_ultimo
        
        return ParametrosConcurso(
            numero_concurso=concurso,
            concurso=concurso,
            data_sorteio=dados_concurso['data_sorteio'],
            numeros=numeros,
            maior_que_ultimo=maior_que_ultimo,
            menor_que_ultimo=menor_que_ultimo,
            igual_ao_ultimo=igual_ao_ultimo,
            n1=n1,
            n15=n15,
            faixa_6a25=faixa_6a25,
            faixa_6a20=faixa_6a20,
            acertos_combinacao_fixa=acertos_combinacao_fixa
        )
    
    def processar_dados_historicos(self):
        """Processa todos os dados históricos e extrai parâmetros"""
        dados_brutos = self.carregar_dados_historicos()
        if not dados_brutos:
            self.logger.error("Nenhum dado histórico disponível")
            return False
        
        self.logger.info(f"Processando {len(dados_brutos)} concursos...")
        
        # Se os dados já são objetos ParametrosConcurso (dados reais), usa diretamente
        if dados_brutos and isinstance(dados_brutos[0], ParametrosConcurso):
            self.dados_historicos = dados_brutos
            self.logger.info(f"Dados já processados: {len(self.dados_historicos)} concursos")
        else:
            # Processar dados brutos (simulados)
            self.dados_historicos = []
            ultimo_concurso = None
            
            for dados_concurso in dados_brutos:
                try:
                    parametros = self.extrair_parametros_concurso(dados_concurso, ultimo_concurso)
                    self.dados_historicos.append(parametros)
                    ultimo_concurso = dados_concurso
                    
                except Exception as e:
                    concurso_id = getattr(dados_concurso, 'concurso', 'N/A') if hasattr(dados_concurso, 'concurso') else dados_concurso.get('concurso', 'N/A')
                    self.logger.warning(f"Erro ao processar concurso {concurso_id}: {e}")
                    continue
        
        self.logger.info(f"Processados {len(self.dados_historicos)} concursos com parametros")
        
        # Salva dados processados
        self._salvar_dados_processados()
        
        return True
    
    def _salvar_dados_processados(self):
        """Salva dados processados em JSON"""
        dados_json = []
        for param in self.dados_historicos:
            # Converte numpy int64 para int padrão
            param_dict = asdict(param)
            for key, value in param_dict.items():
                if hasattr(value, 'item'):  # numpy types
                    param_dict[key] = value.item()
                elif isinstance(value, np.integer):
                    param_dict[key] = int(value)
                elif isinstance(value, list):
                    param_dict[key] = [int(v) if hasattr(v, 'item') else v for v in value]
            dados_json.append(param_dict)
        
        with open(self.arquivo_dados, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_concursos': len(dados_json),
                'dados': dados_json
            }, f, indent=2)
        
        self.logger.info(f"Dados processados salvos em {self.arquivo_dados}")
    
    def _carregar_dados_processados(self):
        """Carrega dados processados do JSON"""
        if not os.path.exists(self.arquivo_dados):
            return False
        
        try:
            with open(self.arquivo_dados, 'r') as f:
                dados_json = json.load(f)
            
            self.dados_historicos = []
            for item in dados_json['dados']:
                self.dados_historicos.append(ParametrosConcurso(**item))
            
            self.logger.info(f"Carregar dados processados de {self.arquivo_dados}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados processados: {e}")
            return False
    
    def analisar_correlacoes(self):
        """Analisa correlações entre os 8 parâmetros"""
        if not self.dados_historicos:
            self.logger.error("Nenhum dado histórico processado disponível")
            return None
        
        # Prepara dados para análise
        df_data = []
        for param in self.dados_historicos:
            df_data.append([
                param.maior_que_ultimo,
                param.menor_que_ultimo,
                param.igual_ao_ultimo,
                param.n1,
                param.n15,
                param.faixa_6a25,
                param.faixa_6a20,
                param.acertos_combinacao_fixa
            ])
        
        colunas = [
            'maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo',
            'n1', 'n15', 'faixa_6a25', 'faixa_6a20', 'acertos_combinacao_fixa'
        ]
        
        df = pd.DataFrame(df_data, columns=colunas)
        
        # Calcula correlações
        correlacoes = df.corr()
        
        self.logger.info("Analise de Correlacoes:")
        for i, col1 in enumerate(colunas):
            for j, col2 in enumerate(colunas):
                if i < j:  # Evita duplicatas
                    corr = correlacoes.loc[col1, col2]
                    if abs(corr) > 0.3:  # Correlações significativas
                        self.logger.info(f"   {col1} <-> {col2}: {corr:.3f}")
        
        return correlacoes
    
    def treinar_modelos_preditivos(self):
        """Treina modelos de ML para predição dos 8 parâmetros"""
        if not ML_DISPONIVEL:
            self.logger.warning("ML não disponível. Usando predição estatística.")
            return self._treinar_modelos_estatisticos()
        
        if not self.dados_historicos:
            self.logger.error("Nenhum dado para treinamento")
            return False
        
        self.logger.info("Iniciando treinamento de modelos preditivos...")
        
        # Prepara features (características) e targets (alvos)
        features = []
        targets = {
            'maior_que_ultimo': [],
            'menor_que_ultimo': [],
            'igual_ao_ultimo': [],
            'n1': [],
            'n15': [],
            'faixa_6a25': [],
            'faixa_6a20': [],
            'acertos_combinacao_fixa': []
        }
        
        # Cria features baseadas em janela temporal
        janela = 5  # Últimos 5 concursos como features
        
        for i in range(janela, len(self.dados_historicos)):
            # Features: dados dos últimos N concursos
            feature_row = []
            for j in range(i - janela, i):
                param = self.dados_historicos[j]
                feature_row.extend([
                    param.maior_que_ultimo,
                    param.menor_que_ultimo,
                    param.igual_ao_ultimo,
                    param.n1,
                    param.n15,
                    param.faixa_6a25,
                    param.faixa_6a20,
                    param.acertos_combinacao_fixa
                ])
            
            features.append(feature_row)
            
            # Target: parâmetros do concurso atual
            param_atual = self.dados_historicos[i]
            targets['maior_que_ultimo'].append(param_atual.maior_que_ultimo)
            targets['menor_que_ultimo'].append(param_atual.menor_que_ultimo)
            targets['igual_ao_ultimo'].append(param_atual.igual_ao_ultimo)
            targets['n1'].append(param_atual.n1)
            targets['n15'].append(param_atual.n15)
            targets['faixa_6a25'].append(param_atual.faixa_6a25)
            targets['faixa_6a20'].append(param_atual.faixa_6a20)
            targets['acertos_combinacao_fixa'].append(param_atual.acertos_combinacao_fixa)
        
        X = np.array(features)
        
        # Normaliza features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['features'] = scaler
        
        # Treina um modelo para cada parâmetro
        resultados_treinamento = {}
        
        for param_name, y in targets.items():
            self.logger.info(f"   Treinando modelo para: {param_name}")
            
            y = np.array(y)
            
            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Treina múltiplos modelos e escolhe o melhor
            modelos = {
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'NeuralNetwork': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
            }
            
            melhor_modelo = None
            melhor_score = float('-inf')
            
            for nome_modelo, modelo in modelos.items():
                try:
                    # Treina modelo
                    modelo.fit(X_train, y_train)
                    
                    # Avalia performance
                    score = modelo.score(X_test, y_test)
                    y_pred = modelo.predict(X_test)
                    mae = mean_absolute_error(y_test, y_pred)
                    
                    self.logger.info(f"      {nome_modelo}: R²={score:.3f}, MAE={mae:.3f}")
                    
                    if score > melhor_score:
                        melhor_score = score
                        melhor_modelo = modelo
                        melhor_nome = nome_modelo
                
                except Exception as e:
                    self.logger.warning(f"      Erro no {nome_modelo}: {e}")
                    continue
            
            if melhor_modelo:
                self.modelos_treinados[param_name] = melhor_modelo
                resultados_treinamento[param_name] = {
                    'modelo': melhor_nome,
                    'score': melhor_score,
                    'mae': mae
                }
                self.logger.info(f"   [OK] Melhor modelo para {param_name}: {melhor_nome} (R²={melhor_score:.3f})")
        
        # Salva modelos treinados
        self._salvar_modelos()
        
        self.logger.info(f"Treinamento concluido para {len(self.modelos_treinados)} parametros")
        return resultados_treinamento
    
    def _treinar_modelos_estatisticos(self):
        """Treina modelos estatísticos simples quando ML não está disponível"""
        self.logger.info("Treinando modelos estatisticos...")
        
        # Calcula médias e tendências para cada parâmetro
        modelos_stats = {}
        
        for i, param in enumerate(['maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo',
                                  'n1', 'n15', 'faixa_6a25', 'faixa_6a20', 'acertos_combinacao_fixa']):
            
            valores = [getattr(p, param) for p in self.dados_historicos[-100:]]  # Últimos 100
            
            modelos_stats[param] = {
                'media': np.mean(valores),
                'std': np.std(valores),
                'tendencia': np.polyfit(range(len(valores)), valores, 1)[0],  # Slope
                'min': np.min(valores),
                'max': np.max(valores)
            }
        
        self.modelos_treinados = modelos_stats
        return modelos_stats
    
    def _salvar_modelos(self):
        """Salva modelos treinados"""
        dados_modelo = {
            'modelos': self.modelos_treinados,
            'scalers': self.scalers,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.arquivo_modelos, 'wb') as f:
            pickle.dump(dados_modelo, f)
        
        self.logger.info(f"Modelos salvos em {self.arquivo_modelos}")
    
    def _carregar_modelos(self):
        """Carrega modelos salvos"""
        if not os.path.exists(self.arquivo_modelos):
            return False
        
        try:
            with open(self.arquivo_modelos, 'rb') as f:
                dados_modelo = pickle.load(f)
            
            self.modelos_treinados = dados_modelo['modelos']
            self.scalers = dados_modelo.get('scalers', {})
            
            self.logger.info(f"Modelos carregados de {self.arquivo_modelos}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelos: {e}")
            return False
    
    def prever_parametros(self, concurso_alvo: int) -> PredicaoParametros:
        """Prevê os 8 parâmetros para um concurso específico"""
        if not self.modelos_treinados:
            self.logger.error("Nenhum modelo treinado disponível")
            return None
        
        if not self.dados_historicos:
            self.logger.error("Nenhum dado histórico disponível")
            return None
        
        self.logger.info(f"Prevendo parametros para concurso {concurso_alvo}...")
        
        if ML_DISPONIVEL and 'features' in self.scalers:
            return self._prever_com_ml(concurso_alvo)
        else:
            return self._prever_com_estatistica(concurso_alvo)
    
    def _prever_com_ml(self, concurso_alvo: int) -> PredicaoParametros:
        """Predição usando modelos de ML"""
        # Prepara features dos últimos 5 concursos
        janela = 5
        feature_row = []
        
        for i in range(len(self.dados_historicos) - janela, len(self.dados_historicos)):
            param = self.dados_historicos[i]
            feature_row.extend([
                param.maior_que_ultimo,
                param.menor_que_ultimo,
                param.igual_ao_ultimo,
                param.n1,
                param.n15,
                param.faixa_6a25,
                param.faixa_6a20,
                param.acertos_combinacao_fixa
            ])
        
        X = np.array([feature_row])
        X_scaled = self.scalers['features'].transform(X)
        
        # Faz predições para cada parâmetro
        predicoes = {}
        confiancas = []
        
        for param_name, modelo in self.modelos_treinados.items():
            try:
                pred = modelo.predict(X_scaled)[0]
                predicoes[param_name] = max(0, round(pred))  # Não pode ser negativo
                
                # Estima confiança baseada na variação histórica
                valores_historicos = [getattr(p, param_name) for p in self.dados_historicos[-50:]]
                std_historica = np.std(valores_historicos)
                confianca = max(0.1, 1.0 - (std_historica / np.mean(valores_historicos)))
                confiancas.append(confianca)
                
            except Exception as e:
                self.logger.warning(f"Erro na predição de {param_name}: {e}")
                # Fallback para média
                valores_historicos = [getattr(p, param_name) for p in self.dados_historicos[-20:]]
                predicoes[param_name] = round(np.mean(valores_historicos))
                confiancas.append(0.5)
        
        # ✅ CORREÇÃO: Garantir que maior_que + menor_que + igual_que = 15
        maior_pred = predicoes.get('maior_que_ultimo', 0)
        menor_pred = predicoes.get('menor_que_ultimo', 0)
        igual_pred = predicoes.get('igual_ao_ultimo', 0)
        
        soma_comparacao = maior_pred + menor_pred + igual_pred
        
        if soma_comparacao != 15:
            self.logger.warning(f"🔧 CORREÇÃO: Soma dos parâmetros de comparação = {soma_comparacao} ≠ 15")
            self.logger.warning(f"   Original: maior_que={maior_pred}, menor_que={menor_pred}, igual_que={igual_pred}")
            
            # Estratégia: Manter maior_que e menor_que, ajustar igual_que
            igual_corrigido = 15 - maior_pred - menor_pred
            
            # Se igual_que ficar negativo, redistributir proporcionalmente
            if igual_corrigido < 0:
                # Redistribuir proporcionalmente
                total_original = maior_pred + menor_pred
                if total_original > 0:
                    fator = 14 / total_original  # Deixa 1 para igual_que
                    maior_pred = max(0, round(maior_pred * fator))
                    menor_pred = max(0, round(menor_pred * fator))
                    igual_corrigido = 15 - maior_pred - menor_pred
                else:
                    # Fallback: distribuição equilibrada
                    maior_pred = 5
                    menor_pred = 5
                    igual_corrigido = 5
            
            # Se ainda não bater, ajuste fino
            if maior_pred + menor_pred + igual_corrigido != 15:
                diferenca = 15 - (maior_pred + menor_pred + igual_corrigido)
                igual_corrigido += diferenca
            
            # Atualiza predições corrigidas
            predicoes['maior_que_ultimo'] = max(0, maior_pred)
            predicoes['menor_que_ultimo'] = max(0, menor_pred)
            predicoes['igual_ao_ultimo'] = max(0, igual_corrigido)
            
            self.logger.info(f"   Corrigido: maior_que={maior_pred}, menor_que={menor_pred}, igual_que={igual_corrigido}")
            self.logger.info(f"   ✅ Nova soma: {maior_pred + menor_pred + igual_corrigido} = 15")
        
        confianca_media = np.mean(confiancas)
        
        return PredicaoParametros(
            concurso_alvo=concurso_alvo,
            maior_que_ultimo=predicoes.get('maior_que_ultimo', 0),
            menor_que_ultimo=predicoes.get('menor_que_ultimo', 0),
            igual_ao_ultimo=predicoes.get('igual_ao_ultimo', 0),
            n1=predicoes.get('n1', 1),
            n15=predicoes.get('n15', 25),
            faixa_6a25=predicoes.get('faixa_6a25', 10),
            faixa_6a20=predicoes.get('faixa_6a20', 8),
            acertos_combinacao_fixa=predicoes.get('acertos_combinacao_fixa', 0),
            confianca=confianca_media,
            timestamp=datetime.now().isoformat()
        )
    
    def _prever_com_estatistica(self, concurso_alvo: int) -> PredicaoParametros:
        """Predição usando modelos estatísticos"""
        predicoes = {}
        
        for param_name, stats in self.modelos_treinados.items():
            # Predição baseada em média + tendência
            media = stats['media']
            tendencia = stats['tendencia']
            
            # Projeta tendência para próximo concurso
            predicao = media + tendencia
            
            # Aplica limites
            predicao = max(stats['min'], min(stats['max'], predicao))
            predicoes[param_name] = round(predicao)
        
        return PredicaoParametros(
            concurso_alvo=concurso_alvo,
            maior_que_ultimo=predicoes.get('maior_que_ultimo', 0),
            menor_que_ultimo=predicoes.get('menor_que_ultimo', 0),
            igual_ao_ultimo=predicoes.get('igual_ao_ultimo', 0),
            n1=predicoes.get('n1', 1),
            n15=predicoes.get('n15', 25),
            faixa_6a25=predicoes.get('faixa_6a25', 10),
            faixa_6a20=predicoes.get('faixa_6a20', 8),
            acertos_combinacao_fixa=predicoes.get('acertos_combinacao_fixa', 0),
            confianca=0.7,  # Confiança moderada para estatística
            timestamp=datetime.now().isoformat()
        )
    
    def executar_analise_completa(self, concurso_alvo: int = None):
        """Executa análise completa: carregamento, processamento, treinamento e predição"""
        self.logger.info("INICIANDO ANALISE PREDITIVA ESPECIALIZADA")
        self.logger.info("="*60)
        
        # 1. Carrega ou processa dados
        if not self._carregar_dados_processados():
            self.logger.info("Processando dados historicos...")
            if not self.processar_dados_historicos():
                self.logger.error("Falha no processamento de dados")
                return False
        
        # 2. Análise de correlações
        self.logger.info("Analisando correlacoes...")
        correlacoes = self.analisar_correlacoes()
        
        # 3. Treinamento de modelos
        if not self._carregar_modelos():
            self.logger.info("Treinando modelos preditivos...")
            resultados = self.treinar_modelos_preditivos()
            if not resultados:
                self.logger.error("Falha no treinamento")
                return False
        
        # 4. Predição
        if concurso_alvo is None:
            ultimo_concurso = self.dados_historicos[-1].concurso
            concurso_alvo = ultimo_concurso + 1
        
        self.logger.info(f"Gerando predicao para concurso {concurso_alvo}...")
        predicao = self.prever_parametros(concurso_alvo)
        
        if predicao:
            self._exibir_resultados(predicao)
            self._salvar_predicao(predicao)
            
        self.logger.info("Analise completa finalizada!")
        return True
    
    def _exibir_resultados(self, predicao: PredicaoParametros):
        """Exibe resultados da predição"""
        print("\n" + "="*60)
        print(f"🎯 PREDIÇÃO PARA CONCURSO {predicao.concurso_alvo}")
        print("="*60)
        
        print(f"\n📊 PARÂMETROS PREVISTOS:")
        print(f"   🔺 maior_que_ultimo: {predicao.maior_que_ultimo}")
        print(f"   🔻 menor_que_ultimo: {predicao.menor_que_ultimo}")
        print(f"   ⚖️  igual_ao_ultimo: {predicao.igual_ao_ultimo}")
        print(f"   1️⃣  N1 (menor): {predicao.n1}")
        print(f"   🔟 N15 (maior): {predicao.n15}")
        print(f"   📊 Faixa 6-25: {predicao.faixa_6a25}")
        print(f"   📈 Faixa 6-20: {predicao.faixa_6a20}")
        print(f"   🎯 Acertos combinação fixa: {predicao.acertos_combinacao_fixa}")
        
        print(f"\n📈 Confiança: {predicao.confianca:.1%}")
        print(f"⏰ Gerado em: {predicao.timestamp}")
        
        print("\n💡 COMBINAÇÃO FIXA DE REFERÊNCIA:")
        print(f"   {self.combinacao_fixa}")
    
    def _salvar_predicao(self, predicao: PredicaoParametros):
        """Salva predição em arquivo"""
        arquivo_predicao = f"predicao_parametros_{predicao.concurso_alvo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(arquivo_predicao, 'w') as f:
            json.dump(asdict(predicao), f, indent=2)
        
        self.logger.info(f"Predicao salva em {arquivo_predicao}")

def main():
    """Função principal com menu interativo"""
    print("🎯 SISTEMA DE ANÁLISE PREDITIVA ESPECIALIZADO")
    print("="*60)
    print("Análise dos 8 parâmetros específicos:")
    print("1. maior_que_ultimo  2. menor_que_ultimo  3. igual_ao_ultimo")
    print("4. N1 (menor)        5. N15 (maior)       6. Faixa 6-25")  
    print("7. Faixa 6-20        8. Acertos combinação (1,2,4,6,8,9,11,13,15,16,19,20,22,24,25)")
    print("="*60)
    
    try:
        # Menu de opções
        while True:
            print("\n🎯 MENU PRINCIPAL:")
            print("="*40)
            print("1. 🚀 Executar análise automática (próximo concurso)")
            print("2. 🎲 Escolher concurso para predição")
            print("3. ✅ Validar predição existente")
            print("4. 📊 Listar predições salvas")
            print("0. ❌ Sair")
            
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "1":
                # Modo automático
                config_db = None
                concurso_alvo = None
                print("\n📊 Executando análise automática...")
                
                analisador = AnalisadorPreditivoEspecializado(config_db)
                sucesso = analisador.executar_analise_completa(concurso_alvo)
                
                if sucesso:
                    print("\n🏆 ANÁLISE CONCLUÍDA COM SUCESSO!")
                else:
                    print("\n❌ Erro na análise")
                    
            elif opcao == "2":
                # Escolher concurso
                config_db = None
                
                print("\n🎲 ESCOLHA DO CONCURSO:")
                concurso_input = input("Digite o número do concurso para predição: ").strip()
                
                try:
                    concurso_alvo = int(concurso_input)
                    print(f"🎯 Concurso alvo: {concurso_alvo}")
                    
                    analisador = AnalisadorPreditivoEspecializado(config_db)
                    sucesso = analisador.executar_analise_completa(concurso_alvo)
                    
                    if sucesso:
                        print(f"\n🏆 PREDIÇÃO PARA CONCURSO {concurso_alvo} CONCLUÍDA!")
                    else:
                        print("\n❌ Erro na análise")
                        
                except ValueError:
                    print("❌ Número de concurso inválido!")
                    
            elif opcao == "3":
                # Validar predição
                print("\n✅ VALIDAÇÃO DE PREDIÇÃO:")
                validar_predicao_interativa()
                
            elif opcao == "4":
                # Listar predições
                print("\n📊 PREDIÇÕES SALVAS:")
                listar_predicoes_salvas()
                
            elif opcao == "0":
                print("👋 Saindo...")
                break
                
            else:
                print("❌ Opção inválida!")
                
            input("\nPressione Enter para continuar...")
                
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

def validar_predicao_interativa():
    """Validação interativa de predições"""
    try:
        import json
        import os
        from glob import glob
        
        # Busca arquivos de predição
        arquivos_predicao = glob("predicao_parametros_*.json")
        
        if not arquivos_predicao:
            print("❌ Nenhuma predição encontrada!")
            return
            
        print(f"📁 Encontradas {len(arquivos_predicao)} predições:")
        for i, arq in enumerate(arquivos_predicao[-10:], 1):
            print(f"   {i}. {arq}")
        
        # Escolha do arquivo
        while True:
            escolha = input("\nEscolha o arquivo (número) ou digite o concurso: ").strip()
            
            try:
                if escolha.isdigit() and int(escolha) <= len(arquivos_predicao):
                    # Escolha por índice
                    arquivo_escolhido = arquivos_predicao[int(escolha) - 1]
                    break
                else:
                    # Busca por concurso
                    concurso = int(escolha)
                    arquivos_concurso = [arq for arq in arquivos_predicao if f"_{concurso}_" in arq]
                    
                    if arquivos_concurso:
                        arquivo_escolhido = arquivos_concurso[0]
                        break
                    else:
                        print(f"❌ Nenhuma predição encontrada para concurso {concurso}")
                        continue
            except ValueError:
                print("❌ Entrada inválida!")
                continue
        
        # Carrega predição
        with open(arquivo_escolhido, 'r') as f:
            predicao = json.load(f)
        
        concurso_alvo = predicao.get('concurso_alvo', 'N/A')
        
        # Extrai parâmetros (podem estar em 'parametros_preditos' ou no primeiro nível)
        parametros_preditos = predicao.get('parametros_preditos', {})
        
        if not parametros_preditos:
            # Se não tem 'parametros_preditos', extrai do primeiro nível
            parametros_preditos = {
                'maior_que_ultimo': predicao.get('maior_que_ultimo'),
                'menor_que_ultimo': predicao.get('menor_que_ultimo'),
                'igual_ao_ultimo': predicao.get('igual_ao_ultimo'),
                'n1': predicao.get('n1'),
                'n15': predicao.get('n15'),
                'faixa_6a25': predicao.get('faixa_6a25'),
                'faixa_6a20': predicao.get('faixa_6a20'),
                'acertos_combinacao_fixa': predicao.get('acertos_combinacao_fixa')
            }
            
            # Remove valores None
            parametros_preditos = {k: v for k, v in parametros_preditos.items() if v is not None}
        
        print(f"\n🎯 PREDIÇÃO CARREGADA - CONCURSO {concurso_alvo}")
        print("="*50)
        print("📊 PARÂMETROS PREDITOS:")
        for param, valor in parametros_preditos.items():
            print(f"   {param}: {valor}")
        
        # Solicita resultado real
        print(f"\n🎲 RESULTADO REAL DO CONCURSO {concurso_alvo}:")
        resultado_input = input("Digite os 15 números sorteados (separados por vírgula): ").strip()
        
        try:
            numeros_reais = [int(x.strip()) for x in resultado_input.split(",")]
            
            if len(numeros_reais) != 15:
                print("❌ Devem ser exatamente 15 números!")
                return
                
            # Valida com ValidadorPredicoes (critério EXATO)
            from validador_predicoes_especializado import ValidadorPredicoes
            validador = ValidadorPredicoes()
            
            resultado_validacao = validador.validar_predicao_manual(
                parametros_preditos, numeros_reais, concurso_alvo
            )
            
            if resultado_validacao is None:
                print("❌ Erro na validação - resultado inválido")
                return
            
            print(f"\n🎯 RESULTADO DA VALIDAÇÃO:")
            print("="*60)
            print(f"⚙️ Critério: {resultado_validacao.get('criterio_usado', 'EXATO')}")
            
            # Validação da regra dos 15
            validacao_15 = resultado_validacao.get('validacao_15', False)
            status_15 = "✅ CORRETA" if validacao_15 else "❌ INCORRETA"
            print(f"🧮 Regra dos 15: {status_15}")
            
            print(f"📊 ACERTOS POR PARÂMETRO:")
            
            total_acertos = resultado_validacao.get('acertos_total', 0)
            total_parametros = resultado_validacao.get('parametros_total', 1)
            detalhes = resultado_validacao.get('detalhes', {})
            
            if not detalhes:
                print("❌ Nenhum detalhe de validação disponível")
                return
            
            # Separar parâmetros por categoria
            comparacao_params = ['maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo']
            diretos_params = ['n1', 'n15', 'faixa_6a25', 'faixa_6a20', 'acertos_combinacao_fixa']
            
            # Mostrar parâmetros de comparação primeiro
            print(f"\n   📊 PARÂMETROS DE COMPARAÇÃO:")
            soma_comparacao = 0
            for param in comparacao_params:
                if param in detalhes:
                    detalhes_param = detalhes[param]
                    acertou = detalhes_param.get('acertou', False)
                    predito = detalhes_param.get('valor_predito', 'N/A')
                    real = detalhes_param.get('valor_real', 'N/A')
                    avaliacao = detalhes_param.get('avaliacao', 'N/A')
                    
                    status = "✅ ACERTOU" if acertou else "❌ ERROU"
                    print(f"     {param}: {status}")
                    print(f"        Predito: {predito} | Real: {real} | {avaliacao}")
                    
                    if isinstance(real, int):
                        soma_comparacao += real
            
            print(f"     📊 Soma: maior_que + menor_que + igual_que = {soma_comparacao}/15")
            
            # Mostrar parâmetros diretos
            print(f"\n   🎯 PARÂMETROS DIRETOS:")
            for param in diretos_params:
                if param in detalhes:
                    detalhes_param = detalhes[param]
                    acertou = detalhes_param.get('acertou', False)
                    predito = detalhes_param.get('valor_predito', 'N/A')
                    real = detalhes_param.get('valor_real', 'N/A')
                    avaliacao = detalhes_param.get('avaliacao', 'N/A')
                    
                    status = "✅ ACERTOU" if acertou else "❌ ERROU"
                    print(f"     {param}: {status}")
                    print(f"        Predito: {predito} | Real: {real} | {avaliacao}")
            
            print(f"\n� RESUMO FINAL:")
            print(f"   🎯 Total de acertos: {total_acertos}/{total_parametros}")
            
            if total_parametros > 0:
                taxa_sucesso = (total_acertos/total_parametros)*100
                print(f"   � Taxa de sucesso: {taxa_sucesso:.1f}%")
                
                # Avaliação com critério EXATO
                if total_acertos >= 7:
                    print("   🏆 PREDIÇÃO EXCELENTE!")
                elif total_acertos >= 5:
                    print("   👍 PREDIÇÃO BOA!")
                elif total_acertos >= 3:
                    print("   😐 PREDIÇÃO REGULAR")
                elif total_acertos >= 1:
                    print("   👎 PREDIÇÃO FRACA")
                else:
                    print("   � PREDIÇÃO MUITO RUIM")
            else:
                print("   ❌ Erro: nenhum parâmetro validado")
                
        except ValueError:
            print("❌ Formato de números inválido!")
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            
    except Exception as e:
        print(f"❌ Erro na validação interativa: {e}")

def listar_predicoes_salvas():
    """Lista todas as predições salvas"""
    try:
        from glob import glob
        import json
        import os
        
        arquivos_predicao = glob("predicao_parametros_*.json")
        
        if not arquivos_predicao:
            print("❌ Nenhuma predição encontrada!")
            return
            
        arquivos_predicao.sort(reverse=True)  # Mais recentes primeiro
        
        print(f"📁 PREDIÇÕES SALVAS ({len(arquivos_predicao)} total):")
        print("="*60)
        
        for i, arquivo in enumerate(arquivos_predicao[:20], 1):  # Mostra últimas 20
            try:
                with open(arquivo, 'r') as f:
                    dados = json.load(f)
                
                concurso = dados.get('concurso_alvo', 'N/A')
                confianca = dados.get('confianca_media', 0)
                timestamp = dados.get('timestamp', 'N/A')
                
                # Extrai data do timestamp ou nome do arquivo
                if timestamp != 'N/A':
                    data = timestamp[:10]
                else:
                    # Extrai do nome do arquivo se possível
                    parts = arquivo.split('_')
                    if len(parts) >= 3:
                        data_str = parts[-1].replace('.json', '')
                        if len(data_str) >= 8:
                            data = f"{data_str[:4]}-{data_str[4:6]}-{data_str[6:8]}"
                        else:
                            data = "N/A"
                    else:
                        data = "N/A"
                
                print(f"   {i:2d}. Concurso {concurso} | Confiança: {confianca:.1f}% | Data: {data}")
                
            except Exception as e:
                print(f"   {i:2d}. {arquivo} (erro ao ler: {e})")
                
        if len(arquivos_predicao) > 20:
            print(f"   ... e mais {len(arquivos_predicao) - 20} predições")
            
    except Exception as e:
        print(f"❌ Erro ao listar predições: {e}")
        
        if sucesso:
            print("\n🏆 ANÁLISE CONCLUÍDA COM SUCESSO!")
        else:
            print("\n❌ Erro na análise")
            
    except KeyboardInterrupt:
        print("\n🛑 Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()