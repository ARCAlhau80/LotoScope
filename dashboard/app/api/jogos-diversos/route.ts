import { NextRequest, NextResponse } from 'next/server';
import { carregarResultados } from '@/lib/database';
import { gerarJogosDiversificados, calcularEstatisticasJogos, calcularEstimativaCombinacoes } from '@/lib/gerador-diversificado';
import { contarJogosComDominios } from '@/lib/dominios-posicionais';
import { parseColunasPosicionais, parseDominiosPosicionais, parseFiltroComparativo, parseFiltroCategorias, parseFiltroRepetidos, parseFixosPosicoes, parseExcluidosPosicoes, parseOrdenacao, parseScoreSets } from '@/lib/colunas-posicionais';
import sql from 'mssql';
import { getLotteryConfig, validarDezenas, calcularPrecoAposta } from '@/lib/lottery-config';
import { resolverModoMesSorte, aplicarMesSorteLista } from '@/lib/mes-sorte';

interface CicloRow {
  Ciclo: number;
  Numero: number;
  QtdSorteados: number;
  ConcursoInicio: number;
  ConcursoFechamento: number | null;
}

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
  const nJogosParam = searchParams.get('n');
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
  const mesParam = searchParams.get('mes');

  const nJogos = nJogosParam ? parseInt(nJogosParam, 10) : 5;
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
  const mes = resolverModoMesSorte(cfg, mesParam);

  return { loteria, nJogos, seed, concursoBase, fixos, excluidos, dezenas, cfg, colunasPosicionais, dominiosPosicionais, filtroComparativo, filtroCategorias: filtroCategoriasCompleto.length > 0 ? filtroCategoriasCompleto : undefined, fixosPosicoes, excluidosPosicoes, estrategias, ordenacao, scoreSets, mes };
}

function buildCicloResponse(cicloDados: Record<number, number> | undefined) {
  if (!cicloDados) return null;
  return {
    numero: Object.entries(cicloDados).map(([numero, qtd]) => ({ numero: Number(numero), qtd })),
    faltantes: Object.entries(cicloDados)
      .filter(([, qtd]) => qtd === 0)
      .map(([n]) => Number(n)),
    baixa_frequencia: Object.entries(cicloDados)
      .filter(([, qtd]) => qtd === 1)
      .map(([n]) => Number(n)),
    media_frequencia: Object.values(cicloDados).reduce((a, b) => a + b, 0) / Object.keys(cicloDados).length,
  };
}

/**
 * A geração por rejection pode terminar com 0 jogos quando a grade posicional
 * é contraditória. Em vez de devolver `success: true` com lista vazia, conta
 * exatamente o conjunto viável e explica o conflito.
 */
function respostaSemJogos(args: {
  jogosGerados: number;
  nParaGerar: number;
  totalNumeros: number;
  numerosPorJogo: number;
  numeroMinimo: number;
  fixos?: number[];
  excluidos?: number[];
  dominios?: Array<number[] | null>;
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
}): NextResponse | null {
  if (args.jogosGerados > 0 || args.nParaGerar <= 0) return null;
  const excluidosCompletos = (args.excluidos ?? [])
    .filter(n => !(args.excluidosPosicoes?.[n]?.length));
  const diag = contarJogosComDominios({
    totalNumeros: args.totalNumeros,
    numerosPorJogo: args.numerosPorJogo,
    numeroMinimo: args.numeroMinimo,
    fixos: args.fixos,
    excluidos: excluidosCompletos,
    dominios: args.dominios,
    fixosPosicoes: args.fixosPosicoes,
    excluidosPosicoes: args.excluidosPosicoes,
  });
  return NextResponse.json(
    {
      success: false,
      error: diag.total === 0
        ? diag.detalhe
        : 'Nenhum jogo válido foi gerado com os filtros atuais. Relaxe uma restrição posicional ou reduza os fixos/excluídos.',
      estimativa_total: diag.total,
    },
    { status: 422 },
  );
}

function temRestricaoPosicionalAtiva(
  dominios?: Array<number[] | null>,
  fixosPosicoes?: Record<number, number[]>,
  excluidosPosicoes?: Record<number, number[]>,
): boolean {
  return Boolean(
    (dominios && dominios.some(d => d && d.length > 0))
    || (fixosPosicoes && Object.keys(fixosPosicoes).length > 0)
    || (excluidosPosicoes && Object.keys(excluidosPosicoes).length > 0),
  );
}

export async function GET(request: NextRequest) {
  try {
    const { loteria, nJogos, seed, concursoBase, fixos, excluidos, dezenas, cfg, colunasPosicionais, dominiosPosicionais, filtroComparativo, filtroCategorias, fixosPosicoes, excluidosPosicoes, estrategias, ordenacao, scoreSets, mes } = parseParams(new URL(request.url).searchParams);

    const resultados = await carregarResultados(loteria);
    const resultadosAteBase = concursoBase !== undefined
      ? resultados.filter(r => r.concurso <= concursoBase)
      : resultados;
    const numeros = resultadosAteBase.map(r => r.numeros);
    const cicloDados = await carregarCicloNoConcurso(loteria, concursoBase);

    const estimativa = calcularEstimativaCombinacoes(fixos, excluidos, cfg.total_numeros, dezenas, cfg.numero_minimo, colunasPosicionais, filtroComparativo, numeros[numeros.length - 1], fixosPosicoes, excluidosPosicoes, filtroCategorias, dominiosPosicionais);

    const temFiltroEstrategias = estrategias && estrategias.length > 0;
    const nParaGerar = nJogos === 0 ? (temFiltroEstrategias ? 500 : 50) : nJogos;

    const jogosBase = gerarJogosDiversificados({
      resultados: numeros,
      cicloDados,
      nJogos: nParaGerar,
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
    });
    const semJogos = respostaSemJogos({
      jogosGerados: jogosBase.length,
      nParaGerar,
      totalNumeros: cfg.total_numeros,
      numerosPorJogo: dezenas,
      numeroMinimo: cfg.numero_minimo,
      fixos,
      excluidos,
      dominios: dominiosPosicionais,
      fixosPosicoes,
      excluidosPosicoes,
    });
    if (semJogos) return semJogos;
    const jogos = aplicarMesSorteLista(jogosBase, mes, seed);

    const estatisticas = calcularEstatisticasJogos(jogos, cfg.total_numeros, cfg.numero_minimo);

    return NextResponse.json({
      success: true,
      concurso_base: concursoBase ?? resultadosAteBase[resultadosAteBase.length - 1]?.concurso,
      concurso_alvo: (concursoBase ?? resultadosAteBase[resultadosAteBase.length - 1]?.concurso) + 1,
      jogos,
      estatisticas,
      estimativa_total: temFiltroEstrategias ? null : estimativa,
      modo_todas: nJogos === 0 && !temFiltroEstrategias
        && !temRestricaoPosicionalAtiva(dominiosPosicionais, fixosPosicoes, excluidosPosicoes),
      dezenas,
      preco_unitario: calcularPrecoAposta(loteria, dezenas),
      mes_sorte: mes,
      ciclo_atual: buildCicloResponse(cicloDados),
    });
  } catch (error) {
    console.error('Erro em /api/jogos-diversos:', error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : 'Erro desconhecido' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { loteria = 'lotofacil', n = 5, seed, fixos, excluidos, concurso, dezenas: dezenasBody, mes: mesBody, colunas_posicionais: colunasParam, colunas_sets: colunasSetsParam, linhas_sets: linhasSetsParam, comparativo: comparativoParam, categorias: categoriasParam, categorias_sets: categoriasSetsParam, repetidos: repetidosParam, repetidos_sets: repetidosSetsParam, ordenacao: ordenacaoParam, score_sets: scoreSetsParam, fixos_posicoes: fixosPosicoesParam, excluidos_posicoes: excluidosPosicoesParam, estrategias: estrategiasParam } = body || {};
    const cfg = getLotteryConfig(loteria);
    const mes = resolverModoMesSorte(cfg, mesBody);
    const nJogos = parseInt(String(n), 10) || 5;
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
    const nParaGerar = nJogos === 0 ? (temFiltroEstrategias ? 500 : 50) : nJogos;

    const jogosBase = gerarJogosDiversificados({
      resultados: numeros,
      cicloDados,
      nJogos: nParaGerar,
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
    });
    const semJogos = respostaSemJogos({
      jogosGerados: jogosBase.length,
      nParaGerar,
      totalNumeros: cfg.total_numeros,
      numerosPorJogo: dezenas,
      numeroMinimo: cfg.numero_minimo,
      fixos: fixosNorm,
      excluidos: excluidosNorm,
      dominios: dominiosPosicionais,
      fixosPosicoes,
      excluidosPosicoes,
    });
    if (semJogos) return semJogos;
    const jogos = aplicarMesSorteLista(jogosBase, mes, seed ? parseInt(String(seed), 10) : undefined);

    const estatisticas = calcularEstatisticasJogos(jogos, cfg.total_numeros, cfg.numero_minimo);

    return NextResponse.json({
      success: true,
      concurso_base: concursoBase ?? resultadosAteBase[resultadosAteBase.length - 1]?.concurso,
      concurso_alvo: (concursoBase ?? resultadosAteBase[resultadosAteBase.length - 1]?.concurso) + 1,
      jogos,
      estatisticas,
      estimativa_total: temFiltroEstrategias ? null : estimativa,
      modo_todas: nJogos === 0 && !temFiltroEstrategias
        && !temRestricaoPosicionalAtiva(dominiosPosicionais, fixosPosicoes, excluidosPosicoes),
      dezenas,
      preco_unitario: calcularPrecoAposta(loteria, dezenas),
      mes_sorte: mes,
      ciclo_atual: buildCicloResponse(cicloDados),
    });
  } catch (error) {
    console.error('Erro em /api/jogos-diversos POST:', error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : 'Erro desconhecido' },
      { status: 500 }
    );
  }
}
