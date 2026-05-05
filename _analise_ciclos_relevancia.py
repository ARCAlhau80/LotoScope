"""
Análise histórica: relevância da tabela NumerosCiclos para
escolha de números a EXCLUIR ou FIXAR no Pool 23.

Hipóteses testadas:
  H1: Números com QtdSorteados=0 no ciclo atual → mais prováveis de SAIR
       (ciclo precisa ser fechado, esse número está "devendo")
  H2: Números mais sorteados no ciclo atual → menos prováveis de sair
       (já pagaram sua cota, tendência de resfriamento)
  H3: Posição no ciclo (quantos concursos já se passaram / média do ciclo)
       influencia a probabilidade de saída

Para cada concurso, usando dados do ciclo vigente NAQUELE MOMENTO, 
verifica se:
  - Os números com QtdSorteados=0 do ciclo saíram mais que esperado
  - Os números mais sorteados do ciclo saíram menos que esperado
  - Isso gerou acerto de exclusão melhor que aleatório

Resultado esperado: se H1 ou H2 são válidas, o sinal é um feature valioso
para a rede neural.
"""

import pyodbc
from collections import defaultdict

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def main():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()

    # ---- 1. Carregar todos os resultados históricos ordenados ----
    cur.execute("""
        SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
        FROM Resultados_INT
        ORDER BY Concurso
    """)
    resultados = {}
    for row in cur.fetchall():
        c = row[0]
        resultados[c] = set(row[1:])

    concursos = sorted(resultados.keys())
    print(f"Concursos carregados: {concursos[0]} → {concursos[-1]} ({len(concursos)} total)")

    # ---- 2. Carregar todos os ciclos ----
    cur.execute("""
        SELECT Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento
        FROM NumerosCiclos
        ORDER BY Ciclo, Numero
    """)
    ciclos_raw = cur.fetchall()

    # Indexar ciclos por número: {concurso_inicio: {numero: qtd}}
    ciclos_por_concurso_inicio = defaultdict(dict)
    ciclo_info = {}  # {ciclo: (concurso_inicio, concurso_fechamento)}
    for row in ciclos_raw:
        ciclo, num, qtd, ini, fim = row
        ciclos_por_concurso_inicio[ini][num] = qtd
        ciclo_info[ciclo] = (ini, fim)

    # Para dado concurso X: qual é o ciclo vigente?
    # ciclo vigente = ciclo cujo ConcursoInicio <= X e ConcursoFechamento >= X (ou NULL)
    ciclos_lista = []
    for ciclo, (ini, fim) in sorted(ciclo_info.items()):
        ciclos_lista.append((ciclo, ini, fim))

    def get_ciclo_vigente(concurso):
        """Retorna (ciclo_num, inicio, fim) do ciclo vigente naquele concurso"""
        for ciclo, ini, fim in reversed(ciclos_lista):
            if ini <= concurso:
                if fim is None or fim >= concurso:
                    return ciclo, ini, fim
        return None, None, None

    def get_qtd_ciclo_ate(ciclo_inicio, concurso_atual):
        """
        Para o ciclo vigente, retorna {numero: qtd_sorteados}
        contando apenas concursos ANTERIORES ao atual (não inclui o atual).
        """
        qtd = defaultdict(int)
        for c in concursos:
            if c >= ciclo_inicio and c < concurso_atual:
                for n in resultados[c]:
                    qtd[n] += 1
        return qtd

    # ---- 3. Para cada concurso (a partir do 100), analisar ----
    print("\nAnalisando concursos...")

    # Métricas acumuladas
    stats_h1 = {'acertos': 0, 'total': 0}   # excluir números c/ qtd=0 (pendentes)
    stats_h2 = {'acertos': 0, 'total': 0}   # excluir números c/ qtd máximo (quentes no ciclo)
    stats_rand = {'acertos': 0, 'total': 0} # baseline aleatório

    # Detalhe: distribuição de saída por qtd_no_ciclo
    saiu_por_qtd = defaultdict(int)
    total_por_qtd = defaultdict(int)

    # Posição no ciclo vs saída
    saiu_por_posicao_ciclo = defaultdict(int)
    total_por_posicao_ciclo = defaultdict(int)

    # Média de concursos por ciclo (histórico)
    tamanhos_ciclos = []
    for ciclo, (ini, fim) in ciclo_info.items():
        if fim is not None:
            tamanhos_ciclos.append(fim - ini + 1)
    media_ciclo = sum(tamanhos_ciclos) / len(tamanhos_ciclos) if tamanhos_ciclos else 5

    print(f"Média de concursos por ciclo: {media_ciclo:.2f}")

    import random
    random.seed(42)

    concursos_analisados = 0
    for idx, conc in enumerate(concursos):
        if conc < 500:  # pular primeiros para ter histórico
            continue

        ciclo_num, ini, fim = get_ciclo_vigente(conc)
        if ini is None:
            continue

        # Quantos concursos já se passaram neste ciclo (ANTES deste)
        concursos_no_ciclo_antes = conc - ini  # quantidade de sorteios já feitos no ciclo

        # Qtd de cada número no ciclo ATÉ AGORA (antes deste concurso)
        qtd_ciclo = get_qtd_ciclo_ate(ini, conc)

        # Números com qtd=0 (nunca saíram neste ciclo ainda)
        pendentes = [n for n in range(1, 26) if qtd_ciclo[n] == 0]
        # Números mais quentes do ciclo
        max_qtd = max(qtd_ciclo[n] for n in range(1, 26)) if any(qtd_ciclo.values()) else 0
        mais_quentes = [n for n in range(1, 26) if qtd_ciclo[n] == max_qtd and max_qtd > 0]

        resultado_real = resultados[conc]

        # -- H1: números pendentes saem mais? --
        for n in range(1, 26):
            qtd_n = qtd_ciclo[n]
            saiu = 1 if n in resultado_real else 0
            saiu_por_qtd[qtd_n] += saiu
            total_por_qtd[qtd_n] += 1

        # Posição no ciclo (normalizada 0-1)
        posicao_norm = min(concursos_no_ciclo_antes / max(1, media_ciclo), 1.0)
        posicao_bucket = round(posicao_norm * 5) / 5  # buckets de 0.2
        for n in range(1, 26):
            if n in resultado_real:
                saiu_por_posicao_ciclo[posicao_bucket] += 1
            total_por_posicao_ciclo[posicao_bucket] += 1

        # -- H2: excluir os 2 mais quentes do ciclo --
        if mais_quentes and len(mais_quentes) >= 2:
            excluidos_h2 = sorted(mais_quentes, key=lambda n: qtd_ciclo[n], reverse=True)[:2]
            acertou = all(n not in resultado_real for n in excluidos_h2)
            stats_h2['acertos'] += int(acertou)
            stats_h2['total'] += 1

        # -- Baseline aleatório --
        excluidos_rand = random.sample(range(1, 26), 2)
        acertou_rand = all(n not in resultado_real for n in excluidos_rand)
        stats_rand['acertos'] += int(acertou_rand)
        stats_rand['total'] += 1

        concursos_analisados += 1
        if concursos_analisados % 500 == 0:
            print(f"  Processado: {conc} ({concursos_analisados} concursos)...")

    # ---- 4. Resultados ----
    print("\n" + "=" * 65)
    print("H1: PROBABILIDADE DE SAIR por QtdSorteados no ciclo atual")
    print("=" * 65)
    print(f"{'QtdCiclo':>8} | {'P(sair)':>8} | {'Total obs':>10} | {'vs Esperado':>12}")
    print("-" * 50)
    expected = 15 / 25  # = 0.60
    for qtd in sorted(saiu_por_qtd.keys()):
        tot = total_por_qtd[qtd]
        p = saiu_por_qtd[qtd] / tot if tot > 0 else 0
        diff = p - expected
        sinal = "▲" if diff > 0.02 else ("▼" if diff < -0.02 else "~")
        print(f"  {qtd:>6}   | {p:>7.1%} | {tot:>10} | {diff:>+10.1%}  {sinal}")

    print("\n" + "=" * 65)
    print("H2: ACERTO DE EXCLUSÃO — excluir os 2 MAIS QUENTES do ciclo")
    print("=" * 65)
    if stats_h2['total'] > 0:
        taxa_h2 = stats_h2['acertos'] / stats_h2['total']
        taxa_rand = stats_rand['acertos'] / stats_rand['total']
        print(f"  Taxa H2 (mais quentes do ciclo): {taxa_h2:.1%} ({stats_h2['acertos']}/{stats_h2['total']})")
        print(f"  Taxa Aleatório (baseline):        {taxa_rand:.1%} ({stats_rand['acertos']}/{stats_rand['total']})")
        print(f"  Diferença:                        {taxa_h2-taxa_rand:+.1%}")
        if taxa_h2 > taxa_rand + 0.01:
            print("  ✅ Ciclo QUENTE melhora exclusão!")
        elif taxa_h2 < taxa_rand - 0.01:
            print("  ❌ Ciclo QUENTE piora exclusão!")
        else:
            print("  ~ Neutro (sem ganho significativo)")

    print("\n" + "=" * 65)
    print("H3: Posição no ciclo (0=início, 1=fim) vs P(sair)")
    print("=" * 65)
    print(f"{'Posição':>8} | {'P(sair)':>8} | {'Total obs':>10}")
    print("-" * 38)
    for pos in sorted(saiu_por_posicao_ciclo.keys()):
        tot = total_por_posicao_ciclo[pos]
        p = saiu_por_posicao_ciclo[pos] / tot if tot > 0 else 0
        print(f"  {pos:>6.1f}   | {p:>7.1%} | {tot:>10}")

    conn.close()

if __name__ == "__main__":
    main()
