export interface UltimoSorteio {
  concurso: number;
  numeros: number[];
  trevos?: number[];
  soma: number;
  pares: number;
  pares_numeros: number[];
  impares: number;
  impares_numeros: number[];
  primos: number;
  primos_numeros: number[];
  fibonacci: number;
  fibonacci_numeros: number[];
  repetidos: number;
  repetidos_numeros: number[];
  consecutivas: number;
  consecutivas_pares: string[];
  amplitude: number;
  nao_sorteados: number;
  nao_sorteados_numeros: number[];
  baixos: number;
  baixos_numeros: number[];
  altos: number;
  altos_numeros: number[];
  multiplos_3: number;
  multiplos_3_numeros: number[];
  multiplos_5: number;
  multiplos_5_numeros: number[];
}

export interface PrevisaoItem {
  numero: number;
  prob: number;
}

export interface RankingCombinacaoItem {
  id: number;
  numeros: number[];
  acertos_11: number;
  acertos_12: number;
  acertos_13: number;
  acertos_14: number;
  atraso_11: number;
  atraso_12: number;
  atraso_13: number;
  atraso_14: number;
  score: number;
}

export interface CicloInfo {
  freq_30: number;
  freq_esperada: number;
  diferenca: number;
  estado: 'aquecendo' | 'esfriando' | 'estavel';
}

export interface AtrasadoItem {
  numero: number;
  p_gap: number;
  gap: number;
  lambda_blend: number;
}

export interface TransicaoRegistro {
  concurso: number;
  quentes: number;
  mornos: number;
  frios: number;
  pct_q: number;
  pct_m: number;
  pct_f: number;
  q_set: number[];
  m_set: number[];
  f_set: number[];
}

export interface TransicaoQMF {
  medias: {
    quentes: number;
    mornos: number;
    frios: number;
    pct_q: number;
    pct_m: number;
    pct_f: number;
    total_sorteios: number;
  };
  recentes: TransicaoRegistro[];
  tendencia: {
    quentes: number;
    mornos: number;
    frios: number;
  };
}

export interface MediasHistoricas {
  soma: number;
  pares: number;
  impares: number;
  primos: number;
  fibonacci: number;
  repetidos: number;
  consecutivas: number;
  amplitude: number;
  baixos: number;
  altos: number;
  multiplos_3: number;
  multiplos_5: number;
}

export interface DashboardData {
  loteria: string;
  nome_jogo: string;
  total_numeros: number;
  numeros_por_jogo: number;
  numeros_por_aposta: number;
  ultimo_concurso: number;
  total_sorteios: number;
  ultimo_sorteio: UltimoSorteio;
  frequencia_total: Record<string, number>;
  frequencia_30: Record<string, number>;
  gaps: Record<string, number>;
  numeros_quentes: [number, number][];
  numeros_frios: [number, number][];
  numeros_mornos: [number, number][];
  previsao_posicional: Record<string, PrevisaoItem[]>;
  palpite: number[];
  previsao_combinada: number[];
  atrasados_posicionais: Record<string, AtrasadoItem[]>;
  ciclos: Record<string, CicloInfo>;
  transicao_qmf: TransicaoQMF;
  medias_historicas: MediasHistoricas;
  janela_usada: number;
  concurso_analisado: number;
  concursos_disponiveis: number[];
  timestamp: string;
  repetidos_cadeia: number[];
  tem_trevos?: boolean;
  frequencia_trevos_total?: Record<string, number>;
  frequencia_trevos_recente?: Record<string, number>;
  gaps_trevos?: Record<string, number>;
  trevos_quentes?: [number, number][];
  trevos_frios?: [number, number][];
  trevos_mornos?: [number, number][];
  ciclos_trevos?: Record<string, CicloInfo>;
  is_positional?: boolean;
  supersete?: AnaliseSuperSete;
  quarentena_posicoes?: Record<string, QuarentenaPosicaoLF>;
  comparativo_posicional?: ComparativoPosicional;
  tendencia_comparativo?: TendenciaComparativo[];
  ranking_combinacoes?: RankingCombinacaoItem[];
}

export type DirecaoComparativo = 'maior' | 'menor' | 'igual';

export interface ComparativoItem {
  posicao: number;
  atual: number;
  anterior: number;
  direcao: DirecaoComparativo;
  expectativa?: DirecaoComparativo;
  acertou?: boolean;
}

export interface ComparativoPosicional {
  concurso_atual: number;
  concurso_anterior: number;
  itens: ComparativoItem[];
  total_maiores: number;
  total_menores: number;
  total_iguais: number;
}

export interface TendenciaComparativo {
  concurso: number;
  maiores: number;
  menores: number;
  iguais: number;
}

export interface ColunaAnaliseSS {
  coluna: string;
  frequencia_total: Record<number, number>;
  frequencia_recente: Record<number, number>;
  lambda_blend: Record<number, number>;
  quentes: number[];
  mornos: number[];
  frios: number[];
  gap: Record<number, number>;
  atrasados: { digito: number; gap: number; p_gap: number }[];
  ciclo: Record<number, { freq_recente: number; freq_esperada: number; diferenca: number; estado: 'aquecendo' | 'esfriando' | 'estavel' }>;
  previsao: { digito: number; prob: number }[];
}

export interface CorrelacaoColunasSS {
  col_a: string;
  col_b: string;
  pares_frequentes: { dig_a: number; dig_b: number; freq: number }[];
  correlacao: number;
}

export interface PadraoParidadeSS {
  por_coluna: Record<string, { pares: number; impares: number; pct_par: number }>;
  distribuicao: Record<string, number>;
  mais_comum: string;
}

export interface DistribuicaoSomaSS {
  media: number;
  mediana: number;
  desvio: number;
  min: number;
  max: number;
  faixas: { faixa: string; count: number; pct: number }[];
  histograma: Record<number, number>;
}

export interface RepeticaoColunasSS {
  media_repeticoes: number;
  pct_com_repeticao: number;
  distribuicao: Record<number, number>;
  digitos_mais_repetidos: { digito: number; count: number }[];
}

export interface ApostaMultiplaSS {
  colunas: Record<string, { digitos: number[]; confianca: number[] }>;
  combinacoes_possiveis: number;
  palpite_multipla: Record<string, number[]>;
}

export interface PrevisaoExclusaoItem {
  digito: number;
  score: number;
  status: 'mantido' | 'excluido';
}

export interface PrevisaoExclusaoSS {
  colunas: Record<string, {
    estrategia: string;
    scores: PrevisaoExclusaoItem[];
    top3: number[];
  }>;
}

export interface QuarentenaInfo {
  digito: number;
  gap_atual: number;
  media: number;
  mediana: number;
  sigma: number;
  p90: number;
  status: 'quarentena' | 'normal' | 'atrasado' | 'muito_atrasado';
}

export interface QuarentenaColuna {
  coluna: string;
  digitos: QuarentenaInfo[];
  em_quarentena: number[];
  atrasados: number[];
  muito_atrasados: number[];
}

export interface QuarentenaPosicaoLF {
  posicao: string;
  numeros: QuarentenaInfo[];
  em_quarentena: number[];
  atrasados: number[];
  muito_atrasados: number[];
}

export interface AnaliseSuperSete {
  colunas: Record<string, ColunaAnaliseSS>;
  correlacoes: CorrelacaoColunasSS[];
  paridade: PadraoParidadeSS;
  soma: DistribuicaoSomaSS;
  repeticao: RepeticaoColunasSS;
  aposta_multipla: ApostaMultiplaSS;
  previsao_exclusao: PrevisaoExclusaoSS;
  quarentena: Record<string, QuarentenaColuna>;
  comparativo_posicional?: ComparativoSuperSete;
}

export interface TransicaoDigitoSS {
  digito: number;
  total: number;
  mesmo: number;
  maior: number;
  menor: number;
  pct_mesmo: number;
  pct_maior: number;
  pct_menor: number;
}

export interface ComparativoSuperSete {
  por_coluna: Record<string, {
    transicoes: TransicaoDigitoSS[];
    mesmo: number;
    maior: number;
    menor: number;
    total: number;
  }>;
  ultimo_sorteio: number[];
  penultimo_sorteio: number[];
}
