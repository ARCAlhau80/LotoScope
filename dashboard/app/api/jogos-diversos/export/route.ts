import { NextRequest, NextResponse } from 'next/server';
import { carregarResultados } from '@/lib/database';
import { gerarJogosDiversificados, calcularEstimativaCombinacoes, type JogoGerado, type ColunasPosicionaisConstraint, type FiltroComparativo } from '@/lib/gerador-diversificado';
import { parseColunasPosicionais, parseFiltroComparativo, parseFixosPosicoes, parseExcluidosPosicoes } from '@/lib/colunas-posicionais';
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

interface GerarExportOptions {
  resultados: number[][];
  cicloDados?: Record<number, number>;
  seed?: number;
  fixos?: number[];
  excluidos?: number[];
  totalNumeros: number;
  numerosPorJogo: number;
  numeroMinimo: number;
  primos: number[];
  colunasPosicionais?: ColunasPosicionaisConstraint;
  filtroComparativo?: FiltroComparativo;
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
}

function gerarExportJogos(options: GerarExportOptions, limiteMemoria: number): JogoGerado[] | null {
  const { resultados, cicloDados, seed, fixos, excluidos, totalNumeros, numerosPorJogo, numeroMinimo, primos, colunasPosicionais, filtroComparativo, fixosPosicoes, excluidosPosicoes } = options;
  let jogos = gerarJogosDiversificados({
    resultados,
    cicloDados,
    nJogos: 0,
    seed,
    fixos,
    excluidos,
    totalNumeros,
    numerosPorJogo,
    numeroMinimo,
    primos,
    colunasPosicionais,
    filtroComparativo,
    fixosPosicoes,
    excluidosPosicoes,
  });

  if (jogos.length === 0 && (colunasPosicionais || filtroComparativo || fixosPosicoes || excluidosPosicoes)) {
    const bruta = calcularEstimativaCombinacoes(fixos, excluidos, totalNumeros, numerosPorJogo, numeroMinimo);
    if (bruta > limiteMemoria) return null;
    jogos = gerarJogosDiversificados({
      resultados,
      cicloDados,
      nJogos: 0,
      seed,
      fixos,
      excluidos,
      totalNumeros,
      numerosPorJogo,
      numeroMinimo,
      primos,
      colunasPosicionais: undefined,
      filtroComparativo: undefined,
      fixosPosicoes: undefined,
      excluidosPosicoes: undefined,
    });
  }

  return jogos;
}

function parseParams(searchParams: URLSearchParams) {
  const loteria = searchParams.get('loteria') || 'lotofacil';
  const cfg = getLotteryConfig(loteria);
  const seedParam = searchParams.get('seed');
  const fixosParam = searchParams.get('fixos');
  const excluidosParam = searchParams.get('excluidos');
  const concursoParam = searchParams.get('concurso');
  const dezenasParam = searchParams.get('dezenas');
  const colunasParam = searchParams.get('colunas_posicionais');
  const colunasSetsParam = searchParams.get('colunas_sets');
  const comparativoParam = searchParams.get('comparativo');
  const fixosPosicoesParam = searchParams.get('fixos_posicoes');
  const excluidosPosicoesParam = searchParams.get('excluidos_posicoes');

  const seed = seedParam ? parseInt(seedParam, 10) : undefined;
  const concursoBase = concursoParam ? parseInt(concursoParam, 10) : undefined;
  const dezenasRaw = dezenasParam ? parseInt(dezenasParam, 10) : undefined;
  const dezenas = validarDezenas(cfg, dezenasRaw);
  const fixos = fixosParam ? fixosParam.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
  const excluidos = excluidosParam ? excluidosParam.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
  const colunasPosicionais = parseColunasPosicionais(colunasParam, colunasSetsParam);
  const filtroComparativo = parseFiltroComparativo(comparativoParam);
  const fixosPosicoes = parseFixosPosicoes(fixosPosicoesParam);
  const excluidosPosicoes = parseExcluidosPosicoes(excluidosPosicoesParam);

  return { loteria, seed, concursoBase, fixos, excluidos, dezenas, cfg, colunasPosicionais, filtroComparativo, fixosPosicoes, excluidosPosicoes };
}

export async function GET(request: NextRequest) {
  try {
    const { loteria, seed, concursoBase, fixos, excluidos, dezenas, cfg, colunasPosicionais, filtroComparativo, fixosPosicoes, excluidosPosicoes } = parseParams(new URL(request.url).searchParams);

    const resultados = await carregarResultados(loteria);
    const resultadosAteBase = concursoBase !== undefined
      ? resultados.filter(r => r.concurso <= concursoBase)
      : resultados;
    const numeros = resultadosAteBase.map(r => r.numeros);
    const cicloDados = await carregarCicloNoConcurso(loteria, concursoBase);

    const estimativa = calcularEstimativaCombinacoes(fixos, excluidos, cfg.total_numeros, dezenas, cfg.numero_minimo, colunasPosicionais, filtroComparativo, numeros[numeros.length - 1], fixosPosicoes, excluidosPosicoes);

    const LIMITE_MEMORIA = 500000;
    if (estimativa > LIMITE_MEMORIA) {
      return NextResponse.json(
        { success: false, error: `Total de combinações (${estimativa.toLocaleString('pt-BR')}) excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

    const jogos = gerarExportJogos({
      resultados: numeros,
      cicloDados,
      seed,
      fixos,
      excluidos,
      totalNumeros: cfg.total_numeros,
      numerosPorJogo: dezenas,
      numeroMinimo: cfg.numero_minimo,
      primos: cfg.primos,
      colunasPosicionais,
      filtroComparativo,
      fixosPosicoes,
      excluidosPosicoes,
    }, LIMITE_MEMORIA);

    if (jogos === null) {
      return NextResponse.json(
        { success: false, error: `Nenhum jogo atende aos filtros e o total de combinações sem filtros excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

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
    const { loteria = 'lotofacil', seed, fixos, excluidos, concurso, dezenas: dezenasBody, colunas_posicionais: colunasParam, colunas_sets: colunasSetsParam, comparativo: comparativoParam, fixos_posicoes: fixosPosicoesParam, excluidos_posicoes: excluidosPosicoesParam } = body || {};
    const cfg = getLotteryConfig(loteria);
    const concursoBase = concurso !== undefined ? parseInt(String(concurso), 10) : undefined;
    const dezenas = validarDezenas(cfg, dezenasBody !== undefined ? parseInt(String(dezenasBody), 10) : undefined);
    const fixosNorm = Array.isArray(fixos) ? fixos.map(Number).filter((n: number) => n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
    const excluidosNorm = Array.isArray(excluidos) ? excluidos.map(Number).filter((n: number) => n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
    const colunasPosicionais = parseColunasPosicionais(typeof colunasParam === 'string' ? colunasParam : null, typeof colunasSetsParam === 'string' ? colunasSetsParam : null);
    const filtroComparativo = parseFiltroComparativo(typeof comparativoParam === 'string' ? comparativoParam : null);
    const fixosPosicoes = parseFixosPosicoes(typeof fixosPosicoesParam === 'string' ? fixosPosicoesParam : null);
    const excluidosPosicoes = parseExcluidosPosicoes(typeof excluidosPosicoesParam === 'string' ? excluidosPosicoesParam : null);

    const resultados = await carregarResultados(loteria);
    const resultadosAteBase = concursoBase !== undefined
      ? resultados.filter(r => r.concurso <= concursoBase)
      : resultados;
    const numeros = resultadosAteBase.map(r => r.numeros);
    const cicloDados = await carregarCicloNoConcurso(loteria, concursoBase);

    const estimativa = calcularEstimativaCombinacoes(fixosNorm, excluidosNorm, cfg.total_numeros, dezenas, cfg.numero_minimo, colunasPosicionais, filtroComparativo, numeros[numeros.length - 1], fixosPosicoes, excluidosPosicoes);

    const LIMITE_MEMORIA = 500000;
    if (estimativa > LIMITE_MEMORIA) {
      return NextResponse.json(
        { success: false, error: `Total de combinações (${estimativa.toLocaleString('pt-BR')}) excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

    const jogos = gerarExportJogos({
      resultados: numeros,
      cicloDados,
      seed: seed ? parseInt(String(seed), 10) : undefined,
      fixos: fixosNorm,
      excluidos: excluidosNorm,
      totalNumeros: cfg.total_numeros,
      numerosPorJogo: dezenas,
      numeroMinimo: cfg.numero_minimo,
      primos: cfg.primos,
      colunasPosicionais,
      filtroComparativo,
      fixosPosicoes,
      excluidosPosicoes,
    }, LIMITE_MEMORIA);

    if (jogos === null) {
      return NextResponse.json(
        { success: false, error: `Nenhum jogo atende aos filtros e o total de combinações sem filtros excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

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
