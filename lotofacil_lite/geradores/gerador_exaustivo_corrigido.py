#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GERADOR EXAUSTIVO - TODAS AS COMBINAÇÕES C(25,15)
==================================================

CORREÇÃO do problema identificado:
- O gerador acadêmico NÃO gera todas as combinações
- max_tentativas = quantas vezes tentar encontrar UMA combinação válida
- Este gerador cria MATEMATICAMENTE todas as 3.268.760 combinações possíveis

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

import itertools
import time
from datetime import datetime
from pathlib import Path

class GeradorExaustivo:
    """
    Gerador que cria TODAS as combinações possíveis de 15 números
    """
    
    def __init__(self):
        self.total_combinacoes = 0
        self.progresso_callback = None
    
    def gerar_todas_combinacoes_15(self, salvar_arquivo=True, callback_progresso=None):
        """
        Gera TODAS as 3.268.760 combinações possíveis de 15 números de 1 a 25
        
        Args:
            salvar_arquivo: Se deve salvar em arquivo
            callback_progresso: Função para callback de progresso
        
        Returns:
            str: Caminho do arquivo gerado ou None
        """
        print("🔥" * 25)
        print("🔥 GERADOR EXAUSTIVO - TODAS AS COMBINAÇÕES C(25,15)")
        print("🔥" * 25)
        
        print("🧮 Calculando todas as combinações possíveis...")
        print("📊 Total de combinações C(25,15) = 3.268.760")
        print("⚠️ ATENÇÃO: Este processo pode demorar vários minutos!")
        print()
        
        continuar = input("🤔 Deseja continuar? (s/n): ").strip().lower()
        if not continuar.startswith('s'):
            print("❌ Operação cancelada pelo usuário")
            return None
        
        inicio = time.time()
        
        # Gerar nome do arquivo
        if salvar_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"todas_combinacoes_15nums_exaustivo_{timestamp}.txt"
            caminho_arquivo = Path(__file__).parent / nome_arquivo
            
            print(f"💾 Salvando em: {nome_arquivo}")
            arquivo_handle = open(caminho_arquivo, 'w', encoding='utf-8')
            
            # Cabeçalho
            arquivo_handle.write("🔥 TODAS AS COMBINAÇÕES C(25,15) - GERADOR EXAUSTIVO\n")
            arquivo_handle.write("=" * 60 + "\n")
            arquivo_handle.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            arquivo_handle.write("Total de combinações: 3.268.760\n")
            arquivo_handle.write("Método: Itertools.combinations (matemático)\n")
            arquivo_handle.write("Formato: 15 números separados por vírgula (1-25)\n")
            arquivo_handle.write("=" * 60 + "\n\n")
        else:
            arquivo_handle = None
        
        try:
            print("🔄 Gerando combinações matematicamente...")
            
            # Usar itertools.combinations para gerar TODAS as combinações
            combinacoes_geradas = 0
            
            for combinacao in itertools.combinations(range(1, 26), 15):
                combinacoes_geradas += 1
                
                # Salvar no arquivo se solicitado
                if arquivo_handle:
                    combinacao_str = ','.join(map(str, combinacao))
                    arquivo_handle.write(f"{combinacao_str}\n")
                
                # Callback de progresso
                if callback_progresso and combinacoes_geradas % 100000 == 0:
                    callback_progresso(combinacoes_geradas, 3268760)
                
                # Progress no console
                if combinacoes_geradas % 250000 == 0:
                    tempo_decorrido = time.time() - inicio
                    progresso_pct = (combinacoes_geradas / 3268760) * 100
                    tempo_estimado = tempo_decorrido * (100 / progresso_pct) if progresso_pct > 0 else 0
                    tempo_restante = tempo_estimado - tempo_decorrido
                    
                    print(f"⏱️ {progresso_pct:5.1f}% | "
                          f"{combinacoes_geradas:,}/3,268,760 | "
                          f"Tempo: {tempo_decorrido:.0f}s | "
                          f"Restante: ~{tempo_restante:.0f}s")
            
            fim = time.time()
            tempo_total = fim - inicio
            
            print(f"\n✅ GERAÇÃO CONCLUÍDA!")
            print(f"📊 Total gerado: {combinacoes_geradas:,} combinações")
            print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
            print(f"🚀 Velocidade: {combinacoes_geradas / tempo_total:,.0f} combinações/segundo")
            
            # Verificação de integridade
            if combinacoes_geradas == 3268760:
                print("✅ VERIFICAÇÃO: Todas as combinações foram geradas corretamente!")
            else:
                print(f"❌ ERRO: Esperado 3.268.760, gerado {combinacoes_geradas}")
            
            # Fechar arquivo
            if arquivo_handle:
                arquivo_handle.close()
                print(f"💾 Arquivo salvo: {caminho_arquivo}")
                return str(caminho_arquivo)
            
            return combinacoes_geradas
            
        except Exception as e:
            print(f"❌ Erro durante geração: {e}")
            if arquivo_handle:
                arquivo_handle.close()
            return None
    
    def verificar_combinacao_especifica(self, combinacao_procurada):
        """
        Verifica se uma combinação específica existe no conjunto completo
        
        Args:
            combinacao_procurada: Lista com 15 números
            
        Returns:
            tuple: (existe, posicao)
        """
        print(f"🔍 Verificando se {combinacao_procurada} existe em C(25,15)...")
        
        combinacao_tuple = tuple(sorted(combinacao_procurada))
        
        # Verifica se é válida
        if len(set(combinacao_procurada)) != 15:
            return False, -1
        
        if not all(1 <= n <= 25 for n in combinacao_procurada):
            return False, -1
        
        # Procura na sequência matemática
        posicao = 0
        for combinacao in itertools.combinations(range(1, 26), 15):
            posicao += 1
            if combinacao == combinacao_tuple:
                print(f"✅ Combinação encontrada na posição {posicao:,}")
                return True, posicao
        
        print(f"❌ Combinação não encontrada (não deveria acontecer)")
        return False, -1
    
    def comparar_com_arquivo_existente(self, arquivo_para_verificar):
        """
        Compara um arquivo existente com o conjunto completo
        
        Args:
            arquivo_para_verificar: Caminho do arquivo para verificar
        """
        print(f"🔍 Comparando {arquivo_para_verificar} com conjunto completo...")
        
        try:
            # Ler combinações do arquivo
            combinacoes_arquivo = set()
            
            with open(arquivo_para_verificar, 'r', encoding='utf-8') as f:
                for linha_num, linha in enumerate(f, 1):
                    linha = linha.strip()
                    
                    # Pular cabeçalhos e linhas vazias
                    if not linha or linha.startswith('#') or linha.startswith('=') or 'COMBINAÇÕES' in linha.upper():
                        continue
                    
                    try:
                        # Extrair números
                        if ':' in linha:  # Formato "Jogo X: numeros"
                            numeros_str = linha.split(':')[1].strip()
                        else:
                            numeros_str = linha
                        
                        if ',' in numeros_str:
                            numeros = [int(x.strip()) for x in numeros_str.split(',') if x.strip().isdigit()]
                            
                            if len(numeros) == 15 and all(1 <= n <= 25 for n in numeros):
                                combinacoes_arquivo.add(tuple(sorted(numeros)))
                    
                    except Exception:
                        continue
            
            print(f"📊 Combinações únicas no arquivo: {len(combinacoes_arquivo):,}")
            print(f"📊 Total teórico esperado: 3,268,760")
            
            if len(combinacoes_arquivo) == 3268760:
                print("✅ ARQUIVO COMPLETO: Contém todas as combinações!")
            else:
                diferenca = 3268760 - len(combinacoes_arquivo)
                print(f"❌ ARQUIVO INCOMPLETO: Faltam {diferenca:,} combinações")
            
            # Verificar combinação específica de teste
            resultado_teste = [2,6,7,8,9,10,11,12,16,17,18,19,22,24,25]
            resultado_tuple = tuple(sorted(resultado_teste))
            
            if resultado_tuple in combinacoes_arquivo:
                print(f"✅ Combinação de teste ENCONTRADA no arquivo")
            else:
                print(f"❌ Combinação de teste NÃO ENCONTRADA no arquivo")
            
            return len(combinacoes_arquivo) == 3268760
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {arquivo_para_verificar}")
            return False
        except Exception as e:
            print(f"❌ Erro na comparação: {e}")
            return False

def main():
    """
    Função principal
    """
    print("🔥 GERADOR EXAUSTIVO - TODAS AS COMBINAÇÕES C(25,15)")
    print("=" * 60)
    print("💡 Este gerador cria MATEMATICAMENTE todas as 3.268.760 combinações")
    print("   possíveis de 15 números de 1 a 25 usando itertools.combinations")
    print()
    print("🔍 CORREÇÃO do problema identificado:")
    print("   • O gerador acadêmico NÃO gera todas as combinações")
    print("   • max_tentativas = quantas vezes tentar encontrar UMA combinação")
    print("   • Este gera REALMENTE todas as combinações existentes")
    print()
    
    gerador = GeradorExaustivo()
    
    print("📋 OPÇÕES DISPONÍVEIS:")
    print("1️⃣ Gerar TODAS as 3.268.760 combinações")
    print("2️⃣ Verificar combinação específica")
    print("3️⃣ Comparar arquivo existente com conjunto completo")
    print("0️⃣ Sair")
    print()
    
    opcao = input("Escolha uma opção: ").strip()
    
    if opcao == "1":
        arquivo_gerado = gerador.gerar_todas_combinacoes_15()
        if arquivo_gerado:
            print(f"\n🎉 SUCESSO! Arquivo gerado: {arquivo_gerado}")
            print("✅ Agora você tem TODAS as combinações matemáticas possíveis!")
    
    elif opcao == "2":
        print("\n🔍 Digite a combinação para verificar (15 números):")
        entrada = input("Combinação (formato: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15): ").strip()
        
        try:
            numeros = [int(x.strip()) for x in entrada.split(',')]
            if len(numeros) == 15:
                existe, posicao = gerador.verificar_combinacao_especifica(numeros)
                if existe:
                    print(f"✅ Combinação existe na posição {posicao:,}")
                else:
                    print(f"❌ Combinação inválida ou não encontrada")
            else:
                print(f"❌ Digite exatamente 15 números")
        except:
            print(f"❌ Formato inválido")
    
    elif opcao == "3":
        arquivo = input("\n📁 Digite o caminho do arquivo para verificar: ").strip()
        if arquivo:
            completo = gerador.comparar_com_arquivo_existente(arquivo)
            if completo:
                print("✅ Arquivo está completo!")
            else:
                print("❌ Arquivo está incompleto!")
    
    elif opcao == "0":
        print("👋 Até logo!")
    
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()