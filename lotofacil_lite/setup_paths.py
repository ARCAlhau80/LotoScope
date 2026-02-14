#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 CONFIGURAÇÃO DE PATHS - LOTOSCOPE v2.0
==========================================
Módulo utilitário para configurar os caminhos do sistema reorganizado.
Importe este módulo no início de qualquer script para garantir que
os imports funcionem corretamente.

USO:
    import setup_paths  # Adiciona automaticamente as pastas ao sys.path
    
    # Agora pode importar de qualquer pasta
    from database_config import db_config
    from gerador_academico_dinamico import GeradorAcademicoDinamico
    # etc.
"""

import os
import sys
from pathlib import Path

def configurar_paths():
    """Configura todos os paths necessários para o LotoScope"""
    
    # Detecta o diretório base (lotofacil_lite)
    current_file = Path(__file__).resolve()
    
    # Se estiver na raiz de lotofacil_lite
    if current_file.parent.name == 'lotofacil_lite':
        base_dir = current_file.parent
    # Se estiver em uma subpasta
    elif current_file.parent.parent.name == 'lotofacil_lite':
        base_dir = current_file.parent.parent
    else:
        # Busca lotofacil_lite no path
        for parent in current_file.parents:
            if parent.name == 'lotofacil_lite':
                base_dir = parent
                break
        else:
            base_dir = current_file.parent
    
    # Lista de pastas a adicionar ao path
    pastas = [
        base_dir,
        base_dir / 'core',
        base_dir / 'geradores',
        base_dir / 'analisadores',
        base_dir / 'ia',
        base_dir / 'sistemas',
        base_dir / 'utils',
        base_dir / 'interfaces',
        base_dir / 'validadores',
        base_dir / 'relatorios',
    ]
    
    # Adiciona ao sys.path se ainda não estiver
    for pasta in pastas:
        pasta_str = str(pasta)
        if pasta_str not in sys.path:
            sys.path.insert(0, pasta_str)
    
    return base_dir

# Configura automaticamente ao importar
BASE_DIR = configurar_paths()

# Função auxiliar para obter caminho de script
def get_script_path(filename: str) -> str:
    """
    Retorna o caminho completo de um script, buscando nas pastas do projeto.
    
    Args:
        filename: Nome do arquivo (ex: 'gerador_academico_dinamico.py')
    
    Returns:
        Caminho completo do arquivo ou o nome original se não encontrado
    """
    pastas_busca = [
        'geradores', 'analisadores', 'ia', 'sistemas', 
        'utils', 'interfaces', 'validadores', 'relatorios', 
        'core', '_archive', ''  # '' = raiz
    ]
    
    for pasta in pastas_busca:
        if pasta:
            path = BASE_DIR / pasta / filename
        else:
            path = BASE_DIR / filename
        
        if path.exists():
            return str(path)
    
    return filename

# Mapeamento de arquivos para suas localizações (cache)
_FILE_CACHE = {}

def localizar_arquivo(filename: str) -> str:
    """Localiza um arquivo no projeto com cache"""
    if filename in _FILE_CACHE:
        return _FILE_CACHE[filename]
    
    path = get_script_path(filename)
    _FILE_CACHE[filename] = path
    return path


if __name__ == "__main__":
    print("🔧 CONFIGURAÇÃO DE PATHS - LOTOSCOPE v2.0")
    print("=" * 50)
    print(f"📁 Diretório base: {BASE_DIR}")
    print(f"📋 Pastas no path: {len([p for p in sys.path if str(BASE_DIR) in p])}")
    print()
    print("✅ Paths configurados com sucesso!")
