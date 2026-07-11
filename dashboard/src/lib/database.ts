import sql from 'mssql';
import { getLotteryConfig, type LotteryConfig } from './lottery-config';

const DB_CONFIG: sql.config = {
  server: process.env.DB_SERVER || 'localhost',
  database: process.env.DB_NAME || 'Lotofacil',
  user: process.env.DB_USER || 'sa',
  password: process.env.DB_PASSWORD || 'LotoScope@2024',
  options: {
    trustServerCertificate: true,
    connectTimeout: 15000,
  },
};

let pool: sql.ConnectionPool | null = null;

async function getPool(): Promise<sql.ConnectionPool> {
  if (!pool) {
    pool = await sql.connect(DB_CONFIG);
  }
  return pool;
}

export interface Resultado {
  concurso: number;
  numeros: number[];
  trevos?: number[];
}

export async function carregarResultados(lotteryId?: string): Promise<Resultado[]> {
  const cfg = lotteryId ? getLotteryConfig(lotteryId) : getLotteryConfig('lotofacil');
  const p = await getPool();
  const cols = [...cfg.colunas_resultado];
  if (cfg.trevos_cols) cols.push(...cfg.trevos_cols);
  const sqlQuery = cols.length > 0
    ? `SELECT Concurso,${cols.join(',')} FROM ${cfg.tabela_resultados} ORDER BY Concurso`
    : `SELECT * FROM ${cfg.tabela_resultados} ORDER BY Concurso`;
  const result = await p.request().query(sqlQuery);

  if (result.recordset.length === 0) return [];

  const trevosSet = new Set(cfg.trevos_cols ?? []);
  const keys = Object.keys(result.recordset[0]).filter(k => k !== 'Concurso' && !trevosSet.has(k));
  const trevoKeys = cfg.trevos_cols ?? [];
  return result.recordset.map((r: Record<string, number>) => ({
    concurso: Number(r.Concurso),
    numeros: keys.map(k => Number(r[k])).filter(n => !isNaN(n)),
    ...(trevoKeys.length > 0 ? { trevos: trevoKeys.map(k => Number(r[k])).filter(n => !isNaN(n)) } : {}),
  }));
}

export async function carregarResultadosPorConfig(cfg: LotteryConfig): Promise<Resultado[]> {
  return carregarResultados(cfg.id);
}
