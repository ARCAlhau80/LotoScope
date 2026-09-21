import { NextRequest, NextResponse } from 'next/server';
import { spawnSync } from 'child_process';
import path from 'path';
import { writeFile, unlink } from 'fs/promises';
import os from 'os';
import { randomUUID } from 'crypto';
import { getLotteryConfig, calcularPrecoAposta } from '@/lib/lottery-config';

export const dynamic = 'force-dynamic';
export const maxDuration = 120;

export async function POST(request: NextRequest) {
  let tmpPath: string | null = null;
  try {
    const form = await request.formData();
    const file = form.get('arquivo');
    const loteria = String(form.get('loteria') || 'lotofacil');

    if (!file || typeof file === 'string' || !('arrayBuffer' in file)) {
      return NextResponse.json({ success: false, error: 'Nenhum arquivo enviado' }, { status: 400 });
    }

    const cfg = getLotteryConfig(loteria);
    const buffer = Buffer.from(await file.arrayBuffer());
    const ext = path.extname(file.name || '.txt').toLowerCase();

    tmpPath = path.join(os.tmpdir(), `apostador-${randomUUID()}${ext}`);
    await writeFile(tmpPath, buffer);

    const projectRoot = path.resolve(process.cwd(), '..');
    const scriptPath = path.join(projectRoot, 'apostador_parse_cli.py');
    const args = [scriptPath, tmpPath, '--loteria', loteria, '--json'];

    const stdout = spawnSync(getPythonBin(), args, {
      cwd: projectRoot,
      timeout: 120_000,
      maxBuffer: 10 * 1024 * 1024,
      encoding: 'utf-8',
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    });

    if (stdout.error) {
      throw stdout.error;
    }
    const text = stdout.stdout || '';
    let result;
    try {
      result = JSON.parse(text);
    } catch {
      const stderr = (stdout.stderr || '').trim() || 'Falha ao processar arquivo';
      return NextResponse.json({ success: false, error: stderr }, { status: 500 });
    }
    if (!result.success) {
      return NextResponse.json({ success: false, error: result.error }, { status: 400 });
    }

    const validos = result.validos ?? [];
    const precoUnit = calcularPrecoAposta(loteria, validos[0]?.numeros?.length ?? cfg.numeros_por_jogo);
    const custoTotal = validos.length * precoUnit;

    return NextResponse.json({
      success: true,
      loteria,
      nome_jogo: cfg.nome_jogo,
      total_jogos: result.total_jogos,
      validos,
      invalids: result.invalids ?? [],
      preco_unitario: precoUnit,
      custo_total: custoTotal,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Erro desconhecido';
    console.error('Erro em /api/apostador/parse:', err);
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  } finally {
    if (tmpPath) {
      unlink(tmpPath).catch(() => {});
    }
  }
}

function getPythonBin(): string {
  if (process.platform !== 'win32') return 'python';
  const venv = path.join(process.cwd(), '..', '.venv', 'Scripts', 'python.exe');
  return venv;
}