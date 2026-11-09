import { NextRequest, NextResponse } from 'next/server';
import {
  gerarFechamentoComRestricoes,
  gerarFechamentoComWheel,
  buscarWheel,
  buscaLocalSimulatedAnnealing,
  verificarCobertura,
  relatorioCusto,
  cacheObter,
  cacheSalvar,
  gerarChaveCache,
  nCombinacoes,
  removerApostasRedundantes,
  apostaSatisfazRepetidas,
  limiteInferiorCobertura,
  backtestFechamento,
  mapearCoverConhecido,
  maxApostasIlimitado,
  permutarCoverParaFiltros,
  completarCobertura,
  apostaSatisfazCategorias,
  type BacktestFechamentoResult,
} from '@/lib/fechamento-combinatorio';
import { getFechamentoConfig, normalizarKt } from '@/lib/fechamento/config';
import { buscarCover } from '@/lib/fechamento/covers';
import { carregarResultados } from '@/lib/database';
import { resolverFechamentoSolver, type CpSatFechamentoResult, type SolverFechamento } from '@/lib/cp-sat';

export const runtime = 'nodejs';
export const maxDuration = 120;

// Fechamento: suporta garantia condicional aos fixos, cover conhecido
// permutado para filtros de categoria e reparo de cobertura pós-filtros.

function parseNumero(valor: unknown, padrao: number): number {
  if (valor === null || valor === undefined || valor === "") return padrao;
  const n = typeof valor === "number" ? valor : parseInt(String(valor), 10);
  return Number.isNaN(n) ? padrao : n;
}

function parseBoolean(valor: unknown, padrao: boolean): boolean {
  if (valor === null || valor === undefined) return padrao;
  if (typeof valor === "boolean") return valor;
  if (typeof valor === "number") return valor !== 0;
  const s = String(valor).toLowerCase();
  return s === "true" || s === "1";
}

function parseNumerosArray(valor: string | null): number[] {
  if (!valor) return [];
  return valor
    .split(",")
    .map((x) => parseInt(x.trim(), 10))
    .filter((n) => !Number.isNaN(n) && n > 0);
}

function parseUniverso(valor: string | null): number[] | undefined {
  if (!valor) return undefined;
  return parseNumerosArray(valor);
}

function parseFiltrosCategorias(valor: any): { numeros: number[]; min: number; max: number }[] {
  if (!valor) return [];
  try {
    const arr = Array.isArray(valor) ? valor : JSON.parse(valor);
    return arr
      .filter((f: any) => f && Array.isArray(f.numeros) && Number.isInteger(f.min) && Number.isInteger(f.max))
      .map((f: any) => ({
        numeros: f.numeros.filter((n: number) => Number.isInteger(n) && n > 0),
        min: f.min,
        max: f.max,
      }));
  } catch {
    return [];
  }
}

function montarOpcoesDoQuery(searchParams: URLSearchParams) {
  const universo = parseUniverso(searchParams.get("universo"));
  const fixos = parseNumerosArray(searchParams.get("fixos"));
  const excluidos = parseNumerosArray(searchParams.get("excluidos"));
  const k = parseNumero(searchParams.get("k"), 15);
  const t = parseNumero(searchParams.get("t"), 11);
  const maxApostas = parseNumero(searchParams.get("maxApostas"), 200);
  const seed = parseNumero(searchParams.get("seed"), 7);
  const otimizado = parseBoolean(searchParams.get("otimizado"), true);
  const candidatosPool = parseNumero(searchParams.get("candidatosPool"), 400);
  const amostraPorPasso = parseNumero(searchParams.get("amostraPorPasso"), t <= 3 ? 2000 : t === 4 ? 500 : t <= 8 ? 60 : 25);
  const maxIteracoes = parseNumero(searchParams.get("maxIteracoes"), 40);
  const buscaSeed = parseNumero(searchParams.get("buscaSeed"), seed + 1);
  const usarWheel = parseBoolean(searchParams.get("usarWheel"), true);
  const usarSimulatedAnnealing = parseBoolean(searchParams.get("usarSimulatedAnnealing"), false);
  const usarCache = parseBoolean(searchParams.get("usarCache"), true);
  return { universo, fixos, excluidos, k, t, maxApostas, seed, otimizado, candidatosPool, amostraPorPasso, maxIteracoes, buscaSeed, usarWheel, usarSimulatedAnnealing, usarCache };
}

function montarResposta(opts: any, apostas: number[][], cobertura: any, custo: any, modo: string, wheelUsado: boolean) {
  const universoEfetivo = opts.universo ?? Array.from({ length: 25 }, (_, i) => i + 1);
  return {
    sucesso: true,
    universo: universoEfetivo,
    fixos: opts.fixos,
    excluidos: opts.excluidos,
    k: opts.k,
    t: opts.t,
    modo,
    wheelUsado,
    totalApostas: apostas.length,
    apostas,
    cobertura,
    custo,
  };
}

interface FiltroRepetidas {
  numeros: number[];
  min: number;
  max: number;
}

function parseFiltroRepetidas(valor: any, maxPermitido: number = 15): FiltroRepetidas | null {
  if (!valor || !Array.isArray(valor.numeros) || valor.numeros.length === 0) return null;
  const numeros = valor.numeros
    .map((n: any) => parseInt(String(n), 10))
    .filter((n: number) => Number.isInteger(n) && n > 0);
  if (!numeros.length) return null;
  const min = parseNumero(valor.min, 0);
  const max = parseNumero(valor.max, maxPermitido);
  return {
    numeros,
    min: Math.max(0, Math.min(min, max)),
    max: Math.min(maxPermitido, Math.max(min, max)),
  };
}

function aplicarFiltroRepetidas(apostas: number[][], filtro: FiltroRepetidas | null): number[][] {
  if (!filtro) return apostas;
  return apostas.filter(a => apostaSatisfazRepetidas(a, filtro.numeros, filtro.min, filtro.max));
}

function calcularCoberturaRestante(
  apostas: number[][],
  universo: number[],
  fixos: number[],
  excluidos: number[],
  k: number,
  t: number,
) {
  const universoRestante = universo.filter(n => !fixos.includes(n) && !excluidos.includes(n));
  const kRestante = k - fixos.length;
  if (kRestante < t || universoRestante.length < t) return null;
  const apostasLivres = apostas.map(a => a.filter(n => !fixos.includes(n) && !excluidos.includes(n)));
  return verificarCobertura(apostasLivres, universoRestante, kRestante, t);
}

function calcularLimiteInferior(
  loteria: string,
  universo: number[],
  fixos: number[],
  excluidos: number[],
  k: number,
  t: number,
): number {
  const universoRestante = universo.filter(n => !fixos.includes(n) && !excluidos.includes(n));
  const kRestante = k - fixos.length;
  if (kRestante <= 0 || universoRestante.length < kRestante) return 0;
  const conhecido = buscarCover(loteria, universoRestante.length, kRestante, t);
  if (conhecido) return conhecido.limiteInferior;
  return limiteInferiorCobertura(universoRestante.length, kRestante, t);
}

function montarRespostaFinal(args: {
  loteria: string;
  universo: number[];
  fixos: number[];
  excluidos: number[];
  filtrosCategorias: any[];
  k: number;
  t: number;
  /** Quando true, a garantia vale apenas se todos os fixos forem sorteados. */
  garantiaCondicional?: boolean;
  /** t reduzido usado na geração (t - fixos.length quando condicional). */
  tEfetivo?: number;
  modo: string;
  wheelUsado: boolean;
  apostas: number[][];
  cobertura: any;
  coberturaRestante: any;
  limiteInferior: number;
  custo: any;
  seedUsado: number;
  seeds: number;
  filtroRepetidas: FiltroRepetidas | null;
  removidasRepetidas: number;
  aviso?: string;
  backtest?: BacktestFechamentoResult | null;
  tempoGeracaoMs?: number;
  cpSat?: (CpSatFechamentoResult & { usado: boolean }) | null;
  coverConhecido?: { v: number; k: number; t: number; blocos: number; fonte: string; limiteInferior?: number; verificado?: boolean } | null;
}) {
  return {
    sucesso: true,
    universo: args.universo,
    loteria: args.loteria,
    fixos: args.fixos,
    excluidos: args.excluidos,
    filtrosCategorias: args.filtrosCategorias,
    k: args.k,
    t: args.t,
    garantiaCondicional: args.garantiaCondicional ?? false,
    tEfetivo: args.tEfetivo ?? args.t,
    modo: args.modo,
    wheelUsado: args.wheelUsado,
    totalApostas: args.apostas.length,
    apostas: args.apostas,
    cobertura: args.cobertura,
    coberturaRestante: args.coberturaRestante,
    limiteInferior: args.limiteInferior,
    eficiencia: args.limiteInferior > 0 ? args.apostas.length / args.limiteInferior : null,
    custo: args.custo,
    seedUsado: args.seedUsado,
    seedsTestadas: args.seeds,
    filtroRepetidas: args.filtroRepetidas
      ? { min: args.filtroRepetidas.min, max: args.filtroRepetidas.max, removidas: args.removidasRepetidas }
      : null,
    aviso: args.aviso ?? null,
    backtest: args.backtest ?? null,
    tempoGeracaoMs: args.tempoGeracaoMs ?? null,
    cpSat: args.cpSat ?? null,
    coverConhecido: args.coverConhecido ?? null,
  };
}

export async function GET(request: NextRequest) {
  try {
    const { universo, fixos, excluidos, k, t, maxApostas, seed, otimizado, candidatosPool, amostraPorPasso, maxIteracoes, buscaSeed, usarWheel, usarSimulatedAnnealing, usarCache } =
      montarOpcoesDoQuery(new URL(request.url).searchParams);

    const universoEfetivo = universo ?? Array.from({ length: 25 }, (_, i) => i + 1);
    const chaveCache = usarCache ? gerarChaveCache({ v: universoEfetivo.length, k, t, maxApostas, seed, otimizado, fixos, excluidos }) : null;
    if (chaveCache) {
      const cacheado = cacheObter(chaveCache);
      if (cacheado) {
        return NextResponse.json({
          sucesso: true,
          universo: universoEfetivo,
          fixos,
          excluidos,
          k,
          t,
          modo: 'cache',
          wheelUsado: false,
          totalApostas: cacheado.apostas.length,
          apostas: cacheado.apostas,
          cobertura: cacheado.cobertura,
          custo: relatorioCusto(cacheado.apostas, k),
        });
      }
    }

    let apostas: number[][] = [];
    let modo = '';
    let wheelUsado = false;

    if (usarWheel && !fixos.length && !excluidos.length) {
      const wheelResult = gerarFechamentoComWheel(universoEfetivo.length, k, t, maxApostas, seed);
      apostas = wheelResult.apostas;
      modo = wheelResult.modo;
      wheelUsado = wheelResult.wheelUsado;
    }

    if (!apostas.length) {
      const gerados = gerarFechamentoComRestricoes({
        universo: universoEfetivo,
        fixos,
        excluidos,
        filtrosCategorias: [],
        k, t, maxApostas, seed, otimizado, maxIteracoes, buscaSeed, candidatosPool, amostraPorPasso,
      });
      apostas = gerados;
      modo = otimizado ? 'guloso_amostrado + busca_local' : 'guloso_amostrado';
    }

    if (usarSimulatedAnnealing && apostas.length > 1) {
      apostas = buscaLocalSimulatedAnnealing({
        apostas, universo: universoEfetivo, k, t,
        maxIteracoes: 500,
        temperaturaInicial: 10,
        taxaResfriamento: 0.995,
        candidatosPool: 400,
        seed: seed + 1,
      });
      modo += ' + simulated_annealing';
    }

    const cobertura = verificarCobertura(apostas, universoEfetivo, k, t);
    const custo = relatorioCusto(apostas, k);

    if (chaveCache) {
      cacheSalvar(chaveCache, { parametros: { v: universoEfetivo.length, k, t, maxApostas, seed, otimizado }, apostas, cobertura, geradoEm: new Date().toISOString() });
    }

    return NextResponse.json({
      sucesso: true,
      universo: universoEfetivo,
      fixos,
      excluidos,
      k,
      t,
      modo,
      wheelUsado,
      totalApostas: apostas.length,
      apostas,
      cobertura,
      custo,
    });
  } catch (error: any) {
    return NextResponse.json({ sucesso: false, error: error?.message || "Erro desconhecido" }, { status: 400 });
  }
}

export async function POST(request: NextRequest) {
  const inicioRequisicao = Date.now();
  try {
    const body = (await request.json()) as any;
    const universo = Array.isArray(body.universo)
      ? body.universo.map((n: any) => Number(n)).filter((n: number) => Number.isInteger(n) && n > 0)
      : undefined;
    const fixos = Array.isArray(body.fixos)
      ? [...new Set<number>(body.fixos.map((n: any) => Number(n)).filter((n: number) => Number.isInteger(n) && n > 0))]
      : [];
    const excluidos = Array.isArray(body.excluidos)
      ? [...new Set<number>(body.excluidos.map((n: any) => Number(n)).filter((n: number) => Number.isInteger(n) && n > 0))]
      : [];
    const loteria = typeof body.loteria === 'string' && body.loteria ? body.loteria : 'lotofacil';
    const fcfg = getFechamentoConfig(loteria);
    const filtrosCategorias = parseFiltrosCategorias(body.filtrosCategorias);
    const kSolicitado = parseNumero(body.k, fcfg.kPadrao);
    const tSolicitado = parseNumero(body.t, fcfg.tPadrao);
    const { k, t } = normalizarKt(fcfg, kSolicitado, tSolicitado);
    const garantiaCondicional = parseBoolean(body.garantiaCondicional, false) && fixos.length > 0;
    // Condicional: "t acertos SE os f fixos saírem" => reduz o alvo para t-f.
    // Se f >= t, os próprios fixos já garantem t; usamos tEfetivo=1 como piso.
    const tEfetivo = garantiaCondicional ? Math.max(1, t - fixos.length) : t;
    const filtroRepetidas = parseFiltroRepetidas(body.repetidas, fcfg.dezenasPorAposta);
    const maxApostas = parseNumero(body.maxApostas, 200);
    const seed = parseNumero(body.seed, 7);
    const otimizado = body.otimizado !== false;
    const candidatosPool = parseNumero(body.candidatosPool, 400);
    const amostraPorPasso = parseNumero(body.amostraPorPasso, tEfetivo <= 3 ? 2000 : tEfetivo === 4 ? 500 : tEfetivo <= 8 ? 60 : 25);
    const maxIteracoes = parseNumero(body.maxIteracoes, 40);
    const buscaSeed = parseNumero(body.buscaSeed, 7 + 1);
    const usarWheel = parseBoolean(body.usarWheel, true);
    const usarSimulatedAnnealing = parseBoolean(body.usarSimulatedAnnealing, false);
    const usarCache = parseBoolean(body.usarCache, true);
    const removerRedundantes = parseBoolean(body.removerRedundantes, true);
    const priorizarPremios = parseBoolean(body.priorizarPremios, false);
    const usarCpSat = parseBoolean(body.usarCpSat, false);
    const solverBody = String(body.solver ?? 'cp_sat').toLowerCase();
    const solver: SolverFechamento = solverBody === 'scip' ? 'SCIP' : solverBody === 'cbc' ? 'CBC' : 'cp_sat';
    const cpSatTimeLimit = Math.max(1, Math.min(60, parseNumero(body.cpSatTimeLimit, 10)));
    const incluirBacktest = parseBoolean(body.incluirBacktest, false);
    const limiteTempoMs = Math.max(0, parseNumero(body.limiteTempoMs, 120_000));
    const seedsSolicitadas = Math.max(1, Math.min(10, parseNumero(body.buscarMelhorSeed, 1)));
    // "Priorizar prêmios" só faz sentido comparando pelo menos 2 seeds.
    const seedsBase = priorizarPremios ? Math.max(2, seedsSolicitadas) : seedsSolicitadas;
    // Com "0 = todas" a geração já é pesada; limita a busca de seeds.
    const seeds = maxApostas === 0 ? Math.min(seedsBase, 5) : seedsBase;
    const limitePorSeed = seeds > 1 && limiteTempoMs > 0
      ? Math.max(15_000, Math.floor(limiteTempoMs / seeds))
      : limiteTempoMs;

    const universoEfetivo = universo?.length ? universo : Array.from({ length: fcfg.totalNumeros }, (_, i) => i + 1);
    const universoCobertura: number[] = universoEfetivo.filter((n: number) => !excluidos.includes(n));
    const universoRestante = universoEfetivo.filter((n: number) => !fixos.includes(n) && !excluidos.includes(n));
    const precisaHistorico = (priorizarPremios && seeds > 1) || incluirBacktest;
    let resultadosHistoricos: Awaited<ReturnType<typeof carregarResultados>> | null = null;
    let avisoHistorico: string | null = null;
    if (precisaHistorico) {
      try {
        resultadosHistoricos = await carregarResultados(loteria);
        if (!resultadosHistoricos.length) {
          resultadosHistoricos = null;
          avisoHistorico = 'Não há resultados históricos para o backtest.';
        }
      } catch {
        avisoHistorico = 'Não foi possível carregar o histórico para o backtest.';
      }
    }

    // Cache só quando não há backtest/multi-seed/filtro de repetidas/condicional.
    const podeCache = usarCache && !incluirBacktest && !priorizarPremios && seeds === 1 && !filtroRepetidas && !garantiaCondicional && !filtrosCategorias.length;
    const chaveCache = podeCache
      ? `${loteria}_${gerarChaveCache({ v: universoEfetivo.length, k, t: tEfetivo, maxApostas, seed, otimizado, fixos, excluidos })}_r${removerRedundantes ? 1 : 0}`
      : null;

    if (chaveCache) {
      const cacheado = cacheObter(chaveCache);
      if (cacheado) {
        const coberturaRestante = calcularCoberturaRestante(cacheado.apostas, universoEfetivo, fixos, excluidos, k, tEfetivo);
        return NextResponse.json(montarRespostaFinal({
          loteria,
          universo: universoEfetivo,
          fixos,
          excluidos,
          filtrosCategorias,
          k,
          t,
          garantiaCondicional,
          tEfetivo,
          modo: 'cache',
          wheelUsado: false,
          apostas: cacheado.apostas,
          cobertura: garantiaCondicional ? coberturaRestante ?? cacheado.cobertura : cacheado.cobertura,
          coberturaRestante,
          limiteInferior: calcularLimiteInferior(loteria, universoEfetivo, fixos, excluidos, k, tEfetivo),
          custo: relatorioCusto(cacheado.apostas, k, fcfg.dezenasPorAposta, fcfg.precoBase),
          seedUsado: seed,
          seeds: 1,
          filtroRepetidas: null,
          removidasRepetidas: 0,
          tempoGeracaoMs: Date.now() - inicioRequisicao,
        }));
      }
    }

    // Wheel pré-computado é determinístico; não faz sentido testar várias seeds.
    let wheelApostas: number[][] | null = null;
    let modoWheel = '';
    if (usarWheel && !fixos.length && !excluidos.length && !filtrosCategorias.length && !filtroRepetidas) {
      const wheel = buscarWheel(universoEfetivo.length, k, tEfetivo);
      if (wheel && (maxApostasIlimitado(maxApostas) || wheel.apostas.length <= maxApostas)) {
        wheelApostas = wheel.apostas;
        modoWheel = 'wheel_pre_computado';
      }
    }

    // Coberturas ótimas conhecidas (La Jolla). Com filtros de categoria, ainda
    // tentamos o cover: permutando os rótulos, muitas vezes ele satisfaz os
    // filtros sem custar nenhuma aposta extra.
    let coverApostas: number[][] | null = null;
    let coverInfo: { v: number; k: number; t: number; blocos: number; fonte: string; limiteInferior: number; verificado: boolean; permutado?: boolean } | null = null;
    let coverIgnorado: { v: number; k: number; t: number; blocos: number } | null = null;
    {
      const universoRestanteCover: number[] = universoEfetivo.filter((n: number) => !fixos.includes(n) && !excluidos.includes(n));
      const kRestanteCover = k - fixos.length;
      const cover = buscarCover(loteria, universoRestanteCover.length, kRestanteCover, tEfetivo);
      const cabeNoMax = cover ? (maxApostasIlimitado(maxApostas) || maxApostas >= cover.blocos.length) : false;
      if (cover && cabeNoMax) {
        if (!filtrosCategorias.length) {
          const blocos = mapearCoverConhecido(cover, universoRestanteCover);
          coverApostas = blocos.map(b => [...fixos, ...b].sort((a, b) => a - b));
          coverInfo = { v: cover.v, k: cover.k, t: cover.t, blocos: cover.blocos.length, fonte: cover.fonte, limiteInferior: cover.limiteInferior, verificado: cover.verificado ?? false };
        } else {
          const perm = permutarCoverParaFiltros({
            blocos: cover.blocos,
            universo: universoRestanteCover,
            fixos,
            filtros: filtrosCategorias,
            seed,
            limiteTempoMs: 1000,
          });
          if (perm && perm.violacoes === 0) {
            coverApostas = perm.apostas;
            coverInfo = {
              v: cover.v,
              k: cover.k,
              t: cover.t,
              blocos: cover.blocos.length,
              fonte: cover.fonte,
              limiteInferior: cover.limiteInferior,
              verificado: cover.verificado ?? false,
              permutado: true,
            };
          } else if (perm) {
            // Nem toda permutação satisfaz o filtro. Aproveita os blocos válidos
            // do cover e completa a cobertura adicionando só blocos permitidos.
            // Só vale a pena se o reparo não inflar demais o número de apostas.
            const validas = perm.apostas.filter(a => apostaSatisfazCategorias(a, filtrosCategorias));
            if (validas.length > 0) {
              const livres = validas.map(a => a.filter(n => !fixos.includes(n) && !excluidos.includes(n)));
              const reparado = completarCobertura({
                apostas: livres,
                universo: universoRestante,
                k: k - fixos.length,
                t: tEfetivo,
                maxApostas: maxApostasIlimitado(maxApostas) ? 0 : maxApostas,
                seed,
                candidatosPool: 5000,
                aceitarBloco: (a) => apostaSatisfazCategorias([...fixos, ...a], filtrosCategorias),
                limiteTempoMs: 3000,
              });
              const cabeSemInflar = reparado.length > 0 && reparado.length <= Math.ceil(cover.blocos.length * 1.5);
              if (cabeSemInflar) {
                const completa = reparado.map(a => [...fixos, ...a].sort((x, y) => x - y));
                const cob = calcularCoberturaRestante(completa, universoEfetivo, fixos, excluidos, k, tEfetivo);
                if (cob?.coberta) {
                  coverApostas = completa;
                  coverInfo = {
                    v: cover.v,
                    k: cover.k,
                    t: cover.t,
                    blocos: completa.length,
                    fonte: `${cover.fonte} (parcial + reparo)`,
                    limiteInferior: cover.limiteInferior,
                    verificado: false,
                    permutado: true,
                  };
                }
              }
            }
          }
        }
      } else if (cover) {
        coverIgnorado = { v: cover.v, k: cover.k, t: cover.t, blocos: cover.blocos.length };
      }
    }

    const seedsEfetivas = (wheelApostas || coverApostas) ? 1 : seeds;
    // Cover verificado e sem filtros: a remoção de redundantes e a verificação
    // exaustiva são desnecessárias (e caras para t=11/12).
    const usaCoverVerificado = coverInfo?.verificado === true && fixos.length === 0 && excluidos.length === 0 && !filtroRepetidas;
    let melhor: {
      apostas: number[][];
      apostasBrutas: number[][];
      seed: number;
      cobertura: ReturnType<typeof verificarCobertura>;
      coberturaRestante: ReturnType<typeof verificarCobertura> | null;
      custo: ReturnType<typeof relatorioCusto>;
      backtest: BacktestFechamentoResult | null;
    } | null = null;

    for (let i = 0; i < seedsEfetivas; i++) {
      const seedAtual = seed + i;
      const buscaSeedAtual = buscaSeed + i;

      let apostasBrutas: number[][];
      if (wheelApostas) {
        apostasBrutas = wheelApostas.map(a => [...a]);
      } else if (coverApostas) {
        apostasBrutas = coverApostas.map(a => [...a]);
      } else {
        apostasBrutas = gerarFechamentoComRestricoes({
          universo: universoEfetivo,
          fixos,
          excluidos,
          filtrosCategorias,
          k, t: tEfetivo, maxApostas,
          seed: seedAtual,
          otimizado,
          maxIteracoes,
          buscaSeed: buscaSeedAtual,
          candidatosPool,
          amostraPorPasso,
          removerRedundantes: false,
          limiteTempoMs: limitePorSeed,
        });
      }

      let candidato = aplicarFiltroRepetidas(apostasBrutas, filtroRepetidas);
      if (removerRedundantes && candidato.length > 1 && !usaCoverVerificado) {
        candidato = removerApostasRedundantes(candidato, universoEfetivo, k, tEfetivo);
      }

      if (!candidato.length) continue;

      // Cover já verificado offline: evita reenumerar C(25,t) no request
      // (t=11/12 têm milhares de apostas e a verificação custaria segundos).
      const custo = relatorioCusto(candidato, k, fcfg.dezenasPorAposta, fcfg.precoBase);
      const coberturaFull = usaCoverVerificado
        ? {
            coberta: true,
            tSubsetsTotal: nCombinacoes(universoCobertura.length, tEfetivo),
            tSubsetsCobertos: nCombinacoes(universoCobertura.length, tEfetivo),
            garantiaPercentual: 100,
            apostasValidas: candidato.length,
            apostasInvalidas: 0,
            totalApostas: candidato.length,
            custoEstimado: custo.custoTotal,
          }
        : garantiaCondicional
          ? null
          : verificarCobertura(candidato, universoCobertura, k, tEfetivo, fcfg.dezenasPorAposta, fcfg.precoBase);
      // Sem fixos/excluídos, a cobertura do restante é idêntica à cobertura plena.
      const coberturaRestante = fixos.length === 0 && excluidos.length === 0
        ? coberturaFull
        : calcularCoberturaRestante(candidato, universoEfetivo, fixos, excluidos, k, tEfetivo);
      // Na garantia condicional, a métrica válida é a do universo restante
      // (t-f subconjuntos cobertos por apostas de k-f dezenas).
      const cobertura = (garantiaCondicional ? coberturaRestante : coberturaFull) ?? coberturaRestante ?? coberturaFull!;
      const backtest = priorizarPremios && resultadosHistoricos
        ? backtestFechamento({
            apostas: candidato,
            resultados: resultadosHistoricos,
            k,
            faixasPremio: fcfg.faixasPremio,
            premios: fcfg.premios,
            dezenasBase: fcfg.dezenasPorAposta,
            precoBase: fcfg.precoBase,
          })
        : null;

      const candidatoInfo = { apostas: candidato, apostasBrutas, seed: seedAtual, cobertura, coberturaRestante, custo, backtest };

      if (!melhor) {
        melhor = candidatoInfo;
        continue;
      }

      const coberturaA = coberturaRestante?.garantiaPercentual ?? cobertura.garantiaPercentual;
      const coberturaB = melhor.coberturaRestante?.garantiaPercentual ?? melhor.cobertura.garantiaPercentual;
      let melhorCandidato = false;
      if (coberturaA > coberturaB + 1e-9) {
        melhorCandidato = true;
      } else if (Math.abs(coberturaA - coberturaB) <= 1e-9) {
        if (priorizarPremios && backtest && melhor.backtest) {
          const lucroA = backtest.premioMedio - backtest.custoTotal;
          const lucroB = melhor.backtest.premioMedio - melhor.backtest.custoTotal;
          if (Math.abs(lucroA - lucroB) > 1e-9) melhorCandidato = lucroA > lucroB;
          else melhorCandidato = candidato.length < melhor.apostas.length;
        } else {
          melhorCandidato = candidato.length < melhor.apostas.length;
        }
      }
      if (melhorCandidato) melhor = candidatoInfo;
    }
    if (!melhor) {
      throw new Error('Não foi possível gerar apostas com os filtros informados. Reduza as restrições.');
    }

    // CP-SAT: tenta reduzir o número de apostas a partir da solução heurística.
    // Roda sobre o universo restante (sem fixos/excluídos) e só substitui se
    // devolver uma solução válida com MENOS apostas e cobertura de 100%.
    let apostasBrutasFinal = melhor.apostasBrutas;
    let cpSatInfo: (CpSatFechamentoResult & { usado: boolean }) | null = null;
    if (usarCpSat && !wheelApostas && !coverApostas && tEfetivo <= 5) {
      const fixosSet = new Set<number>(fixos);
      const excluidosSet = new Set<number>(excluidos);
      const universoRestante: number[] = universoEfetivo.filter((n: number) => !fixosSet.has(n) && !excluidosSet.has(n));
      const kRestante = k - fixos.length;
      const totalAlvosSolver = nCombinacoes(universoRestante.length, tEfetivo);
      const extras = apostasBrutasFinal
        .map(a => a.filter(n => !fixosSet.has(n) && !excluidosSet.has(n)))
        .filter(a => a.length === kRestante);
      if (totalAlvosSolver <= 200_000 && kRestante >= tEfetivo && universoRestante.length >= kRestante && extras.length > 1) {
        const pool = tEfetivo <= 3 ? Math.max(500, extras.length + 200) : tEfetivo === 4 ? 400 : 300;
        const cp = await resolverFechamentoSolver({
          universo: universoRestante,
          k: kRestante,
          t: tEfetivo,
          extras,
          seed,
          pool,
          timeLimit: cpSatTimeLimit,
          threads: 4,
          maxApostas: maxApostas > 0 ? maxApostas : 0,
          upperBound: extras.length - 1,
          solver,
        });
        if (cp) {
          let usado = false;
          if (cp.bets.length > 0 && cp.bets.length < apostasBrutasFinal.length) {
            const apostasCp = cp.bets.map(b => [...fixos, ...b].sort((a, b) => a - b));
            const betsValidas = cp.bets.every(b =>
              b.length === kRestante
              && new Set(b).size === kRestante
              && b.every(n => universoRestante.includes(n))
            );
            const coberturaCp = verificarCobertura(apostasCp, universoCobertura, k, tEfetivo);
            if (betsValidas && coberturaCp.coberta) {
              apostasBrutasFinal = apostasCp;
              usado = true;
            }
          }
          cpSatInfo = { ...cp, usado };
        }
      }
    }

    let apostas = aplicarFiltroRepetidas(apostasBrutasFinal, filtroRepetidas);
    const removidasRepetidas = apostasBrutasFinal.length - apostas.length;
    let modoReparo = false;
    let reparoAdicionadas = 0;
    if (removerRedundantes && apostas.length > 1) {
      apostas = removerApostasRedundantes(apostas, universoEfetivo, k, tEfetivo);
    }

    // Reparo: filtros pós-geração (repetidas/categorias) podem remover apostas.
    // Completamos a cobertura com blocos que ainda satisfaçam todos os filtros.
    if (
      !usaCoverVerificado
      && apostas.length
      && tEfetivo <= 10
      && (removidasRepetidas > 0 || filtrosCategorias.length > 0)
    ) {
      const aceitarReparo = (a: number[]) => {
        if (filtroRepetidas && !apostaSatisfazRepetidas(a, filtroRepetidas.numeros, filtroRepetidas.min, filtroRepetidas.max)) return false;
        if (filtrosCategorias.length && !apostaSatisfazCategorias(a, filtrosCategorias)) return false;
        return true;
      };
      const livres = apostas.map(a => a.filter(n => !fixos.includes(n) && !excluidos.includes(n)));
      const reparado = completarCobertura({
        apostas: livres,
        universo: universoRestante,
        k: k - fixos.length,
        t: tEfetivo,
        maxApostas: maxApostasIlimitado(maxApostas) ? 0 : Math.max(maxApostas, apostas.length),
        seed,
        aceitarBloco: (a) => aceitarReparo([...fixos, ...a]),
        limiteTempoMs: Math.max(1000, Math.min(5000, limitePorSeed)),
      });
      if (reparado.length > apostas.length) {
        const antes = apostas.length;
        apostas = reparado.map(a => [...fixos, ...a].sort((a, b) => a - b));
        modoReparo = true;
        reparoAdicionadas = apostas.length - antes;
      }
    }
    if (!apostas.length) {
      throw new Error('Nenhuma aposta sobrou após os filtros. Reduza as restrições.');
    }

    let modo = coverApostas
      ? 'cover_conhecido'
      : wheelApostas
        ? modoWheel
        : (otimizado ? 'guloso_amostrado + busca_local' : 'guloso_amostrado');
    if (removerRedundantes) modo += ' + remocao_redundantes';
    if (!wheelApostas && seedsEfetivas > 1) modo += ' + multi_seed';
    if (filtroRepetidas) modo += ' + filtro_repetidas';
    if (cpSatInfo?.usado) modo += ' + cp_sat';
    if (modoReparo) modo += ' + reparo_cobertura';
    if (garantiaCondicional) modo += ' + garantia_condicional';

    if (usarSimulatedAnnealing && apostas.length > 1) {
      apostas = buscaLocalSimulatedAnnealing({
        apostas, universo: universoEfetivo, k, t: tEfetivo,
        maxIteracoes: 500,
        temperaturaInicial: 10,
        taxaResfriamento: 0.995,
        candidatosPool: 400,
        seed: buscaSeed,
        aceitarBloco: filtrosCategorias.length
          ? (a) => apostaSatisfazCategorias(a, filtrosCategorias)
          : undefined,
      });
      modo += ' + simulated_annealing';
    }

    const coberturaFull = verificarCobertura(apostas, universoCobertura, k, tEfetivo, fcfg.dezenasPorAposta, fcfg.precoBase);
    const coberturaRestante = calcularCoberturaRestante(apostas, universoEfetivo, fixos, excluidos, k, tEfetivo);
    const cobertura = garantiaCondicional ? (coberturaRestante ?? coberturaFull) : coberturaFull;
    const custo = relatorioCusto(apostas, k, fcfg.dezenasPorAposta, fcfg.precoBase);
    const limiteInferior = calcularLimiteInferior(loteria, universoEfetivo, fixos, excluidos, k, tEfetivo);

    let backtestFinal: BacktestFechamentoResult | null = null;
    if (resultadosHistoricos && (incluirBacktest || priorizarPremios)) {
      backtestFinal = backtestFechamento({
        apostas,
        resultados: resultadosHistoricos,
        k,
        faixasPremio: fcfg.faixasPremio,
        premios: fcfg.premios,
        dezenasBase: fcfg.dezenasPorAposta,
        precoBase: fcfg.precoBase,
      });
    }

    const avisos: string[] = [];
    if (avisoHistorico) avisos.push(avisoHistorico);
    if (garantiaCondicional) {
      avisos.push(`Garantia CONDICIONAL: ${t} acertos valem apenas se os ${fixos.length} fixos forem sorteados. A cobertura verifica C(${universoRestante.length},${k - fixos.length},${tEfetivo}) = ${coberturaRestante?.tSubsetsTotal ?? 0} alvos. Se algum fixo não sair, não há garantia.`);
      if (fixos.length >= t) {
        avisos.push(`Com ${fixos.length} fixos ≥ t=${t}, os próprios fixos já garantem ${t} acertos se todos saírem; o cover reduzido cobre ${tEfetivo} acerto(s) adicional(is) por segurança.`);
      }
    }
    if (coverInfo) {
      const tipo = coverInfo.verificado
        ? 'verificada'
        : coverInfo.blocos === coverInfo.limiteInferior
          ? 'ótima (provada)'
          : 'conhecida';
      avisos.push(`Cobertura ${tipo}${coverInfo.permutado ? ' (permutada para os filtros)' : ''}: ${coverInfo.blocos} blocos para C(${coverInfo.v},${coverInfo.k},${coverInfo.t}) · ${coverInfo.fonte}.`);
    }
    if (coverIgnorado) {
      avisos.push(`Existe cover C(${coverIgnorado.v},${coverIgnorado.k},${coverIgnorado.t}) com ${coverIgnorado.blocos} apostas, mas "Máx. apostas"=${maxApostas}. Use 0 (sem limite) para usá-lo.`);
    }
    if (maxApostas === 0 && !coverInfo) avisos.push('0 = sem limite: a geração pode demorar em cenários com t alto.');
    if (fcfg.avisoVolume && !coverInfo && maxApostas === 0 && universoEfetivo.length >= 40) avisos.push(fcfg.avisoVolume);
    if (filtroRepetidas && removidasRepetidas > 0) {
      avisos.push(`Filtro de repetidas removeu ${removidasRepetidas} aposta(s); a cobertura exibida já é a recalculada.`);
    }
    if (modoReparo) {
      avisos.push(`Reparo de cobertura: +${reparoAdicionadas} aposta(s) válidas para restaurar 100% dos t-subconjuntos.`);
    }
    if (coberturaRestante && !coberturaRestante.coberta) {
      avisos.push('A cobertura do universo restante não ficou em 100%. Reduza filtros ou aumente o limite de apostas.');
    }
    if (!wheelApostas && seedsEfetivas > 1) {
      avisos.push(`Foram testadas ${seedsEfetivas} seed(s); o tempo limite foi dividido entre elas.`);
    }
    if (cpSatInfo) {
      const rotuloSolver = cpSatInfo.solver === 'cp_sat' ? 'CP-SAT' : cpSatInfo.solver;
      if (cpSatInfo.usado) {
        avisos.push(`${rotuloSolver} reduziu de ${melhor.apostasBrutas.length} para ${apostasBrutasFinal.length} aposta(s) (status ${cpSatInfo.status}).`);
      } else if (cpSatInfo.error) {
        avisos.push(`${rotuloSolver} indisponível/não melhorou: ${cpSatInfo.error}`);
      } else if (cpSatInfo.status === 'UNKNOWN') {
        avisos.push(`${rotuloSolver} atingiu o limite de ${cpSatTimeLimit}s sem melhorar (UNKNOWN); heurístico mantido.`);
      } else if (cpSatInfo.status === 'INFEASIBLE') {
        avisos.push(`${rotuloSolver} não encontrou solução com menos apostas (INFEASIBLE); heurístico mantido.`);
      } else {
        avisos.push(`${rotuloSolver} não melhorou a solução (status ${cpSatInfo.status}).`);
      }
    }

    if (chaveCache) {
      cacheSalvar(chaveCache, {
        parametros: { v: universoEfetivo.length, k, t: tEfetivo, maxApostas, seed, otimizado },
        apostas,
        cobertura,
        geradoEm: new Date().toISOString(),
      });
    }

    return NextResponse.json(montarRespostaFinal({
      loteria,
      universo: universoEfetivo,
      fixos,
      excluidos,
      filtrosCategorias,
      k,
      t,
      garantiaCondicional,
      tEfetivo,
      modo,
      wheelUsado: Boolean(wheelApostas),
      apostas,
      cobertura,
      coberturaRestante,
      limiteInferior,
      custo,
      seedUsado: melhor.seed,
      seeds: seedsEfetivas,
      filtroRepetidas,
      removidasRepetidas,
      aviso: avisos.length ? avisos.join(' | ') : undefined,
      backtest: backtestFinal,
      tempoGeracaoMs: Date.now() - inicioRequisicao,
      cpSat: cpSatInfo,
      coverConhecido: coverInfo,
    }));
  } catch (error: any) {
    return NextResponse.json({ sucesso: false, error: error?.message || "Erro desconhecido" }, { status: 400 });
  }
}
