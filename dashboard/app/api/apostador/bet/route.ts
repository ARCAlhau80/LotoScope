import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { writeFile, mkdir } from 'fs/promises';
import { randomUUID } from 'crypto';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const form = await request.formData();
    const file = form.get('arquivo');
    const loteria = String(form.get('loteria') || 'lotofacil');
    const headless = String(form.get('headless') || 'true') === 'true';
    const dryRun = String(form.get('dry_run') || 'false') === 'true';
    const attach = String(form.get('attach') || 'false') === 'true';
    const debugPortRaw = form.get('debug_port');

    if (!file || typeof file === 'string' || !('arrayBuffer' in file)) {
      return NextResponse.json({ success: false, error: 'Nenhum arquivo enviado' }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const ext = path.extname(file.name || '.txt').toLowerCase();
    const jobId = randomUUID();

    const projectRoot = path.resolve(process.cwd(), '..');
    const uploadDir = path.join(projectRoot, 'workflow-graph', 'apostador-uploads');
    await mkdir(uploadDir, { recursive: true });
    const filePath = path.join(uploadDir, `${jobId}${ext}`);
    await writeFile(filePath, buffer);

    const scriptPath = path.join(projectRoot, 'apostador_automacao_cli.py');
    const args = [scriptPath, filePath, '--loteria', loteria, '--json'];
    if (headless) args.push('--headless');
    if (dryRun) args.push('--dry-run');
    if (attach) {
      args.push('--attach');
      const port = parseInt(String(debugPortRaw), 10);
      if (!Number.isNaN(port)) args.push('--debug-port', String(port));
    }

    const logPath = path.join(projectRoot, 'workflow-graph', 'apostador-uploads', `${jobId}.log`);
    const logFd = require('fs').openSync(logPath, 'a');

    const child = spawn(getPythonBin(), args, {
      cwd: projectRoot,
      detached: true,
      stdio: ['ignore', logFd, logFd],
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    });
    child.unref();

    return NextResponse.json({
      success: true,
      job_id: jobId,
      status: 'iniciado',
      loteria,
      mensagem: 'Automação iniciada em segundo plano. O navegador abrirá e permanecerá aberto — faça login e finalize a compra quando terminar.',
      log: logPath,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Erro desconhecido';
    console.error('Erro em /api/apostador/bet:', err);
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}

function getPythonBin(): string {
  if (process.platform !== 'win32') return 'python';
  const venv = path.join(process.cwd(), '..', '.venv', 'Scripts', 'python.exe');
  return venv;
}