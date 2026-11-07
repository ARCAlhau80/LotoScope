import { readFileSync, writeFileSync } from 'node:fs';
import { gerarJogosDiversificados, type ObjetivoRanking, type OrdenacaoJogos, type OtimizacaoRanking } from '../src/lib/gerador-diversificado';
import { carregarResultados } from '../src/lib/database';

export interface Draw {
  concurso: number;
  numeros: number[];
}

export interface BacktestConfig {
  nJogos: number;
  totalNumeros: number;
  numerosPorJogo: number;
  numeroMinimo: number;
  ordenacao: OrdenacaoJogos;
  objetivoRanking: ObjetivoRanking;
  otimizacao: OtimizacaoRanking;
  seed: number;
  baselineRuns: number;
  warmup: number;
  limit: number;
  step: number;
}

export interface ResultadoConcurso {
  concurso: number;
  acertos: number[];
  melhorAcertos: number;
  mediaAcertos: number;
  baselineMelhor: number;
  baselineMedia: number;
  baselineTaxa11: number;
}

export interface ResumoBacktest {
  concursos: number;
  jogosPorConcurso: number;
  mediaMelhor: number;
  maxMelhor: number;
  mediaMedia: number;
  distribuicaoMelhor: Record<string, number>;
  distribuicaoJogos: Record<string, number>;
  baselineMediaMelhor: number;
  baselineMaxMelhor: number;
  liftMedia: number | null;
  taxa11mais: number;
  baselineTaxa11mais: number;
  lift11mais: number | null;
}

export interface BacktestOutput {
  config: BacktestConfig;
  concursos: ResultadoConcurso[];
  resumo: ResumoBacktest;
}

const DEFAULT_CONFIG: BacktestConfig = {
  nJogos: 5,
  totalNumeros: 25,
  numerosPorJogo: 15,
  numeroMinimo: 1,
  ordenacao: 'melhores',
  objetivoRanking: 'top1',
  otimizacao: 'pool',
  seed: 2024,
  baselineRuns: 100,
  warmup: 30,
  limit: 0,
  step: 1,
};

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

export function normalizarDraws(raw: unknown): Draw[] {
  if (!Array.isArray(raw)) throw new Error('JSON deve ser um array de sorteios');
  return raw.map((item, i): Draw => {
    if (Array.isArray(item)) {
      const numeros = item.map(Number).filter(n => Number.isFinite(n));
      if (numeros.length === 0) throw new Error(`Sorteio ${i + 1}: lista de números vazia`);
      return { concurso: i + 1, numeros: [...new Set(numeros)].sort((a, b) => a - b) };
    }
    if (isRecord(item) && Array.isArray(item.numeros)) {
      const numeros = item.numeros.map(Number).filter(n => Number.isFinite(n));
      if (numeros.length === 0) throw new Error(`Sorteio ${i + 1}: lista de números vazia`);
      const concurso = typeof item.concurso === 'number' ? item.concurso : i + 1;
      return { concurso, numeros: [...new Set(numeros)].sort((a, b) => a - b) };
    }
    throw new Error(`Sorteio ${i + 1}: formato inválido (esperado number[] ou {concurso, numeros})`);
  });
}

export function carregarDraws(filePath: string): Draw[] {
  const raw = JSON.parse(readFileSync(filePath, 'utf-8').replace(/^\uFEFF/, '')) as unknown;
  return normalizarDraws(raw);
}

function rng(seed: number): () => number {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function seedConcurso(base: number, concurso: number): number {
  return ((base ^ (concurso * 2654435761)) >>> 0) || 1;
}

function jogoAleatorio(total: number, minimo: number, k: number, rand: () => number): number[] {
  const pool = Array.from({ length: total }, (_, i) => i + minimo);
  for (let i = 0; i < k; i++) {
    const j = i + Math.floor(rand() * (total - i));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, k).sort((a, b) => a - b);
}

function contarAcertos(jogo: number[], drawSet: Set<number>): number {
  let hits = 0;
  for (const n of jogo) if (drawSet.has(n)) hits++;
  return hits;
}

function distribuicao(acertos: number[], maxAcertos: number): Record<string, number> {
  const out: Record<string, number> = {};
  for (let h = 0; h <= maxAcertos; h++) out[String(h)] = 0;
  for (const h of acertos) out[String(h)] = (out[String(h)] ?? 0) + 1;
  return out;
}

function media(xs: number[]): number {
  return xs.length > 0 ? xs.reduce((a, b) => a + b, 0) / xs.length : 0;
}

function razao(a: number, b: number): number | null {
  return b > 0 ? Math.round((a / b) * 10000) / 10000 : null;
}

export function resumir(resultados: ResultadoConcurso[], cfg: BacktestConfig): ResumoBacktest {
  const melhores = resultados.map(r => r.melhorAcertos);
  const todos = resultados.flatMap(r => r.acertos);
  const baseline = resultados.map(r => r.baselineMelhor);
  const taxa11 = melhores.filter(h => h >= 11).length / Math.max(resultados.length, 1);
  const baselineTaxa11 = media(resultados.map(r => r.baselineTaxa11));
  return {
    concursos: resultados.length,
    jogosPorConcurso: cfg.nJogos,
    mediaMelhor: Math.round(media(melhores) * 100) / 100,
    maxMelhor: melhores.length > 0 ? Math.max(...melhores) : 0,
    mediaMedia: Math.round(media(resultados.map(r => r.mediaAcertos)) * 100) / 100,
    distribuicaoMelhor: distribuicao(melhores, cfg.numerosPorJogo),
    distribuicaoJogos: distribuicao(todos, cfg.numerosPorJogo),
    baselineMediaMelhor: Math.round(media(baseline) * 100) / 100,
    baselineMaxMelhor: baseline.length > 0 ? Math.max(...baseline) : 0,
    liftMedia: razao(media(melhores), media(baseline)),
    taxa11mais: Math.round(taxa11 * 10000) / 10000,
    baselineTaxa11mais: Math.round(baselineTaxa11 * 10000) / 10000,
    lift11mais: razao(taxa11, baselineTaxa11),
  };
}

export function executarBacktest(draws: Draw[], cfg: BacktestConfig): BacktestOutput {
  if (draws.length === 0) throw new Error('Nenhum sorteio para o backtest');
  const inicio = Math.min(Math.max(cfg.warmup, 1), draws.length - 1);
  const resultados: ResultadoConcurso[] = [];

  for (let i = inicio; i < draws.length; i += Math.max(cfg.step, 1)) {
    if (cfg.limit > 0 && resultados.length >= cfg.limit) break;
    const historico = draws.slice(0, i).map(d => d.numeros);
    const alvo = draws[i];
    const alvoSet = new Set(alvo.numeros);
    const jogos = gerarJogosDiversificados({
      resultados: historico,
      nJogos: cfg.nJogos,
      seed: seedHistorico(cfg.seed, alvo.concurso),
      totalNumeros: cfg.totalNumeros,
      numerosPorJogo: cfg.numerosPorJogo,
      numeroMinimo: cfg.numeroMinimo,
      ordenacao: cfg.ordenacao,
      objetivoRanking: cfg.objetivoRanking,
      otimizacao: cfg.otimizacao,
    });
    const acertos = jogos.map(j => contarAcertos(j.numeros, alvoSet));

    const rand = rng(seedConcurso(cfg.seed, alvo.concurso));
    // Baseline justo: `baselineRuns` grupos de `nJogos` jogos aleatórios.
    // Compara o melhor-do-grupo (mesmo k do ranking) com o melhor do ranking.
    const grupos = Math.max(cfg.baselineRuns, 1);
    let somaMelhor = 0;
    let somaMedia = 0;
    let grupos11 = 0;
    for (let g = 0; g < grupos; g++) {
      const acertosGrupo: number[] = [];
      for (let r = 0; r < cfg.nJogos; r++) {
        const jogo = jogoAleatorio(cfg.totalNumeros, cfg.numeroMinimo, cfg.numerosPorJogo, rand);
        acertosGrupo.push(contarAcertos(jogo, alvoSet));
      }
      const melhorGrupo = Math.max(...acertosGrupo);
      somaMelhor += melhorGrupo;
      somaMedia += media(acertosGrupo);
      if (melhorGrupo >= 11) grupos11++;
    }

    resultados.push({
      concurso: alvo.concurso,
      acertos,
      melhorAcertos: acertos.length > 0 ? Math.max(...acertos) : 0,
      mediaAcertos: Math.round(media(acertos) * 100) / 100,
      baselineMelhor: Math.round((somaMelhor / grupos) * 100) / 100,
      baselineMedia: Math.round((somaMedia / grupos) * 100) / 100,
      baselineTaxa11: Math.round((grupos11 / grupos) * 10000) / 10000,
    });
  }

  return { config: cfg, concursos: resultados, resumo: resumir(resultados, cfg) };
}

function seedHistorico(base: number, concurso: number): number {
  return (base + concurso * 7919) % 2147483647;
}

function parseArgs(argv: string[]): { filePath?: string; db: boolean; loteria: string; json: boolean; out?: string; help: boolean; cfg: BacktestConfig } {
  const cfg: BacktestConfig = { ...DEFAULT_CONFIG };
  let filePath: string | undefined;
  let db = false;
  let loteria = 'lotofacil';
  let json = false;
  let out: string | undefined;
  let help = false;

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = () => {
      const v = argv[++i];
      if (v === undefined) throw new Error(`Faltou valor para ${arg}`);
      return v;
    };
    const num = (minimo: number) => {
      const n = Number(next());
      if (!Number.isFinite(n)) throw new Error(`Valor numérico inválido para ${arg}`);
      return Math.max(minimo, Math.trunc(n));
    };
    switch (arg) {
      case '--file': filePath = next(); break;
      case '--db': db = true; break;
      case '--loteria': loteria = next(); break;
      case '--n': cfg.nJogos = num(1); break;
      case '--dezenas': cfg.numerosPorJogo = num(1); break;
      case '--total': cfg.totalNumeros = num(1); break;
      case '--min': cfg.numeroMinimo = num(-1_000_000); break;
      case '--seed': cfg.seed = num(-2_147_483_646); break;
      case '--baseline': cfg.baselineRuns = num(1); break;
      case '--warmup': cfg.warmup = num(1); break;
      case '--limit': cfg.limit = num(0); break;
      case '--step': cfg.step = num(1); break;
      case '--ordenacao': {
        const v = next();
        if (v !== 'melhores' && v !== 'piores') throw new Error('--ordenacao deve ser melhores ou piores');
        cfg.ordenacao = v;
        break;
      }
      case '--objetivo': {
        const v = next();
        if (v !== 'top1' && v !== 'soma' && v !== 'minimo') throw new Error('--objetivo deve ser top1, soma ou minimo');
        cfg.objetivoRanking = v;
        break;
      }
      case '--otimizacao': {
        const v = next();
        if (v !== 'pool' && v !== 'exata') throw new Error('--otimizacao deve ser pool ou exata');
        cfg.otimizacao = v;
        break;
      }
      case '--json': json = true; break;
      case '--out': out = next(); break;
      case '--help':
      case '-h': help = true; break;
      default: throw new Error(`Argumento desconhecido: ${arg}`);
    }
  }
  return { filePath, db, loteria, json, out, help, cfg };
}

function imprimirAjuda(): void {
  console.log(`Backtest do ranking (acertos vs baseline aleatório)

Uso:
  npx tsx scripts/backtest-ranking.ts --file dados/sorteios.json [opções]
  npx tsx scripts/backtest-ranking.ts --db [opções]

Entrada JSON (offline):
  - number[][]                      ex.: [[1,2,...], ...] (ordem cronológica)
  - {concurso, numeros: number[]}[] ex.: [{"concurso":1,"numeros":[...]}, ...]

Opções:
  --db             usa os sorteios do SQL Server (em vez de --file)
  --loteria <id>   loteria do banco (default lotofacil)
  --n <k>          jogos por concurso (default 5)
  --dezenas <k>    dezenas por jogo (default 15)
  --total <n>      universo de dezenas (default 25)
  --min <n>        primeira dezena (default 1)
  --warmup <n>     sorteios usados antes do 1º teste (default 30)
  --limit <n>      máximo de concursos testados (0 = todos, default 0)
  --step <n>       passo entre concursos (default 1)
  --baseline <n>   grupos de n jogos aleatórios por concurso (default 100)
  --ordenacao <m>  melhores | piores (default melhores)
  --objetivo <o>   top1 | soma | minimo (default top1)
  --otimizacao <m> pool | exata (default pool)
  --seed <n>       seed determinística (default 2024)
  --json           imprime o resultado completo em JSON
  --out <arquivo>  grava o resultado JSON no arquivo
  --help           esta ajuda
`);
}

function imprimirResumo(out: BacktestOutput): void {
  const r = out.resumo;
  console.log(`\nBacktest: ${r.concursos} concurso(s) · ${r.jogosPorConcurso} jogo(s)/concurso · ${out.config.ordenacao}/${out.config.otimizacao}${out.config.otimizacao === 'exata' ? `/${out.config.objetivoRanking}` : ''}`);
  console.log(`  Melhor acerto: média ${r.mediaMelhor} · máximo ${r.maxMelhor}`);
  console.log(`  Média de acertos dos jogos: ${r.mediaMedia}`);
  console.log(`  Baseline aleatório: média ${r.baselineMediaMelhor} · máximo ${r.baselineMaxMelhor}`);
  console.log(`  Lift (média): ${r.liftMedia ?? 'n/d'}`);
  console.log(`  11+ acertos: ${(r.taxa11mais * 100).toFixed(2)}% vs baseline ${(r.baselineTaxa11mais * 100).toFixed(2)}% · lift ${r.lift11mais ?? 'n/d'}`);
  console.log('  Distribuição do melhor acerto por concurso:');
  for (const [h, qtd] of Object.entries(r.distribuicaoMelhor)) {
    if (qtd > 0) console.log(`    ${h} acerto(s): ${qtd}`);
  }
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { imprimirAjuda(); return; }
  let draws: Draw[];
  if (args.db) {
    const resultados = await carregarResultados(args.loteria);
    draws = resultados.map(r => ({ concurso: r.concurso, numeros: r.numeros }));
  } else {
    if (!args.filePath) { imprimirAjuda(); process.exitCode = 1; return; }
    draws = carregarDraws(args.filePath);
  }
  const out = executarBacktest(draws, args.cfg);
  if (args.out) writeFileSync(args.out, JSON.stringify(out, null, 2), 'utf-8');
  if (args.json) console.log(JSON.stringify(out, null, 2));
  else imprimirResumo(out);
}

const invokedDirectly = (process.argv[1] ?? '').replace(/\\/g, '/').endsWith('/scripts/backtest-ranking.ts');
if (invokedDirectly) {
  main().catch(err => {
    console.error(err instanceof Error ? err.message : String(err));
    process.exitCode = 1;
  });
}
