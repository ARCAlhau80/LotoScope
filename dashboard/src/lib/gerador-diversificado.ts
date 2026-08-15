export interface GeradorDiversificadoOptions {
  resultados: number[][];
  cicloDados?: Record<number, number>;
  nJogos?: number;
  seed?: number;
  fixos?: number[];
  excluidos?: number[];
  totalNumeros?: number;
  numerosPorJogo?: number;
  numeroMinimo?: number;
  primos?: number[];
}

export interface JogoGerado {
  numeros: number[];
  estrategia: string;
  soma: number;
  pares: number;
  impares: number;
  primos: number;
}

interface LP {
  totalNumeros: number;
  numerosPorJogo: number;
  numeroMinimo: number;
  numeroMaximo: number;
  primosSet: Set<number>;
}

function buildLP(opts: GeradorDiversificadoOptions): LP {
  const totalNumeros = opts.totalNumeros ?? 25;
  const numerosPorJogo = opts.numerosPorJogo ?? 15;
  const numeroMinimo = opts.numeroMinimo ?? 1;
  const primosList = opts.primos ?? [2, 3, 5, 7, 11, 13, 17, 19, 23];
  return {
    totalNumeros,
    numerosPorJogo,
    numeroMinimo,
    numeroMaximo: numeroMinimo + totalNumeros - 1,
    primosSet: new Set(primosList),
  };
}

function rng(seed?: number): () => number {
  let s = seed ?? Date.now() % 2147483647;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function sample<T>(arr: T[], k: number, rand: () => number): T[] {
  const copy = [...arr];
  const result: T[] = [];
  for (let i = 0; i < k && copy.length > 0; i++) {
    const idx = Math.floor(rand() * copy.length);
    result.push(copy[idx]);
    copy.splice(idx, 1);
  }
  return result;
}

function shuffle<T>(arr: T[], rand: () => number): T[] {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function sorted(nums: number[]): number[] {
  return [...nums].sort((a, b) => a - b);
}

function combinacoes(n: number, k: number): number {
  if (k < 0 || k > n) return 0;
  if (k === 0 || k === n) return 1;
  let res = 1;
  for (let i = 1; i <= k; i++) {
    res = (res * (n - k + i)) / i;
  }
  return Math.round(res);
}

function* gerarCombinacoes(pool: number[], k: number): Generator<number[]> {
  const n = pool.length;
  const indices = Array.from({ length: k }, (_, i) => i);

  while (true) {
    yield indices.map(i => pool[i]);

    let i = k - 1;
    while (i >= 0 && indices[i] === i + n - k) {
      i--;
    }
    if (i < 0) return;

    indices[i]++;
    for (let j = i + 1; j < k; j++) {
      indices[j] = indices[j - 1] + 1;
    }
  }
}

export function calcularEstimativaCombinacoes(fixos?: number[], excluidos?: number[], totalNumeros = 25, numerosPorJogo = 15, numeroMinimo = 1): number {
  const { fixosNorm, excluidosNorm } = normalizarConstraints(fixos, excluidos, totalNumeros, numeroMinimo);
  const totalDisp = totalNumeros - fixosNorm.length - excluidosNorm.length;
  const escolher = numerosPorJogo - fixosNorm.length;
  return combinacoes(totalDisp, escolher);
}

function aplicarConstraints(jogo: number[], rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, excluidosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const jogoSet = new Set(jogo);
  for (const e of excluidosNorm) jogoSet.delete(e);
  for (const f of fixosNorm) jogoSet.add(f);
  const faltam = lp.numerosPorJogo - jogoSet.size;
  if (faltam > 0) {
    const pool = disponiveis.filter(n => !jogoSet.has(n));
    const extras = sample(pool, Math.min(faltam, pool.length), rand);
    for (const n of extras) jogoSet.add(n);
  }
  return sorted([...jogoSet]);
}

function normalizarConstraints(fixos?: number[], excluidos?: number[], totalNumeros = 25, numeroMinimo = 1): { fixosNorm: number[]; excluidosNorm: number[]; disponiveis: number[] } {
  const numeroMaximo = numeroMinimo + totalNumeros - 1;
  const fixosNorm = [...new Set((fixos ?? []).filter(n => n >= numeroMinimo && n <= numeroMaximo))];
  const excluidosNorm = [...new Set((excluidos ?? []).filter(n => n >= numeroMinimo && n <= numeroMaximo))];
  const excluidosEfetivos = excluidosNorm.filter(n => !fixosNorm.includes(n));
  const disponiveis = Array.from({ length: totalNumeros }, (_, i) => i + numeroMinimo).filter(n => !excluidosEfetivos.includes(n));
  return { fixosNorm, excluidosNorm: excluidosEfetivos, disponiveis };
}

function completarJogo(selecionados: number[], fixos: number[], disponiveis: number[], rand: () => number, numerosPorJogo: number): number[] {
  const jogoSet = new Set([...fixos, ...selecionados]);
  const faltam = numerosPorJogo - jogoSet.size;
  if (faltam > 0) {
    const pool = disponiveis.filter(n => !jogoSet.has(n));
    if (pool.length < faltam) {
      return sorted([...jogoSet]);
    }
    const extras = sample(pool, faltam, rand);
    for (const n of extras) jogoSet.add(n);
  }
  return sorted([...jogoSet]);
}

function gerarAleatorio(rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const selecionados = sample(disponiveis.filter(n => !fixosNorm.includes(n)), Math.max(0, lp.numerosPorJogo - fixosNorm.length), rand);
  return completarJogo(selecionados, fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarAtraso(ultimosConcursos: number[][], rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const todosDisponiveis = new Set(disponiveis);
  const recentes = new Set<number>();
  for (const c of ultimosConcursos) {
    for (const n of c) if (todosDisponiveis.has(n)) recentes.add(n);
  }
  let atrasados = [...todosDisponiveis].filter(n => !recentes.has(n) && !fixosNorm.includes(n));
  if (atrasados.length < Math.max(0, lp.numerosPorJogo - fixosNorm.length)) {
    atrasados = [...todosDisponiveis].filter(n => !fixosNorm.includes(n));
  }
  const maxAtrasados = Math.min(
    Math.floor(rand() * Math.max(1, Math.ceil(lp.numerosPorJogo / 3))) + Math.max(1, Math.floor(lp.numerosPorJogo * 0.5)),
    Math.max(0, lp.numerosPorJogo - fixosNorm.length),
    atrasados.length
  );
  const selecionados = sample(atrasados, maxAtrasados, rand);
  return completarJogo(selecionados, fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarHot(ultimosConcursos: number[][], nHot: number, rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const todosDisponiveis = new Set(disponiveis);
  const hot = new Set<number>();
  const recentes = ultimosConcursos.slice(-3);
  for (const c of recentes) {
    for (const n of c) if (todosDisponiveis.has(n)) hot.add(n);
  }
  const hotList = [...hot].filter(n => !fixosNorm.includes(n));
  const nFixosHot = Math.min(nHot, hotList.length, Math.max(0, lp.numerosPorJogo - fixosNorm.length));
  const selecionados = sample(hotList, nFixosHot, rand);
  return completarJogo(selecionados, fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarPersistenciaCategoria(ultimos2: number[][], categoria: string, rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const meio = lp.numeroMinimo + Math.floor((lp.totalNumeros - 1) / 2);
  let catFunc: (n: number) => boolean;
  switch (categoria) {
    case 'impares':
      catFunc = n => n % 2 === 1;
      break;
    case 'primos':
      catFunc = n => lp.primosSet.has(n);
      break;
    case 'baixos':
      catFunc = n => n <= meio;
      break;
    case 'altos':
      catFunc = n => n > meio;
      break;
    case 'pares':
    default:
      catFunc = n => n % 2 === 0;
      break;
  }

  if (ultimos2.length < 2) {
    return gerarAleatorio(rand, lp, fixos, excluidos);
  }

  const catAnterior = ultimos2[0].filter(n => disponiveis.includes(n) && catFunc(n));
  const catAtual = ultimos2[1].filter(n => disponiveis.includes(n) && catFunc(n));
  const taxa = catAnterior.length > 0 && catAtual.length > 0
    ? catAnterior.filter(n => catAtual.includes(n)).length / Math.max(catAnterior.length, catAtual.length)
    : 0.5;

  const fixosForaCategoria = fixosNorm.filter(n => !catFunc(n));

  const poolCat = disponiveis.filter(n => !fixosNorm.includes(n) && catFunc(n));
  const outros = disponiveis.filter(n => !fixosNorm.includes(n) && !catFunc(n));

  const vagasCategoria = Math.max(0, lp.numerosPorJogo - fixosForaCategoria.length);
  const nCat = taxa > 0.5
    ? Math.min(Math.floor(rand() * 4) + Math.ceil(lp.numerosPorJogo * 0.45), poolCat.length, vagasCategoria)
    : Math.min(Math.floor(rand() * 3) + Math.ceil(lp.numerosPorJogo * 0.25), poolCat.length, vagasCategoria);

  const selecionadosCat = sample(poolCat, nCat, rand);
  const selecionadosOutros = sample(outros, Math.max(0, lp.numerosPorJogo - fixosNorm.length - selecionadosCat.length), rand);
  return completarJogo([...selecionadosCat, ...selecionadosOutros], fixosNorm, disponiveis, rand, lp.numerosPorJogo);
}

function gerarCiclo(cicloDados: Record<number, number> | undefined, rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): number[] {
  const { fixosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  if (!cicloDados) {
    return gerarAleatorio(rand, lp, fixos, excluidos);
  }

  const pesos: Record<number, number> = {};
  for (const n of disponiveis) {
    if (fixosNorm.includes(n)) {
      pesos[n] = 100.0;
      continue;
    }
    const qtd = cicloDados[n] ?? 0;
    if (qtd === 0) pesos[n] = 4.0;
    else if (qtd <= 1) pesos[n] = 2.0;
    else pesos[n] = 1.0;
  }

  const totalPeso = Object.values(pesos).reduce((a, b) => a + b, 0);
  let jogo: number[] = [];
  let tentativas = 0;
  while (new Set(jogo).size < lp.numerosPorJogo && tentativas < 100) {
    jogo = [];
    while (jogo.length < lp.numerosPorJogo) {
      let acc = 0;
      const r = rand() * totalPeso;
      for (const n of disponiveis) {
        acc += pesos[n];
        if (acc >= r) {
          jogo.push(n);
          break;
        }
      }
    }
    tentativas++;
  }

  if (new Set(jogo).size < lp.numerosPorJogo) {
    return gerarAleatorio(rand, lp, fixos, excluidos);
  }

  return sorted([...new Set(jogo)]);
}

function mediaIntersecoes(jogo: number[], jogos: number[][]): number {
  if (jogos.length === 0) return 0;
  const s = new Set(jogo);
  const soma = jogos.reduce((acc, ex) => acc + [...s].filter(n => ex.includes(n)).length, 0);
  return soma / jogos.length;
}

function garantirCobertura(jogos: number[][], rand: () => number, lp: LP, fixos: number[] = [], excluidos: number[] = []): number[][] {
  const cobertura = new Set(jogos.flat());
  const faltando = Array.from({ length: lp.totalNumeros }, (_, i) => i + lp.numeroMinimo)
    .filter(n => !cobertura.has(n) && !excluidos.includes(n));
  if (faltando.length === 0 || jogos.length < 3) return jogos;

  const result = jogos.map(j => [...j]);
  for (const numFaltando of faltando) {
    let melhorIdx = 0;
    let melhorScore = -1;
    for (let idx = 0; idx < result.length; idx++) {
      const outras = result.filter((_, i) => i !== idx);
      const score = mediaIntersecoes(result[idx], outras);
      if (score > melhorScore) {
        melhorScore = score;
        melhorIdx = idx;
      }
    }

    const jogo = result[melhorIdx];
    const candidatosTroca = jogo
      .map((n, pos) => ({ n, pos }))
      .filter(({ n }) => !fixos.includes(n) && result.filter(j => j.includes(n)).length > 1)
      .sort(() => rand() - 0.5);

    let trocou = false;
    for (const { pos } of candidatosTroca) {
      const novoJogo = sorted([...jogo.slice(0, pos), ...jogo.slice(pos + 1), numFaltando]);
      if (!excluidos.includes(numFaltando) && !result.some(j => JSON.stringify(j) === JSON.stringify(novoJogo))) {
        result[melhorIdx] = novoJogo;
        trocou = true;
        break;
      }
    }

    if (!trocou) {
      const candidatosTroca2 = jogo
        .map((n, pos) => ({ n, pos }))
        .filter(({ n }) => !fixos.includes(n))
        .sort(() => rand() - 0.5);
      for (const { pos } of candidatosTroca2) {
        const novoJogo = sorted([...jogo.slice(0, pos), ...jogo.slice(pos + 1), numFaltando]);
        if (!excluidos.includes(numFaltando) && !result.some(j => JSON.stringify(j) === JSON.stringify(novoJogo))) {
          result[melhorIdx] = novoJogo;
          break;
        }
      }
    }
  }

  return result;
}

export function gerarJogosDiversificados(options: GeradorDiversificadoOptions): JogoGerado[] {
  const { resultados, cicloDados, nJogos = 5, seed, fixos, excluidos } = options;
  const lp = buildLP(options);
  const rand = rng(seed);
  const { fixosNorm, excluidosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);

  if (fixosNorm.length > lp.numerosPorJogo) {
    throw new Error(`Não é possível fixar mais de ${lp.numerosPorJogo} números. Recebido: ${fixosNorm.length}`);
  }
  if (fixosNorm.length + disponiveis.filter(n => !fixosNorm.includes(n)).length < lp.numerosPorJogo) {
    throw new Error(`Não há números suficientes disponíveis para completar ${lp.numerosPorJogo} dezenas com os exclusões/fixos informados.`);
  }

  if (nJogos === 0) {
    return gerarTodasAsCombinacoes(rand, lp, fixos, excluidos);
  }

  const count = nJogos;

  if (resultados.length === 0) {
    return Array.from({ length: count }, () => {
      const numeros = gerarAleatorio(rand, lp, fixos, excluidos);
      return buildJogo(numeros, 'aleatorio', lp.primosSet);
    });
  }

  const ultimos = resultados.slice(-5);
  const ultimos3 = resultados.slice(-3);
  const ultimos2 = resultados.slice(-2);

  const baseHot = Math.max(2, Math.floor(lp.numerosPorJogo / 2));
  const minOverlap = Math.max(0, 2 * lp.numerosPorJogo - lp.totalNumeros);
  const maxIntersecao = Math.max(Math.ceil(lp.numerosPorJogo * 0.6), minOverlap + 2);

  const estrategias: { nome: string; fn: () => number[] }[] = [
    { nome: 'atraso', fn: () => gerarAtraso(ultimos, rand, lp, fixos, excluidos) },
    { nome: 'hot7-9', fn: () => gerarHot(ultimos3, Math.min(Math.floor(rand() * 3) + baseHot, lp.numerosPorJogo), rand, lp, fixos, excluidos) },
    { nome: 'persistencia', fn: () => gerarPersistenciaCategoria(ultimos2, shuffle(['pares', 'impares', 'primos'], rand)[0], rand, lp, fixos, excluidos) },
    { nome: 'aleatorio', fn: () => gerarAleatorio(rand, lp, fixos, excluidos) },
    { nome: 'ciclo', fn: () => gerarCiclo(cicloDados, rand, lp, fixos, excluidos) },
  ];

  const jogos: number[][] = [];
  const nomes: string[] = [];
  let tentativa = 0;
  const maxTentativas = count * 300;

  while (jogos.length < count && tentativa < maxTentativas) {
    tentativa++;
    const estrategia = estrategias[jogos.length % estrategias.length];
    const jogoBruto = estrategia.fn();
    const jogo = aplicarConstraints(jogoBruto, rand, lp, fixos, excluidos);

    if (jogo.length !== lp.numerosPorJogo || jogos.some(ex => JSON.stringify(ex) === JSON.stringify(jogo))) {
      continue;
    }

    if (jogos.length > 0) {
      const inter = mediaIntersecoes(jogo, jogos);
      if (inter > maxIntersecao) continue;
    }

    jogos.push(jogo);
    nomes.push(estrategia.nome);
  }

  while (jogos.length < count) {
    const jogoBruto = gerarAleatorio(rand, lp, fixos, excluidos);
    const jogo = aplicarConstraints(jogoBruto, rand, lp, fixos, excluidos);
    if (jogo.length === lp.numerosPorJogo && !jogos.some(ex => JSON.stringify(ex) === JSON.stringify(jogo))) {
      jogos.push(jogo);
      nomes.push('aleatorio');
    }
  }

  const jogosFinais = garantirCobertura(jogos, rand, lp, fixosNorm, excluidosNorm);

  const jogosValidados = jogosFinais.map(j => aplicarConstraints(j, rand, lp, fixos, excluidos));

  return jogosValidados.map((numeros, i) => buildJogo(numeros, nomes[i] ?? 'aleatorio', lp.primosSet));
}

function gerarTodasAsCombinacoes(rand: () => number, lp: LP, fixos?: number[], excluidos?: number[]): JogoGerado[] {
  const { fixosNorm, excluidosNorm, disponiveis } = normalizarConstraints(fixos, excluidos, lp.totalNumeros, lp.numeroMinimo);
  const pool = disponiveis.filter(n => !fixosNorm.includes(n));
  const k = lp.numerosPorJogo - fixosNorm.length;

  const todas: number[][] = [];
  for (const combo of gerarCombinacoes(pool, k)) {
    todas.push(sorted([...fixosNorm, ...combo]));
  }

  for (let i = todas.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [todas[i], todas[j]] = [todas[j], todas[i]];
  }

  return todas.map(numeros => buildJogo(numeros, 'todas-combinacoes', lp.primosSet));
}

function buildJogo(numeros: number[], estrategia: string, primosSet: Set<number>): JogoGerado {
  return {
    numeros,
    estrategia,
    soma: numeros.reduce((a, b) => a + b, 0),
    pares: numeros.filter(n => n % 2 === 0).length,
    impares: numeros.filter(n => n % 2 === 1).length,
    primos: numeros.filter(n => primosSet.has(n)).length,
  };
}

export function calcularCobertura(jogos: number[][], totalNumeros: number = 25, numeroMinimo: number = 1): { total: number; frequencia: Record<number, number> } {
  const freq: Record<number, number> = {};
  for (let i = numeroMinimo; i < numeroMinimo + totalNumeros; i++) freq[i] = 0;
  for (const j of jogos) {
    for (const n of j) freq[n] = (freq[n] ?? 0) + 1;
  }
  const total = Object.values(freq).filter(v => v > 0).length;
  return { total, frequencia: freq };
}

export function calcularEstatisticasJogos(jogos: JogoGerado[], totalNumeros: number = 25, numeroMinimo: number = 1) {
  const todasEstrategias = jogos.map(j => j.estrategia);
  const estrategiaCounts = todasEstrategias.reduce((acc, e) => {
    acc[e] = (acc[e] ?? 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const cobertura = calcularCobertura(jogos.map(j => j.numeros), totalNumeros, numeroMinimo);

  return {
    total: jogos.length,
    cobertura: cobertura.total,
    frequencia: cobertura.frequencia,
    estrategias: estrategiaCounts,
  };
}
