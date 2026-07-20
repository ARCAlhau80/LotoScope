#!/usr/bin/env python3
"""
ia_lotoscope.py — Agente de análise estatística com IA local (Ollama)
Conecta no SQL Server, carrega resultados de qualquer loteria, computa
estatísticas e envia ao modelo local para análise em linguagem natural.
Saída exportada para .md com timestamp.
"""

import sys
import json
import math
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
    """Transição de dígitos por posição (N1..N7) no Super Sete.
    Cada resultado tem exatamente 7 dígitos (posições 0..6).
    """
    total = len(resultados)
    if total < 2:
        return {}

    num_pos = 7
    # Para cada posição: matriz 10x10 de transições
    transicoes = [Counter() for _ in range(num_pos)]
    freq_pos = [Counter() for _ in range(num_pos)]

    for i in range(1, total):
        r_atual = resultados[i]
        r_anterior = resultados[i - 1]
        for p in range(num_pos):
            d_ant = r_anterior[p]
            d_atual = r_atual[p]
            transicoes[p][(d_ant, d_atual)] += 1

    for r in resultados:
        for p in range(num_pos):
            freq_pos[p][r[p]] += 1

    # Último resultado e penúltimo
    ultimo = resultados[-1]
    penultimo = resultados[-2]

    saida = {"posicoes": []}
    for p in range(num_pos):
        total_trans = sum(transicoes[p].values())
        mais_comum = transicoes[p].most_common(5)

        trans_dict = {}
        for (d_ant, d_atual), count in transicoes[p].items():
            key = f"{d_ant}->{d_atual}"
            trans_dict[key] = {
                "count": count,
                "pct": round(count / total_trans * 100, 1) if total_trans else 0,
            }

        digitos_ordenados = sorted(freq_pos[p].items(), key=lambda x: -x[1])
        ult_digito = ultimo[p]
        ant_digito = penultimo[p]

        saida["posicoes"].append({
            "posicao": p + 1,
            "ultimo_digito": ult_digito,
            "anterior_digito": ant_digito,
            "mudou": ult_digito != ant_digito,
            "frequencia_posicional": {str(d): c for d, c in digitos_ordenados},
            "top_transicoes": [
                {
                    "de": t[0][0],
                    "para": t[0][1],
                    "count": t[1],
                    "pct": round(t[1] / total_trans * 100, 1) if total_trans else 0,
                }
                for t in mais_comum
            ],
        })

    return saida


# ── PROMPTS ────────────────────────────────────────────────────────────────────

def montar_prompt(est: dict, cfg: dict) -> str:
    return f"""## Dados Estatisticos - {cfg['nome']}

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
{chr(10).join(f'{n}: global={est["frequencia_global"][str(n)]} | recente={est["frequencia_30"][str(n)]}' for n in sorted(est['frequencia_global'], key=lambda x: -(abs(est["frequencia_global"][x] / max(1, est["total_sorteios"]) - est["frequencia_30"][x] / max(1, min(30, est["total_sorteios"])))))[:5])}

---
Com base estritamente nos dados acima, realize uma analise em portugues do Brasil cobrindo:
1. Distribuicao do ultimo sorteio vs media historica (soma, paridade, primos)
2. Anomalias de frequencia (numeros muito acima ou abaixo do esperado)
3. Tendencias de atraso - gaps acima do P90
4. Sugestao de enfoque para os proximos sorteios com base nos dados
Use formato estruturado com topicos. Seja analitico, nao especulativo.
"""


def montar_prompt_supersete(est: dict, pos: dict) -> str:
    prompt = f"""## Dados Estatisticos - Super Sete

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
{chr(10).join(f'{n}: global={est["frequencia_global"][str(n)]} | recente={est["frequencia_30"][str(n)]}' for n in sorted(est['frequencia_global'], key=lambda x: -(abs(est["frequencia_global"][x] / max(1, est["total_sorteios"]) - est["frequencia_30"][x] / max(1, min(30, est["total_sorteios"])))))[:5])}

### Analise Posicional (transicao de digitos por coluna)
"""
    for pos_info in pos["posicoes"]:
        ant = pos_info["anterior_digito"]
        ult = pos_info["ultimo_digito"]
        seta = "->" if pos_info["mudou"] else "=="
        prompt += f"\nColuna {pos_info['posicao']}: {ant} {seta} {ult}"
        prompt += f"\n  Top transicoes historicas: "
        prompt += ", ".join(
            f"{t['de']}->{t['para']} ({t['pct']}%)"
            for t in pos_info["top_transicoes"][:3]
        )
        prompt += f"\n  Frequencia por digito: "
        sorted_freq = sorted(
            pos_info["frequencia_posicional"].items(),
            key=lambda x: -x[1],
        )
        prompt += ", ".join(f"{d}({c}x)" for d, c in sorted_freq[:5])

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
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
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


# ── ANALISE ────────────────────────────────────────────────────────────────────

def analisar_loteria(conn: pyodbc.Connection, loteria_id: str) -> str:
    """Executa analise de uma loteria e retorna o texto formatado."""
    cfg = LOTERIAS[loteria_id]
    linhas = []
    sep = "=" * 60
    linhas.append(f"\n{sep}\n  {cfg['nome']}\n{sep}")

    resultados = carregar_resultados(conn, loteria_id)
    if not resultados:
        linhas.append("  0 sorteios - SEM DADOS\n")
        return "\n".join(linhas)

    linhas.append(f"  Sorteios: {len(resultados)}\n")

    est = estatisticas_globais(resultados, loteria_id)
    print(f"  Enviando {cfg['nome']} para IA...", flush=True)

    if loteria_id == "supersete" and cfg.get("is_positional"):
        pos = analise_posicional_supersete(resultados)
        prompt = montar_prompt_supersete(est, pos)
    else:
        prompt = montar_prompt(est, cfg)

    resposta = chamar_ollama(prompt)
    linhas.append(resposta + "\n")

    return "\n".join(linhas)


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
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "modelfile": modelfile,
    }).encode()

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


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print("+-----------------------------------------------+")
    print("|  ia_lotoscope.py - Analise com IA Local       |")
    print("|  Modelo: gemma-lotto (Ollama)                 |")
    print("+-----------------------------------------------+")

    try:
        conn = conectar()
    except Exception as e:
        print(f"Erro ao conectar no SQL Server: {e}")
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
        print("Nenhuma tabela de loteria encontrada.")
        conn.close()
        sys.exit(1)

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

    # Coleta todas as analises
    conn_ana = conectar()
    partes = []
    for lid in selecao:
        try:
            texto = analisar_loteria(conn_ana, lid)
            partes.append(texto)
        except OllamaOcupadoError as e:
            print(f"\n  ERRO: {e}")
            print("  Ollama ocupado. Execute novamente mais tarde.")
            conn_ana.close()
            sys.exit(1)
        except OllamaError as e:
            print(f"\n  ERRO: {e}")
            conn_ana.close()
            sys.exit(1)
    conn_ana.close()

    # Gera o .md
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M")
    arquivo = Path(f"analise_{agora}.md")
    cabecalho = f"""# Analise LottoScopio - IA Local

Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Modelo: {OLLAMA_MODEL}
Loterias: {', '.join(LOTERIAS[l]['nome'] for l in selecao)}

"""
    conteudo = cabecalho + "\n---\n".join(partes)
    arquivo.write_text(conteudo, encoding="utf-8")
    print(f"\nAnalise salva em: {arquivo}")


if __name__ == "__main__":
    main()
