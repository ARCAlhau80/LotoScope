# Fechamento — Baseline dos geradores

> **Estado congelado em 2026-11-15 (commit `69dff39`).**
> Os geradores de fechamento para **Lotofácil k=15** e **Mega-Sena k=6** estão
> considerados **perfeitos**. Qualquer alteração nos geradores (código, registro
> de designs ou parâmetros padrão) **exige confirmação explícita do usuário**
> antes de ser implementada.
>
> Aditivo (não mexe nos defaults): caminho `k > m` por complementos, com designs
> `L(25,k,15,11)` registrados para k=16..20 — ver "Implementado" abaixo. O
> registro agora é consultado **antes** do limite de 30 dezenas, o que permite
> design verificado para universos grandes (Mega-Sena); nenhum design de v=60 foi
> registrado por inviabilidade econômica — ver "Avaliado e NÃO registrado".

## Escopo congelado

| Arquivo | Papel |
|---|---|
| `dashboard/src/lib/fechamento-combinatorio.ts` | núcleo (cover, lotto design `L(v,k,m,t)`, verificação) |
| `dashboard/src/lib/fechamento/lotto.ts` | registro e mapeamento dos lotto designs |
| `dashboard/src/data/lotto-lotofacil.json` | designs verificados da Lotofácil |
| `dashboard/src/data/lotto-megasena.json` | registro da Mega-Sena (hoje vazio, por decisão) |
| `dashboard/app/api/fechamento/route.ts` (bloco do Lotto design) | escolha cover × lotto, limites |
| `dashboard/src/lib/fechamento/config.ts` | k/t padrão, dezenas sorteadas, preço |

## Referências validadas (não regredir)

### Lotofácil — k=15, t=11

| Cenário | Apostas | Garantia |
|---|---|---|
| Sem fixos/excluídas | 14.944 | 100% dos C(25,11) |
| 2 fixos (condicional) | 33 | 11 (5 fixos + 6) |
| 3 fixos | 26 | 11 |
| 4 fixos | 20 | 11 |
| 5 fixos | 11 | 11 |
| 10 excluídas | 1 | piso 15 |
| 5 excluídas | 4 | piso 11 em C(20,15) = 15.504 sorteios |
| 4 excluídas | 4 | piso 11 |
| 3 excluídas | 6 | piso 11 |
| 2 excluídas | 21 | piso 11 |
| 2 fixos + 5 excluídas | 3 | piso 11 |

Piso condicional aos excluídos (universo efetivo): 10 excluídas → 15;
2 a 6 excluídas → 11 (piso do próprio design); 2 fixos + 5 excluídas → 11.

### Mega-Sena — k=6, t=4

| Cenário | Apostas |
|---|---|
| 54 excluídas (universo 6) | 1 (piso 6) |

## Regra de mudança

1. **Nenhuma alteração em gerador sem confirmação do usuário.**
2. Toda mudança precisa de: `npx tsc --noEmit`, verificação exaustiva do design,
   teste no navegador e registro do design (quando aplicável).
3. Não alterar os defaults `k=15` (Lotofácil) e `k=6` (Mega-Sena).

## Implementado — Lotofácil k=16..20 (t=11)

Antes: o Lotto design não entrava (`C(25,15) = 3.268.760` > limite de 800.000) e
o fechamento caía no guloso amostrado com 200 apostas — cobertura **parcial**:
18,5% (k=16), 45,2% (k=17), 80,7% (k=18), 98,7% (k=19), 100% (k=20).

Agora existem dois caminhos:

1. **Registro** (`lotto-lotofacil.json`) com `L(25,k,15,11)` para k=16..20 —
   consulta instantânea, sem enumeração no request.
2. **Construtor por complementos** (`construirLottoDesignComplemento`) para
   qualquer `k > m`: bloco `B = Aᶜ` de `v−k`, alvo `S = Dᶜ` de `v−m`, limiar
   `t* = t − (k + m − v)`, porque `|A∩D| = k+m−v + |B∩S|`. Entra quando
   `C(v,m) > 800.000` e `C(v, v−m) ≤ 4.000.000`
   (`LIMITE_ALVOS_LOTTO_COMPLEMENTO`), com orçamento de 5 s.

Designs verificados exaustivamente (3.268.760 sorteios, falhas = 0):

| k | Apostas | Piso | Cota inferior |
|---|---|---|---|
| 16 | 28 | 11 | 5 |
| 17 | 10 | 11 | 3 |
| 18 | 4 | 11 | 2 |
| 19 | 4 | 11 | 2 |
| 20 | 4 | 11 | 4 (ótimo provado) |

Com exclusões/fixos o construtor por complementos resolve na hora (verificado
contra a API enumerando todos os sorteios do universo efetivo):

| Cenário | Apostas | Piso |
|---|---|---|
| k=16, 1 excluída (v=24) | 15 | 11 |
| k=17..19, 1 excluída | 4 | 11 |
| k=20, 1 excluída | 1 | 11 |
| k=16, 2 excluídas (v=23) | 6 | 11 |
| k=16, 3 excluídas (v=22) | 4 | 11 |
| k=16, 4 excluídas (v=21) | 4 | 11 |
| k=17, 1 fixo (v=24) | 43 | 12 (1 fixo + 11) |
| k=18, 1 fixo | 18 | 12 |
| k=19, 1 fixo | 6 | 12 |
| k=20, 1 fixo | 4 | 12 |
| k=19, 2 fixos (v=23) | 30 | 13 |
| k=20, 2 fixos | 8 | 13 |

Limitação conhecida: k=16 com 1–2 fixos e k=17/18 com 2 fixos **não fecham** no
guloso por bitset (o limiar `t*` fica alto demais); gastam até 5 s e caem no
fechamento por cobertura, como antes.

## Avaliado e NÃO registrado — Mega-Sena k=7..20 (t=4, universo 60)

A infraestrutura está pronta (`lotto-megasena.json` vazio + registro na rota,
que agora consulta o registro **antes** do limite de 30 dezenas), mas **nenhum
design de v=60 foi registrado**: a garantia de 4 acertos em 60 dezenas é
economicamente inviável em qualquer `k`, inclusive no piso teórico.

Cotas inferiores por contagem (`C(60,6) / E(k)`, com
`E(k) = C(k,4)·C(60−k,2) + C(k,5)·C(60−k,1) + C(k,6)`), e o custo **mínimo
possível** com aposta de `k` dezenas a R$ 6,00 por combinação de 6:

| k | Apostas (cota inferior) | Custo mínimo |
|---|---|---|
| 7 | 1.015 | R$ 42.630 |
| 8 | 523 | R$ 87.864 |
| 9 | 300 | R$ 151.200 |
| 10 | 186 | R$ 234.360 |
| 11 | 122 | R$ 338.184 |
| 12 | 84 | R$ 465.696 |
| 13 | 60 | R$ 617.760 |
| 14 | 45 | R$ 810.810 |
| 15 | 34 | R$ 1.021.020 |
| 16 | 27 | R$ 1.297.296 |
| 17 | 21 | R$ 1.559.376 |
| 18 | 17 | R$ 1.893.528 |
| 19 | 14 | R$ 2.279.088 |
| 20 | 12 | R$ 2.790.720 |

O que foi construído e medido (`tools/lotto-design/gerar-megasena.mjs`: guloso
esparso guiado por sorteio descoberto + bitset de 50.063.860 bits, `falta === 0`
= prova exaustiva; rank/enumeração validados por `teste-rank-megasena.mjs`):

| k | Cota inferior | Obtido | Fator | Custo real |
|---|---|---|---|---|
| 7 | 1.015 | 7.621 | 7,5× | R$ 320.082 |
| 8 | 523 | 4.170 | 8,0× | R$ 700.560 |
| 10 | 186 | 1.671 | 9,0× | R$ 2.105.460 |
| 11 | 122 | 1.117 | 9,2× | R$ 3.096.324 |
| 12 | 84 | 796 | 9,5× | R$ 4.413.024 |

Conclusão: o piso teórico já custa de R$ 42 mil (k=7) a R$ 2,79 milhões (k=20),
então **não é problema de algoritmo** — nenhuma melhoria do guloso torna o design
utilizável. Decisão: manter o registro vazio e a mensagem da UI explícita
("universo restante com 60 dezenas"); a Mega-Sena segue no cover (k=6) e no
guloso amostrado (k>6).

Universo reduzido (`v ≤ 30`, via exclusões) **funciona** e é o caminho útil:

| Cenário | Apostas | Piso | Cota inferior |
|---|---|---|---|
| 30 excluídas (v=30), k=10 | 79 | 4 | 14 |
| 30 excluídas (v=30), k=12 | 38 | 4 | 7 |
| 30 excluídas (v=30), k=8 | 200 (não fecha) | 3 | 35 |
