'use client';

import { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { getLotteryConfig, dezenasValidas, calcularPrecoAposta, combinacoes, MESES_SORTE, nomeMesSorte } from '@/lib/lottery-config';
import { premioMesSorte } from '@/lib/premios';
import { getJanelaAlvo, type JanelaAlvoData, type JanelaAlvoNumero } from '@/lib/api';
import type { PrevisaoItem, PrevisaoTendenciaComparativo, PrevisaoColunaRange, QuarentenaPosicaoLF, CicloInfo, TransicaoQMF, Repeticao3Sorteios } from '@/types';
import type { AnaliseGruposData } from '@/lib/analise-grupos';
import { parseColunasPosicionais, parseExcluidosPosicoes, parseFiltroComparativo, parseFixosPosicoes } from '@/lib/colunas-posicionais';
import type { VerificarCoberturaResult, RelatorioCustoResult, BacktestFechamentoResult } from '@/lib/fechamento-combinatorio';
import type { CpSatFechamentoResult } from '@/lib/cp-sat';
import { getFechamentoConfig, textoPremios, LIMITE_COBERTURA_COMPLETA } from '@/lib/fechamento/config';
import type { FiltrosSnapshot } from '@/lib/analise-filtros';
import GeneratingOverlay from '@/components/GeneratingOverlay';
import QuarantineMatrixMini from '@/components/QuarantineMatrixMini';

interface OtimizacaoCandidato {
  seed: number;
  totalApostas: number;
  cobertura: number;
  sobreposicaoMedia: number | null;
  lucroTreino: number | null;
  lucroHoldout: number | null;
}

interface OtimizacaoInfo {
  criterio: string;
  seedsTestadas: number;
  seedEscolhida: number;
  totalApostas: number;
  cobertura: number;
  sobreposicaoMedia: number | null;
  lucroTreino: number | null;
  lucroHoldout: number | null;
  holdoutConcursos: number;
  candidatos: OtimizacaoCandidato[];
}

const CRITERIOS_OTIMIZACAO: Record<string, string> = {
  custo: 'menos apostas',
  diversidade: 'mais diversidade',
  backtest: 'backtest (holdout)',
  equilibrado: 'equilibrado',
};

interface JogoGerado {
  numeros: number[];
  trevos?: number[];
  /** Mês da Sorte (1-12) — Dia de Sorte. */
  mes?: number;
  estrategia: string;
  soma: number;
  pares: number;
  impares: number;
  primos: number;
  score?: number;
}

interface Estatisticas {
  total: number;
  cobertura: number;
  frequencia: Record<number, number>;
  estrategias: Record<string, number>;
}

interface CicloNumero {
  numero: number;
  qtd: number;
}

interface CicloAtual {
  numero: CicloNumero[];
  faltantes: number[];
  baixa_frequencia: number[];
  media_frequencia: number;
}

interface JogosDiversosSectionProps {
  loteria?: string;
  concursoBase?: number;
  concursoAtual?: number;
  numerosSorteadosAtual?: number[];
  previsaoPosicional?: Record<string, PrevisaoItem[]> | null;
  previsaoTendencia?: PrevisaoTendenciaComparativo;
  previsaoColunas?: PrevisaoColunaRange[];
  quarentena?: Record<string, QuarentenaPosicaoLF> | null;
  grupos?: AnaliseGruposData | null;
  numerosQuentes?: [number, number][];
  numerosMornos?: [number, number][];
  numerosFrios?: [number, number][];
  ciclos?: Record<string, CicloInfo>;
  transicaoQmf?: TransicaoQMF;
  repeticao3?: Repeticao3Sorteios;
  onFiltrosAplicados?: (filtros: FiltrosSnapshot) => void;
  /** Concursos disponíveis para o seletor compacto da grade. */
  concursosDisponiveis?: number[];
  /** Troca o concurso base (mesma fonte de verdade do seletor do topo). */
  onConcursoChange?: (concurso: number | undefined) => void;
}

/**
 * Seletor compacto de concurso base, exibido junto à grade de dezenas.
 *
 * Espelha o seletor do topo — mesma fonte de verdade, sem estado paralelo — só
 * que ao alcance do mouse enquanto se escolhem fixos e excluídos. `undefined`
 * significa "Geral" (último concurso / todos os sorteios).
 */
function SeletorConcursoBase({
  concursos,
  value,
  onChange,
  carregando = false,
}: {
  concursos: number[];
  value: number | undefined;
  onChange: (concurso: number | undefined) => void;
  carregando?: boolean;
}) {
  const [texto, setTexto] = useState('');
  const [editando, setEditando] = useState(false);
  const cancelarRef = useRef(false);

  const idxAtual = value !== undefined ? concursos.indexOf(value) : concursos.length - 1;
  const podeAnterior = concursos.length > 1 && idxAtual > 0;
  const podeProximo = value !== undefined && concursos.length > 0;

  const irPara = useCallback((delta: number) => {
    if (concursos.length === 0) return;
    const idx = value !== undefined ? concursos.indexOf(value) : concursos.length - 1;
    if (idx < 0) return;
    const alvo = idx + delta;
    if (alvo < 0) return;
    // Depois do último concurso só existe "Geral".
    if (alvo >= concursos.length) {
      onChange(undefined);
      return;
    }
    onChange(concursos[alvo]);
  }, [concursos, value, onChange]);

  const aplicar = useCallback(() => {
    const digitos = texto.replace(/\D/g, '');
    if (digitos === '') {
      onChange(undefined);
    } else {
      const n = Number(digitos);
      if (concursos.includes(n)) onChange(n);
    }
    setEditando(false);
    setTexto('');
  }, [texto, concursos, onChange]);

  const valorExibido = editando ? texto : (value !== undefined ? String(value) : '');

  const btnNav = 'w-7 h-7 flex items-center justify-center rounded-md bg-white/10 text-muted hover:text-fg hover:bg-white/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed text-sm';

  return (
    <div className="flex items-center gap-1">
      <button
        type="button"
        onClick={() => irPara(-1)}
        disabled={!podeAnterior}
        title="Concurso anterior"
        className={btnNav}
      >
        −
      </button>

      <div className="relative">
        <input
          type="text"
          inputMode="numeric"
          value={valorExibido}
          placeholder="último"
          onFocus={e => {
            setEditando(true);
            setTexto(value !== undefined ? String(value) : '');
            e.currentTarget.select();
          }}
          onBlur={() => {
            if (cancelarRef.current) {
              cancelarRef.current = false;
              setEditando(false);
              setTexto('');
              return;
            }
            aplicar();
          }}
          onChange={e => setTexto(e.target.value.replace(/\D/g, ''))}
          onKeyDown={e => {
            if (e.key === 'Enter') {
              e.preventDefault();
              e.currentTarget.blur();
            }
            if (e.key === 'Escape') {
              cancelarRef.current = true;
              setEditando(false);
              setTexto('');
              e.currentTarget.blur();
            }
          }}
          className="w-20 px-2 py-1 rounded-md text-xs text-center text-ink bg-white/5 border border-white/10 focus:border-accent-2/50 focus:outline-none focus:ring-1 focus:ring-accent-2/30"
          title="Digite o concurso e pressione Enter"
        />
        {carregando && (
          <span
            className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-accent-2 animate-pulse"
            title="Carregando resultado do concurso..."
          />
        )}
      </div>

      <button
        type="button"
        onClick={() => irPara(1)}
        disabled={!podeProximo}
        title="Próximo concurso"
        className={btnNav}
      >
        +
      </button>

      <button
        type="button"
        onClick={() => onChange(undefined)}
        className={`text-[11px] px-2 py-1 rounded-md border transition-colors ${
          value === undefined
            ? 'bg-accent/20 border-accent/40 text-accent-2 font-semibold'
            : 'bg-white/5 border-white/10 text-muted hover:text-fg hover:bg-white/10'
        }`}
        title="Voltar ao concurso atual (todos os sorteios)"
      >
        Geral
      </button>
    </div>
  );
}

interface CategoriaDef {
  id: string;
  label: string;
  cor: string;
  set: number[];
}const ESTRATEGIA_LABEL: Record<string, string> = {
  atraso: 'Atrasados',
  'hot7-9': 'Quentes',
  persistencia: 'Persistência',
  aleatorio: 'Aleatório',
  ciclo: 'Ciclo',
  colunas: 'Colunas',
  comparativo: 'Comparativo',
};

type NumeroEstado = 'normal' | 'fixo' | 'excluido';

const ORDENACAO_LABEL: Record<string, string> = {
  aleatorio: 'Aleatório',
  melhores: 'Melhores (score)',
  balanceado: 'Balanceado',
  piores: 'Piores (score)',
};

const REPETIDOS_LABELS = ['Anterior', 'Ante-anterior', 'Ante-ante-anterior'];
const REPETIDOS_CORES = ['#93c5fd', '#c4b5fd', '#fca5a5'];

const jogoLinha = (jogo: JogoGerado): string => {
  const dezenas = jogo.numeros.join(',');
  if (jogo.trevos && jogo.trevos.length > 0) return `${dezenas}|${jogo.trevos.join(',')}`;
  if (jogo.mes) return `${dezenas}|M:${jogo.mes}`;
  return dezenas;
};

function parseFaixa(valor: string): { min: number; max: number } {
  const [a, b] = valor.split('-').map(x => parseInt(x, 10));
  return { min: a, max: b ?? a };
}

/**
 * Sorteia `quantidade` itens de `itens` (Fisher-Yates parcial, sem repetição).
 * Base para o modo aleatório da aplicação em lote — o modo otimizado usará a
 * mesma assinatura, apenas trocando o critério de escolha.
 */
function classeBadgeJanela(item: JanelaAlvoNumero): string {
  if (item.ocorrencias === 0) return 'bg-hot/30 text-hot-bright border-hot/50';
  if (item.percentual >= 60) return 'bg-emerald-500/40 text-emerald-50 border-emerald-400/60';
  if (item.percentual >= 30) return 'bg-amber-500/35 text-amber-100 border-amber-400/60';
  return 'bg-[rgba(129,140,248,0.35)] text-[#e0e7ff] border-[rgba(129,140,248,0.55)]';
}

function sortearSubconjunto<T>(itens: T[], quantidade: number): T[] {
  const copia = [...itens];
  const limite = Math.min(quantidade, copia.length);
  for (let i = 0; i < limite; i++) {
    const j = i + Math.floor(Math.random() * (copia.length - i));
    [copia[i], copia[j]] = [copia[j], copia[i]];
  }
  return copia.slice(0, limite);
}

/**
 * Calcula um score de atratividade para cada número disponível, combinando:
 *  - frequência (quentes/mornos/frios)
 *  - ciclo (aquecendo/esfriando/estável) e diferença vs esperada
 *  - previsão posicional (máxima probabilidade em qualquer posição)
 *  - repetição recente (saiu no concurso atual)
 *
 * Números com score mais alto são melhores candidatos a fixar; os de menor
 * score são candidatos a excluir. Quando não há dados de previsão, o score
 * cai de volta para 0 (neutro) e o sorteio aleatório continua valendo.
 */
function calcularScoresNumeros(
  numeros: number[],
  {
    numerosQuentes,
    numerosMornos,
    numerosFrios,
    ciclos,
    previsaoPosicional,
    numerosSorteadosAtual,
  }: {
    numerosQuentes?: [number, number][];
    numerosMornos?: [number, number][];
    numerosFrios?: [number, number][];
    ciclos?: Record<string, CicloInfo>;
    previsaoPosicional?: Record<string, PrevisaoItem[]> | null;
    numerosSorteadosAtual?: number[];
  },
): Record<number, number> {
  const quentesMap = new Map(numerosQuentes?.map(([n, v]) => [n, v]) ?? []);
  const mornosMap = new Map(numerosMornos?.map(([n, v]) => [n, v]) ?? []);
  const friosMap = new Map(numerosFrios?.map(([n, v]) => [n, v]) ?? []);
  const sorteadosSet = new Set(numerosSorteadosAtual ?? []);

  const scores: Record<number, number> = {};
  for (const n of numeros) {
    let score = 0;

    // Frequência: quentes somam, frios subtraem, mornos neutro leve.
    const q = quentesMap.get(n) ?? 0;
    const m = mornosMap.get(n) ?? 0;
    const f = friosMap.get(n) ?? 0;
    const freqMax = Math.max(q, m, f, 1);
    score += (q / freqMax) * 30;      // quente: até +30
    score -= (f / freqMax) * 30;      // frio: até -30
    score += (m / freqMax) * 5;       // morno: até +5

    // Ciclo: aquecendo bônus, esfriando penalidade, proporcional à diferença.
    const ciclo = ciclos?.[String(n)];
    if (ciclo) {
      if (ciclo.estado === 'aquecendo') score += 20 + Math.min(10, ciclo.diferenca);
      else if (ciclo.estado === 'esfriando') score -= 20 + Math.min(10, -ciclo.diferenca);
    }

    // Previsão posicional: melhor probabilidade em qualquer posição.
    if (previsaoPosicional) {
      let melhorProb = 0;
      for (const pos of Object.keys(previsaoPosicional)) {
        const item = previsaoPosicional[pos].find(x => x.numero === n);
        if (item && item.prob > melhorProb) melhorProb = item.prob;
      }
      score += melhorProb * 40; // até +40 se tiver 100% de prob em alguma posição
    }

    // Repetição imediata: saiu no concurso atual → leve penalidade (evita
    // apostar tudo no que já saiu; ainda assim não zera o número).
    if (sorteadosSet.has(n)) score -= 10;

    scores[n] = score;
  }
  return scores;
}

/** Unidade do sorteio em lote: dezenas soltas, ou a casa inteira da grade. */
type LoteUnidade = 'dezena' | 'coluna' | 'linha';

/** Colunas da grade de dezenas — mesma geometria usada no render. */
function colunasDaGrade(total: number): 5 | 8 | 10 {
  return total <= 25 ? 5 : total <= 31 ? 8 : 10;
}

/** Classes Tailwind da grade; literais para o JIT não perder as regras. */
const GRID_CLASS_POR_COLUNAS: Record<5 | 8 | 10, string> = {
  5: 'grid-cols-5',
  8: 'grid-cols-8',
  10: 'grid-cols-10',
};

interface GrupoGrade {
  id: number;
  numeros: number[];
}

/**
 * Agrupa as dezenas por coluna ou por linha, na mesma ordem da grade.
 * Coluna = mesma posição em todas as linhas (na Mega-Sena, 6 dezenas);
 * linha = uma faixa de `colunas` dezenas (na Mega-Sena, a década).
 */
function gruposDaGrade(
  numeros: number[],
  colunas: number,
  unidade: 'coluna' | 'linha',
): GrupoGrade[] {
  const mapa = new Map<number, number[]>();
  numeros.forEach((n, i) => {
    const id = unidade === 'coluna' ? (i % colunas) + 1 : Math.floor(i / colunas) + 1;
    const lista = mapa.get(id);
    if (lista) lista.push(n);
    else mapa.set(id, [n]);
  });
  return [...mapa.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([id, nums]) => ({ id, numeros: nums }));
}

/**
 * Escolhe `quantidade` números de `disponiveis` ordenados por score.
 * Quando `otimizado` está ativo, pega os de maior score (fixar) ou menor
 * score (excluir); caso contrário, sorteia aleatoriamente.
 */
function selecionarNumerosLote(
  disponiveis: number[],
  quantidade: number,
  otimizado: boolean,
  scores: Record<number, number>,
  modo: 'fixo' | 'excluido',
): number[] {
  if (!otimizado || quantidade === 0) return sortearSubconjunto(disponiveis, quantidade).sort((a, b) => a - b);

  const ordenados = [...disponiveis].sort((a, b) => {
    const sa = scores[a] ?? 0;
    const sb = scores[b] ?? 0;
    // Fixar: maiores scores primeiro. Excluir: menores scores primeiro.
    return modo === 'fixo' ? sb - sa : sa - sb;
  });
  return ordenados.slice(0, quantidade).sort((a, b) => a - b);
}

export default function JogosDiversosSection({ loteria = 'lotofacil', concursoBase, concursoAtual, numerosSorteadosAtual = [], previsaoPosicional, previsaoTendencia, previsaoColunas, quarentena, grupos, numerosQuentes, numerosMornos, numerosFrios, ciclos, transicaoQmf, repeticao3, onFiltrosAplicados, concursosDisponiveis, onConcursoChange }: JogosDiversosSectionProps) {
  const cfg = getLotteryConfig(loteria);
  const fechamentoCfg = useMemo(() => getFechamentoConfig(loteria), [loteria]);
  const opcoesDezenas = dezenasValidas(cfg);
  const [quantidade, setQuantidade] = useState<number>(5);
  const [dezenas, setDezenas] = useState<number>(cfg.numeros_por_jogo);
  const [mesSorte, setMesSorte] = useState<number | 'aleatorio'>('aleatorio');
  const [mostrarJanela, setMostrarJanela] = useState<boolean>(true);
  const [janelaTamanho, setJanelaTamanho] = useState<number>(7);
  const [janelaDados, setJanelaDados] = useState<JanelaAlvoData | null>(null);
  const [janelaCarregando, setJanelaCarregando] = useState<boolean>(false);
  const [janelaErro, setJanelaErro] = useState<string | null>(null);
  const [estados, setEstados] = useState<Record<number, NumeroEstado>>({});
  const [jogos, setJogos] = useState<JogoGerado[] | null>(null);
  const [estatisticas, setEstatisticas] = useState<Estatisticas | null>(null);
  const [cicloAtual, setCicloAtual] = useState<CicloAtual | null>(null);
  const [estimativaTotal, setEstimativaTotal] = useState<number | null>(null);
  const [modoTodas, setModoTodas] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progresso, setProgresso] = useState(0);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [colunasInputs, setColunasInputs] = useState<string[]>(['', '', '', '', '']);
  const [linhasFiltro, setLinhasFiltro] = useState<Record<string, number[]>>({});
  const [comparativoInputs, setComparativoInputs] = useState<string[]>(['', '', '']);
  const [fixosPosicoes, setFixosPosicoes] = useState<Record<number, number[]>>({});
  const [excluidosPosicoes, setExcluidosPosicoes] = useState<Record<number, number[]>>({});
  const [estrategiasFiltro, setEstrategiasFiltro] = useState<string[]>([]);
  const [categoriasInputs, setCategoriasInputs] = useState<Record<string, string>>({});
  const [repetidosInputs, setRepetidosInputs] = useState<string[]>(['', '', '']);
  const [ordenacao, setOrdenacao] = useState<string>('aleatorio');
  // Aplicação em lote: a quantidade de números a sortear (fixar ou excluir).
  const [loteQuantidade, setLoteQuantidade] = useState<string>('');
  const [loteModo, setLoteModo] = useState<'fixo' | 'excluido'>('fixo');
  const [loteOtimizado, setLoteOtimizado] = useState<boolean>(false);
  // Unidade do lote: dezena solta, ou a casa inteira da grade (coluna/linha).
  const [loteUnidade, setLoteUnidade] = useState<LoteUnidade>('dezena');
  const [loteFeedback, setLoteFeedback] = useState<{ tipo: 'ok' | 'erro'; texto: string } | null>(null);

  // Seletor compacto de concurso junto à grade: o resultado do concurso escolhido
  // é buscado num endpoint leve e destacado na hora, enquanto a análise recarrega.
  const [concursoPreview, setConcursoPreview] = useState<{ concurso: number; numeros: number[] } | null>(null);
  const [carregandoConcurso, setCarregandoConcurso] = useState(false);
  const concursoPreviewReq = useRef(0);
  // Resultados já visitados: navegar de volta é instantâneo, sem ida ao servidor.
  const resultadoCache = useRef(new Map<number, number[]>());
  const resultadosEmVoo = useRef(new Map<number, Promise<number[] | null>>());

  const buscarResultadoConcurso = useCallback((concurso: number): Promise<number[] | null> => {
    const emCache = resultadoCache.current.get(concurso);
    if (emCache) return Promise.resolve(emCache);
    const emVoo = resultadosEmVoo.current.get(concurso);
    if (emVoo) return emVoo;

    const pedido = (async (): Promise<number[] | null> => {
      try {
        const resp = await fetch(
          `/api/resultado-concurso?loteria=${encodeURIComponent(loteria)}&concurso=${concurso}`,
        );
        if (!resp.ok) return null;
        const j = await resp.json();
        const numeros = Array.isArray(j.numeros) ? j.numeros.map(Number) : [];
        if (numeros.length === 0) return null;
        resultadoCache.current.set(concurso, numeros);
        return numeros;
      } catch {
        return null;
      } finally {
        resultadosEmVoo.current.delete(concurso);
      }
    })();

    resultadosEmVoo.current.set(concurso, pedido);
    return pedido;
  }, [loteria]);

  const aplicarConcursoBase = useCallback((novo: number | undefined) => {
    const req = ++concursoPreviewReq.current;
    if (novo === undefined) {
      setConcursoPreview(null);
      setCarregandoConcurso(false);
      onConcursoChange?.(undefined);
      return;
    }

    const emCache = resultadoCache.current.get(novo);
    if (emCache) {
      setConcursoPreview({ concurso: novo, numeros: emCache });
      setCarregandoConcurso(false);
      onConcursoChange?.(novo);
      return;
    }

    // A requisição leve sai antes do reload da análise: como o cálculo roda no
    // mesmo processo do servidor, inverter a ordem evita ficar na fila dele.
    setCarregandoConcurso(true);
    const pendente = buscarResultadoConcurso(novo);
    onConcursoChange?.(novo);
    pendente.then(numeros => {
      // Só a última requisição pode escrever no preview (evita corrida no −/+).
      if (concursoPreviewReq.current !== req) return;
      setCarregandoConcurso(false);
      if (!numeros) return;
      setConcursoPreview({ concurso: novo, numeros });
    });
  }, [buscarResultadoConcurso, onConcursoChange]);

  useEffect(() => {
    // Troca de loteria invalida preview e cache (dezenas de outro universo).
    resultadoCache.current.clear();
    resultadosEmVoo.current.clear();
    setConcursoPreview(null);
    setCarregandoConcurso(false);
  }, [loteria]);

  // Janela anterior ao concurso alvo exibida sobre a grade de fixos/excluídos.
  const concursoAlvoJanela = concursoBase ?? concursoAtual;
  const janelaPorNumero = useMemo(() => {
    const mapa = new Map<number, JanelaAlvoNumero>();
    for (const item of janelaDados?.numeros ?? []) mapa.set(item.numero, item);
    return mapa;
  }, [janelaDados]);

  useEffect(() => {
    if (!mostrarJanela || concursoAlvoJanela === undefined) {
      setJanelaDados(null);
      setJanelaErro(null);
      setJanelaCarregando(false);
      return;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => {
      setJanelaCarregando(true);
      setJanelaErro(null);
      getJanelaAlvo(loteria, concursoAlvoJanela, janelaTamanho, controller.signal)
        .then(res => {
          if (!controller.signal.aborted) setJanelaDados(res);
        })
        .catch(err => {
          if (controller.signal.aborted) return;
          setJanelaDados(null);
          setJanelaErro(err instanceof Error ? err.message : 'Erro ao carregar a janela');
        })
        .finally(() => {
          if (!controller.signal.aborted) setJanelaCarregando(false);
        });
    }, 250);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [mostrarJanela, loteria, concursoAlvoJanela, janelaTamanho]);

  useEffect(() => {
    // Pré-carrega os concursos vizinhos do base: o próximo −/+ sai do cache.
    const base = concursoBase ?? concursoAtual;
    const lista = concursosDisponiveis ?? [];
    if (base === undefined) return;
    const idx = lista.indexOf(base);
    if (idx < 0) return;
    for (const d of [-1, 1]) {
      const vizinho = lista[idx + d];
      if (vizinho !== undefined && !resultadoCache.current.has(vizinho)) {
        void buscarResultadoConcurso(vizinho);
      }
    }
  }, [concursoBase, concursoAtual, concursosDisponiveis, buscarResultadoConcurso]);

  useEffect(() => {
    // Quando a análise alcança o concurso escolhido, o preview já não é necessário.
    if (concursoPreview && concursoAtual === concursoPreview.concurso) {
      setConcursoPreview(null);
      setCarregandoConcurso(false);
    }
  }, [concursoAtual, concursoPreview]);

  useEffect(() => {
    // Se o concurso base mudou por fora (seletor do topo), o preview fica obsoleto.
    if (concursoPreview && concursoPreview.concurso !== concursoBase) {
      setConcursoPreview(null);
      setCarregandoConcurso(false);
    }
  }, [concursoBase, concursoPreview]);

  // --- Fechamento Combinatório ---
  const [modoFechamento, setModoFechamento] = useState<boolean>(false);
  const [fechamentoK, setFechamentoK] = useState<number>(fechamentoCfg.kPadrao);
  const [fechamentoT, setFechamentoT] = useState<number>(fechamentoCfg.tPadrao);
  const [fechamentoMax, setFechamentoMax] = useState<number>(200);
  const [fechamentoSeed, setFechamentoSeed] = useState<number>(7);
  const [fechamentoOtimizado, setFechamentoOtimizado] = useState<boolean>(true);
  const [fechamentoUsarLottoDesign, setFechamentoUsarLottoDesign] = useState<boolean>(false);
  const [fechamentoCoberturaCompleta, setFechamentoCoberturaCompleta] = useState<boolean>(false);
  const [lottoDesignInfo, setLottoDesignInfo] = useState<{
    v: number; k: number; m: number; t: number; blocos: number;
    piso: number; pisoTotal: number; alvos: number; limiteInferior: number;
    fonte: string; verificado: boolean; tempoMs: number;
  } | null>(null);
  const [lottoIgnoradoInfo, setLottoIgnoradoInfo] = useState<{ motivo: string } | null>(null);
  const [aplicarFiltrosCategorias, setAplicarFiltrosCategorias] = useState<boolean>(false);
  const [apostasFechamento, setApostasFechamento] = useState<number[][]>([]);
  const [coberturaFechamento, setCoberturaFechamento] = useState<VerificarCoberturaResult | null>(null);
  const [custoFechamento, setCustoFechamento] = useState<RelatorioCustoResult | null>(null);
  const [gerandoFechamento, setGerandoFechamento] = useState<boolean>(false);
  const [fechamentoSeeds, setFechamentoSeeds] = useState<number>(1);
  const [fechamentoAmostra, setFechamentoAmostra] = useState<number>(0);
  const [fechamentoUsarCpSat, setFechamentoUsarCpSat] = useState<boolean>(true);
  const [fechamentoSolver, setFechamentoSolver] = useState<'cp_sat' | 'SCIP' | 'CBC'>('cp_sat');
  const [fechamentoCpSatTime, setFechamentoCpSatTime] = useState<number>(10);
  const [cpSatInfo, setCpSatInfo] = useState<(CpSatFechamentoResult & { usado: boolean }) | null>(null);
  const [coverConhecidoInfo, setCoverConhecidoInfo] = useState<{ v: number; k: number; t: number; blocos: number; fonte: string; limiteInferior?: number; verificado?: boolean } | null>(null);
  const [fechamentoPriorizarPremios, setFechamentoPriorizarPremios] = useState<boolean>(false);
  const [fechamentoRemoverRedundantes, setFechamentoRemoverRedundantes] = useState<boolean>(true);
  const [fechamentoGarantiaCondicional, setFechamentoGarantiaCondicional] = useState<boolean>(false);
  const [fechamentoTInfo, setFechamentoTInfo] = useState<{ garantiaCondicional: boolean; tEfetivo: number; t: number } | null>(null);
  const [fechamentoOtimizarQtd, setFechamentoOtimizarQtd] = useState<number>(20);
  const [fechamentoCriterioOtimizacao, setFechamentoCriterioOtimizacao] = useState<'custo' | 'diversidade' | 'backtest' | 'equilibrado'>('custo');
  const [fechamentoAplicarFiltrosTela, setFechamentoAplicarFiltrosTela] = useState<boolean>(false);
  const [otimizacaoInfo, setOtimizacaoInfo] = useState<OtimizacaoInfo | null>(null);
  const [fechamentoFiltroRepetidasAtivo, setFechamentoFiltroRepetidasAtivo] = useState<boolean>(false);
  const [fechamentoRepetidasFaixa, setFechamentoRepetidasFaixa] = useState<string>(fechamentoCfg.repetidasPadrao);
  const [fechamentoSeedUsado, setFechamentoSeedUsado] = useState<number | null>(null);
  const [fechamentoSeedsTestadas, setFechamentoSeedsTestadas] = useState<number | null>(null);
  const [fechamentoLimiteInferior, setFechamentoLimiteInferior] = useState<number | null>(null);
  const [fechamentoCoberturaRestante, setFechamentoCoberturaRestante] = useState<VerificarCoberturaResult | null>(null);
  const [fechamentoPisoCondicional, setFechamentoPisoCondicional] = useState<{
    piso: number; pisoTotal: number; alvos: number; universoEfetivo: number; m: number; completo: boolean;
  } | null>(null);
  const [fechamentoAviso, setFechamentoAviso] = useState<string | null>(null);
  const [fechamentoFiltroInfo, setFechamentoFiltroInfo] = useState<{ min: number; max: number; removidas: number } | null>(null);
  const [backtestFechamento, setBacktestFechamento] = useState<BacktestFechamentoResult | null>(null);
  const [rodandoBacktest, setRodandoBacktest] = useState<boolean>(false);
  const abortFechamentoRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // t = k é pré-requisito da cobertura completa por enumeração.
    if (fechamentoT !== fechamentoK) setFechamentoCoberturaCompleta(false);
  }, [fechamentoT, fechamentoK]);

  const repetidosItens = useMemo(() => repeticao3?.itens ?? [], [repeticao3]);

  const categoriasDefs = useMemo<CategoriaDef[]>(() => {
    const defs: CategoriaDef[] = [];
    if (grupos) {
      defs.push(
        { id: 'grupoA', label: 'Grupo A', cor: '#a78bfa', set: [...grupos.grupos.A] },
        { id: 'grupoB', label: 'Grupo B', cor: '#6ee7b7', set: [...grupos.grupos.B] },
        { id: 'grupoC', label: 'Grupo C', cor: '#c084fc', set: [...grupos.grupos.C] },
      );
    }
    if (ciclos) {
      const aquecendo = Object.entries(ciclos).filter(([, c]) => c.estado === 'aquecendo').map(([n]) => Number(n));
      const esfriando = Object.entries(ciclos).filter(([, c]) => c.estado === 'esfriando').map(([n]) => Number(n));
      if (aquecendo.length > 0) defs.push({ id: 'aquecendo', label: 'Aquecendo', cor: '#6ee7b7', set: aquecendo });
      if (esfriando.length > 0) defs.push({ id: 'esfriando', label: 'Esfriando', cor: '#fdba74', set: esfriando });
    }
    if (numerosQuentes && numerosQuentes.length > 0) defs.push({ id: 'quentes', label: 'Quentes', cor: '#fb923c', set: numerosQuentes.map(n => n[0]) });
    if (numerosMornos && numerosMornos.length > 0) defs.push({ id: 'mornos', label: 'Mornos', cor: '#a3b3cc', set: numerosMornos.map(n => n[0]) });
    if (numerosFrios && numerosFrios.length > 0) defs.push({ id: 'frios', label: 'Frios', cor: '#67e8f9', set: numerosFrios.map(n => n[0]) });
    return defs;
  }, [grupos, ciclos, numerosQuentes, numerosMornos, numerosFrios]);

  const colunasSets = useMemo(() => {
    if (!previsaoPosicional) return null;
    const sets: number[][] = [[], [], [], [], []];
    for (const pos of Object.keys(previsaoPosicional)) {
      const preds = previsaoPosicional[pos] || [];
      preds.slice(0, 5).forEach((x, c) => sets[c].push(x.numero));
    }
    return sets.map(s => [...new Set(s)]);
  }, [previsaoPosicional]);

  const posicoesLinhas = useMemo(() => {
    if (!previsaoPosicional) return [] as string[];
    return Object.keys(previsaoPosicional).sort((a, b) => {
      const na = parseInt(a.replace(/\D/g, ''), 10) || 0;
      const nb = parseInt(b.replace(/\D/g, ''), 10) || 0;
      return na - nb;
    });
  }, [previsaoPosicional]);

  const toggleLinha = (pos: string, numero: number) => {
    setLinhasFiltro(prev => {
      const atual = prev[pos] ?? [];
      const proximo = atual.includes(numero)
        ? atual.filter(n => n !== numero)
        : [...atual, numero];
      return { ...prev, [pos]: proximo };
    });
  };

  const linhasMaisConcentradas = (limite: number) =>
    [...posicoesLinhas]
      .sort((a, b) => {
        const pa = previsaoPosicional?.[a]?.[0]?.prob ?? 0;
        const pb = previsaoPosicional?.[b]?.[0]?.prob ?? 0;
        return pb - pa;
      })
      .slice(0, Math.max(1, limite));

  const aplicarTopLinhas = (top: number) => {
    if (!previsaoPosicional) return;
    const next: Record<string, number[]> = {};
    for (const pos of linhasMaisConcentradas(top)) {
      next[pos] = (previsaoPosicional[pos] ?? []).slice(0, top).map(x => x.numero);
    }
    setLinhasFiltro(next);
  };

  const aplicarCoberturaLinhas = (alvo: number) => {
    if (!previsaoPosicional) return;
    const next: Record<string, number[]> = {};
    for (const pos of posicoesLinhas) {
      const preds = previsaoPosicional[pos] ?? [];
      let acumulado = 0;
      const escolhidos: number[] = [];
      for (const item of preds) {
        escolhidos.push(item.numero);
        acumulado += item.prob;
        if (acumulado >= alvo) break;
      }
      next[pos] = escolhidos;
    }
    setLinhasFiltro(next);
  };

  const coberturaLinha = (pos: string) => {
    const preds = previsaoPosicional?.[pos] ?? [];
    const selecionados = linhasFiltro[pos] ?? [];
    return preds
      .filter(x => selecionados.includes(x.numero))
      .reduce((acc, x) => acc + x.prob, 0);
  };

  useEffect(() => {
    const novoCfg = getLotteryConfig(loteria);
    setEstados({});
    setJogos(null);
    setEstatisticas(null);
    setCicloAtual(null);
    setEstimativaTotal(null);
    setDezenas(novoCfg.numeros_por_jogo);
    setColunasInputs(['', '', '', '', '']);
    setLinhasFiltro({});
    setComparativoInputs(['', '', '']);
    setFixosPosicoes({});
    setExcluidosPosicoes({});
    setEstrategiasFiltro([]);
    setCategoriasInputs({});
    setRepetidosInputs(['', '', '']);
    setOrdenacao('aleatorio');
    setFechamentoK(fechamentoCfg.kPadrao);
    setFechamentoT(fechamentoCfg.tPadrao);
    setFechamentoGarantiaCondicional(false);
    setFechamentoCoberturaCompleta(false);
    setFechamentoTInfo(null);
    setOtimizacaoInfo(null);
    setFechamentoAplicarFiltrosTela(false);
    setFechamentoRepetidasFaixa(fechamentoCfg.repetidasPadrao);
    setApostasFechamento([]);
    setCoberturaFechamento(null);
    setCustoFechamento(null);
    setBacktestFechamento(null);
    setCpSatInfo(null);
    setCoverConhecidoInfo(null);
    setLottoDesignInfo(null);
    setLottoIgnoradoInfo(null);
  }, [loteria, fechamentoCfg]);

  useEffect(() => {
    setJogos(null);
    setEstatisticas(null);
    setEstimativaTotal(null);
    setError(null);
  }, [colunasInputs, linhasFiltro, comparativoInputs, categoriasInputs, repetidosInputs, ordenacao]);

  useEffect(() => {
    if (!loading) return;
    setProgresso(0);
    const id = setInterval(() => {
      setProgresso(p => (p >= 90 ? p : Math.min(90, Math.round(p + Math.max(1, (90 - p) * 0.09)))));
    }, 130);
    return () => clearInterval(id);
  }, [loading]);

  const fixos = Object.entries(estados).filter(([, e]) => e === 'fixo').map(([n]) => Number(n));
  const excluidos = Object.entries(estados).filter(([, e]) => e === 'excluido').map(([n]) => Number(n));
  const sorteadosAtualSet = new Set(
    concursoPreview && concursoPreview.numeros.length > 0 ? concursoPreview.numeros : numerosSorteadosAtual,
  );

  const colunasPosicionaisStr = colunasInputs.map(v => v.trim().replace(/\s+/g, '')).join(',');
  const colunasSetsStr = colunasSets ? colunasSets.map(s => s.join(',')).join(';') : '';
  const temColunas = colunasInputs.some(v => v.trim() !== '') && colunasSets !== null;

  const linhasSetsArray = posicoesLinhas.map(pos => linhasFiltro[pos] ?? []);
  const linhasSetsStr = linhasSetsArray.map(s => s.join(',')).join(';');
  const temLinhas = linhasSetsArray.some(s => s.length > 0);

  const comparativoStr = comparativoInputs.map(v => v.trim()).join(',');
  const temComparativo = comparativoInputs.some(v => v.trim() !== '');

  const categoriasRangesStr = categoriasDefs.map(c => (categoriasInputs[c.id] ?? '').trim()).join(',');
  const categoriasSetsStr = categoriasDefs.map(c => c.set.join(',')).join(';');
  const temCategorias = categoriasDefs.some(c => (categoriasInputs[c.id] ?? '').trim() !== '');
  const scoreSetsStr = categoriasDefs.map(c => `${c.id}:${c.set.join(',')}`).join(';');

  const repetidosRangesStr = repetidosItens.map((_, i) => (repetidosInputs[i] ?? '').trim()).join(',');
  const repetidosSetsStr = repetidosItens.map(item => item.numeros.join(',')).join(';');
  const temRepetidos = repetidosItens.some((_, i) => (repetidosInputs[i] ?? '').trim() !== '');

  const numeroMaximo = cfg.numero_minimo + cfg.total_numeros - 1;
  const posicoesValidas = (n: number) => {
    const lo = Math.max(1, n - numeroMaximo + dezenas);
    const hi = Math.min(dezenas, n - cfg.numero_minimo + 1);
    const res: number[] = [];
    for (let p = lo; p <= hi; p++) res.push(p);
    return res;
  };
  const fixosPosicoesStr = Object.entries(fixosPosicoes)
    .filter(([, ps]) => ps.length > 0)
    .map(([n, ps]) => `${n}:${ps.join(',')}`)
    .join(';');
  const excluidosCompletos = excluidos.filter(n => !(excluidosPosicoes[n] ?? []).length);
  const excluidosPosicoesStr = Object.entries(excluidosPosicoes)
    .filter(([, ps]) => ps.length > 0)
    .map(([n, ps]) => `${n}:${ps.join(',')}`)
    .join(';');

  const usarPrevisaoTendencia = () => {
    if (!previsaoTendencia) {
      setError('Previsão da Tendência Posicional indisponível. Recarregue o dashboard.');
      return;
    }
    const cats = previsaoTendencia.categorias;
    setComparativoInputs([
      `${cats.maiores.p25}-${cats.maiores.p75}`,
      `${cats.iguais.p25}-${cats.iguais.p75}`,
      `${cats.menores.p25}-${cats.menores.p75}`,
    ]);
  };

  const usarPrevisaoColunas = () => {
    if (!previsaoColunas || previsaoColunas.length < 5) {
      setError('Faixas da Previsão Posicional indisponíveis. Recarregue o dashboard.');
      return;
    }
    setColunasInputs(previsaoColunas.map(r => `${r.p25}-${r.p75}`));
  };

  const usarAnaliseCategorias = () => {
    if (categoriasDefs.length === 0) {
      setError('Análise de categorias indisponível para esta loteria. Recarregue o dashboard.');
      return;
    }
    const totalN = cfg.total_numeros;
    const proximo: Record<string, string> = {};
    for (const c of categoriasDefs) {
      if (grupos && (c.id === 'grupoA' || c.id === 'grupoB' || c.id === 'grupoC')) {
        const g = c.id === 'grupoA' ? 'A' : c.id === 'grupoB' ? 'B' : 'C';
        const s = grupos.stats[g];
        proximo[c.id] = `${s.min}-${s.max}`;
      } else if (transicaoQmf && transicaoQmf.recentes.length >= 3 && (c.id === 'quentes' || c.id === 'mornos' || c.id === 'frios')) {
        const key = c.id === 'quentes' ? 'quentes' : c.id === 'mornos' ? 'mornos' : 'frios';
        const vals = transicaoQmf.recentes.map(r => r[key]);
        proximo[c.id] = `${Math.min(...vals)}-${Math.max(...vals)}`;
      } else {
        const esperado = Math.round(c.set.length / totalN * dezenas);
        const lo = Math.max(0, esperado - 2);
        const hi = Math.min(dezenas, esperado + 2);
        proximo[c.id] = `${lo}-${hi}`;
      }
    }
    setCategoriasInputs(proximo);
  };

  const validarCategorias = (): string | null => {
    const pattern = /^\d+(-\d+)?$/;
    for (const c of categoriasDefs) {
      const v = (categoriasInputs[c.id] ?? '').trim();
      if (v === '') continue;
      if (!pattern.test(v)) return `Formato inválido em "${c.label}". Use "min" ou "min-max", ex.: 2-5`;
    }
    return null;
  };

  const usarAnaliseRepetidos = () => {
    if (repetidosItens.length === 0) {
      setError('Análise de repetições indisponível. Recarregue o dashboard.');
      return;
    }
    setRepetidosInputs(repetidosItens.map(item => `${item.p25}-${item.p75}`));
  };

  const validarRepetidos = (): string | null => {
    const pattern = /^\d+(-\d+)?$/;
    for (let i = 0; i < repetidosItens.length; i++) {
      const v = (repetidosInputs[i] ?? '').trim();
      if (v === '') continue;
      if (!pattern.test(v)) return `Formato inválido em "${REPETIDOS_LABELS[i]}". Use "min" ou "min-max", ex.: 8-10`;
    }
    return null;
  };

  const validarColunas = (): string | null => {
    if (!colunasInputs.some(v => v.trim() !== '')) return null;
    if (!colunasSets) return 'Dados de previsão posicional indisponíveis. Recarregue o dashboard.';
    const pattern = /^\d+(-\d+)?$/;
    for (const v of colunasInputs) {
      if (v.trim() === '') continue;
      if (!pattern.test(v.trim())) return 'Formato inválido nas colunas posicionais. Use "min" ou "min-max", ex.: 7-8';
    }
    return null;
  };

  const toggleNumero = useCallback((n: number) => {
    const atual = estados[n] || 'normal';
    const totalFixos = Object.values(estados).filter(e => e === 'fixo').length;
    const totalExcluidos = Object.values(estados).filter(e => e === 'excluido').length;
    // Uma aposta tem `dezenas` números: fixar mais que (dezenas - 1) deixaria a
    // aposta sem nenhuma dezena livre, e excluir mais que (total - dezenas)
    // deixaria o universo menor que a própria aposta. Vale para qualquer
    // loteria (Lotofácil: 14 fixos / 10 exclusões; Mega-Sena: 5 / 54).
    const maxFixos = Math.max(0, dezenas - 1);
    const maxExcluidos = Math.max(0, cfg.total_numeros - dezenas);

    if (atual === 'normal' && totalFixos >= maxFixos) {
      setLoteFeedback({
        tipo: 'erro',
        texto: `Máximo de ${maxFixos} número(s) para fixar em ${cfg.nome_jogo}.`,
      });
      return;
    }
    if (atual === 'fixo' && totalExcluidos >= maxExcluidos) {
      setLoteFeedback({
        tipo: 'erro',
        texto: `Máximo de ${maxExcluidos} número(s) para excluir em ${cfg.nome_jogo}.`,
      });
      return;
    }

    setEstados(prev => {
      const estadoAtual = prev[n] || 'normal';
      let proximo: NumeroEstado;
      if (estadoAtual === 'normal') proximo = 'fixo';
      else if (estadoAtual === 'fixo') proximo = 'excluido';
      else proximo = 'normal';
      return { ...prev, [n]: proximo };
    });
    setFixosPosicoes(prev => {
      if (!(n in prev)) return prev;
      const copy = { ...prev };
      delete copy[n];
      return copy;
    });
    setExcluidosPosicoes(prev => {
      if (!(n in prev)) return prev;
      const copy = { ...prev };
      delete copy[n];
      return copy;
    });
  }, [estados, dezenas, cfg]);

  /**
   * Garante o invariante de fixos/excluídos mesmo quando o guarda acima não vê o
   * estado mais recente (cliques rápidos em sequência) ou quando `dezenas`
   * diminui depois da seleção. Sem isso, o app aceitaria mais fixos do que a
   * aposta comporta e a geração ficaria impossível.
   */
  useEffect(() => {
    const maxFixos = Math.max(0, dezenas - 1);
    const maxExcluidos = Math.max(0, cfg.total_numeros - dezenas);
    setEstados(prev => {
      const fixos = Object.keys(prev).filter(k => prev[Number(k)] === 'fixo');
      const excluidos = Object.keys(prev).filter(k => prev[Number(k)] === 'excluido');
      if (fixos.length <= maxFixos && excluidos.length <= maxExcluidos) return prev;
      const proximo = { ...prev };
      for (const k of fixos.slice(maxFixos)) delete proximo[Number(k)];
      for (const k of excluidos.slice(maxExcluidos)) delete proximo[Number(k)];
      return proximo;
    });
  }, [estados, dezenas, cfg.total_numeros]);

  const togglePosicaoFixo = useCallback((n: number, p: number) => {
    setFixosPosicoes(prev => {
      const atuais = prev[n] || [];
      const proximas = atuais.includes(p) ? atuais.filter(x => x !== p) : [...atuais, p];
      return { ...prev, [n]: proximas };
    });
  }, []);

  const toggleExclusaoPosicao = useCallback((n: number, p: number) => {
    setExcluidosPosicoes(prev => {
      const atuais = prev[n] || [];
      const proximas = atuais.includes(p) ? atuais.filter(x => x !== p) : [...atuais, p];
      return { ...prev, [n]: proximas };
    });
  }, []);

  const limparSelecao = useCallback(() => {
    setEstados({});
    setFixosPosicoes({});
    setExcluidosPosicoes({});
    setLoteFeedback(null);
  }, []);

  /**
   * Aplica uma quantidade de números de uma vez: sorteia N números entre os
   * disponíveis e marca todos como fixos (ou excluídos). Substitui a seleção
   * do modo escolhido; 0 ou vazio limpa. Números do outro modo não entram no
   * sorteio e restrições de posição antigas deixam de valer.
   *
   * Quando `loteOtimizado` está ativo, em vez de sortear aleatoriamente, escolhe
   * os números com maior score (fixar) ou menor score (excluir) com base em
   * frequência, ciclo, previsão posicional e repetição recente.
   */
  const aplicarLote = useCallback(() => {
    const bruto = loteQuantidade.trim();
    const total = cfg.total_numeros;
    const todos = Array.from({ length: total }, (_, i) => i + cfg.numero_minimo);
    const fixosAtuais = Object.entries(estados)
      .filter(([, e]) => e === 'fixo')
      .map(([n]) => Number(n));
    const excluidosAtuais = Object.entries(estados)
      .filter(([, e]) => e === 'excluido')
      .map(([n]) => Number(n));
    const opostos = loteModo === 'fixo' ? excluidosAtuais : fixosAtuais;
    const bloqueados = new Set(opostos);
    const disponiveis = todos.filter(n => !bloqueados.has(n));
    // Mesmo limite exibido na UI: fixar até (dezenas - 1) e excluir até
    // (total - dezenas), sempre respeitando o que já está marcado no outro modo.
    // Sem teto fixo de 14 — ele só fazia sentido para a Lotofácil e barrava a
    // exclusão na Mega-Sena (60 - 6 = 54).
    const limite = loteModo === 'fixo'
      ? Math.max(0, Math.min(dezenas - 1, disponiveis.length))
      : Math.max(0, Math.min(total - dezenas, disponiveis.length));
    const rotulo = loteModo === 'fixo' ? 'fixo(s)' : 'excluído(s)';
    const acao = loteModo === 'fixo' ? 'fixar' : 'excluir';
    const modoTexto = loteOtimizado ? 'otimizado(s)' : 'sorteado(s)';

    const quantidade = bruto === '' ? 0 : Number(bruto);
    if (!Number.isInteger(quantidade) || quantidade < 0) {
      setLoteFeedback({
        tipo: 'erro',
        texto: `Informe uma quantidade inteira de 0 a ${limite} para ${acao}.`,
      });
      return;
    }

    const scores = loteOtimizado
      ? calcularScoresNumeros(todos, {
          numerosQuentes,
          numerosMornos,
          numerosFrios,
          ciclos,
          previsaoPosicional,
          numerosSorteadosAtual,
        })
      : {};

    // Aplica a seleção final (dezenas já resolvidas), venha ela de dezenas
    // soltas ou de colunas/linhas inteiras.
    const aplicarSelecao = (escolhidos: number[]) => {
      setEstados(prev => {
        const proximo = { ...prev };
        for (const [chave, valor] of Object.entries(proximo)) {
          if (valor === loteModo) delete proximo[Number(chave)];
        }
        for (const n of escolhidos) proximo[n] = loteModo;
        return proximo;
      });
      setFixosPosicoes(prev => {
        if (loteModo === 'fixo') return {};
        const copia = { ...prev };
        for (const n of escolhidos) delete copia[n];
        return copia;
      });
      setExcluidosPosicoes(prev => {
        if (loteModo === 'excluido') return {};
        const copia = { ...prev };
        for (const n of escolhidos) delete copia[n];
        return copia;
      });
    };

    if (loteUnidade === 'dezena') {
      if (quantidade > limite) {
        setLoteFeedback({
          tipo: 'erro',
          texto: `Máximo de ${limite} número(s) para ${acao}.`,
        });
        return;
      }
      const escolhidos = selecionarNumerosLote(disponiveis, quantidade, loteOtimizado, scores, loteModo);
      aplicarSelecao(escolhidos);
      setLoteFeedback({
        tipo: 'ok',
        texto: escolhidos.length === 0
          ? `Seleção de ${rotulo} limpa.`
          : `${escolhidos.length} ${rotulo} ${modoTexto}: ${escolhidos.join(', ')}.`,
      });
      return;
    }

    // --- Colunas ou linhas inteiras da grade --------------------------------
    const nomeUnidade = loteUnidade === 'coluna' ? 'coluna' : 'linha';
    const prefixo = loteUnidade === 'coluna' ? 'C' : 'L';
    // Só entram casas 100% livres: uma coluna que contém dezena do outro modo
    // não pode ser marcada inteira sem apagar a marcação existente.
    const grupos = gruposDaGrade(todos, colunasDaGrade(total), loteUnidade)
      .filter(g => g.numeros.every(n => !bloqueados.has(n)));

    if (quantidade > grupos.length) {
      const livres = grupos.length === 1 ? 'livre' : 'livres';
      setLoteFeedback({
        tipo: 'erro',
        texto: `Só há ${grupos.length} ${nomeUnidade}${grupos.length === 1 ? '' : 's'} ${livres} para ${acao}.`,
      });
      return;
    }

    const mediaScore = (g: GrupoGrade) =>
      g.numeros.length === 0
        ? 0
        : g.numeros.reduce((soma, n) => soma + (scores[n] ?? 0), 0) / g.numeros.length;

    const escolhidosGrupos = loteOtimizado
      ? [...grupos]
          .sort((a, b) => (loteModo === 'fixo'
            ? mediaScore(b) - mediaScore(a)
            : mediaScore(a) - mediaScore(b)))
          .slice(0, quantidade)
      : sortearSubconjunto(grupos, quantidade);

    const escolhidos = escolhidosGrupos.flatMap(g => g.numeros).sort((a, b) => a - b);
    if (escolhidos.length > limite) {
      const tamanho = escolhidosGrupos[0]?.numeros.length ?? 1;
      const maxGrupos = Math.floor(limite / tamanho);
      const pluralErro = escolhidosGrupos.length === 1 ? nomeUnidade : `${nomeUnidade}s`;
      setLoteFeedback({
        tipo: 'erro',
        texto: `${escolhidos.length} dezenas em ${escolhidosGrupos.length} ${pluralErro} passam do máximo de ${limite} para ${acao} (até ${maxGrupos} ${maxGrupos === 1 ? nomeUnidade : `${nomeUnidade}s`}).`,
      });
      return;
    }

    aplicarSelecao(escolhidos);
    const n = escolhidosGrupos.length;
    const nomePlural = n === 1 ? nomeUnidade : `${nomeUnidade}s`;
    const verbo = loteOtimizado
      ? (n === 1 ? 'otimizada' : 'otimizadas')
      : (n === 1 ? 'sorteada' : 'sorteadas');
    setLoteFeedback({
      tipo: 'ok',
      texto: n === 0
        ? `Seleção de ${nomeUnidade}s limpa.`
        : `${n} ${nomePlural} ${verbo}: ${escolhidosGrupos.map(g => `${prefixo}${g.id}`).join(', ')} · ${escolhidos.length} dezenas.`,
    });
    // Mantém o valor digitado no box para que o usuário possa reaplicar ou ajustar.
  }, [loteQuantidade, loteModo, loteOtimizado, loteUnidade, estados, dezenas, cfg, numerosQuentes, numerosMornos, numerosFrios, ciclos, previsaoPosicional, numerosSorteadosAtual]);

  const toggleEstrategia = useCallback((e: string) => {
    setEstrategiasFiltro(prev => {
      const marcada = prev.includes(e);
      const proximo = marcada ? prev.filter(x => x !== e) : [...prev, e];
      if (!marcada && quantidade === 0) setQuantidade(50);
      return proximo;
    });
  }, [quantidade]);

  const jogosFiltrados = useMemo(() => {
    if (!jogos) return null;
    if (estrategiasFiltro.length === 0) return jogos;
    return jogos.filter(j => estrategiasFiltro.includes(j.estrategia));
  }, [jogos, estrategiasFiltro]);

  const gerar = useCallback(async () => {
    const colunasErr = validarColunas();
    if (colunasErr) {
      setError(colunasErr);
      return;
    }
    if (temComparativo && comparativoInputs.some(v => v.trim() !== '' && !/^\d+(-\d+)?$/.test(v.trim()))) {
      setError('Formato inválido no filtro comparativo. Use "min-max" ou "min", ex.: 2-5');
      return;
    }
    const categoriasErr = validarCategorias();
    if (categoriasErr) {
      setError(categoriasErr);
      return;
    }
    const repetidosErr = validarRepetidos();
    if (repetidosErr) {
      setError(repetidosErr);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const seed = Date.now();
      const params = new URLSearchParams();
      params.set('loteria', loteria);
      params.set('n', String(quantidade));
      params.set('seed', String(seed));
      params.set('dezenas', String(dezenas));
      if (cfg.mes_sorte) params.set('mes', String(mesSorte));
      if (fixos.length > 0) params.set('fixos', fixos.join(','));
      if (excluidosCompletos.length > 0) params.set('excluidos', excluidosCompletos.join(','));
      if (concursoBase !== undefined) params.set('concurso', String(concursoBase));
      if (fixos.length > 0 && fixosPosicoesStr) params.set('fixos_posicoes', fixosPosicoesStr);
      if (excluidosPosicoesStr) params.set('excluidos_posicoes', excluidosPosicoesStr);
      if (temColunas) {
        params.set('colunas_posicionais', colunasPosicionaisStr);
        params.set('colunas_sets', colunasSetsStr);
      }
      if (temLinhas) params.set('linhas_sets', linhasSetsStr);
      if (temComparativo) params.set('comparativo', comparativoStr);
      if (temCategorias) {
        params.set('categorias', categoriasRangesStr);
        params.set('categorias_sets', categoriasSetsStr);
      }
      if (temRepetidos) {
        params.set('repetidos', repetidosRangesStr);
        params.set('repetidos_sets', repetidosSetsStr);
      }
      if (ordenacao !== 'aleatorio') {
        params.set('ordenacao', ordenacao);
        if (scoreSetsStr) params.set('score_sets', scoreSetsStr);
      }
      if (estrategiasFiltro.length > 0) params.set('estrategias', estrategiasFiltro.join(','));

      const res = await fetch(`/api/jogos-diversos?${params.toString()}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Erro ao gerar jogos');
      setJogos(data.jogos);
      setEstatisticas(data.estatisticas);
      setCicloAtual(data.ciclo_atual);
      setEstimativaTotal(data.estimativa_total ?? null);
      setModoTodas(data.modo_todas ?? false);
      if (typeof data.dezenas === 'number') setDezenas(data.dezenas);
      if (onFiltrosAplicados) {
        const dezenasAplicadas = typeof data.dezenas === 'number' ? data.dezenas : dezenas;
        const categorias = [
          ...categoriasDefs
            .filter(c => (categoriasInputs[c.id] ?? '').trim() !== '')
            .map(c => {
              const valor = (categoriasInputs[c.id] ?? '').trim();
              return { label: c.label, numeros: c.set, ...parseFaixa(valor) };
            }),
          ...repetidosItens
            .map((item, i) => ({ item, valor: (repetidosInputs[i] ?? '').trim(), label: REPETIDOS_LABELS[i] }))
            .filter(x => x.valor !== '')
            .map(x => ({ label: `Repetidos · ${x.label}`, numeros: x.item.numeros, ...parseFaixa(x.valor) })),
        ];
        onFiltrosAplicados({
          loteria,
          concursoBase: concursoBase ?? concursoAtual,
          geradoEm: new Date().toISOString(),
          jogosGerados: data.jogos.length,
          dezenas: dezenasAplicadas,
          numerosSorteados: cfg.colunas_resultado.length,
          totalNumeros: cfg.total_numeros,
          numeroMinimo: cfg.numero_minimo,
          baseComparativo: numerosSorteadosAtual,
          fixos,
          excluidos: excluidosCompletos,
          colunasPosicionais: temColunas ? parseColunasPosicionais(colunasPosicionaisStr, colunasSetsStr) : undefined,
          dominiosPosicionais: temLinhas ? linhasSetsArray : undefined,
          filtroComparativo: temComparativo ? parseFiltroComparativo(comparativoStr) : undefined,
          categorias,
          fixosPosicoes: fixos.length > 0 ? parseFixosPosicoes(fixosPosicoesStr) : undefined,
          excluidosPosicoes: parseExcluidosPosicoes(excluidosPosicoesStr),
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao gerar jogos');
    } finally {
      setProgresso(100);
      setTimeout(() => setLoading(false), 450);
    }
  }, [loteria, quantidade, dezenas, fixos, excluidos, excluidosCompletos, concursoBase, temColunas, colunasPosicionaisStr, colunasSetsStr, temLinhas, linhasSetsStr, validarColunas, temComparativo, comparativoStr, temCategorias, categoriasRangesStr, categoriasSetsStr, categoriasDefs, categoriasInputs, temRepetidos, repetidosRangesStr, repetidosSetsStr, repetidosItens, repetidosInputs, ordenacao, scoreSetsStr, fixosPosicoesStr, excluidosPosicoesStr, estrategiasFiltro, numerosSorteadosAtual, concursoAtual, onFiltrosAplicados, cfg.colunas_resultado.length, cfg.total_numeros, cfg.numero_minimo, cfg.mes_sorte, mesSorte]);

  const exportarTodas = useCallback(async () => {
    const colunasErr = validarColunas();
    if (colunasErr) {
      setError(colunasErr);
      return;
    }
    if (temComparativo && comparativoInputs.some(v => v.trim() !== '' && !/^\d+(-\d+)?$/.test(v.trim()))) {
      setError('Formato inválido no filtro comparativo. Use "min-max" ou "min", ex.: 2-5');
      return;
    }
    const categoriasErr = validarCategorias();
    if (categoriasErr) {
      setError(categoriasErr);
      return;
    }
    const repetidosErr = validarRepetidos();
    if (repetidosErr) {
      setError(repetidosErr);
      return;
    }
    setExporting(true);
    setError(null);
    try {
      const seed = Date.now();
      const params = new URLSearchParams();
      params.set('loteria', loteria);
      params.set('seed', String(seed));
      params.set('dezenas', String(dezenas));
      if (cfg.mes_sorte) params.set('mes', String(mesSorte));
      if (fixos.length > 0) params.set('fixos', fixos.join(','));
      if (excluidosCompletos.length > 0) params.set('excluidos', excluidosCompletos.join(','));
      if (concursoBase !== undefined) params.set('concurso', String(concursoBase));
      if (fixos.length > 0 && fixosPosicoesStr) params.set('fixos_posicoes', fixosPosicoesStr);
      if (excluidosPosicoesStr) params.set('excluidos_posicoes', excluidosPosicoesStr);
      if (temColunas) {
        params.set('colunas_posicionais', colunasPosicionaisStr);
        params.set('colunas_sets', colunasSetsStr);
      }
      if (temLinhas) params.set('linhas_sets', linhasSetsStr);
      if (temComparativo) params.set('comparativo', comparativoStr);
      if (temCategorias) {
        params.set('categorias', categoriasRangesStr);
        params.set('categorias_sets', categoriasSetsStr);
      }
      if (temRepetidos) {
        params.set('repetidos', repetidosRangesStr);
        params.set('repetidos_sets', repetidosSetsStr);
      }
      if (ordenacao !== 'aleatorio') {
        params.set('ordenacao', ordenacao);
        if (scoreSetsStr) params.set('score_sets', scoreSetsStr);
      }
      if (estrategiasFiltro.length > 0) params.set('estrategias', estrategiasFiltro.join(','));

      const res = await fetch(`/api/jogos-diversos/export?${params.toString()}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Erro ${res.status} ao exportar`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `jogos-${loteria}-${dezenas}dezenas-todas-${new Date().toISOString().slice(0, 10)}.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao exportar jogos');
    } finally {
      setExporting(false);
    }
  }, [loteria, dezenas, fixos, excluidos, excluidosCompletos, concursoBase, temColunas, colunasPosicionaisStr, colunasSetsStr, temLinhas, linhasSetsStr, validarColunas, temComparativo, comparativoStr, comparativoInputs, temCategorias, categoriasRangesStr, categoriasSetsStr, temRepetidos, repetidosRangesStr, repetidosSetsStr, repetidosItens, ordenacao, scoreSetsStr, fixosPosicoesStr, excluidosPosicoesStr, estrategiasFiltro, cfg.mes_sorte, mesSorte]);

  const gerarFechamento = useCallback(async (opcoes?: {
    otimizarSeeds?: boolean;
    quantidadeSeeds?: number;
    criterioOtimizacao?: 'custo' | 'diversidade' | 'backtest' | 'equilibrado';
  }) => {
    abortFechamentoRef.current?.abort();
    const controller = new AbortController();
    abortFechamentoRef.current = controller;

    setGerandoFechamento(true);
    setError(null);
    setOtimizacaoInfo(null);
    setApostasFechamento([]);
    setCoberturaFechamento(null);
    setCustoFechamento(null);
    setBacktestFechamento(null);
    setFechamentoSeedUsado(null);
    setFechamentoSeedsTestadas(null);
    setFechamentoLimiteInferior(null);
    setFechamentoCoberturaRestante(null);
    setFechamentoPisoCondicional(null);
    setFechamentoAviso(null);
    setFechamentoFiltroInfo(null);
    setCpSatInfo(null);
    setCoverConhecidoInfo(null);
    setLottoDesignInfo(null);
    setLottoIgnoradoInfo(null);
    try {
      const fixosSelecionados = Object.entries(estados)
        .filter(([, e]) => e === 'fixo')
        .map(([n]) => Number(n));
      const excluidosSelecionados = Object.entries(estados)
        .filter(([, e]) => e === 'excluido')
        .map(([n]) => Number(n));

      const filtrosCategoriasTela = categoriasDefs
        .filter(c => (categoriasInputs[c.id] ?? '').trim() !== '')
        .map(c => {
          const faixa = parseFaixa(categoriasInputs[c.id] ?? '');
          return { numeros: c.set, min: faixa.min, max: faixa.max };
        });
      const filtrosCategorias = (aplicarFiltrosCategorias || fechamentoAplicarFiltrosTela)
        ? filtrosCategoriasTela
        : [];

      const regexFiltro = /^\d+(-\d+)?$/;
      if (fechamentoAplicarFiltrosTela) {
        if (temColunas) {
          const err = validarColunas();
          if (err) { setError(err); return; }
        }
        if (temComparativo && comparativoInputs.some(v => v.trim() !== '' && !regexFiltro.test(v.trim()))) {
          setError('Formato inválido no filtro comparativo. Use "min-max" ou "min", ex.: 2-5');
          return;
        }
        if (temRepetidos && repetidosInputs.some((v, i) => (repetidosItens[i] && v.trim() !== '' && !regexFiltro.test(v.trim())))) {
          setError('Formato inválido no filtro de repetidos. Use "min-max" ou "min", ex.: 2-5');
          return;
        }
      }

      const filtrosExtras = fechamentoAplicarFiltrosTela
        ? {
            colunas: temColunas ? parseColunasPosicionais(colunasPosicionaisStr, colunasSetsStr) : undefined,
            linhas: temLinhas ? linhasSetsArray : undefined,
            comparativo: temComparativo ? parseFiltroComparativo(comparativoStr) : undefined,
            baseComparativo: numerosSorteadosAtual,
            repetidos3: temRepetidos
              ? repetidosItens
                  .map((item, i) => ({ numeros: item.numeros, valor: (repetidosInputs[i] ?? '').trim() }))
                  .filter(x => x.valor !== '')
                  .map(x => ({ numeros: x.numeros, ...parseFaixa(x.valor) }))
              : undefined,
          }
        : undefined;

      const faixaRepetidas = parseFaixa(fechamentoRepetidasFaixa || '0-15');
      const repetidas = fechamentoFiltroRepetidasAtivo && numerosSorteadosAtual.length > 0
        ? { numeros: numerosSorteadosAtual, min: faixaRepetidas.min, max: faixaRepetidas.max }
        : undefined;

      const res = await fetch('/api/fechamento', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          fixos: fixosSelecionados,
          excluidos: excluidosSelecionados,
          filtrosCategorias,
          filtrosExtras,
          k: fechamentoK,
          t: fechamentoT,
          garantiaCondicional: fechamentoGarantiaCondicional && fixosSelecionados.length > 0,
          maxApostas: fechamentoMax,
          seed: fechamentoSeed,
          otimizado: fechamentoOtimizado,
          usarLottoDesign: fechamentoUsarLottoDesign,
          coberturaCompleta: fechamentoCoberturaCompleta,
          ...(fechamentoAmostra > 0 ? { amostraPorPasso: fechamentoAmostra } : {}),
          buscarMelhorSeed: fechamentoSeeds,
          priorizarPremios: fechamentoPriorizarPremios,
          removerRedundantes: fechamentoRemoverRedundantes,
          usarCpSat: fechamentoUsarCpSat,
          solver: fechamentoSolver,
          cpSatTimeLimit: fechamentoCpSatTime,
          repetidas,
          loteria,
          limiteTempoMs: 120000,
          ...(opcoes?.otimizarSeeds
            ? {
                otimizarSeeds: true,
                quantidadeSeeds: opcoes.quantidadeSeeds ?? 20,
                criterioOtimizacao: opcoes.criterioOtimizacao ?? 'custo',
              }
            : {}),
        }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Erro ${res.status} ao gerar fechamento`);
      }
      const data = await res.json();
      if (!data.sucesso) throw new Error(data.error || 'Erro ao gerar fechamento');

      setApostasFechamento(data.apostas ?? []);
      setCoberturaFechamento(data.cobertura ?? null);
      setCustoFechamento(data.custo ?? null);
      setFechamentoSeedUsado(data.seedUsado ?? null);
      setFechamentoSeedsTestadas(data.seedsTestadas ?? null);
      setFechamentoLimiteInferior(data.limiteInferior ?? null);
      setFechamentoCoberturaRestante(data.coberturaRestante ?? null);
      setFechamentoPisoCondicional(data.pisoCondicional ?? null);
      setFechamentoAviso(data.aviso ?? null);
      setFechamentoFiltroInfo(data.filtroRepetidas ?? null);
      setBacktestFechamento(data.backtest ?? null);
      setCpSatInfo(data.cpSat ?? null);
      setCoverConhecidoInfo(data.coverConhecido ?? null);
      setLottoDesignInfo(data.lottoDesign ?? null);
      setLottoIgnoradoInfo(data.lottoIgnorado ?? null);
      setOtimizacaoInfo(data.otimizacao ?? null);
      setFechamentoTInfo({
        garantiaCondicional: Boolean(data.garantiaCondicional),
        tEfetivo: Number(data.tEfetivo ?? fechamentoT),
        t: Number(data.t ?? fechamentoT),
      });
    } catch (err) {
      if ((err as any)?.name === 'AbortError') {
        setError('Geração cancelada.');
      } else {
        setError(err instanceof Error ? err.message : 'Erro ao gerar fechamento');
      }
    } finally {
      if (abortFechamentoRef.current === controller) abortFechamentoRef.current = null;
      setGerandoFechamento(false);
    }
  }, [estados, categoriasDefs, categoriasInputs, aplicarFiltrosCategorias, fechamentoK, fechamentoT, fechamentoMax, fechamentoSeed, fechamentoOtimizado, fechamentoUsarLottoDesign, fechamentoCoberturaCompleta, fechamentoSeeds, fechamentoAmostra, fechamentoUsarCpSat, fechamentoSolver, fechamentoCpSatTime, fechamentoPriorizarPremios, fechamentoRemoverRedundantes, fechamentoGarantiaCondicional, fechamentoFiltroRepetidasAtivo, fechamentoRepetidasFaixa, numerosSorteadosAtual, loteria]);

  const cancelarFechamento = useCallback(() => {
    abortFechamentoRef.current?.abort();
  }, []);

  const rodarBacktest = useCallback(async () => {
    if (!apostasFechamento.length) return;
    setRodandoBacktest(true);
    setError(null);
    try {
      const res = await fetch('/api/fechamento/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apostas: apostasFechamento,
          k: fechamentoK,
          loteria,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.sucesso) throw new Error(data.error || 'Erro ao rodar backtest');
      setBacktestFechamento(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao rodar backtest');
    } finally {
      setRodandoBacktest(false);
    }
  }, [apostasFechamento, fechamentoK, loteria]);

  const getNumeroClasses = (n: number) => {
    const estado = estados[n] || 'normal';
    if (estado === 'fixo') {
      return 'bg-emerald-500/30 text-emerald-100 border-emerald-500/60 ring-1 ring-emerald-500/50';
    }
    if (estado === 'excluido') {
      return 'bg-hot/20 text-hot/70 border-hot/40 line-through opacity-60';
    }
    return 'bg-[rgba(129,140,248,0.12)] text-accent-2 border-[rgba(129,140,248,0.25)] hover:bg-[rgba(129,140,248,0.22)]';
  };

  const totalNumeros = cfg.total_numeros;
  const colunasGrade = colunasDaGrade(totalNumeros);
  const gridClass = GRID_CLASS_POR_COLUNAS[colunasGrade];
  const gridMaxW = totalNumeros <= 25 ? 280 : totalNumeros <= 31 ? 400 : 480;
  const btnSize = totalNumeros <= 25 ? 'w-10 h-10 text-sm' : totalNumeros <= 50 ? 'w-9 h-9 text-xs' : 'w-8 h-8 text-xs';
  const cicloGridClass = gridClass;
  const cicloMaxW = gridMaxW + 40;
  const numeroMin = cfg.numero_minimo;
  const numeroMax = cfg.numero_maximo;
  const numeros = Array.from({ length: totalNumeros }, (_, i) => i + numeroMin);
  // Limites do lote consideram o que já está marcado no outro modo: um número
  // não pode ser fixo e excluído ao mesmo tempo, e a exclusão não pode deixar
  // o universo menor que o necessário para montar um jogo (total - dezenas).
  // Não há teto fixo: Lotofácil permite 10 exclusões (25 - 15), Mega-Sena 54
  // (60 - 6), Lotomania 50 (100 - 50). O mesmo cálculo vale para fixar.
  const limiteLoteFixo = Math.max(0, Math.min(dezenas - 1, totalNumeros - excluidos.length));
  const limiteLoteExcluido = Math.max(0, Math.min(totalNumeros - dezenas, totalNumeros - fixos.length));

  // Geometria do lote por coluna/linha: quantas dezenas cada casa carrega e
  // quantas casas cabem dentro do limite de dezenas (o limite real é numérico).
  const gruposLote = loteUnidade === 'dezena'
    ? []
    : gruposDaGrade(numeros, colunasDaGrade(totalNumeros), loteUnidade);
  const tamanhosGrupo = [...new Set(gruposLote.map(g => g.numeros.length))].sort((a, b) => a - b);
  const tamanhoGrupoTexto = tamanhosGrupo.length === 0
    ? ''
    : tamanhosGrupo.length === 1
      ? String(tamanhosGrupo[0])
      : `${tamanhosGrupo[0]}–${tamanhosGrupo[tamanhosGrupo.length - 1]}`;
  const limiteNumerosLote = loteModo === 'fixo' ? limiteLoteFixo : limiteLoteExcluido;
  const limiteLoteExibido = loteUnidade === 'dezena'
    ? limiteNumerosLote
    : Math.floor(limiteNumerosLote / Math.max(1, tamanhosGrupo[tamanhosGrupo.length - 1] ?? 1));
  const labelUnidade = loteUnidade === 'dezena'
    ? 'dezena(s)'
    : loteUnidade === 'coluna'
      ? 'coluna(s)'
      : 'linha(s)';
  const precoUnit = calcularPrecoAposta(loteria, dezenas);
  const coberturaCompletaV = Math.max(0, cfg.total_numeros - fixos.length - excluidos.length);
  const coberturaCompletaK = fechamentoK - fixos.length;
  const coberturaCompletaTotal = coberturaCompletaK > 0 && coberturaCompletaV >= coberturaCompletaK
    ? combinacoes(coberturaCompletaV, coberturaCompletaK)
    : 0;
  const coberturaCompletaPreco = calcularPrecoAposta(loteria, fechamentoK);
  const coberturaCompletaCusto = coberturaCompletaTotal * coberturaCompletaPreco;
  const coberturaCompletaValida = fechamentoCoberturaCompleta
    && fechamentoT === fechamentoK
    && coberturaCompletaTotal > 0
    && coberturaCompletaTotal <= LIMITE_COBERTURA_COMPLETA;
  const mostraSeletorDezenas = opcoesDezenas.length > 1;

  return (
    <div className="rounded-2xl border border-[rgba(129,140,248,0.15)] p-5 sm:p-6 mb-6"
      style={{ background: 'linear-gradient(135deg, rgba(129,140,248,0.06), rgba(52,211,153,0.03))' }}>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div>
          <h3 className="text-lg font-semibold text-ink">Jogos Diversificados</h3>
          <p className="text-xs text-muted mt-1">
            Múltiplas estratégias (atraso, quentes, persistência, ciclo) para distribuir risco.
            {concursoBase !== undefined && (
              <span className="ml-1 text-accent-2">
                Alvo: concurso {concursoBase + 1}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {mostraSeletorDezenas && (
            <>
              <label className="text-sm text-muted">Dezenas por jogo:</label>
              <select
                value={dezenas}
                onChange={e => setDezenas(parseInt(e.target.value, 10))}
                className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
                title="Quantidade de dezenas de cada jogo gerado"
              >
                {opcoesDezenas.map(d => (
                  <option key={d} value={d} className="bg-[#1a1d2e]">{d}</option>
                ))}
              </select>
              {dezenas > cfg.numeros_por_jogo && (
                <span className="text-xs px-2 py-1 rounded-full bg-accent-2/15 text-[#a5b4fc] border border-[#818cf8]/30">
                  R$ {precoUnit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}/jogo
                </span>
              )}
            </>
          )}
          {cfg.mes_sorte && (
            <>
              <label className="text-sm text-muted">Mês da Sorte:</label>
              <select
                value={String(mesSorte)}
                onChange={e => setMesSorte(e.target.value === 'aleatorio' ? 'aleatorio' : parseInt(e.target.value, 10))}
                className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
                title="Mês marcado na aposta. Acertando o mês sorteado, a Caixa paga R$ 2,50 por combinação de 7 dezenas (bônus independente dos acertos)."
              >
                <option value="aleatorio" className="bg-[#1a1d2e]">Aleatório</option>
                {MESES_SORTE.map((nome, i) => (
                  <option key={nome} value={i + 1} className="bg-[#1a1d2e]">{nome}</option>
                ))}
              </select>
            </>
          )}
          <label className="text-sm text-muted">Quantidade:</label>
          <input
            type="number"
            min={estrategiasFiltro.length > 0 ? 1 : 0}
            value={quantidade}
            onChange={e => setQuantidade(Math.max(estrategiasFiltro.length > 0 ? 1 : 0, parseInt(e.target.value, 10) || (estrategiasFiltro.length > 0 ? 1 : 0)))}
            className="w-24 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
            title={estrategiasFiltro.length > 0 ? 'Com filtro de estratégia, defina uma quantidade (modo "todas as combinações" não se aplica)' : '0 = todas as combinações'}
          />
          {quantidade === 0 && estrategiasFiltro.length === 0 && (
            <span className="text-xs px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-500/30">
              Todas as combinações
            </span>
          )}
          <label className="text-sm text-muted">Ordenação:</label>
          <select
            value={ordenacao}
            onChange={e => setOrdenacao(e.target.value)}
            className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
            title="Aleatório (ordem de geração) · Melhores/Piores por score de análises combinadas · Balanceado (mistura faixas alta/média/baixa)"
          >
            {Object.entries(ORDENACAO_LABEL).map(([k, l]) => (
              <option key={k} value={k} className="bg-[#1a1d2e]">{l}</option>
            ))}
          </select>
          <button
            onClick={gerar}
            disabled={loading}
            className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110 disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
            {loading ? 'Gerando...' : 'Gerar'}
          </button>
          <button
            onClick={() => setModoFechamento(true)}
            disabled={loading || gerandoFechamento}
            className="px-3 py-2 rounded-lg text-sm font-semibold text-[#a5b4fc] border border-[#818cf8]/40 hover:bg-[#818cf8]/10 transition-all disabled:opacity-50">
            Fechamento
          </button>
        </div>
      </div>

      <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
        <div className="flex flex-wrap items-center gap-3 mb-2">
          <span className="text-sm font-semibold text-ink">Filtrar por estratégia</span>
          <span className="text-xs text-muted">
            {estrategiasFiltro.length > 0
              ? 'gerar apenas jogos da(s) estratégia(s) marcada(s)'
              : 'opcional — sem seleção usa todas as estratégias'}
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {Object.entries(ESTRATEGIA_LABEL).map(([key, label]) => {
            const marcada = estrategiasFiltro.includes(key);
            return (
              <label
                key={key}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs cursor-pointer border transition-colors select-none ${
                  marcada
                    ? 'bg-accent/20 text-accent-2 border-accent-2/40'
                    : 'bg-white/5 text-muted border-white/10 hover:text-fg hover:bg-white/10'
                }`}
              >
                <input
                  type="checkbox"
                  checked={marcada}
                  onChange={() => toggleEstrategia(key)}
                  className="accent-[#818cf8]"
                />
                {label}
              </label>
            );
          })}
          {estrategiasFiltro.length > 0 && (
            <button
              onClick={() => setEstrategiasFiltro([])}
              className="px-3 py-1.5 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
            >
              Limpar filtro
            </button>
          )}
        </div>
      </div>

      {previsaoPosicional && (
        <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="text-sm font-semibold text-ink">Colunas Posicionais (Previsão Posicional)</div>
            <div className="text-xs text-muted">
              min-max de números de cada coluna <strong className="text-fg">#1..#5</strong> por jogo. Ex.: <strong className="text-fg">7-8</strong> (min 7, máx 8) ou <strong className="text-fg">3</strong> (mínimo 3, sem limite). Vazio = sem restrição.
            </div>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            {colunasInputs.map((v, i) => (
              <label key={i} className="flex flex-col items-center gap-1">
                <span className="text-[11px] text-muted">
                  #{i + 1}
                  {colunasSets && <span className="ml-1 text-accent-2">({colunasSets[i]?.length ?? 0} nºs)</span>}
                </span>
                <input
                  type="text"
                  inputMode="numeric"
                  value={v}
                  onChange={e => setColunasInputs(prev => prev.map((x, j) => (j === i ? e.target.value : x)))}
                  placeholder="min-max"
                  className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] text-center placeholder:text-muted/90"
                />
              </label>
            ))}
            <button
              onClick={usarPrevisaoColunas}
              disabled={!previsaoColunas || previsaoColunas.length < 5}
              className="px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
              title={previsaoColunas && previsaoColunas.length >= 5
                ? 'Preenche com as faixas P25–P75 de acerto histórico de cada coluna'
                : 'Faixas indisponíveis para esta loteria'}
            >
              Usar previsão da Posicional
            </button>
            <button
              onClick={() => setColunasInputs(['', '', '', '', ''])}
              className="px-3 py-2 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
            >
              Limpar
            </button>
            <div className="flex-1 text-[11px] text-muted leading-relaxed">
              A soma dos mínimos nunca pode ultrapassar as <strong className="text-fg">{dezenas}</strong> dezenas por jogo (a distribuição é adaptada
              automaticamente). Se a soma for menor que o jogo, os números restantes são preenchidos <strong className="text-fg">aleatoriamente</strong>.
              O botão <strong className="text-fg">"Usar previsão da Posicional"</strong> preenche com a faixa central (P25–P75) de quantos
              números de cada coluna costumaram sair nos últimos 100 sorteios.
            </div>
          </div>
        </div>
      )}

      {previsaoPosicional && posicoesLinhas.length > 0 && (
        <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="text-sm font-semibold text-ink">Linhas Posicionais (Domínio por Posição)</div>
            <div className="text-xs text-muted">
              <strong className="text-fg">N1</strong> = menor número do jogo, <strong className="text-fg">{posicoesLinhas[posicoesLinhas.length - 1]}</strong> = maior.
              Clique nos números para definir quem pode ocupar cada posição.
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            {[3, 4, 5].map(top => (
              <button
                key={top}
                onClick={() => aplicarTopLinhas(top)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
                style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
              >
                Top {top}
              </button>
            ))}
            {[0.9, 0.95].map(alvo => (
              <button
                key={alvo}
                onClick={() => aplicarCoberturaLinhas(alvo)}
                className="px-3 py-1.5 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
              >
                Cobertura {Math.round(alvo * 100)}%
              </button>
            ))}
            <button
              onClick={() => setLinhasFiltro({})}
              className="px-3 py-1.5 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
            >
              Limpar linhas
            </button>
            <span className={`text-[11px] ${temLinhas ? 'text-accent-2' : 'text-muted'}`}>
              {temLinhas ? `${linhasSetsArray.reduce((a, s) => a + s.length, 0)} números fixados em ${linhasSetsArray.filter(s => s.length > 0).length} linhas` : 'Nenhuma linha restrita'}
            </span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-2">
            {posicoesLinhas.map(pos => {
              const preds = previsaoPosicional[pos] ?? [];
              const selecionados = linhasFiltro[pos] ?? [];
              const cobertura = coberturaLinha(pos);
              return (
                <div key={pos} className="p-2 rounded-lg bg-white/[0.03] border border-white/10">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[11px] font-semibold text-fg">{pos}</span>
                    <span className={`text-[10px] ${selecionados.length > 0 ? 'text-accent-2' : 'text-muted'}`}>
                      {selecionados.length > 0 ? `cobertura ${(cobertura * 100).toFixed(1)}%` : 'livre'}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {preds.slice(0, 5).map(item => {
                      const ativo = selecionados.includes(item.numero);
                      return (
                        <button
                          key={item.numero}
                          onClick={() => toggleLinha(pos, item.numero)}
                          title={`${(item.prob * 100).toFixed(1)}% de chance histórica nesta posição`}
                          className={`px-1.5 py-1 rounded text-[10px] border transition-colors ${
                            ativo
                              ? 'bg-indigo-500/30 border-indigo-400/60 text-indigo-100'
                              : 'bg-white/5 border-white/10 text-muted hover:text-fg hover:bg-white/10'
                          }`}
                        >
                          <span className="font-semibold">{item.numero}</span>
                          <span className="ml-1 opacity-70">{(item.prob * 100).toFixed(0)}%</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-2 text-[11px] text-muted leading-relaxed">
            Cada linha é uma posição ordenada. Restringir muitas linhas reduz drasticamente as combinações;
            <strong className="text-fg"> Top 3/4/5</strong> aplica o preset às N linhas mais concentradas.
            Linha sem seleção = sem restrição.
          </div>
        </div>
      )}

      <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="text-sm font-semibold text-ink">Filtro Comparativo (Tendência Posicional)</div>
          <div className="text-xs text-muted">
            Cada jogo é comparado posição a posição com o último sorteio: quantas posições ficam ▲ maiores / ▼ menores / = iguais.
            Ex.: <strong className="text-fg">2-5</strong> = a quantidade de iguais no jogo deve ficar entre 2 e 5.
          </div>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          {comparativoInputs.map((v, i) => (
            <label key={i} className="flex flex-col items-center gap-1">
              <span className="text-[11px] text-muted">{['▲ Maiores', '= Iguais', '▼ Menores'][i]}</span>
              <input
                type="text"
                inputMode="numeric"
                value={v}
                onChange={e => setComparativoInputs(prev => prev.map((x, j) => (j === i ? e.target.value : x)))}
                placeholder="min-max"
                className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] text-center placeholder:text-muted/90"
              />
            </label>
          ))}
          <button
            onClick={usarPrevisaoTendencia}
            className="px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
            style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
            title="Preenche com as faixas P25–P75 da previsão da Tendência Posicional"
          >
            Usar previsão da Tendência
          </button>
          <button
            onClick={() => setComparativoInputs(['', '', ''])}
            className="px-3 py-2 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
          >
            Limpar
          </button>
          <div className="flex-1 text-[11px] text-muted leading-relaxed">
            Vazio = sem restrição na categoria. O botão <strong className="text-fg">"Usar previsão"</strong> usa as faixas
            centrais (P25–P75) calculadas na Tendência Posicional.
            {dezenas !== cfg.numeros_por_jogo && (
              <div className="mt-1 text-amber-200/80">
                Jogo com {dezenas} dezenas: o comparativo é aplicado às primeiras {cfg.numeros_por_jogo} posições
                (o sorteio tem {cfg.numeros_por_jogo} dezenas).
              </div>
            )}
          </div>
        </div>
      </div>

      {categoriasDefs.length > 0 && (
        <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="text-sm font-semibold text-ink">Filtro por Categorias (Grupos &amp; Frequência)</div>
            <div className="text-xs text-muted">
              Min/max de quantas dezenas de cada categoria o jogo deve conter.
              Ex.: <strong className="text-fg">2-5</strong> = entre 2 e 5 dezenas da categoria. Vazio = sem restrição.
            </div>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            {categoriasDefs.map(c => (
              <label key={c.id} className="flex flex-col items-center gap-1">
                <span className="text-[11px]" style={{ color: c.cor }}>
                  {c.label}
                  <span className="ml-1 opacity-70">({c.set.length})</span>
                </span>
                <input
                  type="text"
                  inputMode="numeric"
                  value={categoriasInputs[c.id] ?? ''}
                  onChange={e => setCategoriasInputs(prev => ({ ...prev, [c.id]: e.target.value }))}
                  placeholder="min-max"
                  className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] text-center placeholder:text-muted/90"
                />
              </label>
            ))}
            <button
              onClick={usarAnaliseCategorias}
              className="px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
              title="Preenche os min/max com base na análise (Grupos: min-máx histórico; Frequência: bandas recentes)"
            >
              Usar análise
            </button>
            <button
              onClick={() => setCategoriasInputs({})}
              className="px-3 py-2 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
            >
              Limpar
            </button>
            <div className="flex-1 text-[11px] text-muted leading-relaxed">
              Considera as dezenas <strong className="text-fg">presentes no jogo</strong>. Categorias podem se sobrepor
              (uma dezena pode ser, ao mesmo tempo, Grupo A e Quente). Números fixos contam para as categorias.
            </div>
          </div>
        </div>
      )}

      {repetidosItens.length > 0 && (
        <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="text-sm font-semibold text-ink">Filtro de Repetidos (3 Últimos Sorteios)</div>
            <div className="text-xs text-muted">
              Min/max de quantas dezenas do jogo devem repetir de cada um dos 3 últimos sorteios.
              Ex.: <strong className="text-fg">8-10</strong> = entre 8 e 10 dezenas repetidas. Vazio = sem restrição.
            </div>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            {repetidosItens.map((item, i) => (
              <label key={item.rotulo} className="flex flex-col items-center gap-1">
                <span className="text-[11px]" style={{ color: REPETIDOS_CORES[i] }}>
                  {REPETIDOS_LABELS[i]}
                  <span className="ml-1 opacity-70">(C{item.concurso} · {item.numeros.length})</span>
                </span>
                <input
                  type="text"
                  inputMode="numeric"
                  value={repetidosInputs[i] ?? ''}
                  onChange={e => setRepetidosInputs(prev => prev.map((x, j) => (j === i ? e.target.value : x)))}
                  placeholder="min-max"
                  title={`Histórico: ${item.min}-${item.max} · P25–P75: ${item.p25}-${item.p75} · média ${item.media}`}
                  className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] text-center placeholder:text-muted/90"
                />
              </label>
            ))}
            <button
              onClick={usarAnaliseRepetidos}
              className="px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
              title="Preenche com a faixa central (P25–P75) da distribuição histórica de repetições de cada sorteio"
            >
              Usar análise
            </button>
            <button
              onClick={() => setRepetidosInputs(['', '', ''])}
              className="px-3 py-2 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
            >
              Limpar
            </button>
            <div className="flex-1 text-[11px] text-muted leading-relaxed">
              Conta as dezenas <strong className="text-fg">presentes no jogo</strong> que também saíram em cada sorteio.
              A análise usa a distribuição histórica; <strong className="text-fg">"Usar análise"</strong> aplica a faixa
              central (P25–P75). Números fixos contam para os repetidos.
            </div>
          </div>
        </div>
      )}

      <div className="mb-5">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
          <div className="text-sm text-ink">Clique nos números para fixar 🟢 ou excluir 🔴</div>
          <div className="flex flex-wrap items-center gap-2">
            {onConcursoChange && concursosDisponiveis && concursosDisponiveis.length > 0 && (
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] text-muted">Concurso base:</span>
                <SeletorConcursoBase
                  concursos={concursosDisponiveis}
                  value={concursoBase}
                  onChange={aplicarConcursoBase}
                  carregando={carregandoConcurso}
                />
              </div>
            )}
            <button
              onClick={() => setMostrarJanela(v => !v)}
              type="button"
              aria-pressed={mostrarJanela}
              className={`text-xs px-3 py-1 rounded-lg border transition-colors ${
                mostrarJanela
                  ? 'bg-accent/20 text-accent-2 border-accent-2/40'
                  : 'bg-white/5 text-muted border-white/10 hover:text-fg hover:bg-white/10'
              }`}
              title="Mostra na grade quantas vezes cada dezena saiu na janela anterior ao concurso alvo"
            >
              Janela {mostrarJanela ? '✓' : ''}
            </button>
            {mostrarJanela && (
              <>
                <input
                  type="number"
                  min={1}
                  max={500}
                  value={janelaTamanho}
                  onChange={e => {
                    const valor = parseInt(e.target.value, 10);
                    setJanelaTamanho(Number.isFinite(valor) ? Math.max(1, Math.min(500, valor)) : 7);
                  }}
                  className="w-14 px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-fg text-center focus:outline-none focus:border-[#818cf8]"
                  title="Quantidade de concursos na janela"
                  aria-label="Tamanho da janela em concursos"
                />
                <span className="text-[11px] text-muted">
                  {janelaCarregando
                    ? 'calculando...'
                    : janelaErro
                      ? 'indisponível'
                      : janelaDados
                        ? `${janelaDados.primeiroConcursoJanela ?? '—'}–${janelaDados.ultimoConcursoJanela ?? '—'} · alvo ${janelaDados.concursoAlvo}`
                        : `alvo ${concursoAlvoJanela ?? '—'}`}
                </span>
              </>
            )}
            <button
              onClick={limparSelecao}
              className="text-xs px-3 py-1 rounded-lg bg-white/5 text-muted hover:text-fg hover:bg-white/10 transition-colors">
              Limpar seleção
            </button>
          </div>
        </div>
        <div className="flex flex-wrap gap-4 items-start">
        <div className="flex-1 min-w-[300px]">
        <div className={`grid ${gridClass} gap-2`} style={{ maxWidth: gridMaxW }}>
          {numeros.map(n => {
            const sorteado = sorteadosAtualSet.has(n);
            const janelaItem = janelaPorNumero.get(n);
            return (
              <button
                key={n}
                onClick={() => toggleNumero(n)}
                className={`relative ${btnSize} flex items-center justify-center rounded-lg font-bold border transition-all ${getNumeroClasses(n)}`}>
                {n}
                {mostrarJanela && janelaItem && (
                  <span
                    className={`absolute -bottom-1 -right-1 min-w-[15px] h-[15px] px-0.5 rounded-full border text-[8px] font-bold leading-none flex items-center justify-center ${classeBadgeJanela(janelaItem)}`}
                    title={`Saiu ${janelaItem.ocorrencias}x em ${janelaDados?.janelaEfetiva ?? janelaTamanho} concurso(s) da janela anterior ao alvo ${janelaDados?.concursoAlvo ?? concursoAlvoJanela ?? '—'} (${janelaItem.percentual.toFixed(0)}%)`}>
                    {janelaItem.ocorrencias}
                  </span>
                )}
                {sorteado && (
                  <span
                    className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 border border-emerald-600/40 shadow-sm"
                    title="Sorteado no concurso base"
                  />
                )}
              </button>
            );
          })}
        </div>
        <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted">
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500/30 border border-emerald-500/60" /> Fixo</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-hot/20 border border-hot/40" /> Excluído</span>
          <span className="flex items-center gap-1"><span className="relative w-3 h-3 rounded bg-white/5 border border-white/10"><span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 border border-emerald-600/40" /></span> Sorteado no concurso base</span>
          {mostrarJanela && (
            <span className="flex items-center gap-1">
              <span className="min-w-[15px] h-[15px] px-1 rounded-full border border-emerald-400/60 bg-emerald-500/40 text-emerald-50 text-[9px] font-bold flex items-center justify-center">4</span>
              saiu na janela (nº de concursos)
            </span>
          )}
        </div>
        {mostrarJanela && (
          janelaErro ? (
            <div className="mt-2 text-[11px] text-amber-200">
              Janela indisponível: {janelaErro}
            </div>
          ) : janelaDados ? (
            <div className="mt-2 text-[11px] text-muted">
              Janela de <strong className="text-fg">{janelaDados.janelaEfetiva}</strong> concurso(s)
              {janelaDados.primeiroConcursoJanela !== null && janelaDados.ultimoConcursoJanela !== null
                ? ` (${janelaDados.primeiroConcursoJanela} a ${janelaDados.ultimoConcursoJanela})`
                : ''} anterior(es) ao alvo <strong className="text-fg">{janelaDados.concursoAlvo}</strong>. O alvo não entra na contagem.
            </div>
          ) : null
        )}

        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-muted">Em lote:</span>
          <div
            className="flex rounded-lg overflow-hidden border border-white/10"
            role="group"
            aria-label="Unidade do sorteio em lote"
            title="Escolha o que o sorteio em lote move: dezenas soltas, ou a casa inteira da grade (coluna/linha)"
          >
            {([
              ['dezena', 'Dezenas'],
              ['coluna', 'Colunas'],
              ['linha', 'Linhas'],
            ] as const).map(([id, label]) => (
              <button
                key={id}
                type="button"
                onClick={() => {
                  setLoteUnidade(id);
                  setLoteFeedback(null);
                }}
                aria-pressed={loteUnidade === id}
                className={`px-2 py-1.5 transition-colors ${
                  loteUnidade === id
                    ? 'bg-accent/25 text-accent-2 font-semibold'
                    : 'bg-white/5 text-muted hover:text-fg'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <input
            type="text"
            inputMode="numeric"
            value={loteQuantidade}
            onChange={e => {
              setLoteQuantidade(e.target.value.replace(/[^0-9]/g, ''));
              setLoteFeedback(null);
            }}
            onKeyDown={e => {
              if (e.key === 'Enter') aplicarLote();
            }}
            placeholder={`0 a ${limiteLoteExibido}`}
            aria-label={`Quantidade de ${labelUnidade} para sortear em lote`}
            title={loteUnidade === 'dezena'
              ? 'Digite só a quantidade — as dezenas são sorteadas entre as disponíveis'
              : `Digite quantas ${labelUnidade} inteiras — cada uma carrega ${tamanhoGrupoTexto} dezenas`}
            className="w-20 px-2 py-1.5 rounded-lg bg-white/5 border border-white/10 text-fg text-center placeholder:text-muted/60 focus:outline-none focus:border-accent/60"
          />
          <div className="flex rounded-lg overflow-hidden border border-white/10" role="group" aria-label="Sortear números em lote para fixar ou excluir">
            <button
              type="button"
              onClick={() => {
                setLoteModo('fixo');
                setLoteFeedback(null);
              }}
              aria-pressed={loteModo === 'fixo'}
              className={`px-2.5 py-1.5 transition-colors ${
                loteModo === 'fixo'
                  ? 'bg-emerald-500/25 text-emerald-200 font-semibold'
                  : 'bg-white/5 text-muted hover:text-fg'
              }`}
            >
              🟢 Fixar
            </button>
            <button
              type="button"
              onClick={() => {
                setLoteModo('excluido');
                setLoteFeedback(null);
              }}
              aria-pressed={loteModo === 'excluido'}
              className={`px-2.5 py-1.5 transition-colors ${
                loteModo === 'excluido'
                  ? 'bg-hot/25 text-hot font-semibold'
                  : 'bg-white/5 text-muted hover:text-fg'
              }`}
            >
              🔴 Excluir
            </button>
          </div>
          <label
            className="flex items-center gap-1 cursor-pointer select-none bg-white/5 px-2 py-1.5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
            title={loteUnidade === 'dezena'
              ? 'Quando ativo, escolhe os melhores números (fixar) ou piores (excluir) com base em frequência, ciclo, previsão posicional e repetição recente. Desativado, sorteia aleatoriamente.'
              : `Quando ativo, ranqueia as ${labelUnidade} pelo score médio das dezenas de cada uma (melhores para fixar, piores para excluir). Desativado, sorteia ${labelUnidade} aleatórias.`}
          >
            <input
              type="checkbox"
              checked={loteOtimizado}
              onChange={() => {
                setLoteOtimizado(prev => !prev);
                setLoteFeedback(null);
              }}
              className="w-3 h-3 rounded border-white/30 bg-white/5 text-accent focus:ring-accent"
            />
            <span className="text-[11px] text-muted">Otimizado</span>
          </label>
          <button
            type="button"
            onClick={aplicarLote}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
            style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
            title={loteOtimizado
              ? `Escolhe as melhores/piores ${labelUnidade} por score e marca${loteUnidade === 'dezena' ? ' os números' : ' as dezenas da casa'}`
              : `Sorteia ${loteUnidade === 'dezena' ? 'a quantidade informada' : `as ${labelUnidade} informadas`} e marca`}
          >
            {loteOtimizado ? '✨ Aplicar' : '🎲 Sortear'}
          </button>
          <span className="text-[11px] text-muted">
            até {limiteLoteExibido} {labelUnidade}
            {loteUnidade !== 'dezena' && ` (${tamanhoGrupoTexto} dezenas cada)`} ·
            {loteOtimizado ? ' por score (melhor → pior)' : ' aleatório entre os disponíveis'} · 0 limpa
          </span>
          {loteFeedback && (
            <span
              role="status"
              className={`text-[11px] ${loteFeedback.tipo === 'ok' ? 'text-emerald-300' : 'text-amber-300'}`}
            >
              {loteFeedback.texto}
            </span>
          )}
        </div>
        {(fixos.length > 0 || excluidos.length > 0) && (
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            {fixos.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-muted">Fixos:</span>
                {fixos.map(n => {
                  const validas = posicoesValidas(n);
                  const selecionadas = fixosPosicoes[n] || [];
                  return (
                    <div
                      key={n}
                      className="flex flex-wrap items-center gap-1 px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-500/30"
                      title={selecionadas.length > 0
                        ? `Restrito às posições N${selecionadas.join(', N')}`
                        : 'Usado em qualquer posição válida'}
                    >
                      <span className="font-semibold">{n}</span>
                      <div className="flex items-center gap-0.5">
                        {validas.map(p => {
                          const ativo = selecionadas.includes(p);
                          return (
                            <button
                              key={p}
                              onClick={() => togglePosicaoFixo(n, p)}
                              title={`Restringir ${n} à posição N${p}`}
                              className={`text-[10px] px-1.5 py-0.5 rounded-full border leading-none transition-colors ${
                                ativo
                                  ? 'bg-emerald-400 text-emerald-950 border-emerald-300 font-bold'
                                  : 'bg-transparent text-emerald-200/60 border-emerald-500/25 hover:bg-emerald-400/15'
                              }`}
                            >
                              N{p}
                            </button>
                          );
                        })}
                      </div>
                      {selecionadas.length === 0 && (
                        <span className="text-[10px] text-emerald-200/50">(qualquer)</span>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
            {excluidos.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-muted">Excluídos:</span>
                {excluidos.map(n => {
                  const validas = posicoesValidas(n);
                  const proibidas = excluidosPosicoes[n] || [];
                  const completa = proibidas.length === 0;
                  return (
                    <div
                      key={n}
                      className="flex flex-wrap items-center gap-1 px-2 py-1 rounded-full bg-hot/15 text-hot/80 border border-hot/30"
                      title={completa
                        ? 'Excluído completamente'
                        : `Excluído das posições N${proibidas.join(', N')}`}
                    >
                      <span className="font-semibold">{n}</span>
                      {validas.length > 0 && (
                        <div className="flex items-center gap-0.5">
                          {validas.map(p => {
                            const proibido = proibidas.includes(p);
                            return (
                              <button
                                key={p}
                                onClick={() => toggleExclusaoPosicao(n, p)}
                                title={`Excluir ${n} da posição N${p}`}
                                className={`text-[10px] px-1.5 py-0.5 rounded-full border leading-none transition-colors ${
                                  proibido
                                    ? 'bg-hot/40 text-hot border-hot/60 font-bold'
                                    : 'bg-transparent text-hot/50 border-hot/25 hover:bg-hot/20'
                                }`}
                              >
                                N{p}
                              </button>
                            );
                          })}
                        </div>
                      )}
                      {completa && (
                        <span className="text-[10px] text-hot/60">(completa)</span>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
        </div>
        {quarentena && (
          <QuarantineMatrixMini quarentena={quarentena} numerosSorteados={numerosSorteadosAtual} />
        )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-sm">
          {error}
        </div>
      )}

      {estatisticas && (
        <div className="mb-5 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Jogos</div>
            <div className="text-lg font-bold text-fg">{estatisticas.total}</div>
          </div>
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Cobertura</div>
            <div className="text-lg font-bold text-fg">{estatisticas.cobertura}/{totalNumeros}</div>
          </div>
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Custo</div>
            <div className="text-lg font-bold text-fg">R$ {(estatisticas.total * precoUnit).toFixed(2)}</div>
          </div>
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Estimativa total</div>
            <div className="text-lg font-bold text-fg">
              {estimativaTotal === null ? '—' : estimativaTotal.toLocaleString('pt-BR')}
            </div>
          </div>
        </div>
      )}

      {cicloAtual && (
        <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm font-semibold text-ink">Frequência no ciclo atual</div>
            <div className="text-xs text-muted">
              Média: <strong className="text-fg">{cicloAtual.media_frequencia.toFixed(2)}</strong> sorteios/número
            </div>
          </div>
          <div className={`grid ${cicloGridClass} gap-2`} style={{ maxWidth: cicloMaxW }}>
            {cicloAtual.numero.sort((a, b) => a.numero - b.numero).map(({ numero, qtd }) => {
              let classes = 'bg-white/5 text-muted border-white/10';
              if (qtd === 0) classes = 'bg-amber-500/25 text-amber-100 border-amber-500/40';
              else if (qtd === 1) classes = 'bg-amber-500/10 text-amber-200/80 border-amber-500/20';
              else if (qtd >= 4) classes = 'bg-emerald-500/15 text-emerald-200 border-emerald-500/30';
              const sorteado = sorteadosAtualSet.has(numero);
              return (
                <div key={numero} className={`flex flex-col items-center justify-center rounded-lg border p-1 ${classes}`}>
                  <span
                    className={`text-sm font-bold ${sorteado ? 'text-emerald-400' : ''}`}
                    title={sorteado ? 'Sorteado no concurso base' : undefined}
                  >{numero}</span>
                  <span className="text-[10px] opacity-80">{qtd}x</span>
                </div>
              );
            })}
          </div>
          <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-500/25 border border-amber-500/40" /> 0 sorteios (faltante)</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-500/10 border border-amber-500/20" /> 1 sorteio</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500/15 border border-emerald-500/30" /> 4+ sorteios</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-transparent border border-emerald-500/30 flex items-center justify-center text-[9px] font-bold text-emerald-400">n</span> sorteado no concurso atual</span>
          </div>
        </div>
      )}

      {jogosFiltrados && (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <button
              onClick={() => {
                const texto = jogosFiltrados.map(jogoLinha).join('\n');
                navigator.clipboard.writeText(texto);
              }}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
              Copiar todos (CSV)
            </button>
            <button
              onClick={() => {
                if (modoTodas) {
                  void exportarTodas();
                  return;
                }
                const texto = jogosFiltrados.map(jogoLinha).join('\n');
                const blob = new Blob([texto], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `jogos-${loteria}-${new Date().toISOString().slice(0, 10)}.txt`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                setTimeout(() => URL.revokeObjectURL(url), 1000);
              }}
              disabled={exporting}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold text-ink bg-white/5 border border-white/10 hover:bg-white/10 transition-colors disabled:opacity-50">
              Baixar .txt
            </button>
            {(modoTodas || jogosFiltrados.length >= 50) && (
              <button
                onClick={exportarTodas}
                disabled={exporting}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
                {exporting ? 'Exportando...' : 'Exportar todas'}
              </button>
            )}
            <span className="text-xs text-muted">
              Formato: números separados por vírgula, um jogo por linha
              {cfg.trevos_cols && cfg.trevos_cols.length > 0 ? ' (Mais Milionária: dezenas|trevos)' : cfg.mes_sorte ? ' (Dia de Sorte: dezenas|M:mês)' : ''}
            </span>
          </div>
          {estrategiasFiltro.length > 0 && (
            <div className="text-xs text-[#a5b4fc] bg-accent-2/10 border border-[#818cf8]/20 rounded-lg p-2">
              Filtrando por {estrategiasFiltro.length} estratégia(s): {estrategiasFiltro.map(e => ESTRATEGIA_LABEL[e] || e).join(', ')} — {jogosFiltrados.length} de {jogos?.length ?? 0} jogo(s).
            </div>
          )}
          {modoTodas && estimativaTotal !== null && (
            <div className="text-xs text-emerald-200 bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2">
              Modo "todas as combinações": geradas {estimativaTotal.toLocaleString('pt-BR')} apostas.
              Apenas as 50 primeiras são exibidas; use <strong>Exportar todas</strong> para baixar o arquivo completo.
            </div>
          )}
          {!modoTodas && jogosFiltrados.length >= 50 && (
            <div className="text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
              Exibindo as 50 primeiras apostas. Use <strong>Exportar todas</strong> para baixar o arquivo completo.
            </div>
          )}
          {jogosFiltrados.length === 0 ? (
            <div className="text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
              Nenhum jogo atende às estratégias selecionadas. Desmarque filtros para ver todas as apostas.
            </div>
          ) : jogosFiltrados.length < quantidade && !modoTodas ? (
            <div className="text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
              Pedidos {quantidade} jogo(s), mas apenas <strong>{jogosFiltrados.length}</strong> atendem às restrições.
              Os demais foram descartados.
            </div>
          ) : null}
          {jogosFiltrados.slice(0, 50).map((jogo, idx) => (
            <div key={idx} className="rounded-xl bg-white/5 border border-white/10 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-ink">Jogo {idx + 1}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent-2/15 text-[#a5b4fc]">
                    {ESTRATEGIA_LABEL[jogo.estrategia] || jogo.estrategia}
                  </span>
                  {jogo.mes && (
                    <span
                      className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-200 border border-amber-500/30"
                      title={`Mês da Sorte — se sorteado, paga R$ ${premioMesSorte(loteria, jogo.numeros.length).toLocaleString('pt-BR', { minimumFractionDigits: 2 })} nesta aposta`}>
                      Mês: {nomeMesSorte(jogo.mes)}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-muted">
                  <span>Soma: <strong className="text-fg">{jogo.soma}</strong></span>
                  <span>Pares: <strong className="text-fg">{jogo.pares}</strong></span>
                  <span>Ímpares: <strong className="text-fg">{jogo.impares}</strong></span>
                  <span>Primos: <strong className="text-fg">{jogo.primos}</strong></span>
                  <button
                    onClick={() => navigator.clipboard.writeText(jogoLinha(jogo))}
                    className="text-accent-2 hover:text-[#a5b4fc] transition-colors"
                    title="Copiar jogo">
                    Copiar
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {jogo.numeros.map(n => {
                  const sorteado = sorteadosAtualSet.has(n);
                  const faltante = cicloAtual?.faltantes.includes(n);
                  const classes = sorteado
                    ? 'bg-emerald-500/25 text-emerald-100 border-emerald-500/50 ring-1 ring-emerald-500/30'
                    : faltante
                      ? 'bg-amber-500/20 text-amber-100 border-amber-500/40'
                      : 'bg-[rgba(129,140,248,0.12)] text-accent-2 border-[rgba(129,140,248,0.25)]';
                  return (
                    <span
                      key={n}
                      className={`w-9 h-9 flex items-center justify-center rounded-lg text-sm font-bold border transition-all ${classes}`}
                      title={sorteado ? 'Sorteado no concurso base' : undefined}>
                      {n}
                    </span>
                  );
                })}
              </div>
              {jogo.trevos && jogo.trevos.length > 0 && (
                <div className="flex flex-wrap items-center gap-2 mt-3">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-200 border border-amber-500/40">
                    Trevos
                  </span>
                  {jogo.trevos.map(t => (
                    <span
                      key={t}
                      className="w-9 h-9 flex items-center justify-center rounded-lg text-sm font-bold border bg-amber-500/25 text-amber-100 border-amber-500/50">
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {modoFechamento && (
        <div className="mb-5 p-5 rounded-xl bg-white/5 border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-ink">Fechamento Combinatório</h3>
              <p className="text-xs text-muted">
                C(v, k, t) — garante t acertos se as t dezenas sorteadas estiverem entre as v escolhidas.
              </p>
            </div>
            <button
              onClick={() => setModoFechamento(false)}
              className="text-xs px-3 py-1 rounded-lg bg-white/5 text-muted hover:text-fg hover:bg-white/10 transition-colors">
              Voltar para gerador
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="flex flex-col gap-1">
              <label className="text-xs text-muted">k (dezenas por aposta)</label>
              <input
                type="number"
                min={fechamentoCfg.kMin}
                max={fechamentoCfg.kMax}
                value={fechamentoK}
                onChange={e => setFechamentoK(Math.max(fechamentoCfg.kMin, Math.min(fechamentoCfg.kMax, parseInt(e.target.value, 10) || fechamentoCfg.kPadrao)))}
                className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-muted">t (garantia de acertos)</label>
              <input
                type="number"
                min={1}
                max={Math.min(fechamentoK, fechamentoCfg.tMax)}
                value={fechamentoT}
                onChange={e => setFechamentoT(Math.max(1, Math.min(fechamentoK, fechamentoCfg.tMax, parseInt(e.target.value, 10) || fechamentoCfg.tPadrao)))}
                className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-muted">Máx. apostas (0 = todas)</label>
              <input
                type="number"
                min={0}
                max={fechamentoCfg.maxApostasMax}
                value={fechamentoMax}
                disabled={fechamentoCoberturaCompleta}
                onChange={e => {
                  const valor = parseInt(e.target.value, 10);
                  setFechamentoMax(Number.isNaN(valor) ? 0 : Math.max(0, Math.min(fechamentoCfg.maxApostasMax, valor)));
                }}
                title={fechamentoCoberturaCompleta
                  ? 'Ignorado na cobertura completa (todas as C(v,k) apostas)'
                  : '0 = sem limite de apostas, mas o pool de candidatos é limitado a 20.000; a geração para ao cobrir todos os t-subconjuntos ou esgotar o pool'}
                className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-muted">Seed</label>
              <input
                type="number"
                value={fechamentoSeed}
                onChange={e => setFechamentoSeed(parseInt(e.target.value, 10) || 7)}
                className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
              />
            </div>
          </div>

          {fechamentoT === fechamentoK && (
            <div className={`mb-4 rounded-xl border p-3 ${
              fechamentoCoberturaCompleta
                ? 'border-amber-400/40 bg-amber-500/[0.06]'
                : 'border-white/10 bg-white/[0.02]'
            }`}>
              <label className="flex items-start gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={fechamentoCoberturaCompleta}
                  onChange={e => setFechamentoCoberturaCompleta(e.target.checked)}
                  className="mt-0.5 accent-[#f59e0b]"
                />
                <span className="text-xs">
                  <strong className="text-fg">Cobertura completa (t = k)</strong>
                  <span className="block text-muted mt-0.5">
                    Gera <strong className="text-fg">todas as C(v,k)</strong> apostas do universo restante,
                    sem o teto de 20.000 candidatos. Ignora o limite de Máx. apostas e os filtros de
                    repetidas/categorias/tela.
                  </span>
                </span>
              </label>
              {fechamentoCoberturaCompleta && (
                <div className="mt-2 text-[11px]">
                  {coberturaCompletaTotal > 0 ? (
                    <>
                      <span className="text-fg">
                        C({coberturaCompletaV},{coberturaCompletaK}) ={' '}
                        <strong>{coberturaCompletaTotal.toLocaleString('pt-BR')}</strong> apostas
                      </span>
                      <span className="text-muted">
                        {' '}· R$ {coberturaCompletaCusto.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </span>
                      {coberturaCompletaTotal > LIMITE_COBERTURA_COMPLETA && (
                        <div className="mt-1 text-amber-200">
                          Acima do limite de {LIMITE_COBERTURA_COMPLETA.toLocaleString('pt-BR')} apostas.
                          Reduza o universo (mais exclusões) ou use t &lt; k.
                        </div>
                      )}
                    </>
                  ) : (
                    <span className="text-amber-200">
                      Universo restante insuficiente para k = {fechamentoK}.
                    </span>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="flex flex-col gap-1">
              <label className="text-xs text-muted">Seeds a testar</label>
              <input
                type="number"
                min={1}
                max={10}
                value={fechamentoSeeds}
                onChange={e => setFechamentoSeeds(Math.max(1, Math.min(10, parseInt(e.target.value, 10) || 1)))}
                title="1 = usa a seed atual; acima disso testa várias seeds e fica com a mais eficiente (ou com melhor prêmio histórico, se marcado)"
                className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
              />
              <span className="text-[10px] text-muted">1 = seed atual</span>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-muted">Repetidas do último concurso</label>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={fechamentoFiltroRepetidasAtivo}
                  onChange={() => setFechamentoFiltroRepetidasAtivo(!fechamentoFiltroRepetidasAtivo)}
                  disabled={numerosSorteadosAtual.length === 0}
                  className="accent-[#818cf8]"
                  title={numerosSorteadosAtual.length === 0 ? 'Sem sorteio atual carregado' : 'Filtrar apostas pela quantidade de dezenas repetidas do último sorteio'}
                />
                <input
                  type="text"
                  value={fechamentoRepetidasFaixa}
                  onChange={e => setFechamentoRepetidasFaixa(e.target.value)}
                  disabled={!fechamentoFiltroRepetidasAtivo || numerosSorteadosAtual.length === 0}
                  placeholder="ex.: 7-10"
                  className="w-24 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] disabled:opacity-50"
                />
              </div>
              <span className="text-[10px] text-muted">min-max; vazio/desligado = sem filtro</span>
            </div>
            <label className="flex items-center gap-2 text-xs cursor-pointer select-none self-end pb-2">
              <input
                type="checkbox"
                checked={fechamentoRemoverRedundantes}
                onChange={() => setFechamentoRemoverRedundantes(!fechamentoRemoverRedundantes)}
                className="accent-[#818cf8]"
              />
              Remover apostas redundantes
            </label>
            <label
              className="flex items-start gap-2 text-xs cursor-pointer select-none self-end pb-2"
              title="Garantia condicional: os t acertos valem apenas se TODOS os fixos forem sorteados. Reduz o alvo para t−f e gera muito menos apostas. Se algum fixo não sair, não há garantia."
            >
              <input
                type="checkbox"
                checked={fechamentoGarantiaCondicional}
                onChange={() => setFechamentoGarantiaCondicional(!fechamentoGarantiaCondicional)}
                className="accent-[#818cf8] mt-0.5"
              />
              <span className="flex flex-col leading-tight">
                <span>Garantia condicional aos fixos</span>
                <span className="text-[10px] text-muted">
                  {fixos.length === 0
                    ? 'selecione fixos para ativar'
                    : fixos.length >= fechamentoT
                      ? 'fixos ≥ t: garantia automática'
                      : `reduz o alvo para t−${fixos.length} = ${Math.max(1, fechamentoT - fixos.length)}`}
                </span>
              </span>
            </label>
            <label className="flex items-center gap-2 text-xs cursor-pointer select-none self-end pb-2" title="Compara várias seeds e escolhe a de melhor retorno histórico. Ao ativar, usa pelo menos 5 seeds.">
              <input
                type="checkbox"
                checked={fechamentoPriorizarPremios}
                onChange={() => {
                  const novo = !fechamentoPriorizarPremios;
                  setFechamentoPriorizarPremios(novo);
                  if (novo && fechamentoSeeds < 2) setFechamentoSeeds(5);
                }}
                className="accent-[#818cf8]"
              />
              Priorizar prêmios no histórico
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-3 mb-4">
              <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={fechamentoOtimizado}
                  onChange={() => setFechamentoOtimizado(!fechamentoOtimizado)}
                  className="accent-[#818cf8]"
                />
                Otimizado (guloso + busca local)
              </label>
              <label
                className="flex items-center gap-2 text-xs cursor-pointer select-none"
                title="Troca o covering design (todo t-subconjunto dentro de algum bloco) por um lotto design (todo sorteio possível atinge o piso em algum bloco). Mesmo piso de acertos com muito menos apostas, e o design acompanha fixos e excluídos: 2 fixos e alvo 11 → 33 apostas; 5 fixos e alvo 11 → 11 (contra 343 do cover); 5 excluídos e alvo 11 → 4 (contra 544 do cover). Com fixos ou excluídos a garantia é condicional: vale se os fixos saírem e os excluídos não saírem."
              >
                <input
                  type="checkbox"
                  checked={fechamentoUsarLottoDesign}
                  onChange={() => setFechamentoUsarLottoDesign(!fechamentoUsarLottoDesign)}
                  className="accent-[#818cf8]"
                />
                Lotto design (reduz apostas, mesmo piso)
              </label>
              <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={aplicarFiltrosCategorias}
                  onChange={() => setAplicarFiltrosCategorias(!aplicarFiltrosCategorias)}
                  className="accent-[#818cf8]"
                />
                Aplicar filtros de categoria (min/max)
              </label>
              <label
                className="flex items-center gap-2 text-xs cursor-pointer select-none"
                title="Aplica ao fechamento os filtros preenchidos na tela: Colunas Posicionais, Linhas Posicionais, Comparativo, Categorias e Repetidos dos 3 últimos sorteios. Filtros muito restritivos podem reduzir a cobertura; o sistema avisa no resultado."
              >
                <input
                  type="checkbox"
                  checked={fechamentoAplicarFiltrosTela}
                  onChange={() => setFechamentoAplicarFiltrosTela(!fechamentoAplicarFiltrosTela)}
                  className="accent-[#818cf8]"
                />
                Aplicar filtros da tela ao fechamento
              </label>
              <label className="flex items-center gap-2 text-xs cursor-pointer select-none" title="Tenta reduzir o número de apostas com CP-SAT ou MIP (SCIP/CBC). Coberturas ótimas conhecidas são usadas automaticamente antes do solver.">
                <input
                  type="checkbox"
                  checked={fechamentoUsarCpSat}
                  onChange={() => setFechamentoUsarCpSat(!fechamentoUsarCpSat)}
                  className="accent-[#818cf8]"
                />
                Solver
                <select
                  value={fechamentoSolver}
                  onChange={e => setFechamentoSolver(e.target.value as 'cp_sat' | 'SCIP' | 'CBC')}
                  disabled={!fechamentoUsarCpSat}
                  className="px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-fg focus:outline-none focus:border-[#818cf8] disabled:opacity-50"
                >
                  <option value="cp_sat">CP-SAT</option>
                  <option value="SCIP">SCIP</option>
                  <option value="CBC">CBC</option>
                </select>
                <input
                  type="number"
                  min={5}
                  max={60}
                  value={fechamentoCpSatTime}
                  onChange={e => {
                    const valor = parseInt(e.target.value, 10);
                    setFechamentoCpSatTime(Number.isNaN(valor) ? 10 : Math.max(5, Math.min(60, valor)));
                  }}
                  disabled={!fechamentoUsarCpSat}
                  className="w-14 px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-fg focus:outline-none focus:border-[#818cf8] disabled:opacity-50"
                  title="Tempo máximo do solver em segundos"
                />
                s
              </label>
              <label className="flex items-center gap-2 text-xs" title="0 = automático (recomendado). 25 = busca rápida (reproduz o conjunto antigo). 2000 = busca intensa para t=3.">
                Amostra
                <input
                  type="number"
                  min={0}
                  max={5000}
                  value={fechamentoAmostra}
                  onChange={e => {
                    const valor = parseInt(e.target.value, 10);
                    setFechamentoAmostra(Number.isNaN(valor) ? 0 : Math.max(0, Math.min(5000, valor)));
                  }}
                  className="w-20 px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-fg focus:outline-none focus:border-[#818cf8]"
                />
              </label>
              <label className="flex items-center gap-2 text-xs whitespace-nowrap" title="Quantidade de seeds consecutivos testados na otimização (2 a 50).">
                Seeds a otimizar
                <input
                  type="number"
                  min={2}
                  max={50}
                  value={fechamentoOtimizarQtd}
                  onChange={e => {
                    const valor = parseInt(e.target.value, 10);
                    setFechamentoOtimizarQtd(Number.isNaN(valor) ? 20 : Math.max(2, Math.min(50, valor)));
                  }}
                  className="w-16 px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-fg focus:outline-none focus:border-[#818cf8]"
                />
              </label>
              <label className="flex items-center gap-2 text-xs whitespace-nowrap" title="Critério de desempate da otimização de seeds.">
                Critério
                <select
                  value={fechamentoCriterioOtimizacao}
                  onChange={e => setFechamentoCriterioOtimizacao(e.target.value as 'custo' | 'diversidade' | 'backtest' | 'equilibrado')}
                  className="px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-fg focus:outline-none focus:border-[#818cf8]"
                >
                  <option value="custo">Menos apostas</option>
                  <option value="diversidade">Mais diversidade</option>
                  <option value="backtest">Backtest (holdout)</option>
                  <option value="equilibrado">Equilibrado</option>
                </select>
              </label>
              <button
                onClick={() => gerarFechamento({
                  otimizarSeeds: true,
                  quantidadeSeeds: fechamentoOtimizarQtd,
                  criterioOtimizacao: fechamentoCriterioOtimizacao,
                })}
                disabled={gerandoFechamento || fechamentoCoberturaCompleta}
                title="Testa várias seeds consecutivas e escolhe a melhor pelo critério (menos apostas → diversidade → backtest com holdout). Não se aplica à cobertura completa."
                className="px-4 py-2 rounded-lg text-sm font-semibold text-emerald-200 border border-emerald-400/40 hover:bg-emerald-500/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {gerandoFechamento ? 'Otimizando...' : 'Otimizar seeds'}
              </button>
            <div className="relative group">
              <button
                onClick={() => gerarFechamento()}
                disabled={gerandoFechamento || (fechamentoCoberturaCompleta && !coberturaCompletaValida)}
                title={fechamentoCoberturaCompleta
                  ? `Cobertura completa: ${coberturaCompletaTotal.toLocaleString('pt-BR')} apostas`
                  : fechamentoCfg.tooltipReceita}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
                {gerandoFechamento ? 'Gerando fechamento...' : 'Gerar fechamento'}
              </button>
              <div className="pointer-events-none absolute bottom-full left-0 mb-2 w-80 rounded-xl bg-[#0b1220] border border-white/15 p-3 text-xs text-fg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-50">
                <div className="font-semibold text-accent-2 mb-2">Receita recomendada — {fechamentoCfg.nome}</div>
                <p className="text-muted mb-2">{fechamentoCfg.tooltipReceita}</p>
                <ul className="space-y-1 text-muted list-disc pl-4">
                  <li><strong className="text-fg">k={fechamentoCfg.kPadrao}, t={fechamentoCfg.tPadrao}</strong> (limites: k {fechamentoCfg.kMin}–{fechamentoCfg.kMax}, t ≤ {fechamentoCfg.tMax}).</li>
                  <li><strong className="text-fg">Máx. apostas = 0</strong>; filtros de categoria e repetidas desligados para 100% de cobertura.</li>
                  <li>O solver (CP-SAT/SCIP/CBC) só entra quando não existe cover conhecido.</li>
                  <li>Use <strong className="text-fg">Backtest histórico</strong> para comparar as faixas de prêmio.</li>
                </ul>
              </div>
            </div>
            {gerandoFechamento && (
              <button
                onClick={cancelarFechamento}
                className="px-3 py-2 rounded-lg text-sm font-semibold text-rose-200 border border-rose-400/40 hover:bg-rose-500/10 transition-all">
                Cancelar
              </button>
            )}
          </div>

          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs text-muted">
              {fixos.length > 0 || excluidos.length > 0 || aplicarFiltrosCategorias
                ? `Aplicados: ${fixos.length} fixo(s) ${fixos.length > 0 ? `(${fixos.join(', ')})` : ''} ${excluidos.length > 0 ? `| ${excluidos.length} excluído(s) (${excluidos.join(', ')})` : ''} ${aplicarFiltrosCategorias || fechamentoAplicarFiltrosTela ? `| ${categoriasDefs.filter(c => (categoriasInputs[c.id] ?? '').trim() !== '').length} filtro(s) de categoria` : ''}${fechamentoAplicarFiltrosTela ? ' | filtros da tela (colunas/linhas/comparativo/repetidos)' : ''}`
                : 'Sem fixos/excluídos aplicados'}
            </span>
          </div>

          {error && (
            <div className="mb-3 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-sm">
              {error}
            </div>
          )}

          {otimizacaoInfo && (
            <div className="mb-3 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="font-semibold text-emerald-200">
                  Otimização de seeds · {otimizacaoInfo.seedsTestadas} testados · critério {CRITERIOS_OTIMIZACAO[otimizacaoInfo.criterio] ?? otimizacaoInfo.criterio}
                </div>
                <div className="text-muted">
                  escolhido: seed <strong className="text-fg">{otimizacaoInfo.seedEscolhida}</strong>
                </div>
              </div>
              <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-muted">
                <span>{otimizacaoInfo.totalApostas} aposta(s)</span>
                <span>cobertura {otimizacaoInfo.cobertura.toFixed(2)}%</span>
                {otimizacaoInfo.sobreposicaoMedia !== null && (
                  <span>sobreposição média (sem fixos) {otimizacaoInfo.sobreposicaoMedia.toFixed(2)}</span>
                )}
                {otimizacaoInfo.lucroTreino !== null && (
                  <span>lucro treino R$ {otimizacaoInfo.lucroTreino.toFixed(2)}</span>
                )}
                {otimizacaoInfo.lucroHoldout !== null && (
                  <span>holdout R$ {otimizacaoInfo.lucroHoldout.toFixed(2)} ({otimizacaoInfo.holdoutConcursos} concursos)</span>
                )}
              </div>
              {otimizacaoInfo.candidatos.length > 0 && (
                <details className="mt-2">
                  <summary className="text-accent-2 cursor-pointer select-none">Top seeds testados</summary>
                  <div className="mt-2 overflow-x-auto">
                    <table className="w-full text-left text-[11px] border-collapse">
                      <thead>
                        <tr className="text-muted">
                          <th className="pb-1 pr-3 font-normal">#</th>
                          <th className="pb-1 pr-3 font-normal">Seed</th>
                          <th className="pb-1 pr-3 font-normal">Apostas</th>
                          <th className="pb-1 pr-3 font-normal">Cobertura</th>
                          <th className="pb-1 pr-3 font-normal">Sobreposição</th>
                          <th className="pb-1 pr-3 font-normal">Lucro treino</th>
                          <th className="pb-1 font-normal">Lucro holdout</th>
                        </tr>
                      </thead>
                      <tbody>
                        {otimizacaoInfo.candidatos.map((c, idx) => (
                          <tr key={c.seed} className={`border-t border-white/5 ${c.seed === otimizacaoInfo.seedEscolhida ? 'bg-emerald-500/10' : ''}`}>
                            <td className="py-1 pr-3 text-muted">{idx + 1}</td>
                            <td className="py-1 pr-3 text-fg font-medium">{c.seed}</td>
                            <td className="py-1 pr-3">{c.totalApostas}</td>
                            <td className="py-1 pr-3">{c.cobertura.toFixed(2)}%</td>
                            <td className="py-1 pr-3">{c.sobreposicaoMedia !== null ? c.sobreposicaoMedia.toFixed(2) : '—'}</td>
                            <td className="py-1 pr-3">{c.lucroTreino !== null ? `R$ ${c.lucroTreino.toFixed(2)}` : '—'}</td>
                            <td className="py-1">{c.lucroHoldout !== null ? `R$ ${c.lucroHoldout.toFixed(2)}` : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </details>
              )}
            </div>
          )}

          {apostasFechamento.length > 0 && (
            <>
              <div className="mb-3 grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="rounded-xl bg-white/5 p-3 text-center">
                  <div className="text-xs text-muted">Total de apostas</div>
                  <div className="text-lg font-bold text-fg">{apostasFechamento.length}</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3 text-center">
                  <div className="text-xs text-muted">
                    {fechamentoPisoCondicional
                      ? 'Piso condicional (excluídos)'
                      : lottoDesignInfo
                        ? 'Piso garantido'
                        : fechamentoTInfo?.garantiaCondicional || excluidos.length > 0
                          ? 'Garantia condicional'
                          : 'Garantia'}
                  </div>
                  <div className="text-lg font-bold text-fg">
                    {fechamentoPisoCondicional
                      ? `${fechamentoPisoCondicional.pisoTotal} acerto(s)`
                      : lottoDesignInfo
                        ? `${lottoDesignInfo.pisoTotal} acerto(s)`
                        : `${coberturaFechamento?.garantiaPercentual?.toFixed(2)}%`}
                  </div>
                  {fechamentoPisoCondicional ? (
                    <div className="text-[10px] text-amber-200">
                      se os {excluidos.length} excluído(s) não saírem
                      {fixos.length > 0 ? ` e os ${fixos.length} fixo(s) saírem` : ''}
                    </div>
                  ) : lottoDesignInfo ? (
                    <div className="text-[10px] text-emerald-200">
                      em qualquer dos {lottoDesignInfo.alvos.toLocaleString('pt-BR')} sorteios
                    </div>
                  ) : fechamentoTInfo?.garantiaCondicional ? (
                    <div className="text-[10px] text-amber-200">
                      se os {fixos.length} fixo(s) saírem (t={fechamentoTInfo.tEfetivo})
                    </div>
                  ) : excluidos.length > 0 ? (
                    <div className="text-[10px] text-amber-200">
                      se os {excluidos.length} excluído(s) não saírem
                    </div>
                  ) : null}
                </div>
                <div className="rounded-xl bg-white/5 p-3 text-center">
                  <div className="text-xs text-muted">
                    {lottoDesignInfo ? 'Sorteios verificados' : 'Cobertura t-subconjuntos'}
                  </div>
                  <div className="text-lg font-bold text-fg">
                    {lottoDesignInfo
                      ? lottoDesignInfo.alvos.toLocaleString('pt-BR')
                      : `${coberturaFechamento?.tSubsetsCobertos?.toLocaleString()}/${coberturaFechamento?.tSubsetsTotal?.toLocaleString()}`}
                  </div>
                </div>
                <div className="rounded-xl bg-white/5 p-3 text-center">
                  <div className="text-xs text-muted">Custo estimado</div>
                  <div className="text-lg font-bold text-fg">R$ {custoFechamento?.custoTotal?.toFixed(2)}</div>
                  <div className="text-[10px] text-muted">R$ {custoFechamento?.precoPorJogo?.toFixed(2)} / aposta</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3 text-center">
                  <div className="text-xs text-muted">Limite inferior</div>
                  <div className="text-lg font-bold text-fg">{fechamentoLimiteInferior ?? '—'}</div>
                  <div className="text-[10px] text-muted">
                    {fechamentoLimiteInferior && fechamentoLimiteInferior > 0
                      ? `${(apostasFechamento.length / fechamentoLimiteInferior).toFixed(2)}x o mínimo`
                      : '—'}
                  </div>
                </div>
              </div>

              <div className="mb-2 text-xs text-muted">
                {lottoDesignInfo ? (
                  <span className="text-emerald-200">
                    ✅ Lotto design L({lottoDesignInfo.v},{lottoDesignInfo.k},{lottoDesignInfo.m},{lottoDesignInfo.t}): piso de{' '}
                    <strong>{lottoDesignInfo.pisoTotal} acerto(s)</strong>
                    {fixos.length > 0 ? ` (${fixos.length} fixos + ${lottoDesignInfo.piso})` : ''} em{' '}
                    {lottoDesignInfo.blocos} aposta(s)
                    {lottoDesignInfo.verificado ? ', verificado exaustivamente' : ''}.
                    {excluidos.length > 0 ? (
                      <span className="text-amber-200">
                        {' '}Cobre os sorteios do universo sem os {excluidos.length} excluído(s): se alguma excluída sair, não há garantia.
                      </span>
                    ) : null}
                  </span>
                ) : fechamentoTInfo?.garantiaCondicional ? (
                  fixos.length >= fechamentoTInfo.t ? (
                    <span className="text-emerald-200">
                      ✅ Garantia automática: os {fixos.length} fixo(s) já garantem {fechamentoTInfo.t} acertos se todos forem sorteados.
                    </span>
                  ) : (
                    <span className="text-amber-200">
                      ⚠️ Garantia CONDICIONAL: {fechamentoTInfo.t} acertos valem apenas se os {fixos.length} fixo(s) forem sorteados.
                      A verificação usa t={fechamentoTInfo.tEfetivo} no universo restante.
                    </span>
                  )
                ) : coberturaFechamento?.coberta ? (
                  '✅ Fechamento cobre 100% dos t-subconjuntos (garantia total)'
                ) : (
                  `⚠️ Cobertura parcial: ${coberturaFechamento?.garantiaPercentual?.toFixed(2)}% dos t-subconjuntos`
                )}
              </div>

              {fechamentoCoberturaRestante && !lottoDesignInfo && (fixos.length > 0 || excluidos.length > 0) && (
                <div className="mb-2 text-xs text-muted">
                  Cobertura do universo restante (garantia real):{' '}
                  <strong className="text-fg">
                    {fechamentoCoberturaRestante.tSubsetsCobertos.toLocaleString()}/{fechamentoCoberturaRestante.tSubsetsTotal.toLocaleString()}
                  </strong>{' '}
                  ({fechamentoCoberturaRestante.garantiaPercentual.toFixed(2)}%)
                </div>
              )}

              {excluidos.length > 0 && (
                <div className="mb-2 text-xs text-amber-200">
                  🔒 Garantia condicional aos excluídos:{' '}
                  {fechamentoTInfo?.t ?? fechamentoT} acerto(s) valem apenas se os {excluidos.length} excluído(s) não forem sorteados.
                  {fechamentoPisoCondicional ? (
                    <>
                      {' '}Nesse cenário o piso real é{' '}
                      <strong>{fechamentoPisoCondicional.pisoTotal} acerto(s)</strong>
                      {fechamentoPisoCondicional.pisoTotal > (fechamentoTInfo?.t ?? fechamentoT)
                        ? ' (maior que o alvo, porque o universo encolheu)'
                        : ''}
                      {' '}— verificado em {fechamentoPisoCondicional.alvos.toLocaleString('pt-BR')} sorteio(s) com{' '}
                      {fechamentoPisoCondicional.universoEfetivo} dezena(s) efetivas.
                    </>
                  ) : (
                    <>
                      {' '}Universo efetivo de {Math.max(0, totalNumeros - excluidos.length - fixos.length)} dezena(s);
                      piso real não calculado (universo grande demais para enumerar).
                    </>
                  )}
                </div>
              )}

              {!coverConhecidoInfo && !lottoDesignInfo && (fechamentoSeedUsado !== null || fechamentoSeedsTestadas !== null) && (
                <div className="mb-2 text-xs text-muted">
                  Seed usada: <strong className="text-fg">{fechamentoSeedUsado ?? '—'}</strong>
                  {fechamentoSeedsTestadas && fechamentoSeedsTestadas > 1
                    ? ` (de ${fechamentoSeedsTestadas} testada(s): ${fechamentoSeed}–${fechamentoSeed + fechamentoSeedsTestadas - 1})`
                    : ''}
                </div>
              )}

              {coverConhecidoInfo && (
                <div className="mb-2 text-xs text-muted">
                  Cover determinístico: a seed não altera este conjunto.
                </div>
              )}

              {fechamentoFiltroInfo && (
                <div className="mb-2 text-xs text-muted">
                  Filtro de repetidas: <strong className="text-fg">{fechamentoFiltroInfo.min}–{fechamentoFiltroInfo.max}</strong>
                  {' · '}{fechamentoFiltroInfo.removidas} aposta(s) removida(s)
                </div>
              )}

              {coverConhecidoInfo && (
                <div className="mb-2 text-xs text-emerald-200 bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2">
                  {coverConhecidoInfo.verificado
                    ? 'Cobertura verificada'
                    : coverConhecidoInfo.limiteInferior === coverConhecidoInfo.blocos
                      ? 'Cobertura ótima (provada)'
                      : 'Melhor cobertura conhecida'}: <strong>{coverConhecidoInfo.blocos} bloco(s)</strong> para C({coverConhecidoInfo.v},{coverConhecidoInfo.k},{coverConhecidoInfo.t}) · {coverConhecidoInfo.fonte}
                </div>
              )}

              {lottoDesignInfo && (
                <div className="mb-2 text-xs text-emerald-200 bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2">
                  Lotto design: <strong>{lottoDesignInfo.blocos} aposta(s)</strong> para L({lottoDesignInfo.v},{lottoDesignInfo.k},{lottoDesignInfo.m},{lottoDesignInfo.t})
                  {' · '}piso {lottoDesignInfo.pisoTotal}
                  {' · '}limite inferior {lottoDesignInfo.limiteInferior}
                  {' · '}{lottoDesignInfo.fonte}
                </div>
              )}

              {lottoIgnoradoInfo && (
                <div className="mb-2 text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
                  Lotto design não aplicado: {lottoIgnoradoInfo.motivo}
                </div>
              )}

              {cpSatInfo && (
                <div className="mb-2 text-xs text-muted">
                  {cpSatInfo.solver === 'cp_sat' ? 'CP-SAT' : cpSatInfo.solver}: <strong className="text-fg">{cpSatInfo.status}</strong>
                  {cpSatInfo.usado
                    ? ' · solução usada'
                    : cpSatInfo.status === 'UNKNOWN'
                      ? ' · tempo esgotado'
                      : ' · heurístico mantido'}
                  {cpSatInfo.objective != null ? ` · ${cpSatInfo.objective} aposta(s)` : ''}
                  {cpSatInfo.bestBound != null ? ` · bound ${cpSatInfo.bestBound}` : ''}
                  {` · ${cpSatInfo.wallTime.toFixed(1)}s`}
                </div>
              )}

              {fechamentoAviso && (
                <div className="mb-2 text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
                  {fechamentoAviso}
                </div>
              )}

              <div className="mb-3">
                <button
                  onClick={rodarBacktest}
                  disabled={rodandoBacktest}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-ink bg-white/5 border border-white/10 hover:bg-white/10 transition-colors disabled:opacity-50">
                  {rodandoBacktest ? 'Rodando backtest...' : 'Backtest histórico'}
                </button>
              </div>

              {backtestFechamento && (
                <div className="mb-3 rounded-xl bg-white/5 border border-white/10 p-3">
                  <div className="flex flex-wrap gap-4 text-xs">
                    <div><span className="text-muted">Média melhor acerto:</span> <strong>{backtestFechamento.mediaMelhorAcerto.toFixed(2)}</strong></div>
                    <div><span className="text-muted">Prêmio médio/concurso:</span> <strong>R$ {backtestFechamento.premioMedio.toFixed(2)}</strong></div>
                    <div><span className="text-muted">Custo/concurso:</span> <strong>R$ {backtestFechamento.custoTotal.toFixed(2)}</strong></div>
                    <div>
                      <span className="text-muted">ROI médio:</span>{' '}
                      <strong className={backtestFechamento.roiMedio >= 0 ? 'text-emerald-300' : 'text-rose-300'}>
                        {(backtestFechamento.roiMedio * 100).toFixed(1)}%
                      </strong>
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    {backtestFechamento.faixas.map(f => (
                      <span key={f.acertos} className="px-2 py-1 rounded bg-white/5">
                        ≥{f.acertos}: <strong>{f.percentual.toFixed(2)}%</strong> ({f.concursos})
                      </span>
                    ))}
                  </div>
                  <div className="mt-2 text-[11px] text-muted">
                    Distribuição do melhor acerto:{' '}
                    {backtestFechamento.distribuicaoMelhorAcerto
                      .map((c, h) => (c ? `${h}:${c}` : null))
                      .filter(Boolean)
                      .join(' · ')}
                  </div>
                  <div className="mt-1 text-[11px] text-muted">
                    Melhores concursos:{' '}
                    {backtestFechamento.melhoresConcursos
                      .map(m => `#${m.concurso} (${m.melhorAcerto} acertos, ${m.repetidas} repetidas)`)
                      .join(' · ')}
                  </div>
                  <div className="mt-1 text-[11px] text-muted">
                    Repetidas do anterior:{' '}
                    {backtestFechamento.repetidasDistribuicao
                      .map(r => `${r.repetidas}:${r.percentual.toFixed(1)}%`)
                      .join(' · ')}
                  </div>
                  <div className="mt-2 text-[10px] text-muted">
                    Prêmios de referência ({fechamentoCfg.nome}): {textoPremios(fechamentoCfg)}. Valores reais variam por concurso.
                  </div>
                </div>
              )}

              <div className="flex gap-2 mb-3">
                <button
                  onClick={() => {
                    const texto = apostasFechamento.map(j => j.join(',')).join('\n');
                    navigator.clipboard.writeText(texto);
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
                  style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
                  Copiar apostas (CSV)
                </button>
                <button
                  onClick={() => {
                    const texto = apostasFechamento.map(j => j.join(',')).join('\n');
                    const blob = new Blob([texto], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `fechamento-${loteria}-k${fechamentoK}t${fechamentoT}-${new Date().toISOString().slice(0, 10)}.txt`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    setTimeout(() => URL.revokeObjectURL(url), 1000);
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-ink bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                  Baixar .txt{apostasFechamento.length > 50 ? ` (${apostasFechamento.length})` : ''}
                </button>
              </div>

              {apostasFechamento.length > 50 && (
                <div className="mb-3 text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
                  Exibindo as 50 primeiras apostas de {apostasFechamento.length}. Use <strong>Baixar .txt</strong> para o arquivo completo.
                </div>
              )}

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr>
                      {apostasFechamento[0]?.map((_, i) => (
                        <th key={i} className="pb-2 pr-2 text-muted font-normal">N{i + 1}</th>
                      ))}
                      <th className="pb-2 pr-2 text-muted font-normal text-right">Soma</th>
                    </tr>
                  </thead>
                  <tbody>
                    {apostasFechamento.slice(0, 50).map((jogo, idx) => (
                      <tr key={idx} className="border-b border-white/10">
                        {jogo.map(n => (
                          <td key={n} className="py-1 pr-2 text-fg font-mono">
                            {n}
                          </td>
                        ))}
                        <td className="py-1 pr-2 text-muted text-right font-mono">
                          {jogo.reduce((a, b) => a + b, 0)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {apostasFechamento.length === 0 && !gerandoFechamento && !error && (
            <div className="text-center py-8 text-muted text-sm">
              Configure k, t e clique em <strong>Gerar fechamento</strong>.
            </div>
          )}
        </div>
      )}

      {!jogos && !loading && !modoFechamento && (
        <div className="text-center py-8 text-muted text-sm">
          Clique em <strong>Gerar</strong> para criar jogos diversificados.
        </div>
      )}

      <GeneratingOverlay show={loading} progress={progresso} />
    </div>
  );
}
