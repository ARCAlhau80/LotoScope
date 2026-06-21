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
  timestamp: string;
  repetidos_cadeia: number[];
}
