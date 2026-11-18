export interface FechamentoConfig {
  id: string;
  nome: string;
  totalNumeros: number;
  kPadrao: number;
  tPadrao: number;
  kMin: number;
  kMax: number;
  tMax: number;
  /** Quantidade de dezenas da aposta simples (base para custo). */
  dezenasPorAposta: number;
  /** Quantidade de dezenas sorteadas por concurso. */
  dezenasSorteadas: number;
  /** Preço da aposta simples. */
  precoBase: number;
  faixasPremio: number[];
  premios: Record<number, number>;
  repetidasPadrao: string;
  maxApostasMax: number;
  tooltipReceita: string;
  avisoVolume?: string;
}

const PREMIOS_LOTOFACIL: Record<number, number> = {
  11: 7,
  12: 14,
  13: 35,
  14: 2400,
  15: 2_250_000,
};

const PREMIOS_MEGASENA: Record<number, number> = {
  4: 800,
  5: 30_000,
  6: 50_000_000,
};

const PREMIOS_DIADESORTE: Record<number, number> = {
  4: 5,
  5: 25,
  6: 2_000,
  7: 1_500_000,
};

const PREMIOS_QUINA: Record<number, number> = {
  2: 5,
  3: 150,
  4: 10_000,
  5: 10_000_000,
};

/** Teto de apostas para o modo de cobertura completa por enumeração. */
export const LIMITE_COBERTURA_COMPLETA = 200_000;

export const FECHAMENTOS: Record<string, FechamentoConfig> = {  lotofacil: {
    id: 'lotofacil',
    nome: 'Lotofácil',
    totalNumeros: 25,
    kPadrao: 15,
    tPadrao: 11,
    kMin: 3,
    kMax: 25,
    tMax: 15,
    dezenasPorAposta: 15,
    dezenasSorteadas: 15,
    precoBase: 3.5,
    faixasPremio: [11, 12, 13, 14, 15],
    premios: PREMIOS_LOTOFACIL,
    repetidasPadrao: '7-10',
    maxApostasMax: 200000,
    tooltipReceita:
      'Receita recomendada: k=15, t=3, Máx. apostas=0, filtros de categoria e repetidas desligados para 100%. t=3 usa cover ótimo/consagrado; t=4–8 usa o melhor cover conhecido e t=9–12 cover gerado/verificado (milhares de apostas). t≥13 só por exportação. O solver só entra quando não existe cover para o (v,k,t). Use Backtest para comparar 14/15.',
  },
  megasena: {
    id: 'megasena',
    nome: 'Mega-Sena',
    totalNumeros: 60,
    kPadrao: 6,
    tPadrao: 4,
    kMin: 6,
    kMax: 20,
    tMax: 6,
    dezenasPorAposta: 6,
    dezenasSorteadas: 6,
    precoBase: 6.0,
    faixasPremio: [4, 5, 6],
    premios: PREMIOS_MEGASENA,
    repetidasPadrao: '2-4',
    maxApostasMax: 50000,
    tooltipReceita:
      'Receita recomendada: k=6, t=4 ou 5, Máx. apostas=0, filtros desligados para 100%. Para v=60 o fechamento gera milhares de apostas e custa dezenas/centenas de milhares de reais. Reduza o universo com fixos/excluídos (ex.: v=15–25) ou use k maior. Use Backtest para ver a distribuição de 4/5/6 acertos.',
    avisoVolume:
      'Mega-Sena com v=60 e t>=4 gera milhares de apostas. Reduza o universo com fixos/excluídos ou aumente k para diminuir o custo.',
  },
  diadesorte: {
    id: 'diadesorte',
    nome: 'Dia de Sorte',
    totalNumeros: 31,
    kPadrao: 7,
    tPadrao: 5,
    kMin: 7,
    kMax: 15,
    tMax: 7,
    dezenasPorAposta: 7,
    dezenasSorteadas: 7,
    precoBase: 2.5,
    faixasPremio: [4, 5, 6, 7],
    premios: PREMIOS_DIADESORTE,
    repetidasPadrao: '1-3',
    maxApostasMax: 20000,
    tooltipReceita:
      'Receita recomendada: k=7, t=5, Máx. apostas=200, filtros desligados para 100%. Com v=15–20 e t=5–6 o lotto design costuma reduzir bem o número de apostas. Para v=31 o fechamento cresce muito: reduza o universo com fixos/excluídos ou use o lotto design.',
    avisoVolume:
      'Dia de Sorte com v=31 e t>=5 gera milhares de apostas. Reduza o universo com fixos/excluídos ou use o lotto design.',
  },
  quina: {
    id: 'quina',
    nome: 'Quina',
    totalNumeros: 80,
    kPadrao: 5,
    tPadrao: 3,
    kMin: 5,
    kMax: 15,
    tMax: 5,
    dezenasPorAposta: 5,
    dezenasSorteadas: 5,
    precoBase: 3.0,
    faixasPremio: [2, 3, 4, 5],
    premios: PREMIOS_QUINA,
    repetidasPadrao: '0-2',
    maxApostasMax: 200000,
    tooltipReceita:
      'Receita recomendada: k=5, t=3, Máx. apostas=200, filtros desligados para 100%. Com t=4 ou 5 reduza bastante o universo usando fixos/excluídos: v=40 já exige milhares de apostas para garantir 4. O lotto design ajuda quando v ≤ 30.',
    avisoVolume:
      'Quina com v=80 e t>=4 gera milhares de apostas. Reduza o universo com fixos/excluídos ou use o lotto design.',
  },
};

export function getFechamentoConfig(loteriaId: string): FechamentoConfig {
  return FECHAMENTOS[loteriaId] ?? FECHAMENTOS.lotofacil;
}

export function loteriasComFechamento(): string[] {
  return Object.keys(FECHAMENTOS);
}

/** Garante que k/t estão dentro dos limites da loteria. */
export function normalizarKt(
  cfg: FechamentoConfig,
  k: number,
  t: number,
): { k: number; t: number } {
  const kk = Math.max(cfg.kMin, Math.min(cfg.kMax, Math.trunc(k) || cfg.kPadrao));
  const tt = Math.max(1, Math.min(Math.min(cfg.tMax, kk), Math.trunc(t) || cfg.tPadrao));
  return { k: kk, t: tt };
}

/** Texto de referência de prêmios para a UI. */
export function textoPremios(cfg: FechamentoConfig): string {
  return cfg.faixasPremio
    .map(f => `${f}=R$ ${(cfg.premios[f] ?? 0).toLocaleString('pt-BR')}`)
    .join(' · ');
}
