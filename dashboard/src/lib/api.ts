import type { DashboardData } from '@/types';
import type { AnaliseGruposData } from '@/lib/analise-grupos';

export async function getDashboardData(janela?: number, signal?: AbortSignal, loteria?: string, concurso?: number): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (janela) params.set('janela', String(janela));
  if (loteria && loteria !== 'lotofacil') params.set('loteria', loteria);
  if (concurso !== undefined) params.set('concurso', String(concurso));
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
