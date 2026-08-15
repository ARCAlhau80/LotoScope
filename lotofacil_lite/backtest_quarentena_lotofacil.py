#!/usr/bin/env python3
"""
Backtest robusto: Poisson Blend vs Quarentena por Posição (Lotofácil)

Compara 3 estratégias:
1. Poisson Blend (atual)
2. Quarentena por Posição (evita números que saíram recentemente em cada posição)
3. Combinada (Poisson + Quarentena)

Métricas:
- Taxa de acerto por posição (N1-N15)
- Taxa de acerto global (quantos dos 15 números acertou)
- Distribuição de acertos
"""

import sys
from pathlib import Path
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

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


def calcular_lambda_blend_por_posicao(
    resultados: List[List[int]], 
    janela: int = 30,
    alpha: float = 0.6
) -> Dict[int, Dict[int, float]]:
    """Calcula lambda blend para cada posição x número."""
    lambdas = {}
    total = len(resultados)
    
    for pos in range(NUM_POSICOES):
        lambdas[pos] = {}
        seq = [r[pos] for r in resultados]
        
        for num in NUMEROS_POOL:
            freq_total = seq.count(num) / total if total > 0 else 0
            freq_recente = seq[-janela:].count(num) / janela if janela > 0 else 0
            lambdas[pos][num] = alpha * freq_total + (1 - alpha) * freq_recente
    
    return lambdas


def calcular_quarentena_por_posicao(
    resultados: List[List[int]],
    fator_quarentena: float = 0.35
) -> Dict[int, Dict[int, Dict]]:
    """Calcula status de quarentena para cada posição x número."""
    quarentena = {}
    
    for pos in range(NUM_POSICOES):
        quarentena[pos] = {}
        seq = [r[pos] for r in resultados]
        
        for num in NUMEROS_POOL:
            gaps = []
            ultima_pos = None
            for i, val in enumerate(seq):
                if val == num:
                    if ultima_pos is not None:
                        gaps.append(i - ultima_pos)
                    ultima_pos = i
            
            gap_atual = (len(seq) - 1 - ultima_pos) if ultima_pos is not None else len(seq)
            
            if len(gaps) < 2:
                quarentena[pos][num] = {
                    "gap_atual": gap_atual,
                    "media": 0.0,
                    "p90": 0.0,
                    "sigma": 0.0,
                    "status": "normal"
                }
                continue
            
            arr = np.array(gaps)
            media = float(np.mean(arr))
            sigma = float(np.std(arr))
            p90 = float(np.percentile(arr, 90))
            
            if gap_atual <= 3:
                status = "quarentena"
            elif gap_atual > p90:
                status = "muito_atrasado"
            elif gap_atual > media + fator_quarentena * sigma:
                status = "atrasado"
            else:
                status = "normal"
            
            quarentena[pos][num] = {
                "gap_atual": gap_atual,
                "media": media,
                "p90": p90,
                "sigma": sigma,
                "status": status
            }
    
    return quarentena


def estrategia_poisson_blend(
    lambdas: Dict[int, Dict[int, float]],
    top_k: int = 3
) -> List[List[int]]:
    """Retorna top_k números por posição baseado em lambda blend."""
    palpites = []
    for pos in range(NUM_POSICOES):
        ranked = sorted(lambdas[pos].items(), key=lambda x: x[1], reverse=True)
        palpites.append([num for num, _ in ranked[:top_k]])
    return palpites


def estrategia_quarentena(
    lambdas: Dict[int, Dict[int, float]],
    quarentena: Dict[int, Dict[int, Dict]],
    top_k: int = 3
) -> List[List[int]]:
    """Retorna top_k números por posição, priorizando atrasados e evitando quarentena."""
    palpites = []
    
    for pos in range(NUM_POSICOES):
        candidatos = []
        for num in NUMEROS_POOL:
            q_info = quarentena[pos][num]
            
            if not isinstance(q_info, dict):
                q_info = {"status": "normal"}
            
            lambda_val = lambdas[pos][num]
            
            if q_info["status"] == "quarentena":
                score = lambda_val * 0.85
            elif q_info["status"] == "muito_atrasado":
                score = lambda_val * 1.25
            elif q_info["status"] == "atrasado":
                score = lambda_val * 1.10
            else:
                score = lambda_val
            
            candidatos.append((num, score))
        
        ranked = sorted(candidatos, key=lambda x: x[1], reverse=True)
        palpites.append([num for num, _ in ranked[:top_k]])
    
    return palpites


def estrategia_combinada(
    lambdas: Dict[int, Dict[int, float]],
    quarentena: Dict[int, Dict[int, Dict]],
    top_k: int = 3
) -> List[List[int]]:
    """Combina Poisson blend com quarentena (pesos mais suaves)."""
    palpites = []
    
    for pos in range(NUM_POSICOES):
        candidatos = []
        for num in NUMEROS_POOL:
            lambda_val = lambdas[pos][num]
            q_info = quarentena[pos][num]
            
            if not isinstance(q_info, dict):
                q_info = {"status": "normal"}
            
            score = lambda_val
            
            if q_info["status"] == "quarentena":
                score *= 0.85
            elif q_info["status"] == "muito_atrasado":
                score *= 1.25
            elif q_info["status"] == "atrasado":
                score *= 1.10
            
            candidatos.append((num, score))
        
        ranked = sorted(candidatos, key=lambda x: x[1], reverse=True)
        palpites.append([num for num, _ in ranked[:top_k]])
    
    return palpites


def backtest_estrategia(
    resultados: List[List[int]],
    estrategia_fn,
    janela_treino: int = 100,
    janela_teste: int = 50,
    top_k: int = 3
) -> Dict:
    """
    Backtest sliding window.
    Treina nos últimos `janela_treino` sorteios, testa nos próximos `janela_teste`.
    """
    total = len(resultados)
    resultados_teste = []
    
    for i in range(janela_treino, total - janela_teste, janela_teste):
        treino = resultados[i - janela_treino:i]
        teste = resultados[i:i + janela_teste]
        
        lambdas = calcular_lambda_blend_por_posicao(treino, janela=30)
        quarentena = calcular_quarentena_por_posicao(treino)
        
        if estrategia_fn == estrategia_poisson_blend:
            palpites = estrategia_fn(lambdas, top_k)
        else:
            palpites = estrategia_fn(lambdas, quarentena, top_k)
        
        for sorteio_real in teste:
            acertos_por_posicao = []
            for pos in range(NUM_POSICOES):
                if sorteio_real[pos] in palpites[pos]:
                    acertos_por_posicao.append(1)
                else:
                    acertos_por_posicao.append(0)
            
            resultados_teste.append({
                "sorteio": sorteio_real,
                "palpites": palpites,
                "acertos_por_posicao": acertos_por_posicao,
                "total_acertos": sum(acertos_por_posicao)
            })
    
    return resultados_teste


def calcular_metricas(resultados: List[Dict]) -> Dict:
    """Calcula métricas agregadas."""
    total_testes = len(resultados)
    
    acertos_por_posicao = defaultdict(list)
    total_acertos = []
    
    for r in resultados:
        for pos in range(NUM_POSICOES):
            acertos_por_posicao[pos].append(r["acertos_por_posicao"][pos])
        total_acertos.append(r["total_acertos"])
    
    metricas = {
        "total_testes": total_testes,
        "media_acertos": np.mean(total_acertos),
        "mediana_acertos": np.median(total_acertos),
        "max_acertos": max(total_acertos),
        "min_acertos": min(total_acertos),
        "acertos_por_posicao": {
            pos: {
                "taxa": np.mean(vals),
                "total": sum(vals),
                "count": len(vals)
            }
            for pos, vals in acertos_por_posicao.items()
        }
    }
    
    return metricas


def imprimir_comparacao(metricas: Dict[str, Dict]):
    """Imprime comparação entre estratégias."""
    print("\n" + "="*100)
    print("  COMPARAÇÃO DE ESTRATÉGIAS - BACKTEST LOTOFÁCIL")
    print("="*100)
    
    for nome, m in metricas.items():
        print(f"\n  {nome}:")
        print(f"    Total de testes: {m['total_testes']}")
        print(f"    Média de acertos: {m['media_acertos']:.2f} / 15")
        print(f"    Mediana: {m['mediana_acertos']:.1f}")
        print(f"    Max: {m['max_acertos']} | Min: {m['min_acertos']}")
        
        print(f"\n    Taxa de acerto por posição:")
        for pos in range(NUM_POSICOES):
            taxa = m['acertos_por_posicao'][pos]['taxa']
            print(f"      N{pos+1:2d}: {taxa*100:5.1f}%")


def main():
    if not HAS_PYODBC:
        print("ERRO: pyodbc não instalado")
        sys.exit(1)
    
    print("Carregando resultados da Lotofácil...")
    resultados = carregar_resultados()
    print(f"Total de sorteios: {len(resultados)}")
    
    print("\nExecutando backtest...")
    print("  Janela de treino: 100 sorteios")
    print("  Janela de teste: 50 sorteios")
    print("  Top-K: 3 números por posição")
    
    metricas = {}
    
    print("\n1/3 - Testando Poisson Blend...")
    resultados_poisson = backtest_estrategia(
        resultados,
        estrategia_poisson_blend,
        janela_treino=100,
        janela_teste=50,
        top_k=3
    )
    metricas["Poisson Blend (atual)"] = calcular_metricas(resultados_poisson)
    
    print("2/3 - Testando Quarentena por Posição...")
    resultados_quarentena = backtest_estrategia(
        resultados,
        estrategia_quarentena,
        janela_treino=100,
        janela_teste=50,
        top_k=3
    )
    metricas["Quarentena por Posição"] = calcular_metricas(resultados_quarentena)
    
    print("3/3 - Testando Estratégia Combinada...")
    resultados_combinada = backtest_estrategia(
        resultados,
        estrategia_combinada,
        janela_treino=100,
        janela_teste=50,
        top_k=3
    )
    metricas["Combinada (Poisson + Quarentena)"] = calcular_metricas(resultados_combinada)
    
    imprimir_comparacao(metricas)
    
    print("\n" + "="*100)
    print("  CONCLUSÃO")
    print("="*100)
    
    melhor = max(metricas.items(), key=lambda x: x[1]['media_acertos'])
    print(f"\n  Melhor estratégia: {melhor[0]}")
    print(f"  Média de acertos: {melhor[1]['media_acertos']:.2f} / 15")
    
    diff = melhor[1]['media_acertos'] - metricas["Poisson Blend (atual)"]['media_acertos']
    if diff > 0:
        print(f"  Melhoria vs Poisson: +{diff:.2f} acertos ({diff/15*100:.1f}%)")
    else:
        print(f"  Diferença vs Poisson: {diff:.2f} acertos")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    main()
