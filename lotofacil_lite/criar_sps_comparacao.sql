-- ========================================================
-- CRIAÇÃO DAS STORED PROCEDURES DE COMPARAÇÃO
-- ========================================================
-- Cria as SPs SP_AtualizarCamposComparacao e SP_AtualizarCombinacoesComparacao
-- baseadas na lógica de comparação posição-por-posição validada

USE LOTOFACIL
GO

-- ========================================================
-- SP_AtualizarCamposComparacao
-- ========================================================
-- Atualiza os campos de comparação na tabela RESULTADOS_INT
-- usando a lógica posição-por-posição

IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'SP_AtualizarCamposComparacao')
    DROP PROCEDURE SP_AtualizarCamposComparacao
GO

CREATE PROCEDURE SP_AtualizarCamposComparacao
    @UltimoConcurso INT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @ConcursoAnterior INT = @UltimoConcurso - 1;
    
    -- Verifica se ambos os concursos existem
    IF NOT EXISTS (SELECT 1 FROM RESULTADOS_INT WHERE Concurso = @UltimoConcurso)
        OR NOT EXISTS (SELECT 1 FROM RESULTADOS_INT WHERE Concurso = @ConcursoAnterior)
    BEGIN
        PRINT 'Concursos não encontrados: ' + CAST(@ConcursoAnterior AS VARCHAR) + ' ou ' + CAST(@UltimoConcurso AS VARCHAR);
        RETURN;
    END
    
    -- Declara variáveis para armazenar os números dos concursos
    DECLARE @N1_Ant INT, @N2_Ant INT, @N3_Ant INT, @N4_Ant INT, @N5_Ant INT,
            @N6_Ant INT, @N7_Ant INT, @N8_Ant INT, @N9_Ant INT, @N10_Ant INT,
            @N11_Ant INT, @N12_Ant INT, @N13_Ant INT, @N14_Ant INT, @N15_Ant INT;
            
    DECLARE @N1_Atu INT, @N2_Atu INT, @N3_Atu INT, @N4_Atu INT, @N5_Atu INT,
            @N6_Atu INT, @N7_Atu INT, @N8_Atu INT, @N9_Atu INT, @N10_Atu INT,
            @N11_Atu INT, @N12_Atu INT, @N13_Atu INT, @N14_Atu INT, @N15_Atu INT;
    
    -- Busca números do concurso anterior
    SELECT @N1_Ant = N1, @N2_Ant = N2, @N3_Ant = N3, @N4_Ant = N4, @N5_Ant = N5,
           @N6_Ant = N6, @N7_Ant = N7, @N8_Ant = N8, @N9_Ant = N9, @N10_Ant = N10,
           @N11_Ant = N11, @N12_Ant = N12, @N13_Ant = N13, @N14_Ant = N14, @N15_Ant = N15
    FROM RESULTADOS_INT 
    WHERE Concurso = @ConcursoAnterior;
    
    -- Busca números do concurso atual
    SELECT @N1_Atu = N1, @N2_Atu = N2, @N3_Atu = N3, @N4_Atu = N4, @N5_Atu = N5,
           @N6_Atu = N6, @N7_Atu = N7, @N8_Atu = N8, @N9_Atu = N9, @N10_Atu = N10,
           @N11_Atu = N11, @N12_Atu = N12, @N13_Atu = N13, @N14_Atu = N14, @N15_Atu = N15
    FROM RESULTADOS_INT 
    WHERE Concurso = @UltimoConcurso;
    
    -- Calcula comparações posição por posição
    DECLARE @Menor INT = 0, @Maior INT = 0, @Igual INT = 0;
    
    -- Posição 1
    IF @N1_Atu < @N1_Ant SET @Menor = @Menor + 1;
    ELSE IF @N1_Atu > @N1_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 2
    IF @N2_Atu < @N2_Ant SET @Menor = @Menor + 1;
    ELSE IF @N2_Atu > @N2_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 3
    IF @N3_Atu < @N3_Ant SET @Menor = @Menor + 1;
    ELSE IF @N3_Atu > @N3_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 4
    IF @N4_Atu < @N4_Ant SET @Menor = @Menor + 1;
    ELSE IF @N4_Atu > @N4_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 5
    IF @N5_Atu < @N5_Ant SET @Menor = @Menor + 1;
    ELSE IF @N5_Atu > @N5_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 6
    IF @N6_Atu < @N6_Ant SET @Menor = @Menor + 1;
    ELSE IF @N6_Atu > @N6_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 7
    IF @N7_Atu < @N7_Ant SET @Menor = @Menor + 1;
    ELSE IF @N7_Atu > @N7_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 8
    IF @N8_Atu < @N8_Ant SET @Menor = @Menor + 1;
    ELSE IF @N8_Atu > @N8_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 9
    IF @N9_Atu < @N9_Ant SET @Menor = @Menor + 1;
    ELSE IF @N9_Atu > @N9_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 10
    IF @N10_Atu < @N10_Ant SET @Menor = @Menor + 1;
    ELSE IF @N10_Atu > @N10_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 11
    IF @N11_Atu < @N11_Ant SET @Menor = @Menor + 1;
    ELSE IF @N11_Atu > @N11_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 12
    IF @N12_Atu < @N12_Ant SET @Menor = @Menor + 1;
    ELSE IF @N12_Atu > @N12_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 13
    IF @N13_Atu < @N13_Ant SET @Menor = @Menor + 1;
    ELSE IF @N13_Atu > @N13_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 14
    IF @N14_Atu < @N14_Ant SET @Menor = @Menor + 1;
    ELSE IF @N14_Atu > @N14_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Posição 15
    IF @N15_Atu < @N15_Ant SET @Menor = @Menor + 1;
    ELSE IF @N15_Atu > @N15_Ant SET @Maior = @Maior + 1;
    ELSE SET @Igual = @Igual + 1;
    
    -- Atualiza os campos na tabela RESULTADOS_INT
    UPDATE RESULTADOS_INT 
    SET menor_que_ultimo = @Menor,
        maior_que_ultimo = @Maior,
        igual_ao_ultimo = @Igual
    WHERE Concurso = @UltimoConcurso;
    
    PRINT 'Campos de comparação atualizados para concurso ' + CAST(@UltimoConcurso AS VARCHAR);
    PRINT 'Menor: ' + CAST(@Menor AS VARCHAR) + ', Maior: ' + CAST(@Maior AS VARCHAR) + ', Igual: ' + CAST(@Igual AS VARCHAR);
    
END
GO

-- ========================================================
-- SP_AtualizarCombinacoesComparacao  
-- ========================================================
-- Atualiza os campos de comparação na tabela COMBINACOES_LOTOFACIL
-- para todas as combinações, comparando com o último concurso

IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'SP_AtualizarCombinacoesComparacao')
    DROP PROCEDURE SP_AtualizarCombinacoesComparacao
GO

CREATE PROCEDURE SP_AtualizarCombinacoesComparacao
    @UltimoConcurso INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Verifica se o concurso existe
    IF NOT EXISTS (SELECT 1 FROM RESULTADOS_INT WHERE Concurso = @UltimoConcurso)
    BEGIN
        PRINT 'Concurso não encontrado: ' + CAST(@UltimoConcurso AS VARCHAR);
        RETURN;
    END
    
    -- Busca números do último concurso
    DECLARE @N1 INT, @N2 INT, @N3 INT, @N4 INT, @N5 INT,
            @N6 INT, @N7 INT, @N8 INT, @N9 INT, @N10 INT,
            @N11 INT, @N12 INT, @N13 INT, @N14 INT, @N15 INT;
    
    SELECT @N1 = N1, @N2 = N2, @N3 = N3, @N4 = N4, @N5 = N5,
           @N6 = N6, @N7 = N7, @N8 = N8, @N9 = N9, @N10 = N10,
           @N11 = N11, @N12 = N12, @N13 = N13, @N14 = N14, @N15 = N15
    FROM RESULTADOS_INT 
    WHERE Concurso = @UltimoConcurso;
    
    DECLARE @ContadorAtualizacoes INT = 0;
    
    -- Atualiza cada combinação comparando posição por posição com o último concurso
    UPDATE COMBINACOES_LOTOFACIL
    SET menor_que_ultimo = (
        CASE WHEN N1 < @N1 THEN 1 ELSE 0 END +
        CASE WHEN N2 < @N2 THEN 1 ELSE 0 END +
        CASE WHEN N3 < @N3 THEN 1 ELSE 0 END +
        CASE WHEN N4 < @N4 THEN 1 ELSE 0 END +
        CASE WHEN N5 < @N5 THEN 1 ELSE 0 END +
        CASE WHEN N6 < @N6 THEN 1 ELSE 0 END +
        CASE WHEN N7 < @N7 THEN 1 ELSE 0 END +
        CASE WHEN N8 < @N8 THEN 1 ELSE 0 END +
        CASE WHEN N9 < @N9 THEN 1 ELSE 0 END +
        CASE WHEN N10 < @N10 THEN 1 ELSE 0 END +
        CASE WHEN N11 < @N11 THEN 1 ELSE 0 END +
        CASE WHEN N12 < @N12 THEN 1 ELSE 0 END +
        CASE WHEN N13 < @N13 THEN 1 ELSE 0 END +
        CASE WHEN N14 < @N14 THEN 1 ELSE 0 END +
        CASE WHEN N15 < @N15 THEN 1 ELSE 0 END
    ),
    maior_que_ultimo = (
        CASE WHEN N1 > @N1 THEN 1 ELSE 0 END +
        CASE WHEN N2 > @N2 THEN 1 ELSE 0 END +
        CASE WHEN N3 > @N3 THEN 1 ELSE 0 END +
        CASE WHEN N4 > @N4 THEN 1 ELSE 0 END +
        CASE WHEN N5 > @N5 THEN 1 ELSE 0 END +
        CASE WHEN N6 > @N6 THEN 1 ELSE 0 END +
        CASE WHEN N7 > @N7 THEN 1 ELSE 0 END +
        CASE WHEN N8 > @N8 THEN 1 ELSE 0 END +
        CASE WHEN N9 > @N9 THEN 1 ELSE 0 END +
        CASE WHEN N10 > @N10 THEN 1 ELSE 0 END +
        CASE WHEN N11 > @N11 THEN 1 ELSE 0 END +
        CASE WHEN N12 > @N12 THEN 1 ELSE 0 END +
        CASE WHEN N13 > @N13 THEN 1 ELSE 0 END +
        CASE WHEN N14 > @N14 THEN 1 ELSE 0 END +
        CASE WHEN N15 > @N15 THEN 1 ELSE 0 END
    ),
    igual_ao_ultimo = (
        CASE WHEN N1 = @N1 THEN 1 ELSE 0 END +
        CASE WHEN N2 = @N2 THEN 1 ELSE 0 END +
        CASE WHEN N3 = @N3 THEN 1 ELSE 0 END +
        CASE WHEN N4 = @N4 THEN 1 ELSE 0 END +
        CASE WHEN N5 = @N5 THEN 1 ELSE 0 END +
        CASE WHEN N6 = @N6 THEN 1 ELSE 0 END +
        CASE WHEN N7 = @N7 THEN 1 ELSE 0 END +
        CASE WHEN N8 = @N8 THEN 1 ELSE 0 END +
        CASE WHEN N9 = @N9 THEN 1 ELSE 0 END +
        CASE WHEN N10 = @N10 THEN 1 ELSE 0 END +
        CASE WHEN N11 = @N11 THEN 1 ELSE 0 END +
        CASE WHEN N12 = @N12 THEN 1 ELSE 0 END +
        CASE WHEN N13 = @N13 THEN 1 ELSE 0 END +
        CASE WHEN N14 = @N14 THEN 1 ELSE 0 END +
        CASE WHEN N15 = @N15 THEN 1 ELSE 0 END
    );
    
    SET @ContadorAtualizacoes = @@ROWCOUNT;
    
    PRINT 'Campos de comparação atualizados para ' + CAST(@ContadorAtualizacoes AS VARCHAR) + ' combinações';
    PRINT 'Baseado no concurso ' + CAST(@UltimoConcurso AS VARCHAR);
    
END
GO

-- ========================================================
-- TESTE DAS STORED PROCEDURES
-- ========================================================
-- Executa um teste básico das SPs criadas

PRINT '========================================';
PRINT 'TESTANDO AS STORED PROCEDURES CRIADAS';
PRINT '========================================';

-- Testa SP_AtualizarCamposComparacao
PRINT 'Testando SP_AtualizarCamposComparacao...';
EXEC SP_AtualizarCamposComparacao @ConcursoNovo = 3505;

-- Testa SP_AtualizarCombinacoesComparacao  
PRINT 'Testando SP_AtualizarCombinacoesComparacao...';
EXEC SP_AtualizarCombinacoesComparacao @ConcursoReferencia = 3505;

PRINT '========================================';
PRINT 'STORED PROCEDURES CRIADAS E TESTADAS!';
PRINT '========================================';