#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEMONSTRAÇÃO: Probabilidade de cada número na Lotofácil

Prova que TODOS os 25 números têm EXATAMENTE 60% de chance de sair,
independente de qualquer "ordem de escolha"
"""

import pyodbc
from collections import Counter
from math import comb

def conectar_banco():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def carregar_resultados():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT ORDER BY Concurso
    """)
    resultados = []
    for row in cursor.fetchall():
        resultados.append(set(row[1:16]))
    conn.close()
    return resultados

def main():
    print("\n" + "="*70)
    print("🎲 DEMONSTRAÇÃO: PROBABILIDADE DE CADA NÚMERO")
    print("="*70)
    
    # ========================================
    # PARTE 1: PROVA MATEMÁTICA TEÓRICA
    # ========================================
    print("\n" + "─"*70)
    print("📐 PARTE 1: PROVA MATEMÁTICA")
    print("─"*70)
    
    # Total de combinações possíveis: C(25,15)
    total_combinacoes = comb(25, 15)
    print(f"\n📊 Total de combinações possíveis C(25,15) = {total_combinacoes:,}")
    
    # Combinações que CONTÉM o número 1 (ou qualquer número específico)
    # Se o número 1 está na combinação, restam 14 posições para 24 números
    # C(24,14)
    combinacoes_com_1 = comb(24, 14)
    print(f"📊 Combinações que contém o número 1: C(24,14) = {combinacoes_com_1:,}")
    
    # Probabilidade teórica
    prob_teorica = combinacoes_com_1 / total_combinacoes
    print(f"\n🎯 Probabilidade teórica = {combinacoes_com_1:,} / {total_combinacoes:,}")
    print(f"🎯 Probabilidade teórica = {prob_teorica:.10f}")
    print(f"🎯 Probabilidade teórica = {prob_teorica * 100:.2f}%")
    print(f"🎯 Que é EXATAMENTE = 15/25 = 0.60 = 60%")
    
    # Provar que é o mesmo para QUALQUER número
    print(f"\n✅ PROVA: Isso vale para QUALQUER número de 1 a 25!")
    print(f"   Por simetria combinatória, todos os números são equivalentes")
    
    # ========================================
    # PARTE 2: VERIFICAÇÃO EMPÍRICA
    # ========================================
    print("\n" + "─"*70)
    print("📊 PARTE 2: VERIFICAÇÃO EMPÍRICA (dados reais)")
    print("─"*70)
    
    resultados = carregar_resultados()
    total_concursos = len(resultados)
    print(f"\n📊 Analisando {total_concursos} concursos reais...")
    
    # Contar frequência de cada número
    frequencia = Counter()
    for resultado in resultados:
        frequencia.update(resultado)
    
    # Calcular taxa de aparição
    print(f"\n{'Número':<8} {'Aparições':<12} {'Taxa Real':<12} {'Esperado':<12} {'Diferença':<12}")
    print("─"*60)
    
    esperado = 60.0
    desvios = []
    
    for num in range(1, 26):
        aparicoes = frequencia[num]
        taxa = aparicoes / total_concursos * 100
        diff = taxa - esperado
        desvios.append(abs(diff))
        
        # Indicador
        if abs(diff) < 1:
            ind = "✅"
        elif abs(diff) < 2:
            ind = "⚠️"
        else:
            ind = "❌"
        
        print(f"{num:<8} {aparicoes:<12} {taxa:<11.2f}% {esperado:<11.2f}% {diff:+.2f}%       {ind}")
    
    print("─"*60)
    
    # Estatísticas
    media_desvio = sum(desvios) / len(desvios)
    max_desvio = max(desvios)
    min_desvio = min(desvios)
    
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"   Desvio médio da média: {media_desvio:.3f}%")
    print(f"   Maior desvio: {max_desvio:.3f}%")
    print(f"   Menor desvio: {min_desvio:.3f}%")
    
    # ========================================
    # PARTE 3: DESMENTINDO A "ORDEM DE ESCOLHA"
    # ========================================
    print("\n" + "─"*70)
    print("🎯 PARTE 3: A ORDEM NÃO IMPORTA!")
    print("─"*70)
    
    print("""
    ❌ PENSAMENTO ERRADO:
    "Se eu escolho 1 primeiro, ele tem 1/25 de chance..."
    "Se eu escolho 3 segundo, ele tem 2/24 de chance..."
    
    ✅ REALIDADE:
    Você NÃO está "escolhendo" nada. Você está APOSTANDO.
    
    A ordem em que você PENSA nos números não afeta a probabilidade!
    
    O sorteio acontece INDEPENDENTEMENTE da sua aposta.
    Cada número tem 60% de chance de estar no resultado.
    """)
    
    # ========================================
    # PARTE 4: SIMULAÇÃO DA "LÓGICA ERRADA"
    # ========================================
    print("\n" + "─"*70)
    print("🧪 PARTE 4: TESTANDO A LÓGICA ERRADA")
    print("─"*70)
    
    print("""
    Se a sua lógica estivesse correta, números "baixos" (1, 2, 3...)
    deveriam sair MAIS que números "altos" (23, 24, 25).
    
    Vamos testar:
    """)
    
    # Comparar primeiros vs últimos
    baixos = {1, 2, 3, 4, 5}
    altos = {21, 22, 23, 24, 25}
    
    freq_baixos = sum(frequencia[n] for n in baixos)
    freq_altos = sum(frequencia[n] for n in altos)
    
    media_baixos = freq_baixos / 5 / total_concursos * 100
    media_altos = freq_altos / 5 / total_concursos * 100
    
    print(f"   Taxa média números BAIXOS (1-5):  {media_baixos:.2f}%")
    print(f"   Taxa média números ALTOS (21-25): {media_altos:.2f}%")
    print(f"   Diferença: {media_baixos - media_altos:+.2f}%")
    
    if abs(media_baixos - media_altos) < 1:
        print(f"\n   ✅ CONCLUSÃO: NÃO HÁ DIFERENÇA SIGNIFICATIVA!")
        print(f"   A 'ordem de escolha' é irrelevante.")
    
    # ========================================
    # PARTE 5: A FALÁCIA "OU SAI OU NÃO SAI = 50%"
    # ========================================
    print("\n" + "─"*70)
    print("⚠️ PARTE 5: A FALÁCIA DO 50/50")
    print("─"*70)
    
    print("""
    FALÁCIA: "Ou o número sai ou não sai, então é 50%"
    
    Isso é como dizer:
    - "Ou ganho na Mega-Sena ou não ganho, então é 50%"
    - "Ou chove amanhã ou não chove, então é 50%"
    
    ❌ ERRADO: Dois resultados possíveis ≠ probabilidades iguais!
    
    ✅ CORRETO:
    - Lotofácil sorteia 15 de 25 números
    - P(número X sair) = 15/25 = 60%
    - P(número X NÃO sair) = 10/25 = 40%
    
    São 60/40, NÃO 50/50!
    """)
    
    # Verificar empiricamente
    saiu = sum(frequencia.values())  # Total de aparições
    nao_saiu = total_concursos * 25 - saiu  # Total de "não aparições"
    
    # Cada concurso tem 15 números que saíram e 10 que não saíram
    taxa_saiu = saiu / (total_concursos * 25) * 100
    taxa_nao_saiu = nao_saiu / (total_concursos * 25) * 100
    
    print(f"   📊 Verificação empírica ({total_concursos} concursos):")
    print(f"   Taxa de 'saiu': {taxa_saiu:.2f}%")
    print(f"   Taxa de 'não saiu': {taxa_nao_saiu:.2f}%")
    print(f"\n   ✅ Confirmado: É 60/40, não 50/50!")
    
    # ========================================
    # CONCLUSÃO FINAL
    # ========================================
    print("\n" + "="*70)
    print("📋 CONCLUSÃO FINAL")
    print("="*70)
    
    print("""
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  1. TODOS os 25 números têm EXATAMENTE 60% de chance de sair      │
│                                                                    │
│  2. A ordem em que você PENSA ou ESCOLHE não importa              │
│                                                                    │
│  3. "Ou sai ou não sai" NÃO é 50/50 - é 60/40!                    │
│                                                                    │
│  4. O sorteio é COMPLETAMENTE ALEATÓRIO e INDEPENDENTE            │
│     da sua aposta                                                  │
│                                                                    │
│  5. A única forma de aumentar chances é:                           │
│     - Jogar MAIS combinações (caro)                                │
│     - Eliminar combinações ESTATISTICAMENTE IMPROVÁVEIS            │
│       (soma, par/ímpar) - mas isso NÃO muda a probabilidade        │
│       individual de cada número                                    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
    """)

if __name__ == "__main__":
    main()
