---
description: "Analyze a specific Lotofácil draw — provide full statistical breakdown including hit rates, positional analysis, frequency, anomalies, and filter performance"
name: "Analyze Draw"
agent: "agent"
tools: [execute, read, search]
argument-hint: "Número do concurso (ex: 3615) ou 'último'"
---

Analise o concurso da Lotofácil indicado com um relatório estatístico completo.

## Dados do Concurso

Concurso alvo: {{CONCURSO}}

## O Que Analisar

1. **Resultado bruto**: Números sorteados por posição (N1-N15)
2. **Frequência recente**: Quantas vezes cada número saiu nos últimos 30 concursos
3. **Consecutivas**: Números com sequências consecutivas de aparição antes deste concurso
4. **Distribuição posicional**: Comparar com médias históricas por posição
5. **Soma e paridade**: Total da soma, quantidade de pares/ímpares
6. **Filtros Pool 23**: Este resultado passaria nos filtros de qual nível?
7. **Anomalias**: Algum número com comportamento anômalo (10+ consecutivas, 8+ ausências, etc.)?

## Formato de Saída

```
=== ANÁLISE CONCURSO XXXX ===
Resultado: [N1 N2 ... N15]
Soma: XXX | Pares: X | Ímpares: X

📊 FREQUÊNCIA (últimos 30 concursos):
[Tabela: Número | Freq | Status (HOT/COLD/NORMAL)]

🔄 CONSECUTIVAS PRÉ-SORTEIO:
[Lista de números com consecutivas + contagem]

📍 POSICIONAIS:
[Desvios significativos vs média histórica]

🎯 FILTROS POOL 23:
[Level 1..6: PASSARIA / FALHARIA no filtro X]

🚨 ANOMALIAS DETECTADAS:
[Números com comportamento fora do padrão]
```

## Conexão e Dados

```python
import pyodbc
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
```

Use os últimos 30-50 concursos como janela de frequência recente.
