import { NextRequest, NextResponse } from 'next/server';
import { carregarResultados } from '@/lib/database';
import { LOTERIAS } from '@/lib/lottery-config';

export const dynamic = 'force-dynamic';

const JANELA_PADRAO = 7;
const JANELA_MAX = 500;

/**
 * Análise da janela anterior ao concurso alvo.
 *
 * GET /api/janela-alvo?loteria=lotofacil&concurso=3824&janela=7
 *
 * Retorna os números sorteados nos `janela` concursos IMEDIATAMENTE ANTERIORES
 * ao concurso alvo, com a contagem de ocorrências de cada número.
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const loteria = searchParams.get('loteria') || 'lotofacil';
    const cfg = LOTERIAS[loteria];
    if (!cfg) {
      return NextResponse.json({ error: `Loteria inválida: ${loteria}` }, { status: 400 });
    }

    const janelaParam = Number(searchParams.get('janela') ?? JANELA_PADRAO);
    const janela = Number.isFinite(janelaParam)
      ? Math.max(1, Math.min(JANELA_MAX, Math.trunc(janelaParam)))
      : JANELA_PADRAO;

    const concursoParam = searchParams.get('concurso');
    let concursoAlvo: number | undefined;
    if (concursoParam !== null && concursoParam !== '') {
      concursoAlvo = Number(concursoParam);
      if (!Number.isInteger(concursoAlvo) || concursoAlvo <= 0) {
        return NextResponse.json({ error: `Concurso inválido: ${concursoParam}` }, { status: 400 });
      }
    }

    const resultados = await carregarResultados(loteria);
    if (!resultados.length) {
      return NextResponse.json({ error: 'Nenhum resultado encontrado para esta loteria.' }, { status: 404 });
    }

    let alvoIdx = resultados.length - 1;
    if (concursoAlvo !== undefined) {
      alvoIdx = resultados.findIndex(r => r.concurso === concursoAlvo);
      if (alvoIdx < 0) {
        return NextResponse.json({ error: `Concurso ${concursoAlvo} não encontrado.` }, { status: 404 });
      }
    } else {
      concursoAlvo = resultados[alvoIdx].concurso;
    }

    const inicio = Math.max(0, alvoIdx - janela);
    const janelaConcursos = resultados.slice(inicio, alvoIdx); // anteriores, sem o alvo

    const contagem = new Map<number, number>();
    for (const r of janelaConcursos) {
      for (const n of r.numeros) {
        contagem.set(n, (contagem.get(n) ?? 0) + 1);
      }
    }

    const janelaEfetiva = janelaConcursos.length;
    const numeros = [] as { numero: number; ocorrencias: number; percentual: number }[];
    for (let n = cfg.numero_minimo; n <= cfg.numero_maximo; n++) {
      const ocorrencias = contagem.get(n) ?? 0;
      numeros.push({
        numero: n,
        ocorrencias,
        percentual: janelaEfetiva > 0 ? (100 * ocorrencias) / janelaEfetiva : 0,
      });
    }
    numeros.sort((a, b) => b.ocorrencias - a.ocorrencias || a.numero - b.numero);

    const alvo = resultados[alvoIdx];

    return NextResponse.json({
      sucesso: true,
      loteria,
      concursoAlvo,
      janelaSolicitada: janela,
      janelaEfetiva,
      totalSorteios: resultados.length,
      primeiroConcursoJanela: janelaConcursos[0]?.concurso ?? null,
      ultimoConcursoJanela: janelaConcursos[janelaConcursos.length - 1]?.concurso ?? null,
      numeros,
      concursos: janelaConcursos.map(r => ({
        concurso: r.concurso,
        numeros: r.numeros,
        data: r.data ?? null,
      })),
      alvo: {
        concurso: alvo.concurso,
        numeros: alvo.numeros,
        data: alvo.data ?? null,
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Erro ao calcular a janela.';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
