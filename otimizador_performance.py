#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 OTIMIZADOR DE PERFORMANCE LOTOSCOPE
=====================================
Sistema completo para identificar e corrigir gargalos de performance
Autor: AR CALHAU
Data: Novembro 2025
"""

import os
import sys
import time
import threading
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta

class PerformanceOptimizer:
    """
    Otimizador de performance para o sistema LotoScope
    """
    
    def __init__(self):
        self.cache = {}
        self.import_cache = {}
        self.conexao_cache = None
        self.conexao_timestamp = None
        self.conexao_ttl = 300  # 5 minutos
        
    def lazy_import(self, module_name: str, package: str = None):
        """
        🚀 LAZY IMPORT - Carrega módulos apenas quando necessário
        """
        cache_key = f"{package}.{module_name}" if package else module_name
        
        if cache_key in self.import_cache:
            return self.import_cache[cache_key]
        
        try:
            if package:
                module = __import__(f"{package}.{module_name}", fromlist=[module_name])
            else:
                module = __import__(module_name)
            
            self.import_cache[cache_key] = module
            print(f"✅ Módulo carregado: {cache_key}")
            return module
            
        except ImportError as e:
            print(f"❌ Erro ao importar {cache_key}: {e}")
            return None
    
    def cached_connection(self):
        """
        💾 CONEXÃO COM CACHE - Reutiliza conexão existente
        """
        now = datetime.now()
        
        # Verifica se a conexão está válida
        if (self.conexao_cache and self.conexao_timestamp and 
            (now - self.conexao_timestamp).total_seconds() < self.conexao_ttl):
            try:
                # Testa se a conexão ainda está ativa
                cursor = self.conexao_cache.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute("SELECT 1")
                cursor.close()
                return self.conexao_cache
            except:
                self.conexao_cache = None
        
        # Cria nova conexão
        try:
            import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

            server = 'DESKTOP-K6JPBDS'
            database = 'LOTOFACIL'
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                self.conexao_cache = pyodbc.connect(connection_string)
            self.conexao_timestamp = now
            print(f"✅ Nova conexão criada e cacheada")
            return self.conexao_cache
            
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return None
    
    def performance_timer(self, func):
        """
        ⏱️ DECORATOR PARA MEDIR PERFORMANCE
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            print(f"⏱️ {func.__name__}: {execution_time:.2f}s")
            
            return result
        return wrapper
    
    def async_executor(self, func: Callable, *args, **kwargs):
        """
        🔄 EXECUTOR ASSÍNCRONO - Para operações pesadas
        """
        def worker():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"❌ Erro na execução assíncrona: {e}")
                return None
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        return thread
    
    def cached_query(self, query: str, cache_duration: int = 300):
        """
        📊 CACHE DE QUERIES SQL
        """
        cache_key = hash(query)
        now = time.time()
        
        # Verifica cache
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if now - timestamp < cache_duration:
                print(f"📊 Query do cache: {len(str(result))} chars")
                return result
        
        # Executa query
        connection = self.cached_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            
            # Armazena no cache
            self.cache[cache_key] = (result, now)
            print(f"📊 Query executada e cacheada: {len(result)} resultados")
            return result
            
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            return None
    
    def optimize_imports_in_file(self, file_path: str):
        """
        🔧 OTIMIZA IMPORTS EM UM ARQUIVO ESPECÍFICO
        """
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        try:
            # Lê o arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Identifica imports pesados
            heavy_imports = [
                'import pandas as pd',
                'import numpy as np', 
                'import scipy',
                'import sklearn',
                'import tensorflow',
                'import torch',
                'import matplotlib',
                'import seaborn'
            ]
            
            optimized_lines = []
            imports_to_optimize = []
            
            for line in lines:
                line_stripped = line.strip()
                
                # Verifica se é um import pesado
                is_heavy = any(heavy in line_stripped for heavy in heavy_imports)
                
                if is_heavy and not line_stripped.startswith('#'):
                    # Comenta o import e adiciona lazy loading
                    optimized_lines.append(f"# OTIMIZADO: {line}")
                    imports_to_optimize.append(line_stripped)
                else:
                    optimized_lines.append(line)
            
            # Adiciona sistema de lazy loading no início
            if imports_to_optimize:
                header = self._generate_lazy_loading_header(imports_to_optimize)
                
                # Encontra onde inserir o header (após docstring inicial)
                insert_pos = 0
                in_docstring = False
                
                for i, line in enumerate(optimized_lines):
                    if '"""' in line or "'''" in line:
                        if not in_docstring:
                            in_docstring = True
                        else:
                            insert_pos = i + 1
                            break
                    elif not in_docstring and line.strip() and not line.startswith('#'):
                        insert_pos = i
                        break
                
                # Insere o header
                optimized_lines.insert(insert_pos, header)
                
                # Salva arquivo otimizado
                backup_path = file_path + '.backup'
                os.rename(file_path, backup_path)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(optimized_lines)
                
                print(f"✅ Arquivo otimizado: {file_path}")
                print(f"📁 Backup salvo: {backup_path}")
                print(f"🚀 Imports otimizados: {len(imports_to_optimize)}")
                return True
            else:
                print(f"ℹ️ Nenhum import pesado encontrado em: {file_path}")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao otimizar {file_path}: {e}")
            return False
    
    def _generate_lazy_loading_header(self, imports: list) -> str:
        """
        Gera header com sistema de lazy loading
        """
        header = "\n# 🚀 SISTEMA DE LAZY LOADING OTIMIZADO\n"
        header += "# Imports pesados carregados apenas quando necessário\n"
        header += "import sys\n"
        header += "import importlib\n\n"
        header += "class LazyLoader:\n"
        header += "    def __init__(self):\n"
        header += "        self._modules = {}\n\n"
        header += "    def get(self, module_name):\n"
        header += "        if module_name not in self._modules:\n"
        header += "            try:\n"
        header += "                self._modules[module_name] = importlib.import_module(module_name)\n"
        header += "                print(f'✅ Lazy load: {module_name}')\n"
        header += "            except ImportError as e:\n"
        header += "                print(f'❌ Erro lazy load {module_name}: {e}')\n"
        header += "                return None\n"
        header += "        return self._modules[module_name]\n\n"
        header += "_lazy = LazyLoader()\n"
        header += "# Exemplo de uso: pd = _lazy.get('pandas')\n\n"
        
        return header
    
    def scan_and_optimize_project(self, project_path: str = None):
        """
        🔍 ESCANEIA E OTIMIZA TODO O PROJETO
        """
        if not project_path:
            project_path = os.getcwd()
        
        print(f"🔍 Escaneando projeto: {project_path}")
        
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Ignora alguns diretórios
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.vscode', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        print(f"📁 Encontrados {len(python_files)} arquivos Python")
        
        # Análise de problemas
        self._analyze_performance_issues(python_files)
        
        # Otimização opcional
        optimize = input("\n🚀 Aplicar otimizações? (s/N): ").lower().strip()
        if optimize == 's':
            self._apply_optimizations(python_files)
    
    def _analyze_performance_issues(self, python_files: list):
        """
        Analisa problemas de performance nos arquivos
        """
        print("\n📊 ANÁLISE DE PROBLEMAS DE PERFORMANCE:")
        print("=" * 50)
        
        total_issues = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = []
                
                # Verifica imports pesados
                heavy_imports = ['pandas', 'numpy', 'scipy', 'sklearn', 'tensorflow', 'torch']
                for imp in heavy_imports:
                    if f'import {imp}' in content or f'from {imp}' in content:
                        issues.append(f"Import pesado: {imp}")
                
                # Verifica subprocess calls
                if 'subprocess.run' in content or 'subprocess.call' in content:
                    issues.append("Uso de subprocess (lento)")
                
                # Verifica múltiplas conexões de banco
                if content.count('pyodbc.connect') > 1:
                    issues.append("Múltiplas conexões de banco")
                
                # Verifica sleeps desnecessários
                if 'time.sleep' in content:
                    issues.append("Uso de time.sleep")
                
                if issues:
                    rel_path = os.path.relpath(file_path)
                    print(f"\n❌ {rel_path}:")
                    for issue in issues:
                        print(f"   • {issue}")
                    total_issues += len(issues)
                    
            except Exception as e:
                print(f"⚠️ Erro ao analisar {file_path}: {e}")
        
        print(f"\n📊 RESUMO: {total_issues} problemas encontrados em {len(python_files)} arquivos")
    
    def _apply_optimizations(self, python_files: list):
        """
        Aplica otimizações nos arquivos
        """
        print("\n🔧 APLICANDO OTIMIZAÇÕES...")
        
        optimized_count = 0
        
        for file_path in python_files:
            # Aplica otimizações específicas
            if self.optimize_imports_in_file(file_path):
                optimized_count += 1
            
            # Pausa pequena para não sobrecarregar
            time.sleep(0.1)
        
        print(f"\n✅ OTIMIZAÇÕES CONCLUÍDAS!")
        print(f"📁 Arquivos otimizados: {optimized_count}")
        print(f"🚀 Sistema deve estar mais rápido agora!")

# CACHE GLOBAL PARA PERFORMANCE
_performance_optimizer = None

def get_optimizer():
    """
    🚀 SINGLETON PARA O OTIMIZADOR
    """
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

def quick_optimize():
    """
    🚀 OTIMIZAÇÃO RÁPIDA DO SISTEMA
    """
    print("🚀 INICIANDO OTIMIZAÇÃO RÁPIDA DO LOTOSCOPE")
    print("=" * 50)
    
    optimizer = get_optimizer()
    
    # Otimiza arquivos críticos
    critical_files = [
        "super_menu.py",
        "analisador_academico_padroes.py", 
        "visualizador_padroes.py",
        "gerador_academico_dinamico.py"
    ]
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for file_name in critical_files:
        # Tenta encontrar o arquivo
        possible_paths = [
            os.path.join(base_path, file_name),
            os.path.join(base_path, "lotofacil_lite", file_name),
            os.path.join(base_path, "..", file_name)
        ]
        
        for file_path in possible_paths:
            if os.path.exists(file_path):
                print(f"🔧 Otimizando: {file_name}")
                optimizer.optimize_imports_in_file(file_path)
                break
        else:
            print(f"⚠️ Arquivo não encontrado: {file_name}")
    
    print("\n✅ OTIMIZAÇÃO RÁPIDA CONCLUÍDA!")
    print("🚀 O sistema deve estar mais responsivo agora!")

if __name__ == "__main__":
    print("🚀 OTIMIZADOR DE PERFORMANCE - LOTOSCOPE")
    print("=" * 50)
    
    print("1️⃣  🚀 Otimização Rápida (arquivos críticos)")
    print("2️⃣  🔍 Análise Completa do Projeto") 
    print("3️⃣  🔧 Otimização Completa do Projeto")
    print("4️⃣  💾 Testar Cache de Conexão")
    print("0️⃣  🚪 Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == "1":
        quick_optimize()
    elif opcao == "2":
        optimizer = get_optimizer()
        optimizer.scan_and_optimize_project()
    elif opcao == "3":
        optimizer = get_optimizer()
        optimizer.scan_and_optimize_project()
        input("\nPressione ENTER para aplicar otimizações...")
        # A aplicação acontece durante o scan
    elif opcao == "4":
        optimizer = get_optimizer()
        conn = optimizer.cached_connection()
        if conn:
            print("✅ Cache de conexão funcionando!")
        else:
            print("❌ Problema no cache de conexão")
    elif opcao == "0":
        print("🚪 Saindo...")
    else:
        print("❌ Opção inválida!")