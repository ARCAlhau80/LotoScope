"""
Configurações compartilhadas do LotoScope Web
"""
import os
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados"""
    server: str = "DESKTOP-K6JPBDS"
    database: str = "LOTOFACIL"
    trusted_connection: bool = True
    
    def get_connection_string(self) -> str:
        """Retorna string de conexão"""
        if self.trusted_connection:
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;"
        else:
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};"

@dataclass
class WebConfig:
    """Configurações da aplicação web"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True
    secret_key: str = "lotoscope-web-2025"
    max_combinations: int = 10000
    max_fixed_numbers: int = 14

@dataclass
class GameConfig:
    """Configurações do jogo"""
    min_game_size: int = 15
    max_game_size: int = 20
    total_numbers: int = 25
    
    # Filtros padrão para a procedure
    default_filters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.default_filters is None:
            self.default_filters = {
                'qtde_primos': (2, 3, 4, 5, 6, 7, 8),
                'qtde_fibonacci': (2, 3, 4, 5, 6),
                'qtde_impares': (6, 7, 8, 9, 10),
                'qtde_repetidos': (7, 8, 9, 10),
                'quintil1': (1, 2, 3, 4, 5),
                'quintil2': (1, 2, 3, 4, 5),
                'quintil3': (1, 2, 3, 4, 5),
                'quintil4': (1, 2, 3, 4, 5),
                'quintil5': (1, 2, 3, 4, 5),
                'seq': (6, 7, 8, 9, 10, 11, 12, 13, 14),
                'qtde_multiplos3': (3, 4, 5, 6),
                'distancia_extremos': (19, 20, 21, 22, 23, 24),
                'menor_que_ultimo': (11, 12, 13, 14),
                'maior_que_ultimo': (1, 2, 3, 4),
                'igual_ao_ultimo': (0, 1, 2, 3, 4),
                'repetidos_mesma_posicao': (0, 1, 2, 3, 4),
                'soma_total_min': 180,
                'soma_total_max': 219
            }

# Instâncias globais
db_config = DatabaseConfig()
web_config = WebConfig()
game_config = GameConfig()

def get_position_ranges():
    """
    Retorna os ranges posicionais padrão baseados na análise de tendências
    """
    return {
        'n1': (1, 2),
        'n2': (2, 3),
        'n3': (3, 4, 5),
        'n4': (5, 6, 7),
        'n5': (6, 7, 8),
        'n6': (8, 9, 10),
        'n7': (10, 11, 12),
        'n8': (11, 12, 13, 14),
        'n9': (14, 15, 16),
        'n10': (15, 16, 17),
        'n11': (17, 18, 19),
        'n12': (19, 20, 21),
        'n13': (20, 21, 22),
        'n14': (22, 23, 24),
        'n15': (23, 24, 25)
    }