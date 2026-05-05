# -*- coding: utf-8 -*-
"""
Análise de Padrões de String para Lotofácil
============================================
Conceito: cada combinação → string fixa 30 chars (''.join(f'{n:02d}' for n in sorted(combo)))
Bigrams   = pares adjacentes na string ordenada  (pares de números consecutivos no combo)
Trigrams  = trios adjacentes na string ordenada  (trios consecutivos no combo)

Uso principal:
  - Alerta na fase de exclusão (Op31 / Op30.2): mostra pares/trios quentes e frios
  - Filtro complementar pós-geração: rejeita combos com muitos cold-bigrams/trigrams
"""

import pyodbc
from collections import Counter

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


# ─────────────────────────────────────────────────────────────────────────────
# Funções auxiliares
# ─────────────────────────────────────────────────────────────────────────────

def combo_to_str(nums):
    """Converte 15 números para string fixa 30 chars (zero-padded)."""
    return ''.join(f'{n:02d}' for n in sorted(nums))


def get_bigrams(combo_sorted):
    """Retorna lista de bigram strings para um combo ordenado."""
    return [f'{combo_sorted[i]:02d}{combo_sorted[i+1]:02d}' for i in range(len(combo_sorted)-1)]


def get_trigrams(combo_sorted):
    """Retorna lista de trigram strings para um combo ordenado."""
    return [f'{combo_sorted[i]:02d}{combo_sorted[i+1]:02d}{combo_sorted[i+2]:02d}' for i in range(len(combo_sorted)-2)]


def hamming_numeros(c1_sorted, c2_sorted):
    """Quantos numeros diferem entre dois combos de 15 (0..15)."""
    return 15 - len(set(c1_sorted) & set(c2_sorted))


# ─────────────────────────────────────────────────────────────────────────────
# Cálculo de deltas histórico vs recente
# ─────────────────────────────────────────────────────────────────────────────

def calcular_padroes_string(conn_str=None, janela=50):
    """
    Carrega histórico do DB e calcula frequências de bigrams e trigrams.

    Returns:
        bigram_deltas  : dict  key='XXYY' → delta (freq_recente - freq_hist)
        trigram_deltas : dict  key='XXYYZZ' → delta
        bigram_freq_all: dict  key='XXYY' → freq % histórico
        trigram_freq_all: dict key='XXYYZZ' → freq % histórico
        n_total        : int   total de concursos
    """
    if conn_str is None:
        conn_str = CONN_STR

    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 "
            "FROM Resultados_INT ORDER BY Concurso"
        )
        rows = cursor.fetchall()

    all_combos = []
    for row in rows:
        nums = sorted(row)
        all_combos.append(nums)

    n_total = len(all_combos)
    recentes = all_combos[-janela:]

    bigram_all = Counter()
    bigram_rec = Counter()
    trigram_all = Counter()
    trigram_rec = Counter()

    for s in all_combos:
        for b in get_bigrams(s):
            bigram_all[b] += 1
        for t in get_trigrams(s):
            trigram_all[t] += 1

    for s in recentes:
        for b in get_bigrams(s):
            bigram_rec[b] += 1
        for t in get_trigrams(s):
            trigram_rec[t] += 1

    bigram_freq_all = {k: v/n_total*100 for k, v in bigram_all.items()}
    bigram_freq_rec = {k: v/janela*100 for k, v in bigram_rec.items()}
    trigram_freq_all = {k: v/n_total*100 for k, v in trigram_all.items()}
    trigram_freq_rec = {k: v/janela*100 for k, v in trigram_rec.items()}

    bigram_deltas = {}
    for k in set(list(bigram_freq_all.keys()) + list(bigram_freq_rec.keys())):
        bigram_deltas[k] = bigram_freq_rec.get(k, 0) - bigram_freq_all.get(k, 0)

    trigram_deltas = {}
    for k in set(list(trigram_freq_all.keys()) + list(trigram_freq_rec.keys())):
        trigram_deltas[k] = trigram_freq_rec.get(k, 0) - trigram_freq_all.get(k, 0)

    return bigram_deltas, trigram_deltas, bigram_freq_all, trigram_freq_all, n_total, all_combos


# ─────────────────────────────────────────────────────────────────────────────
# Alerta principal (chamado no console)
# ─────────────────────────────────────────────────────────────────────────────

def alerta_padroes_pool(pool_disponivel, conn_str=None, janela=50, threshold=8.0,
                        threshold_hist_min=5.0):
    """
    Exibe alerta de bigrams/trigrams quentes e frios para o pool disponível.
    Pergunta ao usuário se quer ativar filtro complementar.

    Args:
        pool_disponivel : list/set  — números do pool após exclusões (ex: 23 números)
        conn_str        : str       — connection string SQL Server
        janela          : int       — tamanho da janela recente (default 50)
        threshold       : float     — delta mínimo para classificar como hot/cold (%)
        threshold_hist_min: float   — frequência histórica mínima para considerar (%)

    Returns:
        cold_bigrams   : set  — bigrams string com delta < -threshold
        cold_trigrams  : set  — trigrams string com delta < -threshold
        hot_bigrams    : set  — bigrams string com delta > +threshold
        hot_trigrams   : set  — trigrams string com delta > +threshold
        usar_filtro    : bool — True se usuário ativou filtro
        max_violacoes  : int  — máximo de cold-bigrams tolerados por combo
    """
    pool_set = set(pool_disponivel)

    print("\n" + "─"*78)
    print("🔤 PADRÕES DE STRING — BIGRAMS/TRIGRAMS QUENTES E FRIOS")
    print("─"*78)
    print(f"   Analisando últimos {janela} concursos vs histórico completo...")

    try:
        bd, td, bfa, tfa, n_total, all_combos = calcular_padroes_string(conn_str, janela)
    except Exception as e:
        print(f"   ⚠️  Não foi possível calcular padrões: {e}")
        return set(), set(), set(), set(), False, 1, [], False, 4

    print(f"   ✅ {n_total} concursos analisados")

    ultimo_sorteio = all_combos[-1] if all_combos else []

    # Filtrar bigrams onde ambos os números estão no pool e freq hist >= threshold_hist_min
    def _parse_bigram(b):
        return int(b[:2]), int(b[2:4])

    def _parse_trigram(t):
        return int(t[:2]), int(t[2:4]), int(t[4:6])

    bi_pool = {b: d for b, d in bd.items()
               if all(n in pool_set for n in _parse_bigram(b))
               and bfa.get(b, 0) >= threshold_hist_min}

    tri_pool = {t: d for t, d in td.items()
                if all(n in pool_set for n in _parse_trigram(t))
                and tfa.get(t, 0) >= threshold_hist_min}

    cold_bigrams = {b for b, d in bi_pool.items() if d < -threshold}
    hot_bigrams  = {b for b, d in bi_pool.items() if d > threshold}
    cold_trigrams = {t for t, d in tri_pool.items() if d < -threshold}
    hot_trigrams  = {t for t, d in tri_pool.items() if d > threshold}

    # ── Exibir HOT bigrams ─────────────────────────────────────────────────
    hot_bi_sorted = sorted(hot_bigrams, key=lambda b: -bi_pool[b])
    cold_bi_sorted = sorted(cold_bigrams, key=lambda b: bi_pool[b])
    hot_tri_sorted = sorted(hot_trigrams, key=lambda t: -tri_pool[t])
    cold_tri_sorted = sorted(cold_trigrams, key=lambda t: tri_pool[t])

    print(f"\n   BIGRAMS DO POOL (threshold=±{threshold:.0f}%) — {len(bi_pool)} pares relevantes:")
    print(f"   {'Par':>8} | {'Hist%':>8} | {'Ult{janela}%'.format(janela=janela):>8} | {'Delta':>8}")

    if hot_bi_sorted:
        print(f"   🔥 QUENTES ({len(hot_bi_sorted)}):")
        for b in hot_bi_sorted[:5]:
            n1, n2 = _parse_bigram(b)
            fa = bfa.get(b, 0)
            fr = fa + bi_pool[b]
            print(f"      {n1:>2},{n2:>2} ({b}) | {fa:>7.1f}% | {fr:>7.1f}% | {bi_pool[b]:>+7.1f}%")
    else:
        print(f"   🔥 Nenhum bigram quente acima de +{threshold:.0f}%")

    if cold_bi_sorted:
        print(f"   🧊 FRIOS ({len(cold_bi_sorted)}):")
        for b in cold_bi_sorted[:5]:
            n1, n2 = _parse_bigram(b)
            fa = bfa.get(b, 0)
            fr = fa + bi_pool[b]
            print(f"      {n1:>2},{n2:>2} ({b}) | {fa:>7.1f}% | {fr:>7.1f}% | {bi_pool[b]:>+7.1f}%")
    else:
        print(f"   🧊 Nenhum bigram frio abaixo de -{threshold:.0f}%")

    print(f"\n   TRIGRAMS DO POOL (threshold=±{threshold:.0f}%) — {len(tri_pool)} trios relevantes:")
    if hot_tri_sorted:
        print(f"   🔥 QUENTES ({len(hot_tri_sorted)}):")
        for t in hot_tri_sorted[:3]:
            n1, n2, n3 = _parse_trigram(t)
            fa = tfa.get(t, 0)
            fr = fa + tri_pool[t]
            print(f"      {n1:>2},{n2:>2},{n3:>2} ({t}) | {fa:>6.1f}% → {fr:>6.1f}% (Δ{tri_pool[t]:>+6.1f}%)")
    else:
        print(f"   🔥 Nenhum trigram quente acima de +{threshold:.0f}%")

    if cold_tri_sorted:
        print(f"   🧊 FRIOS ({len(cold_tri_sorted)}):")
        for t in cold_tri_sorted[:3]:
            n1, n2, n3 = _parse_trigram(t)
            fa = tfa.get(t, 0)
            fr = fa + tri_pool[t]
            print(f"      {n1:>2},{n2:>2},{n3:>2} ({t}) | {fa:>6.1f}% → {fr:>6.1f}% (Δ{tri_pool[t]:>+6.1f}%)")
    else:
        print(f"   🧊 Nenhum trigram frio abaixo de -{threshold:.0f}%")

    # ── Resumo de relevância ───────────────────────────────────────────────
    print(f"\n   📋 Resumo: {len(cold_bigrams)} bigrams frios | {len(cold_trigrams)} trigrams frios no pool")
    if cold_bigrams:
        cold_pares = [f"({_parse_bigram(b)[0]},{_parse_bigram(b)[1]})" for b in cold_bi_sorted[:8]]
        print(f"   🧊 Pares frios (evitar adjacentes): {', '.join(cold_pares)}")
    if cold_trigrams:
        cold_trios = [f"({_parse_trigram(t)[0]},{_parse_trigram(t)[1]},{_parse_trigram(t)[2]})" for t in cold_tri_sorted[:5]]
        print(f"   🧊 Trios frios (evitar adjacentes): {', '.join(cold_trios)}")


    # -- HAMMING SIMILARITY --------------------------------------------------------
    print(f"\n   \U0001f4cf HAMMING SIMILARITY")
    print(f"   Ultimo sorteio: {ultimo_sorteio}")

    if len(all_combos) >= 2:
        recentes_100 = all_combos[-101:]
        dists_consec = [hamming_numeros(recentes_100[i], recentes_100[i+1]) for i in range(len(recentes_100)-1)]
        avg_h = sum(dists_consec) / len(dists_consec)
        print(f"   Hamming consecutivos (ult.100): media={avg_h:.1f} | min={min(dists_consec)} | max={max(dists_consec)}")

        dists_to_last = [(i, hamming_numeros(all_combos[i], ultimo_sorteio))
                         for i in range(len(all_combos)-1)]
        dists_to_last.sort(key=lambda x: x[1])
        print(f"   TOP 5 mais similares ao ultimo:")
        for idx, d in dists_to_last[:5]:
            comuns = len(set(all_combos[idx]) & set(ultimo_sorteio))
            print(f"      Concurso ~{idx+1}: Hamming={d} ({comuns} em comum)")

        from collections import Counter as _C
        dist_counter = _C(d for _, d in dists_to_last)
        raros = sum(dist_counter.get(k, 0) for k in range(4))
        print(f"   Combos com Hamming < 4: {raros} de {len(dists_to_last)} ({raros/len(dists_to_last)*100:.1f}%)")

    # ── Pergunta ao usuário ────────────────────────────────────────────────
    print(f"\n   💡 FILTRO COMPLEMENTAR (rejeita combos com muitos cold-bigrams adjacentes):")
    print(f"      [0] Desativado — sem filtro de padrões string  ⭐ DEFAULT")
    print(f"      [1] Leve   — rejeitar combos com >1 cold-bigram adjacente")
    print(f"      [2] Médio  — rejeitar combos com >2 cold-bigrams adjacentes")
    print(f"      [3] Forte  — rejeitar qualquer combo com cold-bigram adjacente")

    usar_filtro = False
    max_violacoes = 1

    try:
        _inp = input("   Escolha [0-3, ENTER=0]: ").strip()
        if _inp == '' or _inp == '0':
            usar_filtro = False
            print("   ✅ Filtro de padrões string: DESATIVADO")
        elif _inp == '1':
            usar_filtro = True
            max_violacoes = 1
            print(f"   ✅ Filtro LEVE: rejeitar combos com >1 cold-bigram adjacente")
        elif _inp == '2':
            usar_filtro = True
            max_violacoes = 2
            print(f"   ✅ Filtro MÉDIO: rejeitar combos com >2 cold-bigrams adjacentes")
        elif _inp == '3':
            usar_filtro = True
            max_violacoes = 0
            print(f"   ✅ Filtro FORTE: rejeitar qualquer combo com cold-bigram adjacente")
        else:
            usar_filtro = False
            print("   ✅ Filtro de padrões string: DESATIVADO")
    except Exception:
        usar_filtro = False

    # -- Pergunta filtro Hamming ---------------------------------------------------
    print(f"\n   FILTRO HAMMING (rejeita combos muito similares ao ultimo sorteio):")
    print(f"      [0] Desativado  (DEFAULT)")
    print(f"      [1] Leve   - rejeitar Hamming < 3")
    print(f"      [2] Medio  - rejeitar Hamming < 4 (recomendado)")
    print(f"      [3] Forte  - rejeitar Hamming < 5")

    usar_hamming = False
    min_hamming = 4

    try:
        _inp_h = input("   Escolha [0-3, ENTER=0]: ").strip()
        if _inp_h == '1':
            usar_hamming = True
            min_hamming = 3
            print("   Hamming LEVE ativado: rejeitar combos com < 3 numeros diferentes")
        elif _inp_h == '2':
            usar_hamming = True
            min_hamming = 4
            print("   Hamming MEDIO ativado: rejeitar combos com < 4 numeros diferentes")
        elif _inp_h == '3':
            usar_hamming = True
            min_hamming = 5
            print("   Hamming FORTE ativado: rejeitar combos com < 5 numeros diferentes")
        else:
            usar_hamming = False
            print("   Filtro Hamming: DESATIVADO")
    except Exception:
        usar_hamming = False

    return cold_bigrams, cold_trigrams, hot_bigrams, hot_trigrams, usar_filtro, max_violacoes, ultimo_sorteio, usar_hamming, min_hamming


# ─────────────────────────────────────────────────────────────────────────────
# Filtro complementar de combinações
# ─────────────────────────────────────────────────────────────────────────────

def filtrar_por_padroes_string(combinacoes, cold_bigrams, cold_trigrams=None,
                               max_violacoes=1):
    """
    Filtra combinações que contenham mais de max_violacoes cold-bigrams adjacentes.

    Args:
        combinacoes   : list of tuples/lists  — combinações geradas
        cold_bigrams  : set   — bigrams string proibidos (ex: {'1718', '1819'})
        cold_trigrams : set   — trigrams string proibidos (opcional)
        max_violacoes : int   — máximo de cold-bigrams tolerados (0=nenhum)

    Returns:
        list  — combinações que passaram no filtro
        int   — número de combinações rejeitadas
    """
    if not cold_bigrams and not cold_trigrams:
        return list(combinacoes), 0

    cold_trigrams = cold_trigrams or set()
    aprovadas = []
    rejeitadas = 0

    for combo in combinacoes:
        cs = sorted(combo)
        bigrams = get_bigrams(cs)

        # Contar violações de bigram
        viol_bigram = sum(1 for b in bigrams if b in cold_bigrams)
        if viol_bigram > max_violacoes:
            rejeitadas += 1
            continue

        # Verificar trigrams (se fornecidos) — qualquer violação rejeita
        if cold_trigrams:
            trigrams = get_trigrams(cs)
            viol_trigram = sum(1 for t in trigrams if t in cold_trigrams)
            if viol_trigram > 0:
                rejeitadas += 1
                continue

        aprovadas.append(combo)

    return aprovadas, rejeitadas


# --------------------------------------------------------------------------
# Filtro complementar: Hamming distance
# --------------------------------------------------------------------------

def filtrar_por_hamming(combinacoes, ultimo_sorteio, min_hamming=4):
    """
    Rejeita combinacoes muito similares ao ultimo sorteio.

    Args:
        combinacoes    : list  - combinacoes geradas
        ultimo_sorteio : list  - ultimo sorteio ordenado (15 numeros)
        min_hamming    : int   - distancia minima exigida

    Returns:
        list  - combinacoes aprovadas
        int   - numero de rejeitadas
    """
    if not ultimo_sorteio or min_hamming <= 0:
        return list(combinacoes), 0

    ultimo_set = set(ultimo_sorteio)
    aprovadas = []
    rejeitadas = 0

    for combo in combinacoes:
        dist = 15 - len(set(combo) & ultimo_set)
        if dist < min_hamming:
            rejeitadas += 1
        else:
            aprovadas.append(combo)

    return aprovadas, rejeitadas
