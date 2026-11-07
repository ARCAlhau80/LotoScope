import { gerarJogosDiversificados, type OrdenacaoJogos } from '../src/lib/gerador-diversificado.ts';

let pass = 0;
let fail = 0;
function ok(cond: boolean, msg: string) {
  if (cond) pass++;
  else {
    fail++;
    console.error('  FALHOU -', msg);
  }
}
function titulo(t: string) {
  console.log('\n==', t);
}

function makeResultados(n: number, seed: number): number[][] {
  let s = seed;
  const rnd = () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
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
const base = {
  resultados,
  nJogos: 8,
  seed: 777,
  totalNumeros: 25,
  numerosPorJogo: 15,
  numeroMinimo: 1,
  scoreSets,
};
const modos: OrdenacaoJogos[] = ['aleatorio', 'melhores', 'piores', 'balanceado'];
const chave = (js: { numeros: number[]; score?: number }[]) =>
  js.map(j => `${j.numeros.join(',')}#${j.score}`).join('|');

titulo('Aleatorio: comportamento atual (sem score)');
{
  const jogos = gerarJogosDiversificados({ ...base, ordenacao: 'aleatorio' });
  ok(jogos.length === 8, `8 jogos (${jogos.length})`);
  ok(jogos.every(j => j.score === undefined), 'nenhum score atribuido');
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

titulo('Melhores vs Piores: faixas de score nao se cruzam (mesmo seed)');
{
  const ml = gerarJogosDiversificados({ ...base, ordenacao: 'melhores' });
  const pr = gerarJogosDiversificados({ ...base, ordenacao: 'piores' });
  const minMelhor = Math.min(...ml.map(j => j.score as number));
  const maxPior = Math.max(...pr.map(j => j.score as number));
  ok(minMelhor >= maxPior, `min(melhores)=${minMelhor} >= max(piores)=${maxPior}`);
}

titulo('Balanceado: quantidade correta e multiplas faixas de score');
{
  const jogos = gerarJogosDiversificados({ ...base, ordenacao: 'balanceado' });
  ok(jogos.length === 8, `8 jogos (${jogos.length})`);
  const s = jogos.map(j => j.score as number);
  ok(Math.max(...s) > Math.min(...s), `ha variacao de score (${Math.min(...s)}..${Math.max(...s)})`);
  ok(jogos.every(j => typeof j.score === 'number'), 'todos com score');
}

titulo('Sequencial: mesma seed e deterministica para as 4 modalidades');
{
  const a = Object.fromEntries(modos.map(m => [m, chave(gerarJogosDiversificados({ ...base, ordenacao: m }))]));
  const b = Object.fromEntries(modos.map(m => [m, chave(gerarJogosDiversificados({ ...base, ordenacao: m }))]));
  for (const m of modos) ok(a[m] === b[m], `${m}: deterministico`);
  ok(a['melhores'] !== a['piores'], 'melhores != piores');
  ok(a['melhores'] !== a['balanceado'], 'melhores != balanceado');
}

titulo('Todas as combinacoes (nJogos=0): ordenacao respeitada');
{
  const mini = {
    resultados,
    nJogos: 0,
    seed: 42,
    totalNumeros: 10,
    numerosPorJogo: 5,
    numeroMinimo: 1,
    scoreSets,
  };
  const total = 252; // C(10,5)
  const al = gerarJogosDiversificados({ ...mini, ordenacao: 'aleatorio' });
  const ml = gerarJogosDiversificados({ ...mini, ordenacao: 'melhores' });
  const pr = gerarJogosDiversificados({ ...mini, ordenacao: 'piores' });
  const bl = gerarJogosDiversificados({ ...mini, ordenacao: 'balanceado' });

  ok(al.length === total, `aleatorio: ${total} combinacoes (${al.length})`);
  ok(ml.length === total, `melhores: ${total} combinacoes (${ml.length})`);
  ok(pr.length === total, `piores: ${total} combinacoes (${pr.length})`);
  ok(bl.length === total, `balanceado: ${total} combinacoes (${bl.length})`);

  ok(al.every(j => j.score === undefined), 'aleatorio sem score');
  ok(ml.every(j => typeof j.score === 'number'), 'melhores com score');
  ok(pr.every(j => typeof j.score === 'number'), 'piores com score');
  ok(bl.every(j => typeof j.score === 'number'), 'balanceado com score');

  const sm = ml.map(j => j.score as number);
  const sp = pr.map(j => j.score as number);
  ok(sm.every((v, i) => i === 0 || sm[i - 1] >= v), 'melhores: desc');
  ok(sp.every((v, i) => i === 0 || sp[i - 1] <= v), 'piores: asc');
  ok(sm[0] >= sp[0], `melhores topo (${sm[0]}) >= piores topo (${sp[0]})`);

  const sb = bl.map(j => j.score as number);
  ok(new Set(bl.map(j => j.numeros.join(','))).size === total, 'balanceado: todas unicas');
  ok(Math.max(...sb) > Math.min(...sb), 'balanceado: mistura de faixas');

  ok(chave(ml) !== chave(pr), 'todas/melhores != todas/piores');
  ok(chave(ml) !== chave(al), 'todas/melhores != todas/aleatorio');
}

console.log(`\n${fail === 0 ? 'OK' : 'FALHOU'} - ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
