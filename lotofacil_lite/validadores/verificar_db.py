#!/usr/bin/env python3
import sqlite3

def verificar_database():
    try:
        conn = sqlite3.connect('C:/Users/AR CALHAU/source/repos/LotoScope/LotoScope.db')
        cursor = conn.cursor()
        
        # Listar tabelas
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        print('📊 TABELAS DISPONÍVEIS:')
        for tabela in tabelas:
            print(f'  - {tabela[0]}')
        
        # Verificar qual tem resultados da lotofácil
        for tabela in tabelas:
            nome_tabela = tabela[0]
            if 'lotof' in nome_tabela.lower() or 'resultado' in nome_tabela.lower():
                print(f'\n🔍 ANALISANDO TABELA: {nome_tabela}')
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute(f"SELECT MAX(Concurso) as ultimo_concurso FROM {nome_tabela} LIMIT 1")
                try:
                    resultado = cursor.fetchone()
                    if resultado and resultado[0]:
                        print(f'  📈 Último concurso: {resultado[0]}')
                        print(f'  🔮 Próximo concurso: {resultado[0] + 1}')
                    else:
                        print(f'  ❌ Sem dados de concurso')
                except Exception as e:
                    print(f'  ⚠️  Erro na tabela: {e}')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Erro ao conectar database: {e}')

if __name__ == "__main__":
    verificar_database()
