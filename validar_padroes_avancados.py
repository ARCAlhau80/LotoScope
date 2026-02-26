#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VALIDADOR DE PADRÕES MATEMÁTICOS AVANÇADOS
Testa múltiplos padrões como potenciais filtros redutores

Padrões testados:
1. Dígitos de Euler (e)
2. Dígitos de Pi (π)
3. Proporção Áurea (φ)
4. Números Triangulares
5. Números Quadrados Perfeitos
6. Números de Lucas
7. Números Consecutivos (sequências)
8. Lacunas (gaps) entre números
9. Números Perfeitos
10. Números Deficientes/Abundantes
"""

import pyodbc
from collections import Counter, defaultdict
from datetime import datetime
import statistics

def conectar_banco():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def carregar_resultados():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT ORDER BY Concurso ASC
    """)
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            'concurso': row[0],
            'numeros': sorted(row[1:16])
        })
    conn.close()
    return resultados

# ========================================
# DEFINIÇÃO DOS PADRÕES MATEMÁTICOS
# ========================================

# Euler (e = 2.71828182845904523536...)
# Dígitos únicos de 1-25: 2, 7, 1, 8, 2, 8, 1, 8, 2, 8, 4, 5, 9, 0, 4, 5, 2, 3, 5, 3, 6
EULER_DIGITOS = {2, 7, 1, 8, 4, 5, 9, 3, 6}  # Dígitos únicos que aparecem

# Pi (π = 3.14159265358979323846...)
# Dígitos únicos: 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6
PI_DIGITOS = {3, 1, 4, 5, 9, 2, 6, 8, 7}  # Dígitos únicos

# Proporção Áurea (φ = 1.61803398874989484820...)
PHI_DIGITOS = {1, 6, 8, 0, 3, 9, 7, 4, 2, 5}  # Dígitos únicos

# Números relacionados a Euler/Pi/Phi dentro de 1-25
EULER_RELACIONADOS = {2, 7, 8, 18, 27}  # 2.7..., números com 2,7,8
PI_RELACIONADOS = {3, 14, 15, 22}  # π≈3.14, 22/7
PHI_RELACIONADOS = {1, 2, 3, 5, 8, 13, 21}  # Fibonacci (φ relacionado)

# Números Triangulares: n(n+1)/2 → 1, 3, 6, 10, 15, 21
TRIANGULARES = {1, 3, 6, 10, 15, 21}

# Quadrados Perfeitos: 1, 4, 9, 16, 25
QUADRADOS = {1, 4, 9, 16, 25}

# Números de Lucas: 2, 1, 3, 4, 7, 11, 18 (similar a Fibonacci)
LUCAS = {2, 1, 3, 4, 7, 11, 18}

# Números Primos (já testado, mas incluir para comparação)
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

# Potências de 2: 1, 2, 4, 8, 16
POTENCIAS_2 = {1, 2, 4, 8, 16}

# Números Perfeitos (soma dos divisores = número): apenas 6 em 1-25
PERFEITOS = {6}  # 1+2+3=6

# Números Deficientes (soma divisores < número): maioria
# Números Abundantes (soma divisores > número): 12, 18, 20, 24
ABUNDANTES = {12, 18, 20, 24}

# Números em posições específicas do tabuleiro visual (5x5)
DIAGONAL_PRINCIPAL = {1, 7, 13, 19, 25}  # Se organizado em 5x5
DIAGONAL_SECUNDARIA = {5, 9, 13, 17, 21}
CENTRO_CRUZ = {3, 11, 12, 13, 14, 15, 23}  # Cruz central

# Múltiplos
MULT_4 = {4, 8, 12, 16, 20, 24}
MULT_6 = {6, 12, 18, 24}
MULT_7 = {7, 14, 21}

GRUPOS = {
    'EULER_DIG': EULER_DIGITOS,
    'PI_DIG': PI_DIGITOS,
    'PHI_DIG': PHI_DIGITOS,
    'TRIANGULAR': TRIANGULARES,
    'QUADRADOS': QUADRADOS,
    'LUCAS': LUCAS,
    'PRIMOS': PRIMOS,
    'POT_2': POTENCIAS_2,
    'ABUNDANTES': ABUNDANTES,
    'DIAG_PRINC': DIAGONAL_PRINCIPAL,
    'DIAG_SEC': DIAGONAL_SECUNDARIA,
    'CENTRO': CENTRO_CRUZ,
    'MULT_4': MULT_4,
    'MULT_6': MULT_6,
    'MULT_7': MULT_7,
}

def calcular_consecutivos(numeros):
    """Conta quantos pares de números consecutivos existem (ex: 3-4, 7-8)"""
    numeros = sorted(numeros)
    consecutivos = 0
    for i in range(len(numeros) - 1):
        if numeros[i+1] - numeros[i] == 1:
            consecutivos += 1
    return consecutivos

def calcular_sequencias(numeros):
    """Conta sequências de 3+ números consecutivos"""
    numeros = sorted(numeros)
    sequencias = 0
    seq_atual = 1
    
    for i in range(len(numeros) - 1):
        if numeros[i+1] - numeros[i] == 1:
            seq_atual += 1
        else:
            if seq_atual >= 3:
                sequencias += 1
            seq_atual = 1
    
    if seq_atual >= 3:
        sequencias += 1
    
    return sequencias

def calcular_maior_gap(numeros):
    """Calcula o maior gap entre números consecutivos"""
    numeros = sorted(numeros)
    maior_gap = 0
    for i in range(len(numeros) - 1):
        gap = numeros[i+1] - numeros[i]
        if gap > maior_gap:
            maior_gap = gap
    return maior_gap

def calcular_soma_gaps(numeros):
    """Soma de todos os gaps (relacionado à dispersão)"""
    numeros = sorted(numeros)
    return sum(numeros[i+1] - numeros[i] for i in range(len(numeros) - 1))

def analisar_grupo(resultados, nome, numeros_grupo):
    """Analisa estatísticas de um grupo"""
    acertos = []
    for r in resultados:
        nums_set = set(r['numeros'])
        acertos.append(len(numeros_grupo & nums_set))
    
    esperado = len(numeros_grupo) * (15/25)
    media = statistics.mean(acertos)
    
    return {
        'nome': nome,
        'numeros': sorted(numeros_grupo),
        'tamanho': len(numeros_grupo),
        'esperado': esperado,
        'media': media,
        'delta': media - esperado,
        'delta_pct': (media / esperado - 1) * 100 if esperado > 0 else 0,
        'distribuicao': Counter(acertos)
    }

def analisar_consecutivos(resultados):
    """Analisa padrões de números consecutivos"""
    stats = defaultdict(int)
    
    for r in resultados:
        n_consec = calcular_consecutivos(r['numeros'])
        stats[n_consec] += 1
    
    return dict(stats)

def analisar_sequencias(resultados):
    """Analisa sequências de 3+ consecutivos"""
    stats = defaultdict(int)
    
    for r in resultados:
        n_seq = calcular_sequencias(r['numeros'])
        stats[n_seq] += 1
    
    return dict(stats)

def analisar_gaps(resultados):
    """Analisa distribuição de gaps"""
    maior_gaps = []
    soma_gaps = []
    
    for r in resultados:
        maior_gaps.append(calcular_maior_gap(r['numeros']))
        soma_gaps.append(calcular_soma_gaps(r['numeros']))
    
    return {
        'maior_gap': {
            'media': statistics.mean(maior_gaps),
            'min': min(maior_gaps),
            'max': max(maior_gaps),
            'dist': Counter(maior_gaps)
        },
        'soma_gaps': {
            'media': statistics.mean(soma_gaps),
            'min': min(soma_gaps),
            'max': max(soma_gaps)
        }
    }

def main():
    print("\n" + "="*80)
    print("🔬 VALIDADOR DE PADRÕES MATEMÁTICOS AVANÇADOS")
    print("="*80)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    resultados = carregar_resultados()
    total = len(resultados)
    print(f"✅ {total} concursos carregados")
    
    # ========================================
    # ANÁLISE DE GRUPOS MATEMÁTICOS
    # ========================================
    print("\n" + "="*80)
    print("📊 ANÁLISE DE GRUPOS MATEMÁTICOS")
    print("="*80)
    
    analises = []
    for nome, numeros in GRUPOS.items():
        if numeros:  # Só se tiver números
            stats = analisar_grupo(resultados, nome, numeros)
            analises.append(stats)
    
    # Ordenar por delta absoluto
    analises.sort(key=lambda x: abs(x['delta_pct']), reverse=True)
    
    print(f"\n{'Grupo':<12} {'Números':<30} {'Tam':<4} {'Esper.':<7} {'Média':<7} {'Δ%':<8} {'Status'}")
    print("─"*95)
    
    for a in analises:
        nums_str = str(a['numeros'][:5]) + ('...' if len(a['numeros']) > 5 else '')
        
        if abs(a['delta_pct']) > 5:
            status = "⚠️ SIGNIFICATIVO"
        elif abs(a['delta_pct']) > 2:
            status = "📊 Leve"
        else:
            status = "➖ Normal"
        
        print(f"{a['nome']:<12} {nums_str:<30} {a['tamanho']:<4} {a['esperado']:<7.2f} {a['media']:<7.2f} {a['delta_pct']:>+6.1f}%  {status}")
    
    # ========================================
    # ANÁLISE DE CONSECUTIVOS
    # ========================================
    print("\n" + "="*80)
    print("📊 ANÁLISE DE NÚMEROS CONSECUTIVOS")
    print("="*80)
    
    consec_stats = analisar_consecutivos(resultados)
    
    print(f"\n🔢 Pares consecutivos (ex: 3-4, 12-13):")
    print(f"{'Pares':<10} {'Concursos':<12} {'%':<10} {'Barra'}")
    print("─"*50)
    
    for n_pares in sorted(consec_stats.keys()):
        count = consec_stats[n_pares]
        pct = count / total * 100
        bar = '█' * int(pct / 2)
        print(f"{n_pares:<10} {count:<12} {pct:<9.1f}% {bar}")
    
    # Faixa mais comum para filtro
    media_consec = sum(k * v for k, v in consec_stats.items()) / total
    print(f"\n📈 Média de pares consecutivos: {media_consec:.2f}")
    
    # Calcular cobertura de filtros
    for min_c, max_c in [(2, 5), (3, 5), (2, 4), (3, 4)]:
        cobertura = sum(consec_stats.get(i, 0) for i in range(min_c, max_c + 1)) / total * 100
        print(f"   Filtro {min_c}-{max_c} consecutivos: {cobertura:.1f}% cobertura")
    
    # ========================================
    # ANÁLISE DE SEQUÊNCIAS (3+ consecutivos)
    # ========================================
    print("\n" + "="*80)
    print("📊 ANÁLISE DE SEQUÊNCIAS (3+ consecutivos)")
    print("="*80)
    
    seq_stats = analisar_sequencias(resultados)
    
    print(f"\n🔢 Sequências de 3+ números (ex: 5-6-7):")
    print(f"{'Seqs':<10} {'Concursos':<12} {'%':<10}")
    print("─"*35)
    
    for n_seq in sorted(seq_stats.keys()):
        count = seq_stats[n_seq]
        pct = count / total * 100
        print(f"{n_seq:<10} {count:<12} {pct:.1f}%")
    
    # ========================================
    # ANÁLISE DE GAPS
    # ========================================
    print("\n" + "="*80)
    print("📊 ANÁLISE DE GAPS (lacunas)")
    print("="*80)
    
    gap_stats = analisar_gaps(resultados)
    
    print(f"\n🔢 Maior gap entre números consecutivos:")
    print(f"   Média: {gap_stats['maior_gap']['media']:.2f}")
    print(f"   Mínimo: {gap_stats['maior_gap']['min']}")
    print(f"   Máximo: {gap_stats['maior_gap']['max']}")
    
    print(f"\n📊 Distribuição do maior gap:")
    dist = gap_stats['maior_gap']['dist']
    for gap in sorted(dist.keys()):
        count = dist[gap]
        pct = count / total * 100
        if pct >= 1:
            bar = '█' * int(pct / 2)
            print(f"   Gap {gap}: {count:>5} ({pct:>5.1f}%) {bar}")
    
    # Filtros sugeridos
    print(f"\n🎯 Filtros de gap sugeridos:")
    for max_gap in [3, 4, 5, 6]:
        cobertura = sum(dist.get(i, 0) for i in range(1, max_gap + 1)) / total * 100
        print(f"   Máximo gap ≤ {max_gap}: {cobertura:.1f}% cobertura")
    
    # ========================================
    # CONCLUSÃO E FILTROS RECOMENDADOS
    # ========================================
    print("\n" + "="*80)
    print("📋 CONCLUSÃO: FILTROS REDUTORES RECOMENDADOS")
    print("="*80)
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  FILTRO                    │ COBERTURA │ REDUÇÃO │ RECOMENDAÇÃO             │
├─────────────────────────────────────────────────────────────────────────────┤""")
    
    # Calcular coberturas reais
    filtros = []
    
    # Consecutivos 2-5
    cob = sum(consec_stats.get(i, 0) for i in range(2, 6)) / total * 100
    filtros.append(('Consecutivos 2-5', cob, 100-cob))
    
    # Consecutivos 3-5
    cob = sum(consec_stats.get(i, 0) for i in range(3, 6)) / total * 100
    filtros.append(('Consecutivos 3-5', cob, 100-cob))
    
    # Máximo gap ≤ 4
    cob = sum(gap_stats['maior_gap']['dist'].get(i, 0) for i in range(1, 5)) / total * 100
    filtros.append(('Máximo gap ≤ 4', cob, 100-cob))
    
    # Máximo gap ≤ 5
    cob = sum(gap_stats['maior_gap']['dist'].get(i, 0) for i in range(1, 6)) / total * 100
    filtros.append(('Máximo gap ≤ 5', cob, 100-cob))
    
    # Grupos matemáticos
    for a in analises[:5]:  # Top 5 por delta
        nome = a['nome']
        tam = a['tamanho']
        # Estimar cobertura (baseado em média ± 1)
        min_ac = max(0, round(a['media'] - 1))
        max_ac = min(tam, round(a['media'] + 1))
        cob = sum(a['distribuicao'].get(i, 0) for i in range(min_ac, max_ac + 1)) / total * 100
        filtros.append((f'{nome} {min_ac}-{max_ac}', cob, 100-cob))
    
    for nome, cob, red in sorted(filtros, key=lambda x: x[1], reverse=True):
        if cob >= 80:
            rec = "✅ SEGURO"
        elif cob >= 60:
            rec = "⚠️ MODERADO"
        else:
            rec = "❌ ARRISCADO"
        print(f"│  {nome:<24} │ {cob:>7.1f}% │ {red:>6.1f}% │ {rec:<24} │")
    
    print("└─────────────────────────────────────────────────────────────────────────────┘")
    
    # ========================================
    # ÚLTIMO CONCURSO
    # ========================================
    print("\n" + "="*80)
    print(f"📊 ÚLTIMO CONCURSO: {resultados[-1]['concurso']}")
    print("="*80)
    
    ultimo = resultados[-1]['numeros']
    print(f"Números: {ultimo}")
    print(f"Pares consecutivos: {calcular_consecutivos(ultimo)}")
    print(f"Sequências 3+: {calcular_sequencias(ultimo)}")
    print(f"Maior gap: {calcular_maior_gap(ultimo)}")
    
    print("\nAcertos por grupo:")
    for nome, numeros in list(GRUPOS.items())[:8]:
        acertos = len(numeros & set(ultimo))
        esperado = len(numeros) * 0.6
        print(f"  {nome}: {acertos} (esperado: {esperado:.1f})")

if __name__ == "__main__":
    main()
