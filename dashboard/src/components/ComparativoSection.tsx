'use client';

import type { TendenciaComparativo, PrevisaoTendenciaComparativo, CategoriaComparativo } from '@/types';

const CAT_META: Record<CategoriaComparativo, { label: string; cor: string }> = {
  maiores: { label: '▲ Maiores', cor: '#34d399' },
  iguais: { label: '= Iguais', cor: '#818cf8' },
  menores: { label: '▼ Menores', cor: '#ef4444' },
};

const DIRECAO: Record<string, { texto: string; seta: string }> = {
  cair: { texto: 'tende a cair', seta: '▼' },
  subir: { texto: 'tende a subir', seta: '▲' },
  estavel: { texto: 'tende a se manter', seta: '=' },
};

export default function ComparativoSection({ data, previsao }: {
  data: TendenciaComparativo[];
  previsao?: PrevisaoTendenciaComparativo;
}) {
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

      {previsao && (
        <div className="mt-5 pt-4 border-t border-white/6">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <h4 className="text-sm font-semibold text-[#e0e7ff]">
              Previsão para o próximo concurso
              <span className="text-accent-2 font-mono ml-1.5">#{previsao.concurso_alvo}</span>
              <span className="text-[11px] text-muted font-normal ml-2">(ainda não sorteado)</span>
            </h4>
            <span className="text-[11px] text-muted">
              condicionada ao concurso #{previsao.base_concurso} · {previsao.total_historico} transições históricas
            </span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {(['maiores', 'iguais', 'menores'] as CategoriaComparativo[]).map(k => {
              const c = previsao.categorias[k];
              const meta = CAT_META[k];
              const dir = DIRECAO[c.tendencia] ?? DIRECAO.estavel;
              const dominante = previsao.dominante === k;
              return (
                <div
                  key={k}
                  className="rounded-lg border px-3 py-2.5 transition-colors"
                  style={{
                    borderColor: dominante ? meta.cor : 'rgba(255,255,255,0.08)',
                    background: dominante ? `${meta.cor}14` : 'rgba(255,255,255,0.03)',
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-semibold" style={{ color: meta.cor }}>{meta.label}</span>
                    <span className="text-[10px] font-mono text-muted">atual: {c.atual} (faixa {c.banda_atual})</span>
                  </div>
                  <div className="text-lg font-bold text-fg mt-1">
                    {c.casos > 0 ? `${c.p25}–${c.p75}` : '—'}
                    <span className="text-[11px] font-normal text-muted ml-1">números no próximo</span>
                  </div>
                  <div className="text-[11px] text-muted mt-0.5">
                    mediana <strong className="text-fg">{c.mediana}</strong> · no máx. 10: <strong className="text-fg">{c.pct_le_10}%</strong> · no máx. 5: <strong className="text-fg">{c.pct_le_5}%</strong>
                  </div>
                  {c.casos > 0 ? (
                    <div className="text-[11px] mt-1" style={{ color: meta.cor }}>
                      {dir.seta} {dir.texto} <span className="text-muted">(mediana {c.mediana} vs atual {c.atual})</span>
                    </div>
                  ) : (
                    <div className="text-[11px] mt-1 text-muted">sem casos na faixa no histórico</div>
                  )}
                  {c.casos > 0 && (
                    <div className="text-[10px] text-muted mt-0.5">{c.casos} cenários em que a faixa foi {c.banda_atual}</div>
                  )}
                  {dominante && (
                    <div className="text-[10px] mt-1 font-semibold text-fg">tendência dominante</div>
                  )}
                </div>
              );
            })}
          </div>
          <div className="text-[11px] text-muted mt-2">
            Previsão condicionada por faixa do valor atual (0–5 / 6–10 / 11–15), sobre todo o histórico. Ex.: se o
            atual foi alto (11–15), o próximo historicamente tende a ficar menor.
          </div>
        </div>
      )}

      <div className="flex items-center gap-4 mt-3 text-[11px] text-muted">
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-emerald opacity-80" /> ▲ Maior que anterior</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#818cf8] opacity-40" /> = Igual</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-hot opacity-80" /> ▼ Menor que anterior</span>
      </div>
    </div>
  );
}