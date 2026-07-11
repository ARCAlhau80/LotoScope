'use client';

import { useState, useCallback, useRef } from 'react';

function parseCombinacoes(text: string): number[][] {
  const lines = text.split(/\r?\n/);
  const result: number[][] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const nums = trimmed.split(/[,;\s]+/).map(s => parseInt(s, 10)).filter(n => !isNaN(n));
    if (nums.length > 0) result.push(nums);
  }
  return result;
}

export default function ConferidorSection({ sorteioAtual, numerosPorJogo, loteria }: {
  sorteioAtual: number[];
  numerosPorJogo: number;
  loteria?: string;
}) {
  const [combinacoes, setCombinacoes] = useState<number[][]>([]);
  const [arrastando, setArrastando] = useState(false);
  const [texto, setTexto] = useState('');
  const dropRef = useRef<HTMLDivElement>(null);

  const processar = useCallback((text: string) => {
    const parsed = parseCombinacoes(text);
    setCombinacoes(parsed);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setArrastando(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => processar(reader.result as string);
      reader.readAsText(file);
    }
  }, [processar]);

  const handlePaste = useCallback(() => {
    processar(texto);
  }, [texto, processar]);

  const isPositional = loteria === 'supersete';

  function contarAcertos(combo: number[]): number {
    if (isPositional) {
      return combo.reduce((s, n, i) => s + (n === sorteioAtual[i] ? 1 : 0), 0);
    }
    const set = new Set(sorteioAtual);
    return combo.filter(n => set.has(n)).length;
  }

  const stats = combinacoes.length > 0 ? (() => {
    const hits = combinacoes.map(contarAcertos);
    const maxPossivel = sorteioAtual.length;
    const dist: Record<number, number> = {};
    for (let i = 0; i <= maxPossivel; i++) dist[i] = 0;
    for (const h of hits) dist[h] = (dist[h] || 0) + 1;
    const maiores = [...combinacoes].sort((a, b) => contarAcertos(b) - contarAcertos(a)).slice(0, 5);
    return { hits, dist, maiores, maxPossivel };
  })() : null;

  return (
    <section className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
        Conferidor
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">
          arraste .txt ou cole as combinações
        </span>
      </h3>

      <div
        ref={dropRef}
        onDragOver={e => { e.preventDefault(); setArrastando(true); }}
        onDragLeave={() => setArrastando(false)}
        onDrop={handleDrop}
        className={`relative rounded-xl border-2 border-dashed p-6 transition-all ${
          arrastando
            ? 'border-accent-2/60 bg-accent-2/5'
            : 'border-white/10 bg-white/[0.02] hover:border-white/20'
        }`}
      >
        <textarea
          value={texto}
          onChange={e => setTexto(e.target.value)}
          placeholder="Cole aqui as combinações (uma por linha, números separados por vírgula ou espaço)
Ex: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"
          className="w-full h-28 px-3 py-2 rounded-lg text-xs text-[#e0e7ff] bg-white/5 border border-white/10 focus:border-accent-2/50 focus:outline-none focus:ring-1 focus:ring-accent-2/30 font-mono resize-y mb-3 placeholder:text-muted/50"
        />
        <div className="flex gap-2">
          <button
            onClick={handlePaste}
            disabled={!texto.trim()}
            className="px-4 py-1.5 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
          >
            Conferir
          </button>
          {combinacoes.length > 0 && (
            <button
              onClick={() => { setCombinacoes([]); setTexto(''); }}
              className="px-4 py-1.5 rounded-lg text-sm bg-white/10 text-muted hover:text-fg transition-colors"
            >
              Limpar
            </button>
          )}
          {combinacoes.length === 0 && !texto.trim() && (
            <span className="text-xs text-muted self-center">
              ou arraste um arquivo .txt
            </span>
          )}
        </div>
      </div>

      {combinacoes.length > 0 && stats && (
        <div className="mt-4 animate-fade-in">
          <div className="flex flex-wrap items-center gap-4 mb-3">
            <span className="text-sm text-muted">
              {combinacoes.length} combinações conferidas
            </span>
            <span className="text-sm text-muted">
              Sorteio de referência: <strong className="text-fg">{sorteioAtual.join(', ')}</strong>
            </span>
          </div>

          <div className="flex flex-wrap gap-2 mb-4">
            {Array.from({ length: stats.maxPossivel + 1 }, (_, i) => i).reverse().map(n => (
              stats.dist[n] > 0 && (
                <div key={n}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                    n >= 11 ? 'bg-emerald/20 text-emerald border border-emerald/30' :
                    n >= 8 ? 'bg-accent/20 text-accent-2 border border-accent-2/30' :
                    n >= 5 ? 'bg-[rgba(251,146,60,0.2)] text-[#fb923c] border border-[rgba(251,146,60,0.3)]' :
                    'bg-hot/10 text-hot/70 border border-hot/20'
                  }`}
                >
                  {n} acerto{n !== 1 ? 's' : ''}: {stats.dist[n]}
                </div>
              )
            ))}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 max-h-[500px] overflow-y-auto pr-1">
            {combinacoes.map((combo, i) => {
              const acertos = contarAcertos(combo);
              const maxAcertos = Math.min(numerosPorJogo, sorteioAtual.length);
              return (
                <div key={i}
                  className={`p-2.5 rounded-lg border text-xs font-mono transition-all ${
                    acertos >= 11 ? 'border-emerald/30 bg-emerald/5' :
                    acertos >= 8 ? 'border-accent-2/20 bg-accent-2/5' :
                    acertos >= Math.ceil(maxAcertos * 0.5) ? 'border-[rgba(251,146,60,0.2)] bg-[rgba(251,146,60,0.05)]' :
                    'border-white/5 bg-white/[0.02]'
                  }`}
                >
                  <div className="flex justify-between mb-1">
                    <span className="text-muted">#{i + 1}</span>
                    <span className={`font-bold ${
                      acertos >= 11 ? 'text-emerald' :
                      acertos >= 8 ? 'text-accent-2' :
                      acertos >= Math.ceil(maxAcertos * 0.5) ? 'text-[#fb923c]' :
                      'text-muted'
                    }`}>{acertos}</span>
                  </div>
                  <div>
                    {combo.map((n, idx) => {
                      const match = isPositional ? n === sorteioAtual[idx] : (new Set(sorteioAtual)).has(n);
                      return (
                        <span key={`${idx}-${n}`}
                          className={`inline-block mx-0.5 px-0.5 ${
                            match ? 'text-emerald font-bold' : 'text-fg/60'
                          }`}
                        >
                          {String(n).padStart(2, '0')}
                        </span>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}
