---
name: pool23-workflow
description: 'Complete Pool 23 Hybrid workflow: exclusion analysis → combination generation → filter application → backtesting. Use for running Option 31 of super_menu.py, choosing filter levels, debugging generation issues, or validating ROI per level.'
tools:
  - read
  - search
  - execute
---

# Pool 23 Hybrid Workflow

## When to Use
- Generating betting combinations for the next Lotofácil draw
- Choosing which filter level (0-8) to generate from
- Backtesting historical ROI per level (Option 30.2)
- Debugging why a specific level yields 0 combinations
- Verifying which numbers were excluded and why

## Key Files
- `lotofacil_lite/interfaces/super_menu.py` — Options 30, 31
- `filtro_probabilistico.py` — probabilistic filter (COMBINACOES_LOTOFACIL table)
- `analise_anomalias_frequencia.py` — HOT/COLD consecutive detection

## Core Algorithm: INVERTIDA v3.0

### Exclusion Scoring (exclude HIGHEST scoring numbers)
| Condition | Score |
|---|---|
| 10+ consecutive appearances (**ANOMALY — PROTECT!**) | **-5** |
| 5-9 consecutive appearances | +6 |
| 4 consecutive appearances | +5 |
| 3+ consecutive + high overall freq | +4 |
| 100% frequency in last 5 draws | +4 |

**Exclude the 2 numbers with highest score (avoid scores of -5)**

### Pool Size after Exclusion
- 25 numbers → exclude 2 → 23 numbers → C(23,15) = 490,314 combinations

### Filter Levels
| Level | Filters | ~Combos |
|---|---|---|
| 0 | None | 490k |
| 1 | Sum + Qtde 6-25 + Débito Posicional | ~200k |
| 2 | L1 + Piores Histórico (tol=0) | ~100k |
| 3 | L2 + Piores Recente (tol=1) | ~50k |
| 4 | Moderate + Piores Recente (tol=0) | ~25k |
| 5 | Aggressive + positional filters | ~10k |
| 6 | Ultra + ALL filters + Núcleo ≥8 | ~5k |
| 7 | L0 + Cold Positions (tol=4, window=6) | ~200k |
| 8 | Cascade 6→1 + Cold Positions | varies |

### ⚠️ Critical Rules
- **Improbabilidade Posicional DISABLED in Levels 4-6** — was rejecting jackpots!
- Levels 1-3 OK with Improbabilidade (tolerance=2)
- Numbers 1-25 only, exactly 15 per combo
- Cold Positions: window=6 recent draws, checks (number, position) pairs

## ROI Reference (validated results)
| Level | ROI (jackpot draw) | ROI (no jackpot) |
|---|---|---|
| 3 | +492% | +14.3% ✅ |
| 5 | +1257% | +33.3% ✅ |
| 6 | **+2841%** | N/A |

## Backtesting Command Flow
1. Run `python super_menu.py`
2. Select **30** → **2** (Backtest Pool 23)
3. Enter contest range (e.g., 3610-3625)
4. Select level(s) to compare
5. Review ROI comparative table output

## Debugging Zero-Combo Level
If a level returns 0 combinations:
1. Run with `debug_debitos.py` to check positional debit calculations
2. Check if tuple unpacking is correct in `_calcular_debitos_posicionais`
3. Try raising tolerance by 1 to verify filter is over-restricting
4. Check if `analise_anomalias_frequencia.py` is using `max_hot_allowed` correctly
