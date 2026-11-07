#!/usr/bin/env python3
"""CP-SAT para fechamento combinatório (set cover).

Recebe JSON via stdin:
{
  "universo": [2,3,...,24],
  "k": 13,
  "t": 3,
  "seed": 1,
  "pool": 5000,
  "time_limit": 20,
  "threads": 4,
  "max_apostas": 0,
  "extras": [[...], ...]   # candidatos que já cobrem tudo (ex.: solução heurística)
}

Retorna JSON:
{"status": "OPTIMAL|FEASIBLE|INFEASIBLE|UNKNOWN|MODEL_INVALID",
 "objective": 9, "best_bound": 8, "bets": [[...]], "wall_time": 1.23,
 "num_candidates": 5000, "num_targets": 1771, "lower_bound": 8}
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from itertools import combinations
from typing import Iterable, List, Optional

from ortools.sat.python import cp_model


def _dedup(candidatos: Iterable[Iterable[int]], k: int) -> List[List[int]]:
    vistos = set()
    out: List[List[int]] = []
    for cand in candidatos:
        c = tuple(sorted(int(x) for x in cand))
        if len(c) != k or len(set(c)) != k:
            continue
        if c in vistos:
            continue
        vistos.add(c)
        out.append(list(c))
    return out


def _gerar_candidatos(
    universo: List[int],
    k: int,
    pool: int,
    seed: int,
    extras: List[List[int]],
) -> List[List[int]]:
    candidatos = _dedup(extras, k)
    total = math.comb(len(universo), k) if len(universo) >= k else 0
    if total <= pool:
        for c in combinations(universo, k):
            candidatos.append(list(c))
        return _dedup(candidatos, k)

    rng = random.Random(seed)
    alvo = max(pool, len(candidatos))
    tentativas = 0
    limite_tentativas = alvo * 20
    vistos = {tuple(c) for c in candidatos}
    while len(candidatos) < alvo and tentativas < limite_tentativas:
        cand = tuple(sorted(rng.sample(universo, k)))
        tentativas += 1
        if cand in vistos:
            continue
        vistos.add(cand)
        candidatos.append(list(cand))
    return candidatos


def _limite_inferior_schonheim(v: int, k: int, t: int) -> int:
    if t <= 0 or k <= 0 or v <= 0 or k > v:
        return 0
    if t == 1:
        return math.ceil(v / k)
    return math.ceil((v / k) * _limite_inferior_schonheim(v - 1, k - 1, t - 1))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "MODEL_INVALID", "error": f"JSON inválido: {exc}"}))
        return 1

    universo = sorted({int(x) for x in payload.get("universo", [])})
    k = int(payload.get("k", 0))
    t = int(payload.get("t", 0))
    seed = int(payload.get("seed", 1))
    pool = max(1, int(payload.get("pool", 5000)))
    time_limit = max(0.5, float(payload.get("time_limit", 20.0)))
    threads = max(1, int(payload.get("threads", 4)))
    max_apostas = int(payload.get("max_apostas", 0) or 0)
    upper_bound = int(payload.get("upper_bound", 0) or 0)
    extras = payload.get("extras", []) or []

    inicio = time.time()
    if len(universo) < k or k < t or t < 1:
        print(json.dumps({"status": "MODEL_INVALID", "error": "Deve valer 1 <= t <= k <= v"}))
        return 0

    alvos = list(combinations(universo, t))
    total_alvos = len(alvos)
    if total_alvos <= 0:
        print(json.dumps({"status": "FEASIBLE", "objective": 0, "best_bound": 0, "bets": [], "wall_time": 0.0, "num_candidates": 0, "num_targets": 0, "lower_bound": 0}))
        return 0

    # Limita o pool para não estourar memória em t alto.
    if total_alvos > 200_000:
        pool = min(pool, 2000)
    elif total_alvos > 50_000:
        pool = min(pool, 3000)
    elif total_alvos > 10_000:
        pool = min(pool, 4000)

    candidatos = _gerar_candidatos(universo, k, pool, seed, extras)
    n = len(candidatos)
    if n == 0:
        print(json.dumps({"status": "INFEASIBLE", "error": "Pool de candidatos vazio"}))
        return 0

    indice_alvo = {alvo: i for i, alvo in enumerate(alvos)}
    coverers: List[List[int]] = [[] for _ in range(total_alvos)]

    # Mapeia cada t-subconjunto para os candidatos que o cobrem.
    for ci, cand in enumerate(candidatos):
        for sub in combinations(cand, t):
            alvo_idx = indice_alvo.get(sub)
            if alvo_idx is not None:
                coverers[alvo_idx].append(ci)

    # Sem extras garantindo cobertura, pode faltar alvo. Reporta para o caller
    # decidir entre ampliar o pool ou cair no heurístico.
    sem_cobertura = [i for i, c in enumerate(coverers) if not c]
    if sem_cobertura:
        print(json.dumps({
            "status": "POOL_INCOMPLETO",
            "error": f"{len(sem_cobertura)} t-subconjunto(s) sem candidato no pool",
            "num_candidates": n,
            "num_targets": total_alvos,
            "lower_bound": _limite_inferior_schonheim(len(universo), k, t),
        }))
        return 0

    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(n)]
    for cover in coverers:
        model.Add(sum(x[i] for i in cover) >= 1)
    model.Minimize(sum(x))
    if upper_bound > 0:
        model.Add(sum(x) <= upper_bound)
    if max_apostas > 0:
        model.Add(sum(x) <= max_apostas)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = threads
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)
    status_name = solver.StatusName(status)

    bets: List[List[int]] = []
    objective: Optional[float] = None
    best_bound: Optional[float] = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        bets = [candidatos[i] for i in range(n) if solver.Value(x[i])]
        objective = solver.ObjectiveValue()
        best_bound = solver.BestObjectiveBound()

    print(json.dumps({
        "status": status_name,
        "objective": objective,
        "best_bound": best_bound,
        "bets": bets,
        "wall_time": round(time.time() - inicio, 3),
        "num_candidates": n,
        "num_targets": total_alvos,
        "lower_bound": _limite_inferior_schonheim(len(universo), k, t),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
