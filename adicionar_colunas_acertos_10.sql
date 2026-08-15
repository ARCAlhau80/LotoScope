-- =====================================================
-- 🔧 ADICIONAR COLUNAS ACERTOS_10 - COMBINACOES_LOTOFACIL
-- =====================================================
-- Adiciona colunas para contagem e rastreio de 10 acertos.
-- Segue o mesmo padrão das colunas Acertos_11..15.
--
-- Autor: AR CALHAU
-- Data: 29/07/2026
-- =====================================================

USE LOTOFACIL;
GO

-- Acertos 10
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Acertos_10')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Acertos_10 INT DEFAULT 0 NOT NULL;
    PRINT '✅ Coluna Acertos_10 adicionada!';
END
ELSE PRINT '⚠️ Coluna Acertos_10 já existe.';
GO

-- Último concurso com 10 acertos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL' AND COLUMN_NAME = 'Ultimo_Acertos_10')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL ADD Ultimo_Acertos_10 INT NULL;
    PRINT '✅ Coluna Ultimo_Acertos_10 adicionada!';
END
ELSE PRINT '⚠️ Coluna Ultimo_Acertos_10 já existe.';
GO

-- Índice para consultas rápidas
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Acertos_10' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL'))
BEGIN
    CREATE INDEX IX_COMBINACOES_LF_Acertos_10 ON COMBINACOES_LOTOFACIL(Acertos_10);
    PRINT '✅ Índice IX_COMBINACOES_LF_Acertos_10 criado!';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES_LF_Ultimo_10' 
               AND object_id = OBJECT_ID('COMBINACOES_LOTOFACIL'))
BEGIN
    CREATE INDEX IX_COMBINACOES_LF_Ultimo_10 ON COMBINACOES_LOTOFACIL(Ultimo_Acertos_10);
    PRINT '✅ Índice IX_COMBINACOES_LF_Ultimo_10 criado!';
END
GO

-- Verificação final
PRINT '';
SELECT 
    COLUMN_NAME AS Coluna,
    DATA_TYPE AS Tipo,
    IS_NULLABLE AS Nulo
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL'
AND COLUMN_NAME IN ('Acertos_10', 'Ultimo_Acertos_10')
ORDER BY COLUMN_NAME;
GO
