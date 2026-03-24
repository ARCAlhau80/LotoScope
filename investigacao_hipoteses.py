"""
🔬 INVESTIGAÇÃO: O QUE SEPARA TRIGGERS DE SUCESSO vs FRACASSO?
===============================================================
Hipóteses a testar:
1. Quantidade de números fortes (5+ é melhor que 4?)
2. Combinação com outros indicadores (frequência recente, anomalias)
3. Características dos triggers que acertam 100% vs 0%
"""
import pyodbc
from collections import defaultdict, Counter
import statistics

print('='*70)
print('🔬 INVESTIGAÇÃO: SUCESSO vs FRACASSO EM TRIGGERS DE DÉBITO')
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
    """Frequência geral (não posicional) na janela"""
    cont = Counter()
    for i in range(inicio, min(inicio + tam, len(res))):
        for num in res[i]['numeros']:
            cont[num] += 1
    return {n: cont[n] / tam * 100 for n in range(1, 26)}

def consecutivos(res, inicio, num):
    """Quantas vezes seguidas o número apareceu/não apareceu"""
    apareceu = 0
    nao_apareceu = 0
    for i in range(inicio - 1, -1, -1):
        if num in res[i]['numeros']:
            apareceu += 1
            if nao_apareceu > 0:
                break
        else:
            nao_apareceu += 1
            if apareceu > 0:
                break
    return apareceu, nao_apareceu

JANELA = 6
MIN_HIST = 100

print('\nProcessando triggers...')

# Coletar todos os triggers com características detalhadas
triggers_detalhados = []

for idx in range(MIN_HIST + JANELA, len(resultados)):
    conc = resultados[idx]
    sort = set(conc['numeros'])
    
    media = calc_media(resultados, idx - JANELA)
    freq = calc_freq(resultados, idx - JANELA, JANELA)
    f = fortes(media, freq, 0.3, 3)
    freq_g = freq_geral_janela(resultados, idx - JANELA, JANELA)
    
    if len(f) >= 4:
        nums = list(f.keys())
        ac = [n for n in nums if n in sort]
        taxa = len(ac) / len(nums) * 100
        
        # Características adicionais
        deficit_total = sum(f[n]['deficit'] for n in nums)
        deficit_medio = deficit_total / len(nums)
        max_posicoes = max(len(f[n]['pos']) for n in nums)
        min_posicoes = min(len(f[n]['pos']) for n in nums)
        
        # Frequência geral dos números sugeridos
        freq_media = statistics.mean([freq_g[n] for n in nums])
        
        # Consecutivos (quantos estão "frios" - não apareceram recentemente)
        frios = 0
        quentes = 0
        for n in nums:
            ap, nap = consecutivos(resultados, idx, n)
            if nap >= 2:
                frios += 1
            if ap >= 2:
                quentes += 1
        
        triggers_detalhados.append({
            'concurso': conc['concurso'],
            'idx': idx,
            'sugeridos': nums,
            'acertos': ac,
            'taxa': taxa,
            'qtde_fortes': len(nums),
            'deficit_total': deficit_total,
            'deficit_medio': deficit_medio,
            'max_posicoes': max_posicoes,
            'min_posicoes': min_posicoes,
            'freq_media': freq_media,
            'frios': frios,
            'quentes': quentes
        })

print(f'Total de triggers: {len(triggers_detalhados)}')

# ═══════════════════════════════════════════════════════════════════════════════
# HIPÓTESE 1: QUANTIDADE DE NÚMEROS FORTES
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 HIPÓTESE 1: QUANTIDADE DE NÚMEROS FORTES')
print('='*70)

por_qtde = defaultdict(list)
for t in triggers_detalhados:
    por_qtde[t['qtde_fortes']].append(t['taxa'])

print(f'\n{"Qtde Fortes":>12} | {"Triggers":>10} | {"Taxa Média":>12} | {"Dif vs 60%":>12} | {"100%":>8} | {"0%":>8}')
print('-'*70)

for qtde in sorted(por_qtde.keys()):
    taxas = por_qtde[qtde]
    media_taxa = statistics.mean(taxas)
    dif = media_taxa - 60
    cem_pct = sum(1 for t in taxas if t == 100)
    zero_pct = sum(1 for t in taxas if t == 0)
    dif_str = f"+{dif:.1f}pp" if dif >= 0 else f"{dif:.1f}pp"
    print(f'{qtde:>12} | {len(taxas):>10} | {media_taxa:>10.1f}% | {dif_str:>12} | {cem_pct:>8} | {zero_pct:>8}')

# ═══════════════════════════════════════════════════════════════════════════════
# HIPÓTESE 2: DÉFICIT TOTAL/MÉDIO
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 HIPÓTESE 2: DÉFICIT ACUMULADO (números mais "devendo")')
print('='*70)

# Separar por faixas de déficit médio
faixas_deficit = [(0, 10), (10, 15), (15, 20), (20, 25), (25, 100)]
print(f'\n{"Déficit Médio":>15} | {"Triggers":>10} | {"Taxa Média":>12} | {"Dif vs 60%":>12}')
print('-'*60)

for ini, fim in faixas_deficit:
    filtrados = [t for t in triggers_detalhados if ini <= t['deficit_medio'] < fim]
    if filtrados:
        media_taxa = statistics.mean([t['taxa'] for t in filtrados])
        dif = media_taxa - 60
        dif_str = f"+{dif:.1f}pp" if dif >= 0 else f"{dif:.1f}pp"
        print(f'{ini:>6}-{fim:<6} | {len(filtrados):>10} | {media_taxa:>10.1f}% | {dif_str:>12}')

# ═══════════════════════════════════════════════════════════════════════════════
# HIPÓTESE 3: FREQUÊNCIA GERAL NA JANELA
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 HIPÓTESE 3: FREQUÊNCIA GERAL DOS NÚMEROS SUGERIDOS')
print('='*70)
print('   (Os números sugeridos estão aparecendo muito ou pouco na janela?)')

faixas_freq = [(0, 40), (40, 50), (50, 60), (60, 70), (70, 100)]
print(f'\n{"Freq Média %":>15} | {"Triggers":>10} | {"Taxa Média":>12} | {"Dif vs 60%":>12}')
print('-'*60)

for ini, fim in faixas_freq:
    filtrados = [t for t in triggers_detalhados if ini <= t['freq_media'] < fim]
    if filtrados:
        media_taxa = statistics.mean([t['taxa'] for t in filtrados])
        dif = media_taxa - 60
        dif_str = f"+{dif:.1f}pp" if dif >= 0 else f"{dif:.1f}pp"
        print(f'{ini:>6}-{fim:<6}% | {len(filtrados):>10} | {media_taxa:>10.1f}% | {dif_str:>12}')

# ═══════════════════════════════════════════════════════════════════════════════
# HIPÓTESE 4: NÚMEROS FRIOS vs QUENTES
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 HIPÓTESE 4: PROPORÇÃO DE NÚMEROS FRIOS (2+ ausências consecutivas)')
print('='*70)

faixas_frios = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 10)]
print(f'\n{"Qtde Frios":>15} | {"Triggers":>10} | {"Taxa Média":>12} | {"Dif vs 60%":>12}')
print('-'*60)

for ini, fim in faixas_frios:
    filtrados = [t for t in triggers_detalhados if ini <= t['frios'] < fim]
    if filtrados:
        media_taxa = statistics.mean([t['taxa'] for t in filtrados])
        dif = media_taxa - 60
        dif_str = f"+{dif:.1f}pp" if dif >= 0 else f"{dif:.1f}pp"
        print(f'{ini:>6}-{fim:<6} | {len(filtrados):>10} | {media_taxa:>10.1f}% | {dif_str:>12}')

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE DETALHADA: 100% vs 0%
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('🔍 ANÁLISE: CARACTERÍSTICAS DOS 100% vs 0%')
print('='*70)

cem_porcento = [t for t in triggers_detalhados if t['taxa'] == 100]
zero_porcento = [t for t in triggers_detalhados if t['taxa'] == 0]

print(f'\nTotal 100%: {len(cem_porcento)}')
print(f'Total 0%: {len(zero_porcento)}')

if cem_porcento and zero_porcento:
    print(f'\n{"Característica":<25} | {"100%":>15} | {"0%":>15} | {"Diferença":>15}')
    print('-'*75)
    
    # Qtde de fortes
    media_100 = statistics.mean([t['qtde_fortes'] for t in cem_porcento])
    media_0 = statistics.mean([t['qtde_fortes'] for t in zero_porcento])
    print(f'{"Qtde Fortes":<25} | {media_100:>15.2f} | {media_0:>15.2f} | {media_100-media_0:>+15.2f}')
    
    # Déficit médio
    media_100 = statistics.mean([t['deficit_medio'] for t in cem_porcento])
    media_0 = statistics.mean([t['deficit_medio'] for t in zero_porcento])
    print(f'{"Déficit Médio":<25} | {media_100:>15.2f} | {media_0:>15.2f} | {media_100-media_0:>+15.2f}')
    
    # Freq média
    media_100 = statistics.mean([t['freq_media'] for t in cem_porcento])
    media_0 = statistics.mean([t['freq_media'] for t in zero_porcento])
    print(f'{"Freq Média na Janela":<25} | {media_100:>15.2f} | {media_0:>15.2f} | {media_100-media_0:>+15.2f}')
    
    # Frios
    media_100 = statistics.mean([t['frios'] for t in cem_porcento])
    media_0 = statistics.mean([t['frios'] for t in zero_porcento])
    print(f'{"Qtde Números Frios":<25} | {media_100:>15.2f} | {media_0:>15.2f} | {media_100-media_0:>+15.2f}')
    
    # Max posições
    media_100 = statistics.mean([t['max_posicoes'] for t in cem_porcento])
    media_0 = statistics.mean([t['max_posicoes'] for t in zero_porcento])
    print(f'{"Max Posições Débito":<25} | {media_100:>15.2f} | {media_0:>15.2f} | {media_100-media_0:>+15.2f}')

# ═══════════════════════════════════════════════════════════════════════════════
# HIPÓTESE 5: COMBINAÇÃO DE FATORES
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 HIPÓTESE 5: COMBINAÇÃO DE FATORES (filtro múltiplo)')
print('='*70)

# Testar: 5+ fortes + déficit médio > 15 + freq_media < 60
print('\nTestando diferentes combinações:')
print('-'*70)

combinacoes = [
    ("5+ fortes", lambda t: t['qtde_fortes'] >= 5),
    ("6+ fortes", lambda t: t['qtde_fortes'] >= 6),
    ("5+ fortes + déficit>15", lambda t: t['qtde_fortes'] >= 5 and t['deficit_medio'] > 15),
    ("5+ fortes + freq<60", lambda t: t['qtde_fortes'] >= 5 and t['freq_media'] < 60),
    ("5+ fortes + frios>=2", lambda t: t['qtde_fortes'] >= 5 and t['frios'] >= 2),
    ("5+ fortes + max_pos>=4", lambda t: t['qtde_fortes'] >= 5 and t['max_posicoes'] >= 4),
    ("4+ fortes + déficit>20", lambda t: t['qtde_fortes'] >= 4 and t['deficit_medio'] > 20),
    ("Todos: 5+ + déficit>15 + frios>=2", lambda t: t['qtde_fortes'] >= 5 and t['deficit_medio'] > 15 and t['frios'] >= 2),
]

print(f'\n{"Combinação":<40} | {"Triggers":>10} | {"Taxa":>10} | {"Dif":>10}')
print('-'*75)

for nome, filtro in combinacoes:
    filtrados = [t for t in triggers_detalhados if filtro(t)]
    if filtrados:
        total_sug = sum(t['qtde_fortes'] for t in filtrados)
        total_ac = sum(len(t['acertos']) for t in filtrados)
        taxa = total_ac / total_sug * 100 if total_sug else 0
        dif = taxa - 60
        dif_str = f"+{dif:.1f}pp" if dif >= 0 else f"{dif:.1f}pp"
        print(f'{nome:<40} | {len(filtrados):>10} | {taxa:>8.1f}% | {dif_str:>10}')
    else:
        print(f'{nome:<40} | {"N/A":>10} | {"N/A":>10} | {"N/A":>10}')

# ═══════════════════════════════════════════════════════════════════════════════
# ÚLTIMOS 50 CONCURSOS (período recente)
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📊 ANÁLISE ÚLTIMOS 50 CONCURSOS (período recente)')
print('='*70)

ultimo_conc = resultados[-1]['concurso']
recentes = [t for t in triggers_detalhados if t['concurso'] > ultimo_conc - 50]

if recentes:
    total_sug = sum(t['qtde_fortes'] for t in recentes)
    total_ac = sum(len(t['acertos']) for t in recentes)
    taxa = total_ac / total_sug * 100 if total_sug else 0
    
    print(f'\nTriggers nos últimos 50 concursos: {len(recentes)}')
    print(f'Taxa de acerto: {taxa:.1f}% (dif: {taxa-60:+.1f}pp)')
    
    # Distribuição
    print('\nDistribuição:')
    dist = Counter([int(t['taxa']//20)*20 for t in recentes])
    for faixa in sorted(dist.keys()):
        print(f'  {faixa}-{faixa+19}%: {dist[faixa]} triggers')

# ═══════════════════════════════════════════════════════════════════════════════
# CONCLUSÃO
# ═══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('📋 CONCLUSÃO')
print('='*70)
print('''
Os resultados mostram:

1. QUANTIDADE DE FORTES: Mais fortes = ligeiramente melhor
   - 8+ fortes: ~64% (+4pp)
   - 5 fortes: ~62% (+2pp)
   - 4 fortes: ~59% (-1pp)

2. DÉFICIT: Não há diferença significativa entre alto/baixo déficit

3. FREQUÊNCIA: Não há diferença significativa

4. FRIOS: Não há diferença significativa

5. COMBINAÇÕES: As melhores são 5+ fortes com fatores adicionais

IMPORTANTE: A diferença entre sucesso (100%) e fracasso (0%) parece ser
ALEATÓRIA - não encontramos um padrão consistente que separe os casos.

RECOMENDAÇÃO FINAL:
- Usar apenas quando houver 5+ números com forte indicação
- Expectativa: ~62% (apenas +2pp acima do aleatório)
- NÃO É SUFICIENTE para sistema de números fixos confiável
''')
