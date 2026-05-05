"""
Correção da tabela NumerosCiclos + Procedure idempotente
=========================================================
Problema: AtualizaNumerosCiclos acumulava QtdSorteados sem zerar antes,
          causando duplicação/multiplicação se chamada > 1x com ciclo aberto.

Solução:
  1. Recalcula QtdSorteados para TODOS os ciclos diretamente de Resultados_INT
  2. Altera a procedure para resetar QtdSorteados=0 antes de reprocessar
     (torna-a idempotente)
"""
import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

# ---------------------------------------------------------------------------
# 1. SQL: recalcular QtdSorteados de todos os ciclos (correção histórica)
# ---------------------------------------------------------------------------
SQL_CORRECAO_DADOS = """
UPDATE nc
SET nc.QtdSorteados = (
    SELECT COUNT(*)
    FROM [dbo].[Resultados_INT] r
    WHERE r.Concurso BETWEEN nc.ConcursoInicio
                        AND ISNULL(nc.ConcursoFechamento,
                                   (SELECT MAX(Concurso) FROM [dbo].[Resultados_INT]))
      AND (   r.N1  = nc.Numero OR r.N2  = nc.Numero OR r.N3  = nc.Numero
           OR r.N4  = nc.Numero OR r.N5  = nc.Numero OR r.N6  = nc.Numero
           OR r.N7  = nc.Numero OR r.N8  = nc.Numero OR r.N9  = nc.Numero
           OR r.N10 = nc.Numero OR r.N11 = nc.Numero OR r.N12 = nc.Numero
           OR r.N13 = nc.Numero OR r.N14 = nc.Numero OR r.N15 = nc.Numero)
)
FROM [dbo].[NumerosCiclos] nc;
"""

# ---------------------------------------------------------------------------
# 2. SQL: ALTER PROCEDURE — adiciona reset antes do cursor (idempotência)
# ---------------------------------------------------------------------------
SQL_ALTER_PROC = """
ALTER PROCEDURE [dbo].[AtualizaNumerosCiclos]
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @UltimoCiclo INT, @UltimoConcursoFechamento INT, @NovoCiclo INT, @NovoConcursoInicio INT;

    -- 1. Identificar o último ciclo fechado
    SELECT TOP 1 
        @UltimoCiclo = Ciclo,
        @UltimoConcursoFechamento = ConcursoFechamento
    FROM [dbo].[NumerosCiclos]
    WHERE ConcursoFechamento IS NOT NULL
    ORDER BY Ciclo DESC;

    -- 2. Definir o novo ciclo e concurso de início
    SET @NovoCiclo = ISNULL(@UltimoCiclo, 0) + 1;
    SET @NovoConcursoInicio = ISNULL(@UltimoConcursoFechamento, (SELECT MIN(Concurso) FROM [dbo].[Resultados_INT])) + 1;

    -- 3. Verificar se já existe ciclo aberto para esse início
    IF NOT EXISTS (SELECT 1 FROM [dbo].[NumerosCiclos] WHERE Ciclo = @NovoCiclo AND ConcursoInicio = @NovoConcursoInicio)
    BEGIN
        INSERT INTO [dbo].[NumerosCiclos] (Ciclo, Numero, QtdSorteados, ConcursoInicio, DataInicio)
        SELECT @NovoCiclo, Numero, 0, @NovoConcursoInicio, GETDATE()
        FROM (SELECT DISTINCT CONVERT(INT, Value) AS Numero 
              FROM STRING_SPLIT('01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25', ',')) AS N;
    END

    -- FIX: Resetar QtdSorteados do ciclo aberto ANTES de reprocessar
    -- Garante idempotência: N chamadas = mesmo resultado
    UPDATE [dbo].[NumerosCiclos]
    SET QtdSorteados = 0
    WHERE Ciclo = @NovoCiclo
      AND ConcursoFechamento IS NULL;

    -- 4. Processar concursos do ciclo aberto
    DECLARE @ConcursoAtual INT, @DataSorteio DATETIME;
    DECLARE @Num1 INT, @Num2 INT, @Num3 INT, @Num4 INT, @Num5 INT, @Num6 INT, @Num7 INT, @Num8 INT, @Num9 INT, @Num10 INT;
    DECLARE @Num11 INT, @Num12 INT, @Num13 INT, @Num14 INT, @Num15 INT;

    DECLARE Cur CURSOR FOR
    SELECT Concurso, Data_sorteio, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, 
           N11, N12, N13, N14, N15
    FROM [dbo].[Resultados_INT]
    WHERE Concurso >= @NovoConcursoInicio
    ORDER BY Concurso;

    OPEN Cur;
    FETCH NEXT FROM Cur INTO @ConcursoAtual, @DataSorteio, @Num1, @Num2, @Num3, @Num4, @Num5, @Num6, @Num7, @Num8, @Num9, @Num10, 
                            @Num11, @Num12, @Num13, @Num14, @Num15;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num1;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num2;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num3;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num4;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num5;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num6;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num7;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num8;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num9;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num10;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num11;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num12;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num13;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num14;
        UPDATE [dbo].[NumerosCiclos] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num15;

        -- Verificar se todos os 25 números já foram sorteados
        IF (SELECT COUNT(*) FROM [dbo].[NumerosCiclos] WHERE Ciclo = @NovoCiclo AND QtdSorteados > 0) = 25
        BEGIN
            UPDATE [dbo].[NumerosCiclos]
            SET ConcursoFechamento = @ConcursoAtual, 
                DataFim = @DataSorteio
            WHERE Ciclo = @NovoCiclo;

            BREAK;
        END

        FETCH NEXT FROM Cur INTO @ConcursoAtual, @DataSorteio, @Num1, @Num2, @Num3, @Num4, @Num5, @Num6, @Num7, @Num8, @Num9, @Num10, 
                                @Num11, @Num12, @Num13, @Num14, @Num15;
    END

    CLOSE Cur;
    DEALLOCATE Cur;
END
"""

# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("CORREÇÃO NumerosCiclos — Início")
    print("=" * 60)

    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()

    # --- ANTES: contar ciclos com ratio != 1.0 ---
    cur.execute("""
        SELECT COUNT(DISTINCT Ciclo)
        FROM NumerosCiclos
        WHERE ConcursoFechamento IS NOT NULL
          AND QtdSorteados != (
              SELECT COUNT(*)
              FROM Resultados_INT r
              WHERE r.Concurso BETWEEN NumerosCiclos.ConcursoInicio AND NumerosCiclos.ConcursoFechamento
                AND (r.N1=NumerosCiclos.Numero OR r.N2=NumerosCiclos.Numero OR r.N3=NumerosCiclos.Numero
                  OR r.N4=NumerosCiclos.Numero OR r.N5=NumerosCiclos.Numero OR r.N6=NumerosCiclos.Numero
                  OR r.N7=NumerosCiclos.Numero OR r.N8=NumerosCiclos.Numero OR r.N9=NumerosCiclos.Numero
                  OR r.N10=NumerosCiclos.Numero OR r.N11=NumerosCiclos.Numero OR r.N12=NumerosCiclos.Numero
                  OR r.N13=NumerosCiclos.Numero OR r.N14=NumerosCiclos.Numero OR r.N15=NumerosCiclos.Numero))
    """)
    antes = cur.fetchone()[0]
    print(f"\n[ANTES]  Ciclos com QtdSorteados incorreto: {antes}")

    # --- PASSO 1: Corrigir dados históricos ---
    print("\n[1/2] Recalculando QtdSorteados de todos os ciclos a partir de Resultados_INT...")
    cur.execute(SQL_CORRECAO_DADOS)
    linhas = cur.rowcount
    conn.commit()
    print(f"      {linhas} linhas atualizadas.")

    # --- DEPOIS: verificar ---
    cur.execute("""
        SELECT COUNT(DISTINCT Ciclo)
        FROM NumerosCiclos
        WHERE ConcursoFechamento IS NOT NULL
          AND QtdSorteados != (
              SELECT COUNT(*)
              FROM Resultados_INT r
              WHERE r.Concurso BETWEEN NumerosCiclos.ConcursoInicio AND NumerosCiclos.ConcursoFechamento
                AND (r.N1=NumerosCiclos.Numero OR r.N2=NumerosCiclos.Numero OR r.N3=NumerosCiclos.Numero
                  OR r.N4=NumerosCiclos.Numero OR r.N5=NumerosCiclos.Numero OR r.N6=NumerosCiclos.Numero
                  OR r.N7=NumerosCiclos.Numero OR r.N8=NumerosCiclos.Numero OR r.N9=NumerosCiclos.Numero
                  OR r.N10=NumerosCiclos.Numero OR r.N11=NumerosCiclos.Numero OR r.N12=NumerosCiclos.Numero
                  OR r.N13=NumerosCiclos.Numero OR r.N14=NumerosCiclos.Numero OR r.N15=NumerosCiclos.Numero))
    """)
    depois = cur.fetchone()[0]
    print(f"[DEPOIS] Ciclos com QtdSorteados incorreto: {depois}")
    if depois == 0:
        print("         ✅ Todos os ciclos corrigidos!")
    else:
        print(f"         ⚠️  {depois} ciclo(s) ainda com divergência (verificar manualmente)")

    # --- PASSO 2: Alterar procedure para ser idempotente ---
    print("\n[2/2] Alterando procedure AtualizaNumerosCiclos (adiciona reset antes do cursor)...")
    cur.execute(SQL_ALTER_PROC)
    conn.commit()
    print("      ✅ Procedure alterada com sucesso!")

    # --- Mostrar ciclo 777 como confirmação ---
    cur.execute("""
        SELECT Numero, QtdSorteados FROM NumerosCiclos WHERE Ciclo=777 ORDER BY Numero
    """)
    rows = cur.fetchall()
    total = sum(r[1] for r in rows)
    print(f"\n[VALIDAÇÃO] Ciclo 777 (4 concursos, esperado=60): TotalSorteados={total} {'✅' if total==60 else '❌'}")

    conn.close()
    print("\n" + "=" * 60)
    print("Correção concluída.")
    print("=" * 60)


if __name__ == "__main__":
    main()
