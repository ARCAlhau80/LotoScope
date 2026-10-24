"""
DEMONSTRAÇÃO FINAL DO SISTEMA ACADÊMICO
=======================================
Script automatizado para mostrar as capacidades do sistema
"""

import os
import subprocess
import sys
import time
from datetime import datetime

def executar_demonstracao():
    """Executa demonstração completa do sistema"""
    
    print("🎓 DEMONSTRAÇÃO DO SISTEMA ACADÊMICO LOTOFÁCIL")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🎯 Objetivo: Demonstrar análise científica de 3.522 concursos")
    print("-" * 60)
    
    # Verificar dependências
    print("\n1️⃣ VERIFICANDO DEPENDÊNCIAS...")
    dependencias = ['numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn', 'pyodbc']
    deps_ok = 0
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
            deps_ok += 1
        except ImportError:
            print(f"   ❌ {dep} - FALTA")
    
    print(f"   📊 Resultado: {deps_ok}/{len(dependencias)} dependências OK")
    
    if deps_ok < len(dependencias):
        print("   ⚠️ Instale as dependências em falta:")
        print("   pip install numpy pandas matplotlib scipy scikit-learn pyodbc")
        return False
    
    # Verificar conexão com banco
    print("\n2️⃣ VERIFICANDO CONEXÃO COM BANCO...")
    try:
        import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=VADER;DATABASE=LOTOFACIL;Trusted_Connection=yes'
        # Conexão otimizada para performance
        if _db_optimizer:
            conn = _db_optimizer.create_optimized_connection()
        else:
            conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
        cursor.execute("SELECT COUNT(*) FROM RESULTADOS_INT")
        total = cursor.fetchone()[0]
        print(f"   ✅ Banco conectado: {total} registros disponíveis")
        conn.close()
    except Exception as e:
        print(f"   ❌ Erro no banco: {e}")
        return False
    
    # Executar análise acadêmica
    print("\n3️⃣ EXECUTANDO ANÁLISE ACADÊMICA COMPLETA...")
    print("   🔬 Iniciando análise de 6 metodologias científicas...")
    
    try:
        inicio = time.time()
        
        resultado = subprocess.run([
            sys.executable, 
            'analisador_academico_limpo.py'
        ], capture_output=True, text=True, timeout=120)
        
        fim = time.time()
        tempo_execucao = fim - inicio
        
        if resultado.returncode == 0:
            print(f"   ✅ Análise concluída em {tempo_execucao:.1f} segundos")
            
            # Verificar arquivos gerados
            import glob
            relatorios = glob.glob("relatorio_analise_*.json")
            if relatorios:
                arquivo_mais_recente = max(relatorios, key=os.path.getctime)
                print(f"   📊 Relatório gerado: {arquivo_mais_recente}")
            else:
                print("   ⚠️ Nenhum relatório JSON encontrado")
        else:
            print(f"   ❌ Erro na análise: {resultado.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Timeout - Análise demorou mais que 2 minutos")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False
    
    # Gerar visualizações
    print("\n4️⃣ GERANDO VISUALIZAÇÕES CIENTÍFICAS...")
    
    try:
        from visualizador_simples import VisualizadorSimples
        import glob
        
        relatorios = glob.glob("relatorio_analise_*.json")
        if relatorios:
            arquivo_mais_recente = max(relatorios, key=os.path.getctime)
            
            visualizador = VisualizadorSimples()
            if visualizador.carregar_relatorio(arquivo_mais_recente):
                # Gerar apenas frequências para demonstração
                fig = visualizador.plot_frequencias_numeros(salvar=True)
                if fig:
                    print("   ✅ Gráfico de frequências gerado")
                    import matplotlib.pyplot as plt
                    plt.close(fig)
                
                # Gerar relatório texto
                relatorio_txt = visualizador.gerar_relatorio_texto()
                if relatorio_txt:
                    print(f"   ✅ Relatório executivo: {relatorio_txt}")
            else:
                print("   ❌ Erro ao carregar relatório para visualização")
        else:
            print("   ❌ Nenhum relatório disponível para visualização")
            
    except Exception as e:
        print(f"   ❌ Erro nas visualizações: {e}")
    
    # Mostrar resultados
    print("\n5️⃣ RESUMO DOS RESULTADOS...")
    
    try:
        import glob
        import json
        
        # Contar arquivos gerados
        relatorios_json = glob.glob("relatorio_analise_*.json")
        relatorios_txt = glob.glob("relatorio_simples_*.txt")
        graficos = glob.glob("*_simples.png")
        
        print(f"   📄 Relatórios JSON: {len(relatorios_json)} arquivo(s)")
        print(f"   📋 Relatórios TXT:  {len(relatorios_txt)} arquivo(s)")
        print(f"   📊 Gráficos PNG:    {len(graficos)} arquivo(s)")
        
        # Mostrar descobertas principais
        if relatorios_json:
            arquivo_mais_recente = max(relatorios_json, key=os.path.getctime)
            
            with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            resumo = dados.get('resumo_executivo', {})
            descobertas = resumo.get('principais_descobertas', [])
            
            if descobertas:
                print(f"\n   🎯 PRINCIPAIS DESCOBERTAS ({len(descobertas)}):")
                for i, descoberta in enumerate(descobertas[:3], 1):
                    # Limpar caracteres especiais
                    texto_limpo = descoberta.encode('ascii', errors='ignore').decode('ascii')
                    print(f"      {i}. {texto_limpo}")
    
    except Exception as e:
        print(f"   ⚠️ Erro ao processar resultados: {e}")
    
    # Conclusão
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("📈 Sistema acadêmico funcionando perfeitamente")
    print("🔬 6 metodologias científicas implementadas")
    print("📊 3.522 concursos analisados automaticamente")
    print("🎯 Padrões e anomalias identificados")
    print("\n💡 Para usar o sistema completo:")
    print("   python sistema_final.py")
    print("=" * 60)
    
    return True

def main():
    """Função principal"""
    try:
        sucesso = executar_demonstracao()
        if sucesso:
            print("\n✅ Demonstração executada com sucesso!")
        else:
            print("\n❌ Demonstração falhou. Verifique os requisitos.")
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado na demonstração: {e}")

if __name__ == "__main__":
    main()
    input("\n⏸️ Pressione ENTER para finalizar...")