import { NextResponse } from 'next/server';
import { carregarResultados } from '@/lib/database';
import { getLotteryConfig } from '@/lib/lottery-config';

export const dynamic = 'force-dynamic';

const DIGITOS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const NUM_COLUNAS = 7;
const ALPHA = 0.6;

function calcularLambdaBlend(resultados: number[][], janelaRecente: number = 0) {
  const total = resultados.length;
  const janela = janelaRecente === 0 ? total : Math.min(janelaRecente, total);
  const cutoff = Math.max(0, total - janela);

  const lambdaBlend: Record<number, Record<number, number>> = {};

  for (let col = 0; col < NUM_COLUNAS; col++) {
    lambdaBlend[col] = {};
    const freqTotal: Record<number, number> = {};
    const freqRecente: Record<number, number> = {};

    for (const d of DIGITOS) {
      freqTotal[d] = 0;
      freqRecente[d] = 0;
    }

    for (let idx = 0; idx < resultados.length; idx++) {
      const nums = resultados[idx];
      if (col < nums.length) {
        const d = nums[col];
        if (d >= 0 && d <= 9) {
          freqTotal[d]++;
          if (idx >= cutoff) {
            freqRecente[d]++;
          }
        }
      }
    }

    for (const d of DIGITOS) {
      const lambdaHist = total > 0 ? freqTotal[d] / total : 0;
      const lambdaRecent = janela > 0 ? freqRecente[d] / janela : 0;
      lambdaBlend[col][d] = ALPHA * lambdaHist + (1 - ALPHA) * lambdaRecent;
    }
  }

  return lambdaBlend;
}

function gerarJogoProbabilistico(lambdaBlend: Record<number, Record<number, number>>): number[] {
  const jogo: number[] = [];

  for (let col = 0; col < NUM_COLUNAS; col++) {
    const pesos = DIGITOS.map(d => Math.max(lambdaBlend[col][d], 0.001));
    const totalPeso = pesos.reduce((a, b) => a + b, 0);
    const probs = pesos.map(p => p / totalPeso);

    let random = Math.random();
    let escolhido = 0;
    for (let i = 0; i < DIGITOS.length; i++) {
      random -= probs[i];
      if (random <= 0) {
        escolhido = DIGITOS[i];
        break;
      }
    }
    jogo.push(escolhido);
  }

  return jogo;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const {
      quantidade = 5,
      janela_recente = 0,
      restricoes = {},
    } = body;

    const cfg = getLotteryConfig('supersete');
    const resultadosRaw = await carregarResultados(cfg.id);
    const resultados = resultadosRaw.map(r => r.numeros);

    if (resultados.length === 0) {
      return NextResponse.json({
        success: false,
        error: 'Nenhum resultado disponível para Super Sete',
      }, { status: 400 });
    }

    const lambdaBlend = calcularLambdaBlend(resultados, janela_recente);

    const somaMin = restricoes.soma_min || 0;
    const somaMax = restricoes.soma_max || 63;
    const maxRepeticoes = restricoes.max_repeticoes || 3;

    const jogos: number[][] = [];
    const vistos = new Set<string>();
    let tentativas = 0;
    const maxTentativas = quantidade * 200;

    while (jogos.length < quantidade && tentativas < maxTentativas) {
      const jogo = gerarJogoProbabilistico(lambdaBlend);
      const soma = jogo.reduce((a, b) => a + b, 0);

      if (soma < somaMin || soma > somaMax) {
        tentativas++;
        continue;
      }

      const counts: Record<number, number> = {};
      for (const d of jogo) {
        counts[d] = (counts[d] || 0) + 1;
      }
      const reps = Object.values(counts).reduce((sum, c) => sum + Math.max(0, c - 1), 0);

      if (reps > maxRepeticoes) {
        tentativas++;
        continue;
      }

      const chave = jogo.join(',');
      if (!vistos.has(chave)) {
        vistos.add(chave);
        jogos.push(jogo);
      }

      tentativas++;
    }

    return NextResponse.json({
      success: true,
      jogos,
      count: jogos.length,
      total_sorteios: resultados.length,
      lambda_blend: lambdaBlend,
      restricoes_aplicadas: {
        soma_min: somaMin,
        soma_max: somaMax,
        max_repeticoes: maxRepeticoes,
      },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
