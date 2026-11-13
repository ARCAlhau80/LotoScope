"""
Gerador de lotto design L(v,k,m,t) para casos grandes.

Diferente de um covering C(v,k,t), o lotto design so exige que todo m-subconjunto
do universo tenha interseccao >= t com algum bloco. Para t proximo de m isso
reduz muito o numero de blocos, mas o guloso classico (varrer todos os alvos a
cada passo) fica caro.

Aqui o guloso usa ganhos incrementais:
  - cada bloco candidato guarda a lista de alvos que cobre;
  - um indice reverso alvo -> candidatos permite decrementar o ganho apenas dos
    candidatos afetados quando um alvo passa a estar coberto;
  - o custo total vira O(pool * alvos_por_bloco), independente do numero de passos.

Uso:
  python lotto_gen_fast.py v k m t [pool] [restarts] [seed] [--json-arquivo]

A saida inclui a verificacao exaustiva (todos os C(v,m) sorteios).
"""
import sys, json, time, itertools, math
import numpy as np


def mascaras_subconjuntos(v, m):
    """Mascaras de todos os m-subconjuntos de range(v), em ordem lexicografica."""
    total = math.comb(v, m)
    out = np.empty(total, dtype=np.int64)
    atual = []
    p = 0

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


def alvos_cobertos(bmask, v, m, t):
    """Mascaras dos m-subconjuntos D com |B n D| >= t."""
    dentro = [i for i in range(v) if bmask >> i & 1]
    fora = [i for i in range(v) if not (bmask >> i & 1)]
    out = []
    for i in range(t, min(len(dentro), m) + 1):
        j = m - i
        if j > len(fora):
            continue
        for a in itertools.combinations(dentro, i):
            ma = 0
            for e in a:
                ma |= 1 << e
            for b in itertools.combinations(fora, j):
                mb = 0
                for e in b:
                    mb |= 1 << e
                out.append(ma | mb)
    return out


POP16 = np.array([bin(i).count('1') for i in range(1 << 16)], dtype=np.int8)


def popcount(arr):
    a = arr.astype(np.int64, copy=False)
    return POP16[a & 0xffff].astype(np.int32) + POP16[(a >> 16) & 0xffff].astype(np.int32)


def verifica(blocos, v, m, t, chunk=2048):
    """Percorre todos os C(v,m) sorteios e devolve (pior, falhas, total).

    `blocos` usa dezenas 1..v; os alvos usam posicoes 0..v-1.
    """
    alvos = mascaras_subconjuntos(v, m)
    masks = np.array([sum(1 << (e - 1) for e in b) for b in blocos], dtype=np.int64)
    pior, falhas = 99, 0
    for ini in range(0, len(alvos), chunk):
        bloco_alvos = alvos[ini:ini + chunk]
        inter = popcount(bloco_alvos[:, None] & masks[None, :])
        melhor = inter.max(axis=1)
        pior = min(pior, int(melhor.min()))
        falhas += int((melhor < t).sum())
    return pior, falhas, len(alvos)


def limite_inferior(v, k, m, t):
    por = sum(math.comb(k, i) * math.comb(v - k, m - i) for i in range(t, min(k, m) + 1))
    return math.ceil(math.comb(v, m) / por) if por else 0


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    v, k, m, t = (int(sys.argv[i]) for i in range(1, 5))
    pool = int(sys.argv[5]) if len(sys.argv) > 5 else 2000
    restarts = int(sys.argv[6]) if len(sys.argv) > 6 else 3
    seed = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    destino = sys.argv[8] if len(sys.argv) > 8 else None

    t0 = time.time()
    rng = np.random.default_rng(seed)

    alvos = mascaras_subconjuntos(v, m)
    N = len(alvos)
    indice = np.full(1 << v, -1, dtype=np.int32)
    indice[alvos] = np.arange(N, dtype=np.int32)
    print(f'L({v},{k},{m},{t}) alvos={N} LB={limite_inferior(v,k,m,t)} indice em {time.time()-t0:.1f}s', flush=True)

    vistos = set()
    cands = []
    tentativas = 0
    while len(cands) < pool and tentativas < pool * 20:
        tentativas += 1
        c = tuple(sorted(rng.choice(v, size=k, replace=False).tolist()))
        mask = 0
        for e in c:
            mask |= 1 << e
        if mask in vistos:
            continue
        vistos.add(mask)
        cands.append(mask)

    tc = time.time()
    cobertura = []
    for bm in cands:
        ms = alvos_cobertos(bm, v, m, t)
        cobertura.append(indice[np.array(ms, dtype=np.int64)])
    print(f'candidatos={len(cands)} cobertura/bloco={len(cobertura[0])} em {time.time()-tc:.1f}s', flush=True)

    # indice reverso alvo -> candidatos que o cobrem
    tr = time.time()
    rev = [[] for _ in range(N)]
    for j, idx in enumerate(cobertura):
        for i in idx:
            rev[int(i)].append(j)
    print(f'indice reverso em {time.time()-tr:.1f}s', flush=True)

    melhor = None
    for r in range(restarts):
        descoberto = np.ones(N, dtype=bool)
        ganhos = np.array([len(x) for x in cobertura], dtype=np.int32)
        escolhidos = []
        restantes = N
        while restantes > 0:
            mx = int(ganhos.max())
            if mx <= 0:
                break
            iguais = np.flatnonzero(ganhos == mx)
            j = int(iguais[rng.integers(len(iguais))]) if len(iguais) > 1 else int(iguais[0])
            escolhidos.append(j)
            for i in cobertura[j]:
                i = int(i)
                if not descoberto[i]:
                    continue
                descoberto[i] = False
                restantes -= 1
                for jj in rev[i]:
                    ganhos[jj] -= 1
        if restantes == 0:
            if melhor is None or len(escolhidos) < len(melhor):
                melhor = escolhidos
                print(f'  restart {r}: {len(escolhidos)} blocos (melhor ate agora)', flush=True)
            else:
                print(f'  restart {r}: fechou com {len(escolhidos)} blocos (pior que o melhor)', flush=True)
        else:
            print(f'  restart {r}: parou com {restantes} alvos descobertos', flush=True)

    if melhor is None:
        print('NAO FECHOU')
        sys.exit(2)

    # poda: remove bloco cuja cobertura esta toda com contagem >= 2
    cont = np.zeros(N, dtype=np.int32)
    for j in melhor:
        cont[cobertura[j]] += 1
    manter = []
    for j in melhor:
        idx = cobertura[j]
        if (cont[idx] > 1).all():
            cont[idx] -= 1
        else:
            manter.append(j)
    print(f'greedy={len(melhor)} apos poda={len(manter)}', flush=True)

    blocos = [[i + 1 for i in range(v) if bm >> i & 1] for bm in (cands[j] for j in manter)]
    blocos = [sorted(b) for b in blocos]

    pior, falhas, total = verifica(blocos, v, m, t)
    print(f'VERIFICACAO v={v} k={k} m={m} t={t} blocos={len(blocos)} alvos={total} falhas={falhas} pior={pior}')
    if falhas:
        print('DESIGN INVALIDO')
        sys.exit(3)

    if destino:
        with open(destino, 'w', encoding='utf-8') as f:
            json.dump(blocos, f)
        print('blocos salvos em', destino)
    else:
        print(json.dumps(blocos))


if __name__ == '__main__':
    main()
