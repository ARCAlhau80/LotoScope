#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧮 ANALISADOR DE DISTRIBUIÇÕES ESPECIAIS
=======================================
Análise de padrões matemáticos não-óbvios: Fibonacci, primos, quadrados perfeitos,
triangulares, somas mágicas e outros padrões matemáticos ocultos
"""

import pyodbc
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
import json
import math
from typing import List, Dict, Set, Tuple

# Importa configuração de banco existente
try:
    from database_optimizer import get_optimized_connection
    USE_OPTIMIZER = True
except ImportError:
    USE_OPTIMIZER = None

class AnalisadorDistribuicoesEspeciais:
    """🧮 Analisador de padrões matemáticos especiais"""
    
    def __init__(self):
        self.conexao = None
        self.dados = None
        self.padroes_matematicos = {}
        self.descobertas_especiais = []
        
        # Define sequências matemáticas especiais até 25
        self.fibonacci = self._gerar_fibonacci(25)
        self.primos = self._gerar_primos(25)
        self.quadrados_perfeitos = self._gerar_quadrados_perfeitos(25)
        self.triangulares = self._gerar_triangulares(25)
        self.pentagonais = self._gerar_pentagonais(25)
        
    def _gerar_fibonacci(self, limite: int) -> Set[int]:
        """🌀 Gera números de Fibonacci até o limite"""
        fib = {1, 1, 2, 3, 5, 8, 13, 21}
        return {f for f in fib if f <= limite}
    
    def _gerar_primos(self, limite: int) -> Set[int]:
        """🔢 Gera números primos até o limite"""
        primos = set()
        for num in range(2, limite + 1):
            if all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1)):
                primos.add(num)
        return primos
    
    def _gerar_quadrados_perfeitos(self, limite: int) -> Set[int]:
        """🔳 Gera quadrados perfeitos até o limite"""
        return {i*i for i in range(1, int(math.sqrt(limite)) + 1)}
    
    def _gerar_triangulares(self, limite: int) -> Set[int]:
        """🔺 Gera números triangulares até o limite"""
        triangulares = set()
        n = 1
        while True:
            tri = n * (n + 1) // 2
            if tri > limite:
                break
            triangulares.add(tri)
            n += 1
        return triangulares
    
    def _gerar_pentagonais(self, limite: int) -> Set[int]:
        """⬟ Gera números pentagonais até o limite"""
        pentagonais = set()
        n = 1
        while True:
            pent = n * (3*n - 1) // 2
            if pent > limite:
                break
            pentagonais.add(pent)
            n += 1
        return pentagonais
    
    def conectar_banco(self) -> bool:
        """🔌 Conecta ao banco ou gera dados sintéticos"""
        try:
            if USE_OPTIMIZER:
                self.conexao = get_optimized_connection()
                print("✅ Conectado via optimizer")
                return True
        except Exception as e:
            print(f"⚠️ Optimizer falhou: {e}")
        
        try:
            connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=DESKTOP-K6JPBDS\\SQLEXPRESS;"
                "DATABASE=LotofacilDB;"
                "Trusted_Connection=yes;"
                "MARS_Connection=Yes;"
            )
            self.conexao = pyodbc.connect(connection_string)
            print("✅ Conectado diretamente")
            return True
        except Exception as e:
            print(f"⚠️ Conexão direta falhou: {e}")
            return self._gerar_dados_sinteticos()
    
    def _gerar_dados_sinteticos(self) -> bool:
        """🎲 Gera dados sintéticos baseados em padrões interessantes"""
        try:
            import random
            
            print("🔄 Gerando dados sintéticos com padrões matemáticos...")
            
            dados_sinteticos = []
            for concurso in range(1, 1001):  # 1000 concursos
                # 70% aleatório + 30% com viés para padrões matemáticos
                if random.random() < 0.3:
                    # Adiciona viés para números especiais
                    candidatos = list(range(1, 26))
                    
                    # Favorece Fibonacci e primos
                    for _ in range(3):  # Triplica chance
                        candidatos.extend(self.fibonacci)
                        candidatos.extend(self.primos)
                    
                    # Favorece quadrados perfeitos moderadamente
                    candidatos.extend(self.quadrados_perfeitos)
                    
                    numeros = sorted(random.sample(candidatos, 15))
                    while len(set(numeros)) < 15:  # Garante 15 únicos
                        numeros = sorted(random.sample(candidatos, 15))
                    numeros = sorted(list(set(numeros))[:15])
                else:
                    # Completamente aleatório
                    numeros = sorted(random.sample(range(1, 26), 15))
                
                row = {'Concurso': concurso}
                for i, num in enumerate(numeros):
                    row[f'N{i+1}'] = num
                
                dados_sinteticos.append(row)
            
            self.dados = pd.DataFrame(dados_sinteticos)
            print(f"✅ Dados sintéticos gerados: {len(self.dados)} concursos")
            print("⚠️ ATENÇÃO: Dados SINTÉTICOS com viés matemático para demonstração")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar dados sintéticos: {e}")
            return False
    
    def carregar_dados(self) -> bool:
        """📊 Carrega dados do banco"""
        if hasattr(self, 'dados') and self.dados is not None:
            return True  # Dados sintéticos já carregados
            
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
            print(f"📊 Carregados {len(self.dados)} concursos reais")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analisar_fibonacci(self):
        """🌀 Análise de padrões Fibonacci"""
        print("\n🌀 ANÁLISE DE NÚMEROS DE FIBONACCI")
        print("=" * 37)
        print(f"   Fibonacci até 25: {sorted(self.fibonacci)}")
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        total_concursos = len(self.dados)
        fibonacci_stats = {
            'total_aparicoes': 0,
            'concursos_com_fibonacci': 0,
            'media_por_concurso': 0,
            'max_por_concurso': 0,
            'distribuicao_quantidade': Counter()
        }
        
        for idx, row in self.dados.iterrows():
            numeros_fibonacci_no_concurso = 0
            for col in numeros_cols:
                if pd.notna(row[col]) and int(row[col]) in self.fibonacci:
                    numeros_fibonacci_no_concurso += 1
                    fibonacci_stats['total_aparicoes'] += 1
            
            if numeros_fibonacci_no_concurso > 0:
                fibonacci_stats['concursos_com_fibonacci'] += 1
            
            fibonacci_stats['distribuicao_quantidade'][numeros_fibonacci_no_concurso] += 1
            fibonacci_stats['max_por_concurso'] = max(fibonacci_stats['max_por_concurso'], 
                                                     numeros_fibonacci_no_concurso)
        
        fibonacci_stats['media_por_concurso'] = fibonacci_stats['total_aparicoes'] / total_concursos
        porcentagem_concursos = (fibonacci_stats['concursos_com_fibonacci'] / total_concursos) * 100
        
        print(f"   📊 Estatísticas:")
        print(f"      • Total de aparições: {fibonacci_stats['total_aparicoes']}")
        print(f"      • Concursos com Fibonacci: {fibonacci_stats['concursos_com_fibonacci']} ({porcentagem_concursos:.1f}%)")
        print(f"      • Média por concurso: {fibonacci_stats['media_por_concurso']:.2f}")
        print(f"      • Máximo por concurso: {fibonacci_stats['max_por_concurso']}")
        
        # Análise da distribuição
        print(f"\n   🎯 Distribuição por concurso:")
        for qtd in range(fibonacci_stats['max_por_concurso'] + 1):
            freq = fibonacci_stats['distribuicao_quantidade'][qtd]
            if freq > 0:
                pct = (freq / total_concursos) * 100
                print(f"      • {qtd} Fibonacci: {freq} concursos ({pct:.1f}%)")
        
        # Verifica se há padrão significativo
        esperado_aleatorio = len(self.fibonacci) / 25 * 15  # Esperado aleatório
        if abs(fibonacci_stats['media_por_concurso'] - esperado_aleatorio) > esperado_aleatorio * 0.2:
            significancia = "ALTA" if fibonacci_stats['media_por_concurso'] > esperado_aleatorio else "BAIXA"
            self.descobertas_especiais.append({
                'tipo': 'fibonacci',
                'significancia': significancia,
                'observado': fibonacci_stats['media_por_concurso'],
                'esperado': esperado_aleatorio,
                'diferenca_pct': ((fibonacci_stats['media_por_concurso'] - esperado_aleatorio) / esperado_aleatorio) * 100
            })
            print(f"   🚨 PADRÃO DETECTADO: Fibonacci aparece {significancia} frequência!")
        
        self.padroes_matematicos['fibonacci'] = fibonacci_stats
    
    def analisar_primos(self):
        """🔢 Análise de números primos"""
        print("\n🔢 ANÁLISE DE NÚMEROS PRIMOS")
        print("=" * 32)
        print(f"   Primos até 25: {sorted(self.primos)}")
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        total_concursos = len(self.dados)
        primos_stats = {
            'total_aparicoes': 0,
            'concursos_com_primos': 0,
            'media_por_concurso': 0,
            'max_por_concurso': 0,
            'distribuicao_quantidade': Counter(),
            'primos_individuais': Counter()
        }
        
        for idx, row in self.dados.iterrows():
            numeros_primos_no_concurso = 0
            for col in numeros_cols:
                if pd.notna(row[col]) and int(row[col]) in self.primos:
                    numero = int(row[col])
                    numeros_primos_no_concurso += 1
                    primos_stats['total_aparicoes'] += 1
                    primos_stats['primos_individuais'][numero] += 1
            
            if numeros_primos_no_concurso > 0:
                primos_stats['concursos_com_primos'] += 1
            
            primos_stats['distribuicao_quantidade'][numeros_primos_no_concurso] += 1
            primos_stats['max_por_concurso'] = max(primos_stats['max_por_concurso'], 
                                                  numeros_primos_no_concurso)
        
        primos_stats['media_por_concurso'] = primos_stats['total_aparicoes'] / total_concursos
        
        print(f"   📊 Estatísticas:")
        print(f"      • Média por concurso: {primos_stats['media_por_concurso']:.2f}")
        print(f"      • Máximo por concurso: {primos_stats['max_por_concurso']}")
        
        # Primos mais frequentes
        print(f"\n   🎯 Primos mais frequentes:")
        for primo, freq in primos_stats['primos_individuais'].most_common(5):
            pct = (freq / total_concursos) * 100
            print(f"      • {primo}: {freq} aparições ({pct:.1f}%)")
        
        esperado_aleatorio = len(self.primos) / 25 * 15
        if abs(primos_stats['media_por_concurso'] - esperado_aleatorio) > esperado_aleatorio * 0.2:
            significancia = "ALTA" if primos_stats['media_por_concurso'] > esperado_aleatorio else "BAIXA"
            self.descobertas_especiais.append({
                'tipo': 'primos',
                'significancia': significancia,
                'observado': primos_stats['media_por_concurso'],
                'esperado': esperado_aleatorio,
                'diferenca_pct': ((primos_stats['media_por_concurso'] - esperado_aleatorio) / esperado_aleatorio) * 100
            })
            print(f"   🚨 PADRÃO DETECTADO: Primos com frequência {significancia}!")
        
        self.padroes_matematicos['primos'] = primos_stats
    
    def analisar_quadrados_perfeitos(self):
        """🔳 Análise de quadrados perfeitos"""
        print("\n🔳 ANÁLISE DE QUADRADOS PERFEITOS")
        print("=" * 36)
        print(f"   Quadrados até 25: {sorted(self.quadrados_perfeitos)}")
        
        self._analisar_sequencia_generica('quadrados_perfeitos', self.quadrados_perfeitos)
    
    def analisar_triangulares(self):
        """🔺 Análise de números triangulares"""
        print("\n🔺 ANÁLISE DE NÚMEROS TRIANGULARES")
        print("=" * 37)
        print(f"   Triangulares até 25: {sorted(self.triangulares)}")
        
        self._analisar_sequencia_generica('triangulares', self.triangulares)
    
    def _analisar_sequencia_generica(self, nome: str, sequencia: Set[int]):
        """🔍 Análise genérica para qualquer sequência"""
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        total_concursos = len(self.dados)
        stats = {
            'total_aparicoes': 0,
            'media_por_concurso': 0,
            'max_por_concurso': 0,
            'distribuicao_quantidade': Counter()
        }
        
        for idx, row in self.dados.iterrows():
            count_no_concurso = 0
            for col in numeros_cols:
                if pd.notna(row[col]) and int(row[col]) in sequencia:
                    count_no_concurso += 1
                    stats['total_aparicoes'] += 1
            
            stats['distribuicao_quantidade'][count_no_concurso] += 1
            stats['max_por_concurso'] = max(stats['max_por_concurso'], count_no_concurso)
        
        stats['media_por_concurso'] = stats['total_aparicoes'] / total_concursos
        
        print(f"   📊 Média por concurso: {stats['media_por_concurso']:.2f}")
        print(f"   🎯 Máximo por concurso: {stats['max_por_concurso']}")
        
        esperado = len(sequencia) / 25 * 15
        if abs(stats['media_por_concurso'] - esperado) > esperado * 0.3:
            significancia = "ALTA" if stats['media_por_concurso'] > esperado else "BAIXA"
            self.descobertas_especiais.append({
                'tipo': nome,
                'significancia': significancia,
                'observado': stats['media_por_concurso'],
                'esperado': esperado,
                'diferenca_pct': ((stats['media_por_concurso'] - esperado) / esperado) * 100
            })
            print(f"   🚨 PADRÃO DETECTADO: {nome} com frequência {significancia}!")
        
        self.padroes_matematicos[nome] = stats
    
    def analisar_somas_especiais(self):
        """🧮 Análise de somas com propriedades especiais"""
        print("\n🧮 ANÁLISE DE SOMAS ESPECIAIS")
        print("=" * 32)
        
        numeros_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                       'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
        
        somas_especiais = {
            'multiplos_7': 0,
            'multiplos_11': 0,
            'multiplos_13': 0,
            'potencias_2': 0,
            'entre_200_250': 0,
            'palindromicas': 0  # Somas que são palíndromas
        }
        
        total_concursos = len(self.dados)
        
        for idx, row in self.dados.iterrows():
            numeros = [int(row[col]) for col in numeros_cols if pd.notna(row[col])]
            if len(numeros) == 15:
                soma = sum(numeros)
                
                # Múltiplos especiais
                if soma % 7 == 0:
                    somas_especiais['multiplos_7'] += 1
                if soma % 11 == 0:
                    somas_especiais['multiplos_11'] += 1
                if soma % 13 == 0:
                    somas_especiais['multiplos_13'] += 1
                
                # Potências de 2
                if soma in {128, 256, 512}:  # Potências de 2 na faixa típica
                    somas_especiais['potencias_2'] += 1
                
                # Faixa especial
                if 200 <= soma <= 250:
                    somas_especiais['entre_200_250'] += 1
                
                # Palindrômicas (soma lida igual de trás pra frente)
                if str(soma) == str(soma)[::-1]:
                    somas_especiais['palindromicas'] += 1
        
        print("   📊 Frequências especiais:")
        for tipo, freq in somas_especiais.items():
            pct = (freq / total_concursos) * 100
            print(f"      • {tipo.replace('_', ' ').title()}: {freq} ({pct:.1f}%)")
            
            # Verifica significância (acima de 5% pode ser interessante)
            if pct > 5:
                self.descobertas_especiais.append({
                    'tipo': f'soma_{tipo}',
                    'significancia': 'ALTA',
                    'frequencia': freq,
                    'porcentagem': pct
                })
        
        self.padroes_matematicos['somas_especiais'] = somas_especiais
    
    def gerar_relatorio_distribuicoes(self):
        """📋 Gera relatório final de distribuições"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE DISTRIBUIÇÕES MATEMÁTICAS ESPECIAIS")
        print("="*60)
        
        print(f"\n📊 RESUMO DAS ANÁLISES:")
        print(f"   • {len(self.padroes_matematicos)} tipos de padrões analisados")
        print(f"   • {len(self.descobertas_especiais)} descobertas significativas")
        
        if self.descobertas_especiais:
            print(f"\n🚨 DESCOBERTAS SIGNIFICATIVAS:")
            for i, descoberta in enumerate(self.descobertas_especiais, 1):
                print(f"   {i}. {descoberta['tipo'].title()}: {descoberta['significancia']}")
                if 'diferenca_pct' in descoberta:
                    print(f"      Diferença: {descoberta['diferenca_pct']:+.1f}% do esperado")
        else:
            print(f"\n⚪ Nenhuma descoberta altamente significativa")
        
        # Salva resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        resultado = {
            'timestamp': timestamp,
            'padroes_matematicos': {
                k: {sk: (int(sv) if isinstance(sv, np.integer) else 
                        float(sv) if isinstance(sv, np.floating) else 
                        sv) for sk, sv in v.items() if sk != 'distribuicao_quantidade'}
                for k, v in self.padroes_matematicos.items()
            },
            'descobertas_especiais': self.descobertas_especiais,
            'sequencias_analisadas': {
                'fibonacci': list(self.fibonacci),
                'primos': list(self.primos),
                'quadrados_perfeitos': list(self.quadrados_perfeitos),
                'triangulares': list(self.triangulares)
            }
        }
        
        nome_arquivo = f"distribuicoes_especiais_{timestamp}.json"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {nome_arquivo}")
        
        # Avaliação final
        if len(self.descobertas_especiais) >= 3:
            print(f"\n✅ RECOMENDAÇÃO: Padrões matemáticos SIGNIFICATIVOS - Explorar mais!")
            return True
        elif len(self.descobertas_especiais) >= 1:
            print(f"\n📈 RECOMENDAÇÃO: Alguns padrões interessantes - Investigar")
            return True
        else:
            print(f"\n⚪ RECOMENDAÇÃO: Padrões dentro do esperado - Continuar pesquisa")
            return False
    
    def executar_analise_completa(self):
        """🚀 Executa análise completa de distribuições especiais"""
        print("🧮 ANALISADOR DE DISTRIBUIÇÕES MATEMÁTICAS ESPECIAIS")
        print("="*52)
        
        if not self.conectar_banco() or not self.carregar_dados():
            return False
        
        # Executa todas as análises
        self.analisar_fibonacci()
        self.analisar_primos()
        self.analisar_quadrados_perfeitos()
        self.analisar_triangulares()
        self.analisar_somas_especiais()
        
        # Gera relatório final
        return self.gerar_relatorio_distribuicoes()

def main():
    """Função principal"""
    analisador = AnalisadorDistribuicoesEspeciais()
    return analisador.executar_analise_completa()

if __name__ == "__main__":
    main()