'use client';

import NumBadge from './NumBadge';

export default function CiclosSection({ ciclos }: { ciclos: Record<string, { estado: string }> }) {
  if (!ciclos) return null;

  const aquecendo = Object.entries(ciclos).filter(([_, c]) => c.estado === 'aquecendo').map(([n]) => Number(n));
  const esfriando = Object.entries(ciclos).filter(([_, c]) => c.estado === 'esfriando').map(([n]) => Number(n));

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
        Ciclos de Frequência
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">freq 30 vs esperado</span>
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl p-5 border border-[rgba(52,211,153,0.2)] bg-white/3 transition-all duration-200 hover:bg-white/[0.05] animate-slide-up"
          style={{ animationDelay: '0s' }}>
          <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">🟢 Aquecendo</h4>
          <div className="flex flex-wrap gap-1.5">
            {aquecendo.map(n => <NumBadge key={n} n={n} className="bg-[rgba(52,211,153,0.2)] text-[#6ee7b7] border border-[rgba(52,211,153,0.3)]" />)}
            {aquecendo.length === 0 && <span className="text-xs text-muted">Nenhum</span>}
          </div>
        </div>
        <div className="rounded-xl p-5 border border-[rgba(251,146,60,0.2)] bg-white/3 transition-all duration-200 hover:bg-white/[0.05] animate-slide-up"
          style={{ animationDelay: '0.08s' }}>
          <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">🟠 Esfriando</h4>
          <div className="flex flex-wrap gap-1.5">
            {esfriando.map(n => <NumBadge key={n} n={n} className="bg-[rgba(251,146,60,0.2)] text-[#fdba74] border border-[rgba(251,146,60,0.3)]" />)}
            {esfriando.length === 0 && <span className="text-xs text-muted">Nenhum</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
