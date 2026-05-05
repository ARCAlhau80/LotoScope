import ast, re
path = 'lotofacil_lite/interfaces/super_menu.py'
with open(path, encoding='utf-8') as fh: lines = fh.readlines()
n = len(lines); changes = []

# === E1: add min_c1_e init after modo_3camadas = None ===
for i,l in enumerate(lines):
    if 'modo_3camadas = None' in l and 'C' in l and i < 13200:
        lines.insert(i+1, '        min_c1_e = 4  # Estrat. E: min numeros C1 em cada combo (3-5)\n')
        print(f'E1: min_c1_e inserido apos L{i+1}'); break

# === E2a: add [E] display line after [D] line ===
from math import comb as _cc
_est_e = 5*_cc(18,11) + _cc(18,10)
for i,l in enumerate(lines):
    if '[D] Estrat. D' in l and '3-Cam' in l and i < 13300:
        el = '        print(f"   [E] Estrat. E \u2014 Soft C1 min4/5  \u2192 ~' + str(_est_e) + ' combos (41% cobert.) \u2b50")' + '\n'
        lines.insert(i+1, el)
        print(f'E2a: [E] display inserido apos L{i+1}'); break

# === E2b: change input prompt [P/C/D -> P/C/D/E] ===
for i,l in enumerate(lines):
    if 'Escolha [P/C/D, ENTER=P]' in l and i < 13300:
        lines[i] = l.replace('[P/C/D, ENTER=P]','[P/C/D/E, ENTER=P]')
        print(f'E2b: prompt alterado L{i+1}'); break

# === E2c: add E to outer if condition ===
for i,l in enumerate(lines):
    if "_modo3c_inp in ('C', 'D'):" in l and i < 13300:
        lines[i] = l.replace("('C', 'D'):","('C', 'D', 'E'):")
        print(f'E2c: if C/D/E L{i+1}'); break

# === E2d: change D handler else -> elif + add E block ===
for i,l in enumerate(lines):
    if '            else:' in l and i < 13300:
        if any('cobertura_k_3c =' in lines[j] for j in range(max(0,i-8),i)):
            lines[i] = "            elif modo_3camadas == 'D':\n"
            e_blk = [
                "            elif modo_3camadas == 'E':\n",
                '                try:\n',
                '                    _e_inp = input("   Minimo C1 em cada combo [3-5, ENTER=4]: ").strip()\n',
                '                    min_c1_e = int(_e_inp) if _e_inp.isdigit() and 3<=int(_e_inp)<=5 else 4\n',
                '                except:\n',
                '                    min_c1_e = 4\n',
                '                print(f"   OK Estrat. E -- min {min_c1_e}/5 C1 -- ~202k combos (41% cobertura)")\n',
            ]
            for j,el in enumerate(e_blk): lines.insert(i+2+j, el)
            print(f'E2d: elif D + elif E inseridos em L{i+1}'); break

# === E3: generation block Op31 -- insert elif E before elif numeros_fixos ===
for i,l in enumerate(lines):
    if 'elif numeros_fixos:' in l and 14000 < i < 15000:
        e_gen = [
            "            elif modo_3camadas == 'E':\n",
            '                # Estrat. E: Pool 23 c/ filtro Soft C1 (min 4/5)\n',
            '                if usar_neural_puro and scores_neural:\n',
            '                    _p3e=sorted(pool_23,key=lambda n:scores_neural.get(n,0))\n',
            '                elif usar_hibrido and ranking_hibrido:\n',
            '                    _sh_e={h["num"]:h["score_hibrido"] for h in ranking_hibrido}\n',
            '                    _p3e=sorted(pool_23,key=lambda n:_sh_e.get(n,0))\n',
            '                else:\n',
            '                    _si_e={c["num"]:c["score"] for c in candidatos}\n',
            '                    _p3e=sorted(pool_23,key=lambda n:_si_e.get(n,0))\n',
            '                _c1_e=set(_p3e[:5])\n',
            '                print(f"   ESTRAT. E -- C1={sorted(_c1_e)} min={min_c1_e}/5")\n',
            '                inicio=time.time()\n',
            '                todas_combos=[c for c in combinations(pool_23,15) if len(set(c)&_c1_e)>=min_c1_e]\n',
            '                tempo_geracao=time.time()-inicio\n',
            '                print(f"   {len(todas_combos):,} combos em {tempo_geracao:.1f}s  -- {(1-len(todas_combos)/490314)*100:.1f}% reducao")\n',
            '                combos_suaves_count=0\n',
        ]
        for j,el in enumerate(e_gen): lines.insert(i+j,el)
        print(f'E3: bloco E gen inserido antes L{i+1}'); break

# === E4: Op30.2 menu -- add [E] + prompt + if condition ===
for i,l in enumerate(lines):
    if '[D] Estrat. D' in l and '3-Cam' in l and i > 19000:
        el2 = '        print(f"   [E] Estrat. E \u2014 Soft C1 min4/5  \u2192 ~' + str(_est_e) + ' combos (41% cobert.) \u2b50")' + '\n'
        lines.insert(i+1, el2)
        print(f'E4a: [E] 302 display inserido apos L{i+1}'); break
for i,l in enumerate(lines):
    if 'Escolha [P/C/D, ENTER=P]' in l and i > 19000:
        lines[i]=l.replace('[P/C/D, ENTER=P]','[P/C/D/E, ENTER=P]')
        print(f'E4b: 302 prompt L{i+1}'); break
for i,l in enumerate(lines):
    if "_modo3c_inp_302 in ('C', 'D'):" in l and i > 19000:
        lines[i]=l.replace("('C', 'D'):","('C', 'D', 'E'):")
        print(f'E4c: 302 if C/D/E L{i+1}'); break

# === E5: Op30.2 generation block -- add min_c1_e_302 init ===
for i,l in enumerate(lines):
    if 'modo_3camadas_302 = None' in l and i > 19000 and i < 20200:
        lines.insert(i+1,'        min_c1_e_302 = 4  # Estrat. E 302\n')
        print(f'E5a: min_c1_e_302 inserido L{i+1}'); break
for i,l in enumerate(lines):
    if "_modo3c_inp_302 in ('C', 'D', 'E'):" in l and i > 19000:
        lines[i+1] = lines[i+1].replace("('C', 'D')","('C', 'D', 'E')")
        print(f'E5b noop L{i+1}'); break

# === E6: Op30.2 generation block -- insert elif E before elif numeros_fixos ===
for i,l in enumerate(lines):
    if 'elif numeros_fixos:' in l and i > 20000:
        e_gen2 = [
            "        elif modo_3camadas_302 == 'E':\n",
            '            _si2={c["num"]:c["score"] for c in ranking_ativo_302}\n',
            '            if neural_302_disponivel and scores_neural_302:\n',
            '                _p3e2=sorted(pool_23,key=lambda n:scores_neural_302.get(n,0))\n',
            '            else:\n',
            '                _p3e2=sorted(pool_23,key=lambda n:_si2.get(n,0))\n',
            '            _c1_e2=set(_p3e2[:5])\n',
            '            print(f"   ESTRAT. E 302 -- C1={sorted(_c1_e2)} min={min_c1_e_302}/5")\n',
            '            inicio=time.time()\n',
            '            todas_combos=[c for c in combinations(pool_23,15) if len(set(c)&_c1_e2)>=min_c1_e_302]\n',
            '            print(f"   {len(todas_combos):,} combos em {time.time()-inicio:.1f}s")\n',
            '            combos_suaves_count_302=0\n',
        ]
        for j,el in enumerate(e_gen2): lines.insert(i+j,el)
        print(f'E6: bloco E 302 inserido L{i+1}'); break

# === SALVAR E VERIFICAR SINTAXE ===
with open(path,'w',encoding='utf-8') as fh: fh.writelines(lines)
import ast
with open(path,encoding='utf-8') as fh: src=fh.read()
try:
    ast.parse(src); print(f'SINTAXE OK -- {len(src.splitlines())} linhas')
except SyntaxError as e:
    print(f'ERRO L{e.lineno}: {e.msg}')
    lns=src.splitlines()
    for k in range(max(0,e.lineno-3),min(len(lns),e.lineno+3)): print(f'  L{k+1}: {repr(lns[k][:80])}')
