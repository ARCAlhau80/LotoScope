#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔒 QUARENTENA DE ARQUIVOS CORROMPIDOS
Move arquivos com erros de sintaxe para pasta de quarentena
"""

import sys
import os
import ast
import shutil
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
LOTOFACIL_DIR = ROOT_DIR / 'lotofacil_lite'
QUARENTENA_DIR = LOTOFACIL_DIR / '_quarentena'

def verificar_sintaxe(caminho):
    """Verifica se o arquivo tem erro de sintaxe"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        if conteudo.startswith('\ufeff'):
            conteudo = conteudo[1:]
        ast.parse(conteudo)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def mover_para_quarentena():
    """Move arquivos corrompidos para quarentena"""
    print("=" * 70)
    print("🔒 SISTEMA DE QUARENTENA - LotoScope")
    print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Criar pasta de quarentena
    QUARENTENA_DIR.mkdir(exist_ok=True)
    
    # Criar arquivo de log
    log_path = QUARENTENA_DIR / 'LOG_QUARENTENA.txt'
    log_entries = []
    log_entries.append(f"Quarentena criada em: {datetime.now()}")
    log_entries.append("=" * 60)
    log_entries.append("")
    
    pastas = ['geradores', 'analisadores', 'sistemas', 'utils', 'ia', 
              'validadores', 'interfaces', 'relatorios', 'core']
    
    total_corrompidos = 0
    movidos = 0
    
    print("\n📋 Identificando arquivos corrompidos...\n")
    
    for pasta in pastas:
        pasta_path = LOTOFACIL_DIR / pasta
        if not pasta_path.exists():
            continue
        
        for arquivo in pasta_path.glob('*.py'):
            valido, erro = verificar_sintaxe(arquivo)
            
            if not valido:
                total_corrompidos += 1
                nome_rel = arquivo.relative_to(LOTOFACIL_DIR)
                print(f"  ⚠️ Corrompido: {nome_rel}")
                print(f"     Erro: {erro[:60]}...")
                
                # Criar subpasta na quarentena para manter estrutura
                destino_pasta = QUARENTENA_DIR / pasta
                destino_pasta.mkdir(exist_ok=True)
                
                destino = destino_pasta / arquivo.name
                
                # Mover arquivo
                try:
                    shutil.move(str(arquivo), str(destino))
                    movidos += 1
                    print(f"     ✅ Movido para _quarentena/{pasta}/")
                    
                    log_entries.append(f"Arquivo: {nome_rel}")
                    log_entries.append(f"Erro: {erro}")
                    log_entries.append(f"Movido para: {destino}")
                    log_entries.append("")
                    
                except Exception as e:
                    print(f"     ❌ Erro ao mover: {e}")
    
    # Salvar log
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_entries))
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO")
    print("=" * 70)
    print(f"   Arquivos corrompidos: {total_corrompidos}")
    print(f"   Arquivos movidos: {movidos}")
    print(f"   Log salvo em: _quarentena/LOG_QUARENTENA.txt")
    print("")
    print("   🔄 Os arquivos podem ser corrigidos manualmente e movidos de volta.")
    print("   📁 Estrutura de pastas mantida em _quarentena/")
    print("=" * 70)
    
    return movidos

if __name__ == "__main__":
    mover_para_quarentena()
