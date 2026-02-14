#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 INVESTIGAÇÃO ESPECÍFICA: ARQUIVO DE 20 NÚMEROS
===============================================

Analisando especificamente o arquivo de 20 números para entender
como pode ter mais combinações que o máximo teórico de 53.130

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

import os
import math

def main():
    """
    Análise específica do arquivo de 20 números
    """
    print("🔍 INVESTIGAÇÃO: ARQUIVO DE 20 NÚMEROS")
    print("=" * 50)
    
    # Máximo teórico
    max_teorico = math.comb(25, 20)
    print(f"📊 Máximo teórico C(25,20): {max_teorico:,} combinações únicas")
    print()
    
    # Arquivo específico
    arquivo = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combinacoes_academico_baixa_20nums_20250914_180204.txt"
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return
    
    # Informações básicas do arquivo
    tamanho = os.path.getsize(arquivo)
    tamanho_mb = tamanho / (1024 * 1024)
    
    print(f"📄 Arquivo: combinacoes_academico_baixa_20nums_20250914_180204.txt")
    print(f"💾 Tamanho: {tamanho:,} bytes ({tamanho_mb:.1f} MB)")
    print()
    
    # Análise linha por linha
    print("🔄 Analisando conteúdo...")
    
    combinacoes_unicas = set()
    total_linhas = 0
    linhas_validas = 0
    linhas_20_nums = 0
    diferentes_tamanhos = {}
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha_num, linha in enumerate(f, 1):
                total_linhas += 1
                linha = linha.strip()
                
                # Pular linhas vazias
                if not linha or not any(c.isdigit() for c in linha):
                    continue
                
                try:
                    # Extrair números da linha
                    if ':' in linha:
                        numeros_str = linha.split(':')[1].strip()
                    else:
                        numeros_str = linha
                    
                    if ',' in numeros_str:
                        numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                        
                        if len(numeros) >= 15 and all(1 <= n <= 25 for n in numeros):
                            linhas_validas += 1
                            
                            # Contar tamanhos
                            tamanho = len(numeros)
                            diferentes_tamanhos[tamanho] = diferentes_tamanhos.get(tamanho, 0) + 1
                            
                            # Contar especificamente 20 números
                            if tamanho == 20:
                                linhas_20_nums += 1
                            
                            # Adicionar às únicas
                            combinacao_tuple = tuple(sorted(numeros))
                            combinacoes_unicas.add(combinacao_tuple)
                
                except:
                    continue
        
        print(f"📊 RESULTADOS DA ANÁLISE:")
        print(f"   • Total de linhas: {total_linhas:,}")
        print(f"   • Linhas válidas: {linhas_validas:,}")
        print(f"   • Combinações únicas: {len(combinacoes_unicas):,}")
        print(f"   • Linhas com 20 números: {linhas_20_nums:,}")
        print()
        
        print(f"📈 DISTRIBUIÇÃO POR TAMANHO:")
        for tamanho in sorted(diferentes_tamanhos.keys()):
            quantidade = diferentes_tamanhos[tamanho]
            porcentagem = (quantidade / linhas_validas) * 100 if linhas_validas > 0 else 0
            print(f"   • {tamanho} números: {quantidade:,} ({porcentagem:.1f}%)")
        
        print()
        
        # Análise específica para 20 números
        if linhas_20_nums > 0:
            print(f"🎯 ANÁLISE ESPECÍFICA - 20 NÚMEROS:")
            print(f"   • Combinações de 20 números: {linhas_20_nums:,}")
            print(f"   • Máximo teórico possível: {max_teorico:,}")
            
            if linhas_20_nums > max_teorico:
                excesso = linhas_20_nums - max_teorico
                fator_duplicacao = linhas_20_nums / max_teorico
                print(f"   ⚠️ EXCESSO: {excesso:,} combinações a mais!")
                print(f"   📊 Fator de duplicação: {fator_duplicacao:.2f}x")
                print(f"   💡 EXPLICAÇÃO: Sistema está gerando duplicatas!")
            else:
                print(f"   ✅ Dentro do limite teórico")
        
        # Verificar duplicatas únicas de 20 números
        combinacoes_20_unicas = set()
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha or not any(c.isdigit() for c in linha):
                    continue
                
                try:
                    if ':' in linha:
                        numeros_str = linha.split(':')[1].strip()
                    else:
                        numeros_str = linha
                    
                    if ',' in numeros_str:
                        numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                        
                        if len(numeros) == 20 and all(1 <= n <= 25 for n in numeros):
                            combinacao_tuple = tuple(sorted(numeros))
                            combinacoes_20_unicas.add(combinacao_tuple)
                except:
                    continue
        
        print(f"\n🔍 ANÁLISE DE DUPLICATAS (20 NÚMEROS):")
        print(f"   • Total de linhas com 20 números: {linhas_20_nums:,}")
        print(f"   • Combinações únicas de 20 números: {len(combinacoes_20_unicas):,}")
        
        if linhas_20_nums > len(combinacoes_20_unicas):
            duplicatas = linhas_20_nums - len(combinacoes_20_unicas)
            taxa_duplicacao = linhas_20_nums / len(combinacoes_20_unicas) if len(combinacoes_20_unicas) > 0 else 0
            print(f"   • Duplicatas: {duplicatas:,}")
            print(f"   • Taxa de duplicação: {taxa_duplicacao:.2f}x")
            
            print(f"\n💡 CONCLUSÃO:")
            print(f"   ❌ IMPOSSÍVEL TER 1 MILHÃO DE COMBINAÇÕES ÚNICAS DE 20 NÚMEROS!")
            print(f"   📊 Máximo matemático: {max_teorico:,}")
            print(f"   🔄 Se arquivo tem mais, são DUPLICATAS ou MISTURAS de tamanhos")
        else:
            print(f"   ✅ Todas as combinações são únicas")
    
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

if __name__ == "__main__":
    main()