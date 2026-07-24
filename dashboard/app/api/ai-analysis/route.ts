import { NextResponse } from 'next/server';
import { execSync } from 'child_process';
import path from 'path';

export const dynamic = 'force-dynamic';
export const maxDuration = 300;

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const loteria: string | undefined = body.loteria;
    const compare: number | undefined = body.compare;
    const pedido: string | undefined = body.pedido;
    const rankingPerfil: string | undefined = body.rankingPerfil;
    const rankingTop: number | undefined = body.rankingTop;

    const projectRoot = path.resolve(process.cwd(), '..');
    const scriptPath = path.join(projectRoot, 'ia_lotoscope.py');

    let cmd = `python "${scriptPath}" --json --no-save --no-context`;
    if (compare && compare > 0) {
      cmd += ` --compare ${compare}`;
    }
    if (pedido) {
      cmd += ` --pedido "${pedido.replace(/"/g, '\\"')}"`;
    }
    if (rankingPerfil) {
      cmd += ` --ranking-perfil ${rankingPerfil}`;
    }
    if (rankingTop && rankingTop > 0) {
      cmd += ` --ranking-top ${rankingTop}`;
    }
    if (loteria) {
      cmd += ` "${loteria}"`;
    }

    const stdout = execSync(cmd, {
      cwd: projectRoot,
      timeout: 300_000,
      shell: process.platform === 'win32' ? 'powershell' : undefined,
      maxBuffer: 10 * 1024 * 1024,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    });

    const text = Buffer.from(stdout).toString();
    const result = JSON.parse(text);
    return NextResponse.json(result);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}
