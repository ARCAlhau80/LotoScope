"""
Gera TODAS as combinações de 15 números com classificação térmica (janela 3 concursos)
Regras: 5-6 Quentes, 4-5 Mornos, 4-5 Frios
Geração exaustiva (não amostragem)
"""
import sys
from itertools import combinations
from math import comb
from datetime import datetime

sys.path.insert(0, r'C:\Users\AR CALHAU\source\repos\LotoScope')
from shared.database import cached_query

rows = cached_query(
    'SELECT TOP 3 Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 '
    'FROM Resultados_INT ORDER BY Concurso DESC'
)

window = []
for row in rows:
    nums = frozenset(row[j] for j in range(1, 16))
    window.append(nums)

freq = {i: 0 for i in range(1, 26)}
for nums in window:
    for n in nums:
        freq[n] += 1

sorted_nums = sorted(range(1, 26), key=lambda n: (-freq[n], n))

print(f"Últimos 3 concursos: {[row[0] for row in rows]}")
print(f"Frequências: {{{', '.join(f'{n}:{freq[n]}' for n in range(1, 26))}}}")

# Busca a melhor classificação H/M/F que produza entre 5.000 e 50.000 combos totais
# (totalmente enumerável, não trivial)
best_config = None
best_count = 0

for h_size in range(5, 13):
    for f_size in range(5, 13):
        m_size = 25 - h_size - f_size
        if m_size < 4 or m_size > 16:
            continue

        h_set = set(sorted_nums[:h_size])
        f_set = set(sorted_nums[-f_size:])
        m_set = set(range(1, 26)) - h_set - f_set

        if len(m_set) != m_size:
            continue

        total = 0
        for hk in [5, 6]:
            for mk in [4, 5]:
                ck = 15 - hk - mk
                if ck < 4 or ck > 5:
                    continue
                if hk > h_size or mk > m_size or ck > f_size:
                    continue
                total += comb(h_size, hk) * comb(m_size, mk) * comb(f_size, ck)

        # Prefere classificação com 5.000-50.000 combos (totalmente enumerável)
        # e com H e F balanceados (nem muito pequenos)
        if 5000 <= total <= 50000 and h_size >= 5 and f_size >= 5:
            if best_config is None or \
               (abs(total - 12012) < abs(best_config[6] - 12012)):
                best_config = (h_size, m_size, f_size, h_set, m_set, f_set, total)

if best_config is None:
    print("Nenhuma classificação adequada encontrada.")
    sys.exit(1)

h_size, m_size, f_size, h_set, m_set, f_set, total = best_config
quentes = sorted(h_set)
mornos = sorted(m_set)
frios = sorted(f_set)

print(f"\nClassificação: H={h_size} M={m_size} F={f_size}")
print(f"QUENTES: {quentes}")
print(f"MORNOS:  {mornos}")
print(f"FRIOS:   {frios}")
print(f"Total de combinações válidas: {total:,}")

# Geração exaustiva
print(f"\nGerando todas as {total:,} combinações...")
encontradas = []

for hk in [5, 6]:
    for mk in [4, 5]:
        ck = 15 - hk - mk
        if ck < 4 or ck > 5:
            continue
        if hk > h_size or mk > m_size or ck > f_size:
            continue

        for h_part in combinations(quentes, hk):
            for m_part in combinations(mornos, mk):
                for f_part in combinations(frios, ck):
                    combo = tuple(sorted(h_part + m_part + f_part))
                    encontradas.append(combo)

# Dados de contagem
qtd_q = [sum(1 for n in c if n in quentes) for c in encontradas]
qtd_m = [sum(1 for n in c if n in mornos) for c in encontradas]
qtd_f = [sum(1 for n in c if n in frios) for c in encontradas]

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'combinacoes_quentes_mornos_frios_3jan_{timestamp}.txt'
filepath = rf'C:\Users\AR CALHAU\source\repos\LotoScope\{filename}'

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(f"TODAS AS COMBINAÇÕES DE 15 NÚMEROS - CLASSIFICAÇÃO TÉRMICA (janela 3 concursos)\n")
    f.write(f"Regras: 5-6 Quentes, 4-5 Mornos, 4-5 Frios\n")
    f.write(f"Últimos concursos: {[row[0] for row in rows]}\n")
    f.write(f"QUENTES ({len(quentes)}): {quentes}\n")
    f.write(f"MORNOS  ({len(mornos)}): {mornos}\n")
    f.write(f"FRIOS   ({len(frios)}): {frios}\n")
    f.write(f"Total: {len(encontradas):,} combinações\n")
    f.write(f"Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    f.write("=" * 60 + "\n\n")
    for i, combo in enumerate(encontradas, 1):
        q = sum(1 for n in combo if n in quentes)
        m = sum(1 for n in combo if n in mornos)
        c = sum(1 for n in combo if n in frios)
        f.write(f"{i:6d}. {str(list(combo)):55s}  Q:{q} M:{m} F:{c}\n")

print(f"\nArquivo salvo: {filename}")
print(f"Caminho: {filepath}")
