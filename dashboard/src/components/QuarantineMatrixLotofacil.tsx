'use client';

import { useState } from 'react';
import type { QuarentenaPosicaoLF } from '@/types';

const STATUS_CONFIG = {
  quarentena: { label: 'Q', color: 'bg-[#ef4444]/25 text-[#fca5a5] border-[#ef4444]/35', title: 'Quarentena - saiu nos últimos 3 concursos' },
  normal: { label: 'N', color: 'bg-white/5 text-[#94a3b8] border-white/10', title: 'Normal' },
  atrasado: { label: 'A', color: 'bg-[#f59e0b]/20 text-[#fcd34d] border-[#f59e0b]/30', title: 'Atrasado - gap >= 1.75x o esperado' },
  muito_atrasado: { label: 'M', color: 'bg-[#3b82f6]/25 text-[#93c5fd] border-[#3b82f6]/40', title: 'Muito atrasado - gap >= 3x o esperado' },
  rara: { label: 'R', color: 'bg-[#a78bfa]/15 text-[#c4b5fd] border-[#a78bfa]/25', title: 'Rara estrutural - probabilidade muito baixa, atraso não é sinal' },
  inviavel: { label: '·', color: 'bg-transparent text-[#3f4a5f] border-white/5', title: 'Inviável - não pode ocorrer nesta posição' },
};

export default function QuarantineMatrixLotofacil({
  quarentena,
  numerosSorteados = [],
}: {
  quarentena: Record<string, QuarentenaPosicaoLF>;
  numerosSorteados?: number[];
}) {
  const [hoveredCell, setHoveredCell] = useState<{ pos: string; num: number } | null>(null);
  const sorteadosSet = new Set(numerosSorteados);

  const positions = Object.keys(quarentena).sort((a, b) => {
    const numA = parseInt(a.substring(1));
    const numB = parseInt(b.substring(1));
    return numA - numB;
  });

  const allNums = quarentena[positions[0]]?.numeros.map(n => n.digito) || [];

  const hoveredInfo = hoveredCell
    ? quarentena[hoveredCell.pos]?.numeros.find(n => n.digito === hoveredCell.num)
    : null;

  const totalQ = positions.reduce((s, p) => s + (quarentena[p]?.em_quarentena.length || 0), 0);
  const totalA = positions.reduce((s, p) => s + (quarentena[p]?.atrasados.length || 0), 0);
  const totalM = positions.reduce((s, p) => s + (quarentena[p]?.muito_atrasados.length || 0), 0);
  const totalR = positions.reduce((s, p) => s + (quarentena[p]?.numeros.filter(n => n.status === 'rara').length || 0), 0);

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
      <h3 className="text-sm font-semibold text-[#c7d2fe] mb-4 flex items-center gap-2">
        <span>🛡️</span>
        Matriz de Quarentena por Posição - Lotofácil
      </h3>

      <div className="flex gap-4 mb-4 text-xs">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-[#ef4444]/25 border border-[#ef4444]/35" />
          Q = Quarentena ({totalQ})
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-white/5 border border-white/10" />
          N = Normal
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-[#f59e0b]/20 border border-[#f59e0b]/30" />
          A = Atrasado ({totalA})
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-[#3b82f6]/25 border border-[#3b82f6]/40" />
          M = Muito Atrasado ({totalM})
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-[#a78bfa]/15 border border-[#a78bfa]/25" />
          R = Rara estrutural ({totalR})
        </span>
        <span className="text-muted">· = célula inviável na posição</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="text-xs text-muted p-2 text-left w-12">Núm</th>
              {positions.map(pos => (
                <th key={pos} className="text-xs text-[#818cf8] font-bold p-2 text-center">{pos}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {allNums.map(num => (
              <tr key={num}>
                <td className={`text-xs p-2 font-mono ${sorteadosSet.has(num) ? 'text-emerald font-bold' : 'text-muted'}`}>{num}</td>
                {positions.map(pos => {
                  const info = quarentena[pos]?.numeros.find(n => n.digito === num);
                  if (!info) return <td key={pos} className="p-1"><span className="text-xs text-muted">?</span></td>;
                  const cfg = STATUS_CONFIG[info.status];
                  const inviavel = info.status === 'inviavel';
                  const isHovered = hoveredCell?.pos === pos && hoveredCell?.num === num;
                  const posIdx = parseInt(pos.substring(1), 10) - 1;
                  const sorteadoNaPosicao = numerosSorteados[posIdx] === num;
                  return (
                    <td key={pos} className="p-1">
                      <div
                        className={`w-full h-8 flex items-center justify-center rounded-lg text-xs font-bold border ${inviavel
                          ? 'cursor-default'
                          : `cursor-pointer transition-all ${cfg.color} ${isHovered ? 'scale-110 ring-1 ring-white/20' : ''}`} ${sorteadoNaPosicao ? 'ring-1 ring-emerald/50 shadow-[0_0_10px_rgba(52,211,153,0.35)]' : ''}`}
                        title={inviavel
                          ? 'Inviável — não pode ocorrer nesta posição'
                          : `${cfg.title} | gap=${info.gap_atual} esperado=${info.gap_esperado ?? '—'} P90=${info.p90}`}
                        onMouseEnter={inviavel ? undefined : () => setHoveredCell({ pos, num })}
                        onMouseLeave={inviavel ? undefined : () => setHoveredCell(null)}
                      >
                        {inviavel ? '·' : <span className={sorteadoNaPosicao ? 'text-emerald' : ''}>{cfg.label}</span>}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hoveredInfo && hoveredCell && (
        <div className="mt-3 p-3 rounded-lg bg-white/[0.03] border border-white/[0.06] text-xs space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[#818cf8] font-bold">{hoveredCell.pos}</span>
            <span className="text-muted">número</span>
            <span className="text-[#c7d2fe] font-bold">{hoveredInfo.digito}</span>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-muted">
            <span>Gap atual: <span className="text-[#c7d2fe]">{hoveredInfo.gap_atual}</span> sorteios</span>
            <span>Gap esperado: <span className="text-[#c7d2fe]">{hoveredInfo.gap_esperado ?? '—'}</span></span>
            <span>P teórica: <span className="text-[#c7d2fe]">{((hoveredInfo.prob_teorica ?? 0) * 100).toFixed(3)}%</span></span>
            <span>Média: <span className="text-[#c7d2fe]">{hoveredInfo.media}</span></span>
            <span>Mediana: <span className="text-[#c7d2fe]">{hoveredInfo.mediana}</span></span>
            <span>P90: <span className="text-[#c7d2fe]">{hoveredInfo.p90}</span></span>
            <span>Sigma: <span className="text-[#c7d2fe]">{hoveredInfo.sigma}</span></span>
            <span>Status: <span className={`font-bold ${
              hoveredInfo.status === 'quarentena' ? 'text-[#fca5a5]' :
              hoveredInfo.status === 'muito_atrasado' ? 'text-[#93c5fd]' :
              hoveredInfo.status === 'atrasado' ? 'text-[#fcd34d]' :
              hoveredInfo.status === 'rara' ? 'text-[#c4b5fd]' : 'text-muted'
            }`}>{STATUS_CONFIG[hoveredInfo.status].title}</span></span>
          </div>
        </div>
      )}

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-lg p-3 bg-[#ef4444]/5 border border-[#ef4444]/10">
          <p className="text-xs text-[#fca5a5] font-medium mb-1">Em Quarentena</p>
          <div className="flex flex-wrap gap-1">
            {positions.map(pos =>
              quarentena[pos]?.em_quarentena.map(num => (
                <span key={`${pos}-${num}`} className="text-[10px] px-1.5 py-0.5 rounded bg-[#ef4444]/15 text-[#fca5a5]">
                  {pos}:{num}
                </span>
              ))
            )}
          </div>
        </div>
        <div className="rounded-lg p-3 bg-[#f59e0b]/5 border border-[#f59e0b]/10">
          <p className="text-xs text-[#fcd34d] font-medium mb-1">Atrasados</p>
          <div className="flex flex-wrap gap-1">
            {positions.map(pos =>
              quarentena[pos]?.atrasados.map(num => (
                <span key={`${pos}-${num}`} className="text-[10px] px-1.5 py-0.5 rounded bg-[#f59e0b]/15 text-[#fcd34d]">
                  {pos}:{num}
                </span>
              ))
            )}
          </div>
        </div>
        <div className="rounded-lg p-3 bg-[#3b82f6]/5 border border-[#3b82f6]/10">
          <p className="text-xs text-[#93c5fd] font-medium mb-1">Muito Atrasados</p>
          <div className="flex flex-wrap gap-1">
            {positions.map(pos =>
              quarentena[pos]?.muito_atrasados.map(num => (
                <span key={`${pos}-${num}`} className="text-[10px] px-1.5 py-0.5 rounded bg-[#3b82f6]/15 text-[#93c5fd]">
                  {pos}:{num}
                </span>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
