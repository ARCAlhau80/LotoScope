import { NextResponse } from 'next/server';
import { carregarRankingCombinacoes, type RankingPerfil } from '@/lib/database';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const perfil = (searchParams.get('perfil') || 'altovalor') as RankingPerfil;
    const topStr = searchParams.get('top');
    const top = topStr ? Math.min(50, Math.max(1, parseInt(topStr, 10))) : 10;

    if (!['foco11', 'equilibrado', 'altovalor'].includes(perfil)) {
      return NextResponse.json({ error: 'Perfil inválido' }, { status: 400 });
    }

    const ranking = await carregarRankingCombinacoes(perfil, top, 'lotofacil');
    return NextResponse.json({ ranking, perfil, top });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
