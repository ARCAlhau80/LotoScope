"""
VALIDAÇÃO DO CONCEITO: DÉBITO POSICIONAL
=========================================

Hipótese: Se um número está "devendo" em uma posição específica
(frequência recente < média histórica), ele tende a sair nessa posição
nos próximos concursos.

Metodologia:
1. Calcular média histórica de cada número em cada posição
2. Para cada ponto no tempo, calcular frequência em janela recente (5 concursos)
3. Identificar "débitos" (freq_recente < media_historica * 0.5)
4. Verificar se o número aparece nessa posição nos próximos X concursos
"""

import pyodbc
from collections import defaultdict
import statistics

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

print("="*80)
print("🔬 VALIDAÇÃO: DÉBITO POSICIONAL")
print("="*80)

# Carregar dados
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    ORDER BY Concurso ASC
""")

resultados = []
for row in cursor.fetchall():
    resultados.append({
        'concurso': row[0],
        'numeros': list(row[1:16])  # N1 a N15 em ordem
    })

conn.close()
print(f"📊 {len(resultados)} concursos carregados")

# ═══════════════════════════════════════════════════════════════════════════════
# PASSO 1: CALCULAR MÉDIA HISTÓRICA POR NÚMERO/POSIÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_media_historica(resultados, ate_concurso_idx):
    """Calcula a frequência média de cada número em cada posição até um ponto."""
    contagem = defaultdict(lambda: defaultdict(int))  # {numero: {posicao: count}}
    total = ate_concurso_idx
    
    for i in range(ate_concurso_idx):
        for pos in range(15):
            num = resultados[i]['numeros'][pos]
            contagem[num][pos+1] += 1
    
    # Converter para percentual
    media = defaultdict(lambda: defaultdict(float))
    for num in range(1, 26):
        for pos in range(1, 16):
            media[num][pos] = contagem[num][pos] / total * 100 if total > 0 else 0
    
    return media

def calcular_frequencia_janela(resultados, inicio_idx, tamanho_janela):
    """Calcula frequência de cada número em cada posição numa janela."""
    contagem = defaultdict(lambda: defaultdict(int))
    
    for i in range(inicio_idx, min(inicio_idx + tamanho_janela, len(resultados))):
        for pos in range(15):
            num = resultados[i]['numeros'][pos]
            contagem[num][pos+1] += 1
    
    # Converter para percentual
    freq = defaultdict(lambda: defaultdict(float))
    for num in range(1, 26):
        for pos in range(1, 16):
            freq[num][pos] = contagem[num][pos] / tamanho_janela * 100
    
    return freq

def identificar_debitos(media_historica, freq_recente, limiar=0.3):
    """
    Identifica números em "débito" em posições específicas.
    Débito = freq_recente < media_historica * limiar
    """
    debitos = []
    
    for num in range(1, 26):
        for pos in range(1, 16):
            media = media_historica[num][pos]
            recente = freq_recente[num][pos]
            
            # Só considerar posições onde o número tem presença histórica significativa
            if media >= 5:  # Pelo menos 5% de presença histórica
                if recente < media * limiar:  # Está muito abaixo da média
                    debitos.append({
                        'numero': num,
                        'posicao': pos,
                        'media_historica': media,
                        'freq_recente': recente,
                        'deficit': media - recente
                    })
    
    # Ordenar por maior déficit
    debitos.sort(key=lambda x: x['deficit'], reverse=True)
    return debitos

# ═══════════════════════════════════════════════════════════════════════════════
# PASSO 2: VALIDAR NO HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("🔍 VALIDANDO CONCEITO NO HISTÓRICO")
print("="*80)

JANELA_ANALISE = 5  # Últimos 5 concursos para calcular freq recente
JANELA_VALIDACAO = 3  # Próximos 3 concursos para validar
MIN_HISTORICO = 100  # Começar após 100 concursos (base estatística)

acertos_total = 0
testes_total = 0
acertos_por_posicao = defaultdict(lambda: {'acertos': 0, 'testes': 0})
acertos_por_numero = defaultdict(lambda: {'acertos': 0, 'testes': 0})

print(f"\n   Janela de análise: {JANELA_ANALISE} concursos")
print(f"   Janela de validação: {JANELA_VALIDACAO} concursos")
print(f"   Início: após concurso {MIN_HISTORICO}")
print(f"   Testando {len(resultados) - MIN_HISTORICO - JANELA_ANALISE - JANELA_VALIDACAO} pontos...")

# Para cada ponto no tempo
for ponto in range(MIN_HISTORICO, len(resultados) - JANELA_ANALISE - JANELA_VALIDACAO):
    # Média histórica até este ponto
    media_hist = calcular_media_historica(resultados, ponto)
    
    # Frequência na janela recente (últimos 5)
    freq_rec = calcular_frequencia_janela(resultados, ponto, JANELA_ANALISE)
    
    # Identificar débitos
    debitos = identificar_debitos(media_hist, freq_rec, limiar=0.3)
    
    # Pegar top 10 maiores débitos
    top_debitos = debitos[:10]
    
    # Validar nos próximos concursos
    for deb in top_debitos:
        num = deb['numero']
        pos = deb['posicao']
        
        # Verificar se o número aparece nessa posição nos próximos X concursos
        acertou = False
        for i in range(JANELA_VALIDACAO):
            idx = ponto + JANELA_ANALISE + i
            if idx < len(resultados):
                numero_na_posicao = resultados[idx]['numeros'][pos-1]
                if numero_na_posicao == num:
                    acertou = True
                    break
        
        testes_total += 1
        acertos_por_posicao[pos]['testes'] += 1
        acertos_por_numero[num]['testes'] += 1
        
        if acertou:
            acertos_total += 1
            acertos_por_posicao[pos]['acertos'] += 1
            acertos_por_numero[num]['acertos'] += 1

# ═══════════════════════════════════════════════════════════════════════════════
# PASSO 3: RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📊 RESULTADOS DA VALIDAÇÃO")
print("="*80)

taxa_geral = acertos_total / testes_total * 100 if testes_total > 0 else 0
print(f"\n   🎯 TAXA GERAL DE ACERTO: {taxa_geral:.1f}%")
print(f"   📈 Acertos: {acertos_total} de {testes_total} testes")

# Calcular baseline (chance aleatória)
# Para cada posição, a chance de um número específico aparecer é aproximadamente:
# Depende da posição, mas em média ~15/25 * 1/15 = 4% por número/posição
print(f"\n   📉 Baseline (aleatório): ~4-6% por número/posição")
print(f"   📊 Melhoria: {taxa_geral / 5:.1f}x vs aleatório")

# Por posição
print("\n" + "-"*60)
print("📍 TAXA DE ACERTO POR POSIÇÃO:")
print("-"*60)

posicoes_ordenadas = sorted(acertos_por_posicao.items(), 
                           key=lambda x: x[1]['acertos']/x[1]['testes'] if x[1]['testes'] > 0 else 0,
                           reverse=True)

for pos, dados in posicoes_ordenadas:
    if dados['testes'] > 10:
        taxa = dados['acertos'] / dados['testes'] * 100
        barra = "█" * int(taxa/2)
        print(f"   N{pos:02d}: {taxa:5.1f}% ({dados['acertos']:4d}/{dados['testes']:4d}) {barra}")

# Por número (top 10)
print("\n" + "-"*60)
print("🔢 TAXA DE ACERTO POR NÚMERO (Top 10):")
print("-"*60)

numeros_ordenados = sorted(acertos_por_numero.items(),
                          key=lambda x: x[1]['acertos']/x[1]['testes'] if x[1]['testes'] > 0 else 0,
                          reverse=True)

for num, dados in numeros_ordenados[:10]:
    if dados['testes'] > 10:
        taxa = dados['acertos'] / dados['testes'] * 100
        barra = "█" * int(taxa/2)
        print(f"   Nº {num:02d}: {taxa:5.1f}% ({dados['acertos']:4d}/{dados['testes']:4d}) {barra}")

# ═══════════════════════════════════════════════════════════════════════════════
# PASSO 4: TESTE COM DIFERENTES LIMIARES
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("🔬 TESTANDO DIFERENTES LIMIARES DE DÉBITO")
print("="*80)

for limiar in [0.1, 0.2, 0.3, 0.5, 0.7]:
    acertos = 0
    testes = 0
    
    for ponto in range(MIN_HISTORICO, len(resultados) - JANELA_ANALISE - JANELA_VALIDACAO, 10):  # Pular de 10 em 10
        media_hist = calcular_media_historica(resultados, ponto)
        freq_rec = calcular_frequencia_janela(resultados, ponto, JANELA_ANALISE)
        debitos = identificar_debitos(media_hist, freq_rec, limiar=limiar)
        
        for deb in debitos[:5]:  # Top 5
            num = deb['numero']
            pos = deb['posicao']
            
            for i in range(JANELA_VALIDACAO):
                idx = ponto + JANELA_ANALISE + i
                if idx < len(resultados):
                    if resultados[idx]['numeros'][pos-1] == num:
                        acertos += 1
                        break
            testes += 1
    
    taxa = acertos / testes * 100 if testes > 0 else 0
    barra = "█" * int(taxa)
    print(f"   Limiar {limiar:.1f}: {taxa:5.1f}% ({acertos}/{testes}) {barra}")

# ═══════════════════════════════════════════════════════════════════════════════
# PASSO 5: EXEMPLO PRÁTICO COM ÚLTIMOS CONCURSOS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("🎯 EXEMPLO PRÁTICO - DÉBITOS ATUAIS")
print("="*80)

# Usar todo histórico como média
media_total = calcular_media_historica(resultados, len(resultados) - JANELA_ANALISE)

# Frequência dos últimos 5 concursos
freq_ultimos = calcular_frequencia_janela(resultados, len(resultados) - JANELA_ANALISE, JANELA_ANALISE)

# Identificar débitos atuais
debitos_atuais = identificar_debitos(media_total, freq_ultimos, limiar=0.3)

print(f"\n   Baseado nos últimos {JANELA_ANALISE} concursos:")
print(f"   Último concurso analisado: {resultados[-1]['concurso']}")

print("\n   TOP 15 DÉBITOS POSICIONAIS (maior potencial):")
print("   " + "-"*65)
print(f"   {'Nº':>3} | {'Pos':>4} | {'Média Hist':>10} | {'Freq Rec':>10} | {'Déficit':>8}")
print("   " + "-"*65)

for deb in debitos_atuais[:15]:
    print(f"   {deb['numero']:3d} |  N{deb['posicao']:<2d} | {deb['media_historica']:9.1f}% | {deb['freq_recente']:9.1f}% | {deb['deficit']:+7.1f}%")

print("\n" + "="*80)
print("💡 CONCLUSÃO")
print("="*80)

if taxa_geral > 10:
    print(f"""
   ✅ CONCEITO VALIDADO!
   
   Taxa de acerto: {taxa_geral:.1f}% (vs ~5% aleatório)
   Melhoria: {taxa_geral/5:.1f}x sobre o baseline
   
   O conceito de "débito posicional" tem valor preditivo.
   Números que estão devendo em posições específicas tendem
   a aparecer nessas posições nos próximos concursos.
""")
elif taxa_geral > 5:
    print(f"""
   ⚠️ CONCEITO PARCIALMENTE VÁLIDO
   
   Taxa de acerto: {taxa_geral:.1f}% (vs ~5% aleatório)
   Melhoria modesta sobre o baseline.
   
   Pode ser útil como filtro complementar, mas não como
   indicador principal.
""")
else:
    print(f"""
   ❌ CONCEITO NÃO VALIDADO
   
   Taxa de acerto: {taxa_geral:.1f}% (similar ao aleatório)
   Sem vantagem estatística significativa.
""")

print("="*80)
