#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DESCOBRIR NOMES EXATOS DAS COLUNAS
==================================
"""

try:
    from conector_megasena_db import ConectorMegaSena
    
    print("🔍 DESCOBRINDO NOMES EXATOS DAS COLUNAS")
    print("=" * 45)
    
    conector = ConectorMegaSena()
    
    if conector.conectar_banco():
        print("✅ Conexão OK")
        cursor = conector.conexao.cursor()
        
        # Descobre as colunas da tabela Resultados_MegaSenaFechado
        print("\n📊 TABELA: Resultados_MegaSenaFechado")
        print("-" * 40)
        
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Resultados_MegaSenaFechado'
            ORDER BY ORDINAL_POSITION
        """)
        
        colunas = cursor.fetchall()
        for coluna in colunas:
            print(f"   {coluna[0]} ({coluna[1]})")
        
        # Também pega uma amostra dos dados
        print("\n📋 AMOSTRA DOS DADOS (TOP 1):")
        print("-" * 30)
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT TOP 1 * FROM Resultados_MegaSenaFechado")
        
        # Pega os nomes das colunas do resultado
        nomes_colunas = [desc[0] for desc in cursor.description]
        print(f"Colunas na consulta: {nomes_colunas}")
        
        # Pega os dados
        dados = cursor.fetchone()
        if dados:
            print("Dados da primeira linha:")
            for i, (nome, valor) in enumerate(zip(nomes_colunas, dados)):
                print(f"   {nome} = {valor}")
        
        conector.fechar_conexao()
        print("\n✅ Investigação concluída!")
    else:
        print("❌ Falha na conexão")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
