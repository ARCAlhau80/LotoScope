-- =====================================================
-- 🔧 TRIGGER PARA ATUALIZAÇÃO AUTOMÁTICA DE ACERTOS
-- =====================================================
-- Este trigger é executado AUTOMATICAMENTE após qualquer
-- INSERT na tabela Resultados_INT, processando os acertos
-- para os novos concursos.
--
-- COMPORTAMENTO:
-- - Dispara após INSERT na Resultados_INT
-- - Processa APENAS os concursos recém inseridos
-- - Atualiza Acertos_11 a Acertos_15
-- - Atualiza Ultimo_Acertos_11 a Ultimo_Acertos_15
-- - Atualiza UltimoConcursoAtualizado
--
-- Autor: AR CALHAU
-- Data: 15/02/2026
-- =====================================================

USE LOTOFACIL;
GO

-- =====================================================
-- 🗑️ Remover trigger se existir
-- =====================================================
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_AtualizarAcertos_AfterInsert')
BEGIN
    DROP TRIGGER trg_AtualizarAcertos_AfterInsert;
    PRINT '🗑️ Trigger existente removido';
END
GO

-- =====================================================
-- 📦 Criar trigger
-- =====================================================
CREATE TRIGGER trg_AtualizarAcertos_AfterInsert
ON Resultados_INT
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Variáveis
    DECLARE @Concurso INT;
    DECLARE @N1 INT, @N2 INT, @N3 INT, @N4 INT, @N5 INT;
    DECLARE @N6 INT, @N7 INT, @N8 INT, @N9 INT, @N10 INT;
    DECLARE @N11 INT, @N12 INT, @N13 INT, @N14 INT, @N15 INT;
    DECLARE @QtdTotal INT = 0;
    
    -- =====================================================
    -- 📍 VERIFICAR SE TABELA COMBINACOES EXISTE
    -- =====================================================
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO')
    BEGIN
        -- Tabela não existe, não fazer nada
        RETURN;
    END
    
    -- =====================================================
    -- 🔄 PROCESSAR CADA CONCURSO INSERIDO
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
        -- 🎯 ATUALIZAR ACERTOS 15 (JACKPOT)
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
        -- 🎯 ATUALIZAR ACERTOS 14
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
        -- 🎯 ATUALIZAR ACERTOS 13
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
        -- 🎯 ATUALIZAR ACERTOS 12
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
        -- 🎯 ATUALIZAR ACERTOS 11
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
        -- 🔄 ATUALIZAR CONTROLE
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
    -- 📝 LOG DE PROCESSAMENTO (opcional)
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

-- =====================================================
-- 📋 VERIFICAR CRIAÇÃO
-- =====================================================
PRINT '';
PRINT '✅ Trigger trg_AtualizarAcertos_AfterInsert criado com sucesso!';
PRINT '';
PRINT '📖 COMPORTAMENTO:';
PRINT '   • Dispara automaticamente após INSERT na Resultados_INT';
PRINT '   • Atualiza campos Acertos_11 a Acertos_15';
PRINT '   • Atualiza campos Ultimo_Acertos_11 a Ultimo_Acertos_15';
PRINT '   • Atualiza UltimoConcursoAtualizado';
PRINT '';
PRINT '⚠️ NOTA: O trigger pode aumentar o tempo de INSERT na Resultados_INT';
PRINT '   Se preferir controle manual, desabilite o trigger com:';
PRINT '   ALTER TABLE Resultados_INT DISABLE TRIGGER trg_AtualizarAcertos_AfterInsert';
GO

-- =====================================================
-- 📊 VERIFICAR STATUS DO TRIGGER
-- =====================================================
SELECT 
    name AS TriggerName,
    CASE WHEN is_disabled = 0 THEN '✅ ATIVO' ELSE '❌ DESABILITADO' END AS Status,
    create_date AS DataCriacao,
    modify_date AS UltimaModificacao
FROM sys.triggers 
WHERE name = 'trg_AtualizarAcertos_AfterInsert';
GO
