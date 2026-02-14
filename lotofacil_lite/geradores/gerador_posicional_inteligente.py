#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 GERADOR POSICIONAL INTELIGENTE COM CICLOS
Sistema híbrido que combina análise posicional + padrões de ciclos
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

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import statistics
import random
import warnings
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from gerador_posicional import GeradorPosicional

# Suprimir warnings
warnings.filterwarnings('ignore', category=FutureWarning)

class GeradorPosicionalInteligente:
    """
    Gerador que combina análise posicional com inteligência de ciclos
    Usa padrões da tabela NumerosCiclos para otimizar escolhas posicionais
    """
    
    def __init__(self):
        """Inicializa o gerador inteligente"""
        self.gerador_base = GeradorPosicional()
        self.dados_ciclos = None
        self.padroes_ciclos = {}
        self.inteligencia_posicional = {}
        self.dados_carregados = False
        
        print("🧠 Gerador Posicional Inteligente inicializado")
        print("🔄 Combina análise posicional + padrões de ciclos")
    
    def carregar_dados_ciclos(self) -> bool:
        """
        Carrega e analisa dados da tabela NumerosCiclos
        
        Returns:
            bool: True se carregou com sucesso
        """
        if self.dados_carregados:
            return True
            
        try:
            print("🔄 Carregando dados de ciclos...")
            
            with db_config.get_connection() as conn:
                query = """
                SELECT 
                    Numero, Ciclo, QtdSorteados, ConcursoInicio, 
                    ConcursoFechamento, DataInicio, DataFim
                FROM NumerosCiclos
                WHERE Numero BETWEEN 1 AND 25
                ORDER BY Numero, Ciclo DESC
                """
                
                self.dados_ciclos = pd.read_sql(query, conn)
                
                print(f"✅ {len(self.dados_ciclos)} registros de ciclos carregados")
                
                # Analisa padrões
                self._analisar_padroes_ciclos()
                self._gerar_inteligencia_posicional()
                
                self.dados_carregados = True
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados de ciclos: {str(e)}")
            return False
    
    def _analisar_padroes_ciclos(self):
        """Analisa padrões nos dados de ciclos"""
        print("🧠 Analisando padrões de ciclos...")
        
        # Agrupa por número
        for numero in range(1, 26):
            dados_numero = self.dados_ciclos[self.dados_ciclos['Numero'] == numero]
            
            if len(dados_numero) > 0:
                # Calcula estatísticas com base nos dados reais
                total_sorteios = dados_numero['QtdSorteados'].sum()
                ciclos_recentes = dados_numero.head(5)  # Últimos 5 ciclos
                
                # Calcula "urgência" baseada na frequência de sorteios recentes
                if len(ciclos_recentes) > 0:
                    freq_recente = ciclos_recentes['QtdSorteados'].mean()
                    freq_total = total_sorteios / len(dados_numero) if len(dados_numero) > 0 else 0
                    
                    # Número com baixa frequência recente = mais urgente
                    urgencia_calculada = max(0, (freq_total - freq_recente) / freq_total) if freq_total > 0 else 0
                else:
                    urgencia_calculada = 0.5  # Neutro
                
                self.padroes_ciclos[numero] = {
                    'urgencia_calculada': urgencia_calculada,
                    'total_sorteios': total_sorteios,
                    'ciclos_historicos': len(dados_numero),
                    'freq_media_por_ciclo': freq_total,
                    'freq_recente': freq_recente if len(ciclos_recentes) > 0 else 0,
                    'status_tendencia': self._calcular_tendencia(dados_numero),
                    'score_inteligencia': self._calcular_score_inteligencia(urgencia_calculada, total_sorteios, len(dados_numero))
                }
        
        print(f"✅ Padrões analisados para {len(self.padroes_ciclos)} números")
    
    def _calcular_tendencia(self, dados_numero):
        """Calcula tendência baseada nos dados históricos"""
        if len(dados_numero) < 3:
            return 'NEUTRO'
        
        # Analisa os últimos 3 ciclos vs anteriores
        ultimos_3 = dados_numero.head(3)['QtdSorteados'].mean()
        anteriores = dados_numero.iloc[3:]['QtdSorteados'].mean() if len(dados_numero) > 3 else ultimos_3
        
        if ultimos_3 > anteriores * 1.2:
            return 'QUENTE'  # Saindo mais frequentemente
        elif ultimos_3 < anteriores * 0.8:
            return 'FRIO'    # Saindo menos frequentemente
        else:
            return 'NEUTRO'
    
    def _calcular_score_inteligencia(self, urgencia, total_sorteios, num_ciclos):
        """Calcula score de inteligência para priorização"""
        # Combina urgência + histórico + estabilidade
        score_urgencia = urgencia * 40  # 40% peso para urgência
        score_historico = min(total_sorteios / 100, 1) * 35  # 35% peso para histórico (normalizado)
        score_estabilidade = min(num_ciclos / 20, 1) * 25  # 25% peso para estabilidade (mais ciclos = mais confiável)
        
        return score_urgencia + score_historico + score_estabilidade
    
    def _gerar_inteligencia_posicional(self):
        """Gera inteligência específica por posição baseada na análise posicional + ciclos"""
        print("🎯 Gerando inteligência posicional...")
        
        # IMPORTANTE: Verifica se é modo temporal
        if hasattr(self, '_carregar_dados_ciclos_temporal'):
            # Modo temporal: carrega dados históricos com limite temporal
            print("📊 Carregando dados históricos com filtro temporal...")
            self._carregar_dados_historicos_temporal()
        else:
            # Modo normal: carrega dados históricos do gerador base
            self.gerador_base.carregar_dados_historicos()
        
        for posicao in range(1, 16):  # Posições 1 a 15
            pos_key = f'N{posicao}'
            
            # Combina dados posicionais com inteligência de ciclos
            numeros_inteligentes = []
            
            for numero in range(1, 26):
                if numero in self.padroes_ciclos:
                    try:
                        # Usa o gerador base para calcular score posicional
                        score_posicional = self.gerador_base.calcular_score_posicional_geral(
                            pos_key, numero, 500  # Usa janela de 500 concursos
                        )
                        
                        # Score de ciclo já calculado
                        score_ciclo = self.padroes_ciclos[numero]['score_inteligencia']
                        
                        # Verifica se score posicional é válido
                        if score_posicional == 0:
                            # Fallback: usa score básico baseado na análise posicional
                            score_posicional = self._calcular_score_posicional_alternativo(pos_key, numero)
                        
                        # Normaliza scores para mesma escala
                        score_posicional_norm = score_posicional * 100  # Converte para escala 0-100
                        score_ciclo_norm = score_ciclo  # Já está na escala 0-100
                        
                        # Score combinado: posição + ciclo
                        score_combinado = (score_posicional_norm * 0.6) + (score_ciclo_norm * 0.4)
                        
                        numeros_inteligentes.append({
                            'numero': numero,
                            'score_combinado': score_combinado,
                            'score_posicional': score_posicional_norm,
                            'score_ciclo': score_ciclo_norm,
                            'tendencia': self.padroes_ciclos[numero]['status_tendencia'],
                            'urgencia': self.padroes_ciclos[numero]['urgencia_calculada']
                        })
                    except Exception as e:
                        # Se der erro no cálculo posicional, usa apenas ciclos
                        score_ciclo = self.padroes_ciclos[numero]['score_inteligencia']
                        
                        numeros_inteligentes.append({
                            'numero': numero,
                            'score_combinado': score_ciclo,
                            'score_posicional': 0.0,
                            'score_ciclo': score_ciclo,
                            'tendencia': self.padroes_ciclos[numero]['status_tendencia'],
                            'urgencia': self.padroes_ciclos[numero]['urgencia_calculada']
                        })
            
            # Ordena por score combinado
            numeros_inteligentes.sort(key=lambda x: x['score_combinado'], reverse=True)
            
            self.inteligencia_posicional[pos_key] = {
                'numeros_otimizados': numeros_inteligentes[:15],  # Top 15
                'estrategia_recomendada': self._definir_estrategia_posicao(numeros_inteligentes),
                'total_numeros_analisados': len(numeros_inteligentes)
            }
        
        print(f"✅ Inteligência gerada para {len(self.inteligencia_posicional)} posições")
    
    def _calcular_score_posicional_alternativo(self, posicao: str, numero: int) -> float:
        """Calcula score posicional alternativo baseado na lógica da Lotofácil"""
        pos_num = int(posicao[1:])  # N1 -> 1, N15 -> 15
        
        # Lógica correta baseada na análise real dos dados:
        # N1-N3: números 1-7 (muito baixos)
        # N4-N7: números 4-12 (baixos-médios) 
        # N8-N11: números 8-18 (médios-altos)
        # N12-N15: números 15-25 (altos)
        
        if pos_num <= 3:  # N1, N2, N3 - Primeiras posições
            if numero <= 7:
                return 0.9  # Muito adequado
            elif numero <= 10:
                return 0.6  # Adequado
            elif numero <= 15:
                return 0.3  # Pouco adequado
            else:
                return 0.1  # Inadequado
                
        elif pos_num <= 7:  # N4-N7 - Posições baixas-médias
            if 4 <= numero <= 12:
                return 0.9  # Muito adequado
            elif numero <= 7 or (13 <= numero <= 15):
                return 0.7  # Adequado
            elif numero <= 3 or (16 <= numero <= 18):
                return 0.4  # Pouco adequado
            else:
                return 0.2  # Inadequado
                
        elif pos_num <= 11:  # N8-N11 - Posições médias-altas
            if 8 <= numero <= 18:
                return 0.9  # Muito adequado
            elif 6 <= numero <= 7 or 19 <= numero <= 20:
                return 0.7  # Adequado
            elif numero <= 5 or 21 <= numero <= 22:
                return 0.4  # Pouco adequado
            else:
                return 0.2  # Inadequado
                
        else:  # N12-N15 - Últimas posições
            if numero >= 18:
                return 0.9  # Muito adequado
            elif numero >= 15:
                return 0.7  # Adequado
            elif numero >= 12:
                return 0.4  # Pouco adequado
            elif numero >= 8:
                return 0.2  # Inadequado
            else:
                return 0.05  # Muito inadequado (nunca deveria acontecer)
    
    def _definir_estrategia_posicao(self, numeros_inteligentes):
        """Define estratégia recomendada para a posição"""
        if not numeros_inteligentes:
            return 'NEUTRO'
        
        # Analisa tendências dos top numbers
        top_5 = numeros_inteligentes[:5]
        
        quentes = sum(1 for n in top_5 if n['tendencia'] == 'QUENTE')
        frios = sum(1 for n in top_5 if n['tendencia'] == 'FRIO')
        
        if quentes >= 3:
            return 'FOCAR_QUENTES'  # Priorizar números quentes
        elif frios >= 3:
            return 'FOCAR_FRIOS'    # Priorizar números com urgência
        else:
            return 'EQUILIBRIO'     # Balancear quentes e frios
            scores_posicao = {}
            
            for numero in range(1, 26):
                if numero in self.padroes_ciclos:
                    dados_numero = self.padroes_ciclos[numero]
                    
                    # Se esta posição está nas preferenciais do número
                    if pos_num in dados_numero['posicoes_preferenciais']:
                        peso = dados_numero['score_urgencia_medio'] * dados_numero['urgencia_media']
                        numeros_preferenciais.append((numero, peso))
                    
                    # Se esta posição está nas que o número evita
                    elif pos_num in dados_numero['posicoes_evitar']:
                        numeros_evitar.append(numero)
                    
                    # Score individual do número nesta posição
                    dados_posicao = self.dados_ciclos[
                        (self.dados_ciclos['Numero'] == numero) & 
                        (self.dados_ciclos['Posicao'] == pos_num)
                    ]
                    
                    if len(dados_posicao) > 0:
                        score = dados_posicao['ScoreUrgencia'].iloc[0]
                        urgencia = dados_posicao['Urgencia'].iloc[0]
                        status = dados_posicao['StatusCiclo'].iloc[0]
                        
                        # Score combinado considerando ciclo
                        multiplicador_status = {
                            'URGENTE': 1.5,
                            'ATIVO': 1.2,
                            'EMERGENTE': 1.3,
                            'NEUTRO': 1.0,
                            'DORMINDO': 0.7,
                            'FRIO': 0.5
                        }
                        
                        score_final = score * urgencia * multiplicador_status.get(status, 1.0)
                        scores_posicao[numero] = score_final
            
            # Ordena números preferenciais por peso
            numeros_preferenciais.sort(key=lambda x: x[1], reverse=True)
            
            # Ordena todos os números por score na posição
            top_numeros = sorted(scores_posicao.items(), key=lambda x: x[1], reverse=True)
            
            self.inteligencia_posicional[posicao] = {
                'numeros_preferenciais': [num for num, peso in numeros_preferenciais[:8]],  # Top 8
                'numeros_evitar': numeros_evitar,
                'ranking_scores': top_numeros,
                'score_medio': statistics.mean(scores_posicao.values()) if scores_posicao else 0,
                'score_maximo': max(scores_posicao.values()) if scores_posicao else 0
            }
    
    def escolher_numero_inteligente(self, posicao: str, numeros_ja_escolhidos: List[int] = None, 
                                  variacao: float = 0.3) -> Tuple[int, float, str]:
        """
        Escolhe número usando inteligência de ciclos + análise posicional
        
        Args:
            posicao: Posição a analisar (N1, N2, etc.)
            numeros_ja_escolhidos: Números já escolhidos
            variacao: Factor de variação
            
        Returns:
            Tuple: (numero_escolhido, score_final, fonte_escolha)
        """
        if numeros_ja_escolhidos is None:
            numeros_ja_escolhidos = []
        
        # Pega análise posicional tradicional
        numero_posicional, score_posicional = self.gerador_base.escolher_melhor_numero_posicao(
            posicao, numeros_ja_escolhidos, variacao
        )
        
        # Pega inteligência de ciclos para esta posição
        inteligencia = self.inteligencia_posicional.get(posicao, {})
        numeros_preferenciais = inteligencia.get('numeros_preferenciais', [])
        numeros_evitar = inteligencia.get('numeros_evitar', [])
        ranking_scores = inteligencia.get('ranking_scores', [])
        
        # Cria lista de candidatos inteligentes
        candidatos_inteligentes = []
        
        # Analisa números preferenciais disponíveis
        for numero in numeros_preferenciais:
            if numero not in numeros_ja_escolhidos and numero not in numeros_evitar:
                # Encontra score do número no ranking
                score_ciclo = 0
                for num, score in ranking_scores:
                    if num == numero:
                        score_ciclo = score
                        break
                
                candidatos_inteligentes.append((numero, score_ciclo, 'PREFERENCIAL'))
        
        # Se não há preferenciais suficientes, usa ranking geral (exceto os a evitar)
        if len(candidatos_inteligentes) < 3:
            for numero, score_ciclo in ranking_scores:
                if (numero not in numeros_ja_escolhidos and 
                    numero not in numeros_evitar and 
                    numero not in [c[0] for c in candidatos_inteligentes]):
                    
                    candidatos_inteligentes.append((numero, score_ciclo, 'RANKING'))
                    
                    if len(candidatos_inteligentes) >= 8:  # Limita a 8 candidatos
                        break
        
        # Se ainda não há candidatos suficientes, inclui análise posicional
        if len(candidatos_inteligentes) < 2:
            if numero_posicional not in numeros_ja_escolhidos:
                candidatos_inteligentes.append((numero_posicional, score_posicional * 100, 'POSICIONAL'))
        
        # Escolhe entre candidatos inteligentes
        if candidatos_inteligentes:
            # Aplica variação probabilística
            if variacao > 0 and len(candidatos_inteligentes) > 1:
                # Seleciona dos melhores 50% com probabilidade ponderada
                top_percent = max(1, int(len(candidatos_inteligentes) * 0.5))
                top_candidatos = candidatos_inteligentes[:top_percent]
                
                if random.random() < variacao:
                    # Seleção ponderada pelos scores
                    pesos = [score for _, score, _ in top_candidatos]
                    peso_total = sum(pesos) if sum(pesos) > 0 else 1
                    
                    if peso_total > 0:
                        probs = [p/peso_total for p in pesos]
                        escolhido_idx = random.choices(range(len(top_candidatos)), weights=probs)[0]
                        numero, score, fonte = top_candidatos[escolhido_idx]
                        return numero, score, fonte
            
            # Escolha determinística (melhor score)
            numero, score, fonte = candidatos_inteligentes[0]
            return numero, score, fonte
        
        # Fallback: usa análise posicional tradicional
        return numero_posicional, score_posicional * 100, 'FALLBACK'
    
    def gerar_combinacao_inteligente(self, debug: bool = True, variacao: float = None) -> List[int]:
        """
        Gera combinação usando inteligência híbrida
        
        Args:
            debug: Se deve mostrar debug
            variacao: Factor de variação
            
        Returns:
            List[int]: Combinação gerada
        """
        if not self.carregar_dados_ciclos():
            print("⚠️ Dados de ciclos não disponíveis, usando análise posicional padrão")
            return self.gerador_base.gerar_combinacao_posicional(debug, variacao)
        
        # Carrega dados do gerador base
        if not self.gerador_base.carregar_dados_historicos():
            raise Exception("Erro ao carregar dados históricos")
        
        # Define variação
        if variacao is None:
            variacao = random.uniform(0.2, 0.5)
        
        if debug:
            print("\n🧠 GERANDO COMBINAÇÃO POSICIONAL INTELIGENTE")
            print("=" * 55)
            print("🎯 Análise Posicional + Inteligência de Ciclos")
        
        combinacao = []
        fontes_escolha = []
        
        posicoes = [f'N{i}' for i in range(1, 16)]
        
        for posicao in posicoes:
            if debug:
                print(f"\n🔍 Analisando {posicao}...")
            
            numero, score, fonte = self.escolher_numero_inteligente(posicao, combinacao, variacao)
            
            combinacao.append(numero)
            fontes_escolha.append(fonte)
            
            if debug:
                emoji_fonte = {
                    'PREFERENCIAL': '🎯',
                    'RANKING': '📊', 
                    'POSICIONAL': '📍',
                    'FALLBACK': '🔄'
                }
                emoji = emoji_fonte.get(fonte, '❓')
                print(f"   ✅ {posicao}: {numero:2d} (Score: {score:6.1f}) {emoji} {fonte}")
        
        if debug:
            print(f"\n🎉 COMBINAÇÃO INTELIGENTE GERADA: {combinacao}")
            print(f"   📊 Soma total: {sum(combinacao)}")
            print(f"   🔢 Pares: {sum(1 for n in combinacao if n % 2 == 0)}")
            print(f"   🔢 Ímpares: {sum(1 for n in combinacao if n % 2 == 1)}")
            
            # Estatísticas das fontes
            contador_fontes = Counter(fontes_escolha)
            print(f"\n📈 FONTES DE ESCOLHA:")
            for fonte, count in contador_fontes.items():
                emoji = {'PREFERENCIAL': '🎯', 'RANKING': '📊', 'POSICIONAL': '📍', 'FALLBACK': '🔄'}.get(fonte, '❓')
                print(f"   {emoji} {fonte}: {count} números")
            
            print(f"\n⚠️ ATENÇÃO: Ordenando números (padrão da Lotofácil)...")
        
        # CORREÇÃO CRÍTICA: Ordena a combinação (padrão da Lotofácil)
        combinacao.sort()
        
        if debug:
            print(f"🎯 COMBINAÇÃO FINAL ORDENADA: {combinacao}")
        
        return combinacao
    
    def gerar_multiplas_combinacoes_inteligentes(self, quantidade: int = 5) -> List[List[int]]:
        """
        Gera múltiplas combinações inteligentes com estratégia de cobertura
        
        Primeira combinação: Mais eficaz e provável
        Demais combinações: Exatamente 10 números em comum com a principal
        
        Args:
            quantidade: Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"🧠 Gerando {quantidade} combinações posicionais inteligentes...")
        print("🔄 Usando análise posicional + padrões de ciclos")
        print("🎯 Estratégia: 1ª = Mais eficaz | Demais = 10 números em comum")
        
        # Carrega dados uma vez
        if not self.carregar_dados_ciclos():
            print("⚠️ Fallback para gerador posicional padrão")
            return self.gerador_base.gerar_multiplas_combinacoes(quantidade)
        
        combinacoes = []
        
        # 1. GERA A COMBINAÇÃO PRINCIPAL (mais eficaz)
        print(f"\n--- Combinação Principal (1/{quantidade}) ---")
        print("🎯 Gerando combinação mais eficaz e provável...")
        
        # Para garantir que seja a mais eficaz, gera várias e escolhe a melhor
        candidatas_principais = []
        for tentativa in range(5):  # Gera 5 candidatas
            try:
                candidata = self.gerar_combinacao_inteligente(debug=False, variacao=0.1)
                score = self._avaliar_qualidade_combinacao(candidata)
                candidatas_principais.append((candidata, score))
            except Exception as e:
                print(f"⚠️ Erro na candidata {tentativa+1}: {e}")
        
        if not candidatas_principais:
            print("❌ Não foi possível gerar candidatas principais")
            return []
        
        # Escolhe a melhor candidata como combinação principal
        combinacao_principal, score_principal = max(candidatas_principais, key=lambda x: x[1])
        combinacoes.append(combinacao_principal)
        
        print(f"✅ Principal: {combinacao_principal} (Score: {score_principal:.1f})")
        
        # 2. GERA AS DEMAIS COMBINAÇÕES (10 números em comum)
        for i in range(1, quantidade):
            print(f"\n--- Combinação Derivada {i+1}/{quantidade} ---")
            print("🔗 Mantendo 10 números em comum com a principal...")
            
            try:
                combinacao_derivada = self._gerar_combinacao_com_overlap_inteligente(
                    combinacao_principal, overlap_target=10
                )
                
                # Verifica overlap real
                overlap_real = len(set(combinacao_principal) & set(combinacao_derivada))
                score_derivada = self._avaliar_qualidade_combinacao(combinacao_derivada)
                
                combinacoes.append(combinacao_derivada)
                print(f"✅ Derivada: {combinacao_derivada} (Score: {score_derivada:.1f})")
                print(f"🔗 Overlap: {overlap_real}/15 números em comum")
                
            except Exception as e:
                print(f"❌ Erro na combinação derivada {i+1}: {e}")
                # Fallback: gera uma combinação normal com variação
                try:
                    variacao = 0.2 + (i * 0.15)
                    if variacao > 0.9:
                        variacao = random.uniform(0.3, 0.8)
                    combinacao = self.gerar_combinacao_inteligente(debug=False, variacao=variacao)
                    combinacoes.append(combinacao)
                    print(f"⚠️ Fallback: {combinacao}")
                except:
                    print(f"❌ Falha total na combinação {i+1}")
        
        print(f"\n🎉 {len(combinacoes)} combinações inteligentes geradas!")
        
        # Exibe resumo final
        print(f"\n🏆 RESUMO DAS {len(combinacoes)} COMBINAÇÕES:")
        for i, comb in enumerate(combinacoes):
            if i == 0:
                print(f"   {i+1}º: {comb} (Principal)")
            else:
                overlap = len(set(combinacoes[0]) & set(comb))
                print(f"   {i+1}º: {comb} (Derivada, overlap: {overlap})")
        
        return combinacoes
    
    def _gerar_combinacao_com_overlap_inteligente(self, combinacao_base: List[int], overlap_target: int = 10) -> List[int]:
        """
        Gera combinação inteligente com overlap específico
        
        Args:
            combinacao_base: Combinação de referência
            overlap_target: Quantidade de números em comum desejada
            
        Returns:
            List[int]: Nova combinação com overlap desejado
        """
        import random
        
        if overlap_target > 15 or overlap_target < 0:
            overlap_target = 10
        
        # 1. Seleciona números da combinação base para manter
        numeros_manter = random.sample(combinacao_base, overlap_target)
        
        # 2. Precisa substituir (15 - overlap_target) números
        numeros_substituir = 15 - overlap_target
        
        # 3. Pool de números disponíveis (não estão na base)
        numeros_disponiveis = [n for n in range(1, 26) if n not in combinacao_base]
        
        # 4. Prioriza números baseado na inteligência de ciclos
        candidatos_inteligentes = []
        for numero in numeros_disponiveis:
            if numero in self.padroes_ciclos:
                dados_ciclo = self.padroes_ciclos[numero]
                score = dados_ciclo.get('score_posicional', 50.0)
                
                # Bonifica números em status favoráveis
                status = dados_ciclo.get('status_tendencia', 'normal')
                if status == 'urgente':
                    score += 20
                elif status == 'ativo':
                    score += 15
                elif status == 'emergente':
                    score += 10
                
                candidatos_inteligentes.append((numero, score))
            else:
                # Score padrão para números sem dados de ciclo
                candidatos_inteligentes.append((numero, 50.0))
        
        # 5. Ordena por score e seleciona com alguma aleatoriedade
        candidatos_inteligentes.sort(key=lambda x: x[1], reverse=True)
        
        numeros_novos = []
        pool_candidatos = candidatos_inteligentes[:min(len(candidatos_inteligentes), numeros_substituir * 3)]
        
        for i in range(numeros_substituir):
            if pool_candidatos:
                # Usa distribuição ponderada favorecendo os melhores
                pesos = [2 ** (len(pool_candidatos) - j) for j in range(len(pool_candidatos))]
                candidato = random.choices(pool_candidatos, weights=pesos)[0]
                numeros_novos.append(candidato[0])
                pool_candidatos.remove(candidato)
        
        # 6. Combina números mantidos + números novos
        combinacao_final = numeros_manter + numeros_novos
        combinacao_final.sort()
        
        return combinacao_final
    
    def _avaliar_qualidade_combinacao(self, combinacao: List[int]) -> float:
        """
        Avalia a qualidade de uma combinação baseada nos critérios inteligentes
        
        Args:
            combinacao: Combinação a avaliar
            
        Returns:
            float: Score de qualidade (0-100)
        """
        score = 50.0  # Score base
        
        try:
            # 1. Score baseado em ciclos
            score_ciclos = 0
            count_ciclos = 0
            
            for numero in combinacao:
                if numero in self.padroes_ciclos:
                    dados = self.padroes_ciclos[numero]
                    score_ciclos += dados.get('score_posicional', 50.0)
                    count_ciclos += 1
            
            if count_ciclos > 0:
                score += (score_ciclos / count_ciclos - 50) * 0.4  # Peso 40%
            
            # 2. Distribuição de status
            status_counts = {'urgente': 0, 'ativo': 0, 'emergente': 0, 'normal': 0, 'frio': 0}
            for numero in combinacao:
                if numero in self.padroes_ciclos:
                    status = self.padroes_ciclos[numero].get('status_tendencia', 'normal')
                    status_counts[status] += 1
            
            # Bonifica combinações balanceadas
            if status_counts['urgente'] >= 2:
                score += 10
            if status_counts['ativo'] >= 3:
                score += 8
            if status_counts['emergente'] >= 2:
                score += 5
            
            # 3. Penaliza muitos números frios
            if status_counts['frio'] > 3:
                score -= 15
            
            # 4. Soma e características básicas
            soma = sum(combinacao)
            if 180 <= soma <= 210:  # Faixa boa de soma
                score += 8
            
            # 5. Distribuição por quintis
            quintis = [0] * 5
            for numero in combinacao:
                quintil = min(4, (numero - 1) // 5)
                quintis[quintil] += 1
            
            # Bonifica distribuição balanceada
            if all(2 <= q <= 4 for q in quintis):
                score += 5
            
        except Exception as e:
            print(f"⚠️ Erro na avaliação de qualidade: {e}")
        
        return max(0, min(100, score))
    
    def analisar_padroes_descobertos(self):
        """Exibe análise dos padrões descobertos nos ciclos"""
        if not self.dados_carregados:
            if not self.carregar_dados_ciclos():
                print("❌ Não foi possível carregar dados de ciclos")
                return
        
        print("\n🧠 ANÁLISE DE PADRÕES DESCOBERTOS")
        print("=" * 50)
        
        # Números por status de ciclo
        status_counts = Counter()
        numeros_urgentes = []
        numeros_ativos = []
        numeros_emergentes = []
        numeros_frios = []
        
        for numero, dados in self.padroes_ciclos.items():
            status = dados['status_tendencia']  # Campo correto
            status_counts[status] += 1
            
            if status == 'QUENTE':
                numeros_urgentes.append((numero, dados['score_inteligencia']))
            elif status == 'NEUTRO':
                numeros_ativos.append((numero, dados['score_inteligencia']))
            elif status == 'FRIO':
                numeros_frios.append((numero, dados['score_inteligencia']))
        
        print(f"📊 DISTRIBUIÇÃO POR STATUS:")
        for status, count in status_counts.most_common():
            print(f"   {status}: {count} números")
        
        # Top números por categoria
        if numeros_urgentes:
            numeros_urgentes.sort(key=lambda x: x[1], reverse=True)
            print(f"\n🔥 TOP NÚMEROS QUENTES:")
            for numero, score in numeros_urgentes[:5]:
                print(f"   {numero:2d}: Score {score:.2f}")
        
        if numeros_ativos:
            numeros_ativos.sort(key=lambda x: x[1], reverse=True)
            print(f"\n⚡ TOP NÚMEROS NEUTROS:")
            for numero, score in numeros_ativos[:5]:
                print(f"   {numero:2d}: Score {score:.2f}")
        
        if numeros_frios:
            numeros_frios.sort(key=lambda x: x[1], reverse=True)
            print(f"\n❄️ TOP NÚMEROS FRIOS:")
            for numero, score in numeros_frios[:5]:
                print(f"   {numero:2d}: Score {score:.2f}")
        
        # Análise posicional
        print(f"\n🎯 INTELIGÊNCIA POSICIONAL:")
        for posicao in ['N1', 'N3', 'N8', 'N15']:  # Amostra de posições
            intel = self.inteligencia_posicional.get(posicao, {})
            otimizados = intel.get('numeros_otimizados', [])
            
            if otimizados:
                top3 = [str(n['numero']) for n in otimizados[:3]]
                print(f"   {posicao}: Top {', '.join(top3)}")


def main():
    """Função principal para teste do gerador inteligente"""
    print("🧠 TESTE DO GERADOR POSICIONAL INTELIGENTE")
    print("=" * 55)
    
    # Cria instância do gerador
    gerador = GeradorPosicionalInteligente()
    
    # Menu de teste
    while True:
        print(f"\n🎯 OPÇÕES DE TESTE:")
        print(f"   1 - Gerar 1 combinação inteligente (com debug)")
        print(f"   2 - Gerar múltiplas combinações inteligentes")
        print(f"   3 - Analisar padrões descobertos")
        print(f"   4 - Comparar com gerador posicional tradicional")
        print(f"   0 - Sair")
        
        try:
            opcao = input(f"\nEscolha uma opção: ").strip()
            
            if opcao == "0":
                print("👋 Encerrando...")
                break
            elif opcao == "1":
                combinacao = gerador.gerar_combinacao_inteligente(debug=True)
                print(f"\n🎯 Combinação: {combinacao}")
                
            elif opcao == "2":
                quantidade = int(input("Quantas combinações? (1-10): "))
                combinacoes = gerador.gerar_multiplas_combinacoes_inteligentes(quantidade)
                
                print(f"\n🧠 COMBINAÇÕES INTELIGENTES GERADAS:")
                for i, comb in enumerate(combinacoes, 1):
                    soma = sum(comb)
                    pares = sum(1 for n in comb if n % 2 == 0)
                    print(f"   {i:2d}: {comb} (Soma: {soma}, Pares: {pares})")
                
            elif opcao == "3":
                gerador.analisar_padroes_descobertos()
                
            elif opcao == "4":
                print("\n🔍 COMPARAÇÃO: Inteligente vs Tradicional")
                print("-" * 50)
                
                # Gera com inteligente
                print("🧠 Gerando com INTELIGENTE...")
                comb_inteligente = gerador.gerar_combinacao_inteligente(debug=False)
                
                # Gera com tradicional
                print("📍 Gerando com TRADICIONAL...")
                comb_tradicional = gerador.gerador_base.gerar_combinacao_posicional(debug=False)
                
                print(f"\n📊 COMPARAÇÃO:")
                print(f"   🧠 Inteligente: {comb_inteligente}")
                print(f"   📍 Tradicional: {comb_tradicional}")
                print(f"   🔄 Diferenças: {set(comb_inteligente) - set(comb_tradicional)}")
                
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Interrompido...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    main()
