#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 VERIFICADOR DE DUPLICATAS - ARQUIVO ESPECÍFICO
=================================================

Analisa o arquivo combinacoes_academico_baixa_20nums_20250914_204044.txt
para verificar se a correção eliminou as duplicatas.

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

import os
from collections import Counter

def analisar_duplicatas_arquivo():
    """
    Analisa duplicatas no arquivo específico
    """
    arquivo = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combinacoes_academico_baixa_20nums_20250914_204044.txt"
    
    print("🔍 VERIFICADOR DE DUPLICATAS - ARQUIVO ESPECÍFICO")
    print("=" * 60)
    print(f"📄 Arquivo: combinacoes_academico_baixa_20nums_20250914_204044.txt")
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return
    
    # Informações básicas
    tamanho = os.path.getsize(arquivo)
    tamanho_mb = tamanho / (1024 * 1024)
    print(f"💾 Tamanho: {tamanho:,} bytes ({tamanho_mb:.1f} MB)")
    
    print(f"\n🔄 Analisando conteúdo...")
    
    combinacoes_encontradas = []
    combinacoes_set = set()
    total_linhas = 0
    linhas_validas = 0
    diferentes_tamanhos = {}
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha_num, linha in enumerate(f, 1):
                total_linhas += 1
                linha = linha.strip()
                
                # Pula linhas vazias ou cabeçalhos
                if not linha or not any(c.isdigit() for c in linha):
                    continue
                
                try:
                    # Extrair números da linha
                    if ':' in linha:
                        numeros_str = linha.split(':')[1].strip()
                    else:
                        numeros_str = linha
                    
                    # Remove "Jogo X:" se existir no início
                    if numeros_str.startswith('Jogo '):
                        parts = numeros_str.split(':', 1)
                        if len(parts) > 1:
                            numeros_str = parts[1].strip()
                    
                    if ',' in numeros_str:
                        numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                        
                        if len(numeros) >= 15 and all(1 <= n <= 25 for n in numeros):
                            linhas_validas += 1
                            
                            # Conta tamanhos
                            tamanho_comb = len(numeros)
                            diferentes_tamanhos[tamanho_comb] = diferentes_tamanhos.get(tamanho_comb, 0) + 1
                            
                            # Normaliza combinação (ordenada)
                            combinacao_ordenada = tuple(sorted(numeros))
                            combinacoes_encontradas.append({
                                'linha': linha_num,
                                'combinacao': combinacao_ordenada,
                                'tamanho': tamanho_comb
                            })
                            
                            combinacoes_set.add(combinacao_ordenada)
                
                except Exception as e:
                    continue
        
        print(f"📊 RESULTADOS DA ANÁLISE:")
        print(f"   • Total de linhas: {total_linhas:,}")
        print(f"   • Linhas válidas: {linhas_validas:,}")
        print(f"   • Combinações únicas: {len(combinacoes_set):,}")
        
        # Calcula duplicatas
        duplicatas = linhas_validas - len(combinacoes_set)
        
        print(f"\n🎯 ANÁLISE DE DUPLICATAS:")
        print(f"   • Total de combinações: {linhas_validas:,}")
        print(f"   • Combinações únicas: {len(combinacoes_set):,}")
        print(f"   • Duplicatas encontradas: {duplicatas:,}")
        
        if duplicatas == 0:
            print(f"   🎉 PERFEITO: ZERO DUPLICATAS ENCONTRADAS!")
            print(f"   ✅ Correção funcionou 100%!")
        else:
            taxa_duplicacao = linhas_validas / len(combinacoes_set) if len(combinacoes_set) > 0 else 0
            print(f"   ❌ Taxa de duplicação: {taxa_duplicacao:.2f}x")
            print(f"   💡 Correção ainda não está funcionando perfeitamente")
        
        print(f"\n📈 DISTRIBUIÇÃO POR TAMANHO:")
        for tamanho in sorted(diferentes_tamanhos.keys()):
            quantidade = diferentes_tamanhos[tamanho]
            porcentagem = (quantidade / linhas_validas) * 100 if linhas_validas > 0 else 0
            print(f"   • {tamanho} números: {quantidade:,} ({porcentagem:.1f}%)")
        
        # Análise específica para 20 números
        combinacoes_20_nums = [c for c in combinacoes_encontradas if c['tamanho'] == 20]
        if combinacoes_20_nums:
            print(f"\n🎯 ANÁLISE ESPECÍFICA - 20 NÚMEROS:")
            print(f"   • Combinações de 20 números: {len(combinacoes_20_nums):,}")
            
            # Verifica duplicatas específicas de 20 números
            combinacoes_20_set = set()
            duplicatas_20 = []
            
            for comb_info in combinacoes_20_nums:
                comb_tuple = comb_info['combinacao']
                if comb_tuple in combinacoes_20_set:
                    duplicatas_20.append(comb_info)
                else:
                    combinacoes_20_set.add(comb_tuple)
            
            print(f"   • Combinações únicas de 20 números: {len(combinacoes_20_set):,}")
            print(f"   • Duplicatas de 20 números: {len(duplicatas_20):,}")
            
            # Limite matemático
            import math
            max_teorico = math.comb(25, 20)
            print(f"   • Máximo teórico C(25,20): {max_teorico:,}")
            
            if len(combinacoes_20_set) <= max_teorico:
                print(f"   ✅ Dentro do limite matemático!")
            else:
                print(f"   ❌ ERRO: Mais combinações que o matematicamente possível!")
            
            # Mostra algumas duplicatas se existirem
            if duplicatas_20:
                print(f"\n🔍 PRIMEIRAS 5 DUPLICATAS DE 20 NÚMEROS:")
                for i, dup in enumerate(duplicatas_20[:5], 1):
                    print(f"   {i}. Linha {dup['linha']}: {list(dup['combinacao'])}")
        
        # Mostra amostra das primeiras combinações
        print(f"\n📋 PRIMEIRAS 5 COMBINAÇÕES ENCONTRADAS:")
        for i, comb_info in enumerate(combinacoes_encontradas[:5], 1):
            print(f"   {i}. Linha {comb_info['linha']} ({comb_info['tamanho']} nums): {list(comb_info['combinacao'])}")
        
        # Verifica se há padrões suspeitos
        print(f"\n🕵️ ANÁLISE DE PADRÕES SUSPEITOS:")
        
        # Conta números mais frequentes
        contador_numeros = Counter()
        for comb_info in combinacoes_encontradas:
            contador_numeros.update(comb_info['combinacao'])
        
        print(f"   🔥 TOP 10 NÚMEROS MAIS FREQUENTES:")
        for numero, freq in contador_numeros.most_common(10):
            percent = (freq / linhas_validas) * 100 if linhas_validas > 0 else 0
            print(f"      {numero:2d}: {freq:3d}x ({percent:4.1f}%)")
        
        # Verifica se algum número aparece em TODAS as combinações (suspeito)
        numeros_em_todas = []
        if linhas_validas > 0:
            for numero in range(1, 26):
                if contador_numeros[numero] == linhas_validas:
                    numeros_em_todas.append(numero)
        
        if numeros_em_todas:
            print(f"   ⚠️ NÚMEROS EM TODAS AS COMBINAÇÕES: {numeros_em_todas}")
            print(f"   💡 Isso pode indicar problema no algoritmo de geração")
        else:
            print(f"   ✅ Boa distribuição - nenhum número em todas as combinações")
    
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Função principal
    """
    analisar_duplicatas_arquivo()

if __name__ == "__main__":
    main()