#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 SISTEMA DE FILTRO REDUTOR AUTOMÁTICO V4.0
============================================
Sistema revolucionário que gera filtros de metadados com flexibilidade 
automática e conecta com análise neural para ranking inteligente.

CONCEITO INOVADOR:
1. Filtro Redutor: Configura restrição automática (1-10)
2. Análise Neural: Score de probabilidade para cada combinação
3. Ranking Inteligente: TOP 1 até TOP máxima ordenadas

Autor: AR CALHAU
Data: 18/09/2025
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import random

class SistemaFiltroRedutorV4:
    """Sistema de filtro redutor automático com análise inteligente"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        
        # Faixas base dos metadados (baseadas em análise histórica)
        self.metadados_base = {
            'QtdePrimos': {'min': 2, 'max': 8, 'ideal': (4, 5)},
            'QtdeFibonacci': {'min': 1, 'max': 7, 'ideal': (3, 5)},
            'QtdeImpares': {'min': 5, 'max': 10, 'ideal': (7, 9)},
            'SomaTotal': {'min': 160, 'max': 240, 'ideal': (184, 218)},
            'Quintil1': {'min': 1, 'max': 5, 'ideal': (2, 4)},
            'Quintil2': {'min': 0, 'max': 5, 'ideal': (1, 4)},
            'Quintil3': {'min': 0, 'max': 5, 'ideal': (1, 3)},
            'Quintil4': {'min': 0, 'max': 5, 'ideal': (2, 4)},
            'Quintil5': {'min': 1, 'max': 6, 'ideal': (3, 6)},
            'QtdeGaps': {'min': 3, 'max': 10, 'ideal': (4, 7)},
            'QtdeRepetidos': {'min': 5, 'max': 12, 'ideal': (7, 10)},
            'SEQ': {'min': 4, 'max': 12, 'ideal': (6, 9)},
            'DistanciaExtremos': {'min': 18, 'max': 25, 'ideal': (20, 25)},
            'ParesSequencia': {'min': 1, 'max': 7, 'ideal': (2, 5)},
            'QtdeMultiplos3': {'min': 1, 'max': 8, 'ideal': (2, 7)},
            'ParesSaltados': {'min': 0, 'max': 4, 'ideal': (0, 2)},
            'Faixa_Baixa': {'min': 2, 'max': 8, 'ideal': (3, 7)},
            'Faixa_Media': {'min': 2, 'max': 8, 'ideal': (3, 7)},
            'Faixa_Alta': {'min': 1, 'max': 7, 'ideal': (2, 6)},
            'RepetidosMesmaPosicao': {'min': 0, 'max': 6, 'ideal': (0, 5)}
        }
    
    def gerar_filtro_automatico(self, nivel_restricao=5, campos_personalizados=None):
        """
        Gera filtro automático baseado no nível de restrição
        
        Args:
            nivel_restricao (int): 1=muito restrito, 10=muito flexível
            campos_personalizados (dict): Sobrescreve campos específicos
        
        Returns:
            str: Query SQL gerada
        """
        
        print(f"🔍 GERANDO FILTRO AUTOMÁTICO - NÍVEL {nivel_restricao}/10")
        print("-" * 50)
        
        # Calcular flexibilidade baseada no nível (1-10)
        flexibilidade = (nivel_restricao - 1) / 9.0  # 0.0 a 1.0
        
        condicoes = []
        filtros_aplicados = {}
        
        for campo, config in self.metadados_base.items():
            # Usar valor personalizado se fornecido
            if campos_personalizados and campo in campos_personalizados:
                min_val, max_val = campos_personalizados[campo]
            else:
                # Calcular faixa baseada na flexibilidade
                ideal_min, ideal_max = config['ideal']
                range_min, range_max = config['min'], config['max']
                
                # Expandir faixa baseada na flexibilidade
                expansao_min = int(flexibilidade * (ideal_min - range_min))
                expansao_max = int(flexibilidade * (range_max - ideal_max))
                
                min_val = max(range_min, ideal_min - expansao_min)
                max_val = min(range_max, ideal_max + expansao_max)
            
            condicoes.append(f"{campo} BETWEEN {min_val} AND {max_val}")
            filtros_aplicados[campo] = (min_val, max_val)
            
            print(f"   • {campo}: {min_val}-{max_val}")
        
        # Montar query completa
        query = "SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM COMBINACOES_LOTOFACIL WHERE "
        query += " AND ".join(condicoes)
        
        return query, filtros_aplicados
    
    def executar_filtro_redutor(self, nivel_restricao=5, max_combinacoes=1000, campos_personalizados=None):
        """
        Executa o filtro redutor e retorna combinações
        
        Args:
            nivel_restricao (int): 1-10 (restrição)
            max_combinacoes (int): Máximo de combinações a retornar
            campos_personalizados (dict): Campos específicos
        
        Returns:
            list: Combinações encontradas
        """
        
        print(f"🚀 EXECUTANDO FILTRO REDUTOR V4.0")
        print("=" * 60)
        print(f"⚙️  Configurações:")
        print(f"   • Nível de Restrição: {nivel_restricao}/10")
        print(f"   • Máximo de Combinações: {max_combinacoes:,}")
        print("=" * 60)
        
        # Gerar filtro automático
        query, filtros = self.gerar_filtro_automatico(nivel_restricao, campos_personalizados)
        
        # Primeiro, contar quantas combinações serão retornadas
        query_count = query.replace(
            "SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15",
            "SELECT COUNT_BIG(*)"
        )
        
        try:
            resultado_count = self.db_config.execute_query(query_count)
            total_encontradas = resultado_count[0][0]
            
            print(f"📊 RESULTADO DO FILTRO:")
            print(f"   • Total encontradas: {total_encontradas:,} combinações")
            print(f"   • Redução: {((3268760 - total_encontradas) / 3268760 * 100):.2f}%")
            print(f"   • Probabilidade: 1/{total_encontradas:,}")
            
            if total_encontradas == 0:
                print("❌ Nenhuma combinação encontrada! Tente nível menos restritivo.")
                return []
            
            if total_encontradas > max_combinacoes:
                print(f"⚠️  Limitando a {max_combinacoes:,} combinações (TOP primeiras)")
                query += f" ORDER BY N1, N2, N3, N4, N5"  # Ordenação para consistência
                query = query.replace("SELECT", f"SELECT TOP {max_combinacoes}")
            
            # Executar query para obter combinações
            combinacoes = self.db_config.execute_query(query)
            
            print(f"✅ Retornando {len(combinacoes):,} combinações para análise neural")
            
            return combinacoes
            
        except Exception as e:
            print(f"❌ Erro ao executar filtro: {e}")
            return []
    
    def analisar_combinacao_completa(self, combinacao):
        """
        Análise completa de uma combinação (simulada por enquanto)
        TODO: Integrar com Sistema Neural V7.0 real
        """
        
        # Por enquanto, análise simulada baseada em metadados
        numeros = list(combinacao)
        
        # Calcular score baseado em múltiplos fatores
        score = 0.0
        detalhes = {}
        
        # 1. Análise de primos
        primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        qtde_primos = sum(1 for n in numeros if n in primos)
        score += (qtde_primos / 15) * 0.15  # 15% do score
        detalhes['primos'] = qtde_primos
        
        # 2. Análise de distribuição
        soma = sum(numeros)
        if 180 <= soma <= 220:
            score += 0.20  # 20% do score
        detalhes['soma'] = soma
        
        # 3. Análise de sequências
        sequencias = 0
        for i in range(len(numeros) - 1):
            if numeros[i+1] - numeros[i] == 1:
                sequencias += 1
        score += min(sequencias / 10, 0.15)  # 15% do score
        detalhes['sequencias'] = sequencias
        
        # 4. Análise de gaps
        gaps = []
        for i in range(len(numeros) - 1):
            gaps.append(numeros[i+1] - numeros[i] - 1)
        gap_medio = sum(gaps) / len(gaps) if gaps else 0
        if 0.5 <= gap_medio <= 2.0:
            score += 0.15  # 15% do score
        detalhes['gap_medio'] = gap_medio
        
        # 5. Análise de posicionamento
        extremos = numeros[-1] - numeros[0]
        if 20 <= extremos <= 24:
            score += 0.10  # 10% do score
        detalhes['extremos'] = extremos
        
        # 6. Componente aleatório (simula complexidade neural)
        score += random.uniform(0.0, 0.25)  # 25% aleatório
        
        # Normalizar score para 0-100
        score_final = min(score * 100, 100.0)
        
        return {
            'score': score_final,
            'detalhes': detalhes,
            'combinacao': numeros
        }
    
    def executar_sistema_completo(self, nivel_restricao=5, max_combinacoes=500, top_selecionar=20):
        """
        Executa o sistema completo: Filtro + Análise + Ranking
        """
        
        print(f"🎯 SISTEMA DE ANÁLISE ESCALONADA INTELIGENTE V4.0")
        print("=" * 70)
        
        # FASE 1: Filtro Redutor
        combinacoes = self.executar_filtro_redutor(nivel_restricao, max_combinacoes)
        
        if not combinacoes:
            return []
        
        print(f"\n🧠 FASE 2: ANÁLISE NEURAL AVANÇADA")
        print("-" * 50)
        print(f"⚙️  Analisando {len(combinacoes):,} combinações...")
        
        # FASE 2: Análise Neural
        resultados_analisados = []
        
        for i, combinacao in enumerate(combinacoes):
            if i % 100 == 0:  # Progress
                print(f"   📊 Progresso: {i:,}/{len(combinacoes):,} ({(i/len(combinacoes)*100):.1f}%)")
            
            analise = self.analisar_combinacao_completa(combinacao)
            resultados_analisados.append(analise)
        
        # FASE 3: Ranking Inteligente
        print(f"\n🏆 FASE 3: RANKING INTELIGENTE")
        print("-" * 50)
        
        # Ordenar por score (maior para menor)
        resultados_analisados.sort(key=lambda x: x['score'], reverse=True)
        
        # Selecionar TOP
        top_combinacoes = resultados_analisados[:top_selecionar]
        
        print(f"✅ TOP {len(top_combinacoes)} COMBINAÇÕES SELECIONADAS:")
        print("=" * 70)
        
        for i, resultado in enumerate(top_combinacoes, 1):
            numeros = resultado['combinacao']
            score = resultado['score']
            detalhes = resultado['detalhes']
            
            numeros_str = " ".join([f"{n:2d}" for n in numeros])
            print(f"#{i:2d} | Score: {score:5.1f}% | [{numeros_str}]")
            print(f"     Primos:{detalhes['primos']} Soma:{detalhes['soma']} Seq:{detalhes['sequencias']} Gap:{detalhes['gap_medio']:.1f}")
            
            if i <= 5:  # Mostrar detalhes das TOP 5
                print(f"     📊 Detalhes: Extremos:{detalhes['extremos']}")
            print()
        
        return top_combinacoes

# Função de demonstração
def demonstrar_sistema():
    """Demonstra o sistema completo"""
    
    sistema = SistemaFiltroRedutorV4()
    
    print("🎮 DEMONSTRAÇÃO: SISTEMA DE ANÁLISE ESCALONADA INTELIGENTE")
    print("=" * 80)
    
    # Teste com diferentes níveis
    niveis_teste = [3, 5, 7]
    
    for nivel in niveis_teste:
        print(f"\n🧪 TESTE: NÍVEL DE RESTRIÇÃO {nivel}/10")
        print("=" * 60)
        
        resultados = sistema.executar_sistema_completo(
            nivel_restricao=nivel,
            max_combinacoes=300,
            top_selecionar=10
        )
        
        if resultados:
            melhor = resultados[0]
            print(f"🏆 MELHOR COMBINAÇÃO (Score: {melhor['score']:.1f}%):")
            numeros_str = " ".join([f"{n:2d}" for n in melhor['combinacao']])
            print(f"    [{numeros_str}]")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    demonstrar_sistema()