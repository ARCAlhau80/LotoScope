'use client';

import { useState } from 'react';

interface AiAnalysisProps {
  loteria: string;
}

export default function AiAnalysis({ loteria }: AiAnalysisProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analise, setAnalise] = useState<string | null>(null);
  const [compare, setCompare] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  async function rodarAnalise() {
    setLoading(true);
    setError(null);
    setAnalise(null);
    try {
      const r = await fetch('/api/ai-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          loteria,
          compare: compare > 0 ? compare : undefined,
        }),
      });
      const data = await r.json();
      if (!data.ok) {
        setError(data.error || 'Erro desconhecido');
      } else {
        const texto = data.resultados?.[0]?.analise || 'Sem resposta';
        setAnalise(texto);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro de rede');
    }
    setLoading(false);
  }

  return (
    <div className="mb-6">
      <button
        onClick={() => {
          setOpen(!open);
          if (!open && !analise && !error) rodarAnalise();
        }}
        className="px-4 py-2 rounded-xl text-sm font-semibold
          bg-gradient-to-r from-[#818cf8] to-[#a78bfa]
          hover:brightness-110 active:scale-95 transition-all duration-200
          text-white shadow-lg"
      >
        {open ? 'Fechar Análise IA' : 'Análise IA'}
      </button>

      {open && (
        <div className="mt-4 p-5 rounded-2xl border border-[rgba(129,140,248,0.2)]
          bg-[rgba(129,140,248,0.04)] animate-slide-up">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <label className="text-xs text-muted flex items-center gap-2">
              Comparar com N concursos atrás:
              <select
                value={compare}
                onChange={e => setCompare(Number(e.target.value))}
                className="bg-[rgba(129,140,248,0.1)] border border-[rgba(129,140,248,0.2)]
                  rounded-lg px-2 py-1 text-sm text-fg"
              >
                <option value={0}>Sem comparação</option>
                <option value={10}>10 concursos</option>
                <option value={25}>25 concursos</option>
                <option value={50}>50 concursos</option>
                <option value={100}>100 concursos</option>
              </select>
            </label>
            <button
              onClick={rodarAnalise}
              disabled={loading}
              className="px-3 py-1 rounded-lg text-xs font-medium
                bg-[rgba(52,211,153,0.15)] text-[#34d399]
                hover:bg-[rgba(52,211,153,0.25)] transition-all
                disabled:opacity-50"
            >
              {loading ? 'Analisando...' : 'Reanalisar'}
            </button>
          </div>

          {loading && (
            <div className="flex items-center gap-3 text-sm text-accent-2">
              <div className="w-5 h-5 rounded-full border-2 border-[rgba(129,140,248,0.2)]
                border-t-[#818cf8] animate-spin" />
              Enviando para gemma-lotto...
            </div>
          )}

          {error && (
            <div className="text-sm text-red-400 bg-red-500/10 rounded-xl p-3">
              {error}
            </div>
          )}

          {analise && !loading && (
            <div className="text-sm text-muted leading-relaxed whitespace-pre-wrap
              max-h-[60vh] overflow-y-auto pr-2
              [&::-webkit-scrollbar]:w-1.5
              [&::-webkit-scrollbar-thumb]:bg-[rgba(129,140,248,0.3)]
              [&::-webkit-scrollbar-thumb]:rounded-full">
              {analise}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
