# LotoScope Agent System - Arquitetura Completa

## Visão Geral

Sistema de agentes inteligente com **orquestração bidirecional** entre Copilot, agentes locais e OpenCode (LLM).

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA COMPLETA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Usuário    │────▶│   Copilot    │────▶│   @Agente X  │    │
│  │  (Terminal)  │     │   (VS Code)  │     │  (MCP Tool)  │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                    │                      │            │
│         │                    │                      ▼            │
│         │                    │           ┌──────────────────┐   │
│         │                    │           │  Agent Orchestr. │   │
│         │                    │           │  (Python CLI)    │   │
│         │                    │           └──────────────────┘   │
│         │                    │                      │            │
│         │                    │          ┌───────────┴────────  │
│         │                    │          ▼                    ▼  │
│         │                    │   ┌────────────┐      ┌────────│
│         │                    │   │ Tools      │      │ OpenCode││
│         │                    │   │ Locais     │      │  (LLM)  ││
│         │                    │   │            │      │         ││
│         │                    │   │ • SQL      │      │ • qwen  ││
│         │                    │   │ • Execute  │      │ • llama ││
│         │                    │   │ • Files    │      │ • etc   ││
│         │                    │   └────────────┘      └────────│
│         │                    │          │                    │   │
│         │                    │          └───────────┬────────┘  │
│         │                    │                      ▼            │
│         │                    │           ┌──────────────────┐   │
│         │                    │           │   Resposta       │   │
│         │                    │           │   Consolidada    │   │
│         │                    │           └──────────────────┘   │
│         │                    │                      │            │
│         │                    ◀──────────────────────┘            │
│         ────────────────────────────────────────────────────── │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes

### 1. Interface de Entrada

| Interface | Como Usar | Quando Usar |
|-----------|-----------|-------------|
| **Copilot Chat** | `@Agente X tarefa` | Interação natural no VS Code |
| **Terminal CLI** | `python lotoscope_agents.py call ...` | Scripts, automação |
| **Terminal MCP** | `python mcp_client.py call ...` | Teste de servidor MCP |
| **Scripts .bat** | `.\agent-call.bat ...` | Acesso rápido |

### 2. Agentes Disponíveis

| Agente | ID | Especialidade | Tools |
|--------|----|---------------|-------|
| **Coordinator** | `coordinator` | Roteamento, multi-agente | read, search, execute, editFiles, **llm** |
| **Architect** | `architect` | Arquitetura, regras | read, search, **llm** |
| **Analyst** | `analyst` | Análise estatística | read, search, execute, sql, **llm** |
| **Pool23** | `pool23` | Geração combinações | execute, read, search, **llm** |
| **Strategy** | `strategy` | Validação, ROI | read, search, execute, sql, **llm** |
| **Dev** | `dev` | Código, bugs | read, search, execute, editFiles, **llm** |
| **Docs** | `docs` | Documentação | read, edit, search, **llm** |

### 3. Tools MCP (10 tools)

#### Tools de Agente (6)
- `lotoscope_list_agents` - Lista agentes
- `lotoscope_list_workflows` - Lista workflows
- `lotoscope_route` - Roteia request
- `lotoscope_call_agent` - Chama agente
- `lotoscope_get_context` - Contexto do agente
- `lotoscope_orchestrate` - Workflow multi-agente

#### Tools de Delegação (2)
- `lotoscope_delegate` - **Delega ao OpenCode** ← Bidirecional
- `lotoscope_check_delegation` - Verifica delegações

#### Tools de Execução (2)
- `lotoscope_execute_command` - Executa comandos
- `lotoscope_query_database` - Query SQL

### 4. OpenCode (LLM Backend)

Quando o agente não sabe resolver, chama o OpenCode:

```python
# Exemplo de delegação
await session.call_tool("lotoscope_delegate", {
    "request": "Explique a estratégia Pool 23",
    "context": {"agent": "analyst", "topic": "pool23"},
    "agent_id": "analyst"
})
```

## Fluxos de Trabalho

### Fluxo 1: Agente Resolve Localmente
```
Usuário → @Analyst "verificar frequências"
    ↓
Analyst usa lotoscope_query_database
    ↓
Analyst retorna resultado
    ↓
Usuário recebe resposta
```

### Fluxo 2: Agente Delega ao OpenCode
```
Usuário → @Analyst "interpretar padrões complexos"
    ↓
Analyst tenta tools locais
    ↓
Não sabe → lotoscope_delegate
    ↓
OpenCode processa com LLM
    ↓
OpenCode retorna resposta
    ↓
Analyst consolida e retorna
    ↓
Usuário recebe resposta completa
```

### Fluxo 3: Workflow Multi-Agente
```
Usuário → @Coordinator "preparar para próximo concurso"
    ↓
Coordinator executa lotoscope_orchestrate("preparacao")
    ↓
Step 1: Analyst analisa tendências
Step 2: Architect valida anomalias
Step 3: Pool23 gera combinações
Step 4: Strategy confirma nível
    ↓
Coordinator consolida resultados
    ↓
Usuário recebe relatório completo
```

## Como Usar

### 1. Iniciar OpenCode

```powershell
# Opção A: Script automático
.\start-opencode.bat

# Opção B: Manual
opencode web

# Opção C: Verificar status
python lotoscope_agents.py opencode-status
```

### 2. Usar via Copilot

```
@LotoScope Analyst analise o concurso 3700
@Pool 23 Generator gere combinações nível 3
@LotoScope Dev corrija o bug na opção 30.2
```

### 3. Usar via Terminal

```powershell
# Listar agentes
python lotoscope_agents.py list

# Roteamento automático
python lotoscope_agents.py route "analisar concurso 3700"

# Chamar agente (sem LLM)
python lotoscope_agents.py call analyst "verificar frequências"

# Chamar agente (com LLM)
python lotoscope_agents.py call-llm analyst "interpretar padrões"

# Delegar ao OpenCode
python lotoscope_agents.py delegate "explique Pool 23"

# Executar workflow
python lotoscope_agents.py orchestrate pos_sorteio
```

### 4. Usar via MCP Client

```powershell
# Listar
python mcp_client.py list

# Roteamento
python mcp_client.py route "gerar combinacoes"

# Chamar agente
python mcp_client.py call pool23 "gerar nivel 3"

# Workflow
python mcp_client.py orchestrate pos_sorteio
```

## Configuração

### Variáveis de Ambiente

```powershell
# URL do OpenCode (padrão: http://localhost:11434/v1)
$env:OPENCODE_BASE_URL = "http://localhost:11434/v1"

# API Key (padrão: opencode-go)
$env:OPENCODE_API_KEY = "opencode-go"

# Modelo (padrão: qwen3.7-plus)
$env:OPENCODE_MODEL = "qwen3.7-plus"

# Timeout em segundos (padrão: 60)
$env:OPENCODE_TIMEOUT = "60"
```

### Arquivo .mcp.json

```json
{
  "mcpServers": {
    "lotoscope-agents": {
      "command": ".venv\\Scripts\\python.exe",
      "args": ["lotoscope_mcp_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "OPENCODE_BASE_URL": "http://localhost:11434/v1",
        "OPENCODE_API_KEY": "opencode-go"
      }
    }
  }
}
```

## Estrutura de Arquivos

```
LotoScope/
│
├── .github/agents/                    # Definições dos agentes
│   ├── lotoscope-coordinator.agent.md
│   ├── lotoscope-architect.agent.md
│   ├── lotoscope-analyst.agent.md
│   ├── pool23-generator.agent.md
│   ├── strategy-reviewer.agent.md
│   ├── lotoscope-dev.agent.md
│   └── docs-updater.agent.md
│
├── lotoscope_agents.py                # Orquestrador principal
├── lotoscope_mcp_server.py            # Servidor MCP
── mcp_client.py                      # Cliente MCP
│
├── agent-list.bat                     # Scripts .bat
├── agent-route.bat
├── agent-call.bat
├── agent-run.bat
├── start-opencode.bat                 # Inicia OpenCode
│
├── test_mcp_server.py                 # Teste MCP
├── test_opencode_integration.py       # Teste OpenCode
│
├── .mcp.json                          # Configuração MCP
├── AGENT_INTEGRATION.md               # Guia de integração
├── AGENT_ORCHESTRATOR.md              # Documentação orquestrador
├── SETUP_OPENCODE.md                  # Setup do OpenCode
── README_AGENT_SYSTEM.md             # Este arquivo
```

## Troubleshooting

### OpenCode não conecta
```powershell
# Verificar se está rodando
opencode status

# Verificar porta
netstat -ano | findstr "LISTENING"

# Reiniciar
opencode web
```

### Agente não aparece no Copilot
- Verifique arquivo `.agent.md` em `.github/agents/`
- Reinicie VS Code
- Verifique `.mcp.json`

### Erro de autenticação
```powershell
$env:OPENCODE_API_KEY = "opencode-go"
```

### Modelo não encontrado
```powershell
# Listar modelos
opencode models

# Configurar modelo
$env:OPENCODE_MODEL = "qwen3.7-plus"
```

## Exemplos Avançados

### Exemplo 1: Análise com Fallback Automático
```python
from lotoscope_agents import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Tenta resolver localmente primeiro
result = orchestrator.call_agent("analyst", "buscar últimos 10 concursos")

# Se precisar de interpretação, usa LLM
if result.get("status") == "needs_llm":
    result = orchestrator.call_agent("analyst", "interpretar padrões", use_llm=True)
```

### Exemplo 2: Delegação Direta
```python
# Delegar pergunta complexa
result = orchestrator.delegate_to_opencode(
    "Explique a diferença entre INVERTIDA v3.0 e SUPERÁVIT",
    context={"topic": "estratégias", "agent": "strategy"}
)

print(result["response"])
```

### Exemplo 3: Workflow Personalizado
```python
# Criar workflow customizado
custom_workflow = {
    "name": "Análise Completa",
    "steps": [
        {"agent": "analyst", "task": "Analisar dados"},
        {"agent": "strategy", "task": "Validar estratégia"},
        {"agent": "docs", "task": "Documentar resultados"}
    ]
}

# Executar
result = orchestrator.orchestrate_custom(custom_workflow)
```

## Performance

### Métricas Esperadas

| Operação | Tempo Médio |
|----------|-------------|
| Roteamento | <100ms |
| Tool local (SQL) | 100-500ms |
| Tool local (execute) | 500-2000ms |
| Chamada LLM (OpenCode) | 2000-10000ms |
| Workflow completo | 5000-30000ms |

### Otimizações

- **Cache de contexto**: Agentes mantêm histórico de conversa
- **Lazy loading**: Tools carregadas sob demanda
- **Connection pooling**: SQL reutiliza conexões
- **Timeout configurável**: Evita travamentos

## Segurança

### Boas Práticas

1. **SQL Parameters**: Sempre usar `?` para parâmetros
2. **Timeout**: Limitar tempo de execução
3. **Validação**: Verificar inputs do usuário
4. **Logs**: Registrar delegações para auditoria

### Restrições

- OpenCode roda localmente (sem envio para nuvem)
- SQL usa Windows Authentication
- Files limitados ao diretório do projeto
- Commands com timeout de 30 segundos

## Suporte

### Documentação

- `AGENT_INTEGRATION.md` - Guia de integração
- `SETUP_OPENCODE.md` - Setup do OpenCode
- `AGENT_ORCHESTRATOR.md` - Documentação orquestrador

### Testes

```powershell
# Testar MCP
python test_mcp_server.py

# Testar OpenCode
python test_opencode_integration.py

# Testar agentes
python lotoscope_agents.py list
```

### Logs

Os agentes registram:
- Delegações pendentes
- Erros de conexão
- Tempo de execução
- Histórico de conversas

---

**Versão**: 1.0.0  
**Última atualização**: 2026-06-04  
**Python**: 3.10+  
**OpenCode**: qwen3.7-plus
