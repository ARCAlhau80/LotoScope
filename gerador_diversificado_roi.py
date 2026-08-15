import pyodbc
import random
import json
from collections import Counter, defaultdict
from statistics import mean
from itertools import combinations

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

# Premiacoes aproximadas da Lotofacil (valores medios historicos)
PREMIOS = {
    11: 5.0,
    12: 15.0,
    13: 150.0,
    14: 1500.0,
    15: 1000000.0,
}
CUSTO_POR_JOGO = 2.5

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}


def contar_acertos(jogo, resultado):
    return len(set(jogo) & set(resultado))


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


def gerar_ciclo(ciclo_dados=None):
    todos = set(range(1, 26))
    if not ciclo_dados:
        return gerar_aleatorio()

    faltantes = {n for n, qtd in ciclo_dados.items() if qtd == 0}
    pesos = {}
    for n in todos:
        if n in faltantes:
            pesos[n] = 4.0
        elif ciclo_dados.get(n, 0) <= 1:
            pesos[n] = 2.0
        else:
            pesos[n] = 1.0

    total_peso = sum(pesos.values())
    nums = sorted(todos)
    probs = [pesos[n] / total_peso for n in nums]

    jogo = sorted(random.choices(nums, weights=probs, k=15))
    while len(set(jogo)) < 15:
        jogo = sorted(random.choices(nums, weights=probs, k=15))
    return jogo


def gerar_diversificado_v2(sorteios, idx_atual, n_jogos=20, usar_ciclo=False, ciclo_dados=None, min_distintos=25):
    """
    Versao melhorada: garante cobertura minima dos 25 numeros e evita jogos muito similares.
    """
    ultimos = [sorteios[j][1] for j in range(max(0, idx_atual - 5), idx_atual)]
    jogos = []
    estrategias = []

    max_tentativas = n_jogos * 200
    tentativa = 0

    while len(jogos) < n_jogos and tentativa < max_tentativas:
        tentativa += 1
        estrategia = len(jogos) % 6
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
                jogo = gerar_ciclo(ciclo_dados)
            else:
                jogo = gerar_aleatorio()

        # Evita duplicados
        if jogo in jogos:
            continue

        # Evita jogos muito similares (intersecao > 12)
        muito_similar = False
        for existente in jogos:
            if len(set(jogo) & set(existente)) > 12:
                muito_similar = True
                break
        if muito_similar:
            continue

        jogos.append(jogo)
        estrategias.append(estrategia)

    # Se nao conseguiu gerar o suficiente, relaxa restricao
    while len(jogos) < n_jogos:
        estrategia = len(jogos) % 6
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
                jogo = gerar_ciclo(ciclo_dados)
            else:
                jogo = gerar_aleatorio()
        if jogo not in jogos:
            jogos.append(jogo)

    # Garante cobertura minima: se faltam numeros, troca alguns nos jogos
    if min_distintos >= 25:
        cobertura = set(n for j in jogos for n in j)
        faltando = sorted(set(range(1, 26)) - cobertura)
        for num_faltando in faltando:
            # Troca um numero em um jogo aleatorio pelo numero faltando
            idx_jogo = random.randrange(len(jogos))
            jogo = jogos[idx_jogo]
            # Troca um numero que nao e o faltando
            pos_trocar = random.randrange(15)
            novo_jogo = jogo.copy()
            novo_jogo[pos_trocar] = num_faltando
            novo_jogo = sorted(novo_jogo)
            if novo_jogo not in jogos:
                jogos[idx_jogo] = novo_jogo

    return jogos


def calcular_roi(resultados_por_concurso, n_jogos=20):
    """Calcula retorno esperado por estrategia."""
    total_gasto = 0.0
    total_retorno = 0.0
    for r in resultados_por_concurso:
        total_gasto += n_jogos * CUSTO_POR_JOGO
        for acertos in r['acertos']:
            total_retorno += PREMIOS.get(acertos, 0.0)
    roi = (total_retorno - total_gasto) / total_gasto * 100
    return {
        'gasto': total_gasto,
        'retorno': total_retorno,
        'saldo': total_retorno - total_gasto,
        'roi_pct': roi,
    }


def carregar_dados():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
    sorteios = [(r[0], set(r[1:16])) for r in cur.fetchall()]

    cur.execute("SELECT Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento FROM NumerosCiclos ORDER BY Ciclo, Numero")
    ciclos_raw = defaultdict(lambda: {'numeros': {}, 'inicio': None, 'fim': None})
    for r in cur.fetchall():
        ciclo, num, qtd, ini, fim = r
        ciclos_raw[ciclo]['numeros'][num] = qtd
        ciclos_raw[ciclo]['inicio'] = ini
        ciclos_raw[ciclo]['fim'] = fim

    concurso_ciclo = {}
    for ciclo_id, ciclo in ciclos_raw.items():
        ini, fim = ciclo['inicio'], ciclo['fim']
        if ini is None:
            continue
        fim = fim or 99999
        for c in range(ini, fim + 1):
            concurso_ciclo[c] = (ciclo_id, ciclo['numeros'])

    return sorteios, concurso_ciclo


def backtest(sorteios, concurso_ciclo, n_jogos=20, usar_ciclo=False):
    resultados = []
    for i in range(5, len(sorteios)):
        concurso_atual, resultado_atual = sorteios[i]
        ciclo_info = concurso_ciclo.get(concurso_atual)
        ciclo_dados = ciclo_info[1] if ciclo_info else None
        jogos = gerar_diversificado_v2(sorteios, i, n_jogos=n_jogos, usar_ciclo=usar_ciclo, ciclo_dados=ciclo_dados)
        acertos = [contar_acertos(j, list(resultado_atual)) for j in jogos]
        cobertura = len(set(n for j in jogos for n in j))
        resultados.append({
            'concurso': concurso_atual,
            'acertos': acertos,
            'max': max(acertos),
            'mean': mean(acertos),
            'cobertura': cobertura,
        })
    return resultados


def resumo(nome, resultados, n_jogos=20):
    print(f"\n=== {nome} ===")
    print(f"Concursos testados: {len(resultados)}")
    print(f"Media do maximo acerto: {mean([r['max'] for r in resultados]):.2f}")
    print(f"Media dos acertos medios: {mean([r['mean'] for r in resultados]):.2f}")
    print(f"Media de cobertura: {mean([r['cobertura'] for r in resultados]):.2f}")

    maximos = [r['max'] for r in resultados]
    c = Counter(maximos)
    total = len(maximos)
    print(f"Distribuicao dos maximos: { {k: {'count': c[k], 'pct': f'{c[k]/total*100:.2f}%'} for k in sorted(c.keys())} }")

    # ROI
    roi = calcular_roi(resultados, n_jogos=n_jogos)
    print(f"ROI estimado: {roi['roi_pct']:.2f}%")
    print(f"  Gasto total: R$ {roi['gasto']:,.2f}")
    print(f"  Retorno total: R$ {roi['retorno']:,.2f}")
    print(f"  Saldo: R$ {roi['saldo']:,.2f}")


def main():
    sorteios, concurso_ciclo = carregar_dados()
    print(f"Sorteios carregados: {len(sorteios)}")

    n_jogos = 20

    # Baseline
    resultados_base = []
    for i in range(5, len(sorteios)):
        resultado_atual = sorteios[i][1]
        jogos = [gerar_aleatorio() for _ in range(n_jogos)]
        acertos = [contar_acertos(j, list(resultado_atual)) for j in jogos]
        cobertura = len(set(n for j in jogos for n in j))
        resultados_base.append({'concurso': sorteios[i][0], 'acertos': acertos, 'max': max(acertos), 'mean': mean(acertos), 'cobertura': cobertura})
    resumo("BASELINE ALEATORIO", resultados_base, n_jogos=n_jogos)

    # Diversificado v2 sem ciclo
    res_div = backtest(sorteios, concurso_ciclo, n_jogos=n_jogos, usar_ciclo=False)
    resumo("GERADOR DIVERSIFICADO v2 (sem ciclo)", res_div, n_jogos=n_jogos)

    # Diversificado v2 com ciclo
    res_div_ciclo = backtest(sorteios, concurso_ciclo, n_jogos=n_jogos, usar_ciclo=True)
    resumo("GERADOR DIVERSIFICADO v2 + CICLO", res_div_ciclo, n_jogos=n_jogos)

    # Geracao para o proximo concurso
    print("\n=== GERACAO PARA O PROXIMO CONCURSO ===")
    ciclo_info = concurso_ciclo.get(sorteios[-1][0])
    ciclo_dados = ciclo_info[1] if ciclo_info else None
    jogos = gerar_diversificado_v2(sorteios, len(sorteios), n_jogos=n_jogos, usar_ciclo=True, ciclo_dados=ciclo_dados)
    print(f"Cobertura: {len(set(n for j in jogos for n in j))}/25")
    for idx, jogo in enumerate(jogos, 1):
        print(f"Jogo {idx:2d}: {' '.join(f'{n:02d}' for n in jogo)}")


if __name__ == "__main__":
    main()
