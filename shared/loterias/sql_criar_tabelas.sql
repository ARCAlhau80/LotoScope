-- ============================================================
-- CRIAÇÃO DAS TABELAS DE RESULTADOS
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
    PRINT 'OK Resultados_MegaSenaFechado';
END
ELSE PRINT 'EXISTE Resultados_MegaSenaFechado';

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
    PRINT 'OK Resultados_Quina';
END
ELSE PRINT 'EXISTE Resultados_Quina';

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
    PRINT 'OK Resultados_DuplaSena';
END
ELSE PRINT 'EXISTE Resultados_DuplaSena';

-- 4. DIA DE SORTE (7 números, 1-31)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados_DiaDeSorte' AND xtype='U')
BEGIN
    CREATE TABLE Resultados_DiaDeSorte (
        Concurso INT PRIMARY KEY,
        Data_Sorteio VARCHAR(10),
        N1 INT, N2 INT, N3 INT, N4 INT, N5 INT, N6 INT, N7 INT,
        S1 INT DEFAULT NULL, S2 INT DEFAULT NULL, S3 INT DEFAULT NULL,
        S4 INT DEFAULT NULL, S5 INT DEFAULT NULL, S6 INT DEFAULT NULL, S7 INT DEFAULT NULL,
        DataGeracao DATETIME DEFAULT GETDATE()
    );
    PRINT 'OK Resultados_DiaDeSorte';
END
ELSE PRINT 'EXISTE Resultados_DiaDeSorte';

-- 5. TIMEMANIA (7 números, 1-80)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados_Timemania' AND xtype='U')
BEGIN
    CREATE TABLE Resultados_Timemania (
        Concurso INT PRIMARY KEY,
        Data_Sorteio VARCHAR(10),
        N1 INT, N2 INT, N3 INT, N4 INT, N5 INT, N6 INT, N7 INT,
        S1 INT DEFAULT NULL, S2 INT DEFAULT NULL, S3 INT DEFAULT NULL,
        S4 INT DEFAULT NULL, S5 INT DEFAULT NULL, S6 INT DEFAULT NULL, S7 INT DEFAULT NULL,
        DataGeracao DATETIME DEFAULT GETDATE()
    );
    PRINT 'OK Resultados_Timemania';
END
ELSE PRINT 'EXISTE Resultados_Timemania';

-- 6. SUPER SETE (7 colunas, digito 0-9 cada)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados_SuperSete' AND xtype='U')
BEGIN
    CREATE TABLE Resultados_SuperSete (
        Concurso INT PRIMARY KEY,
        Data_Sorteio VARCHAR(10),
        N1 INT, N2 INT, N3 INT, N4 INT, N5 INT, N6 INT, N7 INT,
        S1 INT DEFAULT NULL, S2 INT DEFAULT NULL, S3 INT DEFAULT NULL,
        S4 INT DEFAULT NULL, S5 INT DEFAULT NULL, S6 INT DEFAULT NULL, S7 INT DEFAULT NULL,
        DataGeracao DATETIME DEFAULT GETDATE()
    );
    PRINT 'OK Resultados_SuperSete';
END
ELSE PRINT 'EXISTE Resultados_SuperSete';

-- 7. MAIS MILIONÁRIA (6 números 1-50 + 2 trevos 1-6)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Resultados_MaisMilionaria' AND xtype='U')
BEGIN
    CREATE TABLE Resultados_MaisMilionaria (
        Concurso INT PRIMARY KEY,
        Data_Sorteio VARCHAR(10),
        N1 INT, N2 INT, N3 INT, N4 INT, N5 INT, N6 INT,
        T1 INT, T2 INT,
        S1 INT DEFAULT NULL, S2 INT DEFAULT NULL, S3 INT DEFAULT NULL,
        S4 INT DEFAULT NULL, S5 INT DEFAULT NULL, S6 INT DEFAULT NULL,
        DataGeracao DATETIME DEFAULT GETDATE()
    );
    PRINT 'OK Resultados_MaisMilionaria';
END
ELSE PRINT 'EXISTE Resultados_MaisMilionaria';
