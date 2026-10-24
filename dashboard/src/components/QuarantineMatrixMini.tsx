'use client';

import type { QuarentenaPosicaoLF } from '@/types';

const STATUS_CONFIG = {
  quarentena: { label: 'Q', color: 'bg-[#ef4444]/25 text-hot-bright border-[#ef4444]/35', title: 'Quarentena - saiu nos últimos 3 concursos' },
  normal: { label: 'N', color: 'bg-white/5 text-warm border-white/10', title: 'Normal' },
  atrasado: { label: 'A', color: 'bg-[#f59e0b]/20 text-[#fcd34d] border-[#f59e0b]/30', title: 'Atrasado - gap >= 1.75x o esperado' },
  muito_atrasado: { label: 'M', color: 'bg-[#3b82f6]/25 text-[#93c5fd] border-[#3b82f6]/40', title: 'Muito atrasado - gap >= 3x o esperado' },
  rara: { label: 'R', color: 'bg-[#a78bfa]/15 text-[#c4b5fd] border-[#a78bfa]/25', title: 'Rara estrutural - probabilidade muito baixa, atraso não é sinal' },
  inviavel: { label: '·', color: 'bg-transparent text-[#3f4a5f] border-white/5', title: 'Inviável - não pode ocorrer nesta posição' },
};

export default function QuarantineMatrixMini({
  quarentena,
  numerosSorteados = [],
}: {
  quarentena: Record<string, QuarentenaPosicaoLF>;
  numerosSorteados?: number[];
}) {
  const sorteadosSet = new Set(numerosSorteados);

  const positions = Object.keys(quarentena).sort((a, b) => {
    return parseInt(a.substring(1), 10) - parseInt(b.substring(1), 10);
  });

  if (positions.length === 0) return null;

  const numeros = (quarentena[positions[0]]?.numeros.map(n => n.digito) || [])
    .sort((a, b) => a - b);

  const totalQ = positions.reduce((s, p) => s + (quarentena[p]?.em_quarentena.length || 0), 0);
  const totalA = positions.reduce((s, p) => s + (quarentena[p]?.atrasados.length || 0), 0);
  const totalM = positions.reduce((s, p) => s + (quarentena[p]?.muito_atrasados.length || 0), 0);
  const totalR = positions.reduce((s, p) => s + (quarentena[p]?.numeros.filter(n => n.status === 'rara').length || 0), 0);

  return (
    <div className="rounded-xl border border-[rgba(129,140,248,0.15)] bg-white/5 p-3 w-fit max-w-full">
      <div className="text-[11px] font-semibold text-[#c7d2fe] mb-2 flex items-center gap-1.5">
        <span>🛡️</span> Quarentena (mini)
        <span className="ml-auto font-normal text-[10px] text-muted">número × posição</span>
      </div>
      <div className="overflow-x-auto">
        <table className="border-collapse">
          <thead>
            <tr>
              <th className="text-[9px] text-muted px-0.5 py-0.5 sticky left-0 bg-[#1a1d2e] z-10 text-right pr-1.5">N</th>
              {positions.map(pos => (
                <th key={pos} className="text-[9px] text-accent-2 font-bold px-0.5 py-0.5 text-center">{pos.replace('N', '')}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {numeros.map(num => (
              <tr key={num}>
                <td className={`text-[9px] px-0.5 py-0.5 sticky left-0 bg-[#1a1d2e] z-10 text-right pr-1.5 font-mono ${sorteadosSet.has(num) ? 'text-emerald font-bold' : 'text-muted'}`}>{num}</td>
                {positions.map(pos => {
                  const info = quarentena[pos]?.numeros.find(n => n.digito === num);
                  if (!info) return <td key={pos} className="p-[1px]"><span className="text-[8px] text-muted">?</span></td>;
                  const cfg = STATUS_CONFIG[info.status];
                  const inviavel = info.status === 'inviavel';
                  const posIdx = parseInt(pos.substring(1), 10) - 1;
                  const sorteadoNaPosicao = numerosSorteados[posIdx] === num;
                  return (
                    <td key={pos} className="p-[2px]">
                      <div
                        className={`w-5 h-5 min-w-5 flex items-center justify-center rounded-[3px] text-[9px] leading-none font-bold border ${cfg.color} ${sorteadoNaPosicao ? 'ring-1 ring-emerald/60' : ''}`}
                        title={inviavel
                          ? 'Inviável — não pode ocorrer nesta posição'
                          : `${cfg.title} | gap=${info.gap_atual} esperado=${info.gap_esperado ?? '—'} P90=${info.p90}`}
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
      <div className="flex flex-wrap gap-x-2 gap-y-0.5 mt-2 text-[10px] text-muted">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-[#ef4444]/40 border border-[#ef4444]/50" /> Q {totalQ}</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-white/10 border border-white/20" /> N</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-[#f59e0b]/30 border border-[#f59e0b]/40" /> A {totalA}</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-[#3b82f6]/35 border border-[#3b82f6]/45" /> M {totalM}</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-[#a78bfa]/25 border border-[#a78bfa]/35" /> R {totalR}</span>
      </div>
    </div>
  );
}