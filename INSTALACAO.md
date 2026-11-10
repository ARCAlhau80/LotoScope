# LotoScope — Guia de Instalação e Implantação

> Documento de instalação do sistema completo: banco SQL Server, ambiente Python,
> dashboard Next.js, atualização de resultados, fechamento combinatório, IA e
> ferramentas opcionais. Foi escrito para permitir reconstruir o ambiente do zero.

---

## 1. Visão geral

O LotoScope é composto por quatro camadas:

```
┌──────────────────────────────────────────────────────────────┐
│  Dashboard Next.js (dashboard/)                              │
│  UI + API routes (/api/*) — porta 3003 (dev) / 3000 (prod)   │
└───────────────▲──────────────────────────────┬───────────────┘
                │ mssql (SQL Server)           │ execSync python
┌───────────────┴──────────────┐   ┌───────────▼───────────────┐
│  SQL Server — LOTOFACIL      │   │  Python (raiz + shared/ +  │
│  resultados, ciclos,         │   │  lotofacil_lite/)          │
│  combinações, acertos        │   │  atualização, análises, IA │
└──────────────────────────────┘   └───────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│  Ferramentas opcionais                                       │
│  covergen (.NET) · Ollama/OpenRouter · MCP/OpenCode          │
└──────────────────────────────────────────────────────────────┘
```

| Camada | Tecnologia | Obrigatória? |
|---|---|---|
| Dashboard | Next.js 15 + React 19 + Tailwind | Sim (UI principal) |
| Banco | SQL Server 2019+ | Sim |
| Análises/atualização | Python 3.10+ | Sim |
| Fechamento/covergen | .NET 10 SDK | Opcional (covers já versionados) |
| IA/Chat | Ollama ou OpenRouter/OpenAI/Google | Opcional |
| MCP/OpenCode | Node/uvx | Opcional (desenvolvimento) |

---

## 2. Requisitos

### 2.1 Obrigatórios

| Item | Versão mínima | Observação |
|---|---|---|
| Windows | 10/11 | Caminhos e scripts `.bat`/`.ps1` são para Windows; Linux/macOS exigem adaptação |
| SQL Server | 2019+ (Express serve) | Banco `LOTOFACIL` |
| ODBC Driver 17 for SQL Server | 17.x | Usado pelo `pyodbc` |
| Python | 3.10+ (recomendado 3.11/3.12) | `pyodbc`, `numpy`, `scipy` etc. |
| Node.js | 20+ | Next.js 15 |
| npm | 10+ | Vem com o Node |
| Git | 2.x | Para clonar o repositório |

### 2.2 Opcionais

| Item | Uso |
|---|---|
| .NET SDK 10 | `tools/covergen` (gerar covers além do registry) |
| Ollama | Chat/IA local (`OLLAMA_MODEL`) |
| Chave OpenRouter/OpenAI/Google | Chat/IA em nuvem |
| `ngrok` | Exposição externa para testes (`start_external.ps1`) |
| `uvx`/`npx` | Servidores MCP (Context7, Playwright, Serena, mcp-graph) |

### 2.3 Portas

| Porta | Serviço |
|---:|---|
| 1433 | SQL Server |
| 3003 | Dashboard em desenvolvimento (`npm run dev`) |
| 3000 | Dashboard em produção (`npm start`) e MCP Graph |
| 11434 | Ollama |
| 8111 | OpenCode Proxy (`opencode_proxy.py`, opcional) |

---

## 3. Estrutura do repositório

| Caminho | Função |
|---|---|
| `dashboard/` | Dashboard Next.js (UI + API). Ver `dashboard/src/lib/lottery-config.ts` |
| `shared/` | Atualizadores das loterias (`shared/loterias/`) e conexão (`shared/database.py`) |
| `lotofacil_lite/` | CLI, geradores, analisadores e configuração de banco legada |
| `sql/` | Scripts de instalação do banco (este guia) |
| `tools/covergen/` | Gerador de covering designs em .NET |
| `tests/` | Testes Python (covers, fechamento, apostador, etc.) |
| `ia_lotoscope.py` | Análise consolidada via IA/LLM usada pelo dashboard |
| `lotoscope_mcp_server.py` | Servidor MCP dos agentes LotoScope |
| `dados/` | Saídas de análises e históricos (parcialmente ignorado pelo Git) |
| `web/` | Interface Flask legada (não é o dashboard principal) |

---

## 4. Banco de dados

### 4.1 Criar o banco e as tabelas

Há duas formas: manual (`sqlcmd`) ou pelo SQL Server Management Studio (SSMS).

**Manual (PowerShell):**

```powershell
cd C:\caminho\LotoScope

# Autenticação Windows
sqlcmd -S localhost -E -i sql\01_core_tables.sql

# Autenticação SQL (se usar usuário/senha)
sqlcmd -S localhost -U sa -P "SUA_SENHA" -i sql\01_core_tables.sql
```

O script `sql/01_core_tables.sql`:

- cria o banco `LOTOFACIL` se não existir;
- cria as tabelas essenciais de forma **idempotente** (`IF OBJECT_ID ... IS NULL`);
- cria os índices principais.

Depois, aplique procedures/triggers:

```powershell
sqlcmd -S localhost -E -i sql\03_procedures_triggers.sql
```

> `sql/03_procedures_triggers.sql` usa `CREATE OR ALTER` (SQL Server 2016+).
> Se usar SQL Server 2014 ou anterior, troque por `DROP` + `CREATE`.

Opcionalmente, crie a tabela de 20 dezenas:

```powershell
sqlcmd -S localhost -E -i sql\02_opcional_combinacoes_20.sql
```

### 4.2 Tabelas essenciais

| Tabela | Conteúdo | Observação |
|---|---|---|
| `Resultados_INT` | Sorteios da Lotofácil + 60 colunas estatísticas | Fonte principal do dashboard |
| `NumerosCiclos` | Ciclos por número (7 colunas) | Necessária para Ciclos/Heatmap |
| `COMBINACOES_LOTOFACIL` | 3.268.760 combinações de 15 dezenas + acertos | Necessária para o Ranking; pesada |
| `COMBINACOES_LOTOFACIL20_COMPLETO` | 53.130 combinações de 20 dezenas + estatísticas | Recursos legados/avançados |
| `Resultados_MegaSenaFechado` | Sorteios da Mega-Sena | Aba Mega-Sena |
| `COMBIN_MEGASENA` | 50.063.860 combinações de 6 dezenas | Ranking Mega; muito pesada |
| `NumerosCiclosMega` | Ciclos da Mega-Sena | Aba Mega-Sena |
| `Resultados_Quina`, `Resultados_DuplaSena`, `Resultados_Lotomania`, `Resultados_DiaDeSorte`, `Resultados_Timemania`, `Resultados_SuperSete`, `Resultados_MaisMilionaria` | Resultados das demais loterias | Abas multi-loteria |
| `NumerosCiclos_Lotomania` | Ciclos da Lotomania | Aba Lotomania |

**Importante — conflito de `NumerosCiclos`:** o `lotofacil_lite/utils/setup_banco.py`
cria uma versão **diferente** de `NumerosCiclos` (25 linhas, colunas
`UltimoSorteio/CicloAtual/Urgencia/MediaCiclo`). O dashboard espera a versão de
**7 colunas** (`Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento,
DataInicio, DataFim`). Rode `sql/01_core_tables.sql` **antes** de qualquer
`setup_banco.py`, ou simplesmente não rode o `setup_banco.py` no mesmo banco.

### 4.3 Tabelas opcionais/legadas

O banco de referência do projeto contém dezenas de tabelas legadas
(`COMBIN_10`, `10_combin`, `Combinacoes_BemSucedidas`, `Padroes_Detectados`,
`Previsoes_*`, `AprendizadoControle`, etc.). Elas **não são necessárias** para o
dashboard principal. Recursos específicos podem exigi-las; nesse caso, importe
do backup ou gere pelos scripts correspondentes.

### 4.4 Configuração de conexão

O projeto tem **três pontos de conexão**:

#### a) Python — `shared/database.py`

```python
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=VADER;"          # troque para localhost, .\SQLEXPRESS ou o IP
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;" # autenticação Windows
    ...
)
```

#### b) Python — `lotofacil_lite/utils/database_config.py`

```python
def __init__(self, server: str = "VADER",
             database: str = "LOTOFACIL",
             driver: str = "ODBC Driver 17 for SQL Server"):
```

É essa configuração que os **atualizadores** (`shared/loterias/atualizador_base.py`)
usam. Ajuste `server` e `database` para o seu ambiente.

#### c) Dashboard — `dashboard/.env.local`

Copie `dashboard/.env.example` para `dashboard/.env.local` e preencha:

```env
DB_SERVER=localhost
DB_NAME=LOTOFACIL
DB_USER=sa
DB_PASSWORD=SUA_SENHA

AI_PROVIDER=openrouter
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=google/gemini-2.5-pro
OLLAMA_MODEL=
```

Se `DB_USER`/`DB_PASSWORD` não forem definidos, `dashboard/src/lib/database.ts`
usa `sa` / `LotoScope@2024` como padrão. **Não use esse padrão em produção.**

Para autenticação Windows no dashboard, o driver `mssql` precisa de
`options.trustedConnection: true` e de `user`/`password` ausentes. O código atual
passa usuário/senha sempre; a forma mais simples é criar um login SQL dedicado.

### 4.5 Carga inicial de resultados

Com o banco e as tabelas criados:

```powershell
.\.venv\Scripts\Activate.ps1
python atualizar_todas.py
```

Ou apenas Lotofácil:

```powershell
python atualizar_lotofacil_auto.py
```

Os atualizadores consultam a API pública da Caixa
(`https://servicebus2.caixa.gov.br/portaldeloterias/api/...`) e fazem upsert nas
tabelas `Resultados_*`.

Após um truncate/reimport manual de `Resultados_INT`, recompute os campos
posicionais:

```powershell
python pos_carga_resultados_int.py
```

**Carga histórica em lote (importante):** os triggers de acertos em
`Resultados_INT` atualizam as tabelas de combinações a cada INSERT. Em uma carga
grande, desative-os antes e reative depois:

```sql
DISABLE TRIGGER trg_AtualizarAcertos_LF15_AfterInsert ON dbo.Resultados_INT;
DISABLE TRIGGER trg_AtualizarAcertos_AfterInsert ON dbo.Resultados_INT;
-- ... importe os concursos ...
ENABLE TRIGGER trg_AtualizarAcertos_LF15_AfterInsert ON dbo.Resultados_INT;
ENABLE TRIGGER trg_AtualizarAcertos_AfterInsert ON dbo.Resultados_INT;
-- Recalcule uma vez:
EXEC dbo.sp_AtualizarAcertos_LF15;
EXEC dbo.sp_AtualizarAcertos;
```

### 4.6 Combinações e acertos (opcional/pesado)

- `COMBINACOES_LOTOFACIL` (3,27M linhas): importe de backup ou popule com o
  gerador legado. Sem ela, a seção **Ranking de Combinações** não funciona.
- `COMBINACOES_LOTOFACIL20_COMPLETO` (53.130 linhas): pode ser gerada por
  `gerador_completo_20.py` (CSV) e importada; os acertos são calculados por
  `calcular_acertos_inicial.py` / `atualizar_acertos_completo.py`.
- `COMBINACOES_LOTOFACIL20` (53.130 linhas): opcional; use
  `sql/02_opcional_combinacoes_20.sql` e `gerador_combinacoes_20.py`.
- `COMBIN_MEGASENA` (50M linhas): muito pesada; crie apenas se for usar o
  ranking da Mega-Sena.

---

## 5. Ambiente Python

```powershell
cd C:\caminho\LotoScope
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> `requirements.txt` inclui `ortools` (usado pelo CP-SAT do fechamento). O
> `pyproject.toml` não lista `ortools`; por isso prefira `requirements.txt`.

Teste a conexão:

```powershell
python -c "from shared.database import get_optimized_connection; c=get_optimized_connection(); print('OK' if c else 'FALHOU')"
```

### 5.1 Comandos úteis

| Comando | Função |
|---|---|
| `python atualizar_todas.py` | Atualiza todas as loterias |
| `python atualizar_lotofacil_auto.py` | Atualiza só a Lotofácil (tarefa agendada) |
| `python pos_carga_resultados_int.py` | Recalcula campos posicionais |
| `python ia_lotoscope.py --json --no-save --no-context` | Análise consolidada (usada pelo dashboard) |
| `python lotofacil_lite/interfaces/super_menu.py` | Menu CLI legado |
| `python gerador_combinacoes_20.py` | Gera/popula combinações de 20 dezenas |
| `python atualizar_acertos_completo.py` | Atualiza acertos incrementais |
| `python calcular_acertos_inicial.py` | Cálculo inicial de acertos (uma vez) |

### 5.2 Tarefa agendada (opcional)

O script `atualizar_lotofacil_auto.py` foi feito para o Agendador de Tarefas do
Windows (sugestão: diariamente às 21:45). Ele grava
`atualizacao_auto_lotofacil.log` na raiz.

---

## 6. Dashboard Next.js

```powershell
cd dashboard
npm install
Copy-Item .env.example .env.local
# edite .env.local com DB_SERVER/DB_NAME/DB_USER/DB_PASSWORD e IA
npm run dev
```

Acesse `http://localhost:3003`.

Para produção:

```powershell
npm run build
npm start
```

O script `start` usa a porta **3000** (`next start --port 3000`). O `dev` usa
**3003**.

### 6.1 Observações

- O dashboard fala com o SQL Server **pelo servidor Next.js**; o navegador não
  acessa o banco diretamente.
- A rota `/api/ai-analysis` executa `python ia_lotoscope.py` via `execSync`.
  Ative a `.venv` antes de subir o dashboard para que o `python` do PATH seja o
  da venv (ou ajuste a rota para `.venv\Scripts\python.exe`).
- A rota `/api/chat` tenta Ollama (`OLLAMA_MODEL`) e, se falhar, usa
  `OPENROUTER_API_KEY`.
- Scripts prontos: `start-dashboard-next.bat`, `start.bat` (Ollama + dashboard),
  `start-dashboard.bat`.

---

## 7. Fechamento combinatório / covers

O dashboard já inclui o registry `dashboard/src/data/covers-lotofacil.json`
(covers C(25,15,t) para t=3..12, incluindo C(25,15,5)=42 e C(24,14,4)=23).
Para usar o fechamento, nenhuma instalação extra é necessária.

Para gerar covers novos:

```powershell
cd tools\covergen
dotnet run -c Release -- --t 9  --pool 50000  --out ..\..\c9.json
dotnet run -c Release -- --t 10 --pool 40000  --out ..\..\c10.json
```

Requisito: .NET SDK 10 (o `covergen.csproj` tem `net10.0`). Se tiver outro SDK,
ajuste `TargetFramework` no `.csproj`.

Para importar covers do La Jolla/Zenodo (download de ~4,19 GB):

```powershell
python dashboard/scripts/import_zenodo_covers.py --dry-run
python dashboard/scripts/import_zenodo_covers.py
```

Teste de integridade dos covers:

```powershell
pytest tests\test_covers_lotofacil.py -q
# covers grandes (t>=9):
$env:LOTOSCOPE_SLOW="1"; pytest tests\test_covers_lotofacil.py -q
```

---

## 8. IA / LLM

### 8.1 Ollama (local)

```powershell
# instale o Ollama e baixe um modelo
ollama pull gpt-oss:20b

# suba o servidor (porta 11434)
ollama serve
```

No `.env.local`:

```env
OLLAMA_MODEL=gpt-oss:20b
```

### 8.2 OpenRouter / OpenAI / Google

```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=google/gemini-2.5-pro

# ou
# AI_PROVIDER=openai
# OPENAI_API_KEY=...
# OPENAI_MODEL=gpt-4o

# ou
# AI_PROVIDER=google
# GOOGLE_API_KEY=...
# GOOGLE_MODEL=gemini-2.5-pro
```

O chat tenta Ollama primeiro quando `OLLAMA_MODEL` está definido; se não
responder, cai para o provedor configurado.

---

## 9. MCP / OpenCode (opcional)

Arquivos: `.mcp.json` (clientes MCP) e `opencode.json` (OpenCode).

- `lotoscope-agents` usa `.venv\Scripts\python.exe lotoscope_mcp_server.py`.
- `mcp-graph` roda via `npx -y @mcp-graph-workflow/mcp-graph`.
- `context7`, `playwright`, `serena` são opcionais.
- `start-mcp-graph.bat` sobe o dashboard do mcp-graph na porta 3000.
- `start-proxy.bat` sobe `opencode_proxy.py` na porta 8111.

Teste dos agentes:

```powershell
python lotoscope_agents.py opencode-status
python lotoscope_agents.py call analyst "verificar frequências"
python lotoscope_agents.py call-llm analyst "analisar padrões dos últimos 30 concursos"
```

---

## 10. Instalação rápida (checklist)

```text
[ ] 1. Instalar SQL Server + ODBC Driver 17
[ ] 2. git clone https://github.com/ARCAlhau80/LotoScope.git
[ ] 3. python -m venv .venv && .\.venv\Scripts\Activate.ps1
[ ] 4. pip install -r requirements.txt
[ ] 5. Editar shared/database.py e lotofacil_lite/utils/database_config.py
[ ] 6. sqlcmd -S localhost -E -i sql\01_core_tables.sql
[ ] 7. sqlcmd -S localhost -E -i sql\03_procedures_triggers.sql
[ ] 8. python atualizar_todas.py  (ou atualizar_lotofacil_auto.py)
[ ] 9. cd dashboard && npm install
[ ]10. Copy-Item .env.example .env.local  (editar DB e IA)
[ ]11. npm run dev  → http://localhost:3003
[ ]12. (Opcional) Ollama + OLLAMA_MODEL, covers, MCP
```

---

## 11. Testes e validação

```powershell
# Python — covers (não exige banco)
pytest tests\test_covers_lotofacil.py -q

# Python — fechamento/CP-SAT (exige ortools; alguns exigem banco)
pytest tests\test_fechamento_combinatorio.py -q
pytest tests\test_cp_sat_fechamento.py -q

# TypeScript
cd dashboard
npx tsc --noEmit
npm run build
```

Smoke tests manuais:

1. Abra `http://localhost:3003`.
2. Verifique se o concurso atual e as abas carregam.
3. Teste `/api/dashboard-data?loteria=lotofacil`.
4. Gere um fechamento com t=5 e confira a cobertura.
5. Se usar IA, envie uma mensagem no chat.

---

## 12. Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ODBC Driver 17 for SQL Server` não encontrado | Driver não instalado | Instale o MS ODBC Driver 17 |
| `Login failed for user 'sa'` | Autenticação SQL desabilitada/senha errada | Habilite mixed mode ou use autenticação Windows |
| `Cannot open database "LOTOFACIL"` | Banco não criado/sem permissão | Rode `sql/01_core_tables.sql`; conceda acesso |
| `Invalid object name 'Resultados_INT'` | Tabelas não criadas | Rode `sql/01_core_tables.sql` |
| `Invalid column name 'Ciclo'` em `NumerosCiclos` | Versão de 25 linhas do `setup_banco.py` | Recrie a tabela de 7 colunas (`sql/01`) |
| `EADDRINUSE :::3003` | Porta ocupada | `netstat -ano \| findstr 3003` e finalize o PID, ou troque a porta |
| `Cannot find module 'mssql'` | `npm install` não rodou | `cd dashboard && npm install` |
| `next build` estoura memória | Build grande | `$env:NODE_OPTIONS="--max-old-space-size=4096"` |
| Ollama offline | Servidor não iniciado | `ollama serve` ou configure OpenRouter |
| `401` no chat | Chave inválida | Revise `OPENROUTER_API_KEY` |
| `pyodbc` não instala | Falta build tools/ODBC | Instale Visual C++ Build Tools e o driver ODBC |
| Covers `t>=9` lentos | Verificação exaustiva | Use `LOTOSCOPE_SLOW=1` só quando necessário |
| `covergen` falha no build | SDK .NET diferente de 10 | Instale .NET 10 ou ajuste `TargetFramework` |
| Consultas em `COMBINACOES_LOTOFACIL` lentas | Tabela de 3,2M linhas | Use `TOP`, filtros indexados e evite `SELECT *` |

### 12.1 Erros de encoding

O dashboard define `PYTHONIOENCODING=utf-8` para a rota de IA. Em execuções
manuais no PowerShell:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

---

## 13. Segurança

- **Nunca comite** `dashboard/.env.local`, chaves de API ou senhas.
- Em produção, **não use** o usuário `sa`; crie um login dedicado com permissões
  apenas no banco `LOTOFACIL`.
- O dashboard **não tem autenticação**. A exposição via ngrok
  (`start_external.ps1`) é apenas para testes controlados; pare o túnel depois.
- Faça backup do banco antes de rodar scripts que fazem `DROP`/`TRUNCATE`.
- Os scripts `criar_tabela_combinacoes_20.sql` e `gerador_combinacoes_20.py`
  **recriam** `COMBINACOES_LOTOFACIL20`; use `sql/02_opcional_combinacoes_20.sql`
  se quiser apenas criar sem apagar.

---

## 14. Apêndice — arquivos SQL existentes

| Arquivo | Uso |
|---|---|
| `sql/01_core_tables.sql` | **Novo** — banco + tabelas essenciais (idempotente) |
| `sql/02_opcional_combinacoes_20.sql` | **Novo** — tabela opcional de 20 dezenas |
| `sql/03_procedures_triggers.sql` | **Novo** — procedures/triggers essenciais |
| `shared/loterias/sql_criar_tabelas.sql` | Versão simples das tabelas de resultados (alternativa) |
| `adicionar_colunas_acertos_lotofacil15.sql` | Colunas de acertos em `COMBINACOES_LOTOFACIL` |
| `adicionar_colunas_acertos_10.sql` | Colunas `Acertos_10` em `COMBINACOES_LOTOFACIL` |
| `adicionar_colunas_acertos.sql` | Colunas de acertos em `COMBINACOES_LOTOFACIL20_COMPLETO` |
| `adicionar_colunas_ultimo_acerto.sql` | Colunas de último acerto em `COMBINACOES_LOTOFACIL20_COMPLETO` |
| `criar_procedure_trigger_lotofacil15.sql` | Proc/trigger de acertos em `COMBINACOES_LOTOFACIL` |
| `criar_procedure_atualizar_acertos.sql` | Proc de acertos em `COMBINACOES_LOTOFACIL20_COMPLETO` |
| `criar_trigger_atualizar_acertos.sql` | Trigger de acertos em `COMBINACOES_LOTOFACIL20_COMPLETO` |
| `criar_tabela_combinacoes_20.sql` | Cria/recria `COMBINACOES_LOTOFACIL20` (cuidado: `DROP`) |

### 14.1 Endpoints principais do dashboard

| Rota | Função |
|---|---|
| `/api/dashboard-data` | Análise completa da loteria |
| `/api/janela-alvo` | Números e ocorrências dos X concursos anteriores ao concurso alvo |
| `/api/jogos-diversos` | Gerador diversificado |
| `/api/fechamento` | Fechamento combinatório |
| `/api/fechamento/backtest` | Backtest do fechamento |
| `/api/ranking-combinacoes` | Ranking de combinações |
| `/api/resultado-concurso` | Resultado de um concurso |
| `/api/analise-grupos` | Análise de grupos |
| `/api/reentradas` | Reentradas |
| `/api/ai-analysis` | Análise via `ia_lotoscope.py` |
| `/api/chat` | Chat com Ollama/OpenRouter |
| `/api/apostador/parse` | Parse de apostas |
| `/api/generate-supersete` | Gerador Super Sete |

---

## 15. Referências internas

- `README.md` — visão geral e estratégias validadas.
- `CONTEXTO_MASTER_IA.md` — contexto histórico e conclusões científicas.
- `REFERENCIA_TECNICA_IA.md` — referência técnica dos módulos de IA.
- `QUICK_START_IA.md` — início rápido da IA.
- `SETUP_OPENCODE.md` — integração com OpenCode.
- `GUIA-EXPOSICAO.md` — exposição externa via ngrok.
- `tools/covergen/README.md` — gerador de covers.
- `lotofacil_lite/README.md` — CLI legado.
- `dashboard/src/lib/lottery-config.ts` — mapeamento de tabelas por loteria.
- `dashboard/src/lib/database.ts` — conexão e queries do dashboard.

---

*Última atualização: 2026-11-10.*
