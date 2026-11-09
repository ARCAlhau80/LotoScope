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

export const FECHAMENTOS: Record<string, FechamentoConfig> = {
  lotofacil: {
    id: 'lotofacil',
    nome: 'Lotofácil',
    totalNumeros: 25,
    kPadrao: 15,
    tPadrao: 11,
    kMin: 3,
    kMax: 25,
    tMax: 15,
    dezenasPorAposta: 15,
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
