#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VALIDADOR DE PADRÕES MATEMÁTICOS
Testa se grupos especiais de números têm comportamento diferente do esperado

1. Números Primos: 2, 3, 5, 7, 11, 13, 17, 19, 23
2. Sequência Fibonacci: 1, 2, 3, 5, 8, 13, 21
3. Múltiplos de 3: 3, 6, 9, 12, 15, 18, 21, 24
4. Múltiplos de 5: 5, 10, 15, 20, 25
5. Números nas bordas: 1, 2, 24, 25
"""

import pyodbc
from collections import Counter, defaultdict
from datetime import datetime
import statistics

def conectar_banco():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def carregar_todos_resultados():
    """Carrega TODOS os resultados"""
    conn = conectar_banco()
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
            'numeros': set(row[1:16])
        })
    
    conn.close()
    return resultados

# Definir grupos matemáticos
GRUPOS = {
    'PRIMOS': {2, 3, 5, 7, 11, 13, 17, 19, 23},
    'FIBONACCI': {1, 2, 3, 5, 8, 13, 21},
    'MULT_3': {3, 6, 9, 12, 15, 18, 21, 24},
    'MULT_5': {5, 10, 15, 20, 25},
    'BORDAS': {1, 2, 24, 25},
    'CENTRO': {12, 13, 14},
    'BAIXOS': {1, 2, 3, 4, 5},
    'ALTOS': {21, 22, 23, 24, 25},
    'PARES': {2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24},
    'IMPARES': {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25},
}

def calcular_esperado(tamanho_grupo):
    """
    Calcula quantos números de um grupo deveriam sair em média
    
    Lotofácil: 15 números de 25
    Probabilidade de cada número = 15/25 = 60%
    Esperado = tamanho_grupo × 0.60
    """
    return tamanho_grupo * (15/25)

def analisar_grupo(resultados, nome_grupo, numeros_grupo):
    """Analisa a distribuição de acertos de um grupo em todos os concursos"""
    
    acertos_por_concurso = []
    
    for r in resultados:
        acertos = len(numeros_grupo & r['numeros'])
        acertos_por_concurso.append(acertos)
    
    # Estatísticas
    media = statistics.mean(acertos_por_concurso)
    desvio = statistics.stdev(acertos_por_concurso)
    minimo = min(acertos_por_concurso)
    maximo = max(acertos_por_concurso)
    esperado = calcular_esperado(len(numeros_grupo))
    
    # Distribuição
    distribuicao = Counter(acertos_por_concurso)
    
    return {
        'nome': nome_grupo,
        'numeros': sorted(numeros_grupo),
        'tamanho': len(numeros_grupo),
        'esperado': esperado,
        'media': media,
        'desvio': desvio,
        'minimo': minimo,
        'maximo': maximo,
        'distribuicao': distribuicao,
        'total_concursos': len(resultados),
        'delta': media - esperado,
        'delta_pct': (media / esperado - 1) * 100 if esperado > 0 else 0
    }

def calcular_faixas_cobertura(stats):
    """Calcula em quantos % dos concursos cada faixa de acertos ocorreu"""
    total = stats['total_concursos']
    dist = stats['distribuicao']
    
    faixas = {}
    for acertos, count in sorted(dist.items()):
        faixas[acertos] = {
            'count': count,
            'pct': count / total * 100
        }
    
    return faixas

def validar_filtro_exclusao(resultados, nome_grupo, numeros_grupo, min_acertos, max_acertos):
    """
    Valida se usar um filtro de min-max acertos em um grupo seria eficaz
    
    Retorna: % de concursos que passariam no filtro
    """
    passou = 0
    for r in resultados:
        acertos = len(numeros_grupo & r['numeros'])
        if min_acertos <= acertos <= max_acertos:
            passou += 1
    
    return passou / len(resultados) * 100

def main():
    print("\n" + "="*80)
    print("🔬 VALIDADOR DE PADRÕES MATEMÁTICOS")
    print("="*80)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("\nCarregando dados...")
    
    resultados = carregar_todos_resultados()
    print(f"✅ {len(resultados)} concursos carregados")
    
    # ========================================
    # ANÁLISE DE CADA GRUPO
    # ========================================
    print("\n" + "="*80)
    print("📊 ANÁLISE POR GRUPO MATEMÁTICO")
    print("="*80)
    
    resultados_analise = []
    
    for nome, numeros in GRUPOS.items():
        stats = analisar_grupo(resultados, nome, numeros)
        resultados_analise.append(stats)
    
    # Ordenar por delta (diferença vs esperado)
    resultados_analise.sort(key=lambda x: abs(x['delta']), reverse=True)
    
    print(f"\n{'Grupo':<12} {'Números':<35} {'Tam':<4} {'Esper.':<7} {'Média':<7} {'Δ':<8} {'Δ%':<8}")
    print("─"*90)
    
    for stats in resultados_analise:
        nums_str = str(stats['numeros'][:6]) + ('...' if len(stats['numeros']) > 6 else '')
        delta_str = f"{stats['delta']:+.2f}"
        delta_pct_str = f"{stats['delta_pct']:+.1f}%"
        
        # Indicador
        if stats['delta_pct'] > 3:
            ind = "⬆️"
        elif stats['delta_pct'] < -3:
            ind = "⬇️"
        else:
            ind = "➖"
        
        print(f"{stats['nome']:<12} {nums_str:<35} {stats['tamanho']:<4} {stats['esperado']:<7.2f} {stats['media']:<7.2f} {delta_str:<8} {delta_pct_str:<8} {ind}")
    
    # ========================================
    # ANÁLISE DETALHADA DOS 3 GRUPOS PEDIDOS
    # ========================================
    grupos_interesse = ['PRIMOS', 'FIBONACCI', 'MULT_3']
    
    for nome in grupos_interesse:
        numeros = GRUPOS[nome]
        stats = analisar_grupo(resultados, nome, numeros)
        
        print("\n" + "="*80)
        print(f"🔍 ANÁLISE DETALHADA: {nome}")
        print("="*80)
        print(f"\n📋 Números: {sorted(numeros)}")
        print(f"📊 Tamanho do grupo: {len(numeros)} números")
        print(f"📈 Esperado estatístico: {stats['esperado']:.2f} acertos por concurso")
        print(f"📊 Média real: {stats['media']:.2f} acertos por concurso")
        print(f"📊 Desvio padrão: {stats['desvio']:.2f}")
        print(f"📊 Mínimo: {stats['minimo']} | Máximo: {stats['maximo']}")
        
        delta = stats['delta']
        delta_pct = stats['delta_pct']
        
        if abs(delta_pct) > 5:
            print(f"\n⚠️ DIFERENÇA SIGNIFICATIVA: {delta:+.2f} ({delta_pct:+.1f}%)")
        else:
            print(f"\n✅ Diferença mínima: {delta:+.2f} ({delta_pct:+.1f}%)")
        
        # Distribuição de acertos
        print(f"\n📊 Distribuição de acertos:")
        faixas = calcular_faixas_cobertura(stats)
        
        for acertos in range(stats['minimo'], stats['maximo'] + 1):
            if acertos in faixas:
                f = faixas[acertos]
                bar = '█' * int(f['pct'] / 2)
                print(f"   {acertos} acertos: {f['count']:>5} ({f['pct']:>5.1f}%) {bar}")
        
        # Sugestões de filtro
        print(f"\n🎯 ANÁLISE DE FILTROS POTENCIAIS:")
        
        # Calcular faixas mais comuns (80% dos concursos)
        sorted_faixas = sorted(faixas.items(), key=lambda x: x[1]['pct'], reverse=True)
        
        # Encontrar faixa que cobre 80%
        acumulado = 0
        faixa_80 = []
        for acertos, dados in sorted_faixas:
            faixa_80.append(acertos)
            acumulado += dados['pct']
            if acumulado >= 80:
                break
        
        min_faixa = min(faixa_80)
        max_faixa = max(faixa_80)
        cobertura = validar_filtro_exclusao(resultados, nome, numeros, min_faixa, max_faixa)
        
        print(f"   Faixa que cobre ~80%: {min_faixa}-{max_faixa} acertos")
        print(f"   Cobertura real: {cobertura:.1f}% dos concursos")
        
        # Testar filtro mais restritivo
        if len(numeros) >= 5:
            # Testar com média ± 1
            filtro_min = max(0, round(stats['media'] - 1))
            filtro_max = round(stats['media'] + 1)
            cobertura_restrita = validar_filtro_exclusao(resultados, nome, numeros, filtro_min, filtro_max)
            print(f"   Filtro restrito ({filtro_min}-{filtro_max}): {cobertura_restrita:.1f}% dos concursos")
    
    # ========================================
    # CONCLUSÃO: USABILIDADE COMO FILTRO
    # ========================================
    print("\n" + "="*80)
    print("📋 CONCLUSÃO: USABILIDADE COMO FILTRO")
    print("="*80)
    
    print("""
┌─────────────┬─────────┬────────────┬────────────────────────────────────────┐
│   Grupo     │  Δ vs   │ Funciona?  │ Recomendação                           │
│             │ Esperado│            │                                        │
├─────────────┼─────────┼────────────┼────────────────────────────────────────┤""")
    
    for stats in resultados_analise:
        nome = stats['nome']
        delta = stats['delta_pct']
        
        # Determinar se é útil como filtro
        if abs(delta) > 5:
            funciona = "✅ SIM"
            if delta > 0:
                rec = f"Exigir ≥{round(stats['media'])} do grupo"
            else:
                rec = f"Limitar ≤{round(stats['media'])} do grupo"
        elif abs(delta) > 2:
            funciona = "⚠️ LEVE"
            rec = "Pode ajudar marginalmente"
        else:
            funciona = "❌ NÃO"
            rec = "Sem vantagem estatística"
        
        print(f"│ {nome:<11} │ {delta:>+5.1f}% │ {funciona:<10} │ {rec:<38} │")
    
    print("└─────────────┴─────────┴────────────┴────────────────────────────────────────┘")
    
    # ========================================
    # FILTROS COMBINADOS PROPOSTOS
    # ========================================
    print("\n" + "="*80)
    print("🎯 ANÁLISE: FILTROS COMBINADOS")
    print("="*80)
    
    # Testar combinações de filtros
    filtros_teste = [
        ('PRIMOS 4-7', 'PRIMOS', 4, 7),
        ('PRIMOS 5-6', 'PRIMOS', 5, 6),
        ('FIBONACCI 3-5', 'FIBONACCI', 3, 5),
        ('FIBONACCI 4-5', 'FIBONACCI', 4, 5),
        ('MULT_3 4-6', 'MULT_3', 4, 6),
        ('MULT_3 5-6', 'MULT_3', 5, 6),
    ]
    
    print(f"\n{'Filtro':<20} {'Cobertura':<12} {'Comentário'}")
    print("─"*60)
    
    for nome_filtro, grupo, min_ac, max_ac in filtros_teste:
        numeros = GRUPOS[grupo]
        cobertura = validar_filtro_exclusao(resultados, grupo, numeros, min_ac, max_ac)
        
        if cobertura >= 80:
            status = "✅ Seguro"
        elif cobertura >= 60:
            status = "⚠️ Moderado"
        else:
            status = "❌ Arriscado"
        
        print(f"{nome_filtro:<20} {cobertura:>6.1f}%      {status}")
    
    # ========================================
    # VERIFICAR ÚLTIMO CONCURSO
    # ========================================
    print("\n" + "="*80)
    print("📊 ÚLTIMO CONCURSO ANALISADO")
    print("="*80)
    
    ultimo = resultados[-1]
    print(f"\n🎯 Concurso: {ultimo['concurso']}")
    print(f"📋 Números: {sorted(ultimo['numeros'])}")
    
    for nome, numeros in [('PRIMOS', GRUPOS['PRIMOS']), 
                           ('FIBONACCI', GRUPOS['FIBONACCI']), 
                           ('MULT_3', GRUPOS['MULT_3'])]:
        acertos = len(numeros & ultimo['numeros'])
        esperado = calcular_esperado(len(numeros))
        quais = sorted(numeros & ultimo['numeros'])
        print(f"\n{nome}:")
        print(f"   Acertos: {acertos} (esperado: {esperado:.1f})")
        print(f"   Quais: {quais}")

if __name__ == "__main__":
    main()
