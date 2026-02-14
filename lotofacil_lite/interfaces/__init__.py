"""
🖥️ Módulo Interfaces - LotoScope
Contém menus, GUIs e interfaces do sistema

Interfaces principais:
- super_menu: Menu principal unificado (16 sistemas)
- menu_lotofacil: Menu simplificado
- interface_sistema_v4: Interface escalonada
- seletor_combinacoes_gui: GUI para seleção
"""

try:
    from .super_menu import SuperMenuLotofacil
except ImportError:
    pass

try:
    from .menu_lotofacil import *
except ImportError:
    pass

__all__ = [
    'SuperMenuLotofacil'
]
