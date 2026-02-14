#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 VERIFICADOR DE LINHA ESPECÍFICA
=================================

Verifica uma linha específica do arquivo de combinações
e também procura a combinação exata do resultado.
"""

import itertools

def verificar_linha_especifica():
    """
    Verifica a linha 2.000.000 e procura a combinação exata
    """
    print("🔍" * 25)
    print("🔍 VERIFICADOR DE LINHA ESPECÍFICA")
    print("🔍" * 25)
    
    # Resultado do sorteio
    resultado = [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]
    resultado_set = set(resultado)
    resultado_str = "2,6,7,8,9,10,11,12,16,17,18,19,22,24,25"
    
    print(f"🎲 Resultado procurado: {resultado_str}")
    
    arquivo = "combinacoes_academico_alta_15nums_20250914_161542.txt"
    
    try:
        print(f"\n📁 Analisando arquivo: {arquivo}")
        print("🔍 Procurando linha 2.000.000 e a combinação exata...")
        
        linha_atual = 0
        linha_target = 2000000
        combinacao_linha_target = None
        combinacao_exata_encontrada = False
        linha_combinacao_exata = 0
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha_atual += 1
                linha = linha.strip()
                
                # Pular linhas vazias, comentários ou cabeçalhos
                if not linha or linha.startswith('#') or linha.startswith('=') or linha.startswith('-') or 'COMBINAÇÕES' in linha.upper():
                    continue
                
                try:
                    # Extrair números da linha
                    if '|' in linha:  # Formato com score: "123. 1500 | 1,2,3,..."
                        partes = linha.split('|')
                        if len(partes) >= 2:
                            numeros_str = partes[1].strip()
                        else:
                            continue
                    else:  # Formato simples: "1,2,3,..."
                        numeros_str = linha.strip()
                    
                    # Converter para números
                    if ',' in numeros_str:
                        numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                        numeros_set = set(numeros)
                    else:
                        continue
                    
                    # Verificar se tem exatamente 15 números válidos
                    if len(numeros) != 15 or not all(1 <= n <= 25 for n in numeros):
                        continue
                    
                    # Salvar linha target
                    if linha_atual == linha_target:
                        combinacao_linha_target = sorted(numeros)
                        print(f"📍 LINHA {linha_target}: {','.join(map(str, combinacao_linha_target))}")
                    
                    # Verificar se é a combinação exata
                    if numeros_set == resultado_set:
                        combinacao_exata_encontrada = True
                        linha_combinacao_exata = linha_atual
                        print(f"🎉 COMBINAÇÃO EXATA ENCONTRADA! Linha {linha_atual}")
                        print(f"   Combinação: {','.join(map(str, sorted(numeros)))}")
                        break
                    
                    # Progress a cada 500.000 linhas
                    if linha_atual % 500000 == 0:
                        print(f"⏱️ Processadas {linha_atual:,} linhas...")
                
                except Exception as e:
                    continue
        
        print(f"\n📊 RESULTADO DA VERIFICAÇÃO:")
        print(f"📋 Total de linhas processadas: {linha_atual:,}")
        
        if combinacao_linha_target:
            print(f"📍 Linha {linha_target}: {','.join(map(str, combinacao_linha_target))}")
        else:
            print(f"❌ Linha {linha_target} não encontrada ou inválida")
        
        if combinacao_exata_encontrada:
            print(f"🎉 Combinação exata ENCONTRADA na linha {linha_combinacao_exata}!")
        else:
            print(f"❌ Combinação exata NÃO encontrada")
        
        # Verificar se realmente existe todas as combinações
        print(f"\n🧮 VERIFICAÇÃO TEÓRICA:")
        total_teorico = len(list(itertools.combinations(range(1, 26), 15)))
        print(f"📊 Total teórico de combinações C(25,15): {total_teorico:,}")
        print(f"📁 Linhas no arquivo: {linha_atual:,}")
        
        if linha_atual >= total_teorico:
            print("✅ O arquivo tem pelo menos todas as combinações teóricas")
        else:
            print("❌ O arquivo NÃO tem todas as combinações teóricas")
        
        # Se não encontrou, vamos procurar manualmente
        if not combinacao_exata_encontrada:
            print(f"\n🔍 PROCURANDO MANUALMENTE A COMBINAÇÃO {resultado_str}...")
            return procurar_combinacao_manual(arquivo, resultado_set, resultado_str)
        
        return combinacao_exata_encontrada
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        return False

def procurar_combinacao_manual(arquivo, resultado_set, resultado_str):
    """
    Procura manualmente a combinação linha por linha
    """
    print("🔍 BUSCA MANUAL LINHA POR LINHA...")
    
    try:
        linha_atual = 0
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha_atual += 1
                linha_original = linha
                linha = linha.strip()
                
                # Verificar se a linha contém exatamente nossa combinação
                if resultado_str in linha:
                    print(f"🎯 POSSÍVEL MATCH na linha {linha_atual}!")
                    print(f"   Linha completa: {linha_original.strip()}")
                    
                    # Extrair e verificar
                    try:
                        if '|' in linha:
                            partes = linha.split('|')
                            if len(partes) >= 2:
                                numeros_str = partes[1].strip()
                            else:
                                numeros_str = linha
                        else:
                            numeros_str = linha
                        
                        if ',' in numeros_str:
                            numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                            if set(numeros) == resultado_set:
                                print(f"🎉 CONFIRMADO! Combinação exata na linha {linha_atual}")
                                return True
                    except:
                        pass
                
                if linha_atual % 1000000 == 0:
                    print(f"⏱️ Busca manual: {linha_atual:,} linhas...")
        
        print(f"❌ Busca manual concluída: {linha_atual:,} linhas, combinação NÃO encontrada")
        return False
        
    except Exception as e:
        print(f"❌ Erro na busca manual: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🔍 VERIFICADOR DE LINHA ESPECÍFICA")
    print("=" * 45)
    print("💡 Verificando linha 2.000.000 e procurando a combinação exata")
    print("   do resultado 2,6,7,8,9,10,11,12,16,17,18,19,22,24,25")
    print()
    
    try:
        encontrado = verificar_linha_especifica()
        
        print("\n" + "=" * 60)
        if encontrado:
            print("🎉 RESULTADO: Combinação exata ENCONTRADA!")
        else:
            print("❌ RESULTADO: Combinação exata NÃO encontrada!")
            print("🤔 Isso indica um problema no gerador ou validador.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Verificação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()