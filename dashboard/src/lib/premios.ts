export interface FaixaPremio {
  nome: string;
  acertos: number;
  trevosMin?: number;
  trevosMax?: number;
  valor: number;
  fixo: boolean;
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
    { nome: "Quina (5)", acertos: 5, valor: 1_500_000, fixo: false, observacao: "≈ rateio" },
    { nome: "Quadra (4)", acertos: 4, valor: 8_000, fixo: false, observacao: "≈ rateio" },
    { nome: "Terno (3)", acertos: 3, valor: 200, fixo: false, observacao: "≈ rateio" },
    { nome: "Duque (2)", acertos: 2, valor: 4, fixo: false, observacao: "≈ rateio" },
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
    { nome: "6 acertos", acertos: 6, valor: 1_500, fixo: false, observacao: "≈ rateio" },
    { nome: "5 acertos", acertos: 5, valor: 25, fixo: true, observacao: "valor fixo Caixa" },
    { nome: "4 acertos", acertos: 4, valor: 5, fixo: true, observacao: "valor fixo Caixa" },
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

export function obterPremio(loteria: string, acertos: number, trevosAcertos = 0): PremioResult {
  const faixas = TABELA[loteria] ?? [];
  const faixa = faixas.find(f => {
    if (f.acertos !== acertos) return false;
    if (f.trevosMin !== undefined && f.trevosMax !== undefined) {
      return trevosAcertos >= f.trevosMin && trevosAcertos <= f.trevosMax;
    }
    return true;
  });
  if (!faixa) return { faixa: null, premiado: false };
  return { faixa, premiado: true };
}