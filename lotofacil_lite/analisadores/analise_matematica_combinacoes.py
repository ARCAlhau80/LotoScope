#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧮 ANÁLISE MATEMÁTICA: COMBINAÇÕES DE 20 NÚMEROS
===============================================

PERGUNTA: Como é possível gerar 1 milhão de combinações de 20 números
se existem apenas C(25,20) = 53.130 combinações únicas possíveis?

INVESTIGAÇÃO MATEMÁTICA COMPLETA

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

import math
from itertools import combinations

def calcular_combinacoes_teoricas():
    """
    Calcula o número teórico de combinações C(25,20)
    """
    print("🧮 CÁLCULO MATEMÁTICO TEÓRICO")
    print("=" * 50)
    
    # Cálculo C(25,20) = 25! / (20! * 5!)
    c_25_20 = math.comb(25, 20)
    
    print(f"📊 C(25,20) = 25! / (20! × 5!)")
    print(f"📊 C(25,20) = {c_25_20:,} combinações únicas possíveis")
    print()
    
    # Também é igual a C(25,5) pois C(n,k) = C(n,n-k)
    c_25_5 = math.comb(25, 5)
    print(f"💡 Verificação: C(25,20) = C(25,5) = {c_25_5:,}")
    print(f"✅ Confirmado: {c_25_20 == c_25_5}")
    print()
    
    return c_25_20

def investigar_arquivo_1milhao():
    """
    Investiga como um arquivo pode ter mais combinações que o matematicamente possível
    """
    print("🔍 INVESTIGAÇÃO: ARQUIVO COM 1 MILHÃO DE COMBINAÇÕES")
    print("=" * 60)
    
    combinacoes_teoricas = 53130
    print(f"📊 Máximo teórico: {combinacoes_teoricas:,} combinações únicas")
    print(f"❓ Arquivo alegado: ~1.000.000 combinações")
    print(f"⚠️ Diferença: {1000000 - combinacoes_teoricas:,} combinações a mais!")
    print()
    
    print("🔍 POSSÍVEIS EXPLICAÇÕES:")
    print("=" * 30)
    
    print("1️⃣ DUPLICATAS MASSIVAS:")
    print("   • Arquivo contém ~18x duplicatas de cada combinação única")
    print("   • 53.130 × 18.8 ≈ 1.000.000")
    print("   • Sistema gerou a mesma combinação múltiplas vezes")
    print()
    
    print("2️⃣ DIFERENTES QUANTIDADES DE NÚMEROS:")
    print("   • Mistura de combinações de 15, 16, 17, 18, 19, 20 números")
    print("   • Não são apenas combinações de 20 números")
    print("   • Total seria soma de diferentes C(25,k)")
    print()
    
    print("3️⃣ FORMATO DIFERENTE:")
    print("   • Não são combinações de 20 para escolher 20")
    print("   • Podem ser sequências, permutações ou outro formato")
    print("   • Arquivo pode conter dados adicionais")
    print()
    
    print("4️⃣ ERRO DE CONTAGEM:")
    print("   • Arquivo pode ter menos combinações do que aparenta")
    print("   • Linhas vazias, cabeçalhos contados incorretamente")
    print("   • Necessário análise linha por linha")

def verificar_arquivo_real():
    """
    Verifica o arquivo real para entender a discrepância
    """
    print("🔍 VERIFICAÇÃO DO ARQUIVO REAL")
    print("=" * 40)
    
    # Primeiro, vamos procurar arquivos com "1 milhão" de combinações
    import os
    import glob
    
    # Procurar arquivos na pasta
    pasta = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite"
    
    print(f"📁 Procurando arquivos em: {pasta}")
    print()
    
    # Arquivos de combinações
    arquivos_encontrados = []
    
    for arquivo in glob.glob(os.path.join(pasta, "*.txt")):
        nome_arquivo = os.path.basename(arquivo)
        tamanho = os.path.getsize(arquivo)
        tamanho_mb = tamanho / (1024 * 1024)
        
        if "combinac" in nome_arquivo.lower() and tamanho_mb > 50:  # Arquivos grandes
            arquivos_encontrados.append((nome_arquivo, tamanho, tamanho_mb))
    
    if arquivos_encontrados:
        print("📋 ARQUIVOS GRANDES ENCONTRADOS:")
        for nome, tamanho, tamanho_mb in sorted(arquivos_encontrados, key=lambda x: x[1], reverse=True):
            print(f"   📄 {nome}")
            print(f"      💾 {tamanho:,} bytes ({tamanho_mb:.1f} MB)")
            
            # Estimar número de linhas baseado no tamanho
            # Assumindo ~80 caracteres por linha média
            linhas_estimadas = tamanho // 80
            print(f"      📊 ~{linhas_estimadas:,} linhas estimadas")
            print()
    else:
        print("❌ Nenhum arquivo grande encontrado")
    
    return arquivos_encontrados

def analisar_primeiro_arquivo_grande():
    """
    Analisa o primeiro arquivo grande encontrado
    """
    print("🔬 ANÁLISE DETALHADA DO PRIMEIRO ARQUIVO")
    print("=" * 50)
    
    # Verificar arquivos grandes
    arquivos = verificar_arquivo_real()
    
    if not arquivos:
        print("❌ Nenhum arquivo para analisar")
        return
    
    # Pegar o maior arquivo
    arquivo_maior = max(arquivos, key=lambda x: x[1])
    nome_arquivo = arquivo_maior[0]
    caminho_completo = os.path.join(r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite", nome_arquivo)
    
    print(f"📄 Analisando: {nome_arquivo}")
    print()
    
    try:
        combinacoes_unicas = set()
        total_linhas = 0
        linhas_validas = 0
        diferentes_tamanhos = {}
        
        print("🔄 Processando arquivo...")
        
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            for linha_num, linha in enumerate(f, 1):
                total_linhas += 1
                linha = linha.strip()
                
                if not linha or not any(c.isdigit() for c in linha):
                    continue
                
                try:
                    # Extrair números
                    if ':' in linha:
                        numeros_str = linha.split(':')[1].strip()
                    else:
                        numeros_str = linha
                    
                    if ',' in numeros_str:
                        numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                        
                        if len(numeros) >= 15 and all(1 <= n <= 25 for n in numeros):
                            linhas_validas += 1
                            
                            # Contar diferentes tamanhos
                            tamanho = len(numeros)
                            diferentes_tamanhos[tamanho] = diferentes_tamanhos.get(tamanho, 0) + 1
                            
                            # Adicionar às combinações únicas
                            combinacao_tuple = tuple(sorted(numeros))
                            combinacoes_unicas.add(combinacao_tuple)
                
                except:
                    continue
                
                # Parar após 100k linhas para análise rápida
                if total_linhas >= 100000:
                    break
        
        print(f"📊 RESULTADOS DA ANÁLISE:")
        print(f"   • Total de linhas processadas: {total_linhas:,}")
        print(f"   • Linhas válidas: {linhas_validas:,}")
        print(f"   • Combinações únicas: {len(combinacoes_unicas):,}")
        print()
        
        print(f"📈 DISTRIBUIÇÃO POR TAMANHO:")
        for tamanho in sorted(diferentes_tamanhos.keys()):
            quantidade = diferentes_tamanhos[tamanho]
            print(f"   • {tamanho} números: {quantidade:,} combinações")
        
        # Análise de duplicatas
        if linhas_validas > 0:
            taxa_duplicacao = linhas_validas / len(combinacoes_unicas) if len(combinacoes_unicas) > 0 else 0
            print(f"\n🔍 ANÁLISE DE DUPLICAÇÃO:")
            print(f"   • Taxa de duplicação: {taxa_duplicacao:.2f}x")
            print(f"   • Duplicatas: {linhas_validas - len(combinacoes_unicas):,}")
            
            if taxa_duplicacao > 2:
                print(f"   ⚠️ ALTA DUPLICAÇÃO DETECTADA!")
                print(f"   💡 Isso explica como ter mais que C(25,20) = 53.130")
    
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

def main():
    """
    Função principal
    """
    print("🧮 ANÁLISE MATEMÁTICA: COMBINAÇÕES DE 20 NÚMEROS")
    print("=" * 60)
    print("❓ PERGUNTA: Como gerar 1 milhão se só existem 53.130 combinações únicas?")
    print()
    
    # 1. Cálculo teórico
    combinacoes_teoricas = calcular_combinacoes_teoricas()
    
    # 2. Investigação teórica
    investigar_arquivo_1milhao()
    
    print("\n" + "="*60)
    
    # 3. Verificação de arquivos reais
    verificar_arquivo_real()
    
    print("\n" + "="*60)
    
    # 4. Análise detalhada
    analisar_primeiro_arquivo_grande()
    
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   • Máximo teórico: {combinacoes_teoricas:,} combinações únicas de 20 números")
    print(f"   • Se arquivo tem 1 milhão, há ~18x duplicação")
    print(f"   • Necessário verificar arquivo específico para confirmar")

if __name__ == "__main__":
    main()