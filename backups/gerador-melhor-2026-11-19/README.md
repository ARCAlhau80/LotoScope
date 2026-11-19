# Baseline Lotofácil — melhor gerador/fechamento até 2026-11-19

Este snapshot congela o estado do fechamento combinatório da Lotofácil que consideramos
o **mais preciso até agora** (estado da arte do projeto).

- **Commit base:** `78285a7` — `feat(fechamento): restaura lotto design por complementos e designs do dia 15`
- **Tag:** `baseline-lotofacil-melhor-2026-11-19`
- **Branch:** `baseline/lotofacil-melhor-2026-11-19`

## O que este estado tem

- `construirLottoDesignComplemento` (k > m) — caminho por complementos e bitset.
- Checagem de **design conhecido antes** do limite `v > 30`.
- Design `L(25,16,15,11)` e demais `25,17..20,15,11` no `lotto-lotofacil.json`.
- Registro `lotto-megasena.json` + import no `lotto.ts` (vazio por enquanto).
- Modo forçado: pool de candidatos maior, até **120 s** para o lotto design.
- Trava de viabilidade com opção de ignorar (“Forçar geração acima do limite prático”).
- Cobertura completa por enumeração para `t = k`.
- Covers conhecidos da Mega-Sena e Lotofácil preservados.

## Resultados validados neste estado

| Caso | Resultado |
|---|---|
| Lotofácil `25,16,15,11` | **28 apostas**, piso **11**, fonte “complementos + guloso por bitset”, verificado |
| Lotofácil `24,16,15,11` | **15 apostas**, piso **11**, via complementos, verificado |
| Mega-Sena `60,6,4` | cover conhecido **37.995 apostas**, cobertura **100%** |

Custo do `25,16,15,11`: 28 × R$ 56,00 = **R$ 1.568,00**.

## Arquivos incluídos

```
dashboard/src/lib/fechamento-combinatorio.ts
dashboard/app/api/fechamento/route.ts
dashboard/src/lib/fechamento/config.ts
dashboard/src/lib/fechamento/lotto.ts
dashboard/src/lib/fechamento/covers.ts
dashboard/src/data/lotto-lotofacil.json
dashboard/src/data/lotto-megasena.json
dashboard/src/components/JogosDiversosSection.tsx
```

Os arquivos grandes de covers (`covers-lotofacil.json`, `covers-megasena.json`) **não**
foram duplicados aqui; eles estão preservados no commit/tag e não mudaram neste ciclo.

## Como restaurar

Opção 1 — pelo git:

```powershell
git checkout baseline/lotofacil-melhor-2026-11-19
```

Opção 2 — copiando o snapshot:

```powershell
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\src\lib\fechamento-combinatorio.ts" "dashboard\src\lib\fechamento-combinatorio.ts" -Force
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\app\api\fechamento\route.ts" "dashboard\app\api\fechamento\route.ts" -Force
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\src\lib\fechamento\config.ts" "dashboard\src\lib\fechamento\config.ts" -Force
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\src\lib\fechamento\lotto.ts" "dashboard\src\lib\fechamento\lotto.ts" -Force
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\src\lib\fechamento\covers.ts" "dashboard\src\lib\fechamento\covers.ts" -Force
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\src\data\lotto-lotofacil.json" "dashboard\src\data\lotto-lotofacil.json" -Force
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\src\data\lotto-megasena.json" "dashboard\src\data\lotto-megasena.json" -Force
Copy-Item "backups\gerador-melhor-2026-11-19\dashboard\src\components\JogosDiversosSection.tsx" "dashboard\src\components\JogosDiversosSection.tsx" -Force
```

Depois:

```powershell
cd dashboard
npx tsc --noEmit
```

## Não regredir

Ao mexer no fechamento, preserve estes pontos:

1. `construirLottoDesignComplemento` e o branch da rota para `kL > mL`.
2. As chaves `25,16..20,15,11` do `lotto-lotofacil.json`.
3. A checagem `buscarLottoDesign(...)` **antes** do limite `vL > 30`.
4. O modo forçado e o teto de 120 s do lotto design.
5. A verificação por marcação de t-subconjuntos (não voltar para O(apostas × C(v,t))).
