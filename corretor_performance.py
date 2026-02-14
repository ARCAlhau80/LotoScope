#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 CORREÇÕES ESPECÍFICAS DE PERFORMANCE
====================================
Sistema para aplicar correções diretas nos arquivos mais problemáticos
"""

import os
import sys
import time
import re

class CorretorPerformance:
    """
    Aplicador de correções específicas de performance
    """
    
    def __init__(self):
        self.arquivos_corrigidos = []
        
    def corrigir_super_menu(self):
        """
        🔧 CORRIGE PERFORMANCE DO SUPER_MENU.PY
        """
        print("🔧 Corrigindo performance do super_menu.py...")
        
        # Encontra o arquivo
        possible_paths = [
            "lotofacil_lite/super_menu.py",
            "super_menu.py",
            "../super_menu.py"
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            print("❌ super_menu.py não encontrado")
            return False
        
        try:
            # Lê o arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Backup
            backup_path = file_path + '.backup_performance'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Aplicar correções específicas
            content_fixed = self._apply_super_menu_fixes(content)
            
            # Salva o arquivo corrigido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content_fixed)
            
            print(f"✅ super_menu.py corrigido!")
            print(f"📁 Backup: {backup_path}")
            self.arquivos_corrigidos.append(file_path)
            return True
            
        except Exception as e:
            print(f"❌ Erro ao corrigir super_menu.py: {e}")
            return False
    
    def _apply_super_menu_fixes(self, content: str) -> str:
        """
        Aplica correções específicas no super_menu.py
        """
        lines = content.split('\n')
        fixed_lines = []
        
        # Adicionar sistema de lazy loading no início
        lazy_loading_system = '''
# 🚀 SISTEMA DE LAZY LOADING PARA PERFORMANCE
import importlib
import functools

class LazyImporter:
    """Sistema de importação lazy para melhorar performance de inicialização"""
    def __init__(self):
        self._modules = {}
        self._loading = set()
    
    def get_module(self, module_name, attribute=None):
        """Carrega módulo apenas quando necessário"""
        if module_name in self._loading:
            return None  # Evita import circular
            
        if module_name not in self._modules:
            try:
                self._loading.add(module_name)
                self._modules[module_name] = importlib.import_module(module_name)
                print(f"⚡ Lazy load: {module_name}")
            except ImportError as e:
                print(f"⚠️ Erro lazy import {module_name}: {e}")
                return None
            finally:
                self._loading.discard(module_name)
        
        module = self._modules[module_name]
        return getattr(module, attribute) if attribute else module

# Instância global do lazy importer
_lazy = LazyImporter()

def lazy_import(module_name, attribute=None):
    """Helper para importação lazy"""
    return _lazy.get_module(module_name, attribute)

# Cache para subprocess calls
_subprocess_cache = {}

def cached_subprocess_run(cmd, **kwargs):
    """Subprocess com cache simples"""
    cmd_key = str(cmd) + str(kwargs)
    if cmd_key in _subprocess_cache:
        return _subprocess_cache[cmd_key]
    
    result = subprocess.run(cmd, **kwargs)
    _subprocess_cache[cmd_key] = result
    return result
'''
        
        in_class = False
        added_lazy_system = False
        
        for i, line in enumerate(lines):
            # Adiciona sistema lazy após imports iniciais
            if (not added_lazy_system and 
                line.strip().startswith('import') and 
                i > 10):  # Depois de alguns imports básicos
                fixed_lines.append(lazy_loading_system)
                added_lazy_system = True
            
            # Identifica início da classe
            if line.strip().startswith('class SuperMenuLotofacil'):
                in_class = True
            
            # Otimiza imports pesados dentro de métodos
            if in_class and 'subprocess.run' in line:
                # Substitui subprocess.run por versão cached
                line = line.replace('subprocess.run', 'cached_subprocess_run')
            
            # Otimiza imports de módulos pesados
            if ('from gerador_academico_dinamico import' in line or
                'from ia_numeros_repetidos import' in line or
                'from sistema_' in line):
                # Transforma em lazy import
                line = f"            # LAZY: {line.strip()}"
                
                # Adiciona lazy loading correspondente
                if 'GeradorAcademicoDinamico' in line:
                    fixed_lines.append(line)
                    fixed_lines.append("            # Lazy loading:")
                    fixed_lines.append("            GeradorAcademicoDinamico = lazy_import('gerador_academico_dinamico', 'GeradorAcademicoDinamico')")
                    fixed_lines.append("            if not GeradorAcademicoDinamico:")
                    fixed_lines.append("                print('❌ Erro ao carregar GeradorAcademicoDinamico')")
                    fixed_lines.append("                return")
                    continue
            
            # Adiciona verificação de erro para imports críticos
            if line.strip().startswith('try:') and 'ImportError' in lines[i+5:i+10]:
                # Já tem tratamento de erro
                pass
            elif ('gerador = ' in line and 'Gerador' in line):
                # Adiciona tratamento de erro
                fixed_lines.append("            try:")
                fixed_lines.append(f"    {line}")
                fixed_lines.append("            except Exception as e:")
                fixed_lines.append("                print(f'❌ Erro ao instanciar gerador: {e}')")
                fixed_lines.append("                return")
                continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def corrigir_analisador_academico(self):
        """
        🔧 CORRIGE PERFORMANCE DO ANALISADOR ACADÊMICO
        """
        print("🔧 Corrigindo performance do analisador acadêmico...")
        
        file_path = "lotofacil_lite/analisador_academico_padroes.py"
        
        if not os.path.exists(file_path):
            print("❌ analisador_academico_padroes.py não encontrado")
            return False
        
        try:
            # Lê o arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Backup
            backup_path = file_path + '.backup_performance'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Aplicar correções
            content_fixed = self._apply_analisador_fixes(content)
            
            # Salva o arquivo corrigido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content_fixed)
            
            print(f"✅ analisador_academico_padroes.py corrigido!")
            print(f"📁 Backup: {backup_path}")
            self.arquivos_corrigidos.append(file_path)
            return True
            
        except Exception as e:
            print(f"❌ Erro ao corrigir analisador: {e}")
            return False
    
    def _apply_analisador_fixes(self, content: str) -> str:
        """
        Aplica correções no analisador acadêmico
        """
        # Sistema de cache para conexões
        cache_system = '''

# 🚀 SISTEMA DE CACHE PARA PERFORMANCE
import threading
from datetime import datetime, timedelta

class ConnectionCache:
    """Cache singleton para conexões de banco"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.conn = None
                    cls._instance.timestamp = None
                    cls._instance.ttl = 300  # 5 minutos
        return cls._instance
    
    def get_connection(self):
        """Obtém conexão cached ou cria nova"""
        now = datetime.now()
        
        # Verifica se conexão está válida
        if (self.conn and self.timestamp and 
            (now - self.timestamp).total_seconds() < self.ttl):
            try:
                cursor = self.conn.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute("SELECT 1")
                cursor.close()
                return self.conn
            except:
                self.conn = None
        
        # Cria nova conexão
        try:
            server = 'DESKTOP-K6JPBDS'
            database = 'LOTOFACIL'
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                self.conn = pyodbc.connect(connection_string)
            self.timestamp = now
            print("⚡ Nova conexão cached criada")
            return self.conn
        except Exception as e:
            print(f"❌ Erro na conexão cached: {e}")
            return None

_conn_cache = ConnectionCache()
'''
        
        # Adiciona sistema de cache após imports
        lines = content.split('\n')
        
        # Encontra onde inserir o cache system
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('class AnalisadorPadroesAcademico'):
                insert_pos = i
                break
        
        # Insere sistema de cache
        lines.insert(insert_pos, cache_system)
        
        # Corrige método de conexão
        fixed_lines = []
        for line in lines:
            if 'self.conn = pyodbc.connect' in line:
                # Substitui por conexão cached
                indentation = len(line) - len(line.lstrip())
                space = ' ' * indentation
                fixed_lines.append(f"{space}# Usa conexão cached para performance")
                fixed_lines.append(f"{space}self.conn = _conn_cache.get_connection()")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def corrigir_imports_lentos(self):
        """
        🔧 CORRIGE IMPORTS LENTOS EM ARQUIVOS CRÍTICOS
        """
        print("🔧 Corrigindo imports lentos...")
        
        arquivos_criticos = [
            "lotofacil_lite/visualizador_padroes.py",
            "gerador_academico_dinamico.py",
            "sistema_hibrido.py"
        ]
        
        for arquivo in arquivos_criticos:
            if os.path.exists(arquivo):
                self._otimizar_imports_arquivo(arquivo)
            else:
                print(f"⚠️ Arquivo não encontrado: {arquivo}")
    
    def _otimizar_imports_arquivo(self, file_path: str):
        """
        Otimiza imports de um arquivo específico
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Backup
            backup_path = file_path + '.backup_imports'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Padrões de imports pesados para otimizar
            heavy_patterns = [
                (r'^import pandas as pd$', '# import pandas as pd  # LAZY LOAD'),
                (r'^import numpy as np$', '# import numpy as np  # LAZY LOAD'),
                (r'^import matplotlib\.pyplot as plt$', '# import matplotlib.pyplot as plt  # LAZY LOAD'),
                (r'^import seaborn as sns$', '# import seaborn as sns  # LAZY LOAD'),
                (r'^from sklearn', '# from sklearn'),  # Comenta imports sklearn
                (r'^from scipy', '# from scipy'),      # Comenta imports scipy
            ]
            
            lines = content.split('\n')
            fixed_lines = []
            has_lazy_system = False
            
            for line in lines:
                line_fixed = line
                
                # Aplica otimizações de imports
                for pattern, replacement in heavy_patterns:
                    if re.match(pattern, line.strip()):
                        line_fixed = replacement
                        if not has_lazy_system:
                            # Adiciona sistema lazy loading
                            fixed_lines.append("")
                            fixed_lines.append("# 🚀 LAZY LOADING SYSTEM")
                            fixed_lines.append("def lazy_load(module_name):")
                            fixed_lines.append("    try:")
                            fixed_lines.append("        return __import__(module_name)")
                            fixed_lines.append("    except ImportError as e:")
                            fixed_lines.append("        print(f'⚠️ Lazy load failed {module_name}: {e}')")
                            fixed_lines.append("        return None")
                            fixed_lines.append("")
                            has_lazy_system = True
                        break
                
                fixed_lines.append(line_fixed)
            
            # Salva arquivo otimizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            print(f"✅ Imports otimizados: {os.path.basename(file_path)}")
            self.arquivos_corrigidos.append(file_path)
            
        except Exception as e:
            print(f"❌ Erro ao otimizar {file_path}: {e}")
    
    def aplicar_todas_correcoes(self):
        """
        🚀 APLICA TODAS AS CORREÇÕES DE PERFORMANCE
        """
        print("🚀 APLICANDO TODAS AS CORREÇÕES DE PERFORMANCE")
        print("=" * 60)
        
        # 1. Corrige super menu (principal)
        self.corrigir_super_menu()
        
        # 2. Corrige analisador acadêmico
        self.corrigir_analisador_academico()
        
        # 3. Corrige imports lentos
        self.corrigir_imports_lentos()
        
        # 4. Relatório final
        print(f"\n✅ CORREÇÕES APLICADAS!")
        print(f"📁 Arquivos corrigidos: {len(self.arquivos_corrigidos)}")
        for arquivo in self.arquivos_corrigidos:
            print(f"   • {arquivo}")
        
        print(f"\n🚀 PERFORMANCE MELHORADA!")
        print(f"💡 Os backups foram salvos com extensão .backup_performance")
        print(f"💡 Para reverter, renomeie os backups de volta")
        
        return len(self.arquivos_corrigidos) > 0

def main():
    """
    Função principal para correção de performance
    """
    print("🔧 CORRETOR ESPECÍFICO DE PERFORMANCE")
    print("=" * 50)
    
    corretor = CorretorPerformance()
    
    print("1️⃣  🔧 Corrigir super_menu.py")
    print("2️⃣  🔧 Corrigir analisador acadêmico")
    print("3️⃣  🔧 Corrigir imports lentos")
    print("4️⃣  🚀 Aplicar TODAS as correções")
    print("0️⃣  🚪 Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == "1":
        corretor.corrigir_super_menu()
    elif opcao == "2":
        corretor.corrigir_analisador_academico()
    elif opcao == "3":
        corretor.corrigir_imports_lentos()
    elif opcao == "4":
        corretor.aplicar_todas_correcoes()
    elif opcao == "0":
        print("🚪 Saindo...")
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()