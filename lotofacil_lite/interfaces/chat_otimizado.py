#!/usr/bin/env python3
"""
LotoScope AI Chat - Versão Otimizada
Com fallback automático para modelos mais rápidos
"""

import sys
import time
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from lotoscope_ai_assistant import LotoScopeAIAssistant

class LotoScopeOptimizedChat:
    def __init__(self):
        """Inicializa chat com detecção de modelo otimizada"""
        self.assistant = LotoScopeAIAssistant()
        self.fast_mode = False
        
        # Testar velocidade do modelo atual
        self._test_model_speed()
    
    def _test_model_speed(self):
        """Testa velocidade do modelo atual"""
        print("🧪 Testando velocidade do modelo...")
        
        start_time = time.time()
        try:
            # Pergunta muito simples para teste
            resp = self.assistant.responder("Oi")
            test_time = time.time() - start_time
            
            if test_time > 60:  # Mais de 1 minuto
                print(f"⚠️  Modelo lento ({test_time:.1f}s). Ativando modo rápido.")
                self.fast_mode = True
            else:
                print(f"✅ Modelo responsivo ({test_time:.1f}s)")
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            self.fast_mode = True
    
    def responder_otimizado(self, pergunta):
        """Resposta otimizada com fallback"""
        if self.fast_mode:
            # Perguntas mais diretas para modelos lentos
            pergunta_otimizada = f"Responda brevemente: {pergunta}"
        else:
            pergunta_otimizada = pergunta
        
        try:
            return self.assistant.responder(pergunta_otimizada)
        except Exception as e:
            return f"❌ Erro: {e}"
    
    def executar_chat(self):
        """Executa loop principal do chat"""
        print("🤖" + "="*60 + "🤖")
        print("    LOTOSCOPE AI - MODO OTIMIZADO")
        print("🤖" + "="*60 + "🤖")
        print(f"🧠 Modelo: {self.assistant.model}")
        print(f"⚡ Modo rápido: {'Ativado' if self.fast_mode else 'Desativado'}")
        print("\n💡 Digite 'sair' para encerrar")
        print("-" * 62)
        
        while True:
            try:
                # Input do usuário
                pergunta = input("\n👤 Você: ").strip()
                
                if not pergunta:
                    continue
                
                if pergunta.lower() in ['sair', 'quit', 'exit']:
                    print("\n👋 Até logo!")
                    break
                
                # Comandos especiais
                if pergunta.startswith('/'):
                    self._processar_comando(pergunta)
                    continue
                
                # Resposta normal
                print("🧠 Processando...")
                start_time = time.time()
                
                resposta = self.responder_otimizado(pergunta)
                
                tempo = time.time() - start_time
                print(f"🤖 Assistente ({tempo:.1f}s): {resposta}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido. Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
    
    def _processar_comando(self, comando):
        """Processa comandos especiais"""
        if comando == '/speed':
            print(f"🚀 Modo rápido: {'Ativado' if self.fast_mode else 'Desativado'}")
            print(f"🤖 Modelo atual: {self.assistant.model}")
            
        elif comando == '/test':
            print("🧪 Testando velocidade...")
            self._test_model_speed()
            
        elif comando.startswith('/switch'):
            # Tentar trocar para modelo mais rápido
            modelos_rapidos = ['llama3.2:3b', 'llama3.2:1b', 'phi:latest']
            print("🔄 Procurando modelos mais rápidos...")
            
            # Aqui seria implementada a troca de modelo
            print("💡 Funcionalidade em desenvolvimento")
            
        elif comando == '/help':
            print("\n📚 COMANDOS DISPONÍVEIS:")
            print("   /speed  - Mostra informações de velocidade")
            print("   /test   - Testa velocidade do modelo")
            print("   /switch - Tenta usar modelo mais rápido")
            print("   /help   - Esta ajuda")
            
        else:
            print("❓ Comando não reconhecido. Use /help para ver comandos disponíveis")

def main():
    """Função principal"""
    try:
        chat = LotoScopeOptimizedChat()
        chat.executar_chat()
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
