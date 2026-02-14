#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ATUALIZAR COLUNAS DE ACERTOS - COMBINACOES_LOTOFACIL20_COMPLETO
==================================================================
Este script adiciona as colunas Acertos_11, Acertos_12, Acertos_13,
Acertos_14 e Acertos_15 na tabela COMBINACOES_LOTOFACIL20_COMPLETO.

Executar este script antes de atualizar os concursos para garantir
que as colunas existam.

Autor: LotoScope
Data: 20/01/2026
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from database_config import DatabaseConfig
    db_config = DatabaseConfig()
except ImportError:
    from lotofacil_lite.database_config import DatabaseConfig
    db_config = DatabaseConfig()


def criar_colunas_acertos() -> bool:
    """
    Cria as colunas de acertos (11 a 15) na tabela COMBINACOES_LOTOFACIL20_COMPLETO.
    
    Returns:
        bool: True se criou/verificou com sucesso
    """
    print("\n🔧 CRIANDO/VERIFICANDO COLUNAS DE ACERTOS")
    print("=" * 60)
    
    colunas_necessarias = [
        ('Acertos_15', 'INT DEFAULT 0 NOT NULL'),
        ('Acertos_14', 'INT DEFAULT 0 NOT NULL'),
        ('Acertos_13', 'INT DEFAULT 0 NOT NULL'),
        ('Acertos_12', 'INT DEFAULT 0 NOT NULL'),
        ('Acertos_11', 'INT DEFAULT 0 NOT NULL'),
    ]
    
    try:
        with db_config.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("❌ Tabela COMBINACOES_LOTOFACIL20_COMPLETO não encontrada!")
                return False
            
            print("✅ Tabela COMBINACOES_LOTOFACIL20_COMPLETO encontrada")
            
            # Verificar cada coluna e criar se necessário
            colunas_criadas = 0
            colunas_existentes = 0
            
            for coluna_nome, coluna_tipo in colunas_necessarias:
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
                    AND COLUMN_NAME = ?
                """, (coluna_nome,))
                
                if cursor.fetchone()[0] == 0:
                    # Coluna não existe, criar
                    print(f"   🔄 Criando coluna {coluna_nome}...")
                    cursor.execute(f"""
                        ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
                        ADD {coluna_nome} {coluna_tipo}
                    """)
                    conn.commit()
                    print(f"   ✅ Coluna {coluna_nome} criada com sucesso!")
                    colunas_criadas += 1
                else:
                    print(f"   ⚠️ Coluna {coluna_nome} já existe")
                    colunas_existentes += 1
            
            # Criar índices para as colunas
            print("\n📊 Verificando/Criando índices...")
            
            for coluna_nome, _ in colunas_necessarias:
                indice_nome = f"IX_COMBINACOES20_{coluna_nome}"
                
                cursor.execute("""
                    SELECT COUNT(*) FROM sys.indexes 
                    WHERE name = ? AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL20_COMPLETO')
                """, (indice_nome,))
                
                if cursor.fetchone()[0] == 0:
                    print(f"   🔄 Criando índice {indice_nome}...")
                    cursor.execute(f"""
                        CREATE INDEX {indice_nome} 
                        ON COMBINACOES_LOTOFACIL20_COMPLETO({coluna_nome})
                    """)
                    conn.commit()
                    print(f"   ✅ Índice {indice_nome} criado!")
                else:
                    print(f"   ⚠️ Índice {indice_nome} já existe")
            
            print("\n📋 RESUMO:")
            print("=" * 60)
            print(f"   ✅ Colunas criadas: {colunas_criadas}")
            print(f"   ⚠️ Colunas já existentes: {colunas_existentes}")
            print(f"   📊 Total de colunas de acertos: {colunas_criadas + colunas_existentes}")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar colunas: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_estrutura_colunas() -> dict:
    """
    Verifica a estrutura atual das colunas de acertos.
    
    Returns:
        dict: Informações sobre as colunas
    """
    print("\n📋 VERIFICANDO ESTRUTURA DAS COLUNAS DE ACERTOS")
    print("=" * 60)
    
    resultado = {
        'tabela_existe': False,
        'colunas': {},
        'total_registros': 0
    }
    
    try:
        with db_config.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar tabela
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
            """)
            
            resultado['tabela_existe'] = cursor.fetchone()[0] > 0
            
            if not resultado['tabela_existe']:
                print("❌ Tabela não encontrada!")
                return resultado
            
            # Buscar informações das colunas de acertos
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
                AND COLUMN_NAME LIKE 'Acertos_%'
                ORDER BY COLUMN_NAME DESC
            """)
            
            print(f"\n{'COLUNA':<20} {'TIPO':<10} {'NULO':<6} {'PADRÃO':<10}")
            print("-" * 50)
            
            for row in cursor.fetchall():
                coluna = row[0]
                tipo = row[1]
                nulo = row[2]
                padrao = str(row[3]) if row[3] else "Nenhum"
                
                resultado['colunas'][coluna] = {
                    'tipo': tipo,
                    'nullable': nulo,
                    'default': padrao
                }
                
                print(f"{coluna:<20} {tipo:<10} {nulo:<6} {padrao:<10}")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL20_COMPLETO")
            resultado['total_registros'] = cursor.fetchone()[0]
            
            print(f"\n📊 Total de combinações na tabela: {resultado['total_registros']:,}")
            
            # Estatísticas de acertos (se colunas existem)
            if resultado['colunas']:
                print("\n📈 ESTATÍSTICAS DE ACERTOS:")
                print("-" * 50)
                
                for coluna in sorted(resultado['colunas'].keys(), reverse=True):
                    try:
                        cursor.execute(f"""
                            SELECT 
                                SUM({coluna}) as total_acertos,
                                COUNT(CASE WHEN {coluna} > 0 THEN 1 END) as combinacoes_com_acertos,
                                MAX({coluna}) as max_acertos
                            FROM COMBINACOES_LOTOFACIL20_COMPLETO
                        """)
                        stats = cursor.fetchone()
                        total = stats[0] if stats[0] else 0
                        com_acertos = stats[1] if stats[1] else 0
                        max_acertos = stats[2] if stats[2] else 0
                        
                        print(f"   {coluna}: {total:,} total | {com_acertos:,} combinações | máx: {max_acertos}")
                    except:
                        pass
            
            return resultado
            
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return resultado


if __name__ == "__main__":
    print("🎯 SCRIPT DE ATUALIZAÇÃO DE COLUNAS DE ACERTOS")
    print("=" * 60)
    print("Tabela: COMBINACOES_LOTOFACIL20_COMPLETO")
    print("Colunas: Acertos_11, Acertos_12, Acertos_13, Acertos_14, Acertos_15")
    print("=" * 60)
    
    # Primeiro verificar estrutura atual
    verificar_estrutura_colunas()
    
    # Perguntar se deseja criar/atualizar
    print("\n")
    resposta = input("🔄 Deseja criar/atualizar as colunas? (s/n): ").strip().lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        if criar_colunas_acertos():
            print("\n✅ Colunas criadas/verificadas com sucesso!")
            
            # Verificar estrutura final
            print("\n")
            verificar_estrutura_colunas()
        else:
            print("\n❌ Erro ao criar colunas!")
    else:
        print("\n⏸️ Operação cancelada pelo usuário.")
    
    input("\n⏸️ Pressione ENTER para sair...")
