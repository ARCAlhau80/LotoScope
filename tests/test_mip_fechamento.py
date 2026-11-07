"""Teste do script MIP (SCIP/CBC) de fechamento combinatório."""
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import pytest

pytest.importorskip("ortools")

SCRIPT = Path(__file__).resolve().parents[1] / "dashboard" / "scripts" / "mip_fechamento.py"


def _cobre(apostas, universo, t):
    alvos = set(combinations(sorted(universo), t))
    cobertos = set()
    for aposta in apostas:
        cobertos.update(combinations(sorted(aposta), t))
    return alvos.issubset(cobertos)


@pytest.mark.parametrize("solver", ["SCIP", "CBC"])
def test_mip_resolve_instancia_pequena(solver):
    universo = list(range(1, 8))
    payload = {
        "universo": universo,
        "k": 5,
        "t": 3,
        "seed": 1,
        "pool": 100,
        "time_limit": 5,
        "threads": 1,
        "max_apostas": 0,
        "extras": [],
        "solver": solver,
    }
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["status"] in ("OPTIMAL", "FEASIBLE")
    assert data["bets"]
    assert all(len(b) == 5 for b in data["bets"])
    assert _cobre(data["bets"], universo, 3)
