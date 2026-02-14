#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 SISTEMA DE APRENDIZADO COM JANELA DESLIZANTE (7.11)
========================================================
Sistema que aprende progressivamente usando janela deslizante de 30 concursos.

COMO FUNCIONA:
1. Carrega histórico completo da tabela Resultados_INT
2. Usa janela de 30 concursos para análise
3. Gera 3 tipos de combinações:
   - 50 focadas em ATRASADOS (números em dívida)
   - 50 focadas em QUENTES (números frequentes)
   - 50 EQUILIBRADAS (mix quentes + frios)
4. Valida contra o concurso subsequente (31º)
5. Aprende o que funciona melhor
6. Move a janela e repete até o fim
7. Exporta relatório com insights e palpites

VALORES DE REFERÊNCIA (Lotofácil):
- Aposta: R$ 3,50
- Prêmio 11 acertos: R$ 7,00
- Prêmio 12 acertos: R$ 14,00
- Prêmio 13 acertos: R$ 30,00
- Prêmio 14 acertos: R$ 1.000,00
- Prêmio 15 acertos: R$ 1.800.000,00

TAXA DE SUCESSO:
- Considerado sucesso quando prêmios > custo das apostas

INTEGRAÇÃO PADRÕES OCULTOS (NOVO):
- Usa padrões da tabela COMBINACOES_LOTOFACIL20_COMPLETO
- Aplica filtro de score para priorizar melhores combinações

Autor: LotoScope AI
Data: Janeiro 2026
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
from itertools import combinations
import random
import statistics

# Configurar paths
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'analisadores'))

from database_config import db_config

# Importar integrador de padrões ocultos
try:
    from integracao_padroes_ocultos import (
        PadroesOcultosIntegrador,
        obter_numeros_padroes_ocultos,
        calcular_score_padroes,
        filtrar_por_padroes_ocultos
    )
    PADROES_OCULTOS_DISPONIVEIS = True
except ImportError:
    PADROES_OCULTOS_DISPONIVEIS = False

# Constantes de valores
CUSTO_APOSTA = 3.50
PREMIO_11 = 7.00
PREMIO_12 = 14.00
PREMIO_13 = 35.00
PREMIO_14 = 1000.00
PREMIO_15 = 1800000.00

PREMIOS = {11: PREMIO_11, 12: PREMIO_12, 13: PREMIO_13, 14: PREMIO_14, 15: PREMIO_15}


class SistemaJanelaDeslizante:
    """
    Sistema de aprendizado com janela deslizante.
    Aprende progressivamente testando diferentes estratégias.
    """
    
    def __init__(self, tamanho_janela: int = 30, combos_por_estrategia: int = 50):
        """
        Inicializa o sistema.
        
        Args:
            tamanho_janela: Tamanho da janela de análise (padrão: 30 concursos)
            combos_por_estrategia: Combinações geradas por estratégia (padrão: 50)
        """
        self.tamanho_janela = tamanho_janela
        self.combos_por_estrategia = combos_por_estrategia
        self.db_config = db_config
        
        # Dados carregados
        self.historico_completo = []  # Lista de concursos {concurso, numeros: [1-15]}
        self.total_concursos = 0
        
        # Aprendizado
        self.arquivo_aprendizado = _BASE_DIR / 'aprendizado_janela_deslizante.json'
        self.aprendizado = self._carregar_aprendizado()
        
        # Estatísticas da sessão atual
        self.stats_sessao = {
            'atrasados': {'acertos': defaultdict(int), 'lucro_total': 0, 'custo_total': 0},
            'quentes': {'acertos': defaultdict(int), 'lucro_total': 0, 'custo_total': 0},
            'equilibrada': {'acertos': defaultdict(int), 'lucro_total': 0, 'custo_total': 0}
        }
        
        # Histórico de janelas processadas
        self.janelas_processadas = []
        
        # NOVO: Integração com padrões ocultos
        self.usar_padroes_ocultos = PADROES_OCULTOS_DISPONIVEIS
        self.integrador_padroes = None
        if self.usar_padroes_ocultos:
            try:
                self.integrador_padroes = PadroesOcultosIntegrador()
                print("✅ Padrões ocultos carregados para janela deslizante!")
            except Exception as e:
                print(f"⚠️ Padrões ocultos não disponíveis: {e}")
                self.usar_padroes_ocultos = False
        
    def _carregar_aprendizado(self) -> Dict:
        """Carrega aprendizado de sessões anteriores."""
        if self.arquivo_aprendizado.exists():
            try:
                with open(self.arquivo_aprendizado, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"   ⚠️ Erro ao carregar aprendizado: {e}")
        
        # Estrutura inicial de aprendizado
        return {
            'sessoes': [],
            'melhor_estrategia': None,
            'parametros_otimos': {
                'peso_atrasados': 1.0,
                'peso_quentes': 1.0,
                'peso_equilibrada': 1.0,
                'limite_atraso_minimo': 5,
                'limite_frequencia_quente': 0.6  # 60% do máximo
            },
            'insights': [],
            'taxa_sucesso_global': {
                'atrasados': {'tentativas': 0, 'sucessos': 0},
                'quentes': {'tentativas': 0, 'sucessos': 0},
                'equilibrada': {'tentativas': 0, 'sucessos': 0}
            },
            'acertos_por_estrategia': {
                'atrasados': {11: 0, 12: 0, 13: 0, 14: 0, 15: 0},
                'quentes': {11: 0, 12: 0, 13: 0, 14: 0, 15: 0},
                'equilibrada': {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
            }
        }
    
    def _salvar_aprendizado(self):
        """Salva aprendizado em arquivo JSON."""
        try:
            with open(self.arquivo_aprendizado, 'w', encoding='utf-8') as f:
                json.dump(self.aprendizado, f, indent=2, ensure_ascii=False, default=str)
            print(f"   ✅ Aprendizado salvo em: {self.arquivo_aprendizado}")
        except Exception as e:
            print(f"   ❌ Erro ao salvar aprendizado: {e}")
    
    def carregar_historico(self) -> bool:
        """Carrega histórico completo da tabela Resultados_INT."""
        print("\n📂 Carregando histórico completo...")
        
        try:
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
            
            resultados = self.db_config.execute_query(query)
            
            if not resultados:
                print("   ❌ Nenhum resultado encontrado!")
                return False
            
            self.historico_completo = []
            for row in resultados:
                self.historico_completo.append({
                    'concurso': row[0],
                    'numeros': sorted([row[i] for i in range(1, 16)])
                })
            
            self.total_concursos = len(self.historico_completo)
            print(f"   ✅ {self.total_concursos} concursos carregados")
            print(f"   📊 Primeiro: {self.historico_completo[0]['concurso']}, "
                  f"Último: {self.historico_completo[-1]['concurso']}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao carregar histórico: {e}")
            return False
    
    def analisar_janela(self, inicio: int, fim: int) -> Dict:
        """
        Analisa uma janela de concursos e calcula estatísticas.
        
        Args:
            inicio: Índice do primeiro concurso da janela
            fim: Índice do último concurso da janela
        
        Returns:
            Dict com análise da janela (frequências, atrasos, etc.)
        """
        janela = self.historico_completo[inicio:fim]
        
        # Frequência de cada número na janela
        frequencias = Counter()
        ultimo_aparecimento = {}  # número -> índice do último concurso
        
        for i, concurso in enumerate(janela):
            for num in concurso['numeros']:
                frequencias[num] += 1
                ultimo_aparecimento[num] = i
        
        tamanho = len(janela)
        
        # Calcular atraso (quantos concursos desde última aparição)
        atrasos = {}
        for num in range(1, 26):
            if num in ultimo_aparecimento:
                atrasos[num] = tamanho - 1 - ultimo_aparecimento[num]
            else:
                atrasos[num] = tamanho  # Nunca apareceu na janela
        
        # Classificar números
        freq_max = max(frequencias.values()) if frequencias else 1
        
        numeros_quentes = []  # Alta frequência
        numeros_frios = []    # Baixa frequência/alto atraso
        numeros_medios = []   # Médio
        
        for num in range(1, 26):
            freq = frequencias.get(num, 0)
            atraso = atrasos.get(num, tamanho)
            
            # Usar parâmetros do aprendizado
            params = self.aprendizado['parametros_otimos']
            
            if freq >= freq_max * params['limite_frequencia_quente']:
                numeros_quentes.append((num, freq, atraso))
            elif atraso >= params['limite_atraso_minimo']:
                numeros_frios.append((num, freq, atraso))
            else:
                numeros_medios.append((num, freq, atraso))
        
        # Ordenar
        numeros_quentes.sort(key=lambda x: x[1], reverse=True)  # Por frequência desc
        numeros_frios.sort(key=lambda x: x[2], reverse=True)    # Por atraso desc
        
        return {
            'frequencias': dict(frequencias),
            'atrasos': atrasos,
            'quentes': numeros_quentes,
            'frios': numeros_frios,
            'medios': numeros_medios,
            'primeiro_concurso': janela[0]['concurso'],
            'ultimo_concurso': janela[-1]['concurso']
        }
    
    def gerar_combinacoes_atrasados(self, analise: Dict, n: int = 50) -> List[List[int]]:
        """
        Gera combinações focadas em números ATRASADOS (em dívida).
        
        Estratégia: Prioriza números com maior atraso, combinados com alguns quentes
        para equilibrar.
        """
        frios = [x[0] for x in analise['frios'][:15]]  # Top 15 mais atrasados
        medios = [x[0] for x in analise['medios'][:10]]
        quentes = [x[0] for x in analise['quentes'][:5]]  # Alguns quentes para base
        
        # Pool de números disponíveis
        pool = list(set(frios + medios + quentes))
        if len(pool) < 15:
            # Completar com outros números
            todos = list(range(1, 26))
            random.shuffle(todos)
            for num in todos:
                if num not in pool:
                    pool.append(num)
                if len(pool) >= 20:
                    break
        
        # Se não há frios suficientes, usar pool geral
        if len(frios) < 5:
            frios = pool[:15]
        
        combinacoes = set()
        tentativas = 0
        max_tentativas = n * 100
        
        while len(combinacoes) < n and tentativas < max_tentativas:
            tentativas += 1
            
            # Montar combinação: usar o máximo de frios disponíveis
            max_frios = min(12, len(frios))
            min_frios = min(10, max_frios)  # Garantir que min <= max
            if min_frios < 1:
                min_frios = 1
            
            n_frios = random.randint(min_frios, max_frios) if max_frios >= min_frios else max_frios
            combo_frios = random.sample(frios, min(n_frios, len(frios)))
            
            restante = 15 - len(combo_frios)
            outros = [x for x in pool if x not in combo_frios]
            
            if len(outros) >= restante:
                combo_outros = random.sample(outros, restante)
                combo = tuple(sorted(combo_frios + combo_outros))
                combinacoes.add(combo)
            elif len(combo_frios) + len(outros) >= 15:
                # Usar todos os outros disponíveis
                combo = tuple(sorted(combo_frios + outros)[:15])
                combinacoes.add(combo)
        
        return [list(c) for c in combinacoes]
    
    def gerar_combinacoes_quentes(self, analise: Dict, n: int = 50) -> List[List[int]]:
        """
        Gera combinações focadas em números QUENTES (frequentes).
        
        Estratégia: Prioriza números com maior frequência.
        """
        quentes = [x[0] for x in analise['quentes'][:15]]
        medios = [x[0] for x in analise['medios'][:10]]
        
        pool = list(set(quentes + medios))
        if len(pool) < 15:
            todos = list(range(1, 26))
            random.shuffle(todos)
            for num in todos:
                if num not in pool:
                    pool.append(num)
                if len(pool) >= 20:
                    break
        
        # Se não há quentes suficientes, usar pool geral
        if len(quentes) < 5:
            quentes = pool[:15]
        
        combinacoes = set()
        tentativas = 0
        max_tentativas = n * 100
        
        while len(combinacoes) < n and tentativas < max_tentativas:
            tentativas += 1
            
            # Montar combinação: usar o máximo de quentes disponíveis
            max_quentes = min(12, len(quentes))
            min_quentes = min(10, max_quentes)  # Garantir que min <= max
            if min_quentes < 1:
                min_quentes = 1
            
            n_quentes = random.randint(min_quentes, max_quentes) if max_quentes >= min_quentes else max_quentes
            combo_quentes = random.sample(quentes, min(n_quentes, len(quentes)))
            
            restante = 15 - len(combo_quentes)
            outros = [x for x in pool if x not in combo_quentes]
            
            if len(outros) >= restante:
                combo_outros = random.sample(outros, restante)
                combo = tuple(sorted(combo_quentes + combo_outros))
                combinacoes.add(combo)
            elif len(combo_quentes) + len(outros) >= 15:
                combo = tuple(sorted(combo_quentes + outros)[:15])
                combinacoes.add(combo)
        
        return [list(c) for c in combinacoes]
    
    def gerar_combinacoes_equilibrada(self, analise: Dict, n: int = 50) -> List[List[int]]:
        """
        Gera combinações EQUILIBRADAS (mix de quentes e frios).
        
        Estratégia: 7-8 quentes + 7-8 frios para equilibrar
        """
        quentes = [x[0] for x in analise['quentes'][:12]]
        frios = [x[0] for x in analise['frios'][:12]]
        medios = [x[0] for x in analise['medios'][:8]]
        
        pool = list(set(quentes + frios + medios))
        
        # Garantir pool mínimo
        if len(pool) < 15:
            todos = list(range(1, 26))
            random.shuffle(todos)
            for num in todos:
                if num not in pool:
                    pool.append(num)
                if len(pool) >= 20:
                    break
        
        # Se não há quentes ou frios suficientes, usar pool
        if len(quentes) < 3:
            quentes = pool[:10]
        if len(frios) < 3:
            frios = pool[5:15]
        
        combinacoes = set()
        tentativas = 0
        max_tentativas = n * 100
        
        while len(combinacoes) < n and tentativas < max_tentativas:
            tentativas += 1
            
            # Equilibrar: usar o que estiver disponível
            max_quentes = min(8, len(quentes))
            min_quentes = min(7, max_quentes)
            if min_quentes < 1:
                min_quentes = 1
            
            max_frios = min(8, len(frios))
            min_frios = min(7, max_frios)
            if min_frios < 1:
                min_frios = 1
            
            n_quentes = random.randint(min_quentes, max_quentes) if max_quentes >= min_quentes else max(1, max_quentes)
            n_frios = random.randint(min_frios, max_frios) if max_frios >= min_frios else max(1, max_frios)
            
            combo_quentes = random.sample(quentes, min(n_quentes, len(quentes)))
            combo_frios = random.sample(frios, min(n_frios, len(frios)))
            
            base = list(set(combo_quentes + combo_frios))
            
            if len(base) < 15:
                restante = 15 - len(base)
                outros = [x for x in pool if x not in base]
                if len(outros) >= restante:
                    extras = random.sample(outros, restante)
                    base.extend(extras)
                else:
                    # Completar com números aleatórios
                    todos = list(range(1, 26))
                    random.shuffle(todos)
                    for num in todos:
                        if num not in base:
                            base.append(num)
                        if len(base) >= 15:
                            break
            
            if len(base) >= 15:
                combo = tuple(sorted(base[:15]))
                combinacoes.add(combo)
        
        return [list(c) for c in combinacoes]
    
    def _aplicar_filtro_padroes_ocultos(self, combinacoes: List[List[int]], 
                                         top_percentual: float = 0.7) -> List[List[int]]:
        """
        Aplica filtro de padrões ocultos para priorizar melhores combinações.
        
        Args:
            combinacoes: Lista de combinações a filtrar
            top_percentual: Percentual das melhores a manter (0.7 = 70%)
            
        Returns:
            Lista filtrada ordenada por score
        """
        if not self.usar_padroes_ocultos or not self.integrador_padroes:
            return combinacoes
        
        if not combinacoes:
            return []
        
        # Calcular score de cada combinação
        scored = []
        for combo in combinacoes:
            score = self.integrador_padroes.calcular_score_combinacao(combo)
            scored.append((combo, score))
        
        # Ordenar por score
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Manter top percentual
        quantidade = max(1, int(len(scored) * top_percentual))
        return [combo for combo, score in scored[:quantidade]]
    
    def gerar_combinacoes_padroes_ocultos(self, n: int = 50) -> List[List[int]]:
        """
        Gera combinações baseadas nos padrões ocultos da tabela
        COMBINACOES_LOTOFACIL20_COMPLETO.
        
        Esta é uma quarta estratégia que usa apenas os padrões descobertos.
        """
        if not self.usar_padroes_ocultos or not self.integrador_padroes:
            print("   ⚠️ Padrões ocultos não disponíveis")
            return []
        
        combinacoes = set()
        tentativas = 0
        max_tentativas = n * 100
        
        # Obter dados dos padrões
        numeros_prioritarios = self.integrador_padroes.obter_numeros_prioritarios(20)
        trios = self.integrador_padroes.obter_trios_prioritarios(5)
        
        while len(combinacoes) < n and tentativas < max_tentativas:
            tentativas += 1
            
            combo = set()
            
            # 50% de chance de começar com um trio
            if trios and random.random() < 0.5:
                trio = random.choice(trios)
                combo.update(trio)
            
            # Completar com números prioritários
            for num in numeros_prioritarios:
                if len(combo) >= 15:
                    break
                combo.add(num)
            
            # Se ainda falta, adicionar aleatório
            while len(combo) < 15:
                num = random.randint(1, 25)
                combo.add(num)
            
            combinacoes.add(tuple(sorted(list(combo)[:15])))
        
        return [list(c) for c in combinacoes]
        
    def validar_combinacoes(self, combinacoes: List[List[int]], resultado: List[int]) -> Dict:
        """
        Valida combinações contra um resultado real.
        
        Args:
            combinacoes: Lista de combinações geradas
            resultado: Números sorteados
        
        Returns:
            Dict com acertos e estatísticas
        """
        resultado_set = set(resultado)
        acertos_dist = defaultdict(int)  # acertos -> quantidade
        
        for combo in combinacoes:
            acertos = len(set(combo) & resultado_set)
            acertos_dist[acertos] += 1
        
        # Calcular lucro
        custo = len(combinacoes) * CUSTO_APOSTA
        lucro = 0
        for acertos, qtd in acertos_dist.items():
            if acertos in PREMIOS:
                lucro += PREMIOS[acertos] * qtd
        
        return {
            'acertos': dict(acertos_dist),
            'custo': custo,
            'lucro_bruto': lucro,
            'lucro_liquido': lucro - custo,
            'sucesso': lucro > custo,
            'total_combinacoes': len(combinacoes)
        }
    
    def processar_janela(self, idx_inicio: int) -> Optional[Dict]:
        """
        Processa uma janela e valida contra o próximo concurso.
        
        Args:
            idx_inicio: Índice do primeiro concurso da janela
        
        Returns:
            Dict com resultados ou None se não há próximo concurso
        """
        idx_fim = idx_inicio + self.tamanho_janela
        
        # Verificar se há concurso subsequente para validar
        if idx_fim >= len(self.historico_completo):
            return None
        
        # Analisar janela
        analise = self.analisar_janela(idx_inicio, idx_fim)
        
        # Resultado a validar (concurso subsequente)
        resultado_validacao = self.historico_completo[idx_fim]
        
        # Gerar combinações para cada estratégia
        combos_atrasados = self.gerar_combinacoes_atrasados(analise, self.combos_por_estrategia)
        combos_quentes = self.gerar_combinacoes_quentes(analise, self.combos_por_estrategia)
        combos_equilibrada = self.gerar_combinacoes_equilibrada(analise, self.combos_por_estrategia)
        
        # Validar cada estratégia
        val_atrasados = self.validar_combinacoes(combos_atrasados, resultado_validacao['numeros'])
        val_quentes = self.validar_combinacoes(combos_quentes, resultado_validacao['numeros'])
        val_equilibrada = self.validar_combinacoes(combos_equilibrada, resultado_validacao['numeros'])
        
        return {
            'janela_inicio': analise['primeiro_concurso'],
            'janela_fim': analise['ultimo_concurso'],
            'concurso_validacao': resultado_validacao['concurso'],
            'resultado_real': resultado_validacao['numeros'],
            'atrasados': val_atrasados,
            'quentes': val_quentes,
            'equilibrada': val_equilibrada
        }
    
    def atualizar_estatisticas(self, resultado_janela: Dict):
        """Atualiza estatísticas com resultado de uma janela."""
        for estrategia in ['atrasados', 'quentes', 'equilibrada']:
            dados = resultado_janela[estrategia]
            
            # Acertos
            for acertos, qtd in dados['acertos'].items():
                self.stats_sessao[estrategia]['acertos'][acertos] += qtd
                if acertos >= 11:
                    # Atualizar aprendizado global
                    self.aprendizado['acertos_por_estrategia'][estrategia][acertos] = \
                        self.aprendizado['acertos_por_estrategia'][estrategia].get(acertos, 0) + qtd
            
            # Lucro/Custo
            self.stats_sessao[estrategia]['lucro_total'] += dados['lucro_bruto']
            self.stats_sessao[estrategia]['custo_total'] += dados['custo']
            
            # Taxa de sucesso
            self.aprendizado['taxa_sucesso_global'][estrategia]['tentativas'] += 1
            if dados['sucesso']:
                self.aprendizado['taxa_sucesso_global'][estrategia]['sucessos'] += 1
    
    def ajustar_parametros(self):
        """
        Ajusta parâmetros baseado no aprendizado acumulado.
        Chamado ao final de cada sessão.
        """
        # Calcular taxas de sucesso
        taxas = {}
        for estrategia in ['atrasados', 'quentes', 'equilibrada']:
            dados = self.aprendizado['taxa_sucesso_global'][estrategia]
            if dados['tentativas'] > 0:
                taxas[estrategia] = dados['sucessos'] / dados['tentativas']
            else:
                taxas[estrategia] = 0
        
        # Encontrar melhor estratégia
        if taxas:
            melhor = max(taxas, key=taxas.get)
            self.aprendizado['melhor_estrategia'] = melhor
            
            # Ajustar pesos proporcionalmente às taxas
            params = self.aprendizado['parametros_otimos']
            total_taxa = sum(taxas.values()) or 1
            
            params['peso_atrasados'] = max(0.5, min(2.0, taxas.get('atrasados', 0.5) / (total_taxa / 3)))
            params['peso_quentes'] = max(0.5, min(2.0, taxas.get('quentes', 0.5) / (total_taxa / 3)))
            params['peso_equilibrada'] = max(0.5, min(2.0, taxas.get('equilibrada', 0.5) / (total_taxa / 3)))
            
            # Ajustar limites baseado em acertos
            acertos_atrasados = sum(self.aprendizado['acertos_por_estrategia']['atrasados'].values())
            acertos_quentes = sum(self.aprendizado['acertos_por_estrategia']['quentes'].values())
            
            if acertos_atrasados > acertos_quentes * 1.2:
                # Atrasados performando melhor, ser mais agressivo
                params['limite_atraso_minimo'] = max(3, params['limite_atraso_minimo'] - 1)
            elif acertos_quentes > acertos_atrasados * 1.2:
                # Quentes performando melhor, ser mais conservador
                params['limite_frequencia_quente'] = min(0.7, params['limite_frequencia_quente'] + 0.05)
    
    def gerar_insight(self) -> str:
        """Gera insight baseado no aprendizado acumulado."""
        taxas = self.aprendizado['taxa_sucesso_global']
        acertos = self.aprendizado['acertos_por_estrategia']
        
        insights = []
        
        # Melhor estratégia
        if self.aprendizado['melhor_estrategia']:
            insights.append(f"Melhor estratégia: {self.aprendizado['melhor_estrategia'].upper()}")
        
        # Acertos por estratégia
        for estrategia in ['atrasados', 'quentes', 'equilibrada']:
            total_acertos = sum(acertos[estrategia].values())
            acertos_11_15 = sum(qtd for ac, qtd in acertos[estrategia].items() if ac >= 11)
            if total_acertos > 0:
                insights.append(f"{estrategia.capitalize()}: {acertos_11_15} acertos premiados")
        
        return "; ".join(insights) if insights else "Ainda acumulando dados..."
    
    def executar_sessao(self, exportar_report: bool = True) -> Dict:
        """
        Executa uma sessão completa de aprendizado.
        Processa todas as janelas do início ao fim.
        """
        print("\n" + "=" * 70)
        print("🧠 SISTEMA DE APRENDIZADO COM JANELA DESLIZANTE")
        print("=" * 70)
        
        # Carregar dados
        if not self.carregar_historico():
            return {'erro': 'Falha ao carregar histórico'}
        
        # Calcular total de janelas
        total_janelas = self.total_concursos - self.tamanho_janela
        print(f"\n📊 Total de janelas a processar: {total_janelas}")
        print(f"   Tamanho da janela: {self.tamanho_janela} concursos")
        print(f"   Combinações por estratégia: {self.combos_por_estrategia}")
        
        # Mostrar aprendizado anterior se existir
        if self.aprendizado['sessoes']:
            print(f"\n📚 Sessões anteriores: {len(self.aprendizado['sessoes'])}")
            print(f"   Melhor estratégia histórica: {self.aprendizado['melhor_estrategia'] or 'Indefinida'}")
        
        # Processar janelas
        print(f"\n🔄 Processando janelas...")
        inicio_sessao = datetime.now()
        
        resultados_janelas = []
        
        for i in range(total_janelas):
            resultado = self.processar_janela(i)
            
            if resultado is None:
                break
            
            resultados_janelas.append(resultado)
            self.atualizar_estatisticas(resultado)
            
            # Mostrar progresso a cada 10%
            progresso = (i + 1) / total_janelas * 100
            if (i + 1) % max(1, total_janelas // 10) == 0 or i == total_janelas - 1:
                print(f"   ▓ {progresso:5.1f}% | Janela {i+1}/{total_janelas} | "
                      f"Concurso {resultado['concurso_validacao']}")
        
        duracao = (datetime.now() - inicio_sessao).total_seconds()
        print(f"\n✅ Processamento concluído em {duracao:.1f} segundos")
        
        # Ajustar parâmetros
        self.ajustar_parametros()
        
        # Gerar relatório da sessão
        relatorio = self._gerar_relatorio_sessao(resultados_janelas)
        
        # Salvar sessão no aprendizado
        self.aprendizado['sessoes'].append({
            'data': datetime.now().isoformat(),
            'janelas_processadas': len(resultados_janelas),
            'duracao_segundos': duracao,
            'estatisticas': {
                estrategia: {
                    'acertos': dict(self.stats_sessao[estrategia]['acertos']),
                    'lucro_total': self.stats_sessao[estrategia]['lucro_total'],
                    'custo_total': self.stats_sessao[estrategia]['custo_total']
                }
                for estrategia in ['atrasados', 'quentes', 'equilibrada']
            }
        })
        
        self.aprendizado['insights'].append({
            'data': datetime.now().isoformat(),
            'insight': self.gerar_insight()
        })
        
        # Verificar resultado futuro
        self._verificar_resultado_futuro()
        
        # Salvar aprendizado
        self._salvar_aprendizado()
        
        # Exportar relatório
        if exportar_report:
            self._exportar_relatorio(relatorio)
        
        return relatorio
    
    def _gerar_relatorio_sessao(self, resultados_janelas: List[Dict]) -> Dict:
        """Gera relatório da sessão atual com métricas de evolução."""
        
        # Estatísticas por estratégia
        stats = {}
        for estrategia in ['atrasados', 'quentes', 'equilibrada']:
            dados = self.stats_sessao[estrategia]
            custo = dados['custo_total']
            lucro = dados['lucro_total']
            
            stats[estrategia] = {
                'acertos': dict(dados['acertos']),
                'custo_total': custo,
                'lucro_bruto': lucro,
                'lucro_liquido': lucro - custo,
                'roi': ((lucro - custo) / custo * 100) if custo > 0 else 0,
                'taxa_sucesso': self.aprendizado['taxa_sucesso_global'][estrategia]
            }
            
            # Calcular métricas adicionais
            total_combos = sum(dados['acertos'].values())
            acertos_premiados = sum(qtd for ac, qtd in dados['acertos'].items() if ac >= 11)
            stats[estrategia]['total_combinacoes'] = total_combos
            stats[estrategia]['acertos_premiados'] = acertos_premiados
            stats[estrategia]['taxa_premio'] = (acertos_premiados / total_combos * 100) if total_combos > 0 else 0
            
            # Valor esperado por aposta
            stats[estrategia]['valor_esperado'] = (lucro / total_combos) if total_combos > 0 else 0
        
        # Melhor estratégia
        melhor = max(stats, key=lambda x: stats[x]['lucro_liquido'])
        
        # Calcular evolução em relação à sessão anterior
        evolucao = self._calcular_evolucao(stats)
        
        # Análise de breakeven
        breakeven = self._calcular_breakeven(stats)
        
        # Sugestões de melhoria
        sugestoes = self._gerar_sugestoes(stats)
        
        return {
            'data': datetime.now().isoformat(),
            'sessao_numero': len(self.aprendizado['sessoes']) + 1,
            'janelas_processadas': len(resultados_janelas),
            'estatisticas': stats,
            'melhor_estrategia': melhor,
            'parametros_atuais': self.aprendizado['parametros_otimos'].copy(),
            'insight': self.gerar_insight(),
            'evolucao': evolucao,
            'breakeven': breakeven,
            'sugestoes': sugestoes
        }
    
    def _calcular_evolucao(self, stats_atual: Dict) -> Dict:
        """Calcula % de evolução em relação à sessão anterior."""
        evolucao = {
            'tem_sessao_anterior': False,
            'melhoria_roi': {},
            'melhoria_taxa_premio': {},
            'tendencia': 'primeira_sessao'
        }
        
        if not self.aprendizado['sessoes']:
            return evolucao
        
        evolucao['tem_sessao_anterior'] = True
        sessao_anterior = self.aprendizado['sessoes'][-1]
        
        for estrategia in ['atrasados', 'quentes', 'equilibrada']:
            # ROI anterior
            stats_ant = sessao_anterior['estatisticas'].get(estrategia, {})
            custo_ant = stats_ant.get('custo_total', 0)
            lucro_ant = stats_ant.get('lucro_total', 0)
            roi_ant = ((lucro_ant - custo_ant) / custo_ant * 100) if custo_ant > 0 else 0
            
            # ROI atual
            roi_atual = stats_atual[estrategia]['roi']
            
            # Melhoria (menos negativo = melhor)
            melhoria_roi = roi_atual - roi_ant
            evolucao['melhoria_roi'][estrategia] = melhoria_roi
            
            # Taxa de prêmio anterior
            acertos_ant = stats_ant.get('acertos', {})
            total_ant = sum(acertos_ant.values()) if acertos_ant else 1
            premiados_ant = sum(qtd for ac, qtd in acertos_ant.items() if ac >= 11)
            taxa_ant = (premiados_ant / total_ant * 100) if total_ant > 0 else 0
            
            taxa_atual = stats_atual[estrategia]['taxa_premio']
            melhoria_taxa = taxa_atual - taxa_ant
            evolucao['melhoria_taxa_premio'][estrategia] = melhoria_taxa
        
        # Tendência geral
        melhorias_roi = list(evolucao['melhoria_roi'].values())
        media_melhoria = sum(melhorias_roi) / len(melhorias_roi) if melhorias_roi else 0
        
        if media_melhoria > 1:
            evolucao['tendencia'] = 'melhorando'
        elif media_melhoria < -1:
            evolucao['tendencia'] = 'piorando'
        else:
            evolucao['tendencia'] = 'estavel'
        
        evolucao['media_melhoria_roi'] = media_melhoria
        
        return evolucao
    
    def _calcular_breakeven(self, stats: Dict) -> Dict:
        """Calcula análise de breakeven para cada estratégia."""
        breakeven = {}
        
        for estrategia in ['atrasados', 'quentes', 'equilibrada']:
            dados = stats[estrategia]
            acertos = dados.get('acertos', {})
            total_combos = dados.get('total_combinacoes', 0)
            
            if total_combos == 0:
                breakeven[estrategia] = {'viavel': False, 'motivo': 'Sem dados'}
                continue
            
            # Calcular distribuição de acertos
            dist_acertos = {}
            for ac in range(5, 16):
                qtd = acertos.get(ac, 0)
                dist_acertos[ac] = (qtd / total_combos * 100) if total_combos > 0 else 0
            
            # Taxa de acertos 11+
            taxa_11_mais = sum(dist_acertos.get(ac, 0) for ac in range(11, 16))
            
            # Valor médio por prêmio
            lucro_bruto = dados.get('lucro_bruto', 0)
            acertos_premiados = dados.get('acertos_premiados', 0)
            valor_medio_premio = (lucro_bruto / acertos_premiados) if acertos_premiados > 0 else 0
            
            # Para breakeven: custo = lucro
            # Custo por combo = 3.50
            # Precisamos: taxa_premio * valor_medio >= 3.50
            taxa_necessaria = (CUSTO_APOSTA / valor_medio_premio * 100) if valor_medio_premio > 0 else 100
            
            breakeven[estrategia] = {
                'taxa_atual_11mais': round(taxa_11_mais, 2),
                'taxa_necessaria': round(taxa_necessaria, 2),
                'valor_medio_premio': round(valor_medio_premio, 2),
                'viavel': taxa_11_mais >= taxa_necessaria,
                'gap': round(taxa_11_mais - taxa_necessaria, 2),
                'dist_acertos': {k: round(v, 2) for k, v in dist_acertos.items() if v > 0}
            }
        
        return breakeven
    
    def _gerar_sugestoes(self, stats: Dict) -> List[str]:
        """Gera sugestões de melhoria baseadas nas estatísticas."""
        sugestoes = []
        
        # Encontrar melhor e pior estratégia
        rois = {e: stats[e]['roi'] for e in stats}
        melhor = max(rois, key=rois.get)
        pior = min(rois, key=rois.get)
        
        # Sugestão 1: Focar na melhor estratégia
        if rois[melhor] > rois[pior] + 5:
            sugestoes.append(f"📈 Aumentar peso da estratégia '{melhor.upper()}' que tem melhor ROI ({rois[melhor]:.1f}%)")
        
        # Sugestão 2: Analisar taxa de prêmios
        taxas = {e: stats[e]['taxa_premio'] for e in stats}
        if max(taxas.values()) < 15:
            sugestoes.append("⚠️ Taxa de prêmios baixa (<15%). Considerar reduzir quantidade de combinações e focar em qualidade")
        
        # Sugestão 3: Verificar acertos de 14/15
        for estrategia in stats:
            acertos = stats[estrategia].get('acertos', {})
            ac_14 = acertos.get(14, 0)
            ac_15 = acertos.get(15, 0)
            total = stats[estrategia].get('total_combinacoes', 1)
            
            if ac_14 > 0:
                taxa_14 = ac_14 / total * 100
                if taxa_14 > 0.01:  # > 0.01%
                    sugestoes.append(f"🎯 Estratégia '{estrategia}' tem {ac_14} acertos de 14 ({taxa_14:.3f}%). Potencial alto!")
        
        # Sugestão 4: Comparar atrasados vs quentes
        if stats['atrasados']['acertos_premiados'] > stats['quentes']['acertos_premiados'] * 1.2:
            sugestoes.append("🔄 Números atrasados gerando mais prêmios. Aumentar foco em 'dívidas'")
        elif stats['quentes']['acertos_premiados'] > stats['atrasados']['acertos_premiados'] * 1.2:
            sugestoes.append("🔥 Números quentes gerando mais prêmios. Seguir tendências recentes")
        
        # Sugestão 5: ROI muito negativo
        for estrategia in stats:
            if stats[estrategia]['roi'] < -80:
                sugestoes.append(f"🚨 ROI de '{estrategia}' muito baixo ({stats[estrategia]['roi']:.1f}%). Revisar parâmetros")
        
        # Sugestão 6: Breakeven
        custo_total = sum(stats[e]['custo_total'] for e in stats)
        lucro_total = sum(stats[e]['lucro_bruto'] for e in stats)
        if lucro_total > 0:
            combos_breakeven = int(custo_total / (lucro_total / sum(stats[e]['total_combinacoes'] for e in stats)))
            sugestoes.append(f"💡 Para breakeven, seria necessário ~{combos_breakeven} combinações por estratégia")
        
        if not sugestoes:
            sugestoes.append("✅ Parâmetros parecem equilibrados. Continue monitorando a evolução")
        
        return sugestoes

    def _verificar_resultado_futuro(self):
        """Pergunta ao usuário se há resultado futuro para validar."""
        print("\n" + "=" * 70)
        print("📋 VALIDAÇÃO DE RESULTADO FUTURO")
        print("=" * 70)
        
        ultimo_concurso = self.historico_completo[-1]['concurso']
        proximo_concurso = ultimo_concurso + 1
        
        print(f"\n   Último concurso processado: {ultimo_concurso}")
        print(f"   Próximo concurso esperado: {proximo_concurso}")
        
        resposta = input(f"\n   O resultado do concurso {proximo_concurso} já saiu? (s/n): ").strip().lower()
        
        if resposta == 's':
            print("\n   Digite os 15 números sorteados (separados por vírgula ou espaço):")
            entrada = input("   > ").strip()
            
            try:
                # Parsear números
                numeros = []
                for parte in entrada.replace(',', ' ').split():
                    numeros.append(int(parte.strip()))
                
                if len(numeros) != 15:
                    print(f"   ⚠️ Esperado 15 números, recebido {len(numeros)}")
                    return
                
                if not all(1 <= n <= 25 for n in numeros):
                    print("   ⚠️ Números devem estar entre 1 e 25")
                    return
                
                numeros = sorted(numeros)
                
                # Gerar palpites e validar
                print(f"\n   ✅ Resultado informado: {numeros}")
                print("   🔄 Gerando palpites com as 3 estratégias...")
                
                # Usar última janela para análise
                analise = self.analisar_janela(
                    len(self.historico_completo) - self.tamanho_janela,
                    len(self.historico_completo)
                )
                
                for estrategia in ['atrasados', 'quentes', 'equilibrada']:
                    if estrategia == 'atrasados':
                        combos = self.gerar_combinacoes_atrasados(analise, self.combos_por_estrategia)
                    elif estrategia == 'quentes':
                        combos = self.gerar_combinacoes_quentes(analise, self.combos_por_estrategia)
                    else:
                        combos = self.gerar_combinacoes_equilibrada(analise, self.combos_por_estrategia)
                    
                    validacao = self.validar_combinacoes(combos, numeros)
                    
                    print(f"\n   📊 {estrategia.upper()}:")
                    for acertos in sorted(validacao['acertos'].keys(), reverse=True):
                        print(f"      {acertos} acertos: {validacao['acertos'][acertos]}x")
                    print(f"      Lucro: R$ {validacao['lucro_liquido']:.2f}")
                    
                    # Atualizar aprendizado
                    self.atualizar_estatisticas({
                        estrategia: validacao,
                        **{e: {'acertos': {}, 'custo': 0, 'lucro_bruto': 0, 'sucesso': False}
                           for e in ['atrasados', 'quentes', 'equilibrada'] if e != estrategia}
                    })
                
            except ValueError as e:
                print(f"   ❌ Erro ao processar números: {e}")
        else:
            print("\n   📝 Sessão de aprendizado encerrada sem validação futura.")
    
    def gerar_palpites_futuro(self, quantidade: int = None) -> List[List[int]]:
        """
        Gera palpites para o próximo concurso baseado no aprendizado.
        
        Args:
            quantidade: Número de palpites (None = calcular automaticamente)
        
        Returns:
            Lista de combinações mais prováveis
        """
        print("\n" + "=" * 70)
        print("🎯 GERAÇÃO DE PALPITES PARA PRÓXIMO CONCURSO")
        print("=" * 70)
        
        # Usar última janela
        idx_inicio = len(self.historico_completo) - self.tamanho_janela
        analise = self.analisar_janela(idx_inicio, len(self.historico_completo))
        
        # Determinar quantidade se não especificada
        if quantidade is None:
            # Calcular mínimo para garantir acertos > 11
            # Baseado em histórico, ~2-5% das combinações têm 11+ acertos
            quantidade = max(20, 100 // max(1, int(self.aprendizado['parametros_otimos']['peso_equilibrada'] * 50)))
            print(f"   📊 Quantidade calculada automaticamente: {quantidade}")
        
        # Gerar combinações de cada estratégia
        pesos = self.aprendizado['parametros_otimos']
        
        n_atrasados = int(quantidade * pesos['peso_atrasados'] / 
                        (pesos['peso_atrasados'] + pesos['peso_quentes'] + pesos['peso_equilibrada']))
        n_quentes = int(quantidade * pesos['peso_quentes'] / 
                       (pesos['peso_atrasados'] + pesos['peso_quentes'] + pesos['peso_equilibrada']))
        n_equilibrada = quantidade - n_atrasados - n_quentes
        
        print(f"\n   🎲 Distribuição por estratégia:")
        print(f"      • Atrasados: {n_atrasados}")
        print(f"      • Quentes: {n_quentes}")
        print(f"      • Equilibrada: {n_equilibrada}")
        
        combos_atrasados = self.gerar_combinacoes_atrasados(analise, n_atrasados)
        combos_quentes = self.gerar_combinacoes_quentes(analise, n_quentes)
        combos_equilibrada = self.gerar_combinacoes_equilibrada(analise, n_equilibrada)
        
        # Combinar e remover duplicatas
        todas = combos_atrasados + combos_quentes + combos_equilibrada
        unicas = list({tuple(sorted(c)): c for c in todas}.values())
        
        print(f"\n   ✅ {len(unicas)} palpites únicos gerados")
        
        # Custo estimado
        custo = len(unicas) * CUSTO_APOSTA
        print(f"   💰 Custo estimado: R$ {custo:.2f}")
        
        return unicas
    
    def _exportar_relatorio(self, relatorio: Dict):
        """Exporta relatório em formato legível com métricas de evolução."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = _BASE_DIR / f"relatorio_aprendizado_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("🧠 RELATÓRIO DE APRENDIZADO COM JANELA DESLIZANTE\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"📅 Data: {relatorio['data']}\n")
            f.write(f"🔢 Sessão #: {relatorio.get('sessao_numero', 1)}\n")
            f.write(f"📊 Janelas processadas: {relatorio['janelas_processadas']}\n")
            f.write(f"🏆 Melhor estratégia: {relatorio['melhor_estrategia'].upper()}\n\n")
            
            # ========== EVOLUÇÃO ENTRE SESSÕES ==========
            evolucao = relatorio.get('evolucao', {})
            if evolucao.get('tem_sessao_anterior'):
                f.write("-" * 70 + "\n")
                f.write("📈 EVOLUÇÃO EM RELAÇÃO À SESSÃO ANTERIOR\n")
                f.write("-" * 70 + "\n\n")
                
                f.write(f"   Tendência geral: {evolucao.get('tendencia', 'N/A').upper()}\n")
                f.write(f"   Média de melhoria ROI: {evolucao.get('media_melhoria_roi', 0):+.2f}%\n\n")
                
                f.write("   Melhoria por estratégia (ROI):\n")
                for estrategia, melhoria in evolucao.get('melhoria_roi', {}).items():
                    sinal = "📈" if melhoria > 0 else "📉" if melhoria < 0 else "➡️"
                    f.write(f"      {sinal} {estrategia.capitalize()}: {melhoria:+.2f}%\n")
                
                f.write("\n   Melhoria por estratégia (Taxa de Prêmio):\n")
                for estrategia, melhoria in evolucao.get('melhoria_taxa_premio', {}).items():
                    sinal = "📈" if melhoria > 0 else "📉" if melhoria < 0 else "➡️"
                    f.write(f"      {sinal} {estrategia.capitalize()}: {melhoria:+.2f}%\n")
                f.write("\n")
            
            # ========== ESTATÍSTICAS POR ESTRATÉGIA ==========
            f.write("-" * 70 + "\n")
            f.write("📈 ESTATÍSTICAS POR ESTRATÉGIA\n")
            f.write("-" * 70 + "\n\n")
            
            for estrategia, dados in relatorio['estatisticas'].items():
                f.write(f"🎯 {estrategia.upper()}\n")
                f.write(f"   Custo total: R$ {dados['custo_total']:.2f}\n")
                f.write(f"   Lucro bruto: R$ {dados['lucro_bruto']:.2f}\n")
                f.write(f"   Lucro líquido: R$ {dados['lucro_liquido']:.2f}\n")
                f.write(f"   ROI: {dados['roi']:.1f}%\n")
                f.write(f"   Total combinações: {dados.get('total_combinacoes', 0):,}\n")
                f.write(f"   Acertos premiados (11+): {dados.get('acertos_premiados', 0):,}\n")
                f.write(f"   Taxa de prêmio: {dados.get('taxa_premio', 0):.2f}%\n")
                f.write(f"   Valor esperado/aposta: R$ {dados.get('valor_esperado', 0):.2f}\n")
                f.write(f"   Acertos:\n")
                for acertos in sorted(dados['acertos'].keys(), reverse=True):
                    f.write(f"      {acertos} acertos: {dados['acertos'][acertos]}x\n")
                f.write("\n")
            
            # ========== ANÁLISE DE BREAKEVEN ==========
            breakeven = relatorio.get('breakeven', {})
            if breakeven:
                f.write("-" * 70 + "\n")
                f.write("💰 ANÁLISE DE BREAKEVEN (PONTO DE EQUILÍBRIO)\n")
                f.write("-" * 70 + "\n\n")
                
                for estrategia, dados in breakeven.items():
                    viavel_emoji = "✅" if dados.get('viavel') else "❌"
                    f.write(f"   {estrategia.upper()}: {viavel_emoji}\n")
                    f.write(f"      Taxa atual (11+): {dados.get('taxa_atual_11mais', 0):.2f}%\n")
                    f.write(f"      Taxa necessária: {dados.get('taxa_necessaria', 0):.2f}%\n")
                    f.write(f"      Gap: {dados.get('gap', 0):+.2f}%\n")
                    f.write(f"      Valor médio prêmio: R$ {dados.get('valor_medio_premio', 0):.2f}\n")
                f.write("\n")
            
            # ========== SUGESTÕES DE MELHORIA ==========
            sugestoes = relatorio.get('sugestoes', [])
            if sugestoes:
                f.write("-" * 70 + "\n")
                f.write("💡 SUGESTÕES DE MELHORIA\n")
                f.write("-" * 70 + "\n\n")
                
                for i, sugestao in enumerate(sugestoes, 1):
                    f.write(f"   {i}. {sugestao}\n")
                f.write("\n")
            
            # ========== INSIGHT ==========
            f.write("-" * 70 + "\n")
            f.write("💡 INSIGHT GERAL\n")
            f.write("-" * 70 + "\n")
            f.write(f"{relatorio['insight']}\n\n")
            
            # ========== PARÂMETROS ==========
            f.write("-" * 70 + "\n")
            f.write("⚙️ PARÂMETROS OTIMIZADOS\n")
            f.write("-" * 70 + "\n")
            for param, valor in relatorio['parametros_atuais'].items():
                f.write(f"   {param}: {valor}\n")
            
            # ========== RESUMO EXECUTIVO ==========
            f.write("\n" + "=" * 70 + "\n")
            f.write("📋 RESUMO EXECUTIVO\n")
            f.write("=" * 70 + "\n\n")
            
            # Totais gerais
            custo_total = sum(relatorio['estatisticas'][e]['custo_total'] for e in relatorio['estatisticas'])
            lucro_total = sum(relatorio['estatisticas'][e]['lucro_bruto'] for e in relatorio['estatisticas'])
            roi_geral = ((lucro_total - custo_total) / custo_total * 100) if custo_total > 0 else 0
            
            f.write(f"   💵 Investimento total simulado: R$ {custo_total:,.2f}\n")
            f.write(f"   🎁 Retorno total simulado: R$ {lucro_total:,.2f}\n")
            f.write(f"   📊 ROI geral: {roi_geral:.1f}%\n")
            f.write(f"   🏆 Estratégia recomendada: {relatorio['melhor_estrategia'].upper()}\n")
            
            # Acertos especiais
            total_14 = sum(relatorio['estatisticas'][e]['acertos'].get(14, 0) for e in relatorio['estatisticas'])
            total_15 = sum(relatorio['estatisticas'][e]['acertos'].get(15, 0) for e in relatorio['estatisticas'])
            
            if total_14 > 0 or total_15 > 0:
                f.write(f"\n   🎯 ACERTOS ESPECIAIS:\n")
                if total_15 > 0:
                    f.write(f"      🏆 15 acertos (JACKPOT): {total_15}x\n")
                if total_14 > 0:
                    f.write(f"      ⭐ 14 acertos: {total_14}x\n")
        
        print(f"\n   📄 Relatório exportado: {arquivo}")


def main():
    """Função principal - interface interativa."""
    print("\n" + "=" * 70)
    print("🧠 SISTEMA DE APRENDIZADO COM JANELA DESLIZANTE (7.11)")
    print("=" * 70)
    print()
    print("Este sistema aprende progressivamente usando janela deslizante")
    print("de 30 concursos, testando 3 estratégias:")
    print("   • ATRASADOS: Foco em números em dívida")
    print("   • QUENTES: Foco em números frequentes")
    print("   • EQUILIBRADA: Mix de quentes e frios")
    print()
    print("O sistema valida cada janela contra o concurso seguinte,")
    print("aprende o que funciona melhor e ajusta parâmetros automaticamente.")
    print()
    
    sistema = SistemaJanelaDeslizante()
    
    while True:
        print("\n" + "=" * 70)
        print("📋 MENU")
        print("=" * 70)
        print("   1. Executar sessão de aprendizado completa")
        print("   2. Gerar palpites para próximo concurso")
        print("   3. Ver estatísticas de aprendizado")
        print("   4. Resetar aprendizado")
        print("   0. Voltar")
        
        opcao = input("\n🎯 Escolha uma opção: ").strip()
        
        if opcao == "1":
            sistema.executar_sessao()
            
        elif opcao == "2":
            if not sistema.historico_completo:
                sistema.carregar_historico()
            
            entrada = input("\n   Quantidade de palpites (Enter=automático): ").strip()
            quantidade = int(entrada) if entrada else None
            
            palpites = sistema.gerar_palpites_futuro(quantidade)
            
            # Perguntar se quer exportar
            if input("\n   Exportar palpites? (s/n): ").strip().lower() == 's':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                arquivo = _BASE_DIR / f"palpites_{timestamp}.txt"
                
                with open(arquivo, 'w', encoding='utf-8') as f:
                    for palpite in palpites:
                        linha = ",".join(f"{n:02d}" for n in palpite)
                        f.write(linha + "\n")
                
                print(f"   ✅ Palpites exportados: {arquivo}")
            
        elif opcao == "3":
            print("\n" + "=" * 70)
            print("📊 ESTATÍSTICAS DE APRENDIZADO")
            print("=" * 70)
            
            print(f"\n   Sessões realizadas: {len(sistema.aprendizado['sessoes'])}")
            print(f"   Melhor estratégia: {sistema.aprendizado['melhor_estrategia'] or 'Indefinida'}")
            
            print("\n   Taxa de sucesso por estratégia:")
            for estrategia in ['atrasados', 'quentes', 'equilibrada']:
                dados = sistema.aprendizado['taxa_sucesso_global'][estrategia]
                if dados['tentativas'] > 0:
                    taxa = dados['sucessos'] / dados['tentativas'] * 100
                    print(f"      • {estrategia.capitalize()}: {taxa:.1f}% ({dados['sucessos']}/{dados['tentativas']})")
            
            print("\n   Acertos por estratégia:")
            for estrategia in ['atrasados', 'quentes', 'equilibrada']:
                acertos = sistema.aprendizado['acertos_por_estrategia'][estrategia]
                total = sum(acertos.values())
                print(f"      • {estrategia.capitalize()}: {total} acertos (11+)")
                for n in [15, 14, 13, 12, 11]:
                    if acertos.get(n, 0) > 0:
                        print(f"         {n} acertos: {acertos[n]}x")
            
            if sistema.aprendizado['insights']:
                print("\n   Últimos insights:")
                for insight in sistema.aprendizado['insights'][-3:]:
                    print(f"      • {insight['insight']}")
            
        elif opcao == "4":
            if input("\n   ⚠️ Confirma reset do aprendizado? (s/n): ").strip().lower() == 's':
                # Resetar para estrutura inicial
                sistema.aprendizado = {
                    'sessoes': [],
                    'melhor_estrategia': None,
                    'parametros_otimos': {
                        'peso_atrasados': 1.0,
                        'peso_quentes': 1.0,
                        'peso_equilibrada': 1.0,
                        'limite_atraso_minimo': 5,
                        'limite_frequencia_quente': 0.6
                    },
                    'insights': [],
                    'taxa_sucesso_global': {
                        'atrasados': {'tentativas': 0, 'sucessos': 0},
                        'quentes': {'tentativas': 0, 'sucessos': 0},
                        'equilibrada': {'tentativas': 0, 'sucessos': 0}
                    },
                    'acertos_por_estrategia': {
                        'atrasados': {11: 0, 12: 0, 13: 0, 14: 0, 15: 0},
                        'quentes': {11: 0, 12: 0, 13: 0, 14: 0, 15: 0},
                        'equilibrada': {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
                    }
                }
                sistema._salvar_aprendizado()
                print("   ✅ Aprendizado resetado!")
            
        elif opcao == "0":
            break
        
        else:
            print("   ❌ Opção inválida!")
    
    print("\n👋 Até a próxima sessão de aprendizado!")


if __name__ == "__main__":
    main()
