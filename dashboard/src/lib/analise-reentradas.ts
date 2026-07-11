import { carregarResultadosPorConfig, type Resultado } from './database';
import { getLotteryConfig } from './lottery-config';

export interface ReentradaRecord {
  concurso: number;
  nao_sorteados: number[];
  qtd_nao_sorteados: number;
  qtd_reentraram: number;
  pct: number;
}

export interface ReentradaDistrib {
  [qtd: number]: number;
}

export interface ReentradaReport {
  total_concursos: number;
  total_numeros: number;
  numeros_por_jogo: number;
  nao_sorteados_por_concurso: number;
  records: ReentradaRecord[];
  distribuicao: ReentradaDistrib;
  distribuicao_pct: Record<string, string>;
  media: number;
  mediana: number;
  moda: number;
  min: number;
  max: number;
  desvio: number;
}

function analisarReentradas(resultados: Resultado[], totalNumeros: number): ReentradaReport {
  const records: ReentradaRecord[] = [];
  const dist: ReentradaDistrib = {};
  const todosNumeros = Array.from({ length: totalNumeros }, (_, i) => i + 1);

  for (let i = 1; i < resultados.length; i++) {
    const anterior = resultados[i - 1];
    const atual = resultados[i];

    const setAnterior = new Set(anterior.numeros);
    const nao_sorteados = todosNumeros.filter(n => !setAnterior.has(n));

    const setAtual = new Set(atual.numeros);
    const qtd_reentraram = nao_sorteados.filter(n => setAtual.has(n)).length;

    records.push({
      concurso: atual.concurso,
      nao_sorteados,
      qtd_nao_sorteados: nao_sorteados.length,
      qtd_reentraram,
      pct: Math.round((qtd_reentraram / nao_sorteados.length) * 10000) / 100,
    });

    dist[qtd_reentraram] = (dist[qtd_reentraram] || 0) + 1;
  }

  const valores = records.map(r => r.qtd_reentraram).sort((a, b) => a - b);
  const n = valores.length;
  const media = valores.reduce((s, v) => s + v, 0) / n;
  const mediana = n % 2 === 0
    ? (valores[n / 2 - 1] + valores[n / 2]) / 2
    : valores[Math.floor(n / 2)];
  const moda = Object.entries(dist).sort((a, b) => b[1] - a[1])[0];
  const desvio = Math.sqrt(valores.reduce((s, v) => s + (v - media) ** 2, 0) / n);

  const sortedKeys = Object.keys(dist).map(Number).sort((a, b) => a - b);
  const distribuicao_pct: Record<string, string> = {};
  for (const k of sortedKeys) {
    distribuicao_pct[String(k)] = `${((dist[k] / n) * 100).toFixed(1)}%`;
  }

  return {
    total_concursos: n,
    total_numeros: totalNumeros,
    numeros_por_jogo: resultados[0]?.numeros.length || 15,
    nao_sorteados_por_concurso: totalNumeros - (resultados[0]?.numeros.length || 15),
    records,
    distribuicao: dist,
    distribuicao_pct,
    media: Math.round(media * 100) / 100,
    mediana,
    moda: Number(moda[0]),
    min: valores[0],
    max: valores[n - 1],
    desvio: Math.round(desvio * 100) / 100,
  };
}

export interface RepetidosRecord {
  concurso: number;
  anteriores: number[];
  qtd_repetidos: number;
  pct: number;
}

export interface RepetidosReport {
  total_concursos: number;
  total_numeros: number;
  numeros_por_jogo: number;
  records: RepetidosRecord[];
  distribuicao: ReentradaDistrib;
  distribuicao_pct: Record<string, string>;
  media: number;
  mediana: number;
  moda: number;
  min: number;
  max: number;
  desvio: number;
}

function analisarRepetidos(resultados: Resultado[]): RepetidosReport {
  const records: RepetidosRecord[] = [];
  const dist: ReentradaDistrib = {};

  for (let i = 1; i < resultados.length; i++) {
    const anterior = resultados[i - 1];
    const atual = resultados[i];

    const setAtual = new Set(atual.numeros);
    const qtd_repetidos = anterior.numeros.filter(n => setAtual.has(n)).length;

    records.push({
      concurso: atual.concurso,
      anteriores: anterior.numeros,
      qtd_repetidos,
      pct: Math.round((qtd_repetidos / anterior.numeros.length) * 10000) / 100,
    });

    dist[qtd_repetidos] = (dist[qtd_repetidos] || 0) + 1;
  }

  const valores = records.map(r => r.qtd_repetidos).sort((a, b) => a - b);
  const n = valores.length;
  const media = valores.reduce((s, v) => s + v, 0) / n;
  const mediana = n % 2 === 0
    ? (valores[n / 2 - 1] + valores[n / 2]) / 2
    : valores[Math.floor(n / 2)];
  const moda = Object.entries(dist).sort((a, b) => b[1] - a[1])[0];
  const desvio = Math.sqrt(valores.reduce((s, v) => s + (v - media) ** 2, 0) / n);

  const sortedKeys = Object.keys(dist).map(Number).sort((a, b) => a - b);
  const distribuicao_pct: Record<string, string> = {};
  for (const k of sortedKeys) {
    distribuicao_pct[String(k)] = `${((dist[k] / n) * 100).toFixed(1)}%`;
  }

  return {
    total_concursos: n,
    total_numeros: 0,
    numeros_por_jogo: resultados[0]?.numeros.length || 15,
    records,
    distribuicao: dist,
    distribuicao_pct,
    media: Math.round(media * 100) / 100,
    mediana,
    moda: Number(moda[0]),
    min: valores[0],
    max: valores[n - 1],
    desvio: Math.round(desvio * 100) / 100,
  };
}

export interface PersistenciaRecord {
  concurso: number;
  repetidos_anteriores: number[];
  qtd_repetidos_anteriores: number;
  qtd_persistiram: number;
  pct: number;
}

export interface PersistenciaReport {
  total_concursos: number;
  numeros_por_jogo: number;
  records: PersistenciaRecord[];
  distribuicao: ReentradaDistrib;
  distribuicao_pct: Record<string, string>;
  media: number;
  mediana: number;
  moda: number;
  min: number;
  max: number;
  desvio: number;
}

function analisarPersistencia(resultados: Resultado[]): PersistenciaReport {
  const records: PersistenciaRecord[] = [];
  const dist: ReentradaDistrib = {};

  for (let i = 2; i < resultados.length; i++) {
    const iMinus2 = resultados[i - 2];
    const iMinus1 = resultados[i - 1];
    const atual = resultados[i];

    const set_iMinus1 = new Set(iMinus1.numeros);
    const set_atual = new Set(atual.numeros);

    const repetidos_anteriores = iMinus2.numeros.filter(n => set_iMinus1.has(n));
    const qtd_persistiram = repetidos_anteriores.filter(n => set_atual.has(n)).length;

    records.push({
      concurso: atual.concurso,
      repetidos_anteriores,
      qtd_repetidos_anteriores: repetidos_anteriores.length,
      qtd_persistiram,
      pct: repetidos_anteriores.length > 0
        ? Math.round((qtd_persistiram / repetidos_anteriores.length) * 10000) / 100
        : 0,
    });

    dist[qtd_persistiram] = (dist[qtd_persistiram] || 0) + 1;
  }

  const valores = records.map(r => r.qtd_persistiram).sort((a, b) => a - b);
  const n = valores.length;
  const media = valores.reduce((s, v) => s + v, 0) / n;
  const mediana = n % 2 === 0
    ? (valores[n / 2 - 1] + valores[n / 2]) / 2
    : valores[Math.floor(n / 2)];
  const moda = Object.entries(dist).sort((a, b) => b[1] - a[1])[0];
  const desvio = Math.sqrt(valores.reduce((s, v) => s + (v - media) ** 2, 0) / n);

  const sortedKeys = Object.keys(dist).map(Number).sort((a, b) => a - b);
  const distribuicao_pct: Record<string, string> = {};
  for (const k of sortedKeys) {
    distribuicao_pct[String(k)] = `${((dist[k] / n) * 100).toFixed(1)}%`;
  }

  return {
    total_concursos: n,
    numeros_por_jogo: resultados[0]?.numeros.length || 15,
    records,
    distribuicao: dist,
    distribuicao_pct,
    media: Math.round(media * 100) / 100,
    mediana,
    moda: Number(moda[0]),
    min: valores[0],
    max: valores[n - 1],
    desvio: Math.round(desvio * 100) / 100,
  };
}

export async function getReentradasReport(loteria?: string): Promise<ReentradaReport> {
  const cfg = getLotteryConfig(loteria || 'lotofacil');
  const resultados = await carregarResultadosPorConfig(cfg);
  return analisarReentradas(resultados, cfg.total_numeros);
}

export async function getRepetidosReport(loteria?: string): Promise<RepetidosReport> {
  const cfg = getLotteryConfig(loteria || 'lotofacil');
  const resultados = await carregarResultadosPorConfig(cfg);
  return analisarRepetidos(resultados);
}

export async function getPersistenciaReport(loteria?: string): Promise<PersistenciaReport> {
  const cfg = getLotteryConfig(loteria || 'lotofacil');
  const resultados = await carregarResultadosPorConfig(cfg);
  return analisarPersistencia(resultados);
}
