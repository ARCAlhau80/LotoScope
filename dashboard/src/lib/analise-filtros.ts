import type {
  ColunasPosicionaisConstraint,
  FiltroCategoria,
  FiltroComparativo,
  FiltrosAvaliaveis,
} from './gerador-diversificado';
import { avaliarFiltrosCombinacao } from './gerador-diversificado';

export interface CategoriaSnapshot extends FiltroCategoria {
  label: string;
}

export interface FiltrosSnapshot {
  loteria: string;
  concursoBase?: number;
  geradoEm: string;
  jogosGerados: number;
  dezenas: number;
  numerosSorteados: number;
  totalNumeros: number;
  numeroMinimo: number;
  baseComparativo: number[];
  fixos: number[];
  excluidos: number[];
  colunasPosicionais?: ColunasPosicionaisConstraint;
  dominiosPosicionais?: Array<number[] | null>;
  filtroComparativo?: FiltroComparativo;
  categorias: CategoriaSnapshot[];
  fixosPosicoes?: Record<number, number[]>;
  excluidosPosicoes?: Record<number, number[]>;
}

export interface FiltroAnalise {
  id: string;
  label: string;
  falhas: number;
  total: number;
}

export interface AnaliseFiltrosResultado {
  totalCandidatos: number;
  aprovados: number;
  eliminado: boolean;
  filtros: FiltroAnalise[];
  eliminadoresIndividuais: FiltroAnalise[];
}

function combinacoes<T>(arr: T[], k: number): T[][] {
  if (k < 0 || k > arr.length) return [];
  if (k === 0) return [[]];
  const out: T[][] = [];
  const atual: T[] = [];
  const rec = (inicio: number) => {
    if (atual.length === k) {
      out.push([...atual]);
      return;
    }
    const faltam = k - atual.length;
    for (let i = inicio; i <= arr.length - faltam; i++) {
      atual.push(arr[i]);
      rec(i + 1);
      atual.pop();
    }
  };
  rec(0);
  return out;
}

function labelDoFiltro(id: string, snapshot: FiltrosSnapshot): string {
  switch (id) {
    case 'fixos':
      return `Fixos (${snapshot.fixos.join(', ')})`;
    case 'excluidos':
      return `Excluídos (${snapshot.excluidos.join(', ')})`;
    case 'colunas':
      return 'Colunas posicionais';
    case 'dominios':
      return 'Domínios posicionais (N1..Nn)';
    case 'comparativo':
      return 'Comparativo posicional';
    case 'fixos_posicoes':
      return 'Posições fixas';
    case 'excluidos_posicoes':
      return 'Posições excluídas';
    default: {
      if (id.startsWith('categoria:')) {
        const i = Number(id.slice('categoria:'.length));
        const c = snapshot.categorias[i];
        return c ? `${c.label} ${c.min}-${c.max}` : `Categoria ${i + 1}`;
      }
      return id;
    }
  }
}

function montarFiltros(snapshot: FiltrosSnapshot): FiltrosAvaliaveis {
  return {
    totalNumeros: snapshot.totalNumeros,
    numeroMinimo: snapshot.numeroMinimo,
    numerosPorJogo: snapshot.dezenas,
    fixos: snapshot.fixos,
    excluidos: snapshot.excluidos,
    colunasPosicionais: snapshot.colunasPosicionais,
    dominiosPosicionais: snapshot.dominiosPosicionais,
    filtroComparativo: snapshot.filtroComparativo,
    baseComparativo: snapshot.baseComparativo,
    filtroCategorias: snapshot.categorias,
    fixosPosicoes: snapshot.fixosPosicoes,
    excluidosPosicoes: snapshot.excluidosPosicoes,
  };
}

export function analisarFiltrosPremioMaximo(
  snapshot: FiltrosSnapshot,
  sorteio: number[]
): AnaliseFiltrosResultado {
  const totalNumeros = snapshot.totalNumeros;
  const numeroMinimo = snapshot.numeroMinimo;
  const universo: number[] = [];
  for (let n = numeroMinimo; n < numeroMinimo + totalNumeros; n++) universo.push(n);

  const sorteados = new Set(sorteio);
  const foraDoSorteio = universo.filter(n => !sorteados.has(n));
  const extras = snapshot.dezenas - sorteio.length;
  const candidatos = combinacoes(foraDoSorteio, extras).map(extra =>
    [...sorteio, ...extra].sort((a, b) => a - b)
  );

  const filtrosBase = montarFiltros(snapshot);
  const falhas = new Map<string, number>();
  let aprovados = 0;
  let ids: string[] = [];

  for (const jogo of candidatos) {
    const avaliacoes = avaliarFiltrosCombinacao(jogo, filtrosBase);
    ids = avaliacoes.map(a => a.id);
    let passouTudo = true;
    for (const avaliacao of avaliacoes) {
      if (!avaliacao.passou) {
        passouTudo = false;
        falhas.set(avaliacao.id, (falhas.get(avaliacao.id) ?? 0) + 1);
      }
    }
    if (passouTudo) aprovados++;
  }

  if (ids.length === 0) {
    ids = avaliarFiltrosCombinacao(sorteio, filtrosBase).map(a => a.id);
  }

  const total = candidatos.length;
  const filtros: FiltroAnalise[] = ids.map(id => ({
    id,
    label: labelDoFiltro(id, snapshot),
    falhas: falhas.get(id) ?? 0,
    total,
  }));

  return {
    totalCandidatos: total,
    aprovados,
    eliminado: total > 0 && aprovados === 0,
    filtros,
    eliminadoresIndividuais: total > 0 ? filtros.filter(f => f.falhas === total) : [],
  };
}
