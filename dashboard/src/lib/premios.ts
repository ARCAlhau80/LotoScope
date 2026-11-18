import { combinacoes } from './lottery-config';

export interface FaixaPremio {
  nome: string;
  acertos: number;
  trevosMin?: number;
  trevosMax?: number;
  valor: number;
  fixo: boolean;
  /** 'mes' = Mês da Sorte (Dia de Sorte), prêmio independente e cumulativo. */
  tipo?: 'acertos' | 'mes';
  observacao?: string;
}

export interface PremioResult {
  faixa: FaixaPremio | null;
  premiado: boolean;
}

type TabelaPremios = FaixaPremio[];

const TABELA: Record<string, TabelaPremios> = {
  lotofacil: [
    { nome: "15 acertos", acertos: 15, valor: 1_500_000, fixo: false, observacao: "≈ rateio" },
    { nome: "14 acertos", acertos: 14, valor: 1_500, fixo: false, observacao: "≈ rateio" },
    { nome: "13 acertos", acertos: 13, valor: 35, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "12 acertos", acertos: 12, valor: 14, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "11 acertos", acertos: 11, valor: 7, fixo: true, observacao: "valor fixo Caixa" },
  ],
  megasena: [
    { nome: "Sena (6)", acertos: 6, valor: 40_000_000, fixo: false, observacao: "≈ rateio" },
    { nome: "Quina (5)", acertos: 5, valor: 40_000, fixo: false, observacao: "≈ rateio" },
    { nome: "Quadra (4)", acertos: 4, valor: 1_000, fixo: false, observacao: "≈ rateio" },
  ],
  quina: [
    { nome: "Quina (5)", acertos: 5, valor: 10_000_000, fixo: false, observacao: "≈ rateio (varia por concurso)" },
    { nome: "Quadra (4)", acertos: 4, valor: 10_000, fixo: false, observacao: "≈ rateio (varia por concurso)" },
    { nome: "Terno (3)", acertos: 3, valor: 150, fixo: false, observacao: "≈ rateio (varia por concurso)" },
    { nome: "Duque (2)", acertos: 2, valor: 5, fixo: false, observacao: "≈ rateio (varia por concurso)" },
  ],
  duplasena: [
    { nome: "Sena (6)", acertos: 6, valor: 1_500_000, fixo: false, observacao: "≈ rateio 1º sorteio" },
    { nome: "Quina (5)", acertos: 5, valor: 5_000, fixo: false, observacao: "≈ rateio" },
    { nome: "Quadra (4)", acertos: 4, valor: 120, fixo: false, observacao: "≈ rateio" },
    { nome: "Terno (3)", acertos: 3, valor: 3, fixo: false, observacao: "≈ rateio" },
  ],
  lotomania: [
    { nome: "20 acertos", acertos: 20, valor: 3_000_000, fixo: false, observacao: "≈ rateio" },
    { nome: "19 acertos", acertos: 19, valor: 60_000, fixo: false, observacao: "≈ rateio" },
    { nome: "18 acertos", acertos: 18, valor: 2_100, fixo: false, observacao: "≈ rateio" },
    { nome: "17 acertos", acertos: 17, valor: 200, fixo: false, observacao: "≈ rateio" },
    { nome: "16 acertos", acertos: 16, valor: 35, fixo: false, observacao: "≈ rateio" },
    { nome: "15 acertos", acertos: 15, valor: 8, fixo: false, observacao: "≈ rateio" },
    { nome: "0 acertos", acertos: 0, valor: 500, fixo: false, observacao: "≈ rateio" },
  ],
  diadesorte: [
    { nome: "7 acertos", acertos: 7, valor: 1_500_000, fixo: false, observacao: "≈ rateio" },
    { nome: "6 acertos", acertos: 6, valor: 2_000, fixo: false, observacao: "≈ rateio" },
    { nome: "5 acertos", acertos: 5, valor: 25, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "4 acertos", acertos: 4, valor: 5, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "Mês da Sorte", acertos: -1, valor: 2.5, fixo: true, tipo: "mes", observacao: "prêmio fixo Caixa · independente e cumulativo" },
  ],
  timemania: [
    { nome: "7 acertos", acertos: 7, valor: 3_000_000, fixo: false, observacao: "≈ rateio" },
    { nome: "6 acertos", acertos: 6, valor: 30_000, fixo: false, observacao: "≈ rateio" },
    { nome: "5 acertos", acertos: 5, valor: 1_500, fixo: false, observacao: "≈ rateio" },
    { nome: "4 acertos", acertos: 4, valor: 10.5, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "3 acertos", acertos: 3, valor: 3.5, fixo: true, observacao: "valor fixo Caixa" },
  ],
  supersete: [
    { nome: "7 acertos", acertos: 7, valor: 8_000_000, fixo: false, observacao: "≈ rateio" },
    { nome: "6 acertos", acertos: 6, valor: 28_000, fixo: false, observacao: "≈ rateio" },
    { nome: "5 acertos", acertos: 5, valor: 1_200, fixo: false, observacao: "≈ rateio" },
    { nome: "4 acertos", acertos: 4, valor: 70, fixo: false, observacao: "≈ rateio" },
    { nome: "3 acertos", acertos: 3, valor: 6, fixo: true, observacao: "valor fixo Caixa" },
  ],
  maismilionaria: [
    { nome: "6+2", acertos: 6, trevosMin: 2, trevosMax: 2, valor: 10_000_000, fixo: false, observacao: "≈ rateio (mín. R$10M)" },
    { nome: "6+1 ou 6+0", acertos: 6, trevosMin: 0, trevosMax: 1, valor: 100_000, fixo: false, observacao: "≈ rateio" },
    { nome: "5+2", acertos: 5, trevosMin: 2, trevosMax: 2, valor: 50_000, fixo: false, observacao: "≈ rateio" },
    { nome: "5+1 ou 5+0", acertos: 5, trevosMin: 0, trevosMax: 1, valor: 10_000, fixo: false, observacao: "≈ rateio" },
    { nome: "4+2", acertos: 4, trevosMin: 2, trevosMax: 2, valor: 3_000, fixo: false, observacao: "≈ rateio" },
    { nome: "4+1 ou 4+0", acertos: 4, trevosMin: 0, trevosMax: 1, valor: 1_500, fixo: false, observacao: "≈ rateio" },
    { nome: "3+2", acertos: 3, trevosMin: 2, trevosMax: 2, valor: 50, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "3+1", acertos: 3, trevosMin: 1, trevosMax: 1, valor: 24, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "2+2", acertos: 2, trevosMin: 2, trevosMax: 2, valor: 12, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "2+1", acertos: 2, trevosMin: 1, trevosMax: 1, valor: 6, fixo: true, observacao: "valor fixo Caixa" },
  ],
};

export function tabelaPremios(loteria: string): FaixaPremio[] {
  return TABELA[loteria] ?? [];
}

/** Valor fixo do Mês da Sorte por aposta simples de 7 dezenas. */
export const PREMIO_MES_SORTE = 2.5;

/**
 * Prêmio do Mês da Sorte para uma aposta com `dezenas` dezenas.
 *
 * A Caixa paga R$ 2,50 por combinação de 7 dezenas da aposta quando o mês
 * escolhido é sorteado (ex.: 8 dezenas = 8 × 2,50 = R$ 20,00).
 */
export function premioMesSorte(loteria: string, dezenas: number): number {
  if (loteria !== 'diadesorte') return 0;
  return PREMIO_MES_SORTE * combinacoes(dezenas, 7);
}

/** Confere o Mês da Sorte de uma aposta (independente dos acertos). */
export function obterPremioMesSorte(
  loteria: string,
  dezenas: number,
  mesAposta: number | null | undefined,
  mesSorteado: number | null | undefined,
): PremioResult {
  if (
    loteria !== 'diadesorte' ||
    mesAposta == null ||
    mesSorteado == null ||
    mesAposta !== mesSorteado
  ) {
    return { faixa: null, premiado: false };
  }
  return {
    faixa: {
      nome: 'Mês da Sorte',
      acertos: -1,
      valor: premioMesSorte(loteria, dezenas),
      fixo: true,
      tipo: 'mes',
      observacao: 'prêmio fixo Caixa · independente e cumulativo',
    },
    premiado: true,
  };
}

/**
 * Quantidade de prêmios de uma faixa em uma aposta múltipla.
 *
 * Combinações de `base` dezenas da aposta com exatamente `faixa` acertos:
 * C(acertos, faixa) × C(dezenas − acertos, base − faixa).
 * Para a aposta simples (`dezenas = base`) resulta sempre 1 ou 0.
 */
export function quantidadePremiosPorFaixa(
  dezenas: number,
  acertos: number,
  base: number,
  faixa: number,
): number {
  if (dezenas < base || faixa < 0 || faixa > base) return 0;
  return combinacoes(acertos, faixa) * combinacoes(dezenas - acertos, base - faixa);
}

/** Quantidade de prêmios do Dia de Sorte (base 7 dezenas por aposta). */
export function quantidadePremiosDiaDeSorte(
  dezenas: number,
  acertos: number,
  faixa: number,
): number {
  if (faixa < 4 || faixa > 7) return 0;
  return quantidadePremiosPorFaixa(dezenas, acertos, 7, faixa);
}

/** Quantidade de prêmios da Quina (base 5 dezenas por aposta). */
export function quantidadePremiosQuina(
  dezenas: number,
  acertos: number,
  faixa: number,
): number {
  if (faixa < 2 || faixa > 5) return 0;
  return quantidadePremiosPorFaixa(dezenas, acertos, 5, faixa);
}

export function obterPremio(loteria: string, acertos: number, trevosAcertos = 0): PremioResult {
  const faixas = TABELA[loteria] ?? [];
  const faixa = faixas.find(f => {
    if (f.tipo === 'mes') return false;
    if (f.acertos !== acertos) return false;
    if (f.trevosMin !== undefined && f.trevosMax !== undefined) {
      return trevosAcertos >= f.trevosMin && trevosAcertos <= f.trevosMax;
    }
    return true;
  });
  if (!faixa) return { faixa: null, premiado: false };
  return { faixa, premiado: true };
}