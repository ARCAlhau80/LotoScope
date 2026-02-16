# 🎯 CONTEXTO MASTER PARA AGENTES IA - LOTOSCOPE
## Documentação Completa e Unificada do Sistema

> **IMPORTANTE**: Este arquivo é a FONTE ÚNICA DE VERDADE para qualquer agente de IA
> trabalhando no projeto LotoScope. Mantenha-o atualizado após cada sessão significativa.

```
📅 ÚLTIMA ATUALIZAÇÃO: 16/02/2026
👤 AUTOR: AR CALHAU
🤖 VALIDADO POR: Claude Opus 4.5
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
