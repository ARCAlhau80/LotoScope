#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔢🌀 MÓDULO DE INTELIGÊNCIA PRIMOS E FIBONACCI
Sistema de análise e predição baseado em números primos e sequência de Fibonacci
Autor: AR CALHAU
Data: 06 de Agosto de 2025
"""

import sys
import os
import random
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
import statistics
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class InteligenciaPrimosFibonacci:
    """
    Sistema de inteligência baseado em números primos e Fibonacci
    """
    
    def __init__(self):
        """Inicializa o sistema de inteligência"""
        # Definições matemáticas
        self.PRIMOS = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        self.FIBONACCI = [1, 2, 3, 5, 8, 13, 21]
        self.PRIMOS_FIBONACCI = [2, 3, 5, 13]  # Intersecção
        
        # Dados históricos
        self.dados_historicos = None
        self.padroes_primos = {}
        self.padroes_fibonacci = {}
        self.distribuicoes = {}
        self.dados_carregados = False
        
        print("🔢🌀 Inteligência Primos/Fibonacci inicializada")
    
    def carregar_dados_historicos(self, concurso_limite: Optional[int] = None) -> bool:
        """
        Carrega dados históricos para análise
        
        Args:
            concurso_limite: Limite temporal para backtesting (opcional)
            
        Returns:
            bool: True se carregou com sucesso
        """
        try:
            print("📊 Carregando dados históricos primos/fibonacci...")
            
            with db_config.get_connection() as conn:
                # Query com filtro temporal se necessário
                where_clause = ""
                params = []
                if concurso_limite:
                    where_clause = "WHERE Concurso < ?"
                    params = [concurso_limite]
                
                query = f"""
                SELECT 
                    Concurso, QtdePrimos, QtdeFibonacci,
                    N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                    N11, N12, N13, N14, N15
                FROM Resultados_INT 
                {where_clause}
                ORDER BY Concurso DESC
                """
                
                self.dados_historicos = pd.read_sql(query, conn, params=params)
                
                # Cria colunas auxiliares
                self.dados_historicos['NumerosSorteados'] = self.dados_historicos.apply(
                    lambda row: [
                        row['N1'], row['N2'], row['N3'], row['N4'], row['N5'],
                        row['N6'], row['N7'], row['N8'], row['N9'], row['N10'],
                        row['N11'], row['N12'], row['N13'], row['N14'], row['N15']
                    ], axis=1
                )
                
                print(f"✅ {len(self.dados_historicos)} concursos carregados")
                if concurso_limite:
                    print(f"   🕰️ Filtro temporal: até concurso {concurso_limite-1}")
                
                # Analisa padrões
                self._analisar_padroes()
                self.dados_carregados = True
                
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def _analisar_padroes(self):
        """Analisa padrões históricos de primos e Fibonacci"""
        print("🧠 Analisando padrões primos/fibonacci...")
        
        # Distribuições gerais
        self.distribuicoes = {
            'primos': Counter(self.dados_historicos['QtdePrimos']),
            'fibonacci': Counter(self.dados_historicos['QtdeFibonacci']),
            'combinados': Counter(zip(self.dados_historicos['QtdePrimos'], 
                                    self.dados_historicos['QtdeFibonacci']))
        }
        
        # Padrões de primos
        self.padroes_primos = {
            'media': self.dados_historicos['QtdePrimos'].mean(),
            'mediana': self.dados_historicos['QtdePrimos'].median(),
            'moda': self.dados_historicos['QtdePrimos'].mode()[0],
            'range': (self.dados_historicos['QtdePrimos'].min(), 
                     self.dados_historicos['QtdePrimos'].max()),
            'frequencia_por_numero': self._calcular_frequencia_primos(),
            'tendencia_recente': self._calcular_tendencia_primos()
        }
        
        # Padrões de Fibonacci
        self.padroes_fibonacci = {
            'media': self.dados_historicos['QtdeFibonacci'].mean(),
            'mediana': self.dados_historicos['QtdeFibonacci'].median(),
            'moda': self.dados_historicos['QtdeFibonacci'].mode()[0],
            'range': (self.dados_historicos['QtdeFibonacci'].min(), 
                     self.dados_historicos['QtdeFibonacci'].max()),
            'frequencia_por_numero': self._calcular_frequencia_fibonacci(),
            'tendencia_recente': self._calcular_tendencia_fibonacci()
        }
        
        print(f"✅ Padrões analisados:")
        print(f"   🔢 Primos: {self.padroes_primos['media']:.1f} média, moda={self.padroes_primos['moda']}")
        print(f"   🌀 Fibonacci: {self.padroes_fibonacci['media']:.1f} média, moda={self.padroes_fibonacci['moda']}")
    
    def _calcular_frequencia_primos(self) -> Dict[int, float]:
        """Calcula frequência de cada número primo"""
        frequencias = {}
        total_sorteios = len(self.dados_historicos)
        
        for primo in self.PRIMOS:
            # Conta quantas vezes cada primo apareceu
            aparicoes = 0
            for numeros in self.dados_historicos['NumerosSorteados']:
                if primo in numeros:
                    aparicoes += 1
            
            frequencias[primo] = aparicoes / total_sorteios
        
        return frequencias
    
    def _calcular_frequencia_fibonacci(self) -> Dict[int, float]:
        """Calcula frequência de cada número Fibonacci"""
        frequencias = {}
        total_sorteios = len(self.dados_historicos)
        
        for fib in self.FIBONACCI:
            # Conta quantas vezes cada Fibonacci apareceu
            aparicoes = 0
            for numeros in self.dados_historicos['NumerosSorteados']:
                if fib in numeros:
                    aparicoes += 1
            
            frequencias[fib] = aparicoes / total_sorteios
        
        return frequencias
    
    def _calcular_tendencia_primos(self) -> Dict:
        """Calcula tendência recente de primos"""
        ultimos_100 = self.dados_historicos.head(100)
        ultimos_20 = self.dados_historicos.head(20)
        
        return {
            'media_recente_100': ultimos_100['QtdePrimos'].mean(),
            'media_recente_20': ultimos_20['QtdePrimos'].mean(),
            'tendencia': 'alta' if ultimos_20['QtdePrimos'].mean() > ultimos_100['QtdePrimos'].mean() else 'baixa'
        }
    
    def _calcular_tendencia_fibonacci(self) -> Dict:
        """Calcula tendência recente de Fibonacci"""
        ultimos_100 = self.dados_historicos.head(100)
        ultimos_20 = self.dados_historicos.head(20)
        
        return {
            'media_recente_100': ultimos_100['QtdeFibonacci'].mean(),
            'media_recente_20': ultimos_20['QtdeFibonacci'].mean(),
            'tendencia': 'alta' if ultimos_20['QtdeFibonacci'].mean() > ultimos_100['QtdeFibonacci'].mean() else 'baixa'
        }
    
    def calcular_score_primo(self, numero: int) -> float:
        """
        Calcula score de inteligência para um número primo
        
        Args:
            numero: Número a analisar
            
        Returns:
            float: Score 0-100
        """
        if numero not in self.PRIMOS:
            return 0.0
        
        if not self.dados_carregados:
            return 50.0  # Score neutro
        
        # Frequência histórica
        freq_historica = self.padroes_primos['frequencia_por_numero'].get(numero, 0)
        
        # Bônus se é primo especial (também Fibonacci)
        bonus_especial = 10.0 if numero in self.PRIMOS_FIBONACCI else 0.0
        
        # Ajuste por tendência
        ajuste_tendencia = 5.0 if self.padroes_primos['tendencia_recente']['tendencia'] == 'alta' else -5.0
        
        # Score final
        score = (freq_historica * 100) + bonus_especial + ajuste_tendencia
        
        return max(0.0, min(100.0, score))
    
    def calcular_score_fibonacci(self, numero: int) -> float:
        """
        Calcula score de inteligência para um número Fibonacci
        
        Args:
            numero: Número a analisar
            
        Returns:
            float: Score 0-100
        """
        if numero not in self.FIBONACCI:
            return 0.0
        
        if not self.dados_carregados:
            return 50.0  # Score neutro
        
        # Frequência histórica
        freq_historica = self.padroes_fibonacci['frequencia_por_numero'].get(numero, 0)
        
        # Bônus se é Fibonacci especial (também primo)
        bonus_especial = 10.0 if numero in self.PRIMOS_FIBONACCI else 0.0
        
        # Ajuste por tendência
        ajuste_tendencia = 5.0 if self.padroes_fibonacci['tendencia_recente']['tendencia'] == 'alta' else -5.0
        
        # Score final
        score = (freq_historica * 100) + bonus_especial + ajuste_tendencia
        
        return max(0.0, min(100.0, score))
    
    def calcular_score_combinado(self, numero: int) -> float:
        """
        Calcula score combinado (primo + Fibonacci)
        
        Args:
            numero: Número a analisar
            
        Returns:
            float: Score 0-100
        """
        score_primo = self.calcular_score_primo(numero)
        score_fibonacci = self.calcular_score_fibonacci(numero)
        
        # Se é ambos (primo E Fibonacci), potencializa
        if numero in self.PRIMOS_FIBONACCI:
            return min(100.0, (score_primo + score_fibonacci) * 0.75)
        
        # Se é apenas um deles
        return max(score_primo, score_fibonacci)
    
    def sugerir_quantidade_primos(self) -> int:
        """
        Sugere quantidade ideal de primos para próximo sorteio
        
        Returns:
            int: Quantidade sugerida de primos
        """
        if not self.dados_carregados:
            return 5  # Valor padrão baseado na moda histórica
        
        # Usa moda com ajuste por tendência
        quantidade_base = int(self.padroes_primos['moda'])
        
        # Ajuste por tendência recente
        if self.padroes_primos['tendencia_recente']['tendencia'] == 'alta':
            quantidade_base += 1
        elif self.padroes_primos['tendencia_recente']['tendencia'] == 'baixa':
            quantidade_base -= 1
        
        # Mantém dentro do range histórico
        min_val, max_val = self.padroes_primos['range']
        return max(min_val, min(max_val, quantidade_base))
    
    def sugerir_quantidade_fibonacci(self) -> int:
        """
        Sugere quantidade ideal de Fibonacci para próximo sorteio
        
        Returns:
            int: Quantidade sugerida de Fibonacci
        """
        if not self.dados_carregados:
            return 4  # Valor padrão baseado na moda histórica
        
        # Usa moda com ajuste por tendência
        quantidade_base = int(self.padroes_fibonacci['moda'])
        
        # Ajuste por tendência recente
        if self.padroes_fibonacci['tendencia_recente']['tendencia'] == 'alta':
            quantidade_base += 1
        elif self.padroes_fibonacci['tendencia_recente']['tendencia'] == 'baixa':
            quantidade_base -= 1
        
        # Mantém dentro do range histórico
        min_val, max_val = self.padroes_fibonacci['range']
        return max(min_val, min(max_val, quantidade_base))
    
    def avaliar_combinacao(self, numeros: List[int]) -> Dict:
        """
        Avalia uma combinação quanto aos padrões primos/Fibonacci
        
        Args:
            numeros: Lista de 15 números
            
        Returns:
            Dict: Avaliação detalhada
        """
        primos_na_combinacao = [n for n in numeros if n in self.PRIMOS]
        fibonacci_na_combinacao = [n for n in numeros if n in self.FIBONACCI]
        especiais_na_combinacao = [n for n in numeros if n in self.PRIMOS_FIBONACCI]
        
        qtd_primos = len(primos_na_combinacao)
        qtd_fibonacci = len(fibonacci_na_combinacao)
        qtd_especiais = len(especiais_na_combinacao)
        
        # Calcula desvios das quantidades ideais
        primos_ideal = self.sugerir_quantidade_primos()
        fibonacci_ideal = self.sugerir_quantidade_fibonacci()
        
        desvio_primos = abs(qtd_primos - primos_ideal)
        desvio_fibonacci = abs(qtd_fibonacci - fibonacci_ideal)
        
        # Score geral (quanto menor o desvio, melhor)
        score_primos = max(0, 100 - (desvio_primos * 20))
        score_fibonacci = max(0, 100 - (desvio_fibonacci * 20))
        score_geral = (score_primos + score_fibonacci) / 2
        
        return {
            'qtd_primos': qtd_primos,
            'qtd_fibonacci': qtd_fibonacci,
            'qtd_especiais': qtd_especiais,
            'primos_presentes': primos_na_combinacao,
            'fibonacci_presentes': fibonacci_na_combinacao,
            'especiais_presentes': especiais_na_combinacao,
            'primos_ideal': primos_ideal,
            'fibonacci_ideal': fibonacci_ideal,
            'desvio_primos': desvio_primos,
            'desvio_fibonacci': desvio_fibonacci,
            'score_primos': score_primos,
            'score_fibonacci': score_fibonacci,
            'score_geral': score_geral,
            'balanceamento': 'ótimo' if desvio_primos <= 1 and desvio_fibonacci <= 1 else 'moderado' if desvio_primos <= 2 and desvio_fibonacci <= 2 else 'desbalanceado'
        }
    
    def otimizar_combinacao(self, numeros_base: List[int], debug: bool = False) -> List[int]:
        """
        Otimiza uma combinação considerando padrões primos/Fibonacci
        
        Args:
            numeros_base: Combinação inicial
            debug: Se deve mostrar debug
            
        Returns:
            List[int]: Combinação otimizada
        """
        numeros = numeros_base.copy()
        
        if debug:
            print(f"🔧 Otimizando combinação com inteligência primos/fibonacci...")
        
        # Avalia combinação inicial
        avaliacao_inicial = self.avaliar_combinacao(numeros)
        
        if debug:
            print(f"   📊 Inicial: {avaliacao_inicial['qtd_primos']} primos, {avaliacao_inicial['qtd_fibonacci']} fibonacci")
            print(f"   🎯 Ideal: {avaliacao_inicial['primos_ideal']} primos, {avaliacao_inicial['fibonacci_ideal']} fibonacci")
        
        # Tentativas de otimização
        melhor_combinacao = numeros.copy()
        melhor_score = avaliacao_inicial['score_geral']
        
        for tentativa in range(int(10:  # Máximo 10 tentativas
            candidata = numeros.copy()
            
            # Seleciona número aleatório para trocar
            idx_trocar = np.random.randint(0)), int(int(15))
            numero_atual = candidata[idx_trocar]
            
            # Gera candidatos baseados na necessidade
            candidatos = []
            
            # Se precisa de mais primos
            if avaliacao_inicial['desvio_primos'] > 0 and avaliacao_inicial['qtd_primos'] < avaliacao_inicial['primos_ideal']:
                candidatos.extend([p for p in self.PRIMOS if p not in candidata])
            
            # Se precisa de mais Fibonacci
            if avaliacao_inicial['desvio_fibonacci'] > 0 and avaliacao_inicial['qtd_fibonacci'] < avaliacao_inicial['fibonacci_ideal']:
                candidatos.extend([f for f in self.FIBONACCI if f not in candidata])
            
            # Se não tem candidatos específicos), int(usa números aleatórios
            if not candidatos:
                candidatos = [n for n in range(int(1), 26) if n not in candidata]
            
            if candidatos:
                novo_numero = np.random.choice(candidatos)
                candidata[idx_trocar] = novo_numero
                candidata.sort()
                
                # Avalia nova combinação
                nova_avaliacao = self.avaliar_combinacao(candidata)
                
                if nova_avaliacao['score_geral'] > melhor_score:
                    melhor_combinacao = candidata.copy()
                    melhor_score = nova_avaliacao['score_geral']
                    
                    if debug:
                        print(f"   ✨ Melhoria encontrada! Score: {melhor_score:.1f}")
        
        if debug:
            avaliacao_final = self.avaliar_combinacao(melhor_combinacao)
            print(f"   🎯 Final: {avaliacao_final['qtd_primos']} primos, {avaliacao_final['qtd_fibonacci']} fibonacci")
            print(f"   📈 Score: {avaliacao_inicial['score_geral']:.1f} → {melhor_score:.1f}")
        
        return melhor_combinacao
    
    def relatorio_inteligencia(self) -> str:
        """
        Gera relatório de inteligência primos/Fibonacci
        
        Returns:
            str: Relatório formatado
        """
        if not self.dados_carregados:
            return "❌ Dados não carregados"
        
        relatorio = []
        relatorio.append("🔢🌀 RELATÓRIO DE INTELIGÊNCIA PRIMOS/FIBONACCI")
        relatorio.append("=" * 60)
        
        # Padrões de primos
        relatorio.append(f"\n🔢 PADRÕES DE PRIMOS:")
        relatorio.append(f"   Média histórica: {self.padroes_primos['media']:.1f}")
        relatorio.append(f"   Moda (mais comum): {self.padroes_primos['moda']}")
        relatorio.append(f"   Range: {self.padroes_primos['range'][0]} - {self.padroes_primos['range'][1]}")
        relatorio.append(f"   Tendência recente: {self.padroes_primos['tendencia_recente']['tendencia']}")
        
        # Padrões de Fibonacci
        relatorio.append(f"\n🌀 PADRÕES DE FIBONACCI:")
        relatorio.append(f"   Média histórica: {self.padroes_fibonacci['media']:.1f}")
        relatorio.append(f"   Moda (mais comum): {self.padroes_fibonacci['moda']}")
        relatorio.append(f"   Range: {self.padroes_fibonacci['range'][0]} - {self.padroes_fibonacci['range'][1]}")
        relatorio.append(f"   Tendência recente: {self.padroes_fibonacci['tendencia_recente']['tendencia']}")
        
        # Frequências individuais
        relatorio.append(f"\n📊 FREQUÊNCIAS DOS PRIMOS:")
        for primo in sorted(self.PRIMOS):
            freq = self.padroes_primos['frequencia_por_numero'].get(primo, 0)
            score = self.calcular_score_primo(primo)
            relatorio.append(f"   {primo:2d}: {freq:.3f} ({freq*100:.1f}%) - Score: {score:.1f}")
        
        relatorio.append(f"\n📊 FREQUÊNCIAS DOS FIBONACCI:")
        for fib in sorted(self.FIBONACCI):
            freq = self.padroes_fibonacci['frequencia_por_numero'].get(fib, 0)
            score = self.calcular_score_fibonacci(fib)
            relatorio.append(f"   {fib:2d}: {freq:.3f} ({freq*100:.1f}%) - Score: {score:.1f}")
        
        # Sugestões
        relatorio.append(f"\n💡 SUGESTÕES PARA PRÓXIMO SORTEIO:")
        relatorio.append(f"   Primos recomendados: {self.sugerir_quantidade_primos()}")
        relatorio.append(f"   Fibonacci recomendados: {self.sugerir_quantidade_fibonacci()}")
        
        return "\n".join(relatorio)


def main():
    """Função principal para teste do módulo"""
    print("🔢🌀 MÓDULO DE INTELIGÊNCIA PRIMOS/FIBONACCI")
    print("=" * 60)
    
    # Testa o módulo
    inteligencia = InteligenciaPrimosFibonacci()
    
    if inteligencia.carregar_dados_historicos():
        print(inteligencia.relatorio_inteligencia())
        
        # Testa otimização
        print(f"\n🧪 TESTE DE OTIMIZAÇÃO:")
        combinacao_teste = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 24, 25, 4]
        combinacao_teste.sort()
        
        print(f"   Original: {combinacao_teste}")
        avaliacao_original = inteligencia.avaliar_combinacao(combinacao_teste)
        print(f"   Score original: {avaliacao_original['score_geral']:.1f}")
        
        combinacao_otimizada = inteligencia.otimizar_combinacao(combinacao_teste, debug=True)
        print(f"   Otimizada: {combinacao_otimizada}")


if __name__ == "__main__":
    main()
