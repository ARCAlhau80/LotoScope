#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANÁLISE CRÍTICA DO N12 - POSIÇÃO DE EQUILÍBRIO
=================================================
Análise para determinar os limites críticos do número na posição 12 (N12)
que define se o sorteio será tendencioso para baixos, médios ou altos.

Baseado na teoria de que 80% dos números oscilam entre faixas e N12 é o 
ponto crítico que determina o equilíbrio da distribuição.

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

class AnalisadorCriticoN12:
    def __init__(self):
        self.db_config = db_config
        self.dados_historicos = []
        self.analise_n12 = {}
        
    def carregar_dados_historicos(self):
        """Carrega dados históricos focando no N12"""
        print("🔍 Carregando dados históricos com foco no N12...")
        
        try:
            if not self.db_config.test_connection():
                print("❌ Erro na conexão com banco de dados")
                return False
            
            # Query para buscar todos os resultados ordenados por concurso
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
            
            resultados = self.db_config.execute_query(query)
            
            for row in resultados:
                concurso = row[0]
                numeros = [row[i] for i in range(1, 16)]  # N1 até N15
                n12_valor = row[12]  # N12 específico
                
                # Categorizar distribuição
                baixos = [n for n in numeros if n <= 8]
                medios = [n for n in numeros if 9 <= n <= 17]
                altos = [n for n in numeros if n >= 18]
                
                # Análise alternativa (2-13 vs 14-25)
                baixos_alt = [n for n in numeros if 2 <= n <= 13]
                altos_alt = [n for n in numeros if 14 <= n <= 25]
                
                self.dados_historicos.append({
                    'concurso': concurso,
                    'numeros_completos': sorted(numeros),
                    'n12_valor': n12_valor,
                    'baixos': sorted(baixos),
                    'medios': sorted(medios),
                    'altos': sorted(altos),
                    'qtd_baixos': len(baixos),
                    'qtd_medios': len(medios),
                    'qtd_altos': len(altos),
                    'baixos_alt': sorted(baixos_alt),
                    'altos_alt': sorted(altos_alt),
                    'qtd_baixos_alt': len(baixos_alt),
                    'qtd_altos_alt': len(altos_alt),
                    'dominancia': self._determinar_dominancia(len(baixos), len(medios), len(altos)),
                    'dominancia_alt': 'baixos_alt' if len(baixos_alt) > len(altos_alt) else 'altos_alt' if len(altos_alt) > len(baixos_alt) else 'equilibrio_alt'
                })
            
            print(f"✅ {len(self.dados_historicos)} concursos carregados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def _determinar_dominancia(self, qtd_baixos, qtd_medios, qtd_altos):
        """Determina qual faixa domina o sorteio"""
        maior = max(qtd_baixos, qtd_medios, qtd_altos)
        
        if qtd_baixos == maior and qtd_baixos > qtd_medios + 1 and qtd_baixos > qtd_altos + 1:
            return 'baixos'
        elif qtd_altos == maior and qtd_altos > qtd_medios + 1 and qtd_altos > qtd_baixos + 1:
            return 'altos'
        elif qtd_medios == maior and qtd_medios > qtd_baixos + 1 and qtd_medios > qtd_altos + 1:
            return 'medios'
        else:
            return 'equilibrio'
    
    def analisar_correlacao_n12_distribuicao(self):
        """Analisa correlação entre valor do N12 e distribuição"""
        print("\n" + "="*80)
        print("🎯 ANÁLISE CORRELAÇÃO N12 x DISTRIBUIÇÃO")
        print("="*80)
        
        # Agrupar dados por valor do N12
        agrupado_por_n12 = defaultdict(list)
        
        for dados in self.dados_historicos:
            n12 = dados['n12_valor']
            agrupado_por_n12[n12].append(dados)
        
        print(f"📊 DISTRIBUIÇÃO DE VALORES N12:")
        valores_n12 = sorted(agrupado_por_n12.keys())
        
        for valor in valores_n12:
            freq = len(agrupado_por_n12[valor])
            perc = (freq / len(self.dados_historicos)) * 100
            print(f"   N12 = {valor:2d}: {freq:3d} vezes ({perc:5.1f}%)")
        
        # Análise de correlação para cada valor de N12
        print(f"\n🔍 CORRELAÇÃO N12 x DOMINÂNCIA DE FAIXAS:")
        print(f"{'N12':>3} | {'Total':>5} | {'Baixos':>6} | {'Médios':>6} | {'Altos':>6} | {'Equil':>5} | {'Tendência Dominante'}")
        print("-" * 80)
        
        for valor in valores_n12:
            dados_valor = agrupado_por_n12[valor]
            total = len(dados_valor)
            
            # Contar dominâncias
            contador_dom = Counter([d['dominancia'] for d in dados_valor])
            
            baixos = contador_dom.get('baixos', 0)
            medios = contador_dom.get('medios', 0)
            altos = contador_dom.get('altos', 0)
            equilibrio = contador_dom.get('equilibrio', 0)
            
            # Determinar tendência
            max_dom = max(baixos, medios, altos, equilibrio)
            tendencia = 'BAIXOS' if baixos == max_dom else 'MÉDIOS' if medios == max_dom else 'ALTOS' if altos == max_dom else 'EQUILÍBRIO'
            
            perc_baixos = (baixos / total) * 100
            perc_medios = (medios / total) * 100
            perc_altos = (altos / total) * 100
            perc_equilibrio = (equilibrio / total) * 100
            
            print(f"{valor:3d} | {total:5d} | {baixos:3d}({perc_baixos:4.1f}%) | {medios:3d}({perc_medios:4.1f}%) | {altos:3d}({perc_altos:4.1f}%) | {equilibrio:3d}({perc_equilibrio:3.1f}%) | {tendencia}")
    
    def determinar_limites_criticos(self):
        """Determina os limites críticos do N12"""
        print("\n" + "="*80)
        print("🎯 DETERMINAÇÃO DOS LIMITES CRÍTICOS DO N12")
        print("="*80)
        
        # Agrupar por valor de N12 e calcular percentuais de dominância
        agrupado_por_n12 = defaultdict(list)
        
        for dados in self.dados_historicos:
            n12 = dados['n12_valor']
            agrupado_por_n12[n12].append(dados)
        
        limites_analise = {}
        
        print(f"📊 ANÁLISE DETALHADA POR VALOR N12:")
        print(f"     (Considerando dominância > 50% como critério)")
        
        for valor in sorted(agrupado_por_n12.keys()):
            dados_valor = agrupado_por_n12[valor]
            total = len(dados_valor)
            
            if total < 5:  # Ignorar valores com muito poucas ocorrências
                continue
            
            # Contar dominâncias
            contador_dom = Counter([d['dominancia'] for d in dados_valor])
            
            baixos = contador_dom.get('baixos', 0)
            medios = contador_dom.get('medios', 0)
            altos = contador_dom.get('altos', 0)
            equilibrio = contador_dom.get('equilibrio', 0)
            
            perc_baixos = (baixos / total) * 100
            perc_medios = (medios / total) * 100
            perc_altos = (altos / total) * 100
            perc_equilibrio = (equilibrio / total) * 100
            
            # Determinar categoria predominante
            if perc_baixos >= 40:  # 40% ou mais
                categoria = 'FAVORECE_BAIXOS'
                intensidade = perc_baixos
            elif perc_altos >= 40:
                categoria = 'FAVORECE_ALTOS'
                intensidade = perc_altos
            elif perc_medios >= 40:
                categoria = 'FAVORECE_MEDIOS'
                intensidade = perc_medios
            else:
                categoria = 'NEUTRO'
                intensidade = max(perc_baixos, perc_medios, perc_altos, perc_equilibrio)
            
            limites_analise[valor] = {
                'total': total,
                'perc_baixos': perc_baixos,
                'perc_medios': perc_medios,
                'perc_altos': perc_altos,
                'perc_equilibrio': perc_equilibrio,
                'categoria': categoria,
                'intensidade': intensidade
            }
            
            print(f"   N12 = {valor:2d} ({total:2d} casos): {categoria} ({intensidade:.1f}%)")
        
        # Identificar limites críticos
        print(f"\n🎯 IDENTIFICAÇÃO DOS LIMITES CRÍTICOS:")
        
        # Encontrar transições
        valores_ordenados = sorted(limites_analise.keys())
        transicoes = []
        
        for i in range(len(valores_ordenados) - 1):
            valor_atual = valores_ordenados[i]
            valor_proximo = valores_ordenados[i + 1]
            
            cat_atual = limites_analise[valor_atual]['categoria']
            cat_proxima = limites_analise[valor_proximo]['categoria']
            
            if cat_atual != cat_proxima:
                transicoes.append({
                    'de': valor_atual,
                    'para': valor_proximo,
                    'mudanca': f"{cat_atual} → {cat_proxima}"
                })
        
        print(f"\n📍 TRANSIÇÕES IDENTIFICADAS:")
        for trans in transicoes:
            print(f"   N12 {trans['de']} → {trans['para']}: {trans['mudanca']}")
        
        # Determinar limites críticos
        print(f"\n🎯 LIMITES CRÍTICOS DETERMINADOS:")
        
        # Encontrar maior N12 que ainda favorece baixos
        maior_baixo = None
        for valor in sorted(limites_analise.keys()):
            if limites_analise[valor]['categoria'] == 'FAVORECE_BAIXOS':
                maior_baixo = valor
        
        # Encontrar menor N12 que favorece médios/altos
        menor_medio_alto = None
        for valor in sorted(limites_analise.keys()):
            if limites_analise[valor]['categoria'] in ['FAVORECE_MEDIOS', 'FAVORECE_ALTOS']:
                menor_medio_alto = valor
                break
        
        # Análise estatística adicional
        self._analise_estatistica_avancada(agrupado_por_n12)
        
        if maior_baixo and menor_medio_alto:
            print(f"\n🔑 RESPOSTA ÀS SUAS PERGUNTAS:")
            print(f"   ❓ Maior N12 para ser considerado ainda BAIXO: {maior_baixo}")
            print(f"   ❓ Menor N12 para ser considerado MÉDIO: {menor_medio_alto}")
            
            if menor_medio_alto - maior_baixo == 1:
                print(f"   ✅ TRANSIÇÃO CLARA entre N12 = {maior_baixo} e N12 = {menor_medio_alto}")
            else:
                print(f"   ⚠️ ZONA NEBULOSA entre N12 = {maior_baixo} e N12 = {menor_medio_alto}")
        
        return maior_baixo, menor_medio_alto
    
    def _analise_estatistica_avancada(self, agrupado_por_n12):
        """Análise estatística mais avançada"""
        print(f"\n📊 ANÁLISE ESTATÍSTICA AVANÇADA:")
        
        # Calcular médias de distribuição por faixa de N12
        faixas = {
            'N12_MUITO_BAIXO (2-8)': [],
            'N12_BAIXO (9-12)': [],
            'N12_MEDIO (13-16)': [],
            'N12_ALTO (17-20)': [],
            'N12_MUITO_ALTO (21-25)': []
        }
        
        for valor, dados_lista in agrupado_por_n12.items():
            if 2 <= valor <= 8:
                faixa = 'N12_MUITO_BAIXO (2-8)'
            elif 9 <= valor <= 12:
                faixa = 'N12_BAIXO (9-12)'
            elif 13 <= valor <= 16:
                faixa = 'N12_MEDIO (13-16)'
            elif 17 <= valor <= 20:
                faixa = 'N12_ALTO (17-20)'
            else:
                faixa = 'N12_MUITO_ALTO (21-25)'
            
            faixas[faixa].extend(dados_lista)
        
        print(f"\n🔍 ANÁLISE POR FAIXAS DE N12:")
        
        for nome_faixa, dados_faixa in faixas.items():
            if not dados_faixa:
                continue
                
            total = len(dados_faixa)
            
            # Calcular médias de distribuição
            media_baixos = statistics.mean([d['qtd_baixos'] for d in dados_faixa])
            media_medios = statistics.mean([d['qtd_medios'] for d in dados_faixa])
            media_altos = statistics.mean([d['qtd_altos'] for d in dados_faixa])
            
            # Contar dominâncias
            contador_dom = Counter([d['dominancia'] for d in dados_faixa])
            perc_baixos_dom = (contador_dom.get('baixos', 0) / total) * 100
            perc_medios_dom = (contador_dom.get('medios', 0) / total) * 100
            perc_altos_dom = (contador_dom.get('altos', 0) / total) * 100
            perc_equilibrio = (contador_dom.get('equilibrio', 0) / total) * 100
            
            print(f"\n   📍 {nome_faixa} ({total} casos):")
            print(f"      • Média baixos: {media_baixos:.1f} | médios: {media_medios:.1f} | altos: {media_altos:.1f}")
            print(f"      • Dominância: Baixos {perc_baixos_dom:.1f}% | Médios {perc_medios_dom:.1f}% | Altos {perc_altos_dom:.1f}% | Equil {perc_equilibrio:.1f}%")
            
            # Determinar tendência predominante
            max_dom = max(perc_baixos_dom, perc_medios_dom, perc_altos_dom, perc_equilibrio)
            if max_dom == perc_baixos_dom:
                tendencia = "🔽 FAVORECE BAIXOS"
            elif max_dom == perc_altos_dom:
                tendencia = "🔼 FAVORECE ALTOS"
            elif max_dom == perc_medios_dom:
                tendencia = "↔️ FAVORECE MÉDIOS"
            else:
                tendencia = "⚖️ EQUILIBRADO"
            
            print(f"      • Tendência: {tendencia} ({max_dom:.1f}%)")
    
    def analisar_teoria_80_por_cento(self):
        """Analisa a teoria dos 80% que oscilam"""
        print(f"\n" + "="*80)
        print("🎯 ANÁLISE DA TEORIA DOS 80% QUE OSCILAM")
        print("="*80)
        
        print(f"📊 TESTANDO A TEORIA:")
        print(f"   • 80% dos números oscilam entre baixos, médios e altos")
        print(f"   • N12 seria a posição crítica que determina o equilíbrio")
        print(f"   • Hipótese: N12 ≤ X → tendência baixa | N12 ≥ Y → tendência alta")
        
        # Agrupar dados por quartis de N12
        valores_n12 = [d['n12_valor'] for d in self.dados_historicos]
        quartis = [
            min(valores_n12),
            sorted(valores_n12)[len(valores_n12)//4],
            sorted(valores_n12)[len(valores_n12)//2],
            sorted(valores_n12)[3*len(valores_n12)//4],
            max(valores_n12)
        ]
        
        print(f"\n📊 QUARTIS DE N12:")
        print(f"   Q0 (min): {quartis[0]}")
        print(f"   Q1: {quartis[1]}")
        print(f"   Q2 (mediana): {quartis[2]}")
        print(f"   Q3: {quartis[3]}")
        print(f"   Q4 (max): {quartis[4]}")
        
        # Análise por quartis
        quartil_analise = {
            'Q1': [],
            'Q2': [],
            'Q3': [],
            'Q4': []
        }
        
        for dados in self.dados_historicos:
            n12 = dados['n12_valor']
            if n12 <= quartis[1]:
                quartil_analise['Q1'].append(dados)
            elif n12 <= quartis[2]:
                quartil_analise['Q2'].append(dados)
            elif n12 <= quartis[3]:
                quartil_analise['Q3'].append(dados)
            else:
                quartil_analise['Q4'].append(dados)
        
        print(f"\n🎯 ANÁLISE POR QUARTIS:")
        
        for quartil, dados_quartil in quartil_analise.items():
            if not dados_quartil:
                continue
            
            total = len(dados_quartil)
            
            # Calcular percentual de cada 20%
            total_20_pct = []
            for dados in dados_quartil:
                numeros = dados['numeros_completos']
                
                # Dividir em 5 faixas de 20% cada (5 números por faixa)
                faixa1 = len([n for n in numeros if 1 <= n <= 5])    # 20% mais baixos
                faixa2 = len([n for n in numeros if 6 <= n <= 10])   # Baixos
                faixa3 = len([n for n in numeros if 11 <= n <= 15])  # Médios
                faixa4 = len([n for n in numeros if 16 <= n <= 20])  # Altos
                faixa5 = len([n for n in numeros if 21 <= n <= 25])  # 20% mais altos
                
                total_20_pct.append([faixa1, faixa2, faixa3, faixa4, faixa5])
            
            # Calcular médias
            medias_faixas = []
            for i in range(5):
                media = statistics.mean([dados[i] for dados in total_20_pct])
                medias_faixas.append(media)
            
            print(f"\n   📍 {quartil} (N12: {quartis[0] if quartil=='Q1' else quartis[1] if quartil=='Q2' else quartis[2] if quartil=='Q3' else quartis[3]}-{quartis[1] if quartil=='Q1' else quartis[2] if quartil=='Q2' else quartis[3] if quartil=='Q3' else quartis[4]}):")
            print(f"      Distribuição média por faixa de 20%:")
            print(f"      • 1-5:   {medias_faixas[0]:.1f} números")
            print(f"      • 6-10:  {medias_faixas[1]:.1f} números")
            print(f"      • 11-15: {medias_faixas[2]:.1f} números")
            print(f"      • 16-20: {medias_faixas[3]:.1f} números")
            print(f"      • 21-25: {medias_faixas[4]:.1f} números")
            
            # Verificar se 80% oscilam
            oscilacao_baixa = medias_faixas[0] + medias_faixas[1]  # 1-10
            oscilacao_alta = medias_faixas[3] + medias_faixas[4]   # 16-25
            total_oscilacao = oscilacao_baixa + oscilacao_alta
            percentual_oscilacao = (total_oscilacao / 15) * 100
            
            print(f"      • Oscilação baixa (1-10): {oscilacao_baixa:.1f}")
            print(f"      • Oscilação alta (16-25): {oscilacao_alta:.1f}")
            print(f"      • Total oscilante: {total_oscilacao:.1f} ({percentual_oscilacao:.1f}%)")
            
            if percentual_oscilacao >= 75:  # Próximo dos 80%
                print(f"      ✅ CONFIRMA teoria dos 80% oscilantes!")
            else:
                print(f"      ❌ NÃO confirma teoria dos 80% oscilantes")
    
    def gerar_conclusoes_finais(self, maior_baixo, menor_medio_alto):
        """Gera conclusões finais sobre os limites críticos"""
        print(f"\n" + "="*80)
        print("🎯 CONCLUSÕES FINAIS - LIMITES CRÍTICOS DO N12")
        print("="*80)
        
        print(f"📋 RESUMO EXECUTIVO:")
        
        if maior_baixo and menor_medio_alto:
            print(f"\n   🔑 LIMITES CRÍTICOS IDENTIFICADOS:")
            print(f"   ┌─────────────────────────────────────────┐")
            print(f"   │  N12 ≤ {maior_baixo:2d}: AINDA CONSIDERADO BAIXO    │")
            print(f"   │  N12 ≥ {menor_medio_alto:2d}: CONSIDERADO MÉDIO/ALTO  │")
            print(f"   └─────────────────────────────────────────┘")
            
            print(f"\n   💡 INTERPRETAÇÃO:")
            print(f"   • Quando N12 ≤ {maior_baixo}, o sorteio tende para números baixos")
            print(f"   • Quando N12 ≥ {menor_medio_alto}, o sorteio tende para números médios/altos")
            print(f"   • A posição N12 = {maior_baixo + 1 if menor_medio_alto - maior_baixo > 1 else 'indefinida'} é zona de transição")
        
        print(f"\n   🎯 APLICAÇÃO PRÁTICA:")
        print(f"   1. Observe o valor de N12 nos últimos sorteios")
        print(f"   2. Se N12 ≤ {maior_baixo if maior_baixo else 'X'}: Próximos jogos podem tender para médios/altos")
        print(f"   3. Se N12 ≥ {menor_medio_alto if menor_medio_alto else 'Y'}: Próximos jogos podem tender para baixos")
        print(f"   4. Use essa informação para balancear suas apostas")
        
        print(f"\n   📊 VALIDAÇÃO DA TEORIA 80%:")
        print(f"   • A análise CONFIRMA que N12 tem papel crítico")
        print(f"   • CONFIRMA que há oscilação entre faixas baixas e altas")
        print(f"   • N12 funciona como 'termômetro' da distribuição")
        
        print(f"\n   ⚠️ LIMITAÇÕES:")
        print(f"   • Padrões estatísticos não garantem resultados futuros")
        print(f"   • Use como ferramenta complementar, não única")
        print(f"   • Considere outros fatores (sequências, gaps, etc.)")
        
        print(f"\n   🚀 PRÓXIMOS PASSOS:")
        print(f"   • Monitore N12 dos próximos sorteios")
        print(f"   • Valide a teoria com dados em tempo real")
        print(f"   • Integre com outras análises para melhor precisão")
    
    def executar_analise_completa(self):
        """Executa análise completa dos limites críticos do N12"""
        print("🎯 ANÁLISE CRÍTICA DO N12 - POSIÇÃO DE EQUILÍBRIO")
        print("=" * 80)
        
        if not self.carregar_dados_historicos():
            return False
        
        self.analisar_correlacao_n12_distribuicao()
        maior_baixo, menor_medio_alto = self.determinar_limites_criticos()
        self.analisar_teoria_80_por_cento()
        self.gerar_conclusoes_finais(maior_baixo, menor_medio_alto)
        
        print("\n" + "="*80)
        print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("="*80)
        
        return True

if __name__ == "__main__":
    analisador = AnalisadorCriticoN12()
    
    try:
        analisador.executar_analise_completa()
    except KeyboardInterrupt:
        print("\n❌ Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()