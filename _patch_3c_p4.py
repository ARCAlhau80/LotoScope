with open('lotofacil_lite/interfaces/super_menu.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total: {len(lines)} linhas")

# Localizar os 2 if/else a 8-space indentation depois da linha "Gerar todas"
IDX_GERAR = next(i for i,l in enumerate(lines) if 'Gerar todas as combina' in l and 'sem n' in l)
print(f"Gerar base: L{IDX_GERAR+1}")

# Encontrar if numeros_fixos a 8 espaços logo depois
IDX_IF = None
for i in range(IDX_GERAR, IDX_GERAR+10):
    if lines[i].rstrip() == '        if numeros_fixos:':
        IDX_IF = i
        break

if IDX_IF is None:
    print("ERRO: 'if numeros_fixos:' com 8 espaços nao encontrado")
    import sys; sys.exit(1)

print(f"if numeros_fixos linha {IDX_IF+1}: {repr(lines[IDX_IF][:60])}")

GEN_3C_302 = """\
        # GERAÇÃO 3-CAMADAS 302 (Estratégia C / D) — quando modo_3camadas_302 ativo
        if modo_3camadas_302 in ('C', 'D'):
            import random as _rnd3c_302
            # Ordenar pool_23 por score crescente da estratégia ativa (baixo = confiável)
            _si_302 = {c['num']: c['score'] for c in ranking_ativo_302}
            if neural_302_disponivel and scores_neural_302:
                _pool3c_sorted_302 = sorted(pool_23, key=lambda n: scores_neural_302.get(n, 0))
            else:
                _pool3c_sorted_302 = sorted(pool_23, key=lambda n: _si_302.get(n, 0))

            _sz_302 = len(_pool3c_sorted_302)
            _c2s_302 = (_sz_302 - 5) // 2
            _c3s_302 = (_sz_302 - 5) - _c2s_302
            c1_3c_302 = _pool3c_sorted_302[:5]
            c2_3c_302 = _pool3c_sorted_302[5:5+_c2s_302]
            c3_3c_302 = _pool3c_sorted_302[5+_c2s_302:]

            print(f"   🏗️  GERAÇÃO 3-CAMADAS ATIVA (backtesting):")
            print(f"      C1 (FIXOS 5): {c1_3c_302}")
            print(f"      C2 (MID {_c2s_302}):  {c2_3c_302}")
            print(f"      C3 (LOW {_c3s_302}):  {c3_3c_302}")

            _c2_combos_302 = list(combinations(c2_3c_302, 5))
            _c3_combos_302 = list(combinations(c3_3c_302, 5))
            _fixos3c_302 = tuple(sorted(c1_3c_302))

            if modo_3camadas_302 == 'C':
                _k_eff_302 = min(cobertura_k_3c_302, len(_c3_combos_302))
                if _k_eff_302 < len(_c3_combos_302):
                    _c3_sample_302 = _rnd3c_302.sample(_c3_combos_302, _k_eff_302)
                else:
                    _c3_sample_302 = _c3_combos_302
                print(f"      Modo C: K={_k_eff_302} → {len(_c2_combos_302)*_k_eff_302:,} combos")
            else:
                _c3_sample_302 = _c3_combos_302
                print(f"      Modo D: {len(_c2_combos_302)*len(_c3_combos_302):,} combos → filtros")

            inicio = time.time()
            todas_combos = []
            for _cc2 in _c2_combos_302:
                for _cc3 in _c3_sample_302:
                    todas_combos.append(tuple(sorted(_fixos3c_302 + _cc2 + _cc3)))
            print(f"   ✅ {len(todas_combos):,} combinações em {time.time()-inicio:.1f}s")
            numeros_fixos = set(c1_3c_302)
            combos_suaves_count_302 = 0
        el"""

GEN_3C_302 = GEN_3C_302[:-2] + "if "
lines[IDX_IF] = GEN_3C_302 + lines[IDX_IF].lstrip()

with open('lotofacil_lite/interfaces/super_menu.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("PATCH 4 OK — geração 3-camadas adicionada na Op30.2")
