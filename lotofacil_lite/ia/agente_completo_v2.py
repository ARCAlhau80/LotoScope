#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AGENTE DE NEURÔNIOS EVOLUTIVOS v2.0 - LOTOSCOPE
=================================================
Sistema de IA evolutiva com DADOS REAIS do SQL Server

Diferenças da v1.0:
- Conecta ao banco de dados real (SQL Server)
- Usa histórico completo de 3600+ concursos
- Estratégias baseadas em análises validadas (Pool 23)
- Backtesting real para evolução dos pesos
- Integração com filtros do sistema principal

Autor: LotoScope AI
Data: 2026-03-15
"""

import os
import sys
import json
import random
import numpy as np
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, Counter
import logging

from itertools import combinations

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# FILTROS VALIDADOS DO POOL 23 (extraídos do super_menu.py - NÃO ALTERAR!)
# ═══════════════════════════════════════════════════════════════════════════════

FILTROS_POR_NIVEL = {
    0: {},  # Sem filtros - 490k combos
    1: {
        'soma_min': 175, 'soma_max': 235,
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
    },
    2: {
        'soma_min': 180, 'soma_max': 230,
        'consecutivos_min': 7, 'consecutivos_max': 10,
        'gap_max': 5,
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
    },
    3: {
        'soma_min': 185, 'soma_max': 225,
        'pares_min': 5, 'pares_max': 10,
        'primos_min': 3, 'primos_max': 8,
        'consecutivos_min': 7, 'consecutivos_max': 10,
        'gap_max': 5,
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
    },
    4: {
        'soma_min': 190, 'soma_max': 220,
        'pares_min': 6, 'pares_max': 9,
        'primos_min': 4, 'primos_max': 7,
        'consecutivos_min': 7, 'consecutivos_max': 9,
        'gap_max': 4,
        'seq_max': 5,
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
    },
    5: {
        'soma_min': 180, 'soma_max': 210,
        'pares_min': 6, 'pares_max': 9,
        'primos_min': 3, 'primos_max': 7,
        'consecutivos_min': 7, 'consecutivos_max': 9,
        'gap_max': 4,
        'seq_max': 5,
        'rep_min': 4, 'rep_max': 11,
        'nucleo_min': 8,
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
    },
    6: {
        'soma_min': 185, 'soma_max': 205,
        'pares_min': 6, 'pares_max': 9,
        'primos_min': 4, 'primos_max': 7,
        'consecutivos_min': 7, 'consecutivos_max': 9,
        'gap_max': 4,
        'seq_max': 5,
        'rep_min': 5, 'rep_max': 10,
        'nucleo_min': 8,
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
    },
}

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}


@dataclass
class Estrategia:
    """Representa uma estratégia evolutiva"""
    nome: str
    peso: float = 0.2
    sucesso_total: float = 0.0
    tentativas: int = 0
    taxa_sucesso: float = 0.0
    
    def atualizar(self, sucesso: bool, magnitude: float = 1.0):
        """Atualiza estatísticas da estratégia"""
        self.tentativas += 1
        if sucesso:
            self.sucesso_total += magnitude
        self.taxa_sucesso = self.sucesso_total / self.tentativas if self.tentativas > 0 else 0


@dataclass
class ResultadoEvolucao:
    """Resultado de uma iteração evolutiva"""
    geracao: int
    concurso_testado: int
    combinacao_gerada: List[int]
    numeros_sorteados: List[int]
    acertos: int
    estrategia_principal: str
    pesos_estrategias: Dict[str, float]
    tempo_ms: float
    sucesso_minimo: bool  # >= 11 acertos


@dataclass
class EstadoAgente:
    """Estado persistente do agente"""
    versao: str = "2.0"
    geracoes_totais: int = 0
    melhor_acerto: int = 0
    melhor_combinacao: List[int] = field(default_factory=list)
    estrategias: Dict[str, Dict] = field(default_factory=dict)
    historico_evolucao: List[Dict] = field(default_factory=list)
    ultima_atualizacao: str = ""
    nivel_preferido: int = 3  # Nível Pool 23 aprendido (default=3 balanced)
    ultimo_concurso_treinado: int = 0  # Último concurso usado no treino


class AgenteNeuroniosEvolutivo:
    """
    Agente de IA Evolutiva para Lotofácil - v2.0
    
    Usa dados REAIS do SQL Server e estratégias validadas:
    - INVERTIDA v3.0: Exclui números quentes (consecutivos altos)
    - Débito Posicional: Números em déficit posicional
    - Frequência Adaptativa: Pesos baseados em janelas móveis
    - Padrões Par/Ímpar: Distribuição histórica
    - Anomalias: Números com comportamento atípico
    """
    
    CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    
    def __init__(self, geracoes_max: int = 50, populacao: int = 100):
        self.geracoes_max = geracoes_max
        self.populacao = populacao
        
        # Estratégias evolutivas com pesos iniciais baseados em benchmarks
        self.estrategias = {
            'frequencia_global': Estrategia('frequencia_global', peso=0.15),
            'frequencia_recente': Estrategia('frequencia_recente', peso=0.20),
            'debito_posicional': Estrategia('debito_posicional', peso=0.15),
            'par_impar': Estrategia('par_impar', peso=0.10),
            'soma_equilibrada': Estrategia('soma_equilibrada', peso=0.10),
            'exclusao_quentes': Estrategia('exclusao_quentes', peso=0.20),  # INVERTIDA v3.0
            'aleatorio_ponderado': Estrategia('aleatorio_ponderado', peso=0.10)
        }
        
        # Cache de dados
        self._resultados_cache = None
        self._analises_cache = {}
        
        # Estado persistente
        self.estado = EstadoAgente()
        self._carregar_estado()
        
        # Estatísticas da sessão
        self.sessao_inicio = datetime.now()
        self.sessao_geracoes = 0
        self.sessao_acertos = []
    
    def _conectar_db(self):
        """Conecta ao banco de dados SQL Server"""
        try:
            import pyodbc
            return pyodbc.connect(self.CONN_STR)
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
    
    def _carregar_resultados(self, force: bool = False) -> List[Dict]:
        """Carrega resultados do banco de dados (com cache)"""
        if self._resultados_cache and not force:
            return self._resultados_cache
        
        logger.info("Carregando resultados do banco de dados...")
        
        conn = self._conectar_db()
        cursor = conn.cursor()
        
        query = '''
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        self._resultados_cache = [
            {
                'concurso': row[0],
                'numeros': sorted(list(row[1:16]))
            }
            for row in rows
        ]
        
        logger.info(f"Carregados {len(self._resultados_cache)} concursos")
        return self._resultados_cache
    
    def _analisar_frequencias(self, resultados: List[Dict], janela: int = 30) -> Dict:
        """Analisa frequências globais e em janela móvel"""
        cache_key = f"freq_{janela}_{resultados[0]['concurso']}"
        if cache_key in self._analises_cache:
            return self._analises_cache[cache_key]
        
        # Frequência global
        freq_global = Counter()
        for r in resultados:
            freq_global.update(r['numeros'])
        
        # Frequência na janela recente
        freq_recente = Counter()
        for r in resultados[:janela]:
            freq_recente.update(r['numeros'])
        
        total_global = len(resultados)
        total_recente = min(janela, len(resultados))
        
        analise = {
            'freq_global': {n: freq_global[n] / total_global * 100 for n in range(1, 26)},
            'freq_recente': {n: freq_recente[n] / total_recente * 100 for n in range(1, 26)},
            'media_global': 60.0,  # 15/25 * 100
            'media_recente': 60.0
        }
        
        self._analises_cache[cache_key] = analise
        return analise
    
    def _analisar_consecutivos(self, resultados: List[Dict], limite: int = 30) -> Dict[int, int]:
        """Conta aparições consecutivas de cada número"""
        consecutivos = {n: 0 for n in range(1, 26)}
        
        for r in resultados[:limite]:
            for n in range(1, 26):
                if n in r['numeros']:
                    consecutivos[n] += 1
                else:
                    break  # Parou de aparecer
        
        # Na verdade, queremos contar quantas vezes seguidas apareceu
        consecutivos = {n: 0 for n in range(1, 26)}
        for n in range(1, 26):
            for r in resultados:
                if n in r['numeros']:
                    consecutivos[n] += 1
                else:
                    break
        
        return consecutivos
    
    def _analisar_debito_posicional(self, resultados: List[Dict], janela: int = 6) -> Dict[int, Dict]:
        """Analisa débito posicional (números devendo em certas posições)"""
        MIN_HISTORICO = 100
        LIMIAR_DEBITO = 0.3
        
        if len(resultados) < MIN_HISTORICO + janela:
            return {}
        
        # Histórico (excluindo janela recente)
        historico = resultados[janela:]
        contagem_hist = defaultdict(lambda: defaultdict(int))
        
        for r in historico:
            for pos, num in enumerate(r['numeros']):
                contagem_hist[num][pos + 1] += 1
        
        total_hist = len(historico)
        
        # Janela recente
        recentes = resultados[:janela]
        contagem_rec = defaultdict(lambda: defaultdict(int))
        
        for r in recentes:
            for pos, num in enumerate(r['numeros']):
                contagem_rec[num][pos + 1] += 1
        
        # Calcular débitos
        debitos = {}
        for num in range(1, 26):
            posicoes_debito = []
            deficit_total = 0
            
            for pos in range(1, 16):
                media = contagem_hist[num][pos] / total_hist * 100 if total_hist > 0 else 0
                recente = contagem_rec[num][pos] / janela * 100
                
                if media >= 5:  # Presença histórica significativa
                    if recente < media * LIMIAR_DEBITO:
                        deficit = media - recente
                        posicoes_debito.append(pos)
                        deficit_total += deficit
            
            debitos[num] = {
                'posicoes_debito': len(posicoes_debito),
                'deficit_total': deficit_total,
                'posicoes': posicoes_debito
            }
        
        return debitos
    
    def _calcular_score_exclusao(self, resultados: List[Dict]) -> List[Dict]:
        """
        Calcula score de exclusão usando estratégia INVERTIDA v3.0
        (Excluir números QUENTES - que vão esfriar)
        """
        consecutivos = self._analisar_consecutivos(resultados, 30)
        freq_analise = self._analisar_frequencias(resultados, 5)
        freq_curta = freq_analise['freq_recente']
        
        candidatos = []
        
        for n in range(1, 26):
            score = 0
            cons = consecutivos[n]
            fc = freq_curta[n]
            
            # Anomalia: 10+ consecutivos = PROTEGER (não excluir)
            if cons >= 10:
                score = -5  # Score negativo = não excluir
                status = "🛡️ ANOMALIA PROTEGIDA"
            elif cons >= 8:
                score = 6
                status = "🔥🔥🔥 SUPER QUENTE"
            elif cons >= 5:
                score = 5
                status = "🔥🔥 MUITO QUENTE"
            elif cons >= 3 and fc >= 80:
                score = 4
                status = "🔥 QUENTE"
            elif fc >= 100:
                score = 4
                status = "💯 100% FREQ"
            elif fc >= 80:
                score = 3
                status = "📈 FREQ ALTA"
            else:
                score = 1
                status = "📊 NORMAL"
            
            candidatos.append({
                'num': n,
                'score': score,
                'consecutivos': cons,
                'freq_curta': fc,
                'status': status
            })
        
        # Ordenar por score (maior = mais provável de sair, excluir)
        candidatos.sort(key=lambda x: (-x['score'], -x['consecutivos'], -x['freq_curta']))
        
        return candidatos
    
    def _gerar_combinacao_evolutiva(self, resultados: List[Dict], 
                                      excluidos: Set[int] = None) -> Tuple[List[int], str]:
        """
        Gera uma combinação usando estratégias evolutivas ponderadas
        
        Returns:
            (combinação, estratégia_principal)
        """
        if excluidos is None:
            excluidos = set()
        
        pool = [n for n in range(1, 26) if n not in excluidos]
        combinacao = set()
        estrategia_usada = ""
        
        # Escolher estratégia principal baseada nos pesos
        pesos = [self.estrategias[e].peso for e in self.estrategias]
        total_peso = sum(pesos)
        pesos_norm = [p / total_peso for p in pesos]
        
        estrategia_idx = np.random.choice(len(self.estrategias), p=pesos_norm)
        estrategia_nome = list(self.estrategias.keys())[estrategia_idx]
        estrategia_usada = estrategia_nome
        
        # Aplicar estratégia principal
        freq_analise = self._analisar_frequencias(resultados)
        
        if estrategia_nome == 'frequencia_global':
            # Números com maior frequência histórica
            freq = freq_analise['freq_global']
            nums_ordenados = sorted(pool, key=lambda x: freq.get(x, 0), reverse=True)
            combinacao.update(nums_ordenados[:10])
        
        elif estrategia_nome == 'frequencia_recente':
            # Números mais frequentes na janela recente
            freq = freq_analise['freq_recente']
            nums_ordenados = sorted(pool, key=lambda x: freq.get(x, 0), reverse=True)
            combinacao.update(nums_ordenados[:10])
        
        elif estrategia_nome == 'debito_posicional':
            # Números em débito posicional (vão compensar)
            debitos = self._analisar_debito_posicional(resultados)
            nums_debito = sorted(
                [n for n in pool if debitos.get(n, {}).get('posicoes_debito', 0) >= 2],
                key=lambda x: debitos[x]['deficit_total'],
                reverse=True
            )
            combinacao.update(nums_debito[:8])
            # Complementa com frequência
            freq = freq_analise['freq_recente']
            resto = sorted([n for n in pool if n not in combinacao], 
                          key=lambda x: freq.get(x, 0), reverse=True)
            combinacao.update(resto[:5])
        
        elif estrategia_nome == 'par_impar':
            # Distribuição 7-8 ou 8-7 (mais comum)
            pares = [n for n in pool if n % 2 == 0]
            impares = [n for n in pool if n % 2 == 1]
            random.shuffle(pares)
            random.shuffle(impares)
            # Distribuição 7/8
            if random.random() < 0.5:
                combinacao.update(pares[:7])
                combinacao.update(impares[:8])
            else:
                combinacao.update(pares[:8])
                combinacao.update(impares[:7])
        
        elif estrategia_nome == 'soma_equilibrada':
            # Soma entre 185-215 (faixa ótima validada)
            tentativas = 0
            melhor = None
            melhor_diff = float('inf')
            
            while tentativas < 100:
                cand = sorted(random.sample(pool, 15))
                soma = sum(cand)
                diff = abs(soma - 200)  # Alvo: 200
                
                if 185 <= soma <= 215:
                    combinacao.update(cand)
                    break
                
                if diff < melhor_diff:
                    melhor = cand
                    melhor_diff = diff
                
                tentativas += 1
            
            if not combinacao and melhor:
                combinacao.update(melhor)
        
        elif estrategia_nome == 'exclusao_quentes':
            # Usar estratégia INVERTIDA v3.0
            scores = self._calcular_score_exclusao(resultados)
            # Excluir top 2 quentes (além dos já excluídos)
            top_quentes = [c['num'] for c in scores[:2] if c['num'] not in excluidos]
            pool_ajustado = [n for n in pool if n not in top_quentes]
            
            # Selecionar do pool ajustado
            freq = freq_analise['freq_recente']
            nums_ordenados = sorted(pool_ajustado, key=lambda x: freq.get(x, 0), reverse=True)
            combinacao.update(nums_ordenados[:15])
        
        else:  # aleatorio_ponderado
            # Aleatório mas ponderado por frequência
            freq = freq_analise['freq_recente']
            pesos_nums = [freq.get(n, 50) for n in pool]
            total = sum(pesos_nums)
            prob = [p / total for p in pesos_nums]
            
            escolhidos = np.random.choice(pool, size=min(15, len(pool)), replace=False, p=prob)
            combinacao.update(escolhidos)
        
        # Completar se necessário
        if len(combinacao) < 15:
            restantes = [n for n in pool if n not in combinacao]
            random.shuffle(restantes)
            combinacao.update(restantes[:15 - len(combinacao)])
        
        # Garantir exatamente 15
        combinacao = sorted(list(combinacao)[:15])
        
        return combinacao, estrategia_usada
    
    def _verificar_acertos(self, combinacao: List[int], resultado: List[int]) -> int:
        """Verifica quantos acertos entre combinação e resultado"""
        return len(set(combinacao) & set(resultado))
    
    def _atualizar_pesos(self, estrategia_usada: str, acertos: int):
        """Atualiza pesos das estratégias baseado no resultado"""
        # Sucesso se >= 11 acertos
        sucesso = acertos >= 11
        magnitude = (acertos - 10) / 5 if acertos >= 11 else 0
        
        self.estrategias[estrategia_usada].atualizar(sucesso, magnitude)
        
        # Recalcular pesos baseado nas taxas de sucesso
        if self.sessao_geracoes > 0 and self.sessao_geracoes % 10 == 0:
            self._rebalancear_pesos()
    
    def _rebalancear_pesos(self):
        """Rebalanceia pesos das estratégias baseado no desempenho"""
        taxas = {nome: est.taxa_sucesso for nome, est in self.estrategias.items()}
        total = sum(taxas.values()) + 0.001  # Evitar divisão por zero
        
        for nome, est in self.estrategias.items():
            # Novo peso = base (0.1) + proporção do sucesso (0.8)
            novo_peso = 0.1 + 0.8 * (taxas[nome] / total)
            # Suavizar mudança (não mudar muito de uma vez)
            est.peso = est.peso * 0.7 + novo_peso * 0.3
        
        # Normalizar
        total_peso = sum(est.peso for est in self.estrategias.values())
        for est in self.estrategias.values():
            est.peso /= total_peso
        
        logger.info(f"Pesos rebalanceados: {self._resumir_pesos()}")
    
    def _resumir_pesos(self) -> Dict[str, str]:
        """Resumo dos pesos para log"""
        return {nome: f"{est.peso:.3f}" for nome, est in self.estrategias.items()}
    
    def executar_evolucao(self, concursos_teste: int = 20) -> List[ResultadoEvolucao]:
        """
        Executa ciclo evolutivo usando backtesting real COM FILTROS POOL 23
        
        Testa as estratégias E níveis de filtro contra os últimos N concursos reais
        e evolui os pesos e nível ótimo baseado no desempenho
        """
        print("\n" + "=" * 70)
        print("🧠 AGENTE NEURÔNIOS EVOLUTIVO v2.0 - CICLO DE EVOLUÇÃO")
        print("=" * 70)
        
        resultados_db = self._carregar_resultados()
        
        # Mínimo de 30 concursos de histórico para cálculos
        max_testavel = len(resultados_db) - 30
        
        if max_testavel < 10:
            print(f"❌ Dados insuficientes. Mínimo: 40 concursos no banco")
            return []
        
        if concursos_teste > max_testavel:
            print(f"⚠️ Ajustando de {concursos_teste} para {max_testavel} (precisa de 30 concursos de histórico)")
            concursos_teste = max_testavel
        
        print(f"\n📊 Total de concursos: {len(resultados_db)}")
        print(f"🎯 Concursos para teste: {concursos_teste}")
        print(f"📈 Combinações por concurso: {self.populacao}")
        print(f"\n🔄 Pesos iniciais: {self._resumir_pesos()}")
        
        # Verificar se tem nível preferido aprendido
        nivel_preferido = getattr(self.estado, 'nivel_preferido', 3)
        print(f"🎯 Nível Pool 23 atual: {nivel_preferido}")
        
        print(f"\n📋 MODO DE EVOLUÇÃO:")
        print(f"   [1] Evoluir com nível fixo ({nivel_preferido})")
        print(f"   [2] Comparar TODOS os níveis (0-6) e aprender o melhor")
        print(f"   [3] Benchmark rápido (3 níveis: 2, 3, 4)")
        
        modo = input("\n   Escolha [ENTER=1]: ").strip()
        modo = int(modo) if modo else 1
        
        if modo == 2:
            return self._evolucao_comparativa(resultados_db, concursos_teste, [0, 1, 2, 3, 4, 5, 6])
        elif modo == 3:
            return self._evolucao_comparativa(resultados_db, concursos_teste, [2, 3, 4])
        else:
            return self._evolucao_nivel_fixo(resultados_db, concursos_teste, nivel_preferido)
    
    def _evolucao_nivel_fixo(self, resultados_db: List[Dict], concursos_teste: int, 
                             nivel: int) -> List[ResultadoEvolucao]:
        """Evolução usando nível de filtro fixo"""
        print(f"\n▶️ Evoluindo com Nível {nivel}...")
        input("⏎ Pressione Enter para iniciar...")
        
        resultados_evolucao = []
        filtros = FILTROS_POR_NIVEL.get(nivel, {})
        
        for idx in range(concursos_teste):
            concurso_alvo = resultados_db[idx]
            dados_disponiveis = resultados_db[idx + 1:]
            resultado_anterior = dados_disponiveis[0]['numeros'] if dados_disponiveis else None
            
            print(f"\n{'─' * 70}")
            print(f"📍 Testando concurso {concurso_alvo['concurso']} ({idx + 1}/{concursos_teste})")
            print(f"   Resultado real: {concurso_alvo['numeros']}")
            
            # Exclusão INVERTIDA v3.0
            scores = self._calcular_score_exclusao(dados_disponiveis)
            excluidos = {scores[0]['num'], scores[1]['num']}
            pool_23 = [n for n in range(1, 26) if n not in excluidos]
            
            print(f"   Excluídos: {sorted(excluidos)} | Pool: {len(pool_23)}")
            
            inicio = datetime.now()
            
            # Gerar combinações COM filtros Pool 23
            combinacoes_validas = []
            for combo in combinations(pool_23, 15):
                if self._aplicar_filtro_pool23(combo, filtros, resultado_anterior):
                    combinacoes_validas.append(list(combo))
                    if len(combinacoes_validas) >= self.populacao:
                        break
            
            print(f"   Combinações válidas (filtro N{nivel}): {len(combinacoes_validas)}")
            
            # Se não tiver suficientes, relaxar
            if len(combinacoes_validas) < 10:
                print(f"   ⚠️ Poucas combinações, usando nível 0...")
                for combo in combinations(pool_23, 15):
                    combinacoes_validas.append(list(combo))
                    if len(combinacoes_validas) >= self.populacao:
                        break
            
            # Verificar acertos de TODAS as combinações
            melhor_acertos = 0
            melhor_combinacao = []
            total_11_mais = 0
            
            for combo in combinacoes_validas:
                acertos = self._verificar_acertos(combo, concurso_alvo['numeros'])
                if acertos > melhor_acertos:
                    melhor_acertos = acertos
                    melhor_combinacao = combo
                if acertos >= 11:
                    total_11_mais += 1
            
            # Atualizar estatísticas das estratégias
            self._atualizar_pesos('exclusao_quentes', melhor_acertos)
            self.sessao_geracoes += 1
            
            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000
            
            resultado = ResultadoEvolucao(
                geracao=self.sessao_geracoes,
                concurso_testado=concurso_alvo['concurso'],
                combinacao_gerada=melhor_combinacao,
                numeros_sorteados=concurso_alvo['numeros'],
                acertos=melhor_acertos,
                estrategia_principal=f"pool23_N{nivel}",
                pesos_estrategias=self._resumir_pesos(),
                tempo_ms=tempo_ms,
                sucesso_minimo=melhor_acertos >= 11
            )
            
            resultados_evolucao.append(resultado)
            self.sessao_acertos.append(melhor_acertos)
            
            if melhor_acertos > self.estado.melhor_acerto:
                self.estado.melhor_acerto = melhor_acertos
                self.estado.melhor_combinacao = melhor_combinacao
            
            emoji = "🎯" if melhor_acertos >= 13 else ("✅" if melhor_acertos >= 11 else "📊")
            print(f"   {emoji} Melhor: {melhor_acertos} acertos | Com 11+: {total_11_mais}/{len(combinacoes_validas)}")
        
        self._gerar_relatorio(resultados_evolucao)
        
        # Salvar último concurso treinado
        self.estado.ultimo_concurso_treinado = resultados_db[0]['concurso']
        self._salvar_estado()
        
        return resultados_evolucao
    
    def _evolucao_comparativa(self, resultados_db: List[Dict], concursos_teste: int,
                               niveis: List[int]) -> List[ResultadoEvolucao]:
        """
        Compara TODOS os níveis de filtro e APRENDE qual é o melhor!
        Isso é o VERDADEIRO aprendizado evolutivo baseado nos resultados da Opção 31.
        """
        print(f"\n" + "=" * 70)
        print(f"🧬 EVOLUÇÃO COMPARATIVA - APRENDENDO O MELHOR NÍVEL POOL 23")
        print(f"=" * 70)
        print(f"   Níveis a testar: {niveis}")
        print(f"   Concursos: {concursos_teste}")
        input("\n⏎ Pressione Enter para iniciar (pode demorar)...")
        
        # Estatísticas por nível
        stats_por_nivel = {nivel: {
            'acertos_total': 0,
            'combos_testadas': 0,
            'taxa_11_mais': 0,
            'jackpots': 0,
            'concursos_com_11': 0,
            'melhor_acerto': 0,
            'acertos_lista': []
        } for nivel in niveis}
        
        resultados_evolucao = []
        
        for idx in range(concursos_teste):
            concurso_alvo = resultados_db[idx]
            dados_disponiveis = resultados_db[idx + 1:]
            resultado_anterior = dados_disponiveis[0]['numeros'] if dados_disponiveis else None
            
            print(f"\n{'─' * 70}")
            print(f"📍 Concurso {concurso_alvo['concurso']} ({idx + 1}/{concursos_teste})")
            print(f"   Resultado: {concurso_alvo['numeros']}")
            
            # Exclusão INVERTIDA v3.0
            scores = self._calcular_score_exclusao(dados_disponiveis)
            excluidos = {scores[0]['num'], scores[1]['num']}
            pool_23 = [n for n in range(1, 26) if n not in excluidos]
            
            melhor_nivel = None
            melhor_acertos = 0
            
            # Testar cada nível
            for nivel in niveis:
                filtros = FILTROS_POR_NIVEL.get(nivel, {})
                
                # Gerar combinações
                combinacoes = []
                for combo in combinations(pool_23, 15):
                    if self._aplicar_filtro_pool23(combo, filtros, resultado_anterior):
                        combinacoes.append(list(combo))
                        if len(combinacoes) >= 100:  # Limitar para velocidade
                            break
                
                if len(combinacoes) == 0:
                    continue
                
                # Verificar acertos
                acertos_nivel = []
                for combo in combinacoes:
                    acertos = self._verificar_acertos(combo, concurso_alvo['numeros'])
                    acertos_nivel.append(acertos)
                
                max_acertos = max(acertos_nivel) if acertos_nivel else 0
                taxa_11 = sum(1 for a in acertos_nivel if a >= 11) / len(acertos_nivel) * 100 if acertos_nivel else 0
                
                # Atualizar stats
                stats_por_nivel[nivel]['acertos_total'] += sum(acertos_nivel)
                stats_por_nivel[nivel]['combos_testadas'] += len(combinacoes)
                stats_por_nivel[nivel]['acertos_lista'].extend(acertos_nivel)
                if max_acertos >= 11:
                    stats_por_nivel[nivel]['concursos_com_11'] += 1
                if max_acertos == 15:
                    stats_por_nivel[nivel]['jackpots'] += 1
                if max_acertos > stats_por_nivel[nivel]['melhor_acerto']:
                    stats_por_nivel[nivel]['melhor_acerto'] = max_acertos
                
                if max_acertos > melhor_acertos:
                    melhor_acertos = max_acertos
                    melhor_nivel = nivel
                
                # Mini relatório
                emoji = "🎯" if max_acertos >= 13 else ("✅" if max_acertos >= 11 else "•")
                print(f"   {emoji} N{nivel}: max={max_acertos} | 11+={taxa_11:.0f}% ({len(combinacoes)} combos)")
            
            self.sessao_geracoes += 1
            
            # Registrar melhor resultado deste concurso
            if melhor_nivel is not None:
                resultado = ResultadoEvolucao(
                    geracao=self.sessao_geracoes,
                    concurso_testado=concurso_alvo['concurso'],
                    combinacao_gerada=[],
                    numeros_sorteados=concurso_alvo['numeros'],
                    acertos=melhor_acertos,
                    estrategia_principal=f"melhor_N{melhor_nivel}",
                    pesos_estrategias={f"N{n}": "..." for n in niveis},
                    tempo_ms=0,
                    sucesso_minimo=melhor_acertos >= 11
                )
                resultados_evolucao.append(resultado)
        
        # RELATÓRIO FINAL - APRENDIZADO
        print(f"\n" + "=" * 70)
        print(f"📊 RELATÓRIO DE APRENDIZADO - COMPARAÇÃO DE NÍVEIS")
        print(f"=" * 70)
        
        print(f"\n{'NÍVEL':<8} {'MÉDIA':<8} {'TAXA 11+':<12} {'JACKPOTS':<10} {'CONC.11+':<10}")
        print(f"{'─'*50}")
        
        ranking = []
        for nivel in niveis:
            stats = stats_por_nivel[nivel]
            if stats['combos_testadas'] > 0:
                media = np.mean(stats['acertos_lista']) if stats['acertos_lista'] else 0
                taxa_11 = sum(1 for a in stats['acertos_lista'] if a >= 11) / len(stats['acertos_lista']) * 100
                conc_11_pct = stats['concursos_com_11'] / concursos_teste * 100
                
                ranking.append((nivel, media, taxa_11, stats['jackpots'], conc_11_pct))
                
                print(f"N{nivel:<7} {media:<8.2f} {taxa_11:<12.1f}% {stats['jackpots']:<10} {conc_11_pct:.0f}%")
        
        # Encontrar melhor nível (por taxa de 11+)
        if ranking:
            melhor = max(ranking, key=lambda x: (x[2], x[1]))  # Taxa 11+ primeiro, depois média
            nivel_aprendido = melhor[0]
            
            print(f"\n🏆 MELHOR NÍVEL APRENDIDO: N{nivel_aprendido}")
            print(f"   Taxa 11+: {melhor[2]:.1f}%")
            print(f"   Média: {melhor[1]:.2f}")
            print(f"   Jackpots: {melhor[3]}")
            
            # SALVAR APRENDIZADO
            self.estado.nivel_preferido = nivel_aprendido
            self.estado.historico_evolucao.append({
                'data': datetime.now().isoformat(),
                'concursos_testados': concursos_teste,
                'niveis_comparados': niveis,
                'nivel_aprendido': nivel_aprendido,
                'taxa_11': melhor[2],
                'ranking': ranking
            })
            
            # Salvar último concurso treinado
            self.estado.ultimo_concurso_treinado = resultados_db[0]['concurso']
            self._salvar_estado()
            
            print(f"\n✅ Nível N{nivel_aprendido} salvo como preferido para próximas gerações!")
        
        return resultados_evolucao
    
    def validar_nivel_atual(self, janela: int = 20) -> Dict:
        """
        Valida se o nível aprendido ainda é o melhor nos últimos N sorteios.
        Retorna diagnóstico com sugestão de ação.
        """
        print(f"\n🔍 Validando nível atual nos últimos {janela} sorteios...")
        
        resultados_db = self._carregar_resultados()
        nivel_atual = getattr(self.estado, 'nivel_preferido', 3)
        ultimo_treinado = getattr(self.estado, 'ultimo_concurso_treinado', 0)
        ultimo_db = resultados_db[0]['concurso']
        
        # Quantos novos desde último treino?
        novos = ultimo_db - ultimo_treinado if ultimo_treinado > 0 else ultimo_db
        
        print(f"   • Nível aprendido: N{nivel_atual}")
        print(f"   • Último treino: concurso {ultimo_treinado}")
        print(f"   • Último no DB: concurso {ultimo_db}")
        print(f"   • Novos sorteios: {novos}")
        
        # Testar níveis nos últimos N sorteios
        niveis_teste = [nivel_atual - 1, nivel_atual, nivel_atual + 1]
        niveis_teste = [n for n in niveis_teste if 0 <= n <= 6]
        
        stats = {}
        for nivel in niveis_teste:
            filtros = FILTROS_POR_NIVEL.get(nivel, {})
            taxa_11 = 0
            total = 0
            
            for idx in range(min(janela, len(resultados_db) - 30)):
                concurso = resultados_db[idx]
                dados_anteriores = resultados_db[idx + 1:]
                resultado_anterior = dados_anteriores[0]['numeros'] if dados_anteriores else None
                
                # Exclusão
                scores = self._calcular_score_exclusao(dados_anteriores)
                excluidos = {scores[0]['num'], scores[1]['num']}
                pool_23 = [n for n in range(1, 26) if n not in excluidos]
                
                # Testar
                count_11 = 0
                tested = 0
                for combo in combinations(pool_23, 15):
                    if self._aplicar_filtro_pool23(combo, filtros, resultado_anterior):
                        acertos = self._verificar_acertos(list(combo), concurso['numeros'])
                        if acertos >= 11:
                            count_11 += 1
                        tested += 1
                        if tested >= 50:  # Amostra
                            break
                
                if tested > 0:
                    taxa_11 += count_11 / tested
                    total += 1
            
            if total > 0:
                stats[nivel] = taxa_11 / total * 100
                print(f"   • N{nivel}: taxa 11+ = {stats[nivel]:.1f}%")
        
        # Diagnóstico
        melhor_nivel = max(stats.keys(), key=lambda n: stats[n]) if stats else nivel_atual
        
        resultado = {
            'nivel_atual': nivel_atual,
            'melhor_recente': melhor_nivel,
            'novos_sorteios': novos,
            'precisa_retreinar': melhor_nivel != nivel_atual or novos >= 10,
            'stats': stats
        }
        
        if resultado['precisa_retreinar']:
            if melhor_nivel != nivel_atual:
                print(f"\n⚠️  ALERTA: Nível N{melhor_nivel} parece melhor nos últimos {janela} sorteios!")
            if novos >= 10:
                print(f"⚠️  ALERTA: {novos} novos sorteios desde último treino!")
            print(f"   💡 Recomendação: Execute evolução com modo 2 ou 3")
        else:
            print(f"\n✅ Nível N{nivel_atual} ainda é o melhor!")
        
        return resultado
    
    def treinar_incremental(self) -> List[ResultadoEvolucao]:
        """
        Treina APENAS os novos sorteios desde a última execução.
        Mais rápido e mantém aprendizado atualizado.
        """
        resultados_db = self._carregar_resultados()
        ultimo_treinado = getattr(self.estado, 'ultimo_concurso_treinado', 0)
        ultimo_db = resultados_db[0]['concurso']
        
        if ultimo_treinado == 0:
            print("⚠️  Nenhum treino anterior. Execute evolução completa primeiro (opção 1, modo 2).")
            return []
        
        # Quantos novos?
        novos = 0
        for i, r in enumerate(resultados_db):
            if r['concurso'] <= ultimo_treinado:
                novos = i
                break
        
        if novos == 0:
            print("✅ Nenhum novo sorteio desde último treino!")
            return []
        
        print(f"\n🔄 TREINO INCREMENTAL")
        print(f"   • Último treinado: {ultimo_treinado}")
        print(f"   • Último no DB: {ultimo_db}")
        print(f"   • Novos sorteios: {novos}")
        
        return self._evolucao_comparativa(resultados_db, novos, [2, 3, 4])
    
    def _gerar_relatorio(self, resultados: List[ResultadoEvolucao]):
        """Gera relatório final da evolução"""
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL - EVOLUÇÃO NEURAL")
        print("=" * 70)
        
        acertos = [r.acertos for r in resultados]
        sucessos = sum(1 for a in acertos if a >= 11)
        jackpots = sum(1 for a in acertos if a == 15)
        
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   • Concursos testados: {len(resultados)}")
        print(f"   • Gerações totais: {self.sessao_geracoes:,}")
        print(f"   • Tempo total: {(datetime.now() - self.sessao_inicio).total_seconds():.1f}s")
        
        print(f"\n🎯 ACERTOS:")
        print(f"   • Média: {np.mean(acertos):.2f} acertos")
        print(f"   • Máximo: {max(acertos)} acertos")
        print(f"   • Mínimo: {min(acertos)} acertos")
        print(f"   • Desvio padrão: {np.std(acertos):.2f}")
        
        print(f"\n✅ SUCESSOS (≥11 acertos):")
        print(f"   • Taxa: {sucessos}/{len(resultados)} ({sucessos/len(resultados)*100:.1f}%)")
        if jackpots > 0:
            print(f"   • 🏆 JACKPOTS (15): {jackpots}")
        
        print(f"\n🧠 EVOLUÇÃO DOS PESOS:")
        for nome, est in self.estrategias.items():
            barra = "█" * int(est.peso * 50)
            print(f"   • {nome:25s}: {est.peso:.3f} {barra}")
        
        print(f"\n📊 DISTRIBUIÇÃO DE ACERTOS:")
        for a in range(15, 9, -1):
            qtd = sum(1 for x in acertos if x == a)
            barra = "█" * qtd
            pct = qtd / len(acertos) * 100
            print(f"   {a:2d} acertos: {qtd:3d} ({pct:5.1f}%) {barra}")
        
        # Análise por estratégia
        print(f"\n📈 DESEMPENHO POR ESTRATÉGIA:")
        for nome, est in sorted(self.estrategias.items(), 
                                key=lambda x: x[1].taxa_sucesso, reverse=True):
            if est.tentativas > 0:
                emoji = "⭐" if est.taxa_sucesso > 0.3 else ("✅" if est.taxa_sucesso > 0.1 else "📊")
                print(f"   {emoji} {nome:25s}: taxa={est.taxa_sucesso:.3f} (n={est.tentativas})")
    
    def _carregar_estado(self):
        """Carrega estado persistente do arquivo"""
        estado_path = os.path.join(os.path.dirname(__file__), 'estado_agente_v2.json')
        if os.path.exists(estado_path):
            try:
                with open(estado_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    # Garantir campos novos para arquivos antigos
                    if 'nivel_preferido' not in dados:
                        dados['nivel_preferido'] = 3
                    if 'ultimo_concurso_treinado' not in dados:
                        dados['ultimo_concurso_treinado'] = 0
                    self.estado = EstadoAgente(**dados)
                    logger.info(f"Estado carregado: {self.estado.geracoes_totais} gerações anteriores")
            except Exception as e:
                logger.warning(f"Erro ao carregar estado: {e}")
    
    def _salvar_estado(self):
        """Salva estado persistente"""
        self.estado.geracoes_totais += self.sessao_geracoes
        self.estado.ultima_atualizacao = datetime.now().isoformat()
        self.estado.estrategias = {
            nome: {'peso': est.peso, 'taxa_sucesso': est.taxa_sucesso, 'tentativas': est.tentativas}
            for nome, est in self.estrategias.items()
        }
        
        estado_path = os.path.join(os.path.dirname(__file__), 'estado_agente_v2.json')
        try:
            with open(estado_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.estado), f, indent=2, ensure_ascii=False)
            logger.info(f"Estado salvo: {estado_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def gerar_previsao(self, qtd_combinacoes: int = 10) -> List[List[int]]:
        """
        Gera combinações otimizadas para o PRÓXIMO concurso
        usando as estratégias evoluídas
        """
        print("\n" + "=" * 70)
        print("🎯 GERAÇÃO DE PREVISÕES - PRÓXIMO CONCURSO")
        print("=" * 70)
        
        resultados = self._carregar_resultados()
        ultimo_concurso = resultados[0]['concurso']
        
        print(f"📊 Último concurso: {ultimo_concurso}")
        print(f"🎯 Prevendo para: {ultimo_concurso + 1}")
        print(f"📈 Combinações a gerar: {qtd_combinacoes}")
        print(f"🧠 Pesos atuais: {self._resumir_pesos()}")
        
        # Calcular exclusões
        scores = self._calcular_score_exclusao(resultados)
        excluidos = {scores[0]['num'], scores[1]['num']}
        
        print(f"\n🚫 Excluídos (INVERTIDA v3.0): {sorted(excluidos)}")
        print(f"   Top 3 quentes: {[c['num'] for c in scores[:3]]}")
        print(f"   Scores: {[(c['num'], c['score']) for c in scores[:3]]}")
        
        # Gerar combinações diversificadas
        combinacoes = []
        estrategias_usadas = Counter()
        
        for i in range(qtd_combinacoes * 10):  # Gera mais para selecionar as melhores
            comb, estrategia = self._gerar_combinacao_evolutiva(resultados, excluidos)
            
            # Verificar diversidade (não repetir combinações idênticas)
            if comb not in combinacoes:
                combinacoes.append(comb)
                estrategias_usadas[estrategia] += 1
            
            if len(combinacoes) >= qtd_combinacoes:
                break
        
        print(f"\n✅ {len(combinacoes)} combinações geradas:")
        for i, comb in enumerate(combinacoes, 1):
            print(f"   {i:2d}. {comb}")
        
        print(f"\n📊 Estratégias utilizadas:")
        for est, qtd in estrategias_usadas.most_common():
            print(f"   • {est}: {qtd}")
        
        return combinacoes
    
    def menu_interativo(self):
        """Menu interativo para o agente"""
        while True:
            # Calcular novos sorteios
            try:
                resultados_db = self._carregar_resultados()
                ultimo_db = resultados_db[0]['concurso']
                ultimo_treinado = getattr(self.estado, 'ultimo_concurso_treinado', 0)
                nivel_preferido = getattr(self.estado, 'nivel_preferido', 3)
                novos = ultimo_db - ultimo_treinado if ultimo_treinado > 0 else 0
            except:
                ultimo_db = 0
                novos = 0
                nivel_preferido = 3
            
            print("\n" + "=" * 70)
            print("🧠 AGENTE NEURÔNIOS EVOLUTIVO v2.0 + POOL 23")
            print("=" * 70)
            print(f"📊 Estado: {self.estado.geracoes_totais:,} gerações acumuladas")
            print(f"🏆 Melhor acerto histórico: {self.estado.melhor_acerto}")
            print(f"🎯 Nível Pool 23 aprendido: N{nivel_preferido}")
            print(f"📅 Último treino: concurso {ultimo_treinado} | Atual: {ultimo_db}")
            
            # Alerta de novos sorteios
            if novos >= 5:
                print(f"⚠️  ALERTA: {novos} novos sorteios! Considere retreinar.")
            
            print()
            print("📋 OPÇÕES:")
            print("1️⃣  🔄 Executar Ciclo Evolutivo (treinar com histórico)")
            print("2️⃣  🎯 Gerar Previsões (modo livre)")
            print("3️⃣  🎯 GERAR COM FILTROS POOL 23 ⭐⭐ RECOMENDADO!")
            print("4️⃣  📊 Ver Estatísticas das Estratégias")
            print("5️⃣  ⚙️ Configurar Parâmetros")
            print("6️⃣  🔍 Analisar Concurso Específico")
            print("7️⃣  💾 Resetar Estado (reiniciar aprendizado)")
            print("8️⃣  🔍 Validar Nível Atual (checar se ainda é o melhor)")
            print("9️⃣  🔄 Treinar Incremental (só novos sorteios)")
            print("0️⃣  🔙 Voltar")
            print("=" * 70)
            
            opcao = input("\n🎯 Escolha: ").strip()
            
            if opcao == "1":
                try:
                    print("   💡 Use valor alto (ex: 9999) para todo o histórico")
                    n = input("   Quantos concursos para teste? [ENTER=20]: ").strip()
                    n = int(n) if n else 20
                    self.executar_evolucao(n)
                except ValueError:
                    print("   ❌ Valor inválido")
                input("\n⏎ Enter para continuar...")
            
            elif opcao == "2":
                try:
                    n = input("   Quantas combinações? [ENTER=10]: ").strip()
                    n = int(n) if n else 10
                    combinacoes = self.gerar_previsao(n)
                    
                    # Opção de salvar
                    salvar = input("\n   💾 Salvar em arquivo? [S/N]: ").strip().upper()
                    if salvar == "S":
                        nome = f"previsao_agente_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        with open(nome, 'w') as f:
                            for comb in combinacoes:
                                f.write(' '.join(f'{n:02d}' for n in comb) + '\n')
                        print(f"   ✅ Salvo em: {nome}")
                except ValueError:
                    print("   ❌ Valor inválido")
                input("\n⏎ Enter para continuar...")
            
            elif opcao == "3":
                # NOVO: Gerar com filtros Pool 23
                self._gerar_pool23_interativo()
                input("\n⏎ Enter para continuar...")
            
            elif opcao == "4":
                self._mostrar_estatisticas()
                input("\n⏎ Enter para continuar...")
            
            elif opcao == "5":
                self._configurar_parametros()
            
            elif opcao == "6":
                self._analisar_concurso_especifico()
            
            elif opcao == "7":
                confirmar = input("   ⚠️ Resetar todo o aprendizado? [S/N]: ").strip().upper()
                if confirmar == "S":
                    self.estado = EstadoAgente()
                    for est in self.estrategias.values():
                        est.peso = 1.0 / len(self.estrategias)
                        est.sucesso_total = 0
                        est.tentativas = 0
                        est.taxa_sucesso = 0
                    self._salvar_estado()
                    print("   ✅ Estado resetado!")
                input("\n⏎ Enter para continuar...")
            
            elif opcao == "8":
                try:
                    j = input("   Janela de validação [ENTER=20]: ").strip()
                    j = int(j) if j else 20
                    self.validar_nivel_atual(j)
                except ValueError:
                    print("   ❌ Valor inválido")
                input("\n⏎ Enter para continuar...")
            
            elif opcao == "9":
                self.treinar_incremental()
                input("\n⏎ Enter para continuar...")
            
            elif opcao == "0":
                print("\n👋 Voltando...")
                break
            
            else:
                print("❌ Opção inválida")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GERAÇÃO COM FILTROS POOL 23 (mesmo conceito da Opção 31)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _aplicar_filtro_pool23(self, combo: Tuple[int, ...], filtros: Dict, 
                                resultado_anterior: List[int] = None) -> bool:
        """Aplica filtros validados do Pool 23"""
        numeros = list(combo)
        soma = sum(numeros)
        
        # Soma
        if 'soma_min' in filtros and soma < filtros['soma_min']:
            return False
        if 'soma_max' in filtros and soma > filtros['soma_max']:
            return False
        
        # Pares
        pares = sum(1 for n in numeros if n % 2 == 0)
        if 'pares_min' in filtros and pares < filtros['pares_min']:
            return False
        if 'pares_max' in filtros and pares > filtros['pares_max']:
            return False
        
        # Primos
        primos = sum(1 for n in numeros if n in PRIMOS)
        if 'primos_min' in filtros and primos < filtros['primos_min']:
            return False
        if 'primos_max' in filtros and primos > filtros['primos_max']:
            return False
        
        # Consecutivos (números em sequência tipo 1,2,3)
        if 'consecutivos_min' in filtros or 'consecutivos_max' in filtros:
            consecutivos = 0
            for i in range(len(numeros) - 1):
                if numeros[i + 1] - numeros[i] == 1:
                    consecutivos += 1
            consecutivos += 1  # Conta o primeiro
            
            if 'consecutivos_min' in filtros and consecutivos < filtros['consecutivos_min']:
                return False
            if 'consecutivos_max' in filtros and consecutivos > filtros['consecutivos_max']:
                return False
        
        # Gap máximo
        if 'gap_max' in filtros:
            max_gap = max(numeros[i + 1] - numeros[i] for i in range(len(numeros) - 1))
            if max_gap > filtros['gap_max']:
                return False
        
        # Sequência máxima
        if 'seq_max' in filtros:
            max_seq = 1
            current_seq = 1
            for i in range(len(numeros) - 1):
                if numeros[i + 1] - numeros[i] == 1:
                    current_seq += 1
                    max_seq = max(max_seq, current_seq)
                else:
                    current_seq = 1
            if max_seq > filtros['seq_max']:
                return False
        
        # Repetições do concurso anterior
        if resultado_anterior and ('rep_min' in filtros or 'rep_max' in filtros):
            reps = len(set(numeros) & set(resultado_anterior))
            if 'rep_min' in filtros and reps < filtros['rep_min']:
                return False
            if 'rep_max' in filtros and reps > filtros['rep_max']:
                return False
        
        # Qtde 6-25
        if filtros.get('usar_filtro_qtde_6_25'):
            qtde_6_25 = sum(1 for n in numeros if 6 <= n <= 25)
            valores_aceitos = filtros.get('qtde_6_25_valores', [10, 11, 12, 13])
            if qtde_6_25 not in valores_aceitos:
                return False
        
        return True
    
    def _gerar_pool23_interativo(self):
        """Menu interativo para geração com Pool 23"""
        print("\n" + "=" * 70)
        print("🎯 GERADOR COM FILTROS POOL 23 - MESMO CONCEITO DA OPÇÃO 31")
        print("=" * 70)
        print("   ✅ Usa exclusão INVERTIDA v3.0 (exclui quentes)")
        print("   ✅ Aplica filtros validados (soma, pares, primos, etc)")
        print("   ✅ Rankeia com estratégias neurais evolutivas")
        print("=" * 70)
        
        # Carregar dados
        resultados = self._carregar_resultados()
        ultimo_concurso = resultados[0]
        
        print(f"\n📊 Último concurso: {ultimo_concurso['concurso']}")
        print(f"   Resultado: {ultimo_concurso['numeros']}")
        print(f"🎯 Prevendo para: {ultimo_concurso['concurso'] + 1}")
        
        # Nível aprendido
        nivel_aprendido = getattr(self.estado, 'nivel_preferido', 3)
        
        # Escolher nível
        print(f"\n📊 NÍVEIS DE FILTRO DISPONÍVEIS:")
        print("   [0] Sem filtros (490k combos) - Conservador")
        print("   [1] Básico: soma 175-235, qtde_6_25")
        print("   [2] Médio: + consecutivos, gap")
        print(f"   [3] Balanceado: + pares, primos {' ⭐ APRENDIDO' if nivel_aprendido == 3 else ''}")
        print(f"   [4] Agressivo: + seq_max {' ⭐ APRENDIDO' if nivel_aprendido == 4 else ''}")
        print(f"   [5] Muito Agressivo: + repetições, núcleo {' ⭐ APRENDIDO' if nivel_aprendido == 5 else ''}")
        print(f"   [6] Ultra: filtros máximos {' ⭐ APRENDIDO' if nivel_aprendido == 6 else ''}")
        
        print(f"\n   🧠 Nível aprendido na evolução: {nivel_aprendido}")
        
        nivel_str = input(f"\n   Nível [ENTER={nivel_aprendido}]: ").strip()
        nivel = int(nivel_str) if nivel_str else nivel_aprendido
        nivel = max(0, min(6, nivel))
        
        # Quantidade
        qtd_str = input("   Quantas combinações? [ENTER=50]: ").strip()
        qtd = int(qtd_str) if qtd_str else 50
        
        print(f"\n🔧 Configuração:")
        print(f"   • Nível: {nivel}")
        print(f"   • Combinações: {qtd}")
        
        # Exclusão INVERTIDA v3.0
        print(f"\n🔥 PASSO 1: Exclusão INVERTIDA v3.0")
        scores = self._calcular_score_exclusao(resultados)
        excluidos = {scores[0]['num'], scores[1]['num']}
        print(f"   Excluídos (quentes): {sorted(excluidos)}")
        print(f"   Top 3 quentes: {[(c['num'], c['score']) for c in scores[:3]]}")
        
        # Pool 23
        pool_23 = [n for n in range(1, 26) if n not in excluidos]
        print(f"\n✅ PASSO 2: Pool {len(pool_23)}")
        print(f"   Números disponíveis: {pool_23}")
        
        # Aplicar filtros
        filtros = FILTROS_POR_NIVEL.get(nivel, {})
        print(f"\n🔧 PASSO 3: Aplicando filtros nível {nivel}")
        print(f"   Filtros: {list(filtros.keys())[:6]}...")
        
        print(f"\n⏳ Gerando combinações (pode demorar alguns segundos)...")
        
        # Gerar combinações válidas
        combinacoes_validas = []
        total_testadas = 0
        resultado_anterior = resultados[1]['numeros'] if len(resultados) > 1 else None
        
        import time
        start = time.time()
        
        for combo in combinations(pool_23, 15):
            total_testadas += 1
            if self._aplicar_filtro_pool23(combo, filtros, resultado_anterior):
                combinacoes_validas.append(list(combo))
                if len(combinacoes_validas) >= qtd * 10:  # Gera 10x para ter variedade
                    break
            
            # Feedback a cada 100k
            if total_testadas % 100000 == 0:
                print(f"   Testadas: {total_testadas:,} | Válidas: {len(combinacoes_validas):,}")
        
        tempo = time.time() - start
        print(f"   ✅ {len(combinacoes_validas):,} combinações válidas em {tempo:.1f}s")
        
        if len(combinacoes_validas) == 0:
            print(f"   ⚠️ Nenhuma combinação! Relaxando para nível 0...")
            for combo in combinations(pool_23, 15):
                combinacoes_validas.append(list(combo))
                if len(combinacoes_validas) >= qtd * 10:
                    break
            print(f"   ✅ {len(combinacoes_validas):,} combinações geradas")
        
        # Rankear usando estratégias neurais
        print(f"\n🧠 PASSO 4: Ranking neural")
        
        # Calcular scores para ranking
        freq = self._analisar_frequencias(resultados, 30)
        freq_recente = freq['freq_recente']
        
        combinacoes_rankeadas = []
        for combo in combinacoes_validas:
            # Score baseado nas estratégias evolutivas
            score = 0
            
            # Frequência recente (peso alto)
            score_freq = sum(freq_recente.get(n, 0) for n in combo) / 15
            score += self.estrategias['frequencia_recente'].peso * score_freq
            
            # Equilíbrio baixos/médios/altos
            baixos = sum(1 for n in combo if n <= 8)
            medios = sum(1 for n in combo if 9 <= n <= 17)
            altos = sum(1 for n in combo if n >= 18)
            desvio = abs(baixos - 5) + abs(medios - 6) + abs(altos - 4)
            score_eq = max(0, 10 - desvio)
            score += self.estrategias['par_impar'].peso * score_eq
            
            # Aleatoriedade (diversidade)
            score += self.estrategias['aleatorio_ponderado'].peso * random.random() * 5
            
            combinacoes_rankeadas.append((combo, score))
        
        # Ordenar por score
        combinacoes_rankeadas.sort(key=lambda x: x[1], reverse=True)
        
        # Selecionar top N
        combinacoes_finais = [c for c, s in combinacoes_rankeadas[:qtd]]
        
        print(f"   Top {len(combinacoes_finais)} selecionadas")
        
        # Resultado
        print(f"\n{'='*70}")
        print(f"✅ {len(combinacoes_finais)} COMBINAÇÕES GERADAS (Pool 23 + Neural):")
        print(f"{'='*70}")
        
        for i, combo in enumerate(combinacoes_finais[:15], 1):  # Mostra top 15
            soma = sum(combo)
            print(f"   {i:2d}. {combo} (soma={soma})")
        
        if len(combinacoes_finais) > 15:
            print(f"   ... e mais {len(combinacoes_finais) - 15}")
        
        # Salvar
        salvar = input("\n💾 Salvar em arquivo? [S/N]: ").strip().upper()
        if salvar == "S":
            nome = f"pool23_neural_{ultimo_concurso['concurso']+1}_N{nivel}_{datetime.now().strftime('%H%M%S')}.txt"
            with open(nome, 'w') as f:
                for combo in combinacoes_finais:
                    f.write(' '.join(f'{n:02d}' for n in combo) + '\n')
            print(f"   ✅ Salvo em: {nome}")
    
    def _mostrar_estatisticas(self):
        """Mostra estatísticas detalhadas das estratégias"""
        print("\n" + "=" * 70)
        print("📊 ESTATÍSTICAS DAS ESTRATÉGIAS")
        print("=" * 70)
        
        print(f"\n📈 Estado geral:")
        print(f"   • Gerações totais: {self.estado.geracoes_totais + self.sessao_geracoes:,}")
        print(f"   • Melhor acerto: {self.estado.melhor_acerto}")
        print(f"   • Sessão atual: {self.sessao_geracoes:,} gerações")
        
        if self.sessao_acertos:
            print(f"\n📊 Sessão atual:")
            print(f"   • Concursos testados: {len(self.sessao_acertos)}")
            print(f"   • Média de acertos: {np.mean(self.sessao_acertos):.2f}")
            print(f"   • Taxa ≥11: {sum(1 for a in self.sessao_acertos if a >= 11)/len(self.sessao_acertos)*100:.1f}%")
        
        print(f"\n🧠 Estratégias:")
        for nome, est in sorted(self.estrategias.items(), key=lambda x: x[1].peso, reverse=True):
            barra = "█" * int(est.peso * 40)
            print(f"   {nome:25s}: peso={est.peso:.3f} taxa={est.taxa_sucesso:.3f} n={est.tentativas:,}")
            print(f"   {' ' * 25}  {barra}")
    
    def _configurar_parametros(self):
        """Configura parâmetros do agente"""
        print("\n⚙️ CONFIGURAÇÃO DE PARÂMETROS")
        print(f"   Gerações: {self.geracoes_max}")
        print(f"   População: {self.populacao}")
        
        try:
            g = input(f"   Novas gerações [ENTER=manter]: ").strip()
            if g:
                self.geracoes_max = int(g)
            
            p = input(f"   Nova população [ENTER=manter]: ").strip()
            if p:
                self.populacao = int(p)
            
            print(f"   ✅ Configurado: {self.geracoes_max} gerações, {self.populacao} população")
        except ValueError:
            print("   ❌ Valor inválido")
    
    def _analisar_concurso_especifico(self):
        """Analisa um concurso específico"""
        print("\n🔍 ANÁLISE DE CONCURSO ESPECÍFICO")
        
        try:
            resultados = self._carregar_resultados()
            ultimo = resultados[0]['concurso']
            
            concurso = input(f"   Concurso a analisar [{ultimo-50} a {ultimo}]: ").strip()
            concurso = int(concurso)
            
            # Encontrar posição
            pos = None
            for i, r in enumerate(resultados):
                if r['concurso'] == concurso:
                    pos = i
                    break
            
            if pos is None:
                print("   ❌ Concurso não encontrado")
                return
            
            # Dados disponíveis ANTES desse concurso
            dados_antes = resultados[pos + 1:]
            resultado_real = resultados[pos]
            
            print(f"\n📊 Concurso {concurso}:")
            print(f"   Resultado real: {resultado_real['numeros']}")
            
            # O que teríamos previsto?
            scores = self._calcular_score_exclusao(dados_antes)
            excluidos = {scores[0]['num'], scores[1]['num']}
            
            print(f"\n🔥 TOP 5 QUENTES (excluir):")
            for c in scores[:5]:
                em_resultado = "✅" if c['num'] in resultado_real['numeros'] else "❌"
                print(f"   {c['num']:02d}: score={c['score']:.1f} consec={c['consecutivos']} {em_resultado}")
            
            # Verificar se exclusão funcionou
            excluidos_que_sairam = [n for n in excluidos if n in resultado_real['numeros']]
            if excluidos_que_sairam:
                print(f"\n   ⚠️ Excluídos que saíram: {excluidos_que_sairam}")
            else:
                print(f"\n   ✅ Exclusão correta! Nenhum dos {sorted(excluidos)} saiu")
            
            # Gerar algumas combinações e testar
            print(f"\n🎯 Teste de 100 combinações:")
            acertos_teste = []
            for _ in range(100):
                comb, _ = self._gerar_combinacao_evolutiva(dados_antes, excluidos)
                ac = self._verificar_acertos(comb, resultado_real['numeros'])
                acertos_teste.append(ac)
            
            print(f"   Média: {np.mean(acertos_teste):.2f}")
            print(f"   Max: {max(acertos_teste)}")
            print(f"   Taxa ≥11: {sum(1 for a in acertos_teste if a >= 11)}%")
            
        except ValueError:
            print("   ❌ Valor inválido")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        input("\n⏎ Enter para continuar...")


def main():
    """Função principal"""
    print("=" * 70)
    print("🧠 AGENTE NEURÔNIOS EVOLUTIVO v2.0 - LOTOSCOPE")
    print("   Sistema de IA com dados REAIS do SQL Server")
    print("=" * 70)
    
    try:
        agente = AgenteNeuroniosEvolutivo()
        agente.menu_interativo()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
