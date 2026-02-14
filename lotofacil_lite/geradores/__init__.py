"""
🎲 Módulo Geradores - LotoScope
Contém todos os geradores de combinações da Lotofácil

Geradores principais:
- gerador_academico_dinamico: Insights em tempo real
- gerador_zona_conforto: 80% zona 1-17
- super_gerador_ia: Sistema integrado completo
- piramide_invertida_dinamica: Análise de faixas com IA
- gerador_complementacao_inteligente: Desdobramento C(5,3)
"""

# Imports principais
try:
    from .gerador_academico_dinamico import *
except ImportError:
    pass

try:
    from .gerador_zona_conforto import *
except ImportError:
    pass

try:
    from .super_gerador_ia import *
except ImportError:
    pass

try:
    from .piramide_invertida_dinamica import *
except ImportError:
    pass

try:
    from .gerador_complementacao_inteligente import *
except ImportError:
    pass

__all__ = [
    'gerador_academico_dinamico',
    'gerador_zona_conforto', 
    'super_gerador_ia',
    'piramide_invertida_dinamica',
    'gerador_complementacao_inteligente'
]
