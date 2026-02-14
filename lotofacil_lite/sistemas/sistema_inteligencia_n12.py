#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA INTELIGENTE N12 - INTEGRAÇÃO PARA GERADORES
======================================================
Sistema para aplicar o aprendizado sobre N12 como termômetro
de distribuição em todos os geradores de combinações.

TEORIA COMPROVADA:
• N12 ≤ 18: Tendência BAIXOS/MÉDIOS
• N12 = 19: EQUILÍBRIO (pode oscilar para qualquer lado)
• N12 ≥ 20: Tendência ALTOS

Autor: AR CALHAU
Data: 19/09/2025
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import random
from collections import defaultdict

class SistemaInteligenciaDistribuicaoN12:
    def __init__(self):
        self.db_config = db_config
        self.ultimo_concurso = None
        self.ultimo_n12 = None
        self.distribuicao_atual = None
        self.predicao_proxima = None
        self.historico_oscillacao = []
        
        # Limites N12 dinâmicos baseados na análise histórica
        self.limites_n12 = self._calcular_limites_n12()
        
    def _calcular_limites_n12(self):
        """Calcula os limites N12 baseados na análise histórica da tabela"""
        try:
            if not self.db_config.test_connection():
                # Fallback para valores padrão se não conseguir conectar
                return {'limite_baixo': 18, 'limite_equilibrio': 19, 'limite_alto': 20}
                
            # Analisar distribuição histórica de N12
            query = """
            SELECT N12, 
                   SUM(CASE WHEN Faixa_Baixa > Faixa_Media AND Faixa_Baixa > Faixa_Alta THEN 1 ELSE 0 END) as Baixa_Count,
                   SUM(CASE WHEN Faixa_Media > Faixa_Baixa AND Faixa_Media > Faixa_Alta THEN 1 ELSE 0 END) as Media_Count,
                   SUM(CASE WHEN Faixa_Alta > Faixa_Baixa AND Faixa_Alta > Faixa_Media THEN 1 ELSE 0 END) as Alta_Count,
                   SUM(CASE WHEN Faixa_Baixa = Faixa_Media AND Faixa_Media = Faixa_Alta THEN 1 ELSE 0 END) as Equilibrio_Count,
                   COUNT(*) as Total
            FROM Resultados_INT 
            WHERE N12 BETWEEN 10 AND 25
            GROUP BY N12 
            ORDER BY N12
            """
            
            resultados = self.db_config.execute_query(query)
            
            if resultados:
                # Analisar tendências por N12
                limite_baixo = 18  # valor padrão
                limite_equilibrio = 19  # valor padrão
                limite_alto = 20  # valor padrão
                
                # Buscar o N12 com maior equilíbrio
                max_equilibrio_perc = 0
                for row in resultados:
                    n12, baixa_count, media_count, alta_count, equilibrio_count, total = row
                    
                    if total > 10:  # Apenas N12 com amostra suficiente
                        equilibrio_perc = equilibrio_count / total
                        if equilibrio_perc > max_equilibrio_perc:
                            max_equilibrio_perc = equilibrio_perc
                            limite_equilibrio = n12
                
                return {
                    'limite_baixo': limite_equilibrio - 1,
                    'limite_equilibrio': limite_equilibrio, 
                    'limite_alto': limite_equilibrio + 1
                }
            
        except Exception as e:
            print(f"⚠️ Erro ao calcular limites N12: {e}")
            
        # Fallback para valores padrão
        return {'limite_baixo': 18, 'limite_equilibrio': 19, 'limite_alto': 20}
        
    def analisar_situacao_atual(self):
        """Analisa a situação atual baseada no último concurso"""
        print("🔍 ANALISANDO SITUAÇÃO ATUAL COM BASE NO N12...")
        
        try:
            if not self.db_config.test_connection():
                print("❌ Erro na conexão")
                return False
                
            # Buscar último concurso
            query = """
            SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                   Faixa_Baixa, Faixa_Media, Faixa_Alta
            FROM Resultados_INT 
            ORDER BY Concurso DESC
            """
            
            resultado = self.db_config.execute_query(query)
            
            if resultado:
                row = resultado[0]
                self.ultimo_concurso = row[0]
                numeros = [row[i] for i in range(1, 16)]
                self.ultimo_n12 = row[12]  # N12
                faixa_baixa = row[16]
                faixa_media = row[17]
                faixa_alta = row[18]
                
                # Determinar distribuição atual
                if faixa_baixa > faixa_media and faixa_baixa > faixa_alta:
                    self.distribuicao_atual = "BAIXA"
                elif faixa_media > faixa_baixa and faixa_media > faixa_alta:
                    self.distribuicao_atual = "MEDIA"
                elif faixa_alta > faixa_baixa and faixa_alta > faixa_media:
                    self.distribuicao_atual = "ALTA"
                else:
                    self.distribuicao_atual = "EQUILIBRADA"
                
                print(f"📊 SITUAÇÃO ATUAL:")
                print(f"   🎯 Último concurso: {self.ultimo_concurso}")
                print(f"   📍 N12 atual: {self.ultimo_n12}")
                print(f"   📊 Distribuição: {self.distribuicao_atual}")
                print(f"   🔢 Faixas: B={faixa_baixa}, M={faixa_media}, A={faixa_alta}")
                
                return True
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def buscar_ultimo_concurso(self):
        """Busca os dados do último concurso para uso externo"""
        try:
            if not self.db_config.test_connection():
                print("❌ Erro na conexão")
                return None
                
            # Buscar último concurso
            query = """
            SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT 
            ORDER BY Concurso DESC
            """
            
            resultado = self.db_config.execute_query(query)
            
            if resultado:
                row = resultado[0]
                concurso = row[0]
                numeros = [row[i] for i in range(1, 16)]
                n12 = row[12]  # N12
                
                return {
                    'concurso': concurso,
                    'numeros': numeros,
                    'n12': n12
                }
            return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar último concurso: {e}")
            return None
    
    def prever_proxima_distribuicao(self):
        """Prevê a próxima distribuição com base na teoria N12 e oscilação"""
        if not self.ultimo_n12:
            return None
            
        print(f"\n🔮 PREVISÃO PARA PRÓXIMO CONCURSO:")
        print("-" * 40)
        
        # Análise baseada no N12 atual
        limite_baixo = self.limites_n12['limite_baixo']
        limite_equilibrio = self.limites_n12['limite_equilibrio'] 
        limite_alto = self.limites_n12['limite_alto']
        
        if self.ultimo_n12 <= limite_baixo:
            tendencia_base = "BAIXOS_MEDIOS"
            print(f"📈 N12={self.ultimo_n12} ≤ {limite_baixo} → Tendência: BAIXOS/MÉDIOS")
        elif self.ultimo_n12 >= limite_alto:
            tendencia_base = "ALTOS"
            print(f"📈 N12={self.ultimo_n12} ≥ {limite_alto} → Tendência: ALTOS")
        else:  # N12 == limite_equilibrio
            tendencia_base = "EQUILIBRIO_OSCILACAO"
            print(f"📈 N12={self.ultimo_n12} = {limite_equilibrio} → EQUILÍBRIO: Pode oscilar para qualquer lado!")
        
        # Análise da oscilação (se estamos em equilíbrio)
        if self.distribuicao_atual == "EQUILIBRADA":
            print(f"⚖️ Situação atual: EQUILÍBRIO PERFEITO")
            print(f"🔄 Próximo: Alta probabilidade de OSCILAÇÃO")
            
            if tendencia_base == "EQUILIBRIO_OSCILACAO":
                self.predicao_proxima = {
                    'tipo': 'OSCILACAO_LIVRE',
                    'opcoes': ['BAIXA', 'MEDIA', 'ALTA'],
                    'probabilidades': [35, 30, 35],  # Ligeiramente favorável aos extremos
                    'estrategia': 'DIVERSIFICADA_EXTREMOS'
                }
            elif tendencia_base == "BAIXOS_MEDIOS":
                self.predicao_proxima = {
                    'tipo': 'OSCILACAO_BAIXA_MEDIA',
                    'opcoes': ['BAIXA', 'MEDIA'],
                    'probabilidades': [45, 55],
                    'estrategia': 'FOCAR_BAIXOS_MEDIOS'
                }
            else:  # ALTOS
                self.predicao_proxima = {
                    'tipo': 'OSCILACAO_PARA_ALTOS',
                    'opcoes': ['ALTA'],
                    'probabilidades': [70],
                    'estrategia': 'FOCAR_ALTOS'
                }
        else:
            # Não estamos em equilíbrio, aplicar lógica de OSCILAÇÃO CONTRÁRIA
            print(f"🔄 TEORIA OSCILAÇÃO: Atual {self.distribuicao_atual} → Próximo tende ao CONTRÁRIO")
            
            if self.distribuicao_atual == "BAIXA":
                # Se atual é BAIXA, próximo tende para MÉDIA/ALTA
                self.predicao_proxima = {
                    'tipo': 'OSCILACAO_CONTRARIA_BAIXA',
                    'opcoes': ['MEDIA', 'ALTA'],
                    'probabilidades': [55, 45],
                    'estrategia': 'PRIVILEGIAR_MEDIOS_ALTOS'
                }
                print(f"   🎯 Atual BAIXA → Próximo: MÉDIA (55%), ALTA (45%)")
                
            elif self.distribuicao_atual == "MEDIA":
                # Se atual é MÉDIA, próximo pode oscilar para BAIXA ou ALTA
                self.predicao_proxima = {
                    'tipo': 'OSCILACAO_CONTRARIA_MEDIA',
                    'opcoes': ['BAIXA', 'ALTA'],
                    'probabilidades': [50, 50],
                    'estrategia': 'PRIVILEGIAR_EXTREMOS'
                }
                print(f"   🎯 Atual MÉDIA → Próximo: BAIXA (50%), ALTA (50%)")
                
            elif self.distribuicao_atual == "ALTA":
                # Se atual é ALTA, próximo tende para BAIXA/MÉDIA
                self.predicao_proxima = {
                    'tipo': 'OSCILACAO_CONTRARIA_ALTA', 
                    'opcoes': ['BAIXA', 'MEDIA'],
                    'probabilidades': [45, 55],
                    'estrategia': 'PRIVILEGIAR_BAIXOS_MEDIOS'
                }
                print(f"   🎯 Atual ALTA → Próximo: BAIXA (45%), MÉDIA (55%)")
                
            else:  # EQUILIBRIO_OSCILACAO ou outros casos
                self.predicao_proxima = {
                    'tipo': 'EQUILIBRIO_NATURAL',
                    'opcoes': ['BAIXA', 'MEDIA', 'ALTA'],
                    'probabilidades': [33, 34, 33],
                    'estrategia': 'MANTER_EQUILIBRIO'
                }
        
        print(f"\n🎯 PREVISÃO DETALHADA:")
        for i, opcao in enumerate(self.predicao_proxima['opcoes']):
            prob = self.predicao_proxima['probabilidades'][i]
            print(f"   • {opcao}: {prob}% de probabilidade")
        
        print(f"🔧 Estratégia recomendada: {self.predicao_proxima['estrategia']}")
        
        return self.predicao_proxima
    
    def aplicar_filtro_inteligente_n12(self, combinacoes_candidatas):
        """Aplica filtro inteligente baseado na predição N12"""
        if not self.predicao_proxima:
            return combinacoes_candidatas
            
        print(f"\n🔧 APLICANDO FILTRO INTELIGENTE N12...")
        print(f"📊 Estratégia: {self.predicao_proxima['estrategia']}")
        
        combinacoes_filtradas = []
        
        for combinacao in combinacoes_candidatas:
            # Calcular N12 da combinação (12ª posição)
            n12_combinacao = combinacao[11]
            
            # Calcular distribuição da combinação
            baixos = len([n for n in combinacao if 1 <= n <= 8])
            medios = len([n for n in combinacao if 9 <= n <= 17])
            altos = len([n for n in combinacao if 18 <= n <= 25])
            
            # Determinar distribuição dominante
            if baixos > medios and baixos > altos:
                dist_combinacao = "BAIXA"
            elif medios > baixos and medios > altos:
                dist_combinacao = "MEDIA"
            elif altos > baixos and altos > medios:
                dist_combinacao = "ALTA"
            else:
                dist_combinacao = "EQUILIBRADA"
            
            # Aplicar critérios baseados na estratégia
            score_combinacao = 0
            
            if self.predicao_proxima['estrategia'] == 'DIVERSIFICADA_EXTREMOS':
                # Favorecer N12 próximo ao equilíbrio mas permitir variação
                if 17 <= n12_combinacao <= 21:
                    score_combinacao += 3
                if dist_combinacao in ['BAIXA', 'ALTA']:
                    score_combinacao += 2
                    
            elif self.predicao_proxima['estrategia'] == 'FOCAR_BAIXOS_MEDIOS':
                # Favorecer N12 <= 18 e distribuição baixa/média
                if n12_combinacao <= 18:
                    score_combinacao += 3
                if dist_combinacao in ['BAIXA', 'MEDIA']:
                    score_combinacao += 2
                    
            elif self.predicao_proxima['estrategia'] == 'FOCAR_ALTOS':
                # Favorecer N12 >= 20 e distribuição alta
                if n12_combinacao >= 20:
                    score_combinacao += 3
                if dist_combinacao == 'ALTA':
                    score_combinacao += 2
                    
            elif self.predicao_proxima['estrategia'] == 'PRIVILEGIAR_BAIXOS_MEDIOS':
                # Priorizar baixos/médios mas com menos rigor
                if n12_combinacao <= 19:
                    score_combinacao += 2
                if dist_combinacao in ['BAIXA', 'MEDIA']:
                    score_combinacao += 1
                    
            elif self.predicao_proxima['estrategia'] == 'PRIVILEGIAR_ALTOS':
                # Priorizar altos mas com menos rigor  
                if n12_combinacao >= self.limites_n12['limite_equilibrio']:
                    score_combinacao += 2
                if dist_combinacao == 'ALTA':
                    score_combinacao += 1
                    
            elif self.predicao_proxima['estrategia'] == 'PRIVILEGIAR_MEDIOS_ALTOS':
                # Priorizar médios e altos (oscilação contrária de BAIXA)
                if n12_combinacao >= self.limites_n12['limite_equilibrio']:
                    score_combinacao += 3
                if dist_combinacao in ['MEDIA', 'ALTA']:
                    score_combinacao += 2
                    
            elif self.predicao_proxima['estrategia'] == 'PRIVILEGIAR_EXTREMOS':
                # Priorizar baixos e altos (oscilação contrária de MÉDIA)
                if n12_combinacao <= self.limites_n12['limite_baixo'] or n12_combinacao >= self.limites_n12['limite_alto']:
                    score_combinacao += 3
                if dist_combinacao in ['BAIXA', 'ALTA']:
                    score_combinacao += 2
                    
            elif self.predicao_proxima['estrategia'] == 'DIVERSIFICAR_COM_ENFASE_EXTREMOS':
                # Estratégia equilibrada mas privilegiando extremos
                if self.limites_n12['limite_baixo'] <= n12_combinacao <= self.limites_n12['limite_alto']:
                    score_combinacao += 2
                if dist_combinacao in ['BAIXA', 'ALTA']:
                    score_combinacao += 1
                    
            elif self.predicao_proxima['estrategia'] == 'MANTER_EQUILIBRIO':
                # Favorecer combinações equilibradas
                if self.limites_n12['limite_baixo'] <= n12_combinacao <= self.limites_n12['limite_alto']:
                    score_combinacao += 2
                if dist_combinacao == 'EQUILIBRADA':
                    score_combinacao += 3
            
            # Incluir combinação sempre, priorizando por score
            # Para garantir que temos combinações para gerar
            combinacoes_filtradas.append({
                'combinacao': combinacao,
                'n12': n12_combinacao,
                    'distribuicao': dist_combinacao,
                    'score': score_combinacao,
                    'baixos': baixos,
                    'medios': medios,
                    'altos': altos
                })
        
        # Ordenar por score decrescente
        combinacoes_filtradas.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Filtradas: {len(combinacoes_filtradas)} de {len(combinacoes_candidatas)} combinações")
        
        return combinacoes_filtradas
    
    def gerar_relatorio_estrategia(self):
        """Gera relatório da estratégia atual"""
        print(f"\n📋 RELATÓRIO DA ESTRATÉGIA N12")
        print("="*50)
        print(f"🎯 Último concurso: {self.ultimo_concurso}")
        print(f"📍 N12 atual: {self.ultimo_n12}")
        print(f"📊 Distribuição atual: {self.distribuicao_atual}")
        
        if self.predicao_proxima:
            print(f"\n🔮 PREVISÃO PRÓXIMO CONCURSO:")
            print(f"🔧 Estratégia: {self.predicao_proxima['estrategia']}")
            print(f"🎲 Opções prováveis: {', '.join(self.predicao_proxima['opcoes'])}")
            
            # Dicas práticas
            print(f"\n💡 DICAS PARA GERADORES:")
            if 'BAIXOS_MEDIOS' in self.predicao_proxima['estrategia']:
                print("   • Priorizar números 1-17")
                print("   • N12 ideal: ≤ 18")
                print("   • Evitar muitos números 20-25")
            elif 'ALTOS' in self.predicao_proxima['estrategia']:
                print("   • Priorizar números 18-25")
                print("   • N12 ideal: ≥ 20")
                print("   • Equilibrar com alguns médios")
            elif 'EQUILIBRIO' in self.predicao_proxima['estrategia']:
                print("   • Distribuição balanceada 5-5-5")
                print("   • N12 ideal: 18-20")
                print("   • Aproveitar a oscilação natural")
            elif 'OSCILACAO' in self.predicao_proxima['estrategia']:
                print("   • ALTA PROBABILIDADE DE MUDANÇA!")
                print("   • Preparar para os extremos")
                print("   • N12 pode variar bastante")

def integrar_sistema_n12_em_gerador(gerador_funcao):
    """Decorador para integrar sistema N12 em qualquer gerador"""
    def wrapper(*args, **kwargs):
        # Inicializar sistema N12
        sistema_n12 = SistemaInteligenciaDistribuicaoN12()
        sistema_n12.analisar_situacao_atual()
        sistema_n12.prever_proxima_distribuicao()
        sistema_n12.gerar_relatorio_estrategia()
        
        # Executar gerador original
        combinacoes_originais = gerador_funcao(*args, **kwargs)
        
        # Aplicar filtro inteligente N12
        if isinstance(combinacoes_originais, list) and len(combinacoes_originais) > 0:
            combinacoes_otimizadas = sistema_n12.aplicar_filtro_inteligente_n12(combinacoes_originais)
            return combinacoes_otimizadas
        
        return combinacoes_originais
    
    return wrapper

if __name__ == "__main__":
    # Teste do sistema
    sistema = SistemaInteligenciaDistribuicaoN12()
    sistema.analisar_situacao_atual()
    sistema.prever_proxima_distribuicao()
    sistema.gerar_relatorio_estrategia()