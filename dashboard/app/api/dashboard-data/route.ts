import { NextResponse } from 'next/server';
import { analiseCompleta } from '@/lib/analise-completa';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    let janela: number | undefined;
    let concurso: number | undefined;
    const loteria = searchParams.get('loteria') || undefined;

    const janelaStr = searchParams.get('janela');
    if (janelaStr) {
      const parsed = parseInt(janelaStr, 10);
      if (!isNaN(parsed) && parsed >= 2) janela = parsed;
    }

    const concursoStr = searchParams.get('concurso');
    if (concursoStr) {
      const parsed = parseInt(concursoStr, 10);
      if (!isNaN(parsed) && parsed > 0) concurso = parsed;
    }

    const data = await analiseCompleta(janela, loteria, concurso);
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
