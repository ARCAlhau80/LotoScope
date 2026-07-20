#!/usr/bin/env python3
"""
ia_lotoscope.py — Agente de análise estatística com IA local (Ollama)
Conecta no SQL Server, carrega resultados de qualquer loteria, computa
estatísticas e envia ao modelo local para análise em linguagem natural.
Saída exportada para .md com timestamp.

Flags:
  --json         Saída em JSON (para consumo via API)
  --compare N    Análise comparativa entre época atual e N concursos atrás
  --no-save      Não salva memória no grafo
  --no-context   Não carrega contexto de memórias anteriores
"""

import sys
import json
import math

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import argparse
import subprocess
import urllib.request
import urllib.error
import urllib
from datetime import datetime
from pathlib import Path
from typing import Any
from collections import Counter

try:
    import pyodbc
except ImportError:
    print("pyodbc nao instalado. Rode: pip install pyodbc")
    sys.exit(1)

# ── CONFIGURACOES ──────────────────────────────────────────────────────────────

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma-lotto"

LOTERIAS = {
    "lotofacil": {
        "nome": "Lotofacil",
        "tabela": "Resultados_INT",
        "cols_num": [f"N{i}" for i in range(1, 16)],
        "total_numeros": 25,
        "numeros_por_jogo": 15,
        "min": 1, "max": 25,
    },
    "megasena": {
        "nome": "Mega-Sena",
        "tabela": "Resultados_MegaSenaFechado",
        "cols_num": [f"N{i}" for i in range(1, 7)],
        "total_numeros": 60,
        "numeros_por_jogo": 6,
        "min": 1, "max": 60,
    },
    "quina": {
        "nome": "Quina",
        "tabela": "Resultados_Quina",
        "cols_num": [f"N{i}" for i in range(1, 6)],
        "total_numeros": 80,
        "numeros_por_jogo": 5,
        "min": 1, "max": 80,
    },
    "duplasena": {
        "nome": "Dupla Sena",
        "tabela": "Resultados_DuplaSena",
        "cols_num": [f"N{i}" for i in range(1, 7)],
        "cols_num2": [f"S2_N{i}" for i in range(1, 7)],
        "total_numeros": 50,
        "numeros_por_jogo": 6,
        "min": 1, "max": 50,
    },
    "lotomania": {
        "nome": "Lotomania",
        "tabela": "Resultados_Lotomania",
        "cols_num": [f"N{i}" for i in range(1, 21)],
        "total_numeros": 100,
        "numeros_por_jogo": 50,
        "min": 0, "max": 99,
    },
    "supersete": {
        "nome": "Super Sete",
        "tabela": "Resultados_SuperSete",
        "cols_num": [f"N{i}" for i in range(1, 8)],
        "total_numeros": 10,
        "numeros_por_jogo": 7,
        "min": 0, "max": 9,
        "is_positional": True,
    },
}

PRIMOS = {
    "lotofacil": [2, 3, 5, 7, 11, 13, 17, 19, 23],
    "megasena": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59],
    "quina": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79],
    "duplasena": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
    "lotomania": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97],
    "supersete": [],
}

FIBONACCI = {
    "lotofacil": [1, 2, 3, 5, 8, 13, 21],
    "megasena": [1, 2, 3, 5, 8, 13, 21, 34, 55],
    "quina": [1, 2, 3, 5, 8, 13, 21, 34, 55],
    "duplasena": [1, 2, 3, 5, 8, 13, 21, 34],
    "lotomania": [1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
    "supersete": [],
}

PRIMOS_PADRAO = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
FIB_PADRAO = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]


# ── BANCO ──────────────────────────────────────────────────────────────────────

def conectar() -> pyodbc.Connection:
    return pyodbc.connect(CONN_STR)


def carregar_resultados(conn: pyodbc.Connection, loteria_id: str) -> list[list[int]]:
    cfg = LOTERIAS[loteria_id]
    cursor = conn.cursor()

    cursor.execute(f"SELECT TOP 0 * FROM {cfg['tabela']}")
    colunas_reais = [c[0] for c in cursor.description]
    col_concurso = next((c for c in colunas_reais if c.lower() == "concurso"), "Concurso")
    colunas_validas = [c for c in cfg["cols_num"] if c in colunas_reais]

    if not colunas_validas:
        return []

    cols_sql = ", ".join([col_concurso] + colunas_validas)
    cursor.execute(f"SELECT {cols_sql} FROM {cfg['tabela']} ORDER BY {col_concurso}")
    linhas = []
    for r in cursor.fetchall():
        nums = [int(getattr(r, c)) for c in colunas_validas if getattr(r, c) is not None]
        linhas.append(nums)
    return linhas


# ── ESTATISTICAS ───────────────────────────────────────────────────────────────

def estatisticas_globais(resultados: list[list[int]], loteria_id: str) -> dict:
    cfg = LOTERIAS[loteria_id]
    total = len(resultados)
    if total == 0:
        return {}

    ultimo = resultados[-1]
    todas_dezenas = [n for r in resultados for n in r]
    freq_global = Counter(todas_dezenas)

    janela = min(30, total)
    recente = [n for r in resultados[-janela:] for n in r]
    freq_recente = Counter(recente)

    all_nums = list(range(cfg["min"], cfg["max"] + 1))

    gaps = {}
    for n in all_nums:
        ultima_pos = -1
        for idx, r in enumerate(resultados):
            if n in r:
                ultima_pos = idx
        gaps[n] = total - 1 - ultima_pos

    qty = 9 if cfg["total_numeros"] >= 25 else 5
    quentes = [n for n, _ in sorted(freq_recente.items(), key=lambda x: -x[1])[:qty]]
    frios = sorted(
        [(n, f) for n, f in freq_recente.items()],
        key=lambda x: (x[1], -freq_global[x[0]]),
    )[:qty]
    frios = [n for n, _ in frios]

    primos_lista = PRIMOS.get(loteria_id, PRIMOS_PADRAO)
    fib_lista = FIBONACCI.get(loteria_id, FIB_PADRAO)
    penultimo_set = set(resultados[-2]) if total > 1 else set()
    ultimo_set = set(ultimo)

    p90_gap = sorted(gaps.values())[int(len(gaps) * 0.9)]

    return {
        "total_sorteios": total,
        "ultimo_concurso": ultimo,
        "frequencia_global": {str(n): freq_global.get(n, 0) for n in all_nums},
        "frequencia_30": {str(n): freq_recente.get(n, 0) for n in all_nums},
        "gaps": {str(n): gaps[n] for n in all_nums},
        "quentes": quentes,
        "frios": frios,
        "soma_ultimo": sum(ultimo),
        "media_soma": sum(sum(r) for r in resultados) / total,
        "pares_ultimo": sum(1 for n in ultimo if n % 2 == 0),
        "impares_ultimo": sum(1 for n in ultimo if n % 2 != 0),
        "primos_ultimo": sum(1 for n in ultimo if n in primos_lista),
        "fib_ultimo": sum(1 for n in ultimo if n in fib_lista),
        "repetidos_ultimo": len(ultimo_set & penultimo_set),
        "amplitude_ultimo": max(ultimo) - min(ultimo),
        "p90_gap": p90_gap,
        "qtd_acima_p90": sum(1 for g in gaps.values() if g >= p90_gap),
    }


def analise_posicional_supersete(resultados: list[list[int]]) -> dict:
    total = len(resultados)
    if total < 2:
        return {}

    num_pos = 7
    transicoes = [Counter() for _ in range(num_pos)]
    freq_pos = [Counter() for _ in range(num_pos)]

    for i in range(1, total):
        for p in range(num_pos):
            transicoes[p][(resultados[i - 1][p], resultados[i][p])] += 1

    for r in resultados:
        for p in range(num_pos):
            freq_pos[p][r[p]] += 1

    ultimo = resultados[-1]
    penultimo = resultados[-2]

    saida = {"posicoes": []}
    for p in range(num_pos):
        total_trans = sum(transicoes[p].values())
        mais_comum = transicoes[p].most_common(5)
        digitos_ordenados = sorted(freq_pos[p].items(), key=lambda x: -x[1])

        saida["posicoes"].append({
            "posicao": p + 1,
            "ultimo_digito": ultimo[p],
            "anterior_digito": penultimo[p],
            "mudou": ultimo[p] != penultimo[p],
            "frequencia_posicional": {str(d): c for d, c in digitos_ordenados},
            "top_transicoes": [
                {"de": t[0][0], "para": t[0][1], "count": t[1],
                 "pct": round(t[1] / total_trans * 100, 1) if total_trans else 0}
                for t in mais_comum
            ],
        })

    return saida


# ── CICLOS (aquecendo/esfriando) ───────────────────────────────────────────────

def carregar_ciclos(resultados: list[list[int]],
                    loteria_id: str) -> dict[str, dict]:
    """Computa ciclo de cada numero: freq_30 vs freq_esperada."""
    cfg = LOTERIAS[loteria_id]
    total = len(resultados)
    if total == 0:
        return {}
    todas_dezenas = [n for r in resultados for n in r]
    freq_global = Counter(todas_dezenas)
    janela = min(30, total)
    recente = [n for r in resultados[-janela:] for n in r]
    freq_recente = Counter(recente)
    all_nums = list(range(cfg["min"], cfg["max"] + 1))
    ciclos: dict[str, dict] = {}
    for n in all_nums:
        freq_esp = freq_global.get(n, 0) / total * janela
        diff = freq_recente.get(n, 0) - freq_esp
        if diff > 1.5:
            estado = "aquecendo"
        elif diff < -1.5:
            estado = "esfriando"
        else:
            estado = "estavel"
        ciclos[str(n)] = {
            "freq_30": freq_recente.get(n, 0),
            "freq_esperada": round(freq_esp, 1),
            "diferenca": round(diff, 1),
            "estado": estado,
        }
    return ciclos


# ── MATRIZ DE QUARENTENA POR POSICAO ──────────────────────────────────────────

def carregar_quarentena_posicoes(
    resultados: list[list[int]],
    loteria_id: str,
    fator_quarentena: float = 0.35,
) -> dict[str, dict]:
    """Computa matriz de quarentena por posicao (N1..N15).
    Para cada posicao x numero: gap, media, sigma, p90, status.
    """
    cfg = LOTERIAS[loteria_id]
    total = len(resultados)
    if total < 2:
        return {}
    num_pos = cfg["numeros_por_jogo"]
    all_nums = list(range(cfg["min"], cfg["max"] + 1))
    quarentena: dict[str, dict] = {}

    for p in range(num_pos):
        pos = f"N{p + 1}"
        sequencia = [r[p] for r in resultados]
        nums_info = []
        em_quarentena = []
        atrasados = []
        muito_atrasados = []

        for num in all_nums:
            gaps = []
            ultima_pos = None
            for i, val in enumerate(sequencia):
                if val == num:
                    if ultima_pos is not None:
                        gaps.append(i - ultima_pos)
                    ultima_pos = i

            gap_atual = (total - 1 - ultima_pos) if ultima_pos is not None else total

            if len(gaps) < 2:
                nums_info.append({
                    "digito": num,
                    "gap_atual": gap_atual,
                    "media": 0, "mediana": 0, "sigma": 0, "p90": 0,
                    "status": "normal",
                })
                continue

            sorted_gaps = sorted(gaps)
            media = sum(gaps) / len(gaps)
            mediana = (sorted_gaps[len(sorted_gaps) // 2]
                       if len(sorted_gaps) % 2
                       else (sorted_gaps[len(sorted_gaps) // 2 - 1] +
                             sorted_gaps[len(sorted_gaps) // 2]) / 2)
            variancia = sum((g - media) ** 2 for g in gaps) / len(gaps)
            sigma = math.sqrt(variancia)
            p90_idx = min(len(sorted_gaps) - 1,
                          max(0, math.ceil(len(sorted_gaps) * 0.9) - 1))
            p90 = sorted_gaps[p90_idx]

            if gap_atual <= 3:
                status = "quarentena"
                em_quarentena.append(num)
            elif gap_atual > p90:
                status = "muito_atrasado"
                muito_atrasados.append(num)
            elif gap_atual > media + fator_quarentena * sigma:
                status = "atrasado"
                atrasados.append(num)
            else:
                status = "normal"

            nums_info.append({
                "digito": num,
                "gap_atual": gap_atual,
                "media": round(media, 1),
                "mediana": round(mediana, 1),
                "sigma": round(sigma, 1),
                "p90": round(p90, 1),
                "status": status,
            })

        quarentena[pos] = {
            "posicao": pos,
            "numeros": nums_info,
            "em_quarentena": em_quarentena,
            "atrasados": atrasados,
            "muito_atrasados": muito_atrasados,
        }

    return quarentena


# ── FREQUENCIA POR POSICAO ──────────────────────────────────────────────────

def carregar_frequencia_posicoes(
    resultados: list[list[int]],
    loteria_id: str,
) -> dict[str, dict]:
    """Computa frequencia de cada numero por posicao (N1..N15).
    Retorna top 5 numeros + ultimos 3 que apareceram em cada posicao.
    """
    cfg = LOTERIAS[loteria_id]
    total = len(resultados)
    if total == 0:
        return {}
    num_pos = cfg["numeros_por_jogo"]
    all_nums = list(range(cfg["min"], cfg["max"] + 1))
    freq_posicoes: dict[str, dict] = {}

    for p in range(num_pos):
        pos = f"N{p + 1}"
        sequencia = [r[p] for r in resultados]
        freq = Counter(sequencia)
        ordenados = sorted(freq.items(), key=lambda x: -x[1])
        top5 = [(int(n), c) for n, c in ordenados[:5]]
        ultimos3 = [int(sequencia[-(i + 1)]) for i in range(min(3, total))]

        freq_info: dict[str, list | dict] = {}
        for n in all_nums:
            freq_info[str(n)] = {
                "freq": freq.get(n, 0),
                "pct": round(freq.get(n, 0) / total * 100, 1),
            }

        freq_posicoes[pos] = {
            "top5": top5,
            "ultimos3": ultimos3,
            "frequencia": freq_info,
        }

    return freq_posicoes


# ── CICLOS (NumerosCiclos table - SQL Server) ──────────────────────────────

def carregar_ciclos_tabela(conn: pyodbc.Connection) -> dict:
    """Carrega dados da tabela NumerosCiclos para Lotofacil.
    Retorna ciclo atual, historico por numero e comparacao.
    """
    cur = conn.cursor()
    # Ultimos 20 ciclos completos + atual
    cur.execute("""
        SELECT Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento
        FROM NumerosCiclos
        WHERE Ciclo > (SELECT MAX(Ciclo) - 20 FROM NumerosCiclos)
        ORDER BY Ciclo, Numero
    """)
    linhas = cur.fetchall()
    if not linhas:
        return {}

    ciclos: dict[int, dict] = {}
    for r in linhas:
        ciclo = r.Ciclo
        if ciclo not in ciclos:
            total_conc = (r.ConcursoFechamento or 0) - (r.ConcursoInicio or 0)
            fechado = r.ConcursoFechamento is not None
            ciclos[ciclo] = {
                "ciclo": ciclo,
                "inicio": r.ConcursoInicio,
                "fim": r.ConcursoFechamento,
                "total_concursos": total_conc if fechado else None,
                "fechado": fechado,
                "numeros": {},
            }
        ciclos[ciclo]["numeros"][str(r.Numero)] = r.QtdSorteados

    # Ordenar por ciclo
    sorted_ciclos = sorted(ciclos.values(), key=lambda x: -x["ciclo"])
    if not sorted_ciclos:
        return {}

    atual = sorted_ciclos[0]
    historicos = sorted_ciclos[1:]

    # Media historica por numero (ciclos anteriores)
    medias: dict[str, dict] = {}
    for n in range(1, 26):
        ns = str(n)
        vals = [c["numeros"].get(ns, 0) for c in historicos if ns in c["numeros"]]
        if vals:
            media = sum(vals) / len(vals)
            qtd_atual = atual["numeros"].get(ns, 0)
            diff = qtd_atual - media
            medias[ns] = {
                "qtd_atual": qtd_atual,
                "media_historica": round(media, 1),
                "diferenca": round(diff, 1),
                "tendencia": "acima" if diff > 1 else ("abaixo" if diff < -1 else "normal"),
            }
        else:
            medias[ns] = {
                "qtd_atual": atual["numeros"].get(ns, 0),
                "media_historica": 0,
                "diferenca": 0,
                "tendencia": "normal",
            }

    return {
        "ciclo_atual": atual["ciclo"],
        "concursos_ciclo_atual": atual.get("total_concursos"),
        "fechado": atual["fechado"],
        "numeros": medias,
        "historico_media_geral": round(
            sum(m["media_historica"] for m in medias.values()) / 25, 1
        ) if medias else 0,
    }


def _formatar_ciclos_tabela_para_prompt(dados: dict) -> str:
    saida = f"### Ciclo {dados['ciclo_atual']} (NumerosCiclos)\n"
    if dados["concursos_ciclo_atual"] is not None:
        saida += f"Concursos no ciclo atual: {dados['concursos_ciclo_atual']}\n"
    acima = [n for n, m in dados["numeros"].items() if m["tendencia"] == "acima"]
    abaixo = [n for n, m in dados["numeros"].items() if m["tendencia"] == "abaixo"]
    zerados = [n for n, m in dados["numeros"].items() if m["qtd_atual"] == 0]
    if acima:
        saida += f"Acima da media historica: {', '.join(acima)}\n"
    if abaixo:
        saida += f"Abaixo da media historica: {', '.join(abaixo)}\n"
    if zerados:
        saida += f"Ainda nao sorteados neste ciclo: {', '.join(zerados)}\n"
    saida += f"Media historica geral do ciclo: {dados['historico_media_geral']} sorteios/numero\n"
    saida += "Legenda: acima/abaixo = diferenca >|1| sorteio vs media historica\n"
    return saida


# ── FORMATACAO DE CICLOS / QUARENTENA / FREQ POSICOES PARA PROMPT ───────────

def _formatar_ciclos_para_prompt(ciclos: dict[str, dict]) -> str:
    saida = "### Ciclos (freq_30 vs esperada)\n"
    aquecendo = [n for n, c in ciclos.items() if c["estado"] == "aquecendo"]
    esfriando = [n for n, c in ciclos.items() if c["estado"] == "esfriando"]
    estaveis = [n for n, c in ciclos.items() if c["estado"] == "estavel"]
    if aquecendo:
        saida += f"Aquecendo (freq > esperada): {', '.join(aquecendo)}\n"
    if esfriando:
        saida += f"Esfriando (freq < esperada): {', '.join(esfriando)}\n"
    saida += f"Estaveis: {len(estaveis)} numeros\n"
    return saida


def _formatar_quarentena_para_prompt(q: dict[str, dict]) -> str:
    saida = "### Matriz de Quarentena por Posicao\n"
    for pos, info in q.items():
        pq = info["em_quarentena"]
        pa = info["atrasados"]
        pm = info["muito_atrasados"]
        partes = []
        if pq:
            partes.append(f"Q={pq}")
        if pa:
            partes.append(f"A={pa}")
        if pm:
            partes.append(f"MA={pm}")
        saida += f"{pos}: {', '.join(partes)}\n"
    saida += "Legenda: Q=quarentena A=atrasado MA=muito_atrasado\n"
    return saida


def _formatar_frequencia_posicoes_para_prompt(fp: dict[str, dict]) -> str:
    saida = "### Freq. por Posicao (top 5 numeros)\n"
    for pos, info in fp.items():
        top5 = info["top5"]
        ultimos3 = info["ultimos3"]
        saida += f"{pos}: top={[n for n, _ in top5]} ultimos={ultimos3}\n"
    saida += "Os numeros em cada posicao sao ordenados do menor (N1) ao maior (N15).\n"
    return saida


# ── PROMPTS ────────────────────────────────────────────────────────────────────

def _top_diferencas(est: dict) -> str:
    total = max(1, est["total_sorteios"])
    janela = min(30, total)
    items = sorted(est['frequencia_global'],
                   key=lambda x: -(abs(est["frequencia_global"][x] / total -
                                       est["frequencia_30"][x] / max(1, janela))))[:5]
    return "\n".join(
        f'{n}: global={est["frequencia_global"][n]} | recente={est["frequencia_30"][n]}'
        for n in items
    )


def montar_prompt(est: dict, cfg: dict, contexto_anterior: str = "",
                  ciclos: dict[str, dict] | None = None,
                  quarentena: dict[str, dict] | None = None,
                  freq_posicoes: dict[str, dict] | None = None,
                  ciclos_tabela: dict | None = None) -> str:
    ctx = ""
    if contexto_anterior:
        ctx = f"\n### Contexto de analises anteriores\n{contexto_anterior}\n"

    extra = ""
    if ciclos:
        extra += "\n" + _formatar_ciclos_para_prompt(ciclos)
    if quarentena:
        extra += "\n" + _formatar_quarentena_para_prompt(quarentena)
    if freq_posicoes:
        extra += "\n" + _formatar_frequencia_posicoes_para_prompt(freq_posicoes)
    if ciclos_tabela:
        extra += "\n" + _formatar_ciclos_tabela_para_prompt(ciclos_tabela)

    return f"""## Dados Estatisticos - {cfg['nome']}{ctx}

### Ultimo Sorteio
Numeros: {est['ultimo_concurso']}
Soma: {est['soma_ultimo']} (media historica: {est['media_soma']:.1f})
Pares: {est['pares_ultimo']} | Impares: {est['impares_ultimo']}
Primos: {est['primos_ultimo']} | Fibonacci: {est['fib_ultimo']}
Repetidos vs anterior: {est['repetidos_ultimo']}
Amplitude: {est['amplitude_ultimo']}

### Top Quentes (ultimos 30)
{', '.join(str(n) for n in est['quentes'])}

### Top Frios (ultimos 30)
{', '.join(str(n) for n in est['frios'])}

### Gaps (sorteios sem sair)
P90 gap: {est['p90_gap']} | Acima do P90: {est['qtd_acima_p90']} numeros
Maiores gaps: {', '.join(f'{n}({est["gaps"][str(n)]})' for n in sorted(est['gaps'], key=lambda x: -est['gaps'][x])[:5])}

### Frequencia Global vs Recente (top 5 diferencas)
{_top_diferencas(est)}
{extra}
---
Com base estritamente nos dados acima, realize uma analise em portugues do Brasil cobrindo:
1. Distribuicao do ultimo sorteio vs media historica (soma, paridade, primos)
2. Anomalias de frequencia (numeros muito acima ou abaixo do esperado)
3. Tendencias de atraso - gaps acima do P90
4. Ciclos: numeros aquecendo e esfriando
5. Matriz de Quarentena: numeros por posicao (Q/A/MA)
6. Analise da tabela NumerosCiclos: compare o ciclo atual com ciclos anteriores — quais numeros estao acima/abaixo da media? Quais ainda nao sairam? O que isso sugere?
7. Sugestao de NUMEROS POR POSICAO (N1 a N15) — para cada posicao, indique 1 a 3 numeros candidatos com base na frequencia historica da posicao, gaps, quarentena, ciclo atual vs historico e tendencias de ciclo. Justifique cada sugestao.
Use formato estruturado com topicos. Seja analitico, nao especulativo.
"""


def montar_prompt_supersete(est: dict, pos: dict, contexto_anterior: str = "") -> str:
    ctx = ""
    if contexto_anterior:
        ctx = f"\n### Contexto de analises anteriores\n{contexto_anterior}\n"

    prompt = f"""## Dados Estatisticos - Super Sete{ctx}

### Ultimo Sorteio
Numeros: {est['ultimo_concurso']}
Soma: {est['soma_ultimo']} (media historica: {est['media_soma']:.1f})
Pares: {est['pares_ultimo']} | Impares: {est['impares_ultimo']}

### Top Quentes (ultimos 30)
{', '.join(str(n) for n in est['quentes'])}

### Top Frios (ultimos 30)
{', '.join(str(n) for n in est['frios'])}

### Gaps (sorteios sem sair)
P90 gap: {est['p90_gap']} | Acima do P90: {est['qtd_acima_p90']} numeros
Maiores gaps: {', '.join(f'{n}({est["gaps"][str(n)]})' for n in sorted(est['gaps'], key=lambda x: -est['gaps'][x])[:5])}

### Frequencia Global vs Recente (top 5 diferencas)
{_top_diferencas(est)}

### Analise Posicional (transicao de digitos por coluna)
"""
    for pos_info in pos["posicoes"]:
        ant = pos_info["anterior_digito"]
        ult = pos_info["ultimo_digito"]
        seta = "->" if pos_info["mudou"] else "=="
        prompt += f"\nColuna {pos_info['posicao']}: {ant} {seta} {ult}"
        prompt += "\n  Top transicoes: " + ", ".join(
            f"{t['de']}->{t['para']} ({t['pct']}%)"
            for t in pos_info["top_transicoes"][:3]
        )
        sorted_freq = sorted(pos_info["frequencia_posicional"].items(), key=lambda x: -x[1])
        prompt += "\n  Frequencia: " + ", ".join(f"{d}({c}x)" for d, c in sorted_freq[:5])

    prompt += """

---
Com base estritamente nos dados acima, realize uma analise em portugues do Brasil cobrindo:
1. Distribuicao do ultimo sorteio vs media historica (soma, paridade)
2. Anomalias de frequencia e tendencias de atraso
3. Analise posicional: padroes de transicao por coluna (digitos que mais se repetem vs mudam)
4. Sugestao de enfoque para os proximos sorteios com base nos dados
Use formato estruturado com topicos. Seja analitico, nao especulativo.
"""
    return prompt


def montar_prompt_compare(resultados_atuais: list[list[int]],
                          resultados_antigos: list[list[int]],
                          loteria_id: str, n_concursos: int) -> str:
    cfg = LOTERIAS[loteria_id]
    est_atual = estatisticas_globais(resultados_atuais, loteria_id)
    est_antigo = estatisticas_globais(resultados_antigos, loteria_id)

    return f"""## Dados Comparativos - {cfg['nome']}

### Epoca ATUAL (ultimos {min(30, len(resultados_atuais))} sorteios)
Ultimo numero: {resultados_atuais[-1]}
Soma media: {est_atual['media_soma']:.1f}
Pares_media: {est_atual.get('pares_ultimo', 0)} | Impares_media: {est_atual.get('impares_ultimo', 0)}
Quentes: {', '.join(str(n) for n in est_atual['quentes'])}
Frios: {', '.join(str(n) for n in est_atual['frios'])}
Maiores gaps: {', '.join(f'{n}({est_atual["gaps"][str(n)]})' for n in sorted(est_atual['gaps'], key=lambda x: -est_atual['gaps'][x])[:5])}

### Epoca PASSADA ({n_concursos} concursos atras - ultimos {min(30, len(resultados_antigos))} sorteios da epoca)
Ultimo numero: {resultados_antigos[-1]}
Soma media: {est_antigo['media_soma']:.1f}
Pares_media: {est_antigo.get('pares_ultimo', 0)} | Impares_media: {est_antigo.get('impares_ultimo', 0)}
Quentes: {', '.join(str(n) for n in est_antigo['quentes'])}
Frios: {', '.join(str(n) for n in est_antigo['frios'])}
Maiores gaps: {', '.join(f'{n}({est_antigo["gaps"][str(n)]})' for n in sorted(est_antigo['gaps'], key=lambda x: -est_antigo['gaps'][x])[:5])}

### O que realmente aconteceu entre as duas epocas
Numeros sorteados nos ultimos {n_concursos} concursos:
{', '.join(str(r[-1]) for r in resultados_atuais[-n_concursos:])[:200]}

---
Analise comparativa em portugues do Brasil:
1. Como o perfil dos numeros quentes/frios mudou entre as duas epocas?
2. As anomalias detectadas na epoca passada se confirmaram?
3. Houve mudanca no comportamento (soma, paridade, amplitude)?
4. O que isso sugere para os proximos sorteios?
Seja analitico. Nao invente dados.
"""


# ── OLLAMA ─────────────────────────────────────────────────────────────────────

class OllamaError(Exception):
    pass


class OllamaOcupadoError(Exception):
    pass


def chamar_ollama(prompt: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "top_p": 0.9},
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
            resposta = result.get("response", "")
            if not resposta:
                raise OllamaError("Resposta vazia do Ollama")
            return resposta
    except urllib.error.HTTPError as e:
        corpo = e.read().decode()[:300]
        if e.code == 503:
            raise OllamaOcupadoError(f"Ollama ocupado (503): {corpo}")
        raise OllamaError(f"Erro HTTP {e.code}: {corpo}")
    except urllib.error.URLError as e:
        raise OllamaError(f"Ollama nao esta rodando ({e.reason})")
    except (json.JSONDecodeError, KeyError) as e:
        raise OllamaError(f"Resposta invalida do Ollama: {e}")


# ── MEMORIA (agf) ──────────────────────────────────────────────────────────────

def carregar_memorias(loteria_id: str, limite: int = 3) -> tuple[str, int]:
    """Busca analises anteriores no grafo via agf memory search.
    Retorna (texto_contexto, quantidade_de_memorias)."""
    try:
        r = subprocess.run(
            ["agf", "memory", "search", loteria_id, "--limit", str(limite)],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return "", 0
        data = json.loads(r.stdout)
        if not data.get("ok") or not data.get("data"):
            return "", 0
        memorias = data["data"]
        if isinstance(memorias, list) and len(memorias) > 0:
            trechos = []
            for m in memorias[:limite]:
                nome = m.get("name", m.get("id", "?"))
                snippet = m.get("content", m.get("snippet", ""))
                if len(snippet) > 300:
                    snippet = snippet[:300] + "..."
                trechos.append(f"[{nome}] {snippet}")
            return "\n".join(trechos), len(trechos)
        return "", 0
    except Exception:
        return "", 0


def salvar_memoria(loteria_id: str, nome_jogo: str, resposta_ia: str, args: Any) -> None:
    """Salva a analise como memoria no grafo."""
    if args.no_save:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    nome = f"analise_{loteria_id}_{timestamp}"
    conteudo = f"# Analise {nome_jogo} - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n{resposta_ia}"
    try:
        subprocess.run(
            ["agf", "memory", "write", nome, "--content", conteudo],
            capture_output=True, text=True, timeout=10,
        )
    except Exception:
        pass


# ── ANALISE ────────────────────────────────────────────────────────────────────

def analisar_loteria(conn: pyodbc.Connection, loteria_id: str,
                     args: Any) -> dict:
    """Executa analise de uma loteria.
    Retorna dict com {loteria, nome, sorteios, analise, timestamp, memorias_carregadas}.
    """
    cfg = LOTERIAS[loteria_id]
    resultados = carregar_resultados(conn, loteria_id)
    total = len(resultados)

    resultado = {
        "loteria": loteria_id,
        "nome": cfg["nome"],
        "sorteios": total,
        "timestamp": datetime.now().isoformat(),
        "memorias_carregadas": 0,
    }

    if total == 0:
        resultado["analise"] = "Sem dados disponiveis."
        return resultado

    # RAG: carrega memorias anteriores
    contexto_anterior = ""
    if not args.no_context:
        ctx_texto, qtd_mem = carregar_memorias(loteria_id)
        contexto_anterior = ctx_texto
        resultado["memorias_carregadas"] = qtd_mem

    if not args.json:
        print(f"  Enviando {cfg['nome']} para IA...", flush=True)

    # Modo COMPARE
    if args.compare and args.compare > 0 and args.compare < total:
        n = args.compare
        resultados_antigos = resultados[:total - n]
        prompt = montar_prompt_compare(resultados, resultados_antigos, loteria_id, n)
    else:
        est = estatisticas_globais(resultados, loteria_id)
        if loteria_id == "supersete" and cfg.get("is_positional"):
            pos = analise_posicional_supersete(resultados)
            prompt = montar_prompt_supersete(est, pos, contexto_anterior)
        else:
            eh_lf = loteria_id == "lotofacil"
            ciclos_dados = carregar_ciclos(resultados, loteria_id) if eh_lf else None
            quarentena_dados = carregar_quarentena_posicoes(resultados, loteria_id) if eh_lf else None
            freq_pos_dados = carregar_frequencia_posicoes(resultados, loteria_id) if eh_lf else None
            ciclos_tabela_dados = carregar_ciclos_tabela(conn) if eh_lf else None
            prompt = montar_prompt(est, cfg, contexto_anterior,
                                   ciclos=ciclos_dados,
                                   quarentena=quarentena_dados,
                                   freq_posicoes=freq_pos_dados,
                                   ciclos_tabela=ciclos_tabela_dados)

    resposta = chamar_ollama(prompt)
    resultado["analise"] = resposta
    resultado["prompt"] = prompt

    # Salva memoria no grafo
    salvar_memoria(loteria_id, cfg["nome"], resposta, args)

    return resultado


# ── SETUP OLLAMA ───────────────────────────────────────────────────────────────

def verificar_modelo_ollama() -> None:
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=10) as resp:
            modelos = json.loads(resp.read())
            nomes = [m["name"].removesuffix(":latest") for m in modelos.get("models", [])]
            if OLLAMA_MODEL not in nomes:
                print(f"\nModelo '{OLLAMA_MODEL}' nao encontrado.")
                criar = input("Criar agora via Modelfile? (s/N): ").strip().lower()
                if criar == "s":
                    if not _criar_modelo():
                        sys.exit(1)
                else:
                    sys.exit(0)
    except urllib.error.URLError:
        print("\nOllama nao esta rodando. Inicie com 'ollama serve'.")
        sys.exit(1)


def _criar_modelo() -> bool:
    modelfile = (
        "FROM qwen2.5:14b\n"
        'PARAMETER temperature 0.2\n'
        "PARAMETER top_p 0.9\n"
        'SYSTEM """'
        "You are an AI specialized in lotto statistical analysis. "
        "Interpret frequency distributions, gap analysis, and historical patterns. "
        "Never invent data. Base every statement strictly on the numbers provided. "
        "Respond in Brazilian Portuguese.\n"
        '"""\n'
    )
    payload = json.dumps({"model": OLLAMA_MODEL, "modelfile": modelfile}).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/create",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            for line in resp:
                chunk = json.loads(line)
                s = chunk.get("status", "")
                print(f"    {s}")
                if chunk.get("done"):
                    print("  Modelo criado.\n")
                    return True
            return False
    except urllib.error.HTTPError as e:
        print(f"  Erro HTTP {e.code}: {e.read().decode()[:200]}")
        return False
    except urllib.error.URLError:
        print("  Ollama nao esta rodando.")
        return False


# ── OUTPUT ─────────────────────────────────────────────────────────────────────

def _formatar_md(resultados_analise: list[dict], selecao: list[str]) -> str:
    agora = datetime.now()
    cabecalho = f"""# Analise LottoScopio - IA Local

Gerado em: {agora.strftime('%d/%m/%Y %H:%M')}
Modelo: {OLLAMA_MODEL}
Loterias: {', '.join(LOTERIAS[l]['nome'] for l in selecao)}

"""
    partes = []
    for r in resultados_analise:
        sep = "=" * 60
        bloco = f"\n{sep}\n  {r['nome']}\n{sep}\n"
        bloco += f"  Sorteios: {r['sorteios']}\n"
        if r.get("memorias_carregadas"):
            bloco += f"  Memorias RAG: {r['memorias_carregadas']}\n"
        bloco += f"\n{r['analise']}\n"
        partes.append(bloco)

    return cabecalho + "\n---\n".join(partes)


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analise de loterias com IA local")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    parser.add_argument("--compare", type=int, default=0,
                        help="Modo comparativo: N concursos atras vs atual")
    parser.add_argument("--no-save", action="store_true",
                        help="Nao salva memoria no grafo")
    parser.add_argument("--no-context", action="store_true",
                        help="Nao carrega contexto de memorias anteriores")
    parser.add_argument("loteria", nargs="?", default=None,
                        help="ID da loteria (ou vazio para menu interativo)")
    args = parser.parse_args()

    if not args.json:
        print("+-----------------------------------------------+")
        print("|  ia_lotoscope.py - Analise com IA Local       |")
        print("|  Modelo: gemma-lotto (Ollama)                 |")
        print("+-----------------------------------------------+")

    try:
        conn = conectar()
    except Exception as e:
        err = f"Erro ao conectar no SQL Server: {e}"
        if args.json:
            print(json.dumps({"ok": False, "error": err}))
        else:
            print(err)
        sys.exit(1)

    verificar_modelo_ollama()

    cursor = conn.cursor()
    disponiveis = []
    for lid, cfg in LOTERIAS.items():
        try:
            cursor.execute(f"SELECT TOP 0 * FROM {cfg['tabela']}")
            colunas_reais = [c[0] for c in cursor.description]
            if any(c in colunas_reais for c in cfg["cols_num"]):
                disponiveis.append(lid)
        except Exception:
            pass

    if not disponiveis:
        conn.close()
        err = "Nenhuma tabela de loteria encontrada."
        if args.json:
            print(json.dumps({"ok": False, "error": err}))
        else:
            print(err)
        sys.exit(1)

    # Selecao
    selecao = []
    if args.loteria:
        if args.loteria in disponiveis:
            selecao = [args.loteria]
        elif args.loteria == "todas":
            selecao = disponiveis
        else:
            conn.close()
            err = f"Loteria '{args.loteria}' nao encontrada. Disponiveis: {', '.join(disponiveis)}"
            if args.json:
                print(json.dumps({"ok": False, "error": err}))
            else:
                print(err)
            sys.exit(1)
    else:
        if not args.json:
            print(f"\nLoterias disponiveis: {', '.join(LOTERIAS[d]['nome'] for d in disponiveis)}")
            print("1 - Todas")
            for i, lid in enumerate(disponiveis, 2):
                print(f"{i} - {LOTERIAS[lid]['nome']}")
            try:
                escolha = input("\nEscolha: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                conn.close()
                sys.exit(0)

            if escolha == "1":
                selecao = disponiveis
            else:
                try:
                    idx = int(escolha) - 2
                    if 0 <= idx < len(disponiveis):
                        selecao = [disponiveis[idx]]
                    else:
                        print("Opcao invalida.")
                        conn.close()
                        sys.exit(1)
                except ValueError:
                    print("Opcao invalida.")
                    conn.close()
                    sys.exit(1)

    conn.close()

    # Executa analises
    conn_ana = conectar()
    resultados_analise = []
    try:
        for lid in selecao:
            r = analisar_loteria(conn_ana, lid, args)
            resultados_analise.append(r)
    except (OllamaOcupadoError, OllamaError) as e:
        conn_ana.close()
        err = str(e)
        if args.json:
            print(json.dumps({"ok": False, "error": err, "resultados": resultados_analise}))
        else:
            print(f"\n  ERRO: {err}")
        sys.exit(1)
    conn_ana.close()

    # Saida
    if args.json:
        print(json.dumps({
            "ok": True,
            "resultados": resultados_analise,
            "loterias": [r["loteria"] for r in resultados_analise],
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False))
    else:
        conteudo = _formatar_md(resultados_analise, selecao)
        agora = datetime.now().strftime("%Y-%m-%d_%H-%M")
        arquivo = Path(f"analise_{agora}.md")
        arquivo.write_text(conteudo, encoding="utf-8")
        print(f"\nAnalise salva em: {arquivo}")


if __name__ == "__main__":
    main()
