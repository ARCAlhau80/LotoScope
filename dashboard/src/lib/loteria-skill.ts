import fs from 'fs';
import path from 'path';

function formatPositionPrevisao(previsao: Record<string, { numero: number; prob: number }[]>, totalNumeros: number): string {
  const lines: string[] = [];
  const positions = Array.from({ length: totalNumeros }, (_, i) => `N${i + 1}`);
  for (const pos of positions) {
    const top3 = previsao[pos]?.slice(0, 3);
    if (top3 && top3.length > 0) {
      lines.push(`  ${pos}: ${top3.map(p => `${p.numero} (${(p.prob * 100).toFixed(1)}%)`).join(', ')}`);
    }
  }
  return lines.join('\n');
}

function formatAtrasados(atrasados: Record<string, { numero: number; p_gap: number; gap: number; lambda_blend: number }[]>): string {
  const lines: string[] = [];
  for (const [pos, items] of Object.entries(atrasados)) {
    for (const item of items.slice(0, 3)) {
      lines.push(`  ${pos} #${item.numero}: ${item.gap} sorteios sem sair (p=${(item.p_gap * 100).toFixed(2)}%)`);
    }
  }
  return lines.length > 0 ? lines.join('\n') : '  Nenhum atraso critico no momento';
}

function formatCiclos(ciclos: Record<string, { freq_30: number; freq_esperada: number; diferenca: number; estado: string }>): string {
  const aquecendo: string[] = [];
  const esfriando: string[] = [];
  for (const [num, c] of Object.entries(ciclos)) {
    if (c.estado === 'aquecendo') aquecendo.push(`#${num} (dif: ${c.diferenca > 0 ? '+' : ''}${c.diferenca})`);
    else if (c.estado === 'esfriando') esfriando.push(`#${num} (dif: ${c.diferenca > 0 ? '+' : ''}${c.diferenca})`);
  }
  const lines: string[] = [];
  if (aquecendo.length > 0) lines.push(`  Aquecendo: ${aquecendo.join(', ')}`);
  if (esfriando.length > 0) lines.push(`  Esfriando: ${esfriando.join(', ')}`);
  return lines.join('\n');
}

export function loadLoteriaSkill(loteriaId: string): string {
  const skillPath = path.join(process.cwd(), '..', '.agents', 'skills', 'loteria', `${loteriaId}.md`);
  try {
    const content = fs.readFileSync(skillPath, 'utf-8');
    const clean = content
      .replace(/---[\s\S]*?---\n?/, '')
      .replace(/#.*\n=+\n?/g, '')
      .trim();
    return clean || '';
  } catch {
    return '';
  }
}

export function buildEnrichedContext(dashboardData: any, skillContent: string): string {
  const u = dashboardData.ultimo_sorteio;
  const qSet = dashboardData.numeros_quentes?.map((n: [number, number]) => n[0]) || [];
  const mSet = dashboardData.numeros_mornos?.map((n: [number, number]) => n[0]) || [];
  const fSet = dashboardData.numeros_frios?.map((n: [number, number]) => n[0]) || [];

  const parts: string[] = ['## CONHECIMENTO DA LOTERIA\n' + skillContent];

  parts.push(`## DADOS AO VIVO
Ultimo: #${dashboardData.ultimo_concurso} (${new Date().toLocaleDateString('pt-BR')})
Total de sorteios: ${dashboardData.total_sorteios}
Janela de analise: ${dashboardData.janela_usada} sorteios`);

  parts.push(`## ULTIMO SORTEIO
Concurso #${u.concurso}
Numeros: ${u.numeros.join(', ')}
Soma: ${u.soma} | Pares: ${u.pares} | Impares: ${u.impares}
Primos: ${u.primos} | Fibonacci: ${u.fibonacci} | Nao Sorteados: ${u.nao_sorteados} (${u.nao_sorteados_numeros.join(', ')})
Repetidos do anterior: ${u.repetidos} (${u.repetidos_numeros.join(', ')})
Consecutivas: ${u.consecutivas} (${u.consecutivas_pares.join(', ')})
Baixos: ${u.baixos} | Altos: ${u.altos}
Multiplos 3: ${u.multiplos_3} | Multiplos 5: ${u.multiplos_5}`);

  parts.push(`## CLASSIFICACAO QMF (${dashboardData.janela_usada} sorteios)
QUENTES (top ${dashboardData.numeros_quentes?.length || 0}): ${qSet.join(', ')}
MORNOS: ${mSet.join(', ')}
FRIOS (ultimos ${dashboardData.numeros_frios?.length || 0}): ${fSet.join(', ')}`);

  parts.push(`## TENDENCIA QMF
  Quentes: ${dashboardData.transicao_qmf?.tendencia?.quentes > 0 ? '+' : ''}${dashboardData.transicao_qmf?.tendencia?.quentes?.toFixed(2)}
  Mornos: ${dashboardData.transicao_qmf?.tendencia?.mornos > 0 ? '+' : ''}${dashboardData.transicao_qmf?.tendencia?.mornos?.toFixed(2)}
  Frios: ${dashboardData.transicao_qmf?.tendencia?.frios > 0 ? '+' : ''}${dashboardData.transicao_qmf?.tendencia?.frios?.toFixed(2)}
  Media ultimos 20: ${dashboardData.transicao_qmf?.recentes?.slice(-1)?.[0]?.pct_q?.toFixed(1) || '?'}%Q / ${dashboardData.transicao_qmf?.recentes?.slice(-1)?.[0]?.pct_m?.toFixed(1) || '?'}%M / ${dashboardData.transicao_qmf?.recentes?.slice(-1)?.[0]?.pct_f?.toFixed(1) || '?'}%F`);

  parts.push(`## MELHORES NUMEROS POR POSICAO
${formatPositionPrevisao(dashboardData.previsao_posicional, dashboardData.numeros_por_jogo)}`);

  parts.push(`## ATRASOS POSICIONAIS CRITICOS
${formatAtrasados(dashboardData.atrasados_posicionais)}`);

  parts.push(`## CICLOS (AQUECENDO / ESFRIANDO)
${formatCiclos(dashboardData.ciclos)}`);

  parts.push(`## MEDIAS HISTORICAS
  Soma media: ${dashboardData.medias_historicas?.soma}
  Pares: ${dashboardData.medias_historicas?.pares} | Impares: ${dashboardData.medias_historicas?.impares}
  Primos: ${dashboardData.medias_historicas?.primos} | Fibonacci: ${dashboardData.medias_historicas?.fibonacci}
  Repetidos: ${dashboardData.medias_historicas?.repetidos} | Consecutivas: ${dashboardData.medias_historicas?.consecutivas}
  Amplitude media: ${dashboardData.medias_historicas?.amplitude}`);

  if (dashboardData.tem_trevos && dashboardData.trevos_quentes) {
    const tQ = dashboardData.trevos_quentes?.map((n: [number, number]) => n[0]) || [];
    const tF = dashboardData.trevos_frios?.map((n: [number, number]) => n[0]) || [];
    const tM = dashboardData.trevos_mornos?.map((n: [number, number]) => n[0]) || [];
    parts.push(`## TREVOS DA MAIS MILIONARIA
  Quentes: ${tQ.join(', ')}
  Mornos: ${tM.join(', ')}
  Frios: ${tF.join(', ')}`);
  }

  return parts.join('\n\n');
}
