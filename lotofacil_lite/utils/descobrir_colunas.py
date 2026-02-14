#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DESCOBRIR ESTRUTURA DAS TABELAS
==============================
"""

def descobrir_colunas_tabelas():
    """Descobre as colunas das 3 tabelas"""
    print("🔍 DESCOBRINDO ESTRUTURA DAS TABELAS")
    print("=" * 50)
    
    try:
        from conector_megasena_db import ConectorMegaSena
        
        conector = ConectorMegaSena()
        if conector.conectar_banco():
            print("✅ Conectado ao banco!")
            cursor = conector.conexao.cursor()
            
            # Tabela 1: Resultados_MegaSenaFechado
            print("\n📊 TABELA: Resultados_MegaSenaFechado")
            print("-" * 40)
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT TOP 1 * FROM Resultados_MegaSenaFechado")
            columns = [column[0] for column in cursor.description]
            print(f"Colunas: {columns}")
            
            # Tabela 2: NumerosCiclosMega
            print("\n🔄 TABELA: NumerosCiclosMega")
            print("-" * 30)
            try:
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute("SELECT TOP 1 * FROM NumerosCiclosMega")
                columns = [column[0] for column in cursor.description]
                print(f"Colunas: {columns}")
            except Exception as e:
                print(f"Erro ou tabela não existe: {e}")
            
            # Tabela 3: COMBIN_MEGASENA
            print("\n🎲 TABELA: COMBIN_MEGASENA")
            print("-" * 25)
            try:
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute("SELECT TOP 1 * FROM COMBIN_MEGASENA")
                columns = [column[0] for column in cursor.description]
                print(f"Colunas: {columns}")
            except Exception as e:
                print(f"Erro ou tabela não existe: {e}")
            
            conector.fechar_conexao()
            
        else:
            print("❌ Falha na conexão")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    descobrir_colunas_tabelas()
