// Cruzamento: Matriz de Quarentena por Posição x Reentradas/Repetidos/Persistência
// Para cada concurso i (base=i-1, anterior=i-2, sorteio=i):
//   - calcula o status da matriz de quarentena (Q/N/A/M/R/inviável) p/ cada célula (pos, num)
//     usando EXATAMENTE a mesma regra do dashboard (analise-completa.ts)
//   - classifica cada número sorteado em i como reentrada/repetido-persistente/repetido-nao-persistente
//   - cruza status x categoria e responde: a matriz tem poder preditivo?
const mssql = require('mssql');

const DB_CONFIG = {
  server: process.env.DB_SERVER || 'localhost',
  database: process.env.DB_NAME || 'Lotofacil',
  user: process.env.DB_USER || 'sa',
  password: process.env.DB_PASSWORD || 'LotoScope@2024',
  options: { trustServerCertificate: true, connectTimeout: 15000 },
};

// ---- regras da matriz (idênticas ao dashboard) ----
const JANELA_Q = 3;
const LIM_ATRASO_A = 1.75;
const LIM_ATRASO_M = 3.0;
const RARO_MIN_HITS = 10;

function logChoose(n, k) {
  if (k < 0 || k > n) return Number.NEGATIVE_INFINITY;
  let s = 0;
  for (let i = 0; i < k; i++) s += Math.log(n - i) - Math.log(i + 1);
  return s;
}
function probTeoricaPosicao(k, v, total, m) {
  return Math.exp(logChoose(v - 1, k - 1) + logChoose(total - v, m - k) - logChoose(total, m));
}

// status da matriz por posição para uma sequência de resultados ATÉ o base
// devolve: { pos: { num: 'Q'|'N'|'A'|'M'|'R'|'·' } }
function matrizQuarentena(resultados) {
  const m = 15, totalNumeros = 25;
  const totalConcursos = resultados.length;
  const positions = Array.from({ length: m }, (_, i) => `N${i + 1}`);
  const matriz = {};
  for (const pos of positions) {
    const k = parseInt(pos.substring(1), 10);
    const sequencia = resultados.map(r => r.numeros[k - 1]);
    const vMin = k, vMax = totalNumeros - m + k;
    const cells = {};
    for (let v = 1; v <= totalNumeros; v++) {
      const num = v;
      if (v < vMin || v > vMax) { cells[num] = '·'; continue; }
      const p = probTeoricaPosicao(k, v, totalNumeros, m);
      const gapEsperado = 1 / p;
      const gaps = [];
      let ultimaPos = null;
      for (let i = 0; i < sequencia.length; i++) {
        if (sequencia[i] === num) {
          if (ultimaPos !== null) gaps.push(i - ultimaPos);
          ultimaPos = i;
        }
      }
      const gapAtual = ultimaPos !== null ? sequencia.length - 1 - ultimaPos : sequencia.length;
      const raraEstrutural = p * totalConcursos < RARO_MIN_HITS;
      let status;
      if (gapAtual <= JANELA_Q - 1 && ultimaPos !== null) status = 'Q';
      else if (raraEstrutural) status = 'R';
      else if (ultimaPos === null) status = 'N';
      else if (gapAtual >= LIM_ATRASO_M * gapEsperado) status = 'M';
      else if (gapAtual >= LIM_ATRASO_A * gapEsperado) status = 'A';
      else status = 'N';
      cells[num] = status;
    }
    matriz[pos] = cells;
  }
  return matriz;
}

const STATUS_LABEL = { Q: 'Q·Quarentena', N: 'N·Normal', A: 'A·Atrasado', M: 'M·Muito Atr.', R: 'R·Rara', '·': '··Inviável' };

async function main() {
  const pool = await mssql.connect(DB_CONFIG);
  const r = await pool.request().query('SELECT Concurso,N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso');
  await mssql.close();
  const results = r.recordset.map(row => {
    const keys = Object.keys(row).filter(k => k !== 'Concurso');
    return { concurso: Number(row.Concurso), numeros: keys.map(k => Number(row[k])) };
  });
  const n = results.length;

  // categorias por número sorteado no concurso i, usando base=i-1 e anterior=i-2
  // 'reentrada' = não estava na base | 'persistente' = estava na base E no anterior | 'repetido_no' = na base mas não no anterior
  const cross = {};   // status -> categoria -> contagem
  const catTotal = {}; // categoria -> contagem
  const statTotal = {};
  const cells = {};   // status -> total de células viáveis observadas (denominador)
  const theoExp = {}; // status -> soma das probabilidades teóricas (E[números sorteados] por status)
  let totalSorteado = 0;

  for (let i = 2; i < n; i++) {
    const prev = results[i - 2].numeros;
    const base = results[i - 1].numeros;
    const sorteio = results[i].numeros;
    const prevSet = new Set(prev), baseSet = new Set(base);

    const matriz = matrizQuarentena(results.slice(0, i - 1)); // matriz conhecida ANTES do sorteio i
    for (let pIdx = 0; pIdx < 15; pIdx++) {
      const num = sorteio[pIdx];
      const pos = `N${pIdx + 1}`;
      const status = matriz[pos]?.[num] ?? '?';
      let cat;
      if (!baseSet.has(num)) cat = 'reentrada';
      else if (prevSet.has(num)) cat = 'persistente';
      else cat = 'repetido_nao_pers';
      totalSorteado++;
      catTotal[cat] = (catTotal[cat] || 0) + 1;
      statTotal[status] = (statTotal[status] || 0) + 1;
      cross[status] = cross[status] || {};
      cross[status][cat] = (cross[status][cat] || 0) + 1;
    }
    // denominador: células viáveis da matriz + esperado teórico (soma das p teóricas por status)
    for (const pos of Object.keys(matriz)) {
      const k = parseInt(pos.substring(1), 10);
      for (const num of Object.keys(matriz[pos])) {
        const st = matriz[pos][num];
        if (st === '·') continue;
        cells[st] = (cells[st] || 0) + 1;
        theoExp[st] = (theoExp[st] || 0) + probTeoricaPosicao(k, Number(num), 25, 15);
      }
    }
  }

  console.log(`=== CRUZAMENTO — MATRIZ DE QUARENTENA x REENTRADAS/REPETIDOS/PERSISTÊNCIA (${n - 2} concursos) ===`);
  console.log(`Total de números sorteados: ${totalSorteado.toLocaleString('pt-BR')}`);
  console.log('Distribuição por categoria:');
  for (const c of ['reentrada', 'persistente', 'repetido_nao_pers']) {
    console.log(`  ${c.padEnd(18)}: ${catTotal[c].toLocaleString('pt-BR')} (${((catTotal[c] / totalSorteado) * 100).toFixed(1)}%)`);
  }
  console.log();

  console.log('=== P(status da matriz | categoria do número sorteado) ===');
  console.log('categoria\t' + Object.keys(cross).map(s => STATUS_LABEL[s].padEnd(14)).join('\t'));
  for (const c of ['reentrada', 'persistente', 'repetido_nao_pers']) {
    const row = Object.keys(cross).map(s => {
      const cnt = cross[s][c] || 0;
      const pct = catTotal[c] ? ((cnt / catTotal[c]) * 100).toFixed(1) + '%' : '0%';
      return pct.padEnd(14);
    });
    console.log(`${c.padEnd(12)}\t${row.join('\t')}`);
  }
  console.log();

  // distribuição esperada se fosse aleatório (E teórico = soma das p teóricas por status)
  console.log('=== P(status) observada no sorteio vs esperada TEÓRICA (soma das p das células) ===');
  console.log('status\tobservada\tesperada\trazão');
  const theoTotal = Object.values(theoExp).reduce((a, b) => a + b, 0);
  for (const s of ['Q', 'N', 'A', 'M', 'R']) {
    const obs = statTotal[s] || 0;
    const exp = (theoExp[s] || 0) / theoTotal * totalSorteado;
    console.log(`${s.padEnd(6)}\t${((obs / totalSorteado) * 100).toFixed(2)}%\t${((exp / totalSorteado) * 100).toFixed(2)}%\t${(obs / Math.max(1, exp)).toFixed(3)}x`);
  }
  console.log();

  // preditividade: para cada status, a "mistura" de categorias observada
  console.log('=== Mistura de categorias DENTRO de cada status sorteado ===');
  for (const s of ['Q', 'N', 'A', 'M', 'R']) {
    const parts = (cross[s] || {});
    const tot = Object.values(parts).reduce((a, b) => a + b, 0);
    const fmt = c => parts[c] ? `${((parts[c] / tot) * 100).toFixed(1)}%` : '0%';
    console.log(`${s.padEnd(6)}: reentrada ${fmt('reentrada').padStart(6)} | persistente ${fmt('persistente').padStart(6)} | repetido_não_pers ${fmt('repetido_nao_pers').padStart(6)}  (${tot.toLocaleString('pt-BR')})`);
  }
}

main().catch(e => { console.error('ERRO:', e.message); process.exit(1); });
