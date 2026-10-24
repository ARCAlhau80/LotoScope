import type { Resultado } from './database';
import type { TendenciaComparativo, CategoriaComparativo, PrevisaoCategoriaComparativo, PrevisaoTendenciaComparativo, StreaksTendencia } from '@/types';

const BANDAS = [
  { label: '0–5', teste: (v: number) => v <= 5 },
  { label: '6–10', teste: (v: number) => v >= 6 && v <= 10 },
  { label: '11–15', teste: (v: number) => v >= 11 },
];

const bandaDe = (v: number): string => BANDAS.find(b => b.teste(v))?.label ?? '0–5';

function calcularPrevisaoTendencia(todas: TendenciaComparativo[]): PrevisaoTendenciaComparativo {
  const atual = todas[todas.length - 1];

  const preverCat = (key: CategoriaComparativo): PrevisaoCategoriaComparativo => {
    const atualV = atual[key];
    const banda = bandaDe(atualV);
    const successors: number[] = [];
    for (let i = 1; i < todas.length; i++) {
      if (bandaDe(todas[i - 1][key]) === banda) successors.push(todas[i][key]);
    }
    if (successors.length === 0) {
      return { atual: atualV, banda_atual: banda, casos: 0, min: 0, max: 15, mediana: 0, p25: 0, p75: 0, pct_le_5: 0, pct_le_10: 0, tendencia: 'estavel' };
    }
    const sorted = [...successors].sort((a, b) => a - b);
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    const mediana = sorted[Math.floor(sorted.length / 2)];
    const p25 = sorted[Math.floor(sorted.length * 0.25)];
    const p75 = sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * 0.75))];
    const pct_le_5 = Math.round(successors.filter(v => v <= 5).length / successors.length * 100);
    const pct_le_10 = Math.round(successors.filter(v => v <= 10).length / successors.length * 100);
    const tendencia: PrevisaoCategoriaComparativo['tendencia'] = mediana < atualV ? 'cair' : mediana > atualV ? 'subir' : 'estavel';
    return { atual: atualV, banda_atual: banda, casos: successors.length, min, max, mediana, p25, p75, pct_le_5, pct_le_10, tendencia };
  };

  const categorias: Record<CategoriaComparativo, PrevisaoCategoriaComparativo> = {
    maiores: preverCat('maiores'),
    iguais: preverCat('iguais'),
    menores: preverCat('menores'),
  };

  const dominante = (['maiores', 'iguais', 'menores'] as CategoriaComparativo[])
    .slice()
    .sort((a, b) => categorias[b].mediana - categorias[a].mediana)[0];

  return {
    base_concurso: atual.concurso,
    concurso_alvo: atual.concurso + 1,
    total_historico: todas.length,
    categorias,
    dominante,
  };
}

export function calcularTendenciaComparativo(resultados: Resultado[]): {
  tendencia_comparativo: TendenciaComparativo[];
  previsao_tendencia: PrevisaoTendenciaComparativo;
  streaks_tendencia: StreaksTendencia;
} {
  const todas: TendenciaComparativo[] = [];
  for (let i = 1; i < resultados.length; i++) {
    const curr = resultados[i];
    const prev = resultados[i - 1];
    let m = 0, men = 0, ig = 0;
    for (let j = 0; j < Math.min(curr.numeros.length, prev.numeros.length); j++) {
      if (curr.numeros[j] > prev.numeros[j]) m++;
      else if (curr.numeros[j] < prev.numeros[j]) men++;
      else ig++;
    }
    todas.push({ concurso: curr.concurso, maiores: m, menores: men, iguais: ig });
  }

  return {
    tendencia_comparativo: todas.slice(-10),
    previsao_tendencia: calcularPrevisaoTendencia(todas),
    streaks_tendencia: calcularStreaksTendencia(todas),
  };
}

export function calcularStreaksTendencia(todas: TendenciaComparativo[]): StreaksTendencia {
  const categorias: CategoriaComparativo[] = ['maiores', 'menores', 'iguais'];
  const result = {} as StreaksTendencia;

  for (const cat of categorias) {
    let curLen = 0, curSum = 0;
    const streaks: { len: number; sum: number }[] = [];
    const zeros: number[] = [];
    let inicio: number | null = null;
    let streakAtualInicio: number | null = null;

    for (const t of todas) {
      const v = t[cat];
      if (v === 0) {
        zeros.push(t.concurso);
        if (curLen > 0) streaks.push({ len: curLen, sum: curSum });
        curLen = 0;
        curSum = 0;
        inicio = null;
      } else {
        if (curLen === 0) inicio = t.concurso;
        curLen++;
        curSum += v;
      }
    }
    // streak final ainda ativo
    if (curLen > 0 && inicio !== null) {
      streakAtualInicio = inicio;
    }

    const completos = streaks;
    const lenVals = completos.map(s => s.len);
    const sumVals = completos.map(s => s.sum);
    const mediaLen = completos.length ? lenVals.reduce((a, b) => a + b, 0) / completos.length : 0;
    const mediaSum = completos.length ? sumVals.reduce((a, b) => a + b, 0) / completos.length : 0;
    const sortedLen = [...lenVals].sort((a, b) => a - b);
    const medianaLen = completos.length ? sortedLen[Math.floor(sortedLen.length / 2)] : 0;
    const maxLen = completos.length ? Math.max(...lenVals) : 0;
    const maxSum = completos.length ? Math.max(...sumVals) : 0;

    result[cat] = {
      zeros: zeros.length,
      pct_zeros: todas.length > 0 ? Math.round(zeros.length / todas.length * 1000) / 10 : 0,
      total_concursos: todas.length,
      streaks: completos.length,
      max_streak: maxLen,
      max_soma: maxSum,
      media_len: Math.round(mediaLen * 100) / 100,
      mediana_len: medianaLen,
      media_soma: Math.round(mediaSum * 100) / 100,
      streak_atual_len: curLen,
      streak_atual_soma: curSum,
      streak_atual_inicio: streakAtualInicio,
      ultimos_zeros: zeros.slice(-12),
    };
  }

  return result;
}