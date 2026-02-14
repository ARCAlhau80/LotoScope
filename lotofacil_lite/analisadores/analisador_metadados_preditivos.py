#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANALISADOR DE METADADOS PREDITIVOS - LOTOFÁCIL
=================================================
Análise dos campos de apoio da tabela Resultados_INT para identificar
padrões e gerar cláusulas WHERE preditivas para o próximo concurso.

CAMPOS ANALISADOS (ignorando nulos: Resultado, Localidade, Latitude, Longitude):
✅ QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal
✅ Quintil1-5, QtdeGaps, QtdeRepetidos, SEQ
✅ DistanciaExtremos, ParesSequencia, QtdeMultiplos3
✅ ParesSaltados, Faixa_Baixa, Faixa_Media, Faixa_Alta
✅ RepetidosMesmaPosicao, Acumulou

Autor: AR CALHAU
Data: 18/09/2025
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

import statistics
from collections import Counter, defaultdict
import pandas as pd
import numpy as np

class AnalisadorMetadadosPreditivos:
    def analisar_n11_igual_17_n17_proximo(self):
        """Analisa concursos onde N11=17 e comportamento de N17 no concurso seguinte."""
        print("\n" + "="*70)
        print("🔎 ANÁLISE: Quando N11=17, comportamento de N17 no próximo concurso")
        print("="*70)
        # Buscar concursos onde N11=17
        indices = [i for i, d in enumerate(self.dados_historicos[:-1]) if 'N11' in d and d['N11'] == 17]
        if not indices:
            print("❌ Nenhum concurso encontrado com N11=17.")
            return
        n17_next = []
        for i in indices:
            prox = self.dados_historicos[i+1]
            if 'N17' in prox and prox['N17'] is not None:
                n17_next.append(prox['N17'])
        if not n17_next:
            print("❌ Nenhum dado de N17 no próximo concurso encontrado.")
            return
        igual_17 = sum(1 for v in n17_next if v == 17)
        maior_17 = sum(1 for v in n17_next if v > 17)
        menor_17 = sum(1 for v in n17_next if v < 17)
        total = len(n17_next)
        print(f"Total de casos analisados: {total}")
        print(f"N17 igual a 17: {igual_17} ({(igual_17/total)*100:.1f}%)")
        print(f"N17 maior que 17: {maior_17} ({(maior_17/total)*100:.1f}%)")
        print(f"N17 menor que 17: {menor_17} ({(menor_17/total)*100:.1f}%)")
        # Maior e menor valor de N17 nessas situações
        print(f"Maior valor observado de N17: {max(n17_next)}")
        print(f"Menor valor observado de N17: {min(n17_next)}")
        # Frequência dos valores
        from collections import Counter
        mais_comuns = Counter(n17_next).most_common(3)
        print(f"Valores de N17 mais comuns: {mais_comuns}")
    def analisar_finais_4e5(self):
        """Analisa concursos de final 4 e 5 em busca de padrões automáticos, sem viés anterior."""
        print("\n" + "="*70)
        print("🔎 ANÁLISE AUTOMÁTICA: CONCURSOS FINAL 4 E 5")
        print("="*70)
        finais_4e5 = [d for d in self.dados_historicos if str(d['concurso'])[-1] in ("4", "5")]
        if not finais_4e5:
            print("❌ Nenhum concurso final 4 ou 5 encontrado.")
            return

        print(f"Total de concursos final 4 ou 5: {len(finais_4e5)}")
        # Estatísticas gerais
        acumulou = [d['Acumulou'] for d in finais_4e5 if d['Acumulou'] is not None]
        if acumulou:
            perc_acumulou = (sum(1 for a in acumulou if a) / len(acumulou)) * 100
            print(f"• Acumulou: {sum(1 for a in acumulou if a)} de {len(acumulou)} ({perc_acumulou:.1f}%)")
        else:
            print("• Acumulou: sem dados")

        # Estatísticas automáticas para todos os campos
        import statistics
        for campo in self.campos_analise:
            if campo == 'Acumulou':
                continue
            valores = [d[campo] for d in finais_4e5 if d[campo] is not None]
            if not valores:
                continue
            print(f"\n📊 Campo: {campo}")
            print(f"  • Média: {statistics.mean(valores):.2f}")
            print(f"  • Mediana: {statistics.median(valores):.2f}")
            print(f"  • Mínimo: {min(valores)}")
            print(f"  • Máximo: {max(valores)}")
            if len(valores) > 1:
                print(f"  • Desvio padrão: {statistics.stdev(valores):.2f}")
            # Frequência dos valores mais comuns
            from collections import Counter
            mais_comuns = Counter(valores).most_common(3)
            print(f"  • Valores mais comuns: {mais_comuns}")
        print("\nAnálise concluída. Veja se algum campo apresenta comportamento fora do padrão geral.")
    def __init__(self):
        self.db_config = db_config
        self.dados_historicos = []
        self.campos_analise = [
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'QtdeGaps', 'QtdeRepetidos', 'SEQ', 'DistanciaExtremos',
            'ParesSequencia', 'QtdeMultiplos3', 'ParesSaltados',
            'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta', 'RepetidosMesmaPosicao',
            'Acumulou'
        ] + [f'N{i}' for i in range(1, 16)]

    def analisar_n_dezena_valor_nX_proximo(self, dezena='N11', valor=17, alvo='N17'):
        """Analisa concursos onde dezena=N e comportamento de alvo no próximo concurso."""
        print("\n" + "="*70)
        print(f"🔎 ANÁLISE: Quando {dezena}={valor}, comportamento de {alvo} no próximo concurso")
        print("="*70)
        # Buscar concursos onde dezena=valor
        indices = [i for i, d in enumerate(self.dados_historicos[:-1]) if dezena in d and d[dezena] == valor]
        if not indices:
            print(f"❌ Nenhum concurso encontrado com {dezena}={valor}.")
            return
        alvo_next = []
        for i in indices:
            prox = self.dados_historicos[i+1]
            if alvo in prox and prox[alvo] is not None:
                alvo_next.append(prox[alvo])
        if not alvo_next:
            print(f"❌ Nenhum dado de {alvo} no próximo concurso encontrado.")
            return
        igual = sum(1 for v in alvo_next if v == valor)
        maior = sum(1 for v in alvo_next if v > valor)
        menor = sum(1 for v in alvo_next if v < valor)
        total = len(alvo_next)
        print(f"Total de casos analisados: {total}")
        print(f"{alvo} igual a {valor}: {igual} ({(igual/total)*100:.1f}%)")
        print(f"{alvo} maior que {valor}: {maior} ({(maior/total)*100:.1f}%)")
        print(f"{alvo} menor que {valor}: {menor} ({(menor/total)*100:.1f}%)")
        # Maior e menor valor de alvo nessas situações
        print(f"Maior valor observado de {alvo}: {max(alvo_next)}")
        print(f"Menor valor observado de {alvo}: {min(alvo_next)}")
        # Frequência dos valores
        from collections import Counter
        mais_comuns = Counter(alvo_next).most_common(3)
        print(f"Valores de {alvo} mais comuns: {mais_comuns}")
        self.padroes_identificados = {}
        self.clausulas_where = []
        
    def carregar_dados_metadados(self):
        """Carrega dados dos metadados da tabela Resultados_INT"""
        print("🔍 Carregando metadados históricos...")
        
        try:
            if not self.db_config.test_connection():
                print("❌ Erro na conexão com banco")
                return False
            
            # Query focada nos campos de metadados (ignorando campos nulos)
            campos_query = ", ".join(self.campos_analise)
            query = f"""
            SELECT Concurso, Data_Sorteio, {campos_query}
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
            
            resultados = self.db_config.execute_query(query)
            
            for row in resultados:
                dados = {
                    'concurso': row[0],
                    'data_sorteio': row[1]
                }
                
                # Adicionar campos de metadados
                for i, campo in enumerate(self.campos_analise):
                    dados[campo] = row[i + 2]  # +2 porque Concurso e Data_Sorteio vêm primeiro
                
                self.dados_historicos.append(dados)
            
            print(f"✅ {len(self.dados_historicos)} concursos carregados")
            print(f"✅ {len(self.campos_analise)} campos de metadados analisados")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analisar_distribuicoes_campos(self):
        """Analisa as distribuições de cada campo de metadados"""
        print("\n" + "="*70)
        print("📊 ANÁLISE DE DISTRIBUIÇÕES DOS CAMPOS DE METADADOS")
        print("="*70)
        
        for campo in self.campos_analise:
            print(f"\n🔍 CAMPO: {campo}")
            print("-" * 50)
            
            valores = [dados[campo] for dados in self.dados_historicos if dados[campo] is not None]
            
            if not valores:
                print("   ⚠️ Sem dados válidos")
                continue
            
            # Estatísticas básicas
            if campo == 'Acumulou':  # Campo booleano
                contador = Counter(valores)
                total = len(valores)
                print(f"   • Acumulou=True: {contador.get(1, 0)} ({(contador.get(1, 0)/total)*100:.1f}%)")
                print(f"   • Acumulou=False: {contador.get(0, 0)} ({(contador.get(0, 0)/total)*100:.1f}%)")
            else:  # Campos numéricos
                print(f"   • Média: {statistics.mean(valores):.2f}")
                print(f"   • Mediana: {statistics.median(valores):.1f}")
                print(f"   • Mínimo: {min(valores)} | Máximo: {max(valores)}")
                print(f"   • Desvio padrão: {statistics.stdev(valores):.2f}")
                
                # Distribuição de frequências (top 10)
                contador = Counter(valores)
                print(f"   • Valores mais frequentes:")
                for valor, freq in contador.most_common(10):
                    perc = (freq / len(valores)) * 100
                    print(f"     - {valor}: {freq} vezes ({perc:.1f}%)")
    
    def analisar_tendencias_sequenciais(self):
        """Analisa tendências entre concursos consecutivos"""
        print("\n" + "="*70)
        print("🔄 ANÁLISE DE TENDÊNCIAS SEQUENCIAIS")
        print("="*70)
        
        tendencias = {}
        
        for campo in self.campos_analise:
            print(f"\n📈 TENDÊNCIAS: {campo}")
            print("-" * 40)
            
            if campo == 'Acumulou':
                continue  # Skip para campo booleano
            
            # Calcular mudanças entre concursos consecutivos
            mudancas = []
            valores_consecutivos = []
            
            for i in range(len(self.dados_historicos) - 1):
                atual = self.dados_historicos[i][campo]
                proximo = self.dados_historicos[i + 1][campo]
                if atual is not None and proximo is not None:
                    mudanca = proximo - atual
                    mudancas.append(mudanca)
                    valores_consecutivos.append((atual, proximo))
            
            if mudancas:
                # Estatísticas de mudanças
                print(f"   • Mudança média: {statistics.mean(mudancas):.2f}")
                print(f"   • Mudanças positivas: {sum(1 for m in mudancas if m > 0)} ({(sum(1 for m in mudancas if m > 0)/len(mudancas))*100:.1f}%)")
                print(f"   • Mudanças negativas: {sum(1 for m in mudancas if m < 0)} ({(sum(1 for m in mudancas if m < 0)/len(mudancas))*100:.1f}%)")
                print(f"   • Sem mudança: {sum(1 for m in mudancas if m == 0)} ({(sum(1 for m in mudancas if m == 0)/len(mudancas))*100:.1f}%)")
                
                # Detectar padrões de reversão
                reversoes = 0
                continuidades = 0
                
                for i in range(len(mudancas) - 1):
                    if (mudancas[i] > 0 and mudancas[i+1] < 0) or (mudancas[i] < 0 and mudancas[i+1] > 0):
                        reversoes += 1
                    elif (mudancas[i] > 0 and mudancas[i+1] > 0) or (mudancas[i] < 0 and mudancas[i+1] < 0):
                        continuidades += 1
                
                total_padroes = reversoes + continuidades
                if total_padroes > 0:
                    print(f"   • Tendência de reversão: {(reversoes/total_padroes)*100:.1f}%")
                    print(f"   • Tendência de continuidade: {(continuidades/total_padroes)*100:.1f}%")
                
                tendencias[campo] = {
                    'mudanca_media': statistics.mean(mudancas),
                    'reversao_perc': (reversoes/total_padroes)*100 if total_padroes > 0 else 0,
                    'continuidade_perc': (continuidades/total_padroes)*100 if total_padroes > 0 else 0
                }
        
        self.padroes_identificados['tendencias'] = tendencias
    
    def identificar_padroes_valores_extremos(self):
        """Identifica padrões quando valores estão em extremos"""
        print("\n" + "="*70)
        print("⚡ ANÁLISE DE VALORES EXTREMOS")
        print("="*70)
        
        for campo in self.campos_analise:
            if campo == 'Acumulou':
                continue
                
            print(f"\n🎯 EXTREMOS: {campo}")
            print("-" * 30)
            
            valores = [dados[campo] for dados in self.dados_historicos if dados[campo] is not None]
            
            if not valores:
                continue
            
            # Definir extremos (10% inferior e superior)
            valores_ordenados = sorted(valores)
            limite_inferior = np.percentile(valores_ordenados, 10)
            limite_superior = np.percentile(valores_ordenados, 90)
            
            print(f"   • Limite inferior (10%): {limite_inferior:.1f}")
            print(f"   • Limite superior (90%): {limite_superior:.1f}")
            
            # Analisar o que acontece após valores extremos
            apos_minimo = []
            apos_maximo = []
            
            for i in range(len(self.dados_historicos) - 1):
                atual = self.dados_historicos[i][campo]
                proximo = self.dados_historicos[i + 1][campo]
                if atual is not None and proximo is not None:
                    if atual <= limite_inferior:
                        apos_minimo.append(proximo)
                    elif atual >= limite_superior:
                        apos_maximo.append(proximo)
            
            # Estatísticas após extremos
            if apos_minimo:
                print(f"   • Após valor mínimo (média próximo): {statistics.mean(apos_minimo):.2f}")
                tendencia_min = "⬆️ SOBE" if statistics.mean(apos_minimo) > limite_inferior else "⬇️ DESCE"
                print(f"   • Tendência após mínimo: {tendencia_min}")
            
            if apos_maximo:
                print(f"   • Após valor máximo (média próximo): {statistics.mean(apos_maximo):.2f}")
                tendencia_max = "⬇️ DESCE" if statistics.mean(apos_maximo) < limite_superior else "⬆️ SOBE"
                print(f"   • Tendência após máximo: {tendencia_max}")
    
    def detectar_correlacoes_campos(self):
        """Detecta correlações entre diferentes campos"""
        print("\n" + "="*70)
        print("🔗 ANÁLISE DE CORRELAÇÕES ENTRE CAMPOS")
        print("="*70)
        
        # Preparar dados para correlação
        dados_numericos = {}
        for campo in self.campos_analise:
            if campo != 'Acumulou':  # Ignorar campo booleano por enquanto
                valores = [dados[campo] for dados in self.dados_historicos if dados[campo] is not None]
                dados_numericos[campo] = valores
        
        # Calcular correlações importantes
        correlacoes_fortes = []
        
        campos_lista = list(dados_numericos.keys())
        for i in range(len(campos_lista)):
            for j in range(i + 1, len(campos_lista)):
                campo1 = campos_lista[i]
                campo2 = campos_lista[j]
                # Garantir mesmo tamanho
                tamanho_min = min(len(dados_numericos[campo1]), len(dados_numericos[campo2]))
                valores1 = dados_numericos[campo1][:tamanho_min]
                valores2 = dados_numericos[campo2][:tamanho_min]
                # Calcular correlação
                if len(valores1) > 1 and len(valores2) > 1:
                    correlacao = np.corrcoef(valores1, valores2)[0, 1]
                    # Apenas correlações significativas (>0.3 ou <-0.3)
                    if abs(correlacao) > 0.3:
                        correlacoes_fortes.append((campo1, campo2, correlacao))
        
        # Mostrar correlações fortes
        if correlacoes_fortes:
            print("🔗 CORRELAÇÕES SIGNIFICATIVAS (>30%):")
            correlacoes_fortes.sort(key=lambda x: abs(x[2]), reverse=True)
            
            for campo1, campo2, corr in correlacoes_fortes[:10]:  # Top 10
                simbolo = "📈" if corr > 0 else "📉"
                print(f"   {simbolo} {campo1} ↔ {campo2}: {corr:.3f}")
        else:
            print("   ℹ️ Nenhuma correlação forte encontrada")
    
    def analisar_situacao_atual(self):
        """Analisa a situação do último concurso"""
        print("\n" + "="*70)
        print("📊 SITUAÇÃO ATUAL (ÚLTIMO CONCURSO)")
        print("="*70)
        
        if not self.dados_historicos:
            print("❌ Sem dados para análise")
            return
        
        ultimo_concurso = self.dados_historicos[-1]
        penultimo_concurso = self.dados_historicos[-2] if len(self.dados_historicos) > 1 else None
        
        print(f"🎯 Concurso atual: {ultimo_concurso['concurso']}")
        print(f"📅 Data: {ultimo_concurso['data_sorteio']}")
        print()
        
        print("📋 VALORES ATUAIS DOS METADADOS:")
        for campo in self.campos_analise:
            valor_atual = ultimo_concurso[campo]
            simbolo_mudanca = ""
            
            if penultimo_concurso and campo != 'Acumulou':
                valor_anterior = penultimo_concurso[campo]
                if valor_atual is not None and valor_anterior is not None:
                    if valor_atual > valor_anterior:
                        simbolo_mudanca = " ⬆️"
                    elif valor_atual < valor_anterior:
                        simbolo_mudanca = " ⬇️"
                    else:
                        simbolo_mudanca = " ➡️"
            
            print(f"   • {campo}: {valor_atual}{simbolo_mudanca}")
        
        return ultimo_concurso
    
    def gerar_clausulas_where_preditivas(self):
        """Gera cláusulas WHERE preditivas baseadas nos padrões identificados"""
        print("\n" + "="*70)
        print("🔮 GERAÇÃO DE CLÁUSULAS WHERE PREDITIVAS")
        print("="*70)
        
        if not self.dados_historicos:
            print("❌ Sem dados para gerar predições")
            return
        
        ultimo_concurso = self.dados_historicos[-1]
        clausulas = []
        justificativas = []
        
        print("🧠 ANALISANDO PADRÕES PARA PREDIÇÃO...")
        
        for campo in self.campos_analise:
            if campo == 'Acumulou':
                continue  # Skip campo booleano por enquanto
            
            valor_atual = ultimo_concurso[campo]
            if valor_atual is None:
                continue
            
            # Calcular estatísticas históricas do campo
            valores_historicos = [d[campo] for d in self.dados_historicos if d[campo] is not None]
            
            if not valores_historicos:
                continue
            
            media = statistics.mean(valores_historicos)
            desvio = statistics.stdev(valores_historicos)
            mediana = statistics.median(valores_historicos)
            
            # Analisar se valor atual está em extremo
            percentil_atual = (sorted(valores_historicos).index(valor_atual) / len(valores_historicos)) * 100
            
            # Analisar tendência baseada em últimos 5 valores
            ultimos_5 = [d[campo] for d in self.dados_historicos[-5:] if d[campo] is not None]
            
            if len(ultimos_5) >= 3:
                tendencia_recente = "CRESCENTE" if ultimos_5[-1] > ultimos_5[0] else "DECRESCENTE"
                
                # REGRAS PREDITIVAS
                
                # Regra 1: Reversão após extremos
                if percentil_atual < 15:  # Valor muito baixo
                    valor_predito_min = int(media - desvio/2)
                    valor_predito_max = int(media + desvio/2)
                    clausulas.append(f"{campo} BETWEEN {valor_predito_min} AND {valor_predito_max}")
                    justificativas.append(f"{campo}: Reversão após valor baixo ({valor_atual} → média)")
                
                elif percentil_atual > 85:  # Valor muito alto
                    valor_predito_min = int(media - desvio/2)
                    valor_predito_max = int(media + desvio/2)
                    clausulas.append(f"{campo} BETWEEN {valor_predito_min} AND {valor_predito_max}")
                    justificativas.append(f"{campo}: Reversão após valor alto ({valor_atual} → média)")
                
                # Regra 2: Continuidade de tendência (com moderação)
                elif tendencia_recente == "CRESCENTE" and valor_atual < media:
                    valor_predito_min = valor_atual
                    valor_predito_max = int(media + desvio/3)
                    clausulas.append(f"{campo} BETWEEN {valor_predito_min} AND {valor_predito_max}")
                    justificativas.append(f"{campo}: Continuidade crescente moderada")
                
                elif tendencia_recente == "DECRESCENTE" and valor_atual > media:
                    valor_predito_min = int(media - desvio/3)
                    valor_predito_max = valor_atual
                    clausulas.append(f"{campo} BETWEEN {valor_predito_min} AND {valor_predito_max}")
                    justificativas.append(f"{campo}: Continuidade decrescente moderada")
                
                # Regra 3: Retorno à média (padrão mais comum)
                else:
                    valor_predito_min = int(mediana - desvio/3)
                    valor_predito_max = int(mediana + desvio/3)
                    clausulas.append(f"{campo} BETWEEN {valor_predito_min} AND {valor_predito_max}")
                    justificativas.append(f"{campo}: Retorno à mediana histórica")
        
        # Mostrar resultados
        print(f"\n🎯 CLÁUSULAS WHERE GERADAS ({len(clausulas)} condições):")
        print("=" * 50)
        
        for i, (clausula, justificativa) in enumerate(zip(clausulas, justificativas), 1):
            print(f"{i:2}. {clausula}")
            print(f"    💡 {justificativa}")
            print()
        
        # Gerar query completa
        if clausulas:
            query_completa = "SELECT * FROM Resultados_INT WHERE " + " AND ".join(clausulas)
            
            print("🔍 QUERY COMPLETA PREDITIVA:")
            print("=" * 50)
            print(query_completa)
            print()
            
            # Testar quantos concursos históricos atendem às condições
            print("🧪 TESTE DE VALIDAÇÃO:")
            print("-" * 30)
            
            try:
                resultados_teste = self.db_config.execute_query(query_completa)
                print(f"   ✅ {len(resultados_teste)} concursos históricos atendem às condições")
                print(f"   📊 Isso representa {(len(resultados_teste)/len(self.dados_historicos))*100:.1f}% do histórico")
                
                if len(resultados_teste) > 0:
                    concursos_encontrados = [r[0] for r in resultados_teste[-5:]]  # Últimos 5
                    print(f"   🎯 Últimos concursos similares: {concursos_encontrados}")
                
            except Exception as e:
                print(f"   ⚠️ Erro no teste: {e}")
        
        self.clausulas_where = clausulas
        return clausulas, justificativas
    
    def executar_analise_completa(self):
        """Executa a análise completa dos metadados"""
        print("🔍 INICIANDO ANÁLISE COMPLETA DE METADADOS PREDITIVOS")
        print("="*70)
        
        if not self.carregar_dados_metadados():
            return False
        
        self.analisar_distribuicoes_campos()
        self.analisar_tendencias_sequenciais()
        self.identificar_padroes_valores_extremos()
        self.detectar_correlacoes_campos()
        self.analisar_situacao_atual()
        clausulas, justificativas = self.gerar_clausulas_where_preditivas()
        
        print("\n" + "="*70)
        print("✅ ANÁLISE DE METADADOS CONCLUÍDA!")
        print("="*70)
        print(f"🎯 {len(clausulas)} cláusulas WHERE preditivas geradas")
        print("🧠 Baseado em análise de padrões históricos de metadados")
        
        return True

def main():
    """Função principal"""
    analisador = AnalisadorMetadadosPreditivos()
    
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