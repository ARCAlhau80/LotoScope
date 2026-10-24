---
target: the LotoScope dashboard
total_score: 20
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 3
target_identity: "file:C:\\Users\\AR CALHAU\\source\\repos\\LotoScope\\dashboard\\app\\page.tsx"
target_fingerprint: "sha256:35a51395905be48d41158905410a3dcf1833ca0768cadf4283772cf20136538d"
target_path: "C:\\Users\\AR CALHAU\\source\\repos\\LotoScope\\dashboard\\app\\page.tsx"
timestamp: 2026-10-15T21-19-18Z
slug: dashboard-app-page-tsx
closed: true
---
# Critique — LotoScope Dashboard (`dashboard/`)

Method: dual-agent (A: ses_ebec366ddffenyIJRxRrP9wFBd · B: ses_ebec357a0ffe5sj4TDfIPd3G0W)

## Design Health Score — Nielsen (Operate/dashboard surface, 0–4)

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Skeleton/overlay present, but global `janela` recompute has no page-level affordance |
| 2 | Match System / Real World | 2 | Strong domain lexicon; `Q/N/A/M/R`, `Σ%`, `N1..N5` need decoding |
| 3 | User Control and Freedom | 2 | Num state is a 3-way cycle with no direct set and no global undo |
| 4 | Consistency and Standards | 2 | Emerald (thermal) used as primary action color; NumBadge size drifts 36/40/36 |
| 5 | Error Prevention | 2 | `ConferidorSection` silently drops bad lines; real-money action has no confirmation |
| 6 | Recognition Rather Than Recall | 2 | Matrix state codes + `Σ%` rely on recall; tooltips hover-only |
| 7 | Flexibility and Efficiency | 2 | Real power affordances (drag .txt, CSV, CDP) but no shortcuts/jump/presets |
| 8 | Aesthetic and Minimalist Design | 2 | Coherent dark observatory, but 20 equal panels + emoji + clipped tooltips |
| 9 | Error Recovery | 2 | Error banner w/ retry good; per-section inline errors plain, no export |
| 10 | Help and Documentation | 2 | Strong inline explanations + ChatBot, but chat is icon-only, no key ref |
| **Total** | | **20/40** | **Acceptable** |

Note: the P0 mojibake (a session-introduced regression, since repaired) depressed heuristics 1/2/9; post-fix these re-rate ~3.

## Design Specificity Verdict

Specific (keep): `NumBadge` (the lit marker: neutral indigo / fixed emerald ring + scale / excluded red + line-through), `QuarantineMatrixLotofacil` (positions×numbers matrix with Q/N/A/M/R and a hover diagnostics panel), the `PrevisaoSection` Pos×#1..#5×Σ% table.
Interchangeable: the page composition — sticky gradient tab bar with "Beta" pill, gradient hero panel, `grid-cols-6` metric cards, gradient buttons, floating chat bubble with "Online" pulse. Strip the Portuguese and it's a generic "insights" shell.
Verdict: the atoms are product-specific; the composition and chrome are not.

Deterministic scan (Assessment B): `impeccable detect --json` on `dashboard/app/page.tsx`, `dashboard/app/layout.tsx`, `dashboard/src/components` → exit 0, **0 findings**. No false positives. Browser overlay unavailable: no server reachable on :3003 or :3000 (app needs a local SQL Server/DB); no reliable user-visible overlay.

## Overall Impression

Handsome, coherent dark system with genuinely specific domain atoms bolted onto a generic 20-panel dashboard shell. Biggest opportunity: make the layout argue for the product (strategy comparison + the durable combinations artifact as the spine) instead of 20 equal-weight stat panels.

## What's Working

1. `NumBadge` state language — instantly legible, consistent across three surfaces.
2. `QuarantineMatrixLotofacil` — a real instrument with methodological transparency (gap/esperado/P90/sigma/P-teórica).
3. Guardrails + honesty in copy: Conferidor separates fixos vs estimados (~); Apostador states it stops before payment; responsible-gambling strip always present.

## Priority Issues

- **P0 — Source-level mojibake across the surface.** UTF-8 read as Latin-1 (`NÃ£o`, `anÃ¡lise`, `ðŸ›¡ï¸`). Violates the pt-BR constraint and the product's scientific credibility. **Status: introduced by this session's scripted edits and REPAIRED during the run** (24 files reversed to correct UTF-8; tsc/build/detector clean). Add an encoding guard (`Ã|â€|ðŸ` in CI) so it cannot regress.
- **P1 — Flat 20-panel single column, no nav/collapse.** `page.tsx:150-285` stacks every section at equal weight. Root of HIGH cognitive load and Alex's frustration. Fix: group into 4 zones (Análise/Geração/Conferência/Automação) with sticky sub-nav + collapsible sections; surface Conferidor as a destination.
- **P1 — Hover-only data unreachable for keyboard/SR.** `HeroCard` tips (`group-hover`), QuarantineMatrix detail panel (`onMouseEnter/Leave`), ChatBot toggle (`title` only). Fix: focusable triggers + `aria-describedby`/`aria-expanded`, keyboard cell nav, labeled chat toggle.
- **P1 — High-stakes money action lacks confirmation.** `ApostadorSection:311` fires real automation on one click; Conferidor prints ROI/lucro with no caveat. Fix: confirmation modal (N apostas, R$ total, "nenhum pagamento é feito aqui") + ROI caveat.
- **P2 — Semantic-color & atom drift.** Emerald used as primary action ("Usar previsão", "Ler jogos", "Exportar todas"); NumBadge 36→40→36. Breaks The One Accent / Thermal Signal rules. Fix: reserve emerald for state; add a structural secondary button; tokenize badge size.
- **P3 — Tooltip clipping.** `HeroCard` tooltip `whitespace-nowrap … overflow-hidden text-ellipsis max-w-[260px]` collapses the multi-line comparativo tooltip to one clipped line. Fix: `whitespace-pre-line` or a real popover.

## Persona Red Flags

**Alex (power user):** must scroll past ~18 sections to reach Conferidor/Apostador; no command palette/shortcuts/section jump; the global `janela` knob is buried in `QmfSection` though it affects the whole dataset; no saved strategy presets (~18 controls re-set each time).
**Sam (accessibility/keyboard/SR):** hover-only disclosure (hero tips, matrix panel, chat toggle); `Q/N/A/M/R` carry meaning only via `title`/color; matrix cells are non-focusable `<div>`s; focus visibility inconsistent (inputs `focus:outline-none` + faint border; only NumBadge has `focus-visible:ring`); table headers lack `scope`.
**Jordan (first-timer):** "Concurso base" appears twice with shared state; jargon (`Σ%`, `Q/N/A/M/R`, "Restringir 7 à posição N3") with no first-run decoding; ~18 controls before the primary "Gerar"; the flagship differentiator (Pool 23 Híbrido/ROI) is never surfaced.

## Cognitive Load

8/8 checklist items fail (single focus, chunking, grouping, hierarchy, one-at-a-time, minimal choices, working memory, progressive disclosure) → **HIGH**. Decision points >4 options: 9 lottery tabs, 13 hero metrics, 7 strategy chips, 6-state matrix legend.

## Emotional Journey

Peak: the Hero with luminous markers. Valleys: mid-page monotony (18 identical panels), and the money moment with no ceremony. Peak-end: the page *ends* on the automation/spend section → recollected feeling is spend-anxiety rather than insight.

## Minor Observations

`layout.tsx` metadata title names only Lotofácil though the app is multi-loteria; `ChatBot.tsx:125` uses `dangerouslySetInnerHTML` with a regex link injector (hardening risk); emoji (`🛡️`, `🟢/🔴`) is off-vocabulary for a sober product; stagger delays run to 0.6s across 20 sections; the "Beta" pill is indefinite; DESIGN.md says NumBadge 36px but the atom renders 40px.

## Questions to Consider

- If the moat is Pool 23 Híbrido + backtested ROI, why does the dashboard open on the raw last draw instead of the recommended combination and its rationale?
- Should the durable artifact (the combinations file) be the spine of the layout, with the 20 panels as supporting evidence?
- Given Principle #5, why is responsible-gambling framing a 12px strip rather than a persistent, dignified element?
- The product is "local, sem telemetria" — why a chat bubble with a pulsing "Online" dot that implies a remote service?
