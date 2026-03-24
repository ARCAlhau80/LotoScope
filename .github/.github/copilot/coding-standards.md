# 💻 CODING STANDARDS — LotoScope

**Escopo:** Python 3.11+ no projeto LotoScope  
**Aplicado:** Para humanos E IA  
**Atualizado:** 24/03/2026

---

## 🏛️ Convenções de Nomenclatura

### Funções e Métodos (snake_case)

```python
# ✅ PADRÃO Python — snake_case para tudo:
def calcular_frequencia_recente(resultados: list, janela: int = 30) -> dict:
    ...

def filtrar_combinacoes_por_nivel(combos: list, nivel: int) -> list:
    ...

def _calcular_score_exclusao(numero: int, historico: list) -> float:
    # Prefixo _ = método privado/interno
    ...
```

```python
# ❌ NUNCA:
def calcularFrequencia():  # camelCase — não é Python
def Processar():           # PascalCase — reservado para Classes
def fn():                  # Nomes sem significado
```

### Classes (PascalCase)

```python
# ✅ PADRÃO:
class FiltroProbabilistico:      # Filtro de probabilidade
class AnalisadorAnomalias:       # Analisador de anomalias
class GeradorPool23:             # Gerador do Pool 23
class EstrategiaInvertidaV3:     # Estratégia INVERTIDA v3.0
class SistemaAprendizadoML:      # Sistema de ML

# ❌ NUNCA:
class filtro_probabilistico:     # snake_case para classe
class Proc:                      # Abreviação sem significado
```

### Constantes (UPPER_SNAKE_CASE)

```python
# ✅ PADRÃO:
BASE_DIR = r"C:\Users\AR CALHAU\source\repos\LotoScope"
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};...'
NUMEROS_VALIDOS = range(1, 26)  # 1 a 25
COMBO_SIZE = 15
POOL_SIZE = 25

# Filtros C1/C2:
DIV_C1 = [1, 3, 4]
DIV_C2 = [15, 17, 18]
NUCLEO = [6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]

# Noneto:
NONETO_PADRAO = [1, 2, 4, 8, 10, 13, 20, 24, 25]
```

### Arquivos e Módulos (snake_case)

```
filtro_probabilistico.py        ✅
analise_anomalias_frequencia.py ✅
super_menu.py                   ✅
estrategia_combo20.py           ✅
FiltroProb.py                   ❌ (camelCase)
filtro-probabilistico.py        ❌ (hyphen — problemático no import)
```

---

## 📝 Idioma no Código

| Categoria | Idioma | Exemplo |
|---|---|---|
| Nomes de funções/variáveis | Inglês | `filter_combinations`, `combo_size` |
| Strings user-facing (print) | Português BR | `"✅ Combinações geradas com sucesso!"` |
| Comentários de código | Inglês ou Português | Consistente dentro do arquivo |
| Docstrings | Português BR | `"""Calcula a frequência de cada número..."""` |
| Commits/PRs | Inglês ou Português | Consistente |

---

## 🔒 Type Hints (Recomendado)

```python
# ✅ Use type hints em funções novas:
from typing import List, Dict, Tuple, Optional, Set

def calcular_score(numero: int, historico: List[Set[int]], janela: int = 30) -> float:
    ...

def filtrar_nivel(combos: List[Tuple[int, ...]], nivel: int) -> List[Tuple[int, ...]]:
    ...

# Para Python 3.11+, pode usar built-ins diretamente:
def processar(numeros: list[int], resultado: dict[int, float]) -> None:
    ...
```

---

## 📦 Estrutura de Módulo

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Breve descrição do módulo em português.
Uso: como executar ou importar este módulo.
"""

# Imports stdlib primeiro
import os
import sys
from typing import List, Dict

# Imports externos
import pyodbc
import numpy as np

# Imports internos (relative ou absolute)
sys.path.insert(0, BASE_DIR)  # Se necessário

# Constantes
CONN_STR = '...'

# Classes e funções
class MinhaClasse:
    ...

# Entry point (se executável direto)
if __name__ == "__main__":
    main()
```

---

## 🚫 Anti-Padrões Proibidos

```python
# ❌ Nunca usar f-string com SQL (injection risk):
cursor.execute(f"SELECT * FROM Resultados_INT WHERE Concurso = {n}")  # PROIBIDO

# ✅ Sempre usar parâmetros:
cursor.execute("SELECT * FROM Resultados_INT WHERE Concurso = ?", (n,))

# ❌ Nunca omitir encoding ao abrir arquivos:
open("arquivo.txt")  # PROIBIDO no Windows com acentos

# ✅ Sempre especificar encoding:
open("arquivo.txt", encoding='utf-8')

# ❌ Nunca usar caminhos relativos para dados:
open("dados/resultado.txt")  # FRÁGIL

# ✅ Sempre usar caminhos absolutos:
open(os.path.join(BASE_DIR, "dados", "resultado.txt"), encoding='utf-8')
```
```

### Variáveis

```
✅ PADRÃO:
- camelCase (Java/JS/TS) ou snake_case (Python/Ruby)
- Nomes descritivos: totalAmount, isActive, userList
- Constantes: UPPER_SNAKE_CASE → MAX_RETRY_COUNT

❌ NUNCA:
- 1 letra (exceto loops): a, x, d
- Tipo no nome: strName, intCount, listUsers
- Abreviações obscuras: usrMgr, txnProc
```

---

## 🎯 Estrutura de Classes

### Template Geral

```
[LANGUAGE] class structure:

1. Constants / Static fields
2. Instance fields (private)
3. Constructor(s)
4. Public methods (API surface)
5. Protected methods (extension points)
6. Private methods (internal logic)
```

<!-- Adicione templates específicos para cada tipo de classe do seu projeto -->

### [TIPO_CLASSE_1] Template (ex: Controller)

```
// Adapte este template para sua linguagem e framework

[Annotations/Decorators]
public class [Nome][Tipo] {

    // 1. Dependencies (injection)
    private final [Dependency1] dependency1;
    
    // 2. Constructor
    public [Nome][Tipo]([Dependency1] dependency1) {
        this.dependency1 = dependency1;
    }
    
    // 3. Public methods
    public [ReturnType] [method]([Params]) {
        // Implementation
    }
}
```

---

## 📦 Organização de Pacotes/Módulos

```
[PACKAGE_BASE]/
├── [camada_1]/           # Presentation (controllers, views)
├── [camada_2]/           # Application (services, use cases)
├── [camada_3]/           # Domain (entities, value objects)
├── [camada_4]/           # Infrastructure (repos, adapters)
└── [camada_5]/           # Config (security, database)
```

---

## ⚠️ Anti-Patterns (NUNCA fazer)

<!-- Liste os anti-patterns específicos do seu projeto -->

1. ❌ [ANTI_PATTERN_1 — ex: God class com 500+ linhas]
2. ❌ [ANTI_PATTERN_2 — ex: Lógica de negócio no controller]
3. ❌ [ANTI_PATTERN_3 — ex: Queries SQL construídas por concatenação]
4. ❌ [ANTI_PATTERN_4 — ex: Try-catch vazio (engolir exceção)]
5. ❌ [ANTI_PATTERN_5 — ex: Credentials hardcoded]

---

## ✅ Padrões Obrigatórios

<!-- Liste padrões que TODO código novo deve seguir -->

1. ✅ [PADRÃO_1 — ex: Todo endpoint retorna ResponseEntity com status HTTP correto]
2. ✅ [PADRÃO_2 — ex: Logging estruturado com correlation ID]
3. ✅ [PADRÃO_3 — ex: Testes unitários para toda lógica de negócio]
4. ✅ [PADRÃO_4 — ex: Validação com Bean Validation (@Valid)]
5. ✅ [PADRÃO_5 — ex: Error handling centralizado com @ControllerAdvice]

---

## 🧪 Padrões de Teste

```
Nomenclatura:  [ClasseTestada]Test (unit) ou [Classe]IntegrationTest
Estrutura:     Given-When-Then / Arrange-Act-Assert
Localização:   Espelhar estrutura de pacotes do src/
Cobertura:     Target: [XX]% (mínimo: [YY]%)
```

| Componente | Tipo de Teste | Framework |
|------------|---------------|-----------|
| [Tipo_1]   | Unit          | [Framework] |
| [Tipo_2]   | Integration   | [Framework] |
| [Tipo_3]   | E2E           | [Framework] |
