path = 'lotofacil_lite/interfaces/super_menu.py'
with open(path, encoding='utf-8') as f: lines = f.readlines()
for i,l in enumerate(lines):
    if i < 19000 or i > 19950: continue
    if '            else:' in l:
        ctx = any('cobertura_k_3c_302' in lines[j] for j in range(max(0,i-10),i))
        if ctx:
            lines[i] = "            elif modo_3camadas_302 == 'D':\n"
            e_blk = [
                "            elif modo_3camadas_302 == 'E':\n",
                '                try:\n',
                '                    _ei2=input("   Minimo C1 [3-5, ENTER=4]: ").strip()\n',
                '                    min_c1_e_302=int(_ei2) if _ei2.isdigit() and 3<=int(_ei2)<=5 else 4\n',
                '                except: min_c1_e_302=4\n',
                '                print(f"   Estrat. E -- min {min_c1_e_302}/5 C1 -- ~202k (41% cob.)")\n',
            ]
            for j,el in enumerate(e_blk): lines.insert(i+2+j, el)
            print(f'Fix! elif D/E 302 em L{i+1}'); break
with open(path,'w',encoding='utf-8') as f: f.writelines(lines)
import ast
with open(path,encoding='utf-8') as f: src=f.read()
try: ast.parse(src); print('SINTAXE OK --', len(src.splitlines()))
except SyntaxError as e: print('ERRO L'+str(e.lineno)+': '+str(e.msg))
