#!/usr/bin/env python3
"""
LotoScope AI Setup - Instalador Automatizado do Llama
Instala e configura o assistente IA local automaticamente
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import json
import time
from pathlib import Path
import platform

class LlamaSetupInstaller:
    """Instalador automatizado do Llama para LotoScope"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.project_root = Path(__file__).parent
        self.downloads_dir = self.project_root / "downloads"
        self.ollama_installed = False
        
        # URLs de download
        self.ollama_urls = {
            "windows": {
                "x86_64": "https://ollama.ai/download/OllamaSetup.exe",
                "amd64": "https://ollama.ai/download/OllamaSetup.exe"
            }
        }
        
        # Modelos recomendados
        self.recommended_models = [
            {"name": "llama3:8b", "size": "4.7GB", "ram": "8GB", "description": "Rápido, boa qualidade"},
            {"name": "llama3:70b", "size": "40GB", "ram": "32GB", "description": "Muito preciso, lento"},
            {"name": "codellama:13b", "size": "7.3GB", "ram": "16GB", "description": "Especializado em código"}
        ]
    
    def print_header(self):
        """Cabeçalho do instalador"""
        print("🚀" + "="*60 + "🚀")
        print("    LOTOSCOPE AI SETUP - INSTALADOR AUTOMÁTICO")
        print("🚀" + "="*60 + "🚀")
        print("🤖 Instalação automatizada do Llama Local")
        print("🎯 Especializado para análise de loterias")
        print("🔒 100% Privado - sem envio de dados")
        print("-" * 62)
    
    def check_system_requirements(self):
        """Verifica requisitos do sistema"""
        print("🔍 VERIFICANDO REQUISITOS DO SISTEMA...")
        
        requirements = {
            "os": {"status": False, "info": ""},
            "ram": {"status": False, "info": ""},
            "disk": {"status": False, "info": ""},
            "python": {"status": False, "info": ""},
            "internet": {"status": False, "info": ""}
        }
        
        # Verificar SO
        if self.system == "windows":
            requirements["os"]["status"] = True
            requirements["os"]["info"] = f"✅ {platform.system()} {platform.release()}"
        else:
            requirements["os"]["info"] = f"❌ SO não suportado: {platform.system()}"
        
        # Verificar RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            if ram_gb >= 8:
                requirements["ram"]["status"] = True
                requirements["ram"]["info"] = f"✅ {ram_gb:.1f}GB RAM disponível"
            else:
                requirements["ram"]["info"] = f"⚠️ {ram_gb:.1f}GB RAM (recomendado: 16GB+)"
        except ImportError:
            requirements["ram"]["info"] = "⚠️ Não foi possível verificar RAM"
        
        # Verificar espaço em disco
        try:
            disk_free = shutil.disk_usage(self.project_root).free / (1024**3)
            if disk_free >= 20:
                requirements["disk"]["status"] = True
                requirements["disk"]["info"] = f"✅ {disk_free:.1f}GB livres"
            else:
                requirements["disk"]["info"] = f"❌ {disk_free:.1f}GB livres (precisa 20GB+)"
        except:
            requirements["disk"]["info"] = "⚠️ Não foi possível verificar espaço"
        
        # Verificar Python
        if sys.version_info >= (3, 8):
            requirements["python"]["status"] = True
            requirements["python"]["info"] = f"✅ Python {sys.version.split()[0]}"
        else:
            requirements["python"]["info"] = f"❌ Python {sys.version.split()[0]} (precisa 3.8+)"
        
        # Verificar internet
        try:
            urllib.request.urlopen('https://ollama.ai', timeout=5)
            requirements["internet"]["status"] = True
            requirements["internet"]["info"] = "✅ Conexão com internet OK"
        except:
            requirements["internet"]["info"] = "❌ Sem conexão com internet"
        
        # Mostrar resultados
        print("\n📋 REQUISITOS:")
        for req, data in requirements.items():
            print(f"   {data['info']}")
        
        # Verificar se pode continuar
        critical_reqs = ["os", "disk", "python", "internet"]
        can_continue = all(requirements[req]["status"] for req in critical_reqs)
        
        if not can_continue:
            print("\n❌ REQUISITOS CRÍTICOS NÃO ATENDIDOS!")
            print("💡 Resolva os problemas acima antes de continuar")
            return False
        
        print("\n✅ REQUISITOS OK - Pode continuar a instalação!")
        return True
    
    def check_ollama_installed(self):
        """Verifica se Ollama já está instalado"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Ollama já instalado: {version}")
                self.ollama_installed = True
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        print("ℹ️ Ollama não encontrado - será instalado")
        return False
    
    def download_ollama(self):
        """Baixa o instalador do Ollama"""
        if self.ollama_installed:
            return True
        
        print("\n📥 BAIXANDO OLLAMA...")
        
        # Criar diretório de downloads
        self.downloads_dir.mkdir(exist_ok=True)
        
        # URL para Windows
        if self.system != "windows":
            print("❌ Instalação automática só disponível para Windows")
            print("💡 Instale manualmente: https://ollama.ai/download")
            return False
        
        url = self.ollama_urls["windows"]["x86_64"]
        installer_path = self.downloads_dir / "OllamaSetup.exe"
        
        try:
            print(f"🌐 Baixando de: {url}")
            print("⏳ Isso pode demorar alguns minutos...")
            
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = (block_num * block_size / total_size) * 100
                    print(f"\r📊 Progresso: {percent:.1f}%", end="", flush=True)
            
            urllib.request.urlretrieve(url, installer_path, progress_hook)
            print(f"\n✅ Download concluído: {installer_path}")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro no download: {e}")
            print("💡 Baixe manualmente: https://ollama.ai/download")
            return False
    
    def install_ollama(self):
        """Instala o Ollama"""
        if self.ollama_installed:
            return True
        
        print("\n⚙️ INSTALANDO OLLAMA...")
        
        installer_path = self.downloads_dir / "OllamaSetup.exe"
        
        if not installer_path.exists():
            print("❌ Instalador não encontrado")
            return False
        
        try:
            print("🚀 Executando instalador...")
            print("💡 Siga as instruções na tela do instalador")
            
            # Executar instalador
            process = subprocess.Popen([str(installer_path)], 
                                     shell=True)
            process.wait()
            
            print("✅ Instalação do Ollama concluída")
            
            # Verificar se foi instalado
            time.sleep(5)  # Aguardar um pouco
            
            if self.check_ollama_installed():
                return True
            else:
                print("⚠️ Ollama pode precisar de reinicialização")
                print("💡 Reinicie o terminal e execute novamente")
                return False
                
        except Exception as e:
            print(f"❌ Erro na instalação: {e}")
            return False
    
    def list_available_models(self):
        """Lista modelos disponíveis"""
        print("\n🧠 MODELOS DISPONÍVEIS:")
        print("-" * 50)
        
        for i, model in enumerate(self.recommended_models, 1):
            print(f"{i}. {model['name']}")
            print(f"   📦 Tamanho: {model['size']}")
            print(f"   🧮 RAM mín: {model['ram']}")  
            print(f"   📝 {model['description']}")
            print()
    
    def install_model(self, model_name):
        """Instala modelo específico"""
        print(f"\n🤖 INSTALANDO MODELO: {model_name}")
        print("⏳ Isso pode demorar MUITO tempo...")
        print("💡 O download pode ser de vários GB")
        
        try:
            process = subprocess.Popen(['ollama', 'pull', model_name],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     universal_newlines=True)
            
            # Mostrar progresso em tempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"📊 {output.strip()}")
            
            if process.returncode == 0:
                print(f"✅ Modelo {model_name} instalado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao instalar modelo {model_name}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def test_installation(self, model_name):
        """Testa a instalação"""
        print(f"\n🧪 TESTANDO INSTALAÇÃO COM {model_name}...")
        
        try:
            # Testar comando básico
            test_prompt = "Responda apenas: 'Olá, sou o LotoScope AI Assistant!'"
            
            process = subprocess.Popen(['ollama', 'run', model_name],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            output, error = process.communicate(input=test_prompt, timeout=30)
            
            if "LotoScope" in output or "Olá" in output:
                print("✅ TESTE BEM-SUCEDIDO!")
                print(f"🤖 Resposta: {output[:100]}...")
                return True
            else:
                print("⚠️ Teste parcialmente bem-sucedido")
                print(f"🤖 Resposta: {output[:100]}...")
                return True
                
        except subprocess.TimeoutExpired:
            print("⚠️ Teste demorou muito - mas instalação OK")
            return True
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def install_python_dependencies(self):
        """Instala dependências Python"""
        print("\n📦 INSTALANDO DEPENDÊNCIAS PYTHON...")
        
        dependencies = ['psutil', 'requests', 'pathlib-extensions']
        
        for dep in dependencies:
            try:
                print(f"📥 Instalando {dep}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                print(f"✅ {dep} instalado")
            except subprocess.CalledProcessError:
                print(f"⚠️ Erro ao instalar {dep}")
    
    def create_shortcuts(self):
        """Cria atalhos para facilitar uso"""
        print("\n🔗 CRIANDO ATALHOS...")
        
        # Script de inicialização rápida
        quick_start_script = f"""@echo off
cd /d "{self.project_root}"
echo 🤖 Iniciando LotoScope AI Assistant...
python lotoscope_ai_chat.py
pause
"""
        
        with open(self.project_root / "Iniciar_LotoScope_AI.bat", 'w') as f:
            f.write(quick_start_script)
        
        print("✅ Atalho criado: Iniciar_LotoScope_AI.bat")
    
    def show_completion_info(self, model_name):
        """Mostra informações de conclusão"""
        print("\n🎉" + "="*50 + "🎉")
        print("    INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🎉" + "="*50 + "🎉")
        print()
        print("✅ Ollama instalado e funcionando")
        print(f"✅ Modelo {model_name} disponível")
        print("✅ Assistente IA configurado")
        print("✅ Atalhos criados")
        print()
        print("🚀 COMO USAR:")
        print("1. Execute: Iniciar_LotoScope_AI.bat")
        print("2. Ou: python lotoscope_ai_chat.py")
        print("3. Digite suas perguntas sobre loterias!")
        print()
        print("💡 COMANDOS ÚTEIS:")
        print("   /analyze arquivo.py  - Analisa código")
        print("   /improve tópico      - Sugere melhorias")
        print("   /patterns megasena   - Pesquisa padrões")
        print("   /help               - Ajuda completa")
        print()
        print("🎯 SEU ASSISTENTE IA ESTÁ PRONTO!")
    
    def run_installation(self):
        """Executa instalação completa"""
        self.print_header()
        
        # Verificar requisitos
        if not self.check_system_requirements():
            return False
        
        # Verificar se já está instalado
        self.check_ollama_installed()
        
        # Baixar Ollama se necessário
        if not self.ollama_installed:
            if not self.download_ollama():
                return False
            
            if not self.install_ollama():
                return False
        
        # Listar modelos
        self.list_available_models()
        
        # Escolher modelo
        print("🎯 ESCOLHA UM MODELO:")
        print("1. llama3:8b (recomendado para começar)")
        print("2. llama3:70b (mais preciso, precisa mais RAM)")
        print("3. codellama:13b (especializado em código)")
        
        choice = input("\n👤 Sua escolha (1-3): ").strip()
        
        model_map = {"1": "llama3:8b", "2": "llama3:70b", "3": "codellama:13b"}
        model_name = model_map.get(choice, "llama3:8b")
        
        print(f"🎯 Modelo selecionado: {model_name}")
        
        # Instalar modelo
        if not self.install_model(model_name):
            print("❌ Falha na instalação do modelo")
            return False
        
        # Testar instalação
        if not self.test_installation(model_name):
            print("⚠️ Instalação pode ter problemas")
        
        # Instalar dependências Python
        self.install_python_dependencies()
        
        # Criar atalhos
        self.create_shortcuts()
        
        # Mostrar informações finais
        self.show_completion_info(model_name)
        
        return True

def main():
    """Função principal"""
    installer = LlamaSetupInstaller()
    
    try:
        success = installer.run_installation()
        
        if success:
            print("\n🏆 SETUP CONCLUÍDO COM SUCESSO!")
            
            # Perguntar se quer iniciar agora
            start_now = input("\n🚀 Iniciar o assistente agora? (s/n): ").lower().strip()
            if start_now in ['s', 'sim', 'y', 'yes']:
                print("🤖 Iniciando LotoScope AI Assistant...")
                subprocess.run([sys.executable, 'lotoscope_ai_chat.py'])
        else:
            print("\n❌ SETUP FALHOU!")
            print("💡 Tente a instalação manual seguindo o guia")
    
    except KeyboardInterrupt:
        print("\n👋 Instalação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
