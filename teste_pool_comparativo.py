# -*- coding: utf-8 -*-
"""
COMPARATIVO: POOL 22 vs POOL 23 vs POOL 21
============================================
Testando qual tamanho de pool é ideal usando estratégia híbrida.

Pool 22 = Excluir 3 números
Pool 23 = Excluir 2 números  
Pool 21 = Excluir 4 números (bônus)

Combinações:
- C(21,15) = 54.264
- C(22,15) = 170.544
- C(23,15) = 490.314
"""

import pyodbc
from collections import Counter

print("="*70)
print("🧪 COMPARATIVO: POOL 21 vs POOL 22 vs POOL 23")
print("="*70)

# Conexão
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 FROM Resultados_INT ORDER BY Concurso DESC")
rows = cursor.fetchall()

todos_resultados = []
for row in rows:
    nums = [row[i] for i in range(1, 16)]
    todos_resultados.append({
        'concurso': row[0],
        'numeros': nums,
        'set': set(nums)
    })

print(f"✅ {len(todos_resultados)} concursos carregados")

# ═══════════════════════════════════════════════════════════════════
# FUNÇÃO: Estratégia Híbrida (Mediano + Tendência de Queda)
# ═══════════════════════════════════════════════════════════════════
def identificar_candidatos_exclusao(resultados_anteriores, n_excluir=2):
    """
    Identifica os N melhores candidatos para excluir usando estratégia híbrida.
    """
    JANELA_CURTA = 5
    JANELA_MEDIA = 15
    JANELA_LONGA = 50
    
    def freq_janela(tamanho):
        freq = Counter()
        for r in resultados_anteriores[:min(tamanho, len(resultados_anteriores))]:
            freq.update(r['numeros'])
        return {n: freq.get(n, 0) / min(tamanho, len(resultados_anteriores)) * 100 for n in range(1, 26)}
    
    freq_curta = freq_janela(JANELA_CURTA)
    freq_media = freq_janela(JANELA_MEDIA)
    freq_longa = freq_janela(JANELA_LONGA)
    
    freq_esperada = 60
    
    candidatos = []
    
    for n in range(1, 26):
        fc = freq_curta[n]
        fm = freq_media[n]
        fl = freq_longa[n]
        
        # Tendência descendente
        queda_forte = fc < fm < fl
        tendencia_queda = (fc < fm) or (fm < fl)
        
        # Não é extremo
        nao_extremo = 35 < fl < 85
        
        # Abaixo da média no curto prazo
        abaixo_curto = fc < freq_esperada
        
        # Score
        score = 0
        
        if queda_forte:
            score += 3
        elif tendencia_queda:
            score += 1
        
        if nao_extremo:
            score += 2
        
        if abaixo_curto:
            score += 1
        
        distancia_media = abs(fl - freq_esperada)
        score += max(0, (30 - distancia_media) / 10)
        
        if fc > 70:
            score *= 0.3
        
        if fc < 20:
            score *= 0.5
        
        candidatos.append({'num': n, 'score': score, 'fc': fc, 'fm': fm, 'fl': fl})
    
    candidatos.sort(key=lambda x: -x['score'])
    
    return [c['num'] for c in candidatos[:n_excluir]]

# ═══════════════════════════════════════════════════════════════════
# BACKTESTING: Comparar Pool 21, 22, 23
# ═══════════════════════════════════════════════════════════════════
N_TESTES = 100

resultados = {
    'Pool 21 (excluir 4)': {'acertos': [], 'jackpots': 0, 'taxa_13': 0},
    'Pool 22 (excluir 3)': {'acertos': [], 'jackpots': 0, 'taxa_13': 0},
    'Pool 23 (excluir 2)': {'acertos': [], 'jackpots': 0, 'taxa_13': 0},
}

print("\n⏳ Processando backtesting...")

for i in range(N_TESTES):
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    # Pool 21 (excluir 4)
    excluir_4 = identificar_candidatos_exclusao(resultados_anteriores, 4)
    pool_21 = set([n for n in range(1, 26) if n not in excluir_4])
    acertos_21 = len(resultado_real['set'] & pool_21)
    resultados['Pool 21 (excluir 4)']['acertos'].append(acertos_21)
    if acertos_21 == 15:
        resultados['Pool 21 (excluir 4)']['jackpots'] += 1
    if acertos_21 >= 13:
        resultados['Pool 21 (excluir 4)']['taxa_13'] += 1
    
    # Pool 22 (excluir 3)
    excluir_3 = identificar_candidatos_exclusao(resultados_anteriores, 3)
    pool_22 = set([n for n in range(1, 26) if n not in excluir_3])
    acertos_22 = len(resultado_real['set'] & pool_22)
    resultados['Pool 22 (excluir 3)']['acertos'].append(acertos_22)
    if acertos_22 == 15:
        resultados['Pool 22 (excluir 3)']['jackpots'] += 1
    if acertos_22 >= 13:
        resultados['Pool 22 (excluir 3)']['taxa_13'] += 1
    
    # Pool 23 (excluir 2)
    excluir_2 = identificar_candidatos_exclusao(resultados_anteriores, 2)
    pool_23 = set([n for n in range(1, 26) if n not in excluir_2])
    acertos_23 = len(resultado_real['set'] & pool_23)
    resultados['Pool 23 (excluir 2)']['acertos'].append(acertos_23)
    if acertos_23 == 15:
        resultados['Pool 23 (excluir 2)']['jackpots'] += 1
    if acertos_23 >= 13:
        resultados['Pool 23 (excluir 2)']['taxa_13'] += 1

# ═══════════════════════════════════════════════════════════════════
# RESULTADOS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 RESULTADOS COMPARATIVOS")
print("="*70)

# Combinações por pool
combinacoes = {
    'Pool 21 (excluir 4)': 54264,
    'Pool 22 (excluir 3)': 170544,
    'Pool 23 (excluir 2)': 490314,
}

print(f"\n{'Pool':<22} {'Combos':>12} {'Média':>8} {'Jackpot':>10} {'13+':>8} {'12+':>8}")
print("-"*70)

for nome, dados in resultados.items():
    media = sum(dados['acertos']) / len(dados['acertos'])
    jackpot_pct = dados['jackpots'] / N_TESTES * 100
    taxa_13_pct = dados['taxa_13'] / N_TESTES * 100
    taxa_12 = sum(1 for a in dados['acertos'] if a >= 12) / N_TESTES * 100
    combos = combinacoes[nome]
    
    print(f"{nome:<22} {combos:>12,} {media:>8.2f} {jackpot_pct:>9.1f}% {taxa_13_pct:>7.1f}% {taxa_12:>7.1f}%")

# Distribuição detalhada
print("\n" + "="*70)
print("📈 DISTRIBUIÇÃO DE ACERTOS")
print("="*70)

for nome, dados in resultados.items():
    print(f"\n{nome}:")
    dist = Counter(dados['acertos'])
    for ac in sorted(dist.keys(), reverse=True):
        qtd = dist[ac]
        pct = qtd / N_TESTES * 100
        barra = "█" * int(pct / 2)
        print(f"   {ac:2d}/15: {qtd:3d} ({pct:5.1f}%) {barra}")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE DE ERROS POR POOL
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("🔍 ANÁLISE: QUANDO EXCLUÍMOS CERTO?")
print("="*70)

# Detalhes dos últimos 10 concursos
print("\n📋 Últimos 10 concursos (comparativo):")
print(f"{'#':<8} {'Real':^35} {'P21':>6} {'P22':>6} {'P23':>6}")
print("-"*70)

for i in range(10):
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    excluir_4 = identificar_candidatos_exclusao(resultados_anteriores, 4)
    excluir_3 = identificar_candidatos_exclusao(resultados_anteriores, 3)
    excluir_2 = identificar_candidatos_exclusao(resultados_anteriores, 2)
    
    pool_21 = set([n for n in range(1, 26) if n not in excluir_4])
    pool_22 = set([n for n in range(1, 26) if n not in excluir_3])
    pool_23 = set([n for n in range(1, 26) if n not in excluir_2])
    
    ac_21 = len(resultado_real['set'] & pool_21)
    ac_22 = len(resultado_real['set'] & pool_22)
    ac_23 = len(resultado_real['set'] & pool_23)
    
    real_str = str(sorted(resultado_real['numeros']))
    
    # Marcar jackpots
    mk_21 = "🏆" if ac_21 == 15 else f"{ac_21:2d}"
    mk_22 = "🏆" if ac_22 == 15 else f"{ac_22:2d}"
    mk_23 = "🏆" if ac_23 == 15 else f"{ac_23:2d}"
    
    print(f"{resultado_real['concurso']:<8} {real_str:^35} {mk_21:>6} {mk_22:>6} {mk_23:>6}")
    
    # Mostrar excluídos
    print(f"{'':8} Excluídos: P21={sorted(excluir_4)}, P22={sorted(excluir_3)}, P23={sorted(excluir_2)}")
    print()

# ═══════════════════════════════════════════════════════════════════
# RECOMENDAÇÃO FINAL
# ═══════════════════════════════════════════════════════════════════
print("="*70)
print("🎯 RECOMENDAÇÃO FINAL")
print("="*70)

# Qual é melhor?
media_21 = sum(resultados['Pool 21 (excluir 4)']['acertos']) / N_TESTES
media_22 = sum(resultados['Pool 22 (excluir 3)']['acertos']) / N_TESTES
media_23 = sum(resultados['Pool 23 (excluir 2)']['acertos']) / N_TESTES

jackpot_21 = resultados['Pool 21 (excluir 4)']['jackpots']
jackpot_22 = resultados['Pool 22 (excluir 3)']['jackpots']
jackpot_23 = resultados['Pool 23 (excluir 2)']['jackpots']

print(f"""
┌───────────────────────────────────────────────────────────────────┐
│                    ANÁLISE COMPARATIVA                            │
├───────────────────────────────────────────────────────────────────┤
│  Pool 21 (54k combos):   Média {media_21:.2f}/15, Jackpot {jackpot_21}%                │
│  Pool 22 (170k combos):  Média {media_22:.2f}/15, Jackpot {jackpot_22}%               │
│  Pool 23 (490k combos):  Média {media_23:.2f}/15, Jackpot {jackpot_23}%               │
├───────────────────────────────────────────────────────────────────┤
""")

# Determinar vencedor
melhor = max([
    ('Pool 21', jackpot_21, media_21, 54264),
    ('Pool 22', jackpot_22, media_22, 170544),
    ('Pool 23', jackpot_23, media_23, 490314),
], key=lambda x: (x[1], x[2]))

print(f"│  🏆 VENCEDOR: {melhor[0]} com {melhor[1]}% jackpot e média {melhor[2]:.2f}        │")
print(f"│     Combinações: {melhor[3]:,} (filtros reduzem para ~1000)         │")
print("└───────────────────────────────────────────────────────────────────┘")

cursor.close()
conn.close()

print("\n✅ Análise concluída!")
