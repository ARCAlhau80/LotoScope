"""
Reconstrução da tabela NumerosCiclosMega + Procedure automática
================================================================
Problema: NumerosCiclosMega está desatualizada (parou no ciclo 60, concurso 2853).
          Mega-Sena está no concurso 3039+ e não tem processo automático.

Solução:
  1. Reconstrói TODOS os ciclos históricos a partir de Resultados_MegaSenaFechado
  2. Cria procedure AtualizaNumerosCiclosMega (idempotente) para atualização automática
  3. A procedure é chamada automaticamente pelo AtualizadorMegaSena
"""
import pyodbc
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'shared'))
sys.path.insert(0, str(Path(__file__).parent / 'lotofacil_lite' / 'utils'))

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

# ---------------------------------------------------------------------------
# 1. SQL: Recriar tabela do zero
# ---------------------------------------------------------------------------
SQL_DROP_TABLE = """
IF EXISTS (SELECT * FROM sysobjects WHERE name='NumerosCiclosMega' AND xtype='U')
DROP TABLE [dbo].[NumerosCiclosMega];
"""

SQL_CREATE_TABLE = """
CREATE TABLE [dbo].[NumerosCiclosMega] (
    Ciclo INT NOT NULL,
    Numero INT NOT NULL,
    QtdSorteados INT DEFAULT 0,
    ConcursoInicio INT NOT NULL,
    ConcursoFechamento INT NULL,
    DataInicio DATETIME DEFAULT GETDATE(),
    DataFim DATETIME NULL,
    CONSTRAINT PK_NumerosCiclosMega PRIMARY KEY (Ciclo, Numero)
);

CREATE INDEX IX_NumerosCiclosMega_Ciclo ON NumerosCiclosMega(Ciclo);
CREATE INDEX IX_NumerosCiclosMega_Numero ON NumerosCiclosMega(Numero);
"""

# ---------------------------------------------------------------------------
# 2. SQL: Procedure para atualização automática (idempotente)
# ---------------------------------------------------------------------------
SQL_CREATE_PROCEDURE = """
CREATE OR ALTER PROCEDURE [dbo].[AtualizaNumerosCiclosMega]
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @UltimoCiclo INT, @UltimoConcursoFechamento INT, @NovoCiclo INT, @NovoConcursoInicio INT;
    DECLARE @TotalNumeros INT = 60;  -- Mega-Sena tem 60 números

    -- 1. Identificar o último ciclo fechado
    SELECT TOP 1 
        @UltimoCiclo = Ciclo,
        @UltimoConcursoFechamento = ConcursoFechamento
    FROM [dbo].[NumerosCiclosMega]
    WHERE ConcursoFechamento IS NOT NULL
    ORDER BY Ciclo DESC;

    -- 2. Definir o novo ciclo e concurso de início
    SET @NovoCiclo = ISNULL(@UltimoCiclo, 0) + 1;
    SET @NovoConcursoInicio = ISNULL(@UltimoConcursoFechamento, (SELECT MIN(Concurso) FROM [dbo].[Resultados_MegaSenaFechado])) + 1;

    -- 3. Verificar se já existe ciclo aberto para esse início
    IF NOT EXISTS (SELECT 1 FROM [dbo].[NumerosCiclosMega] WHERE Ciclo = @NovoCiclo AND ConcursoInicio = @NovoConcursoInicio)
    BEGIN
        -- Inserir 60 números (1-60) para o novo ciclo
        DECLARE @i INT = 1;
        WHILE @i <= @TotalNumeros
        BEGIN
            INSERT INTO [dbo].[NumerosCiclosMega] (Ciclo, Numero, QtdSorteados, ConcursoInicio, DataInicio)
            VALUES (@NovoCiclo, @i, 0, @NovoConcursoInicio, GETDATE());
            SET @i = @i + 1;
        END
    END

    -- FIX: Resetar QtdSorteados do ciclo aberto ANTES de reprocessar
    -- Garante idempotência: N chamadas = mesmo resultado
    UPDATE [dbo].[NumerosCiclosMega]
    SET QtdSorteados = 0
    WHERE Ciclo = @NovoCiclo
      AND ConcursoFechamento IS NULL;

    -- 4. Processar concursos do ciclo aberto
    DECLARE @ConcursoAtual INT, @DataSorteio DATETIME;
    DECLARE @Num1 INT, @Num2 INT, @Num3 INT, @Num4 INT, @Num5 INT, @Num6 INT;

    DECLARE Cur CURSOR FOR
    SELECT Concurso, Data_Sorteio, N1, N2, N3, N4, N5, N6
    FROM [dbo].[Resultados_MegaSenaFechado]
    WHERE Concurso >= @NovoConcursoInicio
    ORDER BY Concurso;

    OPEN Cur;
    FETCH NEXT FROM Cur INTO @ConcursoAtual, @DataSorteio, @Num1, @Num2, @Num3, @Num4, @Num5, @Num6;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        UPDATE [dbo].[NumerosCiclosMega] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num1;
        UPDATE [dbo].[NumerosCiclosMega] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num2;
        UPDATE [dbo].[NumerosCiclosMega] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num3;
        UPDATE [dbo].[NumerosCiclosMega] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num4;
        UPDATE [dbo].[NumerosCiclosMega] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num5;
        UPDATE [dbo].[NumerosCiclosMega] SET QtdSorteados = QtdSorteados + 1 WHERE Ciclo = @NovoCiclo AND Numero = @Num6;

        -- Verificar se todos os 60 números já foram sorteados
        IF (SELECT COUNT(*) FROM [dbo].[NumerosCiclosMega] WHERE Ciclo = @NovoCiclo AND QtdSorteados > 0) = @TotalNumeros
        BEGIN
            UPDATE [dbo].[NumerosCiclosMega]
            SET ConcursoFechamento = @ConcursoAtual, 
                DataFim = @DataSorteio
            WHERE Ciclo = @NovoCiclo;

            BREAK;
        END

        FETCH NEXT FROM Cur INTO @ConcursoAtual, @DataSorteio, @Num1, @Num2, @Num3, @Num4, @Num5, @Num6;
    END

    CLOSE Cur;
    DEALLOCATE Cur;
END
"""

# ---------------------------------------------------------------------------
# 3. Reconstrução histórica completa
# ---------------------------------------------------------------------------
def rebuild_historical_data(cursor, conn):
    """Reconstrói todos os ciclos a partir do histórico de resultados"""
    print("\n[1/3] Reconstruindo dados históricos...")
    
    # Buscar todos os resultados ordenados por concurso
    cursor.execute("""
        SELECT Concurso, Data_Sorteio, N1, N2, N3, N4, N5, N6
        FROM Resultados_MegaSenaFechado
        ORDER BY Concurso
    """)
    
    resultados = cursor.fetchall()
    print(f"   Total de concursos: {len(resultados)}")
    
    # Estrutura para rastrear ciclos
    ciclos = []  # Lista de ciclos fechados
    ciclo_atual = {
        'numero': 1,
        'concurso_inicio': 1,
        'concurso_fechamento': None,
        'data_inicio': None,
        'data_fim': None,
        'frequencia': {i: 0 for i in range(1, 61)}  # 1-60
    }
    
    for row in resultados:
        concurso, data_sorteio, n1, n2, n3, n4, n5, n6 = row
        numeros = [n1, n2, n3, n4, n5, n6]
        
        if ciclo_atual['data_inicio'] is None:
            ciclo_atual['data_inicio'] = data_sorteio
            ciclo_atual['concurso_inicio'] = concurso
        
        # Atualizar frequência
        for num in numeros:
            ciclo_atual['frequencia'][num] += 1
        
        # Verificar se todos os 60 números foram sorteados
        todos_sortearam = all(v > 0 for v in ciclo_atual['frequencia'].values())
        
        if todos_sortearam:
            # Fechar ciclo
            ciclo_atual['concurso_fechamento'] = concurso
            ciclo_atual['data_fim'] = data_sorteio
            ciclos.append(ciclo_atual.copy())
            
            # Iniciar novo ciclo
            ciclo_atual = {
                'numero': len(ciclos) + 1,
                'concurso_inicio': concurso + 1,
                'concurso_fechamento': None,
                'data_inicio': None,
                'data_fim': None,
                'frequencia': {i: 0 for i in range(1, 61)}
            }
    
    print(f"   Ciclos completos encontrados: {len(ciclos)}")
    
    # Se há concurso pendente (ciclo aberto), adicionar
    if ciclo_atual['data_inicio'] is not None and ciclo_atual['concurso_fechamento'] is None:
        ciclos.append(ciclo_atual)
        print(f"   Ciclo aberto: {ciclo_atual['numero']} (concurso {ciclo_atual['concurso_inicio']}+)")
    
    # Inserir dados na tabela
    print("   Inserindo dados na tabela...")
    
    # Limpar tabela existente
    cursor.execute("DELETE FROM NumerosCiclosMega")
    conn.commit()
    
    # Inserir todos os ciclos
    for ciclo in ciclos:
        for numero in range(1, 61):
            cursor.execute("""
                INSERT INTO NumerosCiclosMega 
                (Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento, DataInicio, DataFim)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ciclo['numero'],
                numero,
                ciclo['frequencia'][numero],
                ciclo['concurso_inicio'],
                ciclo['concurso_fechamento'],
                ciclo['data_inicio'],
                ciclo['data_fim']
            ))
    
    conn.commit()
    print(f"   [OK] {len(ciclos) * 60} registros inseridos")
    
    return len(ciclos)


def main():
    print("=" * 70)
    print("RECONSTRUÇÃO NumerosCiclosMega — Início")
    print("=" * 70)
    
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    # --- PASSO 1: Reconstrução histórica ---
    total_ciclos = rebuild_historical_data(cursor, conn)
    
    # --- PASSO 2: Criar procedure ---
    print("\n[2/3] Criando procedure AtualizaNumerosCiclosMega...")
    cursor.execute(SQL_CREATE_PROCEDURE)
    conn.commit()
    print("   [OK] Procedure criada com sucesso!")
    
    # --- PASSO 3: Validação ---
    print("\n[3/3] Validando dados...")
    
    # Verificar último ciclo fechado
    cursor.execute("""
        SELECT TOP 1 Ciclo, ConcursoInicio, ConcursoFechamento 
        FROM NumerosCiclosMega 
        WHERE ConcursoFechamento IS NOT NULL 
        ORDER BY Ciclo DESC
    """)
    ultimo_fechado = cursor.fetchone()
    if ultimo_fechado:
        print(f"   Último ciclo fechado: {ultimo_fechado[0]} (concursos {ultimo_fechado[1]}-{ultimo_fechado[2]})")
    
    # Verificar ciclo aberto
    cursor.execute("""
        SELECT TOP 1 Ciclo, ConcursoInicio 
        FROM NumerosCiclosMega 
        WHERE ConcursoFechamento IS NULL 
        ORDER BY Ciclo DESC
    """)
    ciclo_aberto = cursor.fetchone()
    if ciclo_aberto:
        print(f"   Ciclo aberto: {ciclo_aberto[0]} (a partir do concurso {ciclo_aberto[1]})")
    
    # Verificar último concurso da Mega-Sena
    cursor.execute("SELECT MAX(Concurso) FROM Resultados_MegaSenaFechado")
    ultimo_concurso = cursor.fetchone()[0]
    print(f"   Último concurso Mega-Sena: {ultimo_concurso}")
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM NumerosCiclosMega")
    total_registros = cursor.fetchone()[0]
    print(f"   Total de registros: {total_registros}")
    
    # Testar procedure
    print("\n   Testando procedure...")
    cursor.execute("EXEC AtualizaNumerosCiclosMega")
    conn.commit()
    print("   [OK] Procedure executada com sucesso!")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"[OK] Reconstrução concluída! {total_ciclos} ciclos processados.")
    print("[OK] Procedure automática criada e testada.")
    print("[OK] Agora o AtualizadorMegaSena chamará a procedure automaticamente.")
    print("=" * 70)


if __name__ == "__main__":
    main()
