import {
  MES_SORTE_MAX,
  MES_SORTE_MIN,
  type LotteryConfig,
} from './lottery-config';

/** Mês fixo (1-12) ou "aleatorio" (um mês por aposta). */
export type ModoMesSorte = number | 'aleatorio';

/**
 * Normaliza o parâmetro vindo da URL/body.
 *
 * Retorna `null` quando a loteria não tem Mês da Sorte. Para Dia de Sorte,
 * qualquer valor inválido cai em "aleatorio" (mesmo comportamento da
 * Surpresinha), sem quebrar a geração.
 */
export function resolverModoMesSorte(cfg: LotteryConfig, raw: unknown): ModoMesSorte | null {
  if (!cfg.mes_sorte) return null;
  if (raw == null || raw === '') return 'aleatorio';

  const texto = String(raw).trim().toLowerCase();
  if (['aleatorio', 'aleatório', 'auto', 'random', 'sorteio', 'surpresinha'].includes(texto)) {
    return 'aleatorio';
  }

  const numero = Number.parseInt(texto, 10);
  if (Number.isInteger(numero) && numero >= MES_SORTE_MIN && numero <= MES_SORTE_MAX) {
    return numero;
  }
  return 'aleatorio';
}

function hash32(valor: number): number {
  let n = valor >>> 0;
  n = Math.imul(n ^ (n >>> 16), 0x45d9f3b) >>> 0;
  n = Math.imul(n ^ (n >>> 16), 0x45d9f3b) >>> 0;
  return (n ^ (n >>> 16)) >>> 0;
}

/** Mês determinístico para a aposta `indice` (1-based) a partir da seed. */
export function mesDaAposta(modo: ModoMesSorte, seed: number | undefined, indice: number): number {
  if (typeof modo === 'number') return modo;
  const base = hash32((seed ?? 1) ^ Math.imul(indice + 1, 0x9e3779b1));
  return (base % MES_SORTE_MAX) + MES_SORTE_MIN;
}

/** Atribui o mês a cada jogo sem tocar nas dezenas (regras do gerador intactas). */
export function aplicarMesSorteLista<T extends { mes?: number }>(
  jogos: T[],
  modo: ModoMesSorte | null,
  seed?: number,
): T[] {
  if (modo === null) return jogos;
  return jogos.map((jogo, i) => ({ ...jogo, mes: mesDaAposta(modo, seed, i) }));
}
