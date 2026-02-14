#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 EXECUTOR DO SISTEMA AUTO-TREINO REAL
=======================================
"""

from sistema_auto_treino_real import SistemaAutoTreinoReal

def main():
    print("🎯 SISTEMA DE AUTO-TREINO REAL - LOTOFACIL")
    print("=" * 50)
    print("Usando dados REAIS da tabela resultados_int")
    print("Aprendizado inteligente: treino -> validação")
    print()
    
    sistema = SistemaAutoTreinoReal()
    
    # Testa conexão e dados
    print("🔍 Verificando conexão e dados...")
    concursos = sistema.buscar_concursos_disponiveis()
    
    if not concursos:
        print("❌ Erro: Não foi possível conectar ou buscar concursos!")
        return
    
    print(f"✅ Conectado! Encontrados {len(concursos)} concursos")
    print(f"   Range: {min(concursos)} a {max(concursos)}")
    print()
    
    # Testa um exemplo
    print("🧪 Testando um ciclo de exemplo...")
    resultado = sistema.executar_ciclo_aprendizado()
    
    if 'erro' in resultado:
        print(f"❌ Erro: {resultado['erro']}")
        return
    
    print("✅ Teste bem-sucedido!")
    print(f"   Treino: Concurso {resultado['concurso_treino']}")
    print(f"   Validação: Concurso {resultado['concurso_validacao']}")
    print(f"   Combinação gerada: {resultado['combinacao_gerada']}")
    print(f"   Resultado oficial: {resultado['resultado_oficial']}")
    print(f"   Acertos: {resultado['acertos']}/15")
    print()
    
    # Menu de opções
    while True:
        print("OPÇÕES:")
        print("1. Executar sessão de 10 ciclos")
        print("2. Executar sessão de 50 ciclos")
        print("3. Executar até conseguir 14+ acertos")
        print("4. Ver relatório atual")
        print("5. Executar ciclo único")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n🚀 Executando 10 ciclos...")
            sistema.executar_sessao_aprendizado(10)
            
        elif opcao == "2":
            print("\n🚀 Executando 50 ciclos...")
            sistema.executar_sessao_aprendizado(50)
            
        elif opcao == "3":
            print("\n🎯 Executando até conseguir 14+ acertos...")
            max_tentativas = 100
            
            for tentativa in range(max_tentativas):
                resultado = sistema.executar_ciclo_aprendizado()
                
                if resultado.get('acertos', 0) >= 14:
                    print(f"🏆 SUCESSO! {resultado['acertos']} acertos na tentativa {tentativa + 1}")
                    print(f"   Combinação: {resultado['combinacao_gerada']}")
                    print(f"   Resultado oficial: {resultado['resultado_oficial']}")
                    break
                
                if (tentativa + 1) % 10 == 0:
                    print(f"   Tentativa {tentativa + 1}: {resultado.get('acertos', 0)} acertos")
            else:
                print(f"Não conseguiu 14+ acertos em {max_tentativas} tentativas")
            
            sistema._salvar_conhecimento()
            
        elif opcao == "4":
            print("\n📊 RELATÓRIO ATUAL:")
            sistema.gerar_relatorio_aprendizado()
            
        elif opcao == "5":
            print("\n🧪 Executando ciclo único...")
            resultado = sistema.executar_ciclo_aprendizado()
            print(f"Resultado: {resultado.get('acertos', 0)} acertos")
            
        elif opcao == "0":
            print("👋 Saindo...")
            break
            
        else:
            print("❌ Opção inválida!")
        
        print()

if __name__ == "__main__":
    main()