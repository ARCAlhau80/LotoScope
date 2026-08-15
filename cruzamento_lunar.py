#!/usr/bin/env python3
"""
cruzamento_lunar.py — Cruza sorteios com posicao lunar e envia dossie para IA local.

Pipeline:
  1. Conecta SQL Server → extrai ultimos 50 sorteios (Concurso, Data_Sorteio, N1..N15)
  2. Calcula ephem para cada Data_Sorteio (altitude, fase da Lua) em SBC (-23.6938, -46.5656)
  3. Estatisticas: quentes/frias globais VS qdo lua visivel vs abaixo horizonte
  4. Monta dossie em texto + envia para gemma-lotto (Ollama) analisar

Flags:
  --json    Saida em JSON (para consumo via API)
"""

import sys
import os
import json
import math
from datetime import datetime, timezone, timedelta
from collections import Counter
from typing import Any

try:
    import pyodbc
except ImportError:
    print("pyodbc nao instalado. Rode: pip install pyodbc")
    sys.exit(1)

try:
    import ephem
except ImportError:
    print("ephem nao instalado. Rode: pip install ephem")
    sys.exit(1)

try:
    import urllib.request
except ImportError:
    print("urllib nao disponivel")
    sys.exit(1)

# ── CONFIG ──────────────────────────────────────────────────────────────────────

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma-lotto"

SBC = {
    "lat": "-23.5658",
    "lon": "-46.6507",
    "elev": 810,
}

NUM_SORTEIOS = 2000
NUM_POSICOES = 15
MAX_DEZENA = 25
TZ_BR = timedelta(hours=-3)  # UTC-3


# ── FASE LUNAR ──────────────────────────────────────────────────────────────────

def classificar_fase(moon_phase: float) -> str:
    if moon_phase < 0.05:
        return "Nova"
    if moon_phase < 0.45:
        return "Crescente"
    if moon_phase < 0.55:
        return "Cheia"
    if moon_phase < 0.95:
        return "Minguante"
    return "Nova"


def calcular_lua(dt_br: datetime) -> dict[str, Any]:
    """Calcula posicao da Lua em SBC para um datetime UTC-3.
    Retorna altitude (rad), visivel bool, fase, nome_fase.
    """
    dt_utc = dt_br.replace(tzinfo=timezone.utc) - TZ_BR
    obs = ephem.Observer()
    obs.lat = SBC["lat"]
    obs.lon = SBC["lon"]
    obs.elevation = SBC["elev"]
    obs.date = dt_utc.strftime("%Y/%m/%d %H:%M:%S")

    moon = ephem.Moon()
    moon.compute(obs)
    alt_rad = float(moon.alt)
    alt_deg = alt_rad * 180.0 / math.pi
    mp = moon.moon_phase

    return {
        "altitude_rad": round(alt_rad, 6),
        "altitude_deg": round(alt_deg, 2),
        "visivel": alt_rad > 0,
        "fase": mp,
        "nome_fase": classificar_fase(mp),
    }


# ── SQL ────────────────────────────────────────────────────────────────────────

def conectar() -> pyodbc.Connection:
    conn = pyodbc.connect(CONN_STR)
    return conn


def extrair_sorteios(conn: pyodbc.Connection) -> list[dict[str, Any]]:
    """Retorna os ultimos NUM_SORTEIOS sorteios."""
    cols = ", ".join(f"N{i}" for i in range(1, NUM_POSICOES + 1))
    sql = f"""
        SELECT TOP({NUM_SORTEIOS}) Concurso, Data_Sorteio, {cols}
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    resultados = []
    for r in rows:
        try:
            dt = r.Data_Sorteio
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            elif hasattr(dt, "to_pydatetime"):
                dt = dt.to_pydatetime()
            if dt.hour == 0 and dt.minute == 0:
                dt = dt.replace(hour=20, minute=0)
            nums = [getattr(r, f"N{i}") for i in range(1, NUM_POSICOES + 1)]
            resultados.append({
                "concurso": r.Concurso,
                "data": dt,
                "numeros": nums,
            })
        except Exception as e:
            print(f"[aviso] pula concurso {r.Concurso}: {e}", file=sys.stderr)
            continue

    resultados.reverse()  # ordem cronologica
    return resultados


# ── ESTATISTICAS ────────────────────────────────────────────────────────────────

def _teste_chi2(o_vis: int, o_inv: int, total_vis: int, total_inv: int) -> dict:
    """Teste qui-quadrado simples (1 GL) para uma dezena entre dois grupos.
    Retorna chi2, p_valor e interpretacao.
    """
    total = o_vis + o_inv
    if total == 0 or total_vis == 0 or total_inv == 0:
        return {"chi2": 0.0, "p_valor": 1.0, "significante": False}
    e_vis = total * total_vis / (total_vis + total_inv)
    e_inv = total * total_inv / (total_vis + total_inv)
    chi2 = 0.0
    if e_vis > 0:
        chi2 += (o_vis - e_vis) ** 2 / e_vis
    if e_inv > 0:
        chi2 += (o_inv - e_inv) ** 2 / e_inv
    # p-value aproximado para 1 GL (distribuicao normal aproximada)
    # Usamos formula: p = 2 * (1 - Phi(sqrt(chi2)))
    import math
    z = math.sqrt(max(0.0, chi2))
    # aproximacao de Abramowitz & Stegun para normal CDF
    p = math.erfc(z / math.sqrt(2))
    return {
        "chi2": round(chi2, 4),
        "p_valor": round(p, 6),
        "significante": p < 0.05,
    }


def computar_estatisticas(
    sorteios: list[dict[str, Any]],
    dados_lua: list[dict[str, Any]],
) -> dict[str, Any]:
    """Agrupa dezenas sorteadas em tres cenarios: geral, visivel, invisivel.
    Inclui teste chi-square por dezena e distribuicao por fase lunar.
    """
    total = Counter()
    visivel = Counter()
    invisivel = Counter()
    por_fase: dict[str, Counter] = {}

    for s, lua in zip(sorteios, dados_lua):
        for n in s["numeros"]:
            total[n] += 1
            if lua["visivel"]:
                visivel[n] += 1
            else:
                invisivel[n] += 1
            fase = lua["nome_fase"]
            if fase not in por_fase:
                por_fase[fase] = Counter()
            por_fase[fase][n] += 1

    total_vis = sum(1 for l in dados_lua if l["visivel"])
    total_inv = len(dados_lua) - total_vis

    def topn(c: Counter, n: int = 5) -> list[tuple[int, int]]:
        return sorted(c.items(), key=lambda x: -x[1])[:n]

    def bottom5(c: Counter) -> list[tuple[int, int]]:
        return sorted(c.items(), key=lambda x: x[1])[:5]

    # Qui-quadrado por dezena
    chi2_por_dezena = {}
    for n in range(1, MAX_DEZENA + 1):
        o_vis = visivel.get(n, 0)
        o_inv = invisivel.get(n, 0)
        res = _teste_chi2(o_vis, o_inv, total_vis, total_inv)
        if res["significante"]:
            chi2_por_dezena[str(n)] = res

    # Top5 por fase lunar
    top5_por_fase = {}
    for fase, c in por_fase.items():
        top5_por_fase[fase] = topn(c, 5)

    total_top10 = topn(total, 10)
    visivel_top10 = topn(visivel, 10)
    invisivel_top10 = topn(invisivel, 10)

    return {
        "total_qtd": len(sorteios),
        "total_top10": total_top10,
        "total_bottom5": bottom5(total),
        "visivel_qtd": total_vis,
        "visivel_top10": visivel_top10,
        "invisivel_qtd": total_inv,
        "invisivel_top10": invisivel_top10,
        "top5_por_fase": top5_por_fase,
        "chi2_significantes": chi2_por_dezena,
        "cross": {
            "aparece_em_ambos": sorted(set(n for n, _ in total_top10) & set(n for n, _ in visivel_top10) & set(n for n, _ in invisivel_top10)),
            "so_visivel": sorted(set(n for n, _ in visivel_top10) - set(n for n, _ in invisivel_top10)),
            "so_invisivel": sorted(set(n for n, _ in invisivel_top10) - set(n for n, _ in visivel_top10)),
        },
    }


# ── DOSSIER ─────────────────────────────────────────────────────────────────────

def montar_dossie(
    ultimo: dict[str, Any],
    lua_ultimo: dict[str, Any],
    est: dict[str, Any],
    todos_lua: list[dict[str, Any]],
    todos_sorteios: list[dict[str, Any]],
) -> str:
    def fmt_top(lst: list) -> str:
        return ", ".join(f"{n} ({c}x)" for n, c in lst)

    def fmt_top(lst: list) -> str:
        return ", ".join(f"{n} ({c}x)" for n, c in lst)

    freq_visivel = sum(1 for l in todos_lua if l["visivel"])
    freq_invisivel = len(todos_lua) - freq_visivel

    datas_lua = ", ".join(
        f"{s['concurso']}=>{l['nome_fase']}({'visivel' if l['visivel'] else 'oculta'})"
        for s, l in zip(todos_sorteios[-10:], todos_lua[-10:])
    )

    # Chi-square summary
    chi2_lines = ""
    if est.get("chi2_significantes"):
        for n, r in sorted(est["chi2_significantes"].items(), key=lambda x: x[1]["p_valor"]):
            chi2_lines += f"  {n}: chi2={r['chi2']} p={r['p_valor']}\n"
    else:
        chi2_lines = "  Nenhuma dezena com diferenca estatisticamente significante (p<0.05).\n"

    # Phase distribution
    fases_lines = ""
    for fase in ["Nova", "Crescente", "Cheia", "Minguante"]:
        qtd = sum(1 for l in todos_lua if l["nome_fase"] == fase)
        if qtd:
            fases_lines += f"  {fase}: {qtd} sorteios ({qtd/len(todos_lua)*100:.1f}%)\n"

    # Top5 per phase
    top5_fase_lines = ""
    for fase in ["Nova", "Crescente", "Cheia", "Minguante"]:
        if fase in est.get("top5_por_fase", {}):
            top5_fase_lines += f"  {fase}: {fmt_top(est['top5_por_fase'][fase])}\n"

    return f"""=== DOSSIE LUNAR - LOTOFACIL ===
Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Coordenadas: {SBC['lat']}, {SBC['lon']}, {SBC['elev']}m
Amostra: {est['total_qtd']} sorteios

-- DADOS DO SORTEIO ATUAL --
Concurso: {ultimo['concurso']}
Data: {ultimo['data'].strftime("%Y-%m-%d %H:%M")}
Dezenas: {ultimo['numeros']}
Lua: {lua_ultimo['nome_fase']} | Altitude: {lua_ultimo['altitude_deg']}°
Visivel no ceu: {"Sim" if lua_ultimo['visivel'] else "Nao"}

-- DISTRIBUICAO POR FASE LUNAR --
{fases_lines}
-- DISTRIBUICAO POR VISIBILIDADE --
Visivel: {freq_visivel} ({freq_visivel/len(todos_lua)*100:.1f}%)
Oculta:  {freq_invisivel} ({freq_invisivel/len(todos_lua)*100:.1f}%)

Fases nos ultimos 10 sorteios: {datas_lua}

-- TOP 10 DEZENAS MAIS FREQUENTES (GERAL) --
{fmt_top(est['total_top10'])}

-- TOP 10 DEZENAS MAIS FREQUENTES (LUA VISIVEL) --
{fmt_top(est['visivel_top10'])}

-- TOP 10 DEZENAS MAIS FREQUENTES (LUA OCULTA) --
{fmt_top(est['invisivel_top10'])}

-- TOP 5 DEZENAS POR FASE LUNAR --
{top5_fase_lines}
-- CRUZAMENTO VISIBILIDADE (TOP 10) --
Presentes em ambos:  {est['cross']['aparece_em_ambos']}
Exclusivas visivel:  {est['cross']['so_visivel']}
Exclusivas oculta:   {est['cross']['so_invisivel']}

-- TESTE QUI-QUADRADO (p<0.05 = diferenca estatistica entre visivel/oculta) --
{chi2_lines}
-- NOTA --
Teste qui-quadrado com 1 GL. p<0.05 indica que a frequencia da dezena
depende da visibilidade lunar com 95% de confianca.
(Fonte: ephem, altitude > 0° = visivel)
"""


# ── LLM ─────────────────────────────────────────────────────────────────────────

def enviar_para_ia(dossie: str) -> str:
    prompt = (
        "Analise este dossier cruzando a incidencia de dezenas "
        "com a visibilidade lunar. Ha algum padrao comportamental "
        "ou anomalia estatistica notavel quando a lua esta visivel "
        "no ceu versus quando nao esta?\n\n" + dossie
    )
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "[sem resposta]")
    except Exception as e:
        return f"[erro ao chamar Ollama] {e}"


# ── MAIN ────────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Cruza sorteios com posicao lunar")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    args = parser.parse_args()

    print("=== CRUZAMENTO LUNAR - LOTOFACIL ===", file=sys.stderr)

    # 1. Dados
    print("[1/4] Conectando SQL Server...", file=sys.stderr)
    try:
        conn = conectar()
    except Exception as e:
        print(f"ERRO conexao: {e}", file=sys.stderr)
        sys.exit(1)

    print("[2/4] Extraindo sorteios...", file=sys.stderr)
    sorteios = extrair_sorteios(conn)
    conn.close()

    if not sorteios:
        print("Nenhum sorteio encontrado.", file=sys.stderr)
        sys.exit(1)

    print(f"  -> {len(sorteios)} sorteios carregados", file=sys.stderr)

    # 2. Ephem
    print("[3/4] Calculando posicao lunar (ephem)...", file=sys.stderr)
    dados_lua = []
    for s in sorteios:
        try:
            lua = calcular_lua(s["data"])
        except Exception as e:
            print(f"  [aviso] erro ephem concurso {s['concurso']}: {e}", file=sys.stderr)
            lua = {"altitude_rad": 0, "altitude_deg": 0.0, "visivel": False, "fase": 0.0, "nome_fase": "?"}
        dados_lua.append(lua)

    visivel_count = sum(1 for l in dados_lua if l["visivel"])
    print(f"  -> Lua visivel: {visivel_count} | oculta: {len(dados_lua) - visivel_count}", file=sys.stderr)

    # 3. Estatisticas
    est = computar_estatisticas(sorteios, dados_lua)
    ultimo = sorteios[-1]
    lua_ultimo = dados_lua[-1]

    # 4. Dossier
    dossie = montar_dossie(ultimo, lua_ultimo, est, dados_lua, sorteios)

    # 5. Enviar IA
    print("[4/4] Enviando para IA local gemma-lotto...", file=sys.stderr)
    resposta = enviar_para_ia(dossie)

    if args.json:
        saida = {
            "ok": True,
            "dossie": dossie,
            "analise_ia": resposta,
            "estatisticas": {
                "total_sorteios": est["total_qtd"],
                "visivel_count": visivel_count,
                "oculta_count": len(dados_lua) - visivel_count,
                "top10_geral": [{"dezena": n, "freq": c} for n, c in est["total_top10"]],
                "top10_visivel": [{"dezena": n, "freq": c} for n, c in est["visivel_top10"]],
                "top10_oculta": [{"dezena": n, "freq": c} for n, c in est["invisivel_top10"]],
                "bottom5_geral": [{"dezena": n, "freq": c} for n, c in est["total_bottom5"]],
                "chi2_significantes": est["chi2_significantes"],
                "top5_por_fase": {k: [{"dezena": n, "freq": c} for n, c in v] for k, v in est["top5_por_fase"].items()},
                "cruzamento": est["cross"],
            },
            "ultimo_sorteio": {
                "concurso": ultimo["concurso"],
                "data": ultimo["data"].strftime("%Y-%m-%d %H:%M"),
                "dezenas": ultimo["numeros"],
                "lua": lua_ultimo,
            },
        }
        print(json.dumps(saida, ensure_ascii=False))
    else:
        print("\n" + "=" * 60, file=sys.stderr)
        print(dossie)
        print("=" * 60, file=sys.stderr)
        print("\n=== RESPOSTA DA IA ===", file=sys.stderr)
        print(resposta)


if __name__ == "__main__":
    main()
