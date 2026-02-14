#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔬 BENCHMARK OTIMIZADO DE RANGE
Testa qual range é melhor - versão otimizada com cache

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


class BenchmarkRangeOtimizado:
    """
    Benchmark otimizado - carrega tudo em memória.
    """
    
    def __init__(self):
        self.todos_concursos = []  # Lista de (concurso, numeros)
        
        # Ranges a testar
        self.ranges = [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
                       75, 100, 150, 200, 300, 500, 1000]
        
        print("🔬 BENCHMARK OTIMIZADO DE RANGE")
        print("=" * 60)
        self._carregar_tudo()
    
    def _carregar_tudo(self):
        """Carrega TODOS os concursos em memória"""
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT ORDER BY Concurso DESC
            """)
            
            for row in cursor.fetchall():
                self.todos_concursos.append({
                    'concurso': row[0],
                    'numeros': set(row[1:])
                })
            
            cursor.close()
            conn.close()
            
            print(f"📚 {len(self.todos_concursos)} concursos carregados em memória")
            print(f"📊 Do {self.todos_concursos[-1]['concurso']} ao {self.todos_concursos[0]['concurso']}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def _calcular_frequencia_memoria(self, idx_validacao: int, range_concursos: int) -> Dict[int, int]:
        """
        Calcula frequência dos N concursos ANTES do índice de validação.
        idx_validacao = 0 significa o mais recente (3572)
        """
        freq = {i: 0 for i in range(1, 26)}
        
        # Pegar os próximos N concursos após idx_validacao
        inicio = idx_validacao + 1
        fim = min(inicio + range_concursos, len(self.todos_concursos))
        
        for i in range(inicio, fim):
            for num in self.todos_concursos[i]['numeros']:
                freq[num] += 1
        
        return freq
    
    def _gerar_combinacao(self, freq: Dict[int, int], num_quentes: int = 12) -> Set[int]:
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
    
    def testar_range(self, range_concursos: int, 
                     num_concursos_validacao: int = 50,
                     num_combinacoes: int = 100) -> Dict:
        """Testa um range contra múltiplos concursos"""
        
        todos_acertos = []
        
        # Testar contra os primeiros N concursos (mais recentes)
        for idx in range(num_concursos_validacao):
            # Verificar se temos concursos suficientes
            if idx + range_concursos >= len(self.todos_concursos):
                break
            
            numeros_real = self.todos_concursos[idx]['numeros']
            freq = self._calcular_frequencia_memoria(idx, range_concursos)
            
            for _ in range(num_combinacoes):
                comb = self._gerar_combinacao(freq)
                acertos = len(comb & numeros_real)
                todos_acertos.append(acertos)
        
        if not todos_acertos:
            return None
        
        total = len(todos_acertos)
        
        return {
            'range': range_concursos,
            'media': statistics.mean(todos_acertos),
            'mediana': statistics.median(todos_acertos),
            'melhor': max(todos_acertos),
            'pior': min(todos_acertos),
            'taxa_11': sum(1 for a in todos_acertos if a >= 11) / total * 100,
            'taxa_12': sum(1 for a in todos_acertos if a >= 12) / total * 100,
            'taxa_13': sum(1 for a in todos_acertos if a >= 13) / total * 100,
            'taxa_14': sum(1 for a in todos_acertos if a >= 14) / total * 100,
            'taxa_15': sum(1 for a in todos_acertos if a == 15) / total * 100,
            'total_testes': total
        }
    
    def executar_benchmark(self, num_concursos_validacao: int = 50,
                           num_combinacoes: int = 100):
        """Executa benchmark completo"""
        
        total_testes = num_concursos_validacao * num_combinacoes
        
        print()
        print(f"🔬 Testando {len(self.ranges)} ranges")
        print(f"📊 Validando contra {num_concursos_validacao} concursos")
        print(f"🎲 {num_combinacoes} combinações por concurso")
        print(f"📈 Total de testes por range: {total_testes}")
        print("=" * 90)
        print()
        
        resultados = []
        
        for i, rng in enumerate(self.ranges, 1):
            print(f"[{i}/{len(self.ranges)}] Range {rng}...", end=" ", flush=True)
            resultado = self.testar_range(rng, num_concursos_validacao, num_combinacoes)
            
            if resultado:
                resultados.append(resultado)
                print(f"Média: {resultado['media']:.2f} | "
                      f"11+: {resultado['taxa_11']:.1f}% | "
                      f"13+: {resultado['taxa_13']:.2f}%")
            else:
                print("SKIP (poucos dados)")
        
        # Ordenar por média
        resultados_media = sorted(resultados, key=lambda x: -x['media'])
        resultados_13 = sorted(resultados, key=lambda x: -x['taxa_13'])
        
        print()
        print("=" * 90)
        print("📊 RANKING POR MÉDIA DE ACERTOS")
        print("=" * 90)
        
        print()
        print(f"{'Rank':<5} {'Range':<8} {'Média':<8} {'Mediana':<8} "
              f"{'11+%':<8} {'12+%':<8} {'13+%':<8} {'14+%':<8} {'Melhor':<8}")
        print("-" * 90)
        
        for i, r in enumerate(resultados_media[:10], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{emoji}{i:<3} {r['range']:<8} {r['media']:<8.2f} {r['mediana']:<8.1f} "
                  f"{r['taxa_11']:<8.1f} {r['taxa_12']:<8.1f} {r['taxa_13']:<8.2f} "
                  f"{r['taxa_14']:<8.2f} {r['melhor']:<8}")
        
        print()
        print("=" * 90)
        print("🎯 RANKING POR TAXA DE 13+ ACERTOS")
        print("=" * 90)
        
        print()
        for i, r in enumerate(resultados_13[:10], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{emoji}{i:<3} Range {r['range']:<6} → 13+: {r['taxa_13']:<6.2f}% | "
                  f"14+: {r['taxa_14']:<6.2f}% | Média: {r['media']:.2f}")
        
        # Conclusão
        melhor_media = resultados_media[0]
        melhor_13 = resultados_13[0]
        
        print()
        print("=" * 90)
        print("🏆 CONCLUSÃO")
        print("=" * 90)
        print()
        print(f"📊 MELHOR RANGE PARA MÉDIA DE ACERTOS: {melhor_media['range']} concursos")
        print(f"   → Média: {melhor_media['media']:.2f} acertos")
        print()
        print(f"🎯 MELHOR RANGE PARA 13+ ACERTOS: {melhor_13['range']} concursos")
        print(f"   → Taxa 13+: {melhor_13['taxa_13']:.2f}%")
        print(f"   → Taxa 14+: {melhor_13['taxa_14']:.2f}%")
        print("=" * 90)
        
        return resultados_media


def main():
    print()
    print("🔬" * 30)
    print("  BENCHMARK OTIMIZADO DE RANGE")
    print("🔬" * 30)
    print()
    
    benchmark = BenchmarkRangeOtimizado()
    
    try:
        qtd_conc = input("\n📊 Quantos concursos para validação? [50]: ").strip()
        num_conc = int(qtd_conc) if qtd_conc else 50
        
        qtd_comb = input("🎲 Quantas combinações por concurso? [100]: ").strip()
        num_comb = int(qtd_comb) if qtd_comb else 100
    except:
        num_conc = 50
        num_comb = 100
    
    resultados = benchmark.executar_benchmark(num_conc, num_comb)
    
    print()
    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
