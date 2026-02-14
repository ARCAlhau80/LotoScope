#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 ANALISADOR DE COMPORTAMENTO NUMÉRICO - SISTEMA REVOLUCIONÁRIO
================================================================
Sistema avançado de análise comportamental dos números da Lotofácil
baseado em padrões de sequências e pausas em janelas de 15 concursos.

Características:
- Análise dinâmica com parâmetro de último concurso
- Identificação de sequências e pausas
- Classificação comportamental dos números
- Score inteligente baseado em múltiplos critérios
- Geração do núcleo dos 10 melhores números

Uso:
    python analisador_comportamento_numerico.py [ultimo_concurso]
    
Se não especificar ultimo_concurso, usa o último da base.
"""

import sys
import os
from pathlib import Path
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

from datetime import datetime
import statistics

class AnalisadorComportamentoNumerico:
    """Sistema de análise comportamental dos números da Lotofácil"""
    
    def __init__(self, ultimo_concurso=None):
        """
        Inicializa o analisador
        
        Args:
            ultimo_concurso (int, optional): Concurso final da janela de análise.
                                           Se None, usa o último da base.
        """
        self.ultimo_concurso = ultimo_concurso
        self.janela_concursos = 15
        self.numeros = list(range(1, 26))  # 1 a 25
        self.db = DatabaseConfig()  # Instância da configuração do banco
        
        # Pesos para cálculo do score
        self.pesos = {
            'frequencia_base': 0.25,      # Quantas vezes saiu
            'estabilidade_sequencias': 0.30,  # Regularidade das sequências
            'padrao_pausas': 0.20,        # Previsibilidade das pausas
            'estado_atual': 0.15,         # Tendência atual
            'tendencia_historica': 0.10   # Comparação com histórico
        }
        
        print("🧠 ANALISADOR DE COMPORTAMENTO NUMÉRICO INICIALIZADO")
        print(f"📊 Janela de análise: {self.janela_concursos} concursos")
        
    def obter_ultimo_concurso_base(self):
        """Obtém o último concurso disponível na base"""
        try:
            query = "SELECT MAX(concurso) as ultimo FROM resultados_int"
            resultado = self.db.execute_query_dataframe(query)
            if resultado is not None and not resultado.empty:
                return resultado.iloc[0]['ultimo']
            return None
        except Exception as e:
            print(f"❌ Erro ao obter último concurso: {e}")
            return None
    
    def definir_janela_analise(self):
        """Define a janela de concursos para análise"""
        if self.ultimo_concurso is None:
            self.ultimo_concurso = self.obter_ultimo_concurso_base()
            if self.ultimo_concurso is None:
                raise ValueError("Não foi possível determinar o último concurso")
        
        self.concurso_inicial = self.ultimo_concurso - (self.janela_concursos - 1)
        
        print(f"🎯 Janela de análise definida:")
        print(f"   📅 Concursos: {self.concurso_inicial} a {self.ultimo_concurso}")
        print(f"   📊 Total: {self.janela_concursos} concursos")
        
        return self.concurso_inicial, self.ultimo_concurso
    
    def obter_resultados_janela(self):
        """Obtém os resultados dos concursos da janela de análise"""
        try:
            query = """
            SELECT concurso, 
                   n1, n2, n3, n4, n5, n6, n7, n8, n9, n10,
                   n11, n12, n13, n14, n15
            FROM resultados_int 
            WHERE concurso >= ? AND concurso <= ?
            ORDER BY concurso
            """
            
            df = self.db.execute_query_dataframe(query, (self.concurso_inicial, self.ultimo_concurso))
            
            if df is None or len(df) != self.janela_concursos:
                raise ValueError(f"Esperados {self.janela_concursos} concursos, obtidos {len(df) if df is not None else 0}")
            
            # Converte DataFrame para lista de dicionários
            resultados = df.to_dict('records')
            
            print(f"✅ Obtidos {len(resultados)} concursos para análise")
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao obter resultados: {e}")
            raise
    
    def mapear_aparicoes_numero(self, numero, resultados):
        """
        Mapeia as aparições de um número específico na janela
        
        Args:
            numero (int): Número a analisar (1-25)
            resultados (list): Lista de resultados dos concursos
            
        Returns:
            list: Lista binária (1=apareceu, 0=não apareceu) por concurso
        """
        aparicoes = []
        
        for resultado in resultados:
            # Extrai os 15 números sorteados
            nums_sorteados = [
                resultado['n1'], resultado['n2'], resultado['n3'], resultado['n4'], resultado['n5'],
                resultado['n6'], resultado['n7'], resultado['n8'], resultado['n9'], resultado['n10'],
                resultado['n11'], resultado['n12'], resultado['n13'], resultado['n14'], resultado['n15']
            ]
            
            # Verifica se o número apareceu
            apareceu = 1 if numero in nums_sorteados else 0
            aparicoes.append(apareceu)
        
        return aparicoes
    
    def identificar_sequencias(self, aparicoes):
        """
        Identifica sequências de aparições consecutivas
        
        Args:
            aparicoes (list): Lista binária de aparições
            
        Returns:
            list: Lista com tamanhos das sequências de aparições
        """
        sequencias = []
        sequencia_atual = 0
        
        for apareceu in aparicoes:
            if apareceu == 1:
                sequencia_atual += 1
            else:
                if sequencia_atual > 0:
                    sequencias.append(sequencia_atual)
                    sequencia_atual = 0
        
        # Adiciona a última sequência se terminou com aparição
        if sequencia_atual > 0:
            sequencias.append(sequencia_atual)
            
        return sequencias
    
    def calcular_pausas(self, aparicoes):
        """
        Calcula as pausas (sequências de não aparições)
        
        Args:
            aparicoes (list): Lista binária de aparições
            
        Returns:
            list: Lista com tamanhos das pausas
        """
        pausas = []
        pausa_atual = 0
        
        for apareceu in aparicoes:
            if apareceu == 0:
                pausa_atual += 1
            else:
                if pausa_atual > 0:
                    pausas.append(pausa_atual)
                    pausa_atual = 0
        
        # Adiciona a última pausa se terminou sem aparição
        if pausa_atual > 0:
            pausas.append(pausa_atual)
            
        return pausas
    
    def avaliar_estabilidade(self, sequencias, pausas):
        """
        Avalia a estabilidade do comportamento baseado em sequências e pausas
        
        Args:
            sequencias (list): Lista de tamanhos das sequências
            pausas (list): Lista de tamanhos das pausas
            
        Returns:
            dict: Dicionário com métricas de estabilidade
        """
        metricas = {
            'total_sequencias': len(sequencias),
            'sequencia_media': statistics.mean(sequencias) if sequencias else 0,
            'sequencia_desvio': statistics.stdev(sequencias) if len(sequencias) > 1 else 0,
            'total_pausas': len(pausas),
            'pausa_media': statistics.mean(pausas) if pausas else 0,
            'pausa_desvio': statistics.stdev(pausas) if len(pausas) > 1 else 0,
            'regularidade_sequencias': 0,
            'regularidade_pausas': 0
        }
        
        # Calcula regularidade (inverso do coeficiente de variação)
        if metricas['sequencia_media'] > 0:
            cv_seq = metricas['sequencia_desvio'] / metricas['sequencia_media']
            metricas['regularidade_sequencias'] = max(0, 1 - cv_seq)
        
        if metricas['pausa_media'] > 0:
            cv_pausa = metricas['pausa_desvio'] / metricas['pausa_media']
            metricas['regularidade_pausas'] = max(0, 1 - cv_pausa)
        
        return metricas
    
    def determinar_estado_atual(self, aparicoes):
        """
        Determina o estado atual do número (em sequência ou em pausa)
        
        Args:
            aparicoes (list): Lista binária de aparições
            
        Returns:
            dict: Estado atual e tamanho da sequência/pausa atual
        """
        if not aparicoes:
            return {'estado': 'indefinido', 'tamanho': 0, 'tendencia': 0}
        
        # Analisa os últimos valores
        ultimo = aparicoes[-1]
        tamanho_atual = 1
        
        # Conta quantos concursos consecutivos no mesmo estado
        for i in range(len(aparicoes) - 2, -1, -1):
            if aparicoes[i] == ultimo:
                tamanho_atual += 1
            else:
                break
        
        estado = 'em_sequencia' if ultimo == 1 else 'em_pausa'
        
        # Calcula tendência baseada nos últimos 5 concursos
        ultimos_5 = aparicoes[-5:] if len(aparicoes) >= 5 else aparicoes
        tendencia = sum(ultimos_5) / len(ultimos_5)
        
        return {
            'estado': estado,
            'tamanho': tamanho_atual,
            'tendencia': tendencia
        }
    
    def classificar_comportamento(self, metricas, estado_atual, frequencia):
        """
        Classifica o tipo de comportamento do número
        
        Returns:
            str: Tipo de comportamento identificado
        """
        freq_alta = frequencia >= 0.6  # Apareceu em 60%+ dos concursos
        regular_seq = metricas['regularidade_sequencias'] >= 0.5
        regular_pausa = metricas['regularidade_pausas'] >= 0.5
        
        if freq_alta and regular_seq and regular_pausa:
            return 'ESTAVEL_FREQUENTE'
        elif not freq_alta and regular_seq and regular_pausa:
            return 'ESTAVEL_ESPORADICO'
        elif freq_alta and (not regular_seq or not regular_pausa):
            return 'IRREGULAR_ATIVO'
        elif not freq_alta and (not regular_seq or not regular_pausa):
            return 'IRREGULAR_PASSIVO'
        elif metricas['sequencia_media'] > 0 and metricas['pausa_media'] > 0:
            # Verifica se há padrão cíclico
            ciclo_score = abs(metricas['sequencia_media'] - metricas['pausa_media'])
            if ciclo_score <= 1.0:
                return 'EM_CICLO'
        
        # Verifica mudança de tendência
        if estado_atual['tendencia'] > 0.7 or estado_atual['tendencia'] < 0.3:
            return 'EM_TENDENCIA'
        
        return 'NEUTRO'
    
    def calcular_score_numero(self, numero, aparicoes, metricas, estado_atual):
        """
        Calcula o score comportamental de um número
        
        Returns:
            float: Score de 0 a 100
        """
        # 1. Frequência base
        frequencia = sum(aparicoes) / len(aparicoes)
        score_freq = frequencia * 100
        
        # 2. Estabilidade de sequências
        estab_seq = metricas['regularidade_sequencias'] * 100
        
        # 3. Padrão de pausas
        padrao_pausas = metricas['regularidade_pausas'] * 100
        
        # 4. Estado atual
        if estado_atual['estado'] == 'em_sequencia':
            # Bonifica se está em sequência, mas penaliza se já é muito longa
            bonus = max(0, 20 - (estado_atual['tamanho'] - 1) * 5)
        else:
            # Bonifica se pausa está ficando longa (tendência de sair)
            bonus = min(20, estado_atual['tamanho'] * 3)
        
        score_estado = min(100, bonus + estado_atual['tendencia'] * 50)
        
        # 5. Tendência histórica (simplificado)
        score_tendencia = estado_atual['tendencia'] * 100
        
        # Calcula score final ponderado
        score_final = (
            score_freq * self.pesos['frequencia_base'] +
            estab_seq * self.pesos['estabilidade_sequencias'] +
            padrao_pausas * self.pesos['padrao_pausas'] +
            score_estado * self.pesos['estado_atual'] +
            score_tendencia * self.pesos['tendencia_historica']
        )
        
        return round(score_final, 1)
    
    def analisar_todos_numeros(self):
        """Executa análise completa de todos os números"""
        print("\n🔍 INICIANDO ANÁLISE COMPORTAMENTAL...")
        
        # Define janela de análise
        self.definir_janela_analise()
        
        # Obtém resultados
        resultados = self.obter_resultados_janela()
        
        # Analisa cada número
        analises = {}
        
        print(f"\n📊 Analisando comportamento dos 25 números...")
        
        for numero in self.numeros:
            # Mapeia aparições
            aparicoes = self.mapear_aparicoes_numero(numero, resultados)
            
            # Identifica sequências e pausas
            sequencias = self.identificar_sequencias(aparicoes)
            pausas = self.calcular_pausas(aparicoes)
            
            # Avalia estabilidade
            metricas = self.avaliar_estabilidade(sequencias, pausas)
            
            # Estado atual
            estado_atual = self.determinar_estado_atual(aparicoes)
            
            # Frequência
            frequencia = sum(aparicoes) / len(aparicoes)
            
            # Classificação
            comportamento = self.classificar_comportamento(metricas, estado_atual, frequencia)
            
            # Score
            score = self.calcular_score_numero(numero, aparicoes, metricas, estado_atual)
            
            # Armazena análise
            analises[numero] = {
                'aparicoes': aparicoes,
                'sequencias': sequencias,
                'pausas': pausas,
                'metricas': metricas,
                'estado_atual': estado_atual,
                'comportamento': comportamento,
                'frequencia': frequencia,
                'score': score
            }
        
        return analises
    
    def gerar_relatorio_numero(self, numero, analise):
        """Gera relatório detalhado de um número específico"""
        print(f"\n🔢 NÚMERO {numero:2d} - Score: {analise['score']:5.1f}")
        print("=" * 50)
        
        # Aparições
        aparicoes_str = "".join(['●' if x else '○' for x in analise['aparicoes']])
        print(f"📊 Aparições: {aparicoes_str}")
        print(f"   Frequência: {analise['frequencia']:.1%} ({sum(analise['aparicoes'])}/{len(analise['aparicoes'])})")
        
        # Sequências
        if analise['sequencias']:
            print(f"🔗 Sequências: {analise['sequencias']}")
            print(f"   Média: {analise['metricas']['sequencia_media']:.1f}")
            print(f"   Regularidade: {analise['metricas']['regularidade_sequencias']:.1%}")
        
        # Pausas
        if analise['pausas']:
            print(f"⏸️  Pausas: {analise['pausas']}")
            print(f"   Média: {analise['metricas']['pausa_media']:.1f}")
            print(f"   Regularidade: {analise['metricas']['regularidade_pausas']:.1%}")
        
        # Estado atual
        estado = analise['estado_atual']
        estado_emoji = "🔥" if estado['estado'] == 'em_sequencia' else "❄️"
        print(f"{estado_emoji} Estado: {estado['estado'].replace('_', ' ').title()}")
        print(f"   Duração atual: {estado['tamanho']} concursos")
        print(f"   Tendência: {estado['tendencia']:.1%}")
        
        # Comportamento
        comportamento = analise['comportamento']
        comp_emoji = {
            'ESTAVEL_FREQUENTE': '🟢',
            'ESTAVEL_ESPORADICO': '🟡', 
            'IRREGULAR_ATIVO': '🟠',
            'IRREGULAR_PASSIVO': '🔴',
            'EM_CICLO': '🔵',
            'EM_TENDENCIA': '🟣',
            'NEUTRO': '⚪'
        }.get(comportamento, '❓')
        
        print(f"{comp_emoji} Comportamento: {comportamento.replace('_', ' ').title()}")
    
    def obter_top_10_numeros(self, analises):
        """Obtém os 10 números com melhor score comportamental"""
        # Ordena por score decrescente
        numeros_ordenados = sorted(analises.items(), key=lambda x: x[1]['score'], reverse=True)
        
        top_10 = numeros_ordenados[:10]
        
        print("\n🏆 TOP 10 NÚMEROS - NÚCLEO COMPORTAMENTAL")
        print("=" * 60)
        
        for i, (numero, analise) in enumerate(top_10, 1):
            estado_emoji = "🔥" if analise['estado_atual']['estado'] == 'em_sequencia' else "❄️"
            comp_emoji = {
                'ESTAVEL_FREQUENTE': '🟢',
                'ESTAVEL_ESPORADICO': '🟡',
                'IRREGULAR_ATIVO': '🟠',
                'IRREGULAR_PASSIVO': '🔴',
                'EM_CICLO': '🔵',
                'EM_TENDENCIA': '🟣',
                'NEUTRO': '⚪'
            }.get(analise['comportamento'], '❓')
            
            print(f"{i:2d}º lugar: Número {numero:2d} - Score: {analise['score']:5.1f} {estado_emoji}{comp_emoji}")
            print(f"        Freq: {analise['frequencia']:.1%} | {analise['comportamento'].replace('_', ' ').title()}")
        
        nucleo = [num for num, _ in top_10]
        print(f"\n🎯 NÚCLEO COMPORTAMENTAL: {sorted(nucleo)}")
        
        return nucleo, top_10
    
    def gerar_relatorio_completo(self, analises):
        """Gera relatório completo da análise"""
        print(f"\n📋 RELATÓRIO COMPLETO - ANÁLISE COMPORTAMENTAL")
        print("=" * 70)
        print(f"📅 Período: Concursos {self.concurso_inicial} a {self.ultimo_concurso}")
        print(f"📊 Janela: {self.janela_concursos} concursos")
        print(f"🕐 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Estatísticas gerais
        scores = [analise['score'] for analise in analises.values()]
        frequencias = [analise['frequencia'] for analise in analises.values()]
        
        print(f"\n📈 ESTATÍSTICAS GERAIS:")
        print(f"   Score médio: {statistics.mean(scores):.1f}")
        print(f"   Score mediano: {statistics.median(scores):.1f}")
        print(f"   Frequência média: {statistics.mean(frequencias):.1%}")
        
        # Distribuição por comportamento
        comportamentos = {}
        for analise in analises.values():
            comp = analise['comportamento']
            comportamentos[comp] = comportamentos.get(comp, 0) + 1
        
        print(f"\n🏷️  DISTRIBUIÇÃO POR COMPORTAMENTO:")
        for comp, qtd in sorted(comportamentos.items()):
            print(f"   {comp.replace('_', ' ').title()}: {qtd} números")
        
        # Top 10
        nucleo, top_10 = self.obter_top_10_numeros(analises)
        
        return nucleo, analises

def main():
    """Função principal"""
    # Verifica se foi passado parâmetro de último concurso
    ultimo_concurso = None
    if len(sys.argv) > 1:
        try:
            ultimo_concurso = int(sys.argv[1])
            print(f"🎯 Usando último concurso especificado: {ultimo_concurso}")
        except ValueError:
            print("⚠️ Parâmetro inválido. Usando último concurso da base.")
    
    try:
        # Inicializa analisador
        analisador = AnalisadorComportamentoNumerico(ultimo_concurso)
        
        # Executa análise
        analises = analisador.analisar_todos_numeros()
        
        # Gera relatório
        nucleo, analises_completas = analisador.gerar_relatorio_completo(analises)
        
        # Salva resultado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"analise_comportamental_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(f"ANÁLISE COMPORTAMENTAL - NÚCLEO DOS 10 MELHORES\n")
            f.write(f"Período: {analisador.concurso_inicial} a {analisador.ultimo_concurso}\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            f.write(f"NÚCLEO COMPORTAMENTAL: {sorted(nucleo)}\n\n")
            
            for i, (numero, analise) in enumerate([(n, analises[n]) for n in nucleo], 1):
                f.write(f"{i:2d}º: Número {numero:2d} - Score {analise['score']:5.1f} - {analise['comportamento']}\n")
        
        print(f"\n💾 Relatório salvo: {arquivo}")
        print("\n🎉 ANÁLISE COMPORTAMENTAL CONCLUÍDA!")
        
    except Exception as e:
        print(f"\n❌ ERRO na análise: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
