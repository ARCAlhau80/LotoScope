import sys

with open('lotofacil_lite/interfaces/super_menu.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total linhas: {len(lines)}")

# ─────────────────────────────────────────────────────────────────
# PATCH 1 (Op31): Inserir menu 3-camadas antes linha 13107
# (antes do comentário 'A geração real acontece...')
# ─────────────────────────────────────────────────────────────────
INSERT_1_BEFORE = 13107 - 1  # 0-indexed = 13106

MENU_3C_CODE = """\

        # ═══════════════════════════════════════════════════════════════════
        # MODO DE GERAÇÃO: Padrão ou 3-CAMADAS (Estratégia C / D)
        # C1 (FIXOS 5): números de maior confiança → em todas as combos
        # C2 (MID 9) : próximos 9 → escolher 5 → C(9,5) = 126 combos
        # C3 (LOW 9) : últimos 9  → escolher 5 → C(9,5) = 126 combos
        # Total: 126 × 126 = 15.876 (vs 490k Pool 23 completo)
        # ═══════════════════════════════════════════════════════════════════
        modo_3camadas = None   # None=padrão | 'C'=cobertura K | 'D'=3-cam+filtros
        cobertura_k_3c = 126
        from math import comb as _cn3c
        _ps3c = 25 - qtd_excluir
        _c2s3c = (_ps3c - 5) // 2
        _c3s3c = (_ps3c - 5) - _c2s3c
        _c2_cnt = _cn3c(_c2s3c, 5)
        _c3_cnt = _cn3c(_c3s3c, 5)
        _total_3c = _c2_cnt * _c3_cnt

        print("\\n" + "─"*78)
        print("🏗️  MODO DE GERAÇÃO: 3-CAMADAS (opcional)")
        print("─"*78)
        print(f"   Pool {_ps3c} dividido por score (neural/INVERTIDA):")
        print(f"      C1—FIXOS ({5} melhores): em TODAS as combos")
        print(f"      C2—MID   ({_c2s3c} números): escolher 5 → {_c2_cnt} combos")
        print(f"      C3—LOW   ({_c3s3c} números): escolher 5 → {_c3_cnt} combos")
        print(f"   [P] Pool {_ps3c} completo         → até {_cn3c(_ps3c,15):,} combos  ⭐")
        print(f"   [C] Estrat. C — Cobertura K  → {_total_3c:,} combos máx (K config)")
        print(f"   [D] Estrat. D — 3-Cam+Filtro → ~2.000-5.000 combos via filtros")
        try:
            _modo3c_inp = input("   Escolha [P/C/D, ENTER=P]: ").strip().upper()
        except:
            _modo3c_inp = 'P'
        if _modo3c_inp in ('C', 'D'):
            modo_3camadas = _modo3c_inp
            if modo_3camadas == 'C':
                print(f"   📊 K (pares C3 por combo C2):")
                print(f"      K=1:{_c2_cnt:,} | K=10:{_c2_cnt*10:,} | K=50:{_c2_cnt*50:,} | K={_c3_cnt}:{_total_3c:,}")
                try:
                    _k_inp = input(f"   Digite K [1-{_c3_cnt}, ENTER={_c3_cnt}]: ").strip()
                    cobertura_k_3c = int(_k_inp) if _k_inp else _c3_cnt
                    cobertura_k_3c = max(1, min(_c3_cnt, cobertura_k_3c))
                except:
                    cobertura_k_3c = _c3_cnt
                print(f"   ✅ Estrat. C — K={cobertura_k_3c} → {_c2_cnt * cobertura_k_3c:,} combos")
            else:
                print(f"   ✅ Estrat. D — {_total_3c:,} combos → filtros por nível")
            _crit = "NEURAL" if usar_neural_puro else ("HÍBRIDO" if usar_hibrido else "INVERTIDA")
            print(f"   📋 Ordenação: score {_crit} crescente (C1=mais confiável, C3=menos)")
            print("   ℹ️  Fixos manuais (PASSO 4) ignorados no modo 3-Camadas")
        else:
            modo_3camadas = None
            print(f"   ✅ Modo padrão Pool {_ps3c} completo")
"""

# Verifica se a âncora está onde esperamos
expected = "        # A gera"
if not lines[INSERT_1_BEFORE].startswith(expected[:15]):
    print(f"ERRO PATCH 1: linha {INSERT_1_BEFORE+1} = {repr(lines[INSERT_1_BEFORE][:60])}")
    sys.exit(1)

lines.insert(INSERT_1_BEFORE, MENU_3C_CODE)
print(f"PATCH 1 OK — inserido {len(MENU_3C_CODE.splitlines())} linhas antes de {INSERT_1_BEFORE+2}")

with open('lotofacil_lite/interfaces/super_menu.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Arquivo salvo PATCH 1.")
