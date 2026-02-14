"""
Sistema de Predição Inteligente com Aprendizado Contínuo
========================================================

Este sistema:
1. Armazena todas as predições feitas
2. Analisa acertos quando novos sorteios chegam
3. Aprende com os resultados para melhorar predições futuras
4. Meta: ≥ 11 acertos por jogo

Autor: Sistema LotoScope
Data: 07/11/2025
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('predicao_inteligente.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Predicao:
    """Classe para armazenar dados de uma predição"""
    id: str
    timestamp: str
    numeros_preditos: List[int]
    confiancas: List[float]
    confianca_media: float
    metodo_usado: str
    parametros_ml: Dict
    concurso_alvo: int
    acertos: Optional[int] = None
    numeros_sorteados: Optional[List[int]] = None
    data_verificacao: Optional[str] = None
    feedback_aplicado: bool = False

@dataclass
class ResultadoAprendizado:
    """Resultado de uma sessão de aprendizado"""
    timestamp: str
    predicoes_analisadas: int
    acertos_medios: float
    melhor_acerto: int
    pior_acerto: int
    ajustes_realizados: Dict
    meta_alcancada: bool

class SistemaPredicaoInteligente:
    """Sistema principal de predição com aprendizado contínuo"""
    
    def __init__(self, db_path: str = "predicoes_inteligentes.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.meta_acertos = 11  # Meta de acertos
        
        # Arquivos de controle
        self.arquivo_predicoes = "historico_predicoes.json"
        self.arquivo_aprendizado = "conhecimento_predicao.json"
        self.arquivo_modelos = "modelos_otimizados.pkl"
        
        # Conhecimento do sistema
        self.conhecimento = self._carregar_conhecimento()
        self.modelos_otimizados = self._carregar_modelos()
        
        # Inicializar banco
        self._inicializar_banco()
        
        self.logger.info("🧠 Sistema de Predição Inteligente inicializado")
        self.logger.info(f"🎯 Meta de acertos: {self.meta_acertos}")
        
    def _inicializar_banco(self):
        """Inicializa o banco de dados para armazenar predições"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de predições
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predicoes (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    numeros_preditos TEXT NOT NULL,
                    confiancas TEXT NOT NULL,
                    confianca_media REAL NOT NULL,
                    metodo_usado TEXT NOT NULL,
                    parametros_ml TEXT NOT NULL,
                    concurso_alvo INTEGER NOT NULL,
                    acertos INTEGER,
                    numeros_sorteados TEXT,
                    data_verificacao TEXT,
                    feedback_aplicado BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabela de aprendizado
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessoes_aprendizado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    predicoes_analisadas INTEGER NOT NULL,
                    acertos_medios REAL NOT NULL,
                    melhor_acerto INTEGER NOT NULL,
                    pior_acerto INTEGER NOT NULL,
                    ajustes_realizados TEXT NOT NULL,
                    meta_alcancada BOOLEAN NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("✅ Banco de dados inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar banco: {e}")
            
    def _carregar_conhecimento(self) -> Dict:
        """Carrega conhecimento acumulado do sistema"""
        try:
            if Path(self.arquivo_aprendizado).exists():
                with open(self.arquivo_aprendizado, 'r', encoding='utf-8') as f:
                    conhecimento = json.load(f)
                self.logger.info(f"📚 Conhecimento carregado: {len(conhecimento.get('historico_ajustes', []))} ajustes")
                return conhecimento
            else:
                return {
                    'versao': '1.0',
                    'total_predicoes': 0,
                    'total_acertos': 0,
                    'melhor_acerto_historico': 0,
                    'historico_ajustes': [],
                    'padroes_descobertos': {},
                    'pesos_posicionais': {f'N{i}': 1.0 for i in range(1, 16)},
                    'fatores_correcao': {},
                    'ultima_atualizacao': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar conhecimento: {e}")
            return {}
            
    def _salvar_conhecimento(self):
        """Salva conhecimento atualizado"""
        try:
            self.conhecimento['ultima_atualizacao'] = datetime.now().isoformat()
            with open(self.arquivo_aprendizado, 'w', encoding='utf-8') as f:
                json.dump(self.conhecimento, f, indent=2, ensure_ascii=False)
            self.logger.info("💾 Conhecimento salvo")
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar conhecimento: {e}")
            
    def _carregar_modelos(self) -> Dict:
        """Carrega modelos ML otimizados"""
        try:
            if Path(self.arquivo_modelos).exists():
                with open(self.arquivo_modelos, 'rb') as f:
                    modelos = pickle.load(f)
                self.logger.info("🤖 Modelos otimizados carregados")
                return modelos
            else:
                return {}
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar modelos: {e}")
            return {}
            
    def _salvar_modelos(self):
        """Salva modelos ML otimizados"""
        try:
            with open(self.arquivo_modelos, 'wb') as f:
                pickle.dump(self.modelos_otimizados, f)
            self.logger.info("🤖 Modelos otimizados salvos")
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar modelos: {e}")
            
    def conectar_banco_sorteios(self):
        """Conecta ao banco principal de sorteios"""
        try:
            # Importar configuração do banco
            import sys
            sys.path.append('lotofacil_lite')
            from database_config import db_config
            
            conn = db_config.get_connection()
            if conn:
                self.logger.info("✅ Conectado ao banco de sorteios")
            return conn
            
        except Exception as e:
            self.logger.error(f"❌ Erro na conexão: {e}")
            return None
            
    def obter_ultimo_concurso(self) -> Optional[int]:
        """Obtém o número do último concurso disponível"""
        try:
            conn = self.conectar_banco_sorteios()
            if not conn:
                return None
                
            # Tentar diferentes nomes de tabela
            tabelas_possiveis = ['lotofacil_resultados', 'Resultados_INT', 'resultados']
            
            for tabela in tabelas_possiveis:
                try:
                    query = f"SELECT MAX(Concurso) FROM {tabela}"
                    df = pd.read_sql_query(query, conn)
                    ultimo_concurso = df.iloc[0, 0]
                    
                    if ultimo_concurso and ultimo_concurso > 0:
                        conn.close()
                        self.logger.info(f"🎲 Último concurso: {ultimo_concurso}")
                        return ultimo_concurso
                except:
                    continue
            
            conn.close()
            self.logger.warning("⚠️ Nenhuma tabela de resultados encontrada")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter último concurso: {e}")
            return None
            
    def obter_resultado_concurso(self, concurso: int) -> Optional[List[int]]:
        """Obtém resultado de um concurso específico"""
        try:
            conn = self.conectar_banco_sorteios()
            if not conn:
                return None
                
            # Tentar diferentes nomes de tabela e estruturas
            tentativas = [
                # Estrutura original
                {
                    'tabela': 'lotofacil_resultados',
                    'query': f"""
                        SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                        FROM lotofacil_resultados 
                        WHERE Concurso = {concurso}
                    """
                },
                # Estrutura Resultados_INT
                {
                    'tabela': 'Resultados_INT',
                    'query': f"""
                        SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                        FROM Resultados_INT 
                        WHERE Concurso = {concurso}
                    """
                },
                # Estrutura genérica resultados
                {
                    'tabela': 'resultados',
                    'query': f"""
                        SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                        FROM resultados 
                        WHERE Concurso = {concurso}
                    """
                }
            ]
            
            for tentativa in tentativas:
                try:
                    df = pd.read_sql_query(tentativa['query'], conn)
                    
                    if len(df) > 0:
                        numeros = df.iloc[0].tolist()
                        conn.close()
                        self.logger.info(f"🎯 Resultado concurso {concurso}: {numeros}")
                        return numeros
                        
                except Exception:
                    continue
            
            conn.close()
            self.logger.warning(f"⚠️ Concurso {concurso} não encontrado")
            return None
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter resultado: {e}")
            return None
            
    def gerar_predicao_inteligente(self, usar_conhecimento: bool = True) -> Predicao:
        """Gera uma predição usando análise posicional avançada (método original otimizado)"""
        self.logger.info("🔮 Gerando predição inteligente baseada em análise posicional...")
        
        try:
            # Obter último concurso para definir alvo
            ultimo_concurso = self.obter_ultimo_concurso()
            if not ultimo_concurso:
                raise Exception("Não foi possível obter último concurso")
                
            concurso_alvo = ultimo_concurso + 1
            
            # Carregar dados históricos
            conn = self.conectar_banco_sorteios()
            
            # Tentar diferentes tabelas
            tabelas_possiveis = ['Resultados_INT', 'lotofacil_resultados', 'resultados']
            df = None
            
            for tabela in tabelas_possiveis:
                try:
                    # Para SQL Server, usar TOP em vez de LIMIT
                    query = f"""
                        SELECT TOP 500 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                        FROM {tabela}
                        ORDER BY Concurso DESC
                    """
                    df = pd.read_sql_query(query, conn)
                    if len(df) > 0:
                        self.logger.info(f"📊 Dados carregados da tabela: {tabela} ({len(df)} registros)")
                        break
                except Exception as e:
                    self.logger.debug(f"Falha na tabela {tabela}: {e}")
                    continue
            
            conn.close()
            
            if df is None or len(df) == 0:
                raise Exception("Nenhuma tabela de resultados encontrada ou sem dados")
            
            # Ordenar por concurso crescente para análise temporal
            df = df.sort_values('Concurso').reset_index(drop=True)
            
            # ANÁLISE POSICIONAL AVANÇADA COM ML (método original completo)
            periodos = [30, 15, 10, 5, 3]
            posicoes = [f'N{i}' for i in range(1, 16)]
            
            # Gerar predição com ML para cada posição
            numeros_preditos = []
            confiancas = []
            
            self.logger.info("🤖 Iniciando treinamento ML para cada posição...")
            
            for i, pos in enumerate(posicoes, 1):
                self.logger.info(f"🔧 Treinando modelo para {pos}...")
                
                # Preparar dados de treinamento para esta posição específica
                X_treino = []
                y_treino = []
                
                # Criar features baseadas nos períodos de análise
                for idx in range(max(periodos), len(df) - 1):
                    features = []
                    
                    # Features de frequência por período
                    for periodo in periodos:
                        inicio = max(0, idx - periodo + 1)
                        fim = idx + 1
                        subset = df[pos].iloc[inicio:fim]
                        
                        # Frequência de cada número no período
                        for numero in range(1, 26):
                            freq = (subset == numero).sum() / len(subset) if len(subset) > 0 else 0
                            features.append(freq)
                        
                        # Estatísticas do período
                        if len(subset) > 0:
                            features.extend([
                                subset.mean(),           # Média
                                subset.std(),            # Desvio padrão  
                                subset.iloc[-1],         # Último valor
                                (subset == subset.iloc[-1]).sum() / len(subset)  # Freq. do último
                            ])
                        else:
                            features.extend([0, 0, 0, 0])
                    
                    # Features adicionais posicionais
                    features.extend([
                        i,  # Número da posição (1-15)
                        idx,  # Índice temporal
                        df[pos].iloc[:idx].std() if idx > 1 else 0,  # Variabilidade histórica
                    ])
                    
                    # Aplicar conhecimento acumulado
                    if usar_conhecimento:
                        peso_posicional = self.conhecimento.get('pesos_posicionais', {}).get(pos, 1.0)
                        features.append(peso_posicional)
                    else:
                        features.append(1.0)
                    
                    X_treino.append(features)
                    y_treino.append(df[pos].iloc[idx + 1])
                
                X_treino = np.array(X_treino)
                y_treino = np.array(y_treino)
                
                # Treinar ensemble de modelos para esta posição
                if pos in self.modelos_otimizados:
                    modelo_otimizado = self.modelos_otimizados[pos]
                    self.logger.info(f"📁 Modelo carregado para {pos}")
                else:
                    # Criar ensemble de modelos especializados
                    modelos_candidatos = [
                        ('RandomForest', RandomForestRegressor(
                            n_estimators=100, 
                            max_depth=10, 
                            random_state=42,
                            n_jobs=-1
                        )),
                        ('GradientBoosting', GradientBoostingRegressor(
                            n_estimators=100, 
                            max_depth=6, 
                            random_state=42
                        )),
                        ('Linear', LinearRegression()),
                    ]
                    
                    # Testar modelos e escolher o melhor
                    melhor_modelo = None
                    melhor_score = -float('inf')
                    melhor_nome = ""
                    
                    for nome, modelo in modelos_candidatos:
                        try:
                            # Treinar modelo
                            modelo.fit(X_treino, y_treino)
                            
                            # Avaliar performance
                            score = modelo.score(X_treino, y_treino)
                            
                            if score > melhor_score:
                                melhor_score = score
                                melhor_modelo = modelo
                                melhor_nome = nome
                                
                        except Exception as e:
                            self.logger.warning(f"⚠️ Erro no modelo {nome} para {pos}: {e}")
                            continue
                    
                    modelo_otimizado = melhor_modelo
                    self.modelos_otimizados[pos] = modelo_otimizado
                    self.logger.info(f"✅ Melhor modelo para {pos}: {melhor_nome} (Score: {melhor_score:.3f})")
                
                # Preparar features para predição
                features_predicao = []
                
                # Features baseadas nos últimos dados
                for periodo in periodos:
                    ultimos_dados = df[pos].tail(periodo)
                    
                    # Frequência de cada número
                    for numero in range(1, 26):
                        freq = (ultimos_dados == numero).sum() / len(ultimos_dados)
                        features_predicao.append(freq)
                    
                    # Estatísticas do período
                    features_predicao.extend([
                        ultimos_dados.mean(),
                        ultimos_dados.std(),
                        ultimos_dados.iloc[-1],
                        (ultimos_dados == ultimos_dados.iloc[-1]).sum() / len(ultimos_dados)
                    ])
                
                # Features adicionais
                features_predicao.extend([
                    i,  # Posição
                    len(df),  # Índice atual
                    df[pos].std(),  # Variabilidade total
                ])
                
                # Conhecimento acumulado
                if usar_conhecimento:
                    peso_posicional = self.conhecimento.get('pesos_posicionais', {}).get(pos, 1.0)
                    features_predicao.append(peso_posicional)
                else:
                    features_predicao.append(1.0)
                
                # Fazer predição
                try:
                    pred_valor = modelo_otimizado.predict([features_predicao])[0]
                    numero_predito = max(1, min(25, round(pred_valor)))
                    
                    # Calcular confiança baseada na performance do modelo
                    if hasattr(modelo_otimizado, 'score'):
                        confianca_base = max(50.0, modelo_otimizado.score(X_treino, y_treino) * 100)
                    else:
                        confianca_base = 75.0
                    
                    # Ajustar confiança com conhecimento acumulado
                    if usar_conhecimento:
                        fator_correcao = self.conhecimento.get('fatores_correcao', {}).get(pos, 1.0)
                        confianca_final = min(99.9, confianca_base * fator_correcao)
                    else:
                        confianca_final = confianca_base
                    
                    numeros_preditos.append(numero_predito)
                    confiancas.append(confianca_final)
                    
                    self.logger.info(f"🎯 {pos}: {numero_predito} ({confianca_final:.1f}%) - Predição ML: {pred_valor:.2f}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro na predição para {pos}: {e}")
                    # Fallback para análise de frequência simples
                    ultimos_30 = df[pos].tail(30)
                    numero_mais_freq = ultimos_30.mode().iloc[0] if len(ultimos_30.mode()) > 0 else 13
                    numeros_preditos.append(numero_mais_freq)
                    confiancas.append(60.0)
            
            # Ajustar para não ter números repetidos
            numeros_preditos = self._ajustar_numeros_unicos(numeros_preditos, confiancas)
            
            # Criar objeto predição
            predicao = Predicao(
                id=f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now().isoformat(),
                numeros_preditos=numeros_preditos,
                confiancas=confiancas,
                confianca_media=np.mean(confiancas),
                metodo_usado="ML_Posicional_Avancado_v3",
                parametros_ml={
                    "usar_conhecimento": usar_conhecimento,
                    "periodos_analisados": periodos,
                    "modelos_treinados": len(self.modelos_otimizados),
                    "features_por_posicao": len(features_predicao),
                    "peso_medio": np.mean(list(self.conhecimento.get('pesos_posicionais', {}).values())) if self.conhecimento.get('pesos_posicionais') else 1.0,
                    "total_ajustes": len(self.conhecimento.get('historico_ajustes', []))
                },
                concurso_alvo=concurso_alvo
            )
            
            # Salvar predição e modelos otimizados
            self._salvar_predicao(predicao)
            self._salvar_modelos()
            
            self.logger.info(f"✅ Predição gerada: {numeros_preditos}")
            self.logger.info(f"🎯 Confiança média: {predicao.confianca_media:.1f}%")
            self.logger.info(f"🎲 Concurso alvo: {concurso_alvo}")
            self.logger.info(f"🤖 Modelos treinados e salvos para todas as posições")
            
            return predicao
            
        except Exception as e:
            self.logger.error(f"❌ Erro na predição: {e}")
            raise
            
    def _ajustar_numeros_unicos(self, numeros: List[int], confiancas: List[float]) -> List[int]:
        """Ajusta a lista para ter apenas números únicos"""
        numeros_unicos = []
        usados = set()
        
        # Ordenar por confiança (maior primeiro)
        indices_ordenados = sorted(range(len(confiancas)), key=lambda i: confiancas[i], reverse=True)
        
        for idx in indices_ordenados:
            numero = numeros[idx]
            
            if numero not in usados:
                numeros_unicos.append((idx, numero))
                usados.add(numero)
        
        # Preencher posições restantes
        for idx in range(15):
            if idx not in [x[0] for x in numeros_unicos]:
                # Encontrar número disponível próximo ao original
                numero_original = numeros[idx]
                for offset in range(1, 26):
                    for sinal in [1, -1]:
                        novo_numero = numero_original + (offset * sinal)
                        if 1 <= novo_numero <= 25 and novo_numero not in usados:
                            numeros_unicos.append((idx, novo_numero))
                            usados.add(novo_numero)
                            break
                    if len(numeros_unicos) > len([x for x in numeros_unicos if x[0] <= idx]):
                        break
        
        # Reordenar por posição
        numeros_unicos.sort(key=lambda x: x[0])
        return [x[1] for x in numeros_unicos]
        
    def _salvar_predicao(self, predicao: Predicao):
        """Salva predição no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predicoes (
                    id, timestamp, numeros_preditos, confiancas, confianca_media,
                    metodo_usado, parametros_ml, concurso_alvo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                predicao.id,
                predicao.timestamp,
                json.dumps(predicao.numeros_preditos),
                json.dumps(predicao.confiancas),
                predicao.confianca_media,
                predicao.metodo_usado,
                json.dumps(predicao.parametros_ml),
                predicao.concurso_alvo
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"💾 Predição salva: {predicao.id}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar predição: {e}")
            
    def verificar_resultados_predicoes(self) -> List[Tuple[Predicao, int]]:
        """Verifica resultados de predições pendentes"""
        self.logger.info("🔍 Verificando resultados de predições...")
        
        resultados = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar predições sem verificação
            cursor.execute('''
                SELECT id, timestamp, numeros_preditos, confiancas, confianca_media,
                       metodo_usado, parametros_ml, concurso_alvo
                FROM predicoes 
                WHERE acertos IS NULL
                ORDER BY timestamp DESC
            ''')
            
            predicoes_pendentes = cursor.fetchall()
            conn.close()
            
            for linha in predicoes_pendentes:
                predicao = Predicao(
                    id=linha[0],
                    timestamp=linha[1],
                    numeros_preditos=json.loads(linha[2]),
                    confiancas=json.loads(linha[3]),
                    confianca_media=linha[4],
                    metodo_usado=linha[5],
                    parametros_ml=json.loads(linha[6]),
                    concurso_alvo=linha[7]
                )
                
                # Verificar se resultado está disponível
                numeros_sorteados = self.obter_resultado_concurso(predicao.concurso_alvo)
                
                if numeros_sorteados:
                    # Calcular acertos
                    acertos = len(set(predicao.numeros_preditos) & set(numeros_sorteados))
                    
                    # Atualizar predição
                    predicao.acertos = acertos
                    predicao.numeros_sorteados = numeros_sorteados
                    predicao.data_verificacao = datetime.now().isoformat()
                    
                    self._atualizar_predicao_com_resultado(predicao)
                    resultados.append((predicao, acertos))
                    
                    self.logger.info(f"✅ Concurso {predicao.concurso_alvo}: {acertos} acertos")
                    self.logger.info(f"   Preditos: {predicao.numeros_preditos}")
                    self.logger.info(f"   Sorteados: {numeros_sorteados}")
                    
                    # Verificar se alcançou a meta
                    if acertos >= self.meta_acertos:
                        self.logger.info(f"🎉 META ALCANÇADA! {acertos} acertos!")
            
            if resultados:
                # Aplicar aprendizado
                self._aplicar_aprendizado(resultados)
                
        except Exception as e:
            self.logger.error(f"❌ Erro na verificação: {e}")
            
        return resultados
        
    def _atualizar_predicao_com_resultado(self, predicao: Predicao):
        """Atualiza predição com resultado real"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE predicoes 
                SET acertos = ?, numeros_sorteados = ?, data_verificacao = ?
                WHERE id = ?
            ''', (
                predicao.acertos,
                json.dumps(predicao.numeros_sorteados),
                predicao.data_verificacao,
                predicao.id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar predição: {e}")
            
    def _aplicar_aprendizado(self, resultados: List[Tuple[Predicao, int]]):
        """Aplica aprendizado baseado nos resultados"""
        self.logger.info("🧠 Aplicando aprendizado...")
        
        try:
            ajustes_realizados = {}
            
            for predicao, acertos in resultados:
                # Analisar por posição
                for i, (num_predito, num_real) in enumerate(zip(predicao.numeros_preditos, predicao.numeros_sorteados)):
                    pos = f'N{i+1}'
                    
                    # Ajustar peso posicional
                    if num_predito == num_real:
                        # Acerto: aumentar peso
                        self.conhecimento['pesos_posicionais'][pos] *= 1.1
                        ajustes_realizados[f'{pos}_peso'] = 'aumentado'
                    else:
                        # Erro: diminuir peso
                        self.conhecimento['pesos_posicionais'][pos] *= 0.95
                        ajustes_realizados[f'{pos}_peso'] = 'diminuido'
                    
                    # Limitar pesos
                    self.conhecimento['pesos_posicionais'][pos] = max(0.1, min(2.0, 
                        self.conhecimento['pesos_posicionais'][pos]))
                
                # Atualizar estatísticas globais
                self.conhecimento['total_predicoes'] += 1
                self.conhecimento['total_acertos'] += acertos
                
                if acertos > self.conhecimento['melhor_acerto_historico']:
                    self.conhecimento['melhor_acerto_historico'] = acertos
                    ajustes_realizados['novo_recorde'] = acertos
                
                # Adicionar ao histórico
                self.conhecimento['historico_ajustes'].append({
                    'timestamp': datetime.now().isoformat(),
                    'predicao_id': predicao.id,
                    'acertos': acertos,
                    'meta_alcancada': acertos >= self.meta_acertos,
                    'ajustes': dict(ajustes_realizados)
                })
                
                # Marcar feedback aplicado
                self._marcar_feedback_aplicado(predicao.id)
            
            # Salvar conhecimento atualizado
            self._salvar_conhecimento()
            
            # Registrar sessão de aprendizado
            resultado_aprendizado = ResultadoAprendizado(
                timestamp=datetime.now().isoformat(),
                predicoes_analisadas=len(resultados),
                acertos_medios=np.mean([r[1] for r in resultados]),
                melhor_acerto=max([r[1] for r in resultados]),
                pior_acerto=min([r[1] for r in resultados]),
                ajustes_realizados=ajustes_realizados,
                meta_alcancada=any(r[1] >= self.meta_acertos for r in resultados)
            )
            
            self._salvar_sessao_aprendizado(resultado_aprendizado)
            
            self.logger.info(f"✅ Aprendizado aplicado: {len(ajustes_realizados)} ajustes")
            
        except Exception as e:
            self.logger.error(f"❌ Erro no aprendizado: {e}")
            
    def _marcar_feedback_aplicado(self, predicao_id: str):
        """Marca que o feedback foi aplicado à predição"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE predicoes 
                SET feedback_aplicado = TRUE
                WHERE id = ?
            ''', (predicao_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao marcar feedback: {e}")
            
    def _salvar_sessao_aprendizado(self, resultado: ResultadoAprendizado):
        """Salva sessão de aprendizado no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessoes_aprendizado (
                    timestamp, predicoes_analisadas, acertos_medios, melhor_acerto,
                    pior_acerto, ajustes_realizados, meta_alcancada
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                resultado.timestamp,
                resultado.predicoes_analisadas,
                resultado.acertos_medios,
                resultado.melhor_acerto,
                resultado.pior_acerto,
                json.dumps(resultado.ajustes_realizados),
                resultado.meta_alcancada
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar sessão: {e}")
            
    def gerar_relatorio_completo(self) -> Dict:
        """Gera relatório completo do sistema"""
        self.logger.info("📊 Gerando relatório completo...")
        
        try:
            # Dados do banco
            conn = sqlite3.connect(self.db_path)
            
            # Estatísticas de predições
            predicoes_df = pd.read_sql_query('''
                SELECT * FROM predicoes 
                WHERE acertos IS NOT NULL
                ORDER BY timestamp DESC
            ''', conn)
            
            # Estatísticas de aprendizado
            aprendizado_df = pd.read_sql_query('''
                SELECT * FROM sessoes_aprendizado
                ORDER BY timestamp DESC
            ''', conn)
            
            conn.close()
            
            # Calcular métricas
            relatorio = {
                'timestamp': datetime.now().isoformat(),
                'resumo_geral': {
                    'total_predicoes': len(predicoes_df),
                    'total_verificadas': len(predicoes_df[predicoes_df['acertos'].notna()]),
                    'acertos_medio': predicoes_df['acertos'].mean() if len(predicoes_df) > 0 else 0,
                    'melhor_resultado': predicoes_df['acertos'].max() if len(predicoes_df) > 0 else 0,
                    'meta_alcancada_vezes': len(predicoes_df[predicoes_df['acertos'] >= self.meta_acertos]),
                    'taxa_sucesso_meta': (len(predicoes_df[predicoes_df['acertos'] >= self.meta_acertos]) / len(predicoes_df) * 100) if len(predicoes_df) > 0 else 0
                },
                'ultimas_predicoes': [],
                'evolucao_aprendizado': [],
                'conhecimento_atual': self.conhecimento,
                'recomendacoes': []
            }
            
            # Últimas predições
            for _, row in predicoes_df.head(10).iterrows():
                relatorio['ultimas_predicoes'].append({
                    'id': row['id'],
                    'concurso_alvo': row['concurso_alvo'],
                    'acertos': row['acertos'],
                    'confianca_media': row['confianca_media'],
                    'meta_alcancada': row['acertos'] >= self.meta_acertos if pd.notna(row['acertos']) else False
                })
            
            # Evolução do aprendizado
            for _, row in aprendizado_df.head(5).iterrows():
                relatorio['evolucao_aprendizado'].append({
                    'timestamp': row['timestamp'],
                    'acertos_medios': row['acertos_medios'],
                    'melhor_acerto': row['melhor_acerto'],
                    'meta_alcancada': row['meta_alcancada']
                })
            
            # Recomendações
            if len(predicoes_df) > 0:
                acertos_medio = predicoes_df['acertos'].mean()
                
                if acertos_medio < 8:
                    relatorio['recomendacoes'].append("🔴 Performance baixa. Considere revisar estratégia.")
                elif acertos_medio < 10:
                    relatorio['recomendacoes'].append("🟡 Performance média. Continue coletando dados.")
                else:
                    relatorio['recomendacoes'].append("🟢 Performance boa. Sistema está aprendendo bem.")
                
                if relatorio['resumo_geral']['taxa_sucesso_meta'] > 0:
                    relatorio['recomendacoes'].append(f"🎯 Meta alcançada {relatorio['resumo_geral']['taxa_sucesso_meta']:.1f}% das vezes.")
                else:
                    relatorio['recomendacoes'].append("🎯 Meta ainda não alcançada. Sistema continua aprendendo.")
            
            self.logger.info("✅ Relatório gerado")
            return relatorio
            
        except Exception as e:
            self.logger.error(f"❌ Erro no relatório: {e}")
            return {}
            
    def _ajustar_numeros_unicos(self, numeros_preditos: List[int], confiancas: List[float]) -> List[int]:
        """Ajusta os números preditos para garantir que sejam únicos"""
        numeros_ajustados = []
        confiancas_ajustadas = list(confiancas)
        
        for i, numero in enumerate(numeros_preditos):
            if numero not in numeros_ajustados:
                numeros_ajustados.append(numero)
            else:
                # Encontrar um número próximo não usado
                for delta in range(1, 13):  # Procurar até 12 números de distância
                    for sinal in [1, -1]:
                        novo_numero = numero + (delta * sinal)
                        if 1 <= novo_numero <= 25 and novo_numero not in numeros_ajustados:
                            numeros_ajustados.append(novo_numero)
                            # Reduzir um pouco a confiança por ser ajustado
                            confiancas_ajustadas[i] *= 0.95
                            self.logger.info(f"⚠️ Ajustado N{i+1}: {numero} → {novo_numero}")
                            break
                    if len(numeros_ajustados) == i + 1:
                        break
                
                # Se ainda não encontrou, usar qualquer número disponível
                if len(numeros_ajustados) != i + 1:
                    for num in range(1, 26):
                        if num not in numeros_ajustados:
                            numeros_ajustados.append(num)
                            confiancas_ajustadas[i] *= 0.8
                            self.logger.info(f"⚠️ Forçado N{i+1}: {numero} → {num}")
                            break
        
        return numeros_ajustados

def main():
    """Função principal para teste do sistema"""
    print("🧠 SISTEMA DE PREDIÇÃO POSICIONAL INTELIGENTE")
    print("="*55)
    print("📍 Análise baseada em períodos: 30, 15, 10, 5, 3 sorteios")
    print("🎯 Método: Frequências posicionais com aprendizado contínuo")
    print("="*55)
    
    sistema = SistemaPredicaoInteligente()
    
    while True:
        print("\n🎯 MENU PRINCIPAL")
        print("="*30)
        print("1. 🔮 Gerar nova predição inteligente")
        print("2. 🔍 Verificar resultados de predições")
        print("3. 📊 Relatório completo")
        print("4. 📈 Ver histórico de aprendizado")
        print("5. 🎲 Status do conhecimento")
        print("0. ❌ Sair")
        
        try:
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "1":
                print("\n🔮 Gerando predição inteligente...")
                predicao = sistema.gerar_predicao_inteligente()
                
                print(f"\n✅ PREDIÇÃO GERADA")
                print(f"🆔 ID: {predicao.id}")
                print(f"🎲 Concurso alvo: {predicao.concurso_alvo}")
                print(f"🔢 Números: {predicao.numeros_preditos}")
                print(f"📊 Confiança média: {predicao.confianca_media:.1f}%")
                
            elif opcao == "2":
                print("\n🔍 Verificando resultados...")
                resultados = sistema.verificar_resultados_predicoes()
                
                if resultados:
                    print(f"\n✅ {len(resultados)} predições verificadas")
                    for predicao, acertos in resultados:
                        status = "🎉 META ALCANÇADA!" if acertos >= sistema.meta_acertos else f"{acertos} acertos"
                        print(f"🎲 Concurso {predicao.concurso_alvo}: {status}")
                else:
                    print("ℹ️ Nenhuma predição pendente para verificar")
                    
            elif opcao == "3":
                print("\n📊 Gerando relatório...")
                relatorio = sistema.gerar_relatorio_completo()
                
                print(f"\n📈 RELATÓRIO COMPLETO")
                print(f"📊 Total de predições: {relatorio['resumo_geral']['total_predicoes']}")
                print(f"🎯 Acertos médios: {relatorio['resumo_geral']['acertos_medio']:.1f}")
                print(f"🏆 Melhor resultado: {relatorio['resumo_geral']['melhor_resultado']}")
                print(f"🎉 Meta alcançada: {relatorio['resumo_geral']['meta_alcancada_vezes']} vezes")
                print(f"📈 Taxa de sucesso: {relatorio['resumo_geral']['taxa_sucesso_meta']:.1f}%")
                
                if relatorio['recomendacoes']:
                    print("\n💡 RECOMENDAÇÕES:")
                    for rec in relatorio['recomendacoes']:
                        print(f"   {rec}")
                        
            elif opcao == "4":
                print("\n📈 Histórico de aprendizado...")
                conn = sqlite3.connect(sistema.db_path)
                df = pd.read_sql_query('SELECT * FROM sessoes_aprendizado ORDER BY timestamp DESC LIMIT 5', conn)
                conn.close()
                
                if len(df) > 0:
                    for _, row in df.iterrows():
                        print(f"📅 {row['timestamp'][:19]}")
                        print(f"   📊 {row['predicoes_analisadas']} predições analisadas")
                        print(f"   🎯 {row['acertos_medios']:.1f} acertos médios")
                        print(f"   {'🎉' if row['meta_alcancada'] else '📈'} Meta: {'Alcançada' if row['meta_alcancada'] else 'Não alcançada'}")
                        print()
                else:
                    print("ℹ️ Nenhuma sessão de aprendizado registrada")
                    
            elif opcao == "5":
                print(f"\n🧠 STATUS DO CONHECIMENTO")
                print(f"📚 Total de ajustes: {len(sistema.conhecimento.get('historico_ajustes', []))}")
                print(f"🎯 Melhor acerto histórico: {sistema.conhecimento.get('melhor_acerto_historico', 0)}")
                print(f"📊 Total de predições: {sistema.conhecimento.get('total_predicoes', 0)}")
                print(f"🔄 Última atualização: {sistema.conhecimento.get('ultima_atualizacao', 'N/A')[:19]}")
                
                print("\n⚖️ Pesos posicionais atuais:")
                pesos = sistema.conhecimento.get('pesos_posicionais', {})
                for i in range(1, 16):
                    pos = f'N{i}'
                    peso = pesos.get(pos, 1.0)
                    print(f"   {pos}: {peso:.3f}")
                    
            elif opcao == "0":
                print("👋 Saindo...")
                break
                
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()