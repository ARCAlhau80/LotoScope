#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA DE ANÁLISE SEQUENCIAL DE PADRÕES
Analisa padrões sequenciais e probabilidades de transição para TODOS os filtros
Implementa sistema inteligente de redução baseado em análise temporal
Autor: AR CALHAU
Data: 11 de Agosto de 2025
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from collections import defaultdict, Counter
import statistics
import warnings
from datetime import datetime
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


# Suprimir warnings
warnings.filterwarnings('ignore', category=FutureWarning)


class SistemaAnaliseSequencial:
    """
    🧠 Sistema de Análise Sequencial de Padrões
    Analisa padrões sequenciais e probabilidades de transição para TODOS os filtros
    """
    
    def __init__(self):
        """Inicializa o sistema de análise sequencial"""
        self.filtros_monitorados = [
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'QtdeGaps', 'QtdeRepetidos', 'DistanciaExtremos', 'ParesSequencia',
            'QtdeMultiplos3', 'ParesSaltados', 'Faixa_Baixa', 'Faixa_Media',
            'Faixa_Alta', 'RepetidosMesmaPosicao'
        ]
        
        # Ranges esperados para cada filtro
        self.ranges_filtros = {
            'QtdePrimos': list(range(0, 9)),           # 0-8 números primos
            'QtdeFibonacci': list(range(0, 8)),        # 0-7 fibonacci
            'QtdeImpares': list(range(0, 16)),         # 0-15 ímpares
            'SomaTotal': list(range(100, 301)),        # Soma total 100-300
            'Quintil1': list(range(0, 6)),             # 0-5 números quintil 1
            'Quintil2': list(range(0, 6)),             # 0-5 números quintil 2
            'Quintil3': list(range(0, 6)),             # 0-5 números quintil 3
            'Quintil4': list(range(0, 6)),             # 0-5 números quintil 4
            'Quintil5': list(range(0, 6)),             # 0-5 números quintil 5
            'QtdeGaps': list(range(0, 16)),            # 0-15 gaps
            'QtdeRepetidos': list(range(0, 16)),       # 0-15 repetidos
            'DistanciaExtremos': list(range(4, 25)),   # 4-24 distância
            'ParesSequencia': list(range(0, 8)),       # 0-7 pares sequenciais
            'QtdeMultiplos3': list(range(0, 9)),       # 0-8 múltiplos de 3
            'ParesSaltados': list(range(0, 8)),        # 0-7 pares saltados
            'Faixa_Baixa': list(range(0, 11)),         # 0-10 faixa baixa
            'Faixa_Media': list(range(0, 11)),         # 0-10 faixa média
            'Faixa_Alta': list(range(0, 11)),          # 0-10 faixa alta
            'RepetidosMesmaPosicao': list(range(0, 16)) # 0-15 repetidos mesma posição
        }
        
        self.analise_historica = {}
        self.padroes_sequenciais = {}
        self.probabilidades_transicao = {}
        
        print("🧠 Sistema de Análise Sequencial inicializado")
        print(f"📊 Monitorando {len(self.filtros_monitorados)} filtros estatísticos")
        print(f"🎯 Análise sequencial para detecção de padrões temporais")
    
    def carregar_dados_historicos_completos(self) -> bool:
        """
        Carrega dados históricos completos para análise sequencial
        
        Returns:
            bool: True se carregou com sucesso
        """
        try:
            print("🔄 Carregando dados históricos para análise sequencial...")
            
            with db_config.get_connection() as conn:
                query = """
                SELECT 
                    Concurso, QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal,
                    Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                    QtdeGaps, QtdeRepetidos, DistanciaExtremos, ParesSequencia,
                    QtdeMultiplos3, ParesSaltados, Faixa_Baixa, Faixa_Media,
                    Faixa_Alta, RepetidosMesmaPosicao
                FROM Resultados_INT
                ORDER BY Concurso ASC
                """
                
                self.dados_historicos = pd.read_sql(query, conn)
                
                if len(self.dados_historicos) == 0:
                    print("❌ Nenhum dado histórico encontrado")
                    return False
                
                print(f"✅ {len(self.dados_historicos)} concursos carregados")
                print(f"📅 Período: {self.dados_historicos['Concurso'].min()} até {self.dados_historicos['Concurso'].max()}")
                
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados históricos: {str(e)}")
            return False
    
    def analisar_frequencias_historicas(self) -> Dict:
        """
        FASE 1: Análise Histórica Completa
        Mapeia frequências de cada valor para todos os filtros
        
        Returns:
            Dict: Análise de frequências por filtro
        """
        print(f"\n📊 FASE 1 - ANÁLISE HISTÓRICA COMPLETA")
        print("=" * 60)
        
        if not hasattr(self, 'dados_historicos') or self.dados_historicos is None:
            if not self.carregar_dados_historicos_completos():
                return {'erro': 'Não foi possível carregar dados históricos'}
        
        frequencias_por_filtro = {}
        
        for filtro in self.filtros_monitorados:
            if filtro not in self.dados_historicos.columns:
                print(f"⚠️  Filtro {filtro} não encontrado nos dados")
                continue
            
            print(f"🔍 Analisando frequências: {filtro}")
            
            # Conta frequências de cada valor
            frequencias = self.dados_historicos[filtro].value_counts().sort_index()
            total_concursos = len(self.dados_historicos)
            
            # Calcula percentuais e ranking
            analise_filtro = {
                'total_concursos': total_concursos,
                'valores_encontrados': len(frequencias),
                'frequencias_absolutas': frequencias.to_dict(),
                'frequencias_percentuais': (frequencias / total_concursos * 100).to_dict(),
                'valor_mais_comum': frequencias.idxmax(),
                'valor_mais_raro': frequencias.idxmin(),
                'frequencia_maxima': frequencias.max(),
                'frequencia_minima': frequencias.min(),
                'ranking_valores': frequencias.sort_values(ascending=False).to_dict()
            }
            
            frequencias_por_filtro[filtro] = analise_filtro
            
            # Exibe resumo
            mais_comum = analise_filtro['valor_mais_comum']
            freq_mais_comum = analise_filtro['frequencias_percentuais'][mais_comum]
            print(f"   📈 Mais comum: {mais_comum} ({freq_mais_comum:.1f}%)")
            
            # Mostra top 3
            top_3 = list(analise_filtro['ranking_valores'].items())[:3]
            for i, (valor, freq) in enumerate(top_3):
                perc = analise_filtro['frequencias_percentuais'][valor]
                emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                print(f"   {emoji} {valor}: {freq} vezes ({perc:.1f}%)")
        
        self.analise_historica = frequencias_por_filtro
        
        print(f"\n✅ Análise histórica concluída para {len(frequencias_por_filtro)} filtros")
        return frequencias_por_filtro
    
    def detectar_sequencias_temporais(self, janela_analise: List[int] = [15, 10, 5, 3]) -> Dict:
        """
        FASE 2: Análise de Sequências Temporais
        Detecta padrões sequenciais nos últimos N sorteios
        
        Args:
            janela_analise: Lista com tamanhos de janela para análise [15, 10, 5, 3]
            
        Returns:
            Dict: Padrões sequenciais detectados
        """
        print(f"\n🔍 FASE 2 - ANÁLISE DE SEQUÊNCIAS TEMPORAIS")
        print("=" * 60)
        print(f"📊 Janelas de análise: {janela_analise}")
        
        if not hasattr(self, 'dados_historicos') or self.dados_historicos is None:
            return {'erro': 'Dados históricos não carregados'}
        
        sequencias_detectadas = {}
        dados_recentes = self.dados_historicos.tail(max(janela_analise))
        
        for filtro in self.filtros_monitorados:
            if filtro not in self.dados_historicos.columns:
                continue
            
            print(f"🔍 Detectando sequências: {filtro}")
            
            analise_filtro = {
                'sequencias_por_janela': {},
                'sequencias_ativas': [],
                'padroes_repetitivos': [],
                'valor_atual': None,
                'tendencia_detectada': None
            }
            
            # Pega valor mais recente
            if len(dados_recentes) > 0:
                analise_filtro['valor_atual'] = dados_recentes[filtro].iloc[-1]
            
            # Analisa cada janela temporal
            for janela in janela_analise:
                if len(dados_recentes) < janela:
                    continue
                
                # Pega últimos N valores
                ultimos_valores = dados_recentes[filtro].tail(janela).tolist()
                
                # Detecta sequências de valores iguais
                sequencias_iguais = self._detectar_sequencias_iguais(ultimos_valores)
                
                # Detecta padrões alternados
                padroes_alternados = self._detectar_padroes_alternados(ultimos_valores)
                
                # Detecta tendências crescentes/decrescentes
                tendencias = self._detectar_tendencias(ultimos_valores)
                
                analise_janela = {
                    'tamanho_janela': janela,
                    'valores': ultimos_valores,
                    'sequencias_iguais': sequencias_iguais,
                    'padroes_alternados': padroes_alternados,
                    'tendencias': tendencias,
                    'valor_mais_frequente': max(set(ultimos_valores), key=ultimos_valores.count),
                    'frequencia_mais_comum': ultimos_valores.count(max(set(ultimos_valores), key=ultimos_valores.count))
                }
                
                analise_filtro['sequencias_por_janela'][janela] = analise_janela
                
                # Identifica sequências ativas (valor repetindo no final)
                if len(sequencias_iguais) > 0:
                    ultima_sequencia = sequencias_iguais[-1]
                    if ultima_sequencia['fim'] == len(ultimos_valores) - 1:  # Sequência ativa no final
                        analise_filtro['sequencias_ativas'].append({
                            'janela': janela,
                            'valor': ultima_sequencia['valor'],
                            'tamanho': ultima_sequencia['tamanho'],
                            'inicio': ultima_sequencia['inicio'],
                            'probabilidade_continuacao': self._calcular_prob_continuacao(filtro, ultima_sequencia['valor'], ultima_sequencia['tamanho'])
                        })
            
            sequencias_detectadas[filtro] = analise_filtro
            
            # Exibe resumo das sequências ativas
            if analise_filtro['sequencias_ativas']:
                print(f"   🔥 Sequências ativas detectadas:")
                for seq in analise_filtro['sequencias_ativas']:
                    valor = seq['valor']
                    tamanho = seq['tamanho']
                    prob = seq['probabilidade_continuacao']
                    print(f"      📊 Valor {valor} repetindo por {tamanho} sorteios (prob. cont.: {prob:.1f}%)")
            else:
                valor_atual = analise_filtro['valor_atual']
                print(f"   📊 Valor atual: {valor_atual} (sem sequência ativa)")
        
        self.padroes_sequenciais = sequencias_detectadas
        
        print(f"\n✅ Análise sequencial concluída para {len(sequencias_detectadas)} filtros")
        return sequencias_detectadas
    
    def _detectar_sequencias_iguais(self, valores: List[int]) -> List[Dict]:
        """
        Detecta sequências de valores iguais consecutivos
        
        Args:
            valores: Lista de valores para analisar
            
        Returns:
            List[Dict]: Lista de sequências encontradas
        """
        if not valores:
            return []
        
        sequencias = []
        i = 0
        
        while i < len(valores):
            valor_atual = valores[i]
            inicio = i
            
            # Conta quantos valores iguais consecutivos
            while i < len(valores) and valores[i] == valor_atual:
                i += 1
            
            tamanho = i - inicio
            
            # Só considera sequências de 2 ou mais
            if tamanho >= 2:
                sequencias.append({
                    'valor': valor_atual,
                    'tamanho': tamanho,
                    'inicio': inicio,
                    'fim': i - 1
                })
        
        return sequencias
    
    def _detectar_padroes_alternados(self, valores: List[int]) -> List[Dict]:
        """
        Detecta padrões alternados (ex: A-B-A-B-A)
        
        Args:
            valores: Lista de valores para analisar
            
        Returns:
            List[Dict]: Lista de padrões alternados encontrados
        """
        if len(valores) < 4:
            return []
        
        padroes = []
        
        # Tenta detectar alternância de 2 valores
        for i in range(len(valores) - 3):
            # Verifica padrão A-B-A-B
            if (valores[i] == valores[i+2] and 
                valores[i+1] == valores[i+3] and 
                valores[i] != valores[i+1]):
                
                padroes.append({
                    'tipo': 'alternancia_2_valores',
                    'valores': [valores[i], valores[i+1]],
                    'inicio': i,
                    'tamanho_detectado': 4,
                    'padrao': valores[i:i+4]
                })
        
        return padroes
    
    def _detectar_tendencias(self, valores: List[int]) -> Dict:
        """
        Detecta tendências crescentes ou decrescentes
        
        Args:
            valores: Lista de valores para analisar
            
        Returns:
            Dict: Análise de tendências
        """
        if len(valores) < 3:
            return {'tendencia': 'insuficiente', 'forca': 0}
        
        # Calcula diferenças consecutivas
        diferencas = [valores[i+1] - valores[i] for i in range(len(valores)-1)]
        
        positivas = sum(1 for d in diferencas if d > 0)
        negativas = sum(1 for d in diferencas if d < 0)
        neutras = sum(1 for d in diferencas if d == 0)
        
        total = len(diferencas)
        
        if positivas > negativas + neutras:
            tendencia = 'crescente'
            forca = positivas / total
        elif negativas > positivas + neutras:
            tendencia = 'decrescente'
            forca = negativas / total
        else:
            tendencia = 'estavel'
            forca = neutras / total
        
        return {
            'tendencia': tendencia,
            'forca': forca,
            'diferencas': diferencas,
            'positivas': positivas,
            'negativas': negativas,
            'neutras': neutras
        }
    
    def _calcular_prob_continuacao(self, filtro: str, valor: int, tamanho_sequencia: int) -> float:
        """
        Calcula probabilidade de continuação de uma sequência
        
        Args:
            filtro: Nome do filtro
            valor: Valor da sequência
            tamanho_sequencia: Tamanho atual da sequência
            
        Returns:
            float: Probabilidade de continuação (0-100%)
        """
        if not hasattr(self, 'dados_historicos') or filtro not in self.dados_historicos.columns:
            return 50.0  # Probabilidade neutra
        
        # Busca sequências históricas similares
        dados_filtro = self.dados_historicos[filtro].tolist()
        sequencias_historicas = []
        
        # Encontra todas as sequências do mesmo valor
        i = 0
        while i < len(dados_filtro):
            if dados_filtro[i] == valor:
                inicio = i
                while i < len(dados_filtro) and dados_filtro[i] == valor:
                    i += 1
                tamanho = i - inicio
                if tamanho >= 2:  # Só considera sequências de 2+
                    sequencias_historicas.append(tamanho)
            else:
                i += 1
        
        if not sequencias_historicas:
            return 30.0  # Probabilidade baixa se não há histórico
        
        # Calcula probabilidade baseada no histórico
        sequencias_maiores = [s for s in sequencias_historicas if s > tamanho_sequencia]
        sequencias_iguais_ou_maiores = [s for s in sequencias_historicas if s >= tamanho_sequencia]
        
        if not sequencias_iguais_ou_maiores:
            return 10.0  # Probabilidade muito baixa
        
        # Probabilidade = (sequências que continuaram) / (sequências no tamanho atual)
        prob = len(sequencias_maiores) / len(sequencias_iguais_ou_maiores) * 100
        
        # Ajusta baseado no tamanho da sequência (sequências muito longas são mais raras)
        if tamanho_sequencia >= 4:
            prob *= 0.7  # Reduz probabilidade para sequências longas
        elif tamanho_sequencia >= 6:
            prob *= 0.5  # Reduz mais ainda
        
        return min(prob, 85.0)  # Máximo de 85%
    
    def calcular_probabilidades_transicao(self) -> Dict:
        """
        FASE 3: Detecção de Padrões Emergentes
        Calcula matrizes de probabilidade de transição para cada filtro
        
        Returns:
            Dict: Matrizes de probabilidade de transição
        """
        print(f"\n🔮 FASE 3 - CÁLCULO DE PROBABILIDADES DE TRANSIÇÃO")
        print("=" * 60)
        
        if not hasattr(self, 'dados_historicos') or self.dados_historicos is None:
            return {'erro': 'Dados históricos não carregados'}
        
        probabilidades = {}
        
        for filtro in self.filtros_monitorados:
            if filtro not in self.dados_historicos.columns:
                continue
            
            print(f"🎯 Calculando probabilidades: {filtro}")
            
            valores_filtro = self.dados_historicos[filtro].tolist()
            
            # Cria matriz de transições
            transicoes = {}
            total_transicoes = 0
            
            # Conta transições de valor para valor
            for i in range(len(valores_filtro) - 1):
                valor_atual = valores_filtro[i]
                valor_proximo = valores_filtro[i + 1]
                
                if valor_atual not in transicoes:
                    transicoes[valor_atual] = {}
                
                if valor_proximo not in transicoes[valor_atual]:
                    transicoes[valor_atual][valor_proximo] = 0
                
                transicoes[valor_atual][valor_proximo] += 1
                total_transicoes += 1
            
            # Converte contagens em probabilidades
            prob_transicao = {}
            for valor_origem in transicoes:
                total_origem = sum(transicoes[valor_origem].values())
                prob_transicao[valor_origem] = {
                    valor_destino: (count / total_origem * 100)
                    for valor_destino, count in transicoes[valor_origem].items()
                }
            
            # Calcula estatísticas adicionais
            valor_mais_recente = valores_filtro[-1] if valores_filtro else None
            previsoes_proximas = {}
            
            if valor_mais_recente and valor_mais_recente in prob_transicao:
                # Ordena próximos valores por probabilidade
                probs_ordenadas = sorted(
                    prob_transicao[valor_mais_recente].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                previsoes_proximas = {
                    'valor_atual': valor_mais_recente,
                    'proximos_mais_provaveis': probs_ordenadas[:5],  # Top 5
                    'probabilidade_repeticao': prob_transicao[valor_mais_recente].get(valor_mais_recente, 0),
                    'total_opcoes': len(probs_ordenadas)
                }
            
            analise_filtro = {
                'total_transicoes': total_transicoes,
                'matriz_transicao': transicoes,
                'probabilidades_percentuais': prob_transicao,
                'previsoes_proximas': previsoes_proximas,
                'valores_observados': list(set(valores_filtro))
            }
            
            probabilidades[filtro] = analise_filtro
            
            # Exibe previsões
            if previsoes_proximas:
                valor_atual = previsoes_proximas['valor_atual']
                prob_repeticao = previsoes_proximas['probabilidade_repeticao']
                print(f"   📊 Valor atual: {valor_atual}")
                print(f"   🔄 Prob. repetição: {prob_repeticao:.1f}%")
                
                print(f"   🎯 Próximos mais prováveis:")
                for i, (valor, prob) in enumerate(previsoes_proximas['proximos_mais_provaveis'][:3]):
                    emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                    print(f"      {emoji} {valor}: {prob:.1f}%")
        
        self.probabilidades_transicao = probabilidades
        
        print(f"\n✅ Probabilidades de transição calculadas para {len(probabilidades)} filtros")
        return probabilidades
    
    def gerar_recomendacoes_inteligentes(self, debug: bool = True) -> Dict:
        """
        FASE 4: Motor de Decisão Inteligente
        Combina todas as análises para gerar recomendações
        
        Args:
            debug: Se deve mostrar debug detalhado
            
        Returns:
            Dict: Recomendações inteligentes para próximo concurso
        """
        print(f"\n🧠 FASE 4 - MOTOR DE DECISÃO INTELIGENTE")
        print("=" * 60)
        
        # Verifica se todas as análises foram feitas
        if not hasattr(self, 'analise_historica') or not self.analise_historica:
            print("⚠️  Executando análise histórica...")
            self.analisar_frequencias_historicas()
        
        if not hasattr(self, 'padroes_sequenciais') or not self.padroes_sequenciais:
            print("⚠️  Executando análise sequencial...")
            self.detectar_sequencias_temporais()
        
        if not hasattr(self, 'probabilidades_transicao') or not self.probabilidades_transicao:
            print("⚠️  Calculando probabilidades de transição...")
            self.calcular_probabilidades_transicao()
        
        recomendacoes = {}
        clausulas_where = []
        
        for filtro in self.filtros_monitorados:
            if (filtro not in self.analise_historica or 
                filtro not in self.padroes_sequenciais or 
                filtro not in self.probabilidades_transicao):
                continue
            
            if debug:
                print(f"\n🎯 Analisando recomendações: {filtro}")
            
            # Dados das análises
            historico = self.analise_historica[filtro]
            sequencial = self.padroes_sequenciais[filtro]
            transicao = self.probabilidades_transicao[filtro]
            
            # Estratégia de decisão
            recomendacao = self._decidir_estrategia_filtro(filtro, historico, sequencial, transicao, debug)
            
            recomendacoes[filtro] = recomendacao
            
            # Gera cláusula WHERE se houver recomendação específica
            if recomendacao['acao'] != 'neutro' and recomendacao['valor_recomendado'] is not None:
                valor = recomendacao['valor_recomendado']
                confianca = recomendacao['confianca']
                
                if confianca >= 60:  # Só inclui se confiança alta
                    if isinstance(valor, list):
                        # Múltiplos valores recomendados
                        clausula = f"{filtro} IN ({','.join(map(str, valor))})"
                    else:
                        # Valor único
                        clausula = f"{filtro} = {valor}"
                    
                    clausulas_where.append({
                        'filtro': filtro,
                        'clausula': clausula,
                        'confianca': confianca,
                        'justificativa': recomendacao['justificativa']
                    })
            
            if debug:
                acao = recomendacao['acao']
                valor = recomendacao['valor_recomendado']
                confianca = recomendacao['confianca']
                print(f"   📊 Ação: {acao.upper()}")
                print(f"   🎯 Valor: {valor}")
                print(f"   📈 Confiança: {confianca:.1f}%")
                print(f"   💡 Justificativa: {recomendacao['justificativa']}")
        
        # Gera WHERE clause combinada
        where_clause = self._gerar_where_clause_otimizada(clausulas_where)
        
        resultado = {
            'recomendacoes_por_filtro': recomendacoes,
            'clausulas_individuais': clausulas_where,
            'where_clause_combinada': where_clause,
            'total_filtros_analisados': len(recomendacoes),
            'filtros_com_recomendacao': len([r for r in recomendacoes.values() if r['acao'] != 'neutro']),
            'confianca_media': sum([r['confianca'] for r in recomendacoes.values()]) / len(recomendacoes) if recomendacoes else 0
        }
        
        # Exibe resumo final
        print(f"\n📊 RESUMO DAS RECOMENDAÇÕES:")
        print(f"   🎯 Filtros analisados: {resultado['total_filtros_analisados']}")
        print(f"   ✅ Filtros com recomendação: {resultado['filtros_com_recomendacao']}")
        print(f"   📈 Confiança média: {resultado['confianca_media']:.1f}%")
        print(f"   🎲 Cláusulas WHERE geradas: {len(clausulas_where)}")
        
        if where_clause:
            print(f"\n🎯 WHERE CLAUSE OTIMIZADA:")
            print(f"   {where_clause}")
        
        return resultado
    
    def _decidir_estrategia_filtro(self, filtro: str, historico: Dict, sequencial: Dict, 
                                  transicao: Dict, debug: bool = False) -> Dict:
        """
        Decide estratégia para um filtro específico baseada em todas as análises
        
        Args:
            filtro: Nome do filtro
            historico: Dados da análise histórica
            sequencial: Dados da análise sequencial
            transicao: Dados das probabilidades de transição
            debug: Se deve mostrar debug
            
        Returns:
            Dict: Estratégia recomendada
        """
        valor_atual = sequencial.get('valor_atual')
        sequencias_ativas = sequencial.get('sequencias_ativas', [])
        previsoes = transicao.get('previsoes_proximas', {})
        
        # Estratégia 1: Sequência ativa com alta probabilidade de continuação
        if sequencias_ativas:
            seq_ativa = sequencias_ativas[0]  # Pega a primeira (mais recente)
            prob_cont = seq_ativa['probabilidade_continuacao']
            
            if prob_cont >= 60:  # Alta probabilidade de continuar
                return {
                    'acao': 'continuar_sequencia',
                    'valor_recomendado': seq_ativa['valor'],
                    'confianca': prob_cont,
                    'justificativa': f"Sequência ativa de {seq_ativa['tamanho']} sorteios com {prob_cont:.1f}% prob. continuação"
                }
            elif prob_cont <= 25:  # Baixa probabilidade de continuar
                # Busca próximo valor mais provável diferente do atual
                if previsoes and 'proximos_mais_provaveis' in previsoes:
                    for valor_prox, prob_prox in previsoes['proximos_mais_provaveis']:
                        if valor_prox != valor_atual and prob_prox >= 20:
                            return {
                                'acao': 'quebrar_sequencia',
                                'valor_recomendado': valor_prox,
                                'confianca': prob_prox + 20,  # Bonus por quebra de sequência
                                'justificativa': f"Sequência provável de quebrar ({prob_cont:.1f}% cont.), próximo mais provável: {valor_prox}"
                            }
        
        # Estratégia 2: Transição baseada em probabilidades
        if previsoes and 'proximos_mais_provaveis' in previsoes:
            proximos = previsoes['proximos_mais_provaveis']
            if proximos:
                valor_mais_provavel, prob_maior = proximos[0]
                
                if prob_maior >= 40:  # Probabilidade significativa
                    return {
                        'acao': 'seguir_transicao',
                        'valor_recomendado': valor_mais_provavel,
                        'confianca': prob_maior,
                        'justificativa': f"Transição mais provável do valor {valor_atual} para {valor_mais_provavel} ({prob_maior:.1f}%)"
                    }
                
                # Se há empate técnico, considera top 2-3
                elif len(proximos) >= 2 and proximos[1][1] >= prob_maior * 0.8:
                    valores_equiparados = [v for v, p in proximos[:3] if p >= prob_maior * 0.7]
                    return {
                        'acao': 'multiplas_opcoes',
                        'valor_recomendado': valores_equiparados,
                        'confianca': prob_maior * 0.8,
                        'justificativa': f"Múltiplas transições equiprováveis: {valores_equiparados}"
                    }
        
        # Estratégia 3: Baseado no histórico geral (valor mais comum)
        if historico and 'valor_mais_comum' in historico:
            valor_comum = historico['valor_mais_comum']
            freq_comum = historico['frequencias_percentuais'][valor_comum]
            
            if freq_comum >= 25 and valor_comum != valor_atual:  # Valor historicamente forte
                return {
                    'acao': 'retorno_ao_comum',
                    'valor_recomendado': valor_comum,
                    'confianca': min(freq_comum + 10, 50),  # Bonus por ser historicamente comum
                    'justificativa': f"Retorno ao valor mais comum historicamente: {valor_comum} ({freq_comum:.1f}%)"
                }
        
        # Estratégia padrão: Neutro
        return {
            'acao': 'neutro',
            'valor_recomendado': None,
            'confianca': 30,
            'justificativa': "Sem padrão claro detectado, seguir distribuição natural"
        }
    
    def _gerar_where_clause_otimizada(self, clausulas: List[Dict]) -> str:
        """
        Gera WHERE clause otimizada combinando as melhores recomendações
        
        Args:
            clausulas: Lista de cláusulas individuais
            
        Returns:
            str: WHERE clause otimizada
        """
        if not clausulas:
            return ""
        
        # Ordena por confiança (maiores primeiro)
        clausulas_ordenadas = sorted(clausulas, key=lambda x: x['confianca'], reverse=True)
        
        # Pega as top clausulas (máximo 8 para não ficar muito restritivo)
        top_clausulas = clausulas_ordenadas[:8]
        
        # Filtra apenas alta confiança (>=60%)
        clausulas_alta_confianca = [c for c in top_clausulas if c['confianca'] >= 60]
        
        # Se não há clausulas de alta confiança, pega as melhores disponíveis
        if not clausulas_alta_confianca:
            clausulas_alta_confianca = top_clausulas[:5]
        
        # Constrói WHERE clause
        if clausulas_alta_confianca:
            clausulas_texto = [c['clausula'] for c in clausulas_alta_confianca]
            where_clause = "WHERE " + " AND ".join(clausulas_texto)
            return where_clause
        
        return ""
    
    def executar_analise_completa(self, debug: bool = True) -> Dict:
        """
        Executa análise sequencial completa (todas as 4 fases)
        
        Args:
            debug: Se deve mostrar debug detalhado
            
        Returns:
            Dict: Resultado completo da análise
        """
        print(f"\n🚀 SISTEMA DE ANÁLISE SEQUENCIAL - EXECUÇÃO COMPLETA")
        print("=" * 80)
        
        try:
            # FASE 1: Análise Histórica
            print(f"🔄 Iniciando FASE 1...")
            frequencias = self.analisar_frequencias_historicas()
            
            # FASE 2: Sequências Temporais
            print(f"🔄 Iniciando FASE 2...")
            sequencias = self.detectar_sequencias_temporais()
            
            # FASE 3: Probabilidades de Transição
            print(f"🔄 Iniciando FASE 3...")
            probabilidades = self.calcular_probabilidades_transicao()
            
            # FASE 4: Recomendações Inteligentes
            print(f"🔄 Iniciando FASE 4...")
            recomendacoes = self.gerar_recomendacoes_inteligentes(debug)
            
            # Resultado consolidado
            resultado_completo = {
                'timestamp': datetime.now().isoformat(),
                'total_concursos_analisados': len(self.dados_historicos) if hasattr(self, 'dados_historicos') else 0,
                'fase_1_frequencias': frequencias,
                'fase_2_sequencias': sequencias,
                'fase_3_probabilidades': probabilidades,
                'fase_4_recomendacoes': recomendacoes,
                'where_clause_final': recomendacoes.get('where_clause_combinada', ''),
                'sucesso': True
            }
            
            print(f"\n✅ ANÁLISE SEQUENCIAL COMPLETA CONCLUÍDA!")
            print(f"   📊 {len(self.filtros_monitorados)} filtros analisados")
            print(f"   🎯 {recomendacoes['filtros_com_recomendacao']} filtros com recomendações")
            print(f"   📈 Confiança média: {recomendacoes['confianca_media']:.1f}%")
            
            if recomendacoes.get('where_clause_combinada'):
                print(f"\n🎲 FILTRO REDUTOR INTELIGENTE GERADO:")
                print(f"   {recomendacoes['where_clause_combinada']}")
            
            return resultado_completo
            
        except Exception as e:
            print(f"❌ Erro durante análise sequencial: {str(e)}")
            return {
                'erro': str(e),
                'sucesso': False
            }


# Exemplo de uso
if __name__ == "__main__":
    # Cria instância do sistema
    sistema = SistemaAnaliseSequencial()
    
    # Executa análise completa
    resultado = sistema.executar_analise_completa(debug=True)
    
    if resultado.get('sucesso'):
        print(f"\n🎯 FILTRO REDUTOR FINAL:")
        print(resultado.get('where_clause_final', 'Nenhum filtro gerado'))
    else:
        print(f"❌ Erro na análise: {resultado.get('erro', 'Erro desconhecido')}")
