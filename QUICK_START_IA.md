# 🚀 QUICK START - LOTOSCOPE
## Resumo Ultra-Rápido para IAs

> **Leia isto primeiro!** Se precisar de mais detalhes:
> - `CONTEXTO_MASTER_IA.md` - Visão geral completa
> - `REFERENCIA_TECNICA_IA.md` - Código e APIs

---

## O QUE É

**LotoScope** = Sistema Python para gerar combinações otimizadas da **Lotofácil** (loteria BR)

## DADOS CHAVE

```
Lotofácil: 15 números de 25 (1-25)
Banco: SQL Server localhost, database "Lotofacil", tabela "Resultados_INT"
~3.592 concursos históricos
Prêmio máximo: 15 acertos = R$ 1.8 milhão
```

## COMANDO PRINCIPAL

```powershell
cd "C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\interfaces"
python super_menu.py
```

## ESTRATÉGIAS ATUAIS (Jan/2026)

### 1. Sistema C1/C2 Complementar (Opção 22 → Opção 6)
```python
DIV_C1 = [1, 3, 4]      # Divergentes Combo 1
DIV_C2 = [15, 17, 18]   # Divergentes Combo 2
NUCLEO = [6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]  # 17 núcleo
```

### 2. Filtro Noneto Personalizado (Opção 22 → Opção 7)
```python
# Noneto = 9 números que concentram acertos
NONETO = [1, 2, 4, 8, 10, 13, 20, 24, 25]
# Em 80% dos sorteios: 5-7 desses números são sorteados
```

### 3. Conferidor Simples (Opção 23) ⭐ NOVO!
```python
# Confere TXT de combinações contra resultados
# 3 modos: TODOS, RANGE (3470-3475), ou MANUAL
# Análise financeira: Custo × Prêmio = Lucro/ROI
CUSTO_APOSTA = 3.50
PREMIOS = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}
```

### 4. Association Rules v2.0 (Opção 7.12 → Opção 10) ⭐ NOVO!
```python
# Descobre padrões: X → Y, X → ¬Y, {X,Y} → Z
# Métricas: Support, Confidence, Lift, Conviction, Zhang's Interest
# Explorer dedicado com 9 opções
```

### 5. Gerador Mestre Unificado (Opção 29) ⭐⭐⭐ MÁXIMO!
```python
# INTEGRA TODO O CONHECIMENTO DO SISTEMA:
# - Frequência geral (últimos 30/50/100 concursos)
# - Sistema C1/C2 (divergentes e tendência)
# - Filtro Noneto (concentração de acertos 5-7)
# - Análise Linhas/Colunas (remoção de frios L1-L5, C1-C5)
# - Regras de Associação (pares frequentes/raros)
# - Padrões estruturais (soma, pares/ímpares, primos)

# Sistema de scoring multi-camada (0-100 pontos):
# - Frequência: 0-20 pts
# - C1/C2: 0-15 pts
# - Noneto: 0-15 pts
# - Linhas/Colunas: 0-20 pts
# - Associações: 0-10 pts
# - Estrutura: 0-20 pts

# Modos de geração:
# 1. RÁPIDA: 1.000 combinações → filtra TOP N
# 2. MÉDIA: 10.000 combinações → filtra TOP N
# 3. INTENSIVA: 100.000 combinações → filtra TOP N
# 4. PERSONALIZADA: você define quantidade
```

### 6. Combinações Complementares Reversas (Opção 19.3) ⭐ NOVO!
```python
# Estratégia matemática: Principal + Reversa
# Pool A: 20 números favorecidos
# Pool B: 5 números complementares
# Se |S ∩ A| = 12-13, então |S ∩ B| = 2-3

# Principal: 12-13 de A + 2-3 de B (foco no favorecido)
# Reversa: Maximiza B (hedge contra escape do padrão)

# Modos de pareamento:
# 1. ALEATÓRIO: Principal e Reversa independentes
# 2. COMPLEMENTAR: Reversa minimiza repetição
# 3. OPOSTO: Reversa = 26 - Principal
```

### 7. Gerador Pool 23 Híbrido (Opção 31) ⭐⭐⭐ BREAKTHROUGH!
```python
# ESTRATÉGIA TESTADA COM 21% DE TAXA DE JACKPOT!
# Exclui apenas 2 números usando análise híbrida

# Lógica de exclusão:
# 1. Números MEDIANOS (próximos da média de frequência)
# 2. Em TENDÊNCIA DE QUEDA (curto < médio < longo prazo)
# 3. NÃO extremos (nem muito quentes, nem muito frios)

# FILTROS DINÂMICOS VALIDADOS:
# - REVERSÃO DE SOMA: 82-97% assertividade (3610 concursos validados)
# - COMPENSAÇÃO POSICIONAL: 64% assertividade
# - MAPA TÉRMICO POSICIONAL: até 84% assertividade ⭐ NOVO!

# 7 NÍVEIS DE FILTROS:
# Nível 0: SEM FILTROS (490.314 combos)
# Nível 1: SOMA DINÂMICA + MAPA TÉRMICO (até 97% assertividade)
# Nível 2: BÁSICO - RECOMENDADO JACKPOT ⭐
#          SOMA + PARES + PRIMOS + COMP. POSICIONAL + MAPA TÉRMICO
# Nível 3: EQUILIBRADO (+ sequência máx 6)
# Nível 4: MODERADO (+ repetição 4-11)
# Nível 5: AGRESSIVO - ROI OTIMIZADO (+ núcleo ≥9)
# Nível 6: ULTRA (mínimo custo, + favorecidos ≥5)

# RESULTADOS REAIS (Concurso 3610):
# Nível 2: 367k combos, JACKPOT ✅, ROI +118.6%
# Nível 6: 2.3k combos, sem jackpot, ROI +16.6%

CUSTO_APOSTA = 3.50
```

### 8. Mapa Térmico Posicional (Opção 31 → Sub-opção 2) ⭐ NOVO!
```python
# VISUALIZAÇÃO: Números MENOS PROVÁVEIS por posição (N1-N15)
# Baseado em 3 indicadores validados:

# 1. REPETIÇÃO NA MESMA POSIÇÃO (69% assertividade)
#    → Após 3+ repetições, número tende a MUDAR

# 2. FREQUÊNCIA RECENTE NA POSIÇÃO (84% assertividade!) ⭐
#    → Número muito frequente (4+ em 10) tende a NÃO repetir

# 3. SOMA + SALDO COMBINADOS (60-62% assertividade)
#    → Indica direção geral (números altos/baixos)

# FILTRO INTEGRADO:
# Rejeita combinações com >2 números improváveis em posições erradas
# Tolerância flexível para não perder jackpots
```

### 9. Backtesting Pool 23 (Opção 30 → Sub-opção 2) ⭐⭐ NOVO!
```python
# TESTE AUTOMATIZADO de todos os níveis do Pool 23
# Fluxo:
# 1. Pergunta se quer ajustar números excluídos (S/N)
# 2. Se N → usa sugestão automática (estratégia híbrida)
# 3. Gera TODOS os níveis (0-6) automaticamente
# 4. Salva arquivos de cada nível em dados/
# 5. Pergunta o resultado sorteado (entrada manual - concurso futuro)
# 6. Valida TODOS os arquivos contra o resultado
# 7. Exibe tabela comparativa com ROI de cada nível

# Output:
# ┌─────────────────────────────────────────────────────────────────┐
# │ NÍVEL │ COMBOS │  CUSTO  │ 11ac │ 12ac │ 13ac │ 14ac │ 15ac │   │
# │   0   │ 490k   │ R$1.7M  │ xxx  │ xxx  │ xxx  │  xx  │  x   │   │
# │   2   │ 370k   │ R$1.3M  │ xxx  │ xxx  │ xxx  │  xx  │  x   │ ⭐│
# │  ...  │  ...   │  ...    │ ...  │ ...  │ ...  │ ...  │ ...  │   │
# └─────────────────────────────────────────────────────────────────┘
```

### ⚠️ PADRÃO EM TODOS OS GERADORES
```python
# TODOS os geradores permitem:
# - Gerar quantidade específica (ex: 50, 100, 500)
# - Gerar TODAS as possíveis (digite 0 ou 'TODAS')
# Isso permite análise completa do universo de combinações
```

## ARQUIVOS IMPORTANTES

```
super_menu.py                    # Menu principal (12000+ linhas)
sistema_aprendizado_ml.py        # ML com 15 algoritmos (Association Rules v2.0)
combo20_FILTRADAS_TOP1000.txt    # 1000 melhores combinações C1
combo20_C2_tendencia.txt         # 1000 melhores combinações C2
dados/noneto_personalizado.txt   # Noneto salvo pelo usuário
dados/mestre_unificado_*.txt     # Combinações do Gerador Mestre
dados/backtest_pool23_*.txt      # Combinações do Backtesting Pool 23
```

## CONEXÃO BANCO

```python
import pyodbc
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
```

## RESULTADO VALIDADO

✅ **15 acertos** (jackpot) no concurso 3474 com 50 combinações
✅ **15 acertos** (jackpot) no concurso 3610 com Pool 23 Híbrido (Opção 31)

---

## ANÁLISE ECONÔMICA

| Estratégia | Combos | Custo | Jackpot? | ROI |
|------------|--------|-------|----------|-----|
| Pool 23 Nível 2 | ~370k | R$ 1.3M | ✅ Alta | +118% |
| Pool 23 Nível 6 | ~2.3k | R$ 8k | ❌ Baixa | +16% |
| Gerador Mestre | 1-100k | variável | Média | variável |

**Descoberta:** Pool 23 com Nível 2 (Básico) é o melhor custo-benefício para jackpot!

---

> Para detalhes: `CONTEXTO_MASTER_IA.md`
> Última atualização: 13/02/2026
