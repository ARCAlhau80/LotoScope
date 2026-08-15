import { carregarResultados } from './database';

export const CORINGA = 1;

export const GRUPOS: Record<string, number[]> = {
  A: [2, 5, 6, 8, 11, 13, 17, 20],
  B: [3, 7, 9, 12, 14, 18, 19, 21],
  C: [4, 10, 15, 16, 22, 23, 24, 25],
};

type GrupoId = 'A' | 'B' | 'C';

interface HitRecord {
  concurso: number;
  coringa: number;
  A: number;
  B: number;
  C: number;
  [key: string]: number;
}

interface GrupoStats {
  media: number;
  mediana: number;
  desvio: number;
  min: number;
  max: number;
  moda: number[];
  freq_30: number;
  freq_30_esperada: number;
}

export interface AnaliseGruposData {
  grupos: Record<GrupoId, readonly number[]>;
  coringa: number;
  total_sorteios: number;
  ultimo_concurso: number;
  stats: Record<GrupoId, GrupoStats>;
  composicoes_comuns: { a: number; b: number; c: number; freq: number; pct: number }[];
  ultimos: HitRecord[];
  coringa_freq: number;
  coringa_freq_30: number;
  media_acertos_total: number;
}

function calcularMedia(arr: number[]): number {
  return arr.reduce((s, v) => s + v, 0) / arr.length;
}

function calcularMediana(arr: number[]): number {
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function calcularDesvio(arr: number[], media: number): number {
  return Math.sqrt(arr.reduce((s, v) => s + (v - media) ** 2, 0) / arr.length);
}

function calcularModa(arr: number[]): number[] {
  const freq: Record<number, number> = {};
  for (const v of arr) freq[v] = (freq[v] || 0) + 1;
  const maxFreq = Math.max(...Object.values(freq));
  return Object.entries(freq)
    .filter(([_, f]) => f === maxFreq)
    .map(([v]) => Number(v));
}

function contarHits(numeros: number[], grupo: readonly number[]): number {
  const set = new Set(grupo);
  return numeros.filter(n => set.has(n)).length;
}

export async function analiseGrupos(): Promise<AnaliseGruposData> {
  const resultados = await carregarResultados();
  const total = resultados.length;
  const ultimo = resultados[total - 1];

  const registros: HitRecord[] = resultados.map(r => ({
    concurso: r.concurso,
    coringa: r.numeros.includes(CORINGA) ? 1 : 0,
    A: contarHits(r.numeros, GRUPOS.A),
    B: contarHits(r.numeros, GRUPOS.B),
    C: contarHits(r.numeros, GRUPOS.C),
  }));

  const stats: Record<GrupoId, GrupoStats> = {} as Record<GrupoId, GrupoStats>;
  for (const g of ['A', 'B', 'C'] as GrupoId[]) {
    const vals = registros.map(r => r[g]);
    const media = calcularMedia(vals);
    const recentes = registros.slice(-30);
    const freq30 = recentes.reduce((s, r) => s + r[g], 0);
    stats[g] = {
      media: Math.round(media * 100) / 100,
      mediana: calcularMediana(vals),
      desvio: Math.round(calcularDesvio(vals, media) * 100) / 100,
      min: Math.min(...vals),
      max: Math.max(...vals),
      moda: calcularModa(vals),
      freq_30: freq30,
      freq_30_esperada: Math.round(media * 30 * 100) / 100,
    };
  }

  const composFreq: Record<string, { a: number; b: number; c: number; count: number }> = {};
  for (const r of registros) {
    const key = `${r.A},${r.B},${r.C}`;
    if (!composFreq[key]) composFreq[key] = { a: r.A, b: r.B, c: r.C, count: 0 };
    composFreq[key].count++;
  }

  const composicoes_comuns = Object.values(composFreq)
    .sort((x, y) => y.count - x.count)
    .slice(0, 20)
    .map(c => ({
      a: c.a,
      b: c.b,
      c: c.c,
      freq: c.count,
      pct: Math.round(c.count / total * 10000) / 100,
    }));

  const coringaFreq = registros.filter(r => r.coringa === 1).length;
  const coringaFreq30 = registros.slice(-30).filter(r => r.coringa === 1).length;

  return {
    grupos: { A: GRUPOS.A, B: GRUPOS.B, C: GRUPOS.C },
    coringa: CORINGA,
    total_sorteios: total,
    ultimo_concurso: ultimo.concurso,
    stats,
    composicoes_comuns,
    ultimos: registros.slice(-30).reverse(),
    coringa_freq: coringaFreq,
    coringa_freq_30: coringaFreq30,
    media_acertos_total: stats.A.media + stats.B.media + stats.C.media,
  };
}
