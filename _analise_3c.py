import pyodbc
from math import comb
from collections import Counter

CONN = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=stofacil;Trusted_Connection=yes;'

with pyodbc.connect(CONN) as cn:
    cur = cn.cursor()
    cur.execute('SELECT Concurso,N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT WHERE Concurso BETWEEN 3450 AND 3659 ORDER BYConcurso')
    resultados = [(r[4], set(r[1:16])) for r in cur.fetchall()]

print('Carregados:', len(resultados))

def sc_inv(hist):
    draws = [n for _,n in hist]
    ul = draws[-30:]
    sc = {}
    for num in range(1,26):
        s = 0
        freq = sum(1 for d in ul if num in d) / max(len(ul),1)
        cons = 0
        for d in reversed(draws[-20:]):
            if num in d: cons += 1
            else: break
        if cons >= 10: s -= 5
        elif cons >= 5: s += 6
        elif cons >= 4: s += 5
        elif cons >= 3 and freq > 0.6: s += 4
        if len(draws) >= 5 and all(num in d for d in draws[-5:]): s += 4
        sc[num] = s
    return sc

T = 0
c1k = Counter()
c1ok = 0
ac4 = []
ac2 = []
ac3 = []
best = Counter()
excf = 0

for i, (conc, sorteio) in enumerate(resultados):
    if i < 30: continue
    sc = sc_inv(resultados[:i])
    excl = [n  for n in sorted(range(1,26),key=lambda n: -sc[n]) if sc[n] >= 0][:2]
    pool = sorted([n for n in range(1,26) if n not in excl])
    if any(e in sorteio for e in excl): excf += 1
    por = sorted(pool, key=lambda n: sc[n])
    c1 = por[:5]
    c2 = por[5:14]
    c3 = por[14:]
    a1 = len(set(c1) & sorteio)
    a2 = len(set(c2) & sorteio)
    a3 = len(set(c3) & sorteio)
    ac4.append(a1)
    ac2.append(a2)
    ac3.append(a3)
    c1k[a1] += 1
    if a1 == 5: c1ok += 1
    best[min(15, a1+min(a2,5)+min(a3,5))] += 1
    T += 1

print('Analisados:', T)
print()
print('=== C1 ACERTOS (5 FIXOS) NO SORTEIO ===')
for k in range(6):
    f = c1k.get(k,0)
    nt = 'JACKPOT POSS.' if k == 5 else ('max 14' if k == 4 else 'max <14')
    print(f'  {k}/5: {f:4d} ({f/T*100:5.1f}%)  {nt}')
print(f'  Completo 5/5: {c1ok}/{T} = {c1ok/T*100:.1f}%')

a1m = sum(ac4)/len(ac4)
a2m = sum(ac2)/len(ac2)
a3m = sum(ac3)/len(ac3)
print()
print('=== MEDIA ACERTOS POR CAMADA ===')
print(f'  C1 (5 fixos):  {a1m:.2f}/5  = {a1m/5*100:.1f}%')
print(f'  C2 (9 medios): {a2m:.2f}/9  = {a2m/9*100:.1f}%')
print(f'  C3 (9 baixos):  {a3m:.2f}/9  = {a3m/9*100:.1f}%')
diff = a1m/5 - a3m/9
print(f'  C1 vs C3: {diff*100:+.1f} p.p -> {"C1 melhor" if diff > 0 else "SEM DE.SCTINUIDADE"}')

print()
print('=== BEST-CASE 3CAMADAS===')
for k in sorted(best.keys(), reverse=True):
    f = best[k]
    mk = 'JACKPOT' if k == 15 else ('bom' if k >= 13 else '')
    print(f'  {k} acertos: {f:4d} ({f/T*100:5.1f}%)(™íµ­ôœ¤()•á½¬€ôP€´•á˜)ÁÉ¥¹Ğ ¤)ÁÉ¥¹Ğ œôôôA==0ÈÌ5Q5Q% ôôôœ¤)ÁÉ¥¹Ğ¡˜œ€á±ÕÍ…¼=,èí•á½­ô½íQô€ôí•á½¬½P¨ÄÀÀè¸Å™ô”œ¤)À€ô½µˆ ÈÀ°ÄÀ¤½½µˆ ÈÔ°ÄÔ¤)©ÀÍŒ€ô‰•ÍĞ¹•Ğ ÄÔ°À¤)ÁÉ¥¹Ğ¡˜œ€@ ÕÄÍ½ÉÑ•…‘½Ì¤Ñ•¼èíÀ¨ÄÀÀè¸Å™ô”€½‰ÌèíŒÅ½¬½P¨ÄÀÀè¸Å™ô”œ¤)ÁÉ¥¹Ğ¡˜œ€)…­Á½ĞA½½°ÈÌè€í•á½¬½P¨ÄÀÀè¸Å™ô”œ¤)ÁÉ¥¹Ğ¡˜œ€)…­Á½Ğ€Í…µ…‘…Ìèí©ÀÍŒ½P¨ÄÀÀè¸Å™ô”€€¡µ•±¡½È½µ‰¼Ñ•¼¤€œ¤)ÁÉ¥¹Ğ¡˜œ€A•É‘„½‰•ÉÑÕÉ„èí•á½¬½P¨ÄÀÀ€´©ÀÍŒ½P¨ÄÀÀè¸Å™ôÀ¹À¸œ¤)ÁÉ¥¹Ğ¡˜œ€½µ‰½ÌA½½°ÈÌèí½µˆ ÈÌ°ÄÔ¤éô€€Í…´èí½µˆ ä°Ô¤¨¨Èéô€I•‘Õ…¼èí¼Äµ½µˆ ä°Ô¤¨¨È½±½µˆ ÈÌ°ÄÔ¤¤¨ÄÀÀè¸Å™ô”œ¤)ŒÅ}µ¥¸Ğ€ôŒÅ¬¹•Ğ Ğ°À¤€¬ŒÅ¬¹•Ğ Ô°À¤)ÁÉ¥¹Ğ¡˜œ€M”Äµ¥¸ôĞ¼ÔèíŒÅ}µ¥¸Ñô½íQô€ôíŒÅ}µ¥¸Ğ½P¨ÄÀÀè¸Å™ô”€ÙÌ…ÑÕ…°íŒÅ½¬½P¨ÄÀÀè¸Å™ô”œ¤(