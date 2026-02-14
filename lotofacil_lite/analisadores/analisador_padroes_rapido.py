#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANALISADOR DE PADRÕES: PARES/ÍMPARES E FINAIS ESPECÍFICOS
============================================================
Análise rápida para descobrir padrões óbvios em concursos
baseado em paridade e finais específicos (0 e 5)
"""

import pyodbc
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
import json

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

class AnalisadorPadroesRapido:
    """Analisador rápido de padrões por paridade e finais"""
    
    def __init__(self):
        self.conexao = None
        self.dados = None
        self.resultados = {}
        
    def conectar_banco(self):
        """🔌 Conecta ao banco de dados"""
        try:
            if USE_OPTIMIZER:
                self.conexao = get_optimized_connection()
            elif USE_OPTIMIZER is False:
                self.conexao = db_config.get_connection()
            else:
                # Fallback para conexão direta
                connection_string = (
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=DESKTOP-71QV65D\\SQLEXPRESS;"
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
        """📊 Carrega todos os dados da tabela resultados_int"""
        if not self.conexao:
            return False
            
        try:
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15
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
    
    def analisar_padroes_paridade(self):
        """🔢 Analisa padrões entre concursos pares e ímpares"""
        print("\n🔢 ANÁLISE DE PADRÕES: CONCURSOS PARES vs ÍMPARES")
        print("=" * 60)
        
        # Separa concursos pares e ímpares
        concursos_pares = self.dados[self.dados['Concurso'] % 2 == 0]
        concursos_impares = self.dados[self.dados['Concurso'] % 2 == 1]
        
        print(f"📊 Concursos pares: {len(concursos_pares)}")
        print(f"📊 Concursos ímpares: {len(concursos_impares)}")
        
        # Análise de frequência de números
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        # Frequências em concursos pares
        freq_pares = {}
        for col in numeros_cols:
            valores = concursos_pares[col].dropna().tolist()
            freq_pares.update(Counter(valores))
        
        # Frequências em concursos ímpares  
        freq_impares = {}
        for col in numeros_cols:
            valores = concursos_impares[col].dropna().tolist()
            freq_impares.update(Counter(valores))
        
        # Normaliza por quantidade de concursos
        for num in range(1, 26):
            if num in freq_pares:
                freq_pares[num] = freq_pares[num] / len(concursos_pares)
            if num in freq_impares:
                freq_impares[num] = freq_impares[num] / len(concursos_impares)
        
        # Encontra diferenças significativas
        diferencas = {}
        for num in range(1, 26):
            freq_par = freq_pares.get(num, 0)
            freq_impar = freq_impares.get(num, 0)
            diferenca = freq_par - freq_impar
            diferencas[num] = {
                'freq_pares': freq_par,
                'freq_impares': freq_impar,
                'diferenca': diferenca,
                'preferencia': 'PARES' if diferenca > 0.01 else 'ÍMPARES' if diferenca < -0.01 else 'NEUTRA'
            }
        
        # Top números que preferem pares
        top_pares = sorted(diferencas.items(), key=lambda x: x[1]['diferenca'], reverse=True)[:5]
        # Top números que preferem ímpares  
        top_impares = sorted(diferencas.items(), key=lambda x: x[1]['diferenca'])[:5]
        
        print("\n🎯 TOP 5 NÚMEROS QUE PREFEREM CONCURSOS PARES:")
        for num, data in top_pares:
            print(f"   {num:2d}: {data['freq_pares']:.3f} vs {data['freq_impares']:.3f} "
                  f"(+{data['diferenca']:.3f})")
        
        print("\n🎯 TOP 5 NÚMEROS QUE PREFEREM CONCURSOS ÍMPARES:")
        for num, data in top_impares:
            print(f"   {num:2d}: {data['freq_pares']:.3f} vs {data['freq_impares']:.3f} "
                  f"({data['diferenca']:.3f})")
        
        self.resultados['paridade'] = {
            'concursos_pares': len(concursos_pares),
            'concursos_impares': len(concursos_impares),
            'frequencias_detalhadas': diferencas,
            'top_preferem_pares': top_pares,
            'top_preferem_impares': top_impares
        }
    
    def analisar_finais_especificos(self):
        """🎯 Analisa padrões em concursos com finais 0 e 5"""
        print("\n🎯 ANÁLISE DE FINAIS ESPECÍFICOS: 0 e 5")
        print("=" * 45)
        
        # Separa por finais
        final_0 = self.dados[self.dados['Concurso'] % 10 == 0]
        final_5 = self.dados[self.dados['Concurso'] % 10 == 5]
        outros_finais = self.dados[~self.dados['Concurso'].isin(
            list(final_0['Concurso']) + list(final_5['Concurso'])
        )]
        
        print(f"📊 Concursos final 0: {len(final_0)}")
        print(f"📊 Concursos final 5: {len(final_5)}")
        print(f"📊 Outros finais: {len(outros_finais)}")
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        def calcular_frequencias(df):
            freq = {}
            for col in numeros_cols:
                valores = df[col].dropna().tolist()
                freq.update(Counter(valores))
            # Normaliza
            for num in range(1, 26):
                if num in freq:
                    freq[num] = freq[num] / len(df) if len(df) > 0 else 0
                else:
                    freq[num] = 0
            return freq
        
        freq_final_0 = calcular_frequencias(final_0)
        freq_final_5 = calcular_frequencias(final_5)
        freq_outros = calcular_frequencias(outros_finais)
        
        # Análise comparativa
        print("\n📈 NÚMEROS COM MAIOR FREQUÊNCIA EM FINAIS 0:")
        top_final_0 = sorted(freq_final_0.items(), key=lambda x: x[1], reverse=True)[:10]
        for num, freq in top_final_0:
            freq_outros_num = freq_outros.get(num, 0)
            diferenca = freq - freq_outros_num
            print(f"   {num:2d}: {freq:.3f} (outros: {freq_outros_num:.3f}, "
                  f"dif: {diferenca:+.3f})")
        
        print("\n📈 NÚMEROS COM MAIOR FREQUÊNCIA EM FINAIS 5:")
        top_final_5 = sorted(freq_final_5.items(), key=lambda x: x[1], reverse=True)[:10]
        for num, freq in top_final_5:
            freq_outros_num = freq_outros.get(num, 0)
            diferenca = freq - freq_outros_num
            print(f"   {num:2d}: {freq:.3f} (outros: {freq_outros_num:.3f}, "
                  f"dif: {diferenca:+.3f})")
        
        self.resultados['finais_especificos'] = {
            'final_0': {
                'quantidade': len(final_0),
                'frequencias': freq_final_0,
                'top_10': top_final_0
            },
            'final_5': {
                'quantidade': len(final_5),
                'frequencias': freq_final_5,
                'top_10': top_final_5
            },
            'outros_finais': {
                'quantidade': len(outros_finais),
                'frequencias': freq_outros
            }
        }
    
    def analisar_campos_comparativos(self):
        """📊 Analisa maior_que_ultimo vs menor_que_ultimo por paridade"""
        print("\n📊 ANÁLISE DE CAMPOS COMPARATIVOS")
        print("=" * 40)
        
        # Calcula campos comparativos
        self.dados['ultimo_numero'] = self.dados['N15']
        self.dados['maior_que_ultimo'] = 0
        self.dados['menor_que_ultimo'] = 0
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14']
        
        for idx, row in self.dados.iterrows():
            ultimo = row['ultimo_numero']
            if pd.notna(ultimo):
                maior_count = 0
                menor_count = 0
                for col in numeros_cols:
                    if pd.notna(row[col]):
                        if row[col] > ultimo:
                            maior_count += 1
                        elif row[col] < ultimo:
                            menor_count += 1
                
                self.dados.at[idx, 'maior_que_ultimo'] = maior_count
                self.dados.at[idx, 'menor_que_ultimo'] = menor_count
        
        # Análise por paridade
        pares = self.dados[self.dados['Concurso'] % 2 == 0]
        impares = self.dados[self.dados['Concurso'] % 2 == 1]
        
        print("📊 MÉDIAS EM CONCURSOS PARES:")
        print(f"   Maior que último: {pares['maior_que_ultimo'].mean():.2f}")
        print(f"   Menor que último: {pares['menor_que_ultimo'].mean():.2f}")
        
        print("\n📊 MÉDIAS EM CONCURSOS ÍMPARES:")
        print(f"   Maior que último: {impares['maior_que_ultimo'].mean():.2f}")
        print(f"   Menor que último: {impares['menor_que_ultimo'].mean():.2f}")
        
        print("\n📈 DIFERENÇAS (Pares - Ímpares):")
        dif_maior = pares['maior_que_ultimo'].mean() - impares['maior_que_ultimo'].mean()
        dif_menor = pares['menor_que_ultimo'].mean() - impares['menor_que_ultimo'].mean()
        print(f"   Maior que último: {dif_maior:+.3f}")
        print(f"   Menor que último: {dif_menor:+.3f}")
        
        self.resultados['campos_comparativos'] = {
            'pares': {
                'maior_que_ultimo_media': float(pares['maior_que_ultimo'].mean()),
                'menor_que_ultimo_media': float(pares['menor_que_ultimo'].mean())
            },
            'impares': {
                'maior_que_ultimo_media': float(impares['maior_que_ultimo'].mean()),
                'menor_que_ultimo_media': float(impares['menor_que_ultimo'].mean())
            },
            'diferencas': {
                'maior_que_ultimo': float(dif_maior),
                'menor_que_ultimo': float(dif_menor)
            }
        }
    
    def analisar_outros_finais(self):
        """🔍 Análise de todos os finais (0-9)"""
        print("\n🔍 ANÁLISE DE TODOS OS FINAIS (0-9)")
        print("=" * 40)
        
        finais_stats = {}
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        for final in range(10):
            dados_final = self.dados[self.dados['Concurso'] % 10 == final]
            quantidade = len(dados_final)
            
            if quantidade > 0:
                # Calcula estatísticas básicas
                soma_total_media = 0
                numeros_mais_frequentes = {}
                
                for col in numeros_cols:
                    valores = dados_final[col].dropna().tolist()
                    soma_total_media += np.mean(valores) if valores else 0
                    
                    counter = Counter(valores)
                    for num, freq in counter.items():
                        if num not in numeros_mais_frequentes:
                            numeros_mais_frequentes[num] = 0
                        numeros_mais_frequentes[num] += freq
                
                # Normaliza frequências
                for num in numeros_mais_frequentes:
                    numeros_mais_frequentes[num] /= quantidade
                
                top_3 = sorted(numeros_mais_frequentes.items(), 
                             key=lambda x: x[1], reverse=True)[:3]
                
                finais_stats[final] = {
                    'quantidade': quantidade,
                    'soma_total_media': soma_total_media,
                    'top_3_numeros': top_3
                }
                
                print(f"\n📊 FINAL {final}: {quantidade} concursos")
                print(f"   Soma média das posições: {soma_total_media:.1f}")
                print(f"   Top 3 números: {', '.join([f'{n}({f:.3f})' for n, f in top_3])}")
        
        self.resultados['todos_finais'] = finais_stats
    
    def gerar_relatorio_final(self):
        """📋 Gera relatório final com todos os insights"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL - INSIGHTS DESCOBERTOS")
        print("=" * 60)
        
        # Insights de paridade
        print("\n🔢 INSIGHTS - PARIDADE DE CONCURSOS:")
        if 'paridade' in self.resultados:
            top_pares = self.resultados['paridade']['top_preferem_pares'][:3]
            top_impares = self.resultados['paridade']['top_preferem_impares'][:3]
            
            print(f"   🎯 Números que preferem concursos PARES: "
                  f"{', '.join([str(x[0]) for x in top_pares])}")
            print(f"   🎯 Números que preferem concursos ÍMPARES: "
                  f"{', '.join([str(x[0]) for x in top_impares])}")
        
        # Insights de finais específicos
        print("\n🎯 INSIGHTS - FINAIS ESPECÍFICOS:")
        if 'finais_especificos' in self.resultados:
            final_0_top = self.resultados['finais_especificos']['final_0']['top_10'][:3]
            final_5_top = self.resultados['finais_especificos']['final_5']['top_10'][:3]
            
            print(f"   🎯 Final 0 - Top 3: {', '.join([str(x[0]) for x in final_0_top])}")
            print(f"   🎯 Final 5 - Top 3: {', '.join([str(x[0]) for x in final_5_top])}")
        
        # Insights de campos comparativos
        print("\n📊 INSIGHTS - CAMPOS COMPARATIVOS:")
        if 'campos_comparativos' in self.resultados:
            difs = self.resultados['campos_comparativos']['diferencas']
            print(f"   🔼 Maior que último: pares têm {difs['maior_que_ultimo']:+.3f} a mais")
            print(f"   🔽 Menor que último: pares têm {difs['menor_que_ultimo']:+.3f} a mais")
        
        # Conclusão sobre utilidade
        print("\n💡 AVALIAÇÃO DE UTILIDADE:")
        
        # Verifica se há padrões significativos
        padroes_significativos = []
        
        if 'paridade' in self.resultados:
            for num, data in self.resultados['paridade']['frequencias_detalhadas'].items():
                if abs(data['diferenca']) > 0.02:  # Diferença > 2%
                    padroes_significativos.append(f"Número {num} - paridade")
        
        if 'campos_comparativos' in self.resultados:
            difs = self.resultados['campos_comparativos']['diferencas']
            if abs(difs['maior_que_ultimo']) > 0.1:
                padroes_significativos.append("Campo maior_que_ultimo - paridade")
            if abs(difs['menor_que_ultimo']) > 0.1:
                padroes_significativos.append("Campo menor_que_ultimo - paridade")
        
        if padroes_significativos:
            print(f"   ✅ {len(padroes_significativos)} padrões significativos encontrados!")
            print("   📈 RECOMENDAÇÃO: Integrar ao sistema principal")
            for padrao in padroes_significativos[:3]:
                print(f"      • {padrao}")
        else:
            print("   ⚠️ Padrões encontrados são sutis (< 2% diferença)")
            print("   📊 RECOMENDAÇÃO: Limpar teste - não justifica integração")
        
        return len(padroes_significativos) > 0
    
    def salvar_resultados(self):
        """💾 Salva resultados em arquivo JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"analise_padroes_rapida_{timestamp}.json"
        
        resultado_completo = {
            'timestamp': timestamp,
            'resumo': {
                'total_concursos_analisados': len(self.dados),
                'range_concursos': f"{self.dados['Concurso'].min()} a {self.dados['Concurso'].max()}",
                'analises_realizadas': list(self.resultados.keys())
            },
            'dados': self.resultados
        }
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado_completo, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {nome_arquivo}")
        return nome_arquivo
    
    def executar_analise_completa(self):
        """🚀 Executa análise completa"""
        print("🔍 ANALISADOR DE PADRÕES RÁPIDO - LOTOFÁCIL")
        print("=" * 50)
        
        if not self.conectar_banco():
            return False
        
        if not self.carregar_dados():
            return False
        
        # Executa todas as análises
        self.analisar_padroes_paridade()
        self.analisar_finais_especificos()
        self.analisar_campos_comparativos()
        self.analisar_outros_finais()
        
        # Gera relatório e avalia utilidade
        util = self.gerar_relatorio_final()
        
        # Salva resultados
        arquivo = self.salvar_resultados()
        
        print(f"\n🎯 CONCLUSÃO: {'ÚTIL - Integrar!' if util else 'Não útil - Limpar teste'}")
        
        return util

def main():
    """Função principal"""
    analisador = AnalisadorPadroesRapido()
    return analisador.executar_analise_completa()

if __name__ == "__main__":
    main()