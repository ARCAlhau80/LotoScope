'use client';

import { useState, useCallback, useMemo } from 'react';
import type { AnaliseSuperSete } from '@/types';
import QuarantineMatrix from './QuarantineMatrix';

const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const COL_NAMES = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7'];
const MAX_FIXED_PER_COL = 3;
const MAX_FIXED_TOTAL = 21;
const MAX_EXCLUDED_PER_COL = 9;
const MAX_EXCLUDED_TOTAL = 63;

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

function ColunaCard({ col, data, quarentenaData }: { col: string; data: AnaliseSuperSete['colunas'][string]; quarentenaData?: AnaliseSuperSete['quarentena'][string] }) {
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
                {data.atrasados.map((a, i) => {
                  const qInfo = quarentenaData?.digitos.find(d => d.digito === a.digito);
                  return (
                    <div key={i} className="flex items-center gap-1.5 bg-[#3b82f6]/10 rounded-lg px-2 py-1" title={qInfo ? `Media: ${qInfo.media} | P90: ${qInfo.p90}` : undefined}>
                      <DigitBadge digit={a.digito} variant="cold" />
                      <span className="text-[10px] text-[#93c5fd]">{a.gap}x sem sair</span>
                      {qInfo && (
                        <span className="text-[9px] text-muted ml-0.5">
                          (μ{qInfo.media} P90:{qInfo.p90})
                        </span>
                      )}
                    </div>
                  );
                })}
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
  const [tab, setTab] = useState<'colunas' | 'correlacoes' | 'padroes' | 'multipla' | 'exclusao' | 'quarentena' | 'comparativo'>('colunas');

  const tabs = [
    { id: 'colunas' as const, label: 'Por Coluna' },
    { id: 'correlacoes' as const, label: 'Correlações' },
    { id: 'padroes' as const, label: 'Padrões' },
    { id: 'multipla' as const, label: 'Aposta Múltipla' },
    { id: 'exclusao' as const, label: 'Exclusão' },
    { id: 'quarentena' as const, label: 'Quarentena' },
    { id: 'comparativo' as const, label: 'Transição' },
  ];

  const [sel, setSel] = useState<Record<string, Record<number, 'fixed' | 'excluded'>>>({});
  const [genQty, setGenQty] = useState(10);
  const [combos, setCombos] = useState<number[][] | null>(null);
  const [comboError, setComboError] = useState<string | null>(null);
  const [comboTotal, setComboTotal] = useState(0);

  const fixedCount = useMemo(() => {
    let total = 0;
    for (const col of COL_NAMES) if (sel[col]) for (const s of Object.values(sel[col])) if (s === 'fixed') total++;
    return total;
  }, [sel]);

  const excludedCount = useMemo(() => {
    let total = 0;
    for (const col of COL_NAMES) if (sel[col]) for (const s of Object.values(sel[col])) if (s === 'excluded') total++;
    return total;
  }, [sel]);

  const fixedPerCol = useMemo(() => {
    const r: Record<string, number> = {};
    for (const col of COL_NAMES) {
      r[col] = sel[col] ? Object.values(sel[col]).filter(s => s === 'fixed').length : 0;
    }
    return r;
  }, [sel]);

  const excludedPerCol = useMemo(() => {
    const r: Record<string, number> = {};
    for (const col of COL_NAMES) {
      r[col] = sel[col] ? Object.values(sel[col]).filter(s => s === 'excluded').length : 0;
    }
    return r;
  }, [sel]);

  const handleCellClick = useCallback((col: string, digit: number) => {
    setSel(prev => {
      const cur = prev[col]?.[digit];
      const next = { ...prev };
      if (!next[col]) next[col] = {};

      if (!cur) {
        const fCount = next[col] ? Object.values(next[col]).filter(s => s === 'fixed').length : 0;
        if (fCount >= MAX_FIXED_PER_COL) return prev;
        if (fixedCount >= MAX_FIXED_TOTAL) return prev;
        next[col] = { ...next[col], [digit]: 'fixed' };
      } else if (cur === 'fixed') {
        const eCount = next[col] ? Object.values(next[col]).filter(s => s === 'excluded').length : 0;
        if (eCount >= MAX_EXCLUDED_PER_COL) return prev;
        if (excludedCount >= MAX_EXCLUDED_TOTAL) return prev;
        next[col] = { ...next[col], [digit]: 'excluded' };
      } else {
        const { [digit]: _, ...rest } = next[col];
        next[col] = Object.keys(rest).length > 0 ? rest : undefined as any;
      }
      return next;
    });
  }, [fixedCount, excludedCount]);

  const getAvailableDigits = useCallback((col: string): number[] => {
    const colSel = sel[col];
    if (!colSel) return DIGITS;
    const fixed = DIGITS.filter(d => colSel[d] === 'fixed');
    if (fixed.length > 0) return fixed;
    return DIGITS.filter(d => colSel[d] !== 'excluded');
  }, [sel]);

  const totalCombos = useMemo(() => {
    return COL_NAMES.reduce((acc, col) => acc * getAvailableDigits(col).length, 1);
  }, [getAvailableDigits]);

  const generateCombinations = useCallback((qty: number) => {
    setComboError(null);
    const available = COL_NAMES.map(col => getAvailableDigits(col));
    const emptyCol = available.findIndex(a => a.length === 0);
    if (emptyCol !== -1) {
      setComboError(`${COL_NAMES[emptyCol]} sem digitos disponiveis. Selecione ao menos 1.`);
      setCombos(null);
      return;
    }

    const maxPossible = available.reduce((acc, a) => acc * a.length, 1);
    const generateAll = qty <= 0 || qty >= maxPossible;

    if (generateAll) {
      if (maxPossible > 2000000) {
        setComboError(`Muitas combinações (${maxPossible.toLocaleString()}). Aplique mais restrições para reduzir.`);
        setCombos(null);
        return;
      }
      const all: number[][] = [];
      function cartesian(idx: number, current: number[]) {
        if (idx === available.length) { all.push([...current]); return; }
        for (const d of available[idx]) { current.push(d); cartesian(idx + 1, current); current.pop(); }
      }
      cartesian(0, []);
      setCombos(all);
      setComboTotal(all.length);
      return;
    }

    const count = Math.min(qty, maxPossible);
    const seen = new Set<string>();
    const result: number[][] = [];

    for (let attempt = 0; attempt < count * 10 && result.length < count; attempt++) {
      const combo: number[] = [];
      for (const a of available) {
        combo.push(a[Math.floor(Math.random() * a.length)]);
      }
      const key = combo.join(',');
      if (!seen.has(key)) {
        seen.add(key);
        result.push(combo);
      }
    }
    setCombos(result);
    setComboTotal(result.length);
  }, [getAvailableDigits]);

  const exportCombos = useCallback(() => {
    const data = combos;
    if (!data || data.length === 0) return;
    const text = data.map(c => c.join(',')).join('\n');
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `combinacoes-supersete.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [combos]);

  const displayCombos = useMemo(() => combos ? combos.slice(0, 10) : null, [combos]);

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
          Clique nas células para <span className="text-emerald-400">fixar</span> (verde) ou <span className="text-red-400">excluir</span> (X vermelho) digitos.
          <span className="ml-2 text-muted">          1x = Fixar | 2x = Excluir | 3x = Limpar | 0 na qtd = todas possiveis</span>
        </p>

        <div className="flex flex-wrap gap-3 mb-4 text-xs">
          <span className="text-muted">
            Fixados: <strong className="text-emerald-400">{fixedCount}/{MAX_FIXED_TOTAL}</strong>
          </span>
          <span className="text-muted">
            Excluidos: <strong className="text-red-400">{excludedCount}/{MAX_EXCLUDED_TOTAL}</strong>
          </span>
          <span className="text-muted">
            Combinações possiveis: <strong className="text-[#c7d2fe]">{totalCombos.toLocaleString()}</strong>
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-center">
            <thead>
              <tr>
                <th className="text-xs text-muted font-medium py-2 px-1 text-left">Digito</th>
                {COL_NAMES.map(col => (
                  <th key={col} className="text-xs font-bold py-2 px-1">
                    <span className="text-[#818cf8]">{col}</span>
                    <span className="block text-[10px] text-emerald-400">F:{fixedPerCol[col]}</span>
                    <span className="block text-[10px] text-red-400">E:{excludedPerCol[col]}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DIGITS.map(d => (
                <tr key={d} className="border-t border-white/[0.04]">
                  <td className="py-1.5 px-1 text-left">
                    <span className="text-sm font-bold text-[#c7d2fe]">{d}</span>
                  </td>
                  {COL_NAMES.map(col => {
                    const status = sel[col]?.[d];
                    const qmfClass = getQMFClass(col, d);
                    let bg = '';
                    let border = '';
                    if (status === 'fixed') {
                      bg = 'bg-emerald-500/40';
                      border = 'border-emerald-400/60';
                    } else if (status === 'excluded') {
                      bg = qmfClass.split(' ')[0];
                      border = 'border-red-400/60';
                    } else {
                      bg = qmfClass.split(' ')[0];
                      border = qmfClass.split(' ')[2] || 'border-white/10';
                    }
                    return (
                      <td key={col} className="py-1.5 px-1">
                        <button
                          onClick={() => handleCellClick(col, d)}
                          className={`inline-flex items-center justify-center w-10 h-10 rounded-lg text-sm font-bold border transition-all cursor-pointer hover:scale-110 active:scale-95 ${bg} ${border} ${status === 'fixed' ? 'text-white' : status === 'excluded' ? 'text-red-400' : 'text-[#c7d2fe]'}`}
                          title={
                            status === 'fixed' ? 'Fixado - clique para excluir' :
                            status === 'excluded' ? 'Excluido - clique para limpar' :
                            'Clique para fixar'
                          }
                        >
                          {status === 'excluded' ? (
                            <svg className="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                              <line x1="4" y1="4" x2="16" y2="16" />
                              <line x1="16" y1="4" x2="4" y2="16" />
                            </svg>
                          ) : (
                            d
                          )}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex flex-wrap gap-3 mt-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-500/40 border border-emerald-400/60" />
            <span className="text-muted">Fixado</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded border-2 border-red-400/60 flex items-center justify-center text-red-400 font-bold text-[10px]">X</div>
            <span className="text-muted">Excluido</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#ef4444]/30 border border-[#ef4444]/40" />
            <span className="text-muted">Quente (QMF)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#f59e0b]/20 border border-[#f59e0b]/30" />
            <span className="text-muted">Morno (QMF)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#3b82f6]/30 border border-[#3b82f6]/40" />
            <span className="text-muted">Frio (QMF)</span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/[0.04] flex flex-wrap items-center gap-3">
          <span className="text-xs text-muted">Quarentena:</span>
          <button
            onClick={() => {
              if (!data.quarentena) return;
              setSel({});
              const next: Record<string, Record<number, 'fixed' | 'excluded'>> = {};
              for (const col of COL_NAMES) {
                const q = data.quarentena[col];
                if (q?.em_quarentena.length > 0) {
                  next[col] = {};
                  for (const d of q.em_quarentena) {
                    next[col][d] = 'excluded';
                  }
                }
              }
              setSel(next);
              setCombos(null);
            }}
            className="px-3 py-1.5 rounded-lg text-[10px] font-semibold text-[#fca5a5] bg-[#ef4444]/10 border border-[#ef4444]/20 hover:bg-[#ef4444]/20 transition-all"
            title="Excluir digitos em quarentena (sairam recentemente)"
          >
            Excluir Recentes
          </button>
          <button
            onClick={() => {
              if (!data.quarentena) return;
              setSel({});
              const next: Record<string, Record<number, 'fixed' | 'excluded'>> = {};
              for (const col of COL_NAMES) {
                const q = data.quarentena[col];
                if (q?.muito_atrasados.length > 0) {
                  next[col] = {};
                  for (const d of q.muito_atrasados) {
                    next[col][d] = 'fixed';
                  }
                }
              }
              setSel(next);
              setCombos(null);
            }}
            className="px-3 py-1.5 rounded-lg text-[10px] font-semibold text-[#93c5fd] bg-[#3b82f6]/10 border border-[#3b82f6]/20 hover:bg-[#3b82f6]/20 transition-all"
            title="Fixar digitos muito atrasados (acima do P90)"
          >
            Focar Atrasados
          </button>
          <button
            onClick={() => {
              if (!data.quarentena) return;
              setSel({});
              const next: Record<string, Record<number, 'fixed' | 'excluded'>> = {};
              for (const col of COL_NAMES) {
                const q = data.quarentena[col];
                next[col] = {};
                if (q?.em_quarentena) {
                  for (const d of q.em_quarentena) {
                    next[col][d] = 'excluded';
                  }
                }
                if (q?.muito_atrasados) {
                  for (const d of q.muito_atrasados) {
                    next[col][d] = 'fixed';
                  }
                }
              }
              setSel(next);
              setCombos(null);
            }}
            className="px-3 py-1.5 rounded-lg text-[10px] font-semibold text-[#c7d2fe] bg-[#818cf8]/10 border border-[#818cf8]/20 hover:bg-[#818cf8]/20 transition-all"
            title="Combinado: excluir recentes + focar atrasados"
          >
            Combinado
          </button>
          <span className="text-xs text-muted ml-2">Qtd:</span>
          <input
            type="number"
            min={0}
            max={999999}
            value={genQty}
            onChange={e => setGenQty(Math.max(0, parseInt(e.target.value) || 0))}
            className="w-20 px-2 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm text-white text-center font-mono"
          />
          <button
            onClick={() => generateCombinations(genQty)}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
            style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
          >
            Gerar
          </button>
          <button
            onClick={() => { setSel({}); setCombos(null); setComboError(null); setComboTotal(0); }}
            className="px-4 py-1.5 rounded-lg text-xs font-medium text-muted bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
          >
            Limpar seleção
          </button>
          {combos && combos.length > 0 && (
            <button
              onClick={exportCombos}
              className="px-4 py-1.5 rounded-lg text-xs font-medium text-white bg-emerald-600/60 border border-emerald-500/40 hover:bg-emerald-600/80 transition-all"
            >
              Exportar TXT
            </button>
          )}
        </div>

        {comboError && (
          <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="text-xs text-[#fca5a5]">{comboError}</p>
          </div>
        )}

        {combos && combos.length > 0 && (
          <div className="mt-4 pt-4 border-t border-white/[0.04]">
            <p className="text-xs font-semibold text-[#c7d2fe] mb-3">
              Combinações Geradas ({comboTotal.toLocaleString()})
              {comboTotal > 10 && <span className="text-muted font-normal ml-2">(mostrando 10 de {comboTotal.toLocaleString()} — exporte o TXT para todas)</span>}
            </p>
            <div className="space-y-1.5">
              {displayCombos!.map((combo, i) => (
                <div key={i} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04] text-sm">
                  <span className="text-[10px] text-muted font-mono w-8 text-right">{i + 1}.</span>
                  {COL_NAMES.map((col, ci) => (
                    <span key={col} className="flex items-center gap-1">
                      <span className="text-[10px] text-muted">{col}:</span>
                      <span className="font-bold text-[#c7d2fe]">{combo[ci]}</span>
                    </span>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {tab === 'colunas' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {COL_NAMES.map(col => (
            <ColunaCard key={col} col={col} data={data.colunas[col]} quarentenaData={data.quarentena?.[col]} />
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

      {tab === 'exclusao' && (
        <div className="space-y-4">
          <Card title="Previsao por Exclusao" icon="🎯">
            <p className="text-xs text-muted mb-4">
              Para cada coluna, excluimos 7 digitos e mantemos os 3 mais provaveis.
              <span className="text-emerald-400 ml-2">Verde = Mantido (top 3)</span>
              <span className="text-red-400 ml-2">Vermelho = Excluido</span>
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {COL_NAMES.map(col => {
                const p = data.previsao_exclusao.colunas[col];
                return (
                  <div key={col} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold text-[#818cf8] bg-[#818cf8]/10 px-2.5 py-1 rounded-md">{col}</span>
                      <span className="text-[10px] text-muted">{p.estrategia}</span>
                    </div>
                    <div className="space-y-1">
                      {p.scores.map((item) => {
                        const isTop3 = item.status === 'mantido';
                        const intensity = isTop3
                          ? Math.round(60 + item.score * 40)
                          : Math.round(20 + (1 - item.score) * 60);
                        const bgColor = isTop3
                          ? `rgba(16, 185, 129, ${intensity / 100})`
                          : `rgba(239, 68, 68, ${(100 - intensity) / 100})`;
                        const borderColor = isTop3
                          ? `rgba(16, 185, 129, ${intensity / 100 + 0.2})`
                          : `rgba(239, 68, 68, ${(100 - intensity) / 100 + 0.2})`;
                        return (
                          <div
                            key={item.digito}
                            className="flex items-center justify-between px-3 py-1.5 rounded-lg text-sm transition-all"
                            style={{ backgroundColor: bgColor, border: `1px solid ${borderColor}` }}
                          >
                            <span className="font-bold text-white">{item.digito}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-20 h-1.5 rounded-full bg-white/10 overflow-hidden">
                                <div
                                  className="h-full rounded-full bg-white/40"
                                  style={{ width: `${Math.round(item.score * 100)}%` }}
                                />
                              </div>
                              <span className={`text-[10px] font-mono ${isTop3 ? 'text-emerald-300' : 'text-red-300'}`}>
                                {isTop3 ? 'manter' : 'excluir'}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>
      )}

      {tab === 'quarentena' && data.quarentena && (
        <div className="space-y-4">
          <QuarantineMatrix quarentena={data.quarentena} />
        </div>
      )}

      {tab === 'comparativo' && data.comparativo_posicional && (
        <div className="space-y-6">
          <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">Transição Dígito-a-Dígito por Coluna</h4>
          <p className="text-xs text-muted mb-4">
            Último: {data.comparativo_posicional.ultimo_sorteio.join(' · ')}<br />
            Penúltimo: {data.comparativo_posicional.penultimo_sorteio.join(' · ')}
          </p>
          {COL_NAMES.map(col => {
            const pc = data.comparativo_posicional!.por_coluna[col];
            if (!pc) return null;
            return (
              <div key={col} className="rounded-xl border border-white/6 bg-white/3 p-4">
                <h5 className="text-sm font-semibold text-[#e0e7ff] mb-2">{col}</h5>
                <div className="flex flex-wrap gap-2 mb-3 text-xs text-muted">
                  <span className="text-emerald">▲ Maior: {pc.maior} ({pc.total > 0 ? Math.round(pc.maior / pc.total * 1000) / 10 : 0}%)</span>
                  <span className="text-accent-2/70">= Mesmo: {pc.mesmo} ({pc.total > 0 ? Math.round(pc.mesmo / pc.total * 1000) / 10 : 0}%)</span>
                  <span className="text-hot">▼ Menor: {pc.menor} ({pc.total > 0 ? Math.round(pc.menor / pc.total * 1000) / 10 : 0}%)</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-center">
                    <thead>
                      <tr className="text-muted border-b border-white/6">
                        <th className="py-1 px-2">Atual ↓</th>
                        <th className="py-1 px-2">Total</th>
                        <th className="py-1 px-2 text-emerald">▲ Maior</th>
                        <th className="py-1 px-2 text-accent-2/70">= Mesmo</th>
                        <th className="py-1 px-2 text-hot">▼ Menor</th>
                        <th className="py-1 px-2 text-emerald">%▲</th>
                        <th className="py-1 px-2 text-accent-2/70">%=</th>
                        <th className="py-1 px-2 text-hot">%▼</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pc.transicoes.map(t => (
                        <tr key={t.digito} className="border-b border-white/4 hover:bg-white/4 transition-colors">
                          <td className="py-1 px-2 font-semibold text-[#e0e7ff]">{t.digito}</td>
                          <td className="py-1 px-2 text-muted">{t.total}</td>
                          <td className="py-1 px-2 text-emerald">{t.maior}</td>
                          <td className="py-1 px-2 text-accent-2/70">{t.mesmo}</td>
                          <td className="py-1 px-2 text-hot">{t.menor}</td>
                          <td className="py-1 px-2 text-emerald">{t.pct_maior}%</td>
                          <td className="py-1 px-2 text-accent-2/70">{t.pct_mesmo}%</td>
                          <td className="py-1 px-2 text-hot">{t.pct_menor}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      )}

    </section>
  );
}
