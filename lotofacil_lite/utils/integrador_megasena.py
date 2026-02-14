#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
INTEGRADOR MEGA-SENA
===================
        print("🎯 OPÇÕE       whi       print("     print("📋 FUNCIONALID    while True:
        print("🎯 OPÇÕES:")
        print("1. 🚀 Executar Gerador Básico Mega-Sena")
        print("2. 🧠 Executar Gerador Dinâmico (AVANÇADO)")
        print("3. 🎯 Acesso Direto - Gerador Dinâmico")
        print("4. 🔗 Testar Conectividade Banco")
        print("5. 📊 Informações do Sistema")
        print("6. 🔧 Verificar Dependências")
        print("0. 🔙 Voltar ao Menu Principal")SPONÍVEIS:")
    print("   🧠 Análise de padrões históricos")
    print("   🤖 Geração com Inteligência Artificial") 
    print("   🔥 Estratégia números quentes")
    print("   ❄️ Estratégia números frios")
    print("   ⚖️ Estratégia equilibrada")
    print("   🔄 Estratégia contrária")
    print("   🔗 Integração com banco de dados")
    print("   💾 Salvamento automático")
    print()
    
    print("💡 ACESSO DIRETO AO GERADOR DINÂMICO:")
    print("   Execute: python gerador_dinamico_direto.py")
    print("   🚀 Geração ILIMITADA + 6-20 números por jogo")
    print()ração com banco de dados")
    print("   �💾 Salvamento automático")
    print()
    
    while True:
        print("🎯 OPÇÕES:")
        print("1. 🚀 Executar Gerador Básico Mega-Sena")
        print("2. 🧠 Executar Gerador Dinâmico (AVANÇADO)")
        print("3. 🔗 Testar Conectividade Banco")
        print("4. 📊 Informações do Sistema")
        print("5. 🔧 Verificar Dependências")
        print("0. 🔙 Voltar ao Menu Principal")
        
        try:
            escolha = input("\n➤ Sua escolha: ").strip()
            
            if escolha == '1':
                if verificar_dependencias():
                    executar_gerador_megasena()
                else:
                    print("❌ Impossível executar - dependências ausentes!")  print("🎯 OPÇÕES:")
        print("1. 🚀 Executar Gerador Básico Mega-Sena")
        print("2. 🧠 Executar Gerador Dinâmico (AVANÇADO)")
        print("3. 🔗 Testar Conectividade Banco")
        print("4. 📊 Informações do Sistema")
        print("5. 🔧 Verificar Dependências")
        print("0. 🔙 Voltar ao Menu Principal"):
        print("🎯 OPÇÕES:")
        print("1. 🚀 Executar Gerador Básico Mega-Sena")
        print("2. 🧠 Executar Gerador Dinâmico (AVANÇADO)")
        print("3. 🔗 Testar Conectividade Banco")
        print("4. 📊 Informações do Sistema")
        print("5. 🔧 Verificar Dependências")
        print("0. 🔙 Voltar ao Menu Principal")int("🎯 OPÇÕES:")
        print("1. 🚀 Executar Gerador Mega-Sena (Básico)")
        print("2. 🧠 Executar Gerador Acadêmico Dinâmico (Avançado)")
        print("3. 🗄️ Testar Conectividade Banco")
        print("4. 📊 Informações do Sistema")
        print("5. 🔧 Verificar Dependências")
        print("0. 🔙 Voltar ao Menu Principal")        print("1. 🚀 Executar Gerador Mega-Sena Básico")
        print("2. 🎯 Gerador Acadêmico Dinâmico (NOVO!)")
        print("3. 🗄️ Testar Conectividade Banco")
        print("4. 📊 Informações do Sistema")
        print("5. 🔧 Verificar Dependências")
        print("0. 🔙 Voltar ao Menu Principal") para integração do Gerador Acadêmico Mega-Sena
ao sistema principal, mantendo total separação dos códigos.
"""

import os
import sys
from datetime import datetime

def verificar_dependencias():
    """Verifica se os arquivos necessários existem"""
    arquivos_necessarios = [
        'gerador_academico_megasena.py',
        'config_megasena.py'
    ]
    
    arquivos_opcionais = [
        'conector_megasena_db.py'
    ]
    
    print("🔍 Verificando dependências...")
    
    # Verifica arquivos essenciais
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - NÃO ENCONTRADO")
            return False
    
    # Verifica arquivos opcionais
    for arquivo in arquivos_opcionais:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo} (integração banco)")
        else:
            print(f"   ⚠️ {arquivo} - OPCIONAL (sem integração banco)")
    
    print("✅ Dependências essenciais encontradas!")
    return True

def executar_gerador_dinamico():
    """Executa o gerador acadêmico dinâmico"""
    try:
        print("🚀 Iniciando Gerador Acadêmico Dinâmico Mega-Sena...")
        print("-" * 55)
        
        from gerador_academico_dinamico_megasena import GeradorAcademicoDinamicoMegaSena
        
        gerador = GeradorAcademicoDinamicoMegaSena()
        gerador.menu_principal()
        
    except ImportError as e:
        print(f"❌ Erro ao importar gerador dinâmico: {e}")
        print("💡 Verifique se o arquivo gerador_academico_dinamico_megasena.py existe")
    except Exception as e:
        print(f"❌ Erro durante execução do gerador dinâmico: {e}")

def executar_gerador_megasena():
    """Executa o gerador da Mega-Sena"""
    try:
        print("🎰 Iniciando Gerador Acadêmico Mega-Sena...")
        print("-" * 50)
        
        # Importa e executa o gerador
        from gerador_academico_megasena import GeradorAcademicoMegaSena
        
        gerador = GeradorAcademicoMegaSena()
        gerador.menu_principal()
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        print("💡 Verifique se todos os arquivos estão no diretório correto")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

def executar_gerador_dinamico():
    """Executa o gerador acadêmico dinâmico"""
    try:
        print("🚀 Iniciando Gerador Acadêmico Dinâmico Mega-Sena...")
        print("-" * 55)
        
        from gerador_academico_dinamico_megasena import GeradorAcademicoDinamicoMegaSena
        
        gerador = GeradorAcademicoDinamicoMegaSena()
        gerador.menu_principal()
        
    except ImportError as e:
        print(f"❌ Erro ao importar gerador dinâmico: {e}")
        print("💡 Verifique se o arquivo gerador_academico_dinamico_megasena.py existe")
    except Exception as e:
        print(f"❌ Erro durante execução do gerador dinâmico: {e}")

def executar_gerador_dinamico_direto():
    """Executa o gerador dinâmico via script direto"""
    try:
        print("🚀 Executando Gerador Dinâmico via Script Direto...")
        print("-" * 55)
        
        import subprocess
        import sys
        
        # Executar o script direto
        resultado = subprocess.run([sys.executable, "gerador_dinamico_direto.py"], 
                                 capture_output=False, 
                                 text=True)
        
        if resultado.returncode == 0:
            print("✅ Gerador dinâmico executado com sucesso!")
        else:
            print("⚠️ Gerador dinâmico encerrado")
            
    except FileNotFoundError:
        print("❌ Arquivo gerador_dinamico_direto.py não encontrado")
        print("💡 Execute diretamente: python gerador_dinamico_direto.py")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Execute diretamente: python gerador_dinamico_direto.py")

def menu_megasena():
    """Menu específico para Mega-Sena"""
    print("\n" + "🎰" * 25)
    print("     GERADOR ACADÊMICO MEGA-SENA")
    print("🎰" * 25)
    print()
    print("📋 FUNCIONALIDADES DISPONÍVEIS:")
    print("   🧠 Análise de padrões históricos")
    print("   🤖 Geração com Inteligência Artificial") 
    print("   🔥 Estratégia números quentes")
    print("   ❄️ Estratégia números frios")
    print("   ⚖️ Estratégia equilibrada")
    print("   🔄 Estratégia contrária")
    print("   �️ Integração com banco de dados")
    print("   �💾 Salvamento automático")
    print()
    
    while True:
        print("🎯 OPÇÕES:")
        print("1. 🚀 Executar Gerador Mega-Sena")
        print("2. �️ Testar Conectividade Banco")
        print("3. �📊 Informações do Sistema")
        print("4. 🔧 Verificar Dependências")
        print("0. 🔙 Voltar ao Menu Principal")
        
        try:
            escolha = input("\n➤ Sua escolha: ").strip()
            
            if escolha == '1':
                if verificar_dependencias():
                    executar_gerador_megasena()
                else:
                    print("❌ Impossível executar - dependências ausentes!")
            
            elif escolha == '2':
                if verificar_dependencias():
                    executar_gerador_dinamico()
                else:
                    print("❌ Impossível executar - dependências ausentes!")
            
            elif escolha == '3':
                executar_gerador_dinamico_direto()
            
            elif escolha == '4':
                testar_conectividade_banco()
            
            elif escolha == '5':
                mostrar_informacoes()
            
            elif escolha == '6':
                verificar_dependencias()
            
            elif escolha == '0':
                print("🔙 Voltando ao menu principal...")
                break
            
            else:
                print("❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n🔙 Voltando...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

def testar_conectividade_banco():
    """Testa a conectividade com o banco de dados"""
    print("\n🔍 TESTANDO CONECTIVIDADE COM BANCO...")
    print("-" * 40)
    
    try:
        from conector_megasena_db import ConectorMegaSena
        
        conector = ConectorMegaSena()
        
        if conector.conectar_banco():
            print("✅ Conexão estabelecida com sucesso!")
            
            # Testa carregamento de dados
            resultados = conector.carregar_resultados()
            if resultados:
                print(f"📊 Total de sorteios: {len(resultados)}")
                print(f"📅 Primeiro sorteio: {min(r['concurso'] for r in resultados)}")
                print(f"📅 Último sorteio: {max(r['concurso'] for r in resultados)}")
            else:
                print("⚠️ Nenhum resultado encontrado")
            
            # Testa tabela de combinações
            stats = conector.obter_estatisticas_combinacoes()
            if stats:
                print(f"💾 Combinações salvas: {stats['total_combinacoes']}")
                print(f"📈 Origens diferentes: {stats['origens_diferentes']}")
            
            conector.fechar_conexao()
            print("🔌 Conexão fechada")
            
        else:
            print("❌ Não foi possível conectar ao banco")
            print("📝 O sistema funcionará com dados simulados")
            
    except ImportError:
        print("❌ Módulo do conector não encontrado")
        print("💡 Certifique-se que conector_megasena_db.py está presente")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        print("📝 O sistema funcionará com dados simulados")

def mostrar_informacoes():
    """Mostra informações sobre o sistema"""
    print("\n📊 INFORMAÇÕES DO SISTEMA:")
    print("-" * 40)
    print("🎰 Nome: Gerador Acadêmico Mega-Sena")
    print("👨‍💻 Baseado em: Gerador Acadêmico Lotofácil")
    print("🧠 Tecnologia: Inteligência Artificial")
    print("📈 Análise: Padrões históricos")
    print()
    print("🎯 ESPECIFICAÇÕES MEGA-SENA:")
    print("   🔢 Números: 1 a 60")
    print("   🎲 Por jogo: 6 números")
    print("   📊 Faixas: Baixa (1-20), Média (21-40), Alta (41-60)")
    print("   🤖 Estratégias: 4 tipos disponíveis")
    print()
    print("🗄️ INTEGRAÇÃO BANCO DE DADOS:")
    print("   📋 Tabela sorteios: Resultados_MegaSenaFechado")
    print("   💾 Tabela combinações: COMBIN_MEGASENA")
    print("   🔌 Conexão: pyodbc (SQL Server)")
    print("   🛡️ Fallback: Dados simulados se banco indisponível")
    print()
    print("⚡ DIFERENCIAIS:")
    print("   ✅ Sistema totalmente separado (não interfere na Lotofácil)")
    print("   ✅ Mesma qualidade do gerador acadêmico aprovado")
    print("   ✅ Adaptado especificamente para Mega-Sena")
    print("   ✅ Análise de padrões em tempo real")
    print("   ✅ Múltiplas estratégias de geração")
    print("   ✅ Integração com banco de dados real")
    print("   ✅ Salvamento automático em arquivo e banco")

def criar_executavel_direto():
    """Cria um .bat para execução direta"""
    conteudo_bat = '''@echo off
echo ==========================================
echo    GERADOR ACADEMICO MEGA-SENA
echo ==========================================
echo.

cd /d "%~dp0"

python integrador_megasena.py

echo.
echo ==========================================
echo    EXECUCAO FINALIZADA
echo ==========================================
pause
'''
    
    try:
        with open('executar_megasena.bat', 'w', encoding='utf-8') as f:
            f.write(conteudo_bat)
        print("✅ Arquivo 'executar_megasena.bat' criado!")
        print("💡 Você pode executar diretamente clicando neste arquivo")
    except Exception as e:
        print(f"❌ Erro ao criar .bat: {e}")

def main():
    """Função principal do integrador"""
    print("🎰 INTEGRADOR MEGA-SENA")
    print("=" * 30)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verifica se está sendo chamado como módulo
    if __name__ == "__main__":
        menu_megasena()
    else:
        # Se importado, apenas retorna função do menu
        return menu_megasena

if __name__ == "__main__":
    main()
