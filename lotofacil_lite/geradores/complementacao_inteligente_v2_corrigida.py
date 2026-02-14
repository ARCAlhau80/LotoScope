#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 COMPLEMENTAÇÃO INTELIGENTE V2.0 - VERSÃO CORRIGIDA

CORREÇÕES APLICADAS:
1. Simplificação dos critérios de scoring
2. Melhor distribuição entre números extremos e centrais
3. Redução da super-otimização que estava prejudicando
4. Foco em padrões reais vs teóricos complexos

Data: 17 de Setembro de 2025
Autor: AR CALHAU
"""

import os
import sys
import random
import datetime
from itertools import combinations
from typing import List, Tuple, Dict, Optional

# Importa dependências necessárias
# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    from database_config import db_config
except ImportError:
    print("⚠️ Banco de dados não disponível - usando modo simulado")
    db_config = None

class ComplementacaoInteligenteV2:
    """
    Versão corrigida do sistema de complementação inteligente
    Foca em simplicidade e eficácia vs complexidade excessiva
    """
    
    def __init__(self):
        self.numeros_primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
        self.dados_historicos = []
        
        # Configurações simplificadas
        self.peso_distribuicao = 3.0    # Distribuição equilibrada
        self.peso_frequencia = 2.0      # Frequência moderada
        self.peso_diversidade = 2.5     # Evitar clusters
        
        print("🔧 Complementação Inteligente V2.0 - Versão Corrigida")
        print("📊 Foco: Simplicidade + Distribuição equilibrada")
    
    def gerar_base_20_corrigida(self) -> List[int]:
        """
        Gera uma base de 20 números com distribuição CORRIGIDA
        CORREÇÃO: Não privilegia excessivamente números centrais
        """
        print("\n🎯 GERANDO BASE DE 20 NÚMEROS (VERSÃO CORRIGIDA)")
        print("=" * 50)
        
        # 1. DISTRIBUIÇÃO FORÇADA POR FAIXAS (CORREÇÃO PRINCIPAL)
        faixas = {
            'extrema_baixa': list(range(1, 6)),      # 1-5:   2-3 números
            'baixa': list(range(6, 11)),             # 6-10:  3-4 números  
            'central': list(range(11, 16)),          # 11-15: 4-5 números
            'alta': list(range(16, 21)),             # 16-20: 3-4 números
            'extrema_alta': list(range(21, 26))      # 21-25: 2-3 números
        }
        
        # CORREÇÃO: Garante números extremos (problema identificado)
        base_20 = []
        
        # Força pelo menos 2 números de cada extremo
        base_20.extend(random.sample(faixas['extrema_baixa'], 2))  # 1-5
        base_20.extend(random.sample(faixas['extrema_alta'], 2))   # 21-25
        
        # Distribui o restante equilibradamente
        base_20.extend(random.sample(faixas['baixa'], 4))          # 6-10
        base_20.extend(random.sample(faixas['central'], 5))        # 11-15 (centro)
        base_20.extend(random.sample(faixas['alta'], 4))           # 16-20
        
        # Completa os últimos 3 com diversidade
        restantes = [n for n in range(1, 26) if n not in base_20]
        base_20.extend(random.sample(restantes, 3))
        
        base_20.sort()
        
        print(f"✅ Base 20: {base_20}")
        self.analisar_distribuicao_base(base_20)
        
        return base_20
    
    def analisar_distribuicao_base(self, base_20: List[int]):
        """Analisa a distribuição da base gerada"""
        faixas_count = {
            '01-05': len([n for n in base_20 if 1 <= n <= 5]),
            '06-10': len([n for n in base_20 if 6 <= n <= 10]),
            '11-15': len([n for n in base_20 if 11 <= n <= 15]),
            '16-20': len([n for n in base_20 if 16 <= n <= 20]),
            '21-25': len([n for n in base_20 if 21 <= n <= 25])
        }
        
        print(f"📊 Distribuição por faixas: {faixas_count}")
        
        # Verifica se tem números extremos (CORREÇÃO PRINCIPAL)
        extremos_baixos = [n for n in base_20 if n <= 5]
        extremos_altos = [n for n in base_20 if n >= 21]
        
        if extremos_baixos and extremos_altos:
            print(f"✅ CORREÇÃO OK: Extremos baixos {extremos_baixos}, altos {extremos_altos}")
        else:
            print(f"⚠️ ATENÇÃO: Poucos extremos - baixos {extremos_baixos}, altos {extremos_altos}")
    
    def selecionar_15_inteligente(self, base_20: List[int]) -> List[int]:
        """
        Seleciona 15 números da base de 20 com critérios SIMPLIFICADOS
        CORREÇÃO: Remove super-otimização que estava prejudicando
        """
        print("\n🧠 SELECIONANDO 15 DE 20 (CRITÉRIOS SIMPLIFICADOS)")
        print("=" * 50)
        
        scores = {}
        
        for num in base_20:
            score = 1.0  # Base simples
            
            # 1. FREQUÊNCIA SIMULADA EQUILIBRADA (não extremos)
            freq_simulada = abs(num - 13) / 12.0  # 0 a 1.0
            if freq_simulada <= 0.4:  # Próximo do centro
                score += 1.5
            elif freq_simulada <= 0.7:  # Moderadamente distante
                score += 1.0
            else:  # Extremos - AGORA COM VALOR POSITIVO (CORREÇÃO)
                score += 0.8  # Antes era muito penalizado
            
            # 2. DIVERSIDADE POR POSIÇÃO
            if num <= 5:      # Extremo baixo
                score += 1.0  # CORREÇÃO: valor aumentado
            elif num >= 21:   # Extremo alto  
                score += 1.0  # CORREÇÃO: valor aumentado
            elif 11 <= num <= 15:  # Centro
                score += 1.2
            else:             # Intermediários
                score += 1.1
            
            # 3. PADRÕES SIMPLES (não complexos)
            if num in self.numeros_primos:
                score += 0.3
            if num % 5 == 0:  # Múltiplos de 5
                score += 0.2
            if num % 2 == 1:  # Ímpares (leve preferência)
                score += 0.1
            
            scores[num] = score
        
        # SELEÇÃO COM DIVERSIDADE FORÇADA
        selecionados = []
        candidatos = sorted(base_20, key=lambda x: scores[x], reverse=True)
        
        # Força pelo menos 1 de cada extremo (CORREÇÃO CRÍTICA)
        extremos_baixos = [n for n in candidatos if n <= 5]
        extremos_altos = [n for n in candidatos if n >= 21]
        
        if extremos_baixos:
            melhor_baixo = max(extremos_baixos, key=lambda x: scores[x])
            selecionados.append(melhor_baixo)
            candidatos.remove(melhor_baixo)
        
        if extremos_altos:
            melhor_alto = max(extremos_altos, key=lambda x: scores[x])
            selecionados.append(melhor_alto)
            candidatos.remove(melhor_alto)
        
        # Completa com os melhores restantes evitando clusters
        while len(selecionados) < 15 and candidatos:
            melhor = candidatos[0]
            
            # Verifica se cria cluster excessivo
            cluster_ok = True
            for sel in selecionados:
                if abs(melhor - sel) <= 1:  # Consecutivo
                    cluster_count = sum(1 for s in selecionados if abs(s - melhor) <= 2)
                    if cluster_count >= 3:  # Limite de cluster
                        cluster_ok = False
                        break
            
            if cluster_ok:
                selecionados.append(melhor)
            candidatos.remove(melhor)
        
        selecionados.sort()
        
        print(f"✅ 15 selecionados: {selecionados}")
        print(f"📊 Scores: {[(n, f'{scores[n]:.1f}') for n in selecionados[:8]]}")
        
        return selecionados
    
    def gerar_desdobramento_c53(self, complementares: List[int], quantidade: int = 10) -> List[List[int]]:
        """
        Gera desdobramento C(5,3) dos números complementares
        """
        print(f"\n🎲 DESDOBRAMENTO C(5,3) - {len(complementares)} COMPLEMENTARES")
        print("=" * 50)
        
        if len(complementares) != 5:
            print(f"⚠️ Esperados 5 complementares, recebidos {len(complementares)}")
            return []
        
        # Gera todas as combinações C(5,3) = 10
        todas_combinacoes = list(combinations(complementares, 3))
        
        print(f"📊 Geradas {len(todas_combinacoes)} combinações C(5,3)")
        print(f"🎯 Complementares: {complementares}")
        
        # Avalia e seleciona as melhores
        combinacoes_avaliadas = []
        for combo in todas_combinacoes:
            score = self.avaliar_trio(list(combo))
            combinacoes_avaliadas.append((list(combo), score))
        
        # Ordena por score e retorna as melhores
        combinacoes_avaliadas.sort(key=lambda x: x[1], reverse=True)
        
        resultado = []
        for i, (combo, score) in enumerate(combinacoes_avaliadas[:quantidade]):
            resultado.append(combo)
            print(f"   Trio {i+1}: {combo} (score: {score:.1f})")
        
        return resultado
    
    def avaliar_trio(self, trio: List[int]) -> float:
        """Avalia a qualidade de um trio de números complementares"""
        score = 1.0
        
        # Diversidade de posições
        if max(trio) - min(trio) >= 3:  # Espalhado
            score += 1.0
        
        # Equilíbrio par/ímpar
        pares = sum(1 for n in trio if n % 2 == 0)
        if pares in [1, 2]:  # Mistura equilibrada
            score += 0.5
        
        # Primos
        primos = sum(1 for n in trio if n in self.numeros_primos)
        if primos >= 1:
            score += 0.3
        
        return score
    
    def gerar_sistema_completo(self, qtd_combinacoes: int = 15) -> List[List[int]]:
        """
        Gera um sistema completo de complementação inteligente
        VERSÃO CORRIGIDA com melhor distribuição
        """
        print("\n🔧 SISTEMA COMPLETO V2.0 - COMPLEMENTAÇÃO CORRIGIDA")
        print("=" * 60)
        
        resultado = []
        
        for i in range(qtd_combinacoes):
            print(f"\n🎯 Gerando combinação {i+1}/{qtd_combinacoes}")
            
            # 1. Gera base de 20 com distribuição corrigida
            base_20 = self.gerar_base_20_corrigida()
            
            # 2. Seleciona 15 inteligentemente
            base_15 = self.selecionar_15_inteligente(base_20)
            
            # 3. Identifica os 5 complementares (corrigido)
            complementares = [n for n in range(1, 26) if n not in base_20]
            print(f"   📋 Complementares (5): {complementares}")
            
            # 4. Seleciona o melhor trio C(5,3)
            if len(complementares) == 5:
                trios = self.gerar_desdobramento_c53(complementares, 1)
                if trios:
                    trio_escolhido = trios[0]
                    
                    # 5. Combina base_15 menos 3 números + trio complementar
                    base_12 = random.sample(base_15, 12)  # Remove 3 da base
                    combinacao_final = sorted(base_12 + trio_escolhido)
                    
                    resultado.append(combinacao_final)
                    print(f"✅ Combinação final: {combinacao_final}")
                else:
                    # Fallback: usa base_15 diretamente
                    resultado.append(base_15)
                    print(f"⚠️ Usando base_15 como fallback: {base_15}")
            else:
                # Fallback: usa base_15 diretamente
                resultado.append(base_15)
                print(f"⚠️ Complementares != 5, usando base_15: {base_15}")
        return resultado

def main():
    """Função principal para teste"""
    print("🔧 TESTE - COMPLEMENTAÇÃO INTELIGENTE V2.0")
    print("=" * 60)
    
    gerador = ComplementacaoInteligenteV2()
    
    # Gera 3 combinações de teste
    combinacoes = gerador.gerar_sistema_completo(3)
    
    print(f"\n🎯 RESULTADO FINAL - {len(combinacoes)} COMBINAÇÕES:")
    print("=" * 60)
    
    for i, combo in enumerate(combinacoes, 1):
        print(f"Jogo {i:2d}: {combo}")
        
        # Análise rápida
        extremos_baixos = [n for n in combo if n <= 5]
        extremos_altos = [n for n in combo if n >= 21]
        print(f"         Extremos baixos: {extremos_baixos}, altos: {extremos_altos}")
    
    print("\n✅ CORREÇÕES APLICADAS:")
    print("   • Força números extremos (1-5 e 21-25)")
    print("   • Simplifica critérios de scoring")
    print("   • Remove super-otimização prejudicial")
    print("   • Melhora distribuição equilibrada")

if __name__ == "__main__":
    main()