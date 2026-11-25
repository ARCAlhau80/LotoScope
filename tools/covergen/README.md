# covergen — gerador de covering designs C(25,15,t)

Gerador offline para os `t` que não existem no catálogo La Jolla/Zenodo
(o repositório oficial para em `t=8`).

Algoritmo: **greedy exato de máxima cobertura** com CSR reverso
(`t-subconjunto -> candidatos`) e buckets por ganho.

```
O(P · C(k,t))  operações,  memória ~ O(P · C(k,t) + 2^v)
```

## Uso

```powershell
cd tools/covergen

# t=9 (1.962 blocos) — warm start no cover de t=8 + pool maior
dotnet run -c Release -- --t 9  --pool 79000   --seed 1 --warm c8.json --out ..\..\c9.json

# t=10 (5.154)
dotnet run -c Release -- --t 10 --pool 130000  --seed 1 --out ..\..\c10.json

# t=11 (13.924)
dotnet run -c Release -- --t 11 --pool 290000  --seed 2 --out ..\..\c11.json

# t=12 (40.504)
dotnet run -c Release -- --t 12 --pool 879000  --seed 1 --out ..\..\c12.json

# t=13 (136.921) — exportação
dotnet run -c Release -- --t 13 --pool 1500000 --out ..\..\c13.json

# t=14 (537.040) — exportação (pool 0 = todos os C(25,15))
dotnet run -c Release -- --t 14 --pool 0       --out ..\..\c14.json

# t=15 = todas as C(25,15)=3.268.760 apostas (exportação; ~150 MB)
dotnet run -c Release -- --t 15 --pool 0       --out ..\..\c15.json
```

`--warm arquivo.json` reaproveita um cover menor (campo `blocos`) como base.
`--seed N` muda o pool aleatório (múltiplas execuções → escolha a menor).

## Resultados medidos (v=25, k=15)

| t | blocos | tempo | LB (Schönheim) | fator | arquivo |
|---:|---:|---:|---:|---:|---:|
| 9 | **1.962** | 39 s | 544 | 3,61× | 86 KB |
| 10 | **5.154** | 40 s | 1.359 | 3,79× | 226 KB |
| 11 | **13.924** | 45 s | 3.370 | 4,13× | 612 KB |
| 12 | **40.504** | 64 s | 13.175 | 3,07× | 1,7 MB |
| 13 | 136.921 | 38 s | 58.887 | 2,33× | 5,6 MB |
| 14 | 537.040 | 11 s | 297.172 | 1,81× | 21,8 MB |
| 15 | 3.268.760 | — | 3.268.760 | 1,00× | ~150 MB |

Os valores acima usam pool maior (até o limite de 400 M de incidências),
warm start no cover de `t-1` quando ajuda e uma **poda de blocos redundantes**
(remove blocos cujos alvos já estão cobertos por outros) antes de gravar o JSON.
A poda sozinha reduziu os covers antigos em 6/13/25/144 blocos; o pool maior foi
o que mais rendeu (ex.: `t=12`: 43.786 → 40.504).

O greedy ainda fica ~1,6–1,8× o ótimo conhecido nos casos pequenos
(t=4: 33 vs 21; t=5: 72 vs 42; t=6: 163 vs 94). Para chegar mais perto do
melhor conhecido seria necessário um local search (LNS/SA) por cima.

## LNS (`--improve`)

`--improve N` roda um **ruin & recreate (LNS + SA)** por `N` segundos depois do greedy:

- **destroy**: metade das iterações remove todos os blocos que cobrem um
  `t`-subconjunto sorteado (alvo único); a outra metade sorteia vários alvos
  (multi-alvo), forçando uma re-cobertura maior.
- **reparo**: para cada alvo descoberto, escolhe o candidato que o contém e
  cobre mais alvos descobertos (ganho incremental).
- **tabu**: os blocos removidos não podem ser re-adicionados na mesma iteração.
- **aceitação**: SA — aceita piora com probabilidade `exp(-Δ/T)`, com `T`
  resfriando linearmente até 0,05; a melhor solução é guardada à parte.
- verificação exaustiva no final; o JSON sai com `fonte` contendo `+ LNS`.

```powershell
# t=9 com warm start e 60 s de LNS
dotnet run -c Release -- --t 9 --pool 79000 --seed 1 --warm c8.json --improve 60 --out ..\..\c9.json
# qualquer (v,k,t) pequeno com pool completo
dotnet run -c Release -- --v 12 --k 6 --t 4 --pool 0 --improve 10 --out ..\..\c12_6_4.json
```

Validação (10 s de LNS, pool completo):

| instância | greedy | LNS |
|---|---:|---:|
| C(10,5,3) | 19 | **17** |
| C(12,6,4) | 52 | **46** |

Nos casos `v=25,k=15,t=9..12` com os pools atuais, o LNS **não reduziu** em
90–120 s: o greedy já é um mínimo local forte e o pool cobre só ~1–2,5% dos
`C(25,15)` blocos. As reduções de `t=9..12` documentadas acima vieram de pools
maiores + poda de redundantes. Para atacar esses casos com LNS seria preciso um
reparo sem pool (construir candidatos a partir dos alvos descobertos) ou
re-otimização por CP-SAT em subconjuntos.

## Integração no app

`t=9..12` estão embutidos em `dashboard/src/data/covers-lotofacil.json`
com `verificado: true`. A rota usa esse selo para não reenumerar
`C(25,t)` a cada request.

`t=13..15` **não** entram no bundle: gere com o comando acima e use o
arquivo como exportação. Para `t=15` a cobertura é trivialmente todas as
combinações de 15 dezenas em 25.
