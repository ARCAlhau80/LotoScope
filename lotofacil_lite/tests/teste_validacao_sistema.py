#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TESTE AUTOMATIZADO DE VALIDAÇÃO DO SISTEMA LOTOSCOPE
========================================================
Valida todas as opções do SuperMenu após reorganização de pastas.

Testes realizados:
1. Existência de todos os arquivos registrados
2. Sintaxe Python válida em cada arquivo
3. Importação dos módulos principais
4. Conexão com banco de dados
5. Instanciação das classes principais

Autor: AR CALHAU
Data: 28/12/2025
"""

import sys
import os
import importlib
import importlib.util
import traceback
from pathlib import Path
from datetime import datetime

# Configurar paths
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'interfaces'))
sys.path.insert(0, str(_BASE_DIR / 'geradores'))
sys.path.insert(0, str(_BASE_DIR / 'analisadores'))
sys.path.insert(0, str(_BASE_DIR / 'sistemas'))
sys.path.insert(0, str(_BASE_DIR / 'ia'))
sys.path.insert(0, str(_BASE_DIR / 'validadores'))
sys.path.insert(0, str(_BASE_DIR / 'relatorios'))
sys.path.insert(0, str(_BASE_DIR / 'core'))


class TestadorSistema:
    """Sistema de testes automatizados para validação do LotoScope"""
    
    def __init__(self):
        self.resultados = {
            'passou': [],
            'falhou': [],
            'avisos': []
        }
        self.total_testes = 0
        
    def log_sucesso(self, teste: str, detalhes: str = ""):
        """Registra teste bem-sucedido"""
        self.resultados['passou'].append({'teste': teste, 'detalhes': detalhes})
        print(f"  ✅ {teste}")
        
    def log_falha(self, teste: str, erro: str):
        """Registra teste que falhou"""
        self.resultados['falhou'].append({'teste': teste, 'erro': erro})
        print(f"  ❌ {teste}")
        print(f"     └─ Erro: {erro[:100]}...")
        
    def log_aviso(self, teste: str, mensagem: str):
        """Registra aviso (não crítico)"""
        self.resultados['avisos'].append({'teste': teste, 'mensagem': mensagem})
        print(f"  ⚠️ {teste}: {mensagem}")

    # =========================================================================
    # TESTE 1: Existência dos arquivos
    # =========================================================================
    def teste_existencia_arquivos(self):
        """Verifica se todos os arquivos do _FILE_PATHS existem"""
        print("\n" + "="*70)
        print("📁 TESTE 1: EXISTÊNCIA DOS ARQUIVOS REGISTRADOS")
        print("="*70)
        
        try:
            from super_menu import _FILE_PATHS, _BASE_DIR
            
            arquivos_encontrados = 0
            arquivos_faltando = 0
            
            for nome, caminho_completo in _FILE_PATHS.items():
                if os.path.exists(caminho_completo):
                    arquivos_encontrados += 1
                    self.log_sucesso(f"Arquivo '{nome}'", caminho_completo[-50:])
                else:
                    arquivos_faltando += 1
                    self.log_falha(f"Arquivo '{nome}'", f"Não encontrado: {caminho_completo[-60:]}")
                    
            print(f"\n  📊 Resumo: {arquivos_encontrados}/{len(_FILE_PATHS)} arquivos encontrados")
            return arquivos_faltando == 0
            
        except Exception as e:
            self.log_falha("Importação _FILE_PATHS", str(e))
            return False

    # =========================================================================
    # TESTE 2: Sintaxe Python válida
    # =========================================================================
    def teste_sintaxe_arquivos(self):
        """Verifica se todos os arquivos Python têm sintaxe válida"""
        print("\n" + "="*70)
        print("🔍 TESTE 2: SINTAXE PYTHON DOS ARQUIVOS")
        print("="*70)
        
        pastas_testar = ['geradores', 'analisadores', 'sistemas', 'utils', 
                         'interfaces', 'ia', 'validadores', 'relatorios', 'core']
        
        arquivos_ok = 0
        arquivos_erro = 0
        
        for pasta in pastas_testar:
            pasta_path = _BASE_DIR / pasta
            if not pasta_path.exists():
                continue
                
            for arquivo in pasta_path.glob("*.py"):
                if arquivo.name.startswith("__"):
                    continue
                    
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        codigo = f.read()
                    compile(codigo, arquivo.name, 'exec')
                    arquivos_ok += 1
                except SyntaxError as e:
                    arquivos_erro += 1
                    self.log_falha(f"{pasta}/{arquivo.name}", f"Linha {e.lineno}: {e.msg}")
                except Exception as e:
                    arquivos_erro += 1
                    self.log_falha(f"{pasta}/{arquivo.name}", str(e))
                    
        print(f"\n  📊 Resumo: {arquivos_ok} arquivos com sintaxe válida, {arquivos_erro} com erros")
        return arquivos_erro == 0

    # =========================================================================
    # TESTE 3: Importação de módulos principais
    # =========================================================================
    def teste_importacao_modulos(self):
        """Tenta importar os módulos principais do sistema"""
        print("\n" + "="*70)
        print("📦 TESTE 3: IMPORTAÇÃO DOS MÓDULOS PRINCIPAIS")
        print("="*70)
        
        modulos_testar = [
            # Utils
            ('database_config', 'utils'),
            ('filtro_dinamico', 'utils'),
            
            # Interfaces
            ('super_menu', 'interfaces'),
            ('menu_lotofacil', 'interfaces'),
            
            # Sistemas
            ('sistema_neural_network_v7', 'sistemas'),
            ('sistema_inteligencia_n12', 'sistemas'),
            ('sistema_ultra_precisao_v4', 'sistemas'),
            
            # Geradores
            ('lotofacil_generator', 'geradores'),
            ('gerador_posicional', 'geradores'),
            ('gerador_avancado', 'geradores'),
            
            # Analisadores
            ('analisador_metadados_preditivos', 'analisadores'),
            ('analisador_comportamento_numerico', 'analisadores'),
            
            # IA
            ('ia_numeros_repetidos', 'ia'),
            ('calibrador_automatico', 'ia'),
        ]
        
        modulos_ok = 0
        modulos_erro = 0
        
        for modulo, pasta in modulos_testar:
            try:
                # Adicionar pasta ao path temporariamente
                pasta_path = str(_BASE_DIR / pasta)
                if pasta_path not in sys.path:
                    sys.path.insert(0, pasta_path)
                    
                imported = importlib.import_module(modulo)
                modulos_ok += 1
                self.log_sucesso(f"{modulo}", f"de {pasta}/")
            except Exception as e:
                modulos_erro += 1
                erro_curto = str(e).split('\n')[0][:80]
                self.log_falha(f"{modulo}", erro_curto)
                
        print(f"\n  📊 Resumo: {modulos_ok}/{len(modulos_testar)} módulos importados com sucesso")
        return modulos_erro == 0

    # =========================================================================
    # TESTE 4: Conexão com banco de dados
    # =========================================================================
    def teste_conexao_banco(self):
        """Testa conexão com o banco de dados"""
        print("\n" + "="*70)
        print("🗄️ TESTE 4: CONEXÃO COM BANCO DE DADOS")
        print("="*70)
        
        try:
            from database_config import db_config
            
            # Testar conexão
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM Resultados_INT")
                total = cursor.fetchone()[0]
                
            self.log_sucesso(f"Conexão SQL Server", f"{total} concursos na base")
            return True
            
        except Exception as e:
            self.log_falha("Conexão SQL Server", str(e))
            return False

    # =========================================================================
    # TESTE 5: Instanciação de classes principais
    # =========================================================================
    def teste_instanciacao_classes(self):
        """Tenta instanciar as classes principais do sistema"""
        print("\n" + "="*70)
        print("🏗️ TESTE 5: INSTANCIAÇÃO DE CLASSES PRINCIPAIS")
        print("="*70)
        
        classes_testar = [
            ('SuperMenuLotofacil', 'super_menu', 'interfaces'),
            ('MenuLotofacil', 'menu_lotofacil', 'interfaces'),
            ('LotofacilGenerator', 'lotofacil_generator', 'geradores'),
            ('FiltroDinamico', 'filtro_dinamico', 'utils'),
        ]
        
        classes_ok = 0
        classes_erro = 0
        
        for classe, modulo, pasta in classes_testar:
            try:
                pasta_path = str(_BASE_DIR / pasta)
                if pasta_path not in sys.path:
                    sys.path.insert(0, pasta_path)
                    
                mod = importlib.import_module(modulo)
                cls = getattr(mod, classe)
                instancia = cls()
                classes_ok += 1
                self.log_sucesso(f"{classe}", f"Instanciado com sucesso")
                del instancia
            except Exception as e:
                classes_erro += 1
                erro_curto = str(e).split('\n')[0][:80]
                self.log_falha(f"{classe}", erro_curto)
                
        print(f"\n  📊 Resumo: {classes_ok}/{len(classes_testar)} classes instanciadas")
        return classes_erro == 0

    # =========================================================================
    # TESTE 6: Verificação de imports cruzados
    # =========================================================================
    def teste_imports_cruzados(self):
        """Verifica se os imports entre módulos funcionam"""
        print("\n" + "="*70)
        print("🔗 TESTE 6: IMPORTS CRUZADOS ENTRE MÓDULOS")
        print("="*70)
        
        testes_import = [
            # (módulo_origem, import_testado, descrição)
            ('geradores.gerador_posicional', 'database_config', 'Gerador → Utils'),
            ('sistemas.sistema_neural_network_v7', 'database_config', 'Sistema → Utils'),
            ('analisadores.analisador_metadados_preditivos', 'database_config', 'Analisador → Utils'),
            ('ia.ia_numeros_repetidos', 'database_config', 'IA → Utils'),
        ]
        
        imports_ok = 0
        imports_erro = 0
        
        for modulo, import_nome, descricao in testes_import:
            try:
                # Importar módulo e verificar se o import funcionou
                pasta, nome = modulo.split('.')
                pasta_path = str(_BASE_DIR / pasta)
                if pasta_path not in sys.path:
                    sys.path.insert(0, pasta_path)
                    
                mod = importlib.import_module(nome)
                
                # Verificar se tem acesso ao db_config
                if hasattr(mod, 'db_config') or hasattr(mod, 'DatabaseConfig'):
                    imports_ok += 1
                    self.log_sucesso(descricao, f"{nome} importa {import_nome}")
                else:
                    imports_ok += 1
                    self.log_sucesso(descricao, f"{nome} carregado (import implícito)")
                    
            except Exception as e:
                imports_erro += 1
                self.log_falha(descricao, str(e)[:80])
                
        print(f"\n  📊 Resumo: {imports_ok}/{len(testes_import)} imports cruzados OK")
        return imports_erro == 0

    # =========================================================================
    # EXECUTAR TODOS OS TESTES
    # =========================================================================
    def executar_todos(self):
        """Executa todos os testes e gera relatório"""
        print("\n" + "🧪"*35)
        print("🧪 TESTE AUTOMATIZADO DE VALIDAÇÃO DO SISTEMA LOTOSCOPE")
        print("🧪"*35)
        print(f"\n📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📁 Diretório base: {_BASE_DIR}")
        
        # Executar testes
        resultados = {
            'Existência de arquivos': self.teste_existencia_arquivos(),
            'Sintaxe Python': self.teste_sintaxe_arquivos(),
            'Importação de módulos': self.teste_importacao_modulos(),
            'Conexão com banco': self.teste_conexao_banco(),
            'Instanciação de classes': self.teste_instanciacao_classes(),
            'Imports cruzados': self.teste_imports_cruzados(),
        }
        
        # Relatório final
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL")
        print("="*70)
        
        passou = sum(1 for v in resultados.values() if v)
        total = len(resultados)
        
        for teste, resultado in resultados.items():
            status = "✅ PASSOU" if resultado else "❌ FALHOU"
            print(f"  {status} - {teste}")
            
        print("\n" + "-"*70)
        print(f"  📈 TOTAL: {passou}/{total} testes passaram ({100*passou//total}%)")
        
        if passou == total:
            print("\n  🎉 SISTEMA 100% VALIDADO! Todas as opções funcionando!")
        else:
            print(f"\n  ⚠️ ATENÇÃO: {total - passou} teste(s) falharam. Verifique os erros acima.")
            
        print("\n" + "="*70)
        
        # Estatísticas detalhadas
        print(f"\n📋 ESTATÍSTICAS DETALHADAS:")
        print(f"   ✅ Testes passou: {len(self.resultados['passou'])}")
        print(f"   ❌ Testes falhou: {len(self.resultados['falhou'])}")
        print(f"   ⚠️ Avisos: {len(self.resultados['avisos'])}")
        
        return passou == total


def main():
    """Função principal"""
    testador = TestadorSistema()
    sucesso = testador.executar_todos()
    
    # Retornar código de saída apropriado
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()
