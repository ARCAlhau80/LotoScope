"""
MENU FINAL INTEGRADO
====================
Sistema completo funcional para análise acadêmica da Lotofácil
"""

import os
import subprocess
import sys
from datetime import datetime

class MenuLotofacilFinal:
    """Menu principal completo e funcional"""
    
    def __init__(self):
        self.opcoes = {
            '1': 'Executar Análise Acadêmica Completa',
            '2': 'Gerar Visualizações dos Resultados',
            '3': 'Ver Relatório Executivo',
            '4': 'Status do Sistema',
            '5': 'Executar Pipeline Completo',
            '0': 'Sair'
        }
        
    def mostrar_banner(self):
        """Mostra banner do sistema"""
        print("\n" + "=" * 60)
        print("    SISTEMA LOTOFÁCIL - ANÁLISE ACADÊMICA AVANÇADA")
        print("=" * 60)
        print("  Análise estatística científica de padrões da Lotofácil")
        print("  • 6 metodologias acadêmicas implementadas")
        print("  • 3.522 concursos analisados")
        print("  • Visualizações científicas automáticas")
        print("-" * 60)
        
    def mostrar_menu(self):
        """Exibe o menu de opções"""
        for chave, descricao in self.opcoes.items():
            if chave == '0':
                print(f"\n{chave}. {descricao}")
            else:
                print(f"{chave}. {descricao}")
        print("\n" + "-" * 60)
        
    def executar_analise_completa(self):
        """Executa análise acadêmica completa"""
        print("\n🔬 EXECUTANDO ANÁLISE ACADÊMICA COMPLETA...")
        print("=" * 50)
        print("Metodologias implementadas:")
        print("  1. Análise de Frequências e Distribuições")
        print("  2. Correlações Temporais e Tendências")
        print("  3. Análise de Sazonalidade (FFT)")
        print("  4. Detecção de Anomalias (Isolation Forest)")
        print("  5. Clustering de Padrões (K-means)")
        print("  6. Análise de Entropia e Complexidade")
        print("-" * 50)
        
        try:
            resultado = subprocess.run([
                sys.executable, 
                'analisador_academico_limpo.py'
            ], capture_output=False, text=True)
            
            if resultado.returncode == 0:
                print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
                return True
            else:
                print("\n❌ ERRO na análise")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO ao executar análise: {e}")
            return False
    
    def gerar_visualizacoes(self):
        """Gera visualizações automáticas"""
        print("\n📊 GERANDO VISUALIZAÇÕES...")
        print("-" * 30)
        
        try:
            # Importar e executar diretamente para evitar timeout
            import glob
            
            # Verificar se há relatórios
            relatorios = glob.glob("relatorio_analise_*.json")
            if not relatorios:
                print("❌ Nenhum relatório encontrado. Execute primeiro a análise.")
                return False
            
            # Executar visualizador
            from visualizador_simples import VisualizadorSimples
            
            visualizador = VisualizadorSimples()
            arquivo_mais_recente = max(relatorios, key=os.path.getctime)
            
            print(f"📁 Usando relatório: {arquivo_mais_recente}")
            
            if visualizador.carregar_relatorio(arquivo_mais_recente):
                resultado = visualizador.testar_visualizacoes()
                
                if resultado:
                    print("\n✅ VISUALIZAÇÕES GERADAS COM SUCESSO!")
                    print("📁 Arquivos criados:")
                    print("   • frequencias_numeros_simples.png")
                    print("   • correlacoes_simples.png")
                    print("   • relatorio_simples_YYYYMMDD_HHMMSS.txt")
                    return True
                else:
                    print("\n❌ ERRO ao gerar visualizações")
                    return False
            else:
                print("\n❌ ERRO ao carregar relatório")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO nas visualizações: {e}")
            return False
    
    def ver_relatorio_executivo(self):
        """Mostra resumo do relatório mais recente"""
        print("\n📋 RELATÓRIO EXECUTIVO")
        print("=" * 40)
        
        import glob
        import json
        
        # Buscar relatórios JSON
        relatorios_json = glob.glob("relatorio_analise_*.json")
        relatorios_txt = glob.glob("relatorio_simples_*.txt")
        
        if relatorios_json:
            arquivo_json = max(relatorios_json, key=os.path.getctime)
            print(f"📊 Relatório JSON: {arquivo_json}")
            
            try:
                with open(arquivo_json, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                metadata = dados.get('metadata', {})
                resumo = dados.get('resumo_executivo', {})
                
                print(f"📅 Data da análise: {metadata.get('data_analise', 'N/A')}")
                print(f"📈 Total de registros: {metadata.get('total_registros', 'N/A')}")
                print(f"🔬 Análises realizadas: {resumo.get('total_analises', 'N/A')}")
                
                descobertas = resumo.get('principais_descobertas', [])
                if descobertas:
                    print(f"\n🎯 PRINCIPAIS DESCOBERTAS ({len(descobertas)}):")
                    for i, descoberta in enumerate(descobertas[:5], 1):
                        # Limpar emojis da descoberta
                        texto_limpo = descoberta.encode('ascii', errors='ignore').decode('ascii')
                        print(f"   {i}. {texto_limpo}")
                
            except Exception as e:
                print(f"❌ ERRO ao ler relatório JSON: {e}")
        
        if relatorios_txt:
            arquivo_txt = max(relatorios_txt, key=os.path.getctime)
            print(f"\n📄 Relatório TXT: {arquivo_txt}")
        
        if not relatorios_json and not relatorios_txt:
            print("❌ Nenhum relatório encontrado.")
            print("💡 Execute primeiro a análise e visualizações.")
    
    def mostrar_status_sistema(self):
        """Mostra status completo do sistema"""
        print("\n🔧 STATUS DO SISTEMA")
        print("=" * 30)
        
        # Verificar componentes
        componentes = {
            'analisador_academico_limpo.py': 'Analisador Acadêmico',
            'visualizador_simples.py': 'Visualizador',
            'menu_principal_simples.py': 'Menu Principal'
        }
        
        print("📦 COMPONENTES:")
        for arquivo, nome in componentes.items():
            status = "✅ OK" if os.path.exists(arquivo) else "❌ FALTA"
            print(f"   {nome}: {status}")
        
        # Verificar dependências críticas
        print("\n🐍 DEPENDÊNCIAS PYTHON:")
        deps = ['numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn', 'pyodbc']
        for dep in deps:
            try:
                __import__(dep)
                print(f"   {dep}: ✅ OK")
            except ImportError:
                print(f"   {dep}: ❌ FALTA")
        
        # Verificar arquivos gerados
        import glob
        
        relatorios_json = glob.glob("relatorio_analise_*.json")
        relatorios_txt = glob.glob("relatorio_simples_*.txt")
        graficos = glob.glob("*_simples.png")
        
        print(f"\n📁 ARQUIVOS GERADOS:")
        print(f"   Relatórios JSON: {len(relatorios_json)} arquivo(s)")
        print(f"   Relatórios TXT:  {len(relatorios_txt)} arquivo(s)")
        print(f"   Gráficos PNG:    {len(graficos)} arquivo(s)")
        
        # Conexão com banco
        print(f"\n🗄️ BANCO DE DADOS:")
        try:
            import pyodbc
            conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=VADER;DATABASE=LOTOFACIL;Trusted_Connection=yes'
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM RESULTADOS_INT")
            total = cursor.fetchone()[0]
            print(f"   Conexão: ✅ OK ({total} registros)")
            conn.close()
        except:
            print(f"   Conexão: ❌ ERRO")
    
    def executar_pipeline_completo(self):
        """Executa o pipeline completo: análise + visualizações"""
        print("\n🚀 EXECUTANDO PIPELINE COMPLETO...")
        print("=" * 50)
        
        # Passo 1: Análise
        print("PASSO 1/2: Análise Acadêmica")
        if not self.executar_analise_completa():
            print("❌ Pipeline interrompido - falha na análise")
            return False
        
        print("\n⏳ Aguardando 3 segundos...")
        import time
        time.sleep(3)
        
        # Passo 2: Visualizações
        print("\nPASSO 2/2: Visualizações")
        if not self.gerar_visualizacoes():
            print("❌ Pipeline interrompido - falha nas visualizações")
            return False
        
        print("\n🎉 PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
        print("📊 Sistema pronto para análise científica dos dados.")
        return True
    
    def executar(self):
        """Loop principal do menu"""
        while True:
            try:
                self.mostrar_banner()
                self.mostrar_menu()
                
                opcao = input("Escolha uma opção: ").strip()
                
                if opcao == '0':
                    print("\n👋 Encerrando sistema...")
                    break
                elif opcao == '1':
                    self.executar_analise_completa()
                elif opcao == '2':
                    self.gerar_visualizacoes()
                elif opcao == '3':
                    self.ver_relatorio_executivo()
                elif opcao == '4':
                    self.mostrar_status_sistema()
                elif opcao == '5':
                    self.executar_pipeline_completo()
                else:
                    print("❌ Opção inválida! Tente novamente.")
                
                if opcao in ['1', '2', '3', '4', '5']:
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Encerrando sistema...")
                break
            except Exception as e:
                print(f"\n❌ ERRO inesperado: {e}")
                input("⏸️ Pressione ENTER para continuar...")

def main():
    """Função principal"""
    print("🚀 Inicializando Sistema Lotofácil Acadêmico...")
    
    menu = MenuLotofacilFinal()
    menu.executar()
    
    print("✅ Sistema encerrado com sucesso.")

if __name__ == "__main__":
    main()