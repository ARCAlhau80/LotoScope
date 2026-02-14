#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔬 BENCHMARK MULTI-CONCURSO DE RANGE
Testa qual range é melhor validando contra MÚLTIPLOS concursos

Autor: LotoScope AI
Data: Dezembro 2025
"""

import sys
import random
from pathlib import Path
from typing import List, Set, Dict, Tuple
from collections import Counter
from datetime import datetime
import statistics

# Configurar paths
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config


class BenchmarkMultiConcurso:
    """
    Benchmark que testa múltiplos concursos como validação.
    """
    
    def __init__(self):
        self.todos_resultados = []
        
        # Ranges a testar
        self.ranges = [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
                       75, 100, 150, 200, 300, 500]
        
        print("🔬 BENCHMARK MULTI-CONCURSO DE RANGE")
        print("=" * 60)
        self._carregar_dados()
    
    def _carregar_dados(self):
        """Carrega últimos N concursos para validação"""
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            # Pegar últimos 100 concursos
            cursor.execute("""
                SELECT TOP 100 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT ORDER BY Concurso DESC
            """)
            
            for row in cursor.fetchall():
                self.todos_resultados.append({
                    'concurso': row[0],
                    'numeros': set(row[1:])
                })
            
            cursor.close()
            conn.close()
            
            print(f"📚 Concursos carregados: {len(self.todos_resultados)}")
            print(f"📊 Do concurso {self.todos_resultados[-1]['concurso']} "
                  f"até {self.todos_resultados[0]['concurso']}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def _calcular_frequencia(self, concurso_validacao: int, 
                              range_concursos: int) -> Dict[int, int]:
        """Calcula frequência nos N concursos ANTES do concurso de validação"""
        freq = {i: 0 for i in range(1, 26)}
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT TOP {range_concursos} N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT 
                WHERE Concurso < ?
                ORDER BY Concurso DESC
            """, (concurso_validacao,))
            
            for row in cursor.fetchall():
                for num in row:
                    if num in freq:
                        freq[num] += 1
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return freq
    
    def _gerar_combinacao(self, freq: Dict[int, int], 
                          num_quentes: int = 12) -> Set[int]:
        """Gera combinação com N números quentes"""
        ordenados = sorted(freq.items(), key=lambda x: -x[1])
        quentes = [n for n, _ in ordenados[:15]]
        frios = [n for n, _ in ordenados[15:]]
        
        numeros = set()
        random.shuffle(quentes)
        numeros.update(quentes[:num_quentes])
        
        random.shuffle(frios)
        while len(numeros) < 15:
            numeros.add(frios.pop())
        
        return numeros
    
    def testar_range_multi(self, range_concursos: int, 
                           num_concursos_validacao: int = 30,
                           num_combinacoes: int = 50) -> Dict:
        """Testa um range contra múltiplos concursos"""
        
        todos_acertos = []
        acertos_11_mais = 0
        acertos_12_mais = 0
        acertos_13_mais = 0
        acertos_14_mais = 0
        acertos_15 = 0
        
        # Pegar concursos para validação (pula os primeiros que são muito recentes)
        concursos_val = self.todos_resultados[:num_concursos_validacao]
        
        for resultado in concursos_val:
            concurso = resultado['concurso']
            numeros_real = resultado['numeros']
            
            # Calcular frequência antes deste concurso
            freq = self._calcular_frequencia(concurso, range_concursos)
            
            # Gerar combinações
            for _ in range(num_combinacoes):
                comb = self._gerar_combinacao(freq)
                acertos = len(comb & numeros_real)
                todos_acertos.append(acertos)
                
                if acertos >= 11: acertos_11_mais += 1
                if acertos >= 12: acertos_12_mais += 1
                if acertos >= 13: acertos_13_mais += 1
                if acertos >= 14: acertos_14_mais += 1
                if acertos == 15: acertos_15 += 1
        
        total = len(todos_acertos)
        
        return {
            'range': range_concursos,
            'media': statistics.mean(todos_acertos),
            'mediana': statistics.median(todos_acertos),
            'melhor': max(todos_acertos),
            'pior': min(todos_acertos),
            'taxa_11': (acertos_11_mais / total) * 100,
            'taxa_12': (acertos_12_mais / total) * 100,
            'taxa_13': (acertos_13_mais / total) * 100,
            'taxa_14': (acertos_14_mais / total) * 100,
            'taxa_15': (acertos_15 / total) * 100,
            'total_testes': total
        }
    
    def executar_benchmark(self, num_concursos_validacao: int = 30,
                           num_combinacoes: int = 50):
        """Executa benchmark completo"""
        
        print()
        print(f"🔬 Testando {len(self.ranges)} ranges")
        print(f"📊 Validando contra {num_concursos_validacao} concursos")
        print(f"🎲 {num_combinacoes} combinações por concurso")
        print(f"📈 Total de testes por range: {num_concursos_validacao * num_combinacoes}")
        print("=" * 90)
        print()
        
        resultados = []
        
        for i, rng in enumerate(self.ranges, 1):
            print(f"[{i}/{len(self.ranges)}] Range {rng}...", end=" ", flush=True)
            resultado = self.testar_range_multi(rng, num_concursos_validacao, num_combinacoes)
            resultados.append(resultado)
            print(f"Média: {resultado['media']:.2f} | "
                  f"11+: {resultado['taxa_11']:.1f}% | "
                  f"13+: {resultado['taxa_13']:.1f}%")
        
        # Ordenar por média
        resultados_ordenados = sorted(resultados, key=lambda x: -x['media'])
        
        print()
        print("=" * 90)
        print("📊 RANKING FINAL - MÉDIA DE ACERTOS POR RANGE")
        print("=" * 90)
        
        print()
        print(f"{'Rank':<5} {'Range':<8} {'Média':<8} {'Mediana':<8} "
              f"{'11+%':<8} {'12+%':<8} {'13+%':<8} {'14+%':<8} {'Melhor':<8}")
        print("-" * 90)
        
        for i, r in enumerate(resultados_ordenados, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{emoji}{i:<3} {r['range']:<8} {r['media']:<8.2f} {r['mediana']:<8.1f} "
                  f"{r['taxa_11']:<8.1f} {r['taxa_12']:<8.1f} {r['taxa_13']:<8.1f} "
                  f"{r['taxa_14']:<8.1f} {r['melhor']:<8}")
        
        # Análise do melhor
        melhor = resultados_ordenados[0]
        
        print()
        print("=" * 90)
        print(f"🏆 MELHOR RANGE ESTATÍSTICO: {melhor['range']} concursos")
        print(f"   📊 Média de acertos: {melhor['media']:.2f}")
        print(f"   📈 Taxa 11+: {melhor['taxa_11']:.1f}%")
        print(f"   📈 Taxa 12+: {melhor['taxa_12']:.1f}%")
        print(f"   📈 Taxa 13+: {melhor['taxa_13']:.1f}%")
        print(f"   🎯 Melhor resultado: {melhor['melhor']} acertos")
        print("=" * 90)
        
        # Análise por foco em 13+
        melhor_13 = max(resultados, key=lambda x: x['taxa_13'])
        
        print()
        print(f"🎯 MELHOR RANGE PARA 13+ ACERTOS: {melhor_13['range']} concursos")
        print(f"   📈 Taxa 13+: {melhor_13['taxa_13']:.2f}%")
        print(f"   📈 Taxa 14+: {melhor_13['taxa_14']:.2f}%")
        
        return resultados_ordenados


def main():
    print()
    print("🔬" * 30)
    print("  BENCHMARK MULTI-CONCURSO DE RANGE")
    print("🔬" * 30)
    print()
    
    benchmark = BenchmarkMultiConcurso()
    
    try:
        qtd_conc = input("\n📊 Quantos concursos para validação? [30]: ").strip()
        num_conc = int(qtd_conc) if qtd_conc else 30
        
        qtd_comb = input("🎲 Quantas combinações por concurso? [50]: ").strip()
        num_comb = int(qtd_comb) if qtd_comb else 50
    except:
        num_conc = 30
        num_comb = 50
    
    resultados = benchmark.executar_benchmark(num_conc, num_comb)
    
    print()
    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
