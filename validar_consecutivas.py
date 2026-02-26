"""
🔬 ANÁLISE APROFUNDADA - CONSECUTIVAS E EXTREMOS
Validação detalhada de padrões temporais na Lotofácil
"""

import pyodbc
from collections import Counter

print('🔬 ANÁLISE APROFUNDADA - CONSECUTIVAS E EXTREMOS')
print('='*80)

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute('SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 FROM Resultados_INT ORDER BY Concurso ASC')
resultados = [{'concurso': row[0], 'numeros': set(row[1:16])} for row in cursor.fetchall()]
conn.close()
print(f'Concursos: {len(resultados):,}')

# 1. ANÁLISE DE CONSECUTIVAS
print('\n' + '='*80)
print('🔄 ANÁLISE DE CONSECUTIVAS')
print('Se um número saiu N vezes seguidas, qual a chance de sair de novo?')
print('='*80)

def contar_consecutivas(resultados, numero, fim_idx):
    """Conta quantas vezes o número saiu consecutivamente antes de fim_idx"""
    count = 0
    for i in range(fim_idx - 1, -1, -1):
        if numero in resultados[i]['numeros']:
            count += 1
        else:
            break
    return count

stats_consec = {}
for consec in range(1, 12):
    stats_consec[consec] = {'total': 0, 'saiu': 0}

for i in range(1, len(resultados)):
    proximo = resultados[i]
    for n in range(1, 26):
        consec = contar_consecutivas(resultados, n, i)
        if consec > 0 and consec <= 11:
            stats_consec[consec]['total'] += 1
            if n in proximo['numeros']:
                stats_consec[consec]['saiu'] += 1

print(f'\n{"Consecutivas":<15} {"Total":<12} {"Saiu":<10} {"Taxa":<10} {"vs 60%"}')
print('-'*60)
for consec in range(1, 11):
    s = stats_consec[consec]
    if s['total'] > 0:
        taxa = s['saiu'] / s['total'] * 100
        diff = taxa - 60
        sinal = '+' if diff >= 0 else ''
        print(f'{consec:<15} {s["total"]:>10,} {s["saiu"]:>8,} {taxa:>6.1f}%   {sinal}{diff:.1f}%')

# 2. ANÁLISE APÓS SEQUÊNCIAS LONGAS
print('\n' + '='*80)
print('🔥 O QUE ACONTECE APÓS MUITAS CONSECUTIVAS?')
print('(Esperado: 40% param, 60% continuam)')
print('='*80)

for limite in [4, 5, 6, 7, 8]:
    total = 0
    parou = 0
    for i in range(1, len(resultados)):
        for n in range(1, 26):
            consec = contar_consecutivas(resultados, n, i)
            if consec >= limite:
                total += 1
                if n not in resultados[i]['numeros']:
                    parou += 1
    
    if total > 0:
        taxa_parou = parou / total * 100
        diff = taxa_parou - 40  # Esperado é 40% parar
        sinal = '+' if diff >= 0 else ''
        tendencia = "⬆️ + chance parar" if diff > 2 else ("⬇️ - chance parar" if diff < -2 else "≈ normal")
        print(f'{limite}+ consec: {total:>5} eventos | {taxa_parou:.1f}% pararam | {sinal}{diff:.1f}% {tendencia}')

# 3. ANÁLISE DE AUSÊNCIA LONGA
print('\n' + '='*80)
print('❄️ O QUE ACONTECE APÓS AUSÊNCIA PROLONGADA?')
print('(Esperado: 60% voltam)')
print('='*80)

def contar_ausencia(resultados, numero, fim_idx):
    """Conta há quantos sorteios o número está ausente"""
    count = 0
    for i in range(fim_idx - 1, -1, -1):
        if numero not in resultados[i]['numeros']:
            count += 1
        else:
            break
    return count

for limite in [3, 4, 5, 6, 7, 8, 10]:
    total = 0
    voltou = 0
    for i in range(limite, len(resultados)):
        for n in range(1, 26):
            ausencia = contar_ausencia(resultados, n, i)
            if ausencia == limite:
                total += 1
                if n in resultados[i]['numeros']:
                    voltou += 1
    
    if total > 0:
        taxa_voltou = voltou / total * 100
        diff = taxa_voltou - 60  # Esperado é 60% voltar
        sinal = '+' if diff >= 0 else ''
        tendencia = "⬆️ + chance voltar" if diff > 2 else ("⬇️ - chance voltar" if diff < -2 else "≈ normal")
        print(f'{limite} ausências: {total:>5} eventos | {taxa_voltou:.1f}% voltaram | {sinal}{diff:.1f}% {tendencia}')

# 4. CONCLUSÃO
print('\n' + '='*80)
print('🎯 CONCLUSÃO DA ANÁLISE APROFUNDADA')
print('='*80)

# Calcular médias para análise
media_consec_alta = sum(stats_consec[c]['saiu']/stats_consec[c]['total']*100 for c in [5,6,7,8] if stats_consec[c]['total'] > 0) / 4
print(f'\nMédia de saída após 5-8 consecutivas: {media_consec_alta:.1f}% (esperado 60%)')

# Verificar padrão
if media_consec_alta > 60:
    print('📈 Números "quentes" CONTINUAM quentes na Lotofácil!')
    print('💡 A "falácia do jogador" não se aplica - é como moeda sem memória')
else:
    print('📉 Números "quentes" tendem a esfriar')
    print('💡 Pode haver leve reversão à média')

print('\n⚠️ IMPORTANTE: A Lotofácil é diferente da Mega-Sena porque')
print('   15 números de 25 (60%) vs 6 de 60 (10%) muda completamente a dinâmica!')
print('   Na Lotofácil, a alta probabilidade diminui o efeito de anomalias.')
