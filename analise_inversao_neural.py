"""
Análise Neural do padrão de INVERSÃO POSICIONAL
Usa a rede neural existente + features adaptadas para capturar padrões de inversão
"""
import pyodbc
import numpy as np
import sys
import os
from collections import Counter

# Adicionar path dos sistemas
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lotofacil_lite', 'sistemas'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lotofacil_lite', 'interfaces'))

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;')
cursor = conn.cursor()

cursor.execute('''
    SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
           menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
    FROM Resultados_INT
    ORDER BY Concurso
''')
all_rows = []
for r in cursor.fetchall():
    all_rows.append({
        'concurso': r[0],
        'nums': list(r[1:16]),
        'set': set(r[1:16]),
        'menor': r[16] if r[16] is not None else 0,
        'maior': r[17] if r[17] is not None else 0,
        'igual': r[18] if r[18] is not None else 0
    })
conn.close()

print(f"Total concursos: {len(all_rows)}")

# ═══════════════════════════════════════════════════════════════
# 1. ANÁLISE POR POSIÇÃO: Quais posições N1-N15 mais contribuem
#    para menor/maior_que_ultimo quando há inversão?
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("1. CONTRIBUIÇÃO POR POSIÇÃO QUANDO menor >= 12")
print("   Para cada posição, quantas vezes contribuiu para 'menor'")
print("=" * 70)

pos_contrib_menor = [0] * 15  # Quantas vezes posição i contribuiu para "menor"
pos_contrib_maior = [0] * 15
pos_contrib_igual = [0] * 15
total_casos = 0

for i in range(1, len(all_rows)):
    curr = all_rows[i]
    prev = all_rows[i-1]
    
    if curr['menor'] >= 12:
        total_casos += 1
        for p in range(15):
            if curr['nums'][p] < prev['nums'][p]:
                pos_contrib_menor[p] += 1
            elif curr['nums'][p] > prev['nums'][p]:
                pos_contrib_maior[p] += 1
            else:
                pos_contrib_igual[p] += 1

print(f"  Total concursos com menor >= 12: {total_casos}")
print(f"  {'Pos':>5} {'Men%':>6} {'Mai%':>6} {'Igu%':>6} | Direção predominante")
print("  " + "-" * 60)
for p in range(15):
    men_pct = pos_contrib_menor[p] / total_casos * 100
    mai_pct = pos_contrib_maior[p] / total_casos * 100
    igu_pct = pos_contrib_igual[p] / total_casos * 100
    dir_str = "⬇️ MENOR" if men_pct > 60 else ("⬆️ MAIOR" if mai_pct > 60 else "⚖️ misto")
    print(f"  N{p+1:>3} {men_pct:>5.1f}% {mai_pct:>5.1f}% {igu_pct:>5.1f}% | {dir_str}")

# ═══════════════════════════════════════════════════════════════
# 2. DELTA POSICIONAL: Que delta (N - N_anterior) por posição
#    é mais comum quando menor >= 12?
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("2. DELTA POSICIONAL MÉDIO QUANDO menor >= 12")
print("   Delta = num[posição] - num_anterior[posição]")
print("=" * 70)

deltas_extremo = [[] for _ in range(15)]
deltas_normal = [[] for _ in range(15)]

for i in range(1, len(all_rows)):
    curr = all_rows[i]
    prev = all_rows[i-1]
    
    for p in range(15):
        delta = curr['nums'][p] - prev['nums'][p]
        if curr['menor'] >= 12:
            deltas_extremo[p].append(delta)
        else:
            deltas_normal[p].append(delta)

print(f"  {'Pos':>5} {'ExtrMéd':>8} {'NormMéd':>8} {'Diferença':>10} | Interpretação")
print("  " + "-" * 60)
for p in range(15):
    ext_mean = np.mean(deltas_extremo[p]) if deltas_extremo[p] else 0
    nor_mean = np.mean(deltas_normal[p]) if deltas_normal[p] else 0
    diff = ext_mean - nor_mean
    interp = "⬇️ muito diferente" if abs(diff) > 1.5 else ("⬇️ diferente" if abs(diff) > 0.5 else "~ similar")
    print(f"  N{p+1:>3} {ext_mean:>8.2f} {nor_mean:>8.2f} {diff:>+10.2f} | {interp}")

# ═══════════════════════════════════════════════════════════════
# 3. PADRÕES DE SEQUÊNCIA: Qual é o padrão de menor/maior nos 
#    últimos 3-5 concursos antes de uma inversão extrema?
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("3. PADRÕES PRÉ-INVERSÃO (últimos 3 concursos)")
print("   Quando menor >= 13 leva a inversão (prox maior >= 10)")
print("=" * 70)

# Classificar cada concurso: D = desceu (menor>=8), S = subiu (maior>=8), N = neutro
def classificar(menor, maior):
    if menor >= 10:
        return 'D'  # Desceu muito
    elif maior >= 10:
        return 'S'  # Subiu muito
    else:
        return 'N'  # Neutro

# Buscar padrões de 3 antes de inversão
patterns_before_inversion = Counter()
patterns_before_no_inversion = Counter()

for i in range(4, len(all_rows) - 1):
    curr = all_rows[i]
    prox = all_rows[i + 1]
    
    if curr['menor'] >= 13:
        # Padrão dos 3 anteriores
        p1 = classificar(all_rows[i-2]['menor'], all_rows[i-2]['maior'])
        p2 = classificar(all_rows[i-1]['menor'], all_rows[i-1]['maior'])
        p3 = classificar(curr['menor'], curr['maior'])
        pattern = f"{p1}{p2}{p3}"
        
        if prox['maior'] >= 10:
            patterns_before_inversion[pattern] += 1
        else:
            patterns_before_no_inversion[pattern] += 1

print(f"  {'Padrão':>10} {'Inversão':>10} {'Sem inv.':>10} {'Taxa':>8}")
print("  " + "-" * 50)
all_patterns = set(list(patterns_before_inversion.keys()) + list(patterns_before_no_inversion.keys()))
for pat in sorted(all_patterns, key=lambda p: -(patterns_before_inversion.get(p, 0) + patterns_before_no_inversion.get(p, 0))):
    inv = patterns_before_inversion.get(pat, 0)
    no_inv = patterns_before_no_inversion.get(pat, 0)
    total = inv + no_inv
    taxa = inv / total * 100 if total > 0 else 0
    if total >= 3:
        print(f"  {pat:>10} {inv:>10} {no_inv:>10} {taxa:>7.1f}%")

print("\n  Legenda: D=desceu(menor>=10), S=subiu(maior>=10), N=neutro")

# ═══════════════════════════════════════════════════════════════
# 4. REDE NEURAL: Tentar prever menor/maior do próximo concurso
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("4. ANÁLISE NEURAL: Previsão de inversão")
print("=" * 70)

try:
    from disputa_neural_pool23 import RedeNeuralExclusao
    neural_path = os.path.join(os.path.dirname(__file__), 'lotofacil_lite', 'dados', 'neural_exclusao.pkl')
    
    if os.path.exists(neural_path):
        neural = RedeNeuralExclusao.carregar(neural_path)
        print(f"  ✅ Rede neural carregada: {neural_path}")
        
        # Testar: A neural já captura implicitamente padrões de inversão?
        # Vamos comparar scores neurais ANTES de inversões vs não-inversões
        
        scores_before_inversion = []
        scores_before_no_inversion = []
        
        for i in range(30, len(all_rows) - 1):
            curr = all_rows[i]
            prox = all_rows[i+1]
            
            # Calcular features para posição i
            resultados_slice = [{'concurso': all_rows[j]['concurso'], 
                                 'numeros': all_rows[j]['nums'], 
                                 'set': all_rows[j]['set']} 
                                for j in range(i, max(0, i-30), -1)]
            
            features = np.zeros(150)
            for n in range(1, 26):
                features[n-1] = sum(1 for r in resultados_slice[:30] if n in r['set']) / max(1, min(30, len(resultados_slice)))
            for n in range(1, 26):
                atraso = 0
                for r in resultados_slice[:30]:
                    if n in r['set']:
                        break
                    atraso += 1
                features[24 + n] = atraso / 30
            for n in range(1, 26):
                cons = 0
                for r in resultados_slice[:30]:
                    if n in r['set']:
                        cons += 1
                    else:
                        break
                features[49 + n] = cons / 30
            
            freq_10 = Counter()
            for r in resultados_slice[:10]:
                freq_10.update(r['set'])
            freq_ant = Counter()
            for r in resultados_slice[10:20]:
                freq_ant.update(r['set'])
            for n in range(1, 26):
                tend = (freq_10[n] / 10) - (freq_ant.get(n, 0) / max(1, min(10, len(resultados_slice) - 10))) if len(resultados_slice) >= 20 else 0
                features[74 + n] = (tend + 1) / 2
            for n in range(1, 26):
                features[99 + n] = freq_10[n] / 10
            for n in range(1, 26):
                features[124 + n] = 0  # Score invertida placeholder
            
            scores = neural.obter_scores(features)
            
            # Números que a neural sugere EXCLUIR (top scores)
            top_excl = sorted(scores.items(), key=lambda x: -x[1])[:2]
            excluidos_neural = set(n for n, s in top_excl)
            
            # Verificar se os excluídos realmente NÃO saíram
            resultado_prox = prox['set']
            acertou = len(excluidos_neural - resultado_prox)  # Quantos excluídos não saíram
            
            # Classificar se houve inversão
            if curr['menor'] >= 12:
                if prox['maior'] >= 10:
                    scores_before_inversion.append({
                        'concurso': curr['concurso'],
                        'excluidos': list(excluidos_neural),
                        'resultado': sorted(resultado_prox),
                        'acertou_excl': acertou,
                        'top_scores': [(n, round(s, 3)) for n, s in top_excl]
                    })
                else:
                    scores_before_no_inversion.append({
                        'concurso': curr['concurso'],
                        'excluidos': list(excluidos_neural),
                        'resultado': sorted(resultado_prox),
                        'acertou_excl': acertou,
                        'top_scores': [(n, round(s, 3)) for n, s in top_excl]
                    })
        
        print(f"\n  Casos com inversão: {len(scores_before_inversion)}")
        print(f"  Casos sem inversão: {len(scores_before_no_inversion)}")
        
        if scores_before_inversion:
            taxa_acerto_inv = sum(1 for s in scores_before_inversion if s['acertou_excl'] == 2) / len(scores_before_inversion) * 100
            taxa_acerto_no = sum(1 for s in scores_before_no_inversion if s['acertou_excl'] == 2) / len(scores_before_no_inversion) * 100 if scores_before_no_inversion else 0
            
            print(f"\n  Neural acerta exclusão (2/2) com inversão: {taxa_acerto_inv:.1f}%")
            print(f"  Neural acerta exclusão (2/2) sem inversão: {taxa_acerto_no:.1f}%")
            print(f"  Diferença: {taxa_acerto_inv - taxa_acerto_no:+.1f}pp")
            
            if taxa_acerto_inv > taxa_acerto_no + 5:
                print(f"\n  ⚡ A neural PERFORMA MELHOR quando há inversão!")
            elif taxa_acerto_inv < taxa_acerto_no - 5:
                print(f"\n  ⚠️ A neural tem DIFICULDADE com inversões!")
            else:
                print(f"\n  📊 Performance neural SIMILAR em ambos os cenários")
        
        # Últimos 10 casos com inversão
        print(f"\n  Últimos 10 casos de inversão com scores neurais:")
        print(f"  {'Conc':>5} {'Excl Neural':>15} {'Acertou':>8} {'Scores':>25}")
        print("  " + "-" * 60)
        for s in scores_before_inversion[-10:]:
            acert = "✅ 2/2" if s['acertou_excl'] == 2 else f"⚠️ {s['acertou_excl']}/2"
            scores_str = str(s['top_scores'])
            print(f"  {s['concurso']:>5} {str(sorted(s['excluidos'])):>15} {acert:>8} {scores_str:>25}")
    else:
        print(f"  ❌ Modelo neural não encontrado: {neural_path}")
except Exception as e:
    print(f"  ❌ Erro ao carregar neural: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════
# 5. UTILIDADE PARA FILTRO: Se soubermos menor/maior do concurso 
#    atual, que faixa de menor/maior esperar no próximo?
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("5. TABELA DE PREDIÇÃO: Faixa esperada para próximo concurso")
print("   Dado menor_que_ultimo do concurso atual")
print("=" * 70)

faixas = [(0, 3), (4, 7), (8, 10), (11, 13), (14, 15)]
for faixa_men in faixas:
    casos = []
    for i in range(len(all_rows) - 1):
        curr = all_rows[i]
        prox = all_rows[i+1]
        if faixa_men[0] <= curr['menor'] <= faixa_men[1]:
            casos.append(prox['maior'])
    
    if casos:
        print(f"\n  Quando menor = {faixa_men[0]}-{faixa_men[1]} ({len(casos)} casos):")
        print(f"    Próx maior: média={np.mean(casos):.1f}, P25={np.percentile(casos, 25):.0f}, P50={np.percentile(casos, 50):.0f}, P75={np.percentile(casos, 75):.0f}")
        
        # Faixa mais provável do próximo
        prox_baixo = sum(1 for c in casos if c <= 5) / len(casos) * 100
        prox_medio = sum(1 for c in casos if 6 <= c <= 10) / len(casos) * 100
        prox_alto = sum(1 for c in casos if c >= 11) / len(casos) * 100
        print(f"    Próx maior 0-5: {prox_baixo:.1f}% | 6-10: {prox_medio:.1f}% | 11-15: {prox_alto:.1f}%")

print()
print("=" * 70)
print("6. CONCLUSÃO: Aplicabilidade para Pool 23")
print("=" * 70)

# Estatística final
total = len(all_rows) - 1
for limiar in [12, 13, 14]:
    casos_ext = [(all_rows[i], all_rows[i+1]) for i in range(total) if all_rows[i]['menor'] >= limiar]
    inversoes = sum(1 for c, p in casos_ext if p['maior'] >= 10)
    baseline = sum(1 for r in all_rows if r['maior'] >= 10) / len(all_rows) * 100
    taxa = inversoes / len(casos_ext) * 100 if casos_ext else 0
    lift = taxa / baseline if baseline > 0 else 0
    print(f"  menor >= {limiar}: {len(casos_ext)} ocorr, inversão(maior>=10) = {taxa:.1f}% vs baseline {baseline:.1f}% → lift = {lift:.2f}x")
