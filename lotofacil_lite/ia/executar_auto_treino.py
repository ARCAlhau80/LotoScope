#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 SISTEMA DE AUTO-TREINO CONTÍNUO - EXECUÇÃO PRINCIPAL
=======================================================
Sistema completo de IA autônoma para Lotofácil
Integra todos os componentes desenvolvidos
"""

import os
import sys
import json
import time
from datetime import datetime

def exibir_menu_principal():
    """Exibe menu principal do sistema"""
    print("\n" + "="*60)
    print("    SISTEMA DE AUTO-TREINO CONTINUO - LOTOFACIL")
    print("="*60)
    print("1. Executar Auto-Treino Contínuo (Produção)")
    print("2. Demonstração Simplificada")
    print("3. Configurar Sistema")
    print("4. Ver Status do Sistema")
    print("5. Testar Componentes")
    print("0. Sair")
    print("-"*60)

def executar_auto_treino_producao():
    """Executa sistema completo de produção"""
    try:
        # Verifica se arquivo principal existe
        if os.path.exists('sistema_auto_treino.py'):
            print("\n[INICIANDO] Sistema de Auto-Treino de Produção...")
            print("Carregando sistema completo...")
            
            # Importa e executa sistema principal
            from sistema_auto_treino import SistemaAutoTreinoContinuo
            
            # Carrega configuração
            if os.path.exists('config_auto_treino.json'):
                with open('config_auto_treino.json', 'r') as f:
                    config = json.load(f)
                print(f"[OK] Configuração carregada: {len(config)} parâmetros")
            else:
                print("[AVISO] Usando configuração padrão")
                config = {}
            
            # Inicia sistema
            sistema = SistemaAutoTreinoContinuo()
            print("[INICIADO] Sistema autônomo em execução...")
            print("Pressione Ctrl+C para parar")
            
            sistema.executar_continuamente()
            
        else:
            print("\n[ERRO] Sistema principal não encontrado!")
            print("Execute: criar_sistema_auto_treino() primeiro")
            
    except KeyboardInterrupt:
        print("\n[PARADA] Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n[ERRO] Falha na execução: {e}")

def executar_demonstracao():
    """Executa demonstração simplificada"""
    try:
        from demo_auto_treino import DemoAutoTreino
        
        print("\n[DEMO] Iniciando demonstração...")
        demo = DemoAutoTreino()
        
        print("Escolha o tipo de demonstração:")
        print("1. Rápida (3 sessões)")
        print("2. Completa (10 sessões)")
        print("3. Interativa")
        
        opcao = input("Opção: ").strip()
        
        if opcao == "1":
            demo.executar_demo_continua(3)
        elif opcao == "2":
            demo.executar_demo_continua(10)
        elif opcao == "3":
            # Demo interativa
            while True:
                print("\n--- CONTROLES DA DEMO ---")
                print("1. Executar sessão")
                print("2. Ver evolução")
                print("3. Auto-implementar")
                print("0. Voltar")
                
                sub_opcao = input("Comando: ").strip()
                
                if sub_opcao == "1":
                    demo.executar_sessao_treino()
                elif sub_opcao == "2":
                    demo.exibir_evolucao()
                elif sub_opcao == "3":
                    demo.auto_implementar_melhoria()
                elif sub_opcao == "0":
                    break
        else:
            print("Opção inválida")
            
    except ImportError:
        print("\n[ERRO] Demo não disponível")
    except Exception as e:
        print(f"\n[ERRO] Falha na demo: {e}")

def configurar_sistema():
    """Configura parâmetros do sistema"""
    print("\n[CONFIG] Configuração do Sistema")
    print("-"*40)
    
    config_padrao = {
        "intervalo_sessoes": 300,
        "max_sessoes_dia": 48,
        "limite_iteracoes": 10000,
        "auto_implementacao": True,
        "salvar_conhecimento": True,
        "backup_automatico": True,
        "log_detalhado": True
    }
    
    # Carrega configuração existente
    if os.path.exists('config_auto_treino.json'):
        with open('config_auto_treino.json', 'r') as f:
            config = json.load(f)
        print("[OK] Configuração atual carregada")
    else:
        config = config_padrao
        print("[NOVO] Usando configuração padrão")
    
    # Mostra configuração atual
    print("\nConfiguração atual:")
    for chave, valor in config.items():
        print(f"  {chave}: {valor}")
    
    # Permite edição
    print("\nDeseja alterar algum parâmetro? (s/n)")
    if input().lower() == 's':
        for chave in config:
            novo_valor = input(f"{chave} [{config[chave]}]: ").strip()
            if novo_valor:
                # Tenta converter para tipo apropriado
                try:
                    if isinstance(config[chave], bool):
                        config[chave] = novo_valor.lower() in ('true', 's', 'sim', '1')
                    elif isinstance(config[chave], int):
                        config[chave] = int(novo_valor)
                    else:
                        config[chave] = novo_valor
                except ValueError:
                    print(f"[ERRO] Valor inválido para {chave}")
    
    # Salva configuração
    with open('config_auto_treino.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n[SALVO] Configuração atualizada")

def ver_status_sistema():
    """Exibe status atual do sistema"""
    print("\n[STATUS] Estado do Sistema")
    print("-"*40)
    
    # Verifica arquivos principais
    arquivos_sistema = [
        'sistema_auto_treino.py',
        'agente_completo.py', 
        'demo_auto_treino.py',
        'config_auto_treino.json'
    ]
    
    print("Componentes do sistema:")
    for arquivo in arquivos_sistema:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            print(f"  [OK] {arquivo} ({tamanho:,} bytes)")
        else:
            print(f"  [--] {arquivo} (não encontrado)")
    
    # Verifica conhecimento acumulado
    arquivos_conhecimento = [f for f in os.listdir('.') if f.startswith('conhecimento_')]
    if arquivos_conhecimento:
        print(f"\nConhecimento acumulado: {len(arquivos_conhecimento)} arquivos")
        for arquivo in sorted(arquivos_conhecimento)[-3:]:  # Últimos 3
            print(f"  {arquivo}")
    
    # Verifica estratégias auto-geradas
    arquivos_estrategias = [f for f in os.listdir('.') if f.startswith('estrategia_auto_')]
    if arquivos_estrategias:
        print(f"\nEstratégias auto-geradas: {len(arquivos_estrategias)} arquivos")
    
    # Mostra configuração
    if os.path.exists('config_auto_treino.json'):
        with open('config_auto_treino.json', 'r') as f:
            config = json.load(f)
        print(f"\nConfiguração ativa: {len(config)} parâmetros")
        print(f"  Auto-implementação: {config.get('auto_implementacao', 'N/A')}")
        print(f"  Sessões por dia: {config.get('max_sessoes_dia', 'N/A')}")

def testar_componentes():
    """Testa componentes do sistema"""
    print("\n[TESTE] Verificação de Componentes")
    print("-"*40)
    
    testes = {
        "Importação demo": lambda: __import__('demo_auto_treino'),
        "Configuração": lambda: json.load(open('config_auto_treino.json')) if os.path.exists('config_auto_treino.json') else {},
        "Sistema principal": lambda: __import__('sistema_auto_treino') if os.path.exists('sistema_auto_treino.py') else None,
        "Agente completo": lambda: __import__('agente_completo') if os.path.exists('agente_completo.py') else None
    }
    
    for nome, teste in testes.items():
        try:
            resultado = teste()
            if resultado is not None:
                print(f"  [OK] {nome}")
            else:
                print(f"  [--] {nome} (não disponível)")
        except Exception as e:
            print(f"  [ERRO] {nome}: {str(e)[:50]}")

def main():
    """Função principal"""
    try:
        while True:
            exibir_menu_principal()
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                executar_auto_treino_producao()
            elif opcao == "2":
                executar_demonstracao()
            elif opcao == "3":
                configurar_sistema()
            elif opcao == "4":
                ver_status_sistema()
            elif opcao == "5":
                testar_componentes()
            elif opcao == "0":
                print("\n[SAINDO] Sistema finalizado")
                break
            else:
                print("\n[ERRO] Opção inválida")
            
            # Pausa entre operações
            input("\nPressione Enter para continuar...")
    
    except KeyboardInterrupt:
        print("\n\n[PARADA] Sistema interrompido")
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] {e}")

if __name__ == "__main__":
    main()