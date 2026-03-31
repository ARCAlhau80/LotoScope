# -*- coding: utf-8 -*-
"""
Teste: Quadrantes como Filtro de EXCLUSÃO (Pool 23 Híbrido)
============================================================
Hipótese: Usar quadrantes para escolher quais 2 números EXCLUIR
         em vez de quais 15 incluir.

Abordagem:
- Q5 (números menos frequentes) → candidatos à exclusão
- Combina: Q5 como "danger zone" + análise clássica de exclusão

Data: 28/03/2026
"""

import pyodbc
from collections import defaultdict
from itertools import combinations

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def obter_concursos(n_concursos=200):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {n_concursos} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def calcular_frequencia(concursos, n_recentes=None):
    freq = defaultdict(int)
    dados = concursos[:n_recentes] if n_recentes else concursos
    for row in dados:
        nums = [row[i] for i in range(1, 16)]
        for n in nums:
            freq[n] += 1
    return dict(freq)

def criar_quadrantes_por_frequencia(freq_dict):
    """Q1=mais frequentes, Q5=menos frequentes"""
    ordenado = sorted(range(1, 26), key=lambda x: freq_dict.get(x, 0), reverse=True)
    return {
        'Q1': ordenado[0:5],
        'Q2': ordenado[5:10],
        'Q3': ordenado[10:15],
        'Q4': ordenado[15:20],
        'Q5': ordenado[20:25]  # MENOS frequentes → candidatos à exclusão
    }

def avaliar_exclusao(numeros_excluir, concursos_teste):
    """Avalia excluir 2 números específicos (pool de 23)"""
    pool23 = set(range(1, 26)) - set(numeros_excluir)
    
    acertos_11 = 0
    jackpots = 0
    
    for row in concursos_teste:
        sorteio = set([row[i] for i in range(1, 16)])
        
        # Quantos dos excluídos foram sorteados?
        excluidos_sorteados = len(set(numeros_excluir) & sorteio)
        
        # Se excluiu corretamente (0 excluídos foram sorteados) = jackpot possível
        # Se 1 excluído foi sorteado = 14 acertos possíveis
        # Se 2 excluídos foram sorteados = 13 acertos possíveis
        
        acertos_max = 15 - excluidos_sorteados
        
        if excluidos_sorteados == 0:
            jackpots += 1
        if acertos_max >= 11:  # Ainda garante prêmio
            acertos_11 += 1
    
    return {
        'excluidos': numeros_excluir,
        'taxa_premio': acertos_11 / len(concursos_teste) * 100,
        'taxa_jackpot': jackpots / len(concursos_teste) * 100,
        'jackpots': jackpots
    }

def main():
    print("=" * 70)
    print("🔬 TESTE: QUADRANTES COMO FILTRO DE EXCLUSÃO (POOL 23)")
    print("=" * 70)
    
    # Busca dados
    print("\n📊 Buscando dados...")
    concursos = obter_concursos(200)
    concursos_analise = concursos[100:]  # Para calcular frequências
    concursos_teste = concursos[:100]     # Para testar
    
    print(f"   {len(concursos_teste)} concursos de teste")
    
    # Calcula frequências na base de análise
    freq_global = calcular_frequencia(concursos_analise)
    freq_recente = calcular_frequencia(concursos_analise, 30)
    
    # Cria quadrantes por frequência
    quads_global = criar_quadrantes_por_frequencia(freq_global)
    quads_recente = criar_quadrantes_por_frequencia(freq_recente)
    
    print("\n📋 Q5 (menos frequentes - candidatos à exclusão):")
    print(f"   Global: {quads_global['Q5']}")
    print(f"   Recente: {quads_recente['Q5']}")
    
    # Estratégias de exclusão baseadas em quadrantes
    estrategias = {
        'E1: Q5[0] + Q5[1] (global)': quads_global['Q5'][:2],
        'E2: Q5[0] + Q5[1] (recente)': quads_recente['Q5'][:2],
        'E3: Q5[0] + Q4[4] (global)': [quads_global['Q5'][0], quads_global['Q4'][4]],
        'E4: Q5[0] + Q4[4] (recente)': [quads_recente['Q5'][0], quads_recente['Q4'][4]],
        'E5: Q5[0] + Q5[2] (global)': [quads_global['Q5'][0], quads_global['Q5'][2]],
        'E6: Q5 random (2 de 5)': quads_global['Q5'][1:3],  # Exemplo
    }
    
    # Adiciona todas combinações de Q5
    print("\n📊 Testando TODAS combinações de 2 números de Q5 (global):")
    for combo in combinations(quads_global['Q5'], 2):
        nome = f'Q5: {list(combo)}'
        estrategias[nome] = list(combo)
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS POR ESTRATÉGIA:")
    print("=" * 70)
    
    resultados = []
    for nome, excluir in estrategias.items():
        r = avaliar_exclusao(excluir, concursos_teste)
        r['nome'] = nome
        resultados.append(r)
    
    # Ordena por taxa de jackpot
    resultados.sort(key=lambda x: x['taxa_jackpot'], reverse=True)
    
    print(f"\n{'Estratégia':<35} {'Exclui':<12} {'Jackpot%':>10} {'Premio%':>10}")
    print("-" * 70)
    
    for r in resultados[:15]:  # Top 15
        print(f"{r['nome']:<35} {str(r['excluidos']):<12} {r['taxa_jackpot']:>9.1f}% {r['taxa_premio']:>9.1f}%")
    
    # Comparação com baseline
    print("\n" + "=" * 70)
    print("📈 COMPARAÇÃO COM BASELINES:")
    print("=" * 70)
    
    melhor = resultados[0]
    
    # Baseline 1: Exclusão RANDOM (média de todas as 300 combinações)
    todas_exclusoes = list(combinations(range(1, 26), 2))
    taxas_random = []
    for combo in todas_exclusoes:
        r = avaliar_exclusao(list(combo), concursos_teste)
        taxas_random.append(r['taxa_jackpot'])
    media_random = sum(taxas_random) / len(taxas_random)
    
    print(f"   Exclusão RANDOM (média 300 combos): {media_random:.1f}% jackpot")
    print(f"   Melhor Q5: {melhor['taxa_jackpot']:.1f}% jackpot ({melhor['excluidos']})")
    
    diff = melhor['taxa_jackpot'] - media_random
    if diff > 0:
        print(f"   ✅ Q5 é +{diff:.1f}pp SUPERIOR à exclusão aleatória!")
    else:
        print(f"   ❌ Q5 é {diff:.1f}pp abaixo da exclusão aleatória")
    
    # Baseline 2: Pool 23 com INVERTIDA v3.0 (exclusão dos 2 mais quentes)
    # Simula: exclui os 2 com mais consecutivas + freq alta
    freq_ordenada = sorted(range(1, 26), key=lambda x: freq_recente.get(x, 0), reverse=True)
    excluir_invertida = freq_ordenada[:2]  # 2 mais quentes
    r_invertida = avaliar_exclusao(excluir_invertida, concursos_teste)
    
    print(f"\n   INVERTIDA v3.0 (2 mais quentes): {r_invertida['taxa_jackpot']:.1f}% ({excluir_invertida})")
    
    # Conclusão
    print("\n" + "=" * 70)
    print("🎯 CONCLUSÃO:")
    print("=" * 70)
    
    if melhor['taxa_jackpot'] > r_invertida['taxa_jackpot']:
        print(f"   ✅ Quadrante Q5 ({melhor['taxa_jackpot']:.1f}%) SUPERA INVERTIDA v3.0 ({r_invertida['taxa_jackpot']:.1f}%)")
        print(f"      → Vale integrar como opção no Pool 23!")
    elif melhor['taxa_jackpot'] == r_invertida['taxa_jackpot']:
        print(f"   🟰 Empate técnico: Q5 = INVERTIDA = {melhor['taxa_jackpot']:.1f}%")
        print(f"      → Pode usar qualquer uma")
    else:
        print(f"   ❌ INVERTIDA v3.0 ({r_invertida['taxa_jackpot']:.1f}%) ainda é SUPERIOR a Q5 ({melhor['taxa_jackpot']:.1f}%)")
        print(f"      → Manter INVERTIDA como default")
    
    print("\n✅ Análise concluída!")

if __name__ == '__main__':
    main()
