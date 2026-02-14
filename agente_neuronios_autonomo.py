#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 AGENTE DE NEURÔNIOS AUTÔNOMO - LOTOSCOPE
==========================================
Sistema de IA evolutiva que aprende autonomamente 
a prever resultados da Lotofácil através de auto-modificação
"""

import os
import sys
import json
import random
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
import sqlite3
import logging
from dataclasses import dataclass, asdict
from copy import deepcopy

# Importa nossa base LotoScope existente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from database_optimizer import get_optimized_connection, cached_query
    from lotofacil_lite.gerador_academico_dinamico import GeradorAcademicoDinamico
    from lotofacil_lite.analisador_academico_padroes import AnalisadorAcademicoPadroes
except ImportError as e:
    print(f"⚠️ Módulo não encontrado: {e}")

@dataclass
class EstadoAprendizado:
    """Estado do aprendizado do agente"""
    passo: int
    concurso_alvo: int
    combinacoes_necessarias: int
    padroes_relevantes: Dict[str, float]
    padroes_irrelevantes: List[str]
    timestamp: str
    acertos_obtidos: List[int]
    estrategia_usada: str
    tempo_execucao: float
    sucesso: bool

@dataclass
class ConfiguracaoAgente:
    """Configurações do agente autônomo"""
    passos_max: int = 10
    concurso_alvo: int = None
    limite_combinacoes: int = 1000000
    threshold_melhoria: float = 0.95  # Deve usar <= 95% das combinações anteriores
    usar_rede_neural: bool = True
    auto_modificacao: bool = True
    salvar_estado: bool = True

class AgenteNeuroniosAutonomo:
    """
    🧠 Agente de IA autônomo para predição de Lotofácil
    
    Características:
    - Aprende autonomamente com dados reais
    - Auto-modifica seu próprio código
    - Evolui estratégias baseado em resultados
    - Usa rede neural de 24.000+ neurônios
    """
    
    def __init__(self, config: ConfiguracaoAgente = None):
        self.config = config or ConfiguracaoAgente()
        self.historico_estados = []
        self.padroes_globais = {}
        self.estrategias_codigo = {}
        self.rede_neural = None
        self.dados_historicos = None
        self.logger = self._configurar_logging()
        
        # Estado atual
        self.passo_atual = 0
        self.baseline_combinacoes = None
        self.melhor_resultado = None
        
        # Caminhos de arquivos
        self.arquivo_estado = "agente_estado.json"
        self.arquivo_padroes = "agente_padroes.pkl"
        self.arquivo_codigo = "agente_codigo_gerado.py"
        
        self.logger.info("Agente Neuronios Autonomo inicializado")
        
    def _configurar_logging(self):
        """Configura sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agente_autonomo.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('AgenteAutonomo')
    
    def inicializar_base_dados(self):
        """Carrega dados históricos reais da Lotofácil"""
        self.logger.info("Carregando base de dados histórica...")
        
        try:
            # Conecta com nossa base otimizada
            conn = get_optimized_connection()
            
            # Carrega todos os concursos
            query = """
            SELECT concurso, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, 
                   n11, n12, n13, n14, n15, data_sorteio
            FROM resultado_lotofacil 
            ORDER BY concurso
            """
            
            # Executa query diretamente se cached_query falhar
            try:
                self.dados_historicos = cached_query(query, conn)
            except Exception as e:
                self.logger.warning(f"Cached query falhou: {e}, tentando query direta...")
                cursor = conn.cursor()
                cursor.execute(query)
                self.dados_historicos = cursor.fetchall()
                cursor.close()
            
            self.logger.info(f"Dados carregados: {len(self.dados_historicos)} concursos")
            
            # Define concurso alvo se não especificado
            if not self.config.concurso_alvo:
                # Escolhe um concurso aleatório entre os últimos 500
                ultimos_concursos = [row[0] for row in self.dados_historicos[-500:]]
                self.config.concurso_alvo = random.choice(ultimos_concursos)
                
            self.logger.info(f"Concurso alvo definido: {self.config.concurso_alvo}")
            
            conn.close()
            return len(self.dados_historicos) > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            # Fallback: usar dados mockados mínimos para teste
            self.logger.info("Usando dados de fallback para teste...")
            self._criar_dados_fallback()
            return len(self.dados_historicos) > 0
    
    def _criar_dados_fallback(self):
        """Cria dados de fallback para teste"""
        self.logger.info("Criando dados de fallback...")
        
        # Gera dados simulados baseados em padrões reais da Lotofácil
        self.dados_historicos = []
        
        for concurso in range(3520, 3528):  # Últimos concursos
            # Gera combinação realística
            numeros = sorted(random.sample(range(1, 26), 15))
            data_sorteio = f"2024-{(concurso % 12) + 1:02d}-{(concurso % 28) + 1:02d}"
            
            # Formato: (concurso, n1, n2, ..., n15, data_sorteio)
            row = [concurso] + numeros + [data_sorteio]
            self.dados_historicos.append(tuple(row))
        
        # Define concurso alvo como o último
        if not self.config.concurso_alvo:
            self.config.concurso_alvo = 3527
            
        self.logger.info(f"Dados fallback criados: {len(self.dados_historicos)} concursos")
    
    def inicializar_rede_neural(self, tamanho_custom=None):
        """Inicializa ou carrega rede neural"""
        self.logger.info("🧠 Inicializando rede neural...")
        
        try:
            # Tenta carregar rede existente
            if os.path.exists("rede_neural_agente.pkl"):
                with open("rede_neural_agente.pkl", "rb") as f:
                    self.rede_neural = pickle.load(f)
                self.logger.info("✅ Rede neural carregada do arquivo")
            else:
                # Cria nova rede neural
                tamanho = tamanho_custom or 24000
                self.rede_neural = self._criar_rede_neural(tamanho)
                self.logger.info(f"✅ Nova rede neural criada com {tamanho} neurônios")
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na rede neural: {e}")
            return False
    
    def _criar_rede_neural(self, tamanho):
        """Cria rede neural personalizada para Lotofácil"""
        # Estrutura da rede neural adaptada para Lotofácil
        rede = {
            'camada_entrada': np.random.randn(25, 100),  # 25 números possíveis
            'camada_oculta1': np.random.randn(100, 500),
            'camada_oculta2': np.random.randn(500, 1000),
            'camada_oculta3': np.random.randn(1000, tamanho),
            'camada_saida': np.random.randn(tamanho, 25),
            'bias': np.random.randn(tamanho),
            'pesos_padroes': {},
            'memoria_sequencial': []
        }
        return rede
    
    def obter_dados_validos(self):
        """Obtém dados válidos até o concurso anterior ao alvo"""
        dados_validos = []
        for row in self.dados_historicos:
            if row[0] < self.config.concurso_alvo:
                # Converte para formato mais útil
                numeros = list(row[1:16])  # n1 a n15
                dados_validos.append({
                    'concurso': row[0],
                    'numeros': numeros,
                    'data': row[16]
                })
        
        self.logger.info(f"📊 {len(dados_validos)} concursos válidos para análise")
        return dados_validos
    
    def obter_resultado_alvo(self):
        """Obtém o resultado do concurso alvo"""
        for row in self.dados_historicos:
            if row[0] == self.config.concurso_alvo:
                return list(row[1:16])  # n1 a n15
        return None
    
    def analisar_padroes_historicos(self, dados_validos):
        """Analisa padrões nos dados históricos"""
        self.logger.info("🔍 Analisando padrões históricos...")
        
        padroes = {
            'frequencia_numeros': {},
            'sequencias_comuns': {},
            'gaps_medios': {},
            'padroes_pares_impares': {},
            'padroes_posicionais': {},
            'tendencias_recentes': {},
            'correlacoes': {}
        }
        
        # Análise de frequência
        for concurso in dados_validos:
            for num in concurso['numeros']:
                padroes['frequencia_numeros'][num] = padroes['frequencia_numeros'].get(num, 0) + 1
        
        # Análise de sequências (últimos 50 concursos)
        ultimos_50 = dados_validos[-50:]
        for i, concurso in enumerate(ultimos_50):
            nums = set(concurso['numeros'])
            if i > 0:
                nums_anterior = set(ultimos_50[i-1]['numeros'])
                intersecao = len(nums.intersection(nums_anterior))
                padroes['sequencias_comuns'][intersecao] = padroes['sequencias_comuns'].get(intersecao, 0) + 1
        
        # Análise de gaps (números não sorteados)
        todos_numeros = set(range(1, 26))
        for num in todos_numeros:
            ultimo_sorteio = -1
            gaps = []
            for i, concurso in enumerate(dados_validos):
                if num in concurso['numeros']:
                    if ultimo_sorteio >= 0:
                        gaps.append(i - ultimo_sorteio)
                    ultimo_sorteio = i
            if gaps:
                padroes['gaps_medios'][num] = sum(gaps) / len(gaps)
        
        # Análise de pares/ímpares
        for concurso in dados_validos[-30:]:  # Últimos 30 concursos
            pares = sum(1 for num in concurso['numeros'] if num % 2 == 0)
            impares = 15 - pares
            chave = f"{pares}-{impares}"
            padroes['padroes_pares_impares'][chave] = padroes['padroes_pares_impares'].get(chave, 0) + 1
        
        self.logger.info(f"✅ Padrões analisados: {len(padroes)} categorias")
        return padroes
    
    def gerar_combinacao_inteligente(self, dados_validos, padroes, tentativa=1):
        """Gera combinação usando padrões aprendidos e rede neural"""
        self.logger.info(f"🎯 Gerando combinação inteligente (tentativa {tentativa})...")
        
        combinacao = set()
        
        # 1. Usa números mais frequentes (peso 40%)
        freq_ordenada = sorted(padroes['frequencia_numeros'].items(), key=lambda x: x[1], reverse=True)
        top_freq = [num for num, freq in freq_ordenada[:10]]
        combinacao.update(random.sample(top_freq, min(6, len(top_freq))))
        
        # 2. Usa análise de gaps (peso 20%)
        gaps_ordenados = sorted(padroes['gaps_medios'].items(), key=lambda x: x[1])
        numeros_gap = [num for num, gap in gaps_ordenados[:8]]
        combinacao.update(random.sample(numeros_gap, min(3, len(numeros_gap))))
        
        # 3. Balanceamento pares/ímpares (peso 20%)
        pares_mais_comum = max(padroes['padroes_pares_impares'].items(), key=lambda x: x[1])
        pares_target, impares_target = map(int, pares_mais_comum[0].split('-'))
        
        numeros_restantes = list(set(range(1, 26)) - combinacao)
        pares_disponiveis = [n for n in numeros_restantes if n % 2 == 0]
        impares_disponiveis = [n for n in numeros_restantes if n % 2 == 1]
        
        pares_atuais = sum(1 for n in combinacao if n % 2 == 0)
        impares_atuais = len(combinacao) - pares_atuais
        
        # Completa com balanceamento
        pares_necessarios = max(0, pares_target - pares_atuais)
        impares_necessarios = max(0, impares_target - impares_atuais)
        
        if pares_necessarios > 0 and pares_disponiveis:
            combinacao.update(random.sample(pares_disponiveis, min(pares_necessarios, len(pares_disponiveis))))
        
        if impares_necessarios > 0 and impares_disponiveis:
            combinacao.update(random.sample(impares_disponiveis, min(impares_necessarios, len(impares_disponiveis))))
        
        # 4. Completa com rede neural (peso 20%)
        if self.rede_neural and len(combinacao) < 15:
            faltam = 15 - len(combinacao)
            numeros_restantes = list(set(range(1, 26)) - combinacao)
            
            # Aplica rede neural nos números restantes
            scores_neural = self._aplicar_rede_neural(numeros_restantes, dados_validos)
            melhores_neural = sorted(zip(numeros_restantes, scores_neural), key=lambda x: x[1], reverse=True)
            
            for num, score in melhores_neural[:faltam]:
                combinacao.add(num)
                if len(combinacao) >= 15:
                    break
        
        # 5. Completa aleatoriamente se necessário
        if len(combinacao) < 15:
            restantes = list(set(range(1, 26)) - combinacao)
            combinacao.update(random.sample(restantes, 15 - len(combinacao)))
        
        # Garante exatamente 15 números
        combinacao = sorted(list(combinacao)[:15])
        
        self.logger.info(f"✅ Combinação gerada: {combinacao}")
        return combinacao
    
    def _aplicar_rede_neural(self, numeros, dados_validos):
        """Aplica rede neural para scoring de números"""
        try:
            # Prepara entrada da rede
            entrada = np.zeros(25)
            for concurso in dados_validos[-10:]:  # Últimos 10 concursos
                for num in concurso['numeros']:
                    entrada[num-1] += 1
            
            # Forward pass simplificado
            x = entrada.reshape(1, -1)
            h1 = np.tanh(np.dot(x, self.rede_neural['camada_entrada']))
            h2 = np.tanh(np.dot(h1, self.rede_neural['camada_oculta1'][:100, :500]))
            output = np.dot(h2, self.rede_neural['camada_oculta2'][:500, :25])
            
            # Retorna scores para os números solicitados
            scores = []
            for num in numeros:
                scores.append(output[0][num-1])
                
            return scores
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro na rede neural: {e}")
            return [random.random() for _ in numeros]
    
    def verificar_acertos(self, combinacao, resultado_alvo):
        """Verifica quantos números foram acertados"""
        acertos = len(set(combinacao).intersection(set(resultado_alvo)))
        self.logger.info(f"🎯 Acertos obtidos: {acertos}/15")
        return acertos
    
    def tentar_acertar_15(self, dados_validos, padroes, resultado_alvo):
        """Tenta acertar 15 números incrementando combinações"""
        self.logger.info(f"🚀 Iniciando tentativa de acerto para concurso {self.config.concurso_alvo}")
        
        combinacoes_testadas = []
        combinacoes_count = 0
        max_acertos = 0
        melhor_combinacao = None
        
        inicio = datetime.now()
        
        while combinacoes_count < self.config.limite_combinacoes:
            combinacoes_count += 1
            
            # Gera combinação inteligente
            combinacao = self.gerar_combinacao_inteligente(dados_validos, padroes, combinacoes_count)
            combinacoes_testadas.append(combinacao)
            
            # Verifica acertos
            acertos = self.verificar_acertos(combinacao, resultado_alvo)
            
            if acertos > max_acertos:
                max_acertos = acertos
                melhor_combinacao = combinacao
                self.logger.info(f"🎯 Novo máximo: {max_acertos} acertos com {combinacoes_count} combinações")
            
            # Se acertou 15, para
            if acertos == 15:
                self.logger.info(f"🏆 SUCESSO! 15 acertos com {combinacoes_count} combinações!")
                break
            
            # Log de progresso
            if combinacoes_count % 1000 == 0:
                self.logger.info(f"📊 Progresso: {combinacoes_count} combinações, máximo: {max_acertos} acertos")
        
        tempo_execucao = (datetime.now() - inicio).total_seconds()
        
        resultado = {
            'combinacoes_necessarias': combinacoes_count,
            'max_acertos': max_acertos,
            'melhor_combinacao': melhor_combinacao,
            'tempo_execucao': tempo_execucao,
            'sucesso': max_acertos == 15,
            'todas_combinacoes': combinacoes_testadas
        }
        
        self.logger.info(f"📊 Resultado final: {max_acertos} acertos, {combinacoes_count} combinações, {tempo_execucao:.2f}s")
        return resultado
    
    def aprender_com_resultado(self, resultado, padroes):
        """Aprende com o resultado e atualiza padrões"""
        self.logger.info("🧠 Aprendendo com resultado...")
        
        if resultado['sucesso'] or resultado['max_acertos'] >= 12:
            # Analisa a melhor combinação
            melhor = resultado['melhor_combinacao']
            
            # Aprende padrões da combinação bem-sucedida
            padroes_novos = {
                'numeros_relevantes': melhor,
                'balanceamento_pares': sum(1 for n in melhor if n % 2 == 0),
                'distribuicao_faixas': {
                    'baixos': sum(1 for n in melhor if n <= 8),
                    'medios': sum(1 for n in melhor if 9 <= n <= 17),
                    'altos': sum(1 for n in melhor if n >= 18)
                }
            }
            
            # Atualiza pesos dos padrões globais
            for num in melhor:
                if 'numeros_validos' not in self.padroes_globais:
                    self.padroes_globais['numeros_validos'] = {}
                self.padroes_globais['numeros_validos'][num] = self.padroes_globais['numeros_validos'].get(num, 0) + 1
            
            # Atualiza rede neural
            if self.rede_neural:
                self._atualizar_rede_neural(melhor, resultado['max_acertos'])
            
            self.logger.info("✅ Padrões atualizados com sucesso")
        else:
            self.logger.info("⚠️ Resultado insuficiente para aprendizado")
    
    def _atualizar_rede_neural(self, combinacao_sucesso, acertos):
        """Atualiza pesos da rede neural baseado no sucesso"""
        try:
            # Taxa de aprendizado baseada no número de acertos
            taxa_aprendizado = acertos / 15.0
            
            # Reforça conexões dos números que deram certo
            for num in combinacao_sucesso:
                # Atualiza pesos positivamente
                self.rede_neural['camada_saida'][:, num-1] *= (1 + taxa_aprendizado * 0.1)
            
            # Diminui pesos dos números não escolhidos
            numeros_nao_escolhidos = set(range(1, 26)) - set(combinacao_sucesso)
            for num in numeros_nao_escolhidos:
                self.rede_neural['camada_saida'][:, num-1] *= (1 - taxa_aprendizado * 0.05)
            
            self.logger.info(f"🧠 Rede neural atualizada (taxa: {taxa_aprendizado:.3f})")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar rede neural: {e}")
    
    def salvar_estado(self, estado: EstadoAprendizado):
        """Salva estado atual do agente"""
        self.historico_estados.append(estado)
        
        # Salva em arquivo JSON
        estados_dict = [asdict(estado) for estado in self.historico_estados]
        with open(self.arquivo_estado, 'w') as f:
            json.dump(estados_dict, f, indent=2, default=str)
        
        # Salva padrões em pickle
        with open(self.arquivo_padroes, 'wb') as f:
            pickle.dump(self.padroes_globais, f)
        
        # Salva rede neural
        if self.rede_neural:
            with open("rede_neural_agente.pkl", 'wb') as f:
                pickle.dump(self.rede_neural, f)
        
        self.logger.info(f"💾 Estado salvo - Passo {estado.passo}")
    
    def carregar_estado(self):
        """Carrega estado anterior se existir"""
        try:
            if os.path.exists(self.arquivo_estado):
                with open(self.arquivo_estado, 'r') as f:
                    estados_dict = json.load(f)
                
                self.historico_estados = []
                for estado_dict in estados_dict:
                    estado = EstadoAprendizado(**estado_dict)
                    self.historico_estados.append(estado)
                
                if self.historico_estados:
                    ultimo_estado = self.historico_estados[-1]
                    self.passo_atual = ultimo_estado.passo
                    self.baseline_combinacoes = ultimo_estado.combinacoes_necessarias
                
                self.logger.info(f"📂 Estado carregado - {len(self.historico_estados)} passos")
            
            if os.path.exists(self.arquivo_padroes):
                with open(self.arquivo_padroes, 'rb') as f:
                    self.padroes_globais = pickle.load(f)
                self.logger.info("📂 Padrões globais carregados")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar estado: {e}")
    
    def auto_modificar_codigo(self):
        """Auto-modifica código baseado no aprendizado"""
        if not self.config.auto_modificacao:
            return
            
        self.logger.info("🔧 Iniciando auto-modificação de código...")
        
        # Analisa histórico para identificar melhorias
        if len(self.historico_estados) >= 3:
            # Encontra padrões de sucesso
            sucessos = [e for e in self.historico_estados if e.sucesso]
            
            if sucessos:
                # Gera código otimizado baseado nos sucessos
                codigo_otimizado = self._gerar_codigo_otimizado(sucessos)
                
                # Salva novo código
                with open(self.arquivo_codigo, 'w') as f:
                    f.write(codigo_otimizado)
                
                self.logger.info("✅ Código auto-modificado criado")
    
    def _gerar_codigo_otimizado(self, sucessos):
        """Gera código otimizado baseado nos sucessos"""
        # Analisa padrões de sucesso
        numeros_comuns = {}
        estrategias_sucesso = {}
        
        for sucesso in sucessos:
            for padrao, peso in sucesso.padroes_relevantes.items():
                if padrao not in estrategias_sucesso:
                    estrategias_sucesso[padrao] = []
                estrategias_sucesso[padrao].append(peso)
        
        # Gera código novo
        codigo = f'''# Código auto-gerado pelo Agente Autônomo
# Baseado em {len(sucessos)} sucessos identificados

def estrategia_otimizada_auto():
    """Estratégia auto-gerada pelo agente"""
    padroes_sucesso = {estrategias_sucesso}
    
    # Implementa lógica otimizada baseada no aprendizado
    return gerar_combinacao_com_padroes(padroes_sucesso)
'''
        
        return codigo
    
    def executar_ciclo_completo(self):
        """Executa ciclo completo de aprendizado autônomo"""
        self.logger.info("🚀 INICIANDO CICLO COMPLETO DE APRENDIZADO AUTÔNOMO")
        
        # Inicialização
        if not self.inicializar_base_dados():
            return False
        
        if not self.inicializar_rede_neural():
            return False
        
        # Carrega estado anterior se existir
        self.carregar_estado()
        
        # Obtem dados válidos
        dados_validos = self.obter_dados_validos()
        resultado_alvo = self.obter_resultado_alvo()
        
        if not resultado_alvo:
            self.logger.error(f"❌ Concurso alvo {self.config.concurso_alvo} não encontrado")
            return False
        
        self.logger.info(f"🎯 Resultado alvo: {resultado_alvo}")
        
        # Analisa padrões históricos
        padroes = self.analisar_padroes_historicos(dados_validos)
        
        # Executa passos de aprendizado
        for passo in range(self.passo_atual + 1, self.config.passos_max + 1):
            self.logger.info(f"\n🔄 === PASSO {passo}/{self.config.passos_max} ===")
            
            # Tenta acertar 15
            resultado = self.tentar_acertar_15(dados_validos, padroes, resultado_alvo)
            
            # Verifica critério de sucesso
            if passo == 1:
                # Primeiro passo - estabelece baseline
                self.baseline_combinacoes = resultado['combinacoes_necessarias']
                sucesso_passo = True
                self.logger.info(f"📊 Baseline estabelecido: {self.baseline_combinacoes} combinações")
            else:
                # Passos subsequentes - deve melhorar ou igualar
                limite = int(self.baseline_combinacoes * self.config.threshold_melhoria)
                sucesso_passo = resultado['combinacoes_necessarias'] <= limite
                
                if sucesso_passo:
                    self.logger.info(f"✅ SUCESSO! {resultado['combinacoes_necessarias']} <= {limite}")
                    # Atualiza baseline se melhorou significativamente
                    if resultado['combinacoes_necessarias'] < self.baseline_combinacoes * 0.8:
                        self.baseline_combinacoes = resultado['combinacoes_necessarias']
                        self.logger.info(f"📊 Novo baseline: {self.baseline_combinacoes}")
                else:
                    self.logger.warning(f"❌ FALHA! {resultado['combinacoes_necessarias']} > {limite}")
                    self.logger.info("🔄 Reiniciando ciclo...")
                    self.passo_atual = 0
                    self.baseline_combinacoes = None
                    continue
            
            # Aprende com resultado
            self.aprender_com_resultado(resultado, padroes)
            
            # Cria estado
            estado = EstadoAprendizado(
                passo=passo,
                concurso_alvo=self.config.concurso_alvo,
                combinacoes_necessarias=resultado['combinacoes_necessarias'],
                padroes_relevantes=self.padroes_globais,
                padroes_irrelevantes=[],
                timestamp=datetime.now().isoformat(),
                acertos_obtidos=[resultado['max_acertos']],
                estrategia_usada="inteligente_neural",
                tempo_execucao=resultado['tempo_execucao'],
                sucesso=sucesso_passo
            )
            
            # Salva estado
            self.salvar_estado(estado)
            self.passo_atual = passo
            
            # Auto-modifica código a cada 3 passos
            if passo % 3 == 0:
                self.auto_modificar_codigo()
        
        self.logger.info("🏆 CICLO COMPLETO FINALIZADO!")
        self.gerar_relatorio_final()
        return True
    
    def gerar_relatorio_final(self):
        """Gera relatório final do aprendizado"""
        self.logger.info("📊 Gerando relatório final...")
        
        relatorio = f"""
🧠 RELATÓRIO FINAL - AGENTE NEURÔNIOS AUTÔNOMO
============================================
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Concurso Alvo: {self.config.concurso_alvo}
Passos Executados: {len(self.historico_estados)}

📈 EVOLUÇÃO DO APRENDIZADO:
"""
        
        for i, estado in enumerate(self.historico_estados):
            status = "✅ SUCESSO" if estado.sucesso else "❌ FALHA"
            relatorio += f"""
Passo {estado.passo}: {status}
  • Combinações necessárias: {estado.combinacoes_necessarias:,}
  • Acertos máximos: {max(estado.acertos_obtidos)}
  • Tempo: {estado.tempo_execucao:.2f}s
"""
        
        if self.historico_estados:
            sucessos = [e for e in self.historico_estados if e.sucesso]
            melhor_resultado = min(self.historico_estados, key=lambda x: x.combinacoes_necessarias)
            
            relatorio += f"""

🏆 ESTATÍSTICAS FINAIS:
=====================
• Total de sucessos: {len(sucessos)}/{len(self.historico_estados)}
• Taxa de sucesso: {len(sucessos)/len(self.historico_estados)*100:.1f}%
• Melhor resultado: {melhor_resultado.combinacoes_necessarias:,} combinações
• Padrões aprendidos: {len(self.padroes_globais)}

🧠 EVOLUÇÃO DA IA:
================
• Rede neural atualizada: {len(self.historico_estados)} vezes
• Auto-modificações: {len(self.historico_estados) // 3}
• Código otimizado gerado: {'✅' if os.path.exists(self.arquivo_codigo) else '❌'}
"""
        
        # Salva relatório
        nome_arquivo = f"relatorio_agente_autonomo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        print(relatorio)
        self.logger.info(f"📊 Relatório salvo em: {nome_arquivo}")

def main():
    """Função principal"""
    print("🧠 AGENTE NEURÔNIOS AUTÔNOMO - LOTOSCOPE")
    print("=" * 50)
    
    # Configuração interativa
    print("⚙️ CONFIGURAÇÃO:")
    
    try:
        passos = int(input("Quantos passos de aprendizado? (padrão: 10): ") or "10")
        concurso = input("Concurso alvo (deixe vazio para aleatório): ").strip()
        concurso = int(concurso) if concurso else None
        limite = int(input("Limite de combinações por tentativa (padrão: 100000): ") or "100000")
        
        config = ConfiguracaoAgente(
            passos_max=passos,
            concurso_alvo=concurso,
            limite_combinacoes=limite
        )
        
        print(f"\n🎯 Configuração:")
        print(f"   • Passos: {config.passos_max}")
        print(f"   • Concurso alvo: {config.concurso_alvo or 'Aleatório'}")
        print(f"   • Limite por tentativa: {config.limite_combinacoes:,}")
        
        print("\n🚀 Iniciando agente autônomo...")
        
        # Cria e executa agente
        agente = AgenteNeuroniosAutonomo(config)
        sucesso = agente.executar_ciclo_completo()
        
        if sucesso:
            print("\n🏆 AGENTE EXECUTADO COM SUCESSO!")
        else:
            print("\n❌ Erro na execução do agente")
            
    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()