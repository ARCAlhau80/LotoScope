-- =====================================================
-- 🔧 STORED PROCEDURE PARA ATUALIZAÇÃO DE ACERTOS
-- =====================================================
-- Esta procedure atualiza os campos de acertos para um
-- concurso específico ou processa todos os pendentes.
--
-- MODOS DE USO:
--   EXEC sp_AtualizarAcertos @Concurso = 3615  -- Concurso específico
--   EXEC sp_AtualizarAcertos                   -- Todos pendentes
--
-- Autor: AR CALHAU
-- Data: 15/02/2026
-- =====================================================

USE LOTOFACIL;
GO

-- =====================================================
-- 🗑️ Remover procedure se existir
-- =====================================================
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_AtualizarAcertos')
BEGIN
    DROP PROCEDURE sp_AtualizarAcertos;
    PRINT '🗑️ Procedure existente removida';
END
GO

-- =====================================================
-- 📦 Criar procedure principal
-- =====================================================
CREATE PROCEDURE sp_AtualizarAcertos
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
    -- 📍 DETERMINAR CONCURSOS A PROCESSAR
    -- =====================================================
    
    IF @Concurso IS NOT NULL
    BEGIN
        -- Modo: Concurso específico
        IF @VerboseMode = 1
            PRINT '📍 Modo: Concurso específico - ' + CAST(@Concurso AS VARCHAR(10));
    END
    ELSE
    BEGIN
        -- Modo: Todos os pendentes
        SELECT @UltimoAtualizado = ISNULL(MIN(UltimoConcursoAtualizado), 0)
        FROM COMBINACOES_LOTOFACIL20_COMPLETO;
        
        IF @VerboseMode = 1
        BEGIN
            PRINT '📍 Modo: Atualização incremental';
            PRINT '📊 Último concurso atualizado: ' + CAST(@UltimoAtualizado AS VARCHAR(10));
        END
    END
    
    -- =====================================================
    -- 🔄 CURSOR PARA PROCESSAR CONCURSOS
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
            PRINT '🔄 Processando Concurso ' + CAST(@ConcursoAtual AS VARCHAR(10)) + 
                  ' | Números: ' + CAST(@N1 AS VARCHAR) + ',' + CAST(@N2 AS VARCHAR) + ',' + 
                  CAST(@N3 AS VARCHAR) + ',' + CAST(@N4 AS VARCHAR) + ',' + CAST(@N5 AS VARCHAR) + ',' +
                  CAST(@N6 AS VARCHAR) + ',' + CAST(@N7 AS VARCHAR) + ',' + CAST(@N8 AS VARCHAR) + ',' +
                  CAST(@N9 AS VARCHAR) + ',' + CAST(@N10 AS VARCHAR) + ',' + CAST(@N11 AS VARCHAR) + ',' +
                  CAST(@N12 AS VARCHAR) + ',' + CAST(@N13 AS VARCHAR) + ',' + CAST(@N14 AS VARCHAR) + ',' +
                  CAST(@N15 AS VARCHAR);
        
        -- =====================================================
        -- 🎯 ATUALIZAR ACERTOS 15
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
        -- 🎯 ATUALIZAR ACERTOS 14
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
        -- 🎯 ATUALIZAR ACERTOS 13
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
        -- 🎯 ATUALIZAR ACERTOS 12
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
        -- 🎯 ATUALIZAR ACERTOS 11
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
        -- 🔄 ATUALIZAR CONTROLE
        -- =====================================================
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET UltimoConcursoAtualizado = @ConcursoAtual
        WHERE UltimoConcursoAtualizado < @ConcursoAtual;
        
        IF @VerboseMode = 1
        BEGIN
            PRINT '   ✅ 15 acertos: ' + CAST(@QtdAfetadas_15 AS VARCHAR) + 
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
    -- 📋 RELATÓRIO FINAL
    -- =====================================================
    DECLARE @TempoTotal INT = DATEDIFF(SECOND, @DataInicio, GETDATE());
    
    PRINT '';
    PRINT '═══════════════════════════════════════════════════════════════';
    PRINT '📋 RELATÓRIO FINAL';
    PRINT '═══════════════════════════════════════════════════════════════';
    PRINT '✅ Concursos processados: ' + CAST(@TotalConcursos AS VARCHAR);
    PRINT '⏱️ Tempo total: ' + CAST(@TempoTotal AS VARCHAR) + ' segundos';
    PRINT '═══════════════════════════════════════════════════════════════';
    
END
GO

-- =====================================================
-- 📋 VERIFICAR CRIAÇÃO
-- =====================================================
PRINT '';
PRINT '✅ Procedure sp_AtualizarAcertos criada com sucesso!';
PRINT '';
PRINT '📖 MODOS DE USO:';
PRINT '   EXEC sp_AtualizarAcertos @Concurso = 3615  -- Concurso específico';
PRINT '   EXEC sp_AtualizarAcertos                   -- Todos pendentes';
PRINT '   EXEC sp_AtualizarAcertos @VerboseMode = 0  -- Silencioso';
GO
