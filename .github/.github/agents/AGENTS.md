# 🤖 AI Agents Guide — LotoScope

---

## 📋 Agent Index

| Agent | Expertise | Quando Usar |
|-------|-----------|-------------|
| 🏛️ [ARCHITECT](ARCHITECT.md) | Design, Padrões, Performance | Revisar arquitetura, decisões |
| 💻 [BACKEND](BACKEND.md) | Geração de código | Criar novos componentes |
| 🧪 [QA](QA.md) | Testes, Cobertura | Gerar testes, validar qualidade |
| 🔧 [REFACTOR](REFACTOR.md) | Code smells, Limpeza | Melhorar código existente |
| 🎯 [COORDINATOR](COORDINATOR.md) | Planejamento, Sequenciamento | Planejar tarefas, sprints |
| 📊 [OBSERVABILITY](OBSERVABILITY.md) | Logs, Métricas, Tracing | Instrumentar código, debugar produção |

---

## 🎯 Quick Reference

| Preciso de... | → Use |
|---------------|-------|
| "Como devo projetar isso?" | ARCHITECT |
| "Gere código para este requisito" | BACKEND |
| "Crie testes para meu código" | QA |
| "Este código está confuso, como melhorar?" | REFACTOR |
| "O que devemos fazer a seguir?" | COORDINATOR |
| "Adicione logs/métricas ao meu código" | OBSERVABILITY |
| "Investigue este erro em produção" | OBSERVABILITY |

---

## 🔄 Workflow: Nova Feature

```
1. COORDINATOR → Divide em tarefas
2. ARCHITECT → Valida design (se complexo)
3. BACKEND → Gera código
4. QA → Gera testes
5. COORDINATOR → Verifica completude
```

## 🔄 Workflow: Melhoria de Qualidade

```
1. REFACTOR → Identifica code smells
2. ARCHITECT → Valida mudanças (se estrutural)
3. REFACTOR → Aplica refactoring
4. QA → Garante que testes passam
```

## 🔄 Workflow: Planejamento

```
1. COORDINATOR → Analisa backlog + AS-IS + TO-BE
2. COORDINATOR → Prioriza tarefas
3. Distribui para agentes (BACKEND, QA, REFACTOR)
4. COORDINATOR → Acompanha progresso
```
