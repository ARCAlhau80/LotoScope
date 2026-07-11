import { NextResponse } from 'next/server';
import { getReentradasReport, getRepetidosReport, getPersistenciaReport } from '@/lib/analise-reentradas';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const loteria = searchParams.get('loteria') || undefined;
    const tipo = searchParams.get('tipo') || 'reentradas';

    if (tipo === 'repetidos') {
      const data = await getRepetidosReport(loteria);
      return NextResponse.json(data);
    }
    if (tipo === 'persistencia') {
      const data = await getPersistenciaReport(loteria);
      return NextResponse.json(data);
    }

    const data = await getReentradasReport(loteria);
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
