"""
🗄️ Database Service para LotoScope Web
Integração com banco de dados usando sistema existente do lotofacil_lite
"""
import sys
import os
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import json
from typing import List, Dict, Any, Optional, Tuple

# Adicionar path do sistema existente
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lotofacil_lite'))

try:
    from database_config import DatabaseConfig
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class LotoScopeWebDatabase:
    """Classe para gerenciar conexões e consultas do banco de dados"""
    
    def __init__(self):
        self.db_config = None
        self.connection = None
        self.is_connected = False
        
        if DB_AVAILABLE:
            try:
                self.db_config = DatabaseConfig()
                self.test_connection()
            except Exception as e:
                print(f"⚠️ Erro ao inicializar banco: {e}")
    
    def test_connection(self) -> bool:
        """Testa conexão com banco de dados"""
        try:
            if not DB_AVAILABLE:
                return False
                
            with self.db_config.get_connection() as conn:
                cursor = conn.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute("SELECT 1")
                cursor.fetchone()
                self.is_connected = True
                print("✅ Conexão com banco estabelecida")
                return True
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            self.is_connected = False
            return False
    
    def get_connection(self):
        """Retorna conexão ativa com o banco"""
        if not self.is_connected or not DB_AVAILABLE:
            raise Exception("Banco de dados não disponível")
        return self.db_config.get_connection()
    
    def calculate_total_combinations(self, fixed_numbers: List[int], game_size: int) -> int:
        """
        Calcula total de combinações possíveis baseado nos números fixos
        """
        try:
            if not self.is_connected:
                return self._calculate_combinations_fallback(fixed_numbers, game_size)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Query para contar combinações baseada nos critérios
                where_clauses = []
                params = []
                
                # Adicionar filtros para números fixos se houver
                if fixed_numbers:
                    fixed_str = ','.join(map(str, fixed_numbers))
                    where_clauses.append("""
                        (CASE WHEN N1 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N2 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N3 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N4 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N5 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N6 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N7 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N8 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N9 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N10 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N11 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N12 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N13 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N14 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N15 IN ({}) THEN 1 ELSE 0 END) >= ?
                    """.format(*([fixed_str] * 15)))
                    params.append(len(fixed_numbers))
                
                # Adicionar filtros baseados no esquema real da tabela
                where_clauses.extend([
                    "QtdePrimos BETWEEN 2 AND 8",
                    "QtdeFibonacci BETWEEN 2 AND 6", 
                    "QtdeImpares BETWEEN 6 AND 10",
                    "SomaTotal BETWEEN 180 AND 219"
                ])
                
                where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
                
                query = f"""
                    SELECT COUNT_BIG(*) as TotalCombinacoes
                    FROM [dbo].[COMBINACOES_LOTOFACIL20_COMPLETO] 
                    WHERE {where_sql}
                """
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                total = result[0] if result else 0
                
                print(f"🔢 Total de combinações encontradas: {total:,}")
                return max(total, 1)  # Garantir pelo menos 1
                
        except Exception as e:
            print(f"❌ Erro no cálculo: {e}")
            return self._calculate_combinations_fallback(fixed_numbers, game_size)
    
    def generate_combinations_from_db(self, fixed_numbers: List[int], game_size: int, quantity: int) -> List[List[int]]:
        """
        Gera combinações reais do banco de dados baseadas na procedure existente
        """
        try:
            if not self.is_connected:
                return self._generate_combinations_fallback(fixed_numbers, game_size, quantity)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Construir query baseada na procedure original
                where_clauses = []
                params = []
                
                # Números fixos obrigatórios
                if fixed_numbers:
                    fixed_str = ','.join(map(str, fixed_numbers))
                    where_clauses.append("""
                        (CASE WHEN N1 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N2 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N3 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N4 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N5 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N6 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N7 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N8 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N9 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N10 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N11 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N12 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N13 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N14 IN ({}) THEN 1 ELSE 0 END +
                         CASE WHEN N15 IN ({}) THEN 1 ELSE 0 END) >= ?
                    """.format(*([fixed_str] * 15)))
                    params.append(len(fixed_numbers))
                
                # Filtros otimizados baseados no esquema real da tabela
                where_clauses.extend([
                    "QtdePrimos BETWEEN 2 AND 8",
                    "QtdeFibonacci BETWEEN 2 AND 6",
                    "QtdeImpares BETWEEN 6 AND 10",
                    "QtdeConsecutivos BETWEEN 0 AND 5",
                    "SomaTotal BETWEEN 180 AND 219",
                    "MaiorGap BETWEEN 1 AND 8",
                    "MenorGap BETWEEN 1 AND 4"
                ])
                
                # Aplicar ranges posicionais da análise de tendências
                position_ranges = self._get_position_ranges()
                for pos, numbers in position_ranges.items():
                    if numbers:
                        numbers_str = ','.join(map(str, numbers))
                        where_clauses.append(f"{pos} IN ({numbers_str})")
                
                where_sql = " AND ".join(where_clauses)
                
                # Query principal
                query = f"""
                    SELECT TOP {quantity}
                        N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                    FROM [dbo].[COMBINACOES_LOTOFACIL20_COMPLETO] 
                    WHERE {where_sql}
                    ORDER BY CRYPT_GEN_RANDOM(4)
                """
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                combinations = []
                for row in rows:
                    # Converter para lista de 15 números (ajustar se game_size diferente)
                    combo = list(row[:15])  # Pegar apenas os primeiros 15
                    
                    # Se o jogo for maior que 15, adicionar números extras inteligentemente
                    if game_size > 15:
                        combo = self._extend_combination(combo, fixed_numbers, game_size)
                    
                    combinations.append(sorted(combo))
                
                print(f"✅ {len(combinations)} combinações geradas do banco")
                return combinations
                
        except Exception as e:
            print(f"❌ Erro na geração: {e}")
            return self._generate_combinations_fallback(fixed_numbers, game_size, quantity)
    
    def _get_position_ranges(self) -> Dict[str, List[int]]:
        """Retorna ranges posicionais baseados na análise de tendências"""
        return {
            'n1': [1, 2],
            'n2': [2, 3],
            'n3': [3, 4, 5],
            'n4': [5, 6, 7],
            'n5': [6, 7, 8],
            'n6': [8, 9, 10],
            'n7': [10, 11, 12],
            'n8': [11, 12, 13, 14],
            'n9': [14, 15, 16],
            'n10': [15, 16, 17],
            'n11': [17, 18, 19],
            'n12': [19, 20, 21],
            'n13': [20, 21, 22],
            'n14': [22, 23, 24],
            'n15': [23, 24, 25]
        }
    
    def _extend_combination(self, base_combo: List[int], fixed_numbers: List[int], target_size: int) -> List[int]:
        """Estende combinação de 15 para mais números de forma inteligente"""
        if len(base_combo) >= target_size:
            return base_combo[:target_size]
        
        # Números disponíveis que não estão na combinação
        available = [n for n in range(1, 26) if n not in base_combo]
        needed = target_size - len(base_combo)
        
        # Selecionar números extras de forma inteligente
        import random
        extra_numbers = random.sample(available, min(needed, len(available)))
        
        return base_combo + extra_numbers
    
    def _calculate_combinations_fallback(self, fixed_numbers: List[int], game_size: int) -> int:
        """Cálculo fallback quando banco não disponível"""
        base_combinations = 3268760  # C(25,15)
        if len(fixed_numbers) > 0:
            reduction_factor = 0.75 ** len(fixed_numbers)
            return max(int(base_combinations * reduction_factor), 1)
        return base_combinations
    
    def _generate_combinations_fallback(self, fixed_numbers: List[int], game_size: int, quantity: int) -> List[List[int]]:
        """Geração fallback quando banco não disponível"""
        import random
        combinations = []
        available_numbers = [n for n in range(1, 26) if n not in fixed_numbers]
        
        for _ in range(quantity):
            combo = fixed_numbers.copy()
            needed = game_size - len(fixed_numbers)
            extra = random.sample(available_numbers, min(needed, len(available_numbers)))
            combo.extend(extra)
            combinations.append(sorted(combo))
        
        return combinations
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        try:
            if not self.is_connected:
                return self._get_stats_fallback()
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Estatísticas gerais
                stats = {}
                
                # Total de combinações por tamanho
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute("SELECT COUNT(*) FROM [dbo].[COMBINACOES_LOTOFACIL20_COMPLETO]")
                stats['total_combinations'] = cursor.fetchone()[0]
                
                # Números mais frequentes
                cursor.execute("""
                    SELECT TOP 10 Numero, Frequencia 
                    FROM (
                        SELECT 1 as Numero, COUNT(*) as Frequencia FROM [dbo].[COMBINACOES_LOTOFACIL20_COMPLETO] WHERE N1=1 OR N2=1 OR N3=1 OR N4=1 OR N5=1 OR N6=1 OR N7=1 OR N8=1 OR N9=1 OR N10=1 OR N11=1 OR N12=1 OR N13=1 OR N14=1 OR N15=1 UNION ALL
                        SELECT 2, COUNT(*) FROM [dbo].[COMBINACOES_LOTOFACIL20_COMPLETO] WHERE N1=2 OR N2=2 OR N3=2 OR N4=2 OR N5=2 OR N6=2 OR N7=2 OR N8=2 OR N9=2 OR N10=2 OR N11=2 OR N12=2 OR N13=2 OR N14=2 OR N15=2 UNION ALL
                        SELECT 3, COUNT(*) FROM [dbo].[COMBINACOES_LOTOFACIL20_COMPLETO] WHERE N1=3 OR N2=3 OR N3=3 OR N4=3 OR N5=3 OR N6=3 OR N7=3 OR N8=3 OR N9=3 OR N10=3 OR N11=3 OR N12=3 OR N13=3 OR N14=3 OR N15=3
                    ) freq 
                    ORDER BY Frequencia DESC
                """)
                
                most_frequent = cursor.fetchall()
                stats['most_frequent_numbers'] = [row[0] for row in most_frequent]
                
                return stats
                
        except Exception as e:
            print(f"❌ Erro nas estatísticas: {e}")
            return self._get_stats_fallback()
    
    def _get_stats_fallback(self) -> Dict[str, Any]:
        """Estatísticas fallback"""
        return {
            'total_combinations': 3268760,
            'most_frequent_numbers': [13, 5, 4, 16, 20, 18, 19, 10, 25, 14],
            'mode': 'fallback'
        }


# Instância global
web_database = LotoScopeWebDatabase()