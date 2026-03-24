#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 TESTE REGRESSIVO — Seleção de Estratégia de Exclusão (Opção 30.2)
======================================================================
Valida que o menu de estratégias [0-5] está presente e funcional no
método _executar_backtesting_pool23 do super_menu.py.

Feature implementada em: 24/03/2026
Estratégias disponíveis:
  [0] Comparar todas (diagnóstico no PASSO 4)
  [1] Débito
  [2] Invertida v3.0 (padrão)
  [3] Q1-Q5 Quadrantes
  [4] Híbrido Invertida + Q1-Q5
  [5] Híbrido TODOS

Como executar:
    cd "C:\\Users\\AR CALHAU\\source\\repos\\LotoScope"
    .venv\\Scripts\\activate
    python tests\\test_backtesting_302_strategy.py
"""

import sys
import io
import os
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

# Configurar path
ROOT_DIR = Path(__file__).parent.parent
LOTOFACIL_DIR = ROOT_DIR / 'lotofacil_lite'

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR / 'interfaces'))
sys.path.insert(0, str(LOTOFACIL_DIR / 'utils'))


def _run_302(inputs_list):
    """Executa _executar_backtesting_pool23 com inputs mockados e captura stdout."""
    from lotofacil_lite.interfaces.super_menu import SuperMenuLotofacil
    inputs = iter(inputs_list)
    buf = io.StringIO()
    with patch('builtins.input', side_effect=lambda prompt='': next(inputs)):
        with redirect_stdout(buf):
            try:
                SuperMenuLotofacil()._executar_backtesting_pool23()
            except StopIteration:
                pass
    return buf.getvalue()


def teste_menu_estrategia_presente():
    """Verifica que o menu [0-5] aparece no início da execução."""
    out = _run_302([''])  # entrada vazia → aceita default e sai
    marcas = [
        'ESTRATÉGIA DE EXCLUSÃO',
        'Débito',          # aparece como "[1] 📉 Débito ..."
        'Invertida v3.0',  # aparece como "[2] 🔥 Invertida v3.0 ..."
        'Comparar TODAS',  # aparece como "[0] 🔄 Comparar TODAS ..."
    ]
    falhas = [m for m in marcas if m not in out]
    if falhas:
        return False, f"Faltam no output: {falhas}"
    return True, "Menu de estratégia exibido corretamente"


def teste_opcao_0_comparar_todas():
    """
    Valida fluxo completo com opção 0 (comparar todas):
      - Menu exibido
      - COMPARAR TODAS confirmado
      - PASSO 4 alcançado
      - Diagnóstico comparativo exibido no PASSO 4
      - Linha '⭐ Melhor no resultado informado' presente
    """
    inputs_list = [
        '0',            # estratégia: comparar todas
        '',             # filtro probabilístico: padrão
        'N',            # sem fixos extras
        '10',           # qtd fixos: 10
        '1 2 3 4 5 7 8 9 11 12',   # números fixos
        '0',            # opção nível: 0
        '1 2 3 4 5 7 8 9 11 12 13 14 15 16 17',  # resultado real
        'N',            # não repetir
        '',             # encerrar
    ]
    out = _run_302(inputs_list)

    marcadores = {
        'ESTRATÉGIA DE EXCLUSÃO': 'Menu de estratégia',
        'COMPARAR TODAS': 'Confirmação opção 0',
        'PASSO 4': 'Passo 4 alcançado',
        'COMPARAÇÃO DE ESTRATÉGIAS (PASSO 4 - DIAGNÓSTICO DE EXCLUSÃO)': 'Diagnóstico comparativo',
        'Melhor no resultado informado': 'Linha vencedora',
    }
    falhas = []
    for marca, descricao in marcadores.items():
        if marca not in out:
            falhas.append(f"{descricao}: FALTOU ({marca!r})")

    if falhas:
        return False, "Falhas:\n  " + "\n  ".join(falhas)
    return True, "Fluxo opção 0 (comparar todas) validado com sucesso"


def teste_opcao_2_padrao():
    """
    Valida que a estratégia padrão [2] (Invertida v3.0) não exibe diagnóstico
    comparativo (comportamento esperado: diagnóstico somente quando opção = 0).
    """
    inputs_list = [
        '2',            # estratégia: Invertida v3.0 (padrão)
        '',             # filtro probabilístico: padrão
        'N',            # sem fixos extras
        '10',           # qtd fixos: 10
        '1 2 3 4 5 7 8 9 11 12',
        '0',
        '1 2 3 4 5 7 8 9 11 12 13 14 15 16 17',
        'N',
        '',
    ]
    out = _run_302(inputs_list)

    diagnostico_presente = 'COMPARAÇÃO DE ESTRATÉGIAS (PASSO 4 - DIAGNÓSTICO DE EXCLUSÃO)' in out
    if diagnostico_presente:
        return False, "Diagnóstico comparativo NÃO deveria aparecer para estratégia 2 (individual)"
    if 'Invertida v3.0' not in out and 'QUENTES' not in out:
        return False, "Estratégia Invertida v3.0 não reconhecida no output"
    return True, "Estratégia 2 individual: sem diagnóstico comparativo (correto)"


# ─── Runner ──────────────────────────────────────────────────────────────────

TESTES = [
    ("Menu estratégia presente",         teste_menu_estrategia_presente),
    ("Opção 0 — comparar todas",         teste_opcao_0_comparar_todas),
    ("Opção 2 — individual sem diag.",   teste_opcao_2_padrao),
]


def main():
    print("=" * 70)
    print("🧪 REGRESSÃO — Estratégia de Exclusão — Opção 30.2")
    print("=" * 70)
    passou = 0
    falhou = 0
    for nome, func in TESTES:
        print(f"\n  ▶ {nome} ...", end=" ", flush=True)
        try:
            ok, msg = func()
            if ok:
                print(f"✅  {msg}")
                passou += 1
            else:
                print(f"❌  {msg}")
                falhou += 1
        except Exception as exc:
            print(f"💥  EXCEÇÃO: {exc}")
            falhou += 1

    print("\n" + "=" * 70)
    print(f"  Resultado: {passou}/{len(TESTES)} testes passaram", end="")
    if falhou == 0:
        print("  ✅ TODOS OK")
    else:
        print(f"  ❌ {falhou} FALHA(S)")
    print("=" * 70)
    return 0 if falhou == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
