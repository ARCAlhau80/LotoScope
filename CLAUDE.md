<!-- agent-graph-flow:start -->
## agent-graph-flow (`agf`) — LotoScope

Este projeto usa **agent-graph-flow** para gestão de execução via grafo persistente (SQLite).
Dados em `workflow-graph/graph.db` (local, gitignored). **Tudo via o CLI `agf` — zero MCP.**

### ⚠️ Regra de Execução OBRIGATÓRIA

**O grafo (`agf`) é a fonte de verdade ABSOLUTA. Nenhuma implementação acontece fora do grafo.**

1. **Node deve existir** — antes de escrever QUALQUER código, o node correspondente DEVE existir no grafo (`agf node add` ou `agf import-prd`).
2. **Fluxo obrigatório** — `agf start → [implementar com TDD] → agf done` (pipeline) ou `agf next → agf context <id> → [TDD] → agf check <id> → agf node status <id> done` (granular) — SEM EXCEÇÕES.
3. **Epic = estrutura primeiro** — `agf import-prd` (ou `agf node add` + `agf edge add`) cria Epic + tasks + edges ANTES de implementar.
4. **Status tracking** — `agf node status <id> in_progress` ANTES de codar, `agf node status <id> done` (ou `agf done <id>`) APÓS completar.
5. **Validação** — `agf check <id>` (DoD + AC + TDD) após cada task.
6. **Zero trabalho não-rastreado** — se não tem node no grafo, CRIAR PRIMEIRO.

> **Sem node no grafo = sem código escrito. Tudo via `agf` — zero MCP.**

### Comandos `agf` (CLI nativo — exponha 100%, zero MCP)

#### Front door (SHAPE → BUILD → SHIP)

| Comando | O que faz |
|---------|-----------|
| `agf deliver "<pedido>"` | Pipeline ponta-a-ponta: normaliza → PRD → grafo → build TDD |
| `agf import-prd <file>` | Importa PRD (.md/.txt/.pdf/.html/.docx) → grafo |
| `agf generate-prd "<ideia>"` | Gera PRD a partir de um prompt (via LLM) |
| `agf build` | Lifecycle completo: PRD → grafo → decompose → autopilot |
| `agf autopilot [--simulate|--live|--max <n>|--retries <n>]` | Loop autônomo: next → DoD → done|escalate |
| `agf loop --every <dur> <cmd> | --goal <rubric> --cmd <cmd>` | Loop por intervalo (--every) ou goal-driven (--goal) |
| `agf run "<prompt>"` | Execução one-shot: gera → aplica → testa |
| `agf exec` | Composição cross-platform de comandos agf |
| `agf exec pipe <command> [args...]` | Executa um comando agf e retorna o .data JSON |
| `agf exec chain "<cmd1>; <cmd2>; ..."` | Pipeline de comandos agf separados por ; |

#### Grafo — leitura

| Comando | O que faz |
|---------|-----------|
| `agf next` | Puxa a próxima task desbloqueada (pull, WIP=1) |
| `agf query [--type --status --parent --search --limit]` | Consulta nós por tipo/status/parent/texto |
| `agf node show <id>` | Detalhes de um nó + arestas de entrada/saída |
| `agf edge ls [--from <id>] [--to <id>]` | Lista arestas com filtros opcionais |
| `agf context <id> [--compressed]` | Context-pack compacto + RAG de um nó |
| `agf brief <id> [--format markdown|json|claude-prompt]` | Brief de execução p/ delegar ao executor |
| `agf search "<query>" [--limit <n>]` | Busca FTS5/BM25 sobre os nós do grafo |
| `agf retrieve-command "<intenção>" [--threshold <n>] [--limit <n>] [--local]` | RAG-IN: recupera o comando exato para uma intenção (fallback --help sob o limiar) |
| `agf montar-output "<objetivo>" [--threshold <n>] [--limit <n>]` | RAG-OUT: recupera scaffold adequado (preenche slots) ou gera, por objetivo |
| `agf stats` | Contagens e estatísticas: nodes, edges, byType, byStatus |
| `agf kanban [--swimlane]` | Board Kanban com swimlanes e métricas de fluxo |
| `agf insights` | Analítica determinística: DORA, gargalos, fases, fluxo |
| `agf insights dora` | Métricas DORA (deploy freq, lead time, CFR, MTTR, trend) |
| `agf insights bottlenecks` | Detecção de gargalos (bloqueadas, sem AC, oversized) |
| `agf insights phases` | Distribuição de tasks por fase do lifecycle |
| `agf insights wip` | Contagem de WIP + alerta de violação |
| `agf insights summary` | Resumo de fluxo: métricas + WIP + gargalos |
| `agf export [-o <file>]` | Serializa o grafo como JSON |

#### Grafo — mutação

| Comando | O que faz |
|---------|-----------|
| `agf node add --title <t> --type <t> [--parent <id> --status <s> --priority <n> --ac <c>]` | Cria um nó (task, epic, subtask, risk, etc.) |
| `agf node update <id> [--title --description --priority --type]` | Atualiza título, descrição, prioridade, tipo |
| `agf node status <id> <state> [--force]` | Muda status com validação status_flow |
| `agf node move <id> --parent <pid>` | Reparenta um nó sob novo pai |
| `agf node clone <id> [--parent <pid>]` | Clona um nó com seus atributos |
| `agf node rm <id>` | Remove um nó do grafo |
| `agf edge add <from> <to> [--type <t>] [--reason <r>]` | Cria relação (depends_on, blocks, parent_of…) |
| `agf edge rm <id>` | Remove uma aresta |
| `agf import-graph <file> [--dry-run]` | Funde um grafo JSON exportado no projeto |

#### Pipeline de task (2 calls)

| Comando | O que faz |
|---------|-----------|
| `agf start` | Inicia próxima task: wake-up + next + context + marca in_progress |
| `agf check <id>` | Definition of Done (12 checks) + aderência TDD |
| `agf done <id> [--skip-test]` | Finaliza: DoD + run tests + memória + done + sugere próxima |
| `agf pipeline` | Compound commands: múltiplas operações num único ciclo store |
| `agf pipeline next-context [--full] [-d dir]` | Find next task + load context (1 store open) |
| `agf pipeline next-start [--full] [-d dir]` | Find next + context + mark in_progress (1 store open) |
| `agf pipeline next-context-start [--full] [-d dir]` | Alias for next-start |

#### Decomposição & planejamento

| Comando | O que faz |
|---------|-----------|
| `agf decompose` | Detecta tasks grandes e sugere subtasks atômicas |
| `agf phase` | Taxonomia SHAPE→BUILD→SHIP + fase atual |
| `agf gate <design|review|handoff|deploy|listening|all>` | Gates de prontidão por fase do lifecycle |
| `agf template list` | Lista templates de decomposição disponíveis |
| `agf template apply <name>` | Aplica um template a um nó do grafo |
| `agf scaffold <nome> [--type class|fn|comp|iface|type]` | Scaffold/boilerplate determinístico (acoplador) |

#### Qualidade, harness, forecast

| Comando | O que faz |
|---------|-----------|
| `agf eval [--suite --models --provider --live --repeat --out]` | Suíte de cenários reais → scorecard |
| `agf harness [--violations]` | Scan de agent-readiness (8 dimensões, score A/B/C/D) |
| `agf hooks` | Inspeciona a taxonomia de 28 hooks (list/test/discover) |
| `agf hooks list` | Lista os 28 pontos: ponto → canal → módulo-owner |
| `agf hooks test <channel>` | Dry-fire de um canal com payload de fixture |
| `agf hooks discover` | Lista canais da taxonomia sem handler registrado |
| `agf code index` | Re-indexa o projeto (tree-sitter + LSP) |
| `agf code search <symbol>` | Busca semântica de símbolos via FTS5 |
| `agf code callers <symbol>` | Lista callers de um símbolo (incoming calls) |
| `agf code callees <symbol>` | Lista símbolos chamados (outgoing calls) |
| `agf code def <symbol>` | Go-to-definition via LSP |
| `agf code refs <symbol>` | Lista todas as referências via LSP |
| `agf code impact <file>` | Blast radius: símbolos afetados por mudança |
| `agf code affected <file>` | Testes afetados por mudanças no arquivo |
| `agf gaps [--kind --severity --limit --json]` | Detecta lacunas de completude (~0 token) |
| `agf scan-repos [root] [--report --ingest --json]` | Explora repos vizinhos: fingerprint + insights |
| `agf quality` | Gate 95/95 (testes + logs sobre src/) |
| `agf forecast` | Previsão de ETA do backlog com 95% CI |

#### Memória, snapshot, heal

| Comando | O que faz |
|---------|-----------|
| `agf memory write <name> [--content <c>|--file <f>]` | Escreve uma memória do projeto |
| `agf memory read <name>` | Lê uma memória do projeto |
| `agf memory list` | Lista todas as memórias do projeto |
| `agf memory rm <name>` | Remove uma memória do projeto |
| `agf memory search "<query>" [--limit <n>]` | Busca textual nas memórias do projeto |
| `agf snapshot create` | Cria um snapshot do grafo (backup) |
| `agf snapshot list` | Lista snapshots disponíveis |
| `agf snapshot restore <id>` | Restaura o grafo a partir de um snapshot |
| `agf heal [--apply] [--log]` | Self-healing do grafo (MAPE-K) |
| `agf gc` | Coleta de lixo (worktrees/branches órfãos) |

#### Modelo, métricas, custo

| Comando | O que faz |
|---------|-----------|
| `agf calibrate [--lever <name>] [--band <n>]` | Calibra o limiar do portão RAG por score×saved (lê o lever ledger) |
| `agf model list` | Lista tiers do tier-router (cheap/build/frontier/fallback) |
| `agf model current` | Mostra o modelo ativo configurado |
| `agf model set <id|auto>` | Fixa um modelo ou volta para auto |
| `agf model route <kind>` | Mostra qual modelo o tier-router usaria |
| `agf provider list` | Lista providers LLM disponíveis |
| `agf provider use <id> [--base-url <url>]` | Seleciona o provider ativo |
| `agf provider current` | Mostra provider ativo + fallback chain |
| `agf provider set-url [url]` | Define/limpa o endpoint do provider ativo |
| `agf provider failover [chain] [--clear]` | Configura cadeia de failover |
| `agf metrics [--session --baseline --simulate --economy-report]` | Tokens/$ por task e sessão (llm_call_ledger) |
| `agf compress <filters|discover|test>` | Compressor de saída de ferramenta |
| `agf compress filters` | Lista filtros de compressão ativos |
| `agf compress discover [--ledger]` | Saídas sem filtro registradas |
| `agf compress test <file>` | Testa qual filtro casaria com um arquivo |
| `agf rtk <filters|discover|test>` | Alias para agf compress |
| `agf savings [--reset]` | Economia cumulativa de tokens (ledger) |
| `agf retrieve <hash> [--query --limit]` | Resgata original CCR por hash |
| `agf learning stats` | Performance por-agente + routing |
| `agf learning route <agentId>` | Decisão de roteamento de agente baseada no histórico |
| `agf learning explain <agentId>` | Explica a decisão de roteamento (breakdown) |
| `agf learning export` | Exporta todos os registros de learning (JSON) |
| `agf status` | Painel unificado: provider/model/cache + tokens/$ |

#### Spec-kit & governança

| Comando | O que faz |
|---------|-----------|
| `agf adr create` | Cria um Architecture Decision Record no grafo |
| `agf adr list` | Lista ADRs existentes no grafo |
| `agf constitution` | Princípios governantes: --create|--list|--check |
| `agf preset --list|--show|--apply <name>` | Presets de workflow: --list|--show|--apply |
| `agf spec --generate|--validate|--list-templates` | Geração/validação de specs por fase |
| `agf spec-sync register` | Registra uma spec versionada |
| `agf spec-sync list` | Lista specs registradas |
| `agf spec-sync status` | Status de sync das specs |
| `agf spec-sync link <specId> <nodeId>` | Linka spec a um nó do grafo |
| `agf principles` | Doctrine: lista e exibe princípios |
| `agf plugin` | Gerencia plugins (--install, --remove, --list) |
| `agf profile` | Perfis de configuração (list, show) |

#### Dev tooling (test, lint, usage)

| Comando | O que faz |
|---------|-----------|
| `agf test [--blast|--changed|--file <path>|--node <id>]` | Vitest: --blast|--changed|--file|--node |
| `agf lint [--fix|--file <path>|--all]` | ESLint: --fix|--file|--all |
| `agf usage report [--top <n>]` | Top comandos usados + sugestão de wrappers |
| `agf usage wrap <command> [--apply]` | Auto-gera wrapper agf para comando nativo |

#### Setup & ambiente

| Comando | O que faz |
|---------|-----------|
| `agf init` | Inicializa o projeto: DB, gitignore, context files, docs |
| `agf doctor [--json --providers]` | Diagnóstico do ambiente + contexto LLM + drift detection |
| `agf daemon start [-p <port>]` | Inicia o serviço local em background |
| `agf daemon stop` | Para o serviço local deste workspace |
| `agf daemon status` | Verifica se o daemon está rodando |
| `agf daemon prune [--dry-run]` | Mata daemons órfãos + limpa state dirs |
| `agf daemon list` | Lista daemons e seus status |
| `agf login` | Autentica no GitHub Copilot (device-flow) |
| `agf logout` | Remove o token do GitHub Copilot |
| `agf skill list` | Lista skills do ciclo de vida |
| `agf skill show <name>` | Exibe o conteúdo de uma skill |
| `agf tui` | TUI interativa (Ink) — agf sem args num TTY |
| `agf ui [--port <n>]` | Web mínima de progresso: grafo + tokens + logs |

> Dev: `npm run dev -- <comando>`. Build: `agf` (binário) ou `agent-graph-flow`.
> `agf` sem args num TTY (com projeto) abre a TUI.

### Custo de token & providers (3º pilar)

**Providers** — `agf provider use <id>` escolhe por onde a chamada LLM vai. A *mesma* via CLI serve qualquer agente (Claude, Copilot, Codex, Cursor, Gemini…) — **nunca MCP**.
Todos os 10 providers são auto-detectados de env vars (`agf doctor --providers` lista quais estão configurados):

| Provider | Env var | Gateway |
|----------|---------|---------|
| `anthropic` | `ANTHROPIC_API_KEY` | auto-wired |
| `openai` | `OPENAI_API_KEY` | auto-wired |
| `openrouter` | `OPENROUTER_API_KEY` | auto-wired |
| `gemini` | `GEMINI_API_KEY` | auto-wired |
| `bedrock` | `BEDROCK_API_KEY` | auto-wired |
| `azure` | `AZURE_OPENAI_API_KEY` | auto-wired |
| `deepseek` | `DEEPSEEK_API_KEY` | auto-wired |
| `glm` | `GLM_API_KEY` | auto-wired |
| `kimi` | `KIMI_API_KEY` | auto-wired |
| `groq` | `GROQ_API_KEY` | auto-wired |
| `copilot` | (via `agf login`) | default |
| `ollama` | (local, <!-- mcp-graph:start -->
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
/token) | manual URL |

- **OpenRouter:** `export OPENROUTER_API_KEY=…` → `agf provider use openrouter`. Fixe um modelo com `--pin` (ex.: `agf deliver "…" --live --pin deepseek/deepseek-v4-flash`) ou deixe o tier-router escolher (cheap→`deepseek-v4-flash`, build→`llama-4-maverick`, frontier→`qwen3.6-plus`).

**Alavancas automáticas** (sem comando — agem no gateway): diff-edits (só a região alterada), repo-map ranqueado por PageRank (~1k tok), lossy-gate (auto-revert se a compressão quebra o sentido), AAAK, content-router (SmartCrusher p/ arrays JSON homogêneos + compressão AST de código), **CCR reversível** (cacheia o original + marcador ⟨ccr:hash⟩ → outcome `ccr_dropped`; resgate com `agf retrieve <hash>`), retry com feedback compacto. Cada economia entra no `llm_call_ledger`.

**Medir** (transformar a promessa em número):
- `agf metrics [--economy-report]` — tokens/$ por task e sessão + o que as alavancas pouparam.
- `agf metrics --simulate` — re-precifica a fatura real sob todos os modelos.
- `agf eval --models <ids> --live` — cenários reais → scorecard (resolve% × custo-por-sucesso).
- `agf savings` — economia cumulativa de tokens por task (ledger real, cached tokens contabilizados automaticamente).
- `agf savings --reset` — zera o contador cumulativo.

**Rastreabilidade** — cada chamada LLM é gravada no `llm_call_ledger` com `node_id` (atribuição por task), `cached_input_tokens`, `cost_usd` e `session_id`. O `agf done` registra automaticamente a economia da task. Use `agf doctor --providers` para ver quais providers estão configurados no ambiente.

### Harness de Completude — `agf gaps` (detect → delegate → verify)

`agf gaps` é determinístico (~0 token) e acha lacunas de completude no grafo: rastreabilidade
requirement→task→test, cobertura de AC na decomposição, AC sem testabilidade, NFR faltando,
edge-cases/erros ausentes, ambiguidade, atomicidade, design/estimate drift.

**A IA condutora (você — Copilot/Claude/Codex/Cursor/Gemini/OpenCode) fecha as lacunas**; o agf só
detecta e re-verifica. Cada gap traz `applyVia`: os comandos `agf` exatos pra fechá-lo.

**Loop:**
1. `agf gaps --severity required --json` — pega os blockers acionáveis.
2. Pra cada gap, rode o `applyVia` (ex.: `agf edge add --from <task> --to <req> --type implements`), escolhendo a semântica.
3. `agf gaps` de novo até `ready: true` — desfecho determinístico, independente de qual CLI fechou.

Filtros: `--kind <k>`, `--severity required|recommended`, `--limit N`, `--json` (relatório completo p/ loops).

### Brief de execução — delegando uma task ao executor

**Heurística:** _especifique a ponta e a saída; delegue o meio._ Onde o executor pode errar caro
(contrato, limites, incerteza) você gasta tokens preventivos baratos; o que ele faz bem sozinho
(escrever o código dentro das guardas) você deixa livre. "De outro mundo" não é um prompt mais longo —
é um que fecha as saídas de erro caras com o mínimo de palavras.

Gere o esqueleto pronto a partir do node: `agf brief <id>` (`--format markdown|json|claude-prompt`).
Ele auto-preenche o que o grafo sabe (intenção, AC, blast radius, deps, prontidão) e deixa os campos
de julgamento como `<fill: …>` pra você completar.

**Template:**
- **Intenção** (1 linha): para que existe / efeito desejado.
- **Tarefa** (atômica): uma só — node do grafo: `<id>`.
- **Imite:** arquivo-espelho a seguir como padrão.
- **Ler/tocar** (exato): caminhos + símbolos a reusar.
- **Contrato:** assinatura/tipos/comportamento (trechos pequenos **inline**; arquivos grandes → aponte o path).
- **AC** (testável): 2–4 critérios verificáveis.
- **NÃO:** refatorar vizinhos / deps novas / tocar X / mudar default.
- **Blast radius:** arquivos sensíveis → mudança aditiva.
- **Orçamento:** ~N arquivos, sem deps, sem hot-path.
- **Incerteza:** se o contrato falhar ou faltar info, PARE e reporte; se ambíguo, escolha e justifique em 1 linha.
- **Teste com:** fixture/stub concreto (ex.: `new Database(':memory:')`, stub da chamada LLM com contador) — evita setup flaky ou bater em auth que não existe no sandbox.
- **DoD:** typecheck · teste do arquivo · blast · lint.
- **Self-review antes de retornar** (~30 tokens, substitui um ciclo caro): sobrou placeholder? escopo vazou? AC cobertos? default intacto?
- **Retorne (schema):** `{arquivos[], testes{passed,failed}, desvios[]}` — sem dump de código; não commitar.

**Validação de retorno** — o condutor usa `parseExecutorResult(resposta)` para parsear o JSON estruturado
do executor (com fallback regex) e `validateBriefReady(brief)` para verificar que todos os campos de
julgamento (`imitate`, `readTouch`, `contract`, `testWith`) foram preenchidos antes de delegar.
Retorno inválido → rejeitar e pedir correção; válido → fechar o loop em 1 passo.

> Retorno estruturado torna a validação trivial (parse em vez de leitura). O condutor valida e fecha o loop; o executor escreve o meio.

### Fluxo de trabalho OBRIGATÓRIO

**Pipeline (2 calls):**
```bash
agf start                 # wake-up + next + context + marca in_progress
# … implementa com TDD (Red → Green → Refactor) …
agf done <id>             # DoD + memória + marca done + sugere próxima
```

**Granular (controle fino):**
```bash
agf next                  # puxa a próxima task (pull, WIP=1)
agf context <id>          # context-pack compact + RAG
# … TDD …
agf check <id>            # Definition of Done + aderência TDD
agf node status <id> done # transição validada (status_flow)
```

**Modo delegado (sem provider — qualquer CLI-agente dirige):** se nenhum provider
está conectado ao agf, os comandos `--live` (`agf run`/`agf deliver`/`agf autopilot --live`)
NÃO quebram — retornam `mode:delegated` com o brief pronto p/ VOCÊ (Claude/Copilot/Codex/…)
executar com seu próprio LLM. Feche o loop com `agf submit`:
```bash
agf next                  # próxima task
agf brief <id>            # spec de delegação (intenção, AC, contrato, blast)
# … você implementa com seu próprio LLM e aplica os edits …
agf submit <id> --result '{"arquivos":["x.ts"],"testes":{"passed":N,"failed":0},"desvios":[]}'
                          # valida → blast → DoD → done; desvios viram findings
```

### Lifecycle (9 fases) — comandos `agf` por fase

1. **ANALYZE** — `agf import-prd` · `agf node add` · `agf gate` (Definition of Ready)
2. **DESIGN** — `agf node add`/`agf edge add` (ADRs, interfaces) · `agf constitution` · `agf gate design`
3. **PLAN** — `agf decompose` · `agf template apply` · AC testável por task
4. **IMPLEMENT** — `agf start` → TDD → `agf done` (ou granular) · `agf harness`
5. **VALIDATE** — `agf check <id>` · `agf gate` · `agf metrics`
6. **REVIEW** — `agf export` · `agf insights` · `agf gate review`
7. **HANDOFF** — `agf memory write` · `agf snapshot create` · `agf gate handoff`
8. **DEPLOY** — `agf export` · `agf forecast` · `agf gate deploy` (harness ≥ 70)
9. **LISTENING** — `agf node add` · `agf import-prd` (novo ciclo)

### Índice de skills do ciclo (escolha a abordagem certa)

Qualquer CLI lê esta tabela pra escolher a skill certa pro intent atual — a coluna **Quando usar** mapeia situação → skill. Rode com `agf skill show <name>` ou siga o comando de entrada.

| Skill | Fase | Quando usar | Comando de entrada | Skills relacionadas |
|-------|------|-------------|--------------------|---------------------|
| `graph-prd` | ANALYZE | Start of a cycle with a vague idea | `agf generate-prd "<idea>"` | graph-analyze |
| `graph-analyze` | ANALYZE | PRD already imported | `agf import-prd <file>` | graph-prd, graph-design |
| `graph-design` | DESIGN | DoR approved | `agf context <id>` | graph-analyze, graph-plan |
| `graph-plan` | PLAN | DESIGN ready | `agf context <id>` | graph-design, graph-implement |
| `graph-implement` | IMPLEMENT | An unblocked task exists | `agf start` | graph-plan, graph-validate, graph-bugs |
| `graph-validate` | VALIDATE | ≥50% of tasks done with AC | `agf kanban` | graph-implement, graph-review |
| `graph-review` | REVIEW | VALIDATE complete | `agf insights` | graph-validate, graph-handoff |
| `graph-handoff` | HANDOFF | REVIEW approved | `agf memory write <name>` | graph-review, graph-deploy |
| `graph-deploy` | DEPLOY | HANDOFF approved | `agf provider use <id>` | graph-handoff, graph-listening |
| `graph-listening` | LISTENING | Post-deploy | `agf learning stats` | graph-deploy, graph-analyze |
| `graph-quality` | REVIEW | Code smells or accumulated debt | `agf quality` | graph-review, graph-validate |
| `graph-security` | REVIEW | Change touches authn/authz, external I/O or secrets | `agf check <id>` | graph-review, graph-deploy |
| `graph-bugs` | IMPLEMENT | Incorrect behavior observed | `agf node add --type bug` | graph-implement |
| `graph-platform` | VALIDATE | Delivery has a UI/platform surface | `agf harness` | graph-validate, graph-deploy |
| `graph-mega-brain` | ORCHESTRATION | Drive a PRD/feature end-to-end through the graph (ANALYZE→…→LISTENING) | `agf stats / agf query` | graph-lead, graph-implement, graph-validate |

### Definition of Done (rode `agf check <id>` antes de `agf done`)

| # | Check | Severidade |
|---|-------|------------|
| 1 | Tem acceptance criteria | required |
| 2 | Score AC ≥ 60 (INVEST) | required |
| 3 | Sem blockers não resolvidos | required |
| 4 | Status flow válido (passou por in_progress) | required |
| 5 | Tem descrição | recomendado |
| 6 | Não oversized (sem L/XL sem subtasks) | recomendado |
| 7 | ≥1 AC testável | recomendado |
| 8 | testFiles preenchido | recomendado |

### Princípios de Fluxo (Little's Law + Lean + TOC)

- **WIP = 1** — no máximo 1 task `in_progress`. `cycle_time = WIP / throughput`.
- **Pull, não Push** — `agf next` puxa; nunca empurrar para in_progress sem terminar a anterior.
- **Gargalo primeiro (TOC)** — se VALIDATE acumula, pare de implementar e valide.
- **Eliminar desperdício (Lean/Toyota)** — sem overproduction (features não planejadas), sem waiting (tasks blocked sem ação), use `agf context` (não dumps), TDD elimina defects.
- **Métricas de fluxo** — `agf insights` / `agf forecast`: cycle time, lead time, throughput, flow efficiency (> 40%).

### Princípios XP Anti-Vibe-Coding

- **TDD obrigatório** — Teste antes do código. Sem teste = sem implementação.
- **Anti-one-shot** — Nunca gere sistemas inteiros em um prompt. Decomponha em tasks atômicas (`agf decompose`).
- **Decomposição atômica** — Cada task completável em ≤2h.
- **Honestidade** — surfar pontas soltas como finding/risk no grafo (`agf node add --type risk`); nunca marcar done com alegação falsa.
- **CLAUDE.md como spec evolutiva** — documente padrões e decisões.

### Gates de Teste Hierárquicos

| Gate | Comando | Trigger |
|------|---------|---------|
| Task | `npm run test:blast` | a cada task finalizada (`agf done`) |
| Épico | `npm run test:node` | promoção de épico |
| PR | `npm test` | antes de push/PR |

Blast obrigatório no `agf done`. Full obrigatório pré-PR.

### Spec-Driven Development (spec-kit, via `agf`)

- `agf constitution` — princípios governantes (indexados, validados em gates).
- `agf preset --apply <name>` — workflow (default/strict-tdd/agile-light/enterprise).
- `agf spec --generate <template>` / `--validate <file>` — specs por fase.
- `agf spec-sync link <specId> <nodeId>` — specs vivas ligadas ao grafo.

### Memory ≠ Estado Atual

Memory files são snapshots point-in-time, não estado live. Contagens ("X/Y done") ficam stale.

1. Grep pelo arquivo/função — se existe, o memory é stale.
2. **Código vence memory.**
3. Reconcilie com `agf stats`/`agf query` antes de planejar.

> Nunca confiar em contagens de progresso de memories. Verificar no código/grafo primeiro.
### Contexto do Projeto

Stack detectada: node, typescript, react, vitest, python.

- **TypeScript**: Usar tipos estritos (`strict: true`). Evitar `any`. Tipar retornos de funções públicas.
- **React**: Componentes funcionais com hooks. Props tipadas via interfaces. Evitar `useEffect` com deps vazias. Testar com React Testing Library (RTL).
- **Testes (Vitest)**: Arquivos `*.test.ts`. Use `describe`/`it`/`expect`. Mock com `vi.fn()`. Blast: `npm run test:blast`.
- **Node.js**: ESM preferido (`"type": "module"`). Use `node:` prefix em imports built-in.
- **Python**: Type hints obrigatórias (`def foo(x: int) -> str`). Use `pytest` para testes. PEP 8.
- **Package Manager**: npm. Lockfile deve estar versionado.


> **Referência completa de comandos:** `agf help` (índice agrupado) · `agf <comando> --help` (flags) · `agf skill list` (skills do ciclo de vida).
<!-- agent-graph-flow:end -->


## agf JSON Output Contract

Every `agf` command returns a single-line JSON object to stdout:

```json
{"ok":true|false, "code":"string|null", "data":..., "error":"string|null", "meta":{"command":"string","ms":number,"count?":number}}
```

### Envelope fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | `true` = success, `false` = error |
| `code` | string | Machine-readable error code (present when `ok=false`) |
| `data` | any | Payload (present when `ok=true`; may also be present on `fail`) |
| `error` | string | Human-readable error message (present when `ok=false`) |
| `meta.command` | string | Always present — the command that produced this output |
| `meta.ms` | number | Duration in milliseconds |
| `meta.count` | number | Result count for list commands (optional) |

### Error codes

| Code | Meaning |
|------|---------|
| `ALL_BLOCKED` | Todas as tasks estão bloqueadas por dependências |
| `ALREADY_IMPORTED` | Arquivo já foi importado |
| `DOCTOR_ERROR` | Erro ao rodar diagnóstico |
| `DOCTOR_FAILED` | Checks críticos do ambiente falharam |
| `DOD_FAILED` | Definition of Done checks required failed |
| `EMPTY_EXTRACTION` | Nenhuma entidade extraída do arquivo |
| `GAPS_FOUND` | Completeness gaps detected |
| `GATE_FAILED` | Phase gate did not pass |
| `INIT_ERROR` | Erro durante inicialização |
| `INIT_FAILED` | Falha na inicialização do projeto |
| `INVALID_FORMAT` | Formato de saída inválido |
| `INVALID_KIND` | Tipo de tarefa inválido para roteamento |
| `INVALID_PORT` | Número de porta inválido |
| `INVALID_TRANSITION` | Transição de status inválida |
| `MISSING_ID` | Task ID não fornecido |
| `NOT_FOUND` | Recurso não encontrado (nó, aresta, memória, etc.) |
| `NO_SCENARIOS` | Nenhum cenário de eval encontrado |
| `NO_TASKS` | Nenhuma task disponível para puxar |
| `PARSE_ERROR` | Falha ao parsear arquivo |
| `STORE_OPEN_FAILED` | Falha ao abrir o store do projeto |
| `UNKNOWN_KIND` | Kind de gap desconhecido |
| `UNKNOWN_MODEL` | Modelo desconhecido |
| `UNKNOWN_PHASE` | Fase de gate desconhecida |
| `UNKNOWN_PROVIDER` | Provider desconhecido |
| `UNKNOWN_SEVERITY` | Severity de gap desconhecida |

### Command output schemas

| Command | Args | `ok:true` → `data` shape | Error codes |
|---------|------|---------------------------|-------------|
| `agf stats` | [-d dir] | `{totalNodes, totalEdges, byType, byStatus}` | — |
| `agf next` | [-d dir] | `{node: GraphNode, reason, warning?}` | `NO_TASKS`, `ALL_BLOCKED` |
| `agf query` | [--type] [--status] [--parent] [--search] [--limit] [-d dir] | `GraphNode[]` | — |
| `agf search` | <query> [--limit] [-d dir] | `SearchResult[]` | — |
| `agf check` | <nodeId> [-d dir] | `{dod: {ready,score,grade,checks}, tdd}` | `NOT_FOUND`, `DOD_FAILED` |
| `agf node add` | --title [--type] [--parent] [--status] [--priority] [--ac] [-d dir] | `{id, type, status, title}` | — |
| `agf node show` | <id> [-d dir] | `{node: GraphNode, outEdges, incEdges}` | `NOT_FOUND` |
| `agf node update` | <id> [--title] [--description] [--priority] [--type] [-d dir] | `{id, updated}` | `NOT_FOUND` |
| `agf node status` | <id> <state> [--force] [-d dir] | `{id, from, to}` | `NOT_FOUND`, `INVALID_TRANSITION` |
| `agf node move` | <id> --parent <pid> [-d dir] | `{id, parent}` | `NOT_FOUND` |
| `agf node clone` | <id> [--parent] [-d dir] | `{source, clone}` | `NOT_FOUND` |
| `agf node rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge add` | <from> <to> [--type] [--reason] [-d dir] | `{id, from, to, relationType}` | `NOT_FOUND` |
| `agf edge rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge ls` | [--from] [--to] [-d dir] | `GraphEdge[]` | — |
| `agf context` | <id> [--compressed] [-d dir] | `TaskContext` | `NOT_FOUND` |
| `agf brief` | <id> [--format markdown|json|claude-prompt] [-d dir] | `ExecutorBrief | {markdown} | {prompt}` | `NOT_FOUND`, `INVALID_FORMAT` |
| `agf export` | [-o file] [-d dir] | `{path?,nodeCount,edgeCount} | GraphDocument` | — |
| `agf import-prd` | <file> [--force] [--allow-empty] [-d dir] | `{nodes, edges, source}` | `ALREADY_IMPORTED`, `EMPTY_EXTRACTION`, `PARSE_ERROR` |
| `agf start` | [-d dir] | `{taskId, title, context}` | `NO_TASKS` |
| `agf done` | <taskId> [-d dir] | `{taskId, dodScore, dodGrade, savings, next?}` | `NOT_FOUND`, `MISSING_ID`, `DOD_FAILED` |
| `agf status` | [-d dir] | `StatusReport | {project:null}` | — |
| `agf metrics` | [-d dir] [--session] [--baseline|--simulate|--economy-report] | `{totals, byTask, bySession, costPerSuccess, ...}` | — |
| `agf forecast` | [-d dir] | `DoraMetrics` | — |
| `agf insights` | <dora|bottlenecks|phases|summary> [-d dir] | `DoraMetrics | BottleneckReport | PhaseDistribution[] | MetricsReport` | — |
| `agf kanban` | [-d dir] [--swimlane] | `{board: KanbanBoard, ledger}` | — |
| `agf harness` | [-d dir] [--violations] | `HarnessScanResult` | — |
| `agf gaps` | [-d dir] [--kind] [--severity] [--history] | `GapReport | {history}` | `UNKNOWN_KIND`, `UNKNOWN_SEVERITY`, `GAPS_FOUND` |
| `agf eval` | [--suite] [--model] [--models] [--live] [--repeat] [--out] | `{scorecard, simulate, mode, totalRuns}` | `NO_SCENARIOS` |
| `agf gate` | <phase> [-d dir] | `{phases: [{phase, report}], anyFail}` | `UNKNOWN_PHASE`, `GATE_FAILED` |
| `agf doctor` | [-d dir] [--providers] | `{checks?, providers?, llmContext?}` | `DOCTOR_FAILED`, `DOCTOR_ERROR` |
| `agf init` | [-d dir] [--name] [--port] [--skip-neural] [--no-serve] | `{success, serveStarted, port?, nextSteps[]}` | `INVALID_PORT`, `INIT_FAILED`, `INIT_ERROR` |
| `agf quality` | [-d dir] [--min-tests] [--min-logs] | `{totalModules, testScore, logScore, thresholds, gatePassed}` | `GATE_FAILED` |
| `agf model list` |  | `{mode, tiers}` | — |
| `agf model current` | [-d dir] | `{mode, modelId}` | — |
| `agf model set` | <idOrAuto> [-d dir] | `{mode, modelId}` | `UNKNOWN_MODEL` |
| `agf model route` | <kind> [-d dir] | `{kind, model}` | `INVALID_KIND` |
| `agf provider list` |  | `{providers[]}` | — |
| `agf provider use` | <id> [--base-url] [-d dir] | `{provider, baseUrl, requiresKey, envVar?}` | `UNKNOWN_PROVIDER` |
| `agf provider current` | [-d dir] | `{provider, kind, baseURL?, fallback?}` | — |
| `agf provider failover` | [chain] [--clear] [-d dir] | `{failover: string[] | null}` | `UNKNOWN_PROVIDER` |
| `agf memory write` | <name> [--content|--file] [-d dir] | `{name, bytes}` | — |
| `agf memory read` | <name> [-d dir] | `{name, content}` | `NOT_FOUND` |
| `agf memory list` | [-d dir] | `string[]` | — |
| `agf memory rm` | <name> [-d dir] | `{name, removed}` | `NOT_FOUND` |
| `agf memory search` | <query> [-d dir] [--limit] | `SearchResult[]` | — |
| `agf snapshot create` | [-d dir] | `{snapshotId}` | — |
| `agf snapshot list` | [-d dir] | `Snapshot[]` | — |
| `agf snapshot restore` | <id> [-d dir] | `{nodesValid, edgesRestored}` | — |
| `agf exec pipe` | <command> [args...] | `data do envelope do comando interno` | — |
| `agf exec chain` | "<cmd1>; <cmd2>; ..." | `{results: [{command, ok, data}]}` | — |
| `agf pipeline next-context` | [--full] [-d dir] | `{node: {id,title,status,priority}, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-context-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf compress` | [filters | discover | test <file>] | `{filters[]} | {misses[]} | {filter, before, after, savedPct}` | — |
| `agf code` | <index|search|callers|callees|def|refs|impact|affected> [target] [-d dir] | `CodeIntelResult` | — |
| `agf savings` | [--reset] [-d dir] | `{tasks[], totals, pricing, backlogCount, projectedCost, commands?, economyBlock?, globalTotals?}` | — |
| `agf retrieve` | <hash> [--query] [--limit] [-d dir] | `{hash, original} | {hash, query, matches[]}` | `NOT_FOUND` |

### Decision logic for consumers

```
if (!envelope.ok) {
  switch (envelope.code) {
    case "DOD_FAILED":
    case "GAPS_FOUND":
      // envelope.data contains detailed check results
      // fix issues and retry
      break
    case "NOT_FOUND":
      // resource does not exist
      break
    case "NO_TASKS":
      // no work available — stand by
      break
    default:
      // handle unknown error
  }
}
// On success: process envelope.data
```

### Consuming output cheaply (token + memory discipline)

`agf` stdout is always **minified JSON**; logs are NDJSON on **stderr** — parse stdout only. Consume the smallest slice you need:

- **Project fields with `--select`** (no external `jq`; ~80–90% fewer tokens): `agf next --select data.node.id,data.node.title`. Works in any position, always keeps `ok`/`code`/`error`/`meta`, and an invalid path falls back to the full envelope (never errors).
- **Use `--profile <name>`** for agent-aware presets (claude-code, copilot, opencode, minimal): automatically selects the right fields per command. `--select` wins over `--profile` when both are provided.
- **`--pretty`** only for human debugging (indented JSON).
- **Compose natively with `agf exec`** (cross-platform, no shell): `agf exec pipe next` returns the inner `.data`; `agf exec chain "next; check <id>"` runs a sequence.
- **Pipe further when needed** — POSIX: `agf query --status ready | jq -c '.data[].title'`; PowerShell: `agf query --status ready | ConvertFrom-Json | Select-Object -Expand data`.
- **Large output → temp file, then filter** (OS temp dir — `/tmp` on POSIX, `%TEMP%` on Windows; in code use `os.tmpdir()`): `agf export -o "$TMPDIR/g.json" && jq -c '.data.nodes[] | {id,title}' "$TMPDIR/g.json"`.
- **Sweep big structures with short async one-liners** (`node -e "..."`) rather than long scripts — decide what to keep, deterministically.
- **`agf compress`** is for compressing OTHER tools' output (grep/test/build) — never wrap `agf` itself; it is already minimal.
- **Scaffold-decide:** pick a scaffold from `github.com` or locally via `agf scaffold`, filter/cache, return — never dump whole repos.

Runs identically on Windows, macOS, and Linux — the native `--select` / `agf exec` path needs no shell.

> **Fundamentação:** minified JSON + field projection is the recommended agent-CLI pattern (Anthropic "Effective context engineering"; GitHub "token efficiency in agentic workflows") — returning only the needed fields cuts input tokens ~80–90%.

## agf JSON Output Contract

Every `agf` command returns a single-line JSON object to stdout:

```json
{"ok":true|false, "code":"string|null", "data":..., "error":"string|null", "meta":{"command":"string","ms":number,"count?":number}}
```

### Envelope fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | `true` = success, `false` = error |
| `code` | string | Machine-readable error code (present when `ok=false`) |
| `data` | any | Payload (present when `ok=true`; may also be present on `fail`) |
| `error` | string | Human-readable error message (present when `ok=false`) |
| `meta.command` | string | Always present — the command that produced this output |
| `meta.ms` | number | Duration in milliseconds |
| `meta.count` | number | Result count for list commands (optional) |

### Error codes

| Code | Meaning |
|------|---------|
| `ALL_BLOCKED` | Todas as tasks estão bloqueadas por dependências |
| `ALREADY_IMPORTED` | Arquivo já foi importado |
| `DOCTOR_ERROR` | Erro ao rodar diagnóstico |
| `DOCTOR_FAILED` | Checks críticos do ambiente falharam |
| `DOD_FAILED` | Definition of Done checks required failed |
| `EMPTY_EXTRACTION` | Nenhuma entidade extraída do arquivo |
| `GAPS_FOUND` | Completeness gaps detected |
| `GATE_FAILED` | Phase gate did not pass |
| `INIT_ERROR` | Erro durante inicialização |
| `INIT_FAILED` | Falha na inicialização do projeto |
| `INVALID_FORMAT` | Formato de saída inválido |
| `INVALID_KIND` | Tipo de tarefa inválido para roteamento |
| `INVALID_PORT` | Número de porta inválido |
| `INVALID_TRANSITION` | Transição de status inválida |
| `MISSING_ID` | Task ID não fornecido |
| `NOT_FOUND` | Recurso não encontrado (nó, aresta, memória, etc.) |
| `NO_SCENARIOS` | Nenhum cenário de eval encontrado |
| `NO_TASKS` | Nenhuma task disponível para puxar |
| `PARSE_ERROR` | Falha ao parsear arquivo |
| `STORE_OPEN_FAILED` | Falha ao abrir o store do projeto |
| `UNKNOWN_KIND` | Kind de gap desconhecido |
| `UNKNOWN_MODEL` | Modelo desconhecido |
| `UNKNOWN_PHASE` | Fase de gate desconhecida |
| `UNKNOWN_PROVIDER` | Provider desconhecido |
| `UNKNOWN_SEVERITY` | Severity de gap desconhecida |

### Command output schemas

| Command | Args | `ok:true` → `data` shape | Error codes |
|---------|------|---------------------------|-------------|
| `agf stats` | [-d dir] | `{totalNodes, totalEdges, byType, byStatus}` | — |
| `agf next` | [-d dir] | `{node: GraphNode, reason, warning?}` | `NO_TASKS`, `ALL_BLOCKED` |
| `agf query` | [--type] [--status] [--parent] [--search] [--limit] [-d dir] | `GraphNode[]` | — |
| `agf search` | <query> [--limit] [-d dir] | `SearchResult[]` | — |
| `agf check` | <nodeId> [-d dir] | `{dod: {ready,score,grade,checks}, tdd}` | `NOT_FOUND`, `DOD_FAILED` |
| `agf node add` | --title [--type] [--parent] [--status] [--priority] [--ac] [-d dir] | `{id, type, status, title}` | — |
| `agf node show` | <id> [-d dir] | `{node: GraphNode, outEdges, incEdges}` | `NOT_FOUND` |
| `agf node update` | <id> [--title] [--description] [--priority] [--type] [-d dir] | `{id, updated}` | `NOT_FOUND` |
| `agf node status` | <id> <state> [--force] [-d dir] | `{id, from, to}` | `NOT_FOUND`, `INVALID_TRANSITION` |
| `agf node move` | <id> --parent <pid> [-d dir] | `{id, parent}` | `NOT_FOUND` |
| `agf node clone` | <id> [--parent] [-d dir] | `{source, clone}` | `NOT_FOUND` |
| `agf node rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge add` | <from> <to> [--type] [--reason] [-d dir] | `{id, from, to, relationType}` | `NOT_FOUND` |
| `agf edge rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge ls` | [--from] [--to] [-d dir] | `GraphEdge[]` | — |
| `agf context` | <id> [--compressed] [-d dir] | `TaskContext` | `NOT_FOUND` |
| `agf brief` | <id> [--format markdown|json|claude-prompt] [-d dir] | `ExecutorBrief | {markdown} | {prompt}` | `NOT_FOUND`, `INVALID_FORMAT` |
| `agf export` | [-o file] [-d dir] | `{path?,nodeCount,edgeCount} | GraphDocument` | — |
| `agf import-prd` | <file> [--force] [--allow-empty] [-d dir] | `{nodes, edges, source}` | `ALREADY_IMPORTED`, `EMPTY_EXTRACTION`, `PARSE_ERROR` |
| `agf start` | [-d dir] | `{taskId, title, context}` | `NO_TASKS` |
| `agf done` | <taskId> [-d dir] | `{taskId, dodScore, dodGrade, savings, next?}` | `NOT_FOUND`, `MISSING_ID`, `DOD_FAILED` |
| `agf status` | [-d dir] | `StatusReport | {project:null}` | — |
| `agf metrics` | [-d dir] [--session] [--baseline|--simulate|--economy-report] | `{totals, byTask, bySession, costPerSuccess, ...}` | — |
| `agf forecast` | [-d dir] | `DoraMetrics` | — |
| `agf insights` | <dora|bottlenecks|phases|summary> [-d dir] | `DoraMetrics | BottleneckReport | PhaseDistribution[] | MetricsReport` | — |
| `agf kanban` | [-d dir] [--swimlane] | `{board: KanbanBoard, ledger}` | — |
| `agf harness` | [-d dir] [--violations] | `HarnessScanResult` | — |
| `agf gaps` | [-d dir] [--kind] [--severity] [--history] | `GapReport | {history}` | `UNKNOWN_KIND`, `UNKNOWN_SEVERITY`, `GAPS_FOUND` |
| `agf eval` | [--suite] [--model] [--models] [--live] [--repeat] [--out] | `{scorecard, simulate, mode, totalRuns}` | `NO_SCENARIOS` |
| `agf gate` | <phase> [-d dir] | `{phases: [{phase, report}], anyFail}` | `UNKNOWN_PHASE`, `GATE_FAILED` |
| `agf doctor` | [-d dir] [--providers] | `{checks?, providers?, llmContext?}` | `DOCTOR_FAILED`, `DOCTOR_ERROR` |
| `agf init` | [-d dir] [--name] [--port] [--skip-neural] [--no-serve] | `{success, serveStarted, port?, nextSteps[]}` | `INVALID_PORT`, `INIT_FAILED`, `INIT_ERROR` |
| `agf quality` | [-d dir] [--min-tests] [--min-logs] | `{totalModules, testScore, logScore, thresholds, gatePassed}` | `GATE_FAILED` |
| `agf model list` |  | `{mode, tiers}` | — |
| `agf model current` | [-d dir] | `{mode, modelId}` | — |
| `agf model set` | <idOrAuto> [-d dir] | `{mode, modelId}` | `UNKNOWN_MODEL` |
| `agf model route` | <kind> [-d dir] | `{kind, model}` | `INVALID_KIND` |
| `agf provider list` |  | `{providers[]}` | — |
| `agf provider use` | <id> [--base-url] [-d dir] | `{provider, baseUrl, requiresKey, envVar?}` | `UNKNOWN_PROVIDER` |
| `agf provider current` | [-d dir] | `{provider, kind, baseURL?, fallback?}` | — |
| `agf provider failover` | [chain] [--clear] [-d dir] | `{failover: string[] | null}` | `UNKNOWN_PROVIDER` |
| `agf memory write` | <name> [--content|--file] [-d dir] | `{name, bytes}` | — |
| `agf memory read` | <name> [-d dir] | `{name, content}` | `NOT_FOUND` |
| `agf memory list` | [-d dir] | `string[]` | — |
| `agf memory rm` | <name> [-d dir] | `{name, removed}` | `NOT_FOUND` |
| `agf memory search` | <query> [-d dir] [--limit] | `SearchResult[]` | — |
| `agf snapshot create` | [-d dir] | `{snapshotId}` | — |
| `agf snapshot list` | [-d dir] | `Snapshot[]` | — |
| `agf snapshot restore` | <id> [-d dir] | `{nodesValid, edgesRestored}` | — |
| `agf exec pipe` | <command> [args...] | `data do envelope do comando interno` | — |
| `agf exec chain` | "<cmd1>; <cmd2>; ..." | `{results: [{command, ok, data}]}` | — |
| `agf pipeline next-context` | [--full] [-d dir] | `{node: {id,title,status,priority}, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-context-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf compress` | [filters | discover | test <file>] | `{filters[]} | {misses[]} | {filter, before, after, savedPct}` | — |
| `agf code` | <index|search|callers|callees|def|refs|impact|affected> [target] [-d dir] | `CodeIntelResult` | — |
| `agf savings` | [--reset] [-d dir] | `{tasks[], totals, pricing, backlogCount, projectedCost, commands?, economyBlock?, globalTotals?}` | — |
| `agf retrieve` | <hash> [--query] [--limit] [-d dir] | `{hash, original} | {hash, query, matches[]}` | `NOT_FOUND` |

### Decision logic for consumers

```
if (!envelope.ok) {
  switch (envelope.code) {
    case "DOD_FAILED":
    case "GAPS_FOUND":
      // envelope.data contains detailed check results
      // fix issues and retry
      break
    case "NOT_FOUND":
      // resource does not exist
      break
    case "NO_TASKS":
      // no work available — stand by
      break
    default:
      // handle unknown error
  }
}
// On success: process envelope.data
```

### Consuming output cheaply (token + memory discipline)

`agf` stdout is always **minified JSON**; logs are NDJSON on **stderr** — parse stdout only. Consume the smallest slice you need:

- **Project fields with `--select`** (no external `jq`; ~80–90% fewer tokens): `agf next --select data.node.id,data.node.title`. Works in any position, always keeps `ok`/`code`/`error`/`meta`, and an invalid path falls back to the full envelope (never errors).
- **Use `--profile <name>`** for agent-aware presets (claude-code, copilot, opencode, minimal): automatically selects the right fields per command. `--select` wins over `--profile` when both are provided.
- **`--pretty`** only for human debugging (indented JSON).
- **Compose natively with `agf exec`** (cross-platform, no shell): `agf exec pipe next` returns the inner `.data`; `agf exec chain "next; check <id>"` runs a sequence.
- **Pipe further when needed** — POSIX: `agf query --status ready | jq -c '.data[].title'`; PowerShell: `agf query --status ready | ConvertFrom-Json | Select-Object -Expand data`.
- **Large output → temp file, then filter** (OS temp dir — `/tmp` on POSIX, `%TEMP%` on Windows; in code use `os.tmpdir()`): `agf export -o "$TMPDIR/g.json" && jq -c '.data.nodes[] | {id,title}' "$TMPDIR/g.json"`.
- **Sweep big structures with short async one-liners** (`node -e "..."`) rather than long scripts — decide what to keep, deterministically.
- **`agf compress`** is for compressing OTHER tools' output (grep/test/build) — never wrap `agf` itself; it is already minimal.
- **Scaffold-decide:** pick a scaffold from `github.com` or locally via `agf scaffold`, filter/cache, return — never dump whole repos.

Runs identically on Windows, macOS, and Linux — the native `--select` / `agf exec` path needs no shell.

> **Fundamentação:** minified JSON + field projection is the recommended agent-CLI pattern (Anthropic "Effective context engineering"; GitHub "token efficiency in agentic workflows") — returning only the needed fields cuts input tokens ~80–90%.
