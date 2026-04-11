# -*- coding: utf-8 -*-
"""
CONFIGURAÇÃO CENTRALIZADA DOS FILTROS DO POOL 23
=================================================
Arquivo único de configuração para todos os níveis de filtros.
Usado por: Option 31 (Gerador), Option 30.2 (Backtesting), Option 30.4 (Histórico)

ATUALIZADO: 06/04/2026
- Nova estrutura baseada em análise de seletividade
- Filosofia: Níveis 1-3 (Jackpot), 4-5 (Equilibrado), 6 (Agressivo)
- Remoção de filtros "assassinos" (Extremos 2-4, Consecutivos max 3)
- Adição do filtro de TRIOS FREQUENTES para níveis 4-6
- NOVOS: Filtros Fibonacci, Quintis e Faixa 6-20 (POC Monte Carlo 06/04/2026)
  - Fibonacci: seletividade 1.084-1.139 | Quintis: 1.048-1.092 | Faixa 6-20: 1.028-1.115
  - Combinados: Fib+Quintis seletividade 1.169 (efeito sinérgico!)

SELETIVIDADE = Taxa_Real / Taxa_Random
- > 1.0: Filtro INTELIGENTE (rejeita mais lixo que jackpots)
- = 1.0: Filtro NEUTRO (só reduz volume)
- < 1.0: Filtro BURRO (rejeita mais jackpots que lixo)
"""

import pyodbc
from itertools import combinations
from functools import lru_cache

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
NUCLEO_C1C2 = {2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 22, 24, 25}

# Posições com sinal preditivo estável quando "travadas" (3/3 ou 2/3 em janela de 3)
# Ganho médio: N1 +12pp, N2 +9pp, N3 +6pp, N6 +7pp, N14 +8pp, N15 +18pp
# Validado historicamente em 3.653 concursos, estável em blocos de 500
POSICOES_TRAVADAS_ALVO = [0, 1, 2, 5, 13, 14]  # 0-indexed: N1, N2, N3, N6, N14, N15

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE FILTROS POR NÍVEL
# ═══════════════════════════════════════════════════════════════════════════════
# FILOSOFIA:
#   Níveis 1-3: FOCO JACKPOT - preservar 65-90% dos jackpots
#   Níveis 4-5: EQUILIBRADO - reduzir volume, compensar com prêmios menores (11-14)
#   Nível 6: AGRESSIVO CONSCIENTE - aceita perder jackpots, aposta concentrada

FILTROS_POR_NIVEL = {
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 0: SEM FILTROS (baseline)
    # ═══════════════════════════════════════════════════════════════════════════
    0: {
        # 490k combinações, 100% jackpots preservados
        'descricao': 'Sem filtros - baseline 490k',
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 1: MÍNIMO - Foco Jackpot (meta: ~90% jackpots, ~350k combos)
    # ═══════════════════════════════════════════════════════════════════════════
    1: {
        'descricao': 'Mínimo - foco jackpot',
        # Soma: range amplo (seletividade ~1.0, 97.7% cobertura)
        'soma_min': 170, 'soma_max': 235,
        # ═══════════════════════════════════════════════════════════════════
        # FILTRO DE REPETIÇÃO (quantos do último sorteio devem repetir)
        # Histórico: média ~9, 90% dos casos entre 6-12
        # ═══════════════════════════════════════════════════════════════════
        'rep_min': 5, 'rep_max': 12,  # Amplo (quase não filtra)
        # Débito posicional (50.7% assertividade)
        'usar_debito_posicional': True,
        'debito_min_matches': 1,
        # Análise de anomalias (evita números "muito quentes")
        'usar_analise_anomalias': True,
        'anomalias_max_quentes': 3,
        'anomalias_min_frios': 0,
        # Qtde 6-25 (seletividade 1.0, 93.7% cobertura)
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [9, 10, 11, 12, 13, 14],  # Ampliado
        # Sub-combos quentes (COMBIN_10) — seletividade 5.75x com min_acertos=6
        'usar_filtro_subcombos': True,
        'subcombos_min_acertos': 6,
        'subcombos_min_hot': 400,  # Conservador (~95% jackpots, ~20% random)
        # ═══════════════════════════════════════════════════════════════════
        # NOVOS FILTROS POC 06/04/2026 — Fibonacci, Faixa 6-20
        # Conservador: faixas amplas, máxima preservação de jackpots
        # ═══════════════════════════════════════════════════════════════════
        'usar_filtro_fibonacci': True,
        'fibonacci_min': 3, 'fibonacci_max': 6,  # Seletiv 1.084, 93% jackpots
        'usar_filtro_faixa_6_20': True,
        'faixa_6_20_min': 7, 'faixa_6_20_max': 10,  # Seletiv 1.115, 88.4% jackpots
        # Posições Travadas (janela 3 — favorecer repetição em posições estáveis)
        'usar_filtro_posicoes_travadas': True,
        'posicoes_travadas_tolerancia': 4,  # Muito permissivo (~91% concursos passam)
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 2: BÁSICO - Foco Jackpot (meta: ~80% jackpots, ~250k combos)
    # ═══════════════════════════════════════════════════════════════════════════
    2: {
        'descricao': 'Básico - foco jackpot',
        # Soma um pouco mais restrita
        'soma_min': 175, 'soma_max': 230,
        # Pares: seletividade 1.01x
        'pares_min': 6, 'pares_max': 9,
        # Repetição com último sorteio
        'rep_min': 5, 'rep_max': 11,
        # Consecutivos amplos (NUNCA usar max < 5!)
        'consecutivos_min': 7, 'consecutivos_max': 11,
        'gap_max': 5,
        # Reversão de soma
        'usar_reversao_soma': True,
        # Débito posicional
        'usar_debito_posicional': True,
        'debito_min_matches': 2,
        # Anomalias
        'usar_analise_anomalias': True,
        'anomalias_max_quentes': 3,
        'anomalias_min_frios': 0,
        # Filtros posicionais
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
        'usar_filtro_piores_historico': True,
        'piores_tolerancia_historico': 1,  # Tolerância 1 (antes era 0)
        # Sub-combos quentes
        'usar_filtro_subcombos': True,
        'subcombos_min_acertos': 6,
        'subcombos_min_hot': 450,
        # NOVOS FILTROS POC 06/04/2026 — Conservador
        'usar_filtro_fibonacci': True,
        'fibonacci_min': 3, 'fibonacci_max': 6,
        'usar_filtro_faixa_6_20': True,
        'faixa_6_20_min': 7, 'faixa_6_20_max': 10,
        # Posições Travadas
        'usar_filtro_posicoes_travadas': True,
        'posicoes_travadas_tolerancia': 3,  # Recomendado (~75% concursos passam)
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 3: BALANCEADO - Foco Jackpot (meta: ~66% jackpots, ~150k combos)
    # ═══════════════════════════════════════════════════════════════════════════
    3: {
        'descricao': 'Balanceado - foco jackpot',
        # Soma equilibrada
        'soma_min': 180, 'soma_max': 225,
        # Pares/Primos
        'pares_min': 6, 'pares_max': 9,
        'primos_min': 4, 'primos_max': 7,
        # Repetição com último sorteio (moderado)
        'rep_min': 5, 'rep_max': 11,
        # Consecutivos (IMPORTANTE: max >= 6 para não matar jackpots)
        'consecutivos_min': 7, 'consecutivos_max': 10,
        'gap_max': 5,
        'seq_max': 6,  # Máximo de números consecutivos na combinação
        # Reversão de soma
        'usar_reversao_soma': True,
        # Débito posicional
        'usar_debito_posicional': True,
        'debito_min_matches': 2,
        # Anomalias (um pouco mais restritivo)
        'usar_analise_anomalias': True,
        'anomalias_max_quentes': 2,
        'anomalias_min_frios': 1,
        # Filtros posicionais
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
        'usar_filtro_piores_historico': True,
        'piores_tolerancia_historico': 0,
        'usar_filtro_piores_recente': True,
        'piores_tolerancia_recente': 5,  # Tolerância alta (gradiente 5→4→3→2)
        # Sub-combos quentes
        'usar_filtro_subcombos': True,
        'subcombos_min_acertos': 6,
        'subcombos_min_hot': 500,
        # NOVOS FILTROS POC 06/04/2026 — Equilibrado (Fib + Quintis + F6-20)
        'usar_filtro_fibonacci': True,
        'fibonacci_min': 3, 'fibonacci_max': 6,
        'usar_filtro_quintis': True,
        'quintis_min': 1, 'quintis_max': 4,  # Seletiv 1.091, 73.2% jackpots
        'usar_filtro_faixa_6_20': True,
        'faixa_6_20_min': 7, 'faixa_6_20_max': 10,
        # Posições Travadas
        'usar_filtro_posicoes_travadas': True,
        'posicoes_travadas_tolerancia': 3,  # ~75% concursos passam
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 4: EQUILIBRADO (meta: ~35% jackpots, ~80k combos, bom ROI em 11-14)
    # ═══════════════════════════════════════════════════════════════════════════
    4: {
        'descricao': 'Equilibrado - redução + prêmios menores',
        # Soma moderada
        'soma_min': 180, 'soma_max': 220,
        # Pares/Primos mais restritos
        'pares_min': 6, 'pares_max': 9,
        'primos_min': 4, 'primos_max': 7,
        # Repetição com último sorteio (mais restrito)
        'rep_min': 5, 'rep_max': 10,
        # Consecutivos e gap
        'consecutivos_min': 7, 'consecutivos_max': 9,
        'gap_max': 4,
        'seq_max': 5,
        # Reversão de soma
        'usar_reversao_soma': True,
        # Débito posicional
        'usar_debito_posicional': True,
        'debito_min_matches': 3,
        # Anomalias restritivo
        'usar_analise_anomalias': True,
        'anomalias_max_quentes': 2,
        'anomalias_min_frios': 1,
        # Filtros posicionais
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
        'usar_filtro_piores_historico': True,
        'piores_tolerancia_historico': 0,
        'usar_filtro_piores_recente': True,
        'piores_tolerancia_recente': 4,
        # ═══════════════════════════════════════════════════════════════════
        # NOVO: FILTRO DE TRIOS FREQUENTES (seletividade ~1.14x)
        # ═══════════════════════════════════════════════════════════════════
        'usar_filtro_trios': True,
        'trios_min_frequencia': 750,  # Trios com >= 750 aparições (~20% dos concursos)
        'trios_min_presentes': 80,    # Mínimo de trios frequentes na combinação
        # Sub-combos quentes
        'usar_filtro_subcombos': True,
        'subcombos_min_acertos': 6,
        'subcombos_min_hot': 550,
        # NOVOS FILTROS POC 06/04/2026 — Agressivo (faixas apertadas)
        'usar_filtro_fibonacci': True,
        'fibonacci_min': 4, 'fibonacci_max': 5,  # Seletiv 1.139, 59% jackpots
        'usar_filtro_quintis': True,
        'quintis_min': 2, 'quintis_max': 4,  # Seletiv 1.092, 55.4% jackpots
        'usar_filtro_faixa_6_20': True,
        'faixa_6_20_min': 8, 'faixa_6_20_max': 10,  # Seletiv 1.028, 78% jackpots
        # Posições Travadas
        'usar_filtro_posicoes_travadas': True,
        'posicoes_travadas_tolerancia': 2,  # Moderado (~49% concursos passam)
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 5: AGRESSIVO (meta: ~16% jackpots, ~40k combos, ROI alto em 11-14)
    # ═══════════════════════════════════════════════════════════════════════════
    5: {
        'descricao': 'Agressivo - ROI em prêmios menores',
        # Soma mais restrita
        'soma_min': 180, 'soma_max': 215,
        # Pares/Primos
        'pares_min': 6, 'pares_max': 9,
        'primos_min': 4, 'primos_max': 7,
        # Consecutivos e gap restritivos
        'consecutivos_min': 7, 'consecutivos_max': 9,
        'gap_max': 4,
        'seq_max': 5,
        # Repetição com concurso anterior
        'rep_min': 4, 'rep_max': 11,
        'nucleo_min': 8,
        # Reversão de soma
        'usar_reversao_soma': True,
        # Débito posicional
        'usar_debito_posicional': True,
        'debito_min_matches': 3,
        # Anomalias muito restritivo
        'usar_analise_anomalias': True,
        'anomalias_max_quentes': 1,
        'anomalias_min_frios': 2,
        # Filtros posicionais
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
        'usar_filtro_piores_historico': True,
        'piores_tolerancia_historico': 0,
        'usar_filtro_piores_recente': True,
        'piores_tolerancia_recente': 3,
        # Linhas 2-4 (seletividade 1.02x - bom complemento)
        'usar_filtro_linhas': True,
        'linhas_min': 2, 'linhas_max': 4,
        # FILTRO DE TRIOS mais restritivo
        'usar_filtro_trios': True,
        'trios_min_frequencia': 750,
        'trios_min_presentes': 100,   # Mais exigente que N4
        # Sub-combos quentes
        'usar_filtro_subcombos': True,
        'subcombos_min_acertos': 6,
        'subcombos_min_hot': 600,
        # NOVOS FILTROS POC 06/04/2026 — Agressivo
        'usar_filtro_fibonacci': True,
        'fibonacci_min': 4, 'fibonacci_max': 5,
        'usar_filtro_quintis': True,
        'quintis_min': 2, 'quintis_max': 4,
        'usar_filtro_faixa_6_20': True,
        'faixa_6_20_min': 8, 'faixa_6_20_max': 10,
        # Posições Travadas
        'usar_filtro_posicoes_travadas': True,
        'posicoes_travadas_tolerancia': 2,  # Moderado (~49% concursos passam)
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 6: ULTRA AGRESSIVO (meta: ~5% jackpots, ~15k combos, aposta concentrada)
    # ═══════════════════════════════════════════════════════════════════════════
    6: {
        'descricao': 'Ultra - aposta concentrada',
        # Soma estreita
        'soma_min': 185, 'soma_max': 210,
        # Pares mais restrito (seletividade 1.09x - MELHOR)
        'pares_min': 7, 'pares_max': 8,
        # Primos
        'primos_min': 4, 'primos_max': 6,
        # Consecutivos e gap
        'consecutivos_min': 7, 'consecutivos_max': 9,
        'gap_max': 4,
        'seq_max': 5,
        # Repetição
        'rep_min': 5, 'rep_max': 10,
        'nucleo_min': 8,
        # Reversão de soma
        'usar_reversao_soma': True,
        # Débito posicional
        'usar_debito_posicional': True,
        'debito_min_matches': 3,
        # Anomalias máximo
        'usar_analise_anomalias': True,
        'anomalias_max_quentes': 1,
        'anomalias_min_frios': 2,
        # Filtros posicionais
        'usar_filtro_qtde_6_25': True,
        'qtde_6_25_valores': [10, 11, 12, 13],
        'usar_filtro_piores_historico': True,
        'piores_tolerancia_historico': 0,
        'usar_filtro_piores_recente': True,
        'piores_tolerancia_recente': 2,  # Mais apertado
        # Linhas/Colunas (seletividade ~1.0, boa redução)
        'usar_filtro_linhas': True,
        'linhas_min': 2, 'linhas_max': 4,
        'usar_filtro_colunas': True,
        'colunas_min': 2, 'colunas_max': 4,
        # FILTRO DE TRIOS máximo
        'usar_filtro_trios': True,
        'trios_min_frequencia': 750,
        'trios_min_presentes': 120,   # Mais exigente
        # Sub-combos quentes
        'usar_filtro_subcombos': True,
        'subcombos_min_acertos': 6,
        'subcombos_min_hot': 650,
        # NOVOS FILTROS POC 06/04/2026 — Ultra agressivo
        'usar_filtro_fibonacci': True,
        'fibonacci_min': 4, 'fibonacci_max': 5,
        'usar_filtro_quintis': True,
        'quintis_min': 2, 'quintis_max': 4,
        'usar_filtro_faixa_6_20': True,
        'faixa_6_20_min': 8, 'faixa_6_20_max': 10,
        # Posições Travadas
        'usar_filtro_posicoes_travadas': True,
        'posicoes_travadas_tolerancia': 1,  # Agressivo (~34% concursos passam)
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 7: POSIÇÕES FRIAS (Nível 0 + filtro posicional frio)
    # ═══════════════════════════════════════════════════════════════════════════
    7: {
        'descricao': 'Posições frias sobre N0',
        'usar_filtro_posicoes_frias': True,
        'posicoes_frias_janela': 6,
        'posicoes_frias_tolerancia': 4,
        'nivel_base': 0,
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NÍVEL 8: CASCATA + POSIÇÕES FRIAS
    # ═══════════════════════════════════════════════════════════════════════════
    8: {
        'descricao': 'Cascata adaptativa + posições frias',
        'usar_filtro_posicoes_frias': True,
        'posicoes_frias_janela': 6,
        'posicoes_frias_tolerancia': 3,
        'nivel_base': 'cascata',  # Começa no 6, desce até encontrar combos
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE: FILTRO DE TRIOS FREQUENTES
# ═══════════════════════════════════════════════════════════════════════════════
class FiltroTrios:
    """
    Filtro que verifica se uma combinação contém trios frequentes.
    
    Seletividade: ~1.14x (trios com freq >= 750, min 100 presentes)
    - Preserva 35% dos jackpots
    - Reduz 70% das combinações
    """
    
    _instance = None
    _trios_cache = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if FiltroTrios._trios_cache is None:
            self._carregar_trios()
    
    def _carregar_trios(self):
        """Carrega trios da view CONTA_TRIOS_LOTO"""
        try:
            conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT num1, num2, num3, quantidade FROM [dbo].[CONTA_TRIOS_LOTO]")
            
            FiltroTrios._trios_cache = {}
            for row in cursor.fetchall():
                trio = (row[0], row[1], row[2])
                FiltroTrios._trios_cache[trio] = row[3]
            
            conn.close()
            print(f"      🔺 FiltroTrios: {len(FiltroTrios._trios_cache):,} trios carregados")
        except Exception as e:
            print(f"      ⚠️ FiltroTrios: Erro ao carregar ({e})")
            FiltroTrios._trios_cache = {}
    
    def contar_trios_frequentes(self, combinacao, min_frequencia=700):
        """
        Conta quantos trios frequentes existem na combinação.
        
        Args:
            combinacao: lista de 15 números
            min_frequencia: frequência mínima do trio para contar
            
        Returns:
            int: quantidade de trios frequentes na combinação
        """
        if not FiltroTrios._trios_cache:
            return 455  # Retorna máximo se não tem dados (não filtrar)
        
        nums = tuple(sorted(combinacao))
        contagem = 0
        
        for trio in combinations(nums, 3):
            if trio in FiltroTrios._trios_cache:
                if FiltroTrios._trios_cache[trio] >= min_frequencia:
                    contagem += 1
        
        return contagem
    
    def filtrar(self, combinacao, min_frequencia=700, min_presentes=80):
        """
        Verifica se a combinação passa no filtro de trios.
        
        Args:
            combinacao: lista de 15 números
            min_frequencia: frequência mínima do trio
            min_presentes: quantidade mínima de trios frequentes exigidos
            
        Returns:
            bool: True se passa no filtro
        """
        return self.contar_trios_frequentes(combinacao, min_frequencia) >= min_presentes


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE FILTRAGEM
# ═══════════════════════════════════════════════════════════════════════════════

def filtro_soma(combinacao, soma_min, soma_max):
    """Verifica se soma está no range"""
    soma = sum(combinacao)
    return soma_min <= soma <= soma_max

def filtro_pares(combinacao, pares_min, pares_max):
    """Verifica quantidade de números pares"""
    qtde = sum(1 for n in combinacao if n % 2 == 0)
    return pares_min <= qtde <= pares_max

def filtro_primos(combinacao, primos_min, primos_max):
    """Verifica quantidade de números primos"""
    qtde = sum(1 for n in combinacao if n in PRIMOS)
    return primos_min <= qtde <= primos_max

def filtro_consecutivos_sequencia(combinacao, seq_max):
    """Verifica maior sequência de números consecutivos"""
    nums = sorted(combinacao)
    max_seq = 1
    seq_atual = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            seq_atual += 1
            max_seq = max(max_seq, seq_atual)
        else:
            seq_atual = 1
    return max_seq <= seq_max

def filtro_linhas(combinacao, linhas_min, linhas_max):
    """Verifica se cada linha tem entre min e max números"""
    linhas = [0, 0, 0, 0, 0]
    for n in combinacao:
        linhas[(n-1) // 5] += 1
    return all(linhas_min <= l <= linhas_max for l in linhas)

def filtro_colunas(combinacao, colunas_min, colunas_max):
    """Verifica se cada coluna tem entre min e max números"""
    colunas = [0, 0, 0, 0, 0]
    for n in combinacao:
        colunas[(n-1) % 5] += 1
    return all(colunas_min <= c <= colunas_max for c in colunas)

def filtro_qtde_6_25(combinacao, valores_aceitos):
    """Verifica se quantidade de números no range 6-25 está nos valores aceitos"""
    qtde = sum(1 for n in combinacao if 6 <= n <= 25)
    return qtde in valores_aceitos


def filtro_fibonacci(combinacao, fib_min, fib_max):
    """Verifica quantidade de números Fibonacci {1,2,3,5,8,13,21} na combinação"""
    qtde = sum(1 for n in combinacao if n in FIBONACCI)
    return fib_min <= qtde <= fib_max


def filtro_faixa_6_20(combinacao, f_min, f_max):
    """Verifica quantidade de números no range 6-20"""
    qtde = sum(1 for n in combinacao if 6 <= n <= 20)
    return f_min <= qtde <= f_max


def filtro_quintis(combinacao, q_min, q_max):
    """Verifica se cada quintil (1-5,6-10,11-15,16-20,21-25) tem entre q_min e q_max números"""
    quintis = [0, 0, 0, 0, 0]
    for n in combinacao:
        quintis[(n - 1) // 5] += 1
    return all(q_min <= q <= q_max for q in quintis)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER: Obter configuração do nível
# ═══════════════════════════════════════════════════════════════════════════════

def obter_filtros_nivel(nivel: int) -> dict:
    """
    Retorna a configuração de filtros para um nível específico.
    
    Args:
        nivel: 0-8
        
    Returns:
        dict: configuração de filtros do nível
    """
    return FILTROS_POR_NIVEL.get(nivel, {})


def obter_descricao_nivel(nivel: int) -> str:
    """Retorna descrição curta do nível"""
    config = obter_filtros_nivel(nivel)
    return config.get('descricao', f'Nível {nivel}')


def listar_niveis():
    """Lista todos os níveis disponíveis"""
    return list(FILTROS_POR_NIVEL.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# PARA DEBUG/EXIBIÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def exibir_resumo_filtros():
    """Exibe um resumo dos filtros por nível"""
    print("\n" + "═"*78)
    print("📊 RESUMO DOS FILTROS POR NÍVEL (Pool 23)")
    print("═"*78)
    
    for nivel, config in FILTROS_POR_NIVEL.items():
        desc = config.get('descricao', 'Sem descrição')
        print(f"\n   [N{nivel}] {desc}")
        
        # Filtros principais
        if 'soma_min' in config:
            print(f"      • Soma: {config['soma_min']}-{config['soma_max']}")
        if 'pares_min' in config:
            print(f"      • Pares: {config['pares_min']}-{config['pares_max']}")
        if 'seq_max' in config:
            print(f"      • Consecutivos: max {config['seq_max']}")
        if config.get('usar_filtro_trios'):
            print(f"      • Trios: freq>={config['trios_min_frequencia']}, min={config['trios_min_presentes']}")
        if config.get('usar_filtro_linhas'):
            print(f"      • Linhas: {config['linhas_min']}-{config['linhas_max']} cada")
        if config.get('usar_filtro_posicoes_frias'):
            print(f"      • Posições frias: janela={config['posicoes_frias_janela']}, tol={config['posicoes_frias_tolerancia']}")
    
    print("\n" + "═"*78)


if __name__ == '__main__':
    exibir_resumo_filtros()
