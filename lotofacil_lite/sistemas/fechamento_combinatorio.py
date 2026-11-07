#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎰 FECHAMENTO COMBINATÓRIO (WHEEL / COVERING DESIGN) - LOTOFÁCIL
----------------------------------------------------------------
Implementa fechamentos combinatórios (C(v, k, t)) para redução de custo:

- C(v, k, t): escolhe apostas de k dezenas sobre um universo de v dezenas
  de modo que TODA combinação de t dezenas do universo esteja contida em
  pelo menos uma aposta. Garante t acertos se as t dezenas sorteadas
  estiverem entre as v escolhidas.

- Redutor guloso (set cover): elimina apostas redundantes e reporta o
  custo real em vez de estimativas heurísticas.

Autor: LotoScope
"""

from __future__ import annotations

import functools
import random
from itertools import combinations
from math import ceil, comb
from typing import Dict, Iterable, List, Optional, Set, Tuple

PRECO_APOSTA_15 = 3.50
# Alias de compatibilidade para chamadas antigas.
PRECO_POR_JOGO = PRECO_APOSTA_15

# Escala: teto de candidatos distintos no pool e de avaliacoes na busca local.
LIMITE_POOL_CANDIDATOS = 5000
# Teto de candidatos quando max_apostas = 0 (sem limite de apostas).
LIMITE_POOL_CANDIDATOS_ILIMITADO = 20000
ORCAMENTO_BUSCA_LOCAL = 250_000


@functools.lru_cache(maxsize=None)
def n_combinacoes(n: int, k: int) -> int:
    """C(n, k) = n! / (k! * (n-k)!), com otimização C(n, k) = C(n, n-k)."""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    resultado = 1
    for i in range(k):
        resultado = resultado * (n - i) // (i + 1)
    return resultado


def limite_inferior_cobertura(v: int, k: int, t: int) -> int:
    """Limite inferior de Schönheim para C(v, k, t).

    Não é necessariamente alcançável, mas mostra a folga do heurístico.
    """
    if t <= 0 or k <= 0 or v <= 0 or k > v:
        return 0
    if t == 1:
        return ceil(v / k)
    return ceil((v / k) * limite_inferior_cobertura(v - 1, k - 1, t - 1))


def custo_por_aposta(k: int) -> float:
    """Custo de UMA aposta de k dezenas.

    Uma aposta de k dezenas equivale a C(k, 15) apostas simples:
    k=15 -> 3,50 | 16 -> 56,00 | 17 -> 476,00 | 18 -> 2.856,00
    k=19 -> 13.566,00 | 20 -> 54.264,00

    Para k < 15 (fechamento exploratorio, nao jogavel) usa-se o preco de
    uma aposta simples como piso.
    """
    if k < 15:
        return PRECO_APOSTA_15
    return round(n_combinacoes(k, 15) * PRECO_APOSTA_15, 2)


def _mask(nums: Iterable[int], universo: List[int]) -> int:
    """Converte uma lista de números numa máscara de bits sobre o universo."""
    pos = {n: i for i, n in enumerate(universo)}
    m = 0
    for n in nums:
        m |= 1 << pos[n]
    return m


def _subsets(universo: List[int], r: int) -> List[Tuple[int, ...]]:
    """Todas as combinações de r elementos do universo."""
    return list(combinations(universo, r))


def gerar_apostas_candidatas(universo: List[int], k: int, limite: Optional[int] = None) -> List[Tuple[int, ...]]:
    """Lista apostas candidatas de k dezenas.

    Quando ``limite`` e' menor que o universo completo, amostra deterministamente
    em vez de materializar todas as C(v, k) combinacoes (impraticavel para v=25).
    """
    universo = sorted(set(int(x) for x in universo))
    v = len(universo)
    total = n_combinacoes(v, k)
    if limite is None or limite >= total:
        return list(combinations(universo, k))

    rng = random.Random(hash((tuple(universo), k)) & 0xFFFFFFFF)
    visto: Set[Tuple[int, ...]] = set()
    out: List[Tuple[int, ...]] = []
    while len(out) < limite:
        cand = tuple(sorted(rng.sample(universo, k)))
        if cand not in visto:
            visto.add(cand)
            out.append(cand)
    return out


def cobrir_fechamento(
    universo: List[int],
    k: int,
    t: int,
    max_apostas: Optional[int] = None,
    candidato_limite: Optional[int] = None,
) -> List[List[int]]:
    """
    Constrói um fechamento C(v, k, t) por set cover guloso.

    Seleciona, a cada passo, a aposta que cobre o maior número de
    t-subconjuntos ainda não cobertos, até cobrir todos (ou atingir max_apostas).

    Params
    ------
    universo : lista de dezenas base (v)
    k        : tamanho de cada aposta
    t        : garantia de acertos (t dezenas sorteadas dentro do universo)
    max_apostas : teto de apostas geradas (None = sem limite)
    candidato_limite : teto de apostas candidatas avaliadas (performance)
    """
    v = len(universo)
    if k < t or t < 1 or k > v:
        raise ValueError("Deve valer 1 <= t <= k <= v")

    t_subsets = _subsets(universo, t)
    total_t = len(t_subsets)
    if total_t == 0:
        return []

    # Máscaras dos t-subconjuntos alvo
    alvos = [_mask(s, universo) for s in t_subsets]
    coberto = [False] * total_t

    apostas: List[Tuple[int, ...]] = []
    candidatos = gerar_apostas_candidatas(universo, k, candidato_limite)

    while True:
        if all(coberto):
            break
        if max_apostas is not None and len(apostas) >= max_apostas:
            break

        melhor_aposta = None
        melhor_ganho = -1
        melhor_mask = 0

        for aposta in candidatos:
            if aposta in apostas:
                continue
            mask = _mask(aposta, universo)
            ganho = 0
            for i, alvo in enumerate(alvos):
                if not coberto[i] and (mask & alvo) == alvo:
                    ganho += 1
            if ganho > melhor_ganho:
                melhor_ganho = ganho
                melhor_aposta = aposta
                melhor_mask = mask

        if melhor_aposta is None or melhor_ganho == 0:
            # Nenhuma aposta restante cobre novos alvos (candidatos limitados).
            break

        apostas.append(melhor_aposta)
        for i, alvo in enumerate(alvos):
            if not coberto[i] and (melhor_mask & alvo) == alvo:
                coberto[i] = True

    return [list(a) for a in apostas]


def verificar_cobertura(
    apostas: List[List[int]],
    universo: List[int],
    k: int,
    t: int,
) -> Dict[str, object]:
    """
    Verifica EXATAMENTE se o fechamento cobre todos os t-subconjuntos.

    Retorna dicionário com: coberta (bool), t_subsets_total,
    t_subsets_cobertos, garantia_percentual, apostas_validas,
    apostas_invalidas, custo_estimado.
    """
    if k < t:
        raise ValueError("Deve valer t <= k")

    pos = {n: i for i, n in enumerate(universo)}
    t_subsets = _subsets(universo, t)
    total_t = len(t_subsets)
    alvos = [_mask(s, universo) for s in t_subsets]
    coberto = [False] * total_t

    apostas_validas = 0
    apostas_invalidas = 0
    masks_apostas: List[int] = []

    for aposta in apostas:
        if len(aposta) != k or any(n not in pos for n in aposta):
            apostas_invalidas += 1
            continue
        if len(set(aposta)) != k:
            apostas_invalidas += 1
            continue
        apostas_validas += 1
        masks_apostas.append(_mask(aposta, universo))

    for mask in masks_apostas:
        for i, alvo in enumerate(alvos):
            if not coberto[i] and (mask & alvo) == alvo:
                coberto[i] = True

    cobertos = sum(coberto)
    garantia = (cobertos / total_t * 100) if total_t else 100.0

    return {
        "coberta": cobertos == total_t,
        "t_subsets_total": total_t,
        "t_subsets_cobertos": cobertos,
        "garantia_percentual": round(garantia, 4),
        "apostas_validas": apostas_validas,
        "apostas_invalidas": apostas_invalidas,
        "total_apostas": len(apostas),
        "preco_por_aposta": custo_por_aposta(k),
        "custo_estimado": round(apostas_validas * custo_por_aposta(k), 2),
    }


def relatorio_custo(
    apostas: List[List[int]],
    k: Optional[int] = None,
    preco_por_jogo: Optional[float] = None,
) -> Dict[str, object]:
    """Custo real do fechamento, considerando o tamanho real de cada aposta (k)."""
    total = len(apostas)
    k_efetivo = k if k is not None else (len(apostas[0]) if apostas else 15)
    preco = preco_por_jogo if preco_por_jogo is not None else custo_por_aposta(k_efetivo)
    return {
        "total_apostas": total,
        "k": k_efetivo,
        "preco_por_jogo": preco,
        "custo_total": round(total * preco, 2),
        "reducao_vs_universo_25_15": round((1 - total / n_combinacoes(25, 15)) * 100, 4),
    }


def comb_rank_lex(comb: Iterable[int], n: int) -> int:
    """Rank lexicografico contiguo (0 .. C(n,k)-1) de uma combinacao ordenada de 1..n.

    Usa a formula C(n,k)-1 - sum_i C(n - c_i, k - i), em O(k) consultas a C(n,k).
    """
    comb = sorted(int(x) for x in comb)
    k = len(comb)
    total = n_combinacoes(n, k)
    s = 0
    for i, c in enumerate(comb):
        s += n_combinacoes(n - c, k - i)
    return total - 1 - s


def indices_alvos_cobertos_por_aposta(aposta: Iterable[int], universo: List[int], t: int) -> List[int]:
    """Índices (rank lex) de todos os t-subconjuntos cobertos por uma aposta de k dezenas.

    O rank lexicográfico opera sobre posições 1..v no universo, não sobre os
    rótulos das dezenas (que podem ser 3..25, por exemplo).
    """
    u = sorted(set(int(x) for x in universo))
    v = len(u)
    pos = {n: i + 1 for i, n in enumerate(u)}
    a = sorted(pos[n] for n in aposta if n in pos)
    return [comb_rank_lex(sub, v) for sub in combinations(a, t)]


def remover_apostas_redundantes(
    apostas: List[List[int]],
    universo: Iterable[int],
    k: int,
    t: int,
) -> List[List[int]]:
    """Remove apostas que não cobrem nenhum t-subconjunto exclusivo.

    A cobertura é preservada exatamente; o resultado é um subconjunto mínimo
    local do fechamento original, não necessariamente o ótimo global.
    """
    if len(apostas) <= 1:
        return [list(a) for a in apostas]
    u = sorted(set(int(x) for x in universo))
    total_t = n_combinacoes(len(u), t)
    if total_t <= 0:
        return [list(a) for a in apostas]

    indices = [indices_alvos_cobertos_por_aposta(a, u, t) for a in apostas]
    contagem = [0] * total_t
    for idxs in indices:
        for i in idxs:
            contagem[i] += 1

    ativas = [True] * len(apostas)
    alterou = True
    while alterou:
        alterou = False
        for bi, idxs in enumerate(indices):
            if not ativas[bi]:
                continue
            tem_exclusivo = any(contagem[i] == 1 for i in idxs)
            if not tem_exclusivo:
                for i in idxs:
                    contagem[i] -= 1
                ativas[bi] = False
                alterou = True

    return [list(a) for a, ativa in zip(apostas, ativas) if ativa]


def aposta_satisfaz_repetidas(
    aposta: Iterable[int],
    numeros_base: Iterable[int],
    minimo: int,
    maximo: int,
) -> bool:
    """Verifica se a aposta repete entre ``minimo`` e ``maximo`` dezenas da base."""
    base = set(int(x) for x in numeros_base)
    if not base:
        return True
    qtd = sum(1 for n in aposta if n in base)
    return minimo <= qtd <= maximo


def construir_fechamento_guloso_amostrado(
    universo: Iterable[int],
    k: int,
    t: int,
    max_apostas: Optional[int] = 2000,
    seed: int = 42,
    candidatos_pool: int = 3000,
    amostra_por_passo: int = 200,
) -> List[List[int]]:
    """
    Constrói um fechamento aproximado C(v, k, t) por set cover guloso amostrado.

    Para v=25 (Lotofácil) não é viável avaliar todas as C(25,15) apostas candidatas;
    usa-se um pool determinístico de candidatas e, a cada passo, escolhe a de uma
    amostra aleatória que cobre mais t-subconjuntos ainda não cobertos.

    ``max_apostas=0`` (ou negativo) significa "sem limite": o guloso roda até
    cobrir todos os t-subconjuntos ou esgotar o pool de candidatas.

    Retorna a lista de apostas (cada uma com k dezenas).
    """
    universo = sorted(set(int(x) for x in universo))
    v = len(universo)
    if k < t or t < 1 or k > v:
        raise ValueError("Deve valer 1 <= t <= k <= v")

    total_t = n_combinacoes(v, t)
    coberta = bytearray(total_t)
    cobertos = 0

    rng = random.Random(seed)
    sem_limite = max_apostas is None or max_apostas <= 0
    # O pool precisa ter ao menos max_apostas candidatos distintos; caso
    # contrario o guloso esgota os candidatos e devolve menos que o pedido.
    # Sem limite, usa um teto maior para nao parar artificialmente em 5000.
    teto_pool = LIMITE_POOL_CANDIDATOS_ILIMITADO if sem_limite else LIMITE_POOL_CANDIDATOS
    limite_pool = max(candidatos_pool, teto_pool if sem_limite else min(max_apostas, teto_pool))
    pool = gerar_apostas_candidatas(universo, k, limite=limite_pool)
    rng.shuffle(pool)

    indices_cache: List[Optional[List[int]]] = [None] * len(pool)

    def indices_de(ci: int) -> List[int]:
        idx = indices_cache[ci]
        if idx is None:
            idx = indices_alvos_cobertos_por_aposta(pool[ci], universo, t)
            indices_cache[ci] = idx
        return idx

    apostas: List[Tuple[int, ...]] = []
    restantes = list(range(len(pool)))

    while cobertos < total_t and restantes and (sem_limite or len(apostas) < max_apostas):
        amostra = rng.sample(restantes, min(amostra_por_passo, len(restantes)))
        melhor_idx = None
        melhor_ganho = -1
        for ci in amostra:
            ganho = sum(1 for idx in indices_de(ci) if not coberta[idx])
            if ganho > melhor_ganho:
                melhor_ganho = ganho
                melhor_idx = ci
        if melhor_idx is None or melhor_ganho <= 0:
            if len(restantes) > amostra_por_passo:
                continue
            break
        ci = melhor_idx
        apostas.append(pool[ci])
        for idx in indices_de(ci):
            if not coberta[idx]:
                coberta[idx] = 1
                cobertos += 1
        restantes.remove(ci)

    return [list(a) for a in apostas]


def _calcular_coberta(
    universo: List[int],
    k: int,
    t: int,
    apostas: List[Iterable[int]],
) -> Tuple[bytearray, int]:
    """Retorna (mascara de t-subconjuntos cobertos, quantidade coberta)."""
    v = len(universo)
    total_t = n_combinacoes(v, t)
    coberta = bytearray(total_t)
    cobertos = 0
    for aposta in apostas:
        for idx in indices_alvos_cobertos_por_aposta(aposta, universo, t):
            if not coberta[idx]:
                coberta[idx] = 1
                cobertos += 1
    return coberta, cobertos


def busca_local_fechamento(
    apostas: List[List[int]],
    universo: List[int],
    k: int,
    t: int,
    max_iteracoes: int = 200,
    seed: int = 1,
    candidatos_pool: int = 600,
    orcamento_avaliacoes: int = ORCAMENTO_BUSCA_LOCAL,
) -> List[List[int]]:
    """
    Hill climbing sobre o fechamento: tenta substituir cada aposta por um
    candidato que aumente a cobertura total de t-subconjuntos, sem alterar o
    numero de apostas (reducao de custo mantendo/elevando a garantia).

    ``orcamento_avaliacoes`` limita os pares (aposta, candidato) avaliados para
    que volumes grandes nao degenerem em minutos/horas de execucao.
    """
    universo = sorted(set(int(x) for x in universo))
    v = len(universo)
    rng = random.Random(seed)

    apostas_tuplas = [tuple(a) for a in apostas]

    if orcamento_avaliacoes <= 0:
        return [list(a) for a in apostas_tuplas]

    pool = gerar_apostas_candidatas(universo, k, limite=candidatos_pool)
    rng.shuffle(pool)
    # A cada iteracao avaliamos no maximo `apostas_por_iteracao` apostas contra
    # o pool. Sem esse teto, n apostas x pool degenera em minutos/horas.
    apostas_por_iteracao = max(
        1,
        min(
            len(apostas_tuplas),
            orcamento_avaliacoes // (max(1, max_iteracoes) * max(1, len(pool))),
        ),
    )

    indices_por_aposta = [indices_alvos_cobertos_por_aposta(a, universo, t) for a in apostas_tuplas]

    total_t = n_combinacoes(v, t)
    contagem = [0] * total_t
    coberta = bytearray(total_t)
    cobertos = 0
    for indices in indices_por_aposta:
        for idx in indices:
            if contagem[idx] == 0:
                coberta[idx] = 1
                cobertos += 1
            contagem[idx] += 1

    indices_pool = [indices_alvos_cobertos_por_aposta(a, universo, t) for a in pool]

    for _ in range(max_iteracoes):
        if cobertos >= total_t:
            break
        # Embaralha pares (aposta, indices) juntos para nao dessincronizar.
        pares = list(zip(apostas_tuplas, indices_por_aposta))
        rng.shuffle(pares)
        progresso = False
        for i in range(min(apostas_por_iteracao, len(pares))):
            aposta_atual, indices_atual = pares[i]
            for ci in range(len(pool)):
                if pool[ci] == aposta_atual:
                    continue
                indices_cand = indices_pool[ci]
                novo_coberto = sum(1 for idx in indices_cand if contagem[idx] == 0)
                perdido = sum(1 for idx in indices_atual if contagem[idx] == 1)
                liquido = novo_coberto - perdido
                if liquido > 0:
                    for idx in indices_atual:
                        contagem[idx] -= 1
                        if contagem[idx] == 0:
                            coberta[idx] = 0
                            cobertos -= 1
                    for idx in indices_cand:
                        if contagem[idx] == 0:
                            coberta[idx] = 1
                            cobertos += 1
                        contagem[idx] += 1
                    pares[i] = (pool[ci], indices_cand)
                    progresso = True
                    break
            if cobertos >= total_t:
                break
        apostas_tuplas = [a for a, _ in pares]
        indices_por_aposta = [ix for _, ix in pares]
        if not progresso:
            break

    return [list(a) for a in apostas_tuplas]


def fechamento_lotofacil_25(
    k: int = 15,
    t: int = 11,
    max_apostas: int = 2000,
    seed: int = 42,
    universo: Optional[List[int]] = None,
    **kw,
) -> List[List[int]]:
    """
    Fechamento para Lotofacil.

    Default: universo 1..25, garantia de 11 acertos (t=11) em apostas de
    15 dezenas (k=15), com no maximo ``max_apostas`` jogos.
    """
    universo_efetivo = list(universo) if universo is not None else list(range(1, 26))
    return construir_fechamento_guloso_amostrado(
        universo_efetivo,
        k=k,
        t=t,
        max_apostas=max_apostas,
        seed=seed,
        **kw,
    )


def fechamento_lotofacil_25_otimizado(
    k: int = 15,
    t: int = 11,
    max_apostas: int = 200,
    seed: int = 7,
    universo: Optional[List[int]] = None,
    remover_redundantes: bool = False,
    **kw,
) -> List[List[int]]:
    """
    Fechamento para Lotofacil com otimizacao de busca local.

    Executa o guloso amostrado e depois aplica hill climbing para elevar a
    cobertura sem aumentar o numero de apostas (melhor custo-beneficio).
    ``universo`` permite gerar sobre um subconjunto (ex.: apos remover
    fixos e excluidos) sem que a busca local escape dele.
    """
    universo_efetivo = list(universo) if universo is not None else list(range(1, 26))
    apostas = construir_fechamento_guloso_amostrado(
        universo_efetivo,
        k=k,
        t=t,
        max_apostas=max_apostas,
        seed=seed,
        **{kk: vv for kk, vv in kw.items() if kk not in ("max_iteracoes", "busca_seed")},
    )
    if len(apostas) > 1:
        apostas = busca_local_fechamento(
            apostas,
            universo_efetivo,
            k=k,
            t=t,
            max_iteracoes=kw.get("max_iteracoes", 100),
            seed=kw.get("busca_seed", seed + 1),
            candidatos_pool=kw.get("candidatos_pool", 400),
        )
    if remover_redundantes:
        apostas = remover_apostas_redundantes(apostas, universo_efetivo, k, t)
    return apostas
