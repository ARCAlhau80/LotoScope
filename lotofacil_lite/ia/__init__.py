"""
🧠 Módulo IA - LotoScope
Contém sistemas de inteligência artificial e machine learning

Sistemas principais:
- ia_numeros_repetidos: Rede neural 24.384 neurônios
- sistema_auto_treino: Auto-treino contínuo 24/7
- modelo_preditivo_avancado: Modelo ML avançado
- lotoscope_ai_assistant: Assistente IA local
"""

try:
    from .ia_numeros_repetidos import IANumerosRepetidos
except ImportError:
    pass

try:
    from .sistema_auto_treino import *
except ImportError:
    pass

try:
    from .lotoscope_ai_assistant import LotoScopeAIAssistant
except ImportError:
    pass

__all__ = [
    'IANumerosRepetidos',
    'LotoScopeAIAssistant'
]
