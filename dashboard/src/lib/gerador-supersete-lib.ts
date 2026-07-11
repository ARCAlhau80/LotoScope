import { carregarResultados } from './database';

const DIGITOS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const NUM_COLUNAS = 7;

export interface RestricoesSS {
  quantidade?: number;
  janela_recente?: number;
  soma_min?: number;
  soma_max?: number;
  max_repeticoes?: number;
  digitos_excluidos?: Record<number, number[]>;
  digitos_obrigatorios?: Record<number, number[]>;
  max_colunas_quentes?: number;
  coluna_nao_repetir_anterior?: boolean;
  ultimo_sorteio?: number[];
}

function calcularLambdaBlend(resultados: number[][], janelaRecente: number = 0) {
  const total = resultados.length;
  const janela = janelaRecente === 0 ? total : Math.min(janelaRecente, total);
  const cutoff = Math.max(0, total - janela);

  const lambdaBlend: Record<number, Record<number, number>> = {};

  for (let col = 0; col < NUM_COLUNAS; col++) {
    lambdaBlend[col] = {};
    const freqTotal: Record<number, number> = {};
    const freqRecente: Record<number, number> = {};

    for (const d of DIGITOS) { freqTotal[d] = 0; freqRecente[d] = 0; }

    for (let idx = 0; idx < resultados.length; idx++) {
      const nums = resultados[idx];
      if (col < nums.length) {
        const d = nums[col];
        if (d >= 0 && d <= 9) {
          freqTotal[d]++;
          if (idx >= cutoff) freqRecente[d]++;
        }
      }
    }

    for (const d of DIGITOS) {
      const lambdaHist = total > 0 ? freqTotal[d] / total : 0;
      const lambdaRecent = janela > 0 ? freqRecente[d] / janela : 0;
      lambdaBlend[col][d] = 0.6 * lambdaHist + 0.4 * lambdaRecent;
    }
  }

  return lambdaBlend;
}

function getQuentesPorColuna(lambdaBlend: Record<number, Record<number, number>>): Record<number, number[]> {
  const quentes: Record<number, number[]> = {};
  for (let col = 0; col < NUM_COLUNAS; col++) {
    const ranked = DIGITOS.sort((a, b) => lambdaBlend[col][b] - lambdaBlend[col][a]);
    quentes[col] = ranked.slice(0, 3);
  }
  return quentes;
}

function gerarJogo(
  lambdaBlend: Record<number, Record<number, number>>,
  restricoes: RestricoesSS,
  ultimoSorteio: number[] | null,
): number[] | null {
  const quentes = getQuentesPorColuna(lambdaBlend);

  for (let tentativa = 0; tentativa < 500; tentativa++) {
    const jogo: number[] = [];
    let valido = true;
    let colunasComQuentes = 0;

    for (let col = 0; col < NUM_COLUNAS; col++) {
      let disponiveis = [...DIGITOS];

      if (restricoes.digitos_excluidos?.[col]) {
        disponiveis = disponiveis.filter(d => !restricoes.digitos_excluidos![col].includes(d));
      }

      if (restricoes.digitos_obrigatorios?.[col]) {
        const obrig = restricoes.digitos_obrigatorios[col];
        disponiveis = disponiveis.filter(d => obrig.includes(d));
      }

      if (restricoes.coluna_nao_repetir_anterior && ultimoSorteio && col < ultimoSorteio.length) {
        disponiveis = disponiveis.filter(d => d !== ultimoSorteio[col]);
      }

      if (disponiveis.length === 0) { valido = false; break; }

      const pesos = disponiveis.map(d => Math.max(lambdaBlend[col][d], 0.001));
      const totalPeso = pesos.reduce((a, b) => a + b, 0);
      const probs = pesos.map(p => p / totalPeso);

      let rand = Math.random();
      let escolhido = disponiveis[0];
      for (let i = 0; i < disponiveis.length; i++) {
        rand -= probs[i];
        if (rand <= 0) { escolhido = disponiveis[i]; break; }
      }

      jogo.push(escolhido);

      if (quentes[col].includes(escolhido)) {
        colunasComQuentes++;
      }
    }

    if (!valido) continue;

    if (restricoes.max_colunas_quentes !== undefined && colunasComQuentes > restricoes.max_colunas_quentes) {
      continue;
    }

    const soma = jogo.reduce((a, b) => a + b, 0);
    if (restricoes.soma_min !== undefined && soma < restricoes.soma_min) continue;
    if (restricoes.soma_max !== undefined && soma > restricoes.soma_max) continue;

    const counts: Record<number, number> = {};
    for (const d of jogo) counts[d] = (counts[d] || 0) + 1;
    const reps = Object.values(counts).reduce((sum, c) => sum + Math.max(0, c - 1), 0);
    const maxRep = restricoes.max_repeticoes ?? 3;
    if (reps > maxRep) continue;

    return jogo;
  }

  return null;
}

export async function gerarCombinacoesSuperSete(
  quantidade: number,
  restricoes: RestricoesSS = {},
): Promise<{ combinacoes: number[][]; total_sorteios: number }> {
  const resultadosRaw = await carregarResultados('supersete');
  const resultados = resultadosRaw.map(r => r.numeros);

  if (resultados.length === 0) {
    return { combinacoes: [], total_sorteios: 0 };
  }

  const lambdaBlend = calcularLambdaBlend(resultados, restricoes.janela_recente || 0);
  const ultimoSorteio = restricoes.ultimo_sorteio ?? resultados[resultados.length - 1];

  const jogos: number[][] = [];
  const vistos = new Set<string>();
  let tentativas = 0;
  const maxTentativas = quantidade * 500;

  while (jogos.length < quantidade && tentativas < maxTentativas) {
    const jogo = gerarJogo(lambdaBlend, restricoes, ultimoSorteio);
    if (jogo) {
      const chave = jogo.join(',');
      if (!vistos.has(chave)) {
        vistos.add(chave);
        jogos.push(jogo);
      }
    }
    tentativas++;
  }

  return { combinacoes: jogos, total_sorteios: resultados.length };
}
