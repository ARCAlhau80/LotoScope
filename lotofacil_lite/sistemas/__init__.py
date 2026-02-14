"""
⚙️ Módulo Sistemas - LotoScope
Contém os sistemas integrados principais

Sistemas principais:
- sistema_hibrido_v3: Lógica adaptativa (RECOMENDADO)
- sistema_neural_network_v7: TensorFlow + Ensemble
- sistema_escalonado_v4: Filtro + Neural + Ranking
- sistema_ultra_precisao_v4: Alta precisão configurável
"""

try:
    from .sistema_neural_network_v7 import *
except ImportError:
    pass

try:
    from .sistema_ultra_precisao_v4 import *
except ImportError:
    pass

try:
    from .sistema_validador_universal import *
except ImportError:
    pass

__all__ = [
    'sistema_neural_network_v7',
    'sistema_ultra_precisao_v4',
    'sistema_validador_universal'
]
