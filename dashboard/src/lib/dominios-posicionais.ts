/**
 * Contagem e geração exata de jogos com domínios posicionais.
 *
 * Um jogo é uma sequência crescente x1 < x2 < ... < xk. Cada posição j pode
 * ter um domínio D_j (números permitidos). Além disso:
 *   - `fixos` são obrigatórios e não podem ser pulados;
 *   - `excluidos` não podem aparecer;
 *   - `fixosPosicoes` restringe um número fixo a certas posições;
 *   - `excluidosPosicoes` proíbe um número em certas posições.
 *
 * O DP abaixo conta e amostra exatamente esse conjunto, sem rejection sampling.
 * Complexidade O(k·N²), com N <= 100 nas loterias suportadas.
 */

export interface DominiosPosicionaisOptions {
  totalNumeros: number;
  numerosPorJogo: number;
  numeroMinimo: number;
  fixos?: number[];
  excluidos?: number[];
  dominios?: Array<number[] | null | undefined>;
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
}

export interface ContextoDominios {
  total: number;
  /** Posições (1-based) em que nenhuma sequência viável consegue passar. */
  posicoesSemCandidato: number[];
  /** Mensagem curta para a UI quando total = 0. */
  detalhe: string;
  /** Sorteia um jogo uniforme entre os válidos. Devolve null se total = 0. */
  gerar(rand: () => number): number[] | null;
}

const LIMITE_CONTAGEM = Number.MAX_SAFE_INTEGER;

function normalizarSet(nums?: number[]): Set<number> {
  return new Set((nums ?? []).filter(n => Number.isInteger(n)));
}

function nextFixed(last: number, fixos: number[]): number | null {
  // fixos está ordenado; N <= 100, então a busca linear é irrelevante.
  for (const f of fixos) if (f > last) return f;
  return null;
}

function preparar(opts: DominiosPosicionaisOptions): {
  K: number;
  min: number;
  max: number;
  none: number;
  fixos: number[];
  ways: number[][];
  allowed: (pos: number, x: number) => boolean;
} {
  const N = Math.max(0, Math.trunc(opts.totalNumeros));
  const K = Math.max(0, Math.trunc(opts.numerosPorJogo));
  const min = Math.trunc(opts.numeroMinimo);
  const max = min + N - 1;

  const fixosSet = normalizarSet(opts.fixos);
  const excluidosSet = normalizarSet(opts.excluidos);
  // Fixo vence exclusão (mesma regra de normalizarConstraints no gerador).
  const excluidosEfetivos = new Set([...excluidosSet].filter(n => !fixosSet.has(n)));
  const fixos = [...fixosSet]
    .filter(n => n >= min && n <= max)
    .sort((a, b) => a - b);

  const dominios: Array<Set<number> | null> = [];
  for (let j = 0; j < K; j++) {
    const raw = opts.dominios?.[j];
    if (!raw || raw.length === 0) {
      dominios.push(null);
      continue;
    }
    const set = new Set(
      raw.filter(n => Number.isInteger(n) && n >= min && n <= max),
    );
    dominios.push(set.size > 0 ? set : null);
  }

  const fixosPos = new Map<number, Set<number>>();
  for (const [k, v] of Object.entries(opts.fixosPosicoes ?? {})) {
    const n = Number(k);
    if (Number.isInteger(n) && Array.isArray(v) && v.length > 0) {
      fixosPos.set(n, new Set(v.filter(p => Number.isInteger(p) && p >= 1 && p <= K)));
    }
  }
  const excluidosPos = new Map<number, Set<number>>();
  for (const [k, v] of Object.entries(opts.excluidosPosicoes ?? {})) {
    const n = Number(k);
    if (Number.isInteger(n) && Array.isArray(v) && v.length > 0) {
      excluidosPos.set(n, new Set(v.filter(p => Number.isInteger(p) && p >= 1 && p <= K)));
    }
  }

  const allowed = (pos: number, x: number): boolean => {
    if (x < min || x > max) return false;
    if (excluidosEfetivos.has(x)) return false;
    const dom = dominios[pos - 1];
    if (dom && !dom.has(x)) return false;
    const fp = fixosPos.get(x);
    if (fp && fp.size > 0 && !fp.has(pos)) return false;
    const ep = excluidosPos.get(x);
    if (ep && ep.size > 0 && ep.has(pos)) return false;
    return true;
  };

  // ways[pos][last] = quantas sequências completam as posições `pos..K`
  // dado que o último número escolhido foi `last`. O sentinela `none` fica
  // abaixo do mínimo (Lotomania começa em 0, então 0 não pode ser o sentinela).
  const none = min - 1;
  const lastCount = max - none + 1;
  const idx = (last: number) => last - none;
  const ways: number[][] = Array.from({ length: K + 2 }, () => new Array(lastCount).fill(0));
  for (let last = none; last <= max; last++) {
    ways[K + 1][idx(last)] = nextFixed(last, fixos) === null ? 1 : 0;
  }

  for (let pos = K; pos >= 1; pos--) {
    for (let last = none; last <= max; last++) {
      const f = nextFixed(last, fixos);
      const upper = Math.min(max, f ?? max);
      let soma = 0;
      for (let x = last + 1; x <= upper; x++) {
        if (!allowed(pos, x)) continue;
        const w = ways[pos + 1][idx(x)];
        if (w === 0) continue;
        soma += w;
        if (soma >= LIMITE_CONTAGEM) {
          soma = LIMITE_CONTAGEM;
          break;
        }
      }
      ways[pos][idx(last)] = soma;
    }
  }

  return { K, min, max, none, fixos, ways, allowed };
}

function diagnosticar(
  K: number,
  min: number,
  max: number,
  none: number,
  fixos: number[],
  ways: number[][],
  allowed: (pos: number, x: number) => boolean,
): { posicoesSemCandidato: number[]; detalhe: string } {
  if (ways[1][0] > 0) return { posicoesSemCandidato: [], detalhe: '' };
  const idx = (last: number) => last - none;

  // Diagnóstico local: na posição pos, x precisa ter pos-1 dezenas menores
  // disponíveis e K-pos maiores. Se nem essa faixa tem candidato permitido,
  // a posição é o gargalo (ex.: N7 entre os fixos 7 e 18, com 8–17 proibidos).
  const vazias: number[] = [];
  for (let pos = 1; pos <= K; pos++) {
    const lo = min + (pos - 1);
    const hi = max - (K - pos);
    let tem = false;
    for (let x = lo; x <= hi; x++) {
      if (allowed(pos, x)) { tem = true; break; }
    }
    if (!tem) vazias.push(pos);
  }

  // Segundo: segue o caminho de maior viabilidade até o primeiro ponto sem
  // candidato. Reportar todas as posições seguintes é ruído.
  const sem: number[] = vazias.length > 0 ? vazias.slice(0, 1) : [];
  if (sem.length === 0) {
    let pos = 1;
    let last = none;
    while (pos <= K) {
      const f = nextFixed(last, fixos);
      const upper = Math.min(max, f ?? max);
      let melhor = -1;
      let melhorPeso = 0;
      for (let x = last + 1; x <= upper; x++) {
        if (!allowed(pos, x)) continue;
        const w = ways[pos + 1][idx(x)];
        if (w > melhorPeso) {
          melhor = x;
          melhorPeso = w;
        }
      }
      if (melhor < 0) {
        sem.push(pos);
        break;
      }
      last = melhor;
      pos++;
    }
    if (sem.length === 0 && nextFixed(last, fixos) !== null) {
      // Chegou ao fim com fixo pendente: o último slot não comporta o fixo.
      sem.push(K);
    }
  }

  const fixosSemPosicao = fixos.filter(f => {
    for (let pos = 1; pos <= K; pos++) {
      if (allowed(pos, f)) return false;
    }
    return true;
  });

  const partes: string[] = [];
  if (sem.length > 0) partes.push(`sem candidato viável em N${sem.join(', N')}`);
  if (fixosSemPosicao.length > 0) partes.push(`fixos sem posição válida: ${fixosSemPosicao.join(', ')}`);
  if (partes.length === 0) {
    partes.push('as restrições combinadas não deixam nenhuma sequência crescente válida');
  }

  return {
    posicoesSemCandidato: sem,
    detalhe: `Nenhuma combinação válida: ${partes.join('; ')}.`,
  };
}

export function prepararDominios(opts: DominiosPosicionaisOptions): ContextoDominios {
  const { K, min, max, none, fixos, ways, allowed } = preparar(opts);
  const total = ways[1][0] ?? 0;
  const diag = diagnosticar(K, min, max, none, fixos, ways, allowed);
  const idx = (last: number) => last - none;

  const gerar = (rand: () => number): number[] | null => {
    if (total <= 0) return null;
    const jogo: number[] = [];
    let last = none;
    for (let pos = 1; pos <= K; pos++) {
      const f = nextFixed(last, fixos);
      const upper = Math.min(max, f ?? max);
      const candidatos: Array<{ x: number; w: number }> = [];
      let somaPesos = 0;
      for (let x = last + 1; x <= upper; x++) {
        if (!allowed(pos, x)) continue;
        const w = ways[pos + 1][idx(x)];
        if (w <= 0) continue;
        candidatos.push({ x, w });
        somaPesos += w;
      }
      if (candidatos.length === 0 || somaPesos <= 0) return null;
      let r = rand() * somaPesos;
      let escolhido = candidatos[candidatos.length - 1].x;
      for (const c of candidatos) {
        r -= c.w;
        if (r <= 0) {
          escolhido = c.x;
          break;
        }
      }
      jogo.push(escolhido);
      last = escolhido;
    }
    return jogo;
  };

  return {
    total,
    posicoesSemCandidato: diag.posicoesSemCandidato,
    detalhe: diag.detalhe,
    gerar,
  };
}

export function contarJogosComDominios(opts: DominiosPosicionaisOptions): {
  total: number;
  posicoesSemCandidato: number[];
  detalhe: string;
} {
  const ctx = prepararDominios(opts);
  return {
    total: ctx.total,
    posicoesSemCandidato: ctx.posicoesSemCandidato,
    detalhe: ctx.detalhe,
  };
}

export function gerarJogoComDominios(rand: () => number, opts: DominiosPosicionaisOptions): number[] | null {
  return prepararDominios(opts).gerar(rand);
}
