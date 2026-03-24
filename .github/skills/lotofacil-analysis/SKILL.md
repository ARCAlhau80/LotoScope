---
name: lotofacil-analysis
description: 'Workflow for analyzing Lotofácil draws using LotoScope statistical tools. Use for: investigating a specific draw, checking frequency patterns, validating anomalies, or understanding why a strategy passed/failed. Invokes super_menu.py options 7.x and 22.'
tools:
  - read
  - search
  - execute
---

# Lotofácil Analysis Workflow

## When to Use
- Analyzing a specific draw (concurso number)
- Checking number frequency or consecutive patterns
- Investigating why a combo won or was filtered out
- Validating HOT/COLD status of numbers before the next draw

## Key Files
- `lotofacil_lite/interfaces/super_menu.py` — main entry point (Options 7, 22, 23)
- `analise_anomalias_frequencia.py` — consecutive detection
- `analisador_transicao_posicional.py` — positional transition matrices

## Standard Analysis Steps

1. **Load recent draws** (last 30-50 contests from `Resultados_INT`)
2. **Check frequency table** — Option 7.1 in super_menu
3. **Check consecutive patterns** — identify HOT/COLD numbers
4. **Positional heatmap** — Option 7.13 (last 30 contests)
5. **Compare against last draw** — what repeated, what was new

## SQL Pattern
```python
import pyodbc
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()
cursor.execute("SELECT TOP 30 Concurso, N1,N2,...,N15 FROM Resultados_INT ORDER BY Concurso DESC")
```

## Output Format
Always output:
- Numbers sorted ascending
- Frequency as percentage (last N draws)
- Consecutive count (positive = appearances, negative = absences)
- HOT/COLD flag (HOT: 5+ consecutives, COLD: 4+ absences)
