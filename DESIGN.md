---
name: LotoScope
description: Dashboard analítico noturno para estatística de loterias
colors:
  deep-space: "#070b1a"
  deep-space-2: "#0a0f24"
  panel: "#111630"
  panel-tint: "rgba(255,255,255,0.03)"
  panel-tint-hover: "rgba(255,255,255,0.06)"
  starlight: "#f0f4ff"
  ink-bright: "#e0e7ff"
  slate-haze: "#8892b0"
  signal-indigo: "#6366f1"
  accent-tint: "rgba(99,102,241,0.10)"
  ion-violet: "#818cf8"
  nebula-violet: "#a78bfa"
  positive-emerald: "#10b981"
  emerald-tint: "rgba(16,185,129,0.15)"
  emerald-bright: "#34d399"
  warning-gold: "#f59e0b"
  hot-red: "#ef4444"
  hot-tint: "rgba(239,68,68,0.15)"
  hot-red-bright: "#fca5a5"
  cold-blue: "#3b82f6"
  warm-grey: "#94a3b8"
typography:
  display:
    fontFamily: "Inter, system-ui, -apple-system, sans-serif"
    fontSize: "36px"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Inter, system-ui, -apple-system, sans-serif"
    fontSize: "30px"
    fontWeight: 800
    lineHeight: 1.15
  title:
    fontFamily: "Inter, system-ui, -apple-system, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "Inter, system-ui, -apple-system, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Inter, system-ui, -apple-system, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    letterSpacing: "0.05em"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "10px"
    fontWeight: 500
rounded:
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  2xl: "24px"
components:
  button-primary:
    backgroundColor: "{colors.signal-indigo}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "8px 20px"
  button-primary-hover:
    backgroundColor: "{colors.ion-violet}"
  num-badge:
    backgroundColor: "{colors.accent-tint}"
    textColor: "{colors.ion-violet}"
    rounded: "{rounded.md}"
    size: "36px"
  num-badge-fixed:
    backgroundColor: "{colors.emerald-tint}"
    textColor: "{colors.positive-emerald}"
  num-badge-excluded:
    backgroundColor: "{colors.hot-tint}"
    textColor: "{colors.hot-red}"
  metric-card:
    backgroundColor: "{colors.panel-tint}"
    textColor: "{colors.starlight}"
    rounded: "{rounded.lg}"
    padding: "16px"
  section-panel:
    backgroundColor: "{colors.panel-tint}"
    textColor: "{colors.starlight}"
    rounded: "{rounded.lg}"
    padding: "20px"
  pill:
    backgroundColor: "{colors.emerald-tint}"
    textColor: "{colors.positive-emerald}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  input:
    backgroundColor: "rgba(255,255,255,0.05)"
    textColor: "{colors.starlight}"
    rounded: "{rounded.xs}"
    padding: "2px 6px"
---

# Design System: LotoScope

## Overview

**Creative North Star: "The Night Observatory"**

O LotoScope vive à noite. O fundo é um céu profundo (`#070b1a`) e cada número, métrica ou série aparece como um marcador luminoso observado num instrumento de precisão. A interface não compete com os dados: ela os instrumenta. Densidade alta, mas nunca ruidosa — o analista lê padrões, não decoração.

A paleta carrega significado, não estilo. Índigo é a estrutura (navegação, acento, seleção); esmeralda, âmbar e vermelho são sinais térmicos que só aparecem quando descrevem um estado do dado (quente, atenção, frio, excluído). A atmosfera é científica e noturna: sóbria no repouso, tátil no toque. Superfícies ficam planas paradas e ganham leve elevação, brilho e micro-movimento apenas em resposta a estado (hover, foco, seleção).

Os componentes tendem ao "tátil e confiante": cantos suaves e consistentes, bordas de 1px translúcidas em vez de sombras pesadas, gradientes contidos reservados a momentos de hierarquia (hero, tab ativa, marca). Nada de ornamentos que não informem.

**Key Characteristics:**
- Céu profundo + painéis translúcidos; profundidade tonal, não sombras duras.
- Cor como sinal térmico (quente/frio/positivo/excluído), nunca como enfeite.
- Índigo estrutural e raro; acentos semânticos é que saltam.
- Micro-rótulos uppercase (9–11px) sobre dados em sentence case e números em destaque.
- Movimento por estado: fade/slide/scale de entrada, glow e lift no hover.

## Colors

Paleta noturna de alto contraste: um índigo estrutural sobre campos escuros, com um vocabulário térmico (esmeralda/âmbar/vermelho/azul) reservado à leitura do dado.

### Primary
- **Signal Indigo** (`#6366f1`): acento estrutural. Botões primários, seleção, realces de foco. Raro por design.
- **Ion Violet** (`#818cf8`): índigo claro para texto/badges de acento sobre fundo escuro e estados ativos; a variante legível do accent.
- **Nebula Violet** (`#a78bfa`): terceiro tom do gradiente de marca (logo, título hero).

### Secondary
- **Positive Emerald** (`#10b981`) e **Emerald Bright** (`#34d399`): estado positivo, número fixado/selecionado, acerto de expectativa.
- **Warning Gold** (`#f59e0b`): atenção e destaques neutros-quentes.

### Tertiary
- **Hot Signal Red** (`#ef4444`) / **Hot Red Bright** (`#fca5a5`): número excluído, erro, aviso; vermelho claro para texto sobre fundo.
- **Cold Signal Blue** (`#3b82f6`): polo frio de séries térmicas.
- **Warm Grey** (`#94a3b8`): polo morno/neutro de séries térmicas.

### Neutral
- **Deep Space** (`#070b1a`): fundo global da aplicação (`body`).
- **Deep Space 2** (`#0a0f24`): segundo nível de fundo/overlay.
- **Panel** (`#111630`): fundo sólido de superfície quando a transparência não basta.
- **Starlight** (`#f0f4ff`): texto principal.
- **Ink Bright** (`#e0e7ff`): títulos de seção em índigo-branco.
- **Slate Haze** (`#8892b0`): texto secundário, legendas, eixos de gráfico.
- **Panel Tint** (`rgba(255,255,255,0.03)` / hover `0.06`): preenchimento translúcido de cards e painéis.

### Named Rules
**The Thermal Signal Rule.** Quente/frio/esmeralda/vermelho codificam ESTADO DO DADO (quente, frio, acerto, exclusão). Nunca use uma cor térmica como decoração ou para "deixar bonito".
**The One Accent Rule.** Índigo é o único acento estrutural e ocupa ≤10% de qualquer tela. A raridade é o ponto.

## Typography

**Display Font:** Inter (next/font, subset latin, com fallback `system-ui, -apple-system, sans-serif`)
**Body Font:** Inter (mesma família)
**Label/Mono Font:** mono do sistema (`ui-monospace`) para meta-dados numéricos compactos

**Character:** Uma única família sans neutra e de alta legibilidade, usada em contraste de peso (400 → 800) em vez de contraste de família. A hierarquia vem de peso e tamanho, não de fontes diferentes. Números são os protagonistas.

### Hierarchy
- **Display** (800, 36px / clamp via `text-3xl sm:text-4xl`, lh 1.1): título hero ("Resultado Oficial") e manchetes de destaque.
- **Headline** (800, 30px, lh 1.15): títulos de seção de grande porte.
- **Title** (600, 18px, lh 1.3): cabeçalhos de seção (`Section` h3).
- **Body** (400, 14px, lh 1.5): texto corrente, tabelas, descrições.
- **Label** (600, 11px, tracking 0.05em, **uppercase**): micro-rótulos de métrica, badges e categorias.
- **Mono** (500, 9–10px): detalhes numéricos truncados, notação compacta (`font-mono`).

### Named Rules
**The Uppercase Micro-Label Rule.** Rótulos de dado (categorias, unidades, meta) são uppercase 9–11px com tracking; conteúdo legível fica em sentence case. Nunca escreva parágrafos em uppercase.

## Layout

Modelo de coluna única centralizada, densa e escaneável. Container `max-w-[1360px]` com `px-4 sm:px-5` e `py-4 sm:py-6`. As seções empilham com ritmo `mb-6`/`mb-8`; o Hero abre a página em painel bordado.

- Grid de métricas do Hero: `grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6`, `gap-3`.
- Grades de análise (ex.: previsão): `grid-cols-1 lg:grid-cols-2`, `gap-5`.
- Cabeçalho (TopBar): `sticky top-0`, `backdrop-blur-xl`, fundo gradiente translúcido, navegação de loterias com scroll horizontal.
- Breakpoints observados e efetivos: `sm` (640px) para densidade de grade e exibição de rótulos; `md`/`lg` (768/1024px) para colunas duplas. Alvos são primeiramente desktop analítico, degradando para mobile sem perder legibilidade.
- A página longa é organizada em **4 zonas** (Análise · Previsão & Geração · Conferência · Automação) com uma **sub-nav sticky** (`top-52px`) e cada zona é **colapsável** (estado persistido em `localStorage`), mantendo o WIP visual baixo.

## Elevation & Depth

Híbrido, mas de base plana: a profundidade vem primeiro de **camadas tonais translúcidas** (painéis `rgba(255,255,255,0.03)` sobre o céu, com bordas de 1px) e só depois de sombra/brilho. Sombras duras não são linguagem do sistema; quando existem, são ambientais e tingidas de índigo, amarradas a estado (hover, seleção) ou a elementos flutuantes (tooltip, tab ativa, header sticky).

### Shadow Vocabulary
- **Accent glow** (`box-shadow: 0 0 20px rgba(129,140,248,0.1)` → `…0.2` no pulso): respiração do Hero e foco de elementos de acento.
- **Selection lift** (`box-shadow: 0 10px 15px -3px rgba(129,140,248,0.15)`): tab ativa / cartão selecionado.
- **Floating tooltip** (`box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1)`): tooltips e popovers sobre painéis.

### Named Rules
**The Glow-on-State Rule.** Superfícies são planas no repouso. Brilho e elevação aparecem apenas como resposta a estado (hover, foco, seleção) — nunca como decoração estática.

## Shapes

Linguagem de cantos suaves e consistentes, com bordas de 1px translúcidas como delimitação primária. Uma única família de raio cobre todos os componentes:
- `4px` (rounded) — inputs compactos.
- `6–8px` (rounded-md/lg) — botões, badges de número, tabs.
- `12px` (rounded-xl) — cards de métrica e painéis de seção.
- `16px` (rounded-2xl) — painel Hero.
- `9999px` (rounded-full) — pills, dot indicators, indicador de tab ativa.

Bordas: `1px solid rgba(129,140,248,0.12)` em superfícies bordadas e `1px solid rgba(255,255,255,0.06)` em cards tonais. Círculos (dots de status, spinner) usam `rounded-full`. Sem clipping diagonal, chanfro ou silhuetas afiadas.

### Named Rules
**The Single Radius Family Rule.** Todo canto pertence à mesma família de raio. Não invente raios avulsos; se um canto precisa de outra curvatura, ela é `full` (pílula) ou já existe na escala.

## Components

### Buttons
- **Shape:** cantos `8px` (rounded-lg).
- **Primary:** fundo gradiente `linear-gradient(135deg,#6366f1,#818cf8)`, texto branco, `px-5 py-2`, `text-sm font-semibold`; usado para a ação principal (ex.: "Tentar novamente").
- **Hover / Focus:** `hover:brightness-110`, transição `200ms`; foco realça o anel de acento.
- **Ghost / Tab:** tabs de loteria sem fundo no repouso (`text-muted`, `hover:text-[#c4c9e8] hover:bg-white/[0.04]`); a tab ativa recebe fundo gradiente índigo translúcido, borda `rgba(129,140,248,0.2)` e indicador inferior de 3px.

### Chips
- **Style:** pills `rounded-full`, fundo tingido (ex.: `bg-emerald/15`) com texto na mesma cor e borda `1px` na cor, `text-[11px] font-semibold uppercase tracking-wider`.
- **State:** o pill é informativo (status do sorteio, tag "Beta"); a tab de loteria é a variante acionável/selecionável.

### Cards / Containers
- **Corner Style:** `12px` (rounded-xl) para cards de métrica e painéis; `16px` para o Hero.
- **Background:** `rgba(255,255,255,0.03)` tonal sobre o céu; Hero usa gradiente `linear-gradient(135deg,#0f1429,#1a1040,#0f1a2e)`.
- **Shadow Strategy:** ver Elevation & Depth — plano no repouso, glow/lift no hover.
- **Border:** `1px solid rgba(255,255,255,0.06)` (tonal) ou `rgba(129,140,248,0.12)` (bordado).
- **Internal Padding:** `p-4` (métricas), `p-5` (painéis), `p-6 sm:p-8 lg:p-10` (Hero).
- **No nesting:** os tiles de métrica dentro do painel Hero são **células de estatística sem chrome** (sem fundo/borda em repouso) — o fundo/borda só aparece no hover. Nunca coloque um card dentro de outro.

### Inputs / Fields
- **Style:** fundo `rgba(255,255,255,0.05)`, borda `1px solid rgba(255,255,255,0.10)`, raio `4px`, texto `text-fg text-xs`, padding compacto `px-1.5 py-0.5`.
- **Focus:** remoção do outline nativo + realce de borda/acento (sem glow pesado).
- **Placeholder:** `text-muted/50`; campos numéricos usam `inputMode="numeric"` e `datalist` para sugestões.

### Navigation
- **Style:** header sticky com `backdrop-blur-xl` e gradiente translúcido (`rgba(15,20,41,0.9)` → `rgba(26,16,64,0.9)`); navegação de loterias em `flex` com scroll horizontal no mobile.
- **States:** inativa `text-muted`; ativa com fundo gradiente índigo, borda translúcida e barra de 3px; tipografia `text-[13px] font-semibold` com sub-rótulo mono `text-[9px] opacity-50`.

### Signature: Number Badge (`NumBadge`)
- **Shape:** quadrado `40px` (`w-10 h-10`), `8px` de raio, `text-sm font-semibold`.
- **Default:** fundo `bg-accent/10`, texto `text-accent-2` índigo claro.
- **Fixed:** `bg-emerald/30 text-emerald` + `ring-1 ring-emerald/40` + `scale-110` (selecionado/fixado).
- **Excluded:** `bg-hot/25 text-hot` + `line-through` + `ring-1 ring-hot/30` (riscado).
- **Interaction:** `hover:scale-110 hover:brightness-125`, transição `200ms`; números sorteados ficam `text-emerald`. É o átomo visual do produto — o "marcador luminoso" do observatório.

## Do's and Don'ts

### Do:
- **Do** derivar profundidade de camadas tonais (`rgba(255,255,255,0.03–0.06)`) e bordas de 1px antes de recorrer a sombra.
- **Do** usar índigo como acento estrutural raro e reservar esmeralda/âmbar/vermelho/azul para estado do dado (The Thermal Signal Rule).
- **Do** escrever rótulos de dado em uppercase 9–11px com tracking e manter o conteúdo em sentence case.
- **Do** manter todo canto dentro da família de raio (`4/6/8/12/16/full`) e todo texto em pt-BR com acentuação correta.
- **Do** manter o aviso de jogo responsável e o enquadramento educacional visíveis (compromisso de produto).
- **Do** animar por entrada/estado (`fadeIn` 0.6s, `slideUp` 0.5s, `scaleIn` 0.4s) — não em loop decorativo.
- **Do** respeitar `prefers-reduced-motion`: as animações decorativas (fade/slide/scale/shimmer/typing/pulse) são desligadas e o `hero-glow` some, preservando o estado final visível.

### Don't:
- **Don't** usar cor térmica como decoração ou introduzir uma nova família de acento (viola The One Accent Rule).
- **Don't** empilhar sombras pesadas/escuras como profundidade padrão — profundidade é tonal aqui.
- **Don't** adicionar uma segunda família tipográfica; a hierarquia é por peso. (Nota: Inter é a fonte vigente; o padrão da fábrica a marca como "sobreusada", então só troque-a num redesign explícito, nunca em trabalho escopado.)
- **Don't** fabricar números, rótulos ou estados que não venham dos dados reais do banco (compromisso de produto).
- **Don't** acumular em-dashes no copy nem perder acentuação pt-BR.
- **Don't** reintroduzir `background-clip: text` (gradient-text) nem glow cromático zero-offset (`box-shadow: 0 0 Npx cor`) — removidos nesta passada. A marca usa gradiente apenas em *fundos* (badge do logo, tab ativa, painel Hero).
