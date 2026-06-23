'use client';

import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import type { TransicaoQMF } from '@/types';

export default function TransicaoSection({ t, janela, numerosPorJogo }: { t: TransicaoQMF; janela: number; numerosPorJogo: number }) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !t?.recentes?.length) return;
    if (chartInstance.current) chartInstance.current.destroy();

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: t.recentes.map(r => String(r.concurso)),
        datasets: [
          { label: 'Quentes', data: t.recentes.map(r => r.quentes), backgroundColor: 'rgba(239,68,68,0.6)', borderColor: 'rgba(239,68,68,0.9)', borderWidth: 1 },
          { label: 'Mornos', data: t.recentes.map(r => r.mornos), backgroundColor: 'rgba(148,163,184,0.5)', borderColor: 'rgba(148,163,184,0.8)', borderWidth: 1 },
          { label: 'Frios', data: t.recentes.map(r => r.frios), backgroundColor: 'rgba(59,130,246,0.6)', borderColor: 'rgba(59,130,246,0.9)', borderWidth: 1 },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { stacked: true, max: numerosPorJogo, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        },
        plugins: {
          legend: { labels: { color: '#94a3b8', font: { size: 11 } } },
        },
      },
    });

    return () => { if (chartInstance.current) chartInstance.current.destroy(); };
  }, [t]);

  if (!t) return null;

  const { medias: m, tendencia: te } = t;

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
        De Onde Vêm os Acertos?
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">janela: {janela} sorteios</span>
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <MetricCard title="🔥 Quentes" value={m.quentes} pct={m.pct_q} tendencia={te.quentes} color="#fca5a5" />
        <MetricCard title="💨 Mornos" value={m.mornos} pct={m.pct_m} tendencia={te.mornos} color="#cbd5e1" />
        <MetricCard title="🧊 Frios" value={m.frios} pct={m.pct_f} tendencia={te.frios} color="#93c5fd" />
      </div>
      <div className="rounded-xl p-5 border border-white/6 bg-white/3">
        <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">Composição Q/M/F nos últimos {t.recentes.length} sorteios (janela: {janela})</h4>
        <div style={{ height: 200 }}><canvas ref={chartRef} /></div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, pct, tendencia, color }: {
  title: string; value: number; pct: number; tendencia: number; color: string;
}) {
  return (
    <div className="rounded-xl p-5 border border-white/6 bg-white/3 transition-all duration-200 hover:bg-white/[0.05] hover:-translate-y-0.5">
      <h4 className="text-sm font-semibold text-[#e0e7ff] mb-2">{title}</h4>
      <div className="text-3xl font-bold" style={{ color }}>{value}</div>
      <div className="text-xs text-muted mt-1">média por sorteio ({pct}%)</div>
      <div className="flex items-center gap-1 mt-2 text-xs" style={{ color: tendencia > 0 ? '#6ee7b7' : '#fca5a5' }}>
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d={tendencia > 0 ? 'M5 10l7-7m0 0l7 7m-7-7v18' : 'M19 14l-7 7m0 0l-7-7m7 7V3'} />
        </svg>
        <span>tendência: {tendencia > 0 ? '+' : ''}{tendencia.toFixed(2)}</span>
      </div>
    </div>
  );
}
