import { NextRequest, NextResponse } from 'next/server';
import { carregarResultado } from '@/lib/database';
import { LOTERIAS } from '@/lib/lottery-config';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const loteria = searchParams.get('loteria') || 'lotofacil';

    if (!LOTERIAS[loteria]) {
      return NextResponse.json({ error: `Loteria inválida: ${loteria}` }, { status: 400 });
    }

    const concursoParam = searchParams.get('concurso');
    let concurso: number | undefined;
    if (concursoParam !== null) {
      concurso = Number(concursoParam);
      if (!Number.isInteger(concurso) || concurso <= 0) {
        return NextResponse.json({ error: `Concurso inválido: ${concursoParam}` }, { status: 400 });
      }
    }

    const resultado = await carregarResultado(loteria, concurso);
    if (!resultado) {
      return NextResponse.json(
        { error: concurso ? `Concurso ${concurso} não encontrado` : 'Nenhum resultado encontrado' },
        { status: 404 },
      );
    }

    return NextResponse.json(resultado);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Erro ao carregar resultado';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
