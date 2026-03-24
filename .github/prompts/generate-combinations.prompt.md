---
description: "Generate Lotofácil combinations using Pool 23 Hybrid strategy — specify filter level (0-8), optionally override the two numbers to exclude, and save the output TXT file. Use for creating betting files for the next draw."
name: "Generate Pool 23 Combinations"
agent: "agent"
tools: [execute, read, search]
argument-hint: "Nível de filtro (0-8), concurso de referência para exclusão, e nome do arquivo de saída"
---

Gere combinações Lotofácil usando o Pool 23 Híbrido para o próximo concurso.

## Parâmetros

- **Nível de filtro**: {{NIVEL}} (0-8, padrão: 3)
- **Referência**: {{REFERENCIA}} (ex: "último concurso" ou número específico)
- **Excluir manualmente**: {{EXCLUIR}} (opcional — se vazio, usar exclusão automática INVERTIDA v3.0)
- **Arquivo de saída**: {{ARQUIVO}} (ex: "pool23_nivel3_proximo.txt")

## Workflow

1. **Identificar** o último concurso disponível no banco
2. **Calcular** ranking INVERTIDA v3.0 dos números mais HOT:
   - Verificar consecutivas de cada número
   - Proteger números com 10+ consecutivas (persistência = anomalia)
   - Selecionar TOP 2 com maior score para exclusão
3. **Confirmar** exclusão com o usuário (mostrar TOP 10 candidatos)
4. **Gerar** C(23,15) combinações = 490.314 combos base
5. **Aplicar** filtros do nível escolhido:
   - Level 3 (recomendado): ~100k combos, ROI +492% jackpot, +14.3% sem jackpot
   - Level 6 (ultra): ~18k combos, ROI +2841% jackpot
6. **Salvar** arquivo TXT de saída (UTF-8, um combo por linha)
7. **Resumo**: Quantidade gerada, custo total (R$ 3,50/combo), break-even

## Exclusão Automática — Scoring INVERTIDA v3.0

```
Candidatos a excluir (ordem decrescente de score):
Score += 6 → 5-9 consecutivas de aparição
Score += 5 → 4 consecutivas
Score += 4 → 3+ consecutivas + freq > 70% últimos 5
Score += 4 → 100% freq nos últimos 5 concursos
Score -= 5 → 10+ consecutivas (ANOMALIA — PROTEGIDO, não excluir)
```

## Referência de Combos por Nível

| Level | Combos Aprox. | Custo (R$) | Recomendação |
|---|---|---|---|
| 0 | 490.314 | 1.716.099 | Apenas referência |
| 3 | ~100k | ~350.000 | **Padrão recomendado** |
| 5 | ~42k | ~147.000 | Agressivo |
| 6 | ~18k | ~63.000 | Ultra (maior ROI %) |
| 7 | ~50k | ~175.000 | Cold Positions |

## Saída Esperada

```
✅ Exclusão: Números [X] e [Y] (scores: XX e XX)
📦 Pool gerado: 23 números [lista]
🔢 Combinações geradas: XXX.XXX
💾 Salvo em: [caminho do arquivo]
💰 Custo total: R$ XXX.XXX,00
```
