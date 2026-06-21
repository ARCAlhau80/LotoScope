import { NextResponse } from 'next/server';
import { analiseCompleta } from '@/lib/analise-completa';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    let janela: number | undefined;
    const loteria = searchParams.get('loteria') || undefined;

    const janelaStr = searchParams.get('janela');
    if (janelaStr) {
      const parsed = parseInt(janelaStr, 10);
      if (!isNaN(parsed) && parsed >= 2) janela = parsed;
    }

    const data = await analiseCompleta(janela, loteria);
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
