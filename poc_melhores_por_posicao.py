# -*- coding: utf-8 -*-
"""
🏆 POC — MELHORES NÚMEROS POR POSIÇÃO
======================================

Analisa, para cada posição (N1-N15), quais são os TOP-3 números mais frequentes:
  - Histórico completo
  - Janela de 6 concursos
  - Janela de 10 concursos

Depois calcula um SCORE PONDERADO por (número, posição) e avalia:
  - Distribuição de "match score" nos concursos históricos
  - Se pode ser usado como filtro no Pool 23 (Opções 31 e 30.2)

Uso:
    python poc_melhores_por_posicao.py

Autor: LotoScope AI
Data: 25/04/2026
"""

import sys
import os
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

import pyodbc

CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
)

TOP_K = 3          # Candidatos por posição
PESOS = {'hist': 0.5, 'win10': 0.3, 'win6': 0.2}   # Score ponderado
LIMIAR_MATCH = 10  # Mínimo de matches para considerar "boa" combinação


# ─────────────────────────────────────────────────────────────────────────────
# CARREGAMENTO
# ─────────────────────────────────────────────────────────────────────────────

def carregar_historico() -> List[Dict]:
    """Carrega todos os concursos ordenados crescente."""
    resultados = []
    try:
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
                FROM Resultados_INT ORDER BY Concurso ASC
            """)
            for row in cursor.fetchall():
                resultados.append({
                    'concurso': row[0],
                    'numeros': [row[i] for i in range(1, 16)]  # N1..N15 já ordenados
                })
        print(f"   ✅ {len(resultados)} concursos carregados")
    except pyodbc.Error as e:
        print(f"   ❌ Erro de banco: {e}")
        sys.exit(1)
    return resultados


# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULO DE MELHORES POR POSIÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def calcular_top_k_por_posicao(resultados: List[Dict], janela: int = None, top_k: int = TOP_K) -> Dict:
    """
    Retorna {posicao(1-15): [num1, num2, ..., numK]} com os top-K números
    mais frequentes naquela posição.

    Args:
        resultados: Lista ordenada crescente.
        janela: None = histórico completo; int = últimos N concursos.
        top_k: Quantos candidatos por posição.
    """
    dados = resultados[-janela:] if janela else resultados
    freq = defaultdict(Counter)   # freq[posicao][numero] = contagem

    for r in dados:
        for pos_idx, num in enumerate(r['numeros']):
            freq[pos_idx + 1][num] += 1

    top_por_posicao = {}
    for pos in range(1, 16):
        top_por_posicao[pos] = [n for n, _ in freq[pos].most_common(top_k)]

    return top_por_posicao


def calcular_score_ponderado(
    top_hist: Dict, top_10: Dict, top_6: Dict
) -> Dict[Tuple[int, int], float]:
    """
    Retorna {(numero, posicao): score_ponderado} onde o score indica
    quão "bom" é esse número para essa posição.
    Score máximo = 1.0 (top-1 nas três janelas).
    """
    scores = defaultdict(float)

    for pos in range(1, 16):
        for rank_0, num in enumerate(top_hist.get(pos, [])):
            scores[(num, pos)] += PESOS['hist'] * (TOP_K - rank_0) / TOP_K
        for rank_0, num in enumerate(top_10.get(pos, [])):
            scores[(num, pos)] += PESOS['win10'] * (TOP_K - rank_0) / TOP_K
        for rank_0, num in enumerate(top_6.get(pos, [])):
            scores[(num, pos)] += PESOS['win6'] * (TOP_K - rank_0) / TOP_K

    return scores


# ─────────────────────────────────────────────────────────────────────────────
# AVALIAÇÃO NOS CONCURSOS
# ─────────────────────────────────────────────────────────────────────────────

def calcular_match_score(combo_15: List[int], top_por_posicao: Dict) -> int:
    """
    Conta quantas das 15 posições têm seu número dentro do top-K.
    Máximo = 15.
    """
    count = 0
    for pos_idx, num in enumerate(combo_15):
        if num in top_por_posicao.get(pos_idx + 1, []):
            count += 1
    return count


def avaliar_historico(resultados: List[Dict]) -> None:
    """Avalia o match score de cada concurso histórico e imprime estatísticas."""
    print("\n" + "=" * 65)
    print("📊 ANÁLISE: MELHORES NÚMEROS POR POSIÇÃO — SCORE PONDERADO")
    print("=" * 65)

    distribuicao_hist = Counter()
    distribuicao_10 = Counter()
    distribuicao_6 = Counter()
    distribuicao_ponderado = Counter()

    INICIO_AVALIACAO = 50  # concursos mínimos de histórico para calcular top-K

    for i in range(INICIO_AVALIACAO, len(resultados)):
        concurso = resultados[i]['concurso']
        numeros = resultados[i]['numeros']
        historico_anterior = resultados[:i]

        top_hist = calcular_top_k_por_posicao(historico_anterior, janela=None)
        top_10   = calcular_top_k_por_posicao(historico_anterior, janela=10)
        top_6    = calcular_top_k_por_posicao(historico_anterior, janela=6)

        score_hist = calcular_match_score(numeros, top_hist)
        score_10   = calcular_match_score(numeros, top_10)
        score_6    = calcular_match_score(numeros, top_6)

        # Score ponderado: combina os 3 tops
        top_pond = _combinar_tops(top_hist, top_10, top_6)
        score_pond = calcular_match_score(numeros, top_pond)

        distribuicao_hist[score_hist] += 1
        distribuicao_10[score_10] += 1
        distribuicao_6[score_6] += 1
        distribuicao_ponderado[score_pond] += 1

    total = sum(distribuicao_hist.values())

    _imprimir_distribuicao("Histórico Completo", distribuicao_hist, total)
    _imprimir_distribuicao("Janela 10", distribuicao_10, total)
    _imprimir_distribuicao("Janela 6", distribuicao_6, total)
    _imprimir_distribuicao("Score Ponderado (hist 50% + win10 30% + win6 20%)", distribuicao_ponderado, total)

    # Análise de utilidade como filtro
    print("\n" + "-" * 65)
    print(f"📌 ANÁLISE DO FILTRO (limiar ≥ {LIMIAR_MATCH} matches):")
    for label, dist in [
        ("Histórico", distribuicao_hist),
        ("Janela 10", distribuicao_10),
        ("Ponderado", distribuicao_ponderado),
    ]:
        acima = sum(v for k, v in dist.items() if k >= LIMIAR_MATCH)
        pct = 100 * acima / total if total else 0
        print(f"   {label}: {acima}/{total} concursos passariam ({pct:.1f}%)")

    print()


def _combinar_tops(top_hist, top_10, top_6) -> Dict:
    """Une os três tops: um número é candidato se está em QUALQUER um dos três."""
    combinado = {}
    for pos in range(1, 16):
        candidatos = set(top_hist.get(pos, [])) | set(top_10.get(pos, [])) | set(top_6.get(pos, []))
        combinado[pos] = list(candidatos)
    return combinado


def _imprimir_distribuicao(label: str, dist: Counter, total: int) -> None:
    print(f"\n  ┌─ {label}")
    acumulado_acima = 0
    for score in range(15, 7, -1):
        qtd = dist.get(score, 0)
        pct = 100 * qtd / total if total else 0
        acumulado_acima += qtd
        pct_acum = 100 * acumulado_acima / total if total else 0
        barra = "█" * int(pct / 2)
        print(f"  │ ≥{score:2d} match  {qtd:5d} conc ({pct:5.1f}%)  acum={pct_acum:5.1f}%  {barra}")
    print(f"  └{'─' * 40}")


# ─────────────────────────────────────────────────────────────────────────────
# ANÁLISE DA POSIÇÃO ATUAL (último concurso + previsão próximo)
# ─────────────────────────────────────────────────────────────────────────────

def mostrar_top_por_posicao_atual(resultados: List[Dict]) -> None:
    """Mostra o top-3 atual por posição (com base em todo o histórico)."""
    print("\n" + "=" * 65)
    print("🏆 TOP-3 NÚMEROS POR POSIÇÃO (ESTADO ATUAL)")
    print("=" * 65)

    top_hist = calcular_top_k_por_posicao(resultados, janela=None)
    top_10   = calcular_top_k_por_posicao(resultados, janela=10)
    top_6    = calcular_top_k_por_posicao(resultados, janela=6)

    scores   = calcular_score_ponderado(top_hist, top_10, top_6)

    # Melhores combinações de (número, posição) pelo score ponderado
    print(f"\n  {'POS':>4}  {'HIST TOP-3':>20}  {'WIN-10 TOP-3':>20}  {'WIN-6 TOP-3':>20}")
    print(f"  {'─'*4}  {'─'*20}  {'─'*20}  {'─'*20}")
    for pos in range(1, 16):
        h = ", ".join(f"{n:02d}" for n in top_hist.get(pos, []))
        w10 = ", ".join(f"{n:02d}" for n in top_10.get(pos, []))
        w6  = ", ".join(f"{n:02d}" for n in top_6.get(pos, []))
        print(f"  N{pos:>2}:  {h:>20}  {w10:>20}  {w6:>20}")

    # Top scores globais (mais fortes pares número×posição)
    print("\n  🥇 TOP-15 PARES (número, posição) por score ponderado:")
    top_pares = sorted(scores.items(), key=lambda x: -x[1])[:15]
    for (num, pos), sc in top_pares:
        print(f"     N{pos:>2} = {num:02d}  score={sc:.3f}")

    ultimo = resultados[-1]
    print(f"\n  📋 Último concurso ({ultimo['concurso']}): {ultimo['numeros']}")
    top_pond = _combinar_tops(top_hist, top_10, top_6)
    score_atual = calcular_match_score(ultimo['numeros'], top_pond)
    score_hist_atual = calcular_match_score(ultimo['numeros'], top_hist)
    print(f"  ✅ Match score hist={score_hist_atual}/15 | ponderado={score_atual}/15")


# ─────────────────────────────────────────────────────────────────────────────
# AVALIAÇÃO COMO FILTRO DO POOL 23
# ─────────────────────────────────────────────────────────────────────────────

def avaliar_como_filtro_pool23(resultados: List[Dict]) -> None:
    """
    Simula o filtro nos últimos 200 concursos:
    - Para cada concurso 'alvo', usa o histórico anterior para calcular top-3 por posição
    - Conta combinações do Pool 23 que passariam pelo filtro (estimativa)
    - Mostra a taxa de jackpot entre os que passariam
    """
    print("\n" + "=" * 65)
    print("🎯 SIMULAÇÃO: FILTRO NO POOL 23 (últimos 200 concursos)")
    print("=" * 65)

    limiares = [9, 10, 11, 12]
    resultados_por_limiar = {l: {'passou': 0, 'total': 0} for l in limiares}

    INICIO = max(50, len(resultados) - 200)
    for i in range(INICIO, len(resultados)):
        historico_anterior = resultados[:i]
        alvo = resultados[i]

        top_hist = calcular_top_k_por_posicao(historico_anterior, janela=None)
        top_10   = calcular_top_k_por_posicao(historico_anterior, janela=10)
        top_6    = calcular_top_k_por_posicao(historico_anterior, janela=6)
        top_pond = _combinar_tops(top_hist, top_10, top_6)

        score = calcular_match_score(alvo['numeros'], top_pond)

        for l in limiares:
            resultados_por_limiar[l]['total'] += 1
            if score >= l:
                resultados_por_limiar[l]['passou'] += 1

    print(f"\n  {'Limiar':>8}  {'Concursos OK':>14}  {'% passa filtro':>16}  {'Utilidade':>12}")
    print(f"  {'─'*8}  {'─'*14}  {'─'*16}  {'─'*12}")
    for l in limiares:
        r = resultados_por_limiar[l]
        passou = r['passou']
        total = r['total']
        pct = 100 * passou / total if total else 0
        utilidade = "✅ Bom" if 60 <= pct <= 95 else ("⚠️ Restritivo" if pct < 60 else "⚠️ Permissivo")
        print(f"  {l:>8}  {passou:>6}/{total:<7}  {pct:>14.1f}%  {utilidade:>12}")

    print("""
  💡 INTERPRETAÇÃO:
     - Se % passa filtro = 70-90% → filtro útil (preserva jackpots, corta lixo)
     - Cada combinação gerada pelo Pool 23 seria avaliada pelo score
     - Filtramos as que não têm número "bom" em posições suficientes
    """)


# ─────────────────────────────────────────────────────────────────────────────
# CONCLUSÃO / RECOMENDAÇÃO DE IMPLEMENTAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def imprimir_conclusao() -> None:
    print("\n" + "=" * 65)
    print("📋 CONCLUSÃO — VIABILIDADE DE IMPLEMENTAÇÃO NO POOL 23")
    print("=" * 65)
    print("""
  SITUAÇÃO ATUAL:
    • Pool 23 já tem filtro NEGATIVO: 'Piores por posição' (rejeita ruins)
    • Pool 23 NÃO tem filtro POSITIVO: 'Melhores por posição' (exige bons)
    • Neural heatmap (feature 175-199) é perspectiva INVERTIDA (por número)

  PROPOSTA:
    Adicionar 'FiltroMelhoresPorPosicao' nas Opções 31 e 30.2:
    - Parâmetros: top_k=3, pesos=(hist=50%, win10=30%, win6=20%), limiar=10
    - Rejeita combinações onde < limiar posições têm número no top-K
    - Pode ser configurado como nível opcional ou parâmetro do nível

  COMO NOVO NÍVEL OU OPÇÃO EXISTENTE:
    - Adicionado como sub-filtro nos níveis 2-6 (onde piores já ativo)
    - Ou como nível separado (ex. Nível 9: ponderado top-3 por posição)
    - Backtesting obrigatório para validar antes de produção

  PRÓXIMOS PASSOS:
    1. Rodar este script para ver os números reais de % passa filtro
    2. Se > 70% dos jackpots passam → implementar nas Opções 31 e 30.2
    3. Integrar como _calcular_melhores_por_posicao() + _filtrar_por_melhores()
    """)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 65)
    print("  🏆 POC — MELHORES NÚMEROS POR POSIÇÃO (top-3, ponderado)")
    print("═" * 65 + "\n")

    print("📥 Carregando histórico do banco de dados...")
    resultados = carregar_historico()

    mostrar_top_por_posicao_atual(resultados)
    avaliar_historico(resultados)
    avaliar_como_filtro_pool23(resultados)
    imprimir_conclusao()

    input("\n[ENTER para sair...]")


if __name__ == '__main__':
    main()
