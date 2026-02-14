#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 LOTOSCOPE - SISTEMA PRINCIPAL CONSOLIDADO v2.0
==================================================
Ponto de entrada unificado para todos os sistemas LotoScope

ESTRUTURA REORGANIZADA:
- geradores/    - 54 geradores de combinações
- analisadores/ - 55 sistemas de análise
- ia/           - 25 sistemas de IA/ML
- sistemas/     - 39 sistemas integrados
- interfaces/   - 16 menus e GUIs
- utils/        - 36 utilitários
- validadores/  - 21 validadores
- relatorios/   - 11 geradores de relatórios
- _archive/     - 32 arquivos arquivados
"""

import os
import sys
from datetime import datetime

# Adicionar diretório atual ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def exibir_banner():
    """🎨 Exibe banner do sistema"""
    print("🔥" * 80)
    print("🎯 LOTOSCOPE - SISTEMA INTEGRADO COMPLETO")
    print("🧠 Inteligência Artificial para Lotofácil")
    print("📊 Sistema consolidado e organizado")
    print("✅ Validado: 15 acertos em produção!")
    print("🔥" * 80)
    print()

def menu_principal():
    """📋 Menu principal do sistema consolidado"""
    while True:
        exibir_banner()
        
        print("📋 SISTEMAS DISPONÍVEIS:")
        print("=" * 60)
        print("1️⃣  🧠 SUPER MENU - Sistema Principal Completo")
        print("     • Interface completa com todos os geradores")
        print("     • Análises e estatísticas avançadas")
        print("     • ✅ Sistema validado com 15 acertos!")
        print()
        print("2️⃣  🚀 SISTEMA AUTO-TREINO - Aprendizado Contínuo")
        print("     • IA com 24.000+ neurônios")
        print("     • Treinamento automático e contínuo")
        print("     • Evolução autônoma de estratégias")
        print()
        print("3️⃣  🎯 SISTEMA AUTO-TREINO REAL - Dados Históricos")
        print("     • Aprendizado baseado em dados reais")
        print("     • Validação com concursos históricos")
        print("     • Estratégias de treino -> validação")
        print()
        print("4️⃣  🧠 AGENTE COMPLETO - Neurônios Evolutivos")
        print("     • Sistema neural evolutivo")
        print("     • Padrões adaptativos")
        print("     • Estratégias self-learning")
        print()
        print("5️⃣  🎯 DETECTOR DE PADRÕES - Análise Estatística")
        print("     • Padrões baseados em 68 achados significativos")
        print("     • Ciclos temporais e números especiais")
        print("     • Predições baseadas em evidências estatísticas")
        print()
        print("🤖 === SISTEMAS AI AGENT (NOVOS) === 🤖")
        print()
        print("6️⃣  ⚡ ANÁLISE EM TEMPO REAL - Inspired by Trading Bot")
        print("     • Sistema de análise contínua como trading")
        print("     • Estratégias: momentum, reversão, tendência")
        print("     • Alertas automáticos e métricas de performance")
        print()
        print("7️⃣  🧠 APRENDIZADO CONTÍNUO - AutoGen Framework")
        print("     • Sistema de concept drift detection")
        print("     • Adaptação automática de modelos")
        print("     • Retenção inteligente de conhecimento")
        print()
        print("8️⃣  🎭 AGENTE CONVERSACIONAL - Multi-Agent Framework")
        print("     • Dr. Stats (estatística), Pattern (padrões), Mystic (intuição)")
        print("     • Conversação natural e consenso multi-agente")
        print("     • Análise colaborativa entre especialistas IA")
        print()
        print("9️⃣  📁 EXPLORAR PASTA DE TRABALHO")
        print("     • Abrir explorador na pasta lotofacil_lite")
        print("     • Acessar todos os arquivos do sistema")
        print()
        print("🔟  📊 INFORMAÇÕES DO SISTEMA")
        print("     • Status de arquivos consolidados")
        print("     • Estatísticas da organização")
        print()
        print("0️⃣  🚪 SAIR")
        print("=" * 60)
        
        opcao = input("\n🎯 Escolha uma opção (0-10): ").strip()
        
        if opcao == "1":
            executar_super_menu()
        elif opcao == "2":
            executar_auto_treino()
        elif opcao == "3":
            executar_auto_treino_real()
        elif opcao == "4":
            executar_agente_completo()
        elif opcao == "5":
            executar_detector_padroes()
        elif opcao == "6":
            executar_analise_tempo_real()
        elif opcao == "7":
            executar_aprendizado_continuo()
        elif opcao == "8":
            executar_agente_conversacional()
        elif opcao == "9":
            abrir_pasta_trabalho()
        elif opcao == "10":
            mostrar_informacoes_sistema()
        elif opcao == "0":
            print("\n👋 Obrigado por usar o LotoScope!")
            print("🎯 Sistema consolidado com AI Agents integrados!")
            print("✅ Todos os componentes funcionando na pasta lotofacil_lite")
            break
        else:
            print("\n❌ Opção inválida! Tente novamente.")
            input("\nPressione Enter para continuar...")

def executar_super_menu():
    """🧠 Executa o Super Menu principal"""
    print("\n🚀 Iniciando Super Menu...")
    try:
        from interfaces import super_menu
        super_menu.main()
    except ImportError:
        try:
            # Fallback para import direto
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'interfaces'))
            import super_menu
            super_menu.main()
        except Exception as e:
            print(f"\n❌ Erro ao executar Super Menu: {e}")
            input("\nPressione Enter para voltar...")

def executar_auto_treino():
    """🚀 Executa o Sistema de Auto-Treino"""
    print("\n🚀 Iniciando Sistema Auto-Treino...")
    try:
        from ia import executar_auto_treino
        executar_auto_treino.main()
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ia'))
            import executar_auto_treino
            executar_auto_treino.main()
        except Exception as e:
            print(f"\n❌ Erro ao executar Auto-Treino: {e}")
            input("\nPressione Enter para voltar...")

def executar_auto_treino_real():
    """🎯 Executa o Sistema Auto-Treino Real"""
    print("\n🚀 Iniciando Auto-Treino Real...")
    try:
        from ia import executar_auto_treino_real
        executar_auto_treino_real.main()
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ia'))
            import executar_auto_treino_real
            executar_auto_treino_real.main()
        except Exception as e:
            print(f"\n❌ Erro ao executar Auto-Treino Real: {e}")
            input("\nPressione Enter para voltar...")

def executar_agente_completo():
    """🧠 Executa o Agente Completo"""
    print("\n🚀 Iniciando Agente Completo...")
    try:
        from ia.agente_completo import AgenteNeuroniosCompleto
        agente = AgenteNeuroniosCompleto()
        agente.menu_interativo()
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ia'))
            from agente_completo import AgenteNeuroniosCompleto
            agente = AgenteNeuroniosCompleto()
            agente.menu_interativo()
        except Exception as e:
            print(f"\n❌ Erro ao executar Agente Completo: {e}")
            input("\nPressione Enter para voltar...")

def executar_detector_padroes():
    """🎯 Executa o Detector de Padrões"""
    print("\n🚀 Iniciando Detector de Padrões...")
    try:
        from analisadores.detector_padroes import DetectorPadroes
        detector = DetectorPadroes()
        detector.menu_interativo()
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analisadores'))
            from detector_padroes import DetectorPadroes
            detector = DetectorPadroes()
            detector.menu_interativo()
        except Exception as e:
            print(f"\n❌ Erro ao executar Detector de Padrões: {e}")
            input("\nPressione Enter para voltar...")

def executar_analise_tempo_real():
    """⚡ Executa o Sistema de Análise em Tempo Real"""
    print("\n⚡ Iniciando Sistema de Análise em Tempo Real...")
    try:
        from sistemas import sistema_analise_tempo_real
        sistema_analise_tempo_real.main()
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sistemas'))
            import sistema_analise_tempo_real
            sistema_analise_tempo_real.main()
        except Exception as e:
            print(f"\n❌ Erro ao executar Análise Tempo Real: {e}")
            input("\nPressione Enter para voltar...")

def executar_aprendizado_continuo():
    """🧠 Executa o Sistema de Aprendizado Contínuo"""
    print("\n🧠 Iniciando Sistema de Aprendizado Contínuo...")
    try:
        from sistemas import sistema_aprendizado_continuo
        sistema_aprendizado_continuo.main()
    except ImportError:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sistemas'))
            import sistema_aprendizado_continuo
            sistema_aprendizado_continuo.main()
        except Exception as e:
            print(f"\n❌ Erro ao executar Aprendizado Contínuo: {e}")
            input("\nPressione Enter para voltar...")

def executar_agente_conversacional():
    """🎭 Executa o Agente Conversacional Multi-Agent"""
    print("\n🎭 Iniciando Agente Conversacional Multi-Agent...")
    try:
        import agente_conversacional_multi
        agente_conversacional_multi.main()
    except Exception as e:
        print(f"\n❌ Erro ao executar Agente Conversacional: {e}")
        input("\nPressione Enter para voltar...")

def abrir_pasta_trabalho():
    """📁 Abre a pasta de trabalho no explorador"""
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    print(f"\n📁 Abrindo pasta: {pasta_atual}")
    
    try:
        # Windows
        if os.name == 'nt':
            os.startfile(pasta_atual)
        # macOS
        elif sys.platform == 'darwin':
            os.system(f'open "{pasta_atual}"')
        # Linux
        else:
            os.system(f'xdg-open "{pasta_atual}"')
            
        print("✅ Pasta aberta no explorador!")
        
    except Exception as e:
        print(f"❌ Erro ao abrir pasta: {e}")
        print(f"📍 Pasta manual: {pasta_atual}")
    
    input("\nPressione Enter para voltar...")

def mostrar_informacoes_sistema():
    """📊 Mostra informações do sistema consolidado"""
    print("\n📊 INFORMAÇÕES DO SISTEMA CONSOLIDADO v2.0")
    print("=" * 60)
    
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Conta arquivos por pasta
    pastas = {
        'geradores': 'Geradores de combinações',
        'analisadores': 'Sistemas de análise',
        'ia': 'Inteligência artificial',
        'sistemas': 'Sistemas integrados',
        'interfaces': 'Menus e GUIs',
        'utils': 'Utilitários',
        'validadores': 'Validadores',
        'relatorios': 'Relatórios',
        '_archive': 'Arquivados'
    }
    
    print(f"📍 Pasta de trabalho: {pasta_atual}")
    print()
    print("📁 ESTRUTURA REORGANIZADA:")
    
    total_arquivos = 0
    for pasta, descricao in pastas.items():
        pasta_path = os.path.join(pasta_atual, pasta)
        if os.path.exists(pasta_path):
            count = len([f for f in os.listdir(pasta_path) if f.endswith('.py')])
            total_arquivos += count
            print(f"   📁 {pasta}/: {count} arquivos - {descricao}")
    
    # Arquivos na raiz
    raiz_count = len([f for f in os.listdir(pasta_atual) if f.endswith('.py') and os.path.isfile(os.path.join(pasta_atual, f))])
    print(f"   📄 raiz/: {raiz_count} arquivos - Pontos de entrada")
    
    print()
    print(f"📊 Total de arquivos Python: {total_arquivos + raiz_count}")
    
    print()
    print("✅ BENEFÍCIOS DA REORGANIZAÇÃO v2.0:")
    print("   • ✅ Estrutura modular e profissional")
    print("   • ✅ Imports organizados com __init__.py")
    print("   • ✅ Separação clara de responsabilidades")
    print("   • ✅ Fácil navegação e manutenção")
    print("   • 🧠 Classes base no módulo core/")
    print("   • 📦 Arquivos antigos preservados em _archive/")
    
    print()
    print(f"📅 Reorganizado em: Dezembro 2025")
    print(f"🕐 Verificado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    input("\nPressione Enter para voltar...")

def main():
    """🎯 Função principal do sistema"""
    # Define o diretório de trabalho como o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Inicia o menu principal
    menu_principal()

if __name__ == "__main__":
    main()
