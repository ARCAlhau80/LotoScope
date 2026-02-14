#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 INVESTIGADOR DE ARQUIVO ACADÊMICO
===================================

Verifica se o arquivo combinacoes_academico_baixa_20nums_20250914_180204.txt:
1. Contém combinações únicas
2. Possui a combinação específica [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

import os
from pathlib import Path

def investigar_arquivo_academico():
    """
    Investiga o arquivo acadêmico para verificar unicidade e presença da combinação
    """
    print("🔍 INVESTIGADOR DE ARQUIVO ACADÊMICO")
    print("=" * 60)
    
    # Arquivo a investigar
    arquivo_academico = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\combinacoes_academico_baixa_20nums_20250914_180204.txt"
    
    # Combinação a procurar
    combinacao_teste = [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]
    combinacao_ordenada = tuple(sorted(combinacao_teste))
    
    print(f"📁 Arquivo: {Path(arquivo_academico).name}")
    print(f"🔍 Procurando: {combinacao_teste}")
    print(f"🔍 Ordenada: {list(combinacao_ordenada)}")
    print()
    
    # Verifica se arquivo existe
    if not os.path.exists(arquivo_academico):
        print(f"❌ ARQUIVO NÃO ENCONTRADO!")
        print(f"   Caminho: {arquivo_academico}")
        return False
    
    # Obter informações do arquivo
    tamanho_arquivo = os.path.getsize(arquivo_academico)
    print(f"📊 Tamanho do arquivo: {tamanho_arquivo:,} bytes ({tamanho_arquivo / 1024 / 1024:.1f} MB)")
    
    try:
        # Ler e processar arquivo
        combinacoes_encontradas = set()
        combinacoes_20_nums = []  # Para armazenar combinações de 20 números
        combinacoes_15_nums = set()  # Para extrair combinações de 15 números
        
        total_linhas = 0
        linhas_validas = 0
        combinacao_encontrada = False
        linha_encontrada = 0
        
        print(f"🔄 Processando arquivo...")
        
        with open(arquivo_academico, 'r', encoding='utf-8') as f:
            for num_linha, linha in enumerate(f, 1):
                total_linhas += 1
                linha = linha.strip()
                
                # Pular cabeçalhos e linhas vazias
                if not linha or linha.startswith('#') or linha.startswith('=') or 'COMBINAÇÕES' in linha.upper():
                    continue
                
                if not any(c.isdigit() for c in linha):
                    continue
                
                try:
                    # Extrair números da linha
                    if ':' in linha:  # Formato "Jogo X: numeros"
                        numeros_str = linha.split(':')[1].strip()
                    else:
                        numeros_str = linha
                    
                    if ',' in numeros_str:
                        numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                        
                        # Verifica se tem números válidos
                        if len(numeros) >= 15 and all(1 <= n <= 25 for n in numeros):
                            linhas_validas += 1
                            
                            # Se for combinação de 20 números
                            if len(numeros) == 20:
                                combinacoes_20_nums.append(sorted(numeros))
                                combinacao_20_tuple = tuple(sorted(numeros))
                                combinacoes_encontradas.add(combinacao_20_tuple)
                                
                                # Verifica se contém nossa combinação de 15 números
                                numeros_set = set(numeros)
                                combinacao_teste_set = set(combinacao_teste)
                                
                                if combinacao_teste_set.issubset(numeros_set):
                                    combinacao_encontrada = True
                                    linha_encontrada = linhas_validas
                                    print(f"✅ COMBINAÇÃO ENCONTRADA na linha {linha_encontrada}!")
                                    print(f"📊 Combinação de 20: {sorted(numeros)}")
                                    print(f"🎯 Contém nossa combinação de 15: {combinacao_teste}")
                                    break
                            
                            # Se for combinação de 15 números
                            elif len(numeros) == 15:
                                combinacao_15_tuple = tuple(sorted(numeros))
                                combinacoes_15_nums.add(combinacao_15_tuple)
                                
                                if combinacao_15_tuple == combinacao_ordenada:
                                    combinacao_encontrada = True
                                    linha_encontrada = linhas_validas
                                    print(f"✅ COMBINAÇÃO EXATA ENCONTRADA na linha {linha_encontrada}!")
                                    print(f"🎯 Combinação: {list(combinacao_15_tuple)}")
                                    break
                
                except Exception as e:
                    continue
                
                # Progress a cada 1000 linhas
                if total_linhas % 1000 == 0:
                    print(f"   📍 Processadas {total_linhas:,} linhas...")
        
        # Relatório final
        print(f"\n📊 RELATÓRIO FINAL:")
        print(f"   • Total de linhas: {total_linhas:,}")
        print(f"   • Linhas válidas: {linhas_validas:,}")
        
        if len(combinacoes_20_nums) > 0:
            print(f"   • Combinações de 20 números: {len(combinacoes_20_nums):,}")
            print(f"   • Combinações únicas de 20: {len(combinacoes_encontradas):,}")
            
            # Verifica duplicatas
            if len(combinacoes_20_nums) == len(combinacoes_encontradas):
                print(f"   ✅ TODAS AS COMBINAÇÕES DE 20 SÃO ÚNICAS!")
            else:
                duplicatas = len(combinacoes_20_nums) - len(combinacoes_encontradas)
                print(f"   ⚠️ {duplicatas:,} combinações duplicadas encontradas")
        
        if len(combinacoes_15_nums) > 0:
            print(f"   • Combinações únicas de 15: {len(combinacoes_15_nums):,}")
        
        # Resultado da busca
        print(f"\n🎯 RESULTADO DA BUSCA:")
        if combinacao_encontrada:
            print(f"   ✅ COMBINAÇÃO ENCONTRADA!")
            print(f"   📍 Posição: linha {linha_encontrada}")
            print(f"   🎉 O arquivo CONTÉM a combinação procurada!")
        else:
            print(f"   ❌ COMBINAÇÃO NÃO ENCONTRADA")
            print(f"   ⚠️ A combinação {combinacao_teste} não está no arquivo")
        
        return combinacao_encontrada
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🔍 INVESTIGADOR DE ARQUIVO ACADÊMICO")
    print("=" * 60)
    print("🎯 Verificando arquivo: combinacoes_academico_baixa_20nums_20250914_180204.txt")
    print("🔍 Procurando: [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]")
    print()
    
    resultado = investigar_arquivo_academico()
    
    if resultado:
        print(f"\n🎉 CONCLUSÃO: SUCESSO!")
        print(f"✅ Arquivo contém a combinação procurada")
        print(f"✅ Sistema acadêmico funcionou corretamente")
    else:
        print(f"\n❌ CONCLUSÃO: NÃO ENCONTRADA")
        print(f"⚠️ Arquivo não contém a combinação procurada")
        print(f"💡 Considere usar o gerador exaustivo para garantia 100%")

if __name__ == "__main__":
    main()