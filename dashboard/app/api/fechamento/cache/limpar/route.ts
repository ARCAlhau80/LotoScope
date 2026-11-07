import { NextRequest, NextResponse } from 'next/server';
import { cacheLimpar } from '@/lib/fechamento-combinatorio';

export async function POST(request: NextRequest) {
  try {
    cacheLimpar();
    return NextResponse.json({ sucesso: true, mensagem: "Cache de fechamentos limpo com sucesso" });
  } catch (error: any) {
    return NextResponse.json({ sucesso: false, error: error?.message }, { status: 400 });
  }
}
