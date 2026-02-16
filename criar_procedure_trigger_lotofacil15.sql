-- =====================================================
-- 🔧 PROCEDURE E TRIGGER - COMBINACOES_LOTOFACIL (15 números)
-- =====================================================
-- Stored procedure e trigger para atualização automática
-- de acertos na tabela de combinações de 15 números.
--
-- Autor: AR CALHAU
-- Data: 15/02/2026
-- =====================================================

USE LOTOFACIL;
GO

-- =====================================================
-- 🗑️ Remover procedure se existir
-- =====================================================
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_AtualizarAcertos_LF15')
BEGIN
    DROP PROCEDURE sp_AtualizarAcertos_LF15;
    PRINT '🗑️ Procedure sp_AtualizarAcertos_LF15 removida';
END
GO

-- =====================================================
-- 📦 Criar procedure
-- =====================================================
CREATE PROCEDURE sp_AtualizarAcertos_LF15
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
            PRINT '📍 Modo incremental - Último atualizado: ' + CAST(@UltimoAtualizado AS VARCHAR(10));
    END
    ELSE
    BEGIN
        IF @VerboseMode = 1
            PRINT '📍 Modo concurso específico: ' + CAST(@Concurso AS VARCHAR(10));
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
        
        -- ACERTOS 15 (combinação = sorteio)
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
    
    -- Relatório
    DECLARE @TempoTotal INT = DATEDIFF(SECOND, @DataInicio, GETDATE());
    
    PRINT '';
    PRINT '═══════════════════════════════════════════════════════════════';
    PRINT '📋 RELATÓRIO - COMBINACOES_LOTOFACIL';
    PRINT '═══════════════════════════════════════════════════════════════';
    PRINT '✅ Concursos processados: ' + CAST(@TotalConcursos AS VARCHAR);
    PRINT '⏱️ Tempo total: ' + CAST(@TempoTotal AS VARCHAR) + ' segundos';
    PRINT '═══════════════════════════════════════════════════════════════';
END
GO

PRINT '';
PRINT '✅ Procedure sp_AtualizarAcertos_LF15 criada!';
GO

-- =====================================================
-- 🗑️ Remover trigger se existir
-- =====================================================
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_AtualizarAcertos_LF15_AfterInsert')
BEGIN
    DROP TRIGGER trg_AtualizarAcertos_LF15_AfterInsert;
    PRINT '🗑️ Trigger existente removido';
END
GO

-- =====================================================
-- 📦 Criar trigger
-- =====================================================
CREATE TRIGGER trg_AtualizarAcertos_LF15_AfterInsert
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

PRINT '';
PRINT '✅ Trigger trg_AtualizarAcertos_LF15_AfterInsert criado!';
PRINT '';
PRINT '📖 USO:';
PRINT '   EXEC sp_AtualizarAcertos_LF15                -- Todos pendentes';
PRINT '   EXEC sp_AtualizarAcertos_LF15 @Concurso=3615 -- Concurso específico';
GO

-- Verificar triggers
SELECT 
    name AS TriggerName,
    CASE WHEN is_disabled = 0 THEN '✅ ATIVO' ELSE '❌ DESABILITADO' END AS Status
FROM sys.triggers 
WHERE name LIKE '%AtualizarAcertos%';
GO
