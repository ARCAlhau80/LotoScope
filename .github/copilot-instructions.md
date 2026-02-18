# Copilot Instructions for LotoScope Project

## Project Overview

LotoScope is a scientific Python system for analyzing and generating optimized lottery combinations for **Lotofácil** (Brazilian lottery game).

## Key Documentation Files

Before making any changes, read these files in order:

1. `QUICK_START_IA.md` - 1-minute overview
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

### 4. Simple Checker (Option 23) ⭐ NEW!
- **Purpose**: Check TXT file combinations against real results
- **Modes**: ALL, RANGE (3470-3475), or MANUAL entry
- **Financial Analysis**: Cost R$3.50/bet, Prizes (11=R$7, 12=R$14, 13=R$35, 14=R$1000, 15=R$1.8M)
- **Output**: Total cost, prize, profit/loss, ROI%

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
  - Level 1: Sum only (381k combos)
  - Level 2: Basic - **RECOMMENDED FOR JACKPOT** (325k combos)
  - Level 3: Balanced (100k combos, seq max 6)
  - Level 4: Moderate (12k combos, strict soma)
  - Level 5: Aggressive (42k combos, ROI optimized)
  - Level 6: Ultra (18k combos, **+2841% ROI** when jackpot!)

### 7. Probabilistic Filter (Option 31 + Backtesting) ⭐⭐ UPDATED!
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

### 8. Learning System v2.1 (Option 30 → Option 3) ⭐⭐ NEW!
- **Purpose**: Track exclusion/compensation accuracy over backtests
- **Exclusion Algorithm v2.1**: Conservative mode - protects numbers in last 3 draws
- **Compensation Logic**: INVERTED (predict SUBIR → accept DESCER)
- **Current Stats**: 50% exclusion accuracy (8 backtests)
- **Report Features**: Detailed history table, accuracy bars, pattern analysis

## Important Files

| File | Purpose |
|------|---------|  
| `super_menu.py` | Main menu (4800+ lines) |
| `filtro_probabilistico.py` | Probabilistic filter for Option 31 |
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

## Economic Analysis (Important!)

- Break-even without jackpot: **Impossible** (but Pool 23 Level 6 gives +2841% ROI when jackpot!)
- Our filters improve odds by ~650x vs random
- **Pool 23 Levels Performance**:
  - Level 2: 325k combos, best jackpot preservation, +134% ROI
  - Level 3: 100k combos, balanced, +492% ROI
  - Level 5: 42k combos, aggressive, +1257% ROI
  - Level 6: 18k combos, ultra, **+2841% ROI** ⭐ BEST!
- Recommended: Level 2-3 for jackpot hunting, Level 5-6 for maximum ROI

## Bug Fixes & Improvements (Feb/2026)

1. **Fixed**: `_calcular_debitos_posicionais` tuple unpacking (levels 1-6 showed 0 combos)
2. **Fixed**: Compensation logic was INVERTED (now: predict SUBIR → accept DESCER)
3. **Improved**: Exclusion algorithm v2.1 (conservative mode, protects recent numbers)
4. **Added**: Probabilistic filter now available in Backtesting (Option 30.2)

---
*Last updated: 2026-02-18*
