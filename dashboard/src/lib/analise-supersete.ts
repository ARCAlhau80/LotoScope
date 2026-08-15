import { carregarResultados, type Resultado } from './database';
import { getLotteryConfig, type LotteryConfig } from './lottery-config';
import type {
  DashboardData, UltimoSorteio, PrevisaoItem, AtrasadoItem,
  TransicaoQMF, TransicaoRegistro, MediasHistoricas, CicloInfo,
  ColunaAnaliseSS, CorrelacaoColunasSS, PadraoParidadeSS,
  DistribuicaoSomaSS, RepeticaoColunasSS, ApostaMultiplaSS,
  AnaliseSuperSete, PrevisaoExclusaoSS, QuarentenaColuna, QuarentenaInfo,
  ComparativoSuperSete, TransicaoDigitoSS,
  ComparativoPosicional, DirecaoComparativo,
} from '@/types';

const ALPHA = 0.6;
const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const NUM_COLS = 7;
const QMF_QTY = 3;

function colNames(): string[] {
  return Array.from({ length: NUM_COLS }, (_, i) => `N${i + 1}`);
}

function buildColunaOcorrencias(resultados: Resultado[]): Record<string, Record<number, number[]>> {
  const cols = colNames();
  const occ: Record<string, Record<number, number[]>> = {};
  for (const c of cols) {
    occ[c] = {};
    for (const d of DIGITS) occ[c][d] = [];
  }
  for (let idx = 0; idx < resultados.length; idx++) {
    const r = resultados[idx];
    for (let ci = 0; ci < cols.length; ci++) {
      const digit = r.numeros[ci];
      if (digit !== undefined && DIGITS.includes(digit)) {
        occ[cols[ci]][digit].push(idx);
      }
    }
  }
  return occ;
}

function calcularLambdasPorColuna(
  occ: Record<string, Record<number, number[]>>,
  totalDraws: number,
  janela: number
): Record<string, Record<number, { lambda_hist: number; lambda_recent: number; lambda_blend: number; count_hist: number; count_recent: number; gap: number }>> {
  const cols = colNames();
  const dados: Record<string, Record<number, { lambda_hist: number; lambda_recent: number; lambda_blend: number; count_hist: number; count_recent: number; gap: number }>> = {};
  for (const col of cols) {
    dados[col] = {};
    for (const d of DIGITS) {
      const o = occ[col][d];
      const ch = o.length;
      const lh = totalDraws > 0 ? ch / totalDraws : 0;
      const cutoff = totalDraws - janela;
      const oRec = o.filter(i => i >= cutoff);
      const cr = oRec.length;
      const lr = (totalDraws >= janela && janela > 0) ? cr / janela : 0;
      const lb = ALPHA * lh + (1 - ALPHA) * lr;
      const ui = o.length > 0 ? Math.max(...o) : null;
      const gap = ui !== null ? totalDraws - 1 - ui : totalDraws;
      dados[col][d] = {
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

function calcularFrequenciaPorColuna(
  resultados: Resultado[],
  janela: number
): { freqTotal: Record<string, Record<number, number>>; freqRecente: Record<string, Record<number, number>> } {
  const cols = colNames();
  const freqTotal: Record<string, Record<number, number>> = {};
  const freqRecente: Record<string, Record<number, number>> = {};
  for (const c of cols) {
    freqTotal[c] = {};
    freqRecente[c] = {};
    for (const d of DIGITS) {
      freqTotal[c][d] = 0;
      freqRecente[c][d] = 0;
    }
  }
  for (let idx = 0; idx < resultados.length; idx++) {
    const r = resultados[idx];
    const isRecent = idx >= resultados.length - janela;
    for (let ci = 0; ci < cols.length; ci++) {
      const digit = r.numeros[ci];
      if (digit !== undefined && DIGITS.includes(digit)) {
        freqTotal[cols[ci]][digit]++;
        if (isRecent) freqRecente[cols[ci]][digit]++;
      }
    }
  }
  return { freqTotal, freqRecente };
}

function classificarQMFPorColuna(
  freqRecente: Record<number, number>,
  freqTotal: Record<number, number>
): { quentes: number[]; mornos: number[]; frios: number[] } {
  const sorted = [...DIGITS].sort((a, b) => (freqRecente[b] || 0) - (freqRecente[a] || 0));
  const quentes = sorted.slice(0, QMF_QTY);
  const sortedFrios = [...DIGITS].sort((a, b) => {
    const fa = freqRecente[a] || 0;
    const fb = freqRecente[b] || 0;
    if (fa !== fb) return fa - fb;
    return (freqTotal[a] || 0) - (freqTotal[b] || 0);
  });
  const frios = sortedFrios.slice(0, QMF_QTY);
  const qSet = new Set(quentes);
  const fSet = new Set(frios);
  const mornos = DIGITS.filter(d => !qSet.has(d) && !fSet.has(d));
  return { quentes, mornos, frios };
}

function calcularCiclosPorColuna(
  freqTotal: Record<string, Record<number, number>>,
  freqRecente: Record<string, Record<number, number>>,
  totalDraws: number,
  janela: number
): Record<string, Record<number, { freq_recente: number; freq_esperada: number; diferenca: number; estado: 'aquecendo' | 'esfriando' | 'estavel' }>> {
  const cols = colNames();
  const ciclos: Record<string, Record<number, { freq_recente: number; freq_esperada: number; diferenca: number; estado: 'aquecendo' | 'esfriando' | 'estavel' }>> = {};
  for (const col of cols) {
    ciclos[col] = {};
    for (const d of DIGITS) {
      const fTotal = freqTotal[col][d];
      const fRecente = freqRecente[col][d];
      const freqEsperada = totalDraws > 0 ? (fTotal / totalDraws) * janela : 0;
      const diff = fRecente - freqEsperada;
      let estado: 'aquecendo' | 'esfriando' | 'estavel';
      if (diff > 1.5) estado = 'aquecendo';
      else if (diff < -1.5) estado = 'esfriando';
      else estado = 'estavel';
      ciclos[col][d] = {
        freq_recente: fRecente,
        freq_esperada: Math.round(freqEsperada * 10) / 10,
        diferenca: Math.round(diff * 10) / 10,
        estado,
      };
    }
  }
  return ciclos;
}

function calcularAtrasadosPorColuna(
  lambdas: Record<string, Record<number, { lambda_blend: number; gap: number }>>
): Record<string, { digito: number; gap: number; p_gap: number }[]> {
  const cols = colNames();
  const atrasados: Record<string, { digito: number; gap: number; p_gap: number }[]> = {};
  for (const col of cols) {
    const atr: { digito: number; gap: number; p_gap: number }[] = [];
    for (const d of DIGITS) {
      const lb = lambdas[col][d].lambda_blend;
      const gap = lambdas[col][d].gap;
      const pGap = lb > 0 ? Math.exp(-lb * gap) : 1.0;
      if (pGap < 0.05 && gap > 0) {
        atr.push({ digito: d, gap, p_gap: Math.round(pGap * 10000) / 10000 });
      }
    }
    atrasados[col] = atr.sort((a, b) => a.p_gap - b.p_gap);
  }
  return atrasados;
}

function calcularQuarentenaPorColuna(
  resultados: Resultado[],
  fatorQuarentena: number = 0.35
): Record<string, QuarentenaColuna> {
  const cols = colNames();
  const quarentena: Record<string, QuarentenaColuna> = {};

  for (const col of cols) {
    const colIdx = parseInt(col.substring(1)) - 1;
    const sequencia = resultados.map(r => r.numeros[colIdx]);
    const digitos: QuarentenaInfo[] = [];
    const emQuarentena: number[] = [];
    const atrasadosList: number[] = [];
    const muitoAtrasados: number[] = [];

    for (const d of DIGITS) {
      const gaps: number[] = [];
      let ultimaPos: number | null = null;

      for (let i = 0; i < sequencia.length; i++) {
        if (sequencia[i] === d) {
          if (ultimaPos !== null) {
            gaps.push(i - ultimaPos);
          }
          ultimaPos = i;
        }
      }

      const gapAtual = ultimaPos !== null ? sequencia.length - 1 - ultimaPos : sequencia.length;

      if (gaps.length < 2) {
        digitos.push({
          digito: d,
          gap_atual: gapAtual,
          media: 0,
          mediana: 0,
          sigma: 0,
          p90: 0,
          status: 'normal',
        });
        continue;
      }

      const sorted = [...gaps].sort((a, b) => a - b);
      const media = gaps.reduce((a, b) => a + b, 0) / gaps.length;
      const mediana = sorted.length % 2 === 0
        ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
        : sorted[Math.floor(sorted.length / 2)];
      const variance = gaps.reduce((s, g) => s + (g - media) ** 2, 0) / gaps.length;
      const sigma = Math.sqrt(variance);
      const p90Idx = Math.ceil(sorted.length * 0.9) - 1;
      const p90 = sorted[Math.max(0, p90Idx)];

      let status: QuarentenaInfo['status'];
      if (gapAtual <= 3) {
        status = 'quarentena';
        emQuarentena.push(d);
      } else if (gapAtual > p90) {
        status = 'muito_atrasado';
        muitoAtrasados.push(d);
      } else if (gapAtual > media + fatorQuarentena * sigma) {
        status = 'atrasado';
        atrasadosList.push(d);
      } else {
        status = 'normal';
      }

      digitos.push({
        digito: d,
        gap_atual: gapAtual,
        media: Math.round(media * 10) / 10,
        mediana: Math.round(mediana * 10) / 10,
        sigma: Math.round(sigma * 10) / 10,
        p90: Math.round(p90 * 10) / 10,
        status,
      });
    }

    quarentena[col] = {
      coluna: col,
      digitos,
      em_quarentena: emQuarentena,
      atrasados: atrasadosList,
      muito_atrasados: muitoAtrasados,
    };
  }

  return quarentena;
}

function previsaoPorColuna(
  lambdas: Record<string, Record<number, { lambda_blend: number }>>
): Record<string, { digito: number; prob: number }[]> {
  const cols = colNames();
  const prev: Record<string, { digito: number; prob: number }[]> = {};
  for (const col of cols) {
    const ranked = DIGITS
      .map(d => ({ digito: d, prob: lambdas[col][d].lambda_blend }))
      .sort((a, b) => b.prob - a.prob);
    prev[col] = ranked.filter(r => r.prob > 0).slice(0, 5);
  }
  return prev;
}

function analisarCorrelacoes(resultados: Resultado[]): CorrelacaoColunasSS[] {
  const cols = colNames();
  const correlacoes: CorrelacaoColunasSS[] = [];
  for (let i = 0; i < cols.length; i++) {
    for (let j = i + 1; j < cols.length; j++) {
      const parFreq: Record<string, number> = {};
      for (const r of resultados) {
        const da = r.numeros[i];
        const db = r.numeros[j];
        if (da !== undefined && db !== undefined) {
          const key = `${da}-${db}`;
          parFreq[key] = (parFreq[key] || 0) + 1;
        }
      }
      const pares = Object.entries(parFreq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([k, v]) => {
          const [a, b] = k.split('-').map(Number);
          return { dig_a: a, dig_b: b, freq: v };
        });

      const n = resultados.length;
      const meanA = resultados.reduce((s, r) => s + (r.numeros[i] || 0), 0) / n;
      const meanB = resultados.reduce((s, r) => s + (r.numeros[j] || 0), 0) / n;
      let cov = 0, varA = 0, varB = 0;
      for (const r of resultados) {
        const da = (r.numeros[i] || 0) - meanA;
        const db = (r.numeros[j] || 0) - meanB;
        cov += da * db;
        varA += da * da;
        varB += db * db;
      }
      const denom = Math.sqrt(varA * varB);
      const corr = denom > 0 ? cov / denom / n : 0;

      correlacoes.push({
        col_a: cols[i],
        col_b: cols[j],
        pares_frequentes: pares,
        correlacao: Math.round(corr * 10000) / 10000,
      });
    }
  }
  return correlacoes;
}

function analisarParidade(resultados: Resultado[]): PadraoParidadeSS {
  const cols = colNames();
  const porColuna: Record<string, { pares: number; impares: number; pct_par: number }> = {};
  const patternCount: Record<string, number> = {};

  for (const c of cols) porColuna[c] = { pares: 0, impares: 0, pct_par: 0 };

  for (const r of resultados) {
    let pattern = '';
    for (let ci = 0; ci < cols.length; ci++) {
      const d = r.numeros[ci];
      if (d !== undefined) {
        if (d % 2 === 0) {
          porColuna[cols[ci]].pares++;
          pattern += 'P';
        } else {
          porColuna[cols[ci]].impares++;
          pattern += 'I';
        }
      }
    }
    patternCount[pattern] = (patternCount[pattern] || 0) + 1;
  }

  for (const c of cols) {
    const total = porColuna[c].pares + porColuna[c].impares;
    porColuna[c].pct_par = total > 0 ? Math.round(porColuna[c].pares / total * 1000) / 10 : 0;
  }

  const sorted = Object.entries(patternCount).sort((a, b) => b[1] - a[1]);
  const distribuicao: Record<string, number> = {};
  for (const [k, v] of sorted.slice(0, 20)) distribuicao[k] = v;

  return {
    por_coluna: porColuna,
    distribuicao,
    mais_comum: sorted[0]?.[0] || '',
  };
}

function analisarSoma(resultados: Resultado[]): DistribuicaoSomaSS {
  const somas = resultados.map(r => r.numeros.reduce((s, n) => s + (n || 0), 0));
  const n = somas.length;
  const sorted = [...somas].sort((a, b) => a - b);
  const media = somas.reduce((s, v) => s + v, 0) / n;
  const mediana = n % 2 === 0 ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2 : sorted[Math.floor(n / 2)];
  const desvio = Math.sqrt(somas.reduce((s, v) => s + (v - media) ** 2, 0) / n);

  const faixas = [
    { nome: '0-15', min: 0, max: 15 },
    { nome: '16-25', min: 16, max: 25 },
    { nome: '26-35', min: 26, max: 35 },
    { nome: '36-45', min: 36, max: 45 },
    { nome: '46-63', min: 46, max: 63 },
  ];
  const faixaCounts = faixas.map(f => {
    const count = somas.filter(s => s >= f.min && s <= f.max).length;
    return { faixa: f.nome, count, pct: Math.round(count / n * 1000) / 10 };
  });

  const histograma: Record<number, number> = {};
  for (const s of somas) histograma[s] = (histograma[s] || 0) + 1;

  return {
    media: Math.round(media * 100) / 100,
    mediana,
    desvio: Math.round(desvio * 100) / 100,
    min: sorted[0],
    max: sorted[n - 1],
    faixas: faixaCounts,
    histograma,
  };
}

function analisarRepeticao(resultados: Resultado[]): RepeticaoColunasSS {
  let totalReps = 0;
  let comRepeticao = 0;
  const dist: Record<number, number> = {};
  const digRepCount: Record<number, number> = {};

  for (const r of resultados) {
    const digitCounts: Record<number, number> = {};
    for (const d of r.numeros) {
      if (d !== undefined) digitCounts[d] = (digitCounts[d] || 0) + 1;
    }
    const reps = Object.values(digitCounts).filter(c => c > 1).reduce((s, c) => s + c - 1, 0);
    totalReps += reps;
    if (reps > 0) comRepeticao++;
    dist[reps] = (dist[reps] || 0) + 1;

    for (const [d, c] of Object.entries(digitCounts)) {
      if (c > 1) digRepCount[Number(d)] = (digRepCount[Number(d)] || 0) + 1;
    }
  }

  const n = resultados.length;
  const digitosMaisRepetidos = Object.entries(digRepCount)
    .sort((a, b) => b[1] - a[1])
    .map(([d, c]) => ({ digito: Number(d), count: c }));

  return {
    media_repeticoes: Math.round(totalReps / n * 100) / 100,
    pct_com_repeticao: Math.round(comRepeticao / n * 1000) / 10,
    distribuicao: dist,
    digitos_mais_repetidos: digitosMaisRepetidos.slice(0, 10),
  };
}

function calcularExclusaoPorColuna(
  resultados: Resultado[],
  janela: number
): PrevisaoExclusaoSS {
  const cols = colNames();
  const colunas: PrevisaoExclusaoSS['colunas'] = {};

  for (const col of cols) {
    const ci = cols.indexOf(col);
    const valCol = resultados.map(r => r.numeros[ci]);

    // Media Ponderada (janela=5) - melhor heuristica geral
    const pesoRecente5 = (h: number[]) => {
      const n = h.length;
      const pesos = h.map((_, i) => 1 + (i / n) * 2);
      const score: Record<number, number> = {};
      for (const d of [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]) score[d] = 0;
      for (let i = 0; i < n; i++) score[h[i]] += pesos[i];
      return score;
    };

    // Alternancia+Freq(15) - melhor para N6
    const altFreq15 = (h: number[]) => {
      const n = h.length;
      const ultimo = n > 0 ? h[n - 1] : -1;
      const rec = h.slice(-15);
      const freq: Record<number, number> = {};
      for (const d of [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]) freq[d] = 0;
      for (const d of rec) freq[d]++;
      const candidatos = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].filter(d => d !== ultimo);
      for (const d of [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]) {
        if (!candidatos.includes(d)) freq[d] = -1;
      }
      return freq;
    };

    // Escolhe estrategia por coluna baseado na analise previa
    const estrategiaPorColuna: Record<string, string> = {
      N1: 'MediaPonderada5', N2: 'MediaPonderada5', N3: 'MediaPonderada5',
      N4: 'MediaPonderada5', N5: 'MediaPonderada5', N6: 'AlternanciaFreq15', N7: 'MediaPonderada5',
    };

    const hist = valCol.slice(0, -1);
    let score: Record<number, number>;
    if (estrategiaPorColuna[col] === 'AlternanciaFreq15') {
      score = altFreq15(hist);
    } else {
      score = pesoRecente5(hist);
    }

    // Normaliza scores para 0-1
    const vals = Object.values(score);
    const maxScore = Math.max(...vals, 0.001);
    const minScore = Math.min(...vals);
    const range = maxScore - minScore || 1;

    const scores: { digito: number; score: number; status: 'mantido' | 'excluido' }[] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
      .map(d => ({
        digito: d,
        score: (score[d] - minScore) / range,
        status: 'excluido' as const,
      }))
      .sort((a, b) => b.score - a.score);

    // Top 3 = mantidos
    const top3 = scores.slice(0, 3).map(s => s.digito);
    for (const s of scores.slice(0, 3)) s.status = 'mantido';

    colunas[col] = { estrategia: estrategiaPorColuna[col], scores, top3 };
  }

  return { colunas };
}

function gerarApostaMultipla(
  lambdas: Record<string, Record<number, { lambda_blend: number }>>,
  freqRecente: Record<string, Record<number, number>>
): ApostaMultiplaSS {
  const cols = colNames();
  const colunas: Record<string, { digitos: number[]; confianca: number[] }> = {};
  const palpiteMultipla: Record<string, number[]> = {};
  let combinacoes = 1;

  for (const col of cols) {
    const ranked = DIGITS
      .map(d => ({ digito: d, prob: lambdas[col][d].lambda_blend, freq: freqRecente[col][d] || 0 }))
      .sort((a, b) => b.prob - a.prob);

    const top3 = ranked.slice(0, 3);
    colunas[col] = {
      digitos: top3.map(r => r.digito),
      confianca: top3.map(r => Math.round(r.prob * 10000) / 100),
    };
    palpiteMultipla[col] = top3.slice(0, 2).map(r => r.digito);
    combinacoes *= 2;
  }

  return { colunas, combinacoes_possiveis: combinacoes, palpite_multipla: palpiteMultipla };
}

function montarAnaliseColunas(
  freqTotal: Record<string, Record<number, number>>,
  freqRecente: Record<string, Record<number, number>>,
  lambdas: Record<string, Record<number, { lambda_hist: number; lambda_recent: number; lambda_blend: number; count_hist: number; count_recent: number; gap: number }>>,
  ciclos: Record<string, Record<number, { freq_recente: number; freq_esperada: number; diferenca: number; estado: 'aquecendo' | 'esfriando' | 'estavel' }>>,
  atrasados: Record<string, { digito: number; gap: number; p_gap: number }[]>,
  previsao: Record<string, { digito: number; prob: number }[]>
): Record<string, ColunaAnaliseSS> {
  const cols = colNames();
  const colunas: Record<string, ColunaAnaliseSS> = {};
  for (const col of cols) {
    const qmf = classificarQMFPorColuna(freqRecente[col], freqTotal[col]);
    const lbRecord: Record<number, number> = {};
    const gapRecord: Record<number, number> = {};
    for (const d of DIGITS) {
      lbRecord[d] = lambdas[col][d].lambda_blend;
      gapRecord[d] = lambdas[col][d].gap;
    }
    colunas[col] = {
      coluna: col,
      frequencia_total: freqTotal[col],
      frequencia_recente: freqRecente[col],
      lambda_blend: lbRecord,
      quentes: qmf.quentes,
      mornos: qmf.mornos,
      frios: qmf.frios,
      gap: gapRecord,
      atrasados: atrasados[col],
      ciclo: ciclos[col],
      previsao: previsao[col],
    };
  }
  return colunas;
}

function calcularMediasHistoricasSS(resultados: Resultado[]): MediasHistoricas {
  let somaSoma = 0, somaPares = 0, somaImpares = 0, somaPrimos = 0;
  let somaFib = 0, somaRep = 0, somaAmp = 0;
  let somaBaixos = 0, somaAltos = 0, somaMult3 = 0, somaMult5 = 0;
  const t = resultados.length;
  const primosSet = new Set([2, 3, 5, 7]);
  const fibSet = new Set([0, 1, 2, 3, 5, 8]);

  for (let i = 0; i < t; i++) {
    const nums = resultados[i].numeros;
    somaSoma += nums.reduce((s, n) => s + (n || 0), 0);
    somaPares += nums.filter(n => n !== undefined && n % 2 === 0).length;
    somaImpares += nums.filter(n => n !== undefined && n % 2 === 1).length;
    somaPrimos += nums.filter(n => n !== undefined && primosSet.has(n)).length;
    somaFib += nums.filter(n => n !== undefined && fibSet.has(n)).length;
    somaBaixos += nums.filter(n => n !== undefined && n <= 4).length;
    somaAltos += nums.filter(n => n !== undefined && n > 4).length;
    const validNums = nums.filter(n => n !== undefined);
    if (validNums.length > 0) {
      somaAmp += Math.max(...validNums) - Math.min(...validNums);
    }
    somaMult3 += nums.filter(n => n !== undefined && n % 3 === 0).length;
    somaMult5 += nums.filter(n => n !== undefined && n % 5 === 0).length;
    if (i > 0) {
      const prevDigits = new Set(resultados[i - 1].numeros);
      somaRep += nums.filter(n => n !== undefined && prevDigits.has(n)).length;
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
    consecutivas: 0,
    amplitude: r(somaAmp),
    baixos: r(somaBaixos),
    altos: r(somaAltos),
    multiplos_3: r(somaMult3),
    multiplos_5: r(somaMult5),
  };
}

function analisarTransicaoQMFPorColuna(
  resultados: Resultado[],
  janela: number
): TransicaoQMF {
  const cols = colNames();
  const total = resultados.length;
  const registros: TransicaoRegistro[] = [];

  for (let idx = janela; idx < total; idx++) {
    const window = resultados.slice(idx - janela, idx);
    const freqW: Record<string, Record<number, number>> = {};
    const freqT: Record<string, Record<number, number>> = {};
    for (const c of cols) {
      freqW[c] = {};
      freqT[c] = {};
      for (const d of DIGITS) { freqW[c][d] = 0; freqT[c][d] = 0; }
    }
    for (let ri = 0; ri < idx; ri++) {
      for (let ci = 0; ci < cols.length; ci++) {
        const d = resultados[ri].numeros[ci];
        if (d !== undefined) freqT[cols[ci]][d]++;
      }
    }
    for (const r of window) {
      for (let ci = 0; ci < cols.length; ci++) {
        const d = r.numeros[ci];
        if (d !== undefined) freqW[cols[ci]][d]++;
      }
    }

    let qtdQ = 0, qtdM = 0, qtdF = 0;
    const allQ: number[] = [], allM: number[] = [], allF: number[] = [];
    for (let ci = 0; ci < cols.length; ci++) {
      const qmf = classificarQMFPorColuna(freqW[cols[ci]], freqT[cols[ci]]);
      const drawnDigit = resultados[idx].numeros[ci];
      if (drawnDigit !== undefined) {
        if (qmf.quentes.includes(drawnDigit)) { qtdQ++; allQ.push(drawnDigit); }
        else if (qmf.frios.includes(drawnDigit)) { qtdF++; allF.push(drawnDigit); }
        else { qtdM++; allM.push(drawnDigit); }
      }
    }

    registros.push({
      concurso: resultados[idx].concurso,
      quentes: qtdQ, mornos: qtdM, frios: qtdF,
      pct_q: Math.round(qtdQ / NUM_COLS * 100 * 10) / 10,
      pct_m: Math.round(qtdM / NUM_COLS * 100 * 10) / 10,
      pct_f: Math.round(qtdF / NUM_COLS * 100 * 10) / 10,
      q_set: allQ.sort((a, b) => a - b),
      m_set: allM.sort((a, b) => a - b),
      f_set: allF.sort((a, b) => a - b),
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

function calcularComparativoSuperSete(resultados: Resultado[]): ComparativoSuperSete | null {
  if (resultados.length < 2) return null;
  const NUM_COLS = 7;
  const DIGITOS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
  const ultimo = resultados[resultados.length - 1];
  const penultimo = resultados[resultados.length - 2];
  const porColuna: ComparativoSuperSete['por_coluna'] = {};

  for (let col = 0; col < NUM_COLS; col++) {
    const transMap: Record<number, { total: number; mesmo: number; maior: number; menor: number }> = {};
    for (const d of DIGITOS) transMap[d] = { total: 0, mesmo: 0, maior: 0, menor: 0 };

    for (let i = 1; i < resultados.length; i++) {
      const ant = resultados[i - 1].numeros[col];
      const atu = resultados[i].numeros[col];
      if (ant === undefined || atu === undefined) continue;
      const t = transMap[ant];
      t.total++;
      if (atu === ant) t.mesmo++;
      else if (atu > ant) t.maior++;
      else t.menor++;
    }

    const transicoes: TransicaoDigitoSS[] = DIGITOS.map(d => {
      const t = transMap[d];
      return {
        digito: d,
        total: t.total,
        mesmo: t.mesmo,
        maior: t.maior,
        menor: t.menor,
        pct_mesmo: t.total > 0 ? Math.round(t.mesmo / t.total * 1000) / 10 : 0,
        pct_maior: t.total > 0 ? Math.round(t.maior / t.total * 1000) / 10 : 0,
        pct_menor: t.total > 0 ? Math.round(t.menor / t.total * 1000) / 10 : 0,
      };
    });

    const agg = transicoes.reduce((acc, t) => ({
      mesmo: acc.mesmo + t.mesmo,
      maior: acc.maior + t.maior,
      menor: acc.menor + t.menor,
      total: acc.total + t.total,
    }), { mesmo: 0, maior: 0, menor: 0, total: 0 });

    porColuna[`N${col + 1}`] = { transicoes, ...agg };
  }

  return {
    por_coluna: porColuna,
    ultimo_sorteio: ultimo.numeros,
    penultimo_sorteio: penultimo.numeros,
  };
}

export async function analiseSuperSete(janela?: number, concurso?: number): Promise<DashboardData> {
  const cfg = getLotteryConfig('supersete');
  let resultados = await carregarResultados(cfg.id);

  const concursosDisponiveis = resultados.map(r => r.concurso);

  if (concurso !== undefined) {
    const idx = resultados.findIndex(r => r.concurso === concurso);
    if (idx === -1) throw new Error(`Concurso ${concurso} não encontrado`);
    resultados = resultados.slice(0, idx + 1);
  }

  const total = resultados.length;
  const janelaValida = Math.max(2, Math.min(janela ?? 30, total));
  const cols = colNames();

  const occ = buildColunaOcorrencias(resultados);
  const lambdas = calcularLambdasPorColuna(occ, total, janelaValida);
  const { freqTotal, freqRecente } = calcularFrequenciaPorColuna(resultados, janelaValida);
  const ciclos = calcularCiclosPorColuna(freqTotal, freqRecente, total, janelaValida);
  const atrasados = calcularAtrasadosPorColuna(lambdas);
  const prev = previsaoPorColuna(lambdas);

  const colunasAnalise = montarAnaliseColunas(freqTotal, freqRecente, lambdas, ciclos, atrasados, prev);
  const correlacoes = analisarCorrelacoes(resultados);
  const paridade = analisarParidade(resultados);
  const soma = analisarSoma(resultados);
  const repeticao = analisarRepeticao(resultados);
  const apostaMultipla = gerarApostaMultipla(lambdas, freqRecente);
  const previsaoExclusao = calcularExclusaoPorColuna(resultados, janelaValida);
  const quarentena = calcularQuarentenaPorColuna(resultados);

  const analiseSS: AnaliseSuperSete = {
    colunas: colunasAnalise,
    correlacoes,
    paridade,
    soma,
    repeticao,
    aposta_multipla: apostaMultipla,
    previsao_exclusao: previsaoExclusao,
    quarentena,
    comparativo_posicional: calcularComparativoSuperSete(resultados) ?? undefined,
  };

  const ultimo = resultados[total - 1];
  const numsUltimo = ultimo.numeros;
  const penultimo = total > 1 ? resultados[total - 2] : null;
  const numsPenultimo = penultimo ? penultimo.numeros : [];
  
  const repetidosNumeros: number[] = [];
  const repetidosPorColuna: string[] = [];
  for (let col = 0; col < NUM_COLS; col++) {
    if (col < numsUltimo.length && col < numsPenultimo.length) {
      if (numsUltimo[col] === numsPenultimo[col]) {
        repetidosNumeros.push(numsUltimo[col]);
        repetidosPorColuna.push(`N${col + 1}`);
      }
    }
  }
  
  const antepenultimo = total > 2 ? resultados[total - 3] : null;
  const numsAntepenultimo = antepenultimo ? antepenultimo.numeros : [];
  
  const repetidosCadeia: number[] = [];
  const repetidosCadeiaPorColuna: string[] = [];
  for (let col = 0; col < NUM_COLS; col++) {
    if (col < numsUltimo.length && col < numsPenultimo.length && col < numsAntepenultimo.length) {
      if (numsUltimo[col] === numsPenultimo[col] && numsPenultimo[col] === numsAntepenultimo[col]) {
        repetidosCadeia.push(numsUltimo[col]);
        repetidosCadeiaPorColuna.push(`N${col + 1}`);
      }
    }
  }

  const primosSet = new Set([2, 3, 5, 7]);
  const fibSet = new Set([0, 1, 2, 3, 5, 8]);

  const freqGlobalTotal: Record<string, number> = {};
  const freqGlobal30: Record<string, number> = {};
  const gapsGlobal: Record<string, number> = {};
  for (const d of DIGITS) {
    freqGlobalTotal[String(d)] = 0;
    freqGlobal30[String(d)] = 0;
  }
  for (const r of resultados) {
    for (const d of r.numeros) {
      if (d !== undefined) freqGlobalTotal[String(d)]++;
    }
  }
  for (const r of resultados.slice(-janelaValida)) {
    for (const d of r.numeros) {
      if (d !== undefined) freqGlobal30[String(d)]++;
    }
  }
  for (const d of DIGITS) {
    let last = -1;
    for (let idx = 0; idx < resultados.length; idx++) {
      if (resultados[idx].numeros.includes(d)) last = idx;
    }
    gapsGlobal[String(d)] = total - 1 - last;
  }

  const sortedFreq30 = Object.entries(freqGlobal30).sort((a, b) => b[1] - a[1]);
  const quentes: [number, number][] = sortedFreq30.slice(0, 3).map(([n, f]) => [Number(n), f]);
  const frios: [number, number][] = Object.entries(freqGlobal30)
    .sort((a, b) => a[1] !== b[1] ? a[1] - b[1] : (freqGlobalTotal[a[0]] || 0) - (freqGlobalTotal[b[0]] || 0))
    .slice(0, 3)
    .map(([n, f]) => [Number(n), f]);
  const qSet = new Set(quentes.map(([n]) => n));
  const fSet = new Set(frios.map(([n]) => n));
  const mornos: [number, number][] = sortedFreq30
    .filter(([n]) => !qSet.has(Number(n)) && !fSet.has(Number(n)))
    .map(([n, f]) => [Number(n), f]);

  const previsaoPosicional: Record<string, PrevisaoItem[]> = {};
  for (const col of cols) {
    previsaoPosicional[col] = prev[col].slice(0, 3).map(p => ({ numero: p.digito, prob: p.prob }));
  }

  const palpite = cols.map(col => {
    const q = quarentena[col];
    if (!q) return prev[col]?.[0]?.digito ?? 0;
    const candidatos = q.digitos
      .filter(d => d.status === 'normal' || d.status === 'atrasado')
      .sort((a, b) => {
        const distA = Math.abs(a.gap_atual - a.media);
        const distB = Math.abs(b.gap_atual - b.media);
        return distA - distB;
      });
    return candidatos.length > 0 ? candidatos[0].digito : prev[col]?.[0]?.digito ?? 0;
  });

  const previsaoCombinada = cols.map(col => {
    const q = quarentena[col];
    if (!q) return prev[col]?.[0]?.digito ?? 0;
    const candidatos = q.digitos
      .filter(d => d.status === 'muito_atrasado' || d.status === 'atrasado')
      .sort((a, b) => (b.gap_atual / Math.max(b.p90, 1)) - (a.gap_atual / Math.max(a.p90, 1)));
    return candidatos.length > 0 ? candidatos[0].digito : prev[col]?.[0]?.digito ?? 0;
  });

  const atrasadosPosicionais: Record<string, AtrasadoItem[]> = {};
  for (const col of cols) {
    atrasadosPosicionais[col] = atrasados[col].map(a => ({
      numero: a.digito,
      p_gap: a.p_gap,
      gap: a.gap,
      lambda_blend: lambdas[col][a.digito].lambda_blend,
    }));
  }

  const ciclosGlobal: Record<string, CicloInfo> = {};
  for (const d of DIGITS) {
    const fTotal = freqGlobalTotal[String(d)];
    const fRecente = freqGlobal30[String(d)];
    const freqEsperada = total > 0 ? (fTotal / total) * janelaValida : 0;
    const diff = fRecente - freqEsperada;
    let estado: 'aquecendo' | 'esfriando' | 'estavel';
    if (diff > 1.5) estado = 'aquecendo';
    else if (diff < -1.5) estado = 'esfriando';
    else estado = 'estavel';
    ciclosGlobal[String(d)] = {
      freq_30: fRecente,
      freq_esperada: Math.round(freqEsperada * 10) / 10,
      diferenca: Math.round(diff * 10) / 10,
      estado,
    };
  }

  const ultimoStats: UltimoSorteio = {
    concurso: ultimo.concurso,
    numeros: numsUltimo,
    soma: numsUltimo.reduce((a, b) => a + (b || 0), 0),
    pares: numsUltimo.filter(n => n !== undefined && n % 2 === 0).length,
    pares_numeros: numsUltimo.filter(n => n !== undefined && n % 2 === 0),
    impares: numsUltimo.filter(n => n !== undefined && n % 2 === 1).length,
    impares_numeros: numsUltimo.filter(n => n !== undefined && n % 2 === 1),
    primos: numsUltimo.filter(n => n !== undefined && primosSet.has(n)).length,
    primos_numeros: numsUltimo.filter(n => n !== undefined && primosSet.has(n)),
    fibonacci: numsUltimo.filter(n => n !== undefined && fibSet.has(n)).length,
    fibonacci_numeros: numsUltimo.filter(n => n !== undefined && fibSet.has(n)),
    repetidos: repetidosNumeros.length,
    repetidos_numeros: repetidosNumeros,
    consecutivas: 0,
    consecutivas_pares: [],
    amplitude: numsUltimo.length > 0 ? Math.max(...numsUltimo) - Math.min(...numsUltimo) : 0,
    nao_sorteados: 0,
    nao_sorteados_numeros: DIGITS.filter(d => !numsUltimo.includes(d)),
    baixos: numsUltimo.filter(n => n !== undefined && n <= 4).length,
    baixos_numeros: numsUltimo.filter(n => n !== undefined && n <= 4),
    altos: numsUltimo.filter(n => n !== undefined && n > 4).length,
    altos_numeros: numsUltimo.filter(n => n !== undefined && n > 4),
    multiplos_3: numsUltimo.filter(n => n !== undefined && n % 3 === 0).length,
    multiplos_3_numeros: numsUltimo.filter(n => n !== undefined && n % 3 === 0),
    multiplos_5: numsUltimo.filter(n => n !== undefined && n % 5 === 0).length,
    multiplos_5_numeros: numsUltimo.filter(n => n !== undefined && n % 5 === 0),
  };

  const transicao = analisarTransicaoQMFPorColuna(resultados, janelaValida);
  const mediasHistoricas = calcularMediasHistoricasSS(resultados);

  const penultimoResultado = total > 1 ? resultados[total - 2] : null;
  const comparativoSS: ComparativoPosicional | undefined = penultimoResultado ? {
    concurso_atual: ultimo.concurso,
    concurso_anterior: penultimoResultado.concurso,
    itens: ultimo.numeros.map((atual, i) => {
      const anterior = penultimoResultado!.numeros[i];
      const dir = atual > anterior ? 'maior' : atual < anterior ? 'menor' : 'igual';
      const colKey = `N${i + 1}`;
      const transicoes = analiseSS.comparativo_posicional?.por_coluna[colKey]?.transicoes;
      const t = transicoes?.find(t => t.digito === anterior);
      let expectativa: DirecaoComparativo | undefined;
      if (t && t.total > 0) {
        if (t.pct_maior >= t.pct_menor && t.pct_maior >= t.pct_mesmo) expectativa = 'maior';
        else if (t.pct_menor >= t.pct_maior && t.pct_menor >= t.pct_mesmo) expectativa = 'menor';
        else expectativa = 'igual';
      }
      return { posicao: i + 1, atual, anterior, direcao: dir, expectativa, acertou: expectativa ? dir === expectativa : undefined };
    }),
    total_maiores: ultimo.numeros.filter((n, i) => n > penultimoResultado!.numeros[i]).length,
    total_menores: ultimo.numeros.filter((n, i) => n < penultimoResultado!.numeros[i]).length,
    total_iguais: ultimo.numeros.filter((n, i) => n === penultimoResultado!.numeros[i]).length,
  } : undefined;

  return {
    loteria: cfg.id,
    nome_jogo: cfg.nome_jogo,
    total_numeros: cfg.total_numeros,
    numeros_por_jogo: cfg.numeros_por_jogo,
    numeros_por_aposta: cfg.numeros_por_aposta ?? cfg.numeros_por_jogo,
    ultimo_concurso: ultimo.concurso,
    total_sorteios: total,
    ultimo_sorteio: ultimoStats,
    frequencia_total: freqGlobalTotal,
    frequencia_30: freqGlobal30,
    gaps: gapsGlobal,
    numeros_quentes: quentes,
    numeros_frios: frios,
    numeros_mornos: mornos,
    previsao_posicional: previsaoPosicional,
    palpite,
    previsao_combinada: previsaoCombinada,
    atrasados_posicionais: atrasadosPosicionais,
    ciclos: ciclosGlobal,
    transicao_qmf: transicao,
    medias_historicas: mediasHistoricas,
    janela_usada: janelaValida,
    concurso_analisado: ultimo.concurso,
    concursos_disponiveis: concursosDisponiveis,
    timestamp: new Date().toISOString(),
    repetidos_cadeia: repetidosCadeia,
    tem_trevos: false,
    is_positional: true,
    supersete: analiseSS,
    comparativo_posicional: comparativoSS,
  };
}
