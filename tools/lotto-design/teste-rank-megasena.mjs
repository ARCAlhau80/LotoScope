// Teste do rank/enumeração usados no gerador da Mega-Sena.
// Verifica: (1) quantidade == E(k); (2) nenhum rank repetido; (3) todo rank
// decodificado tem |A∩D| >= 4; (4) nenhum sorteio com |A∩D| >= 4 ficou de fora
// (checagem por amostragem ampla de todos os C(60,6) via força bruta em parte).
const V = 60, M = 6, T = 4;
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
  const scratch = new Int32Array(6);
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
              const Tt = scratch;
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
              const Tt = scratch;
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

/** Decodifica um rank de colex em 6 dezenas (0-based). */
function decodificar(rank) {
  const out = [];
  let r = rank;
  for (let j = M; j >= 1; j--) {
    let n = j - 1;
    while (n + 1 <= V && C[n + 1][j] <= r) n++;
    out.push(n);
    r -= C[n][j];
  }
  return out.sort((a, b) => a - b);
}

let falhas = 0;
for (const k of [7, 8, 10, 12, 15, 20]) {
  const A = Array.from({ length: k }, (_, i) => i * 3 % V).sort((a, b) => a - b);
  const uniq = new Set();
  const dentro = new Uint8Array(V);
  for (const p of A) dentro[p] = 1;
  let total = 0, ruim = 0, maxRank = -1;
  enumerarCobertos(A, dentro, (r) => {
    total++;
    uniq.add(r);
    if (r > maxRank) maxRank = r;
    if (r < 0 || r >= 50063860) ruim++;
  });
  // decodifica e confere |A∩D| >= 4
  let interRuim = 0;
  for (const r of uniq) {
    const D = decodificar(r);
    const inter = D.filter((x) => dentro[x]).length;
    if (inter < T) interRuim++;
    // confere que o rank decodificado volta ao mesmo valor
    let rr = 0;
    for (let i = 0; i < M; i++) rr += C[D[i]][i + 1];
    if (rr !== r) interRuim++;
  }
  const ok = total === E(k) && uniq.size === total && ruim === 0 && interRuim === 0;
  if (!ok) falhas++;
  console.log(
    `${ok ? 'OK ' : 'FALHA'} k=${k}: visitados=${total} E(k)=${E(k)} unicos=${uniq.size} foraDoRange=${ruim} ruins=${interRuim} maxRank=${maxRank}`,
  );
}
console.log(falhas === 0 ? '\nrank e enumeração OK' : `\n${falhas} caso(s) com falha`);
