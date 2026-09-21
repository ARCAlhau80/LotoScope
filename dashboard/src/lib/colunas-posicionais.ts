import type { ColunasPosicionaisConstraint, FiltroComparativo } from './gerador-diversificado';

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