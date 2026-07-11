#!/usr/bin/env python3
"""
LotoScope Agent Orchestrator com Integração OpenCode
Permite que os agentes chamem o OpenCode como LLM backend quando não souberem resolver.

Fluxo:
1. Usuário chama agente via CLI ou MCP
2. Agente tenta resolver com tools locais (SQL, execução, etc)
3. Se não souber → chama OpenCode via API local
4. OpenCode responde → agente retorna ao usuário
"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
AGENTS_DIR = BASE_DIR / ".github" / "agents"

# Configuração do OpenCode
OPENCODE_CONFIG = {
    "base_url": os.environ.get("OPENCODE_BASE_URL", "http://localhost:11434/v1"),
    "api_key": os.environ.get("OPENCODE_API_KEY", "opencode-go"),
    "model": os.environ.get("OPENCODE_MODEL", "gpt-oss:20b"),
    "timeout": 60
}

# Definição dos agentes
AGENTS = {
    "coordinator": {
        "name": "LotoScope Coordinator",
        "description": "Ponto de entrada inteligente. Interpreta pedidos e orquestra agentes especialistas.",
        "keywords": ["orquestrar", "coordenar", "multi-agente", "não sei", "ajuda"],
        "tools": ["read", "search", "execute", "editFiles", "llm"],
        "prompt_file": "lotoscope-coordinator.agent.md"
    },
    "architect": {
        "name": "LotoScope Architect",
        "description": "Guardião da arquitetura, regras de negócio e integridade do sistema.",
        "keywords": ["arquitetura", "regra", "restrição", "design", "modelo de dados", "restricao"],
        "tools": ["read", "search", "llm"],
        "prompt_file": "lotoscope-architect.agent.md"
    },
    "analyst": {
        "name": "LotoScope Analyst",
        "description": "Análise estatística da Lotofácil: frequências, backtests, padrões, ROI.",
        "keywords": ["análise", "frequência", "concurso", "histórico", "padrão", "tendência", "analise", "frequencia"],
        "tools": ["read", "search", "execute", "sql", "llm"],
        "prompt_file": "lotoscope-analyst.agent.md"
    },
    "pool23": {
        "name": "Pool 23 Generator",
        "description": "Geração de combinações Pool 23 Híbrido (Opção 31), níveis 0-8.",
        "keywords": ["gerar", "combinações", "nível", "excluir", "pool 23", "opção 31", "nivel", "combinacoes"],
        "tools": ["execute", "read", "search", "llm"],
        "prompt_file": "pool23-generator.agent.md"
    },
    "strategy": {
        "name": "Strategy Reviewer",
        "description": "Validação e comparação de estratégias, benchmark, ROI.",
        "keywords": ["ROI", "benchmark", "comparar", "estratégia", "melhor nível", "estrategia", "nivel"],
        "tools": ["read", "search", "execute", "sql", "llm"],
        "prompt_file": "strategy-reviewer.agent.md"
    },
    "dev": {
        "name": "LotoScope Dev",
        "description": "Implementação, correção e evolução do código LotoScope.",
        "keywords": ["implementar", "corrigir", "bug", "código", "feature", "refatorar", "codigo"],
        "tools": ["read", "search", "execute", "editFiles", "llm"],
        "prompt_file": "lotoscope-dev.agent.md"
    },
    "docs": {
        "name": "Docs Updater",
        "description": "Manutenção da documentação: CONTEXTO_MASTER, QUICK_START, etc.",
        "keywords": ["documentar", "atualizar docs", "registrar", "sincronizar", "documentação"],
        "tools": ["read", "edit", "search", "llm"],
        "prompt_file": "docs-updater.agent.md"
    }
}

# Workflows pré-definidos
WORKFLOWS = {
    "pos_sorteio": {
        "name": "Pós-Sorteio",
        "description": "Analisa resultados após sorteio e calcula ROI",
        "steps": [
            {"agent": "analyst", "task": "Verificar acertos das combinações geradas"},
            {"agent": "strategy", "task": "Calcular ROI do concurso"},
            {"agent": "docs", "task": "Registrar resultado nos docs"}
        ]
    },
    "preparacao": {
        "name": "Preparação para Próximo Concurso",
        "description": "Analisa tendências e gera combinações otimizadas",
        "steps": [
            {"agent": "analyst", "task": "Analisar últimos 10 concursos, identificar HOT/COLD"},
            {"agent": "architect", "task": "Validar se há anomalias de persistência"},
            {"agent": "pool23", "task": "Gerar combinações com números excluídos"},
            {"agent": "strategy", "task": "Confirmar nível com melhor ROI"}
        ]
    },
    "nova_feature": {
        "name": "Nova Feature",
        "description": "Implementa nova feature com validação completa",
        "steps": [
            {"agent": "architect", "task": "Validar design contra regras de negócio"},
            {"agent": "dev", "task": "Implementar a feature"},
            {"agent": "analyst", "task": "Validar com backtest"},
            {"agent": "docs", "task": "Documentar a mudança"}
        ]
    },
    "investigacao_bug": {
        "name": "Investigação de Bug",
        "description": "Diagnostica e corrige bugs com validação",
        "steps": [
            {"agent": "dev", "task": "Diagnosticar e corrigir o bug"},
            {"agent": "architect", "task": "Confirmar que não viola restrições"},
            {"agent": "docs", "task": "Registrar o fix no histórico"}
        ]
    }
}


class OpenCodeClient:
    """Cliente para API do OpenCode (compatível com OpenAI)."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or OPENCODE_CONFIG
        self.base_url = self.config["base_url"]
        self.api_key = self.config["api_key"]
        self.model = self.config["model"]
        self.timeout = self.config["timeout"]
        
        # Tentar importar openai
        try:
            import openai
            self.client = openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout
            )
            self.available = True
        except ImportError:
            print("Aviso: openai não instalado. Usando fallback HTTP.")
            self.client = None
            self.available = False
        except Exception as e:
            print(f"Aviso: Erro ao conectar com OpenCode: {e}")
            self.client = None
            self.available = False
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """Envia chat para o OpenCode e retorna resposta."""
        if not self.available:
            return self._http_fallback(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao chamar OpenCode: {e}")
            return self._http_fallback(messages)
    
    def _http_fallback(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Fallback via HTTP direto se openai não estiver disponível."""
        import urllib.request
        import urllib.error
        
        try:
            url = f"{self.base_url}/chat/completions"
            data = json.dumps({
                "model": self.model,
                "messages": messages
            }).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            print(f"Erro no fallback HTTP: {e}")
            return None
    
    def is_available(self) -> bool:
        """Verifica se o OpenCode está acessível."""
        if not self.available:
            return False
        
        try:
            # Tentar listar modelos
            models = self.client.models.list()
            return len(models.data) > 0
        except:
            return False


class AgentOrchestrator:
    """Orquestrador de agentes com integração OpenCode."""
    
    def __init__(self):
        self.agents = AGENTS
        self.workflows = WORKFLOWS
        self.opencode = OpenCodeClient()
        self.conversation_history: Dict[str, List] = {}
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """Lista todos os agentes disponíveis."""
        result = []
        for agent_id, agent_info in self.agents.items():
            result.append({
                "id": agent_id,
                "name": agent_info["name"],
                "description": agent_info["description"],
                "keywords": agent_info["keywords"],
                "tools": agent_info["tools"],
                "llm_available": self.opencode.is_available()
            })
        return result
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """Lista todos os workflows disponíveis."""
        result = []
        for wf_id, wf_info in self.workflows.items():
            result.append({
                "id": wf_id,
                "name": wf_info["name"],
                "description": wf_info["description"],
                "steps": len(wf_info["steps"])
            })
        return result
    
    def route_request(self, request: str) -> Dict[str, Any]:
        """Roteia request para o agente mais apropriado."""
        request_lower = request.lower()
        
        scores = {}
        for agent_id, agent_info in self.agents.items():
            score = sum(1 for kw in agent_info["keywords"] if kw in request_lower)
            if score > 0:
                scores[agent_id] = score
        
        if scores:
            best_agent = max(scores, key=scores.get)
            agent_info = self.agents[best_agent]
            return {
                "routed_to": best_agent,
                "agent_name": agent_info["name"],
                "confidence": scores[best_agent],
                "reason": "Keywords detectadas na request"
            }
        
        return {
            "routed_to": "coordinator",
            "agent_name": self.agents["coordinator"]["name"],
            "confidence": 0,
            "reason": "Nenhuma keyword específica detectada, usando coordinator"
        }
    
    def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """Retorna contexto completo do agente."""
        if agent_id not in self.agents:
            return {"error": f"Agente {agent_id} não encontrado"}
        
        agent = self.agents[agent_id]
        prompt_file = AGENTS_DIR / agent["prompt_file"]
        
        system_prompt = ""
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        system_prompt = parts[2].strip()
                else:
                    system_prompt = content
        
        return {
            "id": agent_id,
            "name": agent["name"],
            "description": agent["description"],
            "available_tools": agent["tools"],
            "system_prompt": system_prompt,
            "llm_available": self.opencode.is_available()
        }
    
    def call_agent(self, agent_id: str, task: str, use_llm: bool = False) -> Dict[str, Any]:
        """Chama um agente específico com uma tarefa."""
        if agent_id not in self.agents:
            return {"error": f"Agente {agent_id} não encontrado"}
        
        context = self.get_agent_context(agent_id)
        
        result = {
            "agent_id": agent_id,
            "agent_name": context["name"],
            "task": task,
            "context": context,
            "status": "ready",
            "message": f"Agente {context['name']} pronto para executar: {task}",
            "instruction": f"Use o contexto acima para executar a tarefa: {task}"
        }
        
        # Se use_llm=True e OpenCode disponível, chama o LLM
        if use_llm and self.opencode.is_available():
            llm_response = self._agent_llm_call(agent_id, task, context)
            result["llm_response"] = llm_response
            result["used_llm"] = True
        
        return result
    
    def _agent_llm_call(self, agent_id: str, task: str, context: Dict) -> Optional[str]:
        """Chama o OpenCode com o contexto do agente."""
        system_prompt = context.get("system_prompt", "")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # Adicionar histórico se existir
        if agent_id in self.conversation_history:
            messages.extend(self.conversation_history[agent_id])
        
        response = self.opencode.chat(messages)
        
        # Salvar no histórico
        if agent_id not in self.conversation_history:
            self.conversation_history[agent_id] = []
        
        self.conversation_history[agent_id].append({"role": "user", "content": task})
        if response:
            self.conversation_history[agent_id].append({"role": "assistant", "content": response})
        
        return response
    
    def orchestrate(self, workflow_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Orquestra múltiplos agentes em sequência."""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow '{workflow_id}' não encontrado"}
        
        workflow = self.workflows[workflow_id]
        steps_with_context = []
        
        for step in workflow["steps"]:
            agent_id = step["agent"]
            if agent_id in self.agents:
                step_context = self.get_agent_context(agent_id)
                steps_with_context.append({
                    "step": len(steps_with_context) + 1,
                    "agent_id": agent_id,
                    "agent_name": step_context["name"],
                    "task": step["task"],
                    "context_available": True,
                    "llm_available": self.opencode.is_available()
                })
            else:
                steps_with_context.append({
                    "step": len(steps_with_context) + 1,
                    "agent_id": agent_id,
                    "error": "Agente não encontrado"
                })
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "description": workflow["description"],
            "steps": steps_with_context,
            "params": params or {},
            "llm_available": self.opencode.is_available()
        }
    
    def delegate_to_opencode(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Delega tarefa diretamente ao OpenCode."""
        if not self.opencode.is_available():
            return {
                "error": "OpenCode não disponível",
                "request": request,
                "status": "failed"
            }
        
        messages = [
            {"role": "system", "content": "Você é o assistente OpenCode do projeto LotoScope."},
            {"role": "user", "content": request}
        ]
        
        if context:
            messages[0]["content"] += f"\n\nContexto: {json.dumps(context, ensure_ascii=False)}"
        
        response = self.opencode.chat(messages)
        
        return {
            "delegated_to": "opencode",
            "request": request,
            "context": context or {},
            "status": "completed" if response else "failed",
            "response": response
        }
    
    def check_opencode_status(self) -> Dict[str, Any]:
        """Verifica status do OpenCode."""
        available = self.opencode.is_available()
        
        return {
            "available": available,
            "base_url": self.opencode.base_url,
            "model": self.opencode.model,
            "message": "OpenCode disponível" if available else "OpenCode não disponível. Verifique se está rodando."
        }


def main():
    """CLI principal."""
    if len(sys.argv) < 2:
        print("Uso: python lotoscope_agents.py <comando> [args]")
        print("\nComandos:")
        print("  list                          - Lista agentes disponíveis")
        print("  workflows                     - Lista workflows disponíveis")
        print("  route <request>               - Roteia request para agente")
        print("  context <agent_id>            - Obtém contexto do agente")
        print("  call <agent_id> <task>        - Chama agente com tarefa")
        print("  call-llm <agent_id> <task>    - Chama agente com LLM (OpenCode)")
        print("  delegate <request>            - Delega tarefa ao OpenCode")
        print("  orchestrate <workflow>        - Executa workflow")
        print("  opencode-status               - Verifica status do OpenCode")
        sys.exit(1)
    
    orchestrator = AgentOrchestrator()
    command = sys.argv[1]
    
    if command == "list":
        result = orchestrator.list_agents()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "workflows":
        result = orchestrator.list_workflows()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "route":
        if len(sys.argv) < 3:
            print("Uso: route <request>")
            sys.exit(1)
        request = " ".join(sys.argv[2:])
        result = orchestrator.route_request(request)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "context":
        if len(sys.argv) < 3:
            print("Uso: context <agent_id>")
            sys.exit(1)
        agent_id = sys.argv[2]
        result = orchestrator.get_agent_context(agent_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "call":
        if len(sys.argv) < 4:
            print("Uso: call <agent_id> <task>")
            sys.exit(1)
        agent_id = sys.argv[2]
        task = " ".join(sys.argv[3:])
        result = orchestrator.call_agent(agent_id, task, use_llm=False)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "call-llm":
        if len(sys.argv) < 4:
            print("Uso: call-llm <agent_id> <task>")
            sys.exit(1)
        agent_id = sys.argv[2]
        task = " ".join(sys.argv[3:])
        result = orchestrator.call_agent(agent_id, task, use_llm=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "delegate":
        if len(sys.argv) < 3:
            print("Uso: delegate <request>")
            sys.exit(1)
        request = " ".join(sys.argv[2:])
        result = orchestrator.delegate_to_opencode(request)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "orchestrate":
        if len(sys.argv) < 3:
            print("Uso: orchestrate <workflow>")
            sys.exit(1)
        workflow_id = sys.argv[2]
        result = orchestrator.orchestrate(workflow_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "opencode-status":
        result = orchestrator.check_opencode_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
