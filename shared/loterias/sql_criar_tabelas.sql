-- ============================================================
-- CRIAÇÃO DAS TABELAS DE RESULTADOS - MEGA-SENA, QUINA, DUPLA SENA
-- ============================================================
-- Execute no banco LOTOFACIL (SSMS ou Azure Data Studio)
-- ============================================================

-- 1. MEGA-SENA (6 números, 1-60)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados_MegaSenaFechado' AND xtype='U')
BEGIN
    CREATE TABLE Resultados_MegaSenaFechado (
        Concurso INT PRIMARY KEY,
        Data_Sorteio VARCHAR(10),
        N1 INT, N2 INT, N3 INT, N4 INT, N5 INT, N6 INT,
        S1 INT DEFAULT NULL, S2 INT DEFAULT NULL, S3 INT DEFAULT NULL,
        S4 INT DEFAULT NULL, S5 INT DEFAULT NULL, S6 INT DEFAULT NULL,
        DataGeracao DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Resultados_MegaSenaFechado criada';
END
ELSE
    PRINT 'ℹ️ Resultados_MegaSenaFechado já existe';

-- 2. QUINA (5 números, 1-80)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados_Quina' AND xtype='U')
BEGIN
    CREATE TABLE Resultados_Quina (
        Concurso INT PRIMARY KEY,
        Data_Sorteio VARCHAR(10),
        N1 INT, N2 INT, N3 INT, N4 INT, N5 INT,
        S1 INT DEFAULT NULL, S2 INT DEFAULT NULL, S3 INT DEFAULT NULL,
        S4 INT DEFAULT NULL, S5 INT DEFAULT NULL,
        DataGeracao DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Resultados_Quina criada';
END
ELSE
    PRINT 'ℹ️ Resultados_Quina já existe';

-- 3. DUPLA SENA (6 números, 1-50)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados_DuplaSena' AND xtype='U')
BEGIN
    CREATE TABLE Resultados_DuplaSena (
        Concurso INT PRIMARY KEY,
        Data_Sorteio VARCHAR(10),
        N1 INT, N2 INT, N3 INT, N4 INT, N5 INT, N6 INT,
        S1 INT DEFAULT NULL, S2 INT DEFAULT NULL, S3 INT DEFAULT NULL,
        S4 INT DEFAULT NULL, S5 INT DEFAULT NULL, S6 INT DEFAULT NULL,
        DataGeracao DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Resultados_DuplaSena criada';
END
ELSE
    PRINT 'ℹ️ Resultados_DuplaSena já existe';
