#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA DE AUTO-TREINO CONTÍNUO - AGENTE LOTOSCOPE
=====================================================
Sistema de IA que treina continuamente, aprendendo e se auto-corrigindo
"""

import os
import json
import random
import time
import threading
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass, asdict
import logging

@dataclass
class SessaoTreino:
    """Registro de uma sessão de treino"""
    id_sessao: str
    concurso_alvo: int
    resultado_esperado: list
    combinacoes_necessarias: int
    acertos_obtidos: int
    tempo_execucao: float
    estrategias_usadas: dict
    padroes_descobertos: dict
    melhoria_obtida: float
    timestamp: str

class SistemaAutoTreinoContinuo:
    """
    🧠 Sistema de Auto-Treino Contínuo
    
    Funcionalidades:
    - Treino 24/7 automático
    - Seleção aleatória de concursos para treino
    - Auto-correção de estratégias
    - Persistência de conhecimento
    - Monitoramento de evolução
    - Auto-implementação de melhorias
    """
    
    def __init__(self, config_arquivo="config_auto_treino.json"):
        self.config_arquivo = config_arquivo
        self.config = self._carregar_configuracao()
        
        # Configura logger primeiro
        self.logger = self._configurar_logging()
        
        # Estado do agente
        self.estrategias = self._inicializar_estrategias()
        self.conhecimento_global = self._carregar_conhecimento()
        self.sessoes_treino = []
        self.metricas_performance = {
            'sessoes_totais': 0,
            'sucessos': 0,
            'media_acertos': 0,
            'melhoria_acumulada': 0,
            'tempo_total_treino': 0
        }
        
        # Controle de execução
        self.executando = False
        self.thread_treino = None
        
        # Base de dados histórica
        self.dados_historicos = self._carregar_dados_historicos()
        
        self.logger.info("Sistema de Auto-Treino Contínuo inicializado")
        
    def _carregar_configuracao(self):
        """Carrega configuração do sistema"""
        config_padrao = {
            'intervalo_treino_segundos': 30,  # Treina a cada 30 segundos
            'concursos_por_sessao': 5,        # Testa 5 concursos por sessão
            'limite_combinacoes_por_teste': 10000,
            'threshold_melhoria': 0.05,       # 5% de melhoria mínima
            'salvar_estado_intervalo': 100,   # Salva a cada 100 sessões
            'auto_implementar_melhorias': True,
            'logging_nivel': 'INFO',
            'backup_conhecimento': True,
            'reiniciar_se_degradar': True,
            'limite_sessoes_por_dia': 2880    # 24h * 60min * 2 = máximo 2880 sessões/dia
        }
        
        if os.path.exists(self.config_arquivo):
            try:
                with open(self.config_arquivo, 'r') as f:
                    config_usuario = json.load(f)
                config_padrao.update(config_usuario)
            except Exception as e:
                print(f"Erro ao carregar config: {e}, usando padrão")
        
        # Salva configuração atualizada
        with open(self.config_arquivo, 'w') as f:
            json.dump(config_padrao, f, indent=2)
            
        return config_padrao
    
    def _configurar_logging(self):
        """Configura logging detalhado"""
        try:
            log_level = getattr(logging, self.config.get('logging_nivel', 'INFO'))
            
            # Criar logger específico para auto-treino
            logger = logging.getLogger('AutoTreino')
            logger.setLevel(log_level)
            
            # Remove handlers existentes para evitar duplicação
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # Handler para arquivo com rotação
            from logging.handlers import RotatingFileHandler
            handler_arquivo = RotatingFileHandler(
                'auto_treino.log', 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            
            # Handler para console
            handler_console = logging.StreamHandler()
            
            # Formato
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler_arquivo.setFormatter(formatter)
            handler_console.setFormatter(formatter)
            
            logger.addHandler(handler_arquivo)
            logger.addHandler(handler_console)
            
            return logger
            
        except Exception as e:
            # Fallback para logging básico se der erro
            print(f"Erro na configuração de logging: {e}")
            logger = logging.getLogger('AutoTreino')
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            return logger
    
    def _inicializar_estrategias(self):
        """Inicializa estratégias evolutivas"""
        return {
            'frequencia_global': {'peso': 0.25, 'sucesso_acumulado': 0, 'tentativas': 0},
            'frequencia_recente': {'peso': 0.25, 'sucesso_acumulado': 0, 'tentativas': 0},
            'balanceamento_pares': {'peso': 0.20, 'sucesso_acumulado': 0, 'tentativas': 0},
            'distribuicao_posicional': {'peso': 0.15, 'sucesso_acumulado': 0, 'tentativas': 0},
            'gaps_temporais': {'peso': 0.10, 'sucesso_acumulado': 0, 'tentativas': 0},
            'sequencias_comuns': {'peso': 0.05, 'sucesso_acumulado': 0, 'tentativas': 0}
        }
    
    def _carregar_conhecimento(self):
        """Carrega conhecimento acumulado"""
        arquivo_conhecimento = "conhecimento_agente.json"
        
        conhecimento_padrao = {
            'numeros_mais_eficazes': {},
            'padroes_vencedores': [],
            'distribuicoes_sucesso': {},
            'combinacoes_historicas_sucesso': [],
            'insights_descobertos': [],
            'ultima_atualizacao': datetime.now().isoformat()
        }
        
        if os.path.exists(arquivo_conhecimento):
            try:
                with open(arquivo_conhecimento, 'r') as f:
                    conhecimento_salvo = json.load(f)
                conhecimento_padrao.update(conhecimento_salvo)
                self.logger.info("Conhecimento anterior carregado")
            except Exception as e:
                self.logger.warning(f"Erro ao carregar conhecimento: {e}")
        
        return conhecimento_padrao
    
    def _salvar_conhecimento(self):
        """Salva conhecimento acumulado"""
        arquivo_conhecimento = "conhecimento_agente.json"
        self.conhecimento_global['ultima_atualizacao'] = datetime.now().isoformat()
        
        # Backup se configurado
        if self.config['backup_conhecimento']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_arquivo = f"conhecimento_backup_{timestamp}.json"
            try:
                with open(backup_arquivo, 'w') as f:
                    json.dump(self.conhecimento_global, f, indent=2)
            except Exception as e:
                self.logger.warning(f"Erro no backup: {e}")
        
        # Salva conhecimento principal
        try:
            with open(arquivo_conhecimento, 'w') as f:
                json.dump(self.conhecimento_global, f, indent=2)
            self.logger.debug("Conhecimento salvo")
        except Exception as e:
            self.logger.error(f"Erro ao salvar conhecimento: {e}")
    
    def _carregar_dados_historicos(self):
        """Carrega ou simula dados históricos"""
        # Simulação de dados para teste - em produção, conectar ao SQL Server
        dados = []
        
        for concurso in range(3400, 3528):  # 128 concursos simulados
            # Gera combinação realística usando distribuições observadas
            numeros = self._gerar_combinacao_realistica()
            dados.append({
                'concurso': concurso,
                'numeros': numeros,
                'data': f"2024-{((concurso % 12) + 1):02d}-{((concurso % 28) + 1):02d}"
            })
        
        self.logger.info(f"Base histórica carregada: {len(dados)} concursos")
        return dados
    
    def _gerar_combinacao_realistica(self):
        """Gera combinação baseada em padrões reais da Lotofácil"""
        # Distribuições baseadas em análise real da Lotofácil
        numeros_alta_freq = [2, 3, 4, 5, 6, 11, 12, 13, 14, 20]  # 40% mais frequentes
        numeros_media_freq = [1, 7, 8, 9, 10, 15, 16, 17, 18, 19] # 40% frequência média
        numeros_baixa_freq = [21, 22, 23, 24, 25]                 # 20% menos frequentes
        
        combinacao = []
        
        # Distribui proporcionalmente
        combinacao.extend(random.sample(numeros_alta_freq, 6))    # 6 de alta
        combinacao.extend(random.sample(numeros_media_freq, 7))   # 7 de média  
        combinacao.extend(random.sample(numeros_baixa_freq, 2))   # 2 de baixa
        
        return sorted(combinacao)
    
    def selecionar_concursos_treino(self):
        """Seleciona concursos aleatórios para treino"""
        quantidade = self.config['concursos_por_sessao']
        
        # Seleciona concursos aleatórios, excluindo os últimos 10 (reserva para teste final)
        concursos_disponiveis = [c['concurso'] for c in self.dados_historicos[:-10]]
        concursos_selecionados = random.sample(concursos_disponiveis, 
                                             min(quantidade, len(concursos_disponiveis)))
        
        return concursos_selecionados
    
    def analisar_padroes_contextuais(self, concurso_alvo):
        """Analisa padrões específicos ao contexto do concurso"""
        # Busca dados do concurso e contexto anterior
        dados_concurso = None
        indice_concurso = -1
        
        for i, dados in enumerate(self.dados_historicos):
            if dados['concurso'] == concurso_alvo:
                dados_concurso = dados
                indice_concurso = i
                break
        
        if not dados_concurso or indice_concurso < 10:
            return {}
        
        # Analisa contexto (10 concursos anteriores)
        contexto = self.dados_historicos[max(0, indice_concurso-10):indice_concurso]
        
        padroes = {
            'frequencia_contexto': {},
            'tendencias_recentes': {},
            'gaps_no_contexto': {},
            'padroes_sequenciais': {}
        }
        
        # Análise de frequência no contexto
        for concurso in contexto:
            for num in concurso['numeros']:
                padroes['frequencia_contexto'][num] = padroes['frequencia_contexto'].get(num, 0) + 1
        
        # Tendências dos últimos 3 concursos
        ultimos_3 = contexto[-3:]
        for concurso in ultimos_3:
            for num in concurso['numeros']:
                padroes['tendencias_recentes'][num] = padroes['tendencias_recentes'].get(num, 0) + 1
        
        return padroes
    
    def gerar_combinacao_inteligente(self, concurso_alvo, padroes_contexto):
        """Gera combinação usando estratégias evolutivas e contexto"""
        combinacao = set()
        
        # Aplica estratégias com pesos evolutivos
        estrategias_ativas = {k: v for k, v in self.estrategias.items() if v['peso'] > 0.01}
        
        for estrategia, dados in estrategias_ativas.items():
            peso = dados['peso']
            quantidade = int(15 * peso)
            
            if estrategia == 'frequencia_global':
                # Usa conhecimento global acumulado
                if self.conhecimento_global['numeros_mais_eficazes']:
                    nums_ordenados = sorted(
                        self.conhecimento_global['numeros_mais_eficazes'].items(),
                        key=lambda x: x[1], reverse=True
                    )
                    candidatos = [int(num) for num, score in nums_ordenados[:12]]
                    if candidatos and quantidade > 0:
                        combinacao.update(random.sample(candidatos, min(quantidade, len(candidatos))))
            
            elif estrategia == 'frequencia_recente':
                # Usa padrões do contexto
                if padroes_contexto.get('frequencia_contexto'):
                    nums_ordenados = sorted(
                        padroes_contexto['frequencia_contexto'].items(),
                        key=lambda x: x[1], reverse=True
                    )
                    candidatos = [int(num) for num, freq in nums_ordenados[:10]]
                    if candidatos and quantidade > 0:
                        combinacao.update(random.sample(candidatos, min(quantidade, len(candidatos))))
            
            elif estrategia == 'balanceamento_pares':
                # Balanceia pares/ímpares baseado em padrões de sucesso
                if len(combinacao) < 15:
                    restantes = set(range(1, 26)) - combinacao
                    pares = [n for n in restantes if n % 2 == 0]
                    impares = [n for n in restantes if n % 2 == 1]
                    
                    pares_atuais = sum(1 for n in combinacao if n % 2 == 0)
                    target_pares = 7  # Padrão comum na Lotofácil
                    
                    if pares_atuais < target_pares and pares and quantidade > 0:
                        combinacao.update(random.sample(pares, min(quantidade, len(pares))))
        
        # Completa com números aleatórios inteligentes se necessário
        if len(combinacao) < 15:
            restantes = list(set(range(1, 26)) - combinacao)
            faltam = 15 - len(combinacao)
            combinacao.update(random.sample(restantes, min(faltam, len(restantes))))
        
        return sorted(list(combinacao)[:15])
    
    def executar_sessao_treino(self):
        """Executa uma sessão completa de treino"""
        sessao_id = f"sessao_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        self.logger.info(f"Iniciando {sessao_id}")
        
        # Seleciona concursos para treino
        concursos_treino = self.selecionar_concursos_treino()
        
        resultados_sessao = []
        melhoria_total = 0
        
        for concurso_alvo in concursos_treino:
            inicio = time.time()
            
            # Encontra resultado esperado
            resultado_esperado = None
            for dados in self.dados_historicos:
                if dados['concurso'] == concurso_alvo:
                    resultado_esperado = dados['numeros']
                    break
            
            if not resultado_esperado:
                continue
            
            # Analisa padrões contextuais
            padroes_contexto = self.analisar_padroes_contextuais(concurso_alvo)
            
            # Treina no concurso específico
            resultado_treino = self._treinar_concurso_especifico(
                concurso_alvo, resultado_esperado, padroes_contexto
            )
            
            tempo_execucao = time.time() - inicio
            
            # Registra resultado
            sessao_treino = SessaoTreino(
                id_sessao=sessao_id,
                concurso_alvo=concurso_alvo,
                resultado_esperado=resultado_esperado,
                combinacoes_necessarias=resultado_treino['combinacoes_necessarias'],
                acertos_obtidos=resultado_treino['max_acertos'],
                tempo_execucao=tempo_execucao,
                estrategias_usadas=dict(self.estrategias),
                padroes_descobertos=padroes_contexto,
                melhoria_obtida=resultado_treino['melhoria'],
                timestamp=datetime.now().isoformat()
            )
            
            resultados_sessao.append(sessao_treino)
            melhoria_total += resultado_treino['melhoria']
            
            # Aprende com o resultado
            self._aprender_com_resultado(resultado_treino, resultado_esperado, padroes_contexto)
        
        # Atualiza métricas globais
        self._atualizar_metricas_globais(resultados_sessao)
        
        # Auto-implementa melhorias se configurado
        if self.config['auto_implementar_melhorias'] and melhoria_total > self.config['threshold_melhoria']:
            self._implementar_melhorias_automaticas()
        
        self.logger.info(f"Sessão {sessao_id} concluída: {len(resultados_sessao)} treinos, melhoria: {melhoria_total:.3f}")
        
        return resultados_sessao
    
    def _treinar_concurso_especifico(self, concurso_alvo, resultado_esperado, padroes_contexto):
        """Treina especificamente em um concurso"""
        limite = self.config['limite_combinacoes_por_teste']
        
        max_acertos = 0
        combinacoes_testadas = 0
        melhor_combinacao = None
        
        baseline_anterior = self.conhecimento_global.get(f'baseline_concurso_{concurso_alvo}', float('inf'))
        
        while combinacoes_testadas < limite:
            combinacoes_testadas += 1
            
            # Gera combinação inteligente
            combinacao = self.gerar_combinacao_inteligente(concurso_alvo, padroes_contexto)
            
            # Verifica acertos
            acertos = len(set(combinacao) & set(resultado_esperado))
            
            if acertos > max_acertos:
                max_acertos = acertos
                melhor_combinacao = combinacao
            
            # Para se acertou 15
            if acertos == 15:
                break
        
        # Calcula melhoria
        melhoria = 0
        if baseline_anterior != float('inf'):
            if combinacoes_testadas < baseline_anterior:
                melhoria = (baseline_anterior - combinacoes_testadas) / baseline_anterior
        
        # Atualiza baseline
        if combinacoes_testadas < baseline_anterior:
            self.conhecimento_global[f'baseline_concurso_{concurso_alvo}'] = combinacoes_testadas
        
        return {
            'combinacoes_necessarias': combinacoes_testadas,
            'max_acertos': max_acertos,
            'melhor_combinacao': melhor_combinacao,
            'melhoria': melhoria
        }
    
    def _aprender_com_resultado(self, resultado_treino, resultado_esperado, padroes_contexto):
        """Aprende e atualiza estratégias baseado no resultado"""
        acertos = resultado_treino['max_acertos']
        combinacao = resultado_treino['melhor_combinacao']
        
        if acertos >= 12:  # Sucesso significativo
            # Atualiza eficácia dos números
            for num in combinacao:
                if num in resultado_esperado:
                    self.conhecimento_global['numeros_mais_eficazes'][str(num)] = \
                        self.conhecimento_global['numeros_mais_eficazes'].get(str(num), 0) + 1
            
            # Registra padrão de sucesso
            if acertos >= 14:
                self.conhecimento_global['padroes_vencedores'].append({
                    'combinacao': combinacao,
                    'acertos': acertos,
                    'contexto': padroes_contexto,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Limita tamanho da lista
                if len(self.conhecimento_global['padroes_vencedores']) > 100:
                    self.conhecimento_global['padroes_vencedores'] = \
                        self.conhecimento_global['padroes_vencedores'][-100:]
        
        # Atualiza estratégias
        self._atualizar_estrategias_evolutivas(resultado_treino)
    
    def _atualizar_estrategias_evolutivas(self, resultado_treino):
        """Atualiza pesos das estratégias baseado no sucesso"""
        acertos = resultado_treino['max_acertos']
        
        # Taxa de sucesso (0.0 a 1.0)
        taxa_sucesso = acertos / 15.0
        
        # Atualiza cada estratégia
        for estrategia in self.estrategias:
            self.estrategias[estrategia]['tentativas'] += 1
            self.estrategias[estrategia]['sucesso_acumulado'] += taxa_sucesso
            
            # Recalcula peso baseado na eficácia histórica
            if self.estrategias[estrategia]['tentativas'] > 0:
                eficacia = self.estrategias[estrategia]['sucesso_acumulado'] / self.estrategias[estrategia]['tentativas']
                # Peso varia entre 0.05 e 0.50 baseado na eficácia
                self.estrategias[estrategia]['peso'] = 0.05 + (0.45 * eficacia)
        
        # Normaliza pesos
        total_peso = sum(est['peso'] for est in self.estrategias.values())
        if total_peso > 0:
            for estrategia in self.estrategias:
                self.estrategias[estrategia]['peso'] /= total_peso
    
    def _atualizar_metricas_globais(self, resultados_sessao):
        """Atualiza métricas de performance global"""
        self.metricas_performance['sessoes_totais'] += 1
        
        for resultado in resultados_sessao:
            if resultado.acertos_obtidos >= 14:
                self.metricas_performance['sucessos'] += 1
            
            self.metricas_performance['tempo_total_treino'] += resultado.tempo_execucao
            self.metricas_performance['melhoria_acumulada'] += resultado.melhoria_obtida
        
        # Calcula média de acertos
        if resultados_sessao:
            media_sessao = sum(r.acertos_obtidos for r in resultados_sessao) / len(resultados_sessao)
            # Média móvel ponderada
            self.metricas_performance['media_acertos'] = \
                (self.metricas_performance['media_acertos'] * 0.9) + (media_sessao * 0.1)
    
    def _implementar_melhorias_automaticas(self):
        """Implementa melhorias automáticas no código"""
        self.logger.info("Implementando melhorias automáticas...")
        
        # Analisa padrões de sucesso para gerar código otimizado
        padroes_sucesso = self.conhecimento_global.get('padroes_vencedores', [])
        
        if len(padroes_sucesso) >= 10:  # Mínimo de dados para implementar
            # Gera nova estratégia baseada em padrões
            nova_estrategia = self._gerar_estrategia_automatica(padroes_sucesso)
            
            # Salva estratégia como código
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_estrategia = f"estrategia_auto_gerada_{timestamp}.py"
            
            with open(arquivo_estrategia, 'w') as f:
                f.write(nova_estrategia)
            
            self.logger.info(f"Nova estratégia auto-gerada salva em: {arquivo_estrategia}")
    
    def _gerar_estrategia_automatica(self, padroes_sucesso):
        """Gera código de estratégia automaticamente"""
        # Analisa padrões comuns
        numeros_comuns = {}
        for padrao in padroes_sucesso[-20:]:  # Últimos 20 padrões
            for num in padrao['combinacao']:
                numeros_comuns[num] = numeros_comuns.get(num, 0) + 1
        
        nums_mais_eficazes = sorted(numeros_comuns.items(), key=lambda x: x[1], reverse=True)[:15]
        
        codigo = f'''# Estratégia auto-gerada em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Baseada em {len(padroes_sucesso)} padrões de sucesso

import random

def estrategia_auto_gerada():
    """Estratégia gerada automaticamente pelo sistema de auto-treino"""
    
    # Números mais eficazes identificados automaticamente
    numeros_eficazes = {dict(nums_mais_eficazes)}
    
    # Distribui números por eficácia
    alta_eficacia = {[n for n, score in nums_mais_eficazes[:8]]}
    media_eficacia = {[n for n, score in nums_mais_eficazes[8:12]]}
    baixa_eficacia = {[n for n, score in nums_mais_eficazes[12:]]}
    
    # Gera combinação inteligente
    combinacao = []
    
    # 60% de alta eficácia
    if alta_eficacia:
        combinacao.extend(random.sample(alta_eficacia, min(9, len(alta_eficacia))))
    
    # 30% de média eficácia
    if media_eficacia:
        combinacao.extend(random.sample(media_eficacia, min(4, len(media_eficacia))))
    
    # 10% de baixa eficácia para diversidade
    if baixa_eficacia:
        combinacao.extend(random.sample(baixa_eficacia, min(2, len(baixa_eficacia))))
    
    # Completa se necessário
    if len(combinacao) < 15:
        restantes = [n for n in range(1, 26) if n not in combinacao]
        combinacao.extend(random.sample(restantes, 15 - len(combinacao)))
    
    return sorted(combinacao[:15])

# Métricas de eficácia desta estratégia
METRICAS_ESTRATEGIA = {{
    'padroes_analisados': {len(padroes_sucesso)},
    'numeros_identificados': {len(nums_mais_eficazes)},
    'data_geracao': '{datetime.now().isoformat()}',
    'versao': '1.0'
}}
'''
        
        return codigo
    
    def iniciar_auto_treino(self):
        """Inicia o processo de auto-treino contínuo"""
        if self.executando:
            self.logger.warning("Auto-treino já está em execução")
            return
        
        self.executando = True
        self.thread_treino = threading.Thread(target=self._loop_treino_continuo, daemon=True)
        self.thread_treino.start()
        
        self.logger.info("Auto-treino contínuo iniciado")
        print("[AUTO-TREINO CONTINUO INICIADO]")
        print("   - Treinando a cada {} segundos".format(self.config['intervalo_treino_segundos']))
        print("   - {} concursos por sessão".format(self.config['concursos_por_sessao']))
        print("   - Pressione Ctrl+C para parar")
    
    def _loop_treino_continuo(self):
        """Loop principal de treino contínuo"""
        sessoes_hoje = 0
        ultimo_dia = datetime.now().date()
        
        while self.executando:
            try:
                # Reset contador diário
                dia_atual = datetime.now().date()
                if dia_atual != ultimo_dia:
                    sessoes_hoje = 0
                    ultimo_dia = dia_atual
                
                # Verifica limite diário
                if sessoes_hoje >= self.config['limite_sessoes_por_dia']:
                    self.logger.info("Limite diário de sessões atingido, aguardando...")
                    time.sleep(3600)  # Espera 1 hora
                    continue
                
                # Executa sessão de treino
                resultados = self.executar_sessao_treino()
                sessoes_hoje += 1
                
                # Salva estado periodicamente
                if self.metricas_performance['sessoes_totais'] % self.config['salvar_estado_intervalo'] == 0:
                    self._salvar_conhecimento()
                    self._salvar_metricas()
                
                # Verifica se precisa reiniciar por degradação
                if self.config['reiniciar_se_degradar']:
                    self._verificar_degradacao_performance()
                
                # Aguarda próxima sessão
                time.sleep(self.config['intervalo_treino_segundos'])
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Erro no loop de treino: {e}")
                time.sleep(60)  # Espera 1 minuto antes de tentar novamente
        
        self.executando = False
        self.logger.info("Auto-treino contínuo finalizado")
    
    def _verificar_degradacao_performance(self):
        """Verifica se a performance está degradando"""
        if self.metricas_performance['sessoes_totais'] < 50:
            return  # Precisa de mais dados
        
        # Analisa últimas 20 sessões vs primeiras 20
        # Implementação simplificada - em produção seria mais sofisticada
        if self.metricas_performance['media_acertos'] < 10:  # Threshold de degradação
            self.logger.warning("Degradação de performance detectada, reiniciando estratégias")
            self.estrategias = self._inicializar_estrategias()
    
    def _salvar_metricas(self):
        """Salva métricas de performance"""
        arquivo_metricas = f"metricas_auto_treino_{datetime.now().strftime('%Y%m%d')}.json"
        
        metricas_completas = {
            'metricas_performance': self.metricas_performance,
            'estrategias_atuais': self.estrategias,
            'timestamp': datetime.now().isoformat(),
            'sessoes_executadas': len(self.sessoes_treino)
        }
        
        with open(arquivo_metricas, 'w') as f:
            json.dump(metricas_completas, f, indent=2)
    
    def parar_auto_treino(self):
        """Para o auto-treino contínuo"""
        self.executando = False
        if self.thread_treino:
            self.thread_treino.join(timeout=5)
        
        # Salva estado final
        self._salvar_conhecimento()
        self._salvar_metricas()
        
        self.logger.info("Auto-treino parado e estado salvo")
        print("🛑 AUTO-TREINO PARADO")
    
    def executar_continuamente(self):
        """Interface compatível para execução contínua"""
        print("[INICIANDO AUTO-TREINO CONTINUO...]")
        self.iniciar_auto_treino()
        
        try:
            while self.executando:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        finally:
            self.parar_auto_treino()
    
    def parar(self):
        """Interface compatível para parada"""
        self.parar_auto_treino()
    
    def exibir_status(self):
        """Exibe status atual do sistema"""
        print("\n" + "="*60)
        print("[STATUS DO SISTEMA DE AUTO-TREINO]")
        print("="*60)
        
        print(f"Executando: {'SIM' if self.executando else 'NAO'}")
        print(f"Sessões totais: {self.metricas_performance['sessoes_totais']:,}")
        print(f"Sucessos: {self.metricas_performance['sucessos']:,}")
        print(f"Taxa de sucesso: {self.metricas_performance['sucessos']/max(1, self.metricas_performance['sessoes_totais'])*100:.1f}%")
        print(f"Média de acertos: {self.metricas_performance['media_acertos']:.2f}")
        print(f"Melhoria acumulada: {self.metricas_performance['melhoria_acumulada']:.3f}")
        print(f"Tempo total de treino: {self.metricas_performance['tempo_total_treino']:.1f}s")
        
        print(f"\n[ESTRATEGIAS ATUAIS]:")
        for estrategia, dados in self.estrategias.items():
            eficacia = dados['sucesso_acumulado'] / max(1, dados['tentativas'])
            print(f"   {estrategia}: peso={dados['peso']:.3f}, eficácia={eficacia:.3f}")
        
        print(f"\n[CONHECIMENTO ACUMULADO]:")
        print(f"   Números eficazes: {len(self.conhecimento_global.get('numeros_mais_eficazes', {}))}")
        print(f"   Padrões vencedores: {len(self.conhecimento_global.get('padroes_vencedores', []))}")
        
        print("="*60)

def main():
    """Função principal"""
    print("[SISTEMA DE AUTO-TREINO CONTINUO - LOTOSCOPE]")
    print("="*60)
    
    # Cria sistema
    sistema = SistemaAutoTreinoContinuo()
    
    print("\nOpções:")
    print("1. Iniciar auto-treino contínuo")
    print("2. Executar sessão única de treino")
    print("3. Exibir status atual")
    print("4. Configurar sistema")
    print("0. Sair")
    
    try:
        while True:
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "1":
                sistema.iniciar_auto_treino()
                try:
                    while sistema.executando:
                        time.sleep(1)
                        if input("") == "s":  # Permite parar com 's'
                            break
                except KeyboardInterrupt:
                    pass
                sistema.parar_auto_treino()
                
            elif opcao == "2":
                print("Executando sessão única...")
                resultados = sistema.executar_sessao_treino()
                print(f"Sessão concluída: {len(resultados)} treinos executados")
                
            elif opcao == "3":
                sistema.exibir_status()
                
            elif opcao == "4":
                print("Configuração atual salva em:", sistema.config_arquivo)
                print("Edite o arquivo e reinicie para aplicar mudanças")
                
            elif opcao == "0":
                break
                
            else:
                print("Opção inválida")
                
    except KeyboardInterrupt:
        print("\nFinalizando...")
    finally:
        if sistema.executando:
            sistema.parar_auto_treino()

if __name__ == "__main__":
    main()