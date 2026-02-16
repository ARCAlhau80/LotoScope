-- =====================================================
-- 🔧 ADICIONAR COLUNAS DE ACERTOS - COMBINACOES_LOTOFACIL (15 números)
-- =====================================================
-- Adiciona as colunas de contagem de acertos (11-15),
-- último concurso de cada acerto, e controle incremental.
--
-- Autor: AR CALHAU
-- Data: 15/02/2026
-- =====================================================

USE LOTOFACIL;
GO

-- =====================================================
-- 🎯 COLUNAS DE CONTAGEM DE ACERTOS
-- =====================================================

-- Acertos 15 (PRÊMIO MÁXIMO - JACKPOT)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Acertos_15')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Acertos_15 INT DEFAULT 0 NOT NULL;
    PRINT '✅ Coluna Acertos_15 adicionada!';
END
ELSE PRINT '⚠️ Coluna Acertos_15 já existe.';
GO

-- Acertos 14
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Acertos_14')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Acertos_14 INT DEFAULT 0 NOT NULL;
    PRINT '✅ Coluna Acertos_14 adicionada!';
END
ELSE PRINT '⚠️ Coluna Acertos_14 já existe.';
GO

-- Acertos 13
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Acertos_13')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Acertos_13 INT DEFAULT 0 NOT NULL;
    PRINT '✅ Coluna Acertos_13 adicionada!';
END
ELSE PRINT '⚠️ Coluna Acertos_13 já existe.';
GO

-- Acertos 12
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Acertos_12')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Acertos_12 INT DEFAULT 0 NOT NULL;
    PRINT '✅ Coluna Acertos_12 adicionada!';
END
ELSE PRINT '⚠️ Coluna Acertos_12 já existe.';
GO

-- Acertos 11 (PRÊMIO MÍNIMO)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Acertos_11')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Acertos_11 INT DEFAULT 0 NOT NULL;
    PRINT '✅ Coluna Acertos_11 adicionada!';
END
ELSE PRINT '⚠️ Coluna Acertos_11 já existe.';
GO

-- =====================================================
-- 📊 COLUNAS DE ÚLTIMO CONCURSO COM ACERTO
-- =====================================================

-- Último concurso com 15 acertos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Ultimo_Acertos_15')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Ultimo_Acertos_15 INT NULL;
    PRINT '✅ Coluna Ultimo_Acertos_15 adicionada!';
END
ELSE PRINT '⚠️ Coluna Ultimo_Acertos_15 já existe.';
GO

-- Último concurso com 14 acertos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Ultimo_Acertos_14')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Ultimo_Acertos_14 INT NULL;
    PRINT '✅ Coluna Ultimo_Acertos_14 adicionada!';
END
ELSE PRINT '⚠️ Coluna Ultimo_Acertos_14 já existe.';
GO

-- Último concurso com 13 acertos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Ultimo_Acertos_13')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Ultimo_Acertos_13 INT NULL;
    PRINT '✅ Coluna Ultimo_Acertos_13 adicionada!';
END
ELSE PRINT '⚠️ Coluna Ultimo_Acertos_13 já existe.';
GO

-- Último concurso com 12 acertos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Ultimo_Acertos_12')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Ultimo_Acertos_12 INT NULL;
    PRINT '✅ Coluna Ultimo_Acertos_12 adicionada!';
END
ELSE PRINT '⚠️ Coluna Ultimo_Acertos_12 já existe.';
GO

-- Último concurso com 11 acertos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Ultimo_Acertos_11')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Ultimo_Acertos_11 INT NULL;
    PRINT '✅ Coluna Ultimo_Acertos_11 adicionada!';
END
ELSE PRINT '⚠️ Coluna Ultimo_Acertos_11 já existe.';
GO

-- =====================================================
-- 🔄 COLUNA DE CONTROLE INCREMENTAL
-- =====================================================

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'UltimoConcursoAtualizado')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD UltimoConcursoAtualizado INT DEFAULT 0 NOT NULL;
    PRINT '✅ Coluna UltimoConcursoAtualizado adicionada!';
END
ELSE PRINT '⚠️ Coluna UltimoConcursoAtualizado já existe.';
GO

-- =====================================================
-- 📊 CRIAR ÍNDICES PARA CONSULTAS RÁPIDAS
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Acertos_15' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL'))
BEGIN
    CREATE INDEX IX_COMBINACOES_LF_Acertos_15 ON COMBINACOES_LOTOFACIL(Acertos_15);
    PRINT '✅ Índice IX_COMBINACOES_LF_Acertos_15 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Acertos_14' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL'))
BEGIN
    CREATE INDEX IX_COMBINACOES_LF_Acertos_14 ON COMBINACOES_LOTOFACIL(Acertos_14);
    PRINT '✅ Índice IX_COMBINACOES_LF_Acertos_14 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Ultimo_15' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL'))
BEGIN
    CREATE INDEX IX_COMBINACOES_LF_Ultimo_15 ON COMBINACOES_LOTOFACIL(Ultimo_Acertos_15);
    PRINT '✅ Índice IX_COMBINACOES_LF_Ultimo_15 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_UltimoAtualizado' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL'))
BEGIN
    CREATE INDEX IX_COMBINACOES_LF_UltimoAtualizado ON COMBINACOES_LOTOFACIL(UltimoConcursoAtualizado);
    PRINT '✅ Índice IX_COMBINACOES_LF_UltimoAtualizado criado!';
END
GO

-- =====================================================
-- 📋 VERIFICAR ESTRUTURA FINAL
-- =====================================================
PRINT '';
PRINT '📋 NOVAS COLUNAS ADICIONADAS À COMBINACOES_LOTOFACIL:';
PRINT '======================================================';

SELECT 
    COLUMN_NAME AS Coluna,
    DATA_TYPE AS Tipo,
    IS_NULLABLE AS Nulo,
    COLUMN_DEFAULT AS Padrao
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL'
AND COLUMN_NAME IN ('Acertos_15', 'Acertos_14', 'Acertos_13', 'Acertos_12', 'Acertos_11',
                    'Ultimo_Acertos_15', 'Ultimo_Acertos_14', 'Ultimo_Acertos_13', 
                    'Ultimo_Acertos_12', 'Ultimo_Acertos_11', 'UltimoConcursoAtualizado')
ORDER BY COLUMN_NAME;

PRINT '';
PRINT '✅ Tabela COMBINACOES_LOTOFACIL pronta para atualização de acertos!';
GO
