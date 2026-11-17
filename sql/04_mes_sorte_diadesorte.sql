-- Dia de Sorte: coluna do "Mês da Sorte" (1 = Janeiro ... 12 = Dezembro).
-- Idempotente: pode rodar em bancos que já têm a coluna.
IF COL_LENGTH('dbo.Resultados_DiaDeSorte', 'Mes_Sorte') IS NULL
BEGIN
    ALTER TABLE dbo.Resultados_DiaDeSorte ADD Mes_Sorte INT NULL;
    PRINT 'Coluna Mes_Sorte adicionada em Resultados_DiaDeSorte.';
END
ELSE
    PRINT 'Coluna Mes_Sorte ja existe em Resultados_DiaDeSorte.';
GO
