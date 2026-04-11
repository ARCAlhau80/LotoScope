"""Validação completa de menor/maior/igual_ao_ultimo em Resultados_INT."""

import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def _calcular_campos(nums, prev_nums):
    calc_men = calc_mai = calc_igu = 0
    for idx in range(15):
        if nums[idx] < prev_nums[idx]:
            calc_men += 1
        elif nums[idx] > prev_nums[idx]:
            calc_mai += 1
        else:
            calc_igu += 1
    return calc_men, calc_mai, calc_igu


def recalcular_campos_posicionais(verbose=True):
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,
                   menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
            FROM Resultados_INT
            ORDER BY Concurso
            '''
        )
        rows = cursor.fetchall()

        if verbose:
            print(f"Total concursos: {len(rows)}")

        prev_nums = None
        erros = []
        nulos = []
        total_ok = 0
        corrigidos = 0

        for row in rows:
            concurso = row[0]
            nums = list(row[1:16])
            db_men = row[16]
            db_mai = row[17]
            db_igu = row[18]

            if prev_nums is not None:
                calc_men, calc_mai, calc_igu = _calcular_campos(nums, prev_nums)
                is_null = db_men is None or db_mai is None or db_igu is None
                is_wrong = (not is_null) and (db_men != calc_men or db_mai != calc_mai or db_igu != calc_igu)

                if is_null:
                    nulos.append(concurso)
                if is_wrong:
                    erros.append((concurso, (db_men, db_mai, db_igu), (calc_men, calc_mai, calc_igu)))

                if is_null or is_wrong:
                    cursor.execute(
                        '''
                        UPDATE Resultados_INT
                        SET menor_que_ultimo = ?, maior_que_ultimo = ?, igual_ao_ultimo = ?
                        WHERE Concurso = ?
                        ''',
                        calc_men,
                        calc_mai,
                        calc_igu,
                        concurso,
                    )
                    corrigidos += 1
                else:
                    total_ok += 1
            else:
                if db_men is None or db_men != 0 or db_mai is None or db_mai != 0 or db_igu is None or db_igu != 0:
                    cursor.execute(
                        '''
                        UPDATE Resultados_INT
                        SET menor_que_ultimo = 0, maior_que_ultimo = 0, igual_ao_ultimo = 0
                        WHERE Concurso = ?
                        ''',
                        concurso,
                    )
                    corrigidos += 1
                else:
                    total_ok += 1

            prev_nums = nums

        conn.commit()

        cursor.execute('SELECT COUNT(*) FROM Resultados_INT WHERE menor_que_ultimo IS NULL')
        null_count = cursor.fetchone()[0]
        cursor.execute(
            '''
            SELECT COUNT(*) FROM Resultados_INT
            WHERE Concurso > 1 AND (menor_que_ultimo + maior_que_ultimo + igual_ao_ultimo) != 15
            '''
        )
        soma_errada = cursor.fetchone()[0]
        cursor.execute(
            '''
            SELECT TOP 10 Concurso, menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
            FROM Resultados_INT
            ORDER BY Concurso DESC
            '''
        )
        ultimos = cursor.fetchall()

    resumo = {
        'total_concursos': len(rows),
        'ok_sem_alteracao': total_ok,
        'nulls_encontrados': len(nulos),
        'valores_errados': len(erros),
        'corrigidos': corrigidos,
        'concursos_com_null': nulos,
        'amostra_erros': erros[:50],
        'nulls_restantes': null_count,
        'soma_errada_restante': soma_errada,
        'ultimos_10': ultimos,
    }

    if verbose:
        print('\nResultados:')
        print(f"  OK (sem alteracao): {resumo['ok_sem_alteracao']}")
        print(f"  NULLs encontrados: {resumo['nulls_encontrados']}")
        print(f"  Valores ERRADOS: {resumo['valores_errados']}")
        print(f"  Total CORRIGIDOS: {resumo['corrigidos']}")

        if nulos:
            print(f"\n  Concursos com NULL: {nulos}")
        if erros:
            print('\n  Concursos com valor errado:')
            for concurso, db_vals, calc_vals in resumo['amostra_erros']:
                print(
                    f"    {concurso}: DB=({db_vals[0]},{db_vals[1]},{db_vals[2]}) -> "
                    f"Correto=({calc_vals[0]},{calc_vals[1]},{calc_vals[2]})"
                )

        print('\n--- VERIFICAÇÃO PÓS-CORREÇÃO ---')
        print(f"NULLs restantes: {resumo['nulls_restantes']}")
        print(f"Registros com soma != 15: {resumo['soma_errada_restante']}")
        print('\nÚltimos 10 concursos:')
        print(f"  {'Conc':>5} {'Men':>4} {'Mai':>4} {'Igu':>4} {'Soma':>5}")
        for row in resumo['ultimos_10']:
            soma = (row[1] or 0) + (row[2] or 0) + (row[3] or 0)
            ok = 'OK' if soma == 15 or row[0] == 1 else 'ERRO'
            print(f"  {row[0]:>5} {row[1]:>4} {row[2]:>4} {row[3]:>4} {soma:>5} {ok}")
        print('\n✅ Validação e correção completa!')

    return resumo


def main():
    recalcular_campos_posicionais(verbose=True)


if __name__ == '__main__':
    main()

