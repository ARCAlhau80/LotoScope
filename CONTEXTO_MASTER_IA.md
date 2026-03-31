# 🎯 CONTEXTO MASTER PARA AGENTES IA - LOTOSCOPE
## Documentação Completa e Unificada do Sistema

> **IMPORTANTE**: Este arquivo é a FONTE ÚNICA DE VERDADE para qualquer agente de IA
> trabalhando no projeto LotoScope. Mantenha-o atualizado após cada sessão significativa.

```
📅 ÚLTIMA ATUALIZAÇÃO: 30/03/2026
👤 AUTOR: AR CALHAU
🤖 VALIDADO POR: Claude Sonnet 4.6
```

---

## 📋 SUMÁRIO EXECUTIVO

O **LotoScope** é um sistema científico completo para análise estatística e geração inteligente de combinações para a **Lotofácil** (loteria brasileira). O sistema combina:

- **Análise estatística avançada** de 3.615+ concursos históricos
- **Redes neurais** e machine learning para padrões
- **Interface web Flask** para interação
- **Menu console (super_menu.py)** com 31+ sistemas integrados
- **Sistema de aprendizado** que rastreia erros e acertos

### 🏆 RESULTADOS VALIDADOS
✅ **15 ACERTOS (PRÊMIO MÁXIMO)** no Concurso 3474 (50 combinações)
✅ **15 ACERTOS (PRÊMIO MÁXIMO)** no Concurso 3610 (Pool 23 Híbrido)
✅ **15 ACERTOS (PRÊMIO MÁXIMO)** no Concurso 3615 (Pool 23 Nível 6, **ROI +2841%**!)
✅ **LUCRO SEM JACKPOT** em 01/03/2026: Nível 3 (+14.3%) e Nível 5 (+33.3%) ⭐ NOVO!

---

## 📊 MCP-GRAPH WORKFLOW (11/03/2026)

Sistema de gestão de tasks via grafo visual instalado para organizar sprints e desenvolvimento.

### Iniciar Dashboard
```powershell
.\start-mcp-graph.bat
# ou
$env:Path = "C:\Program Files\nodejs;" + $env:Path
npx -y @mcp-graph-workflow/mcp-graph serve --port 3000
```

**Dashboard**: http://localhost:3000

### Dados Importados
- **24 nodes** criados a partir do CONTEXTO_MASTER_IA.md
- **4 edges** (dependências)
- Grafo em: `workflow-graph/graph.db`

### Fluxo de Trabalho
```
next → context → [implementar] → update_status → next
```

Ver `CLAUDE.md` e `.github/copilot-instructions.md` para documentação completa.

---

## 🎲 ENTENDENDO A LOTOFÁCIL

### Regras Básicas
```
- 25 números disponíveis (1 a 25)
- Jogador escolhe 15 números por aposta
- Sorteio: 15 números aleatórios
- Premiação: acertar 11, 12, 13, 14 ou 15 números
```

### Tabela de Prêmios (valores médios)
| Acertos | Prêmio Médio | Probabilidade |
|---------|--------------|---------------|
| 11      | R$ 7,00      | 1 em 11       |
| 12      | R$ 14,00     | 1 em 60       |
| 13      | R$ 35,00     | 1 em 691      |
| 14      | R$ 1.000,00  | 1 em 21.621   |
| 15      | R$ 1.800.000 | 1 em 3.268.760|

### Custo por Aposta
- 15 números: R$ 3,00
- 16 números: R$ 48,00 (16 apostas)
- 17 números: R$ 408,00 (136 apostas)
- 18 números: R$ 2.448,00 (816 apostas)
- 19 números: R$ 11.628,00 (3.876 apostas)
- 20 números: R$ 46.512,00 (15.504 apostas)

---

## 🗄️ INFRAESTRUTURA TÉCNICA

### Banco de Dados
```
Servidor:    localhost (SQL Server)
Database:    Lotofacil
Driver:      ODBC Driver 17 for SQL Server
Autenticação: Windows (Trusted_Connection=yes)
```

### Tabela Principal: `Resultados_INT`
```sql
- Concurso (INT)           -- Número sequencial do concurso
- N1 a N15 (INT)           -- Os 15 números sorteados (ordenados)
- Data_Sorteio (VARCHAR)   -- Data do sorteio
- Campos estatísticos      -- Métricas calculadas
```

### Dados Atuais
- **~3.592 concursos** carregados (Jan/2026)
- Primeiro concurso: 2003
- Frequência: 3x por semana (Seg, Qua, Sex)

### Ambiente de Desenvolvimento
```
OS:          Windows 11
IDE:         VS Code
Python:      3.11+
Frameworks:  Flask, PyODBC, NumPy, Pandas
Diretório:   C:\Users\AR CALHAU\source\repos\LotoScope\
```

---

## 📁 ESTRUTURA DO PROJETO

```
LotoScope/
├── lotofacil_lite/                    # Diretório principal
│   ├── interfaces/
│   │   ├── super_menu.py              # ⭐ MENU PRINCIPAL (4000+ linhas)
│   │   ├── super_menu_final.py        # Versão Flask do menu
│   │   └── super_menu_web.py          # Interface web
│   │
│   ├── geradores/                     # Scripts de geração
│   │   ├── gerador_academico_dinamico.py
│   │   ├── gerador_zona_conforto.py
│   │   └── gerador_complementacao_inteligente.py
│   │
│   ├── analisadores/                  # Scripts de análise
│   │   ├── estrategia_combo20.py      # ⭐ Sistema C1/C2
│   │   ├── analisador_retorno_garantido.py
│   │   ├── filtro_rapido.py
│   │   └── gerador_c1_c2_complementar.py
│   │
│   ├── web/                           # Servidor web Flask
│   │   ├── backend/
│   │   │   └── app.py
│   │   └── frontend/
│   │
│   ├── ia_repetidos/                  # Dados de IA
│   │   ├── feedback_resultados.json
│   │   └── historico_aprendizado.json
│   │
│   └── *.txt                          # Arquivos de combinações geradas
│
├── CONTEXTO_MASTER_IA.md              # ⭐ ESTE ARQUIVO
├── AGENTE_LOTOSCOPE_CONTEXTO.md       # Contexto antigo (backup)
└── README_AUTO_TREINO.md              # Documentação auto-treino
```

---

## 🎯 SUPER MENU - OPÇÕES DISPONÍVEIS

O arquivo `super_menu.py` é o **centro de controle** do sistema. Acesso:
```bash
cd lotofacil_lite/interfaces
python super_menu.py
```

### Menu Principal (23 Opções)
```
1️⃣  🧠 IA DE NÚMEROS REPETIDOS
2️⃣  🎯 GERADOR ACADÊMICO DINÂMICO
2️⃣.1 🔒 GERADOR TOP FIXO
2️⃣.2 🎯 GERADOR ZONA DE CONFORTO
3️⃣  🔥 SUPER GERADOR COM IA (RECOMENDADO)
4️⃣  🔺 PIRÂMIDE INVERTIDA DINÂMICA
5️⃣  📊 ANÁLISES E ESTATÍSTICAS
6️⃣  🧠 SISTEMA APRENDIZADO E PERFORMANCE
7️⃣  🧠 COMPLEMENTAÇÃO INTELIGENTE
7️⃣.1 🎯 SISTEMA ULTRA-PRECISÃO V4
7️⃣.2 🧠 SISTEMA NEURAL V7
7️⃣.12 📊 SISTEMA APRENDIZADO ML (15 algoritmos)
7️⃣.13 📊 ANÁLISE NÚMERO × POSIÇÃO
... (continua até opção 22)
2️⃣2️⃣ 🎯 ESTRATÉGIA COMBO 20 (DIVERGENTES) ⭐
2️⃣3️⃣ ✅ CONFERIDOR SIMPLES ⭐ NOVO!
```

---

## 🔥 ESTRATÉGIA COMBO 20 - SISTEMA C1/C2 (CRÍTICO)

### Conceito Fundamental
A Lotofácil tem 25 números. Descobriu-se que existem **duas combinações de 20 números** que são **mutuamente excludentes** em 3 números cada:

```python
COMBO1 = [1,3,4, 6,7,8,9,10,11,12,13,14, 16, 19,20,21,22,23,24,25]  # 20 números
COMBO2 = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]  # 20 números

# Divergentes (aparecem em apenas uma combo)
DIV_C1 = [1, 3, 4]      # Exclusivos da Combo 1
DIV_C2 = [15, 17, 18]   # Exclusivos da Combo 2

# Núcleo Comum (17 números presentes em ambas)
NUCLEO = [6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]

# Fora de ambas as combos
FORA_AMBAS = [2, 5]
```

### Por que isso é importante?
- Todo sorteio **OBRIGATORIAMENTE** tem pelo menos 1 divergente de C1 **OU** C2
- Analisar a **tendência** dos últimos concursos permite prever qual combo está "quente"
- Filtrar combinações pelo **núcleo** (≥13 números) aumenta probabilidade de acerto

### Arquivos Gerados pelo Sistema C1/C2
```
combo20_FILTRADAS_TOP1000.txt      # 1000 melhores combinações C1
combo20_C2_tendencia.txt           # 1000 melhores combinações C2
combo20_C1_TOP50_*.txt             # Exportações personalizadas
```

### Submenu da Opção 22 (Estratégia Combo 20)
```
1️⃣  Ver tendência atual (últimos 100 concursos)
2️⃣  Ver sugestão de estratégia
3️⃣  Gerar combinações (CONFIGURÁVEL)
4️⃣  Gerar combinações (RÁPIDO - estratégia sugerida)
5️⃣  Gerar com COMPLEMENTARES (Principal + Hedge)
6️⃣  🔄 ANÁLISE C1/C2 COMPLEMENTAR (TOP FILTRADAS)
7️⃣  🔢 FILTRO POR NONETO PERSONALIZADO ⭐ NOVO!
```

### Opção 6 - Análise C1/C2 Complementar
1. Analisa os últimos 20 concursos
2. Conta divergentes C1 vs C2 em cada resultado
3. Determina tendência (C1 ou C2 favorável)
4. Carrega combinações pré-filtradas do arquivo correto
5. Permite escolher quantidade (10, 25, 50, 100, 1000)
6. Salva arquivo com timestamp

### Opção 7 - Filtro por Noneto Personalizado ⭐ NOVO! (24/01/2026)
Um **NONETO** é um conjunto de 9 números que concentram acertos:

```python
# Noneto padrão descoberto
NONETO = [1, 2, 4, 8, 10, 13, 20, 24, 25]

# Estatísticas validadas:
# - 79% dos sorteios têm 5-7 desses números
# - 80% nos últimos 30 concursos (5-7)
# - Média: 5.47 acertos
```

**Funcionalidades:**
1. Usar noneto padrão ou definir personalizado
2. Analisar distribuição de acertos (histórico completo)
3. Ver faixas de concentração (5-7, 5-8, 6-7)
4. Calcular poder de redução
5. Buscar melhores nonetos automaticamente (amostra 5.000)
6. Salvar noneto para uso futuro

---

## 📊 PADRÕES DE RETORNO GARANTIDO

### Descoberta Matemática
Ao gerar combinações com a estratégia Combo 20, observam-se **percentuais de retorno recorrentes**:
- 131.02% (maioria acerta ≥11)
- 26.50%
- 8.05%

Isso ocorre porque o retorno é uma **média ponderada** discreta das combinações que atingem cada faixa de acerto.

### Histórico de Validação (últimos 100 concursos)
```
Quando C1 favorável → Jogar C1 performa melhor
Quando C2 favorável → Jogar C2 dá lucro positivo (+R$1.305)
Complementaridade real: 4 concursos onde um lucra e outro perde
```

---

## ✅ OPÇÃO 23 - CONFERIDOR SIMPLES ⭐ NOVO! (27/01/2026)

### Funcionalidade
Confere automaticamente as combinações de um arquivo TXT contra resultados reais do banco de dados.

### Modos de Operação
```
1️⃣ TODOS - Confere contra todos os concursos no banco
2️⃣ RANGE - Confere de concurso X até Y (ex: 3470-3475)
3️⃣ MANUAL - Digita os números do resultado manualmente
```

### Análise Financeira Integrada
```python
CUSTO_APOSTA = 3.50  # Reais
PREMIOS = {
    11: 7.00,        # 11 acertos
    12: 14.00,       # 12 acertos
    13: 35.00,       # 13 acertos
    14: 1000.00,     # 14 acertos
    15: 1800000.00   # 15 acertos (Jackpot!)
}
```

### Saída do Conferidor
```
📊 RESULTADO DO CONFERIMENTO
══════════════════════════════════════
Combinações conferidas: 50
Concursos analisados: 6

📈 Distribuição de Acertos:
  11 acertos: 23 combinações (R$ 161,00)
  12 acertos: 8 combinações (R$ 112,00)
  13 acertos: 2 combinações (R$ 70,00)
  14 acertos: 0 combinações (R$ 0,00)
  15 acertos: 0 combinações (R$ 0,00)

💰 ANÁLISE FINANCEIRA:
  Custo total: R$ 1.050,00 (50 apostas × 6 concursos × R$3,50)
  Prêmio total: R$ 343,00
  Lucro/Prejuízo: -R$ 707,00
  ROI: -67.3%
```

---

## 🔬 ASSOCIATION RULES v2.0 (Opção 7.12 → Opção 10)

### Conceito
Association Rules (Regras de Associação) descobrem padrões como:
- "Se número 7 sai, então 14 também sai com 68% de confiança"
- "Se números 3 e 12 saem juntos, então 21 sai com 72% de confiança"

### Métricas Implementadas
```python
# Suporte: Frequência da regra no histórico
support = count(X, Y) / total_draws

# Confiança: P(Y|X) - probabilidade condicional
confidence = support(X, Y) / support(X)

# Lift: Quanto a regra é melhor que o acaso
lift = confidence / support(Y)

# Conviction: Força da implicação
conviction = (1 - support(Y)) / (1 - confidence)

# Zhang's Interest: Métrica balanceada
zhang = (confidence - support(Y)) / max(confidence*(1-support(Y)), support(Y)*(1-confidence))
```

### Tipos de Regras
```
1️⃣ POSITIVAS: X → Y (7 → 14, confiança 68%)
2️⃣ NEGATIVAS: X → ¬Y (3 → ¬22, confiança 45%)
3️⃣ MULTI-ANTECEDENTE: {X, Y} → Z ({3, 12} → 21, confiança 72%)
```

### Submenu Explorer (Opção 10)
```
╔═══════════════════════════════════════════════════╗
║     🔬 EXPLORER DE ASSOCIATION RULES              ║
╠═══════════════════════════════════════════════════╣
║ 1. 📊 Ver Regras Positivas (TOP 30)               ║
║ 2. 📊 Ver Regras Negativas (TOP 30)               ║
║ 3. 📊 Ver Regras Multi-Antecedente (TOP 30)       ║
║ 4. ⚠️  Ver Números a Evitar                       ║
║ 5. 🎯 Gerar 1 Combinação (baseada em regras)      ║
║ 6. 🎯 Gerar 10 Combinações                        ║
║ 7. 📈 Ver Ranking Completo (todas as regras)      ║
║ 8. 📊 Ver Estatísticas Gerais                     ║
║ 9. 🔙 Voltar                                      ║
╚═══════════════════════════════════════════════════╝
```

### Geração de Combinações com Regras
O sistema usa as regras descobertas para gerar combinações:
1. Coleta regras positivas com lift > 1.1
2. Identifica números a evitar (regras negativas fortes)
3. Constrói combinação priorizando números com mais regras positivas
4. Penaliza números identificados nas regras negativas

---

## 🔧 COMANDOS FREQUENTES

### Executar Super Menu
```powershell
cd "C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\interfaces"
python super_menu.py
```

### Executar Análise C1/C2 Diretamente
```python
from super_menu import SuperMenuLotofacil
menu = SuperMenuLotofacil()
menu.executar_analise_c1c2_complementar()
```

### Conexão com Banco de Dados
```python
import pyodbc
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT TOP 10 * FROM Resultados_INT ORDER BY Concurso DESC')
    for row in cursor.fetchall():
        print(row)
```

### Carregar Combinações de Arquivo
```python
def carregar_combinacoes(arquivo):
    combinacoes = []
    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                nums = [int(n) for n in linha.split(',')]
                if len(nums) == 15:
                    combinacoes.append(nums)
    return combinacoes
```

---

## 🚨 PONTOS DE ATENÇÃO PARA IAs

### ⚠️ SEMPRE VERIFICAR
1. **Número do último concurso** - Muda 3x por semana
2. **Tendência C1/C2** - Recalcular antes de recomendar
3. **Arquivos existentes** - Verificar se foram gerados

### ⚠️ NÃO ASSUMIR
1. Que o banco de dados está atualizado (perguntar)
2. Que os arquivos .txt existem (verificar com `os.path.exists`)
3. Que o usuário quer gerar combinações (pode só querer análise)

### ⚠️ CUIDADO COM
1. **Escapamento de strings** em comandos Python inline
2. **Caminhos absolutos** vs relativos
3. **Encoding UTF-8** em arquivos

---

## 📈 MÉTRICAS DE SUCESSO

### Objetivo Principal
- **Meta**: 50%+ das combinações com ≥11 acertos
- **Ideal**: Maximizar combinações com 13+ acertos

### Indicadores de Performance
```
✅ Bom:   Média ≥10.5 acertos por combinação
✅ Ótimo: Média ≥11.0 acertos por combinação
✅ Excelente: Qualquer combinação com 14+ acertos
🏆 Jackpot: 15 acertos (já alcançado no concurso 3474)
```

---

## 🔄 FLUXO DE TRABALHO TÍPICO

### Para Gerar Combinações para Próximo Concurso
```
1. Executar super_menu.py
2. Opção 22 (Estratégia Combo 20)
3. Opção 6 (Análise C1/C2 Complementar)
4. Ver tendência → Escolher C1 ou C2
5. Selecionar quantidade (ex: 50)
6. Salvar arquivo
7. Jogar as combinações geradas
```

### Para Analisar Resultado Após Sorteio
```
1. Atualizar banco de dados com novo resultado
2. Verificar acertos das combinações jogadas
3. Analisar se tendência se confirmou
4. Ajustar estratégia se necessário
```

---

## 📝 HISTÓRICO DE SESSÕES IMPORTANTES

### 31/03/2026 - NOVAS FEATURES: Neural FRIOS Diagnostic + Neural PURO como padrão ⭐⭐ NOVO!

**1. Diagnóstico "FRIOS FAVORECIDOS PELA NEURAL" — Forma 1**

Bloco diagnóstico adicionado em **DOIS lugares** no `super_menu.py`:
- **Opção 31** (~linha 12537): após o ranking híbrido neural, exibe números frios (ausentes ≥ 2 sorteios) ordenados por score neural ascendente. Score baixo = neural prevê que o número vai retornar.
- **Opção 30→[6]** (~linha 15470): após o resumo do benchmark, carrega a rede neural fresh, chama `_extrair_features(idx_ultimo)` + `obter_scores()`, exibe a mesma tabela diagnóstica.

Sistema de rating:
- ⭐ FORTE: score < 0.30
- candidato: score < 0.45
- neutro: demais

Exibe até 5 candidatos frios. **Somente diagnóstico — não altera a lógica de geração.**
Validado: última execução identificou {3, 6, 23} com scores 0.400, 0.404, 0.443.

---

**2. Estratégia Neural PURO — novo padrão na Opção 31**

O menu de estratégia da Opção 31 agora apresenta **TRÊS opções**:
```
[N] Neural PURO ⭐⭐ MELHOR!   ← NOVO, agora padrão (ENTER = N)
[H] Híbrido Neural+INVERTIDA   ← antigo padrão (+3.3pp)
[I] INVERTIDA v3.0             ← clássico
```

**Benchmark validado (31/03/2026):**
- Neural PURO: **22.9%** vs INVERTIDA v3.0: **15.2%** = **+7.7pp acima da INVERTIDA** ✅
- Resultado anterior (Híbrido): +3.3pp — o novo treinamento melhorou significativamente

Implementação: Neural PURO usa `scores_neural` dict diretamente (25 números ordenados por score descendente, sem combinar com INVERTIDA). A tela de ajuste manual também exibe o TOP 10 NEURAL.

**Arquivos alterados:**
- `lotofacil_lite/interfaces/super_menu.py` — bloco FRIOS adicionado na Opção 31 (~l.12537) e Opção 30→[6] (~l.15470); menu de estratégia da Opção 31 atualizado com [N]/[H]/[I]

---

### 30/03/2026 - NOVA FEATURE: Opção 30→[6] Retreinar Rede Neural + Benchmark ⭐⭐ NOVO!
**Descrição:**
O menu de Backtesting (Opção 30) ganhou a sub-opção **[6] Retreinar Rede Neural + Benchmark**, que permite treinar, continuar treinando ou apenas comparar a performance da rede neural contra a estratégia Invertida v3.0.

**Modos disponíveis:**
```
[T] Treinar do zero      — descarta pesos anteriores e reinicia
[C] Continuar treinando  — fine-tuning sobre pesos salvos
[B] Benchmark apenas     — compara sem retreinar
```

**Períodos pré-definidos:**
- Últimos 500, 1.000 ou 2.000 concursos
- Todo o histórico disponível
- Personalizado (intervalo manual)

**Resumo final exibido:**
- Comparativo Neural vs INVERTIDA com diagnóstico emoji: 🎉 (Neural vence), 📊 (Invertida vence), 🤝 (empate)

**Arquitetura da Rede Neural (referência):**
```
Entrada:  150 features  (6 features × 25 números)
Oculta 1: 256 neurônios (ReLU)
Oculta 2: 128 neurônios (ReLU)
Oculta 3:  64 neurônios (ReLU)
Saída:     25 neurônios (Sigmoid)
Total:  81.433 parâmetros treináveis
```

**Features de entrada (6 por número):**
`freq_30`, `atraso`, `consecutividade`, `tendência`, `freq_10`, `score_INVERTIDA`

> 🔴 **EM RADAR — Risco de Overfitting (não implementado ainda):**
> - Razão parâmetros/amostras: ~40:1 (81k params / 2.000 amostras) → alto risco
> - Gap observado: treino chegou a 25.3% mas validação ficou em 18.6% (+6.7pp de gap)
> - Proposta futura: reduzir arquitetura para 150→64→32→25 + L2 regularização + Dropout
> - **DECISÃO PENDENTE**: usuário vai retreinar com até 500 iterações primeiro, depois decide

**Correção conceitual — contagem de concursos:**
- `Resultados_INT` tem 3.647 linhas totais
- 3.617 utilizáveis = 3.647 − 30 (buffer mínimo de histórico para calcular features)
- O número 3.617 **NÃO é bug** — é comportamento correto de `idx_inicio_real = max(30, idx_inicio)`

**Arquivos alterados:**
- `lotofacil_lite/interfaces/super_menu.py` — adicionado opção [6] no menu da Opção 30 e método `_executar_retreino_neural_benchmark()`

**Nota:** A mesma rede neural (e arquitetura) é compartilhada com Opção 30→[5] (Disputa Neural) e Opção 31 (Pool 23 Híbrido).

---

### 24/03/2026 - NOVA FEATURE: Seleção de Estratégia de Exclusão na Opção 30.2 ⭐⭐⭐ NOVO!
**Descrição:**
O Backtesting Pool 23 (Opção 30 → 2) ganhou seleção de estratégia de exclusão com diagnóstico comparativo.

**PASSO 1 — Menu de Estratégia (exibido antes da geração):**
```
[0] Comparar todas   [1] Débito   [2] Invertida v3.0 (padrão)   [3] Q1-Q5   [4] Híbrido Inv+Q   [5] Híbrido TODOS
```

**As 5 Estratégias:**
| # | Nome | Lógica |
|---|------|--------|
| 1 | Débito | Exclui números com maior excedente posicional |
| 2 | Invertida v3.0 (QUENTES) | Padrão — exclui os mais quentes (inversão de tendência) |
| 3 | Q1-Q5 Quadrantes | Exclui do pior quadrante (Q1) |
| 4 | Híbrido Invertida + Q1-Q5 | Média ponderada: 60% Invertida + 40% Quadrante |
| 5 | Híbrido TODOS | Débito (25%) + Invertida (50%) + Quadrante (25%) |

**Comportamento da Opção 0 (Comparar todas):**
- Gera as combinações usando a estratégia 2 (Invertida v3.0) normalmente
- Após o PASSO 4 (usuário informa o resultado real sorteado), exibe tabela comparativa
- A tabela mostra qual teria sido a exclusão de cada estratégia e se o número excluído saiu de fato
- Objetivo: avaliar retrospectivamente qual estratégia teria excluído melhor no concurso

**Variáveis de controle:**
- `comparar_estrategias_302` — flag booleana ativada pela opção 0
- `NOMES_ESTRATEGIA_302` — dicionário com nomes exibíveis das 5 estratégias
- `ranking_ativo_302` — ranking da estratégia escolhida para geração
- `rankings_estrategias_302` — dict com rankings de todas as estratégias (para comparativo)

---

### 20/03/2026 - CORREÇÃO: Filtro Probabilístico na Opção 30.2 ⭐⭐ IMPORTANTE!
**Problema:**
- Filtro probabilístico NUNCA funcionava na Opção 30→2 (Backtesting Pool 23)
- Código chamava métodos inexistentes: `carregar_dados()` e `verificar_combinacao()`
- Exceção era capturada silenciosamente → filtro sempre desativado
- Usuário selecionava modo 1-4 mas filtro nunca era aplicado

**Causa Raiz:**
- A classe `FiltroProbabilistico` tem API: `.carregar()`, `.filtrar_lista()`, `.passa()`
- Opção 30→2 usava nomes errados (provavelmente copy-paste incompleto)
- Adicionalmente faltava `sys.path.insert()` para resolução do módulo

**Correção:**
- `carregar_dados()` → `carregar(min_acertos_11=filtro_prob_limite, max_concursos_sem_11=None)`
- `verificar_combinacao()` → `filtrar_lista(todas_combos, verbose=True)`
- Adicionado `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` antes do import

**Status das 3 funções:**
| Função | Status |
|--------|--------|
| Opção 30→4 (Backtesting Histórico) | ✅ Já estava correto |
| Opção 30→2 (Backtesting Pool 23) | ✅ Corrigido |
| Opção 31 (Gerador) | ✅ Usa mesma função da 30→4 |

### 01/03/2026 - LUCRO SEM JACKPOT! ⭐⭐⭐ MARCO IMPORTANTE!
**Resultado do Backtest:**
- Resultado real: [1, 2, 4, 5, 6, 9, 11, 12, 13, 16, 18, 22, 23, 24, 25]
- Soma: 191, Pares: 8, Primos: 5, Seq.Máx: 4, Núcleo: 11

**Performance por Nível:**
| Nível | Combos | Custo | 11ac | Prêmio | ROI |
|-------|--------|-------|------|--------|-----|
| 0 | 12 | R$42 | 5 | R$35 | -16.7% |
| 1 | 12 | R$42 | 5 | R$35 | -16.7% |
| 2 | 9 | R$32 | 4 | R$28 | -11.1% |
| **3** | **7** | **R$24** | **4** | **R$28** | **+14.3%** ⭐ |
| 4 | 0 | R$0 | 0 | R$0 | 0% |
| **5** | **3** | **R$10** | **2** | **R$14** | **+33.3%** ⭐ |
| 6 | 0 | R$0 | 0 | R$0 | 0% |

**Análise:**
- ❌ Exclusão falhou: excluiu 9 números, 4 estavam no resultado {5, 12, 13, 18}
- ✅ Previsão de soma ACERTOU (previu BAIXA, resultado 191 = BAIXA)
- ✅ Níveis 3 e 5 foram LUCRATIVOS mesmo sem jackpot!
- 💡 Demonstra que filtros agressivos podem gerar lucro com 11 acertos

**Nova Funcionalidade Implementada:**
- TOP 10 candidatos à exclusão (ordenado por score)
- Quantidade de exclusão ajustável: 1 a 10 números (era fixo em 2)
- Permite ajuste manual a partir do TOP 10

### 12/03/2026 - Níveis 7 e 8: Filtro Posições Frias (Opção 31 + 30.2) ⭐⭐⭐ NOVO!
**Conceito:**
- Identifica pares (número, posição) com **0% de frequência** nos últimos 6 concursos
- Exemplo: Se número 14 NUNCA apareceu na posição N3 nos últimos 6 sorteios → par (14, N3) é "frio"
- O número NÃO é removido inteiramente — apenas proibido naquela posição específica
- Combinações com muitas violações (número em posição fria) são rejeitadas

**Diagnóstico Histórico:**
- Média de 4.0 violações por sorteio real (min 1, max 8)
- Tolerância 0 = impossível (elimina todos os jackpots)
- Tolerância 4-5 = filtragem eficaz sem perder jackpots

**Níveis Implementados:**
| Nível | Base | Filtro Posições Frias | Tolerância | Janela |
|-------|------|-----------------------|------------|--------|
| **7** | Nível 0 (sem filtros) | ✅ Somente freq=0% | **4** | 6 concursos |
| **8** | Cascata 6→1 (melhor nível com ≥1 combo) | ✅ Somente freq=0% | **3** | 6 concursos |

**Nível 8 - Lógica Cascata:**
1. Calcula posições frias (janela=6, apenas 0%)
2. Tenta Nível 6 + posições frias (tol=3) → se ≥1 combo, usa esse
3. Se 0 combos, tenta Nível 5 + posições frias → e assim por diante até Nível 1
4. Se nenhum nível funciona, usa Nível 0 + posições frias (tol=3)

**Resultados do Backtesting (131 concursos, 3508-3638):**
- N7: Muitas combinações (~340k), 2 jackpots em 31 testes iniciais
- N8: Melhor ROI (-53.0%), ~68.9k combos, 1 jackpot em 31 testes iniciais
- Taxa de exclusão geral: 22.1%

**Sincronização:**
- ✅ Implementado na Opção 31 (Gerador Pool 23)
- ✅ Implementado na Opção 30.2 (Backtesting Pool 23)

**Funções Utilizadas:**
- `_calcular_debitos_posicionais(resultados, janela=6, limiar=0.3)`: Calcula débitos posicionais
- `_aplicar_filtros_com_posicoes_frias(combos, filtros, ..., posicoes_frias_tolerancia=3)`: Aplica filtros + posições frias

### 01/03/2026 - CORREÇÃO CRÍTICA: Filtro Improbabilidade Posicional ⭐⭐ IMPORTANTE!
**Problema Identificado:**
- Filtro de Improbabilidade Posicional estava eliminando jackpots nos níveis 4, 5 e 6
- Análise de 18 backtests: **4 falhas** no N4_IMPROBABILIDADE
- Nível 4 tinha **0 jackpots** preservados!
- Sorteios reais tinham ~6 violações, mas filtro rejeitava >2

**Solução Aplicada:**
- ✅ DESATIVADO o filtro `usar_improbabilidade_posicional` nos níveis 4, 5 e 6
- Mantido ativo nos níveis 1, 2 e 3 (com tolerância=2)

**Arquivos Alterados:**
- `lotofacil_lite/interfaces/super_menu.py` (Opção 31 - Gerador)
- `lotofacil_lite/interfaces/super_menu.py` (Opção 30.2 - Backtesting)

**Impacto:**
- Níveis 4-6 agora preservarão mais jackpots
- Outros filtros posicionais (Qtde 6-25, Piores Histórico, Piores Recente) continuam ativos

### 26/02/2026 - Filtros Posicionais Dinâmicos (Opção 31 + 30.2) ⭐⭐ NOVO!
**Conceito:**
- Números que RARAMENTE aparecem em determinada posição (N1-N15) são "ruins"
- Baseado em análise SQL que se mostrou muito eficiente
- 3 filtros complementares implementados

**Filtros Implementados:**
1. **Qtde 6-25**: Conta quantos números do intervalo 6-25 estão na combinação
   - Combinações boas têm 10-13 números de 6-25 (ou seja, 2-5 de 1-5)
   - Valores aceitos: [10, 11, 12, 13]

2. **Piores Histórico**: Números raramente vistos em posições específicas (todo histórico)
   - Calculado dinamicamente a cada execução
   - Tolerância configurável por nível (0 = sem violações)

3. **Piores Recente**: Mesmo conceito, mas últimos 30 concursos
   - Captura tendências recentes
   - Tolerância: 0-1 dependendo do nível

**Configuração por Nível:**
| Nível | Qtde 6-25 | Piores Histórico | Piores Recente |
|-------|-----------|------------------|----------------|
| 1     | ✅ (10-13) | -               | -              |
| 2     | ✅ (10-13) | ✅ tol=0        | -              |
| 3     | ✅ (10-13) | ✅ tol=0        | ✅ tol=1       |
| 4     | ✅ (10-13) | ✅ tol=0        | ✅ tol=0       |
| 5     | ✅ (10-13) | ✅ tol=0        | ✅ tol=0       |
| 6     | ✅ (10-13) | ✅ tol=0        | ✅ tol=0       |

**Sincronização:**
- ✅ Implementado na Opção 31 (Gerador Pool 23)
- ✅ Implementado na Opção 30.2 (Backtesting Pool 23)

**Funções Criadas:**
- `_calcular_piores_numeros_por_posicao(resultados, janela=None)`: Calcula piores dinamicamente
- `_contar_qtde_intervalo_6_25(combo)`: Conta números 6-25 na combinação

### 24/01/2026 - Filtro Noneto + Análise Econômica
- Implementada opção 7 no submenu da opção 22: Filtro por Noneto
- Noneto padrão: [1, 2, 4, 8, 10, 13, 20, 24, 25]
- Cobertura: 79% histórico (5-7 acertos), 80% últimos 30
- Análise econômica completa: break-even impossível sem jackpot
- Nossos filtros melhoram chances em ~650x vs aleatório
- Recomendação: 200-500 combinações/concurso = melhor custo-benefício

### 13/02/2026 - Filtro Probabilístico na Opção 31 ⭐ NOVO!
**Conceito:**
- Combinações com mais "hits" históricos de 11+ acertos têm MAIOR probabilidade
- Análise de 3.268.760 combinações na tabela COMBINACOES_LOTOFACIL
- Descoberta: correlação <0.15 para padrões ocultos, mas frequência de acertos funciona!

**Implementação:**
- Arquivo: `lotofacil_lite/interfaces/filtro_probabilistico.py`
- Integrado como sub-filtro OPCIONAL na Opção 31 (Pool 23 Híbrido)
- 4 modos de operação:
  - [0] Desativado (padrão)
  - [1] Conservador: Acertos_11 >= 313 (58% das combos, +11% chance)
  - [2] Moderado: Acertos_11 >= 320 (45% das combos, +15% chance)
  - [3] Agressivo: Acertos_11 >= 330 (35% das combos, +18% chance)
  - [4] Personalizado: Limite manual (300-350)

**Filtro de "Recentes" (opcional):**
- Combinações "encalhadas" (sem 11+ há muito tempo) performam 0.72x PIOR
- Opção para limitar a max N concursos sem 11+ (ex: 20)
- Recomendado: 20 concursos para balance entre chance e volume

**Performance:**
- Carregamento: ~7 segundos para 1.9M combinações
- Lookup: <1ms para 100k combinações (dicionário em memória)
- Memória: ~91MB

**Validação (Concurso 3614):**
- Combinação vencedora: ID 2522851
- Acertos_11: 317 (acima da mediana 313)
- Ultimo_Acertos_11: 3611 (2 concursos antes)
- ✅ PASSA no filtro Conservador (Acertos_11 >= 313)
- ❌ NÃO PASSA no filtro Agressivo (Acertos_11 < 330)

**Uso na Opção 31:**
1. Selecionar números a excluir (método híbrido)
2. Escolher nível de filtro (0-6)
3. **NOVO:** Escolher modo do filtro probabilístico (0-4)
4. Opcionalmente ativar filtro de recentes
5. Gerar combinações filtradas

### 27/01/2026 - Conferidor Simples + Association Rules v2.0 ⭐ NOVO!
**Opção 23 - Conferidor Simples:**
- Confere combinações de arquivo TXT contra resultados reais
- 3 modos: TODOS os concursos, RANGE, ou entrada MANUAL
- **Análise financeira completa:**
  - Custo por aposta: R$3,50
  - Prêmios: 11=R$7 | 12=R$14 | 13=R$35 | 14=R$1.000 | 15=R$1.800.000
  - Calcula: Custo Total, Prêmio Total, Lucro/Prejuízo, ROI%
- Exporta resultados detalhados para TXT

**Association Rules v2.0 (Opção 7.12 → Opção 10):**
- Regras Negativas: X → ¬Y (números que NÃO aparecem juntos)
- Regras Multi-Antecedente: {X, Y} → Z
- Novas métricas: Conviction e Zhang's Interest
- Sliding Window: análise temporal (últimos N concursos)
- Explorer dedicado com 9 sub-opções:
  1. Regras Positivas TOP 30
  2. Regras Negativas TOP 30
  3. Regras Multi-Antecedente TOP 30
  4. Números a Evitar (baseado em regras negativas)
  5. Gerar 1 Combinação (baseada em regras)
  6. Gerar 10 Combinações
  7. Ranking Completo (todas as regras)
  8. Estatísticas Gerais
  9. Voltar
- Correção de bug: cálculo de confiança de regras negativas

### 22/01/2026 - Implementação C1/C2 Complementar
- Criado `gerador_c2_real.py` para gerar combinações C2
- Implementada opção 6 no submenu da opção 22
- Arquivos: `combo20_FILTRADAS_TOP1000.txt`, `combo20_C2_tendencia.txt`
- Análise mostrou: C1 favorável 40%, C2 favorável 35%, Neutros 25%

### 21/01/2026 - Descoberta dos Padrões de Retorno
- Analisados 490.314 combinações da estratégia Combo 20
- Identificados padrões de retorno recorrentes (131%, 26.5%, 8.05%)
- Criado `filtro_rapido.py` para seleção top 1000
- Encontrado jackpot (15 acertos) no concurso 3521

### 26/02/2026 - VALIDAÇÃO CIENTÍFICA COMPLETA ⭐⭐⭐

#### 🔬 Métricas Testadas e Resultados

| Métrica | Concursos | Resultado | Conclusão |
|---------|-----------|-----------|-----------|
| Ranking Quintetos (débito) | 200 | 0% vantagem | ❌ NÃO FUNCIONA |
| Índice de Débito extremo | 2000+ casos | 0% vantagem | ❌ NÃO FUNCIONA |
| Anomaly v2.0 (consecutivas) | 3619 | +2-3% | ⚠️ INCONCLUSIVO |
| Números Primos | 3619 | -0.3% | ❌ NÃO FUNCIONA |
| Fibonacci | 3619 | -0.2% | ❌ NÃO FUNCIONA |
| Múltiplos de 3 | 3619 | -0.4% | ❌ NÃO FUNCIONA |
| Euler (e) | 3619 | -0.6% | ❌ NÃO FUNCIONA |
| Pi (π) | 3619 | -0.6% | ❌ NÃO FUNCIONA |

**Conclusão:** A loteria é VERDADEIRAMENTE ALEATÓRIA. Padrões matemáticos e históricos não predizem resultados futuros.

#### ✅ Novos Filtros VALIDADOS (Redutores)

| Filtro | Cobertura | Uso |
|--------|-----------|-----|
| **Consecutivos 7-10** | 90.5% | Elimina combinações muito espalhadas/agrupadas |
| **Gap máximo ≤5** | 93.5% | Elimina combinações com lacunas grandes |
| **Primos 4-7** | 91.4% | Elimina extremos |
| **Fibonacci 3-5** | 81.7% | Elimina extremos |

#### 🔧 Implementação no Pool 23

Novos filtros adicionados aos níveis 2-6:
```
Nível 2: Consecutivos 7-10, Gap ≤5 (seguro para jackpot)
Nível 3: Consecutivos 7-10, Gap ≤5
Nível 4-6: Consecutivos 7-9, Gap ≤4 (mais restritivo)
```

#### 📊 Probabilidade Fundamental

**TODOS os 25 números têm EXATAMENTE 60% de chance de sair:**
- Prova matemática: C(24,14) / C(25,15) = 0.60
- Verificação empírica (3619 concursos): 57.3% - 62.6% (variação natural)
- "Ou sai ou não sai" NÃO é 50/50 - é 60/40!

#### 🎯 Abordagem Recomendada

```
1. NÃO tentar prever qual número vai sair (impossível)
2. FOCAR em reduzir universo eliminando combinações improváveis
3. USAR: Pool 23 + filtros validados (soma, consecutivos, gap)
4. ACEITAR: ROI negativo sem jackpot, positivo com jackpot
```

#### 📁 Arquivos de Validação Criados
- `validar_ranking_quintetos.py` - Valida ranking por débito
- `validar_anomaly_v2.py` - Valida consecutivas
- `validar_padroes_matematicos.py` - Valida primos, fibonacci, múltiplos
- `validar_padroes_avancados.py` - Valida Euler, Pi, consecutivos, gaps
- `demonstrar_probabilidade_60.py` - Prova dos 60%

---

## 🆘 TROUBLESHOOTING

### Erro: "Arquivo não encontrado"
```python
# Verificar se está no diretório correto
import os
print(os.getcwd())

# Usar caminho absoluto
caminho = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\arquivo.txt"
```

### Erro: "Conexão com banco falhou"
```python
# Verificar se SQL Server está rodando
# Services.msc → SQL Server (MSSQLSERVER) → Start
```

### Erro: "Módulo não encontrado"
```python
# Adicionar path
import sys
sys.path.insert(0, r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite")
sys.path.insert(0, r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\analisadores")
```

---

## ✅ CHECKLIST PARA NOVAS SESSÕES

Ao iniciar uma nova sessão com qualquer modelo de IA:

- [ ] Ler este arquivo `CONTEXTO_MASTER_IA.md`
- [ ] Verificar último concurso no banco de dados
- [ ] Confirmar objetivo do usuário (análise? geração? debug?)
- [ ] Identificar arquivos relevantes já existentes
- [ ] Perguntar se há atualizações desde última sessão

---

## 📞 CONTATO E SUPORTE

**Desenvolvedor**: AR CALHAU
**Projeto**: LotoScope
**Linguagem Principal**: Python 3.11+
**Base de Dados**: SQL Server (localhost)

---

> 💡 **DICA FINAL**: Em caso de dúvida, execute `python super_menu.py` e explore as opções.
> O sistema é autoexplicativo e possui validações internas.
