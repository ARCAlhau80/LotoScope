// Verificação do registro da Mega-Sena.
// 1) Recalcula a cobertura de cada design LENDO O JSON (prova exaustiva: falta 0).
// 2) Para k=7 e k=20 faz uma checagem INDEPENDENTE por 4-subconjuntos: todo
//    sorteio de 6 dezenas precisa conter algum 4-subconjunto presente em algum
//    bloco (|A∩D| >= 4  <=>  algum 4-subconjunto de D está contido em A).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const V = 60, M = 6, T = 4;
const TOTAL = 50063860;
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
const E = (k) => c(k, 4) * c(V - k, 2) + c(k, 5) * c(V - k, 1) + c(k, 6);

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
              let ix = 0, iy = 0;
              if (t0 < x) ix++; if (t1 < x) ix++; if (t2 < x) ix++; if (t3 < x) ix++;
              if (t0 < y) iy++; if (t1 < y) iy++; if (t2 < y) iy++; if (t3 < y) iy++;
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
              if (t0 < x) ix++; if (t1 < x) ix++; if (t2 < x) ix++; if (t3 < x) ix++; if (t4 < x) ix++;
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

const registro = JSON.parse(readFileSync(ARQ, 'utf8'));

// ---------- 1) prova exaustiva relendo o JSON ----------
console.log('=== cobertura recalculada a partir do JSON ===');
for (const chave of Object.keys(registro)) {
  const e = registro[chave];
  const k = e.k;
  const covered = new Uint32Array(WORDS);
  const dentro = new Uint8Array(V);
  let falta = TOTAL;
  const t0 = Date.now();
  for (const bloco of e.blocos) {
    const A = bloco.map((p) => p - 1);
    dentro.fill(0);
    for (const p of A) dentro[p] = 1;
    enumerarCobertos(A, dentro, (r) => {
      const w = r >>> 5, bit = 1 << (r & 31);
      if ((covered[w] & bit) === 0) { covered[w] |= bit; falta--; }
    });
  }
  const tamOk = e.blocos.every((b) => b.length === k && new Set(b).size === k && b.every((p) => p >= 1 && p <= V));
  const lb = Math.ceil(TOTAL / E(k));
  const ok = falta === 0 && tamOk && lb === e.limiteInferior;
  console.log(
    `${ok ? 'OK ' : 'FALHA'} ${chave.padEnd(10)} apostas=${String(e.blocos.length).padStart(5)} falta=${falta} lb=${lb} (json ${e.limiteInferior}) tamOk=${tamOk} ${((Date.now() - t0) / 1000).toFixed(0)}s`,
  );
}

// ---------- 2) checagem independente por 4-subconjuntos (k=7 e k=20) ----------
const R4 = 487635; // C(60,4)
function rank4(b0, b1, b2, b3) {
  return C[b0][1] + C[b1][2] + C[b2][3] + C[b3][4];
}

console.log('\n=== checagem independente por 4-subconjuntos (amostra de 3M sorteios) ===');
for (const k of [7, 20]) {
  const chave = `${V},${k},${M},${T}`;
  const e = registro[chave];
  if (!e) { console.log(`${chave}: ausente`); continue; }
  const marcado = new Uint8Array(R4);
  for (const bloco of e.blocos) {
    const A = bloco.map((p) => p - 1);
    for (let a = 0; a < A.length - 3; a++)
      for (let b = a + 1; b < A.length - 2; b++)
        for (let d = b + 1; d < A.length - 1; d++)
          for (let f = d + 1; f < A.length; f++) marcado[rank4(A[a], A[b], A[d], A[f])] = 1;
  }
  let s = 12345 >>> 0;
  const rnd = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  let falhas = 0;
  const N = 3_000_000;
  for (let i = 0; i < N; i++) {
    // sorteio aleatório de 6 dezenas distintas
    const set = new Set();
    while (set.size < 6) set.add(Math.floor(rnd() * V));
    const D = [...set].sort((x, y) => x - y);
    let achou = 0;
    for (let a = 0; a < 3 && !achou; a++)
      for (let b = a + 1; b < 4 && !achou; b++)
        for (let d = b + 1; d < 5 && !achou; d++)
          for (let f = d + 1; f < 6 && !achou; f++)
            if (marcado[rank4(D[a], D[b], D[d], D[f])]) achou = 1;
    if (!achou) falhas++;
  }
  console.log(`${falhas === 0 ? 'OK ' : 'FALHA'} ${chave}: ${N.toLocaleString('pt-BR')} sorteios amostrados · sem cobertura = ${falhas}`);
}
