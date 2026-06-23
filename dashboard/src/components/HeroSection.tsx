'use client';

import NumBadge from './NumBadge';
import type { UltimoSorteio, MediasHistoricas } from '@/types';

export default function HeroSection({ u, concurso, total, medias, nomeJogo, numerosPorJogo, totalNumeros }: {
  u: UltimoSorteio; concurso: number; total: number; medias: MediasHistoricas; nomeJogo?: string; numerosPorJogo?: number; totalNumeros?: number;
}) {
  const temTrevos = u.trevos && u.trevos.length > 0;
  const npj = numerosPorJogo ?? 15;
  const meio = Math.floor((1 + (totalNumeros ?? 25)) / 2);
  const maxNum = (totalNumeros ?? 25);
  return (
    <div className="relative overflow-hidden rounded-2xl p-6 sm:p-8 lg:p-10 mb-8 border border-[rgba(129,140,248,0.12)] animate-scale-in"
      style={{ background: 'linear-gradient(135deg,#0f1429 0%,#1a1040 50%,#0f1a2e 100%)' }}>
      <div className="hero-glow absolute inset-0" />
      <div className="absolute inset-0 opacity-[0.04]"
        style={{ background: 'radial-gradient(circle at 50% 0%, rgba(129,140,248,0.4) 0%, transparent 60%)' }} />
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-2">
          <span className="px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wider bg-emerald/15 text-emerald border border-emerald/20">
            {nomeJogo || 'Lotofácil'} · Último Sorteio · {concurso}
          </span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold mb-1 bg-gradient-to-r from-[#e0e7ff] via-[#a78bfa] to-[#34d399] bg-clip-text text-transparent"
          style={{ textShadow: '0 0 40px rgba(129,140,248,0.15)' }}>
          Resultado Oficial
        </h2>
        <p className="text-muted text-sm mb-6 sm:mb-8">{concurso} sorteios analisados</p>

        <div className="flex flex-wrap gap-2.5 mb-4 sm:mb-6">
          {u.numeros.map((n, i) => (
            <div key={`num-${i}`} className={`animate-slide-up`} style={{ animationDelay: `${i * 0.04}s` }}>
              <NumBadge n={n} />
            </div>
          ))}
        </div>

        {temTrevos && (
          <div className="mb-6 sm:mb-8">
            <p className="text-[11px] text-muted uppercase tracking-wider font-semibold mb-2">Trevos</p>
            <div className="flex flex-wrap gap-2.5">
              {u.trevos!.map((t, i) => (
                <div key={`trevo-${i}`} className="animate-slide-up" style={{ animationDelay: `${i * 0.04}s` }}>
                  <NumBadge n={t} />
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <HeroCard value={String(u.soma)} label="Soma Total" tip={`Média histórica: ${medias.soma}`} idx={0} />
          <HeroCard value={String(u.pares)} label="Pares" sub={u.pares_numeros.join(', ')} tip={`Média: ${medias.pares} por concurso (${(medias.pares / npj * 100).toFixed(0)}%)`} idx={1} />
          <HeroCard value={String(u.impares)} label="Ímpares" sub={u.impares_numeros.join(', ')} tip={`Média: ${medias.impares} por concurso (${(medias.impares / npj * 100).toFixed(0)}%)`} idx={2} />
          <HeroCard value={String(u.primos)} label="Primos" sub={u.primos_numeros.join(', ')} tip={`Média: ${medias.primos} por concurso`} idx={3} />
          <HeroCard value={String(u.fibonacci)} label="Fibonacci" sub={u.fibonacci_numeros.join(', ')} tip={`Média: ${medias.fibonacci} por concurso`} idx={4} />
          <HeroCard value={String(u.repetidos)} label="Repetidos" sub={u.repetidos_numeros.join(', ')} tip={`Média: ${medias.repetidos} por concurso`} idx={5} />
          <HeroCard value={String(u.consecutivas)} label="Consecutivas" sub={u.consecutivas_pares.join(' · ')} tip={`Média: ${medias.consecutivas} pares consecutivos por concurso`} idx={6} />
          <HeroCard value={String(u.amplitude)} label="Amplitude" tip={`Média histórica: ${medias.amplitude}`} idx={7} />
          <HeroCard value={String(u.baixos)} label={`Baixos (1-${meio})`} sub={u.baixos_numeros.join(', ')} tip={`Média: ${medias.baixos} por concurso`} idx={8} />
          <HeroCard value={String(u.altos)} label={`Altos (${meio+1}-${maxNum})`} sub={u.altos_numeros.join(', ')} tip={`Média: ${medias.altos} por concurso`} idx={9} />
          <HeroCard value={String(u.multiplos_3)} label="Múlt. 3" sub={u.multiplos_3_numeros.join(', ')} tip={`Média: ${medias.multiplos_3} por concurso`} idx={10} />
          <HeroCard value={String(u.multiplos_5)} label="Múlt. 5" sub={u.multiplos_5_numeros.join(', ')} tip={`Média: ${medias.multiplos_5} por concurso`} idx={11} />
        </div>
      </div>
    </div>
  );
}

function HeroCard({ value, label, sub, tip, idx = 0 }: { value: string; label: string; sub?: string; tip?: string; idx?: number }) {
  return (
    <div
      className="bg-white/4 rounded-xl p-4 border border-white/6 text-center relative group cursor-default transition-all duration-200 hover:bg-white/[0.06] hover:-translate-y-0.5 hover:border-accent-2/20 animate-slide-up"
      style={{ animationDelay: `${0.3 + idx * 0.04}s` }}
    >
      {tip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 rounded-lg bg-[#1a1040] border border-[rgba(129,140,248,0.2)] text-[11px] text-[#e0e7ff] whitespace-nowrap opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none z-20 shadow-lg max-w-[260px] overflow-hidden text-ellipsis">
          {tip}
        </div>
      )}
      <div className="text-xl sm:text-2xl font-bold text-white">{value}</div>
      <div className="text-[11px] text-muted uppercase tracking-wide mt-1">{label}</div>
      {sub && <div className="text-[10px] text-accent-2/70 mt-0.5 font-mono truncate max-w-full" title={sub}>{sub}</div>}
    </div>
  );
}
