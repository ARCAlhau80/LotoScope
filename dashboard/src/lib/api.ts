import type { DashboardData, RankingCombinacaoItem } from '@/types';
import type { AnaliseGruposData } from '@/lib/analise-grupos';

export async function getDashboardData(janela?: number, signal?: AbortSignal, loteria?: string, concurso?: number, poissonJanela?: number): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (janela) params.set('janela', String(janela));
  if (loteria && loteria !== 'lotofacil') params.set('loteria', loteria);
  if (concurso !== undefined) params.set('concurso', String(concurso));
  if (poissonJanela !== undefined) params.set('poisson_janela', String(poissonJanela));
  const qs = params.toString();
  const res = await fetch(`/api/dashboard-data${qs ? `?${qs}` : ''}`, { signal });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data;
}

export async function getAnaliseGrupos(signal?: AbortSignal): Promise<AnaliseGruposData> {
  const res = await fetch('/api/analise-grupos', { signal });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data;
}

export interface JanelaAlvoNumero {
  numero: number;
  ocorrencias: number;
  percentual: number;
}

export interface JanelaAlvoConcurso {
  concurso: number;
  numeros: number[];
  data: string | null;
}

export interface JanelaAlvoData {
  sucesso: boolean;
  loteria: string;
  concursoAlvo: number;
  janelaSolicitada: number;
  janelaEfetiva: number;
  totalSorteios: number;
  primeiroConcursoJanela: number | null;
  ultimoConcursoJanela: number | null;
  numeros: JanelaAlvoNumero[];
  concursos: JanelaAlvoConcurso[];
  alvo: JanelaAlvoConcurso | null;
}

export async function getJanelaAlvo(
  loteria: string,
  concurso: number | undefined,
  janela: number,
  signal?: AbortSignal,
): Promise<JanelaAlvoData> {
  const params = new URLSearchParams();
  params.set('loteria', loteria);
  if (concurso !== undefined) params.set('concurso', String(concurso));
  params.set('janela', String(janela));
  const res = await fetch(`/api/janela-alvo?${params.toString()}`, { signal });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data;
}

export async function getRankingCombinacoes(
  perfil: string = 'altovalor',
  top: number = 10,
  signal?: AbortSignal
): Promise<RankingCombinacaoItem[]> {
  const params = new URLSearchParams();
  params.set('perfil', perfil);
  params.set('top', String(top));
  const res = await fetch(`/api/ranking-combinacoes?${params.toString()}`, { signal });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data.ranking || [];
}

export async function generateCombinations(params: {
  mandatory_numbers: number[];
  excluded_numbers?: number[];
  game_size?: number;
  quantity?: number;
  loteria?: string;
}): Promise<{
  success: boolean;
  combinations: number[][];
  count: number;
  total_possible?: number;
  error?: string;
}> {
  const res = await fetch('/api/generate-combinations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  const data = await res.json();
  if (!data.success) throw new Error(data.error || 'Erro ao gerar combinações');
  return data;
}
