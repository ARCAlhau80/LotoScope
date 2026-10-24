export interface GeradorDiversificadoOptions {
  resultados: number[][];
  cicloDados?: Record<number, number>;
  nJogos?: number;
  seed?: number;
  fixos?: number[];
  excluidos?: number[];
  totalNumeros?: number;
  numerosPorJogo?: number;
  numeroMinimo?: number;
  primos?: number[];
  colunasPosicionais?: ColunasPosicionaisConstraint;
  dominiosPosicionais?: Array<number[] | null>;
  filtroComparativo?: FiltroComparativo;
  filtroCategorias?: FiltroCategoria[];
  ordenacao?: OrdenacaoJogos;
  scoreSets?: Record<string, number[]>;
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
  estrategias?: string[];
  trevosTotal?: number;
  trevosMin?: number;
  trevosPorJogo?: number;
}

export interface ColunasPosicionaisConstraint {
  sets: number[][];
  mins: number[];
  maxs: number[];
}

export interface FiltroComparativo {
  maiores?: { min: number; max: number };
  iguais?: { min: number; max: number };
  menores?: { min: number; max: number };
}

export interface FiltroCategoria {
  numeros: number[];
  min: number;
  max: number;
}

export type OrdenacaoJogos = 'aleatorio' | 'melhores' | 'balanceado' | 'piores';

export interface JogoGerado {
  numeros: number[];
  trevos?: number[];
  estrategia: string;
  soma: number;
  pares: number;
  impares: number;
  primos: number;
  score?: number;
}

interface LP {
  totalNumeros: number;
  numerosPorJogo: number;
  numeroMinimo: number;
  numeroMaximo: number;
  primosSet: Set<number>;
  trevosTotal?: number;
  trevosMin?: number;
  trevosPorJogo?: number;
}

function buildLP(opts: GeradorDiversificadoOptions): LP {
  const totalNumeros = opts.totalNumeros ?? 25;
  const numerosPorJogo = opts.numerosPorJogo ?? 15;
  const numeroMinimo = opts.numeroMinimo ?? 1;
  const primosList = opts.primos ?? [2, 3, 5, 7, 11, 13, 17, 19, 23];
  return {
    totalNumeros,
    numerosPorJogo,
    numeroMinimo,
    numeroMaximo: numeroMinimo + totalNumeros - 1,
    primosSet: new Set(primosList),
    trevosTotal: opts.trevosTotal,
    trevosMin: opts.trevosMin,
    trevosPorJogo: opts.trevosPorJogo,
  };
}

function rng(seed?: number): () => number {
  let s = seed ?? Date.now() % 2147483647;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function sample<T>(arr: T[], k: number, rand: () => number): T[] {
  const copy = [...arr];
  const result: T[] = [];
  for (let i = 0; i < k && copy.length > 0; i++) {
    const idx = Math.floor(rand() * copy.length);
    result.push(copy[idx]);
    copy.splice(idx, 1);
  }
  return result;
}

function shuffle<T>(arr: T[], rand: () => number): T[] {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function sorted(nums: number[]): number[] {
  return [...nums].sort((a, b) => a - b);
}

function combinacoes(n: number, k: number): number {
  if (k < 0 || k > n) return 0;
  if (k === 0 || k === n) return 1;
  let res = 1;
  for (let i = 1; i <= k; i++) {
    res = (res * (n - k + i)) / i;
  }
  return Math.round(res);
}

function* gerarCombinacoes(pool: number[], k: number): Generator<number[]> {
  const n = pool.length;
  const indices = Array.from({ length: k }, (_, i) => i);

  while (true) {
    yield indices.map(i => pool[i]);

    let i = k - 1;
    while (i >= 0 && indices[i] === i + n - k) {
      i--;
    }
    if (i < 0) return;

    indices[i]++;
    for (let j = i + 1; j < k; j++) {
      indices[j] = indices[j - 1] + 1;
    }
  }
}

export function calcularEstimativaCombinacoes(
  fixos?: number[],
  excluidos?: number[],
  totalNumeros = 25,
  numerosPorJogo = 15,
  numeroMinimo = 1,
  colunasPosicionais?: ColunasPosicionaisConstraint,
  filtroComparativo?: FiltroComparativo,
  baseComparativo: number[] = [],
  fixosPosicoes?: Record<number, number[]>,
  excluidosPosicoes?: Record<number, number[]>,
  filtroCategorias?: FiltroCategoria[],
  dominiosPosicionais?: Array<number[] | null>
): number {
  const excluidosCompletos = (excluidos ?? []).filter(n => !(excluidosPosicoes?.[n]?.length));
  const { fixosNorm, excluidosNorm, disponiveis } = normalizarConstraints(fixos, excluidosCompletos, totalNumeros, numeroMinimo);
  const totalDisp = totalNumeros - fixosNorm.length - excluidosNorm.length;
  const escolher = numerosPorJogo - fixosNorm.length;
  const base = combinacoes(totalDisp, escolher);

  const temCmp = filtroComparativo !== undefined && baseComparativo.length > 0;
  const temPos = fixosPosicoes !== undefined && fixosNorm.some(n => (fixosPosicoes[n] ?? []).length > 0);
  const temExclPos = excluidosPosicoes !== undefined
    && Object.keys(excluidosPosicoes).some(n => {
      const num = Number(n);
      return (excluidosPosicoes[num] ?? []).length > 0 && num >= numeroMinimo && num < numeroMinimo + totalNumeros && !fixosNorm.includes(num);
    });

  // normaliza as colunas exatamente como a geração faz (fixos/excluídos fora dos conjuntos,
  // mins/maxs limitados ao tamanho do conjunto) para a estimativa bater com o gerado
  const colunasNorm = normalizarColunas(colunasPosicionais, {
    totalNumeros,
    numerosPorJogo,
    numeroMinimo,
    numeroMaximo: numeroMinimo + totalNumeros - 1,
    primosSet: new Set<number>(),
  }, fixosNorm, excluidosNorm);
  const temColunas = colunasNorm !== undefined && colunasNorm.sets.length > 0;

  const categoriasNorm = normalizarCategorias(filtroCategorias, {
    numerosPorJogo,
    numeroMinimo,
    numeroMaximo: numeroMinimo + totalNumeros - 1,
  });
  const temCats = categoriasNorm !== undefined;

  const dominiosNorm = normalizarDominios(
    dominiosPosicionais,
    { numeroMinimo, numeroMaximo: numeroMinimo + totalNumeros - 1, numerosPorJogo },
    excluidosNorm
  );
  const temDominios = dominiosNorm !== undefined;

  if (!temColunas && !temCmp && !temPos && !temExclPos && !temCats && !temDominios) return base;

  if (temDominios) {
    const est = estimativaMonteCarlo(
      fixosNorm, excluidosNorm, totalNumeros, numerosPorJogo, numeroMinimo,
      colunasNorm ?? { sets: [], mins: [], maxs: [] },
      filtroComparativo ?? {},
      baseComparativo,
      totalDisp,
      escolher,
      20260921,
      fixosPosicoes,
      excluidosPosicoes,
      categoriasNorm,
      dominiosNorm
    );
    return Math.min(Math.max(0, est), base);
  }

  if (temCats) {
    const est = estimativaMonteCarlo(
      fixosNorm, excluidosNorm, totalNumeros, numerosPorJogo, numeroMinimo,
      colunasNorm ?? { sets: [], mins: [], maxs: [] },
      filtroComparativo ?? {},
      baseComparativo,
      totalDisp,
      escolher,
      20260921,
      fixosPosicoes,
      excluidosPosicoes,
      categoriasNorm
    );
    return Math.min(Math.max(0, est), base);
  }

  if (temPos && !temColunas && !temCmp && !temExclPos) {
    return contarCombinacoesComPosicoes(fixosNorm, fixosPosicoes, disponiveis, totalNumeros, numerosPorJogo, numeroMinimo);
  }

  if (temColunas && !temCmp && !temPos && !temExclPos) {
    return contarCombinacoesComColunas(fixosNorm, excluidosNorm, disponiveis, totalNumeros, numerosPorJogo, numeroMinimo, colunasNorm!, base);
  }

  if (!temColunas && temCmp && !temPos && !temExclPos) {
    const est = contarCombinacoesColunasComparativo(fixosNorm, excluidosNorm, totalNumeros, numerosPorJogo, numeroMinimo, undefined, filtroComparativo, baseComparativo);
    return Math.min(est ?? base, base);
  }

  // combinação de filtros (colunas e/ou comparativo e/ou posições e/ou exclusões por posição):
  // DP combinada exata com rastreamento de posição
  const est = contarCombinacoesColunasComparativo(
    fixosNorm, excluidosNorm, totalNumeros, numerosPorJogo, numeroMinimo,
    temColunas ? colunasNorm : undefined,
    temCmp ? filtroComparativo : undefined,
    baseComparativo,
    fixosPosicoes,
    excluidosPosicoes
  );
  if (est !== null) return Math.min(est, base);

  // orçamento da DP estourou: aproximação conservadora (menor dos limites individuais)
  const estCol = temColunas
    ? contarCombinacoesComColunas(fixosNorm, excluidosNorm, disponiveis, totalNumeros, numerosPorJogo, numeroMinimo, colunasNorm!, base)
    : base;
  const estPos = temPos
    ? contarCombinacoesComPosicoes(fixosNorm, fixosPosicoes, disponiveis, totalNumeros, numerosPorJogo, numeroMinimo)
    : base;
  const estCmp = temCmp
    ? (contarCombinacoesColunasComparativo(fixosNorm, excluidosNorm, totalNumeros, numerosPorJogo, numeroMinimo, undefined, filtroComparativo, baseComparativo) ?? base)
    : base;

  if (temColunas && temCmp) {
    const estMC = estimativaMonteCarlo(fixosNorm, excluidosNorm, totalNumeros, numerosPorJogo, numeroMinimo, colunasNorm!, filtroComparativo!, baseComparativo, totalDisp, escolher, 20260921, fixosPosicoes, excluidosPosicoes);
    return Math.min(estMC, estCol, estCmp, estPos, base);
  }
  return Math.min(estCol, estCmp, estPos, base);
}

function estimativaMonteCarlo(
  fixosNorm: number[],
  excluidosNorm: number[],
  totalNumeros: number,
  numerosPorJogo: number,
  numeroMinimo: number,
  col: ColunasPosicionaisConstraint,
  filtro: FiltroComparativo,
  base: number[],
  totalDisp: number,
  escolher: number,
  seed = 20260921,
  fixosPosicoes?: Record<number, number[]>,
  excluidosPosicoes?: Record<number, number[]>,
  categorias?: FiltroCategoria[],
  dominios?: Array<number[] | null>
): number {
  const numeroMaximo = numeroMinimo + totalNumeros - 1;
  const pool = Array.from({ length: totalNumeros }, (_, i) => i + numeroMinimo).filter(n => !excluidosNorm.includes(n) && !fixosNorm.includes(n));
  const nCols = Math.min(col.sets.length, 5);
  const setC: number[][] = [];
  const minC: number[] = [];
  const maxC: number[] = [];
  for (let c = 0; c < nCols; c++) {
    setC.push([...new Set((col.sets[c] || []).filter(n => n >= numeroMinimo && n <= numeroMaximo))]);
    minC.push(Math.max(0, col.mins[c] ?? 0));
    maxC.push(col.maxs[c] ?? Number.POSITIVE_INFINITY);
  }

  const rand = rng(seed);
  const N = 30000;
  let hits = 0;
  for (let i = 0; i < N; i++) {
    const chosen = sample(pool, escolher, rand);
    const jogo = sorted([...fixosNorm, ...chosen]);
    if (jogo.length !== numerosPorJogo) continue;
    let ok = true;
    for (let c = 0; c < nCols; c++) {
      const cnt = setC[c].reduce((k, n) => k + (jogo.includes(n) ? 1 : 0), 0);
      if (cnt < minC[c] || cnt > maxC[c]) { ok = false; break; }
    }
    if (ok && base.length > 0) {
      const nCmp = posicoesComparaveis(numerosPorJogo, base.length);
      let m = 0, men = 0, ig = 0;
      for (let i2 = 0; i2 < nCmp; i2++) {
        if (jogo[i2] > base[i2]) m++;
        else if (jogo[i2] < base[i2]) men++;
        else ig++;
      }
      const r = (v: { min: number; max: number } | undefined, cnt: number) => !v || (cnt >= v.min && cnt <= v.max);
      ok = r(filtro.maiores, m) && r(filtro.iguais, ig) && r(filtro.menores, men);
    }
    if (ok && !satisfazPosicoes(jogo, fixosPosicoes)) ok = false;
    if (ok && !satisfazExclusaoPosicoes(jogo, excluidosPosicoes)) ok = false;
    if (ok && categorias && !satisfazCategorias(jogo, categorias)) ok = false;
    if (ok && dominios && !satisfazDominios(jogo, dominios)) ok = false;
    if (ok) hits++;
  }
  return Math.round(hits / N * combinacoes(totalDisp, escolher));
}

function contarCombinacoesColunasComparativo(
  fixosNorm: number[],
  excluidosNorm: number[],
  totalNumeros: number,
  numerosPorJogo: number,
  numeroMinimo: number,
  col: ColunasPosicionaisConstraint | undefined,
  filtro: FiltroComparativo | undefined,
  base: number[],
  fixosPosicoes?: Record<number, number[]>,
  excluidosPosicoes?: Record<number, number[]>
): number | null {
  const numeroMaximo = numeroMinimo + totalNumeros - 1;
  if (filtro && base.length === 0) return null;
  const nCmp = filtro ? posicoesComparaveis(numerosPorJogo, base.length) : 0;
  const nCols = col ? Math.min(col.sets.length, 5) : 0;

  const setC: number[][] = [];
  const minC: number[] = [];
  const maxC: number[] = [];
  for (let c = 0; c < nCols; c++) {
    const s = [...new Set((col!.sets[c] || []).filter(n => n >= numeroMinimo && n <= numeroMaximo))];
    setC.push(s);
    minC.push(Math.max(0, col!.mins[c] ?? 0));
    maxC.push(col!.maxs[c] ?? Number.POSITIVE_INFINITY);
  }

  const capC: number[] = [];
  const needC: number[] = [];
  for (let c = 0; c < nCols; c++) {
    if (isFinite(maxC[c])) {
      if (minC[c] > maxC[c]) return 0;
      capC.push(Math.min(maxC[c], numerosPorJogo));
    } else {
      capC.push(Math.min(minC[c], numerosPorJogo));
    }
    needC.push(Math.min(minC[c], capC[c]));
  }
  if (minC.some((m, c) => m > numerosPorJogo)) return 0;

  const cmKeys = ['maiores', 'iguais', 'menores'] as const;
  const cmpMax: number[] = [];
  const capM: number[] = [];
  const needM: number[] = [];
  for (let i = 0; i < 3; i++) {
    const r = filtro ? filtro[cmKeys[i]] : undefined;
    const mn = r ? Math.max(0, r.min) : 0;
    const mx = r ? (Number.isFinite(r.max) ? r.max : Number.POSITIVE_INFINITY) : Number.POSITIVE_INFINITY;
    cmpMax.push(mx);
    const cap = Number.isFinite(mx) ? Math.min(mx, nCmp) : Math.min(mn, nCmp);
    capM.push(Math.max(0, cap));
    needM.push(Math.min(mn, capM[capM.length - 1]));
  }
  if (cmpMax.some((mx, i) => {
    const mn = (filtro ? filtro[cmKeys[i]] : undefined)?.min ?? 0;
    return mn > nCmp || (Number.isFinite(mx) && mn > mx);
  })) return 0;

  const fixoSet = new Set(fixosNorm);
  const excluidoSet = new Set(excluidosNorm);

  const radixC = capC.map(x => x + 1);
  const radixM = capM.map(x => x + 1);
  const encode = (k: number, m: number[], cols: number[]): number => {
    let key = k;
    for (let i = 0; i < 3; i++) key = key * radixM[i] + m[i];
    for (let c = 0; c < nCols; c++) key = key * radixC[c] + cols[c];
    return key;
  };
  const decode = (key: number): { k: number; m: number[]; cols: number[] } => {
    const cols: number[] = [];
    for (let c = nCols - 1; c >= 0; c--) { cols[c] = key % radixC[c]; key = Math.floor(key / radixC[c]); }
    const m: number[] = [];
    for (let i = 2; i >= 0; i--) { m[i] = key % radixM[i]; key = Math.floor(key / radixM[i]); }
    return { k: key, m, cols };
  };

  const BUDGET = 1_000_000;
  let dp = new Map<number, number>();
  dp.set(encode(0, [0, 0, 0], capC.map(() => 0)), 1);

  const add = (map: Map<number, number>, key: number, ways: number) => {
    map.set(key, (map.get(key) ?? 0) + ways);
  };

  for (let x = numeroMinimo; x <= numeroMaximo; x++) {
    if (excluidoSet.has(x)) continue;
    const next = new Map<number, number>();
    const isFixo = fixoSet.has(x);
    for (const [key, ways] of dp) {
      const { k, m, cols } = decode(key);
      if (k === numerosPorJogo) {
        if (!isFixo) add(next, key, ways);
        continue;
      }
      if (!isFixo) add(next, key, ways);

      if (isFixo) {
        const pj = fixosPosicoes?.[x];
        if (pj && pj.length > 0 && !pj.includes(k + 1)) continue;
      }

      const qj = excluidosPosicoes?.[x];
      if (qj && qj.length > 0 && qj.includes(k + 1)) continue;

      let ok = true;
      const nm = [m[0], m[1], m[2]];
      if (k < nCmp) {
        const b = base[k];
        if (x > b) {
          if (Number.isFinite(cmpMax[0])) { nm[0] = m[0] + 1; if (nm[0] > cmpMax[0]) ok = false; }
          else nm[0] = Math.min(m[0] + 1, capM[0]);
        } else if (x < b) {
          if (Number.isFinite(cmpMax[2])) { nm[2] = m[2] + 1; if (nm[2] > cmpMax[2]) ok = false; }
          else nm[2] = Math.min(m[2] + 1, capM[2]);
        } else {
          if (Number.isFinite(cmpMax[1])) { nm[1] = m[1] + 1; if (nm[1] > cmpMax[1]) ok = false; }
          else nm[1] = Math.min(m[1] + 1, capM[1]);
        }
      }
      if (!ok) continue;

      const ncols = [...cols];
      for (let c = 0; c < nCols; c++) {
        if (!setC[c].includes(x)) continue;
        if (Number.isFinite(maxC[c])) {
          const raw = cols[c] + 1;
          if (raw > maxC[c]) { ok = false; break; }
          ncols[c] = raw;
        } else {
          ncols[c] = Math.min(cols[c] + 1, capC[c]);
        }
      }
      if (!ok) continue;

      add(next, encode(k + 1, nm, ncols), ways);
    }
    dp = next;
    if (dp.size > BUDGET) return null;
  }

  let total = 0;
  for (const [key, ways] of dp) {
    const { k, m, cols } = decode(key);
    if (k !== numerosPorJogo) continue;
    let ok = true;
    if (m[0] < needM[0] || m[1] < needM[1] || m[2] < needM[2]) ok = false;
    for (let c = 0; c < nCols; c++) if (cols[c] < needC[c]) { ok = false; break; }
    if (ok) total += ways;
  }
  return total;
}

function contarCombinacoesComColunas(
  fixosNorm: number[],
  excluidosNorm: number[],
  disponiveis: number[],
  totalNumeros: number,
  numerosPorJogo: number,
  numeroMinimo: number,
  col: ColunasPosicionaisConstraint,
  base: number
): number {
  const numeroMaximo = numeroMinimo + totalNumeros - 1;
  const numCols = Math.min(col.sets.length, 5);

  const setC: number[][] = [];
  const minC: number[] = [];
  const maxC: number[] = [];
  for (let c = 0; c < numCols; c++) {
    const s = [...new Set((col.sets[c] || []).filter(n => n >= numeroMinimo && n <= numeroMaximo))];
    setC.push(s);
    minC.push(Math.max(0, col.mins[c] ?? 0));
    maxC.push(col.maxs[c] ?? Number.POSITIVE_INFINITY);
  }

  const baseCounts: number[] = [];
  for (let c = 0; c < numCols; c++) {
    const cnt = fixosNorm.reduce((k, n) => k + (setC[c].includes(n) ? 1 : 0), 0);
    if (cnt > maxC[c]) return 0;
    baseCounts.push(cnt);
  }

  const cap: number[] = [];
  const need: number[] = [];
  for (let c = 0; c < numCols; c++) {
    if (isFinite(maxC[c])) {
      if (minC[c] > maxC[c]) return 0;
      cap.push(Math.min(maxC[c], numerosPorJogo));
    } else {
      cap.push(Math.min(minC[c], numerosPorJogo));
    }
    need.push(Math.min(minC[c], cap[c]));
  }
  if (minC.some((m, c) => m > numerosPorJogo)) return 0;

  const pool = disponiveis.filter(n => !fixosNorm.includes(n));
  const maskCount: Record<number, number> = {};
  for (const n of pool) {
    let mask = 0;
    for (let c = 0; c < numCols; c++) if (setC[c].includes(n)) mask |= 1 << c;
    maskCount[mask] = (maskCount[mask] ?? 0) + 1;
  }

  const radix = cap.map(x => x + 1);
  const encode = (chosen: number, counts: number[]): number => {
    let key = chosen;
    for (let c = 0; c < numCols; c++) key = key * radix[c] + counts[c];
    return key;
  };
  const decode = (key: number): { chosen: number; counts: number[] } => {
    const counts: number[] = [];
    for (let c = numCols - 1; c >= 0; c--) {
      counts[c] = key % radix[c];
      key = Math.floor(key / radix[c]);
    }
    return { chosen: key, counts };
  };

  let dp = new Map<number, number>();
  dp.set(encode(fixosNorm.length, baseCounts.map((b, c) => Math.min(b, cap[c]))), 1);

  for (const [maskStr, m] of Object.entries(maskCount)) {
    const mask = Number(maskStr);
    const next = new Map<number, number>();
    for (const [key, ways] of dp) {
      const { chosen, counts } = decode(key);
      const maxTake = Math.min(m, numerosPorJogo - chosen);
      for (let t = 0; t <= maxTake; t++) {
        let ok = true;
        const nc = [...counts];
        for (let c = 0; c < numCols; c++) {
          if (!(mask & (1 << c))) continue;
          const raw = counts[c] + t;
          if (isFinite(maxC[c])) {
            if (raw > maxC[c]) { ok = false; break; }
            nc[c] = raw;
          } else {
            nc[c] = Math.min(raw, cap[c]);
          }
        }
        if (!ok) continue;
        const nkey = encode(chosen + t, nc);
        next.set(nkey, (next.get(nkey) ?? 0) + ways * combinacoes(m, t));
      }
    }
    dp = next;
  }

  let total = 0;
  for (const [key, ways] of dp) {
    const { chosen, counts } = decode(key);
    if (chosen !== numerosPorJogo) continue;
    let ok = true;
    for (let c = 0; c < numCols; c++) {
      if (counts[c] < need[c]) { ok = false; break; }
    }
    if (ok) total += ways;
  }

  return Math.min(total, base);
}

function contarCombinacoesComPosicoes(
  fixosNorm: number[],
  fixosPosicoes: Record<number, number[]> | undefined,
  disponiveis: number[],
  totalNumeros: number,
  numerosPorJogo: number,
  numeroMinimo: number
): number {
  const numeroMaximo = numeroMinimo + totalNumeros - 1;
  const fixosOrdenados = [...fixosNorm].sort((a, b) => a - b);
  const F = fixosOrdenados.length;

  const fixoSet = new Set(fixosNorm);
  const excluidoSet = new Set(Array.from({ length: totalNumeros }, (_, i) => i + numeroMinimo).filter(n => !disponiveis.includes(n)));
  const available = (n: number) => !fixoSet.has(n) && !excluidoSet.has(n);

  const posMap: Record<number, number[]> = {};
  for (const n of fixosOrdenados) {
    const p = fixosPosicoes?.[n];
    if (p && p.length > 0) posMap[n] = p;
  }
  if (Object.keys(posMap).length === 0) {
    return combinacoes(disponiveis.length - fixoSet.size, numerosPorJogo - F);
  }

  const bounds = [numeroMinimo - 1, ...fixosOrdenados, numeroMaximo + 1];
  const b: number[] = [];
  for (let j = 0; j < bounds.length - 1; j++) {
    let cnt = 0;
    for (let n = bounds[j] + 1; n <= bounds[j + 1] - 1; n++) if (available(n)) cnt++;
    b.push(cnt);
  }

  let dp = new Map<number, number>();
  for (let a = 0; a <= b[0]; a++) {
    const pos = a + 1;
    const pj = posMap[fixosOrdenados[0]];
    if (!pj || pj.includes(pos)) dp.set(a, combinacoes(b[0], a));
  }

  for (let j = 1; j < F; j++) {
    const next = new Map<number, number>();
    const pj = posMap[fixosOrdenados[j]];
    for (const [c, ways] of dp) {
      for (let a = 0; a <= b[j]; a++) {
        const c2 = c + a;
        const pos = c2 + (j + 1);
        if (!pj || pj.includes(pos)) {
          next.set(c2, (next.get(c2) ?? 0) + ways * combinacoes(b[j], a));
        }
      }
    }
    dp = next;
    if (dp.size === 0) return 0;
  }

  const alvo = numerosPorJogo - F;
  let total = 0;
  for (const [c, ways] of dp) {
    const a = alvo - c;
    if (a >= 0 && a <= b[F]) total += ways * combinacoes(b[F], a);
  }
  return total;
}

function aplicarConstraints(jogo: number[], rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, excluidosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const jogoSet = new Set(jogo);
  for (const e of excluidosNorm) jogoSet.delete(e);
  for (const f of fixosNorm) jogoSet.add(f);
  const faltam = lp.numerosPorJogo - jogoSet.size;
  if (faltam > 0) {
    const pool = disponiveis.filter(n => !jogoSet.has(n));
    const extras = sample(pool, Math.min(faltam, pool.length), rand);
    for (const n of extras) jogoSet.add(n);
  }
  return sorted([...jogoSet]);
}

function normalizarConstraints(fixos?: number[], excluidos?: number[], totalNumeros = 25, numeroMinimo = 1): { fixosNorm: number[]; excluidosNorm: number[]; disponiveis: number[] } {
  const numeroMaximo = numeroMinimo + totalNumeros - 1;
  const fixosNorm = [...new Set((fixos ?? []).filter(n => n >= numeroMinimo && n <= numeroMaximo))];
  const excluidosNorm = [...new Set((excluidos ?? []).filter(n => n >= numeroMinimo && n <= numeroMaximo))];
  const excluidosEfetivos = excluidosNorm.filter(n => !fixosNorm.includes(n));
  const disponiveis = Array.from({ length: totalNumeros }, (_, i) => i + numeroMinimo).filter(n => !excluidosEfetivos.includes(n));
  return { fixosNorm, excluidosNorm: excluidosEfetivos, disponiveis };
}

function normalizarColunas(
  col: ColunasPosicionaisConstraint | undefined,
  lp: LP,
  fixosNorm: number[],
  excluidosNorm: number[]
): ColunasPosicionaisConstraint | undefined {
  if (!col) return undefined;
  const numCols = Math.min(col.sets.length, 5);
  const sets: number[][] = [];
  const mins: number[] = [];
  const maxs: number[] = [];
  for (let c = 0; c < numCols; c++) {
    const s = [...new Set((col.sets[c] || []).filter(n =>
      n >= lp.numeroMinimo && n <= lp.numeroMaximo && !fixosNorm.includes(n) && !excluidosNorm.includes(n)
    ))];
    sets.push(s);
    const m = Math.max(0, Math.min(col.mins[c] ?? 0, s.length));
    const x = Math.min(col.maxs[c] ?? s.length, s.length);
    mins.push(m);
    maxs.push(Math.max(m, x));
  }
  return { sets, mins, maxs };
}

function satisfazColunas(jogo: number[], col: ColunasPosicionaisConstraint): boolean {
  for (let c = 0; c < col.sets.length; c++) {
    const s = col.sets[c] || [];
    const cnt = s.reduce((acc, n) => acc + (jogo.includes(n) ? 1 : 0), 0);
    if (cnt < (col.mins[c] ?? 0) || cnt > (col.maxs[c] ?? s.length)) return false;
  }
  return true;
}

function normalizarDominios(
  dominios: Array<number[] | null> | undefined,
  lp: Pick<LP, 'numeroMinimo' | 'numeroMaximo' | 'numerosPorJogo'>,
  excluidosNorm: number[]
): Array<number[] | null> | undefined {
  if (!dominios || dominios.length === 0) return undefined;
  const out: Array<number[] | null> = [];
  let temRestricao = false;
  for (let i = 0; i < lp.numerosPorJogo; i++) {
    const raw = dominios[i];
    if (!raw || raw.length === 0) {
      out.push(null);
      continue;
    }
    temRestricao = true;
    const s = [...new Set(raw.filter(n =>
      n >= lp.numeroMinimo && n <= lp.numeroMaximo && !excluidosNorm.includes(n)
    ))].sort((a, b) => a - b);
    out.push(s);
  }
  return temRestricao ? out : undefined;
}

function satisfazDominios(jogo: number[], dominios: Array<number[] | null>): boolean {
  const ord = sorted(jogo);
  for (let i = 0; i < ord.length; i++) {
    const d = dominios[i];
    if (d === null || d === undefined) continue;
    if (!d.includes(ord[i])) return false;
  }
  return true;
}

function satisfazPosicoes(jogo: number[], fixosPosicoes: Record<number, number[]> | undefined): boolean {
  if (!fixosPosicoes) return true;
  for (let i = 0; i < jogo.length; i++) {
    const p = fixosPosicoes[jogo[i]];
    if (p && p.length > 0 && !p.includes(i + 1)) return false;
  }
  return true;
}

function satisfazExclusaoPosicoes(jogo: number[], excluidosPosicoes: Record<number, number[]> | undefined): boolean {
  if (!excluidosPosicoes) return true;
  for (let i = 0; i < jogo.length; i++) {
    const q = excluidosPosicoes[jogo[i]];
    if (q && q.length > 0 && q.includes(i + 1)) return false;
  }
  return true;
}

function posicoesComparaveis(tamanhoJogo: number, tamanhoBase: number): number {
  return Math.min(tamanhoJogo, tamanhoBase);
}

function satisfazComparativo(jogo: number[], base: number[], filtro: FiltroComparativo | undefined): boolean {
  if (!filtro) return true;
  if (base.length === 0 || jogo.length === 0) return true;
  const n = posicoesComparaveis(jogo.length, base.length);
  let m = 0, men = 0, ig = 0;
  for (let i = 0; i < n; i++) {
    if (jogo[i] > base[i]) m++;
    else if (jogo[i] < base[i]) men++;
    else ig++;
  }
  const check = (r: { min: number; max: number } | undefined, cnt: number) => !r || (cnt >= r.min && cnt <= r.max);
  return check(filtro.maiores, m) && check(filtro.iguais, ig) && check(filtro.menores, men);
}

function normalizarCategorias(
  cats: FiltroCategoria[] | undefined,
  lp: Pick<LP, 'numeroMinimo' | 'numeroMaximo' | 'numerosPorJogo'>
): FiltroCategoria[] | undefined {
  if (!cats || cats.length === 0) return undefined;
  const out: FiltroCategoria[] = [];
  for (const c of cats) {
    const nums = [...new Set((c.numeros ?? []).filter(n => n >= lp.numeroMinimo && n <= lp.numeroMaximo))];
    if (nums.length === 0) continue;
    const limite = Math.min(nums.length, lp.numerosPorJogo);
    const min = Math.max(0, Math.min(c.min, limite));
    const max = Math.max(min, Math.min(c.max, limite));
    out.push({ numeros: nums, min, max });
  }
  return out.length > 0 ? out : undefined;
}

function satisfazCategorias(jogo: number[], cats: FiltroCategoria[] | undefined): boolean {
  if (!cats || cats.length === 0) return true;
  const set = new Set(jogo);
  for (const c of cats) {
    let cnt = 0;
    for (const n of c.numeros) if (set.has(n)) cnt++;
    if (cnt < c.min || cnt > c.max) return false;
  }
  return true;
}

export interface FiltrosAvaliaveis {
  totalNumeros?: number;
  numerosPorJogo?: number;
  numeroMinimo?: number;
  fixos?: number[];
  excluidos?: number[];
  colunasPosicionais?: ColunasPosicionaisConstraint;
  dominiosPosicionais?: Array<number[] | null>;
  filtroComparativo?: FiltroComparativo;
  baseComparativo?: number[];
  filtroCategorias?: FiltroCategoria[];
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
}

export interface AvaliacaoFiltro {
  id: string;
  passou: boolean;
}

// Avalia uma combinação contra os mesmos filtros usados na geração.
// Retorna uma entrada por filtro ativo; categorias usam ids "categoria:<índice>".
export function avaliarFiltrosCombinacao(jogo: number[], filtros: FiltrosAvaliaveis): AvaliacaoFiltro[] {
  const totalNumeros = filtros.totalNumeros ?? 25;
  const numeroMinimo = filtros.numeroMinimo ?? 1;
  const numerosPorJogo = filtros.numerosPorJogo ?? jogo.length;
  const numeroMaximo = numeroMinimo + totalNumeros - 1;
  const ordenado = sorted(jogo);
  const out: AvaliacaoFiltro[] = [];

  if (filtros.fixos && filtros.fixos.length > 0) {
    out.push({ id: 'fixos', passou: filtros.fixos.every(n => jogo.includes(n)) });
  }
  if (filtros.excluidos && filtros.excluidos.length > 0) {
    out.push({ id: 'excluidos', passou: !filtros.excluidos.some(n => jogo.includes(n)) });
  }
  if (filtros.colunasPosicionais) {
    const colunas = normalizarColunas(
      filtros.colunasPosicionais,
      { totalNumeros, numerosPorJogo, numeroMinimo, numeroMaximo, primosSet: new Set<number>() },
      filtros.fixos ?? [],
      filtros.excluidos ?? []
    );
    if (colunas) out.push({ id: 'colunas', passou: satisfazColunas(jogo, colunas) });
  }
  const dominios = normalizarDominios(
    filtros.dominiosPosicionais,
    { numeroMinimo, numeroMaximo, numerosPorJogo },
    filtros.excluidos ?? []
  );
  if (dominios) {
    out.push({ id: 'dominios', passou: satisfazDominios(ordenado, dominios) });
  }
  if (filtros.filtroComparativo) {
    out.push({
      id: 'comparativo',
      passou: satisfazComparativo(ordenado, filtros.baseComparativo ?? [], filtros.filtroComparativo),
    });
  }
  if (filtros.fixosPosicoes) {
    out.push({ id: 'fixos_posicoes', passou: satisfazPosicoes(ordenado, filtros.fixosPosicoes) });
  }
  if (filtros.excluidosPosicoes) {
    out.push({ id: 'excluidos_posicoes', passou: satisfazExclusaoPosicoes(ordenado, filtros.excluidosPosicoes) });
  }
  const cats = normalizarCategorias(filtros.filtroCategorias, { numeroMinimo, numeroMaximo, numerosPorJogo });
  if (cats) {
    cats.forEach((c, i) => out.push({ id: `categoria:${i}`, passou: satisfazCategorias(jogo, [c]) }));
  }
  return out;
}

interface ScoreContext {
  freqRecente: Record<number, number>;
  freqMedia: Record<number, number>;
  gap: Record<number, number>;
  quentes: Set<number>;
  aquecendo: Set<number>;
  frios: Set<number>;
  esfriando: Set<number>;
  grupos: number[][];
  janelaRecente: number;
  janelaMedia: number;
}

// Score por análises combinadas: frequência recente (janela curta e média),
// atraso (gap), quentes/aquecendo (bônus) e frios/esfriando (penalidade),
// além de um bônus de equilíbrio entre os grupos A/B/C quando informados.
function construirScoreContext(resultados: number[][], lp: LP, scoreSets?: Record<string, number[]>): ScoreContext {
  const janelaRecente = 10;
  const janelaMedia = 30;
  const total = resultados.length;
  const freqRecente: Record<number, number> = {};
  const freqMedia: Record<number, number> = {};
  const gap: Record<number, number> = {};
  for (let n = lp.numeroMinimo; n <= lp.numeroMaximo; n++) {
    freqRecente[n] = 0;
    freqMedia[n] = 0;
    gap[n] = total;
  }
  for (const r of resultados.slice(-janelaRecente)) for (const n of r) if (n in freqRecente) freqRecente[n]++;
  for (const r of resultados.slice(-janelaMedia)) for (const n of r) if (n in freqMedia) freqMedia[n]++;
  for (let i = total - 1; i >= 0; i--) {
    for (const n of resultados[i]) if (gap[n] === total) gap[n] = total - 1 - i;
  }
  const toSet = (k: string) => new Set((scoreSets?.[k] ?? []).filter(n => n >= lp.numeroMinimo && n <= lp.numeroMaximo));
  const grupos: number[][] = [];
  for (const k of ['grupoA', 'grupoB', 'grupoC']) if ((scoreSets?.[k] ?? []).length > 0) grupos.push(scoreSets![k]);
  return {
    freqRecente, freqMedia, gap,
    quentes: toSet('quentes'),
    aquecendo: toSet('aquecendo'),
    frios: toSet('frios'),
    esfriando: toSet('esfriando'),
    grupos,
    janelaRecente,
    janelaMedia,
  };
}

function scoreJogo(jogo: number[], ctx: ScoreContext): number {
  const jset = new Set(jogo);
  let s = 0;
  for (const n of jogo) {
    s += 2.0 * ((ctx.freqRecente[n] ?? 0) / ctx.janelaRecente);
    s += 1.0 * ((ctx.freqMedia[n] ?? 0) / ctx.janelaMedia);
    s += 0.5 * (Math.min(ctx.gap[n] ?? 0, 10) / 10);
    if (ctx.quentes.has(n)) s += 1.0;
    if (ctx.aquecendo.has(n)) s += 1.0;
    if (ctx.frios.has(n)) s -= 0.5;
    if (ctx.esfriando.has(n)) s -= 0.5;
  }
  if (ctx.grupos.length > 0) {
    let presentes = 0;
    for (const g of ctx.grupos) if (g.some(n => jset.has(n))) presentes++;
    s += presentes >= 3 ? 2.0 : presentes * 0.5;
  }
  return Math.round(s * 100) / 100;
}

function selecionarPorScore(
  jogos: number[][],
  nomes: string[],
  scores: number[],
  count: number,
  modo: OrdenacaoJogos
): { jogos: number[][]; nomes: string[]; scores: number[] } {
  const montar = (idx: number[]) => ({
    jogos: idx.map(i => jogos[i]),
    nomes: idx.map(i => nomes[i]),
    scores: idx.map(i => scores[i]),
  });
  const idx = jogos.map((_, i) => i);
  if (modo === 'melhores') {
    idx.sort((a, b) => scores[b] - scores[a]);
    return montar(idx.slice(0, count));
  }
  if (modo === 'piores') {
    idx.sort((a, b) => scores[a] - scores[b]);
    return montar(idx.slice(0, count));
  }
  // balanceado: estratifica em 3 faixas (alto / médio / baixo) e pega porções iguais
  const ordenado = [...idx].sort((a, b) => scores[b] - scores[a]);
  const faixas = 3;
  const porFaixa = Math.ceil(count / faixas);
  const tam = ordenado.length;
  const escolhidos: number[] = [];
  for (let f = 0; f < faixas && escolhidos.length < count; f++) {
    const ini = Math.floor(f * tam / faixas);
    const fim = Math.floor((f + 1) * tam / faixas);
    escolhidos.push(...ordenado.slice(ini, fim).slice(0, porFaixa));
  }
  return montar(escolhidos.slice(0, count));
}

function naoViolaLimites(n: number, jogo: Set<number>, col: ColunasPosicionaisConstraint): boolean {
  for (let c = 0; c < col.sets.length; c++) {
    const setC = col.sets[c] || [];
    if (!setC.includes(n)) continue;
    const maxC = col.maxs[c] ?? setC.length;
    const cnt = setC.reduce((s, x) => s + (jogo.has(x) ? 1 : 0), 0);
    if (cnt + 1 > maxC) return false;
  }
  return true;
}

function gerarComColunas(
  rand: () => number,
  lp: LP,
  fixosNorm: number[],
  excluidosNorm: number[],
  disponiveis: number[],
  col: ColunasPosicionaisConstraint
): number[] {
  const numCols = col.sets.length;
  for (let attempt = 0; attempt < 40; attempt++) {
    const jogo = new Set<number>(fixosNorm);
    const ordem = shuffle(Array.from({ length: numCols }, (_, i) => i), rand);
    let falhou = false;
    for (const c of ordem) {
      const setC = col.sets[c] || [];
      if (setC.length === 0) continue;
      const minC = col.mins[c] ?? 0;
      const atual = setC.reduce((s, n) => s + (jogo.has(n) ? 1 : 0), 0);
      let need = Math.max(0, minC - atual);
      if (need === 0) continue;
      for (let k = 0; k < need; k++) {
        const pool = setC.filter(n => !jogo.has(n) && naoViolaLimites(n, jogo, col));
        if (pool.length === 0) { falhou = true; break; }
        jogo.add(pool[Math.floor(rand() * pool.length)]);
      }
      if (falhou) break;
    }
    if (falhou) continue;

    if (jogo.size < lp.numerosPorJogo) {
      const faltam = lp.numerosPorJogo - jogo.size;
      let okFill = true;
      for (let f = 0; f < faltam; f++) {
        const pool = disponiveis.filter(n => !jogo.has(n) && naoViolaLimites(n, jogo, col));
        if (pool.length === 0) { okFill = false; break; }
        jogo.add(pool[Math.floor(rand() * pool.length)]);
      }
      if (!okFill) continue;
    }

    if (jogo.size === lp.numerosPorJogo && satisfazColunas([...jogo], col)) {
      return sorted([...jogo]);
    }
  }
  return gerarAleatorio(rand, lp, fixosNorm, excluidosNorm);
}

function completarJogo(selecionados: number[], fixos: number[], disponiveis: number[], rand: () => number, numerosPorJogo: number): number[] {
  const jogoSet = new Set([...fixos, ...selecionados]);
  const faltam = numerosPorJogo - jogoSet.size;
  if (faltam > 0) {
    const pool = disponiveis.filter(n => !jogoSet.has(n));
    if (pool.length < faltam) {
      return sorted([...jogoSet]);
    }
    const extras = sample(pool, faltam, rand);
    for (const n of extras) jogoSet.add(n);
  }
  return sorted([...jogoSet]);
}

function gerarAleatorio(rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const selecionados = sample(disponiveis.filter(n => !fixosNorm.includes(n)), Math.max(0, lp.numerosPorJogo - fixosNorm.length), rand);
  return completarJogo(selecionados, fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarAtraso(ultimosConcursos: number[][], rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const todosDisponiveis = new Set(disponiveis);
  const recentes = new Set<number>();
  for (const c of ultimosConcursos) {
    for (const n of c) if (todosDisponiveis.has(n)) recentes.add(n);
  }
  let atrasados = [...todosDisponiveis].filter(n => !recentes.has(n) && !fixosNorm.includes(n));
  if (atrasados.length < Math.max(0, lp.numerosPorJogo - fixosNorm.length)) {
    atrasados = [...todosDisponiveis].filter(n => !fixosNorm.includes(n));
  }
  const maxAtrasados = Math.min(
    Math.floor(rand() * Math.max(1, Math.ceil(lp.numerosPorJogo / 3))) + Math.max(1, Math.floor(lp.numerosPorJogo * 0.5)),
    Math.max(0, lp.numerosPorJogo - fixosNorm.length),
    atrasados.length
  );
  const selecionados = sample(atrasados, maxAtrasados, rand);
  return completarJogo(selecionados, fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarHot(ultimosConcursos: number[][], nHot: number, rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const todosDisponiveis = new Set(disponiveis);
  const hot = new Set<number>();
  const recentes = ultimosConcursos.slice(-3);
  for (const c of recentes) {
    for (const n of c) if (todosDisponiveis.has(n)) hot.add(n);
  }
  const hotList = [...hot].filter(n => !fixosNorm.includes(n));
  const nFixosHot = Math.min(nHot, hotList.length, Math.max(0, lp.numerosPorJogo - fixosNorm.length));
  const selecionados = sample(hotList, nFixosHot, rand);
  return completarJogo(selecionados, fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarPersistenciaCategoria(ultimos2: number[][], categoria: string, rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const meio = lp.numeroMinimo + Math.floor((lp.totalNumeros - 1) / 2);
  let catFunc: (n: number) => boolean;
  switch (categoria) {
    case 'impares':
      catFunc = n => n % 2 === 1;
      break;
    case 'primos':
      catFunc = n => lp.primosSet.has(n);
      break;
    case 'baixos':
      catFunc = n => n <= meio;
      break;
    case 'altos':
      catFunc = n => n > meio;
      break;
    case 'pares':
    default:
      catFunc = n => n % 2 === 0;
      break;
  }

  if (ultimos2.length < 2) {
    return gerarAleatorio(rand, lp, fixos, excluidos);
  }

  const catAnterior = ultimos2[0].filter(n => disponiveis.includes(n) && catFunc(n));
  const catAtual = ultimos2[1].filter(n => disponiveis.includes(n) && catFunc(n));
  const taxa = catAnterior.length > 0 && catAtual.length > 0
    ? catAnterior.filter(n => catAtual.includes(n)).length / Math.max(catAnterior.length, catAtual.length)
    : 0.5;

  const fixosForaCategoria = fixosNorm.filter(n => !catFunc(n));

  const poolCat = disponiveis.filter(n => !fixosNorm.includes(n) && catFunc(n));
  const outros = disponiveis.filter(n => !fixosNorm.includes(n) && !catFunc(n));

  const vagasCategoria = Math.max(0, lp.numerosPorJogo - fixosForaCategoria.length);
  const nCat = taxa > 0.5
    ? Math.min(Math.floor(rand() * 4) + Math.ceil(lp.numerosPorJogo * 0.45), poolCat.length, vagasCategoria)
    : Math.min(Math.floor(rand() * 3) + Math.ceil(lp.numerosPorJogo * 0.25), poolCat.length, vagasCategoria);

  const selecionadosCat = sample(poolCat, nCat, rand);
  const selecionadosOutros = sample(outros, Math.max(0, lp.numerosPorJogo - fixosNorm.length - selecionadosCat.length), rand);
  return completarJogo([...selecionadosCat, ...selecionadosOutros], fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarCiclo(cicloDados: Record<number, number> | undefined, rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  if (!cicloDados) {
    return gerarAleatorio(rand, lp, fixos, excluidos);
  }

  const pesos: Record<number, number> = {};
  for (const n of disponiveis) {
    if (fixosNorm.includes(n)) {
      pesos[n] = 100.0;
      continue;
    }
    const qtd = cicloDados[n] ?? 0;
    if (qtd === 0) pesos[n] = 4.0;
    else if (qtd <= 1) pesos[n] = 2.0;
    else pesos[n] = 1.0;
  }

  const totalPeso = Object.values(pesos).reduce((a, b) => a + b, 0);
  let jogo: number[] = [];
  let tentativas = 0;
  while (new Set(jogo).size < lp.numerosPorJogo && tentativas < 100) {
    jogo = [];
    while (jogo.length < lp.numerosPorJogo) {
      let acc = 0;
      const r = rand() * totalPeso;
      for (const n of disponiveis) {
        acc += pesos[n];
        if (acc >= r) {
          jogo.push(n);
          break;
        }
      }
    }
    tentativas++;
  }

  if (new Set(jogo).size < lp.numerosPorJogo) {
    return gerarAleatorio(rand, lp, fixos, excluidos);
  }

  return sorted([...new Set(jogo)]);
}

function mediaIntersecoes(jogo: number[], jogos: number[][]): number {
  if (jogos.length === 0) return 0;
  const s = new Set(jogo);
  const soma = jogos.reduce((acc, ex) => acc + [...s].filter(n => ex.includes(n)).length, 0);
  return soma / jogos.length;
}

interface FiltrosCobertura {
  colunas?: ColunasPosicionaisConstraint;
  dominios?: Array<number[] | null>;
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
  baseComparativo?: number[];
  filtroComparativo?: FiltroComparativo;
  categorias?: FiltroCategoria[];
}

function jogoValido(jogo: number[], filtros?: FiltrosCobertura): boolean {
  if (!filtros) return true;
  if (filtros.colunas && !satisfazColunas(jogo, filtros.colunas)) return false;
  if (filtros.dominios && !satisfazDominios(jogo, filtros.dominios)) return false;
  if (filtros.fixosPosicoes && !satisfazPosicoes(jogo, filtros.fixosPosicoes)) return false;
  if (filtros.excluidosPosicoes && !satisfazExclusaoPosicoes(jogo, filtros.excluidosPosicoes)) return false;
  if (filtros.filtroComparativo && !satisfazComparativo(jogo, filtros.baseComparativo ?? [], filtros.filtroComparativo)) return false;
  if (filtros.categorias && !satisfazCategorias(jogo, filtros.categorias)) return false;
  return true;
}

function garantirCobertura(jogos: number[][], rand: () => number, lp: LP, fixos: number[] = [], excluidos: number[] = [], filtros?: FiltrosCobertura): number[][] {
  const result = jogos.map(j => [...j]);
  if (result.length < 3) return result;

  const pool = Array.from({ length: lp.totalNumeros }, (_, i) => i + lp.numeroMinimo)
    .filter(n => !excluidos.includes(n) && !fixos.includes(n));
  const freq: Record<number, number> = {};
  for (const n of pool) freq[n] = 0;
  for (const j of result) for (const n of j) if (n in freq) freq[n]++;

  const ideal = (result.length * lp.numerosPorJogo) / Math.max(1, pool.length);

  // alvos: números sub-representados (prioridade: os que faltam totalmente)
  const alvos = pool.filter(n => freq[n] < ideal).sort((a, b) => freq[a] - freq[b]);

  for (const alvo of alvos) {
    // ordena jogos por redundância (maior média de interseção primeiro)
    const scores: number[] = result.map((j, idx) => {
      const outras = result.filter((_, i) => i !== idx);
      return mediaIntersecoes(j, outras);
    });
    const ordem = result.map((_, idx) => idx).sort((a, b) => scores[b] - scores[a]);

    let trocou = false;
    for (const idx of ordem) {
      const jogo = result[idx];

      // tenta trocar um número super-representado (> ideal) por um não-fixo
      const candidatos = jogo
        .map((n, pos) => ({ n, pos }))
        .filter(({ n }) => !fixos.includes(n) && freq[n] > ideal)
        .sort(() => rand() - 0.5);
      for (const { pos } of candidatos) {
        if (jogo.includes(alvo)) break;
        const novoJogo = sorted([...jogo.slice(0, pos), ...jogo.slice(pos + 1), alvo]);
        if (novoJogo.length === new Set(novoJogo).size
          && !result.some(j => JSON.stringify(j) === JSON.stringify(novoJogo))
          && jogoValido(novoJogo, filtros)) {
          result[idx] = novoJogo;
          freq[alvo] = (freq[alvo] ?? 0) + 1;
          freq[jogo[pos]] = freq[jogo[pos]] - 1;
          trocou = true;
          break;
        }
      }
      if (trocou) break;

      // fallback: qualquer número não-fixo
      const candidatos2 = jogo
        .map((n, pos) => ({ n, pos }))
        .filter(({ n }) => !fixos.includes(n))
        .sort(() => rand() - 0.5);
      for (const { pos } of candidatos2) {
        if (jogo.includes(alvo)) break;
        const novoJogo = sorted([...jogo.slice(0, pos), ...jogo.slice(pos + 1), alvo]);
        if (novoJogo.length === new Set(novoJogo).size
          && !result.some(j => JSON.stringify(j) === JSON.stringify(novoJogo))
          && jogoValido(novoJogo, filtros)) {
          result[idx] = novoJogo;
          freq[alvo] = (freq[alvo] ?? 0) + 1;
          freq[jogo[pos]] = freq[jogo[pos]] - 1;
          trocou = true;
          break;
        }
      }
      if (trocou) break;
    }
  }

  return result;
}

export function gerarJogosDiversificados(options: GeradorDiversificadoOptions): JogoGerado[] {
  const { resultados, cicloDados, nJogos = 5, seed, fixos, excluidos, colunasPosicionais, dominiosPosicionais, filtroComparativo, filtroCategorias, ordenacao = 'aleatorio', scoreSets, fixosPosicoes, excluidosPosicoes, estrategias: estrategiasFiltro } = options;
  const lp = buildLP(options);
  const rand = rng(seed);
  // números com exclusão apenas por posição permanecem no pool (só evitam certas posições)
  const excluidosCompletos = (excluidos ?? []).filter(n => !(excluidosPosicoes?.[n]?.length));
  const { fixosNorm, excluidosNorm, disponiveis } = normalizarConstraints(fixos, excluidosCompletos, lp.totalNumeros, lp.numeroMinimo);

  if (fixosNorm.length > lp.numerosPorJogo) {
    throw new Error(`Não é possível fixar mais de ${lp.numerosPorJogo} números. Recebido: ${fixosNorm.length}`);
  }
  if (fixosNorm.length + disponiveis.filter(n => !fixosNorm.includes(n)).length < lp.numerosPorJogo) {
    throw new Error(`Não há números suficientes disponíveis para completar ${lp.numerosPorJogo} dezenas com os exclusões/fixos informados.`);
  }

  const colunasNorm = normalizarColunas(colunasPosicionais, lp, fixosNorm, excluidosNorm);
  const dominiosNorm = normalizarDominios(dominiosPosicionais, lp, excluidosNorm);
  const categoriasNorm = normalizarCategorias(filtroCategorias, lp);
  const baseComparativo = resultados.length > 0 ? resultados[resultados.length - 1] : [];

  const temFiltroEstrategias = estrategiasFiltro && estrategiasFiltro.length > 0;

  if (nJogos === 0) {
    if (temFiltroEstrategias) {
      // "todas as combinações" não faz sentido com filtro de estratégia:
      // gera um lote grande usando apenas as estratégias selecionadas
    } else {
      return gerarTodasAsCombinacoes(options);
    }
  }

  const count = nJogos === 0 && temFiltroEstrategias ? 500 : nJogos;

  const rankingAtivo = ordenacao !== 'aleatorio';
  // com ranking, gera um pool maior de candidatos e seleciona os melhores/piores/balanceados
  const genCount = rankingAtivo ? Math.min(Math.max(count * 8, count + 40), 1500) : count;
  const scoreCtx = rankingAtivo ? construirScoreContext(resultados, lp, scoreSets) : null;
  const finalizar = (arrJogos: number[][], arrNomes: string[]): JogoGerado[] => {
    if (!scoreCtx) {
      return arrJogos.map((numeros, i) => buildJogo(numeros, arrNomes[i] ?? 'aleatorio', lp, rand));
    }
    const scores = arrJogos.map(j => scoreJogo(j, scoreCtx));
    const sel = selecionarPorScore(arrJogos, arrNomes, scores, count, ordenacao);
    return sel.jogos.map((numeros, i) => buildJogo(numeros, sel.nomes[i] ?? 'aleatorio', lp, rand, sel.scores[i]));
  };

  if (resultados.length === 0) {
    const jogos: number[][] = [];
    const maxTent = categoriasNorm || dominiosNorm
      ? Math.max(genCount * 2000, 10000)
      : Math.max(genCount * 5, 100);
    for (let i = 0; i < maxTent && jogos.length < genCount; i++) {
      const jogo = colunasNorm
        ? gerarComColunas(rand, lp, fixosNorm, excluidosNorm, disponiveis, colunasNorm)
        : gerarAleatorio(rand, lp, fixos, excluidosCompletos);
      if (jogo.length !== lp.numerosPorJogo) continue;
      if (colunasNorm && !satisfazColunas(jogo, colunasNorm)) continue;
      if (dominiosNorm && !satisfazDominios(jogo, dominiosNorm)) continue;
      if (!satisfazPosicoes(jogo, fixosPosicoes)) continue;
      if (!satisfazExclusaoPosicoes(jogo, excluidosPosicoes)) continue;
      if (!satisfazCategorias(jogo, categoriasNorm)) continue;
      if (jogos.some(ex => JSON.stringify(ex) === JSON.stringify(jogo))) continue;
      jogos.push(jogo);
    }
    const nome = colunasNorm ? 'colunas' : 'aleatorio';
    return finalizar(jogos, jogos.map(() => nome));
  }

  const ultimos = resultados.slice(-5);
  const ultimos3 = resultados.slice(-3);
  const ultimos2 = resultados.slice(-2);

  const baseHot = Math.max(2, Math.floor(lp.numerosPorJogo / 2));
  const minOverlap = Math.max(0, 2 * lp.numerosPorJogo - lp.totalNumeros);
  const maxIntersecao = Math.max(Math.ceil(lp.numerosPorJogo * 0.6), minOverlap + 2);

  const todasEstrategias: { nome: string; fn: () => number[] }[] = [
    { nome: 'atraso', fn: () => gerarAtraso(ultimos, rand, lp, fixos, excluidosCompletos) },
    { nome: 'hot7-9', fn: () => gerarHot(ultimos3, Math.min(Math.floor(rand() * 3) + baseHot, lp.numerosPorJogo), rand, lp, fixos, excluidosCompletos) },
    { nome: 'persistencia', fn: () => gerarPersistenciaCategoria(ultimos2, shuffle(['pares', 'impares', 'primos'], rand)[0], rand, lp, fixos, excluidosCompletos) },
    { nome: 'aleatorio', fn: () => gerarAleatorio(rand, lp, fixos, excluidosCompletos) },
    { nome: 'ciclo', fn: () => gerarCiclo(cicloDados, rand, lp, fixos, excluidosCompletos) },
    ...(colunasNorm ? [{ nome: 'colunas', fn: () => gerarComColunas(rand, lp, fixosNorm, excluidosNorm, disponiveis, colunasNorm) }] : []),
  ];

  const estrategias = estrategiasFiltro && estrategiasFiltro.length > 0
    ? todasEstrategias.filter(e => estrategiasFiltro.includes(e.nome))
    : todasEstrategias;

  const estrategiasUsaveis = estrategias.length > 0 ? estrategias : todasEstrategias;

  const jogos: number[][] = [];
  const nomes: string[] = [];
  const temComparativo = filtroComparativo !== undefined && baseComparativo.length > 0;
  const temCategorias = categoriasNorm !== undefined;
  let tentativa = 0;
  let semProgresso = 0;
  const buscaAmpla = temComparativo || temCategorias || dominiosNorm !== undefined;
  const maxSemProgresso = buscaAmpla ? Math.max(genCount * 4000, 10000) : Math.max(genCount * 5, 100);
  const maxTentativas = buscaAmpla ? Math.max(genCount * 8000, 20000) : Math.max(genCount * 40, 400);

  while (jogos.length < genCount && tentativa < maxTentativas && semProgresso < maxSemProgresso) {
    tentativa++;
    const estrategia = estrategiasUsaveis[jogos.length % estrategiasUsaveis.length];
    const jogo = aplicarConstraints(estrategia.fn(), rand, lp, fixos, excluidosCompletos);
    const nome = estrategia.nome;

    if (jogo.length !== lp.numerosPorJogo || jogos.some(ex => JSON.stringify(ex) === JSON.stringify(jogo))) {
      semProgresso++;
      continue;
    }
    if (colunasNorm && !satisfazColunas(jogo, colunasNorm)) {
      semProgresso++;
      continue;
    }
    if (dominiosNorm && !satisfazDominios(jogo, dominiosNorm)) {
      semProgresso++;
      continue;
    }
    if (fixosPosicoes && !satisfazPosicoes(jogo, fixosPosicoes)) {
      semProgresso++;
      continue;
    }
    if (excluidosPosicoes && !satisfazExclusaoPosicoes(jogo, excluidosPosicoes)) {
      semProgresso++;
      continue;
    }
    if (filtroComparativo && !satisfazComparativo(jogo, baseComparativo, filtroComparativo)) {
      semProgresso++;
      continue;
    }
    if (categoriasNorm && !satisfazCategorias(jogo, categoriasNorm)) {
      semProgresso++;
      continue;
    }

    if (!colunasNorm && !filtroComparativo && !temCategorias && jogos.length > 0) {
      const inter = mediaIntersecoes(jogo, jogos);
      if (inter > maxIntersecao) {
        semProgresso++;
        continue;
      }
    }

    jogos.push(jogo);
    nomes.push(nome);
    semProgresso = 0;
  }

  let fallbackGuard = 0;
  semProgresso = 0;
  const maxFallback = buscaAmpla ? Math.max(genCount * 8000, 20000) : Math.max(genCount * 20, 500);
  while (jogos.length < genCount && fallbackGuard++ < maxFallback && semProgresso < maxSemProgresso) {
    const filtroAtivo = estrategiasFiltro && estrategiasFiltro.length > 0;
    let jogo: number[];
    let nomeFallback: string;
    if (filtroAtivo) {
      const estrategia = estrategiasUsaveis[jogos.length % estrategiasUsaveis.length];
      jogo = aplicarConstraints(estrategia.fn(), rand, lp, fixos, excluidosCompletos);
      nomeFallback = estrategia.nome;
    } else {
      jogo = temComparativo
        ? gerarAleatorio(rand, lp, fixos, excluidosCompletos)
        : colunasNorm
          ? gerarComColunas(rand, lp, fixosNorm, excluidosNorm, disponiveis, colunasNorm)
          : aplicarConstraints(gerarAleatorio(rand, lp, fixos, excluidosCompletos), rand, lp, fixos, excluidosCompletos);
      nomeFallback = temComparativo ? 'comparativo' : colunasNorm ? 'colunas' : 'aleatorio';
    }
    if (jogo.length === lp.numerosPorJogo && !jogos.some(ex => JSON.stringify(ex) === JSON.stringify(jogo))) {
      if (colunasNorm && !satisfazColunas(jogo, colunasNorm)) {
        semProgresso++;
        continue;
      }
      if (dominiosNorm && !satisfazDominios(jogo, dominiosNorm)) {
        semProgresso++;
        continue;
      }
      if (fixosPosicoes && !satisfazPosicoes(jogo, fixosPosicoes)) {
        semProgresso++;
        continue;
      }
      if (excluidosPosicoes && !satisfazExclusaoPosicoes(jogo, excluidosPosicoes)) {
        semProgresso++;
        continue;
      }
      if (filtroComparativo && !satisfazComparativo(jogo, baseComparativo, filtroComparativo)) {
        semProgresso++;
        continue;
      }
      if (categoriasNorm && !satisfazCategorias(jogo, categoriasNorm)) {
        semProgresso++;
        continue;
      }
      jogos.push(jogo);
      nomes.push(nomeFallback);
      semProgresso = 0;
    } else {
      semProgresso++;
    }
  }

  let jogosFinais = jogos;
  if (jogos.length >= 3) {
    jogosFinais = garantirCobertura(jogos, rand, lp, fixosNorm, excluidosNorm, {
      colunas: colunasNorm,
      dominios: dominiosNorm,
      fixosPosicoes,
      excluidosPosicoes,
      baseComparativo,
      filtroComparativo,
      categorias: categoriasNorm,
    });
    if (!dominiosNorm) {
      jogosFinais = jogosFinais.map(j => aplicarConstraints(j, rand, lp, fixos, excluidosCompletos));
    }
  }

  return finalizar(jogosFinais, jogosFinais.map((_, i) => nomes[i] ?? 'aleatorio'));
}

export function* iterarTodasAsCombinacoes(options: GeradorDiversificadoOptions): Generator<JogoGerado> {
  const { resultados, fixos, excluidos, colunasPosicionais, dominiosPosicionais, filtroComparativo, fixosPosicoes, excluidosPosicoes, filtroCategorias } = options;
  const lp = buildLP(options);
  const rand = rng(options.seed);
  const excluidosCompletos = (excluidos ?? []).filter(n => !(excluidosPosicoes?.[n]?.length));
  const { fixosNorm, excluidosNorm, disponiveis } = normalizarConstraints(fixos, excluidosCompletos, lp.totalNumeros, lp.numeroMinimo);

  if (fixosNorm.length > lp.numerosPorJogo) {
    throw new Error(`Não é possível fixar mais de ${lp.numerosPorJogo} números. Recebido: ${fixosNorm.length}`);
  }
  if (fixosNorm.length + disponiveis.filter(n => !fixosNorm.includes(n)).length < lp.numerosPorJogo) {
    throw new Error(`Não há números suficientes disponíveis para completar ${lp.numerosPorJogo} dezenas com os exclusões/fixos informados.`);
  }

  const colunasNorm = normalizarColunas(colunasPosicionais, lp, fixosNorm, excluidosNorm);
  const dominiosNorm = normalizarDominios(dominiosPosicionais, lp, excluidosNorm);
  const categoriasNorm = normalizarCategorias(filtroCategorias, lp);
  const baseComparativo = resultados.length > 0 ? resultados[resultados.length - 1] : [];
  const pool = disponiveis.filter(n => !fixosNorm.includes(n));
  const k = lp.numerosPorJogo - fixosNorm.length;

  for (const combo of gerarCombinacoes(pool, k)) {
    const jogo = sorted([...fixosNorm, ...combo]);
    if (colunasNorm && !satisfazColunas(jogo, colunasNorm)) continue;
    if (dominiosNorm && !satisfazDominios(jogo, dominiosNorm)) continue;
    if (!satisfazPosicoes(jogo, fixosPosicoes)) continue;
    if (!satisfazExclusaoPosicoes(jogo, excluidosPosicoes)) continue;
    if (!satisfazComparativo(jogo, baseComparativo, filtroComparativo)) continue;
    if (!satisfazCategorias(jogo, categoriasNorm)) continue;
    yield buildJogo(jogo, 'todas-combinacoes', lp, rand);
  }
}

function gerarTodasAsCombinacoes(options: GeradorDiversificadoOptions): JogoGerado[] {
  const todas = [...iterarTodasAsCombinacoes(options)];
  const rand = rng(options.seed);
  for (let i = todas.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [todas[i], todas[j]] = [todas[j], todas[i]];
  }
  return todas;
}

function gerarTrevos(rand: () => number, lp: LP): number[] {
  const total = lp.trevosTotal ?? 0;
  const porJogo = lp.trevosPorJogo ?? 0;
  const min = lp.trevosMin ?? 1;
  if (total <= 0 || porJogo <= 0) return [];
  const pool = Array.from({ length: total }, (_, i) => i + min);
  return sorted(sample(pool, Math.min(porJogo, pool.length), rand));
}

function buildJogo(numeros: number[], estrategia: string, lp: LP, rand: () => number, score?: number): JogoGerado {
  const trevos = gerarTrevos(rand, lp);
  return {
    numeros,
    trevos: trevos.length > 0 ? trevos : undefined,
    estrategia,
    soma: numeros.reduce((a, b) => a + b, 0),
    pares: numeros.filter(n => n % 2 === 0).length,
    impares: numeros.filter(n => n % 2 === 1).length,
    primos: numeros.filter(n => lp.primosSet.has(n)).length,
    ...(score !== undefined ? { score } : {}),
  };
}

export function calcularCobertura(jogos: number[][], totalNumeros: number = 25, numeroMinimo: number = 1): { total: number; frequencia: Record<number, number> } {
  const freq: Record<number, number> = {};
  for (let i = numeroMinimo; i < numeroMinimo + totalNumeros; i++) freq[i] = 0;
  for (const j of jogos) {
    for (const n of j) freq[n] = (freq[n] ?? 0) + 1;
  }
  const total = Object.values(freq).filter(v => v > 0).length;
  return { total, frequencia: freq };
}

export function calcularEstatisticasJogos(jogos: JogoGerado[], totalNumeros: number = 25, numeroMinimo: number = 1) {
  const todasEstrategias = jogos.map(j => j.estrategia);
  const estrategiaCounts = todasEstrategias.reduce((acc, e) => {
    acc[e] = (acc[e] ?? 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const cobertura = calcularCobertura(jogos.map(j => j.numeros), totalNumeros, numeroMinimo);

  return {
    total: jogos.length,
    cobertura: cobertura.total,
    frequencia: cobertura.frequencia,
    estrategias: estrategiaCounts,
  };
}
