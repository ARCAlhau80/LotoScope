#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 ANALISADOR DE SIMILARIDADE E SISTEMA DE PIVÔS
================================================

Prova de Conceito (POC) que integra duas análises poderosas:

1. 📊 ANÁLISE RESULTADO x RESULTADO (Matriz de Similaridade)
   - Compara cada concurso com todos os demais
   - Descobre o "perfil DNA" das combinações sorteadas
   - Identifica clusters de resultados similares
   - Encontra o núcleo comum de números

2. 🎯 GERADOR BASEADO EM PIVÔS (Distribuição Controlada)
   - Usa números pivô informados pelo usuário (5 a 20 números)
   - Gera combinações respeitando distribuição histórica
   - Mínimo de apostas → Máxima cobertura probabilística
   - Integra com opção 7.12 (Machine Learning)

Autor: LotoScope POC
Data: Janeiro 2026
"""

import pyodbc
import random
import math
import json
import os
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional
from itertools import combinations
from datetime import datetime

# Constantes
TODOS_NUMEROS = list(range(1, 26))
CUSTO_APOSTA = 3.50
PREMIO = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}

# Importar integrador de padrões ocultos
try:
    from integracao_padroes_ocultos import (
        PadroesOcultosIntegrador,
        obter_numeros_padroes_ocultos,
        obter_trios_padroes_ocultos,
        calcular_score_padroes,
        filtrar_por_padroes_ocultos
    )
    PADROES_OCULTOS_DISPONIVEIS = True
except ImportError:
    PADROES_OCULTOS_DISPONIVEIS = False
    print("⚠️ Integração de padrões ocultos não disponível")


class AnalisadorPivoSimilaridade:
    """
    Classe principal que integra análise de similaridade e geração por pivôs.
    Agora com suporte a padrões ocultos da tabela COMBINACOES_LOTOFACIL20_COMPLETO.
    """
    
    def __init__(self):
        self.conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=Lotofacil;"
            "Trusted_Connection=yes;"
        )
        self.resultados = []  # Lista de (concurso, set de números)
        self.matriz_similaridade = {}  # {(c1, c2): acertos}
        self.perfil_distribuicao = {}  # {qtd_acertos: frequencia}
        self.numeros_pivo = []  # Números pivô informados
        self.distribuicao_pivo = {}  # {qtd_pivos: percentual}
        
        # Integração com padrões ocultos
        self.usar_padroes_ocultos = PADROES_OCULTOS_DISPONIVEIS
        self.integrador_padroes = None
        if self.usar_padroes_ocultos:
            try:
                self.integrador_padroes = PadroesOcultosIntegrador()
            except Exception as e:
                print(f"⚠️ Erro ao carregar padrões ocultos: {e}")
                self.usar_padroes_ocultos = False
        
    def conectar_banco(self):
        """Conecta ao banco de dados."""
        return pyodbc.connect(self.conn_str)
    
    def carregar_resultados(self) -> int:
        """Carrega todos os resultados da tabela Resultados_INT."""
        print("📥 Carregando resultados do banco de dados...")
        
        with self.conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Concurso, 
                       N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT
                ORDER BY Concurso ASC
            """)
            
            self.resultados = []
            for row in cursor.fetchall():
                concurso = row.Concurso
                numeros = set(row[i] for i in range(1, 16))
                self.resultados.append((concurso, numeros))
        
        print(f"✅ {len(self.resultados)} concursos carregados!")
        return len(self.resultados)
    
    # =========================================================================
    # PARTE 1: ANÁLISE DE SIMILARIDADE RESULTADO x RESULTADO
    # =========================================================================
    
    def analisar_similaridade_completa(self, amostra_max: int = None) -> Dict:
        """
        Analisa similaridade entre TODOS os resultados.
        
        Para cada par de concursos, calcula quantos números têm em comum.
        Isso revela o "perfil DNA" das combinações sorteadas.
        
        Args:
            amostra_max: Se informado, usa apenas os últimos N concursos (performance)
        
        Returns:
            Dict com estatísticas de similaridade
        """
        print("\n" + "=" * 70)
        print("📊 ANÁLISE DE SIMILARIDADE RESULTADO x RESULTADO")
        print("=" * 70)
        
        # Usar amostra ou todos
        dados = self.resultados[-amostra_max:] if amostra_max else self.resultados
        total_concursos = len(dados)
        
        print(f"🔢 Analisando {total_concursos} concursos...")
        print(f"📈 Total de comparações: {total_concursos * (total_concursos - 1) // 2:,}")
        
        # Contadores
        distribuicao_acertos = defaultdict(int)
        soma_acertos = 0
        total_comparacoes = 0
        min_acertos = 15
        max_acertos = 0
        
        # Armazenar pares interessantes
        pares_max_similaridade = []  # Pares com máximo de acertos (exceto 15)
        pares_min_similaridade = []  # Pares com mínimo de acertos
        
        # Calcular similaridade para cada par
        print("\n⏳ Calculando matriz de similaridade...")
        
        for i in range(len(dados)):
            c1, nums1 = dados[i]
            
            for j in range(i + 1, len(dados)):
                c2, nums2 = dados[j]
                
                # Calcular interseção (acertos em comum)
                acertos = len(nums1 & nums2)
                
                # Atualizar estatísticas
                distribuicao_acertos[acertos] += 1
                soma_acertos += acertos
                total_comparacoes += 1
                
                if acertos < min_acertos:
                    min_acertos = acertos
                    pares_min_similaridade = [(c1, c2, acertos)]
                elif acertos == min_acertos:
                    pares_min_similaridade.append((c1, c2, acertos))
                
                if acertos > max_acertos and acertos < 15:  # Exceto o próprio
                    max_acertos = acertos
                    pares_max_similaridade = [(c1, c2, acertos)]
                elif acertos == max_acertos and acertos < 15:
                    pares_max_similaridade.append((c1, c2, acertos))
            
            # Progress
            if (i + 1) % 500 == 0:
                print(f"   Processado: {i + 1}/{len(dados)} ({(i+1)/len(dados)*100:.1f}%)")
        
        # Calcular média
        media_acertos = soma_acertos / total_comparacoes if total_comparacoes > 0 else 0
        
        # Guardar distribuição para uso posterior
        self.perfil_distribuicao = dict(distribuicao_acertos)
        
        # Exibir resultados
        print("\n" + "=" * 70)
        print("📊 RESULTADO DA ANÁLISE DE SIMILARIDADE")
        print("=" * 70)
        print(f"🔢 Total de concursos analisados: {total_concursos}")
        print(f"📈 Total de comparações realizadas: {total_comparacoes:,}")
        print()
        
        print("📊 ESTATÍSTICAS DE ACERTOS ENTRE RESULTADOS:")
        print("-" * 50)
        print(f"   🔻 MÍNIMO:  {min_acertos} números em comum")
        print(f"   📊 MÉDIA:   {media_acertos:.2f} números em comum")
        print(f"   🔺 MÁXIMO:  {max_acertos} números em comum")
        print()
        
        print("📈 DISTRIBUIÇÃO DE SIMILARIDADE:")
        print("-" * 50)
        for acertos in sorted(distribuicao_acertos.keys(), reverse=True):
            qtd = distribuicao_acertos[acertos]
            pct = qtd / total_comparacoes * 100
            barra = '█' * int(pct / 2)
            print(f"   {acertos:2d} números: {qtd:8,} pares ({pct:5.2f}%) {barra}")
        print()
        
        # Mostrar pares mais similares
        if pares_max_similaridade:
            print(f"🏆 PARES MAIS SIMILARES ({max_acertos} números em comum):")
            print("-" * 50)
            for c1, c2, acc in pares_max_similaridade[:10]:
                print(f"   Concursos {c1} ↔ {c2}: {acc} números iguais")
            if len(pares_max_similaridade) > 10:
                print(f"   ... e mais {len(pares_max_similaridade) - 10} pares")
        print()
        
        # Mostrar pares menos similares
        if pares_min_similaridade:
            print(f"📉 PARES MENOS SIMILARES ({min_acertos} números em comum):")
            print("-" * 50)
            for c1, c2, acc in pares_min_similaridade[:10]:
                print(f"   Concursos {c1} ↔ {c2}: {acc} números iguais")
            if len(pares_min_similaridade) > 10:
                print(f"   ... e mais {len(pares_min_similaridade) - 10} pares")
        print()
        
        # Análise do "núcleo comum"
        self._analisar_nucleo_comum(dados)
        
        return {
            'total_concursos': total_concursos,
            'total_comparacoes': total_comparacoes,
            'min_acertos': min_acertos,
            'max_acertos': max_acertos,
            'media_acertos': media_acertos,
            'distribuicao': dict(distribuicao_acertos),
            'pares_max': pares_max_similaridade[:20],
            'pares_min': pares_min_similaridade[:20]
        }
    
    def _analisar_nucleo_comum(self, dados: List[Tuple[int, Set[int]]]):
        """
        Analisa quais números formam o "núcleo comum" dos resultados.
        Números que aparecem com mais frequência em pares de alta similaridade.
        """
        print("🧬 ANÁLISE DO NÚCLEO COMUM (DNA dos Resultados):")
        print("-" * 50)
        
        # Contar frequência de cada número
        frequencia = Counter()
        for _, nums in dados:
            for n in nums:
                frequencia[n] += 1
        
        # Calcular percentual
        total = len(dados)
        print("   📊 Frequência de cada número nos resultados:")
        print()
        
        # Ordenar por frequência
        ordenados = frequencia.most_common()
        
        # Dividir em grupos
        grupo_alto = [n for n, f in ordenados if f/total >= 0.65]
        grupo_medio = [n for n, f in ordenados if 0.55 <= f/total < 0.65]
        grupo_baixo = [n for n, f in ordenados if f/total < 0.55]
        
        print(f"   🔥 QUENTES (≥65%): {sorted(grupo_alto)}")
        print(f"   📊 MÉDIOS (55-65%): {sorted(grupo_medio)}")
        print(f"   ❄️ FRIOS (<55%): {sorted(grupo_baixo)}")
        print()
        
        # Top 16 (para sugestão de pivôs)
        top_16 = [n for n, _ in ordenados[:16]]
        print(f"   💡 SUGESTÃO DE PIVÔS (Top 16): {sorted(top_16)}")
        print()
    
    # =========================================================================
    # PARTE 2: SISTEMA DE PIVÔS COM DISTRIBUIÇÃO CONTROLADA
    # =========================================================================
    
    def definir_pivos(self, numeros_pivo: List[int]) -> bool:
        """
        Define os números pivô para análise e geração.
        
        Args:
            numeros_pivo: Lista de 5 a 20 números entre 1 e 25
            
        Returns:
            True se válido, False caso contrário
        """
        # Validações
        if len(numeros_pivo) < 5 or len(numeros_pivo) > 20:
            print(f"❌ Informe de 5 a 20 números pivô! Você informou {len(numeros_pivo)}.")
            return False
        
        if any(n < 1 or n > 25 for n in numeros_pivo):
            print("❌ Todos os números devem estar entre 1 e 25!")
            return False
        
        if len(set(numeros_pivo)) != len(numeros_pivo):
            print("❌ Não pode haver números repetidos!")
            return False
        
        self.numeros_pivo = sorted(set(numeros_pivo))
        print(f"✅ Pivôs definidos: {self.numeros_pivo}")
        return True
    
    def definir_pivos_padroes_ocultos(self, quantidade: int = 16) -> bool:
        """
        Define os pivôs automaticamente baseado nos padrões ocultos 
        descobertos na tabela COMBINACOES_LOTOFACIL20_COMPLETO.
        
        Args:
            quantidade: Quantidade de números pivô (5 a 20)
            
        Returns:
            True se definiu com sucesso
        """
        if not self.usar_padroes_ocultos or not self.integrador_padroes:
            print("❌ Padrões ocultos não disponíveis!")
            print("   Execute primeiro o analisador_padroes_ocultos_20.py")
            return False
        
        print("\n" + "=" * 70)
        print("🔮 DEFININDO PIVÔS BASEADO EM PADRÕES OCULTOS")
        print("=" * 70)
        
        # Obter números prioritários dos padrões
        numeros_prioritarios = self.integrador_padroes.obter_numeros_prioritarios(quantidade)
        
        if not numeros_prioritarios or len(numeros_prioritarios) < 5:
            print("❌ Não foi possível obter números dos padrões ocultos!")
            return False
        
        # Exibir análise dos padrões
        print(f"\n📊 Top {quantidade} números dos padrões ocultos:")
        nums_vencedores = self.integrador_padroes.numeros_vencedores
        for i, num in enumerate(numeros_prioritarios[:quantidade], 1):
            freq = nums_vencedores.get(num, 0) * 100
            print(f"   {i:2d}. Número {num:2d}: aparece em {freq:.1f}% das combinações vencedoras")
        
        # Exibir trios recomendados
        trios = self.integrador_padroes.obter_trios_prioritarios(3)
        if trios:
            print(f"\n🎲 Trios mais frequentes incluídos:")
            for trio in trios:
                print(f"   [{trio[0]:2d}, {trio[1]:2d}, {trio[2]:2d}]")
        
        # Definir pivôs
        self.numeros_pivo = sorted(numeros_prioritarios[:quantidade])
        print(f"\n✅ Pivôs definidos (padrões ocultos): {self.numeros_pivo}")
        return True
    
    def aplicar_padroes_ocultos_combinacoes(self, combinacoes: List[List[int]], 
                                             top_percentual: float = 0.5) -> List[List[int]]:
        """
        Filtra combinações mantendo as que melhor se alinham com padrões ocultos.
        
        Args:
            combinacoes: Lista de combinações a filtrar
            top_percentual: Percentual das melhores a manter (0.5 = 50%)
            
        Returns:
            Lista filtrada e ordenada por score
        """
        if not self.usar_padroes_ocultos or not self.integrador_padroes:
            print("⚠️ Padrões ocultos não disponíveis, retornando combinações originais")
            return combinacoes
        
        print(f"\n📊 Aplicando padrões ocultos para filtrar {len(combinacoes)} combinações...")
        
        # Calcular score de cada combinação
        scored = []
        for combo in combinacoes:
            score = self.integrador_padroes.calcular_score_combinacao(combo)
            scored.append((combo, score))
        
        # Ordenar por score
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Manter top percentual
        quantidade = max(1, int(len(scored) * top_percentual))
        filtradas = [combo for combo, score in scored[:quantidade]]
        
        print(f"✅ Filtradas para {len(filtradas)} combinações (top {top_percentual*100:.0f}%)")
        
        # Exibir top 5 scores
        print(f"\n🏆 Top 5 combinações por score de padrões:")
        for i, (combo, score) in enumerate(scored[:5], 1):
            print(f"   {i}. {combo} - Score: {score:.2f}")
        
        return filtradas

    def analisar_distribuicao_pivos(self) -> Dict:
        """
        Analisa como os números pivô se distribuem nos resultados históricos.
        
        Para cada resultado, conta quantos números dos pivôs aparecem.
        Isso define a distribuição ideal para geração de combinações.
        
        Returns:
            Dict com distribuição de pivôs
        """
        if not self.numeros_pivo:
            print("❌ Defina os números pivô primeiro!")
            return {}
        
        if not self.resultados:
            self.carregar_resultados()
        
        print("\n" + "=" * 70)
        print("🎯 ANÁLISE DE DISTRIBUIÇÃO DOS PIVÔS")
        print("=" * 70)
        print(f"🔢 Pivôs analisados ({len(self.numeros_pivo)}): {self.numeros_pivo}")
        print(f"📊 Total de concursos: {len(self.resultados)}")
        print()
        
        # Números complementares (fora dos pivôs)
        numeros_complemento = [n for n in TODOS_NUMEROS if n not in self.numeros_pivo]
        print(f"🔄 Complementos ({len(numeros_complemento)}): {numeros_complemento}")
        print()
        
        # Contar distribuição
        distribuicao = defaultdict(list)  # {qtd_pivos: [concursos]}
        
        for concurso, nums in self.resultados:
            qtd_pivos = len(nums & set(self.numeros_pivo))
            distribuicao[qtd_pivos].append(concurso)
        
        # Calcular estatísticas
        total = len(self.resultados)
        qtd_pivos_lista = [len(nums & set(self.numeros_pivo)) for _, nums in self.resultados]
        
        min_pivos = min(qtd_pivos_lista)
        max_pivos = max(qtd_pivos_lista)
        media_pivos = sum(qtd_pivos_lista) / len(qtd_pivos_lista)
        
        print("📊 ESTATÍSTICAS:")
        print("-" * 50)
        print(f"   🔻 MÍNIMO:  {min_pivos} pivôs no resultado")
        print(f"   📊 MÉDIA:   {media_pivos:.2f} pivôs no resultado")
        print(f"   🔺 MÁXIMO:  {max_pivos} pivôs no resultado")
        print()
        
        # Distribuição detalhada
        print("📈 DISTRIBUIÇÃO DE PIVÔS NOS RESULTADOS:")
        print("-" * 50)
        
        self.distribuicao_pivo = {}
        for qtd in sorted(distribuicao.keys(), reverse=True):
            concursos = distribuicao[qtd]
            pct = len(concursos) / total * 100
            barra = '█' * int(pct / 2)
            print(f"   {qtd:2d} pivôs: {len(concursos):5d} concursos ({pct:5.2f}%) {barra}")
            self.distribuicao_pivo[qtd] = {
                'quantidade': len(concursos),
                'percentual': pct,
                'concursos': concursos[:5]  # Primeiros 5 exemplos
            }
        print()
        
        # Faixa ideal (onde está a maioria)
        faixa_ideal = [qtd for qtd, info in self.distribuicao_pivo.items() 
                      if info['percentual'] >= 10]
        if faixa_ideal:
            print(f"🎯 FAIXA IDEAL DE PIVÔS: {min(faixa_ideal)} a {max(faixa_ideal)}")
            pct_faixa = sum(self.distribuicao_pivo[q]['percentual'] for q in faixa_ideal)
            print(f"   📊 Cobertura desta faixa: {pct_faixa:.2f}%")
        print()
        
        # Análise de complementos necessários
        print("🔄 COMPLEMENTOS NECESSÁRIOS (15 - pivôs):")
        print("-" * 50)
        for qtd in sorted(distribuicao.keys(), reverse=True):
            complementos = 15 - qtd
            pct = self.distribuicao_pivo[qtd]['percentual']
            if pct >= 1:
                print(f"   {complementos:2d} números fora dos pivôs: {pct:5.2f}% dos resultados")
        print()
        
        return self.distribuicao_pivo
    
    def gerar_combinacoes_pivo(self, quantidade: int = 50, 
                                respeitar_distribuicao: bool = True) -> List[List[int]]:
        """
        Gera combinações respeitando a distribuição histórica de pivôs.
        
        Args:
            quantidade: Número de combinações a gerar
            respeitar_distribuicao: Se True, respeita percentuais históricos
            
        Returns:
            Lista de combinações geradas
        """
        if not self.numeros_pivo:
            print("❌ Defina os números pivô primeiro!")
            return []
        
        if not self.distribuicao_pivo:
            self.analisar_distribuicao_pivos()
        
        print("\n" + "=" * 70)
        print("🎰 GERADOR DE COMBINAÇÕES BASEADO EM PIVÔS")
        print("=" * 70)
        print(f"🔢 Pivôs: {self.numeros_pivo}")
        print(f"🎯 Quantidade solicitada: {quantidade}")
        print(f"📊 Respeitar distribuição histórica: {'Sim' if respeitar_distribuicao else 'Não'}")
        print()
        
        combinacoes = []
        numeros_complemento = [n for n in TODOS_NUMEROS if n not in self.numeros_pivo]
        
        if respeitar_distribuicao:
            # Calcular quantas combinações para cada faixa
            distribuicao_quantidade = {}
            soma_pct = sum(info['percentual'] for info in self.distribuicao_pivo.values())
            
            for qtd_pivos, info in self.distribuicao_pivo.items():
                # Só considerar faixas viáveis (min 5 pivôs se temos 16 pivôs)
                if qtd_pivos <= len(self.numeros_pivo) and (15 - qtd_pivos) <= len(numeros_complemento):
                    n_combinacoes = int(round(quantidade * info['percentual'] / soma_pct))
                    if n_combinacoes > 0:
                        distribuicao_quantidade[qtd_pivos] = n_combinacoes
            
            # Ajustar para total exato
            total_planejado = sum(distribuicao_quantidade.values())
            if total_planejado < quantidade:
                # Adicionar na faixa mais frequente
                faixa_maior = max(distribuicao_quantidade.keys(), 
                                 key=lambda x: self.distribuicao_pivo[x]['percentual'])
                distribuicao_quantidade[faixa_maior] += quantidade - total_planejado
            
            print("📈 Distribuição planejada:")
            for qtd_pivos in sorted(distribuicao_quantidade.keys(), reverse=True):
                n = distribuicao_quantidade[qtd_pivos]
                complementos = 15 - qtd_pivos
                print(f"   {qtd_pivos} pivôs + {complementos} complementos: {n} combinações")
            print()
            
            # Gerar combinações para cada faixa
            for qtd_pivos, n_combinacoes in distribuicao_quantidade.items():
                qtd_complementos = 15 - qtd_pivos
                
                for _ in range(n_combinacoes):
                    tentativas = 0
                    while tentativas < 100:
                        # Selecionar pivôs
                        pivos_selecionados = random.sample(self.numeros_pivo, qtd_pivos)
                        
                        # Selecionar complementos
                        complementos_selecionados = random.sample(numeros_complemento, qtd_complementos)
                        
                        # Combinar e ordenar
                        combinacao = sorted(pivos_selecionados + complementos_selecionados)
                        
                        # Verificar duplicata
                        if combinacao not in combinacoes:
                            combinacoes.append(combinacao)
                            break
                        
                        tentativas += 1
        
        else:
            # Geração aleatória simples
            while len(combinacoes) < quantidade:
                combinacao = sorted(random.sample(TODOS_NUMEROS, 15))
                if combinacao not in combinacoes:
                    combinacoes.append(combinacao)
        
        print(f"✅ {len(combinacoes)} combinações geradas!")
        
        # Aplicar filtro de padrões ocultos se disponível
        if self.usar_padroes_ocultos and self.integrador_padroes:
            print("\n🔮 Aplicando padrões ocultos para melhorar as combinações...")
            combinacoes = self.aplicar_padroes_ocultos_combinacoes(
                combinacoes, 
                top_percentual=0.7  # Mantém 70% das melhores
            )
        
        return combinacoes
    
    def gerar_combinacoes_pivo_otimizadas(self, quantidade: int = 50) -> List[List[int]]:
        """
        Gera combinações otimizadas usando padrões ocultos como pivôs.
        
        Este método combina:
        1. Pivôs definidos automaticamente pelos padrões ocultos
        2. Distribuição histórica de acertos
        3. Filtro final por score de padrões
        
        Args:
            quantidade: Número de combinações a gerar
            
        Returns:
            Lista de combinações otimizadas
        """
        print("\n" + "=" * 70)
        print("🚀 GERADOR OTIMIZADO COM PADRÕES OCULTOS")
        print("=" * 70)
        
        if not self.usar_padroes_ocultos or not self.integrador_padroes:
            print("⚠️ Padrões ocultos não disponíveis, usando geração padrão...")
            return self.gerar_combinacoes_pivo(quantidade)
        
        # 1. Definir pivôs automaticamente usando padrões ocultos
        if not self.numeros_pivo:
            self.definir_pivos_padroes_ocultos(16)
        
        # 2. Gerar mais combinações que o necessário (para filtrar depois)
        quantidade_inicial = int(quantidade * 1.5)  # Gerar 50% a mais
        combinacoes = []
        
        # Obter trios prioritários para garantir que apareçam
        trios_prioritarios = self.integrador_padroes.obter_trios_prioritarios(5)
        
        # Gerar algumas combinações garantindo trios
        print(f"\n🎲 Gerando combinações com trios prioritários...")
        for trio in trios_prioritarios:
            for _ in range(quantidade // len(trios_prioritarios)):
                tentativas = 0
                while tentativas < 100:
                    # Começar com o trio
                    combo = list(trio)
                    
                    # Completar com números prioritários
                    nums_prioritarios = self.integrador_padroes.obter_numeros_prioritarios(20)
                    for num in nums_prioritarios:
                        if num not in combo and len(combo) < 15:
                            combo.append(num)
                    
                    # Se ainda falta, adicionar aleatório
                    while len(combo) < 15:
                        num = random.randint(1, 25)
                        if num not in combo:
                            combo.append(num)
                    
                    combo = sorted(combo)
                    if combo not in combinacoes:
                        combinacoes.append(combo)
                        break
                    tentativas += 1
        
        # Completar com combinações da distribuição histórica
        if len(combinacoes) < quantidade_inicial:
            restante = quantidade_inicial - len(combinacoes)
            print(f"\n📊 Completando com {restante} combinações por distribuição...")
            combos_adicionais = self.gerar_combinacoes_pivo(restante, respeitar_distribuicao=True)
            
            for combo in combos_adicionais:
                if combo not in combinacoes:
                    combinacoes.append(combo)
        
        # 3. Filtrar usando padrões ocultos (manter top 67%)
        print(f"\n🔮 Filtrando {len(combinacoes)} combinações por padrões ocultos...")
        combinacoes_finais = self.aplicar_padroes_ocultos_combinacoes(
            combinacoes, 
            top_percentual=quantidade / len(combinacoes) if combinacoes else 1.0
        )
        
        # Garantir quantidade exata
        combinacoes_finais = combinacoes_finais[:quantidade]
        
        print(f"\n✅ {len(combinacoes_finais)} combinações otimizadas geradas!")
        return combinacoes_finais
    
    def validar_combinacoes_contra_historico(self, combinacoes: List[List[int]]) -> Dict:
        """
        Valida as combinações geradas contra todos os resultados históricos.
        
        Args:
            combinacoes: Lista de combinações a validar
            
        Returns:
            Dict com estatísticas de validação
        """
        if not self.resultados:
            self.carregar_resultados()
        
        print("\n" + "=" * 70)
        print("📊 VALIDAÇÃO DAS COMBINAÇÕES CONTRA HISTÓRICO")
        print("=" * 70)
        print(f"🎰 Combinações a validar: {len(combinacoes)}")
        print(f"📈 Concursos no histórico: {len(self.resultados)}")
        print()
        
        # Estatísticas por combinação
        resultados_validacao = []
        
        for i, comb in enumerate(combinacoes):
            comb_set = set(comb)
            acertos_lista = []
            
            for concurso, resultado in self.resultados:
                acertos = len(comb_set & resultado)
                acertos_lista.append(acertos)
            
            resultados_validacao.append({
                'combinacao': comb,
                'min_acertos': min(acertos_lista),
                'max_acertos': max(acertos_lista),
                'media_acertos': sum(acertos_lista) / len(acertos_lista),
                'acertos_15': acertos_lista.count(15),
                'acertos_14': acertos_lista.count(14),
                'acertos_13': acertos_lista.count(13),
                'acertos_12': acertos_lista.count(12),
                'acertos_11': acertos_lista.count(11),
            })
        
        # Estatísticas gerais
        todas_medias = [r['media_acertos'] for r in resultados_validacao]
        todos_max = [r['max_acertos'] for r in resultados_validacao]
        
        print("📊 ESTATÍSTICAS GERAIS DAS COMBINAÇÕES:")
        print("-" * 50)
        print(f"   📊 Média geral de acertos: {sum(todas_medias)/len(todas_medias):.2f}")
        print(f"   🔺 Melhor acerto máximo: {max(todos_max)}")
        print()
        
        # Contagem de prêmios potenciais
        total_15 = sum(r['acertos_15'] for r in resultados_validacao)
        total_14 = sum(r['acertos_14'] for r in resultados_validacao)
        total_13 = sum(r['acertos_13'] for r in resultados_validacao)
        total_12 = sum(r['acertos_12'] for r in resultados_validacao)
        total_11 = sum(r['acertos_11'] for r in resultados_validacao)
        
        print("🏆 POTENCIAL DE PRÊMIOS (se jogasse todas em todos os concursos):")
        print("-" * 50)
        print(f"   15 acertos: {total_15} (R$ {total_15 * PREMIO[15]:,.2f})")
        print(f"   14 acertos: {total_14} (R$ {total_14 * PREMIO[14]:,.2f})")
        print(f"   13 acertos: {total_13} (R$ {total_13 * PREMIO[13]:,.2f})")
        print(f"   12 acertos: {total_12} (R$ {total_12 * PREMIO[12]:,.2f})")
        print(f"   11 acertos: {total_11} (R$ {total_11 * PREMIO[11]:,.2f})")
        print()
        
        # Top 10 melhores combinações
        print("🏆 TOP 10 MELHORES COMBINAÇÕES:")
        print("-" * 50)
        ordenados = sorted(resultados_validacao, 
                          key=lambda x: (x['max_acertos'], x['media_acertos']), 
                          reverse=True)
        
        for i, r in enumerate(ordenados[:10], 1):
            print(f"   {i}. {r['combinacao']}")
            print(f"      Max: {r['max_acertos']} | Média: {r['media_acertos']:.2f} | "
                  f"11+: {r['acertos_11']+r['acertos_12']+r['acertos_13']+r['acertos_14']+r['acertos_15']}")
        
        return {
            'resultados': resultados_validacao,
            'media_geral': sum(todas_medias) / len(todas_medias),
            'total_premios': {15: total_15, 14: total_14, 13: total_13, 12: total_12, 11: total_11}
        }
    
    def gerar_pool_otimizado(self, quantidade_maxima: int = 100) -> List[List[int]]:
        """
        Gera pool otimizado de combinações com máxima cobertura.
        
        Estratégia:
        1. Gera candidatas respeitando distribuição de pivôs
        2. Seleciona as que têm melhor cobertura diversificada
        3. Remove redundâncias (combinações muito similares)
        
        Args:
            quantidade_maxima: Máximo de combinações no pool final
            
        Returns:
            Pool otimizado de combinações
        """
        print("\n" + "=" * 70)
        print("🔬 GERADOR DE POOL OTIMIZADO (Máxima Cobertura)")
        print("=" * 70)
        
        # Gerar pool inicial maior
        pool_inicial = self.gerar_combinacoes_pivo(quantidade_maxima * 3, True)
        
        # Validar contra histórico
        print("\n📊 Validando pool inicial...")
        validacao = self.validar_combinacoes_contra_historico(pool_inicial)
        
        # Ordenar por performance
        pool_ordenado = sorted(validacao['resultados'],
                              key=lambda x: (x['max_acertos'], 
                                           x['acertos_11'] + x['acertos_12'] * 2 + 
                                           x['acertos_13'] * 3 + x['acertos_14'] * 5 + 
                                           x['acertos_15'] * 10,
                                           x['media_acertos']),
                              reverse=True)
        
        # Selecionar diversificando
        pool_final = []
        for item in pool_ordenado:
            comb = item['combinacao']
            
            # Verificar se não é muito similar às já selecionadas
            muito_similar = False
            for selecionada in pool_final:
                acertos_comum = len(set(comb) & set(selecionada))
                if acertos_comum >= 13:  # Muito similar
                    muito_similar = True
                    break
            
            if not muito_similar:
                pool_final.append(comb)
                
                if len(pool_final) >= quantidade_maxima:
                    break
        
        print(f"\n✅ Pool otimizado: {len(pool_final)} combinações selecionadas")
        print(f"   (Redução de {len(pool_inicial)} para {len(pool_final)})")
        
        return pool_final
    
    def exportar_combinacoes(self, combinacoes: List[List[int]], 
                            arquivo: str = None) -> str:
        """
        Exporta combinações para arquivo TXT no diretório lotofacil_lite.
        Formato: apenas combinações separadas por vírgula, uma por linha.
        
        Args:
            combinacoes: Lista de combinações
            arquivo: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        # Diretório padrão: lotofacil_lite
        diretorio_base = Path(__file__).parent.parent  # lotofacil_lite
        
        if not arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"combinacoes_pivo_{timestamp}.txt"
        
        caminho_completo = diretorio_base / arquivo
        
        with open(caminho_completo, 'w') as f:
            for comb in combinacoes:
                linha = ",".join(str(n).zfill(2) for n in comb)
                f.write(f"{linha}\n")
        
        print(f"✅ Combinações exportadas para: {caminho_completo}")
        return str(caminho_completo)
    
    def exportar_para_ml(self, combinacoes: List[List[int]]) -> Dict:
        """
        Prepara dados para integração com o sistema ML 7.12.
        
        Exporta:
        1. Arquivo TXT com combinações
        2. JSON com metadados para ML
        3. Distribuição de pivôs para uso como feature
        
        Returns:
            Dict com caminhos dos arquivos e dados para ML
        """
        diretorio_base = Path(__file__).parent.parent  # lotofacil_lite
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Exportar combinações
        arquivo_txt = self.exportar_combinacoes(combinacoes, f"combinacoes_pivo_ml_{timestamp}.txt")
        
        # 2. Criar JSON com metadados para ML
        dados_ml = {
            'timestamp': datetime.now().isoformat(),
            'numeros_pivo': self.numeros_pivo,
            'total_combinacoes': len(combinacoes),
            'distribuicao_pivo': self.distribuicao_pivo,
            'perfil_similaridade': self.perfil_distribuicao,
            'combinacoes': combinacoes,
            'insights': self._extrair_insights(),
            'features_ml': self._preparar_features_ml(combinacoes)
        }
        
        arquivo_json = diretorio_base / f"dados_pivo_ml_{timestamp}.json"
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(dados_ml, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dados ML exportados para: {arquivo_json}")
        
        return {
            'arquivo_txt': arquivo_txt,
            'arquivo_json': str(arquivo_json),
            'dados': dados_ml
        }
    
    def _extrair_insights(self) -> Dict:
        """Extrai insights úteis da análise para o ML."""
        insights = {
            'faixa_ideal_pivos': [],
            'cobertura_faixa_ideal': 0,
            'media_similaridade': 0,
            'numeros_nucleo': [],
            'recomendacoes': []
        }
        
        # Faixa ideal de pivôs
        if self.distribuicao_pivo:
            faixa_ideal = [qtd for qtd, info in self.distribuicao_pivo.items() 
                          if info['percentual'] >= 10]
            if faixa_ideal:
                insights['faixa_ideal_pivos'] = [min(faixa_ideal), max(faixa_ideal)]
                insights['cobertura_faixa_ideal'] = sum(
                    self.distribuicao_pivo[q]['percentual'] for q in faixa_ideal
                )
        
        # Média de similaridade
        if self.perfil_distribuicao:
            total_pares = sum(self.perfil_distribuicao.values())
            if total_pares > 0:
                soma_ponderada = sum(k * v for k, v in self.perfil_distribuicao.items())
                insights['media_similaridade'] = soma_ponderada / total_pares
        
        # Números núcleo (aparecem em mais de 60% dos resultados)
        if self.resultados:
            from collections import Counter
            frequencia = Counter()
            for _, nums in self.resultados:
                for n in nums:
                    frequencia[n] += 1
            total = len(self.resultados)
            insights['numeros_nucleo'] = [n for n, f in frequencia.most_common() if f/total >= 0.60]
        
        # Recomendações para ML
        if insights['faixa_ideal_pivos']:
            min_pivo, max_pivo = insights['faixa_ideal_pivos']
            insights['recomendacoes'] = [
                f"Usar {min_pivo}-{max_pivo} números dos pivôs em cada combinação",
                f"Cobertura esperada: {insights['cobertura_faixa_ideal']:.1f}%",
                f"Complementar com {15-max_pivo} a {15-min_pivo} números fora dos pivôs"
            ]
        
        return insights
    
    def _preparar_features_ml(self, combinacoes: List[List[int]]) -> List[Dict]:
        """Prepara features de cada combinação para ML."""
        features = []
        pivo_set = set(self.numeros_pivo)
        
        for comb in combinacoes:
            comb_set = set(comb)
            
            # Features básicas
            qtd_pivos = len(comb_set & pivo_set)
            qtd_complementos = 15 - qtd_pivos
            
            # Features de distribuição
            soma = sum(comb)
            pares = sum(1 for n in comb if n % 2 == 0)
            baixos = sum(1 for n in comb if n <= 12)
            
            # Sequências
            seq_max = 1
            seq_atual = 1
            for i in range(1, len(comb)):
                if comb[i] == comb[i-1] + 1:
                    seq_atual += 1
                    seq_max = max(seq_max, seq_atual)
                else:
                    seq_atual = 1
            
            features.append({
                'combinacao': comb,
                'qtd_pivos': qtd_pivos,
                'qtd_complementos': qtd_complementos,
                'soma': soma,
                'pares': pares,
                'impares': 15 - pares,
                'baixos': baixos,
                'altos': 15 - baixos,
                'seq_max': seq_max
            })
        
        return features
    
    # =========================================================================
    # INTEGRAÇÃO COM ML 7.12
    # =========================================================================
    
    def integrar_com_ml(self, quantidade: int = 50) -> Dict:
        """
        Integração direta com o Sistema de Aprendizado ML (7.12).
        
        Fluxo:
        1. Gera combinações usando pivôs com distribuição histórica
        2. Aplica algoritmos ML para otimização (Genetic, Simulated Annealing)
        3. Usa Thompson Sampling para selecionar melhores estratégias
        4. Retorna pool híbrido otimizado
        
        Args:
            quantidade: Número de combinações finais desejadas
            
        Returns:
            Dict com combinações otimizadas e métricas
        """
        import sys
        from pathlib import Path
        
        # Adicionar path do sistemas
        dir_sistemas = Path(__file__).parent.parent / 'sistemas'
        if str(dir_sistemas) not in sys.path:
            sys.path.insert(0, str(dir_sistemas))
        
        print("\n" + "=" * 70)
        print("🤖 INTEGRAÇÃO PIVÔS + ML 7.12")
        print("=" * 70)
        
        try:
            from sistema_aprendizado_ml import SistemaAprendizadoML
            
            # Inicializar sistema ML
            sistema_ml = SistemaAprendizadoML(tamanho_janela=30, combos_por_estrategia=5)
            sistema_ml.carregar_historico()
            
            print("✅ Sistema ML 7.12 carregado com sucesso!")
            print(f"   📊 {sistema_ml.total_concursos} concursos no histórico")
            
        except ImportError as e:
            print(f"⚠️ Não foi possível importar ML 7.12: {e}")
            print("   Usando geração baseada apenas em pivôs...")
            return self._gerar_sem_ml(quantidade)
        
        # ETAPA 1: Gerar pool inicial com pivôs
        print("\n📊 ETAPA 1: Gerando pool inicial com pivôs...")
        pool_inicial_size = max(quantidade * 10, 100)  # Mínimo 100 para diversidade
        pool_pivo = self.gerar_combinacoes_pivo(pool_inicial_size, True)
        print(f"   ✅ {len(pool_pivo)} combinações geradas com distribuição de pivôs")
        
        # ETAPA 2: Extrair features do ML
        print("\n🧠 ETAPA 2: Extraindo features do ML...")
        # Construir janela de resultados para o ML
        janela = []
        for concurso, numeros in self.resultados[-30:]:
            janela.append({
                'concurso': concurso,
                'numeros': list(numeros)
            })
        features_ml = sistema_ml._calcular_features_avancados(janela)
        print(f"   ✅ Features extraídos: {len(features_ml)} números analisados")
        
        # ETAPA 3: Aplicar algoritmo genético no pool
        print("\n🧬 ETAPA 3: Aplicando algoritmo genético...")
        from sistema_aprendizado_ml import GeneticIndividual
        
        # Converter pool para indivíduos genéticos
        populacao = []
        for comb in pool_pivo:
            individuo = GeneticIndividual(genes=comb)
            # Calcular fitness baseado em características
            individuo.fitness = self._calcular_fitness_hibrido(comb, features_ml)
            populacao.append(individuo)
        
        # Evoluir por algumas gerações
        n_geracoes = 10
        for gen in range(n_geracoes):
            # Ordenar por fitness
            populacao.sort(key=lambda x: x.fitness, reverse=True)
            
            # Manter elite
            elite_size = int(len(populacao) * 0.2)
            nova_pop = populacao[:elite_size]
            
            # Crossover e mutação
            while len(nova_pop) < len(populacao):
                p1, p2 = random.sample(populacao[:elite_size * 2], 2)
                filho = GeneticIndividual.crossover(p1, p2)
                
                # Garantir que respeita pivôs
                filho = self._ajustar_para_pivos(filho)
                filho.fitness = self._calcular_fitness_hibrido(filho.genes, features_ml)
                
                if random.random() < 0.15:  # Mutação
                    filho = filho.mutate(0.1)
                    filho = self._ajustar_para_pivos(filho)
                    filho.fitness = self._calcular_fitness_hibrido(filho.genes, features_ml)
                
                nova_pop.append(filho)
            
            populacao = nova_pop
            
            if (gen + 1) % 3 == 0:
                melhor = max(p.fitness for p in populacao)
                print(f"   Geração {gen + 1}/{n_geracoes}: Melhor fitness = {melhor:.4f}")
        
        # ETAPA 4: Selecionar melhores e diversificar
        print("\n🎯 ETAPA 4: Selecionando e diversificando...")
        populacao.sort(key=lambda x: x.fitness, reverse=True)
        
        pool_final = []
        # Ajustar threshold de similaridade baseado na quantidade desejada
        # Menos restritivo se precisar de mais combinações
        threshold_inicial = 11  # Máximo 11 números em comum
        
        for threshold in range(threshold_inicial, 14):  # Tenta de 11 a 13
            pool_final = []
            for ind in populacao:
                comb = sorted(ind.genes)
                
                # Verificar diversidade
                muito_similar = False
                for selecionada in pool_final:
                    if len(set(comb) & set(selecionada)) > threshold:
                        muito_similar = True
                        break
                
                if not muito_similar:
                    pool_final.append(comb)
                    if len(pool_final) >= quantidade:
                        break
            
            if len(pool_final) >= quantidade:
                break
        
        # Se ainda não tem suficiente, pega as melhores sem filtro
        if len(pool_final) < quantidade:
            for ind in populacao:
                comb = sorted(ind.genes)
                if comb not in pool_final:
                    pool_final.append(comb)
                    if len(pool_final) >= quantidade:
                        break
        
        # ETAPA 5: Estatísticas finais
        print("\n📈 ETAPA 5: Calculando estatísticas...")
        stats = self._calcular_stats_pool(pool_final, features_ml)
        
        print(f"\n✅ INTEGRAÇÃO CONCLUÍDA!")
        print(f"   🎯 {len(pool_final)} combinações otimizadas")
        print(f"   📊 Fitness médio: {stats['fitness_medio']:.4f}")
        print(f"   🔥 Cobertura de quentes: {stats['cobertura_quentes']:.1f}%")
        print(f"   📉 Cobertura de atrasados: {stats['cobertura_atrasados']:.1f}%")
        
        return {
            'combinacoes': pool_final,
            'stats': stats,
            'metodo': 'pivo_ml_hibrido',
            'pivôs_usados': self.numeros_pivo,
            'distribuicao_pivo': self.distribuicao_pivo
        }
    
    def _gerar_sem_ml(self, quantidade: int) -> Dict:
        """Fallback: gera sem ML."""
        pool = self.gerar_pool_otimizado(quantidade)
        return {
            'combinacoes': pool,
            'stats': {},
            'metodo': 'pivo_apenas',
            'pivos_usados': self.numeros_pivo
        }
    
    def _calcular_fitness_hibrido(self, comb: List[int], features: Dict) -> float:
        """
        Calcula fitness híbrido: pivôs + ML.
        
        Componentes:
        1. Respeito à distribuição de pivôs (40%)
        2. Frequência dos números (20%)
        3. Atraso balanceado (20%)
        4. Distribuição estatística (20%)
        """
        fitness = 0.0
        comb_set = set(comb)
        pivo_set = set(self.numeros_pivo)
        
        # 1. Score de pivôs (40%)
        qtd_pivos = len(comb_set & pivo_set)
        # Ideal: estar na faixa 8-11
        if 8 <= qtd_pivos <= 11:
            pivo_score = 1.0
        elif qtd_pivos == 7 or qtd_pivos == 12:
            pivo_score = 0.7
        else:
            pivo_score = 0.3
        fitness += pivo_score * 0.4
        
        # 2. Score de frequência (20%)
        freq = features.get('frequencia', {})
        if freq:
            max_freq = max(freq.values())
            freq_score = sum(freq.get(n, 0) for n in comb) / (15 * max_freq) if max_freq > 0 else 0.5
            fitness += freq_score * 0.2
        else:
            fitness += 0.1
        
        # 3. Score de atraso balanceado (20%)
        atraso = features.get('atraso', {})
        if atraso:
            max_atraso = max(atraso.values()) if atraso.values() else 1
            # Queremos alguns atrasados, não todos
            atraso_score = sum(min(atraso.get(n, 0), 5) for n in comb) / (15 * 5)
            fitness += atraso_score * 0.2
        else:
            fitness += 0.1
        
        # 4. Distribuição estatística (20%)
        soma = sum(comb)
        pares = sum(1 for n in comb if n % 2 == 0)
        baixos = sum(1 for n in comb if n <= 12)
        
        # Soma ideal: 180-210
        if 180 <= soma <= 210:
            soma_score = 1.0
        elif 165 <= soma <= 225:
            soma_score = 0.7
        else:
            soma_score = 0.3
        
        # Paridade ideal: 7-8
        if 7 <= pares <= 8:
            par_score = 1.0
        elif 6 <= pares <= 9:
            par_score = 0.7
        else:
            par_score = 0.3
        
        # Baixos/Altos ideal: 7-8
        if 7 <= baixos <= 8:
            baixo_score = 1.0
        elif 6 <= baixos <= 9:
            baixo_score = 0.7
        else:
            baixo_score = 0.3
        
        dist_score = (soma_score + par_score + baixo_score) / 3
        fitness += dist_score * 0.2
        
        return fitness
    
    def _ajustar_para_pivos(self, individuo) -> 'GeneticIndividual':
        """Ajusta indivíduo para respeitar distribuição de pivôs."""
        from sistema_aprendizado_ml import GeneticIndividual
        
        genes = list(individuo.genes)
        pivo_set = set(self.numeros_pivo)
        complemento_set = set(n for n in TODOS_NUMEROS if n not in pivo_set)
        
        qtd_pivos_atual = sum(1 for g in genes if g in pivo_set)
        
        # Ajustar para faixa 8-11
        if qtd_pivos_atual < 8:
            # Adicionar mais pivôs
            nao_pivos = [g for g in genes if g not in pivo_set]
            pivos_disponiveis = [p for p in pivo_set if p not in genes]
            
            while qtd_pivos_atual < 8 and nao_pivos and pivos_disponiveis:
                # Trocar um não-pivô por um pivô
                remover = random.choice(nao_pivos)
                adicionar = random.choice(pivos_disponiveis)
                
                genes.remove(remover)
                genes.append(adicionar)
                nao_pivos.remove(remover)
                pivos_disponiveis.remove(adicionar)
                qtd_pivos_atual += 1
        
        elif qtd_pivos_atual > 11:
            # Remover alguns pivôs
            pivos_na_comb = [g for g in genes if g in pivo_set]
            compl_disponiveis = [c for c in complemento_set if c not in genes]
            
            while qtd_pivos_atual > 11 and pivos_na_comb and compl_disponiveis:
                remover = random.choice(pivos_na_comb)
                adicionar = random.choice(compl_disponiveis)
                
                genes.remove(remover)
                genes.append(adicionar)
                pivos_na_comb.remove(remover)
                compl_disponiveis.remove(adicionar)
                qtd_pivos_atual -= 1
        
        return GeneticIndividual(genes=sorted(genes), generation=individuo.generation)
    
    def _calcular_stats_pool(self, pool: List[List[int]], features: Dict) -> Dict:
        """Calcula estatísticas do pool final."""
        if not pool:
            return {}
        
        freq = features.get('frequencia', {})
        atraso = features.get('atraso', {})
        
        # Identificar quentes e atrasados
        if freq:
            max_freq = max(freq.values())
            quentes = set(n for n in TODOS_NUMEROS if freq.get(n, 0) >= max_freq * 0.6)
        else:
            quentes = set()
        
        if atraso:
            atrasados = set(n for n in TODOS_NUMEROS if atraso.get(n, 0) >= 5)
        else:
            atrasados = set()
        
        # Calcular métricas
        fitness_lista = [self._calcular_fitness_hibrido(c, features) for c in pool]
        
        cobertura_quentes = 0
        cobertura_atrasados = 0
        
        for comb in pool:
            comb_set = set(comb)
            if quentes:
                cobertura_quentes += len(comb_set & quentes) / len(quentes) * 100 / len(pool)
            if atrasados:
                cobertura_atrasados += len(comb_set & atrasados) / len(atrasados) * 100 / len(pool)
        
        return {
            'fitness_medio': sum(fitness_lista) / len(fitness_lista),
            'fitness_max': max(fitness_lista),
            'fitness_min': min(fitness_lista),
            'cobertura_quentes': cobertura_quentes,
            'cobertura_atrasados': cobertura_atrasados,
            'total_combinacoes': len(pool)
        }
    
    def _calcular_fitness_numero(self, numero: int, features: Dict) -> float:
        """
        Calcula o fitness individual de um número.
        
        Critérios:
        1. Frequência (40%)
        2. Atraso baixo = quente (30%)
        3. É pivô (30%)
        
        Returns:
            Score de fitness do número (0 a 1)
        """
        fitness = 0.0
        
        # 1. Score de frequência (40%)
        freq = features.get('frequencia', {})
        if freq:
            max_freq = max(freq.values()) if freq.values() else 1
            freq_score = freq.get(numero, 0) / max_freq
            fitness += freq_score * 0.4
        else:
            fitness += 0.2
        
        # 2. Score de atraso (quente = baixo atraso) (30%)
        atraso = features.get('atraso', {})
        if atraso:
            atraso_num = atraso.get(numero, 0)
            # Quanto menor o atraso, maior o score
            if atraso_num <= 2:
                atraso_score = 1.0
            elif atraso_num <= 5:
                atraso_score = 0.7
            elif atraso_num <= 10:
                atraso_score = 0.4
            else:
                atraso_score = 0.2
            fitness += atraso_score * 0.3
        else:
            fitness += 0.15
        
        # 3. É pivô? (30%)
        if self.numeros_pivo and numero in self.numeros_pivo:
            fitness += 0.3
        
        return fitness
    
    def gerar_anticombinacoes(self, combinacoes: List[List[int]], features: Dict = None) -> Dict:
        """
        🔄 GERADOR DE ANTICOMBINAÇÕES
        
        Conceito radical:
        - Para cada combinação (15 números), os 10 números NÃO usados
          se tornam FIXOS na anticombinação
        - Os 5 números restantes são os 5 MELHORES (por fitness) da combinação original
        
        Fórmula:
        Anticombinação = 10 números fora + 5 melhores da original
        
        Args:
            combinacoes: Lista de combinações originais
            features: Features ML para calcular fitness (opcional)
            
        Returns:
            Dict com anticombinações e estatísticas
        """
        print("\n" + "=" * 70)
        print("🔄 GERADOR DE ANTICOMBINAÇÕES (CONCEITO RADICAL)")
        print("=" * 70)
        
        # VALIDAÇÃO: Precisa ter PIVO definido!
        if not self.numeros_pivo or len(self.numeros_pivo) < 1:
            print("❌ ATENÇÃO: Defina um PIVO para gerar ANTIPIVO!")
            if combinacoes:
                print("   Usando combinações fornecidas como fallback...")
            else:
                return {}
        
        # ===== CÁLCULO FLEXÍVEL: Qualquer tamanho de PIVO =====
        tamanho_pivo = len(self.numeros_pivo) if self.numeros_pivo else 15
        pivo_set = set(self.numeros_pivo) if self.numeros_pivo else set()
        
        # Números FORA do PIVO
        numeros_fora_pivo = sorted([n for n in TODOS_NUMEROS if n not in pivo_set])
        qtd_fora = len(numeros_fora_pivo)  # = 25 - tamanho_pivo
        
        # Quantos precisamos pegar do PIVO para completar 15?
        qtd_do_pivo = max(0, 15 - qtd_fora)
        
        # Se FORA >= 15, pegamos só 15 FORA e 0 do PIVO
        qtd_fora_usar = min(15, qtd_fora)
        
        print(f"📐 PIVO com {tamanho_pivo} números → {qtd_fora} FORA + {qtd_do_pivo} do PIVO")
        print(f"🎯 Fórmula: Anticombinação = {qtd_fora_usar} FORA (fixos) + {qtd_do_pivo} melhores do PIVO")
        print()
        
        # Se não tem features, calcular
        if features is None:
            print("📊 Calculando features para fitness...")
            if not self.resultados:
                self.carregar_resultados()
            
            # Calcular features básicos
            from collections import Counter
            
            freq_counter = Counter()
            atraso = {}
            ultimo_aparecimento = {}
            
            for idx, (concurso, nums) in enumerate(self.resultados):
                for n in nums:
                    freq_counter[n] += 1
                    ultimo_aparecimento[n] = idx
            
            # Calcular atraso (distância do último aparecimento)
            ultimo_idx = len(self.resultados) - 1
            for n in TODOS_NUMEROS:
                if n in ultimo_aparecimento:
                    atraso[n] = ultimo_idx - ultimo_aparecimento[n]
                else:
                    atraso[n] = ultimo_idx
            
            features = {
                'frequencia': dict(freq_counter),
                'atraso': atraso
            }
        
        anticombinacoes = []
        detalhes = []
        
        # ===== MODO CORRETO: Usar PIVO definido (qualquer tamanho) =====
        if self.numeros_pivo and len(self.numeros_pivo) >= 1:
            
            # Os números FORA do PIVO (podem ser de 5 a 24 dependendo do PIVO)
            # Usamos no máximo 15 (para caber na combinação)
            fora_fixos = numeros_fora_pivo[:qtd_fora_usar]
            
            print(f"🎯 PIVO DEFINIDO ({tamanho_pivo}): {sorted(self.numeros_pivo)}")
            print(f"🔒 {len(fora_fixos)} FIXOS (fora do PIVO): {fora_fixos}")
            
            if qtd_do_pivo > 0:
                print(f"📊 + {qtd_do_pivo} melhores do PIVO para completar 15")
            
            print(f"📊 Gerando {len(combinacoes) if combinacoes else 50} anticombinações...")
            print("-" * 70)
            
            # Se precisamos de números do PIVO, calcular fitness
            # IMPORTANTE: Ordenamos do PIOR para o MELHOR!
            # Porque queremos EXCLUIR os piores do PIVO, não os melhores
            fitness_pivo = []
            if qtd_do_pivo > 0:
                for n in self.numeros_pivo:
                    fit = self._calcular_fitness_numero(n, features)
                    fitness_pivo.append((n, fit))
                # Ordenar CRESCENTE (piores primeiro) - esses serão excluídos na anti-combinação
                fitness_pivo.sort(key=lambda x: x[1], reverse=False)
            
            # Quantidade de anticombinações a gerar
            qtd = len(combinacoes) if combinacoes else 50
            
            for i in range(qtd):
                # Selecionar do PIVO com variação (se precisar)
                if qtd_do_pivo == 0:
                    # PIVO pequeno (<=10): só usa FORA
                    nums_do_pivo = []
                elif qtd_do_pivo >= tamanho_pivo:
                    # PIVO muito grande (>20): precisa de todos do PIVO
                    nums_do_pivo = list(self.numeros_pivo)
                else:
                    # Caso normal: pegar os PIORES do PIVO (para excluir)
                    # Assim os MELHORES do PIVO ficam disponíveis para jogar!
                    pool_size = min(len(fitness_pivo), max(qtd_do_pivo + 3, int(tamanho_pivo * 0.7)))
                    worst_pool = [n for n, _ in fitness_pivo[:pool_size]]  # Piores estão no início
                    
                    if i == 0:
                        # Primeira: os piores exatos
                        nums_do_pivo = [n for n, _ in fitness_pivo[:qtd_do_pivo]]
                    else:
                        # Variações entre os piores
                        nums_do_pivo = sorted(random.sample(worst_pool, qtd_do_pivo))
                
                # Montar anticombinação: FORA fixos + PIORES do PIVO
                anticomb = sorted(fora_fixos + nums_do_pivo)
                
                # Garantir exatamente 15 números
                if len(anticomb) != 15:
                    print(f"⚠️ Erro: anticomb tem {len(anticomb)} números!")
                    continue
                
                if anticomb not in anticombinacoes:
                    anticombinacoes.append(anticomb)
                    
                    detalhe = {
                        'pivo_base': sorted(self.numeros_pivo),
                        'tamanho_pivo': tamanho_pivo,
                        'numeros_fora_fixos': fora_fixos,
                        'nums_do_pivo': nums_do_pivo,
                        'anticombinacao': anticomb
                    }
                    detalhes.append(detalhe)
                    
                    # Mostrar primeiras 5
                    if len(anticombinacoes) <= 5:
                        print(f"\n🔄 AntiPivo {len(anticombinacoes)}:")
                        print(f"   {len(fora_fixos)} FORA:   {','.join(f'{n:02d}' for n in fora_fixos)}")
                        if nums_do_pivo:
                            print(f"   {len(nums_do_pivo)} PIORES do PIVO: {','.join(f'{n:02d}' for n in nums_do_pivo)}")
                        print(f"   ANTI:     {','.join(f'{n:02d}' for n in anticomb)}")
            
            print(f"\n   ✅ {len(anticombinacoes)} anticombinações únicas geradas")
            
            # Mostrar garantia matemática
            print(f"\n📊 LÓGICA DA EXCLUSÃO:")
            print(f"   PIVO tem {tamanho_pivo} números (média 8-11 acertos)")
            print(f"   Anti-combinação = {qtd_fora_usar} FORA do PIVO + {qtd_do_pivo} PIORES do PIVO")
            print(f"   → Exclui: números fora do grupo bom + os menos prováveis dentro do grupo")
            print(f"   → Mantém livres: os MELHORES do PIVO para suas combinações!")
        
        # ===== MODO FALLBACK: Usar combinações fornecidas =====
        elif combinacoes:
            print(f"📊 Processando {len(combinacoes)} combinações (modo fallback)...")
            print("-" * 70)
            
            for i, comb in enumerate(combinacoes, 1):
                comb_set = set(comb)
                
                # 1. Identificar os 10 números FORA da combinação (FIXOS - esses não vão sair)
                numeros_fora = sorted([n for n in TODOS_NUMEROS if n not in comb_set])
                
                # 2. Calcular fitness de cada número DA combinação
                fitness_numeros = []
                for n in comb:
                    fit = self._calcular_fitness_numero(n, features)
                    fitness_numeros.append((n, fit))
                
                # 3. Ordenar por fitness CRESCENTE e pegar os 5 PIORES
                # Assim excluímos os piores e mantemos os melhores livres para jogar!
                fitness_numeros.sort(key=lambda x: x[1], reverse=False)  # Crescente!
                cinco_piores = [n for n, _ in fitness_numeros[:5]]
                
                # 4. Montar anticombinação: 10 fora + 5 piores da combinação
                anticomb = sorted(numeros_fora + cinco_piores)
                
                anticombinacoes.append(anticomb)
                
                # Guardar detalhes
                detalhe = {
                    'combinacao_original': sorted(comb),
                    'numeros_fora_fixos': numeros_fora,
                    'cinco_piores': cinco_piores,
                    'fitness_cinco': [f for n, f in fitness_numeros[:5]],
                    'anticombinacao': anticomb
                }
                detalhes.append(detalhe)
                
                # Mostrar progresso para as primeiras 5
                if i <= 5:
                    print(f"\n🎯 Combinação {i}:")
                    print(f"   Original:    {','.join(f'{n:02d}' for n in sorted(comb))}")
                    print(f"   Fora (10):   {','.join(f'{n:02d}' for n in numeros_fora)}")
                    print(f"   5 Piores:    {','.join(f'{n:02d}' for n in cinco_piores)} (fitness: {[f'{f:.3f}' for n, f in fitness_numeros[:5]]})")
                    print(f"   ANTI:        {','.join(f'{n:02d}' for n in anticomb)}")
            
            if len(combinacoes) > 5:
                print(f"\n   ... e mais {len(combinacoes) - 5} anticombinações geradas")
        
        # Estatísticas
        print("\n" + "=" * 70)
        print("📈 ESTATÍSTICAS DAS ANTICOMBINAÇÕES")
        print("=" * 70)
        
        # Verificar sobreposição entre anticombinações
        sobreposicao_media = 0
        if len(anticombinacoes) > 1:
            count = 0
            for i in range(len(anticombinacoes)):
                for j in range(i+1, len(anticombinacoes)):
                    sobreposicao = len(set(anticombinacoes[i]) & set(anticombinacoes[j]))
                    sobreposicao_media += sobreposicao
                    count += 1
            sobreposicao_media /= count
        
        # Contar números mais frequentes nas anticombinações
        from collections import Counter
        num_counter = Counter()
        for ac in anticombinacoes:
            for n in ac:
                num_counter[n] += 1
        
        mais_frequentes = num_counter.most_common(10)
        
        print(f"📊 Total de anticombinações: {len(anticombinacoes)}")
        print(f"🔄 Sobreposição média entre anti's: {sobreposicao_media:.1f} números")
        print(f"\n🔥 TOP 10 números mais frequentes nas ANTI's:")
        for n, freq in mais_frequentes:
            barra = "█" * int(freq / len(anticombinacoes) * 20)
            print(f"   {n:2d}: {freq:3d}x ({freq/len(anticombinacoes)*100:.0f}%) {barra}")
        
        # Verificar quantos pivôs estão nas anticombinações
        if self.numeros_pivo:
            pivos_em_anti = []
            for ac in anticombinacoes:
                qtd = len(set(ac) & set(self.numeros_pivo))
                pivos_em_anti.append(qtd)
            print(f"\n🎯 Pivôs nas anticombinações: média {sum(pivos_em_anti)/len(pivos_em_anti):.1f}")
        
        print("\n✅ ANTICOMBINAÇÕES GERADAS COM SUCESSO!")
        
        return {
            'anticombinacoes': anticombinacoes,
            'detalhes': detalhes,
            'stats': {
                'total': len(anticombinacoes),
                'sobreposicao_media': sobreposicao_media,
                'numeros_mais_frequentes': mais_frequentes
            }
        }
    
    def exportar_anticombinacoes(self, resultado_anti: Dict, nome_arquivo: str = None) -> str:
        """
        Exporta anticombinações para arquivo TXT.
        
        Formato limpo: apenas números separados por vírgula.
        """
        if not resultado_anti or not resultado_anti.get('anticombinacoes'):
            print("❌ Nenhuma anticombinação para exportar!")
            return ""
        
        anticombinacoes = resultado_anti['anticombinacoes']
        
        # Diretório de exportação
        diretorio = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite"
        
        # Nome do arquivo
        if not nome_arquivo:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"anticombinacoes_pivo_{timestamp}.txt"
        
        caminho = os.path.join(diretorio, nome_arquivo)
        
        # Escrever arquivo (formato limpo)
        with open(caminho, 'w', encoding='utf-8') as f:
            for anti in anticombinacoes:
                linha = ','.join(f'{n:02d}' for n in sorted(anti))
                f.write(linha + '\n')
        
        print(f"\n💾 ANTICOMBINAÇÕES EXPORTADAS!")
        print(f"   📁 Arquivo: {caminho}")
        print(f"   📊 Total: {len(anticombinacoes)} anticombinações")
        
        return caminho
    
    # =========================================================================
    # 🔬 VALIDAÇÃO E PATTERN MINING PARA ANTICOMBINAÇÕES
    # =========================================================================
    
    def validar_anticombinacoes_historico(self, n_concursos: int = 100) -> Dict:
        """
        🔬 VALIDAÇÃO DE ANTICOMBINAÇÕES COM BACKTESTING
        
        Testa diferentes estratégias para escolher as 5 fixas:
        1. FITNESS (algoritmo genético)
        2. QUENTES (mais frequentes recentes)
        3. ATRASADOS (maior atraso)
        4. PARES_ATRASADOS (pares com maior atraso combinado)
        5. TRIOS_ATRASADOS (trios com maior atraso combinado)
        6. HIBRIDO (mix de quentes + atrasados)
        
        Para cada estratégia, mede:
        - Acertos das 10 antipivo
        - Acertos das 5 fixas
        - Total de acertos
        - Média e distribuição
        
        Args:
            n_concursos: Quantos concursos testar (do mais recente para trás)
            
        Returns:
            Dict com resultados de cada estratégia
        """
        print("\n" + "=" * 70)
        print("🔬 VALIDAÇÃO DE ANTICOMBINAÇÕES - PATTERN MINING")
        print("=" * 70)
        print("📊 Testando diferentes estratégias para escolher as 5 FIXAS")
        print("🎯 Comparando com resultados REAIS da tabela Resultados_INT")
        print()
        
        if not self.resultados:
            self.carregar_resultados()
        
        if not self.numeros_pivo:
            print("❌ Defina os números pivô primeiro!")
            return {}
        
        # Estratégias para testar
        estrategias = {
            'FITNESS': self._selecionar_5_por_fitness,
            'QUENTES': self._selecionar_5_mais_quentes,
            'ATRASADOS': self._selecionar_5_mais_atrasados,
            'PARES_ATRASADOS': self._selecionar_5_pares_atrasados,
            'TRIOS_ATRASADOS': self._selecionar_5_trios_atrasados,
            'HIBRIDO': self._selecionar_5_hibrido
        }
        
        # Resultados por estratégia
        resultados = {nome: {
            'acertos_10_anti': [],
            'acertos_5_fixas': [],
            'acertos_total': [],
            'detalhes': []
        } for nome in estrategias}
        
        total_concursos = len(self.resultados)
        inicio = max(50, total_concursos - n_concursos)  # Precisa de histórico
        
        print(f"📊 Testando {total_concursos - inicio} concursos")
        print(f"   Início: concurso {self.resultados[inicio][0]}")
        print(f"   Fim: concurso {self.resultados[-1][0]}")
        print()
        print("⏳ Processando backtesting...")
        
        # Para cada concurso (do mais antigo para o mais recente dentro da janela)
        for idx in range(inicio, total_concursos):
            concurso_atual, resultado_real = self.resultados[idx]
            resultado_real_set = set(resultado_real)
            
            # Histórico até este ponto (sem incluir o atual)
            historico = self.resultados[:idx]
            
            # Calcular features baseados no histórico
            features = self._calcular_features_janela(historico[-30:])
            
            # Gerar uma combinação base (simulando o que faríamos)
            # Usar os últimos resultados como "combinação original" para derivar antipivo
            if idx > 0:
                _, comb_anterior = self.resultados[idx - 1]
                comb_anterior = list(comb_anterior)
            else:
                continue
            
            # Os 10 antipivo são os números FORA da combinação anterior
            numeros_fora = sorted([n for n in TODOS_NUMEROS if n not in comb_anterior])
            
            # Testar cada estratégia para selecionar as 5 fixas
            for nome_estrategia, func_selecao in estrategias.items():
                # Selecionar 5 fixas usando a estratégia
                cinco_fixas = func_selecao(comb_anterior, features, historico)
                
                # Montar anticombinação: 10 fora + 5 fixas
                anticomb = sorted(numeros_fora + cinco_fixas)
                anticomb_set = set(anticomb)
                
                # Calcular acertos
                acertos_total = len(anticomb_set & resultado_real_set)
                acertos_10_anti = len(set(numeros_fora) & resultado_real_set)
                acertos_5_fixas = len(set(cinco_fixas) & resultado_real_set)
                
                # Guardar resultados
                resultados[nome_estrategia]['acertos_10_anti'].append(acertos_10_anti)
                resultados[nome_estrategia]['acertos_5_fixas'].append(acertos_5_fixas)
                resultados[nome_estrategia]['acertos_total'].append(acertos_total)
                resultados[nome_estrategia]['detalhes'].append({
                    'concurso': concurso_atual,
                    'resultado_real': list(resultado_real),
                    'anticomb': anticomb,
                    'cinco_fixas': cinco_fixas,
                    'acertos': acertos_total
                })
            
            # Progresso
            if (idx - inicio + 1) % 50 == 0:
                print(f"   Processados: {idx - inicio + 1}/{total_concursos - inicio}")
        
        # Calcular estatísticas
        print("\n" + "=" * 70)
        print("📈 RESULTADOS DO BACKTESTING")
        print("=" * 70)
        
        ranking = []
        
        for nome, dados in resultados.items():
            if not dados['acertos_total']:
                continue
                
            media_total = sum(dados['acertos_total']) / len(dados['acertos_total'])
            media_10_anti = sum(dados['acertos_10_anti']) / len(dados['acertos_10_anti'])
            media_5_fixas = sum(dados['acertos_5_fixas']) / len(dados['acertos_5_fixas'])
            
            # Distribuição de acertos
            dist = Counter(dados['acertos_total'])
            
            # Prêmios (11+ acertos)
            premios_11 = sum(1 for a in dados['acertos_total'] if a >= 11)
            premios_12 = sum(1 for a in dados['acertos_total'] if a >= 12)
            premios_13 = sum(1 for a in dados['acertos_total'] if a >= 13)
            premios_14 = sum(1 for a in dados['acertos_total'] if a >= 14)
            premios_15 = sum(1 for a in dados['acertos_total'] if a == 15)
            
            ranking.append({
                'estrategia': nome,
                'media_total': media_total,
                'media_10_anti': media_10_anti,
                'media_5_fixas': media_5_fixas,
                'premios_11': premios_11,
                'premios_12': premios_12,
                'premios_13': premios_13,
                'premios_14': premios_14,
                'premios_15': premios_15,
                'total_testes': len(dados['acertos_total']),
                'distribuicao': dict(dist)
            })
        
        # Ordenar por média total
        ranking.sort(key=lambda x: x['media_total'], reverse=True)
        
        # Exibir resultados
        print(f"\n{'ESTRATÉGIA':<20} {'MÉDIA':>8} {'10 ANTI':>8} {'5 FIXAS':>8} {'11+':>6} {'12+':>6} {'13+':>6} {'14+':>6} {'15':>5}")
        print("-" * 85)
        
        for r in ranking:
            print(f"{r['estrategia']:<20} {r['media_total']:>8.2f} {r['media_10_anti']:>8.2f} {r['media_5_fixas']:>8.2f} "
                  f"{r['premios_11']:>6} {r['premios_12']:>6} {r['premios_13']:>6} {r['premios_14']:>6} {r['premios_15']:>5}")
        
        # Melhor estratégia
        melhor = ranking[0]
        print("\n" + "=" * 70)
        print(f"🏆 MELHOR ESTRATÉGIA: {melhor['estrategia']}")
        print("=" * 70)
        print(f"   📊 Média de acertos: {melhor['media_total']:.2f}")
        print(f"   📊 Média 10 antipivo: {melhor['media_10_anti']:.2f}")
        print(f"   📊 Média 5 fixas: {melhor['media_5_fixas']:.2f}")
        print(f"   🎯 Prêmios 11+: {melhor['premios_11']} ({melhor['premios_11']/melhor['total_testes']*100:.1f}%)")
        print(f"   🎯 Prêmios 12+: {melhor['premios_12']} ({melhor['premios_12']/melhor['total_testes']*100:.1f}%)")
        print(f"   🎯 Prêmios 13+: {melhor['premios_13']} ({melhor['premios_13']/melhor['total_testes']*100:.1f}%)")
        
        # Distribuição detalhada da melhor
        print(f"\n📈 DISTRIBUIÇÃO DE ACERTOS ({melhor['estrategia']}):")
        for acertos in sorted(melhor['distribuicao'].keys()):
            qtd = melhor['distribuicao'][acertos]
            pct = qtd / melhor['total_testes'] * 100
            barra = "█" * int(pct / 2)
            print(f"   {acertos:2d} acertos: {qtd:4d} ({pct:5.1f}%) {barra}")
        
        return {
            'ranking': ranking,
            'melhor_estrategia': melhor['estrategia'],
            'resultados_detalhados': resultados
        }
    
    def _calcular_features_janela(self, janela: List) -> Dict:
        """Calcula features para uma janela de resultados."""
        freq = Counter()
        ultimo_aparecimento = {}
        
        for idx, (_, nums) in enumerate(janela):
            for n in nums:
                freq[n] += 1
                ultimo_aparecimento[n] = idx
        
        # Atraso
        ultimo_idx = len(janela) - 1
        atraso = {}
        for n in TODOS_NUMEROS:
            if n in ultimo_aparecimento:
                atraso[n] = ultimo_idx - ultimo_aparecimento[n]
            else:
                atraso[n] = ultimo_idx + 1
        
        return {
            'frequencia': dict(freq),
            'atraso': atraso,
            'janela_size': len(janela)
        }
    
    def _selecionar_5_por_fitness(self, comb: List[int], features: Dict, historico: List) -> List[int]:
        """Seleciona 5 números por FITNESS (algoritmo genético)."""
        fitness_nums = []
        for n in comb:
            fit = self._calcular_fitness_numero(n, features)
            fitness_nums.append((n, fit))
        
        fitness_nums.sort(key=lambda x: x[1], reverse=True)
        return [n for n, _ in fitness_nums[:5]]
    
    def _selecionar_5_mais_quentes(self, comb: List[int], features: Dict, historico: List) -> List[int]:
        """Seleciona 5 números mais QUENTES (menor atraso)."""
        atraso = features.get('atraso', {})
        atraso_nums = [(n, atraso.get(n, 999)) for n in comb]
        atraso_nums.sort(key=lambda x: x[1])  # Menor atraso = mais quente
        return [n for n, _ in atraso_nums[:5]]
    
    def _selecionar_5_mais_atrasados(self, comb: List[int], features: Dict, historico: List) -> List[int]:
        """Seleciona 5 números mais ATRASADOS (maior atraso)."""
        atraso = features.get('atraso', {})
        atraso_nums = [(n, atraso.get(n, 0)) for n in comb]
        atraso_nums.sort(key=lambda x: x[1], reverse=True)  # Maior atraso
        return [n for n, _ in atraso_nums[:5]]
    
    def _selecionar_5_pares_atrasados(self, comb: List[int], features: Dict, historico: List) -> List[int]:
        """
        Seleciona 5 números baseado em PARES ATRASADOS.
        Encontra os pares com maior atraso combinado e seleciona seus números.
        """
        atraso = features.get('atraso', {})
        
        # Calcular score de pares
        pares_score = []
        for i, n1 in enumerate(comb):
            for n2 in comb[i+1:]:
                score = atraso.get(n1, 0) + atraso.get(n2, 0)
                pares_score.append(((n1, n2), score))
        
        # Ordenar por maior score
        pares_score.sort(key=lambda x: x[1], reverse=True)
        
        # Pegar números dos melhores pares
        selecionados = set()
        for (n1, n2), _ in pares_score:
            selecionados.add(n1)
            selecionados.add(n2)
            if len(selecionados) >= 5:
                break
        
        return sorted(list(selecionados))[:5]
    
    def _selecionar_5_trios_atrasados(self, comb: List[int], features: Dict, historico: List) -> List[int]:
        """
        Seleciona 5 números baseado em TRIOS ATRASADOS.
        Encontra os trios com maior atraso combinado e seleciona seus números.
        """
        atraso = features.get('atraso', {})
        
        # Calcular score de trios
        trios_score = []
        for i, n1 in enumerate(comb):
            for j, n2 in enumerate(comb[i+1:], i+1):
                for n3 in comb[j+1:]:
                    score = atraso.get(n1, 0) + atraso.get(n2, 0) + atraso.get(n3, 0)
                    trios_score.append(((n1, n2, n3), score))
        
        # Ordenar por maior score
        trios_score.sort(key=lambda x: x[1], reverse=True)
        
        # Pegar números dos melhores trios
        selecionados = set()
        for (n1, n2, n3), _ in trios_score:
            selecionados.add(n1)
            selecionados.add(n2)
            selecionados.add(n3)
            if len(selecionados) >= 5:
                break
        
        return sorted(list(selecionados))[:5]
    
    def _selecionar_5_hibrido(self, comb: List[int], features: Dict, historico: List) -> List[int]:
        """
        Seleção HÍBRIDA: 2 quentes + 2 atrasados + 1 melhor fitness.
        Busca equilíbrio entre tendências.
        """
        atraso = features.get('atraso', {})
        
        # 2 mais quentes
        atraso_nums = [(n, atraso.get(n, 999)) for n in comb]
        atraso_nums.sort(key=lambda x: x[1])
        quentes = [n for n, _ in atraso_nums[:2]]
        
        # 2 mais atrasados (excluindo os já selecionados)
        restantes = [n for n in comb if n not in quentes]
        atraso_restantes = [(n, atraso.get(n, 0)) for n in restantes]
        atraso_restantes.sort(key=lambda x: x[1], reverse=True)
        atrasados = [n for n, _ in atraso_restantes[:2]]
        
        # 1 melhor fitness (excluindo os já selecionados)
        restantes2 = [n for n in comb if n not in quentes and n not in atrasados]
        fitness_restantes = [(n, self._calcular_fitness_numero(n, features)) for n in restantes2]
        fitness_restantes.sort(key=lambda x: x[1], reverse=True)
        fitness_top = [n for n, _ in fitness_restantes[:1]]
        
        return sorted(quentes + atrasados + fitness_top)
    
    def analisar_pattern_mining_avancado(self, n_concursos: int = 200) -> Dict:
        """
        🔬 PATTERN MINING AVANÇADO
        
        Analisa padrões mais sofisticados:
        1. Sequências de números (consecutivos)
        2. Padrões par/ímpar nas 5 fixas
        3. Padrões alto/baixo nas 5 fixas
        4. Repetições do concurso anterior
        5. Números que "viram" entre posições antipivo ↔ fixas
        
        Args:
            n_concursos: Quantos concursos analisar
            
        Returns:
            Dict com padrões descobertos
        """
        print("\n" + "=" * 70)
        print("🔬 PATTERN MINING AVANÇADO - ANTICOMBINAÇÕES")
        print("=" * 70)
        
        if not self.resultados:
            self.carregar_resultados()
        
        total = len(self.resultados)
        inicio = max(30, total - n_concursos)
        
        # Padrões a analisar
        padroes = {
            'pares_nas_5': [],      # Quantos pares nas 5 fixas que acertaram
            'baixos_nas_5': [],     # Quantos baixos (1-12) nas 5 fixas que acertaram
            'consecutivos_5': [],   # Sequências consecutivas nas 5 fixas
            'repeticoes_anterior': [],  # Números que repetem do anterior
            'transicao_anti_fixa': [],  # Números que eram anti e viraram fixa
        }
        
        print(f"📊 Analisando {total - inicio} concursos...")
        
        for idx in range(inicio, total):
            concurso_atual, resultado = self.resultados[idx]
            resultado_set = set(resultado)
            
            if idx > 0:
                _, anterior = self.resultados[idx - 1]
                anterior_set = set(anterior)
                
                # Análise das 5 "melhores" do anterior que estariam nas fixas
                features = self._calcular_features_janela(self.resultados[:idx][-30:])
                fixas_simuladas = self._selecionar_5_por_fitness(list(anterior), features, self.resultados[:idx])
                fixas_set = set(fixas_simuladas)
                
                # Anti (10 fora do anterior)
                anti = set([n for n in TODOS_NUMEROS if n not in anterior_set])
                
                # 1. Pares nas 5 fixas que acertaram
                acertos_fixas = fixas_set & resultado_set
                pares_acertados = sum(1 for n in acertos_fixas if n % 2 == 0)
                padroes['pares_nas_5'].append(pares_acertados)
                
                # 2. Baixos (1-12) nas 5 fixas que acertaram
                baixos_acertados = sum(1 for n in acertos_fixas if n <= 12)
                padroes['baixos_nas_5'].append(baixos_acertados)
                
                # 3. Consecutivos nas 5 fixas
                fixas_sorted = sorted(fixas_simuladas)
                consec = 0
                for i in range(len(fixas_sorted) - 1):
                    if fixas_sorted[i+1] - fixas_sorted[i] == 1:
                        consec += 1
                padroes['consecutivos_5'].append(consec)
                
                # 4. Repetições do anterior no resultado
                repeticoes = len(anterior_set & resultado_set)
                padroes['repeticoes_anterior'].append(repeticoes)
                
                # 5. Transição: números que eram anti e agora estão no resultado
                transicao = len(anti & resultado_set)
                padroes['transicao_anti_fixa'].append(transicao)
        
        # Estatísticas
        print("\n📈 PADRÕES DESCOBERTOS:")
        print("-" * 70)
        
        for nome, valores in padroes.items():
            if valores:
                media = sum(valores) / len(valores)
                maximo = max(valores)
                minimo = min(valores)
                
                # Distribuição
                dist = Counter(valores)
                moda = dist.most_common(1)[0][0] if dist else 0
                
                print(f"\n🔹 {nome.upper()}:")
                print(f"   Média: {media:.2f} | Mín: {minimo} | Máx: {maximo} | Moda: {moda}")
                
                # Gráfico de distribuição
                for val in sorted(dist.keys()):
                    qtd = dist[val]
                    pct = qtd / len(valores) * 100
                    barra = "█" * int(pct / 3)
                    print(f"   {val:2d}: {qtd:4d} ({pct:5.1f}%) {barra}")
        
        # Insights
        print("\n" + "=" * 70)
        print("💡 INSIGHTS DO PATTERN MINING")
        print("=" * 70)
        
        media_repeticoes = sum(padroes['repeticoes_anterior']) / len(padroes['repeticoes_anterior']) if padroes['repeticoes_anterior'] else 0
        media_transicao = sum(padroes['transicao_anti_fixa']) / len(padroes['transicao_anti_fixa']) if padroes['transicao_anti_fixa'] else 0
        
        print(f"📊 Em média, {media_repeticoes:.1f} números repetem do concurso anterior")
        print(f"📊 Em média, {media_transicao:.1f} números 'antipivo' aparecem no próximo resultado")
        print(f"📊 Isso significa que os 10 antipivo têm ~{media_transicao/10*100:.0f}% de chance de acerto cada")
        
        if media_transicao > 5:
            print("\n⚠️ ALERTA: Os números 'antipivo' têm taxa de acerto MAIOR que esperado!")
            print("   Isso VALIDA o conceito de anticombinações!")
        
        return {
            'padroes': padroes,
            'insights': {
                'media_repeticoes': media_repeticoes,
                'media_transicao': media_transicao,
                'taxa_acerto_anti': media_transicao / 10
            }
        }


def menu_interativo():
    """Menu interativo para usar o analisador."""
    analisador = AnalisadorPivoSimilaridade()
    combinacoes_geradas = []  # Guardar última geração
    
    while True:
        print("\n" + "🔬" * 35)
        print("🎯 ANALISADOR DE SIMILARIDADE E PIVÔS")
        print("🔬" * 35)
        print()
        print("1️⃣  📊 Análise de Similaridade (Resultado x Resultado)")
        print("2️⃣  🎯 Definir Números Pivô (5-20 números)")
        print("3️⃣  📈 Analisar Distribuição dos Pivôs")
        print("4️⃣  🎰 Gerar Combinações com Pivôs")
        print("5️⃣  🔬 Gerar Pool Otimizado (Máxima Cobertura)")
        print("6️⃣  📊 Validar Combinações contra Histórico")
        print("7️⃣  💾 Exportar Combinações para TXT")
        print("8️⃣  🤖 Exportar para ML 7.12 (com features)")
        print("9️⃣  🔄 Execução Completa (Análise + Geração)")
        print("🔟  🧬 INTEGRAÇÃO DIRETA ML 7.12 (Genético + Thompson) ⭐")
        print("0️⃣  ❌ Sair")
        print()
        
        opcao = input("🎯 Escolha uma opção: ").strip()
        
        if opcao == "1":
            # Análise de similaridade
            if not analisador.resultados:
                analisador.carregar_resultados()
            
            amostra = input("📊 Usar todos os concursos ou amostra? [T]odos/[A]mostra: ").strip().upper()
            if amostra == 'A':
                n = input("   Quantos últimos concursos? [500]: ").strip()
                n = int(n) if n else 500
                analisador.analisar_similaridade_completa(amostra_max=n)
            else:
                analisador.analisar_similaridade_completa()
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "2":
            # Definir pivôs
            print("\n🎯 DEFINIÇÃO DE NÚMEROS PIVÔ")
            print("=" * 50)
            print("Informe de 5 a 20 números entre 1 e 25.")
            print("Separe por vírgula ou espaço.")
            print("Exemplo: 1,3,4,5,6,8,9,10,12,13,14,15,16,17,19,20")
            print()
            
            entrada = input("🔢 Números pivô: ").strip()
            entrada = entrada.replace(',', ' ')
            
            try:
                numeros = [int(n.strip()) for n in entrada.split() if n.strip()]
                analisador.definir_pivos(numeros)
            except ValueError:
                print("❌ Entrada inválida! Use apenas números.")
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "3":
            # Analisar distribuição
            if not analisador.numeros_pivo:
                print("❌ Defina os números pivô primeiro (opção 2)!")
            else:
                analisador.analisar_distribuicao_pivos()
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "4":
            # Gerar combinações
            if not analisador.numeros_pivo:
                print("❌ Defina os números pivô primeiro (opção 2)!")
            else:
                qtd = input("🎰 Quantas combinações gerar? [50]: ").strip()
                qtd = int(qtd) if qtd else 50
                
                resp = input("📊 Respeitar distribuição histórica? [S/N]: ").strip().upper()
                respeitar = resp != 'N'
                
                combinacoes = analisador.gerar_combinacoes_pivo(qtd, respeitar)
                
                # Mostrar algumas
                print("\n📋 Primeiras 10 combinações:")
                for i, c in enumerate(combinacoes[:10], 1):
                    print(f"   {i}. {c}")
                
                if len(combinacoes) > 10:
                    print(f"   ... e mais {len(combinacoes) - 10} combinações")
                
                # Perguntar se quer exportar
                resp_exp = input("\n💾 Exportar para TXT? [S/N]: ").strip().upper()
                if resp_exp == 'S':
                    analisador.exportar_combinacoes(combinacoes)
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "5":
            # Pool otimizado
            if not analisador.numeros_pivo:
                print("❌ Defina os números pivô primeiro (opção 2)!")
            else:
                qtd = input("🔬 Tamanho máximo do pool? [50]: ").strip()
                qtd = int(qtd) if qtd else 50
                
                pool = analisador.gerar_pool_otimizado(qtd)
                
                print("\n📋 Pool Otimizado:")
                for i, c in enumerate(pool[:20], 1):
                    print(f"   {i}. {c}")
                if len(pool) > 20:
                    print(f"   ... e mais {len(pool) - 20} combinações")
                
                # Perguntar se quer exportar
                resp_exp = input("\n💾 Exportar para TXT? [S/N]: ").strip().upper()
                if resp_exp == 'S':
                    analisador.exportar_combinacoes(pool)
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "6":
            # Validar combinações
            print("📥 Informe as combinações para validar.")
            print("   Formato: cada linha uma combinação, números separados por vírgula")
            print("   Digite 'FIM' para encerrar a entrada")
            print()
            
            combinacoes = []
            while True:
                linha = input("   > ").strip()
                if linha.upper() == 'FIM':
                    break
                try:
                    nums = [int(n.strip()) for n in linha.replace(',', ' ').split() if n.strip()]
                    if len(nums) == 15:
                        combinacoes.append(sorted(nums))
                    else:
                        print(f"     ⚠️ Combinação deve ter 15 números (tem {len(nums)})")
                except ValueError:
                    print("     ⚠️ Entrada inválida, tente novamente")
            
            if combinacoes:
                analisador.validar_combinacoes_contra_historico(combinacoes)
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "7":
            # Exportar
            print("❓ Gerar novas combinações ou usar as últimas geradas?")
            resp = input("   [N]ovas / [U]ltimas: ").strip().upper()
            
            if resp == 'N':
                if not analisador.numeros_pivo:
                    print("❌ Defina os números pivô primeiro!")
                    continue
                qtd = input("   Quantas? [50]: ").strip()
                qtd = int(qtd) if qtd else 50
                combinacoes_geradas = analisador.gerar_combinacoes_pivo(qtd, True)
            else:
                if not combinacoes_geradas:
                    print("❌ Nenhuma combinação gerada ainda! Gerando 50 novas...")
                    if not analisador.numeros_pivo:
                        print("❌ Defina os números pivô primeiro!")
                        input("\n⏸️ Pressione ENTER para continuar...")
                        continue
                    combinacoes_geradas = analisador.gerar_combinacoes_pivo(50, True)
            
            analisador.exportar_combinacoes(combinacoes_geradas)
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "8":
            # Exportar para ML 7.12
            if not analisador.numeros_pivo:
                print("❌ Defina os números pivô primeiro (opção 2)!")
                input("\n⏸️ Pressione ENTER para continuar...")
                continue
            
            print("\n🤖 EXPORTAR PARA ML 7.12")
            print("=" * 50)
            print("Este recurso exporta:")
            print("  • Arquivo TXT com combinações")
            print("  • Arquivo JSON com metadados e features para ML")
            print("  • Insights extraídos da análise")
            print()
            
            qtd = input("   Quantas combinações? [50]: ").strip()
            qtd = int(qtd) if qtd else 50
            
            combinacoes_geradas = analisador.gerar_combinacoes_pivo(qtd, True)
            resultado = analisador.exportar_para_ml(combinacoes_geradas)
            
            print("\n📊 INSIGHTS EXTRAÍDOS:")
            print("-" * 50)
            insights = resultado['dados']['insights']
            if insights['faixa_ideal_pivos']:
                print(f"   🎯 Faixa ideal: {insights['faixa_ideal_pivos'][0]}-{insights['faixa_ideal_pivos'][1]} pivôs")
                print(f"   📊 Cobertura: {insights['cobertura_faixa_ideal']:.1f}%")
            if insights['media_similaridade']:
                print(f"   🔗 Similaridade média: {insights['media_similaridade']:.2f} números em comum")
            if insights['numeros_nucleo']:
                print(f"   🧬 Núcleo comum: {insights['numeros_nucleo'][:10]}")
            print()
            for rec in insights['recomendacoes']:
                print(f"   💡 {rec}")
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "9":
            # Execução completa
            print("\n🔄 EXECUÇÃO COMPLETA")
            print("=" * 50)
            
            # 1. Carregar dados
            analisador.carregar_resultados()
            
            # 2. Análise de similaridade
            print("\n📊 ETAPA 1: Análise de Similaridade")
            analisador.analisar_similaridade_completa(amostra_max=1000)
            
            # 3. Definir pivôs
            print("\n🎯 ETAPA 2: Definição de Pivôs")
            print("Informe de 5 a 20 números (ou ENTER para sugestão automática):")
            entrada = input("🔢 Números pivô: ").strip()
            
            if entrada:
                entrada = entrada.replace(',', ' ')
                try:
                    numeros = [int(n.strip()) for n in entrada.split() if n.strip()]
                    analisador.definir_pivos(numeros)
                except ValueError:
                    print("❌ Entrada inválida!")
                    continue
            else:
                # Sugestão automática: top 16 mais frequentes
                frequencia = Counter()
                for _, nums in analisador.resultados:
                    for n in nums:
                        frequencia[n] += 1
                top_16 = [n for n, _ in frequencia.most_common(16)]
                analisador.definir_pivos(top_16)
            
            # 4. Analisar distribuição
            print("\n📈 ETAPA 3: Análise de Distribuição")
            analisador.analisar_distribuicao_pivos()
            
            # 5. Gerar pool otimizado
            print("\n🔬 ETAPA 4: Geração de Pool Otimizado")
            qtd = input("   Quantas combinações no pool? [50]: ").strip()
            qtd = int(qtd) if qtd else 50
            combinacoes_geradas = analisador.gerar_pool_otimizado(qtd)
            
            # 6. Exportar
            print("\n💾 ETAPA 5: Exportação")
            print("   1. Apenas TXT")
            print("   2. TXT + JSON para ML 7.12")
            resp = input("   Escolha [1/2]: ").strip()
            
            if resp == "2":
                analisador.exportar_para_ml(combinacoes_geradas)
            else:
                analisador.exportar_combinacoes(combinacoes_geradas)
            
            print("\n✅ EXECUÇÃO COMPLETA FINALIZADA!")
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "10":
            # Integração direta com ML 7.12
            if not analisador.numeros_pivo:
                print("❌ Defina os números pivô primeiro (opção 2)!")
                input("\n⏸️ Pressione ENTER para continuar...")
                continue
            
            if not analisador.resultados:
                analisador.carregar_resultados()
            
            print("\n🧬 INTEGRAÇÃO DIRETA COM ML 7.12")
            print("=" * 50)
            print("Este modo combina:")
            print("  • Geração baseada em Pivôs (distribuição histórica)")
            print("  • Algoritmo Genético (evolução de combinações)")
            print("  • Features do ML (frequência, atraso, tendências)")
            print("  • Otimização por fitness híbrido")
            print()
            
            qtd = input("   Quantas combinações finais? [50]: ").strip()
            qtd = int(qtd) if qtd else 50
            
            resultado = analisador.integrar_com_ml(qtd)
            
            if resultado['combinacoes']:
                combinacoes_geradas = resultado['combinacoes']
                
                print("\n📋 PRIMEIRAS 15 COMBINAÇÕES:")
                print("-" * 60)
                for i, c in enumerate(combinacoes_geradas[:15], 1):
                    qtd_pivos = len(set(c) & set(analisador.numeros_pivo))
                    print(f"   {i:2d}. {c} ({qtd_pivos} pivôs)")
                
                if len(combinacoes_geradas) > 15:
                    print(f"   ... e mais {len(combinacoes_geradas) - 15} combinações")
                
                # Perguntar se quer exportar
                resp = input("\n💾 Exportar combinações? [S/N]: ").strip().upper()
                if resp == 'S':
                    analisador.exportar_combinacoes(combinacoes_geradas)
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "0":
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida!")


if __name__ == "__main__":
    print("=" * 70)
    print("🔬 ANALISADOR DE SIMILARIDADE E SISTEMA DE PIVÔS")
    print("=" * 70)
    print("Prova de Conceito - LotoScope")
    print()
    
    menu_interativo()
