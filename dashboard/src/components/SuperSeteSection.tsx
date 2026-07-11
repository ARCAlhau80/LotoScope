'use client';

import { useState } from 'react';
import type { AnaliseSuperSete } from '@/types';

const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const COL_NAMES = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7'];

function DigitBadge({ digit, variant = 'neutral' }: { digit: number; variant?: 'hot' | 'cold' | 'warm' | 'neutral' | 'primary' }) {
  const colors = {
    hot: 'bg-[#ef4444]/20 text-[#fca5a5] border-[#ef4444]/30',
    cold: 'bg-[#3b82f6]/20 text-[#93c5fd] border-[#3b82f6]/30',
    warm: 'bg-[#f59e0b]/15 text-[#fcd34d] border-[#f59e0b]/20',
    neutral: 'bg-white/5 text-[#c7d2fe] border-white/10',
    primary: 'bg-[#818cf8]/20 text-[#c7d2fe] border-[#818cf8]/30',
  };
  return (
    <span className={`inline-flex items-center justify-center w-8 h-8 rounded-lg text-sm font-bold border ${colors[variant]}`}>
      {digit}
    </span>
  );
}

function Card({ title, children, icon }: { title: string; children: React.ReactNode; icon?: string }) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
      <h3 className="text-sm font-semibold text-[#c7d2fe] mb-4 flex items-center gap-2">
        {icon && <span>{icon}</span>}
        {title}
      </h3>
      {children}
    </div>
  );
}

function ColunaCard({ col, data }: { col: string; data: AnaliseSuperSete['colunas'][string] }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-[#818cf8] bg-[#818cf8]/10 px-2.5 py-1 rounded-md">{col}</span>
          <div className="flex gap-1">
            {data.previsao.slice(0, 3).map((p, i) => (
              <DigitBadge key={i} digit={p.digito} variant={i === 0 ? 'primary' : 'neutral'} />
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            {data.quentes.map(d => <DigitBadge key={d} digit={d} variant="hot" />)}
          </div>
          <svg className={`w-4 h-4 text-muted transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-white/[0.04]">
          <div className="pt-3">
            <p className="text-xs text-muted mb-2 font-medium">QMF por Coluna</p>
            <div className="flex gap-4 text-xs">
              <div>
                <span className="text-[#fca5a5]">Quentes:</span>{' '}
                <span className="flex gap-1 mt-1">{data.quentes.map(d => <DigitBadge key={d} digit={d} variant="hot" />)}</span>
              </div>
              <div>
                <span className="text-[#fcd34d]">Mornos:</span>{' '}
                <span className="flex gap-1 mt-1">{data.mornos.map(d => <DigitBadge key={d} digit={d} variant="warm" />)}</span>
              </div>
              <div>
                <span className="text-[#93c5fd]">Frios:</span>{' '}
                <span className="flex gap-1 mt-1">{data.frios.map(d => <DigitBadge key={d} digit={d} variant="cold" />)}</span>
              </div>
            </div>
          </div>

          <div>
            <p className="text-xs text-muted mb-2 font-medium">Frequência (últimos sorteios)</p>
            <div className="grid grid-cols-10 gap-1">
              {DIGITS.map(d => {
                const freq = data.frequencia_recente[d] || 0;
                const maxFreq = Math.max(...DIGITS.map(dd => data.frequencia_recente[dd] || 0), 1);
                const pct = (freq / maxFreq) * 100;
                return (
                  <div key={d} className="text-center">
                    <div className="h-16 flex items-end justify-center mb-1">
                      <div
                        className="w-full rounded-t bg-[#818cf8]/40 min-h-[2px] transition-all"
                        style={{ height: `${pct}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-muted">{d}</span>
                    <span className="block text-[10px] text-[#c7d2fe]">{freq}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {data.atrasados.length > 0 && (
            <div>
              <p className="text-xs text-muted mb-2 font-medium">Atrasados (P(gap) {'<'} 5%)</p>
              <div className="flex flex-wrap gap-2">
                {data.atrasados.map((a, i) => (
                  <div key={i} className="flex items-center gap-1.5 bg-[#3b82f6]/10 rounded-lg px-2 py-1">
                    <DigitBadge digit={a.digito} variant="cold" />
                    <span className="text-[10px] text-[#93c5fd]">{a.gap}x sem sair</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <p className="text-xs text-muted mb-2 font-medium">Ciclo (tendência)</p>
            <div className="flex flex-wrap gap-1">
              {DIGITS.map(d => {
                const c = data.ciclo[d];
                const color = c.estado === 'aquecendo' ? 'text-[#fca5a5]' : c.estado === 'esfriando' ? 'text-[#93c5fd]' : 'text-muted';
                const icon = c.estado === 'aquecendo' ? '↑' : c.estado === 'esfriando' ? '↓' : '→';
                return (
                  <span key={d} className={`text-xs px-1.5 py-0.5 rounded ${color}`}>
                    {d}{icon}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SuperSeteSection({ data }: { data: AnaliseSuperSete }) {
  const [tab, setTab] = useState<'colunas' | 'correlacoes' | 'padroes' | 'multipla'>('colunas');

  const tabs = [
    { id: 'colunas' as const, label: 'Por Coluna' },
    { id: 'correlacoes' as const, label: 'Correlações' },
    { id: 'padroes' as const, label: 'Padrões' },
    { id: 'multipla' as const, label: 'Aposta Múltipla' },
  ];

  const getQMFClass = (col: string, digit: number): string => {
    const colData = data.colunas[col];
    if (colData.quentes.includes(digit)) return 'bg-[#ef4444]/30 text-[#fca5a5] border-[#ef4444]/40';
    if (colData.frios.includes(digit)) return 'bg-[#3b82f6]/30 text-[#93c5fd] border-[#3b82f6]/40';
    return 'bg-[#f59e0b]/20 text-[#fcd34d] border-[#f59e0b]/30';
  };

  const getInsights = () => {
    const insights: { digit: number; hotCols: string[]; coldCols: string[] }[] = [];
    for (const d of DIGITS) {
      const hotCols: string[] = [];
      const coldCols: string[] = [];
      for (const col of COL_NAMES) {
        if (data.colunas[col].quentes.includes(d)) hotCols.push(col);
        if (data.colunas[col].frios.includes(d)) coldCols.push(col);
      }
      if (hotCols.length > 0 && coldCols.length > 0) {
        insights.push({ digit: d, hotCols, coldCols });
      }
    }
    return insights.slice(0, 3);
  };

  const insights = getInsights();

  return (
    <section className="space-y-5">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-bold text-white">Análise Super Sete</h2>
        <span className="text-[10px] font-bold text-[#818cf8] bg-[#818cf8]/10 px-2 py-0.5 rounded-full uppercase tracking-wider">
          Posicional
        </span>
      </div>

      <div className="flex gap-1 bg-white/[0.03] rounded-lg p-1 w-fit">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-md text-xs font-medium transition-all ${
              tab === t.id
                ? 'bg-[#818cf8]/20 text-[#c7d2fe]'
                : 'text-muted hover:text-[#c7d2fe] hover:bg-white/[0.03]'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
        <h3 className="text-sm font-semibold text-[#c7d2fe] mb-4 flex items-center gap-2">
          <span>🗺️</span>
          Mapa de Calor QMF por Coluna
        </h3>
        <p className="text-xs text-muted mb-4">
          Cada célula mostra se o dígito é <span className="text-[#fca5a5]">quente</span>, <span className="text-[#fcd34d]">morno</span> ou <span className="text-[#93c5fd]">frio</span> naquela coluna específica.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-center">
            <thead>
              <tr>
                <th className="text-xs text-muted font-medium py-2 px-1 text-left">Dígito</th>
                {COL_NAMES.map(col => (
                  <th key={col} className="text-xs font-bold text-[#818cf8] py-2 px-1">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DIGITS.map(d => (
                <tr key={d} className="border-t border-white/[0.04]">
                  <td className="py-2 px-1 text-left">
                    <span className="text-sm font-bold text-[#c7d2fe]">{d}</span>
                  </td>
                  {COL_NAMES.map(col => (
                    <td key={col} className="py-2 px-1">
                      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg text-sm font-bold border ${getQMFClass(col, d)}`}>
                        {d}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex gap-4 mt-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#ef4444]/30 border border-[#ef4444]/40" />
            <span className="text-muted">Quente (top 3)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#f59e0b]/20 border border-[#f59e0b]/30" />
            <span className="text-muted">Morno</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#3b82f6]/30 border border-[#3b82f6]/40" />
            <span className="text-muted">Frio (bottom 3)</span>
          </div>
        </div>

        {insights.length > 0 && (
          <div className="mt-4 pt-4 border-t border-white/[0.04]">
            <p className="text-xs font-semibold text-[#c7d2fe] mb-2">💡 Insights Automáticos</p>
            <div className="space-y-2">
              {insights.map((ins, i) => (
                <div key={i} className="text-xs text-muted bg-white/[0.02] rounded-lg p-3 border border-white/[0.04]">
                  <span className="font-bold text-[#c7d2fe]">Dígito {ins.digit}:</span>{' '}
                  <span className="text-[#fca5a5]">quente em {ins.hotCols.join(', ')}</span>
                  {' '}mas{' '}
                  <span className="text-[#93c5fd]">frio em {ins.coldCols.join(', ')}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {tab === 'colunas' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {COL_NAMES.map(col => (
            <ColunaCard key={col} col={col} data={data.colunas[col]} />
          ))}
        </div>
      )}

      {tab === 'correlacoes' && (
        <div className="space-y-3">
          <Card title="Correlação entre Colunas" icon="🔗">
            <div className="space-y-3">
              {data.correlacoes.slice(0, 10).map((c, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-[#818cf8]">{c.col_a}</span>
                    <span className="text-muted text-xs">×</span>
                    <span className="text-xs font-bold text-[#818cf8]">{c.col_b}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex gap-1.5 flex-wrap">
                      {c.pares_frequentes.slice(0, 3).map((p, j) => (
                        <span key={j} className="text-xs bg-white/5 px-2 py-0.5 rounded">
                          <span className="text-[#c7d2fe]">{p.dig_a}</span>
                          <span className="text-muted mx-0.5">-</span>
                          <span className="text-[#c7d2fe]">{p.dig_b}</span>
                          <span className="text-muted ml-1">({p.freq}x)</span>
                        </span>
                      ))}
                    </div>
                  </div>
                  <span className={`text-xs font-mono ${Math.abs(c.correlacao) > 0.1 ? 'text-[#fcd34d]' : 'text-muted'}`}>
                    r={c.correlacao.toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {tab === 'padroes' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card title="Distribuição da Soma" icon="📊">
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <p className="text-xs text-muted">Média</p>
                  <p className="text-lg font-bold text-[#c7d2fe]">{data.soma.media}</p>
                </div>
                <div>
                  <p className="text-xs text-muted">Mediana</p>
                  <p className="text-lg font-bold text-[#c7d2fe]">{data.soma.mediana}</p>
                </div>
                <div>
                  <p className="text-xs text-muted">Desvio</p>
                  <p className="text-lg font-bold text-[#c7d2fe]">{data.soma.desvio}</p>
                </div>
              </div>
              <div className="space-y-1.5">
                {data.soma.faixas.map((f, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-xs text-muted w-12">{f.faixa}</span>
                    <div className="flex-1 h-4 bg-white/[0.03] rounded overflow-hidden">
                      <div
                        className="h-full bg-[#818cf8]/40 rounded transition-all"
                        style={{ width: `${f.pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-[#c7d2fe] w-12 text-right">{f.pct}%</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card title="Repetição entre Colunas" icon="🔄">
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3 text-center">
                <div>
                  <p className="text-xs text-muted">Média de repetições</p>
                  <p className="text-lg font-bold text-[#c7d2fe]">{data.repeticao.media_repeticoes}</p>
                </div>
                <div>
                  <p className="text-xs text-muted">% com repetição</p>
                  <p className="text-lg font-bold text-[#fcd34d]">{data.repeticao.pct_com_repeticao}%</p>
                </div>
              </div>
              <div>
                <p className="text-xs text-muted mb-2">Dígitos mais repetidos entre colunas</p>
                <div className="flex flex-wrap gap-2">
                  {data.repeticao.digitos_mais_repetidos.slice(0, 5).map((d, i) => (
                    <div key={i} className="flex items-center gap-1.5 bg-white/[0.03] rounded-lg px-2 py-1">
                      <DigitBadge digit={d.digito} variant="warm" />
                      <span className="text-xs text-muted">{d.count}x</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          <Card title="Paridade por Coluna" icon="⚖️">
            <div className="space-y-2">
              {COL_NAMES.map(col => {
                const p = data.paridade.por_coluna[col];
                return (
                  <div key={col} className="flex items-center gap-3">
                    <span className="text-xs font-bold text-[#818cf8] w-8">{col}</span>
                    <div className="flex-1 flex items-center gap-1">
                      <div className="flex-1 h-3 bg-white/[0.03] rounded overflow-hidden flex">
                        <div className="h-full bg-[#818cf8]/40" style={{ width: `${p.pct_par}%` }} />
                        <div className="h-full bg-[#f59e0b]/30" style={{ width: `${100 - p.pct_par}%` }} />
                      </div>
                    </div>
                    <span className="text-[10px] text-muted w-20 text-right">
                      {p.pct_par}% par
                    </span>
                  </div>
                );
              })}
              <div className="mt-3 pt-3 border-t border-white/[0.04]">
                <p className="text-xs text-muted">Padrão mais comum: <span className="text-[#c7d2fe] font-mono font-bold">{data.paridade.mais_comum}</span></p>
                <p className="text-[10px] text-muted mt-1">P = Par, I = Ímpar (por coluna N1-N7)</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {tab === 'multipla' && (
        <div className="space-y-4">
          <Card title="Aposta Múltipla Sugerida" icon="🎯">
            <p className="text-xs text-muted mb-4">
              Top dígitos por coluna com base na probabilidade (lambda blend). 
              Combine 2-3 dígitos por coluna para apostas múltiplas.
            </p>
            <div className="grid grid-cols-7 gap-3">
              {COL_NAMES.map(col => {
                const c = data.aposta_multipla.colunas[col];
                return (
                  <div key={col} className="text-center">
                    <p className="text-xs font-bold text-[#818cf8] mb-2">{col}</p>
                    <div className="space-y-1.5">
                      {c.digitos.map((d, i) => (
                        <div key={i} className="flex items-center justify-center gap-1">
                          <DigitBadge digit={d} variant={i === 0 ? 'primary' : 'neutral'} />
                          <span className="text-[10px] text-muted">{c.confianca[i]}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 pt-4 border-t border-white/[0.04] flex items-center justify-between">
              <span className="text-xs text-muted">
                Combinações possíveis: <strong className="text-[#c7d2fe]">{data.aposta_multipla.combinacoes_possiveis}</strong>
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted">Palpite (2 por coluna):</span>
                <div className="flex gap-1">
                  {COL_NAMES.map(col => (
                    <DigitBadge key={col} digit={data.aposta_multipla.palpite_multipla[col]?.[0] ?? 0} variant="primary" />
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </section>
  );
}
