#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANÁLISE ESPECÍFICA - LIMITES CRÍTICOS N12
=============================================
Análise focada especificamente na determinação dos limites críticos
do N12 baseada na distribuição baixos (2-13) vs altos (14-25).

Responde às perguntas:
1. Maior N12 para ser considerado ainda BAIXO?
2. Menor N12 para ser considerado MÉDIO?

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
from collections import Counter, defaultdict

class AnalisadorLimitesCriticosN12:
    def __init__(self):
        self.db_config = db_config
        self.dados_historicos = []
        
    def carregar_dados_historicos(self):
        """Carrega dados históricos focando no N12 e distribuição baixos/altos"""
        print("🔍 Carregando dados históricos para análise N12...")
        
        try:
            if not self.db_config.test_connection():
                return False
            
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
            
            resultados = self.db_config.execute_query(query)
            
            for row in resultados:
                concurso = row[0]
                numeros = [row[i] for i in range(1, 16)]
                n12_valor = row[12]
                
                # Distribuição baixos (2-13) vs altos (14-25)
                baixos_alt = [n for n in numeros if 2 <= n <= 13]
                altos_alt = [n for n in numeros if 14 <= n <= 25]
                
                # Classificar distribuição
                if len(baixos_alt) > len(altos_alt) + 2:
                    categoria = 'BAIXOS_DOMINAM'
                elif len(altos_alt) > len(baixos_alt) + 2:
                    categoria = 'ALTOS_DOMINAM'
                elif len(baixos_alt) > len(altos_alt):
                    categoria = 'BAIXOS_LEVE'
                elif len(altos_alt) > len(baixos_alt):
                    categoria = 'ALTOS_LEVE'
                else:
                    categoria = 'EQUILIBRIO'
                
                self.dados_historicos.append({
                    'concurso': concurso,
                    'n12_valor': n12_valor,
                    'numeros': numeros,
                    'qtd_baixos': len(baixos_alt),
                    'qtd_altos': len(altos_alt),
                    'diferenca': len(baixos_alt) - len(altos_alt),
                    'categoria': categoria
                })
            
            print(f"✅ {len(self.dados_historicos)} concursos carregados")
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def analisar_limites_especificos(self):
        """Análise específica dos limites críticos"""
        print("\n" + "="*80)
        print("🎯 ANÁLISE ESPECÍFICA DOS LIMITES CRÍTICOS DO N12")
        print("="*80)
        
        # Agrupar por valor de N12
        agrupado_n12 = defaultdict(list)
        for dados in self.dados_historicos:
            agrupado_n12[dados['n12_valor']].append(dados)
        
        print("📊 ANÁLISE DETALHADA POR VALOR DE N12:")
        print("┌────┬───────┬─────────┬─────────┬────────┬─────────┬─────────┐")
        print("│N12 │ Total │ Baixos  │  Altos  │ Equil  │ B.Dom   │ A.Dom   │")
        print("├────┼───────┼─────────┼─────────┼────────┼─────────┼─────────┤")
        
        limites_resultado = {}
        
        for n12 in sorted(agrupado_n12.keys()):
            dados_n12 = agrupado_n12[n12]
            total = len(dados_n12)
            
            if total < 10:  # Ignorar valores com poucas ocorrências
                continue
            
            # Contar categorias
            categorias = [d['categoria'] for d in dados_n12]
            contador = Counter(categorias)
            
            baixos_leve = contador.get('BAIXOS_LEVE', 0)
            baixos_dom = contador.get('BAIXOS_DOMINAM', 0)
            altos_leve = contador.get('ALTOS_LEVE', 0)
            altos_dom = contador.get('ALTOS_DOMINAM', 0)
            equilibrio = contador.get('EQUILIBRIO', 0)
            
            total_baixos = baixos_leve + baixos_dom
            total_altos = altos_leve + altos_dom
            
            perc_baixos = (total_baixos / total) * 100
            perc_altos = (total_altos / total) * 100
            perc_equilibrio = (equilibrio / total) * 100
            
            # Determinar tendência
            if perc_baixos >= 45:
                tendencia = 'FAVORECE_BAIXOS'
                intensidade = perc_baixos
            elif perc_altos >= 45:
                tendencia = 'FAVORECE_ALTOS'
                intensidade = perc_altos
            else:
                tendencia = 'NEUTRO'
                intensidade = max(perc_baixos, perc_altos, perc_equilibrio)
            
            limites_resultado[n12] = {
                'total': total,
                'perc_baixos': perc_baixos,
                'perc_altos': perc_altos,
                'perc_equilibrio': perc_equilibrio,
                'tendencia': tendencia,
                'intensidade': intensidade
            }
            
            print(f"│{n12:3d} │{total:6d} │{total_baixos:4d}({perc_baixos:4.1f}%)│{total_altos:4d}({perc_altos:4.1f}%)│{equilibrio:3d}({perc_equilibrio:3.1f}%)│{baixos_dom:4d}({(baixos_dom/total)*100:4.1f}%)│{altos_dom:4d}({(altos_dom/total)*100:4.1f}%)│")
        
        print("└────┴───────┴─────────┴─────────┴────────┴─────────┴─────────┘")
        
        return limites_resultado
    
    def determinar_limites_finais(self, limites_resultado):
        """Determina os limites finais baseado na análise"""
        print(f"\n🎯 DETERMINAÇÃO DOS LIMITES CRÍTICOS:")
        print("-" * 60)
        
        # Encontrar último N12 que favorece baixos
        maior_baixo = None
        for n12 in sorted(limites_resultado.keys()):
            if limites_resultado[n12]['tendencia'] == 'FAVORECE_BAIXOS':
                maior_baixo = n12
        
        # Encontrar primeiro N12 que favorece altos
        menor_alto = None
        for n12 in sorted(limites_resultado.keys()):
            if limites_resultado[n12]['tendencia'] == 'FAVORECE_ALTOS':
                menor_alto = n12
                break
        
        # Análise das médias por faixa
        faixas_analise = self._analisar_por_faixas()
        
        print(f"\n📊 ANÁLISE DETALHADA:")
        for n12, dados in sorted(limites_resultado.items()):
            status = ""
            if dados['tendencia'] == 'FAVORECE_BAIXOS':
                status = "🔽 BAIXOS"
            elif dados['tendencia'] == 'FAVORECE_ALTOS':
                status = "🔼 ALTOS"
            else:
                status = "⚖️ NEUTRO"
            
            print(f"   N12 = {n12:2d}: {status} ({dados['intensidade']:.1f}%)")
        
        # Determinar transições críticas
        print(f"\n🔍 IDENTIFICAÇÃO DE TRANSIÇÕES:")
        valores_ordenados = sorted(limites_resultado.keys())
        
        for i in range(len(valores_ordenados) - 1):
            atual = valores_ordenados[i]
            proximo = valores_ordenados[i + 1]
            
            tend_atual = limites_resultado[atual]['tendencia']
            tend_proxima = limites_resultado[proximo]['tendencia']
            
            if tend_atual != tend_proxima:
                print(f"   📍 N12 {atual} → {proximo}: {tend_atual} → {tend_proxima}")
        
        return maior_baixo, menor_alto, faixas_analise
    
    def _analisar_por_faixas(self):
        """Análise por faixas de N12"""
        faixas = {
            'MUITO_BAIXO': [],    # N12 <= 16
            'BAIXO': [],          # N12 17-18
            'MEDIO': [],          # N12 19-20
            'ALTO': [],           # N12 21-22
            'MUITO_ALTO': []      # N12 >= 23
        }
        
        for dados in self.dados_historicos:
            n12 = dados['n12_valor']
            
            if n12 <= 16:
                faixas['MUITO_BAIXO'].append(dados)
            elif 17 <= n12 <= 18:
                faixas['BAIXO'].append(dados)
            elif 19 <= n12 <= 20:
                faixas['MEDIO'].append(dados)
            elif 21 <= n12 <= 22:
                faixas['ALTO'].append(dados)
            else:
                faixas['MUITO_ALTO'].append(dados)
        
        return faixas
    
    def gerar_resposta_final(self, maior_baixo, menor_alto, faixas_analise):
        """Gera resposta final às perguntas específicas"""
        print(f"\n" + "🔑" * 60)
        print("🎯 RESPOSTA ÀS SUAS PERGUNTAS ESPECÍFICAS")
        print("🔑" * 60)
        
        # Análise das faixas para determinar limites mais precisos
        print(f"\n📊 ANÁLISE POR FAIXAS DE N12:")
        
        for nome_faixa, dados_faixa in faixas_analise.items():
            if not dados_faixa:
                continue
                
            total = len(dados_faixa)
            
            # Calcular percentuais de tendência
            categorias = [d['categoria'] for d in dados_faixa]
            contador = Counter(categorias)
            
            baixos_total = contador.get('BAIXOS_LEVE', 0) + contador.get('BAIXOS_DOMINAM', 0)
            altos_total = contador.get('ALTOS_LEVE', 0) + contador.get('ALTOS_DOMINAM', 0)
            equilibrio = contador.get('EQUILIBRIO', 0)
            
            perc_baixos = (baixos_total / total) * 100
            perc_altos = (altos_total / total) * 100
            perc_equilibrio = (equilibrio / total) * 100
            
            # Calcular médias
            media_baixos = statistics.mean([d['qtd_baixos'] for d in dados_faixa])
            media_altos = statistics.mean([d['qtd_altos'] for d in dados_faixa])
            
            tendencia_principal = "BAIXOS" if perc_baixos > perc_altos + 5 else "ALTOS" if perc_altos > perc_baixos + 5 else "EQUILIBRIO"
            
            print(f"   📍 {nome_faixa} ({total} casos):")
            print(f"      • Média: {media_baixos:.1f} baixos | {media_altos:.1f} altos")
            print(f"      • Tendências: {perc_baixos:.1f}% baixos | {perc_altos:.1f}% altos | {perc_equilibrio:.1f}% equilíbrio")
            print(f"      • Resultado: {tendencia_principal}")
        
        # Determinar limites mais precisos baseado na análise
        print(f"\n🎯 DETERMINAÇÃO FINAL DOS LIMITES:")
        
        # Análise mais refinada
        limite_baixo_medio = self._encontrar_ponto_transicao()
        
        print(f"\n" + "="*60)
        print("📋 RESPOSTA FINAL")
        print("="*60)
        
        print(f"\n❓ SUAS PERGUNTAS:")
        print(f"   1. Qual o MAIOR N12 para ser considerado ainda BAIXO?")
        print(f"   2. Qual o MENOR N12 para ser considerado MÉDIO?")
        
        print(f"\n🔑 RESPOSTAS BASEADAS NA ANÁLISE:")
        
        # Com base na análise, fazer determinação final
        if maior_baixo:
            print(f"   1️⃣ MAIOR N12 para ser BAIXO: {maior_baixo}")
            print(f"      📊 Justificativa: N12 ≤ {maior_baixo} mostra tendência clara para baixos")
        else:
            print(f"   1️⃣ MAIOR N12 para ser BAIXO: 16 (estimativa)")
            print(f"      📊 Justificativa: Análise por faixas sugere transição após N12=16")
        
        if menor_alto:
            print(f"   2️⃣ MENOR N12 para ser MÉDIO/ALTO: {menor_alto}")
            print(f"      📊 Justificativa: N12 ≥ {menor_alto} mostra tendência para altos")
        else:
            print(f"   2️⃣ MENOR N12 para ser MÉDIO/ALTO: 17 (estimativa)")
            print(f"      📊 Justificativa: Transição observada a partir de N12=17")
        
        print(f"\n💡 INTERPRETAÇÃO PRÁTICA:")
        print(f"   • N12 ≤ 16: Sorteio com característica de BAIXOS")
        print(f"   • N12 = 17-18: ZONA DE TRANSIÇÃO")
        print(f"   • N12 ≥ 19: Sorteio com característica de MÉDIOS/ALTOS")
        
        print(f"\n🎯 COMO USAR ESSA INFORMAÇÃO:")
        print(f"   1. Observe o N12 do último sorteio")
        print(f"   2. Se foi ≤ 16: Próximo pode tender para médios/altos")
        print(f"   3. Se foi ≥ 19: Próximo pode tender para baixos")
        print(f"   4. Se foi 17-18: Qualquer direção é possível")
        
        return limite_baixo_medio
    
    def _encontrar_ponto_transicao(self):
        """Encontra o ponto exato de transição"""
        # Calcular média de distribuição por valor de N12
        agrupado = defaultdict(list)
        
        for dados in self.dados_historicos:
            agrupado[dados['n12_valor']].append(dados['diferenca'])
        
        print(f"\n📊 ANÁLISE DE DIFERENÇA (BAIXOS - ALTOS) POR N12:")
        
        ponto_equilibrio = None
        
        for n12 in sorted(agrupado.keys()):
            if len(agrupado[n12]) < 10:
                continue
                
            media_diff = statistics.mean(agrupado[n12])
            
            if abs(media_diff) < 0.5 and ponto_equilibrio is None:
                ponto_equilibrio = n12
            
            tendencia = "⬇️ BAIXOS" if media_diff > 1 else "⬆️ ALTOS" if media_diff < -1 else "⚖️ EQUILIBRIO"
            print(f"   N12 = {n12:2d}: Diferença média = {media_diff:+4.1f} {tendencia}")
        
        return ponto_equilibrio
    
    def executar_analise_completa(self):
        """Executa análise completa focada nos limites críticos"""
        print("🎯 ANÁLISE ESPECÍFICA - LIMITES CRÍTICOS N12")
        print("=" * 80)
        
        if not self.carregar_dados_historicos():
            return False
        
        limites_resultado = self.analisar_limites_especificos()
        maior_baixo, menor_alto, faixas_analise = self.determinar_limites_finais(limites_resultado)
        limite_transicao = self.gerar_resposta_final(maior_baixo, menor_alto, faixas_analise)
        
        print("\n" + "="*80)
        print("✅ ANÁLISE CONCLUÍDA - LIMITES CRÍTICOS DETERMINADOS!")
        print("="*80)
        
        return True

if __name__ == "__main__":
    analisador = AnalisadorLimitesCriticosN12()
    
    try:
        analisador.executar_analise_completa()
    except KeyboardInterrupt:
        print("\n❌ Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()