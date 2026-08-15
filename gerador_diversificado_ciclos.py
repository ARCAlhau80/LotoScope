import pyodbc
import random
import json
from collections import Counter, defaultdict
from statistics import mean
from datetime import datetime

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


# ============ GERADORES DIVERSIFICADOS ============

def gerar_aleatorio(excluidos=None):
    todos = set(range(1, 26)) - set(excluidos or [])
    return sorted(random.sample(sorted(todos), 15))


def gerar_atraso(ultimos_concursos):
    todos = set(range(1, 26))
    recentes = set()
    for s in ultimos_concursos:
        recentes |= s
    atrasados = sorted(todos - recentes)
    if len(atrasados) < 15:
        atrasados = sorted(todos)
    n_atrasados = min(random.randint(8, 12), len(atrasados))
    fixos = random.sample(atrasados, n_atrasados)
    resto = sorted(todos - set(fixos))
    return sorted(fixos + random.sample(resto, 15 - n_atrasados))


def gerar_hot(ultimos_concursos, n_hot=8):
    todos = set(range(1, 26))
    hot = set()
    for s in ultimos_concursos[-3:]:
        hot |= s
    hot = sorted(hot)
    n_fixos = min(n_hot, len(hot))
    fixos = random.sample(hot, n_fixos)
    resto = sorted(todos - set(fixos))
    return sorted(fixos + random.sample(resto, 15 - n_fixos))


def gerar_persistencia_categoria(ultimos_2, categoria='pares'):
    todos = list(range(1, 26))
    if categoria == 'pares':
        cat_func = lambda x: x % 2 == 0
    elif categoria == 'impares':
        cat_func = lambda x: x % 2 == 1
    elif categoria == 'primos':
        cat_func = lambda x: x in PRIMOS
    elif categoria == 'baixos':
        cat_func = lambda x: x <= 13
    elif categoria == 'altos':
        cat_func = lambda x: x >= 14
    else:
        cat_func = lambda x: x % 2 == 0

    if len(ultimos_2) < 2:
        return gerar_aleatorio()

    cat_anterior = {n for n in ultimos_2[0] if cat_func(n)}
    cat_atual = {n for n in ultimos_2[1] if cat_func(n)}
    taxa = len(cat_anterior & cat_atual) / max(len(cat_anterior), len(cat_atual), 1)

    pool_cat = sorted({n for n in todos if cat_func(n)})
    outros = sorted({n for n in todos if not cat_func(n)})
    max_cat = len(pool_cat)

    if taxa > 0.5:
        n_cat = min(random.randint(7, 10), max_cat)
    else:
        n_cat = min(random.randint(4, 6), max_cat)
    return sorted(random.sample(pool_cat, n_cat) + random.sample(outros, 15 - n_cat))


def gerar_ciclo(historico_ate_agora, ciclo_dados=None):
    """
    Usa informacao do ciclo atual: da peso maior para numeros que ainda nao sairam no ciclo.
    """
    todos = set(range(1, 26))
    if not ciclo_dados:
        return gerar_aleatorio()

    faltantes = {n for n, qtd in ciclo_dados.items() if qtd == 0}
    # Probabilidade proporcional: faltantes tem peso maior, mas nao excludente
    pesos = {}
    for n in todos:
        if n in faltantes:
            pesos[n] = 3.0  # peso alto
        elif ciclo_dados.get(n, 0) <= 1:
            pesos[n] = 1.5
        else:
            pesos[n] = 1.0

    total_peso = sum(pesos.values())
    nums = sorted(todos)
    probs = [pesos[n] / total_peso for n in nums]

    jogo = sorted(random.choices(nums, weights=probs, k=15))
    # Evita duplicados
    while len(set(jogo)) < 15:
        jogo = sorted(random.choices(nums, weights=probs, k=15))
    return jogo


def gerar_diversificado(sorteios, idx_atual, n_jogos=20, usar_ciclo=False, ciclo_dados=None):
    """Gera jogos diversos usando multiplas estrategias."""
    ultimos = [sorteios[j][1] for j in range(max(0, idx_atual - 5), idx_atual)]
    jogos = []
    estrategias = []

    for i in range(n_jogos):
        estrategia = i % 6
        if estrategia == 0:
            jogo = gerar_aleatorio()
        elif estrategia == 1:
            jogo = gerar_atraso(ultimos[-5:])
        elif estrategia == 2:
            jogo = gerar_hot(ultimos[-3:], n_hot=random.randint(7, 9))
        elif estrategia == 3:
            jogo = gerar_persistencia_categoria(ultimos[-2:], categoria=random.choice(['pares', 'impares', 'primos', 'baixos', 'altos']))
        elif estrategia == 4:
            jogo = gerar_hot(ultimos[-3:], n_hot=random.randint(5, 7))
        else:
            if usar_ciclo:
                jogo = gerar_ciclo(ultimos, ciclo_dados)
            else:
                jogo = gerar_aleatorio()

        # Evita duplicados exatos
        tentativas = 0
        while jogo in jogos and tentativas < 50:
            if estrategia == 0:
                jogo = gerar_aleatorio()
            elif estrategia == 1:
                jogo = gerar_atraso(ultimos[-5:])
            elif estrategia == 2:
                jogo = gerar_hot(ultimos[-3:], n_hot=random.randint(7, 9))
            elif estrategia == 3:
                jogo = gerar_persistencia_categoria(ultimos[-2:], categoria=random.choice(['pares', 'impares', 'primos', 'baixos', 'altos']))
            elif estrategia == 4:
                jogo = gerar_hot(ultimos[-3:], n_hot=random.randint(5, 7))
            else:
                if usar_ciclo:
                    jogo = gerar_ciclo(ultimos, ciclo_dados)
                else:
                    jogo = gerar_aleatorio()
            tentativas += 1
        jogos.append(jogo)
        estrategias.append(estrategia)

    return jogos


# ============ CARREGAMENTO ============

def carregar_dados():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()

    cur.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
    sorteios = [(r[0], set(r[1:16])) for r in cur.fetchall()]

    # Carregar ciclos: mapa concurso -> ciclo atual e dados do ciclo
    cur.execute("SELECT Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento FROM NumerosCiclos ORDER BY Ciclo, Numero")
    ciclos = defaultdict(lambda: {'numeros': {}, 'inicio': None, 'fim': None})
    for r in cur.fetchall():
        ciclo, num, qtd, ini, fim = r
        ciclos[ciclo]['numeros'][num] = qtd
        ciclos[ciclo]['inicio'] = ini
        ciclos[ciclo]['fim'] = fim

    # Mapa: concurso -> ciclo que o contem
    concurso_ciclo = {}
    for ciclo_id, ciclo in ciclos.items():
        ini, fim = ciclo['inicio'], ciclo['fim']
        if ini is None:
            continue
        fim = fim or 99999
        for c in range(ini, fim + 1):
            concurso_ciclo[c] = (ciclo_id, ciclo['numeros'])

    return sorteios, concurso_ciclo


# ============ BACKTEST ============

def backtest(sorteios, concurso_ciclo, n_jogos=20, usar_ciclo=False):
    resultados = []
    for i in range(5, len(sorteios)):
        concurso_atual, resultado_atual = sorteios[i]
        ciclo_info = concurso_ciclo.get(concurso_atual)
        ciclo_dados = ciclo_info[1] if ciclo_info else None
        jogos = gerar_diversificado(sorteios, i, n_jogos=n_jogos, usar_ciclo=usar_ciclo, ciclo_dados=ciclo_dados)
        acertos = [contar_acertos(j, list(resultado_atual)) for j in jogos]
        # Cobertura: quantos numeros distintos aparecem nos N jogos
        cobertura = len(set(n for j in jogos for n in j))
        resultados.append({
            'concurso': concurso_atual,
            'acertos': acertos,
            'max': max(acertos),
            'mean': mean(acertos),
            'cobertura': cobertura,
        })
    return resultados


def resumo(nome, resultados):
    print(f"\n=== {nome} ===")
    print(f"Concursos testados: {len(resultados)}")
    print(f"Media do maximo acerto: {mean([r['max'] for r in resultados]):.2f}")
    print(f"Media dos acertos medios: {mean([r['mean'] for r in resultados]):.2f}")
    print(f"Media de cobertura (numeros distintos nos {len(resultados[0]['acertos'])} jogos): {mean([r['cobertura'] for r in resultados]):.2f}")

    maximos = [r['max'] for r in resultados]
    c = Counter(maximos)
    total = len(maximos)
    print(f"Distribuicao dos maximos: { {k: {'count': c[k], 'pct': f'{c[k]/total*100:.2f}%'} for k in sorted(c.keys())} }")

    # Contar quantos 11+ aconteceram
    onze_mais = sum(1 for r in resultados if r['max'] >= 11)
    doze_mais = sum(1 for r in resultados if r['max'] >= 12)
    treze_mais = sum(1 for r in resultados if r['max'] >= 13)
    print(f"Concursos com pelo menos um 11+: {onze_mais} ({onze_mais/total*100:.2f}%)")
    print(f"Concursos com pelo menos um 12+: {doze_mais} ({doze_mais/total*100:.2f}%)")
    print(f"Concursos com pelo menos um 13+: {treze_mais} ({treze_mais/total*100:.2f}%)")


def main():
    sorteios, concurso_ciclo = carregar_dados()
    print(f"Sorteios carregados: {len(sorteios)}")

    n_jogos = 20

    # Gerador diversificado SEM ciclo
    res_div = backtest(sorteios, concurso_ciclo, n_jogos=n_jogos, usar_ciclo=False)
    resumo(f"GERADOR DIVERSIFICADO ({n_jogos} jogos, SEM ciclo)", res_div)

    # Gerador diversificado COM ciclo
    res_div_ciclo = backtest(sorteios, concurso_ciclo, n_jogos=n_jogos, usar_ciclo=True)
    resumo(f"GERADOR DIVERSIFICADO + CICLOS ({n_jogos} jogos)", res_div_ciclo)

    # Baseline aleatorio puro
    resultados_base = []
    for i in range(5, len(sorteios)):
        resultado_atual = sorteios[i][1]
        jogos = [gerar_aleatorio() for _ in range(n_jogos)]
        acertos = [contar_acertos(j, list(resultado_atual)) for j in jogos]
        cobertura = len(set(n for j in jogos for n in j))
        resultados_base.append({
            'concurso': sorteios[i][0],
            'acertos': acertos,
            'max': max(acertos),
            'mean': mean(acertos),
            'cobertura': cobertura,
        })
    resumo(f"BASELINE ALEATORIO ({n_jogos} jogos)", resultados_base)

    # Analise de ciclo: quando falta 1 numero, ele sai no proximo?
    print("\n=== ANALISE DO CICLO ===")
    analise_ciclo(sorteios, concurso_ciclo)

    # Gerar jogos para o proximo concurso (3745) se disponivel
    gerar_para_proximo(sorteios, concurso_ciclo, n_jogos=20)


def analise_ciclo(sorteios, concurso_ciclo):
    # Reconstruir ciclos para analise
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("SELECT Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento FROM NumerosCiclos ORDER BY Ciclo, Numero")
    ciclos_raw = defaultdict(lambda: {'numeros': {}, 'inicio': None, 'fim': None})
    for r in cur.fetchall():
        ciclo, num, qtd, ini, fim = r
        ciclos_raw[ciclo]['numeros'][num] = qtd
        ciclos_raw[ciclo]['inicio'] = ini
        ciclos_raw[ciclo]['fim'] = fim

    sorteios_dict = {c: nums for c, nums in sorteios}

    resultados = []
    for ciclo_id, ciclo in ciclos_raw.items():
        ini, fim = ciclo['inicio'], ciclo['fim']
        if not ini or not fim:
            continue
        faltantes = set()
        for concurso in range(ini, fim + 1):
            if concurso == ini:
                faltantes = set(range(1, 26)) - sorteios_dict.get(concurso, set())
                continue
            sairam = sorteios_dict.get(concurso, set())
            acertos = len(faltantes & sairam)
            resultados.append({'faltantes': len(faltantes), 'acertos': acertos})
            faltantes -= sairam

    agrupado = defaultdict(list)
    for r in resultados:
        agrupado[r['faltantes']].append(r['acertos'])

    print("Numeros faltantes no ciclo -> media que saem no proximo concurso:")
    for k in sorted(agrupado.keys()):
        vals = agrupado[k]
        print(f"  {k:2d} faltantes: media {mean(vals):.2f} | ocorrencias {len(vals)}")


def gerar_para_proximo(sorteios, concurso_ciclo, n_jogos=20):
    ultimo_concurso = sorteios[-1][0]
    proximo_concurso = ultimo_concurso + 1
    print(f"\n=== GERACAO PARA O PROXIMO CONCURSO ({proximo_concurso}) ===")

    ciclo_info = concurso_ciclo.get(ultimo_concurso)
    ciclo_dados = ciclo_info[1] if ciclo_info else None

    if ciclo_dados:
        faltantes = sorted([n for n, qtd in ciclo_dados.items() if qtd == 0])
        baixa_freq = sorted([n for n, qtd in ciclo_dados.items() if qtd <= 1])
        print(f"Ciclo atual: {ciclo_info[0]}")
        print(f"Numeros ainda nao sorteados no ciclo: {faltantes}")
        print(f"Numeros com baixa frequencia (0-1) no ciclo: {baixa_freq}")
    else:
        print("Sem dados de ciclo para o ultimo concurso.")

    jogos = gerar_diversificado(sorteios, len(sorteios), n_jogos=n_jogos, usar_ciclo=True, ciclo_dados=ciclo_dados)

    print(f"\n{n_jogos} jogos gerados:")
    for idx, jogo in enumerate(jogos, 1):
        print(f"  Jogo {idx:2d}: {' '.join(f'{n:02d}' for n in jogo)}")

    # Estatisticas dos jogos gerados
    cobertura = len(set(n for j in jogos for n in j))
    print(f"\nCobertura total: {cobertura}/25 numeros")
    freq_numeros = Counter(n for j in jogos for n in j)
    print("Frequencia dos numeros nos jogos gerados:")
    for n in sorted(range(1, 26)):
        print(f"  {n:02d}: {freq_numeros[n]:2d}x", end="")
        if n % 5 == 0:
            print()
    print()


if __name__ == "__main__":
    main()
