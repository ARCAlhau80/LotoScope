import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()
cursor.execute('SELECT TOP 20 Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso DESC')
rows = cursor.fetchall()
conn.close()
draws = []
concursos = []
for r in rows:
    concursos.append(r[0])
    draws.append(set(r[i] for i in range(1, 16)))
ultimo = concursos[0]
print('=== SCORING INVERTIDA v3.0 - Ultimos %d concursos ===' % len(draws))
print('Ultimo: %d  |  Proximo: %d' % (ultimo, ultimo + 1))
print()
resultados = []
for num in range(1, 26):
    cons = 0
    if num in draws[0]:
        for d in draws:
            if num in d: cons += 1
            else: break
    else:
        for d in draws:
            if num not in d: cons -= 1
            else: break
    freq20 = sum(1 for d in draws if num in d)
    pct20 = freq20 / len(draws) * 100
    freq5 = sum(1 for d in draws[:5] if num in d)
    pct5 = freq5 / 5 * 100
    score = 0
    motivos = []
    if cons >= 10:
        score -= 5; motivos.append('ANOMALIA(%d) PROTEGIDO' % cons)
    elif cons >= 5:
        score += 6; motivos.append('%dconsec' % cons)
    elif cons == 4:
        score += 5; motivos.append('4consec')
    elif cons >= 3 and pct20 >= 60:
        score += 4; motivos.append('3consec+freq%d' % int(pct20))
    if pct5 == 100 and cons < 10:
        score += 4; motivos.append('100pct_ult5')
    if score >= 9: st = 'HOT++'
    elif score >= 5: st = 'HOT'
    elif score >= 3: st = 'QUENTE'
    elif cons <= -4: st = 'FRIO'
    elif cons >= 10: st = 'ANOMALIA'
    else: st = 'normal'
    resultados.append((score, num, cons, pct20, pct5, st, motivos))
resultados.sort(key=lambda x: -x[0])
print('%-4s %-6s %-7s %-8s %-7s %-8s %s' % ('Num','Score','Consec','Freq20','Freq5','Status','Motivos'))
print('-' * 78)
for score, num, cons, pct20, pct5, st, motivos in resultados:
    c = ('+%d' % cons) if cons > 0 else str(cons)
    mot = ', '.join(motivos) if motivos else '-'
    print('%-4d %-6d %-7s %-7.0f%% %-6.0f%%  %-8s %s' % (num, score, c, pct20, pct5, st, mot))
print()
print('=== TOP 2 PARA EXCLUSAO ===')
excl = []
for score, num, cons, pct20, pct5, st, motivos in resultados:
    if score > 0 and len(excl) < 2:
        excl.append(num); print('  N%02d | Score=%d | %s | %s' % (num, score, st, ', '.join(motivos)))
pool = sorted(set(range(1, 26)) - set(excl[:2]))
print()
print('POOL 23: %s' % pool)
print('Excluidos: %s' % excl[:2])
