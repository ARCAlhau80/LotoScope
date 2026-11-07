"""Teste do script CP-SAT de fechamento combinatório."""
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import pytest

pytest.importorskip("ortools")

SCRIPT = Path(__file__).resolve().parents[1] / "dashboard" / "scripts" / "cp_sat_fechamento.py"


def _cobre(apostas, universo, t):
    alvos = set(combinations(sorted(universo), t))
    cobertos = set()
    for aposta in apostas:
        cobertos.update(combinations(sorted(aposta), t))
    return alvos.issubset(cobertos)


def test_cp_sat_resolve_instancia_pequena():
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
