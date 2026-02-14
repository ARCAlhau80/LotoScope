#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔍 ANALISADOR DE COMBINAÇÕES GERADAS v3.0
==========================================
⭐ FILTRA AS MELHORES DAS MELHORES ⭐
🧠 INSIGHTS AVANÇADOS BASEADOS EM ANÁLISE ESTATÍSTICA

Lê um arquivo TXT de combinações (gerado pelo Gerador Posicional Probabilístico)
e aplica TODOS os filtros/critérios do sistema LotoScope para selecionar
apenas as combinações mais promissoras.

FILTROS APLICADOS v3.0:
=== BÁSICOS ===
1. Soma (180-220 range ideal)
2. Pares/Ímpares (7/8 ou 8/7)
3. Primos (4-6 ideal)
4. Fibonacci (3-5 ideal)
5. Sequências (máx 4 consecutivas)
6. Faixas (01-05, 06-10, etc.)
7. Linhas/Colunas (distribuição no volante 5x5)
8. Números Quentes (mínimo presentes)
9. Números Frios (máximo permitido)
10. Repetições com último resultado (faixa ideal)

=== TRIOS/QUINTETOS ===
11. Trios Quentes (top 100 mais frequentes)
12. Trios Frios (bottom 100 menos frequentes)
13. Quintetos Quentes (top 200 mais frequentes)
14. Quintetos Frios (bottom 200 menos frequentes)

=== INSIGHTS v3.0 (NOVOS) ===
15. Índice de Dívida - trios frequentes + atrasados (candidatos a sair)
16. Números Pivô - números que conectam trios de alta frequência (10,11,13,20,25)
17. Momentum - trios que estão "quentes" no momento
18. Paridade de Trios - distribuição par/ímpar nos trios (3 pares = 96.8% ativo)
19. Ciclos de Recorrência - padrão médio de retorno por frequência

NOVIDADES v3.0:
- Análise de "dívida" de trios (freq≥700, atraso≥10)
- Números pivô identificados estatisticamente
- Momentum de trios (ganhando força recentemente)
- Score de paridade baseado em taxa de ativação real
- Ciclos de recorrência por categoria de frequência

Autor: LotoScope AI
Data: Janeiro 2026
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from collections import Counter
import random

# Configurar paths
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LOTOFACIL_LITE = os.path.dirname(_BASE_DIR)
sys.path.insert(0, _LOTOFACIL_LITE)
sys.path.insert(0, _BASE_DIR)

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False


class AnalisadorCombinacoesGeradas:
    """
    Analisador v2.0 que filtra combinações usando múltiplos critérios estatísticos.
    Seleciona apenas as "melhores das melhores" combinações.
    
    NOVIDADES v2.0:
    - Validação contra histórico real
    - Análise de linhas/colunas do volante
    - Score ponderado inteligente
    - Diversidade de seleção
    - Benchmark automático
    """
    
    # Conexão com banco
    CONN_STR = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-K6JPBDS;"
        "DATABASE=LOTOFACIL;"
        "Trusted_Connection=yes;"
    )
    
    # Constantes matemáticas
    PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
    
    # Volante 5x5 da Lotofácil
    LINHAS = {
        1: [1, 2, 3, 4, 5],
        2: [6, 7, 8, 9, 10],
        3: [11, 12, 13, 14, 15],
        4: [16, 17, 18, 19, 20],
        5: [21, 22, 23, 24, 25]
    }
    COLUNAS = {
        1: [1, 6, 11, 16, 21],
        2: [2, 7, 12, 17, 22],
        3: [3, 8, 13, 18, 23],
        4: [4, 9, 14, 19, 24],
        5: [5, 10, 15, 20, 25]
    }
    
    # Pesos para score ponderado (baseado em eficácia histórica)
    PESOS = {
        'soma': 25,
        'pares': 15,
        'primos': 10,
        'fibonacci': 5,
        'sequencias': 15,
        'faixas': 15,
        'linhas_colunas': 10,
        'quentes': 20,
        'frios': 10,
        'repeticoes': 15,
        'repeticoes_mesma_posicao': 15,  # NOVO: peso para repetidos na mesma posição
        'validacao_hist': 30,
        'trios': 25,      # peso para análise de trios
        'quintetos': 30,  # peso para análise de quintetos (mais valioso que trios)
        # NOVOS INSIGHTS v3.0
        'divida_trios': 20,      # trios frequentes + atrasados (prestes a sair)
        'numeros_pivo': 15,      # números que conectam trios frequentes
        'momentum': 20,          # trios ganhando força recentemente
        'paridade_trios': 10,    # distribuição par/ímpar nos trios
    }
    
    # Números PIVÔ - que formam os trios mais frequentes (baseado em análise)
    NUMEROS_PIVO = {20, 25, 10, 11, 13, 14, 24, 1, 3, 4}  # Top 10 conectores
    
    # Limites de paridade para trios (baseado em insight: 3 pares = 96.8% ativos)
    PARIDADE_IDEAL_TRIOS = {
        '3_pares': 0.968,      # 96.8% de taxa de ativação
        '2_pares_1_impar': 0.934,
        '1_par_2_impares': 0.874,
        '3_impares': 0.808,
    }
    
    # Configuração padrão dos filtros
    FILTROS_PADRAO = {
        'soma_min': 180,
        'soma_max': 220,
        'pares_min': 6,
        'pares_max': 9,
        'primos_min': 4,
        'primos_max': 7,
        'fibonacci_min': 3,
        'fibonacci_max': 6,
        'sequencias_max': 15,          # DESATIVADO (era 4) - eliminava 57% das boas
        'faixa_min': 2,
        'faixa_max': 5,
        'linha_min': 1,
        'linha_max': 5,                # RELAXADO (era 2-4) - eliminava 42% das boas
        'coluna_min': 1,
        'coluna_max': 5,               # RELAXADO (era 2-4) - eliminava 44% das boas
        'quentes_min': 4,
        'frios_max': 15,               # DESATIVADO (era 5) - eliminava 65% das boas
        'repeticoes_min': 7,           # ATUALIZADO: 96.6% dos sorteios têm 7-11 repetidos
        'repeticoes_max': 11,          # ATUALIZADO: baseado em análise estatística real
        'repeticoes_mesma_posicao_min': 0,   # NOVO: repetidos na MESMA posição
        'repeticoes_mesma_posicao_max': 5,   # NOVO: 84.6% dos sorteios têm 0-5
        'trios_quentes_min': 0,        # DESATIVADO (era 20) - eliminava 53% das boas
        'trios_frios_max': 500,        # DESATIVADO (era 10) - eliminava 75% das boas
        'trios_atrasados_min': 3,      # mínimo de trios atrasados (bonus)
        'quintetos_quentes_min': 0,    # DESATIVADO (era 5) - eliminava 37% das boas
        'quintetos_frios_max': 50,     # máximo de quintetos raros (bottom 200)
        'media_acertos_min': 8.5,  # Média realista (esperado ~9 acertos em 15/25)
        # NOVOS INSIGHTS v3.0
        'divida_trios_min': 3,         # mínimo de trios com "dívida" (freq>=700, atraso>=10)
        'numeros_pivo_min': 5,         # mínimo de números pivô na combinação
        'momentum_min': 2,             # mínimo de trios com momentum positivo
        'paridade_trios_score_min': 0.85,  # score mínimo de paridade dos trios
    }
    
    def __init__(self, filtros_customizados: Dict = None):
        self.filtros = self.FILTROS_PADRAO.copy()
        if filtros_customizados:
            self.filtros.update(filtros_customizados)
        
        self.combinacoes = []
        self.estatisticas = {}
        self.numeros_quentes = []
        self.numeros_frios = []
        self.ultimo_resultado = []
        self.historico_resultados = []
        
        # Dados de trios
        self.trios_quentes = set()   # Top 100 trios mais frequentes
        self.trios_frios = set()     # Bottom 100 trios menos frequentes
        self.trios_atrasados = set() # Trios com atraso >= 15 concursos
        self.trios_dados = {}        # Dict com todos os trios
        
        # NOVO: Dados de quintetos (calculado em Python - muito mais rápido que SQL)
        self.quintetos_quentes = set()  # Top 200 quintetos mais frequentes
        self.quintetos_frios = set()    # Bottom 200 quintetos menos frequentes
        self.quintetos_dados = {}       # Dict com todos os quintetos
        
        # NOVOS INSIGHTS v3.0
        self.trios_divida = set()       # Trios com "dívida" (freq>=700, atraso>=10)
        self.trios_momentum = set()     # Trios com momentum positivo (ganhando força)
        self.ultimo_concurso = 0        # Último concurso para cálculos
        
        if HAS_PYODBC:
            self._carregar_dados_historicos()
            self._carregar_dados_trios()
            self._carregar_dados_quintetos()
            self._calcular_insights_avancados()  # NOVO v3.0
    
    def _carregar_dados_historicos(self, ultimos_n: int = 100):
        """Carrega dados históricos do banco"""
        try:
            conn = pyodbc.connect(self.CONN_STR)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT TOP {ultimos_n} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT
                ORDER BY Concurso DESC
            """)
            
            rows = cursor.fetchall()
            
            if rows:
                self.ultimo_resultado = [int(rows[0][i+1]) for i in range(15)]
                self.historico_resultados = []
                for row in rows:
                    self.historico_resultados.append({
                        'concurso': int(row[0]),
                        'numeros': [int(row[i+1]) for i in range(15)]
                    })
            
            # Calcular quentes/frios com últimos 15 concursos
            contagem = Counter()
            for resultado in self.historico_resultados[:15]:
                contagem.update(resultado['numeros'])
            
            self.numeros_quentes = [n for n, _ in contagem.most_common(10)]
            
            todos_nums = set(range(1, 26))
            frios_contagem = [(n, contagem.get(n, 0)) for n in todos_nums]
            frios_contagem.sort(key=lambda x: x[1])
            self.numeros_frios = [n for n, _ in frios_contagem[:10]]
            
            conn.close()
            
            print(f"📊 Dados históricos carregados ({len(self.historico_resultados)} concursos):")
            print(f"   🔥 Quentes (últimos 15): {self.numeros_quentes}")
            print(f"   🥶 Frios (últimos 15): {self.numeros_frios}")
            print(f"   🎯 Último resultado: {self.ultimo_resultado}")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados históricos: {e}")
    
    def _carregar_dados_trios(self):
        """Carrega dados de trios da view CONTA_TRIOS_LOTO"""
        try:
            conn = pyodbc.connect(self.CONN_STR)
            cursor = conn.cursor()
            
            # Buscar último concurso para calcular atraso
            cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
            self.ultimo_concurso = cursor.fetchone()[0] or 3573
            
            # Carregar todos os trios
            cursor.execute("""
                SELECT num1, num2, num3, quantidade, UltimoConcurso 
                FROM dbo.CONTA_TRIOS_LOTO
            """)
            
            todos_trios = []
            for row in cursor.fetchall():
                trio = (int(row[0]), int(row[1]), int(row[2]))
                qtd = int(row[3])
                ultimo = int(row[4])
                atraso = self.ultimo_concurso - ultimo
                
                self.trios_dados[trio] = {'qtd': qtd, 'ultimo': ultimo, 'atraso': atraso}
                todos_trios.append((trio, qtd, atraso))
            
            # Top 100 mais frequentes (quentes)
            todos_trios_por_qtd = sorted(todos_trios, key=lambda x: x[1], reverse=True)
            self.trios_quentes = set(t[0] for t in todos_trios_por_qtd[:100])
            
            # Bottom 100 menos frequentes (frios)
            self.trios_frios = set(t[0] for t in todos_trios_por_qtd[-100:])
            
            # Trios atrasados (atraso >= 15 concursos)
            self.trios_atrasados = set(t[0] for t in todos_trios if t[2] >= 15)
            
            conn.close()
            
            print(f"   🎲 Trios carregados: {len(self.trios_dados):,}")
            print(f"      Quentes (top 100): {len(self.trios_quentes)}")
            print(f"      Frios (bottom 100): {len(self.trios_frios)}")
            print(f"      Atrasados (≥15 conc): {len(self.trios_atrasados)}")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar trios: {e}")
    
    def _carregar_dados_quintetos(self):
        """
        Carrega dados de quintetos calculando em Python (muito mais rápido que SQL).
        C(25,5) = 53.130 quintetos possíveis.
        """
        from itertools import combinations as iter_combinations
        from collections import Counter as PyCounter
        
        try:
            conn = pyodbc.connect(self.CONN_STR)
            cursor = conn.cursor()
            
            # Buscar último concurso
            cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
            ultimo_concurso = cursor.fetchone()[0] or 3573
            
            # Carregar todos os resultados
            cursor.execute("""
                SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT ORDER BY Concurso
            """)
            
            resultados = []
            for row in cursor.fetchall():
                concurso = int(row[0])
                numeros = tuple(sorted([int(row[i+1]) for i in range(15)]))
                resultados.append((concurso, numeros))
            
            conn.close()
            
            # Contar quintetos em Python (muito mais rápido que SQL)
            quintetos_count = PyCounter()
            quintetos_ultimo = {}
            
            for concurso, nums in resultados:
                for quinteto in iter_combinations(nums, 5):
                    quintetos_count[quinteto] += 1
                    quintetos_ultimo[quinteto] = concurso
            
            # Armazenar dados
            for quinteto, qtd in quintetos_count.items():
                self.quintetos_dados[quinteto] = {
                    'qtd': qtd,
                    'ultimo': quintetos_ultimo[quinteto]
                }
            
            # Top 200 mais frequentes (quentes)
            todos_quintetos = [(q, d['qtd']) for q, d in self.quintetos_dados.items()]
            todos_quintetos.sort(key=lambda x: x[1], reverse=True)
            self.quintetos_quentes = set(q[0] for q in todos_quintetos[:200])
            
            # Bottom 200 menos frequentes (frios)
            self.quintetos_frios = set(q[0] for q in todos_quintetos[-200:])
            
            print(f"   🎯 Quintetos calculados (Python): {len(self.quintetos_dados):,}")
            print(f"      Quentes (top 200): {len(self.quintetos_quentes)}")
            print(f"      Frios (bottom 200): {len(self.quintetos_frios)}")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar quintetos: {e}")
    
    def _calcular_insights_avancados(self):
        """
        NOVOS INSIGHTS v3.0 - Análises avançadas baseadas em descobertas estatísticas
        
        1. Índice de Dívida: trios frequentes (>=700) mas atrasados (>=10)
        2. Momentum: trios que apareceram recentemente e têm alta frequência
        3. Ciclos de Recorrência: padrão médio de retorno por frequência
        """
        if not self.trios_dados:
            return
        
        print("\n🧠 CALCULANDO INSIGHTS AVANÇADOS v3.0...")
        
        # 1. TRIOS COM "DÍVIDA" - frequentes mas atrasados
        # Baseado na análise: trios com freq>=700 e atraso>=10 são candidatos fortes
        for trio, dados in self.trios_dados.items():
            qtd = dados['qtd']
            atraso = dados['atraso']
            
            # Índice de dívida: quanto maior freq e maior atraso, maior a "dívida"
            if qtd >= 700 and atraso >= 10:
                indice_divida = (qtd / 700.0) * (atraso / 10.0)
                if indice_divida >= 1.0:
                    self.trios_divida.add(trio)
        
        # 2. TRIOS COM MOMENTUM - apareceram recentemente E são frequentes
        # Insight: trios que estão "quentes" no momento
        for trio, dados in self.trios_dados.items():
            qtd = dados['qtd']
            atraso = dados['atraso']
            
            # Momentum: alta frequência + aparição recente (últimos 5 concursos)
            if qtd >= 750 and atraso <= 5:
                self.trios_momentum.add(trio)
        
        # 3. Calcular ciclos médios de recorrência por categoria
        self.ciclos_recorrencia = self._calcular_ciclos_recorrencia()
        
        print(f"   💰 Trios com Dívida (freq≥700, atraso≥10): {len(self.trios_divida)}")
        print(f"   🚀 Trios com Momentum (freq≥750, atraso≤5): {len(self.trios_momentum)}")
        print(f"   🔄 Ciclos de recorrência calculados: {len(self.ciclos_recorrencia)} categorias")
    
    def _calcular_ciclos_recorrencia(self) -> Dict:
        """
        Calcula padrão médio de ciclos de recorrência por faixa de frequência.
        Insight: trios mais frequentes tendem a ter ciclos menores.
        """
        ciclos = {
            'muito_quente': {'freq_min': 780, 'freq_max': 999, 'atraso_medio': 0, 'count': 0},
            'quente': {'freq_min': 740, 'freq_max': 779, 'atraso_medio': 0, 'count': 0},
            'medio': {'freq_min': 700, 'freq_max': 739, 'atraso_medio': 0, 'count': 0},
            'frio': {'freq_min': 660, 'freq_max': 699, 'atraso_medio': 0, 'count': 0},
            'muito_frio': {'freq_min': 0, 'freq_max': 659, 'atraso_medio': 0, 'count': 0},
        }
        
        for trio, dados in self.trios_dados.items():
            qtd = dados['qtd']
            atraso = dados['atraso']
            
            for cat, cfg in ciclos.items():
                if cfg['freq_min'] <= qtd <= cfg['freq_max']:
                    cfg['atraso_medio'] = (cfg['atraso_medio'] * cfg['count'] + atraso) / (cfg['count'] + 1)
                    cfg['count'] += 1
                    break
        
        return ciclos
    
    def _analisar_insights_combinacao(self, combinacao: List[int]) -> Dict:
        """
        Analisa uma combinação usando os novos insights v3.0
        
        Returns:
            Dict com métricas dos novos insights
        """
        from itertools import combinations as iter_comb
        
        resultado = {
            'trios_divida': 0,          # Quantos trios com "dívida"
            'trios_momentum': 0,         # Quantos trios com momentum
            'numeros_pivo': 0,           # Quantos números pivô
            'score_paridade': 0.0,       # Score médio de paridade dos trios
            'indice_divida_total': 0.0,  # Soma do índice de dívida
            'ciclo_esperado': 0.0,       # Ciclo médio esperado dos trios
        }
        
        if not self.trios_dados:
            return resultado
        
        comb_set = set(combinacao)
        trios_da_comb = list(iter_comb(sorted(combinacao), 3))
        
        # Contar números pivô
        resultado['numeros_pivo'] = len(comb_set & self.NUMEROS_PIVO)
        
        paridades = []
        ciclos = []
        
        for trio in trios_da_comb:
            # Verificar se é trio com dívida
            if trio in self.trios_divida:
                resultado['trios_divida'] += 1
            
            # Verificar se é trio com momentum
            if trio in self.trios_momentum:
                resultado['trios_momentum'] += 1
            
            # Dados do trio
            if trio in self.trios_dados:
                dados = self.trios_dados[trio]
                
                # Calcular índice de dívida
                if dados['qtd'] >= 700 and dados['atraso'] >= 10:
                    resultado['indice_divida_total'] += (dados['qtd'] / 700.0) * (dados['atraso'] / 10.0)
                
                # Calcular paridade do trio
                pares = sum(1 for n in trio if n % 2 == 0)
                if pares == 3:
                    paridades.append(0.968)
                elif pares == 2:
                    paridades.append(0.934)
                elif pares == 1:
                    paridades.append(0.874)
                else:
                    paridades.append(0.808)
                
                # Estimar ciclo de recorrência baseado na frequência
                qtd = dados['qtd']
                if hasattr(self, 'ciclos_recorrencia'):
                    for cat, cfg in self.ciclos_recorrencia.items():
                        if cfg['freq_min'] <= qtd <= cfg['freq_max']:
                            ciclos.append(cfg['atraso_medio'])
                            break
        
        if paridades:
            resultado['score_paridade'] = sum(paridades) / len(paridades)
        
        if ciclos:
            resultado['ciclo_esperado'] = sum(ciclos) / len(ciclos)
        
        return resultado

    def carregar_arquivo(self, caminho: str) -> bool:
        """Carrega combinações de um arquivo TXT"""
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            self.combinacoes = []
            for linha in linhas:
                linha = linha.strip()
                if linha:
                    # Detectar separador
                    if ' - ' in linha:
                        # Formato: 01 - 02 - 03 - ...
                        nums = [int(n.strip()) for n in linha.split(' - ')]
                    elif ',' in linha:
                        nums = [int(n.strip()) for n in linha.split(',')]
                    elif ';' in linha:
                        nums = [int(n.strip()) for n in linha.split(';')]
                    else:
                        # Separado por espaço simples
                        nums = [int(n.strip()) for n in linha.split() if n.strip().isdigit()]
                    
                    if len(nums) == 15:
                        self.combinacoes.append(sorted(nums))
            
            print(f"\n✅ Arquivo carregado: {caminho}")
            print(f"   📊 Total de combinações: {len(self.combinacoes):,}")
            
            return len(self.combinacoes) > 0
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {caminho}")
            return False
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
            return False
    
    # ==================== MÉTODOS DE CÁLCULO ====================
    
    def _calcular_soma(self, combinacao: List[int]) -> int:
        return sum(combinacao)
    
    def _contar_pares(self, combinacao: List[int]) -> int:
        return sum(1 for n in combinacao if n % 2 == 0)
    
    def _contar_primos(self, combinacao: List[int]) -> int:
        return sum(1 for n in combinacao if n in self.PRIMOS)
    
    def _contar_fibonacci(self, combinacao: List[int]) -> int:
        return sum(1 for n in combinacao if n in self.FIBONACCI)
    
    def _contar_sequencias(self, combinacao: List[int]) -> int:
        if not combinacao:
            return 0
        max_seq = 1
        seq_atual = 1
        nums_ordenados = sorted(combinacao)
        for i in range(1, len(nums_ordenados)):
            if nums_ordenados[i] == nums_ordenados[i-1] + 1:
                seq_atual += 1
                max_seq = max(max_seq, seq_atual)
            else:
                seq_atual = 1
        return max_seq
    
    def _calcular_faixas(self, combinacao: List[int]) -> Dict[str, int]:
        return {
            'f01_05': sum(1 for n in combinacao if 1 <= n <= 5),
            'f06_10': sum(1 for n in combinacao if 6 <= n <= 10),
            'f11_15': sum(1 for n in combinacao if 11 <= n <= 15),
            'f16_20': sum(1 for n in combinacao if 16 <= n <= 20),
            'f21_25': sum(1 for n in combinacao if 21 <= n <= 25),
        }
    
    def _calcular_linhas(self, combinacao: List[int]) -> Dict[int, int]:
        linhas = {}
        comb_set = set(combinacao)
        for num_linha, nums in self.LINHAS.items():
            linhas[num_linha] = len(comb_set & set(nums))
        return linhas
    
    def _calcular_colunas(self, combinacao: List[int]) -> Dict[int, int]:
        colunas = {}
        comb_set = set(combinacao)
        for num_coluna, nums in self.COLUNAS.items():
            colunas[num_coluna] = len(comb_set & set(nums))
        return colunas
    
    def _contar_quentes(self, combinacao: List[int]) -> int:
        return sum(1 for n in combinacao if n in self.numeros_quentes)
    
    def _contar_frios(self, combinacao: List[int]) -> int:
        return sum(1 for n in combinacao if n in self.numeros_frios)
    
    def _repeticoes_ultimo(self, combinacao: List[int]) -> int:
        if not self.ultimo_resultado:
            return 0
        return len(set(combinacao) & set(self.ultimo_resultado))
    
    def _repeticoes_mesma_posicao(self, combinacao: List[int]) -> int:
        """
        Calcula quantos números repetem NA MESMA POSIÇÃO do último resultado.
        Ex: Se N3 do último sorteio = 5 e N3 desta combinação = 5, conta como 1.
        Estatística: 84.6% dos sorteios têm 0-5 repetidos na mesma posição.
        """
        if not self.ultimo_resultado:
            return 0
        comb_sorted = sorted(combinacao)
        count = 0
        for i in range(15):
            if comb_sorted[i] == self.ultimo_resultado[i]:
                count += 1
        return count
    
    def _calcular_acertos(self, combinacao: List[int], resultado: List[int]) -> int:
        return len(set(combinacao) & set(resultado))
    
    def _analisar_trios(self, combinacao: List[int]) -> Dict:
        """
        Analisa os trios de uma combinação.
        Uma combinação de 15 números tem C(15,3) = 455 trios.
        """
        from itertools import combinations
        
        trios_comb = list(combinations(sorted(combinacao), 3))
        
        trios_quentes_count = 0
        trios_frios_count = 0
        trios_atrasados_count = 0
        soma_frequencia = 0
        
        for trio in trios_comb:
            if trio in self.trios_quentes:
                trios_quentes_count += 1
            if trio in self.trios_frios:
                trios_frios_count += 1
            if trio in self.trios_atrasados:
                trios_atrasados_count += 1
            
            # Somar frequência do trio
            if trio in self.trios_dados:
                soma_frequencia += self.trios_dados[trio]['qtd']
        
        media_frequencia = soma_frequencia / len(trios_comb) if trios_comb else 0
        
        return {
            'total_trios': len(trios_comb),
            'quentes': trios_quentes_count,
            'frios': trios_frios_count,
            'atrasados': trios_atrasados_count,
            'media_frequencia': media_frequencia
        }
    
    def _analisar_quintetos(self, combinacao: List[int]) -> Dict:
        """
        Analisa os quintetos de uma combinação.
        Uma combinação de 15 números tem C(15,5) = 3.003 quintetos.
        """
        from itertools import combinations
        
        quintetos_comb = list(combinations(sorted(combinacao), 5))
        
        quintetos_quentes_count = 0
        quintetos_frios_count = 0
        soma_frequencia = 0
        
        for quinteto in quintetos_comb:
            if quinteto in self.quintetos_quentes:
                quintetos_quentes_count += 1
            if quinteto in self.quintetos_frios:
                quintetos_frios_count += 1
            
            if quinteto in self.quintetos_dados:
                soma_frequencia += self.quintetos_dados[quinteto]['qtd']
        
        media_frequencia = soma_frequencia / len(quintetos_comb) if quintetos_comb else 0
        
        return {
            'total_quintetos': len(quintetos_comb),
            'quentes': quintetos_quentes_count,
            'frios': quintetos_frios_count,
            'media_frequencia': media_frequencia
        }
    
    def _validar_historico(self, combinacao: List[int], ultimos_n: int = 50) -> Dict:
        """Valida combinação contra histórico real"""
        if not self.historico_resultados:
            return {'media': 0, 'min': 0, 'max': 0, 'distribuicao': {}}
        
        resultados_usar = self.historico_resultados[:ultimos_n]
        acertos_lista = []
        
        for resultado in resultados_usar:
            acertos = self._calcular_acertos(combinacao, resultado['numeros'])
            acertos_lista.append(acertos)
        
        distribuicao = Counter(acertos_lista)
        
        return {
            'media': sum(acertos_lista) / len(acertos_lista) if acertos_lista else 0,
            'min': min(acertos_lista) if acertos_lista else 0,
            'max': max(acertos_lista) if acertos_lista else 0,
            'acertos_11_mais': sum(1 for a in acertos_lista if a >= 11),
            'acertos_12_mais': sum(1 for a in acertos_lista if a >= 12),
            'acertos_13_mais': sum(1 for a in acertos_lista if a >= 13),
            'distribuicao': dict(distribuicao)
        }
    
    # ==================== AVALIAÇÃO COMPLETA ====================
    
    def _avaliar_combinacao(self, combinacao: List[int], validar_hist: bool = True) -> Dict:
        """Avalia uma combinação em TODOS os critérios v3.0 + TRIOS + INSIGHTS AVANÇADOS"""
        filtros = self.filtros
        
        soma = self._calcular_soma(combinacao)
        pares = self._contar_pares(combinacao)
        impares = 15 - pares
        primos = self._contar_primos(combinacao)
        fibonacci = self._contar_fibonacci(combinacao)
        sequencias = self._contar_sequencias(combinacao)
        faixas = self._calcular_faixas(combinacao)
        linhas = self._calcular_linhas(combinacao)
        colunas = self._calcular_colunas(combinacao)
        quentes = self._contar_quentes(combinacao)
        frios = self._contar_frios(combinacao)
        rep_ultimo = self._repeticoes_ultimo(combinacao)
        rep_mesma_posicao = self._repeticoes_mesma_posicao(combinacao)  # NOVO: mesma posição
        
        # Análise de trios
        trios_info = None
        if self.trios_dados:
            trios_info = self._analisar_trios(combinacao)
        
        # NOVO: Análise de quintetos
        quintetos_info = None
        if self.quintetos_dados:
            quintetos_info = self._analisar_quintetos(combinacao)
        
        # NOVO v3.0: Análise de insights avançados
        insights_info = None
        if self.trios_dados:
            insights_info = self._analisar_insights_combinacao(combinacao)
        
        validacao_hist = None
        if validar_hist and self.historico_resultados:
            validacao_hist = self._validar_historico(combinacao, 50)
        
        # Verificar filtros
        passou_soma = filtros['soma_min'] <= soma <= filtros['soma_max']
        passou_pares = filtros['pares_min'] <= pares <= filtros['pares_max']
        passou_primos = filtros['primos_min'] <= primos <= filtros['primos_max']
        passou_fibonacci = filtros['fibonacci_min'] <= fibonacci <= filtros['fibonacci_max']
        passou_sequencias = sequencias <= filtros['sequencias_max']
        passou_faixas = all(filtros['faixa_min'] <= v <= filtros['faixa_max'] for v in faixas.values())
        passou_linhas = all(filtros['linha_min'] <= v <= filtros['linha_max'] for v in linhas.values())
        passou_colunas = all(filtros['coluna_min'] <= v <= filtros['coluna_max'] for v in colunas.values())
        passou_quentes = quentes >= filtros['quentes_min']
        passou_frios = frios <= filtros['frios_max']
        passou_repeticoes = filtros['repeticoes_min'] <= rep_ultimo <= filtros['repeticoes_max']
        passou_rep_mesma_posicao = filtros['repeticoes_mesma_posicao_min'] <= rep_mesma_posicao <= filtros['repeticoes_mesma_posicao_max']  # NOVO
        
        # Filtros de trios
        passou_trios_quentes = True
        passou_trios_frios = True
        passou_trios_atrasados = True
        if trios_info:
            passou_trios_quentes = trios_info['quentes'] >= filtros.get('trios_quentes_min', 0)
            passou_trios_frios = trios_info['frios'] <= filtros.get('trios_frios_max', 999)
            passou_trios_atrasados = trios_info['atrasados'] >= filtros.get('trios_atrasados_min', 0)
        
        # NOVO: Filtros de quintetos
        passou_quintetos_quentes = True
        passou_quintetos_frios = True
        if quintetos_info:
            passou_quintetos_quentes = quintetos_info['quentes'] >= filtros.get('quintetos_quentes_min', 0)
            passou_quintetos_frios = quintetos_info['frios'] <= filtros.get('quintetos_frios_max', 999)
        
        # NOVO v3.0: Filtros de insights avançados
        passou_divida = True
        passou_pivo = True
        passou_momentum = True
        passou_paridade = True
        if insights_info:
            passou_divida = insights_info['trios_divida'] >= filtros.get('divida_trios_min', 0)
            passou_pivo = insights_info['numeros_pivo'] >= filtros.get('numeros_pivo_min', 0)
            passou_momentum = insights_info['trios_momentum'] >= filtros.get('momentum_min', 0)
            passou_paridade = insights_info['score_paridade'] >= filtros.get('paridade_trios_score_min', 0)
        
        passou_historico = True
        if validacao_hist:
            passou_historico = validacao_hist['media'] >= filtros['media_acertos_min']
        
        # Score ponderado
        pesos = self.PESOS
        score = 0
        if passou_soma: score += pesos['soma']
        if passou_pares: score += pesos['pares']
        if passou_primos: score += pesos['primos']
        if passou_fibonacci: score += pesos['fibonacci']
        if passou_sequencias: score += pesos['sequencias']
        if passou_faixas: score += pesos['faixas']
        if passou_linhas and passou_colunas: score += pesos['linhas_colunas']
        if passou_quentes: score += pesos['quentes']
        if passou_frios: score += pesos['frios']
        if passou_repeticoes: score += pesos['repeticoes']
        if passou_rep_mesma_posicao: score += pesos['repeticoes_mesma_posicao']  # NOVO
        if passou_historico and validacao_hist:
            bonus_hist = min(pesos['validacao_hist'], int((validacao_hist['media'] - 10) * 10))
            score += max(0, bonus_hist)
        
        # Score de trios
        if trios_info and passou_trios_quentes and passou_trios_frios:
            score += pesos['trios']
            # Bonus extra por trios atrasados (chance de sair)
            if trios_info['atrasados'] >= 5:
                score += 10
        
        # Score de quintetos
        if quintetos_info and passou_quintetos_quentes and passou_quintetos_frios:
            score += pesos['quintetos']
            # Bonus por alta frequência média
            if quintetos_info['media_frequencia'] >= 220:
                score += 15
        
        # NOVO v3.0: Score de insights avançados
        if insights_info:
            # Bonus por trios com dívida (candidatos a aparecer)
            if passou_divida and insights_info['trios_divida'] >= 3:
                score += pesos['divida_trios']
                # Bonus extra proporcional à dívida
                score += min(10, int(insights_info['indice_divida_total']))
            
            # Bonus por números pivô (conectores fortes)
            if passou_pivo and insights_info['numeros_pivo'] >= 5:
                score += pesos['numeros_pivo']
                # Bonus extra por muitos pivôs
                if insights_info['numeros_pivo'] >= 7:
                    score += 10
            
            # Bonus por trios com momentum
            if passou_momentum and insights_info['trios_momentum'] >= 2:
                score += pesos['momentum']
            
            # Bonus por boa paridade nos trios
            if passou_paridade:
                score += pesos['paridade_trios']
                # Bonus proporcional ao score de paridade
                score += int((insights_info['score_paridade'] - 0.85) * 50)
        
        passou_todos = all([
            passou_soma, passou_pares, passou_primos, passou_fibonacci,
            passou_sequencias, passou_faixas, passou_linhas, passou_colunas,
            passou_quentes, passou_frios, passou_repeticoes, passou_rep_mesma_posicao,  # ATUALIZADO
            passou_historico, passou_trios_quentes, passou_trios_frios,
            passou_quintetos_quentes, passou_quintetos_frios,
            passou_divida, passou_pivo, passou_momentum, passou_paridade  # NOVO v3.0
        ])
        
        return {
            'combinacao': combinacao,
            'soma': soma, 'pares': pares, 'impares': impares,
            'primos': primos, 'fibonacci': fibonacci, 'sequencias': sequencias,
            'faixas': faixas, 'linhas': linhas, 'colunas': colunas,
            'quentes': quentes, 'frios': frios, 'rep_ultimo': rep_ultimo,
            'rep_mesma_posicao': rep_mesma_posicao,  # NOVO: repetidos na mesma posição
            'trios_info': trios_info,
            'quintetos_info': quintetos_info,
            'insights_info': insights_info,  # NOVO v3.0
            'validacao_hist': validacao_hist,
            'passou_soma': passou_soma, 'passou_pares': passou_pares,
            'passou_primos': passou_primos, 'passou_fibonacci': passou_fibonacci,
            'passou_sequencias': passou_sequencias, 'passou_faixas': passou_faixas,
            'passou_linhas': passou_linhas, 'passou_colunas': passou_colunas,
            'passou_quentes': passou_quentes, 'passou_frios': passou_frios,
            'passou_repeticoes': passou_repeticoes, 'passou_rep_mesma_posicao': passou_rep_mesma_posicao,
            'passou_historico': passou_historico,
            'passou_trios_quentes': passou_trios_quentes,
            'passou_trios_frios': passou_trios_frios,
            'passou_trios_atrasados': passou_trios_atrasados,
            'passou_quintetos_quentes': passou_quintetos_quentes,
            'passou_quintetos_frios': passou_quintetos_frios,
            # NOVO v3.0: Insights avançados
            'passou_divida': passou_divida,
            'passou_pivo': passou_pivo,
            'passou_momentum': passou_momentum,
            'passou_paridade': passou_paridade,
            'passou_todos': passou_todos, 'score': score
        }
    
    def analisar_todas(self, validar_hist: bool = True) -> List[Dict]:
        """Analisa todas as combinações carregadas"""
        if not self.combinacoes:
            print("❌ Nenhuma combinação carregada!")
            return []
        
        print(f"\n🔍 ANALISANDO {len(self.combinacoes):,} COMBINAÇÕES (v3.0 + INSIGHTS)...")
        print("=" * 70)
        
        avaliacoes = []
        stats = {
            'total': len(self.combinacoes),
            'passou_soma': 0, 'passou_pares': 0, 'passou_primos': 0,
            'passou_fibonacci': 0, 'passou_sequencias': 0, 'passou_faixas': 0,
            'passou_linhas': 0, 'passou_colunas': 0, 'passou_quentes': 0,
            'passou_frios': 0, 'passou_repeticoes': 0, 'passou_rep_mesma_posicao': 0,  # NOVO
            'passou_historico': 0,
            'passou_trios_quentes': 0, 'passou_trios_frios': 0,
            'passou_quintetos_quentes': 0, 'passou_quintetos_frios': 0,
            # NOVO v3.0: Insights avançados
            'passou_divida': 0, 'passou_pivo': 0, 'passou_momentum': 0, 'passou_paridade': 0,
            'passou_todos': 0
        }
        
        for i, comb in enumerate(self.combinacoes):
            if i > 0 and i % 5000 == 0:
                print(f"   Processando... {i:,}/{stats['total']:,} ({i/stats['total']*100:.1f}%)")
            
            avaliacao = self._avaliar_combinacao(comb, validar_hist)
            avaliacoes.append(avaliacao)
            
            for key in stats:
                if key.startswith('passou_') and key in avaliacao:
                    if avaliacao[key]:
                        stats[key] += 1
        
        self.estatisticas = stats
        avaliacoes.sort(key=lambda x: x['score'], reverse=True)
        self._mostrar_estatisticas()
        
        return avaliacoes
    
    def _mostrar_estatisticas(self):
        """Mostra estatísticas detalhadas da análise v3.0 + INSIGHTS AVANÇADOS"""
        stats = self.estatisticas
        total = stats['total']
        f = self.filtros
        
        print("\n📊 RESULTADO DA ANÁLISE v3.0 + INSIGHTS AVANÇADOS:")
        print("-" * 70)
        print(f"   📐 FILTROS BÁSICOS:")
        print(f"   • Soma ({f['soma_min']}-{f['soma_max']})............ {stats['passou_soma']:,} ({stats['passou_soma']/total*100:.1f}%)")
        print(f"   • Pares ({f['pares_min']}-{f['pares_max']})............. {stats['passou_pares']:,} ({stats['passou_pares']/total*100:.1f}%)")
        print(f"   • Primos ({f['primos_min']}-{f['primos_max']})............ {stats['passou_primos']:,} ({stats['passou_primos']/total*100:.1f}%)")
        print(f"   • Fibonacci ({f['fibonacci_min']}-{f['fibonacci_max']})......... {stats['passou_fibonacci']:,} ({stats['passou_fibonacci']/total*100:.1f}%)")
        print(f"   • Sequências (≤{f['sequencias_max']})........ {stats['passou_sequencias']:,} ({stats['passou_sequencias']/total*100:.1f}%)")
        print(f"   • Faixas ({f['faixa_min']}-{f['faixa_max']})........... {stats['passou_faixas']:,} ({stats['passou_faixas']/total*100:.1f}%)")
        print(f"   • Linhas ({f['linha_min']}-{f['linha_max']})........... {stats['passou_linhas']:,} ({stats['passou_linhas']/total*100:.1f}%)")
        print(f"   • Colunas ({f['coluna_min']}-{f['coluna_max']}).......... {stats['passou_colunas']:,} ({stats['passou_colunas']/total*100:.1f}%)")
        print(f"   • Quentes (≥{f['quentes_min']}).......... {stats['passou_quentes']:,} ({stats['passou_quentes']/total*100:.1f}%)")
        print(f"   • Frios (≤{f['frios_max']})............. {stats['passou_frios']:,} ({stats['passou_frios']/total*100:.1f}%)")
        print(f"   • Repetições ({f['repeticoes_min']}-{f['repeticoes_max']})...... {stats['passou_repeticoes']:,} ({stats['passou_repeticoes']/total*100:.1f}%)")
        print(f"   • Mesma Posição ({f['repeticoes_mesma_posicao_min']}-{f['repeticoes_mesma_posicao_max']}).... {stats.get('passou_rep_mesma_posicao', 0):,} ({stats.get('passou_rep_mesma_posicao', 0)/total*100:.1f}%)  ⭐ NOVO")
        print(f"   • Histórico (≥{f['media_acertos_min']})...... {stats['passou_historico']:,} ({stats['passou_historico']/total*100:.1f}%)")
        print()
        print(f"   🎲 FILTROS DE TRIOS/QUINTETOS:")
        print(f"   • Trios Quentes (≥{f.get('trios_quentes_min', 20)})... {stats.get('passou_trios_quentes', 0):,} ({stats.get('passou_trios_quentes', 0)/total*100:.1f}%)")
        print(f"   • Trios Frios (≤{f.get('trios_frios_max', 10)})...... {stats.get('passou_trios_frios', 0):,} ({stats.get('passou_trios_frios', 0)/total*100:.1f}%)")
        print(f"   • Quintetos Quentes (≥{f.get('quintetos_quentes_min', 5)}) {stats.get('passou_quintetos_quentes', 0):,} ({stats.get('passou_quintetos_quentes', 0)/total*100:.1f}%)")
        print(f"   • Quintetos Frios (≤{f.get('quintetos_frios_max', 50)})... {stats.get('passou_quintetos_frios', 0):,} ({stats.get('passou_quintetos_frios', 0)/total*100:.1f}%)")
        print()
        print(f"   🧠 INSIGHTS AVANÇADOS v3.0:")
        print(f"   • Trios c/ Dívida (≥{f.get('divida_trios_min', 3)}).. {stats.get('passou_divida', 0):,} ({stats.get('passou_divida', 0)/total*100:.1f}%)")
        print(f"   • Números Pivô (≥{f.get('numeros_pivo_min', 5)}).... {stats.get('passou_pivo', 0):,} ({stats.get('passou_pivo', 0)/total*100:.1f}%)")
        print(f"   • Trios c/ Momentum (≥{f.get('momentum_min', 2)}) {stats.get('passou_momentum', 0):,} ({stats.get('passou_momentum', 0)/total*100:.1f}%)")
        print(f"   • Score Paridade (≥{f.get('paridade_trios_score_min', 0.85)}) {stats.get('passou_paridade', 0):,} ({stats.get('passou_paridade', 0)/total*100:.1f}%)")
        print("-" * 70)
        print(f"   ⭐ PASSOU EM TODOS: {stats['passou_todos']:,} ({stats['passou_todos']/total*100:.2f}%)")
        print("-" * 70)
    
    def filtrar_melhores(self, avaliacoes: List[Dict] = None, top_n: int = None) -> List[Dict]:
        """Filtra apenas as combinações que passaram em todos os critérios"""
        if avaliacoes is None:
            avaliacoes = self.analisar_todas()
        
        melhores = [a for a in avaliacoes if a['passou_todos']]
        
        if top_n and len(melhores) > top_n:
            melhores = melhores[:top_n]
        
        return melhores
    
    def aplicar_diversidade(self, melhores: List[Dict], max_sobreposicao: int = 11,
                            quantidade_final: int = None, modo_exato: bool = False) -> List[Dict]:
        """
        Filtra para manter diversidade entre combinações - VERSÃO OTIMIZADA
        
        Args:
            melhores: Lista de combinações avaliadas
            max_sobreposicao: Quantidade de números em comum
            quantidade_final: Limite de combinações a retornar
            modo_exato: Se True, aceita apenas combinações com EXATAMENTE X números em comum
                        Se False (padrão), aceita combinações com ATÉ X números em comum
        """
        if not melhores:
            return []
        
        if modo_exato:
            print(f"\n🎯 APLICANDO DIVERSIDADE (EXATAMENTE {max_sobreposicao} números iguais)...")
        else:
            print(f"\n🎯 APLICANDO DIVERSIDADE (ATÉ {max_sobreposicao} números iguais)...")
        print(f"   📊 Total a processar: {len(melhores):,} combinações")
        
        from datetime import datetime
        inicio = datetime.now()
        
        diversas = [melhores[0]]
        total = len(melhores)
        
        # Pré-converter para sets para evitar conversões repetidas
        sets_diversas = [set(melhores[0]['combinacao'])]
        
        # Mostrar progresso a cada X combinações
        intervalo_progresso = max(1, total // 20)  # 5% de progresso
        ultimo_progresso = 0
        
        for i, avaliacao in enumerate(melhores[1:], 1):
            # Mostrar progresso
            if i - ultimo_progresso >= intervalo_progresso:
                pct = (i / total) * 100
                tempo_decorrido = (datetime.now() - inicio).total_seconds()
                velocidade = i / tempo_decorrido if tempo_decorrido > 0 else 0
                restante = (total - i) / velocidade if velocidade > 0 else 0
                print(f"   ⏳ {pct:.0f}% ({i:,}/{total:,}) | Selecionadas: {len(diversas):,} | "
                      f"Tempo: {tempo_decorrido:.0f}s | Restante: ~{restante:.0f}s", end='\r')
                ultimo_progresso = i
            
            comb_set = set(avaliacao['combinacao'])
            eh_diversa = True
            
            # Otimização: verificar do fim para o início (mais provável encontrar similar recente)
            for sel_set in reversed(sets_diversas):
                sobreposicao = len(comb_set & sel_set)
                
                if modo_exato:
                    # MODO EXATO: aceita apenas se tiver EXATAMENTE X números em comum
                    if sobreposicao != max_sobreposicao:
                        eh_diversa = False
                        break
                else:
                    # MODO ATÉ: rejeita se tiver MAIS de X números em comum
                    if sobreposicao > max_sobreposicao:
                        eh_diversa = False
                        break
            
            if eh_diversa:
                diversas.append(avaliacao)
                sets_diversas.append(comb_set)
                if quantidade_final and len(diversas) >= quantidade_final:
                    break
        
        tempo_total = (datetime.now() - inicio).total_seconds()
        print(f"\n   ✅ Selecionadas {len(diversas):,} combinações diversas")
        print(f"   📉 Redução por diversidade: {(1 - len(diversas)/len(melhores))*100:.1f}%")
        print(f"   ⏱️ Tempo: {tempo_total:.1f} segundos")
        
        return diversas
    
    def aplicar_redutor_inteligente(self, combinacoes: List[Dict], 
                                     filtros_redutor: Dict = None) -> List[Dict]:
        """
        🎯 REDUTOR INTELIGENTE - Aplica filtros estatísticos avançados
        
        Filtra combinações baseado em critérios estatísticos derivados do histórico:
        - Primos, Fibonacci, Ímpares
        - Quintis (distribuição por faixas de 5)
        - Sequências, Múltiplos de 3, Distância dos extremos
        - Repetidos com último resultado
        
        Args:
            combinacoes: Lista de combinações (com ou sem avaliação prévia)
            filtros_redutor: Dicionário com os ranges de cada filtro
        """
        # Filtros padrão baseados em análise histórica
        if filtros_redutor is None:
            filtros_redutor = {
                'QtdePrimos': [2, 3, 4, 5, 6, 7, 8],
                'QtdeFibonacci': [2, 3, 4, 5, 6],
                'QtdeImpares': [6, 7, 8, 9, 10],
                'QtdeRepetidos': [6, 7, 8, 9, 10],
                'Quintil1': [1, 2, 3, 4, 5],
                'Quintil2': [1, 2, 3, 4, 5],
                'Quintil3': [1, 2, 3, 4, 5],
                'Quintil4': [0, 1, 2, 3, 4, 5],
                'Quintil5': [1, 2, 3, 4, 5],
                'SEQ': [6, 7, 8, 9, 10, 11, 12, 13, 14],
                'QtdeMultiplos3': [3, 4, 5, 6],
                'DistanciaExtremos': [19, 20, 21, 22, 23, 24],
            }
        
        print("\n" + "=" * 70)
        print("🎯 REDUTOR INTELIGENTE - FILTROS ESTATÍSTICOS")
        print("=" * 70)
        print(f"   📊 Combinações de entrada: {len(combinacoes):,}")
        print()
        print("   📋 FILTROS CONFIGURADOS:")
        for campo, valores in filtros_redutor.items():
            print(f"      • {campo}: {valores}")
        print()
        
        # Buscar último resultado para calcular repetidos
        ultimo_resultado = None
        if HAS_PYODBC:
            try:
                conn = pyodbc.connect(self.CONN_STR)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TOP 1 N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                    FROM Resultados_INT ORDER BY Concurso DESC
                """)
                row = cursor.fetchone()
                if row:
                    ultimo_resultado = [int(row[i]) for i in range(15)]
                    print(f"   📍 Último resultado: {'-'.join(f'{n:02d}' for n in ultimo_resultado)}")
                conn.close()
            except Exception as e:
                print(f"   ⚠️ Não foi possível carregar último resultado: {e}")
        
        # Constantes para cálculo
        PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
        FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
        MULTIPLOS_3 = {3, 6, 9, 12, 15, 18, 21, 24}
        QUINTIL_1 = set(range(1, 6))
        QUINTIL_2 = set(range(6, 11))
        QUINTIL_3 = set(range(11, 16))
        QUINTIL_4 = set(range(16, 21))
        QUINTIL_5 = set(range(21, 26))
        
        # Contadores para estatísticas
        stats = {campo: 0 for campo in filtros_redutor}
        
        from datetime import datetime
        inicio = datetime.now()
        
        resultado = []
        total = len(combinacoes)
        
        for i, comb in enumerate(combinacoes):
            # Progresso
            if (i + 1) % max(1, total // 10) == 0:
                pct = ((i + 1) / total) * 100
                print(f"   ⏳ {pct:.0f}% processado... Aprovadas: {len(resultado):,}", end='\r')
            
            # Extrair números
            if isinstance(comb, dict):
                numeros = comb.get('combinacao', comb.get('numeros', []))
            else:
                numeros = list(comb)
            
            if len(numeros) != 15:
                continue
            
            numeros = sorted(numeros)
            nums_set = set(numeros)
            
            # Calcular métricas
            metricas = {}
            metricas['QtdePrimos'] = len(nums_set & PRIMOS)
            metricas['QtdeFibonacci'] = len(nums_set & FIBONACCI)
            metricas['QtdeImpares'] = sum(1 for n in numeros if n % 2 == 1)
            metricas['Quintil1'] = len(nums_set & QUINTIL_1)
            metricas['Quintil2'] = len(nums_set & QUINTIL_2)
            metricas['Quintil3'] = len(nums_set & QUINTIL_3)
            metricas['Quintil4'] = len(nums_set & QUINTIL_4)
            metricas['Quintil5'] = len(nums_set & QUINTIL_5)
            metricas['QtdeMultiplos3'] = len(nums_set & MULTIPLOS_3)
            metricas['DistanciaExtremos'] = numeros[-1] - numeros[0]
            
            # Maior sequência consecutiva
            seq_max = 1
            seq_atual = 1
            for j in range(1, len(numeros)):
                if numeros[j] == numeros[j-1] + 1:
                    seq_atual += 1
                    seq_max = max(seq_max, seq_atual)
                else:
                    seq_atual = 1
            metricas['SEQ'] = seq_max
            
            # Repetidos com último resultado
            if ultimo_resultado:
                metricas['QtdeRepetidos'] = len(nums_set & set(ultimo_resultado))
            else:
                metricas['QtdeRepetidos'] = 7  # Valor neutro se não tiver último resultado
            
            # Verificar todos os filtros
            passou = True
            for campo, valores_validos in filtros_redutor.items():
                if campo in metricas:
                    if metricas[campo] not in valores_validos:
                        passou = False
                    else:
                        stats[campo] += 1
            
            if passou:
                if isinstance(comb, dict):
                    resultado.append(comb)
                else:
                    resultado.append({'combinacao': numeros, 'metricas': metricas})
        
        tempo_total = (datetime.now() - inicio).total_seconds()
        
        print("\n")
        print("=" * 70)
        print("📊 RESULTADO DO REDUTOR INTELIGENTE")
        print("=" * 70)
        print(f"   📥 Entrada: {total:,} combinações")
        print(f"   ✅ Aprovadas: {len(resultado):,} combinações")
        print(f"   📉 Redução: {(1 - len(resultado)/total)*100:.2f}%")
        print(f"   ⏱️ Tempo: {tempo_total:.1f} segundos")
        print()
        print("   📋 ESTATÍSTICAS POR FILTRO (passaram):")
        for campo, qtd in stats.items():
            print(f"      • {campo}: {qtd:,} ({qtd/total*100:.1f}%)")
        print("=" * 70)
        
        return resultado
    
    def menu_redutor_inteligente(self, combinacoes: List[Dict]) -> List[Dict]:
        """
        Menu interativo para configurar o redutor inteligente.
        """
        print("\n" + "=" * 70)
        print("🎯 REDUTOR INTELIGENTE - CONFIGURAÇÃO")
        print("=" * 70)
        print()
        print("   1. Usar filtros PADRÃO (baseados em análise histórica)")
        print("   2. Configurar filtros PERSONALIZADOS")
        print("   3. Voltar (não aplicar redutor)")
        print()
        
        opcao = input("   Escolha (1-3) [1]: ").strip() or "1"
        
        if opcao == "3":
            return combinacoes
        
        filtros_redutor = None
        
        if opcao == "2":
            print("\n   📝 CONFIGURE OS FILTROS (Enter = usar padrão):")
            print("   Formato: números separados por vírgula (ex: 2,3,4,5)")
            print()
            
            filtros_redutor = {}
            
            campos_config = [
                ('QtdePrimos', [2, 3, 4, 5, 6, 7, 8]),
                ('QtdeFibonacci', [2, 3, 4, 5, 6]),
                ('QtdeImpares', [6, 7, 8, 9, 10]),
                ('QtdeRepetidos', [6, 7, 8, 9, 10]),
                ('Quintil1', [1, 2, 3, 4, 5]),
                ('Quintil2', [1, 2, 3, 4, 5]),
                ('Quintil3', [1, 2, 3, 4, 5]),
                ('Quintil4', [0, 1, 2, 3, 4, 5]),
                ('Quintil5', [1, 2, 3, 4, 5]),
                ('SEQ', [6, 7, 8, 9, 10, 11, 12, 13, 14]),
                ('QtdeMultiplos3', [3, 4, 5, 6]),
                ('DistanciaExtremos', [19, 20, 21, 22, 23, 24]),
            ]
            
            for campo, padrao in campos_config:
                valor = input(f"   {campo} {padrao}: ").strip()
                if valor:
                    try:
                        filtros_redutor[campo] = [int(x.strip()) for x in valor.split(',')]
                    except:
                        print(f"      ⚠️ Formato inválido, usando padrão")
                        filtros_redutor[campo] = padrao
                else:
                    filtros_redutor[campo] = padrao
        
        return self.aplicar_redutor_inteligente(combinacoes, filtros_redutor)

    def benchmark_concurso_especifico(self, combinacoes: List[Dict], 
                                       concurso: int = None, 
                                       numeros: List[int] = None) -> Dict:
        """
        Benchmark contra um concurso específico.
        
        Args:
            combinacoes: Lista de combinações avaliadas
            concurso: Número do concurso (busca na base)
            numeros: Lista de 15 números (se não estiver na base)
        """
        resultado_nums = None
        
        # Tentar buscar na base
        if concurso and not numeros:
            for res in self.historico_resultados:
                if res['concurso'] == concurso:
                    resultado_nums = res['numeros']
                    break
            
            # Se não encontrou, buscar diretamente no banco
            if not resultado_nums and HAS_PYODBC:
                try:
                    conn = pyodbc.connect(self.CONN_STR)
                    cursor = conn.cursor()
                    cursor.execute(f"""
                        SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                        FROM Resultados_INT WHERE Concurso = {concurso}
                    """)
                    row = cursor.fetchone()
                    if row:
                        resultado_nums = [int(row[i]) for i in range(15)]
                    conn.close()
                except:
                    pass
        
        # Se passou números manualmente
        if numeros and len(numeros) == 15:
            resultado_nums = sorted(numeros)
        
        if not resultado_nums:
            print(f"❌ Concurso {concurso} não encontrado na base!")
            print("   💡 Informe os 15 números manualmente")
            return {}
        
        print(f"\n🎯 BENCHMARK CONCURSO {concurso if concurso else 'MANUAL'}")
        print("-" * 70)
        print(f"   📊 Resultado: {' - '.join(f'{n:02d}' for n in sorted(resultado_nums))}")
        print("-" * 70)
        
        resultado_set = set(resultado_nums)
        acertos_lista = []
        melhores_combinacoes = []
        
        for avaliacao in combinacoes:
            comb = set(avaliacao['combinacao'])
            acertos = len(comb & resultado_set)
            acertos_lista.append({
                'combinacao': avaliacao['combinacao'],
                'acertos': acertos,
                'score': avaliacao['score']
            })
        
        # Ordenar por acertos (maior primeiro)
        acertos_lista.sort(key=lambda x: (x['acertos'], x['score']), reverse=True)
        
        # Distribuição
        dist = Counter(a['acertos'] for a in acertos_lista)
        
        # Valores dos prêmios (Lotofácil - valores atualizados)
        # 11=R$7, 12=R$14, 13=R$35, 14=R$1.000, 15=R$1.000.000
        PREMIOS_VALOR = {11: 7.00, 12: 14.00, 13: 35.00, 14: 1000.00, 15: 1000000.00}
        
        # Calcular custo e prêmios
        custo_total = len(combinacoes) * 3.50
        premio_total = 0.0
        premios_detalhes = {}
        
        for ac in [11, 12, 13, 14, 15]:
            qtd = dist.get(ac, 0)
            valor = PREMIOS_VALOR.get(ac, 0)
            premio_ac = qtd * valor
            premio_total += premio_ac
            premios_detalhes[ac] = {'qtd': qtd, 'valor_unit': valor, 'total': premio_ac}
        
        lucro = premio_total - custo_total
        
        print(f"\n   📊 Combinações testadas: {len(combinacoes):,}")
        print(f"\n   📈 DISTRIBUIÇÃO DE ACERTOS:")
        for ac in sorted(dist.keys(), reverse=True):
            barra = "█" * min(dist[ac], 50)
            print(f"      {ac:2} acertos: {dist[ac]:5,} {barra}")
        
        # Mostrar top 5 melhores
        print(f"\n   🏆 TOP 5 MELHORES COMBINAÇÕES:")
        print("   " + "-" * 65)
        for i, item in enumerate(acertos_lista[:5], 1):
            comb_str = " - ".join(f"{n:02d}" for n in item['combinacao'])
            print(f"   {i}. [{item['acertos']:2} acertos] {comb_str}")
        print("   " + "-" * 65)
        
        melhor_acerto = acertos_lista[0]['acertos'] if acertos_lista else 0
        qtd_11_mais = sum(1 for a in acertos_lista if a['acertos'] >= 11)
        qtd_12_mais = sum(1 for a in acertos_lista if a['acertos'] >= 12)
        qtd_13_mais = sum(1 for a in acertos_lista if a['acertos'] >= 13)
        
        print(f"\n   🎯 RESUMO:")
        print(f"      Melhor acerto: {melhor_acerto}")
        print(f"      Com 11+ acertos: {qtd_11_mais}")
        print(f"      Com 12+ acertos: {qtd_12_mais}")
        print(f"      Com 13+ acertos: {qtd_13_mais}")
        
        # Seção Financeira
        print(f"\n   💰 ANÁLISE FINANCEIRA:")
        print(f"      Custo ({len(combinacoes):,} × R$ 3,50): R$ {custo_total:,.2f}")
        print()
        print(f"      Prêmios estimados:")
        for ac in [11, 12, 13, 14, 15]:
            det = premios_detalhes[ac]
            if det['qtd'] > 0:
                print(f"         {ac} acertos: {det['qtd']:3} × R$ {det['valor_unit']:,.2f} = R$ {det['total']:,.2f}")
        print(f"      " + "-" * 45)
        print(f"      Total prêmios: R$ {premio_total:,.2f}")
        print()
        if lucro >= 0:
            print(f"      ✅ LUCRO: R$ {lucro:,.2f}")
        else:
            print(f"      ❌ PREJUÍZO: R$ {abs(lucro):,.2f}")
        
        print("-" * 70)
        
        return {
            'concurso': concurso,
            'resultado': resultado_nums,
            'melhor_acerto': melhor_acerto,
            'distribuicao': dict(dist),
            'qtd_11_mais': qtd_11_mais,
            'qtd_12_mais': qtd_12_mais,
            'qtd_13_mais': qtd_13_mais,
            'top_5': acertos_lista[:5],
            'custo': custo_total,
            'premio_total': premio_total,
            'lucro': lucro,
            'premios_detalhes': premios_detalhes
        }
    
    def benchmark_automatico(self, combinacoes: List[Dict], ultimos_n: int = 100) -> Dict:
        """Executa benchmark contra últimos N concursos reais"""
        if not self.historico_resultados:
            print("❌ Sem histórico para benchmark!")
            return {}
        
        print(f"\n🏆 BENCHMARK AUTOMÁTICO (últimos {ultimos_n} concursos)...")
        print("-" * 70)
        
        resultados = self.historico_resultados[:ultimos_n]
        acertos_dist = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
        melhores_por_concurso = {}
        
        for resultado in resultados:
            concurso = resultado['concurso']
            nums_resultado = set(resultado['numeros'])
            melhor_acerto = 0
            
            for avaliacao in combinacoes:
                comb = set(avaliacao['combinacao'])
                acertos = len(comb & nums_resultado)
                melhor_acerto = max(melhor_acerto, acertos)
                if acertos >= 11:
                    acertos_dist[acertos] = acertos_dist.get(acertos, 0) + 1
            
            melhores_por_concurso[concurso] = melhor_acerto
        
        media_melhor = sum(melhores_por_concurso.values()) / len(melhores_por_concurso)
        concursos_11 = sum(1 for v in melhores_por_concurso.values() if v >= 11)
        concursos_12 = sum(1 for v in melhores_por_concurso.values() if v >= 12)
        concursos_13 = sum(1 for v in melhores_por_concurso.values() if v >= 13)
        
        print(f"   📊 Combinações testadas: {len(combinacoes):,}")
        print(f"   📊 Concursos avaliados: {len(resultados)}")
        print()
        print(f"   🎯 Média melhor acerto/concurso: {media_melhor:.2f}")
        print(f"   🎯 Concursos com 11+: {concursos_11} ({concursos_11/len(resultados)*100:.1f}%)")
        print(f"   🎯 Concursos com 12+: {concursos_12} ({concursos_12/len(resultados)*100:.1f}%)")
        print(f"   🎯 Concursos com 13+: {concursos_13} ({concursos_13/len(resultados)*100:.1f}%)")
        print()
        print(f"   📈 Distribuição de acertos:")
        for ac in [11, 12, 13, 14, 15]:
            print(f"      {ac} acertos: {acertos_dist.get(ac, 0):,}")
        print("-" * 70)
        
        return {
            'media_melhor_acerto': media_melhor,
            'concursos_11_mais': concursos_11,
            'concursos_12_mais': concursos_12,
            'concursos_13_mais': concursos_13,
            'distribuicao_acertos': acertos_dist
        }
    
    def salvar_melhores(self, melhores: List[Dict], sufixo: str = "") -> str:
        """Salva as melhores combinações em arquivo TXT"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if sufixo:
            arquivo = f"melhores_combinacoes_{sufixo}_{timestamp}_{len(melhores)}.txt"
        else:
            arquivo = f"melhores_combinacoes_{timestamp}_{len(melhores)}.txt"
        
        print(f"\n💾 Salvando em: {arquivo}")
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            for avaliacao in melhores:
                comb = avaliacao['combinacao']
                linha = ",".join(f"{n:02d}" for n in comb)
                f.write(linha + "\n")
        
        print(f"✅ Arquivo salvo com sucesso!")
        print(f"   • {len(melhores):,} combinações")
        custo = len(melhores) * 3.50
        print(f"   • 💰 Custo estimado: R$ {custo:,.2f}")
        
        return arquivo
    
    def mostrar_amostra(self, melhores: List[Dict], n: int = 5):
        """Mostra amostra das melhores combinações v2.0"""
        print(f"\n📋 TOP {min(n, len(melhores))} MELHORES COMBINAÇÕES:")
        print("-" * 95)
        print(f"{'#':>4} | {'Combinação':^50} | Score | Soma | P/I | Qnt | Média")
        print("-" * 95)
        
        for i, aval in enumerate(melhores[:n], 1):
            comb = aval['combinacao']
            nums_str = " - ".join(f"{n:02d}" for n in comb)
            p_i = f"{aval['pares']}/{aval['impares']}"
            media = aval['validacao_hist']['media'] if aval.get('validacao_hist') else 0
            print(f"{i:4} | {nums_str} | {aval['score']:5} | {aval['soma']:4} | {p_i:3} | {aval['quentes']:3} | {media:.2f}")
        
        print("-" * 95)
        print("Legenda: P/I = Pares/Ímpares | Qnt = Quentes | Média = Média acertos histórico")

    def benchmark_comparativo(self, ultimos_n: int = 50, numeros_manual: List[int] = None, 
                                modo: str = 'historico') -> Dict:
        """
        BENCHMARK COMPARATIVO - Valida eficácia dos filtros
        
        Modos:
        - 'historico': Usa apenas concursos do histórico
        - 'manual': Usa apenas o concurso manual informado
        - 'ambos': Usa histórico + concurso manual
        
        Args:
            ultimos_n: Quantidade de concursos do histórico para usar
            numeros_manual: Lista de 15 números para usar como concurso manual
            modo: 'historico', 'manual' ou 'ambos'
        
        Returns:
            Dict com análise comparativa detalhada
        """
        if not self.combinacoes:
            print("❌ Nenhuma combinação carregada!")
            return {}
        
        if modo == 'manual' and not numeros_manual:
            print("❌ Modo manual requer números!")
            return {}
        
        if modo == 'historico' and not self.historico_resultados:
            print("❌ Sem histórico para benchmark!")
            return {}
        
        print("\n" + "=" * 80)
        print("🔬 BENCHMARK COMPARATIVO - VALIDAÇÃO DE EFICÁCIA DOS FILTROS")
        print("=" * 80)
        
        # ===== INFORMAÇÕES DO ARQUIVO ORIGINAL =====
        print("\n📁 ARQUIVO ORIGINAL (ANTES DA REDUÇÃO):")
        print(f"   📊 Total de combinações carregadas: {len(self.combinacoes):,}")
        
        # Calcular estatísticas básicas do arquivo original
        if self.combinacoes:
            somas = [sum(c) for c in self.combinacoes]
            print(f"   📈 Soma mínima: {min(somas)} | Soma máxima: {max(somas)} | Média: {sum(somas)/len(somas):.1f}")
            
            # Mostrar amostra de configuração
            pares_dist = [sum(1 for n in c if n % 2 == 0) for c in self.combinacoes]
            print(f"   🔢 Pares: mín {min(pares_dist)} | máx {max(pares_dist)} | média {sum(pares_dist)/len(pares_dist):.1f}")
        
        print("-" * 80)
        
        # Preparar resultados para análise
        resultados_hist = []
        
        if modo in ['historico', 'ambos'] and self.historico_resultados:
            resultados_hist = self.historico_resultados[:ultimos_n]
        
        # Se tem números manuais
        if numeros_manual and modo in ['manual', 'ambos']:
            nums_ordenados = sorted(numeros_manual)
            resultado_manual = {
                'concurso': 0,  # Concurso futuro/manual
                'numeros': nums_ordenados
            }
            if modo == 'manual':
                resultados_hist = [resultado_manual]
            else:  # ambos
                resultados_hist = [resultado_manual] + resultados_hist
            
            print(f"\n⭐ CONCURSO MANUAL: {' - '.join(f'{n:02d}' for n in nums_ordenados)}")
        
        if modo == 'ambos':
            print(f"   Total: {len(resultados_hist)} concursos ({len(resultados_hist)-1} histórico + 1 manual)")
        elif modo == 'historico':
            print(f"\n   Usando {len(resultados_hist)} concursos do histórico")
        else:
            print(f"   Analisando apenas o concurso manual")
        
        # ===== ANÁLISE DETALHADA DO ARQUIVO ORIGINAL (ANTES DA REDUÇÃO) =====
        if numeros_manual and modo in ['manual', 'ambos']:
            print("\n" + "=" * 80)
            print("📁 ARQUIVO ORIGINAL (ANTES DA REDUÇÃO) - ANÁLISE DE ACERTOS")
            print("=" * 80)
            
            nums_resultado = set(sorted(numeros_manual))
            acertos_original = []
            melhor_original = 0
            
            for comb in self.combinacoes:
                acertos = len(set(comb) & nums_resultado)
                acertos_original.append({'combinacao': comb, 'acertos': acertos})
                melhor_original = max(melhor_original, acertos)
            
            dist_original = Counter(d['acertos'] for d in acertos_original)
            
            print(f"\n   📊 Total de combinações no arquivo: {len(self.combinacoes):,}")
            print(f"   🏆 MELHOR ACERTO POSSÍVEL: {melhor_original}")
            print(f"\n   📈 Distribuição de acertos no arquivo original:")
            for ac in sorted([k for k in dist_original.keys() if k >= 8], reverse=True):
                qtd = dist_original[ac]
                pct = qtd / len(self.combinacoes) * 100
                barra = "█" * min(int(pct * 2), 50)
                print(f"      {ac:2} acertos: {qtd:>7,} ({pct:>5.2f}%) {barra}")
            
            # Mostrar TOP 5 melhores do arquivo original
            acertos_original.sort(key=lambda x: x['acertos'], reverse=True)
            print(f"\n   🏆 TOP 5 MELHORES DO ARQUIVO ORIGINAL:")
            for i, item in enumerate(acertos_original[:5], 1):
                comb_str = " - ".join(f"{n:02d}" for n in item['combinacao'])
                print(f"      {i}. [{item['acertos']:2} acertos] {comb_str}")
        
        # ===== FASE 1: ANÁLISE ANTES DOS FILTROS (TODAS) =====
        print(f"\n📊 FASE 1: Analisando TODAS as {len(self.combinacoes):,} combinações do arquivo original...")
        
        antes_stats = self._calcular_stats_benchmark(self.combinacoes, resultados_hist, "original")
        
        # ===== FASE 2: APLICAR FILTROS =====
        print(f"\n🔧 FASE 2: Aplicando filtros...")
        avaliacoes = self.analisar_todas(validar_hist=True)
        
        # ===== ANÁLISE: QUAIS FILTROS ELIMINARAM BOAS COMBINAÇÕES? =====
        if numeros_manual and modo in ['manual', 'ambos']:
            print("\n" + "-" * 80)
            print("🔍 ANÁLISE: QUAIS FILTROS ELIMINARAM COMBINAÇÕES COM BONS ACERTOS?")
            print("-" * 80)
            
            # Para cada avaliação, calcular acertos no concurso manual
            for aval in avaliacoes:
                comb = aval['combinacao']
                aval['acertos_manual'] = len(set(comb) & nums_resultado)
            
            # Identificar boas combinações (11+ acertos) que foram eliminadas
            boas_eliminadas = [a for a in avaliacoes if a['acertos_manual'] >= 11 and not a['passou_todos']]
            boas_mantidas = [a for a in avaliacoes if a['acertos_manual'] >= 11 and a['passou_todos']]
            
            print(f"\n   📊 Combinações com 11+ acertos no concurso manual:")
            print(f"      ✅ MANTIDAS após filtros: {len(boas_mantidas):,}")
            print(f"      ❌ ELIMINADAS pelos filtros: {len(boas_eliminadas):,}")
            
            if boas_eliminadas:
                # Analisar quais filtros eliminaram
                filtros_culpados = Counter()
                for aval in boas_eliminadas:
                    if not aval.get('passou_soma', True): filtros_culpados['soma'] += 1
                    if not aval.get('passou_pares', True): filtros_culpados['pares'] += 1
                    if not aval.get('passou_primos', True): filtros_culpados['primos'] += 1
                    if not aval.get('passou_fibonacci', True): filtros_culpados['fibonacci'] += 1
                    if not aval.get('passou_sequencias', True): filtros_culpados['sequencias'] += 1
                    if not aval.get('passou_faixas', True): filtros_culpados['faixas'] += 1
                    if not aval.get('passou_linhas', True): filtros_culpados['linhas'] += 1
                    if not aval.get('passou_colunas', True): filtros_culpados['colunas'] += 1
                    if not aval.get('passou_quentes', True): filtros_culpados['quentes'] += 1
                    if not aval.get('passou_frios', True): filtros_culpados['frios'] += 1
                    if not aval.get('passou_repeticoes', True): filtros_culpados['repeticoes'] += 1
                    if not aval.get('passou_historico', True): filtros_culpados['historico'] += 1
                    if not aval.get('passou_trios_quentes', True): filtros_culpados['trios_quentes'] += 1
                    if not aval.get('passou_trios_frios', True): filtros_culpados['trios_frios'] += 1
                    if not aval.get('passou_quintetos_quentes', True): filtros_culpados['quintetos_quentes'] += 1
                    if not aval.get('passou_quintetos_frios', True): filtros_culpados['quintetos_frios'] += 1
                    if not aval.get('passou_divida', True): filtros_culpados['divida_trios'] += 1
                    if not aval.get('passou_pivo', True): filtros_culpados['numeros_pivo'] += 1
                    if not aval.get('passou_momentum', True): filtros_culpados['momentum'] += 1
                    if not aval.get('passou_paridade', True): filtros_culpados['paridade_trios'] += 1
                
                print(f"\n   ❌ FILTROS QUE ELIMINARAM BOAS COMBINAÇÕES (11+ acertos):")
                for filtro, qtd in filtros_culpados.most_common():
                    pct = qtd / len(boas_eliminadas) * 100
                    impacto = "🔴 CRÍTICO" if pct > 50 else "🟡 MODERADO" if pct > 20 else "🟢 BAIXO"
                    print(f"      {filtro:<20}: {qtd:>5} eliminadas ({pct:>5.1f}%) {impacto}")
                
                # Mostrar exemplos de boas combinações eliminadas
                print(f"\n   📋 EXEMPLOS DE BOAS COMBINAÇÕES ELIMINADAS:")
                boas_eliminadas.sort(key=lambda x: x['acertos_manual'], reverse=True)
                for i, aval in enumerate(boas_eliminadas[:5], 1):
                    comb_str = " - ".join(f"{n:02d}" for n in aval['combinacao'])
                    falhas = []
                    if not aval.get('passou_soma', True): falhas.append('soma')
                    if not aval.get('passou_pares', True): falhas.append('pares')
                    if not aval.get('passou_primos', True): falhas.append('primos')
                    if not aval.get('passou_fibonacci', True): falhas.append('fibonacci')
                    if not aval.get('passou_sequencias', True): falhas.append('sequencias')
                    if not aval.get('passou_faixas', True): falhas.append('faixas')
                    if not aval.get('passou_linhas', True): falhas.append('linhas')
                    if not aval.get('passou_colunas', True): falhas.append('colunas')
                    if not aval.get('passou_quentes', True): falhas.append('quentes')
                    if not aval.get('passou_frios', True): falhas.append('frios')
                    if not aval.get('passou_repeticoes', True): falhas.append('repeticoes')
                    if not aval.get('passou_historico', True): falhas.append('historico')
                    if not aval.get('passou_trios_quentes', True): falhas.append('trios_quentes')
                    if not aval.get('passou_trios_frios', True): falhas.append('trios_frios')
                    falhas_str = ", ".join(falhas[:4])
                    if len(falhas) > 4:
                        falhas_str += f"... +{len(falhas)-4}"
                    print(f"      {i}. [{aval['acertos_manual']:2} acertos] {comb_str}")
                    print(f"         ❌ Falhou em: {falhas_str}")
        
        # Testar cada filtro individualmente
        filtros_analise = {}
        
        # Lista de todos os filtros para testar
        filtros_para_testar = [
            ('soma', lambda a: a['passou_soma']),
            ('pares', lambda a: a['passou_pares']),
            ('primos', lambda a: a['passou_primos']),
            ('fibonacci', lambda a: a['passou_fibonacci']),
            ('sequencias', lambda a: a['passou_sequencias']),
            ('faixas', lambda a: a['passou_faixas']),
            ('linhas', lambda a: a['passou_linhas']),
            ('colunas', lambda a: a['passou_colunas']),
            ('quentes', lambda a: a['passou_quentes']),
            ('frios', lambda a: a['passou_frios']),
            ('repeticoes', lambda a: a['passou_repeticoes']),
            ('historico', lambda a: a['passou_historico']),
            ('trios_quentes', lambda a: a.get('passou_trios_quentes', True)),
            ('trios_frios', lambda a: a.get('passou_trios_frios', True)),
            ('quintetos_quentes', lambda a: a.get('passou_quintetos_quentes', True)),
            ('quintetos_frios', lambda a: a.get('passou_quintetos_frios', True)),
            # NOVOS v3.0: Insights avançados
            ('divida_trios', lambda a: a.get('passou_divida', True)),
            ('numeros_pivo', lambda a: a.get('passou_pivo', True)),
            ('momentum', lambda a: a.get('passou_momentum', True)),
            ('paridade_trios', lambda a: a.get('passou_paridade', True)),
        ]
        
        for nome_filtro, func_filtro in filtros_para_testar:
            aprovadas = [a for a in avaliacoes if func_filtro(a)]
            reprovadas = [a for a in avaliacoes if not func_filtro(a)]
            
            if len(aprovadas) > 0 and len(reprovadas) > 0:
                # Calcular média de acertos das aprovadas vs reprovadas
                media_aprovadas = self._media_acertos_combinacoes(
                    [a['combinacao'] for a in aprovadas], resultados_hist
                )
                media_reprovadas = self._media_acertos_combinacoes(
                    [a['combinacao'] for a in reprovadas], resultados_hist
                )
                
                diferenca = media_aprovadas - media_reprovadas
                eficaz = diferenca >= 0
                
                filtros_analise[nome_filtro] = {
                    'aprovadas': len(aprovadas),
                    'reprovadas': len(reprovadas),
                    'taxa_aprovacao': len(aprovadas) / len(avaliacoes) * 100,
                    'media_aprovadas': media_aprovadas,
                    'media_reprovadas': media_reprovadas,
                    'diferenca': diferenca,
                    'eficaz': eficaz
                }
        
        # ===== FASE 3: ANÁLISE DEPOIS DOS FILTROS (APROVADAS) =====
        melhores = [a for a in avaliacoes if a['passou_todos']]
        
        print(f"\n📊 FASE 3: Analisando {len(melhores):,} combinações APROVADAS...")
        
        if len(melhores) == 0:
            print("⚠️ Nenhuma combinação passou em todos os filtros!")
            # Usar top 100 por score
            melhores = avaliacoes[:min(100, len(avaliacoes))]
            print(f"   Usando TOP {len(melhores)} por score para comparação.")
        
        depois_stats = self._calcular_stats_benchmark(
            [m['combinacao'] for m in melhores], resultados_hist, "filtradas"
        )
        
        # ===== FASE 4: COMPARAÇÃO =====
        print("\n" + "=" * 80)
        print("📊 COMPARAÇÃO: ANTES vs DEPOIS DOS FILTROS")
        print("=" * 80)
        
        print(f"\n{'Métrica':<30} | {'ANTES':>12} | {'DEPOIS':>12} | {'Diferença':>12}")
        print("-" * 80)
        
        metricas_comparar = [
            ('Combinações', 'total', 'd'),
            ('Média acertos', 'media_acertos', 'f'),
            ('Concursos 11+', 'concursos_11', 'd'),
            ('Concursos 12+', 'concursos_12', 'd'),
            ('Concursos 13+', 'concursos_13', 'd'),
            ('Acertos 11', 'acertos_11', 'd'),
            ('Acertos 12', 'acertos_12', 'd'),
            ('Acertos 13', 'acertos_13', 'd'),
            ('Acertos 14', 'acertos_14', 'd'),
            ('Acertos 15', 'acertos_15', 'd'),
        ]
        
        comparacao = {}
        houve_piora = False
        metricas_piores = []
        
        for nome, chave, tipo in metricas_comparar:
            antes_val = antes_stats.get(chave, 0)
            depois_val = depois_stats.get(chave, 0)
            diff = depois_val - antes_val
            
            if tipo == 'f':
                print(f"{nome:<30} | {antes_val:>12.2f} | {depois_val:>12.2f} | {diff:>+12.2f}")
            else:
                print(f"{nome:<30} | {antes_val:>12,} | {depois_val:>12,} | {diff:>+12,}")
            
            # Para métricas de acerto, normalizar por quantidade
            if chave.startswith('acertos_') or chave.startswith('concursos_'):
                antes_norm = antes_val / antes_stats['total'] if antes_stats['total'] > 0 else 0
                depois_norm = depois_val / depois_stats['total'] if depois_stats['total'] > 0 else 0
                diff_norm = depois_norm - antes_norm
                
                comparacao[chave] = {
                    'antes': antes_val, 'depois': depois_val,
                    'antes_norm': antes_norm, 'depois_norm': depois_norm,
                    'diff': diff, 'diff_norm': diff_norm
                }
                
                if diff_norm < -0.01 and chave in ['media_acertos', 'concursos_11', 'concursos_12']:
                    houve_piora = True
                    metricas_piores.append(nome)
        
        print("-" * 80)
        
        # ===== FASE 5: ANÁLISE DE EFICÁCIA DOS FILTROS =====
        print("\n" + "=" * 80)
        print("🔬 ANÁLISE DE EFICÁCIA POR FILTRO")
        print("=" * 80)
        print(f"\n{'Filtro':<20} | {'Aprov':>7} | {'Taxa':>6} | {'Média Aprov':>10} | {'Média Rep':>10} | {'Δ':>8} | {'Status':>10}")
        print("-" * 90)
        
        filtros_problematicos = []
        
        for nome, dados in sorted(filtros_analise.items(), key=lambda x: x[1]['diferenca']):
            status = "✅ EFICAZ" if dados['eficaz'] else "⚠️ REVISAR"
            
            if not dados['eficaz'] and dados['diferenca'] < -0.1:
                filtros_problematicos.append((nome, dados['diferenca']))
                status = "❌ PROBLEMA"
            
            print(f"{nome:<20} | {dados['aprovadas']:>7,} | {dados['taxa_aprovacao']:>5.1f}% | "
                  f"{dados['media_aprovadas']:>10.2f} | {dados['media_reprovadas']:>10.2f} | "
                  f"{dados['diferenca']:>+7.2f} | {status}")
        
        print("-" * 90)
        
        # ===== RESUMO FINAL =====
        print("\n" + "=" * 80)
        print("📋 RESUMO FINAL")
        print("=" * 80)
        
        if houve_piora:
            print("\n⚠️ ALERTA: Os filtros podem estar piorando os resultados!")
            print(f"   Métricas afetadas: {', '.join(metricas_piores)}")
        else:
            print("\n✅ Os filtros estão MANTENDO ou MELHORANDO a performance!")
        
        if filtros_problematicos:
            print("\n❌ FILTROS PROBLEMÁTICOS (causam piora):")
            for nome, diff in sorted(filtros_problematicos, key=lambda x: x[1]):
                print(f"   • {nome}: média {diff:+.2f} acertos")
            print("\n💡 SUGESTÃO: Considere relaxar ou desativar esses filtros.")
        else:
            print("\n✅ Todos os filtros estão contribuindo positivamente!")
        
        # Taxa de redução
        reducao = (1 - depois_stats['total'] / antes_stats['total']) * 100 if antes_stats['total'] > 0 else 0
        print(f"\n📉 Redução de combinações: {reducao:.1f}% ({antes_stats['total']:,} → {depois_stats['total']:,})")
        
        # ===== ANÁLISE FINANCEIRA DO CONCURSO MANUAL =====
        resultado_financeiro = None
        if numeros_manual and modo in ['manual', 'ambos']:
            print("\n" + "=" * 80)
            print("💰 ANÁLISE FINANCEIRA - CONCURSO MANUAL")
            print("=" * 80)
            
            nums_resultado = set(sorted(numeros_manual))
            # Valores dos prêmios (Lotofácil - valores atualizados)
            # 11=R$7, 12=R$14, 13=R$35, 14=R$1.000, 15=R$1.000.000
            PREMIOS_VALOR = {11: 7.00, 12: 14.00, 13: 35.00, 14: 1000.00, 15: 1000000.00}
            
            # Análise ANTES dos filtros (todas)
            print(f"\n📊 ANTES DOS FILTROS ({len(self.combinacoes):,} combinações):")
            antes_acertos = []
            for comb in self.combinacoes:
                acertos = len(set(comb) & nums_resultado)
                antes_acertos.append(acertos)
            
            antes_dist = Counter(antes_acertos)
            antes_custo = len(self.combinacoes) * 3.50
            antes_premio = sum(antes_dist.get(ac, 0) * PREMIOS_VALOR.get(ac, 0) for ac in [11, 12, 13, 14, 15])
            antes_lucro = antes_premio - antes_custo
            
            print(f"   Custo: R$ {antes_custo:,.2f}")
            print(f"   Distribuição de acertos:")
            for ac in sorted([k for k in antes_dist.keys() if k >= 10], reverse=True):
                qtd = antes_dist[ac]
                premio = qtd * PREMIOS_VALOR.get(ac, 0)
                if premio > 0:
                    print(f"      {ac:2} acertos: {qtd:6,} × R$ {PREMIOS_VALOR.get(ac, 0):>10,.2f} = R$ {premio:>12,.2f}")
                else:
                    print(f"      {ac:2} acertos: {qtd:6,}")
            print(f"   Prêmio total: R$ {antes_premio:,.2f}")
            if antes_lucro >= 0:
                print(f"   ✅ LUCRO: R$ {antes_lucro:,.2f}")
            else:
                print(f"   ❌ PREJUÍZO: R$ {abs(antes_lucro):,.2f}")
            
            # Análise DEPOIS dos filtros (aprovadas)
            print(f"\n📊 DEPOIS DOS FILTROS ({len(melhores):,} combinações):")
            depois_acertos = []
            for m in melhores:
                comb = m['combinacao'] if isinstance(m, dict) else m
                acertos = len(set(comb) & nums_resultado)
                depois_acertos.append({'combinacao': comb, 'acertos': acertos})
            
            depois_dist = Counter(d['acertos'] for d in depois_acertos)
            depois_custo = len(melhores) * 3.50
            depois_premio = sum(depois_dist.get(ac, 0) * PREMIOS_VALOR.get(ac, 0) for ac in [11, 12, 13, 14, 15])
            depois_lucro = depois_premio - depois_custo
            
            print(f"   Custo: R$ {depois_custo:,.2f}")
            print(f"   Distribuição de acertos:")
            for ac in sorted([k for k in depois_dist.keys() if k >= 10], reverse=True):
                qtd = depois_dist[ac]
                premio = qtd * PREMIOS_VALOR.get(ac, 0)
                if premio > 0:
                    print(f"      {ac:2} acertos: {qtd:6,} × R$ {PREMIOS_VALOR.get(ac, 0):>10,.2f} = R$ {premio:>12,.2f}")
                else:
                    print(f"      {ac:2} acertos: {qtd:6,}")
            print(f"   Prêmio total: R$ {depois_premio:,.2f}")
            if depois_lucro >= 0:
                print(f"   ✅ LUCRO: R$ {depois_lucro:,.2f}")
            else:
                print(f"   ❌ PREJUÍZO: R$ {abs(depois_lucro):,.2f}")
            
            # Comparação financeira
            print(f"\n📊 COMPARAÇÃO FINANCEIRA:")
            print("-" * 60)
            print(f"   {'':20} | {'ANTES':>15} | {'DEPOIS':>15}")
            print(f"   {'Combinações':<20} | {len(self.combinacoes):>15,} | {len(melhores):>15,}")
            print(f"   {'Custo':<20} | R$ {antes_custo:>11,.2f} | R$ {depois_custo:>11,.2f}")
            print(f"   {'Prêmio':<20} | R$ {antes_premio:>11,.2f} | R$ {depois_premio:>11,.2f}")
            print(f"   {'Resultado':<20} | R$ {antes_lucro:>+11,.2f} | R$ {depois_lucro:>+11,.2f}")
            print("-" * 60)
            
            # Melhor acerto
            melhor_antes = max(antes_acertos) if antes_acertos else 0
            melhor_depois = max(d['acertos'] for d in depois_acertos) if depois_acertos else 0
            
            print(f"\n🏆 MELHOR ACERTO:")
            print(f"   Antes dos filtros: {melhor_antes} acertos")
            print(f"   Depois dos filtros: {melhor_depois} acertos")
            
            if melhor_depois < melhor_antes:
                print(f"   ⚠️ ALERTA: Os filtros eliminaram combinações com {melhor_antes} acertos!")
            elif melhor_depois == melhor_antes:
                print(f"   ✅ Os filtros mantiveram as melhores combinações!")
            
            # Top 5 melhores depois dos filtros
            depois_acertos.sort(key=lambda x: x['acertos'], reverse=True)
            print(f"\n🏆 TOP 5 MELHORES (após filtros):")
            for i, item in enumerate(depois_acertos[:5], 1):
                comb_str = " - ".join(f"{n:02d}" for n in item['combinacao'])
                print(f"   {i}. [{item['acertos']:2} acertos] {comb_str}")
            
            resultado_financeiro = {
                'antes': {'custo': antes_custo, 'premio': antes_premio, 'lucro': antes_lucro, 
                          'melhor': melhor_antes, 'dist': dict(antes_dist)},
                'depois': {'custo': depois_custo, 'premio': depois_premio, 'lucro': depois_lucro,
                           'melhor': melhor_depois, 'dist': dict(depois_dist)}
            }
        
        print("=" * 80)
        
        return {
            'antes': antes_stats,
            'depois': depois_stats,
            'comparacao': comparacao,
            'filtros_analise': filtros_analise,
            'filtros_problematicos': filtros_problematicos,
            'houve_piora': houve_piora,
            'resultado_financeiro': resultado_financeiro
        }
    
    def _calcular_stats_benchmark(self, combinacoes: List, resultados: List[Dict], label: str) -> Dict:
        """Calcula estatísticas de benchmark para um conjunto de combinações"""
        
        if isinstance(combinacoes[0], dict):
            # É uma lista de avaliações
            combinacoes = [c['combinacao'] for c in combinacoes]
        
        total_combinacoes = len(combinacoes)
        total_concursos = len(resultados)
        
        # Contadores
        acertos_por_nivel = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
        concursos_com_11 = 0
        concursos_com_12 = 0
        concursos_com_13 = 0
        soma_melhor_por_concurso = 0
        
        for resultado in resultados:
            nums_resultado = set(resultado['numeros'])
            melhor_acerto_concurso = 0
            
            for comb in combinacoes:
                comb_set = set(comb)
                acertos = len(comb_set & nums_resultado)
                melhor_acerto_concurso = max(melhor_acerto_concurso, acertos)
                
                if acertos >= 11:
                    acertos_por_nivel[acertos] = acertos_por_nivel.get(acertos, 0) + 1
            
            soma_melhor_por_concurso += melhor_acerto_concurso
            if melhor_acerto_concurso >= 11:
                concursos_com_11 += 1
            if melhor_acerto_concurso >= 12:
                concursos_com_12 += 1
            if melhor_acerto_concurso >= 13:
                concursos_com_13 += 1
        
        media_acertos = soma_melhor_por_concurso / total_concursos if total_concursos > 0 else 0
        
        return {
            'total': total_combinacoes,
            'concursos': total_concursos,
            'media_acertos': media_acertos,
            'concursos_11': concursos_com_11,
            'concursos_12': concursos_com_12,
            'concursos_13': concursos_com_13,
            'acertos_11': acertos_por_nivel.get(11, 0),
            'acertos_12': acertos_por_nivel.get(12, 0),
            'acertos_13': acertos_por_nivel.get(13, 0),
            'acertos_14': acertos_por_nivel.get(14, 0),
            'acertos_15': acertos_por_nivel.get(15, 0),
        }
    
    def _media_acertos_combinacoes(self, combinacoes: List[List[int]], resultados: List[Dict]) -> float:
        """Calcula média de melhor acerto por concurso para um conjunto de combinações"""
        if not combinacoes or not resultados:
            return 0.0
        
        soma = 0
        for resultado in resultados:
            nums_resultado = set(resultado['numeros'])
            melhor = 0
            for comb in combinacoes:
                acertos = len(set(comb) & nums_resultado)
                melhor = max(melhor, acertos)
            soma += melhor
        
        return soma / len(resultados)


def main():
    """Função principal interativa v2.0"""
    print("=" * 70)
    print("🔍 ANALISADOR DE COMBINAÇÕES GERADAS v2.0")
    print("⭐ FILTRA AS MELHORES DAS MELHORES ⭐")
    print("=" * 70)
    print("NOVIDADES v2.0:")
    print("   ✅ Validação contra histórico real (últimos 50 concursos)")
    print("   ✅ Análise de linhas/colunas do volante 5x5")
    print("   ✅ Filtro de números quentes (mín 5) e frios (máx 3)")
    print("   ✅ Filtro de repetições do último resultado (5-9)")
    print("   ✅ Score ponderado inteligente")
    print("   ✅ Diversidade de seleção (evita duplicadas)")
    print("   ✅ Benchmark automático (100 concursos)")
    print("=" * 70)
    
    print("\n📂 ARQUIVO DE ENTRADA:")
    caminho = input("   Caminho do arquivo: ").strip()
    
    if not caminho:
        print("❌ Caminho não informado!")
        return
    
    if not caminho.endswith('.txt'):
        caminho += '.txt'
    
    analisador = AnalisadorCombinacoesGeradas()
    
    if not analisador.carregar_arquivo(caminho):
        return
    
    print("\n⚙️ CONFIGURAÇÃO:")
    print("   1. Análise COMPLETA (recomendado)")
    print("   2. Análise RÁPIDA (sem validação histórica)")
    print("   3. Configurar filtros manualmente")
    print()
    
    opcao = input("   Escolha (1-3) [1]: ").strip() or "1"
    
    validar_hist = True
    if opcao == "2":
        validar_hist = False
    elif opcao == "3":
        print("\n   Configurando filtros (Enter = padrão):")
        try:
            for key in ['soma_min', 'soma_max', 'quentes_min', 'frios_max', 
                       'repeticoes_min', 'repeticoes_max', 'media_acertos_min']:
                val = input(f"   {key} [{analisador.filtros[key]}]: ").strip()
                if val:
                    analisador.filtros[key] = float(val) if '.' in val else int(val)
        except ValueError:
            print("   ⚠️ Valor inválido, usando padrão")
    
    f = analisador.filtros
    print("\n📋 FILTROS ATIVOS v2.0:")
    print(f"   • Soma: {f['soma_min']}-{f['soma_max']} | Pares: {f['pares_min']}-{f['pares_max']}")
    print(f"   • Primos: {f['primos_min']}-{f['primos_max']} | Fibonacci: {f['fibonacci_min']}-{f['fibonacci_max']}")
    print(f"   • Linhas: {f['linha_min']}-{f['linha_max']} | Colunas: {f['coluna_min']}-{f['coluna_max']}")
    print(f"   • Quentes: ≥{f['quentes_min']} | Frios: ≤{f['frios_max']} | Repetições: {f['repeticoes_min']}-{f['repeticoes_max']}")
    print(f"   • Média histórica: ≥{f['media_acertos_min']}")
    
    inicio = datetime.now()
    
    avaliacoes = analisador.analisar_todas(validar_hist)
    melhores = analisador.filtrar_melhores(avaliacoes)
    
    if not melhores:
        print("\n❌ Nenhuma combinação passou em TODOS os filtros!")
        print("   💡 Tente ajustar os filtros para serem menos restritivos")
        return
    
    print(f"\n🎯 DIVERSIDADE:")
    print(f"   Encontradas {len(melhores):,} combinações que passaram em todos filtros")
    aplicar_div = input("   Aplicar filtro de diversidade? (s/n) [s]: ").strip().lower()
    
    if aplicar_div != 'n':
        max_sob = input("   Máximo de números iguais entre combinações (8-12) [11]: ").strip()
        max_sob = int(max_sob) if max_sob else 11
        melhores = analisador.aplicar_diversidade(melhores, max_sobreposicao=max_sob)
    
    # REDUTOR INTELIGENTE - Novo filtro estatístico
    print(f"\n🎯 REDUTOR INTELIGENTE:")
    print(f"   Aplica filtros estatísticos avançados (Primos, Quintis, SEQ, etc.)")
    print(f"   Combinações atuais: {len(melhores):,}")
    aplicar_redutor = input("   Aplicar redutor inteligente? (s/n) [n]: ").strip().lower()
    
    if aplicar_redutor == 's':
        melhores = analisador.menu_redutor_inteligente(melhores)
    
    analisador.mostrar_amostra(melhores)
    
    # Loop de Benchmark - permite múltiplos testes sem recarregar
    continuar_benchmark = True
    
    while continuar_benchmark:
        # Menu de Benchmark
        print("\n🏆 BENCHMARK:")
        print("   1. Benchmark AUTOMÁTICO (últimos 100 concursos)")
        print("   2. Benchmark CONCURSO ESPECÍFICO (informar número)")
        print("   3. Benchmark MANUAL (digitar 15 números)")
        print("   4. Benchmark COMPARATIVO (valida eficácia dos filtros) ⭐ NOVO")
        print("   5. Pular benchmark / Sair do loop")
        print()
        
        opcao_bench = input("   Escolha (1-5) [1]: ").strip() or "1"
        
        if opcao_bench == "1":
            analisador.benchmark_automatico(melhores, ultimos_n=100)
        
        elif opcao_bench == "2":
            num_concurso = input("   Número do concurso: ").strip()
            if num_concurso.isdigit():
                analisador.benchmark_concurso_especifico(melhores, concurso=int(num_concurso))
            else:
                print("   ❌ Número inválido!")
        
        elif opcao_bench == "3":
            print("   Digite os 15 números separados por espaço ou vírgula:")
            nums_str = input("   Números: ").strip()
            try:
                if ',' in nums_str:
                    nums = [int(n.strip()) for n in nums_str.split(',')]
                else:
                    nums = [int(n.strip()) for n in nums_str.split()]
                
                if len(nums) == 15 and all(1 <= n <= 25 for n in nums):
                    analisador.benchmark_concurso_especifico(melhores, numeros=nums)
                else:
                    print("   ❌ Deve informar exatamente 15 números entre 1 e 25!")
            except:
                print("   ❌ Formato inválido!")
        
        elif opcao_bench == "4":
            print("\n🔬 BENCHMARK COMPARATIVO - Validação de eficácia dos filtros")
            print("\n   Qual modo de análise?")
            print("   1. Apenas HISTÓRICO (concursos da base)")
            print("   2. Apenas MANUAL (digitar resultado)")
            print("   3. AMBOS (histórico + manual)")
            modo_opcao = input("   Escolha (1-3) [1]: ").strip() or "1"
            
            modo = 'historico'
            n_concursos = 50
            numeros_manual = None
            
            if modo_opcao == "1":
                modo = 'historico'
                n_concursos = input("   Quantos concursos do histórico? (10-100) [50]: ").strip()
                n_concursos = int(n_concursos) if n_concursos.isdigit() else 50
                n_concursos = max(10, min(100, n_concursos))
            
            elif modo_opcao == "2":
                modo = 'manual'
                print("   Digite os 15 números separados por espaço ou vírgula:")
                nums_str = input("   Números: ").strip()
                try:
                    if ',' in nums_str:
                        numeros_manual = [int(n.strip()) for n in nums_str.split(',')]
                    else:
                        numeros_manual = [int(n.strip()) for n in nums_str.split()]
                    
                    if len(numeros_manual) != 15 or not all(1 <= n <= 25 for n in numeros_manual):
                        print("   ❌ Deve informar exatamente 15 números entre 1 e 25!")
                        numeros_manual = None
                except:
                    print("   ❌ Formato inválido!")
                    numeros_manual = None
            
            elif modo_opcao == "3":
                modo = 'ambos'
                n_concursos = input("   Quantos concursos do histórico? (10-100) [50]: ").strip()
                n_concursos = int(n_concursos) if n_concursos.isdigit() else 50
                n_concursos = max(10, min(100, n_concursos))
                
                print("   Digite os 15 números do resultado manual (espaço ou vírgula):")
                nums_str = input("   Números: ").strip()
                try:
                    if ',' in nums_str:
                        numeros_manual = [int(n.strip()) for n in nums_str.split(',')]
                    else:
                        numeros_manual = [int(n.strip()) for n in nums_str.split()]
                    
                    if len(numeros_manual) != 15 or not all(1 <= n <= 25 for n in numeros_manual):
                        print("   ❌ Deve informar exatamente 15 números entre 1 e 25!")
                        numeros_manual = None
                except:
                    print("   ❌ Formato inválido!")
                    numeros_manual = None
            
            if modo == 'manual' and not numeros_manual:
                print("   ❌ Modo manual requer números válidos!")
            else:
                analisador.benchmark_comparativo(ultimos_n=n_concursos, numeros_manual=numeros_manual, modo=modo)
        
        else:
            # Opção 5 ou qualquer outra = sair do loop
            continuar_benchmark = False
            continue
        
        # Perguntar se quer fazer outro benchmark
        print("\n" + "-" * 50)
        repetir = input("   🔄 Fazer outro benchmark com as mesmas combinações? (s/n) [s]: ").strip().lower()
        if repetir == 'n':
            continuar_benchmark = False
    
    print(f"\n💾 SALVAR RESULTADOS?")
    print(f"   Total final: {len(melhores):,} combinações")
    
    salvar = input("   Salvar arquivo? (s/n) [s]: ").strip().lower()
    
    if salvar != 'n':
        arquivo = analisador.salvar_melhores(melhores)
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print("\n" + "=" * 70)
    print("✅ ANÁLISE v2.0 CONCLUÍDA!")
    print("=" * 70)
    print(f"   ⏱️ Tempo total: {duracao:.2f} segundos")
    print(f"   📊 Analisadas: {len(analisador.combinacoes):,} combinações")
    print(f"   ⭐ Finais: {len(melhores):,} combinações")
    print(f"   📉 Redução total: {(1 - len(melhores)/len(analisador.combinacoes))*100:.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
