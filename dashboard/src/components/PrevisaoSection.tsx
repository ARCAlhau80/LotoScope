'use client';

import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import type { PrevisaoItem } from '@/types';

export default function PrevisaoSection({ previsao }: { previsao: Record<string, PrevisaoItem[]> }) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !previsao) return;
    if (chartInstance.current) chartInstance.current.destroy();

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    const posicoes = Object.keys(previsao);
    const top1 = posicoes.map(p => {
      const x = previsao[p]?.[0];
      return { num: x?.numero ?? 0, prob: x?.prob ?? 0 };
    });

    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: posicoes.map((p, i) => `${p} = ${top1[i].num}`),
        datasets: [{
          label: 'Probabilidade do top-1',
          data: top1.map(x => +(x.prob * 100).toFixed(1)),
          backgroundColor: top1.map(x => {
            if (x.prob > 0.3) return 'rgba(52,211,153,0.6)';
            if (x.prob > 0.15) return 'rgba(129,140,248,0.6)';
            return 'rgba(148,163,184,0.4)';
          }),
          borderColor: top1.map(x => {
            if (x.prob > 0.3) return 'rgba(52,211,153,0.9)';
            if (x.prob > 0.15) return 'rgba(129,140,248,0.9)';
            return 'rgba(148,163,184,0.6)';
          }),
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
        scales: {
          x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { beginAtZero: true, ticks: { color: '#94a3b8', font: { size: 10 }, callback: v => v + '%' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        },
      },
    });

    return () => { if (chartInstance.current) chartInstance.current.destroy(); };
  }, [previsao]);

  if (!previsao) return null;

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
        Previsão Posicional (Poisson)
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">top 3 por posição</span>
      </h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="rounded-xl p-5 border border-white/6 bg-white/3">
          <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">Probabilidade por Posição</h4>
          <div style={{ height: 280 }}><canvas ref={chartRef} /></div>
        </div>
        <div className="rounded-xl p-5 border border-white/6 bg-white/3 overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="text-muted font-medium border-b border-white/6">
                <th className="text-left py-2 px-2 uppercase tracking-wide">Pos</th>
                <th className="text-left py-2 px-2">#1</th>
                <th className="text-left py-2 px-2">#2</th>
                <th className="text-left py-2 px-2">#3</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(previsao).map(pos => {
                const p = previsao[pos] || [];
                return (
                  <tr key={pos} className="border-b border-white/4 hover:bg-white/4 transition-colors">
                    <td className="py-2 px-2 font-semibold text-fg">{pos}</td>
                    {p.slice(0, 3).map((x, i) => (
                      <td key={`${pos}-${i}`} className="py-2 px-2">
                        <span className="text-fg">{x.numero}</span>
                        <span className="text-accent-2 ml-1.5">{(x.prob * 100).toFixed(1)}%</span>
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
