import { carregarResultados, type Resultado } from './database';
import type { DashboardData, UltimoSorteio, PrevisaoItem, AtrasadoItem, TransicaoRegistro, TransicaoQMF, CicloInfo, MediasHistoricas } from '@/types';

const POSICOES = Array.from({ length: 15 }, (_, i) => `N${i + 1}`);
const NUMEROS = Array.from({ length: 25 }, (_, i) => i + 1);
const PRIMOS = new Set([2, 3, 5, 7, 11, 13, 17, 19, 23]);
const FIBONACCI = new Set([1, 2, 3, 5, 8, 13, 21]);
const WINDOW = 50;
const ALPHA = 0.6;

function buildOcorrencias(resultados: Resultado[]): Record<string, Record<number, number[]>> {
  const occ: Record<string, Record<number, number[]>> = {};
  for (const p of POSICOES) {
    occ[p] = {};
    for (const n of NUMEROS) occ[p][n] = [];
  }
  for (let idx = 0; idx < resultados.length; idx++) {
    const r = resultados[idx];
    for (let pi = 0; pi < POSICOES.length; pi++) {
      occ[POSICOES[pi]][r.numeros[pi]].push(idx);
    }
  }
  return occ;
}

function calcularLambdas(ocorrencias: Record<string, Record<number, number[]>>, totalDraws: number) {
  const dados: Record<string, Record<number, { lambda_hist: number; lambda_recent: number; lambda_blend: number; count_hist: number; count_recent: number; gap: number }>> = {};
  for (const pos of POSICOES) {
    dados[pos] = {};
    for (const num of NUMEROS) {
      const o = ocorrencias[pos][num];
      const ch = o.length;
      const lh = totalDraws > 0 ? ch / totalDraws : 0;
      const cutoff = totalDraws - WINDOW;
      const oRec = o.filter(i => i >= cutoff);
      const cr = oRec.length;
      const lr = (totalDraws >= WINDOW && WINDOW > 0) ? cr / WINDOW : 0;
      const lb = ALPHA * lh + (1 - ALPHA) * lr;
      const ui = o.length > 0 ? Math.max(...o) : null;
      const gap = ui !== null ? totalDraws - 1 - ui : totalDraws;
      dados[pos][num] = {
        lambda_hist: Math.round(lh * 10000) / 10000,
        lambda_recent: Math.round(lr * 10000) / 10000,
        lambda_blend: Math.round(lb * 10000) / 10000,
        count_hist: ch,
        count_recent: cr,
        gap,
      };
    }
  }
  return dados;
}

function classificarQMF(freq30Window: Record<number, number>, freqTotalWindow: Record<number, number>) {
  const s = Object.entries(freq30Window).sort((a, b) => b[1] - a[1]);
  const qSet = new Set(s.slice(0, 10).map(([n]) => Number(n)));
  const sortedFrios = Object.entries(freq30Window).sort((a, b) => {
    if (a[1] !== b[1]) return a[1] - b[1];
    return (freqTotalWindow[Number(a[0])] || 0) - (freqTotalWindow[Number(b[0])] || 0);
  });
  const fSet = new Set(sortedFrios.slice(0, 10).map(([n]) => Number(n)));
  const mSet = new Set(NUMEROS.filter(n => !qSet.has(n) && !fSet.has(n)));
  return { qSet, mSet, fSet };
}

function analisarTransicaoQuentesFrios(resultados: Resultado[], janelaClass = 30, ultimosN = 100) {
  const total = resultados.length;
  const n = Math.min(ultimosN, total - janelaClass - 1);
  const registros: TransicaoRegistro[] = [];

  for (let idx = janelaClass; idx < total; idx++) {
    const window = resultados.slice(idx - janelaClass, idx);
    const freqW: Record<number, number> = {};
    const freqT: Record<number, number> = {};
    for (const n of NUMEROS) { freqW[n] = 0; freqT[n] = 0; }
    for (let ri = 0; ri < idx; ri++) {
      for (const nu of resultados[ri].numeros) freqT[nu] = (freqT[nu] || 0) + 1;
    }
    for (const r of window) {
      for (const nu of r.numeros) freqW[nu] = (freqW[nu] || 0) + 1;
    }

    const { qSet, mSet, fSet } = classificarQMF(freqW, freqT);
    const numsSaidos = resultados[idx].numeros;
    const qtdQ = numsSaidos.filter(n => qSet.has(n)).length;
    const qtdM = numsSaidos.filter(n => mSet.has(n)).length;
    const qtdF = numsSaidos.filter(n => fSet.has(n)).length;

    registros.push({
      concurso: resultados[idx].concurso,
      quentes: qtdQ, mornos: qtdM, frios: qtdF,
      pct_q: Math.round(qtdQ / 15 * 100 * 10) / 10,
      pct_m: Math.round(qtdM / 15 * 100 * 10) / 10,
      pct_f: Math.round(qtdF / 15 * 100 * 10) / 10,
      q_set: [...qSet].sort((a, b) => a - b),
      m_set: [...mSet].sort((a, b) => a - b),
      f_set: [...fSet].sort((a, b) => a - b),
    });
  }

  const medias = {
    quentes: Math.round(registros.reduce((s, r) => s + r.quentes, 0) / registros.length * 100) / 100,
    mornos: Math.round(registros.reduce((s, r) => s + r.mornos, 0) / registros.length * 100) / 100,
    frios: Math.round(registros.reduce((s, r) => s + r.frios, 0) / registros.length * 100) / 100,
    pct_q: Math.round(registros.reduce((s, r) => s + r.pct_q, 0) / registros.length * 10) / 10,
    pct_m: Math.round(registros.reduce((s, r) => s + r.pct_m, 0) / registros.length * 10) / 10,
    pct_f: Math.round(registros.reduce((s, r) => s + r.pct_f, 0) / registros.length * 10) / 10,
    total_sorteios: registros.length,
  };

  const recentes = registros.slice(-20);
  const meio = Math.floor(registros.length / 2);
  const antiga = registros.slice(0, meio);
  const recente = registros.slice(-meio);

  const tendencia = {
    quentes: Math.round((recente.reduce((s, r) => s + r.quentes, 0) / recente.length - antiga.reduce((s, r) => s + r.quentes, 0) / antiga.length) * 100) / 100,
    mornos: Math.round((recente.reduce((s, r) => s + r.mornos, 0) / recente.length - antiga.reduce((s, r) => s + r.mornos, 0) / antiga.length) * 100) / 100,
    frios: Math.round((recente.reduce((s, r) => s + r.frios, 0) / recente.length - antiga.reduce((s, r) => s + r.frios, 0) / antiga.length) * 100) / 100,
  };

  return { medias, recentes, tendencia };
}

function calcularMediasHistoricas(resultados: Resultado[]): MediasHistoricas {
  let somaSoma = 0, somaPares = 0, somaImpares = 0, somaPrimos = 0;
  let somaFib = 0, somaRep = 0, somaConsec = 0, somaAmp = 0;
  let somaBaixos = 0, somaAltos = 0, somaMult3 = 0, somaMult5 = 0;
  const t = resultados.length;

  for (let i = 0; i < t; i++) {
    const nums = resultados[i].numeros;
    const sorted = [...nums].sort((a, b) => a - b);
    somaSoma += nums.reduce((s, n) => s + n, 0);
    somaPares += nums.filter(n => n % 2 === 0).length;
    somaImpares += nums.filter(n => n % 2 === 1).length;
    somaPrimos += nums.filter(n => PRIMOS.has(n)).length;
    somaFib += nums.filter(n => FIBONACCI.has(n)).length;
    somaBaixos += nums.filter(n => n <= 12).length;
    somaAltos += nums.filter(n => n >= 13).length;
    somaMult3 += nums.filter(n => n % 3 === 0).length;
    somaMult5 += nums.filter(n => n % 5 === 0).length;
    somaAmp += Math.max(...nums) - Math.min(...nums);
    let consec = 0;
    for (let j = 1; j < sorted.length; j++) {
      if (sorted[j] - sorted[j - 1] === 1) consec++;
    }
    somaConsec += consec;
    if (i > 0) {
      const prevSet = new Set(resultados[i - 1].numeros);
      somaRep += nums.filter(n => prevSet.has(n)).length;
    }
  }

  const r = (v: number, n: number = t) => Math.round(v / n * 100) / 100;
  return {
    soma: r(somaSoma),
    pares: r(somaPares),
    impares: r(somaImpares),
    primos: r(somaPrimos),
    fibonacci: r(somaFib),
    repetidos: r(somaRep, t - 1),
    consecutivas: r(somaConsec),
    amplitude: r(somaAmp),
    baixos: r(somaBaixos),
    altos: r(somaAltos),
    multiplos_3: r(somaMult3),
    multiplos_5: r(somaMult5),
  };
}

export async function analiseCompleta(janela?: number): Promise<DashboardData> {
  const resultados = await carregarResultados();
  const total = resultados.length;
  const occ = buildOcorrencias(resultados);
  const dados = calcularLambdas(occ, total);
  const ultimo = resultados[total - 1];

  const janelaValida = Math.max(2, Math.min(janela ?? 30, total));

  const freqTotal: Record<number, number> = {};
  for (const n of NUMEROS) freqTotal[n] = 0;
  for (const r of resultados) {
    for (const n of r.numeros) freqTotal[n]++;
  }

  const freq30: Record<number, number> = {};
  for (const n of NUMEROS) freq30[n] = 0;
  for (const r of resultados.slice(-janelaValida)) {
    for (const n of r.numeros) freq30[n]++;
  }

  const gaps: Record<number, number> = {};
  for (const n of NUMEROS) {
    let last = -1;
    for (let idx = 0; idx < resultados.length; idx++) {
      if (resultados[idx].numeros.includes(n)) last = idx;
    }
    gaps[n] = total - 1 - last;
  }

  const sortedFreq = Object.entries(freq30).sort((a, b) => b[1] - a[1]);
  const quentes: [number, number][] = sortedFreq.slice(0, 10).map(([n, f]) => [Number(n), f]);
  const frios: [number, number][] = Object.entries(freq30)
    .sort((a, b) => {
      if (a[1] !== b[1]) return a[1] - b[1];
      return freqTotal[Number(a[0])] - freqTotal[Number(b[0])];
    })
    .slice(0, 10)
    .map(([n, f]) => [Number(n), f]);
  const quentesSet = new Set(quentes.map(([n]) => n));
  const friosSet = new Set(frios.map(([n]) => n));
  const mornos: [number, number][] = sortedFreq
    .filter(([n]) => !quentesSet.has(Number(n)) && !friosSet.has(Number(n)))
    .map(([n, f]) => [Number(n), f]);

  const previsao: Record<string, PrevisaoItem[]> = {};
  for (const pos of POSICOES) {
    const nums = dados[pos];
    const top3 = Object.entries(nums)
      .filter(([_, v]) => v.lambda_blend > 0)
      .sort((a, b) => b[1].lambda_blend - a[1].lambda_blend)
      .slice(0, 3)
      .map(([n, v]) => ({ numero: Number(n), prob: Math.round(v.lambda_blend * 10000) / 10000 }));
    previsao[pos] = top3;
  }

  const palpite: number[] = POSICOES.map(p => previsao[p][0].numero);

  function contarConsecutivos(n: number): number {
    let count = 0;
    for (const r of resultados.slice(-15)) {
      if (r.numeros.includes(n)) count++;
      else break;
    }
    return count;
  }

  function gerarPrevisaoCombinada(
    cadeiaRep: number[],
    repUltimo: number[]
  ): number[] {
    const freq5: Record<number, number> = {};
    const freq15: Record<number, number> = {};
    const freq30rec: Record<number, number> = {};
    for (const n of NUMEROS) {
      freq5[n] = 0; freq15[n] = 0; freq30rec[n] = 0;
    }
    for (const r of resultados.slice(-5)) for (const n of r.numeros) freq5[n]++;
    for (const r of resultados.slice(-15)) for (const n of r.numeros) freq15[n]++;
    for (const r of resultados.slice(-30)) for (const n of r.numeros) freq30rec[n]++;

    const cadeiaSet = new Set(cadeiaRep);
    const repSet = new Set(repUltimo);

    // Compute per-number aggregate Poisson scores and ciclo direction
    const aggPoisson: Record<number, number> = {};
    const freqEsperada = total > 0 ? Object.values(freqTotal).reduce((s, v) => s + v, 0) / 25 / total * 30 : 18;
    for (const n of NUMEROS) {
      aggPoisson[n] = Object.values(dados).reduce((s, pos) => s + (pos[n]?.lambda_blend || 0), 0);
    }

    const invertidaScores: { num: number; score: number }[] = [];
    for (const n of NUMEROS) {
      const f5 = (freq5[n] / 5) * 100;
      const fm = (freq15[n] / 15) * 100;
      const f30pct = (freq30rec[n] / 30) * 100;
      const consec = contarConsecutivos(n);
      const diff = freq30rec[n] - freqEsperada;
      let score = 0;

      if (consec >= 10) score -= 5;
      else if (consec >= 5) score += 6;
      else if (consec >= 4) score += 5;
      else if (consec >= 3 && f5 >= 80) score += 4;
      else if (consec >= 3) score += 3;
      else if (f5 >= 100) score += 4;
      else if (f5 >= 80) score += 3;

      // Multi-scale factor (J5/J15/J30) — trend direction
      // CONSOL: quente nas 3 janelas → deve esfriar (score +2)
      // EMERG: quente em J5 mas nao em J30 → tendencia alta, proteger (score -2)
      // DECAD: frio em J5 mas quente em J30 → ja esfriou, reforcar exclusao (score +3)
      // FRIO: frio nas 3 → pode voltar, proteger leve (score -1)
      const j5q = f5 >= 70;
      const j15q = fm >= 70;
      const j30q = f30pct >= 70;
      const j5f = f5 < 50;
      const j30f = f30pct < 50;

      if (j5q && j15q && j30q) score += 2;
      else if (j5q && !j30q) score -= 2;
      else if (!j5q && j30q) score += 3;
      else if (j5f && j30f && (f30pct < 50)) score -= 1;

      // Ciclo direction: subindo (+) ou descendo (-)
      if (diff > 1.5) score += 1.5;
      else if (diff < -1.5) score -= 1;

      if (cadeiaSet.has(n)) score -= 8;
      else if (repSet.has(n)) score -= 3;

      invertidaScores.push({ num: n, score });
    }

    invertidaScores.sort((a, b) => b.score - a.score);
    const excluir = new Set(invertidaScores.slice(0, 2).map(x => x.num));
    const pool23 = NUMEROS.filter(n => !excluir.has(n));

    // Compute sum target from recent trend
    const ultimosSomas = resultados.slice(-10).map(r => r.numeros.reduce((a, b) => a + b, 0));
    const mediaSomaRecente = ultimosSomas.reduce((a, b) => a + b, 0) / ultimosSomas.length;
    const somaHist = resultados.reduce((s, r) => s + r.numeros.reduce((a, b) => a + b, 0), 0) / resultados.length;
    const sumTarget = Math.round((mediaSomaRecente + somaHist) / 2);

    // Score each number with sum-bias: if target > media, prefer slightly higher numbers
    const sumBiasDirection = sumTarget - somaHist;
    const sumBias = (n: number) => (n - 13) * (sumBiasDirection / 30);

    const usado = new Set<number>();
    const resultado: number[] = [];
    for (const pos of POSICOES) {
      const candidatos = (previsao[pos] || [])
        .filter(p => pool23.includes(p.numero) && !usado.has(p.numero))
        .sort((a, b) => {
          const diff = (b.prob - a.prob) + sumBias(b.numero) - sumBias(a.numero);
          return diff;
        });
      if (candidatos.length > 0) {
        resultado.push(candidatos[0].numero);
        usado.add(candidatos[0].numero);
      }
    }

    if (resultado.length < 15) {
      const restantes = pool23.filter(n => !usado.has(n)).sort((a, b) => {
        const sa = aggPoisson[a] + sumBias(a);
        const sb = aggPoisson[b] + sumBias(b);
        return sb - sa;
      });
      for (const n of restantes) {
        if (resultado.length >= 15) break;
        resultado.push(n);
        usado.add(n);
      }
    }

    return resultado.sort((a, b) => a - b);
  }

  const atrasadosPos: Record<string, AtrasadoItem[]> = {};
  for (const pos of POSICOES) {
    const atr: AtrasadoItem[] = [];
    for (const n of NUMEROS) {
      const gap = dados[pos][n].gap;
      const lb = dados[pos][n].lambda_blend;
      const pGap = lb > 0 ? Math.exp(-lb * gap) : 1.0;
      if (pGap < 0.05 && gap > 0) {
        atr.push({ numero: n, p_gap: Math.round(pGap * 10000) / 10000, gap, lambda_blend: lb });
      }
    }
    if (atr.length > 0) {
      atrasadosPos[pos] = atr.sort((a, b) => a.p_gap - b.p_gap);
    }
  }

  const freqHistorica: Record<number, number> = {};
  for (const n of NUMEROS) {
    freqHistorica[n] = freqTotal[n] / total * janelaValida;
  }
  const ciclos: Record<string, CicloInfo> = {};
  for (const n of NUMEROS) {
    const diff = freq30[n] - freqHistorica[n];
    let estado: 'aquecendo' | 'esfriando' | 'estavel';
    if (diff > 1.5) estado = 'aquecendo';
    else if (diff < -1.5) estado = 'esfriando';
    else estado = 'estavel';
    ciclos[n] = {
      freq_30: freq30[n],
      freq_esperada: Math.round(freqHistorica[n] * 10) / 10,
      diferenca: Math.round(diff * 10) / 10,
      estado,
    };
  }

  const numsUltimo = ultimo.numeros;
  const penultimo = total > 1 ? resultados[total - 2] : null;
  const numsPenultimo = penultimo ? penultimo.numeros : [];
  const numsUltimoSet = new Set(numsUltimo);
  const numsPenultimoSet = new Set(numsPenultimo);
  const repetidosNumeros = numsPenultimo.filter(n => numsUltimoSet.has(n));
  const antepenultimo = total > 2 ? resultados[total - 3] : null;
  const numsAntepenultimo = antepenultimo ? antepenultimo.numeros : [];
  const repetidosCadeia = numsAntepenultimo.filter(n => numsPenultimoSet.has(n) && numsUltimoSet.has(n));
  const previsaoCombinada = gerarPrevisaoCombinada(repetidosCadeia, repetidosNumeros);
  const fibonacciNumeros = numsUltimo.filter(n => FIBONACCI.has(n));
  const sorted = [...numsUltimo].sort((a, b) => a - b);
  const consecPares: string[] = [];
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i] - sorted[i - 1] === 1) consecPares.push(`${sorted[i - 1]}-${sorted[i]}`);
  }
  const baixosNumeros = numsUltimo.filter(n => n <= 12);
  const altosNumeros = numsUltimo.filter(n => n >= 13);
  const mult3 = numsUltimo.filter(n => n % 3 === 0);
  const mult5 = numsUltimo.filter(n => n % 5 === 0);
  const ultimoStats: UltimoSorteio = {
    concurso: ultimo.concurso,
    numeros: numsUltimo,
    soma: numsUltimo.reduce((a, b) => a + b, 0),
    pares: numsUltimo.filter(n => n % 2 === 0).length,
    pares_numeros: numsUltimo.filter(n => n % 2 === 0),
    impares: numsUltimo.filter(n => n % 2 === 1).length,
    impares_numeros: numsUltimo.filter(n => n % 2 === 1),
    primos: numsUltimo.filter(n => PRIMOS.has(n)).length,
    primos_numeros: numsUltimo.filter(n => PRIMOS.has(n)),
    fibonacci: fibonacciNumeros.length,
    fibonacci_numeros: fibonacciNumeros,
    repetidos: repetidosNumeros.length,
    repetidos_numeros: repetidosNumeros,
    consecutivas: consecPares.length,
    consecutivas_pares: consecPares,
    amplitude: Math.max(...numsUltimo) - Math.min(...numsUltimo),
    baixos: baixosNumeros.length,
    baixos_numeros: baixosNumeros,
    altos: altosNumeros.length,
    altos_numeros: altosNumeros,
    multiplos_3: mult3.length,
    multiplos_3_numeros: mult3,
    multiplos_5: mult5.length,
    multiplos_5_numeros: mult5,
  };

  const transicao: TransicaoQMF = analisarTransicaoQuentesFrios(resultados, janelaValida);

  const mediasHistoricas = calcularMediasHistoricas(resultados);

  const frequenciaTotalRecord: Record<string, number> = {};
  const frequencia30Record: Record<string, number> = {};
  const gapsRecord: Record<string, number> = {};
  for (const n of NUMEROS) {
    frequenciaTotalRecord[String(n)] = freqTotal[n];
    frequencia30Record[String(n)] = freq30[n];
    gapsRecord[String(n)] = gaps[n];
  }

  return {
    ultimo_concurso: ultimo.concurso,
    total_sorteios: total,
    ultimo_sorteio: ultimoStats,
    frequencia_total: frequenciaTotalRecord,
    frequencia_30: frequencia30Record,
    gaps: gapsRecord,
    numeros_quentes: quentes,
    numeros_frios: frios,
    numeros_mornos: mornos,
    previsao_posicional: previsao,
    palpite,
    previsao_combinada: previsaoCombinada,
    atrasados_posicionais: atrasadosPos,
    ciclos,
    transicao_qmf: transicao,
    medias_historicas: mediasHistoricas,
    janela_usada: janelaValida,
    timestamp: new Date().toISOString(),
    repetidos_cadeia: repetidosCadeia,
  };
}
