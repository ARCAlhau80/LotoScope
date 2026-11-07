import { COVERS_CONHECIDOS, type CoverConhecido } from '../fechamento-combinatorio';
import coversLotofacil from '@/data/covers-lotofacil.json';
import coversMegasena from '@/data/covers-megasena.json';

const coversLotofacilJson = coversLotofacil as unknown as Record<string, CoverConhecido>;
const coversMegasenaJson = coversMegasena as unknown as Record<string, CoverConhecido>;

const REGISTRY: Record<string, Record<string, CoverConhecido>> = {
  lotofacil: {
    ...Object.fromEntries(COVERS_CONHECIDOS.map(c => [`${c.v},${c.k},${c.t}`, c])),
    ...coversLotofacilJson,
  },
  megasena: {
    ...coversMegasenaJson,
  },
};

export function buscarCover(
  loteriaId: string,
  v: number,
  k: number,
  t: number,
): CoverConhecido | null {
  return REGISTRY[loteriaId]?.[`${v},${k},${t}`] ?? null;
}

export function temCovers(loteriaId: string): boolean {
  return Object.keys(REGISTRY[loteriaId] ?? {}).length > 0;
}
