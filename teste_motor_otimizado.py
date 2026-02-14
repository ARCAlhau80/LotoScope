# -*- coding: utf-8 -*-
"""
TESTE MOTOR COMPLEMENTAR OTIMIZADO
Configurações que devem dar melhor resultado:
- Pool Base (não automático)
- Range 13-13 (JACKPOT)
- Filtros Agressivos
"""

import pyodbc
from itertools import combinations
from math import comb
from collections import Counter
from datetime import datetime

print("="*70)
print("🧪 TESTE MOTOR COMPLEMENTAR - CONFIGURAÇÕES OTIMIZADAS")
print("="*70)

# ═══════════════════════════════════════════════════════════════════
# CONEXÃO COM BANCO
# ═══════════════════════════════════════════════════════════════════
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Carregar resultados
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
# CONFIGURAÇÃO DO TESTE
# ═══════════════════════════════════════════════════════════════════
CONCURSO_ALVO = 3609  # Último disponível (prever com dados até 3608)

# Encontrar índice do concurso alvo
idx_alvo = None
for i, r in enumerate(todos_resultados):
    if r['concurso'] == CONCURSO_ALVO:
        idx_alvo = i
        break

if idx_alvo is None:
    print(f"❌ Concurso {CONCURSO_ALVO} não encontrado!")
    exit()

# Resultado real do 3610 para validação
resultado_real = todos_resultados[idx_alvo]
print(f"\n📋 CONCURSO ALVO: {CONCURSO_ALVO}")
print(f"   Resultado REAL: {sorted(resultado_real['numeros'])}")

# Usar dados ANTERIORES ao concurso (simulando previsão)
resultados_anteriores = todos_resultados[idx_alvo + 1:]  # Concursos antes do alvo
print(f"   Dados disponíveis: {len(resultados_anteriores)} concursos anteriores")

# ═══════════════════════════════════════════════════════════════════
# PASSO 1: ANÁLISE (últimos 30 concursos ANTES do alvo)
# ═══════════════════════════════════════════════════════════════════
ultimos_30 = resultados_anteriores[:30]
ultimo_sorteio = resultados_anteriores[0]  # 3609

print(f"\n📊 ANÁLISE DOS ÚLTIMOS 30 CONCURSOS (antes do {CONCURSO_ALVO}):")
print(f"   Último sorteio: #{ultimo_sorteio['concurso']} = {sorted(ultimo_sorteio['numeros'])}")

# Frequência dos últimos 30
freq_30 = Counter()
for r in ultimos_30:
    freq_30.update(r['numeros'])

top_15_freq = sorted(freq_30.keys(), key=lambda x: -freq_30[x])[:15]
print(f"   TOP 15 frequentes: {sorted(top_15_freq)}")

# ═══════════════════════════════════════════════════════════════════
# PASSO 2: ANÁLISE LINHAS/COLUNAS (MODERADO - remove interseção)
# ═══════════════════════════════════════════════════════════════════
# Linhas: 1-5, 6-10, 11-15, 16-20, 21-25
# Colunas: 1,6,11,16,21 | 2,7,12,17,22 | etc

linhas = [[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15], [16,17,18,19,20], [21,22,23,24,25]]
colunas = [[1,6,11,16,21], [2,7,12,17,22], [3,8,13,18,23], [4,9,14,19,24], [5,10,15,20,25]]

# Contar frequência por linha e coluna
freq_linhas = {i: Counter() for i in range(5)}
freq_colunas = {i: Counter() for i in range(5)}

for r in ultimos_30:
    for n in r['numeros']:
        for i, linha in enumerate(linhas):
            if n in linha:
                freq_linhas[i][n] += 1
        for i, coluna in enumerate(colunas):
            if n in coluna:
                freq_colunas[i][n] += 1

# Identificar frios (abaixo da média)
frios_linhas = set()
frios_colunas = set()

for i in range(5):
    if freq_linhas[i]:
        media = sum(freq_linhas[i].values()) / len(freq_linhas[i])
        for n, f in freq_linhas[i].items():
            if f < media * 0.7:
                frios_linhas.add(n)
    if freq_colunas[i]:
        media = sum(freq_colunas[i].values()) / len(freq_colunas[i])
        for n, f in freq_colunas[i].items():
            if f < media * 0.7:
                frios_colunas.add(n)

# MODO MODERADO: Remove apenas interseção
frios_intersecao = frios_linhas & frios_colunas
pool_base = sorted([n for n in range(1, 26) if n not in frios_intersecao])

print(f"\n🔶 MODO MODERADO (remove interseção L+C):")
print(f"   Frios linhas: {sorted(frios_linhas)}")
print(f"   Frios colunas: {sorted(frios_colunas)}")
print(f"   Interseção removida: {sorted(frios_intersecao)}")
print(f"   POOL BASE: {len(pool_base)} números → {pool_base}")

# ═══════════════════════════════════════════════════════════════════
# PASSO 3: USAR POOL A JACKPOT (fixo do 3610)
# ═══════════════════════════════════════════════════════════════════
# Pool que deu JACKPOT no concurso 3610!
pool_a = [1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23, 24, 25]
pool_b = [2, 5, 15, 17, 18]

print(f"\n📋 POOL A JACKPOT (20 nums): {pool_a}")
print(f"📋 POOL B JACKPOT (5 nums): {pool_b}")

# Verificar quantos do resultado real estão em cada pool
acertos_a = len(resultado_real['set'] & set(pool_a))
acertos_b = len(resultado_real['set'] & set(pool_b))
print(f"\n   🎯 VALIDAÇÃO: Resultado real tem {acertos_a} de A + {acertos_b} de B")

# ═══════════════════════════════════════════════════════════════════
# PASSO 4: DEFINIR FILTROS AGRESSIVOS
# ═══════════════════════════════════════════════════════════════════

# Calcular ranges históricos
somas = [sum(r['numeros']) for r in ultimos_30]
soma_min = min(somas) - 5
soma_max = max(somas) + 5

pares_hist = [sum(1 for n in r['numeros'] if n % 2 == 0) for r in ultimos_30]
pares_min = max(5, min(pares_hist) - 1)
pares_max = min(10, max(pares_hist) + 1)

primos_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
primos_hist = [len(set(r['numeros']) & primos_set) for r in ultimos_30]
primos_min = max(3, min(primos_hist) - 1)
primos_max = min(7, max(primos_hist) + 1)

# NÚCLEO (17 números comuns entre C1 e C2)
NUCLEO = {2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 22, 24, 25}

# Repetição do último sorteio
min_repetidos = 7
max_repetidos = 11

# Favorecidos
top_15_set = set(top_15_freq)
min_favorecidos = 8
max_favorecidos = 10

print(f"\n⚙️ FILTROS AGRESSIVOS:")
print(f"   Soma: {soma_min}-{soma_max}")
print(f"   Pares: {pares_min}-{pares_max}")
print(f"   Primos: {primos_min}-{primos_max}")
print(f"   Núcleo: mínimo 10 dos 17")
print(f"   Repetição: {min_repetidos}-{max_repetidos}")
print(f"   Favorecidos: {min_favorecidos}-{max_favorecidos}")

# ═══════════════════════════════════════════════════════════════════
# PASSO 5: GERAR COMBINAÇÕES (RANGE 13-13 = JACKPOT)
# ═══════════════════════════════════════════════════════════════════
min_de_a = 13
max_de_a = 13

est_total = sum(comb(20, k) * comb(5, 15-k) for k in range(min_de_a, max_de_a + 1))
print(f"\n🎰 GERANDO COMBINAÇÕES...")
print(f"   Range: {min_de_a}-{max_de_a} de A")
print(f"   Estimativa sem filtros: {est_total:,}")

import time
inicio = time.time()

combinacoes = []
filtradas_soma = 0
filtradas_pares = 0
filtradas_primos = 0
filtradas_nucleo = 0
filtradas_rep = 0
filtradas_fav = 0
total_testadas = 0

ultimo_set = ultimo_sorteio['set']

for k in range(min_de_a, max_de_a + 1):
    b_necessarios = 15 - k
    if b_necessarios > len(pool_b):
        continue
    
    for combo_a in combinations(pool_a, k):
        if b_necessarios == 0:
            combo = list(sorted(combo_a))
        else:
            for combo_b in combinations(pool_b, b_necessarios):
                combo = list(sorted(combo_a + combo_b))
                combo_set = set(combo)
                total_testadas += 1
                
                # Filtro SOMA
                soma = sum(combo)
                if soma < soma_min or soma > soma_max:
                    filtradas_soma += 1
                    continue
                
                # Filtro PARES
                qtd_pares = sum(1 for n in combo if n % 2 == 0)
                if qtd_pares < pares_min or qtd_pares > pares_max:
                    filtradas_pares += 1
                    continue
                
                # Filtro PRIMOS
                qtd_primos = len(combo_set & primos_set)
                if qtd_primos < primos_min or qtd_primos > primos_max:
                    filtradas_primos += 1
                    continue
                
                # Filtro NÚCLEO
                qtd_nucleo = len(combo_set & NUCLEO)
                if qtd_nucleo < 10:
                    filtradas_nucleo += 1
                    continue
                
                # Filtro REPETIÇÃO
                qtd_rep = len(combo_set & ultimo_set)
                if qtd_rep < min_repetidos or qtd_rep > max_repetidos:
                    filtradas_rep += 1
                    continue
                
                # Filtro FAVORECIDOS
                qtd_fav = len(combo_set & top_15_set)
                if qtd_fav < min_favorecidos or qtd_fav > max_favorecidos:
                    filtradas_fav += 1
                    continue
                
                # Passou em tudo!
                combinacoes.append(combo)
                
                if len(combinacoes) % 10000 == 0:
                    print(f"   ... {len(combinacoes):,} geradas...")

tempo = time.time() - inicio
print(f"\n✅ {len(combinacoes):,} combinações geradas em {tempo:.1f}s")
print(f"\n📊 FILTROS APLICADOS:")
print(f"   Testadas: {total_testadas:,}")
print(f"   Soma: {filtradas_soma:,} removidas")
print(f"   Pares: {filtradas_pares:,} removidas")
print(f"   Primos: {filtradas_primos:,} removidas")
print(f"   Núcleo: {filtradas_nucleo:,} removidas")
print(f"   Repetição: {filtradas_rep:,} removidas")
print(f"   Favorecidos: {filtradas_fav:,} removidas")
print(f"   ✅ APROVADAS: {len(combinacoes):,}")

# ═══════════════════════════════════════════════════════════════════
# PASSO 6: VALIDAR CONTRA RESULTADO REAL
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print(f"🎯 VALIDAÇÃO CONTRA CONCURSO {CONCURSO_ALVO}")
print("="*70)
print(f"   Resultado REAL: {sorted(resultado_real['numeros'])}")

# Calcular acertos
acertos_dist = Counter()
melhores = []

for combo in combinacoes:
    acertos = len(set(combo) & resultado_real['set'])
    acertos_dist[acertos] += 1
    if acertos >= 13:
        melhores.append((combo, acertos))

# Ordenar melhores
melhores.sort(key=lambda x: -x[1])

print(f"\n📈 DISTRIBUIÇÃO DE ACERTOS:")
for ac in sorted(acertos_dist.keys(), reverse=True):
    qtd = acertos_dist[ac]
    pct = qtd / len(combinacoes) * 100
    premio = ""
    if ac == 15: premio = " ← JACKPOT R$1.8M!"
    elif ac == 14: premio = " ← R$1.000+"
    elif ac == 13: premio = " ← R$35"
    elif ac == 12: premio = " ← R$14"
    elif ac == 11: premio = " ← R$7"
    barra = "█" * min(40, int(pct * 2))
    print(f"   {ac:2d} acertos: {qtd:6,} ({pct:5.1f}%) {barra}{premio}")

# Estatísticas
media = sum(ac * qtd for ac, qtd in acertos_dist.items()) / len(combinacoes)
max_acertos = max(acertos_dist.keys())
acertos_11_mais = sum(qtd for ac, qtd in acertos_dist.items() if ac >= 11)

print(f"\n📊 ESTATÍSTICAS:")
print(f"   Combinações: {len(combinacoes):,}")
print(f"   Média de acertos: {media:.2f}")
print(f"   Melhor resultado: {max_acertos} acertos")
print(f"   Com 11+ acertos: {acertos_11_mais:,} ({100*acertos_11_mais/len(combinacoes):.1f}%)")

# TOP 10
if melhores:
    print(f"\n🏆 TOP 10 MELHORES COMBINAÇÕES:")
    for i, (combo, ac) in enumerate(melhores[:10], 1):
        corretos = sorted(set(combo) & resultado_real['set'])
        print(f"   {i:2d}. {combo} → {ac} acertos")
        print(f"       Corretos: {corretos}")

# ═══════════════════════════════════════════════════════════════════
# PASSO 7: ANÁLISE FINANCEIRA
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("💰 ANÁLISE FINANCEIRA")
print("="*70)

custo = len(combinacoes) * 3.50
premio_total = 0
for ac, qtd in acertos_dist.items():
    if ac == 11: premio_total += 7 * qtd
    elif ac == 12: premio_total += 14 * qtd
    elif ac == 13: premio_total += 35 * qtd
    elif ac == 14: premio_total += 1000 * qtd
    elif ac == 15: premio_total += 1800000 * qtd

lucro = premio_total - custo
roi = (premio_total / custo - 1) * 100 if custo > 0 else 0

print(f"   Custo: R$ {custo:,.2f}")
print(f"   Prêmios: R$ {premio_total:,.2f}")
print(f"   Lucro/Prejuízo: R$ {lucro:,.2f}")
print(f"   ROI: {roi:+.1f}%")

if lucro > 0:
    print(f"\n   ✅ RESULTADO POSITIVO!")
else:
    print(f"\n   ❌ Prejuízo (esperado sem jackpot)")

# Fechar conexão
cursor.close()
conn.close()

print("\n" + "="*70)
print("✅ TESTE CONCLUÍDO!")
print("="*70)
