"""
📊 Módulo Analisadores - LotoScope
Contém todos os analisadores e sistemas de análise

Analisadores principais:
- analisador_hibrido_v3: Sistema recomendado (lógica adaptativa)
- analisador_metadados_preditivos: Análise de campos de apoio
- analisador_academico_limpo: 6 metodologias científicas
- analisador_transicao_posicional: Matrizes de transição
"""

try:
    from .analisador_hibrido_v3 import *
except ImportError:
    pass

try:
    from .analisador_metadados_preditivos import *
except ImportError:
    pass

try:
    from .analisador_academico_limpo import *
except ImportError:
    pass

__all__ = [
    'analisador_hibrido_v3',
    'analisador_metadados_preditivos',
    'analisador_academico_limpo'
]
