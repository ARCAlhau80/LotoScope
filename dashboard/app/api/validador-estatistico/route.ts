import { NextResponse } from 'next/server';
import { getLotteryConfig } from '@/lib/lottery-config';
import { validarEstatisticamente } from '@/lib/validador-estatistico';

export const dynamic = 'force-dynamic';

function parsePositiveInt(value: string | null): number | undefined {
  if (!value) return undefined;
  const parsed = parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : undefined;
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const loteria = searchParams.get('loteria') || 'lotofacil';
    const cfg = getLotteryConfig(loteria);
    if (cfg.is_positional) {
      return NextResponse.json(
        { error: 'O validador estatístico não se aplica a loterias posicionais.' },
        { status: 400 },
      );
    }

    const janela = parsePositiveInt(searchParams.get('janela'));
    const badgeJanela = parsePositiveInt(searchParams.get('badge_janela'));
    const concurso = parsePositiveInt(searchParams.get('concurso'));

    const data = await validarEstatisticamente({ loteria, janela, badgeJanela, concurso });
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Erro ao validar estatisticamente.';
    const status = message.includes('não encontrado') ? 400 : 500;
    return NextResponse.json({ error: message }, { status });
  }
}
