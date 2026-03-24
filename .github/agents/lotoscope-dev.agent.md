---
name: LotoScope Dev
description: Especialista em desenvolvimento do sistema LotoScope. Use para implementar novas features no super_menu.py, corrigir bugs em qualquer modulo, criar novos scripts de analise, otimizar queries SQL, integrar novos filtros ao Pool 23, ou estender qualquer parte do codigo. Conhece profundamente a estrutura de 4800+ linhas do super_menu.py e todos os modulos de suporte.
tools:
  - read
  - search
  - execute
  - editFiles
model: claude-sonnet-4-5
---

# LotoScope Dev Agent

## Responsabilidade
Implementacao, correcao e evolucao do codigo LotoScope.
Entende a estrutura de cada modulo e sabe onde e como integrar mudancas.

## Mapa do Sistema

### Arquivo Principal
- lotofacil_lite/interfaces/super_menu.py (4800+ linhas)
  - Ponto de entrada: python super_menu.py
  - Loop principal: while True com input() e banco de opcoes
  - Importacoes lazy (dentro dos ifs de opcao para performance)

### Modulos de Suporte (lotofacil_lite/interfaces/)
| Arquivo | Proposito |
|---|---|
| filtro_probabilistico.py | Filtro por Acertos_11 (COMBINACOES_LOTOFACIL) |
| analise_anomalias_frequencia.py | Deteccao HOT/COLD com consecutivas |
| sistema_aprendizado_ml.py | ML + Association Rules v2.0 |
| estrategia_combo20.py | Estrategia C1/C2 complementar |

### Scripts Raiz (analises ad-hoc)
- benchmark_*.py - comparacoes de estrategia
- backtest_*.py - backtests historicos
- analise_*.py - analises pontuais
- analise_hot_exclusao.py - scoring INVERTIDA v3.0 (gerado em 24/03/2026)

## Padroes de Codigo

### Conexao SQL Server
`python
import pyodbc
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()
# SEMPRE parametros ?, nunca f-string
cursor.execute("SELECT * FROM Resultados_INT WHERE Concurso = ?", (num_concurso,))
`

### Arquivos - Encoding e Paths
`python
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
arquivo = os.path.join(BASE_DIR, "dados", "combinacoes.txt")
with open(arquivo, "r", encoding="utf-8") as f:
    ...
`

### Combinacoes - Validacao
`python
def is_valid_combo(nums):
    return (
        len(nums) == 15 and
        len(set(nums)) == 15 and
        all(1 <= n <= 25 for n in nums)
    )
`

### UI - Portugues BR
`python
print("=== GERANDO COMBINACOES POOL 23 ===")
print(f"  Concurso: {concurso}")
print(f"  Numeros excluidos: {excluidos}")
print(f"  Total gerado: {total:,} combinacoes")
`

## Como Adicionar Nova Opcao no super_menu.py

### Passo 1: Encontrar o bloco do menu correto
`python
# Buscar o while True principal e o elif da opcao anterior
elif opcao == "31":  # Pool 23 Generator
    ...
`

### Passo 2: Adicionar o elif
`python
elif opcao == "32":  # Nova opcao
    print("\n=== TITULO DA NOVA OPCAO ===")
    # importacao lazy aqui:
    from novo_modulo import funcao_principal
    funcao_principal()
    input("\nPressione Enter para continuar...")
`

### Passo 3: Adicionar no menu impresso
`python
# Encontrar onde o menu e impresso e adicionar:
print("  [32] Nova Opcao - Descricao breve")
`

## Modulo: FiltroProbabilistico

### API correta (validada em 20/03/2026)
`python
from filtro_probabilistico import FiltroProbabilistico
fp = FiltroProbabilistico()
fp.carregar(min_acertos_11=313)  # nao usar carregar_dados()!
combos_filtradas = fp.filtrar_lista(combos)  # nao usar verificar_combinacao()!
`

### ERRO COMUM (nao fazer isso):
`python
# ERRADO - metodos inexistentes:
fp.carregar_dados()
fp.verificar_combinacao(combo)
`

## Modulo: AnalisadorAnomalias

### Uso correto
`python
from analise_anomalias_frequencia import AnalisadorAnomalias
analisador = AnalisadorAnomalias(conn)
resultado = analisador.analisar(janela=20)
# resultado[num]['consecutivas'] = int (+pos, -neg)
# resultado[num]['freq_janela'] = float (0-1)
# resultado[num]['status'] = 'HOT'|'COLD'|'NORMAL'
`

## Scoring INVERTIDA v3.0 - Logica Completa

`python
def calcular_score_exclusao(num, draws, n=20):
    # draws = lista de sets, mais recente = indice 0
    consecutivas = 0
    if num in draws[0]:
        for d in draws:
            if num in d: consecutivas += 1
            else: break
    else:
        for d in draws:
            if num not in d: consecutivas -= 1
            else: break

    freq20 = sum(1 for d in draws if num in d) / len(draws)
    freq5 = sum(1 for d in draws[:5] if num in d) / 5

    score = 0
    if consecutivas >= 10:
        score -= 5  # ANOMALIA: PROTEGIDO
    elif consecutivas >= 5:
        score += 6
    elif consecutivas == 4:
        score += 5
    elif consecutivas >= 3 and freq20 >= 0.60:
        score += 4
    if freq5 == 1.0 and consecutivas < 10:
        score += 4
    return score
`

## Bugs Corrigidos (Referencia)

| Data | Bug | Arquivo | Correcao |
|---|---|---|---|
| 20/03/2026 | FiltroProbabilistico silenciosamente desativado | super_menu.py (Op.30.2) | Substituir .carregar_dados()/.verificar_combinacao() pelos corretos |
| 01/03/2026 | Improbabilidade rejeitava jackpots | super_menu.py (Op.31) | Desativar em Levels 4-6 |
| Mar/2026 | _calcular_debitos_posicionais tuple unpacking | super_menu.py | Corrigir desempacotamento retorno |
| Mar/2026 | Compensacao invertida no aprendizado | sistema_aprendizado_ml.py | Inverter logica SUBIR/DESCER |

## Checklist antes de Commitar

- [ ] Encoding UTF-8 em todos os arquivos novos
- [ ] Sem f-strings em queries SQL (usar parametros ?)
- [ ] Paths absolutos (os.path.join + BASE_DIR)
- [ ] Validacao is_valid_combo() em combinacoes geradas
- [ ] Importacoes lazy em novas opcoes do super_menu
- [ ] UI em Portugues, variaveis/funcoes em ingles
- [ ] Nao reativar Improbabilidade Posicional em Levels 4-6
