#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CORRETOR DE ESTRUTURA TRY/EXCEPT
Corrige automaticamente blocos try/except mal formados nos arquivos Python
"""

import os
import re
from pathlib import Path

# Diretório base
BASE_DIR = Path(__file__).parent.parent

# Padrão problemático e sua correção
PATTERN_PROBLEMA = r'''try:\s*\n(\s*)from (database_config) import ([^\n]+)\n\n# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO\ntry:\n    from database_optimizer import DatabaseOptimizer\n    _db_optimizer = DatabaseOptimizer\(\)\nexcept ImportError:\n    _db_optimizer = None\n\n(\s*)(.+)\nexcept ImportError'''

PATTERN_CORRECAO = '''# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
\\1from \\2 import \\3
\\4\\5
except ImportError'''


def corrigir_arquivo(filepath):
    """Corrige um arquivo se tiver o padrão problemático"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar se tem o padrão problemático
        if 'try:\n    from database_config import' in conteudo and '# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO\ntry:' in conteudo:
            # Correção manual mais confiável
            novo_conteudo = conteudo
            
            # Padrão 1: try sem except seguido de outro try
            novo_conteudo = re.sub(
                r'try:\n(\s*)from (database_config) import (db_config|DatabaseConfig)\n\n# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO\ntry:\n    from database_optimizer import DatabaseOptimizer\n    _db_optimizer = DatabaseOptimizer\(\)\nexcept ImportError:\n    _db_optimizer = None\n\n(\s*)(.+)\nexcept ImportError(.*?):',
                r'''# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
\1from \2 import \3
\4\5
except ImportError\6:''',
                novo_conteudo
            )
            
            if novo_conteudo != conteudo:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(novo_conteudo)
                return True
        return False
    except Exception as e:
        print(f"  ❌ Erro em {filepath}: {e}")
        return False


def main():
    """Processa todos os arquivos Python"""
    print("🔧 CORRETOR DE ESTRUTURA TRY/EXCEPT")
    print("="*60)
    
    pastas = ['geradores', 'analisadores', 'sistemas', 'utils', 'ia', 'validadores', 'interfaces', 'relatorios']
    
    arquivos_corrigidos = 0
    
    for pasta in pastas:
        pasta_path = BASE_DIR / pasta
        if not pasta_path.exists():
            continue
            
        for arquivo in pasta_path.glob("*.py"):
            if corrigir_arquivo(arquivo):
                print(f"  ✅ Corrigido: {pasta}/{arquivo.name}")
                arquivos_corrigidos += 1
                
    print(f"\n📊 Total: {arquivos_corrigidos} arquivos corrigidos")


if __name__ == "__main__":
    main()
