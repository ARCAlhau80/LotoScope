import pyodbc
import random
from collections import Counter
from statistics import mean

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)


def contar_acertos(jogo, resultado):
    return len(set(jogo) & set(resultado))


def gerar_jogos_intersecao(anterior, anterior2, n_jogos=10, complemento='frios'):
    """
    Usa numeros que se repetiram nos 2 ultimos sorteios (intersecao anterior & anterior2)
    como base e complementa ate 15.
    """
    todos = set(range(1, 26))
    base = set(anterior) & set(anterior2)
    base_list = sorted(base)
    n_base = len(base_list)
    nao_sorteados_recentes = sorted(todos - (set(anterior) | set(anterior2)))

    jogos = []
    for _ in range(n_jogos):
        if n_base >= 15:
            jogo = sorted(random.sample(base_list, 15))
        else:
            fixos = base_list[:]
            faltam = 15 - n_base
            if complemento == 'frios':
                # Usa numeros que nao sairam nos 2 ultimos
                pool = nao_sorteados_recentes if len(nao_sorteados_recentes) >= faltam else sorted(todos - set(fixos))
            elif complemento == 'aleatorio':
                pool = sorted(todos - set(fixos))
            else:
                pool = sorted(todos - set(fixos))
            restante = random.sample(pool, faltam)
            jogo = sorted(fixos + restante)
        jogos.append(jogo)
    return jogos


def gerar_jogos_uniao(anterior, anterior2, n_jogos=10, n_fixos=None):
    """
    Usa a uniao dos 2 ultimos sorteios. Se n_fixos for None, usa toda a uniao (ate 25 numeros).
    Sorteia 15 dessa uniao quando houver mais de 15.
    """
    todos = set(range(1, 26))
    uniao = sorted(set(anterior) | set(anterior2))
    jogos = []
    for _ in range(n_jogos):
        if len(uniao) >= 15:
            jogo = sorted(random.sample(uniao, 15))
        else:
            resto = sorted(todos - set(uniao))
            jogo = sorted(uniao + random.sample(resto, 15 - len(uniao)))
        jogos.append(jogo)
    return jogos


def backtest_intersecao(sorteios, n_jogos=10, complemento='frios'):
    resultados = []
    for i in range(2, len(sorteios)):
        anterior2 = sorteios[i - 2][1]
        anterior = sorteios[i - 1][1]
        resultado_atual = sorteios[i][1]
        jogos = gerar_jogos_intersecao(
            list(anterior),
            list(anterior2),
            n_jogos=n_jogos,
            complemento=complemento,
        )
        acertos = [contar_acertos(j, list(resultado_atual)) for j in jogos]
        base = set(anterior) & set(anterior2)
        resultados.append({
            'concurso': sorteios[i][0],
            'base_size': len(base),
            'acertos': acertos,
            'max': max(acertos),
            'mean': mean(acertos),
        })
    return resultados


def backtest_uniao(sorteios, n_jogos=10):
    resultados = []
    for i in range(2, len(sorteios)):
        anterior2 = sorteios[i - 2][1]
        anterior = sorteios[i - 1][1]
        resultado_atual = sorteios[i][1]
        jogos = gerar_jogos_uniao(list(anterior), list(anterior2), n_jogos=n_jogos)
        uniao = set(anterior) | set(anterior2)
        acertos = [contar_acertos(j, list(resultado_atual)) for j in jogos]
        resultados.append({
            'concurso': sorteios[i][0],
            'base_size': len(uniao),
            'acertos': acertos,
            'max': max(acertos),
            'mean': mean(acertos),
        })
    return resultados


def backtest_aleatorio(sorteios, n_jogos=10):
    todos = list(range(1, 26))
    resultados = []
    for i in range(2, len(sorteios)):
        resultado_atual = sorteios[i][1]
        acertos = []
        for _ in range(n_jogos):
            jogo = sorted(random.sample(todos, 15))
            acertos.append(contar_acertos(jogo, list(resultado_atual)))
        resultados.append({
            'concurso': sorteios[i][0],
            'base_size': 0,
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


def distribuicao_tamanho_base(resultados):
    sizes = [r['base_size'] for r in resultados]
    c = Counter(sizes)
    total = len(sizes)
    return {k: {'count': c[k], 'pct': f"{c[k]/total*100:.2f}%"} for k in sorted(c.keys())}


def main():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
    rows = cur.fetchall()
    sorteios = [(r[0], set(r[1:16])) for r in rows]
    print(f"Sorteios carregados: {len(sorteios)}")

    n_jogos = 20

    print(f"\n=== BASELINE ALEATORIO ({n_jogos} jogos/concurso) ===")
    res_base = backtest_aleatorio(sorteios, n_jogos=n_jogos)
    print(f"Media do maximo acerto: {mean([r['max'] for r in res_base]):.2f}")
    print(f"Distribuicao dos maximos: {distribuicao_maximos(res_base)}")

    print(f"\n=== INTERSECAO 2 ULTIMOS + frios ({n_jogos} jogos/concurso) ===")
    res_int_frios = backtest_intersecao(sorteios, n_jogos=n_jogos, complemento='frios')
    print(f"Tamanho medio da intersecao: {mean([r['base_size'] for r in res_int_frios]):.2f}")
    print(f"Distribuicao do tamanho da intersecao: {distribuicao_tamanho_base(res_int_frios)}")
    print(f"Media do maximo acerto: {mean([r['max'] for r in res_int_frios]):.2f}")
    print(f"Distribuicao dos maximos: {distribuicao_maximos(res_int_frios)}")

    print(f"\n=== INTERSECAO 2 ULTIMOS + aleatorio ({n_jogos} jogos/concurso) ===")
    res_int_ale = backtest_intersecao(sorteios, n_jogos=n_jogos, complemento='aleatorio')
    print(f"Tamanho medio da intersecao: {mean([r['base_size'] for r in res_int_ale]):.2f}")
    print(f"Media do maximo acerto: {mean([r['max'] for r in res_int_ale]):.2f}")
    print(f"Distribuicao dos maximos: {distribuicao_maximos(res_int_ale)}")

    print(f"\n=== UNIAO 2 ULTIMOS ({n_jogos} jogos/concurso) ===")
    res_uniao = backtest_uniao(sorteios, n_jogos=n_jogos)
    print(f"Tamanho medio da uniao: {mean([r['base_size'] for r in res_uniao]):.2f}")
    print(f"Distribuicao do tamanho da uniao: {distribuicao_tamanho_base(res_uniao)}")
    print(f"Media do maximo acerto: {mean([r['max'] for r in res_uniao]):.2f}")
    print(f"Distribuicao dos maximos: {distribuicao_maximos(res_uniao)}")

    # Analise: quando a intersecao e pequena (3-6 numeros), o desempenho melhora?
    print("\n=== INTERSECAO PEQUENA (3-6 numeros) + frios ===")
    filtrado = [r for r in res_int_frios if 3 <= r['base_size'] <= 6]
    print(f"Ocorrencias: {len(filtrado)}")
    if filtrado:
        print(f"Media do maximo acerto: {mean([r['max'] for r in filtrado]):.2f}")
        print(f"Distribuicao dos maximos: {distribuicao_maximos(filtrado)}")

    print("\n=== INTERSECAO GRANDE (7-10 numeros) + frios ===")
    filtrado = [r for r in res_int_frios if 7 <= r['base_size'] <= 10]
    print(f"Ocorrencias: {len(filtrado)}")
    if filtrado:
        print(f"Media do maximo acerto: {mean([r['max'] for r in filtrado]):.2f}")
        print(f"Distribuicao dos maximos: {distribuicao_maximos(filtrado)}")


if __name__ == "__main__":
    main()
