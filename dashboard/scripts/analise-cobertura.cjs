// Analise de cobertura: Reentradas / Repetidos / Persistencia na Lotofacil
// Calcula exatamente (por combinatoria) quantos jogos de 15 dezenas satisfazem
// as restricoes, e compara cobertura maxima vs core vs aleatorio do mesmo tamanho,
// em 300 concursos da base historica.
const mssql = require('mssql');

const DB_CONFIG = {
  server: process.env.DB_SERVER || 'localhost',
  database: process.env.DB_NAME || 'Lotofacil',
  user: process.env.DB_USER || 'sa',
  password: process.env.DB_PASSWORD || 'LotoScope@2024',
  options: { trustServerCertificate: true, connectTimeout: 15000 },
};

// ---------- combinatória ----------
function nCk(n, k) {
  if (k < 0 || k > n) return 0;
  k = Math.min(k, n - k);
  let r = 1;
  for (let i = 0; i < k; i++) r = (r * (n - i)) / (i + 1);
  return Math.round(r);
}
const C = nCk;
const TOTAL = C(25, 15); // 3.268.760

// ---------- restrições ----------
// Repetidos  = |combo ∩ base|
// Reentradas = 15 - Repetidos (complementar)
// Persistência = |combo ∩ (base ∩ anterior)|
const MAX = { repMin: 7, repMax: 11, perMin: 4, perMax: 7 };   // cobertura máxima
const CORE = { repMin: 8, repMax: 10, perMin: 4, perMax: 6 };   // core

// Compartimentos:
//   R = base ∩ anterior          (pool de persistência)   |R| = s
//   A = base \ anterior                                    |A| = 15 - s
//   E = nem base nem anterior                              |E| = s - 5
//   D = anterior \ base                                    |D| = 15 - s
function compartments(B, P) {
  const s = B.filter(n => P.includes(n)).length;
  const R = B.filter(n => P.includes(n));
  const A = B.filter(n => !P.includes(n));
  const E = Array.from({ length: 25 }, (_, i) => i + 1).filter(n => !B.includes(n) && !P.includes(n));
  const D = P.filter(n => !B.includes(n));
  return { s, R, A, E, D };
}

// Número total de jogos que satisfazem a cobertura (sem depender de T)
function coberturaCount(B, P, cfg) {
  const { s } = compartments(B, P);
  let total = 0;
  for (let x = cfg.perMin; x <= cfg.perMax && x <= s; x++) {
    const yMin = Math.max(0, cfg.repMin - x);
    const yMax = Math.min(15 - s, cfg.repMax - x);
    for (let y = yMin; y <= yMax; y++) {
      const rem = 15 - x - y;
      for (let z = 0; z <= rem && z <= s - 5; z++) {
        const w = rem - z;
        if (w < 0 || w > 15 - s) continue;
        total += C(s, x) * C(15 - s, y) * C(s - 5, z) * C(15 - s, w);
      }
    }
  }
  return total;
}

// Distribuição exata de acertos (vs T) da cobertura sobre base B e anterior P.
function coberturaHitDistribution(B, P, T, cfg) {
  const { s, R, A, E, D } = compartments(B, P);
  const tR = R.filter(n => T.includes(n)).length;
  const tA = A.filter(n => T.includes(n)).length;
  const tE = E.filter(n => T.includes(n)).length;
  const tD = D.filter(n => T.includes(n)).length;

  const counts = new Array(16).fill(0);

  for (let x = cfg.perMin; x <= cfg.perMax && x <= s; x++) {
    const yMin = Math.max(0, cfg.repMin - x);
    const yMax = Math.min(15 - s, cfg.repMax - x);
    for (let y = yMin; y <= yMax; y++) {
      const rem = 15 - x - y;
      for (let z = 0; z <= rem && z <= s - 5; z++) {
        const w = rem - z;
        if (w < 0 || w > 15 - s) continue;
        for (let hR = 0; hR <= Math.min(x, tR); hR++) {
          const aR = C(tR, hR) * C(s - tR, x - hR);
          if (!aR) continue;
          for (let hA = 0; hA <= Math.min(y, tA); hA++) {
            const aA = C(tA, hA) * C(15 - s - tA, y - hA);
            if (!aA) continue;
            for (let hE = 0; hE <= Math.min(z, tE); hE++) {
              const aE = C(tE, hE) * C(s - 5 - tE, z - hE);
              if (!aE) continue;
              for (let hD = 0; hD <= Math.min(w, tD); hD++) {
                const aD = C(tD, hD) * C(15 - s - tD, w - hD);
                if (!aD) continue;
                const h = hR + hA + hE + hD;
                if (h <= 15) counts[h] += aR * aA * aE * aD;
              }
            }
          }
        }
      }
    }
  }
  return counts;
}

// distribuição esperada de acertos de `k` jogos aleatórios uniformes
function randomHitDistribution(k) {
  const d = new Array(16).fill(0);
  for (let h = 0; h <= 15; h++) {
    d[h] = (C(15, h) * C(10, 15 - h)) / TOTAL * k;
  }
  return d;
}
const SUM = (d, lo) => d.slice(lo).reduce((a, b) => a + b, 0);

async function main() {
  const pool = await mssql.connect(DB_CONFIG);
  const r = await pool.request().query('SELECT Concurso,N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT ORDER BY Concurso');
  await mssql.close();
  const results = r.recordset.map(row => {
    const keys = Object.keys(row).filter(k => k !== 'Concurso');
    return { concurso: Number(row.Concurso), numeros: keys.map(k => Number(row[k])) };
  });
  const n = results.length;

  // ---------- validação empírica das hipóteses do usuário ----------
  const distRep = {}, distRee = {}, distPer = {};
  for (let i = 1; i < n; i++) {
    const base = results[i - 1].numeros, T = results[i].numeros;
    const rep = base.filter(x => T.includes(x)).length;
    distRep[rep] = (distRep[rep] || 0) + 1;
    distRee[15 - rep] = (distRee[15 - rep] || 0) + 1;
  }
  for (let i = 2; i < n; i++) {
    const P = results[i - 2].numeros, B = results[i - 1].numeros, T = results[i].numeros;
    const R = B.filter(x => P.includes(x));
    const per = R.filter(x => T.includes(x)).length;
    distPer[per] = (distPer[per] || 0) + 1;
  }
  const totRep = n - 1, totPer = n - 2;
  const pctIn = (dist, min, max, total) => {
    let c = 0;
    for (let k = min; k <= max; k++) c += dist[k] || 0;
    return ((c / total) * 100).toFixed(1) + '%';
  };
  console.log('=== VALIDAÇÃO EMPÍRICA (toda a base, %s concursos) ===', n);
  console.log('Repetidos  4-8 :', pctIn(distRep, 4, 8, totRep));
  console.log('Repetidos  7-11:', pctIn(distRep, 7, 11, totRep));
  console.log('Reentradas 4-8 :', pctIn(distRee, 4, 8, totRep));
  console.log('Repetidos core 8-10:', pctIn(distRep, 8, 10, totRep));
  console.log('Persistência 4-7:', pctIn(distPer, 4, 7, totPer));
  console.log('Persistência core 4-6:', pctIn(distPer, 4, 6, totPer));
  console.log('Repetidos: ', JSON.stringify(distRep));
  console.log('Persistência: ', JSON.stringify(distPer));
  console.log('Total de combinações possíveis: C(25,15) =', TOTAL.toLocaleString('pt-BR'));
  console.log();

  // ---------- 300 concursos: comparativo ----------
  const W = 300;
  const start = n - W - 1; // precisa de i-2
  let sumKMax = 0, sumKCore = 0;
  let captMax = 0, captCore = 0;
  const agg = { max: new Array(16).fill(0), core: new Array(16).fill(0), rndMax: new Array(16).fill(0), rndCore: new Array(16).fill(0) };

  for (let i = start + 2; i < n; i++) {
    const P = results[i - 2].numeros, B = results[i - 1].numeros, T = results[i].numeros;
    const Kmax = coberturaCount(B, P, MAX);
    const Kcore = coberturaCount(B, P, CORE);
    sumKMax += Kmax; sumKCore += Kcore;

    const repT = B.filter(x => T.includes(x)).length;
    const R = B.filter(x => P.includes(x));
    const perT = R.filter(x => T.includes(x)).length;
    if (repT >= MAX.repMin && repT <= MAX.repMax && perT >= MAX.perMin && perT <= MAX.perMax) captMax++;
    if (repT >= CORE.repMin && repT <= CORE.repMax && perT >= CORE.perMin && perT <= CORE.perMax) captCore++;

    const hMax = coberturaHitDistribution(B, P, T, MAX);
    const hCore = coberturaHitDistribution(B, P, T, CORE);
    const rMax = randomHitDistribution(Kmax);
    const rCore = randomHitDistribution(Kcore);
    for (let h = 0; h <= 15; h++) {
      agg.max[h] += hMax[h];
      agg.core[h] += hCore[h];
      agg.rndMax[h] += rMax[h];
      agg.rndCore[h] += rCore[h];
    }
  }

  const avgKMax = sumKMax / W, avgKCore = sumKCore / W;
  console.log('=== COMPARATIVO — ÚLTIMOS %s CONCURSOS (média por concurso) ===', W);
  console.log(`Cobertura MÁXIMA : média ${avgKMax.toLocaleString('pt-BR')} jogos/concurso  (${((avgKMax / TOTAL) * 100).toFixed(2)}% do total C(25,15))`);
  console.log(`Cobertura CORE   : média ${avgKCore.toLocaleString('pt-BR')} jogos/concurso  (${((avgKCore / TOTAL) * 100).toFixed(2)}% do total)`);
  console.log(`Redução vs total : máx ${(((1 - avgKMax / TOTAL)) * 100).toFixed(2)}% | core ${(((1 - avgKCore / TOTAL)) * 100).toFixed(2)}%`);
  console.log(`Captura do vencedor (T pertence à cobertura): máx = ${captMax}/${W} (${((captMax / W) * 100).toFixed(1)}%), core = ${captCore}/${W} (${((captCore / W) * 100).toFixed(1)}%)`);
  console.log();

  const label = ['MAX', 'CORE', 'RND_MAX', 'RND_CORE'];
  const sets = { MAX: agg.max, CORE: agg.core, RND_MAX: agg.rndMax, RND_CORE: agg.rndCore };
  console.log(`Acertos acumulados em ${W} concursos (jogos que acertam >= k):`);
  console.log('k\tMAX\tCORE\tRND_MAX\tRND_CORE');
  for (const k of [11, 12, 13, 14, 15]) {
    const row = label.map(l => Math.round(SUM(sets[l], k)).toLocaleString('pt-BR'));
    console.log(`${k}\t${row.join('\t')}`);
  }
  console.log();

  const eff = l => SUM(sets[l], 11) / (l === 'MAX' || l === 'RND_MAX' ? sumKMax : sumKCore);
  console.log(`Eficiência por jogo — P(jogo acerta >=11) em ${W} concursos:`);
  for (const l of ['MAX', 'CORE', 'RND_MAX', 'RND_CORE']) {
    console.log(`  ${l.padEnd(8)}: ${(eff(l) * 100).toFixed(3)}%`);
  }
  console.log();

  // -------- custo / ganho ----------
  const PREÇO = 3.5; // R$ por jogo de 15 dezenas
  // 14 e 15 são VARIÁVEIS na Caixa (percentuais); aqui usamos estimativas atuais observadas
  const PRIZE = { 11: 7, 12: 14, 13: 35, 14: 2400, 15: 2250000 };
  console.log('=== CUSTO x GANHO (média por concurso, apostando TODA a cobertura) ===');
  for (const [name, K, hits] of [['MÁXIMA', avgKMax, agg.max], ['CORE', avgKCore, agg.core]]) {
    const custo = K * PREÇO;
    let ganho = 0;
    for (const k of [11, 12, 13, 14, 15]) ganho += hits[k] / W * PRIZE[k];
    console.log(`  ${name}: custo R$ ${custo.toLocaleString('pt-BR', { maximumFractionDigits: 2 })} | ganho esperado R$ ${ganho.toLocaleString('pt-BR', { maximumFractionDigits: 0 })} | ROI ${((ganho / custo - 1) * 100).toFixed(1)}%`);
  }
  console.log();
  console.log('Aleatório (mesmo tamanho) — ganho esperado por concurso:');
  for (const [name, K, hits] of [['RND_MAX', avgKMax, agg.rndMax], ['RND_CORE', avgKCore, agg.rndCore]]) {
    const custo = K * PREÇO;
    let ganho = 0;
    for (const k of [11, 12, 13, 14, 15]) ganho += hits[k] / W * PRIZE[k];
    console.log(`  ${name}: custo R$ ${custo.toLocaleString('pt-BR', { maximumFractionDigits: 2 })} | ganho esperado R$ ${ganho.toLocaleString('pt-BR', { maximumFractionDigits: 0 })} | ROI ${((ganho / custo - 1) * 100).toFixed(1)}%`);
  }
}

main().catch(e => { console.error('ERRO:', e.message); process.exit(1); });
