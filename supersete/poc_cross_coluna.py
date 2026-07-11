#!/usr/bin/env python3
"""
PoC: Análise de Correlação QMF Cross-Coluna no Super Sete

Objetivo:
1. Verificar se dígitos quentes em múltiplas colunas têm maior probabilidade de sair
2. Verificar se dígitos frios em múltiplas colunas têm menor probabilidade
3. Avaliar se um "pool global" (top dígitos) melhora a geração
4. Comparar estratégias de geração com e sem análise cross-coluna

Metodologia:
- Para cada sorteio histórico, calcular QMF por coluna usando janela móvel
- Classificar cada dígito pelo "score cross-coluna" (quantas colunas é quente - quantas é frio)
- Verificar se há correlação entre score e probabilidade de sair no próximo sorteio
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False
    print("⚠️  pyodbc não disponível - usando dados mock")

NUM_COLUNAS = 7
DIGITOS = list(range(10))
JANELA_QMF = 30
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)


def carregar_resultados() -> List[List[int]]:
    if not HAS_PYODBC:
        return []
    
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT N1, N2, N3, N4, N5, N6, N7 "
            "FROM Resultados_SuperSete ORDER BY Concurso"
        )
        rows = cursor.fetchall()
        conn.close()
        return [[int(r[i]) for i in range(7)] for r in rows]
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return []


def calcular_qmf_por_coluna(
    historico: List[List[int]],
    janela: int = JANELA_QMF
) -> Tuple[Dict[int, List[int]], Dict[int, List[int]], Dict[int, List[int]]]:
    """
    Calcula QMF por coluna usando os últimos `janela` sorteios.
    
    Returns:
        - quentes: {col: [digitos quentes]}
        - mornos: {col: [digitos mornos]}
        - frios: {col: [digitos frios]}
    """
    recentes = historico[-janela:] if len(historico) >= janela else historico
    
    freq: Dict[int, Dict[int, int]] = {col: {d: 0 for d in DIGITOS} for col in range(NUM_COLUNAS)}
    
    for nums in recentes:
        for col in range(NUM_COLUNAS):
            if col < len(nums):
                d = nums[col]
                if 0 <= d <= 9:
                    freq[col][d] += 1
    
    quentes: Dict[int, List[int]] = {}
    mornos: Dict[int, List[int]] = {}
    frios: Dict[int, List[int]] = {}
    
    for col in range(NUM_COLUNAS):
        ranked = sorted(DIGITOS, key=lambda d: freq[col][d], reverse=True)
        quentes[col] = ranked[:3]
        frios[col] = ranked[-3:]
        mornos[col] = [d for d in DIGITOS if d not in quentes[col] and d not in frios[col]]
    
    return quentes, mornos, frios


def calcular_score_cross_coluna(
    quentes: Dict[int, List[int]],
    frios: Dict[int, List[int]]
) -> Dict[int, int]:
    """
    Calcula o "score cross-coluna" de cada dígito.
    
    Score = (quantas colunas é quente) - (quantas colunas é frio)
    
    Exemplo:
    - Dígito 2 é quente em N1, N2, N3 (3 colunas) e frio em N5 (1 coluna)
    - Score = 3 - 1 = 2 (positivo = tende a sair mais)
    """
    scores: Dict[int, int] = {d: 0 for d in DIGITOS}
    
    for d in DIGITOS:
        hot_count = sum(1 for col in range(NUM_COLUNAS) if d in quentes[col])
        cold_count = sum(1 for col in range(NUM_COLUNAS) if d in frios[col])
        scores[d] = hot_count - cold_count
    
    return scores


def analisar_correlacao_score_saida(resultados: List[List[int]]) -> Dict:
    """
    Para cada sorteio, calcula o score cross-coluna ANTES do sorteio
    e verifica se dígitos com score alto têm maior probabilidade de sair.
    
    Mede: de todos os dígitos com score X em todas as colunas, qual % realmente saiu?
    """
    print("\n📊 Analisando correlação entre score cross-coluna e probabilidade de saída...")
    
    saiu_por_score: Dict[int, int] = defaultdict(int)
    total_por_score: Dict[int, int] = defaultdict(int)
    
    for i in range(JANELA_QMF, len(resultados)):
        historico = resultados[:i]
        sorteio_atual = resultados[i]
        
        quentes, _, frios = calcular_qmf_por_coluna(historico)
        scores = calcular_score_cross_coluna(quentes, frios)
        
        sorteados_set = set(sorteio_atual)
        
        for d in DIGITOS:
            score = scores[d]
            total_por_score[score] += 1
            if d in sorteados_set:
                saiu_por_score[score] += 1
    
    print("\n   Score | Saiu | Oportunidades | Taxa de Saída")
    print("   " + "-" * 55)
    
    for score in sorted(saiu_por_score.keys()):
        saiu = saiu_por_score[score]
        total = total_por_score[score]
        taxa = (saiu / total * 100) if total > 0 else 0
        print(f"   {score:+3d}   | {saiu:4d} | {total:13d} | {taxa:5.2f}%")
    
    saiu_pos = sum(saiu_por_score[s] for s in saiu_por_score if s > 0)
    total_pos = sum(total_por_score[s] for s in total_por_score if s > 0)
    saiu_neg = sum(saiu_por_score[s] for s in saiu_por_score if s < 0)
    total_neg = sum(total_por_score[s] for s in total_por_score if s < 0)
    saiu_zero = saiu_por_score.get(0, 0)
    total_zero = total_por_score.get(0, 0)
    
    taxa_pos = (saiu_pos / total_pos * 100) if total_pos > 0 else 0
    taxa_neg = (saiu_neg / total_neg * 100) if total_neg > 0 else 0
    taxa_zero = (saiu_zero / total_zero * 100) if total_zero > 0 else 0
    
    print(f"\n   📈 Resumo:")
    print(f"      Score > 0: {taxa_pos:.2f}% ({saiu_pos}/{total_pos})")
    print(f"      Score = 0: {taxa_zero:.2f}% ({saiu_zero}/{total_zero})")
    print(f"      Score < 0: {taxa_neg:.2f}% ({saiu_neg}/{total_neg})")
    
    diferenca = taxa_pos - taxa_neg
    print(f"      Diferença (pos - neg): {diferenca:+.2f}pp")
    
    baseline = 7 / 10 * 100
    print(f"\n      Baseline aleatório: {baseline:.1f}% (7 dígitos sorteados de 10 possíveis)")
    
    if diferenca > 5:
        print("      ✅ Score cross-coluna TEM poder preditivo!")
    elif diferenca < -5:
        print("      ⚠️  Score cross-coluna tem efeito INVERSO (contrarian)")
    else:
        print("      ❌ Score cross-coluna NÃO tem poder preditivo significativo")
    
    return {
        'saiu_por_score': dict(saiu_por_score),
        'total_por_score': dict(total_por_score),
        'taxa_positivos': taxa_pos,
        'taxa_negativos': taxa_neg,
        'taxa_zero': taxa_zero,
        'diferenca': diferenca,
    }


def analisar_pool_global(resultados: List[List[int]]) -> Dict:
    """
    Testa se um "pool global" (top N dígitos mais quentes em todas as colunas)
    melhora a geração de jogos.
    """
    print("\n🎯 Analisando eficácia de Pool Global...")
    
    acertos_pool_5 = 0
    acertos_pool_7 = 0
    acertos_sem_pool = 0
    total_testes = 0
    
    for i in range(JANELA_QMF, len(resultados)):
        historico = resultados[:i]
        sorteio_atual = resultados[i]
        
        quentes, _, frios = calcular_qmf_por_coluna(historico)
        scores = calcular_score_cross_coluna(quentes, frios)
        
        ranked_global = sorted(DIGITOS, key=lambda d: scores[d], reverse=True)
        pool_5 = set(ranked_global[:5])
        pool_7 = set(ranked_global[:7])
        
        digitos_sorteio = set(sorteio_atual)
        
        acertos_pool_5 += len(digitos_sorteio & pool_5)
        acertos_pool_7 += len(digitos_sorteio & pool_7)
        acertos_sem_pool += len(digitos_sorteio)
        total_testes += 1
    
    media_pool_5 = acertos_pool_5 / total_testes
    media_pool_7 = acertos_pool_7 / total_testes
    media_sem_pool = acertos_sem_pool / total_testes
    
    print(f"\n   Estratégia          | Média de Acertos por Sorteio")
    print("   " + "-" * 55)
    print(f"   Pool Global (5)     | {media_pool_5:.2f} dígitos do pool no sorteio")
    print(f"   Pool Global (7)     | {media_pool_7:.2f} dígitos do pool no sorteio")
    print(f"   Sem Pool (baseline) | {media_sem_pool:.2f} dígitos (sempre 7)")
    
    print(f"\n   📊 Análise:")
    print(f"      Pool 5 cobre {media_pool_5/7*100:.1f}% dos dígitos sorteados")
    print(f"      Pool 7 cobre {media_pool_7/7*100:.1f}% dos dígitos sorteados")
    
    if media_pool_5 > 3.5:
        print("      ✅ Pool de 5 dígitos é EFICAZ (cobre >50% dos sorteados)")
    else:
        print("      ❌ Pool de 5 dígitos NÃO é eficaz")
    
    if media_pool_7 > 5:
        print("      ✅ Pool de 7 dígitos é MUITO eficaz (cobre >70% dos sorteados)")
    else:
        print("      ⚠️  Pool de 7 dígitos tem eficácia moderada")
    
    return {
        'media_pool_5': media_pool_5,
        'media_pool_7': media_pool_7,
        'cobertura_pool_5': media_pool_5 / 7 * 100,
        'cobertura_pool_7': media_pool_7 / 7 * 100,
    }


def comparar_estrategias_geracao(resultados: List[List[int]]) -> Dict:
    """
    Compara 3 estratégias de geração:
    1. Aleatório puro
    2. QMF por coluna (independente)
    3. QMF por coluna + filtro cross-coluna (score > 0)
    """
    print("\n🎲 Comparando estratégias de geração...")
    
    import random
    
    resultados_aleatorio = []
    resultados_qmf_coluna = []
    resultados_qmf_cross = []
    
    for i in range(JANELA_QMF, len(resultados)):
        historico = resultados[:i]
        sorteio_atual = resultados[i]
        
        quentes, _, frios = calcular_qmf_por_coluna(historico)
        scores = calcular_score_cross_coluna(quentes, frios)
        
        jogo_aleatorio = [random.choice(DIGITOS) for _ in range(NUM_COLUNAS)]
        
        jogo_qmf_coluna = []
        for col in range(NUM_COLUNAS):
            top3 = quentes[col][:3]
            jogo_qmf_coluna.append(random.choice(top3) if top3 else random.choice(DIGITOS))
        
        jogo_qmf_cross = []
        for col in range(NUM_COLUNAS):
            candidatos = [d for d in quentes[col] if scores[d] > 0]
            if not candidatos:
                candidatos = quentes[col][:3]
            jogo_qmf_cross.append(random.choice(candidatos) if candidatos else random.choice(DIGITOS))
        
        acertos_aleatorio = sum(1 for col in range(NUM_COLUNAS) if jogo_aleatorio[col] == sorteio_atual[col])
        acertos_qmf_coluna = sum(1 for col in range(NUM_COLUNAS) if jogo_qmf_coluna[col] == sorteio_atual[col])
        acertos_qmf_cross = sum(1 for col in range(NUM_COLUNAS) if jogo_qmf_cross[col] == sorteio_atual[col])
        
        resultados_aleatorio.append(acertos_aleatorio)
        resultados_qmf_coluna.append(acertos_qmf_coluna)
        resultados_qmf_cross.append(acertos_qmf_cross)
    
    media_aleatorio = statistics.mean(resultados_aleatorio)
    media_qmf_coluna = statistics.mean(resultados_qmf_coluna)
    media_qmf_cross = statistics.mean(resultados_qmf_cross)
    
    print(f"\n   Estratégia                    | Média de Acertos | Melhoria vs Aleatório")
    print("   " + "-" * 75)
    print(f"   1. Aleatório                  | {media_aleatorio:.3f}            | -")
    print(f"   2. QMF por Coluna             | {media_qmf_coluna:.3f}            | {(media_qmf_coluna/media_aleatorio - 1)*100:+.1f}%")
    print(f"   3. QMF + Cross-Coluna         | {media_qmf_cross:.3f}            | {(media_qmf_cross/media_aleatorio - 1)*100:+.1f}%")
    
    print(f"\n   🏆 Melhor estratégia: ", end="")
    if media_qmf_cross > media_qmf_coluna > media_aleatorio:
        print("QMF + Cross-Coluna (análise cross-coluna MELHORA a geração)")
    elif media_qmf_coluna > media_aleatorio:
        print("QMF por Coluna (cross-coluna não ajuda, mas QMF independente sim)")
    else:
        print("Aleatório (nenhuma estratégia supera o acaso)")
    
    return {
        'media_aleatorio': media_aleatorio,
        'media_qmf_coluna': media_qmf_coluna,
        'media_qmf_cross': media_qmf_cross,
        'melhoria_qmf': (media_qmf_coluna / media_aleatorio - 1) * 100,
        'melhoria_cross': (media_qmf_cross / media_aleatorio - 1) * 100,
    }


def main():
    print("=" * 80)
    print("🔬 PoC: Análise de Correlação QMF Cross-Coluna no Super Sete")
    print("=" * 80)
    
    resultados = carregar_resultados()
    
    if not resultados:
        print("\n❌ Nenhum resultado carregado. Verifique a conexão com o banco.")
        return
    
    print(f"\n✅ {len(resultados)} sorteios carregados")
    
    analise_correlacao = analisar_correlacao_score_saida(resultados)
    analise_pool = analisar_pool_global(resultados)
    analise_estrategias = comparar_estrategias_geracao(resultados)
    
    print("\n" + "=" * 80)
    print("📋 CONCLUSÕES")
    print("=" * 80)
    
    diff = analise_correlacao['diferenca']
    if diff > 2:
        print("\n✅ Score cross-coluna TEM valor preditivo:")
        print(f"   Dígitos com score positivo saem {diff:.1f}pp mais que dígitos com score negativo")
        print("   Recomendação: usar análise cross-coluna para filtrar candidatos")
    else:
        print("\n❌ Score cross-coluna NÃO tem valor preditivo significativo")
        print("   Recomendação: focar apenas em QMF por coluna (independente)")
    
    cobertura_5 = analise_pool['cobertura_pool_5']
    if cobertura_5 > 50:
        print(f"\n✅ Pool global de 5 dígitos é eficaz ({cobertura_5:.1f}% de cobertura)")
        print("   Recomendação: usar pool global como pré-filtro antes de QMF por coluna")
    else:
        print(f"\n❌ Pool global NÃO é eficaz ({cobertura_5:.1f}% de cobertura)")
        print("   Recomendação: não usar pool global, focar em análise por coluna")
    
    melhoria_cross = analise_estrategias['melhoria_cross']
    melhoria_qmf = analise_estrategias['melhoria_qmf']
    
    if melhoria_cross > melhoria_qmf + 5:
        print(f"\n🏆 Cross-coluna supera QMF independente em {melhoria_cross - melhoria_qmf:.1f}pp")
    elif melhoria_qmf > 10:
        print(f"\n🏆 QMF por coluna já é bom ({melhoria_qmf:.1f}% de melhoria)")
        print("   Cross-coluna não agrega valor significativo")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
