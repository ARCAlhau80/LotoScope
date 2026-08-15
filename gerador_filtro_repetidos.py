import pyodbc
import random
from collections import Counter
from itertools import combinations
from statistics import mean

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)


def contar_acertos(jogo, resultado):
    return len(set(jogo) & set(resultado))


def gerar_jogos_filtro(anterior, n_repetidos=8, n_jogos=10, estrategia='frios'):
    """
    Gera jogos escolhendo n_repetidos do concurso anterior e completando com numeros
    que nao sairam (frios) ou aleatorios.
    """
    todos = set(range(1, 26))
    anterior_set = set(anterior)
    nao_sorteados = sorted(todos - anterior_set)
    jogos = []
    for _ in range(n_jogos):
        repetidos = random.sample(sorted(anterior_set), n_repetidos)
        if estrategia == 'frios':
            # Complementa com os nao sorteados anteriores (aleatoriamente)
            restante = random.sample(nao_sorteados, 15 - n_repetidos)
        else:
            # Complementa aleatoriamente de todo o universo exceto os ja escolhidos
            disponiveis = sorted(todos - set(repetidos))
            restante = random.sample(disponiveis, 15 - n_repetidos)
        jogo = sorted(repetidos + restante)
        jogos.append(jogo)
    return jogos


def backtest(sorteios, n_repetidos=8, n_jogos=10, estrategia='frios'):
    """
    sorteios: lista de tuplas (concurso, set de 15 numeros)
    Retorna media de acertos por concurso testado.
    """
    resultados = []
    for i in range(len(sorteios) - 1):
        concurso_atual, resultado_atual = sorteios[i]
        _, resultado_proximo = sorteios[i + 1]
        jogos = gerar_jogos_filtro(
            list(resultado_atual),
            n_repetidos=n_repetidos,
            n_jogos=n_jogos,
            estrategia=estrategia,
        )
        acertos = [contar_acertos(j, list(resultado_proximo)) for j in jogos]
        resultados.append({
            'concurso': sorteios[i + 1][0],
            'acertos': acertos,
            'max': max(acertos),
            'mean': mean(acertos),
        })
    return resultados


def baseline_aleatorio(sorteios, n_jogos=10):
    """Gera jogos totalmente aleatorios como comparacao."""
    todos = list(range(1, 26))
    resultados = []
    for i in range(len(sorteios) - 1):
        _, resultado_proximo = sorteios[i + 1]
        acertos = []
        for _ in range(n_jogos):
            jogo = sorted(random.sample(todos, 15))
            acertos.append(contar_acertos(jogo, list(resultado_proximo)))
        resultados.append({
            'concurso': sorteios[i + 1][0],
            'acertos': acertos,
            'max': max(acertos),
            'mean': mean(acertos),
        })
    return resultados


def distribuicao_maximos(resultados):
    maximos = [r['max'] for r in resultados]
    c = Counter(maximos)
    total = len(maximos)
    return {k: {'count': c[k], 'pct': f"{c[k]/total*100:.2f}%"} for k in sorted(c.keys())}


def main():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
    rows = cur.fetchall()
    sorteios = [(r[0], set(r[1:16])) for r in rows]
    print(f"Sorteios carregados: {len(sorteios)}")

    n_jogos = 20

    # Baseline aleatorio
    print(f"\n=== BASELINE ALEATORIO ({n_jogos} jogos/concurso) ===")
    res_base = baseline_aleatorio(sorteios, n_jogos=n_jogos)
    print(f"Media do maximo acerto: {mean([r['max'] for r in res_base]):.2f}")
    print(f"Distribuicao dos maximos: {distribuicao_maximos(res_base)}")

    # Filtro 8 +/- 1 com preenchimento por numeros nao sorteados (frios)
    for n_rep in [7, 8, 9]:
        print(f"\n=== FILTRO: repetir {n_rep} do anterior + frios ({n_jogos} jogos/concurso) ===")
        res = backtest(sorteios, n_repetidos=n_rep, n_jogos=n_jogos, estrategia='frios')
        print(f"Media do maximo acerto: {mean([r['max'] for r in res]):.2f}")
        print(f"Distribuicao dos maximos: {distribuicao_maximos(res)}")

    # Filtro 8 +/- 1 com preenchimento aleatorio (repetidos forcam correlacao)
    for n_rep in [7, 8, 9]:
        print(f"\n=== FILTRO: repetir {n_rep} do anterior + aleatorio ({n_jogos} jogos/concurso) ===")
        res = backtest(sorteios, n_repetidos=n_rep, n_jogos=n_jogos, estrategia='aleatorio')
        print(f"Media do maximo acerto: {mean([r['max'] for r in res]):.2f}")
        print(f"Distribuicao dos maximos: {distribuicao_maximos(res)}")

    # Melhor estrategia detalhada
    print("\n=== DETALHAMENTO: repetir 8 + frios ===")
    res_8_frios = backtest(sorteios, n_repetidos=8, n_jogos=n_jogos, estrategia='frios')
    # Estatisticas de acerto 11, 12, 13, 14, 15 considerando todos os jogos gerados
    todos_acertos = []
    for r in res_8_frios:
        todos_acertos.extend(r['acertos'])
    dist = Counter(todos_acertos)
    total = len(todos_acertos)
    print("Distribuicao de todos os acertos:")
    for k in sorted(dist.keys()):
        print(f"  {k} acertos: {dist[k]} ({dist[k]/total*100:.2f}%)")


if __name__ == "__main__":
    main()
