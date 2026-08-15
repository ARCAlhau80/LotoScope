#!/usr/bin/env python3
"""
PoC - Gerador com Quarentena Dinamica (Super Sete).

Duas estrategias:
1. QUARENTENA CURTA (3 concursos): evita digitos que sairam nos ultimos 3 sorteios
2. FOCO EM ATRASADOS: prioriza digitos com gap > P90 (muito atrasados)

Gera combinacoes usando ambas as estrategias separadamente e combinadas.
"""

from typing import List, Dict, Tuple, Set
from collections import Counter
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

NUM_COLUNAS = 7
DIGITOS = list(range(10))
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)
QUARENTENA_CURTA = 3


def carregar_resultados() -> List[List[int]]:
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT N1, N2, N3, N4, N5, N6, N7 FROM Resultados_SuperSete ORDER BY Concurso"
    )
    rows = cursor.fetchall()
    conn.close()
    return [[int(r[i]) for i in range(7)] for r in rows]


def calcular_gaps(sequencia: List[int], digito: int) -> Tuple[List[int], int]:
    gaps = []
    ultima_pos = None
    for i, val in enumerate(sequencia):
        if val == digito:
            if ultima_pos is not None:
                gaps.append(i - ultima_pos)
            ultima_pos = i
    gap_atual = (len(sequencia) - 1 - ultima_pos) if ultima_pos is not None else len(sequencia)
    return gaps, gap_atual


def analisar_coluna_gap(sequencia: List[int]) -> Dict[int, Dict]:
    resultado = {}
    for d in DIGITOS:
        gaps, gap_atual = calcular_gaps(sequencia, d)
        if len(gaps) < 2:
            resultado[d] = {"gap_atual": gap_atual, "p90": None, "media": None}
            continue
        arr = np.array(gaps)
        resultado[d] = {
            "gap_atual": gap_atual,
            "p90": float(np.percentile(arr, 90)),
            "media": float(np.mean(arr)),
            "sigma": float(np.std(arr)),
        }
    return resultado


def estrategia_quarentena_curta(
    resultados: List[List[int]], num_jogos: int = 10
) -> List[List[int]]:
    """
    Evita digitos que sairam nos ultimos QUARENTENA_CURTA sorteios.
    Para cada coluna, exclui os digitos recentes e escolhe aleatoriamente entre os restantes.
    """
    jogos = []
    ultimos = resultados[-QUARENTENA_CURTA:]
    
    for _ in range(num_jogos):
        jogo = []
        for col in range(NUM_COLUNAS):
            sequencia = [r[col] for r in resultados]
            recentes = set(r[col] for r in ultimos)
            disponiveis = [d for d in DIGITOS if d not in recentes]
            
            if not disponiveis:
                disponiveis = DIGITOS
            
            jogo.append(random.choice(disponiveis))
        jogos.append(jogo)
    
    return jogos


def estrategia_atrasados(
    resultados: List[List[int]], num_jogos: int = 10
) -> List[List[int]]:
    """
    Prioriza digitos com gap > P90 (muito atrasados).
    Para cada coluna, da peso maior aos atrasados.
    """
    jogos = []
    
    for _ in range(num_jogos):
        jogo = []
        for col in range(NUM_COLUNAS):
            sequencia = [r[col] for r in resultados]
            analise = analisar_coluna_gap(sequencia)
            
            pesos = []
            for d in DIGITOS:
                info = analise[d]
                if info["p90"] is None:
                    pesos.append(1.0)
                elif info["gap_atual"] > info["p90"]:
                    pesos.append(5.0)
                elif info["gap_atual"] > info["media"]:
                    pesos.append(2.0)
                else:
                    pesos.append(1.0)
            
            total = sum(pesos)
            probs = [p / total for p in pesos]
            escolhido = random.choices(DIGITOS, weights=probs, k=1)[0]
            jogo.append(escolhido)
        jogos.append(jogo)
    
    return jogos


def estrategia_combinada(
    resultados: List[List[int]], num_jogos: int = 10
) -> List[List[int]]:
    """
    Combina quarentena curta + prioridade para atrasados.
    Exclui recentes (quarentena) e prioriza atrasados (gap > P90).
    """
    jogos = []
    ultimos = resultados[-QUARENTENA_CURTA:]
    
    for _ in range(num_jogos):
        jogo = []
        for col in range(NUM_COLUNAS):
            sequencia = [r[col] for r in resultados]
            analise = analisar_coluna_gap(sequencia)
            recentes = set(r[col] for r in ultimos)
            
            disponiveis = [d for d in DIGITOS if d not in recentes]
            if not disponiveis:
                disponiveis = DIGITOS
            
            pesos = []
            for d in disponiveis:
                info = analise[d]
                if info["p90"] is None:
                    pesos.append(1.0)
                elif info["gap_atual"] > info["p90"]:
                    pesos.append(5.0)
                elif info["gap_atual"] > info["media"]:
                    pesos.append(2.0)
                else:
                    pesos.append(1.0)
            
            total = sum(pesos)
            probs = [p / total for p in pesos]
            escolhido = random.choices(disponiveis, weights=probs, k=1)[0]
            jogo.append(escolhido)
        jogos.append(jogo)
    
    return jogos


def imprimir_jogos(jogos: List[List[int]], titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")
    for i, jogo in enumerate(jogos, 1):
        nums = " ".join(f"{d}" for d in jogo)
        print(f"  Jogo {i:>2}: {nums}")
    print(f"{'='*60}")


def analisar_cobertura(jogos: List[List[int]], resultados: List[List[int]]):
    """Analisa quantos digitos de cada coluna foram cobertos pelos jogos."""
    print(f"\n  Cobertura por coluna:")
    for col in range(NUM_COLUNAS):
        digitos_usados = set(jogo[col] for jogo in jogos)
        print(f"    N{col+1}: {len(digitos_usados)}/10 digitos - {sorted(digitos_usados)}")


def main():
    if not HAS_PYODBC:
        print("ERRO: pyodbc nao instalado")
        sys.exit(1)

    print("Carregando resultados do Super Sete...")
    resultados = carregar_resultados()
    total_sorteios = len(resultados)
    print(f"Total de sorteios: {total_sorteios}")

    if total_sorteios < 30:
        print("Dados insuficientes para analise confiavel.")
        sys.exit(1)

    NUM_JOGOS = 15

    print(f"\n{'='*60}")
    print(f"  GERANDO {NUM_JOGOS} JOGOS POR ESTRATEGIA")
    print(f"{'='*60}")

    jogos_quarentena = estrategia_quarentena_curta(resultados, NUM_JOGOS)
    imprimir_jogos(jogos_quarentena, f"ESTRATEGIA 1: QUARENTENA CURTA ({QUARENTENA_CURTA} concursos)")
    analisar_cobertura(jogos_quarentena, resultados)

    jogos_atrasados = estrategia_atrasados(resultados, NUM_JOGOS)
    imprimir_jogos(jogos_atrasados, "ESTRATEGIA 2: FOCO EM ATRASADOS (gap > P90)")
    analisar_cobertura(jogos_atrasados, resultados)

    jogos_combinados = estrategia_combinada(resultados, NUM_JOGOS)
    imprimir_jogos(jogos_combinados, "ESTRATEGIA 3: COMBINADA (quarentena + atrasados)")
    analisar_cobertura(jogos_combinados, resultados)

    print(f"\n{'='*60}")
    print(f"  RESUMO DAS ESTRATEGIAS")
    print(f"{'='*60}")
    print(f"  Quarentena curta: evita digitos dos ultimos {QUARENTENA_CURTA} sorteios")
    print(f"  Atrasados: prioriza digitos com gap > P90 (muito atrasados)")
    print(f"  Combinada: quarentena + prioridade para atrasados")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
