import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';

export type SolverFechamento = 'cp_sat' | 'SCIP' | 'CBC';

export interface CpSatFechamentoInput {
  universo: number[];
  k: number;
  t: number;
  extras: number[][];
  seed?: number;
  pool?: number;
  timeLimit?: number;
  threads?: number;
  maxApostas?: number;
  upperBound?: number;
  solver?: SolverFechamento;
}

export interface CpSatFechamentoResult {
  status: string;
  objective: number | null;
  bestBound: number | null;
  bets: number[][];
  wallTime: number;
  numCandidates: number;
  numTargets: number;
  lowerBound: number;
  solver: SolverFechamento;
  error?: string;
}

function nomeScript(solver: SolverFechamento): string {
  return solver === 'cp_sat' ? 'cp_sat_fechamento.py' : 'mip_fechamento.py';
}

function resolverScript(solver: SolverFechamento): string | null {
  const arquivo = nomeScript(solver);
  const candidatos = [
    path.resolve(process.cwd(), 'scripts', arquivo),
    path.resolve(process.cwd(), '..', 'dashboard', 'scripts', arquivo),
  ];
  for (const candidato of candidatos) {
    if (existsSync(candidato)) return candidato;
  }
  return null;
}

function resolverPython(): string {
  const env = process.env.CP_SAT_PYTHON || process.env.PYTHON_BIN;
  if (env) return env;
  const cwd = process.cwd();
  const candidatos = [
    path.resolve(cwd, '..', '.venv', 'Scripts', 'python.exe'),
    path.resolve(cwd, '.venv', 'Scripts', 'python.exe'),
    path.resolve(cwd, '..', '.venv', 'bin', 'python'),
    path.resolve(cwd, '.venv', 'bin', 'python'),
  ];
  for (const candidato of candidatos) {
    if (existsSync(candidato)) return candidato;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}

function rotuloSolver(solver: SolverFechamento): string {
  return solver === 'cp_sat' ? 'CP-SAT' : solver;
}

/**
 * Executa um solver de fechamento (CP-SAT, SCIP ou CBC).
 * Retorna null se o script Python não existir.
 */
export async function resolverFechamentoSolver(
  input: CpSatFechamentoInput,
): Promise<CpSatFechamentoResult | null> {
  const solver = input.solver ?? 'cp_sat';
  const script = resolverScript(solver);
  if (!script) return null;

  const timeLimit = Math.max(1, input.timeLimit ?? 10);
  const payload = {
    universo: input.universo,
    k: input.k,
    t: input.t,
    extras: input.extras,
    seed: input.seed ?? 1,
    pool: input.pool ?? 500,
    time_limit: timeLimit,
    threads: input.threads ?? 4,
    max_apostas: input.maxApostas ?? 0,
    upper_bound: input.upperBound ?? 0,
    solver: solver === 'cp_sat' ? 'cp_sat' : solver,
  };

  return new Promise((resolve) => {
    let finalizado = false;
    const finalizar = (resultado: CpSatFechamentoResult) => {
      if (finalizado) return;
      finalizado = true;
      resolve(resultado);
    };

    const python = resolverPython();
    const child = spawn(python, [script], {
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
    });

    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      try { child.kill(); } catch { /* ignore */ }
      finalizar({
        status: 'TIMEOUT',
        objective: null,
        bestBound: null,
        bets: [],
        wallTime: timeLimit,
        numCandidates: 0,
        numTargets: 0,
        lowerBound: 0,
        solver,
        error: `${rotuloSolver(solver)} excedeu ${timeLimit + 15}s`,
      });
    }, (timeLimit + 15) * 1000);

    child.stdout.on('data', (data) => { stdout += String(data); });
    child.stderr.on('data', (data) => { stderr += String(data); });
    child.on('error', (error) => {
      clearTimeout(timer);
      finalizar({
        status: 'ERRO',
        objective: null,
        bestBound: null,
        bets: [],
        wallTime: 0,
        numCandidates: 0,
        numTargets: 0,
        lowerBound: 0,
        solver,
        error: error.message,
      });
    });
    child.on('close', () => {
      clearTimeout(timer);
      const texto = stdout.trim();
      if (!texto) {
        finalizar({
          status: 'ERRO',
          objective: null,
          bestBound: null,
          bets: [],
          wallTime: 0,
          numCandidates: 0,
          numTargets: 0,
          lowerBound: 0,
          solver,
          error: stderr.trim().slice(0, 1000) || `${rotuloSolver(solver)} não retornou saída`,
        });
        return;
      }
      try {
        const data = JSON.parse(texto);
        finalizar({
          status: String(data.status ?? 'DESCONHECIDO'),
          objective: data.objective ?? null,
          bestBound: data.best_bound ?? null,
          bets: Array.isArray(data.bets) ? data.bets : [],
          wallTime: Number(data.wall_time ?? 0),
          numCandidates: Number(data.num_candidates ?? 0),
          numTargets: Number(data.num_targets ?? 0),
          lowerBound: Number(data.lower_bound ?? 0),
          solver,
          error: data.error ? String(data.error) : undefined,
        });
      } catch (error: any) {
        finalizar({
          status: 'ERRO',
          objective: null,
          bestBound: null,
          bets: [],
          wallTime: 0,
          numCandidates: 0,
          numTargets: 0,
          lowerBound: 0,
          solver,
          error: `Resposta inválida do ${rotuloSolver(solver)}: ${error?.message ?? error}`,
        });
      }
    });

    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
  });
}

/** Compatibilidade: executa CP-SAT. */
export function resolverFechamentoCpSat(
  input: CpSatFechamentoInput,
): Promise<CpSatFechamentoResult | null> {
  return resolverFechamentoSolver({ ...input, solver: 'cp_sat' });
}

/** Executa MIP com SCIP ou CBC. */
export function resolverFechamentoMip(
  input: CpSatFechamentoInput & { solver: 'SCIP' | 'CBC' },
): Promise<CpSatFechamentoResult | null> {
  return resolverFechamentoSolver(input);
}
