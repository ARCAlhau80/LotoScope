-- QUERY PREDITIVA PARA CONCURSO 3489
-- Gerada em: 3488
-- Condições: 20

SELECT * FROM Resultados_INT WHERE QtdePrimos BETWEEN 4 AND 5 AND QtdeFibonacci BETWEEN 3 AND 5 AND QtdeImpares BETWEEN 7 AND 9 AND SomaTotal BETWEEN 186 AND 204 AND Quintil1 BETWEEN 2 AND 4 AND Quintil2 BETWEEN 2 AND 3 AND Quintil3 BETWEEN 2 AND 3 AND Quintil4 BETWEEN 2 AND 3 AND Quintil5 BETWEEN 2 AND 3 AND QtdeGaps BETWEEN 5 AND 6 AND QtdeRepetidos BETWEEN 8 AND 9 AND SEQ BETWEEN 7 AND 8 AND DistanciaExtremos BETWEEN 22 AND 24 AND ParesSequencia BETWEEN 3 AND 4 AND QtdeMultiplos3 BETWEEN 4 AND 5 AND ParesSaltados BETWEEN 0 AND 1 AND Faixa_Baixa BETWEEN 4 AND 6 AND Faixa_Media BETWEEN 4 AND 5 AND Faixa_Alta BETWEEN 4 AND 5 AND RepetidosMesmaPosicao BETWEEN 2 AND 4;

-- JUSTIFICATIVAS:
-- 1. QtdePrimos: Retorno à mediana histórica
-- 2. QtdeFibonacci: Continuidade decrescente moderada
-- 3. QtdeImpares: Continuidade decrescente moderada
-- 4. SomaTotal: Reversão após valor baixo (165 → média)
-- 5. Quintil1: Continuidade decrescente moderada
-- 6. Quintil2: Continuidade decrescente moderada
-- 7. Quintil3: Reversão após valor alto (5 → média)
-- 8. Quintil4: Reversão após valor baixo (1 → média)
-- 9. Quintil5: Reversão após valor baixo (2 → média)
-- 10. QtdeGaps: Continuidade decrescente moderada
-- 11. QtdeRepetidos: Reversão após valor baixo (7 → média)
-- 12. SEQ: Retorno à mediana histórica
-- 13. DistanciaExtremos: Continuidade decrescente moderada
-- 14. ParesSequencia: Continuidade crescente moderada
-- 15. QtdeMultiplos3: Retorno à mediana histórica
-- 16. ParesSaltados: Retorno à mediana histórica
-- 17. Faixa_Baixa: Continuidade decrescente moderada
-- 18. Faixa_Media: Retorno à mediana histórica
-- 19. Faixa_Alta: Reversão após valor baixo (2 → média)
-- 20. RepetidosMesmaPosicao: Reversão após valor baixo (1 → média)
