# Copilot Instructions — LotoScope

## 🎯 Quick Reference

**Project:** [PROJECT_DESC]  
**Architecture:** Layered (ex: Layered, Clean, Hexagonal, MVC, Microservices)  
**Language:** [LANGUAGE] [VERSION]  
**Framework:** [FRAMEWORK] [VERSION]  
**Build:** `[BUILD_CMD]`  
**Test:** `[TEST_CMD]`  
**Run:** `[RUN_CMD]`

---

## 📌 Core Rules (ALWAYS follow)

<!-- Liste aqui as 3-7 regras mais críticas do seu projeto. 
     Estas regras NUNCA devem ser violadas pelo Copilot. -->

1. ✅ [REGRA 1 — ex: Nunca retornar entity JPA direto na API, sempre usar DTO]
2. ✅ [REGRA 2 — ex: Toda validação de input em @Valid no DTO, nunca no service]
3. ✅ [REGRA 3 — ex: Não usar System.out.println, usar logger SLF4J]
4. ✅ [REGRA 4 — ex: Nomes de classes em inglês, comentários em português]
5. ✅ [REGRA 5 — ex: Todo endpoint deve ter autenticação, exceto /health]

---

## 📚 Documentation Map

| Category | Location | Purpose |
|----------|----------|---------|
| **Project Context** | [.github/copilot/](copilot/) | O que o projeto faz, stack, padrões |
| **Domain Rules** | [.github/copilot/domains-rules.md](copilot/domains-rules.md) | Regras de negócio invioláveis |
| **Architecture** | [.github/context/](context/) | AS-IS, TO-BE, análise estratégica |
| **Agents** | [.github/agents/](agents/) | Agentes IA especializados |
| **Patterns** | [patterns/](../../patterns/) | Templates de design patterns |
| **Skills** | [skills/](../../skills/) | How-to guides técnicos |
| **Prompts** | [prompts/](../../prompts/) | Prompts prontos para IA |
| **Docs** | [docs/](../../docs/) | Arquitetura, legacy analysis, ADRs |
| **Type Matrix** | [.github/context/type_matrix.md](context/type_matrix.md) | Inventário de componentes |

---

## 🤖 AI Agents

| Agent | Responsabilidade | Usar quando |
|-------|-----------------|-------------|
| 🏛️ **ARCHITECT** | Design, Padrões, Performance | Revisar arquitetura de novo código |
| 💻 **BACKEND** | Geração de código | Gerar novo componente |
| 🧪 **QA** | Testes, Cobertura, Qualidade | Criar testes |
| 🔧 **REFACTOR** | Code smells, Limpeza | Melhorar código existente |
| 🎯 **COORDINATOR** | Planejamento, Sequenciamento | Planejar sprint/tarefas |
| 📊 **OBSERVABILITY** | Logs, Métricas, Tracing | Instrumentar código, debugar produção |

---

## 🏗️ Project Structure

<!-- Descreva a estrutura de pastas do seu projeto -->

```
LotoScope/
├── [SOURCE_DIR]/              # Código fonte
│   ├── [LAYER_1]/             # ex: controllers/, pages/, routes/
│   ├── [LAYER_2]/             # ex: services/, hooks/, use-cases/
│   ├── [LAYER_3]/             # ex: repositories/, models/, entities/
│   └── [LAYER_4]/             # ex: config/, utils/, helpers/
├── tests/                # Testes
├── project.yml              # ex: pom.xml, package.json, pyproject.toml
└── README.md
```

---

## ⚙️ How to Use Agents

### Generate Code:
```
1. Ask BACKEND: "Generate [component type] for [requirement]"
2. Copilot reads patterns/ + coding-standards.md
3. Get: Complete, compilable code following project standards
```

### Code Review:
```
1. Ask ARCHITECT: "Review the design of [component]"
2. Copilot reads domains-rules.md + coding-standards.md
3. Get: Review report (approved/conditional/rejected)
```

### Create Tests:
```
1. Ask QA: "Create tests for [component]"
2. Copilot reads skills/ + testing patterns
3. Get: Complete test class with coverage
```

### Improve Code:
```
1. Ask REFACTOR: "Identify code smells in [file/component]"
2. Get: Report with prioritized improvements
```
