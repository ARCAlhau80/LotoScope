import { gerarJogosDiversificados, calcularEstimativaCombinacoes, type FiltroCategoria } from '../src/lib/gerador-diversificado';
import { parseFiltroCategorias } from '../src/lib/colunas-posicionais';

let pass = 0;
let fail = 0;
function ok(cond: boolean, msg: string) {
  if (cond) { pass++; }
  else { fail++; console.error('  ✗', msg); }
}
function titulo(t: string) { console.log('\n•', t); }

titulo('parseFiltroCategorias: ranges vazios são ignorados e ordem preservada');
{
  const r = parseFiltroCategorias('2-3,,4', '1,2,3;5,6;7,8,9');
  ok(!!r && r.length === 2, 'retorna 2 categorias (índice 1 vazio)');
  if (r) {
    ok(r[0].numeros.length === 3 && r[0].min === 2 && r[0].max === 3, 'categoria 0 = {1,2,3} 2-3');
    ok(r[1].numeros.length === 3 && r[1].min === 4 && r[1].max === 4, 'categoria 2 = {7,8,9} 4 (exato)');
  }
}

titulo('parseFiltroCategorias: formato inválido retorna undefined');
{
  ok(parseFiltroCategorias('a-b', '1,2') === undefined, 'letras → undefined');
  ok(parseFiltroCategorias('2-3-4', '1,2,3') === undefined, 'três valores → undefined');
  ok(parseFiltroCategorias(null, '1,2') === undefined, 'sem ranges → undefined');
}

titulo('Gerador: jogos respeitam min/max das categorias');
{
  const cats: FiltroCategoria[] = [
    { numeros: [1, 2, 3, 4, 5], min: 2, max: 3 },
    { numeros: [21, 22, 23, 24, 25], min: 1, max: 2 },
  ];
  const jogos = gerarJogosDiversificados({
    resultados: [],
    nJogos: 12,
    seed: 42,
    totalNumeros: 25,
    numerosPorJogo: 15,
    numeroMinimo: 1,
    filtroCategorias: cats,
  });
  ok(jogos.length === 12, `gerou 12 jogos (obteve ${jogos.length})`);
  const conta = (nums: number[], set: number[]) => nums.filter(n => set.includes(n)).length;
  ok(jogos.every(j => conta(j.numeros, cats[0].numeros) >= 2 && conta(j.numeros, cats[0].numeros) <= 3), 'todos 2-3 de {1..5}');
  ok(jogos.every(j => conta(j.numeros, cats[1].numeros) >= 1 && conta(j.numeros, cats[1].numeros) <= 2), 'todos 1-2 de {21..25}');
}

titulo('Gerador: categorias sobrepostas');
{
  const cats: FiltroCategoria[] = [
    { numeros: [1, 2, 3, 4, 5, 6, 7, 8], min: 3, max: 8 },
    { numeros: [1, 2, 3, 4], min: 1, max: 4 },
  ];
  const jogos = gerarJogosDiversificados({
    resultados: [],
    nJogos: 8,
    seed: 7,
    totalNumeros: 25,
    numerosPorJogo: 15,
    numeroMinimo: 1,
    filtroCategorias: cats,
  });
  ok(jogos.length > 0, 'gerou jogos com categorias sobrepostas');
  ok(jogos.every(j => j.numeros.filter(n => n <= 4).length >= 1 && j.numeros.filter(n => n <= 8).length >= 3), 'respeita ambas');
}

titulo('Gerador: min acima do tamanho do conjunto é limitado (clamp)');
{
  const jogos = gerarJogosDiversificados({
    resultados: [],
    nJogos: 5,
    seed: 1,
    totalNumeros: 25,
    numerosPorJogo: 15,
    numeroMinimo: 1,
    filtroCategorias: [{ numeros: [1, 2, 3, 4, 5], min: 6, max: 6 }],
  });
  ok(jogos.length === 5, `clamp 6→5 gera normalmente (obteve ${jogos.length})`);
  ok(jogos.every(j => j.numeros.filter(n => n <= 5).length === 5), 'cada jogo contém os 5 do conjunto');
}

titulo('Gerador: filtro impossível (soma de mínimos > dezenas) não quebra');
{
  const jogos = gerarJogosDiversificados({
    resultados: [],
    nJogos: 5,
    seed: 1,
    totalNumeros: 25,
    numerosPorJogo: 15,
    numeroMinimo: 1,
    filtroCategorias: [
      { numeros: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], min: 8, max: 8 },
      { numeros: [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], min: 8, max: 8 },
    ],
  });
  ok(jogos.length === 0, `8+8 > 15 dezenas → 0 jogos (obteve ${jogos.length})`);
}

titulo('Todas as combinações respeitam categorias (pool pequeno)');
{
  const todas = gerarJogosDiversificados({
    resultados: [],
    nJogos: 0,
    seed: 3,
    totalNumeros: 6,
    numerosPorJogo: 3,
    numeroMinimo: 1,
    filtroCategorias: [{ numeros: [1, 2, 3], min: 1, max: 1 }],
  });
  ok(todas.length === 9, `C(6,3)=20 filtrado por exatamente 1 de {1,2,3} → 9 (obteve ${todas.length})`);
  ok(todas.every(j => j.numeros.filter(n => n <= 3).length === 1), 'cada jogo tem exatamente 1 de {1,2,3}');
  ok(todas.every(j => j.estrategia === 'todas-combinacoes'), 'estrategia = todas-combinacoes');
}

titulo('Estimativa com categorias é positiva e limitada pelo total bruto');
{
  const cats: FiltroCategoria[] = [{ numeros: [1, 2, 3, 4, 5], min: 2, max: 3 }];
  const est = calcularEstimativaCombinacoes(undefined, undefined, 25, 15, 1, undefined, undefined, [], undefined, undefined, cats);
  const bruto = calcularEstimativaCombinacoes(undefined, undefined, 25, 15, 1);
  ok(est > 0, `estimativa > 0 (${est})`);
  ok(est <= bruto, `estimativa (${est}) <= bruto (${bruto})`);
}

titulo('Estimativa sem categorias permanece igual ao bruto');
{
  const a = calcularEstimativaCombinacoes(undefined, undefined, 25, 15, 1);
  const b = calcularEstimativaCombinacoes(undefined, undefined, 25, 15, 1, undefined, undefined, [], undefined, undefined, undefined);
  ok(a === b, 'sem filtros = C(25,15)');
}

console.log(`\n${fail === 0 ? 'OK' : 'FALHOU'} — ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
