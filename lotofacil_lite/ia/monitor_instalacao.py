#!/usr/bin/env python3
"""
Monitor de Instalação - LotoScope AI
Monitora o progresso da instalação dos modelos
"""

import subprocess
import time
import sys
import os

def check_ollama_path():
    """Encontra o caminho do Ollama"""
    possivel_paths = [
        f"C:\\Users\\{os.environ.get('USERNAME', '')}\\AppData\\Local\\Programs\\Ollama\\ollama.exe",
        "C:\\Program Files\\Ollama\\ollama.exe",
        "ollama"
    ]
    
    for path in possivel_paths:
        try:
            if path != "ollama" and not os.path.exists(path):
                continue
            
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return path
        except:
            continue
    
    return None

def list_models(ollama_path):
    """Lista modelos instalados"""
    try:
        result = subprocess.run([ollama_path, "list"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        return f"Erro: {e}"

def check_server_status():
    """Verifica se servidor está rodando"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔍 MONITOR DE INSTALAÇÃO - LOTOSCOPE AI")
    print("="*50)
    
    # Encontrar Ollama
    ollama_path = check_ollama_path()
    if not ollama_path:
        print("❌ Ollama não encontrado!")
        return
    
    print(f"✅ Ollama encontrado em: {ollama_path}")
    
    # Verificar servidor
    server_running = check_server_status()
    print(f"🖥️  Servidor: {'✅ Rodando' if server_running else '❌ Parado'}")
    
    if not server_running:
        print("\n⚠️  Para iniciar o servidor, execute:")
        print(f"   {ollama_path} serve")
    
    # Listar modelos
    print(f"\n🧠 Modelos instalados:")
    models_output = list_models(ollama_path)
    
    if models_output:
        lines = models_output.strip().split('\n')
        if len(lines) > 1:  # Tem header + modelos
            for line in lines[1:]:  # Pular header
                if line.strip():
                    print(f"   ✅ {line}")
        else:
            print("   ⚠️  Nenhum modelo instalado ainda")
    
    # Verificar modelo específico
    required_models = ["llama3:8b", "llama3:latest"]
    
    print(f"\n🎯 Modelos necessários para LotoScope AI:")
    for model in required_models:
        if models_output and model in models_output:
            print(f"   ✅ {model}")
        else:
            print(f"   ❌ {model} - Execute: {ollama_path} pull {model}")
    
    # Status geral
    models_ok = models_output and any(model in models_output for model in required_models)
    
    print(f"\n📊 STATUS GERAL:")
    print(f"   Ollama:    {'✅' if ollama_path else '❌'}")
    print(f"   Servidor:  {'✅' if server_running else '❌'}")
    print(f"   Modelos:   {'✅' if models_ok else '❌'}")
    
    if ollama_path and server_running and models_ok:
        print("\n🎉 SISTEMA PRONTO!")
        print("   Execute: python lotoscope_ai_chat.py")
        
        # Oferecer teste rápido
        test = input("\n🧪 Fazer teste rápido? (s/n): ").lower().strip()
        if test in ['s', 'sim', 'y', 'yes']:
            print("\n🔄 Testando...")
            try:
                import sys
                sys.path.insert(0, '.')
                from lotoscope_ai_assistant import LotoScopeAIAssistant
                
                assistant = LotoScopeAIAssistant()
                status_ok, status_msg = assistant.check_ollama_status()
                print(f"📊 Status: {status_msg}")
                
                if status_ok:
                    print("🤖 Fazendo pergunta teste...")
                    resposta = assistant.responder("Olá! Você consegue me ajudar?")
                    print(f"💬 Resposta: {resposta[:100]}...")
                    print("✅ TESTE APROVADO!")
                
            except Exception as e:
                print(f"❌ Erro no teste: {e}")
    
    else:
        print("\n⚠️  SISTEMA AINDA NÃO ESTÁ PRONTO")
        if not server_running:
            print(f"1. Inicie o servidor: {ollama_path} serve")
        if not models_ok:
            print(f"2. Instale modelo: {ollama_path} pull llama3:8b")

if __name__ == "__main__":
    main()
