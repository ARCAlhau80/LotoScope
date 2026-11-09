/**
 * FECHAMENTO COMBINATÓRIO (WHEEL / COVERING DESIGN) — LOTOFÁCIL
 * Port TypeScript da lógica em lotofacil_lite/sistemas/fechamento_combinatorio.py
 *
 * C(v, k, t): escolhe apostas de k dezenas sobre um universo de v dezenas
 * de modo que TODA combinação de t dezenas do universo esteja contida em
 * pelo menos uma aposta. Garante t acertos se as t dezenas sorteadas
 * estiverem entre as v escolhidas.
 */

export interface GerarApostasCandidatasOptions {
  universo: number[];
  k: number;
  limite?: number;
  seed?: number;
  /** Só aceita blocos que satisfazem este predicado (ex.: filtros de categoria). */
  aceitarBloco?: (aposta: number[]) => boolean;
}

export interface ConstruirFechamentoOptions {
  universo: number[];
  k: number;
  t: number;
  maxApostas?: number;
  seed?: number;
  candidatosPool?: number;
  amostraPorPasso?: number;
  /** Só aceita blocos que satisfazem este predicado (ex.: filtros de categoria). */
  aceitarBloco?: (aposta: number[]) => boolean;
  /** Tempo máximo em ms; 0/undefined = sem limite. */
  limiteTempoMs?: number;
}

export interface BuscaLocalOptions {
  apostas: number[][];
  universo: number[];
  k: number;
  t: number;
  maxIteracoes?: number;
  seed?: number;
  candidatosPool?: number;
  /** Só aceita blocos candidatos que satisfazem este predicado. */
  aceitarBloco?: (aposta: number[]) => boolean;
  /** Teto de pares (aposta, candidato) avaliados; mantém a busca em segundos. */
  orcamentoAvaliacoes?: number;
}

/** Teto de candidatos distintos no pool do guloso. */
export const LIMITE_POOL_CANDIDATOS = 5000;

/** Teto de candidatos quando maxApostas = 0 (sem limite de apostas). */
export const LIMITE_POOL_CANDIDATOS_ILIMITADO = 20000;

/**
 * `maxApostas` <= 0 (ou não finito) significa "sem limite": o fechamento roda
 * até cobrir todos os t-subconjuntos ou esgotar o pool de candidatas.
 */
export function maxApostasIlimitado(maxApostas: number | null | undefined): boolean {
  if (maxApostas === null || maxApostas === undefined || Number.isNaN(maxApostas)) return false;
  return maxApostas <= 0 || !Number.isFinite(maxApostas);
}

/** Teto de avaliações da busca local (aposta × candidato). */
export const ORCAMENTO_BUSCA_LOCAL = 100_000;

/**
 * Prêmios de referência da Lotofácil por faixa de acertos (R$).
 * Valores fixos/estimados: use apenas para comparação relativa de estratégias.
 */
export const PREMIOS_LOTOFACIL: Record<number, number> = {
  11: 7,
  12: 14,
  13: 35,
  14: 2400,
  15: 2_250_000,
};

export interface CoverConhecido {
  v: number;
  k: number;
  t: number;
  blocos: number[][];
  fonte: string;
  /** Melhor limite inferior conhecido para C(v,k,t). */
  limiteInferior: number;
  /** true quando a cobertura foi verificada exaustivamente offline. */
  verificado?: boolean;
}

/**
 * Coberturas ótimas conhecidas do La Jolla Covering Repository (JCD article).
 * Pontos são 1..v; o caller mapeia para o universo real.
 */
export const COVERS_CONHECIDOS: CoverConhecido[] = [
  {
    v: 25, k: 15, t: 3,
    fonte: 'La Jolla Covering Repository / JCD article (C(25,15,3)=10)',
    limiteInferior: 9,
    blocos: [
      [1,2,3,6,7,8,11,12,13,16,17,18,21,22,23],
      [1,2,4,6,7,9,11,12,14,16,17,19,21,22,24],
      [1,2,5,6,7,10,11,12,15,16,17,20,21,22,25],
      [1,3,4,6,8,9,11,13,14,16,18,19,21,23,24],
      [1,3,5,6,8,10,11,13,15,16,18,20,21,23,25],
      [1,4,5,6,9,10,11,14,15,16,19,20,21,24,25],
      [2,3,4,7,8,9,12,13,14,17,18,19,22,23,24],
      [2,3,5,7,8,10,12,13,15,17,18,20,22,23,25],
      [2,4,5,7,9,10,12,14,15,17,19,20,22,24,25],
      [3,4,5,8,9,10,13,14,15,18,19,20,23,24,25],
    ],
  },
  {
    v: 24, k: 14, t: 3,
    fonte: 'La Jolla Covering Repository / JCD article (C(24,14,3)=11)',
    limiteInferior: 9,
    blocos: [
      [1,2,3,4,5,6,7,13,14,15,16,17,18,19],
      [1,2,3,7,8,9,11,13,14,15,19,20,21,23],
      [1,2,4,5,8,10,11,13,14,16,17,20,22,23],
      [1,2,8,9,10,11,12,13,14,20,21,22,23,24],
      [1,3,6,7,9,10,11,13,15,18,19,21,22,23],
      [1,3,6,8,9,11,12,13,15,18,20,21,23,24],
      [1,4,5,7,9,10,12,13,16,17,19,21,22,24],
      [2,3,6,7,8,10,12,14,15,18,19,20,22,24],
      [2,4,5,6,9,11,12,14,16,17,18,21,23,24],
      [3,4,5,6,8,9,10,15,16,17,18,20,21,22],
      [3,4,5,7,8,11,12,15,16,17,19,20,23,24],
    ],
  },
  {
    v: 23, k: 13, t: 3,
    fonte: 'La Jolla Covering Repository / JCD article (C(23,13,3)=11)',
    limiteInferior: 11,
    blocos: [
      [1,2,3,5,8,11,12,13,14,16,19,22,23],
      [1,2,4,7,8,10,12,13,15,18,19,21,23],
      [1,2,5,6,7,9,12,13,16,17,18,20,23],
      [1,3,4,5,9,10,12,14,15,16,20,21,23],
      [1,3,6,7,10,11,12,14,17,18,21,22,23],
      [1,4,6,8,9,11,12,15,17,19,20,22,23],
      [2,3,4,7,9,11,13,14,15,18,20,22,23],
      [2,3,6,8,9,10,13,14,17,19,20,21,23],
      [2,4,5,6,10,11,13,15,16,17,21,22,23],
      [3,4,5,6,7,8,14,15,16,17,18,19,23],
      [5,7,8,9,10,11,16,18,19,20,21,22,23],
    ],
  },
  {
    v: 22, k: 12, t: 3,
    fonte: 'La Jolla Covering Repository / JCD article (C(22,12,3)=11)',
    limiteInferior: 11,
    blocos: [
      [1,2,3,5,8,11,12,13,14,16,19,22],
      [1,2,4,7,8,10,12,13,15,18,19,21],
      [1,2,5,6,7,9,12,13,16,17,18,20],
      [1,3,4,5,9,10,12,14,15,16,20,21],
      [1,3,6,7,10,11,12,14,17,18,21,22],
      [1,4,6,8,9,11,12,15,17,19,20,22],
      [2,3,4,7,9,11,13,14,15,18,20,22],
      [2,3,6,8,9,10,13,14,17,19,20,21],
      [2,4,5,6,10,11,13,15,16,17,21,22],
      [3,4,5,6,7,8,14,15,16,17,18,19],
      [5,7,8,9,10,11,16,18,19,20,21,22],
    ],
  },
  {
    v: 21, k: 11, t: 3,
    fonte: 'La Jolla Covering Repository / JCD article (C(21,11,3)=14)',
    limiteInferior: 13,
    blocos: [
      [1,2,3,4,11,15,16,17,18,20,21],
      [1,2,3,5,6,7,9,11,12,14,17],
      [1,2,3,8,10,11,13,14,17,18,19],
      [1,3,4,6,7,9,10,15,16,17,18],
      [1,3,5,7,10,12,13,14,16,20,21],
      [1,4,5,8,12,13,14,15,16,18,19],
      [1,6,7,8,9,13,14,18,19,20,21],
      [2,4,5,7,10,11,12,13,15,17,21],
      [2,4,6,8,9,11,14,15,17,19,21],
      [2,5,7,8,11,12,16,17,18,19,20],
      [2,6,9,10,11,13,14,16,17,18,20],
      [3,4,5,6,9,12,13,15,17,19,20],
      [3,4,7,8,10,13,14,15,17,19,20],
      [3,5,6,8,9,10,12,16,18,19,21],
    ],
  },
  {
    v: 20, k: 10, t: 3,
    fonte: 'La Jolla Covering Repository / JCD article (C(20,10,3)=15)',
    limiteInferior: 14,
    blocos: [
      [1,2,3,4,5,6,7,8,9,10],
      [1,2,3,4,5,6,7,8,19,20],
      [1,2,11,12,13,14,15,16,17,18],
      [1,3,4,5,6,15,16,17,18,19],
      [1,3,4,9,10,11,12,17,18,20],
      [1,3,4,9,10,13,14,15,16,19],
      [1,5,6,7,8,11,12,17,18,19],
      [1,5,6,7,8,13,14,15,16,20],
      [1,7,8,9,10,11,12,13,14,19],
      [2,3,4,7,8,11,12,15,16,20],
      [2,3,4,7,8,13,14,17,18,19],
      [2,5,6,9,10,11,12,15,16,19],
      [2,5,6,9,10,13,14,17,18,20],
      [3,4,5,6,11,12,13,14,19,20],
      [7,8,9,10,15,16,17,18,19,20],
    ],
  },
  {
    v: 19, k: 9, t: 3,
    fonte: 'La Jolla Covering Repository / Rade Belic (C(19,9,3)=17)',
    limiteInferior: 16,
    blocos: [
      [1,2,3,4,5,6,11,12,19],
      [1,2,3,4,11,12,13,18,19],
      [1,2,4,5,6,11,12,13,18],
      [1,2,4,7,8,12,13,14,16],
      [1,2,4,9,10,12,13,15,17],
      [1,3,4,6,7,10,15,16,18],
      [1,3,4,6,8,9,14,17,18],
      [1,4,5,7,9,11,16,17,19],
      [1,4,5,8,10,11,14,15,19],
      [2,3,5,6,7,9,12,14,15],
      [2,3,5,6,8,10,12,16,17],
      [2,7,10,11,12,14,17,18,19],
      [2,8,9,11,12,15,16,18,19],
      [3,5,7,8,9,10,13,17,18],
      [3,6,7,8,11,13,15,17,19],
      [3,6,9,10,11,13,14,16,19],
      [5,6,13,14,15,16,17,18,19],
    ],
  },
];

export function buscarCoverConhecido(v: number, k: number, t: number): CoverConhecido | undefined {
  return COVERS_CONHECIDOS.find(c => c.v === v && c.k === k && c.t === t);
}

/** Mapeia os pontos 1..v de um cover conhecido para o universo real (ordenado). */
export function mapearCoverConhecido(cover: CoverConhecido, universo: number[]): number[][] {
  const u = [...new Set(universo)].sort((a, b) => a - b);
  if (u.length !== cover.v) throw new Error(`Universo deve ter ${cover.v} dezenas para o cover conhecido`);
  return cover.blocos.map(bloco => bloco.map(p => u[p - 1]).sort((a, b) => a - b));
}

export interface VerificarCoberturaResult {
  coberta: boolean;
  tSubsetsTotal: number;
  tSubsetsCobertos: number;
  garantiaPercentual: number;
  apostasValidas: number;
  apostasInvalidas: number;
  totalApostas: number;
  custoEstimado: number;
}

export interface RelatorioCustoResult {
  totalApostas: number;
  k: number;
  precoPorJogo: number;
  custoTotal: number;
  reducaoVsUniverso25_15: number;
}

/** Preço de uma aposta simples de 15 dezenas na Lotofácil. */
export const PRECO_APOSTA_15 = 3.5;

/**
 * Custo de UMA aposta de k dezenas.
 *
 * Uma aposta de k dezenas equivale a C(k, 15) apostas simples:
 * k=15 → 3,50 | 16 → 56,00 | 17 → 476,00 | 18 → 2.856,00
 * k=19 → 13.566,00 | 20 → 54.264,00
 *
 * Para k < 15 (fechamento exploratório, que não é uma aposta jogável)
 * assume-se o preço de uma aposta simples como piso.
 */
export function custoPorAposta(
  k: number,
  dezenasBase: number = 15,
  precoBase: number = PRECO_APOSTA_15,
): number {
  if (!Number.isInteger(k) || k < dezenasBase) return precoBase;
  return Math.round(nCombinacoes(k, dezenasBase) * precoBase * 100) / 100;
}

/** LCG simples para geração determinística com seed. */
class LCG {
  private s: number;
  constructor(seed: number) {
    this.s = (seed >>> 0) || 1;
  }
  next(): number {
    this.s = (this.s * 16807) % 2147483647;
    return (this.s - 1) / 2147483646;
  }
}

const MAX_N_TABELA = 30;
const tabelaCombinacoes: number[][] = (() => {
  const t: number[][] = [];
  for (let n = 0; n <= MAX_N_TABELA; n++) {
    const linha = new Array<number>(n + 1).fill(0);
    linha[0] = 1;
    for (let k = 1; k <= n; k++) {
      linha[k] = k === n ? 1 : t[n - 1][k - 1] + (t[n - 1][k] ?? 0);
    }
    t[n] = linha;
  }
  return t;
})();
const combinacoesCache = new Map<string, number>();

/** C(n, k). Para n <= 30 usa tabela pré-computada; acima disso, fórmula com cache. */
export function nCombinacoes(n: number, k: number): number {
  if (n < 0 || k < 0 || k > n) return 0;
  if (k === 0 || k === n) return 1;
  if (n <= MAX_N_TABELA) return tabelaCombinacoes[n][k];
  k = Math.min(k, n - k);
  const key = `${n},${k}`;
  if (combinacoesCache.has(key)) return combinacoesCache.get(key)!;
  let resultado = 1;
  for (let i = 0; i < k; i++) {
    resultado = (resultado * (n - i)) / (i + 1);
  }
  const res = Math.round(resultado);
  combinacoesCache.set(key, res);
  return res;
}

/**
 * Limite inferior de Schönheim para o número de apostas de um fechamento
 * C(v, k, t). Não é necessariamente alcançável, mas mostra a folga do heurístico.
 */
export function limiteInferiorCobertura(v: number, k: number, t: number): number {
  if (t <= 0 || k <= 0 || v <= 0 || k > v) return 0;
  if (t === 1) return Math.ceil(v / k);
  return Math.ceil((v / k) * limiteInferiorCobertura(v - 1, k - 1, t - 1));
}

/** Rank lexicográfico de uma combinação JÁ ordenada (evita o sort por chamada). */
function combRankLexSorted(c: number[], n: number): number {
  const k = c.length;
  const total = nCombinacoes(n, k);
  let s = 0;
  for (let i = 0; i < k; i++) {
    s += nCombinacoes(n - c[i], k - i);
  }
  return total - 1 - s;
}

/** Rank lexicográfico contíguo (0 .. C(n,k)-1) de uma combinação ordenada de 1..n. O(k). */
export function combRankLex(comb: number[], n: number): number {
  return combRankLexSorted([...comb].sort((a, b) => a - b), n);
}

/** Índices (rank lex) de todos os t-subconjuntos cobertos por uma aposta de k dezenas. */
export function indicesAlvosCobertosPorAposta(aposta: number[], universo: number[], t: number): number[] {
  const u = [...new Set(universo)].sort((a, b) => a - b);
  const v = u.length;
  const pos = new Map<number, number>();
  u.forEach((n, i) => pos.set(n, i + 1));
  // O rank lexicografico opera sobre posicoes 1..v no universo, nao sobre os
  // rotulos das dezenas (que podem ser 3..25, por exemplo).
  const a = [...aposta]
    .sort((x, y) => x - y)
    .map((n) => pos.get(n))
    .filter((p): p is number => p !== undefined);
  const idxs: number[] = [];
  const atual: number[] = [];
  function combinar(inicio: number, resto: number): void {
    if (resto === 0) {
      idxs.push(combRankLexSorted(atual, v));
      return;
    }
    for (let i = inicio; i <= a.length - resto; i++) {
      atual.push(a[i]);
      combinar(i + 1, resto - 1);
      atual.pop();
    }
  }
  combinar(0, t);
  return idxs;
}

/** Lista apostas candidatas de k dezenas. Com limite, amostra determinística. */
export function gerarApostasCandidatas(opts: GerarApostasCandidatasOptions): number[][] {
  const { universo, k, limite, seed, aceitarBloco } = opts;
  const u = [...new Set(universo)].sort((a, b) => a - b);
  const v = u.length;
  const total = nCombinacoes(v, k);
  const aceita = (a: number[]) => !aceitarBloco || aceitarBloco(a);

  if (!limite || limite >= total) {
    const out: number[][] = [];
    function combinar(inicio: number, resto: number, atual: number[]): void {
      if (resto === 0) {
        const a = [...atual];
        if (aceita(a) && (limite === undefined || out.length < limite)) out.push(a);
        return;
      }
      for (let i = inicio; i <= u.length - resto; i++) {
        combinar(i + 1, resto - 1, [...atual, u[i]]);
      }
    }
    combinar(0, k, []);
    return out;
  }

  const rng = new LCG(seed ?? (u.join(",") + k).length);
  const visto = new Set<string>();
  const out: number[][] = [];
  // Com filtro, a taxa de aceitação pode ser baixa; limita as tentativas para
  // não travar em filtros impossíveis (ex.: categoria com faixa vazia).
  const maxTentativas = aceitarBloco ? Math.max(limite * 200, 20_000) : Number.POSITIVE_INFINITY;
  let tentativas = 0;
  while (out.length < limite && tentativas < maxTentativas) {
    tentativas++;
    const copia = [...u];
    const cand: number[] = [];
    for (let i = 0; i < k; i++) {
      const j = Math.floor(rng.next() * copia.length);
      cand.push(copia[j]);
      copia.splice(j, 1);
    }
    cand.sort((a, b) => a - b);
    if (!aceita(cand)) continue;
    const chave = cand.join(",");
    if (!visto.has(chave)) {
      visto.add(chave);
      out.push(cand);
    }
  }
  return out;
}

/** Constrói fechamento C(v,k,t) por set cover guloso amostrado. */
export function construirFechamentoGulosoAmostrado(opts: ConstruirFechamentoOptions): number[][] {
  const {
    universo,
    k,
    t,
    maxApostas = 2000,
    seed = 42,
    candidatosPool = 3000,
    amostraPorPasso = t <= 3 ? 2000 : t === 4 ? 500 : t <= 8 ? 60 : 25,
    aceitarBloco,
    limiteTempoMs = 0,
  } = opts;
  const u = [...new Set(universo)].sort((a, b) => a - b);
  const v = u.length;
  if (k < t || t < 1 || k > v) throw new Error("Deve valer 1 <= t <= k <= v");

  const inicio = Date.now();
  const totalT = nCombinacoes(v, t);
  const coberta = new Uint8Array(totalT);
  let cobertos = 0;

  const rng = new LCG(seed);
  const semLimite = maxApostasIlimitado(maxApostas);
  const limiteApostas = semLimite ? Number.POSITIVE_INFINITY : maxApostas;

  // O pool precisa ter ao menos maxApostas candidatos distintos; caso contrário
  // o guloso esgotaria os candidatos e devolveria menos apostas que o pedido.
  // Com maxApostas = 0 (sem limite), usamos um teto maior para que a cobertura
  // não pare artificialmente em 5000 apostas.
  const tetoPool = semLimite ? LIMITE_POOL_CANDIDATOS_ILIMITADO : LIMITE_POOL_CANDIDATOS;
  // Com filtro, o pool precisa ser maior: parte dos candidatos é descartada.
  const poolDesejado = aceitarBloco ? Math.max(candidatosPool, 1500) : candidatosPool;
  const limitePool = aceitarBloco
    ? Math.min(LIMITE_POOL_CANDIDATOS, Math.max(poolDesejado, 5000))
    : Math.min(tetoPool, Math.max(poolDesejado, semLimite ? tetoPool : Math.min(maxApostas, tetoPool)));
  const pool = gerarApostasCandidatas({ universo: u, k, limite: limitePool, seed, aceitarBloco });
  if (pool.length === 0) return [];
  rng.next(); // consumir um pouco para embaralhar diferente
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(rng.next() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }

  const indicesCache: (Int32Array | null)[] = Array(pool.length).fill(null);
  const indicesDe = (ci: number): Int32Array => {
    let idx = indicesCache[ci];
    if (idx === null) {
      idx = Int32Array.from(indicesAlvosCobertosPorAposta(pool[ci], u, t));
      indicesCache[ci] = idx;
    }
    return idx;
  };

  const apostas: number[][] = [];
  const restantes = pool.map((_, i) => i);

  while (cobertos < totalT && restantes.length > 0 && apostas.length < limiteApostas) {
    if (limiteTempoMs > 0 && Date.now() - inicio > limiteTempoMs) break;
    const amostraSize = Math.min(amostraPorPasso, restantes.length);
    const amostra: number[] = [];
    const temp = [...restantes];
    for (let i = 0; i < amostraSize; i++) {
      const j = Math.floor(rng.next() * temp.length);
      amostra.push(temp[j]);
      temp.splice(j, 1);
    }

    let melhorIdx = -1;
    let melhorGanho = -1;
    for (const ci of amostra) {
      let ganho = 0;
      for (const idx of indicesDe(ci)) {
        if (!coberta[idx]) ganho++;
      }
      if (ganho > melhorGanho) {
        melhorGanho = ganho;
        melhorIdx = ci;
      }
    }

    if (melhorIdx === -1 || melhorGanho <= 0) {
      if (restantes.length > amostraPorPasso) continue;
      break;
    }

    const ci = melhorIdx;
    apostas.push([...pool[ci]]);
    for (const idx of indicesDe(ci)) {
      if (!coberta[idx]) {
        coberta[idx] = 1;
        cobertos++;
      }
    }
    restantes.splice(restantes.indexOf(ci), 1);
  }

  return apostas;
}

/**
 * Remove apostas que não cobrem nenhum t-subconjunto exclusivo.
 * A cobertura é preservada exatamente; o resultado é um subconjunto mínimo
 * (local) do fechamento original, não necessariamente o ótimo global.
 */
export function removerApostasRedundantes(
  apostas: number[][],
  universo: number[],
  k: number,
  t: number,
): number[][] {
  if (apostas.length <= 1) return apostas.map(a => [...a]);
  const u = [...new Set(universo)].sort((a, b) => a - b);
  const totalT = nCombinacoes(u.length, t);
  if (totalT <= 0) return apostas.map(a => [...a]);

  const indices = apostas.map(a => indicesAlvosCobertosPorAposta(a, u, t));
  const contagem = new Uint32Array(totalT);
  for (const idxs of indices) {
    for (const i of idxs) contagem[i]++;
  }

  const ativas = new Array<boolean>(apostas.length).fill(true);
  let alterou = true;
  while (alterou) {
    alterou = false;
    for (let bi = 0; bi < apostas.length; bi++) {
      if (!ativas[bi]) continue;
      let temExclusivo = false;
      for (const i of indices[bi]) {
        if (contagem[i] === 1) { temExclusivo = true; break; }
      }
      if (!temExclusivo) {
        for (const i of indices[bi]) contagem[i]--;
        ativas[bi] = false;
        alterou = true;
      }
    }
  }

  return apostas.filter((_, i) => ativas[i]).map(a => [...a]);
}

export interface CompletarCoberturaOptions {
  apostas: number[][];
  universo: number[];
  k: number;
  t: number;
  /** 0/undefined = sem limite de apostas. */
  maxApostas?: number;
  seed?: number;
  candidatosPool?: number;
  amostraPorPasso?: number;
  /** Só aceita blocos que satisfazem este predicado (ex.: filtros + repetidas). */
  aceitarBloco?: (aposta: number[]) => boolean;
  limiteTempoMs?: number;
}

/**
 * Repara uma cobertura parcial: mantém as apostas existentes e adiciona
 * blocos (respeitando `aceitarBloco`) até cobrir 100% dos t-subconjuntos ou
 * atingir `maxApostas`. Útil depois de filtros que removem apostas.
 */
export function completarCobertura(opts: CompletarCoberturaOptions): number[][] {
  const {
    apostas,
    universo,
    k,
    t,
    maxApostas = 0,
    seed = 7,
    candidatosPool = 2000,
    amostraPorPasso = t <= 3 ? 2000 : t === 4 ? 500 : t <= 8 ? 60 : 25,
    aceitarBloco,
    limiteTempoMs = 0,
  } = opts;

  const u = [...new Set(universo)].sort((a, b) => a - b);
  const inicial: number[][] = [];
  const vistos = new Set<string>();
  for (const a of apostas) {
    const ordenada = [...a].sort((x, y) => x - y);
    if (ordenada.length !== k || new Set(ordenada).size !== k) continue;
    if (!ordenada.every(n => u.includes(n))) continue;
    const chave = ordenada.join(",");
    if (vistos.has(chave)) continue;
    vistos.add(chave);
    inicial.push(ordenada);
  }

  const totalT = nCombinacoes(u.length, t);
  if (totalT <= 0) return inicial;

  const coberta = new Uint8Array(totalT);
  let cobertos = 0;
  for (const a of inicial) {
    for (const idx of indicesAlvosCobertosPorAposta(a, u, t)) {
      if (!coberta[idx]) {
        coberta[idx] = 1;
        cobertos++;
      }
    }
  }
  if (cobertos >= totalT) return inicial;

  const limite = maxApostasIlimitado(maxApostas)
    ? Number.POSITIVE_INFINITY
    : Math.max(0, maxApostas - inicial.length);
  if (limite <= 0) return inicial;

  const pool = gerarApostasCandidatas({
    universo: u,
    k,
    limite: Math.min(LIMITE_POOL_CANDIDATOS, Math.max(1, candidatosPool)),
    seed,
    aceitarBloco,
  });
  if (!pool.length) return inicial;

  const indicesCache: (Int32Array | null)[] = new Array(pool.length).fill(null);
  const indicesDe = (ci: number): Int32Array => {
    const cache = indicesCache[ci];
    if (cache !== null) return cache;
    const idx = Int32Array.from(indicesAlvosCobertosPorAposta(pool[ci], u, t));
    indicesCache[ci] = idx;
    return idx;
  };

  const rng = new LCG(seed);
  const restantes = pool
    .map((_, i) => i)
    .filter(ci => {
      const chave = pool[ci].join(",");
      return !vistos.has(chave);
    });
  const resultado = [...inicial];
  const inicio = Date.now();
  let adicionadas = 0;

  while (cobertos < totalT && restantes.length > 0 && adicionadas < limite) {
    if (limiteTempoMs > 0 && Date.now() - inicio > limiteTempoMs) break;
    const amostraSize = Math.min(amostraPorPasso, restantes.length);
    const amostra: number[] = [];
    const temp = [...restantes];
    for (let i = 0; i < amostraSize; i++) {
      const j = Math.floor(rng.next() * temp.length);
      amostra.push(temp[j]);
      temp.splice(j, 1);
    }

    let melhorIdx = -1;
    let melhorGanho = 0;
    for (const ci of amostra) {
      let ganho = 0;
      for (const idx of indicesDe(ci)) {
        if (!coberta[idx]) ganho++;
      }
      if (ganho > melhorGanho) {
        melhorGanho = ganho;
        melhorIdx = ci;
      }
    }
    if (melhorIdx < 0) break;

    resultado.push([...pool[melhorIdx]]);
    vistos.add(pool[melhorIdx].join(","));
    for (const idx of indicesDe(melhorIdx)) {
      if (!coberta[idx]) {
        coberta[idx] = 1;
        cobertos++;
      }
    }
    restantes.splice(restantes.indexOf(melhorIdx), 1);
    adicionadas++;
  }

  return resultado;
}

/** Aplica filtro de repetição de um sorteio-base a cada aposta. */
export function apostaSatisfazRepetidas(
  aposta: number[],
  numerosBase: number[],
  min: number,
  max: number,
): boolean {
  if (!numerosBase.length) return true;
  const base = new Set(numerosBase);
  let qtd = 0;
  for (const n of aposta) if (base.has(n)) qtd++;
  return qtd >= min && qtd <= max;
}

/** Hill climbing: substitui apostas para elevar cobertura sem aumentar o número de apostas. */
export function buscaLocalFechamento(opts: BuscaLocalOptions): number[][] {
  const {
    apostas,
    universo,
    k,
    t,
    maxIteracoes = 200,
    seed = 1,
    candidatosPool = 600,
    aceitarBloco,
    orcamentoAvaliacoes = ORCAMENTO_BUSCA_LOCAL,
  } = opts;
  const u = [...new Set(universo)].sort((a, b) => a - b);
  const v = u.length;
  const rng = new LCG(seed);

  const apostasTuplas = apostas.map((a) => [...a].sort((x, y) => x - y));

  // Orçamento: a cada iteração avaliamos no máximo `apostasPorIteracao` apostas
  // contra o pool. Sem esse teto, n apostas × pool candidatos degenera em
  // minutos/horas para volumes grandes.
  if (orcamentoAvaliacoes <= 0) return apostas;
  const pool = gerarApostasCandidatas({ universo: u, k, limite: candidatosPool, seed, aceitarBloco });
  rng.next();
  const apostasPorIteracao = Math.max(
    1,
    Math.min(
      apostasTuplas.length,
      Math.floor(orcamentoAvaliacoes / (Math.max(1, maxIteracoes) * Math.max(1, pool.length))),
    ),
  );

  const indicesPorAposta = apostasTuplas.map((a) => indicesAlvosCobertosPorAposta(a, u, t));

  const totalT = nCombinacoes(v, t);
  const contagem = new Array(totalT).fill(0);
  const coberta = new Uint8Array(totalT);
  let cobertos = 0;
  for (const indices of indicesPorAposta) {
    for (const idx of indices) {
      if (contagem[idx] === 0) {
        coberta[idx] = 1;
        cobertos++;
      }
      contagem[idx]++;
    }
  }

  const indicesPool = pool.map((a) => indicesAlvosCobertosPorAposta(a, u, t));

  for (let it = 0; it < maxIteracoes; it++) {
    if (cobertos >= totalT) break;
    // embaralha ordem das apostas para tentar trocas diferentes
    for (let i = apostasTuplas.length - 1; i > 0; i--) {
      const j = Math.floor(rng.next() * (i + 1));
      [apostasTuplas[i], apostasTuplas[j]] = [apostasTuplas[j], apostasTuplas[i]];
      [indicesPorAposta[i], indicesPorAposta[j]] = [indicesPorAposta[j], indicesPorAposta[i]];
    }

    let progresso = false;
    for (let i = 0; i < apostasPorIteracao; i++) {
      const apostaAtual = apostasTuplas[i];
      const indicesAtual = indicesPorAposta[i];
      for (let ci = 0; ci < pool.length; ci++) {
        const cand = pool[ci];
        const igual = cand.length === apostaAtual.length && cand.every((x, ix) => x === apostaAtual[ix]);
        if (igual) continue;
        const indicesCand = indicesPool[ci];
        const novoCoberto = indicesCand.filter((idx) => contagem[idx] === 0).length;
        const perdido = indicesAtual.filter((idx) => contagem[idx] === 1).length;
        const liquido = novoCoberto - perdido;
        if (liquido > 0) {
          // remove atual
          for (const idx of indicesAtual) {
            contagem[idx]--;
            if (contagem[idx] === 0) {
              coberta[idx] = 0;
              cobertos--;
            }
          }
          // adiciona candidata
          for (const idx of indicesCand) {
            if (contagem[idx] === 0) {
              coberta[idx] = 1;
              cobertos++;
            }
            contagem[idx]++;
          }
          apostasTuplas[i] = [...cand];
          indicesPorAposta[i] = indicesCand;
          progresso = true;
          break;
        }
      }
      if (cobertos >= totalT) break;
    }
    if (!progresso) break;
  }

  return apostasTuplas;
}

/** Verifica EXATAMENTE se o fechamento cobre todos os t-subconjuntos. */
export function verificarCobertura(
  apostas: number[][],
  universo: number[],
  k: number,
  t: number,
  dezenasBase: number = 15,
  precoBase: number = PRECO_APOSTA_15,
): VerificarCoberturaResult {
  if (k < t) throw new Error("Deve valer t <= k");
  const u = [...new Set(universo)].sort((a, b) => a - b);
  const v = u.length;
  const pos = new Map<number, number>();
  u.forEach((n, i) => pos.set(n, i));

  const totalT = nCombinacoes(v, t);
  if (totalT > 60_000_000) {
    throw new Error(`Cobertura grande demais: C(${v},${t})=${totalT}. Reduza o universo ou t.`);
  }
  const coberta = new Uint8Array(totalT);
  let apostasValidas = 0;
  let apostasInvalidas = 0;

  for (const aposta of apostas) {
    const a = [...aposta].sort((x, y) => x - y);
    if (a.length !== k || a.some((n) => !pos.has(n))) {
      apostasInvalidas++;
      continue;
    }
    if (new Set(a).size !== k) {
      apostasInvalidas++;
      continue;
    }
    apostasValidas++;
    for (const idx of indicesAlvosCobertosPorAposta(a, u, t)) {
      coberta[idx] = 1;
    }
  }

  let cobertos = 0;
  for (let i = 0; i < totalT; i++) if (coberta[i]) cobertos++;
  const garantia = totalT ? (cobertos / totalT) * 100 : 100;

  return {
    coberta: cobertos === totalT,
    tSubsetsTotal: totalT,
    tSubsetsCobertos: cobertos,
    garantiaPercentual: Math.round(garantia * 10000) / 10000,
    apostasValidas,
    apostasInvalidas,
    totalApostas: apostas.length,
    custoEstimado: Math.round(apostasValidas * custoPorAposta(k, dezenasBase, precoBase) * 100) / 100,
  };
}

/** Custo real do fechamento, considerando o tamanho real de cada aposta (k). */
export function relatorioCusto(
  apostas: number[][],
  k?: number,
  dezenasBase: number = 15,
  precoBase: number = PRECO_APOSTA_15,
): RelatorioCustoResult {
  const total = apostas.length;
  const kEfetivo = k ?? apostas[0]?.length ?? dezenasBase;
  const preco = custoPorAposta(kEfetivo, dezenasBase, precoBase);
  return {
    totalApostas: total,
    k: kEfetivo,
    precoPorJogo: preco,
    custoTotal: Math.round(total * preco * 100) / 100,
    reducaoVsUniverso25_15:
      dezenasBase === 15 && kEfetivo === 15
        ? Math.round(((1 - total / nCombinacoes(25, 15)) * 100) * 10000) / 10000
        : 0,
  };
}

/** Fechamento para Lotofácil (universo 1..25). */
export function fechamentoLotofacil25(opts: Partial<ConstruirFechamentoOptions> & { k?: number; t?: number; maxApostas?: number; seed?: number } = {}): number[][] {
  return construirFechamentoGulosoAmostrado({
    universo: opts.universo ?? Array.from({ length: 25 }, (_, i) => i + 1),
    k: opts.k ?? 15,
    t: opts.t ?? 11,
    maxApostas: opts.maxApostas ?? 2000,
    seed: opts.seed ?? 42,
    candidatosPool: opts.candidatosPool,
    amostraPorPasso: opts.amostraPorPasso,
  });
}

/** Fechamento para Lotofácil com otimização de busca local. */
export function fechamentoLotofacil25Otimizado(opts: {
  universo?: number[];
  k?: number;
  t?: number;
  maxApostas?: number;
  seed?: number;
  maxIteracoes?: number;
  buscaSeed?: number;
  candidatosPool?: number;
  amostraPorPasso?: number;
  aceitarBloco?: (aposta: number[]) => boolean;
  limiteTempoMs?: number;
} = {}): number[][] {
  const universo = opts.universo ?? Array.from({ length: 25 }, (_, i) => i + 1);
  const apostas = construirFechamentoGulosoAmostrado({
    universo,
    k: opts.k ?? 15,
    t: opts.t ?? 11,
    maxApostas: opts.maxApostas ?? 200,
    seed: opts.seed ?? 7,
    candidatosPool: opts.candidatosPool,
    amostraPorPasso: opts.amostraPorPasso,
    aceitarBloco: opts.aceitarBloco,
    limiteTempoMs: opts.limiteTempoMs,
  });

  if (apostas.length > 1) {
    return buscaLocalFechamento({
      apostas,
      universo,
      k: opts.k ?? 15,
      t: opts.t ?? 11,
      maxIteracoes: opts.maxIteracoes ?? 100,
      seed: opts.buscaSeed ?? (opts.seed ?? 7) + 1,
      candidatosPool: opts.candidatosPool ?? 400,
      aceitarBloco: opts.aceitarBloco,
    });
  }
  return apostas;
}

export interface GerarFechamentoComRestricoesOptions {
  universo?: number[];
  fixos?: number[];
  excluidos?: number[];
  k: number;
  t: number;
  maxApostas?: number;
  seed?: number;
  otimizado?: boolean;
  maxIteracoes?: number;
  buscaSeed?: number;
  candidatosPool?: number;
  amostraPorPasso?: number;
  filtrosCategorias?: FiltroCategoria[];
  /** Remove apostas redundantes ao final (preserva cobertura). */
  removerRedundantes?: boolean;
  /** Tempo máximo em ms; 0/undefined = sem limite. */
  limiteTempoMs?: number;
}

/**
 * Gera fechamento C(v, k, t) respeitando fixos, excluídos e filtros de categoria.
 *
 * Regras:
 * - excluídos saem do universo
 * - fixos entram em TODA aposta gerada
 * - O fechamento é construído sobre o restante (universo - excluídos - fixos)
 *   com k' = k - fixos.length e t' = t.
 * - Cada aposta final = fixos ∪ (aposta do fechamento do restante).
 *
 * Garantia: se o fechamento do restante cobre todos os t-subconjuntos do
 * restante, então qualquer t-subconjunto do universo total está contido em
 * alguma aposta final (porque S = (S ∩ fixos) ∪ (S ∩ restante), e S ∩ restante
 * pode ser completado a um t-subconjunto do restante que está em alguma aposta
 * que já contém todos os fixos).
 */
export function gerarFechamentoComRestricoes(opts: GerarFechamentoComRestricoesOptions): number[][] {
  const {
    universo: universoInformado,
    fixos: fixosInformados = [],
    excluidos: excluidosInformados = [],
    k,
    t,
    maxApostas = 200,
    seed = 7,
    otimizado = true,
    maxIteracoes = 100,
    buscaSeed,
    candidatosPool = 400,
    amostraPorPasso = t <= 3 ? 2000 : t === 4 ? 500 : t <= 8 ? 60 : 25,
    filtrosCategorias: filtrosInformados = [],
    removerRedundantes = false,
    limiteTempoMs = 0,
  } = opts;

  const fixos = [...new Set(fixosInformados)].sort((a, b) => a - b);
  const excluidos = [...new Set(excluidosInformados)].sort((a, b) => a - b);

  if (fixos.length > k) throw new Error(`Não é possível fixar ${fixos.length} números em aposta de ${k} dezenas`);
  if (t < 1) throw new Error("t deve ser >= 1");

  const universoBase = universoInformado?.length ? [...new Set(universoInformado)] : Array.from({ length: 25 }, (_, i) => i + 1);
  const universoBaseSorted = universoBase.sort((a, b) => a - b);

  const universoRestante = universoBaseSorted.filter(
    n => !excluidos.includes(n) && !fixos.includes(n),
  );

  const kEfetivo = k - fixos.length;
  if (kEfetivo < t) {
    throw new Error(
      `Após descontar ${fixos.length} fixo(s), restam ${kEfetivo} posição(ões) por aposta, insuficiente para garantir t=${t}. Reduza t ou aumente k.`,
    );
  }
  if (universoRestante.length < t) {
    throw new Error(`Universo restante (${universoRestante.length}) menor que t=${t}.`);
  }

  const aceitarBloco = filtrosInformados.length > 0
    ? (a: number[]) => apostaSatisfazCategorias([...fixos, ...a], filtrosInformados)
    : undefined;

  const apostasBase = otimizado
    ? fechamentoLotofacil25Otimizado({
        universo: universoRestante,
        k: kEfetivo,
        t,
        maxApostas,
        seed,
        maxIteracoes,
        buscaSeed,
        candidatosPool,
        amostraPorPasso,
        aceitarBloco,
        limiteTempoMs,
      })
    : construirFechamentoGulosoAmostrado({
        universo: universoRestante,
        k: kEfetivo,
        t,
        maxApostas,
        seed,
        candidatosPool,
        amostraPorPasso,
        aceitarBloco,
        limiteTempoMs,
      });

  // Cada aposta final = fixos ∪ aposta do restante, ordenada e sem duplicatas
  const vistos = new Set<string>();
  const finais: number[][] = [];
  for (const base of apostasBase) {
    const aposta = [...fixos, ...base].sort((a, b) => a - b);
    if (new Set(aposta).size !== aposta.length) continue;
    const chave = aposta.join(",");
    if (!vistos.has(chave)) {
      vistos.add(chave);
      finais.push(aposta);
    }
  }

  // Aplica filtros de categoria, se houver. Como o guloso já gera blocos
  // válidos (aceitarBloco), isto é apenas uma salvaguarda.
  let resultado = finais;
  if (filtrosInformados.length > 0) {
    resultado = resultado.filter((a) => apostaSatisfazCategorias(a, filtrosInformados));

    // Reparo: se algum filtro/limite deixou buracos, completa a cobertura
    // adicionando blocos válidos que ainda caibam no orçamento.
    if (resultado.length > 0) {
      const livres = resultado.map(a => a.filter(n => !fixos.includes(n)));
      const reparado = completarCobertura({
        apostas: livres,
        universo: universoRestante,
        k: kEfetivo,
        t,
        maxApostas: maxApostasIlimitado(maxApostas) ? 0 : Math.max(maxApostas, resultado.length),
        seed,
        aceitarBloco: (a) => apostaSatisfazCategorias([...fixos, ...a], filtrosInformados),
        limiteTempoMs,
      });
      resultado = reparado.map(a => [...fixos, ...a].sort((x, y) => x - y));
    }
  }

  // Remove apostas que não cobrem nenhum trio exclusivo, preservando a cobertura.
  if (removerRedundantes) {
    resultado = removerApostasRedundantes(resultado, universoBaseSorted, k, t);
  }

  return resultado;
}

export interface FiltroCategoria {
  numeros: number[];
  min: number;
  max: number;
}

/** Verifica se uma aposta respeita todos os filtros de categoria (min/max por conjunto). */
export function apostaSatisfazCategorias(
  aposta: number[],
  filtros: FiltroCategoria[],
): boolean {
  for (const f of filtros) {
    const catSet = new Set(f.numeros);
    let qtd = 0;
    for (const n of aposta) {
      if (catSet.has(n)) qtd++;
    }
    if (qtd < f.min || qtd > f.max) return false;
  }
  return true;
}

export interface PermutarCoverParaFiltrosOptions {
  /** Blocos do cover com rótulos 1..v (como no registry). */
  blocos: number[][];
  /** Números reais disponíveis (sem fixos/excluídos), na ordem que será permutada. */
  universo: number[];
  fixos?: number[];
  filtros: FiltroCategoria[];
  seed?: number;
  /** Tempo máximo da busca; 0/undefined usa 750 ms. */
  limiteTempoMs?: number;
  /** Iterações por reinício (teto). */
  maxIteracoes?: number;
}

export interface PermutarCoverParaFiltrosResult {
  /** Mapeamento posição -> número real que satisfez os filtros. */
  universo: number[];
  /** Apostas finais (fixos + bloco mapeado), ordenadas. */
  apostas: number[][];
  /** Número de blocos que violam os filtros (0 = sucesso). */
  violacoes: number;
}

/**
 * Procura uma permutação dos rótulos do cover que faça TODOS os blocos
 * satisfazerem os filtros de categoria. A cobertura é preservada por
 * construção (permutação é bijeção), então se `violacoes === 0` o cover
 * mantém 100% dos t-subconjuntos com o mesmo número de apostas.
 */
export function permutarCoverParaFiltros(
  opts: PermutarCoverParaFiltrosOptions,
): PermutarCoverParaFiltrosResult | null {
  const { blocos, universo, fixos = [], filtros, seed = 7, limiteTempoMs = 750, maxIteracoes = 20_000 } = opts;
  if (!blocos.length || !universo.length) return null;
  if (!filtros.length) {
    return {
      universo,
      apostas: blocos.map(b => [...fixos, ...b.map(x => universo[x - 1])].sort((a, b) => a - b)),
      violacoes: 0,
    };
  }

  const v = universo.length;
  const blocosPos = blocos.map(b => b.map(x => x - 1));
  const filtrosSets = filtros.map(f => ({ set: new Set(f.numeros), min: f.min, max: f.max }));
  // Quantos fixos entram em cada categoria (constante para todos os blocos).
  const fixosPorFiltro = filtrosSets.map(f => fixos.reduce((acc, n) => acc + (f.set.has(n) ? 1 : 0), 0));

  const avaliar = (perm: number[]): number => {
    let violacoes = 0;
    for (const bloco of blocosPos) {
      let ok = true;
      for (let fi = 0; fi < filtrosSets.length; fi++) {
        const f = filtrosSets[fi];
        let qtd = fixosPorFiltro[fi];
        for (const pos of bloco) {
          if (f.set.has(perm[pos])) qtd++;
        }
        if (qtd < f.min || qtd > f.max) {
          ok = false;
          break;
        }
      }
      if (!ok) violacoes++;
    }
    return violacoes;
  };

  const montar = (perm: number[]): number[][] =>
    blocos.map(b => [...fixos, ...b.map(x => perm[x - 1])].sort((a, b) => a - b));

  let melhorPerm = [...universo];
  let melhorViol = avaliar(melhorPerm);
  if (melhorViol === 0) {
    return { universo: melhorPerm, apostas: montar(melhorPerm), violacoes: 0 };
  }

  const rng = new LCG(seed);
  const inicio = Date.now();
  const orcamento = limiteTempoMs > 0 ? limiteTempoMs : 750;
  // Cada avaliação custa ~ blocos * k; limita iterações para não estourar.
  const iteracoesEfetivas = Math.max(
    20,
    Math.min(maxIteracoes, Math.floor(2_000_000 / Math.max(1, blocos.length * (blocos[0]?.length ?? 1)))),
  );
  const reinicios = 6;
  const porReinicio = Math.max(20, Math.floor(iteracoesEfetivas / reinicios));

  for (let r = 0; r < reinicios; r++) {
    if (Date.now() - inicio > orcamento) break;
    const perm = [...universo];
    for (let i = perm.length - 1; i > 0; i--) {
      const j = Math.floor(rng.next() * (i + 1));
      [perm[i], perm[j]] = [perm[j], perm[i]];
    }
    let atual = avaliar(perm);
    if (atual < melhorViol) {
      melhorViol = atual;
      melhorPerm = [...perm];
    }
    if (atual === 0) return { universo: perm, apostas: montar(perm), violacoes: 0 };

    let T = 2.0;
    for (let it = 0; it < porReinicio; it++) {
      if (Date.now() - inicio > orcamento) break;
      let a = Math.floor(rng.next() * v);
      let b = Math.floor(rng.next() * v);
      if (a === b) b = (b + 1) % v;
      [perm[a], perm[b]] = [perm[b], perm[a]];
      const novo = avaliar(perm);
      const aceita = novo <= atual || rng.next() < Math.exp(-(novo - atual) / Math.max(T, 1e-9));
      if (aceita) {
        atual = novo;
        if (novo < melhorViol) {
          melhorViol = novo;
          melhorPerm = [...perm];
        }
        if (novo === 0) return { universo: perm, apostas: montar(perm), violacoes: 0 };
      } else {
        [perm[a], perm[b]] = [perm[b], perm[a]];
      }
      T *= 0.9995;
    }
  }

  return { universo: melhorPerm, apostas: montar(melhorPerm), violacoes: melhorViol };
}


/**
 * Filtra apostas conforme categorias e recalcula a cobertura exata.
 * Retorna { apostasFiltradas, cobertura }.
 */
export function aplicarFiltrosCategoriasERecalcular(
  apostas: number[][],
  filtros: FiltroCategoria[],
  universo: number[],
  k: number,
  t: number,
): { apostasFiltradas: number[][]; cobertura: VerificarCoberturaResult } {
  const apostasFiltradas = apostas.filter((a) => apostaSatisfazCategorias(a, filtros));
  const cobertura = verificarCobertura(apostasFiltradas, universo, k, t);
  return { apostasFiltradas, cobertura };
}

// ============================================================================
// 1. WHEELS PRÉ-COMPUTADOS (Construtivos exatos)
// ============================================================================

export interface WheelConhecido {
  id: string;
  descricao: string;
  v: number;
  k: number;
  t: number;
  totalApostas: number;
  apostas: number[][];
  fonte?: string;
}

/**
 * Wheels pré-computados conhecidos para Lotofácil (v=25).
 * Estes são construtivos exatos: cobrem 100% dos t-subconjuntos.
 */
export const WHEELS_LOTOFACIL: WheelConhecido[] = [
  {
    id: 'lf-25-15-2-30',
    descricao: 'C(25,15,2) - Garante 2 acertos se as 2 dezenas saírem entre as 25',
    v: 25, k: 15, t: 2,
    totalApostas: 30,
    apostas: [
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,16],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,17],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,18],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,19],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,20],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,21],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,22],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,23],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,24],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,25],
      [15,16,17,18,19,20,21,22,23,24,25,1,2,3,4],
      [15,16,17,18,19,20,21,22,23,24,25,5,6,7,8],
      [15,16,17,18,19,20,21,22,23,24,25,9,10,11,12],
      [1,2,3,4,5,15,16,17,18,19,20,21,22,23,24],
      [1,2,3,4,5,15,16,17,18,19,20,21,22,23,25],
      [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
      [6,7,8,9,10,11,12,13,14,15,16,17,18,19,21],
      [6,7,8,9,10,11,12,13,14,15,16,17,18,19,22],
      [6,7,8,9,10,11,12,13,14,15,16,17,18,19,23],
      [6,7,8,9,10,11,12,13,14,15,16,17,18,19,24],
      [6,7,8,9,10,11,12,13,14,15,16,17,18,19,25],
      [20,21,22,23,24,25,1,2,3,4,5,6,7,8,9],
      [20,21,22,23,24,25,10,11,12,13,14,15,16,17],
      [20,21,22,23,24,25,18,19,1,2,3,4,5,6,7],
      [20,21,22,23,24,25,8,9,10,11,12,13,14,15],
      [1,16,17,18,19,20,21,22,23,24,25,2,3,4,5],
      [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
    ],
    fonte: 'Construtivo heurístico LotoScope',
  },
];

/**
 * Busca um wheel pré-computado compatível com (v, k, t).
 */
export function buscarWheel(v: number, k: number, t: number): WheelConhecido | undefined {
  return WHEELS_LOTOFACIL.find(w => w.v === v && w.k === k && w.t === t);
}

/**
 * Gera fechamento usando wheel pré-computado se disponível, senão cai no guloso.
 */
export function gerarFechamentoComWheel(
  v: number,
  k: number,
  t: number,
  maxApostas: number = 200,
  seed: number = 7,
): { apostas: number[][]; modo: string; wheelUsado: boolean } {
  const wheel = buscarWheel(v, k, t);
  if (wheel && (maxApostasIlimitado(maxApostas) || wheel.apostas.length <= maxApostas)) {
    return {
      apostas: wheel.apostas,
      modo: 'wheel_pre_computado',
      wheelUsado: true,
    };
  }
  // Fallback: guloso amostrado
  const universo = Array.from({ length: v }, (_, i) => i + 1);
  const apostas = construirFechamentoGulosoAmostrado({
    universo, k, t, maxApostas, seed,
  });
  return { apostas, modo: 'guloso_amostrado', wheelUsado: false };
}

// ============================================================================
// 2. BUSCA LOCAL AVANÇADA (Simulated Annealing)
// ============================================================================

export interface SimulatedAnnealingOptions {
  apostas: number[][];
  universo: number[];
  k: number;
  t: number;
  maxIteracoes?: number;
  temperaturaInicial?: number;
  taxaResfriamento?: number;
  candidatosPool?: number;
  seed?: number;
  /** Só aceita blocos candidatos que satisfazem este predicado. */
  aceitarBloco?: (aposta: number[]) => boolean;
}

function aceitarPiora(delta: number, temperatura: number, rng: LCG): boolean {
  if (delta > 0) return true;
  const probabilidade = Math.exp(delta / temperatura);
  return rng.next() < probabilidade;
}

export function buscaLocalSimulatedAnnealing(opts: SimulatedAnnealingOptions): number[][] {
  const {
    apostas,
    universo,
    k,
    t,
    maxIteracoes = 500,
    temperaturaInicial = 10.0,
    taxaResfriamento = 0.995,
    candidatosPool = 600,
    seed = 1,
    aceitarBloco,
  } = opts;

  const u = [...new Set(universo)].sort((a, b) => a - b);
  const v = u.length;
  const rng = new LCG(seed);

  const totalT = nCombinacoes(v, t);
  const contagem = new Array(totalT).fill(0);
  const coberta = new Uint8Array(totalT);
  let cobertos = 0;

  const apostasAtuais = apostas.map(a => [...a].sort((x, y) => x - y));
  const indicesPorAposta = apostasAtuais.map(a => indicesAlvosCobertosPorAposta(a, u, t));

  for (const indices of indicesPorAposta) {
    for (const idx of indices) {
      if (contagem[idx] === 0) { coberta[idx] = 1; cobertos++; }
      contagem[idx]++;
    }
  }

  const pool = gerarApostasCandidatas({ universo: u, k, limite: candidatosPool, seed, aceitarBloco });
  const indicesPool = pool.map(a => indicesAlvosCobertosPorAposta(a, u, t));

  let temperatura = temperaturaInicial;
  let melhorCobertos = cobertos;
  let melhorApostas = [...apostasAtuais];

  for (let it = 0; it < maxIteracoes; it++) {
    if (cobertos >= totalT) break;

    // Escolhe uma aposta aleatória para tentar trocar
    const i = Math.floor(rng.next() * apostasAtuais.length);
    const apostaAtual = apostasAtuais[i];
    const indicesAtual = indicesPorAposta[i];

    // Escolhe um candidato aleatório do pool
    const ci = Math.floor(rng.next() * pool.length);
    if (pool[ci].length === apostaAtual.length &&
        pool[ci].every((x, ix) => x === apostaAtual[ix])) continue;

    const indicesCand = indicesPool[ci];

    // Calcula ganho líquido
    const novoCoberto = indicesCand.filter(idx => contagem[idx] === 0).length;
    const perdido = indicesAtual.filter(idx => contagem[idx] === 1).length;
    const delta = novoCoberto - perdido;

    // Decide aceitar
    if (delta > 0 || aceitarPiora(delta, temperatura, rng)) {
      // Remove atual
      for (const idx of indicesAtual) {
        contagem[idx]--;
        if (contagem[idx] === 0) { coberta[idx] = 0; cobertos--; }
      }
      // Adiciona candidata
      for (const idx of indicesCand) {
        if (contagem[idx] === 0) { coberta[idx] = 1; cobertos++; }
        contagem[idx]++;
      }
      apostasAtuais[i] = [...pool[ci]];
      indicesPorAposta[i] = indicesCand;

      if (cobertos > melhorCobertos) {
        melhorCobertos = cobertos;
        melhorApostas = [...apostasAtuais];
      }
    }

    temperatura *= taxaResfriamento;
    if (temperatura < 0.01) temperatura = 0.01;
  }

  return melhorApostas;
}

// ============================================================================
// 3. VALIDAÇÃO CONTRA SORTEIOS REAIS
// ============================================================================

export interface SorteioReal {
  concurso: number;
  dezenas: number[];
  data?: string;
}

export interface ValidacaoSorteiosResult {
  totalSorteios: number;
  sorteiosAvaliados: number;
  distribuicaoAcertos: Record<number, number>; // chave = qtd acertos, valor = qtd sorteios
  garantiaCumprida: boolean; // se pelo menos uma aposta acertou t em cada sorteio
  acertosMin: number;
  acertosMax: number;
  mediaAcertos: number;
  detalhePorSorteio: { concurso: number; acertos: number; apostaIdx: number }[];
}

/**
 * Valida um fechamento contra sorteios reais.
 * Para cada sorteio, verifica quantos acertos a melhor aposta do fechamento obteve.
 */
export function validarContraSorteiosReais(
  apostas: number[][],
  sorteios: SorteioReal[],
  k: number,
  t: number,
): ValidacaoSorteiosResult {
  const distribuicao: Record<number, number> = {};
  const detalhe: { concurso: number; acertos: number; apostaIdx: number }[] = [];
  let apostasAvaliadas = 0;
  let garantiaCumprida = true;
  let acertosMin = Infinity;
  let acertosMax = -Infinity;
  let somaAcertos = 0;

  for (const s of sorteios) {
    const sorteioSet = new Set(s.dezenas);
    let melhorAcertos = 0;
    let melhorIdx = -1;

    for (let i = 0; i < apostas.length; i++) {
      const aposta = apostas[i];
      if (aposta.length !== k) continue;
      let acertos = 0;
      for (const n of aposta) {
        if (sorteioSet.has(n)) acertos++;
      }
      if (acertos > melhorAcertos) {
        melhorAcertos = acertos;
        melhorIdx = i;
      }
    }

    apostasAvaliadas++;
    distribuicao[melhorAcertos] = (distribuicao[melhorAcertos] ?? 0) + 1;
    detalhe.push({ concurso: s.concurso, acertos: melhorAcertos, apostaIdx: melhorIdx });
    somaAcertos += melhorAcertos;
    acertosMin = Math.min(acertosMin, melhorAcertos);
    acertosMax = Math.max(acertosMax, melhorAcertos);

    if (melhorAcertos < t) garantiaCumprida = false;
  }

  return {
    totalSorteios: sorteios.length,
    sorteiosAvaliados: apostasAvaliadas,
    distribuicaoAcertos: distribuicao,
    garantiaCumprida,
    acertosMin: acertosMin === Infinity ? 0 : acertosMin,
    acertosMax,
    mediaAcertos: apostasAvaliadas > 0 ? somaAcertos / apostasAvaliadas : 0,
    detalhePorSorteio: detalhe,
  };
}

// ============================================================================
// 7. ANÁLISE DE SOBREPOSIÇÃO DE DEZENAS
// ============================================================================

export interface AnaliseSobreposicaoResult {
  totalApostas: number;
  frequenciaPorDezena: Record<number, number>;
  dezenasMaisFrequentes: { dezena: number; frequencia: number; percentual: number }[];
  dezenasMenosFrequentes: { dezena: number; frequencia: number; percentual: number }[];
  sobreposicaoMediaEntreApostas: number;
  diversidade: 'Alta' | 'Média' | 'Baixa';
}

export function analisarSobreposicaoDezenas(
  apostas: number[][],
  universo: number[],
): AnaliseSobreposicaoResult {
  const freq: Record<number, number> = {};
  for (const n of universo) freq[n] = 0;

  for (const aposta of apostas) {
    for (const n of aposta) {
      if (freq[n] !== undefined) freq[n]++;
    }
  }

  const totalApostas = apostas.length;
  const items = Object.entries(freq).map(([dezena, frequencia]) => ({
    dezena: Number(dezena),
    frequencia,
    percentual: totalApostas > 0 ? (frequencia / totalApostas) * 100 : 0,
  }));

  const maisFrequentes = [...items].sort((a, b) => b.frequencia - a.frequencia).slice(0, 5);
  const menosFrequentes = [...items].sort((a, b) => a.frequencia - b.frequencia).slice(0, 5);

  // Sobreposição média entre pares de apostas
  let somaSobreposicao = 0;
  let pares = 0;
  for (let i = 0; i < apostas.length; i++) {
    const setA = new Set(apostas[i]);
    for (let j = i + 1; j < apostas.length; j++) {
      let inter = 0;
      for (const n of apostas[j]) if (setA.has(n)) inter++;
      somaSobreposicao += inter;
      pares++;
    }
  }
  const sobreposicaoMedia = pares > 0 ? somaSobreposicao / pares : 0;

  let diversidade: 'Alta' | 'Média' | 'Baixa';
  if (sobreposicaoMedia < 3) diversidade = 'Alta';
  else if (sobreposicaoMedia < 6) diversidade = 'Média';
  else diversidade = 'Baixa';

  return {
    totalApostas,
    frequenciaPorDezena: freq,
    dezenasMaisFrequentes: maisFrequentes,
    dezenasMenosFrequentes: menosFrequentes,
    sobreposicaoMediaEntreApostas: Math.round(sobreposicaoMedia * 100) / 100,
    diversidade,
  };
}

// ============================================================================
// 5. BACKTEST HISTÓRICO (acertos, prêmios e repetidas)
// ============================================================================

export interface ResultadoHistorico {
  concurso: number;
  numeros: number[];
}

export interface BacktestFechamentoOptions {
  apostas: number[][];
  resultados: ResultadoHistorico[];
  k?: number;
  premios?: Record<number, number>;
  faixasPremio?: number[];
  dezenasBase?: number;
  precoBase?: number;
}

export interface BacktestFechamentoResult {
  totalConcursos: number;
  mediaMelhorAcerto: number;
  distribuicaoMelhorAcerto: number[];
  faixas: { acertos: number; concursos: number; percentual: number }[];
  premioMedio: number;
  custoTotal: number;
  roiMedio: number;
  melhoresConcursos: {
    concurso: number;
    melhorAcerto: number;
    premio: number;
    repetidas: number;
    aposta: number[];
  }[];
  repetidasDistribuicao: { repetidas: number; concursos: number; percentual: number }[];
}

/**
 * Roda um conjunto fixo de apostas contra um histórico de sorteios.
 * Retorna a distribuição do MELHOR acerto por concurso, prêmios estimados
 * e a distribuição de repetidas em relação ao concurso anterior.
 */
export function backtestFechamento(opts: BacktestFechamentoOptions): BacktestFechamentoResult {
  const { apostas, resultados, premios = PREMIOS_LOTOFACIL } = opts;
  const k = opts.k ?? apostas[0]?.length ?? 15;
  const faixasPremio = opts.faixasPremio ?? [11, 12, 13, 14, 15];
  const dezenasBase = opts.dezenasBase ?? 15;
  const precoBase = opts.precoBase ?? PRECO_APOSTA_15;
  const n = resultados.length;
  const distribuicao = new Array<number>(Math.max(16, k + 1)).fill(0);
  const repetidasDist = new Array<number>(Math.max(16, k + 1)).fill(0);
  const faixas = faixasPremio.map(a => ({ acertos: a, concursos: 0, percentual: 0 }));
  const detalhes: BacktestFechamentoResult['melhoresConcursos'] = [];

  let somaMelhor = 0;
  let somaPremio = 0;
  let anterior: Set<number> | null = null;
  let concursosComRepetidas = 0;

  for (const resultado of resultados) {
    const draw = new Set(resultado.numeros);
    let melhor = 0;
    let melhorAposta: number[] = [];
    let premioTotal = 0;

    for (const aposta of apostas) {
      let acertos = 0;
      for (const numero of aposta) {
        if (draw.has(numero)) acertos++;
      }
      if (acertos > melhor) {
        melhor = acertos;
        melhorAposta = aposta;
      }
      premioTotal += premios[acertos] ?? 0;
    }

    let repetidas = 0;
    if (anterior) {
      for (const numero of resultado.numeros) {
        if (anterior.has(numero)) repetidas++;
      }
      repetidasDist[repetidas]++;
      concursosComRepetidas++;
    }

    distribuicao[melhor]++;
    somaMelhor += melhor;
    somaPremio += premioTotal;
    for (const faixa of faixas) {
      if (melhor >= faixa.acertos) faixa.concursos++;
    }
    detalhes.push({
      concurso: resultado.concurso,
      melhorAcerto: melhor,
      premio: premioTotal,
      repetidas,
      aposta: melhorAposta,
    });
    anterior = draw;
  }

  const custoTotal = relatorioCusto(apostas, k, dezenasBase, precoBase).custoTotal;
  const premioMedio = n > 0 ? somaPremio / n : 0;

  return {
    totalConcursos: n,
    mediaMelhorAcerto: n > 0 ? somaMelhor / n : 0,
    distribuicaoMelhorAcerto: distribuicao,
    faixas: faixas.map(f => ({
      ...f,
      percentual: n > 0 ? (100 * f.concursos) / n : 0,
    })),
    premioMedio,
    custoTotal,
    roiMedio: custoTotal > 0 ? (premioMedio - custoTotal) / custoTotal : 0,
    melhoresConcursos: [...detalhes]
      .sort((a, b) => b.melhorAcerto - a.melhorAcerto || b.premio - a.premio)
      .slice(0, 5),
    repetidasDistribuicao: repetidasDist
      .map((concursos, repetidas) => ({
        repetidas,
        concursos,
        percentual: concursosComRepetidas > 0 ? (100 * concursos) / concursosComRepetidas : 0,
      }))
      .filter(x => x.concursos > 0),
  };
}

// ============================================================================
// 5. CACHE DE FECHAMENTOS (localStorage)
// ============================================================================

const CACHE_PREFIX = 'fechamento_';

export interface CacheFechamentoEntry {
  parametros: { v: number; k: number; t: number; maxApostas: number; seed: number; otimizado: boolean };
  apostas: number[][];
  cobertura: VerificarCoberturaResult;
  geradoEm: string;
}

export function cacheObter(chave: string): CacheFechamentoEntry | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(`${CACHE_PREFIX}${chave}`);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch { return null; }
}

export function cacheSalvar(chave: string, entry: CacheFechamentoEntry): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(`${CACHE_PREFIX}${chave}`, JSON.stringify(entry));
  } catch { /* storage cheio ou bloqueado */ }
}

export function cacheLimpar(): void {
  if (typeof window === 'undefined') return;
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith(CACHE_PREFIX)) {
      localStorage.removeItem(key);
      i--;
    }
  }
}

export function gerarChaveCache(opts: { v: number; k: number; t: number; maxApostas: number; seed: number; otimizado: boolean; fixos?: number[]; excluidos?: number[] }): string {
  const parts = [
    'v' + opts.v,
    'k' + opts.k,
    't' + opts.t,
    'ma' + opts.maxApostas,
    's' + opts.seed,
    'o' + (opts.otimizado ? 1 : 0),
    'fx' + (opts.fixos?.join(',') || '-'),
    'ex' + (opts.excluidos?.join(',') || '-'),
  ];
  return parts.join('_');
}

// ============================================================================
// 8. EXPORTAÇÃO CSV COM METADADOS
// ============================================================================

export interface ExportacaoFechamentoCSV {
  conteudo: string;
  nomeArquivo: string;
  mimeType: string;
}

export function exportarFechamentoCSV(
  apostas: number[][],
  universo: number[],
  k: number,
  t: number,
  cobertura: VerificarCoberturaResult,
  custo: RelatorioCustoResult,
  parametrosAdicionais?: Record<string, string | number>,
): ExportacaoFechamentoCSV {
  const linhas: string[] = [];

  // Cabeçalho com metadados
  const meta: Record<string, string | number> = {
    geradoEm: new Date().toISOString(),
    loteria: 'Lotofacil',
    universo: universo.length,
    k,
    t,
    garantiaPercentual: cobertura.garantiaPercentual,
    totalApostas: apostas.length,
    custoTotal: custo.custoTotal,
    precoPorJogo: custo.precoPorJogo,
    ...parametrosAdicionais,
  };

  linhas.push('# METADADOS DO FECHAMENTO COMBINATÓRIO');
  for (const [chave, valor] of Object.entries(meta)) {
    linhas.push(`# ${chave}: ${valor}`);
  }
  linhas.push('#');
  linhas.push('# APOSTAS (N1,N2,...,Nk)');
  linhas.push('N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15');

  for (const aposta of apostas) {
    linhas.push(aposta.join(','));
  }

  const nomeArquivo = `fechamento_lotofacil_k${k}_t${t}_${new Date().toISOString().slice(0, 10)}.csv`;

  return {
    conteudo: linhas.join('\n'),
    nomeArquivo,
    mimeType: 'text/csv; charset=utf-8',
  };
}