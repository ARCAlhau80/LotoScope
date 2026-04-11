# -*- coding: utf-8 -*-
"""
POC: Incompatibilidade entre filtros do Pool 23

Objetivo:
- Detectar combinações de filtros estruturais que "matam jackpot"
- Medir pass rate em sorteios reais vs combos aleatórios
- Calcular seletividade e índice de toxicidade para pares/trios e pacotes por nível

Escopo desta POC:
- Somente filtros estruturais, auditáveis e reproduzíveis offline
- Exclui filtros fortemente dinâmicos/contextuais: piores_historico, piores_recente,
  débito posicional, anomalias, subcombos, trios e posições frias
"""

import sys
from collections import Counter
from itertools import combinations

import numpy as np
import pyodbc

from lotofacil_lite.configuracao_filtros_pool23 import FILTROS_POR_NIVEL

sys.stdout.reconfigure(encoding='utf-8')

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
RANDOM_SAMPLES = 200000

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
NUCLEO_C1C2 = {2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 22, 24, 25}


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


def filtro_soma(combo, config):
    return config['soma_min'] <= sum(combo) <= config['soma_max']


def filtro_pares(combo, config):
    if 'pares_min' not in config:
        return True
    qtde = sum(1 for n in combo if n % 2 == 0)
    return config['pares_min'] <= qtde <= config['pares_max']


def filtro_primos(combo, config):
    if 'primos_min' not in config:
        return True
    qtde = sum(1 for n in combo if n in PRIMOS)
    return config['primos_min'] <= qtde <= config['primos_max']


def filtro_seq_max(combo, config):
    if 'seq_max' not in config:
        return True
    nums = sorted(combo)
    max_seq = 1
    seq = 1
    for idx in range(1, len(nums)):
        if nums[idx] == nums[idx - 1] + 1:
            seq += 1
            max_seq = max(max_seq, seq)
        else:
            seq = 1
    return max_seq <= config['seq_max']


def filtro_linhas(combo, config):
    if not config.get('usar_filtro_linhas'):
        return True
    linhas = [0, 0, 0, 0, 0]
    for n in combo:
        linhas[(n - 1) // 5] += 1
    return all(config['linhas_min'] <= x <= config['linhas_max'] for x in linhas)


def filtro_colunas(combo, config):
    if not config.get('usar_filtro_colunas'):
        return True
    colunas = [0, 0, 0, 0, 0]
    for n in combo:
        colunas[(n - 1) % 5] += 1
    return all(config['colunas_min'] <= x <= config['colunas_max'] for x in colunas)


def filtro_qtde_6_25(combo, config):
    if not config.get('usar_filtro_qtde_6_25'):
        return True
    qtde = sum(1 for n in combo if 6 <= n <= 25)
    return qtde in set(config['qtde_6_25_valores'])


def filtro_fibonacci(combo, config):
    if not config.get('usar_filtro_fibonacci'):
        return True
    qtde = sum(1 for n in combo if n in FIBONACCI)
    return config['fibonacci_min'] <= qtde <= config['fibonacci_max']


def filtro_quintis(combo, config):
    if not config.get('usar_filtro_quintis'):
        return True
    quintis = [0, 0, 0, 0, 0]
    for n in combo:
        quintis[(n - 1) // 5] += 1
    return all(config['quintis_min'] <= x <= config['quintis_max'] for x in quintis)


def filtro_faixa_6_20(combo, config):
    if not config.get('usar_filtro_faixa_6_20'):
        return True
    qtde = sum(1 for n in combo if 6 <= n <= 20)
    return config['faixa_6_20_min'] <= qtde <= config['faixa_6_20_max']


def filtro_nucleo(combo, config):
    if 'nucleo_min' not in config:
        return True
    qtde = sum(1 for n in combo if n in NUCLEO_C1C2)
    return qtde >= config['nucleo_min']


def build_filters_for_level(level):
    config = FILTROS_POR_NIVEL[level]
    filters = {}
    if 'soma_min' in config:
        filters['soma'] = lambda c, cfg=config: filtro_soma(c, cfg)
    if 'pares_min' in config:
        filters['pares'] = lambda c, cfg=config: filtro_pares(c, cfg)
    if 'primos_min' in config:
        filters['primos'] = lambda c, cfg=config: filtro_primos(c, cfg)
    if 'seq_max' in config:
        filters['seq_max'] = lambda c, cfg=config: filtro_seq_max(c, cfg)
    if config.get('usar_filtro_linhas'):
        filters['linhas'] = lambda c, cfg=config: filtro_linhas(c, cfg)
    if config.get('usar_filtro_colunas'):
        filters['colunas'] = lambda c, cfg=config: filtro_colunas(c, cfg)
    if config.get('usar_filtro_qtde_6_25'):
        filters['qtde_6_25'] = lambda c, cfg=config: filtro_qtde_6_25(c, cfg)
    if config.get('usar_filtro_fibonacci'):
        filters['fibonacci'] = lambda c, cfg=config: filtro_fibonacci(c, cfg)
    if config.get('usar_filtro_quintis'):
        filters['quintis'] = lambda c, cfg=config: filtro_quintis(c, cfg)
    if config.get('usar_filtro_faixa_6_20'):
        filters['faixa_6_20'] = lambda c, cfg=config: filtro_faixa_6_20(c, cfg)
    if 'nucleo_min' in config:
        filters['nucleo'] = lambda c, cfg=config: filtro_nucleo(c, cfg)
    return filters


def random_combos(n_samples, rng):
    base = np.arange(1, 26)
    return [tuple(sorted(rng.choice(base, 15, replace=False).tolist())) for _ in range(n_samples)]


def pass_rate(combos, predicate):
    passed = sum(1 for combo in combos if predicate(combo))
    total = len(combos)
    return passed, passed / total if total else 0.0


def toxicity_index(real_rate, random_rate):
    if random_rate <= 0:
        return 0.0
    seletividade = real_rate / random_rate
    kill = 1.0 - real_rate
    # Alto quando mata muito jackpot sem inteligência compensatória
    return kill * max(0.0, 1.0 - seletividade)


def format_pct(value):
    return f'{value * 100:6.2f}%'


def analyze_level(level, real_draws, random_draws):
    filters = build_filters_for_level(level)
    if not filters:
        return None

    results = {}
    for name, fn in filters.items():
        _, rr = pass_rate(real_draws, fn)
        _, pr = pass_rate(random_draws, fn)
        sel = rr / pr if pr > 0 else 0.0
        tox = toxicity_index(rr, pr)
        results[name] = {
            'real_rate': rr,
            'random_rate': pr,
            'selectivity': sel,
            'toxicity': tox,
        }

    pair_results = []
    names = sorted(filters.keys())
    for a, b in combinations(names, 2):
        fn = lambda combo, f1=filters[a], f2=filters[b]: f1(combo) and f2(combo)
        _, rr = pass_rate(real_draws, fn)
        _, pr = pass_rate(random_draws, fn)
        sel = rr / pr if pr > 0 else 0.0
        tox = toxicity_index(rr, pr)
        expected_ind = results[a]['real_rate'] * results[b]['real_rate']
        incompat = max(0.0, expected_ind - rr)
        pair_results.append({
            'combo': f'{a}+{b}',
            'real_rate': rr,
            'random_rate': pr,
            'selectivity': sel,
            'toxicity': tox,
            'incompatibility': incompat,
        })

    triplet_results = []
    if len(names) >= 3:
        for a, b, c in combinations(names, 3):
            fn = lambda combo, f1=filters[a], f2=filters[b], f3=filters[c]: f1(combo) and f2(combo) and f3(combo)
            _, rr = pass_rate(real_draws, fn)
            _, pr = pass_rate(random_draws, fn)
            sel = rr / pr if pr > 0 else 0.0
            tox = toxicity_index(rr, pr)
            triplet_results.append({
                'combo': f'{a}+{b}+{c}',
                'real_rate': rr,
                'random_rate': pr,
                'selectivity': sel,
                'toxicity': tox,
            })

    package_fn = lambda combo: all(fn(combo) for fn in filters.values())
    _, pkg_real = pass_rate(real_draws, package_fn)
    _, pkg_rand = pass_rate(random_draws, package_fn)
    package = {
        'real_rate': pkg_real,
        'random_rate': pkg_rand,
        'selectivity': pkg_real / pkg_rand if pkg_rand > 0 else 0.0,
        'toxicity': toxicity_index(pkg_real, pkg_rand),
        'count_filters': len(filters),
    }

    return {
        'level': level,
        'descricao': FILTROS_POR_NIVEL[level]['descricao'],
        'filters': results,
        'pairs': pair_results,
        'triplets': triplet_results,
        'package': package,
    }


def print_level_report(report):
    print('\n' + '=' * 78)
    print(f"NIVEL {report['level']} — {report['descricao']}")
    print('=' * 78)

    print('\nFiltros individuais')
    print(f"{'Filtro':<14} {'Real':>10} {'Random':>10} {'Sel':>8} {'Toxic':>8}")
    for name, data in sorted(report['filters'].items(), key=lambda item: item[1]['toxicity'], reverse=True):
        print(
            f"{name:<14} {format_pct(data['real_rate']):>10} {format_pct(data['random_rate']):>10} "
            f"{data['selectivity']:>7.3f}x {data['toxicity']:>7.3f}"
        )

    print('\nTop pares mais toxicos')
    print(f"{'Par':<28} {'Real':>10} {'Random':>10} {'Sel':>8} {'Incomp':>8} {'Toxic':>8}")
    for item in sorted(report['pairs'], key=lambda x: (x['toxicity'], x['incompatibility']), reverse=True)[:10]:
        print(
            f"{item['combo']:<28} {format_pct(item['real_rate']):>10} {format_pct(item['random_rate']):>10} "
            f"{item['selectivity']:>7.3f}x {item['incompatibility']*100:>7.2f} {item['toxicity']:>7.3f}"
        )

    print('\nTop trios mais toxicos')
    print(f"{'Trio':<40} {'Real':>10} {'Random':>10} {'Sel':>8} {'Toxic':>8}")
    for item in sorted(report['triplets'], key=lambda x: x['toxicity'], reverse=True)[:8]:
        print(
            f"{item['combo']:<40} {format_pct(item['real_rate']):>10} {format_pct(item['random_rate']):>10} "
            f"{item['selectivity']:>7.3f}x {item['toxicity']:>7.3f}"
        )

    pkg = report['package']
    print('\nPacote estrutural completo do nivel')
    print(f"Filtros estruturais: {pkg['count_filters']}")
    print(f"Preservacao real:    {format_pct(pkg['real_rate'])}")
    print(f"Passagem random:     {format_pct(pkg['random_rate'])}")
    print(f"Seletividade:        {pkg['selectivity']:.3f}x")
    print(f"Toxicidade:          {pkg['toxicity']:.3f}")


def main():
    print('=' * 78)
    print('POC — INCOMPATIBILIDADE ENTRE FILTROS DO POOL 23')
    print('=' * 78)
    print(f'Amostra random: {RANDOM_SAMPLES:,}')

    resultados = carregar_resultados()
    real_draws = [r['numeros'] for r in resultados]
    rng = np.random.default_rng(42)
    random_draws_sample = random_combos(RANDOM_SAMPLES, rng)

    level_reports = []
    for level in range(1, 7):
        report = analyze_level(level, real_draws, random_draws_sample)
        if report:
            level_reports.append(report)
            print_level_report(report)

    print('\n' + '=' * 78)
    print('RANKING GERAL — PACOTES MAIS TOXICOS')
    print('=' * 78)
    print(f"{'Nivel':<8} {'Descricao':<36} {'Real':>10} {'Random':>10} {'Sel':>8} {'Toxic':>8}")
    for report in sorted(level_reports, key=lambda x: x['package']['toxicity'], reverse=True):
        pkg = report['package']
        print(
            f"N{report['level']:<7} {report['descricao']:<36} {format_pct(pkg['real_rate']):>10} "
            f"{format_pct(pkg['random_rate']):>10} {pkg['selectivity']:>7.3f}x {pkg['toxicity']:>7.3f}"
        )

    print('\nLeitura sugerida:')
    print('- Toxicidade alta + seletividade <= 1.00x = combo que mata jackpot sem inteligência.')
    print('- Toxicidade alta + seletividade moderada = combo perigoso, só aceitável se objetivo for compressão agressiva.')
    print('- Incompatibilidade alta em pares = filtros que juntos preservam menos jackpots do que o esperado pelas taxas individuais.')


if __name__ == '__main__':
    main()