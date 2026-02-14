#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔬 BENCHMARK DO GERADOR POSICIONAL PROBABILÍSTICO
Testa o gerador contra todos os concursos históricos

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
sys.path.insert(0, str(_BASE_DIR / 'geradores'))

from database_config import db_config
from gerador_posicional_probabilistico import GeradorPosicionalProbabilistico


class BenchmarkPosicional:
    """
    Benchmark do gerador posicional probabilístico.
    Testa contra todos os concursos históricos.
    """
    
    def __init__(self):
        self.gerador = None
        self.todos_concursos = []
        
        print("🔬 BENCHMARK - GERADOR POSICIONAL PROBABILÍSTICO")
        print("=" * 60)
        self._carregar_dados()
    
    def _carregar_dados(self):
        """Carrega todos os concursos"""
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT ORDER BY Concurso ASC
            """)
            
            for row in cursor.fetchall():
                self.todos_concursos.append({
                    'concurso': row[0],
                    'numeros': set(row[1:])
                })
            
            cursor.close()
            conn.close()
            
            print(f"📚 {len(self.todos_concursos)} concursos carregados")
            print(f"📊 Do concurso {self.todos_concursos[0]['concurso']} ao {self.todos_concursos[-1]['concurso']}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def _criar_gerador_silencioso(self):
        """Cria gerador sem prints"""
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        gerador = GeradorPosicionalProbabilistico()
        sys.stdout = old_stdout
        return gerador
    
    def executar_benchmark(self, num_combinacoes: int = 100, 
                           num_concursos: int = None):
        """
        Executa benchmark completo.
        
        Args:
            num_combinacoes: Combinações por concurso
            num_concursos: Quantos concursos testar (None = todos)
        """
        gerador = self._criar_gerador_silencioso()
        
        if num_concursos is None:
            num_concursos = len(self.todos_concursos)
        
        # Usar os mais recentes
        concursos_teste = self.todos_concursos[-num_concursos:]
        
        total_testes = num_concursos * num_combinacoes
        
        print()
        print(f"🔬 Testando {num_concursos} concursos")
        print(f"🎲 {num_combinacoes} combinações por concurso")
        print(f"📈 Total de testes: {total_testes:,}")
        print("=" * 70)
        print()
        
        todos_acertos = []
        contagem_acertos = Counter()
        
        # Progress
        progresso_step = max(1, num_concursos // 20)
        
        for i, resultado in enumerate(concursos_teste):
            if i % progresso_step == 0:
                pct = (i / num_concursos) * 100
                print(f"   Progresso: {pct:.0f}% ({i}/{num_concursos})...", end="\r")
            
            numeros_real = resultado['numeros']
            
            for _ in range(num_combinacoes):
                comb = set(gerador.gerar_combinacao())
                acertos = len(comb & numeros_real)
                todos_acertos.append(acertos)
                contagem_acertos[acertos] += 1
        
        print(f"   Progresso: 100% ({num_concursos}/{num_concursos})   ")
        print()
        
        # Estatísticas
        media = statistics.mean(todos_acertos)
        mediana = statistics.median(todos_acertos)
        
        # Taxas
        taxa_11 = sum(1 for a in todos_acertos if a >= 11) / len(todos_acertos) * 100
        taxa_12 = sum(1 for a in todos_acertos if a >= 12) / len(todos_acertos) * 100
        taxa_13 = sum(1 for a in todos_acertos if a >= 13) / len(todos_acertos) * 100
        taxa_14 = sum(1 for a in todos_acertos if a >= 14) / len(todos_acertos) * 100
        taxa_15 = sum(1 for a in todos_acertos if a == 15) / len(todos_acertos) * 100
        
        # Resultados
        print("=" * 70)
        print("📊 RESULTADO DO BENCHMARK")
        print("=" * 70)
        print()
        print(f"   📈 Média de acertos: {media:.2f}")
        print(f"   📊 Mediana: {mediana:.1f}")
        print(f"   🎯 Melhor resultado: {max(todos_acertos)} acertos")
        print(f"   📉 Pior resultado: {min(todos_acertos)} acertos")
        print()
        
        print("   📊 DISTRIBUIÇÃO DE ACERTOS:")
        print("   " + "-" * 50)
        for acertos in sorted(contagem_acertos.keys(), reverse=True):
            qtd = contagem_acertos[acertos]
            pct = (qtd / len(todos_acertos)) * 100
            barra = "█" * int(pct * 2)
            premio = ""
            if acertos >= 11:
                premio = " 💰"
            if acertos >= 13:
                premio = " 💰💰"
            if acertos >= 14:
                premio = " 💰💰💰"
            if acertos == 15:
                premio = " 🏆"
            print(f"   {acertos:2} acertos: {qtd:6,} ({pct:5.2f}%) {barra}{premio}")
        
        print()
        print("   🏆 TAXAS DE PREMIAÇÃO:")
        print("   " + "-" * 50)
        print(f"   11+ acertos: {taxa_11:.2f}% ({int(taxa_11 * total_testes / 100):,} combinações)")
        print(f"   12+ acertos: {taxa_12:.2f}% ({int(taxa_12 * total_testes / 100):,} combinações)")
        print(f"   13+ acertos: {taxa_13:.2f}% ({int(taxa_13 * total_testes / 100):,} combinações)")
        print(f"   14+ acertos: {taxa_14:.2f}% ({int(taxa_14 * total_testes / 100):,} combinações)")
        print(f"   15  acertos: {taxa_15:.4f}% ({int(taxa_15 * total_testes / 100):,} combinações)")
        
        print()
        print("=" * 70)
        
        # Comparação com aleatório puro
        print()
        print("📊 COMPARAÇÃO COM ALEATÓRIO PURO:")
        print("-" * 50)
        
        # Probabilidade teórica aleatória
        # P(11) = C(15,11) * C(10,4) / C(25,15) ≈ 3.17%
        # P(12) = C(15,12) * C(10,3) / C(25,15) ≈ 0.65%
        # P(13) = C(15,13) * C(10,2) / C(25,15) ≈ 0.09%
        # P(14) = C(15,14) * C(10,1) / C(25,15) ≈ 0.006%
        # P(15) = C(15,15) * C(10,0) / C(25,15) ≈ 0.0003%
        
        print(f"   Aleatório Puro - 11+: ~3.91%")
        print(f"   Posicional    - 11+: {taxa_11:.2f}% ", end="")
        if taxa_11 > 3.91:
            print(f"(+{taxa_11 - 3.91:.2f}% MELHOR) ✅")
        else:
            print(f"({taxa_11 - 3.91:.2f}%)")
        
        print(f"   Aleatório Puro - 12+: ~0.74%")
        print(f"   Posicional    - 12+: {taxa_12:.2f}% ", end="")
        if taxa_12 > 0.74:
            print(f"(+{taxa_12 - 0.74:.2f}% MELHOR) ✅")
        else:
            print(f"({taxa_12 - 0.74:.2f}%)")
        
        print(f"   Aleatório Puro - 13+: ~0.10%")
        print(f"   Posicional    - 13+: {taxa_13:.2f}% ", end="")
        if taxa_13 > 0.10:
            print(f"(+{taxa_13 - 0.10:.2f}% MELHOR) ✅")
        else:
            print(f"({taxa_13 - 0.10:.2f}%)")
        
        print()
        print("=" * 70)
        
        return {
            'media': media,
            'mediana': mediana,
            'taxa_11': taxa_11,
            'taxa_12': taxa_12,
            'taxa_13': taxa_13,
            'taxa_14': taxa_14,
            'taxa_15': taxa_15,
            'distribuicao': dict(contagem_acertos),
            'total_testes': total_testes
        }


def main():
    print()
    print("🔬" * 30)
    print("  BENCHMARK - GERADOR POSICIONAL PROBABILÍSTICO")
    print("🔬" * 30)
    print()
    
    benchmark = BenchmarkPosicional()
    
    try:
        qtd_conc = input("\n📊 Quantos concursos testar? [todos]: ").strip()
        num_conc = int(qtd_conc) if qtd_conc else None
        
        qtd_comb = input("🎲 Quantas combinações por concurso? [100]: ").strip()
        num_comb = int(qtd_comb) if qtd_comb else 100
    except:
        num_conc = None
        num_comb = 100
    
    resultados = benchmark.executar_benchmark(num_comb, num_conc)
    
    print()
    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
