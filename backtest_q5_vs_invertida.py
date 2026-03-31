# -*- coding: utf-8 -*-
"""
Backtest WALK-FORWARD: Q5 vs INVERTIDA vs Random
=================================================
Simula uso real: para cada concurso N, calcula estratégia com dados até N-1

Data: 28/03/2026
"""

import pyodbc
from collections import defaultdict
from itertools import combinations

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def obter_todos_concursos():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def calcular_frequencia(concursos):
    freq = defaultdict(int)
    for row in concursos:
        nums = [row[i] for i in range(1, 16)]
        for n in nums:
            freq[n] += 1
    return dict(freq)

def calcular_consecutivas(concursos, n_recentes=30):
    """Calcula quantas vezes consecutivas cada número apareceu recentemente"""
    consecutivas = {}
    for n in range(1, 26):
        count = 0
        for row in concursos[:n_recentes]:
            nums = set([row[i] for i in range(1, 16)])
            if n in nums:
                count += 1
            else:
                break  # Sequência interrompida
        consecutivas[n] = count
    return consecutivas

def estrategia_q5(freq_dict):
    """Exclui os 2 MENOS frequentes"""
    ordenado = sorted(range(1, 26), key=lambda x: freq_dict.get(x, 0))
    return ordenado[:2]  # 2 menos frequentes

def estrategia_invertida(freq_dict, consecutivas):
    """Exclui os 2 MAIS quentes (freq alta + consecutivas)"""
    # Score = freq_normalizada + consecutivas
    max_freq = max(freq_dict.values()) if freq_dict else 1
    
    scores = {}
    for n in range(1, 26):
        freq_norm = freq_dict.get(n, 0) / max_freq
        consec = consecutivas.get(n, 0)
        scores[n] = freq_norm + (consec / 10)  # Peso para consecutivas
    
    ordenado = sorted(range(1, 26), key=lambda x: scores[x], reverse=True)
    return ordenado[:2]  # 2 mais quentes

def backtest_walk_forward(concursos, janela=100, n_teste=100):
    """
    Para cada concurso de teste:
    - Usa os 'janela' concursos anteriores para calcular estratégia
    - Testa no concurso atual
    """
    resultados = {
        'Q5_frios': {'jackpots': 0, 'acertos': []},
        'INVERTIDA_quentes': {'jackpots': 0, 'acertos': []},
        'RANDOM': {'jackpots': 0, 'acertos': []}
    }
    
    # Começa do concurso 'janela' em diante
    inicio = len(concursos) - n_teste
    
    print(f"\n📊 Backtesting {n_teste} concursos (walk-forward)...")
    print(f"   Janela de análise: {janela} concursos anteriores")
    
    for i in range(inicio, len(concursos)):
        # Dados históricos até o concurso anterior
        historico = concursos[max(0, i-janela):i]
        
        # Concurso atual (para validar)
        atual = concursos[i]
        sorteio = set([atual[j] for j in range(1, 16)])
        
        # Calcula estratégias com dados históricos
        freq = calcular_frequencia(historico)
        consec = calcular_consecutivas(historico[:30])
        
        # Q5: exclui menos frequentes
        excluir_q5 = estrategia_q5(freq)
        jackpot_q5 = len(set(excluir_q5) & sorteio) == 0
        
        # INVERTIDA: exclui mais quentes
        excluir_inv = estrategia_invertida(freq, consec)
        jackpot_inv = len(set(excluir_inv) & sorteio) == 0
        
        # RANDOM: média de todas exclusões
        # (simplificado: usa prob teórica = C(10,2)/C(25,2) = 0.15)
        jackpot_random = 0.15  # Probabilidade teórica
        
        resultados['Q5_frios']['jackpots'] += int(jackpot_q5)
        resultados['INVERTIDA_quentes']['jackpots'] += int(jackpot_inv)
        resultados['RANDOM']['jackpots'] += jackpot_random
    
    return resultados, n_teste

def main():
    print("=" * 70)
    print("🔬 BACKTEST WALK-FORWARD: Q5 vs INVERTIDA vs RANDOM")
    print("=" * 70)
    
    concursos = obter_todos_concursos()
    print(f"\n📊 Total de concursos: {len(concursos)}")
    
    # Testa diferentes períodos
    periodos = [
        ('Últimos 50', 50),
        ('Últimos 100', 100),
        ('Últimos 200', 200),
        ('Últimos 300', 300),
    ]
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS POR PERÍODO:")
    print("=" * 70)
    
    resumo = []
    
    for nome, n_teste in periodos:
        print(f"\n🔹 {nome} concursos:")
        
        resultados, total = backtest_walk_forward(concursos, janela=100, n_teste=n_teste)
        
        taxa_q5 = resultados['Q5_frios']['jackpots'] / total * 100
        taxa_inv = resultados['INVERTIDA_quentes']['jackpots'] / total * 100
        taxa_random = 15.0  # Teórico
        
        print(f"   Q5 (frios):      {resultados['Q5_frios']['jackpots']:>3} jackpots = {taxa_q5:.1f}%")
        print(f"   INVERTIDA:       {resultados['INVERTIDA_quentes']['jackpots']:>3} jackpots = {taxa_inv:.1f}%")
        print(f"   RANDOM (teórico): {taxa_random:.1f}%")
        
        resumo.append({
            'periodo': nome,
            'q5': taxa_q5,
            'inv': taxa_inv,
            'random': taxa_random
        })
    
    # Conclusão
    print("\n" + "=" * 70)
    print("🎯 RESUMO COMPARATIVO:")
    print("=" * 70)
    
    print(f"\n{'Período':<15} {'Q5 (frios)':>12} {'INVERTIDA':>12} {'RANDOM':>12} {'Melhor':>15}")
    print("-" * 70)
    
    for r in resumo:
        melhor = 'Q5' if r['q5'] > r['inv'] else ('INVERTIDA' if r['inv'] > r['q5'] else 'EMPATE')
        diff = r['q5'] - r['inv']
        print(f"{r['periodo']:<15} {r['q5']:>11.1f}% {r['inv']:>11.1f}% {r['random']:>11.1f}% {melhor:>12} ({diff:+.1f}pp)")
    
    # Conclusão final
    print("\n" + "=" * 70)
    print("📋 CONCLUSÃO:")
    print("=" * 70)
    
    vitorias_q5 = sum(1 for r in resumo if r['q5'] > r['inv'])
    vitorias_inv = sum(1 for r in resumo if r['inv'] > r['q5'])
    
    if vitorias_q5 > vitorias_inv:
        print(f"   ✅ Q5 (excluir FRIOS) venceu em {vitorias_q5}/{len(resumo)} períodos")
        print("   → Considerar trocar INVERTIDA por Q5")
    elif vitorias_inv > vitorias_q5:
        print(f"   ✅ INVERTIDA (excluir QUENTES) venceu em {vitorias_inv}/{len(resumo)} períodos")
        print("   → Manter INVERTIDA como default")
    else:
        print("   🟰 Empate técnico - ambas estratégias similares")
    
    # Média geral
    media_q5 = sum(r['q5'] for r in resumo) / len(resumo)
    media_inv = sum(r['inv'] for r in resumo) / len(resumo)
    
    print(f"\n   Média geral Q5:       {media_q5:.1f}%")
    print(f"   Média geral INVERTIDA: {media_inv:.1f}%")
    print(f"   Diferença:            {media_q5 - media_inv:+.1f}pp")
    
    print("\n✅ Backtest concluído!")

if __name__ == '__main__':
    main()
