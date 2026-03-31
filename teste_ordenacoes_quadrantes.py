# -*- coding: utf-8 -*-
"""
Teste de Ordenações Alternativas para Quadrantes
=================================================
Hipótese: A ordenação sequencial (1-5, 6-10...) é arbitrária.
         Ordenaçõões baseadas em critérios estatísticos podem performar melhor.

Ordenações testadas:
1. Sequencial (baseline atual)
2. Por frequência global
3. Por frequência recente (últimos 30)
4. Temperatura mista (hot→cold)
5. Por posição dominante
6. Pares/Ímpares agrupados

Data: 28/03/2026
"""

import pyodbc
from collections import defaultdict
from itertools import combinations

# Conexão SQL Server
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def obter_concursos(n_concursos=200):
    """Busca últimos N concursos"""
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

def calcular_frequencia_global(concursos):
    """Calcula frequência de cada número em todos os concursos"""
    freq = defaultdict(int)
    for row in concursos:
        nums = [row[i] for i in range(1, 16)]
        for n in nums:
            freq[n] += 1
    return dict(freq)

def calcular_frequencia_recente(concursos, n_recentes=30):
    """Calcula frequência nos últimos N concursos"""
    freq = defaultdict(int)
    for row in concursos[:n_recentes]:
        nums = [row[i] for i in range(1, 16)]
        for n in nums:
            freq[n] += 1
    return dict(freq)

def calcular_posicao_dominante(concursos):
    """Para cada número, calcula a posição média onde aparece"""
    posicoes = defaultdict(list)
    for row in concursos:
        nums = [row[i] for i in range(1, 16)]
        for pos, n in enumerate(nums, 1):
            posicoes[n].append(pos)
    
    # Média de posição para cada número
    pos_media = {}
    for n in range(1, 26):
        if posicoes[n]:
            pos_media[n] = sum(posicoes[n]) / len(posicoes[n])
        else:
            pos_media[n] = 8  # Centro
    return pos_media

def criar_quadrantes_sequencial():
    """Ordenação sequencial (1-5, 6-10, 11-15, 16-20, 21-25)"""
    return {
        'Q1': [1, 2, 3, 4, 5],
        'Q2': [6, 7, 8, 9, 10],
        'Q3': [11, 12, 13, 14, 15],
        'Q4': [16, 17, 18, 19, 20],
        'Q5': [21, 22, 23, 24, 25]
    }

def criar_quadrantes_frequencia(freq_dict):
    """Ordena por frequência: Q1=top5 frequentes, Q5=menos frequentes"""
    ordenado = sorted(range(1, 26), key=lambda x: freq_dict.get(x, 0), reverse=True)
    return {
        'Q1': ordenado[0:5],
        'Q2': ordenado[5:10],
        'Q3': ordenado[10:15],
        'Q4': ordenado[15:20],
        'Q5': ordenado[20:25]
    }

def criar_quadrantes_temperatura(freq_recente, freq_global):
    """Combina frequência recente e global para 'temperatura'"""
    # Score = 2*freq_recente + freq_global (peso maior para recente)
    max_recente = max(freq_recente.values()) if freq_recente else 1
    max_global = max(freq_global.values()) if freq_global else 1
    
    scores = {}
    for n in range(1, 26):
        rec_norm = freq_recente.get(n, 0) / max_recente
        glob_norm = freq_global.get(n, 0) / max_global
        scores[n] = 2 * rec_norm + glob_norm
    
    ordenado = sorted(range(1, 26), key=lambda x: scores[x], reverse=True)
    return {
        'Q1_HOT': ordenado[0:5],
        'Q2_WARM': ordenado[5:10],
        'Q3_AVG': ordenado[10:15],
        'Q4_COOL': ordenado[15:20],
        'Q5_COLD': ordenado[20:25]
    }

def criar_quadrantes_posicional(pos_media):
    """Agrupa por posição média onde o número aparece"""
    ordenado = sorted(range(1, 26), key=lambda x: pos_media.get(x, 8))
    return {
        'Q1_INICIO': ordenado[0:5],     # Aparecem mais no início (N1-N3)
        'Q2_MEIO1': ordenado[5:10],
        'Q3_CENTRO': ordenado[10:15],   # Aparecem no centro (N7-N9)
        'Q4_MEIO2': ordenado[15:20],
        'Q5_FIM': ordenado[20:25]       # Aparecem mais no fim (N13-N15)
    }

def criar_quadrantes_paridade(freq_dict):
    """Separa pares e ímpares, ordena cada grupo por frequência"""
    pares = [n for n in range(1, 26) if n % 2 == 0]
    impares = [n for n in range(1, 26) if n % 2 == 1]
    
    pares_ord = sorted(pares, key=lambda x: freq_dict.get(x, 0), reverse=True)
    impares_ord = sorted(impares, key=lambda x: freq_dict.get(x, 0), reverse=True)
    
    return {
        'Q1_PAR_HOT': pares_ord[0:5],      # 5 pares mais frequentes (2,4,6,8,10,12 tem 6 pares)
        'Q2_PAR_COLD': pares_ord[5:10] + [pares_ord[10]] if len(pares_ord) > 10 else pares_ord[5:],
        'Q3_IMPAR_HOT': impares_ord[0:5],  # 5 ímpares mais frequentes
        'Q4_IMPAR_MID': impares_ord[5:10],
        'Q5_IMPAR_COLD': impares_ord[10:13]  # 3 restantes
    }

def criar_quadrantes_zigzag(freq_dict):
    """Intercala números de alta e baixa frequência em cada quadrante"""
    ordenado = sorted(range(1, 26), key=lambda x: freq_dict.get(x, 0), reverse=True)
    
    # Intercala: 1º, último, 2º, penúltimo...
    zigzag = []
    left, right = 0, 24
    while left <= right:
        if left == right:
            zigzag.append(ordenado[left])
        else:
            zigzag.append(ordenado[left])
            zigzag.append(ordenado[right])
        left += 1
        right -= 1
    
    return {
        'Q1_ZIG': zigzag[0:5],
        'Q2_ZIG': zigzag[5:10],
        'Q3_ZIG': zigzag[10:15],
        'Q4_ZIG': zigzag[15:20],
        'Q5_ZIG': zigzag[20:25]
    }

def avaliar_ordenacao(quadrantes, concursos_teste, nome):
    """Avalia uma ordenação de quadrantes"""
    # Pega apenas os valores numéricos (ignora nomes dos quadrantes)
    quads = list(quadrantes.values())
    
    # Todas combinações de 3 quadrantes
    melhores = []
    
    for combo_idx in combinations(range(5), 3):
        # Junta os 3 quadrantes selecionados
        numeros = []
        nomes_q = list(quadrantes.keys())
        for i in combo_idx:
            numeros.extend(quads[i])
        numeros_set = set(numeros)
        
        # Se não tem 15 números, pula
        if len(numeros_set) != 15:
            continue
        
        # Conta acertos
        acertos_11 = 0
        acertos_15 = 0
        
        for row in concursos_teste:
            sorteio = set([row[i] for i in range(1, 16)])
            acertos = len(numeros_set & sorteio)
            if acertos >= 11:
                acertos_11 += 1
            if acertos == 15:
                acertos_15 += 1
        
        nome_combo = '+'.join([nomes_q[i] for i in combo_idx])
        taxa = acertos_11 / len(concursos_teste) * 100
        melhores.append({
            'combo': nome_combo,
            'numeros': sorted(numeros_set),
            'taxa_11': taxa,
            'jackpots': acertos_15
        })
    
    # Ordena por taxa
    melhores.sort(key=lambda x: x['taxa_11'], reverse=True)
    return melhores

def main():
    print("=" * 70)
    print("🔬 TESTE DE ORDENAÇÕES ALTERNATIVAS PARA QUADRANTES")
    print("=" * 70)
    
    # Busca dados
    print("\n📊 Buscando dados...")
    concursos = obter_concursos(200)  # Últimos 200 para análise
    print(f"   {len(concursos)} concursos carregados")
    
    # Divide: 100 para análise, 100 para teste
    concursos_analise = concursos[100:]  # 101-200 (mais antigos)
    concursos_teste = concursos[:100]     # 1-100 (mais recentes)
    
    print(f"   Análise: {len(concursos_analise)} concursos")
    print(f"   Teste: {len(concursos_teste)} concursos")
    
    # Calcula métricas na base de análise
    print("\n📈 Calculando métricas...")
    freq_global = calcular_frequencia_global(concursos_analise)
    freq_recente = calcular_frequencia_recente(concursos_analise, 30)
    pos_media = calcular_posicao_dominante(concursos_analise)
    
    # Cria diferentes ordenações
    ordenacoes = {
        '1. SEQUENCIAL (baseline)': criar_quadrantes_sequencial(),
        '2. FREQUÊNCIA GLOBAL': criar_quadrantes_frequencia(freq_global),
        '3. FREQUÊNCIA RECENTE': criar_quadrantes_frequencia(freq_recente),
        '4. TEMPERATURA MISTA': criar_quadrantes_temperatura(freq_recente, freq_global),
        '5. POSICIONAL': criar_quadrantes_posicional(pos_media),
        '6. ZIG-ZAG (mista)': criar_quadrantes_zigzag(freq_global),
    }
    
    # Mostra composição de cada ordenação
    print("\n" + "=" * 70)
    print("📋 COMPOSIÇÃO DE CADA ORDENAÇÃO:")
    print("=" * 70)
    
    for nome, quads in ordenacoes.items():
        print(f"\n🔹 {nome}")
        for q_nome, numeros in quads.items():
            print(f"   {q_nome}: {numeros}")
    
    # Avalia cada ordenação
    print("\n" + "=" * 70)
    print("📊 AVALIAÇÃO NOS 100 CONCURSOS MAIS RECENTES:")
    print("=" * 70)
    
    resultados_gerais = []
    
    for nome, quads in ordenacoes.items():
        print(f"\n🔹 {nome}")
        resultados = avaliar_ordenacao(quads, concursos_teste, nome)
        
        if resultados:
            melhor = resultados[0]
            pior = resultados[-1]
            media = sum(r['taxa_11'] for r in resultados) / len(resultados)
            
            print(f"   📈 Melhor combo: {melhor['combo']}")
            print(f"      Taxa ≥11: {melhor['taxa_11']:.1f}% | Jackpots: {melhor['jackpots']}")
            print(f"      Números: {melhor['numeros']}")
            print(f"   📉 Pior combo: {pior['combo']}")
            print(f"      Taxa ≥11: {pior['taxa_11']:.1f}%")
            print(f"   📊 Média: {media:.1f}%")
            
            resultados_gerais.append({
                'ordenacao': nome,
                'melhor_taxa': melhor['taxa_11'],
                'melhor_combo': melhor['combo'],
                'melhor_numeros': melhor['numeros'],
                'jackpots': melhor['jackpots'],
                'media': media
            })
    
    # Ranking final
    print("\n" + "=" * 70)
    print("🏆 RANKING FINAL (por melhor taxa de cada ordenação):")
    print("=" * 70)
    
    resultados_gerais.sort(key=lambda x: x['melhor_taxa'], reverse=True)
    
    for i, r in enumerate(resultados_gerais, 1):
        medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "  "))
        print(f"{medal} {i}. {r['ordenacao']}")
        print(f"      Melhor: {r['melhor_taxa']:.1f}% ({r['melhor_combo']})")
        print(f"      Jackpots: {r['jackpots']} | Média: {r['media']:.1f}%")
    
    # Comparação com baseline
    baseline_random = 60  # Taxa esperada com 15 números aleatórios
    melhor_geral = resultados_gerais[0] if resultados_gerais else None
    
    print("\n" + "=" * 70)
    print("📈 COMPARAÇÃO COM BASELINE (60% random):")
    print("=" * 70)
    
    if melhor_geral:
        diff = melhor_geral['melhor_taxa'] - baseline_random
        if diff >= 0:
            print(f"   ✅ Melhor ordenação: {melhor_geral['melhor_taxa']:.1f}% (+{diff:.1f}pp)")
            print(f"   ✅ VALE IMPLEMENTAR!")
        else:
            print(f"   ❌ Melhor ordenação: {melhor_geral['melhor_taxa']:.1f}% ({diff:.1f}pp)")
            print(f"   ❌ Abaixo do baseline - NÃO vale implementar")
    
    # Sugestões de próximos testes
    print("\n" + "=" * 70)
    print("💡 SUGESTÕES DE PRÓXIMOS TESTES:")
    print("=" * 70)
    print("""
    1. QUADRANTES DE 4 NÚMEROS (30 combinatórias vs 10 atuais)
       - Mais flexibilidade, menos restrição
    
    2. QUADRANTES SOBREPOSTOS
       - Q1 e Q2 compartilham 2 números
       - Captura transições
    
    3. ORDENAÇÃO POR CONSECUTIVIDADE
       - Números que aparecem juntos frequentemente
       - Baseado em Association Rules
    
    4. QUADRANTES DINÂMICOS
       - Recalcula a cada concurso baseado em janela móvel
       - Adapta-se às tendências atuais
    
    5. HÍBRIDO: 23 números (Pool 23) + Quadrantes
       - Usa quadrantes apenas para escolher os 2 a excluir
       - Mantém a vantagem do Pool 23
    """)
    
    print("\n✅ Análise concluída!")

if __name__ == '__main__':
    main()
