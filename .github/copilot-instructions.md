# Copilot Instructions for LotoScope Project

## 🎯 MODEL SELECTION (READ FIRST!)

**Evaluate task complexity before processing:**

### ✅ SONNET 4.6 Tasks (3x cheaper):
- Reading docs/code, simple edits, terminal commands
- Checking backtest results, answering "how to" questions
- Creating small files from existing templates
- Obvious bugs (imports, syntax, paths)

### 🧠 OPUS 4.5 Tasks (maximum capability):
- New math/statistical algorithms
- Refactoring large files (>500 lines)
- Subtle bugs, complex logic debugging
- New system architecture, performance optimization
- Multi-file interconnected analysis
- New lottery strategies implementation

**User Tags:** `[SIMPLES]` → Sonnet | `[COMPLEXO]` → Opus | No tag → AI decides

---

## Project Overview

LotoScope is a scientific Python system for analyzing and generating optimized lottery combinations for **Lotofácil** (Brazilian lottery game).

## Key Documentation Files

Before making any changes, read these files in order:

1. `QUICK_START_IA.md` - 1-minute overview (includes model selection guide)
2. `CONTEXTO_MASTER_IA.md` - Complete documentation (Portuguese)
3. `REFERENCIA_TECNICA_IA.md` - Technical reference with code snippets

## Technical Stack

- **Language**: Python 3.11+
- **Database**: SQL Server (localhost)
- **Web Framework**: Flask
- **IDE**: VS Code
- **OS**: Windows 11

## Database Connection

```python
import pyodbc
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
```

## Main Entry Point

```powershell
cd "C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\interfaces"
python super_menu.py
```

## Current Strategy (Feb/2026)

### 1. C1/C2 Complementary System (Option 22 → Option 6)
- **C1 Divergents**: [1, 3, 4]
- **C2 Divergents**: [15, 17, 18]
- **Common Nucleus**: 17 numbers shared between both combos

### 2. Noneto Filter (Option 22 → Option 7)
- **Default Noneto**: [1, 2, 4, 8, 10, 13, 20, 24, 25]
- **Coverage**: 79% of draws have 5-7 numbers from this set
- **Use Case**: Pre-filter combinations before ranking

### 3. Number × Position Heatmap (Option 7.13)
- **Analysis**: Shows frequency of each number (1-25) in each position (N1-N15)
- **Color Coding**: Red (-10%), Blue (-6%), White (avg), Orange (+6%), Purple (+10%)
- **Default**: Last 30 contests (configurable)

### 4. Simple Checker (Option 23) ⭐ UPDATED!
- **Purpose**: Check TXT file combinations against real results
- **Modes**: 
  - Single file: ALL concursos, RANGE (3470-3475), or MANUAL entry
  - **Batch mode** ⭐ NEW: Multiple files at once (ideal for Pool 23 levels)
- **Batch Input**: Accepts formats like:
  - `N0: path/file.txt, N1: path/file2.txt`
  - `path/file.txt, path/file2.txt`
- **Financial Analysis**: Cost R$3.50/bet, Prizes (11=R$7, 12=R$14, 13=R$35, 14=R$1000, 15=R$1.8M)
- **Output**: Comparative table with ROI for each level/file

### 5. Association Rules v2.0 (Option 7.12 → Option 10) ⭐ NEW!
- **Positive Rules**: X → Y (co-occurrence patterns)
- **Negative Rules**: X → ¬Y (numbers that DON'T appear together)
- **Multi-Antecedent**: {X, Y} → Z
- **Metrics**: Support, Confidence, Lift, Conviction, Zhang's Interest
- **Explorer**: Dedicated menu with 9 sub-options

### 6. Pool 23 Hybrid Generator (Option 31) ⭐⭐⭐ BREAKTHROUGH!
- **Strategy**: Exclude 2 numbers using hybrid analysis (median + downward trend)
- **Jackpot Rate**: 21% (vs 15% traditional methods)
- **Validated**: Jackpots on contests 3610, 3615 with ROI up to +2841%
- **9 Filter Levels**:
  - Level 0: No filters (490k combos)
  - Level 1: Sum + Qtde 6-25 + Débito Posicional ⭐NEW
  - Level 2: Basic + Piores Histórico (tol=0) ⭐NEW
  - Level 3: Balanced + Piores Recente (tol=1) ⭐NEW
  - Level 4: Moderate + Piores Recente (tol=0) - **NO Improbabilidade** ⭐FIXED
  - Level 5: Aggressive + positional filters - **NO Improbabilidade** ⭐FIXED
  - Level 6: Ultra + ALL filters + Núcleo ≥8 - **NO Improbabilidade** ⭐FIXED
  - Level 7: Level 0 + Cold Positions filter (tol=4, window=6) ⭐NEW
  - Level 8: Cascade 6→1 + Cold Positions filter (tol=3, window=6) ⭐NEW
- **🔴 WARNING**: Improbabilidade Posicional filter DISABLED on levels 4-6 (was losing jackpots!)
- **Anomaly Filter v2.0** ⭐⭐ Validated historically!
  - Numbers with 8+ consecutive appearances → -5% tend to STOP
  - Numbers with 4-5 consecutive absences → +3-4% tend to RETURN ✅
  - Configurable per level: max_hot_allowed, min_cold_required

### 7. Positional Filters (Option 31 + Option 30.2) ⭐⭐⭐ NEW!
- **Purpose**: Reject combinations with numbers in improbable positions
- **3 Filters**:
  - **Qtde 6-25**: Accept only combos with 10-13 numbers from range 6-25
  - **Piores Histórico**: Dynamic - rejects numbers rarely appearing in specific positions (all history)
  - **Piores Recente**: Dynamic - same concept, but based on last 30 contests
- **Tolerance**:
  - Level 2: Histórico tol=0 (no violations allowed)
  - Level 3: Histórico tol=0, Recente tol=1 (max 1 violation)
  - Level 4-6: Both tol=0 (maximum restriction)
- **Dynamically calculated** at each execution based on real frequency data

### 7b. Best-by-Position Filter / "Melhores por Posição" (Option 31 + Option 30.2) ⭐⭐ NEW! (Apr/2026)
- **Purpose**: Complementary POSITIVE filter — accepts combos whose numbers appear among the historical TOP-K in each position
- **Concept**: For each position P1-P15, identify the TOP-K most frequent numbers using a weighted score:
  - 50% full historical frequency + 30% last-10 window + 20% last-6 window
  - A combo receives a "coverage score" = how many positions have ≥1 of its numbers in the TOP-K
  - Combos with coverage < threshold are **REJECTED**
- **POC Validation** (`poc_melhores_por_posicao.py`):
  - Threshold 11 → 78.5% of jackpots preserved
  - Threshold 10 → 86% of jackpots preserved
- **Configuration per level** (`configuracao_filtros_pool23.py`):
  - Levels 1-3: `usar_filtro_melhores_posicao=True`, `melhores_limiar=11`, `melhores_top_k=3`
  - Levels 4-6: `usar_filtro_melhores_posicao=True`, `melhores_limiar=10`, `melhores_top_k=3`
  - Levels 0, 7, 8: filter disabled
- **Method**: `_calcular_melhores_por_posicao(cursor, concurso_atual, top_k)` in `super_menu.py` (~line 15519)
  - Returns `{position (0-14): [list of top_k most frequent numbers]}`
- **Parity**: ✅ Implemented in both Option 31 (Generator) AND Option 30.2 (Backtesting)

### 8. Cold Positions Filter (Option 31 Levels 7-8 + Backtesting) ⭐⭐⭐ NEW!
- **Purpose**: Reject combinations with numbers at positions where they had 0% frequency recently
- **Concept**: For each (number, position) pair, check frequency in last 6 contests
  - If frequency = 0% → that pair is "cold" (number never appeared at that position recently)
  - The number is NOT removed entirely — only prohibited at that specific position
- **Level 7**: Level 0 (no other filters) + Cold Positions filter (tolerance=4, window=6)
- **Level 8**: Cascade 6→1 (highest level with ≥1 combo) + Cold Positions (tolerance=3, window=6)
- **Diagnostic**: Real draws average 4.0 violations (min 1, max 8) → tolerance 0 impossible
- **Available in**: Option 31 (Generator) AND Option 30.2 (Backtesting)

### 9. Probabilistic Filter (Option 31 + Backtesting) ⭐⭐ UPDATED!
- **Purpose**: Pre-filter combinations based on historical 11+ hits
- **Available in**: Option 31 (Generator) AND Option 30.2 (Backtesting) ⭐ NEW!
- **Concept**: Combinations with more historical 11+ hits have HIGHER probability
- **Modes**:
  - [0] Disabled (default)
  - [1] Conservative: Acertos_11 >= 313 (58% combos, +11% chance)
  - [2] Moderate: Acertos_11 >= 320 (45% combos, +15% chance)
  - [3] Aggressive: Acertos_11 >= 330 (35% combos, +18% chance)
  - [4] Custom: Manual limit (300-350)
- **Recentes Filter**: Optionally exclude "stale" combinations (no 11+ in last N draws)
- **Performance**: ~7s load, <1ms for 100k lookups, ~91MB RAM
- **Validation**: Contest 3614 winner passes Conservative filter (Acertos_11=317)

### 10. Anomaly Frequency Analysis v2.0 (Option 31 Levels 1-6) ⭐⭐ VALIDATED!
- **Adapted from**: MLMEGA system
- **Validated**: Historical analysis of 3,617 contests (23/02/2026)
- **Key Finding**: Sliding window frequency has NO significant effect!
- **NEW Logic v2.0**:
  - **AVOID**: Numbers with 8+ CONSECUTIVE appearances (-5% trend to stop)
  - **FAVOR**: Numbers with 4-5 CONSECUTIVE ABSENCES (+3-4% trend to return) ✅
- **Consecutive Detection**: 4+ consecutive draws = warning
- **Filter Config per Level**:
  - Level 1-2: max 3 hot, min 0 cold
  - Level 3: max 2 hot, min 1 cold
  - Level 4-5: max 1 hot, min 2 cold
  - Level 6: max 1 hot, min 2 cold (maximum restriction)

### 11. Exclusion Strategy INVERTIDA v3.0 (Option 31) ⭐⭐⭐ UPDATED! (03/03/2026)
- **Major Discovery**: Previous SUPERÁVIT strategy was **WRONG**! -1.7pp below random
- **NEW Logic**: Exclude HOT numbers (high recent frequency + consecutives)
- **Anomaly Protection** ⭐ NEW: Numbers with 10+ consecutive appearances are PROTECTED
  - Example: Number 11 appeared 14 consecutive times (contests 3611-3624)
  - Such anomalies indicate "persistence" rather than "cooling down"
- **Benchmark Results by Period** (50 contests each):
  - Last 50: **26%** (+11pp above random) ✅ BEST!
  - 50-100 back: **22%** (+7pp) ✅
  - 100-150 back: **18%** (+3pp) ✅
  - 150-200 back: 10% (-5pp) ❌
  - Random baseline: 15%
- **Key Factors for Exclusion**:
  - 10+ consecutive → score -5 (PROTECTED - anomaly!)
  - 5-9 consecutive appearances → score +6
  - 4 consecutive appearances → score +5
  - 3+ consecutive + high freq → score +4
  - 100% frequency in last 5 → score +4
- **Rationale**: "Mean reversion" - hot numbers tend to cool down, EXCEPT anomalies

#### Tested but NOT Implemented: Hybrid Strategy (1 Hot + 1 Cold)
- **Benchmark Date**: 03/03/2026
- **Results**: INFERIOR to 2 QUENTES in recent periods
  - 2 QUENTES: 19% average (+4pp) - BEST in recent 100 contests
  - HÍBRIDA: 17.5% average (+2.5pp) - More stable but lower
  - 2 FRIOS: 12% average (-3pp) - WORST
- **Decision**: Keep 2 QUENTES as default, HÍBRIDA archived for reference
- **File**: `benchmark_hibrida.py` contains full comparison code

### 12. Exclusion Strategy Selection in Backtesting (Option 30.2) ⭐⭐⭐ NEW! (24/03/2026)
- **When**: STEP 1, before generating combinations
- **Menu**: `[0] Compare all | [1] Débito | [2] Invertida v3.0 (default) | [3] Q1-Q5 | [4] Hybrid Inv+Q | [5] Hybrid ALL`
- **5 strategies**:
  - 1 `Débito` — excludes numbers with highest positional surplus
  - 2 `Invertida v3.0 (QUENTES)` — default; excludes hottest numbers (mean reversion)
  - 3 `Q1-Q5 Quadrantes` — excludes from worst quadrant (Q1)
  - 4 `Hybrid Invertida + Q1-Q5` — weighted average (60% inv + 40% quadrant)
  - 5 `Hybrid ALL` — débito (25%) + invertida (50%) + quadrant (25%)
- **Option 0 behavior**: generates using strategy 2 → at STEP 4 (after user enters real result) displays a comparative table showing which strategy would have excluded best
- **Key variables**: `comparar_estrategias_302`, `NOMES_ESTRATEGIA_302`, `ranking_ativo_302`, `rankings_estrategias_302`

### 13. Learning System v2.1 (Option 30 → Option 3) ⭐⭐ NEW!
- **Purpose**: Track exclusion/compensation accuracy over backtests
- **Exclusion Algorithm**: Now uses INVERTIDA v3.0 (exclude HOT numbers)
- **Compensation Logic**: INVERTED (predict SUBIR → accept DESCER)
- **Current Stats**: Being re-evaluated with new strategy
- **Report Features**: Detailed history table, accuracy bars, pattern analysis

## Important Files

| File | Purpose |
|------|---------|  
| `super_menu.py` | Main menu (4800+ lines) |
| `filtro_probabilistico.py` | Probabilistic filter for Option 31 |
| `analise_anomalias_frequencia.py` | Anomaly frequency analysis (adapted from MLMEGA) |
| `benchmark_hibrida.py` | Hybrid strategy comparison (archived knowledge) |
| `sistema_aprendizado_ml.py` | ML system with 15 algorithms (Association Rules v2.0) |
| `estrategia_combo20.py` | C1/C2 strategy implementation |
| `combo20_FILTRADAS_TOP1000.txt` | Top 1000 C1 combinations |
| `combo20_C2_tendencia.txt` | Top 1000 C2 combinations |
| `dados/noneto_personalizado.txt` | User-saved noneto |

1. Use **absolute paths** for file operations
2. Use **UTF-8 encoding** for all files
3. Always **check file existence** before reading
4. Keep **Portuguese** for user-facing strings
5. Update `CONTEXTO_MASTER_IA.md` after significant changes
6. **🔴 REGRA INVIOLÁVEL — Paridade Opção 31 ↔ Opção 30.2:** Toda feature/filtro/lógica implementada na Opção 31 DEVE ser replicada na Opção 30.2 (Backtesting). Manter paridade funcional completa.

## Validated Results

✅ **15 correct numbers** (jackpot) achieved in contest 3474 with 50 combinations
✅ **15 correct numbers** (jackpot) achieved in contest 3610 with Pool 23 Hybrid (Option 31)
✅ **15 correct numbers** (jackpot) achieved in contest 3615 with Pool 23 Level 6 (+2841% ROI!)
✅ **PROFIT WITHOUT JACKPOT** (01/03/2026): Level 3 (+14.3%) and Level 5 (+33.3%) ⭐ NEW!

## Economic Analysis (Important!)

- Break-even without jackpot: **Previously thought impossible, but ACHIEVED on 01/03/2026!** ⭐
- Our filters improve odds by ~650x vs random
- **Pool 23 Levels Performance**:
  - Level 2: 325k combos, best jackpot preservation, +134% ROI
  - Level 3: 100k combos, balanced, +492% ROI (jackpot) / **+14.3%** (no jackpot!) ⭐
  - Level 5: 42k combos, aggressive, +1257% ROI (jackpot) / **+33.3%** (no jackpot!) ⭐
  - Level 6: 18k combos, ultra, **+2841% ROI** ⭐ BEST!
- Recommended: Level 3-5 for balanced ROI (can profit even without jackpot!)

## Bug Fixes & Improvements (Feb-Mar/2026)

1. **Fixed**: `_calcular_debitos_posicionais` tuple unpacking (levels 1-6 showed 0 combos)
2. **Fixed**: Compensation logic was INVERTED (now: predict SUBIR → accept DESCER)
3. **Improved**: Exclusion algorithm v2.1 (conservative mode, protects recent numbers)
4. **Added**: Probabilistic filter now available in Backtesting (Option 30.2)
5. **Added**: Positional Filters (Qtde 6-25, Piores Histórico, Piores Recente) ⭐⭐ NEW!
6. **Synced**: Option 30.2 (Backtesting) now uses same filters as Option 31 (Generator)
7. **Fixed** (01/03/2026): **DISABLED Improbabilidade Posicional filter on Levels 4-6** ⭐⭐ CRITICAL!
   - The filter was rejecting jackpots (4 failures in 18 backtests, Level 4 had 0 jackpots!)
   - Analysis showed real draws had ~6 violations but filter rejected >2 violations
   - Levels 1-3 still use this filter with tolerance=2
8. **Added** (01/03/2026): **TOP 10 exclusion candidates + adjustable quantity (1-10)** ⭐ NEW!
   - Shows ranking ordered by score
   - Allows choosing how many numbers to exclude (default 2)
   - Allows manual adjustment from TOP 10
9. **MAJOR FIX** (03/03/2026): **Exclusion strategy INVERTED from SUPERÁVIT to INVERTIDA v3.0** ⭐⭐⭐ CRITICAL!
   - Benchmark showed old SUPERÁVIT strategy was -1.7pp BELOW random (13.5% vs 15.2%)
   - NEW INVERTIDA v3.0: +1.8pp ABOVE random (17.0% vs 15.2%) ✅
   - Now excludes HOT numbers (high consecutive + high freq) instead of COLD numbers
   - Key insight: "Mean reversion" - numbers that appear too often tend to stop
10. **Fixed** (20/03/2026): **Probabilistic filter was SILENTLY DISABLED in Option 30.2** ⭐⭐ CRITICAL!
    - Called non-existent methods: `carregar_dados()` and `verificar_combinacao()`
    - Exception was caught silently → filter always disabled regardless of user selection
    - Fix: replaced with correct API: `.carregar(min_acertos_11=...)` and `.filtrar_lista()`
    - Also added missing `sys.path.insert()` for module import resolution
    - Options 30.4 and 31 were already correct
11. **Added** (24/03/2026): **Exclusion strategy selection with comparative diagnosis in Option 30.2** ⭐⭐⭐ NEW!
    - User now selects exclusion strategy BEFORE generating (STEP 1): [0-5]
    - 5 strategies: Débito, Invertida v3.0, Q1-Q5, Hybrid Inv+Q, Hybrid ALL
    - Option 0 = "Compare all": generates with strategy 2 but shows full comparative table at STEP 4
    - Comparative table shows which strategy would have best excluded numbers for that draw
    - Method: `_executar_backtesting_pool23` in `lotofacil_lite/interfaces/super_menu.py`
12. **Added** (30/03/2026): **Option 30→[6] Retrain Neural Network + Benchmark** ⭐⭐ NEW!
    - New sub-option in Backtesting menu (Option 30): `_executar_retreino_neural_benchmark()`
    - Modes: [T] Train from scratch | [C] Continue training | [B] Benchmark only
    - Predefined periods: last 500/1000/2000, all, custom
    - Final summary: Neural vs INVERTIDA with emoji diagnostic 🎉/📊/🤝
    - Architecture: ~~150→256→128→64→25 (81,433 params)~~ → **150→64→32→25 (~12,500 params)** ✅ v2 anti-overfitting
    - 150 features = 6 per number: freq_30, atraso, consecutividade, tendência, freq_10, score_INVERTIDA
    - Same network shared with Option 30→[5] (Neural Disputa) and Option 31 (Pool 23 Hybrid)
    - ✅ FIXED: overfitting resolved — v2 out-of-sample 21.5% vs INVERTIDA 16.5% (+5pp)
    - Regularization: L2(0.001) + Dropout(0.3) + He initialization
    - **FRIOS diagnostic** added (31/03/2026): after benchmark summary, loads neural fresh and shows cold candidates table (see item 13)
    - **3-level training presets** added (04/04/2026): Level 1 (warmup: 3 iter/20 ep/lr=0.005) → Level 2 (consolidation: 5 iter/35 ep/lr=0.001) → Level 3 (deep refinement: 10 iter/50 ep/lr=0.0005 ✅); default window: last 2000 contests; state persisted in `neural_exclusao_train_state.json`
13. **Added** (31/03/2026): **Neural FRIOS Diagnostic — "FRIOS FAVORECIDOS PELA NEURAL"** ⭐ NEW!
    - Diagnostic block added in TWO places in `super_menu.py`:
      - **Option 31** (~line 12537): after neural hybrid ranking, shows cold numbers (absent ≥ 2 draws) sorted by ascending neural score
      - **Option 30→[6]** (~line 15470): after benchmark summary, loads neural fresh, calls `_extrair_features(idx_ultimo)` + `obter_scores()`, shows same table
    - Rating system: ⭐ FORTE (score < 0.30), candidato (< 0.45), neutro
    - Shows up to 5 cold candidates — **diagnostic only, does not change generation logic**
    - Validated: last run identified {3, 6, 23} with scores 0.400, 0.404, 0.443
14. **Added** (31/03/2026): **Neural PURO strategy — new default in Option 31** ⭐⭐ NEW!
    - Option 31 strategy menu now has THREE choices:
      - **[N] Neural PURO ⭐⭐ MELHOR!** — NEW, now default (ENTER = N)
      - **[H] Híbrido Neural+INVERTIDA** — old default (+3.3pp above INVERTIDA)
      - **[I] INVERTIDA v3.0** — classic fallback
    - Default changed from [H] to [N]: benchmark Neural PURO = **22.9%** vs INVERTIDA 15.2% = **+7.7pp** ✅
    - Pure neural uses `scores_neural` dict directly (all 25 numbers ranked by descending score)
    - Manual adjustment screen now also shows TOP 10 NEURAL list
15. **Updated** (04/04/2026): **Presets de treino 3 níveis para Opção 30→[6]** ⭐ NEW!
    - Nível 1 (aquecimento rápido): 3 iterações, 20 épocas, lr=0.005
    - Nível 2 (consolidação): 5 iterações, 35 épocas, lr=0.001
    - Nível 3 (refinamento profundo): 10 iterações, 50 épocas, lr=0.0005 ✅ confirmado
    - Janela padrão: últimos 2000 concursos (⭐ valor ótimo)
    - Fluxo recomendado: N1 com [T] do zero → N2 com [C] continuar → N3 com [C] continuar
    - Estado persiste em `neural_exclusao_train_state.json` (avança sugestão 1→2→3 automaticamente)
16. **Refactored** (04/04/2026): **Arquitetura Neural v2 anti-overfitting** ⭐⭐⭐ CRÍTICO!
    - v1 (81.433 params, 40:1 ratio): overfitting confirmado — out-of-sample 11% vs INVERTIDA 16.5% ❌
    - v2 (12.500 params, 6:1 ratio): generalização validada — out-of-sample **21.5%** vs INVERTIDA 16.5% ✅
    - Mudanças: 150→64→32→25 + L2(0.001) + Dropout(0.3) + He initialization
    - Protocolo: benchmark periódico em #1452-#1651; se <17% → retreinar do zero
    - Arquivo: `disputa_neural_pool23.py` — classe `RedeNeuralExclusao`
17. **Added** (Abr/2026): **Filtro "Melhores por Posição" — análise positiva complementar** ⭐⭐ NOVO!
    - Para cada posição P1-P15, identifica os TOP-K números mais frequentes via score ponderado
      (50% histórico total + 30% janela 10 + 20% janela 6)
    - Score de cobertura da combo = nº de posições com ≥1 número no TOP-K
    - Combos com cobertura < limiar são **REJEITADAS**
    - POC (`poc_melhores_por_posicao.py`): limiar 11 → 78.5% jackpots preservados; limiar 10 → 86%
    - Config: Níveis 1-3 (`limiar=11, top_k=3`), Níveis 4-6 (`limiar=10, top_k=3`), Níveis 0/7/8 desativado
    - Método: `_calcular_melhores_por_posicao(cursor, concurso_atual, top_k)` em `super_menu.py` (~l.15519)
    - ✅ Paridade Opção 31 ↔ 30.2 implementada
18. **Fixed** (Abr/2026): **`import sys` UnboundLocalError em 3 pontos de `super_menu.py`** ⭐ CRÍTICO!
    - **Causa raiz**: Python trata `import sys` dentro de função como atribuição local → qualquer uso de `sys` antes do `import` na mesma função levanta `UnboundLocalError`
    - **Fix 1** — `executar_gerador_pool_23_hibrido`: `import sys` movido para antes do primeiro uso (~l.13694)
    - **Fix 2** — `_executar_backtesting_pool23` (bloco padrões string 302): `import sys` adicionado antes do `sys.path.insert` (~l.20045)
    - **Fix 3** — `_executar_backtesting_pool23` (bloco filtro probabilístico): `import sys` redundante removido (~l.20461, já coberto pelo Fix 2)

---
*Last updated: 2026-04 (Abr/2026)*

<!-- mcp-graph:start -->
## mcp-graph — LotoScope

Este projeto usa **mcp-graph** para gestão de execução via grafo persistente.
Dados em `workflow-graph/graph.db`.

### 🚀 Quick Start - Iniciar Dashboard

```powershell
# Opção 1: Script batch (recomendado)
.\start-mcp-graph.bat

# Opção 2: Comando direto
$env:Path = "C:\Program Files\nodejs;" + $env:Path
npx -y @mcp-graph-workflow/mcp-graph serve --port 3000
```

**Dashboard**: http://localhost:3000

### Ferramentas MCP (principais)

| Tool | Uso |
|------|-----|
| `next` | Próxima task recomendada |
| `context` | Contexto comprimido (token-efficient) |
| `update_status` | Mudar status (backlog→ready→in_progress→done) |
| `import_prd` | Importar PRD para o grafo |
| `plan_sprint` | Planejamento de sprint |
| `decompose` | Decompor tasks grandes |
| `validate_task` | Validar com Playwright |

### Fluxo: `next → context → [TDD] → update_status → next`

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
<!-- mcp-graph:end -->
