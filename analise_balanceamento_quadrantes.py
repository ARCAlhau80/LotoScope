# -*- coding: utf-8 -*-
"""
Teste: BALANCEAMENTO por Quadrantes
====================================
Hipótese: Combinações vencedoras tendem a ter números distribuídos
em múltiplos quadrantes (anti-concentração).

Análise:
1. Como os sorteios reais se distribuem por quadrante?
2. Existe um padrão de distribuição que indica maior chance?

Data: 28/03/2026
"""

import pyodbc
from collections import defaultdict, Counter

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def obter_concursos(n=500):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {n} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def definir_quadrantes():
    """Quadrantes sequenciais (baseline)"""
    return {
        'Q1': set([1, 2, 3, 4, 5]),
        'Q2': set([6, 7, 8, 9, 10]),
        'Q3': set([11, 12, 13, 14, 15]),
        'Q4': set([16, 17, 18, 19, 20]),
        'Q5': set([21, 22, 23, 24, 25]),
    }

def analisar_distribuicao_quadrantes(concursos):
    """Analisa como os sorteios se distribuem por quadrante"""
    quadrantes = definir_quadrantes()
    
    distribuicoes = []
    
    for row in concursos:
        sorteio = set([row[i] for i in range(1, 16)])
        
        # Conta quantos números de cada quadrante
        dist = {}
        for nome, nums in quadrantes.items():
            dist[nome] = len(sorteio & nums)
        
        # Formato: Q1-Q2-Q3-Q4-Q5 (ex: 3-3-3-3-3)
        padrao = f"{dist['Q1']}-{dist['Q2']}-{dist['Q3']}-{dist['Q4']}-{dist['Q5']}"
        
        distribuicoes.append({
            'concurso': row[0],
            'dist': dist,
            'padrao': padrao,
            'min': min(dist.values()),
            'max': max(dist.values()),
            'range': max(dist.values()) - min(dist.values()),
            'qtde_quadrantes': sum(1 for v in dist.values() if v > 0)
        })
    
    return distribuicoes

def main():
    print("=" * 70)
    print("🔬 ANÁLISE DE BALANCEAMENTO POR QUADRANTES")
    print("=" * 70)
    
    concursos = obter_concursos(500)
    print(f"\n📊 Analisando {len(concursos)} concursos")
    
    # Análise de distribuição
    distribuicoes = analisar_distribuicao_quadrantes(concursos)
    
    # Estatísticas de qtde de quadrantes usados
    print("\n" + "=" * 70)
    print("📊 QUANTOS QUADRANTES SÃO USADOS EM CADA SORTEIO:")
    print("=" * 70)
    
    qtde_counter = Counter([d['qtde_quadrantes'] for d in distribuicoes])
    for qtde in sorted(qtde_counter.keys()):
        pct = qtde_counter[qtde] / len(distribuicoes) * 100
        bar = "█" * int(pct / 2)
        print(f"   {qtde} quadrantes: {qtde_counter[qtde]:>4} ({pct:>5.1f}%) {bar}")
    
    # Estatísticas de range (diferença max-min)
    print("\n" + "=" * 70)
    print("📊 RANGE (diferença entre quadrante mais cheio e mais vazio):")
    print("=" * 70)
    
    range_counter = Counter([d['range'] for d in distribuicoes])
    for rng in sorted(range_counter.keys()):
        pct = range_counter[rng] / len(distribuicoes) * 100
        bar = "█" * int(pct / 2)
        print(f"   Range {rng}: {range_counter[rng]:>4} ({pct:>5.1f}%) {bar}")
    
    # Padrões mais comuns
    print("\n" + "=" * 70)
    print("📊 TOP 15 PADRÕES DE DISTRIBUIÇÃO (Q1-Q2-Q3-Q4-Q5):")
    print("=" * 70)
    
    padrao_counter = Counter([d['padrao'] for d in distribuicoes])
    for padrao, count in padrao_counter.most_common(15):
        pct = count / len(distribuicoes) * 100
        print(f"   {padrao}: {count:>4} ({pct:>5.1f}%)")
    
    # Análise: sorteios "balanceados" (range ≤ 2) vs "concentrados" (range > 2)
    print("\n" + "=" * 70)
    print("📊 BALANCEADOS vs CONCENTRADOS:")
    print("=" * 70)
    
    balanceados = [d for d in distribuicoes if d['range'] <= 2]
    concentrados = [d for d in distribuicoes if d['range'] > 2]
    
    pct_bal = len(balanceados) / len(distribuicoes) * 100
    pct_conc = len(concentrados) / len(distribuicoes) * 100
    
    print(f"\n   Balanceados (range ≤ 2): {len(balanceados)} ({pct_bal:.1f}%)")
    print(f"   Concentrados (range > 2): {len(concentrados)} ({pct_conc:.1f}%)")
    
    # Padrão mais comum de balanceados
    print("\n   Padrões mais comuns dos BALANCEADOS:")
    bal_padroes = Counter([d['padrao'] for d in balanceados])
    for padrao, count in bal_padroes.most_common(5):
        pct = count / len(balanceados) * 100
        print(f"      {padrao}: {count} ({pct:.1f}%)")
    
    # Insight para filtro
    print("\n" + "=" * 70)
    print("💡 INSIGHT PARA FILTRO:")
    print("=" * 70)
    
    # Distribuição por quadrante individual
    soma_q = {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0, 'Q5': 0}
    for d in distribuicoes:
        for q, v in d['dist'].items():
            soma_q[q] += v
    
    media_q = {q: v / len(distribuicoes) for q, v in soma_q.items()}
    
    print("\n   Média de números por quadrante:")
    for q, media in media_q.items():
        bar = "█" * int(media * 5)
        print(f"      {q}: {media:.1f} números {bar}")
    
    # Recomendação
    print("\n   RECOMENDAÇÃO:")
    
    # Qual range aparece em 90%+ dos sorteios?
    ranges_acumulado = 0
    range_90 = None
    for rng in sorted(range_counter.keys()):
        ranges_acumulado += range_counter[rng]
        if ranges_acumulado / len(distribuicoes) >= 0.90:
            range_90 = rng
            break
    
    print(f"   → Range ≤ {range_90} cobre 90%+ dos sorteios")
    print(f"   → Filtrar combinações com range > {range_90} pode eliminar outliers")
    
    # Filtro prático
    print("\n" + "=" * 70)
    print("🎯 FILTRO PROPOSTO (BALANCEAMENTO POR QUADRANTES):")
    print("=" * 70)
    
    print(f"""
    Regra: Para cada combinação gerada, calcular distribuição por quadrante.
    
    ACEITAR se:
    - Range (max - min) ≤ {range_90}
    - Usa pelo menos 4 quadrantes
    - Nenhum quadrante tem 0 ou 5 números (extremos)
    
    REJEITAR se:
    - Range > {range_90} (muito concentrado)
    - Usa apenas 3 quadrantes ou menos
    """)
    
    # Simula impacto do filtro
    aprovados = 0
    rejeitados = 0
    
    for d in distribuicoes:
        if d['range'] <= range_90 and d['qtde_quadrantes'] >= 4:
            aprovados += 1
        else:
            rejeitados += 1
    
    print(f"   Simulação retrospectiva:")
    print(f"   - Aprovados: {aprovados} ({aprovados/len(distribuicoes)*100:.1f}%)")
    print(f"   - Rejeitados: {rejeitados} ({rejeitados/len(distribuicoes)*100:.1f}%)")
    
    if rejeitados / len(distribuicoes) < 0.05:
        print("\n   ⚠️ ATENÇÃO: Filtro rejeitaria <5% - pouco impacto!")
    else:
        print(f"\n   ✅ Filtro rejeitaria {rejeitados/len(distribuicoes)*100:.1f}% das combinações")
    
    print("\n✅ Análise concluída!")

if __name__ == '__main__':
    main()
