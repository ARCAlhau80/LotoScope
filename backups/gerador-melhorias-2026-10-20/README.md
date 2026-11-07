# Gerador — snapshot das melhorias pós-sexta (2026-10-20)

Este diretório guarda o estado do gerador **antes** da reversão para o estado de sexta-feira (16/10/2026 ~20:11–20:15). Use este snapshot para reaplicar facilmente as melhorias implementadas depois:

- ranking determinístico por seed (`seedRankingEstavel`)
- busca local (`buscaLocalRanking`)
- otimização exata (`otimizacao: 'exata'`) com objetivo `top1 | soma | minimo`
- explicabilidade do score (`detalhesScore`)
- backtest de ranking
- seletor de Otimização/Objetivo na UI
- suporte correspondente na API e nos testes

## Arquivos incluídos

```
dashboard/src/lib/gerador-diversificado.ts
dashboard/src/lib/colunas-posicionais.ts
dashboard/src/components/JogosDiversosSection.tsx
dashboard/app/api/jogos-diversos/route.ts
dashboard/scripts/validar-ordenacao.ts
dashboard/scripts/validar-ranking-exato.ts
dashboard/scripts/validar-backtest-ranking.ts
dashboard/scripts/backtest-ranking.ts
```

> A rota `dashboard/app/api/jogos-diversos/export/route.ts` **não** foi capturada antes da reversão. A versão atual dela é a de sexta + correção de `parseOrdenacao`/`parseScoreSets` no `POST`. Se a melhoria exigir exportação com exata/objetivo, porte a lógica da rota principal.

## Como reaplicar (PowerShell, a partir da raiz do repo)

```powershell
$src = "backups\gerador-melhorias-2026-10-20\dashboard"

Copy-Item "$src\src\lib\gerador-diversificado.ts" "dashboard\src\lib\gerador-diversificado.ts" -Force
Copy-Item "$src\src\lib\colunas-posicionais.ts" "dashboard\src\lib\colunas-posicionais.ts" -Force
Copy-Item "$src\src\components\JogosDiversosSection.tsx" "dashboard\src\components\JogosDiversosSection.tsx" -Force
Copy-Item "$src\app\api\jogos-diversos\route.ts" "dashboard\app\api\jogos-diversos\route.ts" -Force
Copy-Item "$src\scripts\*.ts" "dashboard\scripts\" -Force
```

Depois valide:

```powershell
cd dashboard
npx --no-install tsc --noEmit
npx --no-install tsx scripts/validar-ordenacao.ts
npx --no-install tsx scripts/validar-ranking-exato.ts
npx --no-install tsx scripts/validar-backtest-ranking.ts
```

## Como voltar para o estado de sexta

Os arquivos de sexta foram restaurados a partir dos blobs:

| Arquivo | Blob |
|---|---|
| `gerador-diversificado.ts` | `22f855e074e445eb9bb6a4cfdd6517f08d041a99` (sexta + fix `buildJogo(score)`) |
| `JogosDiversosSection.tsx` | `d70a94835edc` |
| `app/api/jogos-diversos/route.ts` | `bea160d6f841` |
| `app/api/jogos-diversos/export/route.ts` | `e2cfff5eef24` |

```powershell
cmd /c "git cat-file -p 22f855e074e445eb9bb6a4cfdd6517f08d041a99 > dashboard\src\lib\gerador-diversificado.ts"
cmd /c "git cat-file -p d70a94835edc > dashboard\src\components\JogosDiversosSection.tsx"
cmd /c "git cat-file -p bea160d6f841 > dashboard\app\api\jogos-diversos\route.ts"
cmd /c "git cat-file -p e2cfff5eef24 > dashboard\app\api\jogos-diversos\export\route.ts"
```

A versão de sexta de `colunas-posicionais.ts` é a atual **sem** `parseObjetivoRanking` e `parseOtimizacao` (mantendo `parseOrdenacao` e `parseScoreSets`). Os blobs de API de sexta não definiam `ordenacao`/`scoreSets` no `POST`; as duas linhas de `parseOrdenacao`/`parseScoreSets` precisam ser adicionadas para compilar.

## Observações

- Reaplique **todos** os arquivos juntos: gerador, UI, API e parsers são acoplados.
- O snapshot foi copiado de `%TEMP%\opencode\lotoscope-post-friday` antes da reversão.
- Node do grafo da reversão: `node_49c442d2e412`.
- Último commit do repo: `67282ce` (2026-09-25); todo o trabalho pós-sexta estava não commitado.
