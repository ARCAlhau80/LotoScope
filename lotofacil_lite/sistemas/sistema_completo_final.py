"""
SISTEMA COMPLETO LOTOFÁCIL ACADÊMICO
====================================
Menu integrado: Análise + Geração Inteligente de Combinações
"""

import os
import subprocess
import sys
from datetime import datetime

class SistemaCompletoLotofacil:
    """Sistema completo: análise acadêmica + geração inteligente"""
    
    def __init__(self):
        self.opcoes = {
            '1': 'Análise Acadêmica Completa (6 metodologias)',
            '2': 'Gerar Combinações Inteligentes',
            '3': 'Pipeline Completo (Análise + Combinações)',
            '4': 'Ver Relatórios Gerados',
            '5': 'Status do Sistema',
            '6': 'Demonstração Automática',
            '0': 'Sair'
        }
        
    def mostrar_banner(self):
        """Banner do sistema"""
        print("\n" + "=" * 70)
        print("🎯 SISTEMA LOTOFÁCIL ACADÊMICO + GERAÇÃO INTELIGENTE")
        print("=" * 70)
        print("🔬 6 Metodologias Científicas + Geração Baseada em IA")
        print("📊 3.522 concursos analisados + Tendências atuais")
        print("🎯 Combinações de alta performance com base científica")
        print("-" * 70)
        
    def mostrar_menu(self):
        """Exibe menu de opções"""
        for chave, descricao in self.opcoes.items():
            if chave == '0':
                print(f"\n{chave}. {descricao}")
            else:
                print(f"{chave}. {descricao}")
        print("\n" + "-" * 70)
        
    def executar_analise_academica(self):
        """Executa análise acadêmica completa"""
        print("\n🔬 EXECUTANDO ANÁLISE ACADÊMICA COMPLETA...")
        print("=" * 60)
        print("📊 Metodologias: Frequências, Correlações, FFT, Anomalias, Clustering, Entropia")
        print("-" * 60)
        
        try:
            resultado = subprocess.run([
                sys.executable, 
                'analisador_academico_limpo.py'
            ], capture_output=False, text=True)
            
            if resultado.returncode == 0:
                print("\n✅ ANÁLISE ACADÊMICA CONCLUÍDA!")
                
                # Verificar arquivo gerado
                import glob
                relatorios = glob.glob("relatorio_analise_*.json")
                if relatorios:
                    arquivo_mais_recente = max(relatorios, key=os.path.getctime)
                    print(f"📄 Relatório: {arquivo_mais_recente}")
                
                return True
            else:
                print("\n❌ ERRO na análise acadêmica")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
    
    def executar_gerador_inteligente(self):
        """Executa gerador de combinações inteligentes"""
        print("\n🧠 GERADOR INTELIGENTE DE COMBINAÇÕES...")
        print("=" * 50)
        print("🎯 Baseado em tendências atuais e análises científicas")
        print("-" * 50)
        
        try:
            # Perguntar quantidade de combinações
            while True:
                try:
                    quantidade = input("\nQuantas combinações gerar? (5-50): ").strip()
                    if not quantidade:
                        quantidade = 10
                    else:
                        quantidade = int(quantidade)
                    
                    if 5 <= quantidade <= 50:
                        break
                    else:
                        print("⚠️ Digite um número entre 5 e 50")
                except ValueError:
                    print("⚠️ Digite um número válido")
            
            print(f"\n🎲 Gerando {quantidade} combinações inteligentes...")
            
            # Executar gerador com entrada simulada
            processo = subprocess.Popen([
                sys.executable, 
                'gerador_inteligente.py'
            ], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True)
            
            stdout, stderr = processo.communicate(input=f"{quantidade}\n")
            
            if processo.returncode == 0:
                print("✅ COMBINAÇÕES GERADAS COM SUCESSO!")
                
                # Extrair nome do arquivo do output
                linhas = stdout.split('\n')
                for linha in linhas:
                    if 'combinacoes_inteligentes_' in linha and '.txt' in linha:
                        arquivo = linha.split(': ')[-1]
                        print(f"💾 Arquivo salvo: {arquivo}")
                        break
                
                # Mostrar algumas combinações
                print("\n🎯 PRIMEIRAS 3 COMBINAÇÕES:")
                print("-" * 30)
                linhas_relevantes = [l for l in linhas if l.strip() and (l.startswith(' ') and '.' in l and '|' in l)]
                for i, linha in enumerate(linhas_relevantes[:3]):
                    print(linha.strip())
                
                return True
            else:
                print(f"\n❌ ERRO no gerador: {stderr}")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
    
    def executar_pipeline_completo(self):
        """Executa pipeline completo: análise + geração"""
        print("\n🚀 PIPELINE COMPLETO: ANÁLISE + GERAÇÃO INTELIGENTE")
        print("=" * 65)
        
        # Passo 1: Análise
        print("ETAPA 1/2: Análise Acadêmica")
        if not self.executar_analise_academica():
            print("❌ Pipeline interrompido - falha na análise")
            return False
        
        print("\n⏳ Aguardando 3 segundos...")
        import time
        time.sleep(3)
        
        # Passo 2: Geração
        print("\nETAPA 2/2: Geração Inteligente")
        if not self.executar_gerador_inteligente():
            print("❌ Pipeline interrompido - falha na geração")
            return False
        
        print("\n🎉 PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
        print("🔬 Análise científica + 🧠 Combinações inteligentes prontas!")
        return True
    
    def ver_relatorios(self):
        """Exibe relatórios gerados"""
        print("\n📋 RELATÓRIOS GERADOS")
        print("=" * 30)
        
        import glob
        
        # Relatórios de análise
        relatorios_analise = glob.glob("relatorio_analise_*.json")
        relatorios_txt = glob.glob("relatorio_simples_*.txt")
        
        # Arquivos de combinações
        combinacoes = glob.glob("combinacoes_inteligentes_*.txt")
        
        # Gráficos
        graficos = glob.glob("*_simples.png")
        
        print(f"🔬 ANÁLISES ACADÊMICAS:")
        print(f"   📊 Relatórios JSON: {len(relatorios_analise)} arquivo(s)")
        print(f"   📋 Relatórios TXT:  {len(relatorios_txt)} arquivo(s)")
        print(f"   📈 Gráficos PNG:    {len(graficos)} arquivo(s)")
        
        print(f"\n🧠 COMBINAÇÕES INTELIGENTES:")
        print(f"   🎯 Arquivos de combinações: {len(combinacoes)} arquivo(s)")
        
        # Mostrar arquivos mais recentes
        if relatorios_analise:
            mais_recente_analise = max(relatorios_analise, key=os.path.getctime)
            print(f"\n📄 Análise mais recente: {mais_recente_analise}")
        
        if combinacoes:
            mais_recente_comb = max(combinacoes, key=os.path.getctime)
            print(f"🎯 Combinações mais recentes: {mais_recente_comb}")
            
            # Mostrar primeiras linhas do arquivo de combinações
            try:
                with open(mais_recente_comb, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                
                print(f"\n📖 PRÉVIA DAS COMBINAÇÕES:")
                print("-" * 35)
                for linha in linhas[:10]:  # Primeiras 10 linhas
                    print(linha.rstrip())
                if len(linhas) > 10:
                    print(f"... e mais {len(linhas)-10} linhas")
                    
            except Exception as e:
                print(f"⚠️ Erro ao ler arquivo: {e}")
    
    def mostrar_status(self):
        """Status completo do sistema"""
        print("\n🔧 STATUS DO SISTEMA COMPLETO")
        print("=" * 40)
        
        # Verificar componentes
        componentes = {
            'analisador_academico_limpo.py': 'Analisador Acadêmico',
            'gerador_inteligente.py': 'Gerador Inteligente',
            'visualizador_simples.py': 'Visualizador',
            'sistema_completo_final.py': 'Sistema Integrado'
        }
        
        print("📦 COMPONENTES PRINCIPAIS:")
        for arquivo, nome in componentes.items():
            if os.path.exists(arquivo):
                tamanho = os.path.getsize(arquivo)
                print(f"   ✅ {nome}: OK ({tamanho:,} bytes)")
            else:
                print(f"   ❌ {nome}: FALTA")
        
        # Dependências
        print("\n🐍 DEPENDÊNCIAS PYTHON:")
        deps = ['numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn', 'pyodbc']
        for dep in deps:
            try:
                __import__(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                print(f"   ❌ {dep}")
        
        # Banco de dados
        print("\n🗄️ BANCO DE DADOS:")
        try:
            import pyodbc
            conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-K6JPBDS;DATABASE=LOTOFACIL;Trusted_Connection=yes'
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT COUNT(*) FROM RESULTADOS_INT")
            total = cursor.fetchone()[0]
            print(f"   ✅ Conexão OK ({total} registros)")
            
            # Último concurso
            cursor.execute("SELECT TOP 1 Concurso, Data_Sorteio FROM RESULTADOS_INT ORDER BY Concurso DESC")
            ultimo = cursor.fetchone()
            print(f"   📊 Último concurso: {ultimo[0]} ({ultimo[1].strftime('%d/%m/%Y')})")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Arquivos gerados
        import glob
        
        analises = len(glob.glob("relatorio_analise_*.json"))
        combinacoes = len(glob.glob("combinacoes_inteligentes_*.txt"))
        graficos = len(glob.glob("*_simples.png"))
        
        print(f"\n📊 ARQUIVOS GERADOS:")
        print(f"   📋 Relatórios de análise: {analises}")
        print(f"   🎯 Arquivos de combinações: {combinacoes}")
        print(f"   📈 Gráficos: {graficos}")
    
    def executar_demo(self):
        """Executa demonstração automática"""
        print("\n🎭 DEMONSTRAÇÃO AUTOMÁTICA")
        print("=" * 35)
        
        try:
            resultado = subprocess.run([
                sys.executable, 
                'demo_sistema_completo.py'
            ], capture_output=False, text=True)
            
            if resultado.returncode == 0:
                print("\n✅ Demonstração executada com sucesso!")
                return True
            else:
                print("\n❌ Erro na demonstração")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
    
    def executar(self):
        """Loop principal do sistema"""
        while True:
            try:
                self.mostrar_banner()
                self.mostrar_menu()
                
                opcao = input("Escolha uma opção: ").strip()
                
                if opcao == '0':
                    print("\n👋 Encerrando sistema completo...")
                    break
                elif opcao == '1':
                    self.executar_analise_academica()
                elif opcao == '2':
                    self.executar_gerador_inteligente()
                elif opcao == '3':
                    self.executar_pipeline_completo()
                elif opcao == '4':
                    self.ver_relatorios()
                elif opcao == '5':
                    self.mostrar_status()
                elif opcao == '6':
                    self.executar_demo()
                else:
                    print("❌ Opção inválida! Tente novamente.")
                
                if opcao in ['1', '2', '3', '4', '5', '6']:
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Sistema encerrado pelo usuário")
                break
            except Exception as e:
                print(f"\n❌ ERRO inesperado: {e}")
                input("⏸️ Pressione ENTER para continuar...")

def main():
    """Função principal"""
    print("🚀 Inicializando Sistema Completo Lotofácil...")
    
    sistema = SistemaCompletoLotofacil()
    sistema.executar()
    
    print("✅ Sistema completo encerrado.")

if __name__ == "__main__":
    main()