with open('lotofacil_lite/interfaces/super_menu.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total: {len(lines)} linhas")

# FIX 1: Corrigir "elif if numeros_fixos:" → "elif numeros_fixos:" (linha ~14509)
# FIX 2: Remover bloco 3-camadas duplicado (linhas ~14562..14617) e restaurar
#         "if numeros_fixos:" com indentação 24 spaces (para o loop de exclusão suave)

# Localizar as ocorrências de "elif if numeros_fixos:"
bad_lines = [i for i,l in enumerate(lines) if 'elif if numeros_fixos' in l]
print(f"Linhas com 'elif if numeros_fixos': {[b+1 for b in bad_lines]}")

# FIX 1: Primeira ocorrência → corrigir para 'elif numeros_fixos:'
if len(bad_lines) >= 1:
    i1 = bad_lines[0]
    lines[i1] = '            elif numeros_fixos:\n'
    print(f"FIX 1 OK: linha {i1+1} corrigida para 'elif numeros_fixos:'")

# FIX 2: Segunda ocorrência → encontrar início do bloco 3-camadas duplicado ANTES
if len(bad_lines) >= 2:
    i2 = bad_lines[1]
    # Procurar início do bloco 3-camadas (# GERAÇÃO 3-CAMADAS) antes de i2
    start_dup = None
    for i in range(i2-1, i2-80, -1):
        if '# GERAÇÃO 3-CAMADAS' in lines[i]:
            start_dup = i
            break
    
    if start_dup is not None:
        print(f"FIX 2: removendo linhas {start_dup+1}..{i2+1} (bloco duplicado)")
        # Substituir por restauração da linha original (if numeros_fixos: com 24 spaces)
        lines[start_dup:i2+1] = ['                        if numeros_fixos:\n']
        print(f"FIX 2 OK: restaurado 'if numeros_fixos:' com 24 espaços em L{start_dup+1}")
    else:
        print(f"ERRO FIX 2: não encontrou início do bloco duplicado")
else:
    print(f"AVISO: apenas 1 ocorrência de 'elif if numeros_fixos:' encontrada")

with open('lotofacil_lite/interfaces/super_menu.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print(f"Arquivo salvo. Total: {len(lines)} linhas")
