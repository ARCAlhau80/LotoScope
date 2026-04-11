# -*- coding: utf-8 -*-
"""
POC: V3 Duplas Históricas na Base Inteira
=========================================

Para cada concurso t:
- Treina ranking de duplas com concursos [1 .. t-1]
- Gera jogos pela lógica V3 (cadeia encadeada), com fixos {1, 25}
- Compara com pacotes aleatórios de mesmo tamanho
- Mede:
  * melhor acerto por concurso
  * acerto médio por jogo
  * recuperação financeira média (prêmios / custo)

Prêmios usados no projeto:
11 = R$ 7
12 = R$ 14
13 = R$ 35
14 = R$ 1.000
15 = R$ 1.800.000
Custo = R$ 3,50 por jogo
"""

import sys
import time
from collections import Counter
from itertools import combinations

import numpy as np
import pyodbc

sys.stdout.reconfigure(encoding='utf-8')

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
FIXOS = {1, 25}
TARGET_SIZE = 15
MIN_TREINO = 100
MAX_COMBOS = 100
RANDOM_PACKS = 20
CUSTO_JOGO = 3.50
PREMIOS = {
    11: 7.0,
    12: 14.0,
    13: 35.0,
    14: 1000.0,
    15: 1800000.0,
}


def carregar_resultados():
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
        )
        return [
            {"concurso": row[0], "numeros": tuple(sorted(int(x) for x in row[1:16]))}
            for row in cursor.fetchall()
        ]


def atualizar_pair_count(pair_count, numeros):
    for pair in combinations(numeros, 2):
        pair_count[pair] += 1


def gerar_combos_v3(pair_count, fixos=FIXOS, target_size=TARGET_SIZE, max_combos=MAX_COMBOS):
    """Cadeia encadeada de duplas, igual à POC anterior."""
    ranked_pairs = [pair for pair, _ in pair_count.most_common()]
    combos = []
    seen = set()

    for start_pair in ranked_pairs[:max_combos * 3]:
        jogo = set(fixos)
        jogo.update(start_pair)

        for pair in ranked_pairs:
            if len(jogo) >= target_size:
                break
            a, b = pair
            if a in jogo or b in jogo:
                if a not in jogo and len(jogo) < target_size:
                    jogo.add(a)
                if b not in jogo and len(jogo) < target_size:
                    jogo.add(b)

        if len(jogo) == target_size:
            key = frozenset(jogo)
            if key not in seen:
                seen.add(key)
                combos.append(tuple(sorted(jogo)))

        if len(combos) >= max_combos:
            break

    return combos


def avaliar_pacote(combos, resultado_set, rng):
    hits = []
    payout = 0.0
    faixa = Counter()

    for combo in combos:
        acertos = len(resultado_set.intersection(combo))
        hits.append(acertos)
        if acertos >= 11:
            faixa[acertos] += 1
            payout += PREMIOS[acertos]

    custo = len(combos) * CUSTO_JOGO
    return {
        "hits": hits,
        "best": max(hits) if hits else 0,
        "mean_hits": float(np.mean(hits)) if hits else 0.0,
        "payout": payout,
        "cost": custo,
        "roi": (payout - custo) / custo * 100 if custo > 0 else 0.0,
        "faixa": faixa,
    }


def avaliar_random_baseline(qtd_combos, resultado_set, rng, packs=RANDOM_PACKS):
    all_numbers = np.arange(1, 26)

    best_list = []
    mean_hits_list = []
    payout_list = []
    roi_list = []
    faixa_total = Counter()

    for _ in range(packs):
        combos = [tuple(sorted(rng.choice(all_numbers, 15, replace=False).tolist())) for _ in range(qtd_combos)]
        ev = avaliar_pacote(combos, resultado_set, rng)
        best_list.append(ev["best"])
        mean_hits_list.append(ev["mean_hits"])
        payout_list.append(ev["payout"])
        roi_list.append(ev["roi"])
        faixa_total.update(ev["faixa"])

    return {
        "best_mean": float(np.mean(best_list)) if best_list else 0.0,
        "mean_hits_mean": float(np.mean(mean_hits_list)) if mean_hits_list else 0.0,
        "payout_mean": float(np.mean(payout_list)) if payout_list else 0.0,
        "roi_mean": float(np.mean(roi_list)) if roi_list else 0.0,
        "faixa_mean": {k: v / packs for k, v in faixa_total.items()},
        "best_ge_strategy_count": 0,
    }


def main():
    print("=" * 78)
    print("POC V3 — BASE HISTÓRICA INTEIRA")
    print("=" * 78)
    print(f"Treino mínimo: {MIN_TREINO} concursos")
    print(f"Fixos: {sorted(FIXOS)}")
    print(f"Packs aleatórios por concurso: {RANDOM_PACKS}")

    resultados = carregar_resultados()
    rng = np.random.default_rng(42)
    pair_count = Counter()

    for item in resultados[:MIN_TREINO]:
        atualizar_pair_count(pair_count, item["numeros"])

    metricas = {
        "concursos": 0,
        "qtd_combos": [],
        "strat_best": [],
        "rand_best": [],
        "strat_mean_hits": [],
        "rand_mean_hits": [],
        "strat_payout": [],
        "rand_payout": [],
        "strat_roi": [],
        "rand_roi": [],
        "strat_faixa": Counter(),
        "rand_faixa": Counter(),
        "best_lower_but_mean_better": 0,
        "best_lower_but_roi_better": 0,
        "best_lower_total": 0,
        "best_equal_or_higher": 0,
        "positive_roi_strat": 0,
        "positive_roi_rand": 0,
        "break_even_strat": 0,
        "break_even_rand": 0,
    }

    t0 = time.time()
    total_testes = len(resultados) - MIN_TREINO

    for idx in range(MIN_TREINO, len(resultados)):
        atual = resultados[idx]
        resultado_set = set(atual["numeros"])
        combos_v3 = gerar_combos_v3(pair_count)
        if not combos_v3:
            atualizar_pair_count(pair_count, atual["numeros"])
            continue

        strat = avaliar_pacote(combos_v3, resultado_set, rng)
        rand = avaliar_random_baseline(len(combos_v3), resultado_set, rng)

        metricas["concursos"] += 1
        metricas["qtd_combos"].append(len(combos_v3))
        metricas["strat_best"].append(strat["best"])
        metricas["rand_best"].append(rand["best_mean"])
        metricas["strat_mean_hits"].append(strat["mean_hits"])
        metricas["rand_mean_hits"].append(rand["mean_hits_mean"])
        metricas["strat_payout"].append(strat["payout"])
        metricas["rand_payout"].append(rand["payout_mean"])
        metricas["strat_roi"].append(strat["roi"])
        metricas["rand_roi"].append(rand["roi_mean"])
        metricas["strat_faixa"].update(strat["faixa"])
        for faixa, valor_medio in rand["faixa_mean"].items():
            metricas["rand_faixa"][faixa] += valor_medio

        if strat["roi"] > 0:
            metricas["positive_roi_strat"] += 1
        if rand["roi_mean"] > 0:
            metricas["positive_roi_rand"] += 1
        if strat["payout"] >= strat["cost"]:
            metricas["break_even_strat"] += 1
        if rand["payout_mean"] >= strat["cost"]:
            metricas["break_even_rand"] += 1

        if strat["best"] < rand["best_mean"]:
            metricas["best_lower_total"] += 1
            if strat["mean_hits"] > rand["mean_hits_mean"]:
                metricas["best_lower_but_mean_better"] += 1
            if strat["roi"] > rand["roi_mean"]:
                metricas["best_lower_but_roi_better"] += 1
        else:
            metricas["best_equal_or_higher"] += 1

        atualizar_pair_count(pair_count, atual["numeros"])

        if (idx - MIN_TREINO + 1) % 500 == 0:
            elapsed = time.time() - t0
            print(f"Processado {idx - MIN_TREINO + 1:,}/{total_testes:,} concursos ({elapsed:.1f}s)")

    elapsed_total = time.time() - t0
    concursos = metricas["concursos"]
    media_combos = np.mean(metricas["qtd_combos"]) if metricas["qtd_combos"] else 0.0
    total_jogos = int(sum(metricas["qtd_combos"]))
    custo_total = total_jogos * CUSTO_JOGO

    print("\n" + "=" * 78)
    print("RESULTADO CONSOLIDADO")
    print("=" * 78)
    print(f"Concursos avaliados: {concursos:,}")
    print(f"Jogos médios por concurso: {media_combos:.2f}")
    print(f"Total de jogos V3: {total_jogos:,}")
    print(f"Tempo total: {elapsed_total:.1f}s")

    print("\n1) Melhor acerto por concurso")
    strat_best_mean = float(np.mean(metricas["strat_best"]))
    rand_best_mean = float(np.mean(metricas["rand_best"]))
    print(f"V3:       {strat_best_mean:.3f}")
    print(f"Aleatório:{rand_best_mean:.3f}")
    print(f"Delta:    {strat_best_mean - rand_best_mean:+.3f}")

    print("\n2) Recuperação média por jogo (acertos médios)")
    strat_mean_hits = float(np.mean(metricas["strat_mean_hits"]))
    rand_mean_hits = float(np.mean(metricas["rand_mean_hits"]))
    print(f"V3:       {strat_mean_hits:.4f}")
    print(f"Aleatório:{rand_mean_hits:.4f}")
    print(f"Delta:    {strat_mean_hits - rand_mean_hits:+.4f}")

    print("\n3) Recuperação financeira média por concurso")
    strat_payout_mean = float(np.mean(metricas["strat_payout"]))
    rand_payout_mean = float(np.mean(metricas["rand_payout"]))
    strat_roi_mean = float(np.mean(metricas["strat_roi"]))
    rand_roi_mean = float(np.mean(metricas["rand_roi"]))
    custo_medio = media_combos * CUSTO_JOGO
    print(f"Custo médio do pacote:     R$ {custo_medio:,.2f}")
    print(f"Prêmio médio V3:           R$ {strat_payout_mean:,.2f}")
    print(f"Prêmio médio aleatório:    R$ {rand_payout_mean:,.2f}")
    print(f"Delta prêmio médio:        R$ {strat_payout_mean - rand_payout_mean:+,.2f}")
    print(f"ROI médio V3:              {strat_roi_mean:+.2f}%")
    print(f"ROI médio aleatório:       {rand_roi_mean:+.2f}%")
    print(f"Delta ROI médio:           {strat_roi_mean - rand_roi_mean:+.2f} pp")

    print("\n4) Faixas premiadas acumuladas")
    print(f"{'Faixa':>8s} {'V3':>12s} {'Aleatório':>12s} {'Selet':>8s}")
    for faixa in [11, 12, 13, 14, 15]:
        s = metricas["strat_faixa"].get(faixa, 0.0)
        r = metricas["rand_faixa"].get(faixa, 0.0)
        selet = s / r if r > 0 else float('inf')
        print(f"{faixa:>8d} {s:>12.1f} {r:>12.1f} {selet:>7.3f}x")

    print("\n5) Quando o melhor acerto do V3 fica abaixo do aleatório")
    lower_total = metricas["best_lower_total"]
    lower_pct = lower_total / concursos * 100 if concursos else 0.0
    print(f"Ocorrências: {lower_total:,} ({lower_pct:.1f}%)")
    if lower_total > 0:
        mean_better_pct = metricas["best_lower_but_mean_better"] / lower_total * 100
        roi_better_pct = metricas["best_lower_but_roi_better"] / lower_total * 100
        print(f"Mesmo assim teve acerto médio maior: {metricas['best_lower_but_mean_better']:,} ({mean_better_pct:.1f}%)")
        print(f"Mesmo assim teve ROI maior:          {metricas['best_lower_but_roi_better']:,} ({roi_better_pct:.1f}%)")
    print(f"Empatou ou superou melhor acerto: {metricas['best_equal_or_higher']:,}")

    print("\n6) Consistência financeira")
    pos_strat = metricas["positive_roi_strat"] / concursos * 100 if concursos else 0.0
    pos_rand = metricas["positive_roi_rand"] / concursos * 100 if concursos else 0.0
    be_strat = metricas["break_even_strat"] / concursos * 100 if concursos else 0.0
    be_rand = metricas["break_even_rand"] / concursos * 100 if concursos else 0.0
    print(f"ROI > 0  | V3: {pos_strat:.2f}% | Aleatório: {pos_rand:.2f}%")
    print(f"Break-even | V3: {be_strat:.2f}% | Aleatório: {be_rand:.2f}%")

    print("\n7) Consolidado financeiro total")
    total_payout_v3 = float(sum(metricas["strat_payout"]))
    total_payout_rand = float(sum(metricas["rand_payout"]))
    total_roi_v3 = (total_payout_v3 - custo_total) / custo_total * 100 if custo_total > 0 else 0.0
    total_roi_rand = (total_payout_rand - custo_total) / custo_total * 100 if custo_total > 0 else 0.0
    print(f"Custo total V3:         R$ {custo_total:,.2f}")
    print(f"Prêmio total V3:        R$ {total_payout_v3:,.2f}")
    print(f"Prêmio total aleatório: R$ {total_payout_rand:,.2f}")
    print(f"ROI total V3:           {total_roi_v3:+.2f}%")
    print(f"ROI total aleatório:    {total_roi_rand:+.2f}%")
    print(f"Delta ROI total:        {total_roi_v3 - total_roi_rand:+.2f} pp")


if __name__ == "__main__":
    main()
