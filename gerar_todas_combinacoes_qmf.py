"""
Gera TODAS as combinações de 15 números que atendem a regra QMF
Classificação: rank-based (dashboard), qmf_scale=9
Regras: Quentes in (5,6), Mornos in (4,5), Frios in (4,5)
Janela: configurável (default 3)
Geração exaustiva por composição
"""
import sys
from itertools import combinations
from math import comb
from datetime import datetime

sys.path.insert(0, r'C:\Users\AR CALHAU\source\repos\LotoScope')
from shared.database import cached_query

JANELA = 3  # janela de concursos para classificação QMF
QMF_SCALE = 9  # top N = quentes, bottom N = frios

# Carrega últimos JANELA concursos
rows = cached_query(
    f'SELECT TOP {JANELA} Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 '
    'FROM Resultados_INT ORDER BY Concurso DESC'
)

window_nums = []
for row in rows:
    nums = frozenset(row[j] for j in range(1, 16))
    window_nums.append(nums)

# Frequência na janela
freq_janela = {i: 0 for i in range(1, 26)}
for nums in window_nums:
    for n in nums:
        freq_janela[n] += 1

# Frequência total histórica (para desempate dos frios)
freq_total = {i: 0 for i in range(1, 26)}
all_rows = cached_query(
    'SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT'
)
for row in all_rows:
    for j in range(15):
        freq_total[row[j]] += 1

all_nums = list(range(1, 26))

# Classificação QMF rank-based (igual ao dashboard)
# QUENTES: top QMF_SCALE por frequência na janela (desempate: número)
sorted_q = sorted(all_nums, key=lambda n: (-freq_janela[n], n))
quentes = sorted(sorted_q[:QMF_SCALE])

# FRIOS: bottom QMF_SCALE por frequência na janela (desempate: frequência total)
sorted_f = sorted(all_nums, key=lambda n: (freq_janela[n], freq_total[n], n))
frios = sorted(sorted_f[:QMF_SCALE])

# MORNOS: o resto
mornos = sorted(n for n in all_nums if n not in quentes and n not in frios)

print(f"Últimos {JANELA} concursos: {[row[0] for row in rows]}")
print(f"QUENTES (qmf_scale={QMF_SCALE}): {quentes}")
print(f"MORNOS:  {mornos}")
print(f"FRIOS:   {frios}")
print()

# Cálculo do total de combinações válidas
composicoes = []
for hk in [5, 6]:
    for mk in [4, 5]:
        ck = 15 - hk - mk
        if ck < 4 or ck > 5:
            continue
        if hk > len(quentes) or mk > len(mornos) or ck > len(frios):
            continue
        total_comp = comb(len(quentes), hk) * comb(len(mornos), mk) * comb(len(frios), ck)
        composicoes.append((hk, mk, ck, total_comp))
        print(f"  {hk}Q + {mk}M + {ck}F = 15  =>  C({len(quentes)},{hk})*C({len(mornos)},{mk})*C({len(frios)},{ck}) = {total_comp:,}")

total_geral = sum(c[3] for c in composicoes)
print(f"\nTotal de combinações válidas: {total_geral:,}")
pct = total_geral / comb(25, 15) * 100
print(f"Porcentagem do espaço total: {pct:.2f}%")

if total_geral > 2_000_000:
    print("ATENÇÃO: Muitas combinações! O arquivo TXT pode ser grande.")
    resposta = input("Continuar? (s/N): ").strip().lower()
    if resposta != 's':
        print("Cancelado.")
        sys.exit(0)

# Geração exaustiva
print(f"\nGerando todas as {total_geral:,} combinações...")
encontradas = []

for hk, mk, ck, _ in composicoes:
    for h_part in combinations(quentes, hk):
        for m_part in combinations(mornos, mk):
            for f_part in combinations(frios, ck):
                combo = tuple(sorted(h_part + m_part + f_part))
                encontradas.append(combo)

encontradas.sort()

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'combinacoes_qmf_{JANELA}jan_{timestamp}.txt'
filepath = rf'C:\Users\AR CALHAU\source\repos\LotoScope\{filename}'

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(f"TODAS AS COMBINAÇÕES - CLASSIFICAÇÃO QMF (rank-based, qmf_scale={QMF_SCALE})\n")
    f.write(f"Regras: Quentes in (5,6), Mornos in (4,5), Frios in (4,5)\n")
    f.write(f"Janela: {JANELA} concursos\n")
    f.write(f"Últimos concursos: {[row[0] for row in rows]}\n")
    f.write(f"QUENTES ({len(quentes)}): {quentes}\n")
    f.write(f"MORNOS  ({len(mornos)}): {mornos}\n")
    f.write(f"FRIOS   ({len(frios)}): {frios}\n")
    f.write(f"Total: {len(encontradas):,} combinações\n")
    f.write(f"Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    f.write("=" * 60 + "\n\n")
    for i, combo in enumerate(encontradas, 1):
        qtd_q = sum(1 for n in combo if n in quentes)
        qtd_m = sum(1 for n in combo if n in mornos)
        qtd_f = sum(1 for n in combo if n in frios)
        f.write(f"{i:7d}. {str(list(combo)):55s}  Q:{qtd_q} M:{qtd_m} F:{qtd_f}\n")

print(f"\nArquivo salvo: {filename}")
print(f"Caminho: {filepath}")
