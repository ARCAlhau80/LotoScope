import { NextRequest, NextResponse } from 'next/server';
import { carregarResultados } from '@/lib/database';
import { gerarJogosDiversificados, calcularEstimativaCombinacoes, iterarTodasAsCombinacoes, type JogoGerado, type GeradorDiversificadoOptions, type ColunasPosicionaisConstraint, type FiltroComparativo, type FiltroCategoria, type OrdenacaoJogos } from '@/lib/gerador-diversificado';
import { parseColunasPosicionais, parseDominiosPosicionais, parseFiltroComparativo, parseFiltroCategorias, parseFiltroRepetidos, parseFixosPosicoes, parseExcluidosPosicoes, parseOrdenacao, parseScoreSets } from '@/lib/colunas-posicionais';
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
  dominiosPosicionais?: Array<number[] | null>;
  filtroComparativo?: FiltroComparativo;
  filtroCategorias?: FiltroCategoria[];
  ordenacao?: OrdenacaoJogos;
  scoreSets?: Record<string, number[]>;
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
  estrategias?: string[];
  trevosTotal?: number;
  trevosMin?: number;
  trevosPorJogo?: number;
}

function gerarExportJogos(options: GerarExportOptions, limiteMemoria: number): JogoGerado[] | null {
  const { resultados, cicloDados, seed, fixos, excluidos, totalNumeros, numerosPorJogo, numeroMinimo, primos, colunasPosicionais, dominiosPosicionais, filtroComparativo, filtroCategorias, ordenacao, scoreSets, fixosPosicoes, excluidosPosicoes, estrategias, trevosTotal, trevosMin, trevosPorJogo } = options;
  const temFiltroEstrategias = estrategias && estrategias.length > 0;
  const gerar = (cols?: ColunasPosicionaisConstraint, cmp?: FiltroComparativo, fPos?: Record<number, number[]>, ePos?: Record<number, number[]>, cats?: FiltroCategoria[], doms?: Array<number[] | null>) => gerarJogosDiversificados({
    resultados,
    cicloDados,
    nJogos: temFiltroEstrategias ? 500 : 0,
    seed,
    fixos,
    excluidos,
    totalNumeros,
    numerosPorJogo,
    numeroMinimo,
    primos,
    trevosTotal,
    trevosMin,
    trevosPorJogo,
    colunasPosicionais: cols,
    dominiosPosicionais: doms,
    filtroComparativo: cmp,
    filtroCategorias: cats,
    ordenacao,
    scoreSets,
    fixosPosicoes: fPos,
    excluidosPosicoes: ePos,
    estrategias,
  });
  let jogos = gerar(colunasPosicionais, filtroComparativo, fixosPosicoes, excluidosPosicoes, filtroCategorias, dominiosPosicionais);

  if (jogos.length === 0 && (colunasPosicionais || dominiosPosicionais || filtroComparativo || filtroCategorias || fixosPosicoes || excluidosPosicoes)) {
    const bruta = calcularEstimativaCombinacoes(fixos, excluidos, totalNumeros, numerosPorJogo, numeroMinimo, colunasPosicionais, filtroComparativo, resultados[resultados.length - 1] ?? [], fixosPosicoes, excluidosPosicoes, filtroCategorias, dominiosPosicionais);
    if (bruta > limiteMemoria) return null;
    jogos = gerar(undefined, undefined, undefined, undefined, undefined, dominiosPosicionais);
  }

  return jogos;
}

function filtrarPorEstrategias(jogos: JogoGerado[], estrategias?: string[]): JogoGerado[] {
  if (!estrategias || estrategias.length === 0) return jogos;
  return jogos.filter(j => estrategias.includes(j.estrategia));
}

function formatarJogoLinha(jogo: JogoGerado): string {
  const dezenas = jogo.numeros.join(',');
  if (jogo.trevos && jogo.trevos.length > 0) {
    return `${dezenas}|${jogo.trevos.join(',')}`;
  }
  return dezenas;
}

function headersExport(loteria: string, dezenas: number): HeadersInit {
  return {
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Disposition': `attachment; filename="jogos-${loteria}-${dezenas}dezenas-todas-${new Date().toISOString().slice(0, 10)}.txt"`,
  };
}

function criarStreamExport(options: GeradorDiversificadoOptions): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  const iterator = iterarTodasAsCombinacoes(options);
  let primeiro = true;

  return new ReadableStream<Uint8Array>({
    pull(controller) {
      try {
        let chunk = '';
        for (let i = 0; i < 1000; i++) {
          const proximo = iterator.next();
          if (proximo.done) {
            if (chunk.length > 0) controller.enqueue(encoder.encode(chunk));
            controller.close();
            return;
          }
          chunk += `${primeiro ? '' : '\n'}${formatarJogoLinha(proximo.value)}`;
          primeiro = false;
        }
        controller.enqueue(encoder.encode(chunk));
      } catch (error) {
        controller.error(error);
      }
    },
    cancel() {
      iterator.return(undefined);
    },
  });
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
  const linhasSetsParam = searchParams.get('linhas_sets');
  const comparativoParam = searchParams.get('comparativo');
  const categoriasParam = searchParams.get('categorias');
  const categoriasSetsParam = searchParams.get('categorias_sets');
  const repetidosParam = searchParams.get('repetidos');
  const repetidosSetsParam = searchParams.get('repetidos_sets');
  const fixosPosicoesParam = searchParams.get('fixos_posicoes');
  const excluidosPosicoesParam = searchParams.get('excluidos_posicoes');
  const estrategiasParam = searchParams.get('estrategias');
  const ordenacaoParam = searchParams.get('ordenacao');
  const scoreSetsParam = searchParams.get('score_sets');

  const seed = seedParam ? parseInt(seedParam, 10) : undefined;
  const concursoBase = concursoParam ? parseInt(concursoParam, 10) : undefined;
  const dezenasRaw = dezenasParam ? parseInt(dezenasParam, 10) : undefined;
  const dezenas = validarDezenas(cfg, dezenasRaw);
  const fixos = fixosParam ? fixosParam.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
  const excluidos = excluidosParam ? excluidosParam.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
  const colunasPosicionais = parseColunasPosicionais(colunasParam, colunasSetsParam);
  const dominiosPosicionais = parseDominiosPosicionais(linhasSetsParam);
  const filtroComparativo = parseFiltroComparativo(comparativoParam);
  const filtroCategorias = parseFiltroCategorias(categoriasParam, categoriasSetsParam);
  const filtroRepetidos = parseFiltroRepetidos(repetidosParam, repetidosSetsParam);
  const filtroCategoriasCompleto = [...(filtroCategorias ?? []), ...(filtroRepetidos ?? [])];
  const fixosPosicoes = parseFixosPosicoes(fixosPosicoesParam);
  const excluidosPosicoes = parseExcluidosPosicoes(excluidosPosicoesParam);
  const estrategias = estrategiasParam
    ? estrategiasParam.split(',').map(s => s.trim()).filter(Boolean)
    : undefined;
  const ordenacao = parseOrdenacao(ordenacaoParam);
  const scoreSets = parseScoreSets(scoreSetsParam);

  return { loteria, seed, concursoBase, fixos, excluidos, dezenas, cfg, colunasPosicionais, dominiosPosicionais, filtroComparativo, filtroCategorias: filtroCategoriasCompleto.length > 0 ? filtroCategoriasCompleto : undefined, fixosPosicoes, excluidosPosicoes, estrategias, ordenacao, scoreSets };
}

export async function GET(request: NextRequest) {
  try {
    const { loteria, seed, concursoBase, fixos, excluidos, dezenas, cfg, colunasPosicionais, dominiosPosicionais, filtroComparativo, filtroCategorias, fixosPosicoes, excluidosPosicoes, estrategias, ordenacao, scoreSets } = parseParams(new URL(request.url).searchParams);

    const resultados = await carregarResultados(loteria);
    const resultadosAteBase = concursoBase !== undefined
      ? resultados.filter(r => r.concurso <= concursoBase)
      : resultados;
    const numeros = resultadosAteBase.map(r => r.numeros);
    const cicloDados = await carregarCicloNoConcurso(loteria, concursoBase);

    const estimativa = calcularEstimativaCombinacoes(fixos, excluidos, cfg.total_numeros, dezenas, cfg.numero_minimo, colunasPosicionais, filtroComparativo, numeros[numeros.length - 1], fixosPosicoes, excluidosPosicoes, filtroCategorias, dominiosPosicionais);
    const temFiltroEstrategias = estrategias && estrategias.length > 0;

    const LIMITE_MEMORIA = 500000;
    if (!temFiltroEstrategias && estimativa > LIMITE_MEMORIA) {
      return new NextResponse(criarStreamExport({
        resultados: numeros,
        cicloDados,
        seed,
        fixos,
        excluidos,
        totalNumeros: cfg.total_numeros,
        numerosPorJogo: dezenas,
        numeroMinimo: cfg.numero_minimo,
        primos: cfg.primos,
        trevosTotal: cfg.trevos_total,
        trevosMin: cfg.trevos_min,
        trevosPorJogo: cfg.trevos_cols?.length ?? 0,
        colunasPosicionais,
        dominiosPosicionais,
        filtroComparativo,
        filtroCategorias,
        ordenacao,
        scoreSets,
        fixosPosicoes,
        excluidosPosicoes,
        estrategias,
      }), { headers: headersExport(loteria, dezenas) });
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
      trevosTotal: cfg.trevos_total,
      trevosMin: cfg.trevos_min,
      trevosPorJogo: cfg.trevos_cols?.length ?? 0,
      colunasPosicionais,
      dominiosPosicionais,
      filtroComparativo,
      filtroCategorias,
      ordenacao,
      scoreSets,
      fixosPosicoes,
      excluidosPosicoes,
      estrategias,
    }, LIMITE_MEMORIA);

    if (jogos === null) {
      return NextResponse.json(
        { success: false, error: `Nenhum jogo atende aos filtros e o total de combinações sem filtros excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

    const jogosFiltrados = filtrarPorEstrategias(jogos, estrategias);
    if (estrategias && estrategias.length > 0 && jogosFiltrados.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Nenhum jogo gerado pertence às estratégias selecionadas.' },
        { status: 400 }
      );
    }

    const texto = jogosFiltrados.map(formatarJogoLinha).join('\n');
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
    const { loteria = 'lotofacil', seed, fixos, excluidos, concurso, dezenas: dezenasBody, colunas_posicionais: colunasParam, colunas_sets: colunasSetsParam, linhas_sets: linhasSetsParam, comparativo: comparativoParam, categorias: categoriasParam, categorias_sets: categoriasSetsParam, repetidos: repetidosParam, repetidos_sets: repetidosSetsParam, ordenacao: ordenacaoParam, score_sets: scoreSetsParam, fixos_posicoes: fixosPosicoesParam, excluidos_posicoes: excluidosPosicoesParam, estrategias: estrategiasParam } = body || {};
    const cfg = getLotteryConfig(loteria);
    const concursoBase = concurso !== undefined ? parseInt(String(concurso), 10) : undefined;
    const dezenas = validarDezenas(cfg, dezenasBody !== undefined ? parseInt(String(dezenasBody), 10) : undefined);
    const fixosNorm = Array.isArray(fixos) ? fixos.map(Number).filter((n: number) => n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
    const excluidosNorm = Array.isArray(excluidos) ? excluidos.map(Number).filter((n: number) => n >= cfg.numero_minimo && n <= cfg.numero_maximo) : undefined;
    const colunasPosicionais = parseColunasPosicionais(typeof colunasParam === 'string' ? colunasParam : null, typeof colunasSetsParam === 'string' ? colunasSetsParam : null);
    const dominiosPosicionais = parseDominiosPosicionais(typeof linhasSetsParam === 'string' ? linhasSetsParam : null);
    const filtroComparativo = parseFiltroComparativo(typeof comparativoParam === 'string' ? comparativoParam : null);
    const filtroCategorias = parseFiltroCategorias(typeof categoriasParam === 'string' ? categoriasParam : null, typeof categoriasSetsParam === 'string' ? categoriasSetsParam : null);
    const filtroRepetidos = parseFiltroRepetidos(typeof repetidosParam === 'string' ? repetidosParam : null, typeof repetidosSetsParam === 'string' ? repetidosSetsParam : null);
    const filtroCategoriasCompleto = [...(filtroCategorias ?? []), ...(filtroRepetidos ?? [])];
    const fixosPosicoes = parseFixosPosicoes(typeof fixosPosicoesParam === 'string' ? fixosPosicoesParam : null);
    const excluidosPosicoes = parseExcluidosPosicoes(typeof excluidosPosicoesParam === 'string' ? excluidosPosicoesParam : null);
    const ordenacao = parseOrdenacao(typeof ordenacaoParam === 'string' ? ordenacaoParam : null);
    const scoreSets = parseScoreSets(typeof scoreSetsParam === 'string' ? scoreSetsParam : null);
    const estrategias = Array.isArray(estrategiasParam)
      ? estrategiasParam.map(String).map(s => s.trim()).filter(Boolean)
      : typeof estrategiasParam === 'string'
        ? estrategiasParam.split(',').map(s => s.trim()).filter(Boolean)
        : undefined;

    const resultados = await carregarResultados(loteria);
    const resultadosAteBase = concursoBase !== undefined
      ? resultados.filter(r => r.concurso <= concursoBase)
      : resultados;
    const numeros = resultadosAteBase.map(r => r.numeros);
    const cicloDados = await carregarCicloNoConcurso(loteria, concursoBase);

    const estimativa = calcularEstimativaCombinacoes(fixosNorm, excluidosNorm, cfg.total_numeros, dezenas, cfg.numero_minimo, colunasPosicionais, filtroComparativo, numeros[numeros.length - 1], fixosPosicoes, excluidosPosicoes, filtroCategoriasCompleto.length > 0 ? filtroCategoriasCompleto : undefined, dominiosPosicionais);
    const temFiltroEstrategias = estrategias && estrategias.length > 0;

    const LIMITE_MEMORIA = 500000;
    if (!temFiltroEstrategias && estimativa > LIMITE_MEMORIA) {
      return new NextResponse(criarStreamExport({
        resultados: numeros,
        cicloDados,
        seed: seed ? parseInt(String(seed), 10) : undefined,
        fixos: fixosNorm,
        excluidos: excluidosNorm,
        totalNumeros: cfg.total_numeros,
        numerosPorJogo: dezenas,
        numeroMinimo: cfg.numero_minimo,
        primos: cfg.primos,
        trevosTotal: cfg.trevos_total,
        trevosMin: cfg.trevos_min,
        trevosPorJogo: cfg.trevos_cols?.length ?? 0,
        colunasPosicionais,
        dominiosPosicionais,
        filtroComparativo,
        filtroCategorias: filtroCategoriasCompleto.length > 0 ? filtroCategoriasCompleto : undefined,
        ordenacao,
        scoreSets,
        fixosPosicoes,
        excluidosPosicoes,
        estrategias,
      }), { headers: headersExport(loteria, dezenas) });
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
      trevosTotal: cfg.trevos_total,
      trevosMin: cfg.trevos_min,
      trevosPorJogo: cfg.trevos_cols?.length ?? 0,
      colunasPosicionais,
      dominiosPosicionais,
      filtroComparativo,
      filtroCategorias: filtroCategoriasCompleto.length > 0 ? filtroCategoriasCompleto : undefined,
      ordenacao,
      scoreSets,
      fixosPosicoes,
      excluidosPosicoes,
      estrategias,
    }, LIMITE_MEMORIA);

    if (jogos === null) {
      return NextResponse.json(
        { success: false, error: `Nenhum jogo atende aos filtros e o total de combinações sem filtros excede o limite seguro de ${LIMITE_MEMORIA.toLocaleString('pt-BR')}. Reduza fixos ou remova exclusões.` },
        { status: 400 }
      );
    }

    const jogosFiltrados = filtrarPorEstrategias(jogos, estrategias);
    if (estrategias && estrategias.length > 0 && jogosFiltrados.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Nenhum jogo gerado pertence às estratégias selecionadas.' },
        { status: 400 }
      );
    }

    const texto = jogosFiltrados.map(formatarJogoLinha).join('\n');
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
