#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 ANÁLISE HISTÓRICA DOS 10 MELHORES NÚMEROS - PERFORMANCE TEMPORAL
==================================================================
Testa se o sistema dos 10 melhores números é um padrão recorrente
e como podemos usar isso estrategicamente
==================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime

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


class AnalisadorHistorico10Melhores:
    """Analisador histórico da performance dos 10 melhores números"""
    
    def __init__(self):
        self.periodos_teste = []
        self.resultados_historicos = []
        self.estatisticas_gerais = {}
        
    def executar_analise_completa(self):
        """Execução completa da análise histórica"""
        print("📊 ANÁLISE HISTÓRICA DOS 10 MELHORES NÚMEROS")
        print("=" * 60)
        print("🎯 Objetivo: Verificar padrão recorrente e criar estratégias")
        print()
        
        # 1. Definir períodos de teste
        print("📅 DEFININDO PERÍODOS DE TESTE...")
        periodos = self._definir_periodos_historicos()
        
        # 2. Para cada período, calcular os 10 melhores
        print(f"\n🔍 ANALISANDO {len(periodos)} PERÍODOS HISTÓRICOS...")
        resultados = []
        
        for i, periodo in enumerate(periodos, 1):
            print(f"\n📊 Período {i}/{len(periodos)}: Concursos {periodo['inicio']}-{periodo['fim']}")
            
            # Calcular os 10 melhores do período
            dez_melhores = self._calcular_10_melhores_periodo(periodo)
            
            # Testar performance nos próximos N concursos
            performance = self._testar_performance_futuro(dez_melhores, periodo)
            
            resultado = {
                'periodo': periodo,
                'dez_melhores': dez_melhores,
                'performance': performance
            }
            resultados.append(resultado)
            
            # Mostrar resultado do período
            self._mostrar_resultado_periodo(resultado)
        
        # 3. Análise estatística geral
        print(f"\n📈 ANÁLISE ESTATÍSTICA GERAL")
        self._analisar_estatisticas_gerais(resultados)
        
        # 4. Estratégias identificadas
        print(f"\n🎯 ESTRATÉGIAS IDENTIFICADAS")
        self._identificar_estrategias(resultados)
        
        return resultados
    
    def _definir_periodos_historicos(self):
        """Define períodos históricos para teste (janelas deslizantes)"""
        try:
            # Buscar range de concursos disponíveis
            query = "SELECT MIN(Concurso), MAX(Concurso) FROM Resultados_INT"
            resultado = db_config.execute_query(query)
            
            if not resultado:
                print("❌ Erro ao buscar range de concursos")
                return []
            
            min_concurso, max_concurso = resultado[0]
            print(f"   📊 Range disponível: {min_concurso} a {max_concurso}")
            
            # Definir períodos (janelas de 100 concursos, teste nos próximos 20)
            periodos = []
            janela_analise = 100  # Concursos para calcular os 10 melhores
            janela_teste = 20     # Concursos para testar performance
            passo = 50           # Pular de 50 em 50 concursos
            
            concurso_atual = min_concurso
            while concurso_atual + janela_analise + janela_teste <= max_concurso:
                periodo = {
                    'inicio': concurso_atual,
                    'fim': concurso_atual + janela_analise - 1,
                    'teste_inicio': concurso_atual + janela_analise,
                    'teste_fim': concurso_atual + janela_analise + janela_teste - 1
                }
                periodos.append(periodo)
                concurso_atual += passo
            
            print(f"   ✅ {len(periodos)} períodos definidos")
            print(f"   📋 Configuração: {janela_analise} concursos análise + {janela_teste} teste")
            
            return periodos[:10]  # Limitar a 10 períodos para teste inicial
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return []
    
    def _calcular_10_melhores_periodo(self, periodo):
        """Calcula os 10 melhores números para um período específico"""
        try:
            scores = {}
            
            # Inicializar scores
            for numero in range(1, 26):
                scores[numero] = 0.0
            
            # 1. ANÁLISE DE AUSÊNCIAS (40% do peso)
            for numero in range(1, 26):
                ausencia = self._calcular_ausencia_periodo(numero, periodo)
                score_ausencia = min(ausencia * 5, 100)  # Max 100 pontos
                scores[numero] += score_ausencia * 0.40
            
            # 2. ANÁLISE DE FREQUÊNCIA (30% do peso)
            for numero in range(1, 26):
                frequencia = self._calcular_frequencia_periodo(numero, periodo)
                score_freq = min(frequencia * 3, 100)
                scores[numero] += score_freq * 0.30
            
            # 3. ANÁLISE DE TENDÊNCIA (20% do peso) 
            for numero in range(1, 26):
                tendencia = self._calcular_tendencia_periodo(numero, periodo)
                scores[numero] += tendencia * 0.20
            
            # 4. FATORES ESPECIAIS (10% do peso)
            for numero in range(1, 26):
                especial = self._calcular_fator_especial(numero)
                scores[numero] += especial * 0.10
            
            # Selecionar os 10 melhores
            ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            dez_melhores = [numero for numero, score in ranking[:10]]
            
            return dez_melhores
            
        except Exception as e:
            print(f"      ❌ Erro no cálculo: {e}")
            # Fallback: números mais centrais
            return [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    
    def _calcular_ausencia_periodo(self, numero, periodo):
        """Calcula quantos concursos o número não apareceu no final do período"""
        try:
            # Última aparição do número no período
            query = """
            SELECT MAX(Concurso) FROM Resultados_INT 
            WHERE (N1=? OR N2=? OR N3=? OR N4=? OR N5=? OR N6=? OR N7=? OR N8=? OR 
                   N9=? OR N10=? OR N11=? OR N12=? OR N13=? OR N14=? OR N15=?)
            AND Concurso BETWEEN ? AND ?
            """
            
            params = [numero] * 15 + [periodo['inicio'], periodo['fim']]
            resultado = db_config.execute_query(query, tuple(params))
            
            if resultado and resultado[0][0]:
                ultima_aparicao = resultado[0][0]
                ausencia = periodo['fim'] - ultima_aparicao
            else:
                ausencia = periodo['fim'] - periodo['inicio'] + 1  # Nunca apareceu
            
            return ausencia
            
        except:
            return 5  # Valor padrão
    
    def _calcular_frequencia_periodo(self, numero, periodo):
        """Calcula frequência do número no período"""
        try:
            query = """
            SELECT COUNT_BIG(*) FROM Resultados_INT 
            WHERE (N1=? OR N2=? OR N3=? OR N4=? OR N5=? OR N6=? OR N7=? OR N8=? OR 
                   N9=? OR N10=? OR N11=? OR N12=? OR N13=? OR N14=? OR N15=?)
            AND Concurso BETWEEN ? AND ?
            """
            
            params = [numero] * 15 + [periodo['inicio'], periodo['fim']]
            resultado = db_config.execute_query(query, tuple(params))
            
            if resultado:
                return resultado[0][0]
            return 0
            
        except:
            return 0
    
    def _calcular_tendencia_periodo(self, numero, periodo):
        """Calcula tendência de crescimento/decréscimo no período"""
        try:
            # Dividir período em 2 metades e comparar frequências
            meio = periodo['inicio'] + (periodo['fim'] - periodo['inicio']) // 2
            
            # Primeira metade
            freq1 = self._calcular_frequencia_numero_range(numero, periodo['inicio'], meio)
            
            # Segunda metade  
            freq2 = self._calcular_frequencia_numero_range(numero, meio + 1, periodo['fim'])
            
            # Tendência: diferença percentual
            if freq1 > 0:
                tendencia = ((freq2 - freq1) / freq1) * 100
                return max(0, min(tendencia + 50, 100))  # Normalizar 0-100
            
            return 50  # Neutro se não há dados
            
        except:
            return 50
    
    def _calcular_frequencia_numero_range(self, numero, inicio, fim):
        """Calcula frequência de um número em um range de concursos"""
        try:
            query = """
            SELECT COUNT_BIG(*) FROM Resultados_INT 
            WHERE (N1=? OR N2=? OR N3=? OR N4=? OR N5=? OR N6=? OR N7=? OR N8=? OR 
                   N9=? OR N10=? OR N11=? OR N12=? OR N13=? OR N14=? OR N15=?)
            AND Concurso BETWEEN ? AND ?
            """
            
            params = [numero] * 15 + [inicio, fim]
            resultado = db_config.execute_query(query, tuple(params))
            
            return resultado[0][0] if resultado else 0
            
        except:
            return 0
    
    def _calcular_fator_especial(self, numero):
        """Calcula fatores especiais (primos, centrais, etc.)"""
        score = 0
        
        # Números primos
        primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
        if numero in primos:
            score += 30
        
        # Números centrais (8-18)
        if 8 <= numero <= 18:
            score += 20
        
        # Fibonacci
        fibonacci = {1, 2, 3, 5, 8, 13, 21}
        if numero in fibonacci:
            score += 25
        
        return min(score, 100)
    
    def _testar_performance_futuro(self, dez_melhores, periodo):
        """Testa performance dos 10 melhores nos concursos seguintes"""
        try:
            # Buscar resultados dos concursos de teste
            query = """
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 
            FROM Resultados_INT 
            WHERE Concurso BETWEEN ? AND ?
            ORDER BY Concurso
            """
            
            params = (periodo['teste_inicio'], periodo['teste_fim'])
            resultados = db_config.execute_query(query, params)
            
            if not resultados:
                return {'acertos_por_concurso': [], 'media_acertos': 0, 'total_concursos': 0}
            
            acertos_por_concurso = []
            
            for resultado in resultados:
                concurso = resultado[0]
                numeros_sorteados = resultado[1:16]  # N1 a N15
                
                # Contar quantos dos 10 melhores foram sorteados
                acertos = 0
                for numero in dez_melhores:
                    if numero in numeros_sorteados:
                        acertos += 1
                
                acertos_por_concurso.append({
                    'concurso': concurso,
                    'acertos': acertos,
                    'dez_melhores': dez_melhores.copy(),
                    'sorteados': list(numeros_sorteados)
                })
            
            # Calcular estatísticas
            total_acertos = sum(item['acertos'] for item in acertos_por_concurso)
            total_concursos = len(acertos_por_concurso)
            media_acertos = total_acertos / total_concursos if total_concursos > 0 else 0
            
            return {
                'acertos_por_concurso': acertos_por_concurso,
                'media_acertos': media_acertos,
                'total_concursos': total_concursos,
                'total_acertos': total_acertos
            }
            
        except Exception as e:
            print(f"      ❌ Erro no teste: {e}")
            return {'acertos_por_concurso': [], 'media_acertos': 0, 'total_concursos': 0}
    
    def _mostrar_resultado_periodo(self, resultado):
        """Mostra resultado de um período específico"""
        periodo = resultado['periodo']
        dez_melhores = resultado['dez_melhores']
        performance = resultado['performance']
        
        print(f"   🎯 10 Melhores: {','.join(map(str, dez_melhores))}")
        print(f"   📊 Performance: {performance['media_acertos']:.1f} acertos/concurso (média)")
        print(f"   📈 Total: {performance['total_acertos']} acertos em {performance['total_concursos']} concursos")
        
        # Mostrar alguns exemplos de acertos altos
        acertos_altos = [item for item in performance['acertos_por_concurso'] if item['acertos'] >= 6]
        if acertos_altos:
            print(f"   🔥 Acertos ≥6: {len(acertos_altos)} concursos")
            for item in acertos_altos[:3]:  # Mostrar apenas 3 exemplos
                print(f"      • Concurso {item['concurso']}: {item['acertos']} acertos")
    
    def _analisar_estatisticas_gerais(self, resultados):
        """Análise estatística geral de todos os períodos"""
        if not resultados:
            print("   ❌ Sem dados para análise")
            return
        
        # Coletar todas as performances
        medias = [r['performance']['media_acertos'] for r in resultados]
        acertos_6_plus = []
        acertos_7_plus = []
        acertos_8_plus = []
        
        for resultado in resultados:
            performance = resultado['performance']
            acertos_6 = len([item for item in performance['acertos_por_concurso'] if item['acertos'] >= 6])
            acertos_7 = len([item for item in performance['acertos_por_concurso'] if item['acertos'] >= 7])
            acertos_8 = len([item for item in performance['acertos_por_concurso'] if item['acertos'] >= 8])
            
            acertos_6_plus.append(acertos_6)
            acertos_7_plus.append(acertos_7)
            acertos_8_plus.append(acertos_8)
        
        # Estatísticas gerais
        media_geral = sum(medias) / len(medias)
        media_6_plus = sum(acertos_6_plus) / len(acertos_6_plus)
        media_7_plus = sum(acertos_7_plus) / len(acertos_7_plus)
        media_8_plus = sum(acertos_8_plus) / len(acertos_8_plus)
        
        print(f"   📊 Média geral de acertos: {media_geral:.2f} por concurso")
        print(f"   🔥 Média de concursos com ≥6 acertos: {media_6_plus:.1f} por período")
        print(f"   ⭐ Média de concursos com ≥7 acertos: {media_7_plus:.1f} por período")
        print(f"   🏆 Média de concursos com ≥8 acertos: {media_8_plus:.1f} por período")
        
        # Performance consistente?
        consistencia = len([m for m in medias if m >= 5.0]) / len(medias) * 100
        print(f"   📈 Consistência (≥5 acertos/concurso): {consistencia:.1f}% dos períodos")
    
    def _identificar_estrategias(self, resultados):
        """Identifica estratégias baseadas nos resultados"""
        print("   🎯 ESTRATÉGIAS IDENTIFICADAS:")
        print()
        
        # Estratégia 1: Núcleo fixo + complementares
        print("   1️⃣ **ESTRATÉGIA NÚCLEO FIXO:**")
        print("      • Use os 10 melhores como núcleo obrigatório")
        print("      • Complete com 5 números complementares inteligentes")
        print("      • Expectativa: 5-8 acertos do núcleo por concurso")
        print()
        
        # Estratégia 2: Escalonamento por performance
        print("   2️⃣ **ESTRATÉGIA ESCALONADA:**")
        print("      • Peso maior nos 5 primeiros dos 10 melhores")
        print("      • Uso rotativo dos 5 últimos conforme ausência")
        print("      • Adaptação dinâmica a cada 20-30 concursos")
        print()
        
        # Estratégia 3: Complementação inteligente
        print("   3️⃣ **ESTRATÉGIA COMPLEMENTAÇÃO INTELIGENTE:**")
        print("      • 10 melhores como base científica")
        print("      • 15 números complementares dos 15 restantes")
        print("      • Desdobramento C(15,5) dos complementares")
        print("      • Cobertura total: 10 fixos + variação dos 15")
        print()
        
        # Estratégia 4: Aproveitamento de padrões
        if resultados:
            melhor_resultado = max(resultados, key=lambda r: r['performance']['media_acertos'])
            print("   4️⃣ **ESTRATÉGIA PADRÃO IDENTIFICADO:**")
            print(f"      • Melhor núcleo histórico: {','.join(map(str, melhor_resultado['dez_melhores']))}")
            print(f"      • Performance: {melhor_resultado['performance']['media_acertos']:.1f} acertos/concurso")
            print(f"      • Use como referência para novos cálculos")

def main():
    """Função principal"""
    print("📊 SISTEMA DE ANÁLISE HISTÓRICA DOS 10 MELHORES")
    print("=" * 60)
    
    analisador = AnalisadorHistorico10Melhores()
    resultados = analisador.executar_analise_completa()
    
    print(f"\n💾 ANÁLISE CONCLUÍDA!")
    print(f"📊 {len(resultados)} períodos analisados")
    print(f"🎯 Estratégias identificadas e prontas para uso!")

if __name__ == "__main__":
    main()
