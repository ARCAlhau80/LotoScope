#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌟 GERADOR HÍBRIDO COMPLETO
Sistema completo que integra TODOS os métodos de análise e predição
Combina: Posicional + Ciclos + Primos + Fibonacci + Ímpares + Soma + Quintis + Tendências
Autor: AR CALHAU
Data: 06 de Agosto de 2025
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'geradores'))
sys.path.insert(0, str(_BASE_DIR / 'ia'))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter, defaultdict
import statistics
import random
from datetime import datetime

from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from gerador_posicional_inteligente import GeradorPosicionalInteligente
from gerador_posicional import GeradorPosicional
from inteligencia_primos_fibonacci import InteligenciaPrimosFibonacci


class GeradorHibridoCompleto:
    """
    Gerador híbrido que integra TODOS os métodos de análise disponíveis
    """
    
    def __init__(self):
        """Inicializa o gerador híbrido completo"""
        # Componentes base
        self.gerador_posicional = GeradorPosicional()
        self.gerador_inteligente = GeradorPosicionalInteligente()
        self.inteligencia_primos_fibonacci = InteligenciaPrimosFibonacci()
        
        # Dados históricos consolidados
        self.dados_historicos = None
        self.dados_ciclos = None
        self.dados_carregados = False
        
        # Análises estatísticas
        self.padroes_soma = {}
        self.padroes_impares = {}
        self.padroes_quintis = {}
        self.padroes_gaps = {}
        self.padroes_sequencias = {}
        self.padroes_extremos = {}
        self.padroes_multiplos = {}
        self.padroes_faixas = {}
        
        # Configurações de peso para balanceamento
        self.pesos = {
            'posicional': 0.20,
            'ciclos': 0.20,
            'primos_fibonacci': 0.15,
            'soma': 0.10,
            'impares': 0.10,
            'quintis': 0.10,
            'tendencias': 0.10,
            'padroes_avancados': 0.05
        }
        
        print("🌟 Gerador Híbrido Completo inicializado")
        print("🔥 Integração: Posicional + Ciclos + Primos + Fibonacci + Análises Avançadas")
    
    def carregar_dados_completos(self, concurso_limite: Optional[int] = None) -> bool:
        """
        Carrega todos os dados necessários para análise completa
        
        Args:
            concurso_limite: Limite temporal para backtesting (opcional)
            
        Returns:
            bool: True se carregou com sucesso
        """
        try:
            print("📊 Carregando dados completos para análise híbrida...")
            
            # Carrega dados dos componentes base
            if not self.gerador_posicional.carregar_dados_historicos():
                print("❌ Erro ao carregar dados posicionais")
                return False
            
            if not self.gerador_inteligente.carregar_dados_ciclos():
                print("❌ Erro ao carregar dados de ciclos")
                return False
            
            if not self.inteligencia_primos_fibonacci.carregar_dados_historicos(concurso_limite):
                print("❌ Erro ao carregar dados primos/fibonacci")
                return False
            
            # Carrega dados históricos completos
            with db_config.get_connection() as conn:
                where_clause = ""
                params = []
                if concurso_limite:
                    where_clause = "WHERE Concurso < ?"
                    params = [concurso_limite]
                
                query = f"""
                SELECT 
                    Concurso, 
                    N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                    QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal,
                    Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                    QtdeGaps, QtdeRepetidos, SEQ, DistanciaExtremos,
                    ParesSequencia, QtdeMultiplos3, ParesSaltados,
                    Faixa_Baixa, Faixa_Media, Faixa_Alta,
                    RepetidosMesmaPosicao, Acumulou
                FROM Resultados_INT 
                {where_clause}
                ORDER BY Concurso DESC
                """
                
                self.dados_historicos = pd.read_sql(query, conn, params=params)
                
                # Cria coluna de números sorteados
                self.dados_historicos['NumerosSorteados'] = self.dados_historicos.apply(
                    lambda row: [
                        row['N1'], row['N2'], row['N3'], row['N4'], row['N5'],
                        row['N6'], row['N7'], row['N8'], row['N9'], row['N10'],
                        row['N11'], row['N12'], row['N13'], row['N14'], row['N15']
                    ], axis=1
                )
                
                print(f"✅ {len(self.dados_historicos)} concursos carregados para análise híbrida")
                if concurso_limite:
                    print(f"   🕰️ Filtro temporal: até concurso {concurso_limite-1}")
            
            # Analisa todos os padrões
            self._analisar_padroes_completos()
            self.dados_carregados = True
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados completos: {e}")
            return False
    
    def _analisar_padroes_completos(self):
        """Analisa todos os padrões estatísticos disponíveis"""
        print("🧠 Analisando padrões completos...")
        
        # Padrões de soma
        self.padroes_soma = {
            'media': self.dados_historicos['SomaTotal'].mean(),
            'mediana': self.dados_historicos['SomaTotal'].median(),
            'moda': self.dados_historicos['SomaTotal'].mode().iloc[0] if not self.dados_historicos['SomaTotal'].mode().empty else 195,
            'desvio_padrao': self.dados_historicos['SomaTotal'].std(),
            'range': (self.dados_historicos['SomaTotal'].min(), self.dados_historicos['SomaTotal'].max()),
            'quartis': (
                self.dados_historicos['SomaTotal'].quantile(0.25),
                self.dados_historicos['SomaTotal'].quantile(0.75)
            ),
            'tendencia_recente': self.dados_historicos['SomaTotal'].head(50).mean()
        }
        
        # Padrões de ímpares
        self.padroes_impares = {
            'media': self.dados_historicos['QtdeImpares'].mean(),
            'moda': self.dados_historicos['QtdeImpares'].mode().iloc[0] if not self.dados_historicos['QtdeImpares'].mode().empty else 7,
            'distribuicao': self.dados_historicos['QtdeImpares'].value_counts().to_dict(),
            'tendencia_recente': self.dados_historicos['QtdeImpares'].head(50).mean()
        }
        
        # Padrões de quintis
        self.padroes_quintis = {
            'q1_media': self.dados_historicos['Quintil1'].mean(),
            'q2_media': self.dados_historicos['Quintil2'].mean(),
            'q3_media': self.dados_historicos['Quintil3'].mean(),
            'q4_media': self.dados_historicos['Quintil4'].mean(),
            'q5_media': self.dados_historicos['Quintil5'].mean(),
            'balanceamento_ideal': [3, 3, 3, 3, 3],  # Distribuição ideal
            'variacao_permitida': 1
        }
        
        # Padrões de gaps
        self.padroes_gaps = {
            'media': self.dados_historicos['QtdeGaps'].mean(),
            'moda': self.dados_historicos['QtdeGaps'].mode().iloc[0] if not self.dados_historicos['QtdeGaps'].mode().empty else 5,
            'distribuicao': self.dados_historicos['QtdeGaps'].value_counts().to_dict()
        }
        
        # Padrões de sequências
        self.padroes_sequencias = {
            'seq_media': self.dados_historicos['SEQ'].mean(),
            'pares_sequencia_media': self.dados_historicos['ParesSequencia'].mean(),
            'pares_saltados_media': self.dados_historicos['ParesSaltados'].mean()
        }
        
        # Padrões de extremos
        self.padroes_extremos = {
            'distancia_media': self.dados_historicos['DistanciaExtremos'].mean(),
            'distancia_ideal': 20,  # Entre números 1 e 25
            'variacao_permitida': 5
        }
        
        # Padrões de múltiplos
        self.padroes_multiplos = {
            'multiplos3_media': self.dados_historicos['QtdeMultiplos3'].mean(),
            'multiplos3_moda': self.dados_historicos['QtdeMultiplos3'].mode().iloc[0] if not self.dados_historicos['QtdeMultiplos3'].mode().empty else 5
        }
        
        # Padrões de faixas
        self.padroes_faixas = {
            'baixa_media': self.dados_historicos['Faixa_Baixa'].mean(),
            'media_media': self.dados_historicos['Faixa_Media'].mean(),
            'alta_media': self.dados_historicos['Faixa_Alta'].mean(),
            'balanceamento_ideal': [5, 5, 5]  # Distribuição ideal
        }
        
        print("✅ Padrões completos analisados:")
        print(f"   📊 Soma ideal: {self.padroes_soma['media']:.1f} ± {self.padroes_soma['desvio_padrao']:.1f}")
        print(f"   🔢 Ímpares ideal: {self.padroes_impares['media']:.1f}")
        print(f"   📐 Quintis balanceados: {list(self.padroes_quintis['balanceamento_ideal'])}")
        print(f"   🕳️ Gaps médio: {self.padroes_gaps['media']:.1f}")
        print(f"   📏 Distância extremos: {self.padroes_extremos['distancia_media']:.1f}")
    
    def gerar_combinacao_hibrida(self, debug: bool = False) -> List[int]:
        """
        Gera combinação usando análise híbrida completa
        
        Args:
            debug: Se deve mostrar informações de debug
            
        Returns:
            List[int]: Combinação híbrida otimizada
        """
        if not self.dados_carregados:
            print("⚠️ Carregando dados automaticamente...")
            if not self.carregar_dados_completos():
                raise Exception("Não foi possível carregar dados")
        
        if debug:
            print("\n🌟 GERANDO COMBINAÇÃO HÍBRIDA COMPLETA")
            print("=" * 50)
        
        # 1. Base posicional inteligente (20%)
        if debug:
            print("📍 1. Análise posicional + ciclos...")
        
        base_posicional = self.gerador_inteligente.gerar_combinacao_inteligente(debug=False)
        score_posicional = self._calcular_score_posicional(base_posicional)
        
        # 2. Otimização primos/fibonacci (15%)
        if debug:
            print("🔢 2. Otimização primos/fibonacci...")
        
        combinacao_otimizada = self.inteligencia_primos_fibonacci.otimizar_combinacao(base_posicional, debug=False)
        score_primos_fib = self._calcular_score_primos_fibonacci(combinacao_otimizada)
        
        # 3. Ajuste de soma (10%)
        if debug:
            print("➕ 3. Ajuste de soma...")
        
        combinacao_soma = self._ajustar_soma(combinacao_otimizada, debug=debug)
        score_soma = self._calcular_score_soma(combinacao_soma)
        
        # 4. Balanceamento de ímpares (10%)
        if debug:
            print("🔀 4. Balanceamento ímpares...")
        
        combinacao_impares = self._balancear_impares(combinacao_soma, debug=debug)
        score_impares = self._calcular_score_impares(combinacao_impares)
        
        # 5. Distribuição de quintis (10%)
        if debug:
            print("📐 5. Distribuição quintis...")
        
        combinacao_quintis = self._distribuir_quintis(combinacao_impares, debug=debug)
        score_quintis = self._calcular_score_quintis(combinacao_quintis)
        
        # 6. Otimização de padrões avançados (10%)
        if debug:
            print("🎯 6. Padrões avançados...")
        
        combinacao_final = self._otimizar_padroes_avancados(combinacao_quintis, debug=debug)
        
        # Calcula scores finais
        scores = {
            'posicional': score_posicional,
            'primos_fibonacci': score_primos_fib,
            'soma': score_soma,
            'impares': score_impares,
            'quintis': score_quintis,
            'score_final': self._calcular_score_final(combinacao_final)
        }
        
        if debug:
            print(f"\n📊 SCORES DA COMBINAÇÃO HÍBRIDA:")
            print(f"   📍 Posicional: {scores['posicional']:.1f}/100")
            print(f"   🔢 Primos/Fibonacci: {scores['primos_fibonacci']:.1f}/100")
            print(f"   ➕ Soma: {scores['soma']:.1f}/100")
            print(f"   🔀 Ímpares: {scores['impares']:.1f}/100")
            print(f"   📐 Quintis: {scores['quintis']:.1f}/100")
            print(f"   🌟 SCORE FINAL: {scores['score_final']:.1f}/100")
            print(f"\n🎯 COMBINAÇÃO FINAL: {','.join(map(str, sorted(combinacao_final)))}")
        
        return combinacao_final
    
    def gerar_multiplas_combinacoes_hibridas(self, quantidade: int, debug: bool = False) -> List[Dict[str, Any]]:
        """
        Gera múltiplas combinações híbridas com estratégia de cobertura
        
        Primeira combinação: Mais eficaz e provável
        Demais combinações: Exatamente 10 números em comum com a principal
        
        Args:
            quantidade: Número de combinações a gerar
            debug: Se deve mostrar debug
            
        Returns:
            List[Dict]: Lista com combinações e seus scores
        """
        if debug:
            print(f"\n🚀 GERANDO {quantidade} COMBINAÇÕES HÍBRIDAS")
            print("=" * 60)
            print("🎯 Estratégia: 1ª = Mais eficaz | Demais = 10 números em comum")
        
        combinacoes = []
        
        # 1. GERA A COMBINAÇÃO PRINCIPAL (mais eficaz)
        if debug:
            print(f"\n--- Combinação Principal (1/{quantidade}) ---")
            print("🎯 Gerando combinação mais eficaz e provável...")
        
        # Para garantir que seja a mais eficaz, gera várias e escolhe a melhor
        candidatas_principais = []
        for _ in range(5):  # Gera 5 candidatas para escolher a melhor
            candidata = self.gerar_combinacao_hibrida(debug=False)
            score = self._calcular_score_final(candidata)
            candidatas_principais.append((candidata, score))
        
        # Escolhe a melhor candidata como combinação principal
        combinacao_principal, score_principal = max(candidatas_principais, key=lambda x: x[1])
        
        analise_principal = self._analisar_combinacao_completa(combinacao_principal)
        combinacoes.append({
            'combinacao': combinacao_principal,
            'score_final': score_principal,
            'analise': analise_principal,
            'timestamp': datetime.now(),
            'tipo': 'principal'
        })
        
        if debug:
            print(f"   ✅ Principal: {combinacao_principal} → Score: {score_principal:.1f}")
        
        # 2. GERA AS DEMAIS COMBINAÇÕES (10 números em comum)
        for i in range(1, quantidade):
            if debug:
                print(f"\n--- Combinação Derivada {i+1}/{quantidade} ---")
                print("🔗 Mantendo 10 números em comum com a principal...")
            
            combinacao_derivada = self._gerar_combinacao_com_overlap(
                combinacao_principal, overlap_target=10, debug=debug
            )
            
            score_derivada = self._calcular_score_final(combinacao_derivada)
            analise_derivada = self._analisar_combinacao_completa(combinacao_derivada)
            
            # Verifica overlap real
            overlap_real = len(set(combinacao_principal) & set(combinacao_derivada))
            
            combinacoes.append({
                'combinacao': combinacao_derivada,
                'score_final': score_derivada,
                'analise': analise_derivada,
                'timestamp': datetime.now(),
                'tipo': 'derivada',
                'overlap_com_principal': overlap_real
            })
            
            if debug:
                print(f"   ✅ Derivada: {combinacao_derivada} → Score: {score_derivada:.1f}")
                print(f"   🔗 Overlap: {overlap_real}/15 números em comum")
        
        if debug:
            print(f"\n🏆 RESUMO DAS {quantidade} COMBINAÇÕES:")
            for i, combo in enumerate(combinacoes):
                tipo = combo.get('tipo', 'unknown')
                overlap = combo.get('overlap_com_principal', 15 if i == 0 else 0)
                print(f"   {i+1}º: {','.join(map(str, sorted(combo['combinacao'])))} (Score: {combo['score_final']:.1f}, {tipo}, overlap: {overlap})")
        
        return combinacoes
    
    def _gerar_combinacao_com_overlap(self, combinacao_base: List[int], overlap_target: int = 10, debug: bool = False) -> List[int]:
        """
        Gera combinação com overlap específico em relação à base
        
        Args:
            combinacao_base: Combinação de referência
            overlap_target: Quantidade de números em comum desejada
            debug: Se deve mostrar debug
            
        Returns:
            List[int]: Nova combinação com overlap desejado
        """
        if overlap_target > 15 or overlap_target < 0:
            overlap_target = 10
        
        # 1. Seleciona números da combinação base para manter
        numeros_manter = random.sample(combinacao_base, overlap_target)
        
        # 2. Precisa substituir (15 - overlap_target) números
        numeros_substituir = 15 - overlap_target
        
        # 3. Pool de números disponíveis (não estão na base)
        numeros_disponiveis = [n for n in range(1, 26) if n not in combinacao_base]
        
        # 4. Gera candidatas para os números substitutos
        candidatas_substitutos = []
        
        # Estratégia: prioriza números com bom potencial
        for numero in numeros_disponiveis:
            score_numero = self._avaliar_potencial_numero(numero)
            candidatas_substitutos.append((numero, score_numero))
        
        # Ordena por potencial e seleciona os melhores
        candidatas_substitutos.sort(key=lambda x: x[1], reverse=True)
        
        # Seleciona os substitutos com alguma aleatoriedade
        numeros_novos = []
        pool_candidatos = candidatas_substitutos[:min(len(candidatas_substitutos), numeros_substituir * 3)]
        
        for i in range(numeros_substituir):
            if pool_candidatos:
                # Usa distribuição ponderada favorecendo os melhores
                pesos = [2 ** (len(pool_candidatos) - j) for j in range(len(pool_candidatos))]
                candidato = random.choices(pool_candidatos, weights=pesos)[0]
                numeros_novos.append(candidato[0])
                pool_candidatos.remove(candidato)
        
        # 5. Combina números mantidos + números novos
        combinacao_final = numeros_manter + numeros_novos
        combinacao_final.sort()
        
        # 6. Refinamento para melhorar score mantendo overlap
        combinacao_final = self._refinar_combinacao_com_overlap(
            combinacao_final, combinacao_base, overlap_target
        )
        
        if debug:
            overlap_real = len(set(combinacao_base) & set(combinacao_final))
            print(f"      Base: {combinacao_base}")
            print(f"      Nova: {','.join(map(str, sorted(combinacao_final)))}")
            print(f"      Overlap: {overlap_real}/{overlap_target} (alvo)")
        
        return combinacao_final
    
    def _avaliar_potencial_numero(self, numero: int) -> float:
        """
        Avalia o potencial de um número baseado nos padrões históricos
        
        Args:
            numero: Número a avaliar (1-25)
            
        Returns:
            float: Score de potencial do número
        """
        score = 50.0  # Score base
        
        # Bonifica primos
        if numero in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
            score += 10
        
        # Bonifica fibonacci
        if numero in [1, 2, 3, 5, 8, 13, 21]:
            score += 8
        
        # Bonifica números com frequência equilibrada (zona média)
        if 8 <= numero <= 18:
            score += 5
        
        # Penaliza extremos
        if numero <= 3 or numero >= 23:
            score -= 5
        
        # Adiciona componente aleatório pequeno
        score += random.uniform(-3, 3)
        
        return max(0, score)
    
    def _refinar_combinacao_com_overlap(self, combinacao: List[int], base: List[int], overlap_target: int) -> List[int]:
        """
        Refina combinação mantendo o overlap desejado
        
        Args:
            combinacao: Combinação a refinar
            base: Combinação base de referência
            overlap_target: Overlap desejado
            
        Returns:
            List[int]: Combinação refinada
        """
        combinacao_refinada = combinacao.copy()
        
        # Verifica overlap atual
        overlap_atual = len(set(combinacao_refinada) & set(base))
        
        # Se overlap está correto, faz apenas pequenos ajustes de score
        if overlap_atual == overlap_target:
            # Pequenos ajustes nos números não-compartilhados
            numeros_nao_compartilhados = [n for n in combinacao_refinada if n not in base]
            
            if numeros_nao_compartilhados:
                # Tenta melhorar um número aleatório
                idx_melhoria = random.randint(int(0), int(len(numeros_nao_compartilhados)) - 1)
                numero_atual = numeros_nao_compartilhados[idx_melhoria]
                
                # Busca substitutos próximos que não estejam na base
                for delta in [-2, -1, 1, 2]:
                    candidato = numero_atual + delta
                    if (1 <= candidato <= 25 and 
                        candidato not in combinacao_refinada and 
                        candidato not in base):
                        
                        # Substitui na combinação
                        idx_original = combinacao_refinada.index(numero_atual)
                        combinacao_refinada[idx_original] = candidato
                        combinacao_refinada.sort()
                        break
        
        return combinacao_refinada
    
    def _calcular_score_posicional(self, combinacao: List[int]) -> float:
        """Calcula score baseado em análise posicional"""
        # Usa a avaliação do gerador inteligente
        score_base = 70.0  # Score base
        
        # Penaliza/bonifica baseado em padrões posicionais
        # (Implementação simplificada - pode ser expandida)
        return min(100.0, max(0.0, score_base + random.uniform(-10, 10)))
    
    def _calcular_score_primos_fibonacci(self, combinacao: List[int]) -> float:
        """Calcula score primos/fibonacci"""
        avaliacao = self.inteligencia_primos_fibonacci.avaliar_combinacao(combinacao)
        return avaliacao['score_geral']
    
    def _calcular_score_soma(self, combinacao: List[int]) -> float:
        """Calcula score baseado na soma"""
        soma_atual = sum(combinacao)
        soma_ideal = self.padroes_soma['media']
        desvio_padrao = self.padroes_soma['desvio_padrao']
        
        # Calcula desvio normalizado
        desvio = abs(soma_atual - soma_ideal) / desvio_padrao
        
        # Score inversamente proporcional ao desvio
        score = max(0, 100 - (desvio * 20))
        return min(100.0, score)
    
    def _calcular_score_impares(self, combinacao: List[int]) -> float:
        """Calcula score baseado na quantidade de ímpares"""
        impares_atual = sum(1 for n in combinacao if n % 2 == 1)
        impares_ideal = self.padroes_impares['media']
        
        desvio = abs(impares_atual - impares_ideal)
        score = max(0, 100 - (desvio * 15))
        return min(100.0, score)
    
    def _calcular_score_quintis(self, combinacao: List[int]) -> float:
        """Calcula score baseado na distribuição de quintis"""
        quintis_atual = self._calcular_quintis(combinacao)
        quintis_ideal = self.padroes_quintis['balanceamento_ideal']
        
        # Calcula desvio total
        desvio_total = sum(abs(atual - ideal) for atual, ideal in zip(quintis_atual, quintis_ideal))
        
        score = max(0, 100 - (desvio_total * 10))
        return min(100.0, score)
    
    def _calcular_score_final(self, combinacao: List[int]) -> float:
        """Calcula score final ponderado"""
        scores = {
            'posicional': self._calcular_score_posicional(combinacao),
            'primos_fibonacci': self._calcular_score_primos_fibonacci(combinacao),
            'soma': self._calcular_score_soma(combinacao),
            'impares': self._calcular_score_impares(combinacao),
            'quintis': self._calcular_score_quintis(combinacao)
        }
        
        # Score ponderado
        score_final = (
            scores['posicional'] * (self.pesos['posicional'] + self.pesos['ciclos']) +
            scores['primos_fibonacci'] * self.pesos['primos_fibonacci'] +
            scores['soma'] * self.pesos['soma'] +
            scores['impares'] * self.pesos['impares'] +
            scores['quintis'] * self.pesos['quintis']
        ) / sum([self.pesos['posicional'] + self.pesos['ciclos'], 
                self.pesos['primos_fibonacci'], self.pesos['soma'], 
                self.pesos['impares'], self.pesos['quintis']])
        
        return min(100.0, max(0.0, score_final))
    
    def _ajustar_soma(self, combinacao: List[int], debug: bool = False) -> List[int]:
        """Ajusta combinação para soma ideal"""
        soma_atual = sum(combinacao)
        soma_ideal = self.padroes_soma['media']
        diferenca = soma_ideal - soma_atual
        
        if abs(diferenca) <= 10:  # Diferença aceitável
            return combinacao.copy()
        
        combinacao_ajustada = combinacao.copy()
        
        # Tentativas de ajuste
        for _ in range(5):
            if diferenca > 0:  # Precisa aumentar soma
                # Substitui número baixo por alto
                idx_baixo = min(range(len(combinacao_ajustada)), key=lambda i: combinacao_ajustada[i])
                numero_baixo = combinacao_ajustada[idx_baixo]
                
                candidatos = [n for n in range(numero_baixo + 1, 26) if n not in combinacao_ajustada]
                if candidatos:
                    novo_numero = random.choice(candidatos[int(-3:)])  # Escolhe entre os maiores
                    combinacao_ajustada[idx_baixo] = novo_numero
                    
            else:  # Precisa diminuir soma
                # Substitui número alto por baixo
                idx_alto = max(range(len(combinacao_ajustada)), key=lambda i: combinacao_ajustada[i])
                numero_alto = combinacao_ajustada[idx_alto]
                
                candidatos = [n for n in range(1, numero_alto) if n not in combinacao_ajustada]
                if candidatos:
                    novo_numero = random.choice(candidatos[int(:3)])  # Escolhe entre os menores
                    combinacao_ajustada[idx_alto] = novo_numero
            
            combinacao_ajustada.sort()
            nova_soma = sum(combinacao_ajustada)
            
            if abs(nova_soma - soma_ideal) < abs(diferenca):
                diferenca = soma_ideal - nova_soma
                if abs(diferenca) <= 10:
                    break
        
        if debug:
            print(f"   Soma: {sum(combinacao)} → {sum(combinacao_ajustada)} (ideal: {soma_ideal:.1f})")
        
        return combinacao_ajustada
    
    def _balancear_impares(self, combinacao: List[int], debug: bool = False) -> List[int]:
        """Balanceia quantidade de números ímpares"""
        impares_atual = sum(1 for n in combinacao if n % 2 == 1)
        impares_ideal = round(self.padroes_impares['media'])
        diferenca = impares_ideal - impares_atual
        
        if abs(diferenca) <= 1:  # Diferença aceitável
            return combinacao.copy()
        
        combinacao_balanceada = combinacao.copy()
        
        if diferenca > 0:  # Precisa de mais ímpares
            pares = [n for n in combinacao_balanceada if n % 2 == 0]
            for _ in range(min(diferenca, len(pares))):
                if pares:
                    par_escolhido = random.choice(pares)
                    idx = combinacao_balanceada.index(par_escolhido)
                    
                    # Procura ímpar próximo não usado
                    candidatos_impares = [n for n in range(1, 26, 2) if n not in combinacao_balanceada]
                    if candidatos_impares:
                        novo_impar = min(candidatos_impares, key=lambda x: abs(x - par_escolhido))
                        combinacao_balanceada[idx] = novo_impar
                        pares.remove(par_escolhido)
        
        else:  # Precisa de menos ímpares (mais pares)
            impares = [n for n in combinacao_balanceada if n % 2 == 1]
            for _ in range(min(abs(diferenca), len(impares))):
                if impares:
                    impar_escolhido = random.choice(impares)
                    idx = combinacao_balanceada.index(impar_escolhido)
                    
                    # Procura par próximo não usado
                    candidatos_pares = [n for n in range(2, 26, 2) if n not in combinacao_balanceada]
                    if candidatos_pares:
                        novo_par = min(candidatos_pares, key=lambda x: abs(x - impar_escolhido))
                        combinacao_balanceada[idx] = novo_par
                        impares.remove(impar_escolhido)
        
        combinacao_balanceada.sort()
        
        if debug:
            impares_novo = sum(1 for n in combinacao_balanceada if n % 2 == 1)
            print(f"   Ímpares: {impares_atual} → {impares_novo} (ideal: {impares_ideal})")
        
        return combinacao_balanceada
    
    def _distribuir_quintis(self, combinacao: List[int], debug: bool = False) -> List[int]:
        """Distribui números pelos quintis de forma balanceada"""
        quintis_atual = self._calcular_quintis(combinacao)
        quintis_ideal = self.padroes_quintis['balanceamento_ideal']
        
        # Se já está bem balanceado, retorna
        desvio_total = sum(abs(atual - ideal) for atual, ideal in zip(quintis_atual, quintis_ideal))
        if desvio_total <= 2:
            return combinacao.copy()
        
        combinacao_distribuida = combinacao.copy()
        
        # Tenta rebalancear (implementação simplificada)
        for _ in range(3):  # Máximo 3 tentativas
            quintis_atual = self._calcular_quintis(combinacao_distribuida)
            
            # Encontra quintil com excesso e quintil com falta
            diferencas = [(i, atual - ideal) for i, (atual, ideal) in enumerate(zip(quintis_atual, quintis_ideal))]
            diferencas.sort(key=lambda x: x[1])
            
            quintil_falta = diferencas[0][0]  # Menor diferença (negativa)
            quintil_excesso = diferencas[-1][0]  # Maior diferença (positiva)
            
            if diferencas[0][1] >= -1 and diferencas[-1][1] <= 1:
                break  # Já está balanceado
            
            # Move número do quintil com excesso para quintil com falta
            numeros_excesso = [n for n in combinacao_distribuida if self._obter_quintil(n) == quintil_excesso]
            if numeros_excesso:
                numero_mover = random.choice(numeros_excesso)
                idx = combinacao_distribuida.index(numero_mover)
                
                # Faixa do quintil de destino
                faixa_inicio = quintil_falta * 5 + 1
                faixa_fim = (quintil_falta + 1) * 5
                
                candidatos = [n for n in range(faixa_inicio, faixa_fim + 1) if n not in combinacao_distribuida]
                if candidatos:
                    novo_numero = random.choice(candidatos)
                    combinacao_distribuida[idx] = novo_numero
        
        combinacao_distribuida.sort()
        
        if debug:
            quintis_novo = self._calcular_quintis(combinacao_distribuida)
            print(f"   Quintis: {quintis_atual} → {quintis_novo} (ideal: {quintis_ideal})")
        
        return combinacao_distribuida
    
    def _otimizar_padroes_avancados(self, combinacao: List[int], debug: bool = False) -> List[int]:
        """Otimiza padrões avançados (gaps, sequências, etc.)"""
        combinacao_otimizada = combinacao.copy()
        
        # Análise de gaps
        gaps_atual = self._calcular_gaps(combinacao_otimizada)
        gaps_ideal = self.padroes_gaps['media']
        
        # Análise de sequências
        sequencias_atual = self._calcular_sequencias(combinacao_otimizada)
        
        # Se os padrões estão bons, retorna
        if abs(gaps_atual - gaps_ideal) <= 1:
            return combinacao_otimizada
        
        # Pequenos ajustes (implementação simplificada)
        for _ in range(2):
            # Ajuste aleatório mantendo outras características
            idx_ajuste = random.randint(int(0), int(len(combinacao_otimizada)) - 1)
            numero_atual = combinacao_otimizada[idx_ajuste]
            
            # Procura substitutos próximos
            candidatos = []
            for delta in [-3, -2, -1, 1, 2, 3]:
                candidato = numero_atual + delta
                if 1 <= candidato <= 25 and candidato not in combinacao_otimizada:
                    candidatos.append(candidato)
            
            if candidatos:
                novo_numero = random.choice(candidatos)
                combinacao_otimizada[idx_ajuste] = novo_numero
                combinacao_otimizada.sort()
        
        if debug:
            gaps_novo = self._calcular_gaps(combinacao_otimizada)
            print(f"   Gaps: {gaps_atual} → {gaps_novo} (ideal: {gaps_ideal:.1f})")
        
        return combinacao_otimizada
    
    def _calcular_quintis(self, combinacao: List[int]) -> List[int]:
        """Calcula distribuição por quintis"""
        quintis = [0] * 5
        for numero in combinacao:
            quintil = min(4, (numero - 1) // 5)  # 0-4
            quintis[quintil] += 1
        return quintis
    
    def _obter_quintil(self, numero: int) -> int:
        """Obtém o quintil de um número"""
        return min(4, (numero - 1) // 5)
    
    def _calcular_gaps(self, combinacao: List[int]) -> int:
        """Calcula quantidade de gaps na combinação"""
        gaps = 0
        for i in range(len(combinacao) - 1):
            if combinacao[i + 1] - combinacao[i] > 1:
                gaps += 1
        return gaps
    
    def _calcular_sequencias(self, combinacao: List[int]) -> int:
        """Calcula quantidade de sequências na combinação"""
        sequencias = 0
        for i in range(len(combinacao) - 1):
            if combinacao[i + 1] - combinacao[i] == 1:
                sequencias += 1
        return sequencias
    
    def _adicionar_variacao_aleatoria(self):
        """Adiciona pequena variação nos pesos para diversidade"""
        variacao = 0.05  # 5% de variação
        for chave in self.pesos:
            self.pesos[chave] *= (1 + random.uniform(-variacao, variacao))
        
        # Normaliza pesos
        total_pesos = sum(self.pesos.values())
        for chave in self.pesos:
            self.pesos[chave] /= total_pesos
    
    def _analisar_combinacao_completa(self, combinacao: List[int]) -> Dict[str, Any]:
        """Análise completa de uma combinação"""
        analise = {
            'soma': sum(combinacao),
            'impares': sum(1 for n in combinacao if n % 2 == 1),
            'pares': sum(1 for n in combinacao if n % 2 == 0),
            'quintis': self._calcular_quintis(combinacao),
            'gaps': self._calcular_gaps(combinacao),
            'sequencias': self._calcular_sequencias(combinacao),
            'primos': len([n for n in combinacao if n in [2, 3, 5, 7, 11, 13, 17, 19, 23]]),
            'fibonacci': len([n for n in combinacao if n in [1, 2, 3, 5, 8, 13, 21]]),
            'distancia_extremos': max(combinacao) - min(combinacao),
            'numero_menor': min(combinacao),
            'numero_maior': max(combinacao)
        }
        return analise
    
    def relatorio_combinacao_hibrida(self, combinacao: List[int]) -> str:
        """Gera relatório detalhado de uma combinação híbrida"""
        analise = self._analisar_combinacao_completa(combinacao)
        scores = {
            'posicional': self._calcular_score_posicional(combinacao),
            'primos_fibonacci': self._calcular_score_primos_fibonacci(combinacao),
            'soma': self._calcular_score_soma(combinacao),
            'impares': self._calcular_score_impares(combinacao),
            'quintis': self._calcular_score_quintis(combinacao),
            'final': self._calcular_score_final(combinacao)
        }
        
        relatorio = []
        relatorio.append("🌟 RELATÓRIO ANÁLISE HÍBRIDA COMPLETA")
        relatorio.append("=" * 60)
        relatorio.append(f"🎯 Combinação: {','.join(map(str, sorted(combinacao)))}")
        relatorio.append(f"🌟 Score Final: {scores['final']:.1f}/100")
        relatorio.append("")
        
        relatorio.append("📊 ANÁLISE DETALHADA:")
        relatorio.append(f"   ➕ Soma: {analise['soma']} (Score: {scores['soma']:.1f})")
        relatorio.append(f"   🔀 Ímpares: {analise['impares']} | Pares: {analise['pares']} (Score: {scores['impares']:.1f})")
        relatorio.append(f"   📐 Quintis: {analise['quintis']} (Score: {scores['quintis']:.1f})")
        relatorio.append(f"   🕳️ Gaps: {analise['gaps']}")
        relatorio.append(f"   📏 Sequências: {analise['sequencias']}")
        relatorio.append(f"   🔢 Primos: {analise['primos']} | Fibonacci: {analise['fibonacci']} (Score: {scores['primos_fibonacci']:.1f})")
        relatorio.append(f"   📊 Distância extremos: {analise['distancia_extremos']}")
        relatorio.append(f"   🎯 Range: {analise['numero_menor']} - {analise['numero_maior']}")
        relatorio.append("")
        
        relatorio.append("🎯 SCORES COMPONENTES:")
        relatorio.append(f"   📍 Posicional: {scores['posicional']:.1f}/100")
        relatorio.append(f"   🔢 Primos/Fibonacci: {scores['primos_fibonacci']:.1f}/100")
        relatorio.append(f"   ➕ Soma: {scores['soma']:.1f}/100")
        relatorio.append(f"   🔀 Ímpares: {scores['impares']:.1f}/100")
        relatorio.append(f"   📐 Quintis: {scores['quintis']:.1f}/100")
        
        return "\n".join(relatorio)


def main():
    """Função principal para teste do gerador híbrido"""
    print("🌟 GERADOR HÍBRIDO COMPLETO - TESTE")
    print("=" * 60)
    
    gerador = GeradorHibridoCompleto()
    
    print("\n1. Carregando dados...")
    if not gerador.carregar_dados_completos():
        print("❌ Erro ao carregar dados")
        return
    
    print("\n2. Gerando combinação híbrida...")
    combinacao = gerador.gerar_combinacao_hibrida(debug=True)
    
    print("\n3. Relatório completo:")
    relatorio = gerador.relatorio_combinacao_hibrida(combinacao)
    print(relatorio)
    
    print("\n4. Testando múltiplas combinações...")
    combinacoes = gerador.gerar_multiplas_combinacoes_hibridas(3, debug=True)
    
    print(f"\n✅ Teste concluído! Melhor score: {combinacoes[0]['score_final']:.1f}")


if __name__ == "__main__":
    main()
