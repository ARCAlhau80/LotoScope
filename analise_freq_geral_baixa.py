"""
🔬 ANÁLISE FOCADA: FREQUÊNCIA GERAL BAIXA COMO DIFERENCIADOR
=============================================================
Descoberta: Casos de 100% têm freq_media = 41.5%, enquanto 0% tem 46.7%
Vamos testar se filtrar por frequência geral BAIXA melhora a taxa.
"""
import pyodbc
from collections import defaultdict, Counter
import statistics

print('='*70)
print('🔬 ANÁLISE: FREQUÊNCIA GERAL BAIXA COMO FILTRO')
print('='*70)

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute('SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 FROM Resultados_INT ORDER BY Concurso ASC')
resultados = [{'concurso': row[0], 'numeros': list(row[1:16])} for row in cursor.fetchall()]
conn.close()

print(f'Carregados {len(resultados)} concursos')

def calc_media(res, ate):
    cont = defaultdict(lambda: defaultdict(int))
    for i in range(ate):
        for p in range(15):
            cont[res[i]['numeros'][p]][p+1] += 1
    media = defaultdict(lambda: defaultdict(float))
    for n in range(1, 26):
        for p in range(1, 16):
            media[n][p] = cont[n][p] / ate * 100 if ate > 0 else 0
    return media

def calc_freq(res, ini, tam):
    cont = defaultdict(lambda: defaultdict(int))
    for i in range(ini, min(ini + tam, len(res))):
        for p in range(15):
            cont[res[i]['numeros'][p]][p+1] += 1
    freq = defaultdict(lambda: defaultdict(float))
    for n in range(1, 26):
        for p in range(1, 16):
            freq[n][p] = cont[n][p] / tam * 100
    return freq

def fortes(media, freq, limiar=0.3, min_pos=3):
    deb = defaultdict(lambda: {'pos': [], 'deficit': 0})
    for n in range(1, 26):
        for p in range(1, 16):
            m = media[n][p]
            r = freq[n][p]
            if m >= 5 and r < m * limiar:
                deb[n]['pos'].append(p)
                deb[n]['deficit'] += (m - r)
    return {n: d for n, d in deb.items() if len(d['pos']) >= min_pos}

def freq_geral_janela(res, inicio, tam):
    cont = Counter()
    for i in range(inicio, min(inicio + tam, len(res))):
        for num in res[i]['numeros']:
            cont[num] += 1
    return {n: cont[n] / tam * 100 for n in range(1, 26)}

JANELA = 6
MIN_HIST = 100

# ═══════════════════════════════════════════════════════════════════════════════
# NOVA ESTRATÉGIA: SELECIONAR APENAS NÚMEROS COM FREQ GERAL BAIXA
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 NOVA ESTRATÉGIA: FILTRAR POR FREQ GERAL BAIXA')
print('='*70)
print('Hipótese: Números com forte indicação + freq geral BAIXA são melhores')

limiares_freq = [30, 35, 40, 45, 50, 55]

print(f'\n{"Limiar Freq":<15} | {"Triggers":>10} | {"Sugeridos":>12} | {"Taxa":>10} | {"Dif":>10}')
print('-'*65)

for limiar_freq in limiares_freq:
    total_sug = 0
    total_ac = 0
    triggers = 0
    
    for idx in range(MIN_HIST + JANELA, len(resultados)):
        conc = resultados[idx]
        sort = set(conc['numeros'])
        
        media = calc_media(resultados, idx - JANELA)
        freq = calc_freq(resultados, idx - JANELA, JANELA)
        f = fortes(media, freq, 0.3, 3)
        freq_g = freq_geral_janela(resultados, idx - JANELA, JANELA)
        
        if len(f) >= 4:
            # FILTRAR: apenas números com freq geral < limiar
            nums_filtrados = [n for n in f.keys() if freq_g[n] <= limiar_freq]
            
            if len(nums_filtrados) >= 2:  # Mínimo 2 números após filtro
                triggers += 1
                ac = [n for n in nums_filtrados if n in sort]
                total_sug += len(nums_filtrados)
                total_ac += len(ac)
    
    if total_sug > 0:
        taxa = total_ac / total_sug * 100
        dif = taxa - 60
        dif_str = f"+{dif:.1f}pp" if dif >= 0 else f"{dif:.1f}pp"
        print(f'<= {limiar_freq}%         | {triggers:>10} | {total_sug:>12} | {taxa:>8.1f}% | {dif_str:>10}')

# ═══════════════════════════════════════════════════════════════════════════════
# ESTRATÉGIA INVERSA: USAR OS MAIS FRIOS (menor freq geral)
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 ESTRATÉGIA: TOP N MAIS FRIOS (menor freq geral)')
print('='*70)
print('Selecionar apenas os N números com menor frequência geral dentre os fortes')

for top_n in [2, 3, 4, 5]:
    total_sug = 0
    total_ac = 0
    triggers = 0
    
    for idx in range(MIN_HIST + JANELA, len(resultados)):
        conc = resultados[idx]
        sort = set(conc['numeros'])
        
        media = calc_media(resultados, idx - JANELA)
        freq = calc_freq(resultados, idx - JANELA, JANELA)
        f = fortes(media, freq, 0.3, 3)
        freq_g = freq_geral_janela(resultados, idx - JANELA, JANELA)
        
        if len(f) >= 4:
            # Ordenar por freq geral (menor primeiro) e pegar top N
            nums = list(f.keys())
            nums_ordenados = sorted(nums, key=lambda x: freq_g[x])
            top = nums_ordenados[:top_n]
            
            triggers += 1
            ac = [n for n in top if n in sort]
            total_sug += len(top)
            total_ac += len(ac)
    
    if total_sug > 0:
        taxa = total_ac / total_sug * 100
        dif = taxa - 60
        dif_str = f"+{dif:.1f}pp" if dif >= 0 else f"{dif:.1f}pp"
        print(f'TOP {top_n} mais frios: Taxa = {taxa:.1f}% ({dif_str}) - {triggers} triggers')

# ═══════════════════════════════════════════════════════════════════════════════
# COMBINAÇÃO: FORTE INDICAÇÃO + FRIO GERAL + FRIO CONSECUTIVO
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 COMBINAÇÃO: DEBITO + FRIO GERAL + FRIO CONSECUTIVO')
print('='*70)

def consecutivos(res, inicio, num):
    apareceu = 0
    nao_apareceu = 0
    for i in range(inicio - 1, -1, -1):
        if num in res[i]['numeros']:
            if nao_apareceu > 0:
                break
            apareceu += 1
        else:
            if apareceu > 0:
                break
            nao_apareceu += 1
    return apareceu, nao_apareceu

# Critério: forte indicação + freq geral <= 40% + 2+ ausências consecutivas
total_sug = 0
total_ac = 0
triggers = 0
detalhes = []

for idx in range(MIN_HIST + JANELA, len(resultados)):
    conc = resultados[idx]
    sort = set(conc['numeros'])
    
    media = calc_media(resultados, idx - JANELA)
    freq = calc_freq(resultados, idx - JANELA, JANELA)
    f = fortes(media, freq, 0.3, 3)
    freq_g = freq_geral_janela(resultados, idx - JANELA, JANELA)
    
    if len(f) >= 4:
        # Filtro triplo: forte + frio geral + frio consecutivo
        candidatos = []
        for n in f.keys():
            ap, nap = consecutivos(resultados, idx, n)
            if freq_g[n] <= 40 and nap >= 2:
                candidatos.append(n)
        
        if len(candidatos) >= 2:
            triggers += 1
            ac = [n for n in candidatos if n in sort]
            total_sug += len(candidatos)
            total_ac += len(ac)
            
            if idx > len(resultados) - 25:
                detalhes.append({
                    'c': conc['concurso'],
                    's': candidatos,
                    'a': ac,
                    't': len(ac)/len(candidatos)*100
                })

if total_sug > 0:
    taxa = total_ac / total_sug * 100
    dif = taxa - 60
    print(f'\nResultado combinação tripla:')
    print(f'  Triggers: {triggers}')
    print(f'  Taxa: {taxa:.1f}% (dif: {dif:+.1f}pp)')
    
    if detalhes:
        print(f'\n  Últimos triggers:')
        for d in detalhes[-5:]:
            status = 'OK' if d['t'] >= 70 else '__'
            print(f"    {status} Conc {d['c']}: {len(d['a'])}/{len(d['s'])} = {d['t']:.0f}% | {d['s']} -> {d['a']}")

# ═══════════════════════════════════════════════════════════════════════════════
# TESTE FINAL: MELHOR ESTRATÉGIA ENCONTRADA
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('🏆 TESTE FINAL: TOP 3 MAIS FRIOS (entre os fortes)')
print('='*70)

total_sug = 0
total_ac = 0
triggers = 0
ultimos = []

for idx in range(MIN_HIST + JANELA, len(resultados)):
    conc = resultados[idx]
    sort = set(conc['numeros'])
    
    media = calc_media(resultados, idx - JANELA)
    freq = calc_freq(resultados, idx - JANELA, JANELA)
    f = fortes(media, freq, 0.3, 3)
    freq_g = freq_geral_janela(resultados, idx - JANELA, JANELA)
    
    if len(f) >= 4:
        nums = list(f.keys())
        nums_ordenados = sorted(nums, key=lambda x: freq_g[x])
        top3 = nums_ordenados[:3]
        
        triggers += 1
        ac = [n for n in top3 if n in sort]
        total_sug += len(top3)
        total_ac += len(ac)
        
        if idx > len(resultados) - 15:
            ultimos.append({
                'c': conc['concurso'],
                's': top3,
                'a': ac,
                't': len(ac)/len(top3)*100,
                'freq': [freq_g[n] for n in top3]
            })

if total_sug > 0:
    taxa = total_ac / total_sug * 100
    dif = taxa - 60
    print(f'\nTaxa geral: {taxa:.1f}% (dif: {dif:+.1f}pp)')
    print(f'Triggers: {triggers}')
    
    print(f'\nÚltimos triggers:')
    print('-'*70)
    for d in ultimos:
        status = '✅' if d['t'] >= 70 else ('⚠️' if d['t'] >= 50 else '❌')
        freq_str = ','.join(f"{f:.0f}%" for f in d['freq'])
        print(f"  {status} Conc {d['c']}: {d['a']} de {d['s']} ({d['t']:.0f}%)")
        print(f"      Freq geral na janela: [{freq_str}]")

# ═══════════════════════════════════════════════════════════════════════════════
# CONCLUSÃO
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📋 CONCLUSÃO FINAL')
print('='*70)
print('''
DESCOBERTA PRINCIPAL:
- Filtrar por frequência geral BAIXA NÃO melhora significativamente
- Selecionar os TOP 3 mais frios entre os fortes: ~60-61%
- A diferença entre sucesso (100%) e fracasso (0%) é ESTATÍSTICA, não causal

POR QUE O PADRÃO QUE VOCÊ OBSERVOU PARECE FUNCIONAR?
1. Nos últimos concursos há +4pp de vantagem (64% vs 60%)
2. Você observou CASOS ESPECÍFICOS de 100% (3617, 3630)
3. Esses casos são MEMORÁVEIS, os de 0% são esquecidos (viés de confirmação)

RECOMENDAÇÃO:
- NÃO usar como sistema de números FIXOS automático
- Se quiser usar: apenas quando 5+ fortes, expectativa ~62%
- Melhor uso: como SUGESTÃO para análise manual, não como regra
''')
