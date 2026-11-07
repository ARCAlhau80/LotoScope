import { NextRequest, NextResponse } from 'next/server';
import { backtestFechamento } from '@/lib/fechamento-combinatorio';
import { getFechamentoConfig } from '@/lib/fechamento/config';
import { carregarResultados } from '@/lib/database';

export const runtime = 'nodejs';
export const maxDuration = 60;

const MAX_APOSTAS_BACKTEST = 20_000;

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as any;
    const apostasRaw = Array.isArray(body?.apostas) ? body.apostas : [];
    const apostas: number[][] = apostasRaw
      .filter(Array.isArray)
      .slice(0, MAX_APOSTAS_BACKTEST)
      .map((a: any[]) => a.map((n: any) => Number(n)).filter((n: number) => Number.isInteger(n) && n > 0))
      .filter((a: number[]) => a.length > 0);

    if (!apostas.length) {
      return NextResponse.json({ sucesso: false, error: 'Nenhuma aposta válida informada.' }, { status: 400 });
    }

    const loteria = typeof body.loteria === 'string' && body.loteria ? body.loteria : 'lotofacil';
    const fcfg = getFechamentoConfig(loteria);
    const k = Number.isInteger(body.k) && body.k > 0 ? body.k : fcfg.kPadrao;
    const premios = body.premios && typeof body.premios === 'object'
      ? body.premios as Record<number, number>
      : fcfg.premios;
    const faixasPremio = Array.isArray(body.faixasPremio)
      ? body.faixasPremio.map((n: any) => Number(n)).filter((n: number) => Number.isInteger(n) && n > 0)
      : fcfg.faixasPremio;

    const resultados = await carregarResultados(loteria);
    if (!resultados.length) {
      return NextResponse.json({ sucesso: false, error: 'Sem resultados históricos para backtest.' }, { status: 400 });
    }

    const backtest = backtestFechamento({
      apostas,
      resultados,
      k,
      premios,
      faixasPremio,
      dezenasBase: fcfg.dezenasPorAposta,
      precoBase: fcfg.precoBase,
    });
    return NextResponse.json({ sucesso: true, ...backtest });
  } catch (error: any) {
    return NextResponse.json({ sucesso: false, error: error?.message || 'Erro no backtest' }, { status: 400 });
  }
}
