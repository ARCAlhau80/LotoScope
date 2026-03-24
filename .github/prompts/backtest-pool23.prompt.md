---
description: "Run Pool 23 backtesting across multiple filter levels and analyze ROI — compare levels 0-8, identify which level performs best for a given period, calculate jackpot rate and profitability without jackpot"
name: "Backtest Pool 23"
agent: "agent"
tools: [execute, read, search]
argument-hint: "Período de backtest (ex: últimos 20 concursos, 3600-3620) e nível a testar"
---

Execute um backtest completo do Pool 23 Híbrido para o período especificado e produza análise comparativa de ROI por nível.

## Parâmetros

- **Período**: {{PERIODO}} (ex: "últimos 20 concursos" ou "concursos 3600 a 3620")
- **Nível**: {{NIVEL}} (ex: "todos", "3", "5 e 6")
- **Excluir**: {{EXCLUIR}} (opcional — ex: "usar exclusão automática" ou "excluir números 11 e 14")

## Workflow

1. **Carregar** resultados reais do período do SQL Server
2. **Para cada concurso** do período:
   a. Calcular exclusão dos 2 números HOT (INVERTIDA v3.0) com dados ANTERIORES ao concurso
   b. Gerar Pool 23
   c. Aplicar filtros de cada nível
   d. Verificar quantos acertos o resultado real teria
3. **Calcular métricas** por nível:
   - Jackpot rate (15 acertos / total de concursos)
   - Hit rate 11+ (proporção com ≥11 acertos)
   - ROI com jackpot e sem jackpot
   - Custo total (R$ 3,50 × combos × concursos)
4. **Apresentar** tabela comparativa com ranking

## Tabela de Custo/Prêmio (Referência)

| Acertos | Prêmio |
|---|---|
| 11 | R$ 7,00 |
| 12 | R$ 14,00 |
| 13 | R$ 35,00 |
| 14 | R$ 1.000,00 |
| 15 | ~R$ 1.800.000,00 |
| Custo/bet | R$ 3,50 |

## Formato de Saída

```
=== BACKTEST POOL 23 — [PERÍODO] ===
Concursos analisados: N

| Level | Combos | Custo Total | Prêmios | ROI | Jackpots |
|-------|--------|-------------|---------|-----|----------|
|   0   |  490k  |    R$ XXX   |  R$ XX  | -%  |    0     |
|   3   |  100k  |    R$ XXX   |  R$ XX  | +X% |    X     |
|   6   |   18k  |    R$ XXX   |  R$ XX  | +X% |    X     |

🏆 MELHOR NÍVEL PARA O PERÍODO: Level X (ROI: +X%)
📊 MELHOR NÍVEL SEM JACKPOT: Level X (ROI: +X%)
```

## Scripts de Referência

```
lotofacil_lite/interfaces/super_menu.py (Opção 30.2)
teste_pool_23_backtesting.py
backtest_historico_completo.py
```
