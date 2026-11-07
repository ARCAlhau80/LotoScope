#!/usr/bin/env python3
"""MIP para fechamento combinatório (set cover) usando SCIP ou CBC.

Mesmo contrato do CP-SAT, com um campo extra "solver": "SCIP" | "CBC".
"""
from __future__ import annotations

import contextlib
import json
import math
import random
import sys
import time
from itertools import combinations
from typing import Iterable, List, Optional

from ortools.linear_solver import pywraplp

# Reaproveita geração de pool e bound do script CP-SAT.
from cp_sat_fechamento import _dedup, _gerar_candidatos, _limite_inferior_schonheim


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
    pool = max(1, int(payload.get("pool", 500)))
    time_limit = max(0.5, float(payload.get("time_limit", 10.0)))
    threads = max(1, int(payload.get("threads", 4)))
    max_apostas = int(payload.get("max_apostas", 0) or 0)
    upper_bound = int(payload.get("upper_bound", 0) or 0)
    extras = payload.get("extras", []) or []
    solver_name = str(payload.get("solver", "SCIP")).upper()
    if solver_name not in ("SCIP", "CBC"):
        solver_name = "SCIP"

    inicio = time.time()
    if len(universo) < k or k < t or t < 1:
        print(json.dumps({"status": "MODEL_INVALID", "error": "Deve valer 1 <= t <= k <= v"}))
        return 0

    alvos = list(combinations(universo, t))
    total_alvos = len(alvos)
    if total_alvos <= 0:
        print(json.dumps({"status": "FEASIBLE", "objective": 0, "best_bound": 0, "bets": [], "wall_time": 0.0, "num_candidates": 0, "num_targets": 0, "lower_bound": 0, "solver": solver_name}))
        return 0

    if total_alvos > 200_000:
        pool = min(pool, 2000)
    elif total_alvos > 50_000:
        pool = min(pool, 3000)
    elif total_alvos > 10_000:
        pool = min(pool, 4000)

    candidatos = _gerar_candidatos(universo, k, pool, seed, extras)
    n = len(candidatos)
    if n == 0:
        print(json.dumps({"status": "INFEASIBLE", "error": "Pool de candidatos vazio", "solver": solver_name}))
        return 0

    indice_alvo = {alvo: i for i, alvo in enumerate(alvos)}
    coverers: List[List[int]] = [[] for _ in range(total_alvos)]
    for ci, cand in enumerate(candidatos):
        for sub in combinations(cand, t):
            alvo_idx = indice_alvo.get(sub)
            if alvo_idx is not None:
                coverers[alvo_idx].append(ci)

    sem_cobertura = [i for i, c in enumerate(coverers) if not c]
    if sem_cobertura:
        print(json.dumps({
            "status": "POOL_INCOMPLETO",
            "error": f"{len(sem_cobertura)} t-subconjunto(s) sem candidato no pool",
            "num_candidates": n,
            "num_targets": total_alvos,
            "lower_bound": _limite_inferior_schonheim(len(universo), k, t),
            "solver": solver_name,
        }))
        return 0

    solver = pywraplp.Solver.CreateSolver(solver_name)
    if not solver:
        print(json.dumps({"status": "ERRO", "error": f"Solver {solver_name} indisponível", "solver": solver_name}))
        return 0

    x = [solver.BoolVar(f"x{i}") for i in range(n)]
    for cov in coverers:
        solver.Add(sum(x[i] for i in cov) >= 1)
    solver.Minimize(sum(x))
    if upper_bound > 0:
        solver.Add(sum(x) <= upper_bound)
    if max_apostas > 0:
        solver.Add(sum(x) <= max_apostas)

    # Evita que logs do SCIP/CBC contaminem o JSON de saída.
    with contextlib.redirect_stdout(sys.stderr):
        try:
            if solver_name != "CBC":
                solver.SetNumThreads(threads)
        except Exception:
            pass
        solver.SetTimeLimit(int(time_limit * 1000))

        # Hint com a solução heurística, quando disponível.
        if extras:
            extra_set = {tuple(sorted(c)) for c in extras}
            hint = [1 if tuple(sorted(c)) in extra_set else 0 for c in candidatos]
            try:
                solver.SetHint(x, hint)
            except Exception:
                pass

        status = solver.Solve()

    status_map = {
        pywraplp.Solver.OPTIMAL: "OPTIMAL",
        pywraplp.Solver.FEASIBLE: "FEASIBLE",
        pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
        pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
        pywraplp.Solver.ABNORMAL: "ABNORMAL",
        pywraplp.Solver.MODEL_INVALID: "MODEL_INVALID",
        pywraplp.Solver.NOT_SOLVED: "UNKNOWN",
    }
    status_name = status_map.get(status, "UNKNOWN")

    bets: List[List[int]] = []
    objective: Optional[float] = None
    best_bound: Optional[float] = None
    if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        bets = [candidatos[i] for i in range(n) if x[i].solution_value() > 0.5]
        objective = float(solver.Objective().Value())
        try:
            best_bound = float(solver.Objective().BestBound())
        except Exception:
            best_bound = None

    print(json.dumps({
        "status": status_name,
        "objective": objective,
        "best_bound": best_bound,
        "bets": bets,
        "wall_time": round(time.time() - inicio, 3),
        "num_candidates": n,
        "num_targets": total_alvos,
        "lower_bound": _limite_inferior_schonheim(len(universo), k, t),
        "solver": solver_name,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
