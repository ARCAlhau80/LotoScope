-- ============================================================================
-- 🎯 SCRIPT SQL - GERADOR COMBINAÇÕES LOTOFÁCIL 20 NÚMEROS
-- ============================================================================
-- Cria tabela COMBINACOES_LOTOFACIL20 com todas as combinações possíveis
-- de 20 números únicos da Lotofácil (1 a 25)
-- Total: C(25,20) = 53.130 combinações
-- ============================================================================

PRINT '🚀 INICIANDO GERAÇÃO DE COMBINAÇÕES LOTOFÁCIL - 20 NÚMEROS'
PRINT '============================================================='

-- Verificar se a tabela existe e remover
IF OBJECT_ID('COMBINACOES_LOTOFACIL20', 'U') IS NOT NULL
BEGIN
    PRINT '🗑️ Removendo tabela existente...'
    DROP TABLE COMBINACOES_LOTOFACIL20;
END

-- Criar a tabela
PRINT '🏗️ Criando tabela COMBINACOES_LOTOFACIL20...'
CREATE TABLE COMBINACOES_LOTOFACIL20 (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    N1 TINYINT NOT NULL CHECK (N1 BETWEEN 1 AND 25),
    N2 TINYINT NOT NULL CHECK (N2 BETWEEN 1 AND 25),
    N3 TINYINT NOT NULL CHECK (N3 BETWEEN 1 AND 25),
    N4 TINYINT NOT NULL CHECK (N4 BETWEEN 1 AND 25),
    N5 TINYINT NOT NULL CHECK (N5 BETWEEN 1 AND 25),
    N6 TINYINT NOT NULL CHECK (N6 BETWEEN 1 AND 25),
    N7 TINYINT NOT NULL CHECK (N7 BETWEEN 1 AND 25),
    N8 TINYINT NOT NULL CHECK (N8 BETWEEN 1 AND 25),
    N9 TINYINT NOT NULL CHECK (N9 BETWEEN 1 AND 25),
    N10 TINYINT NOT NULL CHECK (N10 BETWEEN 1 AND 25),
    N11 TINYINT NOT NULL CHECK (N11 BETWEEN 1 AND 25),
    N12 TINYINT NOT NULL CHECK (N12 BETWEEN 1 AND 25),
    N13 TINYINT NOT NULL CHECK (N13 BETWEEN 1 AND 25),
    N14 TINYINT NOT NULL CHECK (N14 BETWEEN 1 AND 25),
    N15 TINYINT NOT NULL CHECK (N15 BETWEEN 1 AND 25),
    N16 TINYINT NOT NULL CHECK (N16 BETWEEN 1 AND 25),
    N17 TINYINT NOT NULL CHECK (N17 BETWEEN 1 AND 25),
    N18 TINYINT NOT NULL CHECK (N18 BETWEEN 1 AND 25),
    N19 TINYINT NOT NULL CHECK (N19 BETWEEN 1 AND 25),
    N20 TINYINT NOT NULL CHECK (N20 BETWEEN 1 AND 25),
    
    -- Campos calculados (preenchidos posteriormente)
    QtdeRepetidos TINYINT NULL,
    RepetidosMesmaPosicao TINYINT NULL,
    
    -- Metadata
    DataGeracao DATETIME2 DEFAULT GETDATE(),
    Processado BIT DEFAULT 0,
    
    -- Garantir que todos os números são únicos e ordenados
    CHECK (N1 < N2 AND N2 < N3 AND N3 < N4 AND N4 < N5 AND 
           N5 < N6 AND N6 < N7 AND N7 < N8 AND N8 < N9 AND N9 < N10 AND
           N10 < N11 AND N11 < N12 AND N12 < N13 AND N13 < N14 AND N14 < N15 AND
           N15 < N16 AND N16 < N17 AND N17 < N18 AND N18 < N19 AND N19 < N20)
);

PRINT '✅ Tabela criada com sucesso!'

-- Criar índices para otimização
PRINT '📊 Criando índices...'
CREATE INDEX IX_COMBINACOES_20_Processado ON COMBINACOES_LOTOFACIL20(Processado);
CREATE INDEX IX_COMBINACOES_20_QtdeRepetidos ON COMBINACOES_LOTOFACIL20(QtdeRepetidos);
CREATE INDEX IX_COMBINACOES_20_DataGeracao ON COMBINACOES_LOTOFACIL20(DataGeracao);

-- Índice composto para busca rápida por combinação
CREATE INDEX IX_COMBINACOES_20_Numeros ON COMBINACOES_LOTOFACIL20(N1, N2, N3, N4, N5);

PRINT '✅ Índices criados!'

-- ============================================================================
-- 🎲 GERAÇÃO DAS COMBINAÇÕES USANDO CTE RECURSIVA
-- ============================================================================
-- ATENÇÃO: Esta abordagem pode ser lenta para 53.130 combinações
-- Recomenda-se usar o script Python para melhor performance
-- ============================================================================

PRINT '⚠️ IMPORTANTE: Para melhor performance, use o script Python!'
PRINT '   Gerando algumas combinações de exemplo...'

-- Gerar primeiras 1000 combinações como exemplo
WITH NumerosCTE AS (
    SELECT 1 as Numero
    UNION ALL
    SELECT Numero + 1
    FROM NumerosCTE
    WHERE Numero < 25
),
CombinacoesCTE AS (
    -- Esta é uma versão simplificada - o script Python é mais eficiente
    SELECT TOP 1000
        ROW_NUMBER() OVER (ORDER BY n1.Numero, n2.Numero) as ID,
        n1.Numero as N1, n2.Numero as N2, n3.Numero as N3, n4.Numero as N4, n5.Numero as N5,
        n6.Numero as N6, n7.Numero as N7, n8.Numero as N8, n9.Numero as N9, n10.Numero as N10,
        n11.Numero as N11, n12.Numero as N12, n13.Numero as N13, n14.Numero as N14, n15.Numero as N15,
        n16.Numero as N16, n17.Numero as N17, n18.Numero as N18, n19.Numero as N19, n20.Numero as N20
    FROM NumerosCTE n1
    CROSS JOIN NumerosCTE n2
    CROSS JOIN NumerosCTE n3
    CROSS JOIN NumerosCTE n4
    CROSS JOIN NumerosCTE n5
    CROSS JOIN NumerosCTE n6
    CROSS JOIN NumerosCTE n7
    CROSS JOIN NumerosCTE n8
    CROSS JOIN NumerosCTE n9
    CROSS JOIN NumerosCTE n10
    CROSS JOIN NumerosCTE n11
    CROSS JOIN NumerosCTE n12
    CROSS JOIN NumerosCTE n13
    CROSS JOIN NumerosCTE n14
    CROSS JOIN NumerosCTE n15
    CROSS JOIN NumerosCTE n16
    CROSS JOIN NumerosCTE n17
    CROSS JOIN NumerosCTE n18
    CROSS JOIN NumerosCTE n19
    CROSS JOIN NumerosCTE n20
    WHERE n1.Numero < n2.Numero 
      AND n2.Numero < n3.Numero
      AND n3.Numero < n4.Numero
      AND n4.Numero < n5.Numero
      AND n5.Numero < n6.Numero
      AND n6.Numero < n7.Numero
      AND n7.Numero < n8.Numero
      AND n8.Numero < n9.Numero
      AND n9.Numero < n10.Numero
      AND n10.Numero < n11.Numero
      AND n11.Numero < n12.Numero
      AND n12.Numero < n13.Numero
      AND n13.Numero < n14.Numero
      AND n14.Numero < n15.Numero
      AND n15.Numero < n16.Numero
      AND n16.Numero < n17.Numero
      AND n17.Numero < n18.Numero
      AND n18.Numero < n19.Numero
      AND n19.Numero < n20.Numero
)
INSERT INTO COMBINACOES_LOTOFACIL20 
(N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, N17, N18, N19, N20)
SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, N17, N18, N19, N20
FROM CombinacoesCTE
OPTION (MAXRECURSION 32767);

-- Verificar quantas foram inseridas
DECLARE @TotalInserido INT = (SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL20)
PRINT '📊 Combinações inseridas: ' + CAST(@TotalInserido AS VARCHAR(10))

-- ============================================================================
-- 📋 INFORMAÇÕES FINAIS
-- ============================================================================

PRINT ''
PRINT '============================================================='
PRINT '🏆 TABELA COMBINACOES_LOTOFACIL20 CRIADA!'
PRINT '============================================================='
PRINT '📊 Status: Estrutura criada, algumas combinações inseridas'
PRINT '🎯 Total esperado: 53.130 combinações'
PRINT '⚠️ Recomendação: Use o script Python para população completa'
PRINT ''
PRINT '🔄 PRÓXIMOS PASSOS:'
PRINT '1. Execute: python gerador_combinacoes_20.py'
PRINT '2. Calcule QtdeRepetidos e RepetidosMesmaPosicao'
PRINT '3. Atualize campo Processado = 1'
PRINT ''
PRINT '✅ Estrutura da tabela pronta para uso!'
PRINT '============================================================='

-- Mostrar estrutura da tabela
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20'
ORDER BY ORDINAL_POSITION;
