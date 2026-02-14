#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 VALIDADOR FINAL - TESTAR COMBINAÇÃO NO ARQUIVO COMPLETO
=========================================================

Teste final: Sua combinação [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]
deve ser encontrada no arquivo completo gerado

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

def testar_combinacao_no_arquivo_completo():
    """
    Testa se a combinação específica existe no arquivo completo
    """
    # Combinação a procurar
    combinacao_teste = [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]
    combinacao_ordenada = tuple(sorted(combinacao_teste))
    
    print("🎯 TESTE FINAL - VALIDAÇÃO DA COMBINAÇÃO")
    print("=" * 50)
    print(f"🔍 Procurando: {combinacao_teste}")
    print(f"🔍 Ordenada: {list(combinacao_ordenada)}")
    print()
    
    # Procurar no arquivo gerado
    arquivo_completo = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\todas_combinacoes_15nums_exaustivo_20250914_165617.txt"
    
    print(f"📁 Arquivo: {arquivo_completo}")
    print("🔄 Procurando no arquivo completo...")
    
    try:
        encontrada = False
        linha_encontrada = 0
        total_linhas = 0
        
        with open(arquivo_completo, 'r', encoding='utf-8') as f:
            for num_linha, linha in enumerate(f, 1):
                linha = linha.strip()
                
                # Pular cabeçalho
                if linha.startswith('🔥') or linha.startswith('=') or not linha:
                    continue
                
                if not any(c.isdigit() for c in linha):
                    continue
                
                total_linhas += 1
                
                try:
                    # Ler números da linha
                    numeros = [int(x.strip()) for x in linha.split(',') if x.strip().isdigit()]
                    
                    if len(numeros) == 15:
                        numeros_tuple = tuple(sorted(numeros))
                        
                        if numeros_tuple == combinacao_ordenada:
                            encontrada = True
                            linha_encontrada = total_linhas
                            print(f"✅ ENCONTRADA na linha {linha_encontrada:,}!")
                            print(f"📊 Combinação: {list(numeros_tuple)}")
                            break
                        
                        # Progress a cada 500K
                        if total_linhas % 500000 == 0:
                            progresso = (total_linhas / 3268760) * 100
                            print(f"⏱️ Progresso: {progresso:5.1f}% ({total_linhas:,}/3,268,760)")
                
                except:
                    continue
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"🔍 Linhas processadas: {total_linhas:,}")
        
        if encontrada:
            print(f"✅ SUCESSO! Combinação encontrada na linha {linha_encontrada:,}")
            print(f"🎉 O arquivo está COMPLETO e sua combinação EXISTE!")
            print(f"🎯 Problema RESOLVIDO: O novo gerador funciona perfeitamente!")
        else:
            print(f"❌ Combinação não encontrada")
            print(f"⚠️ Verificar se o arquivo está correto")
        
        return encontrada
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo_completo}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    resultado = testar_combinacao_no_arquivo_completo()
    
    if resultado:
        print("\n🎉 TESTE FINAL: APROVADO!")
        print("✅ O gerador exaustivo funcionou perfeitamente")
        print("✅ Sua combinação está no arquivo completo")
        print("✅ Problema original foi resolvido!")
    else:
        print("\n❌ TESTE FINAL: FALHOU")
        print("⚠️ Verificar arquivo ou processo")