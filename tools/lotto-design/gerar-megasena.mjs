// Gerador OFFLINE de lotto designs para a Mega-Sena (v=60, m=6, t=4, k=7..20).
//
// Um bloco A de k dezenas cobre exatamente
//     E(k) = C(k,4)·C(60-k,2) + C(k,5)·C(60-k,1) + C(k,6)
// sorteios (os que têm 4, 5 ou 6 dezenas de A). O ganho de um candidato é obtido
// enumerando só esses sorteios e consultando um bitset global de 50M bits.
//
// Para não sofrer no "rabo" (quando quase tudo já está coberto), parte dos
// candidatos é GERADA a partir de um sorteio ainda descoberto: A = D ∪ extras.
// Assim cada passo cobre, no mínimo, aquele sorteio.
//
// Ao final, falta == 0 significa verificação EXAUSTIVA.
//
// Uso: node tools/lotto-design/gerar-megasena.mjs [kInicial] [kFinal] [poolGuiado] [poolAleatorio]
//      node --max-old-space-size=2048 tools/lotto-design/gerar-megasena.mjs 10 10 10 6
//
// Medições (2026-11-15, seed 7): k=7 → 7.621 apostas (cota 1.015); k=10 → 1.671
// apostas (cota 186). Por isso nenhum design de v=60 foi registrado — ver
// FECHAMENTO-BASELINE.md.

import { writeFileSync, readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const V = 60, M = 6, T = 4;
const TOTAL = 50063860; // C(60,6)
const WORDS = (TOTAL + 31) >>> 5;
const ARQ = fileURLToPath(new URL('../../dashboard/src/data/lotto-megasena.json', import.meta.url));

const C = Array.from({ length: V + 1 }, () => new Float64Array(M + 1));
for (let n = 0; n <= V; n++) {
  C[n][0] = 1;
  for (let j = 1; j <= M; j++) {
    if (j > n) C[n][j] = 0;
    else if (j === n) C[n][j] = 1;
    else C[n][j] = C[n - 1][j - 1] + C[n - 1][j];
  }
}
const c = (n, j) => (j < 0 || j > n ? 0 : C[n][j]);
const coberturaDoBloco = (k) => c(k, 4) * c(V - k, 2) + c(k, 5) * c(V - k, 1) + c(k, 6);

class LCG {
  constructor(seed) { this.s = (seed >>> 0) || 1; }
  next() { this.s = (this.s * 16807) % 2147483647; return (this.s - 1) / 2147483646; }
}

/** Enumera todos os sorteios D com |A∩D| >= 4, chamando visitar(rank). */
function enumerarCobertos(A, dentro, visitar) {
  const k = A.length;
  const Tt = new Int32Array(6);
  for (let a = 0; a < k - 3; a++) {
    const t0 = A[a];
    for (let b = a + 1; b < k - 2; b++) {
      const t1 = A[b];
      for (let d = b + 1; d < k - 1; d++) {
        const t2 = A[d];
        for (let e = d + 1; e < k; e++) {
          const t3 = A[e];
          for (let x = 0; x < V - 1; x++) {
            if (dentro[x]) continue;
            for (let y = x + 1; y < V; y++) {
              if (dentro[y]) continue;
              let ix = 0;
              if (t0 < x) ix++;
              if (t1 < x) ix++;
              if (t2 < x) ix++;
              if (t3 < x) ix++;
              let iy = 0;
              if (t0 < y) iy++;
              if (t1 < y) iy++;
              if (t2 < y) iy++;
              if (t3 < y) iy++;
              Tt[0] = t0; Tt[1] = t1; Tt[2] = t2; Tt[3] = t3;
              let r = C[x][ix + 1] + C[y][iy + 2];
              for (let m = 0; m < ix; m++) r += C[Tt[m]][m + 1];
              for (let m = ix; m < iy; m++) r += C[Tt[m]][m + 2];
              for (let m = iy; m < 4; m++) r += C[Tt[m]][m + 3];
              visitar(r);
            }
          }
        }
      }
    }
  }
  for (let a = 0; a < k - 4; a++) {
    const t0 = A[a];
    for (let b = a + 1; b < k - 3; b++) {
      const t1 = A[b];
      for (let d = b + 1; d < k - 2; d++) {
        const t2 = A[d];
        for (let e = d + 1; e < k - 1; e++) {
          const t3 = A[e];
          for (let f = e + 1; f < k; f++) {
            const t4 = A[f];
            for (let x = 0; x < V; x++) {
              if (dentro[x]) continue;
              Tt[0] = t0; Tt[1] = t1; Tt[2] = t2; Tt[3] = t3; Tt[4] = t4;
              let ix = 0;
              if (t0 < x) ix++;
              if (t1 < x) ix++;
              if (t2 < x) ix++;
              if (t3 < x) ix++;
              if (t4 < x) ix++;
              let r = C[x][ix + 1];
              for (let m = 0; m < ix; m++) r += C[Tt[m]][m + 1];
              for (let m = ix; m < 5; m++) r += C[Tt[m]][m + 2];
              visitar(r);
            }
          }
        }
      }
    }
  }
  if (k >= 6) {
    for (let a = 0; a < k - 5; a++) {
      const t0 = A[a];
      for (let b = a + 1; b < k - 4; b++) {
        const t1 = A[b];
        for (let d = b + 1; d < k - 3; d++) {
          const t2 = A[d];
          for (let e = d + 1; e < k - 2; e++) {
            const t3 = A[e];
            for (let f = e + 1; f < k - 1; f++) {
              const t4 = A[f];
              for (let g = f + 1; g < k; g++) {
                const t5 = A[g];
                visitar(C[t0][1] + C[t1][2] + C[t2][3] + C[t3][4] + C[t4][5] + C[t5][6]);
              }
            }
          }
        }
      }
    }
  }
}

/** Decodifica um rank de colex em M dezenas (0-based, crescente). */
function desempacotar(rank) {
  const out = new Array(M);
  let r = rank;
  for (let j = M; j >= 1; j--) {
    let n = j - 1;
    while (n + 1 <= V && C[n + 1][j] <= r) n++;
    out[j - 1] = n;
    r -= C[n][j];
  }
  return out;
}

function conjuntoAleatorio(k, rng) {
  const usados = new Set();
  while (usados.size < k) usados.add(Math.floor(rng.next() * V));
  return [...usados].sort((a, b) => a - b);
}

function construir(k, { poolGuiado = 16, poolAleatorio = 12, seed = 7, limiteMs = 3_600_000 } = {}) {
  const t0 = Date.now();
  const rng = new LCG(seed);
  const covered = new Uint32Array(WORDS);
  const dentro = new Uint8Array(V);
  const ultimaMascara = (TOTAL & 31) ? (1 << (TOTAL & 31)) - 1 : 0xffffffff;
  let falta = TOTAL;
  const escolhidos = [];
  const E = coberturaDoBloco(k);
  let cursor = 0;

  /** Sorteio ainda descoberto: tenta aleatórios e cai no cursor monotônico. */
  const descoberto = () => {
    for (let tent = 0; tent < 16; tent++) {
      const r = Math.floor(rng.next() * TOTAL);
      if ((covered[r >>> 5] & (1 << (r & 31))) === 0) return r;
    }
    while (cursor < WORDS) {
      let bits = ~covered[cursor];
      if (cursor === WORDS - 1) bits &= ultimaMascara;
      if (bits !== 0) {
        const bit = bits & -bits;
        return (cursor << 5) + (31 - Math.clz32(bit));
      }
      cursor++;
    }
    return -1;
  };

  const ganho = (A) => {
    dentro.fill(0);
    for (const p of A) dentro[p] = 1;
    let g = 0;
    enumerarCobertos(A, dentro, (r) => {
      if ((covered[r >>> 5] & (1 << (r & 31))) === 0) g++;
    });
    return g;
  };
  const marcar = (A) => {
    dentro.fill(0);
    for (const p of A) dentro[p] = 1;
    enumerarCobertos(A, dentro, (r) => {
      const w = r >>> 5, bit = 1 << (r & 31);
      if ((covered[w] & bit) === 0) { covered[w] |= bit; falta--; }
    });
  };

  while (falta > 0 && Date.now() - t0 < limiteMs) {
    let melhor = null, melhorG = 0;
    const extras = k - M;
    const r = descoberto();
    if (r >= 0) {
      const base = desempacotar(r);
      for (let c = 0; c < poolGuiado; c++) {
        const A = base.slice();
        const usados = new Set(base);
        while (A.length < k) {
          const p = Math.floor(rng.next() * V);
          if (usados.has(p)) continue;
          usados.add(p);
          A.push(p);
        }
        A.sort((x, y) => x - y);
        const g = ganho(A);
        if (g > melhorG) { melhorG = g; melhor = A; }
      }
    }
    for (let c = 0; c < poolAleatorio; c++) {
      const A = conjuntoAleatorio(k, rng);
      const g = ganho(A);
      if (g > melhorG) { melhorG = g; melhor = A; }
    }
    if (!melhor) break;
    escolhidos.push(melhor);
    marcar(melhor);
    if (escolhidos.length % 50 === 0) {
      process.stdout.write(
        `  k=${k} ${escolhidos.length} blocos · falta ${falta.toLocaleString('pt-BR')} · ${((Date.now() - t0) / 1000).toFixed(0)}s\n`,
      );
    }
  }
  return { blocos: escolhidos, falta, ms: Date.now() - t0, E };
}

const kIni = parseInt(process.argv[2] ?? '7', 10);
const kFim = parseInt(process.argv[3] ?? '20', 10);
const poolGuiado = parseInt(process.argv[4] ?? '16', 10);
const poolAleatorio = parseInt(process.argv[5] ?? '12', 10);

const registro = existsSync(ARQ) ? JSON.parse(readFileSync(ARQ, 'utf8')) : {};

for (let k = kIni; k <= kFim; k++) {
  const chave = `${V},${k},${M},${T}`;
  if (registro[chave]) { console.log(`${chave} já existe (${registro[chave].blocos.length})`); continue; }
  console.log(`\n=== k=${k} (guiado ${poolGuiado} + aleatorio ${poolAleatorio}) ===`);
  const r = construir(k, { poolGuiado, poolAleatorio, seed: 7 });
  if (r.falta !== 0) {
    console.log(`k=${k}: INCOMPLETO — ${r.falta.toLocaleString('pt-BR')} alvos sem cobertura (${(r.ms / 1000).toFixed(0)}s)`);
    continue;
  }
  const lb = Math.ceil(TOTAL / r.E);
  registro[chave] = {
    v: V, k, m: M, t: T,
    blocos: r.blocos.map((b) => b.map((p) => p + 1)),
    fonte: 'LotoScope (guloso esparso guiado por bitset sobre C(60,6); verificado por forca bruta)',
    limiteInferior: lb,
    verificado: true,
  };
  const py = (v) => JSON.stringify(v).replace(/,/g, ', ');
  const extra = `${JSON.stringify(chave)}: ${py(registro[chave])}`;
  let raw = existsSync(ARQ) ? readFileSync(ARQ, 'utf8') : '{}';
  if (raw.trim() === '{}') raw = `{${extra}}`;
  else raw = raw.slice(0, raw.lastIndexOf('}')) + ', ' + extra + '}';
  JSON.parse(raw);
  writeFileSync(ARQ, raw, 'utf8');
  console.log(`k=${k}: ${r.blocos.length} apostas · lb ${lb} · ${(r.ms / 1000).toFixed(0)}s · gravado`);
}
