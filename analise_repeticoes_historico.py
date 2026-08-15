import pyodbc
import json
from collections import Counter
from statistics import mean, median, stdev

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

# Categorias
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}


def pares(nums):
    return {n for n in nums if n % 2 == 0}


def impares(nums):
    return {n for n in nums if n % 2 == 1}


def consecutivos(nums):
    """Retorna pares consecutivos (a, a+1) presentes no conjunto."""
    s = set(nums)
    return {(a, a + 1) for a in s if (a + 1) in s}


def main():
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso")
    rows = cur.fetchall()

    # Lista de tuplas (concurso, set de 15 numeros)
    sorteios = [(r[0], set(r[1:16])) for r in rows]
    print(f"Total de sorteios analisados: {len(sorteios)}")
    if len(sorteios) < 2:
        return

    # Analise: concurso anterior vs proximo
    repeticoes_geral = []
    repeticoes_pares = []
    repeticoes_impares = []
    repeticoes_primos = []
    repeticoes_fibonacci = []
    repeticoes_consecutivos_count = []  # quantidade de pares consecutivos que se repetiram
    detalhes_por_concurso = []

    for i in range(1, len(sorteios)):
        concurso_atual, nums_atual = sorteios[i]
        concurso_anterior, nums_anterior = sorteios[i - 1]

        rep_geral = len(nums_atual & nums_anterior)
        rep_pares = len(pares(nums_atual) & pares(nums_anterior))
        rep_impares = len(impares(nums_atual) & impares(nums_anterior))
        rep_primos = len((nums_atual & PRIMOS) & (nums_anterior & PRIMOS))
        rep_fib = len((nums_atual & FIBONACCI) & (nums_anterior & FIBONACCI))

        cons_atual = consecutivos(nums_atual)
        cons_anterior = consecutivos(nums_anterior)
        rep_cons = len(cons_atual & cons_anterior)

        repeticoes_geral.append(rep_geral)
        repeticoes_pares.append(rep_pares)
        repeticoes_impares.append(rep_impares)
        repeticoes_primos.append(rep_primos)
        repeticoes_fibonacci.append(rep_fib)
        repeticoes_consecutivos_count.append(rep_cons)

        detalhes_por_concurso.append({
            "concurso": concurso_atual,
            "anterior": concurso_anterior,
            "repetidos_geral": rep_geral,
            "repetidos_pares": rep_pares,
            "repetidos_impares": rep_impares,
            "repetidos_primos": rep_primos,
            "repetidos_fibonacci": rep_fib,
            "repetidos_consecutivos": rep_cons,
        })

    def dist(counter):
        total = sum(counter.values())
        return {k: {"count": counter[k], "pct": f"{counter[k]/total*100:.2f}%"} for k in sorted(counter.keys())}

    def stats(arr):
        return {
            "mean": round(mean(arr), 2),
            "median": round(median(arr), 2),
            "stdev": round(stdev(arr), 2) if len(arr) > 1 else 0,
            "min": min(arr),
            "max": max(arr),
        }

    resultado = {
        "total_pares_analisados": len(repeticoes_geral),
        "geral": {
            "stats": stats(repeticoes_geral),
            "distribuicao": dist(Counter(repeticoes_geral)),
        },
        "pares": {
            "stats": stats(repeticoes_pares),
            "distribuicao": dist(Counter(repeticoes_pares)),
        },
        "impares": {
            "stats": stats(repeticoes_impares),
            "distribuicao": dist(Counter(repeticoes_impares)),
        },
        "primos": {
            "stats": stats(repeticoes_primos),
            "distribuicao": dist(Counter(repeticoes_primos)),
        },
        "fibonacci": {
            "stats": stats(repeticoes_fibonacci),
            "distribuicao": dist(Counter(repeticoes_fibonacci)),
        },
        "consecutivos": {
            "stats": stats(repeticoes_consecutivos_count),
            "distribuicao": dist(Counter(repeticoes_consecutivos_count)),
        },
        "casos_extremos": {
            "max_repeticao_geral": [
                {"concurso": d["concurso"], "repetidos": d["repetidos_geral"]}
                for d in detalhes_por_concurso if d["repetidos_geral"] == max(repeticoes_geral)
            ],
            "min_repeticao_geral": [
                {"concurso": d["concurso"], "repetidos": d["repetidos_geral"]}
                for d in detalhes_por_concurso if d["repetidos_geral"] == min(repeticoes_geral)
            ],
        },
        "ultimo_caso": detalhes_por_concurso[-1],
    }

    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    # Salvar detalhes completos para analise
    with open("analise_repeticoes_historico.json", "w", encoding="utf-8") as f:
        json.dump(detalhes_por_concurso, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
