import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  carregarDraws,
  executarBacktest,
  normalizarDraws,
  resumir,
  type BacktestConfig,
  type Draw,
} from './backtest-ranking';

let pass = 0;
let fail = 0;
function ok(cond: boolean, msg: string) {
  if (cond) { pass++; }
  else { fail++; console.error('  ✗', msg); }
}
function titulo(t: string) { console.log('\n•', t); }

function makeDraws(n: number, seed: number, total = 25, porJogo = 15): Draw[] {
  let s = seed;
  const rnd = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
  const out: Draw[] = [];
  for (let i = 0; i < n; i++) {
    const pool = Array.from({ length: total }, (_, k) => k + 1);
    const pick: number[] = [];
    for (let j = 0; j < porJogo; j++) {
      const idx = Math.floor(rnd() * pool.length);
      pick.push(pool[idx]);
      pool.splice(idx, 1);
    }
    out.push({ concurso: i + 1, numeros: pick.sort((a, b) => a - b) });
  }
  return out;
}

titulo('normalizarDraws aceita number[][] e {concurso, numeros}[]');
{
  const a = normalizarDraws([[3, 1, 2], [6, 4, 5]]);
  ok(a.length === 2, '2 sorteios');
  ok(a[0].concurso === 1, 'concurso inferido = 1');
  ok(a[0].numeros.join(',') === '1,2,3', 'números ordenados');
  const b = normalizarDraws([{ concurso: 99, numeros: [3, 2, 1] }]);
  ok(b[0].concurso === 99, 'concurso preservado');
  ok(b[0].numeros.join(',') === '1,2,3', 'números ordenados no formato objeto');
  let erro = '';
  try { normalizarDraws([{ foo: 1 }]); } catch (e) { erro = e instanceof Error ? e.message : String(e); }
  ok(erro.includes('formato inválido'), 'formato inválido lança erro');
}

titulo('carregarDraws lê JSON do disco');
{
  const dir = mkdtempSync(join(tmpdir(), 'lotoscope-backtest-'));
  try {
    const file = join(dir, 'draws.json');
    writeFileSync(file, JSON.stringify(makeDraws(35, 42)), 'utf-8');
    const draws = carregarDraws(file);
    ok(draws.length === 35, `35 sorteios (${draws.length})`);
    ok(draws[0].numeros.length === 15, '15 dezenas por sorteio');
    ok(draws[35 - 1].concurso === 35, 'concurso final = 35');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

const draws = makeDraws(36, 2024);
const cfg: BacktestConfig = {
  nJogos: 3,
  totalNumeros: 25,
  numerosPorJogo: 15,
  numeroMinimo: 1,
  ordenacao: 'melhores',
  objetivoRanking: 'top1',
  otimizacao: 'pool',
  seed: 7,
  baselineRuns: 20,
  warmup: 30,
  limit: 6,
  step: 1,
};

titulo('Backtest: distribuição, resumo e faixa 11..15');
{
  const out = executarBacktest(draws, cfg);
  ok(out.concursos.length === 6, `6 concursos (${out.concursos.length})`);
  ok(out.concursos.every(r => r.acertos.length === cfg.nJogos), 'acertos de todos os jogos registrados');
  ok(out.concursos.every(r => r.melhorAcertos === Math.max(...r.acertos)), 'melhorAcertos = máximo dos acertos');
  ok(out.concursos.every(r => r.baselineMelhor >= 0 && r.baselineMelhor <= cfg.numerosPorJogo), 'baseline dentro da faixa');
  const dist = out.resumo.distribuicaoMelhor;
  ok(['11', '12', '13', '14', '15'].every(k => k in dist), 'faixa 11..15 presente na distribuição');
  const somaDist = Object.values(dist).reduce((a, b) => a + b, 0);
  ok(somaDist === out.concursos.length, `distribuição soma ${out.concursos.length} (${somaDist})`);
  ok(out.resumo.mediaMelhor >= 0 && out.resumo.mediaMelhor <= cfg.numerosPorJogo, 'média dentro da faixa');
  ok(out.resumo.liftMedia !== null, 'lift calculado');
}

titulo('Backtest determinístico (mesma entrada → mesmo JSON)');
{
  const a = executarBacktest(draws, cfg);
  const b = executarBacktest(draws, cfg);
  ok(JSON.stringify(a) === JSON.stringify(b), 'execuções idênticas');
}

titulo('Backtest: piores e objetivo soma também executam');
{
  const piores = executarBacktest(draws, { ...cfg, ordenacao: 'piores' });
  ok(piores.concursos.length === 6, `piores: 6 concursos (${piores.concursos.length})`);
  ok(piores.resumo.distribuicaoMelhor !== undefined, 'piores: distribuição presente');
  const soma = executarBacktest(draws, { ...cfg, objetivoRanking: 'soma', limit: 2 });
  ok(soma.concursos.length === 2, `soma: 2 concursos (${soma.concursos.length})`);
  const exata = executarBacktest(draws, { ...cfg, otimizacao: 'exata', limit: 2 });
  ok(exata.concursos.length === 2, `exata: 2 concursos (${exata.concursos.length})`);
}

titulo('resumir: distribuição de todos os jogos e lift 11+');
{
  const resultados = [
    { concurso: 1, acertos: [11, 10, 9], melhorAcertos: 11, mediaAcertos: 10, baselineMelhor: 11, baselineMedia: 8, baselineTaxa11: 1 },
    { concurso: 2, acertos: [12, 11, 8], melhorAcertos: 12, mediaAcertos: 10.33, baselineMelhor: 10, baselineMedia: 8.5, baselineTaxa11: 0 },
  ];
  const r = resumir(resultados, cfg);
  ok(r.concursos === 2, '2 concursos');
  ok(r.maxMelhor === 12, 'máximo = 12');
  ok(r.mediaMelhor === 11.5, `média = 11.5 (${r.mediaMelhor})`);
  ok(r.distribuicaoJogos['11'] === 2, `11 acertos aparece 2x (${r.distribuicaoJogos['11']})`);
  ok(r.taxa11mais === 1, `taxa 11+ = 1 (${r.taxa11mais})`);
  ok(r.baselineTaxa11mais === 0.5, `baseline 11+ = 0.5 (${r.baselineTaxa11mais})`);
  ok(r.lift11mais === 2, `lift 11+ = 2 (${r.lift11mais})`);
}

console.log(`\n${fail === 0 ? 'OK' : 'FALHOU'} — ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
