#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 GERADOR COMPLETO - COMBINAÇÕES LOTOFÁCIL COM TODAS AS ESTATÍSTICAS
====================================================================
Gera tabela completa com TODOS os campos calculados:
- Números básicos (N1-N20)
- Estatísticas matemáticas (pares, ímpares, primos, etc.)
- Sequências especiais (Fibonacci, consecutivos, etc.)
- Distribuições (colunas, linhas, quadrantes)
- Campos de comparação (repetidos, mesma posição)
"""

import sys
import os
from itertools import combinations
import time
from datetime import datetime
import csv
import math

print("🚀 GERADOR COMPLETO - COMBINAÇÕES LOTOFÁCIL 20 NÚMEROS")
print("="*65)

# Definições matemáticas
def eh_primo(n):
    """Verifica se um número é primo"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def fibonacci_ate_25():
    """Gera sequência de Fibonacci até 25"""
    fib = [1, 1]
    while fib[-1] < 25:
        fib.append(fib[-1] + fib[-2])
    return [f for f in fib if f <= 25]

def obter_linha_numero(num):
    """Retorna a linha do número no cartão da Lotofácil"""
    return ((num - 1) // 5) + 1

def obter_coluna_numero(num):
    """Retorna a coluna do número no cartão da Lotofácil"""
    return ((num - 1) % 5) + 1

def calcular_estatisticas_completas(numeros):
    """
    Calcula todas as estatísticas de uma combinação
    """
    # Definições
    primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    fibonacci = fibonacci_ate_25()
    
    stats = {}
    
    # === ESTATÍSTICAS BÁSICAS ===
    stats['QtdePares'] = sum(1 for n in numeros if n % 2 == 0)
    stats['QtdeImpares'] = sum(1 for n in numeros if n % 2 == 1)
    stats['QtdePrimos'] = sum(1 for n in numeros if eh_primo(n))
    
    # === SEQUÊNCIAS ===
    # Fibonacci
    stats['QtdeFibonacci'] = sum(1 for n in numeros if n in fibonacci)
    
    # Consecutivos
    consecutivos = 0
    for i in range(len(numeros) - 1):
        if numeros[i + 1] == numeros[i] + 1:
            consecutivos += 1
    stats['QtdeConsecutivos'] = consecutivos
    
    # === DISTRIBUIÇÃO POR DEZENAS ===
    stats['QtdeDezena1'] = sum(1 for n in numeros if 1 <= n <= 5)   # 01-05
    stats['QtdeDezena2'] = sum(1 for n in numeros if 6 <= n <= 10)  # 06-10
    stats['QtdeDezena3'] = sum(1 for n in numeros if 11 <= n <= 15) # 11-15
    stats['QtdeDezena4'] = sum(1 for n in numeros if 16 <= n <= 20) # 16-20
    stats['QtdeDezena5'] = sum(1 for n in numeros if 21 <= n <= 25) # 21-25
    
    # === DISTRIBUIÇÃO POR LINHAS (Cartão 5x5) ===
    linhas = [obter_linha_numero(n) for n in numeros]
    stats['QtdeLinha1'] = linhas.count(1)  # Números 1-5
    stats['QtdeLinha2'] = linhas.count(2)  # Números 6-10
    stats['QtdeLinha3'] = linhas.count(3)  # Números 11-15
    stats['QtdeLinha4'] = linhas.count(4)  # Números 16-20
    stats['QtdeLinha5'] = linhas.count(5)  # Números 21-25
    
    # === DISTRIBUIÇÃO POR COLUNAS ===
    colunas = [obter_coluna_numero(n) for n in numeros]
    stats['QtdeColuna1'] = colunas.count(1)  # Números 1,6,11,16,21
    stats['QtdeColuna2'] = colunas.count(2)  # Números 2,7,12,17,22
    stats['QtdeColuna3'] = colunas.count(3)  # Números 3,8,13,18,23
    stats['QtdeColuna4'] = colunas.count(4)  # Números 4,9,14,19,24
    stats['QtdeColuna5'] = colunas.count(5)  # Números 5,10,15,20,25
    
    # === DISTRIBUIÇÃO POR QUADRANTES ===
    # Q1: 1-3, 6-8, 11-13 (canto superior esquerdo)
    q1 = [1,2,3,6,7,8,11,12,13]
    # Q2: 4-5, 9-10, 14-15 (canto superior direito)  
    q2 = [4,5,9,10,14,15]
    # Q3: 16-18, 21-23 (canto inferior esquerdo)
    q3 = [16,17,18,21,22,23]
    # Q4: 19-20, 24-25 (canto inferior direito)
    q4 = [19,20,24,25]
    
    stats['QtdeQuadrante1'] = sum(1 for n in numeros if n in q1)
    stats['QtdeQuadrante2'] = sum(1 for n in numeros if n in q2)
    stats['QtdeQuadrante3'] = sum(1 for n in numeros if n in q3)
    stats['QtdeQuadrante4'] = sum(1 for n in numeros if n in q4)
    
    # === ESTATÍSTICAS NUMÉRICAS ===
    stats['SomaTotal'] = sum(numeros)
    stats['MediaAritmetica'] = round(sum(numeros) / len(numeros), 2)
    
    # Maior e menor gap
    gaps = [numeros[i+1] - numeros[i] for i in range(len(numeros)-1)]
    stats['MaiorGap'] = max(gaps) if gaps else 0
    stats['MenorGap'] = min(gaps) if gaps else 0
    
    # === PADRÕES ESPECIAIS ===
    # Números terminados em...
    stats['QtdeTerminadosEm0'] = sum(1 for n in numeros if n % 10 == 0)
    stats['QtdeTerminadosEm1'] = sum(1 for n in numeros if n % 10 == 1)
    stats['QtdeTerminadosEm2'] = sum(1 for n in numeros if n % 10 == 2)
    stats['QtdeTerminadosEm3'] = sum(1 for n in numeros if n % 10 == 3)
    stats['QtdeTerminadosEm4'] = sum(1 for n in numeros if n % 10 == 4)
    stats['QtdeTerminadosEm5'] = sum(1 for n in numeros if n % 10 == 5)
    stats['QtdeTerminadosEm6'] = sum(1 for n in numeros if n % 10 == 6)
    stats['QtdeTerminadosEm7'] = sum(1 for n in numeros if n % 10 == 7)
    stats['QtdeTerminadosEm8'] = sum(1 for n in numeros if n % 10 == 8)
    stats['QtdeTerminadosEm9'] = sum(1 for n in numeros if n % 10 == 9)
    
    # === CAMPOS PARA COMPARAÇÃO (preenchidos depois) ===
    stats['QtdeRepetidos'] = None
    stats['RepetidosMesmaPosicao'] = None
    
    return stats

def gerar_combinacoes_completas():
    """
    Gera todas as combinações com estatísticas completas
    """
    print("🔢 GERANDO COMBINAÇÕES COMPLETAS COM TODAS AS ESTATÍSTICAS...")
    
    numeros_lotofacil = list(range(1, 26))
    total_combinacoes = math.comb(25, 20)
    
    print(f"📊 Total de combinações: {total_combinacoes:,}")
    print("⏳ Calculando estatísticas completas... (pode demorar)")
    
    combinacoes = []
    contador = 0
    inicio = time.time()
    
    for combo in combinations(numeros_lotofacil, 20):
        contador += 1
        
        if contador % 2500 == 0:
            tempo_decorrido = time.time() - inicio
            percentual = (contador / total_combinacoes) * 100
            print(f"   📈 Progresso: {contador:,}/{total_combinacoes:,} ({percentual:.1f}%) - "
                  f"{tempo_decorrido:.1f}s")
        
        # Calcular todas as estatísticas
        stats = calcular_estatisticas_completas(list(combo))
        
        # Criar registro completo
        registro = {
            'ID': contador,
            # Números
            'N1': combo[0], 'N2': combo[1], 'N3': combo[2], 'N4': combo[3], 'N5': combo[4],
            'N6': combo[5], 'N7': combo[6], 'N8': combo[7], 'N9': combo[8], 'N10': combo[9],
            'N11': combo[10], 'N12': combo[11], 'N13': combo[12], 'N14': combo[13], 'N15': combo[14],
            'N16': combo[15], 'N17': combo[16], 'N18': combo[17], 'N19': combo[18], 'N20': combo[19],
        }
        
        # Adicionar todas as estatísticas
        registro.update(stats)
        
        # Metadata
        registro.update({
            'DataGeracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Processado': False
        })
        
        combinacoes.append(registro)
    
    tempo_total = time.time() - inicio
    print(f"✅ Geração concluída! {len(combinacoes):,} combinações em {tempo_total:.1f} segundos")
    
    return combinacoes

def salvar_csv_completo(combinacoes):
    """
    Salva CSV com todas as colunas e estatísticas
    """
    print("💾 SALVANDO CSV COMPLETO COM TODAS AS ESTATÍSTICAS...")
    
    arquivo = "COMBINACOES_LOTOFACIL20_COMPLETO.csv"
    
    if combinacoes:
        cabecalhos = list(combinacoes[0].keys())
        
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=cabecalhos)
            writer.writeheader()
            writer.writerows(combinacoes)
    
    print(f"✅ Arquivo salvo: {arquivo}")
    print(f"📊 Total de linhas: {len(combinacoes):,}")
    print(f"📋 Total de colunas: {len(cabecalhos)}")
    
    # Mostrar algumas estatísticas
    print("\n📈 ESTATÍSTICAS DO ARQUIVO:")
    print(f"   • Números: N1-N20 (20 colunas)")
    print(f"   • Pares/Ímpares: QtdePares, QtdeImpares") 
    print(f"   • Primos/Fibonacci: QtdePrimos, QtdeFibonacci")
    print(f"   • Dezenas: QtdeDezena1-5 (5 colunas)")
    print(f"   • Linhas: QtdeLinha1-5 (5 colunas)")
    print(f"   • Colunas: QtdeColuna1-5 (5 colunas)")
    print(f"   • Quadrantes: QtdeQuadrante1-4 (4 colunas)")
    print(f"   • Terminações: QtdeTerminadosEm0-9 (10 colunas)")
    print(f"   • Outras: Soma, Média, Gaps, etc.")
    
    return arquivo

def main():
    """
    Função principal
    """
    print("📅 Data/Hora:", datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print()
    
    print("🎯 OBJETIVO: Gerar 53.130 combinações com TODAS as estatísticas")
    print("📊 Incluindo: pares, ímpares, primos, Fibonacci, dezenas, linhas, colunas, etc.")
    print()
    
    print("▶️ Iniciando geração completa...")
    
    # Gerar combinações completas
    inicio_total = time.time()
    combinacoes = gerar_combinacoes_completas()
    
    # Salvar arquivo completo
    arquivo = salvar_csv_completo(combinacoes)
    
    tempo_total = time.time() - inicio_total
    print()
    print("="*65)
    print("🏆 GERAÇÃO COMPLETA FINALIZADA!")
    print("="*65)
    print(f"📊 Combinações geradas: {len(combinacoes):,}")
    print(f"⏱️ Tempo total: {tempo_total:.1f} segundos ({tempo_total/60:.1f} minutos)")
    print(f"📁 Arquivo: {arquivo}")
    print()
    print("✅ TODAS as estatísticas calculadas:")
    print("   • Básicas: pares, ímpares, primos, Fibonacci")
    print("   • Posicionais: dezenas, linhas, colunas, quadrantes")
    print("   • Padrões: consecutivos, gaps, terminações")
    print("   • Campos para comparação: QtdeRepetidos, RepetidosMesmaPosicao")
    print()
    print("🔄 PRÓXIMO PASSO: Calcular campos de comparação com último concurso")
    print("="*65)

if __name__ == "__main__":
    main()
