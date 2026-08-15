from itertools import combinations
from datetime import datetime

fixos = [2, 3, 4, 8, 10, 11, 12, 14, 15, 18, 19]
restantes = [n for n in range(1, 26) if n not in fixos]

print(f"Fixos ({len(fixos)}): {fixos}")
print(f"Restantes ({len(restantes)}): {restantes}")
print(f"Total: C({len(restantes)},4) = {len(list(combinations(restantes, 4)))}\n")

combinacoes = []
for comb in combinations(restantes, 4):
    combinacoes.append(tuple(sorted(fixos + list(comb))))

combinacoes.sort()

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'combinacoes_fixas_{timestamp}.txt'

with open(filename, 'w', encoding='utf-8') as f:
    f.write(f"TODAS AS COMBINAÇÕES DE 15 NÚMEROS COM FIXOS\n")
    f.write(f"Fixos: {fixos}\n")
    f.write(f"Restantes: {restantes}\n")
    f.write(f"Total: {len(combinacoes)} combinações\n")
    f.write(f"Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    f.write("=" * 60 + "\n\n")
    for i, combo in enumerate(combinacoes, 1):
        fixos_presentes = sum(1 for n in combo if n in fixos)
        f.write(f"{i:4d}. {str(list(combo))}\n")

print(f"{len(combinacoes)} combinacoes geradas -> {filename}")
