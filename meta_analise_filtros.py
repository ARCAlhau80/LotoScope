# -*- coding: utf-8 -*-
"""
META-ANÁLISE DE FILTROS DO POOL 23
===================================
Objetivo: Identificar quais filtros contribuem mais para o ROI
e quais podem estar rejeitando jackpots.

Metodologia:
1. Para cada concurso, verificar se o sorteio real passaria em cada filtro
2. Calcular taxa de aprovação por filtro
3. Identificar filtros "assassinos" (rejeitam muitos jackpots)

Data: 28/03/2026
"""

import pyodbc
from collections import defaultdict

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def obter_concursos(n=300):
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

# ============== FILTROS DO POOL 23 ==============

def filtro_soma(nums, min_val=160, max_val=245):
    """Soma dos 15 números"""
    return min_val <= sum(nums) <= max_val

def filtro_pares(nums, min_val=5, max_val=10):
    """Quantidade de pares"""
    pares = sum(1 for n in nums if n % 2 == 0)
    return min_val <= pares <= max_val

def filtro_primos(nums, min_val=3, max_val=8):
    """Quantidade de primos"""
    primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    qtde = sum(1 for n in nums if n in primos)
    return min_val <= qtde <= max_val

def filtro_fibonacci(nums, min_val=2, max_val=6):
    """Quantidade de Fibonacci"""
    fib = {1, 2, 3, 5, 8, 13, 21}
    qtde = sum(1 for n in nums if n in fib)
    return min_val <= qtde <= max_val

def filtro_faixas(nums, max_faixa=6):
    """Números por faixa de 5"""
    faixas = [0, 0, 0, 0, 0]
    for n in nums:
        faixas[(n-1) // 5] += 1
    return all(f <= max_faixa for f in faixas)

def filtro_qtde_6_25(nums, min_val=10, max_val=13):
    """Quantidade de números entre 6-25"""
    qtde = sum(1 for n in nums if 6 <= n <= 25)
    return min_val <= qtde <= max_val

def filtro_consecutivos(nums, max_cons=5):
    """Máximo de consecutivos"""
    nums_sorted = sorted(nums)
    max_seq = 1
    seq_atual = 1
    for i in range(1, len(nums_sorted)):
        if nums_sorted[i] == nums_sorted[i-1] + 1:
            seq_atual += 1
            max_seq = max(max_seq, seq_atual)
        else:
            seq_atual = 1
    return max_seq <= max_cons

def filtro_extremos(nums, min_extremos=2, max_extremos=4):
    """Extremos (1-5 e 21-25)"""
    extremos = sum(1 for n in nums if n <= 5 or n >= 21)
    return min_extremos <= extremos <= max_extremos

def filtro_linhas(nums):
    """Distribuição por linha (5 linhas de 5 números cada)"""
    linhas = [0, 0, 0, 0, 0]
    for n in nums:
        linhas[(n-1) // 5] += 1
    # Todas linhas devem ter pelo menos 1 e no máximo 5
    return all(1 <= l <= 5 for l in linhas)

def filtro_colunas(nums):
    """Distribuição por coluna (5 colunas)"""
    colunas = [0, 0, 0, 0, 0]
    for n in nums:
        colunas[(n-1) % 5] += 1
    # Todas colunas devem ter pelo menos 1 e no máximo 5
    return all(1 <= c <= 5 for c in colunas)

def filtro_dezenas_altas(nums, min_val=7, max_val=10):
    """Dezenas altas (13-25)"""
    qtde = sum(1 for n in nums if n >= 13)
    return min_val <= qtde <= max_val

def filtro_dezenas_baixas(nums, min_val=5, max_val=8):
    """Dezenas baixas (1-12)"""
    qtde = sum(1 for n in nums if n <= 12)
    return min_val <= qtde <= max_val

# Lista de filtros para testar
FILTROS = {
    'Soma (160-245)': lambda nums: filtro_soma(nums, 160, 245),
    'Pares (5-10)': lambda nums: filtro_pares(nums, 5, 10),
    'Primos (3-8)': lambda nums: filtro_primos(nums, 3, 8),
    'Fibonacci (2-6)': lambda nums: filtro_fibonacci(nums, 2, 6),
    'Faixas (max 6)': lambda nums: filtro_faixas(nums, 6),
    'Qtde 6-25 (10-13)': lambda nums: filtro_qtde_6_25(nums, 10, 13),
    'Consecutivos (max 5)': lambda nums: filtro_consecutivos(nums, 5),
    'Extremos (2-4)': lambda nums: filtro_extremos(nums, 2, 4),
    'Linhas (1-5 cada)': filtro_linhas,
    'Colunas (1-5 cada)': filtro_colunas,
    'Altas 13-25 (7-10)': lambda nums: filtro_dezenas_altas(nums, 7, 10),
    'Baixas 1-12 (5-8)': lambda nums: filtro_dezenas_baixas(nums, 5, 8),
    
    # Filtros mais restritivos (como no código atual)
    'Soma RESTRITO (180-220)': lambda nums: filtro_soma(nums, 180, 220),
    'Pares RESTRITO (6-9)': lambda nums: filtro_pares(nums, 6, 9),
    'Primos RESTRITO (4-7)': lambda nums: filtro_primos(nums, 4, 7),
    'Consecutivos RESTRITO (max 3)': lambda nums: filtro_consecutivos(nums, 3),
}

def main():
    print("=" * 80)
    print("🔬 META-ANÁLISE DE FILTROS DO POOL 23")
    print("=" * 80)
    
    concursos = obter_concursos(300)
    print(f"\n📊 Analisando {len(concursos)} sorteios reais")
    
    # Analisa cada filtro
    resultados = {}
    
    for nome, filtro_func in FILTROS.items():
        aprovados = 0
        rejeitados = 0
        
        for row in concursos:
            nums = [row[i] for i in range(1, 16)]
            if filtro_func(nums):
                aprovados += 1
            else:
                rejeitados += 1
        
        taxa = aprovados / len(concursos) * 100
        resultados[nome] = {
            'aprovados': aprovados,
            'rejeitados': rejeitados,
            'taxa': taxa
        }
    
    # Ordena por taxa de aprovação (menor = mais restritivo)
    ordenado = sorted(resultados.items(), key=lambda x: x[1]['taxa'])
    
    print("\n" + "=" * 80)
    print("📊 TAXA DE APROVAÇÃO POR FILTRO (sorteios reais):")
    print("=" * 80)
    
    print(f"\n{'Filtro':<30} {'Aprovados':>10} {'Taxa':>10} {'Status':>15}")
    print("-" * 80)
    
    for nome, r in ordenado:
        taxa = r['taxa']
        
        # Classificação
        if taxa >= 95:
            status = "✅ OK"
        elif taxa >= 85:
            status = "🟡 Atenção"
        elif taxa >= 70:
            status = "⚠️ Restritivo"
        else:
            status = "❌ ASSASSINO"
        
        bar = "█" * int(taxa / 5)
        print(f"{nome:<30} {r['aprovados']:>10} {taxa:>9.1f}% {status:>15}")
    
    # Análise de filtros combinados
    print("\n" + "=" * 80)
    print("📊 ANÁLISE DE FILTROS COMBINADOS:")
    print("=" * 80)
    
    # Filtros do Level 1 (básicos)
    filtros_level1 = ['Soma (160-245)', 'Pares (5-10)', 'Qtde 6-25 (10-13)']
    
    # Filtros do Level 3 (moderados)
    filtros_level3 = filtros_level1 + ['Primos (3-8)', 'Fibonacci (2-6)', 'Faixas (max 6)']
    
    # Filtros do Level 6 (máximos)
    filtros_level6 = list(FILTROS.keys())[:12]  # Todos os filtros não-restritivos
    
    def testar_combinacao(concursos, nomes_filtros):
        aprovados = 0
        for row in concursos:
            nums = [row[i] for i in range(1, 16)]
            passa_todos = all(FILTROS[nome](nums) for nome in nomes_filtros if nome in FILTROS)
            if passa_todos:
                aprovados += 1
        return aprovados / len(concursos) * 100
    
    print("\n   Combinações de filtros:")
    
    taxa_l1 = testar_combinacao(concursos, filtros_level1)
    taxa_l3 = testar_combinacao(concursos, filtros_level3)
    taxa_l6 = testar_combinacao(concursos, filtros_level6)
    
    print(f"   Level 1 (básico):   {taxa_l1:.1f}% aprovação")
    print(f"   Level 3 (moderado): {taxa_l3:.1f}% aprovação")
    print(f"   Level 6 (máximo):   {taxa_l6:.1f}% aprovação")
    
    # Identificar filtros "assassinos"
    print("\n" + "=" * 80)
    print("🎯 FILTROS ASSASSINOS (rejeitam muitos jackpots):")
    print("=" * 80)
    
    assassinos = [(nome, r) for nome, r in resultados.items() if r['taxa'] < 85]
    
    if assassinos:
        print("\n   ⚠️ Estes filtros rejeitam >15% dos sorteios reais:")
        for nome, r in sorted(assassinos, key=lambda x: x[1]['taxa']):
            print(f"      - {nome}: {r['taxa']:.1f}% aprovação (rejeita {r['rejeitados']} jackpots)")
    else:
        print("\n   ✅ Nenhum filtro individual rejeita >15% dos sorteios")
    
    # Recomendações
    print("\n" + "=" * 80)
    print("💡 RECOMENDAÇÕES:")
    print("=" * 80)
    
    # Filtros seguros (>95% aprovação)
    seguros = [nome for nome, r in resultados.items() if r['taxa'] >= 95]
    print(f"\n   ✅ Filtros SEGUROS (>95% aprovação):")
    for nome in seguros:
        print(f"      - {nome}: {resultados[nome]['taxa']:.1f}%")
    
    # Filtros a evitar (<85% aprovação)
    evitar = [nome for nome, r in resultados.items() if r['taxa'] < 85]
    if evitar:
        print(f"\n   ❌ Filtros a EVITAR ou RELAXAR (<85% aprovação):")
        for nome in evitar:
            print(f"      - {nome}: {resultados[nome]['taxa']:.1f}%")
    
    # Análise de impacto incremental
    print("\n" + "=" * 80)
    print("📈 IMPACTO INCREMENTAL (cada filtro adicionado):")
    print("=" * 80)
    
    # Começa sem filtros (100%)
    # Adiciona um a um e vê o impacto
    
    filtros_ordem = [
        'Soma (160-245)',
        'Pares (5-10)',
        'Qtde 6-25 (10-13)',
        'Primos (3-8)',
        'Fibonacci (2-6)',
        'Consecutivos (max 5)',
        'Linhas (1-5 cada)',
        'Colunas (1-5 cada)',
        'Extremos (2-4)',
    ]
    
    taxa_anterior = 100.0
    filtros_ativos = []
    
    print(f"\n   {'Após adicionar':<25} {'Taxa':>10} {'Impacto':>12}")
    print("-" * 50)
    print(f"   {'(sem filtros)':<25} {'100.0%':>10} {'-':>12}")
    
    for nome in filtros_ordem:
        if nome not in FILTROS:
            continue
        filtros_ativos.append(nome)
        taxa = testar_combinacao(concursos, filtros_ativos)
        impacto = taxa - taxa_anterior
        
        emoji = "✅" if impacto > -3 else ("🟡" if impacto > -10 else "❌")
        print(f"   {nome:<25} {taxa:>9.1f}% {impacto:>+10.1f}pp {emoji}")
        
        taxa_anterior = taxa
    
    print("\n✅ Meta-análise concluída!")

if __name__ == '__main__':
    main()
