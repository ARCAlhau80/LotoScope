#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runner da atualização automática da Lotofácil (tarefa agendada do Windows).

Atualiza a tabela Resultados_INT (fonte do dashboard LotoScope — inclusive a
Matriz de Quarentena) com concursos novos já sorteados na Caixa. Sem concurso
novo, sai em silêncio. Log em atualizacao_auto_lotofacil.log (raiz do projeto).

Uso manual:  .venv\Scripts\python.exe atualizar_lotofacil_auto.py
Tarefa:      lotofacil_auto   (agendada 21:45, diário) — ver README da tarefa.
"""

import os
import sys
import datetime
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LOG = os.path.join(ROOT, "atualizacao_auto_lotofacil.log")


def log(msg: str) -> None:
    line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> int:
    from shared.loterias.atualizador_lotofacil import AtualizadorLotofacil

    log("=== Início da atualização automática (Lotofácil) ===")
    atualizador = AtualizadorLotofacil()
    atualizados = atualizador.atualizar_completo(qtde_por_vez=5)
    log(f"Fim: {atualizados} concurso(s) atualizado(s).")
    if atualizados == 0:
        log("Nenhum concurso novo — base já está em dia.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        log("ERRO:\n" + traceback.format_exc())
        sys.exit(1)