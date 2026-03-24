# 🏛️ DOMAIN RULES — LotoScope

**Propósito:** Regras "golden rules" que NÃO podem ser quebradas  
**Escopo:** Projeto inteiro  
**Prioridade:** Máxima — violar qualquer regra aqui é um bug  
**Atualizado:** 24/03/2026

---

## 🚨 Como Usar Este Arquivo

Cada regra aqui é **inviolável**. A IA (Copilot/Claude/Gemini) deve:
1. Verificar contra estas regras ANTES de gerar código
2. Alertar o desenvolvedor se código existente violar
3. Recusar sugestões que violem qualquer regra

---

## 🚨 REGRA 1: Integridade dos Números — 1 a 25, sempre 15

### Descrição
A Lotofácil usa exatamente 25 números (1-25). Cada combinação válida tem EXATAMENTE 15 números distintos. Nenhuma exceção.

### ❌ Violação (NUNCA fazer)

```python
# Número fora do range:
combo = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 26]  # ERRADO: 0 e 26 inválidos

# Menos de 15 números:
combo = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # ERRADO: só 10

# Repetição:
combo = [1, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # ERRADO: 1 aparece 2x
```

### ✅ Correto (SEMPRE fazer)

```python
def is_valid_combo(combo) -> bool:
    nums = sorted(combo)
    return (len(nums) == 15 and
            len(set(nums)) == 15 and
            all(1 <= n <= 25 for n in nums))

# Validar antes de qualquer operação:
assert is_valid_combo(minha_combo), f"Combo inválida: {minha_combo}"
```

---

## 🚨 REGRA 2: Banco de Dados — SOMENTE SQL Server

### Descrição
O projeto usa SQL Server (localhost, Windows Auth) como único banco de dados de produção. Nunca substituir por SQLite, CSV, ou outros para análises com dados reais.

### ❌ Violação

```python
# NUNCA usar SQLite para análises reais:
import sqlite3
conn = sqlite3.connect("LotoScope.db")  # PROIBIDO em produção

# NUNCA hardcodar resultados (usar banco):
resultados = [(1,2,3,...)]  # PROIBIDO — sempre buscar do SQL Server
```

### ✅ Correto

```python
import pyodbc
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
with pyodbc.connect(CONN_STR) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT N1,...,N15 FROM Resultados_INT ORDER BY Concurso DESC")
```

---

## 🚨 REGRA 3: SQL Injection Prevention — Sempre Parâmetros

### Descrição
Nunca concatenar valores diretamente em strings SQL. Sempre usar parâmetros `?` do pyodbc.

### ❌ Violação

```python
# PROIBIDO — SQL injection:
concurso = input("Concurso: ")
cursor.execute(f"SELECT * FROM Resultados_INT WHERE Concurso = {concurso}")
cursor.execute("SELECT * FROM Resultados_INT WHERE Concurso = " + str(concurso))
```

### ✅ Correto

```python
cursor.execute("SELECT * FROM Resultados_INT WHERE Concurso = ?", (int(concurso),))
```

---

## 🚨 REGRA 4: Encoding UTF-8 Obrigatório

### Descrição
Todos os arquivos Python e TXT devem usar UTF-8. O projeto tem acentos e emojis — sem encoding explícito, falha no Windows.

### ❌ Violação

```python
open("resultado.txt")                        # PROIBIDO — encoding implícito
open("resultado.txt", encoding='latin-1')   # PROIBIDO — perda de dados
```

### ✅ Correto

```python
open("resultado.txt", encoding='utf-8')
open("resultado.txt", 'w', encoding='utf-8')
```

---

## 🚨 REGRA 5: Parâmetros Históricos Não Retroativos

### Descrição
Em backtesting, os dados usados para calcular exclusão/scores DEVEM ser anteriores ao concurso sendo testado. Nunca usar dados futuros para decidir exclusões passadas (data leakage).

### ❌ Violação

```python
# PROIBIDO — usar todos os dados para decidir exclusão do concurso X:
todos_os_resultados = carregar_tudo()
excluidos = calcular_exclusao(todos_os_resultados)  # Inclui concursos DEPOIS de X
resultado_x = testar_combo(excluidos, concurso_x)   # RESULTADO INVÁLIDO
```

### ✅ Correto

```python
# Usar APENAS dados ANTERIORES ao concurso X:
resultados_antes_x = [r for r in todos if r['concurso'] < concurso_x]
excluidos = calcular_exclusao(resultados_antes_x)   # Apenas passado
resultado_x = testar_combo(excluidos, concurso_x)   # Válido
```

---

## 🚨 REGRA 6: Improbabilidade Posicional Desativada em Levels 4-6

### Descrição
O filtro "Improbabilidade Posicional" está **desativado** nos Pool 23 Levels 4, 5 e 6. Ativá-lo nesses levels causa perda de jackpots (resultado validado em análise de mar/2026).

### ❌ Violação

```python
# PROIBIDO em levels 4-6:
if nivel >= 4:
    combos = aplicar_improbabilidade_posicional(combos)  # ERRADO — perde jackpots
```

### ✅ Correto

```python
# Improbabilidade Posicional APENAS em levels 1-3:
if nivel <= 3:
    combos = aplicar_improbabilidade_posicional(combos, tolerancia=2)
# Levels 4-6: NÃO aplicar este filtro
```
```
[código errado]
```

### ✅ Correto

```
[código correto]
```

### Impacto de Violação
- [Consequência]

---

## 🚨 REGRA 3: [NOME DA REGRA]

### Descrição
[Descreva a regra]

### ❌ Violação

```
[código errado]
```

### ✅ Correto

```
[código correto]
```

---

<!-- 
EXEMPLOS DE REGRAS COMUNS (copie as relevantes):

## Segurança
- Nunca logar dados sensíveis (CPF, senha, token)
- Nunca construir SQL por concatenação de strings
- Credenciais sempre via variáveis de ambiente
- Todo input externo deve ser validado

## Arquitetura  
- Camada X nunca depende de camada Y diretamente
- Entity/Model nunca exposto na API (usar DTO)
- Lógica de negócio NUNCA no controller/handler
- Um service não pode chamar outro service diretamente (usar events/mediator)

## Dados
- Soft delete obrigatório (nunca DELETE físico)
- Todo registro tem created_at e updated_at
- IDs são UUID, nunca auto-increment exposto
- Paginação obrigatória em listagens

## Qualidade
- Métodos com no máximo [N] linhas
- Complexidade ciclomática máxima: [N]
- Todo branch novo precisa de testes
- Code review obrigatório antes de merge
-->

---

## 📋 Checklist Rápido

Antes de fazer merge/commit, verifique:

- [ ] Nenhuma regra acima foi violada
- [ ] Código segue coding-standards.md
- [ ] Testes passam
- [ ] Sem secrets/credentials no código
- [ ] Logging adequado (sem dados sensíveis)
