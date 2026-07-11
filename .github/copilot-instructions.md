# graph-* Skills — GitHub Copilot Instructions

These skills drive software delivery through the agf CLI lifecycle.
Invoke any skill by typing its name (e.g. `graph-mega-brain`, `graph-prd`).

---

## graph-accessibility

---
name: graph-accessibility
description: Accessibility compliance audit using WCAG 2.2 AA standards, ARIA validation, screen reader testing, keyboard navigation, color contrast analysis, and i18n readiness
triggers:
  - graph-accessibility
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-accessibility

Accessibility compliance audit using WCAG 2.2 AA standards, ARIA validation, screen reader testing, keyboard navigation, color contrast analysis, and i18n readiness. Ensures UI components are usable by all users regardless of ability.

## When to Use

- Before DEPLOY phase for UI features
- When adding dashboard components
- During VALIDATE phase for user-facing changes
- Quarterly accessibility reviews
- When targeting WCAG compliance

## Mandatory Flow

```
WCAG 2.2 → ARIA → keyboard → contrast → screen reader → i18n → focus → report → write_memory
```

## Workflow

### Step 1: WCAG 2.2 AA Checklist

Audit against the 4 WCAG principles (POUR). Score each: PASS, PARTIAL, FAIL.

| Principle | Key checks |
|-----------|-----------|
| **Perceivable** | `alt` text on images; captions for video/audio; semantic HTML structure |
| **Operable** | All functionality via keyboard; no seizure triggers; pause/stop on auto-advancing content |
| **Understandable** | `lang` attribute set; consistent navigation; form errors with suggestions |
| **Robust** | Valid HTML; correct ARIA usage; works with assistive tech |

#### WCAG 2.2 New Criteria (vs 2.1)

These 4 SCs are new in WCAG 2.2 and not covered by older audit templates:

| SC | Name | Level | Test |
|----|------|-------|------|
| 2.4.11 | Focus Appearance (minimum) | AA | Focus indicator has ≥2px perimeter, ≥3:1 contrast vs adjacent color |
| 2.4.12 | Focus Not Obscured (minimum) | AA | Focused component not fully hidden by sticky headers/footers |
| 2.5.7 | Dragging Movements | AA | Every drag action has a single-pointer alternative (e.g. click-to-move) |
| 2.5.8 | Target Size (minimum) | AA | Interactive targets ≥24×24 CSS pixels (or adequate spacing) |

> Check 2.4.12 explicitly when the layout has a sticky nav or fixed footer — focused items near the top/bottom of the viewport are the most common failure mode.

### Step 2: Automated vs Manual Split

Use this split to allocate review time. Automated tools catch ~35% of WCAG issues; the rest require human judgment.

**Automated (run axe or Lighthouse — no manual effort needed):**
- Missing `alt` on images
- Missing form `<label>` associations
- Color contrast violations
- Missing `lang` attribute
- Duplicate `id` attributes
- Invalid ARIA roles or attribute combinations

Run color contrast check specifically:
```bash
npx @axe-core/cli --rules color-contrast <url>
```

Run full axe audit:
```bash
npx @axe-core/cli <url>
```

**Manual only (automated tools cannot reliably detect these):**
- Logical focus order (Tab sequence makes sense in context)
- Screen reader announcement quality (label text is meaningful, not "button" or "click here")
- Keyboard trap absence (can always Tab out)
- Focus management on dynamic content (modals, route changes, toasts)
- Drag interaction alternatives (SC 2.5.7)
- Complex widget keyboard patterns (arrow keys in menus, tree views, date pickers)
- Reading order matches visual order for screen reader users

### Step 3: ARIA Validation

Verify ARIA landmarks present: `banner`, `navigation`, `main`, `contentinfo`.

| Element | Required ARIA | Common mistake |
|---------|--------------|----------------|
| Buttons (non-`<button>`) | `role="button"` | Clickable `<div>` without role |
| Modals | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` | Missing label association |
| Tabs | `role="tablist"` + `tab` + `tabpanel`, `aria-selected` | Missing selected state |
| Multiple navs | `aria-label` on each `<nav>` | Indistinguishable landmarks |

Flag: `aria-hidden="true"` on any interactive element; images without `alt`.

### Step 4: Keyboard Navigation Checklist

Test these 8 interactions manually — tab through the page with a physical keyboard:

| # | Interaction | Expected behavior |
|---|-------------|-------------------|
| 1 | Tab through all interactive elements | Logical order: top-to-bottom, left-to-right |
| 2 | Visible focus indicator | High-contrast ring visible on every focused element (no `outline: none`) |
| 3 | Skip link | First Tab lands on "Skip to content"; activating it moves focus to `<main>` |
| 4 | Escape on modal/dropdown | Closes overlay; focus returns to the element that opened it |
| 5 | Arrow keys in compound widgets | Tab panels, menus, radio groups, listboxes use arrow key navigation |
| 6 | Enter/Space on buttons | Activates the action (not just mouse click) |
| 7 | Focus trap in modals | Tab cycles within modal; cannot Tab to background content while modal is open |
| 8 | No keyboard trap outside modals | Tab always moves forward; Shift+Tab always moves backward; no dead ends |

Test with Playwright where possible:
```
mcp__playwright__browser_press_key({ key: "Tab" })
mcp__playwright__browser_snapshot()
```

### Step 5: Color Contrast

Check all text meets WCAG AA contrast ratios:

| Element | Minimum Ratio | How to Check |
|---------|--------------|--------------|
| Normal text (<18pt) | 4.5:1 | Check foreground vs background color |
| Large text (>=18pt or >=14pt bold) | 3:1 | Check foreground vs background color |
| UI components | 3:1 | Borders, icons, focus indicators |
| Non-text contrast | 3:1 | Charts, graphs, interactive elements |

Verify information is not conveyed by color alone:
- Error states use icons + color (not just red text)
- Chart data uses patterns + color (not just different colors)
- Links have underline or other non-color indicator

Check dark mode contrast if applicable.

### Step 6: Screen Reader Test Protocol

Minimum 5-step protocol. Run on VoiceOver (Mac) and NVDA (Windows):

| Step | VoiceOver (Mac) | NVDA (Windows) | What to verify |
|------|-----------------|----------------|----------------|
| 1 | Cmd+F5; Safari | Insert+Q; Firefox | SR starts without errors |
| 2 | VO+A (read all) | Insert+↓ (read all) | Page title announced; heading order logical |
| 3 | VO+U → Headings | Insert+F7 → Headings | All headings in order; none skipped |
| 4 | Tab to each form field | Tab to each form field | Label announced before field type |
| 5 | Trigger form error | Trigger form error | Error announced immediately (not on next Tab) |

Also verify: live regions announced without stealing focus; table headers with cell data; button labels are descriptive.

### Step 7: i18n Readiness

| Check | Pass Criteria |
|-------|--------------|
| No hardcoded strings | UI text in i18n files or constants |
| Text direction | RTL support via `dir="rtl"` |
| Date/number format | `Intl.DateTimeFormat` / locale-aware APIs |
| No string concatenation | i18n interpolation (word order varies) |
| Content expansion | Layout holds at 30% longer text (German) |
| Pluralization | Plural rules handled beyond simple "s" suffix |

### Step 8: Focus Management

| Scenario | Expected Behavior |
|----------|-------------------|
| Modal opens | Focus → first focusable element or dialog title |
| Modal closes | Focus → trigger element |
| Form error | Focus → first error message |
| Route change | Focus → new content or page title |
| Toast/notification | Does NOT steal focus — use `aria-live` |
| Dropdown open | Focus → first option |

### Step 9: Accessibility Report

Generate comprehensive accessibility report:

```
Tool: mcp__mcp-graph__write_memory
Params:
  title: "Accessibility Audit — <date>"
  content: "<WCAG scores, ARIA compliance, keyboard, contrast, screen reader, i18n, focus management>"
  tags: ["accessibility", "audit", "wcag", "a11y"]
```

## Output Format

```
Phase: ACCESSIBILITY AUDIT
WCAG Principle Scores:
  Perceivable: PASS/PARTIAL/FAIL
  Operable: PASS/PARTIAL/FAIL
  Understandable: PASS/PARTIAL/FAIL
  Robust: PASS/PARTIAL/FAIL
WCAG 2.2 New Criteria: N/4 passing
ARIA Compliance: N%
Keyboard Navigation Score: N/8
Color Contrast Compliance: N%
Screen Reader Pass Rate: N/5 steps
i18n Readiness: N%
Critical Issues: N
Focus Management Score: N/6
Overall Grade: A/B/C/D/F

Saved to memory: "Accessibility Audit — <date>"
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT treat accessibility as optional — it is a legal requirement in many jurisdictions
- Do NOT rely only on automated tools — they catch ~35% of issues; manual testing is required
- Do NOT use `aria-hidden` on interactive elements
- Do NOT remove focus outlines without providing a visible replacement that meets SC 2.4.11
- Do NOT use color as the only indicator of state or meaning
- Do NOT skip screen reader testing — it reveals the real user experience
- Do NOT hardcode strings in UI components — they break i18n
- Do NOT skip WCAG 2.2 new criteria — SC 2.5.8 (target size) fails silently in automated audits

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-analyze

---
name: graph-analyze
description: Execute the ANALYZE phase of the lifecycle via the `agf` CLI — PRD creation, requirements, Definition of Ready (7 checks), cross-project learning
triggers:
  - graph-analyze
version: 2.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-analyze

Execute the ANALYZE phase of the lifecycle, driving the `agf` CLI (zero MCP). Creates the PRD, defines requirements, and imports them into the execution graph. Entry point of the 9-phase lifecycle.

## When to Use

- Starting a new project or feature from scratch
- Defining requirements for a new epic
- Importing an existing PRD into the graph
- The current phase reported by `agf phase` is `ANALYZE`

## Mandatory Flow

```
[agf search] → agf import-prd <file> / agf node add → agf edge add → agf gate analyze → agf phase design
```

## Workflow

### Step 0: Cross-Project Learning

If similar projects exist, apply learning before starting analysis:

```bash
agf search "<errors | estimates | adrs | patterns>"
agf memory read <name>
```

Process: query `agf` history → extract patterns from completed epics (velocity, failure modes, recurring risks) → apply to current analysis. This calibrates estimates and surfaces known risks early. Skip only if the project is the first of its kind.

### Step 1: Understand the Scope

Ask the user what they want to build. Gather:
- Problem statement
- Target users
- Core features (MVP scope)
- Non-functional requirements
- Known constraints

### Step 2: Requirements Quality Gate

Before creating nodes, validate requirements against 4 criteria (from [[swe-at-google]] — requirements that fail this gate produce untestable, ambiguous, or incomplete specs):

| Criterion | Test | Fail signal |
|-----------|------|-------------|
| **Testable** | Can you write a passing/failing test for it? | "system should be fast" → fail |
| **Unambiguous** | Does every reader interpret it the same way? | "intuitive UI" → fail |
| **Complete** | Does it fully describe the behavior including edge cases? | "handle errors" → fail |
| **Consistent** | Does it contradict any other requirement? | conflicting constraints → fail |

Any requirement failing 2+ criteria must be rewritten or resolved before importing.

### Step 3: Ambiguity Resolution Protocol

When requirements are unclear, follow this sequence before creating graph nodes:

1. **Spike** — time-box exploration to 2h max. Write throwaway code or research to reduce uncertainty.
2. **Clarify** — ask the user the specific clarifying question raised by the spike. One question at a time.
3. **Document assumption** — if clarification is unavailable, record the assumption explicitly:
   ```bash
   agf node add --type constraint --title "Assumption: <text>"
   ```

Never silently assume. Every assumption that cannot be confirmed becomes a named constraint node so it surfaces in the DoR gate.

### Step 4: Create or Import PRD

**Option A — Import existing PRD (preferred if $graph-prd was used):**
```bash
agf import-prd <file>
```

**Option B — Create PRD from conversation:**
Write a structured PRD covering vision, problem, objectives, architecture overview, functional requirements, non-functional requirements, and risk analysis. Save as `prd.md`, then import with `agf import-prd prd.md`.

### Step 5: Structure Requirements as Nodes

```bash
agf node add --type requirement
agf node add --type epic
```

### Step 6: Create Edges

```bash
agf edge add <from> <to> --type <rel>
```

Edge types: `requirement → epic`, `epic → milestone`, `requirement → requirement`.

### Step 7: Risk & Constraint Analysis

```bash
agf node add --type risk
agf node add --type constraint
```

Link risks to the requirements/epics they affect. Each Critical/High risk (P×I ≥ 6) must have a mitigation node.

### Step 8: Save Key Decisions

```bash
agf memory write <name>
```

Record requirement decisions, validated assumptions, and risk mitigations that should inform DESIGN.

### Step 9: Analysis Depth Calibration

Stop deepening analysis when confidence in estimates reaches ≥70%. Three signals that indicate sufficient confidence:

1. **Estimation signal** — team can assign an XP size to every epic without heated debate
2. **Risk signal** — no risks remain at Critical severity without a mitigation strategy
3. **Scope signal** — out-of-scope items are explicitly listed and agreed upon

If any signal is absent, run one more round of the Ambiguity Resolution Protocol (Step 3) and reassess. Over-analyzing past 70% confidence yields diminishing returns (from [[kanban-in-action]] — WIP in analysis has a cost; stop when flow can resume).

### Step 10: Validate — PRD Quality

```bash
agf gate analyze
```

### Step 11: Definition of Ready (DoR) — 7 Checks

```bash
agf gate analyze
```

All 7 checks must pass before transitioning to DESIGN. This is the gate between ANALYZE and PLAN (from [[kanban-in-action]] — every column entry requires meeting explicit entry criteria):

| # | Check | What it verifies |
|---|-------|-----------------|
| 1 | `has_requirements` | ≥1 epic or requirement node in graph |
| 2 | `has_acceptance_criteria` | Every epic has ≥1 testable AC node |
| 3 | `no_orphans` | No requirement or epic is disconnected from the graph |
| 4 | `no_cycles` | No dependency cycles in the requirement graph |
| 5 | `has_constraints` | ≥1 constraint node (including documented assumptions) |
| 6 | `has_risks` | ≥1 risk node with P×I score |
| 7 | `prd_quality_score` | PRD quality score ≥ 60/100 |

If any check fails, fix the identified issue and re-run. Do not advance to DESIGN until 7/7 pass.

### Step 12: Transition

Once both gates pass:
```bash
agf phase design
```

Follow the next-action hint printed by the `agf` CLI.

## Output Format

```
Phase: ANALYZE → DESIGN
PRD: imported (N requirements, M epics, K risks, J constraints)
Assumptions documented: A nodes created
Ambiguities resolved: B spikes run
Quality gate: prd_quality — score N/100, grade X
DoR gate: 7/7 checks passed
Cross-project learning: L patterns applied from history
Analysis confidence: ≥70% (estimation + risk + scope signals green)
Status: Ready to proceed to DESIGN phase
```

## Anti-Patterns

- Do NOT start coding during ANALYZE — this phase is requirements only
- Do NOT create task-level nodes yet — that happens in PLAN
- Do NOT skip risk/constraint analysis — they inform DESIGN decisions
- Do NOT silently assume — every unresolved ambiguity becomes a named constraint node
- Do NOT over-analyze — stop when confidence signals reach ≥70%
- Do NOT advance to DESIGN with any DoR check failing
- Do NOT ignore cross-project learning — past patterns prevent repeat mistakes
- Do NOT use deprecated forms — use `agf node add` to create nodes

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

## Economy

Token economy is part of the loop: run `agf savings` / `agf metrics --economy-report` after each task, then feed savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Cross-References

- [[swe-at-google]] — requirements quality gate, testability, Hyrum's Law on implicit assumptions
- [[pragmatic-programmer]] — DRY, Design by Contract, spike-before-implement
- [[kanban-in-action]] — column entry criteria, WIP in analysis, flow resumption signals

---

## graph-api-design

---
name: graph-api-design
description: API governance and design audit using OpenAPI/Swagger spec generation, REST maturity model, contract validation, and breaking change detection
triggers:
  - graph-api-design
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-api-design

API governance and design audit using OpenAPI/Swagger spec generation, REST maturity model, contract validation, and breaking change detection. Ensures consistent naming, validated contracts, backward compatibility, and comprehensive documentation across all API surfaces.

## When to Use

- Before REVIEW when APIs change
- When adding new endpoints or MCP tools
- During DESIGN for API-first development
- Before major releases

## Mandatory Flow

```
endpoint inventory --> naming conventions --> contract validation --> breaking changes --> versioning --> documentation --> report --> write_memory
```

## Workflow

### Step 1: Endpoint Inventory

Catalog all API routes (`src/api/routes/`) and MCP tools (`src/mcp/tools/`). Count endpoints per resource. Verify RESTful naming: pluralized nouns for resources, HTTP verbs for actions. Flag non-RESTful patterns.

- List all Express Router files and extract route definitions (GET, POST, PUT, DELETE, PATCH)
- List all MCP tool registrations via `server.tool()` calls
- Group endpoints by resource (e.g., `/nodes`, `/edges`, `/knowledge`)
- Count total endpoints per router and per HTTP method
- Flag routes using verbs in the URL path (e.g., `/getNodes` instead of `GET /nodes`)

### Step 2: Naming Convention Audit

Check route naming consistency: kebab-case paths, consistent pluralization, no verbs in URLs (use HTTP methods instead). For MCP tools: snake_case names, consistent parameter naming. Compare against existing patterns.

- REST routes: verify kebab-case (`/code-graph`, not `/codeGraph`)
- REST routes: verify pluralized resource nouns (`/nodes`, not `/node`)
- REST routes: verify no action verbs in paths — use HTTP methods instead
- MCP tools: verify snake_case naming (`import_prd`, not `importPrd`)
- MCP tools: verify consistent parameter naming across related tools (e.g., `nodeId` everywhere, not mixed `node_id`/`nodeId`)
- Score: compliant endpoints / total endpoints = naming compliance %

### Step 3: Hyrum's Law Checklist
From [[swe-at-google]] Ch1: "With a sufficient number of users of an API, all observable behaviors will be depended on by somebody." Apply this as the first design law — not a caution, a guarantee.

Seven behaviors that silently become implicit contracts:
1. **Response field order** — consumers parse positionally; even if your spec says "object", order locks in.
2. **Error message text** — clients string-match on error messages. Changing wording breaks them.
3. **Timing and latency** — clients set timeouts calibrated to current latency. Faster or slower can break.
4. **Undocumented fields** — extra fields in responses get parsed and depended on even if never in the spec.
5. **HTTP status codes for edge cases** — a 400 that should have been a 422 gets handled as 400 by all callers.
6. **Pagination shape** — `next_cursor` vs `nextCursor`, presence of `total` — all become expected.
7. **Idempotency behavior** — callers retry on failure; if repeat POSTs weren't always safe, they assumed they were.

For each of the 7: mark Y (currently documented + tested) or N (implicit, untested risk). Any N = design debt.

### Step 4: Contract Validation

Verify all endpoints have Zod schema validation on input (`validateBody`/`validateQuery` middleware). Check all MCP tools have `z.string()`/`z.number()` params. Flag endpoints accepting unvalidated input. Verify response shapes are consistent.

- Check each API route for `validateBody()` or `validateQuery()` middleware usage
- Check each MCP tool for Zod schema definitions on all parameters
- Flag any `req.body` or `req.query` access without prior validation middleware
- Flag any MCP tool parameter without a Zod type definition
- Verify response shapes use consistent patterns (e.g., `{ data, meta }` or `{ result }`)
- Score: validated endpoints / total endpoints = validation coverage %

### Step 5: Breaking Change Classification
From [[swe-at-google]] Ch1/Ch15/Ch21 — classify every detected change before deciding if it needs a version bump.

| Change Type | Classification | Action Required |
|-------------|---------------|-----------------|
| Add optional field to response | Additive — safe | None |
| Add optional request parameter | Additive — safe | None |
| Add new endpoint | Additive — safe | None |
| Remove field from response | Breaking | Major version bump + migration path |
| Remove or rename endpoint | Breaking | Major version bump + migration path |
| Change field type (string → number) | Breaking | Major version bump + migration path |
| Make optional param required | Breaking | Major version bump + migration path |
| Change observable behavior (Hyrum) | Breaking by Hyrum | Treat as breaking even if spec says safe |
| Change error message text | Breaking by Hyrum | Announce in changelog; avoid if possible |

Run: `git diff HEAD~10..HEAD -- src/api/routes/ src/mcp/tools/` to enumerate recent changes, then classify each.

### Step 6: Compatibility Matrix
Three compatibility types to verify per change (from [[swe-at-google]] Ch21):

| Type | Breaks When | Check |
|------|-------------|-------|
| **Source** | A client must change its source code to compile | Parameter rename, type change, removal |
| **Behavioral** | A client's runtime behavior changes without source change | Semantics shift, Hyrum-covered behaviors |
| **Contract** | A documented guarantee is revoked | SLA, idempotency, ordering, pagination |

A change that is source-compatible can still be behavioral-breaking. All three axes must be evaluated.

### Step 7: Deprecation Timeline
From [[swe-at-google]] Ch15 — advisory-only deprecations rarely complete. Use compulsory pattern with staffed migration:

```
Announce → Warn → Sunset → Remove
```

| Phase | Duration | Action |
|-------|----------|--------|
| **Announce** | Day 0 | Publish changelog; mark `@deprecated` with replacement reference |
| **Warn** | 30–90 days | Surface warning at call time (log line, response header); provide migration guide |
| **Sunset** | End of warn period | Stop accepting new dependents; existing callers still work |
| **Remove** | After sunset | Delete endpoint; callers get 410 Gone or tool registration removed |

Deprecation warnings must be **actionable** (link to replacement) and **relevant** (surface at call time, not in batch emails). From [[swe-at-google]] Ch15: alert fatigue is real — one clear warning beats ten vague ones.

### Step 8: Documentation Check

Verify API routes have JSDoc comments. Check MCP tools have description strings in `server.tool()` registration. Flag undocumented public endpoints. Verify parameter descriptions exist.

- Check each route handler file for JSDoc comments on exported functions
- Check each MCP tool for a `description` string in its registration
- Check MCP tool parameters for description strings
- Verify `docs/reference/MCP-TOOLS-REFERENCE.md` is up to date with current tool list
- Verify `docs/reference/REST-API-REFERENCE.md` is up to date with current route list
- Flag any public endpoint without documentation as undocumented

### Step 9: API Report

Generate the full audit report. Score 0-100 per dimension. Save via `mcp__mcp-graph__write_memory`.

```
Tool: mcp__mcp-graph__write_memory
Params:
  title: "API Design Audit — <date>"
  content: "<findings summary with scores per dimension, breaking changes, undocumented endpoints>"
  tags: ["api", "audit", "design", "governance"]
```

## Output Format

```
Phase: API DESIGN AUDIT
Total Endpoints: <N> REST + <N> MCP tools
Naming Compliance: <N>%
Validation Coverage: <N>%
Hyrum Risks: <N> unprotected behaviors
Breaking Changes: <N> (additive: <N>, breaking: <N>, Hyrum-breaking: <N>)
Undocumented Endpoints: <N>
Deprecated Items: <N> (with migration: <N>, without: <N>)
Overall Grade: <A-F>
Recommendations: <top 3 actions>

Saved to memory: "API Design Audit — <date>"
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT add endpoints without Zod validation — every input boundary must be validated
- Do NOT rename parameters without deprecation period — consumers depend on the current contract
- Do NOT remove endpoints without migration path — provide alternatives before removal
- Do NOT use verbs in REST URLs — use HTTP methods (GET, POST, PUT, DELETE) instead
- Do NOT skip API documentation — it is the contract between producer and consumer
- Do NOT break backward compatibility without major version bump — semver is mandatory
- Do NOT treat "undocumented" as "safe to change" — Hyrum's Law applies regardless of what the spec says
- Do NOT use advisory-only deprecation for large API surfaces — it will not complete without a compulsory timeline

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-architecture

---
name: graph-architecture
description: Architecture governance using C4 Model, ADR lifecycle, Architecture Fitness Functions, layer boundary enforcement, and drift detection
triggers:
  - graph-architecture
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-architecture

Architecture governance using C4 Model (Context, Container, Component, Code), ADR lifecycle management, Architecture Fitness Functions, layer boundary enforcement, and architecture drift detection. Ensures the system's documented architecture stays aligned with the actual codebase over time.

## When to Use

- During DESIGN phase for new features
- Quarterly architecture reviews
- When coupling analysis shows degradation
- When onboarding new developers to understand system structure
- Before major refactors

## Mandatory Flow

```
C4 context → C4 container → C4 component → ADR inventory → fitness functions → layer boundaries → drift detection → report → write_memory
```

## Workflow

### Step 1: C4 Context Diagram

Map the system's external boundaries. Identify: users (developers, AI agents), external systems (GitHub, Context7, Playwright, SQLite), and the mcp-graph system itself. Generate mermaid diagram via `mcp__mcp-graph__export(action:"mermaid", format:"flowchart")`. Document: who uses the system, what external dependencies exist, what data flows in/out.

### Step 2: C4 Container Diagram

Map internal containers: CLI (Commander.js), MCP Server (tools), REST API (Express), Dashboard (React), SQLite Store, Knowledge Store, Code Intelligence Engine. For each container: technology, responsibility, communication protocols. Verify containers match `src/` directory structure (`cli/`, `mcp/`, `api/`, `web/`, `core/store/`, `core/code/`).

### Step 3: C4 Component Diagram

For each container, map key components. Core modules: `parser/`, `importer/`, `planner/`, `context/`, `rag/`, `search/`, `insights/`, `integrations/`. Verify component boundaries: `core/` never imports from `cli/` or `mcp/` (dependency direction rule from CLAUDE.md). Use `mcp__mcp-graph__code_intelligence` for real dependency analysis.

### Step 4: ADR Inventory & Lifecycle

List all decision nodes in graph via `mcp__mcp-graph__list(type:"decision")`. Verify each ADR has: Status (Proposed/Accepted/Deprecated/Superseded), Context, Decision, Consequences. Check for stale ADRs (decisions no longer relevant). Use `mcp__mcp-graph__analyze(mode:"adr")` for quality scoring.

### Step 5: Architecture Fitness Functions

Define automated checks that verify architecture properties hold:

| Function | Tool | What It Checks |
|----------|------|----------------|
| No circular dependencies | `mcp__mcp-graph__analyze(mode:"cycles")` | Dependency graph is acyclic |
| Layer isolation | grep imports | `core/` doesn't import `mcp/` or `cli/` |
| Coupling score | `mcp__mcp-graph__analyze(mode:"coupling")` | Module coupling within thresholds |
| Interface completeness | `mcp__mcp-graph__analyze(mode:"interfaces")` | Public contracts fully typed |

Score each fitness function pass/fail. See **Fitness Function Scoring Table** below for thresholds.

### Step 6: Layer Boundary Enforcement

Verify the dependency direction rule: `schemas/` <- `core/` <- `mcp/` <- `cli/`. Check for violations: grep for imports that cross layer boundaries in the wrong direction. Flag: core importing from mcp, schemas importing from core, cli containing business logic. Cross-reference with CLAUDE.md rules. See **Layer Violation Remediation** below when violations are found.

### Step 7: Architecture Drift Detection

Compare current codebase structure with documented architecture (C4 diagrams, ADRs). Detect: new modules not in any diagram, deprecated modules still in use, component responsibilities that shifted, new external dependencies not documented. Use `mcp__mcp-graph__analyze(mode:"code_sync")` for reference staleness. Apply **Architecture Drift Severity** thresholds below.

### Step 8: Architecture Report

Score per dimension (C4 completeness, ADR quality, fitness functions, layer compliance, drift). Generate updated C4 diagrams as mermaid. List architectural debt items. Save via `mcp__mcp-graph__write_memory`.

## Output Format

```
Phase: ARCHITECTURE GOVERNANCE
C4 Diagrams: Context (N actors, N systems), Container (N containers), Component (N components)
ADR Inventory: N total (N accepted, N deprecated, N stale)
ADR Quality Score: N/100
Fitness Functions: N/N passed
Layer Violations: N found
Architecture Drift: N items detected
Architectural Debt: N items
Overall Architecture Health: Grade A-F

Saved to memory: "Architecture Review — <date>"
```

---

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Fitness Function Scoring Table

Numeric thresholds for each automated architecture check. [[pragmatic-programmer]] Tip 59 — test early, test automatically.

| Metric | Pass | Warn | Fail | Fix |
|--------|------|------|------|-----|
| Circular dependency count | 0 | — | ≥1 | Break cycle via interface or move module |
| Layer violation count | 0 | — | ≥1 | See Layer Violation Remediation |
| Module coupling score (0–1) | ≤0.3 | 0.31–0.5 | >0.5 | Extract shared abstraction; invert dependency |
| Interface completeness | 100% | 80–99% | <80% | Add missing type contracts |
| Undocumented external deps | 0 | 1 | ≥2 | Add ADR or update C4 container diagram |
| Stale ADRs (>90 days, Proposed) | 0 | 1 | ≥2 | Accept, reject, or supersede |

Overall: all pass = A, one warn = B, one fail = C, two+ fails = D/F.

---

## ADR Quality Rubric

Score each ADR 0–2 per criterion (max 10 points). [[pragmatic-programmer]] "There Are No Best Practices" — always record context and forces.

| Criterion | 0 | 1 | 2 |
|-----------|---|---|---|
| **Context** | Missing | Vague situation description | Clear problem statement with constraints |
| **Forces** | Missing | One force listed | ≥2 competing forces (cost, speed, correctness…) |
| **Decision** | Missing | States what but not why | States what + why this option over others |
| **Alternatives** | Missing | One alternative named | ≥2 alternatives with brief trade-off each |
| **Consequences** | Missing | Only positive outcomes | Both positive and negative consequences listed |

- **8–10**: High quality — publish and link to affected modules
- **5–7**: Acceptable — add missing sections before next review
- **0–4**: Block merge — incomplete ADR provides false confidence

---

## Architecture Drift Severity

How many new undocumented modules or changes constitute real drift. [[humble-continuous-delivery]] — the pipeline fails fast; architecture governance should too.

| Signal | Severity | Action |
|--------|----------|--------|
| 1 new undocumented module | Monitor | Note in next review; update C4 if it stabilizes |
| 3+ new undocumented modules | Flag | Update C4 diagrams before next feature work |
| Any layer violation | Block | Do not merge; apply Layer Violation Remediation |
| Deprecated module still imported | Flag | Schedule removal; create ADR if intentional keep |
| Component responsibility shift (no ADR) | Flag | Write ADR retroactively; re-score quality |
| New external dependency, no ADR | Block | Write ADR; add to C4 container diagram |

---

## Layer Violation Remediation

When a violation of the `schemas/ ← core/ ← mcp/ ← cli/` rule is found, apply fixes in this order (lowest effort first):

1. **Move to correct layer** — if the import simply belongs in a different module, move it. No new abstraction needed. Best for: accidental misplacement.
2. **Dependency Inversion** — introduce an interface in the lower layer; the upper layer implements it. The lower layer depends on the abstraction, not the concrete upper module. Best for: core needing a capability that lives in mcp.
3. **Adapter layer** — create a thin adapter module that translates between layers without leaking internal structure. Best for: third-party integrations or legacy seams where inversion is impractical.
4. **Extract shared module** — if two layers both need the same code, extract it into `schemas/` or a new `shared/` module that both import. Best for: utility code duplicated across layers.

Never leave a violation with only a comment — board it up with a tracked issue and a target date ([[pragmatic-programmer]] Broken Window Theory).

---

## Early Decay Signals

Five broken-window signals that predict architectural decay before metrics degrade. [[pragmatic-programmer]] Tip 4 — fix or board up every sign of neglect immediately.

1. **TODO imports** — `// TODO: move this to core` comments in boundary-crossing imports. Signal: engineers know the violation exists but it wasn't fixed.
2. **God module growth** — a single module's line count or dependency count grows faster than the rest of the codebase. Signal: responsibilities are collapsing inward.
3. **Test isolation failures** — unit tests that require spinning up more than one layer to pass. Signal: layer isolation is already broken at the code level.
4. **ADR graveyard** — more than 20% of ADRs in Proposed status older than 30 days. Signal: decision-making is stalling; architecture is drifting without governance.
5. **Dependency version skew** — the same external library imported at different versions in different modules. Signal: modules are diverging; shared contracts are eroding.

When any signal appears: log it, assign an owner, set a resolution date. Do not normalize it.

---

## Anti-Patterns

- Do NOT document architecture only once — it drifts
- Do NOT skip C4 Context — it defines system boundaries
- Do NOT create ADRs without Consequences section — trade-offs matter
- Do NOT ignore layer boundary violations — they compound into spaghetti
- Do NOT skip fitness functions — automated checks catch drift early
- Do NOT let ADRs go stale — review quarterly
- Do NOT over-architect — document what exists, not what you wish existed

## Cross-References

- [[pragmatic-programmer]] — Broken Window Theory, Orthogonality, Ubiquitous Automation, DRY at architectural scale
- [[humble-continuous-delivery]] — Deployment pipeline as fitness function model; fail-fast gates; DORA metrics for delivery health

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-brainstorm

---
name: graph-brainstorm
description: Ideação matemática multi-perspectiva pré-ciclo — gera ≥10 candidatos, pontua via PERT × Pareto × Cynefin × TOC, filtra top quartil e persiste como nós `requirement` (tag brainstorm) prontos para $graph-prd. Entry point para espaços de problema vagos.
triggers:
  - graph-brainstorm
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
category: lifecycle
phase: PRÉ-ANALYZE
phases: []
toolchain:
  - agf stats
  - agf query
  - agf gaps
  - agf node add
  - agf memory write
  - agf savings
---

# graph-brainstorm

Ideação matemática pré-ciclo: gera candidatos de alta entropia, descarta o ruído com PERT × Pareto × Cynefin × TOC e persiste só os vencedores como `requirement` nodes no grafo. Dirija tudo pelo CLI `agf` — **zero MCP**.

See also: `[[kanban-in-action]]` (WIP limits, Little's Law, flow metrics)

## When to Use

- Espaço de problema vago: você tem uma ideia mas nenhum PRD
- Backlog vazio ou estagnado: `agf stats` retorna `totalNodes < 4`
- Pós-LISTENING: feedback do usuário sugere pivô ou nova funcionalidade
- `$graph-catalyst` delegou para esta skill (condição: `backlog empty, no PRD`)

**Não usar quando:**
- `agf query --type requirement --status backlog` retorna ≥ 4 nós — vá direto para `$graph-prd`
- `agf query --status in_progress` retorna nó ativo — termine o WIP antes (Little's Law: CT = WIP/TH)

## Mandatory Flow

```
agf stats → cynefin → diverge (7 perspectivas) → TOC constraint ID
→ score (PERT×Pareto×Cynefin×TOC) → pareto filter → WIP gate
→ agf node add (winners) → agf memory write → agf savings
```

## Steps

### Passo 1 — Monitor (estado atual)

```bash
agf stats                          # totalNodes, byStatus
agf savings                        # economy baseline
agf gaps --severity required --json  # blockers ativos
agf query --status in_progress     # WIP check (deve ser 0)
agf query --type requirement --status backlog  # candidatos existentes
```

Se `in_progress` > 0: **PARE** — resolva o WIP antes de divergir.
Se `requirement backlog` ≥ 4: **PULE** para `$graph-prd` (Pareto aplicado previamente).

---

### Passo 2 — Classificação Cynefin

Confirme com o usuário o domínio do problema:

| Domínio | Cynefin Weight (`w`) | Critério |
|---------|----------------------|---------|
| Óbvio | 0.5 | Solução conhecida, padrão claro |
| Complicado | 1.0 | Solução identificável com expertise |
| Complexo | 2.0 | Solução emerge por experimentação |
| Caótico | 3.0 | Sem padrão, ação imediata urgente |

Domínios complexos e caóticos penalizam candidatos de alto esforço — filtrando soluções irrealistas primeiro.

---

### Passo 3 — Identificação da Constraint TOC

Antes de gerar candidatos, identifique o **gargalo sistêmico atual**:

```bash
agf gaps --kind dependency          # gaps que bloqueiam múltiplos nós
agf query --status blocked          # tasks presas por dependência
agf kanban                          # coluna com maior acumulação = bottleneck
```

**Regra de ouro TOC:** o sistema produz no ritmo do seu elo mais fraco. Candidates que desbloqueiam a constraint ativa recebem multiplicador ×2 no score final.

**Como identificar a constraint:**
1. Qual coluna do kanban acumula mais nós? → gargalo de capacidade
2. Qual gap `severity: required` bloqueia mais de 1 nó downstream? → gargalo de dependência
3. Qual módulo aparece em > 3 tasks `blocked`? → gargalo de acoplamento

Registre: `CURRENT_CONSTRAINT = "<descrição>"` para usar no Passo 4.

---

### Passo 4 — Divergência (≥ 10 candidatos)

Gere ≥ 10 ideias radicalmente diferentes usando 7 perspectivas:

| Perspectiva | Pergunta provocadora | Critério de qualidade |
|-------------|---------------------|----------------------|
| **JTBD** | Qual "trabalho" real o usuário quer realizar? | Candidato descreve outcome do usuário, não feature técnica |
| **TOC** | Qual gargalo sistêmico, se removido, libera o maior throughput? | Candidato ataca a `CURRENT_CONSTRAINT` identificada no Passo 3 |
| **Token Economy** | Qual mudança reduz input tokens > 30% com mesmo output? | Candidato tem métrica clara de redução mensurável |
| **Six Sigma** | Qual defeito recorrente está gerando retrabalho silencioso? | Candidato endereça defeito com frequência ≥ 2×/sprint |
| **Wardley** | Qual componente está maduro demais para ser customizado? | Candidato substitui código custom por commodity/OSS |
| **Risk** | Qual risco latente pode explodir como incident se não for endereçado? | Candidato tem likelihood × impact alto no horizonte de 60 dias |
| **Tech Debt** | Qual abstração está travando 3+ features em paralelo? | Candidato desacopla ≥ 3 dependências simultâneas |

Seja específico: cada candidato deve ter uma **ação** e um **resultado** mensuráveis.

---

### Passo 5 — Pontuação (PERT × Pareto × Cynefin × TOC)

#### Fórmula completa

```
# 1. PERT — esforço esperado e incerteza
E     = (O + 4×M + P) / 6        # esforço esperado (story points ou horas)
σ     = (P - O) / 6              # desvio padrão (incerteza)
PERT_norm = 1 / (E + σ)          # normalizado: maior esforço → score menor

# 2. Pareto — valor por unidade de esforço
business_value = impact × δ      # impact (1–5) × entropy gain (0–1, novidade vs grafo)
  δ = 1 - max_cosine_similarity(candidato, existing_tasks)
  # 0 = duplicata exata; 1 = totalmente novo
  # Proxy mental: 0 palavras-chave sobrepostas = δ≈1; todas sobrepostas = δ≈0
Pareto_value = business_value / (E + σ)   # impacto por ponto de esforço

# 3. Cynefin — peso de domínio (do Passo 2)
w = Cynefin_weight               # 0.5 | 1.0 | 2.0 | 3.0

# 4. TOC — multiplicador de constraint
TOC_mult = 2.0  se candidato desbloqueia CURRENT_CONSTRAINT
TOC_mult = 1.0  caso contrário

# Score final (comparável apenas dentro do mesmo domínio Cynefin)
final_score = PERT_norm × Pareto_value × w × TOC_mult
```

**Tabela de pontuação (preencha para cada candidato):**

| # | Candidato | Impact | O | M | P | E | σ | δ | w | TOC_mult | Score |
|---|-----------|--------|---|---|---|---|---|---|---|----------|-------|
| 1 | …         | …      | … | … | … | … | … | … | … | …        | …     |

---

### Passo 6 — Filtro Pareto (top 25%)

De N candidatos, aceite apenas os top **⌈N × 0.25⌉** por `final_score`, com mínimo de 3 e máximo de 5.

Exemplo: 10 candidatos → aceite top 3 (≥ percentil 75). Candidatos abaixo do corte são descartados — não os persista. O valor do brainstorm está na seletividade.

---

### Passo 7 — WIP Gate

```bash
agf query --type requirement --status backlog | jq '.data | length'
```

- ≥ 4 nós do tipo `requirement` no backlog → **PARE**, vá para `$graph-prd` com o que existe.
- < 4 → prossiga para persistência.

---

### Passo 8 — Persistência no Grafo

Para cada candidato vencedor (máximo 5), crie um nó `requirement`:

```bash
agf node add \
  --title "<verbo de ação> <resultado mensurável>" \
  --type requirement \
  --priority <1-5 baseado em score normalizado> \
  --ac "GIVEN <contexto> WHEN <ação> THEN <resultado verificável> [AND score=<score>] [AND cynefin=<domínio>]"
```

**Padrão de título:** Use verbos fortes — "Reduzir", "Eliminar", "Implementar", "Extrair", "Automatizar".

---

### Passo 9 — Memória de Sessão

```bash
agf memory write brainstorm-$(date +%Y%m%d) --content \
  "Candidatos gerados: N | Aprovados: M | Domínio: <cynefin> | Constraint: <CURRENT_CONSTRAINT> | Top score: <value> | Nodes: <ids>"
```

---

### Passo 10 — Economy Spiral

```bash
agf savings
agf metrics --economy-report
agf learning stats        # atualiza routing baseado nesta sessão
```

Reporte o delta de economy: tokens estimados poupados por filtrar candidatos ruins antes de entrar no ciclo LLM completo.

## Output Format

```
Brainstorm: <slug da ideia principal>
Domínio: <cynefin domain> (w=<weight>)
Constraint ativa: <CURRENT_CONSTRAINT>
Candidatos gerados: N | Aprovados pelo Pareto (top 25%): M
─────────────────────────────────────────────────
Top candidatos persistidos:
  #1 <id> — "<título>" | score=<value> | TOC=<mult> | priority=<N>
  #2 <id> — "<título>" | score=<value> | TOC=<mult> | priority=<N>
  …
Economy: tokens estimados poupados na divergência = <N> (vs gerar PRD direto sem filtro)
Próximo: $graph-prd → agf import-prd
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- **NÃO gerar 1 ideia e ir direto para PRD** — o valor está na divergência antes da convergência (OODA: Orient)
- **NÃO criar nós do tipo `idea`** — NodeType inválido; use sempre `--type requirement`
- **NÃO persistir > 5 candidatos** — Pareto obriga a escolher; mais nós = mais WIP = maior cycle time (Little's Law: CT = WIP/TH)
- **NÃO pular Cynefin** — scores sem weight não são comparáveis entre domínios diferentes
- **NÃO pular identificação de constraint** — sem TOC_mult, candidatos que desbloqueiam gargalos são subvalorizados
- **NÃO usar brainstorm se WIP > 0** — resolva o in_progress antes de divergir

## Related Skills

- $graph-catalyst — `agf skill show graph-catalyst` (orquestrador que delega para esta skill)
- $graph-prd — `agf skill show graph-prd` (próxima skill no ciclo)
- $graph-analyze — `agf skill show graph-analyze` (pós-PRD)
- `[[kanban-in-action]]` — WIP limits, Little's Law, flow diagnosis

## Constraints

- CLI-first: tudo via `agf` — zero MCP
- WIP=1: nunca divergir com task `in_progress` ativa
- Pareto obrigatório: top 25%, mínimo 3, máximo 5 — nunca persistir todos os candidatos
- NodeType válido: `requirement` (nunca `idea`)
- Score é comparável apenas dentro do mesmo domínio Cynefin
- TOC_mult deve ser calculado após identificar `CURRENT_CONSTRAINT` no Passo 3

---

## graph-bug-hunter

---
name: graph-bug-hunter
description: Automated bug discovery through static analysis, LSP diagnostics, pattern detection, regression hotspot analysis, and error catalog mining
triggers:
  - graph-bug-hunter
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-bug-hunter

Automated bug discovery through static analysis, LSP diagnostics, pattern detection, regression hotspot analysis, and error catalog mining. Proactively finds bugs before they reach production.

## When to Use

- Before VALIDATE phase — catch bugs early before formal validation
- During code review — systematic bug detection across the codebase
- Proactively during LISTENING phase — periodic health checks
- When quality metrics decline — investigate root causes of quality degradation

## Mandatory Flow

```
LSP diagnostics → ESLint deep scan → pattern detection → dependency issues → regression hotspots → error history → bug triage → false-positive filter → report → node(add) → write_memory
```

## LSP Diagnostic Priority

Not all diagnostics are equal. Process in this order — stop acting on lower tiers until higher tiers are clear (from `[[effective-debugging]]` item 1: prioritize before diving):

| Tier | Level | Action |
|------|-------|--------|
| 1 | **error** | Block — fix before anything else |
| 2 | **warning** | Schedule — fix in current sprint |
| 3 | **hint / info** | Track — batch with Low severity bugs |

Files with ≥3 errors are **high-attention targets**. Files with ≥5 warnings but 0 errors are **smell targets**.

Run: `npx tsc --noEmit` to get the full compiler list. Use `mcp__mcp-graph__code_intelligence` for symbol-level analysis.

## High-Signal Pattern Catalog

Eight patterns that convert to real bugs at high frequency (from `[[effective-debugging]]` and `[[pragmatic-programmer]]`). Run each grep; matches go straight to triage:

```bash
# 1. Non-null assertion (runtime crash waiting to happen)
grep -rn '!\.' src/ --include='*.ts' --include='*.tsx'

# 2. Empty catch (swallowed errors — silent failures)
grep -rn 'catch\s*{[[:space:]]*}' src/

# 3. any type escape hatch (type safety hole)
grep -rn ': any' src/ --include='*.ts'

# 4. Floating promise (unhandled async failure)
grep -rn 'async.*=>' src/ | grep -v 'await\|return'

# 5. TODO/FIXME/HACK (acknowledged technical debt)
grep -rn 'TODO\|FIXME\|HACK' src/

# 6. Synchronous I/O in async context (blocking event loop)
grep -rn 'readFileSync\|writeFileSync\|execSync' src/

# 7. console.log in production paths (data leak / noise)
grep -rn 'console\.log' src/ --include='*.ts' --include='*.tsx'

# 8. Magic numbers (undocumented domain knowledge)
grep -rn '[^a-zA-Z_][0-9]\{3,\}[^0-9]' src/ --include='*.ts'
```

## Hotspot Risk Score

Bugs cluster in high-churn, high-complexity, low-coverage files (from `[[effective-debugging]]` item 8: amplify failure signals). Score every file:

```
Risk = Change Frequency × Complexity × (1 − Coverage)
```

- **Change Frequency**: commits touching the file in the last 30 days  
  `git log --since="30 days" --format="" --name-only | sort | uniq -c | sort -rn`
- **Complexity**: LSP diagnostic count as a proxy (or cyclomatic if available)
- **Coverage**: fraction from the last test run (0–1)

Files changed >5 times + Coverage < 0.5 = **immediate hotspot**. Cross-reference with test coverage — hotspots without tests are the most likely source of future bugs.

## Error History Mining

Recurring bugs leave commit-message traces (from `[[effective-debugging]]` item 26: use git history):

```bash
# Find files most frequently associated with bug-fix commits
git log --oneline --since="90 days" | grep -iE 'fix:|bug:|error:|crash:|revert' | \
  awk '{print $1}' | xargs -I{} git diff-tree --no-commit-id -r --name-only {} | \
  sort | uniq -c | sort -rn | head -20
```

Files appearing in ≥3 bug-fix commits in 90 days are **recurrence hotspots** — static analysis alone won't catch the next bug there; these need regression tests written against the specific failure class.

Also check if previously fixed bugs have regressed via:
```
mcp__mcp-graph__context (action: "rag", query: "error pattern bug fix")
```

## False Positive Filter

Static analysis produces noise. Apply confidence tiers before triaging to avoid drowning in false alarms:

| Tier | Label | Criteria | Action |
|------|-------|----------|--------|
| A | **Definite** | Crash-reproducible, type error, empty catch with evidence | File as Critical/High node |
| B | **Probable** | High-signal pattern + hotspot overlap, >3 LSP errors in file | File as Medium node; confirm before fixing |
| C | **Possible** | Pattern match only, no hotspot signal, no LSP error | Log to report; skip node creation |

Never create graph nodes for Tier C findings alone — they inflate the bug count without signal. Promote a Tier C to Tier B only when two independent sources (pattern + git history, or pattern + LSP warning) agree.

## Workflow

### Step 1: LSP Diagnostics Collection

Collect all errors first (Tier 1), then warnings (Tier 2). Flag files with ≥3 errors as high-attention targets.

### Step 2: ESLint Deep Scan

```bash
npx eslint src/ --max-warnings 0
```

Focus: security plugin warnings, `no-non-null-assertion`, `no-explicit-any`.

### Step 3: High-Signal Pattern Detection

Run all 8 grep commands from the catalog. Record file + line. Map each hit to a confidence tier.

### Step 4: Dependency & Import Issues

- Circular imports (A → B → A)
- Missing `.js` extensions in ESM imports
- Unused exports (dead code)

```
mcp__mcp-graph__analyze (mode: "cycles")
```

### Step 5: Hotspot Risk Scoring

Compute Risk = Change Frequency × Complexity × (1 − Coverage) for all files. List top 10.

### Step 6: Error History Mining

Run the git log command above. Flag recurrence hotspots (≥3 bug-fix commits in 90 days).

### Step 7: Bug Triage

Classify findings by severity, filtered by confidence tier:

| Severity | Criteria | Action |
|----------|----------|--------|
| **Critical** | Security vulnerability, data loss, Tier A | Fix immediately |
| **High** | Wrong behavior, logic errors, Tier A/B | Fix in current sprint |
| **Medium** | Code smell, Tier B | Schedule for next sprint |
| **Low** | Style, Tier C | Track and batch fix |

Create graph nodes only for Critical and High (Tier A) and confirmed Medium (Tier B):
```
mcp__mcp-graph__node (action: "add", type: "task", tags: ["bug", "<severity>"])
```

### Step 8: Bug Report

Save catalog to knowledge store:
```
mcp__mcp-graph__write_memory
```

## Output Format

```
Bug Hunt Report
===============
Total findings: N (Definite: N | Probable: N | Possible: N)
  Critical: N | High: N | Medium: N | Low: N
Hotspot files: N (Risk score ≥ threshold)
Recurrence hotspots: N (≥3 bug-fix commits in 90d)
New bug nodes created: N (Definite/Probable only)
Top 5 priority fixes:
  1. [Critical/Definite] <description> — <file:line>
  2. [Critical/Definite] <description> — <file:line>
  3. [High/Probable] <description> — <file:line>
  4. [High/Probable] <description> — <file:line>
  5. [Medium/Probable] <description> — <file:line>
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT ignore LSP errors — process Tier 1 before Tier 2; errors before warnings
- Do NOT create nodes for Tier C (Possible) findings — noise > signal
- Do NOT skip error history mining — recurring bugs need regression tests, not just fixes
- Do NOT skip the false-positive filter — inflated bug counts erode trust in the report
- Do NOT treat TODO/FIXME as acceptable — track them as Low-severity nodes
- Do NOT ignore regression hotspots — Risk score predicts future bugs
- Do NOT hunt bugs without running tests first — fix known failures before finding new ones

## Related Skills

- `[[effective-debugging]]` — scientific method, binary search, tool selection by problem type
- `[[pragmatic-programmer]]` — DRY principle, assertive programming, broken window theory
- `$graph-bugs` — structured fix workflow once bugs are found
- `$graph-fix-bugs` — Root Cause Analysis (5 Whys), TDD for bugs

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-bug-investigation

---
name: graph-bug-investigation
description: >-
  Investigação estruturada de bugs com metodologia de causa raiz comprovada (5 Whys,
  Fishbone, Differential Debugging, Scientific Method). Use esta skill SEMPRE que o
  usuário reportar um bug, erro, comportamento inesperado, falha em teste, crash, ou
  qualquer coisa que "não deveria acontecer" — mesmo que o usuário não use a palavra
  "bug" explicitamente. Inclui frases como: "por que está falhando?", "quebrou de
  repente", "não entendo esse erro", "antes funcionava", "o teste está passando mas
  não deveria", "algo está errado com X". Cobre desde erros de runtime até bugs
  lógicos sutis, regressões e comportamentos não-determinísticos. Aplica a
  metodologia certa para o tipo de bug: 5 Whys para bugs lógicos, Bisect para
  regressões, Fishbone para bugs com múltiplas causas possíveis.
---

# Bug Investigator — Causa Raiz Primeiro, Sintoma Depois

Toda investigação termina com uma causa raiz identificada, uma correção no lugar
certo, e um teste que teria detectado o bug.

See also: `[[effective-debugging]]`, `[[pragmatic-programmer]]`

---

## Fase 0 — Triage

| Pergunta | Por quê importa |
|----------|-----------------|
| **O que está acontecendo?** (sintoma, stack trace) | Evita investigar o bug errado |
| **O que deveria acontecer?** | Define critério de sucesso |
| **Quando começou / é reproduzível?** | Separa regressão de bug latente |
| **O que mudou?** (código, config, deps, dados) | Ponto de partida do Differential Debugging |

Se não der para reproduzir → adicione logs e force a reprodução antes de continuar.

---

## Escolha da Metodologia

```
Bug é REGRESSÃO? → Bisect / Differential Debugging  ►  seção A
  NÃO → Múltiplas causas (>3 hipóteses)? → Fishbone  ►  seção B
            NÃO → 5 Whys  ►  seção C
```

Qualquer metodologia pode ser combinada com Scientific Method (seção D).

---

## Seção A — Bisect / Differential Debugging

1. **Confirme o baseline** — última vez que funcionou. Use `git bisect` se necessário.
2. **Compare o diff** — `git diff <bom>..<ruim> -- <arquivo>`
3. **Isole a mudança** — reverta uma mudança de cada vez se o diff for grande.
4. **5 Whys na mudança** — a mudança pode ser sintoma de um problema de design maior.
5. **Escreva o teste de regressão ANTES do fix** (seção F).

**Pergunta-chave:** "Qual mudança mínima, se revertida, faz o bug desaparecer?"

---

## Seção B — Fishbone / Ishikawa

Categorias: CÓDIGO · DADOS · DEPENDÊNCIAS · AMBIENTE · CONCORRÊNCIA · CONFIGURAÇÃO

**Passos:**
1. Liste hipóteses em cada categoria (brainstorm puro).
2. Ordene por probabilidade com base nas evidências.
3. Teste a mais provável de cada categoria antes de descartar as outras.
4. Use Scientific Method (seção D) para validar cada hipótese.

**Regra:** não descarte uma categoria por parecer improvável.

---

## Seção C — 5 Whys

```
SINTOMA → Why 1 → Why 2 → Why 3 → Why 4 → Why 5 → CAUSA RAIZ → AÇÃO
```

**Critérios para parar:** decisão de design / ausência de teste (causa real);
respostas circulares → use Fishbone; fato imutável → a causa raiz é uma camada acima.

---

## Seção D — Scientific Method

```
1. HIPÓTESE:    "O bug é causado por X"
2. PREDIÇÃO:    "Se X, ao fazer Y deveria acontecer Z"
3. EXPERIMENTO: Execute Y isolado (minimal reproduction)
4. OBSERVAÇÃO:  O que realmente aconteceu?
5. CONCLUSÃO:   Confirmado / refutado → próxima hipótese ou fix
```

---

## Seção E — Investigation Budget (30-min Rule)

| Fase | Limite | Se atingir |
|------|--------|-----------|
| Triage + escolha de método | 10 min | Peça mais dados ao usuário |
| Teste de uma hipótese | 30 min | Abandone; registre o que foi eliminado; escolha nova hipótese |
| Investigação total sem progresso | 90 min | Escale: pair debugging, rubber duck (seção G), bisect forçado |

**Regra:** sem evidência em 30 min = hipótese errada ou dados insuficientes.
Abandone e reconstrua o mapa de suspeitos do zero.

> "SELECT isn't broken." — Hunt & Thomas. Quando um bug parece impossível, verifique
> suas suposições sobre o ambiente antes de assumir que a lib está errada.

---

## Seção F — Regression Test First

Quando a causa raiz estiver identificada:

```
1. Escreva o teste → RED (falha pelo motivo correto)
2. Aplique o fix   → GREEN
3. Rode a suite    → sem regressões
```

Um teste escrito ANTES do fix captura o comportamento exato quebrado. Um teste
escrito depois valida a implementação, não o comportamento esperado. `[[effective-debugging]]` Item 42.

---

## Seção G — Rubber Duck (triage estruturado)

Use quando preso por mais de 15 minutos, antes de abrir o debugger.

1. Explique o bug em voz alta como se fosse para alguém que não conhece o código.
2. Descreva cada assunção implícita.
3. Indique o ponto exato onde o real diverge do esperado.

A maioria dos bugs é encontrada na etapa 2. `[[effective-debugging]]` Item 39.

---

## Seção H — Non-Deterministic Bug Playbook

```
ISOLE  → ambiente fixo · seed fixo · clock injetado · sem printf no caminho crítico
MINIMIZE → menor código que ainda manifesta o bug · descarte threads desnecessárias
FORCE  → stress test · chaos injection (sleeps aleatórios) · deterministic replay (rr)
         · ThreadSanitizer (-fsanitize=thread) para races
```

`[[effective-debugging]]` Items 61–63. Bug de concorrência sem teste é bug que volta.

---

## Seção I — Elimination Checklist

Antes de assumir que o bug está onde parece:

- [ ] Acontece sem cache? (limpe e reinicie)
- [ ] Acontece com dados frescos? (recrie fixtures)
- [ ] Acontece num branch limpo? (descarte mudanças não relacionadas)
- [ ] Acontece no ambiente mínimo? (reproduza fora do framework)
- [ ] Versão da lib/runtime é a esperada? (`node --version`, `pip show`)
- [ ] Variáveis de ambiente corretas? (`.env` pode ter valor antigo)
- [ ] Comportamento consistente entre runs? (se não → seção H)
- [ ] Você leu a mensagem de erro completa, incluindo o stack trace inteiro?

---

## Fase de Correção

1. Corrija na causa raiz, não no sintoma.
2. Escreva o teste primeiro (seção F).
3. Busque manifestações similares pelo padrão, não pelo sintoma.

---

## Anti-padrões

- Correção esperançosa — mudar algo sem hipótese e ver se funciona
- Symptom patching — `try/catch` em torno do erro sem investigar
- Cargo cult debug — copiar Stack Overflow sem entender se se aplica
- Viés de confirmação — testar apenas hipóteses que confirmam o que já acredita
- Fix sem teste — corrigir sem garantir que o bug não volta
- Shotgun debugging — mudanças aleatórias até algo funcionar

---

## Formato de saída

```
## Triage
Sintoma / Esperado / Reproduzível / Contexto de mudança

## Investigação ([metodologia])
[5 Whys / Fishbone / Bisect aplicado]

## Causa Raiz
[Uma frase: "O bug existe porque X, que acontece quando Y"]

## Correção
[Mudança exata no código]

## Verificação
[Teste que valida o fix + resultado]

## Prevenção
[O que mudamos para não ocorrer de novo]
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-bugs

---
name: graph-bugs
description: Bug discovery + structured fix — LSP, patterns, hotspots → reproduce, 5-Whys, TDD, regression prevention
trigger: /graph-bugs
tools_used: [insights, check, start, done, memory, node, search]
tokens: ~800
---
<!-- shared:pipeline,dod,principles,errors -->

# graph-bugs

Automated bug discovery + structured fix. Two modes: **hunt** (find) and **fix** (correct).

See also: `[[effective-debugging]]`

## When
- **Hunt:** before VALIDATE, code review, or periodically in LISTENING
- **Fix:** reported bug, failing test, post-deploy regression
- `$graph-bugs` or "find bugs", "fix bug", "debug"

## Flow — Hunt
```
LSP diagnostics → ESLint deep → pattern detection → circular deps → regression hotspots → error catalog → triage → agf node add → agf memory write
```

## Flow — Fix
```
select bug → agf start → reproduce (RED) → 5 Whys → impact → fix (GREEN) → regression → verify AC → prevent → agf done
```

## Steps — Bug Hunt

### 1. LSP Diagnostics
`agf insights` — warnings/errors from active language servers.

### 2. ESLint Deep Scan
`npx eslint . --max-warnings 0` — categorize by rule (security, quality, convention).

### 3. Anti-Pattern Detection
Look for: non-null `!`, `any`, empty catch, magic numbers (>3 uses), `console.error` in prod, `setTimeout` without cleanup.

### 4. Bug Category Patterns

Eight categories with detection patterns — match the category before starting to fix:

| Category | Grep / AST Signal | Tool |
|---|---|---|
| **Null dereference** | `!\.`, optional chain missing, `as T` cast | ESLint `@typescript-eslint/no-non-null-assertion` |
| **Async / race** | `await` inside loops, unguarded concurrent writes, missing `useEffect` cleanup | ESLint `no-await-in-loop`, TSan (runtime) |
| **Error swallowing** | empty `catch {}`, `.catch(() => {})`, unhandled Promise | ESLint `no-empty`, `no-floating-promises` |
| **Stale closure** | captured variables in callbacks that change, missing deps array | ESLint `react-hooks/exhaustive-deps` |
| **Type coercion** | `==` instead of `===`, implicit `any`, implicit `toString` | ESLint `eqeqeq`, `@typescript-eslint/no-explicit-any` |
| **Resource leak** | missing `finally`, `clearTimeout` absent, stream not closed | Static: grep `setTimeout` without paired `clear` |
| **Off-by-one** | `<` vs `<=` in loops/slices, fence-post in array access | Manual review + boundary unit tests |
| **Config / env** | hardcoded values, `process.env.X` without fallback or validation | Grep for bare `process.env`, secret scanner |

When a pattern match fires, classify the bug by category before opening the fix. Category determines test type (see `[[graph-fix-bugs]]` regression matrix).

### 5. Hotspot Priority Algorithm

Rank discovered bugs by risk score before triaging:

```
Risk = Change Frequency × Cyclomatic Complexity × (1 − Test Coverage)
```

- **Change frequency**: commits touching the file in the last 30d (`git log --since="30 days ago" -- <file> | wc -l`)
- **Cyclomatic complexity**: from ESLint `complexity` rule or `npx ts-complexity`
- **Test coverage**: from vitest/jest coverage report (0.0–1.0 scale; invert: low coverage = high risk)

Score ≥ 6 → critical triage. Score 3–5 → high. Score < 3 → medium/low.

`agf insights` exposes change frequency and hotspot files directly.

### 6. Circular Dependencies
`agf insights` — circular module deps.

### 7. Regression Hotspots
`agf insights` — high-churn files (30d). Correlate with closed bugs.

### 8. Error Catalog Mining
`agf search "<error pattern>"` — recurring error patterns in knowledge store.

### 9. Triage
Classify: severity (critical/high/medium/low), confidence, category (from Bug Category Patterns above), location. `agf node add` (type task, tag bug).

---

## Steps — Bug Fix

### 1. Select Bug
Pick from graph (status backlog, type task, tag bug). Highest risk score first.

### 2. Start Task
`agf start` — pull next, follow pipeline.

### 3. Reproduce (RED)
Write a test that reproduces the bug. Must FAIL. `npx vitest run <test-file>`.

### 4. Root Cause (5 Whys)
Ask "why" 5× from the symptom. Each why must be **verified with evidence** before moving to the next. Document root cause in node description.

### 5. Impact / Blast Radius
`agf insights` — what else breaks if touched here?

### 6. Fix (GREEN)
Minimal fix. Test passes. No extra features.

### 7. Regression Suite
`npx vitest run --changed` — module tests + bug-covering tests.

### 8. Verify AC
`agf check <id>`. No AC → `agf node update <id>` to add it.

### 9. Prevention
`agf memory write <name>` — root cause + fix pattern + bug category to prevent recurrence.

### 10. Finish Task
`agf done <id>` — DoD checks.

## Exit — Hunt
- [ ] Bugs triaged as graph nodes with category label
- [ ] Hotspot risk scores documented
- [ ] Report (severity + confidence + category) saved

## Exit — Fix
- [ ] RED confirms bug → GREEN confirms fix
- [ ] Root cause documented (verified 5 Whys)
- [ ] Regression suite passes
- [ ] Prevention pattern saved via `agf memory write`
- [ ] DoD passes

Loop: fix done → `agf done <id>` → next: graph-validate.

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-catalyst

---
name: graph-catalyst
description: Motor de orquestração matemática MAPE-K — lê estado completo do projeto, aplica matriz de decisão (Little's Law + TOC + RAG calibration + Cynefin) e delega para a skill certa do ciclo ($graph-brainstorm → $graph-prd → $graph-analyze → … → $graph-listening). Meta-skill de entrada de sessão com acoplamento theta-gamma.
triggers:
  - graph-catalyst
version: 1.1.0
author: Diego Nogueira
date: 2026-06-20
category: lifecycle
phase: ORCHESTRATION
phases: []
toolchain:
  - agf stats
  - agf insights
  - agf gaps
  - agf savings
  - agf metrics
  - agf calibrate
  - agf heal
  - agf query
  - agf kanban
  - agf memory write
  - agf learning
---

# graph-catalyst

Meta-skill de orquestração baseada em MAPE-K (Monitor → Analyze → Plan → Execute). Lê o estado completo do projeto com scan theta (lento, abrangente), aplica a matriz de decisão matemática e delega o ciclo gamma (rápido, local) para a skill certa. **Zero código escrito aqui** — o catalyst decide, delega e mede.

**Acoplamento theta-gamma (metáfora biofísica):**
- **Theta** (~4-8Hz, longo alcance): MAPE-K scan — visão global, detecção de padrão, decisão estratégica
- **Gamma** (~30-80Hz, local): execução de skill — implementação, TDD, gate, done

## When to Use

- Início de qualquer sessão nova (entrada principal antes de qualquer trabalho)
- Backlog estagnado: não sabe por onde continuar
- Economia degradada: `agf savings` mostra taxa < 30%
- Pós-LISTENING: ciclo completo e pronto para o próximo
- `$graph-mega-brain` delegou para calibração e orquestração de entrada

**Não usar quando:**
- Já está no meio de uma task (`in_progress` ativo) — vá direto para a skill da fase atual
- Tem um objetivo específico e claro — use a skill de fase diretamente

## MAPE-K Loop

One full cycle per session — M → A → P → E → K:

| Phase | Action | Output |
|-------|--------|--------|
| **Monitor** | `agf stats` + `agf gaps` + `agf kanban` | wip, gaps, savings_rate, blocked |
| **Analyze** | Bottleneck, WIP violations, economy, graph health | Which condition fires |
| **Plan** | Decision matrix — first matching condition wins | `CATALYST DECISION` block |
| **Execute** | Delegate to selected skill; never implement directly | Skill runs its own flow |
| **Knowledge** | Capture 3 metrics → `agf learning` + session memory | Spiral tightens each cycle |

K grows each cycle: routing accuracy improves, RAG thresholds tighten, graph noise decreases (`[[kanban-in-action]]` — CFD slope should rise session over session).

## Mandatory Flow

```
[THETA] agf stats → agf savings → agf gaps → agf query → agf insights → agf heal
→ [DECISION MATRIX] → delegate to skill
→ [GAMMA] skill executa → agf done/submit
→ [CLOSE] agf calibrate? → agf memory write → agf savings → agf learning
```

## Steps

### Passo 1 — Monitor (scan theta completo)

```bash
agf stats                              # snapshot total: nodes, edges, byStatus
agf savings                            # economy: tokens poupados, taxa de reuso
agf gaps --severity required --json    # blockers: gaps required não fechados
agf query --status in_progress         # WIP: tasks ativas (deve ser ≤ 1)
agf query --type requirement --status backlog  # candidatos brainstorm pendentes
agf query --status blocked             # tasks travadas por dependências
agf kanban                             # flow: cycle time, throughput, WIP por fase
```

Capture: `wip_count` (in_progress nodes) · `required_gaps` · `savings_rate` · `brainstorm_ready` · `blocked_count`.

### Passo 2 — Analyze (diagnóstico de sistema)

```bash
agf insights bottlenecks               # gargalo: onde o fluxo para?
agf insights wip                       # violação de WIP limit?
agf insights phases                    # distribuição por fase SHAPE→BUILD→SHIP
agf metrics --economy-report           # custo real vs baseline
agf heal                               # dry-run: quantos nós precisam cura?
```

Identifique: fase dominante · gargalo primário · savings_rate / hit rate · heal issues count.

### Passo 3 — Plan (matriz de decisão)

**Composite score** (compute before evaluating conditions):
```
score = (wip_count × 40) + (required_gaps × 30) + (100 - savings_rate) × 0.3
```
Weights: WIP is the strongest lever (Little's Law `[[kanban-in-action]]`), required gaps are hard blockers, economy signal is secondary.

**Delegation confidence threshold: ≥ 70%.** If two conditions nearly tie, trigger circuit breaker (see below).

Aplique as condições **em ordem de prioridade** — a primeira que bater define a ação:

| Prioridade | Condição | Ação |
|-----------|----------|------|
| 1 | `wip_count > 0` | **Completa o WIP** — retorne à skill da fase atual; Little's Law: CT=WIP/TH |
| 2 | `required_gaps > 0` | **`agf heal --apply`** → feche os gaps → reavalie |
| 3 | `savings_rate < 30%` | **`agf calibrate`** → ajuste threshold RAG → continue |
| 4 | `brainstorm_ready ≥ 4` | **`$graph-prd`** — candidatos suficientes, evite overproduction (Lean) |
| 5 | `backlog vazio` AND `sem PRD` | **`$graph-brainstorm`** → **`$graph-prd`** |
| 6 | fase = ANALYZE, PRD importado | **`$graph-analyze`** |
| 7 | fase = DESIGN, DoR aprovado | **`$graph-design`** |
| 8 | fase = PLAN, design aprovado | **`$graph-plan`** |
| 9 | fase = IMPLEMENT, tasks `ready` | **`$graph-implement`** |
| 10 | todas tasks `done`, gate pendente | **`agf gate <fase>`** → skill da próxima fase |
| 11 | pós-LISTENING | avalie feedback → **`$graph-brainstorm`** ou **`$graph-prd`** (novo ciclo) |

**Calibração Cynefin da decisão:**
- Domínio **óbvio** → execute a skill diretamente, sem hesitação
- Domínio **complicado** → revise contexto com `agf context <id>` antes de delegar
- Domínio **complexo** → prefira `$graph-brainstorm` mesmo com backlog parcial (mais divergência)
- Domínio **caótico** → `$graph-implement` diretamente no problema mais urgente (`--priority 1`)

---

## Circuit Breaker Conditions

Stop and ask the user (do not auto-delegate) when **any** of these fires:

1. `wip_count > 1` AND `blocked_count > 0` — deadlock risk; human must prioritize or cancel
2. `required_gaps > 3` — graph structurally broken; auto-heal may cascade
3. Two phase conditions tie (same phase, multiple triggers) — ambiguous state

Output: `⚠ CIRCUIT BREAKER — Reason: <X> | Options: <A/B/C> | Waiting for user decision.`

### Passo 4 — Execute (delegação)

Declare a decisão explicitamente antes de delegar:

```
CATALYST DECISION — Condição #<N> | wip=<N> gaps=<N> savings=<N>% score=<N> confidence=<N>%
Skill: $<skill-name> | Rationale: <1 frase>
```

Execute a skill selecionada conforme seu fluxo próprio.

### Passo 5 — Calibração Condicional (pós-execução)

**Só execute se:**
- `savings_rate < 30%` no relatório pré-execução, OU
- `agf heal` (dry-run no Passo 2) encontrou ≥ 2 issues

```bash
agf calibrate                   # ajusta threshold RAG pelo lever ledger
agf heal --apply                # fecha os nós com problemas detectados
agf gaps                        # re-verifica: gaps fechados?
```

### Passo 6 — Memória de Sessão

```bash
agf memory write catalyst-session-$(date +%Y%m%d) --content \
  "Phase: <fase> | Condition: <#N> | Delegated: <skill> | wip=<N> gaps=<N> savings=<N>% | Outcome: <done/blocked>"
```

### Passo 7 — Learning Spiral (fecha o loop)

```bash
agf savings                     # economy delta desta sessão
agf metrics --economy-report    # counterfactual: o que teria custado sem otimizações?
agf learning stats              # performance por agente + routing
agf insights summary            # fluxo geral: DORA + WIP + bottlenecks
```

After each delegation cycle, capture three metrics via `agf learning` to tighten the decision matrix over time (`[[swe-at-google]]` — Sustainability as First-Class Concern):

| Metric | What it improves |
|--------|-----------------|
| Routing accuracy (skill completed without backtrack?) | Condition priority order |
| Economy delta (`agf savings` after − before) | RAG threshold via `agf calibrate` |
| Graph health delta (`agf heal` count after − before) | Heal trigger sensitivity |

## Output Format

```
CATALYST SCAN — <data>
Monitor:    nodes=<N> | in_progress=<N> | blocked=<N> | phase=<PHASE>
Economy:    savings=<N>% | hit_rate=<N>% | gaps_required=<N> | heal=<N>
Score:      composite=<N> | confidence=<N>% | bottleneck=<column>
Decision:   Condition #<N> → $<skill-name> | <rationale>
Post-exec:  calibrate=<y/n> | heal=<y/n> | routing_delta=<+/-N%>
Next:       <next action or skill>
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- **NÃO pular o scan theta** — tomar decisão sem Monitor = OODA sem Observe; custo: skill errada, retrabalho
- **NÃO abrir nova task com WIP ativo** — Little's Law garante que CT sobe linearmente com WIP (`[[kanban-in-action]]`)
- **NÃO usar catalyst no meio de uma implementação** — ele é entry point de sessão, não interruptor de contexto
- **NÃO ignorar `required_gaps`** — gaps required são blockers que invalidam qualquer DoD downstream
- **NÃO calibrar toda sessão** — calibre apenas quando savings_rate < 30% ou heal > 2 issues
- **NÃO substituir a skill de fase** — catalyst decide e delega; nunca implementa diretamente
- **NÃO auto-delegar quando confidence < 70%** — acionar circuit breaker e consultar o usuário
- **NÃO ignorar os 3 circuit breaker conditions** — eles existem para evitar cascata de erros no grafo

## Related Skills

- `[[kanban-in-action]]` — Little's Law, WIP limits, CFD interpretation
- `[[swe-at-google]]` — Sustainability, policy vs. rules, automation at scale
- $graph-brainstorm — `agf skill show graph-brainstorm` (condition #5: backlog vazio)
- $graph-mega-brain — `agf skill show graph-mega-brain` (alternativa para drive autônomo end-to-end)
- $graph-prd — `agf skill show graph-prd` (condition #4 e #5)
- $graph-analyze — `agf skill show graph-analyze` (condition #6)
- $graph-implement — `agf skill show graph-implement` (condition #9)

## Constraints

- CLI-first: tudo via `agf` — zero MCP
- O catalyst **nunca escreve código** — ele decide, delega e mede
- WIP=1 é inviolável: se `wip_count > 0`, Condition #1 sempre vence
- Decisão = primeira condição que bate (prioridade de cima para baixo)
- Delegation confidence threshold: **≥ 70%** — abaixo disso, circuit breaker
- Learning spiral obrigatório ao fim de cada sessão (steps 6-7)
- Se nenhum `.ts` mudar → sem node de grafo obrigatório (skills são artefatos de conteúdo)
- Se qualquer `.ts` mudar durante execução delegada → `agf node add` → TDD → `agf done` (inviolável)

---

## graph-cloud-flow-deploy

---
name: graph-cloud-flow-deploy
description: >-
  Faz o deploy do projeto graph-cloud-flow (graph-flow.cloud) no servidor de produção
  em deploy@13.140.162.224. Use sempre que o usuário quiser "deployar", "publicar",
  "subir para produção", "fazer deploy", "atualizar o site", "push para o servidor",
  "publicar as mudanças" — mesmo que não diga "graph-cloud-flow" ou "skill" explicitamente.
  Cobre o pipeline completo: testes → build → rsync → build remoto → pm2 restart → verificação.
  Também cobre diagnóstico e correção de problemas de SSH, PM2, e build remoto.
---

# Deploy — graph-cloud-flow (graph-flow.cloud)

Pipeline completo de deploy do site Next.js 14 para o servidor de produção.

## Info do servidor

| Campo     | Valor                              |
|-----------|-------------------------------------|
| Host      | `deploy@13.140.162.224`             |
| Diretório | `/var/www/graph-cloud-flow`         |
| Processo  | `graph-flow` (PM2, id 6)            |
| Porta     | `8830`                              |
| SSH alias | `graph-cloud-flow-prod` (ver abaixo)|

## Passo 0 — Verificar conectividade SSH

Antes de qualquer coisa, teste a conexão:

```bash
ssh -o ConnectTimeout=8 -o BatchMode=yes deploy@13.140.162.224 echo "ok" 2>&1
```

**Se retornar `Permission denied (publickey)` → siga o bloco de diagnóstico SSH abaixo.**

Se retornar `ok` → pule direto para o Passo 1.

---

### Diagnóstico e correção de SSH

O `~/.ssh/config` não tem entrada para este servidor. Tente as chaves disponíveis uma a uma:

```bash
for KEY in ~/.ssh/id_ed25519 ~/.ssh/zydron ~/.ssh/copadomundo_ed25519; do
  echo -n "Testando $KEY: "
  ssh -i "$KEY" -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no \
    deploy@13.140.162.224 echo "ok" 2>&1
done
```

Quando encontrar a chave que retorna `ok`, adicione-a ao `~/.ssh/config` para uso automático:

```bash
cat >> ~/.ssh/config << 'EOF'

Host graph-cloud-flow-prod
    HostName 13.140.162.224
    User deploy
    IdentityFile ~/.ssh/<CHAVE_QUE_FUNCIONOU>
    IdentitiesOnly yes
    ServerAliveInterval 30
EOF
```

Substitua `<CHAVE_QUE_FUNCIONOU>` pela chave que retornou `ok`. **A chave atual confirmada é `~/.ssh/copadomundo_ed25519`** (já está em `~/.ssh/config`). Reconfirme:

```bash
ssh graph-cloud-flow-prod echo "conectado"
```

---

## Passo 1 — Rodar os testes de acessibilidade

Aborte o deploy se qualquer teste falhar.

```bash
cd /Users/diegonogueira/projects/graph-cloud-flow && npm run test:a11y
```

## Passo 2 — Build local de validação

Garante que TypeScript e Next.js estão limpos antes de enviar.

```bash
npm run build
```

## Passo 3 — Sincronizar arquivos com o servidor

```bash
rsync -avz --exclude='node_modules' --exclude='.next' --exclude='.git' \
  /Users/diegonogueira/projects/graph-cloud-flow/ \
  graph-cloud-flow-prod:/var/www/graph-cloud-flow/
```

> Se o alias SSH ainda não estiver configurado, use `deploy@13.140.162.224` no lugar de `graph-cloud-flow-prod` e adicione `-i ~/.ssh/<chave>` antes do endereço no rsync: `rsync -avz -e "ssh -i ~/.ssh/<chave>" ...`

## Passo 4 — Build remoto + restart PM2

```bash
ssh graph-cloud-flow-prod "
  cd /var/www/graph-cloud-flow &&
  npm ci &&
  npm run build &&
  pm2 restart graph-flow
"
```

## Passo 5 — Verificar saúde pós-deploy

```bash
ssh graph-cloud-flow-prod "pm2 status graph-cloud-flow && curl -s -o /dev/null -w '%{http_code}' http://localhost:8830/"
```

Esperado: processo `online` + HTTP `200`.

## Passo 6 — Smoke test em produção

```bash
curl -I https://graph-flow.cloud/ 2>&1 | head -5
```

---

## Fluxo feliz (resumo)

```bash
cd /Users/diegonogueira/projects/graph-cloud-flow

# 1. testes
npm run test:a11y

# 2. build local
npm run build

# 3. sync
rsync -avz --exclude='node_modules' --exclude='.next' --exclude='.git' \
  ./ graph-cloud-flow-prod:/var/www/graph-cloud-flow/

# 4. build + restart remoto
ssh graph-cloud-flow-prod "cd /var/www/graph-cloud-flow && npm ci && npm run build && pm2 restart graph-flow"

# 5. verificar
ssh graph-cloud-flow-prod "pm2 status graph-cloud-flow && curl -s -o /dev/null -w '%{http_code}' http://localhost:8830/"
```

---

## Troubleshooting

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| `Permission denied (publickey)` | Chave SSH não configurada | Seguir Passo 0 acima |
| `rsync: connection unexpectedly closed` | SSH falhou antes do rsync | Testar SSH primeiro |
| `npm run build` falha no servidor | Dependências desatualizadas | Rodar `npm ci` antes |
| `pm2: Process or Namespace not found` | Processo não existe | `ssh graph-cloud-flow-prod "cd /var/www/graph-cloud-flow && npm ci && npm run build && pm2 start npm --name graph-flow -- run start -- -p 8830"` |
| HTTP 502/503 após restart | Build levou mais tempo | Aguardar 10s e testar de novo |
| `Error: Cannot find module '.next'` | Build não rodou no servidor | Garantir que `npm run build` rodou após o rsync |

## Economy

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-cobol-to-java

---
name: graph-cobol-to-java
description: Deterministic COBOL + Adabas → Java 17 + Oracle conversion using the Universal IR pipeline. Use whenever converting mainframe COBOL/CICS programs (online or batch) to Java 17+ with Oracle DDL. Covers: COBOL parsing, Adabas DML detection, FNR-to-table mapping, COPYBOOK resolution, Java record emission, Oracle DDL generation, and javac validation.
triggers:
  - graph-cobol-to-java
  - cobol-to-java
  - converter cobol para java
  - migrar mainframe
  - migrar COBOL
  - adabas para oracle
version: 1.0.0
author: Diego Nogueira
date: 2026-06-15
---

# graph-cobol-to-java

Convert COBOL + Adabas programs to Java 17 + Oracle using a deterministic pipeline (Knuth-Bendix confluence). Zero AI, zero randomness. Input: COBOL source + YAML config. Output: Java record + Oracle DDL.

## When to Use

- Migrating mainframe CICS COBOL programs to Java 17+
- Converting Adabas DML (FIND, READ, STORE, UPDATE, DELETE) to Oracle SQL
- Any COBOL online/batch program targeted for Java + Oracle
- The `_lifecycle.phase` is ANALYZE or DESIGN for a migration project

## Pipeline

```
COBOL source (.cbl / raw)
       │
       ▼
  CobolParser        → Universal IR (MainframeIRWithCursors)
       │               with data fields, procedures, cursors, ADABAS blocks
       │
       ├─── JavaEmitter          → .java (Java 17 record, br.com.correios.*)
       │                           91 fields, 94 methods, mainFlow()
       │
       └─── OracleDdlEmitter     → schema-oracle.sql (CREATE TABLE + INDEX)
                                   from fileMappings config
       │
       ▼
  JavaBuildValidator   → javac --release 17 (skips if JDK absent)
```

## Supported COBOL Constructs

| COBOL Construct | Java Equivalent |
|-----------------|-----------------|
| `MOVE A TO B` | `b = a;` (with type coercion) |
| `PERFORM para` | `para();` |
| `PERFORM VARYING...UNTIL` | `for (int i = from; i <= to; i++)` |
| `IF ... ELSE ... END-IF` | `if (...) { ... } else { ... }` |
| `EVALUATE ... WHEN` | `switch (...) { case ... }` |
| `INSPECT ... TALLYING` | `String.count()/replace()` |
| `INSPECT ... REPLACING` | `String.replace()` |
| `ADD / SUBTRACT / COMPUTE` | `+=` / `-=` / `=` |
| `CALL 'PROG' USING ...` | `progService.prog(...);` (stub if no source) |
| `EXEC CICS ADDRESS CWA/TWA` | `context = runtimeEnv.getCwa()/getTwa()` |
| `EXEC CICS LINK PROGRAM` | `programService.link("PROG", commarea)` |
| `EXEC CICS RETURN` | `return` (end of mainFlow) |
| `EXEC CICS ASSIGN ABCODE` | `String abendCode = runtimeEnv.getAbendCode()` |
| `EXEC SQL / EXEC ADABAS` | `PreparedStatement` + `ResultSet` (cursor-based) |
| ADABAS S1/S4 → cursor | `DECLARE CURSOR + OPEN` |
| ADABAS L1/L3 → FETCH | `SELECT * WHERE ISN = :pk` |
| ADABAS N1/N2 → INSERT | `INSERT INTO` |
| ADABAS A1/A4 → UPDATE | `UPDATE ... WHERE` |
| ADABAS E1/E4 → DELETE | `DELETE FROM ... WHERE` |
| ADABAS ET/BT → COMMIT/ROLLBACK | `conn.commit()` / `conn.rollback()` |

## Step-by-Step Conversion

### Step 1: ANALYZE — Understand the source

Read the COBOL source and identify:
- **PROGRAM-ID**: becomes Java class name
- **ADABAS CALLs**: which FNRs are accessed, what commands (S1, L1, N1, etc.)
- **CICS commands**: LINK, ADDRESS, RETURN, ASSIGN
- **Paragraphs**: become `private void` methods
- **COPYBOOKs**: data structures (WORKING-STORAGE, LINKAGE)

```bash
# Analyze construct frequency
grep -c "CALL 'ADABAS'" osb_/SER02220
grep -c "PERFORM" osb_/SER02220
grep -c "EXEC CICS" osb_/SER02220
```

### Step 2: DESIGN — Create YAML config

Create a config file mapping Adabas FNRs to Oracle tables:

```yaml
name: my-project
target: java-oracle

oracle:
  schema: MYSCHEMA
  tableCase: upper
  columnCase: upper

java:
  package: br.com.correios.myproject
  dtoStyle: record

adabasFiles:
  isnColumn: ISN
  isnType: NUMBER(10)

fileMappings:
  - fileNumber: 57
    adabasTable: A-0057SAB02
    oracleTable: MY_TABLE
    columnPrefix: ''
    columns:
      - name: FIELD-NAME
        picture: X(010)
        oracleType: VARCHAR2(10)
```

Key considerations for config:
- `fileNumber` must match the FNR in `MOVE +N TO WBD-FNR`
- `oracleTable` must be ≤30 chars (Oracle limit)
- `isMultiValue: true` → generates separate child table for MU/PE
- `superdescriptors` → generates `CREATE INDEX` for each

### Step 3: IMPLEMENT — Run conversion

**Single file:**
```typescript
import { convert } from './src/orchestrator.js';

const result = await convert('osb_/SER02220', {
  target: 'java-oracle',
  configPath: 'configs/osb-hc99.yaml',
  sourceLanguage: 'cobol',
});

console.log(result.artifacts['SER02220.java']);
console.log(result.artifacts['schema-oracle.sql']);
```

**Or via CLI script:**
```bash
npx tsx scripts/convert-osb-to-java-oracle.ts
```

### Step 4: VALIDATE — Check output

```bash
# Validate Java compiles (requires JDK 17+)
javac --release 17 osb_/java-oracle-output/SER02220.java

# Run pipeline tests
npx vitest tests/language-conversion/java/orchestratorJavaOracle.test.ts

# Check for TODOs/UNHANDLED
grep -i "TODO\|UNHANDLED" osb_/java-oracle-output/SER02220.java
```

### Step 5: Configure new scenarios

To convert a different COBOL program:

1. **Create config**: Copy `configs/osb-hc99.yaml` → `configs/my-project.yaml`
2. **Map FNRs**: Update `fileMappings` with the new program's Adabas files
3. **Set package**: Update `java.package` for the new project
4. **Place sources**: Copy COBOL + COPYBOOKs to the input directory
5. **Run**: Use the `convert()` function or modify the CLI script
6. **Iterate**: For each unsupported construct, extend the parser (see below)

## Extending the Parser

If a COBOL construct is not recognized, it appears as `UnparsedConstruct` in the IR. To add support:

1. **Add regex** in `src/parsers/cobol/procedure-parser.ts` (e.g., new `CONSTANT`)
2. **Add statement type** in `src/ir/schema.ts` if needed
3. **Add emitter** in `src/emitter/java-statement-emitter.ts`
4. **Add test** in `tests/language-conversion/java/`
5. **Run**: `npx vitest` — if tests pass, construct is now covered

## Known Patterns for Common Scenarios

### Online CICS program (like SER02220)
- `EXEC CICS ADDRESS CWA/TWA` → DI context injection
- `EXEC CICS LINK PROGRAM` → service call
- `EXEC CICS RETURN` → method return
- Copybooks for WCA, TWA, CWA → flattened record fields

### Batch program
- No CICS commands → simpler Java class
- FILE SECTION + OPEN/READ/WRITE/CLOSE → JDBC PreparedStatements
- JCL DD statements → Oracle connection config

### Natural → Java (intermediate COBOL)
- If the source is Natural, first convert Natural → COBOL
- Then COBOL → Java using this skill
- See `docs/natural-to-cobol-migration.md` for Natural→COBOL steps

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `[WARNING] config: Using default config` | Use absolute path for `configPath` |
| `No ADABAS file mappings found` | `fileMappings` may be empty — check config YAML |
| `Java build: N error(s) found` | Run `javac` manually to see compilation errors |
| `Success: false` with no errors | JDK not available — set `validate: false` or install JDK 17+ |
| Hyphenated field names in errors | COBOL `WS-CONT` not yet mapped to Java `wsCont` — known limitation |
| `TODO: stubbed` in Java output | External CALL with no available source (e.g., fonetizacao) |
| esbuild Transform error | May be a syntax error in TypeScript source — check for extra braces |

## Determinism Guarantee

The pipeline is 100% deterministic:
- Same COBOL source + same config → identical Java + identical DDL every run
- Verified by `golden-t0-java.test.ts` (double-run byte-equality)
- No AI/LLM, no random, no date-dependent output
- Based on Knuth-Bendix confluence (confluent rewriting system)

## Reference

- Pipeline docs: `docs/cobol-to-java-migration.md`
- Example config: `configs/osb-hc99.yaml`
- Example output: `osb_/java-oracle-output/`
- Test fixtures: `tests/fixtures/corpus/OSB/`
- Conversion script: `scripts/convert-osb-to-java-oracle.ts`
- mcp-graph RAG: `reference/adabas-direct-call-commands`, `reference/adabas-format-search-buffer-syntax`

## Economy

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-dependency

---
name: graph-dependency
description: Dependency management audit using SBOM generation, license compliance, supply chain security, and freshness scoring
triggers:
  - graph-dependency
version: 2.0.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-dependency

Dependency management audit using SBOM generation, license compliance, supply chain security, and freshness scoring. Identifies vulnerabilities, license risks, outdated packages, and supply chain attack vectors across all project dependencies.

> Cross-references: [[swe-at-google]] ch21 (Dependency Management), ch18 (Build Systems); [[humble-continuous-delivery]] ch14 (Advanced Version Control)

## When to Use

- Before DEPLOY phase
- Monthly maintenance cycles
- When adding new dependencies
- During security reviews
- After npm audit findings

## Mandatory Flow

```
npm audit → license scan → one-version check → diamond detection → freshness check → SBOM generation → supply chain analysis → upgrade plan → report → write_memory
```

## Workflow

### Step 1: Dependency Audit

Run `npm audit --json` for full vulnerability report. Categorize by severity (critical/high/medium/low). Check both production and dev dependencies. Flag critical/high CVEs as DEPLOY blockers.

- Count vulnerabilities by severity: critical, high, moderate, low
- Separate findings into production vs dev dependencies
- Check for `npm audit fix` auto-fixable issues vs manual resolution
- Compare with previous audit memory to identify new vs recurring CVEs

### Step 2: One-Version Rule Check

**SWE@Google principle**: enforce exactly one version of every third-party dependency across the project. Multiple versions of the same package create hidden diamond conflicts and inflate bundle size.

```bash
# Find packages with multiple installed versions
npm ls --json --all 2>/dev/null | node -e "
  const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const seen={};
  function walk(deps,name){
    if(!deps) return;
    Object.entries(deps).forEach(([k,v])=>{
      seen[k]=seen[k]||new Set();
      seen[k].add(v.version);
      walk(v.dependencies,k);
    });
  }
  walk(d.dependencies);
  Object.entries(seen).filter(([k,v])=>v.size>1)
    .forEach(([k,v])=>console.log(k+': '+[...v].join(', ')));
"
```

Flag each duplicate version as a **One-Version Violation**. Target state: zero violations.

### Step 3: Diamond Dependency Detection

**Diamond problem**: `app → libA@1.x` and `app → libB@2.x` both depend on `libbase` at incompatible versions. Types and APIs passed across version boundaries break silently.

```bash
# Detect diamond conflicts: packages with 2+ versions in the tree
npm ls --json --all 2>/dev/null | node -e "
  const data = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const versions = {};
  function collect(deps) {
    if (!deps) return;
    for (const [name, info] of Object.entries(deps)) {
      if (!versions[name]) versions[name] = [];
      versions[name].push(info.version);
      collect(info.dependencies);
    }
  }
  collect(data.dependencies);
  Object.entries(versions)
    .filter(([,v]) => new Set(v).size > 1)
    .forEach(([name, v]) => console.log('DIAMOND:', name, [...new Set(v)].join(' vs ')));
"
```

For each diamond: identify which consumers pin the conflicting versions and assess resolution path (upgrade one, dedup, or replace).

### Step 4: License Compliance

Check all dependency licenses via `npm ls --json`. Flag incompatible licenses.

- Allowlist: MIT, ISC, BSD-2-Clause, BSD-3-Clause, Apache-2.0, 0BSD, CC0-1.0
- Denylist (in MIT project): GPL-2.0-only, GPL-3.0-only, AGPL-3.0, SSPL-1.0
- Flag unknown licenses: `UNLICENSED`, `SEE LICENSE IN`, missing license field

### Step 5: Freshness Scoring

Each major version behind represents months of accumulated unpatched CVEs, community drift, and API churn. Freshness is a security signal, not just a hygiene score.

Run `npm outdated --json` and score each production dependency:

| State | Score | Security Implication |
|-------|-------|---------------------|
| Latest installed | 100 | Baseline |
| 1 minor behind | 80 | Minor CVE exposure window |
| 2+ minor behind | 60 | Moderate unpatched surface |
| 1 major behind | 50 | ~6–12 months CVE lag |
| 2+ major behind | 20 | 1+ year unpatched, likely breaking API |
| No release in 12+ months | 0 | Unmaintained — supply chain risk |

Calculate average freshness. List bottom 10 as priority update targets.

### Step 6: SBOM Generation

Generate Software Bill of Materials in CycloneDX format (NIST/CISA mandated for supply chain transparency). Pin all deps with cryptographic hashes — the build must fail if a downloaded artifact doesn't match.

```bash
npm sbom --sbom-format cyclonedx > sbom.json
```

Verify SBOM completeness: total components must match `npm ls --all` count. Validate `package-lock.json` integrity hashes are present for every dependency.

### Step 7: Supply Chain Analysis

- Check for typosquatting: 1–2 char differences from popular package names
- Check for dependency confusion: internal package names must not collide with public npm
- Flag packages with <100 weekly downloads or single maintainer (bus factor = 1)
- Check for recent ownership transfers in the last 6 months
- Verify no `extraneous` or `missing` packages in `npm ls` output

### Step 8: Upgrade Automation Checklist

**SWE@Google principle**: upgrades that are not automated simply do not happen. Manual upgrade policies accumulate as compounding debt.

- [ ] Automated PRs: Dependabot or Renovate configured to open upgrade PRs
- [ ] Test gate: CI must pass before any automated PR can merge
- [ ] Rollback plan: `package-lock.json` committed and pinned — one revert recovers the prior state
- [ ] Pin after update: use exact versions (`"1.2.3"`) not ranges (`"^1.2.3"`) for critical deps
- [ ] Changelog review: automate fetching changelogs (Renovate release notes) — do not skip reading breaking changes

### Step 9: Dependency Report

Score 0-100 (audit 30%, licenses 20%, freshness 25%, supply chain 25%). Save via `mcp__mcp-graph__write_memory`.

**Grading:**
- **A (90-100):** Zero critical/high CVEs, all licenses compliant, freshness > 80%, zero One-Version violations
- **B (75-89):** No critical CVEs, minor license issues, freshness > 65%, ≤2 diamond conflicts
- **C (60-74):** Some high CVEs with fix available, freshness > 50%, One-Version violations present
- **D (45-59):** Critical CVEs, license violations, freshness < 50%, diamond conflicts unresolved
- **F (< 45):** Multiple critical CVEs unfixed, GPL blockers, widespread outdated deps, active supply chain risks

## Output Format

```
Phase: DEPENDENCY AUDIT
Vulnerabilities: <N> critical, <N> high, <N> moderate, <N> low
One-Version Violations: <N> packages with duplicate versions
Diamond Conflicts: <N> detected
License Issues: <N> incompatible, <N> unknown
Average Freshness: <N>%
SBOM: generated (<N> components, hashes verified)
Supply Chain Risks: <N> findings
Upgrade Automation: <N>/5 checks passing
Overall Grade: <A-F>
Recommendations: <top 3 actions>

Saved to memory: "Dependency Audit — <date>"
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT add dependencies without checking license compatibility — one GPL dep can relicense your project
- Do NOT use version ranges (`^`, `~`, `1.+`) for critical deps — breaks reproducibility and rollbacks
- Do NOT skip One-Version checks — silent type mismatches from diamond conflicts surface at runtime, not build time
- Do NOT rely on SemVer patch-safety guarantees at scale — Hyrum's Law means patch changes break observable behavior
- Do NOT delay security updates — critical CVEs need immediate action
- Do NOT import a dependency without a clear owner and update plan — it becomes unmaintained infrastructure

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-deploy

---
name: graph-deploy
description: DEPLOY phase — DORA release health, deploy gate (7 checks), CI pipeline, post-release validation
trigger: /graph-deploy
tools_used: [agf forecast, agf gate deploy, agf snapshot create, agf export]
tokens: ~500
---
<!-- shared:phases,gates,principles,errors,harness -->

# graph-deploy

CI pipeline, release validation, DORA health, post-release verification — all via `agf`.

See also: `[[humble-continuous-delivery]]`, `[[kanban-in-action]]`

## When
- After HANDOFF (PR + docs ready)
- CI green → release
- `_lifecycle.phase === DEPLOY`

## Flow
```
agf forecast → agf gate deploy → [CI/merge] → agf snapshot create → agf gate deploy → agf phase
```

## Steps

### 1. DORA Release Health
`agf forecast` — deploy frequency, lead time, change fail rate, MTTR.

**4-Tier DORA Benchmarks** (State of DevOps):

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deploy Frequency | Multiple/day | Weekly–monthly | Monthly–6 months | < 6 months |
| Lead Time for Changes | < 1 hour | 1 day–1 week | 1 week–1 month | > 6 months |
| Change Failure Rate | 0–15% | 0–15% | 16–30% | 16–30% |
| MTTR | < 1 hour | < 1 day | 1 day–1 week | > 6 months |

If MTTR or CFR is in Medium/Low → block release and fix pipeline health first.

### 2. Release Gate
`agf gate deploy` — 5 required + 2 recommended:

**Required:** CI passed · PR merged · all tests green · snapshot created · all tasks done  
**Recommended:** harness ≥ 70 · no open critical bugs

### 3. Deploy Gate Failure Priority

When `agf gate deploy` fails, fix in this order:

1. **CI failures** (lint, typecheck, build) — nothing else matters until green
2. **Test failures** (unit, integration) — a red test is a stopped pipeline
3. **Snapshot missing** — run `agf snapshot create` before proceeding
4. **Open tasks** — close or move to next cycle via `agf task update`
5. **Harness < 70** — add missing tests or update harness config; do not lower threshold

Never ship with a harness score below 70. If harness is the only failing check,
pause release and spend one cycle raising coverage. `[[humble-continuous-delivery]]` ch07.

### 4. CI Pipeline
Monitor: lint → typecheck → unit → integration → build. Fail → fix → re-run.

**Build time rule** (Humble): if any stage exceeds 10 minutes, developers stop running
it locally — defeating CI. Keep commit stage under 10 min total.

### 5. Merge & Deploy
PR merge → deploy. Post-deploy: run smoke tests immediately (see section below).

### 6. Post-Release Snapshot
`agf snapshot create` — capture post-release baseline.

### 7. Deploy Ready Gate (final)
`agf gate deploy` — all 7 checks must pass. Harness ≥ 70 is mandatory.

---

## Smoke Test Checklist (agf CLI+MCP)

Run these 5 checks immediately after every deploy. If any fails → rollback (see below).

- [ ] `agf status` exits 0 and reports the correct phase
- [ ] MCP server responds to a basic tool call (ping or list)
- [ ] At least one task can be created, read, and deleted end-to-end
- [ ] `agf gate deploy` passes all required checks on the deployed snapshot
- [ ] Logs contain no ERROR-level entries in the first 60 seconds post-start

`[[humble-continuous-delivery]]` ch05: "Smoke-test every deployment immediately."

---

## Rollback vs Roll-Forward Decision

| Condition | Rollback | Roll-Forward |
|-----------|----------|-------------|
| Smoke test failure within 5 min of deploy | ✓ Always rollback | — |
| Data migration already ran | — | ✓ Must roll forward (migration is irreversible) |
| Bug is small, reproducible, fixable in < 30 min | — | ✓ Roll forward; faster and safer |
| Unknown blast radius / production impact unclear | ✓ Rollback first, investigate | — |
| Previous version known to be stable | ✓ Rollback to it | — |
| No previous stable snapshot available | — | ✓ Must roll forward |

**Default rule:** When in doubt, roll back. A known-good state beats an unknown state.
The cost of an extra deploy is always lower than the cost of extended downtime.

`[[humble-continuous-delivery]]` ch10: "Never bypass the pipeline for emergency fixes."

---

## CFD Anomaly Detection

Read the Cumulative Flow Diagram from `agf metrics` / kanban export to catch flow
problems before they become release blockers. `[[kanban-in-action]]` ch11.

| Shape you see | Diagnosis | Action |
|---|---|---|
| **Inbox band growing** (top band widens right) | Downstream bottleneck — work arrives faster than it completes | Apply Theory of Constraints: find the slowest column and subordinate all others to it |
| **Middle band fat / plateau** (In Progress or Review band stays wide) | WIP too high or items blocked mid-flow | Enforce WIP limit; swarm on blockers; stop starting, start finishing |
| **Done band slope flattening** (throughput dropping) | Release pipeline friction or quality gate failures accumulating | Check gate failures, test health, and deploy frequency |

**Key measurement:** lead time = horizontal gap between task creation and Done.
If lead time is growing week-over-week → WIP is too high. Reduce WIP before
raising throughput targets.

---

## Exit
- [ ] CI green (lint + typecheck + tests + build)
- [ ] PR merged, release deployed
- [ ] Smoke tests passed (all 5)
- [ ] `agf gate deploy` all checks pass
- [ ] `agf phase`

Loop: deployed → next: graph-listening.

## Economy
Run `agf savings` / `agf metrics --economy-report` after each task, then feed
savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-design

---
name: graph-design
description: Execute the DESIGN phase of the lifecycle via the `agf` CLI — ADRs, architecture decisions, contract coverage, Code Intelligence impact analysis
triggers:
  - graph-design
version: 2.1.0
author: Diego Nogueira
date: 2026-04-04
---

# graph-design

Execute the DESIGN phase of the lifecycle, driving the `agf` CLI (zero MCP). Defines architecture, creates ADRs, establishes technical design, and validates contract coverage before planning.

## When to Use

- After ANALYZE phase is complete (PRD imported, requirements defined)
- Making architectural decisions for a new feature
- Documenting technical choices (ADRs)
- The current phase reported by `agf phase` is `DESIGN`

## Mandatory Flow

```
agf context <id> → agf node add (decision) → agf edge add → agf insights → agf gate design → agf phase plan
```

## ADR Trigger Criteria

Write an ADR when **any one** of the following is true:

| Condition | Example |
|-----------|---------|
| Decision affects ≥ 2 components | Changing the auth strategy touches API, DB, and frontend |
| Decision is reversible-costly | Migrating databases, switching runtimes |
| Decision affects a public interface | New API shape, event schema, CLI flag |
| Decision has rejected alternatives | Chose REST over GraphQL after evaluation |
| Decision was disputed during design | Team debated two options — record the winner and why |

**No ADR needed:** internal implementation detail within a single module, naming, or formatting choices.

## Contract Coverage Requirements

Every public interface must be "covered" before the design gate passes:

| Interface type | Coverage = |
|----------------|-----------|
| REST/GraphQL endpoint | OpenAPI/schema definition + ≥1 contract test |
| Event / message | Schema (JSON Schema or Avro) + consumer test |
| CLI command | `--help` spec + integration test |
| Exported function/class | TypeScript types + unit tests for boundary conditions |
| Database schema | Migration file + at least one query test |

An interface without a schema is undocumented; without a contract test it is unverified. Both are required to count as covered.

## Design Reviewability Test (20-Min Rule)

Before submitting an ADR or design doc for review, apply this test from `[[swe-at-google]]` ch9:

> "Can a senior engineer who did not attend the design session understand the decision and its trade-offs in ≤ 20 minutes?"

If no, the design is not ready. Ask three questions:

1. **Is the problem stated without jargon?** — A reader with no prior context should understand what problem is being solved.
2. **Are the alternatives documented?** — At minimum, one alternative and why it was rejected.
3. **Are the consequences actionable?** — Follow-up tasks, risks accepted, and trade-offs stated explicitly.

## Architecture Anti-Patterns Checklist

Check for these five patterns during design review:

| Anti-pattern | Signal | Fix |
|---|---|---|
| **Distributed monolith** | Services deployed independently but share a DB or call each other synchronously for every request | Decouple via events or API contracts; each service owns its data |
| **God service** | One service owns all business logic; others are thin adapters | Split by bounded context (DDD); re-assign responsibilities |
| **Chatty interface** | N calls per user action instead of 1 aggregate | Introduce aggregate endpoints or BFF pattern |
| **Leaky abstraction** | Callers must know internal details of a component to use it | Strengthen the contract; hide implementation behind a clean interface |
| **Premature generalization** | Generic framework built for requirements that don't exist yet | Apply YAGNI (`[[pragmatic-programmer]]`); design for current scope, extend when pressure is real |

## Workflow

### Step 1: Load Context

```bash
agf context <epic or requirement id>
agf search "<architecture keywords>"
```

Review requirements, constraints, and risks from ANALYZE phase.

### Step 2: Impact Analysis (for existing codebases)

If modifying existing modules, run Code Intelligence first:
```bash
agf insights
```

**Blast radius scope:** `agf insights` traverses the dependency graph starting from the changed component. Capture:
- Direct callers and importers (depth 1)
- Tests that exercise the changed component (affected test count)
- Shared data schemas or events referenced downstream

This gives a blast radius estimate: low (<5 modules), medium (5-20), high (>20). High blast radius → require additional ADR and a migration plan before proceeding.

### Step 3: Create ADR Decision Nodes

For each significant architectural choice (see ADR Trigger Criteria above):
```bash
agf node add --type decision
```

**ADR Format for description:**
```markdown
## Status: Accepted
## Context: [Why this decision is needed]
## Decision: [What was decided and how]
## Consequences: [Trade-offs, follow-up work, risks accepted]
```

**Common decisions:** Technology stack, data storage, API design, communication patterns, error handling, testing strategy, deployment model.

### Step 4: Link Decisions

```bash
agf edge add <from> <to> --type <rel>
```

Edge types: `decision → requirement`, `decision → epic`, `decision → risk`, `decision → decision`.

### Step 5: Interface Design

Define contracts between components. Document as constraint nodes:
```bash
agf node add --type constraint
```

Apply Contract Coverage Requirements above to each constraint node.

### Step 6: Save Architectural Decisions

```bash
agf memory write <name>
```

Record key architectural choices for future retrieval.

### Step 7: Validate ADRs

```bash
agf insights
```

Apply the Design Reviewability Test to each ADR. Verify Architecture Anti-Patterns Checklist.

### Step 8: Validate Contract Coverage

```bash
agf insights
```

Verify interface/contract completeness across components using Contract Coverage Requirements table.

### Step 9: Validate Design Gate

```bash
agf gate design
```

**Gate criteria:**
- Key architectural decisions documented as ADR nodes (ADR Trigger Criteria met)
- Decisions linked to requirements they address
- No orphan requirements without design coverage
- Interface contracts defined with schema + contract test
- Blast radius estimated for all high-impact changes

If validation fails, add missing ADRs or edges.

### Step 10: Transition

Once gate passes:
```bash
agf phase plan
```

Follow the next-action hint printed by the `agf` CLI for the recommended next command.

## Output Format

```
Phase: DESIGN → PLAN
ADRs: N decision nodes created
Contracts: M interface constraints defined (schema + test)
Impact: K existing modules analyzed | blast_radius=<low|medium|high>
Coverage: J/T requirements addressed by decisions
Gate: design_ready — score N/100, grade X
Status: Ready to proceed to PLAN phase
```

## Anti-Patterns

- Do NOT create implementation tasks during DESIGN — that happens in PLAN
- Do NOT write code — design is documentation and decision-making only
- Do NOT skip ADRs — undocumented decisions lead to inconsistency
- Do NOT over-design — focus on decisions that affect MVP scope (YAGNI)
- Do NOT ignore the next-action hint from the `agf` CLI — it guides the optimal next command
- Do NOT use deprecated forms — use `agf node add` to create nodes
- Do NOT skip Code Intelligence on existing codebases — impact analysis prevents surprises
- Do NOT mark an interface as "covered" without both a schema and a contract test

## Related Skills

- `[[swe-at-google]]` — Design Reviewability Test (ch9), code as liability
- `[[pragmatic-programmer]]` — YAGNI, Orthogonality, Design by Contract

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

## Economy

Token economy is part of the loop: run `agf savings` / `agf metrics --economy-report` after each task, then feed savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-docs

---
name: graph-docs
description: Documentation health audit using JSDoc completeness, README freshness, example code validation, CLAUDE.md convention coverage, API documentation, and architecture doc generation from graph
triggers:
  - graph-docs
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-docs

Documentation health audit using JSDoc completeness, README freshness, example code validation, CLAUDE.md convention coverage, API documentation, and architecture doc generation from graph. Identifies documentation gaps, stale content, and drift between docs and code.

## When to Use

- Before HANDOFF phase, to ensure documentation is complete
- During quarterly doc reviews
- When onboarding new developers
- When CLAUDE.md needs updating after significant changes
- During LISTENING phase for documentation improvements

## Mandatory Flow

```
CLAUDE.md audit --> README check --> JSDoc coverage --> API docs --> example validation --> architecture docs --> changelog --> report --> write_memory
```

## Living Documentation Principles

From [[pragmatic-programmer]] (Ch8 — Pragmatic Projects):

1. **Code is the truth; docs lie when they diverge.** If a doc cannot be generated from code, it will rot. Prefer active generators (scripts that extract API shapes, types, routes) over hand-written prose that describes what the code does.

2. **DRY applied to knowledge.** A business rule described in a README and also in a JSDoc comment and also in a test description is three representations of one fact. Collapse them: the JSDoc is authoritative, the README links to it, the test name reflects it.

3. **If you can't run it, you can't trust it.** Every code example in docs must be executable and verified on CI. A broken example is worse than no example — it signals "nobody checks this."

## DRY Docs Checklist

Generate (from code) — do NOT hand-write these:

- [ ] API endpoint list → generate from route definitions (e.g., `ts-morph` scan of `src/api/routes/`)
- [ ] MCP tool descriptions → generate from `server.tool()` registrations
- [ ] Type reference → generate from exported TypeScript types via `typedoc`
- [ ] CLI flag table → generate from the CLI parser schema
- [ ] Changelog → generate from conventional commits via `release-please` or `conventional-changelog`

Hand-write (cannot be derived from code):

- [ ] Architecture narrative — the "why" behind module boundaries
- [ ] Onboarding walkthrough — first-run sequence, mental model
- [ ] Decision log (ADRs) — rationale for non-obvious choices
- [ ] Gotchas and known limitations — tribal knowledge that tests don't encode

## Comment Quality Rubric

Comments explain WHY, not WHAT. The code already says what it does.

| Quality | Example | Verdict |
|---------|---------|---------|
| Explains intent | `// Skip deleted nodes — soft-delete tombstones must not appear in graph exports` | GOOD |
| Documents invariant | `// Cache must never exceed maxSize — OOM risk in long-running daemon` | GOOD |
| Flags known debt | `// TODO(#412): replace linear scan with indexed lookup once nodes >10K` | GOOD |
| Restates the code | `// Increment counter by 1` next to `counter++` | BAD — delete it |
| Describes the obvious | `// Return the result` | BAD — delete it |

**Five-second test**: cover the comment and read the code. If you already understand it, delete the comment.

## Freshness Signal

A doc is stale when:

1. Any source file it references has a `git log` date newer than the doc's own `git log` date.
2. A type, function, or module name it mentions no longer exists in the codebase.
3. A command it lists exits non-zero when run.
4. Its last commit message is >90 days old and the referenced code has changed since.

**Staleness check (bash)**:
```bash
# Find docs older than their referenced source files
git log --follow -1 --format="%ci" -- docs/architecture/STORE.md
git log --follow -1 --format="%ci" -- src/store/index.ts
# If store/index.ts is newer → flag STORE.md as stale
```

Flag threshold: doc is stale if source is >14 days newer.

## Workflow

### Step 1: CLAUDE.md Audit

Verify CLAUDE.md covers all critical conventions:
- ESM imports (`.js` extension), Zod v4, strict mode, naming conventions
- Logger usage, testing rules, path-specific rules

Compare CLAUDE.md sections with actual codebase patterns using `mcp__mcp-graph__analyze(mode:"doc_completeness")`. Flag: outdated conventions, missing new patterns.

### Step 2: README Freshness

Run `npm install` + `npm run dev`, `npm test`, `npm run build` to verify commands work. Apply **Freshness Signal** to the README itself. Flag broken commands, outdated screenshots, missing sections.

### Step 3: JSDoc Coverage

```
JSDoc coverage = functions with JSDoc / total exported functions
```

Apply **Comment Quality Rubric** to sampled comments. Flag: WHY-less comments and restating-the-code comments.

### Step 4: API Documentation

Apply **DRY Docs Checklist** — verify that API docs are generated, not hand-maintained. For MCP tools: verify each tool has description in `server.tool()`. Cross-reference with `docs/reference/`.

### Step 5: Example Code Validation

For each code example in `docs/` and README: verify syntax, verify referenced modules exist, verify output matches current behavior. Apply the **Living Documentation Principles** rule: if it can't be run, flag it.

### Step 6: Architecture Documentation

Generate/verify architecture docs from graph via `mcp__mcp-graph__export(action:"mermaid")`. Apply **Freshness Signal** — compare doc commit dates against referenced module dates.

### Step 7: Changelog Completeness

Verify CHANGELOG.md covers recent releases. Cross-reference with git tags. Check every `feat:`/`fix:` commit has a changelog entry. Apply **DRY Docs Checklist** — changelog should be generated, not hand-written.

### Step 8: Documentation Report

```
CLAUDE.md coverage: <N>%
README freshness: <days since last update>
JSDoc coverage: <N>%
API doc coverage: <N>%
Example validity: <N>%
Architecture drift items: <N>
Stale docs flagged: <N>
Changelog completeness: <N>%
Top 5 gaps: <list>
Overall grade: <A-F>
```

**Grading:**
- **A (90-100):** All docs current, JSDoc > 80%, no stale examples, no drift
- **B (75-89):** Minor gaps, JSDoc > 60%, few stale examples
- **C (60-74):** CLAUDE.md outdated, JSDoc < 60%, some broken examples
- **D (45-59):** Significant gaps, many undocumented APIs, architecture drift
- **F (< 45):** Critical doc debt, broken README, no JSDoc, stale architecture

Save findings:
```
Tool: mcp__mcp-graph__write_memory
Params:
  title: "Documentation Audit — <date>"
  content: "<findings summary with coverage scores, gaps, recommendations>"
  tags: ["documentation", "audit", "jsdoc", "architecture"]
```

## Output Format

```
Phase: DOCUMENTATION AUDIT
CLAUDE.md coverage: <N>%
README freshness: <N> days
JSDoc coverage: <N>%
API doc coverage: <N>%
Example validity: <N>%
Architecture drift: <N> items
Stale docs flagged: <N>
Changelog completeness: <N>%
Top 5 gaps: <list>
Overall grade: <A-F>

Saved to memory: "Documentation Audit — <date>"
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT treat docs as afterthought — write alongside code
- Do NOT let CLAUDE.md go stale — it's the AI pair programmer's primary context
- Do NOT skip JSDoc on public functions — they're the API contract
- Do NOT leave broken examples — they mislead developers
- Do NOT document what doesn't exist yet — document what IS
- Do NOT write docs without testing commands — broken setup instructions are worse than none
- Do NOT hand-write what can be generated — generated docs can't drift from code
- Do NOT write WHAT comments — explain WHY or delete the comment

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-fix-bugs

---
name: graph-fix-bugs
description: Structured bug fix workflow using Root Cause Analysis (5 Whys), Reproduce-Fix-Verify cycle, TDD for bugs, and regression prevention
triggers:
  - graph-fix-bugs
version: 2.0.0
author: Diego Nogueira
date: 2026-06-21
---
> 💡 **v11 CLI surface available** (`@mcp-graph-workflow/cli@beta`): lifecycle verbs (`start_task`, `finish_task`, `next`, `update_status`, `list`, `add_node`, `set_phase`) have faster slash/shell equivalents. Prefer `/start` over `mcp__mcp-graph__start_task` when possible.

# graph-fix-bugs

Structured bug fix workflow using Root Cause Analysis (5 Whys), Reproduce-Fix-Verify cycle, TDD for bugs, and regression prevention. Every bug fix follows a disciplined process that prevents recurrence.

See also: `[[effective-debugging]]`, `[[feathers-legacy-code]]`

## When to Use

- When a bug is identified (from graph-bug-hunter, user report, or test failure)
- During IMPLEMENT phase for bug-fix tasks
- When a regression is detected after a deployment or merge

## Mandatory Flow

```
select bug → start_task → reproduce (RED) → 5 Whys → impact analysis → fix (GREEN) → regression suite → verify → prevent → finish_task → write_memory
```

## Workflow

### Step 1: Bug Selection

```
Tool: mcp__mcp-graph__list (type: "task", tags: ["bug"])
Tool: mcp__mcp-graph__start_task (nodeId: <bug_node_id>)
```

### Step 2: Reproduce (TDD RED)

Write a test that reproduces the bug. The test MUST fail. If it passes, the bug description is wrong or already fixed.

```bash
npx vitest run src/tests/bug-fix-<description>.test.ts
```

### Step 3: Root Cause Analysis (5 Whys with Verification Discipline)

Each "why" must be **falsifiable** — you must be able to verify it before moving to the next. Never assume; confirm.

| Level | Question | Evidence Required |
|-------|----------|-------------------|
| Why 1 | Why does X fail? | Log, error message, or test output |
| Why 2 | Why does Y cause X? | Code path trace or debugger confirmation |
| Why 3 | Why does Z produce Y? | Reproducer that isolates Z alone |
| Why 4 | Why does W trigger Z? | Specific input/state that triggers W |
| Why 5 | What is the root structural cause? | Design/code decision that made this possible |

Rule: if you cannot produce evidence for a "why", it is a hypothesis — mark it as such and design an experiment to confirm it (see `[[effective-debugging]]` — Scientific Method, Item 1).

Document the verified chain in the bug node description.

### Step 4: Impact Analysis

```
Tool: mcp__mcp-graph__code_intelligence (action: "impact", symbol: "<affected_module>", depth: 3)
```

Determine: how many modules depend on the buggy code, whether the fix will break callers, and whether the same pattern exists at other call sites.

### Step 5: Fix Implementation (TDD GREEN)

Write the minimal fix to make the failing test pass.

- Do NOT refactor during fix — keep the change as small as possible
- Do NOT add features — fix only the bug
- Do NOT change unrelated code — minimize the diff

```bash
npx vitest run src/tests/bug-fix-<description>.test.ts
```

### Step 6: Regression Suite

```bash
npm test
```

Zero regressions allowed. If any test breaks, the fix is too broad — narrow it down.

### Step 7: Fix Verification Criteria

"Tests pass" is necessary but not sufficient. Verify all four:

1. **Similar paths** — Are there other code paths that exercise the same logic? Check them manually or with targeted tests.
2. **Edge cases** — What happens at boundaries (empty, null, max, concurrent)? The bug's root cause often implies more than one vulnerable input.
3. **Related code review** — Does the blast radius analysis reveal other modules with the same pattern? Fix the class of bug, not just the instance (effective-debugging Item 21).
4. **AC validation** — Confirm the original user-reported behavior is resolved.

```
Tool: mcp__mcp-graph__validate (action: "ac", nodeId: <bug_node_id>)
```

### Step 8: TDD Bug Fix Cycle (Complete)

```
1. Write failing test  →  npx vitest run <bug-test>   # RED confirmed
2. Make minimal fix
3. Run bug test        →  npx vitest run <bug-test>   # GREEN confirmed
4. Run full suite      →  npm test                    # No regressions
5. Verify AC           →  agf check <id>
6. Add test to CI      →  test file committed with fix
```

The test must be committed alongside the fix so the CI pipeline catches any future regression.

### Step 9: Regression Prevention Matrix

| Bug Category | Test Type to Add | Coverage Target |
|---|---|---|
| Logic error (wrong condition, off-by-one) | Unit test with boundary inputs | 100% branch for that function |
| Timing / async (race condition, stale state) | Integration test with concurrency probe | At least one concurrent execution scenario |
| Configuration / environment | Smoke test with config variations | All required env vars validated at startup |
| Data shape (null, missing field, wrong type) | Unit test with null/empty/malformed inputs | Each shape variant tested |
| Integration contract (API changed, schema drift) | Integration test against real contract | Contract snapshot in CI |
| UI state (wrong render, stale prop) | Component test asserting state transitions | Full user interaction sequence |

### Step 10: Prevention & Close

Document the bug pattern:

```
Tool: mcp__mcp-graph__write_memory
```

Include: root cause (5 Whys chain), symptoms, fix approach, prevention strategy.

```
Tool: mcp__mcp-graph__finish_task (nodeId: <bug_node_id>, rationale: "<root cause + fix summary>", testFiles: ["src/tests/bug-fix-<name>.test.ts"])
```

## Output Format

```
Bug Fix Report
==============
Bug: <title> (<node_id>)
Root cause: <1-line summary from verified 5 Whys>
Blast radius: N modules affected
Fix: <files changed>, <lines changed>
Tests: N new + M existing passing
Edge cases covered: <list>
Prevention: Pattern documented in knowledge store
DoD: Grade <A/B/C/D> (score: N/100)
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT fix without reproducing first — write the failing test before touching production code
- Do NOT skip evidence at each Why level — unverified Whys are guesses, not root causes
- Do NOT fix multiple bugs in one commit — one bug, one fix, one commit
- Do NOT refactor during bug fix — separate commits for fix and refactor
- Do NOT skip 5 Whys — surface-level fixes recur within weeks
- Do NOT ignore blast radius — fixes can introduce new bugs in dependent modules
- Do NOT skip regression suite — run ALL tests, not just the bug test
- Do NOT close without documenting prevention — the team needs to learn from every bug

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-handoff

---
name: graph-handoff
description: Execute the HANDOFF phase of the lifecycle via the `agf` CLI — PR creation, memory capture, knowledge export, doc completeness validation
triggers:
  - graph-handoff
version: 2.1.0
author: Diego Nogueira
date: 2026-04-04
toolchain:
  - agf memory write
  - agf snapshot create
  - agf export
  - agf gate
  - agf phase
---

# graph-handoff

Execute the HANDOFF phase of the lifecycle, driven entirely by the `agf` CLI (ZERO MCP). Creates PRs, captures technical decisions as memories, shares knowledge, and finalizes documentation for delivery.

## When to Use

- After REVIEW phase has approved the changes
- Creating a PR for the sprint's work
- Capturing decisions and knowledge for future cycles
- The current phase reported by `agf phase` is `HANDOFF`

## Memory Capture Criteria

Not every note deserves a memory. Capture entries that fall into one of three categories:

| Category | Trigger | Examples |
|----------|---------|---------|
| **Decisions** | Architectural or design choice with trade-offs | "Used polling instead of WebSocket because the infra doesn't support long-lived connections" |
| **Non-obvious constraints** | Undocumented limitation that will bite the next cycle | "Auth token TTL is 15 min — never cache it longer than 10 min in the client" |
| **Lessons learned** | Anything you had to discover empirically that should be documented | "Vitest mock.resetModules() must be called before each test or module state bleeds" |

Memories that do not fit any category are noise — skip them. Run `agf memory write <name>` only for qualifying entries.

## PR Quality Checklist (5 Items)

From `[[swe-at-google]]` ch9: a PR must be understandable to someone who was not in the room.

Before `gh pr create`, verify:

- [ ] **Description** — what changed and why, in plain language (not a list of file names)
- [ ] **Context** — link to the task/epic node IDs and the problem being solved
- [ ] **Testing notes** — what was tested, how, and what the results were (include key test output or coverage delta)
- [ ] **Rollback plan** — how to revert if the deploy goes wrong (migration rollback, feature flag off, previous image tag)
- [ ] **Affected systems** — list every service, API contract, or config file touched by this change

PRs that fail any item should be revised before creating — reviewers cannot add context they don't have.

## Required Docs for Handoff

All items must be Y before `agf gate handoff` runs:

| Doc | Required? | How to satisfy |
|-----|-----------|----------------|
| `CLAUDE.md` updated | Y | Add any new conventions, toolchain changes, or env vars introduced this sprint |
| API docs updated | Y if public API changed | Update OpenAPI spec or inline JSDoc; N/A otherwise |
| ADR created | Y if an architectural decision was made | `agf memory write` alone is insufficient — ADR captures rationale persistently |
| Changelog entry | Y | One line per user-visible change; format: `[type] short description` |
| `AGENTS.md` updated | Y if new agent or workflow constraint added | N/A otherwise |

## Mandatory Flow

```
agf memory write <name> → agf snapshot create → agf export → agf export (knowledge) → [create PR] → agf gate handoff → agf phase DEPLOY
```

## Workflow

### Step 1: Capture Technical Decisions

```bash
agf memory write <name>
```

Only capture entries meeting the Memory Capture Criteria above. Memories land under `workflow-graph/memories/`.

### Step 2: Create Snapshot

```bash
agf snapshot create
```

Audit trail for the graph state at handoff.

### Step 3: Export Deliverables

```bash
agf export
agf export --format mermaid
```

Generate PR body content and visual graph overview.

### Step 4: Share Knowledge with Team

```bash
agf export
```

Creates a knowledge package (memory + docs, deduplicated by content hash).

### Step 5: Prepare Commit

```bash
git status
git diff --staged
git log --oneline -5
```

Commit follows project conventions. No force-push; no `--no-verify`.

### Step 6: Create Pull Request

Apply the PR Quality Checklist (5 items) before running:

```bash
gh pr create --title "<PR title>" --body "$(cat <<'EOF'
## Summary
<what changed and why>

## Tasks completed
<node IDs and titles>

## Testing notes
<what was tested, key results, coverage delta>

## Rollback plan
<how to revert>

## Affected systems
<services, APIs, config files>

## Graph
<mermaid output from agf export --format mermaid>
EOF
)"
```

### Step 7: Update Required Docs

Work through the Required Docs for Handoff table. CLAUDE.md, ADR, changelog, AGENTS.md — all applicable items must be Y.

### Step 8: Validate Gate

```bash
agf gate handoff
```

Gate criteria: all sprint tasks done, snapshot created, knowledge exported, memories captured, PR created, required docs updated.

### Step 9: Transition

```bash
agf phase DEPLOY
```

## Final Handoff Gate (5-Item Checklist)

All five must be green before HANDOFF is complete:

- [ ] `agf gate handoff` exits with score ≥ 80/100
- [ ] PR created and passes the 5-item PR Quality Checklist
- [ ] All memory entries match one of the three capture categories (no noise)
- [ ] Required Docs table has no outstanding Y items
- [ ] `agf phase DEPLOY` accepted (phase transition confirmed)

If any item is red, resolve it and re-run `agf gate handoff` before declaring HANDOFF done. See `[[kanban-in-action]]`: work is not done until it has moved through every stage — blocked items are still WIP.

## Output Format

```
Phase: HANDOFF → DEPLOY
PR: #N (url)
Snapshot: created
Memories: N decisions captured (category breakdown)
Knowledge: M docs exported
Docs: CLAUDE.md ✓ | API docs ✓/N/A | ADR ✓/N/A | Changelog ✓ | AGENTS.md ✓/N/A
Gate: handoff_ready — score N/100, grade X
Status: Ready to proceed to DEPLOY phase
```

## Anti-Patterns

- Do NOT capture every note as a memory — only decisions, constraints, and lessons
- Do NOT skip `agf memory write` for qualifying entries — rediscovery is expensive
- Do NOT create PRs without the 5-item checklist satisfied
- Do NOT skip snapshots — they are the audit trail
- Do NOT forget CLAUDE.md and changelog — they are always required
- Do NOT skip `agf export` — enables cross-project learning
- Do NOT ignore `nextAction` from `agf phase`

## Cross-References

- `[[swe-at-google]]` ch9 (Code Review) — PR quality, description standards, LGTM model
- `[[kanban-in-action]]` — done means through every stage, WIP and flow discipline

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

## Economy

Token economy is part of the loop: run `agf savings` / `agf metrics --economy-report` after each task, then feed savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-implement

---
name: graph-implement
description: IMPLEMENT phase — TDD Red-Green-Refactor, task pipeline, 9 DoD checks, epic promotion
trigger: /graph-implement
tools_used: [start, done, node status, check, context, brief, submit]
tokens: ~600
---
<!-- shared:phases,gates,dod,pipeline,principles,errors -->
<!-- cross-ref: [[goos-tdd]] [[khorikov-unit-testing]] -->

# graph-implement

Core coding phase. TDD mandatory. Every line traced via `agf`.

## When
- After PLAN (tasks decomposed, sprints planned)
- `_lifecycle.phase === IMPLEMENT`
- User says "next task", "implement", "start coding"

## Flow
```
agf start → [TDD Outer Loop → Inner Loop] → agf done <id>
```

---

## Steps

### 1. Start Task
`agf start` = `agf next` + `agf context <id>` + `agf node status <id> in_progress`. Returns task + context + ragContext + tddHints. Blocked → see Blocker Decision Tree below.

### 2. Pre-Checks
`agf check <id>` (TDD adherence) · `agf insights` (stale refs / code sync).

### 3. TDD — Two-Loop Model

Every feature lives inside two nested loops [[goos-tdd ch01, ch04]]:

**Outer loop (acceptance)** — opens first, closes last:
- Write one failing acceptance test in domain language (no infrastructure names in the test body).
- This test defines "done" for the task. It stays red until the full behavior is delivered.
- Use when the task is a user-facing behavior, API contract, or integration path (see Walking Skeleton below).

**Inner loop (unit)** — runs many times inside the outer loop:
- **RED** `< 5 min`: Write one failing unit test from AC + tddHints. Name it as a behavior sentence.
- **GREEN** `< 15 min`: Minimal implementation to pass. No gold-plating.
- **REFACTOR** `< 10 min`: Clean up. Tests stay green. No regressions. Extract value types, remove duplication.
- Repeat until the acceptance test passes.

**Which loop to start with?**

| Situation | Start here |
|---|---|
| New feature / new integration path | Acceptance test (outer loop) first |
| Known algorithm / pure logic / utility | Unit test (inner loop) directly |
| Bug fix | Failing regression test (unit) first |
| Brownfield: cannot run end-to-end yet | Automate the build → add characterization tests over code you must change → then refactor |

Test pain = design signal. If writing the test is hard, stop and diagnose [[goos-tdd ch20]]:
- Can't inject a dependency → extract an interface
- Constructor takes 5+ args → bundle correlated args into a named type
- Must run the whole system → missing port/adapter seam
- Hard to construct test data → use Test Data Builder (see below)

### 4. Finish Task
Run `npm run test:blast` first. Then `agf done <id>` — 9 DoD checks → AC validation → `agf node status <id> done` → epic promotion check.

### 5. Delegated Mode (optional)
`agf brief <id>` → executor implements → `agf submit <id> --result <json>` (brief→submit loop closes in one step on valid return).

### 6. Spiral Feedback
After done: `agf savings` / `agf metrics --economy-report` → `agf learning` → calibrate next task.

Concrete metrics to track [[khorikov-unit-testing ch04]]:
- **False positive rate**: tests that went red on correct refactors → fragile tests, over-mocked
- **Cycle durations**: Red/Green/Refactor times per task → slow green = design problem
- **Test pyramid shape**: unit:integration:e2e ratio → should be wide at bottom
- **Blocker recurrence**: same blocker in > 1 task → systemic dependency risk

---

## Walking Skeleton [[goos-tdd ch10]]

Build a Walking Skeleton once per new system or major integration boundary — not per feature.

A skeleton is the thinnest end-to-end slice that compiles, deploys, and exercises one complete path with trivially obvious logic.

**When to build one:**
- Iteration Zero of a new service or subsystem
- First task that crosses a new external boundary (DB, message bus, third-party API)

**How:**
1. Write the acceptance test first in domain language only.
2. Name helpers as if they exist (`FakePaymentGateway`, `AppRunner`) — build them next.
3. Identify minimum components to carry one value end-to-end.
4. Automate: checkout → compile → unit test → integrate → deploy to staging-like env → run acceptance test.
5. Pass with trivially obvious logic; all effort goes to wiring.
6. Document anything NOT truly end-to-end (fake servers, stubbed services) as explicit project risk.
7. Only then: begin feature development under this harness.

If the skeleton takes longer than expected, those delays are risks found early — not a failure.

---

## Test Data Builder [[goos-tdd ch22]]

Use whenever a class has 3+ constructor args or tests repeatedly construct the same type with minor variations.

```ts
// Builder per type, all fields defaulted to valid values
class OrderBuilder {
  private data = { id: 'order-1', amount: 100, status: 'pending' }

  withAmount(amount: number) { return new OrderBuilder({ ...this.data, amount }) }
  withStatus(status: string) { return new OrderBuilder({ ...this.data, status }) }
  but()  { return new OrderBuilder({ ...this.data }) }   // copy constructor
  build(): Order { return new Order(this.data) }
}

const anOrder = () => new OrderBuilder()

// In tests:
const paid = anOrder().withStatus('paid').build()
const refunded = anOrder().withStatus('paid').but().withStatus('refunded').build()
```

**Rules:**
- Static factory with a readable name: `anOrder()`, `aUser()`, `aPayment()`
- `but()` returns a copy — use to produce sibling objects from a shared prototype
- Pass builders through helpers, not built objects — outer code can add its own defaults
- When constructors change: update one builder, not every test

---

## DoD Grade A Criteria [[khorikov-unit-testing ch04, ch06, ch07]]

The 9 DoD checks are the gate. "Grade A" means all of these hold:

**Tests**
- [ ] All tests pass (`npm run test:blast` green)
- [ ] New behavior covered by at least one acceptance test and focused unit tests
- [ ] No test asserts on stubs (only on mocks / return values / state)
- [ ] Test names read as behavior sentences: `"returns empty list when user has no orders"`
- [ ] Preferred style: output-based > state-based > communication-based [[khorikov ch06]]

**Code**
- [ ] Domain logic lives in pure functions or domain objects (Functional Core) — no I/O mixed in
- [ ] Infrastructure calls (DB, HTTP, queues) in adapters only — domain never imports infra packages
- [ ] No class with both business logic and I/O (use Humble Object if found) [[khorikov ch07]]
- [ ] Functions < 50 lines, files < 800 lines, nesting ≤ 4 levels

**Integration**
- [ ] `agf node status <id>` = `done`
- [ ] `testFiles` populated on node
- [ ] Epic promotion checked if all children done

---

## Blocker Decision Tree

```
Blocker found on agf start
│
├─ Can I unblock it now? (missing data, wrong status, dependency not done)
│   ├─ YES → fix it → restart step 1
│   └─ NO
│       ├─ Is there another ready task in the sprint?
│       │   ├─ YES → agf next (pick the other task)
│       │   └─ NO
│       │       ├─ Is the blocker systemic (infra, external team)?
│       │       │   ├─ YES → escalate + park task → agf node status <id> blocked
│       │       │   │         → log in agf learning → move to next sprint
│       │       │   └─ NO → decompose blocker into a new child task
│       │       │             → agf node status <blocker-id> in_progress
│       │       │             → implement blocker task first
│       └─ (after resolution) → return to original task
```

---

## Exit
- [ ] 9 DoD checks pass (Grade A target — see checklist above)
- [ ] `npm run test:blast` passed
- [ ] `testFiles` populated on node
- [ ] Epic promotion checked (if all children done)

Close: `agf submit <id>` (delegated) or `agf check <id>` → `agf done <id>` → next: graph-validate.

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-lead

---
name: graph-lead
description: >-
  Use when the user asks Claude to act as planner/tech-lead over a project graph
  (agent-graph-flow, driven by the `agf` CLI — "o grafo") — reasoning, planning,
  and gate-checking the work while a separate executor agent writes the actual
  code. Trigger for requests (often in Portuguese) to: lead/drive a feature,
  épica or migração through the graph ("lidera/conduz/orquestra pelo grafo");
  write or import a PRD ("faz o PRD"); decompose an epic into atomic
  tasks/subtasks with testable acceptance criteria ("decompõe em tasks com AC");
  build a plan or sprint ("monta o plano"); reconcile the graph — fix statuses,
  missing AC, dedupe ("reconcilia o grafo"); run phase gates (DoD, harness,
  readiness, sprint health) via `agf check`/`agf gate`/`agf harness`; identify
  blockers; or validate/review what the executor produced ("valida/revisa a saída
  do executor"). Also fits "analisa, desenha, planeja — sem escrever código, só
  prepara pro executor." Trigger even if no phase is named or several mix. Do NOT
  trigger when the user wants Claude to write, fix, or commit production code
  itself — that is the executor's lane.
triggers:
  - graph-lead
  - lead-graph
  - orchestrate-graph
version: 2.1.0
author: Diego Nogueira
date: 2026-06-21
phases: [ANALYZE, DESIGN, PLAN, VALIDATE, REVIEW, HANDOFF]
---

# graph-lead

Cadence the agent-graph-flow 9-phase lifecycle from the **Claude reasoning role**: analyze, design, plan,
write the PRD, validate and review. This skill is the conductor that sits **on top of** the per-phase
`graph-*` skills — it decides which phase you're in, runs that phase's `agf` commands and gate, and advances.

**CLI-first:** everything is driven through the `agf` CLI — there is NO MCP server.

## Role boundary (read this first)

**Claude's job here is to think, not to type code.** Responsibilities: **analyze, design, plan, PRD,
validate, review** (and handoff). **Implementation is done by a separate executor agent** — not Claude.

Under this skill: do **not** run `agf start → edit source files → agf done`. At IMPLEMENT, **prepare and
hand off**; resume at VALIDATE to review executor output. The only files Claude edits are planning/spec
artifacts: PRD, ADRs, AC, findings, docs — never application implementation, unless the user explicitly
says "implement / write the code yourself".

## Mandatory flow

```
[pre-flight: agf stats / agf query] →
ANALYZE → DESIGN → PLAN → (IMPLEMENT = delegate) → VALIDATE → REVIEW → HANDOFF
```

Pull, don't push (`agf next`). WIP = 1. Never mark a node `done` on a false claim.

## Pre-flight: reconcile before planning

Memory ≠ live state. Before trusting any progress count:
```bash
agf stats                 # node/edge counts by type & status
agf query --status done   # what the graph actually claims is done
```
If memory says "X done" but the graph/code disagrees, **graph and code win**. Fix the graph before planning.

## Phase cadence

| Phase | Cadence (`agf` CLI) | Gate (`agf`) | Depth skill |
|-------|---------------------|--------------|-------------|
| **ANALYZE** | `agf import-prd` / `agf node add --type requirement\|epic\|risk\|constraint` → `agf edge add` → `agf memory write` | `agf gate analyze` (DoR) | `graph-analyze` |
| **DESIGN** | `agf node add --type decision\|interface` (ADRs) → `agf edge add` → `agf constitution` | `agf gate design` (+harness ≥55) | `graph-design` |
| **PLAN** | `agf decompose` / `agf node add --type task` → testable AC per task → `agf insights` | `agf gate design` / `agf insights` | `graph-plan` |
| **IMPLEMENT** | **DELEGATE** — see handoff protocol. Claude does not code. | — | `graph-plan` (prep) |
| **VALIDATE** | review executor output: run tests, `agf check <id>`, `agf metrics`, `agf harness` | `agf check <id>` (DoD) | `graph-validate` |
| **REVIEW** | `agf insights` (impact) → `agf export` → `agf metrics` | `agf gate review` | `graph-review` |
| **HANDOFF** | `agf memory write` → `agf snapshot create` → `agf export` | `agf gate handoff` | `graph-handoff` |

After each gate passes, advance with `agf phase` and follow the recommended next action.

## Gate Checklist by Phase

Run these checks **before** calling `agf phase` to advance. A phase is not complete until all pass.

| Phase | Check 1 | Check 2 | Check 3 |
|-------|---------|---------|---------|
| **ANALYZE** | All requirements have a source or rationale | Risks surfaced as `risk` nodes | DoR score via `agf gate analyze` ≥ threshold |
| **DESIGN** | Every decision has an ADR with rationale + alternatives | Interfaces match requirements (edge coverage) | Harness ≥ 55 via `agf gate design` |
| **PLAN** | Every task has testable AC (Given/When/Then) | AC quality ≥ 60 via `agf check <id>` | No task blocks another without an edge |
| **VALIDATE** | All DoD items green via `agf check <id>` | Tests are real-source green (not unit-only) | `agf harness` score does not regress |
| **REVIEW** | Blast radius analyzed via `agf insights` | No stale sourceRefs (`agf insights` code_sync clean) | `agf gate review` passes |
| **HANDOFF** | Memory written with findings and decisions | Snapshot created | `agf gate handoff` passes |

→ See `[[swe-at-google]]` ch9 for the principle: presubmit automation handles mechanical checks so human
  gates can focus on design and comprehension quality.

## PRD Quality Rubric

A PRD is ready for `agf import-prd` only when all five criteria pass:

1. **Falsifiable** — every requirement can be proven true or false by a test. "Fast" fails; "P95 latency < 200ms" passes.
2. **Scoped** — explicit in/out-of-scope. Ambiguity in scope becomes scope creep.
3. **Acceptance criteria present** — each requirement has at least one Given/When/Then or measurable outcome.
4. **Risks listed** — at least one `risk` node per external dependency or unknown.
5. **Dependencies declared** — upstream requirements, downstream consumers, and external APIs named.

Fail any criterion → rewrite the PRD before importing. Do not compensate for a weak PRD by over-specifying tasks.

→ From `[[swe-at-google]]`: requirements must be falsifiable and testable — "if you liked it, put a test on it."
→ From `[[pragmatic-programmer]]`: Design by Contract — specify preconditions, postconditions, invariants.

## Atomic Task Criteria

A task is **atomic** when all four hold:

1. **Single concern** — one observable behavior changes. If the task title uses "and", split it.
2. **Independently testable** — can be verified in isolation without other tasks completing first.
3. **Estimable** — size is determinable before starting (S/M/L or story points). If not, spike first.
4. **No hidden knowledge** — all context the executor needs is attached (interfaces, ADR refs, AC).

Tasks that fail these criteria cause estimation errors, parallel-work collisions, and false `done` states.

→ From `[[pragmatic-programmer]]` DRY: each piece of knowledge has one authoritative representation — a task
  encapsulates one unit of that knowledge.

## Blocker Decision Tree

When a task or phase is blocked:

```
Is the blocker inside the graph (missing AC, wrong status, dependency edge)?
  YES → Reconcile: agf node update / agf edge add / agf node status → unblock
  NO ↓

Is the blocker an external dependency (API unavailable, data missing)?
  YES → Record as risk node: agf node add --type risk
        Mark task blocked: agf node status <id> blocked
        Escalate to user for decision
  NO ↓

Is the task too large to hand off cleanly?
  YES → Decompose: agf decompose <epic_id> → smaller atomic tasks
  NO ↓

Is a previous phase gate incomplete?
  YES → Do NOT skip gates. Return to the failed phase and fix it.
        Skipping gates creates downstream debt that compounds.
  NO ↓

Escalate: surface as finding node + report to user.
```

## Reconciliation Triggers

Run `agf stats` + `agf query --status done` + code verification when any of these occur:
- After every 3 tasks complete in IMPLEMENT
- After any rollback or revert
- After sprint boundary
- When memory progress counts contradict the graph
- Before writing the HANDOFF memory

## IMPLEMENT handoff protocol

Claude's deliverable at handoff is a **ready-to-execute work package**:

1. Each task has testable AC (Given/When/Then, AC quality ≥ 60 via `agf check <id>`) and an estimate.
2. Sibling context attached: `agf context <id>` returns the compact + RAG pack.
3. Dependencies/blockers resolved (`agf insights`), WIP=1, task is `ready`.
4. **Hand off to the executor agent.** State explicitly that implementation is delegated.
5. Resume at **VALIDATE**: review executor output — do not re-implement.

## Honesty (hard rule)

Never mark `done` with an unverified claim. Run DoD/gate first (`agf check <id>`). When you find a gap,
record it as a `finding` memory + `risk`/`epic` node and **report it** — do not paper over it.

## Output format

```
Phase: <CURRENT> → <NEXT>
Reconcile: <graph state delta, if any>
Did: <agf commands run this phase>
Gate: <agf gate/check> — <pass/fail, score>
Handoff (if IMPLEMENT): <work package ready: N tasks with AC, delegated to executor>
Findings: <loose ends surfaced as finding/risk nodes, or "none">
Next: <recommended next action / phase>
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-patterns

- Do **not** write production implementation — delegate (see role boundary).
- Do **not** trust memory progress counts — reconcile first (`agf stats`/`agf query`).
- Do **not** skip the phase gate before advancing.
- Do **not** push tasks to `in_progress` in bulk — WIP=1.
- Do **not** mark `done` to make a gate green — fix the work or record the gap.
- Do **not** import a PRD that fails the quality rubric — rewrite it first.
- Do **not** hand off tasks that fail the atomic criteria — decompose them first.

---

## graph-listening

---
name: graph-listening
description: LISTENING phase — DORA retrospective, CFD, knowledge gaps, cross-project learning, next cycle
trigger: /graph-listening
tools_used: [agf forecast, agf insights, agf metrics, agf node add, agf memory write, agf phase]
tokens: ~550
---
<!-- shared:phases,gates,principles,errors -->

# graph-listening

Data-driven retrospective, gap analysis, feedback collection, next-cycle seeding — all via `agf`.

See also: `[[kanban-in-action]]`, `[[humble-continuous-delivery]]`

## When
- After DEPLOY (release live)
- Collect feedback on shipped features
- Sprint retrospective
- `_lifecycle.phase === LISTENING`

## Flow
```
agf forecast → agf insights → agf metrics → [feedback] → agf node add → agf memory write → agf phase
```

## Steps

### 1. DORA Retrospective with Tier Context

`agf forecast` — sprint vs prior baseline; trends (better/worse/flat).

Map each metric to the DORA benchmark tier before calling a trend "good" or "bad":

| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Deploy frequency | On-demand (multiple/day) | Weekly | Monthly | < Monthly |
| Lead time for changes | < 1 hour | 1d – 1w | 1w – 1m | > 1 month |
| Change failure rate | < 5% | 5–10% | 10–15% | > 15% |
| Time to restore service | < 1 hour | < 1 day | < 1 week | > 1 week |

**Retrospective questions per metric:**
- Where does the team sit on this tier scale?
- Did the sprint move the metric up or down a tier?
- What is the single constraint preventing the next tier?

Document answers in `agf memory write` as `dora-retro-<sprint>`.

### 2. CFD Retrospective

`agf insights` — WIP accumulation, bottlenecks (where tasks pile up).

For each anomaly shape detected in the CFD, ask three questions:

| CFD Shape | 3 Retrospective Questions |
|---|---|
| **Inbox band growing** | (1) Which step is the bottleneck? (2) Is this a capacity problem or a dependency/blocker? (3) What WIP limit would surface the bottleneck faster? |
| **Middle band wide / growing** | (1) Are items blocked or just slow? (2) Is WIP exceeding team capacity? (3) Is there a specific item type that stagnates? |
| **Done band flat slope** | (1) Is the pipeline releasing less frequently than items complete? (2) Is integration or QA the gate? (3) What would double the Done slope? |
| **Consistent parallel slopes** | (1) Is this sustainable or are there hidden buffers? (2) Are all service classes flowing? (3) What would break this healthy state? |

Record the dominant shape and the three answers before moving on.

### 3. Knowledge Gap Detection

`agf insights` — RAG categories under-represented; areas needing more data for future context.

**Kanban-informed gap signal**: WIP items that get stuck repeatedly on the same column are not a process gap — they are a **team knowledge gap**. Distinguish:

- Item stuck once → likely external blocker (dependency, info request)
- Item stuck 2+ times in same column across sprints → team does not know how to complete that type of work confidently
- Column consistently has highest WIP → the team pulls but cannot push; a skill or tool is missing

For each identified knowledge gap, add a `learning` node: `agf node add --type task --tag learning`.

### 4. Sprint Metrics

`agf metrics` — throughput, cycle time, lead time, flow efficiency. Target: flow efficiency > 40%.

**Little's Law verification**: `Cycle Time = WIP / Throughput`. If the measured cycle time diverges from the Little's Law prediction by > 20%, there is hidden WIP (work counted as "in-progress" that is actually blocked or waiting). Surface it.

### 5. Collect Feedback

New nodes: bugs → `agf node add --type task`, feature requests → `agf node add --type epic`, tech debt → `agf node add --type task`.

### 6. Cross-Project Learning

`agf insights` — import patterns, estimates, errors from similar projects.

### 7. Backlog Health

`agf insights` — stale tasks (>30d), oversized without subtasks, blocked without action.

### 8. Next Cycle Seed

`agf memory write <name>` — save insights for next ANALYZE. `agf phase` — restart lifecycle.

## Exit
- [ ] DORA retrospective documented with tier positioning (`agf memory write`)
- [ ] CFD anomalies identified and 3-question analysis completed
- [ ] Knowledge gaps (stuck WIP) separated from process gaps and logged as learning nodes
- [ ] Little's Law verified — hidden WIP surfaced
- [ ] Feedback collected as nodes (bugs, features, debt)
- [ ] `agf phase` — next cycle ready

Loop: cycle seeded → next: graph-analyze.

## Economy
Token economy is part of the loop: run `agf savings` / `agf metrics --economy-report` after each task, then feed savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-mega-brain

---
name: graph-mega-brain
description: Drive all 9 phases as a self-improving spiral: pull → brief → build (autonomous or delegated) → submit/done → measure → learn → next. Each turn calibrates the next.
triggers:
  - graph-mega-brain
version: 2.1.0
author: auto-generated
date: 2026-06-21
category: ORCHESTRATION
phase: ORCHESTRATION
tokens: ~1442
phases: [LEAD, IMPLEMENT, VALIDATE]
---

# graph-mega-brain

Drive all 9 phases as a self-improving spiral: pull → brief → build (autonomous or delegated) → submit/done → measure → learn → next. Each turn calibrates the next. Dirija tudo pelo CLI `agf` — **zero MCP**. Carregue contexto com `agf context <id>` antes de mudar qualquer coisa.

## When to Use

- Drive a PRD/feature end-to-end through the graph (ANALYZE→…→LISTENING)
- Delegate the build to any driving CLI (no provider needed) or cheap headless executors
- Token cost matters: RAG + tier-router + gates + telemetry instead of generating everything

## Mandatory Flow

```
agf stats → [per phase: agf phase → phase cmds → agf brief → build → agf submit|done → agf check/gate] → agf savings → agf learning/heal → agf next (calibrated)
```

## Phase Advance Criteria

**DoD-gated, not time-boxed** (from `[[swe-at-google]]` incremental delivery principle).

A phase advances only when its Definition of Done is fully met — never because a timer expired:

| Gate signal | Stay in phase | Advance |
|-------------|--------------|---------|
| DoD checks | <7/7 passing | 7/7 passing |
| Test coverage | delta < 0 | delta ≥ 0 (no regression) |
| Open findings | Critical or High open | All Critical/High closed or recorded as risk |
| Gate command | `agf gate <phase>` returns FAIL | returns PASS |

If the gate fails, fix the work or record an honest gap as a finding — never mark done on a false claim.

## Autonomous vs Delegated

**Delegate when any of these is true:**
- Scope > 3 tasks in the current phase
- Specialized expertise needed (security, DB migration, mobile platform)
- Build requires tool access beyond the conductor's current context
- Task type matches a dedicated sub-skill (see delegation table below)

**Handle inline (autonomous) when:**
- Single-task, well-scoped, conductor has full context
- Quick scaffolding, config update, or doc-only change
- `agf status` returns `mode: autonomous` with a valid provider

## Delegation Decision Table

| Condition | Action | Sub-skill |
|-----------|--------|-----------|
| Scope > 3 tasks | Always delegate | `agf brief <id>` → executor |
| Security-sensitive code | Always delegate | `$graph-security` |
| Bug discovery needed | Delegate | `$graph-bug-hunter` |
| Quality audit needed | Delegate | `$graph-quality` |
| Single task, full context | Inline (autonomous) | — |

## Learning Metrics Per Cycle

Capture these 6 metrics after every `agf done` / `agf submit` via `agf savings` (from `[[kanban-in-action]]` flow measurement):

| # | Metric | How to capture | Informs |
|---|--------|---------------|---------|
| 1 | Token cost (this turn) | `agf metrics --economy-report` | Tier routing calibration |
| 2 | DoD grade (0–7) | `agf gate <phase>` score | Phase health trajectory |
| 3 | Test coverage delta | `agf check <id>` coverage diff | Risk in next phase |
| 4 | Cycle time (task open → done) | `agf learning stats` | WIP limit tuning |
| 5 | Blocker count | Findings in `agf submit` result | Systemic impediment detection |
| 6 | Token savings vs baseline | `agf insights flow` | RAG/flow calibration (Φ) |

Feed all 6 back via `agf learning stats | agf heal` before calling `agf next`. A turn without feedback is a circle, not a spiral.

## Steps

| Comando | O que faz |
|---------|-----------|
| `agf stats / agf query` | Pre-flight: reconcile graph (code/graph beat memory) |
| `agf phase` | Detect current phase (SHAPE→BUILD→SHIP) |
| `agf next` | Pull next task (WIP=1) |
| `agf brief <id>` | Delegation spec; --live cmds return mode:delegated when no provider |
| `agf submit <id> --result <json>` | Close delegated build: validate → blast → DoD → done; deviations → findings |
| `agf done <id>` | Close autonomous build: blast + savings + done + suggest next |
| `agf gate <phase>` | Phase readiness gate |
| `agf gaps` | Detect completeness gaps → delegate fix → re-verify |
| `agf savings / agf metrics --economy-report` | Measure the turn (counterfactual, labeled) |
| `agf insights flow` | Flow A/B verdict (flow_on vs flow_off token savings) |
| `agf learning stats / agf heal` | Learn + self-heal → calibrate the next turn |

## Workflow

Step 1: Pre-flight — `agf stats / agf query`; reconcile (code/graph beat memory)

Step 2: Per phase — `agf phase` detects; run the phase agf commands and pass the gate (see `$graph-<phase>`)

Step 3: Reuse before generating — apply the chain: rag-in → rag-out → artifact_reuse → repo_map → flow → rag-cache. Generate only the genuine delta.

Step 4: Brief — `agf brief <id>`; fill the `<fill:>` judgment calls (imitate, read/touch, contract, testWith)

Step 5: Build — Check `agf status` (data.mode). DELEGATED: implement the brief yourself, apply the edits, close via `agf submit`. AUTONOMOUS: `agf autopilot/run/deliver --live`. Mismatch between CLI mode and status → drive delegated and report it.

Step 6: Close — delegated: `agf submit <id> --result {arquivos,testes,desvios}`. autonomous: `agf check <id>` → `agf done <id>`

Step 7: Measure — capture all 6 learning metrics (see Learning Metrics Per Cycle)

Step 8: Learn — `agf learning stats | agf heal | agf gaps` → re-verify → calibrate → `agf next`

## Exit

- [ ] All 9 phases driven, gate passed each (DoD-gated, not time-boxed)
- [ ] Build delegated (brief → submit) or autonomous (--live → done); return validated by parse, not re-read
- [ ] All 6 learning metrics captured per cycle and fed back
- [ ] Loose ends become finding/risk — never done on a false claim

## Anti-Patterns

- NO one-shot of the whole system — decompose (`agf decompose`) and delegate per task
- NO generating what you can retrieve — RAG before the LLM is the whole economy
- NO frontier for everything — route by tier; frontier only for reasoning
- NO trusting memory progress counts — reconcile graph + code
- NO skipping the gate to go green — fix the work or record the gap honestly
- NO re-reading the executor diff to validate — use `agf submit` (parse the structured return)
- NO circle without feedback — capture all 6 metrics + `agf learning/heal` each turn or it never improves
- NO advancing a phase by time — advance only when DoD gate passes

## Output Format

```
Cycle: <feature/PRD> | Phase: <CURRENT> → <NEXT>
Reconcile: <graph delta, if any>
Mode: <autonomous|delegated> (provider <via>, or none)
Build: <N tasks closed via submit/done, validated M/N>
Gate: <agf gate/check> — <pass/fail, score/harness>
Economy: <tokens/$ this turn, saved vs baseline (method)>
Metrics: DoD=N/7 | Coverage Δ=+N% | Cycle=Nd | Blockers=N | Savings=N%
Learned: <thresholds/routing adjusted from this turn>
Findings: <loose ends as finding/risk, or "none">
Next: <next action / phase>
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Related Skills

- `[[swe-at-google]]` — incremental delivery, Beyoncé Rule (DoD-gated advance)
- `[[kanban-in-action]]` — Little's Law, cycle time, flow metrics (learning metrics)
- `$graph-lead` — `agf skill show graph-lead`
- `$graph-implement` — `agf skill show graph-implement`
- `$graph-validate` — `agf skill show graph-validate`

## Constraints

- CLI-first: everything via agf — zero MCP. Build is autonomous (provider) or delegated (any driving CLI via brief→submit)
- The conductor does not hand-write production code — it briefs, delegates, verifies
- WIP=1, pull (`agf next`); honesty: never done on a false claim
- Delegate when scope > 3 tasks or specialized expertise is needed
- It is a spiral, not a circle: every turn feeds all 6 metrics → learning back into the next

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-performance

---
name: graph-performance
description: Performance engineering audit using Lighthouse, Web Vitals, N+1 query detection, memory profiling, and bundle size analysis
triggers:
  - graph-performance
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-performance

Performance engineering audit using Lighthouse, Web Vitals, N+1 query detection, memory profiling, and bundle size analysis. Identifies performance bottlenecks across build output, runtime behavior, database queries, memory usage, and frontend metrics.

## When to Use

- Before DEPLOY phase — ensure performance baselines are met
- After major feature implementation — detect regressions early
- When performance complaints arise — systematic root cause analysis
- During VALIDATE for UI features — Web Vitals and Lighthouse audit

## Mandatory Flow

```
build analysis --> bundle size --> runtime profiling --> N+1 detection --> memory check --> Web Vitals --> benchmark comparison --> report --> write_memory
```

## Performance Threshold Reference

Use this table as the pass/warn/critical gate for every audit dimension:

| Metric | Target (Pass) | Warning | Critical |
|--------|--------------|---------|----------|
| Build time | <30s | 30-60s | >60s |
| JS bundle — landing page (gzip) | <150KB | 150-250KB | >250KB |
| JS bundle — app page (gzip) | <300KB | 300-450KB | >450KB |
| JS bundle — microsite (gzip) | <80KB | 80-130KB | >130KB |
| CSS bundle | <30KB | 30-50KB | >50KB |
| Event loop lag | <10ms | 10-50ms | >50ms |
| Tool / API response (p95) | <200ms | 200-500ms | >500ms |
| RAG query latency | <300ms | 300-800ms | >800ms |
| FCP | <1.5s | 1.5-3.0s | >3.0s |
| LCP | <2.5s | 2.5-4.0s | >4.0s |
| CLS | <0.1 | 0.1-0.25 | >0.25 |
| Metric regression vs baseline | <10% | 10-20% | >20% |

## Complexity Decision Guide

From [[clrs-algorithms]] — choose the algorithm tier that fits the data size:

| Data size | Acceptable complexity | Examples |
|-----------|----------------------|----------|
| n < 100 | O(n²) fine | Bubble sort, nested loops for small lists |
| n < 1K | O(n²) acceptable, prefer O(n log n) | Insertion sort, simple join |
| n < 100K | O(n log n) required | Merge sort, binary search, heap operations |
| n ≥ 100K | O(n) or O(n log n) only | Hash lookups, counting sort, BFS/DFS |
| n ≥ 1M | O(n) only | Streaming, linear scans, radix sort |

**Rule of thumb**: if the inner loop touches n items and the outer loop also touches n items, verify n < 1K or replace with a hash-based O(n) approach.

## N+1 Fix Patterns

### Pattern 1 — Promise.all batch (JS/TS async)

```ts
// BEFORE — N+1: one DB call per task
for (const task of tasks) {
  task.node = await store.getNodeById(task.nodeId); // N queries
}

// AFTER — 1 call for all
const nodeIds = tasks.map(t => t.nodeId);
const nodes = await store.getNodesByIds(nodeIds);   // 1 query
const nodeMap = new Map(nodes.map(n => [n.id, n]));
for (const task of tasks) {
  task.node = nodeMap.get(task.nodeId);
}
```

### Pattern 2 — IN clause grouping (SQL)

```sql
-- BEFORE — N queries
SELECT * FROM nodes WHERE id = $1;  -- called N times

-- AFTER — 1 query
SELECT * FROM nodes WHERE id IN ($1, $2, $3, ...);
```

In SQLite via better-sqlite3:
```ts
const placeholders = ids.map(() => '?').join(',');
const rows = db.prepare(`SELECT * FROM nodes WHERE id IN (${placeholders})`).all(...ids);
```

### Pattern 3 — DataLoader pattern (deferred batching)

Use when callers are spread across the codebase and can't be co-located:

```ts
import DataLoader from 'dataloader';
const nodeLoader = new DataLoader(async (ids: readonly string[]) => {
  const rows = await store.getNodesByIds([...ids]);
  const map = new Map(rows.map(r => [r.id, r]));
  return ids.map(id => map.get(id) ?? null);
});

// Each caller uses nodeLoader.load(id) — batched automatically per tick
```

Detection signal: `store.getNodeById()` / `db.prepare().get()` inside `for`, `forEach`, or `map`.

## Memory Profiling Toolkit

### Command 1 — Heap snapshot

```bash
node --inspect --inspect-brk src/index.js
# Open chrome://inspect → take heap snapshot before and after a suspected leak
# Sort by "Retained Size" → look for growing arrays, Map, or EventEmitter entries
```

### Command 2 — Continuous heap monitoring

```bash
node --max-old-space-size=512 --expose-gc src/index.js
# Inside code: if (global.gc) global.gc(); then measure process.memoryUsage().heapUsed
```

### Command 3 — Map/Set size instrumentation

```ts
// Add to long-running cache objects
setInterval(() => {
  console.log('[mem]', {
    semanticCache: semanticCache.size,
    queryCache: queryCache.size,
    heapMB: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
  });
}, 30_000);
```

**What to look for**: monotonically increasing `heapUsed` over 10+ minutes without GC reclaim = leak. Map `.size` growing without bound = missing eviction policy.

## Workflow

**Step 1 — Build**: `time npm run build`. Flag >60s. Check TypeScript warnings and circular deps.

**Step 2 — Bundle**: `du -sh dist/`. Apply **Performance Threshold Reference** table. Flag duplicates and tree-shaking failures.

**Step 3 — Runtime**: Measure via `mcp__mcp-graph__metrics`. Flag operations >500ms p95. For React SPA: run Lighthouse.

**Step 4 — N+1**: Apply **N+1 Fix Patterns** above. Search for `store.getNodeById()` / `db.prepare().get()` inside loops. Verify batch queries use `WHERE id IN (...)`.

**Step 5 — Memory**: Apply **Memory Profiling Toolkit** above. Also check: unbounded caches (no `maxSize`/TTL), `on()` without matching `off()`, `fs.open()` without `close()`.

**Step 6 — Web Vitals**: FCP <1.5s · LCP <2.5s · CLS <0.1 · TTI <3.9s. Use Playwright `performance.getEntriesByType('navigation')`.

**Step 7 — Benchmark**: `npm run test:bench`. Flag >20% regression vs baseline from memory.

### Step 8: Performance Report

| Dimension | Weight | Score Criteria |
|-----------|--------|---------------|
| Build | 10% | Time, warnings, incremental |
| Bundle | 20% | Size vs thresholds, no duplicates |
| Runtime | 25% | Response times, event loop lag |
| Queries | 20% | N+1 count, missing indexes, batch usage |
| Memory | 15% | Leaks, cache bounds, cleanup |
| Web Vitals | 10% | FCP, LCP, CLS, TTI |

**Grading:** A (90-100) · B (75-89) · C (60-74) · D (45-59) · F (<45)

Save findings:
```
Tool: mcp__mcp-graph__write_memory (title: "Performance Audit — <date>", content: <report>)
```

## Output Format

```
Phase: PERFORMANCE AUDIT
Build: <N>s build time, <N> warnings
Bundle: <N>KB total (<N> files, largest: <name> at <N>KB)
Runtime: <N>/100 (avg response: <N>ms, p95: <N>ms)
N+1 Queries: <N> detected (<N> critical, <N> warning)
Memory: <N> issues (<N> unbounded caches, <N> leaked listeners)
Web Vitals: FCP <N>s, LCP <N>s, CLS <N>, TTI <N>s
Benchmark: <N> regressions (>20% from baseline)
Overall Grade: <A-F> (<N>/100)
Recommendations: <top 3 actions>

Saved to memory: "Performance Audit — <date>"
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT optimize without measuring first — profile before changing code
- Do NOT micro-optimize — focus on bottlenecks (Pareto 80/20), not hot loops that run once
- Do NOT ignore N+1 queries — they compound under load and are the #1 performance killer
- Do NOT skip memory check — leaks are silent until OOM crashes in production
- Do NOT deploy without bundle size check — bundle regression is common and cumulative
- Do NOT compare without baseline — use benchmark tests and previous audit data from memory
- Do NOT assume O(n²) is fine — verify n is truly small (<1K) before accepting it

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-plan

---
name: graph-plan
description: Execute the PLAN phase of the lifecycle via the `agf` CLI — smart decompose, sprint planning, DORA-based estimation, cross-project learning
triggers:
  - graph-plan
version: 2.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-plan

Execute the PLAN phase of the lifecycle, driving the `agf` CLI (zero MCP). Decomposes epics into atomic tasks (auto or manual), plans sprints, maps dependencies, and prepares for implementation using DORA metrics for estimation.

## When to Use

- After DESIGN phase is complete (ADRs documented, architecture defined)
- Breaking epics into implementable tasks
- Planning sprint scope and priorities
- The current phase reported by `agf phase` is `PLAN`

## Mandatory Flow

```
agf context <id> → agf decompose / agf node add → agf edge add → agf forecast → agf insights → agf phase implement
```

## Workflow

### Step 1: Load Context

```bash
agf context <epic id>
agf search "<epic title + decisions>"
```

Review ADRs, requirements, and architecture from DESIGN phase.

### Step 2: Import Cross-Project Estimates

```bash
agf search "estimates patterns velocity"
```

Query `agf` history → extract velocity patterns from similar past epics → apply DORA-calibrated estimates to current sprint. Use historical deployment frequency and lead time P85 as anchors. Skip if no prior history exists.

### Step 3: Decompose Epics

**Option A — Smart Decompose (v6.0 recommended):**
```bash
agf decompose <epic_id>
```

Auto-creates subtasks: 1 AC = 1 subtask with test type inference:

| Keywords in AC | Inferred test type |
|----------------|-------------------|
| api, endpoint, database, persists, sync, fetch, http | **integration** |
| page, click, browser, redirect, ui, form, button | **e2e** |
| Everything else | **unit** |

**Option B — Manual decomposition:**
```bash
agf node add --type task
agf node add --type subtask
```

**Atomic decomposition rules (XP Anti-Vibe-Coding):**
- Each task completable in ≤ 2h
- Each task has clear AC with testable assertions
- Each task has XP size estimate (XS, S, M, L, XL)
- Prefer many small tasks over few large ones

### Step 4: Decomposition Quality Criteria

Validate every task against these 4 rules before proceeding (from [[pragmatic-programmer]]):

1. **Independent** — deliverable without blocking or being blocked by a sibling task
2. **Estimable** — team can assign an XP size (XS–XL) with confidence; if not, spike first
3. **Testable** — has at least one concrete acceptance criterion with a measurable outcome
4. **< 1 day** — completable within a single working day; if not, decompose further

Any task failing 2+ criteria must be re-decomposed before continuing.

### Step 5: PERT Estimation

Use 3-point PERT when a task has significant uncertainty (size M or larger):

```
PERT estimate  = (O + 4M + P) / 6
Std deviation  = (P − O) / 6
95% confidence = PERT + 2 × σ
```

- **O** = Optimistic (best-case, no surprises)
- **M** = Most likely (realistic, normal conditions)
- **P** = Pessimistic (worst-case, realistic blockers)

Use single-point estimates only for XS/S tasks with no technical unknowns. For tasks with dependencies on external systems or unfamiliar APIs, always apply PERT.

### Step 6: Map Dependencies

```bash
agf edge add <from> <to> --type <rel>
```

Edge types: `task → task`, `subtask → task`, `task → epic`, `task → decision`.

### Step 7: Sprint Capacity Formula

Calculate available capacity before assigning tasks:

```
sprint_capacity = available_hours × focus_factor
focus_factor    = 0.70  (team, ≥2 people — meetings, reviews, interruptions)
focus_factor    = 0.80  (solo — fewer context switches but no pairing buffer)
buffer          = 10–15% of capacity — reserved for unknowns and scope creep
assignable      = sprint_capacity − buffer
```

Map PERT estimates (hours) to assignable capacity. Do not exceed `assignable` when loading a sprint.

### Step 8: Review DORA Metrics

```bash
agf forecast
```

Use historical velocity (deployment frequency, lead time) to validate sprint capacity.

### Step 9: Validate Sprint Health

```bash
agf insights
```

Score the sprint plan: balanced load, no oversized tasks, dependencies resolved.

### Step 10: Definition of Ready (DoR)

Run `agf gate plan` and verify all 7 checks before transitioning to IMPLEMENT (see also [[kanban-in-action]] — work entering a column must meet entry criteria):

| # | Check | What it verifies |
|---|-------|-----------------|
| 1 | `has_decomposition` | Every epic has ≥1 task |
| 2 | `has_acceptance_criteria` | Every task has ≥1 AC |
| 3 | `no_oversized_tasks` | No task larger than L without subtask decomposition |
| 4 | `dependencies_mapped` | All edges added, no cycles |
| 5 | `sprint_assigned` | Every in-scope task has a sprint assignment |
| 6 | `estimates_present` | Every task has an XP size (XS–XL) |
| 7 | `capacity_validated` | Total estimated hours ≤ sprint assignable capacity |

If any check fails, fix it and re-run the gate.

### Step 11: Sync Stack Documentation

Ensure the knowledge base has current API docs for the stack before IMPLEMENT. Refresh stack docs so the executor has accurate references.

### Step 12: Transition

Once gate passes:
```bash
agf phase implement
```

Follow the next-action hint printed by the `agf` CLI for the recommended next command.

## Output Format

```
Phase: PLAN → IMPLEMENT
Tasks: N tasks, M subtasks created (K via agf decompose)
Sprints: J sprints planned
Dependencies: D edges mapped
PERT applied: X tasks (M or larger, uncertain)
Sprint capacity: H hours assignable (focus_factor=0.7x, buffer=15%)
DORA: velocity X tasks/day, lead time P85 Yh
DoR gate: 7/7 checks passed — score N/100, grade X
Status: Ready to proceed to IMPLEMENT phase
```

## Anti-Patterns

- Do NOT write code during PLAN — this phase is planning only
- Do NOT create tasks larger than 2h — use `agf decompose` or decompose manually
- Do NOT skip acceptance criteria — they drive TDD in IMPLEMENT
- Do NOT ignore dependencies — they determine execution order
- Do NOT plan everything at once — plan 1-2 sprints ahead, refine later
- Do NOT use single-point estimates for uncertain M/L/XL tasks — apply PERT
- Do NOT overfill sprints — always subtract the buffer from assignable capacity
- Do NOT skip DoR — a task that fails DoR will block IMPLEMENT
- Do NOT skip refreshing stack docs — current API references prevent executor hallucination

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

## Economy

Token economy is part of the loop: run `agf savings` / `agf metrics --economy-report` after each task, then feed savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Cross-References

- [[kanban-in-action]] — WIP limits, Little's Law, sprint entry criteria
- [[pragmatic-programmer]] — INVEST, decomposition quality, estimability

---

## graph-platform

---
name: graph-platform
description: Platform audits — Test Pyramid + FIRST, Web Vitals + N+1 + bundle, WCAG 2.2 AA + ARIA, Harness score, Kanban
trigger: /graph-platform
tools_used: [harness, check, metrics, forecast, kanban, insights, memory]
tokens: ~900
---
<!-- shared:principles,errors,harness -->

# graph-platform

Integrated platform audit: tests, performance, accessibility, harness engineering, kanban.

> Cross-references: [[khorikov-unit-testing]] (Test Pyramid, Four Pillars); [[swe-at-google]] ch11 (Testing Overview); [[kanban-in-action]] (WIP limits, flow metrics)

## When
- VALIDATE/REVIEW — full audits before ship
- DEPLOY gate — harness ≥ 70 mandatory
- `$graph-platform` or "platform audit", "test audit", "performance check", "accessibility", "harness", "kanban"

## Flow
```
test audit → perf audit → a11y audit → harness scan → kanban → platform score → report → agf memory write
```

---

## Test Audit (Pyramid + FIRST)

1. **Suite Gate:** `npm test` — zero failures, else STOP.
2. **Coverage:** statements/branches/functions/lines ≥ 70%.
3. **Pyramid Ratio Targets** (from Khorikov): target **70% unit / 20% integration / 10% E2E**.
   - Unit: fast, isolated, tests a single behavior or function
   - Integration: tests one managed dependency (real DB, real file system)
   - E2E: tests full user journey through real deployment
   - **Inverted pyramid signal**: if E2E% > unit%, the suite is slow, fragile, and expensive to maintain. Immediate action required.
4. **FIRST:** Fast (no >5s tests), Independent (no shared/ordered state), Repeatable (no unseeded random/Date, no flaky), Self-validating (asserts not console.log), Timely (TDD).
5. **Quality:** descriptive names (`it("should X when Y")`), 1 assert/test, edge cases (null, empty, boundary).

### Test Pyramid Ratio Remediation

| Signal | Action |
|--------|--------|
| E2E > 30% | Decompose into unit + integration tests |
| Integration < 10% | Add real-DB integration tests for repositories |
| Unit < 60% | Identify domain logic with no unit coverage |
| No tests at all | Walking Skeleton first — one E2E, then build pyramid down |

---

## Performance Audit (Web Vitals + N+1 + Bundle)

1. **Bundle:** `npx tsup --silent && ls -lh dist/` — chunks > 100KB? Tree-shaking effective?
2. **Vitals:** FCP < 1.8s, LCP < 2.5s, CLS < 0.1, TTI < 3.8s.
3. **N+1:** loops with SQLite queries, `forEach` + `store.getNode()`, un-batched queries. `agf insights`.
4. **Memory:** unbounded caches (Map no TTL), listeners without cleanup, unclosed file handles, unbounded arrays.
5. **Benchmark:** vs prior baseline. Regression > 10% → flag.

---

## Accessibility Audit (WCAG 2.2 AA)

1. **POUR:** Perceivable (text alternatives, captions, contrast), Operable (keyboard, time, seizure-safe, navigable), Understandable (readable, predictable, input help), Robust (assistive-tech compatible).
2. **ARIA:** correct roles/properties/states, input labels, image alt, heading hierarchy (no skipped levels).
3. **Keyboard:** logical tab order, visible focus, skip links, modal focus traps.
4. **Contrast:** normal ≥ 4.5:1, large ≥ 3:1. `agf check <id>`.
5. **Screen Reader:** `agf check <id>` — Playwright + axe-core.

---

## Harness Engineering

### Harness Score Formula

```
harness_score = (type_coverage × 0.25)
              + (test_coverage  × 0.25)
              + (arch_fitness   × 0.15)
              + (docs_coverage  × 0.10)
              + (naming_clarity × 0.10)
              + (error_handling × 0.05)
              + (context_density× 0.05)
              + (provenance     × 0.05)
```

| Dimension | Weight | CLI |
|-----------|--------|-----|
| Type Coverage | 25% | `agf harness` |
| Test Coverage | 25% | Coverage report |
| Architecture Fitness | 15% | `agf insights` (coupling) + layer check |
| Docs Coverage | 10% | CLAUDE.md, README, rules/, docs/ |
| Naming Clarity | 10% | Descriptive names (no data/result/temp) |
| Error Handling | 5% | Typed errors, no empty catch |
| Context Density | 5% | JSDoc on exports |
| Provenance | 5% | Nodes with source_file receipt |

Grades: A≥85, B≥70, C≥55, D<55. Deploy gate: B (≥70) mandatory. `agf harness` (scan → trend → advice).

---

## Kanban Board Health

Run `agf kanban` — swimlane per epic.

### Quick Health Signals

| Signal | Healthy | Warning |
|--------|---------|---------|
| WIP violations | 0 | Any column over WIP limit |
| Aging items | 0 items > 3 days in same state | >10% of cards stale |
| Blocked ratio | < 5% of active cards | > 10% blocked |

- **WIP (Little's Law):** WIP = 1/agent. cycle_time = WIP/throughput. Flag violations immediately.
- **Bottleneck (TOC):** Find the most-loaded column. VALIDATE piling up → stop IMPLEMENT, focus VALIDATE.
- **Flow Metrics:** `agf metrics` — throughput, cycle/lead time, blocked %. Target flow efficiency > 40%.
- **Aging items:** cards stuck >3 days in the same column signal blockers, unclear AC, or missing dependencies. Surface in standup.

### Kanban Remediation

- WIP violation → refuse new work until column drains below limit
- Blocked > 10% → run impediment review, not more sprints
- Aging > 3 days → split the card or escalate the blocker

---

## Platform Health Synthesis

Five sub-audits combine into one platform score:

```
platform_score = (test_score  × 0.30)
               + (perf_score  × 0.25)
               + (a11y_score  × 0.20)
               + (harness_score × 0.15)
               + (kanban_score × 0.10)
```

| Sub-Audit | Weight | Key Gate |
|-----------|--------|----------|
| Test (pyramid + coverage) | 30% | Zero failures, ≥70% coverage |
| Performance (vitals + N+1) | 25% | 0 regressions > 10% |
| Accessibility (WCAG 2.2 AA) | 20% | 0 critical violations |
| Harness (4-dim formula) | 15% | Score ≥ 70 |
| Kanban (WIP + flow) | 10% | WIP ≤ 1, blocked < 10% |

**Grades:** A≥85, B≥70, C≥55, D<55. Platform grade B is the minimum for DEPLOY.

---

## Exit
- [ ] Test suite green, coverage ≥ 70%, pyramid not inverted
- [ ] Performance: 0 regressions > 10%
- [ ] A11y: 0 critical WCAG violations
- [ ] Harness score ≥ 70 (formula verified)
- [ ] Kanban: WIP ≤ 1, aging < 3 days, blocked < 10%
- [ ] Platform health score documented and ≥ 70
- [ ] Report saved via `agf memory write`

Loop: audits pass → next: graph-deploy.

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-prd

# graph-prd

Phase 0 — Transform a vague idea into a structured, import-ready PRD using 7 product methodologies: 5W2H, Jobs-to-be-Done, Pareto 80/20, MoSCoW, INVEST, Given-When-Then, and Risk Matrix.

## When to Use

- Starting from scratch with only a vague idea or feature concept
- Before the ANALYZE phase when no PRD document exists yet
- When you want a structured requirements elicitation process that covers all angles
- When you want a PRD that scores high on the PRD-quality gate (`agf gate analyze`)

## Mandatory Flow

```
5W2H → JTBD → Brainstorm+Pareto → MoSCoW → INVEST decomposition → Given-When-Then → Risk Matrix → Out-of-Scope → Generate PRD.md → `agf import-prd <file> --dry-run` → $graph-analyze
```

Note: This skill is PRE-lifecycle. It does NOT change the phase (`agf phase`). The transition to ANALYZE happens via `$graph-analyze`.

## Workflow

### Step 1: Vision & Context (5W2H)

Ask the user the 7 structured questions — present them as a single block for the user to answer:

- **What** — What is the product/feature? What problem does it solve?
- **Why** — Why is this needed now? What's the business justification?
- **Who** — Who are the target users? Who are the stakeholders?
- **Where** — Where will this run? (platform, environment, infrastructure)
- **When** — What's the timeline? MVP deadline? Phased delivery?
- **How** — How will it work at a high level? Key technical approach?
- **How Much** — What are the resource constraints? Team size, budget, token limits?

After answers, synthesize a **Vision Statement** (2-3 sentences) and confirm with the user.

### Step 2: Jobs-to-be-Done (JTBD)

Extract user jobs from 5W2H answers. Format each as: **"When [situation], I want to [motivation], so I can [expected outcome]."** Present 2-5 JTBD statements for user review. Identify what the current workaround is and what success looks like.

### Step 3: Hypothesis Format

Each JTBD must produce at least one falsifiable hypothesis (from [[pragmatic-programmer]] and [[swe-at-google]] — requirements that cannot be falsified are untestable):

```
IF  [user action or system behavior]
THEN [observable outcome]
BECAUSE [assumption being validated]
```

Example:
```
IF  a user uploads a file > 10MB
THEN the system rejects it with a clear error within 200ms
BECAUSE the storage quota assumption is 10MB max per upload
```

Every hypothesis must be falsifiable — "users will like it" is not a hypothesis; "DAU increases by 10% in 30 days" is.

### Step 4: Feature Brainstorm & Pareto Analysis (80/20)

Ask the user to brainstorm ALL features (no filter, quantity over quality).

Then apply Pareto 80/20:
1. Rate each feature: **Value** (1-10) and **Effort** (1-10)
2. Calculate **Value/Effort ratio**
3. Present a sorted table
4. Highlight the **top 20%** by ratio — these are the Pareto winners

```
| Feature | Value | Effort | Ratio | Pareto? |
|---------|-------|--------|-------|---------|
| ...     | 9     | 3      | 3.0   | TOP 20% |
```

Ask user to confirm the shortlist.

### Step 5: MoSCoW Prioritization

Categorize ALL features from Step 4. Decision criteria (from [[swe-at-google]] — scope creep is the primary enemy of sustainable delivery):

| Priority | Label | Decision rule |
|----------|-------|---------------|
| 1–2 | **Must** | Cannot launch without — blocking launch or legal/compliance |
| 3 | **Should** | High value, not launch-blocking — deferred to sprint 2 if needed |
| 4 | **Could** | Nice-to-have — first cut when constrained |
| — | **Won't** | Explicitly out of scope this version |

Present the categorization and ask user to adjust. Only Must + Should proceed to decomposition.

### Step 6: Epic & Story Decomposition (INVEST)

Group Must + Should features into **Epics** (become `##` headings in PRD). For each epic, decompose into **Tasks** (become `###` headings).

Validate each task against INVEST criteria:
- **I**ndependent — Can be developed without other tasks?
- **N**egotiable — Not over-specified? Room for implementation decisions?
- **V**aluable — Delivers user-facing value?
- **E**stimable — Can we size it? Assign `**Tamanho:** XS|S|M|L|XL`
- **S**mall — Completable in 1 sprint? If L/XL, decompose further
- **T**estable — Can we write acceptance criteria?

Add metadata to each task:
```
**Tamanho:** S
**Prioridade:** 2
**Tags:** auth, security
**Depende de:** Task 1.1
```

### Step 7: Acceptance Criteria (Given-When-Then)

For each task from Step 6, write testable AC using BDD format (mandatory — from [[swe-at-google]] Beyoncé Rule: if a behavior matters, put a test on it):

```
**Criterios de aceite:**
- GIVEN user is on login page WHEN enters valid credentials THEN receives JWT token
- GIVEN invalid password WHEN login attempted THEN shows error message
```

Target: 2-3 AC per task. Every AC must be testable (concrete values, observable outcomes). Vague AC like "system works correctly" are rejected. Checklist format (`- [ ] ...`) is acceptable for simple tasks.

### Step 8: Risk Register (P×I Matrix)

Apply the Risk Matrix (Probability × Impact = Severity):

```
| Risk | Probability | Impact | Score | Severity | Mitigation |
|------|-------------|--------|-------|----------|------------|
| ...  | High (3)    | High(3)| 9     | Critical | ...        |
```

Scoring scale — Probability: Low=1, Med=2, High=3. Impact: Low=1, Med=2, High=3.

| Score | Severity | Required action |
|-------|----------|-----------------|
| 7–9   | Critical | Mitigation required before sprint 1 |
| 4–6   | High | Mitigation planned in sprint 1 |
| 1–3   | Low | Monitor only |

Identify at least 2 risks. For each Critical/High risk, define a concrete mitigation strategy.

### Step 9: Out-of-Scope Statement

Explicitly list what this PRD does NOT cover (from [[swe-at-google]] — explicit non-requirements prevent scope creep and align stakeholders):

```
## Fora do Escopo
- Mobile native apps (web-only MVP)
- Multi-tenant support (single org only)
- Real-time collaboration (async only)
- <add items confirmed as Won't with the user>
```

At least 3 explicit out-of-scope items are required. If the user cannot name 3, prompt: "What would a stakeholder typically ask for that we are deliberately not building?"

### Step 10: PRD Generation

Assemble the structured markdown using the parser-compatible format. Required sections and parser contract:

- `# PRD: <Title>` — document root
- `## Visao Geral` — vision + JTBD
- `## Hipoteses` — falsifiable hypotheses from Step 3
- `## Fase N — <Name>` → `### Epic: <Name>` → `#### Task N.M: <Title>` — hierarchy
- Task metadata: `**Tamanho:** S`, `**Prioridade:** 2`, `**Tags:** ...`, `**Depende de:** Task X.Y`
- `**Criterios de aceite:**` label required for AC detection (parser looks for this exact label)
- `## Riscos` → `### Risk: <Name>` with `Probabilidade:`, `Impacto:`, `Mitigacao:`
- `## Restricoes` → `### Constraint: <Name>`
- `## Fora do Escopo` → bullet list of ≥3 explicit non-requirements

Parser rules: `##` = epic, `###`/`####` = task. Do NOT use `##` for tasks.

Save to `docs/_internal/prd/<kebab-case-name>.md`.

### Step 11: Quality Validation (Dry Run)

```bash
agf import-prd docs/_internal/prd/<name>.md --dry-run
```

Review: epics detected, tasks have AC, risks and constraints found, dependencies inferred. Iterate if issues found.

### Step 12: Transition

```
PRD ready at docs/_internal/prd/<name>.md
Next step: Run $graph-analyze to import this PRD and begin the 9-phase lifecycle.
```

## Output Format

```
Phase: PRD (Phase 0 — Pre-lifecycle)
Methodologies: 5W2H, JTBD, Hypotheses, Pareto 80/20, MoSCoW, INVEST, GWT, Risk P×I, Out-of-Scope
File: docs/_internal/prd/<name>.md
Epics: N defined
Tasks: M with acceptance criteria
Hypotheses: H falsifiable statements
Risks: K identified (J Critical/High with mitigation)
Out-of-scope: ≥3 explicit items
Dry-run: `agf import-prd --dry-run` — X nodes extracted
Quality: PRD-quality gate (`agf gate analyze`) target ≥ 70/100
Next: $graph-analyze
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT skip methodology steps — each feeds the next
- Do NOT write vague hypotheses — every hypothesis must be falsifiable
- Do NOT write code or make architecture decisions — that belongs to DESIGN
- Do NOT run `agf import-prd` without `--dry-run` first
- Do NOT change the phase (`agf phase`) — pre-lifecycle, transition via `$graph-analyze`
- Do NOT generate the PRD without user confirmation at each step
- Do NOT use `##` headings for tasks — the parser maps `##` to epics
- Do NOT skip the Out-of-Scope section — scope creep is the enemy of sustainable delivery
- Do NOT skip risk/constraint sections — they account for 30% of the prd_quality score
- Do NOT produce vague AC — use concrete Given-When-Then with measurable outcomes

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

## Cross-References

- [[swe-at-google]] — Beyoncé Rule (testable AC), scope creep, sustainability
- [[pragmatic-programmer]] — falsifiable hypotheses, Design by Contract, DRY

---

## graph-publish

---
name: graph-publish
description: Pipeline de release completo — security gate, bump, 5 bundles offline + SHA256, GitHub Release, site + server deploy
trigger: /graph-publish
phases: [DEPLOY]
category: release
tools_used: [npm audit, npm run build, pack:offline, gh release, rsync, ssh, agf memory]
tokens: ~1200
---

# graph-publish

Pipeline completo para publicar uma nova versão do agf: segurança → bump → bundles → 3 repos → GitHub Release → servidor.

> ⚠️ Este skill contém configurações de infraestrutura específicas deste projeto (servidor, paths, SSH key).
> Fica em `.agents/skills/` — não vai para o bundle offline nem para o npm.

## Quando usar

- Há commits `feat:` ou `fix:` acumulados no `main` prontos para release
- `/graph-publish` ou "publicar nova versão", "fazer release", "deploy nova versão"

## Semver Decision Table

| Commit type | Version bump | Example |
|-------------|-------------|---------|
| `feat:` — new capability, backward-compatible | **minor** (0.x.0) | 0.18.0 → 0.19.0 |
| `fix:` — bug fix, no API change | **patch** (0.0.x) | 0.18.0 → 0.18.1 |
| `feat!:` or `BREAKING CHANGE:` footer | **major** (x.0.0) | 0.18.0 → 1.0.0 |
| `chore:` / `docs:` / `refactor:` alone | **no bump** — not a release trigger | — |

When `feat:` and `fix:` coexist since the last tag, the highest-priority rule wins (minor beats patch).

## Security Gate Criteria

All three checks must be **green** before proceeding past Step 0:

| Check | Command | Pass condition |
|-------|---------|---------------|
| Vulnerability scan | `npm audit --json` | Zero `critical` or `high` severities |
| Secrets scan | `git secrets --scan` or `trufflehog git file://.` | Zero findings |
| License compliance | `npx license-checker --onlyAllow 'MIT;ISC;Apache-2.0;BSD-2-Clause;BSD-3-Clause'` | Zero forbidden licenses |

Dev-only `moderate` (e.g. `esbuild`, `intelephense`) are acceptable. If any check fails, stop and fix before bumping.

See `[[humble-continuous-delivery]]` ch4 for deployment pipeline gate theory: gates exist to stop bad builds early, not to slow down good ones.

## Rollback Protocol

If the pipeline fails **after** Step 5 (version already bumped and pushed), execute in order:

1. **Identify last good tag**: `git describe --tags --abbrev=0 HEAD~1`
2. **Revert version bump commit**: `git revert <bump-commit-sha> --no-edit && git push origin main`
3. **Delete the GitHub Release** (if created): `gh release delete vNEW_VERSION --repo DiegoNogueiraDev/graph-flow-skills --yes`
4. **Delete the tag** (if pushed): `git push origin :refs/tags/vNEW_VERSION` and `cd ../graph-flow-skills && git push origin :refs/tags/vNEW_VERSION`

After rollback, diagnose root cause before re-running the pipeline. Do not re-run immediately. See `[[swe-at-google]]` — rollbacks still require review; never skip the investigation step.

## Configuração inicial

No início da sessão, determine e confirme as variáveis:

```bash
# Detecta versão atual (OLD_VERSION)
node -p "require('./package.json').version"

# Define NEW_VERSION com base nos commits desde a última tag:
git log $(git describe --tags --abbrev=0)..HEAD --oneline | grep -E "^[a-f0-9]+ (feat|fix):"
# feat: → minor bump · fix: → patch bump
```

Substitua `NEW_VERSION` e `OLD_VERSION` em todos os comandos abaixo.

---

## Constantes fixas

```
SSH_KEY   = ~/.ssh/copadomundo_ed25519
SERVER    = deploy@13.140.162.224
APP_PATH  = /opt/graph-flow
DIST_DIR  = dist-offline/
GH_REPO   = DiegoNogueiraDev/graph-flow-skills
CLOUD_FLOW = ../graph-cloud-flow
SKILLS    = ../graph-flow-skills
```

---

## Fluxo

```
audit fix → bump → build → test:blast → bundles(5) → sha256(5) → commit agf →
update cloud-flow(3 arquivos) → commit cloud-flow → update skills(2 arquivos) →
commit + tag skills → gh release create (10 assets) → rsync + build + pm2 → verify(4)
```

---

## Passos

### 0. Security gate

```bash
cd /path/to/agent-graph-flow
npm audit fix
npm run typecheck     # 0 erros
npm run test:blast    # 0 falhas
```

Se `npm audit fix` reportar HIGH/CRITICAL remanescentes: investigar antes de prosseguir.
Dev-only deps com moderate (ex: `esbuild`, `intelephense`) são aceitáveis.

---

### 1. Bump de versão

Editar **dois arquivos**:

```bash
# package.json — trocar "version": "OLD_VERSION" → "NEW_VERSION"
# .release-please-manifest.json — trocar ".": "OLD_VERSION" → ".": "NEW_VERSION"
```

---

### 2. Build

```bash
npm run build         # compila dist/
npm run typecheck     # confirma 0 erros
```

---

### 3. Bundles offline (5 plataformas)

```bash
# 1. darwin-arm64 (nativo, usa a máquina atual)
npm run pack:offline

# 2. darwin-x64 (cross-compile)
node scripts/pack-offline.mjs --target-platform darwin --target-arch x64

# 3. linux-x64 (cross-compile)
node scripts/pack-offline.mjs --target-platform linux --target-arch x64

# 4. win32-x64 (cross-compile)
node scripts/pack-offline.mjs --target-platform win32 --target-arch x64

# 5. win32-arm64 (cross-compile)
node scripts/pack-offline.mjs --target-platform win32 --target-arch arm64
```

Resultado esperado em `dist-offline/`:
- `agf-offline-darwin-arm64-NEW_VERSION.tgz`
- `agf-offline-darwin-x64-NEW_VERSION.tgz`
- `agf-offline-linux-x64-NEW_VERSION.tgz`
- `agf-offline-win32-x64-NEW_VERSION.tgz`
- `agf-offline-win32-arm64-NEW_VERSION.tgz`

Linux-arm64 não tem bundle — marcar como `available: false` em `releases/page.tsx`.

---

### 4. SHA256 checksums

```bash
cd dist-offline
for f in agf-offline-*-NEW_VERSION.tgz; do
  shasum -a 256 "$f" > "$f.sha256"
done
cd ..
```

Verificar: `ls -1 dist-offline/*NEW_VERSION*` deve mostrar 10 arquivos (5 `.tgz` + 5 `.sha256`).

**SHA256 consumer verification command** (document in release notes):
```bash
shasum -a 256 -c agf-offline-darwin-arm64-NEW_VERSION.tgz.sha256
# Expected: agf-offline-darwin-arm64-NEW_VERSION.tgz: OK
```

---

### 5. Commit agent-graph-flow

```bash
git add package.json .release-please-manifest.json
git commit -m "chore: bump version to NEW_VERSION"
git push origin main
```

---

### 6. Atualizar graph-cloud-flow

Em `../graph-cloud-flow`, editar **3 arquivos**:

**`public/install.sh`** — trocar `VERSION="OLD_VERSION"` → `VERSION="NEW_VERSION"`:
```
VERSION="NEW_VERSION"
```

**`public/install.ps1`** — trocar `$Version = 'OLD_VERSION'` → `$Version = 'NEW_VERSION'`:
```
$Version = 'NEW_VERSION'
```

**`app/releases/page.tsx`** — atualizar:
```tsx
const VERSION  = 'NEW_VERSION';
const REL_DATE = 'Mmm DD, YYYY';  // data do release (ex: "Jun 19, 2026")
```

Verificar também:
- `size` de cada bundle: `ls -lh dist-offline/*NEW_VERSION.tgz` 
- `available: true` para plataformas geradas; `available: false` para linux-arm64
- `GH_BASE` url usa `${VERSION}` automaticamente — não precisa mudar

---

### 7. Commit graph-cloud-flow

```bash
cd ../graph-cloud-flow
git add public/install.sh public/install.ps1 app/releases/page.tsx
git commit -m "chore: bump agf to NEW_VERSION — install scripts and releases page"
git push origin main
cd -
```

---

### 8. Atualizar graph-flow-skills

Em `../graph-flow-skills`, editar **2 arquivos** (SHA256 verification já implementado — só bump de versão):

**`install.sh`** — linha com `VERSION="${AGF_VERSION:-OLD_VERSION}"`:
```bash
VERSION="${AGF_VERSION:-NEW_VERSION}"
```
Também atualizar comentário no topo: `AGF_VERSION=OLD_VERSION` → `AGF_VERSION=NEW_VERSION`.

**`install.ps1`** — linha com `$Version = if ... { "OLD_VERSION" }`:
```powershell
$Version = if ($env:AGF_VERSION) { $env:AGF_VERSION } else { "NEW_VERSION" }
```
Também atualizar comentário no topo: `$env:AGF_VERSION = "OLD_VERSION"` → `$env:AGF_VERSION = "NEW_VERSION"`.

---

### 9. Commit + tag + push graph-flow-skills

```bash
cd ../graph-flow-skills
git add install.sh install.ps1
git commit -m "chore: bump agf to NEW_VERSION"
git tag vNEW_VERSION
git push origin main --tags
cd -
```

---

### 10. GitHub Release

```bash
DIST=dist-offline
VER=NEW_VERSION

gh release create "v${VER}" \
  --repo DiegoNogueiraDev/graph-flow-skills \
  --title "agf v${VER}" \
  --notes "## agf ${VER}

<!-- Preencher com highlights dos commits desde a versão anterior -->

### Instalação rápida
\`\`\`bash
# macOS/Linux
curl -fsSL https://graph-flow.cloud/install.sh | bash
# Windows (PowerShell)
irm https://graph-flow.cloud/install.ps1 | iex
\`\`\`" \
  "${DIST}/agf-offline-darwin-arm64-${VER}.tgz" \
  "${DIST}/agf-offline-darwin-arm64-${VER}.tgz.sha256" \
  "${DIST}/agf-offline-darwin-x64-${VER}.tgz" \
  "${DIST}/agf-offline-darwin-x64-${VER}.tgz.sha256" \
  "${DIST}/agf-offline-linux-x64-${VER}.tgz" \
  "${DIST}/agf-offline-linux-x64-${VER}.tgz.sha256" \
  "${DIST}/agf-offline-win32-x64-${VER}.tgz" \
  "${DIST}/agf-offline-win32-x64-${VER}.tgz.sha256" \
  "${DIST}/agf-offline-win32-arm64-${VER}.tgz" \
  "${DIST}/agf-offline-win32-arm64-${VER}.tgz.sha256"
```

Esperado: URL `https://github.com/DiegoNogueiraDev/graph-flow-skills/releases/tag/vNEW_VERSION`

---

### 11. Deploy no servidor

```bash
# Rsync do site (sem node_modules e .next)
rsync -avz --exclude 'node_modules' --exclude '.next' \
  -e "ssh -i ~/.ssh/copadomundo_ed25519" \
  ../graph-cloud-flow/ \
  deploy@13.140.162.224:/opt/graph-flow/

# Upload dos bundles 0.18.0 para o servidor
scp -i ~/.ssh/copadomundo_ed25519 \
  dist-offline/agf-offline-*-NEW_VERSION.tgz \
  dist-offline/agf-offline-*-NEW_VERSION.tgz.sha256 \
  deploy@13.140.162.224:/opt/graph-flow/public/releases/

# Build + restart remoto
ssh -i ~/.ssh/copadomundo_ed25519 deploy@13.140.162.224 "
  set -e
  cd /opt/graph-flow
  npm ci --prefer-offline
  npm run build
  cp -r .next/static .next/standalone/.next/static
  cp -r public .next/standalone/public
  pm2 restart graph-flow
"
```

Nginx serve bundles via alias: `/opt/graph-flow/.next/standalone/public/releases/`

---

### 12. Verificação pós-deploy

```bash
VER=NEW_VERSION

# 1. install.sh serve versão correta
curl -s https://graph-flow.cloud/install.sh | grep ^VERSION=
# Esperado: VERSION="NEW_VERSION"

# 2. Bundle acessível no servidor
curl -sI "https://graph-flow.cloud/releases/agf-offline-darwin-arm64-${VER}.tgz" | head -1
# Esperado: HTTP/2 200

# 3. Site online
curl -s -o /dev/null -w "%{http_code}" https://graph-flow.cloud
# Esperado: 200

# 4. GitHub Release com assets
gh release view "v${VER}" --repo DiegoNogueiraDev/graph-flow-skills --json assets --jq '.assets[].name' | sort
# Esperado: 10 arquivos (5 .tgz + 5 .sha256)
```

---

## Exit criteria

- [ ] `npm audit` zero HIGH/CRITICAL
- [ ] `dist-offline/` tem 5 `.tgz` + 5 `.sha256` com `NEW_VERSION`
- [ ] `agent-graph-flow`: `package.json` + manifest commitados e pushados
- [ ] `graph-cloud-flow`: install.sh, install.ps1, releases/page.tsx commitados e pushados
- [ ] `graph-flow-skills`: install.sh, install.ps1 commitados, tag `vNEW_VERSION` pushada
- [ ] GitHub Release `vNEW_VERSION` com 10 assets
- [ ] `curl https://graph-flow.cloud/install.sh | grep VERSION` → `NEW_VERSION`
- [ ] Bundles no servidor: HTTP 200
- [ ] PM2 status: `online`

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Salvar memória

```bash
agf memory write publish-NEW_VERSION --content "v${VER} publicado em $(date +%Y-%m-%d). Bundles: darwin-arm64/x64, linux-x64, win32-x64/arm64. GitHub Release: DiegoNogueiraDev/graph-flow-skills/releases/tag/vNEW_VERSION"
```

## Related Skills

- `[[humble-continuous-delivery]]` — deployment pipeline gates, Blue-Green rollback, release vs. deploy distinction
- `[[swe-at-google]]` — rollbacks require review, build once deploy many, automated upgrades

Loop: publicado → próximo: graph-listening (retrospectiva + seed do próximo ciclo).

---

## graph-quality

---
name: graph-quality
description: Code quality + refactoring audit — Clean Code, SOLID, DRY, McCabe, SQALE, dead code, KISS/YAGNI
trigger: /graph-quality
tools_used: [insights, quality, node, memory]
tokens: ~800
---
<!-- shared:principles,errors -->

# graph-quality

Code quality audit + tech-debt management. 7 Clean Code dimensions + SQALE for debt.

## When
- After IMPLEMENT, before REVIEW
- During refactoring to measure improvement
- `$graph-quality` or "quality audit", "code review", "refactor"

## Flow
```
lint → typecheck → complexity → SOLID → DRY → dead code → SQALE → plan → report → agf memory write
```

## Steps

### 1. Lint + TypeCheck Gate
`npm run lint && npx tsc --noEmit` — fail → fix first.

### 2. Complexity Scan (McCabe)
`agf quality` — cyclomatic complexity per file/function.

| Complexity | Level | Action | Rationale |
|-----------|-------|--------|-----------|
| ≤5 | Simple | None | Fits in working memory as one unit |
| 6-10 | Moderate | Monitor | Fowler: "single function, but worth watching" |
| 11-20 | High | Schedule refactor | Nesting depth ≥4 probable; Extract Function candidate |
| >20 | Critical | Refactor immediately | "Impossible to test all paths" (McCabe 1976) |

Also flag: functions >50 lines (Extract Method candidate), parameters >5 (Introduce Parameter Object), files >500 lines (split module). Why 50 lines? Fowler: whenever you feel the urge to comment a block, that block deserves an extracted, named function instead.

### 3. SOLID Audit — Smell Mapping

| Principle | Check | Smell Signal | Fowler Refactoring |
|-----------|-------|-------------|-------------------|
| **S** Single Responsibility | Classes >200 lines? Multiple reasons to change? | Divergent Change | Extract Class |
| **O** Open/Closed | New features require editing vs extending? | Repeated Switches | Replace Conditional with Polymorphism |
| **L** Liskov | Subclasses break parent contracts? | Refused Bequest | Replace Subclass with Delegate |
| **I** Interface Segregation | Interfaces with unused methods? | Data Class / Fat Interface | Extract Interface |
| **D** Dependency Inversion | High-level depends on low-level? | Feature Envy | Introduce Interface / Inject dependency |

### 4. Smell → Refactoring Catalog

Top 12 smells. Each maps to a SOLID violation and a named Fowler move:

| Smell | Example | Refactoring | SOLID Violation |
|-------|---------|-------------|----------------|
| Long Function | >50 lines, comment blocks | Extract Function | SRP |
| Large Class | >200 lines, unrelated fields | Extract Class | SRP |
| Divergent Change | Class edited for DB *and* pricing | Extract Class, Split Phase | SRP |
| Shotgun Surgery | 1 change → edits in 8 files | Move Function, Combine into Class | SRP |
| Feature Envy | Method uses another class's data more | Move Function | SRP, DIP |
| Repeated Switches | Same switch in 3 places | Replace Conditional with Polymorphism | OCP |
| Speculative Generality | Abstract class with 1 subclass | Collapse Hierarchy, Inline Class | OCP (over-applied) |
| Refused Bequest | Subclass ignores 80% of parent | Replace Subclass with Delegate | LSP |
| Data Class | Only getters/setters, no behavior | Move Function toward the data | ISP |
| Long Parameter List | >5 params, caller must track all | Introduce Parameter Object | ISP |
| Data Clumps | Same 3 fields appear everywhere | Extract Class | DIP |
| Middle Man | Class mostly delegates | Remove Middle Man, Inline Function | DIP |

> Cross-ref: `[[fowler-refactoring]]` ch03 for full smell descriptions, ch06-ch12 for mechanics.

### 5. DRY Analysis
`agf quality` — duplicated blocks (>6 similar lines). Target < 3% duplication.
Three DRY violation types to flag: inadvertent (derived value stored twice), impatient (copy-paste), interdeveloper (same utility in two modules).

### 6. Dead Code Detection
Find: unimported exports, uncalled functions, unreferenced files, unreachable branches. `agf insights` for cross-refs.
Pragmatic Programmer Broken Window rule: dead code is a broken window — it signals "nobody cares" and invites further decay. Remove immediately or board it up with a dated TODO.

### 7. SQALE Tech Debt
**Debt ratio formula**: `debt_ratio = Σ remediation_mins / (LOC × 0.5min)`

| Grade | Debt Ratio | Action |
|-------|-----------|--------|
| A | <5% | Healthy — maintain |
| B | 6-10% | Monitor — address in next sprint |
| C | 11-20% | Warn — allocate 20% capacity |
| D | 21-50% | High — dedicated cleanup sprint |
| F | >50% | Critical — block new features |

Convert findings to remediation minutes: Long Function XS=30m, Large Class M=4h, Architecture violation L=8h+.
Prioritize by hotspot: `git log --format=format: --name-only --since="90 days" -- src/ | sort | uniq -c | sort -rn | head -20`. High churn + high debt = top priority.

### 8. KISS/YAGNI
Detect: over-engineering (factories for 1 impl), premature abstractions, excess config for unplanned features, generalizations without ≥2 concrete uses.
YAGNI test: "Does this complexity serve a *current* requirement?" — Pragmatic Programmer Tip 47.

### 9. Refactoring Priority Matrix

Broken Window Theory (Pragmatic Programmer): one sign of neglect triggers further decay. Use this matrix to triage:

| Impact ↓ / Effort → | XS (< 1h) | S (1-4h) | M (4-16h) | L (>16h) |
|---------------------|-----------|----------|-----------|----------|
| **Critical** (security, data loss) | Do now | Do now | Sprint 0 | Sprint 0 |
| **High** (hot file, daily pain) | Do now | This sprint | Next sprint | Plan+break up |
| **Medium** (occasional friction) | Litter-pickup | Backlog | Backlog | Defer |
| **Low** (cosmetic, rare code) | Opportunistic | Skip | Skip | Skip |

Fowler's four refactoring types to schedule by type:
- **Preparatory** — before adding a feature ("make the change easy, then make the easy change")
- **Comprehension** — while reading ("rename to record understanding")
- **Litter-pickup** — campsite rule ("leave it slightly better")
- **Planned** — dedicated session for M/L items only

### 10. Refactoring Plan
Per item: priority, effort (XS-XL), risk. `agf node add` (type task, tag refactor).
Two Hats rule: never mix refactoring with feature work in the same commit (`[[fowler-refactoring]]` ch02).

### 11. Quality Report
Score per dimension (0-100): Lint 15%, Type Safety 15%, Complexity 15%, SOLID 15%, DRY 10%, Dead Code 10%, Conventions 10%, SQALE 10%. Grade A≥85, B≥70, C≥55, D<55.

## Exit
- [ ] Lint + typecheck pass
- [ ] Complexity hotspots identified (McCabe >10)
- [ ] Dead code mapped and flagged (Broken Window check)
- [ ] Smell → refactoring plan in catalog terms
- [ ] Refactoring plan as graph tasks (via `agf node add`)
- [ ] SQALE debt ratio calculated with A-F grade
- [ ] Report saved via `agf memory write`

Loop: quality clean → next: graph-review.

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Cross-References
- `[[fowler-refactoring]]` — Two Hats, smell catalog (ch03), refactoring mechanics (ch06-ch12)
- `[[pragmatic-programmer]]` — Broken Window Theory, DRY taxonomy, YAGNI (Tip 47)

---

## graph-quality-assurance

---
name: graph-quality-assurance
description: Code quality audit using Clean Code (Uncle Bob), SOLID principles, DRY analysis, McCabe complexity, and project convention checks
triggers:
  - graph-quality-assurance
version: 1.1.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-quality-assurance

Code quality audit using Clean Code (Uncle Bob), SOLID principles, DRY analysis, McCabe cyclomatic complexity, and project convention checks. Produces a scored report across 7 quality dimensions.

> **Scope split**: `graph-quality-assurance` focuses on human-reviewable quality — readability, naming, conventions, review checklist. `graph-quality` focuses on automated metrics — SQALE score, duplication %, complexity distribution.

## When to Use

- After IMPLEMENT phase, before REVIEW phase
- During refactoring to measure improvement
- When code quality is a concern or technical debt is accumulating
- The user says "quality audit", "code review", "check quality", or "clean code"

## Mandatory Flow

```
lint → typecheck → code smells → SOLID → DRY → complexity → conventions → report → write_memory
```

## Workflow

### Step 1: Lint Gate

Run `npm run lint`. Verify zero errors, warnings ≤ 9 threshold, no new violations.
Score: 100 baseline, -10 per error, -2 per warning over threshold.

### Step 2: Type Safety Gate

Run `npm run typecheck`. Verify zero TypeScript errors, no `@ts-ignore` without approval, no `any` in production.
Score: 100 baseline, -5 per error, -10 per `any` in production code.

### Step 3: Code Smells Detection

Analyze modified/new files for common code smells:

| Smell | Threshold | Severity |
|-------|-----------|----------|
| Long functions | > 50 lines | High |
| Deep nesting | > 3 levels | High |
| God classes | > 300 lines | High |
| Feature envy | Method uses more data from another class than its own | Medium |
| Data clumps | Same group of params repeated in 3+ functions | Medium |
| Primitive obsession | Using primitives instead of domain types | Low |
| Dead code | Unused exports, unreachable branches | Medium |
| Commented-out code | Code blocks in comments | Low |

Score: 100 baseline, -5 per low, -10 per medium, -15 per high smell found.

#### Smell Priority Matrix

Not all smells are equal. Prioritize by cost:

| Priority | Smells | Action |
|----------|--------|--------|
| **Fix immediately** | Long functions, deep nesting, dead code, god classes | Block merge if new; fix before next sprint if existing |
| **Fix in current sprint** | Feature envy, data clumps, commented-out code | Address in same PR or follow-up within sprint |
| **Accept or defer** | Primitive obsession, magic numbers in tests | Track as low-priority debt; revisit during refactoring cycles |

Trigger: if a "fix immediately" smell appears in code written *this session*, it must be resolved before writing the quality report.

### Step 4: SOLID Principles Check

Evaluate modified modules against SOLID:

| Principle | Check | How to Verify |
|-----------|-------|---------------|
| **S** — Single Responsibility | One reason to change per module | Count distinct responsibilities; flag if > 1 |
| **O** — Open/Closed | Extend via composition, not modification | Check for switch/if chains that grow with new types |
| **L** — Liskov Substitution | Subtypes substitutable for base types | Verify interface implementations don't throw unexpected errors |
| **I** — Interface Segregation | No fat interfaces | Flag interfaces with > 7 methods or unused method implementations |
| **D** — Dependency Inversion | Depend on abstractions, not concretions | Check for direct instantiation of dependencies vs injection |

Score: 20 points per principle adhered to (100 max). -10 per violation found.

### Step 5: DRY Analysis

Scan modified files for identical/near-identical blocks (> 5 lines), copy-paste candidates, and string literals repeated > 3 times without constants.
Score: 100 if no duplication, -10 per duplicated block, -5 per repeated literal.

### Step 6: Complexity Gate

Count decision points (`if`, `else if`, `case`, `while`, `for`, `&&`, `||`, `catch`, `?:`) per function:

| Range | Rating | Action |
|-------|--------|--------|
| 1-5 | Low | No action |
| 6-10 | Moderate | Monitor |
| 11-20 | High | Flagged — simplify |
| > 20 | Very High | Required decomposition |

Score: 100 if all ≤ 10, -5 per function 11-20, -15 per function > 20.

### Step 7: Convention Compliance

**Auto-enforced (linter/formatter catches these — do not spend review time here):**

| Convention | Rule |
|------------|------|
| Formatting | Prettier / eslint --fix |
| Import order | ESLint import plugin |
| File naming | Kebab-case enforced by linter rule |

**Manual-check (human review required):**

| Convention | Rule | Check |
|------------|------|-------|
| Type naming | PascalCase | `GraphNode`, `NodeStatus` |
| Function naming | camelCase | `findNextTask()`, `buildTaskContext()` |
| Zod imports | From `'zod/v4'` | Never from `'zod'` |
| Exports | Named only | No `export default` |
| Logging | Project logger | No `console.log` in production code |
| Errors | Typed errors | No raw `throw "string"` or `throw new Error("msg")` without custom class |

> **Principle (SWE@Google ch8):** Rules that can be automatically checked must be automatically checked. Human review time is too expensive to spend on formatting debates.

Score: 100 baseline, -5 per manual-check violation (auto-enforced items are not scored here — the linter gate handles them).

### Step 8: Code Review Checklist

Apply the four-pillar review before marking work complete. From [[swe-at-google]] ch9:

| Pillar | Questions to Answer |
|--------|---------------------|
| **Correctness** | Does the code do what it claims? Are edge cases handled? Are errors propagated, not swallowed? |
| **Tests** | Do tests exist for every new behavior? Do they fail when the code is wrong? Are they testing behavior, not implementation? |
| **Design** | Is the change self-contained? Could it be smaller? Does it introduce a layering violation? |
| **Documentation** | Can a new team member understand this in 5 minutes? Are public APIs commented? Are non-obvious decisions explained inline? |

> **Readability standard (SWE@Google readability program):** Three-question test before approving:
> 1. Would a new team member understand what this module does without asking the author?
> 2. Would they know where to add the next piece of related logic?
> 3. Would they understand *why* this approach was chosen over the alternatives?
>
> If any answer is "no," request clarification or restructuring — not just a comment.

### Step 9: Quality Report

Calculate overall score and grade:

| Dimension | Weight | Score |
|-----------|--------|-------|
| Lint | 15% | 0-100 |
| Type Safety | 15% | 0-100 |
| Code Smells | 15% | 0-100 |
| SOLID | 15% | 0-100 |
| DRY | 10% | 0-100 |
| Complexity | 15% | 0-100 |
| Conventions | 15% | 0-100 |

**Grades:** A (85-100), B (70-84), C (55-69), D (40-54), F (< 40).

Save report:
```
Tool: mcp__mcp-graph__write_memory
Params:
  title: "Quality Audit — <date>"
  content: "<scores per dimension, overall grade, top issues, recommendations>"
  tags: ["quality", "audit", "clean-code", "solid"]
```

## Output Format

```
Phase: QUALITY ASSURANCE
Lint:        score/100 (N errors, N warnings)
Type Safety: score/100 (N errors, N any-types)
Code Smells: score/100 (N high, N medium, N low)
SOLID:       score/100 (N violations)
DRY:         score/100 (N duplications)
Complexity:  score/100 (N functions > 10, N functions > 20)
Conventions: score/100 (N violations)

Overall: score/100 — Grade X
Top Issues: <top 3 findings>
Recommendations: N action items

Saved to memory: "Quality Audit — <date>"
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT ignore lint warnings — they indicate real issues that compound over time
- Do NOT use `@ts-ignore` without explicit user approval — fix the type error instead
- Do NOT skip typecheck — type safety is a core project requirement
- Do NOT add `console.log` — use the project logger from `src/core/utils/logger.ts`
- Do NOT create functions > 50 lines without decomposing — extract helpers
- Do NOT use `any` type — use `unknown` with type guards or proper generics
- Do NOT skip convention checks for "quick fixes" — conventions prevent accumulated tech debt
- Do NOT debate formatting in review — auto-enforce it and spend human time on design and correctness

## Cross-References

- [[swe-at-google]] — ch8 (style guides as laws), ch9 (four review pillars, readability program)
- [[pragmatic-programmer]] — Broken Window Theory (ch1), DRY taxonomy (ch2), Ubiquitous Automation (ch8)
- [[fowler-refactoring]] — Smell catalog (ch3), Two Hats discipline, Design Stamina Hypothesis

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-refactor

---
name: graph-refactor
description: Tech debt management and refactoring audit using SQALE method, complexity analysis, dead code detection, and KISS/YAGNI/DRY enforcement
triggers:
  - graph-refactor
version: 2.0.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-refactor

Tech debt management and refactoring audit using SQALE method, complexity analysis, dead code detection, and KISS/YAGNI/DRY enforcement. Identifies code that is too complex, duplicated, unused, or over-engineered, and produces a prioritized refactoring plan tracked in the execution graph.

## When to Use

- During LISTENING phase — track tech debt for future sprints
- Before major features — reduce complexity to make new code easier to add
- When code quality score drops below B — systematic cleanup needed
- At sprint boundaries — allocate 15-20% of capacity for tech debt reduction

## Mandatory Flow

```
complexity scan → dead code detection → duplication analysis → KISS/YAGNI audit → tech debt scoring → refactoring order → test verification → report → write_memory
```

## Workflow

### Step 1: Complexity Scan

Measure cyclomatic complexity per function. Use `mcp__mcp-graph__code_intelligence` for symbol-level analysis.

| Complexity | Level | Action |
|-----------|-------|--------|
| 1-5 | Simple | No action |
| 6-10 | Moderate | Monitor |
| 11-20 | Warning | Schedule refactor |
| >20 | Critical | Refactor immediately |

Also flag: nesting >3 levels, functions >50 lines, parameters >5, files >500 lines.

### Step 2: Dead Code Detection

- Unused exports, unreachable code, commented-out blocks (>3 lines), unused imports, unused variables.
- Broken Window: dead code signals "nobody cares" — remove or board up with dated TODO.

```bash
npx eslint src/ --rule '{"no-unused-vars":"error","no-unreachable":"error"}'
```

### Step 3: Duplication Analysis

Detect blocks >10 lines appearing in multiple files. Target: <3% duplication.
DRY violation types: inadvertent (stored twice), impatient (copy-paste), interdeveloper (same utility twice).

### Step 4: KISS/YAGNI Audit

Flag: single-impl interfaces, abstract classes with one subclass, unused config flags, functions with zero callers, speculative code paths.
Ask: "Does this complexity serve a *current* requirement?" If not → remove.

### Step 5: Tech Debt Scoring (SQALE)

**Full formula:**
```
debt_ratio = Σ remediation_time / (LOC × 30min)
```

| Grade | Debt Ratio | Meaning |
|-------|-----------|---------|
| A | <5% | Healthy |
| B | 6-10% | Manageable — address in next sprint |
| C | 11-20% | Concerning — allocate 20% capacity |
| D | 21-50% | High — dedicated cleanup sprint |
| E | >50% | Critical — new features blocked |

Debt categories:
| Category | Difficulty | Examples |
|----------|-----------|----------|
| Architecture | Hard | Circular deps, layer violations, module boundaries |
| Design | Medium | Missing interfaces, tight coupling, wrong abstractions |
| Code | Easy | Long functions, magic numbers, naming, duplication |

Hotspot analysis (files with high churn AND high debt = top priority):
```bash
git log --format=format: --name-only --since="90 days" -- src/ | sort | uniq -c | sort -rn | head -20
```

### Step 6: Refactoring Order

Never refactor randomly. Apply this sequence — it matches both Feathers' legacy code loop and Fowler's four refactoring types.

**Feathers' Legacy Code Loop** (`[[feathers-legacy-code]]`):
1. Find a seam (Object Seam preferred — where behavior depends on which object receives the call)
2. Break the dependency at the seam's enabling point
3. Get code into a test harness (Characterization Tests document what code *actually does*)
4. Then refactor with confidence

**Fowler's Four Refactoring Types** (`[[fowler-refactoring]]` ch02), in priority order:
1. **Preparatory** — before a feature: "Make the change easy, then make the easy change" (Kent Beck)
2. **Comprehension** — while reading: rename to record understanding, small cleanups
3. **Litter-pickup** — campsite rule: leave it slightly better than you found it
4. **Planned** — scheduled session for M/L items only; rare, short, tracked as tasks

### Step 7: Two Hats Rule

**Never mix refactoring with behavior change.** (`[[fowler-refactoring]]` ch02 — Fowler's core discipline)

- Refactoring hat: change code structure, no new capabilities, tests stay green at every small step
- Feature hat: extend behavior, add new tests, leave structure alone
- Rule: wear one hat at a time; commit structural work before switching hats
- Signal: if you catch yourself writing a new test for new behavior *while* restructuring → stop, commit, switch hats

Practical enforcement:
- Refactoring commits: `refactor: extract pricing logic into PriceCalculator`
- Feature commits: `feat: add volume discount tier`
- Mixed commits = violation — split them

### Step 8: Seam Model (for Untested Code)

When a refactoring target has no tests, use Feathers' Seam Model to break dependencies before refactoring. (`[[feathers-legacy-code]]` ch04)

**Three seam types, in preference order:**

| Seam Type | How It Works | Enabling Point | Use When |
|-----------|-------------|----------------|----------|
| **Object Seam** | Method call behavior depends on which object receives it | Object creation site (constructor, factory, parameter) | Always prefer this first |
| **Link Seam** | Entire class/library resolved at link time | Build configuration | Pervasive dependency spanning many files |
| **Preprocessing Seam** | C/C++ macro replaces text before compile | `#define` / `#ifdef` | Last resort; invisible to code readers |

**Object Seam workflow:**
1. Identify the call you want to fake
2. Make it receivable on a parameter (Parameterize Constructor or Parameterize Method)
3. Pass a fake through the parameter in tests
4. Write Characterization Tests against the real behavior
5. Now refactor safely

### Step 9: Refactoring Catalog

Per finding, select the specific Fowler move:

| Pattern | Refactoring | Effort |
|---------|-------------|--------|
| Long function | Extract Function | XS-S |
| Deep nesting | Guard Clauses / Early Return | XS |
| Duplicate code | Extract Shared Utility | S-M |
| Large class/file | Extract Class, Split Module | M |
| Complex conditional | Replace Conditional with Polymorphism | M-L |
| God object | Decompose into focused modules | L |
| Tight coupling | Introduce Interface / Dependency Injection | M-L |
| Feature Envy | Move Function to where the data lives | S |
| Repeated Switches | Replace Conditional with Polymorphism | M |
| Data Clumps | Extract Class, Introduce Parameter Object | S |

Create graph nodes for M/L refactorings:
```
Tool: mcp__mcp-graph__node (action: "add", type: "task", tags: ["tech-debt", "<category>"])
```

### Step 10: Test Verification

Before ANY refactoring move:
- Tests green? If not, fix tests first — do not refactor into a broken baseline
- No tests? Write Characterization Tests first (Feathers' algorithm: assert dummy value → let failure reveal actual output → pin that as expected)
- Shallow tests? Add edge cases covering paths the change will touch
- Run: `npm test` — must be green before first structural change

Safety protocol (Fowler):
1. Run tests — green
2. Make one named refactoring move
3. Run tests — green
4. Commit with refactoring name in message
5. Repeat

### Step 11: Debt Report

**Scoring:**
- **A (90-100):** Low complexity, no dead code, minimal duplication, debt ratio <5%
- **B (75-89):** Some moderate complexity, minor duplication, debt ratio 5-10%
- **C (60-74):** Several complex functions, noticeable duplication, debt ratio 10-20%
- **D (45-59):** High complexity, significant dead code, debt ratio 20-50%
- **F (< 45):** Critical tech debt, pervasive duplication, debt ratio >50%

Save findings:
```
Tool: mcp__mcp-graph__write_memory (title: "Tech Debt Audit — <date>", content: <report>)
```

## Output Format

```
Phase: TECH DEBT AUDIT
Complexity: <N> functions >10 (<N> critical >20), avg complexity: <N>
Dead Code: <N> unused exports, <N> unreachable blocks, <N> commented blocks
Duplication: <N>% estimated duplication, <N> duplicate patterns found
KISS/YAGNI: <N> over-engineered patterns detected
SQALE Debt Ratio: <N>% (architecture: <N>h, design: <N>h, code: <N>h) → Grade <A-F>
Seam Model: <N> untested refactoring targets needing test harness first
Two Hats violations: <N> (mixed refactor+feature commits detected)
Top 5 Refactoring Candidates:
  1. [<effort>] <Fowler move name> — <file>
  ...
Test Safety: <N>/<M> candidates have tests (<N> need Characterization Tests first)
Overall Grade: <A-F> (<N>/100)
Graph Nodes Created: <N> tech-debt tasks
Saved to memory: "Tech Debt Audit — <date>"
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT refactor without tests — write Characterization Tests first, then refactor
- Do NOT refactor during bug fixes or feature work — Two Hats: separate commits, separate concerns
- Do NOT mix behavior change with structural change in the same commit
- Do NOT chase 100% — diminishing returns after 80%; focus on high-churn hotspots
- Do NOT refactor code that works and rarely changes — hotspots first
- Do NOT plan large refactors as one task — break into atomic steps tracked in the graph
- Do NOT skip the Seam Model for untested code — breaking dependencies safely requires a seam

## Cross-References

- `[[fowler-refactoring]]` — Two Hats (ch02), smell catalog (ch03), refactoring mechanics (ch06-ch12), Preparatory Refactoring, Self-Testing Code prerequisite
- `[[feathers-legacy-code]]` — Seam Model (ch04), Characterization Tests (ch13), Sprout/Wrap (ch06), Legacy Code Change Algorithm

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-review

---
name: graph-review
description: Execute the REVIEW phase of the lifecycle via the `agf` CLI — blast radius insights, code-aware sync, mermaid visualization, quality feedback
triggers:
  - graph-review
version: 2.1.0
author: Diego Nogueira
date: 2026-06-21
toolchain:
  - agf insights
  - agf export
  - agf metrics
  - agf gate
  - agf phase
---

# graph-review

Execute the REVIEW phase of the lifecycle, driven entirely by the `agf` CLI (ZERO MCP). Performs structured
code review across five dimensions, quantifies blast radius, scores code health, and gates the transition
to HANDOFF.

## When to Use

- After VALIDATE phase has confirmed all tests pass
- Reviewing code changes before creating PR
- Analyzing blast radius of changes
- The current phase reported by `agf phase` is `REVIEW`

## Mandatory Flow

```
agf insights (impact) → agf insights (code_sync) → agf export --format mermaid → agf metrics → [review dimensions + LGTM checklist] → agf gate review → agf phase HANDOFF
```

## Review Dimensions

Every change must be assessed across these five lenses before LGTM. Answer Y/N for each:

| # | Dimension | Question |
|---|-----------|----------|
| 1 | **Correctness** | Does the code do what it claims? Are edge cases handled? |
| 2 | **Tests** | Do tests verify real behavior, not just coverage? Are they independently runnable? |
| 3 | **Design** | Does this fit the architecture decided in ADRs? Does it respect existing interfaces? |
| 4 | **Code Health** | Is the codebase left measurably better (or at least no worse) than before this change? |
| 5 | **Documentation** | Are new behaviors, interfaces, and non-obvious decisions explained? |

Any N blocks LGTM. Route back to IMPLEMENT/VALIDATE to fix before advancing.

→ From `[[swe-at-google]]` ch9: code review's primary purpose is not bug detection but ensuring
  comprehension, consistency, and shared ownership over time.

## Blast Radius Formula

Blast radius quantifies the risk surface of a change before it ships.

```
blast_radius = LOC_changed × dependency_fan_out × (1 - test_coverage_ratio)
```

| Variable | Source |
|----------|--------|
| `LOC_changed` | `git diff main...HEAD --stat \| tail -1` |
| `dependency_fan_out` | modules that import changed modules, from `agf insights` |
| `test_coverage_ratio` | fraction of changed lines covered by tests (0.0–1.0) |

**Severity thresholds:**

| Score | Severity | Action |
|-------|----------|--------|
| 0–50 | Low | Proceed |
| 51–200 | Medium | Flag in output; ensure tests cover changed paths |
| 201–500 | High | Require explicit risk acknowledgment before LGTM |
| > 500 | Critical | Block; decompose change or increase coverage first |

Run `agf insights` to get `dependency_fan_out` — do not guess transitive dependencies manually.

## Workflow

### Step 1: Blast Radius Analysis

```bash
agf insights
```

Get upstream/downstream dependents for each modified module. Apply the Blast Radius Formula above.
Record the numeric score and severity in the output block.

### Step 2: Code-Aware Sync Check

```bash
agf insights
```

Detect stale sourceRefs, missing testFiles, and symbol drift. Fix all issues before proceeding — stale
refs cause confusion in future sprints.

### Step 3: Visualize Graph State

```bash
agf export --format mermaid
```

A good dependency visualization must:
- Show any **cycles** (cycles = hidden coupling, block LGTM if new cycles appear)
- Confirm the blast radius nodes are visible and correctly connected
- Reflect the actual post-change state (re-export after fixes)

### Step 4: Collect Metrics

```bash
agf metrics
```

Review velocity, quality (AC pass rates), complexity (task sizes, dependency depth).

### Step 5: Structured Code Review

```bash
git diff main...HEAD
git log main..HEAD --oneline
```

Apply the five **Review Dimensions** above. Check:
- ADR compliance — design decisions from DESIGN phase respected
- Security (OWASP Top 10 — injection, auth, exposure, etc.)
- Error handling completeness
- No new cycles introduced (confirmed via mermaid visualization)

### Step 6: Code Health Gate

A change passes the Code Health Gate when **all three** hold:

1. **No net regression** — complexity, coverage, and dependency fan-out are not worse than before.
2. **Campsite Rule** — at least one small improvement was made beyond the minimum required change
   (better name, extracted function, removed dead code). *(From `[[fowler-refactoring]]`: always leave
   the code slightly better than you found it.)*
3. **No new cycles** — mermaid visualization shows no dependency cycles introduced by this change.

Binary: **PASS** or **FAIL**. A FAIL here blocks LGTM regardless of other checks.

### Step 7: Knowledge Quality Feedback

Use `agf search "<q>"` to inspect RAG knowledge store. Flag stale or misleading entries for cleanup.
Record in `agf memory write` so future retrieval improves.

### Step 8: LGTM Checklist

LGTM means "I have verified this change is correct enough to proceed to HANDOFF." All five must be true:

- [ ] All five Review Dimensions answered Y
- [ ] Blast radius score computed and within acceptable severity (or risk acknowledged)
- [ ] Code Health Gate: PASS
- [ ] No new dependency cycles (mermaid confirmed)
- [ ] ADR decisions from DESIGN phase respected

If any item is unchecked, do not issue LGTM. Return to the appropriate phase.

→ From `[[swe-at-google]]` ch9: LGTM is a permission bit — it means correctness and comprehension have
  been verified, not just "I skimmed it." Seek the minimum number of reviewers needed; rubber-stamping
  adds noise without quality signal.

### Step 9: Validate Gate

```bash
agf gate review
```

**Gate criteria:**
- All sprint tasks validated
- Blast radius analyzed and severity recorded
- Code sync clean (no stale refs)
- LGTM checklist complete
- Metrics within acceptable ranges

### Step 10: Transition

```bash
agf phase HANDOFF
```

Follow the `nextAction` reported by `agf phase`.

## Output Format

```
Phase: REVIEW → HANDOFF
Blast radius: score=<N> severity=<Low|Medium|High|Critical> (LOC=X fan_out=Y coverage=Z)
Review dimensions: Correctness=Y/N Tests=Y/N Design=Y/N CodeHealth=Y/N Docs=Y/N
Code health gate: PASS/FAIL
Cycles: none / [list new cycles if any]
LGTM: YES / NO (reason if NO)
Code sync: M stale refs, K missing testFiles — fixed/pending
Gate: review_ready — score N/100, grade X
Status: Ready to proceed to HANDOFF / Blocked (reason)
```

## Anti-Patterns

- Do NOT skip `agf insights` blast radius — manual analysis misses transitive dependencies
- Do NOT ignore code_sync warnings — stale refs cause confusion in future sprints
- Do NOT rubber-stamp reviews — each Review Dimension must be explicitly verified
- Do NOT skip ADR compliance — design decisions exist for a reason
- Do NOT issue LGTM when any LGTM checklist item is unchecked
- Do NOT accept a new dependency cycle without explicit justification and a plan to remove it
- Do NOT forget to flag stale RAG knowledge — it degrades future retrieval quality

## Codex Notes

- In Codex Plan Mode, use this skill for planning only; do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for edits.

## Economy

Token economy is part of the loop: run `agf savings` / `agf metrics --economy-report` after each task,
then feed savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-security

---
name: graph-security
description: Security + dependency audit — OWASP Top 10, STRIDE, npm audit, secrets, SBOM, license, supply chain
trigger: /graph-security
tools_used: [insights, quality, memory]
tokens: ~800
---
<!-- shared:principles,errors -->

# graph-security

Security + dependency audit. OWASP Top 10, STRIDE, secrets scan, SBOM, license, supply chain.

## When
- Before DEPLOY — security gate mandatory
- After IMPLEMENT for auth, input handling, file I/O features
- `$graph-security` or "security audit", "check vulnerabilities", "dependency audit"

## Flow
```
npm audit → OWASP → secrets scan → STRIDE → input validation → path traversal → [deps: license → freshness → SBOM → supply chain] → report → agf memory write
```

## Steps

### 1. Dependency Vuln Scan
`npm audit --audit-level=high` — count CVEs by severity; flag no-fix packages.

**CVE Remediation SLA** (from [[swe-at-google]] Ch18/Ch23 gate policy):
| Severity | Action | Deadline |
|----------|--------|----------|
| Critical | Block deploy immediately | Fix before any merge |
| High | Fix required | Within 24 hours |
| Medium | Scheduled fix | Next sprint |
| Low | Backlog | Track in issues |

### 2. OWASP Top 10
| # | Category | Check |
|---|----------|-------|
| A01 | Broken Access Control | Auth guards on all routes? |
| A02 | Cryptographic Failures | Sensitive data in plaintext? |
| A03 | Injection | SQL/string interpolation in queries? |
| A04 | Insecure Design | Threat model? Input validation? |
| A05 | Misconfiguration | Security headers? Debug off? |
| A06 | Vulnerable Components | npm audit passed? |
| A07 | Auth Failures | Password strength? Rate limiting? |
| A08 | Integrity Failures | CI/CD supply chain? Checksums? |
| A09 | Logging & Monitoring | Audit trail? Alerts? |
| A10 | SSRF | URL fetching validates hosts? |

### 3. Secrets Detection
Run all three passes:
```bash
git secrets --scan
trufflehog filesystem .
grep -rn "sk-\|pk-\|ghp_\|gho_\|BEGIN.*PRIVATE KEY\|[A-Za-z0-9+/]{40,}" . \
  --include="*.ts" --include="*.js" --include="*.env*" --exclude-dir=node_modules
```
Patterns to flag: `(sk-|pk-|ghp_|gho_)`, `BEGIN.*PRIVATE KEY`, base64 blobs ≥ 40 chars, connection strings with embedded credentials.

### 4. STRIDE Binary Checklist
Each row requires Y/N — not open questions. (From [[pragmatic-programmer]] Tip 31: make implicit assumptions explicit.)
| Threat | Property | Y/N Check |
|--------|----------|-----------|
| Spoofing | Authentication | Is identity verified before every privileged action? |
| Tampering | Integrity | Are all writes validated and signed/checksummed? |
| Repudiation | Non-repudiation | Does an immutable audit log cover every critical action? |
| Info Disclosure | Confidentiality | Are logs, errors, and responses scrubbed of secrets? |
| Denial of Service | Availability | Is rate limiting enforced at every public entry point? |
| Elevation of Privilege | Authorization | Is privilege escalation blocked at the data layer? |

Any N = finding. All six must be Y to pass.

### 5. Input Validation
User input sanitization, XSS (escaping), SQL injection (parameterized queries), file upload (type/size/path traversal).

### 6. Path Traversal
Grep `path.join`, `path.resolve`, `fs.readFile` with user input. Flag vulns.

### 7. License Compliance
`npx license-checker --summary`. Allow: MIT, Apache-2.0, ISC, BSD-2/3. Deny: GPL (if incompatible), unlicensed, unauthorized proprietary.

### 8. Dependency Freshness
Score: latest 100, 1 major behind 70, 2+ behind 20, unmaintained 0. Target avg ≥ 70.

### 9. SBOM
`agf insights` — SPDX or CycloneDX. Include package, version, license, deps.

### 10. Supply Chain Defense
Four mandatory rules (from [[swe-at-google]] Ch18/Ch21 — One-Version Rule + hermetic builds):
1. **Pin versions**: exact versions in lockfile; no `"1.+"` or `"latest"` ranges in production deps.
2. **SBOM present**: generated SBOM includes package, version, license, hash for every dependency.
3. **Hermetic build check**: CI build must not fetch from the internet at build time; all deps resolved from lockfile.
4. **Maintainer risk**: flag packages with a single maintainer and no recent activity (unmaintained + typosquatting risk).

Also check: dependency confusion (private package names published to public npm), transitive dep with no owner on file.

### 11. Security Debt Policy
From [[pragmatic-programmer]] Tip 4 (Broken Windows): known security issues must be fixed or formally documented — never silently ignored.

Decision rule:
- **Fix it now** if severity is Critical or High (see CVE SLA above).
- **Document it** if Medium or Low: open a tracked issue with severity, description, affected surface, and mitigation plan. A comment in code pointing to the issue is required.
- **Never ignore**: undocumented known vulnerabilities are Broken Windows — they signal "nobody cares" and accelerate further decay.

## Exit
- [ ] npm audit: no Critical/High CVEs unaddressed
- [ ] OWASP Top 10 checklist complete
- [ ] 0 exposed secrets
- [ ] STRIDE binary checklist: all 6 = Y
- [ ] Supply chain: versions pinned, SBOM generated, maintainer risk assessed
- [ ] Security debt: all known issues fixed or formally tracked
- [ ] Report saved via `agf memory write`

Loop: security clean → next: graph-review.

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

## graph-tests

---
name: graph-tests
description: Test strategy audit using Test Pyramid, FIRST principles, coverage analysis, and test quality assessment
triggers:
  - graph-tests
version: 2.0.0
author: Diego Nogueira
date: 2026-06-21
---

# graph-tests

Test strategy audit using Test Pyramid, FIRST principles, coverage analysis, and test quality assessment. Identifies gaps in test coverage, validates pyramid shape, ensures TDD discipline, and applies canonical test double and smell detection from Khorikov, Meszaros, and Freeman & Pryce.

## When to Use

- After IMPLEMENT phase, to audit test quality before VALIDATE
- During VALIDATE phase, as part of comprehensive quality checks
- When test coverage is insufficient or declining
- Before major releases to ensure test confidence
- When onboarding new modules that lack test coverage

## Mandatory Flow

```
npm test --> coverage report --> pyramid check --> FIRST audit --> test double audit --> smell scan --> missing tests --> test quality --> edge cases --> report --> write_memory
```

## Workflow

### Step 1: Test Suite Gate

Run the full test suite. All tests must pass with zero failures.

```bash
npm test
```

If any test fails, STOP. Fix failures before proceeding. Never audit quality on a broken suite.

### Step 2: Coverage Report

```bash
npm run test:coverage
```

**Thresholds:**
- Statements: 70% | Branches: 65% | Functions: 70% | Lines: 70%

Report all files below threshold. Identify the top 5 modules with lowest coverage as priority targets.

### Step 3: Test Pyramid Check

Count tests by type to verify pyramid shape:

- **Unit tests:** `src/tests/*.test.ts` without database/store dependencies
- **Integration tests:** Tests using `SqliteStore`, in-memory database, or cross-module interactions
- **E2E tests:** `src/tests/e2e/*.test.ts` (Playwright browser tests)

**Healthy ratio target:** ~70% unit, ~20% integration, ~10% E2E.

Flag inverted pyramids where integration or E2E tests outnumber unit tests.

### Step 4: FIRST Scoring Rubric

Score each principle 0–100. Overall FIRST score = average.

| Principle | Criteria for 100 | Deductions |
|-----------|-----------------|------------|
| **Fast** | Every test < 1s; no `sleep`/`setTimeout`; no network calls | −20 per test > 1s; −30 for network I/O |
| **Independent** | Each test creates its own store/state; `beforeEach` resets; no shared mutable variables | −25 per shared-state leak found |
| **Repeatable** | Same result on every machine/run; no reliance on external services or file system; no `Date.now()` hardcoded | −30 for flaky test found |
| **Self-validating** | Clear assertions with descriptive messages; no console inspection needed; test passes = green, fails = red | −20 for undescribed assertion; −30 for "manual check" comment |
| **Timely** | Test exists in the same commit as the feature (TDD); no untested public functions in recently modified files | −10 per public function added without a corresponding test |

Score each principle 0–100. Overall FIRST score = average.

### Step 5: Test Double Decision Matrix

When code under test needs a collaborator, choose the right double (Meszaros taxonomy):

| Double | When to use | Assert on it? |
|--------|------------|---------------|
| **Dummy** | Parameter required but never used by the test's behavior | No |
| **Stub** | SUT needs a return value from a dependency (query); you don't care whether the call happened | No — never |
| **Spy** | You want to assert *after the fact* that a call occurred, without upfront expectations | Yes — in the Assert phase |
| **Mock** | You need pre-programmed expectations on *outgoing commands*; failure if call doesn't happen | Yes — verified automatically |
| **Fake** | You need a real working implementation (e.g., `:memory:` SQLite) without the real infrastructure cost | No |

**Decision rule (Khorikov):** Only mock **unmanaged dependencies** — services your application doesn't own and whose interactions are visible externally (SMTP, message bus, third-party APIs). Use real implementations (Fake/in-memory) for **managed dependencies** (SQLite store, in-process DB). Never mock intra-system calls between domain classes — those are implementation details.

**For this project:** Prefer `Fake` (`:memory:` SQLite via `SqliteStore`) for store tests. Use `Stub` for external API responses. Reserve `Mock` for verifying outgoing MCP tool calls.

### Step 6: Test Smell Catalog

Scan test files for these smells (Meszaros) and flag each one:

| Smell | Detection signal | Fix |
|-------|-----------------|-----|
| **Assertion Roulette** | Multiple assertions, none with messages; when one fails you can't tell which | One behavior per test, or add assertion messages |
| **Mystery Guest** | Test reads from a file, global, or preset DB row not declared in the test body | Move setup inline or into a named Creation Method |
| **Obscure Test** | Hard to understand the scenario in under 10 seconds | Inline the relevant context; use a Test Data Builder |
| **Eager Test** | One test exercises 3+ distinct behaviors | Split into single-behavior tests |
| **Erratic Test** | Passes sometimes, fails other times (flaky) | Fresh Fixture; remove shared mutable state; eliminate `Date.now()` hardcoding |
| **Fragile Test** | Breaks when production code is refactored but behavior is unchanged | Stop testing implementation details; test through public API only |
| **Interacting Tests** | One test's side effect corrupts the next | `beforeEach` reset; Transaction Rollback or fresh `:memory:` DB per test |
| **Hard-Coded Test Data** | Literal magic values with no context (`42`, `"abc"`, `user1`) | Named constants or factory helpers from `src/tests/helpers/factories.ts` |
| **Overspecified Software** | Mocks have expectations on every method call, including queries | `allowing(...)` for queries; `oneOf(...)` / `Verify` only for the one command under test |

### Step 7: London vs Classical School

Apply the right school per object type (Khorikov + GOOS):

| Object type | School | Strategy |
|-------------|--------|----------|
| Pure function / domain logic | **Classical** | No mocks; assert on return value |
| Domain object with state | **Classical** | Assert on state after act |
| Orchestrator (application service) calling unmanaged deps | **London** | Mock the external boundary; assert the command was sent |
| Orchestrator calling managed deps (SQLite store) | **Classical** | Use real in-memory store (Fake) |

**Decision rule:** If you'd write `expect(result).toBe(...)` on a return value → Classical. If correct behavior IS "it called X on Y with these args" → London. Never use London school for intra-system calls between domain classes.

### Step 8: Missing Test Detection

For each modified `.ts` file in `src/core/` and `src/mcp/`, check if a corresponding `.test.ts` exists in `src/tests/`.

```
Tool: mcp__mcp-graph__analyze (mode: "tdd_check")
```

List all public exported functions without corresponding test assertions.

### Step 9: Test Quality Check

- **AAA structure:** Each test has exactly one Arrange / one Act / one Assert block (blank lines between). Act section = exactly one line — if two lines are needed, fix the SUT's API.
- **No `if` in tests:** An `if` = two behaviors. Split the test.
- **Minimal mocks:** Prefer real instances (`:memory:` SQLite, temp files) over mocks for store tests.
- **Factory helpers:** Use `makeNode`, `makeEdge` from `src/tests/helpers/factories.ts`.
- **Descriptive names:** Plain English facts about behavior, not implementation (`returns_next_unblocked_task_sorted_by_priority`, not `getTask_validInput_returnsTask`).
- **No test pollution:** Proper `beforeEach`/`afterEach` cleanup; no leaked state.
- **Single behavior focus:** Each test verifies one coherent outcome.

### Step 10: Edge Case Coverage

For each function under test, verify coverage of:

- **Happy path:** Normal input → expected output
- **Error paths:** Invalid input, null, undefined, empty strings
- **Boundary conditions:** 0, −1, MAX_SAFE_INTEGER, empty arrays, single-element arrays
- **Async error handling:** Rejected promises, timeout scenarios, concurrent access
- **Type edge cases:** Optional fields missing, extra fields present

### Step 11: Test Report

```
Test Suite: <N> tests, <N> passed, <N> failed
Coverage: statements <N>%, branches <N>%, functions <N>%, lines <N>%
Pyramid: unit <N> / integration <N> / e2e <N> (ratio: <X>:<Y>:<Z>)
FIRST Score: <N>/100 (F:<N> I:<N> R:<N> S:<N> T:<N>)
Test Smells: <N> found — [list by type]
Test Double Issues: <N> violations (over-mocked managed deps, stub assertions)
Gaps: <N> modules without tests
Grade: <A-F>
```

**Grading:**
- **A (90–100):** All thresholds met, pyramid correct, FIRST > 80, no smells, no double violations
- **B (75–89):** Minor gaps, pyramid slightly off, FIRST > 65, ≤ 2 smells
- **C (60–74):** Coverage below threshold in some areas, pyramid inverted for some types
- **D (45–59):** Significant gaps, FIRST < 50, many smells, managed deps mocked
- **F (< 45):** Critical test debt, broken pyramid, widespread quality issues

Save findings:
```
Tool: mcp__mcp-graph__write_memory (title: "Test Audit Report — <date>", content: <report>)
```

## Output Format

```
Phase: TEST AUDIT
Tests: <N> passed, <N> failed
Coverage: <N>% statements, <N>% branches, <N>% functions, <N>% lines
Pyramid: unit:<N> integration:<N> e2e:<N>
FIRST Score: <N>/100
Test Smells: <N> found
Test Double Issues: <N> violations
Gaps: <N> modules without tests
Grade: <A-F>
Recommendations: <top 3 actions>
```

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

## Anti-Patterns

- Do NOT skip running the full test suite — a passing suite is the baseline for any audit
- Do NOT mock what you can use in-memory — prefer `:memory:` SQLite over mocks for store tests
- Do NOT assert on stubs — stub assertions (verifying that a query was called) are overspecification and produce false positives
- Do NOT mock intra-system calls between domain classes — these are implementation details; test state or return values instead
- Do NOT write tests after implementation — TDD first, always
- Do NOT use shared mutable state between tests — each test owns its state
- Do NOT ignore flaky tests — fix the root cause (Fresh Fixture, seed isolation, clock injection)
- Do NOT test implementation details — test behavior through the public API contract
- Do NOT skip edge cases for "happy path only" coverage — edge cases catch real bugs
- Do NOT put `if` statements in tests — split into separate test cases

## Key Takeaways

1. **FIRST score** measures test health numerically — use the rubric per-principle, not as a gut feeling.
2. **Test doubles:** Dummy (ignored), Stub (query input, never assert), Spy (recorded calls), Mock (command expectation), Fake (working lightweight impl). Pick based on whether you need a return value (Stub/Fake) or to verify a call happened (Mock/Spy). ([[meszaros-xunit-patterns]])
3. **Mock boundary:** Only mock unmanaged dependencies (SMTP, external APIs). Use real in-memory implementations for managed ones (SQLite store). Never mock intra-system class interactions. ([[khorikov-unit-testing]])
4. **Test smells are design signals:** Fragile tests → over-specification; Erratic tests → shared state; Mystery Guest → missing inline setup; Assertion Roulette → too many behaviors per test. ([[meszaros-xunit-patterns]])
5. **School selection:** Classical (pure functions, value objects, domain logic). London (application service → external boundary). Both styles coexist in the same codebase. ([[khorikov-unit-testing]], [[goos-tdd]])
6. **AAA is non-negotiable:** One Arrange, one Act (one line), one Assert block. A two-line Act reveals a broken SUT API. An `if` in a test means two tests are needed.
7. **Test pain = design signal:** Hard-to-test code reveals missing interfaces, overloaded responsibilities, or hidden dependencies. Fix the production code, not the test. ([[goos-tdd]])

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

---

## graph-validate

---
name: graph-validate
description: Execute the VALIDATE phase of the lifecycle via the `agf` CLI — unified validation, done integrity, scenario coverage, DORA quality metrics
triggers:
  - graph-validate
version: 2.1.0
author: Diego Nogueira
date: 2026-04-04
toolchain:
  - agf check
  - agf insights
  - agf forecast
  - agf metrics
  - agf gate
  - agf phase
---

# graph-validate

Execute the VALIDATE phase of the lifecycle, driven entirely by the `agf` CLI (ZERO MCP). Runs comprehensive validation: E2E tests, acceptance criteria verification, integrity checks, and quality metrics via DORA.

## Validation vs Verification (Opening Principle)

These are distinct activities and both are required before advancing:

- **Verification** = "Did we build it correctly?" — tests pass, code compiles, DoD checks green. Runs first.
- **Validation** = "Did we build the right thing?" — acceptance criteria met, user scenarios covered, AC is testable. Runs second.

Passing verification alone is not sufficient to exit VALIDATE. A task can have green tests yet fail validation if its AC cannot be traced to a verified behavior. See `[[swe-at-google]]` ch11: "coverage measures that a line was invoked, not that it was verified to behave correctly."

## When to Use

- After IMPLEMENT phase has completed a sprint's worth of tasks
- Verifying that all acceptance criteria are met across multiple tasks
- Running E2E tests that span multiple components
- The current phase reported by `agf phase` is `VALIDATE`

## Done Definition (7 Checks)

A task is "done" only when ALL 7 checks pass:

| # | Check | How to verify |
|---|-------|---------------|
| 1 | All unit + integration tests pass | `npx vitest run` exits 0 |
| 2 | All acceptance criteria are explicitly met | Each AC line maps to a passing test or manual log |
| 3 | No regressions introduced | Full suite green vs baseline |
| 4 | Code reviewed and LGTM | PR or self-review record exists |
| 5 | Documentation updated (CLAUDE.md / API docs / ADR) | Files modified or confirmed unchanged |
| 6 | Status flow was valid (went through `in_progress`) | `agf check <id>` status_flow = pass |
| 7 | No open blocking issues or flaky tests on the path | Test run shows 0 flakes, 0 blockers |

`agf check <task_id>` enforces all 7 checks. A task failing any check must return to IMPLEMENT.

## Scenario Coverage Minimum

"Enough" scenario coverage means at minimum four categories per feature:

1. **Happy path** — expected inputs produce expected outputs
2. **Error path × 3** — at least three distinct failure modes (invalid input, network/IO failure, auth/permission failure)
3. **Boundary** — edge of valid range (empty list, max length, zero, negative)
4. **Edge case** — combinations or ordering that are unusual but valid

`agf insights` reports scenario coverage. Gate blocks if any feature has only happy-path coverage.

## DORA Quality Gate

These thresholds must be met before `agf gate validate` can pass:

| DORA Metric | Target | Hard block? |
|-------------|--------|-------------|
| Change Failure Rate | < 5% (status reversals / done) | Yes — fix rework before advancing |
| Lead Time P85 | < 24h (created → done) | Advisory — flag for retro |
| MTTR | < 1h (mean time from rework open → closed) | Yes — open rework blocks gate |
| AC Pass Rate | ≥ 95% of tasks | Yes — failing tasks return to IMPLEMENT |

See `[[humble-continuous-delivery]]` for the deployment pipeline model: only builds that pass every gate reach the next stage.

## Mandatory Flow

```
agf check <id> (task) → agf check <id> (ac) → agf check <id> (done_integrity) → agf check <id> (status_flow) → agf insights (scenario_coverage) → agf forecast (dora) → agf metrics → agf gate validate → agf phase REVIEW
```

## Workflow

### Step 1: Identify Scope

```bash
agf kanban
```

Filter for current sprint `done` column.

### Step 2–3: Task + AC Validation (per task)

```bash
agf check <task_id>
```

Validates DoD (7 checks) and AC quality (INVEST scoring + measurability).

### Step 4: Run Full Test Suite

```bash
npx vitest run
npx vitest run tests/integration/
```

Verify: all unit + integration tests pass, zero regressions, zero flaky tests.

### Step 5–6: Done Integrity + Status Flow

```bash
agf check <id>
```

`done_integrity` — all `done` nodes meet 7-check DoD.  
`status_flow` — valid transitions (went through `in_progress`).

### Step 7: Scenario Coverage

```bash
agf insights
```

Must show happy path + ≥ 3 error paths + boundary + edge case per feature. Gate blocks on happy-path-only coverage.

### Step 8: DORA Quality Metrics

```bash
agf forecast
```

Apply thresholds from the DORA Quality Gate table above. Hard-block metrics must be resolved before Step 10.

### Step 9: Sprint Metrics

```bash
agf metrics
```

Review: task completion rate, AC pass rate, avg completion time vs estimates.

### Step 10: Validate Gate

```bash
agf gate validate
```

All 7-check DoD, DORA hard-block metrics, and scenario coverage must pass.

### Step 11: Transition

```bash
agf phase REVIEW
```

## Output Format

```
Phase: VALIDATE → REVIEW
Tasks validated: N/M passed
Tests: N passed, M failed
AC pass rate: X%
Scenario coverage: happy+3err+boundary+edge = Y/4 per feature
DORA: CFR Y%, lead time P85 Zh, MTTR Wh
Gate: validate_ready — score N/100, grade X
Status: Ready to proceed to REVIEW phase
```

## Anti-Patterns

- Do NOT conflate verification (tests pass) with validation (AC met) — both are required
- Do NOT skip E2E tests — unit tests alone are insufficient
- Do NOT mark validation as passed if tests fail — fix first
- Do NOT ignore flaky tests — treated as high-priority bugs (`[[swe-at-google]]` ch11)
- Do NOT validate tasks still `in_progress` — complete first
- Do NOT accept happy-path-only scenario coverage — the gate blocks it
- Do NOT ignore `nextAction` from `agf phase`

## Cross-References

- `[[swe-at-google]]` ch11 (Testing Overview) — test taxonomy, Beyoncé Rule, flaky tests
- `[[humble-continuous-delivery]]` — deployment pipeline gates, DORA metrics model

## Codex Notes

- In Codex Plan Mode, use this skill for planning only and do not mutate files.
- During implementation, follow the project `AGENTS.md` rules and use `apply_patch` for manual edits.

## Economy

Token economy is part of the loop: run `agf savings` / `agf metrics --economy-report` after each task, then feed savings → `agf learning` to calibrate the next turn (spiral, not circle).

**Remember:** every implementation's output to the external agent must be JSON, so it can use `--select` to reduce output→input and close the agentic loop.

---

<!-- agent-graph-flow:start -->
## agent-graph-flow (`agf`) — FutebolIA

Este projeto usa **agent-graph-flow** para gestão de execução via grafo persistente (SQLite).
Dados em `workflow-graph/graph.db` (local, gitignored). **Tudo via o CLI `agf` — zero MCP.**

### ⚠️ Regra de Execução OBRIGATÓRIA

**O grafo (`agf`) é a fonte de verdade ABSOLUTA. Nenhuma implementação acontece fora do grafo.**

1. **Node deve existir** — antes de escrever QUALQUER código, o node correspondente DEVE existir no grafo (`agf node add` ou `agf import-prd`).
2. **Fluxo obrigatório** — `agf start → [implementar com TDD] → agf done` (pipeline) ou `agf next → agf context <id> → [TDD] → agf check <id> → agf node status <id> done` (granular) — SEM EXCEÇÕES.
3. **Epic = estrutura primeiro** — `agf import-prd` (ou `agf node add` + `agf edge add`) cria Epic + tasks + edges ANTES de implementar.
4. **Status tracking** — `agf node status <id> in_progress` ANTES de codar, `agf node status <id> done` (ou `agf done <id>`) APÓS completar.
5. **Validação** — `agf check <id>` (DoD + AC + TDD) após cada task.
6. **Zero trabalho não-rastreado** — se não tem node no grafo, CRIAR PRIMEIRO.

> **Sem node no grafo = sem código escrito. Tudo via `agf` — zero MCP.**

### Comandos `agf` (CLI nativo — exponha 100%, zero MCP)

#### Front door (SHAPE → BUILD → SHIP)

| Comando | O que faz |
|---------|-----------|
| `agf deliver "<pedido>"` | Pipeline ponta-a-ponta: normaliza → PRD → grafo → build TDD |
| `agf import-prd <file>` | Importa PRD (.md/.txt/.pdf/.html/.docx) → grafo |
| `agf generate-prd "<ideia>"` | Gera PRD a partir de um prompt (via LLM) |
| `agf build` | Lifecycle completo: PRD → grafo → decompose → autopilot |
| `agf autopilot [--simulate|--live|--max <n>|--retries <n>]` | Loop autônomo: next → DoD → done|escalate |
| `agf loop --every <dur> <cmd> | --goal <rubric> --cmd <cmd>` | Loop por intervalo (--every) ou goal-driven (--goal) |
| `agf run "<prompt>"` | Execução one-shot: gera → aplica → testa |
| `agf exec` | Composição cross-platform de comandos agf |
| `agf exec pipe <command> [args...]` | Executa um comando agf e retorna o .data JSON |
| `agf exec chain "<cmd1>; <cmd2>; ..."` | Pipeline de comandos agf separados por ; |

#### Grafo — leitura

| Comando | O que faz |
|---------|-----------|
| `agf next` | Puxa a próxima task desbloqueada (pull, WIP=1) |
| `agf query [--type --status --parent --search --limit]` | Consulta nós por tipo/status/parent/texto |
| `agf node show <id>` | Detalhes de um nó + arestas de entrada/saída |
| `agf edge ls [--from <id>] [--to <id>]` | Lista arestas com filtros opcionais |
| `agf context <id> [--compressed]` | Context-pack compacto + RAG de um nó |
| `agf brief <id> [--format markdown|json|claude-prompt]` | Brief de execução p/ delegar ao executor |
| `agf search "<query>" [--limit <n>]` | Busca FTS5/BM25 sobre os nós do grafo |
| `agf retrieve-command "<intenção>" [--threshold <n>] [--limit <n>] [--local]` | RAG-IN: recupera o comando exato para uma intenção (fallback --help sob o limiar) |
| `agf montar-output "<objetivo>" [--threshold <n>] [--limit <n>]` | RAG-OUT: recupera scaffold adequado (preenche slots) ou gera, por objetivo |
| `agf stats` | Contagens e estatísticas: nodes, edges, byType, byStatus |
| `agf kanban [--swimlane]` | Board Kanban com swimlanes e métricas de fluxo |
| `agf insights` | Analítica determinística: DORA, gargalos, fases, fluxo |
| `agf insights dora` | Métricas DORA (deploy freq, lead time, CFR, MTTR, trend) |
| `agf insights bottlenecks` | Detecção de gargalos (bloqueadas, sem AC, oversized) |
| `agf insights phases` | Distribuição de tasks por fase do lifecycle |
| `agf insights wip` | Contagem de WIP + alerta de violação |
| `agf insights summary` | Resumo de fluxo: métricas + WIP + gargalos |
| `agf export [-o <file>]` | Serializa o grafo como JSON |

#### Grafo — mutação

| Comando | O que faz |
|---------|-----------|
| `agf node add --title <t> --type <t> [--parent <id> --status <s> --priority <n> --ac <c>]` | Cria um nó (task, epic, subtask, risk, etc.) |
| `agf node update <id> [--title --description --priority --type]` | Atualiza título, descrição, prioridade, tipo |
| `agf node status <id> <state> [--force]` | Muda status com validação status_flow |
| `agf node move <id> --parent <pid>` | Reparenta um nó sob novo pai |
| `agf node clone <id> [--parent <pid>]` | Clona um nó com seus atributos |
| `agf node rm <id>` | Remove um nó do grafo |
| `agf edge add <from> <to> [--type <t>] [--reason <r>]` | Cria relação (depends_on, blocks, parent_of…) |
| `agf edge rm <id>` | Remove uma aresta |
| `agf import-graph <file> [--dry-run]` | Funde um grafo JSON exportado no projeto |

#### Pipeline de task (2 calls)

| Comando | O que faz |
|---------|-----------|
| `agf start` | Inicia próxima task: wake-up + next + context + marca in_progress |
| `agf check <id>` | Definition of Done (12 checks) + aderência TDD |
| `agf done <id> [--skip-test]` | Finaliza: DoD + run tests + memória + done + sugere próxima |
| `agf pipeline` | Compound commands: múltiplas operações num único ciclo store |
| `agf pipeline next-context [--full] [-d dir]` | Find next task + load context (1 store open) |
| `agf pipeline next-start [--full] [-d dir]` | Find next + context + mark in_progress (1 store open) |
| `agf pipeline next-context-start [--full] [-d dir]` | Alias for next-start |

#### Decomposição & planejamento

| Comando | O que faz |
|---------|-----------|
| `agf decompose` | Detecta tasks grandes e sugere subtasks atômicas |
| `agf phase` | Taxonomia SHAPE→BUILD→SHIP + fase atual |
| `agf gate <design|review|handoff|deploy|listening|all>` | Gates de prontidão por fase do lifecycle |
| `agf template list` | Lista templates de decomposição disponíveis |
| `agf template apply <name>` | Aplica um template a um nó do grafo |
| `agf scaffold <nome> [--type class|fn|comp|iface|type]` | Scaffold/boilerplate determinístico (acoplador) |

#### Qualidade, harness, forecast

| Comando | O que faz |
|---------|-----------|
| `agf eval [--suite --models --provider --live --repeat --out]` | Suíte de cenários reais → scorecard |
| `agf harness [--violations]` | Scan de agent-readiness (8 dimensões, score A/B/C/D) |
| `agf hooks` | Inspeciona a taxonomia de 28 hooks (list/test/discover) |
| `agf hooks list` | Lista os 28 pontos: ponto → canal → módulo-owner |
| `agf hooks test <channel>` | Dry-fire de um canal com payload de fixture |
| `agf hooks discover` | Lista canais da taxonomia sem handler registrado |
| `agf code index` | Re-indexa o projeto (tree-sitter + LSP) |
| `agf code search <symbol>` | Busca semântica de símbolos via FTS5 |
| `agf code callers <symbol>` | Lista callers de um símbolo (incoming calls) |
| `agf code callees <symbol>` | Lista símbolos chamados (outgoing calls) |
| `agf code def <symbol>` | Go-to-definition via LSP |
| `agf code refs <symbol>` | Lista todas as referências via LSP |
| `agf code impact <file>` | Blast radius: símbolos afetados por mudança |
| `agf code affected <file>` | Testes afetados por mudanças no arquivo |
| `agf gaps [--kind --severity --limit --json]` | Detecta lacunas de completude (~0 token) |
| `agf scan-repos [root] [--report --ingest --json]` | Explora repos vizinhos: fingerprint + insights |
| `agf quality` | Gate 95/95 (testes + logs sobre src/) |
| `agf forecast` | Previsão de ETA do backlog com 95% CI |

#### Memória, snapshot, heal

| Comando | O que faz |
|---------|-----------|
| `agf memory write <name> [--content <c>|--file <f>]` | Escreve uma memória do projeto |
| `agf memory read <name>` | Lê uma memória do projeto |
| `agf memory list` | Lista todas as memórias do projeto |
| `agf memory rm <name>` | Remove uma memória do projeto |
| `agf memory search "<query>" [--limit <n>]` | Busca textual nas memórias do projeto |
| `agf snapshot create` | Cria um snapshot do grafo (backup) |
| `agf snapshot list` | Lista snapshots disponíveis |
| `agf snapshot restore <id>` | Restaura o grafo a partir de um snapshot |
| `agf heal [--apply] [--log]` | Self-healing do grafo (MAPE-K) |
| `agf gc` | Coleta de lixo (worktrees/branches órfãos) |

#### Modelo, métricas, custo

| Comando | O que faz |
|---------|-----------|
| `agf calibrate [--lever <name>] [--band <n>]` | Calibra o limiar do portão RAG por score×saved (lê o lever ledger) |
| `agf model list` | Lista tiers do tier-router (cheap/build/frontier/fallback) |
| `agf model current` | Mostra o modelo ativo configurado |
| `agf model set <id|auto>` | Fixa um modelo ou volta para auto |
| `agf model route <kind>` | Mostra qual modelo o tier-router usaria |
| `agf provider list` | Lista providers LLM disponíveis |
| `agf provider use <id> [--base-url <url>]` | Seleciona o provider ativo |
| `agf provider current` | Mostra provider ativo + fallback chain |
| `agf provider set-url [url]` | Define/limpa o endpoint do provider ativo |
| `agf provider failover [chain] [--clear]` | Configura cadeia de failover |
| `agf metrics [--session --baseline --simulate --economy-report]` | Tokens/$ por task e sessão (llm_call_ledger) |
| `agf compress <filters|discover|test>` | Compressor de saída de ferramenta |
| `agf compress filters` | Lista filtros de compressão ativos |
| `agf compress discover [--ledger]` | Saídas sem filtro registradas |
| `agf compress test <file>` | Testa qual filtro casaria com um arquivo |
| `agf rtk <filters|discover|test>` | Alias para agf compress |
| `agf savings [--reset]` | Economia cumulativa de tokens (ledger) |
| `agf retrieve <hash> [--query --limit]` | Resgata original CCR por hash |
| `agf learning stats` | Performance por-agente + routing |
| `agf learning route <agentId>` | Decisão de roteamento de agente baseada no histórico |
| `agf learning explain <agentId>` | Explica a decisão de roteamento (breakdown) |
| `agf learning export` | Exporta todos os registros de learning (JSON) |
| `agf status` | Painel unificado: provider/model/cache + tokens/$ |

#### Spec-kit & governança

| Comando | O que faz |
|---------|-----------|
| `agf adr create` | Cria um Architecture Decision Record no grafo |
| `agf adr list` | Lista ADRs existentes no grafo |
| `agf constitution` | Princípios governantes: --create|--list|--check |
| `agf preset --list|--show|--apply <name>` | Presets de workflow: --list|--show|--apply |
| `agf spec --generate|--validate|--list-templates` | Geração/validação de specs por fase |
| `agf spec-sync register` | Registra uma spec versionada |
| `agf spec-sync list` | Lista specs registradas |
| `agf spec-sync status` | Status de sync das specs |
| `agf spec-sync link <specId> <nodeId>` | Linka spec a um nó do grafo |
| `agf principles` | Doctrine: lista e exibe princípios |
| `agf plugin` | Gerencia plugins (--install, --remove, --list) |
| `agf profile` | Perfis de configuração (list, show) |

#### Dev tooling (test, lint, usage)

| Comando | O que faz |
|---------|-----------|
| `agf test [--blast|--changed|--file <path>|--node <id>]` | Vitest: --blast|--changed|--file|--node |
| `agf lint [--fix|--file <path>|--all]` | ESLint: --fix|--file|--all |
| `agf usage report [--top <n>]` | Top comandos usados + sugestão de wrappers |
| `agf usage wrap <command> [--apply]` | Auto-gera wrapper agf para comando nativo |

#### Setup & ambiente

| Comando | O que faz |
|---------|-----------|
| `agf init` | Inicializa o projeto: DB, gitignore, context files, docs |
| `agf doctor [--json --providers]` | Diagnóstico do ambiente + contexto LLM + drift detection |
| `agf daemon start [-p <port>]` | Inicia o serviço local em background |
| `agf daemon stop` | Para o serviço local deste workspace |
| `agf daemon status` | Verifica se o daemon está rodando |
| `agf daemon prune [--dry-run]` | Mata daemons órfãos + limpa state dirs |
| `agf daemon list` | Lista daemons e seus status |
| `agf login` | Autentica no GitHub Copilot (device-flow) |
| `agf logout` | Remove o token do GitHub Copilot |
| `agf skill list` | Lista skills do ciclo de vida |
| `agf skill show <name>` | Exibe o conteúdo de uma skill |
| `agf tui` | TUI interativa (Ink) — agf sem args num TTY |
| `agf ui [--port <n>]` | Web mínima de progresso: grafo + tokens + logs |

> Dev: `npm run dev -- <comando>`. Build: `agf` (binário) ou `agent-graph-flow`.
> `agf` sem args num TTY (com projeto) abre a TUI.

### Custo de token & providers (3º pilar)

**Providers** — `agf provider use <id>` escolhe por onde a chamada LLM vai. A *mesma* via CLI serve qualquer agente (Claude, Copilot, Codex, Cursor, Gemini…) — **nunca MCP**.
Todos os 10 providers são auto-detectados de env vars (`agf doctor --providers` lista quais estão configurados):

| Provider | Env var | Gateway |
|----------|---------|---------|
| `anthropic` | `ANTHROPIC_API_KEY` | auto-wired |
| `openai` | `OPENAI_API_KEY` | auto-wired |
| `openrouter` | `OPENROUTER_API_KEY` | auto-wired |
| `gemini` | `GEMINI_API_KEY` | auto-wired |
| `bedrock` | `BEDROCK_API_KEY` | auto-wired |
| `azure` | `AZURE_OPENAI_API_KEY` | auto-wired |
| `deepseek` | `DEEPSEEK_API_KEY` | auto-wired |
| `glm` | `GLM_API_KEY` | auto-wired |
| `kimi` | `KIMI_API_KEY` | auto-wired |
| `groq` | `GROQ_API_KEY` | auto-wired |
| `copilot` | (via `agf login`) | default |
| `ollama` | (local, $0/token) | manual URL |

- **OpenRouter:** `export OPENROUTER_API_KEY=…` → `agf provider use openrouter`. Fixe um modelo com `--pin` (ex.: `agf deliver "…" --live --pin deepseek/deepseek-v4-flash`) ou deixe o tier-router escolher (cheap→`deepseek-v4-flash`, build→`llama-4-maverick`, frontier→`qwen3.6-plus`).

**Alavancas automáticas** (sem comando — agem no gateway): diff-edits (só a região alterada), repo-map ranqueado por PageRank (~1k tok), lossy-gate (auto-revert se a compressão quebra o sentido), AAAK, content-router (SmartCrusher p/ arrays JSON homogêneos + compressão AST de código), **CCR reversível** (cacheia o original + marcador ⟨ccr:hash⟩ → outcome `ccr_dropped`; resgate com `agf retrieve <hash>`), retry com feedback compacto. Cada economia entra no `llm_call_ledger`.

**Medir** (transformar a promessa em número):
- `agf metrics [--economy-report]` — tokens/$ por task e sessão + o que as alavancas pouparam.
- `agf metrics --simulate` — re-precifica a fatura real sob todos os modelos.
- `agf eval --models <ids> --live` — cenários reais → scorecard (resolve% × custo-por-sucesso).
- `agf savings` — economia cumulativa de tokens por task (ledger real, cached tokens contabilizados automaticamente).
- `agf savings --reset` — zera o contador cumulativo.

**Rastreabilidade** — cada chamada LLM é gravada no `llm_call_ledger` com `node_id` (atribuição por task), `cached_input_tokens`, `cost_usd` e `session_id`. O `agf done` registra automaticamente a economia da task. Use `agf doctor --providers` para ver quais providers estão configurados no ambiente.

### Harness de Completude — `agf gaps` (detect → delegate → verify)

`agf gaps` é determinístico (~0 token) e acha lacunas de completude no grafo: rastreabilidade
requirement→task→test, cobertura de AC na decomposição, AC sem testabilidade, NFR faltando,
edge-cases/erros ausentes, ambiguidade, atomicidade, design/estimate drift.

**A IA condutora (você — Copilot/Claude/Codex/Cursor/Gemini/OpenCode) fecha as lacunas**; o agf só
detecta e re-verifica. Cada gap traz `applyVia`: os comandos `agf` exatos pra fechá-lo.

**Loop:**
1. `agf gaps --severity required --json` — pega os blockers acionáveis.
2. Pra cada gap, rode o `applyVia` (ex.: `agf edge add --from <task> --to <req> --type implements`), escolhendo a semântica.
3. `agf gaps` de novo até `ready: true` — desfecho determinístico, independente de qual CLI fechou.

Filtros: `--kind <k>`, `--severity required|recommended`, `--limit N`, `--json` (relatório completo p/ loops).

### Brief de execução — delegando uma task ao executor

**Heurística:** _especifique a ponta e a saída; delegue o meio._ Onde o executor pode errar caro
(contrato, limites, incerteza) você gasta tokens preventivos baratos; o que ele faz bem sozinho
(escrever o código dentro das guardas) você deixa livre. "De outro mundo" não é um prompt mais longo —
é um que fecha as saídas de erro caras com o mínimo de palavras.

Gere o esqueleto pronto a partir do node: `agf brief <id>` (`--format markdown|json|claude-prompt`).
Ele auto-preenche o que o grafo sabe (intenção, AC, blast radius, deps, prontidão) e deixa os campos
de julgamento como `<fill: …>` pra você completar.

**Template:**
- **Intenção** (1 linha): para que existe / efeito desejado.
- **Tarefa** (atômica): uma só — node do grafo: `<id>`.
- **Imite:** arquivo-espelho a seguir como padrão.
- **Ler/tocar** (exato): caminhos + símbolos a reusar.
- **Contrato:** assinatura/tipos/comportamento (trechos pequenos **inline**; arquivos grandes → aponte o path).
- **AC** (testável): 2–4 critérios verificáveis.
- **NÃO:** refatorar vizinhos / deps novas / tocar X / mudar default.
- **Blast radius:** arquivos sensíveis → mudança aditiva.
- **Orçamento:** ~N arquivos, sem deps, sem hot-path.
- **Incerteza:** se o contrato falhar ou faltar info, PARE e reporte; se ambíguo, escolha e justifique em 1 linha.
- **Teste com:** fixture/stub concreto (ex.: `new Database(':memory:')`, stub da chamada LLM com contador) — evita setup flaky ou bater em auth que não existe no sandbox.
- **DoD:** typecheck · teste do arquivo · blast · lint.
- **Self-review antes de retornar** (~30 tokens, substitui um ciclo caro): sobrou placeholder? escopo vazou? AC cobertos? default intacto?
- **Retorne (schema):** `{arquivos[], testes{passed,failed}, desvios[]}` — sem dump de código; não commitar.

**Validação de retorno** — o condutor usa `parseExecutorResult(resposta)` para parsear o JSON estruturado
do executor (com fallback regex) e `validateBriefReady(brief)` para verificar que todos os campos de
julgamento (`imitate`, `readTouch`, `contract`, `testWith`) foram preenchidos antes de delegar.
Retorno inválido → rejeitar e pedir correção; válido → fechar o loop em 1 passo.

> Retorno estruturado torna a validação trivial (parse em vez de leitura). O condutor valida e fecha o loop; o executor escreve o meio.

### Fluxo de trabalho OBRIGATÓRIO

**Pipeline (2 calls):**
```bash
agf start                 # wake-up + next + context + marca in_progress
# … implementa com TDD (Red → Green → Refactor) …
agf done <id>             # DoD + memória + marca done + sugere próxima
```

**Granular (controle fino):**
```bash
agf next                  # puxa a próxima task (pull, WIP=1)
agf context <id>          # context-pack compact + RAG
# … TDD …
agf check <id>            # Definition of Done + aderência TDD
agf node status <id> done # transição validada (status_flow)
```

**Modo delegado (sem provider — qualquer CLI-agente dirige):** se nenhum provider
está conectado ao agf, os comandos `--live` (`agf run`/`agf deliver`/`agf autopilot --live`)
NÃO quebram — retornam `mode:delegated` com o brief pronto p/ VOCÊ (Claude/Copilot/Codex/…)
executar com seu próprio LLM. Feche o loop com `agf submit`:
```bash
agf next                  # próxima task
agf brief <id>            # spec de delegação (intenção, AC, contrato, blast)
# … você implementa com seu próprio LLM e aplica os edits …
agf submit <id> --result '{"arquivos":["x.ts"],"testes":{"passed":N,"failed":0},"desvios":[]}'
                          # valida → blast → DoD → done; desvios viram findings
```

### Lifecycle (9 fases) — comandos `agf` por fase

1. **ANALYZE** — `agf import-prd` · `agf node add` · `agf gate` (Definition of Ready)
2. **DESIGN** — `agf node add`/`agf edge add` (ADRs, interfaces) · `agf constitution` · `agf gate design`
3. **PLAN** — `agf decompose` · `agf template apply` · AC testável por task
4. **IMPLEMENT** — `agf start` → TDD → `agf done` (ou granular) · `agf harness`
5. **VALIDATE** — `agf check <id>` · `agf gate` · `agf metrics`
6. **REVIEW** — `agf export` · `agf insights` · `agf gate review`
7. **HANDOFF** — `agf memory write` · `agf snapshot create` · `agf gate handoff`
8. **DEPLOY** — `agf export` · `agf forecast` · `agf gate deploy` (harness ≥ 70)
9. **LISTENING** — `agf node add` · `agf import-prd` (novo ciclo)

### Índice de skills do ciclo (escolha a abordagem certa)

Qualquer CLI lê esta tabela pra escolher a skill certa pro intent atual — a coluna **Quando usar** mapeia situação → skill. Rode com `agf skill show <name>` ou siga o comando de entrada.

| Skill | Fase | Quando usar | Comando de entrada | Skills relacionadas |
|-------|------|-------------|--------------------|---------------------|
| `graph-prd` | ANALYZE | Start of a cycle with a vague idea | `agf generate-prd "<idea>"` | graph-analyze |
| `graph-analyze` | ANALYZE | PRD already imported | `agf import-prd <file>` | graph-prd, graph-design |
| `graph-design` | DESIGN | DoR approved | `agf context <id>` | graph-analyze, graph-plan |
| `graph-plan` | PLAN | DESIGN ready | `agf context <id>` | graph-design, graph-implement |
| `graph-implement` | IMPLEMENT | An unblocked task exists | `agf start` | graph-plan, graph-validate, graph-bugs |
| `graph-validate` | VALIDATE | ≥50% of tasks done with AC | `agf kanban` | graph-implement, graph-review |
| `graph-review` | REVIEW | VALIDATE complete | `agf insights` | graph-validate, graph-handoff |
| `graph-handoff` | HANDOFF | REVIEW approved | `agf memory write <name>` | graph-review, graph-deploy |
| `graph-deploy` | DEPLOY | HANDOFF approved | `agf provider use <id>` | graph-handoff, graph-listening |
| `graph-listening` | LISTENING | Post-deploy | `agf learning stats` | graph-deploy, graph-analyze |
| `graph-quality` | REVIEW | Code smells or accumulated debt | `agf quality` | graph-review, graph-validate |
| `graph-security` | REVIEW | Change touches authn/authz, external I/O or secrets | `agf check <id>` | graph-review, graph-deploy |
| `graph-bugs` | IMPLEMENT | Incorrect behavior observed | `agf node add --type bug` | graph-implement |
| `graph-platform` | VALIDATE | Delivery has a UI/platform surface | `agf harness` | graph-validate, graph-deploy |
| `graph-mega-brain` | ORCHESTRATION | Drive a PRD/feature end-to-end through the graph (ANALYZE→…→LISTENING) | `agf stats / agf query` | graph-lead, graph-implement, graph-validate |

### Definition of Done (rode `agf check <id>` antes de `agf done`)

| # | Check | Severidade |
|---|-------|------------|
| 1 | Tem acceptance criteria | required |
| 2 | Score AC ≥ 60 (INVEST) | required |
| 3 | Sem blockers não resolvidos | required |
| 4 | Status flow válido (passou por in_progress) | required |
| 5 | Tem descrição | recomendado |
| 6 | Não oversized (sem L/XL sem subtasks) | recomendado |
| 7 | ≥1 AC testável | recomendado |
| 8 | testFiles preenchido | recomendado |

### Princípios de Fluxo (Little's Law + Lean + TOC)

- **WIP = 1** — no máximo 1 task `in_progress`. `cycle_time = WIP / throughput`.
- **Pull, não Push** — `agf next` puxa; nunca empurrar para in_progress sem terminar a anterior.
- **Gargalo primeiro (TOC)** — se VALIDATE acumula, pare de implementar e valide.
- **Eliminar desperdício (Lean/Toyota)** — sem overproduction (features não planejadas), sem waiting (tasks blocked sem ação), use `agf context` (não dumps), TDD elimina defects.
- **Métricas de fluxo** — `agf insights` / `agf forecast`: cycle time, lead time, throughput, flow efficiency (> 40%).

### Princípios XP Anti-Vibe-Coding

- **TDD obrigatório** — Teste antes do código. Sem teste = sem implementação.
- **Anti-one-shot** — Nunca gere sistemas inteiros em um prompt. Decomponha em tasks atômicas (`agf decompose`).
- **Decomposição atômica** — Cada task completável em ≤2h.
- **Honestidade** — surfar pontas soltas como finding/risk no grafo (`agf node add --type risk`); nunca marcar done com alegação falsa.
- **CLAUDE.md como spec evolutiva** — documente padrões e decisões.

### Gates de Teste Hierárquicos

| Gate | Comando | Trigger |
|------|---------|---------|
| Task | `npm run test:blast` | a cada task finalizada (`agf done`) |
| Épico | `npm run test:node` | promoção de épico |
| PR | `npm test` | antes de push/PR |

Blast obrigatório no `agf done`. Full obrigatório pré-PR.

### Spec-Driven Development (spec-kit, via `agf`)

- `agf constitution` — princípios governantes (indexados, validados em gates).
- `agf preset --apply <name>` — workflow (default/strict-tdd/agile-light/enterprise).
- `agf spec --generate <template>` / `--validate <file>` — specs por fase.
- `agf spec-sync link <specId> <nodeId>` — specs vivas ligadas ao grafo.

### Memory ≠ Estado Atual

Memory files são snapshots point-in-time, não estado live. Contagens ("X/Y done") ficam stale.

1. Grep pelo arquivo/função — se existe, o memory é stale.
2. **Código vence memory.**
3. Reconcilie com `agf stats`/`agf query` antes de planejar.

> Nunca confiar em contagens de progresso de memories. Verificar no código/grafo primeiro.
### Contexto do Projeto

Stack detectada: node, typescript, react, vitest, python.

- **TypeScript**: Usar tipos estritos (`strict: true`). Evitar `any`. Tipar retornos de funções públicas.
- **React**: Componentes funcionais com hooks. Props tipadas via interfaces. Evitar `useEffect` com deps vazias. Testar com React Testing Library (RTL).
- **Testes (Vitest)**: Arquivos `*.test.ts`. Use `describe`/`it`/`expect`. Mock com `vi.fn()`. Blast: `npm run test:blast`.
- **Node.js**: ESM preferido (`"type": "module"`). Use `node:` prefix em imports built-in.
- **Python**: Type hints obrigatórias (`def foo(x: int) -> str`). Use `pytest` para testes. PEP 8.
- **Package Manager**: npm. Lockfile deve estar versionado.


> **Referência completa de comandos:** `agf help` (índice agrupado) · `agf <comando> --help` (flags) · `agf skill list` (skills do ciclo de vida).
<!-- agent-graph-flow:end -->


## agf JSON Output Contract

Every `agf` command returns a single-line JSON object to stdout:

```json
{"ok":true|false, "code":"string|null", "data":..., "error":"string|null", "meta":{"command":"string","ms":number,"count?":number}}
```

### Envelope fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | `true` = success, `false` = error |
| `code` | string | Machine-readable error code (present when `ok=false`) |
| `data` | any | Payload (present when `ok=true`; may also be present on `fail`) |
| `error` | string | Human-readable error message (present when `ok=false`) |
| `meta.command` | string | Always present — the command that produced this output |
| `meta.ms` | number | Duration in milliseconds |
| `meta.count` | number | Result count for list commands (optional) |

### Error codes

| Code | Meaning |
|------|---------|
| `ALL_BLOCKED` | Todas as tasks estão bloqueadas por dependências |
| `ALREADY_IMPORTED` | Arquivo já foi importado |
| `DOCTOR_ERROR` | Erro ao rodar diagnóstico |
| `DOCTOR_FAILED` | Checks críticos do ambiente falharam |
| `DOD_FAILED` | Definition of Done checks required failed |
| `EMPTY_EXTRACTION` | Nenhuma entidade extraída do arquivo |
| `GAPS_FOUND` | Completeness gaps detected |
| `GATE_FAILED` | Phase gate did not pass |
| `INIT_ERROR` | Erro durante inicialização |
| `INIT_FAILED` | Falha na inicialização do projeto |
| `INVALID_FORMAT` | Formato de saída inválido |
| `INVALID_KIND` | Tipo de tarefa inválido para roteamento |
| `INVALID_PORT` | Número de porta inválido |
| `INVALID_TRANSITION` | Transição de status inválida |
| `MISSING_ID` | Task ID não fornecido |
| `NOT_FOUND` | Recurso não encontrado (nó, aresta, memória, etc.) |
| `NO_SCENARIOS` | Nenhum cenário de eval encontrado |
| `NO_TASKS` | Nenhuma task disponível para puxar |
| `PARSE_ERROR` | Falha ao parsear arquivo |
| `STORE_OPEN_FAILED` | Falha ao abrir o store do projeto |
| `UNKNOWN_KIND` | Kind de gap desconhecido |
| `UNKNOWN_MODEL` | Modelo desconhecido |
| `UNKNOWN_PHASE` | Fase de gate desconhecida |
| `UNKNOWN_PROVIDER` | Provider desconhecido |
| `UNKNOWN_SEVERITY` | Severity de gap desconhecida |

### Command output schemas

| Command | Args | `ok:true` → `data` shape | Error codes |
|---------|------|---------------------------|-------------|
| `agf stats` | [-d dir] | `{totalNodes, totalEdges, byType, byStatus}` | — |
| `agf next` | [-d dir] | `{node: GraphNode, reason, warning?}` | `NO_TASKS`, `ALL_BLOCKED` |
| `agf query` | [--type] [--status] [--parent] [--search] [--limit] [-d dir] | `GraphNode[]` | — |
| `agf search` | <query> [--limit] [-d dir] | `SearchResult[]` | — |
| `agf check` | <nodeId> [-d dir] | `{dod: {ready,score,grade,checks}, tdd}` | `NOT_FOUND`, `DOD_FAILED` |
| `agf node add` | --title [--type] [--parent] [--status] [--priority] [--ac] [-d dir] | `{id, type, status, title}` | — |
| `agf node show` | <id> [-d dir] | `{node: GraphNode, outEdges, incEdges}` | `NOT_FOUND` |
| `agf node update` | <id> [--title] [--description] [--priority] [--type] [-d dir] | `{id, updated}` | `NOT_FOUND` |
| `agf node status` | <id> <state> [--force] [-d dir] | `{id, from, to}` | `NOT_FOUND`, `INVALID_TRANSITION` |
| `agf node move` | <id> --parent <pid> [-d dir] | `{id, parent}` | `NOT_FOUND` |
| `agf node clone` | <id> [--parent] [-d dir] | `{source, clone}` | `NOT_FOUND` |
| `agf node rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge add` | <from> <to> [--type] [--reason] [-d dir] | `{id, from, to, relationType}` | `NOT_FOUND` |
| `agf edge rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge ls` | [--from] [--to] [-d dir] | `GraphEdge[]` | — |
| `agf context` | <id> [--compressed] [-d dir] | `TaskContext` | `NOT_FOUND` |
| `agf brief` | <id> [--format markdown|json|claude-prompt] [-d dir] | `ExecutorBrief | {markdown} | {prompt}` | `NOT_FOUND`, `INVALID_FORMAT` |
| `agf export` | [-o file] [-d dir] | `{path?,nodeCount,edgeCount} | GraphDocument` | — |
| `agf import-prd` | <file> [--force] [--allow-empty] [-d dir] | `{nodes, edges, source}` | `ALREADY_IMPORTED`, `EMPTY_EXTRACTION`, `PARSE_ERROR` |
| `agf start` | [-d dir] | `{taskId, title, context}` | `NO_TASKS` |
| `agf done` | <taskId> [-d dir] | `{taskId, dodScore, dodGrade, savings, next?}` | `NOT_FOUND`, `MISSING_ID`, `DOD_FAILED` |
| `agf status` | [-d dir] | `StatusReport | {project:null}` | — |
| `agf metrics` | [-d dir] [--session] [--baseline|--simulate|--economy-report] | `{totals, byTask, bySession, costPerSuccess, ...}` | — |
| `agf forecast` | [-d dir] | `DoraMetrics` | — |
| `agf insights` | <dora|bottlenecks|phases|summary> [-d dir] | `DoraMetrics | BottleneckReport | PhaseDistribution[] | MetricsReport` | — |
| `agf kanban` | [-d dir] [--swimlane] | `{board: KanbanBoard, ledger}` | — |
| `agf harness` | [-d dir] [--violations] | `HarnessScanResult` | — |
| `agf gaps` | [-d dir] [--kind] [--severity] [--history] | `GapReport | {history}` | `UNKNOWN_KIND`, `UNKNOWN_SEVERITY`, `GAPS_FOUND` |
| `agf eval` | [--suite] [--model] [--models] [--live] [--repeat] [--out] | `{scorecard, simulate, mode, totalRuns}` | `NO_SCENARIOS` |
| `agf gate` | <phase> [-d dir] | `{phases: [{phase, report}], anyFail}` | `UNKNOWN_PHASE`, `GATE_FAILED` |
| `agf doctor` | [-d dir] [--providers] | `{checks?, providers?, llmContext?}` | `DOCTOR_FAILED`, `DOCTOR_ERROR` |
| `agf init` | [-d dir] [--name] [--port] [--skip-neural] [--no-serve] | `{success, serveStarted, port?, nextSteps[]}` | `INVALID_PORT`, `INIT_FAILED`, `INIT_ERROR` |
| `agf quality` | [-d dir] [--min-tests] [--min-logs] | `{totalModules, testScore, logScore, thresholds, gatePassed}` | `GATE_FAILED` |
| `agf model list` |  | `{mode, tiers}` | — |
| `agf model current` | [-d dir] | `{mode, modelId}` | — |
| `agf model set` | <idOrAuto> [-d dir] | `{mode, modelId}` | `UNKNOWN_MODEL` |
| `agf model route` | <kind> [-d dir] | `{kind, model}` | `INVALID_KIND` |
| `agf provider list` |  | `{providers[]}` | — |
| `agf provider use` | <id> [--base-url] [-d dir] | `{provider, baseUrl, requiresKey, envVar?}` | `UNKNOWN_PROVIDER` |
| `agf provider current` | [-d dir] | `{provider, kind, baseURL?, fallback?}` | — |
| `agf provider failover` | [chain] [--clear] [-d dir] | `{failover: string[] | null}` | `UNKNOWN_PROVIDER` |
| `agf memory write` | <name> [--content|--file] [-d dir] | `{name, bytes}` | — |
| `agf memory read` | <name> [-d dir] | `{name, content}` | `NOT_FOUND` |
| `agf memory list` | [-d dir] | `string[]` | — |
| `agf memory rm` | <name> [-d dir] | `{name, removed}` | `NOT_FOUND` |
| `agf memory search` | <query> [-d dir] [--limit] | `SearchResult[]` | — |
| `agf snapshot create` | [-d dir] | `{snapshotId}` | — |
| `agf snapshot list` | [-d dir] | `Snapshot[]` | — |
| `agf snapshot restore` | <id> [-d dir] | `{nodesValid, edgesRestored}` | — |
| `agf exec pipe` | <command> [args...] | `data do envelope do comando interno` | — |
| `agf exec chain` | "<cmd1>; <cmd2>; ..." | `{results: [{command, ok, data}]}` | — |
| `agf pipeline next-context` | [--full] [-d dir] | `{node: {id,title,status,priority}, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-context-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf compress` | [filters | discover | test <file>] | `{filters[]} | {misses[]} | {filter, before, after, savedPct}` | — |
| `agf code` | <index|search|callers|callees|def|refs|impact|affected> [target] [-d dir] | `CodeIntelResult` | — |
| `agf savings` | [--reset] [-d dir] | `{tasks[], totals, pricing, backlogCount, projectedCost, commands?, economyBlock?, globalTotals?}` | — |
| `agf retrieve` | <hash> [--query] [--limit] [-d dir] | `{hash, original} | {hash, query, matches[]}` | `NOT_FOUND` |

### Decision logic for consumers

```
if (!envelope.ok) {
  switch (envelope.code) {
    case "DOD_FAILED":
    case "GAPS_FOUND":
      // envelope.data contains detailed check results
      // fix issues and retry
      break
    case "NOT_FOUND":
      // resource does not exist
      break
    case "NO_TASKS":
      // no work available — stand by
      break
    default:
      // handle unknown error
  }
}
// On success: process envelope.data
```

### Consuming output cheaply (token + memory discipline)

`agf` stdout is always **minified JSON**; logs are NDJSON on **stderr** — parse stdout only. Consume the smallest slice you need:

- **Project fields with `--select`** (no external `jq`; ~80–90% fewer tokens): `agf next --select data.node.id,data.node.title`. Works in any position, always keeps `ok`/`code`/`error`/`meta`, and an invalid path falls back to the full envelope (never errors).
- **Use `--profile <name>`** for agent-aware presets (claude-code, copilot, opencode, minimal): automatically selects the right fields per command. `--select` wins over `--profile` when both are provided.
- **`--pretty`** only for human debugging (indented JSON).
- **Compose natively with `agf exec`** (cross-platform, no shell): `agf exec pipe next` returns the inner `.data`; `agf exec chain "next; check <id>"` runs a sequence.
- **Pipe further when needed** — POSIX: `agf query --status ready | jq -c '.data[].title'`; PowerShell: `agf query --status ready | ConvertFrom-Json | Select-Object -Expand data`.
- **Large output → temp file, then filter** (OS temp dir — `/tmp` on POSIX, `%TEMP%` on Windows; in code use `os.tmpdir()`): `agf export -o "$TMPDIR/g.json" && jq -c '.data.nodes[] | {id,title}' "$TMPDIR/g.json"`.
- **Sweep big structures with short async one-liners** (`node -e "..."`) rather than long scripts — decide what to keep, deterministically.
- **`agf compress`** is for compressing OTHER tools' output (grep/test/build) — never wrap `agf` itself; it is already minimal.
- **Scaffold-decide:** pick a scaffold from `github.com` or locally via `agf scaffold`, filter/cache, return — never dump whole repos.

Runs identically on Windows, macOS, and Linux — the native `--select` / `agf exec` path needs no shell.

> **Fundamentação:** minified JSON + field projection is the recommended agent-CLI pattern (Anthropic "Effective context engineering"; GitHub "token efficiency in agentic workflows") — returning only the needed fields cuts input tokens ~80–90%.

## agf JSON Output Contract

Every `agf` command returns a single-line JSON object to stdout:

```json
{"ok":true|false, "code":"string|null", "data":..., "error":"string|null", "meta":{"command":"string","ms":number,"count?":number}}
```

### Envelope fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | `true` = success, `false` = error |
| `code` | string | Machine-readable error code (present when `ok=false`) |
| `data` | any | Payload (present when `ok=true`; may also be present on `fail`) |
| `error` | string | Human-readable error message (present when `ok=false`) |
| `meta.command` | string | Always present — the command that produced this output |
| `meta.ms` | number | Duration in milliseconds |
| `meta.count` | number | Result count for list commands (optional) |

### Error codes

| Code | Meaning |
|------|---------|
| `ALL_BLOCKED` | Todas as tasks estão bloqueadas por dependências |
| `ALREADY_IMPORTED` | Arquivo já foi importado |
| `DOCTOR_ERROR` | Erro ao rodar diagnóstico |
| `DOCTOR_FAILED` | Checks críticos do ambiente falharam |
| `DOD_FAILED` | Definition of Done checks required failed |
| `EMPTY_EXTRACTION` | Nenhuma entidade extraída do arquivo |
| `GAPS_FOUND` | Completeness gaps detected |
| `GATE_FAILED` | Phase gate did not pass |
| `INIT_ERROR` | Erro durante inicialização |
| `INIT_FAILED` | Falha na inicialização do projeto |
| `INVALID_FORMAT` | Formato de saída inválido |
| `INVALID_KIND` | Tipo de tarefa inválido para roteamento |
| `INVALID_PORT` | Número de porta inválido |
| `INVALID_TRANSITION` | Transição de status inválida |
| `MISSING_ID` | Task ID não fornecido |
| `NOT_FOUND` | Recurso não encontrado (nó, aresta, memória, etc.) |
| `NO_SCENARIOS` | Nenhum cenário de eval encontrado |
| `NO_TASKS` | Nenhuma task disponível para puxar |
| `PARSE_ERROR` | Falha ao parsear arquivo |
| `STORE_OPEN_FAILED` | Falha ao abrir o store do projeto |
| `UNKNOWN_KIND` | Kind de gap desconhecido |
| `UNKNOWN_MODEL` | Modelo desconhecido |
| `UNKNOWN_PHASE` | Fase de gate desconhecida |
| `UNKNOWN_PROVIDER` | Provider desconhecido |
| `UNKNOWN_SEVERITY` | Severity de gap desconhecida |

### Command output schemas

| Command | Args | `ok:true` → `data` shape | Error codes |
|---------|------|---------------------------|-------------|
| `agf stats` | [-d dir] | `{totalNodes, totalEdges, byType, byStatus}` | — |
| `agf next` | [-d dir] | `{node: GraphNode, reason, warning?}` | `NO_TASKS`, `ALL_BLOCKED` |
| `agf query` | [--type] [--status] [--parent] [--search] [--limit] [-d dir] | `GraphNode[]` | — |
| `agf search` | <query> [--limit] [-d dir] | `SearchResult[]` | — |
| `agf check` | <nodeId> [-d dir] | `{dod: {ready,score,grade,checks}, tdd}` | `NOT_FOUND`, `DOD_FAILED` |
| `agf node add` | --title [--type] [--parent] [--status] [--priority] [--ac] [-d dir] | `{id, type, status, title}` | — |
| `agf node show` | <id> [-d dir] | `{node: GraphNode, outEdges, incEdges}` | `NOT_FOUND` |
| `agf node update` | <id> [--title] [--description] [--priority] [--type] [-d dir] | `{id, updated}` | `NOT_FOUND` |
| `agf node status` | <id> <state> [--force] [-d dir] | `{id, from, to}` | `NOT_FOUND`, `INVALID_TRANSITION` |
| `agf node move` | <id> --parent <pid> [-d dir] | `{id, parent}` | `NOT_FOUND` |
| `agf node clone` | <id> [--parent] [-d dir] | `{source, clone}` | `NOT_FOUND` |
| `agf node rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge add` | <from> <to> [--type] [--reason] [-d dir] | `{id, from, to, relationType}` | `NOT_FOUND` |
| `agf edge rm` | <id> [-d dir] | `{id, removed}` | `NOT_FOUND` |
| `agf edge ls` | [--from] [--to] [-d dir] | `GraphEdge[]` | — |
| `agf context` | <id> [--compressed] [-d dir] | `TaskContext` | `NOT_FOUND` |
| `agf brief` | <id> [--format markdown|json|claude-prompt] [-d dir] | `ExecutorBrief | {markdown} | {prompt}` | `NOT_FOUND`, `INVALID_FORMAT` |
| `agf export` | [-o file] [-d dir] | `{path?,nodeCount,edgeCount} | GraphDocument` | — |
| `agf import-prd` | <file> [--force] [--allow-empty] [-d dir] | `{nodes, edges, source}` | `ALREADY_IMPORTED`, `EMPTY_EXTRACTION`, `PARSE_ERROR` |
| `agf start` | [-d dir] | `{taskId, title, context}` | `NO_TASKS` |
| `agf done` | <taskId> [-d dir] | `{taskId, dodScore, dodGrade, savings, next?}` | `NOT_FOUND`, `MISSING_ID`, `DOD_FAILED` |
| `agf status` | [-d dir] | `StatusReport | {project:null}` | — |
| `agf metrics` | [-d dir] [--session] [--baseline|--simulate|--economy-report] | `{totals, byTask, bySession, costPerSuccess, ...}` | — |
| `agf forecast` | [-d dir] | `DoraMetrics` | — |
| `agf insights` | <dora|bottlenecks|phases|summary> [-d dir] | `DoraMetrics | BottleneckReport | PhaseDistribution[] | MetricsReport` | — |
| `agf kanban` | [-d dir] [--swimlane] | `{board: KanbanBoard, ledger}` | — |
| `agf harness` | [-d dir] [--violations] | `HarnessScanResult` | — |
| `agf gaps` | [-d dir] [--kind] [--severity] [--history] | `GapReport | {history}` | `UNKNOWN_KIND`, `UNKNOWN_SEVERITY`, `GAPS_FOUND` |
| `agf eval` | [--suite] [--model] [--models] [--live] [--repeat] [--out] | `{scorecard, simulate, mode, totalRuns}` | `NO_SCENARIOS` |
| `agf gate` | <phase> [-d dir] | `{phases: [{phase, report}], anyFail}` | `UNKNOWN_PHASE`, `GATE_FAILED` |
| `agf doctor` | [-d dir] [--providers] | `{checks?, providers?, llmContext?}` | `DOCTOR_FAILED`, `DOCTOR_ERROR` |
| `agf init` | [-d dir] [--name] [--port] [--skip-neural] [--no-serve] | `{success, serveStarted, port?, nextSteps[]}` | `INVALID_PORT`, `INIT_FAILED`, `INIT_ERROR` |
| `agf quality` | [-d dir] [--min-tests] [--min-logs] | `{totalModules, testScore, logScore, thresholds, gatePassed}` | `GATE_FAILED` |
| `agf model list` |  | `{mode, tiers}` | — |
| `agf model current` | [-d dir] | `{mode, modelId}` | — |
| `agf model set` | <idOrAuto> [-d dir] | `{mode, modelId}` | `UNKNOWN_MODEL` |
| `agf model route` | <kind> [-d dir] | `{kind, model}` | `INVALID_KIND` |
| `agf provider list` |  | `{providers[]}` | — |
| `agf provider use` | <id> [--base-url] [-d dir] | `{provider, baseUrl, requiresKey, envVar?}` | `UNKNOWN_PROVIDER` |
| `agf provider current` | [-d dir] | `{provider, kind, baseURL?, fallback?}` | — |
| `agf provider failover` | [chain] [--clear] [-d dir] | `{failover: string[] | null}` | `UNKNOWN_PROVIDER` |
| `agf memory write` | <name> [--content|--file] [-d dir] | `{name, bytes}` | — |
| `agf memory read` | <name> [-d dir] | `{name, content}` | `NOT_FOUND` |
| `agf memory list` | [-d dir] | `string[]` | — |
| `agf memory rm` | <name> [-d dir] | `{name, removed}` | `NOT_FOUND` |
| `agf memory search` | <query> [-d dir] [--limit] | `SearchResult[]` | — |
| `agf snapshot create` | [-d dir] | `{snapshotId}` | — |
| `agf snapshot list` | [-d dir] | `Snapshot[]` | — |
| `agf snapshot restore` | <id> [-d dir] | `{nodesValid, edgesRestored}` | — |
| `agf exec pipe` | <command> [args...] | `data do envelope do comando interno` | — |
| `agf exec chain` | "<cmd1>; <cmd2>; ..." | `{results: [{command, ok, data}]}` | — |
| `agf pipeline next-context` | [--full] [-d dir] | `{node: {id,title,status,priority}, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf pipeline next-context-start` | [--full] [-d dir] | `{taskId, title, reason, context, warning?}` | `NO_TASKS` |
| `agf compress` | [filters | discover | test <file>] | `{filters[]} | {misses[]} | {filter, before, after, savedPct}` | — |
| `agf code` | <index|search|callers|callees|def|refs|impact|affected> [target] [-d dir] | `CodeIntelResult` | — |
| `agf savings` | [--reset] [-d dir] | `{tasks[], totals, pricing, backlogCount, projectedCost, commands?, economyBlock?, globalTotals?}` | — |
| `agf retrieve` | <hash> [--query] [--limit] [-d dir] | `{hash, original} | {hash, query, matches[]}` | `NOT_FOUND` |

### Decision logic for consumers

```
if (!envelope.ok) {
  switch (envelope.code) {
    case "DOD_FAILED":
    case "GAPS_FOUND":
      // envelope.data contains detailed check results
      // fix issues and retry
      break
    case "NOT_FOUND":
      // resource does not exist
      break
    case "NO_TASKS":
      // no work available — stand by
      break
    default:
      // handle unknown error
  }
}
// On success: process envelope.data
```

### Consuming output cheaply (token + memory discipline)

`agf` stdout is always **minified JSON**; logs are NDJSON on **stderr** — parse stdout only. Consume the smallest slice you need:

- **Project fields with `--select`** (no external `jq`; ~80–90% fewer tokens): `agf next --select data.node.id,data.node.title`. Works in any position, always keeps `ok`/`code`/`error`/`meta`, and an invalid path falls back to the full envelope (never errors).
- **Use `--profile <name>`** for agent-aware presets (claude-code, copilot, opencode, minimal): automatically selects the right fields per command. `--select` wins over `--profile` when both are provided.
- **`--pretty`** only for human debugging (indented JSON).
- **Compose natively with `agf exec`** (cross-platform, no shell): `agf exec pipe next` returns the inner `.data`; `agf exec chain "next; check <id>"` runs a sequence.
- **Pipe further when needed** — POSIX: `agf query --status ready | jq -c '.data[].title'`; PowerShell: `agf query --status ready | ConvertFrom-Json | Select-Object -Expand data`.
- **Large output → temp file, then filter** (OS temp dir — `/tmp` on POSIX, `%TEMP%` on Windows; in code use `os.tmpdir()`): `agf export -o "$TMPDIR/g.json" && jq -c '.data.nodes[] | {id,title}' "$TMPDIR/g.json"`.
- **Sweep big structures with short async one-liners** (`node -e "..."`) rather than long scripts — decide what to keep, deterministically.
- **`agf compress`** is for compressing OTHER tools' output (grep/test/build) — never wrap `agf` itself; it is already minimal.
- **Scaffold-decide:** pick a scaffold from `github.com` or locally via `agf scaffold`, filter/cache, return — never dump whole repos.

Runs identically on Windows, macOS, and Linux — the native `--select` / `agf exec` path needs no shell.

> **Fundamentação:** minified JSON + field projection is the recommended agent-CLI pattern (Anthropic "Effective context engineering"; GitHub "token efficiency in agentic workflows") — returning only the needed fields cuts input tokens ~80–90%.
