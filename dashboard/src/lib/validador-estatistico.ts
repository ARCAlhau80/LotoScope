import { carregarResultados } from './database';
import { getLotteryConfig } from './lottery-config';
import type {
  ValidadorBadge,
  ValidadorEstatisticoData,
  ValidadorGrupo,
  ValidadorLinhasVazias,
  ValidadorNumero,
  ValidadorRepeticao,
  ValidadorTeste,
} from './validador-tipos';

const MIN_EXPECTED = 5;

/* ------------------------------------------------------------------ */
/* Matemática                                                          */
/* ------------------------------------------------------------------ */

/** log(Γ(x)) — Lanczos. */
function logGamma(x: number): number {
  const g = 7;
  const c = [
    0.99999999999980993,
    676.5203681218851,
    -1259.1392167224028,
    771.32342877765313,
    -176.61502916214059,
    12.507343278686905,
    -0.13857109526572012,
    9.9843695780195716e-6,
    1.5056327351493116e-7,
  ];
  if (x < 0.5) {
    return Math.log(Math.PI / Math.sin(Math.PI * x)) - logGamma(1 - x);
  }
  x -= 1;
  let a = c[0];
  const t = x + g + 0.5;
  for (let i = 1; i < g + 2; i++) a += c[i] / (x + i);
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}

/** log(C(n, k)); retorna -Infinity para combinações inválidas. */
function logComb(n: number, k: number): number {
  if (k < 0 || k > n || n < 0) return -Infinity;
  return logGamma(n + 1) - logGamma(k + 1) - logGamma(n - k + 1);
}

function logAdd(a: number, b: number): number {
  if (!Number.isFinite(a)) return b;
  if (!Number.isFinite(b)) return a;
  const max = Math.max(a, b);
  return max + Math.log(Math.exp(a - max) + Math.exp(b - max));
}

/** Série para P(a, x). */
function gammaSeries(a: number, x: number): number {
  let sum = 1 / a;
  let term = sum;
  for (let n = 1; n < 500; n++) {
    term *= x / (a + n);
    sum += term;
    if (Math.abs(term) < Math.abs(sum) * 1e-14) break;
  }
  return sum * Math.exp(-x + a * Math.log(x) - logGamma(a));
}

/** Fração continuada para Q(a, x). */
function gammaContinuedFraction(a: number, x: number): number {
  const tiny = 1e-300;
  let b = x + 1 - a;
  let c = 1 / tiny;
  let d = 1 / b;
  let h = d;
  for (let i = 1; i < 500; i++) {
    const an = -i * (i - a);
    b += 2;
    d = an * d + b;
    if (Math.abs(d) < tiny) d = tiny;
    c = b + an / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1 / d;
    const del = d * c;
    h *= del;
    if (Math.abs(del - 1) < 1e-14) break;
  }
  return Math.exp(-x + a * Math.log(x) - logGamma(a)) * h;
}

/** Q(a, x) = 1 - P(a, x). */
function gammaQ(a: number, x: number): number {
  if (x <= 0) return 1;
  if (x < a + 1) return 1 - gammaSeries(a, x);
  return gammaContinuedFraction(a, x);
}

/** p-valor de chi-quadrado. */
function chiSquareP(chi2: number, df: number): number {
  if (!Number.isFinite(chi2) || chi2 <= 0 || df <= 0) return 1;
  return Math.max(0, Math.min(1, gammaQ(df / 2, chi2 / 2)));
}

function zValue(observado: number, esperado: number): number {
  return esperado > 0 ? (observado - esperado) / Math.sqrt(esperado) : 0;
}

/**
 * Chi-quadrado com agrupamento de categorias de esperado baixo.
 * Categorias com esperado < 5 são unidas em um único grupo "outros".
 */
function testarChi2(
  observado: number[],
  esperado: number[],
  nome: string,
  id: string,
): ValidadorTeste {
  const categorias: { o: number; e: number }[] = [];
  let outrosO = 0;
  let outrosE = 0;
  for (let i = 0; i < esperado.length; i++) {
    if (esperado[i] >= MIN_EXPECTED) {
      categorias.push({ o: observado[i] ?? 0, e: esperado[i] });
    } else {
      outrosO += observado[i] ?? 0;
      outrosE += esperado[i] ?? 0;
    }
  }
  if (outrosE > 0) categorias.push({ o: outrosO, e: outrosE });

  let chi2 = 0;
  for (const c of categorias) {
    if (c.e > 0) chi2 += ((c.o - c.e) ** 2) / c.e;
  }
  const df = Math.max(0, categorias.length - 1);
  const p = df > 0 ? chiSquareP(chi2, df) : 1;
  return {
    id,
    nome,
    chi2,
    df,
    p,
    pAjustado: p,
    significativoBruto: false,
    significativoAjustado: false,
    detalhe: outrosE > 0 ? 'Categorias com esperado < 5 foram agrupadas.' : undefined,
  };
}

/* ------------------------------------------------------------------ */
/* Geometria da grade                                                  */
/* ------------------------------------------------------------------ */

function colunasDaGrade(total: number): 5 | 8 | 10 {
  return total <= 25 ? 5 : total <= 31 ? 8 : 10;
}

function gruposDaGrade(
  total: number,
  numeroMinimo: number,
  colunas: number,
  unidade: 'linha' | 'coluna',
): ValidadorGrupo[] {
  const mapa = new Map<number, number[]>();
  for (let i = 0; i < total; i++) {
    const numero = numeroMinimo + i;
    const id = unidade === 'coluna' ? (i % colunas) + 1 : Math.floor(i / colunas) + 1;
    const lista = mapa.get(id);
    if (lista) lista.push(numero);
    else mapa.set(id, [numero]);
  }
  return [...mapa.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([id, dezenas]) => ({
      id,
      rotulo: `${unidade === 'coluna' ? 'C' : 'L'}${id}`,
      dezenas,
      observado: 0,
      esperado: 0,
      z: 0,
    }));
}

/** P(nenhuma linha vazia) por DP exata em log-espaço. */
function probabilidadeNenhumaLinhaVazia(
  grupos: ValidadorGrupo[],
  total: number,
  k: number,
): number {
  if (grupos.length > k) return 0;
  let dp = new Array<number>(k + 1).fill(-Infinity);
  dp[0] = 0;
  for (const grupo of grupos) {
    const size = grupo.dezenas.length;
    const next = new Array<number>(k + 1).fill(-Infinity);
    for (let usado = 0; usado <= k; usado++) {
      if (!Number.isFinite(dp[usado])) continue;
      const maxX = Math.min(size, k - usado);
      for (let x = 1; x <= maxX; x++) {
        const valor = dp[usado] + logComb(size, x);
        next[usado + x] = logAdd(next[usado + x], valor);
      }
    }
    dp = next;
  }
  if (!Number.isFinite(dp[k])) return 0;
  return Math.exp(dp[k] - logComb(total, k));
}

/* ------------------------------------------------------------------ */
/* Validação                                                           */
/* ------------------------------------------------------------------ */

export async function validarEstatisticamente(args: {
  loteria: string;
  janela?: number;
  badgeJanela?: number;
  concurso?: number;
}): Promise<ValidadorEstatisticoData> {
  const cfg = getLotteryConfig(args.loteria);
  const todas = await carregarResultados(cfg.id);
  if (todas.length === 0) throw new Error('Sem resultados cadastrados para esta loteria.');

  let historico = todas;
  if (args.concurso !== undefined) {
    const idx = todas.findIndex(r => r.concurso === args.concurso);
    if (idx < 0) throw new Error(`Concurso ${args.concurso} não encontrado.`);
    historico = todas.slice(0, idx + 1);
  }

  const totalSorteios = todas.length;
  const total = cfg.total_numeros;
  const numeroMinimo = cfg.numero_minimo;
  const k = cfg.numeros_por_jogo;
  const colunasGrade = colunasDaGrade(total);

  const janelaSolicitada =
    args.janela !== undefined && args.janela > 0 ? Math.trunc(args.janela) : null;
  const janelaEfetiva = Math.max(
    1,
    Math.min(janelaSolicitada ?? historico.length, historico.length),
  );
  const inicio = Math.max(0, historico.length - janelaEfetiva);
  const analise = historico.slice(inicio);
  const badgeJanela = Math.max(2, Math.min(20, Math.trunc(args.badgeJanela ?? 7)));
  const concursoBase = historico[historico.length - 1]?.concurso ?? null;

  /* ---------------------------------------------------------------- */
  /* Frequência por dezena                                            */
  /* ---------------------------------------------------------------- */
  const contagemNumero = new Map<number, number>();
  for (let n = numeroMinimo; n < numeroMinimo + total; n++) contagemNumero.set(n, 0);
  let totalAcertos = 0;
  for (const sorteio of analise) {
    for (const n of sorteio.numeros) {
      contagemNumero.set(n, (contagemNumero.get(n) ?? 0) + 1);
      totalAcertos++;
    }
  }
  const esperadoPorNumero = (analise.length * k) / total;
  const numeros: ValidadorNumero[] = [];
  for (let n = numeroMinimo; n < numeroMinimo + total; n++) {
    const observado = contagemNumero.get(n) ?? 0;
    numeros.push({
      numero: n,
      observado,
      esperado: esperadoPorNumero,
      z: zValue(observado, esperadoPorNumero),
    });
  }
  const testeUniformidade = testarChi2(
    numeros.map(n => n.observado),
    numeros.map(n => n.esperado),
    'Uniformidade das dezenas',
    'uniformidade',
  );

  /* ---------------------------------------------------------------- */
  /* Linhas e colunas                                                 */
  /* ---------------------------------------------------------------- */
  const linhas = gruposDaGrade(total, numeroMinimo, colunasGrade, 'linha');
  const colunas = gruposDaGrade(total, numeroMinimo, colunasGrade, 'coluna');
  const linhaPorNumero = new Map<number, number>();
  const colunaPorNumero = new Map<number, number>();
  for (const g of linhas) for (const n of g.dezenas) linhaPorNumero.set(n, g.id);
  for (const g of colunas) for (const n of g.dezenas) colunaPorNumero.set(n, g.id);

  const contagemLinha = new Map<number, number>();
  const contagemColuna = new Map<number, number>();
  for (const g of linhas) contagemLinha.set(g.id, 0);
  for (const g of colunas) contagemColuna.set(g.id, 0);
  for (const sorteio of analise) {
    for (const n of sorteio.numeros) {
      const l = linhaPorNumero.get(n);
      const c = colunaPorNumero.get(n);
      if (l !== undefined) contagemLinha.set(l, (contagemLinha.get(l) ?? 0) + 1);
      if (c !== undefined) contagemColuna.set(c, (contagemColuna.get(c) ?? 0) + 1);
    }
  }
  for (const g of linhas) {
    g.observado = contagemLinha.get(g.id) ?? 0;
    g.esperado = (analise.length * k * g.dezenas.length) / total;
    g.z = zValue(g.observado, g.esperado);
  }
  for (const g of colunas) {
    g.observado = contagemColuna.get(g.id) ?? 0;
    g.esperado = (analise.length * k * g.dezenas.length) / total;
    g.z = zValue(g.observado, g.esperado);
  }
  const testeLinhas = testarChi2(
    linhas.map(g => g.observado),
    linhas.map(g => g.esperado),
    'Distribuição por linha',
    'linhas',
  );
  const testeColunas = testarChi2(
    colunas.map(g => g.observado),
    colunas.map(g => g.esperado),
    'Distribuição por coluna',
    'colunas',
  );

  /* ---------------------------------------------------------------- */
  /* Linhas vazias                                                    */
  /* ---------------------------------------------------------------- */
  const probLinhaVazia = linhas.map(g =>
    total - g.dezenas.length >= k
      ? Math.exp(logComb(total - g.dezenas.length, k) - logComb(total, k))
      : 0,
  );
  const pNenhumaVazia = probabilidadeNenhumaLinhaVazia(linhas, total, k);
  let comPeloMenosUma = 0;
  let somaLinhasVazias = 0;
  for (const sorteio of analise) {
    const set = new Set(sorteio.numeros);
    let vazias = 0;
    for (const g of linhas) {
      if (!g.dezenas.some(n => set.has(n))) vazias++;
    }
    if (vazias > 0) comPeloMenosUma++;
    somaLinhasVazias += vazias;
  }
  const linhasVazias: ValidadorLinhasVazias = {
    comPeloMenosUma,
    percentualComPeloMenosUma: analise.length > 0 ? (comPeloMenosUma / analise.length) * 100 : 0,
    mediaObservada: analise.length > 0 ? somaLinhasVazias / analise.length : 0,
    mediaEsperada: probLinhaVazia.reduce((s, p) => s + p, 0),
    probabilidadeEsperada: Math.max(0, Math.min(1, 1 - pNenhumaVazia)),
  };

  /* ---------------------------------------------------------------- */
  /* Badges: frequência nos últimos N sorteios                        */
  /* ---------------------------------------------------------------- */
  const badgeObs = [0, 0, 0, 0];
  const badgeEsp = [0, 0, 0, 0];
  const badgePoolSum = [0, 0, 0, 0];
  let badgeSorteios = 0;
  for (let i = inicio; i < historico.length; i++) {
    if (i < badgeJanela) continue;
    const contagem = new Map<number, number>();
    for (let j = i - badgeJanela; j < i; j++) {
      for (const n of historico[j].numeros) {
        contagem.set(n, (contagem.get(n) ?? 0) + 1);
      }
    }
    const pool = [0, 0, 0, 0];
    for (let n = numeroMinimo; n < numeroMinimo + total; n++) {
      pool[Math.min(3, contagem.get(n) ?? 0)]++;
    }
    for (let b = 0; b < 4; b++) {
      badgePoolSum[b] += pool[b];
      badgeEsp[b] += (k * pool[b]) / total;
    }
    for (const n of historico[i].numeros) {
      badgeObs[Math.min(3, contagem.get(n) ?? 0)]++;
    }
    badgeSorteios++;
  }
  const rotulosBadge = ['0 (atrasados)', '1 (normais)', '2 (quentes)', '3+ (superquentes)'];
  const badges: ValidadorBadge[] = [0, 1, 2, 3].map(b => {
    const poolMedio = badgeSorteios > 0 ? badgePoolSum[b] / badgeSorteios : 0;
    const acertosBadge = badgeSorteios * k;
    return {
      badge: b,
      rotulo: rotulosBadge[b],
      poolMedio,
      observado: badgeObs[b],
      esperado: badgeEsp[b],
      z: zValue(badgeObs[b], badgeEsp[b]),
      percentualPool: total > 0 ? (poolMedio / total) * 100 : 0,
      percentualAcertos: acertosBadge > 0 ? (badgeObs[b] / acertosBadge) * 100 : 0,
    };
  });
  const testeBadges = testarChi2(
    badges.map(b => b.observado),
    badges.map(b => b.esperado),
    'Distribuição por badge',
    'badges',
  );

  /* ---------------------------------------------------------------- */
  /* Repetição do concurso anterior                                   */
  /* ---------------------------------------------------------------- */
  const repObs = new Array<number>(k + 1).fill(0);
  let pares = 0;
  let somaRep = 0;
  for (let i = Math.max(1, inicio); i < historico.length; i++) {
    const anterior = new Set(historico[i - 1].numeros);
    const repetidas = historico[i].numeros.filter(n => anterior.has(n)).length;
    repObs[repetidas] = (repObs[repetidas] ?? 0) + 1;
    pares++;
    somaRep += repetidas;
  }
  const logTotal = logComb(total, k);
  const probsRep: number[] = [];
  for (let r = 0; r <= k; r++) {
    if (k - r > total - k) {
      probsRep.push(0);
      continue;
    }
    const lp = logComb(k, r) + logComb(total - k, k - r) - logTotal;
    probsRep.push(Math.exp(lp));
  }
  const repEsp = probsRep.map(p => p * pares);
  const distribuicao: ValidadorRepeticao[] = repObs.map((observado, r) => ({
    repetidas: r,
    observado,
    esperado: repEsp[r] ?? 0,
    probabilidade: probsRep[r] ?? 0,
  }));
  const testeRepeticao = testarChi2(
    distribuicao.map(d => d.observado),
    distribuicao.map(d => d.esperado),
    'Repetição do concurso anterior',
    'repeticao',
  );

  /* ---------------------------------------------------------------- */
  /* Testes, correção e avisos                                        */
  /* ---------------------------------------------------------------- */
  const testes = [
    testeUniformidade,
    testeLinhas,
    testeColunas,
    testeBadges,
    testeRepeticao,
  ];
  for (const teste of testes) {
    teste.p = Number.isFinite(teste.p) ? Math.max(0, Math.min(1, teste.p)) : 1;
    teste.pAjustado = Math.min(1, teste.p * testes.length);
    teste.significativoBruto = teste.p < 0.05;
    teste.significativoAjustado = teste.pAjustado < 0.05;
  }
  const significativosBrutos = testes.filter(t => t.significativoBruto).length;
  const significativosAjustados = testes.filter(t => t.significativoAjustado).length;

  const avisos: string[] = [];
  if (janelaEfetiva < 30) {
    avisos.push('Amostra pequena: com menos de 30 sorteios o poder dos testes é baixo.');
  }
  if (esperadoPorNumero < 5) {
    avisos.push('O teste de uniformidade por dezena é aproximado quando o esperado por dezena é menor que 5.');
  }
  if (badgeSorteios < 30) {
    avisos.push('Poucos sorteios com histórico completo de badge; interprete a tabela de badges com cautela.');
  }
  if (significativosAjustados > 0) {
    avisos.push('Há teste(s) significativo(s) após a correção. Antes de virar filtro, valide em outra janela/out-of-sample.');
  } else if (significativosBrutos > 0) {
    avisos.push('Há achado(s) bruto(s), mas nenhum sobrevive à correção de Bonferroni — o esperado em comparações múltiplas.');
  }

  return {
    sucesso: true,
    loteria: cfg.id,
    nomeJogo: cfg.nome_jogo,
    totalSorteios,
    concursoBase,
    janelaSolicitada,
    janelaEfetiva,
    primeiroConcurso: analise[0]?.concurso ?? null,
    ultimoConcurso: analise[analise.length - 1]?.concurso ?? null,
    badgeJanela,
    badgeSorteios,
    numerosPorJogo: k,
    totalNumeros: total,
    totalAcertos,
    colunasGrade,
    numeros,
    linhas,
    colunas,
    badges,
    repeticao: {
      pares,
      mediaObservada: pares > 0 ? somaRep / pares : 0,
      mediaEsperada: (k * k) / total,
      distribuicao,
    },
    linhasVazias,
    testes,
    significativosBrutos,
    significativosAjustados,
    avisos,
  };
}
