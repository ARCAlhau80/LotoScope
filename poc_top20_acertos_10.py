#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POC: TOP 20 CANDIDATAS A ACERTAR 10 NA LOTOFACIL
=================================================
Analisa a tabela COMBINACOES_LOTOFACIL baseado em ciclos de
repeticao e frequencia das dezenas, seleciona as 20 melhores
candidatas a acertar exatamente 10 numeros, e valida contra
o historico.

Autor: AR CALHAU
Data: 29/07/2026
"""

import sys
import os
import math
from datetime import datetime
from itertools import combinations
from random import sample

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotofacil_lite'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotofacil_lite', 'utils'))

try:
    from database_config import DatabaseConfig
except ImportError:
    print("ERRO: database_config nao encontrado.")
    sys.exit(1)


def analisar_frequencias(db, janela=50):
    """Analisa frequencia de cada numero (total e janela recente)."""
    print("=" * 70)
    print(f"ANALISE DE FREQUENCIA DAS DEZENAS (janela recente: {janela} concursos)")
    print("=" * 70)

    total_conc = db.execute_query_dataframe(
        "SELECT COUNT(*) FROM Resultados_INT"
    ).iloc[0, 0]

    ultimo_conc = db.execute_query_dataframe(
        "SELECT MAX(Concurso) FROM Resultados_INT"
    ).iloc[0, 0]

    # Frequencia total
    freq_total = db.execute_query_dataframe("""
        SELECT Numero, COUNT(*) as freq
        FROM (
            SELECT N1 as Numero FROM Resultados_INT UNION ALL
            SELECT N2 FROM Resultados_INT UNION ALL
            SELECT N3 FROM Resultados_INT UNION ALL
            SELECT N4 FROM Resultados_INT UNION ALL
            SELECT N5 FROM Resultados_INT UNION ALL
            SELECT N6 FROM Resultados_INT UNION ALL
            SELECT N7 FROM Resultados_INT UNION ALL
            SELECT N8 FROM Resultados_INT UNION ALL
            SELECT N9 FROM Resultados_INT UNION ALL
            SELECT N10 FROM Resultados_INT UNION ALL
            SELECT N11 FROM Resultados_INT UNION ALL
            SELECT N12 FROM Resultados_INT UNION ALL
            SELECT N13 FROM Resultados_INT UNION ALL
            SELECT N14 FROM Resultados_INT UNION ALL
            SELECT N15 FROM Resultados_INT
        ) AS todos
        GROUP BY Numero
        ORDER BY Numero
    """)

    # Frequencia recente (janela)
    freq_recente = db.execute_query_dataframe(f"""
        SELECT Numero, COUNT(*) as freq
        FROM (
            SELECT N1 as Numero FROM Resultados_INT
            WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N2 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N3 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N4 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N5 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N6 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N7 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N8 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N9 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N10 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N11 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N12 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N13 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N14 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela} UNION ALL
            SELECT N15 FROM Resultados_INT WHERE Concurso > {ultimo_conc - janela}
        ) AS todos
        GROUP BY Numero
        ORDER BY Numero
    """)

    # Frequencia esperada
    freq_esperada_total = total_conc * 15 / 25
    freq_esperada_janela = janela * 15 / 25

    print(f"\nTotal de concursos: {total_conc}")
    print(f"Ultimo concurso: {ultimo_conc}")
    print(f"Freq. esperada total: {freq_esperada_total:.1f}")
    print(f"Freq. esperada (janela {janela}): {freq_esperada_janela:.1f}")
    print()
    print(f"{'Num':>4} {'Freq Tot':>9} {'Esperado':>9} {'Desvio%':>8} {'Freq Rec':>9} {'Desvio%':>8} {'Score':>7}")
    print("-" * 60)

    resultados = {'total': {}, 'recente': {}}
    scores = {}

    for _, row in freq_total.iterrows():
        n = int(row['Numero'])
        ft = int(row['freq'])
        resultados['total'][n] = ft

    for _, row in freq_recente.iterrows():
        n = int(row['Numero'])
        fr = int(row['freq'])
        resultados['recente'][n] = fr

    for n in range(1, 26):
        ft = resultados['total'].get(n, 0)
        fr = resultados['recente'].get(n, 0)

        desv_total = (ft / freq_esperada_total - 1) * 100
        desv_recente = (fr / freq_esperada_janela - 1) * 100

        # Score combinado: peso 0.7 na frequencia total, 0.3 na recente
        # Score alto = numero frequente e quente
        score = 0.7 * (ft / freq_esperada_total) + 0.3 * (fr / freq_esperada_janela)
        scores[n] = score

        print(f"  {n:2d}  {ft:>6} ({freq_esperada_total:>6.0f}) {desv_total:>+6.1f}%  {fr:>3} ({freq_esperada_janela:>5.0f}) {desv_recente:>+6.1f}%  {score:.4f}")

    # Ranking
    ranking = sorted(scores.items(), key=lambda x: -x[1])
    print(f"\nRANKING DAS DEZENAS (maior score = mais frequente):")
    for i, (n, s) in enumerate(ranking, 1):
        ft = resultados['total'][n]
        fr = resultados['recente'].get(n, 0)
        print(f"  {i:2d}. Numero {n:2d} - score={s:.4f} | total={ft} | recente({janela})={fr}")

    return ranking, resultados, ultimo_conc


def gerar_candidatas_por_frequencia(ranking, top_n=12):
    """
    Gera combinacoes combinando numeros frequentes + infrequentes.
    A logica: combinar muitos numeros frequentes com alguns infrequentes
    maximiza a chance de acertar exatamente 10.

    Os 12 primeiros do ranking sao o "core" frequente.
    Os 13 restantes sao "complemento".
    """
    numeros_frequentes = [n for n, _ in ranking[:top_n]]
    numeros_infrequentes = [n for n, _ in ranking[top_n:]]

    print(f"\nNumeros frequentes (top {top_n}): {numeros_frequentes}")
    print(f"Numeros complemento ({25-top_n}): {numeros_infrequentes}")

    candidatas = []
    seen = set()

    # Estrategia: combinar 9-11 numeros frequentes com 4-6 infrequentes
    # Isso cria combinacoes balanceadas para acertar exatamente 10
    from itertools import combinations as comb_iter

    for n_freq in range(9, 12):
        n_infreq = 15 - n_freq
        if n_infreq < 2 or n_infreq > len(numeros_infrequentes):
            continue

        for freq_part in comb_iter(numeros_frequentes, n_freq):
            for infreq_part in comb_iter(numeros_infrequentes, n_infreq):
                combo = tuple(sorted(freq_part + infreq_part))
                if combo not in seen:
                    seen.add(combo)
                    candidatas.append(combo)
                    if len(candidatas) >= 10000:
                        break
            if len(candidatas) >= 10000:
                break
        if len(candidatas) >= 10000:
            break

    print(f"Total de candidatas geradas: {len(candidatas):,}")
    return candidatas, numeros_frequentes, numeros_infrequentes


def pontuar_candidatas(db, candidatas, ultimo_conc):
    """Pontua as candidatas baseado em Acertos_10 historico e atraso."""
    print("\n" + "=" * 70)
    print("PONTUACAO DAS CANDIDATAS")
    print("=" * 70)

    # Construir IN clause
    combinacoes_sql = []
    for combo in candidatas:
        nums_str = ','.join(map(str, combo))
        combinacoes_sql.append(f"(N1={combo[0]} AND N2={combo[1]} AND N3={combo[2]} AND N4={combo[3]} AND N5={combo[4]} AND N6={combo[5]} AND N7={combo[6]} AND N8={combo[7]} AND N9={combo[8]} AND N10={combo[9]} AND N11={combo[10]} AND N12={combo[11]} AND N13={combo[12]} AND N14={combo[13]} AND N15={combo[14]})")

    # Buscar dados no banco (em lotes para evitar SQL enorme)
    lote = 500
    resultados = []

    for i in range(0, len(combinacoes_sql), lote):
        where_clause = ' OR '.join(combinacoes_sql[i:i+lote])
        query = f"""
        SELECT ID, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
               Acertos_10, Ultimo_Acertos_10, Acertos_11, Acertos_12,
               Acertos_13, Acertos_14, Acertos_15
        FROM COMBINACOES_LOTOFACIL
        WHERE {where_clause}
        """
        df = db.execute_query_dataframe(query)
        if df is not None:
            resultados.append(df)

    if not resultados:
        print("ERRO: Nenhuma candidata encontrada na tabela.")
        return []

    import pandas as pd
    df_combos = pd.concat(resultados, ignore_index=True)
    print(f"Candidatas encontradas na tabela: {len(df_combos)}")

    # Pontuacao
    media_acertos_10 = df_combos['Acertos_10'].mean()
    max_acertos_10 = df_combos['Acertos_10'].max()

    atrasos = []
    for _, row in df_combos.iterrows():
        if row['Ultimo_Acertos_10'] and row['Ultimo_Acertos_10'] > 0:
            atrasos.append(ultimo_conc - row['Ultimo_Acertos_10'])
        else:
            atrasos.append(ultimo_conc)
    df_combos['Atraso'] = atrasos

    media_atraso = df_combos['Atraso'].mean()

    # Score: frequencia normalizada + atraso normalizado
    # Quanto maior, mais "devida" e mais frequente
    if media_acertos_10 > 0 and media_atraso > 0:
        df_combos['Score'] = (
            (df_combos['Acertos_10'] / df_combos['Acertos_10'].max()) * 0.6 +
            (df_combos['Atraso'] / df_combos['Atraso'].max()) * 0.4
        )
    else:
        df_combos['Score'] = 0

    # Calcular "proporcao de numeros frequentes"
    df_combos['QtdeFreq'] = df_combos.apply(
        lambda r: sum(1 for j in range(1, 16) if r[f'N{j}'] in numeros_frequentes_global),
        axis=1
    )

    # Ordenar por score
    df_ranking = df_combos.sort_values('Score', ascending=False).reset_index(drop=True)

    return df_ranking


def validar_contra_historico(db, top20_df, ultimo_conc, num_testes=500):
    """
    Valida as 20 candidatas contra os ultimos N concursos.
    Conta quantas vezes cada uma teria acertado exatamente 10.
    Compara com 20 combinacoes aleatorias.
    """
    print("\n" + "=" * 70)
    print(f"VALIDACAO: Backtest nos ultimos {num_testes} concursos")
    print("=" * 70)

    if top20_df is None or len(top20_df) == 0:
        print("ERRO: Nenhuma candidata para validar.")
        return

    # Gerar 20 combinacoes aleatorias para comparacao
    import random
    random.seed(42)
    from itertools import combinations as comb_iter

    todas_combinacoes = list(comb_iter(range(1, 26), 15))
    random_20 = random.sample(todas_combinacoes, 20)
    print(f"Geradas 20 combinacoes aleatorias para comparacao.")

    concursos_teste = db.execute_query_dataframe(f"""
        SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
        FROM Resultados_INT
        WHERE Concurso > {ultimo_conc - num_testes}
        ORDER BY Concurso
    """)

    if concursos_teste is None:
        print("ERRO: Nao foi possivel carregar concursos.")
        return

    print(f"Testando contra {len(concursos_teste)} concursos...")

    # Validar candidatas (frequencia-based)
    acertos_candidatas = []
    for _, row in top20_df.iterrows():
        nums_combo = {int(row[f'N{j}']) for j in range(1, 16)}
        count = 0
        for _, r in concursos_teste.iterrows():
            nums_sorteio = {int(r[f'N{j}']) for j in range(1, 16)}
            if len(nums_combo & nums_sorteio) == 10:
                count += 1
        acertos_candidatas.append(count)

    # Validar aleatorias
    acertos_aleatorias = []
    for combo in random_20:
        nums_combo = set(combo)
        count = 0
        for _, r in concursos_teste.iterrows():
            nums_sorteio = {int(r[f'N{j}']) for j in range(1, 16)}
            if len(nums_combo & nums_sorteio) == 10:
                count += 1
        acertos_aleatorias.append(count)

    # Estatisticas
    media_cand = sum(acertos_candidatas) / len(acertos_candidatas)
    media_rand = sum(acertos_aleatorias) / len(acertos_aleatorias)
    total_cand = sum(acertos_candidatas)
    total_rand = sum(acertos_aleatorias)

    esperado = num_testes * 756756 / 3268760

    print()
    print(f"{'Metrica':>40} {'Candidatas':>12} {'Aleatorias':>12} {'Esperado':>12}")
    print("-" * 80)
    print(f"{'Media de acertos 10 por combo':>40} {media_cand:>12.2f} {media_rand:>12.2f} {esperado:>12.2f}")
    print(f"{'Total acertos 10 (20 combos)':>40} {total_cand:>12} {total_rand:>12} {esperado*20:>12.0f}")
    print(f"{'Melhor combo':>40} {max(acertos_candidatas):>12} {max(acertos_aleatorias):>12}")
    print(f"{'Pior combo':>40} {min(acertos_candidatas):>12} {min(acertos_aleatorias):>12}")
    print(f"{'Desvio padrao':>40} {__import__('statistics').stdev(acertos_candidatas):>12.2f} {__import__('statistics').stdev(acertos_aleatorias):>12.2f}")

    # Teste qui-quadrado para verificar diferenca significativa
    print()
    if abs(total_cand - total_rand) < 2 * (total_cand ** 0.5):
        print("CONCLUSÃO: Diferenca dentro do ruido esperado. Nao ha ganho real.")
        print("As 20 candidatas baseadas em frequencia tem desempenho similar")
        print("a 20 combinacoes aleatorias.")
    else:
        vencedor = "CANDIDATAS" if total_cand > total_rand else "ALEATORIAS"
        print(f"CONCLUSÃO: {vencedor} tiveram desempenho superior estatisticamente.")
        print("Porem o ganho pratico e marginal.")

    return {
        'candidatas': acertos_candidatas,
        'aleatorias': acertos_aleatorias,
        'total_cand': total_cand,
        'total_rand': total_rand,
        'media_cand': media_cand,
        'media_rand': media_rand
    }


def mostrar_top20(top20_df):
    """Exibe as 20 melhores candidatas."""
    print("\n" + "=" * 70)
    print("TOP 20 CANDIDATAS A ACERTAR 10")
    print("=" * 70)
    print(f"{'#':>3} {'ID':>8} {'Combinacao':<50} {'Acertos10':>9} {'Atraso':>7} {'Score':>7}")
    print("-" * 90)

    top20 = top20_df.head(20)
    for i, (_, row) in enumerate(top20.iterrows(), 1):
        nums = ' '.join(f"{int(row[f'N{j}']):02d}" for j in range(1, 16))
        print(f"{i:>3} {int(row['ID']):>8} {nums:<50} {int(row['Acertos_10']):>9} {int(row['Atraso']):>7} {row['Score']:>7.4f}")

    return top20


# Variavel global para acesso nas funcoes
numeros_frequentes_global = []


def main():
    print()
    print("=" * 70)
    print("POC: TOP 20 CANDIDATAS A ACERTAR 10 NA LOTOFACIL")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    db = DatabaseConfig()
    if not db.test_connection():
        print("ERRO: Nao foi possivel conectar ao banco.")
        sys.exit(1)

    # 1. Analisar frequencias
    ranking, freq_data, ultimo_conc = analisar_frequencias(db, janela=50)

    # 2. Gerar candidatas baseadas em frequencia
    global numeros_frequentes_global
    candidatas, numeros_frequentes_global, numeros_infrequentes = \
        gerar_candidatas_por_frequencia(ranking, top_n=12)

    # 3. Pontuar as candidatas
    df_ranking = pontuar_candidatas(db, candidatas, ultimo_conc)

    if len(df_ranking) == 0:
        print("ERRO: Nenhuma candidata pontuada.")
        sys.exit(1)

    # 4. Mostrar top 20
    top20 = mostrar_top20(df_ranking)

    # 5. Validar contra historico
    resultado = validar_contra_historico(db, top20, ultimo_conc, num_testes=500)

    # 6. Mostrar analise teorica
    print()
    print("=" * 70)
    print("ANALISE TEORICA")
    print("=" * 70)
    print(f"""
Probabilidade de qualquer combinacao acertar exatamente 10 em 1 sorteio:
  P = C(15,10) * C(10,5) / C(25,15) = {math.comb(15,10)*math.comb(10,5)/math.comb(25,15):.6f} ({math.comb(15,10)*math.comb(10,5)/math.comb(25,15)*100:.4f}%)

Com {500} concursos de backtest:
  Esperado por combo: {500 * math.comb(15,10)*math.comb(10,5)/math.comb(25,15):.1f}
  Esperado total (20 combos): {500 * math.comb(15,10)*math.comb(10,5)/math.comb(25,15)*20:.1f}

Cada combinacao tem a MESMA probabilidade de acertar 10.
A analise de frequencia/ciclos nao altera a chance individual.
O que o ranking mostra sao apenas flutuacoes historicas aleatorias.
    """)

    if resultado:
        print(f"RESULTADO FINAL:")
        print(f"  20 candidatas por frequencia: {resultado['total_cand']} acertos 10")
        print(f"  20 combinacoes aleatorias:    {resultado['total_rand']} acertos 10")
        diff = resultado['total_cand'] - resultado['total_rand']
        print(f"  Diferenca: {diff:+d} ({diff/resultado['total_rand']*100:+.1f}%)")
        if abs(diff) < 2 * (resultado['total_cand'] ** 0.5):
            print("  -> Diferenca dentro do ruido estatistico.")
            print("  -> Frequencia passada nao preve acerto futuro.")
        else:
            print("  -> Diferenca significativa (mas provavelmente espuria).")

    print()
    print("=" * 70)
    print("POC CONCLUIDA!")
    print("=" * 70)


if __name__ == "__main__":
    main()
