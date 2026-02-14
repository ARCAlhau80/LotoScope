"""
🔧 Módulo Utils - LotoScope
Contém utilitários, configurações e helpers

Utilitários principais:
- database_config: Configuração centralizada do banco
- filtro_dinamico: Filtros inteligentes
- adaptador_geradores: Adaptadores para geradores
"""

try:
    from .database_config import DatabaseConfig, db_config
except ImportError:
    pass

try:
    from .filtro_dinamico import *
except ImportError:
    pass

__all__ = [
    'DatabaseConfig',
    'db_config'
]
