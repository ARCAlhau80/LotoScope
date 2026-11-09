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

# t=9 (2.003 blocos)
dotnet run -c Release -- --t 9  --pool 50000   --out ..\..\c9.json

# t=10 (5.527)
dotnet run -c Release -- --t 10 --pool 40000   --out ..\..\c10.json

# t=11 (14.969)
dotnet run -c Release -- --t 11 --pool 100000  --out ..\..\c11.json

# t=12 (43.786)
dotnet run -c Release -- --t 12 --pool 300000  --out ..\..\c12.json

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
| 9 | 2.003 | 24 s | 544 | 3,68× | 88 KB |
| 10 | 5.527 | 12 s | 1.359 | 4,07× | 225 KB |
| 11 | 14.969 | 16 s | 3.370 | 4,44× | 608 KB |
| 12 | 43.786 | 18 s | 13.175 | 3,32× | 1,8 MB |
| 13 | 136.921 | 38 s | 58.887 | 2,33× | 5,6 MB |
| 14 | 537.040 | 11 s | 297.172 | 1,81× | 21,8 MB |
| 15 | 3.268.760 | — | 3.268.760 | 1,00× | ~150 MB |

O greedy fica ~1,6–1,8× o ótimo conhecido nos casos pequenos
(t=4: 33 vs 21; t=5: 72 vs 42; t=6: 163 vs 94). Para chegar mais perto do
melhor conhecido seria necessário um local search (LNS/SA) por cima.

## Integração no app

`t=9..12` estão embutidos em `dashboard/src/data/covers-lotofacil.json`
com `verificado: true`. A rota usa esse selo para não reenumerar
`C(25,t)` a cada request.

`t=13..15` **não** entram no bundle: gere com o comando acima e use o
arquivo como exportação. Para `t=15` a cobertura é trivialmente todas as
combinações de 15 dezenas em 25.
