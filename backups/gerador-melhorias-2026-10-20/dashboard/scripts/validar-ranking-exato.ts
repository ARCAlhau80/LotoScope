import {
  gerarJogosDiversificados,
  construirScoreContext,
  scoreJogo,
  explicarScoreJogo,
  type GeradorDiversificadoOptions,
  type JogoGerado,
  type ScoreContext,
} from '../src/lib/gerador-diversificado';

let pass = 0;
let fail = 0;
function ok(cond: boolean, msg: string) {
  if (cond) { pass++; }
  else { fail++; console.error('  ✗', msg); }
}
function titulo(t: string) { console.log('\n•', t); }

function makeResultados(n: number, seed: number, total = 25, porJogo = 15): number[][] {
  let s = seed;
  const rnd = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
  const out: number[][] = [];
  for (let i = 0; i < n; i++) {
    const pool = Array.from({ length: total }, (_, k) => k + 1);
    const pick: number[] = [];
    for (let j = 0; j < porJogo; j++) {
      const idx = Math.floor(rnd() * pool.length);
      pick.push(pool[idx]);
      pool.splice(idx, 1);
    }
    out.push(pick.sort((a, b) => a - b));
  }
  return out;
}

function combinacoes(pool: number[], k: number): number[][] {
  const out: number[][] = [];
  const cur: number[] = [];
  const rec = (start: number) => {
    if (cur.length === k) { out.push([...cur]); return; }
    for (let i = start; i <= pool.length - (k - cur.length); i++) {
      cur.push(pool[i]);
      rec(i + 1);
      cur.pop();
    }
  };
  rec(0);
  return out;
}

const overlap = (a: number[], b: number[]) => {
  const st = new Set(b);
  return a.filter(n => st.has(n)).length;
};

const TOTAL = 12;
const POR_JOGO = 6;
const MAX_OV = Math.max(Math.ceil(POR_JOGO * 0.6), Math.max(0, 2 * POR_JOGO - TOTAL) + 2);

const resultados = makeResultados(40, 2024, TOTAL, POR_JOGO);
const lpMini = {
  totalNumeros: TOTAL,
  numerosPorJogo: POR_JOGO,
  numeroMinimo: 1,
  numeroMaximo: TOTAL,
  primosSet: new Set([2, 3, 5, 7, 11]),
};
const scoreSets = {
  quentes: [1, 2, 3, 4],
  aquecendo: [2, 5, 6],
  frios: [9, 10, 11, 12],
  esfriando: [8, 9],
  grupoA: [1, 2, 3, 4],
  grupoB: [5, 6, 7, 8],
  grupoC: [9, 10, 11, 12],
};
const ctx: ScoreContext = construirScoreContext(resultados, lpMini, scoreSets);

const baseMini: GeradorDiversificadoOptions = {
  resultados,
  nJogos: 3,
  seed: 777,
  totalNumeros: TOTAL,
  numerosPorJogo: POR_JOGO,
  numeroMinimo: 1,
  scoreSets,
  otimizacao: 'exata',
};

const universo = Array.from({ length: TOTAL }, (_, i) => i + 1);
const todosJogos = combinacoes(universo, POR_JOGO);
const pontuados = todosJogos.map(g => ({ g, s: scoreJogo(g, ctx) }));

// Oráculo: primeira sequência completa em ordem de qualidade = ótimo lexicográfico,
// sujeito à diversidade (interseção <= MAX_OV) e às restrições de fixos/excluídos.
function oraculo(
  count: number,
  dir: 1 | -1,
  fixos: number[] = [],
  excluidos: number[] = [],
): { g: number[]; s: number }[] | null {
  const validos = pontuados
    .filter(p => fixos.every(n => p.g.includes(n)))
    .filter(p => excluidos.every(n => !p.g.includes(n)))
    .sort((a, b) => (b.s - a.s) * dir || a.g.join(',').localeCompare(b.g.join(',')));
  const sel: { g: number[]; s: number }[] = [];
  let orcamento = 200000;
  const dfs = (): boolean => {
    if (sel.length === count) return true;
    for (const cand of validos) {
      if (--orcamento < 0) return false;
      if (sel.some(x => x.g.join(',') === cand.g.join(','))) continue;
      if (sel.some(x => overlap(x.g, cand.g) > MAX_OV)) continue;
      sel.push(cand);
      if (dfs()) return true;
      sel.pop();
    }
    return false;
  };
  return dfs() ? [...sel] : null;
}

function checarJogos(jogos: JogoGerado[], count: number, dir: 1 | -1): void {
  ok(jogos.length === count, `quantidade ${count} (${jogos.length})`);
  ok(new Set(jogos.map(j => j.numeros.join(','))).size === jogos.length, 'jogos distintos');
  ok(jogos.every(j => j.numeros.length === POR_JOGO), `todos com ${POR_JOGO} dezenas`);
  const s = jogos.map(j => j.score as number);
  ok(s.every((v, i) => i === 0 || (dir === 1 ? s[i - 1] >= v : s[i - 1] <= v)), 'ordenados');
  let maxOv = 0;
  for (let i = 0; i < jogos.length; i++)
    for (let j = i + 1; j < jogos.length; j++)
      maxOv = Math.max(maxOv, overlap(jogos[i].numeros, jogos[j].numeros));
  ok(maxOv <= MAX_OV, `diversidade (maxOverlap=${maxOv} <= ${MAX_OV})`);
}

titulo('Exatidão: melhores (top1) vs força bruta no universo 12/6');
{
  const jogos = gerarJogosDiversificados({ ...baseMini, ordenacao: 'melhores' });
  checarJogos(jogos, 3, 1);
  const ref = oraculo(3, 1);
  ok(!!ref, 'oráculo encontrou sequência');
  if (ref) {
    const a = jogos.map(j => j.score as number);
    const b = ref.map(r => Math.round(r.s * 100) / 100);
    ok(a.join(',') === b.join(','), `scores exatos [${a}] = oráculo [${b}]`);
  }
}

titulo('Exatidão: piores vs força bruta no universo 12/6');
{
  const jogos = gerarJogosDiversificados({ ...baseMini, ordenacao: 'piores' });
  checarJogos(jogos, 3, -1);
  const ref = oraculo(3, -1);
  ok(!!ref, 'oráculo encontrou sequência');
  if (ref) {
    const a = jogos.map(j => j.score as number);
    const b = ref.map(r => Math.round(r.s * 100) / 100);
    ok(a.join(',') === b.join(','), `scores exatos [${a}] = oráculo [${b}]`);
  }
}

titulo('Exatidão com fixos e excluídos');
{
  const jogos = gerarJogosDiversificados({ ...baseMini, nJogos: 2, ordenacao: 'melhores', fixos: [1, 2], excluidos: [12] });
  checarJogos(jogos, 2, 1);
  ok(jogos.every(j => j.numeros.includes(1) && j.numeros.includes(2)), 'respeita fixos');
  ok(jogos.every(j => !j.numeros.includes(12)), 'respeita excluídos');
  const ref = oraculo(2, 1, [1, 2], [12]);
  if (ref) {
    const a = jogos.map(j => j.score as number);
    const b = ref.map(r => Math.round(r.s * 100) / 100);
    ok(a.join(',') === b.join(','), `scores exatos [${a}] = oráculo [${b}]`);
  }
}

titulo('Objetivo "soma": soma total >= top1 e jogos válidos');
{
  const top1 = gerarJogosDiversificados({ ...baseMini, ordenacao: 'melhores', objetivoRanking: 'top1' });
  const soma = gerarJogosDiversificados({ ...baseMini, ordenacao: 'melhores', objetivoRanking: 'soma' });
  checarJogos(soma, 3, 1);
  const somaTotal = (js: JogoGerado[]) => js.reduce((a, j) => a + (j.score as number), 0);
  ok(somaTotal(soma) >= somaTotal(top1) - 1e-9, `soma ${somaTotal(soma)} >= top1 ${somaTotal(top1)}`);
}

titulo('Objetivo "minimo": pior jogo do conjunto >= top1 e jogos válidos');
{
  const top1 = gerarJogosDiversificados({ ...baseMini, ordenacao: 'melhores', objetivoRanking: 'top1' });
  const minimo = gerarJogosDiversificados({ ...baseMini, ordenacao: 'melhores', objetivoRanking: 'minimo' });
  checarJogos(minimo, 3, 1);
  const pior = (js: JogoGerado[]) => Math.min(...js.map(j => j.score as number));
  ok(pior(minimo) >= pior(top1) - 1e-9, `mínimo ${pior(minimo)} >= top1 ${pior(top1)}`);
}

titulo('Determinismo do otimizador exato (seeds diferentes, mesmo resultado)');
{
  const chave = (js: JogoGerado[]) => js.map(j => `${j.numeros.join(',')}#${j.score}`).join('|');
  for (const objetivo of ['top1', 'soma', 'minimo'] as const) {
    const a = gerarJogosDiversificados({ ...baseMini, seed: 11, ordenacao: 'melhores', objetivoRanking: objetivo });
    const b = gerarJogosDiversificados({ ...baseMini, seed: 99991, ordenacao: 'melhores', objetivoRanking: objetivo });
    ok(chave(a) === chave(b), `${objetivo}: determinístico`);
  }
}

titulo('Explicabilidade: breakdown por dezena + bônus fecha com o score');
{
  const jogos = gerarJogosDiversificados({ ...baseMini, ordenacao: 'melhores' });
  for (const j of jogos) {
    const det = j.detalhesScore;
    ok(!!det, 'detalhesScore presente');
    if (!det) continue;
    ok(det.termos.length === POR_JOGO, 'um termo por dezena');
    const somaTermos = det.termos.reduce((a, t) => a + t.subtotal, 0) + det.bonusGrupo;
    ok(Math.abs(somaTermos - det.total) <= 0.011, `soma termos (${somaTermos}) = total (${det.total})`);
    ok(det.total === j.score, `total (${det.total}) = score (${j.score})`);
    ok(det.termos.every(t => j.numeros.includes(t.numero)), 'termos referem-se às dezenas do jogo');
  }
  const manual = explicarScoreJogo(jogos[0].numeros, ctx);
  ok(manual.total === jogos[0].detalhesScore?.total, 'explicarScoreJogo reproduz o total');
}

titulo('Explicabilidade: breakdown identifica quente/frio/gap/grupo');
{
  const draws = [
    [1, 2, 3, 4, 5, 6],
    [1, 2, 3, 4, 5, 7],
    [1, 2, 3, 4, 8, 9],
  ];
  const lpCtl = {
    totalNumeros: TOTAL,
    numerosPorJogo: POR_JOGO,
    numeroMinimo: 1,
    numeroMaximo: TOTAL,
    primosSet: new Set([2, 3, 5, 7, 11]),
  };
  const setsCtl = {
    quentes: [1],
    aquecendo: [2],
    frios: [10],
    esfriando: [11],
    grupoA: [1, 2, 3, 4],
    grupoB: [5, 6, 7, 8],
    grupoC: [9, 10, 11, 12],
  };
  const ctxCtl = construirScoreContext(draws, lpCtl, setsCtl);
  const jogo = [1, 2, 5, 6, 10, 11];
  const det = explicarScoreJogo(jogo, ctxCtl);
  const termo = (n: number) => det.termos.find(t => t.numero === n)!;

  ok(termo(1).quente === 1, 'dezena 1 marcada como quente');
  ok(termo(2).aquecendo === 1, 'dezena 2 marcada como aquecendo');
  ok(termo(10).frio === -0.5, 'dezena 10 penalizada como fria');
  ok(termo(11).esfriando === -0.5, 'dezena 11 penalizada como esfriando');
  ok(Math.abs(termo(10).gap - 0.15) < 1e-9, `gap da dezena 10 (${termo(10).gap}) = 0.15`);
  ok(Math.abs(termo(6).gap - 0.1) < 1e-9, `gap da dezena 6 (${termo(6).gap}) = 0.1`);
  ok(Math.abs(termo(1).freqRecente - 0.6) < 1e-9, `freqRecente da dezena 1 (${termo(1).freqRecente}) = 0.6`);
  ok(Math.abs(termo(1).subtotal - 1.7) < 1e-9, `subtotal da dezena 1 (${termo(1).subtotal}) = 1.7`);
  ok(det.gruposPresentes === 3, `3 grupos presentes (${det.gruposPresentes})`);
  ok(det.bonusGrupo === 2, `bônus de grupo = 2 (${det.bonusGrupo})`);
  ok(det.total === scoreJogo(jogo, ctxCtl), `total (${det.total}) = scoreJogo (${scoreJogo(jogo, ctxCtl)})`);
}

titulo('Fallback com filtros: colunas posicionais ainda respeitadas');
{
  const jogos = gerarJogosDiversificados({
    ...baseMini,
    ordenacao: 'melhores',
    colunasPosicionais: { sets: [[1, 2, 3, 4, 5, 6]], mins: [2], maxs: [4] },
  });
  checarJogos(jogos, 3, 1);
  ok(jogos.every(j => j.numeros.filter(n => n <= 6).length >= 2 && j.numeros.filter(n => n <= 6).length <= 4), 'coluna respeitada');
}

titulo('Desempenho no universo real 25/15 (informativo)');
{
  const resultadosReais = makeResultados(40, 2024);
  const base = { resultados: resultadosReais, seed: 777, totalNumeros: 25, numerosPorJogo: 15, numeroMinimo: 1 };
  for (const n of [8, 20, 50, 100]) {
    const t0 = Date.now();
    const jogos = gerarJogosDiversificados({ ...base, nJogos: n, ordenacao: 'melhores' });
    const ms = Date.now() - t0;
    ok(jogos.length === n, `n=${n}: ${n} jogos (${ms}ms)`);
    console.log(`    n=${n}: ${ms}ms · top=${jogos[0].score}`);
  }
}

titulo('Objetivos no universo real 25/15: soma e mínimo superam o top1');
{
  const resultadosReais = makeResultados(40, 2024);
  const setsReais = {
    quentes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    aquecendo: [1, 2, 3, 4, 5],
    frios: [21, 22, 23, 24, 25],
    esfriando: [20, 21, 22],
    grupoA: [2, 5, 6, 8, 11, 13, 17, 20],
    grupoB: [3, 7, 9, 12, 14, 18, 19, 21],
    grupoC: [4, 10, 15, 16, 22, 23, 24, 25],
  };
  const baseReal: GeradorDiversificadoOptions = {
    resultados: resultadosReais, seed: 777, totalNumeros: 25, numerosPorJogo: 15, numeroMinimo: 1, scoreSets: setsReais,
    otimizacao: 'exata',
  };
  const somaTotal = (js: JogoGerado[]) => Math.round(js.reduce((a, j) => a + (j.score as number), 0) * 100) / 100;
  const pior = (js: JogoGerado[]) => Math.min(...js.map(j => j.score as number));
  for (const n of [8, 20]) {
    const t0 = Date.now();
    const top1 = gerarJogosDiversificados({ ...baseReal, nJogos: n, ordenacao: 'melhores', objetivoRanking: 'top1' });
    const t1 = Date.now();
    const soma = gerarJogosDiversificados({ ...baseReal, nJogos: n, ordenacao: 'melhores', objetivoRanking: 'soma' });
    const t2 = Date.now();
    const minimo = gerarJogosDiversificados({ ...baseReal, nJogos: n, ordenacao: 'melhores', objetivoRanking: 'minimo' });
    const t3 = Date.now();
    console.log(`    n=${n}: top1 soma ${somaTotal(top1)} min ${pior(top1)} (${t1 - t0}ms) · soma ${somaTotal(soma)} (${t2 - t1}ms) · min ${pior(minimo)} (${t3 - t2}ms)`);
    ok(somaTotal(soma) >= somaTotal(top1) - 1e-6, `n=${n}: soma >= top1`);
    ok(pior(minimo) >= pior(top1) - 1e-6, `n=${n}: mínimo >= top1`);
  }
}

console.log(`\n${fail === 0 ? 'OK' : 'FALHOU'} — ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
