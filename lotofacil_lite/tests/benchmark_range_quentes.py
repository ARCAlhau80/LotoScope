#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔬 BENCHMARK DE RANGE - ULTRA QUENTES
Testa qual quantidade de concursos anteriores é mais eficaz

Ranges testados: 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 
                 100, 300, 500, 700, 1000, 1500, 2000, 2500, TODOS

Validação: Último concurso da base (3572)
Treino: Até o penúltimo (3571)

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


class BenchmarkRangeQuentes:
    """
    Benchmark para encontrar o range ideal de concursos
    para calcular números quentes.
    """
    
    def __init__(self):
        self.concurso_validacao = None
        self.resultado_validacao = None
        self.total_concursos = None
        
        # Ranges a testar
        self.ranges = [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
                       75, 100, 150, 200, 300, 500, 700, 1000, 
                       1500, 2000, 2500, 3000]
        
        print("🔬 BENCHMARK DE RANGE - ULTRA QUENTES")
        print("=" * 60)
        self._carregar_dados()
    
    def _carregar_dados(self):
        """Carrega dados de validação"""
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            # Pegar último concurso para validação
            cursor.execute("""
                SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT ORDER BY Concurso DESC
            """)
            row = cursor.fetchone()
            self.concurso_validacao = row[0]
            self.resultado_validacao = set(row[1:])
            
            # Total de concursos disponíveis (excluindo validação)
            cursor.execute("SELECT COUNT(*) FROM RESULTADOS_INT WHERE Concurso < ?", 
                          (self.concurso_validacao,))
            self.total_concursos = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"📊 Concurso de validação: {self.concurso_validacao}")
            print(f"🎯 Resultado a acertar: {sorted(self.resultado_validacao)}")
            print(f"📚 Concursos disponíveis para treino: {self.total_concursos}")
            print()
            
            # Adicionar "TODOS" aos ranges
            self.ranges.append(self.total_concursos)
            # Filtrar ranges maiores que disponíveis
            self.ranges = [r for r in self.ranges if r <= self.total_concursos]
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
    
    def _calcular_frequencia(self, range_concursos: int) -> Dict[int, int]:
        """Calcula frequência dos números nos últimos N concursos antes da validação"""
        freq = {i: 0 for i in range(1, 26)}
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            # Pegar os últimos N concursos ANTES do concurso de validação
            cursor.execute(f"""
                SELECT TOP {range_concursos} N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT 
                WHERE Concurso < ?
                ORDER BY Concurso DESC
            """, (self.concurso_validacao,))
            
            for row in cursor.fetchall():
                for num in row:
                    if num in freq:
                        freq[num] += 1
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return freq
    
    def _gerar_combinacao_quente(self, freq: Dict[int, int], 
                                  num_quentes: int = 12) -> Set[int]:
        """Gera uma combinação baseada nos números mais quentes"""
        # Ordenar por frequência
        ordenados = sorted(freq.items(), key=lambda x: -x[1])
        quentes = [n for n, _ in ordenados[:15]]
        frios = [n for n, _ in ordenados[15:]]
        
        numeros = set()
        
        # Pegar N quentes
        random.shuffle(quentes)
        numeros.update(quentes[:num_quentes])
        
        # Completar com frios
        random.shuffle(frios)
        while len(numeros) < 15:
            numeros.add(frios.pop())
        
        return numeros
    
    def _contar_acertos(self, combinacao: Set[int]) -> int:
        """Conta quantos acertos a combinação teve"""
        return len(combinacao & self.resultado_validacao)
    
    def testar_range(self, range_concursos: int, 
                     num_combinacoes: int = 100,
                     num_quentes: int = 12) -> Dict:
        """Testa um range específico gerando várias combinações"""
        
        freq = self._calcular_frequencia(range_concursos)
        
        # Gerar combinações e contar acertos
        acertos_lista = []
        melhor_acertos = 0
        pior_acertos = 15
        
        for _ in range(num_combinacoes):
            comb = self._gerar_combinacao_quente(freq, num_quentes)
            acertos = self._contar_acertos(comb)
            acertos_lista.append(acertos)
            melhor_acertos = max(melhor_acertos, acertos)
            pior_acertos = min(pior_acertos, acertos)
        
        # Estatísticas
        media = statistics.mean(acertos_lista)
        mediana = statistics.median(acertos_lista)
        
        # Contagem por faixa
        contagem = Counter(acertos_lista)
        
        return {
            'range': range_concursos,
            'media': media,
            'mediana': mediana,
            'melhor': melhor_acertos,
            'pior': pior_acertos,
            'acertos_11_mais': sum(1 for a in acertos_lista if a >= 11),
            'acertos_12_mais': sum(1 for a in acertos_lista if a >= 12),
            'acertos_13_mais': sum(1 for a in acertos_lista if a >= 13),
            'acertos_14_mais': sum(1 for a in acertos_lista if a >= 14),
            'acertos_15': sum(1 for a in acertos_lista if a == 15),
            'distribuicao': dict(contagem),
            'total_combinacoes': num_combinacoes
        }
    
    def executar_benchmark_completo(self, num_combinacoes: int = 100):
        """Executa benchmark para todos os ranges"""
        
        print(f"🔬 Testando {len(self.ranges)} ranges diferentes")
        print(f"📊 {num_combinacoes} combinações por range")
        print(f"🎯 Validando contra concurso {self.concurso_validacao}")
        print("=" * 80)
        print()
        
        resultados = []
        
        for i, rng in enumerate(self.ranges, 1):
            label = "TODOS" if rng == self.total_concursos else str(rng)
            print(f"[{i}/{len(self.ranges)}] Testando range {label}...", end=" ", flush=True)
            
            resultado = self.testar_range(rng, num_combinacoes)
            resultados.append(resultado)
            
            print(f"Média: {resultado['media']:.2f} | "
                  f"13+: {resultado['acertos_13_mais']}% | "
                  f"Melhor: {resultado['melhor']}")
        
        print()
        print("=" * 80)
        print("📊 RESULTADO FINAL - RANKING POR MÉDIA DE ACERTOS")
        print("=" * 80)
        
        # Ordenar por média (decrescente)
        resultados_ordenados = sorted(resultados, key=lambda x: -x['media'])
        
        print()
        print(f"{'Rank':<5} {'Range':<10} {'Média':<8} {'Mediana':<8} "
              f"{'Melhor':<8} {'11+':<6} {'12+':<6} {'13+':<6} {'14+':<6}")
        print("-" * 80)
        
        for i, r in enumerate(resultados_ordenados, 1):
            label = "TODOS" if r['range'] == self.total_concursos else str(r['range'])
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            
            print(f"{emoji}{i:<3} {label:<10} {r['media']:<8.2f} {r['mediana']:<8.1f} "
                  f"{r['melhor']:<8} {r['acertos_11_mais']:<6} {r['acertos_12_mais']:<6} "
                  f"{r['acertos_13_mais']:<6} {r['acertos_14_mais']:<6}")
        
        # Melhor range
        melhor = resultados_ordenados[0]
        melhor_label = "TODOS" if melhor['range'] == self.total_concursos else str(melhor['range'])
        
        print()
        print("=" * 80)
        print(f"🏆 MELHOR RANGE: {melhor_label} concursos")
        print(f"   📊 Média de acertos: {melhor['media']:.2f}")
        print(f"   📈 Taxa 13+: {melhor['acertos_13_mais']}%")
        print(f"   🎯 Melhor resultado: {melhor['melhor']} acertos")
        print("=" * 80)
        
        # Análise detalhada do melhor
        self._mostrar_numeros_quentes(melhor['range'])
        
        return resultados_ordenados
    
    def _mostrar_numeros_quentes(self, range_concursos: int):
        """Mostra os números quentes do melhor range"""
        freq = self._calcular_frequencia(range_concursos)
        ordenados = sorted(freq.items(), key=lambda x: -x[1])
        
        label = "TODOS" if range_concursos == self.total_concursos else str(range_concursos)
        
        print()
        print(f"🔥 NÚMEROS QUENTES DO MELHOR RANGE ({label} concursos):")
        print("-" * 50)
        
        quentes = [n for n, _ in ordenados[:15]]
        acertos_quentes = len(set(quentes) & self.resultado_validacao)
        
        for i, (num, f) in enumerate(ordenados[:15], 1):
            em_resultado = "✅" if num in self.resultado_validacao else "❌"
            pct = (f / range_concursos) * 100 if range_concursos > 0 else 0
            print(f"   {i:2}. Número {num:2} → {f:4} vezes ({pct:5.1f}%) {em_resultado}")
        
        print()
        print(f"   📊 Acertos nos TOP 15 quentes: {acertos_quentes}/15 = {acertos_quentes/15*100:.1f}%")
        
        # Mostrar números do resultado que não são quentes
        nao_quentes = self.resultado_validacao - set(quentes)
        if nao_quentes:
            print(f"   ⚠️  Números do resultado fora dos quentes: {sorted(nao_quentes)}")


def main():
    """Execução principal"""
    print()
    print("🔬" * 30)
    print("  BENCHMARK AUTOMÁTICO DE RANGE - ULTRA QUENTES")
    print("🔬" * 30)
    print()
    
    benchmark = BenchmarkRangeQuentes()
    
    # Perguntar quantidade de combinações
    try:
        qtd = input("\n📊 Quantas combinações por range testar? [100]: ").strip()
        num_comb = int(qtd) if qtd else 100
    except:
        num_comb = 100
    
    print()
    resultados = benchmark.executar_benchmark_completo(num_comb)
    
    print()
    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
