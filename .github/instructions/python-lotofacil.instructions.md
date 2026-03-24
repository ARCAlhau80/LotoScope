---
description: "Use when writing Python code for the LotoScope project. Covers SQL Server connections, file encoding, path conventions, print formatting in Portuguese, and project-specific patterns including pyodbc, numpy, and pandas usage. Apply for all .py files in the LotoScope repository."
name: "Python LotoScope Standards"
applyTo: "**/*.py"
---

# Python LotoScope — Padrões de Desenvolvimento

## Ambiente

```
OS: Windows 11
Python: 3.11+
Venv: .venv\ (ativar: .venv\Scripts\Activate.ps1)
Encoding: UTF-8 para todos os arquivos
Raiz: C:\Users\AR CALHAU\source\repos\LotoScope
```

## Conexão SQL Server (Padrão Obrigatório)

```python
import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def get_connection():
    return pyodbc.connect(CONN_STR)

# Uso correto com context manager:
with pyodbc.connect(CONN_STR) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT N1,N2,...,N15 FROM Resultados_INT WHERE Concurso = ?", (numero,))
    row = cursor.fetchone()
```

## Estrutura da Tabela Principal

```sql
Resultados_INT:
  Concurso        INT   -- Número do concurso (1 a ~3640)
  N1..N15         INT   -- Números sorteados por posição (1-25)
  Data_Sorteio    VARCHAR
  -- 21+ campos estatísticos adicionais
```

## Caminhos de Arquivo

```python
# SEMPRE absolutos no Windows:
import os
BASE_DIR = r"C:\Users\AR CALHAU\source\repos\LotoScope"
INTERFACES_DIR = os.path.join(BASE_DIR, "lotofacil_lite", "interfaces")

# Para arquivos de dados gerados:
DATA_DIR = os.path.join(BASE_DIR, "lotofacil_lite")
```

## Encoding UTF-8 (Obrigatório)

```python
# Leitura:
with open(caminho, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Escrita:
with open(caminho, 'w', encoding='utf-8') as f:
    f.write(conteudo)

# Print com emojis/acentos → garantido no Windows:
import sys
sys.stdout.reconfigure(encoding='utf-8')  # No topo do script se necessário
```

## Strings para o Usuário: Português (BR)

```python
# ✅ Correto — user-facing em português:
print(f"✅ {len(combinacoes)} combinações geradas com sucesso!")
print(f"❌ Erro ao conectar ao banco de dados: {e}")

# ✅ Correto — código/variáveis em inglês:
def filter_combinations(combos: list, level: int) -> list:
    filtered_count = 0
    ...
```

## Imports Padrão do Projeto

```python
import pyodbc          # Banco de dados SQL Server
import numpy as np     # Cálculos numéricos
import pandas as pd    # Análise de dados tabulares
from collections import Counter, defaultdict
from itertools import combinations
from typing import List, Dict, Tuple, Optional
```

## Manipulação de Combinações

```python
# Formato interno: tuple ou list de 15 ints, cada int de 1 a 25
combo: tuple[int, ...] = (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 22, 23, 24, 25)

# Arquivo TXT — um combo por linha, números separados por espaço com zero-padding:
linha = " ".join(f"{n:02d}" for n in sorted(combo))  # "01 03 05..."

# Validação básica:
def is_valid_combo(combo) -> bool:
    nums = sorted(combo)
    return (len(nums) == 15 and
            all(1 <= n <= 25 for n in nums) and
            len(set(nums)) == 15)
```

## Anti-Padrões a Evitar

```python
# ❌ NUNCA usar SQLite em produção (projeto usa SQL Server):
# conn = sqlite3.connect("LotoScope.db")  # ERRADO

# ❌ NUNCA caminhos relativos sem os.path.join:
# open("dados/resultado.txt")  # ERRADO — usar caminho absoluto

# ❌ NUNCA omitir encoding:
# open(arquivo)  # ERRADO — pode falhar com acentos no Windows

# ❌ NUNCA hardcode de dados de concurso na lógica:
# numeros_validos = [1,2,3,...,25]  # OK como constante
# numeros_invalidos = [26, 0]  # Validar na entrada
```

## super_menu.py — Padrão de Novas Opções

```python
# Estrutura de uma nova opção do menu:
elif opcao == "XX":
    print("\n" + "="*60)
    print("🎯 TÍTULO DA NOVA OPCÃO")
    print("="*60)
    # ... implementação
    input("\n[ENTER para continuar...]")
```
