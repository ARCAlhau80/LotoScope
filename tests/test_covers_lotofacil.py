"""Valida o registry de covering designs da Lotofácil.

Todo cover em ``covers-lotofacil.json`` precisa cobrir 100% dos
``t``-subconjuntos do universo ``v`` com blocos de tamanho ``k``.
"""
from __future__ import annotations

import json
import os
from itertools import combinations
from math import comb
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
COVERS = RAIZ / "dashboard" / "src" / "data" / "covers-lotofacil.json"

# t>=9 tem milhares de blocos; a validação exaustiva demora minutos.
# Rode com LOTOSCOPE_SLOW=1 para validar também esses covers.
VALIDAR_GRANDES = os.environ.get("LOTOSCOPE_SLOW") == "1"


def _t_subsets_cobertos(v: int, k: int, t: int, blocos: list[list[int]]) -> set[int]:
    cobertos: set[int] = set()
    for bloco in blocos:
        idx = [p - 1 for p in bloco]
        if len(idx) != k or len(set(idx)) != k or any(i < 0 or i >= v for i in idx):
            continue
        for sub in combinations(idx, t):
            mask = 0
            for x in sub:
                mask |= 1 << x
            cobertos.add(mask)
    return cobertos


def test_covers_lotofacil_sao_validos():
    dados: dict[str, dict] = json.loads(COVERS.read_text(encoding="utf-8"))
    assert dados, "registry de covers vazio"

    falhas: list[str] = []
    for chave, cover in dados.items():
        v, k, t = cover["v"], cover["k"], cover["t"]
        assert chave == f"{v},{k},{t}", f"chave {chave} não bate com v,k,t"
        assert v >= k >= t >= 1, f"C({v},{k},{t}) inválido"
        assert cover["blocos"], f"C({v},{k},{t}) sem blocos"
        assert cover["fonte"], f"C({v},{k},{t}) sem fonte"
        assert cover["limiteInferior"] >= 1, f"C({v},{k},{t}) sem limite inferior"

        if t >= 9 and not VALIDAR_GRANDES:
            assert cover.get("verificado") is True, f"C({v},{k},{t}) grande sem selo verificado"
            continue

        cobertos = _t_subsets_cobertos(v, k, t, cover["blocos"])
        total = comb(v, t)
        if len(cobertos) != total:
            falhas.append(f"C({v},{k},{t}): {len(cobertos)}/{total}")

    assert not falhas, "covers que não cobrem tudo: " + ", ".join(falhas[:10])
