"""Gerador eficiente de lotto design L(v,k,m,t) para universos grandes (v>=23).

O guloso incremental usa CSR numpy:
  - cobertura[j] = indices dos alvos cobertos pelo candidato j
  - indice reverso alvo -> candidatos (rev_idx)
  - ganhos[j] = quantos alvos ainda descobertos o candidato j cobre

Custo total O(arestas), viavel para N ~ 1.1M alvos.
"""
import sys, json, time, math
import numpy as np

POP16 = np.array([bin(i).count('1') for i in range(1 << 16)], dtype=np.int8)


def pc(a):
    a = a.astype(np.int64, copy=False)
    return POP16[a & 0xffff].astype(np.int32) + POP16[(a >> 16) & 0xffff].astype(np.int32)


def mascaras(v, m):
    total = math.comb(v, m)
    out = np.empty(total, dtype=np.int64)
    p = 0
    atual = []

    def rec(inicio, resto):
        nonlocal p
        if resto == 0:
            mask = 0
            for e in atual:
                mask |= 1 << e
            out[p] = mask
            p += 1
            return
        for i in range(inicio, v - resto + 1):
            atual.append(i)
            rec(i + 1, resto - 1)
            atual.pop()

    rec(0, m)
    return out


def verificar(masks, alvos, t, chunk=100_000):
    pior, falhas = 99, 0
    for ini in range(0, len(alvos), chunk):
        a = alvos[ini:ini + chunk]
        inter = pc(a[:, None] & masks[None, :])
        melhor = inter.max(axis=1)
        pior = min(pior, int(melhor.min()))
        falhas += int((melhor < t).sum())
    return pior, falhas


def gerar(v, k, m, t, pool=250, seed=1):
    t0 = time.time()
    rng = np.random.default_rng(seed)
    alvos = mascaras(v, m)
    N = len(alvos)
    print(f'L({v},{k},{m},{t}) alvos={N:,} em {time.time()-t0:.1f}s', flush=True)

    vistos = set()
    cands = []
    while len(cands) < pool:
        c = tuple(sorted(rng.choice(v, size=k, replace=False).tolist()))
        if c in vistos:
            continue
        vistos.add(c)
        cands.append(sum(1 << e for e in c))
    cands = np.array(cands, dtype=np.int64)

    tc = time.time()
    cob = []
    for cand in cands:
        cob.append(np.flatnonzero(pc(alvos & cand) >= t).astype(np.int32))
    print(f'candidatos={pool} cobertura/bloco={len(cob[0]):,} em {time.time()-tc:.1f}s', flush=True)

    tr = time.time()
    indptr = np.concatenate([[0], np.cumsum([len(x) for x in cob])]).astype(np.int64)
    indices = np.concatenate(cob).astype(np.int32)
    cand_de_aresta = np.repeat(np.arange(pool), np.diff(indptr)).astype(np.int32)
    ordem = np.argsort(indices, kind='stable')
    rev_idx = cand_de_aresta[ordem]
    rev_alvo = indices[ordem]
    rev_ptr = np.concatenate([[0], np.cumsum(np.bincount(indices, minlength=N))]).astype(np.int64)
    print(f'indice reverso em {time.time()-tr:.1f}s (arestas={len(indices):,})', flush=True)

    coberto = np.zeros(N, dtype=bool)
    ganhos = np.diff(indptr).astype(np.int32)
    escolhidos = []
    while True:
        j = int(np.argmax(ganhos))
        if ganhos[j] <= 0:
            break
        escolhidos.append(j)
        idxs = indices[indptr[j]:indptr[j + 1]]
        novos = idxs[~coberto[idxs]]
        coberto[novos] = True
        for i in novos:
            ini, fim = rev_ptr[i], rev_ptr[i + 1]
            ganhos[rev_idx[ini:fim]] -= 1
        ganhos[j] = 0
        if len(escolhidos) % 10 == 0:
            print(f'  {len(escolhidos)} blocos, cobertos {int(coberto.sum()):,}/{N:,}', flush=True)

    print(f'guloso={len(escolhidos)} blocos em {time.time()-t0:.1f}s', flush=True)

    masks = np.array([cands[j] for j in escolhidos], dtype=np.int64)
    pior, falhas = verificar(masks, alvos, t)
    print(f'verificacao: pior={pior} falhas={falhas}', flush=True)

    rodada = 0
    while falhas > 0 and rodada < 20:
        rodada += 1
        faltantes = []
        for ini in range(0, N, 100_000):
            a = alvos[ini:ini + 100_000]
            inter = pc(a[:, None] & masks[None, :])
            f = np.flatnonzero(inter.max(axis=1) < t)
            faltantes.extend((ini + f).tolist())
        print(f'  reparo {rodada}: {len(faltantes)} alvos descobertos', flush=True)
        for fi in faltantes[:2000]:
            masks = np.concatenate([masks, np.array([alvos[fi]], dtype=np.int64)])
        # dedup
        _, uniq = np.unique(masks, return_index=True)
        masks = masks[np.sort(uniq)]
        pior, falhas = verificar(masks, alvos, t)
        print(f'  apos reparo: blocos={len(masks)} pior={pior} falhas={falhas}', flush=True)

    blocos = [[e + 1 for e in range(v) if int(mask) >> e & 1] for mask in masks]
    blocos = sorted(sorted(b) for b in blocos)
    print(f'RESULTADO blocos={len(blocos)} pior={pior} falhas={falhas} tempo={time.time()-t0:.0f}s', flush=True)
    return blocos, pior, falhas


if __name__ == '__main__':
    v, k, m, t = (int(x) for x in sys.argv[1:5])
    pool = int(sys.argv[5]) if len(sys.argv) > 5 else 250
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    destino = sys.argv[7] if len(sys.argv) > 7 else None
    blocos, pior, falhas = gerar(v, k, m, t, pool, seed)
    if destino and falhas == 0:
        with open(destino, 'w', encoding='utf-8') as f:
            json.dump(blocos, f)
        print('salvo em', destino, flush=True)
    sys.exit(0 if falhas == 0 else 3)
