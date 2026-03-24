<!-- mcp-graph:start -->
## mcp-graph — LotoScope

Este projeto usa **mcp-graph** para gestão de execução via grafo persistente (SQLite).
Dados armazenados em `workflow-graph/graph.db` (local, gitignored).

### Ferramentas MCP disponíveis (26 tools)

| Tool | Quando usar |
|------|-------------|
| `init` | Inicializar grafo do projeto |
| `import_prd` | Importar PRD (texto/markdown) para o grafo |
| `list` | Listar nodes do grafo (filtrar por tipo/status) |
| `show` | Ver detalhes de um node específico |
| `next` | Próxima task recomendada (prioridade + dependências) |
| `context` | Contexto comprimido da task (token-efficient) |
| `update_status` | Mudar status de um node (backlog→ready→in_progress→done) |
| `add_node` | Criar node manualmente |
| `update_node` | Atualizar campos de um node |
| `delete_node` | Remover node do grafo |
| `edge` | Criar/remover relações entre nodes |
| `dependencies` | Analisar cadeia de dependências |
| `decompose` | Detectar tasks grandes e sugerir decomposição |
| `search` | Busca full-text no grafo (FTS5 + BM25) |
| `rag_context` | Contexto RAG com knowledge base |
| `plan_sprint` | Gerar relatório de planejamento de sprint |
| `velocity` | Métricas de velocidade por sprint |
| `stats` | Estatísticas gerais do grafo |
| `export` | Exportar grafo (JSON ou Mermaid) |
| `snapshot` | Criar/restaurar snapshots do grafo |
| `move_node` | Mover node para outro parent |
| `clone_node` | Clonar node com filhos |
| `bulk_update_status` | Atualizar status de múltiplos nodes |
| `sync_stack_docs` | Sincronizar docs das libs do projeto |
| `reindex_knowledge` | Reindexar knowledge store |
| `validate_task` | Validar task com browser (Playwright) |

### Fluxo de trabalho recomendado

```
next → context → [implementar com TDD] → update_status → next
```

### Lifecycle (8 fases)

1. **ANALYZE** — Criar PRD, definir requisitos (`import_prd`, `add_node`)
2. **DESIGN** — Arquitetura, decisões técnicas (`add_node`, `edge`, `decompose`)
3. **PLAN** — Sprint planning, decomposição (`plan_sprint`, `decompose`, `sync_stack_docs`)
4. **IMPLEMENT** — TDD Red→Green→Refactor (`next`, `context`, `update_status`)
5. **VALIDATE** — Testes E2E, critérios de aceitação (`validate_task`, `velocity`)
6. **REVIEW** — Code review, blast radius (`export`, `stats`)
7. **HANDOFF** — PR, documentação, entrega (`export`, `snapshot`)
8. **LISTENING** — Feedback, novo ciclo (`add_node`, `import_prd`)

### Princípios XP Anti-Vibe-Coding

- **TDD obrigatório** — Teste antes do código. Sem teste = sem implementação.
- **Anti-one-shot** — Nunca gere sistemas inteiros em um prompt. Decomponha em tasks atômicas.
- **Decomposição atômica** — Cada task deve ser completável em ≤2h.
- **Code detachment** — Se a IA errou, explique o erro via prompt. Nunca edite manualmente.
- **CLAUDE.md como spec evolutiva** — Documente padrões e decisões aqui.

### Comandos essenciais

```powershell
# Iniciar dashboard (Windows)
.\start-mcp-graph.bat
# ou: $env:Path = "C:\Program Files\nodejs;" + $env:Path; npx -y @mcp-graph-workflow/mcp-graph serve --port 3000

# Estatísticas do grafo
npx mcp-graph stats

# Listar nodes
npx mcp-graph list

# Importar novo PRD
npx mcp-graph import <arquivo.md>
```

**Dashboard**: http://localhost:3000
<!-- mcp-graph:end -->
