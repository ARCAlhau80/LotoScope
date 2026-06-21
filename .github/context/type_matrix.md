# 🗂️ TYPE MATRIX: Inventário de Componentes — LotoScope

**Propósito:** Catálogo centralizado de TODOS os componentes, suas relações e status  
**Atualizado:** [DATA]

---

## 📋 Legend

- 🎯 = Componente principal
- 🔌 = Interface/Contract
- 📦 = Entity/Model (Domain)
- 🏗️ = Service/Use Case
- 🗄️ = Repository/DAO (Persistence)
- 🔄 = Strategy/Pattern
- ✅ = Bem implementado
- ⚠️ = Precisa refatorar
- ❌ = Problema crítico
- 🆕 = Novo (a ser criado)

---

## 1️⃣ Entities / Models

| # | Classe/Module | Tabela | Campos Principais | Status | Notas |
|---|---------------|--------|-------------------|--------|-------|
| 1 | [Entity1] | [table_name] | id, nome, status, createdAt | ✅ | |
| 2 | [Entity2] | [table_name] | id, entity1_id, value | ⚠️ | Falta audit fields |
| 3 | [Entity3] | [table_name] | id, type, amount | 🆕 | A ser criado |

---

## 2️⃣ Repositories / DAOs

| # | Classe/Module | Entity | Queries Customizadas | Status | Notas |
|---|---------------|--------|---------------------|--------|-------|
| 1 | [Entity1Repository] | Entity1 | findByStatus, findByPeriod | ✅ | |
| 2 | [Entity2Repository] | Entity2 | findByEntity1Id | ⚠️ | N+1 query |

---

## 3️⃣ Services / Use Cases

| # | Classe/Module | Responsabilidade | Dependências | Status | Notas |
|---|---------------|-----------------|--------------|--------|-------|
| 1 | [Entity1Service] | CRUD + regras de negócio | Entity1Repository | ✅ | |
| 2 | [ProcessingService] | Orquestração de processamento | Service1, Service2 | ⚠️ | God class |

---

## 4️⃣ Controllers / Endpoints

| # | Classe/Module | Base Path | Endpoints | Autenticação | Status |
|---|---------------|-----------|-----------|-------------|--------|
| 1 | [Entity1Controller] | /api/v1/entities | GET, POST, PUT, DELETE | JWT | ✅ |
| 2 | [ReportController] | /api/v1/reports | GET | JWT | 🆕 |

---

## 5️⃣ DTOs

| # | Classe/Module | Tipo | Entity Relacionada | Validações | Status |
|---|---------------|------|--------------------|-----------|--------|
| 1 | [Entity1Request] | Request | Entity1 | @NotBlank nome, @Email email | ✅ |
| 2 | [Entity1Response] | Response | Entity1 | — | ✅ |

---

## 6️⃣ Strategies / Patterns (se aplicável)

<!-- Remova esta seção se o projeto não usa Strategy Pattern -->

| # | Strategy | Tipo | Dependências | Status | Complexidade |
|---|----------|------|-------------|--------|-------------|
| 1 | [Strategy1] | [Type] | DAO1, Entity1 | ✅ | Simples |
| 2 | [Strategy2] | [Type] | DAO2, Entity2 | ⚠️ | Complexa |

---

## 📊 Resumo

| Categoria | Total | ✅ OK | ⚠️ Refactor | ❌ Crítico | 🆕 Novo |
|-----------|-------|-------|-------------|-----------|---------|
| Entities | [X] | [X] | [X] | [X] | [X] |
| Repositories | [X] | [X] | [X] | [X] | [X] |
| Services | [X] | [X] | [X] | [X] | [X] |
| Controllers | [X] | [X] | [X] | [X] | [X] |
| DTOs | [X] | [X] | [X] | [X] | [X] |
| **Total** | **[X]** | **[X]** | **[X]** | **[X]** | **[X]** |

---

## 🔗 Mapa de Dependências

```
Controller ──▶ Service ──▶ Repository ──▶ Entity
                 │
                 └──▶ Mapper ──▶ DTO
```

<!-- Adapte o diagrama para o seu projeto. Exemplos:
Controller → Service → Repository → Entity
Service → ExternalAPI
Service → MessageQueue
Scheduler → Service
-->

---

## 📎 Referências

- [Architecture Overview](../../docs/architecture/overview.md) — Visão geral da arquitetura
- [Legacy Analysis](../../docs/legacy-analysis/overview.md) — Análise de débito técnico
- [AS-IS.md](AS-IS.md) — Estado atual
- [TO-BE.md](TO-BE.md) — Roadmap
