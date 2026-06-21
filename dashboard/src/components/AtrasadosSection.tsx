'use client';

import type { AtrasadoItem } from '@/types';

export default function AtrasadosSection({ atrasados }: { atrasados: Record<string, AtrasadoItem[]> }) {
  const keys = Object.keys(atrasados);
  if (keys.length === 0) return null;

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
        Números Atrasados por Posição
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">P(gap) &lt; 5%</span>
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {keys.map((pos, idx) => (
          <div
            key={pos}
            className="rounded-xl p-4 border border-[rgba(239,68,68,0.1)] bg-white/3 transition-all duration-200 hover:bg-white/[0.05] hover:-translate-y-0.5 animate-slide-up"
            style={{ animationDelay: `${idx * 0.04}s` }}
          >
            <div className="text-xs text-muted font-medium mb-1">{pos}</div>
            <div className="flex flex-wrap gap-1">
              {atrasados[pos].map((x, i) => {
                const severity = x.p_gap < 0.01 ? 'intense' : x.p_gap < 0.03 ? 'medium' : 'mild';
                const colors = {
                  intense: 'bg-[rgba(239,68,68,0.25)] text-[#fca5a5] border-[rgba(239,68,68,0.35)]',
                  medium: 'bg-[rgba(239,68,68,0.15)] text-[#fca5a5] border-[rgba(239,68,68,0.2)]',
                  mild: 'bg-[rgba(251,146,60,0.15)] text-[#fdba74] border-[rgba(251,146,60,0.2)]',
                };
                return (
                  <span key={i}
                    className={`w-7 h-7 flex items-center justify-center rounded-lg text-[11px] font-semibold transition-all duration-200 hover:scale-110 ${colors[severity]}`}
                    title={`gap=${x.gap} · P(gap)=${(x.p_gap * 100).toFixed(1)}%`}>
                    {x.numero}
                  </span>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
