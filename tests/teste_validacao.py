#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 TESTE DE VALIDAÇÃO DO SISTEMA LOTOSCOPE
Valida a saúde do sistema após reorganização de pastas
"""

import sys
import os
import ast
import importlib.util
from pathlib import Path
from datetime import datetime

# Configurar path
ROOT_DIR = Path(__file__).parent.parent
LOTOFACIL_DIR = ROOT_DIR / 'lotofacil_lite'

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR / 'utils'))

class TestadorSistema:
    """Classe para testar a saúde do sistema"""
    
    def __init__(self):
        self.resultados = {
            'passou': [],
            'falhou': [],
            'avisos': []
        }
    
    def log_passou(self, msg):
        self.resultados['passou'].append(msg)
        print(f"✅ {msg}")
    
    def log_falhou(self, msg):
        self.resultados['falhou'].append(msg)
        print(f"❌ {msg}")
    
    def log_aviso(self, msg):
        self.resultados['avisos'].append(msg)
        print(f"⚠️ {msg}")
    
    # =========================================================================
    # TESTE 1: Verificar existência de arquivos essenciais do super_menu
    # =========================================================================
    def teste_arquivos_essenciais(self):
        """Verifica se os arquivos essenciais existem"""
        print("\n" + "=" * 60)
        print("📁 TESTE 1: ARQUIVOS ESSENCIAIS")
        print("=" * 60)
        
        arquivos_essenciais = {
            'ia/ia_numeros_repetidos.py': 'IA Números Repetidos',
            'ia/modelo_preditivo_avancado.py': 'Modelo Preditivo',
            'ia/agente_completo.py': 'Agente Completo',
            'geradores/super_gerador_ia.py': 'Super Gerador IA',
            'geradores/piramide_invertida_dinamica.py': 'Pirâmide Invertida',
            'geradores/gerador_academico_dinamico.py': 'Gerador Acadêmico',
            'sistemas/sistema_ultra_precisao_v4.py': 'Sistema Ultra Precisão',
            'sistemas/sistema_neural_network_v7.py': 'Sistema Neural v7',
            'analisadores/analisador_hibrido_v3.py': 'Analisador Híbrido',
            'interfaces/super_menu.py': 'Super Menu Principal',
            'utils/database_config.py': 'Config Database',
        }
        
        existentes = 0
        for arquivo_rel, nome in arquivos_essenciais.items():
            caminho = LOTOFACIL_DIR / arquivo_rel
            if caminho.exists():
                self.log_passou(f"{nome} existe")
                existentes += 1
            else:
                self.log_falhou(f"{nome} NÃO EXISTE: {arquivo_rel}")
        
        print(f"\n   📊 Arquivos: {existentes}/{len(arquivos_essenciais)}")
        return existentes == len(arquivos_essenciais)
    
    # =========================================================================
    # TESTE 2: Verificar sintaxe de arquivos Python
    # =========================================================================
    def teste_sintaxe_arquivos(self):
        """Verifica sintaxe Python de todos os arquivos"""
        print("\n" + "=" * 60)
        print("🔧 TESTE 2: SINTAXE PYTHON")
        print("=" * 60)
        
        pastas = ['geradores', 'analisadores', 'sistemas', 'utils', 'ia', 
                  'validadores', 'interfaces', 'relatorios', 'core']
        
        total = 0
        validos = 0
        erros_detalhes = []
        
        for pasta in pastas:
            pasta_path = LOTOFACIL_DIR / pasta
            if not pasta_path.exists():
                continue
            
            for arquivo in pasta_path.glob('*.py'):
                total += 1
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    # Remover BOM se presente
                    if conteudo.startswith('\ufeff'):
                        conteudo = conteudo[1:]
                    ast.parse(conteudo)
                    validos += 1
                except SyntaxError as e:
                    nome_rel = arquivo.relative_to(LOTOFACIL_DIR)
                    erros_detalhes.append((nome_rel, str(e)[:50]))
                except Exception as e:
                    nome_rel = arquivo.relative_to(LOTOFACIL_DIR)
                    erros_detalhes.append((nome_rel, f"Erro: {str(e)[:40]}"))
        
        print(f"\n   📊 Sintaxe válida: {validos}/{total} arquivos")
        
        if erros_detalhes:
            print(f"\n   ⚠️ {len(erros_detalhes)} arquivos com erros de sintaxe:")
            for nome, erro in erros_detalhes[:10]:
                print(f"      - {nome}: {erro}")
            if len(erros_detalhes) > 10:
                print(f"      ... e mais {len(erros_detalhes) - 10} arquivos")
        
        return len(erros_detalhes) == 0
    
    # =========================================================================
    # TESTE 3: Verificar conexão com banco de dados
    # =========================================================================
    def teste_banco_dados(self):
        """Verifica conexão com banco de dados"""
        print("\n" + "=" * 60)
        print("🗄️ TESTE 3: CONEXÃO BANCO DE DADOS")
        print("=" * 60)
        
        try:
            from database_config import db_config
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM RESULTADOS_INT")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            self.log_passou(f"Conexão OK - {count} concursos no banco")
            return True
        except Exception as e:
            self.log_falhou(f"Erro de conexão: {str(e)[:50]}")
            return False
    
    # =========================================================================
    # TESTE 4: Instanciar classe SuperMenuLotofacil
    # =========================================================================
    def teste_super_menu(self):
        """Testa se o SuperMenuLotofacil pode ser instanciado"""
        print("\n" + "=" * 60)
        print("🎯 TESTE 4: SUPER MENU LOTOFACIL")
        print("=" * 60)
        
        try:
            # Adicionar path para interfaces
            sys.path.insert(0, str(LOTOFACIL_DIR / 'interfaces'))
            from super_menu import SuperMenuLotofacil
            
            # Tentar instanciar (pode falhar se depender de outros arquivos)
            menu = SuperMenuLotofacil()
            self.log_passou("SuperMenuLotofacil instanciado com sucesso")
            return True
        except ImportError as e:
            self.log_falhou(f"Erro de import: {str(e)[:60]}")
            return False
        except Exception as e:
            self.log_falhou(f"Erro ao instanciar: {str(e)[:60]}")
            return False
    
    # =========================================================================
    # TESTE 5: Verificar imports principais
    # =========================================================================
    def teste_imports_principais(self):
        """Testa imports dos módulos principais"""
        print("\n" + "=" * 60)
        print("📦 TESTE 5: IMPORTS PRINCIPAIS")
        print("=" * 60)
        
        modulos = {
            'database_config': 'Database Config',
            'menu_lotofacil': 'Menu Lotofacil',
            'filtro_dinamico': 'Filtro Dinâmico',
            'super_gerador_ia': 'Super Gerador IA',
        }
        
        importados = 0
        for modulo, nome in modulos.items():
            try:
                importlib.import_module(modulo)
                self.log_passou(f"{nome} importado")
                importados += 1
            except ImportError as e:
                self.log_falhou(f"{nome}: {str(e)[:40]}")
            except Exception as e:
                self.log_falhou(f"{nome}: {str(e)[:40]}")
        
        print(f"\n   📊 Imports: {importados}/{len(modulos)}")
        return importados == len(modulos)
    
    # =========================================================================
    # EXECUTAR TODOS OS TESTES
    # =========================================================================
    def executar_todos(self):
        """Executa todos os testes"""
        print("\n" + "=" * 70)
        print("🧪 TESTE DE VALIDAÇÃO DO SISTEMA LOTOSCOPE")
        print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        resultados = {
            'Arquivos Essenciais': self.teste_arquivos_essenciais(),
            'Sintaxe Python': self.teste_sintaxe_arquivos(),
            'Banco de Dados': self.teste_banco_dados(),
            'Super Menu': self.teste_super_menu(),
            'Imports Principais': self.teste_imports_principais(),
        }
        
        # Resumo
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS TESTES")
        print("=" * 70)
        
        passou = sum(1 for r in resultados.values() if r)
        total = len(resultados)
        
        for nome, resultado in resultados.items():
            status = "✅ PASSOU" if resultado else "❌ FALHOU"
            print(f"   {status} - {nome}")
        
        print("\n" + "-" * 70)
        porcentagem = (passou / total) * 100
        print(f"   RESULTADO FINAL: {passou}/{total} testes ({porcentagem:.0f}%)")
        
        if porcentagem == 100:
            print("   🎉 SISTEMA 100% FUNCIONAL!")
        elif porcentagem >= 60:
            print("   ⚠️ Sistema parcialmente funcional")
        else:
            print("   ❌ Sistema precisa de correções")
        
        print("=" * 70)
        return passou == total

def main():
    testador = TestadorSistema()
    sucesso = testador.executar_todos()
    return 0 if sucesso else 1

if __name__ == "__main__":
    sys.exit(main())
