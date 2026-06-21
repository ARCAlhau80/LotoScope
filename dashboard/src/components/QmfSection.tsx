'use client';

import { useState, useCallback } from 'react';
import NumBadge from './NumBadge';

export default function QmfSection({ quentes, mornos, frios, janela, totalSorteios, onJanelaChange }: {
  quentes: [number, number][];
  mornos: [number, number][];
  frios: [number, number][];
  janela: number;
  totalSorteios: number;
  onJanelaChange: (valor: number) => void;
}) {
  const [inputValue, setInputValue] = useState(String(janela));
  const [erro, setErro] = useState<string | null>(null);

  const validarEConfirmar = useCallback((valorStr: string) => {
    setInputValue(valorStr);
    const parsed = parseInt(valorStr, 10);
    if (isNaN(parsed) || valorStr.trim() === '') {
      setErro('Digite um número válido');
      return;
    }
    if (parsed < 2) {
      setErro('Mínimo: 2 sorteios');
      return;
    }
    if (parsed > totalSorteios) {
      setErro(`Máximo: ${totalSorteios} sorteios`);
      return;
    }
    setErro(null);
    onJanelaChange(parsed);
  }, [totalSorteios, onJanelaChange]);

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
        Números Quentes, Mornos &amp; Frios
      </h3>
      <div className="flex items-center gap-2 mb-4">
        <label htmlFor="janela-qmf" className="text-sm text-muted">
          Janela de análise:
        </label>
        <input
          id="janela-qmf"
          type="number"
          min={2}
          max={totalSorteios}
          value={inputValue}
          onChange={e => validarEConfirmar(e.target.value)}
          className="w-24 px-2.5 py-1.5 rounded-lg text-sm text-[#e0e7ff] bg-white/5 border border-white/10 focus:border-accent-2/50 focus:outline-none focus:ring-1 focus:ring-accent-2/30 text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        />
        <span className="text-xs text-muted">últimos sorteios</span>
        {erro && <span className="text-xs text-hot">{erro}</span>}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QmfCard title="🔥 Quentes" idx={0} nums={quentes.map(n => n[0]).sort((a, b) => a - b)} cardBg="bg-[rgba(239,68,68,0.06)]" className="border-[rgba(239,68,68,0.35)] hover:border-[rgba(239,68,68,0.55)]" numClass="bg-[rgba(251,146,60,0.25)] text-[#fb923c] border-[rgba(251,146,60,0.35)]" />
        <QmfCard title="💨 Mornos" idx={1} nums={mornos.map(n => n[0]).sort((a, b) => a - b)} cardBg="bg-[rgba(148,163,184,0.05)]" className="border-[rgba(148,163,184,0.2)] hover:border-[rgba(148,163,184,0.35)]" numClass="bg-[rgba(148,163,184,0.15)] text-[#a3b3cc] border-[rgba(148,163,184,0.2)]" />
        <QmfCard title="🧊 Frios" idx={2} nums={frios.map(n => n[0]).sort((a, b) => a - b)} cardBg="bg-[rgba(56,189,248,0.06)]" className="border-[rgba(56,189,248,0.25)] hover:border-[rgba(56,189,248,0.45)]" numClass="bg-[rgba(56,189,248,0.2)] text-[#67e8f9] border-[rgba(56,189,248,0.3)]" />
      </div>
    </div>
  );
}

function QmfCard({ title, nums, className, numClass, cardBg = 'bg-white/3', idx = 0 }: {
  title: string; nums: number[]; className: string; numClass: string; cardBg?: string; idx?: number;
}) {
  return (
    <div
      className={`rounded-xl p-5 border ${cardBg} transition-all duration-200 hover:-translate-y-0.5 hover:bg-white/[0.05] animate-slide-up ${className}`}
      style={{ animationDelay: `${idx * 0.1}s` }}
    >
      <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">{title}</h4>
      <div className="flex flex-wrap gap-1.5">
        {nums.map(n => <NumBadge key={n} n={n} className={numClass} />)}
      </div>
    </div>
  );
}
