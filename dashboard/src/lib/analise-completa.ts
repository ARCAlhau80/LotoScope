import { carregarResultados, type Resultado } from './database';
import { getLotteryConfig, type LotteryConfig } from './lottery-config';
import type { DashboardData, UltimoSorteio, PrevisaoItem, AtrasadoItem, TransicaoRegistro, TransicaoQMF, CicloInfo, MediasHistoricas } from '@/types';

const WINDOW = 50;
const ALPHA = 0.6;

function buildOcorrencias(resultados: Resultado[], cfg: LotteryConfig): Record<string, Record<number, number[]>> {
  const positions = Array.from({ length: cfg.numeros_por_jogo }, (_, i) => `N${i + 1}`);
  const nums = Array.from({ length: cfg.total_numeros }, (_, i) => i + cfg.numero_minimo);
  const occ: Record<string, Record<number, number[]>> = {};
  for (const p of positions) {
    occ[p] = {};
    for (const n of nums) occ[p][n] = [];
  }
  for (let idx = 0; idx < resultados.length; idx++) {
    const r = resultados[idx];
    for (let pi = 0; pi < positions.length; pi++) {
      occ[positions[pi]][r.numeros[pi]].push(idx);
    }
  }
  return occ;
}

function calcularLambdas(
  ocorrencias: Record<string, Record<number, number[]>>,
  totalDraws: number,
  cfg: LotteryConfig
) {
  const nums = Array.from({ length: cfg.total_numeros }, (_, i) => i + cfg.numero_minimo);
  const positions = Array.from({ length: cfg.numeros_por_jogo }, (_, i) => `N${i + 1}`);
  const dados: Record<string, Record<number, { lambda_hist: number; lambda_recent: number; lambda_blend: number; count_hist: number; count_recent: number; gap: number }>> = {};
  for (const pos of positions) {
    dados[pos] = {};
    for (const num of nums) {
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

function classificarQMF(
  freq30Window: Record<number, number>,
  freqTotalWindow: Record<number, number>,
  cfg: LotteryConfig
) {
  const qty = cfg.qmf_scale;
  const s = Object.entries(freq30Window).sort((a, b) => b[1] - a[1]);
  const qSet = new Set(s.slice(0, qty).map(([n]) => Number(n)));
  const sortedFrios = Object.entries(freq30Window).sort((a, b) => {
    if (a[1] !== b[1]) return a[1] - b[1];
    return (freqTotalWindow[Number(a[0])] || 0) - (freqTotalWindow[Number(b[0])] || 0);
  });
  const fSet = new Set(sortedFrios.slice(0, qty).map(([n]) => Number(n)));
  const allNums = Array.from({ length: cfg.total_numeros }, (_, i) => i + cfg.numero_minimo);
  const mSet = new Set(allNums.filter(n => !qSet.has(n) && !fSet.has(n)));
  return { qSet, mSet, fSet };
}

function analisarTransicaoQuentesFrios(
  resultados: Resultado[],
  cfg: LotteryConfig,
  janelaClass = 30,
  ultimosN = 100
) {
  const total = resultados.length;
  const n = Math.min(ultimosN, total - janelaClass - 1);
  const registros: TransicaoRegistro[] = [];
  const allNums = Array.from({ length: cfg.total_numeros }, (_, i) => i + cfg.numero_minimo);

  for (let idx = janelaClass; idx < total; idx++) {
    const window = resultados.slice(idx - janelaClass, idx);
    const freqW: Record<number, number> = {};
    const freqT: Record<number, number> = {};
    for (const n of allNums) { freqW[n] = 0; freqT[n] = 0; }
    for (let ri = 0; ri < idx; ri++) {
      for (const nu of resultados[ri].numeros) freqT[nu] = (freqT[nu] || 0) + 1;
    }
    for (const r of window) {
      for (const nu of r.numeros) freqW[nu] = (freqW[nu] || 0) + 1;
    }

    const { qSet, mSet, fSet } = classificarQMF(freqW, freqT, cfg);
    const numsSaidos = resultados[idx].numeros;
    const qtdQ = numsSaidos.filter(n => qSet.has(n)).length;
    const qtdM = numsSaidos.filter(n => mSet.has(n)).length;
    const qtdF = numsSaidos.filter(n => fSet.has(n)).length;

    registros.push({
      concurso: resultados[idx].concurso,
      quentes: qtdQ, mornos: qtdM, frios: qtdF,
      pct_q: Math.round(qtdQ / cfg.numeros_por_jogo * 100 * 10) / 10,
      pct_m: Math.round(qtdM / cfg.numeros_por_jogo * 100 * 10) / 10,
      pct_f: Math.round(qtdF / cfg.numeros_por_jogo * 100 * 10) / 10,
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

function calcularMediasHistoricas(resultados: Resultado[], cfg: LotteryConfig): MediasHistoricas {
  let somaSoma = 0, somaPares = 0, somaImpares = 0, somaPrimos = 0;
  let somaFib = 0, somaRep = 0, somaConsec = 0, somaAmp = 0;
  let somaBaixos = 0, somaAltos = 0;
  let somaMult3 = 0, somaMult5 = 0;
  const t = resultados.length;
  const primosSet = new Set(cfg.primos);
  const fibSet = new Set(cfg.fibonacci);
  const meio = Math.floor((cfg.numero_minimo + cfg.numero_maximo) / 2);

  for (let i = 0; i < t; i++) {
    const nums = resultados[i].numeros;
    const sorted = [...nums].sort((a, b) => a - b);
    somaSoma += nums.reduce((s, n) => s + n, 0);
    somaPares += nums.filter(n => n % 2 === 0).length;
    somaImpares += nums.filter(n => n % 2 === 1).length;
    somaPrimos += nums.filter(n => primosSet.has(n)).length;
    somaFib += nums.filter(n => fibSet.has(n)).length;
    somaBaixos += nums.filter(n => n <= meio).length;
    somaAltos += nums.filter(n => n > meio).length;
    somaAmp += Math.max(...nums) - Math.min(...nums);
    somaMult3 += nums.filter(n => n % 3 === 0).length;
    somaMult5 += nums.filter(n => n % 5 === 0).length;
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

export async function analiseCompleta(janela?: number, lotteryId?: string): Promise<DashboardData> {
  const cfg = lotteryId ? getLotteryConfig(lotteryId) : getLotteryConfig('lotofacil');
  const resultados = await carregarResultados(cfg.id);
  const total = resultados.length;
  const occ = buildOcorrencias(resultados, cfg);
  const dados = calcularLambdas(occ, total, cfg);
  const ultimo = resultados[total - 1];

  const janelaValida = Math.max(2, Math.min(janela ?? 30, total));
  const allNums = Array.from({ length: cfg.total_numeros }, (_, i) => i + cfg.numero_minimo);

  const freqTotal: Record<number, number> = {};
  for (const n of allNums) freqTotal[n] = 0;
  for (const r of resultados) {
    for (const n of r.numeros) freqTotal[n]++;
  }

  const freq30: Record<number, number> = {};
  for (const n of allNums) freq30[n] = 0;
  for (const r of resultados.slice(-janelaValida)) {
    for (const n of r.numeros) freq30[n]++;
  }

  const gaps: Record<number, number> = {};
  for (const n of allNums) {
    let last = -1;
    for (let idx = 0; idx < resultados.length; idx++) {
      if (resultados[idx].numeros.includes(n)) last = idx;
    }
    gaps[n] = total - 1 - last;
  }

  const sortedFreq = Object.entries(freq30).sort((a, b) => b[1] - a[1]);
  const qty = cfg.qmf_scale;
  const quentes: [number, number][] = sortedFreq.slice(0, qty).map(([n, f]) => [Number(n), f]);
  const frios: [number, number][] = Object.entries(freq30)
    .sort((a, b) => {
      if (a[1] !== b[1]) return a[1] - b[1];
      return freqTotal[Number(a[0])] - freqTotal[Number(b[0])];
    })
    .slice(0, qty)
    .map(([n, f]) => [Number(n), f]);
  const quentesSet = new Set(quentes.map(([n]) => n));
  const friosSet = new Set(frios.map(([n]) => n));
  const mornos: [number, number][] = sortedFreq
    .filter(([n]) => !quentesSet.has(Number(n)) && !friosSet.has(Number(n)))
    .map(([n, f]) => [Number(n), f]);

  const positions = Array.from({ length: cfg.numeros_por_jogo }, (_, i) => `N${i + 1}`);
  const previsao: Record<string, PrevisaoItem[]> = {};
  for (const pos of positions) {
    const nums = dados[pos];
    const top3 = Object.entries(nums)
      .filter(([_, v]) => v.lambda_blend > 0)
      .sort((a, b) => b[1].lambda_blend - a[1].lambda_blend)
      .slice(0, 3)
      .map(([n, v]) => ({ numero: Number(n), prob: Math.round(v.lambda_blend * 10000) / 10000 }));
    previsao[pos] = top3;
  }

  const palpite: number[] = positions.map(p => previsao[p]?.[0]?.numero ?? 0).filter(n => n > 0);

  function gerarPrevisaoCombinada(
    cadeiaRep: number[],
    repUltimo: number[]
  ): number[] {
    const freq5: Record<number, number> = {};
    const freq15: Record<number, number> = {};
    const freq30rec: Record<number, number> = {};
    for (const n of allNums) {
      freq5[n] = 0; freq15[n] = 0; freq30rec[n] = 0;
    }
    for (const r of resultados.slice(-5)) for (const n of r.numeros) freq5[n]++;
    for (const r of resultados.slice(-15)) for (const n of r.numeros) freq15[n]++;
    for (const r of resultados.slice(-30)) for (const n of r.numeros) freq30rec[n]++;

    const cadeiaSet = new Set(cadeiaRep);
    const repSet = new Set(repUltimo);

    const aggPoisson: Record<number, number> = {};
    for (const n of allNums) {
      aggPoisson[n] = Object.values(dados).reduce((s, pos) => s + (pos[n]?.lambda_blend || 0), 0);
    }

    const invertidaScores: { num: number; score: number }[] = [];
    for (const n of allNums) {
      const f5 = (freq5[n] / 5) * 100;
      const fm = (freq15[n] / 15) * 100;
      const f30pct = (freq30rec[n] / 30) * 100;
      const consec = (() => {
        let count = 0;
        for (const r of resultados.slice(-15)) {
          if (r.numeros.includes(n)) count++;
          else break;
        }
        return count;
      })();
      let score = 0;

      if (consec >= 10) score -= 5;
      else if (consec >= 5) score += 6;
      else if (consec >= 4) score += 5;
      else if (consec >= 3 && f5 >= 80) score += 4;
      else if (consec >= 3) score += 3;
      else if (f5 >= 100) score += 4;
      else if (f5 >= 80) score += 3;

      const j5q = f5 >= 70;
      const j15q = fm >= 70;
      const j30q = f30pct >= 70;
      const j5f = f5 < 50;
      const j30f = f30pct < 50;

      if (j5q && j15q && j30q) score += 2;
      else if (j5q && !j30q) score -= 2;
      else if (!j5q && j30q) score += 3;
      else if (j5f && j30f && (f30pct < 50)) score -= 1;

      const diff = freq30rec[n] - (Object.values(freqTotal).reduce((a, b) => a + b, 0) / cfg.total_numeros / total * 30);
      if (diff > 1.5) score += 1.5;
      else if (diff < -1.5) score -= 1;

      if (cadeiaSet.has(n)) score -= 8;
      else if (repSet.has(n)) score -= 3;

      invertidaScores.push({ num: n, score });
    }

    invertidaScores.sort((a, b) => b.score - a.score);
    const excluir = new Set(invertidaScores.slice(0, 2).map(x => x.num));
    const poolN = allNums.filter(n => !excluir.has(n));

    const ultimosSomas = resultados.slice(-10).map(r => r.numeros.reduce((a, b) => a + b, 0));
    const mediaSomaRecente = ultimosSomas.reduce((a, b) => a + b, 0) / ultimosSomas.length;
    const somaHist = resultados.reduce((s, r) => s + r.numeros.reduce((a, b) => a + b, 0), 0) / resultados.length;
    const sumTarget = Math.round((mediaSomaRecente + somaHist) / 2);
    const sumBiasDirection = sumTarget - somaHist;
    const sumBias = (n: number) => (n - (cfg.numero_minimo + cfg.numero_maximo) / 2) * (sumBiasDirection / 30);

    const usado = new Set<number>();
    const resultado: number[] = [];
    for (const pos of positions) {
      const candidatos = (previsao[pos] || [])
        .filter(p => poolN.includes(p.numero) && !usado.has(p.numero))
        .sort((a, b) => (b.prob - a.prob) + sumBias(b.numero) - sumBias(a.numero));
      if (candidatos.length > 0) {
        resultado.push(candidatos[0].numero);
        usado.add(candidatos[0].numero);
      }
    }

    if (resultado.length < cfg.numeros_por_jogo) {
      const restantes = poolN.filter(n => !usado.has(n)).sort((a, b) => {
        return (aggPoisson[b] + sumBias(b)) - (aggPoisson[a] + sumBias(a));
      });
      for (const n of restantes) {
        if (resultado.length >= cfg.numeros_por_jogo) break;
        resultado.push(n);
        usado.add(n);
      }
    }

    return resultado.sort((a, b) => a - b);
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

  const atrasadosPos: Record<string, AtrasadoItem[]> = {};
  for (const pos of positions) {
    const atr: AtrasadoItem[] = [];
    for (const n of allNums) {
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
  for (const n of allNums) {
    freqHistorica[n] = freqTotal[n] / total * janelaValida;
  }
  const ciclos: Record<string, CicloInfo> = {};
  for (const n of allNums) {
    const diff = freq30[n] - freqHistorica[n];
    let estado: 'aquecendo' | 'esfriando' | 'estavel';
    if (diff > 1.5) estado = 'aquecendo';
    else if (diff < -1.5) estado = 'esfriando';
    else estado = 'estavel';
    ciclos[String(n)] = {
      freq_30: freq30[n],
      freq_esperada: Math.round(freqHistorica[n] * 10) / 10,
      diferenca: Math.round(diff * 10) / 10,
      estado,
    };
  }

  const primosSet = new Set(cfg.primos);
  const fibSet = new Set(cfg.fibonacci);
  const meio = Math.floor((cfg.numero_minimo + cfg.numero_maximo) / 2);
  const sorted = [...numsUltimo].sort((a, b) => a - b);
  const consecPares: string[] = [];
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i] - sorted[i - 1] === 1) consecPares.push(`${sorted[i - 1]}-${sorted[i]}`);
  }

  const ultimoStats: UltimoSorteio = {
    concurso: ultimo.concurso,
    numeros: numsUltimo,
    ...(ultimo.trevos ? { trevos: ultimo.trevos } : {}),
    soma: numsUltimo.reduce((a, b) => a + b, 0),
    pares: numsUltimo.filter(n => n % 2 === 0).length,
    pares_numeros: numsUltimo.filter(n => n % 2 === 0),
    impares: numsUltimo.filter(n => n % 2 === 1).length,
    impares_numeros: numsUltimo.filter(n => n % 2 === 1),
    primos: numsUltimo.filter(n => primosSet.has(n)).length,
    primos_numeros: numsUltimo.filter(n => primosSet.has(n)),
    fibonacci: numsUltimo.filter(n => fibSet.has(n)).length,
    fibonacci_numeros: numsUltimo.filter(n => fibSet.has(n)),
    repetidos: repetidosNumeros.length,
    repetidos_numeros: repetidosNumeros,
    consecutivas: consecPares.length,
    consecutivas_pares: consecPares,
    amplitude: Math.max(...numsUltimo) - Math.min(...numsUltimo),
    baixos: numsUltimo.filter(n => n <= meio).length,
    baixos_numeros: numsUltimo.filter(n => n <= meio),
    altos: numsUltimo.filter(n => n > meio).length,
    altos_numeros: numsUltimo.filter(n => n > meio),
    multiplos_3: numsUltimo.filter(n => n % 3 === 0).length,
    multiplos_3_numeros: numsUltimo.filter(n => n % 3 === 0),
    multiplos_5: numsUltimo.filter(n => n % 5 === 0).length,
    multiplos_5_numeros: numsUltimo.filter(n => n % 5 === 0),
  };

  const transicao: TransicaoQMF = analisarTransicaoQuentesFrios(resultados, cfg, janelaValida);
  const mediasHistoricas = calcularMediasHistoricas(resultados, cfg);

  let temTrevos = false;
  let frequenciaTrevosTotal: Record<string, number> = {};
  let frequenciaTrevosRecente: Record<string, number> = {};
  let gapsTrevos: Record<string, number> = {};
  let trevosQuentes: [number, number][] = [];
  let trevosFrios: [number, number][] = [];
  let trevosMornos: [number, number][] = [];
  let ciclosTrevos: Record<string, CicloInfo> = {};

  if (cfg.trevos_cols && cfg.trevos_total) {
    temTrevos = true;
    const allTrevos = Array.from({ length: cfg.trevos_total }, (_, i) => i + (cfg.trevos_min ?? 1));

    for (const n of allTrevos) {
      frequenciaTrevosTotal[String(n)] = 0;
      frequenciaTrevosRecente[String(n)] = 0;
    }
    for (const r of resultados) {
      if (r.trevos) {
        for (const t of r.trevos) frequenciaTrevosTotal[String(t)]++;
      }
    }
    for (const r of resultados.slice(-janelaValida)) {
      if (r.trevos) {
        for (const t of r.trevos) frequenciaTrevosRecente[String(t)]++;
      }
    }

    for (const n of allTrevos) {
      let last = -1;
      for (let idx = 0; idx < resultados.length; idx++) {
        if (resultados[idx].trevos?.includes(n)) last = idx;
      }
      gapsTrevos[String(n)] = total - 1 - last;
    }

    const sortedFreqTrevos = Object.entries(frequenciaTrevosRecente).sort((a, b) => b[1] - a[1]);
    const trevoQty = Math.min(2, Math.floor(allTrevos.length / 3) + 1);
    trevosQuentes = sortedFreqTrevos.slice(0, trevoQty).map(([n, f]) => [Number(n), f]);
    trevosFrios = Object.entries(frequenciaTrevosRecente)
      .sort((a, b) => {
        if (a[1] !== b[1]) return a[1] - b[1];
        return (frequenciaTrevosTotal[Number(a[0])] || 0) - (frequenciaTrevosTotal[Number(b[0])] || 0);
      })
      .slice(0, trevoQty)
      .map(([n, f]) => [Number(n), f]);
    const trevosQSet = new Set(trevosQuentes.map(([n]) => n));
    const trevosFSet = new Set(trevosFrios.map(([n]) => n));
    trevosMornos = sortedFreqTrevos
      .filter(([n]) => !trevosQSet.has(Number(n)) && !trevosFSet.has(Number(n)))
      .map(([n, f]) => [Number(n), f]);

    for (const n of allTrevos) {
      const fTotal = (frequenciaTrevosTotal[String(n)] || 0) / total * janelaValida;
      const fRecente = frequenciaTrevosRecente[String(n)] || 0;
      const diff = fRecente - fTotal;
      let estado: 'aquecendo' | 'esfriando' | 'estavel';
      if (diff > 0.8) estado = 'aquecendo';
      else if (diff < -0.8) estado = 'esfriando';
      else estado = 'estavel';
      ciclosTrevos[String(n)] = {
        freq_30: fRecente,
        freq_esperada: Math.round(fTotal * 10) / 10,
        diferenca: Math.round(diff * 10) / 10,
        estado,
      };
    }
  }

  return {
    loteria: cfg.id,
    nome_jogo: cfg.nome_jogo,
    total_numeros: cfg.total_numeros,
    numeros_por_jogo: cfg.numeros_por_jogo,
    ultimo_concurso: ultimo.concurso,
    total_sorteios: total,
    ultimo_sorteio: ultimoStats,
    frequencia_total: Object.fromEntries(allNums.map(n => [String(n), freqTotal[n]])),
    frequencia_30: Object.fromEntries(allNums.map(n => [String(n), freq30[n]])),
    gaps: Object.fromEntries(allNums.map(n => [String(n), gaps[n]])),
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
    tem_trevos: temTrevos,
    frequencia_trevos_total: frequenciaTrevosTotal,
    frequencia_trevos_recente: frequenciaTrevosRecente,
    gaps_trevos: gapsTrevos,
    trevos_quentes: trevosQuentes,
    trevos_frios: trevosFrios,
    trevos_mornos: trevosMornos,
    ciclos_trevos: ciclosTrevos,
  };
}
