-- =====================================================
-- 🔧 ADICIONAR COLUNAS DE ACERTOS - LOTOFÁCIL 20 NÚMEROS
-- =====================================================
-- Adiciona as colunas Acertos_15, Acertos_14, Acertos_13, 
-- Acertos_12 e Acertos_11 na tabela COMBINACOES_LOTOFACIL20_COMPLETO
-- 
-- Essas colunas armazenam a contagem de vezes que cada combinação
-- de 20 números conteve os 11, 12, 13, 14 ou 15 números sorteados.
-- =====================================================

USE LOTOFACIL;
GO

-- =====================================================
-- 🎯 ACERTOS 15 (PRÊMIO MÁXIMO)
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Acertos_15')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Acertos_15 INT DEFAULT 0 NOT NULL;
    
    PRINT '✅ Coluna Acertos_15 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Acertos_15 já existe.';
END

-- =====================================================
-- 🎯 ACERTOS 14
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Acertos_14')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Acertos_14 INT DEFAULT 0 NOT NULL;
    
    PRINT '✅ Coluna Acertos_14 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Acertos_14 já existe.';
END

-- =====================================================
-- 🎯 ACERTOS 13
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Acertos_13')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Acertos_13 INT DEFAULT 0 NOT NULL;
    
    PRINT '✅ Coluna Acertos_13 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Acertos_13 já existe.';
END

-- =====================================================
-- 🎯 ACERTOS 12
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Acertos_12')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Acertos_12 INT DEFAULT 0 NOT NULL;
    
    PRINT '✅ Coluna Acertos_12 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Acertos_12 já existe.';
END

-- =====================================================
-- 🎯 ACERTOS 11 (PRÊMIO MÍNIMO)
-- =====================================================
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO' 
               AND COLUMN_NAME = 'Acertos_11')
BEGIN
    ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
    ADD Acertos_11 INT DEFAULT 0 NOT NULL;
    
    PRINT '✅ Coluna Acertos_11 adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Coluna Acertos_11 já existe.';
END

GO

-- =====================================================
-- 📊 CRIAR ÍNDICES PARA CONSULTAS RÁPIDAS
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Acertos_15')
BEGIN
    CREATE INDEX IX_COMBINACOES20_Acertos_15 ON COMBINACOES_LOTOFACIL20_COMPLETO(Acertos_15);
    PRINT '✅ Índice IX_COMBINACOES20_Acertos_15 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Acertos_14')
BEGIN
    CREATE INDEX IX_COMBINACOES20_Acertos_14 ON COMBINACOES_LOTOFACIL20_COMPLETO(Acertos_14);
    PRINT '✅ Índice IX_COMBINACOES20_Acertos_14 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Acertos_13')
BEGIN
    CREATE INDEX IX_COMBINACOES20_Acertos_13 ON COMBINACOES_LOTOFACIL20_COMPLETO(Acertos_13);
    PRINT '✅ Índice IX_COMBINACOES20_Acertos_13 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Acertos_12')
BEGIN
    CREATE INDEX IX_COMBINACOES20_Acertos_12 ON COMBINACOES_LOTOFACIL20_COMPLETO(Acertos_12);
    PRINT '✅ Índice IX_COMBINACOES20_Acertos_12 criado!';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_COMBINACOES20_Acertos_11')
BEGIN
    CREATE INDEX IX_COMBINACOES20_Acertos_11 ON COMBINACOES_LOTOFACIL20_COMPLETO(Acertos_11);
    PRINT '✅ Índice IX_COMBINACOES20_Acertos_11 criado!';
END

GO

-- =====================================================
-- 📋 VERIFICAR ESTRUTURA FINAL
-- =====================================================
PRINT '';
PRINT '📋 ESTRUTURA DAS COLUNAS DE ACERTOS:';
PRINT '=====================================';

SELECT 
    COLUMN_NAME AS Coluna,
    DATA_TYPE AS Tipo,
    IS_NULLABLE AS Nulo,
    COLUMN_DEFAULT AS Padrao
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
AND COLUMN_NAME IN ('Acertos_15', 'Acertos_14', 'Acertos_13', 'Acertos_12', 'Acertos_11')
ORDER BY COLUMN_NAME DESC;

PRINT '';
PRINT '🎯 Estrutura das colunas de acertos verificada!';
PRINT '✅ Colunas prontas para receber contagem de acertos!';
