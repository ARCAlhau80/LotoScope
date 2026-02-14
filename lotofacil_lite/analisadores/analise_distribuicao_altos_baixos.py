#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANÁLISE DE DISTRIBUIÇÃO ALTOS E BAIXOS
==========================================

Análise detalhada da distribuição entre números baixos (2-13) e altos (14-25)
excluindo N1, para identificar padrões e tendências preditivas.

Autor: AR CALHAU
Data: 18/09/2025
"""

import sys
import os
from pathlib import Path
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

import statistics
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

class AnalisadorDistribuicaoAltosBaixos:
    def __init__(self):
        self.db_config = db_config
        self.dados_historicos = []
        self.estatisticas = {}
        
    def carregar_dados_historicos(self):
        """Carrega dados históricos da tabela Resultados_INT"""
        print("🔍 Carregando dados históricos da Resultados_INT...")
        
        try:
            # Conectar ao banco
            if not self.db_config.test_connection():
                print("❌ Erro na conexão com banco de dados")
                return False
            
            # Query para buscar todos os resultados ordenados por concurso
            query = """
            SELECT Concurso, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
            
            resultados = self.db_config.execute_query(query)
            
            for row in resultados:
                concurso = row[0]
                # Excluindo N1, pegamos N2 até N15 (14 números)
                numeros = [row[i] for i in range(1, 15)]
                
                # Separar em baixos (2-13) e altos (14-25)
                baixos = [n for n in numeros if 2 <= n <= 13]
                altos = [n for n in numeros if 14 <= n <= 25]
                
                self.dados_historicos.append({
                    'concurso': concurso,
                    'numeros_completos': sorted(numeros),
                    'baixos': sorted(baixos),
                    'altos': sorted(altos),
                    'qtd_baixos': len(baixos),
                    'qtd_altos': len(altos),
                    'proporcao_baixos': len(baixos) / 14,
                    'proporcao_altos': len(altos) / 14
                })
            
            print(f"✅ {len(self.dados_historicos)} concursos carregados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analisar_distribuicao_geral(self):
        """Análise geral da distribuição ao longo da história"""
        print("\n" + "="*70)
        print("📊 ANÁLISE GERAL DE DISTRIBUIÇÃO ALTOS/BAIXOS")
        print("="*70)
        
        if not self.dados_historicos:
            print("❌ Sem dados para análise")
            return
        
        # Estatísticas básicas
        qtds_baixos = [d['qtd_baixos'] for d in self.dados_historicos]
        qtds_altos = [d['qtd_altos'] for d in self.dados_historicos]
        
        print(f"🔢 NÚMEROS BAIXOS (2-13): Total de 12 números disponíveis")
        print(f"   • Média de baixos por jogo: {statistics.mean(qtds_baixos):.2f}")
        print(f"   • Mediana: {statistics.median(qtds_baixos):.1f}")
        print(f"   • Mínimo: {min(qtds_baixos)} | Máximo: {max(qtds_baixos)}")
        print(f"   • Desvio padrão: {statistics.stdev(qtds_baixos):.2f}")
        
        print(f"\n🔢 NÚMEROS ALTOS (14-25): Total de 12 números disponíveis")
        print(f"   • Média de altos por jogo: {statistics.mean(qtds_altos):.2f}")
        print(f"   • Mediana: {statistics.median(qtds_altos):.1f}")
        print(f"   • Mínimo: {min(qtds_altos)} | Máximo: {max(qtds_altos)}")
        print(f"   • Desvio padrão: {statistics.stdev(qtds_altos):.2f}")
        
        # Distribuição de frequências
        print(f"\n📈 DISTRIBUIÇÃO DE FREQUÊNCIAS:")
        contador_baixos = Counter(qtds_baixos)
        contador_altos = Counter(qtds_altos)
        
        print("   BAIXOS (2-13):")
        for qtd in sorted(contador_baixos.keys()):
            freq = contador_baixos[qtd]
            perc = (freq / len(self.dados_historicos)) * 100
            print(f"   • {qtd} baixos: {freq} vezes ({perc:.1f}%)")
        
        print("\n   ALTOS (14-25):")
        for qtd in sorted(contador_altos.keys()):
            freq = contador_altos[qtd]
            perc = (freq / len(self.dados_historicos)) * 100
            print(f"   • {qtd} altos: {freq} vezes ({perc:.1f}%)")
        
        # Armazenar estatísticas
        self.estatisticas['geral'] = {
            'media_baixos': statistics.mean(qtds_baixos),
            'media_altos': statistics.mean(qtds_altos),
            'distribuicao_baixos': contador_baixos,
            'distribuicao_altos': contador_altos
        }
    
    def analisar_tendencias_sequenciais(self):
        """Analisa tendências entre jogos consecutivos"""
        print("\n" + "="*70)
        print("🔄 ANÁLISE DE TENDÊNCIAS SEQUENCIAIS")
        print("="*70)
        
        # Analisar transições
        transicoes = {
            'mais_baixos_para_mais_baixos': 0,
            'mais_baixos_para_equilibrio': 0,
            'mais_baixos_para_mais_altos': 0,
            'equilibrio_para_mais_baixos': 0,
            'equilibrio_para_equilibrio': 0,
            'equilibrio_para_mais_altos': 0,
            'mais_altos_para_mais_baixos': 0,
            'mais_altos_para_equilibrio': 0,
            'mais_altos_para_mais_altos': 0
        }
        
        # Definir categorias
        def categorizar_jogo(qtd_baixos, qtd_altos):
            if qtd_baixos > qtd_altos + 1:
                return 'mais_baixos'
            elif qtd_altos > qtd_baixos + 1:
                return 'mais_altos'
            else:
                return 'equilibrio'
        
        # Analisar sequências
        for i in range(len(self.dados_historicos) - 1):
            atual = self.dados_historicos[i]
            proximo = self.dados_historicos[i + 1]
            
            cat_atual = categorizar_jogo(atual['qtd_baixos'], atual['qtd_altos'])
            cat_proximo = categorizar_jogo(proximo['qtd_baixos'], proximo['qtd_altos'])
            
            chave = f"{cat_atual}_para_{cat_proximo}"
            if chave in transicoes:
                transicoes[chave] += 1
        
        total_transicoes = sum(transicoes.values())
        
        print("🔄 MATRIZ DE TRANSIÇÕES:")
        print(f"   Total de transições analisadas: {total_transicoes}")
        print("\n   ORIGEM → DESTINO:")
        
        for origem in ['mais_baixos', 'equilibrio', 'mais_altos']:
            print(f"\n   🎯 {origem.replace('_', ' ').upper()}:")
            for destino in ['mais_baixos', 'equilibrio', 'mais_altos']:
                chave = f"{origem}_para_{destino}"
                count = transicoes.get(chave, 0)
                perc = (count / total_transicoes) * 100 if total_transicoes > 0 else 0
                print(f"      → {destino.replace('_', ' ')}: {count} ({perc:.1f}%)")
        
        # Calcular probabilidades condicionais
        print(f"\n📊 PROBABILIDADES CONDICIONAIS:")
        
        for origem in ['mais_baixos', 'equilibrio', 'mais_altos']:
            total_origem = sum(transicoes.get(f"{origem}_para_{dest}", 0) 
                             for dest in ['mais_baixos', 'equilibrio', 'mais_altos'])
            
            if total_origem > 0:
                print(f"\n   Se jogo atual tem {origem.replace('_', ' ').upper()}:")
                for destino in ['mais_baixos', 'equilibrio', 'mais_altos']:
                    count = transicoes.get(f"{origem}_para_{destino}", 0)
                    prob = (count / total_origem) * 100
                    print(f"      • Próximo {destino.replace('_', ' ')}: {prob:.1f}%")
        
        self.estatisticas['transicoes'] = transicoes
    
    def analisar_padroes_ciclicos(self):
        """Analisa padrões cíclicos e sequências"""
        print("\n" + "="*70)
        print("🔄 ANÁLISE DE PADRÕES CÍCLICOS")
        print("="*70)
        
        # Detectar sequências de mesmo tipo
        sequencias = []
        sequencia_atual = {
            'tipo': None,
            'inicio': None,
            'tamanho': 0
        }
        
        def categorizar_jogo(qtd_baixos, qtd_altos):
            if qtd_baixos > qtd_altos + 1:
                return 'mais_baixos'
            elif qtd_altos > qtd_baixos + 1:
                return 'mais_altos'
            else:
                return 'equilibrio'
        
        for i, dados in enumerate(self.dados_historicos):
            categoria = categorizar_jogo(dados['qtd_baixos'], dados['qtd_altos'])
            
            if sequencia_atual['tipo'] == categoria:
                sequencia_atual['tamanho'] += 1
            else:
                if sequencia_atual['tipo'] is not None:
                    sequencias.append(sequencia_atual.copy())
                
                sequencia_atual = {
                    'tipo': categoria,
                    'inicio': i,
                    'tamanho': 1
                }
        
        # Adicionar última sequência
        if sequencia_atual['tipo'] is not None:
            sequencias.append(sequencia_atual)
        
        # Analisar sequências por tipo
        print("🔄 SEQUÊNCIAS DETECTADAS:")
        
        for tipo in ['mais_baixos', 'equilibrio', 'mais_altos']:
            seqs_tipo = [s for s in sequencias if s['tipo'] == tipo]
            if seqs_tipo:
                tamanhos = [s['tamanho'] for s in seqs_tipo]
                print(f"\n   📊 {tipo.replace('_', ' ').upper()}:")
                print(f"      • Total de sequências: {len(seqs_tipo)}")
                print(f"      • Tamanho médio: {statistics.mean(tamanhos):.1f}")
                print(f"      • Maior sequência: {max(tamanhos)} jogos")
                print(f"      • Menor sequência: {min(tamanhos)} jogos")
                
                # Distribuição de tamanhos
                contador_tamanhos = Counter(tamanhos)
                print(f"      • Distribuição:")
                for tam in sorted(contador_tamanhos.keys()):
                    freq = contador_tamanhos[tam]
                    perc = (freq / len(seqs_tipo)) * 100
                    print(f"        - {tam} jogos: {freq} vezes ({perc:.1f}%)")
        
        self.estatisticas['sequencias'] = sequencias
    
    def detectar_padroes_preditivos(self):
        """Detecta padrões que podem ser úteis para previsão"""
        print("\n" + "="*70)
        print("🎯 DETECÇÃO DE PADRÕES PREDITIVOS")
        print("="*70)
        
        # Análise de últimos 10 jogos para identificar tendências atuais
        ultimos_10 = self.dados_historicos[-10:]
        
        print("📈 ANÁLISE DOS ÚLTIMOS 10 JOGOS:")
        for i, dados in enumerate(ultimos_10, 1):
            categoria = self.categorizar_jogo_detalhado(dados['qtd_baixos'], dados['qtd_altos'])
            print(f"   {i:2}. Concurso {dados['concurso']}: "
                  f"{dados['qtd_baixos']} baixos | {dados['qtd_altos']} altos "
                  f"({categoria})")
        
        # Identificar tendência atual
        categorias_recentes = []
        for dados in ultimos_10:
            cat = self.categorizar_jogo_detalhado(dados['qtd_baixos'], dados['qtd_altos'])
            categorias_recentes.append(cat)
        
        print(f"\n🔍 TENDÊNCIA ATUAL:")
        contador_recente = Counter(categorias_recentes)
        for cat, freq in contador_recente.most_common():
            perc = (freq / len(categorias_recentes)) * 100
            print(f"   • {cat}: {freq}/10 jogos ({perc:.0f}%)")
        
        # Previsão baseada em padrões históricos
        ultimo_jogo = self.dados_historicos[-1]
        categoria_atual = self.categorizar_jogo_detalhado(
            ultimo_jogo['qtd_baixos'], ultimo_jogo['qtd_altos']
        )
        
        print(f"\n🎯 PREVISÃO PARA PRÓXIMO JOGO:")
        print(f"   Último jogo ({ultimo_jogo['concurso']}): {categoria_atual}")
        
        # Buscar padrões similares no histórico
        padroes_similares = self.buscar_padroes_similares(ultimos_10[-3:])
        
        if padroes_similares:
            print(f"   📊 Baseado em {len(padroes_similares)} padrões similares:")
            
            previsoes = []
            for padrao in padroes_similares:
                idx = padrao['indice']
                if idx + 1 < len(self.dados_historicos):
                    proximo = self.dados_historicos[idx + 1]
                    cat_proximo = self.categorizar_jogo_detalhado(
                        proximo['qtd_baixos'], proximo['qtd_altos']
                    )
                    previsoes.append(cat_proximo)
            
            if previsoes:
                contador_prev = Counter(previsoes)
                total_prev = len(previsoes)
                
                print(f"   🎲 Probabilidades para próximo jogo:")
                for cat, freq in contador_prev.most_common():
                    prob = (freq / total_prev) * 100
                    print(f"      • {cat}: {prob:.1f}% ({freq}/{total_prev})")
    
    def categorizar_jogo_detalhado(self, qtd_baixos, qtd_altos):
        """Categoriza um jogo de forma mais detalhada"""
        if qtd_baixos >= qtd_altos + 3:
            return "Muito mais baixos"
        elif qtd_baixos >= qtd_altos + 2:
            return "Mais baixos"
        elif qtd_altos >= qtd_baixos + 3:
            return "Muito mais altos"
        elif qtd_altos >= qtd_baixos + 2:
            return "Mais altos"
        elif qtd_baixos == qtd_altos + 1:
            return "Ligeiro desequilíbrio baixos"
        elif qtd_altos == qtd_baixos + 1:
            return "Ligeiro desequilíbrio altos"
        else:
            return "Equilibrio perfeito"
    
    def buscar_padroes_similares(self, sequencia_referencia):
        """Busca padrões similares no histórico"""
        padroes_encontrados = []
        tam_seq = len(sequencia_referencia)
        
        if tam_seq == 0:
            return padroes_encontrados
        
        # Converter sequência de referência para categorias
        cats_ref = []
        for dados in sequencia_referencia:
            cat = self.categorizar_jogo_detalhado(dados['qtd_baixos'], dados['qtd_altos'])
            cats_ref.append(cat)
        
        # Buscar no histórico
        for i in range(len(self.dados_historicos) - tam_seq + 1):
            cats_historico = []
            for j in range(tam_seq):
                dados = self.dados_historicos[i + j]
                cat = self.categorizar_jogo_detalhado(dados['qtd_baixos'], dados['qtd_altos'])
                cats_historico.append(cat)
            
            # Verificar similaridade
            if cats_historico == cats_ref:
                padroes_encontrados.append({
                    'indice': i + tam_seq - 1,  # Índice do último jogo do padrão
                    'sequencia': cats_historico,
                    'concursos': [self.dados_historicos[i + j]['concurso'] for j in range(tam_seq)]
                })
        
        return padroes_encontrados
    
    def gerar_relatorio_final(self):
        """Gera relatório final com insights e recomendações"""
        print("\n" + "="*70)
        print("📋 RELATÓRIO FINAL - INSIGHTS E RECOMENDAÇÕES")
        print("="*70)
        
        if not self.estatisticas:
            print("❌ Sem dados para relatório")
            return
        
        print("🎯 PRINCIPAIS INSIGHTS:")
        
        # Insight 1: Distribuição geral
        media_baixos = self.estatisticas['geral']['media_baixos']
        media_altos = self.estatisticas['geral']['media_altos']
        
        print(f"\n   1️⃣ EQUILÍBRIO NATURAL:")
        print(f"      • Média de baixos: {media_baixos:.2f} (esperado: 7.0)")
        print(f"      • Média de altos: {media_altos:.2f} (esperado: 7.0)")
        
        if abs(media_baixos - 7.0) < 0.1:
            print(f"      ✅ Distribuição praticamente perfeita!")
        elif media_baixos > media_altos:
            print(f"      📊 Ligeira tendência para números baixos")
        else:
            print(f"      📊 Ligeira tendência para números altos")
        
        # Insight 2: Padrões de transição
        print(f"\n   2️⃣ PADRÕES DE TRANSIÇÃO:")
        transicoes = self.estatisticas['transicoes']
        total = sum(transicoes.values())
        
        # Tendência de reversão
        reversoes = (transicoes.get('mais_baixos_para_mais_altos', 0) + 
                    transicoes.get('mais_altos_para_mais_baixos', 0))
        manutencoes = (transicoes.get('mais_baixos_para_mais_baixos', 0) + 
                      transicoes.get('mais_altos_para_mais_altos', 0))
        equilibrios = (transicoes.get('equilibrio_para_equilibrio', 0) +
                      transicoes.get('mais_baixos_para_equilibrio', 0) +
                      transicoes.get('mais_altos_para_equilibrio', 0) +
                      transicoes.get('equilibrio_para_mais_baixos', 0) +
                      transicoes.get('equilibrio_para_mais_altos', 0))
        
        if total > 0:
            perc_reversao = (reversoes / total) * 100
            perc_manutencao = (manutencoes / total) * 100
            perc_equilibrio = (equilibrios / total) * 100
            
            print(f"      • Reversões (baixo↔alto): {perc_reversao:.1f}%")
            print(f"      • Manutenções (mesmo padrão): {perc_manutencao:.1f}%")
            print(f"      • Movimentos via equilíbrio: {perc_equilibrio:.1f}%")
            
            if perc_reversao > perc_manutencao:
                print(f"      🔄 SISTEMA TENDE À REVERSÃO!")
            else:
                print(f"      📈 SISTEMA TENDE À CONTINUIDADE!")
        
        print(f"\n   3️⃣ RECOMENDAÇÕES ESTRATÉGICAS:")
        
        ultimo_jogo = self.dados_historicos[-1]
        cat_atual = self.categorizar_jogo_detalhado(
            ultimo_jogo['qtd_baixos'], ultimo_jogo['qtd_altos']
        )
        
        print(f"      • Situação atual: {cat_atual}")
        
        if "baixos" in cat_atual.lower():
            print(f"      🎯 ESTRATÉGIA: Considere mais números altos (14-25)")
            print(f"      📊 JUSTIFICATIVA: Histórico mostra tendência de reversão")
        elif "altos" in cat_atual.lower():
            print(f"      🎯 ESTRATÉGIA: Considere mais números baixos (2-13)")
            print(f"      📊 JUSTIFICATIVA: Histórico mostra tendência de reversão")
        else:
            print(f"      🎯 ESTRATÉGIA: Manter equilíbrio ou apostar em reversão")
            print(f"      📊 JUSTIFICATIVA: Posição neutra permite qualquer direção")
        
        print(f"\n   4️⃣ RANGE ÓTIMO RECOMENDADO:")
        dist_baixos = self.estatisticas['geral']['distribuicao_baixos']
        dist_altos = self.estatisticas['geral']['distribuicao_altos']
        
        # Encontrar faixas mais frequentes
        qtd_baixos_freq = dist_baixos.most_common(3)
        qtd_altos_freq = dist_altos.most_common(3)
        
        print(f"      • Números baixos (2-13): {qtd_baixos_freq[0][0]} a {qtd_baixos_freq[2][0]}")
        print(f"      • Números altos (14-25): {qtd_altos_freq[0][0]} a {qtd_altos_freq[2][0]}")
    
    def executar_analise_completa(self):
        """Executa a análise completa"""
        print("🎯 INICIANDO ANÁLISE DE DISTRIBUIÇÃO ALTOS/BAIXOS")
        print("="*70)
        
        if not self.carregar_dados_historicos():
            return False
        
        self.analisar_distribuicao_geral()
        self.analisar_tendencias_sequenciais()
        self.analisar_padroes_ciclicos()
        self.detectar_padroes_preditivos()
        self.gerar_relatorio_final()
        
        print("\n" + "="*70)
        print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("="*70)
        
        return True

def main():
    """Função principal"""
    analisador = AnalisadorDistribuicaoAltosBaixos()
    
    try:
        analisador.executar_analise_completa()
    except KeyboardInterrupt:
        print("\n❌ Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()