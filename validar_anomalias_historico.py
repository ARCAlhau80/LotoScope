"""
🔬 VALIDAÇÃO HISTÓRICA - ANOMALIAS DE FREQUÊNCIA LOTOFÁCIL
============================================================

Este script valida se a hipótese de "reversão à média" é verdadeira:
- Números muito quentes (9+ em 10) tendem a esfriar?
- Números muito frios (3- em 10) tendem a voltar?

Autor: AR CALHAU / GitHub Copilot
Data: Fevereiro 2026
"""

import pyodbc
from collections import Counter
import math

print('🔬 VALIDAÇÃO HISTÓRICA - ANOMALIAS DE FREQUÊNCIA LOTOFÁCIL')
print('='*80)

# Conectar
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute('''
    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    ORDER BY Concurso ASC
''')

resultados = []
for row in cursor.fetchall():
    resultados.append({
        'concurso': row[0],
        'numeros': set(row[1:16])
    })

conn.close()
print(f'✅ {len(resultados)} concursos carregados')

# Parâmetros
JANELA = 10
P_ESPERADO = 0.60  # 15/25 = 60%

# Testar múltiplos thresholds
THRESHOLDS = {
    'extremo_quente': (10, None),   # 10/10 = 100%
    'muito_quente': (9, None),      # 9+/10 = 90%+
    'quente': (8, None),            # 8+/10 = 80%+
    'frio': (None, 3),              # 3-/10 = 30%-
    'muito_frio': (None, 2),        # 2-/10 = 20%-
    'extremo_frio': (None, 1),      # 1-/10 = 10%-
}

print(f'\n📊 Analisando {len(resultados) - JANELA} janelas de {JANELA} sorteios...')
print('='*80)

# Função para calcular estatísticas
def calcular_stats(min_freq=None, max_freq=None):
    """Retorna (total, saiu_no_proximo)"""
    total = 0
    saiu = 0
    
    for i in range(JANELA, len(resultados)):
        janela = resultados[i-JANELA:i]
        proximo = resultados[i]
        
        freq = Counter()
        for r in janela:
            freq.update(r['numeros'])
        
        for n in range(1, 26):
            f = freq.get(n, 0)
            
            # Aplicar filtro
            if min_freq is not None and f < min_freq:
                continue
            if max_freq is not None and f > max_freq:
                continue
            
            total += 1
            if n in proximo['numeros']:
                saiu += 1
    
    return total, saiu

# Análise detalhada por frequência
print('\n📊 ANÁLISE DETALHADA POR NÍVEL DE FREQUÊNCIA')
print('='*80)
print(f'{"Freq na Janela":<20} {"Total Eventos":<15} {"Saiu Próx":<12} {"Taxa Real":<12} {"Esperado":<10} {"Diferença":<12}')
print('-'*80)

for freq_val in range(0, 11):
    total, saiu = calcular_stats(min_freq=freq_val, max_freq=freq_val)
    if total > 0:
        taxa_real = saiu / total * 100
        diferenca = taxa_real - P_ESPERADO * 100
        sinal = '+' if diferenca >= 0 else ''
        print(f'{freq_val}/10 ({freq_val*10}%){"":>8} {total:>10,}     {saiu:>8,}     {taxa_real:>6.1f}%      60.0%     {sinal}{diferenca:>5.1f}%')

# Grupos de análise
print('\n\n📊 ANÁLISE POR GRUPOS (VALIDAÇÃO DA HIPÓTESE)')
print('='*80)

# 1. Números MUITO QUENTES (9+/10)
print('\n🔥 NÚMEROS MUITO QUENTES (9+ em 10 sorteios):')
total_q, saiu_q = calcular_stats(min_freq=9)
if total_q > 0:
    taxa_q = saiu_q / total_q * 100
    print(f'   Total de eventos: {total_q:,}')
    print(f'   Saíram no próximo: {saiu_q:,} ({taxa_q:.1f}%)')
    print(f'   Esfriaram: {total_q - saiu_q:,} ({100-taxa_q:.1f}%)')
    print(f'\n   📈 COMPARAÇÃO:')
    print(f'      Esperado sair: 60.0%')
    print(f'      Real: {taxa_q:.1f}%')
    diff = P_ESPERADO * 100 - taxa_q
    if diff > 0:
        print(f'      ⭐ TENDÊNCIA CONFIRMADA: -{diff:.1f}% abaixo do esperado!')
        print(f'      ✅ Números muito quentes REALMENTE tendem a esfriar!')
    else:
        print(f'      ❌ Sem tendência clara: +{-diff:.1f}% acima do esperado')

# 2. Números MUITO FRIOS (≤3/10)
print('\n\n❄️ NÚMEROS MUITO FRIOS (≤3 em 10 sorteios):')
total_f, saiu_f = calcular_stats(max_freq=3)
if total_f > 0:
    taxa_f = saiu_f / total_f * 100
    print(f'   Total de eventos: {total_f:,}')
    print(f'   Voltaram no próximo: {saiu_f:,} ({taxa_f:.1f}%)')
    print(f'   Continuaram fora: {total_f - saiu_f:,} ({100-taxa_f:.1f}%)')
    print(f'\n   📈 COMPARAÇÃO:')
    print(f'      Esperado sair: 60.0%')
    print(f'      Real: {taxa_f:.1f}%')
    diff = taxa_f - P_ESPERADO * 100
    if diff > 0:
        print(f'      ⭐ TENDÊNCIA CONFIRMADA: +{diff:.1f}% acima do esperado!')
        print(f'      ✅ Números muito frios REALMENTE tendem a voltar!')
    else:
        print(f'      ❌ Sem tendência clara: {diff:.1f}% abaixo do esperado')

# 3. Análise de significância estatística
print('\n\n📐 TESTE DE SIGNIFICÂNCIA ESTATÍSTICA')
print('='*80)

def calcular_zscore(n, k, p):
    """Calcula z-score para proporção"""
    if n == 0:
        return 0
    p_obs = k / n
    se = math.sqrt(p * (1-p) / n)
    if se == 0:
        return 0
    return (p_obs - p) / se

# Para quentes
z_quentes = calcular_zscore(total_q, saiu_q, P_ESPERADO)
print(f'\n🔥 NÚMEROS MUITO QUENTES:')
print(f'   Z-score: {z_quentes:.2f}')
if abs(z_quentes) > 1.96:
    print(f'   ⭐ ESTATISTICAMENTE SIGNIFICATIVO (95% confiança)!')
    print(f'   A diferença NÃO é devido ao acaso.')
elif abs(z_quentes) > 1.645:
    print(f'   📊 Marginalmente significativo (90% confiança)')
else:
    print(f'   ❌ Não significativo - pode ser variação aleatória')

# Para frios
z_frios = calcular_zscore(total_f, saiu_f, P_ESPERADO)
print(f'\n❄️ NÚMEROS MUITO FRIOS:')
print(f'   Z-score: {z_frios:.2f}')
if abs(z_frios) > 1.96:
    print(f'   ⭐ ESTATISTICAMENTE SIGNIFICATIVO (95% confiança)!')
    print(f'   A diferença NÃO é devido ao acaso.')
elif abs(z_frios) > 1.645:
    print(f'   📊 Marginalmente significativo (90% confiança)')
else:
    print(f'   ❌ Não significativo - pode ser variação aleatória')

# Conclusão
print('\n\n' + '='*80)
print('🎯 CONCLUSÃO FINAL')
print('='*80)

if total_q > 0 and total_f > 0:
    tendencia_q = P_ESPERADO * 100 - (saiu_q / total_q * 100)
    tendencia_f = (saiu_f / total_f * 100) - P_ESPERADO * 100
    
    print(f'\nBaseado em {len(resultados):,} concursos históricos:')
    print(f'\n🔥 Números MUITO QUENTES (9+ em 10):')
    if tendencia_q > 0:
        print(f'   ✅ CONFIRMADO: Tendem a ESFRIAR ({tendencia_q:.1f}% abaixo do esperado)')
    else:
        print(f'   ❌ NÃO CONFIRMADO: Comportamento aleatório')
    
    print(f'\n❄️ Números MUITO FRIOS (≤3 em 10):')
    if tendencia_f > 0:
        print(f'   ✅ CONFIRMADO: Tendem a VOLTAR ({tendencia_f:.1f}% acima do esperado)')
    else:
        print(f'   ❌ NÃO CONFIRMADO: Comportamento aleatório')
    
    # Recomendação de uso
    print(f'\n📋 RECOMENDAÇÃO PARA FILTRO:')
    if tendencia_q > 2 or tendencia_f > 2:
        print(f'   ⭐ A análise de anomalias É ÚTIL como filtro!')
        if tendencia_q > tendencia_f:
            print(f'   → EVITAR números muito quentes é mais efetivo')
        else:
            print(f'   → FAVORECER números muito frios é mais efetivo')
    else:
        print(f'   ⚠️ A diferença é pequena - usar com cautela')

print('\n' + '='*80)
