'use client';

import { useState } from 'react';
import type { QuarentenaColuna } from '@/types';

const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const COL_NAMES = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7'];

const STATUS_CONFIG = {
  quarentena: { label: 'Q', color: 'bg-[#ef4444]/25 text-[#fca5a5] border-[#ef4444]/35', title: 'Quarentena - saiu recentemente' },
  normal: { label: 'N', color: 'bg-white/5 text-[#94a3b8] border-white/10', title: 'Normal' },
  atrasado: { label: 'A', color: 'bg-[#f59e0b]/20 text-[#fcd34d] border-[#f59e0b]/30', title: 'Atrasado - deve voltar em breve' },
  muito_atrasado: { label: 'M', color: 'bg-[#3b82f6]/25 text-[#93c5fd] border-[#3b82f6]/40', title: 'Muito atrasado - acima do P90' },
  rara: { label: 'R', color: 'bg-[#a78bfa]/15 text-[#c4b5fd] border-[#a78bfa]/25', title: 'Rara estrutural - probabilidade muito baixa, atraso não é sinal' },
  inviavel: { label: '·', color: 'bg-transparent text-[#3f4a5f] border-white/5', title: 'Inviável - não pode ocorrer nesta posição' },
};

export default function QuarantineMatrix({ quarentena }: { quarentena: Record<string, QuarentenaColuna> }) {
  const [hoveredCell, setHoveredCell] = useState<{ col: string; dig: number } | null>(null);

  const hoveredInfo = hoveredCell
    ? quarentena[hoveredCell.col]?.digitos.find(d => d.digito === hoveredCell.dig)
    : null;

  const totalQ = COL_NAMES.reduce((s, c) => s + (quarentena[c]?.em_quarentena.length || 0), 0);
  const totalA = COL_NAMES.reduce((s, c) => s + (quarentena[c]?.atrasados.length || 0), 0);
  const totalM = COL_NAMES.reduce((s, c) => s + (quarentena[c]?.muito_atrasados.length || 0), 0);

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
      <h3 className="text-sm font-semibold text-[#c7d2fe] mb-4 flex items-center gap-2">
        <span>🛡️</span>
        Matriz de Quarentena Dinâmica
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
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="text-xs text-muted p-2 text-left w-12">Dig</th>
              {COL_NAMES.map(col => (
                <th key={col} className="text-xs text-[#818cf8] font-bold p-2 text-center">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {DIGITS.map(d => (
              <tr key={d}>
                <td className="text-xs text-muted p-2 font-mono">{d}</td>
                {COL_NAMES.map(col => {
                  const info = quarentena[col]?.digitos.find(di => di.digito === d);
                  if (!info) return <td key={col} className="p-1"><span className="text-xs text-muted">?</span></td>;
                  const cfg = STATUS_CONFIG[info.status];
                  const isHovered = hoveredCell?.col === col && hoveredCell?.dig === d;
                  return (
                    <td key={col} className="p-1">
                      <div
                        className={`w-full h-9 flex items-center justify-center rounded-lg text-xs font-bold border cursor-pointer transition-all ${cfg.color} ${isHovered ? 'scale-110 ring-1 ring-white/20' : ''}`}
                        title={`${cfg.title} | gap=${info.gap_atual} média=${info.media} P90=${info.p90}`}
                        onMouseEnter={() => setHoveredCell({ col, dig: d })}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        {cfg.label}
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
            <span className="text-[#818cf8] font-bold">{hoveredCell.col}</span>
            <span className="text-muted">dígito</span>
            <span className="text-[#c7d2fe] font-bold">{hoveredInfo.digito}</span>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-muted">
            <span>Gap atual: <span className="text-[#c7d2fe]">{hoveredInfo.gap_atual}</span> sorteios</span>
            <span>Média: <span className="text-[#c7d2fe]">{hoveredInfo.media}</span></span>
            <span>Mediana: <span className="text-[#c7d2fe]">{hoveredInfo.mediana}</span></span>
            <span>P90: <span className="text-[#c7d2fe]">{hoveredInfo.p90}</span></span>
            <span>Sigma: <span className="text-[#c7d2fe]">{hoveredInfo.sigma}</span></span>
            <span>Status: <span className={`font-bold ${
              hoveredInfo.status === 'quarentena' ? 'text-[#fca5a5]' :
              hoveredInfo.status === 'muito_atrasado' ? 'text-[#93c5fd]' :
              hoveredInfo.status === 'atrasado' ? 'text-[#fcd34d]' : 'text-muted'
            }`}>{STATUS_CONFIG[hoveredInfo.status].title}</span></span>
          </div>
        </div>
      )}

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-lg p-3 bg-[#ef4444]/5 border border-[#ef4444]/10">
          <p className="text-xs text-[#fca5a5] font-medium mb-1">Em Quarentena</p>
          <div className="flex flex-wrap gap-1">
            {COL_NAMES.map(col =>
              quarentena[col]?.em_quarentena.map(d => (
                <span key={`${col}-${d}`} className="text-[10px] px-1.5 py-0.5 rounded bg-[#ef4444]/15 text-[#fca5a5]">
                  {col}:{d}
                </span>
              ))
            )}
          </div>
        </div>
        <div className="rounded-lg p-3 bg-[#f59e0b]/5 border border-[#f59e0b]/10">
          <p className="text-xs text-[#fcd34d] font-medium mb-1">Atrasados</p>
          <div className="flex flex-wrap gap-1">
            {COL_NAMES.map(col =>
              quarentena[col]?.atrasados.map(d => (
                <span key={`${col}-${d}`} className="text-[10px] px-1.5 py-0.5 rounded bg-[#f59e0b]/15 text-[#fcd34d]">
                  {col}:{d}
                </span>
              ))
            )}
          </div>
        </div>
        <div className="rounded-lg p-3 bg-[#3b82f6]/5 border border-[#3b82f6]/10">
          <p className="text-xs text-[#93c5fd] font-medium mb-1">Muito Atrasados</p>
          <div className="flex flex-wrap gap-1">
            {COL_NAMES.map(col =>
              quarentena[col]?.muito_atrasados.map(d => (
                <span key={`${col}-${d}`} className="text-[10px] px-1.5 py-0.5 rounded bg-[#3b82f6]/15 text-[#93c5fd]">
                  {col}:{d}
                </span>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
