#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANALISADOR DE PADRÕES REFINADO - BUSCA PADRÕES FORTES
========================================================
Análise refinada para encontrar padrões mais significativos
com critérios estatísticos mais rigorosos
"""

import pyodbc
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
import json
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, ttest_ind
import seaborn as sns

# Importa configuração de banco existente
try:
    from database_optimizer import get_optimized_connection
    USE_OPTIMIZER = True
except ImportError:
    try:
        from database_config import db_config
        USE_OPTIMIZER = False
    except ImportError:
        USE_OPTIMIZER = None

class AnalisadorPadroesRefinado:
    """Analisador refinado com critérios estatísticos rigorosos"""
    
    def __init__(self):
        self.conexao = None
        self.dados = None
        self.resultados = {}
        self.padroes_significativos = []
        
    def conectar_banco(self):
        """🔌 Conecta ao banco de dados"""
        try:
            if USE_OPTIMIZER:
                self.conexao = get_optimized_connection()
            elif USE_OPTIMIZER is False:
                self.conexao = db_config.get_connection()
            else:
                connection_string = (
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=VADER\\SQLEXPRESS;"
                    "DATABASE=LotofacilDB;"
                    "Trusted_Connection=yes;"
                    "MARS_Connection=Yes;"
                )
                self.conexao = pyodbc.connect(connection_string)
            
            print("✅ Conectado ao banco LotofacilDB")
            return True
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def carregar_dados(self):
        """📊 Carrega dados com informações adicionais"""
        if not self.conexao:
            return False
            
        try:
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15,
                   (N1 + N2 + N3 + N4 + N5 + N6 + N7 + N8 + N9 + N10 + N11 + N12 + N13 + N14 + N15) as SomaTotal
            FROM resultados_int 
            WHERE Concurso IS NOT NULL
            ORDER BY Concurso
            """
            
            self.dados = pd.read_sql(query, self.conexao)
            print(f"📊 Dados carregados: {len(self.dados)} concursos")
            print(f"   Range: {self.dados['Concurso'].min()} a {self.dados['Concurso'].max()}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def calcular_estatisticas_avancadas(self):
        """📈 Calcula estatísticas avançadas para cada concurso"""
        print("\n📈 CALCULANDO ESTATÍSTICAS AVANÇADAS...")
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        # Calcula estatísticas por linha
        for idx, row in self.dados.iterrows():
            numeros = [row[col] for col in numeros_cols if pd.notna(row[col])]
            
            if len(numeros) >= 15:
                # Estatísticas básicas
                self.dados.at[idx, 'Media'] = np.mean(numeros)
                self.dados.at[idx, 'Mediana'] = np.median(numeros)
                self.dados.at[idx, 'Desvio'] = np.std(numeros)
                
                # Análise de distribuição
                pares = sum(1 for n in numeros if n % 2 == 0)
                impares = 15 - pares
                self.dados.at[idx, 'QtdPares'] = pares
                self.dados.at[idx, 'QtdImpares'] = impares
                
                # Análise de faixas
                baixos = sum(1 for n in numeros if n <= 12)
                altos = 15 - baixos
                self.dados.at[idx, 'QtdBaixos'] = baixos
                self.dados.at[idx, 'QtdAltos'] = altos
                
                # Análise de sequências
                numeros_sorted = sorted(numeros)
                gaps = [numeros_sorted[i+1] - numeros_sorted[i] for i in range(14)]
                self.dados.at[idx, 'GapMedio'] = np.mean(gaps)
                self.dados.at[idx, 'GapMax'] = max(gaps)
                
                # Análise de décadas
                decadas = defaultdict(int)
                for n in numeros:
                    decada = n // 10
                    decadas[decada] += 1
                self.dados.at[idx, 'Decada0'] = decadas[0]  # 1-9
                self.dados.at[idx, 'Decada1'] = decadas[1]  # 10-19
                self.dados.at[idx, 'Decada2'] = decadas[2]  # 20-25
                
        print("✅ Estatísticas avançadas calculadas")
    
    def analisar_padroes_temporais_profundos(self):
        """⏰ Análise temporal profunda"""
        print("\n⏰ ANÁLISE TEMPORAL PROFUNDA")
        print("=" * 40)
        
        # Análise por múltiplos
        multiplos_interessantes = [2, 3, 5, 10, 25, 50, 100]
        
        for mult in multiplos_interessantes:
            print(f"\n📊 MÚLTIPLOS DE {mult}:")
            
            # Concursos múltiplos vs não múltiplos
            multiplos = self.dados[self.dados['Concurso'] % mult == 0]
            nao_multiplos = self.dados[self.dados['Concurso'] % mult != 0]
            
            if len(multiplos) > 10:  # Só analisa se tiver dados suficientes
                # Compara médias das estatísticas
                stats_para_comparar = ['SomaTotal', 'Media', 'QtdPares', 'QtdBaixos', 'GapMedio']
                
                diferencas_significativas = []
                
                for stat in stats_para_comparar:
                    if stat in multiplos.columns and stat in nao_multiplos.columns:
                        media_mult = multiplos[stat].mean()
                        media_nao_mult = nao_multiplos[stat].mean()
                        diferenca = media_mult - media_nao_mult
                        diferenca_pct = (diferenca / media_nao_mult) * 100 if media_nao_mult != 0 else 0
                        
                        # Teste estatístico
                        try:
                            t_stat, p_value = ttest_ind(multiplos[stat].dropna(), 
                                                      nao_multiplos[stat].dropna())
                            significativo = p_value < 0.05
                        except:
                            significativo = False
                            p_value = 1.0
                        
                        if abs(diferenca_pct) > 3 and significativo:  # Diferença > 3% e significativa
                            diferencas_significativas.append({
                                'estatistica': stat,
                                'diferenca_pct': diferenca_pct,
                                'p_value': p_value,
                                'media_multiplos': media_mult,
                                'media_nao_multiplos': media_nao_mult
                            })
                
                if diferencas_significativas:
                    print(f"   ✅ {len(diferencas_significativas)} padrões significativos encontrados!")
                    for padrao in diferencas_significativas:
                        print(f"      • {padrao['estatistica']}: {padrao['diferenca_pct']:+.1f}% "
                              f"(p={padrao['p_value']:.3f})")
                    
                    self.padroes_significativos.append({
                        'tipo': f'multiplos_de_{mult}',
                        'quantidade_concursos': len(multiplos),
                        'padroes': diferencas_significativas
                    })
                else:
                    print(f"   ⚪ Sem padrões significativos")
    
    def analisar_ciclos_lunares_e_sazonais(self):
        """🌙 Análise de ciclos lunares e sazonais hipotéticos"""
        print("\n🌙 ANÁLISE DE CICLOS ESPECIAIS")
        print("=" * 35)
        
        # Ciclos de diferentes tamanhos
        ciclos_para_testar = [7, 14, 28, 30, 91, 365]  # Semanal, quinzenal, lunar, mensal, trimestral, anual
        
        for ciclo in ciclos_para_testar:
            print(f"\n📊 CICLO DE {ciclo} CONCURSOS:")
            
            # Calcula fase do ciclo para cada concurso
            self.dados[f'fase_ciclo_{ciclo}'] = self.dados['Concurso'] % ciclo
            
            # Agrupa por fase do ciclo
            grupos_ciclo = {}
            for fase in range(ciclo):
                grupos_ciclo[fase] = self.dados[self.dados[f'fase_ciclo_{ciclo}'] == fase]
            
            # Procura por fases com padrões distintos
            stats_para_comparar = ['SomaTotal', 'QtdPares', 'QtdBaixos', 'GapMedio']
            padroes_encontrados = []
            
            for stat in stats_para_comparar:
                medias_por_fase = []
                for fase in range(ciclo):
                    if len(grupos_ciclo[fase]) > 0:
                        media = grupos_ciclo[fase][stat].mean()
                        medias_por_fase.append((fase, media))
                
                if medias_por_fase:
                    # Ordena por média para encontrar outliers
                    medias_por_fase.sort(key=lambda x: x[1])
                    
                    # Verifica se há diferença significativa entre extremos
                    fase_min, valor_min = medias_por_fase[0]
                    fase_max, valor_max = medias_por_fase[-1]
                    
                    diferenca_pct = ((valor_max - valor_min) / valor_min) * 100 if valor_min != 0 else 0
                    
                    if abs(diferenca_pct) > 5:  # Diferença > 5%
                        # Teste estatístico entre grupos extremos
                        try:
                            grupo_min = grupos_ciclo[fase_min][stat].dropna()
                            grupo_max = grupos_ciclo[fase_max][stat].dropna()
                            
                            if len(grupo_min) > 5 and len(grupo_max) > 5:
                                t_stat, p_value = ttest_ind(grupo_min, grupo_max)
                                if p_value < 0.05:
                                    padroes_encontrados.append({
                                        'estatistica': stat,
                                        'fase_min': fase_min,
                                        'fase_max': fase_max,
                                        'diferenca_pct': diferenca_pct,
                                        'p_value': p_value
                                    })
                        except:
                            pass
            
            if padroes_encontrados:
                print(f"   ✅ {len(padroes_encontrados)} padrões cíclicos encontrados!")
                for padrao in padroes_encontrados:
                    print(f"      • {padrao['estatistica']}: Fase {padrao['fase_max']} vs {padrao['fase_min']} "
                          f"({padrao['diferenca_pct']:+.1f}%, p={padrao['p_value']:.3f})")
                
                self.padroes_significativos.append({
                    'tipo': f'ciclo_{ciclo}',
                    'padroes': padroes_encontrados
                })
            else:
                print(f"   ⚪ Sem padrões cíclicos significativos")
    
    def analisar_sequencias_e_consecutivos(self):
        """🔢 Análise de sequências numéricas e padrões consecutivos"""
        print("\n🔢 ANÁLISE DE SEQUÊNCIAS E CONSECUTIVOS")
        print("=" * 45)
        
        # Procura por padrões em concursos consecutivos
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        # Análise de repetições entre concursos consecutivos
        repeticoes_consecutivas = []
        
        for i in range(1, len(self.dados)):
            concurso_atual = self.dados.iloc[i]
            concurso_anterior = self.dados.iloc[i-1]
            
            nums_atual = set([concurso_atual[col] for col in numeros_cols if pd.notna(concurso_atual[col])])
            nums_anterior = set([concurso_anterior[col] for col in numeros_cols if pd.notna(concurso_anterior[col])])
            
            intersecao = len(nums_atual.intersection(nums_anterior))
            repeticoes_consecutivas.append(intersecao)
        
        # Análise estatística das repetições
        media_repeticoes = np.mean(repeticoes_consecutivas)
        desvio_repeticoes = np.std(repeticoes_consecutivas)
        
        print(f"📊 REPETIÇÕES ENTRE CONCURSOS CONSECUTIVOS:")
        print(f"   Média: {media_repeticoes:.2f} números")
        print(f"   Desvio: {desvio_repeticoes:.2f}")
        print(f"   Mínimo: {min(repeticoes_consecutivas)} números")
        print(f"   Máximo: {max(repeticoes_consecutivas)} números")
        
        # Procura por padrões incomuns
        outliers_baixo = [r for r in repeticoes_consecutivas if r < media_repeticoes - 2*desvio_repeticoes]
        outliers_alto = [r for r in repeticoes_consecutivas if r > media_repeticoes + 2*desvio_repeticoes]
        
        if outliers_baixo or outliers_alto:
            print(f"\n🎯 PADRÕES INCOMUNS DETECTADOS:")
            if outliers_baixo:
                print(f"   🔽 {len(outliers_baixo)} casos com muito poucas repetições (≤{min(outliers_baixo)})")
            if outliers_alto:
                print(f"   🔼 {len(outliers_alto)} casos com muitas repetições (≥{max(outliers_alto)})")
            
            self.padroes_significativos.append({
                'tipo': 'repeticoes_consecutivas',
                'media': media_repeticoes,
                'outliers_baixo': len(outliers_baixo),
                'outliers_alto': len(outliers_alto),
                'desvio': desvio_repeticoes
            })
    
    def analisar_padroes_numericos_especificos(self):
        """🎯 Análise de padrões específicos por número"""
        print("\n🎯 ANÁLISE DE PADRÕES ESPECÍFICOS POR NÚMERO")
        print("=" * 50)
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        # Para cada número, analisa em quais contextos aparece mais
        for numero in range(1, 26):
            print(f"\n🔍 ANALISANDO NÚMERO {numero}:")
            
            # Encontra concursos onde o número aparece
            concursos_com_numero = []
            concursos_sem_numero = []
            
            for idx, row in self.dados.iterrows():
                nums_no_concurso = [row[col] for col in numeros_cols if pd.notna(row[col])]
                if numero in nums_no_concurso:
                    concursos_com_numero.append(idx)
                else:
                    concursos_sem_numero.append(idx)
            
            if len(concursos_com_numero) < 20:  # Pula se aparecer muito pouco
                print(f"   ⚪ Aparece poucas vezes ({len(concursos_com_numero)})")
                continue
            
            # Compara características dos concursos com/sem o número
            df_com = self.dados.iloc[concursos_com_numero]
            df_sem = self.dados.iloc[concursos_sem_numero]
            
            stats_para_comparar = ['SomaTotal', 'QtdPares', 'QtdBaixos', 'GapMedio']
            padroes_numero = []
            
            for stat in stats_para_comparar:
                try:
                    media_com = df_com[stat].mean()
                    media_sem = df_sem[stat].mean()
                    diferenca_pct = ((media_com - media_sem) / media_sem) * 100 if media_sem != 0 else 0
                    
                    # Teste estatístico
                    t_stat, p_value = ttest_ind(df_com[stat].dropna(), df_sem[stat].dropna())
                    
                    if abs(diferenca_pct) > 5 and p_value < 0.05:  # Diferença > 5% e significativa
                        padroes_numero.append({
                            'estatistica': stat,
                            'diferenca_pct': diferenca_pct,
                            'p_value': p_value,
                            'frequencia': len(concursos_com_numero) / len(self.dados)
                        })
                except:
                    continue
            
            if padroes_numero:
                print(f"   ✅ {len(padroes_numero)} padrões significativos!")
                for padrao in padroes_numero:
                    print(f"      • {padrao['estatistica']}: {padrao['diferenca_pct']:+.1f}% "
                          f"(p={padrao['p_value']:.3f})")
                
                self.padroes_significativos.append({
                    'tipo': f'numero_{numero}',
                    'frequencia_aparicao': len(concursos_com_numero) / len(self.dados),
                    'padroes': padroes_numero
                })
            else:
                print(f"   ⚪ Sem padrões distintivos")
    
    def gerar_relatorio_refinado(self):
        """📋 Gera relatório refinado com padrões significativos"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO REFINADO - PADRÕES SIGNIFICATIVOS")
        print("=" * 60)
        
        if not self.padroes_significativos:
            print("\n⚠️ NENHUM PADRÃO ESTATISTICAMENTE SIGNIFICATIVO ENCONTRADO")
            print("📊 Todos os padrões estão dentro da variação normal esperada")
            return False
        
        print(f"\n✅ {len(self.padroes_significativos)} CATEGORIAS COM PADRÕES SIGNIFICATIVOS:")
        
        # Organiza por categoria
        categorias = {}
        for padrao in self.padroes_significativos:
            tipo = padrao['tipo']
            categoria = tipo.split('_')[0]
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(padrao)
        
        for categoria, padroes in categorias.items():
            print(f"\n🎯 {categoria.upper()}:")
            for padrao in padroes[:3]:  # Top 3 por categoria
                print(f"   • {padrao['tipo']}: {len(padrao.get('padroes', []))} padrões detectados")
                
                if 'padroes' in padrao:
                    for p in padrao['padroes'][:2]:  # Top 2 padrões por tipo
                        print(f"      - {p['estatistica']}: {p['diferenca_pct']:+.1f}% "
                              f"(significância: {1-p['p_value']:.1%})")
        
        # Avaliação final
        total_padroes = sum(len(p.get('padroes', [])) for p in self.padroes_significativos)
        
        print(f"\n💡 AVALIAÇÃO FINAL:")
        print(f"   📊 Total de padrões significativos: {total_padroes}")
        
        if total_padroes >= 10:
            print("   ✅ MUITOS padrões encontrados - ALTA utilidade!")
            print("   🚀 RECOMENDAÇÃO: Integrar sistema de detecção de padrões")
            utilidade = "ALTA"
        elif total_padroes >= 5:
            print("   📈 ALGUNS padrões encontrados - MÉDIA utilidade")
            print("   🎯 RECOMENDAÇÃO: Integrar padrões mais fortes")
            utilidade = "MÉDIA"
        else:
            print("   📊 POUCOS padrões encontrados - BAIXA utilidade")
            print("   ⚠️ RECOMENDAÇÃO: Limpar teste")
            utilidade = "BAIXA"
        
        return utilidade != "BAIXA"
    
    def salvar_resultados_refinados(self):
        """💾 Salva resultados refinados"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"analise_padroes_refinada_{timestamp}.json"
        
        resultado_completo = {
            'timestamp': timestamp,
            'resumo': {
                'total_concursos_analisados': len(self.dados),
                'total_padroes_significativos': len(self.padroes_significativos),
                'total_padroes_detalhados': sum(len(p.get('padroes', [])) for p in self.padroes_significativos)
            },
            'padroes_significativos': self.padroes_significativos
        }
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado_completo, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados refinados salvos em: {nome_arquivo}")
        return nome_arquivo
    
    def executar_analise_refinada(self):
        """🚀 Executa análise refinada completa"""
        print("🔍 ANALISADOR DE PADRÕES REFINADO - LOTOFÁCIL")
        print("=" * 50)
        
        if not self.conectar_banco():
            return False
        
        if not self.carregar_dados():
            return False
        
        # Calcula estatísticas avançadas
        self.calcular_estatisticas_avancadas()
        
        # Executa análises refinadas
        self.analisar_padroes_temporais_profundos()
        self.analisar_ciclos_lunares_e_sazonais()
        self.analisar_sequencias_e_consecutivos()
        self.analisar_padroes_numericos_especificos()
        
        # Gera relatório e avalia utilidade
        util = self.gerar_relatorio_refinado()
        
        # Salva resultados
        arquivo = self.salvar_resultados_refinados()
        
        print(f"\n🎯 CONCLUSÃO REFINADA: {'ÚTIL - Integrar!' if util else 'Não útil - Limpar'}")
        
        return util

def main():
    """Função principal"""
    analisador = AnalisadorPadroesRefinado()
    return analisador.executar_analise_refinada()

if __name__ == "__main__":
    main()