import type { ColunasPosicionaisConstraint, FiltroComparativo, FiltroCategoria, OrdenacaoJogos } from './gerador-diversificado';

const MAX_COLS = 5;

export function parseColunasPosicionais(
  colunasParam: string | null,
  setsParam: string | null
): ColunasPosicionaisConstraint | undefined {
  if (!colunasParam || !setsParam) return undefined;

  const parts = colunasParam.split(',');
  const sets = setsParam
    .split(';')
    .map(g => g.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n)))
    .slice(0, MAX_COLS);

  const n = Math.min(MAX_COLS, Math.max(sets.length, parts.length));
  if (n === 0) return undefined;

  const mins: number[] = [];
  const maxs: number[] = [];
  for (let i = 0; i < n; i++) {
    const raw = (parts[i] ?? '').trim();
    let min = 0;
    let max = (sets[i] ?? []).length;
    if (raw !== '') {
      const nums = raw.split('-').map(s => parseInt(s, 10));
      if (nums.some(x => isNaN(x))) return undefined;
      if (nums.length === 1) {
        min = nums[0];
        max = Number.POSITIVE_INFINITY;
      } else if (nums.length === 2) {
        min = Math.min(nums[0], nums[1]);
        max = Math.max(nums[0], nums[1]);
      } else {
        return undefined;
      }
    }
    if (min < 0) return undefined;
    mins.push(min);
    maxs.push(max);
  }

  return { sets: sets.slice(0, n).map(s => [...new Set(s)]), mins, maxs };
}

export function parseFixosPosicoes(s: string | null): Record<number, number[]> | undefined {
  if (!s) return undefined;
  const out: Record<number, number[]> = {};
  for (const part of s.split(';')) {
    const [numStr, posStr] = part.split(':');
    const n = parseInt((numStr ?? '').trim(), 10);
    if (isNaN(n)) continue;
    const pos = (posStr ?? '')
      .split(',')
      .map(x => parseInt(x.trim(), 10))
      .filter(x => !isNaN(x) && x >= 1);
    if (pos.length > 0) out[n] = [...new Set(pos)];
  }
  return Object.keys(out).length > 0 ? out : undefined;
}

export function parseExcluidosPosicoes(s: string | null): Record<number, number[]> | undefined {
  if (!s) return undefined;
  const out: Record<number, number[]> = {};
  for (const part of s.split(';')) {
    const [numStr, posStr] = part.split(':');
    const n = parseInt((numStr ?? '').trim(), 10);
    if (isNaN(n)) continue;
    const pos = (posStr ?? '')
      .split(',')
      .map(x => parseInt(x.trim(), 10))
      .filter(x => !isNaN(x) && x >= 1);
    if (pos.length > 0) out[n] = [...new Set(pos)];
  }
  return Object.keys(out).length > 0 ? out : undefined;
}

export function parseFiltroComparativo(s: string | null): FiltroComparativo | undefined {
  if (!s) return undefined;
  const parts = s.split(',');
  const keys = ['maiores', 'iguais', 'menores'] as const;
  const f: FiltroComparativo = {};
  for (let i = 0; i < 3; i++) {
    const raw = (parts[i] ?? '').trim();
    if (!raw) continue;
    const nums = raw.split('-').map(x => parseInt(x, 10));
    if (nums.some(x => isNaN(x))) return undefined;
    if (nums.length === 1) {
      f[keys[i]] = { min: nums[0], max: nums[0] };
    } else if (nums.length === 2) {
      f[keys[i]] = { min: Math.min(nums[0], nums[1]), max: Math.max(nums[0], nums[1]) };
    } else {
      return undefined;
    }
  }
  if (!f.maiores && !f.iguais && !f.menores) return undefined;
  return f;
}

export function parseFiltroCategorias(rangesParam: string | null, setsParam: string | null): FiltroCategoria[] | undefined {
  if (!rangesParam || !setsParam) return undefined;
  const sets = setsParam
    .split(';')
    .map(g => g.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n)));
  const ranges = rangesParam.split(',');
  const n = Math.max(sets.length, ranges.length);
  const out: FiltroCategoria[] = [];
  for (let i = 0; i < n; i++) {
    const raw = (ranges[i] ?? '').trim();
    if (!raw) continue;
    const nums = raw.split('-').map(s => parseInt(s.trim(), 10));
    if (nums.some(x => isNaN(x))) return undefined;
    let min: number;
    let max: number;
    if (nums.length === 1) {
      min = nums[0];
      max = nums[0];
    } else if (nums.length === 2) {
      min = Math.min(nums[0], nums[1]);
      max = Math.max(nums[0], nums[1]);
    } else {
      return undefined;
    }
    if (min < 0 || max < 0) return undefined;
    const numeros = [...new Set(sets[i] ?? [])];
    if (numeros.length === 0) continue;
    out.push({ numeros, min, max });
  }
  return out.length > 0 ? out : undefined;
}

export function parseFiltroRepetidos(rangesParam: string | null, setsParam: string | null): FiltroCategoria[] | undefined {
  return parseFiltroCategorias(rangesParam, setsParam);
}

export function parseOrdenacao(s: string | null): OrdenacaoJogos | undefined {
  if (!s) return undefined;
  const v = s.trim();
  if (v === 'melhores' || v === 'piores' || v === 'balanceado' || v === 'aleatorio') return v;
  return undefined;
}

// Formato: "1,2,3;2,3,4;..." — um grupo por posicao ordenada (N1, N2, ...).
// Grupo vazio = sem restricao para aquela posicao.
export function parseDominiosPosicionais(s: string | null): number[][] | undefined {
  if (!s) return undefined;
  const grupos = s.split(';').map(g =>
    [...new Set(
      g.split(',')
        .map(x => parseInt(x.trim(), 10))
        .filter(n => !isNaN(n) && n > 0)
    )]
  );
  if (grupos.every(g => g.length === 0)) return undefined;
  return grupos;
}

// Formato: "chave:n1,n2,n3;chave2:n4,n5" (ex.: "quentes:1,4,7;grupoA:2,5,6")
export function parseScoreSets(s: string | null): Record<string, number[]> | undefined {
  if (!s) return undefined;
  const out: Record<string, number[]> = {};
  for (const part of s.split(';')) {
    const sep = part.indexOf(':');
    if (sep <= 0) continue;
    const key = part.slice(0, sep).trim();
    const nums = part
      .slice(sep + 1)
      .split(',')
      .map(x => parseInt(x.trim(), 10))
      .filter(n => !isNaN(n));
    if (key && nums.length > 0) out[key] = [...new Set(nums)];
  }
  return Object.keys(out).length > 0 ? out : undefined;
}