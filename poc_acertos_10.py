#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POC: ANALISE DE ACERTOS 10 - COMBINACOES_LOTOFACIL (15 numeros)
================================================================
Conta quantas vezes cada combinacao acertou exatamente 10 numeros
em TODO o historico da Lotofacil, e registra o ultimo concurso.

Mesma abordagem de calcular_acertos_inicial.py (subquery correlacionada
unica processando todos os concursos de uma vez) — adaptada para 10 acertos.

Autor: AR CALHAU
Data: 29/07/2026
"""

import sys
import os
import argparse
from datetime import datetime
import math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotofacil_lite'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotofacil_lite', 'utils'))

try:
    from database_config import DatabaseConfig
except ImportError:
    print("ERRO: database_config nao encontrado. Verifique o path.")
    sys.exit(1)


def verificar_estrutura():
    """Verifica se as colunas Acertos_10 existem."""
    db = DatabaseConfig()
    check = db.execute_query_dataframe("""
        SELECT COUNT(*) as qtd
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL'
        AND COLUMN_NAME IN ('Acertos_10', 'Ultimo_Acertos_10')
    """)
    if check is None:
        return False
    return check.iloc[0]['qtd'] == 2


def adicionar_colunas():
    """Adiciona colunas se nao existirem."""
    db = DatabaseConfig()
    print()
    print("=" * 70)
    print("Verificando colunas Acertos_10 e Ultimo_Acertos_10...")
    print("=" * 70)

    colunas = [
        "ALTER TABLE COMBINACOES_LOTOFACIL ADD Acertos_10 INT DEFAULT 0 NOT NULL",
        "ALTER TABLE COMBINACOES_LOTOFACIL ADD Ultimo_Acertos_10 INT NULL",
    ]

    for ddl in colunas:
        col_name = ddl.split()[4]
        check = db.execute_query_dataframe(f"""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = '{col_name}'
        """)
        if check is not None and check.iloc[0, 0] > 0:
            print(f"  Coluna {col_name} ja existe.")
        else:
            ok = db.execute_command(ddl)
            print(f"  Coluna {col_name} {'criada' if ok else 'ERRO'}.")

    for idx, col in [
        ("IX_COMBINACOES_LF_Acertos_10", "Acertos_10"),
        ("IX_COMBINACOES_LF_Ultimo_10", "Ultimo_Acertos_10"),
    ]:
        check = db.execute_query_dataframe(f"""
            SELECT COUNT(*) FROM sys.indexes
            WHERE name = '{idx}' AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL')
        """)
        if check is not None and check.iloc[0, 0] == 0:
            db.execute_command(f"CREATE INDEX {idx} ON COMBINACOES_LOTOFACIL({col})")
            print(f"  Indice {idx} criado.")
        else:
            print(f"  Indice {idx} ja existe.")


def zerar_contagens():
    """Reseta Acertos_10 para zero."""
    db = DatabaseConfig()
    print()
    print("Zerando contagens de Acertos_10...")
    ok = db.execute_command("""
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_10 = 0, Ultimo_Acertos_10 = NULL, UltimoConcursoAtualizado = 0
    """)
    print(f"  {'OK' if ok else 'ERRO'}")


def obter_estatisticas():
    """Obtem estatisticas para dimensionar o processamento."""
    db = DatabaseConfig()
    stats = db.execute_query_dataframe("""
        SELECT
            (SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL) as total_comb,
            (SELECT COUNT(*) FROM Resultados_INT) as total_concursos,
            (SELECT MIN(Concurso) FROM Resultados_INT) as min_conc,
            (SELECT MAX(Concurso) FROM Resultados_INT) as max_conc
    """)
    if stats is None:
        return None

    s = stats.iloc[0]
    total_comb = int(s['total_comb'])
    total_conc = int(s['total_concursos'])
    min_conc = int(s['min_conc'])
    max_conc = int(s['max_conc'])

    comparacoes = total_comb * total_conc
    tempo_estimado = comparacoes / 500000  # ~500K comparacoes/s (empirico)
    tempo_estimado_str = f"{tempo_estimado/3600:.1f}h" if tempo_estimado > 3600 else f"{tempo_estimado/60:.0f}min"

    print()
    print("=" * 70)
    print("ESTATISTICAS DO PROCESSAMENTO:")
    print("=" * 70)
    print(f"  Total de combinacoes: {total_comb:,}")
    print(f"  Total de concursos historicos: {total_conc:,}")
    print(f"  Range de concursos: {min_conc} - {max_conc}")
    print(f"  Comparacoes necessarias: {comparacoes:,}")
    print(f"  Tempo estimado: ~{tempo_estimado_str}")

    return {
        'total_comb': total_comb,
        'total_conc': total_conc,
        'min_conc': min_conc,
        'max_conc': max_conc,
        'comparacoes': comparacoes,
        'tempo_estimado': tempo_estimado
    }


def processar_acertos_historico():
    """
    Processa TODO o historico em UMA unica UPDATE.
    Usa subquery correlacionada aninhada (mesmo padrao de calcular_acertos_inicial.py).
    """
    db = DatabaseConfig()
    print()
    print("=" * 70)
    print("PROCESSANDO ACERTOS 10 PARA TODO O HISTORICO...")
    print("=" * 70)
    print()
    print("  Isto executa UMA unica SQL que percorre todas as")
    print("  combinacoes x concursos. Pode levar alguns minutos.")
    print("  Nao interrompa.")
    print()

    # SQL unica: para cada combinacao, conta concursos com exatamente 10 acertos
    # e encontra o ultimo concurso onde isso ocorreu.
    # Usa subqueries correlacionadas separadas para COUNT e MAX (SQL Server nao permite
    # agregacao sobre subquery dentro de agregacao).
    sql_update = """
    UPDATE c
    SET
        Acertos_10 = (
            SELECT COUNT_BIG(*)
            FROM Resultados_INT r
            WHERE (
                SELECT COUNT_BIG(*)
                FROM (VALUES (c.N1),(c.N2),(c.N3),(c.N4),(c.N5),
                            (c.N6),(c.N7),(c.N8),(c.N9),(c.N10),
                            (c.N11),(c.N12),(c.N13),(c.N14),(c.N15)) AS comb(numero)
                WHERE numero IN (r.N1, r.N2, r.N3, r.N4, r.N5,
                                r.N6, r.N7, r.N8, r.N9, r.N10,
                                r.N11, r.N12, r.N13, r.N14, r.N15)
            ) = 10
        ),
        Ultimo_Acertos_10 = (
            SELECT MAX(r.Concurso)
            FROM Resultados_INT r
            WHERE (
                SELECT COUNT_BIG(*)
                FROM (VALUES (c.N1),(c.N2),(c.N3),(c.N4),(c.N5),
                            (c.N6),(c.N7),(c.N8),(c.N9),(c.N10),
                            (c.N11),(c.N12),(c.N13),(c.N14),(c.N15)) AS comb(numero)
                WHERE numero IN (r.N1, r.N2, r.N3, r.N4, r.N5,
                                r.N6, r.N7, r.N8, r.N9, r.N10,
                                r.N11, r.N12, r.N13, r.N14, r.N15)
            ) = 10
        )
    FROM COMBINACOES_LOTOFACIL c
    """

    inicio = datetime.now()

    try:
        ok = db.execute_command(sql_update)
        if not ok:
            print("ERRO: Falha na execucao da SQL.")
            return False

        tempo = (datetime.now() - inicio).total_seconds()
        print(f"Processamento concluido em {tempo:.0f}s ({tempo/60:.1f}min)")

        return True

    except Exception as e:
        print(f"ERRO: {e}")
        return False


def atualizar_controle():
    """Atualiza UltimoConcursoAtualizado para o concurso mais recente."""
    db = DatabaseConfig()
    db.execute_command("""
        UPDATE COMBINACOES_LOTOFACIL
        SET UltimoConcursoAtualizado = (SELECT MAX(Concurso) FROM Resultados_INT)
        WHERE UltimoConcursoAtualizado < (SELECT MAX(Concurso) FROM Resultados_INT)
    """)


def gerar_relatorio():
    """Gera ranking e estatisticas."""
    db = DatabaseConfig()
    print()
    print("=" * 70)
    print("RELATORIO DE ACERTOS 10")
    print("=" * 70)

    # Estatisticas descritivas
    stats = db.execute_query_dataframe("""
        SELECT
            COUNT(*) as total_comb,
            MIN(Acertos_10) as min_10,
            MAX(Acertos_10) as max_10,
            AVG(CAST(Acertos_10 AS FLOAT)) as avg_10,
            STDEV(CAST(Acertos_10 AS FLOAT)) as std_10,
            SUM(CASE WHEN Acertos_10 > 0 THEN 1 ELSE 0 END) as com_acerto
        FROM COMBINACOES_LOTOFACIL
    """).iloc[0]

    total_conc = db.execute_query_dataframe(
        "SELECT COUNT(*) FROM Resultados_INT"
    ).iloc[0, 0]

    ultimo_conc = db.execute_query_dataframe(
        "SELECT MAX(Concurso) FROM Resultados_INT"
    ).iloc[0, 0]

    print()
    print("VISAO GERAL:")
    print(f"  Total de combinacoes: {int(stats['total_comb']):,}")
    print(f"  Total de sorteios: {total_conc:,}")
    print(f"  Combinacoes com >=1 acerto 10: {int(stats['com_acerto']):,}  ({int(stats['com_acerto'])/int(stats['total_comb'])*100:.2f}%)")
    print(f"  Combinacoes SEM NENHUM acerto 10: {int(stats['total_comb']) - int(stats['com_acerto']):,} ({(int(stats['total_comb']) - int(stats['com_acerto']))/int(stats['total_comb'])*100:.2f}%)")

    print()
    print("ESTATISTICAS DESCRITIVAS (Acertos_10):")
    print(f"  Minimo: {int(stats['min_10'])}")
    print(f"  Maximo: {int(stats['max_10'])}")
    print(f"  Media: {stats['avg_10']:.4f}")
    print(f"  Desvio padrao: {stats['std_10']:.4f}")

    # Probabilidade teorica
    from math import comb
    prob_10 = comb(15, 10) * comb(10, 5) / comb(25, 15)
    freq_esperada = total_conc * prob_10
    print(f"  Prob. teorica 10 acertos/sorteio: {prob_10:.6f} ({prob_10*100:.4f}%)")
    print(f"  Frequencia esperada media: {freq_esperada:.2f}")
    print(f"  Frequencia observada media: {stats['avg_10']:.4f}")

    # Atraso medio
    atraso = db.execute_query_dataframe(f"""
        SELECT
            AVG(CAST({ultimo_conc} - Ultimo_Acertos_10 AS FLOAT)) as media_atraso,
            MAX({ultimo_conc} - Ultimo_Acertos_10) as max_atraso
        FROM COMBINACOES_LOTOFACIL
        WHERE Acertos_10 > 0 AND Ultimo_Acertos_10 IS NOT NULL
    """).iloc[0]

    media_atr = atraso['media_atraso']
    max_atr = atraso['max_atraso']
    if media_atr is not None:
        print(f"  Atraso medio (ult 10): {float(media_atr):.1f} concursos")
        print(f"  Atraso maximo: {int(max_atr)} concursos")
    else:
        print("  Atraso: sem dados (nenhum acerto 10 registrado)")

    # TOP 30
    print()
    print("=" * 70)
    print("TOP 30 COMBINACOES COM MAIS ACERTOS 10")
    print("=" * 70)
    print(f"{'ID':>8} {'Combinacao':<50} {'10ac':>6} {'11ac':>6} {'12ac':>6} {'Ult10':>7}")
    print("-" * 85)

    top30 = db.execute_query_dataframe("""
        SELECT TOP 30
            ID, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
            Acertos_10, Acertos_11, Acertos_12, Ultimo_Acertos_10
        FROM COMBINACOES_LOTOFACIL
        ORDER BY Acertos_10 DESC
    """)

    for _, row in top30.iterrows():
        nums = ' '.join(f"{int(row[f'N{j}']):02d}" for j in range(1, 16))
        ult10 = int(row['Ultimo_Acertos_10']) if row['Ultimo_Acertos_10'] is not None else 0
        print(f"{int(row['ID']):>8} {nums:<50} {int(row['Acertos_10']):>6} {int(row['Acertos_11']):>6} {int(row['Acertos_12']):>6} {ult10:>7}")

    # TOP 20 atrasadas
    print()
    print("=" * 70)
    print("TOP 20 MAIS ATRASADAS (ja acertaram 10 mas ha mais tempo sem)")
    print("=" * 70)
    print(f"{'ID':>8} {'Combinacao':<50} {'10ac':>6} {'Atraso':>7} {'Ult10':>7}")
    print("-" * 78)

    atrasadas = db.execute_query_dataframe(f"""
        SELECT TOP 20
            ID, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
            Acertos_10, Ultimo_Acertos_10,
            ({ultimo_conc} - Ultimo_Acertos_10) as atraso
        FROM COMBINACOES_LOTOFACIL
        WHERE Acertos_10 > 0 AND Ultimo_Acertos_10 IS NOT NULL
        ORDER BY atraso DESC
    """)

    for _, row in atrasadas.iterrows():
        nums = ' '.join(f"{int(row[f'N{j}']):02d}" for j in range(1, 16))
        ult10 = int(row['Ultimo_Acertos_10']) if row['Ultimo_Acertos_10'] is not None else 0
        print(f"{int(row['ID']):>8} {nums:<50} {int(row['Acertos_10']):>6} {int(row['atraso']):>7} {ult10:>7}")

    # Score combinado
    print()
    print("=" * 70)
    print("TOP 20 SCORE COMBINADO (frequencia + atraso normalizados)")
    print("=" * 70)

    media_10 = db.execute_query_dataframe(
        "SELECT AVG(CAST(Acertos_10 AS FLOAT)) FROM COMBINACOES_LOTOFACIL WHERE Acertos_10 > 0"
    ).iloc[0, 0]

    media_atraso = db.execute_query_dataframe(f"""
        SELECT AVG(CAST({ultimo_conc} - Ultimo_Acertos_10 AS FLOAT))
        FROM COMBINACOES_LOTOFACIL WHERE Acertos_10 > 0 AND Ultimo_Acertos_10 IS NOT NULL
    """).iloc[0, 0]

    if media_10 and media_atraso:
        print(f"{'ID':>8} {'Combinacao':<50} {'10ac':>6} {'Score':>7}")
        print("-" * 73)
        score_data = db.execute_query_dataframe(f"""
            SELECT TOP 20
                ID, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
                Acertos_10, Ultimo_Acertos_10,
                (CAST(Acertos_10 AS FLOAT) / {media_10}) +
                (CAST({ultimo_conc} - Ultimo_Acertos_10 AS FLOAT) / {media_atraso}) AS score
            FROM COMBINACOES_LOTOFACIL
            WHERE Acertos_10 > 0 AND Ultimo_Acertos_10 IS NOT NULL
            ORDER BY score DESC
        """)
        for _, row in score_data.iterrows():
            nums = ' '.join(f"{int(row[f'N{j}']):02d}" for j in range(1, 16))
            print(f"{int(row['ID']):>8} {nums:<50} {int(row['Acertos_10']):>6} {row['score']:>7.2f}")

    # Distribuicao
    print()
    print("=" * 70)
    print("DISTRIBUICAO DE FREQUENCIA (quantas combinacoes tem X acertos 10)")
    print("=" * 70)
    print(f"{'Acertos_10':>10} {'Combinacoes':>12} {'%':>8} {'Acumulado':>10}")
    print("-" * 42)

    dist = db.execute_query_dataframe("""
        SELECT Acertos_10, COUNT(*) as qtd
        FROM COMBINACOES_LOTOFACIL
        GROUP BY Acertos_10
        ORDER BY Acertos_10
    """)

    total = 3268760
    acum = 0
    for _, row in dist.iterrows():
        ac = int(row['Acertos_10'])
        qtd = int(row['qtd'])
        pct = qtd / total * 100
        acum += pct
        if pct > 0.01:
            bar = '*' * max(1, int(pct))
        else:
            bar = ''
        print(f"{ac:>10} {qtd:>12,} {pct:>7.3f}% {acum:>9.1f}% {bar}")


def main():
    print()
    print("=" * 70)
    print("POC: ANALISE DE ACERTOS 10 - COMBINACOES_LOTOFACIL")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    db = DatabaseConfig()
    if not db.test_connection():
        print("ERRO: Nao foi possivel conectar ao banco.")
        sys.exit(1)

    # 1. Colunas
    if not verificar_estrutura():
        print()
        print("Colunas Acertos_10 nao encontradas. Adicionando...")
        adicionar_colunas()
        if not verificar_estrutura():
            print("ERRO: Nao foi possivel criar as colunas.")
            sys.exit(1)
    else:
        print("Colunas Acertos_10 ja existem.")

    # 2. Estatisticas
    stats = obter_estatisticas()

    # 3. Processamento (opcional --full)
    if '--full' in sys.argv or os.environ.get('AGF_MODE') == 'live':
        if stats and stats['tempo_estimado'] > 3600:
            print()
            print(f"ATENCAO: Tempo estimado > {stats['tempo_estimado']/3600:.0f}h")
            if '--force' not in sys.argv:
                print("Use --force para confirmar, ou rode sem --full para relatorio rapido.")
                sys.exit(0)
        zerar_contagens()
        ok = processar_acertos_historico()
        if ok:
            atualizar_controle()
            print("Controle de atualizacao registrado.")
    else:
        print()
        print("Modo relatorio rapido (sem --full).")
        print("Para processar TODO o historico (~6.8h estimado): python poc_acertos_10.py --full")
        print()

    # 4. Relatorio
    gerar_relatorio()

    print()
    print("=" * 70)
    print("POC CONCLUIDA!")
    print("=" * 70)


if __name__ == "__main__":
    main()
