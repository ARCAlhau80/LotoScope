'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import NumBadge, { type NumState } from './NumBadge';
import { LOTERIAS } from '@/lib/lottery-config';

const stateCycle: NumState[] = ['neutral', 'fixed', 'excluded'];

export default function QmfSection({ quentes, mornos, frios, janela, totalSorteios, numerosPorJogo, totalNumeros, loteria, onJanelaChange }: {
  quentes: [number, number][];
  mornos: [number, number][];
  frios: [number, number][];
  janela: number;
  totalSorteios: number;
  numerosPorJogo: number;
  totalNumeros: number;
  loteria?: string;
  onJanelaChange: (valor: number) => void;
}) {
  const [inputValue, setInputValue] = useState(String(janela));
  const [erro, setErro] = useState<string | null>(null);
  const [numStates, setNumStates] = useState<Record<number, NumState>>({});
  const [combinacoes, setCombinacoes] = useState<number[][] | null>(null);
  const [gerando, setGerando] = useState(false);
  const [qtdGeracao, setQtdGeracao] = useState(10);
  const [erroGeracao, setErroGeracao] = useState<string | null>(null);

  useEffect(() => {
    setInputValue(String(janela));
  }, [janela]);

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

  const cfg = loteria && LOTERIAS[loteria] ? LOTERIAS[loteria] : null;
  const gameSize = cfg ? cfg.numeros_por_jogo : numerosPorJogo;
  const totalNums = cfg ? cfg.total_numeros : totalNumeros;
  const maxFixar = gameSize - 1;

  const handleNumClick = useCallback((n: number) => {
    setNumStates(prev => {
      const current = prev[n] || 'neutral';
      const currentIdx = stateCycle.indexOf(current);
      const next = stateCycle[(currentIdx + 1) % stateCycle.length];

      if (next === 'fixed') {
        const fixedCount = Object.values(prev).filter(v => v === 'fixed').length +
          (current !== 'fixed' ? 0 : 0);
        if (fixedCount >= maxFixar) {
          setErroGeracao(`Máximo de ${maxFixar} números fixos para esta loteria`);
          return prev;
        }
      }

      if (next === 'excluded') {
        const excludedCount = Object.values(prev).filter(v => v === 'excluded').length +
          (current !== 'excluded' ? 0 : 0);
        const currentFixed = Object.values(prev).filter(v => v === 'fixed').length;
        const remainingAvailable = totalNums - currentFixed - excludedCount - 1;
        const needed = gameSize - currentFixed;
        if (remainingAvailable < needed) {
          setErroGeracao(`Exclusão impossibilita fechar 1 aposta (precisa de ${needed} números disponíveis)`);
          return prev;
        }
      }

      setErroGeracao(null);
      if (next === 'neutral') {
        const { [n]: _, ...rest } = prev;
        return rest;
      }
      return { ...prev, [n]: next };
    });
    setCombinacoes(null);
  }, [maxFixar, totalNums, gameSize]);

  const allNumbers = useMemo(() => {
    const set = new Set<number>();
    quentes.forEach(n => set.add(n[0]));
    mornos.forEach(n => set.add(n[0]));
    frios.forEach(n => set.add(n[0]));
    return [...set].sort((a, b) => a - b);
  }, [quentes, mornos, frios]);

  const fixedNumbers = useMemo(() =>
    allNumbers.filter(n => numStates[n] === 'fixed'),
    [allNumbers, numStates]
  );

  const excludedNumbers = useMemo(() =>
    allNumbers.filter(n => numStates[n] === 'excluded'),
    [allNumbers, numStates]
  );

  const hasSelection = fixedNumbers.length > 0;

  const getNumState = useCallback((n: number) => numStates[n] || 'neutral', [numStates]);

  const gerarCombinacoes = useCallback(async () => {
    setGerando(true);
    setErroGeracao(null);
    setCombinacoes(null);
    try {
      const res = await fetch('/api/generate-combinations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mandatory_numbers: fixedNumbers,
          excluded_numbers: excludedNumbers,
          game_size: gameSize,
          loteria: loteria || 'lotofacil',
          quantity: qtdGeracao === 0 ? 0 : qtdGeracao,
        }),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Erro ao gerar combinações');
      setCombinacoes(data.combinations);
    } catch (err) {
      setErroGeracao(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setGerando(false);
    }
  }, [fixedNumbers, excludedNumbers, qtdGeracao, gameSize]);

  const sortedFixed = [...fixedNumbers].sort((a, b) => a - b);
  const sortedExcluded = [...excludedNumbers].sort((a, b) => a - b);

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
        Números Quentes, Mornos &amp; Frios
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">clique 1× fixa · 2× exclui · 3× volta · max {maxFixar} fixos</span>
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
        <QmfCard title="🔥 Quentes" idx={0}
          nums={quentes.map(n => n[0]).sort((a, b) => a - b)}
          cardBg="bg-[rgba(239,68,68,0.06)]" className="border-[rgba(239,68,68,0.35)] hover:border-[rgba(239,68,68,0.55)]"
          numClass="bg-[rgba(251,146,60,0.25)] text-[#fb923c] border-[rgba(251,146,60,0.35)]"
          getState={getNumState} onNumClick={handleNumClick} />
        <QmfCard title="💨 Mornos" idx={1}
          nums={mornos.map(n => n[0]).sort((a, b) => a - b)}
          cardBg="bg-[rgba(148,163,184,0.05)]" className="border-[rgba(148,163,184,0.2)] hover:border-[rgba(148,163,184,0.35)]"
          numClass="bg-[rgba(148,163,184,0.15)] text-[#a3b3cc] border-[rgba(148,163,184,0.2)]"
          getState={getNumState} onNumClick={handleNumClick} />
        <QmfCard title="🧊 Frios" idx={2}
          nums={frios.map(n => n[0]).sort((a, b) => a - b)}
          cardBg="bg-[rgba(56,189,248,0.06)]" className="border-[rgba(56,189,248,0.25)] hover:border-[rgba(56,189,248,0.45)]"
          numClass="bg-[rgba(56,189,248,0.2)] text-[#67e8f9] border-[rgba(56,189,248,0.3)]"
          getState={getNumState} onNumClick={handleNumClick} />
      </div>

      {hasSelection && (
        <div className="mt-4 p-4 rounded-xl border border-accent-2/20 bg-white/3 animate-fade-in">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted">Fixos ({fixedNumbers.length}/{maxFixar}):</span>
              <span className="text-emerald font-semibold">{sortedFixed.join(', ') || '—'}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted">Excluídos ({excludedNumbers.length}):</span>
              <span className="text-hot font-semibold">{sortedExcluded.join(', ') || '—'}</span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3 mt-3">
            <label className="text-sm text-muted">Qtd:</label>
            <input
              type="number"
              min={0}
              max={1000}
              value={qtdGeracao}
              onChange={e => setQtdGeracao(parseInt(e.target.value) || 0)}
              className="w-20 px-2.5 py-1.5 rounded-lg text-sm text-[#e0e7ff] bg-white/5 border border-white/10 focus:border-accent-2/50 focus:outline-none focus:ring-1 focus:ring-accent-2/30 text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
            <span className="text-xs text-muted">(0 = todas)</span>
            <button
              onClick={gerarCombinacoes}
              disabled={gerando}
              className="px-5 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
            >
              {gerando ? 'Gerando…' : `🎲 Gerar ${qtdGeracao === 0 ? 'Todas' : qtdGeracao} Combinações`}
            </button>
          </div>
        </div>
      )}

      {erroGeracao && (
        <div className="mt-3 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-sm">
          {erroGeracao}
        </div>
      )}

      {combinacoes && combinacoes.length > 0 && (
        <div className="mt-4 animate-fade-in">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-[#e0e7ff]">
              Combinações Geradas ({combinacoes.length})
            </h4>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const header = `# LotoScope - ${combinacoes.length} combinações\n`;
                  const content = combinacoes.map(c => c.join(',')).join('\n');
                  const blob = new Blob([header + content], { type: 'text/plain;charset=utf-8' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `lotoscope_combinacoes_${combinacoes.length}.txt`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                }}
                className="text-xs px-3 py-1 rounded-lg bg-accent/15 text-accent-2 hover:bg-accent/25 transition-colors"
              >
                Download TXT
              </button>
              <button
                onClick={() => setCombinacoes(null)}
                className="text-xs text-muted hover:text-fg transition-colors"
              >
                Limpar
              </button>
            </div>
          </div>
          <div className="text-xs text-muted mb-2">Exibindo as 10 primeiras de {combinacoes.length}</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 pr-1">
            {combinacoes.slice(0, 10).map((combo, i) => (
              <div key={i}
                className="p-2.5 rounded-lg border border-white/5 bg-white/[0.03] text-xs text-fg font-mono transition-all hover:bg-white/[0.06]"
              >
                <span className="text-muted mr-1">#{i + 1}</span>
                {combo.map(n => {
                  const st = getNumState(n);
                  return (
                    <span key={n}
                      className={`inline-block mx-0.5 px-1 rounded ${
                        st === 'fixed' ? 'text-emerald font-bold' :
                        st === 'excluded' ? 'text-hot line-through' : ''
                      }`}
                    >
                      {String(n).padStart(2, '0')}
                    </span>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      )}

      {combinacoes && combinacoes.length === 0 && (
        <div className="mt-3 p-3 rounded-lg bg-white/5 border border-white/10 text-muted text-sm text-center">
          Nenhuma combinação encontrada com esses critérios.
        </div>
      )}
    </div>
  );
}

function QmfCard({ title, nums, className, numClass, cardBg = 'bg-white/3', idx = 0, getState, onNumClick }: {
  title: string; nums: number[]; className: string; numClass: string; cardBg?: string; idx?: number;
  getState: (n: number) => NumState;
  onNumClick: (n: number) => void;
}) {
  return (
    <div
      className={`rounded-xl p-5 border ${cardBg} transition-all duration-200 hover:-translate-y-0.5 hover:bg-white/[0.05] animate-slide-up ${className}`}
      style={{ animationDelay: `${idx * 0.1}s` }}
    >
      <h4 className="text-sm font-semibold text-[#e0e7ff] mb-3">{title}</h4>
      <div className="flex flex-wrap gap-1.5">
        {nums.map(n => <NumBadge key={n} n={n} className={numClass} state={getState(n)} onClick={onNumClick} />)}
      </div>
    </div>
  );
}
