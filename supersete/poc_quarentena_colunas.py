#!/usr/bin/env python3
"""
PoC - Analise de Quarentena Dinamica por Coluna e Numero (Super Sete).

Para cada coluna (N1-N7) e cada digito (0-9), calcula:
- Gap medio (sorteios entre aparicoes consecutivas)
- Gap atual (sorteios desde a ultima aparicao)
- Desvio padrao, mediana, percentis
- Status de quarentena: QUARENTENA | NORMAL | ATRASADO | MUITO ATRASADO

A quarentena dinamica funciona assim:
  - Se gap_atual < media - fator * sigma => QUARENTENA (saiu recentemente)
  - Se gap_atual > media + fator * sigma => ATRASADO (deve voltar em breve)
  - Se gap_atual > P90 => MUITO ATRASADO
"""

from typing import List, Dict, Tuple
from collections import defaultdict
import sys
from pathlib import Path

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
FATOR_QUARENTENA = 0.5


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


def classificar_status(gap_atual: float, media: float, sigma: float, p90: float) -> str:
    if gap_atual < media - FATOR_QUARENTENA * sigma:
        return "QUARENTENA"
    elif gap_atual > p90:
        return "MUITO ATRASADO"
    elif gap_atual > media + FATOR_QUARENTENA * sigma:
        return "ATRASADO"
    else:
        return "NORMAL"


def analisar_coluna(sequencia: List[int], col_idx: int) -> Dict[int, Dict]:
    resultado = {}
    for d in DIGITOS:
        gaps, gap_atual = calcular_gaps(sequencia, d)
        if len(gaps) < 2:
            resultado[d] = {
                "media": None, "mediana": None, "sigma": None,
                "p25": None, "p75": None, "p90": None,
                "min": None, "max": None,
                "gap_atual": gap_atual, "n_aparicoes": gaps.__len__() + (1 if gap_atual < len(sequencia) else 0),
                "status": "DADOS INSUFICIENTES",
            }
            continue
        arr = np.array(gaps)
        media = float(np.mean(arr))
        mediana = float(np.median(arr))
        sigma = float(np.std(arr))
        p25 = float(np.percentile(arr, 25))
        p75 = float(np.percentile(arr, 75))
        p90 = float(np.percentile(arr, 90))
        minimo = int(np.min(arr))
        maximo = int(np.max(arr))
        status = classificar_status(gap_atual, media, sigma, p90)
        resultado[d] = {
            "media": media, "mediana": mediana, "sigma": sigma,
            "p25": p25, "p75": p75, "p90": p90,
            "min": minimo, "max": maximo,
            "gap_atual": gap_atual, "n_aparicoes": len(gaps) + 1,
            "status": status,
        }
    return resultado


def imprimir_tabela(analise: Dict[int, Dict[int, Dict]], total_sorteios: int):
    print(f"\n{'='*100}")
    print(f"  ANALISE DE QUARENTENA DINAMICA - SUPER SETE")
    print(f"  Total de sorteios analisados: {total_sorteios}")
    print(f"  Fator de quarentena: {FATOR_QUARENTENA}x sigma")
    print(f"{'='*100}")

    for col in range(NUM_COLUNAS):
        print(f"\n{'-'*100}")
        print(f"  COLUNA {col+1} (N{col+1})")
        print(f"{'-'*100}")
        print(f"  {'Dig':>3} | {'Apar':>4} | {'Media':>6} | {'Med':>6} | {'Sigma':>6} | "
              f"{'P25':>5} | {'P75':>5} | {'P90':>5} | {'Min':>4} | {'Max':>4} | "
              f"{'GapAt':>5} | {'Status':<16}")
        print(f"  {'-'*3}-+-{'-'*4}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-"
              f"{'-'*5}-+-{'-'*5}-+-{'-'*5}-+-{'-'*4}-+-{'-'*4}-+-"
              f"{'-'*5}-+-{'-'*16}")

        dados_col = analise[col]
        for d in DIGITOS:
            info = dados_col[d]
            if info["media"] is None:
                print(f"  {d:>3} | {info['n_aparicoes']:>4} | {'N/A':>6} | {'N/A':>6} | {'N/A':>6} | "
                      f"{'N/A':>5} | {'N/A':>5} | {'N/A':>5} | {'N/A':>4} | {'N/A':>4} | "
                      f"{info['gap_atual']:>5} | {info['status']:<16}")
            else:
                print(f"  {d:>3} | {info['n_aparicoes']:>4} | {info['media']:>6.1f} | "
                      f"{info['mediana']:>6.1f} | {info['sigma']:>6.1f} | "
                      f"{info['p25']:>5.1f} | {info['p75']:>5.1f} | {info['p90']:>5.1f} | "
                      f"{info['min']:>4} | {info['max']:>4} | "
                      f"{info['gap_atual']:>5} | {info['status']:<16}")

    print(f"\n{'='*100}")


def imprimir_resumo_quarentena(analise: Dict[int, Dict[int, Dict]]):
    print(f"\n{'='*100}")
    print(f"  RESUMO DA QUARENTENA DINAMICA")
    print(f"{'='*100}")

    quarentena = []
    atrasados = []
    muito_atrasados = []

    for col in range(NUM_COLUNAS):
        for d in DIGITOS:
            info = analise[col][d]
            entry = (col + 1, d, info.get("gap_atual", 0), info.get("media", 0))
            if info["status"] == "QUARENTENA":
                quarentena.append(entry)
            elif info["status"] == "ATRASADO":
                atrasados.append(entry)
            elif info["status"] == "MUITO ATRASADO":
                muito_atrasados.append(entry)

    print(f"\n  EM QUARENTENA (sairam recentemente - evitar):")
    print(f"  {'Coluna':>6} | {'Digito':>6} | {'Gap Atual':>9} | {'Media':>6}")
    print(f"  {'-'*6}-+-{'-'*6}-+-{'-'*9}-+-{'-'*6}")
    for col, dig, gap, media in sorted(quarentena, key=lambda x: x[2]):
        print(f"  N{col:<5} | {dig:>6} | {gap:>9} | {media:>6.1f}")

    print(f"\n  ATRASADOS (devem voltar em breve - considerar):")
    print(f"  {'Coluna':>6} | {'Digito':>6} | {'Gap Atual':>9} | {'Media':>6}")
    print(f"  {'-'*6}-+-{'-'*6}-+-{'-'*9}-+-{'-'*6}")
    for col, dig, gap, media in sorted(atrasados, key=lambda x: -x[2]):
        print(f"  N{col:<5} | {dig:>6} | {gap:>9} | {media:>6.1f}")

    print(f"\n  MUITO ATRASADOS (acima do P90 - alta probabilidade):")
    print(f"  {'Coluna':>6} | {'Digito':>6} | {'Gap Atual':>9} | {'Media':>6}")
    print(f"  {'-'*6}-+-{'-'*6}-+-{'-'*9}-+-{'-'*6}")
    for col, dig, gap, media in sorted(muito_atrasados, key=lambda x: -x[2]):
        print(f"  N{col:<5} | {dig:>6} | {gap:>9} | {media:>6.1f}")

    print(f"\n  Total em quarentena: {len(quarentena)}")
    print(f"  Total atrasados: {len(atrasados)}")
    print(f"  Total muito atrasados: {len(muito_atrasados)}")
    print(f"{'='*100}")


def imprimir_matriz_quarentena(analise: Dict[int, Dict[int, Dict]]):
    print(f"\n{'='*60}")
    print(f"  MATRIZ DE QUARENTENA (Coluna x Digito)")
    print(f"  Q=QUARENTENA  N=NORMAL  A=ATRASADO  M=MUITO ATRASADO")
    print(f"{'='*60}")
    print(f"  {'':>4}", end="")
    for col in range(NUM_COLUNAS):
        print(f" | N{col+1:>2}", end="")
    print()
    print(f"  {'-'*4}", end="")
    for _ in range(NUM_COLUNAS):
        print(f"-+--{'-'*3}", end="")
    print()
    for d in DIGITOS:
        print(f"  {d:>4}", end="")
        for col in range(NUM_COLUNAS):
            status = analise[col][d]["status"]
            simbolo = {"QUARENTENA": " Q ", "NORMAL": " N ", "ATRASADO": " A ", "MUITO ATRASADO": " M "}.get(status, " ? ")
            print(f" | {simbolo}", end="")
        print()
    print(f"{'='*60}")


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

    analise = {}
    for col in range(NUM_COLUNAS):
        sequencia = [r[col] for r in resultados]
        analise[col] = analisar_coluna(sequencia, col)

    imprimir_tabela(analise, total_sorteios)
    imprimir_resumo_quarentena(analise)
    imprimir_matriz_quarentena(analise)


if __name__ == "__main__":
    main()
