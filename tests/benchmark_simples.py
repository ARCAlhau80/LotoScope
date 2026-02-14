#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🏆 BENCHMARK SIMPLES - LOTOSCOPE
Testa geradores que funcionam de forma independente
"""

import sys
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import statistics

# Configurar paths
ROOT_DIR = Path(__file__).parent.parent
LOTOFACIL_DIR = ROOT_DIR / 'lotofacil_lite'
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR / 'utils'))

import warnings
warnings.filterwarnings('ignore')

from database_config import db_config


class BenchmarkSimples:
    """Benchmark direto contra o banco de dados"""
    
    def __init__(self, ultimos_n: int = 20):
        self.ultimos_n = ultimos_n
        self.resultados_historicos = []
        self._carregar_historico()
    
    def _carregar_historico(self):
        """Carrega resultados históricos"""
        print(f"\n📊 Carregando últimos {self.ultimos_n} concursos...")
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT TOP {self.ultimos_n} Concurso, 
                       N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT
                ORDER BY Concurso DESC
            """)
            
            for row in cursor.fetchall():
                self.resultados_historicos.append({
                    'concurso': row[0],
                    'numeros': set(row[1:16])
                })
            
            cursor.close()
            conn.close()
            
            print(f"   ✅ {len(self.resultados_historicos)} concursos carregados")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    def _avaliar(self, combinacoes: List[Set[int]], nome: str) -> Dict:
        """Avalia combinações contra histórico"""
        if not combinacoes or not self.resultados_historicos:
            return None
        
        melhores_por_concurso = []
        
        for resultado in self.resultados_historicos:
            melhor = 0
            for comb in combinacoes:
                acertos = len(comb.intersection(resultado['numeros']))
                melhor = max(melhor, acertos)
            melhores_por_concurso.append(melhor)
        
        return {
            'nome': nome,
            'qtd_combinacoes': len(combinacoes),
            'media_melhor': statistics.mean(melhores_por_concurso),
            'max_acerto': max(melhores_por_concurso),
            'min_acerto': min(melhores_por_concurso),
            'taxa_11_mais': sum(1 for m in melhores_por_concurso if m >= 11) / len(melhores_por_concurso) * 100,
            'taxa_12_mais': sum(1 for m in melhores_por_concurso if m >= 12) / len(melhores_por_concurso) * 100,
            'detalhes': melhores_por_concurso
        }
    
    def gerar_aleatorio(self, qtd: int = 10) -> List[Set[int]]:
        """Gerador aleatório (baseline)"""
        combinacoes = []
        for _ in range(qtd):
            numeros = set(random.sample(range(1, 26), 15))
            combinacoes.append(numeros)
        return combinacoes
    
    def gerar_frequencia(self, qtd: int = 10) -> List[Set[int]]:
        """Gerador baseado em frequência dos números"""
        # Calcular frequência de cada número
        frequencias = {i: 0 for i in range(1, 26)}
        
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        for i in range(1, 16):
            cursor.execute(f"SELECT N{i}, COUNT(*) FROM RESULTADOS_INT GROUP BY N{i}")
            for num, cnt in cursor.fetchall():
                if num in frequencias:
                    frequencias[num] += cnt
        
        cursor.close()
        conn.close()
        
        # Ordenar por frequência
        ordenados = sorted(frequencias.items(), key=lambda x: -x[1])
        top_18 = [n for n, _ in ordenados[:18]]  # Top 18 mais frequentes
        
        combinacoes = []
        for _ in range(qtd):
            # Escolher 15 dos top 18, com variação
            escolhidos = set(random.sample(top_18, 15))
            combinacoes.append(escolhidos)
        
        return combinacoes
    
    def gerar_equilibrado(self, qtd: int = 10) -> List[Set[int]]:
        """Gerador equilibrado (par/ímpar, baixo/alto)"""
        combinacoes = []
        
        for _ in range(qtd):
            numeros = set()
            
            # Meta: 7-8 ímpares, 7-8 pares
            impares = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
            pares = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
            
            qtd_impares = random.choice([7, 8])
            qtd_pares = 15 - qtd_impares
            
            numeros.update(random.sample(impares, qtd_impares))
            numeros.update(random.sample(pares, qtd_pares))
            
            combinacoes.append(numeros)
        
        return combinacoes
    
    def gerar_posicional(self, qtd: int = 10) -> List[Set[int]]:
        """Gerador baseado em análise posicional"""
        # Analisar quais números aparecem mais em cada posição
        posicoes = {i: [] for i in range(1, 16)}
        
        conn = db_config.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 100 N1, N2, N3, N4, N5, N6, N7, N8, 
                   N9, N10, N11, N12, N13, N14, N15
            FROM RESULTADOS_INT
            ORDER BY Concurso DESC
        """)
        
        for row in cursor.fetchall():
            for i, num in enumerate(row, 1):
                posicoes[i].append(num)
        
        cursor.close()
        conn.close()
        
        # Para cada posição, encontrar os números mais comuns
        top_por_posicao = {}
        for pos, nums in posicoes.items():
            from collections import Counter
            contagem = Counter(nums)
            top_por_posicao[pos] = [n for n, _ in contagem.most_common(5)]
        
        combinacoes = []
        for _ in range(qtd):
            numeros = set()
            for pos in range(1, 16):
                # Escolher um dos top 5 para cada posição
                candidatos = [n for n in top_por_posicao[pos] if n not in numeros]
                if candidatos:
                    numeros.add(random.choice(candidatos))
            
            # Se não conseguiu 15, completar aleatoriamente
            while len(numeros) < 15:
                n = random.randint(1, 25)
                if n not in numeros:
                    numeros.add(n)
            
            combinacoes.append(numeros)
        
        return combinacoes
    
    def gerar_tendencia_recente(self, qtd: int = 10) -> List[Set[int]]:
        """Gerador baseado em tendência dos últimos concursos"""
        # Analisar últimos 10 concursos
        recentes = []
        conn = db_config.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 10 N1, N2, N3, N4, N5, N6, N7, N8, 
                   N9, N10, N11, N12, N13, N14, N15
            FROM RESULTADOS_INT
            ORDER BY Concurso DESC
        """)
        
        for row in cursor.fetchall():
            recentes.extend(row)
        
        cursor.close()
        conn.close()
        
        from collections import Counter
        contagem = Counter(recentes)
        
        # Top 20 mais recentes
        top_20 = [n for n, _ in contagem.most_common(20)]
        
        combinacoes = []
        for _ in range(qtd):
            escolhidos = set(random.sample(top_20, 15))
            combinacoes.append(escolhidos)
        
        return combinacoes
    
    def gerar_ciclos_ausencia(self, qtd: int = 10) -> List[Set[int]]:
        """Gerador baseado em ciclos de ausência"""
        # Calcular quantos concursos cada número está ausente
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        # Último concurso de cada número
        ausencias = {}
        
        for num in range(1, 26):
            cursor.execute(f"""
                SELECT TOP 1 Concurso FROM RESULTADOS_INT
                WHERE N1={num} OR N2={num} OR N3={num} OR N4={num} OR N5={num}
                   OR N6={num} OR N7={num} OR N8={num} OR N9={num} OR N10={num}
                   OR N11={num} OR N12={num} OR N13={num} OR N14={num} OR N15={num}
                ORDER BY Concurso DESC
            """)
            row = cursor.fetchone()
            if row:
                ausencias[num] = row[0]
        
        cursor.close()
        conn.close()
        
        # Ordenar por mais ausente (menor concurso = mais tempo ausente)
        ordenados = sorted(ausencias.items(), key=lambda x: x[1])
        
        # Mix: 5 mais ausentes + 5 médios + 5 recentes
        mais_ausentes = [n for n, _ in ordenados[:8]]
        medios = [n for n, _ in ordenados[8:17]]
        recentes = [n for n, _ in ordenados[17:]]
        
        combinacoes = []
        for _ in range(qtd):
            numeros = set()
            numeros.update(random.sample(mais_ausentes, 5))
            numeros.update(random.sample(medios, 5))
            numeros.update(random.sample(recentes, 5))
            combinacoes.append(numeros)
        
        return combinacoes
    
    def executar(self):
        """Executa todos os benchmarks"""
        print("\n" + "=" * 70)
        print("🏆 BENCHMARK DE ESTRATÉGIAS - LOTOSCOPE")
        print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Testando contra últimos {self.ultimos_n} concursos")
        print("=" * 70)
        
        estrategias = [
            ("🎲 Aleatório (baseline)", self.gerar_aleatorio),
            ("📊 Frequência Histórica", self.gerar_frequencia),
            ("⚖️ Equilibrado Par/Ímpar", self.gerar_equilibrado),
            ("📍 Análise Posicional", self.gerar_posicional),
            ("📈 Tendência Recente", self.gerar_tendencia_recente),
            ("🔄 Ciclos de Ausência", self.gerar_ciclos_ausencia),
        ]
        
        resultados = []
        
        for nome, gerador in estrategias:
            print(f"\n{'-' * 60}")
            print(f"{nome}")
            print(f"{'-' * 60}")
            
            try:
                inicio = time.perf_counter()
                combinacoes = gerador(10)
                tempo = (time.perf_counter() - inicio) * 1000
                
                avaliacao = self._avaliar(combinacoes, nome)
                if avaliacao:
                    avaliacao['tempo_ms'] = tempo
                    print(f"   ✅ {avaliacao['qtd_combinacoes']} combinações em {tempo:.0f}ms")
                    print(f"   📊 Média melhor acerto: {avaliacao['media_melhor']:.1f}")
                    print(f"   🎯 Taxa 11+: {avaliacao['taxa_11_mais']:.0f}%")
                    print(f"   🏆 Taxa 12+: {avaliacao['taxa_12_mais']:.0f}%")
                    resultados.append(avaliacao)
                else:
                    print(f"   ❌ Falha na avaliação")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)[:50]}")
        
        # Ranking final
        self._ranking(resultados)
        
        return resultados
    
    def _ranking(self, resultados: List[Dict]):
        """Gera ranking final"""
        if not resultados:
            return
        
        resultados.sort(key=lambda x: (-x['taxa_11_mais'], -x['media_melhor']))
        
        print("\n" + "=" * 70)
        print("🏆 RANKING FINAL")
        print("=" * 70)
        
        print(f"\n{'Pos':<4} {'Estratégia':<30} {'Taxa 11+':<10} {'Taxa 12+':<10} {'Média':<8}")
        print("-" * 70)
        
        for i, r in enumerate(resultados, 1):
            medalha = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f"{i} "
            nome = r['nome'][:28]
            taxa11 = f"{r['taxa_11_mais']:.0f}%"
            taxa12 = f"{r['taxa_12_mais']:.0f}%"
            media = f"{r['media_melhor']:.1f}"
            
            print(f"{medalha:<4} {nome:<30} {taxa11:<10} {taxa12:<10} {media:<8}")
        
        # Campeão
        campeao = resultados[0]
        print("\n" + "=" * 70)
        print(f"🥇 MELHOR ESTRATÉGIA: {campeao['nome']}")
        print("=" * 70)
        print(f"""
   📊 Performance:
      • Taxa 11+ acertos: {campeao['taxa_11_mais']:.0f}%
      • Taxa 12+ acertos: {campeao['taxa_12_mais']:.0f}%
      • Média melhor acerto: {campeao['media_melhor']:.2f}
      • Máximo alcançado: {campeao['max_acerto']} acertos
      • Mínimo: {campeao['min_acerto']} acertos
        """)


def main():
    benchmark = BenchmarkSimples(ultimos_n=20)
    resultados = benchmark.executar()
    
    print("\n" + "=" * 70)
    print("💡 PROPOSTAS DE MELHORIA")
    print("=" * 70)
    
    if resultados:
        melhor = resultados[0]
        
        print(f"""
    📋 ANÁLISE:
    
    1. 🔄 ENSEMBLE: Combinar as top 3 estratégias
       - {resultados[0]['nome'].split(' ')[1] if len(resultados) > 0 else 'N/A'}
       - {resultados[1]['nome'].split(' ')[1] if len(resultados) > 1 else 'N/A'}
       - {resultados[2]['nome'].split(' ')[1] if len(resultados) > 2 else 'N/A'}
    
    2. 📊 OTIMIZAÇÃO DE PARÂMETROS:
       - Ajustar quantidade de números por estratégia
       - Testar diferentes janelas temporais
    
    3. 🎯 META SUGERIDA:
       - Taxa 11+ acertos: 70%+
       - Taxa 12+ acertos: 30%+
       
    4. 🔧 PRÓXIMOS PASSOS:
       - Implementar votação entre estratégias
       - Criar gerador híbrido
       - Dashboard de acompanhamento
        """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
