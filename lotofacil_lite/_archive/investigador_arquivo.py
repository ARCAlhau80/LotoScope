#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 INVESTIGADOR DE PROBLEMAS NO ARQUIVO
======================================

Investiga problemas no arquivo gerado:
1. Formato das linhas
2. Duplicatas
3. Distribuição
4. Linha específica 2.000.000
"""

def investigar_arquivo():
    """
    Investiga problemas no arquivo
    """
    print("🔍" * 25)
    print("🔍 INVESTIGADOR DE PROBLEMAS NO ARQUIVO")
    print("🔍" * 25)
    
    arquivo = "combinacoes_academico_alta_15nums_20250914_161542.txt"
    
    try:
        print(f"📁 Investigando arquivo: {arquivo}")
        
        linha_atual = 0
        linhas_validas = 0
        linhas_cabecalho = 0
        linhas_vazias = 0
        linhas_erro = 0
        linha_2M = None
        amostras = []
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha_atual += 1
                linha_original = linha
                linha = linha.strip()
                
                # Capturar linha 2.000.000
                if linha_atual == 2000000:
                    linha_2M = linha_original.strip()
                
                # Capturar amostras de diferentes posições
                if linha_atual in [1, 100, 1000, 10000, 100000, 1000000]:
                    amostras.append((linha_atual, linha_original.strip()))
                
                # Classificar linha
                if not linha:
                    linhas_vazias += 1
                elif linha.startswith('#') or linha.startswith('=') or linha.startswith('-') or 'COMBINAÇÕES' in linha.upper() or 'TOP' in linha.upper():
                    linhas_cabecalho += 1
                else:
                    try:
                        # Tentar extrair números
                        if '|' in linha:  # Formato com score
                            partes = linha.split('|')
                            if len(partes) >= 2:
                                numeros_str = partes[1].strip()
                            else:
                                linhas_erro += 1
                                continue
                        else:  # Formato simples
                            numeros_str = linha.strip()
                        
                        if ',' in numeros_str:
                            numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                            if len(numeros) == 15 and all(1 <= n <= 25 for n in numeros):
                                linhas_validas += 1
                            else:
                                linhas_erro += 1
                        else:
                            linhas_erro += 1
                    except:
                        linhas_erro += 1
                
                # Progress
                if linha_atual % 1000000 == 0:
                    print(f"⏱️ Investigando: {linha_atual:,} linhas...")
        
        print(f"\n📊 ESTATÍSTICAS DO ARQUIVO:")
        print(f"📋 Total de linhas: {linha_atual:,}")
        print(f"✅ Linhas válidas (combinações): {linhas_validas:,}")
        print(f"📝 Linhas de cabeçalho: {linhas_cabecalho:,}")
        print(f"⚪ Linhas vazias: {linhas_vazias:,}")
        print(f"❌ Linhas com erro: {linhas_erro:,}")
        
        print(f"\n📋 AMOSTRAS DE LINHAS:")
        for linha_num, conteudo in amostras:
            print(f"Linha {linha_num:,}: {conteudo[:100]}...")
        
        if linha_2M:
            print(f"\n📍 LINHA 2.000.000:")
            print(f"   {linha_2M}")
        
        # Análise da discrepância
        print(f"\n🔍 ANÁLISE DA DISCREPÂNCIA:")
        total_esperado = 3268760
        if linhas_validas != total_esperado:
            print(f"❌ PROBLEMA: Esperava {total_esperado:,} combinações, mas encontrou {linhas_validas:,}")
            diferenca = abs(linhas_validas - total_esperado)
            print(f"📊 Diferença: {diferenca:,} combinações")
            
            if linhas_validas > total_esperado:
                print("🔍 Possível causa: DUPLICATAS no arquivo")
            else:
                print("🔍 Possível causa: COMBINAÇÕES FALTANDO")
        else:
            print(f"✅ Número correto de combinações: {linhas_validas:,}")
        
        return linhas_validas, linha_2M
        
    except Exception as e:
        print(f"❌ Erro durante investigação: {e}")
        return 0, None

def main():
    """
    Função principal
    """
    print("🔍 INVESTIGADOR DE PROBLEMAS NO ARQUIVO")
    print("=" * 50)
    print("💡 Investigando problemas no arquivo gerado")
    print()
    
    try:
        linhas_validas, linha_2M = investigar_arquivo()
        
        print("\n" + "=" * 60)
        print("🔍 INVESTIGAÇÃO CONCLUÍDA")
        
        if linhas_validas == 3268760:
            print("✅ Arquivo tem o número correto de combinações")
            print("🤔 Problema pode estar no validador ou formato")
        else:
            print("❌ Arquivo NÃO tem o número correto de combinações")
            print("🤔 Problema está no gerador")
        
        if linha_2M:
            print(f"📍 Linha 2.000.000 encontrada e analisada")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Investigação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()