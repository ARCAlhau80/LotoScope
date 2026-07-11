#!/usr/bin/env python3
"""
LotoScope AI Chat - Interface Interativa
Chat integrado com o assistente IA especializado
"""

import os
import sys
from datetime import datetime
from itertools import combinations
from lotoscope_ai_assistant import LotoScopeAIAssistant

class LotoScopeAIChat:
    """Interface de chat para o assistente IA"""
    
    def __init__(self):
        self.assistant = LotoScopeAIAssistant()
        self.chat_history = []
        self.session_start = datetime.now()
    
    def display_header(self):
        """Mostra cabeçalho do chat"""
        print("🤖" + "="*60 + "🤖")
        print("          LOTOSCOPE AI ASSISTANT - CHAT")
        print("🤖" + "="*60 + "🤖")
        print("🎯 Especialista em Lotofácil & Mega-Sena")
        print("🧠 Powered by Llama 3 Local")
        print("🔒 100% Privado - Dados não saem do seu PC")
        print()
        print("💡 COMANDOS ESPECIAIS:")
        print("   /analyze [arquivo.py] - Analisa código")
        print("   /improve [tópico]     - Sugere melhorias") 
        print("   /patterns [loteria]   - Pesquisa padrões")
        print("   /combinacoes [fixos]  - Gera combinações com números fixos")
        print("   /status               - Status do sistema")
        print("   /history              - Histórico da sessão")
        print("   /help                 - Ajuda")
        print("   /quit                 - Sair")
        print("-" * 62)
    
    def process_command(self, user_input):
        """Processa comandos especiais"""
        if user_input.startswith('/'):
            parts = user_input.split(' ', 1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            if command == '/status':
                return self.show_status()
            elif command == '/analyze':
                return self.analyze_file(args)
            elif command == '/improve':
                return self.suggest_improvements(args)
            elif command == '/combinacoes':
                return self.gerar_combinacoes(args)
            elif command == '/patterns':
                return self.research_patterns(args)
            elif command == '/history':
                return self.show_history()
            elif command == '/help':
                return self.show_help()
            elif command == '/quit':
                return "QUIT"
            else:
                return f"❌ Comando desconhecido: {command}"
        return None
    
    def show_status(self):
        """Mostra status do sistema"""
        status_ok, status_msg = self.assistant.check_ollama_status()
        structure = self.assistant.analyze_project_structure()
        
        info = f"""
🔧 STATUS DO SISTEMA:
{status_msg}

📊 ANÁLISE DO PROJETO:
• {len(structure['python_files'])} arquivos Python
• {len(structure['key_modules'])} módulos principais  
• {len(structure['tests'])} arquivos de teste
• {len(structure['documentation'])} documentos

⏱️ SESSÃO:
• Iniciada: {self.session_start.strftime('%H:%M:%S')}
• Consultas: {len(self.chat_history)}
"""
        return info
    
    def analyze_file(self, filename):
        """Analisa arquivo específico"""
        if not filename:
            return "❌ Especifique um arquivo: /analyze nome_arquivo.py"
        
        file_path = os.path.join(self.assistant.project_root, filename)
        if not os.path.exists(file_path):
            return f"❌ Arquivo não encontrado: {filename}"
        
        print("🔍 Analisando arquivo... (pode demorar alguns segundos)")
        return self.assistant.analyze_code_file(file_path)
    
    def suggest_improvements(self, topic):
        """Sugere melhorias para tópico"""
        if not topic:
            return "❌ Especifique um tópico: /improve gerador dinâmico"
        
        print("💡 Gerando sugestões... (pode demorar alguns segundos)")
        return self.assistant.suggest_improvements(topic)
    
    def gerar_combinacoes(self, args):
        """Gera todas combinações de 15 números com fixos"""
        if not args:
            return "❌ Use: /combinacoes 2,3,4,8,10,11,12,14,15,18,19"

        try:
            fixos = [int(n.strip()) for n in args.replace(",", " ").split()]
            fixos = sorted(set(fixos))

            if len(fixos) < 1 or len(fixos) > 14:
                return "❌ Informe entre 1 e 14 números fixos."
            if any(n < 1 or n > 25 for n in fixos):
                return "❌ Números devem estar entre 1 e 25."

            restantes = [n for n in range(1, 26) if n not in fixos]
            precisamos = 15 - len(fixos)

            if precisamos < 1 or precisamos > len(restantes):
                return f"❌ Impossível: {len(fixos)} fixos precisam de {precisamos} números, mas só há {len(restantes)} disponíveis."

            combinacoes = []
            for comb in combinations(restantes, precisamos):
                combinacoes.append(tuple(sorted(fixos + list(comb))))

            combinacoes.sort()

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'combinacoes_fixas_{timestamp}.txt'
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Fixos: {fixos}\n")
                f.write(f"Total: {len(combinacoes)} combinacoes\n")
                f.write("=" * 50 + "\n\n")
                for i, combo in enumerate(combinacoes, 1):
                    f.write(f"{i:4d}. {str(list(combo))}\n")

            return f"[OK] {len(combinacoes)} combinacoes geradas!\n[ARQUIVO] {filepath}\n[FIXOS] {fixos}\n[AMOSTRA]:\n" + \
                   "\n".join(f"   {str(list(c))}" for c in combinacoes[:5]) + \
                   ("\n   ..." if len(combinacoes) > 5 else "")

        except ValueError:
            return "❌ Formato invalido. Use: /combinacoes 2,3,4,8,10,11,12,14,15,18,19"
        except Exception as e:
            return f"❌ Erro: {e}"

    def research_patterns(self, lottery_type):
        """Pesquisa padrões em loteria"""
        if not lottery_type:
            return "❌ Especifique tipo: /patterns megasena ou /patterns lotofacil"
        
        print("🔬 Pesquisando padrões... (pode demorar alguns segundos)")
        return self.assistant.research_patterns(lottery_type)
    
    def show_history(self):
        """Mostra histórico da sessão"""
        if not self.chat_history:
            return "📝 Nenhuma consulta realizada nesta sessão"
        
        history = "📚 HISTÓRICO DA SESSÃO:\n"
        for i, (question, _) in enumerate(self.chat_history[-5:], 1):
            history += f"{i}. {question[:50]}...\n"
        return history
    
    def show_help(self):
        """Mostra ajuda detalhada"""
        return """
🆘 AJUDA - LOTOSCOPE AI ASSISTANT

CONSULTAS NORMAIS:
• Digite qualquer pergunta sobre loterias, algoritmos, Python, etc.
• O assistente é especializado no projeto LotoScope

COMANDOS ESPECIAIS:
• /analyze gerador_megasena.py - Analisa código específico
• /improve "baixa sobreposição" - Sugere melhorias
• /patterns megasena - Pesquisa padrões numéricos
• /combinacoes 2,3,4,8,10,11,12,14,15,18,19 - Gera combinações com fixos
• /status - Mostra status do sistema
• /history - Histórico das consultas
• /quit - Sair do chat

EXEMPLOS DE PERGUNTAS:
• "Como otimizar o algoritmo de geração dinâmica?"
• "Qual melhor estratégia para análise de correlações?"
• "Como implementar cache para melhorar performance?"
• "Sugestões para interface do usuário mais intuitiva?"

💡 DICA: Seja específico nas perguntas para respostas mais precisas!
"""
    
    def chat_loop(self):
        """Loop principal do chat"""
        self.display_header()
        
        # Verificar se Ollama está funcionando
        status_ok, status_msg = self.assistant.check_ollama_status()
        if not status_ok:
            print(f"❌ {status_msg}")
            print("\n💡 Configure o Ollama primeiro:")
            print("1. Baixar: https://ollama.ai/download")
            print("2. Instalar: ollama pull llama3:8b")
            return
        
        print(f"✅ Sistema pronto! Faça sua primeira pergunta:")
        print()
        
        while True:
            try:
                # Input do usuário
                user_input = input("👤 Você: ").strip()
                
                if not user_input:
                    continue
                
                # Processar comandos especiais
                command_result = self.process_command(user_input)
                if command_result == "QUIT":
                    print("👋 Obrigado por usar o LotoScope AI Assistant!")
                    break
                elif command_result:
                    print(f"🤖 Assistente: {command_result}")
                    continue
                
                # Consulta normal ao assistente
                print("🧠 Pensando... (pode demorar alguns segundos)")
                response = self.assistant.query_llama(user_input)
                
                # Salvar no histórico
                self.chat_history.append((user_input, response))
                
                # Mostrar resposta
                print(f"🤖 Assistente: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Chat interrompido. Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro no chat: {e}")

def main():
    """Inicia o chat do assistente"""
    chat = LotoScopeAIChat()
    chat.chat_loop()

if __name__ == "__main__":
    main()
