import { NextRequest, NextResponse } from 'next/server';
import { analisarSobreposicaoDezenas } from '@/lib/fechamento-combinatorio';

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as any;
    const apostas: number[][] = body.apostas || [];
    const universo: number[] = body.universo || Array.from({ length: 25 }, (_, i) => i + 1);

    const resultado = analisarSobreposicaoDezenas(apostas, universo);
    return NextResponse.json({ sucesso: true, ...resultado });
  } catch (error: any) {
    return NextResponse.json({ sucesso: false, error: error?.message || "Erro desconhecido" }, { status: 400 });
  }
}
