-- =====================================================
-- 🔧 ADICIONAR COLUNAS DE ÚLTIMO ACERTO E CONTROLE
-- =====================================================
-- Adiciona colunas para rastrear o último concurso onde 
-- ocorreu cada tipo de acerto (11, 12, 13, 14, 15)
-- e o campo de controle UltimoConcursoAtualizado
-- 
-- Autor: AR CALHAU
-- Data: 15/02/2026
-- =====================================================

USE LOTOFACIL;
GO

-- =====================================================
-- 📊 ÚLTIMO CONCURSO COM 11 ACERTOS
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Ultimo_Acertos_11')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Ultimo_Acertos_11 INT NULL;
    
    PRINT '✅ Coluna Ultimo_Acertos_11 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Ultimo_Acertos_11 já existe.';
END
GO

-- =====================================================
-- 📊 ÚLTIMO CONCURSO COM 12 ACERTOS
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Ultimo_Acertos_12')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Ultimo_Acertos_12 INT NULL;
    
    PRINT '✅ Coluna Ultimo_Acertos_12 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Ultimo_Acertos_12 já existe.';
END
GO

-- =====================================================
-- 📊 ÚLTIMO CONCURSO COM 13 ACERTOS
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Ultimo_Acertos_13')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Ultimo_Acertos_13 INT NULL;
    
    PRINT '✅ Coluna Ultimo_Acertos_13 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Ultimo_Acertos_13 já existe.';
END
GO

-- =====================================================
-- 📊 ÚLTIMO CONCURSO COM 14 ACERTOS
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Ultimo_Acertos_14')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Ultimo_Acertos_14 INT NULL;
    
    PRINT '✅ Coluna Ultimo_Acertos_14 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Ultimo_Acertos_14 já existe.';
END
GO

-- =====================================================
-- 📊 ÚLTIMO CONCURSO COM 15 ACERTOS (JACKPOT)
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Ultimo_Acertos_15')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Ultimo_Acertos_15 INT NULL;
    
    PRINT '✅ Coluna Ultimo_Acertos_15 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Ultimo_Acertos_15 já existe.';
END
GO

-- =====================================================
-- 🔄 CONTROLE DE ÚLTIMO CONCURSO ATUALIZADO
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'UltimoConcursoAtualizado')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD UltimoConcursoAtualizado INT DEFAULT 0 NOT NULL;
    
    PRINT '✅ Coluna UltimoConcursoAtualizado adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna UltimoConcursoAtualizado já existe.';
END
GO

-- =====================================================
-- 📊 CRIAR ÍNDICES PARA CONSULTAS RÁPIDAS
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Ultimo_15' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL20_COMPLETO'))
BEGIN
    CREATE INDEX IX_COMBINACOES20_Ultimo_15 ON COMBINACOES_LOTOFACIL20_COMPLETO(Ultimo_Acertos_15);
    PRINT '✅ Índice IX_COMBINACOES20_Ultimo_15 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Ultimo_14' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL20_COMPLETO'))
BEGIN
    CREATE INDEX IX_COMBINACOES20_Ultimo_14 ON COMBINACOES_LOTOFACIL20_COMPLETO(Ultimo_Acertos_14);
    PRINT '✅ Índice IX_COMBINACOES20_Ultimo_14 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_UltimoAtualizado' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL20_COMPLETO'))
BEGIN
    CREATE INDEX IX_COMBINACOES20_UltimoAtualizado ON COMBINACOES_LOTOFACIL20_COMPLETO(UltimoConcursoAtualizado);
    PRINT '✅ Índice IX_COMBINACOES20_UltimoAtualizado criado!';
END
GO

-- =====================================================
-- 📋 VERIFICAR ESTRUTURA FINAL
-- =====================================================
PRINT '';
PRINT '📋 ESTRUTURA DAS NOVAS COLUNAS:';
PRINT '=====================================';

SELECT 
    COLUMN_NAME AS Coluna,
    DATA_TYPE AS Tipo,
    IS_NULLABLE AS Nulo,
    COLUMN_DEFAULT AS Padrao
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
AND COLUMN_NAME IN ('Ultimo_Acertos_11', 'Ultimo_Acertos_12', 'Ultimo_Acertos_13', 
                    'Ultimo_Acertos_14', 'Ultimo_Acertos_15', 'UltimoConcursoAtualizado')
ORDER BY COLUMN_NAME;

PRINT '';
PRINT '🎯 Colunas de rastreamento de último acerto configuradas!';
PRINT '✅ Sistema pronto para atualização incremental inteligente!';
GO
