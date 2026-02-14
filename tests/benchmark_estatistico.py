#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔬 BENCHMARK ESTATÍSTICO DO GERADOR HÍBRIDO
Executa múltiplas vezes para obter média confiável
"""

import sys
from pathlib import Path
import statistics

# Configurar paths
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / 'lotofacil_lite'))
sys.path.insert(0, str(ROOT_DIR / 'lotofacil_lite' / 'utils'))
sys.path.insert(0, str(ROOT_DIR / 'lotofacil_lite' / 'geradores'))

import warnings
warnings.filterwarnings('ignore')

# Suprimir prints do gerador
import io
import contextlib

from database_config import db_config


def avaliar_gerador(combinacoes, resultados):
    """Avalia combinações contra resultados"""
    melhores = []
    for resultado in resultados:
        melhor = max(len(c.intersection(resultado)) for c in combinacoes)
        melhores.append(melhor)
    
    taxa_11 = sum(1 for m in melhores if m >= 11) / len(melhores) * 100
    taxa_12 = sum(1 for m in melhores if m >= 12) / len(melhores) * 100
    media = statistics.mean(melhores)
    
    return taxa_11, taxa_12, media


def carregar_resultados(n=20):
    """Carrega últimos N resultados"""
    conn = db_config.get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {n} N1, N2, N3, N4, N5, N6, N7, N8, 
               N9, N10, N11, N12, N13, N14, N15
        FROM RESULTADOS_INT ORDER BY Concurso DESC
    """)
    
    resultados = [set(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return resultados


def main():
    print("\n" + "=" * 70)
    print("🔬 BENCHMARK ESTATÍSTICO - GERADOR HÍBRIDO vs ESTRATÉGIAS")
    print("=" * 70)
    
    resultados_historicos = carregar_resultados(20)
    print(f"📊 Testando contra {len(resultados_historicos)} concursos")
    
    n_iteracoes = 10
    print(f"🔄 Executando {n_iteracoes} iterações de cada estratégia...\n")
    
    # Importar gerador híbrido
    with contextlib.redirect_stdout(io.StringIO()):
        from gerador_hibrido_otimizado import GeradorHibridoOtimizado
    
    # Testar Gerador Híbrido
    print("🏆 GERADOR HÍBRIDO:")
    taxas_11_hibrido = []
    taxas_12_hibrido = []
    
    for i in range(n_iteracoes):
        with contextlib.redirect_stdout(io.StringIO()):
            gerador = GeradorHibridoOtimizado()
            resultado = gerador.gerar_super_combinacoes(10)
        
        combinacoes = [set(c['numeros']) for c in resultado['combinacoes']]
        t11, t12, _ = avaliar_gerador(combinacoes, resultados_historicos)
        taxas_11_hibrido.append(t11)
        taxas_12_hibrido.append(t12)
        print(f"   Iteração {i+1}: 11+={t11:.0f}%, 12+={t12:.0f}%")
    
    media_11_hibrido = statistics.mean(taxas_11_hibrido)
    media_12_hibrido = statistics.mean(taxas_12_hibrido)
    print(f"   📊 MÉDIA: 11+={media_11_hibrido:.1f}%, 12+={media_12_hibrido:.1f}%")
    
    # Testar Equilibrado (baseline)
    print("\n⚖️ EQUILIBRADO PAR/ÍMPAR:")
    import random
    taxas_11_eq = []
    taxas_12_eq = []
    
    for i in range(n_iteracoes):
        combinacoes = []
        for _ in range(10):
            impares = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
            pares = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
            qtd_impares = random.choice([7, 8])
            nums = set(random.sample(impares, qtd_impares))
            nums.update(random.sample(pares, 15 - qtd_impares))
            combinacoes.append(nums)
        
        t11, t12, _ = avaliar_gerador(combinacoes, resultados_historicos)
        taxas_11_eq.append(t11)
        taxas_12_eq.append(t12)
        print(f"   Iteração {i+1}: 11+={t11:.0f}%, 12+={t12:.0f}%")
    
    media_11_eq = statistics.mean(taxas_11_eq)
    media_12_eq = statistics.mean(taxas_12_eq)
    print(f"   📊 MÉDIA: 11+={media_11_eq:.1f}%, 12+={media_12_eq:.1f}%")
    
    # Testar Frequência
    print("\n📊 FREQUÊNCIA HISTÓRICA:")
    
    # Carregar frequências
    conn = db_config.get_connection()
    cursor = conn.cursor()
    freqs = {i: 0 for i in range(1, 26)}
    for i in range(1, 16):
        cursor.execute(f"SELECT N{i}, COUNT(*) FROM RESULTADOS_INT GROUP BY N{i}")
        for num, cnt in cursor.fetchall():
            if num in freqs:
                freqs[num] += cnt
    cursor.close()
    conn.close()
    
    top_18 = [n for n, _ in sorted(freqs.items(), key=lambda x: -x[1])[:18]]
    
    taxas_11_freq = []
    taxas_12_freq = []
    
    for i in range(n_iteracoes):
        combinacoes = []
        for _ in range(10):
            nums = set(random.sample(top_18, 15))
            combinacoes.append(nums)
        
        t11, t12, _ = avaliar_gerador(combinacoes, resultados_historicos)
        taxas_11_freq.append(t11)
        taxas_12_freq.append(t12)
        print(f"   Iteração {i+1}: 11+={t11:.0f}%, 12+={t12:.0f}%")
    
    media_11_freq = statistics.mean(taxas_11_freq)
    media_12_freq = statistics.mean(taxas_12_freq)
    print(f"   📊 MÉDIA: 11+={media_11_freq:.1f}%, 12+={media_12_freq:.1f}%")
    
    # Resumo Final
    print("\n" + "=" * 70)
    print("🏆 RANKING FINAL (MÉDIA DE 10 ITERAÇÕES)")
    print("=" * 70)
    
    resultados = [
        ("🏆 Gerador Híbrido", media_11_hibrido, media_12_hibrido),
        ("⚖️ Equilibrado", media_11_eq, media_12_eq),
        ("📊 Frequência", media_11_freq, media_12_freq),
    ]
    
    # Ordenar por taxa 11+
    resultados.sort(key=lambda x: (-x[1], -x[2]))
    
    print(f"\n{'Estratégia':<25} {'Taxa 11+':<12} {'Taxa 12+':<12}")
    print("-" * 50)
    
    for i, (nome, t11, t12) in enumerate(resultados):
        medalha = ['🥇', '🥈', '🥉'][i] if i < 3 else '  '
        print(f"{medalha} {nome:<23} {t11:>6.1f}%      {t12:>6.1f}%")
    
    # Score combinado
    print("\n📊 SCORE COMBINADO (11+ × 0.6 + 12+ × 0.4):")
    for nome, t11, t12 in resultados:
        score = t11 * 0.6 + t12 * 0.4
        print(f"   {nome}: {score:.1f}")


if __name__ == "__main__":
    main()
