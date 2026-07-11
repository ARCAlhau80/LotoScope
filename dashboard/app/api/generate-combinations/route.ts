import { NextResponse } from 'next/server';
import { getLotteryConfig } from '@/lib/lottery-config';

export const dynamic = 'force-dynamic';

const MAX_GENERATE = 50000;

function nCr(n: number, k: number): number {
  if (k < 0 || k > n) return 0;
  if (k > n - k) k = n - k;
  let result = 1;
  for (let i = 1; i <= k; i++) {
    result = (result * (n - k + i)) / i;
  }
  return result;
}

function generateAllCombs(arr: number[], k: number): number[][] {
  const result: number[][] = [];
  const combo = new Array(k);
  function dfs(start: number, depth: number) {
    if (depth === k) {
      result.push([...combo]);
      return;
    }
    for (let i = start; i <= arr.length - (k - depth); i++) {
      combo[depth] = arr[i];
      dfs(i + 1, depth + 1);
    }
  }
  dfs(0, 0);
  return result;
}

function randomSample(arr: number[], k: number, count: number): number[][] {
  const result: number[][] = [];
  const seen = new Set<string>();
  for (let iter = 0; iter < count * 3 && result.length < count; iter++) {
    const shuffled = [...arr];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    const pick = shuffled.slice(0, k).sort((a, b) => a - b);
    const key = pick.join(',');
    if (!seen.has(key)) {
      seen.add(key);
      result.push(pick);
    }
  }
  return result;
}

function generateSuperSeteCombinations(
  digitosPorColuna: Record<string, number[]>,
  quantity: number
): number[][] {
  const cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7'];
  const pools: number[][] = cols.map(c => digitosPorColuna[c] || [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);

  let totalPossible = 1;
  for (const p of pools) totalPossible *= p.length;

  if (totalPossible <= MAX_GENERATE && (quantity === 0 || quantity >= totalPossible)) {
    const result: number[][] = [];
    function generate(colIdx: number, current: number[]) {
      if (colIdx === 7) {
        result.push([...current]);
        return;
      }
      for (const d of pools[colIdx]) {
        current.push(d);
        generate(colIdx + 1, current);
        current.pop();
      }
    }
    generate(0, []);
    return result;
  }

  const result: number[][] = [];
  const seen = new Set<string>();
  const limit = quantity || Math.min(totalPossible, 10000);
  for (let iter = 0; iter < limit * 3 && result.length < limit; iter++) {
    const combo = pools.map(p => p[Math.floor(Math.random() * p.length)]);
    const key = combo.join(',');
    if (!seen.has(key)) {
      seen.add(key);
      result.push(combo);
    }
  }
  return result;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const {
      mandatory_numbers = [],
      excluded_numbers = [],
      selected_numbers = [],
      fixed_numbers = [],
      game_size,
      quantity,
      loteria = 'lotofacil',
      digitos_por_coluna,
    } = body;

    const cfg = getLotteryConfig(loteria);

    if (cfg.is_positional && cfg.id === 'supersete') {
      const pools = digitos_por_coluna || {};
      const combinations = generateSuperSeteCombinations(pools, quantity || 0);
      let totalPossible = 1;
      for (let i = 1; i <= 7; i++) {
        const pool = pools[`N${i}`] || [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
        totalPossible *= pool.length;
      }
      return NextResponse.json({
        success: true,
        combinations,
        count: combinations.length,
        total_possible: totalPossible,
        requested: quantity || 'all',
        is_positional: true,
      });
    }

    const numerosPorJogo = game_size || cfg.numeros_por_jogo;

    const mandatory = mandatory_numbers.length > 0 ? mandatory_numbers : selected_numbers.length > 0 ? selected_numbers : fixed_numbers;
    const excluded = excluded_numbers;

    const mandatorySet = new Set(mandatory);
    const excludedSet = new Set(excluded);

    const overlap = mandatory.filter((n: number) => excludedSet.has(n));
    if (overlap.length > 0) {
      return NextResponse.json({ success: false, error: `Números não podem ser fixos e excluídos: ${overlap}` }, { status: 400 });
    }

    if (mandatory.length >= numerosPorJogo) {
      return NextResponse.json({ success: false, error: 'Números fixos não podem ser >= tamanho do jogo' }, { status: 400 });
    }

    const available: number[] = [];
    for (let i = cfg.numero_minimo; i <= cfg.numero_maximo; i++) {
      if (!mandatorySet.has(i) && !excludedSet.has(i)) available.push(i);
    }

    const needed = numerosPorJogo - mandatory.length;
    if (available.length < needed) {
      return NextResponse.json({ success: false, error: 'Muitos números excluídos — insuficientes para completar o jogo' }, { status: 400 });
    }

    const totalPossible = nCr(available.length, needed);
    const wantAll = quantity === 0 || quantity === undefined || quantity === null;
    const limit = wantAll ? 0 : Math.min(quantity, 10000);

    let rawCombs: number[][];

    if (totalPossible <= MAX_GENERATE && (wantAll || limit >= totalPossible)) {
      rawCombs = generateAllCombs(available, needed);
    } else {
      const sampleSize = wantAll ? Math.min(MAX_GENERATE, totalPossible) : limit;
      rawCombs = randomSample(available, needed, sampleSize);
    }

    const combinationsResult = rawCombs.map(combo =>
      [...mandatory, ...combo].sort((a: number, b: number) => a - b)
    );

    return NextResponse.json({
      success: true,
      combinations: combinationsResult,
      count: combinationsResult.length,
      total_possible: totalPossible,
      requested: wantAll ? 'all' : quantity,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
