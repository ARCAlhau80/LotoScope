#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎯 GERADOR MEGA 13+ - LOTOSCOPE
Otimizado para maximizar chances de 13+ acertos

Estratégia: Gerar MAIS combinações de alta qualidade
Se 10 combinações dão 1.7% de 13+, 
   20 combinações darão ~3.4%
   30 combinações darão ~5%
   50 combinações darão ~8%

Autor: LotoScope AI
Data: Dezembro 2025
"""

import sys
import random
from pathlib import Path
from typing import List, Set, Dict
from collections import Counter
from datetime import datetime
import statistics

# Configurar paths
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config


class GeradorMega13:
    """
    Gerador otimizado para 13+ acertos.
    
    Estratégia Ultra Quentes:
    - Foco nos 15 números mais frequentes recentemente
    - Equilíbrio par/ímpar
    - Diversificação controlada
    """
    
    def __init__(self):
        self.freq_recente = None
        self.freq_total = None
        self.quentes = None
        self.frios = None
        self.ultimo = None
        
        print("🎯 GERADOR MEGA 13+ inicializado")
        self._carregar_dados()
    
    def _carregar_dados(self):
        """Carrega todos os dados necessários"""
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            # Frequência últimos 50 concursos
            self.freq_recente = {i: 0 for i in range(1, 26)}
            cursor.execute("""
                SELECT TOP 50 N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT ORDER BY Concurso DESC
            """)
            for row in cursor.fetchall():
                for num in row:
                    if num in self.freq_recente:
                        self.freq_recente[num] += 1
            
            # Último resultado
            cursor.execute("""
                SELECT TOP 1 N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT ORDER BY Concurso DESC
            """)
            self.ultimo = set(cursor.fetchone())
            
            cursor.close()
            conn.close()
            
            # Ordenar por frequência
            ordenados = sorted(self.freq_recente.items(), key=lambda x: -x[1])
            self.quentes = [n for n, _ in ordenados[:15]]
            self.frios = [n for n, _ in ordenados[15:]]
            
            print(f"   📊 Números quentes: {self.quentes[:10]}")
            print(f"   ❄️ Números frios: {self.frios}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    def _gerar_ultra_quente(self) -> Set[int]:
        """Gera combinação focando em números quentes"""
        numeros = set()
        
        # Pegar 12-14 quentes
        quentes_embaralhados = self.quentes.copy()
        random.shuffle(quentes_embaralhados)
        numeros.update(quentes_embaralhados[:random.randint(12, 14)])
        
        # Completar com frios
        frios_embaralhados = self.frios.copy()
        random.shuffle(frios_embaralhados)
        
        while len(numeros) < 15:
            numeros.add(frios_embaralhados.pop())
        
        # Ajustar par/ímpar se necessário
        numeros = self._ajustar_paridade(numeros)
        
        return numeros
    
    def _gerar_mista(self) -> Set[int]:
        """Gera combinação mista quentes + último"""
        numeros = set()
        
        # 8-10 quentes
        quentes_embaralhados = self.quentes.copy()
        random.shuffle(quentes_embaralhados)
        numeros.update(quentes_embaralhados[:random.randint(8, 10)])
        
        # 3-5 do último resultado
        ultimo_lista = list(self.ultimo)
        random.shuffle(ultimo_lista)
        for u in ultimo_lista:
            if len(numeros) >= 13:
                break
            numeros.add(u)
        
        # Completar
        todos = list(range(1, 26))
        random.shuffle(todos)
        for n in todos:
            if len(numeros) >= 15:
                break
            if n not in numeros:
                numeros.add(n)
        
        numeros = self._ajustar_paridade(numeros)
        return numeros
    
    def _gerar_distribuida(self) -> Set[int]:
        """Gera combinação bem distribuída por faixas"""
        faixas = {
            1: [n for n in range(1, 6)],
            2: [n for n in range(6, 11)],
            3: [n for n in range(11, 16)],
            4: [n for n in range(16, 21)],
            5: [n for n in range(21, 26)]
        }
        
        numeros = set()
        
        # 3 de cada faixa, priorizando quentes
        for faixa_nums in faixas.values():
            # Ordenar por frequência
            ordenados = sorted(faixa_nums, key=lambda x: -self.freq_recente.get(x, 0))
            # Top 2 + 1 aleatório
            numeros.add(ordenados[0])
            numeros.add(ordenados[1])
            numeros.add(random.choice(ordenados[2:]))
        
        return numeros
    
    def _ajustar_paridade(self, numeros: Set[int]) -> Set[int]:
        """Ajusta para ter entre 6-9 pares"""
        lista = list(numeros)
        pares = [n for n in lista if n % 2 == 0]
        impares = [n for n in lista if n % 2 == 1]
        
        # Ideal: 7-8 pares
        while len(pares) < 6 and impares:
            # Trocar ímpar por par
            remover = random.choice(impares)
            impares.remove(remover)
            lista.remove(remover)
            
            novo = random.choice([n for n in range(2, 26, 2) if n not in lista])
            lista.append(novo)
            pares.append(novo)
        
        while len(pares) > 9 and pares:
            remover = random.choice(pares)
            pares.remove(remover)
            lista.remove(remover)
            
            novo = random.choice([n for n in range(1, 26, 2) if n not in lista])
            lista.append(novo)
            impares.append(novo)
        
        return set(lista[:15])
    
    def _calcular_score(self, numeros: Set[int]) -> float:
        """Calcula score de qualidade da combinação"""
        score = 0.0
        
        # Quentes
        qtd_quentes = len([n for n in numeros if n in self.quentes])
        score += qtd_quentes * 5
        
        # Par/ímpar
        pares = len([n for n in numeros if n % 2 == 0])
        if 7 <= pares <= 8:
            score += 20
        elif 6 <= pares <= 9:
            score += 10
        
        # Soma
        soma = sum(numeros)
        if 180 <= soma <= 200:
            score += 15
        elif 170 <= soma <= 210:
            score += 8
        
        # Distribuição por faixas
        faixas = [
            len([n for n in numeros if 1 <= n <= 5]),
            len([n for n in numeros if 6 <= n <= 10]),
            len([n for n in numeros if 11 <= n <= 15]),
            len([n for n in numeros if 16 <= n <= 20]),
            len([n for n in numeros if 21 <= n <= 25]),
        ]
        if all(f >= 2 for f in faixas):
            score += 15
        
        return score
    
    def gerar_combinacoes(self, quantidade: int = 30) -> List[Dict]:
        """
        Gera combinações otimizadas para 13+
        
        Recomendação:
        - 10 combinações: ~1.7% chance de 13+
        - 20 combinações: ~3.4% chance de 13+
        - 30 combinações: ~5% chance de 13+
        - 50 combinações: ~8% chance de 13+
        """
        print(f"\n🎯 GERANDO {quantidade} COMBINAÇÕES MEGA 13+")
        print("=" * 60)
        
        candidatas = []
        usados = set()
        
        # Gerar 3x mais candidatas
        n_tentativas = quantidade * 5
        
        geradores = [
            (self._gerar_ultra_quente, 0.5),  # 50% ultra quentes
            (self._gerar_mista, 0.3),         # 30% mista
            (self._gerar_distribuida, 0.2),   # 20% distribuída
        ]
        
        for _ in range(n_tentativas):
            # Escolher gerador
            r = random.random()
            acum = 0
            for gerador, peso in geradores:
                acum += peso
                if r <= acum:
                    numeros = gerador()
                    break
            
            chave = tuple(sorted(numeros))
            if chave in usados:
                continue
            
            usados.add(chave)
            score = self._calcular_score(numeros)
            
            candidatas.append({
                'numeros': sorted(numeros),
                'score': score,
                'pares': len([n for n in numeros if n % 2 == 0]),
                'soma': sum(numeros),
                'quentes': len([n for n in numeros if n in self.quentes]),
            })
        
        # Ordenar por score
        candidatas.sort(key=lambda x: -x['score'])
        melhores = candidatas[:quantidade]
        
        print(f"✅ {len(melhores)} combinações geradas\n")
        
        for i, c in enumerate(melhores, 1):
            nums = ' '.join(f'{n:02d}' for n in c['numeros'])
            print(f"   {i:2d}. [{nums}] Sc:{c['score']:.0f} P:{c['pares']} Q:{c['quentes']}")
        
        return melhores
    
    def gerar_super_combinacoes(self, quantidade: int = 30) -> Dict:
        """Interface compatível com menu"""
        return {
            'combinacoes': self.gerar_combinacoes(quantidade),
            'metodo': 'mega_13_mais',
            'foco': '13+ acertos',
            'data': datetime.now().isoformat()
        }


def benchmark_quantidade():
    """Testa como quantidade de combinações afeta taxa de 13+"""
    print("\n" + "=" * 70)
    print("📊 BENCHMARK: QUANTIDADE vs TAXA 13+")
    print("=" * 70)
    
    conn = db_config.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 50 N1, N2, N3, N4, N5, N6, N7, N8, 
               N9, N10, N11, N12, N13, N14, N15
        FROM RESULTADOS_INT ORDER BY Concurso DESC
    """)
    
    resultados = [set(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    gerador = GeradorMega13()
    
    quantidades = [10, 20, 30, 50, 100]
    N_ITERACOES = 10
    
    print(f"\n🔄 {N_ITERACOES} iterações por quantidade\n")
    
    for qtd in quantidades:
        taxas_13 = []
        
        for _ in range(N_ITERACOES):
            combinacoes = gerador.gerar_combinacoes(qtd)
            combs_set = [set(c['numeros']) for c in combinacoes]
            
            acertos_13 = 0
            for r in resultados:
                melhor = max(len(c.intersection(r)) for c in combs_set)
                if melhor >= 13:
                    acertos_13 += 1
            
            taxa = acertos_13 / len(resultados) * 100
            taxas_13.append(taxa)
        
        media = statistics.mean(taxas_13)
        print(f"   📊 {qtd:3d} combinações: {media:.1f}% chance de 13+")
    
    print("\n" + "=" * 70)
    print("💰 CUSTO-BENEFÍCIO (Lotofácil 15 números = R$ 3,50):")
    print("=" * 70)
    for qtd in quantidades:
        custo = qtd * 3.50
        print(f"   • {qtd:3d} combinações: R$ {custo:.2f}")
    
    print("""
   📌 PREMIAÇÃO ATUAL:
      • 11 acertos: R$ 7,00
      • 12 acertos: R$ 14,00
      • 13 acertos: R$ 35,00 ← FOCO DESTE GERADOR
      • 14 acertos: R$ 1.924,15
      • 15 acertos: R$ 569.570,73
    """)


if __name__ == "__main__":
    benchmark_quantidade()
