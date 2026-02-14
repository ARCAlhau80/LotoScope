"""
🎯 LotoScope - Sistema Científico para Análise da Lotofácil
============================================================

Sistema integrado com IA de 24.384 neurônios para análise e geração
de combinações otimizadas para a Lotofácil.

ESTRUTURA DE MÓDULOS:
- core/         - Classes base e interfaces
- geradores/    - Geradores de combinações (54 arquivos)
- analisadores/ - Sistemas de análise (55 arquivos)  
- ia/           - Inteligência artificial e ML (25 arquivos)
- sistemas/     - Sistemas integrados (39 arquivos)
- interfaces/   - Menus e GUIs (16 arquivos)
- utils/        - Utilitários e configs (36 arquivos)
- validadores/  - Validadores (21 arquivos)
- relatorios/   - Geradores de relatórios (11 arquivos)

USO RÁPIDO:
    from lotofacil_lite.interfaces import SuperMenuLotofacil
    menu = SuperMenuLotofacil()
    menu.executar()

Autor: AR CALHAU
Versão: 2.0 (Reorganizado)
Data: Dezembro 2025
"""

import sys
import os

# =================================================================
# CONFIGURAÇÃO AUTOMÁTICA DE PATHS
# Isso permite que arquivos em subpastas importem módulos de outras
# subpastas sem precisar configurar paths manualmente em cada arquivo
# =================================================================

_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_PACKAGE_DIR)  # LotoScope/

# Adiciona todas as subpastas ao path do Python
_SUBFOLDERS = ['utils', 'geradores', 'analisadores', 'ia', 'sistemas', 
               'interfaces', 'validadores', 'relatorios', 'core', '_archive']

for _folder in _SUBFOLDERS:
    _folder_path = os.path.join(_PACKAGE_DIR, _folder)
    if os.path.isdir(_folder_path) and _folder_path not in sys.path:
        sys.path.insert(0, _folder_path)

# Adiciona o próprio diretório lotofacil_lite
if _PACKAGE_DIR not in sys.path:
    sys.path.insert(0, _PACKAGE_DIR)

# Adiciona o diretório raiz LotoScope (para scripts legados)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

# =================================================================

__version__ = "2.0.0"
__author__ = "AR CALHAU"

# Imports principais
try:
    from .core import Combinacao, GeradorBase, AnalisadorBase, ValidadorBase
except ImportError:
    pass

try:
    from .interfaces import SuperMenuLotofacil
except ImportError:
    pass

try:
    from .utils import DatabaseConfig, db_config
except ImportError:
    pass

__all__ = [
    # Core
    'Combinacao',
    'GeradorBase',
    'AnalisadorBase', 
    'ValidadorBase',
    # Interfaces
    'SuperMenuLotofacil',
    # Utils
    'DatabaseConfig',
    'db_config',
    # Versão
    '__version__',
    '__author__'
]
