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

export interface RankingCombinacaoItem {
  id: number;
  numeros: number[];
  acertos_11: number;
  acertos_12: number;
  acertos_13: number;
  acertos_14: number;
  atraso_11: number;
  atraso_12: number;
  atraso_13: number;
  atraso_14: number;
  score: number;
}

export type RankingPerfil = 'foco11' | 'equilibrado' | 'altovalor';

const PESOS_RANKING: Record<RankingPerfil, { freq: number[]; atraso: number[] }> = {
  foco11: {
    freq: [1.0, 0.25, 0.05, 0.01],
    atraso: [1.0, 0.3, 0.1, 0.05],
  },
  equilibrado: {
    freq: [1.0, 1.0, 1.0, 1.0],
    atraso: [1.0, 1.0, 1.0, 1.0],
  },
  altovalor: {
    freq: [0.3, 1.0, 5.0, 20.0],
    atraso: [0.3, 1.0, 5.0, 20.0],
  },
};

export async function carregarRankingCombinacoes(
  perfil: RankingPerfil = 'altovalor',
  top: number = 20,
  loteriaId: string = 'lotofacil'
): Promise<RankingCombinacaoItem[]> {
  const cfg = getLotteryConfig(loteriaId);
  const pesos = PESOS_RANKING[perfil];
  const p = await getPool();

  const maxResult = await p.request()
    .query(`SELECT MAX(UltimoConcursoAtualizado) AS ultimo FROM ${cfg.tabela_combinacoes}`);
  const ultimo = Number(maxResult.recordset[0]?.ultimo ?? 0);
  if (!ultimo) return [];

  const cols = cfg.colunas_resultado.join(',');
  // Query simplificada: sem CTEs de media, ordenacao direta por score bruto.
  // Muito mais rapida (~1-2s vs >15s). O score e relativo, nao normalizado.
  const query = `
    SELECT TOP (@topParam)
      ID,
      ${cols},
      Acertos_11, Acertos_12, Acertos_13, Acertos_14,
      @ultimoParam - Ultimo_Acertos_11 AS a11,
      @ultimoParam - Ultimo_Acertos_12 AS a12,
      @ultimoParam - Ultimo_Acertos_13 AS a13,
      @ultimoParam - Ultimo_Acertos_14 AS a14,
      (
        Acertos_11 * @w11f + Acertos_12 * @w12f + Acertos_13 * @w13f + Acertos_14 * @w14f +
        (@ultimoParam - Ultimo_Acertos_11) * @w11a + (@ultimoParam - Ultimo_Acertos_12) * @w12a +
        (@ultimoParam - Ultimo_Acertos_13) * @w13a + (@ultimoParam - Ultimo_Acertos_14) * @w14a
      ) AS score
    FROM ${cfg.tabela_combinacoes}
    ORDER BY score DESC
  `;

  const result = await p.request()
    .input('ultimoParam', sql.Int, ultimo)
    .input('topParam', sql.Int, Math.max(1, top))
    .input('w11f', sql.Float, pesos.freq[0])
    .input('w12f', sql.Float, pesos.freq[1])
    .input('w13f', sql.Float, pesos.freq[2])
    .input('w14f', sql.Float, pesos.freq[3])
    .input('w11a', sql.Float, pesos.atraso[0])
    .input('w12a', sql.Float, pesos.atraso[1])
    .input('w13a', sql.Float, pesos.atraso[2])
    .input('w14a', sql.Float, pesos.atraso[3])
    .query(query);

  const numCols = cfg.colunas_resultado;
  return result.recordset.map((r: Record<string, number>) => ({
    id: Number(r.ID),
    numeros: numCols.map(k => Number(r[k])),
    acertos_11: Number(r.Acertos_11),
    acertos_12: Number(r.Acertos_12),
    acertos_13: Number(r.Acertos_13),
    acertos_14: Number(r.Acertos_14),
    atraso_11: Number(r.a11),
    atraso_12: Number(r.a12),
    atraso_13: Number(r.a13),
    atraso_14: Number(r.a14),
    score: Number(r.score),
  }));
}
