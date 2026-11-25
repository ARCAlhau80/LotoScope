import type { LottoDesignConhecido } from '../fechamento-combinatorio';
import lottoLotofacil from '@/data/lotto-lotofacil.json';
import lottoMegasena from '@/data/lotto-megasena.json';

/**
 * Registro de lotto designs L(v,k,m,t) pré-computados e verificados.
 *
 * Diferente do covering C(v,k,t) — que exige todo t-subconjunto dentro de algum
 * bloco — o lotto design exige apenas que todo m-subconjunto do universo tenha
 * interseção >= t com algum bloco. Como na Lotofácil só m dezenas do universo
 * restante são sorteadas, isso reduz drasticamente o número de apostas.
 */
const lottoLotofacilJson = lottoLotofacil as unknown as Record<string, LottoDesignConhecido>;
const lottoMegasenaJson = lottoMegasena as unknown as Record<string, LottoDesignConhecido>;

const REGISTRY: Record<string, Record<string, LottoDesignConhecido>> = {
  lotofacil: {
    ...lottoLotofacilJson,
  },
  megasena: {
    ...lottoMegasenaJson,
  },
};

export function buscarLottoDesign(
  loteriaId: string,
  v: number,
  k: number,
  m: number,
  t: number,
): LottoDesignConhecido | null {
  const registry = REGISTRY[loteriaId];
  if (!registry) return null;

  const exato = registry[`${v},${k},${m},${t}`];
  if (exato) return exato;

  // Um design L(v,k,m,t') com t' > t é mais forte e, portanto, também garante
  // t acertos. Reaproveitá-lo evita o efeito perverso de "relaxar o alvo e
  // receber MAIS apostas": sem isto, ao baixar t o registro exato some e o
  // código cai num cover C(v,k,t) genérico (ex.: 2 fixos, t=7 -> 319 apostas)
  // mesmo existindo L(23,13,13,9) com 33 apostas, que já garante 11 acertos.
  // Escolhe o de menor custo (blocos); em empate, o t' mais próximo do pedido.
  let melhor: LottoDesignConhecido | null = null;
  for (const [chave, design] of Object.entries(registry)) {
    const [dv, dk, dm, dt] = chave.split(',').map(Number);
    if (dv !== v || dk !== k || dm !== m || dt < t) continue;
    if (
      !melhor
      || design.blocos.length < melhor.blocos.length
      || (design.blocos.length === melhor.blocos.length && dt < melhor.t)
    ) {
      melhor = design;
    }
  }
  return melhor;
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
