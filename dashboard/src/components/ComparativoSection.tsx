'use client';

import type { TendenciaComparativo } from '@/types';

export default function ComparativoSection({ data }: { data: TendenciaComparativo[] }) {
  if (!data || data.length === 0) return null;

  const maxVal = Math.max(...data.flatMap(d => [d.maiores, d.menores, d.iguais]));

  return (
    <div className="rounded-xl border border-white/6 bg-white/3 p-5 animate-slide-up">
      <h3 className="text-lg font-semibold text-[#e0e7ff] mb-4">
        Tendência Posicional
        <span className="text-xs text-muted font-normal ml-2">últimos {data.length} sorteios</span>
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[11px] text-muted uppercase tracking-wider border-b border-white/6">
              <th className="text-left py-2 pr-3">Concurso</th>
              <th className="text-center px-2 py-2">▲ Maiores</th>
              <th className="text-center px-2 py-2">▼ Menores</th>
              <th className="text-center px-2 py-2">= Iguais</th>
              <th className="text-left pl-3 py-2">Barra</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.concurso} className="border-b border-white/4 hover:bg-white/4 transition-colors">
                <td className="py-2 pr-3 text-muted font-mono text-xs">{d.concurso}</td>
                <td className="text-center px-2 py-2">
                  <span className="text-emerald font-semibold">{d.maiores}</span>
                </td>
                <td className="text-center px-2 py-2">
                  <span className="text-hot font-semibold">{d.menores}</span>
                </td>
                <td className="text-center px-2 py-2">
                  <span className="text-accent-2/70 font-semibold">{d.iguais}</span>
                </td>
                <td className="pl-3 py-2">
                  <div className="flex items-center gap-0.5 h-5">
                    <div
                      className="h-full rounded-l-sm transition-all"
                      style={{
                        width: `${(d.maiores / maxVal) * 60}px`,
                        background: '#34d399',
                        opacity: 0.8,
                      }}
                      title={`${d.maiores} maiores`}
                    />
                    <div
                      className="h-full transition-all"
                      style={{
                        width: `${(d.iguais / maxVal) * 60}px`,
                        background: '#818cf8',
                        opacity: 0.4,
                      }}
                      title={`${d.iguais} iguais`}
                    />
                    <div
                      className="h-full rounded-r-sm transition-all"
                      style={{
                        width: `${(d.menores / maxVal) * 60}px`,
                        background: '#ef4444',
                        opacity: 0.8,
                      }}
                      title={`${d.menores} menores`}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center gap-4 mt-3 text-[11px] text-muted">
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-emerald opacity-80" /> ▲ Maior que anterior</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#818cf8] opacity-40" /> = Igual</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-hot opacity-80" /> ▼ Menor que anterior</span>
      </div>
    </div>
  );
}
