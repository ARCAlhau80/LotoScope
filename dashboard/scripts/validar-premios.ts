import { obterPremio, tabelaPremios } from '../src/lib/premios';
import { PRECO_BASE } from '../src/lib/lottery-config';

const FV = (v: number) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: v >= 100 ? 0 : 2, maximumFractionDigits: v >= 100 ? 0 : 2 });

const cases: [string, number, number, number | null][] = [
  ['lotofacil', 15, 0, 1_500_000],
  ['lotofacil', 14, 0, 1_500],
  ['lotofacil', 13, 0, 35],
  ['lotofacil', 12, 0, 14],
  ['lotofacil', 11, 0, 7],
  ['lotofacil', 10, 0, null],
  ['megasena', 6, 0, 40_000_000],
  ['megasena', 5, 0, 40_000],
  ['megasena', 4, 0, 1_000],
  ['megasena', 3, 0, null],
  ['quina', 5, 0, 1_500_000],
  ['quina', 4, 0, 8_000],
  ['quina', 3, 0, 200],
  ['quina', 2, 0, 4],
  ['duplasena', 6, 0, 1_500_000],
  ['duplasena', 5, 0, 5_000],
  ['duplasena', 4, 0, 120],
  ['duplasena', 3, 0, 3],
  ['lotomania', 20, 0, 3_000_000],
  ['lotomania', 15, 0, 8],
  ['lotomania', 0, 0, 500],
  ['diadesorte', 7, 0, 1_500_000],
  ['diadesorte', 6, 0, 1_500],
  ['diadesorte', 5, 0, 25],
  ['diadesorte', 4, 0, 5],
  ['timemania', 7, 0, 3_000_000],
  ['timemania', 6, 0, 30_000],
  ['timemania', 5, 0, 1_500],
  ['timemania', 4, 0, 10.5],
  ['timemania', 3, 0, 3.5],
  ['supersete', 7, 0, 8_000_000],
  ['supersete', 6, 0, 28_000],
  ['supersete', 5, 0, 1_200],
  ['supersete', 4, 0, 70],
  ['supersete', 3, 0, 6],
  ['maismilionaria', 6, 2, 10_000_000],
  ['maismilionaria', 6, 1, 100_000],
  ['maismilionaria', 6, 0, 100_000],
  ['maismilionaria', 5, 2, 50_000],
  ['maismilionaria', 5, 1, 10_000],
  ['maismilionaria', 4, 2, 3_000],
  ['maismilionaria', 4, 0, 1_500],
  ['maismilionaria', 3, 2, 50],
  ['maismilionaria', 3, 1, 24],
  ['maismilionaria', 2, 2, 12],
  ['maismilionaria', 2, 1, 6],
  ['maismilionaria', 2, 0, null],
];

let ok = 0;
const fails: string[] = [];
for (const [lot, ac, tr, expected] of cases) {
  const r = obterPremio(lot, ac, tr);
  const got = r.premiado ? r.faixa!.valor : null;
  if (got === expected) {
    ok++;
  } else {
    fails.push(`${lot} ${ac}/${tr} => ${got} (expected ${expected})`);
  }
}

const loterias = ['lotofacil', 'megasena', 'quina', 'duplasena', 'lotomania', 'diadesorte', 'timemania', 'supersete', 'maismilionaria'];
const faixaCounts = loterias.map(l => `${l}:${tabelaPremios(l).length}`);

function consolidar(combos: [number, number][]): { premiadas: number; totalFixo: number; totalEstimado: number; porFaixa: Record<string, number> } {
  let totalFixo = 0, totalEstimado = 0, premiadas = 0;
  const porFaixa: Record<string, number> = {};
  for (const [ac, at] of combos) {
    const r = obterPremio('maismilionaria', ac, at);
    if (!r.premiado || !r.faixa) continue;
    premiadas++;
    if (r.faixa.fixo) totalFixo += r.faixa.valor; else totalEstimado += r.faixa.valor;
    porFaixa[r.faixa.nome] = (porFaixa[r.faixa.nome] ?? 0) + r.faixa.valor;
  }
  return { premiadas, totalFixo, totalEstimado, porFaixa };
}

// Distribuicao do exemplo real (50 combos Mais Milionaria: 2ac:10, 1ac:17, 0ac:23; trevos 2:7, 1:27, 0:16)
const combosExemplo: [number, number][] = [
  [2, 2], [2, 2], [2, 1], [2, 1], [2, 1], [2, 1], [2, 0], [2, 0], [2, 0], [2, 0], [2, 0],
  [1, 2], [1, 2], [1, 2], [1, 2], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 0], [1, 0], [1, 0],
  [0, 2], [0, 2], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
];
const consol = consolidar(combosExemplo);

console.log(`valor fixo formata: ${FV(35)} | ${FV(3.5)}`);
console.log(`rateio formata: ${FV(1_500_000)}`);
console.log(`faixas: ${faixaCounts.join(' ')}`);
console.log(`consolidado exemplo: premiadas=${consol.premiadas} fixo=${consol.totalFixo} estimado=${consol.totalEstimado} porFaixa=${JSON.stringify(consol.porFaixa)}`);
const custoEx = PRECO_BASE['maismilionaria'] * combosExemplo.length;
const premioEx = consol.totalFixo + consol.totalEstimado;
const saldoEx = premioEx - custoEx;
const roiEx = custoEx > 0 ? ((premioEx / custoEx - 1) * 100).toFixed(1) : '0';
console.log(`custo exemplo: combos=${combosExemplo.length} custo=${custoEx} premio=${premioEx} saldo=${saldoEx} roi=${roiEx}%`);
console.log(`resultado: ${ok}/${cases.length} ${fails.length === 0 ? 'OK' : 'FAIL'}`);
if (fails.length) fails.forEach(f => console.log('  FAIL', f));