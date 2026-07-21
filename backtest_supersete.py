#!/usr/bin/env python3
"""
backtest_supersete.py — Backtesting temporal com IA (gemma-lotto) para Super Sete.

Pipeline:
  1. Carrega todos os concursos ordenados
  2. Para cada concurso X (>= INICIO_TESTE):
     a. Computa frequencia + gap por coluna (N1..N7) de 1 ateh X-1 (sem vazamento)
     b. Envia para gemma-lotto ranking JSON dos digitos 0-9 por coluna
     c. Valida: em qual tentativa (indice) o digito real estava na lista rankeada?
  3. Ao final: prediz o proximo concurso e salva em validacao_futura_supersete.json
"""

import sys
import json
import re
import time
from datetime import datetime
from collections import Counter
from typing import Any

try:
    import pyodbc
except ImportError:
    print("pyodbc nao instalado. Rode: pip install pyodbc")
    sys.exit(1)

try:
    import urllib.request
except ImportError:
    print("urllib nao disponivel")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs):
        return x


# ── CONFIGURACOES ──────────────────────────────────────────────────────────────

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma-lotto"

COLUNAS = ["N1", "N2", "N3", "N4", "N5", "N6", "N7"]
DIGITOS = list(range(10))
INICIO_TESTE = 300
JANELA_ESTAT = 200
WINDOW_ACERTO = 50


# ── BANCO ──────────────────────────────────────────────────────────────────────

def conectar() -> pyodbc.Connection:
    return pyodbc.connect(CONN_STR)


def carregar_sorteios() -> list[dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()
    cols = ", ".join(COLUNAS)
    cur.execute(f"""
        SELECT Concurso, Data_Sorteio, {cols}
        FROM Resultados_SuperSete
        ORDER BY Concurso ASC
    """)
    sorteios = []
    for r in cur:
        sorteios.append({
            "concurso": r.Concurso,
            "data": str(r.Data_Sorteio),
            "digitos": {c: getattr(r, c) for c in COLUNAS},
        })
    conn.close()
    return sorteios


# ── ESTATISTICAS (sem vazamento) ──────────────────────────────────────────────

def computar_estatisticas(sorteios: list[dict]) -> dict[str, dict]:
    """Calcula frequencia (ultimos JANELA_ESTAT) e gap (total) por coluna."""
    stats: dict[str, dict] = {}
    total = len(sorteios)
    corte = max(0, total - JANELA_ESTAT)
    recentes = sorteios[corte:]

    for col in COLUNAS:
        freq = Counter()
        ultima_aparicao: dict[int, int] = {}
        for i, s in enumerate(recentes):
            d = s["digitos"][col]
            freq[d] += 1
            ultima_aparicao[d] = i
        gap = {}
        for d in DIGITOS:
            if d in ultima_aparicao:
                gap[d] = (total - 1) - (corte + ultima_aparicao[d])
            else:
                gap[d] = total

        ranking_freq = sorted(DIGITOS, key=lambda x: -freq.get(x, 0))
        ranking_gap = sorted(DIGITOS, key=lambda x: -gap.get(x, 0))

        stats[col] = {
            "freq": {str(d): freq.get(d, 0) for d in DIGITOS},
            "gap": {str(d): gap.get(d, 0) for d in DIGITOS},
            "ranking_freq": ranking_freq,
            "ranking_gap": ranking_gap,
        }
    return stats


# ── PROMPT ─────────────────────────────────────────────────────────────────────

def montar_prompt(
    stats: dict[str, dict],
    concurso_alvo: int,
) -> str:
    linhas_col = ""
    for col in COLUNAS:
        s = stats[col]
        freqs = " ".join(f"{d}:{s['freq'][str(d)]}" for d in DIGITOS)
        gaps = " ".join(f"{d}:{s['gap'][str(d)]}" for d in DIGITOS)
        linhas_col += (
            f"  {col}: freq=[{freqs}]  gap=[{gaps}]\n"
        )

    return f"""## Super Sete - Estatisticas pre-concurso {concurso_alvo}

Frequencia (ultimos {JANELA_ESTAT} sorteios) e Gap (concursos sem sair) por coluna.
Digitos possiveis: 0 a 9.

{linhas_col}
Com base estritamente nos dados acima, forneca um ranking de probabilidade
para o PROXIMO sorteio. Ordene os digitos de 0 a 9 do mais provavel para o
menos provavel, para CADA coluna separadamente.

Responda EXCLUSIVAMENTE em JSON, sem texto antes ou depois, neste formato:
{{"N1":[9,8,7,6,5,4,3,2,1,0],"N2":[...],"N3":[...],"N4":[...],"N5":[...],"N6":[...],"N7":[...]}}
Cada lista deve conter TODOS os 10 digitos, ordenados do mais provavel (indice 0)
para o menos provavel (indice 9).
"""


# ── CHAMADA OLLAMA ─────────────────────────────────────────────────────────────

def chamar_ia(prompt: str, timeout: int = 120) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.2,
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result.get("response", "")


# ── PARSER DA RESPOSTA ────────────────────────────────────────────────────────

def extrair_json(texto: str) -> dict | None:
    """Extrai JSON da resposta da IA. Tenta parse direto, depois regex."""
    texto = texto.strip()
    # Tenta parse direto
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass
    # Procura { ... } com regex
    match = re.search(r"\{[^{}]*\"N1\"\s*:\s*\[.*?\].*?\}", texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def gerar_fallback() -> dict:
    """Fallback deterministico: ordena por gap decrescente."""
    return {col: list(range(9, -1, -1)) for col in COLUNAS}


# ── VALIDACAO ──────────────────────────────────────────────────────────────────

def validar_predicao(
    pred: dict,
    real: dict,
) -> dict:
    """Compara predicao com resultado real.
    Retorna: tentativa por coluna + metricas de acerto.
    """
    tentativas = {}
    for col in COLUNAS:
        ranking = pred.get(col, [])
        digito_real = real[col]
        if digito_real in ranking:
            pos = ranking.index(digito_real)
            tentativas[col] = pos + 1  # 1-based
        else:
            tentativas[col] = 10  # nao encontrado = ultima tentativa

    # Contagem de acertos por limite de tentativa
    col3 = sum(1 for v in tentativas.values() if v <= 3)
    col5 = sum(1 for v in tentativas.values() if v <= 5)
    col1 = sum(1 for v in tentativas.values() if v == 1)
    media = sum(tentativas.values()) / len(COLUNAS)

    return {
        "tentativas": tentativas,
        "col1": col1,
        "col3": col3,
        "col5": col5,
        "media_tentativas": round(media, 2),
        "acertou_3_mais": col3 >= 3,
    }


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Backtesting Super Sete com IA")
    parser.add_argument("--max-testes", type=int, default=0,
                        help="Limite de concursos a testar (0=todos)")
    parser.add_argument("--step", type=int, default=1,
                        help="Testar a cada N concursos (1=todos)")
    parser.add_argument("--inicio", type=int, default=INICIO_TESTE,
                        help=f"Concurso inicial (default: {INICIO_TESTE})")
    parser.add_argument("--predict-only", action="store_true",
                        help="So gera predicao futura (sem backtesting)")
    args = parser.parse_args()

    print("=" * 70)
    print("  BACKTESTING SUPER SETE - IA gemma-lotto")
    print(f"  Inicio: concurso {args.inicio}")
    print(f"  Step: {args.step} {'(todos)' if args.step == 1 else f'(1 a cada {args.step})'}")
    if args.max_testes:
        print(f"  Limite: {args.max_testes} concursos")
    print(f"  Janela estatistica: ultimos {JANELA_ESTAT} sorteios")
    print("=" * 70)

    # 1. Carregar dados
    tqdm.write("[1/4] Carregando sorteios...")
    todos = carregar_sorteios()
    tqdm.write(f"  {len(todos)} concursos carregados")
    tqdm.write(f"  Periodo: {todos[0]['concurso']} ({todos[0]['data']}) a "
               f"{todos[-1]['concurso']} ({todos[-1]['data']})")

    # 2. Backtesting (opcional)
    resultados_backtest = []
    fallbacks_usados = 0
    historico_acerto_3 = []

    if not args.predict_only:
        tqdm.write("[2/4] Loop de backtesting...")
        testes = [s for s in todos if s["concurso"] >= args.inicio]
        if args.step > 1:
            testes = testes[::args.step]
        if args.max_testes and len(testes) > args.max_testes:
            testes = testes[:args.max_testes]
        if not testes:
            print(f"Nenhum concurso >= {args.inicio}. Abortando.")
            sys.exit(1)

        total_loop = len(testes)
        for i, sorteio_atual in enumerate(tqdm(testes, desc="  Testando", unit="conc")):
            concurso_x = sorteio_atual["concurso"]
            idx = concurso_x - 1
            anteriores = todos[:idx]

            if len(anteriores) < 10:
                continue

            stats = computar_estatisticas(anteriores)
            prompt = montar_prompt(stats, concurso_x)

            pred = None
            for tentativa in range(2):
                try:
                    resposta = chamar_ia(prompt)
                    pred = extrair_json(resposta)
                    if pred is not None:
                        valido = all(
                            col in pred and isinstance(pred[col], list)
                            and len(pred[col]) == 10
                            and all(isinstance(d, int) for d in pred[col])
                            for col in COLUNAS
                        )
                        if valido:
                            break
                        time.sleep(1)
                    else:
                        time.sleep(2)
                except Exception:
                    time.sleep(3)

            if pred is None:
                pred = gerar_fallback()
                fallbacks_usados += 1

            resultado = validar_predicao(pred, sorteio_atual["digitos"])
            resultado["concurso"] = concurso_x
            resultados_backtest.append(resultado)

            historico_acerto_3.append(resultado["acertou_3_mais"])
            if len(historico_acerto_3) > WINDOW_ACERTO:
                historico_acerto_3.pop(0)

            if i > 0 and (i % max(1, total_loop // 20) == 0 or i == total_loop - 1):
                win_rate = sum(historico_acerto_3) / len(historico_acerto_3) * 100 if historico_acerto_3 else 0
                tqdm.write(
                    f"  [C{concurso_x}] "
                    f"acerto>=3col: {resultado['acertou_3_mais']} "
                    f"media_tent: {resultado['media_tentativas']} "
                    f"win_rate: {win_rate:.1f}%"
                )

    # 3. Sumario / Predicao futura
    if args.predict_only:
        total_testes = 0
        acertos_3_col = 0
        media_tent_geral = 0
        media_col3 = 0
        media_col1 = 0
        tqdm.write("[2/4] Pulando backtesting (--predict-only)...")
    else:
        tqdm.write("\n[3/4] Compilando resultados...")
        total_testes = len(resultados_backtest)
        if total_testes == 0:
            tqdm.write("  Nenhum teste realizado.")
            sys.exit(1)

        acertos_3_col = sum(1 for r in resultados_backtest if r["acertou_3_mais"])
        media_tent_geral = sum(r["media_tentativas"] for r in resultados_backtest) / total_testes
        media_col3 = sum(r["col3"] for r in resultados_backtest) / total_testes
        media_col1 = sum(r["col1"] for r in resultados_backtest) / total_testes

        tqdm.write("\n" + "=" * 70)
        tqdm.write(f"  TOTAL DE CONCURSOS TESTADOS: {total_testes}")
        tqdm.write(f"  Periodo: concurso {args.inicio} ate {testes[-1]['concurso']}")
        tqdm.write(f"  Fallbacks usados: {fallbacks_usados}")
        tqdm.write(f"  Acertou >= 3 colunas: {acertos_3_col}/{total_testes} "
                   f"({acertos_3_col/total_testes*100:.1f}%)")
        tqdm.write(f"  Media tentativas/coluna: {media_tent_geral:.2f}")
        tqdm.write(f"  Media colunas na 1a tentativa: {media_col1:.1f}")
        tqdm.write(f"  Media colunas no Top 3: {media_col3:.1f}")
        tqdm.write(f"  Media colunas no Top 5: {sum(r['col5'] for r in resultados_backtest) / total_testes:.1f}")
        tqdm.write("=" * 70)

    # 4. Predicao futura
    tqdm.write(f"\n[{3 if not args.predict_only else 2}/4] Gerando predicao futura...")
    stats_finais = computar_estatisticas(todos)
    prompt_futuro = montar_prompt(stats_finais, todos[-1]["concurso"] + 1)
    prompt_futuro += (
        "\nResponda EXCLUSIVAMENTE em JSON, sem texto antes ou depois."
    )

    pred_futura = None
    for tentativa in range(3):
        try:
            resposta = chamar_ia(prompt_futuro)
            pred_futura = extrair_json(resposta)
            if pred_futura and all(
                col in pred_futura and len(pred_futura[col]) == 10
                for col in COLUNAS
            ):
                break
            time.sleep(2)
        except Exception:
            time.sleep(2)

    if pred_futura is None:
        pred_futura = gerar_fallback()

    ultimo_conc = todos[-1]
    payload_saida = {
        "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "modelo": OLLAMA_MODEL,
        "ultimo_concurso_analisado": ultimo_conc["concurso"],
        "ultimo_concurso_data": ultimo_conc["data"],
        "ultimo_resultado": ultimo_conc["digitos"],
        "previsao_proximo_concurso": {
            "ranking": pred_futura,
            "melhores_1_tentativa": {col: pred_futura[col][0] for col in COLUNAS},
            "melhores_3_tentativas": {col: pred_futura[col][:3] for col in COLUNAS},
        },
        "estatisticas_backtest": {
            "total_testes": total_testes,
            "acertos_3_colunas": f"{acertos_3_col}/{total_testes} ({acertos_3_col/total_testes*100:.1f}%)" if total_testes else "0/0 (0.0%)",
            "media_tentativas_por_coluna": round(media_tent_geral, 2),
            "win_rate_janela": f"{sum(historico_acerto_3)}/{len(historico_acerto_3)} ({sum(historico_acerto_3)/max(1,len(historico_acerto_3))*100:.1f}%)",
        },
    }

    caminho_pred = "validacao_futura_supersete.json"
    with open(caminho_pred, "w", encoding="utf-8") as f:
        json.dump(payload_saida, f, ensure_ascii=False, indent=2)
    tqdm.write(f"  Predicao salva em {caminho_pred}")

    # Salva resultados detalhados do backtesting para consumo pela IA
    caminho_bt = "backtest_supersete_resultados.json"
    ultimo_conc_testado = testes[-1]["concurso"] if not args.predict_only and 'testes' in dir() and testes else 0
    detalhes_backtest = {
        "data_geracao": payload_saida["data_geracao"],
        "modelo": OLLAMA_MODEL,
        "total_testes": total_testes,
        "periodo_inicio": args.inicio,
        "periodo_fim": ultimo_conc_testado,
        "estatisticas": payload_saida["estatisticas_backtest"],
        "previsao_futura": payload_saida["previsao_proximo_concurso"],
        "ultimo_sorteio_real": {
            "concurso": ultimo_conc["concurso"],
            "data": ultimo_conc["data"],
            "digitos": ultimo_conc["digitos"],
        },
        "resultados_por_concurso": [
            {
                "concurso": r["concurso"],
                "tentativas_por_coluna": r["tentativas"],
                "media_tentativas": r["media_tentativas"],
                "col1": r["col1"],
                "col3": r["col3"],
                "col5": r["col5"],
                "acertou_3_mais": r["acertou_3_mais"],
            }
            for r in resultados_backtest
        ],
    }
    with open(caminho_bt, "w", encoding="utf-8") as f:
        json.dump(detalhes_backtest, f, ensure_ascii=False, indent=2)
    tqdm.write(f"  Resultados detalhados salvos em {caminho_bt}")
    tqdm.write(f"  Proximo concurso: {ultimo_conc['concurso'] + 1}")
    tqdm.write(f"  Melhor aposta (1a tentativa): "
               f"{' '.join(str(pred_futura[c][0]) for c in COLUNAS)}")
    tqdm.write("  Concluido!")


if __name__ == "__main__":
    main()
