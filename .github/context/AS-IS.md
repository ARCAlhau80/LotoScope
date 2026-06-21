# 📊 AS-IS — Estado Atual de LotoScope

**Última atualização:** 24/03/2026  
**Status:** Active Development

---

## 🏗️ Stack Atual

```
Language:       Python 3.11+
Framework:      CLI principal (super_menu.py) + Flask ocasional (web/)
Database:       SQL Server 2019 (localhost, Windows Auth)
Build:          pip + uv + .venv
Tests:          baixa cobertura formal (~5%) — validação empírica via backtest
MCP:            mcp-graph, serena, context7, playwright (todos instalados)
```

---

## 🎯 O Que Funciona Bem

✅ **Pool 23 Híbrido (Opção 31)** — 9 níveis funcionais, ROI validado até +2841%  
✅ **Exclusão INVERTIDA v3.0** — supera baseline +11pp nos últimos 50 concursos  
✅ **Filtro Probabilístico** — disponível no gerador E no backtesting  
✅ **Banco SQL Server** — ~3.640 concursos, tabela COMBINACOES com 3.2M registros  
✅ **Backtesting (Opção 30.2)** — sincronizado com os filtros da Opção 31  
✅ **Association Rules v2.0** — positivas, negativas e multi-antecedente  
✅ **Filtros Posicionais** — Qtde 6-25, Piores Histórico/Recente, Cold Positions  
✅ **Verificador batch (Opção 23)** — múltiplos arquivos TXT com análise de ROI  
✅ **MCP servers** — mcp-graph, serena, context7, playwright instalados e configurados  

---

## 🔴 Pain Points & Dívidas Técnicas

| # | Problema | Severidade | Impacto | Origem |
|---|----------|------------|---------|--------|
| 1 | `super_menu.py` monolítico (4800+ linhas) | 🟡 Média | Difícil manutenção | Crescimento orgânico |
| 2 | Pouca cobertura de testes unitários | 🟡 Média | Risco de regressão em refactors | Foco em backtest empírico |
| 3 | Caminhos hardcoded para usuário específico | 🟡 Média | Não portável para outros devs | `C:\Users\AR CALHAU\...` |
| 4 | Templates ISGT (.github/.github/) incompletos | 🟢 Baixa | IA sem contexto correto | Foram preenchidos em 24/03 |
| 5 | Versão Flask (web/) desatualizada vs CLI | 🟢 Baixa | Funcionalidades novas não refletidas na web | Foco no CLI |

---

## 📊 Métricas Atuais

| Métrica | Valor | Status |
|---------|-------|--------|
| Concursos no banco | ~3.640 | ✅ Atualizado |
| Combinações na tabela | 3.268.760 | ✅ Completa |
| Opções no super_menu | 35+ | ✅ |
| Jackpots validados | 3 (concursos 3474, 3610, 3615) | ✅ |
| Lucro sem jackpot | 2 datas (01/03/2026) | ✅ Breakthrough |
| Cobertura testes | ~5% | 🔴 Baixa |
| MCP servers ativos | 4 de 4 instalados | ✅ |

---

## ⚠️ Riscos Identificados

1. **Dependência de SQL Server local** — projeto não funciona sem SQL Server rodando
2. **Caminhos hardcoded** — scripts assumem `C:\Users\AR CALHAU\` como base
3. **super_menu.py monolítico** — bug em uma opção pode impactar outras (sem isolamento)
4. **Overfitting de estratégias** — backtesting em janelas curtas pode gerar falsos positivos

---

## 🔄 Histórico de Evolução Recente

| Data | Mudança | Impacto |
|---|---|---|
| Jan/2026 | Sistema C1/C2 + Noneto | Base do sistema |
| Fev/2026 | Pool 23 (Opção 31), levels 0-6 | BREAKTHROUGH |
| Fev/2026 | Filtros posicionais + Probabilístico | +ROI |
| Mar/2026 01 | Profits sem jackpot (Level 3 +14.3%, Level 5 +33.3%) | ⭐ Milestone |
| Mar/2026 03 | Inversão exclusão: SUPERÁVIT → INVERTIDA v3.0 | Fix crítico |
| Mar/2026 20 | Fix: filtro probabilístico silenciosamente desativado no 30.2 | Fix crítico |
| Mar/2026 24 | ISGT atualizado, agents VS Code criados, mcp-graph/serena/context7/playwright | Infra IA |

---

<!-- DICA: Para projetos NOVOS, este arquivo pode ficar quase vazio.
     Preencha conforme o projeto evolui e dívidas surgem. -->
