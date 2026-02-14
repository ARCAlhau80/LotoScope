#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ MÓDULO DE OTIMIZAÇÃO DE BANCO - LOTOSCOPE
Módulo para ser importado pelos arquivos que fazem acesso ao banco
"""

import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import time
from typing import List, Dict, Any, Optional

class DatabaseOptimizer:
    """Otimizador singleton para operações de banco"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection_pool = {}
            cls._instance.query_cache = {}
            cls._instance.cache_ttl = 300
        return cls._instance
    
    def create_optimized_connection(self) -> Optional[pyodbc.Connection]:
        """Cria conexão otimizada com configurações de performance"""
        try:
            server = 'DESKTOP-K6JPBDS'
            database = 'LOTOFACIL'
            
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
                "Connection Timeout=15;"
                "Query Timeout=30;"
                "MARS_Connection=yes;"
                "APP=LotoScope_Optimized;"
                "Pooling=yes;"
            )
            
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                conn = pyodbc.connect(connection_string)
            conn.autocommit = True
            return conn
            
        except Exception as e:
            print(f"❌ Erro na conexão otimizada: {e}")
            return None
    
    def cached_query(self, query: str, params: tuple = None) -> List:
        """Executa query com cache"""
        cache_key = hash(query + str(params) if params else query)
        now = time.time()
        
        # Verifica cache
        if cache_key in self.query_cache:
            result, timestamp = self.query_cache[cache_key]
            if now - timestamp < self.cache_ttl:
                return result
        
        # Executa query
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
            
            # Armazena no cache
            self.query_cache[cache_key] = (result, now)
            return result
            
        except Exception as e:
            print(f"❌ Erro na query cached: {e}")
            if conn:
                conn.close()
            return []

# Instância global
_optimizer = DatabaseOptimizer()

def get_optimized_connection():
    """Helper para obter conexão otimizada"""
    return _optimizer.create_optimized_connection()

def cached_query(query: str, params: tuple = None):
    """Helper para query com cache"""
    return _optimizer.cached_query(query, params)
