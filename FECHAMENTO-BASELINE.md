# Fechamento — Baseline dos geradores

> **Estado congelado em 2026-11-15 (commit `69dff39`).**
> Os geradores de fechamento para **Lotofácil k=15** e **Mega-Sena k=6** estão
> considerados **perfeitos**. Qualquer alteração nos geradores (código, registro
> de designs ou parâmetros padrão) **exige confirmação explícita do usuário**
> antes de ser implementada.
>
> Aditivo (não mexe nos defaults): caminho `k > m` por complementos, com designs
> `L(25,k,15,11)` registrados para k=16..20 — ver "Implementado" abaixo.

## Escopo congelado

| Arquivo | Papel |
|---|---|
| `dashboard/src/lib/fechamento-combinatorio.ts` | núcleo (cover, lotto design `L(v,k,m,t)`, verificação) |
| `dashboard/src/lib/fechamento/lotto.ts` | registro e mapeamento dos lotto designs |
| `dashboard/src/data/lotto-lotofacil.json` | designs verificados da Lotofácil |
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

## Pendente — Mega-Sena k=7..20 (t=4, universo 60)

O Lotto design existe e é muito menor que o cover, mas a enumeração de
`C(60,6) = 50.063.860` sorteios inviabiliza o construtor atual. Cotas
inferiores (apostas × C(k,6) × R$ 6,00 = custo mínimo):

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

Observação: com universo reduzido (fixos/excluídas, `v ≤ 30`) o caminho do
Lotto design **já funciona hoje** para Mega-Sena com `k > 6`.
