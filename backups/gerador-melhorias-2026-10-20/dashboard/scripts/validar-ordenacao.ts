import { gerarJogosDiversificados } from '../src/lib/gerador-diversificado';
import { parseOrdenacao, parseObjetivoRanking, parseOtimizacao, parseScoreSets } from '../src/lib/colunas-posicionais';

let pass = 0;
let fail = 0;
function ok(cond: boolean, msg: string) {
  if (cond) { pass++; }
  else { fail++; console.error('  ✗', msg); }
}
function titulo(t: string) { console.log('\n•', t); }

function makeResultados(n: number, seed: number): number[][] {
  let s = seed;
  const rnd = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
  const out: number[][] = [];
  for (let i = 0; i < n; i++) {
    const pool = Array.from({ length: 25 }, (_, k) => k + 1);
    const pick: number[] = [];
    for (let j = 0; j < 15; j++) {
      const idx = Math.floor(rnd() * pool.length);
      pick.push(pool[idx]);
      pool.splice(idx, 1);
    }
    out.push(pick.sort((a, b) => a - b));
  }
  return out;
}

titulo('parseOrdenacao');
{
  ok(parseOrdenacao('melhores') === 'melhores', 'melhores');
  ok(parseOrdenacao('piores') === 'piores', 'piores');
  ok(parseOrdenacao('balanceado') === 'balanceado', 'balanceado');
  ok(parseOrdenacao('aleatorio') === 'aleatorio', 'aleatorio');
  ok(parseOrdenacao('foo') === undefined, 'valor inválido → undefined');
  ok(parseOrdenacao(null) === undefined, 'null → undefined');
}

titulo('parseObjetivoRanking');
{
  ok(parseObjetivoRanking('top1') === 'top1', 'top1');
  ok(parseObjetivoRanking('soma') === 'soma', 'soma');
  ok(parseObjetivoRanking('minimo') === 'minimo', 'minimo');
  ok(parseObjetivoRanking('foo') === undefined, 'valor inválido → undefined');
  ok(parseObjetivoRanking(null) === undefined, 'null → undefined');
}

titulo('parseOtimizacao');
{
  ok(parseOtimizacao('exata') === 'exata', 'exata');
  ok(parseOtimizacao('pool') === 'pool', 'pool');
  ok(parseOtimizacao(null) === 'pool', 'null → pool (padrão)');
  ok(parseOtimizacao('foo') === 'pool', 'valor inválido → pool');
}

titulo('parseScoreSets');
{
  const r = parseScoreSets('quentes:1,4,7;grupoA:2,5,6');
  ok(!!r && r.quentes.join(',') === '1,4,7', 'quentes = 1,4,7');
  ok(!!r && r.grupoA.join(',') === '2,5,6', 'grupoA = 2,5,6');
  ok(parseScoreSets('') === undefined, 'vazio → undefined');
  ok(parseScoreSets('semValores:') === undefined, 'chave sem números → undefined');
}

const resultados = makeResultados(40, 2024);
const scoreSets = {
  quentes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  aquecendo: [1, 2, 3, 4, 5],
  frios: [21, 22, 23, 24, 25],
  esfriando: [20, 21, 22],
  grupoA: [2, 5, 6, 8, 11, 13, 17, 20],
  grupoB: [3, 7, 9, 12, 14, 18, 19, 21],
  grupoC: [4, 10, 15, 16, 22, 23, 24, 25],
};
const base = { resultados, nJogos: 8, seed: 777, totalNumeros: 25, numerosPorJogo: 15, numeroMinimo: 1, scoreSets };

titulo('Aleatório: mantém comportamento atual (sem score)');
{
  const jogos = gerarJogosDiversificados({ ...base, ordenacao: 'aleatorio' });
  ok(jogos.length === 8, `8 jogos (${jogos.length})`);
  ok(jogos.every(j => j.score === undefined), 'nenhum score atribuído');
}

titulo('Melhores: top por score, ordenado desc');
{
  const jogos = gerarJogosDiversificados({ ...base, ordenacao: 'melhores' });
  ok(jogos.length === 8, `8 jogos (${jogos.length})`);
  ok(jogos.every(j => typeof j.score === 'number'), 'todos com score');
  const s = jogos.map(j => j.score as number);
  ok(s.every((v, i) => i === 0 || s[i - 1] >= v), 'ordenado do maior para o menor');
}

titulo('Piores: bottom por score, ordenado asc');
{
  const jogos = gerarJogosDiversificados({ ...base, ordenacao: 'piores' });
  ok(jogos.length === 8, `8 jogos (${jogos.length})`);
  const s = jogos.map(j => j.score as number);
  ok(s.every((v, i) => i === 0 || s[i - 1] <= v), 'ordenado do menor para o maior');
}

titulo('Melhores vs Piores: faixas de score não se cruzam (mesmo seed)');
{
  const ml = gerarJogosDiversificados({ ...base, ordenacao: 'melhores' });
  const pr = gerarJogosDiversificados({ ...base, ordenacao: 'piores' });
  const minMelhor = Math.min(...ml.map(j => j.score as number));
  const maxPior = Math.max(...pr.map(j => j.score as number));
  ok(minMelhor >= maxPior, `min(melhores)=${minMelhor} >= max(piores)=${maxPior}`);
}

titulo('Balanceado: quantidade correta e múltiplas faixas de score');
{
  const jogos = gerarJogosDiversificados({ ...base, ordenacao: 'balanceado' });
  ok(jogos.length === 8, `8 jogos (${jogos.length})`);
  const s = jogos.map(j => j.score as number);
  ok(Math.max(...s) > Math.min(...s), `há variação de score (${Math.min(...s)}..${Math.max(...s)})`);
  ok(jogos.every(j => j.detalhesScore !== undefined), 'todos com detalhesScore');
  ok(jogos.every(j => j.detalhesScore?.total === j.score), 'detalhesScore.total = score');
}

const chaveJogos = (js: { numeros: number[]; score?: number }[]) =>
  js.map(j => `${j.numeros.join(',')}#${j.score}`).join('|');

titulo('Otimização: padrão é pool; exata é opt-in');
{
  const padrao = gerarJogosDiversificados({ ...base, ordenacao: 'melhores' });
  const pool = gerarJogosDiversificados({ ...base, ordenacao: 'melhores', otimizacao: 'pool' });
  ok(chaveJogos(padrao) === chaveJogos(pool), 'sem otimizacao = otimizacao pool');
  const exata = gerarJogosDiversificados({ ...base, ordenacao: 'melhores', otimizacao: 'exata' });
  const topPool = padrao[0].score as number;
  const topExata = exata[0].score as number;
  ok(topExata >= topPool, `exata topo (${topExata}) >= pool topo (${topPool})`);
}

titulo('Exata e determinística; pool varia com o seed (desempate aleatório)');
{
  const a = gerarJogosDiversificados({ ...base, seed: 111, ordenacao: 'melhores', otimizacao: 'exata' });
  const b = gerarJogosDiversificados({ ...base, seed: 987654, ordenacao: 'melhores', otimizacao: 'exata' });
  ok(chaveJogos(a) === chaveJogos(b), 'exata: mesmo conjunto com seeds diferentes');
  for (const modo of ['melhores', 'piores'] as const) {
    const c = gerarJogosDiversificados({ ...base, seed: 111, ordenacao: modo, otimizacao: 'pool' });
    const d = gerarJogosDiversificados({ ...base, seed: 987654, ordenacao: modo, otimizacao: 'pool' });
    ok(chaveJogos(c) !== chaveJogos(d), `${modo}/pool: conjuntos diferentes com seeds diferentes`);
  }
}

titulo('Busca local: quantidade exata, jogos distintos e separação de qualidade');
{
  const overlap = (a: number[], b: number[]) => {
    const st = new Set(b);
    return a.filter(n => st.has(n)).length;
  };
  for (const modo of ['melhores', 'piores'] as const) {
    const n = 10;
    const jogos = gerarJogosDiversificados({ ...base, nJogos: n, ordenacao: modo });
    ok(jogos.length === n, `${modo}: ${n} jogos (${jogos.length})`);
    ok(new Set(jogos.map(j => j.numeros.join(','))).size === n, `${modo}: todos distintos`);
    const s = jogos.map(j => j.score as number);
    ok(s.every((v, i) => i === 0 || (modo === 'melhores' ? s[i - 1] >= v : s[i - 1] <= v)), `${modo}: ordenado`);
    let maxOv = 0;
    for (let i = 0; i < jogos.length; i++)
      for (let j = i + 1; j < jogos.length; j++)
        maxOv = Math.max(maxOv, overlap(jogos[i].numeros, jogos[j].numeros));
    ok(maxOv <= 10, `${modo}: diversidade mantida (maxOverlap=${maxOv})`);
    if (modo === 'melhores') ok(s[0] >= 45, `${modo}: topo atinge o teto do modelo (${s[0]})`);
    else ok(s[0] <= 27, `${modo}: fundo atinge o piso do modelo (${s[0]})`);
  }
}

titulo('Aleatório continua variando entre seeds');
{
  const a = gerarJogosDiversificados({ ...base, seed: 111, ordenacao: 'aleatorio' });
  const b = gerarJogosDiversificados({ ...base, seed: 987654, ordenacao: 'aleatorio' });
  ok(chaveJogos(a) !== chaveJogos(b), 'aleatorio: conjuntos diferentes com seeds diferentes');
}

console.log(`\n${fail === 0 ? 'OK' : 'FALHOU'} — ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
