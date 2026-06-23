export interface FaixaConfig {
  nome: string;
  inicio: number;
  fim: number;
}

export interface EstrategiaConfig {
  nome: string;
  descricao: string;
  peso_quentes: number;
  peso_frios: number;
  peso_aleatorio: number;
}

export interface LotteryConfig {
  id: string;
  nome_jogo: string;
  total_numeros: number;
  numeros_por_jogo: number;
  numero_minimo: number;
  numero_maximo: number;
  colunas_resultado: string[];
  tabela_resultados: string;
  tabela_combinacoes: string;
  db_name: string;
  faixas: Record<string, FaixaConfig>;
  estrategias: Record<string, EstrategiaConfig>;
  primos: number[];
  fibonacci: number[];
  params_estatisticos: Record<string, number>;
  trevos_cols?: string[];
  trevos_total?: number;
  trevos_min?: number;
  trevos_max?: number;
  qmf_scale: number;
}

export const LOTERIAS: Record<string, LotteryConfig> = {
  lotofacil: {
    id: "lotofacil",
    nome_jogo: "Lotofácil",
    total_numeros: 25,
    numeros_por_jogo: 15,
    numero_minimo: 1,
    numero_maximo: 25,
    colunas_resultado: Array.from({ length: 15 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_INT",
    tabela_combinacoes: "COMBINACOES_LOTOFACIL",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (1-12)", inicio: 1, fim: 12 },
      alta: { nome: "Alta (13-25)", inicio: 13, fim: 25 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      quentes: { nome: "Numeros Quentes", descricao: "Prioriza mais frequentes", peso_quentes: 0.7, peso_frios: 0.1, peso_aleatorio: 0.2 },
      frios: { nome: "Numeros Frios", descricao: "Prioriza menos frequentes", peso_quentes: 0.1, peso_frios: 0.7, peso_aleatorio: 0.2 },
      invertida: { nome: "Invertida v3.0", descricao: "Exclui QUENTES (mean reversion)", peso_quentes: 0.3, peso_frios: 0.3, peso_aleatorio: 0.4 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23],
    fibonacci: [1, 2, 3, 5, 8, 13, 21],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 120, soma_maxima: 210, soma_media_esperada: 195, pares_mais_comum: 7, impares_mais_comum: 8 },
    qmf_scale: 9,
  },
  megasena: {
    id: "megasena",
    nome_jogo: "Mega-Sena",
    total_numeros: 60,
    numeros_por_jogo: 6,
    numero_minimo: 1,
    numero_maximo: 60,
    colunas_resultado: Array.from({ length: 6 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_MegaSenaFechado",
    tabela_combinacoes: "COMBIN_MEGASENA",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (1-20)", inicio: 1, fim: 20 },
      media: { nome: "Média (21-40)", inicio: 21, fim: 40 },
      alta: { nome: "Alta (41-60)", inicio: 41, fim: 60 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme por faixas", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      quentes: { nome: "Numeros Quentes", descricao: "Prioriza numeros mais frequentes", peso_quentes: 0.7, peso_frios: 0.1, peso_aleatorio: 0.2 },
      frios: { nome: "Numeros Frios", descricao: "Prioriza numeros menos frequentes", peso_quentes: 0.1, peso_frios: 0.7, peso_aleatorio: 0.2 },
      contrarian: { nome: "Contraria", descricao: "Mix de quentes e frios", peso_quentes: 0.3, peso_frios: 0.3, peso_aleatorio: 0.4 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59],
    fibonacci: [1, 2, 3, 5, 8, 13, 21, 34, 55],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 21, soma_maxima: 345, soma_media_esperada: 183, pares_mais_comum: 3, impares_mais_comum: 3 },
    qmf_scale: 10,
  },
  quina: {
    id: "quina",
    nome_jogo: "Quina",
    total_numeros: 80,
    numeros_por_jogo: 5,
    numero_minimo: 1,
    numero_maximo: 80,
    colunas_resultado: Array.from({ length: 5 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_Quina",
    tabela_combinacoes: "COMBIN_QUINA",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (1-27)", inicio: 1, fim: 27 },
      media: { nome: "Média (28-54)", inicio: 28, fim: 54 },
      alta: { nome: "Alta (55-80)", inicio: 55, fim: 80 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme por faixas", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      quentes: { nome: "Numeros Quentes", descricao: "Prioriza numeros mais frequentes", peso_quentes: 0.7, peso_frios: 0.1, peso_aleatorio: 0.2 },
      frios: { nome: "Numeros Frios", descricao: "Prioriza numeros menos frequentes", peso_quentes: 0.1, peso_frios: 0.7, peso_aleatorio: 0.2 },
      contrarian: { nome: "Contraria", descricao: "Mix de quentes e frios", peso_quentes: 0.3, peso_frios: 0.3, peso_aleatorio: 0.4 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79],
    fibonacci: [1, 2, 3, 5, 8, 13, 21, 34, 55],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 15, soma_maxima: 390, soma_media_esperada: 202, pares_mais_comum: 2, impares_mais_comum: 3 },
    qmf_scale: 8,
  },
  duplasena: {
    id: "duplasena",
    nome_jogo: "Dupla Sena",
    total_numeros: 50,
    numeros_por_jogo: 6,
    numero_minimo: 1,
    numero_maximo: 50,
    colunas_resultado: Array.from({ length: 6 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_DuplaSena",
    tabela_combinacoes: "COMBIN_DUPLASENA",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (1-17)", inicio: 1, fim: 17 },
      media: { nome: "Média (18-34)", inicio: 18, fim: 34 },
      alta: { nome: "Alta (35-50)", inicio: 35, fim: 50 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme por faixas", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      quentes: { nome: "Numeros Quentes", descricao: "Prioriza numeros mais frequentes", peso_quentes: 0.7, peso_frios: 0.1, peso_aleatorio: 0.2 },
      frios: { nome: "Numeros Frios", descricao: "Prioriza numeros menos frequentes", peso_quentes: 0.1, peso_frios: 0.7, peso_aleatorio: 0.2 },
      contrarian: { nome: "Contraria", descricao: "Mix de quentes e frios", peso_quentes: 0.3, peso_frios: 0.3, peso_aleatorio: 0.4 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
    fibonacci: [1, 2, 3, 5, 8, 13, 21, 34],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 21, soma_maxima: 285, soma_media_esperada: 153, pares_mais_comum: 3, impares_mais_comum: 3 },
    qmf_scale: 9,
  },
  lotomania: {
    id: "lotomania",
    nome_jogo: "Lotomania",
    total_numeros: 100,
    numeros_por_jogo: 20,
    numero_minimo: 0,
    numero_maximo: 99,
    colunas_resultado: Array.from({ length: 20 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_Lotomania",
    tabela_combinacoes: "COMBIN_LOTOMANIA",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (0-33)", inicio: 0, fim: 33 },
      media: { nome: "Média (34-66)", inicio: 34, fim: 66 },
      alta: { nome: "Alta (67-99)", inicio: 67, fim: 99 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      concentrada: { nome: "Concentrada", descricao: "Prioriza faixa media", peso_quentes: 0.3, peso_frios: 0.4, peso_aleatorio: 0.3 },
      dispersa: { nome: "Dispersa", descricao: "Prioriza extremos", peso_quentes: 0.5, peso_frios: 0.1, peso_aleatorio: 0.4 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97],
    fibonacci: [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 0, soma_maxima: 1990, soma_media_esperada: 990, pares_mais_comum: 10, impares_mais_comum: 10 },
    qmf_scale: 20,
  },
  diadesorte: {
    id: "diadesorte",
    nome_jogo: "Dia de Sorte",
    total_numeros: 31,
    numeros_por_jogo: 7,
    numero_minimo: 1,
    numero_maximo: 31,
    colunas_resultado: Array.from({ length: 7 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_DiaDeSorte",
    tabela_combinacoes: "COMBIN_DIADESORTE",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (1-10)", inicio: 1, fim: 10 },
      media: { nome: "Média (11-20)", inicio: 11, fim: 20 },
      alta: { nome: "Alta (21-31)", inicio: 21, fim: 31 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      concentrada: { nome: "Concentrada", descricao: "Foco em baixos", peso_quentes: 0.6, peso_frios: 0.1, peso_aleatorio: 0.3 },
      dispersa: { nome: "Dispersa", descricao: "Foco em altos", peso_quentes: 0.2, peso_frios: 0.6, peso_aleatorio: 0.2 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31],
    fibonacci: [1, 2, 3, 5, 8, 13, 21],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 28, soma_maxima: 196, soma_media_esperada: 112, pares_mais_comum: 3, impares_mais_comum: 4 },
    qmf_scale: 7,
  },
  timemania: {
    id: "timemania",
    nome_jogo: "Timemania",
    total_numeros: 80,
    numeros_por_jogo: 7,
    numero_minimo: 1,
    numero_maximo: 80,
    colunas_resultado: Array.from({ length: 7 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_Timemania",
    tabela_combinacoes: "COMBIN_TIMEMANIA",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (1-27)", inicio: 1, fim: 27 },
      media: { nome: "Média (28-54)", inicio: 28, fim: 54 },
      alta: { nome: "Alta (55-80)", inicio: 55, fim: 80 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      torcida: { nome: "Torcida", descricao: "Foco em baixos", peso_quentes: 0.6, peso_frios: 0.1, peso_aleatorio: 0.3 },
      visitante: { nome: "Visitante", descricao: "Foco em altos", peso_quentes: 0.2, peso_frios: 0.6, peso_aleatorio: 0.2 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79],
    fibonacci: [1, 2, 3, 5, 8, 13, 21, 34, 55],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 28, soma_maxima: 532, soma_media_esperada: 280, pares_mais_comum: 3, impares_mais_comum: 4 },
    qmf_scale: 10,
  },
  supersete: {
    id: "supersete",
    nome_jogo: "Super Sete",
    total_numeros: 10,
    numeros_por_jogo: 7,
    numero_minimo: 0,
    numero_maximo: 9,
    colunas_resultado: Array.from({ length: 7 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_SuperSete",
    tabela_combinacoes: "COMBIN_SUPERSETE",
    db_name: "LOTOFACIL",
    faixas: {
      baixa: { nome: "Baixa (0-3)", inicio: 0, fim: 3 },
      media: { nome: "Média (4-6)", inicio: 4, fim: 6 },
      alta: { nome: "Alta (7-9)", inicio: 7, fim: 9 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      baixos: { nome: "Baixos", descricao: "Prioriza digitos baixos", peso_quentes: 0.6, peso_frios: 0.1, peso_aleatorio: 0.3 },
      altos: { nome: "Altos", descricao: "Prioriza digitos altos", peso_quentes: 0.2, peso_frios: 0.6, peso_aleatorio: 0.2 },
    },
    primos: [2, 3, 5, 7],
    fibonacci: [0, 1, 2, 3, 5, 8],
    params_estatisticos: { consecutivos_max_comum: 0, soma_minima: 0, soma_maxima: 63, soma_media_esperada: 31, pares_mais_comum: 3, impares_mais_comum: 4 },
    qmf_scale: 3,
  },
  maismilionaria: {
    id: "maismilionaria",
    nome_jogo: "Mais Milionária",
    total_numeros: 50,
    numeros_por_jogo: 6,
    numero_minimo: 1,
    numero_maximo: 50,
    colunas_resultado: Array.from({ length: 6 }, (_, i) => `N${i + 1}`),
    tabela_resultados: "Resultados_MaisMilionaria",
    tabela_combinacoes: "COMBIN_MAISMILIONARIA",
    db_name: "LOTOFACIL",
    trevos_cols: ['T1', 'T2'],
    trevos_total: 6,
    trevos_min: 1,
    trevos_max: 6,
    faixas: {
      baixa: { nome: "Baixa (1-17)", inicio: 1, fim: 17 },
      media: { nome: "Média (18-34)", inicio: 18, fim: 34 },
      alta: { nome: "Alta (35-50)", inicio: 35, fim: 50 },
    },
    estrategias: {
      equilibrada: { nome: "Equilibrada", descricao: "Distribuicao uniforme", peso_quentes: 0.4, peso_frios: 0.2, peso_aleatorio: 0.4 },
      baixos: { nome: "Baixos", descricao: "Foco em baixos", peso_quentes: 0.6, peso_frios: 0.1, peso_aleatorio: 0.3 },
      altos: { nome: "Altos", descricao: "Foco em altos", peso_quentes: 0.2, peso_frios: 0.6, peso_aleatorio: 0.2 },
    },
    primos: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
    fibonacci: [1, 2, 3, 5, 8, 13, 21, 34],
    params_estatisticos: { consecutivos_max_comum: 2, soma_minima: 21, soma_maxima: 279, soma_media_esperada: 153, pares_mais_comum: 3, impares_mais_comum: 3 },
    qmf_scale: 9,
  },
};

export function getLotteryConfig(id: string): LotteryConfig {
  const cfg = LOTERIAS[id];
  if (!cfg) throw new Error(`Loteria desconhecida: ${id}`);
  return cfg;
}

export const LOTTERY_IDS = Object.keys(LOTERIAS);
