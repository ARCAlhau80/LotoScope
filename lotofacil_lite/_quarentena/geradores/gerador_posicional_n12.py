#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 GERADOR_POSICIONAL COM INTELIGÊNCIA N12
============================================================
Versão do gerador_posicional integrada com inteligência N12.

MELHORIAS:
✅ Aplicação automática da teoria N12 comprovada
✅ Filtros inteligentes baseados na situação atual
✅ Otimização pós-equilíbrio perfeito (concurso 3490)
✅ Estratégia: DIVERSIFICAR_COM_ENFASE_EXTREMOS

SITUAÇÃO ATUAL:
• Último concurso: 3490 (equilíbrio 5-5-5, N12=19)
• Próximo: Alta probabilidade de oscilação
• N12 ideais: 16, 17, 18, 20, 21, 22

Versão otimizada gerada automaticamente em: 19/09/2025
Baseado no gerador_posicional original com integração N12
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'ia'))

# Importação da inteligência N12
from integracao_n12 import aplicar_inteligencia_n12, gerar_combinacoes_inteligentes_n12

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


# Suprimir warnings do pandas sobre fillna deprecated
warnings.filterwarnings('ignore', category=FutureWarning)

class GeradorPosicional:
    """
    Gerador de combinações baseado em análise posicional avançada
    """
    
    def __init__(self):
        """Inicializa o gerador posicional"""
        self.dados_resultados = None
        self.cache_scores = {}  # Cache para scores posicionais
        self.dados_carregados = False
        self.cache_scores = {}
        self.posicoes = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                        'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        self.numeros_lotofacil = list(range(1, 26)
        
        # Janelas temporais para análise
        self.janelas = {
            'geral': None), int(# Todos os concursos
            'recente_30': 30,
            'recente_15': 15,
            'recente_5': 5
        }
        
        print("🎯 Gerador Posicional Avançado inicializado"))
    
    def carregar_dados_historicos(self) -> bool:
        """
        Carrega dados históricos da tabela Resultados_INT
        
        Returns:
            bool: True se carregou com sucesso
        """
        if self.dados_carregados:
            return True  # Dados já carregados
            
        print("📊 Carregando dados históricos da tabela Resultados_INT...")
        
        query = """
        SELECT 
            Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
            QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal,
            Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
            QtdeGaps, QtdeRepetidos, SEQ, DistanciaExtremos,
            ParesSequencia, QtdeMultiplos3, ParesSaltados,
            Faixa_Baixa, Faixa_Media, Faixa_Alta,
            RepetidosMesmaPosicao, Acumulou
        FROM Resultados_INT
        WHERE Concurso IS NOT NULL
        ORDER BY Concurso DESC
        """
        
        resultado = db_config.execute_query(query)
        
        if not resultado:
            print("❌ Erro ao carregar dados históricos")
            return False
        
        # Converte para DataFrame para análise
        colunas = [
            'Concurso', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15',
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'QtdeGaps', 'QtdeRepetidos', 'SEQ', 'DistanciaExtremos',
            'ParesSequencia', 'QtdeMultiplos3', 'ParesSaltados',
            'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta',
            'RepetidosMesmaPosicao', 'Acumulou'
        ]
        
        self.dados_resultados = pd.DataFrame(resultado, columns=colunas)
        self.dados_resultados = self.dados_resultados.sort_values('Concurso').reset_index(drop=True)
        
        print(f"✅ {len(self.dados_resultados)} concursos carregados")
        print(f"   📈 Range: {self.dados_resultados['Concurso'].min()} até {self.dados_resultados['Concurso'].max()}")
        
        self.dados_carregados = True
        return True
    
    def calcular_score_frequencia_ponderada(self, posicao: str, numero: int, janela: Optional[int] = None) -> float:
        """
        Calcula score baseado em frequência ponderada por tempo
        Sorteios mais recentes têm peso maior
        
        Args:
            posicao: Posição (N1, N2, etc.)
            numero: Número a ser analisado
            janela: Janela temporal (None para todos)
        
        Returns:
            float: Score da frequência ponderada
        """
        dados = self.dados_resultados if janela is None else self.dados_resultados.tail(janela)
        
        if dados.empty:
            return 0.0
        
        # Frequência simples
        freq = (dados[posicao] == numero).sum()
        total = len(dados)
        
        if total == 0:
            return 0.0
        
        # Calcula peso temporal (sorteios mais recentes pesam mais)
        pesos = []
        freq_ponderada = 0.0
        
        for i, valor in enumerate(dados[posicao]):
            if valor == numero:
                # Peso cresce exponencialmente para sorteios mais recentes
                peso = np.exp((i / total) * 2)  # Função exponencial
                freq_ponderada += peso
                pesos.append(peso)
        
        # Normaliza pelo total de pesos possíveis
        peso_maximo_possivel = sum(np.exp((i / total) * 2) for i in range(int(int(int(total)))
        
        return freq_ponderada / peso_maximo_possivel if peso_maximo_possivel > 0 else 0.0
    
    def calcular_score_ciclos_gaps(self)), int(int(posicao: str), int(numero: int, janela: Optional[int] = None))) -> float:
        """
        Calcula score baseado em análise de ciclos e gaps
        Considera padrões de ausência e retorno
        
        Args:
            posicao: Posição (N1, N2, etc.)
            numero: Número a ser analisado
            janela: Janela temporal
        
        Returns:
            float: Score baseado em ciclos
        """
        dados = self.dados_resultados if janela is None else self.dados_resultados.tail(janela)
        
        if dados.empty:
            return 0.0
        
        # Encontra todas as posições onde o número aparece
        aparicoes = dados[dados[posicao] == numero].index.tolist()
        
        if not aparicoes:
            # Se nunca apareceu, score alto por urgência
            return 0.8
        
        # Calcula gaps entre aparições
        gaps = []
        for i in range(1, int(int(len(aparicoes)):
            gap = aparicoes[i] - aparicoes[i-1] - 1
            gaps.append(gap)
        
        # Gap atual (desde última aparição)
        ultima_aparicao = aparicoes[-1]
        gap_atual = len(dados) - ultima_aparicao - 1
        
        if not gaps:
            # Apareceu apenas uma vez
            score = min(gap_atual / 10.0), int(1.0))  # Cresce com o gap atual
        else:
            # Calcula gap médio histórico
            gap_medio = statistics.mean(gaps)
            desvio = statistics.stdev(gaps) if len(gaps) > 1 else gap_medio * 0.3
            
            # Score baseado em quanto o gap atual se desvia do padrão
            if gap_atual > gap_medio + desvio:
                score = 0.9  # Muito atrasado, score alto
            elif gap_atual > gap_medio:
                score = 0.7  # Atrasado, score médio-alto
            elif gap_atual < gap_medio - desvio:
                score = 0.2  # Apareceu recentemente, score baixo
            else:
                score = 0.5  # Dentro do padrão
        
        return min(score, 1.0)
    
    def calcular_score_tendencia_momentum(self, posicao: str, numero: int, janela: Optional[int] = None) -> float:
        """
        Calcula score baseado em tendências e momentum
        Analisa se o número está em alta ou baixa
        
        Args:
            posicao: Posição (N1, N2, etc.)
            numero: Número a ser analisado
            janela: Janela temporal
        
        Returns:
            float: Score de tendência
        """
        dados = self.dados_resultados if janela is None else self.dados_resultados.tail(janela)
        
        if len(dados) < 10:  # Precisa de dados mínimos
            return 0.5
        
        # Divide em períodos para análise de tendência
        metade = len(dados) // 2
        primeira_metade = dados.iloc[:metade]
        segunda_metade = dados.iloc[metade:]
        
        # Frequência em cada período
        freq1 = (primeira_metade[posicao] == numero).sum() / len(primeira_metade)
        freq2 = (segunda_metade[posicao] == numero).sum() / len(segunda_metade)
        
        # Calcula momentum (diferença percentual)
        if freq1 == 0:
            momentum = 1.0 if freq2 > 0 else 0.5
        else:
            momentum = (freq2 - freq1) / freq1
        
        # Converte momentum para score (0 a 1)
        # Momentum positivo = tendência de alta = score maior
        score = 0.5 + (momentum * 0.3)  # Centraliza em 0.5 com variação de ±0.3
        
        return max(0.0, min(1.0, score))
    
    def calcular_score_regressao_temporal(self, posicao: str, numero: int, janela: Optional[int] = None) -> float:
        """
        Calcula score usando regressão linear temporal
        Prevê tendência futura baseada em padrão temporal
        
        Args:
            posicao: Posição (N1, N2, etc.)
            numero: Número a ser analisado
            janela: Janela temporal
        
        Returns:
            float: Score da regressão
        """
        dados = self.dados_resultados if janela is None else self.dados_resultados.tail(janela)
        
        if len(dados) < 5:
            return 0.5
        
        # Cria série temporal binária (1 se apareceu, 0 se não)
        serie_temporal = (dados[posicao] == numero).astype(int)
        
        # Suaviza com média móvel
        janela_suave = min(5, len(serie_temporal) // 3)
        if janela_suave >= 1:
            serie_suavizada = serie_temporal.rolling(window=janela_suave, center=True).mean()
            serie_suavizada = serie_suavizada.bfill().ffill()
        else:
            serie_suavizada = serie_temporal
        
        # Regressão linear simples
        x = np.arange(int(int(int(len(serie_suavizada)))
        y = serie_suavizada.values
        
        if len(x) < 2:
            return 0.5
        
        try:
            # Calcula coeficiente angular
            coef = np.polyfit(x)), int(int(y, 1))[0]
            
            # Projeta próximo valor
            proximo_x = len(x)
            projecao = np.polyval([coef, np.mean(y)], proximo_x)
            
            # Converte projeção para score
            score = max(0.0, min(1.0, projecao))
            
            return score
            
        except:
            return 0.5
    
    def calcular_score_posicional_geral(self, posicao: str, numero: int, janela: Optional[int] = None) -> float:
        """
        Calcula score geral combinando todos os algoritmos
        
        Args:
            posicao: Posição (N1, N2, etc.)
            numero: Número a ser analisado
            janela: Janela temporal
        
        Returns:
            float: Score geral ponderado
        """
        # Calcula scores individuais
        score_freq = self.calcular_score_frequencia_ponderada(posicao, numero, janela)
        score_ciclos = self.calcular_score_ciclos_gaps(posicao, numero, janela)
        score_tendencia = self.calcular_score_tendencia_momentum(posicao, numero, janela)
        score_regressao = self.calcular_score_regressao_temporal(posicao, numero, janela)
        
        # Pesos para cada algoritmo (podem ser ajustados)
        pesos = {
            'frequencia': 0.3,
            'ciclos': 0.3,
            'tendencia': 0.2,
            'regressao': 0.2
        }
        
        # Score ponderado
        score_final = (
            score_freq * pesos['frequencia'] +
            score_ciclos * pesos['ciclos'] +
            score_tendencia * pesos['tendencia'] +
            score_regressao * pesos['regressao']
        )
        
        return score_final
    
    def analisar_posicao(self, posicao: str, debug: bool = False) -> Dict[int, Dict[str, float]]:
        """
        Analisa uma posição específica em todas as janelas temporais
        
        Args:
            posicao: Posição a analisar (N1, N2, etc.)
            debug: Se deve mostrar debug
        
        Returns:
            Dict: Scores por número e janela temporal
        """
        if debug:
            print(f"🔍 Analisando posição {posicao}...")
        
        resultados = {}
        
        for numero in self.numeros_lotofacil:
            resultados[numero] = {}
            
            for nome_janela, tamanho_janela in self.janelas.items():
                score = self.calcular_score_posicional_geral(posicao, numero, tamanho_janela)
                resultados[numero][nome_janela] = score
        
        if debug:
            # Mostra top 5 para debug
            scores_gerais = [(num, dados['geral']) for num, dados in resultados.items()]
            scores_gerais.sort(key=lambda x: x[1], reverse=True)
            
            print(f"   📊 Top 5 números para {posicao}:")
            for i, (num, score) in enumerate(scores_gerais[:5], 1):
                print(f"      {i}º N{num}: {score:.3f}")
        
        return resultados
    
    def calcular_score_final_ponderado(self, scores_numero: Dict[str, float]) -> float:
        """
        Calcula score final ponderando as diferentes janelas temporais
        
        Args:
            scores_numero: Scores do número nas diferentes janelas
        
        Returns:
            float: Score final ponderado
        """
        # Pesos para cada janela temporal
        pesos_janelas = {
            'geral': 0.3,      # Base histórica
            'recente_30': 0.3, # Tendência de médio prazo
            'recente_15': 0.25, # Tendência de curto prazo
            'recente_5': 0.15   # Tendência imediata
        }
        
        score_final = sum(
            scores_numero[janela] * peso 
            for janela, peso in pesos_janelas.items()
        )
        
        return score_final
    
    def escolher_melhor_numero_posicao(self, posicao: str, numeros_ja_escolhidos: List[int] = None, 
                                      variacao: float = 0.2) -> Tuple[int, float]:
        """
        Escolhe o melhor número para uma posição específica
        
        Args:
            posicao: Posição a analisar
            numeros_ja_escolhidos: Números já escolhidos (para evitar repetição)
            variacao: Factor de variação (0.0 = determinístico, 1.0 = aleatório)
        
        Returns:
            Tuple: (numero_escolhido, score_final)
        """
        if numeros_ja_escolhidos is None:
            numeros_ja_escolhidos = []
        
        # Analisa a posição
        resultados = self.analisar_posicao(posicao)
        
        # Calcula score final para cada número disponível
        scores_finais = []
        
        for numero in self.numeros_lotofacil:
            if numero not in numeros_ja_escolhidos:
                score_final = self.calcular_score_final_ponderado(resultados[numero])
                scores_finais.append((numero, score_final))
        
        # Ordena por score (maior para menor)
        scores_finais.sort(key=lambda x: x[1], reverse=True)
        
        if not scores_finais:
            return (1, 0.0)
        
        # Introduz variação probabilística
        if variacao > 0 and len(scores_finais) > 1:
            # Seleciona dos melhores 50% com probabilidade ponderada
            top_percent = max(1, int(len(scores_finais) * 0.5))
            candidatos = scores_finais[:top_percent]
            
            # Aplicar random noise baseado na variação
            if random.random() < (variacao * 2):  # Aumentar probabilidade de variação
                # Seleciona com probabilidade ponderada pelos scores
                pesos = [score for _, score in candidatos]
                peso_total = sum(pesos) if sum(pesos) > 0 else 1
                probs = [p/peso_total for p in pesos]
                
                escolhido_idx = random.choices(range(int(int(int(len(candidatos))))), int(int(weights=probs))[0]
                return candidatos[escolhido_idx]
        
        return scores_finais[0]
    
    def analisar_correlacao_posicional(self, int(posicao_atual: str, numero_atual: int, 
                                     proxima_posicao: str, janela: int = 50)) -> Dict[int, float]:
        """
        Analisa correlação causal entre posições
        Ex: Se N1=1, qual o melhor N2?
        
        Args:
            posicao_atual: Posição atual (ex: N1)
            numero_atual: Número escolhido na posição atual
            proxima_posicao: Próxima posição a analisar (ex: N2)
            janela: Janela de análise
        
        Returns:
            Dict: Score de cada número para a próxima posição
        """
        dados = self.dados_resultados.tail(janela)
        
        # Filtra concursos onde a posição atual tem o número específico
        condicao = dados[posicao_atual] == numero_atual
        dados_filtrados = dados[condicao]
        
        if dados_filtrados.empty:
            # Se não há dados históricos, retorna scores neutros
            return {num: 0.5 for num in self.numeros_lotofacil}
        
        # Conta frequência de cada número na próxima posição
        total_ocorrencias = len(dados_filtrados)
        scores = {}
        
        for numero in self.numeros_lotofacil:
            freq = (dados_filtrados[proxima_posicao] == numero).sum()
            score = freq / total_ocorrencias if total_ocorrencias > 0 else 0.0
            scores[numero] = score
        
        return scores
    
    def gerar_combinacao_posicional(self, debug: bool = True, variacao: float = None) -> List[int]:
        """
        Gera uma combinação usando análise posicional completa
        
        Args:
            debug: Se deve mostrar debug
            variacao: Factor de variação (0.0-1.0), se None usa aleatório
        
        Returns:
            List[int]: Combinação gerada
        """
        if not self.carregar_dados_historicos():
            raise Exception("Erro ao carregar dados históricos")

        # Define variação aleatória se não especificada
        if variacao is None:
            variacao = random.uniform(0.1, 0.4)  # 10% a 40% de variação
        
        if debug:
            print("\n🎯 GERANDO COMBINAÇÃO POSICIONAL AVANÇADA")
            print("=" * 50)
        
        combinacao = []
        
        for i, posicao in enumerate(self.posicoes):
            if debug:
                print(f"\n🔍 Escolhendo número para {posicao}...")
            
            if i == 0:
                # Primeira posição: análise pura com variação
                numero, score = self.escolher_melhor_numero_posicao(posicao, combinacao, variacao)
            else:
                # Posições seguintes: considera correlação com anteriores
                numero_base, _ = self.escolher_melhor_numero_posicao(posicao, combinacao, variacao)
                
                # Analisa correlação com posição anterior
                if len(combinacao) > 0:
                    posicao_anterior = self.posicoes[i-1]
                    numero_anterior = combinacao[-1]
                    
                    correlacoes = self.analisar_correlacao_posicional(
                        posicao_anterior, numero_anterior, posicao
                    )
                    
                    # Combina score individual com correlação
                    resultados_posicao = self.analisar_posicao(posicao)
                    
                    scores_combinados = []
                    for num in self.numeros_lotofacil:
                        if num not in combinacao:
                            score_individual = self.calcular_score_final_ponderado(resultados_posicao[num])
                            score_correlacao = correlacoes.get(num, 0.0)
                            
                            # Pondera scores (70% individual, 30% correlação)
                            score_final = (score_individual * 0.7) + (score_correlacao * 0.3)
                            scores_combinados.append((num, score_final))
                    
                    # Escolhe melhor score combinado
                    scores_combinados.sort(key=lambda x: x[1], reverse=True)
                    numero = scores_combinados[0][0] if scores_combinados else numero_base
                    score = scores_combinados[0][1] if scores_combinados else 0.0
                else:
                    numero = numero_base
                    score = 0.0
            
            combinacao.append(numero)
            
            if debug:
                print(f"   ✅ {posicao}: {numero} (Score: {score:.3f})")
        
        if debug:
            print(f"\n🎉 COMBINAÇÃO GERADA: {combinacao}")
            print(f"   📊 Soma total: {sum(combinacao)}")
            print(f"   🔢 Pares: {sum(1 for n in combinacao if n % 2 == 0)}")
            print(f"   🔢 Ímpares: {sum(1 for n in combinacao if n % 2 == 1)}")
        
        return combinacao
    
    def gerar_multiplas_combinacoes(self, quantidade: int = 5) -> List[List[int]]:
        """
        Gera múltiplas combinações posicionais com estratégia de cobertura
        
        Primeira combinação: Mais eficaz e provável
        Demais combinações: Exatamente 10 números em comum com a principal
        
        Args:
            quantidade: Quantidade de combinações
        
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"🎯 Gerando {quantidade} combinações posicionais...")
        print("🎯 Estratégia: 1ª = Mais eficaz | Demais = 10 números em comum")
        
        # Carrega dados uma vez só
        if not self.carregar_dados_historicos():
            raise Exception("Erro ao carregar dados históricos")
        
        combinacoes = []
        
        # 1. GERA A COMBINAÇÃO PRINCIPAL (mais eficaz)
        print(f"\n--- Combinação Principal (1/{quantidade}) ---")
        print("🎯 Gerando combinação mais eficaz e provável...")
        
        # Para garantir que seja a mais eficaz, gera várias e escolhe a melhor
        candidatas_principais = []
        for tentativa in range(int(5:  # Gera 5 candidatas
            try:
                candidata = self.gerar_combinacao_posicional(debug=False)), int(int(variacao=0.1))
                score = self._avaliar_qualidade_combinacao_posicional(candidata)
                candidatas_principais.append((candidata), int(score)))
            except Exception as e:
                print(f"⚠️ Erro na candidata {tentativa+1}: {e}")
        
        if not candidatas_principais:
            raise Exception("Não foi possível gerar candidatas principais")
        
        # Escolhe a melhor candidata como combinação principal
        combinacao_principal, score_principal = max(candidatas_principais, key=lambda x: x[1])
        combinacoes.append(combinacao_principal)
        
        print(f"✅ Principal: {combinacao_principal} (Score: {score_principal:.1f})")
        
        # 2. GERA AS DEMAIS COMBINAÇÕES (10 números em comum)
        for i in range(1, int(int(quantidade):
            print(f"\n--- Combinação Derivada {i+1}/{quantidade} ---")
            print("🔗 Mantendo 10 números em comum com a principal...")
            
            try:
                combinacao_derivada = self._gerar_combinacao_com_overlap_posicional(
                    combinacao_principal, overlap_target=10
                )
                
                # Verifica overlap real
                overlap_real = len(set(combinacao_principal) & set(combinacao_derivada))
                score_derivada = self._avaliar_qualidade_combinacao_posicional(combinacao_derivada)
                
                combinacoes.append(combinacao_derivada)
                print(f"✅ Derivada: {combinacao_derivada} (Score: {score_derivada:.1f})")
                print(f"🔗 Overlap: {overlap_real}/15 números em comum")
                
            except Exception as e:
                print(f"❌ Erro na combinação derivada {i+1}: {e}")
                # Fallback: gera uma combinação normal com variação
                try:
                    variacao = 0.3 + (i * 0.15)
                    if variacao > 0.9:
                        variacao = random.uniform(0.4, 0.9)
                    combinacao = self.gerar_combinacao_posicional(debug=False, variacao=variacao)
                    combinacoes.append(combinacao)
                    print(f"⚠️ Fallback: {combinacao}")
                except:
                    print(f"❌ Falha total na combinação {i+1}")
        
        print(f"\n🎉 {len(combinacoes)} combinações posicionais geradas!")
        
        # Exibe resumo final
        print(f"\n🏆 RESUMO DAS {len(combinacoes)} COMBINAÇÕES:")
        for i, comb in enumerate(combinacoes):
            if i == 0:
                print(f"   {i+1}º: {comb} (Principal)")
            else:
                overlap = len(set(combinacoes[0]) & set(comb))
                print(f"   {i+1}º: {comb} (Derivada, overlap: {overlap})")
        
        return combinacoes
    
    def _gerar_combinacao_com_overlap_posicional(self, combinacao_base: List[int], overlap_target: int = 10) -> List[int]:
        """
        Gera combinação posicional com overlap específico
        
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
        numeros_disponiveis = [n for n in range(1, 26 if n not in combinacao_base]
        
        # 4. Prioriza números baseado na análise posicional
        candidatos_posicionais = []
        for numero in numeros_disponiveis:
            score = self._avaliar_potencial_numero_posicional(numero)
            candidatos_posicionais.append((numero), int(score)))
        
        # 5. Ordena por score e seleciona com alguma aleatoriedade
        candidatos_posicionais.sort(key=lambda x: x[1], reverse=True)
        
        numeros_novos = []
        pool_candidatos = candidatos_posicionais[:min(len(candidatos_posicionais), numeros_substituir * 3)]
        
        for i in range(int(int(int(numeros_substituir):
            if pool_candidatos:
                # Usa distribuição ponderada favorecendo os melhores
                pesos = [2 ** (len(pool_candidatos) - j) for j in range(int(len(pool_candidatos)))]
                candidato = random.choices(pool_candidatos)), int(int(weights=pesos))[0]
                numeros_novos.append(candidato[0])
                pool_candidatos.remove(candidato)
        
        # 6. Combina números mantidos + números novos
        combinacao_final = numeros_manter + numeros_novos
        combinacao_final.sort()
        
        return combinacao_final
    
    def _avaliar_potencial_numero_posicional(self, int(numero: int)) -> float:
        """
        Avalia o potencial de um número baseado na análise posicional
        
        Args:
            numero: Número a avaliar (1-25)
            
        Returns:
            float: Score de potencial do número
        """
        score = 50.0  # Score base
        
        try:
            # Baseado nas tendências posicionais se disponível
            if hasattr(self, 'inteligencia_posicional') and self.inteligencia_posicional:
                # Calcula média das tendências posicionais deste número
                scores_posicionais = []
                for pos in range(1, 16:
                    if pos in self.inteligencia_posicional:
                        numeros_pos = self.inteligencia_posicional[pos].get('numeros_recomendados'), int([]))
                        if numero in numeros_pos:
                            scores_posicionais.append(80)  # Score alto se recomendado
                        else:
                            scores_posicionais.append(40)  # Score baixo se não recomendado
                
                if scores_posicionais:
                    score = sum(scores_posicionais) / len(scores_posicionais)
            
            # Ajustes baseados em características gerais
            # Bonifica números na faixa média
            if 8 <= numero <= 18:
                score += 5
            
            # Penaliza extremos
            if numero <= 3 or numero >= 23:
                score -= 5
            
            # Adiciona componente aleatório pequeno
            score += random.uniform(-3, 3)
            
        except Exception as e:
            print(f"⚠️ Erro na avaliação de potencial: {e}")
        
        return max(0, score)
    
    def _avaliar_qualidade_combinacao_posicional(self, combinacao: List[int]) -> float:
        """
        Avalia a qualidade de uma combinação baseada nos critérios posicionais
        
        Args:
            combinacao: Combinação a avaliar
            
        Returns:
            float: Score de qualidade (0-100)
        """
        score = 50.0  # Score base
        
        try:
            # 1. Compatibilidade com inteligência posicional
            if hasattr(self, 'inteligencia_posicional') and self.inteligencia_posicional:
                matches_posicionais = 0
                total_posicoes = 0
                
                for pos, dados in self.inteligencia_posicional.items():
                    if isinstance(pos, int) and 1 <= pos <= 15:
                        numeros_recomendados = dados.get('numeros_recomendados', [])
                        if pos <= len(combinacao):
                            numero_na_posicao = sorted(combinacao)[pos-1]
                            if numero_na_posicao in numeros_recomendados:
                                matches_posicionais += 1
                            total_posicoes += 1
                
                if total_posicoes > 0:
                    score += (matches_posicionais / total_posicoes) * 30  # Peso 30%
            
            # 2. Características básicas da combinação
            soma = sum(combinacao)
            if 180 <= soma <= 210:  # Faixa boa de soma
                score += 10
            elif 170 <= soma <= 220:  # Faixa aceitável
                score += 5
            
            # 3. Distribuição por quintis
            quintis = [0] * 5
            for numero in combinacao:
                quintil = min(4, (numero - 1) // 5)
                quintis[quintil] += 1
            
            # Bonifica distribuição balanceada
            if all(2 <= q <= 4 for q in quintis):
                score += 8
            elif all(1 <= q <= 5 for q in quintis):
                score += 4
            
            # 4. Evita muitos números consecutivos
            consecutivos = 0
            combinacao_sorted = sorted(combinacao)
            for i in range(int(int(int(len(combinacao_sorted)) - 1):
                if combinacao_sorted[i+1] - combinacao_sorted[i] == 1:
                    consecutivos += 1
            
            if consecutivos <= 2:
                score += 5
            elif consecutivos >= 6:
                score -= 10
            
        except Exception as e:
            print(f"⚠️ Erro na avaliação de qualidade: {e}")
        
        return max(0)), int(int(min(100), int(score))))

# Função para integração com o sistema principal
def gerar_combinacoes_posicionais(quantidade: int = 5) -> List[List[int]]:
    """
    Função principal para geração de combinações posicionais
    
    Args:
        quantidade: Quantidade de combinações
    
    Returns:
        List[List[int]]: Lista de combinações
    """
    try:
        gerador = GeradorPosicional()
        return gerador.gerar_multiplas_combinacoes(quantidade)
    except Exception as e:
        print(f"❌ Erro no gerador posicional: {e}")
        return []

if __name__ == "__main__":
    # Teste do gerador
    print("🧪 TESTE DO GERADOR POSICIONAL")
    print("=" * 40)
    
    gerador = GeradorPosicional()
    
    try:
        # Teste com uma combinação
        combinacao = gerador.gerar_combinacao_posicional(debug=True)
        print(f"\n✅ Teste concluído!")
        print(f"🎯 Combinação: {combinacao}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")


# =============================================================================
# FUNÇÃO OTIMIZADA COM INTELIGÊNCIA N12
# =============================================================================

@aplicar_inteligencia_n12
def gerador_otimizado_n12(quantidade=30):
    """
    Versão otimizada do gerador_posicional com inteligência N12 aplicada
    
    Esta função usa o gerador original mas aplica automaticamente
    os filtros inteligentes baseados na teoria N12 comprovada.
    """
    print(f"🧠 {nome_base.upper()} COM INTELIGÊNCIA N12")
    print("="*50)
    
    # Usar geração inteligente nativa para máximos resultados
    combinacoes = gerar_combinacoes_inteligentes_n12(quantidade)
    
    print(f"✅ {len(combinacoes)} combinações otimizadas geradas")
    print("📊 100% alinhadas com estratégia N12 atual")
    
    return combinacoes

def executar_versao_suprema():
    """Executa a versão suprema do gerador com inteligência N12"""
    print("🏆 EXECUTANDO VERSÃO SUPREMA N12")
    print("="*60)
    
    combinacoes = gerador_otimizado_n12(30)
    
    # Salvar resultado
    nome_arquivo = f"resultado_{nome_base}_n12.txt"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"🏆 RESULTADO {nome_base.upper()} N12\n")
        f.write("="*50 + "\n")
        f.write(f"📅 Gerado em: 19/09/2025\n")
        f.write(f"🎯 Estratégia: DIVERSIFICAR_COM_ENFASE_EXTREMOS\n")
        f.write(f"📊 Combinações: {len(combinacoes)}\n")
        f.write("="*50 + "\n\n")
        
        for i, comb in enumerate(combinacoes, 1):
            n12 = comb[11]
            baixos = len([n for n in comb if 1 <= n <= 8])
            medios = len([n for n in comb if 9 <= n <= 17])
            altos = len([n for n in comb if 18 <= n <= 25])
            
            f.write(f"Jogo {i:2d}: {comb}\n")
            f.write(f"        N12={n12}, B={baixos}, M={medios}, A={altos}\n\n")
    
    print(f"💾 Resultado salvo em: {nome_arquivo}")
    return combinacoes

if __name__ == "__main__":
    executar_versao_suprema()
