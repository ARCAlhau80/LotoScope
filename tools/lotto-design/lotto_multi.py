"""
Lotto design L(20,10,10,t) com greedy randomizado multi-restart.

Reaproveita UMA matriz de cobertura e faz N passes gulosos com
desempate aleatorio entre os melhores candidatos, + poda de redundantes.
Reporta o melhor conjunto encontrado.
"""
import sys, time, itertools, json
import numpy as np

V, K, M = 20, 10, 10
t_alvo = int(sys.argv[1]) if len(sys.argv) > 1 else 6
n_cand = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
n_restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 20
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
top_k = int(sys.argv[5]) if len(sys.argv) > 5 else 3

rng = np.random.default_rng(seed)

todos = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(V), K)], dtype=np.uint32)
N = len(todos)

POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def popcount32(x):
    x = x.view(np.uint8).reshape(-1, 4)
    return POP[x].sum(axis=1).astype(np.int8)


idx = rng.choice(N, size=n_cand // 2, replace=False)
cands = todos[idx]
comp = (~cands) & np.uint32((1 << V) - 1)
cands = np.unique(np.concatenate([cands, comp]))

t0 = time.time()
Mcov = np.zeros((len(cands), N), dtype=bool)
for i, b in enumerate(cands):
    Mcov[i] = popcount32(todos & b) >= t_alvo
print(f"t={t_alvo} candidatos={len(cands)} alvos={N} matriz={time.time()-t0:.1f}s", flush=True)


def podar(sel):
    sel = list(sel)
    mudou = True
    while mudou:
        mudou = False
        for j in list(sel):
            resto = [x for x in sel if x != j]
            if resto and Mcov[resto].any(axis=0).all():
                sel = resto
                mudou = True
    return sel


melhor = None
for r in range(n_restarts):
    descoberto = np.ones(N, dtype=bool)
    sel = []
    while descoberto.any():
        ganhos = Mcov[:, descoberto].sum(axis=1)
        ordem = np.argsort(ganhos)[::-1]
        ordem = ordem[: max(1, top_k)]
        ordem = ordem[ganhos[ordem] > 0]
        if len(ordem) == 0:
            break
        j = int(rng.choice(ordem))
        sel.append(j)
        descoberto &= ~Mcov[j]
    sel = podar(sel)
    completo = Mcov[sel].any(axis=0).all() if sel else False
    if completo and (melhor is None or len(sel) < len(melhor)):
        melhor = sel
        print(f"  restart {r}: {len(sel)} blocos (melhor)", flush=True)

def bits(b):
    return [i + 1 for i in range(V) if b >> i & 1]


print(f"\nRESULTADO L(20,10,10,{t_alvo}): {len(melhor)} blocos ({n_restarts} restarts, top_k={top_k})")
print(json.dumps([bits(int(cands[j])) for j in melhor]))
