#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
📊 BENCHMARK FOCADO EM 13+ ACERTOS
Compara diferentes estratégias para maximizar 13+ acertos

Autor: LotoScope AI
"""

import sys
import random
from pathlib import Path
from collections import Counter
import statistics

# Paths
_BASE = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE))
sys.path.insert(0, str(_BASE / 'utils'))
sys.path.insert(0, str(_BASE / 'lotofacil_lite'))
sys.path.insert(0, str(_BASE / 'lotofacil_lite' / 'utils'))

try:
    from database_config import db_config
except:
    from lotofacil_lite.utils.database_config import db_config


def carregar_dados():
    """Carrega dados completos do banco"""
    conn = db_config.get_connection()
    cursor = conn.cursor()
    
    # Todos os resultados
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, 
               N9, N10, N11, N12, N13, N14, N15
        FROM RESULTADOS_INT ORDER BY Concurso DESC
    """)
    
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            'concurso': row[0],
            'numeros': set(row[1:16])
        })
    
    cursor.close()
    conn.close()
    return resultados


def analisar_padroes_vencedores(resultados, n_ultimos=100):
    """Analisa padrões dos resultados que teriam dado 13+ em concursos anteriores"""
    
    # Frequência últimos N concursos
    freq_recente = {i: 0 for i in range(1, 26)}
    for r in resultados[:n_ultimos]:
        for n in r['numeros']:
            freq_recente[n] += 1
    
    # Frequência total
    freq_total = {i: 0 for i in range(1, 26)}
    for r in resultados:
        for n in r['numeros']:
            freq_total[n] += 1
    
    # Números quentes e frios
    quentes = sorted(freq_recente.items(), key=lambda x: -x[1])
    
    return {
        'freq_recente': freq_recente,
        'freq_total': freq_total,
        'quentes': [n for n, _ in quentes[:15]],
        'frios': [n for n, _ in quentes[15:]],
        'ultimo': list(resultados[0]['numeros']) if resultados else []
    }


def estrategia_ultra_quentes(dados, n=15):
    """Foca nos números mais quentes com equilíbrio"""
    quentes = dados['quentes'].copy()
    random.shuffle(quentes[:10])  # Alguma variação nos top 10
    
    numeros = set(quentes[:15])
    
    # Garantir equilíbrio par/ímpar
    pares = [n for n in numeros if n % 2 == 0]
    impares = [n for n in numeros if n % 2 == 1]
    
    while len(pares) < 6:
        frios_pares = [n for n in dados['frios'] if n % 2 == 0 and n not in numeros]
        if frios_pares:
            # Remover um ímpar
            if impares:
                numeros.remove(impares.pop())
            numeros.add(frios_pares[0])
            pares = [n for n in numeros if n % 2 == 0]
            impares = [n for n in numeros if n % 2 == 1]
        else:
            break
    
    while len(impares) < 6:
        frios_impares = [n for n in dados['frios'] if n % 2 == 1 and n not in numeros]
        if frios_impares:
            if pares:
                numeros.remove(pares.pop())
            numeros.add(frios_impares[0])
            pares = [n for n in numeros if n % 2 == 0]
            impares = [n for n in numeros if n % 2 == 1]
        else:
            break
    
    return sorted(list(numeros)[:15])


def estrategia_repetidos_otimizada(dados, n=15):
    """Combina números do último resultado com quentes"""
    ultimo = set(dados['ultimo'])
    quentes = set(dados['quentes'])
    
    # 7-8 do último + 7-8 quentes
    numeros = set()
    
    # Interseção (quentes que repetiram)
    inter = ultimo.intersection(quentes)
    numeros.update(inter)
    
    # Completar com quentes
    for q in dados['quentes']:
        if len(numeros) >= 11:
            break
        numeros.add(q)
    
    # Adicionar alguns do último
    for u in ultimo:
        if len(numeros) >= 15:
            break
        numeros.add(u)
    
    # Completar se necessário
    if len(numeros) < 15:
        for n in range(1, 26):
            if len(numeros) >= 15:
                break
            if n not in numeros:
                numeros.add(n)
    
    return sorted(list(numeros)[:15])


def estrategia_distribuida_rigorosa(dados, n=15):
    """Distribuição rigorosa com validação extrema"""
    freq = dados['freq_recente']
    
    # Dividir em 5 faixas
    faixas = {
        1: list(range(1, 6)),
        2: list(range(6, 11)),
        3: list(range(11, 16)),
        4: list(range(16, 21)),
        5: list(range(21, 26))
    }
    
    numeros = set()
    
    # Garantir 3 de cada faixa
    for f_nums in faixas.values():
        ordenados = sorted(f_nums, key=lambda x: -freq[x])
        # Top 2 + 1 aleatório
        numeros.add(ordenados[0])
        numeros.add(ordenados[1])
        numeros.add(random.choice(ordenados[2:]))
    
    return sorted(list(numeros))


def estrategia_soma_ideal(dados, n=15):
    """Busca combinação com soma na zona ideal (180-200)"""
    freq = dados['freq_recente']
    candidatas = []
    
    for _ in range(1000):
        # Gerar candidata
        todos = list(range(1, 26))
        pesos = [freq[n] for n in todos]
        escolhidos = []
        
        for _ in range(15):
            total_peso = sum(pesos)
            if total_peso == 0:
                idx = random.randint(0, len(todos)-1)
            else:
                r = random.random() * total_peso
                acum = 0
                idx = 0
                for i, p in enumerate(pesos):
                    acum += p
                    if r <= acum:
                        idx = i
                        break
            
            escolhidos.append(todos[idx])
            todos.pop(idx)
            pesos.pop(idx)
        
        soma = sum(escolhidos)
        if 180 <= soma <= 200:
            candidatas.append(escolhidos)
    
    if candidatas:
        # Pegar a melhor (mais quentes)
        melhor = max(candidatas, key=lambda c: sum(1 for n in c if n in dados['quentes']))
        return sorted(melhor)
    
    return list(range(1, 16))


def estrategia_mista_13(dados, n=15):
    """Estratégia mista otimizada para 13+"""
    numeros = set()
    
    # 50% quentes
    quentes = dados['quentes'][:12]
    random.shuffle(quentes)
    numeros.update(quentes[:8])
    
    # 30% repetidos do último
    ultimo = list(dados['ultimo'])
    random.shuffle(ultimo)
    for u in ultimo:
        if len(numeros) >= 12:
            break
        numeros.add(u)
    
    # Garantir distribuição
    faixas_faltando = []
    if not any(1 <= n <= 5 for n in numeros):
        faixas_faltando.append(list(range(1, 6)))
    if not any(6 <= n <= 10 for n in numeros):
        faixas_faltando.append(list(range(6, 11)))
    if not any(11 <= n <= 15 for n in numeros):
        faixas_faltando.append(list(range(11, 16)))
    if not any(16 <= n <= 20 for n in numeros):
        faixas_faltando.append(list(range(16, 21)))
    if not any(21 <= n <= 25 for n in numeros):
        faixas_faltando.append(list(range(21, 26)))
    
    for faixa in faixas_faltando:
        if len(numeros) >= 15:
            break
        numeros.add(random.choice(faixa))
    
    # Completar
    todos = list(range(1, 26))
    random.shuffle(todos)
    for t in todos:
        if len(numeros) >= 15:
            break
        if t not in numeros:
            numeros.add(t)
    
    return sorted(list(numeros)[:15])


def gerar_combinacoes_estrategia(estrategia, dados, n_comb=10):
    """Gera múltiplas combinações de uma estratégia"""
    combinacoes = []
    usados = set()
    
    for _ in range(n_comb * 5):  # Tentar várias vezes
        comb = tuple(sorted(estrategia(dados)))
        if comb not in usados:
            usados.add(comb)
            combinacoes.append(set(comb))
        
        if len(combinacoes) >= n_comb:
            break
    
    # Completar se necessário
    while len(combinacoes) < n_comb:
        comb = set(random.sample(range(1, 26), 15))
        combinacoes.append(comb)
    
    return combinacoes[:n_comb]


def avaliar(combinacoes, resultados):
    """Avalia combinações contra resultados"""
    acertos = []
    
    for r in resultados:
        melhor = max(len(c.intersection(r['numeros'])) for c in combinacoes)
        acertos.append(melhor)
    
    return {
        'taxa_11': sum(1 for a in acertos if a >= 11) / len(acertos) * 100,
        'taxa_12': sum(1 for a in acertos if a >= 12) / len(acertos) * 100,
        'taxa_13': sum(1 for a in acertos if a >= 13) / len(acertos) * 100,
        'taxa_14': sum(1 for a in acertos if a >= 14) / len(acertos) * 100,
        'media': statistics.mean(acertos),
        'maximo': max(acertos)
    }


def main():
    print("=" * 70)
    print("📊 BENCHMARK FOCADO EM 13+ ACERTOS")
    print("=" * 70)
    
    resultados = carregar_dados()
    testes = resultados[:30]  # Testar contra 30 últimos
    treino = resultados[30:]  # Usar resto para análise
    
    print(f"📁 {len(resultados)} concursos carregados")
    print(f"📊 Testando contra {len(testes)} concursos")
    
    estrategias = {
        "Ultra Quentes": estrategia_ultra_quentes,
        "Repetidos Otimizada": estrategia_repetidos_otimizada,
        "Distribuída Rigorosa": estrategia_distribuida_rigorosa,
        "Soma Ideal (180-200)": estrategia_soma_ideal,
        "Mista 13+": estrategia_mista_13,
    }
    
    N_ITERACOES = 20
    N_COMBINACOES = 10
    
    print(f"\n🔄 Executando {N_ITERACOES} iterações por estratégia...")
    print(f"📝 {N_COMBINACOES} combinações por iteração\n")
    
    resultados_final = {}
    
    for nome, estrategia in estrategias.items():
        print(f"🔍 Testando: {nome}...", end=" ", flush=True)
        
        taxas_11 = []
        taxas_12 = []
        taxas_13 = []
        taxas_14 = []
        
        for i in range(N_ITERACOES):
            dados = analisar_padroes_vencedores(treino, 100)
            combinacoes = gerar_combinacoes_estrategia(estrategia, dados, N_COMBINACOES)
            metricas = avaliar(combinacoes, testes)
            
            taxas_11.append(metricas['taxa_11'])
            taxas_12.append(metricas['taxa_12'])
            taxas_13.append(metricas['taxa_13'])
            taxas_14.append(metricas['taxa_14'])
        
        media_11 = statistics.mean(taxas_11)
        media_12 = statistics.mean(taxas_12)
        media_13 = statistics.mean(taxas_13)
        media_14 = statistics.mean(taxas_14)
        
        resultados_final[nome] = {
            'taxa_11': media_11,
            'taxa_12': media_12,
            'taxa_13': media_13,
            'taxa_14': media_14,
            'score_13': media_13 * 2 + media_14 * 5  # Peso maior para 13+ e 14+
        }
        
        print(f"13+: {media_13:.1f}%")
    
    # Ranking focado em 13+
    print("\n" + "=" * 70)
    print("🏆 RANKING FOCADO EM 13+ ACERTOS")
    print("=" * 70)
    
    ranking = sorted(resultados_final.items(), key=lambda x: -x[1]['score_13'])
    
    for i, (nome, m) in enumerate(ranking, 1):
        medalha = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i-1]
        print(f"""
{medalha} {nome}:
   • Taxa 11+: {m['taxa_11']:.1f}%
   • Taxa 12+: {m['taxa_12']:.1f}%
   • Taxa 13+: {m['taxa_13']:.1f}% ← FOCO
   • Taxa 14+: {m['taxa_14']:.1f}%
   • Score 13+: {m['score_13']:.1f}
        """)
    
    melhor = ranking[0]
    print("=" * 70)
    print(f"🎯 MELHOR PARA 13+: {melhor[0]}")
    print(f"   Taxa 13+: {melhor[1]['taxa_13']:.1f}%")
    print("=" * 70)
    
    return ranking


if __name__ == "__main__":
    main()
