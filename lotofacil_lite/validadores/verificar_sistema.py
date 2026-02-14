#!/usr/bin/env python3
"""
Verificador de Sistema - LotoScope AI
Verifica se tudo está configurado corretamente
"""

import subprocess
import sys
import os
from pathlib import Path

def check_ollama():
    """Verifica instalação do Ollama"""
    print("🔍 Verificando Ollama...")
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ Ollama instalado: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Ollama com problema: {result.stderr}")
            return False
    except FileNotFoundError:
        print("   ❌ Ollama não encontrado")
        return False
    except subprocess.TimeoutExpired:
        print("   ❌ Ollama não responde")
        return False

def check_models():
    """Verifica modelos instalados"""
    print("\n🧠 Verificando modelos...")
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = result.stdout
            if 'llama3' in models.lower():
                print("   ✅ Modelo Llama3 encontrado")
                print(f"   📋 Modelos disponíveis:")
                for line in models.split('\n')[1:]:  # Pular cabeçalho
                    if line.strip():
                        print(f"      • {line.strip()}")
                return True
            else:
                print("   ❌ Nenhum modelo Llama3 instalado")
                return False
        else:
            print("   ❌ Erro ao listar modelos")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def check_python_files():
    """Verifica arquivos do assistente"""
    print("\n📁 Verificando arquivos do assistente...")
    
    required_files = [
        'lotoscope_ai_assistant.py',
        'lotoscope_ai_chat.py',
        'setup_llama.py'
    ]
    
    all_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} não encontrado")
            all_ok = False
    
    return all_ok

def test_assistant():
    """Testa o assistente básico"""
    print("\n🧪 Testando assistente...")
    try:
        # Importar módulo do assistente
        sys.path.insert(0, str(Path(__file__).parent))
        from lotoscope_ai_assistant import LotoScopeAIAssistant
        
        assistant = LotoScopeAIAssistant()
        print("   ✅ Módulo do assistente importado")
        
        # Verificar status
        status_ok, status_msg = assistant.check_ollama_status()
        print(f"   📊 Status: {status_msg}")
        
        return status_ok
        
    except ImportError as e:
        print(f"   ❌ Erro ao importar assistente: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

def show_usage_instructions():
    """Mostra instruções de uso"""
    print("\n" + "="*50)
    print("🚀 COMO USAR O LOTOSCOPE AI ASSISTANT")
    print("="*50)
    print()
    print("💬 CHAT INTERATIVO:")
    print("   python lotoscope_ai_chat.py")
    print()
    print("🔧 COMANDOS ESPECIAIS:")
    print("   /analyze arquivo.py    - Analisa código")
    print("   /improve tópico       - Sugere melhorias")
    print("   /patterns megasena    - Pesquisa padrões")
    print("   /status              - Status do sistema")
    print("   /help                - Ajuda completa")
    print()
    print("💡 EXEMPLOS DE PERGUNTAS:")
    print('   "Como otimizar o gerador dinâmico?"')
    print('   "Melhor estratégia para baixa sobreposição?"')
    print('   "Como implementar cache nos algoritmos?"')
    print()
    print("🎯 OU USE O ATALHO:")
    print("   Duplo-clique em: Iniciar_LotoScope_AI.bat")

def main():
    """Verificação principal"""
    print("🔍 VERIFICADOR DE SISTEMA - LOTOSCOPE AI")
    print("="*50)
    
    # Verificações
    ollama_ok = check_ollama()
    models_ok = check_models()
    files_ok = check_python_files()
    assistant_ok = test_assistant()
    
    print("\n" + "="*50)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("="*50)
    
    print(f"🔧 Ollama:           {'✅ OK' if ollama_ok else '❌ PROBLEMA'}")
    print(f"🧠 Modelos:          {'✅ OK' if models_ok else '❌ PROBLEMA'}")
    print(f"📁 Arquivos:         {'✅ OK' if files_ok else '❌ PROBLEMA'}")
    print(f"🤖 Assistente:       {'✅ OK' if assistant_ok else '❌ PROBLEMA'}")
    
    # Status geral
    all_ok = ollama_ok and models_ok and files_ok and assistant_ok
    
    if all_ok:
        print("\n🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
        show_usage_instructions()
        
        # Perguntar se quer iniciar
        start = input("\n🚀 Iniciar o assistente agora? (s/n): ").lower().strip()
        if start in ['s', 'sim', 'y', 'yes']:
            print("🤖 Iniciando assistente...")
            subprocess.run([sys.executable, 'lotoscope_ai_chat.py'])
    
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS!")
        print("\n🔧 SOLUÇÕES:")
        
        if not ollama_ok:
            print("1. Execute: python setup_llama.py")
            print("2. Ou instale manualmente: https://ollama.ai/download")
        
        if not models_ok:
            print("3. Execute: ollama pull llama3:8b")
        
        if not files_ok:
            print("4. Verifique se todos os arquivos foram criados")
        
        if not assistant_ok:
            print("5. Reinicie o terminal e tente novamente")

if __name__ == "__main__":
    main()
