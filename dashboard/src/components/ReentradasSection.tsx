'use client';

import { useEffect, useState } from 'react';

type Report = {
  total_concursos: number;
  total_numeros?: number;
  numeros_por_jogo: number;
  records: { concurso: number; [k: string]: any }[];
  distribuicao: Record<string, number>;
  distribuicao_pct: Record<string, string>;
  media: number;
  mediana: number;
  moda: number;
  min: number;
  max: number;
  desvio: number;
};

type Aba = 'reentradas' | 'repetidos' | 'persistencia';

const ABA_LABELS: Record<Aba, { titulo: string; desc: string }> = {
  reentradas: { titulo: 'Reentradas', desc: 'Dos não sorteados do anterior, quantos voltam no seguinte?' },
  repetidos: { titulo: 'Repetidos', desc: 'Dos sorteados do anterior, quantos repetem no seguinte?' },
  persistencia: { titulo: 'Persistência', desc: 'Dos números que REPETIRAM (anterior→atual), quantos persistem no PRÓXIMO?' },
};

export default function ReentradasSection() {
  const [aba, setAba] = useState<Aba>('reentradas');
  const [data, setData] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadedAba, setLoadedAba] = useState<Aba | null>(null);

  useEffect(() => {
    setLoading(true);
    setData(null);
    fetch(`/api/reentradas?tipo=${aba}`)
      .then(res => res.json())
      .then(d => { setData(d); setLoadedAba(aba); setLoading(false); })
      .catch(() => setLoading(false));
  }, [aba]);

  const maxDist = data ? Math.max(...Object.values(data.distribuicao)) : 0;
  const dataOk = data && loadedAba === aba;

  const sortedKeys = data
    ? Object.keys(data.distribuicao).map(Number).sort((a, b) => a - b)
    : [];

  const abaInfo = ABA_LABELS[aba];

  function getQtdField(r: any): number {
    if (aba === 'reentradas') return r.qtd_reentraram;
    if (aba === 'persistencia') return r.qtd_persistiram;
    return r.qtd_repetidos;
  }

  function getListField(r: any): number[] {
    if (aba === 'reentradas') return r.nao_sorteados ?? [];
    if (aba === 'persistencia') return r.repetidos_anteriores ?? [];
    return r.anteriores ?? [];
  }

  function getListLabel(): string {
    if (aba === 'reentradas') return 'Não Sorteados';
    if (aba === 'persistencia') return 'Repetidos (anterior)';
    return 'Anterior';
  }

  function getLastCardLabel(): string {
    const npj = data?.numeros_por_jogo ?? 15;
    const total = data?.total_numeros ?? 25;
    if (aba === 'reentradas') return `${total - npj}/${total} Não Sort/Total`;
    if (aba === 'persistencia') return `${npj} Rep Anterior`;
    return `${npj}/${total} Rep/Anterior`;
  }

  return (
    <div className="rounded-2xl border border-[rgba(129,140,248,0.12)] overflow-hidden animate-slide-up"
      style={{ background: 'linear-gradient(135deg,#0f1429 0%,#1a1040 50%,#0f1a2e 100%)' }}
    >
      <div className="flex border-b border-white/6">
        {(Object.entries(ABA_LABELS) as [Aba, typeof ABA_LABELS[Aba]][]).map(([key, info]) => (
          <button
            key={key}
            onClick={() => setAba(key)}
            className={`flex-1 py-3 px-2 text-sm font-semibold text-center transition-all ${
              aba === key
                ? 'text-white border-b-2 border-[#818cf8] bg-white/4'
                : 'text-muted hover:text-white hover:bg-white/4'
            }`}
          >
            {info.titulo}
          </button>
        ))}
      </div>

      <div className="p-4 sm:p-6">
        <p className="text-xs text-muted mb-4 italic">{abaInfo.desc}</p>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="w-6 h-6 rounded-full border-2 border-[rgba(129,140,248,0.15)] border-t-[#818cf8] animate-spin" />
            <span className="ml-3 text-sm text-muted">Analisando...</span>
          </div>
        ) : dataOk ? (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 mb-6">
              <StatCard value={String(data.total_concursos)} label="Concursos" />
              <StatCard value={String(data.media)} label="Média" />
              <StatCard value={String(data.mediana)} label="Mediana" />
              <StatCard value={`${data.min} – ${data.max}`} label="Range" />
              <StatCard value={String(data.moda)} label={`+Comum (${data.moda}x)`} />
              <StatCard value={String(data.desvio)} label="Desvio" />
              <StatCard value={getLastCardLabel()} label="" />
            </div>

            <div className="space-y-1.5 mb-6">
              {sortedKeys.map(qtd => {
                const count = data.distribuicao[qtd];
                const pct = data.distribuicao_pct[String(qtd)];
                return (
                  <div key={qtd} className="flex items-center gap-3">
                    <div className="w-6 text-right text-sm font-bold text-white shrink-0">{qtd}</div>
                    <div className="flex-1 h-6 rounded-md bg-white/5 relative overflow-hidden">
                      <div
                        className="h-full rounded-md bg-gradient-to-r from-[#818cf8] to-[#a78bfa] transition-all duration-500 flex items-center px-2"
                        style={{ width: `${(count / maxDist) * 100}%` }}
                      >
                        <span className="text-[11px] text-white font-semibold whitespace-nowrap">{count}x</span>
                      </div>
                    </div>
                    <div className="w-14 text-right text-sm text-muted shrink-0">{pct}</div>
                  </div>
                );
              })}
            </div>

            <details>
              <summary className="text-sm text-muted cursor-pointer hover:text-white transition-colors select-none">
                Detalhamento por concurso ({data.records.length})
              </summary>
              <div className="mt-3 rounded-xl bg-white/4 border border-white/6 overflow-x-auto max-h-[400px] overflow-y-auto">
                <table className="w-full text-left text-sm">
                  <thead className="sticky top-0 bg-[#0f1429] border-b border-white/6">
                    <tr>
                      <th className="px-3 py-2 text-muted font-semibold">Concurso</th>
                      <th className="px-3 py-2 text-muted font-semibold">{getListLabel()}</th>
                      <th className="px-3 py-2 text-muted font-semibold">Qtd</th>
                      <th className="px-3 py-2 text-muted font-semibold">%</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {data.records.slice(0, 200).map(r => (
                      <tr key={r.concurso} className="hover:bg-white/5 transition-colors">
                        <td className="px-3 py-1.5 text-white font-semibold">{r.concurso}</td>
                        <td className="px-3 py-1.5 text-muted font-mono text-xs max-w-[260px] overflow-hidden text-ellipsis">
                          {getListField(r).join(', ')}
                        </td>
                        <td className="px-3 py-1.5">
                          <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                            aba === 'reentradas'
                              ? (getQtdField(r) >= 5 ? 'bg-emerald/15 text-emerald' : getQtdField(r) >= 3 ? 'bg-accent-2/15 text-accent-2' : 'bg-hot/15 text-hot')
                              : (getQtdField(r) >= 9 ? 'bg-emerald/15 text-emerald' : getQtdField(r) >= 7 ? 'bg-accent-2/15 text-accent-2' : 'bg-hot/15 text-hot')
                          }`}>
                            {getQtdField(r)}
                          </span>
                        </td>
                        <td className="px-3 py-1.5 text-muted">{r.pct}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          </>
        ) : (
          <p className="text-sm text-hot">Erro ao carregar dados.</p>
        )}
      </div>
    </div>
  );
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="bg-white/4 rounded-xl p-3 border border-white/6 text-center">
      <div className="text-lg font-bold text-white">{value}</div>
      {label && <div className="text-[10px] text-muted uppercase tracking-wide mt-0.5">{label}</div>}
    </div>
  );
}
