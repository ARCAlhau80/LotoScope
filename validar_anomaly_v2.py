#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VALIDADOR DE ANOMALY v2.0 (Consecutivas)
Testa as hipóteses:
1. Números com 8+ aparições consecutivas tendem a PARAR
2. Números com 4-5 ausências consecutivas tendem a RETORNAR

Este é o teste MAIS IMPORTANTE porque baseia nossos filtros do Pool 23
"""

import pyodbc
from collections import defaultdict
from datetime import datetime

def conectar_banco():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def carregar_todos_resultados():
    """Carrega TODOS os resultados ordenados do mais antigo ao mais recente"""
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

def calcular_consecutivas(resultados, idx, numero):
    """
    Calcula quantas vezes consecutivas um número apareceu/ausentou
    até o concurso idx (não incluindo idx)
    
    Retorna: (tipo, quantidade)
    - tipo: 'aparicao' ou 'ausencia'
    - quantidade: número de consecutivas
    """
    if idx == 0:
        return ('neutro', 0)
    
    # Verificar o concurso anterior
    ultimo_saiu = numero in resultados[idx-1]['numeros']
    
    count = 1
    for i in range(idx-2, -1, -1):
        saiu = numero in resultados[i]['numeros']
        if saiu == ultimo_saiu:
            count += 1
        else:
            break
    
    tipo = 'aparicao' if ultimo_saiu else 'ausencia'
    return (tipo, count)

def validar_hipotese_parar(resultados, min_consecutivas=8):
    """
    HIPÓTESE 1: Números com N+ aparições consecutivas tendem a PARAR
    
    Testa: Quando um número apareceu N vezes seguidas, qual a chance de NÃO sair no próximo?
    """
    casos = []
    
    # Para cada concurso (começando do 50 para ter histórico)
    for idx in range(50, len(resultados)):
        resultado_atual = resultados[idx]
        
        # Para cada número de 1 a 25
        for num in range(1, 26):
            tipo, qtd = calcular_consecutivas(resultados, idx, num)
            
            if tipo == 'aparicao' and qtd >= min_consecutivas:
                saiu_agora = num in resultado_atual['numeros']
                casos.append({
                    'concurso': resultado_atual['concurso'],
                    'numero': num,
                    'consecutivas': qtd,
                    'saiu': saiu_agora,
                    'parou': not saiu_agora  # Hipótese: deveria parar
                })
    
    return casos

def validar_hipotese_retornar(resultados, min_ausencias=4, max_ausencias=6):
    """
    HIPÓTESE 2: Números com N-M ausências consecutivas tendem a RETORNAR
    
    Testa: Quando um número esteve ausente N-M vezes seguidas, qual a chance de sair?
    """
    casos = []
    
    for idx in range(50, len(resultados)):
        resultado_atual = resultados[idx]
        
        for num in range(1, 26):
            tipo, qtd = calcular_consecutivas(resultados, idx, num)
            
            if tipo == 'ausencia' and min_ausencias <= qtd <= max_ausencias:
                saiu_agora = num in resultado_atual['numeros']
                casos.append({
                    'concurso': resultado_atual['concurso'],
                    'numero': num,
                    'consecutivas': qtd,
                    'saiu': saiu_agora,
                    'retornou': saiu_agora  # Hipótese: deveria retornar
                })
    
    return casos

def analisar_por_faixa(resultados):
    """Analisa probabilidade de sair/não sair por faixa de consecutivas"""
    
    # Estrutura: {consecutivas: {'saiu': N, 'nao_saiu': M}}
    stats_aparicao = defaultdict(lambda: {'saiu': 0, 'nao_saiu': 0})
    stats_ausencia = defaultdict(lambda: {'saiu': 0, 'nao_saiu': 0})
    
    for idx in range(50, len(resultados)):
        resultado_atual = resultados[idx]
        
        for num in range(1, 26):
            tipo, qtd = calcular_consecutivas(resultados, idx, num)
            saiu = num in resultado_atual['numeros']
            
            if tipo == 'aparicao':
                if saiu:
                    stats_aparicao[qtd]['saiu'] += 1
                else:
                    stats_aparicao[qtd]['nao_saiu'] += 1
            elif tipo == 'ausencia':
                if saiu:
                    stats_ausencia[qtd]['saiu'] += 1
                else:
                    stats_ausencia[qtd]['nao_saiu'] += 1
    
    return stats_aparicao, stats_ausencia

def main():
    print("\n" + "="*70)
    print("🔬 VALIDADOR ANOMALY v2.0 - CONSECUTIVAS")
    print("="*70)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("\nCarregando dados...")
    
    resultados = carregar_todos_resultados()
    print(f"✅ {len(resultados)} concursos carregados")
    
    # ========================================
    # ANÁLISE POR FAIXA DE CONSECUTIVAS
    # ========================================
    print("\n" + "="*70)
    print("📊 ANÁLISE POR FAIXA DE CONSECUTIVAS")
    print("="*70)
    
    stats_apar, stats_ausen = analisar_por_faixa(resultados)
    
    PROB_BASE = 60.0  # Probabilidade base: 15/25 = 60%
    
    print("\n📈 APARIÇÕES CONSECUTIVAS (número veio saindo...)")
    print("─"*70)
    print(f"{'Consec.':<10} {'Casos':<10} {'Saiu':<10} {'Parou':<10} {'Taxa Sair':<12} {'Δ vs 60%':<12}")
    print("─"*70)
    
    for consec in sorted(stats_apar.keys()):
        if consec >= 1:
            dados = stats_apar[consec]
            total = dados['saiu'] + dados['nao_saiu']
            if total >= 10:  # Mínimo de casos para relevância
                taxa_sair = dados['saiu'] / total * 100
                delta = taxa_sair - PROB_BASE
                
                # Indicador
                if delta > 5:
                    ind = "⬆️ SOBE"
                elif delta < -5:
                    ind = "⬇️ PARA"
                else:
                    ind = "➖"
                
                print(f"{consec:<10} {total:<10} {dados['saiu']:<10} {dados['nao_saiu']:<10} {taxa_sair:<11.1f}% {delta:+.1f}% {ind}")
    
    print("\n📉 AUSÊNCIAS CONSECUTIVAS (número estava sumido...)")
    print("─"*70)
    print(f"{'Consec.':<10} {'Casos':<10} {'Saiu':<10} {'Ficou':<10} {'Taxa Sair':<12} {'Δ vs 60%':<12}")
    print("─"*70)
    
    for consec in sorted(stats_ausen.keys()):
        if consec >= 1:
            dados = stats_ausen[consec]
            total = dados['saiu'] + dados['nao_saiu']
            if total >= 10:
                taxa_sair = dados['saiu'] / total * 100
                delta = taxa_sair - PROB_BASE
                
                if delta > 5:
                    ind = "⬆️ VOLTA"
                elif delta < -5:
                    ind = "⬇️ FICA FORA"
                else:
                    ind = "➖"
                
                print(f"{consec:<10} {total:<10} {dados['saiu']:<10} {dados['nao_saiu']:<10} {taxa_sair:<11.1f}% {delta:+.1f}% {ind}")
    
    # ========================================
    # TESTE HIPÓTESE 1: 8+ CONSECUTIVAS PARAM
    # ========================================
    print("\n" + "="*70)
    print("🧪 TESTE HIPÓTESE 1: Números com 8+ aparições consecutivas PARAM?")
    print("="*70)
    
    for threshold in [6, 7, 8, 9, 10]:
        casos = validar_hipotese_parar(resultados, min_consecutivas=threshold)
        if casos:
            parou = sum(1 for c in casos if c['parou'])
            total = len(casos)
            taxa_parou = parou / total * 100
            taxa_esperada = 40.0  # 100% - 60%
            delta = taxa_parou - taxa_esperada
            
            if delta > 5:
                status = "✅ CONFIRMA"
            elif delta < -5:
                status = "❌ REFUTA"
            else:
                status = "➖ INCONCL."
            
            print(f"\n{threshold}+ consecutivas:")
            print(f"   Casos: {total}")
            print(f"   Pararam: {parou} ({taxa_parou:.1f}%)")
            print(f"   Esperado aleatório: {taxa_esperada:.1f}%")
            print(f"   Diferença: {delta:+.1f}%")
            print(f"   Status: {status}")
    
    # ========================================
    # TESTE HIPÓTESE 2: 4-5 AUSÊNCIAS RETORNAM
    # ========================================
    print("\n" + "="*70)
    print("🧪 TESTE HIPÓTESE 2: Números com 4-6 ausências consecutivas RETORNAM?")
    print("="*70)
    
    for faixa in [(3, 4), (4, 5), (5, 6), (6, 7), (4, 6)]:
        casos = validar_hipotese_retornar(resultados, min_ausencias=faixa[0], max_ausencias=faixa[1])
        if casos:
            retornou = sum(1 for c in casos if c['retornou'])
            total = len(casos)
            taxa_retorno = retornou / total * 100
            taxa_esperada = 60.0
            delta = taxa_retorno - taxa_esperada
            
            if delta > 5:
                status = "✅ CONFIRMA"
            elif delta < -5:
                status = "❌ REFUTA"
            else:
                status = "➖ INCONCL."
            
            print(f"\n{faixa[0]}-{faixa[1]} ausências consecutivas:")
            print(f"   Casos: {total}")
            print(f"   Retornaram: {retornou} ({taxa_retorno:.1f}%)")
            print(f"   Esperado aleatório: {taxa_esperada:.1f}%")
            print(f"   Diferença: {delta:+.1f}%")
            print(f"   Status: {status}")
    
    # ========================================
    # CONCLUSÃO
    # ========================================
    print("\n" + "="*70)
    print("📋 CONCLUSÃO FINAL")
    print("="*70)
    
    # Calcular métricas finais
    casos_8plus = validar_hipotese_parar(resultados, 8)
    casos_4_5 = validar_hipotese_retornar(resultados, 4, 5)
    
    if casos_8plus:
        taxa_parou_8 = sum(1 for c in casos_8plus if c['parou']) / len(casos_8plus) * 100
    else:
        taxa_parou_8 = 0
        
    if casos_4_5:
        taxa_retorno_4_5 = sum(1 for c in casos_4_5 if c['retornou']) / len(casos_4_5) * 100
    else:
        taxa_retorno_4_5 = 0
    
    print(f"""
┌─────────────────────────────────────────────────────────────────┐
│  HIPÓTESE                           │ RESULTADO │ VEREDITO     │
├─────────────────────────────────────┼───────────┼──────────────┤
│  8+ aparições → PARA                │ {taxa_parou_8:>6.1f}%  │ {'✅ FUNCIONA' if taxa_parou_8 > 45 else '❌ NÃO FUNCIONA' if taxa_parou_8 < 35 else '➖ INCONCL.':^12} │
│  4-5 ausências → RETORNA            │ {taxa_retorno_4_5:>6.1f}%  │ {'✅ FUNCIONA' if taxa_retorno_4_5 > 65 else '❌ NÃO FUNCIONA' if taxa_retorno_4_5 < 55 else '➖ INCONCL.':^12} │
├─────────────────────────────────────┴───────────┴──────────────┤
│  Esperado aleatório: PARAR = 40%, RETORNAR = 60%               │
└────────────────────────────────────────────────────────────────┘
""")
    
    # Recomendação
    delta_parar = taxa_parou_8 - 40
    delta_retornar = taxa_retorno_4_5 - 60
    
    if delta_parar > 5 or delta_retornar > 5:
        print("🎯 RECOMENDAÇÃO: Há indícios de que Anomaly v2.0 tem valor!")
        if delta_parar > 5:
            print(f"   → Evitar números com 8+ aparições consecutivas (+{delta_parar:.1f}% chance de parar)")
        if delta_retornar > 5:
            print(f"   → Incluir números com 4-5 ausências consecutivas (+{delta_retornar:.1f}% chance de retornar)")
    elif delta_parar < -5 and delta_retornar < -5:
        print("❌ RECOMENDAÇÃO: Anomaly v2.0 NÃO tem poder preditivo")
        print("   A loteria é verdadeiramente aleatória neste aspecto")
    else:
        print("⚠️ RECOMENDAÇÃO: Resultados inconclusivos")
        print("   Os dados não mostram padrão claro o suficiente")

if __name__ == "__main__":
    main()
