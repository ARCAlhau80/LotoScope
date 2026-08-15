import { NextRequest, NextResponse } from 'next/server';
import { carregarResultados } from '@/lib/database';
import { gerarJogosDiversificados, calcularEstimativaCombinacoes } from '@/lib/gerador-diversificado';
import sql from 'mssql';
import { getLotteryConfig, validarDezenas } from '@/lib/lottery-config';

async function getPool() {
  return sql.connect({
    server: process.env.DB_SERVER || 'localhost',
    database: process.env.DB_NAME || 'Lotofacil',
    user: process.env.DB_USER || 'sa',
    password: process.env.DB_PASSWORD || 'LotoScope@2024',
    options: { trustServerCertificate: true, connectTimeout: 15000 },
  });
}

async function carregarCicloNoConcurso(loteriaId: string = 'lotofacil', concursoBase?: number): Promise<Record<number, number> | undefined> {
  try {
    const cfg = getLotteryConfig(loteriaId);
    
    if (!cfg.tabela_ciclos) {
      return undefined;
    }
    
    const pool = await getPool();

    let cicloId: number | null = null;
    let concursoInicio: number | null = null;

    if (concursoBase !== undefined) {
      const result = await pool.request()
        .input('concurso', sql.Int, concursoBase)
        .query(`
          SELECT TOP 1 Ciclo, ConcursoInicio 
          FROM ${cfg.tabela_ciclos}
          WHERE ConcursoInicio <= @concurso 
            AND (ConcursoFechamento IS NULL OR ConcursoFechamento >= @concurso)
          ORDER BY Ciclo DESC
        `);
      if (result.recordset[0]) {
        cicloId = Number(result.recordset[0].Ciclo);
        concursoInicio = Number(result.recordset[0].ConcursoInicio);
      }
    }

    if (cicloId === null) {
      const result = await pool.request()
        .query(`SELECT TOP 1 Ciclo, ConcursoInicio FROM ${cfg.tabela_ciclos} ORDER BY Ciclo DESC`);
      if (result.recordset[0]) {
        cicloId = Number(result.recordset[0].Ciclo);
        concursoInicio = Number(result.recordset[0].ConcursoInicio);
      }
    }

    if (cicloId === null || concursoInicio === null) return undefined;

    const resultadoSorteios = await pool.request()
      .input('inicio', sql.Int, concursoInicio)
      .input('fim', sql.Int, concursoBase ?? 99999)
      .query(`
        SELECT ${cfg.colunas_resultado.join(',')}
        FROM ${cfg.tabela_resultados}
        WHERE Concurso >= @inicio AND Concurso <= @fim
        ORDER BY Concurso
      `);

    const cicloDados: Record<number, number> = {};
    for (let i = cfg.numero_minimo; i <= cfg.numero_maximo; i++) cicloDados[i] = 0;

    for (const row of resultadoSorteios.recordset) {
      for (const col of cfg.colunas_resultado) {
        const n = Number(row[col]);
        if (n >= cfg.numero_minimo && n <= cfg.numero_maximo) {
          cicloDados[n] = (cicloDados[n] ?? 0) + 1;
        }
      }
    }

    return cicloDados;
  } catch (e) {
    console.error('Erro ao carregar ciclo no concurso:', e);
    return undefined;
  }
}

function parseParams(searchParams: URLSearchParams) {
  const loteria = searchParams.get('loteria') || 'lotofacil';
  const cfg = getLotteryConfig(loteria);
  const seedParam = searchParams.get('seed');
  const fixosParam = searchParams.get('fixos');
  const excluidosParam = searchParams.get('excluidos');
  const concursoParam = searchParams.get('concurso');
  const dezenasParam = searchParams.get('dezenas');

  const seed = seedParam ? parseInt(seedParam, 10) : undefined;
  const concursoBase = concursoParam ? parseInt(concursoParam, 10) : undefined;
  const dezenasRaw = dezenasParam ? parseInt(dezenasParam, 10) : undefined;
  const dezenas = validarDezenas(cfg, dezenasRaw);
  const fixos = fixosParam ? fixosParam.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
  const excluidos = excluidosParam ? excluidosParam.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;

  return { loteria, seed, concursoBase, fixos, excluidos, dezenas, cfg };
}

export async function GET(request: NextRequest) {
  try {
    const { loteria, seed, concursoBase, fixos, excluidos, dezenas, cfg } = parseParams(new URL(request.url).searchParams);

    const resultados = await carregarResultados(loteria);
    const resultadosAteBase = concursoBase !== undefined
      ? resultados.filter(r => r.concurso <= concursoBase)
      : resultados;
    const numeros = resultadosAteBase.map(r => r.numeros);
    const cicloDados = await carregarCicloNoConcurso(loteria, concursoBase);

    const estimativa = calcularEstimativaCombinacoes(fixos, excluidos, cfg.total_numeros, dezenas, cfg.numero_minimo);

    const LIMITE_MEMORIA = 500000;
    if (estimativa > LIMITE_MEMORIA) {
      return NextResponse.json(
        { success: false, error: `Total de combinações (${estimativa.toLocaleString('pt-BR')}) excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

    const jogos = gerarJogosDiversificados({
      resultados: numeros,
      cicloDados,
      nJogos: 0,
      seed,
      fixos,
      excluidos,
      totalNumeros: cfg.total_numeros,
      numerosPorJogo: dezenas,
      numeroMinimo: cfg.numero_minimo,
      primos: cfg.primos,
    });

    const texto = jogos.map(j => j.numeros.join(',')).join('\n');
    const blob = new Blob([texto], { type: 'text/plain; charset=utf-8' });

    return new NextResponse(blob, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Disposition': `attachment; filename="jogos-${loteria}-${dezenas}dezenas-todas-${new Date().toISOString().slice(0, 10)}.txt"`,
      },
    });
  } catch (error) {
    console.error('Erro em /api/jogos-diversos/export:', error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : 'Erro desconhecido' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { loteria = 'lotofacil', seed, fixos, excluidos, concurso, dezenas: dezenasBody } = body || {};
    const cfg = getLotteryConfig(loteria);
    const concursoBase = concurso !== undefined ? parseInt(String(concurso), 10) : undefined;
    const dezenas = validarDezenas(cfg, dezenasBody !== undefined ? parseInt(String(dezenasBody), 10) : undefined);
    const fixosNorm = Array.isArray(fixos) ? fixos.map(Number).filter((n: number) => n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
    const excluidosNorm = Array.isArray(excluidos) ? excluidos.map(Number).filter((n: number) => n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;

    const resultados = await carregarResultados(loteria);
    const resultadosAteBase = concursoBase !== undefined
      ? resultados.filter(r => r.concurso <= concursoBase)
      : resultados;
    const numeros = resultadosAteBase.map(r => r.numeros);
    const cicloDados = await carregarCicloNoConcurso(loteria, concursoBase);

    const estimativa = calcularEstimativaCombinacoes(fixosNorm, excluidosNorm, cfg.total_numeros, dezenas, cfg.numero_minimo);

    const LIMITE_MEMORIA = 500000;
    if (estimativa > LIMITE_MEMORIA) {
      return NextResponse.json(
        { success: false, error: `Total de combinações (${estimativa.toLocaleString('pt-BR')}) excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

    const jogos = gerarJogosDiversificados({
      resultados: numeros,
      cicloDados,
      nJogos: 0,
      seed: seed ? parseInt(String(seed), 10) : undefined,
      fixos: fixosNorm,
      excluidos: excluidosNorm,
      totalNumeros: cfg.total_numeros,
      numerosPorJogo: dezenas,
      numeroMinimo: cfg.numero_minimo,
      primos: cfg.primos,
    });

    const texto = jogos.map(j => j.numeros.join(',')).join('\n');
    const blob = new Blob([texto], { type: 'text/plain; charset=utf-8' });

    return new NextResponse(blob, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Disposition': `attachment; filename="jogos-${loteria}-${dezenas}dezenas-todas-${new Date().toISOString().slice(0, 10)}.txt"`,
      },
    });
  } catch (error) {
    console.error('Erro em /api/jogos-diversos/export POST:', error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : 'Erro desconhecido' },
      { status: 500 }
    );
  }
}
