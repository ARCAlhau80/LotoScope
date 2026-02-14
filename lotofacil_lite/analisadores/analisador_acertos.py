#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALISADOR DE ACERTOS - VERIFICAR 15 NÚMEROS
==============================================

Verifica se um resultado específico acerta 15 números em alguma 
linha do arquivo de combinações rankeadas.

Resultado a verificar: 2,6,7,8,9,10,11,12,16,17,18,19,22,24,25
"""

def analisar_acertos():
    """
    Analisa se o resultado acerta 15 números em alguma linha
    """
    print("🎯" * 25)
    print("🎯 ANALISADOR DE ACERTOS - VERIFICAR 15 NÚMEROS")
    print("🎯" * 25)
    
    # Resultado do sorteio
    resultado = {2,6,7,8,9,10,11,12,16,17,18,19,22,24,25}
    resultado_str = "2,6,7,8,9,10,11,12,16,17,18,19,22,24,25"
    
    print(f"🎲 Resultado do sorteio: {resultado_str}")
    print(f"📊 Total de números no resultado: {len(resultado)}")
    
    # Arquivo a analisar
    arquivo = "combinacoes_academico_alta_15nums_20250914_161542.txt"
    
    print(f"\n📁 Analisando arquivo: {arquivo}")
    print("🔍 Procurando combinações que acertam 15 números...")
    
    try:
        linha_atual = 0
        acertos_15 = []
        acertos_14 = []
        acertos_13 = []
        max_acertos = 0
        melhor_linha = 0
        melhor_combinacao = ""
        
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
                    elif ':' in linha:  # Formato "Jogo X: 1,2,3,..."
                        partes = linha.split(':')
                        if len(partes) >= 2:
                            numeros_str = partes[1].strip()
                        else:
                            continue
                    else:  # Formato simples: "1,2,3,..."
                        numeros_str = linha.strip()
                    
                    # Converter para números
                    if ',' in numeros_str:
                        numeros = set(int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit())
                    else:
                        continue
                    
                    # Verificar se tem exatamente 15 números válidos
                    if len(numeros) != 15 or not all(1 <= n <= 25 for n in numeros):
                        continue
                    
                    # Calcular intersecção
                    intersecao = resultado & numeros
                    acertos = len(intersecao)
                    
                    # Registrar melhor
                    if acertos > max_acertos:
                        max_acertos = acertos
                        melhor_linha = linha_atual
                        melhor_combinacao = ','.join(map(str, sorted(numeros)))
                    
                    # Categorizar acertos
                    if acertos == 15:
                        acertos_15.append((linha_atual, numeros_str, sorted(intersecao)))
                        print(f"🎉 ACERTO DE 15! Linha {linha_atual}")
                        print(f"   Combinação: {','.join(map(str, sorted(numeros)))}")
                        print(f"   Números que acertaram: {sorted(intersecao)}")
                    elif acertos == 14:
                        acertos_14.append((linha_atual, numeros_str, sorted(intersecao)))
                    elif acertos == 13:
                        acertos_13.append((linha_atual, numeros_str, sorted(intersecao)))
                    
                    # Progress a cada 100.000 linhas
                    if linha_atual % 100000 == 0:
                        print(f"⏱️ Processadas {linha_atual:,} linhas... (Melhor até agora: {max_acertos} acertos)")
                
                except Exception as e:
                    continue  # Ignorar linhas com erro
        
        print(f"\n📊 ANÁLISE CONCLUÍDA!")
        print(f"📋 Total de linhas processadas: {linha_atual:,}")
        print(f"🎯 Máximo de acertos encontrado: {max_acertos}")
        
        if melhor_linha > 0:
            print(f"🏆 Melhor combinação (linha {melhor_linha}): {melhor_combinacao}")
        
        print(f"\n📈 RESUMO DE ACERTOS:")
        print(f"🎉 Acertos de 15 números: {len(acertos_15)}")
        print(f"🥈 Acertos de 14 números: {len(acertos_14)}")
        print(f"🥉 Acertos de 13 números: {len(acertos_13)}")
        
        # Mostrar detalhes dos acertos de 15
        if acertos_15:
            print(f"\n🎉 DETALHES DOS ACERTOS DE 15 NÚMEROS:")
            for i, (linha, combinacao, numeros_acertados) in enumerate(acertos_15, 1):
                print(f"{i}. Linha {linha}: {','.join(map(str, numeros_acertados))}")
        
        # Mostrar alguns acertos de 14 se houver
        elif acertos_14:
            print(f"\n🥈 PRIMEIROS 5 ACERTOS DE 14 NÚMEROS:")
            for i, (linha, combinacao, numeros_acertados) in enumerate(acertos_14[:5], 1):
                faltou = sorted(resultado - set(numeros_acertados))
                print(f"{i}. Linha {linha}: 14 acertos - Faltou: {faltou}")
        
        # Mostrar alguns acertos de 13 se houver
        elif acertos_13:
            print(f"\n🥉 PRIMEIROS 5 ACERTOS DE 13 NÚMEROS:")
            for i, (linha, combinacao, numeros_acertados) in enumerate(acertos_13[:5], 1):
                faltou = sorted(resultado - set(numeros_acertados))
                print(f"{i}. Linha {linha}: 13 acertos - Faltou: {faltou}")
        
        return len(acertos_15) > 0
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        print("💡 Certifique-se de que o arquivo está na pasta atual")
        return False
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🎯 ANALISADOR DE ACERTOS - VERIFICAR 15 NÚMEROS")
    print("=" * 55)
    print("💡 Verificando se o resultado 2,6,7,8,9,10,11,12,16,17,18,19,22,24,25")
    print("   acerta 15 números em alguma linha do arquivo rankeado.")
    print()
    
    try:
        acertou_15 = analisar_acertos()
        
        print("\n" + "=" * 60)
        if acertou_15:
            print("🎉 RESULTADO: SIM! Encontrado(s) acerto(s) de 15 números!")
        else:
            print("❌ RESULTADO: NÃO foram encontrados acertos de 15 números.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Análise interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()