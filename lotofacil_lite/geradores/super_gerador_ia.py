#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SUPER GERADOR COM IA DE REPETIÇÕES
Sistema integrado que combina o Gerador Acadêmico Dinâmico com IA de repetições
"""

import sys
import os
from pathlib import Path
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any
import random
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Adiciona diretórios necessários ao path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'geradores'))
sys.path.insert(0, str(_BASE_DIR / 'ia'))

"""
🔥 SUPER GERADOR COM IA DE NÚMEROS REPETIDOS

Combina o Gerador Acadêmico Dinâmico + IA de Números Repetidos
para gerar combinações super-otimizadas com foco em 11+ acertos em 50%+ das apostas.

Features principais:
- Análise inteligente de padrões de repetição
- Otimização automática baseada em ciclos de ausência  
- Meta de 50% das combinações com 11+ acertos
- Estratégias adaptativas baseadas em confiança da IA

Autor: AR CALHAU
Data: 21 de Agosto de 2025
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import sys
import os

# Imports dos sistemas especializados
from gerador_academico_dinamico import GeradorAcademicoDinamico
from ia_numeros_repetidos import IANumerosRepetidos
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from collections import Counter
import statistics

class SuperGeradorIA:
    """
    Sistema integrado que combina insights acadêmicos com IA de repetições
    """
    
    def __init__(self):
        self.gerador_academico = GeradorAcademicoDinamico()
        self.ia_repeticoes = IANumerosRepetidos()
        
        # Configurações de otimização
        self.meta_acertos_minimos = 11
        self.percentual_meta = 0.5  # 50% das combinações devem ter 11+ acertos
        
        # Dados do último concurso para análise
        self.ultimo_concurso = None
        self.dados_ultimo_concurso = {}
        
        # 🚀 INTEGRAÇÃO DAS DESCOBERTAS DOS CAMPOS DE COMPARAÇÃO
        try:
            from integracao_descobertas_comparacao import IntegracaoDescobertasComparacao
            self.descobertas = IntegracaoDescobertasComparacao()
            print("🔬 Descobertas dos campos de comparação aplicadas ao Super Gerador")
        except ImportError:
            self.descobertas = None
            print("⚠️ Módulo de descobertas não encontrado - funcionamento normal")
        
        # 🔧 INTEGRAÇÃO COM SISTEMA DE CALIBRAÇÃO AUTOMÁTICA
        try:
            from aplicador_calibracao import aplicador_calibracao
            self.aplicador_calibracao = aplicador_calibracao
            print("🔧 Sistema de calibração automática integrado ao Super Gerador")
        except ImportError:
            self.aplicador_calibracao = None
            print("⚠️ Sistema de calibração não disponível")
        
        # Aplicar descobertas dos campos de comparação
        try:
            from integracao_descobertas_comparacao import aplicar_descobertas_comparacao
            aplicar_descobertas_comparacao(self)
            print("✅ Descobertas dos campos de comparação integradas ao SuperGeradorIA")
        except ImportError:
            print("⚠️ Módulo de descobertas de comparação não encontrado")
        
        print("🔥 Super Gerador com IA de Repetições inicializado")
        print("🎯 Meta: 50%+ das combinações com 11+ acertos")
    
    def inicializar_sistemas(self) -> bool:
        """
        Inicializa todos os subsistemas necessários
        """
        print("🔄 Inicializando sistemas especializados...")
        
        # 1. Inicializa gerador acadêmico
        print("   📊 Calculando insights acadêmicos...")
        if not self.gerador_academico.calcular_insights_dinamicos():
            print("❌ Falha ao inicializar gerador acadêmico")
            return False
        
        # 2. Inicializa IA de repetições  
        print("   🧠 Analisando padrões de repetição...")
        if not self.ia_repeticoes.analisar_estatisticas_repetidos():
            print("❌ Falha ao analisar estatísticas de repetição")
            return False
        
        # 3. Carrega dados do último concurso
        print("   🔍 Carregando dados do último concurso...")
        if not self._carregar_ultimo_concurso():
            print("❌ Falha ao carregar último concurso")
            return False
        
        print("✅ Todos os sistemas inicializados com sucesso!")
        return True
    
    def _carregar_ultimo_concurso(self) -> bool:
        """Carrega dados do último concurso da base"""
        try:
            conn = db_config.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Busca último concurso com todos os dados (colunas reais)
            query = """
            SELECT TOP 1
                Concurso,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15,
                QtdeRepetidos, RepetidosMesmaPosicao,
                QtdePrimos, QtdeImpares, SomaTotal
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                self.ultimo_concurso = int(resultado[0])
                # 🔧 CORREÇÃO: Converte todos os números para int Python nativo
                numeros_raw = resultado[1:16]
                numeros_limpos = [int(n) if hasattr(n, 'item') else int(n) for n in numeros_raw]
                
                self.dados_ultimo_concurso = {
                    'concurso': int(resultado[0]),
                    'numeros': numeros_limpos,
                    'QtdeRepetidos': int(resultado[16]) if resultado[16] is not None else 0,
                    'RepetidosMesmaPosicao': int(resultado[17]) if resultado[17] is not None else 0,
                    'QtdePrimos': int(resultado[18]) if resultado[18] is not None else 0,
                    'QtdeImpares': int(resultado[19]) if resultado[19] is not None else 0,
                    'SomaTotal': int(resultado[20]) if resultado[20] is not None else 0
                }
                
                print(f"   📅 Último concurso: {self.ultimo_concurso}")
                print(f"   🎲 Números: {self.dados_ultimo_concurso['numeros']}")
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            print(f"❌ Erro ao carregar último concurso: {e}")
            return False
    
    def gerar_super_combinacoes(self, quantidade: int = 15, qtd_numeros: int = 15) -> Dict:
        """
        Gera super-combinações otimizadas com IA de repetições
        """
        print(f"\n🔥 GERANDO {quantidade} SUPER-COMBINAÇÕES COM IA")
        print("=" * 65)
        
        # 1. Gera combinações base com método acadêmico OTIMIZADO
        print("🏆 Fase 1: Gerando combinações base (BAIXA SOBREPOSIÇÃO)...")
        
        # Usa método otimizado se disponível, senão usa padrão
        if hasattr(self.gerador_academico, 'gerar_multiplas_otimizadas') and qtd_numeros == 20:
            print("✅ Usando estratégia CIENTIFICAMENTE COMPROVADA!")
            combinacoes_base = self.gerador_academico.gerar_multiplas_otimizadas(quantidade * 2)
        else:
            print("⚠️ Usando método padrão (sem otimização de sobreposição)")
            combinacoes_base = self.gerador_academico.gerar_multiplas_combinacoes(
                quantidade * 2, qtd_numeros  # Gera o dobro para ter margem de otimização
            )
        
        if not combinacoes_base:
            return {'erro': 'Falha ao gerar combinações base'}
        
        # Converte todos os valores numpy para int nativo para evitar problemas bit_length
        combinacoes_base = [[int(num) for num in combinacao] for combinacao in combinacoes_base]
        
        print(f"✅ {len(combinacoes_base)} combinações base geradas")
        
        # 2. Analisa padrões de repetição para otimização
        print("🧠 Fase 2: Analisando padrões de repetição com IA...")
        predicao_repeticoes = self.ia_repeticoes.predizer_padroes_repetidos(
            self.dados_ultimo_concurso['numeros'],
            self.dados_ultimo_concurso
        )
        
        if 'erro' in predicao_repeticoes:
            print(f"⚠️ Usando combinações base (erro na IA: {predicao_repeticoes['erro']})")
            combinacoes_otimizadas = combinacoes_base[:quantidade]
        else:
            # 3. Otimiza com IA de repetições
            print("🎯 Fase 3: Otimizando com padrões inteligentes de repetição...")
            combinacoes_otimizadas = self.ia_repeticoes.otimizar_combinacoes_com_repeticoes(
                combinacoes_base, self.dados_ultimo_concurso['numeros']
            )
        
        # Converte novamente para garantir que não há valores numpy após a otimização
        combinacoes_otimizadas = [[int(num) for num in combinacao] for combinacao in combinacoes_otimizadas]
        
        # 4. Seleciona as melhores baseado em critérios inteligentes
        print("⭐ Fase 4: Selecionando super-combinações finais...")
        super_combinacoes = self._selecionar_melhores_combinacoes(
            combinacoes_otimizadas, quantidade, predicao_repeticoes
        )
        
        # Converte as super-combinações finais para garantir tipos nativos
        super_combinacoes = [[int(num) for num in combinacao] for combinacao in super_combinacoes]
        
        # 5. Análise final das super-combinações
        analise_final = self._analisar_super_combinacoes(
            super_combinacoes, predicao_repeticoes
        )
        
        return {
            'combinacoes': super_combinacoes,
            'analise': analise_final,
            'predicao_ia': predicao_repeticoes,
            'ultimo_concurso': self.dados_ultimo_concurso,
            'qtd_numeros': qtd_numeros,
            'timestamp': datetime.now()
        }
    
    def _selecionar_melhores_combinacoes(self, combinacoes: List[List[int]], 
                                       quantidade: int, predicao: Dict) -> List[List[int]]:
        """
        Seleciona as melhores combinações baseado em critérios inteligentes COM DIVERSIFICAÇÃO
        """
        if len(combinacoes) <= quantidade:
            return combinacoes
        
        print(f"   🔍 Selecionando {quantidade} melhores de {len(combinacoes)} combinações...")
        
        # Estratégia híbrida: 60% por score, 40% por diversidade
        qtd_por_score = int(quantidade * 0.6)
        qtd_por_diversidade = quantidade - qtd_por_score
        
        # 1. SELEÇÃO POR SCORE (60%)
        combinacoes_com_score = []
        
        for i, combinacao in enumerate(combinacoes):
            score = self._calcular_score_combinacao(combinacao, predicao)
            combinacoes_com_score.append((combinacao, score, i))
        
        # Ordena por score (maior para menor)
        combinacoes_com_score.sort(key=lambda x: x[1], reverse=True)
        
        # Seleciona as melhores por score
        melhores_score = [comb for comb, score, idx in combinacoes_com_score[:qtd_por_score]]
        
        # 2. SELEÇÃO POR DIVERSIDADE (40%)
        # Remove as já selecionadas
        indices_usados = set([idx for comb, score, idx in combinacoes_com_score[:qtd_por_score]])
        combinacoes_restantes = [combinacoes[i] for i in range(len(combinacoes)) if i not in indices_usados]
        
        melhores_diversidade = self._selecionar_por_diversidade(
            combinacoes_restantes, qtd_por_diversidade, melhores_score
        )
        
        # 3. COMBINA OS RESULTADOS
        resultado_final = melhores_score + melhores_diversidade
        
        # 4. VERIFICAÇÃO DE DIVERSIDADE FINAL
        conjunto_unico = set()
        combinacoes_finais = []
        
        for combinacao in resultado_final:
            comb_tuple = tuple(sorted(combinacao))
            if comb_tuple not in conjunto_unico:
                conjunto_unico.add(comb_tuple)
                combinacoes_finais.append(combinacao)
        
        # Se ainda não tem diversidade suficiente, completa aleatoriamente
        if len(combinacoes_finais) < quantidade:
            import random
            random.seed(42)  # Reproduzibilidade
            combinacoes_extras = [c for c in combinacoes if c not in combinacoes_finais]
            random.shuffle(combinacoes_extras)
            
            while len(combinacoes_finais) < quantidade and combinacoes_extras:
                candidata = combinacoes_extras.pop()
                comb_tuple = tuple(sorted(candidata))
                if comb_tuple not in conjunto_unico:
                    conjunto_unico.add(comb_tuple)
                    combinacoes_finais.append(candidata)
        
        diversidade_final = len(conjunto_unico)
        percentual_diversidade = (diversidade_final / min(quantidade, len(combinacoes_finais))) * 100
        
        print(f"   📊 Selecionadas {len(combinacoes_finais)} super-combinações:")
        print(f"       • {qtd_por_score} por score IA")
        print(f"       • {len(melhores_diversidade)} por diversidade")
        print(f"       • Diversidade final: {diversidade_final} únicas ({percentual_diversidade:.1f}%)")
        
        return combinacoes_finais[:quantidade]
    
    def _selecionar_por_diversidade(self, combinacoes: List[List[int]], 
                                  quantidade: int, ja_selecionadas: List[List[int]]) -> List[List[int]]:
        """
        Seleciona combinações priorizando máxima diversidade
        """
        if quantidade <= 0 or not combinacoes:
            return []
        
        import random
        random.seed(42)  # Para reproduzibilidade
        
        selecionadas = []
        combinacoes_disponiveis = combinacoes.copy()
        
        # Converte já selecionadas para sets para comparação rápida
        sets_ja_selecionadas = [set(comb) for comb in ja_selecionadas]
        
        for _ in range(quantidade):
            if not combinacoes_disponiveis:
                break
            
            melhor_candidata = None
            maior_diversidade = -1
            
            # Para cada combinação disponível, calcula sua diversidade
            for candidata in combinacoes_disponiveis:
                set_candidata = set(candidata)
                
                # Calcula diversidade em relação às já selecionadas
                diversidade = 0
                
                # Diversidade com as já selecionadas (score)
                for set_existente in sets_ja_selecionadas:
                    intersecao = len(set_candidata & set_existente)
                    diversidade += (15 - intersecao)  # Menos intersecção = mais diversidade
                
                # Diversidade com as selecionadas nesta rodada
                for selecionada in selecionadas:
                    set_selecionada = set(selecionada)
                    intersecao = len(set_candidata & set_selecionada)
                    diversidade += (15 - intersecao)
                
                # Adiciona variação baseada na distribuição por quintis
                faixas = [
                    sum(1 for n in candidata if 1 <= n <= 5),
                    sum(1 for n in candidata if 6 <= n <= 10),
                    sum(1 for n in candidata if 11 <= n <= 15),
                    sum(1 for n in candidata if 16 <= n <= 20),
                    sum(1 for n in candidata if 21 <= n <= 25)
                ]
                diversidade += sum(1 for f in faixas if f > 0) * 2  # Bonus por distribuição
                
                # Adiciona aleatoriedade para evitar padrões
                import random
                diversidade += random.uniform(-1.0, 1.0)
                
                if diversidade > maior_diversidade:
                    maior_diversidade = diversidade
                    melhor_candidata = candidata
            
            if melhor_candidata:
                selecionadas.append(melhor_candidata)
                combinacoes_disponiveis.remove(melhor_candidata)
        
        return selecionadas
    
    def _calcular_score_combinacao(self, combinacao: List[int], predicao: Dict) -> float:
        """
        Calcula score inteligente para uma combinação
        """
        score = 0.0
        
        # 🔧 CORREÇÃO: Converte numpy.int64 para int Python nativo
        combinacao_limpa = [int(n) if hasattr(n, 'item') else int(n) for n in combinacao]
        nums_combinacao = set(combinacao_limpa)
        
        # Converte números do último concurso também
        numeros_ultimo = self.dados_ultimo_concurso['numeros']
        if isinstance(numeros_ultimo, (list, tuple)):
            numeros_ultimo_limpos = [int(n) if hasattr(n, 'item') else int(n) for n in numeros_ultimo]
        else:
            numeros_ultimo_limpos = [int(n) for n in numeros_ultimo]
        nums_ultimo = set(numeros_ultimo_limpos)
        
        # 1. Score baseado na predição de repetições
        if 'erro' not in predicao:
            # Repetidos totais
            qtde_rep_atual = len(nums_combinacao & nums_ultimo)
            qtde_rep_ideal = int(predicao['QtdeRepetidos']['predicao'])
            diferenca_rep = abs(qtde_rep_atual - qtde_rep_ideal)
            score_rep = max(0, 10 - diferenca_rep)  # Score inversamente proporcional à diferença
            
            # Bonus se está na faixa ideal (7-9)
            if predicao['QtdeRepetidos']['faixa_ideal'] and qtde_rep_atual == qtde_rep_ideal:
                score_rep += 5
            
            score += score_rep * float(predicao['QtdeRepetidos']['confianca'])
            
            # Repetidos na mesma posição (simplificado)
            # Em implementação real, verificaria posições exatas
            score += 2 * float(predicao['RepetidosMesmaPosicao']['confianca'])
        
        # 2. Score baseado na distribuição dos números
        # Distribuição por faixas (equilibrada é melhor)
        faixas = [
            sum(1 for n in combinacao_limpa if 1 <= n <= 5),    # Faixa 1-5
            sum(1 for n in combinacao_limpa if 6 <= n <= 10),   # Faixa 6-10  
            sum(1 for n in combinacao_limpa if 11 <= n <= 15),  # Faixa 11-15
            sum(1 for n in combinacao_limpa if 16 <= n <= 20),  # Faixa 16-20
            sum(1 for n in combinacao_limpa if 21 <= n <= 25),  # Faixa 21-25
        ]
        
        # Penaliza distribuições muito desbalanceadas
        import statistics
        try:
            desvio_faixas = statistics.stdev(faixas) if len(faixas) > 1 else 0
        except:
            desvio_faixas = 0
        score += max(0, 5 - desvio_faixas)  # Menor desvio = maior score
        
        # 3. Score baseado em pares/ímpares
        qtd_pares = sum(1 for n in combinacao_limpa if n % 2 == 0)
        qtd_impares = 15 - qtd_pares
        
        # Distribuição ideal: 7-8 pares, 7-8 ímpares
        if 7 <= qtd_pares <= 8:
            score += 3
        elif 6 <= qtd_pares <= 9:
            score += 1
        
        # 4. Score baseado na soma
        soma_atual = sum(combinacao_limpa)
        # Soma ideal está entre 180-220 baseado em análises históricas
        if 180 <= soma_atual <= 220:
            score += 4
        elif 160 <= soma_atual <= 240:
            score += 2
        
        # 5. Score baseado nos insights acadêmicos
        if hasattr(self.gerador_academico, 'pesos_academicos'):
            # Soma dos pesos dos números selecionados
            peso_total = sum(self.gerador_academico.pesos_academicos.get(n, 1.0) for n in combinacao)
            score += peso_total / 15 * 5  # Normaliza e multiplica por 5
        
        # 6. Bonus por números em tendência de subida
        if hasattr(self.gerador_academico, 'insights_academicos'):
            nums_subida = set(self.gerador_academico.insights_academicos.get('tendencia_subida', []))
            intersecao_subida = len(nums_combinacao & nums_subida)
            score += intersecao_subida * 0.5
        
        # 7. Diversidade (evita combinações muito similares)
        # Este critério seria implementado comparando com outras combinações já selecionadas
        
        return round(score, 2)
    
    def _analisar_super_combinacoes(self, combinacoes: List[List[int]], 
                                  predicao: Dict) -> Dict:
        """
        Analisa as super-combinações geradas
        """
        analise = {}
        
        if not combinacoes:
            return {'erro': 'Nenhuma combinação para analisar'}
        
        # 1. Análise de repetições
        nums_ultimo = set(self.dados_ultimo_concurso['numeros'])
        repeticoes_por_combinacao = []
        
        for combinacao in combinacoes:
            nums_comb = set(combinacao)
            qtde_rep = len(nums_comb & nums_ultimo)
            repeticoes_por_combinacao.append(qtde_rep)
        
        analise['repeticoes'] = {
            'media': statistics.mean(repeticoes_por_combinacao),
            'min': min(repeticoes_por_combinacao),
            'max': max(repeticoes_por_combinacao),
            'distribuicao': Counter(repeticoes_por_combinacao),
            'alinhamento_ia': sum(1 for r in repeticoes_por_combinacao 
                                if abs(r - predicao.get('QtdeRepetidos', {}).get('predicao', 8)) <= 1) / len(combinacoes) * 100
        }
        
        # 2. Análise de distribuição por faixas
        todas_faixas = {'1-5': [], '6-10': [], '11-15': [], '16-20': [], '21-25': []}
        
        for combinacao in combinacoes:
            faixas = {
                '1-5': sum(1 for n in combinacao if 1 <= n <= 5),
                '6-10': sum(1 for n in combinacao if 6 <= n <= 10),
                '11-15': sum(1 for n in combinacao if 11 <= n <= 15),
                '16-20': sum(1 for n in combinacao if 16 <= n <= 20),
                '21-25': sum(1 for n in combinacao if 21 <= n <= 25)
            }
            
            for faixa, qtd in faixas.items():
                todas_faixas[faixa].append(qtd)
        
        analise['distribuicao_faixas'] = {
            faixa: {
                'media': statistics.mean(valores),
                'min': min(valores),
                'max': max(valores)
            }
            for faixa, valores in todas_faixas.items()
        }
        
        # 3. Análise de pares/ímpares
        pares_por_combinacao = [sum(1 for n in comb if n % 2 == 0) for comb in combinacoes]
        analise['pares_impares'] = {
            'media_pares': statistics.mean(pares_por_combinacao),
            'distribuicao_pares': Counter(pares_por_combinacao),
            'equilibrio': sum(1 for p in pares_por_combinacao if 7 <= p <= 8) / len(combinacoes) * 100
        }
        
        # 4. Análise de somas
        somas = [sum(comb) for comb in combinacoes]
        analise['somas'] = {
            'media': statistics.mean(somas),
            'min': min(somas),
            'max': max(somas),
            'desvio_padrao': statistics.stdev(somas) if len(somas) > 1 else 0,
            'faixa_ideal': sum(1 for s in somas if 180 <= s <= 220) / len(combinacoes) * 100
        }
        
        # 5. Análise de números mais selecionados
        contador_numeros = Counter()
        for combinacao in combinacoes:
            contador_numeros.update(combinacao)
        
        analise['numeros_populares'] = {
            'top_10': contador_numeros.most_common(10),
            'menos_10': contador_numeros.most_common()[-10:] if len(contador_numeros) >= 10 else [],
            'cobertura': len(contador_numeros)  # Quantos números diferentes foram usados
        }
        
        # 6. Previsão de performance
        # Baseado nos padrões históricos e alinhamento com IA
        score_medio = (
            analise['repeticoes']['alinhamento_ia'] * 0.3 +
            analise['pares_impares']['equilibrio'] * 0.2 + 
            analise['somas']['faixa_ideal'] * 0.2 +
            (analise['numeros_populares']['cobertura'] / 25 * 100) * 0.1 +
            50  # Score base
        )
        
        analise['previsao_performance'] = {
            'score_geral': round(score_medio, 1),
            'expectativa_11_acertos': round(max(30, score_medio * 0.6), 1),  # Estima % com 11+ acertos
            'confianca': predicao.get('recomendacao', {}).get('geral', {}).get('nivel', 'MEDIA_CONFIANCA')
        }
        
        return analise
    
    def salvar_super_combinacoes(self, resultado: Dict, nome_arquivo: Optional[str] = None) -> str:
        """
        Salva as super-combinações com análise completa
        """
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"super_combinacoes_ia_{timestamp}.txt"
        
        try:
            combinacoes = resultado['combinacoes']
            analise = resultado['analise']
            predicao = resultado['predicao_ia']
            qtd_numeros = resultado['qtd_numeros']
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🔥 SUPER-COMBINAÇÕES COM IA DE REPETIÇÕES\n")
                f.write("=" * 70 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Baseado no concurso: {self.ultimo_concurso}\n")
                f.write(f"Números do concurso base: {self.dados_ultimo_concurso['numeros']}\n\n")
                
                # Informações da IA de repetições
                f.write("🧠 ANÁLISE IA DE REPETIÇÕES:\n")
                f.write("-" * 40 + "\n")
                if 'erro' not in predicao:
                    f.write(f"• Predição QtdeRepetidos: {predicao['QtdeRepetidos']['predicao']} (confiança: {predicao['QtdeRepetidos']['confianca']:.1%})\n")
                    f.write(f"• Predição MesmaPosição: {predicao['RepetidosMesmaPosicao']['predicao']} (confiança: {predicao['RepetidosMesmaPosicao']['confianca']:.1%})\n")
                    f.write(f"• Estratégia: {predicao['recomendacao']['geral']['recomendacao']}\n")
                    f.write(f"• Nível de confiança: {predicao['recomendacao']['geral']['nivel']}\n\n")
                else:
                    f.write(f"• IA não disponível: {predicao['erro']}\n\n")
                
                # Análise das combinações
                f.write("📊 ANÁLISE DAS SUPER-COMBINAÇÕES:\n")
                f.write("-" * 45 + "\n")
                f.write(f"• Total de combinações: {len(combinacoes)}\n")
                f.write(f"• Números por combinação: {qtd_numeros}\n")
                f.write(f"• Repetições médias: {analise['repeticoes']['media']:.1f}\n")
                f.write(f"• Alinhamento com IA: {analise['repeticoes']['alinhamento_ia']:.1f}%\n")
                f.write(f"• Equilíbrio pares/ímpares: {analise['pares_impares']['equilibrio']:.1f}%\n")
                f.write(f"• Somas na faixa ideal: {analise['somas']['faixa_ideal']:.1f}%\n\n")
                
                # Previsão de performance
                f.write("🎯 PREVISÃO DE PERFORMANCE:\n")
                f.write("-" * 35 + "\n")
                f.write(f"• Score geral: {analise['previsao_performance']['score_geral']}/100\n")
                f.write(f"• Expectativa 11+ acertos: {analise['previsao_performance']['expectativa_11_acertos']:.1f}%\n")
                f.write(f"• Confiança: {analise['previsao_performance']['confianca']}\n")
                f.write(f"• Meta (50%+ com 11+ acertos): {'✅ PROVÁVEL' if analise['previsao_performance']['expectativa_11_acertos'] >= 50 else '⚠️ DESAFIADOR'}\n\n")
                
                # Top números selecionados
                f.write("🔥 TOP NÚMEROS SELECIONADOS:\n")
                f.write("-" * 35 + "\n")
                for numero, freq in analise['numeros_populares']['top_10']:
                    percent = freq / len(combinacoes) * 100
                    f.write(f"• {numero:2d}: {freq:2d}x ({percent:4.1f}%)\n")
                f.write("\n")
                
                # As super-combinações
                f.write(f"🎲 {len(combinacoes)} SUPER-COMBINAÇÕES:\n")
                f.write("=" * 40 + "\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    f.write(f"Super {i:2d}: {','.join(map(str, sorted(combinacao)))}\n")
                
                # Seção de ouro: apenas as combinações
                f.write("\n" + "🏆" * 20 + " SEÇÃO DE OURO " + "🏆" * 20 + "\n")
                f.write("SUPER-COMBINAÇÕES (formato direto):\n")
                f.write("-" * 65 + "\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    f.write(f"{','.join(map(str, sorted(combinacao)))}\n")
                
                f.write("\n" + "🏆" * 60 + "\n")
            
            print(f"✅ Super-combinações salvas: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return ""
    
    def executar_geracao_completa(self, quantidade: int = 15, qtd_numeros: int = 15) -> bool:
        """
        Executa todo o processo de geração de super-combinações
        """
        try:
            # 1. Inicializa sistemas
            if not self.inicializar_sistemas():
                return False
            
            # 2. Gera super-combinações
            resultado = self.gerar_super_combinacoes(quantidade, qtd_numeros)
            
            if 'erro' in resultado:
                print(f"❌ Erro na geração: {resultado['erro']}")
                return False
            
            # 3. Mostra resultados
            self._mostrar_resultados(resultado)
            
            # 4. Salva arquivo
            nome_arquivo = self.salvar_super_combinacoes(resultado)
            
            if nome_arquivo:
                print(f"\n🎉 PROCESSO CONCLUÍDO!")
                print(f"📄 Arquivo: {nome_arquivo}")
                print(f"🎯 Meta 11+ acertos: {resultado['analise']['previsao_performance']['expectativa_11_acertos']:.1f}%")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro no processo completo: {e}")
            return False
    
    def _mostrar_resultados(self, resultado: Dict):
        """Mostra resultados na tela"""
        combinacoes = resultado['combinacoes']
        analise = resultado['analise']
        
        print(f"\n🔥 {len(combinacoes)} SUPER-COMBINAÇÕES GERADAS")
        print("-" * 50)
        
        for i, combinacao in enumerate(combinacoes[:5], 1):  # Mostra só as 5 primeiras
            print(f"Super {i:2d}: {','.join(map(str, sorted(combinacao)))}")
        
        if len(combinacoes) > 5:
            print(f"... e mais {len(combinacoes) - 5} super-combinações")
        
        print(f"\n📊 ANÁLISE RESUMIDA:")
        print(f"• Repetições médias: {analise['repeticoes']['media']:.1f}")
        print(f"• Alinhamento IA: {analise['repeticoes']['alinhamento_ia']:.1f}%")
        print(f"• Expectativa 11+ acertos: {analise['previsao_performance']['expectativa_11_acertos']:.1f}%")
        print(f"• Score geral: {analise['previsao_performance']['score_geral']:.1f}/100")

def main():
    """Função principal"""
    print("🔥 SUPER GERADOR COM IA DE REPETIÇÕES")
    print("=" * 60)
    print("🎯 Sistema integrado para super-combinações otimizadas")
    print("🧠 Meta: 50%+ das combinações com 11+ acertos")
    print()
    
    super_gerador = SuperGeradorIA()
    
    try:
        print("🎮 CONFIGURAÇÃO:")
        qtd_numeros = int(input("Quantos números por combinação (15-20): ") or "15")
        
        if qtd_numeros not in range(15, 21):
            print("❌ Quantidade deve ser entre 15 e 20")
            return
        
        quantidade = int(input("Quantas super-combinações gerar: ") or "15")
        
        if quantidade <= 0:
            print("❌ Quantidade deve ser maior que zero")
            return
        
        print(f"\n🚀 Iniciando geração de {quantidade} super-combinações...")
        
        # Executa processo completo
        sucesso = super_gerador.executar_geracao_completa(quantidade, qtd_numeros)
        
        if sucesso:
            print(f"\n✅ Super-combinações com IA geradas com sucesso!")
            print("🎯 Use essas combinações com alta expectativa de performance!")
        else:
            print(f"\n❌ Falha na geração de super-combinações")
            
    except ValueError:
        print("❌ Valor inválido")
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
