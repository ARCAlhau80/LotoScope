---
description: "Update LotoScope documentation after system changes — sync CONTEXTO_MASTER_IA.md, QUICK_START_IA.md, and copilot-instructions.md with new features, bug fixes, validated results, or strategy changes. Run this protocol after completing any significant system change."
name: "Update Documentation"
agent: "agent"
tools: [read, edit, search]
argument-hint: "O que mudou no sistema (nova feature, bug fix, novo resultado validado, mudança de estratégia)"
---

Execute o protocolo de atualização de documentação do LotoScope após as seguintes mudanças: {{MUDANCAS}}

## Documentos a Verificar e Atualizar

### Prioridade Alta (sempre verificar)
1. `.github/copilot-instructions.md` — Contexto principal para IA
2. `.copilot-instructions.md` (raiz) — Resumo rápido para IA
3. `QUICK_START_IA.md` — Overview 1 minuto

### Prioridade Média (atualizar se mudança for significativa)
4. `CONTEXTO_MASTER_IA.md` — Documentação completa
5. `REFERENCIA_TECNICA_IA.md` — Código e APIs

## Workflow

1. **Ler** cada documento alvo (não editar de memória)
2. **Identificar** o local exato de inserção em cada doc
3. **Aplicar** mudanças cirúrgicas:
   - Novos resultados → seção "Resultados Validados"
   - Bug fixes → seção "Bug Fixes & Improvements", numerado e com data
   - Nova feature → seção de estratégias ativas, com número da opção
   - Estratégia descartada → marcar como `~~DESCARTADO em DD/MM/AAAA~~` com motivo
4. **Atualizar** data `*Última atualização: DD/MM/AAAA*` em todos os docs modificados
5. **Verificar** consistência — mesmos dados em todos os docs (ex: ROI +2841% deve aparecer igual em todos)

## Templates de Inserção

### Novo Resultado Validado
```markdown
✅ **15 acertos** — Concurso **XXXX** (Pool 23 Level X, ROI +XXX%)
```

### Bug Fix
```markdown
N. **Fixed** (DD/MM/AAAA): **[TÍTULO]** ⭐[CRÍTICO/NOVO]
   - Sintoma: [descrição do que estava errado]
   - Causa: [causa raiz]
   - Fix: [o que foi corrigido]
```

### Nova Feature
```markdown
### N. Nome da Feature (Opção XX) ⭐⭐ NOVO (DD/MM/AAAA)
- **Propósito**: [o que resolve]
- **Configuração**: [parâmetros principais]
- **Uso**: Opção XX → sub-opção YY do super_menu.py
```

## Regras Invioláveis

- NUNCA reescrever seções completas — mudanças cirúrgicas apenas
- NUNCA remover resultados validados históricos
- Manter português (BR) nos textos
- Data de atualização: formato DD/MM/AAAA
- Manter numeração sequencial dos bug fixes
