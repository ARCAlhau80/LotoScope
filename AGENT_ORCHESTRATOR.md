# LotoScope Agent Orchestrator

Sistema de orquestração de agentes para o LotoScope. Permite que o opencode chame os agentes e que os agentes chamem o opencode.

## Agentes Disponíveis

| ID | Nome | Função |
|----|------|--------|
| `coordinator` | LotoScope Coordinator | Ponto de entrada, roteia para outros agentes |
| `architect` | LotoScope Architect | Guardião da arquitetura e regras de negócio |
| `analyst` | LotoScope Analyst | Análise estatística, frequências, backtests |
| `pool23` | Pool 23 Generator | Geração de combinações Pool 23 (Opção 31) |
| `strategy` | Strategy Reviewer | Validação e comparação de estratégias, ROI |
| `dev` | LotoScope Dev | Implementação e correção de código |
| `docs` | Docs Updater | Manutenção da documentação |

## Uso via CLI

### Listar agentes
```powershell
python lotoscope_agents.py list
# ou
.\agent-list.bat
```

### Roteamento automático
```powershell
python lotoscope_agents.py route "analisar o concurso 3643"
# ou
.\agent-route.bat "analisar o concurso 3643"
```

### Chamar agente específico
```powershell
python lotoscope_agents.py call analyst "verificar frequências dos últimos 30 concursos"
# ou
.\agent-call.bat analyst "verificar frequências dos últimos 30 concursos"
```

### Executar workflow
```powershell
python lotoscope_agents.py orchestrate pos_sorteio
# ou
.\agent-run.bat pos_sorteio
```

## Workflows Pré-definidos

| ID | Nome | Descrição |
|----|------|-----------|
| `pos_sorteio` | Pós-Sorteio | Analisa resultados e calcula ROI |
| `preparacao` | Preparação | Analisa tendências e gera combinações |
| `nova_feature` | Nova Feature | Implementa com validação completa |
| `investigacao_bug` | Investigação Bug | Diagnostica e corrige bugs |

## Uso com OpenCode

Para usar os agentes durante interações com o opencode:

1. **Chamar agente diretamente:**
   ```
   Use o agente analyst para verificar as frequências dos últimos 30 concursos
   ```

2. **Roteamento automático:**
   ```
   Qual agente devo usar para gerar combinações?
   ```

3. **Orquestração:**
   ```
   Execute o workflow pos_sorteio para o concurso 3700
   ```

## Delegação Bidirecional

Os agentes podem delegar tarefas de volta ao opencode:

```python
from lotoscope_agents import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = orchestrator.delegate_to_opencode(
    request="Executar query SQL para buscar últimos concursos",
    context={"tabela": "Resultados_INT", "limite": 30}
)
```

## Estrutura de Arquivos

```
LotoScope/
├── lotoscope_agents.py          # Orquestrador principal
├── agent-list.bat               # Script para listar agentes
├── agent-route.bat              # Script para roteamento
├── agent-call.bat               # Script para chamar agente
├── agent-run.bat                # Script para workflow
└── .github/agents/              # Definições dos agentes
    ├── lotoscope-coordinator.agent.md
    ├── lotoscope-architect.agent.md
    ├── lotoscope-analyst.agent.md
    ├── pool23-generator.agent.md
    ├── strategy-reviewer.agent.md
    ├── lotoscope-dev.agent.md
    └── docs-updater.agent.md
```

## Integração com MCP (Futuro)

Quando o projeto migrar para Python 3.10+, será possível usar o MCP server:

```json
{
  "mcpServers": {
    "lotoscope-agents": {
      "command": "python",
      "args": ["lotoscope_mcp_server.py"]
    }
  }
}
```
