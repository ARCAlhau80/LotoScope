#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 CRIADOR DE STORED PROCEDURES DE COMPARAÇÃO
============================================
Executa o script SQL para criar as SPs SP_AtualizarCamposComparacao 
e SP_AtualizarCombinacoesComparacao no banco de dados.
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


def executar_script_sql():
    """Executa o script SQL para criar as stored procedures"""
    print("🔧 CRIANDO STORED PROCEDURES DE COMPARAÇÃO")
    print("=" * 50)
    
    # Lê o arquivo SQL
    script_path = os.path.join(os.path.dirname(__file__), 'criar_sps_comparacao.sql')
    
    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            
        print(f"📄 Script SQL carregado: {script_path}")
        print(f"📏 Tamanho: {len(sql_script)} caracteres")
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {script_path}")
        return False
    except Exception as e:
        print(f"❌ Erro ao ler arquivo SQL: {e}")
        return False
    
    # Testa conexão
    print("\n🔍 Testando conexão com banco de dados...")
    if not db_config.test_connection():
        print("❌ Erro na conexão com banco de dados")
        return False
    
    print("✅ Conexão OK")
    
    # Executa o script SQL
    print("\n🚀 Executando script SQL...")
    
    try:
        import pyodbc
        # Conexão otimizada para performance
        if _db_optimizer:
            conn = _db_optimizer.create_optimized_connection()
        else:
            conn = pyodbc.connect(db_config.get_connection_string())
        cursor = conn.cursor()
        
        # Divide o script em comandos individuais (separados por 'GO')
        comandos = sql_script.split('GO')
        
        total_comandos = len([cmd for cmd in comandos if cmd.strip()])
        print(f"📊 Total de comandos a executar: {total_comandos}")
        
        comandos_executados = 0
        
        for i, comando in enumerate(comandos):
            comando = comando.strip()
            if comando:
                try:
                    print(f"⏳ Executando comando {i+1}/{total_comandos}...")
                    cursor.execute(comando)
                    conn.commit()
                    comandos_executados += 1
                    print(f"✅ Comando {i+1} executado com sucesso")
                except Exception as e:
                    print(f"⚠️ Aviso no comando {i+1}: {e}")
                    # Continua com próximo comando
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 SCRIPT EXECUTADO COM SUCESSO!")
        print(f"📊 Comandos executados: {comandos_executados}/{total_comandos}")
        print("\n✅ STORED PROCEDURES CRIADAS:")
        print("   • SP_AtualizarCamposComparacao")
        print("   • SP_AtualizarCombinacoesComparacao")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar script SQL: {e}")
        return False

def verificar_sps_criadas():
    """Verifica se as SPs foram criadas corretamente"""
    print("\n🔍 VERIFICANDO SPs CRIADAS...")
    
    try:
        import pyodbc
        # Conexão otimizada para performance
        if _db_optimizer:
            conn = _db_optimizer.create_optimized_connection()
        else:
            conn = pyodbc.connect(db_config.get_connection_string())
        cursor = conn.cursor()
        
        # Verifica SP_AtualizarCamposComparacao
        cursor.execute("""
            SELECT COUNT_BIG(*) FROM sys.objects 
            WHERE type = 'P' AND name = 'SP_AtualizarCamposComparacao'
        """)
        sp1_existe = cursor.fetchone()[0] > 0
        
        # Verifica SP_AtualizarCombinacoesComparacao
        cursor.execute("""
            SELECT COUNT_BIG(*) FROM sys.objects 
            WHERE type = 'P' AND name = 'SP_AtualizarCombinacoesComparacao'
        """)
        sp2_existe = cursor.fetchone()[0] > 0
        
        cursor.close()
        conn.close()
        
        print("📋 RESULTADO DA VERIFICAÇÃO:")
        print(f"   • SP_AtualizarCamposComparacao: {'✅ EXISTE' if sp1_existe else '❌ NÃO EXISTE'}")
        print(f"   • SP_AtualizarCombinacoesComparacao: {'✅ EXISTE' if sp2_existe else '❌ NÃO EXISTE'}")
        
        return sp1_existe and sp2_existe
        
    except Exception as e:
        print(f"❌ Erro ao verificar SPs: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 SISTEMA DE CRIAÇÃO DE STORED PROCEDURES")
    print("=" * 60)
    print("Este script cria as SPs necessárias para os campos de comparação")
    print("baseadas na lógica posição-por-posição validada.")
    print()
    
    # Executa o script
    if executar_script_sql():
        # Verifica se foram criadas
        if verificar_sps_criadas():
            print("\n🎉 SUCESSO COMPLETO!")
            print("As stored procedures estão prontas para uso.")
        else:
            print("\n⚠️ SPs podem não ter sido criadas corretamente.")
    else:
        print("\n❌ FALHA na criação das SPs.")
    
    print("\n" + "=" * 60)
    input("Pressione ENTER para continuar...")

if __name__ == "__main__":
    main()