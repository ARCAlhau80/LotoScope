import { gerarJogosDiversificados, calcularEstimativaCombinacoes, type JogoGerado } from '../src/lib/gerador-diversificado';
import { parseDominiosPosicionais } from '../src/lib/colunas-posicionais';

let pass = 0;
let fail = 0;
function ok(cond: boolean, msg: string) {
  if (cond) pass++;
  else {
    fail++;
    console.error('  x', msg);
  }
}
function titulo(t: string) {
  console.log('\n-', t);
}
function ordenado(jogo: JogoGerado): number[] {
  return [...jogo.numeros].sort((a, b) => a - b);
}

titulo('parseDominiosPosicionais: grupos separados por ;');
{
  const d = parseDominiosPosicionais('1,2,3;2,3,4;3,4,5');
  ok(!!d && d.length === 3, 'retorna 3 grupos');
  ok(!!d && d[0].join(',') === '1,2,3', 'grupo 1');
  ok(!!d && d[2].join(',') === '3,4,5', 'grupo 3');
}

titulo('parseDominiosPosicionais: vazio/invalido retorna undefined');
{
  ok(parseDominiosPosicionais(null) === undefined, 'null');
  ok(parseDominiosPosicionais('') === undefined, 'vazio');
  ok(parseDominiosPosicionais(';;') === undefined, 'sem numeros');
}

titulo('Gerador: N1 e N15 respeitam dominios posicionais');
{
  const dominios = Array.from({ length: 15 }, (_, i) => {
    if (i === 0) return [1, 2, 3];
    if (i === 14) return [23, 24, 25];
    return Array.from({ length: 25 }, (_, j) => j + 1);
  });
  const jogos = gerarJogosDiversificados({
    resultados: [],
    nJogos: 5,
    seed: 123,
    totalNumeros: 25,
    numerosPorJogo: 15,
    numeroMinimo: 1,
    dominiosPosicionais: dominios,
  });
  ok(jogos.length === 5, `gerou 5 jogos (${jogos.length})`);
  for (const j of jogos) {
    const ord = ordenado(j);
    ok([1, 2, 3].includes(ord[0]), `N1=${ord[0]} em {1,2,3}`);
    ok([23, 24, 25].includes(ord[14]), `N15=${ord[14]} em {23,24,25}`);
  }
}

titulo('Gerador: dominio diagonal e determinismo por seed');
{
  const dominios = Array.from({ length: 15 }, (_, i) =>
    Array.from({ length: 5 }, (_, k) => i + 1 + k).filter(n => n <= 25)
  );
  const base = {
    resultados: [] as number[][],
    nJogos: 5,
    seed: 777,
    totalNumeros: 25,
    numerosPorJogo: 15,
    numeroMinimo: 1,
    dominiosPosicionais: dominios,
  };
  const a = gerarJogosDiversificados(base);
  const b = gerarJogosDiversificados(base);
  ok(a.length > 0, `gerou jogos com dominio diagonal (${a.length})`);
  ok(JSON.stringify(a) === JSON.stringify(b), 'mesma seed = mesmo resultado');
  for (const j of a) {
    const ord = ordenado(j);
    ok(
      ord.every((n, i) => dominios[i].includes(n)),
      `jogo respeita todas as posicoes: ${ord.join(',')}`
    );
  }
}

titulo('Gerador: caminho com historico e cobertura');
{
  const resultados = Array.from({ length: 40 }, (_, i) =>
    Array.from({ length: 15 }, (_, j) => ((i + j) % 25) + 1).sort((a, b) => a - b)
  );
  const dominios = Array.from({ length: 15 }, (_, i) => {
    if (i === 0) return [1, 2, 3];
    if (i === 14) return [23, 24, 25];
    return Array.from({ length: 25 }, (_, j) => j + 1);
  });
  const jogos = gerarJogosDiversificados({
    resultados,
    nJogos: 4,
    seed: 456,
    totalNumeros: 25,
    numerosPorJogo: 15,
    numeroMinimo: 1,
    dominiosPosicionais: dominios,
  });
  ok(jogos.length === 4, `gerou 4 jogos com historico (${jogos.length})`);
  for (const j of jogos) {
    const ord = ordenado(j);
    ok([1, 2, 3].includes(ord[0]), `N1 com historico = ${ord[0]}`);
    ok([23, 24, 25].includes(ord[14]), `N15 com historico = ${ord[14]}`);
  }
}

titulo('Estimativa: dominio posicional reduz o total sem zerar');
{
  const dominios = Array.from({ length: 15 }, (_, i) => {
    if (i === 0) return [1, 2, 3];
    if (i === 14) return [23, 24, 25];
    return Array.from({ length: 25 }, (_, j) => j + 1);
  });
  const base = calcularEstimativaCombinacoes([], [], 25, 15, 1);
  const comDominios = calcularEstimativaCombinacoes([], [], 25, 15, 1, undefined, undefined, [], undefined, undefined, undefined, dominios);
  ok(base > 0, `base > 0 (${base})`);
  ok(comDominios > 0, `com dominios > 0 (${comDominios})`);
  ok(comDominios < base, `com dominios < base (${comDominios} < ${base})`);
}

console.log(`\n${fail === 0 ? 'OK' : 'FALHOU'} - ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
