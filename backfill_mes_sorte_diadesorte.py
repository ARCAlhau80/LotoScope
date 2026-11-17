"""Preenche a coluna Mes_Sorte em Resultados_DiaDeSorte.

Fonte principal: API pública loteriascaixa-api (traz todos os concursos de uma
vez, com o campo `mesSorte`). Fallback: API oficial da Caixa concurso a
concurso (`nomeTimeCoracaoMesSorte`).

Uso:
    python backfill_mes_sorte_diadesorte.py [--dry-run] [--limite N]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared.loterias.mes_sorte import mes_por_nome

FONTE_TODOS = "https://loteriascaixa-api.herokuapp.com/api/diadesorte"
FONTE_CAIXA = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/{concurso}"


def carregar_todos() -> Dict[int, Optional[int]]:
    resp = requests.get(FONTE_TODOS, timeout=60)
    resp.raise_for_status()
    dados = resp.json()
    if not isinstance(dados, list):
        raise RuntimeError("Formato inesperado da fonte de resultados")

    resultado: Dict[int, Optional[int]] = {}
    for item in dados:
        try:
            concurso = int(item.get("concurso"))
        except (TypeError, ValueError):
            continue
        resultado[concurso] = mes_por_nome(item.get("mesSorte"))
    return resultado


def carregar_concurso_caixa(concurso: int) -> Optional[int]:
    resp = requests.get(FONTE_CAIXA.format(concurso=concurso), timeout=30)
    if resp.status_code != 200:
        return None
    return mes_por_nome(resp.json().get("nomeTimeCoracaoMesSorte"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Não grava no banco")
    parser.add_argument("--limite", type=int, default=0, help="Processa só os N concursos mais recentes")
    parser.add_argument("--sem-fallback", action="store_true", help="Não consulta a Caixa para meses faltantes")
    args = parser.parse_args()

    from lotofacil_lite.utils.database_config import db_config

    if not db_config.test_connection():
        print("ERRO: sem conexão com o banco configurado.")
        return 1

    print("Buscando resultados do Dia de Sorte...")
    try:
        meses = carregar_todos()
    except Exception as exc:  # pragma: no cover - depende de rede
        print(f"Falha na fonte principal ({exc}); usando a API da Caixa.")
        meses = {}

    conn = db_config.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Concurso, Mes_Sorte FROM Resultados_DiaDeSorte ORDER BY Concurso")
        atuais = {int(row[0]): row[1] for row in cursor.fetchall()}
        cursor.close()

        concursos = sorted(atuais)
        if args.limite > 0:
            concursos = concursos[-args.limite:]

        faltantes = [c for c in concursos if meses.get(c) is None and atuais.get(c) is None]
        if faltantes and not args.sem_fallback:
            print(f"Buscando {len(faltantes)} mês(es) faltante(s) na API da Caixa...")
            for i, concurso in enumerate(faltantes, start=1):
                mes = carregar_concurso_caixa(concurso)
                if mes is not None:
                    meses[concurso] = mes
                if i % 50 == 0:
                    print(f"  {i}/{len(faltantes)}...")
                time.sleep(0.1)

        atualizados = 0
        sem_mes = 0
        cursor = conn.cursor()
        for concurso in concursos:
            mes = meses.get(concurso)
            if mes is None:
                sem_mes += 1
                continue
            if not args.dry_run:
                cursor.execute(
                    "UPDATE Resultados_DiaDeSorte SET Mes_Sorte = ? "
                    "WHERE Concurso = ? AND (Mes_Sorte IS NULL OR Mes_Sorte <> ?)",
                    (mes, concurso, mes),
                )
            atualizados += 1
        if not args.dry_run:
            conn.commit()
        cursor.close()
    finally:
        conn.close()

    print(
        f"{'[dry-run] ' if args.dry_run else ''}Concursos com mês: {atualizados} · "
        f"sem mês: {sem_mes} · total analisado: {len(concursos)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
