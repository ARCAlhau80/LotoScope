'use client';

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import ConcursoSelector from './ConcursoSelector';
import { tabelaPremios, obterPremio, type FaixaPremio } from '@/lib/premios';
import { PRECO_BASE } from '@/lib/lottery-config';
import { analisarFiltrosPremioMaximo, type FiltrosSnapshot } from '@/lib/analise-filtros';

interface ComboConferencia {
  numeros: number[];
  trevos: number[];
}

export function formatarValor(v: number): string {
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: v >= 100 ? 0 : 2, maximumFractionDigits: v >= 100 ? 0 : 2 });
}

function rotuloFaixa(f: FaixaPremio): string {
  return f.fixo ? f.nome : `~${f.nome}`;
}

function parseCombinacoes(text: string): ComboConferencia[] {
  const lines = text.split(/\r?\n/);
  const result: ComboConferencia[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const [dezenasTxt, trevosTxt] = trimmed.split('|');
    const numeros = (dezenasTxt ?? '').split(/[,;\s]+/).map(s => parseInt(s, 10)).filter(n => !isNaN(n));
    if (numeros.length === 0) continue;
    const trevos = (trevosTxt ?? '').split(/[,;\s]+/).map(s => parseInt(s, 10)).filter(n => !isNaN(n));
    result.push({ numeros, trevos });
  }
  return result;
}

export default function ConferidorSection({ numerosPorJogo, loteria, concursos = [], totalSorteios = 0, filtrosGeracao = null }: {
  numerosPorJogo: number;
  loteria?: string;
  concursos?: number[];
  totalSorteios?: number;
  filtrosGeracao?: FiltrosSnapshot | null;
}) {
  const [combinacoes, setCombinacoes] = useState<ComboConferencia[]>([]);
  const [arrastando, setArrastando] = useState(false);
  const [texto, setTexto] = useState('');
  const [concursoConferidor, setConcursoConferidor] = useState<number | undefined>(undefined);
  const [sorteio, setSorteio] = useState<{ numeros: number[]; trevos: number[] } | null>(null);
  const [carregandoSorteio, setCarregandoSorteio] = useState(true);
  const [erroSorteio, setErroSorteio] = useState<string | null>(null);
  const cacheSorteios = useRef<Map<string, { numeros: number[]; trevos: number[] }>>(new Map());
  const dropRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loteriaId = loteria ?? 'lotofacil';
    const chave = `${loteriaId}:${concursoConferidor ?? 'ultimo'}`;
    const emCache = cacheSorteios.current.get(chave);

    if (emCache) {
      setSorteio(emCache);
      setCarregandoSorteio(false);
      setErroSorteio(null);
      return;
    }

    const controller = new AbortController();
    setSorteio(null);
    setCarregandoSorteio(true);
    setErroSorteio(null);

    const params = new URLSearchParams({ loteria: loteriaId });
    if (concursoConferidor !== undefined) params.set('concurso', String(concursoConferidor));

    fetch(`/api/resultado-concurso?${params.toString()}`, { signal: controller.signal })
      .then(async res => {
        const payload = await res.json();
        if (!res.ok) throw new Error(payload?.error || `HTTP ${res.status}`);
        return payload as { numeros?: number[]; trevos?: number[] };
      })
      .then(payload => {
        const item = { numeros: payload.numeros ?? [], trevos: payload.trevos ?? [] };
        cacheSorteios.current.set(chave, item);
        setSorteio(item);
      })
      .catch(err => {
        if (err instanceof Error && err.name === 'AbortError') return;
        setErroSorteio(err instanceof Error ? err.message : 'Erro ao carregar sorteio');
      })
      .finally(() => {
        if (!controller.signal.aborted) setCarregandoSorteio(false);
      });

    return () => controller.abort();
  }, [loteria, concursoConferidor]);

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
  const sorteioAtual = useMemo(() => sorteio?.numeros ?? [], [sorteio]);
  const trevosSorteio = useMemo(() => sorteio?.trevos ?? [], [sorteio]);
  const temTrevos = trevosSorteio.length > 0;

  const analiseFiltros = useMemo(() => {
    if (!filtrosGeracao || isPositional || sorteioAtual.length === 0) return null;
    return analisarFiltrosPremioMaximo(filtrosGeracao, sorteioAtual);
  }, [filtrosGeracao, isPositional, sorteioAtual]);

  const filtrosMaisRestritivos = analiseFiltros
    ? [...analiseFiltros.filtros].filter(f => f.falhas > 0).sort((a, b) => b.falhas - a.falhas).slice(0, 3)
    : [];

  function contarAcertos(combo: ComboConferencia): number {
    if (isPositional) {
      return combo.numeros.reduce((s, n, i) => s + (n === sorteioAtual[i] ? 1 : 0), 0);
    }
    const set = new Set(sorteioAtual);
    return combo.numeros.filter(n => set.has(n)).length;
  }

  function contarAcertosTrevos(combo: ComboConferencia): number {
    const set = new Set(trevosSorteio);
    return combo.trevos.filter(t => set.has(t)).length;
  }

  const stats = combinacoes.length > 0 && sorteioAtual.length > 0 ? (() => {
    const hits = combinacoes.map(contarAcertos);
    const maxPossivel = sorteioAtual.length;
    const dist: Record<number, number> = {};
    for (let i = 0; i <= maxPossivel; i++) dist[i] = 0;
    for (const h of hits) dist[h] = (dist[h] || 0) + 1;
    const maiores = [...combinacoes].sort((a, b) => contarAcertos(b) - contarAcertos(a)).slice(0, 5);

    let totalFixo = 0;
    let totalEstimado = 0;
    let premiadas = 0;
    const porFaixa: Record<string, { count: number; total: number; fixo: boolean; nome: string }> = {};
    for (const combo of combinacoes) {
      const ac = contarAcertos(combo);
      const at = contarAcertosTrevos(combo);
      const r = obterPremio(loteria ?? 'lotofacil', ac, at);
      if (!r.premiado || !r.faixa) continue;
      premiadas++;
      const f = r.faixa;
      if (f.fixo) totalFixo += f.valor; else totalEstimado += f.valor;
      const e = porFaixa[f.nome] ?? (porFaixa[f.nome] = { count: 0, total: 0, fixo: f.fixo, nome: f.nome });
      e.count++;
      e.total += f.valor;
    }
    const porFaixaList = Object.values(porFaixa).sort((a, b) => b.total - a.total);
    const custoUnitario = PRECO_BASE[loteria ?? 'lotofacil'] ?? 2.5;
    const custoTotal = custoUnitario * combinacoes.length;
    const premioTotal = totalFixo + totalEstimado;
    const saldo = premioTotal - custoTotal;
    return { hits, dist, maiores, maxPossivel, custoUnitario, custoTotal, premioTotal, saldo, premiosResumo: { totalFixo, totalEstimado, premiadas, porFaixa: porFaixaList } };
  })() : null;

  return (
    <section className="mb-8">
      <h3 className="text-lg font-semibold mb-4 text-ink flex items-center gap-2">
        Conferidor
        <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">
          arraste .txt ou cole as combinações
        </span>
      </h3>

      {concursos.length > 0 && (
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <label className="text-sm text-muted">Concurso de referência:</label>
          <ConcursoSelector
            concursos={concursos}
            value={concursoConferidor}
            onChange={setConcursoConferidor}
            totalSorteios={totalSorteios}
          />
          {carregandoSorteio ? (
            <span className="text-xs text-muted">carregando sorteio...</span>
          ) : erroSorteio ? (
            <span className="text-xs text-hot-bright">Erro ao carregar sorteio: {erroSorteio}</span>
          ) : concursoConferidor ? (
            <span className="text-xs text-accent-2">
              conferindo contra o concurso <strong>{concursoConferidor}</strong>
            </span>
          ) : (
            <span className="text-xs text-muted">
              conferindo contra o último concurso
            </span>
          )}
        </div>
      )}

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
          placeholder={temTrevos
            ? "Cole aqui as combinações (dezenas|trevos, uma por linha, separados por vírgula ou espaço)\nEx: 1,2,3,4,5,6|3,5"
            : "Cole aqui as combinações (uma por linha, números separados por vírgula ou espaço)\nEx: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"}
          className="w-full h-28 px-3 py-2 rounded-lg text-xs text-ink bg-white/5 border border-white/10 focus:border-accent-2/50 focus:outline-none focus:ring-1 focus:ring-accent-2/30 font-mono resize-y mb-3 placeholder:text-muted/90"
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
              {temTrevos && (
                <> · <strong className="text-amber-200">trevos {trevosSorteio.join(', ')}</strong></>
              )}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <div className="rounded-xl border border-accent/25 bg-accent/[0.06] p-3 animate-fade-in">
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-1.5">
                <span className="text-sm text-muted">
                  custo: <strong className="text-fg">{formatarValor(stats.custoTotal)}</strong>
                  <span className="text-[11px] text-muted/90 ml-1">({formatarValor(stats.custoUnitario)}/aposta)</span>
                </span>
                {stats.premiosResumo && (stats.premiosResumo.totalFixo > 0 || stats.premiosResumo.totalEstimado > 0) && (
                  <>
                    <span className="text-sm text-muted">
                      prêmios: <strong className="text-emerald">{formatarValor(stats.premioTotal)}</strong>
                    </span>
                    <span className={`text-sm font-semibold ${stats.saldo >= 0 ? 'text-emerald' : 'text-[#fb923c]'}`}>
                      {stats.saldo >= 0 ? 'lucro' : 'prejuízo'}: <strong>{stats.saldo >= 0 ? '' : '-'}{formatarValor(Math.abs(stats.saldo))}</strong>
                    </span>
                  </>
                )}
                {(!stats.premiosResumo || (stats.premiosResumo.totalFixo === 0 && stats.premiosResumo.totalEstimado === 0)) && (
                  <span className="text-sm text-muted/90">
                    sem prêmios nesta leva
                  </span>
                )}
              </div>
              {stats.premiosResumo && (stats.premiosResumo.totalFixo > 0 || stats.premiosResumo.totalEstimado > 0) && (
                <div className="text-[11px] text-muted/90">
                  custo - prêmios = {formatarValor(stats.saldo)} ({stats.custoTotal > 0 ? ((stats.premioTotal / stats.custoTotal - 1) * 100).toFixed(1) : '0'}% ROI)
                </div>
              )}
            </div>
            <div className="rounded-xl border border-emerald/30 bg-emerald/[0.06] p-3 animate-fade-in">
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-1.5">
                <span className="text-sm font-semibold text-emerald">
                  {stats.premiosResumo.premiadas} combinacion{stats.premiosResumo.premiadas !== 1 ? 'es' : ''} premiada{stats.premiosResumo.premiadas !== 1 ? 's' : ''}
                </span>
                {stats.premiosResumo.totalFixo > 0 && (
                  <span className="text-sm text-emerald">
                    fixos: <strong>{formatarValor(stats.premiosResumo.totalFixo)}</strong>
                  </span>
                )}
                {stats.premiosResumo.totalEstimado > 0 && (
                  <span className="text-sm text-amber-200">
                    estimados: <strong>~{formatarValor(stats.premiosResumo.totalEstimado)}</strong>
                  </span>
                )}
                {(stats.premiosResumo.totalFixo > 0 || stats.premiosResumo.totalEstimado > 0) && (
                  <span className="text-sm text-fg/90">
                    total: <strong>{formatarValor(stats.premiosResumo.totalFixo + stats.premiosResumo.totalEstimado)}</strong>
                  </span>
                )}
              </div>
              {stats.premiosResumo.porFaixa.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {stats.premiosResumo.porFaixa.map(f => (
                    <span key={f.nome}
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                        f.fixo ? 'bg-emerald/15 text-emerald border border-emerald/25' : 'bg-amber-500/15 text-amber-200 border border-amber-500/25'
                      }`}
                    >
                      {f.nome}: {f.count} × {f.fixo ? '' : '~'}{formatarValor(f.total / f.count)} = {f.fixo ? '' : '~'}{formatarValor(f.total)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {!isPositional && (
            analiseFiltros ? (
              <div className={`mb-4 rounded-xl border p-3 ${analiseFiltros.eliminado ? 'border-hot/30 bg-hot/[0.06]' : 'border-emerald/25 bg-emerald/[0.04]'}`}>
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <span className="text-sm font-semibold text-ink">Análise de filtros · prêmio máximo</span>
                  <span className="text-[11px] text-muted">
                    última geração: {filtrosGeracao?.jogosGerados} jogos · {filtrosGeracao?.dezenas} dezenas
                    {filtrosGeracao?.concursoBase ? ` · base C${filtrosGeracao.concursoBase}` : ''}
                  </span>
                </div>
                {analiseFiltros.filtros.length === 0 ? (
                  <p className="text-xs text-muted">Nenhum filtro ativo na última geração.</p>
                ) : analiseFiltros.eliminado ? (
                  <>
                    <p className="text-xs text-hot-bright mb-2">
                      {analiseFiltros.totalCandidatos === 1 ? (
                        <>Os filtros da última geração eliminam <strong>a única combinação</strong> que daria o prêmio máximo.</>
                      ) : (
                        <>Os filtros da última geração eliminam <strong>todas as {analiseFiltros.totalCandidatos} combinações</strong> que dariam o prêmio máximo.</>
                      )}
                    </p>
                    {analiseFiltros.eliminadoresIndividuais.length > 0 ? (
                      <p className="text-xs text-fg/90 mb-2">
                        Filtros que sozinhos já eliminam todos: <strong>{analiseFiltros.eliminadoresIndividuais.map(f => f.label).join(' · ')}</strong>
                      </p>
                    ) : (
                      <p className="text-xs text-fg/90 mb-2">
                        Nenhum filtro elimina sozinho; a combinação dos ativos elimina todos. Mais restritivos: <strong>{filtrosMaisRestritivos.map(f => `${f.label} (${f.falhas}/${f.total})`).join(' · ')}</strong>
                      </p>
                    )}
                  </>
                ) : (
                  <p className="text-xs text-fg/90 mb-2">
                    Nenhum filtro elimina o prêmio máximo: <strong>{analiseFiltros.aprovados} de {analiseFiltros.totalCandidatos}</strong>{' '}
                    {analiseFiltros.totalCandidatos === 1 ? 'combinação vencedora passaria' : 'combinações vencedoras passariam'}. Se o prêmio não saiu, a causa é cobertura/quantidade de jogos, não os filtros.
                  </p>
                )}
                {analiseFiltros.filtros.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {analiseFiltros.filtros.map(f => {
                      const tone = f.falhas === 0
                        ? 'bg-emerald/15 text-emerald border-emerald/25'
                        : f.falhas === f.total
                          ? 'bg-hot/15 text-hot-bright border-hot/25'
                          : 'bg-amber-500/15 text-amber-200 border-amber-500/25';
                      const texto = f.falhas === 0 ? 'aprovou todos' : f.falhas === f.total ? 'reprovou todos' : `reprovou ${f.falhas}/${f.total}`;
                      return (
                        <span key={f.id} className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${tone}`}>
                          {f.label}: {texto}
                        </span>
                      );
                    })}
                  </div>
                )}
                <p className="text-[10px] text-muted/80 mt-2">
                  Base: filtros da última geração nesta sessão. Não inclui a seleção de estratégias nem a quantidade/sorteio dos jogos.
                </p>
              </div>
            ) : !filtrosGeracao ? (
              <div className="mb-4 rounded-xl border border-white/10 bg-white/[0.02] p-3 text-xs text-muted">
                Gere jogos com filtros nesta sessão para ver quais filtros eliminariam o prêmio máximo.
              </div>
            ) : null
          )}

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
                  {!temTrevos && (() => {
                    const premio = obterPremio(loteria ?? 'lotofacil', n);
                    if (!premio.premiado || !premio.faixa) return null;
                    return (
                      <span
                        className={`ml-1 ${premio.faixa.fixo ? 'text-emerald' : 'text-amber-200'}`}
                        title={`${premio.faixa.nome} — ${premio.faixa.observacao ?? ''}`}
                      >
                        · {premio.faixa.fixo ? '' : '~'}{formatarValor(premio.faixa.valor)}
                      </span>
                    );
                  })()}
                </div>
              )
            ))}
          </div>

          {temTrevos && (
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <span className="text-xs text-muted">Trevos:</span>
              {[2, 1, 0].map(n => {
                const cnt = combinacoes.filter(c => contarAcertosTrevos(c) === n).length;
                if (cnt === 0) return null;
                return (
                  <div key={n}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/20 text-amber-200 border border-amber-500/40">
                    {n} trevo{n !== 1 ? 's' : ''}: {cnt}
                  </div>
                );
              })}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 max-h-[500px] overflow-y-auto pr-1">
            {combinacoes.map((combo, i) => {
              const acertos = contarAcertos(combo);
              const acertosTrevos = contarAcertosTrevos(combo);
              const maxAcertos = Math.min(numerosPorJogo, sorteioAtual.length);
              const premio = obterPremio(loteria ?? 'lotofacil', acertos, acertosTrevos);
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
                    <span className="flex items-center gap-1.5">
                      {temTrevos && combo.trevos.length > 0 && (
                        <span className={`font-bold ${acertosTrevos > 0 ? 'text-amber-300' : 'text-muted'}`}>
                          {acertosTrevos}/{combo.trevos.length} trevos
                        </span>
                      )}
                      <span className={`font-bold ${
                        acertos >= 11 ? 'text-emerald' :
                        acertos >= 8 ? 'text-accent-2' :
                        acertos >= Math.ceil(maxAcertos * 0.5) ? 'text-[#fb923c]' :
                        'text-muted'
                      }`}>{acertos}</span>
                    </span>
                  </div>
                  <div>
                    {combo.numeros.map((n, idx) => {
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
                  {temTrevos && combo.trevos.length > 0 && (
                    <div className="mt-1 border-t border-white/5 pt-1">
                      {combo.trevos.map((t, idx) => {
                        const match = (new Set(trevosSorteio)).has(t);
                        return (
                          <span key={`t-${idx}-${t}`}
                            className={`inline-block mx-0.5 px-0.5 ${
                              match ? 'text-amber-300 font-bold' : 'text-fg/60'
                            }`}
                          >
                            {String(t).padStart(2, '0')}
                          </span>
                        );
                      })}
                    </div>
                  )}
                  {premio.premiado && premio.faixa && (
                    <div
                      className="mt-1.5 border-t border-white/5 pt-1.5 flex items-center justify-between"
                      title={premio.faixa.observacao ?? ''}
                    >
                      <span className="text-[10px] uppercase tracking-wide text-muted">
                        {rotuloFaixa(premio.faixa)}
                      </span>
                      <span className={`font-bold ${premio.faixa.fixo ? 'text-emerald' : 'text-amber-200'}`}>
                        {premio.faixa.fixo ? '' : '~'}{formatarValor(premio.faixa.valor)}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}
