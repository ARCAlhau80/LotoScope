import { NextRequest, NextResponse } from 'next/server';
import { validarContraSorteiosReais, SorteioReal } from '@/lib/fechamento-combinatorio';

function parseNumero(valor: string | null, padrao: number): number {
  if (valor === null || valor === undefined || valor === "") return padrao;
  const n = parseInt(valor, 10);
  return Number.isNaN(n) ? padrao : n;
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as any;
    const apostas: number[][] = body.apostas || [];
    const sorteios: SorteioReal[] = body.sorteios || [];
    const k: number = parseNumero(body.k, 15);
    const t: number = parseNumero(body.t, 11);

    const resultado = validarContraSorteiosReais(apostas, sorteios, k, t);
    return NextResponse.json({ sucesso: true, ...resultado });
  } catch (error: any) {
    return NextResponse.json({ sucesso: false, error: error?.message || "Erro desconhecido" }, { status: 400 });
  }
}
