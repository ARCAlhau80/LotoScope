"""
SISTEMA COMPLETO LOTOFÁCIL - ANÁLISE + GERAÇÃO INTELIGENTE
===========================================================
Sistema integrado: Análise Acadêmica + Geração de Combinações Inteligentes
"""

import os
import subprocess
import sys
from datetime import datetime

class SistemaCompletoLotofacil:
    """Sistema completo integrado"""
    
    def __init__(self):
        self.opcoes = {
            '1': '🔬 Executar Análise Acadêmica Completa',
            '2': '🧠 Gerar Combinações Inteligentes',
            '3': '🚀 Pipeline Completo (Análise + Geração)',
            '4': '📊 Ver Relatórios e Status',
            '5': '🎯 Geração Personalizada Avançada',
            '6': '📈 Análise da Situação Atual',
            '0': '🚪 Sair'
        }
        
    def mostrar_banner(self):
        """Banner do sistema"""
        print("\n" + "=" * 70)
        print("    🎯 SISTEMA COMPLETO LOTOFÁCIL - ANÁLISE + GERAÇÃO IA")
        print("=" * 70)
        print("  🔬 Análise Científica de 3.524+ concursos")
        print("  🧠 Geração Inteligente baseada em IA")
        print("  📊 6 Metodologias Acadêmicas + 4 Estratégias de Geração")
        print("  🎯 Sistema que usa aprendizado para otimizar combinações")
        print("-" * 70)
        
    def mostrar_menu(self):
        """Menu principal"""
        for chave, descricao in self.opcoes.items():
            if chave == '0':
                print(f"\n{chave}. {descricao}")
            else:
                print(f"{chave}. {descricao}")
        print("\n" + "-" * 70)
        
    def executar_analise_academica(self):
        """Executa análise acadêmica"""
        print("\n🔬 EXECUTANDO ANÁLISE ACADÊMICA COMPLETA...")
        print("=" * 55)
        print("📊 Metodologias científicas:")
        print("   1. Análise de Frequências (Chi-quadrado)")
        print("   2. Correlações Temporais e Tendências")
        print("   3. Sazonalidade com FFT")
        print("   4. Detecção de Anomalias (Isolation Forest)")
        print("   5. Clustering de Padrões (K-means)")
        print("   6. Entropia e Complexidade")
        print("-" * 55)
        
        try:
            resultado = subprocess.run([
                sys.executable, 
                'analisador_academico_limpo.py'
            ], capture_output=False, text=True)
            
            if resultado.returncode == 0:
                print("\n✅ ANÁLISE ACADÊMICA CONCLUÍDA!")
                return True
            else:
                print("\n❌ ERRO na análise acadêmica")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
    
    def gerar_combinacoes_inteligentes(self):
        """Gera combinações inteligentes"""
        print("\n🧠 GERAÇÃO DE COMBINAÇÕES INTELIGENTES...")
        print("=" * 50)
        print("🎯 Estratégias disponíveis:")
        print("   • Equilibrada (baseada em tendências)")
        print("   • Por Tendências (números quentes/frios)")
        print("   • Por Faixas (distribuição por intervalos)")
        print("   • Anomalia Positiva (padrões diferenciados)")
        print("-" * 50)
        
        try:
            # Perguntar quantidade
            while True:
                try:
                    qtd = input("\n📊 Quantas combinações gerar? (5-20, padrão: 10): ").strip()
                    if not qtd:
                        qtd = 10
                    else:
                        qtd = int(qtd)
                    
                    if 5 <= qtd <= 20:
                        break
                    else:
                        print("⚠️ Digite um número entre 5 e 20")
                        
                except ValueError:
                    print("⚠️ Digite um número válido")
            
            # Executar gerador
            resultado = subprocess.run([
                sys.executable, '-c',
                f"from gerador_inteligente import GeradorInteligente; "
                f"g = GeradorInteligente(); "
                f"g.executar_geracao_completa({qtd})"
            ], capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print(f"\n✅ {qtd} COMBINAÇÕES GERADAS COM SUCESSO!")
                
                # Mostrar resumo do output
                linhas = resultado.stdout.split('\n')
                for linha in linhas:
                    if any(palavra in linha for palavra in ['✅', '📊', '🎯', '💾']):
                        print(f"   {linha}")
                
                return True
            else:
                print(f"\n❌ ERRO na geração: {resultado.stderr}")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
    
    def executar_pipeline_completo(self):
        """Pipeline completo: análise + geração"""
        print("\n🚀 EXECUTANDO PIPELINE COMPLETO...")
        print("=" * 45)
        print("📋 Etapas:")
        print("   1. Análise Acadêmica (3.524+ concursos)")
        print("   2. Geração Inteligente (baseada na análise)")
        print("   3. Relatórios Integrados")
        print("-" * 45)
        
        # Etapa 1: Análise
        print("\n🔬 ETAPA 1/2: Análise Acadêmica")
        if not self.executar_analise_academica():
            print("❌ Pipeline interrompido - falha na análise")
            return False
        
        print("\n⏳ Aguardando 3 segundos...")
        import time
        time.sleep(3)
        
        # Etapa 2: Geração
        print("\n🧠 ETAPA 2/2: Geração Inteligente")
        print("📊 Usando padrão de 10 combinações otimizadas...")
        
        try:
            resultado = subprocess.run([
                sys.executable, '-c',
                "from gerador_inteligente import GeradorInteligente; "
                "g = GeradorInteligente(); "
                "g.executar_geracao_completa(10)"
            ], capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print("\n✅ GERAÇÃO CONCLUÍDA!")
                
                # Extrair nome do arquivo gerado
                linhas = resultado.stdout.split('\n')
                arquivo_gerado = None
                for linha in linhas:
                    if 'combinacoes_inteligentes_' in linha and '.txt' in linha:
                        arquivo_gerado = linha.split('💾 Arquivo: ')[-1].strip()
                        break
                
                print(f"\n🎉 PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
                print(f"📄 Análise: relatorio_analise_academica_*.json")
                print(f"🎯 Combinações: {arquivo_gerado if arquivo_gerado else 'combinacoes_inteligentes_*.txt'}")
                return True
            else:
                print(f"\n❌ ERRO na geração: {resultado.stderr}")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
    
    def ver_relatorios_status(self):
        """Mostra relatórios e status"""
        print("\n📊 RELATÓRIOS E STATUS DO SISTEMA")
        print("=" * 45)
        
        import glob
        import json
        
        # Verificar arquivos de análise
        relatorios_json = glob.glob("relatorio_analise_*.json")
        print(f"📄 Relatórios de Análise: {len(relatorios_json)} arquivo(s)")
        
        if relatorios_json:
            arquivo_mais_recente = max(relatorios_json, key=os.path.getctime)
            print(f"   📊 Mais recente: {arquivo_mais_recente}")
            
            try:
                with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                metadata = dados.get('metadata', {})
                resumo = dados.get('resumo_executivo', {})
                
                print(f"   📅 Data: {metadata.get('data_analise', 'N/A')[:19]}")
                print(f"   📈 Registros: {metadata.get('total_registros', 'N/A')}")
                print(f"   🔬 Análises: {resumo.get('total_analises', 'N/A')}")
                
            except Exception as e:
                print(f"   ❌ Erro ao ler: {e}")
        
        # Verificar combinações geradas
        combinacoes = glob.glob("combinacoes_inteligentes_*.txt")
        print(f"\n🎯 Combinações Geradas: {len(combinacoes)} arquivo(s)")
        
        if combinacoes:
            arquivo_mais_recente = max(combinacoes, key=os.path.getctime)
            print(f"   🧠 Mais recente: {arquivo_mais_recente}")
            
            # Ler primeiras linhas
            try:
                with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                
                for linha in linhas[:10]:
                    if 'Total:' in linha or 'Último concurso' in linha:
                        print(f"   {linha.strip()}")
                        
            except Exception as e:
                print(f"   ❌ Erro ao ler: {e}")
        
        # Status do banco
        print(f"\n🗄️ STATUS DO BANCO:")
        try:
            import pyodbc
            conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-K6JPBDS;DATABASE=LOTOFACIL;Trusted_Connection=yes'
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT MAX(Concurso), COUNT(*) FROM RESULTADOS_INT")
            ultimo, total = cursor.fetchone()
            print(f"   📊 Último concurso: {ultimo}")
            print(f"   📈 Total registros: {total}")
            conn.close()
        except Exception as e:
            print(f"   ❌ Erro no banco: {e}")
    
    def geracao_personalizada(self):
        """Geração personalizada avançada"""
        print("\n🎯 GERAÇÃO PERSONALIZADA AVANÇADA")
        print("=" * 40)
        print("⚙️ Configurações disponíveis:")
        print("   1. Quantidade de combinações")
        print("   2. Estratégia preferencial")
        print("   3. Foco em números específicos")
        print("-" * 40)
        
        try:
            # Configurações
            print("\n📊 CONFIGURAÇÕES:")
            
            # Quantidade
            while True:
                try:
                    qtd = input("   Quantidade (5-50): ").strip()
                    qtd = int(qtd) if qtd else 15
                    if 5 <= qtd <= 50:
                        break
                    print("   ⚠️ Entre 5 e 50")
                except ValueError:
                    print("   ⚠️ Número válido")
            
            # Estratégia
            print("\n   Estratégias:")
            print("   1. Equilibrada (padrão)")
            print("   2. Conservadora (números frequentes)")
            print("   3. Agressiva (busca anomalias)")
            print("   4. Mista (todas as estratégias)")
            
            estrategia = input("   Escolha (1-4, padrão: 4): ").strip()
            estrategia = int(estrategia) if estrategia and estrategia.isdigit() else 4
            
            print(f"\n🚀 Gerando {qtd} combinações com estratégia {estrategia}...")
            
            # Executar com configurações
            resultado = subprocess.run([
                sys.executable, '-c',
                f"from gerador_inteligente import GeradorInteligente; "
                f"g = GeradorInteligente(); "
                f"g.executar_geracao_completa({qtd})"
            ], capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print(f"\n✅ GERAÇÃO PERSONALIZADA CONCLUÍDA!")
                return True
            else:
                print(f"\n❌ ERRO: {resultado.stderr}")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
    
    def analisar_situacao_atual(self):
        """Análise da situação atual detalhada"""
        print("\n📈 ANÁLISE DA SITUAÇÃO ATUAL")
        print("=" * 35)
        
        try:
            # Executar análise pontual
            resultado = subprocess.run([
                sys.executable, '-c',
                "from gerador_inteligente import GeradorInteligente; "
                "g = GeradorInteligente(); "
                "g.carregar_dados_historicos(); "
                "g.analisar_situacao_atual()"
            ], capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print("📊 SITUAÇÃO ATUAL DOS SORTEIOS:")
                linhas = resultado.stdout.split('\n')
                for linha in linhas:
                    if any(palavra in linha for palavra in ['últimos', 'médios', 'quentes', 'tendência']):
                        print(f"   {linha}")
                
                print(f"\n💡 RECOMENDAÇÕES:")
                print(f"   • Use o pipeline completo para análise otimizada")
                print(f"   • Geração inteligente já considera estes padrões")
                print(f"   • Combine com análises acadêmicas para melhor precisão")
                
                return True
            else:
                print(f"❌ Erro na análise: {resultado.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def executar(self):
        """Loop principal"""
        while True:
            try:
                self.mostrar_banner()
                self.mostrar_menu()
                
                opcao = input("🎯 Escolha uma opção: ").strip()
                
                if opcao == '0':
                    print("\n👋 Encerrando sistema...")
                    break
                elif opcao == '1':
                    self.executar_analise_academica()
                elif opcao == '2':
                    self.gerar_combinacoes_inteligentes()
                elif opcao == '3':
                    self.executar_pipeline_completo()
                elif opcao == '4':
                    self.ver_relatorios_status()
                elif opcao == '5':
                    self.geracao_personalizada()
                elif opcao == '6':
                    self.analisar_situacao_atual()
                else:
                    print("❌ Opção inválida!")
                
                if opcao in ['1', '2', '3', '4', '5', '6']:
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Sistema encerrado pelo usuário")
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
                input("⏸️ Pressione ENTER para continuar...")

def main():
    """Função principal"""
    print("🚀 Inicializando Sistema Completo Lotofácil...")
    
    sistema = SistemaCompletoLotofacil()
    sistema.executar()
    
    print("✅ Sistema encerrado com sucesso.")

if __name__ == "__main__":
    main()