#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANALISADOR POSICIONAL + COMBINACOES EXPANDIDO - VERSAO v4.0
=============================================================
Integra analise posicional (N1-N15) com TODAS as combinacoes:
Duplas, Trios, Quinas, Sextetos, Setetetos, Octetos, Nonetos, Decatetos e Undecetos

FUNCIONALIDADES:
=== POSICIONAL ===
1. Analise de probabilidades por posicao (N1-N15)
2. Numeros "encalhados" por posicao (nao saem ha X concursos)

=== COMBINACOES EXPANDIDAS (v4.0) ===
3. Duplas (2 numeros) - frequencia, atraso, divida
4. Trios (3 numeros) - frequencia, atraso, divida
5. Quartetos (4 numeros) - frequencia, atraso, divida
6. Quinas (5 numeros) - frequencia, atraso, divida
7. Sextetos (6 numeros) - frequencia, atraso, divida
8. Setetetos (7 numeros) - frequencia, atraso, divida
9. Octetos (8 numeros) - frequencia, atraso, divida
10. Nonetos (9 numeros) - frequencia, atraso, divida
11. Decatetos (10 numeros) - frequencia, atraso, divida
12. Undecetos (11 numeros) - frequencia, atraso, divida

=== ANALISES POR TAMANHO ===
- Combinacoes em "divida" REAL (atraso > intervalo medio)
- Intervalo Medio = Total Concursos / Frequencia
- Desvio = Atraso - Intervalo Medio
- %Acima = Percentual acima da media
- Numeros pivo (conectam combinacoes frequentes)
- MEGA PIVOS (numeros que sao pivo em multiplos tamanhos)

=== PREDICAO ===
12. Predicao posicional para proximo concurso

BASEADO EM:
- View CONTA_TRIOS_LOTO (frequencia, ultimo concurso)
- Calculo dinamico de combinacoes em Python
- Tabela Resultados_INT (posicoes N1-N15)
- Analises validadas no redutor de combinacoes

Autor: LotoScope AI
Data: Janeiro 2026
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
from collections import Counter, defaultdict
import statistics

# Configurar paths
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

# Importar integrador de padrões ocultos
try:
    from integracao_padroes_ocultos import (
        PadroesOcultosIntegrador,
        obter_trios_padroes_ocultos,
        calcular_score_padroes
    )
    PADROES_OCULTOS_DISPONIVEIS = True
except ImportError:
    PADROES_OCULTOS_DISPONIVEIS = False

from database_config import db_config


class AnalisadorPosicionalTrios:
    """
    Analisador que combina:
    - Analise posicional (N1-N15)
    - Dados de combinacoes (duplas a undecetos)
    - Frequencia, atraso e divida para cada tamanho
    - Insights validados no redutor
    
    TAMANHOS ANALISADOS:
    - 2: Duplas
    - 3: Trios
    - 5: Quinas
    - 6: Sextetos
    - 7: Setetetos
    - 8: Octetos
    - 9: Nonetos
    - 10: Decatetos
    - 11: Undecetos
    """
    
    # Nomes dos tamanhos de combinacoes
    NOMES_COMBINACOES = {
        2: "Duplas",
        3: "Trios",
        4: "Quartetos",
        5: "Quinas",
        6: "Sextetos",
        7: "Setetetos",
        8: "Octetos",
        9: "Nonetos",
        10: "Decatetos",
        11: "Undecetos"
    }
    
    def __init__(self):
        self.db_config = db_config
        self.dados_posicionais = []  # Historico de N1-N15
        self.dados_trios = []        # Dados da view CONTA_TRIOS_LOTO
        self.dados_quinas = []       # Dados de quinas (calculado em Python)
        self.ultimo_concurso = None
        self.probs_por_posicao = {}  # Probabilidades por posicao
        self.numeros_encalhados = {} # Por posicao
        self.trios_em_divida = []    # Frequencia alta + atraso alto
        self.quinas_em_divida = []   # Quinas com frequencia alta + atraso alto
        self.numeros_pivo = set()    # Conectam trios frequentes
        self.numeros_pivo_quinas = set()  # Conectam quinas frequentes
        
        # NOVO: Dados para todos os tamanhos de combinacoes
        self.dados_combinacoes = {}  # {tamanho: [lista de dados]}
        self.combinacoes_em_divida = {}  # {tamanho: [lista em divida]}
        self.numeros_pivo_por_tamanho = {}  # {tamanho: set()}
        
        # NOVO: Integração com padrões ocultos
        self.usar_padroes_ocultos = PADROES_OCULTOS_DISPONIVEIS
        self.integrador_padroes = None
        if self.usar_padroes_ocultos:
            try:
                self.integrador_padroes = PadroesOcultosIntegrador()
                print("[PADRÕES] Padrões ocultos carregados com sucesso!")
            except Exception as e:
                print(f"[AVISO] Padrões ocultos não disponíveis: {e}")
                self.usar_padroes_ocultos = False
        
    def carregar_dados_posicionais(self, limite_concursos: int = 500) -> bool:
        """Carrega historico de posicoes N1-N15"""
        print("[DATA] Carregando dados posicionais...")
        
        try:
            query = f"""
            SELECT TOP {limite_concursos}
                Concurso, Data_Sorteio,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            resultados = self.db_config.execute_query(query)
            
            for row in resultados:
                dados = {
                    'concurso': row[0],
                    'data': row[1],
                    'numeros': [row[i] for i in range(2, 17)]  # N1-N15
                }
                # Adicionar por posicao
                for i in range(15):
                    dados[f'N{i+1}'] = row[i+2]
                
                self.dados_posicionais.append(dados)
            
            # Inverter para ordem cronologica
            self.dados_posicionais.reverse()
            
            self.ultimo_concurso = self.dados_posicionais[-1] if self.dados_posicionais else None
            
            print(f"   [OK] {len(self.dados_posicionais)} concursos carregados")
            if self.ultimo_concurso:
                print(f"   [->] Ultimo: {self.ultimo_concurso['concurso']}")
            
            return True
            
        except Exception as e:
            print(f"   [ERRO] {e}")
            return False
    
    def carregar_dados_trios(self) -> bool:
        """Carrega dados da view CONTA_TRIOS_LOTO"""
        print("[TRIOS] Carregando dados de trios...")
        
        # Limpar dados anteriores para evitar duplicação
        self.dados_trios = []
        
        try:
            # Colunas reais: num1, num2, num3, quantidade, UltimoConcurso
            query = """
            SELECT num1, num2, num3, quantidade, UltimoConcurso
            FROM dbo.CONTA_TRIOS_LOTO
            ORDER BY quantidade DESC
            """
            
            resultados = self.db_config.execute_query(query)
            
            if resultados is None:
                print("   [!] Query retornou None")
                return False
            
            ultimo_concurso_geral = self.ultimo_concurso['concurso'] if self.ultimo_concurso else 3575
            
            for row in resultados:
                num1, num2, num3 = row[0], row[1], row[2]
                quantidade = row[3]
                ultimo_conc = row[4] if row[4] else 0
                atraso = ultimo_concurso_geral - ultimo_conc
                
                # Formar string do trio no formato padronizado
                trio = f"{num1:02d}-{num2:02d}-{num3:02d}"
                
                self.dados_trios.append({
                    'trio': trio,
                    'frequencia': quantidade,
                    'ultimo_concurso': ultimo_conc,
                    'atraso': atraso
                })
            
            print(f"   [OK] {len(self.dados_trios)} trios carregados")
            
            return True
            
        except Exception as e:
            print(f"   [ERRO] {e}")
            return False
    
    def carregar_dados_quinas(self) -> bool:
        """
        Carrega dados de quinas calculando em Python.
        C(25,5) = 53.130 quinas possiveis, mas calculamos apenas as que aparecem.
        """
        print("[QUINAS] Carregando dados de quinas...")
        
        try:
            from itertools import combinations
            
            if not self.dados_posicionais:
                print("   [!] Dados posicionais nao carregados")
                return False
            
            ultimo_concurso_geral = self.ultimo_concurso['concurso'] if self.ultimo_concurso else 3575
            
            # Contar quinas em Python
            quinas_count = Counter()
            quinas_ultimo = {}  # Ultimo concurso em que cada quina apareceu
            
            for d in self.dados_posicionais:
                numeros = sorted(d['numeros'])
                concurso = d['concurso']
                
                # Gerar todas as quinas (C(15,5) = 3003 por concurso)
                for quina in combinations(numeros, 5):
                    quina_str = "-".join(f"{n:02d}" for n in quina)
                    quinas_count[quina_str] += 1
                    quinas_ultimo[quina_str] = concurso
            
            # Converter para lista ordenada por frequencia
            for quina_str, freq in quinas_count.most_common():
                ultimo_conc = quinas_ultimo.get(quina_str, 0)
                atraso = ultimo_concurso_geral - ultimo_conc
                
                self.dados_quinas.append({
                    'quina': quina_str,
                    'frequencia': freq,
                    'ultimo_concurso': ultimo_conc,
                    'atraso': atraso
                })
            
            print(f"   [OK] {len(self.dados_quinas)} quinas calculadas")
            
            return True
            
        except Exception as e:
            print(f"   [ERRO] {e}")
            return False
    
    def carregar_dados_combinacoes(self, tamanho: int, top_n: int = 5000) -> bool:
        """
        Carrega dados de combinacoes de qualquer tamanho.
        
        Args:
            tamanho: Tamanho da combinacao (2=duplas, 3=trios, ..., 11=undecetos)
            top_n: Limite de combinacoes mais frequentes a manter
        
        Returns:
            bool: True se carregou com sucesso
        """
        from itertools import combinations
        from math import comb
        
        nome = self.NOMES_COMBINACOES.get(tamanho, f"Combinacoes-{tamanho}")
        print(f"\n[{nome.upper()}] Carregando dados de {nome.lower()}...")
        
        try:
            if not self.dados_posicionais:
                print(f"   [!] Dados posicionais nao carregados")
                return False
            
            ultimo_concurso_geral = self.ultimo_concurso['concurso'] if self.ultimo_concurso else 3575
            
            # Calcular quantidade teorica por concurso
            combos_por_concurso = comb(15, tamanho)
            print(f"   [INFO] C(15,{tamanho}) = {combos_por_concurso:,} combinacoes por concurso")
            
            # Contar combinacoes em Python
            combos_count = Counter()
            combos_ultimo = {}  # Ultimo concurso em que cada combo apareceu
            
            total_concursos = len(self.dados_posicionais)
            
            for i, d in enumerate(self.dados_posicionais):
                numeros = sorted(d['numeros'])
                concurso = d['concurso']
                
                # Gerar todas as combinacoes do tamanho especificado
                for combo in combinations(numeros, tamanho):
                    combo_str = "-".join(f"{n:02d}" for n in combo)
                    combos_count[combo_str] += 1
                    combos_ultimo[combo_str] = concurso
                
                # Mostrar progresso a cada 100 concursos
                if (i + 1) % 100 == 0:
                    print(f"   [PROG] {i+1}/{total_concursos} concursos processados...")
            
            # Converter para lista ordenada por frequencia (top_n)
            dados_tamanho = []
            for combo_str, freq in combos_count.most_common(top_n):
                ultimo_conc = combos_ultimo.get(combo_str, 0)
                atraso = ultimo_concurso_geral - ultimo_conc
                
                dados_tamanho.append({
                    'combo': combo_str,
                    'frequencia': freq,
                    'ultimo_concurso': ultimo_conc,
                    'atraso': atraso
                })
            
            self.dados_combinacoes[tamanho] = dados_tamanho
            
            print(f"   [OK] {len(dados_tamanho):,} {nome.lower()} calculadas (top {top_n})")
            print(f"   [TOP] Mais frequente: {dados_tamanho[0]['combo']} ({dados_tamanho[0]['frequencia']}x)")
            
            return True
            
        except Exception as e:
            print(f"   [ERRO] {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def identificar_combinacoes_em_divida(self, tamanho: int, freq_min: int = None, desvio_min_pct: float = 20.0) -> List[Dict]:
        """
        Identifica combinacoes em "divida" REAL.
        
        LOGICA CORRETA:
        - Intervalo Medio = Total de Concursos / Frequencia
        - Desvio = Atraso Atual - Intervalo Medio
        - Se Desvio > 0 e acima de X% = EM DIVIDA
        
        Args:
            tamanho: Tamanho da combinacao
            freq_min: Frequencia minima (auto-calculado se None)
            desvio_min_pct: Percentual minimo de desvio para considerar em divida (default 20%)
        
        Returns:
            Lista de combinacoes em divida
        """
        nome = self.NOMES_COMBINACOES.get(tamanho, f"Combinacoes-{tamanho}")
        
        if tamanho not in self.dados_combinacoes or not self.dados_combinacoes[tamanho]:
            print(f"   [!] Dados de {nome.lower()} nao carregados")
            return []
        
        dados = self.dados_combinacoes[tamanho]
        # CORRECAO: Usar numero do ultimo concurso (total real) ao inves de len(dados_posicionais)
        total_concursos = self.ultimo_concurso['concurso'] if self.ultimo_concurso else 3575
        
        # Auto-calcular freq_min se nao fornecido
        if freq_min is None:
            # Minimo de 3 aparicoes para ter significancia estatistica
            freq_min = 3
        
        print(f"\n[DIVIDA-{tamanho}] Identificando {nome.lower()} em divida REAL...")
        print(f"   [PARAMS] freq >= {freq_min}, desvio >= {desvio_min_pct:.0f}% acima da media")
        print(f"   [BASE] Total de concursos analisados: {total_concursos}")
        
        # Calcular metricas corretas para cada combinacao
        em_divida = []
        
        for d in dados:
            freq = d['frequencia']
            atraso = d['atraso']
            
            if freq < freq_min:
                continue
            
            # CALCULO CORRETO
            intervalo_medio = total_concursos / freq
            desvio = atraso - intervalo_medio
            desvio_pct = (desvio / intervalo_medio) * 100 if intervalo_medio > 0 else 0
            
            # So considera em divida se atraso > intervalo medio (desvio positivo)
            if desvio > 0 and desvio_pct >= desvio_min_pct:
                em_divida.append({
                    'combo': d['combo'],
                    'frequencia': freq,
                    'atraso': atraso,
                    'ultimo_concurso': d.get('ultimo_concurso', 0),
                    'intervalo_medio': round(intervalo_medio, 1),
                    'desvio': round(desvio, 1),
                    'desvio_pct': round(desvio_pct, 1)
                })
        
        # Ordenar por desvio percentual (quanto mais acima da media, mais em divida)
        em_divida.sort(key=lambda x: x['desvio_pct'], reverse=True)
        
        self.combinacoes_em_divida[tamanho] = em_divida
        
        print(f"   [OK] {len(em_divida)} {nome.lower()} em divida REAL encontradas")
        
        return em_divida
    
    def identificar_pivos_por_tamanho(self, tamanho: int, top_n: int = 100) -> Set[int]:
        """
        Identifica numeros pivo: aparecem em muitas combinacoes frequentes.
        
        Args:
            tamanho: Tamanho da combinacao
            top_n: Quantidade de combinacoes top a considerar
        
        Returns:
            Set de numeros pivo
        """
        nome = self.NOMES_COMBINACOES.get(tamanho, f"Combinacoes-{tamanho}")
        
        if tamanho not in self.dados_combinacoes or not self.dados_combinacoes[tamanho]:
            return set()
        
        dados = self.dados_combinacoes[tamanho][:top_n]
        
        # Contar frequencia de cada numero nos top combinacoes
        contador_numeros = Counter()
        
        for d in dados:
            try:
                numeros = [int(n) for n in d['combo'].split('-')]
                for num in numeros:
                    contador_numeros[num] += 1
            except:
                continue
        
        # Identificar pivos (aparecem em mais de 30% dos top)
        threshold = top_n * 0.3
        pivos = {num for num, count in contador_numeros.items() if count >= threshold}
        
        self.numeros_pivo_por_tamanho[tamanho] = pivos
        
        return pivos
    
    def mostrar_resumo_combinacoes(self, tamanho: int, top_n: int = 15):
        """Mostra resumo das combinacoes em divida para um tamanho"""
        nome = self.NOMES_COMBINACOES.get(tamanho, f"Combinacoes-{tamanho}")
        
        if tamanho not in self.combinacoes_em_divida:
            print(f"   [!] Nenhuma {nome.lower()} em divida identificada")
            return
        
        em_divida = self.combinacoes_em_divida[tamanho][:top_n]
        
        if not em_divida:
            print(f"   [!] Nenhuma {nome.lower()} em divida")
            return
        
        print(f"\n{'=' * 85}")
        print(f"[{nome.upper()}] TOP {min(top_n, len(em_divida))} {nome.upper()} EM DIVIDA REAL")
        print(f"{'=' * 85}")
        print(f"   {'Combo':<35} {'Freq':>5} {'Int.Med':>8} {'Atraso':>7} {'Desvio':>8} {'%Acima':>8}")
        print(f"   {'-'*35} {'-'*5} {'-'*8} {'-'*7} {'-'*8} {'-'*8}")
        
        for i, d in enumerate(em_divida, 1):
            # Status visual baseado no desvio
            desvio_pct = d.get('desvio_pct', 0)
            if desvio_pct >= 100:
                status = "🔴"  # Muito atrasada (2x+ a media)
            elif desvio_pct >= 50:
                status = "🟠"  # Bastante atrasada
            else:
                status = "🟡"  # Moderadamente atrasada
            
            print(f"   {d['combo']:<35} {d['frequencia']:>5} {d['intervalo_medio']:>8.1f} "
                  f"{d['atraso']:>7} {d['desvio']:>+8.1f} {desvio_pct:>7.1f}% {status}")
        
        print(f"\n   📊 LEGENDA:")
        print(f"      • Int.Med = Intervalo Medio (a cada quantos concursos costuma sair)")
        print(f"      • Desvio = Atraso - Int.Med (quanto esta acima/abaixo da media)")
        print(f"      • %Acima = Percentual acima da media (quanto maior, mais em divida)")
        print(f"      • 🔴 = 100%+ acima | 🟠 = 50-100% acima | 🟡 = 20-50% acima")
        
        # Mostrar numeros mais frequentes nas combinacoes em divida
        contador = Counter()
        for d in em_divida:
            try:
                numeros = [int(n) for n in d['combo'].split('-')]
                for num in numeros:
                    contador[num] += 1
            except:
                continue
        
        print(f"\n   [NUM] Numeros mais presentes nas {nome.lower()} em divida:")
        for num, count in contador.most_common(10):
            print(f"      {num:02d}: {count} {nome.lower()}")
    
    def executar_analise_tamanho(self, tamanho: int, top_n_carregar: int = 3000, 
                                  freq_min: int = None, desvio_min_pct: float = 20.0):
        """
        Executa analise completa para um tamanho de combinacao.
        
        Args:
            tamanho: Tamanho da combinacao
            top_n_carregar: Quantidade de combinacoes a carregar
            freq_min: Frequencia minima para divida
            desvio_min_pct: Percentual minimo de desvio para considerar em divida
        """
        nome = self.NOMES_COMBINACOES.get(tamanho, f"Combinacoes-{tamanho}")
        
        print(f"\n{'='*70}")
        print(f"[ANALISE] {nome.upper()} (tamanho {tamanho})")
        print(f"{'='*70}")
        
        # 1. Carregar dados
        if not self.carregar_dados_combinacoes(tamanho, top_n=top_n_carregar):
            return
        
        # 2. Identificar em divida (com nova logica)
        self.identificar_combinacoes_em_divida(tamanho, freq_min, desvio_min_pct)
        
        # 3. Identificar pivos
        pivos = self.identificar_pivos_por_tamanho(tamanho)
        if pivos:
            print(f"   [PIVO] Numeros pivo de {nome.lower()}: {sorted(pivos)}")
        
        # 4. Mostrar resumo
        self.mostrar_resumo_combinacoes(tamanho)

    def calcular_probabilidades_por_posicao(self):
        """Calcula probabilidades historicas para cada posicao N1-N15"""
        print("\n[PROB] Calculando probabilidades por posicao...")
        
        for pos in range(1, 16):
            col = f'N{pos}'
            
            valores = [d[col] for d in self.dados_posicionais if d.get(col)]
            
            if valores:
                contador = Counter(valores)
                total = len(valores)
                
                # Calcular probabilidades
                probs = {}
                for num, freq in contador.items():
                    probs[num] = freq / total
                
                # Ordenar por probabilidade
                probs_ordenadas = sorted(probs.items(), key=lambda x: x[1], reverse=True)
                
                self.probs_por_posicao[pos] = probs_ordenadas
        
        print(f"   [OK] Probabilidades calculadas para 15 posicoes")
    
    def identificar_encalhados_por_posicao(self, limite: int = 10):
        """Identifica numeros encalhados (nao saem ha X concursos) por posicao"""
        print(f"\n[ICE] Identificando numeros encalhados (>{limite} concursos)...")
        
        ultimo_conc = self.ultimo_concurso['concurso']
        
        for pos in range(1, 16):
            col = f'N{pos}'
            
            # Pegar ultimas aparicoes de cada numero nesta posicao
            ultima_aparicao = {}
            
            for d in self.dados_posicionais:
                num = d.get(col)
                if num:
                    ultima_aparicao[num] = d['concurso']
            
            # Identificar encalhados
            encalhados = []
            for num, ultimo in ultima_aparicao.items():
                atraso = ultimo_conc - ultimo
                if atraso >= limite:
                    encalhados.append((num, atraso))
            
            # Ordenar por atraso (maior primeiro)
            encalhados.sort(key=lambda x: x[1], reverse=True)
            
            self.numeros_encalhados[pos] = encalhados
        
        # Resumo
        total_encalhados = sum(len(e) for e in self.numeros_encalhados.values())
        print(f"   [OK] {total_encalhados} numeros encalhados encontrados")
    
    def identificar_trios_em_divida(self, freq_min: int = 10, desvio_min_pct: float = 20.0):
        """
        Identifica trios em DIVIDA REAL usando logica correta:
        - Intervalo Medio = Total de Concursos / Frequencia
        - Desvio = Atraso Atual - Intervalo Medio
        - Se Desvio > X% da media = EM DIVIDA
        
        Args:
            freq_min: Frequencia minima para considerar (default 10)
            desvio_min_pct: Percentual minimo acima da media (default 20%)
        """
        print(f"\n[DIVIDA-TRIO] Identificando trios em DIVIDA REAL (freq>={freq_min}, desvio>={desvio_min_pct}%)...")
        
        # CORRECAO: Usar numero do ultimo concurso (total real) ao inves de len(dados_posicionais)
        total_concursos = self.ultimo_concurso['concurso'] if self.ultimo_concurso else 3575
        
        self.trios_em_divida = []  # Limpar lista anterior
        
        for trio_data in self.dados_trios:
            freq = trio_data['frequencia']
            atraso = trio_data['atraso']
            
            if freq < freq_min:
                continue
            
            # CALCULO CORRETO
            intervalo_medio = total_concursos / freq
            desvio = atraso - intervalo_medio
            desvio_pct = (desvio / intervalo_medio) * 100 if intervalo_medio > 0 else 0
            
            # So considera em divida se atraso > intervalo medio
            if desvio > 0 and desvio_pct >= desvio_min_pct:
                self.trios_em_divida.append({
                    'trio': trio_data['trio'],
                    'frequencia': freq,
                    'atraso': atraso,
                    'ultimo_concurso': trio_data.get('ultimo_concurso', 0),
                    'intervalo_medio': round(intervalo_medio, 1),
                    'desvio': round(desvio, 1),
                    'desvio_pct': round(desvio_pct, 1)
                })
        
        # Ordenar por desvio percentual (quanto mais acima da media, mais em divida)
        self.trios_em_divida.sort(key=lambda x: x['desvio_pct'], reverse=True)
        
        print(f"   [BASE] Total concursos: {total_concursos}")
        print(f"   [OK] {len(self.trios_em_divida)} trios em divida REAL encontrados")
    
    def identificar_numeros_pivo(self, top_n: int = 200):
        """
        Identifica numeros pivo: aparecem em muitos trios frequentes
        Esses numeros "conectam" trios de alta frequencia
        """
        print(f"\n[PIVO] Identificando numeros PIVO (top {top_n} trios)...")
        
        # Pegar top N trios por frequencia
        top_trios = self.dados_trios[:top_n]
        
        # Contar aparicoes de cada numero
        contador_numeros = Counter()
        
        for trio_data in top_trios:
            trio = trio_data['trio']
            # Parse do trio (formato "01-02-03" ou "1-2-3")
            try:
                if isinstance(trio, str):
                    partes = trio.replace(' ', '').split('-')
                    numeros = [int(p) for p in partes]
                    for num in numeros:
                        contador_numeros[num] += 1
            except:
                continue
        
        # Top 10 numeros mais conectados
        top_pivos = contador_numeros.most_common(10)
        
        for num, contagem in top_pivos:
            self.numeros_pivo.add(num)
        
        print(f"   [OK] Numeros pivo: {sorted(self.numeros_pivo)}")
        print(f"   [->] Conexoes: {dict(top_pivos)}")
    
    def identificar_quinas_em_divida(self, freq_min: int = 5, desvio_min_pct: float = 20.0):
        """
        Identifica quinas em DIVIDA REAL usando logica correta:
        - Intervalo Medio = Total de Concursos / Frequencia
        - Desvio = Atraso Atual - Intervalo Medio
        - Se Desvio > X% da media = EM DIVIDA
        
        Args:
            freq_min: Frequencia minima para considerar (default 5)
            desvio_min_pct: Percentual minimo acima da media (default 20%)
        """
        print(f"\n[DIVIDA-QUINA] Identificando quinas em DIVIDA REAL (freq>={freq_min}, desvio>={desvio_min_pct}%)...")
        
        # CORRECAO: Usar numero do ultimo concurso (total real) ao inves de len(dados_posicionais)
        total_concursos = self.ultimo_concurso['concurso'] if self.ultimo_concurso else 3575
        
        self.quinas_em_divida = []  # Limpar lista anterior
        
        for quina_data in self.dados_quinas:
            freq = quina_data['frequencia']
            atraso = quina_data['atraso']
            
            if freq < freq_min:
                continue
            
            # CALCULO CORRETO
            intervalo_medio = total_concursos / freq
            desvio = atraso - intervalo_medio
            desvio_pct = (desvio / intervalo_medio) * 100 if intervalo_medio > 0 else 0
            
            # So considera em divida se atraso > intervalo medio
            if desvio > 0 and desvio_pct >= desvio_min_pct:
                self.quinas_em_divida.append({
                    'quina': quina_data['quina'],
                    'frequencia': freq,
                    'atraso': atraso,
                    'ultimo_concurso': quina_data.get('ultimo_concurso', 0),
                    'intervalo_medio': round(intervalo_medio, 1),
                    'desvio': round(desvio, 1),
                    'desvio_pct': round(desvio_pct, 1)
                })
        
        # Ordenar por desvio percentual (quanto mais acima da media, mais em divida)
        self.quinas_em_divida.sort(key=lambda x: x['desvio_pct'], reverse=True)
        
        print(f"   [BASE] Total concursos: {total_concursos}")
        print(f"   [OK] {len(self.quinas_em_divida)} quinas em divida REAL encontradas")
    
    def identificar_numeros_pivo_quinas(self, top_n: int = 100):
        """
        Identifica numeros pivo das quinas: aparecem em muitas quinas frequentes
        Esses numeros "conectam" quinas de alta frequencia
        """
        print(f"\n[PIVO-QUINA] Identificando numeros PIVO de quinas (top {top_n})...")
        
        # Pegar top N quinas por frequencia
        top_quinas = self.dados_quinas[:top_n]
        
        # Contar aparicoes de cada numero
        contador_numeros = Counter()
        
        for quina_data in top_quinas:
            quina = quina_data['quina']
            try:
                if isinstance(quina, str):
                    partes = quina.replace(' ', '').split('-')
                    numeros = [int(p) for p in partes]
                    for num in numeros:
                        contador_numeros[num] += 1
            except:
                continue
        
        # Top 10 numeros mais conectados
        top_pivos = contador_numeros.most_common(10)
        
        for num, contagem in top_pivos:
            self.numeros_pivo_quinas.add(num)
        
        print(f"   [OK] Numeros pivo quinas: {sorted(self.numeros_pivo_quinas)}")
        print(f"   [->] Conexoes: {dict(top_pivos)}")
    
    def analisar_momentum_quinas(self, ultimos_n: int = 20):
        """
        Analisa momentum de quinas: quinas que estao "quentes" recentemente
        Compara frequencia nos ultimos N concursos vs media historica
        """
        print(f"\n[MOMENTUM-QUINA] Analisando MOMENTUM de quinas (ultimos {ultimos_n} concursos)...")
        
        if len(self.dados_posicionais) < ultimos_n:
            print("   [!] Dados insuficientes")
            return []
        
        from itertools import combinations
        
        # Extrair quinas dos ultimos N concursos
        quinas_recentes = Counter()
        
        for d in self.dados_posicionais[-ultimos_n:]:
            numeros = sorted(d['numeros'])
            # Gerar todas as quinas
            for quina in combinations(numeros, 5):
                quina_str = "-".join(f"{n:02d}" for n in quina)
                quinas_recentes[quina_str] += 1
        
        # Comparar com frequencia historica
        momentum_list = []
        
        for quina, freq_recente in quinas_recentes.most_common(50):
            # Buscar frequencia historica
            freq_historica = 0
            for q in self.dados_quinas:
                if q['quina'] == quina:
                    freq_historica = q['frequencia']
                    break
            
            if freq_historica > 0:
                # Calcular momentum
                media_esperada = freq_historica / len(self.dados_posicionais) * ultimos_n
                momentum = freq_recente / max(media_esperada, 0.1)
                
                if momentum > 1.5:  # 50% acima do esperado
                    momentum_list.append({
                        'quina': quina,
                        'freq_recente': freq_recente,
                        'freq_historica': freq_historica,
                        'momentum': round(momentum, 2)
                    })
        
        momentum_list.sort(key=lambda x: x['momentum'], reverse=True)
        
        print(f"   [OK] {len(momentum_list)} quinas com momentum alto")
        
        return momentum_list[:20]  # Top 20
    
    def mostrar_resumo_quinas_divida(self, top_n: int = 20):
        """Mostra quinas em divida REAL (candidatos a sair)"""
        print("\n" + "=" * 85)
        print("[QUINA-DIVIDA] TOP QUINAS EM DIVIDA REAL (candidatos a sair)")
        print("=" * 85)
        print(f"   {'Quina':<20} {'Freq':>5} {'Int.Med':>8} {'Atraso':>7} {'Desvio':>8} {'%Acima':>8}")
        print(f"   {'-'*20} {'-'*5} {'-'*8} {'-'*7} {'-'*8} {'-'*8}")
        
        for i, q in enumerate(self.quinas_em_divida[:top_n], 1):
            desvio_pct = q.get('desvio_pct', 0)
            if desvio_pct >= 100:
                status = "🔴"
            elif desvio_pct >= 50:
                status = "🟠"
            else:
                status = "🟡"
            
            print(f"   {q['quina']:<20} {q['frequencia']:>5} {q['intervalo_medio']:>8.1f} "
                  f"{q['atraso']:>7} {q['desvio']:>+8.1f} {desvio_pct:>7.1f}% {status}")
        
        print(f"\n   📊 LEGENDA:")
        print(f"      • Int.Med = Intervalo Medio (a cada quantos concursos costuma sair)")
        print(f"      • Desvio = Atraso - Int.Med (quanto esta acima da media)")
        print(f"      • %Acima = Percentual acima da media")
        print(f"      • 🔴 = 100%+ | 🟠 = 50-100% | 🟡 = 20-50%")
        
        # Extrair numeros das quinas em divida
        numeros_divida = Counter()
        for q in self.quinas_em_divida[:top_n]:
            quina = q['quina']
            try:
                partes = quina.replace(' ', '').split('-')
                for p in partes:
                    numeros_divida[int(p)] += 1
            except:
                continue
        
        print(f"\n   [NUM] Numeros mais presentes nas quinas em divida:")
        for num, count in numeros_divida.most_common(10):
            print(f"      {num:02d}: {count} quinas")
    
    def validar_super_pivos_historico(self, super_pivos: list):
        """
        Valida quantas vezes os super pivos apareceram JUNTOS no historico.
        Mostra analise progressiva: 2 numeros, 3 numeros, etc.
        """
        print("\n" + "=" * 70)
        print("[VALIDACAO] ANALISE HISTORICA DOS SUPER PIVOS")
        print("=" * 70)
        print(f"   Super Pivos identificados: {super_pivos}")
        print(f"   Total de concursos analisados: {len(self.dados_posicionais)}")
        print()
        
        if len(super_pivos) < 2:
            print("   [!] Menos de 2 super pivos - analise nao aplicavel")
            return
        
        from itertools import combinations
        
        # Converter concursos para sets para busca rapida
        concursos_sets = []
        for d in self.dados_posicionais:
            concursos_sets.append({
                'concurso': d['concurso'],
                'numeros': set(d['numeros'])
            })
        
        # Analisar combinacoes progressivas: duplas, trios, quartetos, etc.
        print("   📊 FREQUENCIA DE APARICAO CONJUNTA:")
        print("-" * 60)
        
        resultados = []
        
        for tamanho in range(2, len(super_pivos) + 1):
            for combo in combinations(super_pivos, tamanho):
                combo_set = set(combo)
                
                # Contar quantas vezes essa combinacao apareceu
                ocorrencias = []
                for conc in concursos_sets:
                    if combo_set.issubset(conc['numeros']):
                        ocorrencias.append(conc['concurso'])
                
                count = len(ocorrencias)
                pct = (count / len(self.dados_posicionais)) * 100
                
                # Calcular ultimo concurso e atraso
                if ocorrencias:
                    ultimo = max(ocorrencias)
                    atraso = self.ultimo_concurso['concurso'] - ultimo if self.ultimo_concurso else 0
                    
                    # Calcular intervalo medio
                    ocorrencias_ord = sorted(ocorrencias)
                    if len(ocorrencias_ord) >= 2:
                        intervalos = [ocorrencias_ord[i] - ocorrencias_ord[i-1] for i in range(1, len(ocorrencias_ord))]
                        intervalo_medio = sum(intervalos) / len(intervalos)
                    else:
                        intervalo_medio = 0
                else:
                    ultimo = 0
                    atraso = 999
                    intervalo_medio = 0
                
                combo_str = "-".join(f"{n:02d}" for n in combo)
                
                resultados.append({
                    'combo': combo_str,
                    'tamanho': tamanho,
                    'count': count,
                    'pct': pct,
                    'ultimo': ultimo,
                    'atraso': atraso,
                    'intervalo_medio': intervalo_medio
                })
        
        # Mostrar resultados agrupados por tamanho
        for tamanho in range(2, len(super_pivos) + 1):
            combos_tamanho = [r for r in resultados if r['tamanho'] == tamanho]
            if not combos_tamanho:
                continue
                
            print(f"\n   🔢 COMBINACOES DE {tamanho} NUMEROS:")
            
            # Ordenar por frequencia
            combos_tamanho.sort(key=lambda x: x['count'], reverse=True)
            
            for r in combos_tamanho[:10]:  # Top 10 por tamanho
                # Status baseado em comparacao com intervalo medio
                status = ""
                if r['intervalo_medio'] > 0:
                    diferenca = r['atraso'] - r['intervalo_medio']
                    if diferenca >= r['intervalo_medio'] * 0.5:  # 50% acima da media
                        status = " 🔴 MUITO ATRASADO!"
                    elif diferenca > 0:
                        status = " 🟠 Atrasado"
                    elif r['atraso'] <= 3:
                        status = " 🟢 Quente"
                else:
                    if r['atraso'] >= 20:
                        status = " 🔴"
                    elif r['atraso'] <= 3:
                        status = " 🟢"
                
                # Mostrar intervalo medio na saida
                int_med_str = f"(media: {r['intervalo_medio']:.0f})" if r['intervalo_medio'] > 0 else ""
                
                print(f"      {r['combo']}: {r['count']:4} vezes ({r['pct']:5.2f}%) | "
                      f"Atraso: {r['atraso']:3} {int_med_str}{status}")
        
        # TODOS os super pivos juntos
        if len(super_pivos) >= 3:
            todos_set = set(super_pivos)
            ocorrencias_todos = []
            for conc in concursos_sets:
                if todos_set.issubset(conc['numeros']):
                    ocorrencias_todos.append(conc['concurso'])
            
            count_todos = len(ocorrencias_todos)
            pct_todos = (count_todos / len(self.dados_posicionais)) * 100
            
            print("\n" + "=" * 60)
            print(f"   ⭐ TODOS OS {len(super_pivos)} SUPER PIVOS JUNTOS:")
            print(f"      {'-'.join(f'{n:02d}' for n in super_pivos)}")
            print(f"      Apareceram JUNTOS: {count_todos} vezes ({pct_todos:.2f}%)")
            
            if ocorrencias_todos and count_todos >= 2:
                ultimo_todos = max(ocorrencias_todos)
                primeiro_todos = min(ocorrencias_todos)
                atraso_todos = self.ultimo_concurso['concurso'] - ultimo_todos if self.ultimo_concurso else 0
                
                # CALCULAR INTERVALOS ENTRE APARICOES
                ocorrencias_ordenadas = sorted(ocorrencias_todos)
                intervalos = []
                for i in range(1, len(ocorrencias_ordenadas)):
                    intervalo = ocorrencias_ordenadas[i] - ocorrencias_ordenadas[i-1]
                    intervalos.append(intervalo)
                
                # Estatisticas dos intervalos
                if intervalos:
                    intervalo_medio = sum(intervalos) / len(intervalos)
                    intervalo_min = min(intervalos)
                    intervalo_max = max(intervalos)
                    
                    # Desvio padrao
                    variancia = sum((x - intervalo_medio) ** 2 for x in intervalos) / len(intervalos)
                    desvio_padrao = variancia ** 0.5
                    
                    # Mediana
                    intervalos_sorted = sorted(intervalos)
                    meio = len(intervalos_sorted) // 2
                    if len(intervalos_sorted) % 2 == 0:
                        mediana = (intervalos_sorted[meio-1] + intervalos_sorted[meio]) / 2
                    else:
                        mediana = intervalos_sorted[meio]
                    
                    # Quantos desvios padrao o atraso atual esta da media?
                    if desvio_padrao > 0:
                        z_score = (atraso_todos - intervalo_medio) / desvio_padrao
                    else:
                        z_score = 0
                    
                    print(f"\n      📊 ANALISE DE INTERVALOS:")
                    print(f"         Intervalo MEDIO: {intervalo_medio:.1f} concursos")
                    print(f"         Intervalo MEDIANO: {mediana:.1f} concursos")
                    print(f"         Intervalo MIN: {intervalo_min} | MAX: {intervalo_max}")
                    print(f"         Desvio Padrao: {desvio_padrao:.1f}")
                    
                    print(f"\n      📈 COMPARACAO COM ATRASO ATUAL:")
                    print(f"         Atraso atual: {atraso_todos} concursos")
                    print(f"         Media esperada: {intervalo_medio:.1f} concursos")
                    diferenca = atraso_todos - intervalo_medio
                    
                    if diferenca > 0:
                        print(f"         Diferenca: +{diferenca:.1f} concursos ACIMA da media")
                    else:
                        print(f"         Diferenca: {diferenca:.1f} concursos ABAIXO da media")
                    
                    print(f"         Z-Score: {z_score:.2f} desvios padrao")
                    
                    # Interpretacao estatistica
                    print(f"\n      🎯 INTERPRETACAO:")
                    if z_score >= 2.0:
                        print(f"         🔴 MUITO ATRASADO! Atraso extremo (>2 desvios)")
                        print(f"         📍 Probabilidade alta de aparecer em breve!")
                    elif z_score >= 1.0:
                        print(f"         🟠 ATRASADO! Acima de 1 desvio padrao")
                        print(f"         📍 Bom candidato para proximos sorteios")
                    elif z_score >= 0:
                        print(f"         🟡 NORMAL. Dentro da media esperada")
                    else:
                        print(f"         🟢 RECENTE. Abaixo da media esperada")
                    
                    # Mostrar historico de intervalos
                    print(f"\n      📅 HISTORICO DE INTERVALOS (do mais recente ao mais antigo):")
                    for i, intervalo in enumerate(reversed(intervalos[-10:])):  # Ultimos 10
                        idx = len(intervalos) - i
                        status_int = ""
                        if intervalo >= intervalo_medio + desvio_padrao:
                            status_int = " 🔴"
                        elif intervalo <= intervalo_medio - desvio_padrao:
                            status_int = " 🟢"
                        print(f"         Intervalo {idx}: {intervalo} concursos{status_int}")
                
                print(f"\n      📅 ULTIMAS APARICOES:")
                for conc in sorted(ocorrencias_todos, reverse=True)[:5]:
                    # Buscar data se disponivel
                    for d in self.dados_posicionais:
                        if d['concurso'] == conc:
                            data_str = d.get('data', 'N/A')
                            print(f"         Concurso {conc}: {data_str}")
                            break
            
            elif ocorrencias_todos and count_todos == 1:
                print(f"      ⚠️ Apareceu apenas 1 vez - insuficiente para analise de intervalos")
            else:
                print(f"      ⚠️ Nunca apareceram todos juntos no historico!")
        
        print("=" * 60)
        
        # ===================================================================
        # ANÁLISE COMPLEMENTAR: COMBINAÇÕES SUPER AQUECIDAS (MOMENTUM ALTO)
        # ===================================================================
        self._analisar_momentum_super_pivos(super_pivos, resultados, concursos_sets)
    
    def _analisar_momentum_super_pivos(self, super_pivos: list, resultados: list, concursos_sets: list):
        """
        Análise complementar: identifica combinações que estão com MOMENTUM ALTO.
        Ou seja, estão aparecendo MUITO MAIS do que a média histórica sugere.
        
        Exemplo: combinação que deveria sair 1x a cada 50 concursos,
        mas nos últimos 50 concursos já saiu 5 vezes = 5x acima da média!
        """
        from itertools import combinations
        
        print("\n" + "=" * 70)
        print("🔥 ANÁLISE COMPLEMENTAR: COMBINAÇÕES SUPER AQUECIDAS")
        print("=" * 70)
        print("   Combinações que estão aparecendo MUITO MAIS que o esperado!")
        print("   (Frequência recente >> Frequência histórica)")
        print()
        
        total_concursos = len(self.dados_posicionais)
        ultimos_n = 50  # Analisar últimos 50 concursos
        
        if total_concursos < ultimos_n:
            print(f"   [!] Dados insuficientes (< {ultimos_n} concursos)")
            return
        
        # Pegar os últimos N concursos
        concursos_recentes = concursos_sets[-ultimos_n:]
        
        momentum_por_tamanho = {}
        
        for tamanho in range(2, len(super_pivos) + 1):
            combos_momentum = []
            
            for combo in combinations(super_pivos, tamanho):
                combo_set = set(combo)
                combo_str = "-".join(f"{n:02d}" for n in combo)
                
                # Contar frequência TOTAL (histórico completo)
                freq_total = 0
                for conc in concursos_sets:
                    if combo_set.issubset(conc['numeros']):
                        freq_total += 1
                
                # Contar frequência RECENTE (últimos N concursos)
                freq_recente = 0
                for conc in concursos_recentes:
                    if combo_set.issubset(conc['numeros']):
                        freq_recente += 1
                
                if freq_total == 0:
                    continue
                
                # Calcular métricas de momentum
                # Frequência esperada nos últimos N = (freq_total / total_concursos) * ultimos_n
                freq_esperada = (freq_total / total_concursos) * ultimos_n
                
                # Razão de momentum = freq_recente / freq_esperada
                if freq_esperada > 0:
                    momentum_ratio = freq_recente / freq_esperada
                else:
                    momentum_ratio = 0
                
                # Só incluir se tem momentum significativo (pelo menos 1.5x acima do esperado)
                if momentum_ratio >= 1.5 and freq_recente >= 2:
                    combos_momentum.append({
                        'combo': combo_str,
                        'freq_total': freq_total,
                        'freq_recente': freq_recente,
                        'freq_esperada': round(freq_esperada, 2),
                        'momentum_ratio': round(momentum_ratio, 2),
                        'excesso': freq_recente - freq_esperada
                    })
            
            if combos_momentum:
                # Ordenar por momentum ratio
                combos_momentum.sort(key=lambda x: x['momentum_ratio'], reverse=True)
                momentum_por_tamanho[tamanho] = combos_momentum
        
        # Exibir resultados
        if not momentum_por_tamanho:
            print("   [!] Nenhuma combinação com momentum significativo encontrada")
            print("       (nenhuma está 1.5x+ acima do esperado nos últimos 50 concursos)")
            return
        
        print(f"   📊 COMBINAÇÕES COM MOMENTUM ALTO (últimos {ultimos_n} concursos):")
        print(f"   {'='*65}")
        
        for tamanho in sorted(momentum_por_tamanho.keys()):
            combos = momentum_por_tamanho[tamanho]
            
            print(f"\n   🔥 COMBINAÇÕES DE {tamanho} NÚMEROS (aquecidas):")
            print(f"      {'Combo':<25} {'Total':>6} {'Recente':>8} {'Esperado':>9} {'Momentum':>10}")
            print(f"      {'-'*25} {'-'*6} {'-'*8} {'-'*9} {'-'*10}")
            
            for c in combos[:10]:  # Top 10
                # Status visual baseado no momentum
                if c['momentum_ratio'] >= 3.0:
                    status = "🔥🔥🔥"  # Super quente (3x+)
                elif c['momentum_ratio'] >= 2.0:
                    status = "🔥🔥"    # Muito quente (2x+)
                else:
                    status = "🔥"       # Quente (1.5x+)
                
                print(f"      {c['combo']:<25} {c['freq_total']:>6} {c['freq_recente']:>8} "
                      f"{c['freq_esperada']:>9.1f} {c['momentum_ratio']:>8.1f}x {status}")
        
        # Resumo das mais quentes
        print(f"\n   {'='*65}")
        print("   📈 RESUMO - TOP COMBINAÇÕES SUPER AQUECIDAS:")
        
        todas_quentes = []
        for tamanho, combos in momentum_por_tamanho.items():
            for c in combos:
                c['tamanho'] = tamanho
                todas_quentes.append(c)
        
        todas_quentes.sort(key=lambda x: x['momentum_ratio'], reverse=True)
        
        for i, c in enumerate(todas_quentes[:10], 1):
            print(f"      {i:2}. {c['combo']} ({c['tamanho']} nums) - "
                  f"{c['momentum_ratio']:.1f}x acima do esperado "
                  f"({c['freq_recente']} vs {c['freq_esperada']:.1f} esperado)")
        
        print()
        print("   💡 INTERPRETAÇÃO:")
        print("      • Momentum 1.5x-2x = Aquecida (saindo 50-100% mais que o normal)")
        print("      • Momentum 2x-3x   = Muito Quente (saindo 100-200% mais que o normal)")
        print("      • Momentum 3x+     = SUPER QUENTE (saindo 200%+ mais que o normal)")
        print()
        print("   ⚠️  ATENÇÃO: Combinações super quentes podem:")
        print("      • Continuar quentes (tendência) OU")
        print("      • Esfriar (reversão à média)")
        print("      • Use em conjunto com outras análises!")
        print("=" * 70)
    
    def analisar_momentum_trios(self, ultimos_n: int = 20):
        """
        Analisa momentum: trios que estao "quentes" recentemente
        Compara frequencia nos ultimos N concursos vs media historica
        """
        print(f"\n[MOMENTUM] Analisando MOMENTUM de trios (ultimos {ultimos_n} concursos)...")
        
        if len(self.dados_posicionais) < ultimos_n:
            print("   [!] Dados insuficientes")
            return []
        
        # Extrair trios dos ultimos N concursos
        trios_recentes = Counter()
        
        for d in self.dados_posicionais[-ultimos_n:]:
            numeros = sorted(d['numeros'])
            # Gerar todos os trios possiveis
            for i in range(13):
                for j in range(i+1, 14):
                    for k in range(j+1, 15):
                        trio = f"{numeros[i]:02d}-{numeros[j]:02d}-{numeros[k]:02d}"
                        trios_recentes[trio] += 1
        
        # Comparar com frequencia historica
        momentum_list = []
        
        for trio, freq_recente in trios_recentes.most_common(50):
            # Buscar frequencia historica
            freq_historica = 0
            for t in self.dados_trios:
                if t['trio'] == trio:
                    freq_historica = t['frequencia']
                    break
            
            if freq_historica > 0:
                # Calcular momentum (freq_recente / media esperada)
                media_esperada = freq_historica / len(self.dados_posicionais) * ultimos_n
                momentum = freq_recente / max(media_esperada, 0.1)
                
                if momentum > 1.5:  # 50% acima do esperado
                    momentum_list.append({
                        'trio': trio,
                        'freq_recente': freq_recente,
                        'freq_historica': freq_historica,
                        'momentum': round(momentum, 2)
                    })
        
        momentum_list.sort(key=lambda x: x['momentum'], reverse=True)
        
        print(f"   [OK] {len(momentum_list)} trios com momentum alto")
        
        return momentum_list[:20]  # Top 20
    
    def gerar_predicao_posicional(self):
        """
        Gera predicao para proximo concurso baseada em:
        1. Probabilidades por posicao
        2. Numeros encalhados (podem voltar)
        3. Trios em divida
        4. Numeros pivo
        """
        print("\n" + "=" * 70)
        print("[PREDICAO] PREDICAO POSICIONAL PARA PROXIMO CONCURSO")
        print("=" * 70)
        
        proximo_concurso = self.ultimo_concurso['concurso'] + 1 if self.ultimo_concurso else 0
        print(f"\n[->] Concurso alvo: {proximo_concurso}")
        
        predicao = {}
        
        for pos in range(1, 16):
            print(f"\n[POS] POSICAO N{pos}:")
            
            # Top 5 numeros mais provaveis
            probs = self.probs_por_posicao.get(pos, [])[:5]
            
            print(f"   Top 5 provaveis: ", end="")
            for num, prob in probs:
                print(f"{num:02d}({prob*100:.1f}%) ", end="")
            print()
            
            # Encalhados nesta posicao
            encalhados = self.numeros_encalhados.get(pos, [])[:3]
            if encalhados:
                print(f"   [ICE] Encalhados: ", end="")
                for num, atraso in encalhados:
                    print(f"{num:02d}(+{atraso}) ", end="")
                print()
            
            # Verificar se algum numero provavel eh pivo
            pivos_na_pos = [num for num, _ in probs if num in self.numeros_pivo]
            if pivos_na_pos:
                print(f"   [PIVO] Pivos: {pivos_na_pos}")
            
            # Sugestao para esta posicao
            sugestoes = set()
            
            # Adicionar top 3 provaveis
            for num, prob in probs[:3]:
                sugestoes.add(num)
            
            # Adicionar encalhados (podem voltar)
            for num, atraso in encalhados[:2]:
                if num in [n for n, _ in probs]:  # So se ja apareceu nesta posicao
                    sugestoes.add(num)
            
            predicao[pos] = sorted(sugestoes)
            print(f"   [->] Sugestoes: {predicao[pos]}")
        
        # Gerar combinacao sugerida baseada nos insights
        self.gerar_combinacao_inteligente(predicao)
        
        return predicao
    
    def gerar_combinacao_inteligente(self, predicao: dict):
        """
        Gera uma combinacao de 15 numeros baseada em:
        1. Probabilidades por posicao
        2. Numeros pivo (conectam trios)
        3. Numeros em trios com alta divida
        """
        print("\n" + "=" * 70)
        print("[COMBINACAO] COMBINACAO INTELIGENTE SUGERIDA")
        print("=" * 70)
        
        # Extrair numeros dos top trios em divida
        numeros_divida = Counter()
        for t in self.trios_em_divida[:30]:
            trio = t['trio']
            try:
                partes = trio.replace(' ', '').split('-')
                for p in partes:
                    numeros_divida[int(p)] += 1
            except:
                continue
        
        # Pontuacao para cada numero
        pontuacao = defaultdict(float)
        
        # 1. Pontos por probabilidade posicional (mais provaveis)
        for pos in range(1, 16):
            probs = self.probs_por_posicao.get(pos, [])[:5]
            for num, prob in probs:
                pontuacao[num] += prob * 10
        
        # 2. Bonus para numeros pivo
        for num in self.numeros_pivo:
            pontuacao[num] += 5
        
        # 3. Bonus para numeros em trios em divida
        for num, count in numeros_divida.items():
            pontuacao[num] += count * 2
        
        # 4. Ordenar por pontuacao
        ranking = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)
        
        print("\n[RANK] TOP 20 NUMEROS POR PONTUACAO:")
        print("-" * 50)
        for i, (num, pts) in enumerate(ranking[:20], 1):
            pivo = "[PIVO]" if num in self.numeros_pivo else "      "
            divida = numeros_divida.get(num, 0)
            print(f"   {i:2}. {num:02d} = {pts:.2f} pts {pivo} (divida: {divida} trios)")
        
        # Selecionar top 15 numeros
        combinacao = sorted([num for num, _ in ranking[:15]])
        
        print("\n" + "=" * 70)
        print("[***] COMBINACAO RECOMENDADA (15 numeros):")
        print("=" * 70)
        print(f"   {' - '.join(f'{n:02d}' for n in combinacao)}")
        print()
        print("[TXT] Como string: " + ",".join(map(str, combinacao)))
        print()
        
        # Verificar quantos pivos estao na combinacao
        pivos_na_comb = [n for n in combinacao if n in self.numeros_pivo]
        print(f"[PIVO] Numeros pivo na combinacao: {len(pivos_na_comb)} -> {pivos_na_comb}")
        
        # Verificar se inclui numeros dos top trios em divida
        numeros_top_divida = set()
        for t in self.trios_em_divida[:10]:
            partes = t['trio'].replace(' ', '').split('-')
            for p in partes:
                numeros_top_divida.add(int(p))
        
        divida_na_comb = [n for n in combinacao if n in numeros_top_divida]
        print(f"[DIVIDA] Numeros de trios em divida: {len(divida_na_comb)} -> {divida_na_comb}")
        
        # NOVO: Aplicar padrões ocultos se disponível
        if self.usar_padroes_ocultos and self.integrador_padroes:
            combinacao = self._aplicar_padroes_ocultos(combinacao)
        
        return combinacao
    
    def _aplicar_padroes_ocultos(self, combinacao: List[int]) -> List[int]:
        """
        Aplica padrões ocultos para melhorar a combinação gerada.
        
        Integra dados da tabela COMBINACOES_LOTOFACIL20_COMPLETO.
        """
        print("\n[PADRÕES OCULTOS] Aplicando padrões das combinações de 20 números...")
        
        # Obter score atual
        score_original = self.integrador_padroes.calcular_score_combinacao(combinacao)
        print(f"   Score original: {score_original:.2f}")
        
        # Tentar melhorar a combinação
        combinacao_melhorada = self.integrador_padroes.melhorar_combinacao(combinacao, max_trocas=2)
        score_melhorado = self.integrador_padroes.calcular_score_combinacao(combinacao_melhorada)
        
        print(f"   Score melhorado: {score_melhorado:.2f}")
        
        if score_melhorado > score_original:
            print(f"   ✅ Combinação melhorada aplicada!")
            print(f"   Nova: {' - '.join(f'{n:02d}' for n in combinacao_melhorada)}")
            return combinacao_melhorada
        else:
            print(f"   ℹ️ Combinação original mantida (melhor score)")
            return combinacao
    
    def obter_trios_padroes_ocultos(self, quantidade: int = 10) -> List[Tuple[int, int, int]]:
        """
        Obtém os trios mais frequentes dos padrões ocultos.
        
        Returns:
            Lista de trios (tuplas de 3 números)
        """
        if not self.usar_padroes_ocultos or not self.integrador_padroes:
            print("[AVISO] Padrões ocultos não disponíveis")
            return []
        
        trios = self.integrador_padroes.obter_trios_prioritarios(quantidade)
        
        print(f"\n[PADRÕES] Top {quantidade} trios dos padrões ocultos:")
        for i, trio in enumerate(trios, 1):
            print(f"   {i:2d}. [{trio[0]:2d}, {trio[1]:2d}, {trio[2]:2d}]")
        
        return trios
    
    def gerar_combinacao_com_padroes_ocultos(self) -> List[int]:
        """
        Gera uma combinação otimizada usando padrões ocultos.
        
        Combina:
        1. Trios prioritários dos padrões ocultos
        2. Números pivô históricos
        3. Probabilidades posicionais
        """
        if not self.usar_padroes_ocultos or not self.integrador_padroes:
            print("[AVISO] Padrões ocultos não disponíveis, usando geração padrão")
            return self.gerar_combinacao_inteligente({})
        
        print("\n" + "=" * 70)
        print("[PADRÕES OCULTOS] COMBINAÇÃO COM PADRÕES OCULTOS")
        print("=" * 70)
        
        combinacao = set()
        
        # 1. Adicionar números de um trio prioritário
        trios = self.integrador_padroes.obter_trios_prioritarios(3)
        if trios:
            trio_escolhido = trios[0]  # Top trio
            combinacao.update(trio_escolhido)
            print(f"   Trio base: {trio_escolhido}")
        
        # 2. Adicionar números prioritários dos padrões ocultos
        numeros_prioritarios = self.integrador_padroes.obter_numeros_prioritarios(20)
        for num in numeros_prioritarios:
            if len(combinacao) >= 15:
                break
            combinacao.add(num)
        
        combinacao = sorted(list(combinacao))[:15]
        
        # 3. Calcular e exibir score
        score = self.integrador_padroes.calcular_score_combinacao(combinacao)
        
        print(f"\n   Combinação gerada: {' - '.join(f'{n:02d}' for n in combinacao)}")
        print(f"   Score de padrões: {score:.2f}")
        
        return combinacao
    
    def mostrar_resumo_trios_divida(self, top_n: int = 20):
        """Mostra trios em divida REAL (candidatos a sair)"""
        print("\n" + "=" * 85)
        print("[DIVIDA-TRIO] TOP TRIOS EM DIVIDA REAL (candidatos a sair)")
        print("=" * 85)
        print(f"   {'Trio':<12} {'Freq':>6} {'Int.Med':>8} {'Atraso':>7} {'Desvio':>8} {'%Acima':>8}")
        print(f"   {'-'*12} {'-'*6} {'-'*8} {'-'*7} {'-'*8} {'-'*8}")
        
        for i, t in enumerate(self.trios_em_divida[:top_n], 1):
            desvio_pct = t.get('desvio_pct', 0)
            if desvio_pct >= 100:
                status = "🔴"
            elif desvio_pct >= 50:
                status = "🟠"
            else:
                status = "🟡"
            
            print(f"   {t['trio']:<12} {t['frequencia']:>6} {t['intervalo_medio']:>8.1f} "
                  f"{t['atraso']:>7} {t['desvio']:>+8.1f} {desvio_pct:>7.1f}% {status}")
        
        print(f"\n   📊 LEGENDA:")
        print(f"      • Int.Med = Intervalo Medio (a cada quantos concursos costuma sair)")
        print(f"      • Desvio = Atraso - Int.Med (quanto esta acima da media)")
        print(f"      • %Acima = Percentual acima da media")
        print(f"      • 🔴 = 100%+ | 🟠 = 50-100% | 🟡 = 20-50%")
        
        # Extrair numeros dos trios em divida
        numeros_divida = Counter()
        for t in self.trios_em_divida[:top_n]:
            trio = t['trio']
            try:
                partes = trio.replace(' ', '').split('-')
                for p in partes:
                    numeros_divida[int(p)] += 1
            except:
                continue
        
        print(f"\n   [NUM] Numeros mais presentes nos trios em divida:")
        for num, count in numeros_divida.most_common(10):
            print(f"      {num:02d}: {count} trios")
    
    def executar_analise_completa(self, tamanhos_extras: List[int] = None):
        """
        Executa analise completa integrada.
        
        Args:
            tamanhos_extras: Lista de tamanhos adicionais para analisar.
                            Se None, analisa todos: [2, 3, 5, 6, 7, 8, 9, 10, 11]
        """
        print("\n" + "=" * 70)
        print("[***] ANALISADOR POSICIONAL + COMBINACOES v4.0")
        print("      Duplas, Trios, Quinas, Sextetos, Setetetos, Octetos,")
        print("      Nonetos, Decatetos e Undecetos")
        print("=" * 70)
        
        inicio = datetime.now()
        
        # 1. Carregar dados posicionais (base para tudo)
        if not self.carregar_dados_posicionais():
            return False
        
        # 2. Analises posicionais
        self.calcular_probabilidades_por_posicao()
        self.identificar_encalhados_por_posicao(limite=10)
        
        # 3. Carregar dados de trios do banco (mais preciso)
        if not self.carregar_dados_trios():
            print("   [!] Trios do banco nao carregados, calculando em Python...")
        
        # 4. Analises de trios (com logica correta de divida)
        self.identificar_trios_em_divida(freq_min=10, desvio_min_pct=20.0)
        self.identificar_numeros_pivo(top_n=200)
        momentum_trios = self.analisar_momentum_trios(ultimos_n=20)
        
        # 5. Mostrar trios em divida
        self.mostrar_resumo_trios_divida(top_n=20)
        
        # 6. Mostrar momentum trios
        if momentum_trios:
            print("\n" + "=" * 70)
            print("[HOT] TRIOS COM MOMENTUM ALTO (tendencia recente)")
            print("=" * 70)
            for i, m in enumerate(momentum_trios[:10], 1):
                print(f"   {i}. {m['trio']}: {m['freq_recente']}x recente, momentum={m['momentum']}")
        
        # 7. ANÁLISES EXPANDIDAS - Duplas a Undecetos
        # Definir tamanhos a analisar (excluindo 3 que já foi feito acima)
        if tamanhos_extras is None:
            tamanhos_extras = [2, 4, 5, 6, 7, 8, 9, 10, 11]
        
        # Configuracoes por tamanho (top_n_carregar, freq_min, desvio_min_pct)
        # desvio_min_pct = percentual minimo acima da media para considerar em divida
        config_tamanhos = {
            2: {'top_n': 5000, 'freq_min': 5, 'desvio_min_pct': 20.0},    # Duplas
            4: {'top_n': 5000, 'freq_min': 5, 'desvio_min_pct': 20.0},    # Quartetos
            5: {'top_n': 5000, 'freq_min': 5, 'desvio_min_pct': 20.0},    # Quinas
            6: {'top_n': 3000, 'freq_min': 4, 'desvio_min_pct': 20.0},    # Sextetos
            7: {'top_n': 3000, 'freq_min': 4, 'desvio_min_pct': 20.0},    # Setetetos
            8: {'top_n': 2000, 'freq_min': 3, 'desvio_min_pct': 20.0},    # Octetos
            9: {'top_n': 2000, 'freq_min': 3, 'desvio_min_pct': 20.0},    # Nonetos
            10: {'top_n': 1500, 'freq_min': 3, 'desvio_min_pct': 20.0},   # Decatetos
            11: {'top_n': 1000, 'freq_min': 3, 'desvio_min_pct': 20.0},   # Undecetos
        }
        
        print("\n" + "=" * 70)
        print("[EXPANDIDO] ANALISE DE COMBINACOES - DUPLAS A UNDECETOS")
        print("=" * 70)
        
        for tamanho in tamanhos_extras:
            if tamanho == 3:
                continue  # Ja analisado acima
            
            # Configuracoes por tamanho (top_n_carregar, freq_min, desvio_min_pct)
            config = config_tamanhos.get(tamanho, {'top_n': 2000, 'freq_min': 3, 'desvio_min_pct': 20.0})
            
            self.executar_analise_tamanho(
                tamanho=tamanho,
                top_n_carregar=config['top_n'],
                freq_min=config.get('freq_min', 3),
                desvio_min_pct=config.get('desvio_min_pct', 20.0)
            )
        
        # 8. SUPER PIVOS - numeros que aparecem em pivos de multiplos tamanhos
        print("\n" + "=" * 70)
        print("[MEGA-PIVO] NUMEROS PIVO EM MULTIPLOS TAMANHOS")
        print("=" * 70)
        
        # Contar em quantos tamanhos cada numero e pivo
        pivo_count = Counter()
        for tamanho, pivos in self.numeros_pivo_por_tamanho.items():
            for num in pivos:
                pivo_count[num] += 1
        
        # Adicionar pivos de trios e quinas originais
        for num in self.numeros_pivo:
            pivo_count[num] += 1
        for num in self.numeros_pivo_quinas:
            pivo_count[num] += 1
        
        print(f"   {'Numero':>8} | {'Aparece em':>12} | {'Status':>20}")
        print(f"   {'-'*8} | {'-'*12} | {'-'*20}")
        
        mega_pivos = []
        for num, count in pivo_count.most_common():
            if count >= 3:
                status = "⭐ MEGA PIVO" if count >= 5 else "🔥 SUPER PIVO" if count >= 4 else "📈 PIVO FORTE"
                print(f"   {num:>8} | {count:>12} | {status:>20}")
                if count >= 4:
                    mega_pivos.append(num)
        
        if mega_pivos:
            print(f"\n   ⭐ MEGA PIVOS (aparecem em 4+ tamanhos): {sorted(mega_pivos)}")
            
            # Validar estatisticamente
            if len(mega_pivos) >= 3:
                self.validar_super_pivos_historico(sorted(mega_pivos)[:7])  # Max 7 para validacao
        
        # 9. Gerar predicao
        predicao = self.gerar_predicao_posicional()
        
        # 10. Resumo final
        fim = datetime.now()
        duracao = (fim - inicio).total_seconds()
        
        print("\n" + "=" * 70)
        print("[OK] ANALISE COMPLETA v4.0 CONCLUIDA!")
        print("=" * 70)
        print(f"   [TIME] Tempo: {duracao:.2f} segundos")
        print(f"   [DATA] Concursos analisados: {len(self.dados_posicionais)}")
        print(f"   [TRIOS] Trios analisados: {len(self.dados_trios)}")
        
        # Resumo por tamanho
        for tamanho in sorted(self.dados_combinacoes.keys()):
            nome = self.NOMES_COMBINACOES.get(tamanho, f"Tam-{tamanho}")
            qtd = len(self.dados_combinacoes[tamanho])
            divida = len(self.combinacoes_em_divida.get(tamanho, []))
            pivos = len(self.numeros_pivo_por_tamanho.get(tamanho, set()))
            print(f"   [{nome.upper()}] Carregadas: {qtd:,} | Em divida: {divida} | Pivos: {pivos}")
        
        print(f"\n   [MEGA-PIVOS] {sorted(mega_pivos) if mega_pivos else 'Nenhum identificado'}")
        print("=" * 70)
        
        return True


    def analisar_pontos_virada(self, combo_str: str, tamanho: int = 3, janela_curta: int = 15, janela_longa: int = 50) -> Dict:
        """
        Analisa pontos de virada (ciclos quentes/frios) de uma combinação.
        
        LOGICA:
        - Divide o histórico em janelas e calcula a frequência em cada uma
        - Detecta quando a frequência muda drasticamente (viradas)
        - Identifica se está em fase QUENTE (abaixo do intervalo médio) ou FRIA (acima)
        
        Args:
            combo_str: String da combinação (ex: "03-11-16")
            tamanho: Tamanho da combinação (2=dupla, 3=trio, etc)
            janela_curta: Tamanho da janela para análise recente (default 15 concursos)
            janela_longa: Tamanho da janela para análise de período (default 50 concursos)
        
        Returns:
            Dict com análise de viradas e tendência atual
        """
        from itertools import combinations
        
        if not self.dados_posicionais:
            return {'erro': 'Dados não carregados'}
        
        # Parsear a combinação
        try:
            numeros_combo = set(int(n) for n in combo_str.split('-'))
        except:
            return {'erro': f'Formato inválido: {combo_str}'}
        
        if len(numeros_combo) != tamanho:
            return {'erro': f'Tamanho incorreto: esperado {tamanho}, recebido {len(numeros_combo)}'}
        
        # Encontrar todas as ocorrências no histórico
        ocorrencias = []
        for d in self.dados_posicionais:
            numeros_sorteio = set(d['numeros'])
            if numeros_combo.issubset(numeros_sorteio):
                ocorrencias.append(d['concurso'])
        
        if len(ocorrencias) < 3:
            return {
                'combo': combo_str,
                'total_ocorrencias': len(ocorrencias),
                'erro': 'Poucas ocorrências para análise de virada'
            }
        
        total_concursos = self.ultimo_concurso['concurso'] if self.ultimo_concurso else 3575
        ultimo_concurso = self.dados_posicionais[-1]['concurso']
        
        # Calcular intervalos entre aparições
        ocorrencias_sorted = sorted(ocorrencias)
        intervalos = []
        for i in range(1, len(ocorrencias_sorted)):
            intervalo = ocorrencias_sorted[i] - ocorrencias_sorted[i-1]
            intervalos.append({
                'de': ocorrencias_sorted[i-1],
                'para': ocorrencias_sorted[i],
                'intervalo': intervalo
            })
        
        # Estatísticas gerais
        intervalo_medio = total_concursos / len(ocorrencias)
        intervalos_valores = [i['intervalo'] for i in intervalos]
        mediana = statistics.median(intervalos_valores) if intervalos_valores else 0
        desvio_padrao = statistics.stdev(intervalos_valores) if len(intervalos_valores) > 1 else 0
        
        # Atraso atual
        atraso_atual = ultimo_concurso - ocorrencias_sorted[-1]
        
        # Detectar CICLOS DE VIRADA
        # Uma virada ocorre quando o padrão muda significativamente
        ciclos = []
        fase_atual = 'NEUTRO'
        inicio_fase = ocorrencias_sorted[0]
        
        # Classificar cada intervalo
        for i, inter in enumerate(intervalos):
            if inter['intervalo'] <= intervalo_medio * 0.6:
                tipo = 'QUENTE'
            elif inter['intervalo'] >= intervalo_medio * 1.5:
                tipo = 'FRIO'
            else:
                tipo = 'NEUTRO'
            
            intervalos[i]['tipo'] = tipo
        
        # Detectar mudanças de fase (viradas)
        viradas = []
        fase_anterior = intervalos[0]['tipo'] if intervalos else 'NEUTRO'
        inicio_fase = intervalos[0]['de'] if intervalos else 0
        contagem_fase = 0
        
        for i, inter in enumerate(intervalos):
            tipo_atual = inter['tipo']
            
            if tipo_atual != fase_anterior and tipo_atual != 'NEUTRO':
                # Virada detectada!
                if contagem_fase >= 2:  # Só conta se a fase anterior teve pelo menos 2 ocorrências
                    viradas.append({
                        'concurso': inter['de'],
                        'de': fase_anterior,
                        'para': tipo_atual,
                        'duracao_fase_anterior': contagem_fase
                    })
                fase_anterior = tipo_atual
                inicio_fase = inter['de']
                contagem_fase = 1
            else:
                contagem_fase += 1
        
        # Analisar fase atual
        ultimos_5_intervalos = intervalos[-5:] if len(intervalos) >= 5 else intervalos
        quentes_recentes = sum(1 for i in ultimos_5_intervalos if i['tipo'] == 'QUENTE')
        frios_recentes = sum(1 for i in ultimos_5_intervalos if i['tipo'] == 'FRIO')
        
        if quentes_recentes >= 3:
            tendencia_recente = 'QUENTE'
        elif frios_recentes >= 3:
            tendencia_recente = 'FRIO'
        else:
            tendencia_recente = 'MISTA'
        
        # Prever próxima virada baseado no padrão histórico
        # Se está quente por muito tempo, tende a esfriar e vice-versa
        duracao_fase_atual = contagem_fase
        duracao_media_fases = len(intervalos) / (len(viradas) + 1) if viradas else len(intervalos)
        
        probabilidade_virada = min(100, (duracao_fase_atual / duracao_media_fases) * 50) if duracao_media_fases > 0 else 0
        
        # Determinar se está em "dívida" considerando ciclos
        em_divida = atraso_atual > intervalo_medio
        z_score = (atraso_atual - intervalo_medio) / desvio_padrao if desvio_padrao > 0 else 0
        
        resultado = {
            'combo': combo_str,
            'total_ocorrencias': len(ocorrencias),
            'intervalo_medio': round(intervalo_medio, 1),
            'intervalo_mediano': round(mediana, 1),
            'desvio_padrao': round(desvio_padrao, 1),
            'atraso_atual': atraso_atual,
            'z_score': round(z_score, 2),
            'em_divida': em_divida,
            'tendencia_recente': tendencia_recente,
            'fase_anterior': fase_anterior,
            'duracao_fase_atual': duracao_fase_atual,
            'viradas_detectadas': len(viradas),
            'ultima_virada': viradas[-1] if viradas else None,
            'probabilidade_virada': round(probabilidade_virada, 1),
            'intervalos_detalhados': intervalos[-10:],  # Últimos 10 intervalos
            'viradas': viradas[-5:] if viradas else []   # Últimas 5 viradas
        }
        
        return resultado
    
    def mostrar_analise_virada(self, combo_str: str, tamanho: int = 3):
        """Mostra análise de pontos de virada de forma visual"""
        analise = self.analisar_pontos_virada(combo_str, tamanho)
        
        if 'erro' in analise and analise.get('total_ocorrencias', 0) < 3:
            print(f"\n⚠️ {analise.get('erro', 'Erro desconhecido')}")
            return
        
        print(f"\n{'='*70}")
        print(f"🔄 ANÁLISE DE PONTOS DE VIRADA: {combo_str}")
        print(f"{'='*70}")
        
        # Estatísticas gerais
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   Total de aparições: {analise['total_ocorrencias']}")
        print(f"   Intervalo MÉDIO esperado: {analise['intervalo_medio']:.1f} concursos")
        print(f"   Intervalo MEDIANO: {analise['intervalo_mediano']:.1f} concursos")
        print(f"   Desvio Padrão: {analise['desvio_padrao']:.1f}")
        
        # Status atual
        print(f"\n🎯 STATUS ATUAL:")
        print(f"   Atraso atual: {analise['atraso_atual']} concursos")
        print(f"   Z-Score: {analise['z_score']:.2f} desvios padrão")
        
        if analise['em_divida']:
            print(f"   Status: 🔴 EM DÍVIDA (atraso > média)")
        else:
            print(f"   Status: 🟢 DENTRO DA MÉDIA")
        
        # Tendência
        print(f"\n📈 TENDÊNCIA:")
        tendencia = analise['tendencia_recente']
        if tendencia == 'QUENTE':
            print(f"   Fase recente: 🔥 QUENTE (aparecendo frequentemente)")
            print(f"   ⚠️ ATENÇÃO: Pode estar prestes a ESFRIAR!")
        elif tendencia == 'FRIO':
            print(f"   Fase recente: ❄️ FRIO (aparecendo pouco)")
            print(f"   💡 OPORTUNIDADE: Pode estar prestes a AQUECER!")
        else:
            print(f"   Fase recente: 🌡️ MISTA (alternando)")
        
        # Viradas
        print(f"\n🔄 HISTÓRICO DE VIRADAS:")
        print(f"   Total de viradas detectadas: {analise['viradas_detectadas']}")
        print(f"   Duração da fase atual: {analise['duracao_fase_atual']} intervalos")
        print(f"   Probabilidade de virada: {analise['probabilidade_virada']:.0f}%")
        
        if analise['viradas']:
            print(f"\n   Últimas viradas:")
            for v in analise['viradas'][-3:]:
                emoji_de = '🔥' if v['de'] == 'QUENTE' else '❄️' if v['de'] == 'FRIO' else '🌡️'
                emoji_para = '🔥' if v['para'] == 'QUENTE' else '❄️' if v['para'] == 'FRIO' else '🌡️'
                print(f"      Concurso {v['concurso']}: {emoji_de} {v['de']} → {emoji_para} {v['para']} (fase durou {v['duracao_fase_anterior']} intervalos)")
        
        # Últimos intervalos
        print(f"\n📅 ÚLTIMOS INTERVALOS:")
        for inter in analise['intervalos_detalhados'][-7:]:
            emoji = '🔥' if inter['tipo'] == 'QUENTE' else '❄️' if inter['tipo'] == 'FRIO' else '🌡️'
            print(f"      {inter['de']} → {inter['para']}: {inter['intervalo']} concursos {emoji}")
        
        # Conclusão
        print(f"\n💡 CONCLUSÃO:")
        if analise['probabilidade_virada'] >= 70:
            print(f"   ⚠️ ALTA probabilidade de virada de fase!")
            if tendencia == 'QUENTE':
                print(f"   🧊 Preparar para possível ESFRIAMENTO")
            elif tendencia == 'FRIO':
                print(f"   🔥 Preparar para possível AQUECIMENTO - BOM MOMENTO PARA APOSTAR!")
        elif analise['em_divida'] and analise['z_score'] >= 1.5:
            print(f"   🎯 Combinação MUITO atrasada - forte candidata a aparecer!")
        elif not analise['em_divida']:
            print(f"   ✅ Combinação dentro do padrão esperado")
        
        print(f"{'='*70}")


def executar_analise_posicional_trios_interface():
    """Interface para o Super Menu"""
    analisador = AnalisadorPosicionalTrios()
    
    try:
        analisador.executar_analise_completa()
        input("\n[PAUSE] Pressione ENTER para continuar...")
        return True
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Funcao principal"""
    executar_analise_posicional_trios_interface()


if __name__ == "__main__":
    main()
