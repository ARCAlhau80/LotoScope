import { NextRequest, NextResponse } from 'next/server';
import {
  exportarFechamentoCSV,
  verificarCobertura,
  relatorioCusto,
} from '@/lib/fechamento-combinatorio';

function parseNumero(valor: string | null, padrao: number): number {
  if (valor === null || valor === undefined || valor === "") return padrao;
  const n = parseInt(valor, 10);
  return Number.isNaN(n) ? padrao : n;
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as any;
    const apostas: number[][] = body.apostas || [];
    const universo: number[] = body.universo || Array.from({ length: 25 }, (_, i) => i + 1);
    const k: number = parseNumero(body.k, 15);
    const t: number = parseNumero(body.t, 11);
    const cobertura = body.cobertura || verificarCobertura(apostas, universo, k, t);
    const custo = relatorioCusto(apostas, k);

    const resultado = exportarFechamentoCSV(apostas, universo, k, t, cobertura, custo, body.parametrosAdicionais);

    return new NextResponse(resultado.conteudo, {
      headers: {
        'Content-Type': resultado.mimeType,
        'Content-Disposition': `attachment; filename="${resultado.nomeArquivo}"`,
      },
    });
  } catch (error: any) {
    return NextResponse.json({ sucesso: false, error: error?.message || "Erro desconhecido" }, { status: 400 });
  }
}
