'use client';

import NumBadge from './NumBadge';
import type { AnaliseGruposData } from '@/lib/analise-grupos';

export default function GruposSection({ data }: { data: AnaliseGruposData }) {
  if (!data) return null;

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-2 text-[#e0e7ff] flex items-center gap-2">
        Análise por Grupos
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">Coringa {data.coringa}</span>
      </h3>
      <p className="text-xs text-muted mb-4">
        Coringa {data.coringa} removido → acerto de 14 números em A+B+C = sucesso.
        Média histórica: <strong className="text-white">{(data.media_acertos_total).toFixed(1)}</strong> acertos/grupo.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {(['A', 'B', 'C'] as const).map((g, idx) => {
          const s = data.stats[g];
          return (
            <div key={g}
              className="rounded-xl p-5 border border-[rgba(129,140,248,0.12)] bg-white/3 transition-all duration-200 hover:bg-white/[0.05] hover:-translate-y-0.5 animate-slide-up"
              style={{ animationDelay: `${idx * 0.08}s` }}
            >
              <h4 className="text-sm font-bold text-[#e0e7ff] mb-2">{g === 'A' ? '🟦' : g === 'B' ? '🟩' : '🟪'} Grupo {g}</h4>
              <div className="flex flex-wrap gap-1 mb-3">
                {data.grupos[g].map(n => <NumBadge key={n} n={n} />)}
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="bg-white/5 rounded-lg p-2">
                  <div className="text-lg font-bold text-[#a78bfa]">{s.media}</div>
                  <div className="text-muted">Média</div>
                </div>
                <div className="bg-white/5 rounded-lg p-2">
                  <div className="text-lg font-bold text-[#6ee7b7]">{s.min}-{s.max}</div>
                  <div className="text-muted">Min-Max</div>
                </div>
                <div className="bg-white/5 rounded-lg p-2">
                  <div className="text-lg font-bold text-[#fdba74]">{s.moda.join(', ')}</div>
                  <div className="text-muted">Moda</div>
                </div>
              </div>
              <div className="mt-2 text-xs text-muted text-center">σ = {s.desvio} · freq 30: {s.freq_30}/{s.freq_30_esperada}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-xl p-5 border border-[rgba(129,140,248,0.12)] bg-white/3 transition-all duration-200 hover:bg-white/[0.05]">
          <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">Composições Mais Comuns (A, B, C)</h4>
          <div className="space-y-1.5">
            {data.composicoes_comuns.slice(0, 10).map((c, i) => {
              const totalNumeros = c.a + c.b + c.c;
              const sucesso = totalNumeros === 14;
              return (
                <div key={i}
                  className={`flex items-center justify-between text-xs px-3 py-2 rounded-lg transition-colors ${sucesso ? 'bg-[rgba(52,211,153,0.1)] border border-[rgba(52,211,153,0.15)]' : 'bg-white/4 hover:bg-white/[0.06]'}`}>
                  <span className="font-mono">
                    <span className="text-[#a78bfa]">{c.a}</span>
                    {' '}<span className="text-muted">·</span>{' '}
                    <span className="text-[#6ee7b7]">{c.b}</span>
                    {' '}<span className="text-muted">·</span>{' '}
                    <span className="text-[#c084fc]">{c.c}</span>
                    <span className="text-muted ml-1">= {totalNumeros}</span>
                    {sucesso && <span className="ml-1 text-[#6ee7b7]">✅</span>}
                  </span>
                  <span className="text-muted">{c.freq}x ({c.pct}%)</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-xl p-5 border border-[rgba(129,140,248,0.12)] bg-white/3 transition-all duration-200 hover:bg-white/[0.05]">
          <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">Últimos 30 Concursos</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-muted border-b border-white/6">
                  <th className="text-left py-2 pr-2">Concurso</th>
                  <th className="text-center px-1">Coringa</th>
                  <th className="text-center px-1 text-[#a78bfa]">A</th>
                  <th className="text-center px-1 text-[#6ee7b7]">B</th>
                  <th className="text-center px-1 text-[#c084fc]">C</th>
                  <th className="text-center pl-1">Σ</th>
                </tr>
              </thead>
              <tbody>
                {data.ultimos.map(r => {
                  const sum = r.A + r.B + r.C;
                  const sucesso = sum === 14;
                  return (
                    <tr key={r.concurso}
                      className={`border-b border-white/4 transition-colors ${sucesso ? 'bg-[rgba(52,211,153,0.05)]' : 'hover:bg-white/4'}`}>
                      <td className="py-1.5 pr-2 text-muted">#{r.concurso}</td>
                      <td className="text-center px-1">{r.coringa ? '✅' : '❌'}</td>
                      <td className="text-center px-1 text-[#a78bfa] font-mono">{r.A}</td>
                      <td className="text-center px-1 text-[#6ee7b7] font-mono">{r.B}</td>
                      <td className="text-center px-1 text-[#c084fc] font-mono">{r.C}</td>
                      <td className={`text-center pl-1 font-mono ${sucesso ? 'text-[#6ee7b7] font-bold' : ''}`}>{sum}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="mt-3 text-xs text-muted">
            Coringa frequência histórica: <strong className="text-white">{(data.coringa_freq / data.total_sorteios * 100).toFixed(1)}%</strong>
            {' · '}últimos 30: <strong className="text-white">{(data.coringa_freq_30 / 30 * 100).toFixed(1)}%</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
