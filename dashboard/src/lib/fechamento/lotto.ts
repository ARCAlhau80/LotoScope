import type { LottoDesignConhecido } from '../fechamento-combinatorio';
import lottoLotofacil from '@/data/lotto-lotofacil.json';

/**
 * Registro de lotto designs L(v,k,m,t) pré-computados e verificados.
 *
 * Diferente do covering C(v,k,t) — que exige todo t-subconjunto dentro de algum
 * bloco — o lotto design exige apenas que todo m-subconjunto do universo tenha
 * interseção >= t com algum bloco. Como na Lotofácil só m dezenas do universo
 * restante são sorteadas, isso reduz drasticamente o número de apostas.
 */
const lottoLotofacilJson = lottoLotofacil as unknown as Record<string, LottoDesignConhecido>;

const REGISTRY: Record<string, Record<string, LottoDesignConhecido>> = {
  lotofacil: {
    ...lottoLotofacilJson,
  },
};

export function buscarLottoDesign(
  loteriaId: string,
  v: number,
  k: number,
  m: number,
  t: number,
): LottoDesignConhecido | null {
  return REGISTRY[loteriaId]?.[`${v},${k},${m},${t}`] ?? null;
}

export function temLottoDesigns(loteriaId: string): boolean {
  return Object.keys(REGISTRY[loteriaId] ?? {}).length > 0;
}

/** Mapeia os pontos 1..v do design para as dezenas reais do universo. */
export function mapearLottoDesign(design: LottoDesignConhecido, universo: number[]): number[][] {
  const u = [...universo].sort((a, b) => a - b);
  return design.blocos.map(bloco =>
    bloco.map(p => u[p - 1]).filter((n): n is number => n !== undefined).sort((a, b) => a - b),
  );
}
