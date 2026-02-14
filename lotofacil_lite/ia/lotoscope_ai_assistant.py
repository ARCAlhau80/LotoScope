#!/usr/bin/env python3
"""
LotoScope AI Assistant - Prototype
Assistente IA local especializado em análise de loterias
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

class LotoScopeAIAssistant:
    """Assistente IA especializado no projeto LotoScope"""
    
    def __init__(self):
        self.model = "llama3:8b"
        self.project_root = Path(__file__).parent
        self.context_history = []
        self.knowledge_base = self._build_knowledge_base()
        
        # Detectar melhor modelo disponível
        self.model = self._detect_best_model()
    
    def _detect_best_model(self):
        """Detecta o melhor modelo disponível no sistema"""
        preferred_models = [
            "llama3.2:3b",     # Mais rápido
            "llama3.2:1b",     # Muito rápido
            "llama3:8b",
            "llama3:latest", 
            "llama3.1:8b",
            "phi:latest",      # Modelo leve
            "gemma:7b",
            "gpt-oss:20b"      # Movido para último (muito pesado)
        ]
        
        try:
            # Obter lista de modelos instalados
            import os
            possivel_paths = [
                f"C:\\Users\\{os.environ.get('USERNAME', '')}\\AppData\\Local\\Programs\\Ollama\\ollama.exe",
                "ollama"
            ]
            
            for ollama_path in possivel_paths:
                try:
                    if ollama_path != "ollama" and not os.path.exists(ollama_path):
                        continue
                        
                    result = subprocess.run([ollama_path, 'list'], 
                                          capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        models_output = result.stdout.lower()
                        
                        # Procurar modelo preferido
                        for model in preferred_models:
                            if model.lower() in models_output:
                                print(f"🤖 Usando modelo: {model}")
                                return model
                        
                        # Se não encontrou preferido, usar o primeiro disponível
                        lines = result.stdout.split('\n')[1:]  # Pular header
                        for line in lines:
                            if line.strip():
                                model_name = line.split()[0]
                                print(f"🤖 Usando modelo disponível: {model_name}")
                                return model_name
                        
                        break
                except:
                    continue
            
        except Exception as e:
            print(f"⚠️  Erro ao detectar modelo: {e}")
        
        # Fallback para modelo padrão
        return "llama3:8b"
    
    def _build_knowledge_base(self):
        """Constrói base de conhecimento do projeto"""
        knowledge = {
            "project_name": "LotoScope",
            "focus_areas": ["Lotofácil", "Mega-Sena", "Análise Preditiva"],
            "technologies": ["Python", "SQL Server", "Machine Learning"],
            "key_algorithms": [
                "Gerador Acadêmico Dinâmico",
                "Sistema de Baixa Sobreposição", 
                "Análise de Correlações Temporais",
                "Insights em Tempo Real"
            ],
            "database_tables": [
                "Resultados_MegaSenaFechado",
                "COMBIN_MEGASENA", 
                "NumerosCiclosMega"
            ],
            "number_ranges": {
                "lotofacil": "1-25 (15 números)",
                "megasena": "1-60 (6 números)"
            }
        }
        
        # Analisar arquivos Python no projeto
        try:
            arquivos_encontrados = []
            for arquivo in self.project_root.glob("*.py"):
                if arquivo.name != "lotoscope_ai_assistant.py":  # Evitar recursão
                    arquivos_encontrados.append(arquivo.name)
            
            knowledge["arquivos_python"] = arquivos_encontrados[:10]  # Primeiros 10
            
        except Exception:
            knowledge["arquivos_python"] = ["Erro ao listar arquivos"]
        
        return knowledge
    
    def check_ollama_status(self):
        """Verifica se Ollama está instalado e funcionando"""
        try:
            # Caminhos possíveis do Ollama
            import os
            possivel_paths = [
                f"C:\\Users\\{os.environ.get('USERNAME', '')}\\AppData\\Local\\Programs\\Ollama\\ollama.exe",
                "C:\\Program Files\\Ollama\\ollama.exe",
                "ollama"  # Se estiver no PATH
            ]
            
            for ollama_path in possivel_paths:
                try:
                    # Verificar se existe (para caminhos absolutos)
                    if ollama_path != "ollama" and not os.path.exists(ollama_path):
                        continue
                        
                    # Tentar listar modelos
                    result = subprocess.run([ollama_path, 'list'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        models = result.stdout
                        if self.model.split(':')[0] in models:
                            return True, f"✅ Ollama OK - {self.model} disponível"
                        else:
                            return False, f"⚠️ Ollama OK, mas modelo {self.model} não instalado. Execute: {ollama_path} pull {self.model}"
                    else:
                        continue
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
            
            return False, "❌ Ollama não encontrado"
            
        except Exception as e:
            return False, f"❌ Erro: {e}"
    
    def analyze_project_structure(self):
        """Analisa estrutura do projeto LotoScope"""
        analysis = {
            "python_files": [],
            "key_modules": [],
            "databases": [],
            "tests": [],
            "documentation": []
        }
        
        for file_path in self.project_root.glob("**/*.py"):
            file_name = file_path.name
            analysis["python_files"].append(file_name)
            
            # Categorizar arquivos importantes
            if "gerador" in file_name.lower():
                analysis["key_modules"].append(file_name)
            elif "test" in file_name.lower():
                analysis["tests"].append(file_name)
            elif "conector" in file_name.lower() or "db" in file_name.lower():
                analysis["databases"].append(file_name)
        
        # Procurar documentação
        for ext in ["*.md", "*.txt"]:
            for doc_path in self.project_root.glob(ext):
                analysis["documentation"].append(doc_path.name)
        
        return analysis
    
    def query_llama(self, prompt, context=""):
        """Faz consulta ao Llama local"""
        try:
            # Prompt otimizado para respostas completas
            if "20b" in self.model:
                specialized_prompt = f"""Você é um assistente especializado no projeto LotoScope - um sistema de análise de loterias brasileiras.

CONHECIMENTO DO PROJETO:
- Foco: Lotofácil e Mega-Sena
- Linguagem: Python
- Banco: SQL Server
- Algoritmos: Gerador Dinâmico, Baixa Sobreposição
- Tabelas: Resultados_MegaSenaFechado, COMBIN_MEGASENA
- Arquivos: {', '.join(self.knowledge_base.get('arquivos_python', [])[:5])}

INSTRUÇÃO: Responda de forma completa e detalhada. Complete todas as tabelas e explicações que iniciar.

PERGUNTA: {prompt}

Resposta completa e técnica:"""
            else:
                # Construir prompt especializado completo para modelos menores
                specialized_prompt = f"""
            Você é um assistente especializado no projeto LotoScope, focado em análise de loterias brasileiras (Lotofácil e Mega-Sena).
            
            CONTEXTO DO PROJETO:
            - Linguagem: Python
            - Foco: Algoritmos preditivos para loterias
            - Banco: SQL Server 
            - Tecnologias: Machine Learning, análise estatística
            
            BASE DE CONHECIMENTO:
            {json.dumps(self.knowledge_base, indent=2)}
            
            CONTEXTO ADICIONAL:
            {context}
            
            PERGUNTA/SOLICITAÇÃO:
            {prompt}
            
            Por favor, responda de forma técnica, prática e focada no desenvolvimento do projeto LotoScope.
            """
            
            # Executar consulta via Ollama API HTTP
            data = {
                "model": self.model,
                "prompt": specialized_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4,      # Aumentado para mais variação
                    "top_p": 0.9,           # Mais flexível
                    "num_predict": 500,     # Muito mais tokens
                    "repeat_penalty": 1.05, # Menos restritivo
                    "top_k": 50,            # Mais opções
                    "stop": ["👤 Você:", "\n👤", "🤖 Assistente:"]  # Só parar em novos turnos
                }
            }
            
            # Timeout adaptativo baseado no modelo
            if "20b" in self.model:
                timeout = 180  # 3 minutos para modelo muito grande
            elif "8b" in self.model:
                timeout = 90   # 1.5 minuto para modelo médio
            else:
                timeout = 60   # 1 minuto para modelos menores
            
            response = requests.post(
                f"http://localhost:11434/api/generate",
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                resposta = result.get('response', '❌ Resposta vazia').strip()
                
                # Limitar tamanho da resposta
                if len(resposta) > 1000:
                    resposta = resposta[:1000] + "..."
                
                return resposta
            else:
                return f"❌ Erro HTTP {response.status_code}: {response.text[:100]}"
            
        except Exception as e:
            return f"❌ Erro ao consultar Llama: {e}"
    
    def responder(self, pergunta):
        """Responde perguntas usando o modelo de IA"""
        prompt = f"""
        Você é um assistente especializado em análise de loterias e o projeto LotoScope.
        
        Pergunta: {pergunta}
        
        Responda de forma clara e útil, considerando:
        - Expertise em algoritmos de loteria
        - Conhecimento do projeto LotoScope
        - Análise de padrões e estatísticas
        - Otimização de código Python
        
        Resposta:
        """
        
        return self.query_llama(prompt)
    
    def analisar_codigo_python(self, codigo, nome_arquivo=""):
        """Analisa código Python específico"""
        prompt = f"""
        Analise este código Python do projeto LotoScope:
        
        ARQUIVO: {nome_arquivo}
        
        CÓDIGO:
        {codigo}
        
        Forneça análise detalhada incluindo:
        1. Funcionalidade principal
        2. Qualidade do código
        3. Possíveis melhorias
        4. Bugs ou problemas
        5. Sugestões de otimização
        
        Análise:
        """
        
        return self.query_llama(prompt)
    
    def analisar_estrutura_projeto(self):
        """Analisa estrutura geral do projeto"""
        try:
            arquivos = list(self.project_root.glob("*.py"))
            estrutura = "\n".join([f"- {arquivo.name}" for arquivo in arquivos[:10]])
            
            prompt = f"""
            Analise a estrutura do projeto LotoScope:
            
            ARQUIVOS PYTHON ENCONTRADOS:
            {estrutura}
            
            Forneça insights sobre:
            1. Organização do projeto
            2. Arquitetura geral
            3. Pontos fortes
            4. Áreas de melhoria
            5. Sugestões de estruturação
            
            Análise:
            """
            
            return self.query_llama(prompt)
            
        except Exception as e:
            return f"❌ Erro na análise: {e}"
    
    def sugerir_melhorias(self, topico):
        """Sugere melhorias para tópicos específicos"""
        prompt = f"""
        Como especialista em loterias e LotoScope, sugira melhorias para: {topico}
        
        Considere:
        - Algoritmos mais eficientes
        - Melhores práticas Python
        - Otimização de performance
        - Integração com banco de dados
        
        Sugestões:
        """
        
        return self.query_llama(prompt)
    
    def analyze_code_file(self, file_path):
        """Analisa arquivo de código específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            prompt = f"""
            Analise este arquivo Python do projeto LotoScope:
            
            ARQUIVO: {file_path}
            
            CÓDIGO:
            {code[:2000]}  # Limita para não sobrecarregar
            
            Por favor, forneça:
            1. Resumo da funcionalidade
            2. Pontos fortes do código
            3. Sugestões de melhorias
            4. Possíveis bugs ou problemas
            5. Como integrar melhor com outros módulos do LotoScope
            """
            
            return self.query_llama(prompt)
            
        except Exception as e:
            return f"❌ Erro ao analisar arquivo: {e}"
    
    def suggest_improvements(self, topic):
        """Sugere melhorias para tópicos específicos"""
        prompt = f"""
        Como especialista em análise de loterias e algoritmos preditivos, sugira melhorias para:
        
        TÓPICO: {topic}
        
        Considere:
        - Algoritmos mais eficientes
        - Melhores práticas de código Python
        - Estratégias matemáticas avançadas
        - Otimizações de performance
        - Integração com banco de dados
        - Experiência do usuário
        
        Seja específico e prático, com exemplos de código quando apropriado.
        """
        
        return self.query_llama(prompt, f"Projeto atual: {self.analyze_project_structure()}")
    
    def research_patterns(self, lottery_type, data_sample=""):
        """Pesquisa padrões em dados de loteria"""
        prompt = f"""
        Como pesquisador especialista em {lottery_type}, analise padrões e sugira estratégias:
        
        DADOS AMOSTRA:
        {data_sample}
        
        Por favor, identifique:
        1. Padrões numéricos interessantes
        2. Frequências e tendências
        3. Correlações entre números
        4. Estratégias de seleção
        5. Algoritmos recomendados para implementar
        
        Foque em insights práticos para o desenvolvimento de algoritmos preditivos.
        """
        
        return self.query_llama(prompt)

def main():
    """Função principal - demonstração do assistente"""
    print("🤖 LOTOSCOPE AI ASSISTANT - PROTOTYPE")
    print("=" * 50)
    
    assistant = LotoScopeAIAssistant()
    
    # Verificar status do Ollama
    status_ok, status_msg = assistant.check_ollama_status()
    print(f"🔧 Status Ollama: {status_msg}")
    
    if not status_ok:
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Instalar Ollama: https://ollama.ai/download")
        print("2. Executar: ollama pull llama3:8b")
        print("3. Testar: ollama run llama3:8b")
        return
    
    # Analisar projeto
    print(f"\n📊 Analisando projeto LotoScope...")
    structure = assistant.analyze_project_structure()
    print(f"   📁 {len(structure['python_files'])} arquivos Python encontrados")
    print(f"   🎯 {len(structure['key_modules'])} módulos principais")
    print(f"   🧪 {len(structure['tests'])} arquivos de teste")
    
    # Exemplo de consulta
    print(f"\n🤖 Testando consulta ao assistente...")
    response = assistant.query_llama("Qual a melhor estratégia para otimizar o gerador dinâmico da Mega-Sena?")
    print(f"📝 Resposta: {response[:200]}...")
    
    print(f"\n✅ Prototype funcionando! Assistente IA pronto para uso.")

if __name__ == "__main__":
    main()
