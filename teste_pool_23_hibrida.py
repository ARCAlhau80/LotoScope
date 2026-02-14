# -*- coding: utf-8 -*-
"""
ESTRATÉGIA POOL 23 - HÍBRIDA: MEDIANO + TENDÊNCIA DESCENDENTE
================================================================
Hipótese: Excluir números que são:
1. Medianos (previsíveis)
2. E estão em TENDÊNCIA DE QUEDA (curto prazo < médio prazo < longo prazo)

A ideia é pegar números que eram medianos mas estão "esfriando" gradualmente.
"""

import pyodbc
from collections import Counter

print("="*70)
print("🧪 ESTRATÉGIA HÍBRIDA: MEDIANO + TENDÊNCIA DESCENDENTE")
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
# FUNÇÃO: Identificar números com tendência descendente + medianos
# ═══════════════════════════════════════════════════════════════════
def identificar_candidatos_exclusao(resultados_anteriores):
    """
    Identifica os 2 melhores candidatos para excluir.
    
    Critérios:
    1. Tendência descendente: freq_curta < freq_media < freq_longa
    2. Não ser extremo (nem muito quente, nem muito frio)
    3. Consistência na queda (sem oscilações bruscas)
    """
    # Calcular frequências em 3 janelas
    JANELA_CURTA = 5
    JANELA_MEDIA = 15
    JANELA_LONGA = 50
    
    def freq_janela(tamanho):
        freq = Counter()
        for r in resultados_anteriores[:tamanho]:
            freq.update(r['numeros'])
        return {n: freq.get(n, 0) / tamanho * 100 for n in range(1, 26)}
    
    freq_curta = freq_janela(JANELA_CURTA)
    freq_media = freq_janela(JANELA_MEDIA)
    freq_longa = freq_janela(JANELA_LONGA)
    
    # Frequência esperada
    freq_esperada = 60  # 15/25 * 100
    
    candidatos = []
    
    for n in range(1, 26):
        fc = freq_curta[n]
        fm = freq_media[n]
        fl = freq_longa[n]
        
        # Critério 1: Tendência descendente (curta < media OU media < longa)
        tendencia_queda = (fc < fm) or (fm < fl)
        queda_forte = fc < fm < fl  # Queda consistente
        
        # Critério 2: Não é extremo
        nao_extremo = 35 < fl < 85  # Entre 35% e 85% na janela longa
        
        # Critério 3: Abaixo da média no curto prazo
        abaixo_curto = fc < freq_esperada
        
        # Score de exclusão
        # Maior = melhor candidato para excluir
        score = 0
        
        if queda_forte:
            score += 3
        elif tendencia_queda:
            score += 1
        
        if nao_extremo:
            score += 2
        
        if abaixo_curto:
            score += 1
        
        # Quanto mais próximo da média na janela longa, melhor
        distancia_media = abs(fl - freq_esperada)
        score += max(0, (30 - distancia_media) / 10)
        
        # Penalizar números muito frequentes no curto prazo
        if fc > 70:
            score *= 0.3
        
        # Penalizar números que não saem há muito tempo (vão voltar)
        if fc < 20:
            score *= 0.5
        
        candidatos.append({
            'num': n,
            'fc': fc,
            'fm': fm,
            'fl': fl,
            'tendencia': 'QUEDA' if queda_forte else ('queda' if tendencia_queda else 'alta'),
            'score': score
        })
    
    # Ordenar por score (maior = excluir)
    candidatos.sort(key=lambda x: -x['score'])
    
    return candidatos

# ═══════════════════════════════════════════════════════════════════
# TESTE EM UM CONCURSO
# ═══════════════════════════════════════════════════════════════════
CONCURSO_ALVO = 3609

idx_alvo = None
for i, r in enumerate(todos_resultados):
    if r['concurso'] == CONCURSO_ALVO:
        idx_alvo = i
        break

resultado_real = todos_resultados[idx_alvo]
resultados_anteriores = todos_resultados[idx_alvo + 1:]

print(f"\n📋 CONCURSO ALVO: {CONCURSO_ALVO}")
print(f"   Resultado REAL: {sorted(resultado_real['numeros'])}")

candidatos = identificar_candidatos_exclusao(resultados_anteriores)

print("\n" + "="*70)
print("📊 ANÁLISE DE CANDIDATOS À EXCLUSÃO")
print("="*70)

print(f"\n{'Num':<4} {'Curta%':>8} {'Media%':>8} {'Longa%':>8} {'Tendência':>10} {'Score':>8} {'Status':<15}")
print("-"*75)

for c in candidatos:
    n = c['num']
    status = ""
    if c == candidatos[0] or c == candidatos[1]:
        status = "❌ EXCLUIR"
    elif c['tendencia'] == 'QUEDA':
        status = "📉 Queda forte"
    elif c['tendencia'] == 'queda':
        status = "📉 Queda leve"
    else:
        status = "📈 Alta"
    
    if n in resultado_real['set']:
        status += " ✓SAIU"
    
    print(f"{n:3d} {c['fc']:>8.1f} {c['fm']:>8.1f} {c['fl']:>8.1f} {c['tendencia']:>10} {c['score']:>8.2f} {status:<15}")

# Top 2 excluir
excluir = [candidatos[0]['num'], candidatos[1]['num']]
pool_23 = sorted([n for n in range(1, 26) if n not in excluir])

print(f"\n{'='*70}")
print(f"🎯 RESULTADO")
print(f"{'='*70}")
print(f"\n❌ EXCLUIR: {sorted(excluir)}")
print(f"✅ POOL 23: {pool_23}")

acertos = len(resultado_real['set'] & set(pool_23))
print(f"\n🎯 Resultado real tem {acertos}/15 no Pool 23")

if acertos == 15:
    print("   🏆 JACKPOT GARANTIDO!")
else:
    fora = sorted(resultado_real['set'] - set(pool_23))
    print(f"   ⚠️ Fora do pool: {fora}")

# ═══════════════════════════════════════════════════════════════════
# BACKTESTING: 100 CONCURSOS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 BACKTESTING: 100 CONCURSOS")
print("="*70)

N_TESTES = 100
resultados_testes = []

for i in range(N_TESTES):
    if i >= len(todos_resultados) - 100:
        break
    
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    candidatos = identificar_candidatos_exclusao(resultados_anteriores)
    excluir = [candidatos[0]['num'], candidatos[1]['num']]
    pool_23 = set([n for n in range(1, 26) if n not in excluir])
    
    acertos = len(resultado_real['set'] & pool_23)
    
    fora = sorted(resultado_real['set'] - pool_23)
    
    resultados_testes.append({
        'concurso': resultado_real['concurso'],
        'acertos': acertos,
        'excluidos': sorted(excluir),
        'sairam': fora
    })

# Estatísticas
acertos_dist = Counter(r['acertos'] for r in resultados_testes)

print(f"\n📈 DISTRIBUIÇÃO DE ACERTOS:")
for ac in sorted(acertos_dist.keys(), reverse=True):
    qtd = acertos_dist[ac]
    pct = qtd / N_TESTES * 100
    barra = "█" * int(pct)
    print(f"   {ac:2d}/15: {qtd:3d} ({pct:5.1f}%) {barra}")

media = sum(r['acertos'] for r in resultados_testes) / N_TESTES
jackpots = sum(1 for r in resultados_testes if r['acertos'] == 15)
taxa_13_mais = sum(1 for r in resultados_testes if r['acertos'] >= 13)
erros = sum(1 for r in resultados_testes if r['acertos'] < 15)

print(f"\n📊 ESTATÍSTICAS:")
print(f"   Média: {media:.2f}/15")
print(f"   Jackpot (15/15): {jackpots}/{N_TESTES} ({100*jackpots/N_TESTES:.1f}%)")
print(f"   Taxa 13+: {taxa_13_mais}/{N_TESTES}")
print(f"   Erros: {erros}/{N_TESTES}")

# ═══════════════════════════════════════════════════════════════════
# COMPARATIVO GERAL
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 COMPARATIVO GERAL DE ESTRATÉGIAS")
print("="*70)

# Recalcular FRIOS
JANELAS = {'ultra_curta': 3, 'curta': 5, 'media': 10, 'media_longa': 15, 'longa': 30, 'ultra_longa': 100}
PESOS = {'ultra_curta': 3.0, 'curta': 2.5, 'media': 2.0, 'media_longa': 1.5, 'longa': 1.0, 'ultra_longa': 0.5}

resultados_frios = []
for i in range(N_TESTES):
    if i >= len(todos_resultados) - 130:
        break
    
    resultado_real = todos_resultados[i]
    resultados_anteriores = todos_resultados[i + 1:]
    
    freq_por_janela = {}
    for nome, tamanho in JANELAS.items():
        freq = Counter()
        for r in resultados_anteriores[:tamanho]:
            freq.update(r['numeros'])
        for n in freq:
            freq[n] = freq[n] / tamanho * 100
        freq_por_janela[nome] = freq
    
    scores = {}
    for n in range(1, 26):
        score = sum(freq_por_janela[nome].get(n, 0) * peso for nome, peso in PESOS.items())
        scores[n] = score
    
    ranking = sorted(scores.items(), key=lambda x: x[1])
    piores_2 = [ranking[0][0], ranking[1][0]]
    pool_23 = set([n for n in range(1, 26) if n not in piores_2])
    
    acertos = len(resultado_real['set'] & pool_23)
    resultados_frios.append({'acertos': acertos})

media_frios = sum(r['acertos'] for r in resultados_frios) / len(resultados_frios)
jackpots_frios = sum(1 for r in resultados_frios if r['acertos'] == 15)
taxa_13_frios = sum(1 for r in resultados_frios if r['acertos'] >= 13)

print(f"\n{'Estratégia':<25} {'Média':>10} {'Jackpot':>12} {'13+':>10}")
print("-"*60)
print(f"{'Excluir FRIOS':<25} {media_frios:>10.2f} {jackpots_frios:>10}/{N_TESTES} {taxa_13_frios:>10}")
print(f"{'HÍBRIDA (Queda+Médio)':<25} {media:>10.2f} {jackpots:>10}/{N_TESTES} {taxa_13_mais:>10}")

# Melhor resultado
if media > media_frios:
    print(f"\n✅ HÍBRIDA é MELHOR (+{media - media_frios:.2f} média)")
elif media_frios > media:
    print(f"\n✅ FRIOS é MELHOR (+{media_frios - media:.2f} média)")
else:
    print(f"\n⚖️ Empate!")

# ═══════════════════════════════════════════════════════════════════
# ANÁLISE: Quais números são mais excluídos com sucesso?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("📊 QUAIS NÚMEROS SÃO EXCLUÍDOS COM MAIS SUCESSO?")
print("="*70)

sucesso_por_numero = {n: {'excluido': 0, 'acertou': 0} for n in range(1, 26)}

for r in resultados_testes:
    for n in r['excluidos']:
        sucesso_por_numero[n]['excluido'] += 1
        if n not in r['sairam']:
            sucesso_por_numero[n]['acertou'] += 1

print(f"\n{'Num':<4} {'Excluído':>10} {'Acertou':>10} {'Taxa%':>10}")
print("-"*40)

ranking_sucesso = []
for n in range(1, 26):
    excluido = sucesso_por_numero[n]['excluido']
    acertou = sucesso_por_numero[n]['acertou']
    taxa = (acertou / excluido * 100) if excluido > 0 else 0
    ranking_sucesso.append((n, excluido, acertou, taxa))

ranking_sucesso.sort(key=lambda x: (-x[3], -x[1]))

for n, excluido, acertou, taxa in ranking_sucesso:
    if excluido > 0:
        status = "🎯" if taxa > 50 else "⚠️" if taxa > 30 else "❌"
        print(f"{n:3d} {excluido:>10} {acertou:>10} {taxa:>9.1f}% {status}")

cursor.close()
conn.close()

print("\n" + "="*70)
print("✅ ANÁLISE CONCLUÍDA!")
print("="*70)
