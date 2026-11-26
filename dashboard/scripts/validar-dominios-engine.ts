/**
 * Validação do motor exato de domínios posicionais (contagem + geração).
 *
 * Rodar:
 *   cd dashboard
 *   npx tsx scripts/validar-dominios-engine.ts
 */
import { contarJogosComDominios, prepararDominios } from '../src/lib/dominios-posicionais';

function assert(cond: boolean, msg: string): asserts cond {
  if (!cond) throw new Error(msg);
}

const base = { totalNumeros: 25, numerosPorJogo: 15, numeroMinimo: 1 };
const FIXOS_13 = [2, 3, 4, 5, 6, 7, 18, 19, 20, 21, 22, 23, 24];
const EXCLUIDOS_10 = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17];

// 1) Universo completo: C(25,15)
const todos = contarJogosComDominios(base);
assert(todos.total === 3_268_760, `C(25,15) esperado 3.268.760, veio ${todos.total}`);

// 2) 13 fixos + 10 exclusões = uma única combinação
const uma = contarJogosComDominios({ ...base, fixos: FIXOS_13, excluidos: EXCLUIDOS_10 });
assert(uma.total === 1, `13 fixos + 10 exclusões deveria dar 1, veio ${uma.total}`);

// 3) Conflito posicional conhecido: 7 em N6, 18 em N8, 19 em N9,
//    8–17 proibidos em N7 -> sem candidato viável em N7.
const excluidosPosicoes: Record<number, number[]> = {
  8: [1, 2, 3, 4, 5, 6, 7, 8],
  9: [1, 2, 3, 4, 5, 6, 7, 8, 9],
  10: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  11: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
  12: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
  13: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
  14: [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
  15: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  16: [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  17: [7, 8, 9, 10, 11, 12, 13, 14, 15],
};
const conflito = contarJogosComDominios({
  ...base,
  fixos: FIXOS_13,
  excluidosPosicoes,
  fixosPosicoes: { 7: [6], 18: [8], 19: [9] },
});
assert(conflito.total === 0, `conflito deveria dar 0, veio ${conflito.total}`);
assert(conflito.detalhe.includes('N7'), `diagnóstico deveria citar N7: ${conflito.detalhe}`);

// 4) Domínio N1={1}, N15={25} e 5 fixos: gera jogos válidos
const dominios = Array.from({ length: 15 }, (_, i) => {
  if (i === 0) return [1];
  if (i === 14) return [25];
  return Array.from({ length: 25 }, (_, n) => n + 1);
});
const ctx = prepararDominios({ ...base, fixos: [2, 3, 4, 5, 6], dominios });
assert(ctx.total > 0, 'domínio N1=1/N15=25 deveria ter combinações');
let s = 123456789;
const rand = () => {
  s = (s * 16807) % 2147483647;
  return (s - 1) / 2147483646;
};
for (let i = 0; i < 200; i++) {
  const jogo = ctx.gerar(rand);
  assert(!!jogo, 'gerar() devolveu null com total > 0');
  assert(jogo!.length === 15, `jogo com ${jogo!.length} dezenas`);
  assert(jogo![0] === 1, `N1 deveria ser 1: ${jogo!.join(',')}`);
  assert(jogo![14] === 25, `N15 deveria ser 25: ${jogo!.join(',')}`);
  for (const f of [2, 3, 4, 5, 6]) assert(jogo!.includes(f), `fixo ${f} ausente`);
}

// 5) Universo com mínimo 0 (Lotomania): 0 não pode ser confundido com o
//    sentinela "nenhum número escolhido".
const lotomania = prepararDominios({
  totalNumeros: 100,
  numerosPorJogo: 2,
  numeroMinimo: 0,
  fixos: [0],
  dominios: [[0], [1]],
});
assert(lotomania.total === 1, `mínimo 0 deveria dar 1, veio ${lotomania.total}`);
const jogoZero = lotomania.gerar(rand);
assert(!!jogoZero && jogoZero[0] === 0 && jogoZero[1] === 1, `mínimo 0 gerou ${jogoZero?.join(',')}`);

console.log('OK: motor de domínios posicionais (contagem + geração + diagnóstico)');
