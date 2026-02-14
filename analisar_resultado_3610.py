# -*- coding: utf-8 -*-
"""
Análise detalhada das combinações vs Resultado 3610
"""
from collections import Counter

# Resultado REAL do concurso 3610
resultado = {1, 3, 5, 7, 8, 10, 13, 14, 17, 20, 21, 22, 23, 24, 25}

# Pools usados
pool_a = {1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23, 24, 25}
pool_b = {2, 5, 15, 17, 18}

arquivo = r'C:\Users\AR CALHAU\source\repos\LotoScope\dados\complementares_reversos_20260211_022556.txt'

print("="*70)
print("📊 ANÁLISE COMPLETA - RESULTADO 3610")
print("="*70)
print(f"\nResultado REAL: {sorted(resultado)}")
print(f"Pool A (20): {sorted(pool_a)}")
print(f"Pool B (5):  {sorted(pool_b)}")

resultado_em_a = resultado & pool_a
resultado_em_b = resultado & pool_b
print(f"\nResultado em Pool A: {len(resultado_em_a)} → {sorted(resultado_em_a)}")
print(f"Resultado em Pool B: {len(resultado_em_b)} → {sorted(resultado_em_b)}")

# Coletar combinações
combos_por_acertos = {15: [], 14: [], 13: [], 12: [], 11: []}
principais = {15: [], 14: [], 13: [], 12: [], 11: []}
reversas = {15: [], 14: [], 13: [], 12: [], 11: []}

print("\nLendo arquivo...")
linha_num = 0
with open(arquivo, 'r', encoding='utf-8') as f:
    for linha in f:
        if linha.startswith('#') or not linha.strip():
            continue
        linha_num += 1
        try:
            nums = tuple(int(x) for x in linha.strip().split(','))
            if len(nums) == 15:
                acertos = len(set(nums) & resultado)
                if acertos >= 11:
                    combos_por_acertos[acertos].append(nums)
                    if linha_num % 2 == 1:  # Ímpar = Principal
                        principais[acertos].append(nums)
                    else:  # Par = Reversa
                        reversas[acertos].append(nums)
        except:
            continue

print(f"Total linhas processadas: {linha_num:,}")

# ========== DISTRIBUIÇÃO GERAL ==========
print("\n" + "="*70)
print("📊 DISTRIBUIÇÃO DE ACERTOS (11+)")
print("="*70)

total_geral = sum(len(v) for v in combos_por_acertos.values())
print(f"\nTotal com 11+ acertos: {total_geral:,}")

for ac in [15, 14, 13, 12, 11]:
    qtd = len(combos_por_acertos[ac])
    pct = qtd / total_geral * 100 if total_geral > 0 else 0
    qtd_p = len(principais[ac])
    qtd_r = len(reversas[ac])
    emoji = {15: '🏆', 14: '💰', 13: '💵', 12: '💲', 11: '🎫'}[ac]
    print(f"   {emoji} {ac} acertos: {qtd:6,} ({pct:5.2f}%)  |  Principal: {qtd_p:,}  |  Reversa: {qtd_r:,}")

# ========== JACKPOT ==========
print("\n" + "="*70)
print("🏆 ANÁLISE DO JACKPOT (15 ACERTOS)")
print("="*70)

for combo in combos_por_acertos[15]:
    combo_set = set(combo)
    em_a = len(combo_set & pool_a)
    em_b = len(combo_set & pool_b)
    print(f"\n   Combinação vencedora: {list(combo)}")
    print(f"   Números do Pool A: {em_a} → {sorted(combo_set & pool_a)}")
    print(f"   Números do Pool B: {em_b} → {sorted(combo_set & pool_b)}")
    
    # Era principal ou reversa?
    if combo in principais[15]:
        print("   Tipo: PRINCIPAL ✅")
    elif combo in reversas[15]:
        print("   Tipo: REVERSA 🔄")

# ========== FREQUÊNCIA POR FAIXA ==========
print("\n" + "="*70)
print("📊 FREQUÊNCIA DE NÚMEROS NAS COMBINAÇÕES VENCEDORAS")
print("="*70)

for faixa in [14, 13, 12, 11]:
    combos = combos_por_acertos[faixa]
    if not combos:
        continue
    
    todos_nums = []
    for combo in combos:
        todos_nums.extend(combo)
    
    freq = Counter(todos_nums)
    
    print(f"\n--- {faixa} ACERTOS ({len(combos):,} combinações) ---")
    print("TOP 10 números mais frequentes:")
    for num, count in freq.most_common(10):
        pct = count / len(combos) * 100
        in_result = '✅' if num in resultado else '❌'
        in_pool = 'A' if num in pool_a else 'B'
        print(f"   {num:02d}: {count:6,} ({pct:5.1f}%) {in_result} Pool {in_pool}")

# ========== NÚMEROS QUE FALTARAM NOS 14 ==========
print("\n" + "="*70)
print("💰 NÚMEROS QUE FALTARAM NAS COMBINAÇÕES DE 14 ACERTOS")
print("="*70)

combos_14 = combos_por_acertos[14]
numeros_faltando = Counter()
for combo in combos_14:
    faltando = resultado - set(combo)
    for num in faltando:
        numeros_faltando[num] += 1

print(f"\n{len(combos_14)} combinações com 14 acertos - qual número faltou?")
for num, count in numeros_faltando.most_common():
    pct = count / len(combos_14) * 100
    in_pool = 'Pool A' if num in pool_a else 'Pool B'
    print(f"   {num:02d}: faltou {count:3d} vezes ({pct:5.1f}%) - {in_pool}")

# ========== ANÁLISE PRINCIPAL vs REVERSA ==========
print("\n" + "="*70)
print("🔄 COMPARAÇÃO: PRINCIPAL vs REVERSA")
print("="*70)

total_principais = sum(len(v) for v in principais.values())
total_reversas = sum(len(v) for v in reversas.values())

print(f"\nTotal PRINCIPAIS com 11+: {total_principais:,}")
print(f"Total REVERSAS com 11+:   {total_reversas:,}")

print(f"\nDistribuição de acertos nas PRINCIPAIS:")
for ac in [15, 14, 13, 12, 11]:
    qtd = len(principais[ac])
    pct = qtd / total_principais * 100 if total_principais > 0 else 0
    print(f"   {ac} acertos: {qtd:6,} ({pct:.2f}%)")

print(f"\nDistribuição de acertos nas REVERSAS:")
for ac in [15, 14, 13, 12, 11]:
    qtd = len(reversas[ac])
    pct = qtd / total_reversas * 100 if total_reversas > 0 else 0
    print(f"   {ac} acertos: {qtd:6,} ({pct:.2f}%)")

# ========== INSIGHT: QUAL POOL DOMINOU? ==========
print("\n" + "="*70)
print("💡 INSIGHT: QUAL POOL DOMINOU NO JACKPOT?")
print("="*70)

print(f"""
O resultado 3610 teve:
   • {len(resultado_em_a)} números do Pool A (esperado ~13 se config 13-13 de A)
   • {len(resultado_em_b)} números do Pool B (esperado ~2 se config 2-2 de B)

Sua configuração foi:
   • Principal: 13-13 de A (13 do pool A + 2 do pool B)
   • Reversa: 2-2 de B

RESULTADO: O resultado REAL teve exatamente {len(resultado_em_a)} de A e {len(resultado_em_b)} de B!
           A configuração estava PERFEITAMENTE ALINHADA! 🎯
""")

print("="*70)
print("FIM DA ANÁLISE")
print("="*70)
