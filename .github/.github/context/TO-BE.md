# 🎯 TO-BE — Visão Futura de LotoScope

**Horizonte:** 6-12 meses (Abr/2026 → Mar/2027)  
**Objetivo:** Maximizar ROI e jackpot rate com mínimo de combos por sorteio  
**Atualizado:** 24/03/2026

---

## 🚀 Roadmap por Fases

### Fase 1: Análise de Transição Posicional — ✅ DONE (Fev/2026)
```
Período:    Jan-Fev/2026
Objetivo:   Entender probabilidades condicionais por posição
Entregas:
├─ analisador_transicao_posicional.py (53.070 transições calculadas)
├─ Matrizes de transição 25x25 por posição N1-N15
└─ Descoberta: posição N1 número 1 → 59.4% repetição
Métricas: ✅ Implementado e documentado
```

### Fase 2: Pool 23 com Cold Positions (Levels 7-8) — ✅ DONE (Mar/2026)
```
Período:    Mar/2026
Objetivo:   Adicionar filtro de posições frias aos generators
Entregas:
├─ Level 7: Level 0 + Cold Positions (tol=4, window=6)
└─ Level 8: Cascade 6→1 + Cold Positions (tol=3, window=6)
Métricas: ✅ Funcionais, disponíveis no gerador e backtest
```

### Fase 3: Sistema de Aprendizado v3.0 — 🟡 IN PROGRESS
```
Período:    Mar-Abr/2026
Objetivo:   Auto-aprendizado com feedback de cada sorteio real
Entregas:
├─ Registrar cada previsão e resultado real automaticamente
├─ Ajustar pesos dos filtros baseado em acurácia histórica
└─ Dashboard de performance do sistema de aprendizado
Métricas de Sucesso: Acurácia de exclusão > 70% em 30 concursos
```

### Fase 4: Otimização de Níveis Dinâmicos — ⬜ PLANNED
```
Período:    Abr-Mai/2026
Objetivo:   Nível de filtro se adapta ao contexto do sorteio
Entregas:
├─ Detector de "regime" do sorteio (HOT/COLD/NORMAL)
├─ Seleção automática de nível baseada no regime
└─ Backtesting comparativo: nível fixo vs. dinâmico
Dependência: Fase 3 completa (dados de aprendizado)
```

### Fase 5: Interface Web Moderna — ⬜ PLANNED
```
Período:    Jun-Jul/2026
Objetivo:   Trazer funcionalidades do CLI para interface web
Entregas:
├─ Pool 23 Generator na web (todos os 9 níveis)
├─ Dashboard de backtesting em tempo real
└─ Visualização de heatmaps e transições posicionais
Dependência: Fases 3-4 estabilizadas
```

---

## 🏛️ Arquitetura Target

```
┌─────────────────────────────────────────────────────┐
│  INTERFACE LAYER                                      │
│  super_menu.py (CLI) ↔ web/backend/ (Flask REST)     │
├─────────────────────────────────────────────────────┤
│  STRATEGY LAYER                                       │
│  EstrategiaInvertidaV3 | FiltroProbabilistico         │
│  AnalisadorAnomalias   | FiltrosPositionais           │
├─────────────────────────────────────────────────────┤
│  ANALYSIS LAYER                                       │
│  AnalisadorTransicao   | AssociationRules             │
│  BacktestEngine        | SistemaAprendizadoML         │
├─────────────────────────────────────────────────────┤
│  DATA LAYER                                           │
│  SQL Server (Resultados_INT + COMBINACOES)            │
│  Arquivos TXT gerados (dados/)                        │
└─────────────────────────────────────────────────────┘
```

---

## 📈 Metas de Sucesso

| Métrica | Atual | Meta 6 meses | Meta 12 meses |
|---|---|---|---|
| Jackpot rate (últimos 20) | ~20% | 25% | 30% |
| ROI sem jackpot (Level 3) | +14.3% | +20% | +30% |
| Combos no nível ótimo | ~18k-100k | ~10k-50k | ~5k-25k |
| Cobertura de testes | ~5% | 40% | 60% |
| Automação por sorteio | Manual | Semi-auto | Full-auto |
│  [CAMADA 3 — ex: Domain / Business Logic]   │
├─────────────────────────────────────────────┤
│  [CAMADA 4 — ex: Infrastructure / Data]     │
└─────────────────────────────────────────────┘
```

---

## 📊 Metas Quantitativas

| Métrica | Atual | Meta | Prazo |
|---------|-------|------|-------|
| Test Coverage | [XX]% | [YY]% | [DATA] |
| Build Time | [XX]s | [YY]s | [DATA] |
| Deploy Frequency | [XX]/mês | [YY]/mês | [DATA] |
| Mean Time to Recovery | [XX]h | [YY]min | [DATA] |

---

## 🚧 Decisões Pendentes

<!-- Decisões arquiteturais que precisam ser tomadas -->

1. [DECISÃO_1 — ex: Monolito vs Microservices?]
2. [DECISÃO_2 — ex: PostgreSQL vs MongoDB?]
3. [DECISÃO_3 — ex: REST vs GraphQL?]

---

<!-- DICA: Este arquivo é um documento vivo. 
     Atualize status das fases conforme progride. -->
