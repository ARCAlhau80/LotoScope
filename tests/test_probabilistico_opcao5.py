#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 VERIFICAÇÃO — Opção [5] Comparar TODOS modos probabilísticos existe?
==========================================================================

RED-PHASE TEST: Valida que opção [5] de comparação de filtros está implementada
no menu de filtros probabilísticos da opção 30.4.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

def verificar_opcao_5():
    """Verifica se opção [5] comparar todos está no código"""
    
    super_menu_path = ROOT_DIR / 'lotofacil_lite' / 'interfaces' / 'super_menu.py'
    
    with open(super_menu_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    checks = {
        "Menu mostra [5]": "Comparar TODOS modos" in conteudo,
        "Variável _comparar_todos_prob_hist": "_comparar_todos_prob_hist" in conteudo,
        "Modo 5 = True": "elif modo_prob == '5':" in conteudo,
        "Comparação de probabilísticos lógica": "if _comparar_estr_hist or _comparar_todos_prob_hist:" in conteudo,
        "Carregamento múltiplos filtros": "_fp_dict_c" in conteudo,
    }
    
    print("\n" + "="*70)
    print("🧪 VERIFICAÇÃO — Opção [5] Comparação de Filtros Probabilísticos")
    print("="*70)
    
    todos_ok = True
    for descricao, presente in checks.items():
        status = "✅" if presente else "❌"
        print(f"  {status} {descricao}")
        if not presente:
            todos_ok = False
    
    print("\n" + "="*70)
    if todos_ok:
        print("✅ TODOS OS COMPONENTES PRESENTES")
        print("   Problema pode ser: bugs na lógica, não grava resultado, etc.")
    else:
        print("❌ FALTAM COMPONENTES — Implementação incompleta!")
    print("="*70)
    
    return todos_ok


if __name__ == '__main__':
    resultado = verificar_opcao_5()
    sys.exit(0 if resultado else 1)
