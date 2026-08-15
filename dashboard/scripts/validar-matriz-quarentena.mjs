// Valida a Matriz de Quarentena por Posição (regra corrigida §3 — handoff 12/08/2026)
// Uso: node scripts/validar-matriz-quarentena.mjs [baseUrl]
// Default baseUrl: http://localhost:3003 (dev server do dashboard)
// Referência @3759: Q=35, A=16, M=8, R=36 (doc HANDOFF-MATRIZ-QUARENTENA.md §3)

const baseUrl = process.argv[2] || 'http://localhost:3003';

async function getMatriz(concurso) {
  const url = `${baseUrl}/api/dashboard-data?concurso=${concurso}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} em ${url}`);
  const data = await res.json();
  return { q: data.quarentena_posicoes, data };
}

function totais(q) {
  const c = { quarentena: 0, atrasado: 0, muito_atrasado: 0, rara: 0, normal: 0, inviavel: 0 };
  for (const pos of Object.values(q)) for (const cell of pos.numeros) c[cell.status]++;
  return c;
}

function cell(q, pos, dig) {
  return q[pos]?.numeros.find(n => n.digito === dig);
}

let failures = 0;
function assert(name, cond) {
  if (cond) console.log(`  ok ${name}`);
  else { failures++; console.error(`  FAIL ${name}`); }
}

const { q: q3759, data: d3759 } = await getMatriz(3759);
console.log(`@3759 (concurso_analisado=${d3759.concurso_analisado})`);
const t1 = totais(q3759);
assert('Q=35', t1.quarentena === 35);
assert('A=16', t1.atrasado === 16);
assert('M=8', t1.muito_atrasado === 8);
assert('R=36', t1.rara === 36);

console.log('Casos do diagnostico (doc §2/§3):');
assert('N4:4 = quarentena (nunca M com gap 2)', cell(q3759, 'N4', 4)?.status === 'quarentena');
assert('N9:11 = quarentena (saiu em 3759)', cell(q3759, 'N9', 11)?.status === 'quarentena');
assert('N15:19 = rara (nunca A/M)', cell(q3759, 'N15', 19)?.status === 'rara');
assert('N11:23 = inviavel', cell(q3759, 'N11', 23)?.status === 'inviavel');
assert('N10:11 = atrasado (gap >= 1.75x esperado)', cell(q3759, 'N10', 11)?.status === 'atrasado');
assert('N2:6 = muito_atrasado (gap >= 3x esperado)', cell(q3759, 'N2', 6)?.status === 'muito_atrasado');

console.log('Visao por concurso (seletor):');
const { q: q3758 } = await getMatriz(3758);
assert('@3758 N9:14 = quarentena (hit 3756 dentro da janela)', cell(q3758, 'N9', 14)?.status === 'quarentena');

console.log(failures === 0 ? '\nOK — matriz confere com a referencia.' : `\n${failures} falha(s).`);
process.exit(failures === 0 ? 0 : 1);
