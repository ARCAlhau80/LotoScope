# 🎓 PROJECT CONTEXT — LotoScope

**Propósito:** Entendimento rápido do projeto para desenvolvedores e IA  
**Nível:** Fundamental — leia ANTES de qualquer code change  
**Atualizado:** 24/03/2026

---

## 🎯 O Que Este Projeto Faz

**LotoScope** é um sistema científico Python para análise estatística e geração inteligente de combinações da **Lotofácil** — a loteria brasileira onde o jogador escolhe 15 números de 1 a 25.

O sistema transforma os 3.268.760 possíveis bilhetes em um conjunto otimizado de ~18.000-100.000 combinações com probabilidade aumentada de acerto, usando filtros estatísticos, análise de consecutivas, e exclusão de números HOT (mean reversion).

**Casos de uso principais:**

### 1️⃣ Pool 23 — Geração de Combinações (Opção 31)
```
Objetivo:     Gerar 18k-490k combinações de 15 números com maior probabilidade
Entrada:      Histórico de concursos (SQL Server), nível de filtro 0-8
Saída:        Arquivo TXT com combinações, uma por linha
Frequência:   Antes de cada sorteio (2-3x por semana)
Exemplo:      "Gerar Level 6 para o próximo concurso → 18k combos, ROI esperado +2841%"
```

### 2️⃣ Backtesting (Opção 30.2)
```
Objetivo:     Validar estratégia contra concursos históricos reais
Entrada:      Período de análise, nível de filtro, estratégia de exclusão
Saída:        Tabela com hits por concurso, ROI total, jackpot rate
Frequência:   Após qualquer mudança de estratégia ou filtros
Exemplo:      "Backtest últimos 20 concursos → Level 3 teve +14.3% ROI sem jackpot"
```

### 3️⃣ Análise Estatística (Opção 7.x, 22, 23)
```
Objetivo:     Entender padrões históricos para tomar decisões estratégicas
Entrada:      Período (ex: últimos 30 concursos), número ou posição específica
Saída:        Heatmaps, frequências, rankings, association rules
Frequência:   Quando investigando um padrão ou otimizando estratégia
```

---

## 📍 Fluxo Mental

```
┌────────────────────────────────────┐
│  1. ANÁLISE do último sorteio       │
│     "Quais números estão HOT?"      │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│  2. EXCLUSÃO dos 2 HOT (INVERTIDA)  │
│     Score: consecutivas + frequência│
│     Pool resultante: 23 números     │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│  3. GERAÇÃO Pool 23 (L0: 490k)      │
│     Aplicar filtros nível escolhido │
│     L3: ~100k | L6: ~18k combos     │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│  4. VALIDAÇÃO + SAÍDA               │
│     Salvar TXT, calcular custo      │
│     Usar Opção 23 para checar ROI   │
└────────────────────────────────────┘
```

---

## 🗂️ Conceitos-Chave (Glossário do Domínio)

| Termo | Definição |
|---|---|
| **Concurso** | Número sequencial do sorteio (1 a ~3640) |
| **Pool 23** | Conjunto de 23 números base (25 - 2 excluídos) |
| **Exclusão INVERTIDA v3.0** | Excluir números HOT (mean reversion) — exclui os que mais apareceram |
| **Level 0-8** | Nível de filtro do Pool 23 (0=sem filtro, 6=ultra restrito) |
| **anomalia de persistência** | Número com 10+ consecutivas — protegido da exclusão |
| **Acertos_11** | Quantas vezes uma combinação teve 11+ acertos na história (usado no filtro probabilístico) |
| **ROI** | Retorno sobre investimento: (prêmios - custos) / custos × 100% |
| **Baseline** | Prob. aleatória: 60% cada número, ~15% jackpot sem estratégia |
| **HOT** | Número com alta frequência recente + consecutivas (candidato a exclusão) |
| **COLD** | Número com baixa frequência recente (pode retornar — favorável) |
| **Consecutivas** | Quantos sorteios seguidos um número apareceu |

---

## 🏆 Resultados Validados (Mar/2026)

| Concurso | Resultado | Estratégia | ROI |
|---|---|---|---|
| 3474 | 15/15 ✅ | C1/C2 Complementar | — |
| 3610 | 15/15 ✅ | Pool 23 Híbrido | — |
| 3615 | 15/15 ✅ | Pool 23 Level 6 | **+2841%** |
| 01/03/2026 | Lucro sem jackpot | Level 3 | +14.3% |
| 01/03/2026 | Lucro sem jackpot | Level 5 | +33.3% |

| Termo | Definição | Exemplo |
|-------|-----------|---------|
| [TERMO_1] | [O que significa no contexto deste projeto] | [Exemplo] |
| [TERMO_2] | [O que significa] | [Exemplo] |
| [TERMO_3] | [O que significa] | [Exemplo] |

---

## 🏗️ Estrutura do Projeto

```
LotoScope/
├── [SOURCE_DIR]/
│   ├── [CAMADA_1]/          # [Propósito — ex: Controllers, entrada de dados]
│   ├── [CAMADA_2]/          # [Propósito — ex: Services, lógica de negócio]
│   ├── [CAMADA_3]/          # [Propósito — ex: Repositories, acesso a dados]
│   ├── [CAMADA_4]/          # [Propósito — ex: Entities/Models, domínio]
│   └── [CAMADA_5]/          # [Propósito — ex: Config, utilitários]
├── tests/
│   ├── unit/
│   └── integration/
├── project.yml
└── README.md
```

---

## 🔄 Fluxo de Dados

<!-- Descreva como dados fluem pelo sistema -->

```
[ENTRADA] → [VALIDAÇÃO] → [PROCESSAMENTO] → [PERSISTÊNCIA] → [RESPOSTA]

Exemplo:
  HTTP Request → DTO Validation → Service Logic → Repository Save → HTTP Response
```

---

## 🏢 Integrações Externas

<!-- Liste sistemas externos que este projeto se comunica -->

| Sistema | Protocolo | Propósito | Criticidade |
|---------|-----------|-----------|-------------|
| [SISTEMA_1] | [REST/gRPC/SOAP/Queue] | [Para que se integra] | [Alta/Média/Baixa] |
| [SISTEMA_2] | [Protocolo] | [Propósito] | [Criticidade] |

---

## 👥 Stakeholders

| Quem | Papel | Interesse |
|------|-------|-----------|
| [STAKEHOLDER_1] | [Papel] | [O que espera do sistema] |
| [STAKEHOLDER_2] | [Papel] | [O que espera] |
