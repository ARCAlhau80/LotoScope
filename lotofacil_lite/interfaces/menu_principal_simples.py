"""
MENU LOTOFACIL INTEGRADO
========================
Sistema principal com analise academica simplificada
"""

import sys
import os
import subprocess
from datetime import datetime

class MenuLotofacilSimples:
    """
    Menu principal simplificado para o sistema Lotofacil
    Integrado com analise academica sem problemas de encoding
    """
    
    def __init__(self):
        self.opcoes = {
            '1': 'Executar Analise Academica Completa',
            '2': 'Gerar Visualizacoes Simples',
            '3': 'Ver Relatorio de Texto',
            '4': 'Status do Sistema',
            '0': 'Sair'
        }
        
    def mostrar_menu(self):
        """Exibe o menu principal"""
        print("\n" + "=" * 50)
        print("     SISTEMA LOTOFACIL - ANALISE ACADEMICA")
        print("=" * 50)
        
        for chave, descricao in self.opcoes.items():
            if chave == '0':
                print(f"\n{chave}. {descricao}")
            else:
                print(f"{chave}. {descricao}")
        
        print("\n" + "-" * 50)
        
    def executar_analise_academica(self):
        """Executa a analise academica completa"""
        print("\nEXECUTANDO ANALISE ACADEMICA...")
        print("-" * 40)
        
        try:
            # Executar o analisador academico
            resultado = subprocess.run([
                sys.executable, 
                'analisador_academico_padroes.py'
            ], capture_output=True, text=True, encoding='utf-8')
            
            if resultado.returncode == 0:
                print("OK Analise academica executada com sucesso!")
                print("\nRESUMO:")
                # Mostrar apenas as linhas principais do output
                linhas = resultado.stdout.split('\n')
                for linha in linhas:
                    if any(palavra in linha.lower() for palavra in ['ok', 'sucesso', 'gerado', 'analisado']):
                        print(f"  {linha}")
                        
                print(f"\nArquivos gerados: relatorio_analise_academica_*.json")
                return True
            else:
                print(f"ERRO na analise: {resultado.stderr}")
                return False
                
        except Exception as e:
            print(f"ERRO ao executar analise: {e}")
            return False
    
    def executar_visualizacoes(self):
        """Executa o visualizador simples"""
        print("\nGERANDO VISUALIZACOES...")
        print("-" * 30)
        
        try:
            resultado = subprocess.run([
                sys.executable,
                'visualizador_simples.py'
            ], capture_output=True, text=True, encoding='utf-8')
            
            if resultado.returncode == 0:
                print("OK Visualizacoes geradas com sucesso!")
                print("\nArquivos criados:")
                print("  - frequencias_numeros_simples.png")
                print("  - correlacoes_simples.png")
                print("  - relatorio_simples_YYYYMMDD_HHMMSS.txt")
                return True
            else:
                print(f"ERRO nas visualizacoes: {resultado.stderr}")
                return False
                
        except Exception as e:
            print(f"ERRO ao gerar visualizacoes: {e}")
            return False
    
    def ver_relatorio_texto(self):
        """Mostra o relatorio de texto mais recente"""
        import glob
        
        print("\nPROCURANDO RELATORIOS...")
        
        arquivos_relatorio = glob.glob("relatorio_simples_*.txt")
        
        if not arquivos_relatorio:
            print("AVISO Nenhum relatorio encontrado.")
            print("Execute primeiro a opcao 2 (Gerar Visualizacoes)")
            return
        
        # Pegar o mais recente
        arquivo_mais_recente = max(arquivos_relatorio, key=os.path.getctime)
        
        print(f"Abrindo: {arquivo_mais_recente}")
        print("-" * 50)
        
        try:
            with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Mostrar apenas primeiras linhas para nao sobrecarregar
            linhas = conteudo.split('\n')
            for i, linha in enumerate(linhas[:30]):  # Primeiras 30 linhas
                print(linha)
            
            if len(linhas) > 30:
                print(f"\n... ({len(linhas)-30} linhas restantes)")
                print(f"\nArquivo completo: {arquivo_mais_recente}")
            
        except Exception as e:
            print(f"ERRO ao ler relatorio: {e}")
    
    def mostrar_status(self):
        """Mostra status do sistema"""
        print("\nSTATUS DO SISTEMA")
        print("-" * 25)
        
        # Verificar arquivos principais
        arquivos_sistema = [
            'analisador_academico_padroes.py',
            'visualizador_simples.py'
        ]
        
        print("Modulos do sistema:")
        for arquivo in arquivos_sistema:
            if os.path.exists(arquivo):
                print(f"  OK {arquivo}")
            else:
                print(f"  FALTA {arquivo}")
        
        # Verificar relatorios gerados
        import glob
        
        relatorios_json = glob.glob("relatorio_analise_*.json")
        relatorios_txt = glob.glob("relatorio_simples_*.txt")
        graficos_png = glob.glob("*_simples.png")
        
        print(f"\nArquivos gerados:")
        print(f"  Relatorios JSON: {len(relatorios_json)}")
        print(f"  Relatorios TXT:  {len(relatorios_txt)}")
        print(f"  Graficos PNG:    {len(graficos_png)}")
        
        if relatorios_json:
            print(f"  Ultimo JSON: {max(relatorios_json, key=os.path.getctime)}")
    
    def executar(self):
        """Loop principal do menu"""
        while True:
            try:
                self.mostrar_menu()
                
                opcao = input("Escolha uma opcao: ").strip()
                
                if opcao == '0':
                    print("\nSaindo do sistema...")
                    break
                elif opcao == '1':
                    self.executar_analise_academica()
                elif opcao == '2':
                    self.executar_visualizacoes()
                elif opcao == '3':
                    self.ver_relatorio_texto()
                elif opcao == '4':
                    self.mostrar_status()
                else:
                    print("ERRO Opcao invalida! Tente novamente.")
                
                if opcao in ['1', '2', '3', '4']:
                    input("\nPressione ENTER para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\nSaindo do sistema...")
                break
            except Exception as e:
                print(f"\nERRO inesperado: {e}")
                input("Pressione ENTER para continuar...")

def main():
    """Funcao principal"""
    print("Iniciando Sistema Lotofacil...")
    
    menu = MenuLotofacilSimples()
    menu.executar()
    
    print("Sistema encerrado.")

if __name__ == "__main__":
    main()