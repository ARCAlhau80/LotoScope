/** Tipos do validador estatístico (compartilhados entre servidor e cliente). */

export interface ValidadorNumero {
  numero: number;
  observado: number;
  esperado: number;
  z: number;
}

export interface ValidadorGrupo {
  id: number;
  rotulo: string;
  dezenas: number[];
  observado: number;
  esperado: number;
  z: number;
}

export interface ValidadorBadge {
  badge: number;
  rotulo: string;
  /** Média de dezenas com esse badge por sorteio. */
  poolMedio: number;
  observado: number;
  esperado: number;
  z: number;
  percentualPool: number;
  percentualAcertos: number;
}

export interface ValidadorRepeticao {
  repetidas: number;
  observado: number;
  esperado: number;
  probabilidade: number;
}

export interface ValidadorTeste {
  id: string;
  nome: string;
  chi2: number;
  df: number;
  p: number;
  pAjustado: number;
  significativoBruto: boolean;
  significativoAjustado: boolean;
  detalhe?: string;
}

export interface ValidadorLinhasVazias {
  comPeloMenosUma: number;
  percentualComPeloMenosUma: number;
  mediaObservada: number;
  mediaEsperada: number;
  probabilidadeEsperada: number;
}

export interface ValidadorEstatisticoData {
  sucesso: boolean;
  loteria: string;
  nomeJogo: string;
  totalSorteios: number;
  concursoBase: number | null;
  janelaSolicitada: number | null;
  janelaEfetiva: number;
  primeiroConcurso: number | null;
  ultimoConcurso: number | null;
  badgeJanela: number;
  badgeSorteios: number;
  numerosPorJogo: number;
  totalNumeros: number;
  totalAcertos: number;
  colunasGrade: number;
  numeros: ValidadorNumero[];
  linhas: ValidadorGrupo[];
  colunas: ValidadorGrupo[];
  badges: ValidadorBadge[];
  repeticao: {
    pares: number;
    mediaObservada: number;
    mediaEsperada: number;
    distribuicao: ValidadorRepeticao[];
  };
  linhasVazias: ValidadorLinhasVazias;
  testes: ValidadorTeste[];
  significativosBrutos: number;
  significativosAjustados: number;
  avisos: string[];
}
