#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CORRETOR MASSIVO DE SINTAXE
Corrige TODOS os arquivos com problemas de try/except malformados
"""

import os
import sys
import ast
import re
from pathlib import Path

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent.parent / 'lotofacil_lite'

def verificar_sintaxe(conteudo):
    """Verifica se o código tem erro de sintaxe"""
    try:
        ast.parse(conteudo)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def remover_bom(conteudo):
    """Remove BOM se presente"""
    if conteudo.startswith('\ufeff'):
        return conteudo[1:]
    return conteudo

def corrigir_try_except_malformado(conteudo):
    """
    Corrige o padrão problemático onde um try é inserido dentro de outro.
    
    Padrão ERRADO:
    try:
        from database_config import db_config
    
    # 🚀 SISTEMA DE OTIMIZAÇÃO
    try:
        from database_optimizer import DatabaseOptimizer
    
    except ImportError:
        db_config = None
    
    Padrão CORRETO:
    # 🚀 SISTEMA DE OTIMIZAÇÃO
    try:
        from database_optimizer import DatabaseOptimizer
        _db_optimizer = DatabaseOptimizer()
    except ImportError:
        _db_optimizer = None
    
    try:
        from database_config import db_config
    except ImportError:
        db_config = None
    """
    
    linhas = conteudo.split('\n')
    resultado = []
    i = 0
    modificado = False
    
    while i < len(linhas):
        linha = linhas[i]
        
        # Detectar padrão problemático: try seguido de from database_config
        if linha.strip() == 'try:':
            # Verificar próximas linhas
            bloco_atual = [linha]
            j = i + 1
            
            # Coletar linhas até encontrar outro try: ou except:
            while j < len(linhas):
                proxima = linhas[j]
                
                # Se encontrar OUTRO try: antes de except: - problema!
                if proxima.strip() == 'try:' or proxima.strip().startswith('try:'):
                    # Verificar se é o padrão com database_optimizer
                    if j + 1 < len(linhas) and 'database_optimizer' in linhas[j + 1].lower():
                        # Encontramos o padrão problemático!
                        # Precisamos reestruturar
                        
                        # Primeiro, vamos encontrar o except correspondente
                        k = j + 1
                        optimizer_bloco = []
                        while k < len(linhas) and not linhas[k].strip().startswith('except'):
                            optimizer_bloco.append(linhas[k])
                            k += 1
                        
                        # Agora k está no except
                        if k < len(linhas) and linhas[k].strip().startswith('except'):
                            # Coletar o bloco except
                            except_linha = linhas[k]
                            except_bloco = []
                            k += 1
                            while k < len(linhas) and (linhas[k].startswith('    ') or linhas[k].strip() == ''):
                                if linhas[k].strip() == '' and k + 1 < len(linhas) and not linhas[k+1].startswith('    '):
                                    break
                                except_bloco.append(linhas[k])
                                k += 1
                            
                            # REESTRUTURAR:
                            # 1. Adicionar comentário e bloco do optimizer com seu próprio try/except
                            # 2. Adicionar try original com seu except
                            
                            # Encontrar o comentário do optimizer (linha antes do try problemático)
                            comentario_idx = j - 1
                            while comentario_idx >= i and linhas[comentario_idx].strip() == '':
                                comentario_idx -= 1
                            
                            comentario = []
                            if comentario_idx > i and '🚀' in linhas[comentario_idx]:
                                comentario.append(linhas[comentario_idx])
                            
                            # Montar novo código
                            novo_codigo = []
                            
                            # Comentário do optimizer
                            if comentario:
                                novo_codigo.append(comentario[0])
                            else:
                                novo_codigo.append('# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO')
                            
                            # Bloco try do optimizer
                            novo_codigo.append('try:')
                            novo_codigo.append('    from database_optimizer import DatabaseOptimizer')
                            novo_codigo.append('    _db_optimizer = DatabaseOptimizer()')
                            novo_codigo.append('except ImportError:')
                            novo_codigo.append('    _db_optimizer = None')
                            novo_codigo.append('')
                            
                            # Agora o bloco original de database_config
                            for bl in bloco_atual:
                                novo_codigo.append(bl)
                            
                            # Linhas entre o try original e o try do optimizer (exceto comentário)
                            for idx in range(i + 1, comentario_idx if comentario else j):
                                if linhas[idx].strip() != '' and '🚀' not in linhas[idx]:
                                    novo_codigo.append(linhas[idx])
                            
                            # Except original
                            novo_codigo.append(except_linha)
                            for eb in except_bloco:
                                novo_codigo.append(eb)
                            
                            # Adicionar ao resultado
                            resultado.extend(novo_codigo)
                            i = k
                            modificado = True
                            break
                    else:
                        bloco_atual.append(proxima)
                        j += 1
                elif proxima.strip().startswith('except'):
                    bloco_atual.append(proxima)
                    resultado.extend(bloco_atual)
                    i = j + 1
                    break
                else:
                    bloco_atual.append(proxima)
                    j += 1
            else:
                resultado.extend(bloco_atual)
                i = j
        else:
            resultado.append(linha)
            i += 1
    
    return '\n'.join(resultado), modificado

def corrigir_simples(conteudo):
    """
    Correção mais simples: encontrar e remover blocos try duplicados
    """
    # Padrão: try: seguido de import, depois outro try: antes de except:
    
    # Remove BOM
    conteudo = remover_bom(conteudo)
    
    # Padrão 1: try duplo com database_optimizer no meio
    padrao1 = re.compile(
        r'try:\s*\n(\s+from database_config import db_config.*?)\n'
        r'\s*\n'
        r'# 🚀 SISTEMA DE OTIMIZAÇÃO.*?\n'
        r'try:\s*\n'
        r'\s+from database_optimizer import DatabaseOptimizer.*?\n'
        r'\s+_db_optimizer = DatabaseOptimizer\(\).*?\n'
        r'\s*\n'
        r'(except ImportError:.*?(?=\n\n|\nclass|\ndef|\n#|\Z))',
        re.DOTALL
    )
    
    def substituir1(match):
        db_config_import = match.group(1).strip()
        except_bloco = match.group(2).strip()
        
        return f'''# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    {db_config_import}
{except_bloco}'''
    
    novo_conteudo = padrao1.sub(substituir1, conteudo)
    
    return novo_conteudo, novo_conteudo != conteudo

def corrigir_arquivo(caminho):
    """Corrige um arquivo específico"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except UnicodeDecodeError:
        try:
            with open(caminho, 'r', encoding='latin-1') as f:
                conteudo = f.read()
        except:
            return False, "Erro de encoding"
    
    # Verificar sintaxe original
    ok_original, erro_original = verificar_sintaxe(conteudo)
    if ok_original:
        return True, "Já está OK"
    
    # Remover BOM primeiro
    conteudo = remover_bom(conteudo)
    ok_sem_bom, _ = verificar_sintaxe(conteudo)
    if ok_sem_bom:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return True, "Removido BOM"
    
    # Tentar correção simples
    conteudo_corrigido, modificado = corrigir_simples(conteudo)
    if modificado:
        ok_corrigido, _ = verificar_sintaxe(conteudo_corrigido)
        if ok_corrigido:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo_corrigido)
            return True, "Corrigido padrão try/except"
    
    return False, erro_original

def listar_arquivos_com_erro():
    """Lista todos os arquivos Python com erros de sintaxe"""
    arquivos_erro = []
    
    for pasta in ['geradores', 'analisadores', 'sistemas', 'utils', 'ia', 'validadores', 'interfaces', 'relatorios', 'core']:
        pasta_path = ROOT_DIR / pasta
        if pasta_path.exists():
            for arquivo in pasta_path.glob('*.py'):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                except:
                    try:
                        with open(arquivo, 'r', encoding='latin-1') as f:
                            conteudo = f.read()
                    except:
                        continue
                
                ok, erro = verificar_sintaxe(conteudo)
                if not ok:
                    arquivos_erro.append((arquivo, erro))
    
    return arquivos_erro

def main():
    print("=" * 70)
    print("CORRETOR MASSIVO DE SINTAXE - LotoScope")
    print("=" * 70)
    
    # Listar arquivos com erro
    print("\n📋 Identificando arquivos com erros de sintaxe...")
    arquivos_erro = listar_arquivos_com_erro()
    
    print(f"\n🔍 Encontrados {len(arquivos_erro)} arquivos com problemas:\n")
    
    corrigidos = 0
    falhas = []
    
    for arquivo, erro in arquivos_erro:
        nome_rel = arquivo.relative_to(ROOT_DIR)
        print(f"  → {nome_rel}")
        print(f"    Erro: {erro[:60]}...")
        
        sucesso, msg = corrigir_arquivo(arquivo)
        
        if sucesso:
            print(f"    ✅ {msg}")
            corrigidos += 1
        else:
            print(f"    ❌ Não foi possível corrigir automaticamente")
            falhas.append((arquivo, erro))
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTADO: {corrigidos}/{len(arquivos_erro)} arquivos corrigidos")
    
    if falhas:
        print(f"\n⚠️ {len(falhas)} arquivos precisam de correção manual:")
        for arquivo, erro in falhas:
            print(f"  → {arquivo.relative_to(ROOT_DIR)}")
    
    print("=" * 70)
    return len(falhas)

if __name__ == "__main__":
    sys.exit(main())
