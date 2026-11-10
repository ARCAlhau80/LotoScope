'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { getJanelaAlvo, type JanelaAlvoData, type JanelaAlvoNumero } from '@/lib/api';
import { LOTERIAS } from '@/lib/lottery-config';

interface Props {
  loteria: string;
  concursoAtual?: number;
  /** Concurso base selecionado no topo do dashboard (para marcar os sorteados). */
  concursoBase?: number;
  /** Números sorteados no concurso base. */
  numerosBase?: number[];
}

const JANELA_PADRAO = 7;
const JANELA_MAX = 500;

function classeNumero(item: JanelaAlvoNumero): string {
  if (item.ocorrencias === 0) {
    return 'bg-hot/10 text-hot/70 border-hot/20';
  }
  if (item.percentual >= 80) {
    return 'bg-emerald-500/25 text-emerald-100 border-emerald-500/40';
  }
  if (item.percentual >= 60) {
    return 'bg-emerald-500/15 text-emerald-200 border-emerald-500/30';
  }
  if (item.percentual >= 40) {
    return 'bg-white/5 text-fg border-white/10';
  }
  return 'bg-white/[0.03] text-muted border-white/8';
}

function corBarra(item: JanelaAlvoNumero): string {
  if (item.ocorrencias === 0) return 'rgba(239,68,68,0.45)';
  if (item.percentual >= 80) return 'rgba(16,185,129,0.9)';
  if (item.percentual >= 60) return 'rgba(16,185,129,0.65)';
  if (item.percentual >= 40) return 'rgba(129,140,248,0.75)';
  return 'rgba(129,140,248,0.45)';
}

function fmtNumero(n: number): string {
  return String(n).padStart(2, '0');
}

export default function JanelaAlvoSection({ loteria, concursoAtual, concursoBase, numerosBase }: Props) {
  const baseSet = new Set(numerosBase ?? []);
  const [concursoInput, setConcursoInput] = useState<string>(
    concursoAtual ? String(concursoAtual) : '',
  );
  const [janela, setJanela] = useState<number>(JANELA_PADRAO);
  const [data, setData] = useState<JanelaAlvoData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const loteriaRef = useRef<string>(loteria);

  const carregar = useCallback(
    (concurso?: number, janelaAlvo: number = JANELA_PADRAO, silencioso: boolean = false) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      setLoading(true);
      if (!silencioso) setError(null);
      getJanelaAlvo(loteria, concurso, janelaAlvo, controller.signal)
        .then(res => {
          setData(res);
          setConcursoInput(String(res.concursoAlvo));
        })
        .catch(err => {
          if ((err as any)?.name === 'AbortError') return;
          if (!silencioso) {
            setError(err instanceof Error ? err.message : 'Erro ao calcular a janela.');
          }
        })
        .finally(() => {
          if (abortRef.current === controller) {
            abortRef.current = null;
            setLoading(false);
          }
        });
    },
    [loteria],
  );

  // Carrega automaticamente ao entrar/trocar de loteria (último concurso, janela 7).
  useEffect(() => {
    const trocouLoteria = loteriaRef.current !== loteria;
    loteriaRef.current = loteria;
    if (trocouLoteria) {
      setData(null);
      setError(null);
    }
    setConcursoInput(trocouLoteria ? '' : concursoAtual ? String(concursoAtual) : '');
    setJanela(JANELA_PADRAO);
    // Ao trocar de loteria, usa o último concurso da própria API (evita 404
    // enquanto o concurso da loteria anterior ainda está no componente pai).
    carregar(trocouLoteria ? undefined : concursoAtual, JANELA_PADRAO, trocouLoteria);
    return () => abortRef.current?.abort();
  }, [loteria, concursoAtual, carregar]);

  const analisar = () => {
    const concurso = concursoInput.trim() === '' ? undefined : Number(concursoInput);
    if (concurso !== undefined && (!Number.isInteger(concurso) || concurso <= 0)) {
      setError('Informe um concurso alvo válido (inteiro > 0).');
      return;
    }
    const janelaEfetiva = Number.isFinite(janela) ? Math.max(1, Math.min(JANELA_MAX, Math.trunc(janela))) : JANELA_PADRAO;
    setJanela(janelaEfetiva);
    carregar(concurso, janelaEfetiva);
  };

  const top10 = data?.numeros.slice(0, 10) ?? [];
  const nomeLoteria = LOTERIAS[loteria]?.nome_jogo ?? 'Loteria';

  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.02] p-4 sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="text-lg font-semibold text-ink flex items-center gap-2">
            Janela anterior ao concurso alvo
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent/15 text-accent-2 border border-accent/20 font-normal">
              {nomeLoteria}
            </span>
          </h3>
          <p className="text-xs text-muted mt-0.5">
            Conta quantas vezes cada número saiu nos <strong className="text-fg">X concursos imediatamente anteriores</strong> ao
            concurso alvo. O concurso alvo não entra na contagem.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-3 mb-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="janela-alvo-concurso" className="text-xs text-muted">Concurso alvo</label>
          <input
            id="janela-alvo-concurso"
            type="number"
            min={1}
            value={concursoInput}
            onChange={e => setConcursoInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') analisar(); }}
            placeholder={concursoAtual ? `ex.: ${concursoAtual}` : 'ex.: 3824'}
            className="w-32 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="janela-alvo-janela" className="text-xs text-muted">Janela (concursos)</label>
          <input
            id="janela-alvo-janela"
            type="number"
            min={1}
            max={JANELA_MAX}
            value={janela}
            onChange={e => setJanela(Number(e.target.value) || JANELA_PADRAO)}
            onKeyDown={e => { if (e.key === 'Enter') analisar(); }}
            className="w-32 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
          />
        </div>
        <button
          type="button"
          onClick={analisar}
          disabled={loading}
          className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
        >
          {loading ? 'Calculando...' : 'Analisar'}
        </button>
        {concursoAtual && (
          <button
            type="button"
            onClick={() => {
              setConcursoInput(String(concursoAtual));
              carregar(concursoAtual, janela);
            }}
            className="px-3 py-2 rounded-lg text-xs text-muted border border-white/10 hover:text-fg hover:bg-white/5 transition-colors"
          >
            Usar último ({concursoAtual})
          </button>
        )}
      </div>

      {numerosBase && numerosBase.length > 0 && (
        <div className="mb-3 flex items-center gap-2 text-[11px] text-muted">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.8)]" />
          Verde = número sorteado no concurso base
          {concursoBase ? ` ${concursoBase}` : ''}
        </div>
      )}

      {error && (
        <div className="mb-3 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-sm">
          {error}
        </div>
      )}

      {data && (
        <div aria-live="polite">
          <div className="mb-4 text-xs text-muted">
            <strong className="text-fg">Janela:</strong>{' '}
            {data.primeiroConcursoJanela !== null && data.ultimoConcursoJanela !== null
              ? `concursos ${data.primeiroConcursoJanela} a ${data.ultimoConcursoJanela}`
              : 'sem concursos anteriores'}{' '}
            ({data.janelaEfetiva} concurso{data.janelaEfetiva === 1 ? '' : 's'}) ·{' '}
            <strong className="text-fg">Alvo:</strong> {data.concursoAlvo}
            {data.janelaEfetiva < data.janelaSolicitada && (
              <span className="ml-2 text-amber-200">
                (janela ajustada: só existem {data.janelaEfetiva} concurso(s) antes do alvo)
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Grid de todos os números */}
            <div>
              <div className="text-xs font-semibold text-fg mb-2">Todos os números</div>
              <div className="grid grid-cols-5 sm:grid-cols-8 lg:grid-cols-5 gap-2">
                {data.numeros.map(item => {
                  const isBase = baseSet.has(item.numero);
                  return (
                    <div
                      key={item.numero}
                      className={`relative rounded-lg p-2 text-center border ${classeNumero(item)} ${
                        isBase ? 'ring-1 ring-emerald-400/60' : ''
                      }`}
                      title={`${item.numero}: ${item.ocorrencias} de ${data.janelaEfetiva} concursos (${item.percentual.toFixed(1)}%)${
                        isBase ? ' · sorteado no concurso base' : ''
                      }`}
                    >
                      {isBase && (
                        <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.9)]" />
                      )}
                      <div className={`text-sm font-bold leading-tight ${isBase ? 'text-emerald-300' : ''}`}>
                        {fmtNumero(item.numero)}
                      </div>
                      <div className="text-[10px] leading-tight">{item.ocorrencias}x</div>
                      <div className="text-[9px] opacity-80 leading-tight">{item.percentual.toFixed(0)}%</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Top 10 com barras */}
            <div>
              <div className="text-xs font-semibold text-fg mb-2">Mais sorteados na janela</div>
              <div className="space-y-2">
                {top10.map((item, idx) => {
                  const isBase = baseSet.has(item.numero);
                  return (
                    <div key={item.numero} className="flex items-center gap-2">
                      <span className="w-5 text-[10px] text-muted text-right">{idx + 1}.</span>
                      <span className={`w-8 text-xs font-semibold text-center ${isBase ? 'text-emerald-300' : 'text-fg'}`}>
                        {fmtNumero(item.numero)}
                      </span>
                      <span className="w-2 flex justify-center">
                        {isBase && (
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.9)]" title="Sorteado no concurso base" />
                        )}
                      </span>
                      <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${Math.max(2, item.percentual)}%`,
                            background: corBarra(item),
                          }}
                        />
                      </div>
                      <span className="w-14 text-[10px] text-muted text-right">
                        {item.ocorrencias}x · {item.percentual.toFixed(0)}%
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <details className="mt-4">
            <summary className="text-xs text-accent-2 cursor-pointer select-none">
              Ver os {data.janelaEfetiva} concurso(s) da janela e o alvo
            </summary>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="text-muted">
                    <th className="pb-2 pr-3 font-normal">Concurso</th>
                    <th className="pb-2 pr-3 font-normal">Data</th>
                    <th className="pb-2 font-normal">Números</th>
                  </tr>
                </thead>
                <tbody>
                  {data.concursos.map(c => (
                    <tr key={c.concurso} className="border-t border-white/5">
                      <td className="py-1.5 pr-3 text-fg font-medium">{c.concurso}</td>
                      <td className="py-1.5 pr-3 text-muted">{c.data ?? '—'}</td>
                      <td className="py-1.5">
                        <div className="flex flex-wrap gap-1">
                          {c.numeros.map(n => (
                            <span key={n} className="px-1.5 py-0.5 rounded bg-white/5 text-fg font-mono text-[10px]">
                              {fmtNumero(n)}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {data.alvo && (
                    <tr className="border-t border-amber-500/20 bg-amber-500/5">
                      <td className="py-1.5 pr-3 text-amber-200 font-medium">{data.alvo.concurso}</td>
                      <td className="py-1.5 pr-3 text-muted">{data.alvo.data ?? '—'}</td>
                      <td className="py-1.5">
                        <div className="flex flex-wrap gap-1">
                          {data.alvo.numeros.map(n => (
                            <span key={n} className="px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-100 font-mono text-[10px]">
                              {fmtNumero(n)}
                            </span>
                          ))}
                          <span className="text-[10px] text-amber-200/80 self-center ml-1">alvo (não entra na janela)</span>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
