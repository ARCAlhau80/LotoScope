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
from itertools import combinations

import numpy as np

from pool23_hub import (
    RANDOM_SAMPLES,
    carregar_resultados,
    build_filters_for_level,
    random_combos,
    pass_rate,
    toxicity_index,
    format_pct,
    FILTROS_POR_NIVEL,
    analyze_level,
)

sys.stdout.reconfigure(encoding='utf-8')


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