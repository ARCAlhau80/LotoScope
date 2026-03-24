# 🛠️ TECH STACK — LotoScope

**Propósito:** SSOT (Single Source of Truth) para todas as dependências  
**Atualizado:** 24/03/2026

---

## 📦 Stack Atual

### Linguagem & Runtime
```
Language:       Python 3.11+
Runtime:        CPython 3.11 (Windows 11)
Package Mgr:    pip + uv (com .venv virtual environment)
Venv:           .venv\Scripts\Activate.ps1
```

### Framework Principal
```
Framework:      sem framework web ativo (Flask disponível mas não em uso regular)
ORM/ODM:        sem ORM — queries pyodbc diretas
API Style:      CLI (super_menu.py) + opcionalmente Flask REST
Auth:           Trusted Connection (Windows Auth para SQL Server)
```

### Banco de Dados
```
Primary DB:     SQL Server 2019 (localhost, Windows Auth)
Database:       Lotofacil
Tabela Main:    Resultados_INT (~3.640 concursos)
Tabela Combos:  COMBINACOES_LOTOFACIL (3.2M registros)
Cache:          none
Search:         none
Queue:          none
```

### Bibliotecas Python Chave
```
pyodbc          4.x     → Conexão SQL Server
numpy           1.24+   → Cálculos numéricos e arrays
pandas          2.x     → Análise de dados tabulares
scipy           1.x     → Estatística (chi-squared, etc.)
sklearn         1.x     → ML (Isolation Forest, K-Means, etc.)
itertools       stdlib  → Geração de combinações C(n,k)
collections     stdlib  → Counter, defaultdict
tabulate        0.9+    → Formatação de tabelas no terminal
```

### Logging & Observabilidade
```
Logging:        print() statements (informal, mas funcional)
Metrics:        arquivo de logs em texto (workflow-graph/mcp-graph.log)
Tracing:        mcp-graph dashboard (http://localhost:3000)
```

### Testes
```
Unit:           pytest (.venv instalado)
Integration:    scripts bootstrap ad-hoc (tests/ folder)
Coverage:       baixa — foco em backtesting empírico vs testes unitários
```

### Infra & Ferramentas Dev
```
OS:             Windows 11
IDE:            VS Code com GitHub Copilot
CI/CD:          none (desenvolvimento local)
Container:      none
Version Ctrl:   Git (GitHub: ARCAlhau80/LotoScope, branch: master)
```

### MCP Servers (instalados e configurados)
```
mcp-graph       → npx @mcp-graph-workflow/mcp-graph (workflow dashboard)
serena          → uvx oraios/serena (code navigation simbolica)
context7        → npx @upstash/context7-mcp (library docs)
playwright      → npx @playwright/mcp (browser automation)
Config:         .vscode/mcp.json + .mcp.json
```

---

## 📊 Dependências — Matriz de Status

| Lib | Versão Atual | Versão Target | Status | Breaking? |
|-----|-------------|---------------|--------|-----------|
| [LIB_1] | [ATUAL] | [TARGET] | ✅/🟡/🔴 | Sim/Não |
| [LIB_2] | [ATUAL] | [TARGET] | ✅/🟡/🔴 | Sim/Não |
| [LIB_3] | [ATUAL] | [TARGET] | ✅/🟡/🔴 | Sim/Não |

**Legenda:** ✅ Atualizado | 🟡 Update disponível | 🔴 EOL/Vulnerável

---

## 🔄 Caminho de Migração (se aplicável)

### [MIGRAÇÃO_1 — ex: Java 17 → 21]
```
Esforço:    [X] horas
Risco:      [Baixo/Médio/Alto]
Bloqueios:  [Listar dependências que precisam atualizar antes]
```

### [MIGRAÇÃO_2]
```
Esforço:    [X] horas
Risco:      [Nível]
```

---

## 🔒 Vulnerabilidades Conhecidas

| CVE | Lib | Severidade | Status | Mitigação |
|-----|-----|------------|--------|-----------|
| [CVE_ID] | [LIB] | [CVSS] | ✅ Fixed / 🔴 Open | [O que fazer] |

<!-- Manter atualizado com `npm audit`, `mvn dependency-check:check`, `pip audit`, etc. -->
