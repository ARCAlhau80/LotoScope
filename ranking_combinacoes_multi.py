import pyodbc
import argparse
import json

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)

PERFIS = {
    "foco11": {
        "descricao": "Foco em 11 acertos",
        "freq": {"11": 1.0, "12": 0.25, "13": 0.05, "14": 0.01},
        "atraso": {"11": 1.0, "12": 0.3, "13": 0.1, "14": 0.05},
    },
    "equilibrado": {
        "descricao": "Peso equilibrado entre categorias",
        "freq": {"11": 1.0, "12": 1.0, "13": 1.0, "14": 1.0},
        "atraso": {"11": 1.0, "12": 1.0, "13": 1.0, "14": 1.0},
    },
    "altovalor": {
        "descricao": "Peso maior para 13 e 14 acertos",
        "freq": {"11": 0.3, "12": 1.0, "13": 5.0, "14": 20.0},
        "atraso": {"11": 0.3, "12": 1.0, "13": 5.0, "14": 20.0},
    },
}


def calcular_medias(cur, ultimo_concurso):
    medias = {}
    for cat in ["11", "12", "13", "14"]:
        cur.execute(f"""
            SELECT AVG(CAST(Acertos_{cat} AS FLOAT)),
                   AVG(CAST(? - Ultimo_Acertos_{cat} AS FLOAT))
            FROM COMBINACOES_LOTOFACIL
            WHERE Acertos_{cat} > 0
        """, (ultimo_concurso,))
        row = cur.fetchone()
        medias[cat] = {
            "freq": row[0] or 1.0,
            "atraso": row[1] or 1.0,
        }
    return medias


def executar_ranking(perfil, top=50):
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()

    for row in cur.execute("SELECT MAX(UltimoConcursoAtualizado) FROM COMBINACOES_LOTOFACIL"):
        ultimo_concurso = row[0]

    medias = calcular_medias(cur, ultimo_concurso)
    print(f"Perfil: {perfil} - {PERFIS[perfil]['descricao']}")
    print(f"Ultimo concurso: {ultimo_concurso}")
    print("Medias (freq / atraso):")
    for cat in ["11", "12", "13", "14"]:
        print(f"  {cat}: {medias[cat]['freq']:.2f} / {medias[cat]['atraso']:.2f}")

    cols = ", ".join([f"N{i}" for i in range(1, 16)])
    acertos_cols = ", ".join([f"Acertos_{c}" for c in ["11", "12", "13", "14"]])
    ultimo_cols = ", ".join([f"Ultimo_Acertos_{c}" for c in ["11", "12", "13", "14"]])

    freq_expr = " + ".join(
        f"(CAST(Acertos_{c} AS FLOAT) / {medias[c]['freq']}) * {PERFIS[perfil]['freq'][c]}"
        for c in ["11", "12", "13", "14"]
    )
    atraso_expr = " + ".join(
        f"(CAST({ultimo_concurso} - Ultimo_Acertos_{c} AS FLOAT) / {medias[c]['atraso']}) * {PERFIS[perfil]['atraso'][c]}"
        for c in ["11", "12", "13", "14"]
    )

    query = f"""
    SELECT TOP {top}
        ID, {cols},
        {acertos_cols},
        {ultimo_cols},
        ({freq_expr}) + ({atraso_expr}) AS score
    FROM COMBINACOES_LOTOFACIL
    ORDER BY score DESC
    """

    resultados = []
    print(f"\n{'ID':>8} {'Combinacao':<50} {'11':>4} {'12':>4} {'13':>4} {'14':>4} {'A11':>5} {'A12':>5} {'A13':>5} {'A14':>5} {'Score':>8}")
    print("-" * 105)
    for row in cur.execute(query):
        idc = row[0]
        nums = row[1:16]
        a11, a12, a13, a14 = row[16], row[17], row[18], row[19]
        u11, u12, u13, u14 = row[20], row[21], row[22], row[23]
        score = row[24]
        nums_str = " ".join(f"{n:02d}" for n in nums)
        print(f"{idc:>8} {nums_str:<50} {a11:>4} {a12:>4} {a13:>4} {a14:>4} {ultimo_concurso-u11:>5} {ultimo_concurso-u12:>5} {ultimo_concurso-u13:>5} {ultimo_concurso-u14:>5} {score:>8.2f}")
        resultados.append({
            "id": idc,
            "combinacao": list(nums),
            "acertos": {"11": a11, "12": a12, "13": a13, "14": a14},
            "atrasos": {"11": ultimo_concurso-u11, "12": ultimo_concurso-u12, "13": ultimo_concurso-u13, "14": ultimo_concurso-u14},
            "score": score,
        })

    return resultados


def main():
    parser = argparse.ArgumentParser(description="Ranking multi-categoria de combinacoes da Lotofacil")
    parser.add_argument("--perfil", choices=list(PERFIS.keys()), default="foco11",
                        help="Perfil de ponderacao")
    parser.add_argument("--top", type=int, default=50,
                        help="Quantidade de combinacoes no ranking")
    parser.add_argument("--out", type=str, default=None,
                        help="Arquivo JSON para salvar o ranking")
    args = parser.parse_args()

    resultados = executar_ranking(args.perfil, args.top)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({
                "perfil": args.perfil,
                "descricao": PERFIS[args.perfil]["descricao"],
                "total": len(resultados),
                "ranking": resultados,
            }, f, ensure_ascii=False, indent=2)
        print(f"\nSalvo em: {args.out}")


if __name__ == "__main__":
    main()
