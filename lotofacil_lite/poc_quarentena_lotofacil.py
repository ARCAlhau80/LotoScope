#!/usr/bin/env python3
"""
PoC - Quarentena Dinamica para Lotofacil.

Diferente do Super Sete (colunas independentes), a Lotofacil tem:
- Pool de 25 numeros (1-25)
- 15 sorteados por concurso
- Ordenados por posicao (N1=menor, N15=maior)

Esta PoC analisa:
1. Gap por NUMERO (1-25): quantos sorteios desde que cada numero saiu
2. Gap por POSICAO (N1-N15) x NUMERO: qual numero esta "devendo" em qual posicao
3. Classificacao: QUARENTENA | NORMAL | ATRASADO | MUITO ATRASADO
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

NUM_POSICOES = 15
NUMEROS_POOL = list(range(1, 26))
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
        "SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 "
        "FROM Resultados_INT ORDER BY Concurso"
    )
    rows = cursor.fetchall()
    conn.close()
    return [[int(r[i]) for i in range(NUM_POSICOES)] for r in rows]


def calcular_gaps(sequencia: List[int], valor: int) -> Tuple[List[int], int]:
    gaps = []
    ultima_pos = None
    for i, val in enumerate(sequencia):
        if val == valor:
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


def analisar_gap_por_numero(resultados: List[List[int]]) -> Dict[int, Dict]:
    """Analisa gap de cada numero (1-25) independente da posicao."""
    analise = {}
    
    for num in NUMEROS_POOL:
        sequencia = []
        for r in resultados:
            sequencia.append(1 if num in r else 0)
        
        gaps = []
        ultima_aparicao = None
        for i, apareceu in enumerate(sequencia):
            if apareceu == 1:
                if ultima_aparicao is not None:
                    gaps.append(i - ultima_aparicao)
                ultima_aparicao = i
        
        gap_atual = (len(sequencia) - 1 - ultima_aparicao) if ultima_aparicao is not None else len(sequencia)
        
        if len(gaps) < 2:
            analise[num] = {
                "media": None, "mediana": None, "sigma": None,
                "p90": None, "gap_atual": gap_atual,
                "n_aparicoes": len(gaps) + (1 if gap_atual < len(sequencia) else 0),
                "status": "DADOS INSUFICIENTES",
            }
            continue
        
        arr = np.array(gaps)
        media = float(np.mean(arr))
        mediana = float(np.median(arr))
        sigma = float(np.std(arr))
        p90 = float(np.percentile(arr, 90))
        status = classificar_status(gap_atual, media, sigma, p90)
        
        analise[num] = {
            "media": media, "mediana": mediana, "sigma": sigma,
            "p90": p90, "gap_atual": gap_atual,
            "n_aparicoes": len(gaps) + 1,
            "status": status,
        }
    
    return analise


def analisar_gap_por_posicao(resultados: List[List[int]]) -> Dict[int, Dict[int, Dict]]:
    """Analisa gap de cada numero em cada posicao (N1-N15)."""
    analise = {}
    
    for pos in range(NUM_POSICOES):
        analise[pos] = {}
        sequencia = [r[pos] for r in resultados]
        
        for num in NUMEROS_POOL:
            gaps, gap_atual = calcular_gaps(sequencia, num)
            
            if len(gaps) < 2:
                analise[pos][num] = {
                    "media": None, "p90": None, "gap_atual": gap_atual,
                    "n_aparicoes": len(gaps) + (1 if gap_atual < len(sequencia) else 0),
                    "status": "DADOS INSUFICIENTES",
                }
                continue
            
            arr = np.array(gaps)
            media = float(np.mean(arr))
            sigma = float(np.std(arr))
            p90 = float(np.percentile(arr, 90))
            status = classificar_status(gap_atual, media, sigma, p90)
            
            analise[pos][num] = {
                "media": media, "p90": p90, "sigma": sigma,
                "gap_atual": gap_atual,
                "n_aparicoes": len(gaps) + 1,
                "status": status,
            }
    
    return analise


def imprimir_analise_por_numero(analise: Dict[int, Dict], total_sorteios: int):
    print(f"\n{'='*100}")
    print(f"  ANALISE DE QUARENTENA POR NUMERO (Lotofacil)")
    print(f"  Total de sorteios analisados: {total_sorteios}")
    print(f"  Fator de quarentena: {FATOR_QUARENTENA}x sigma")
    print(f"{'='*100}")
    print(f"  {'Num':>3} | {'Apar':>4} | {'Media':>6} | {'Med':>6} | {'Sigma':>6} | "
          f"{'P90':>5} | {'GapAt':>5} | {'Status':<16}")
    print(f"  {'-'*3}-+-{'-'*4}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-"
          f"{'-'*5}-+-{'-'*5}-+-{'-'*16}")
    
    for num in NUMEROS_POOL:
        info = analise[num]
        if info["media"] is None:
            print(f"  {num:>3} | {info['n_aparicoes']:>4} | {'N/A':>6} | {'N/A':>6} | {'N/A':>6} | "
                  f"{'N/A':>5} | {info['gap_atual']:>5} | {info['status']:<16}")
        else:
            print(f"  {num:>3} | {info['n_aparicoes']:>4} | {info['media']:>6.1f} | "
                  f"{info['mediana']:>6.1f} | {info['sigma']:>6.1f} | "
                  f"{info['p90']:>5.1f} | {info['gap_atual']:>5} | {info['status']:<16}")
    
    print(f"{'='*100}")


def imprimir_resumo(analise: Dict[int, Dict]):
    print(f"\n{'='*100}")
    print(f"  RESUMO DA QUARENTENA (POR NUMERO)")
    print(f"{'='*100}")
    
    quarentena = []
    atrasados = []
    muito_atrasados = []
    
    for num in NUMEROS_POOL:
        info = analise[num]
        entry = (num, info.get("gap_atual", 0), info.get("media", 0))
        if info["status"] == "QUARENTENA":
            quarentena.append(entry)
        elif info["status"] == "ATRASADO":
            atrasados.append(entry)
        elif info["status"] == "MUITO ATRASADO":
            muito_atrasados.append(entry)
    
    print(f"\n  EM QUARENTENA (sairam recentemente - evitar): {len(quarentena)}")
    for num, gap, media in sorted(quarentena, key=lambda x: x[1]):
        print(f"    Numero {num:>2}: gap={gap}, media={media:.1f}")
    
    print(f"\n  ATRASADOS (devem voltar em breve - considerar): {len(atrasados)}")
    for num, gap, media in sorted(atrasados, key=lambda x: -x[1]):
        print(f"    Numero {num:>2}: gap={gap}, media={media:.1f}")
    
    print(f"\n  MUITO ATRASADOS (acima do P90 - alta probabilidade): {len(muito_atrasados)}")
    for num, gap, media in sorted(muito_atrasados, key=lambda x: -x[1]):
        print(f"    Numero {num:>2}: gap={gap}, media={media:.1f}")
    
    print(f"{'='*100}")


def imprimir_analise_por_posicao(analise_pos: Dict[int, Dict[int, Dict]]):
    print(f"\n{'='*100}")
    print(f"  ANALISE DE QUARENTENA POR POSICAO (N1-N15)")
    print(f"  Mostrando apenas numeros com status != NORMAL")
    print(f"{'='*100}")
    
    for pos in range(NUM_POSICOES):
        print(f"\n  POSICAO N{pos+1}:")
        print(f"  {'Num':>3} | {'Apar':>4} | {'Media':>6} | {'P90':>5} | {'GapAt':>5} | {'Status':<16}")
        print(f"  {'-'*3}-+-{'-'*4}-+-{'-'*6}-+-{'-'*5}-+-{'-'*5}-+-{'-'*16}")
        
        tem_info = False
        for num in NUMEROS_POOL:
            info = analise_pos[pos][num]
            if info["status"] != "NORMAL" and info["status"] != "DADOS INSUFICIENTES":
                tem_info = True
                if info["media"] is None:
                    print(f"  {num:>3} | {info['n_aparicoes']:>4} | {'N/A':>6} | "
                          f"{'N/A':>5} | {info['gap_atual']:>5} | {info['status']:<16}")
                else:
                    print(f"  {num:>3} | {info['n_aparicoes']:>4} | {info['media']:>6.1f} | "
                          f"{info['p90']:>5.1f} | {info['gap_atual']:>5} | {info['status']:<16}")
        
        if not tem_info:
            print(f"  (todos os numeros estao NORMAL ou com dados insuficientes)")
    
    print(f"\n{'='*100}")


def imprimir_matriz_quarentena(analise_pos: Dict[int, Dict[int, Dict]]):
    print(f"\n{'='*100}")
    print(f"  MATRIZ DE QUARENTENA (Posicao x Numero)")
    print(f"  Q=QUARENTENA  N=NORMAL  A=ATRASADO  M=MUITO ATRASADO  ?=SEM DADOS")
    print(f"{'='*100}")
    
    print(f"  {'Pos':>4}", end="")
    for num in NUMEROS_POOL:
        print(f" | {num:>2}", end="")
    print()
    
    print(f"  {'-'*4}", end="")
    for _ in NUMEROS_POOL:
        print(f"-+--{'-'*2}", end="")
    print()
    
    for pos in range(NUM_POSICOES):
        print(f"  N{pos+1:>2}", end="")
        for num in NUMEROS_POOL:
            status = analise_pos[pos][num]["status"]
            simbolo = {
                "QUARENTENA": "Q", "NORMAL": ".", "ATRASADO": "A",
                "MUITO ATRASADO": "M", "DADOS INSUFICIENTES": "?"
            }.get(status, "?")
            print(f" | {simbolo:>2}", end="")
        print()
    
    print(f"{'='*100}")


def main():
    if not HAS_PYODBC:
        print("ERRO: pyodbc nao instalado")
        sys.exit(1)

    print("Carregando resultados da Lotofacil...")
    resultados = carregar_resultados()
    total_sorteios = len(resultados)
    print(f"Total de sorteios: {total_sorteios}")

    if total_sorteios < 30:
        print("Dados insuficientes para analise confiavel.")
        sys.exit(1)

    print("\n" + "="*100)
    print("  PARTE 1: ANALISE POR NUMERO (independente da posicao)")
    print("="*100)
    
    analise_numero = analisar_gap_por_numero(resultados)
    imprimir_analise_por_numero(analise_numero, total_sorteios)
    imprimir_resumo(analise_numero)

    print("\n" + "="*100)
    print("  PARTE 2: ANALISE POR POSICAO (N1-N15 x Numero)")
    print("="*100)
    
    analise_posicao = analisar_gap_por_posicao(resultados)
    imprimir_analise_por_posicao(analise_posicao)
    imprimir_matriz_quarentena(analise_posicao)

    print("\n" + "="*100)
    print("  CONCLUSAO DA POC")
    print("="*100)
    print("""
  A logica de quarentena dinamica DO Super Sete PODE ser aplicada a Lotofacil,
  mas com adaptacoes:

  1. ANALISE POR NUMERO (1-25):
     - Funciona bem, similar ao Super Sete
     - Cada numero tem seu proprio historico de gaps
     - Pode identificar numeros "quentes" (sairam recentemente) e "frios" (atrasados)

  2. ANALISE POR POSICAO (N1-N15):
     - Mais complexa, mas potencialmente mais util
     - Cada posicao tem um "perfil" diferente (N1 tende a ser baixo, N15 alto)
     - Pode identificar qual numero esta "devendo" em qual posicao
     - Exemplo: "O numero 7 nao aparece na posicao N3 ha 45 sorteios (media=20, P90=35)"

  3. VIABILIDADE:
     - Tecnicamente viavel
     - Requer mais processamento (15 posicoes x 25 numeros = 375 analises)
     - Pode ser integrada ao dashboard como nova aba "Quarentena Lotofacil"

  4. PROXIMOS PASSOS:
     - Backtest para validar se a quarentena melhora as previsoes
     - Integrar ao gerador de combinacoes da Lotofacil
     - Comparar com a estrategia atual (Poisson blend)
    """)
    print("="*100)


if __name__ == "__main__":
    main()
