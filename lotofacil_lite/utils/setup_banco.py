#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗃️ SETUP BANCO DE DADOS - LOTOFÁCIL LITE
Script para criar as tabelas necessárias
Autor: AR CALHAU
Data: 04 de Agosto de 2025
"""

import sys
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


def criar_tabela_resultados():
    """Cria a tabela Resultados compatível com o sistema existente"""
    print("📋 Criando tabela Resultados...")
    
    sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados' AND xtype='U')
    BEGIN
        CREATE TABLE Resultados (
            Concurso INT PRIMARY KEY,
            DataSorteio VARCHAR(10),
            N1 INT, N2 INT, N3 INT, N4 INT, N5 INT,
            N6 INT, N7 INT, N8 INT, N9 INT, N10 INT,
            N11 INT, N12 INT, N13 INT, N14 INT, N15 INT,
            Baixos INT DEFAULT 0,
            Altos INT DEFAULT 0,
            Pares INT DEFAULT 0,
            Impares INT DEFAULT 0,
            Consecutivos INT DEFAULT 0,
            SomaTotal INT DEFAULT 0,
            Acumulado BIT DEFAULT 0,
            ValorEstimado DECIMAL(15,2) DEFAULT 0,
            UltimaAtualizacao DATETIME DEFAULT GETDATE()
        );
        
        PRINT 'Tabela Resultados criada com sucesso';
    END
    ELSE
    BEGIN
        PRINT 'Tabela Resultados já existe';
    END
    """
    
    if db_config.execute_command(sql):
        print("✅ Tabela Resultados: OK")
        return True
    else:
        print("❌ Erro ao criar tabela Resultados")
        return False

def criar_tabela_numerosciclos():
    """Cria a tabela NumerosCiclos (opcional)"""
    print("🔄 Criando tabela NumerosCiclos...")
    
    sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='NumerosCiclos' AND xtype='U')
    BEGIN
        CREATE TABLE NumerosCiclos (
            Numero INT PRIMARY KEY CHECK (Numero BETWEEN 1 AND 25),
            UltimoSorteio INT DEFAULT 0,
            CicloAtual INT DEFAULT 0,
            Urgencia DECIMAL(5,2) DEFAULT 1.0,
            MediaCiclo DECIMAL(5,2) DEFAULT 0,
            UltimaAtualizacao DATETIME DEFAULT GETDATE()
        );
        
        -- Insere os 25 números
        DECLARE @i INT = 1;
        WHILE @i <= 25
        BEGIN
            INSERT INTO NumerosCiclos (Numero) VALUES (@i);
            SET @i = @i + 1;
        END
        
        PRINT 'Tabela NumerosCiclos criada e populada';
    END
    ELSE
    BEGIN
        PRINT 'Tabela NumerosCiclos já existe';
    END
    """
    
    if db_config.execute_command(sql):
        print("✅ Tabela NumerosCiclos: OK")
        return True
    else:
        print("❌ Erro ao criar tabela NumerosCiclos")
        return False

def criar_indices():
    """Cria índices para melhor performance"""
    print("📈 Criando índices...")
    
    indices = [
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Resultados_Concurso')
        BEGIN
            CREATE INDEX IX_Resultados_Concurso ON Resultados(Concurso);
            PRINT 'Índice IX_Resultados_Concurso criado';
        END
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Resultados_DataSorteio')
        BEGIN
            CREATE INDEX IX_Resultados_DataSorteio ON Resultados(DataSorteio);
            PRINT 'Índice IX_Resultados_DataSorteio criado';
        END
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_NumerosCiclos_Urgencia')
        BEGIN
            CREATE INDEX IX_NumerosCiclos_Urgencia ON NumerosCiclos(Urgencia DESC);
            PRINT 'Índice IX_NumerosCiclos_Urgencia criado';
        END
        """
    ]
    
    sucessos = 0
    for sql in indices:
        if db_config.execute_command(sql):
            sucessos += 1
    
    print(f"✅ Índices criados: {sucessos}/{len(indices)}")
    return sucessos == len(indices)

def verificar_estrutura():
    """Verifica se as tabelas foram criadas corretamente"""
    print("🔍 Verificando estrutura do banco...")
    
    # Verifica tabela Resultados
    sql_resultados = """
    SELECT COUNT_BIG(*) FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME = 'Resultados'
    """
    
    resultado = db_config.execute_query(sql_resultados)
    if resultado and resultado[0][0] == 1:
        print("✅ Tabela Resultados: Existe")
        
        # Conta colunas
        sql_colunas = """
        SELECT COUNT_BIG(*) FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Resultados'
        """
        resultado_colunas = db_config.execute_query(sql_colunas)
        if resultado_colunas:
            total_colunas = resultado_colunas[0][0]
            print(f"   📊 Colunas: {total_colunas}")
    else:
        print("❌ Tabela Resultados: Não existe")
        return False
    
    # Verifica tabela NumerosCiclos
    sql_ciclos = """
    SELECT COUNT_BIG(*) FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME = 'NumerosCiclos'
    """
    
    resultado = db_config.execute_query(sql_ciclos)
    if resultado and resultado[0][0] == 1:
        print("✅ Tabela NumerosCiclos: Existe")
        
        # Conta registros
        sql_registros = "SELECT COUNT_BIG(*) FROM NumerosCiclos"
        resultado_registros = db_config.execute_query(sql_registros)
        if resultado_registros:
            total_registros = resultado_registros[0][0]
            print(f"   📊 Registros: {total_registros}")
    else:
        print("⚠️ Tabela NumerosCiclos: Não existe (opcional)")
    
    return True

def executar_setup():
    """Executa o setup completo do banco"""
    print("🗃️ SETUP DO BANCO DE DADOS - LOTOFÁCIL LITE")
    print("=" * 50)
    
    # Testa conexão
    print("🔗 Testando conexão...")
    if not db_config.test_connection():
        print("❌ Falha na conexão com o banco!")
        print("💡 Verifique as configurações em database_config.py")
        return False
    
    print("✅ Conexão estabelecida!")
    
    # Cria tabelas
    print("\n📋 Criando estrutura do banco...")
    
    sucessos = []
    sucessos.append(criar_tabela_resultados())
    sucessos.append(criar_tabela_numerosciclos())
    sucessos.append(criar_indices())
    
    # Verifica resultado
    if all(sucessos):
        print("\n✅ Estrutura criada com sucesso!")
    else:
        print("\n⚠️ Alguns problemas na criação da estrutura")
    
    # Verificação final
    print("\n🔍 Verificação final...")
    verificar_estrutura()
    
    print("\n🎯 SETUP CONCLUÍDO!")
    print("💡 Agora você pode executar 'python main.py'")
    
    return all(sucessos)

if __name__ == "__main__":
    print("Deseja executar o setup do banco de dados? (s/N): ", end="")
    resposta = input().strip().lower()
    
    if resposta == 's':
        sucesso = executar_setup()
        
        if sucesso:
            print("\n🏆 Setup realizado com sucesso!")
        else:
            print("\n❌ Setup apresentou problemas")
    else:
        print("Setup cancelado")
    
    input("\nPressione Enter para sair...")
