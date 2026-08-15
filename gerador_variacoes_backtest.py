import pyodbc
import random
import json
from collections import Counter, defaultdict
from statistics import mean

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}


def contar_acertos(jogo, resultado):
    return len(set(jogo) & set(resultado))


def gerar_jogo_aleatorio(pool, k=15):
    return sorted(random.sample(pool, k))


# ============ ESTRATEGIAS ============

def estrategia_hot_last_n(sorteios, idx_atual, n_concursos=2, n_jogos=20):
    """Numeros que sairam nos ultimos n concursos."""
    hot = set()
    for j in range(1, n_concursos + 1):
        if idx_atual - j >= 0:
            hot |= sorteios[idx_atual - j][1]
    hot = sorted(hot)
    todos = list(range(1, 26))
    jogos = []
    for _ in range(n_jogos):
        if len(hot) >= 15:
            jogo = sorted(random.sample(hot, 15))
        else:
            resto = sorted(set(todos) - set(hot))
            jogo = sorted(random.sample(hot, len(hot)) + random.sample(resto, 15 - len(hot)))
        jogos.append(jogo)
    return jogos


def estrategia_hot_weighted(sorteios, idx_atual, n_jogos=20):
    """Peso decrescente: ultimo=3, anterior=2, antepenultimo=1."""
    pesos = []
    for j in range(1, 4):
        if idx_atual - j >= 0:
            pesos.append((sorteios[idx_atual - j][1], 4 - j))
    contagem = defaultdict(int)
    for nums, peso in pesos:
        for n in nums:
            contagem[n] += peso
    # Ordena por peso, pega top 15 como base, mas permite mistura
    ranking = sorted(contagem.keys(), key=lambda x: contagem[x], reverse=True)
    top = ranking[:15] if len(ranking) >= 15 else ranking
    todos = list(range(1, 26))
    jogos = []
    for _ in range(n_jogos):
        if len(top) >= 15:
            jogo = sorted(random.sample(top, 15))
        else:
            resto = sorted(set(todos) - set(top))
            jogo = sorted(random.sample(top, len(top)) + random.sample(resto, 15 - len(top)))
        jogos.append(jogo)
    return jogos


def estrategia_posicional(sorteios, idx_atual, n_jogos=20):
    """Tenta repetir numeros na mesma posicao do concurso anterior."""
    if idx_atual - 1 < 0:
        return []
    anterior = sorted(sorteios[idx_atual - 1][1])
    todos = list(range(1, 26))
    jogos = []
    for _ in range(n_jogos):
        # Escolhe 5-10 posicoes para fixar o numero anterior
        n_fixos = random.randint(5, 10)
        fixos = set(random.sample(anterior, n_fixos))
        resto = sorted(set(todos) - fixos)
        jogo = sorted(fixos | set(random.sample(resto, 15 - len(fixos))))
        jogos.append(jogo)
    return jogos


def estrategia_posicional_fixo(sorteios, idx_atual, n_fixos=8, n_jogos=20):
    """Fixa n_fixos numeros do concurso anterior em posicoes aleatorias."""
    if idx_atual - 1 < 0:
        return []
    anterior = sorted(sorteios[idx_atual - 1][1])
    todos = list(range(1, 26))
    jogos = []
    for _ in range(n_jogos):
        fixos = set(random.sample(anterior, n_fixos))
        resto = sorted(set(todos) - fixos)
        jogo = sorted(fixos | set(random.sample(resto, 15 - len(fixos))))
        jogos.append(jogo)
    return jogos


def estrategia_persistencia_categoria(sorteios, idx_atual, categoria='pares', n_jogos=20):
    """Se a categoria teve alta repeticao entre n-2 e n-1, forca mais dessa categoria."""
    if idx_atual - 2 < 0:
        return []
    anterior = sorteios[idx_atual - 1][1]
    anterior2 = sorteios[idx_atual - 2][1]
    todos = list(range(1, 26))

    if categoria == 'pares':
        cat_func = lambda x: x % 2 == 0
    elif categoria == 'impares':
        cat_func = lambda x: x % 2 == 1
    elif categoria == 'primos':
        cat_func = lambda x: x in PRIMOS
    elif categoria == 'fibonacci':
        cat_func = lambda x: x in FIBONACCI
    elif categoria == 'baixos':
        cat_func = lambda x: x <= 13
    elif categoria == 'altos':
        cat_func = lambda x: x >= 14
    else:
        cat_func = lambda x: x % 2 == 0

    cat_anterior = {n for n in anterior if cat_func(n)}
    cat_anterior2 = {n for n in anterior2 if cat_func(n)}
    repeticao_cat = len(cat_anterior & cat_anterior2)
    total_cat = max(len(cat_anterior), len(cat_anterior2))
    taxa = repeticao_cat / total_cat if total_cat > 0 else 0.5

    pool_cat = sorted({n for n in todos if cat_func(n)})
    outros = sorted({n for n in todos if not cat_func(n)})
    max_cat = len(pool_cat)

    jogos = []
    for _ in range(n_jogos):
        # Se taxa alta (>0.5), usa mais da categoria; se baixa, usa menos
        if taxa > 0.5:
            n_cat = min(random.randint(7, 10), max_cat)
        else:
            n_cat = min(random.randint(4, 6), max_cat)
        jogo = sorted(random.sample(pool_cat, n_cat) + random.sample(outros, 15 - n_cat))
        jogos.append(jogo)
    return jogos


def estrategia_combinada(sorteios, idx_atual, n_jogos=20):
    """Combina: 5-8 do ultimo, 2-4 do antepenultimo, 1-3 nunca sorteados recentes, resto aleatorio."""
    todos = list(range(1, 26))
    if idx_atual - 1 < 0:
        return []
    ultimo = sorteios[idx_atual - 1][1]
    hot = set()
    for j in range(1, min(4, idx_atual + 1)):
        hot |= sorteios[idx_atual - j][1]
    nao_recentes = sorted(set(todos) - hot)
    jogos = []
    for _ in range(n_jogos):
        n_ultimo = random.randint(5, 8)
        fixos = set(random.sample(sorted(ultimo), n_ultimo))
        n_frios = random.randint(1, 3)
        if len(nao_recentes) >= n_frios:
            fixos |= set(random.sample(nao_recentes, n_frios))
        resto = sorted(set(todos) - fixos)
        jogo = sorted(fixos | set(random.sample(resto, 15 - len(fixos))))
        jogos.append(jogo)
    return jogos


def estrategia_frequencia_historica(sorteios, idx_atual, n_jogos=20):
    """Usa os 15 numeros mais frequentes em toda a historia ATE o concurso anterior."""
    freq = defaultdict(int)
    for j in range(idx_atual):
        for n in sorteios[j][1]:
            freq[n] += 1
    ranking = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
    top = ranking[:15]
    todos = list(range(1, 26))
    jogos = []
    for _ in range(n_jogos):
        # Mistura top com alguns aleatorios
        n_top = random.randint(8, 12)
        fixos = random.sample(top, n_top)
        resto = sorted(set(todos) - set(fixos))
        jogo = sorted(fixos + random.sample(resto, 15 - n_top))
        jogos.append(jogo)
    return jogos


def estrategia_atraso_historico(sorteios, idx_atual, n_jogos=20):
    """Usa numeros com maior atraso (nao sairam recentemente)."""
    ultimos_concursos = 5
    todos = set(range(1, 26))
    recentes = set()
    for j in range(1, min(ultimos_concursos + 1, idx_atual + 1)):
        recentes |= sorteios[idx_atual - j][1]
    atrasados = sorted(todos - recentes)
    # Se muito poucos, aumenta janela
    if len(atrasados) < 15:
        recentes = set()
        for j in range(1, min(10 + 1, idx_atual + 1)):
            recentes |= sorteios[idx_atual - j][1]
        atrasados = sorted(todos - recentes)
    max_atrasados = len(atrasados)
    jogos = []
    for _ in range(n_jogos):
        n_atrasados = min(random.randint(8, 12), max_atrasados)
        fixos = random.sample(atrasados, n_atrasados)
        resto = sorted(todos - set(fixos))
        jogo = sorted(fixos + random.sample(resto, 15 - n_atrasados))
        jogos.append(jogo)
    return jogos


# ============ BACKTEST ============

def backtest_estrategia(sorteios, estrategia_func, n_jogos=20):
    resultados = []
    for i in range(len(sorteios)):
        if i < 3:
            continue
        jogos = estrategia_func(sorteios, i, n_jogos=n_jogos)
        if not jogos:
            continue
        resultado_atual = sorteios[i][1]
        acertos = [contar_acertos(j, list(resultado_atual)) for j in jogos]
        resultados.append({
            'concurso': sorteios[i][0],
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


def resumo(nome, resultados):
    print(f"\n=== {nome} ===")
    print(f"Concursos testados: {len(resultados)}")
    print(f"Media do maximo acerto: {mean([r['max'] for r in resultados]):.2f}")
    print(f"Distribuicao dos maximos: {distribuicao_maximos(resultados)}")


def main():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
    rows = cur.fetchall()
    sorteios = [(r[0], set(r[1:16])) for r in rows]
    print(f"Sorteios carregados: {len(sorteios)}")

    n_jogos = 20

    # Baseline
    res_base = backtest_estrategia(sorteios, lambda s, i, n_jogos: [sorted(random.sample(list(range(1, 26)), 15)) for _ in range(n_jogos)], n_jogos=n_jogos)
    resumo(f"BASELINE ALEATORIO ({n_jogos} jogos)", res_base)

    # Hot last 1
    res = backtest_estrategia(sorteios, lambda s, i, n_jogos: estrategia_hot_last_n(s, i, n_concursos=1, n_jogos=n_jogos), n_jogos=n_jogos)
    resumo(f"HOT: numeros do ultimo concurso ({n_jogos} jogos)", res)

    # Hot last 2
    res = backtest_estrategia(sorteios, lambda s, i, n_jogos: estrategia_hot_last_n(s, i, n_concursos=2, n_jogos=n_jogos), n_jogos=n_jogos)
    resumo(f"HOT: numeros dos 2 ultimos concursos ({n_jogos} jogos)", res)

    # Hot last 3
    res = backtest_estrategia(sorteios, lambda s, i, n_jogos: estrategia_hot_last_n(s, i, n_concursos=3, n_jogos=n_jogos), n_jogos=n_jogos)
    resumo(f"HOT: numeros dos 3 ultimos concursos ({n_jogos} jogos)", res)

    # Hot weighted
    res = backtest_estrategia(sorteios, estrategia_hot_weighted, n_jogos=n_jogos)
    resumo(f"HOT WEIGHTED: peso decrescente ultimos 3 ({n_jogos} jogos)", res)

    # Posicional aleatorio
    res = backtest_estrategia(sorteios, estrategia_posicional, n_jogos=n_jogos)
    resumo(f"POSICIONAL: 5-10 fixos do anterior ({n_jogos} jogos)", res)

    # Posicional fixo 8
    res = backtest_estrategia(sorteios, lambda s, i, n_jogos: estrategia_posicional_fixo(s, i, n_fixos=8, n_jogos=n_jogos), n_jogos=n_jogos)
    resumo(f"POSICIONAL FIXO: 8 do anterior ({n_jogos} jogos)", res)

    # Persistencia por categorias
    for cat in ['pares', 'impares', 'primos', 'fibonacci', 'baixos', 'altos']:
        res = backtest_estrategia(sorteios, lambda s, i, n_jogos, c=cat: estrategia_persistencia_categoria(s, i, categoria=c, n_jogos=n_jogos), n_jogos=n_jogos)
        resumo(f"PERSISTENCIA: {cat.upper()} ({n_jogos} jogos)", res)

    # Combinada
    res = backtest_estrategia(sorteios, estrategia_combinada, n_jogos=n_jogos)
    resumo(f"COMBINADA: 5-8 ultimo + 2-4 frios + resto ({n_jogos} jogos)", res)

    # Frequencia historica
    res = backtest_estrategia(sorteios, estrategia_frequencia_historica, n_jogos=n_jogos)
    resumo(f"FREQUENCIA HISTORICA: top ate concurso anterior ({n_jogos} jogos)", res)

    # Atraso historico
    res = backtest_estrategia(sorteios, estrategia_atraso_historico, n_jogos=n_jogos)
    resumo(f"ATRASO: numeros nao sorteados nos ultimos 5 ({n_jogos} jogos)", res)


if __name__ == "__main__":
    main()
