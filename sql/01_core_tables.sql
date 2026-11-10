-- ============================================================================
-- LotoScope - 01_core_tables.sql
-- Cria o banco LOTOFACIL e as tabelas essenciais do dashboard/analises.
-- Idempotente: pode rodar novamente sem apagar dados existentes.
-- Requer SQL Server 2019+ e permissao para CREATE DATABASE/TABLE/INDEX.
-- ============================================================================

SET NOCOUNT ON;
GO

IF DB_ID('LOTOFACIL') IS NULL
BEGIN
    CREATE DATABASE LOTOFACIL;
    PRINT 'Banco LOTOFACIL criado.';
END
ELSE PRINT 'Banco LOTOFACIL ja existe.';
GO

USE LOTOFACIL;
GO

-- Resultados_INT
IF OBJECT_ID('dbo.Resultados_INT', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_INT (
        [Concurso] BIGINT NOT NULL,
        [Data_Sorteio] DATETIME NULL,
        [N1] BIGINT NULL,
        [N2] BIGINT NULL,
        [N3] BIGINT NULL,
        [N4] BIGINT NULL,
        [N5] BIGINT NULL,
        [N6] BIGINT NULL,
        [N7] BIGINT NULL,
        [N8] BIGINT NULL,
        [N9] BIGINT NULL,
        [N10] BIGINT NULL,
        [N11] BIGINT NULL,
        [N12] BIGINT NULL,
        [N13] BIGINT NULL,
        [N14] BIGINT NULL,
        [N15] BIGINT NULL,
        [Resultado] VARCHAR(MAX) NULL,
        [Localidade] VARCHAR(MAX) NULL,
        [Latitude] VARCHAR(MAX) NULL,
        [Longitude] VARCHAR(MAX) NULL,
        [QtdePrimos] BIGINT NULL,
        [QtdeFibonacci] BIGINT NULL,
        [QtdeImpares] BIGINT NULL,
        [SomaTotal] BIGINT NULL,
        [Quintil1] BIGINT NULL,
        [Quintil2] BIGINT NULL,
        [Quintil3] BIGINT NULL,
        [Quintil4] BIGINT NULL,
        [Quintil5] BIGINT NULL,
        [QtdeGaps] BIGINT NULL,
        [QtdeRepetidos] BIGINT NULL,
        [SEQ] FLOAT NULL,
        [DistanciaExtremos] BIGINT NULL,
        [ParesSequencia] BIGINT NULL,
        [QtdeMultiplos3] INT NULL DEFAULT ((0)),
        [ParesSaltados] INT NULL,
        [Faixa_Baixa] INT NULL,
        [Faixa_Media] INT NULL,
        [Faixa_Alta] INT NULL,
        [RepetidosMesmaPosicao] INT NULL,
        [Acumulou] BIT NULL,
        [menor_que_ultimo] INT NULL,
        [maior_que_ultimo] INT NULL,
        [igual_ao_ultimo] INT NULL,
        [S1] TINYINT NULL,
        [S2] TINYINT NULL,
        [S3] TINYINT NULL,
        [S4] TINYINT NULL,
        [S5] TINYINT NULL,
        [S6] TINYINT NULL,
        [S7] TINYINT NULL,
        [S8] TINYINT NULL,
        [S9] TINYINT NULL,
        [S10] TINYINT NULL,
        [S11] TINYINT NULL,
        [S12] TINYINT NULL,
        [S13] TINYINT NULL,
        [S14] TINYINT NULL,
        [S15] TINYINT NULL,
        CONSTRAINT [PK_Resultados_INT] PRIMARY KEY ([Concurso])
    );
    PRINT 'Tabela Resultados_INT criada.';
END
ELSE PRINT 'Tabela Resultados_INT ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Resultados_INT_Data_Sorteio' AND object_id = OBJECT_ID('dbo.Resultados_INT'))
    CREATE INDEX [IX_Resultados_INT_Data_Sorteio] ON dbo.Resultados_INT (Data_Sorteio);
GO

-- NumerosCiclos
IF OBJECT_ID('dbo.NumerosCiclos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.NumerosCiclos (
        [Ciclo] INT NULL,
        [Numero] INT NULL,
        [QtdSorteados] INT NULL,
        [ConcursoInicio] INT NULL,
        [ConcursoFechamento] INT NULL,
        [DataInicio] DATETIME NULL,
        [DataFim] DATETIME NULL
    );
    PRINT 'Tabela NumerosCiclos criada.';
END
ELSE PRINT 'Tabela NumerosCiclos ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_NumerosCiclos_Ciclo_Numero' AND object_id = OBJECT_ID('dbo.NumerosCiclos'))
    CREATE INDEX [IX_NumerosCiclos_Ciclo_Numero] ON dbo.NumerosCiclos (Ciclo, Numero);
GO

-- COMBINACOES_LOTOFACIL
IF OBJECT_ID('dbo.COMBINACOES_LOTOFACIL', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.COMBINACOES_LOTOFACIL (
        [ID] INT IDENTITY(1,1) NOT NULL,
        [N1] INT NOT NULL,
        [N2] INT NOT NULL,
        [N3] INT NOT NULL,
        [N4] INT NOT NULL,
        [N5] INT NOT NULL,
        [N6] INT NOT NULL,
        [N7] INT NOT NULL,
        [N8] INT NOT NULL,
        [N9] INT NOT NULL,
        [N10] INT NOT NULL,
        [N11] INT NOT NULL,
        [N12] INT NOT NULL,
        [N13] INT NOT NULL,
        [N14] INT NOT NULL,
        [N15] INT NOT NULL,
        [QtdePrimos] INT NULL,
        [QtdeFibonacci] INT NULL,
        [QtdeImpares] INT NULL,
        [SomaTotal] INT NULL,
        [Quintil1] INT NULL,
        [Quintil2] INT NULL,
        [Quintil3] INT NULL,
        [Quintil4] INT NULL,
        [Quintil5] INT NULL,
        [QtdeGaps] INT NULL,
        [QtdeRepetidos] INT NULL,
        [SEQ] INT NULL,
        [DistanciaExtremos] INT NULL,
        [ParesSequencia] INT NULL,
        [QtdeMultiplos3] INT NULL,
        [ParesSaltados] INT NULL,
        [HashQuina] VARCHAR(20) NULL,
        [Faixa_Baixa] INT NULL,
        [Faixa_Media] INT NULL,
        [Faixa_Alta] INT NULL,
        [RepetidosMesmaPosicao] INT NULL,
        [menor_que_ultimo] INT NULL,
        [maior_que_ultimo] INT NULL,
        [igual_ao_ultimo] INT NULL,
        [Acertos_15] INT NOT NULL DEFAULT ((0)),
        [Acertos_14] INT NOT NULL DEFAULT ((0)),
        [Acertos_13] INT NOT NULL DEFAULT ((0)),
        [Acertos_12] INT NOT NULL DEFAULT ((0)),
        [Acertos_11] INT NOT NULL DEFAULT ((0)),
        [Ultimo_Acertos_15] INT NULL,
        [Ultimo_Acertos_14] INT NULL,
        [Ultimo_Acertos_13] INT NULL,
        [Ultimo_Acertos_12] INT NULL,
        [Ultimo_Acertos_11] INT NULL,
        [UltimoConcursoAtualizado] INT NOT NULL DEFAULT ((0)),
        [Acertos_10] INT NOT NULL DEFAULT ((0)),
        [Ultimo_Acertos_10] INT NULL,
        CONSTRAINT [PK_COMBINACOES_LOTOFACIL] PRIMARY KEY ([ID])
    );
    PRINT 'Tabela COMBINACOES_LOTOFACIL criada.';
END
ELSE PRINT 'Tabela COMBINACOES_LOTOFACIL ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Acertos_10' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL'))
    CREATE INDEX [IX_COMBINACOES_LF_Acertos_10] ON dbo.COMBINACOES_LOTOFACIL (Acertos_10);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Acertos_14' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL'))
    CREATE INDEX [IX_COMBINACOES_LF_Acertos_14] ON dbo.COMBINACOES_LOTOFACIL (Acertos_14);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Acertos_15' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL'))
    CREATE INDEX [IX_COMBINACOES_LF_Acertos_15] ON dbo.COMBINACOES_LOTOFACIL (Acertos_15);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Ultimo_10' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL'))
    CREATE INDEX [IX_COMBINACOES_LF_Ultimo_10] ON dbo.COMBINACOES_LOTOFACIL (Ultimo_Acertos_10);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Ultimo_15' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL'))
    CREATE INDEX [IX_COMBINACOES_LF_Ultimo_15] ON dbo.COMBINACOES_LOTOFACIL (Ultimo_Acertos_15);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_UltimoAtualizado' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL'))
    CREATE INDEX [IX_COMBINACOES_LF_UltimoAtualizado] ON dbo.COMBINACOES_LOTOFACIL (UltimoConcursoAtualizado);
GO

-- COMBINACOES_LOTOFACIL20_COMPLETO
IF OBJECT_ID('dbo.COMBINACOES_LOTOFACIL20_COMPLETO', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.COMBINACOES_LOTOFACIL20_COMPLETO (
        [ID] INT NOT NULL,
        [N1] INT NOT NULL,
        [N2] INT NOT NULL,
        [N3] INT NOT NULL,
        [N4] INT NOT NULL,
        [N5] INT NOT NULL,
        [N6] INT NOT NULL,
        [N7] INT NOT NULL,
        [N8] INT NOT NULL,
        [N9] INT NOT NULL,
        [N10] INT NOT NULL,
        [N11] INT NOT NULL,
        [N12] INT NOT NULL,
        [N13] INT NOT NULL,
        [N14] INT NOT NULL,
        [N15] INT NOT NULL,
        [N16] INT NOT NULL,
        [N17] INT NOT NULL,
        [N18] INT NOT NULL,
        [N19] INT NOT NULL,
        [N20] INT NOT NULL,
        [QtdePares] INT NOT NULL,
        [QtdeImpares] INT NOT NULL,
        [QtdePrimos] INT NOT NULL,
        [QtdeFibonacci] INT NOT NULL,
        [QtdeConsecutivos] INT NOT NULL,
        [QtdeDezena1] INT NOT NULL,
        [QtdeDezena2] INT NOT NULL,
        [QtdeDezena3] INT NOT NULL,
        [QtdeDezena4] INT NOT NULL,
        [QtdeDezena5] INT NOT NULL,
        [QtdeLinha1] INT NOT NULL,
        [QtdeLinha2] INT NOT NULL,
        [QtdeLinha3] INT NOT NULL,
        [QtdeLinha4] INT NOT NULL,
        [QtdeLinha5] INT NOT NULL,
        [QtdeColuna1] INT NOT NULL,
        [QtdeColuna2] INT NOT NULL,
        [QtdeColuna3] INT NOT NULL,
        [QtdeColuna4] INT NOT NULL,
        [QtdeColuna5] INT NOT NULL,
        [QtdeQuadrante1] INT NOT NULL,
        [QtdeQuadrante2] INT NOT NULL,
        [QtdeQuadrante3] INT NOT NULL,
        [QtdeQuadrante4] INT NOT NULL,
        [SomaTotal] INT NOT NULL,
        [MediaAritmetica] FLOAT NOT NULL,
        [MaiorGap] INT NOT NULL,
        [MenorGap] INT NOT NULL,
        [QtdeTerminadosEm0] INT NOT NULL,
        [QtdeTerminadosEm1] INT NOT NULL,
        [QtdeTerminadosEm2] INT NOT NULL,
        [QtdeTerminadosEm3] INT NOT NULL,
        [QtdeTerminadosEm4] INT NOT NULL,
        [QtdeTerminadosEm5] INT NOT NULL,
        [QtdeTerminadosEm6] INT NOT NULL,
        [QtdeTerminadosEm7] INT NOT NULL,
        [QtdeTerminadosEm8] INT NOT NULL,
        [QtdeTerminadosEm9] INT NOT NULL,
        [QtdeRepetidos] INT NULL,
        [RepetidosMesmaPosicao] INT NULL,
        [DataGeracao] VARCHAR(50) NOT NULL,
        [Processado] NVARCHAR(50) NOT NULL,
        [Acertos_15] INT NOT NULL DEFAULT ((0)),
        [Acertos_14] INT NOT NULL DEFAULT ((0)),
        [Acertos_13] INT NOT NULL DEFAULT ((0)),
        [Acertos_12] INT NOT NULL DEFAULT ((0)),
        [Acertos_11] INT NOT NULL DEFAULT ((0)),
        [Ultimo_Acertos_11] INT NULL,
        [Ultimo_Acertos_12] INT NULL,
        [Ultimo_Acertos_13] INT NULL,
        [Ultimo_Acertos_14] INT NULL,
        [Ultimo_Acertos_15] INT NULL,
        [UltimoConcursoAtualizado] INT NOT NULL DEFAULT ((0)),
        CONSTRAINT [PK_COMBINACOES_LOTOFACIL20_COMPLETO] PRIMARY KEY ([ID])
    );
    PRINT 'Tabela COMBINACOES_LOTOFACIL20_COMPLETO criada.';
END
ELSE PRINT 'Tabela COMBINACOES_LOTOFACIL20_COMPLETO ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Ultimo_14' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL20_COMPLETO'))
    CREATE INDEX [IX_COMBINACOES20_Ultimo_14] ON dbo.COMBINACOES_LOTOFACIL20_COMPLETO (Ultimo_Acertos_14);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Ultimo_15' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL20_COMPLETO'))
    CREATE INDEX [IX_COMBINACOES20_Ultimo_15] ON dbo.COMBINACOES_LOTOFACIL20_COMPLETO (Ultimo_Acertos_15);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_COMBINACOES20_UltimoAtualizado' AND object_id = OBJECT_ID('dbo.COMBINACOES_LOTOFACIL20_COMPLETO'))
    CREATE INDEX [IX_COMBINACOES20_UltimoAtualizado] ON dbo.COMBINACOES_LOTOFACIL20_COMPLETO (UltimoConcursoAtualizado);
GO

-- Resultados_MegaSenaFechado
IF OBJECT_ID('dbo.Resultados_MegaSenaFechado', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_MegaSenaFechado (
        [concurso] INT NOT NULL,
        [data_sorteio] DATETIME NULL,
        [dezenas] VARCHAR(20) NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [QtdePrimos] INT NULL,
        [QtdeFibonacci] INT NULL,
        [QtdeImpares] INT NULL,
        [SomaTotal] SMALLINT NULL,
        [Quintil1] INT NULL,
        [Quintil2] INT NULL,
        [Quintil3] INT NULL,
        [Quintil4] INT NULL,
        [Quintil5] INT NULL,
        [QtdeGaps] TINYINT NULL,
        [QtdeRepetidos] INT NULL,
        [QtdeMultiplos3] INT NULL DEFAULT ((0)),
        [SEQ] INT NULL DEFAULT ((0)),
        [DistanciaExtremos] INT NULL DEFAULT ((0)),
        [ParesSequencia] INT NULL DEFAULT ((0)),
        [GanhadoresSena] INT NULL,
        [menor_que_ultimo] INT NULL,
        [maior_que_ultimo] INT NULL,
        [igual_ao_ultimo] INT NULL,
        CONSTRAINT [PK_Resultados_MegaSenaFechado] PRIMARY KEY ([concurso])
    );
    PRINT 'Tabela Resultados_MegaSenaFechado criada.';
END
ELSE PRINT 'Tabela Resultados_MegaSenaFechado ja existe.';
GO

-- COMBIN_MEGASENA
IF OBJECT_ID('dbo.COMBIN_MEGASENA', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.COMBIN_MEGASENA (
        [Id] INT IDENTITY(1,1) NOT NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [Dezenas] NCHAR(12) NULL,
        [QtdePrimos] INT NULL,
        [QtdeFibonacci] INT NULL,
        [QtdeImpares] INT NULL,
        [SomaTotal] INT NULL,
        [Quintil1] INT NULL,
        [Quintil2] INT NULL,
        [Quintil3] INT NULL,
        [Quintil4] INT NULL,
        [Quintil5] INT NULL,
        [QtdeGaps] INT NULL,
        [QtdeRepetidos] INT NULL,
        [QtdeMultiplos3] INT NULL DEFAULT ((0)),
        [SEQ] INT NULL DEFAULT ((0)),
        [DistanciaExtremos] INT NULL DEFAULT ((0)),
        [ParesSequencia] INT NULL DEFAULT ((0)),
        CONSTRAINT [PK_COMBIN_MEGASENA] PRIMARY KEY ([Id])
    );
    PRINT 'Tabela COMBIN_MEGASENA criada.';
END
ELSE PRINT 'Tabela COMBIN_MEGASENA ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_combin_megasena' AND object_id = OBJECT_ID('dbo.COMBIN_MEGASENA'))
    CREATE INDEX [idx_combin_megasena] ON dbo.COMBIN_MEGASENA (Id,N1,N2,N3,N4,N5,N6,Dezenas);
GO

-- NumerosCiclosMega
IF OBJECT_ID('dbo.NumerosCiclosMega', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.NumerosCiclosMega (
        [Ciclo] INT NULL,
        [Numero] INT NULL,
        [QtdSorteados] INT NULL,
        [ConcursoInicio] INT NULL,
        [ConcursoFechamento] INT NULL,
        [DataInicio] DATETIME NULL,
        [DataFim] DATETIME NULL
    );
    PRINT 'Tabela NumerosCiclosMega criada.';
END
ELSE PRINT 'Tabela NumerosCiclosMega ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_NumerosCiclosMega_Ciclo_Numero' AND object_id = OBJECT_ID('dbo.NumerosCiclosMega'))
    CREATE INDEX [IX_NumerosCiclosMega_Ciclo_Numero] ON dbo.NumerosCiclosMega (Ciclo, Numero);
GO

-- Resultados_Quina
IF OBJECT_ID('dbo.Resultados_Quina', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_Quina (
        [concurso] INT NULL,
        [data_sorteio] DATETIME NULL,
        [dezenas] VARCHAR(MAX) NULL,
        [N1] VARCHAR(2) NULL,
        [N2] VARCHAR(2) NULL,
        [N3] VARCHAR(2) NULL,
        [N4] VARCHAR(2) NULL,
        [N5] VARCHAR(2) NULL,
        [QtdePrimos] INT NULL,
        [QtdeFibonacci] INT NULL,
        [QtdeImpares] INT NULL,
        [SomaTotal] INT NULL,
        [Quintil1] INT NULL,
        [Quintil2] INT NULL,
        [Quintil3] INT NULL,
        [Quintil4] INT NULL,
        [Quintil5] INT NULL,
        [QtdeGaps] INT NULL,
        [QtdeRepetidos] INT NULL,
        [QtdeMultiplos3] INT NULL,
        [SEQ] INT NULL,
        [DistanciaExtremos] INT NULL,
        [ParesSequencia] INT NULL,
        [id] INT IDENTITY(1,1) NOT NULL,
        CONSTRAINT [PK_Resultados_Quina] PRIMARY KEY ([id])
    );
    PRINT 'Tabela Resultados_Quina criada.';
END
ELSE PRINT 'Tabela Resultados_Quina ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Resultados_Quina_concurso' AND object_id = OBJECT_ID('dbo.Resultados_Quina'))
    CREATE INDEX [IX_Resultados_Quina_concurso] ON dbo.Resultados_Quina (concurso);
GO

-- Resultados_DuplaSena
IF OBJECT_ID('dbo.Resultados_DuplaSena', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_DuplaSena (
        [concurso] INT NULL,
        [data_sorteio] DATE NULL,
        [sorteio] INT NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [resultado] VARCHAR(50) NULL,
        [localidade] VARCHAR(100) NULL,
        [QtdePrimos] INT NULL,
        [QtdeFibonacci] INT NULL,
        [QtdeImpares] INT NULL,
        [SomaTotal] INT NULL,
        [Quintil1] INT NULL,
        [Quintil2] INT NULL,
        [Quintil3] INT NULL,
        [Quintil4] INT NULL,
        [Quintil5] INT NULL,
        [QtdeGaps] INT NULL,
        [DataCarga] DATETIME NOT NULL DEFAULT (getdate()),
        [DataSorteio] DATETIME NOT NULL DEFAULT (getdate()),
        [Acumulado] BIT NULL,
        [NumeroJogo] INT NULL,
        [ValorArrecadado] FLOAT NULL,
        [DezenasPrimeiroSorteio] VARCHAR(50) NOT NULL DEFAULT (''),
        [DezenasSegundoSorteio] VARCHAR(50) NOT NULL DEFAULT (''),
        [S2_N1] INT NOT NULL DEFAULT ((0)),
        [S2_N2] INT NOT NULL DEFAULT ((0)),
        [S2_N3] INT NOT NULL DEFAULT ((0)),
        [S2_N4] INT NOT NULL DEFAULT ((0)),
        [S2_N5] INT NOT NULL DEFAULT ((0)),
        [S2_N6] INT NOT NULL DEFAULT ((0)),
        [Ganhadores6Acertos1Sorteio] INT NOT NULL DEFAULT ((0)),
        [Ganhadores6Acertos2Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdePrimos1Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeFibonacci1Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeImpares1Sorteio] INT NOT NULL DEFAULT ((0)),
        [SomaTotal1Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil1_1Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil2_1Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil3_1Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil4_1Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil5_1Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeGaps1Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeMultiplos3_1Sorteio] INT NOT NULL DEFAULT ((0)),
        [Seq1Sorteio] INT NOT NULL DEFAULT ((0)),
        [DistanciaExtremos1Sorteio] INT NOT NULL DEFAULT ((0)),
        [ParesSequencia1Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeRepetidos1Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdePrimos2Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeFibonacci2Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeImpares2Sorteio] INT NOT NULL DEFAULT ((0)),
        [SomaTotal2Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil1_2Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil2_2Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil3_2Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil4_2Sorteio] INT NOT NULL DEFAULT ((0)),
        [Quintil5_2Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeGaps2Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeMultiplos3_2Sorteio] INT NOT NULL DEFAULT ((0)),
        [Seq2Sorteio] INT NOT NULL DEFAULT ((0)),
        [DistanciaExtremos2Sorteio] INT NOT NULL DEFAULT ((0)),
        [ParesSequencia2Sorteio] INT NOT NULL DEFAULT ((0)),
        [QtdeRepetidos2Sorteio] INT NOT NULL DEFAULT ((0))
    );
    PRINT 'Tabela Resultados_DuplaSena criada.';
END
ELSE PRINT 'Tabela Resultados_DuplaSena ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Resultados_DuplaSena_concurso_sorteio' AND object_id = OBJECT_ID('dbo.Resultados_DuplaSena'))
    CREATE INDEX [IX_Resultados_DuplaSena_concurso_sorteio] ON dbo.Resultados_DuplaSena (concurso, sorteio);
GO

-- Resultados_Lotomania
IF OBJECT_ID('dbo.Resultados_Lotomania', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_Lotomania (
        [concurso] INT NOT NULL,
        [data_sorteio] DATETIME NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [N7] INT NULL,
        [N8] INT NULL,
        [N9] INT NULL,
        [N10] INT NULL,
        [N11] INT NULL,
        [N12] INT NULL,
        [N13] INT NULL,
        [N14] INT NULL,
        [N15] INT NULL,
        [N16] INT NULL,
        [N17] INT NULL,
        [N18] INT NULL,
        [N19] INT NULL,
        [N20] INT NULL,
        [localidade] VARCHAR(100) NULL,
        CONSTRAINT [PK_Resultados_Lotomania] PRIMARY KEY ([concurso])
    );
    PRINT 'Tabela Resultados_Lotomania criada.';
END
ELSE PRINT 'Tabela Resultados_Lotomania ja existe.';
GO

-- NumerosCiclos_Lotomania
IF OBJECT_ID('dbo.NumerosCiclos_Lotomania', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.NumerosCiclos_Lotomania (
        [Ciclo] INT NOT NULL,
        [Numero] INT NOT NULL,
        [QtdSorteados] INT NULL DEFAULT ((0)),
        [ConcursoInicio] INT NOT NULL,
        [DataInicio] DATETIME NOT NULL,
        [ConcursoFechamento] INT NULL,
        [DataFim] DATETIME NULL
    );
    PRINT 'Tabela NumerosCiclos_Lotomania criada.';
END
ELSE PRINT 'Tabela NumerosCiclos_Lotomania ja existe.';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_NumerosCiclos_Lotomania_Ciclo_Numero' AND object_id = OBJECT_ID('dbo.NumerosCiclos_Lotomania'))
    CREATE INDEX [IX_NumerosCiclos_Lotomania_Ciclo_Numero] ON dbo.NumerosCiclos_Lotomania (Ciclo, Numero);
GO

-- Resultados_DiaDeSorte
IF OBJECT_ID('dbo.Resultados_DiaDeSorte', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_DiaDeSorte (
        [Concurso] INT NOT NULL,
        [Data_Sorteio] VARCHAR(10) NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [N7] INT NULL,
        [S1] INT NULL DEFAULT (NULL),
        [S2] INT NULL DEFAULT (NULL),
        [S3] INT NULL DEFAULT (NULL),
        [S4] INT NULL DEFAULT (NULL),
        [S5] INT NULL DEFAULT (NULL),
        [S6] INT NULL DEFAULT (NULL),
        [S7] INT NULL DEFAULT (NULL),
        [DataGeracao] DATETIME NULL DEFAULT (getdate()),
        CONSTRAINT [PK_Resultados_DiaDeSorte] PRIMARY KEY ([Concurso])
    );
    PRINT 'Tabela Resultados_DiaDeSorte criada.';
END
ELSE PRINT 'Tabela Resultados_DiaDeSorte ja existe.';
GO

-- Resultados_Timemania
IF OBJECT_ID('dbo.Resultados_Timemania', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_Timemania (
        [Concurso] INT NOT NULL,
        [Data_Sorteio] VARCHAR(10) NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [N7] INT NULL,
        [S1] INT NULL DEFAULT (NULL),
        [S2] INT NULL DEFAULT (NULL),
        [S3] INT NULL DEFAULT (NULL),
        [S4] INT NULL DEFAULT (NULL),
        [S5] INT NULL DEFAULT (NULL),
        [S6] INT NULL DEFAULT (NULL),
        [S7] INT NULL DEFAULT (NULL),
        [DataGeracao] DATETIME NULL DEFAULT (getdate()),
        CONSTRAINT [PK_Resultados_Timemania] PRIMARY KEY ([Concurso])
    );
    PRINT 'Tabela Resultados_Timemania criada.';
END
ELSE PRINT 'Tabela Resultados_Timemania ja existe.';
GO

-- Resultados_SuperSete
IF OBJECT_ID('dbo.Resultados_SuperSete', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_SuperSete (
        [Concurso] INT NOT NULL,
        [Data_Sorteio] VARCHAR(10) NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [N7] INT NULL,
        [S1] INT NULL DEFAULT (NULL),
        [S2] INT NULL DEFAULT (NULL),
        [S3] INT NULL DEFAULT (NULL),
        [S4] INT NULL DEFAULT (NULL),
        [S5] INT NULL DEFAULT (NULL),
        [S6] INT NULL DEFAULT (NULL),
        [S7] INT NULL DEFAULT (NULL),
        [DataGeracao] DATETIME NULL DEFAULT (getdate()),
        CONSTRAINT [PK_Resultados_SuperSete] PRIMARY KEY ([Concurso])
    );
    PRINT 'Tabela Resultados_SuperSete criada.';
END
ELSE PRINT 'Tabela Resultados_SuperSete ja existe.';
GO

-- Resultados_MaisMilionaria
IF OBJECT_ID('dbo.Resultados_MaisMilionaria', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Resultados_MaisMilionaria (
        [Concurso] INT NOT NULL,
        [Data_Sorteio] VARCHAR(10) NULL,
        [N1] INT NULL,
        [N2] INT NULL,
        [N3] INT NULL,
        [N4] INT NULL,
        [N5] INT NULL,
        [N6] INT NULL,
        [S1] INT NULL DEFAULT (NULL),
        [S2] INT NULL DEFAULT (NULL),
        [S3] INT NULL DEFAULT (NULL),
        [S4] INT NULL DEFAULT (NULL),
        [S5] INT NULL DEFAULT (NULL),
        [S6] INT NULL DEFAULT (NULL),
        [T1] INT NULL,
        [T2] INT NULL,
        [DataGeracao] DATETIME NULL DEFAULT (getdate()),
        CONSTRAINT [PK_Resultados_MaisMilionaria] PRIMARY KEY ([Concurso])
    );
    PRINT 'Tabela Resultados_MaisMilionaria criada.';
END
ELSE PRINT 'Tabela Resultados_MaisMilionaria ja existe.';
GO

PRINT '01_core_tables.sql concluido.';
GO