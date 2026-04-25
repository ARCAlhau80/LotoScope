import sys

with open('lotofacil_lite/interfaces/super_menu.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total: {len(lines)} linhas")

# ───────────────────────────────────────────────────────────────────
# PATCH 2: Op31 PASSO 4.5 — adicionar branch 3-camadas ANTES do
# bloco 'if numeros_fixos:' dentro do bloco de geração
# ───────────────────────────────────────────────────────────────────
# Localizar o if numeros_fixos DEPOIS do PASSO 4.5 (linha ~14445 agora)
IDX_PASSO45 = next(i for i,l in enumerate(lines) if 'PASSO 4.5: GERAR' in l)
# Encontrar 'if numeros_fixos:' logo depois de PASSO 4.5
IDX_IF_FIXOS = next(
    i for i,l in enumerate(lines[IDX_PASSO45:], start=IDX_PASSO45)
    if l.strip().startswith('if numeros_fixos:')
)
print(f"PASSO4.5 linha {IDX_PASSO45+1}, if numeros_fixos linha {IDX_IF_FIXOS+1}")
print(f"  contexto: {repr(lines[IDX_IF_FIXOS][:60])}")

GEN_3C_CODE = """\
            # ═══════════════════════════════════════════════════════════════════
            # GERAÇÃO 3-CAMADAS (Estratégia C / D) — quando modo_3camadas ativo
            # ═══════════════════════════════════════════════════════════════════
            if modo_3camadas in ('C', 'D'):
                import random as _rnd3c
                # Ordenar pool_23 por score crescente (baixo = mais confiável)
                if usar_neural_puro and scores_neural:
                    _pool3c_sorted = sorted(pool_23, key=lambda n: scores_neural.get(n, 0))
                elif usar_hibrido and ranking_hibrido:
                    _sh = {h['num']: h['score_hibrido'] for h in ranking_hibrido}
                    _pool3c_sorted = sorted(pool_23, key=lambda n: _sh.get(n, 0))
                else:
                    _si = {c['num']: c['score'] for c in candidatos}
                    _pool3c_sorted = sorted(pool_23, key=lambda n: _si.get(n, 0))

                _sz = len(_pool3c_sorted)
                _c2s = (_sz - 5) // 2
                _c3s = (_sz - 5) - _c2s
                c1_3c = _pool3c_sorted[:5]
                c2_3c = _pool3c_sorted[5:5+_c2s]
                c3_3c = _pool3c_sorted[5+_c2s:]

                print(f"   🏗️  GERAÇÃO 3-CAMADAS ATIVA:")
                print(f"      C1 (FIXOS 5):  {c1_3c}")
                print(f"      C2 (MID {_c2s}):  {c2_3c}")
                print(f"      C3 (LOW {_c3s}):  {c3_3c}")

                _c2_combos = list(combinations(c2_3c, 5))
                _c3_combos = list(combinations(c3_3c, 5))
                _fixos3c = tuple(sorted(c1_3c))

                if modo_3camadas == 'C':
                    # Estratégia C: K combos C3 por combo C2 (cobertura controlada)
                    _k_eff = min(cobertura_k_3c, len(_c3_combos))
                    if _k_eff < len(_c3_combos):
                        _c3_sample = _rnd3c.sample(_c3_combos, _k_eff)
                    else:
                        _c3_sample = _c3_combos
                    print(f"      Modo C: K={_k_eff} → {len(_c2_combos)*_k_eff:,} combos antes dos filtros")
                else:
                    # Estratégia D: todas as combinações C2×C3
                    _c3_sample = _c3_combos
                    print(f"      Modo D: {len(_c2_combos)*len(_c3_combos):,} combos → filtros por nível")

                inicio = time.time()
                todas_combos = []
                for _cc2 in _c2_combos:
                    for _cc3 in _c3_sample:
                        todas_combos.append(tuple(sorted(_fixos3c + _cc2 + _cc3)))
                tempo_geracao = time.time() - inicio
                print(f"   ✅ {len(todas_combos):,} combinações em {tempo_geracao:.1f}s")
                print(f"   💡 Redução de {(1 - len(todas_combos)/490314)*100:.1f}% vs Pool 23 completo!")
                # Registrar C1 como fixos para exibição/relatório
                numeros_fixos = set(c1_3c)
                combos_suaves_count = 0  # suave não aplica no modo 3-camadas
            el"""

# Remover 'el' do final para conectar ao 'if numeros_fixos:'
GEN_3C_CODE = GEN_3C_CODE[:-2]  # remove 'el'
GEN_3C_CODE += "elif "

lines[IDX_IF_FIXOS] = GEN_3C_CODE + lines[IDX_IF_FIXOS].lstrip()

with open('lotofacil_lite/interfaces/super_menu.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("PATCH 2 OK — geração 3-camadas adicionada na Op31")
