#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 VERIFICADOR DIRETO DA COMBINAÇÃO ESPECÍFICA
==============================================

Busca DIRETAMENTE pela combinação 2,6,7,8,9,10,11,12,16,17,18,19,22,24,25
e verifica se o arquivo está realmente completo.
"""

import itertools

def verificar_combinacao_direta():
    """
    Busca diretamente pela combinação específica
    """
    print("🚨" * 25)
    print("🚨 VERIFICADOR DIRETO DA COMBINAÇÃO ESPECÍFICA")
    print("🚨" * 25)
    
    # Combinação procurada
    resultado = [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]
    resultado_tuple = tuple(sorted(resultado))
    resultado_str = ','.join(map(str, sorted(resultado)))
    
    print(f"🎯 Combinação procurada: {resultado_str}")
    print(f"🔍 Formato tuple: {resultado_tuple}")
    
    arquivo = "combinacoes_academico_alta_15nums_20250914_161542.txt"
    
    try:
        print(f"\n📁 Verificando arquivo: {arquivo}")
        
        # Set para verificar unicidade e completude
        combinacoes_encontradas = set()
        linha_atual = 0
        combinacao_encontrada = False
        linha_combinacao = 0
        
        # Também vamos verificar algumas combinações específicas de controle
        controles = [
            tuple(sorted([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])),  # Primeira possível
            tuple(sorted([11,12,13,14,15,16,17,18,19,20,21,22,23,24,25])),  # Última possível
            tuple(sorted([1,3,5,7,9,11,13,15,17,19,21,23,25,2,4]))  # Combinação aleatória
        ]
        controles_encontrados = {combo: False for combo in controles}
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha_atual += 1
                linha = linha.strip()
                
                # Pular linhas vazias, comentários ou cabeçalhos
                if not linha or linha.startswith('#') or linha.startswith('=') or linha.startswith('-') or 'COMBINAÇÕES' in linha.upper() or 'TOP' in linha.upper() or 'Jogo' not in linha:
                    continue
                
                try:
                    # Extrair números (formato "Jogo X: numeros")
                    if ':' in linha:
                        partes = linha.split(':')
                        if len(partes) >= 2:
                            numeros_str = partes[1].strip()
                        else:
                            continue
                    else:
                        continue
                    
                    # Converter para números
                    if ',' in numeros_str:
                        numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                    else:
                        continue
                    
                    # Validar
                    if len(numeros) != 15 or not all(1 <= n <= 25 for n in numeros):
                        continue
                    
                    # Converter para tuple ordenada
                    combo_tuple = tuple(sorted(numeros))
                    
                    # Adicionar ao set
                    combinacoes_encontradas.add(combo_tuple)
                    
                    # Verificar se é nossa combinação
                    if combo_tuple == resultado_tuple:
                        combinacao_encontrada = True
                        linha_combinacao = linha_atual
                        print(f"🎉 COMBINAÇÃO ENCONTRADA! Linha {linha_atual}")
                        print(f"   Jogo: {linha}")
                    
                    # Verificar controles
                    for controle in controles:
                        if combo_tuple == controle:
                            controles_encontrados[controle] = True
                    
                    # Progress
                    if linha_atual % 500000 == 0:
                        print(f"⏱️ Processadas {linha_atual:,} linhas, {len(combinacoes_encontradas):,} combinações únicas")
                
                except Exception as e:
                    continue
        
        print(f"\n📊 RESULTADOS DA VERIFICAÇÃO:")
        print(f"📋 Total de linhas processadas: {linha_atual:,}")
        print(f"🎯 Combinações únicas encontradas: {len(combinacoes_encontradas):,}")
        print(f"📊 Total teórico esperado: 3,268,760")
        
        # Verificar completude
        if len(combinacoes_encontradas) == 3268760:
            print("✅ ARQUIVO COMPLETO: Todas as combinações estão presentes")
        else:
            diferenca = 3268760 - len(combinacoes_encontradas)
            print(f"❌ ARQUIVO INCOMPLETO: Faltam {diferenca:,} combinações")
        
        # Resultado da busca
        if combinacao_encontrada:
            print(f"🎉 COMBINAÇÃO ESPECÍFICA: ENCONTRADA na linha {linha_combinacao}")
        else:
            print(f"❌ COMBINAÇÃO ESPECÍFICA: NÃO ENCONTRADA")
        
        # Verificar controles
        print(f"\n🔍 VERIFICAÇÃO DE CONTROLES:")
        for i, (controle, encontrado) in enumerate(controles_encontrados.items(), 1):
            status = "✅ ENCONTRADO" if encontrado else "❌ NÃO ENCONTRADO"
            combo_str = ','.join(map(str, controle))
            print(f"   Controle {i}: {combo_str} - {status}")
        
        # Se não encontrou, vamos gerar a combinação teoricamente
        if not combinacao_encontrada:
            print(f"\n🧮 VERIFICAÇÃO TEÓRICA:")
            todas_combinacoes = list(itertools.combinations(range(1, 26), 15))
            if resultado_tuple in todas_combinacoes:
                posicao = todas_combinacoes.index(resultado_tuple) + 1
                print(f"✅ Combinação é VÁLIDA e deveria estar na posição {posicao:,}")
                print(f"❌ Mas NÃO está no arquivo gerado!")
            else:
                print(f"❌ Combinação é INVÁLIDA teoricamente (não deveria acontecer)")
        
        return combinacao_encontrada, len(combinacoes_encontradas)
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False, 0
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        return False, 0

def main():
    """
    Função principal
    """
    print("🚨 VERIFICADOR DIRETO DA COMBINAÇÃO ESPECÍFICA")
    print("=" * 60)
    print("💡 Busca DIRETAMENTE pela combinação que deveria ter acertado 15")
    print()
    
    try:
        encontrada, total_combinacoes = verificar_combinacao_direta()
        
        print("\n" + "=" * 70)
        print("🚨 VERIFICAÇÃO DIRETA CONCLUÍDA")
        
        if encontrada:
            print("🎉 RESULTADO: Combinação específica ENCONTRADA!")
            print("✅ O gerador e arquivo estão corretos")
            print("❌ O problema estava no analisador anterior")
        else:
            print("❌ RESULTADO: Combinação específica NÃO ENCONTRADA!")
            if total_combinacoes < 3268760:
                print("🔍 CAUSA: Arquivo incompleto (gerador com problema)")
            else:
                print("🔍 CAUSA: Combinação específica faltando (bug no gerador)")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Verificação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()