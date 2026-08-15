# HANDOFF — Matriz de Quarentena: análise, correção e automação

> **Para o agente da próxima sessão:** este documento transfere todo o trabalho feito
> (por engano) no repositório `RDESK` para este projeto (**LotoScope**, o correto).
> Leia tudo antes de agir. O usuário pediu: *"aplica o handoff"*.
> Gerado em 12/08/2026 · Base de dados: concursos 1 a **3759** (último: 11/08/2026).

---

## 1. Contexto

O usuário mantém um **dashboard Lotofácil neste repositório (LotoScope)** com seletor
superior de concurso ("Concurso base" com botões −/+), seções de estatísticas,
Posicional vs anterior, Previsões, Quentes/Mornos/Frios, Probabilidade por Posição e
a seção **🛡️ Matriz de Quarentena por Posição**.

Pedidos do usuário (nesta ordem):
1. A matriz de quarentena "não parece 100% ajustada" → analisar com o histórico e propor ajustes. **(FEITO — ver §2 e §3)**
2. A matriz deve se **atualizar automaticamente** quando sair concurso novo. **(FEITO no RDESK — portar, ver §5)**
3. A matriz deve **seguir o seletor superior de concurso** do dashboard: ao mudar o concurso, a matriz mostra o status como estava naquele concurso (visão por concurso). **(PENDENTE — fazer aqui no LotoScope, ver §6)**

⚠️ Por erro de abertura de projeto, a implementação de automação + um dashboard novo
foram criados em `C:\Users\AR CALHAU\source\repos\RDESK\lotofacil\`. **Não usar aquele
dashboard novo** — o alvo é o dashboard já existente do LotoScope. Os assets do RDESK
servem de base para porte (§5).

---

## 2. Diagnóstico da matriz original (evidências)

Cruzamento da matriz do usuário (44 Q / 15 A / 19 M) com o histórico oficial completo:

1. **Quarentena inconsistente**: só **21 das 44** células Q realmente saíram nos últimos
   3 concursos; **14 células** que saíram nos últimos 3 concursos não estavam marcadas Q
   (ex.: N5:6, N6:7, N7:9, N8:10, N9:11 saíram no próprio 3759). Nenhuma janela (1–6)
   ou referência de concurso fecha as 44 — não é só defasagem, a regra/base está errada.
2. **Erros críticos de classificação**:
   - `N4:4` marcado **M** (muito atrasado) mas saiu no concurso **3757** (gap 2) → é Q.
   - `N9:11` marcado **A** mas saiu no **3759** (gap 0) → é Q.
3. **Células raras tratadas como atraso**: `N15:19` (p≈0,09%/concurso) marcada M com
   gap 1.495, quando o gap esperado é ~1.068 → ausência é **estrutural**, não sinal.
   Idem N9:9, N10:11, N11:12, N14:17, N13:16.
4. **Inconsistência interna**: lista "Muito Atrasados" tinha 18 itens, matriz mostrava
   19 (faltava `N15:19` na lista).
5. **Inspetor de célula aceita célula inviável**: exibiu `N11:23` ("gap 3757 sorteios,
   Status: Normal") — mas na posição N11 o maior número possível é **21**. Células
   inviáveis devem ser bloqueadas/marcadas como "·".

---

## 3. Regra corrigida (aprovada pelo usuário)

Posições = dezenas **ordenadas** do sorteio (N1 = menor … N15 = maior).

- **Viabilidade**: posição `k` (1–15) só admite número `n` com `k ≤ n ≤ 10+k`.
  Fora disso → `·` (inviável).
- **Probabilidade da célula**: `p(k,n) = C(n-1, k-1) × C(25-n, 15-k) / C(25,15)`.
  Gap esperado = `1/p` concursos.
- **Q (Quarentena)**: a célula saiu em um dos últimos **3** concursos.
- **A (Atrasado)**: `gap ≥ 1.75 × (1/p)` · **M (Muito Atrasado)**: `gap ≥ 3.0 × (1/p)`.
  (gap normalizado pela probabilidade — NUNCA usar contagem fixa de concursos.)
- **R (Rara estrutural)**: `p × total_concursos < 10` → atraso não é mensurável;
  nunca classificar como A/M.
- Célula viável que **nunca saiu** e não é R → **N** (sem evidência de atraso).

### Matriz de referência @ concurso 3759 (usar para VALIDAÇÃO)

```
Núm  N1 N2 N3 N4 N5 N6 N7 N8 N9 N10 N11 N12 N13 N14 N15
1    Q  ·  ·  ·  ·  ·  ·  ·  ·  ·   ·   ·   ·   ·   ·
2    N  Q  ·  ·  ·  ·  ·  ·  ·  ·   ·   ·   ·   ·   ·
3    N  Q  Q  ·  ·  ·  ·  ·  ·  ·   ·   ·   ·   ·   ·
4    A  N  Q  Q  ·  ·  ·  ·  ·  ·   ·   ·   ·   ·   ·
5    A  A  N  Q  A  ·  ·  ·  ·  ·   ·   ·   ·   ·   ·
6    N  M  N  N  Q  N  ·  ·  ·  ·   ·   ·   ·   ·   ·
7    R  A  A  N  N  Q  N  ·  ·  ·   ·   ·   ·   ·   ·
8    R  N  M  M  Q  Q  N  N  ·  ·   ·   ·   ·   ·   ·
9    R  R  N  M  N  Q  Q  N  R  ·   ·   ·   ·   ·   ·
10   R  R  N  M  A  N  M  Q  N  R   ·   ·   ·   ·   ·
11   R  R  R  A  N  N  Q  N  Q  A   R   ·   ·   ·   ·
12   ·  R  R  N  A  A  N  Q  N  Q   R   R   ·   ·   ·
13   ·  ·  R  R  N  N  A  N  Q  N   Q   R   R   ·   ·
14   ·  ·  ·  R  R  N  N  M  N  Q   N   Q   R   R   ·
15   ·  ·  ·  ·  R  N  A  N  Q  N   N   N   R   R   R
16   ·  ·  ·  ·  ·  R  N  N  N  M   N   N   N   R   R
17   ·  ·  ·  ·  ·  ·  R  N  N  Q   Q   N   Q   R   R
18   ·  ·  ·  ·  ·  ·  ·  N  N  N   N   Q   N   N   R
19   ·  ·  ·  ·  ·  ·  ·  ·  N  A   N   N   A   N   R
20   ·  ·  ·  ·  ·  ·  ·  ·  ·  N   Q   N   Q   N   N
21   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·   N   Q   N   N   N
22   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·   ·   N   Q   A   N
23   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·   ·   ·   N   Q   N
24   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·   ·   ·   ·   Q   Q
25   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·   ·   ·   ·   ·   Q
```
**Totais: Q=35 · A=16 · M=8 · R=36**

Últimos 3 sorteios em 3759 (base da quarentena):
- 3757: 01 02 03 04 06 08 11 12 15 17 20 21 22 23 24
- 3758: 01 03 04 05 08 09 11 12 13 14 17 18 20 24 25
- 3759: 01 02 04 05 06 07 09 10 11 12 13 14 17 24 25

Listas @3759:
- **M (8)**: N2:6 (gap 85) · N3:8 (128) · N4:8 (25) · N4:9 (41) · N4:10 (110) · N7:10 (21) · N8:14 (18) · N10:16 (18)
- **A (16)**: N1:4 (83) · N1:5 (195) · N2:5 (24) · N2:7 (128) · N3:7 (24) · N4:11 (194) · N5:5 (32) · N5:10 (25) · N5:12 (72) · N6:12 (25) · N7:13 (20) · N7:15 (47) · N10:11 (365) · N10:19 (27) · N13:19 (26) · N14:22 (11)

Observação: no dashboard do usuário, com seletor em **3758**, a matriz exibia Q=46
(incluindo N9:14 — hit em 3756, dentro da janela em 3758 ✓). Verificar se o dashboard
já recompute por concurso com outra regra de janela; alinhar com a regra do §3.

---

## 4. Fontes de dados (testadas em 12/08/2026)

1. `https://loteriascaixa-api.herokuapp.com/api/lotofacil` — histórico completo (JSON, ~5 MB)
   - `/latest` → último concurso · `/{n}` → concurso n
   - formato: `{concurso, data: "dd/mm/aaaa", dezenas: ["01",...]}` (ordenadas)
2. **Fallback oficial Caixa**: `https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/`
   - raiz = último · `/{n}` = concurso n
   - formato: `{numero, dataApuracao, listaDezenas: ["01",...]}`

Cache pronto com os 3.759 concursos em:
`C:\Users\AR CALHAU\source\repos\RDESK\lotofacil\historico.json`
(formato: `[{concurso:int, data:str, dezenas:[int×15] ordenadas}]` — pode ser copiado).

---

## 5. Assets construídos no RDESK (portar para cá)

| Asset | Origem (RDESK) | Ação no LotoScope |
|---|---|---|
| Atualizador automático | `RDESK\lotofacil\atualizar_matriz.py` | Adaptar para atualizar a **fonte de dados do dashboard LotoScope** (não gerar MD novo, salvo se útil) |
| Cache histórico | `RDESK\lotofacil\historico.json` | Copiar/adaptar ao formato de dados do LotoScope |
| Template de dashboard | `RDESK\lotofacil\dashboard_template.html` | **NÃO portar** (foi um dashboard paralelo criado por engano) |
| Tarefa agendada Windows | `Lotofacil-MatrizQuarentena` (diário 21:45, roda o script do RDESK) | **Reapontar** para o script no LotoScope ou recriar; remover a antiga |

Lógica do atualizador (manter): consulta `/latest` → sem concurso novo, sai em
silêncio → com concurso novo, baixa só o(s) que falta(m), atualiza cache, recalcula,
grava log. Só stdlib. Parâmetros no topo: `JANELA_Q=3`, `LIM_A=1.75`, `LIM_M=3.0`,
`RARO_MIN_HITS=10`.

---

## 6. Tarefas no LotoScope (o que falta)

1. **Localizar** o dashboard e a seção da Matriz de Quarentena + o seletor
   "Concurso base" (buscar por `Quarentena`, `Concurso base`, `análise até concurso`).
2. **Matriz segue o seletor**: ao mudar o concurso base, recomputar a classificação
   usando apenas concursos ≤ selecionado (visão por concurso). Eficiente: pré-indexar
   hits por célula `pos*100+num → [concursos]` e busca binária do último hit ≤ T.
3. **Aplicar a regra corrigida** (§3), incluindo classe **R** e células inviáveis `·`.
4. **Corrigir o inspetor de célula** (caso `N11:23`): bloquear células inviáveis.
5. **Automação**: integrar o atualizador (§5) ao fluxo de dados do LotoScope e
   reapontar a tarefa agendada; remover a tarefa antiga do RDESK:
   `Unregister-ScheduledTask -TaskName "Lotofacil-MatrizQuarentena"`
6. **Limpeza**: perguntar ao usuário se deseja apagar `RDESK\lotofacil\` após o porte.

## 7. Checklist de aceite

- [x] Seletor no concurso **3759** → matriz idêntica à referência do §3 (Q=35, M=8, A=16, R=36).
      **APLICADO em 12/08/2026** — totas batem via API `dashboard-data?concurso=3759` e pelo
      script `dashboard/scripts/validar-matriz-quarentena.mjs` (11/11 asserts).
- [x] Seletor em concursos anteriores → matriz muda corretamente (ex.: 3758 → N9:14 = Q).
      **Validado** — a visão por concurso já era nativa (slice server-side em `analiseCompleta`).
- [x] Células inviáveis não classificam nem abrem no inspetor (N11:23 bloqueado).
      **APLICADO** — novo status `inviavel` (renderiza `·`, sem hover) em
      `QuarantineMatrixLotofacil.tsx`.
- [x] Tarefa agendada aponta para o LotoScope e atualiza os dados do dashboard.
      **APLICADO em 12/08/2026** — nova task `lotofacil_auto` (diário 21:45) roda
      `atualizar_lotofacil_auto.py` (`.venv\Scripts\pythonw.exe`, Start in = raiz do
      projeto), que chama `AtualizadorLotofacil.atualizar_completo()` e alimenta
      `Resultados_INT`. Task antiga `Lotofacil-MatrizQuarentena` (RDESK) — **removida**.
      Log: `atualizacao_auto_lotofacil.log`. Testado manualmente (DB em dia, 0 pendentes).
      Pasta `C:\Users\AR CALHAU\source\repos\RDESK\lotofacil` — **apagada** por opção do usuário.
- [x] `N4:4` nunca mais aparece como M estando com gap 2. 😄 **Validado** — agora é Q.

**Regra aplicada (grafo `agf`, epic `node_e138c692a6d3`):**
- `dashboard/src/lib/analise-completa.ts` → `calcularQuarentenaPorPosicao` reescrita:
  viabilidade, p teórico via combinatória, Q (janela 3), A/M (gap ≥ 1.75x/3.0x do esperado),
  R (p×total < 10), N (nunca saiu, não rara).
- `dashboard/src/types/index.ts` → status ampliado (`rara`, `inviavel`) + `prob_teorica`
  e `gap_esperado`.
- `dashboard/src/components/QuarantineMatrixLotofacil.tsx` + `QuarantineMatrix.tsx` →
  legendas/cores R e `·`; inspetor mostra P teórica e gap esperado; inviáveis bloqueados.
- `dashboard/scripts/validar-matriz-quarentena.mjs` → artefato de teste reutilizável.
- `npm run build` OK.
