#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 DESCOBRIDOR DE ESTRUTURA - TABELA RESULTADOS
==============================================
Descobre automaticamente a estrutura da tabela de resultados
"""

try:
    from database_optimizer import get_optimized_connection
    USE_OPTIMIZER = True
except ImportError:
    try:
        from database_config import db_config
        USE_OPTIMIZER = False
    except ImportError:
        import pyodbc
        USE_OPTIMIZER = None

def get_connection():
    """🔌 Obtém conexão usando sistema disponível"""
    if USE_OPTIMIZER:
        return get_optimized_connection()
    elif USE_OPTIMIZER is False:
        return db_config.get_connection()
    else:
        # Fallback
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-71QV65D\\SQLEXPRESS;"
            "DATABASE=LotofacilDB;"
            "Trusted_Connection=yes;"
            "MARS_Connection=Yes;"
        )
        return pyodbc.connect(connection_string)

def descobrir_tabela_resultados():
    """🔍 Descobre a tabela e estrutura de resultados"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Possíveis nomes da tabela
            nomes_possiveis = ['resultados_int', 'Resultados_INT', 'RESULTADOS_INT', 'resultados']
            
            tabela_encontrada = None
            
            for nome in nomes_possiveis:
                try:
                    cursor.execute(f"SELECT TOP 1 * FROM {nome}")
                    tabela_encontrada = nome
                    print(f"✅ Tabela encontrada: {nome}")
                    break
                except:
                    continue
            
            if not tabela_encontrada:
                print("❌ Nenhuma tabela de resultados encontrada!")
                return None, []
            
            # Descobre colunas
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{tabela_encontrada.split('.')[-1]}'
                ORDER BY ORDINAL_POSITION
            """)
            
            colunas = cursor.fetchall()
            
            print(f"\n📋 Estrutura da tabela {tabela_encontrada}:")
            for i, (nome, tipo, nullable) in enumerate(colunas, 1):
                print(f"  {i:2d}. {nome:<20} | {tipo:<15} | {'NULL' if nullable == 'YES' else 'NOT NULL'}")
            
            # Identifica colunas de números
            colunas_numeros = []
            for nome, tipo, _ in colunas:
                if any(palavra in nome.lower() for palavra in ['bola', 'numero', 'num', 'dezena']):
                    colunas_numeros.append(nome)
            
            print(f"\n🎯 Colunas de números identificadas: {colunas_numeros}")
            
            # Identifica coluna de concurso
            coluna_concurso = None
            for nome, tipo, _ in colunas:
                if 'concurso' in nome.lower():
                    coluna_concurso = nome
                    break
            
            print(f"🏆 Coluna de concurso: {coluna_concurso}")
            
            # Testa alguns dados
            if colunas_numeros and coluna_concurso:
                select_colunas = ', '.join([coluna_concurso] + colunas_numeros[:15])
                cursor.execute(f"SELECT TOP 2 {select_colunas} FROM {tabela_encontrada} ORDER BY {coluna_concurso} DESC")
                
                print(f"\n📊 Exemplos de dados:")
                resultados = cursor.fetchall()
                for i, resultado in enumerate(resultados, 1):
                    print(f"  {i}. {resultado}")
            
            return tabela_encontrada, {
                'tabela': tabela_encontrada,
                'coluna_concurso': coluna_concurso,
                'colunas_numeros': colunas_numeros,
                'todas_colunas': [nome for nome, _, _ in colunas]
            }
            
    except Exception as e:
        print(f"❌ Erro ao descobrir estrutura: {e}")
        return None, {}

def gerar_queries_otimizadas(estrutura):
    """🔧 Gera queries otimizadas baseadas na estrutura descoberta"""
    
    if not estrutura:
        return {}
    
    tabela = estrutura['tabela']
    col_concurso = estrutura['coluna_concurso']
    cols_numeros = estrutura['colunas_numeros']
    
    # Limita a 15 números (Lotofácil)
    cols_numeros_lotofacil = cols_numeros[:15]
    
    queries = {
        'buscar_concursos': f"""
            SELECT DISTINCT {col_concurso} 
            FROM {tabela} 
            WHERE {col_concurso} IS NOT NULL 
            ORDER BY {col_concurso}
        """,
        
        'obter_resultado': f"""
            SELECT {', '.join(cols_numeros_lotofacil)}
            FROM {tabela} 
            WHERE {col_concurso} = ?
        """,
        
        'ultimo_concurso': f"""
            SELECT MAX({col_concurso}) 
            FROM {tabela}
        """,
        
        'range_concursos': f"""
            SELECT MIN({col_concurso}) as min_conc, MAX({col_concurso}) as max_conc 
            FROM {tabela}
        """
    }
    
    print(f"\n🛠️ Queries geradas:")
    for nome, query in queries.items():
        print(f"\n{nome}:")
        print(f"  {query.strip()}")
    
    return queries

def main():
    """Função principal"""
    print("🔧 DESCOBRIDOR DE ESTRUTURA - TABELA RESULTADOS")
    print("=" * 60)
    
    tabela, estrutura = descobrir_tabela_resultados()
    
    if tabela:
        queries = gerar_queries_otimizadas(estrutura)
        
        print(f"\n✅ ESTRUTURA DESCOBERTA COM SUCESSO!")
        print(f"📁 Tabela: {estrutura['tabela']}")
        print(f"🏆 Concurso: {estrutura['coluna_concurso']}")
        print(f"🎯 Números: {len(estrutura['colunas_numeros'])} colunas")
        
        # Salva estrutura para uso futuro
        import json
        with open('estrutura_tabela_resultados.json', 'w') as f:
            json.dump({
                'estrutura': estrutura,
                'queries': queries,
                'descoberto_em': str(datetime.now()) if 'datetime' in globals() else 'unknown'
            }, f, indent=2)
        
        print(f"💾 Estrutura salva em: estrutura_tabela_resultados.json")
        
    else:
        print(f"❌ Não foi possível descobrir a estrutura!")

if __name__ == "__main__":
    from datetime import datetime
    main()