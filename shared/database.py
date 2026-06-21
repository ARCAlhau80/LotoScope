import pyodbc
import time
from typing import List, Optional, Any

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
    "Connection Timeout=15;"
    "Query Timeout=30;"
    "MARS_Connection=yes;"
    "APP=LotoScope;"
    "Pooling=yes;"
)


class DatabaseOptimizer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection_pool = {}
            cls._instance.query_cache = {}
            cls._instance.cache_ttl = 300
        return cls._instance

    def create_optimized_connection(self) -> Optional[pyodbc.Connection]:
        try:
            conn = pyodbc.connect(CONNECTION_STRING)
            conn.autocommit = True
            return conn
        except Exception as e:
            print(f"Erro na conexão: {e}")
            return None

    def cached_query(self, query: str, params: tuple = None) -> List:
        cache_key = hash(query + str(params) if params else query)
        now = time.time()
        if cache_key in self.query_cache:
            result, timestamp = self.query_cache[cache_key]
            if now - timestamp < self.cache_ttl:
                return result
        conn = self.create_optimized_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            self.query_cache[cache_key] = (result, now)
            return result
        except Exception as e:
            print(f"Erro na query: {e}")
            if conn:
                conn.close()
            return []


_optimizer = DatabaseOptimizer()


def get_optimized_connection():
    return _optimizer.create_optimized_connection()


def cached_query(query: str, params: tuple = None):
    return _optimizer.cached_query(query, params)
