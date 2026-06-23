'use client';

import type { CicloInfo } from '@/types';
import NumBadge from './NumBadge';

export default function TrevoSection({
  trevosUltimo,
  frequenciaTotal,
  frequenciaRecente,
  gaps,
  quentes,
  frios,
  mornos,
  ciclos,
  janela,
}: {
  trevosUltimo: number[];
  frequenciaTotal: Record<string, number>;
  frequenciaRecente: Record<string, number>;
  gaps: Record<string, number>;
  quentes: [number, number][];
  frios: [number, number][];
  mornos: [number, number][];
  ciclos: Record<string, CicloInfo>;
  janela: number;
}) {
  if (!trevosUltimo?.length) return null;

  return (
    <div className="mb-8">
      <div className="rounded-xl p-5 border border-amber/20 bg-gradient-to-r from-[rgba(245,158,11,0.05)] to-[rgba(217,119,6,0.02)]">
        <h3 className="text-lg font-semibold mb-4 text-[#fcd34d] flex items-center gap-2">
          <span>✨ Trevos</span>
          <span className="text-[11px] bg-amber/15 text-amber px-2 py-0.5 rounded font-normal">
            análise estatística
          </span>
        </h3>

        <div className="flex flex-wrap gap-2 mb-5">
          {trevosUltimo.map((t, i) => (
            <div key={`trevo-${i}`}>
              <NumBadge n={t} />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          {Object.entries(frequenciaTotal)
            .sort(([, a], [, b]) => Number(b) - Number(a))
            .map(([n, f]) => {
              const rec = frequenciaRecente[n] || 0;
              const gap = gaps[n] ?? 0;
              const ciclo = ciclos[n];
              return (
                <div key={`trevo-stat-${n}`}
                  className="rounded-xl p-4 border border-white/6 bg-white/3 transition-all duration-200 hover:bg-white/[0.05]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-[#fcd34d]">Trevo {n}</span>
                    {ciclo && (
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
                        ciclo.estado === 'aquecendo' ? 'bg-hot/15 text-hot' :
                        ciclo.estado === 'esfriando' ? 'bg-cold/15 text-cold' :
                        'bg-white/10 text-muted'
                      }`}>
                        {ciclo.estado === 'aquecendo' ? '🔥 aquecendo' :
                         ciclo.estado === 'esfriando' ? '🧊 esfriando' :
                         'estável'}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div>
                      <div className="text-lg font-bold text-white">{f}</div>
                      <div className="text-muted mt-0.5">total</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-white">{rec}</div>
                      <div className="text-muted mt-0.5">últ. {janela}</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-white">{gap}</div>
                      <div className="text-muted mt-0.5">ausente</div>
                    </div>
                  </div>
                </div>
              );
            })}
        </div>

        <div className="flex flex-wrap gap-3">
          {quentes.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-hot font-semibold">🔥 Quentes:</span>
              {quentes.map(([n]) => (
                <span key={`tq-${n}`} className="text-xs font-mono text-hot/80">{n}</span>
              ))}
            </div>
          )}
          {mornos.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-muted font-semibold">💨 Mornos:</span>
              {mornos.map(([n]) => (
                <span key={`tm-${n}`} className="text-xs font-mono text-muted">{n}</span>
              ))}
            </div>
          )}
          {frios.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-cold font-semibold">🧊 Frios:</span>
              {frios.map(([n]) => (
                <span key={`tf-${n}`} className="text-xs font-mono text-cold/80">{n}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
