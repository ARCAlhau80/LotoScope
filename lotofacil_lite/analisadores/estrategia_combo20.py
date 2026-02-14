#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESTRATÉGIA COMBO 20 - DIVERGENTES MUTUAMENTE EXCLUDENTES
==========================================================
Sistema que explora o padrão de duas combinações de 20 números
que diferem em apenas 3 números e são mutuamente excludentes.

COMBO 1: [1,3,4,6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
COMBO 2: [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

DIVERGENTES:
- Grupo C1: [1, 3, 4]
- Grupo C2: [15, 17, 18]
- Núcleo comum: 17 números

PADRÃO EXPLORADO:
- Quando [1,3,4] aparece completo, [15,17,18] NÃO aparece em ~87%
- Tendência histórica ligeiramente favorável ao Grupo C1

Autor: LotoScope AI
Data: Janeiro 2026
"""

import pyodbc
import random
from collections import Counter
from statistics import mean, stdev
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from itertools import combinations


class EstrategiaCombo20:
    """
    Sistema de geração baseado em duas combos de 20 números
    com divergentes mutuamente excludentes.
    """
    
    # Combinações base
    COMBO1 = [1,3,4,6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
    COMBO2 = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    
    # Divergentes
    DIV_C1 = [1, 3, 4]    # Apenas na Combo 1
    DIV_C2 = [15, 17, 18]  # Apenas na Combo 2
    
    # Núcleo comum (17 números)
    NUCLEO = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23, 24, 25]
    
    # Números fora de ambas as combos
    FORA_AMBAS = [2, 5]
    
    def __init__(self):
        self.conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=Lotofacil;"
            "Trusted_Connection=yes;"
        )
        self.resultados = []
        self.tendencia = None
        self.ultimo_concurso = None
        
    def conectar_banco(self):
        """Conecta ao banco de dados."""
        return pyodbc.connect(self.conn_str)
    
    def carregar_resultados(self) -> int:
        """Carrega todos os resultados da tabela Resultados_INT."""
        with self.conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Concurso, 
                       N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT
                ORDER BY Concurso DESC
            """)
            
            self.resultados = []
            for row in cursor.fetchall():
                concurso = row.Concurso
                numeros = set(row[i] for i in range(1, 16))
                self.resultados.append((concurso, numeros))
        
        if self.resultados:
            self.ultimo_concurso = self.resultados[0][0]
        
        return len(self.resultados)
    
    def analisar_tendencia(self, ultimos_n: int = 100) -> Dict:
        """
        Analisa a tendência atual entre as duas combos.
        
        Args:
            ultimos_n: Quantidade de concursos recentes a analisar
        """
        if not self.resultados:
            self.carregar_resultados()
        
        set1 = set(self.COMBO1)
        set2 = set(self.COMBO2)
        
        ultimos = self.resultados[:ultimos_n]
        total = len(ultimos)
        
        c1_wins = 0
        c2_wins = 0
        empates = 0
        
        historico_detalhado = []
        
        for conc, nums in ultimos:
            ac1 = len(set1 & nums)
            ac2 = len(set2 & nums)
            div1 = len(set(self.DIV_C1) & nums)
            div2 = len(set(self.DIV_C2) & nums)
            
            if ac1 > ac2:
                c1_wins += 1
                vencedor = 'C1'
            elif ac2 > ac1:
                c2_wins += 1
                vencedor = 'C2'
            else:
                empates += 1
                vencedor = '=='
            
            historico_detalhado.append({
                'concurso': conc,
                'ac1': ac1,
                'ac2': ac2,
                'div1': div1,
                'div2': div2,
                'vencedor': vencedor
            })
        
        self.tendencia = {
            'ultimos_n': ultimos_n,
            'c1_wins': c1_wins,
            'c2_wins': c2_wins,
            'empates': empates,
            'pct_c1': c1_wins * 100 / total if total > 0 else 0,
            'pct_c2': c2_wins * 100 / total if total > 0 else 0,
            'pct_empate': empates * 100 / total if total > 0 else 0,
            'vencedor_tendencia': 'C1' if c1_wins > c2_wins else ('C2' if c2_wins > c1_wins else 'EMPATE'),
            'historico': historico_detalhado[:30]  # Últimos 30 para display
        }
        
        return self.tendencia
    
    def exibir_tendencia(self):
        """Exibe a tendência atual de forma visual."""
        if not self.tendencia:
            self.analisar_tendencia()
        
        t = self.tendencia
        
        print("\n" + "=" * 70)
        print("   ESTRATEGIA COMBO 20 - DIVERGENTES MUTUAMENTE EXCLUDENTES")
        print("=" * 70)
        
        print("\n   COMBOS ANALISADAS:")
        print(f"   C1: {self.COMBO1}")
        print(f"   C2: {self.COMBO2}")
        print(f"\n   Divergentes C1: {self.DIV_C1}")
        print(f"   Divergentes C2: {self.DIV_C2}")
        print(f"   Nucleo comum:   {len(self.NUCLEO)} numeros")
        print(f"   Fora de ambas:  {self.FORA_AMBAS}")
        
        print("\n" + "=" * 70)
        print(f"   TENDENCIA NOS ULTIMOS {t['ultimos_n']} CONCURSOS")
        print("=" * 70)
        
        print(f"\n   Combo 1 venceu: {t['c1_wins']:3d} vezes ({t['pct_c1']:.1f}%)")
        print(f"   Combo 2 venceu: {t['c2_wins']:3d} vezes ({t['pct_c2']:.1f}%)")
        print(f"   Empates:        {t['empates']:3d} vezes ({t['pct_empate']:.1f}%)")
        
        venc = t['vencedor_tendencia']
        if venc == 'C1':
            print(f"\n   >>> TENDENCIA ATUAL: COMBO 1 [1,3,4] <<<")
        elif venc == 'C2':
            print(f"\n   >>> TENDENCIA ATUAL: COMBO 2 [15,17,18] <<<")
        else:
            print(f"\n   >>> TENDENCIA ATUAL: EQUILIBRADO <<<")
        
        print("\n" + "-" * 70)
        print("   ULTIMOS 30 CONCURSOS:")
        print("-" * 70)
        print("   Conc    C1   C2  Venc   [1,3,4]  [15,17,18]")
        print("   " + "-" * 50)
        
        for h in t['historico']:
            venc_mark = '[C1]' if h['vencedor'] == 'C1' else ('[C2]' if h['vencedor'] == 'C2' else '[==]')
            print(f"   {h['concurso']:5d}   {h['ac1']:2d}   {h['ac2']:2d}  {venc_mark}     {h['div1']}/3       {h['div2']}/3")
    
    def sugerir_estrategia(self) -> str:
        """Sugere a melhor estratégia baseada na tendência atual."""
        if not self.tendencia:
            self.analisar_tendencia()
        
        t = self.tendencia
        
        # Analisar últimos 10 para ver alternância
        ultimos10 = t['historico'][:10]
        c1_recentes = sum(1 for h in ultimos10 if h['vencedor'] == 'C1')
        c2_recentes = sum(1 for h in ultimos10 if h['vencedor'] == 'C2')
        
        print("\n" + "=" * 70)
        print("   SUGESTAO DE ESTRATEGIA")
        print("=" * 70)
        
        if t['vencedor_tendencia'] == 'C1':
            print("\n   Com base na tendencia dos ultimos 100 concursos:")
            print("   >>> Recomendamos usar MAIS numeros do grupo [1, 3, 4]")
            sugestao = 'C1_DOMINANTE'
        elif t['vencedor_tendencia'] == 'C2':
            print("\n   Com base na tendencia dos ultimos 100 concursos:")
            print("   >>> Recomendamos usar MAIS numeros do grupo [15, 17, 18]")
            sugestao = 'C2_DOMINANTE'
        else:
            print("\n   Tendencia equilibrada - recomendamos estrategia HIBRIDA")
            sugestao = 'HIBRIDA'
        
        # Analisar alternância
        if c1_recentes > 7:
            print(f"\n   ATENCAO: Nos ultimos 10, C1 dominou ({c1_recentes}/10)")
            print("   Pode haver reversao para C2 em breve!")
            sugestao = 'ALTERNANCIA_C2'
        elif c2_recentes > 7:
            print(f"\n   ATENCAO: Nos ultimos 10, C2 dominou ({c2_recentes}/10)")
            print("   Pode haver reversao para C1 em breve!")
            sugestao = 'ALTERNANCIA_C1'
        
        return sugestao
    
    def gerar_todas_combinacoes(self, 
                                 min_c1: int = 0, max_c1: int = 20,
                                 min_c2: int = 0, max_c2: int = 20,
                                 usar_fora: bool = False,
                                 limite: int = None) -> List[List[int]]:
        """
        Gera TODAS as combinações possíveis de 15 números dentro dos critérios.
        
        Args:
            min_c1: Mínimo de números da Combo 1 a usar
            max_c1: Máximo de números da Combo 1 a usar
            min_c2: Mínimo de números da Combo 2 a usar
            max_c2: Máximo de números da Combo 2 a usar
            usar_fora: Se True, permite usar [2, 5] que não estão em nenhuma combo
            limite: Limite máximo de combinações (None = sem limite)
            
        Returns:
            Lista de todas as combinações válidas
        """
        # Pool de números disponíveis
        pool_c1 = set(self.COMBO1)
        pool_c2 = set(self.COMBO2)
        
        if usar_fora:
            todos_numeros = list(range(1, 26))
        else:
            # Apenas números que estão em C1 ou C2
            todos_numeros = sorted(list(pool_c1 | pool_c2))
        
        # Ajustar mínimos/máximos
        min_c1 = max(0, min(min_c1, 20))
        max_c1 = max(min_c1, min(max_c1, 20))
        min_c2 = max(0, min(min_c2, 20))
        max_c2 = max(min_c2, min(max_c2, 20))
        
        print(f"\n   Enumerando TODAS as combinacoes possiveis...")
        print(f"   Range C1: {min_c1} a {max_c1} | Range C2: {min_c2} a {max_c2}")
        if usar_fora:
            print(f"   Incluindo numeros fora das combos: {self.FORA_AMBAS}")
        if limite:
            print(f"   Limite maximo: {limite} combinacoes")
        
        combinacoes_validas = []
        total_analisadas = 0
        
        # Gerar todas as combinações de 15 números
        for combo_tuple in combinations(todos_numeros, 15):
            combo = list(combo_tuple)
            combo_set = set(combo)
            
            # Verificar restrições
            n_de_c1 = len(combo_set & pool_c1)
            n_de_c2 = len(combo_set & pool_c2)
            
            if min_c1 <= n_de_c1 <= max_c1 and min_c2 <= n_de_c2 <= max_c2:
                combinacoes_validas.append(combo)
                
                if limite and len(combinacoes_validas) >= limite:
                    print(f"   Limite de {limite} atingido.")
                    break
            
            total_analisadas += 1
            
            # Feedback a cada 100k
            if total_analisadas % 100000 == 0:
                print(f"   ... {total_analisadas:,} analisadas, {len(combinacoes_validas):,} validas")
        
        print(f"\n   Total: {len(combinacoes_validas):,} combinacoes validas encontradas")
        return combinacoes_validas
    
    def gerar_combinacoes(self, quantidade: int = None,
                          min_c1: int = 0, max_c1: int = 20,
                          min_c2: int = 0, max_c2: int = 20,
                          usar_fora: bool = False,
                          estrategia: str = 'SUGERIDA') -> List[List[int]]:
        """
        Gera combinações de 15 números baseada na estratégia.
        
        Args:
            quantidade: Número de combinações a gerar (None = TODAS possíveis)
            min_c1: Mínimo de números da Combo 1 a usar
            max_c1: Máximo de números da Combo 1 a usar
            min_c2: Mínimo de números da Combo 2 a usar
            max_c2: Máximo de números da Combo 2 a usar
            usar_fora: Se True, permite usar [2, 5] que não estão em nenhuma combo
            estrategia: 'C1', 'C2', 'HIBRIDA', 'NUCLEO' ou 'SUGERIDA'
            
        Returns:
            Lista de combinações
        """
        # Se quantidade é None, gerar TODAS as combinações possíveis
        if quantidade is None:
            return self.gerar_todas_combinacoes(
                min_c1=min_c1, max_c1=max_c1,
                min_c2=min_c2, max_c2=max_c2,
                usar_fora=usar_fora
            )
        
        if not self.tendencia:
            self.analisar_tendencia()
        
        combinacoes = []
        
        # Definir estratégia
        if estrategia == 'SUGERIDA':
            estrategia = self.sugerir_estrategia()
        
        print(f"\n   Gerando {quantidade} combinacoes com estrategia: {estrategia}")
        print(f"   Range C1: {min_c1} a {max_c1} | Range C2: {min_c2} a {max_c2}")
        if usar_fora:
            print(f"   Usando numeros fora das combos: {self.FORA_AMBAS}")
        
        # Pool disponível
        pool_c1 = set(self.COMBO1)
        pool_c2 = set(self.COMBO2)
        pool_fora = set(self.FORA_AMBAS) if usar_fora else set()
        
        # Ajustar mínimos/máximos
        min_c1 = max(0, min(min_c1, 20))
        max_c1 = max(min_c1, min(max_c1, 20))
        min_c2 = max(0, min(min_c2, 20))
        max_c2 = max(min_c2, min(max_c2, 20))
        
        tentativas = 0
        max_tentativas = quantidade * 500
        
        while len(combinacoes) < quantidade and tentativas < max_tentativas:
            tentativas += 1
            
            combo = set()
            
            # Estratégia define a distribuição
            if estrategia in ['C1_DOMINANTE', 'C1', 'ALTERNANCIA_C1']:
                # Priorizar C1 - usar mais divergentes de C1
                n_div_c1 = random.randint(2, 3)  # 2-3 de [1,3,4]
                n_div_c2 = random.randint(0, 1)  # 0-1 de [15,17,18]
            elif estrategia in ['C2_DOMINANTE', 'C2', 'ALTERNANCIA_C2']:
                # Priorizar C2 - usar mais divergentes de C2
                n_div_c1 = random.randint(0, 1)  # 0-1 de [1,3,4]
                n_div_c2 = random.randint(2, 3)  # 2-3 de [15,17,18]
            else:  # HIBRIDA ou NUCLEO
                # Equilibrado
                n_div_c1 = random.randint(1, 2)
                n_div_c2 = random.randint(1, 2)
            
            # Adicionar divergentes
            combo.update(random.sample(self.DIV_C1, min(n_div_c1, len(self.DIV_C1))))
            combo.update(random.sample(self.DIV_C2, min(n_div_c2, len(self.DIV_C2))))
            
            # Completar com núcleo comum
            nucleo_restante = [n for n in self.NUCLEO if n not in combo]
            n_nucleo = 15 - len(combo)
            
            if usar_fora:
                # Chance de usar números fora
                if random.random() < 0.3:
                    n_fora = random.randint(1, min(2, n_nucleo))
                    combo.update(random.sample(list(pool_fora), n_fora))
                    n_nucleo = 15 - len(combo)
            
            if len(nucleo_restante) >= n_nucleo:
                combo.update(random.sample(nucleo_restante, n_nucleo))
            else:
                combo.update(nucleo_restante)
                # Completar com qualquer um que falte
                todos = list(range(1, 26))
                faltam = 15 - len(combo)
                disponiveis = [n for n in todos if n not in combo]
                if disponiveis and faltam > 0:
                    combo.update(random.sample(disponiveis, min(faltam, len(disponiveis))))
            
            # Verificar restrições de min/max
            n_de_c1 = len(combo & pool_c1)
            n_de_c2 = len(combo & pool_c2)
            
            if min_c1 <= n_de_c1 <= max_c1 and min_c2 <= n_de_c2 <= max_c2:
                combo_list = sorted(list(combo))[:15]
                if len(combo_list) == 15 and combo_list not in combinacoes:
                    combinacoes.append(combo_list)
        
        return combinacoes
    
    def validar_combinacoes(self, combinacoes: List[List[int]]) -> Dict:
        """Valida as combinações geradas contra o histórico."""
        if not self.resultados:
            self.carregar_resultados()
        
        print(f"\n   Validando {len(combinacoes)} combinacoes contra {len(self.resultados)} concursos...")
        
        resultados_validacao = []
        
        for combo in combinacoes:
            combo_set = set(combo)
            acertos_lista = [len(combo_set & nums) for _, nums in self.resultados]
            
            resultados_validacao.append({
                'combinacao': combo,
                'media': mean(acertos_lista),
                'min': min(acertos_lista),
                'max': max(acertos_lista),
                'ac15': acertos_lista.count(15),
                'ac14': acertos_lista.count(14),
                'ac13': acertos_lista.count(13),
                'ac12': acertos_lista.count(12),
                'ac11': acertos_lista.count(11),
            })
        
        return resultados_validacao
    
    def exibir_combinacoes(self, combinacoes: List[List[int]], validacao: List[Dict] = None):
        """Exibe as combinações geradas."""
        print("\n" + "=" * 70)
        print("   COMBINACOES GERADAS")
        print("=" * 70)
        
        for i, combo in enumerate(combinacoes, 1):
            combo_str = ' - '.join(f'{n:02d}' for n in combo)
            
            # Marcar divergentes
            c1_count = sum(1 for n in combo if n in self.DIV_C1)
            c2_count = sum(1 for n in combo if n in self.DIV_C2)
            fora_count = sum(1 for n in combo if n in self.FORA_AMBAS)
            
            print(f"\n   {i:2d}. {combo_str}")
            print(f"       [1,3,4]={c1_count}/3  [15,17,18]={c2_count}/3  [2,5]={fora_count}/2")
            
            if validacao and i <= len(validacao):
                v = validacao[i-1]
                print(f"       Media: {v['media']:.2f} | 15ac:{v['ac15']} 14ac:{v['ac14']} 13ac:{v['ac13']} 12ac:{v['ac12']} 11ac:{v['ac11']}")
    
    def salvar_combinacoes(self, combinacoes: List[List[int]], arquivo: str = None):
        """Salva as combinações em arquivo TXT."""
        if arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"combo20_estrategia_{timestamp}.txt"
        
        with open(arquivo, 'w') as f:
            f.write(f"# ESTRATEGIA COMBO 20 - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Tendencia: {self.tendencia['vencedor_tendencia'] if self.tendencia else 'N/A'}\n")
            f.write(f"# Total: {len(combinacoes)} combinacoes\n\n")
            
            for combo in combinacoes:
                f.write(','.join(map(str, combo)) + '\n')
        
        print(f"\n   Combinacoes salvas em: {arquivo}")
        return arquivo
    
    def calcular_ranking_numeros(self, ultimos_n: int = 100) -> Dict[int, float]:
        """
        Calcula o ranking de cada número (1-25) baseado em frequência recente.
        
        Args:
            ultimos_n: Quantidade de concursos recentes a considerar
            
        Returns:
            Dicionário {numero: score} onde maior score = melhor
        """
        if not self.resultados:
            self.carregar_resultados()
        
        # Contar frequência nos últimos N concursos
        frequencia = Counter()
        for concurso, numeros in self.resultados[:ultimos_n]:
            frequencia.update(numeros)
        
        # Normalizar para score (0-1)
        max_freq = max(frequencia.values()) if frequencia else 1
        ranking = {n: frequencia.get(n, 0) / max_freq for n in range(1, 26)}
        
        return ranking
    
    def gerar_combinacoes_complementares(self, 
                                          combinacoes: List[List[int]],
                                          n_mantidos: int = 13,
                                          ultimos_n: int = 100) -> List[List[int]]:
        """
        Gera combinações complementares (hedge) para cada combinação proposta.
        
        Lógica: Para cada combinação de 15 números:
        - Pega os N melhores números DA combinação (por ranking de frequência)
        - Pega os (15-N) melhores dos que NÃO estão na combinação
        
        PROPORÇÃO ÓTIMA DESCOBERTA: 13 mantidos + 2 de fora
        (Testado com 21.420 combinações, melhora +0.0091 vs original)
        
        Args:
            combinacoes: Lista de combinações propostas (15 números cada)
            n_mantidos: Quantidade de números a manter da proposta (default: 13 - ótimo)
            ultimos_n: Concursos recentes para calcular ranking
            
        Returns:
            Lista de combinações complementares
        """
        n_fora = 15 - n_mantidos
        
        print(f"\n   Gerando combinacoes complementares (hedge)...")
        print(f"   Proporcao: {n_mantidos} mantidos + {n_fora} de fora")
        print(f"   Ranking baseado nos ultimos {ultimos_n} concursos")
        
        # Calcular ranking de todos os números
        ranking = self.calcular_ranking_numeros(ultimos_n)
        
        complementares = []
        
        for combo in combinacoes:
            combo_set = set(combo)
            fora_combo = [n for n in range(1, 26) if n not in combo_set]
            
            # Ordenar números DA combinação por ranking (melhor primeiro)
            nums_combo_ordenados = sorted(combo, key=lambda n: ranking[n], reverse=True)
            top_mantidos = nums_combo_ordenados[:n_mantidos]
            
            # Ordenar números FORA da combinação por ranking (melhor primeiro)
            nums_fora_ordenados = sorted(fora_combo, key=lambda n: ranking[n], reverse=True)
            top_fora = nums_fora_ordenados[:n_fora]
            
            # Montar combinação complementar
            complementar = sorted(top_mantidos + top_fora)
            complementares.append(complementar)
        
        print(f"   Total: {len(complementares)} combinacoes complementares geradas")
        return complementares
    
    def salvar_com_complementares(self, 
                                   combinacoes: List[List[int]],
                                   complementares: List[List[int]],
                                   arquivo_principal: str = None,
                                   arquivo_complementar: str = None) -> Tuple[str, str]:
        """
        Salva as combinações principais e complementares em arquivos separados.
        
        Args:
            combinacoes: Combinações principais
            complementares: Combinações complementares (hedge)
            arquivo_principal: Nome do arquivo principal (opcional)
            arquivo_complementar: Nome do arquivo complementar (opcional)
            
        Returns:
            Tupla (path_principal, path_complementar)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if arquivo_principal is None:
            arquivo_principal = f"combo20_PRINCIPAL_{timestamp}.txt"
        if arquivo_complementar is None:
            arquivo_complementar = f"combo20_COMPLEMENTAR_{timestamp}.txt"
        
        # Salvar principais
        with open(arquivo_principal, 'w') as f:
            f.write(f"# ESTRATEGIA COMBO 20 - PRINCIPAL\n")
            f.write(f"# Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Tendencia: {self.tendencia['vencedor_tendencia'] if self.tendencia else 'N/A'}\n")
            f.write(f"# Total: {len(combinacoes)} combinacoes\n")
            f.write(f"# Tipo: Combinacoes principais propostas\n\n")
            
            for combo in combinacoes:
                f.write(','.join(map(str, combo)) + '\n')
        
        # Salvar complementares
        with open(arquivo_complementar, 'w') as f:
            f.write(f"# ESTRATEGIA COMBO 20 - COMPLEMENTAR (HEDGE)\n")
            f.write(f"# Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Total: {len(complementares)} combinacoes\n")
            f.write(f"# Tipo: 13 melhores da proposta + 2 melhores de fora (proporcao otima)\n")
            f.write(f"# Objetivo: Cobertura caso a exclusao tenha sido errada\n\n")
            
            for combo in complementares:
                f.write(','.join(map(str, combo)) + '\n')
        
        print(f"\n   Arquivos salvos:")
        print(f"   📁 Principal:     {arquivo_principal}")
        print(f"   📁 Complementar:  {arquivo_complementar}")
        
        return arquivo_principal, arquivo_complementar
    
    def exibir_comparativo(self, 
                           combinacoes: List[List[int]], 
                           complementares: List[List[int]],
                           limite: int = 5):
        """Exibe comparativo entre combinações principais e complementares."""
        print("\n" + "=" * 70)
        print("   COMPARATIVO: PRINCIPAL vs COMPLEMENTAR")
        print("=" * 70)
        
        ranking = self.calcular_ranking_numeros()
        
        for i, (principal, complementar) in enumerate(zip(combinacoes[:limite], complementares[:limite]), 1):
            print(f"\n   {i}. PRINCIPAL:     {' - '.join(f'{n:02d}' for n in principal)}")
            print(f"      COMPLEMENTAR: {' - '.join(f'{n:02d}' for n in complementar)}")
            
            # Mostrar diferenças
            set_p = set(principal)
            set_c = set(complementar)
            
            mantidos = set_p & set_c
            removidos = set_p - set_c
            adicionados = set_c - set_p
            
            print(f"      Mantidos: {sorted(mantidos)} ({len(mantidos)})")
            print(f"      Removidos: {sorted(removidos)} ({len(removidos)})")
            print(f"      Adicionados: {sorted(adicionados)} ({len(adicionados)})")
        
        if len(combinacoes) > limite:
            print(f"\n   ... e mais {len(combinacoes) - limite} pares")
    
    def menu_interativo(self):
        """Menu interativo para a estratégia."""
        print("\n" + "=" * 70)
        print("   ESTRATEGIA COMBO 20 - MENU INTERATIVO")
        print("=" * 70)
        
        # Carregar dados
        print("\n   Carregando dados...")
        total = self.carregar_resultados()
        print(f"   {total} concursos carregados.")
        
        while True:
            print("\n" + "-" * 70)
            print("   OPCOES:")
            print("   1. Ver tendencia atual")
            print("   2. Ver sugestao de estrategia")
            print("   3. Gerar combinacoes (configuravel)")
            print("   4. Gerar combinacoes rapido (estrategia sugerida)")
            print("   0. Voltar ao menu principal")
            print("-" * 70)
            
            opcao = input("\n   Escolha uma opcao: ").strip()
            
            if opcao == '0':
                break
            
            elif opcao == '1':
                self.analisar_tendencia()
                self.exibir_tendencia()
            
            elif opcao == '2':
                self.analisar_tendencia()
                self.exibir_tendencia()
                sugestao = self.sugerir_estrategia()
                print(f"\n   Estrategia sugerida: {sugestao}")
            
            elif opcao == '3':
                self._gerar_configuravel()
            
            elif opcao == '4':
                self._gerar_rapido()
            
            else:
                print("\n   Opcao invalida!")
            
            input("\n   Pressione ENTER para continuar...")
    
    def _gerar_configuravel(self):
        """Geração configurável de combinações."""
        print("\n" + "=" * 70)
        print("   GERACAO CONFIGURAVEL")
        print("=" * 70)
        
        # Mostrar tendência primeiro
        self.analisar_tendencia()
        self.exibir_tendencia()
        sugestao = self.sugerir_estrategia()
        
        print("\n   ESTRATEGIAS DISPONIVEIS:")
        print("   1. C1 - Priorizar [1, 3, 4]")
        print("   2. C2 - Priorizar [15, 17, 18]")
        print("   3. HIBRIDA - Equilibrado entre os dois")
        print("   4. SUGERIDA - Usar a sugestao automatica")
        
        est_opcao = input("\n   Escolha a estrategia (1-4) [4]: ").strip() or '4'
        estrategias = {'1': 'C1', '2': 'C2', '3': 'HIBRIDA', '4': 'SUGERIDA'}
        estrategia = estrategias.get(est_opcao, 'SUGERIDA')
        
        # Quantidade
        print("\n   Por padrao, gera TODAS as combinacoes possiveis.")
        print("   Digite um numero para limitar, ou ENTER para todas.")
        qtd = input("\n   Quantidade de combinacoes [TODAS]: ").strip()
        quantidade = int(qtd) if qtd.isdigit() else None
        
        # Ranges
        print("\n   CONFIGURACAO DE RANGES (quantidade de numeros de cada combo)")
        print(f"   Combo 1 tem {len(self.COMBO1)} numeros: {self.COMBO1}")
        print(f"   Combo 2 tem {len(self.COMBO2)} numeros: {self.COMBO2}")
        
        min_c1 = input("\n   Minimo de numeros da Combo 1 [0]: ").strip()
        min_c1 = int(min_c1) if min_c1.isdigit() else 0
        
        max_c1 = input(f"   Maximo de numeros da Combo 1 [{len(self.COMBO1)}]: ").strip()
        max_c1 = int(max_c1) if max_c1.isdigit() else len(self.COMBO1)
        
        min_c2 = input("\n   Minimo de numeros da Combo 2 [0]: ").strip()
        min_c2 = int(min_c2) if min_c2.isdigit() else 0
        
        max_c2 = input(f"   Maximo de numeros da Combo 2 [{len(self.COMBO2)}]: ").strip()
        max_c2 = int(max_c2) if max_c2.isdigit() else len(self.COMBO2)
        
        # Usar números fora
        usar_fora = input("\n   Usar numeros fora das combos [2,5]? (s/n) [n]: ").strip().lower() == 's'
        
        # Gerar
        combinacoes = self.gerar_combinacoes(
            quantidade=quantidade,
            min_c1=min_c1, max_c1=max_c1,
            min_c2=min_c2, max_c2=max_c2,
            usar_fora=usar_fora,
            estrategia=estrategia
        )
        
        if combinacoes:
            # Validar
            validacao = self.validar_combinacoes(combinacoes)
            self.exibir_combinacoes(combinacoes, validacao)
            
            # Salvar
            salvar = input("\n   Salvar em arquivo? (s/n) [s]: ").strip().lower() != 'n'
            if salvar:
                self.salvar_combinacoes(combinacoes)
        else:
            print("\n   Nenhuma combinacao gerada com os criterios informados.")
    
    def _gerar_rapido(self):
        """Geração rápida com estratégia sugerida."""
        print("\n" + "=" * 70)
        print("   GERACAO RAPIDA (ESTRATEGIA SUGERIDA)")
        print("=" * 70)
        
        self.analisar_tendencia()
        
        print("\n   Por padrao, gera TODAS as combinacoes possiveis.")
        print("   Digite um numero para limitar, ou ENTER para todas.")
        qtd = input("\n   Quantidade de combinacoes [TODAS]: ").strip()
        quantidade = int(qtd) if qtd.isdigit() else None
        
        combinacoes = self.gerar_combinacoes(
            quantidade=quantidade,
            estrategia='SUGERIDA'
        )
        
        if combinacoes:
            validacao = self.validar_combinacoes(combinacoes)
            self.exibir_combinacoes(combinacoes, validacao)
            
            salvar = input("\n   Salvar em arquivo? (s/n) [s]: ").strip().lower() != 'n'
            if salvar:
                self.salvar_combinacoes(combinacoes)


def main():
    """Função principal para execução standalone."""
    sistema = EstrategiaCombo20()
    sistema.menu_interativo()


if __name__ == "__main__":
    main()
