with open('lotofacil_lite/interfaces/super_menu.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total: {len(lines)} linhas")

# ─────────────────────────────────────────────────────────────────
# PATCH 3: Op30.2 — Inserir menu 3-camadas depois da seção candidatos
# Âncora: "PASSO 2.5: CANDIDATOS" — inserir ANTES desta linha
# ─────────────────────────────────────────────────────────────────
IDX_CANDIDATOS = next(i for i,l in enumerate(lines) if 'PASSO 2.5: CANDIDATOS' in l)
print(f"CANDIDATOS linha {IDX_CANDIDATOS+1}: {repr(lines[IDX_CANDIDATOS][:60])}")

# Verificar se já foi inserido
already = any('modo_3camadas_302' in l for l in lines)
if already:
    print("PATCH 3 JA APLICADO - pulando")
else:
    MENU_3C_302 = """\

        # ═══════════════════════════════════════════════════════════════════
        # MODO DE GERAÇÃO: Padrão ou 3-CAMADAS (Estratégia C / D) — Op30.2
        # ═══════════════════════════════════════════════════════════════════
        modo_3camadas_302 = None   # None=padrão | 'C'=cobertura K | 'D'=3-cam
        cobertura_k_3c_302 = 126
        from math import comb as _cn3c_302
        _ps3c_302 = 25 - qtd_excluir
        _c2s3c_302 = (_ps3c_302 - 5) // 2
        _c3s3c_302 = (_ps3c_302 - 5) - _c2s3c_302
        _c2_cnt_302 = _cn3c_302(_c2s3c_302, 5)
        _c3_cnt_302 = _cn3c_302(_c3s3c_302, 5)
        _total_3c_302 = _c2_cnt_302 * _c3_cnt_302

        print("\\n" + "─"*78)
        print("🏗️  MODO DE GERAÇÃO: 3-CAMADAS (opcional)")
        print("─"*78)
        print(f"   Pool {_ps3c_302} dividido por score estratégia ativa:")
        print(f"      C1—FIXOS ({5} melhores): em TODAS as combos")
        print(f"      C2—MID   ({_c2s3c_302} números): escolher 5 → {_c2_cnt_302} combos")
        print(f"      C3—LOW   ({_c3s3c_302} números): escolher 5 → {_c3_cnt_302} combos")
        print(f"   [P] Pool {_ps3c_302} completo         → até {_cn3c_302(_ps3c_302,15):,} combos  ⭐")
        print(f"   [C] Estrat. C — Cobertura K  → {_total_3c_302:,} combos máx (K config)")
        print(f"   [D] Estrat. D — 3-Cam+Filtro → ~2.000-5.000 combos via filtros")
        try:
            _modo3c_inp_302 = input("   Escolha [P/C/D, ENTER=P]: ").strip().upper()
        except:
            _modo3c_inp_302 = 'P'
        if _modo3c_inp_302 in ('C', 'D'):
            modo_3camadas_302 = _modo3c_inp_302
            if modo_3camadas_302 == 'C':
                print(f"   📊 K: K=1:{_c2_cnt_302} | K=10:{_c2_cnt_302*10:,} | K={_c3_cnt_302}:{_total_3c_302:,}")
                try:
                    _k_inp_302 = input(f"   Digite K [1-{_c3_cnt_302}, ENTER={_c3_cnt_302}]: ").strip()
                    cobertura_k_3c_302 = int(_k_inp_302) if _k_inp_302 else _c3_cnt_302
                    cobertura_k_3c_302 = max(1, min(_c3_cnt_302, cobertura_k_3c_302))
                except:
                    cobertura_k_3c_302 = _c3_cnt_302
                print(f"   ✅ Estrat. C — K={cobertura_k_3c_302} → {_c2_cnt_302 * cobertura_k_3c_302:,} combos")
            else:
                print(f"   ✅ Estrat. D — {_total_3c_302:,} combos → filtros por nível")
            print(f"   📋 Ordenação: score estratégia ativa crescente (C1=mais confiável)")
        else:
            modo_3camadas_302 = None
            print(f"   ✅ Modo padrão Pool {_ps3c_302} completo")
"""
    lines.insert(IDX_CANDIDATOS, MENU_3C_302)
    print(f"PATCH 3 OK — menu 3-camadas inserido antes de L{IDX_CANDIDATOS+1}")
    with open('lotofacil_lite/interfaces/super_menu.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Arquivo salvo PATCH 3.")
