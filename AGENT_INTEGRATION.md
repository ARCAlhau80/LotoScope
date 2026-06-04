# LotoScope Agent Integration - Guia Completo

##  Visão Geral

Sistema de agentes integrado entre **GitHub Copilot** e **OpenCode** via MCP server.

```
─────────────────────────────────────────────────────────────┐
│                    FLUXO DE INTEGRAÇÃO                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Usuário → @Agente X (Copilot)                              │
│       ↓                                                     │
│  Agente recebe comando via .agent.md                        │
│       ↓                                                     │
│  Agente executa via MCP tools                               │
│       ↓                                                     │
│  ┌────────────────────────────────────────┐                 │
│  │  Agente sabe resolver?                 │                 │
│  │  SIM → Executa e retorna resultado     │                 │
│  │  NÃO → lotoscope_delegate → OpenCode   │                 │
│  └────────────────────────────────────────┘                 │
│       ↓                                                     │
│  OpenCode executa e retorna                                 │
│       ↓                                                     │
│  Agente retorna ao usuário                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Agentes Disponíveis

| ID | Nome | Quando usar |
|----|------|-------------|
| `coordinator` | LotoScope Coordinator | Não sabe qual agente usar, tarefas complexas multi-agente |
| `architect` | LotoScope Architect | Arquitetura, regras de negócio, validação de design |
| `analyst` | LotoScope Analyst | Análise estatística, frequências, backtests, padrões |
| `pool23` | Pool 23 Generator | Gerar combinações Pool 23 (Opção 31) |
| `strategy` | Strategy Reviewer | Comparar ROI, validar estratégias, benchmark |
| `dev` | LotoScope Dev | Implementar features, corrigir bugs, código |
| `docs` | Docs Updater | Atualizar documentação, registrar resultados |

##  Como Usar no Copilot

### 1. Selecionar Agente

No chat do Copilot, digite `@` e selecione o agente:

```
@LotoScope Analyst analise o concurso 3700
@Pool 23 Generator gere combinações nível 3
@LotoScope Dev corrija o bug na opção 30.2
```

### 2. Agente Executa via MCP

O agente automaticamente usa as tools MCP:

```python
# Exemplo: Analyst executando análise
await session.call_tool("lotoscope_query_database", {
    "query": "SELECT TOP 10 * FROM Resultados_INT ORDER BY Concurso DESC"
})
```

### 3. Delegação Automática ao OpenCode

Se o agente não souber resolver:

```python
# Agente chama OpenCode automaticamente
await session.call_tool("lotoscope_delegate", {
    "request": "Executar backtest completo dos últimos 50 concursos",
    "context": {"concurso": 3700, "nivel": 3},
    "agent_id": "analyst"
})
```

## 🔧 MCP Tools Disponíveis

### Tools de Agente

| Tool | Função |
|------|--------|
| `lotoscope_list_agents` | Lista agentes disponíveis |
| `lotoscope_list_workflows` | Lista workflows |
| `lotoscope_route` | Roteia request para agente apropriado |
| `lotoscope_call_agent` | Chama agente específico |
| `lotoscope_get_context` | Obtém contexto do agente |
| `lotoscope_orchestrate` | Executa workflow multi-agente |

### Tools de Delegação

| Tool | Função |
|------|--------|
| `lotoscope_delegate` | Delega tarefa ao OpenCode |
| `lotoscope_check_delegation` | Verifica delegações pendentes |

### Tools de Execução

| Tool | Função |
|------|--------|
| `lotoscope_execute_command` | Executa comando Python/PowerShell |
| `lotoscope_query_database` | Executa query SQL no banco Lotofacil |

## 📊 Workflows Pré-definidos

### pos_sorteio (Pós-Sorteio)
```
Analyst → Strategy → Docs
```
Analisa resultados, calcula ROI, registra nos docs.

### preparacao (Preparação)
```
Analyst → Architect → Pool23 → Strategy
```
Analisa tendências, valida anomalias, gera combinações, confirma nível.

### nova_feature (Nova Feature)
```
Architect → Dev → Analyst → Docs
```
Valida design, implementa, testa com backtest, documenta.

### investigacao_bug (Bug Fix)
```
Dev → Architect → Docs
```
Diagnostica, valida correção, registra fix.

## 💻 Uso via Terminal

### Scripts .bat (rápido)
```powershell
.\agent-list.bat                              # Lista agentes
.\agent-route.bat "analisar concurso 3700"   # Roteia automaticamente
.\agent-call.bat analyst "verificar frequências"  # Chama agente
.\agent-run.bat pos_sorteio                  # Executa workflow
```

### Via MCP Client
```powershell
python mcp_client.py list
python mcp_client.py route "gerar combinacoes"
python mcp_client.py call pool23 "gerar nivel 3"
python mcp_client.py orchestrate pos_sorteio
```

## 🔐 Configuração MCP

O servidor MCP está configurado em `.mcp.json`:

```json
{
  "mcpServers": {
    "lotoscope-agents": {
      "command": ".venv\\Scripts\\python.exe",
      "args": ["lotoscope_mcp_server.py"],
      "env": {"PYTHONPATH": "."}
    }
  }
}
```

## 📁 Estrutura de Arquivos

```
LotoScope/
├── .github/agents/                    # Definições dos agentes (Copilot lê aqui)
│   ├── lotoscope-coordinator.agent.md
│   ├── lotoscope-architect.agent.md
│   ├── lotoscope-analyst.agent.md
│   ├── pool23-generator.agent.md
│   ├── strategy-reviewer.agent.md
│   ├── lotoscope-dev.agent.md
│   └── docs-updater.agent.md
│
├── lotoscope_agents.py                # Orquestrador CLI
├── lotoscope_mcp_server.py            # Servidor MCP
├── mcp_client.py                      # Cliente MCP para terminal
│
├── agent-list.bat                     # Scripts .bat
├── agent-route.bat
├── agent-call.bat
├── agent-run.bat
│
└── .mcp.json                          # Configuração MCP
```

## 🎓 Exemplos de Uso

### Exemplo 1: Análise Simples
```
Usuário: @LotoScope Analyst verifique as frequências dos últimos 30 concursos

Agente Analyst:
1. Usa lotoscope_query_database para buscar dados
2. Calcula frequências
3. Retorna resultado
```

### Exemplo 2: Geração com Delegação
```
Usuário: @Pool 23 Generator gere combinações nível 3 e valide com backtest

Agente Pool23:
1. Gera combinações via super_menu.py
2. Tenta validar com backtest
3. Se não souber → lotoscope_delegate → OpenCode
4. OpenCode executa backtest
5. Agente retorna resultado completo
```

### Exemplo 3: Workflow Multi-Agente
```
Usuário: @LotoScope Coordinator prepare para o próximo concurso

Coordinator:
1. lotoscope_orchestrate("preparacao")
2. Analyst analisa tendências
3. Architect valida anomalias
4. Pool23 gera combinações
5. Strategy confirma nível
6. Retorna resultado consolidado
```

##  Troubleshooting

### Agente não aparece no Copilot
- Verifique se arquivo `.agent.md` está em `.github/agents/`
- Reinicie o VS Code

### MCP server não conecta
- Verifique se `.venv` tem Python 3.10+
- Execute: `.\.venv\Scripts\python.exe lotoscope_mcp_server.py`

### Delegação não funciona
- Verifique se OpenCode está rodando
- Use `lotoscope_check_delegation` para ver pendências

##  Documentação dos Agentes

Cada agente tem seu arquivo `.agent.md` com:
- System prompt completo
- Keywords para roteamento
- Tools disponíveis
- Workflow específico

Leia os arquivos em `.github/agents/` para detalhes de cada agente.
