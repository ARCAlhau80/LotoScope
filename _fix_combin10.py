# -*- coding: utf-8 -*-
"""
Corrigir COMBIN_10: zerar QTDE_ACERTOS, corrigir proc, re-executar.
ATENÇÃO: Este script modifica dados! Execute apenas uma vez.
"""
import pyodbc
import time

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def main():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    # ═══════════════════════════════════════════════════
    # STEP 1: Verificar estado atual
    # ═══════════════════════════════════════════════════
    print("═" * 60)
    print("STEP 1: ESTADO ATUAL")
    print("═" * 60)
    
    cursor.execute("SELECT MAX(CONCURSO) FROM COMBIN_10")
    combin_conc = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
    result_conc = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(CAST(QTDE_ACERTOS AS BIGINT)) FROM COMBIN_10")
    soma_antes = cursor.fetchone()[0]
    
    print(f"  COMBIN_10 MAX(CONCURSO): {combin_conc}")
    print(f"  Resultados_INT MAX(Concurso): {result_conc}")
    print(f"  Soma QTDE_ACERTOS antes: {soma_antes:,}")
    
    # ═══════════════════════════════════════════════════
    # STEP 2: Zerar QTDE_ACERTOS e CONCURSO
    # ═══════════════════════════════════════════════════
    print(f"\n{'═' * 60}")
    print("STEP 2: ZERANDO QTDE_ACERTOS e CONCURSO...")
    print("═" * 60)
    
    t0 = time.time()
    cursor.execute("UPDATE COMBIN_10 SET QTDE_ACERTOS = 0, CONCURSO = 0")
    conn.commit()
    t1 = time.time()
    
    cursor.execute("SELECT SUM(CAST(QTDE_ACERTOS AS BIGINT)) FROM COMBIN_10")
    soma_zero = cursor.fetchone()[0]
    print(f"  ✅ Zerado em {t1-t0:.1f}s. Soma agora: {soma_zero}")
    
    # ═══════════════════════════════════════════════════
    # STEP 3: Corrigir a proc (remover segundo UPDATE duplicado)
    # ═══════════════════════════════════════════════════
    print(f"\n{'═' * 60}")
    print("STEP 3: CORRIGINDO PROC (removendo UPDATE duplicado)...")
    print("═" * 60)
    
    new_proc = """
ALTER PROCEDURE [dbo].[PROC_ATUALIZAR_COMBIN_10]
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @UltimoConcursoAtualizado INT;
    DECLARE @NovoUltimoConcurso INT;

    -- Descobre o maior concurso já processado na tabela COMBIN_10
    SELECT @UltimoConcursoAtualizado = ISNULL(MAX(CONCURSO), 0) FROM COMBIN_10;

    -- Descobre o maior concurso disponível em RESULTADOS_INT
    SELECT @NovoUltimoConcurso = MAX(Concurso) FROM RESULTADOS_INT;

    -- Atualiza apenas se houver concursos novos
    IF @NovoUltimoConcurso > @UltimoConcursoAtualizado
    BEGIN
        UPDATE C
        SET
            QTDE_ACERTOS = C.QTDE_ACERTOS + ISNULL(N.NOVOS_ACERTOS, 0),
            CONCURSO = @NovoUltimoConcurso
        FROM COMBIN_10 C
        OUTER APPLY (
            SELECT COUNT(1) AS NOVOS_ACERTOS
            FROM RESULTADOS_INT R
            WHERE R.Concurso > @UltimoConcursoAtualizado
              AND R.Concurso <= @NovoUltimoConcurso
              AND C.N1 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N2 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N3 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N4 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N5 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N6 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N7 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N8 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N9 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
              AND C.N10 IN (R.N1, R.N2, R.N3, R.N4, R.N5, R.N6, R.N7, R.N8, R.N9, R.N10, R.N11, R.N12, R.N13, R.N14, R.N15)
        ) N
    END
END
"""
    cursor.execute(new_proc)
    conn.commit()
    print("  ✅ Proc corrigida (UPDATE único, sem duplicação)")
    
    # Verificar proc atualizada
    cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('PROC_ATUALIZAR_COMBIN_10'))")
    proc_text = cursor.fetchone()[0]
    has_double = proc_text.count('UPDATE') 
    print(f"  Proc agora tem {has_double} UPDATE statement(s) (esperado: 1)")
    
    # ═══════════════════════════════════════════════════
    # STEP 4: Re-executar proc (do zero)
    # ═══════════════════════════════════════════════════
    print(f"\n{'═' * 60}")
    print("STEP 4: RE-EXECUTANDO PROC DO ZERO...")
    print("  (Isso pode levar vários minutos para 3.27M rows × 3650 concursos)")
    print("═" * 60)
    
    t0 = time.time()
    cursor.execute("EXEC PROC_ATUALIZAR_COMBIN_10")
    conn.commit()
    t1 = time.time()
    
    print(f"  ✅ Proc executada em {t1-t0:.1f}s")
    
    # ═══════════════════════════════════════════════════
    # STEP 5: Validar resultado
    # ═══════════════════════════════════════════════════
    print(f"\n{'═' * 60}")
    print("STEP 5: VALIDAÇÃO")
    print("═" * 60)
    
    cursor.execute("SELECT SUM(CAST(QTDE_ACERTOS AS BIGINT)) FROM COMBIN_10")
    soma_depois = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
    total_conc = cursor.fetchone()[0]
    esperado = total_conc * 3003  # C(15,10)
    
    print(f"  Soma QTDE_ACERTOS: {soma_depois:,}")
    print(f"  Esperado ({total_conc} × 3003): {esperado:,}")
    ratio = soma_depois / esperado if esperado > 0 else 0
    print(f"  Ratio: {ratio:.4f}x {'✅ OK' if 0.95 < ratio < 1.05 else '⚠️ VERIFICAR'}")
    
    # Manual spot check
    print(f"\n  Spot check (5 amostras):")
    cursor.execute("SELECT TOP 5 N1,N2,N3,N4,N5,N6,N7,N8,N9,N10, QTDE_ACERTOS FROM COMBIN_10 WHERE QTDE_ACERTOS > 0 ORDER BY ID_COMBIN")
    for row in cursor.fetchall():
        nums = list(row[:10])
        tabela_acertos = row[10]
        conditions = ' AND '.join([f'{n} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)' for n in nums])
        cursor.execute(f"SELECT COUNT(*) FROM Resultados_INT WHERE {conditions}")
        real = cursor.fetchone()[0]
        status = '✅' if tabela_acertos == real else '❌'
        print(f"    {nums} → tabela={tabela_acertos}, real={real} {status}")
    
    # Distribution
    print(f"\n  Distribuição QTDE_ACERTOS:")
    cursor.execute("SELECT QTDE_ACERTOS, COUNT(*) FROM COMBIN_10 GROUP BY QTDE_ACERTOS ORDER BY QTDE_ACERTOS")
    for acertos, qtd in cursor.fetchall():
        print(f"    {acertos:>3d}: {qtd:>10,d}")
    
    conn.close()
    print(f"\n✅ Correção completa!")

if __name__ == '__main__':
    main()
