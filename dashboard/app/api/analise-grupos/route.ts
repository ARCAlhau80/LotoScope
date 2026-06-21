import { NextResponse } from 'next/server';
import { analiseGrupos } from '@/lib/analise-grupos';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const data = await analiseGrupos();
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
