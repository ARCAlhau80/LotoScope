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
- **7 Filter Levels**:
  - Level 0: No filters (490k combos)
  - Level 1: Sum + Qtde 6-25 + Débito Posicional ⭐NEW
  - Level 2: Basic + Piores Histórico (tol=0) ⭐NEW
  - Level 3: Balanced + Piores Recente (tol=1) ⭐NEW
  - Level 4: Moderate + Piores Recente (tol=0) - **NO Improbabilidade** ⭐FIXED
  - Level 5: Aggressive + positional filters - **NO Improbabilidade** ⭐FIXED
  - Level 6: Ultra + ALL filters + Núcleo ≥8 - **NO Improbabilidade** ⭐FIXED
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

### 8. Probabilistic Filter (Option 31 + Backtesting) ⭐⭐ UPDATED!
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

### 9. Anomaly Frequency Analysis v2.0 (Option 31 Levels 1-6) ⭐⭐ VALIDATED!
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

### 10. Exclusion Strategy INVERTIDA v3.0 (Option 31) ⭐⭐⭐ UPDATED! (03/03/2026)
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

### 11. Learning System v2.1 (Option 30 → Option 3) ⭐⭐ NEW!
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

---
*Last updated: 2026-03-03*
