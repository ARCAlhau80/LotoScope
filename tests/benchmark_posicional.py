#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎲 BENCHMARK GERADOR POSICIONAL PROBABILÍSTICO
Testa o gerador posicional contra TODOS os concursos históricos

Este benchmark:
1. Gera combinações usando o método posicional
2. Testa contra cada concurso real
3. Calcula distribuição de acertos
4. Compara com geração puramente aleatória
"""

import sys
import os
import random
from datetime import datetime
from collections import defaultdict

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lotofacil_lite', 'geradores'))

import pyodbc

class BenchmarkPosicional:
    def __init__(self):
        self.conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-K6JPBDS;"
            "DATABASE=LOTOFACIL;"
            "Trusted_Connection=yes;"
        )
        self.resultados = []
        
    def carregar_resultados(self):
        """Carrega todos os resultados da Lotofácil"""
        print("📊 Carregando resultados do banco...")
        
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados
                ORDER BY Concurso
            """)
            
            for row in cursor.fetchall():
                concurso = row[0]
                # Converter para inteiros (banco pode ter strings)
                numeros = set(int(n) for n in row[1:16])
                self.resultados.append({
                    'concurso': concurso,
                    'numeros': numeros
                })
            
            conn.close()
            print(f"✅ {len(self.resultados)} concursos carregados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar resultados: {e}")
            return False

    def executar_benchmark(self, n_combinacoes=100, n_testes_por_concurso=1):
        """
        Executa benchmark do gerador posicional
        
        Args:
            n_combinacoes: Quantas combinações testar por concurso
            n_testes_por_concurso: Quantas vezes repetir o teste por concurso
        """
        print("\n" + "=" * 70)
        print("🎲 BENCHMARK GERADOR POSICIONAL PROBABILÍSTICO")
        print("=" * 70)
        
        if not self.resultados:
            if not self.carregar_resultados():
                return
        
        # Importar o gerador
        try:
            from gerador_posicional_probabilistico import GeradorPosicionalProbabilistico
            gerador = GeradorPosicionalProbabilistico()
            print("✅ Gerador posicional carregado")
        except ImportError as e:
            print(f"❌ Erro ao importar gerador: {e}")
            return
        
        print(f"\n📋 CONFIGURAÇÃO:")
        print(f"   • Concursos a testar: {len(self.resultados)}")
        print(f"   • Combinações por concurso: {n_combinacoes}")
        print(f"   • Testes por concurso: {n_testes_por_concurso}")
        print(f"   • Total de combinações: {len(self.resultados) * n_combinacoes * n_testes_por_concurso:,}")
        
        # Estatísticas
        total_combinacoes = 0
        distribuicao = defaultdict(int)  # acertos -> quantidade
        combinacoes_13_mais = []  # Guardar as que tiveram 13+
        
        inicio = datetime.now()
        
        print(f"\n🔄 Executando benchmark...")
        print("-" * 50)
        
        for i, resultado in enumerate(self.resultados):
            if (i + 1) % 500 == 0:
                elapsed = (datetime.now() - inicio).total_seconds()
                print(f"   Concurso {i+1}/{len(self.resultados)} ({(i+1)/len(self.resultados)*100:.1f}%) - {elapsed:.1f}s")
            
            resultado_nums = resultado['numeros']
            
            for _ in range(n_testes_por_concurso):
                # Gerar combinações
                combinacoes = gerador.gerar_combinacoes(n_combinacoes)
                
                for comb in combinacoes:
                    total_combinacoes += 1
                    acertos = len(set(comb) & resultado_nums)
                    distribuicao[acertos] += 1
                    
                    if acertos >= 13:
                        combinacoes_13_mais.append({
                            'concurso': resultado['concurso'],
                            'combinacao': comb,
                            'acertos': acertos
                        })
        
        elapsed = (datetime.now() - inicio).total_seconds()
        
        # Mostrar resultados
        print("\n" + "=" * 70)
        print("📊 RESULTADOS DO BENCHMARK")
        print("=" * 70)
        
        print(f"\n⏱️ Tempo total: {elapsed:.2f} segundos")
        print(f"🎯 Combinações testadas: {total_combinacoes:,}")
        print(f"⚡ Velocidade: {total_combinacoes/elapsed:,.0f} combinações/segundo")
        
        print(f"\n📈 DISTRIBUIÇÃO DE ACERTOS:")
        print("-" * 40)
        
        for acertos in sorted(distribuicao.keys()):
            qtd = distribuicao[acertos]
            pct = (qtd / total_combinacoes) * 100
            bar = '█' * int(pct * 2)
            premio = ""
            if acertos == 11:
                premio = " (R$ 7)"
            elif acertos == 12:
                premio = " (R$ 14)"
            elif acertos == 13:
                premio = " (R$ 35)"
            elif acertos == 14:
                premio = " (R$ 1.924)"
            elif acertos == 15:
                premio = " (JACKPOT!)"
            print(f"   {acertos:2d} acertos: {qtd:8,} ({pct:6.3f}%) {bar}{premio}")
        
        # Estatísticas de prêmios (valores atualizados Lotofácil)
        # 11=R$7, 12=R$14, 13=R$35, 14=R$1.000, 15=R$1.800.000
        print(f"\n💰 ESTATÍSTICAS DE PRÊMIOS:")
        print("-" * 40)
        
        premios = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}
        total_premio = 0
        for acertos, valor in premios.items():
            qtd = distribuicao.get(acertos, 0)
            ganho = qtd * valor
            total_premio += ganho
            print(f"   {acertos} acertos: {qtd:6,} × R$ {valor:10.2f} = R$ {ganho:12.2f}")
        
        custo_total = total_combinacoes * 3.50
        lucro = total_premio - custo_total
        
        print(f"\n   📊 RESUMO FINANCEIRO:")
        print(f"   • Custo total: R$ {custo_total:,.2f}")
        print(f"   • Prêmios: R$ {total_premio:,.2f}")
        print(f"   • {'Lucro' if lucro >= 0 else 'Prejuízo'}: R$ {abs(lucro):,.2f}")
        print(f"   • ROI: {(total_premio/custo_total - 1) * 100:.2f}%")
        
        # Taxa de 13+
        taxa_13_mais = sum(distribuicao.get(a, 0) for a in [13, 14, 15]) / total_combinacoes * 100
        taxa_11_mais = sum(distribuicao.get(a, 0) for a in [11, 12, 13, 14, 15]) / total_combinacoes * 100
        
        print(f"\n🎯 TAXAS DE SUCESSO:")
        print(f"   • 11+ acertos: {taxa_11_mais:.3f}%")
        print(f"   • 13+ acertos: {taxa_13_mais:.4f}%")
        
        # Calcular média de acertos
        total_acertos = sum(acertos * qtd for acertos, qtd in distribuicao.items())
        media_acertos = total_acertos / total_combinacoes
        print(f"   • Média de acertos: {media_acertos:.2f}")
        
        # Mostrar alguns exemplos de 13+
        if combinacoes_13_mais:
            print(f"\n🏆 EXEMPLOS DE COMBINAÇÕES COM 13+ ACERTOS:")
            print("-" * 40)
            for i, item in enumerate(combinacoes_13_mais[:10], 1):
                nums = ' '.join(f'{n:02d}' for n in item['combinacao'])
                print(f"   {i}. Concurso {item['concurso']}: {nums} ({item['acertos']} acertos)")
        
        return {
            'total_combinacoes': total_combinacoes,
            'distribuicao': dict(distribuicao),
            'tempo': elapsed,
            'taxa_13_mais': taxa_13_mais,
            'taxa_11_mais': taxa_11_mais,
            'media_acertos': media_acertos
        }


def main():
    benchmark = BenchmarkPosicional()
    
    # Carregar resultados primeiro
    benchmark.carregar_resultados()
    
    # Executar benchmark: 100 combinações por concurso, 1 teste por concurso
    resultado = benchmark.executar_benchmark(n_combinacoes=100, n_testes_por_concurso=1)
    
    print("\n" + "=" * 70)
    print("✅ BENCHMARK CONCLUÍDO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
