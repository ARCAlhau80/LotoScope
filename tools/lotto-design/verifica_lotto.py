"""Verificador independente (força bruta pura, sem numpy):
para TODO 10-subconjunto D de 20, existe bloco B com |B∩D| >= t ?"""
import sys, itertools, json
t = int(sys.argv[1]); blocos = json.loads(sys.argv[2])
masks = [sum(1 << (x - 1) for x in b) for b in blocos]
pior = 99; falhas = 0
for D in itertools.combinations(range(20), 10):
    d = sum(1 << i for i in D)
    m = max(bin(b & d).count("1") for b in masks)
    pior = min(pior, m)
    if m < t: falhas += 1
print(f"t={t} blocos={len(blocos)} subconjuntos=184756 falhas={falhas} pior_caso={pior}")
