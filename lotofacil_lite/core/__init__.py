"""
🎯 Módulo Core - LotoScope
Contém classes base e interfaces fundamentais

Este módulo define as abstrações principais que outros módulos implementam.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Combinacao:
    """Representa uma combinação de números da Lotofácil"""
    numeros: List[int]
    score: float = 0.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        # Garantir ordenação
        self.numeros = sorted(self.numeros)
    
    def __str__(self):
        return f"[{', '.join(map(str, self.numeros))}] (score: {self.score:.2f})"
    
    def validar(self) -> bool:
        """Valida se a combinação é válida para Lotofácil"""
        if len(self.numeros) != 15:
            return False
        if not all(1 <= n <= 25 for n in self.numeros):
            return False
        if len(set(self.numeros)) != 15:
            return False
        return True


class GeradorBase(ABC):
    """Interface base para todos os geradores"""
    
    @abstractmethod
    def gerar(self, quantidade: int = 1, **kwargs) -> List[Combinacao]:
        """Gera combinações"""
        pass
    
    @abstractmethod
    def nome(self) -> str:
        """Nome do gerador"""
        pass


class AnalisadorBase(ABC):
    """Interface base para todos os analisadores"""
    
    @abstractmethod
    def analisar(self, dados: any) -> Dict:
        """Executa análise e retorna resultados"""
        pass
    
    @abstractmethod
    def nome(self) -> str:
        """Nome do analisador"""
        pass


class ValidadorBase(ABC):
    """Interface base para validadores"""
    
    @abstractmethod
    def validar(self, combinacao: Combinacao, resultado: List[int]) -> Tuple[bool, int]:
        """
        Valida combinação contra resultado
        Returns: (passou, quantidade_acertos)
        """
        pass


__all__ = [
    'Combinacao',
    'GeradorBase', 
    'AnalisadorBase',
    'ValidadorBase'
]
