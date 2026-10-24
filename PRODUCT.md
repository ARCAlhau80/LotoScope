# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Analistas e estudiosos de loterias. O usuário primário explora padrões históricos, backtests, tendências posicionais e ROI para decidir quais estratégias e dezenas usar. Não é um apostador casual de uma jogada só: opera em sessões de análise sobre concursos, com comparação entre estratégias e conferência de resultados.

## Product Purpose

Sistema científico de análise e geração de combinações otimizadas para loterias brasileiras, com foco em Lotofácil (e também Mega-Sena, Quina, Super Sete, Lotomania, Timemania, Dupla Sena, Dia de Sorte e Mais Milionária). Reúne estatística, machine learning e interface web interativa num único ambiente. Sucesso significa entregar leitura estatística confiável e combinações defensáveis a partir do histórico real de sorteios.

## Positioning

O mecanismo que diferencia o LotoScope é a estratégia **Pool 23 Híbrido** validada com jackpots reais (concursos 3474 e 3610), além de dezenas de módulos de análise especializados (transições posicionais, ciclos, repetições, quarentena, bandas posicionais, correlações). O sistema combina ML e análise estatística sobre o histórico completo do banco em vez de heurísticas genéricas.

## Operating Context

- Ambiente local Windows; interface servida em `localhost` (Flask em `web/frontend/`; app Next.js em `dashboard/`, `next dev --port 3003`).
- Fonte de dados: SQL Server local (servidor `VADER`, database `LOTOFACIL`, tabela principal `RESULTADOS_INT`) e o arquivo `LotoScope.db`; análise organizada por número de concurso.
- Uso por sessões de análise: selecionar concurso, inspecionar seções estatísticas, gerar/verificar combinações, comparar estratégias.
- Superfície principal de design: o app **`dashboard/`** (Next.js 15 + React 19 + TypeScript + Tailwind 4). A interface `web/frontend/` (templates Jinja + CSS puro) é uma superfície secundária/legada.

## Capabilities and Constraints

- Loterias cobertas: Lotofácil, Mega-Sena, Quina, Super Sete, Lotomania, Timemania, Dupla Sena, Dia de Sorte, Mais Milionária.
- Seções/módulos do dashboard: previsão posicional, ciclos, reentradas, streaks/tendência, grupos, comparativo, transição, quarentena (matriz), QMF, ranking de combinações, conferidor, atrasados, palpite, jogos diversos, Super Sete, análise por IA.
- Restrições confirmadas:
  - **Dados reais apenas** — toda estatística/gráfico vem do banco local; nunca fabricar números, métricas ou resultados.
  - **pt-BR com acentuação correta** — copy em português do Brasil, sem em-dash saturado.
  - **Aviso de jogo responsável** — manter o enquadramento educacional/científico e o disclaimer legal.
  - **Local, sem telemetria** — roda em localhost; não introduzir tracking ou dependências externas de coleta.
- Identidade/estrutura atuais não foram declaradas como intocáveis; redesign é permitido se preservar as restrições acima (o usuário NÃO exigiu "refino, não redesign").

## Brand Commitments

Nome: **LotoScope**. Discurso científico/analítico, com liderança por evidência (jackpots validados, ROI medido). Sem emblemas visuais de apostas de azar como marca; tom técnico e confiável.

## Evidence on Hand

- Código real das superfícies: `dashboard/src/components/*.tsx` (~28 componentes), `dashboard/app/page.tsx`, `web/frontend/templates/*.html`, `web/frontend/static/css/*.css`.
- Alegações documentadas (tratar como hipótese verificável, não reafirmar sem fonte): 2 jackpots validados (concursos 3474 e 3610), Pool 23 Híbrido com 21% de taxa de jackpot, ROI +118.6% (ver `README.md`).
- Scripts de análise e backtest no raiz do repo (Python) e `dashboard/scripts/*`.
- **Ausências que o trabalho futuro não pode inventar:** depoimentos de usuários, casos de imprensa, benchmarks de terceiros, pricing ou promessas de ganho garantido.

## Product Principles

1. **Evidência acima de estética** — nenhuma tela afirma ou exibe dado que não venha do banco; a UI serve à leitura correta da estatística.
2. **Densidade analítica legível** — muita informação por tela (matrizes, rankings, séries), mas com hierarquia e escaneabilidade para o analista.
3. **Transparência metodológica** — deixar claro de onde vem cada métrica e o que é histórico vs predição.
4. **Local e privado** — funciona inteiramente na máquina do usuário, sem telemetria.
5. **Uso responsável** — enquadramento educacional/científico e aviso de risco sempre presentes.
