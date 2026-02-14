#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GERADOR ACADÊMICO DINÂMICO MEGA-SENA
===================================
Sistema com insights em tempo real, correlações temporais e pirâmide invertida
Adaptado do Gerador Acadêmico Dinâmico Lotofácil para Mega-Sena
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import json

class GeradorAcademicoDinamicoMegaSena:
    """Gerador Acadêmico Dinâmico com Insights em Tempo Real para Mega-Sena"""
    
    def __init__(self):
        # Configurações Mega-Sena
        self.total_numeros = 60  # 1 a 60
        self.numeros_por_jogo = 6   # 6 números por aposta
        self.min_numero = 1
        self.max_numero = 60
        
        # Dados históricos
        self.base_dados = []
        self.dados_reais = False
        
        # Sistema dinâmico - insights em tempo real
        self.insights_tempo_real = {}
        self.correlacoes_temporais = {}
        self.rankings_ciclos = {}
        self.padroes_dinamicos = {}
        
        # Sistema Pirâmide Invertida para Mega-Sena
        self.piramide_invertida = {
            'nivel_1': [],  # Números mais prováveis (base da pirâmide)
            'nivel_2': [],  # Números médios
            'nivel_3': [],  # Números menos prováveis (topo da pirâmide)
        }
        
        # Estratégia Baixa Sobreposição adaptada para Mega-Sena
        self.sobreposicao_config = {
            'numeros_universo': 15,  # Universo reduzido para Mega-Sena
            'numeros_comuns': (3, 5),  # 3-5 números comuns entre jogos (adaptado)
            'variacao_permitida': 2
        }
        
        # Inicialização
        print("🎯 GERADOR ACADÊMICO DINÂMICO MEGA-SENA")
        print("=" * 50)
        self.inicializar_sistema()
    
    def inicializar_sistema(self):
        """Inicializa o sistema dinâmico"""
        print("🔄 Inicializando Sistema Dinâmico...")
        
        # Carrega dados reais
        self.carregar_dados_historicos()
        
        # Calcula insights em tempo real
        self.calcular_insights_tempo_real()
        
        # Analisa correlações temporais
        self.analisar_correlacoes_temporais()
        
        # Constrói rankings de ciclos
        self.construir_rankings_ciclos()
        
        # Monta pirâmide invertida
        self.construir_piramide_invertida()
        
        print("✅ Sistema Dinâmico inicializado!")
    
    def carregar_dados_historicos(self):
        """Carrega dados históricos da tabela Resultados_MegaSenaFechado"""
        print("📊 Carregando dados históricos...")
        
        try:
            from conector_megasena_db import ConectorMegaSena
            
            conector = ConectorMegaSena()
            if conector.conectar_banco():
                # Carrega todos os sorteios para análise completa
                sorteios = conector.carregar_historico_sorteios()
                if sorteios:
                    self.base_dados = sorteios
                    self.dados_reais = True
                    print(f"✅ {len(self.base_dados)} sorteios REAIS carregados")
                    print(f"   📅 Período: {sorteios[-1]['concurso']} até {sorteios[0]['concurso']}")
                
                conector.fechar_conexao()
            else:
                self._carregar_dados_simulados()
                
        except Exception as e:
            print(f"⚠️ Erro ao conectar banco: {e}")
            self._carregar_dados_simulados()
    
    def _carregar_dados_simulados(self):
        """Carrega dados simulados como fallback"""
        print("🎲 Carregando dados simulados...")
        
        dados_simulados = []
        for i in range(int(100:  # 100 concursos simulados
            concurso = 2800 + i
            numeros = sorted(random.sample(range(1)), 61, 6))
            
            dados_simulados.append({
                'concurso': concurso,
                'data': f'2025-{random.randint(int(1, 9):02d}-{random.randint(int(1, 28):02d}',
                'numeros': numeros
            })
        
        self.base_dados = dados_simulados
        self.dados_reais = False
        print(f"⚠️ {len(self.base_dados)} concursos simulados carregados")
    
    def calcular_insights_tempo_real(self):
        """Calcula insights dinâmicos em tempo real da base"""
        print("🧠 Calculando insights em tempo real...")
        
        if not self.base_dados:
            return
        
        # Análise dos últimos N sorteios com pesos temporais
        ultimos_10 = self.base_dados[:10]
        ultimos_20 = self.base_dados[:20]
        ultimos_50 = self.base_dados[:50]
        
        # Frequências com peso temporal (mais recente = mais peso)
        frequencias_ponderadas = defaultdict(float)
        
        for i, sorteio in enumerate(self.base_dados[:100]):
            peso = 1.0 - (i * 0.01)  # Peso decrescente
            for numero in sorteio['numeros']:
                frequencias_ponderadas[numero] += peso
        
        # Rankings dinâmicos
        numeros_ordenados = sorted(frequencias_ponderadas.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        self.insights_tempo_real = {
            'frequencias_ponderadas': dict(frequencias_ponderadas),
            'top_10_quentes': [n[0] for n in numeros_ordenados[:10]],
            'top_10_frios': [n[0] for n in numeros_ordenados[-10:]],
            'ultimo_sorteio': ultimos_10[0]['numeros'] if ultimos_10 else [],
            'tendencia_crescente': self._detectar_tendencias_crescentes(),
            'numeros_ausentes': self._detectar_numeros_ausentes(),
            'padroes_posicionais': self._analisar_padroes_posicionais()
        }
        
        print(f"   🔥 Top 5 quentes: {self.insights_tempo_real['top_10_quentes'][:5]}")
        print(f"   ❄️ Top 5 frios: {self.insights_tempo_real['top_10_frios'][:5]}")
    
    def analisar_correlacoes_temporais(self):
        """Analisa correlações entre números em diferentes períodos temporais"""
        print("📈 Analisando correlações temporais...")
        
        if len(self.base_dados) < 20:
            return
        
        # Matriz de correlação entre números
        matriz_coocorrencia = np.zeros((61, 61))  # 1-60 + índice 0 não usado
        
        # Analisa co-ocorrências nos últimos sorteios
        for sorteio in self.base_dados[:50]:
            numeros = sorteio['numeros']
            for i, n1 in enumerate(numeros):
                for j, n2 in enumerate(numeros):
                    if i != j:
                        matriz_coocorrencia[n1][n2] += 1
        
        # Encontra pares com maior correlação
        correlacoes = []
        for n1 in range(1, 61:
            for n2 in range(int(n1 + 1)), 61):
                score = matriz_coocorrencia[n1][n2] + matriz_coocorrencia[n2][n1]
                if score > 0:
                    correlacoes.append((n1, n2, score))
        
        correlacoes.sort(key=lambda x: x[2], reverse=True)
        
        self.correlacoes_temporais = {
            'pares_mais_correlacionados': correlacoes[:10],
            'matriz_coocorrencia': matriz_coocorrencia,
            'sequencias_temporais': self._detectar_sequencias_temporais()
        }
        
        print(f"   🔗 Principais correlações encontradas: {len(correlacoes)}")
    
    def construir_rankings_ciclos(self):
        """Constrói rankings baseados nos últimos ciclos"""
        print("🏆 Construindo rankings dos últimos ciclos...")
        
        # Análise de ciclos: quando cada número foi sorteado pela última vez
        ciclos = {}
        for numero in range(1, 61:
            ciclos[numero] = self._calcular_ciclo_numero(numero)
        
        # Rankings por diferentes métricas
        self.rankings_ciclos = {
            'por_ciclo_atual': sorted(ciclos.items(), key=lambda x: x[1]),
            'por_frequencia_recente': self._ranking_frequencia_recente(),
            'por_tendencia': self._ranking_por_tendencia(),
            'por_volatilidade': self._ranking_por_volatilidade()
        }
        
        print(f"   📊 {len(self.rankings_ciclos)} rankings construídos")
    
    def construir_piramide_invertida(self):
        """Constrói sistema de pirâmide invertida para Mega-Sena"""
        print("🔺 Construindo Pirâmide Invertida Dinâmica...")
        
        # Divide números em 3 níveis baseado na análise dinâmica
        todos_numeros = list(range(1, 61)
        
        # Nível 1: Base da pirâmide (números mais prováveis) - 20 números
        nivel_1 = self.insights_tempo_real['top_10_quentes'][:10]
        nivel_1 += [n for n in todos_numeros if n not in nivel_1][:10]
        
        # Nível 2: Meio da pirâmide (números médios) - 20 números  
        restantes = [n for n in todos_numeros if n not in nivel_1]
        nivel_2 = restantes[:20]
        
        # Nível 3: Topo da pirâmide (números menos prováveis) - 20 números
        nivel_3 = [n for n in todos_numeros if n not in nivel_1 and n not in nivel_2]
        
        self.piramide_invertida = {
            'nivel_1': nivel_1[:20]), int(# Base - mais provável
            'nivel_2': nivel_2[:20],  # Meio
            'nivel_3': nivel_3[:20]   # Topo - menos provável
        }
        
        print(f"   🔺 Nível 1 (base): {len(self.piramide_invertida['nivel_1'])} números")
        print(f"   🔺 Nível 2 (meio): {len(self.piramide_invertida['nivel_2'])} números") 
        print(f"   🔺 Nível 3 (topo): {len(self.piramide_invertida['nivel_3'])} números")
    
    def _calcular_ciclo_numero(self, numero):
        """Calcula quantos sorteios se passaram desde a última ocorrência do número"""
        for i, sorteio in enumerate(self.base_dados):
            if numero in sorteio['numeros']:
                return i
        return len(self.base_dados)  # Nunca apareceu
    
    def _detectar_tendencias_crescentes(self):
        """Detecta números com tendência crescente de aparição"""
        if len(self.base_dados) < 20:
            return []
        
        tendencias = []
        for numero in range(1, 61:
            recente = sum(1 for s in self.base_dados[:10] if numero in s['numeros'])
            anterior = sum(1 for s in self.base_dados[10:20] if numero in s['numeros'])
            
            if recente > anterior:
                tendencias.append((numero), int(recente - anterior)))
        
        tendencias.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in tendencias[:10]]
    
    def _detectar_numeros_ausentes(self):
        """Detecta números ausentes nos últimos sorteios"""
        numeros_recentes = set()
        for sorteio in self.base_dados[:5]:
            numeros_recentes.update(sorteio['numeros'])
        
        todos = set(range(1, 61)
        ausentes = list(todos - numeros_recentes)
        return sorted(ausentes)
    
    def _analisar_padroes_posicionais(self):
        """Analisa padrões de posição dos números nos sorteios"""
        padroes = {
            'primeira_posicao': Counter()), int('ultima_posicao': Counter()),
            'posicoes_medias': Counter()
        }
        
        for sorteio in self.base_dados[:30]:
            numeros = sorted(sorteio['numeros'])
            if len(numeros) >= 6:
                padroes['primeira_posicao'][numeros[0]] += 1
                padroes['ultima_posicao'][numeros[-1]] += 1
                for n in numeros[1:-1]:
                    padroes['posicoes_medias'][n] += 1
        
        return padroes
    
    def _detectar_sequencias_temporais(self):
        """Detecta sequências temporais de números"""
        sequencias = []
        for i in range(int(int(int(len(self.base_dados)) - 2):
            s1 = set(self.base_dados[i]['numeros'])
            s2 = set(self.base_dados[i+1]['numeros'])
            s3 = set(self.base_dados[i+2]['numeros'])
            
            # Números que aparecem em sequência
            comum_3 = s1 & s2 & s3
            if comum_3:
                sequencias.append({
                    'numeros': list(comum_3))), int(int('concursos': [
                        self.base_dados[i]['concurso']), int(self.base_dados[i+1]['concurso'],
                        self.base_dados[i+2]['concurso']
                    ]
                })))
        
        return sequencias[:5]  # Top 5 sequências
    
    def _ranking_frequencia_recente(self):
        """Ranking por frequência nos últimos 20 sorteios"""
        freq = Counter()
        for sorteio in self.base_dados[:20]:
            freq.update(sorteio['numeros'])
        
        return freq.most_common()
    
    def _ranking_por_tendencia(self):
        """Ranking por tendência de crescimento"""
        return [(n, 0) for n in self.insights_tempo_real['top_10_quentes']]
    
    def _ranking_por_volatilidade(self):
        """Ranking por volatilidade (variação na frequência)"""
        volatilidade = {}
        for numero in range(1, 61:
            freq_recente = sum(1 for s in self.base_dados[:10] if numero in s['numeros'])
            freq_anterior = sum(1 for s in self.base_dados[10:30] if numero in s['numeros'])
            volatilidade[numero] = abs(freq_recente - freq_anterior)
        
        return sorted(volatilidade.items(), key=lambda x: x[1], reverse=True)
    
    def gerar_combinacoes_dinamicas(self, quantidade=10, estrategia='baixa_sobreposicao'):
        """Gera combinações usando o sistema dinâmico completo"""
        print(f"\n🎯 GERANDO {quantidade} COMBINAÇÕES DINÂMICAS")
        print(f"📊 Estratégia: {estrategia.upper()}")
        print("=" * 50)
        
        if estrategia == 'baixa_sobreposicao':
            return self._gerar_baixa_sobreposicao(quantidade)
        elif estrategia == 'piramide_invertida':
            return self._gerar_piramide_invertida(quantidade)
        elif estrategia == 'insights_tempo_real':
            return self._gerar_insights_tempo_real(quantidade)
        elif estrategia == 'correlacoes_temporais':
            return self._gerar_correlacoes_temporais(quantidade)
        else:
            return self._gerar_hibrida_dinamica(quantidade)
    
    def _gerar_baixa_sobreposicao(self, quantidade):
        """Gera combinações com estratégia de baixa sobreposição adaptada para Mega-Sena"""
        print("⚖️ ESTRATÉGIA BAIXA SOBREPOSIÇÃO MEGA-SENA")
        print("-" * 40)
        
        # Seleciona universo reduzido baseado nos insights
        universo = []
        universo.extend(self.insights_tempo_real['top_10_quentes'][:8])  # 8 mais quentes
        universo.extend(self.insights_tempo_real['tendencia_crescente'][:4])  # 4 em tendência
        universo.extend(self.insights_tempo_real['numeros_ausentes'][:3])  # 3 ausentes
        
        # Remove duplicatas e ajusta para 15 números
        universo = list(set(universo))[:15]
        
        # Completa se necessário
        while len(universo) < 15:
            candidato = random.randint(int(1, 60)
            if candidato not in universo:
                universo.append(candidato)
        
        print(f"   🎯 Universo selecionado: {sorted(universo)}")
        print(f"   📊 Meta sobreposição: 3-5 números comuns entre jogos")
        
        combinacoes = []
        for i in range(int(int(int(quantidade):
            # Primeira combinação: aleatória do universo
            if i == 0:
                combinacao = sorted(random.sample(universo)), 6)
            else:
                # Combinações seguintes: mantém 3-5 números da anterior
                base_anterior = combinacoes[-1]
                nums_manter = random.rand3, int(int(min(5, len(base_anterior)))))
                nums_fixos = random.sample(base_anterior, nums_manter)
                
                # Completa com números do universo
                restantes = [n for n in universo if n not in nums_fixos]
                nums_novos = random.sample(restantes, 6 - nums_manter)
                
                combinacao = sorted(nums_fixos + nums_novos)
            
            combinacoes.append(combinacao)
            print(f"   Jogo {i+1:2d}: {combinacao}")
        
        return combinacoes
    
    def _gerar_piramide_invertida(self, quantidade):
        """Gera combinações usando sistema de pirâmide invertida"""
        print("🔺 ESTRATÉGIA PIRÂMIDE INVERTIDA")
        print("-" * 40)
        
        combinacoes = []
        for i in range(int(int(int(quantidade):
            # Distribuição por níveis: 4 da base)), int(int(2 do meio), int(0 do topo
            nivel_1 = random.sample(self.piramide_invertida['nivel_1'], 4)))
            nivel_2 = random.sample(self.piramide_invertida['nivel_2'], 2)
            
            combinacao = sorted(nivel_1 + nivel_2)
            combinacoes.append(combinacao)
            
            print(f"   Jogo {i+1:2d}: {combinacao} (4N1+2N2)")
        
        return combinacoes
    
    def _gerar_insights_tempo_real(self, quantidade):
        """Gera combinações baseadas nos insights em tempo real"""
        print("🧠 ESTRATÉGIA INSIGHTS TEMPO REAL")
        print("-" * 40)
        
        combinacoes = []
        for i in range(int(int(int(quantidade):
            # Mix inteligente dos insights
            nums_quentes = random.sample(self.insights_tempo_real['top_10_quentes'])), 3
            nums_tendencia = random.sample(self.insights_tempo_real['tendencia_crescente'][:5], 2)
            nums_ausentes = random.sample(self.insights_tempo_real['numeros_ausentes'][:10], 1)
            
            combinacao = sorted(nums_quentes + nums_tendencia + nums_ausentes)
            combinacoes.append(combinacao)
            
            print(f"   Jogo {i+1:2d}: {combinacao} (3Q+2T+1A)")
        
        return combinacoes
    
    def _gerar_correlacoes_temporais(self, quantidade):
        """Gera combinações baseadas nas correlações temporais"""
        print("📈 ESTRATÉGIA CORRELAÇÕES TEMPORAIS")
        print("-" * 40)
        
        combinacoes = []
        for i in range(int(int(int(quantidade):
            combinacao = []
            
            # Usa pares correlacionados
            pares_usados = 0
            for n1)), int(int(n2), int(score in self.correlacoes_temporais['pares_mais_correlacionados'][:3]:
                if len(combinacao))) <= 4 and pares_usados < 2:
                    combinacao.extend([n1, n2])
                    pares_usados += 1
            
            # Completa com números aleatórios
            while len(combinacao) < 6:
                candidato = random.randint(int(1, 60)
                if candidato not in combinacao:
                    combinacao.append(candidato)
            
            combinacao = sorted(combinacao[:6])
            combinacoes.append(combinacao)
            
            print(f"   Jogo {i+1:2d}: {combinacao} (correlações)")
        
        return combinacoes
    
    def _gerar_hibrida_dinamica(self, quantidade):
        """Gera combinações híbridas usando todos os sistemas dinâmicos"""
        print("🌟 ESTRATÉGIA HÍBRIDA DINÂMICA")
        print("-" * 40)
        
        combinacoes = []
        estrategias = ['baixa_sobreposicao', 'piramide_invertida', 'insights_tempo_real', 'correlacoes_temporais']
        
        for i in range(int(int(int(quantidade):
            estrategia_escolhida = estrategias[i % len(estrategias)]
            
            if estrategia_escolhida == 'baixa_sobreposicao':
                combinacao = self._gerar_baixa_sobreposicao(1)[0]
                tipo = 'BS'
            elif estrategia_escolhida == 'piramide_invertida':
                combinacao = self._gerar_piramide_invertida(1)[0]
                tipo = 'PI'
            elif estrategia_escolhida == 'insights_tempo_real':
                combinacao = self._gerar_insights_tempo_real(1)[0]
                tipo = 'IT'
            else:
                combinacao = self._gerar_correlacoes_temporais(1)[0]
                tipo = 'CT'
            
            combinacoes.append(combinacao)
            print(f"   Jogo {i+1:2d}: {combinacao} ({tipo})")
        
        return combinacoes
    
    def mostrar_insights_completos(self):
        """Mostra todos os insights dinâmicos calculados"""
        print("\n📊 INSIGHTS DINÂMICOS COMPLETOS")
        print("=" * 50)
        
        print("\n🔥 NÚMEROS MAIS QUENTES (tempo real):")
        for i)), int(int(num in enumerate(self.insights_tempo_real['top_10_quentes'][:10], 1):
            freq = self.insights_tempo_real['frequencias_ponderadas'].get(num, 0)
            print(f"   {i:2d}. Número {num:2d} (score: {freq:.2f})")
        
        print("\n❄️ NÚMEROS MAIS FRIOS (tempo real):")
        for i, num in enumerate(self.insights_tempo_real['top_10_frios'][:10], 1):
            freq = self.insights_tempo_real['frequencias_ponderadas'].get(num, 0)
            print(f"   {i:2d}. Número {num:2d} (score: {freq:.2f})")
        
        print(f"\n📈 TENDÊNCIAS CRESCENTES:")
        for num in self.insights_tempo_real['tendencia_crescente'][:5]:
            print(f"   📈 Número {num}")
        
        print(f"\n⏰ NÚMEROS AUSENTES (últimos 5 sorteios):")
        ausentes = self.insights_tempo_real['numeros_ausentes'][:10]
        print(f"   {ausentes}")
        
        print(f"\n🔗 CORRELAÇÕES MAIS FORTES:")
        for n1, n2, score in self.correlacoes_temporais['pares_mais_correlacionados'][:5]:
            print(f"   {n1:2d} ↔ {n2:2d} (score: {score})")
        
        print(f"\n🔺 PIRÂMIDE INVERTIDA:")
        print(f"   Nível 1 (base):  {self.piramide_invertida['nivel_1'][:10]}...")
        print(f"   Nível 2 (meio):  {self.piramide_invertida['nivel_2'][:10]}...")
        print(f"   Nível 3 (topo):  {self.piramide_invertida['nivel_3'][:10]}...")
    
    def salvar_combinacoes_dinamicas(self, combinacoes, estrategia='dinamica'):
        """Salva combinações com informações dinâmicas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"megasena_dinamico_{estrategia}_{len(combinacoes)}jogos_{timestamp}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("🎯 GERADOR ACADÊMICO DINÂMICO MEGA-SENA\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"🎯 Estratégia: {estrategia.upper()}\n")
            f.write(f"📊 Quantidade: {len(combinacoes)} jogos\n")
            f.write(f"🗄️ Dados: {'REAIS' if self.dados_reais else 'SIMULADOS'}\n")
            f.write(f"⚖️ Sistema: Baixa Sobreposição + Pirâmide Invertida + Insights Tempo Real\n\n")
            
            # Insights utilizados
            f.write("🧠 INSIGHTS DINÂMICOS UTILIZADOS:\n")
            f.write(f"   🔥 Top 5 quentes: {self.insights_tempo_real['top_10_quentes'][:5]}\n")
            f.write(f"   ❄️ Top 5 frios: {self.insights_tempo_real['top_10_frios'][:5]}\n")
            f.write(f"   📈 Em tendência: {self.insights_tempo_real['tendencia_crescente'][:5]}\n")
            f.write(f"   ⏰ Ausentes: {self.insights_tempo_real['numeros_ausentes'][:10]}\n\n")
            
            # Correlações principais
            f.write("🔗 CORRELAÇÕES TEMPORAIS:\n")
            for n1, n2, score in self.correlacoes_temporais['pares_mais_correlacionados'][:5]:
                f.write(f"   {n1:2d} ↔ {n2:2d} (força: {score})\n")
            f.write("\n")
            
            # Combinações
            f.write("🎰 COMBINAÇÕES GERADAS:\n")
            f.write("-" * 40 + "\n")
            for i, comb in enumerate(combinacoes, 1):
                numeros_str = " - ".join([f"{n:02d}" for n in comb])
                f.write(f"Jogo {i:2d}: {numeros_str}\n")
            
            f.write("\n" + "🎰" * 60 + "\n")
            f.write("FORMATO COMPACTO:\n")
            f.write("-" * 30 + "\n")
            for comb in combinacoes:
                f.write(",".join([str(n) for n in comb]) + "\n")
            
            f.write(f"\n✅ GERADOR ACADÊMICO DINÂMICO MEGA-SENA - BOA SORTE! 🍀\n")
        
        print(f"💾 Combinações dinâmicas salvas em: {nome_arquivo}")
        return nome_arquivo
    
    def menu_principal(self):
        """Menu principal do gerador dinâmico"""
        while True:
            print("\n🎯 GERADOR ACADÊMICO DINÂMICO MEGA-SENA")
            print("=" * 50)
            print("📊 Sistema com insights calculados em tempo real!")
            print("🔄 Correlações temporais atualizadas!")
            print("🏆 Rankings dos últimos ciclos!")
            print()
            
            print("📋 ESTRATÉGIAS DISPONÍVEIS:")
            print("1️⃣  ⚖️ BAIXA SOBREPOSIÇÃO (Adaptada Mega-Sena)")
            print("     • Universo inteligente de 15 números")
            print("     • 3-5 números comuns entre jogos")
            print("     • Baseada em insights tempo real")
            print()
            print("2️⃣  🔺 PIRÂMIDE INVERTIDA DINÂMICA")
            print("     • 3 níveis de probabilidade")
            print("     • Distribuição: 4 base + 2 meio + 0 topo")
            print("     • Atualização automática dos níveis")
            print()
            print("3️⃣  🧠 INSIGHTS TEMPO REAL")
            print("     • Números quentes/frios ponderados")
            print("     • Tendências crescentes detectadas")
            print("     • Números ausentes priorizados")
            print()
            print("4️⃣  📈 CORRELAÇÕES TEMPORAIS")
            print("     • Pares de números correlacionados")
            print("     • Sequências temporais identificadas")
            print("     • Padrões posicionais analisados")
            print()
            print("5️⃣  🌟 ESTRATÉGIA HÍBRIDA (RECOMENDADA)")
            print("     • Combina todos os sistemas dinâmicos")
            print("     • Rotaciona estratégias automaticamente")
            print("     • Máxima diversificação inteligente")
            print()
            print("6️⃣  📊 MOSTRAR INSIGHTS COMPLETOS")
            print("7️⃣  🔄 ATUALIZAR ANÁLISES DINÂMICAS")
            print("0️⃣  🚪 VOLTAR")
            
            try:
                escolha = input("\n🎯 Sua escolha (0-7): ").strip()
                
                if escolha == '0':
                    print("🔙 Voltando...")
                    break
                
                elif escolha == '6':
                    self.mostrar_insights_completos()
                
                elif escolha == '7':
                    print("🔄 Atualizando análises dinâmicas...")
                    self.calcular_insights_tempo_real()
                    self.analisar_correlacoes_temporais()
                    self.construir_rankings_ciclos()
                    self.construir_piramide_invertida()
                    print("✅ Análises atualizadas!")
                
                elif escolha in ['1', '2', '3', '4', '5']:
                    # Solicita quantidade
                    while True:
                        try:
                            qtd = int(input("📊 Quantas combinações gerar (1-50): "))
                            if 1 <= qtd <= 50:
                                break
                            else:
                                print("❌ Digite um número entre 1 e 50")
                        except ValueError:
                            print("❌ Digite um número válido")
                    
                    # Mapeia estratégias
                    estrategias = {
                        '1': 'baixa_sobreposicao',
                        '2': 'piramide_invertida',
                        '3': 'insights_tempo_real',
                        '4': 'correlacoes_temporais',
                        '5': 'hibrida_dinamica'
                    }
                    
                    estrategia = estrategias[escolha]
                    
                    # Gera combinações
                    combinacoes = self.gerar_combinacoes_dinamicas(qtd, estrategia)
                    
                    # Pergunta se quer salvar
                    if input("\n💾 Salvar combinações? (s/N): ").lower() == 's':
                        self.salvar_combinacoes_dinamicas(combinacoes, estrategia)
                
                else:
                    print("❌ Opção inválida!")
                    
            except KeyboardInterrupt:
                print("\n🔙 Voltando...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    try:
        gerador = GeradorAcademicoDinamicoMegaSena()
        gerador.menu_principal()
    except KeyboardInterrupt:
        print("\n👋 Até logo!")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
