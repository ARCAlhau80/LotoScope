-- ============================================================================
-- LotoScope - 03_procedures_triggers.sql
-- Procedures/triggers essenciais para atualizacao de acertos e ciclos.
-- Requer o 01_core_tables.sql aplicado antes.
-- SQL Server 2016+ (CREATE OR ALTER).
-- ============================================================================

USE LOTOFACIL;
GO

-- ===== AtualizaNumerosCiclos =====
CREATE OR ALTER PROCEDURE [dbo].[AtualizaNumerosCiclos]
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @UltimoCiclo INT, @UltimoConcursoFechamento INT, @NovoCiclo INT, @NovoConcursoInicio INT;

    -- 1. Identificar o último ciclo fechado
    SELECT TOP 1 
        @UltimoCiclo = Ciclo,
        @UltimoConcursoFechamento = ConcursoFechamento
    FROM [dbo].[NumerosCiclos]
    WHERE ConcursoFechamento IS NOT NULL
    ORDER BY Ciclo DESC;

    -- 2. Definir o novo ciclo e concurso de início
    SET @NovoCiclo = ISNULL(@UltimoCiclo, 0) + 1;
    SET @NovoConcursoInicio = ISNULL(@UltimoConcursoFechamento, (SELECT MIN(Concurso) FROM [dbo].[Resultados_INT])) + 1;

    -- 3. Verificar se já existe ciclo aberto para esse início
    IF NOT EXISTS (SELECT 1 FROM [dbo].[NumerosCiclos] WHERE Ciclo = @NovoCiclo AND ConcursoInicio = @NovoConcursoInicio)
    BEGIN
        INSERT INTO [dbo].[NumerosCiclos] (Ciclo, Numero, QtdSorteados, ConcursoInicio, DataInicio)
        SELECT @NovoCiclo, Numero, 0, @NovoConcursoInicio, GETDATE()
        FROM (SELECT DISTINCT CONVERT(INT, Value) AS Numero 
              FROM STRING_SPLIT('01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25', ',')) AS N;
    END

    -- FIX: Resetar QtdSorteados do ciclo aberto ANTES de reprocessar
    -- Garante idempotência: N chamadas = mesmo resultado
    UPDATE [dbo].[NumerosCiclos]
    SET QtdSorteados = 0
    WHERE Ciclo = @NovoCiclo
      AND ConcursoFechamento IS NULL;

    -- 4. Processar concursos do ciclo aberto
    DECLARE @ConcursoAtual INT, @DataSorteio DATETIME;
    DECLARE @Num1 INT, @Num2 INT, @Num3 INT, @Num4 INT, @Num5 INT, @Num6 INT, @Num7 INT, @Num8 INT, @Num9 INT, @Num10 INT;
    DECLARE @Num11 INT, @Num12 INT, @Num13 INT, @Num14 INT, @Num15 INT;

    DECLARE Cur CURSOR FOR
    SELECT Concurso, Data_sorteio, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, 
           N11, N12, N13, N14, N15
    FROM [dbo].[Resultados_INT]
    WHERE Concurso >= @NovoConcursoInicio
    ORDER BY Concurso;

    OPEN Cur;
    FETCH NEXT FROM Cur INTO @ConcursoAtual, @DataSorteio, @Num1, @Num2, @Num3, @Num4, @Num5, @Num6, @Num7, @Num8, @Num9, @Num10, 
                            @Num11, @Num12, @Num13, @Num14, @Num15;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num1;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num2;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num3;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num4;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num5;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num6;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num7;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num8;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num9;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num10;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num11;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num12;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num13;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num14;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num15;

        -- Verificar se todos os 25 números já foram sorteados
        IF (SELECT COUNT(*) FROM [dbo].[NumerosCiclos] WHERE Ciclo = @NovoCiclo AND QtdSorteados > 0) = 25
        BEGIN
            UPDATE [dbo].[NumerosCiclos]
            SET ConcursoFechamento = @ConcursoAtual, 
                DataFim = @DataSorteio
            WHERE Ciclo = @NovoCiclo;

            BREAK;
        END

        FETCH NEXT FROM Cur INTO @ConcursoAtual, @DataSorteio, @Num1, @Num2, @Num3, @Num4, @Num5, @Num6, @Num7, @Num8, @Num9, @Num10, 
                                @Num11, @Num12, @Num13, @Num14, @Num15;
    END

    CLOSE Cur;
    DEALLOCATE Cur;
END
GO

-- ===== sp_AtualizarAcertos_LF15 =====
-- =====================================================
-- ðŸ“¦ Criar procedure
-- =====================================================
CREATE OR ALTER PROCEDURE sp_AtualizarAcertos_LF15
    @Concurso INT = NULL,
    @VerboseMode BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @DataInicio DATETIME = GETDATE();
    DECLARE @ConcursoAtual INT;
    DECLARE @N1 INT, @N2 INT, @N3 INT, @N4 INT, @N5 INT;
    DECLARE @N6 INT, @N7 INT, @N8 INT, @N9 INT, @N10 INT;
    DECLARE @N11 INT, @N12 INT, @N13 INT, @N14 INT, @N15 INT;
    DECLARE @UltimoAtualizado INT;
    DECLARE @TotalConcursos INT = 0;
    DECLARE @QtdAfetadas_11 INT, @QtdAfetadas_12 INT, @QtdAfetadas_13 INT;
    DECLARE @QtdAfetadas_14 INT, @QtdAfetadas_15 INT;
    
    -- Determinar concursos a processar
    IF @Concurso IS NULL
    BEGIN
        SELECT @UltimoAtualizado = ISNULL(MIN(UltimoConcursoAtualizado), 0)
        FROM COMBINACOES_LOTOFACIL;
        
        IF @VerboseMode = 1
            PRINT 'ðŸ“ Modo incremental - Ãšltimo atualizado: ' + CAST(@UltimoAtualizado AS VARCHAR(10));
    END
    ELSE
    BEGIN
        IF @VerboseMode = 1
            PRINT 'ðŸ“ Modo concurso especÃ­fico: ' + CAST(@Concurso AS VARCHAR(10));
    END
    
    -- Cursor para processar concursos
    DECLARE curConcursos CURSOR LOCAL FAST_FORWARD FOR
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        WHERE (@Concurso IS NOT NULL AND Concurso = @Concurso)
           OR (@Concurso IS NULL AND Concurso > @UltimoAtualizado)
        ORDER BY Concurso ASC;
    
    OPEN curConcursos;
    
    FETCH NEXT FROM curConcursos INTO 
        @ConcursoAtual, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @TotalConcursos = @TotalConcursos + 1;
        
        -- ACERTOS 15 (combinaÃ§Ã£o = sorteio)
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_15 = Acertos_15 + 1, Ultimo_Acertos_15 = @ConcursoAtual
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 15;
        SET @QtdAfetadas_15 = @@ROWCOUNT;
        
        -- ACERTOS 14
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_14 = Acertos_14 + 1, Ultimo_Acertos_14 = @ConcursoAtual
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 14;
        SET @QtdAfetadas_14 = @@ROWCOUNT;
        
        -- ACERTOS 13
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_13 = Acertos_13 + 1, Ultimo_Acertos_13 = @ConcursoAtual
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 13;
        SET @QtdAfetadas_13 = @@ROWCOUNT;
        
        -- ACERTOS 12
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_12 = Acertos_12 + 1, Ultimo_Acertos_12 = @ConcursoAtual
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 12;
        SET @QtdAfetadas_12 = @@ROWCOUNT;
        
        -- ACERTOS 11
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_11 = Acertos_11 + 1, Ultimo_Acertos_11 = @ConcursoAtual
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 11;
        SET @QtdAfetadas_11 = @@ROWCOUNT;
        
        -- ATUALIZAR CONTROLE
        UPDATE COMBINACOES_LOTOFACIL
        SET UltimoConcursoAtualizado = @ConcursoAtual
        WHERE UltimoConcursoAtualizado < @ConcursoAtual;
        
        IF @VerboseMode = 1 AND @TotalConcursos % 100 = 0
            PRINT '   Processados: ' + CAST(@TotalConcursos AS VARCHAR) + ' concursos...';
        
        FETCH NEXT FROM curConcursos INTO 
            @ConcursoAtual, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    END
    
    CLOSE curConcursos;
    DEALLOCATE curConcursos;
    
    -- RelatÃ³rio
    DECLARE @TempoTotal INT = DATEDIFF(SECOND, @DataInicio, GETDATE());
    
    PRINT '';
    PRINT 'â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•';
    PRINT 'ðŸ“‹ RELATÃ“RIO - COMBINACOES_LOTOFACIL';
    PRINT 'â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•';
    PRINT 'âœ… Concursos processados: ' + CAST(@TotalConcursos AS VARCHAR);
    PRINT 'â±ï¸ Tempo total: ' + CAST(@TempoTotal AS VARCHAR) + ' segundos';
    PRINT 'â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•';
END
GO

-- ===== trg_AtualizarAcertos_LF15_AfterInsert =====
-- =====================================================
-- ðŸ“¦ Criar trigger
-- =====================================================
CREATE OR ALTER TRIGGER trg_AtualizarAcertos_LF15_AfterInsert
ON Resultados_INT
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Verificar se tabela existe
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL')
        RETURN;
    
    -- Verificar se colunas existem
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Acertos_15')
        RETURN;
    
    DECLARE @Concurso INT;
    DECLARE @N1 INT, @N2 INT, @N3 INT, @N4 INT, @N5 INT;
    DECLARE @N6 INT, @N7 INT, @N8 INT, @N9 INT, @N10 INT;
    DECLARE @N11 INT, @N12 INT, @N13 INT, @N14 INT, @N15 INT;
    
    DECLARE curInseridos CURSOR LOCAL FAST_FORWARD FOR
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM inserted
        ORDER BY Concurso ASC;
    
    OPEN curInseridos;
    
    FETCH NEXT FROM curInseridos INTO 
        @Concurso, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- ACERTOS 15
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_15 = Acertos_15 + 1, Ultimo_Acertos_15 = @Concurso
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 15;
        
        -- ACERTOS 14
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_14 = Acertos_14 + 1, Ultimo_Acertos_14 = @Concurso
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 14;
        
        -- ACERTOS 13
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_13 = Acertos_13 + 1, Ultimo_Acertos_13 = @Concurso
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 13;
        
        -- ACERTOS 12
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_12 = Acertos_12 + 1, Ultimo_Acertos_12 = @Concurso
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 12;
        
        -- ACERTOS 11
        UPDATE COMBINACOES_LOTOFACIL
        SET Acertos_11 = Acertos_11 + 1, Ultimo_Acertos_11 = @Concurso
        WHERE (SELECT COUNT(*) FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS comb(numero)
               WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)) = 11;
        
        -- CONTROLE
        UPDATE COMBINACOES_LOTOFACIL
        SET UltimoConcursoAtualizado = @Concurso
        WHERE UltimoConcursoAtualizado < @Concurso;
        
        FETCH NEXT FROM curInseridos INTO 
            @Concurso, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    END
    
    CLOSE curInseridos;
    DEALLOCATE curInseridos;
END
GO

-- ===== sp_AtualizarAcertos =====
-- =====================================================
-- ðŸ“¦ Criar procedure principal
-- =====================================================
CREATE OR ALTER PROCEDURE sp_AtualizarAcertos
    @Concurso INT = NULL,
    @VerboseMode BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @DataInicio DATETIME = GETDATE();
    DECLARE @ConcursoAtual INT;
    DECLARE @N1 INT, @N2 INT, @N3 INT, @N4 INT, @N5 INT;
    DECLARE @N6 INT, @N7 INT, @N8 INT, @N9 INT, @N10 INT;
    DECLARE @N11 INT, @N12 INT, @N13 INT, @N14 INT, @N15 INT;
    DECLARE @UltimoAtualizado INT;
    DECLARE @TotalConcursos INT = 0;
    DECLARE @QtdAfetadas_11 INT, @QtdAfetadas_12 INT, @QtdAfetadas_13 INT;
    DECLARE @QtdAfetadas_14 INT, @QtdAfetadas_15 INT;
    
    -- =====================================================
    -- ðŸ“ DETERMINAR CONCURSOS A PROCESSAR
    -- =====================================================
    
    IF @Concurso IS NOT NULL
    BEGIN
        -- Modo: Concurso especÃ­fico
        IF @VerboseMode = 1
            PRINT 'ðŸ“ Modo: Concurso especÃ­fico - ' + CAST(@Concurso AS VARCHAR(10));
    END
    ELSE
    BEGIN
        -- Modo: Todos os pendentes
        SELECT @UltimoAtualizado = ISNULL(MIN(UltimoConcursoAtualizado), 0)
        FROM COMBINACOES_LOTOFACIL20_COMPLETO;
        
        IF @VerboseMode = 1
        BEGIN
            PRINT 'ðŸ“ Modo: AtualizaÃ§Ã£o incremental';
            PRINT 'ðŸ“Š Ãšltimo concurso atualizado: ' + CAST(@UltimoAtualizado AS VARCHAR(10));
        END
    END
    
    -- =====================================================
    -- ðŸ”„ CURSOR PARA PROCESSAR CONCURSOS
    -- =====================================================
    
    DECLARE curConcursos CURSOR LOCAL FAST_FORWARD FOR
        SELECT 
            Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        WHERE (@Concurso IS NOT NULL AND Concurso = @Concurso)
           OR (@Concurso IS NULL AND Concurso > @UltimoAtualizado)
        ORDER BY Concurso ASC;
    
    OPEN curConcursos;
    
    FETCH NEXT FROM curConcursos INTO 
        @ConcursoAtual, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @TotalConcursos = @TotalConcursos + 1;
        
        IF @VerboseMode = 1
            PRINT '';
            PRINT 'ðŸ”„ Processando Concurso ' + CAST(@ConcursoAtual AS VARCHAR(10)) + 
                  ' | NÃºmeros: ' + CAST(@N1 AS VARCHAR) + ',' + CAST(@N2 AS VARCHAR) + ',' + 
                  CAST(@N3 AS VARCHAR) + ',' + CAST(@N4 AS VARCHAR) + ',' + CAST(@N5 AS VARCHAR) + ',' +
                  CAST(@N6 AS VARCHAR) + ',' + CAST(@N7 AS VARCHAR) + ',' + CAST(@N8 AS VARCHAR) + ',' +
                  CAST(@N9 AS VARCHAR) + ',' + CAST(@N10 AS VARCHAR) + ',' + CAST(@N11 AS VARCHAR) + ',' +
                  CAST(@N12 AS VARCHAR) + ',' + CAST(@N13 AS VARCHAR) + ',' + CAST(@N14 AS VARCHAR) + ',' +
                  CAST(@N15 AS VARCHAR);
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 15
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_15 = Acertos_15 + 1,
            Ultimo_Acertos_15 = @ConcursoAtual
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 15;
        
        SET @QtdAfetadas_15 = @@ROWCOUNT;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 14
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_14 = Acertos_14 + 1,
            Ultimo_Acertos_14 = @ConcursoAtual
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 14;
        
        SET @QtdAfetadas_14 = @@ROWCOUNT;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 13
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_13 = Acertos_13 + 1,
            Ultimo_Acertos_13 = @ConcursoAtual
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 13;
        
        SET @QtdAfetadas_13 = @@ROWCOUNT;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 12
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_12 = Acertos_12 + 1,
            Ultimo_Acertos_12 = @ConcursoAtual
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 12;
        
        SET @QtdAfetadas_12 = @@ROWCOUNT;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 11
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_11 = Acertos_11 + 1,
            Ultimo_Acertos_11 = @ConcursoAtual
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 11;
        
        SET @QtdAfetadas_11 = @@ROWCOUNT;
        
        -- =====================================================
        -- ðŸ”„ ATUALIZAR CONTROLE
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET UltimoConcursoAtualizado = @ConcursoAtual
        WHERE UltimoConcursoAtualizado < @ConcursoAtual;
        
        IF @VerboseMode = 1
        BEGIN
            PRINT '   âœ… 15 acertos: ' + CAST(@QtdAfetadas_15 AS VARCHAR) + 
                  ' | 14 acertos: ' + CAST(@QtdAfetadas_14 AS VARCHAR) +
                  ' | 13 acertos: ' + CAST(@QtdAfetadas_13 AS VARCHAR) +
                  ' | 12 acertos: ' + CAST(@QtdAfetadas_12 AS VARCHAR) +
                  ' | 11 acertos: ' + CAST(@QtdAfetadas_11 AS VARCHAR);
        END
        
        FETCH NEXT FROM curConcursos INTO 
            @ConcursoAtual, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    END
    
    CLOSE curConcursos;
    DEALLOCATE curConcursos;
    
    -- =====================================================
    -- ðŸ“‹ RELATÃ“RIO FINAL
    -- =====================================================
    DECLARE @TempoTotal INT = DATEDIFF(SECOND, @DataInicio, GETDATE());
    
    PRINT '';
    PRINT 'â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•';
    PRINT 'ðŸ“‹ RELATÃ“RIO FINAL';
    PRINT 'â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•';
    PRINT 'âœ… Concursos processados: ' + CAST(@TotalConcursos AS VARCHAR);
    PRINT 'â±ï¸ Tempo total: ' + CAST(@TempoTotal AS VARCHAR) + ' segundos';
    PRINT 'â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•';
    
END
GO

-- ===== trg_AtualizarAcertos_AfterInsert =====
-- =====================================================
-- ðŸ“¦ Criar trigger
-- =====================================================
CREATE OR ALTER TRIGGER trg_AtualizarAcertos_AfterInsert
ON Resultados_INT
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- VariÃ¡veis
    DECLARE @Concurso INT;
    DECLARE @N1 INT, @N2 INT, @N3 INT, @N4 INT, @N5 INT;
    DECLARE @N6 INT, @N7 INT, @N8 INT, @N9 INT, @N10 INT;
    DECLARE @N11 INT, @N12 INT, @N13 INT, @N14 INT, @N15 INT;
    DECLARE @QtdTotal INT = 0;
    
    -- =====================================================
    -- ðŸ“ VERIFICAR SE TABELA COMBINACOES EXISTE
    -- =====================================================
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO')
    BEGIN
        -- Tabela nÃ£o existe, nÃ£o fazer nada
        RETURN;
    END
    
    -- =====================================================
    -- ðŸ”„ PROCESSAR CADA CONCURSO INSERIDO
    -- =====================================================
    DECLARE curInseridos CURSOR LOCAL FAST_FORWARD FOR
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM inserted
        ORDER BY Concurso ASC;
    
    OPEN curInseridos;
    
    FETCH NEXT FROM curInseridos INTO 
        @Concurso, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @QtdTotal = @QtdTotal + 1;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 15 (JACKPOT)
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_15 = Acertos_15 + 1,
            Ultimo_Acertos_15 = @Concurso
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 15;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 14
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_14 = Acertos_14 + 1,
            Ultimo_Acertos_14 = @Concurso
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 14;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 13
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_13 = Acertos_13 + 1,
            Ultimo_Acertos_13 = @Concurso
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 13;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 12
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_12 = Acertos_12 + 1,
            Ultimo_Acertos_12 = @Concurso
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 12;
        
        -- =====================================================
        -- ðŸŽ¯ ATUALIZAR ACERTOS 11
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET 
            Acertos_11 = Acertos_11 + 1,
            Ultimo_Acertos_11 = @Concurso
        WHERE (
            SELECT COUNT(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN (@N1,@N2,@N3,@N4,@N5,@N6,@N7,@N8,@N9,@N10,@N11,@N12,@N13,@N14,@N15)
        ) = 11;
        
        -- =====================================================
        -- ðŸ”„ ATUALIZAR CONTROLE
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET UltimoConcursoAtualizado = @Concurso
        WHERE UltimoConcursoAtualizado < @Concurso;
        
        FETCH NEXT FROM curInseridos INTO 
            @Concurso, @N1, @N2, @N3, @N4, @N5, @N6, @N7, @N8, @N9, @N10, @N11, @N12, @N13, @N14, @N15;
    END
    
    CLOSE curInseridos;
    DEALLOCATE curInseridos;
    
    -- =====================================================
    -- ðŸ“ LOG DE PROCESSAMENTO (opcional)
    -- =====================================================
    IF @QtdTotal > 0
    BEGIN
        -- Registrar no log de controle
        IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'CONTROLE_PROCESSAMENTO_ACERTOS')
        BEGIN
            INSERT INTO CONTROLE_PROCESSAMENTO_ACERTOS (UltimoConcursoProcessado, TipoProcessamento)
            SELECT MAX(Concurso), 'TRIGGER_AUTO'
            FROM inserted;
        END
    END
    
END
GO

-- ===== SP_AtualizarCamposComparacao =====
CREATE OR ALTER PROCEDURE SP_AtualizarCamposComparacao(@ConcursoNovo INT = NULL)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Se não informar o concurso, pega o último automaticamente
    IF @ConcursoNovo IS NULL
    BEGIN
        SELECT @ConcursoNovo = MAX(Concurso) FROM RESULTADOS_INT;
    END
    
    -- Verificar se existe concurso anterior para comparar
    IF NOT EXISTS (SELECT 1 FROM RESULTADOS_INT WHERE Concurso = @ConcursoNovo - 1)
    BEGIN
        PRINT 'Não existe concurso anterior para comparar. Concurso: ' + CAST(@ConcursoNovo AS VARCHAR(10));
        RETURN;
    END
    
    -- Atualizar os campos de comparação para o concurso novo
    UPDATE r1 SET 
        menor_que_ultimo = (
            CASE WHEN r1.N1  < r2.N1  THEN 1 ELSE 0 END +
            CASE WHEN r1.N2  < r2.N2  THEN 1 ELSE 0 END +
            CASE WHEN r1.N3  < r2.N3  THEN 1 ELSE 0 END +
            CASE WHEN r1.N4  < r2.N4  THEN 1 ELSE 0 END +
            CASE WHEN r1.N5  < r2.N5  THEN 1 ELSE 0 END +
            CASE WHEN r1.N6  < r2.N6  THEN 1 ELSE 0 END +
            CASE WHEN r1.N7  < r2.N7  THEN 1 ELSE 0 END +
            CASE WHEN r1.N8  < r2.N8  THEN 1 ELSE 0 END +
            CASE WHEN r1.N9  < r2.N9  THEN 1 ELSE 0 END +
            CASE WHEN r1.N10 < r2.N10 THEN 1 ELSE 0 END +
            CASE WHEN r1.N11 < r2.N11 THEN 1 ELSE 0 END +
            CASE WHEN r1.N12 < r2.N12 THEN 1 ELSE 0 END +
            CASE WHEN r1.N13 < r2.N13 THEN 1 ELSE 0 END +
            CASE WHEN r1.N14 < r2.N14 THEN 1 ELSE 0 END +
            CASE WHEN r1.N15 < r2.N15 THEN 1 ELSE 0 END
        ),
        maior_que_ultimo = (
            CASE WHEN r1.N1  > r2.N1  THEN 1 ELSE 0 END +
            CASE WHEN r1.N2  > r2.N2  THEN 1 ELSE 0 END +
            CASE WHEN r1.N3  > r2.N3  THEN 1 ELSE 0 END +
            CASE WHEN r1.N4  > r2.N4  THEN 1 ELSE 0 END +
            CASE WHEN r1.N5  > r2.N5  THEN 1 ELSE 0 END +
            CASE WHEN r1.N6  > r2.N6  THEN 1 ELSE 0 END +
            CASE WHEN r1.N7  > r2.N7  THEN 1 ELSE 0 END +
            CASE WHEN r1.N8  > r2.N8  THEN 1 ELSE 0 END +
            CASE WHEN r1.N9  > r2.N9  THEN 1 ELSE 0 END +
            CASE WHEN r1.N10 > r2.N10 THEN 1 ELSE 0 END +
            CASE WHEN r1.N11 > r2.N11 THEN 1 ELSE 0 END +
            CASE WHEN r1.N12 > r2.N12 THEN 1 ELSE 0 END +
            CASE WHEN r1.N13 > r2.N13 THEN 1 ELSE 0 END +
            CASE WHEN r1.N14 > r2.N14 THEN 1 ELSE 0 END +
            CASE WHEN r1.N15 > r2.N15 THEN 1 ELSE 0 END
        ),
        igual_ao_ultimo = (
            CASE WHEN r1.N1  = r2.N1  THEN 1 ELSE 0 END +
            CASE WHEN r1.N2  = r2.N2  THEN 1 ELSE 0 END +
            CASE WHEN r1.N3  = r2.N3  THEN 1 ELSE 0 END +
            CASE WHEN r1.N4  = r2.N4  THEN 1 ELSE 0 END +
            CASE WHEN r1.N5  = r2.N5  THEN 1 ELSE 0 END +
            CASE WHEN r1.N6  = r2.N6  THEN 1 ELSE 0 END +
            CASE WHEN r1.N7  = r2.N7  THEN 1 ELSE 0 END +
            CASE WHEN r1.N8  = r2.N8  THEN 1 ELSE 0 END +
            CASE WHEN r1.N9  = r2.N9  THEN 1 ELSE 0 END +
            CASE WHEN r1.N10 = r2.N10 THEN 1 ELSE 0 END +
            CASE WHEN r1.N11 = r2.N11 THEN 1 ELSE 0 END +
            CASE WHEN r1.N12 = r2.N12 THEN 1 ELSE 0 END +
            CASE WHEN r1.N13 = r2.N13 THEN 1 ELSE 0 END +
            CASE WHEN r1.N14 = r2.N14 THEN 1 ELSE 0 END +
            CASE WHEN r1.N15 = r2.N15 THEN 1 ELSE 0 END
        )
    FROM RESULTADOS_INT r1
    INNER JOIN RESULTADOS_INT r2 ON r1.Concurso = r2.Concurso + 1
    WHERE r1.Concurso = @ConcursoNovo;
    
    PRINT 'Campos de comparação atualizados para o concurso: ' + CAST(@ConcursoNovo AS VARCHAR(10));
END
GO

-- ===== SP_AtualizarCombinacoesComparacao =====
CREATE OR ALTER PROCEDURE [dbo].[SP_AtualizarCombinacoesComparacao](@ConcursoReferencia INT = NULL)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Se não informar o concurso, pega o último automaticamente
    IF @ConcursoReferencia IS NULL
    BEGIN
        SELECT @ConcursoReferencia = MAX(Concurso) FROM RESULTADOS_INT;
    END
    
    -- Verificar se o concurso existe
    IF NOT EXISTS (SELECT 1 FROM RESULTADOS_INT WHERE Concurso = @ConcursoReferencia)
    BEGIN
        PRINT 'Concurso não encontrado: ' + CAST(@ConcursoReferencia AS VARCHAR(10));
        RETURN;
    END
    
    -- Atualizar todas as combinações comparando com o concurso de referência
    UPDATE c SET 
        menor_que_ultimo = (
            CASE WHEN c.N1  < r.N1  THEN 1 ELSE 0 END +
            CASE WHEN c.N2  < r.N2  THEN 1 ELSE 0 END +
            CASE WHEN c.N3  < r.N3  THEN 1 ELSE 0 END +
            CASE WHEN c.N4  < r.N4  THEN 1 ELSE 0 END +
            CASE WHEN c.N5  < r.N5  THEN 1 ELSE 0 END +
            CASE WHEN c.N6  < r.N6  THEN 1 ELSE 0 END +
            CASE WHEN c.N7  < r.N7  THEN 1 ELSE 0 END +
            CASE WHEN c.N8  < r.N8  THEN 1 ELSE 0 END +
            CASE WHEN c.N9  < r.N9  THEN 1 ELSE 0 END +
            CASE WHEN c.N10 < r.N10 THEN 1 ELSE 0 END +
            CASE WHEN c.N11 < r.N11 THEN 1 ELSE 0 END +
            CASE WHEN c.N12 < r.N12 THEN 1 ELSE 0 END +
            CASE WHEN c.N13 < r.N13 THEN 1 ELSE 0 END +
            CASE WHEN c.N14 < r.N14 THEN 1 ELSE 0 END +
            CASE WHEN c.N15 < r.N15 THEN 1 ELSE 0 END
        ),
        maior_que_ultimo = (
            CASE WHEN c.N1  > r.N1  THEN 1 ELSE 0 END +
            CASE WHEN c.N2  > r.N2  THEN 1 ELSE 0 END +
            CASE WHEN c.N3  > r.N3  THEN 1 ELSE 0 END +
            CASE WHEN c.N4  > r.N4  THEN 1 ELSE 0 END +
            CASE WHEN c.N5  > r.N5  THEN 1 ELSE 0 END +
            CASE WHEN c.N6  > r.N6  THEN 1 ELSE 0 END +
            CASE WHEN c.N7  > r.N7  THEN 1 ELSE 0 END +
            CASE WHEN c.N8  > r.N8  THEN 1 ELSE 0 END +
            CASE WHEN c.N9  > r.N9  THEN 1 ELSE 0 END +
            CASE WHEN c.N10 > r.N10 THEN 1 ELSE 0 END +
            CASE WHEN c.N11 > r.N11 THEN 1 ELSE 0 END +
            CASE WHEN c.N12 > r.N12 THEN 1 ELSE 0 END +
            CASE WHEN c.N13 > r.N13 THEN 1 ELSE 0 END +
            CASE WHEN c.N14 > r.N14 THEN 1 ELSE 0 END +
            CASE WHEN c.N15 > r.N15 THEN 1 ELSE 0 END
        ),
        igual_ao_ultimo = (
            CASE WHEN c.N1  = r.N1  THEN 1 ELSE 0 END +
            CASE WHEN c.N2  = r.N2  THEN 1 ELSE 0 END +
            CASE WHEN c.N3  = r.N3  THEN 1 ELSE 0 END +
            CASE WHEN c.N4  = r.N4  THEN 1 ELSE 0 END +
            CASE WHEN c.N5  = r.N5  THEN 1 ELSE 0 END +
            CASE WHEN c.N6  = r.N6  THEN 1 ELSE 0 END +
            CASE WHEN c.N7  = r.N7  THEN 1 ELSE 0 END +
            CASE WHEN c.N8  = r.N8  THEN 1 ELSE 0 END +
            CASE WHEN c.N9  = r.N9  THEN 1 ELSE 0 END +
            CASE WHEN c.N10 = r.N10 THEN 1 ELSE 0 END +
            CASE WHEN c.N11 = r.N11 THEN 1 ELSE 0 END +
            CASE WHEN c.N12 = r.N12 THEN 1 ELSE 0 END +
            CASE WHEN c.N13 = r.N13 THEN 1 ELSE 0 END +
            CASE WHEN c.N14 = r.N14 THEN 1 ELSE 0 END +
            CASE WHEN c.N15 = r.N15 THEN 1 ELSE 0 END
        )
    FROM COMBINACOES_LOTOFACIL c
    CROSS JOIN RESULTADOS_INT r
    WHERE r.Concurso = @ConcursoReferencia;
    
    PRINT 'Combinações atualizadas com base no concurso: ' + CAST(@ConcursoReferencia AS VARCHAR(10));
END
GO

PRINT '03_procedures_triggers.sql concluido.';
GO