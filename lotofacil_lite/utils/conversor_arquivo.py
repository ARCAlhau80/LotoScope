#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 CONVERSOR DO ARQUIVO 20-15.txt PARA FORMATO CSV
=================================================

Converte o arquivo de TAB para formato CSV com vírgulas
"""

def converter_arquivo():
    """
    Converte o arquivo 20-15.txt para formato CSV
    """
    print("🔧 CONVERSOR PARA FORMATO CSV")
    print("=" * 35)
    
    arquivo_entrada = "../20-15.txt"
    arquivo_saida = "../20-15_convertido.txt"
    combinacoes_convertidas = []
    
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        print(f"📁 Lendo arquivo: {len(linhas)} linhas")
        
        for i, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha:
                continue
            
            try:
                if '\t' in linha:  # Separado por TAB
                    partes = linha.split('\t')
                    # Pegar só os números válidos
                    numeros = []
                    for parte in partes:
                        parte = parte.strip()
                        if parte.isdigit():
                            num = int(parte)
                            if 1 <= num <= 25:
                                numeros.append(num)
                    
                    # Verificar se temos 19 ou 20 números
                    if len(numeros) == 19:
                        # Descobrir qual número está faltando
                        todos_numeros = set(range(1, 26))
                        numeros_presentes = set(numeros)
                        faltando = todos_numeros - numeros_presentes
                        
                        # Pegar o menor número que falta (mais provável)
                        if faltando:
                            numero_faltando = min(faltando)
                            numeros.append(numero_faltando)
                            print(f"⚠️ Linha {i}: Adicionado número {numero_faltando} (estava faltando)")
                    
                    if len(numeros) == 20:
                        numeros_ordenados = sorted(numeros)
                        combinacoes_convertidas.append(numeros_ordenados)
                    else:
                        print(f"❌ Linha {i}: {len(numeros)} números encontrados - ignorando")
                
            except Exception as e:
                print(f"❌ Erro linha {i}: {e}")
        
        # Salvar arquivo convertido
        print(f"\n💾 Salvando {len(combinacoes_convertidas)} combinações em: {arquivo_saida}")
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            for combo in combinacoes_convertidas:
                linha_csv = ','.join(map(str, combo))
                f.write(f"{linha_csv}\n")
        
        print(f"✅ Arquivo convertido salvo!")
        print(f"📊 Total: {len(combinacoes_convertidas)} combinações")
        
        # Mostrar amostra
        print(f"\n📋 AMOSTRA DAS PRIMEIRAS 3 COMBINAÇÕES:")
        for i, combo in enumerate(combinacoes_convertidas[:3], 1):
            combo_str = ','.join(map(str, combo))
            print(f"{i}. {combo_str}")
        
        return arquivo_saida
        
    except Exception as e:
        print(f"❌ Erro ao converter arquivo: {e}")
        return None

if __name__ == "__main__":
    arquivo_convertido = converter_arquivo()
    if arquivo_convertido:
        print(f"\n🎉 CONVERSÃO CONCLUÍDA!")
        print(f"📁 Use o arquivo: {arquivo_convertido}")
        print("💡 Agora execute: python gerador_15_rankeado.py")
    else:
        print("\n❌ CONVERSÃO FALHOU!")
