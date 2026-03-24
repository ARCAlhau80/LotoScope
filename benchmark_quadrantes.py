# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         BENCHMARK: ANÁLISE DE QUADRANTES PARA EXCLUSÃO                      ║
║                                                                              ║
║  Valida a hipótese: números ausentes se concentram em quadrantes?            ║
║  Se sim, sugerir quadrantes "piores" antes da exclusão manual.               ║
║                                                                              ║
║  Conceito:                                                                   ║
║  - Dividir 1-25 em 5 quadrantes de 5 números                                ║
║  - Ordenar dinamicamente por score (hot + débito)                            ║
║  - Analisar padrão histórico de ausências por quadrante                      ║
║  - Comparar: exclusão por quadrante vs aleatória vs INVERTIDA v3.0           ║
║                                                                              ║
║  Criado: 20/03/2026                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pyodbc
import random
from collections import Counter
from itertools import combinations

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def carregar_resultados():
    """Carrega todos os resultados do banco"""
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso ASC
    """)
    resultados = {}
    for row in cursor.fetchall():
        resultados[row[0]] = {
            'concurso': row[0],
            'numeros': list(row[1:16]),
            'set': set(row[1:16])
        }
    conn.close()
    return resultados


# ═══════════════════════════════════════════════════════════════════════════
# SCORING (INVERTIDA v3.0 - idêntica ao super_menu.py)
# ═══════════════════════════════════════════════════════════════════════════

def calcular_score_invertida(dados_historicos):
    """
    Calcula score INVERTIDA v3.0 para cada número 1-25.
    Retorna dict {numero: score} — score alto = candidato a exclusão.
    """
    def freq_janela(tamanho):
        freq = Counter()
        for r in dados_historicos[:min(tamanho, len(dados_historicos))]:
            freq.update(r['numeros'])
        return {n: freq.get(n, 0) / min(tamanho, len(dados_historicos)) * 100 for n in range(1, 26)}

    def contar_consecutivos(n):
        count = 0
        for r in dados_historicos[:15]:
            if n in r['numeros']:
                count += 1
            else:
                break
        return count

    freq_5 = freq_janela(5)
    freq_50 = freq_janela(50)
    FREQ_ESPERADA = 60

    scores = {}
    for n in range(1, 26):
        fc = freq_5[n]
        fl = freq_50[n]
        indice_debito = fl - fc
        consecutivos = contar_consecutivos(n)
        apareceu_recente = any(n in r['numeros'] for r in dados_historicos[:3])

        score = 0
        if consecutivos >= 10:
            score -= 5
        elif consecutivos >= 5:
            score += 6
        elif consecutivos >= 4:
            score += 5
        elif consecutivos >= 3 and fc >= 80:
            score += 4
        elif consecutivos >= 3:
            score += 3
        elif fc >= 100:
            score += 4
        elif fc >= 80 and apareceu_recente:
            score += 3
        elif indice_debito < -35:
            score += 2
        elif indice_debito < -25:
            score += 1
        elif indice_debito >= 0:
            score -= 2
        else:
            score -= 1

        if fc > FREQ_ESPERADA + 20:
            score += 1

        scores[n] = score
    return scores


# ═══════════════════════════════════════════════════════════════════════════
# QUADRANTES
# ═══════════════════════════════════════════════════════════════════════════

def montar_quadrantes_fixos():
    """Quadrantes fixos: Q1=1-5, Q2=6-10, Q3=11-15, Q4=16-20, Q5=21-25"""
    return {
        1: [1, 2, 3, 4, 5],
        2: [6, 7, 8, 9, 10],
        3: [11, 12, 13, 14, 15],
        4: [16, 17, 18, 19, 20],
        5: [21, 22, 23, 24, 25],
    }


def montar_quadrantes_dinamicos(scores):
    """
    Ordena os 25 números por score (desc) e divide em 5 quadrantes.
    Q1 = 5 números com MAIOR score (mais quentes/candidatos a exclusão)
    Q5 = 5 números com MENOR score (mais frios/devendo)
    """
    ordenados = sorted(range(1, 26), key=lambda n: (-scores[n], n))
    quadrantes = {}
    for i in range(5):
        quadrantes[i + 1] = sorted(ordenados[i * 5:(i + 1) * 5])
    return quadrantes


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 1: ANÁLISE DE CLUSTERING
# ═══════════════════════════════════════════════════════════════════════════

def analisar_clustering(todos_resultados, tipo_quadrante='fixo', janela_teste=200):
    """
    Para cada concurso, mede como os 10 ausentes se distribuem nos quadrantes.
    Se distribuição uniforme: 2 ausentes por quadrante.
    Se clustering: 3-5 ausentes no mesmo quadrante.
    """
    concursos = sorted(todos_resultados.keys())
    inicio = max(0, len(concursos) - janela_teste)
    concursos_teste = concursos[inicio:]

    distribuicoes = []  # lista de {q: n_ausentes}
    max_concentracoes = []  # máx ausentes num quadrante
    quadrantes_com_3plus = 0  # quantos concursos têm ≥3 ausentes em algum quadrante
    quadrante_zerado = 0  # quantos concursos têm 0 ausentes (todo quadrante saiu)

    for conc in concursos_teste:
        if conc not in todos_resultados:
            continue
        resultado = todos_resultados[conc]['set']
        ausentes = set(range(1, 26)) - resultado  # 10 números

        # Montar quadrantes
        if tipo_quadrante == 'fixo':
            quadrantes = montar_quadrantes_fixos()
        else:
            # Para dinâmico, precisaria do histórico anterior
            idx = concursos.index(conc)
            if idx < 50:
                continue
            historico = [todos_resultados[c] for c in concursos[:idx]]
            historico.sort(key=lambda x: x['concurso'], reverse=True)
            scores = calcular_score_invertida(historico)
            quadrantes = montar_quadrantes_dinamicos(scores)

        # Contar ausentes por quadrante
        dist = {}
        for q, nums in quadrantes.items():
            dist[q] = len([n for n in nums if n in ausentes])

        distribuicoes.append(dist)
        max_conc = max(dist.values())
        max_concentracoes.append(max_conc)

        if max_conc >= 3:
            quadrantes_com_3plus += 1
        if 0 in dist.values():
            quadrante_zerado += 1

    total = len(distribuicoes)
    if total == 0:
        print("   ⚠️ Sem dados suficientes.")
        return

    # Estatísticas
    avg_max = sum(max_concentracoes) / total
    freq_max = Counter(max_concentracoes)

    print(f"\n   📊 CLUSTERING DE AUSENTES ({tipo_quadrante.upper()}) — {total} concursos")
    print(f"   {'─' * 60}")
    print(f"   Distribuição uniforme esperada: 2 ausentes/quadrante")
    print(f"   Máx. concentração média:        {avg_max:.2f} ausentes/quadrante")
    print(f"   Concursos com ≥3 no mesmo Q:    {quadrantes_com_3plus}/{total} ({quadrantes_com_3plus/total*100:.1f}%)")
    print(f"   Concursos com Q zerado (0 aus): {quadrante_zerado}/{total} ({quadrante_zerado/total*100:.1f}%)")
    print()
    print(f"   Distribuição do máx. ausentes/quadrante:")
    for k in sorted(freq_max.keys()):
        barra = '█' * int(freq_max[k] / total * 50)
        print(f"      {k} ausentes: {freq_max[k]:4d} ({freq_max[k]/total*100:5.1f}%) {barra}")

    # Se clustering ≥3 em >50% dos concursos → significativo
    if quadrantes_com_3plus / total > 0.50:
        print(f"\n   ✅ CLUSTERING SIGNIFICATIVO! {quadrantes_com_3plus/total*100:.0f}% dos concursos concentram ≥3 ausentes")
    else:
        print(f"\n   ⚠️ Clustering moderado/fraco ({quadrantes_com_3plus/total*100:.0f}%)")

    return distribuicoes, max_concentracoes


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 2: BENCHMARK — ESTRATÉGIAS DE EXCLUSÃO (2 números, Pool 23)
# ═══════════════════════════════════════════════════════════════════════════

def benchmark_estrategias(todos_resultados, janela_teste=200, n_simulacoes_aleatorio=500):
    """
    Compara 5 estratégias de excluir 2 números:
    1. INVERTIDA v3.0 (top 2 do ranking geral)
    2. Top 2 do pior quadrante dinâmico (Q1)
    3. Top 1 de cada um dos 2 piores quadrantes dinâmicos
    4. Top 2 do pior quadrante fixo (mais ausentes na janela recente)
    5. Aleatório (baseline)
    """
    concursos = sorted(todos_resultados.keys())
    inicio = max(50, len(concursos) - janela_teste)
    concursos_teste = concursos[inicio:]

    # Contadores de acerto (exclusão correta = nenhum excluído saiu no resultado)
    resultados = {
        'invertida': {'acertos': 0, 'total': 0},
        'q_din_top2_pior': {'acertos': 0, 'total': 0},
        'q_din_1_cada_2piores': {'acertos': 0, 'total': 0},
        'q_fixo_pior_recente': {'acertos': 0, 'total': 0},
        'aleatorio': {'acertos': [], 'total': 0},
    }

    print(f"\n   🔬 BENCHMARK DE EXCLUSÃO (2 números) — {len(concursos_teste)} concursos")
    print(f"   {'─' * 60}")

    for i, conc in enumerate(concursos_teste):
        if conc not in todos_resultados:
            continue

        resultado = todos_resultados[conc]['set']
        idx = concursos.index(conc)
        if idx < 50:
            continue

        historico = [todos_resultados[c] for c in concursos[:idx]]
        historico.sort(key=lambda x: x['concurso'], reverse=True)
        scores = calcular_score_invertida(historico)

        # ───────────────────────────────────────────────────────
        # ESTRATÉGIA 1: INVERTIDA v3.0 (top 2 geral)
        # ───────────────────────────────────────────────────────
        ranking = sorted(range(1, 26), key=lambda n: (-scores[n], n))
        excluir_inv = set(ranking[:2])
        acertou = len(excluir_inv & resultado) == 0
        resultados['invertida']['acertos'] += int(acertou)
        resultados['invertida']['total'] += 1

        # ───────────────────────────────────────────────────────
        # ESTRATÉGIA 2: Top 2 do pior quadrante dinâmico (Q1)
        # ───────────────────────────────────────────────────────
        quadrantes_din = montar_quadrantes_dinamicos(scores)
        # Q1 = 5 números com maior score
        q1_nums = quadrantes_din[1]
        # Ordenar Q1 por score desc
        q1_sorted = sorted(q1_nums, key=lambda n: (-scores[n], n))
        excluir_q1 = set(q1_sorted[:2])
        acertou = len(excluir_q1 & resultado) == 0
        resultados['q_din_top2_pior']['acertos'] += int(acertou)
        resultados['q_din_top2_pior']['total'] += 1

        # ───────────────────────────────────────────────────────
        # ESTRATÉGIA 3: Top 1 de cada um dos 2 piores quadrantes
        # ───────────────────────────────────────────────────────
        # Q1 e Q2 = dois quadrantes com maiores scores
        q1_best = sorted(quadrantes_din[1], key=lambda n: (-scores[n], n))[0]
        q2_best = sorted(quadrantes_din[2], key=lambda n: (-scores[n], n))[0]
        excluir_div = {q1_best, q2_best}
        acertou = len(excluir_div & resultado) == 0
        resultados['q_din_1_cada_2piores']['acertos'] += int(acertou)
        resultados['q_din_1_cada_2piores']['total'] += 1

        # ───────────────────────────────────────────────────────
        # ESTRATÉGIA 4: Pior quadrante FIXO (por ausências recentes)
        # ───────────────────────────────────────────────────────
        quadrantes_fixos = montar_quadrantes_fixos()
        # Contar ausências de cada quadrante nos últimos 10 concursos
        q_ausencias = {}
        for q, nums in quadrantes_fixos.items():
            total_aus = 0
            for r in historico[:10]:
                total_aus += sum(1 for n in nums if n not in r['set'])
            q_ausencias[q] = total_aus
        pior_q = max(q_ausencias, key=q_ausencias.get)
        pior_q_nums = quadrantes_fixos[pior_q]
        # Top 2 com maior score dentro do pior quadrante fixo
        pior_sorted = sorted(pior_q_nums, key=lambda n: (-scores[n], n))
        excluir_fixo = set(pior_sorted[:2])
        acertou = len(excluir_fixo & resultado) == 0
        resultados['q_fixo_pior_recente']['acertos'] += int(acertou)
        resultados['q_fixo_pior_recente']['total'] += 1

        # ───────────────────────────────────────────────────────
        # ESTRATÉGIA 5: Aleatório (baseline)
        # ───────────────────────────────────────────────────────
        corretos_aleat = 0
        for _ in range(n_simulacoes_aleatorio):
            excluir_aleat = set(random.sample(range(1, 26), 2))
            if len(excluir_aleat & resultado) == 0:
                corretos_aleat += 1
        resultados['aleatorio']['acertos'].append(corretos_aleat / n_simulacoes_aleatorio)
        resultados['aleatorio']['total'] += 1

        if (i + 1) % 50 == 0:
            print(f"      Progresso: {i + 1}/{len(concursos_teste)} concursos...")

    # ═══════════════════════════════════════════════════════════════════
    # RESULTADOS
    # ═══════════════════════════════════════════════════════════════════
    total = resultados['invertida']['total']
    media_aleat = sum(resultados['aleatorio']['acertos']) / len(resultados['aleatorio']['acertos']) * 100

    print(f"\n{'═' * 70}")
    print(f"📊 RESULTADOS — {total} concursos testados")
    print(f"{'═' * 70}")
    print()

    estrategias = [
        ('INVERTIDA v3.0 (top 2 geral)', resultados['invertida']),
        ('Quadrante dinâmico: top 2 do Q1', resultados['q_din_top2_pior']),
        ('Quadrante dinâmico: 1 de cada Q1+Q2', resultados['q_din_1_cada_2piores']),
        ('Quadrante fixo: top 2 do pior Q', resultados['q_fixo_pior_recente']),
    ]

    print(f"   {'ESTRATÉGIA':<42} {'ACERTOS':>8} {'TAXA':>8} {'vs ALEAT':>10}")
    print(f"   {'─' * 70}")

    for nome, res in estrategias:
        taxa = res['acertos'] / res['total'] * 100
        diff = taxa - media_aleat
        simbolo = '✅' if diff > 0 else '❌'
        print(f"   {nome:<42} {res['acertos']:>5}/{res['total']:<3} {taxa:>6.1f}% {diff:>+8.1f}pp {simbolo}")

    print(f"   {'Aleatório (baseline)':<42} {'─':>8} {media_aleat:>6.1f}%     ── 🎲")
    print()

    # Probabilidade teórica aleatória para 2 exclusões
    # P(2 certos) = C(10,2)/C(25,2) = 45/300 = 15%
    print(f"   📐 Teórico aleatório P(2 certos de 10 ausentes): 15.0%")
    print(f"   🎲 Aleatório medido: {media_aleat:.1f}%")
    print()

    return resultados


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 3: ANÁLISE DE JANELAS — Padrão previsível nos quadrantes?
# ═══════════════════════════════════════════════════════════════════════════

def analisar_janelas_quadrantes(todos_resultados, janela_teste=200):
    """
    Analisa se o quadrante com mais ausentes tende a se repetir
    ou se há um padrão de rotação previsível.
    """
    concursos = sorted(todos_resultados.keys())
    inicio = max(50, len(concursos) - janela_teste)
    concursos_teste = concursos[inicio:]

    historico_pior_q_fixo = []
    historico_pior_q_din = []

    for conc in concursos_teste:
        if conc not in todos_resultados:
            continue
        resultado = todos_resultados[conc]['set']
        ausentes = set(range(1, 26)) - resultado

        idx = concursos.index(conc)
        if idx < 50:
            continue

        hist = [todos_resultados[c] for c in concursos[:idx]]
        hist.sort(key=lambda x: x['concurso'], reverse=True)
        scores = calcular_score_invertida(hist)

        # Quadrantes fixos — qual tem mais ausentes?
        qf = montar_quadrantes_fixos()
        aus_fixo = {q: sum(1 for n in nums if n in ausentes) for q, nums in qf.items()}
        pior_fixo = max(aus_fixo, key=aus_fixo.get)
        historico_pior_q_fixo.append(pior_fixo)

        # Quadrantes dinâmicos — qual tem mais ausentes?
        qd = montar_quadrantes_dinamicos(scores)
        aus_din = {q: sum(1 for n in nums if n in ausentes) for q, nums in qd.items()}
        pior_din = max(aus_din, key=aus_din.get)
        historico_pior_q_din.append(pior_din)

    print(f"\n{'═' * 70}")
    print(f"📊 ANÁLISE DE JANELAS — PADRÃO DE ROTAÇÃO DOS QUADRANTES")
    print(f"{'═' * 70}")

    for nome, historico in [('FIXO', historico_pior_q_fixo), ('DINÂMICO', historico_pior_q_din)]:
        total = len(historico)
        if total == 0:
            continue

        print(f"\n   🔹 Quadrantes {nome}:")

        # Frequência de cada quadrante como "pior"
        freq = Counter(historico)
        print(f"   Qual quadrante foi o PIOR (mais ausentes)?")
        for q in sorted(freq.keys()):
            barra = '█' * int(freq[q] / total * 50)
            print(f"      Q{q}: {freq[q]:4d} ({freq[q]/total*100:5.1f}%) {barra}")

        # Repetição: quantas vezes o pior Q se repete no concurso seguinte?
        repeticoes = sum(1 for i in range(1, total) if historico[i] == historico[i - 1])
        print(f"\n   Pior Q se repete no concurso seguinte: {repeticoes}/{total-1} ({repeticoes/(total-1)*100:.1f}%)")
        print(f"   Esperado aleatório (se uniforme em 5): ~20%")

        if repeticoes / (total - 1) > 0.25:
            print(f"   ✅ Tendência de PERSISTÊNCIA — pior quadrante tende a continuar!")
        elif repeticoes / (total - 1) < 0.15:
            print(f"   🔄 Tendência de ROTAÇÃO — pior quadrante tende a mudar!")
        else:
            print(f"   ⚖️ Sem padrão forte de persistência ou rotação.")

        # Análise de transição: pior Q(t) → pior Q(t+1)
        transicoes = Counter()
        for i in range(1, total):
            transicoes[(historico[i - 1], historico[i])] += 1

        print(f"\n   Top 5 transições Q(t) → Q(t+1):")
        for (q_de, q_para), cnt in transicoes.most_common(5):
            pct = cnt / (total - 1) * 100
            print(f"      Q{q_de} → Q{q_para}: {cnt:3d} ({pct:.1f}%)")

    # Análise por período (últimos 20, 50, 100, 200)
    print(f"\n{'═' * 70}")
    print(f"📊 TAXA DE ACERTO POR PERÍODO (Quadrante Dinâmico Q1)")
    print(f"{'═' * 70}")
    print(f"   Teste: excluir top 2 do Q1 dinâmico")
    print()

    for periodo in [20, 50, 100, 200]:
        sliced = historico_pior_q_din[-periodo:] if len(historico_pior_q_din) >= periodo else historico_pior_q_din
        # Q1 = pior quadrante (mais quentes). Contar quantas vezes Q1 foi realmente o "pior"
        q1_como_pior = sum(1 for q in sliced if q == 1)
        total_p = len(sliced)
        print(f"   Últimos {periodo:>3}: Q1 foi pior em {q1_como_pior}/{total_p} ({q1_como_pior/total_p*100:.1f}%) — esperado 20%")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║      BENCHMARK: QUADRANTES PARA EXCLUSÃO DE NÚMEROS             ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    print("\n📥 Carregando resultados...")
    todos = carregar_resultados()
    print(f"   ✅ {len(todos)} concursos carregados")

    # ─── ETAPA 1: Análise de clustering ───
    print("\n" + "═" * 70)
    print("📋 ETAPA 1: ANÁLISE DE CLUSTERING (ausentes se concentram?)")
    print("═" * 70)
    analisar_clustering(todos, tipo_quadrante='fixo', janela_teste=200)
    analisar_clustering(todos, tipo_quadrante='dinamico', janela_teste=200)

    # ─── ETAPA 2: Benchmark de estratégias ───
    print("\n" + "═" * 70)
    print("📋 ETAPA 2: BENCHMARK DE ESTRATÉGIAS (2 exclusões)")
    print("═" * 70)
    benchmark_estrategias(todos, janela_teste=200, n_simulacoes_aleatorio=500)

    # ─── ETAPA 3: Análise de janelas ───
    print("\n" + "═" * 70)
    print("📋 ETAPA 3: PADRÃO DE ROTAÇÃO DOS QUADRANTES")
    print("═" * 70)
    analisar_janelas_quadrantes(todos, janela_teste=200)

    print("\n" + "═" * 70)
    print("✅ BENCHMARK CONCLUÍDO!")
    print("═" * 70)
