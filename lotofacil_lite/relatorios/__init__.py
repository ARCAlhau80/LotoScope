"""
📈 Módulo Relatórios - LotoScope
Contém geradores de relatórios e resumos

Relatórios principais:
- relatorio_tendencias_preditivas: Tendências para próximo concurso
- relatorio_status_sistemas_ia: Status de todos os sistemas IA
- relatorio_completo: Relatório completo do sistema
"""

try:
    from .relatorio_tendencias_preditivas import *
except ImportError:
    pass

try:
    from .relatorio_status_sistemas_ia import *
except ImportError:
    pass

__all__ = [
    'relatorio_tendencias_preditivas',
    'relatorio_status_sistemas_ia'
]
