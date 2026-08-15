'use client';

import { useState, useCallback, useEffect } from 'react';
import { getLotteryConfig, dezenasValidas, calcularPrecoAposta } from '@/lib/lottery-config';

interface JogoGerado {
  numeros: number[];
  estrategia: string;
  soma: number;
  pares: number;
  impares: number;
  primos: number;
}

interface Estatisticas {
  total: number;
  cobertura: number;
  frequencia: Record<number, number>;
  estrategias: Record<string, number>;
}

interface CicloNumero {
  numero: number;
  qtd: number;
}

interface CicloAtual {
  numero: CicloNumero[];
  faltantes: number[];
  baixa_frequencia: number[];
  media_frequencia: number;
}

interface JogosDiversosSectionProps {
  loteria?: string;
  concursoBase?: number;
  numerosSorteadosAtual?: number[];
}

const ESTRATEGIA_LABEL: Record<string, string> = {
  atraso: 'Atrasados',
  'hot7-9': 'Quentes',
  persistencia: 'Persistência',
  aleatorio: 'Aleatório',
  ciclo: 'Ciclo',
};

type NumeroEstado = 'normal' | 'fixo' | 'excluido';

export default function JogosDiversosSection({ loteria = 'lotofacil', concursoBase, numerosSorteadosAtual = [] }: JogosDiversosSectionProps) {
  const cfg = getLotteryConfig(loteria);
  const opcoesDezenas = dezenasValidas(cfg);
  const [quantidade, setQuantidade] = useState<number>(5);
  const [dezenas, setDezenas] = useState<number>(cfg.numeros_por_jogo);
  const [estados, setEstados] = useState<Record<number, NumeroEstado>>({});
  const [jogos, setJogos] = useState<JogoGerado[] | null>(null);
  const [estatisticas, setEstatisticas] = useState<Estatisticas | null>(null);
  const [cicloAtual, setCicloAtual] = useState<CicloAtual | null>(null);
  const [estimativaTotal, setEstimativaTotal] = useState<number | null>(null);
  const [modoTodas, setModoTodas] = useState(false);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const novoCfg = getLotteryConfig(loteria);
    setEstados({});
    setJogos(null);
    setEstatisticas(null);
    setCicloAtual(null);
    setEstimativaTotal(null);
    setDezenas(novoCfg.numeros_por_jogo);
  }, [loteria]);

  const fixos = Object.entries(estados).filter(([, e]) => e === 'fixo').map(([n]) => Number(n));
  const excluidos = Object.entries(estados).filter(([, e]) => e === 'excluido').map(([n]) => Number(n));
  const sorteadosAtualSet = new Set(numerosSorteadosAtual);

  const toggleNumero = useCallback((n: number) => {
    setEstados(prev => {
      const atual = prev[n] || 'normal';
      let proximo: NumeroEstado;
      if (atual === 'normal') proximo = 'fixo';
      else if (atual === 'fixo') proximo = 'excluido';
      else proximo = 'normal';
      return { ...prev, [n]: proximo };
    });
  }, []);

  const limparSelecao = useCallback(() => {
    setEstados({});
  }, []);

  const gerar = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const seed = Date.now();
      const params = new URLSearchParams();
      params.set('loteria', loteria);
      params.set('n', String(quantidade));
      params.set('seed', String(seed));
      params.set('dezenas', String(dezenas));
      if (fixos.length > 0) params.set('fixos', fixos.join(','));
      if (excluidos.length > 0) params.set('excluidos', excluidos.join(','));
      if (concursoBase !== undefined) params.set('concurso', String(concursoBase));

      const res = await fetch(`/api/jogos-diversos?${params.toString()}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Erro ao gerar jogos');
      setJogos(data.jogos);
      setEstatisticas(data.estatisticas);
      setCicloAtual(data.ciclo_atual);
      setEstimativaTotal(data.estimativa_total ?? null);
      setModoTodas(data.modo_todas ?? false);
      if (typeof data.dezenas === 'number') setDezenas(data.dezenas);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao gerar jogos');
    } finally {
      setLoading(false);
    }
  }, [loteria, quantidade, dezenas, fixos, excluidos, concursoBase]);

  const exportarTodas = useCallback(async () => {
    setExporting(true);
    setError(null);
    try {
      const seed = Date.now();
      const params = new URLSearchParams();
      params.set('loteria', loteria);
      params.set('seed', String(seed));
      params.set('dezenas', String(dezenas));
      if (fixos.length > 0) params.set('fixos', fixos.join(','));
      if (excluidos.length > 0) params.set('excluidos', excluidos.join(','));
      if (concursoBase !== undefined) params.set('concurso', String(concursoBase));

      const res = await fetch(`/api/jogos-diversos/export?${params.toString()}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Erro ${res.status} ao exportar`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `jogos-${loteria}-${dezenas}dezenas-todas-${new Date().toISOString().slice(0, 10)}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao exportar jogos');
    } finally {
      setExporting(false);
    }
  }, [loteria, dezenas, fixos, excluidos, concursoBase]);

  const getNumeroClasses = (n: number) => {
    const estado = estados[n] || 'normal';
    if (estado === 'fixo') {
      return 'bg-emerald-500/30 text-emerald-100 border-emerald-500/60 ring-1 ring-emerald-500/50';
    }
    if (estado === 'excluido') {
      return 'bg-hot/20 text-hot/70 border-hot/40 line-through opacity-60';
    }
    return 'bg-[rgba(129,140,248,0.12)] text-accent-2 border-[rgba(129,140,248,0.25)] hover:bg-[rgba(129,140,248,0.22)]';
  };

  const totalNumeros = cfg.total_numeros;
  const gridClass = totalNumeros <= 25 ? 'grid-cols-5' : totalNumeros <= 31 ? 'grid-cols-8' : 'grid-cols-10';
  const gridMaxW = totalNumeros <= 25 ? 280 : totalNumeros <= 31 ? 400 : 480;
  const btnSize = totalNumeros <= 25 ? 'w-10 h-10 text-sm' : totalNumeros <= 50 ? 'w-9 h-9 text-xs' : 'w-8 h-8 text-xs';
  const cicloGridClass = gridClass;
  const cicloMaxW = gridMaxW + 40;
  const numeroMin = cfg.numero_minimo;
  const numeroMax = cfg.numero_maximo;
  const numeros = Array.from({ length: totalNumeros }, (_, i) => i + numeroMin);
  const precoUnit = calcularPrecoAposta(loteria, dezenas);
  const mostraSeletorDezenas = opcoesDezenas.length > 1;

  return (
    <div className="rounded-2xl border border-[rgba(129,140,248,0.15)] p-5 sm:p-6 mb-6"
      style={{ background: 'linear-gradient(135deg, rgba(129,140,248,0.06), rgba(52,211,153,0.03))' }}>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div>
          <h3 className="text-lg font-semibold text-[#e0e7ff]">Jogos Diversificados</h3>
          <p className="text-xs text-muted mt-1">
            Múltiplas estratégias (atraso, quentes, persistência, ciclo) para distribuir risco.
            {concursoBase !== undefined && (
              <span className="ml-1 text-accent-2">
                Alvo: concurso {concursoBase + 1}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {mostraSeletorDezenas && (
            <>
              <label className="text-sm text-muted">Dezenas por jogo:</label>
              <select
                value={dezenas}
                onChange={e => setDezenas(parseInt(e.target.value, 10))}
                className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
                title="Quantidade de dezenas de cada jogo gerado"
              >
                {opcoesDezenas.map(d => (
                  <option key={d} value={d} className="bg-[#1a1d2e]">{d}</option>
                ))}
              </select>
              {dezenas > cfg.numeros_por_jogo && (
                <span className="text-xs px-2 py-1 rounded-full bg-[#818cf8]/15 text-[#a5b4fc] border border-[#818cf8]/30">
                  R$ {precoUnit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}/jogo
                </span>
              )}
            </>
          )}
          <label className="text-sm text-muted">Quantidade:</label>
          <input
            type="number"
            min={0}
            value={quantidade}
            onChange={e => setQuantidade(Math.max(0, parseInt(e.target.value, 10) || 0))}
            className="w-24 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
          />
          {quantidade === 0 && (
            <span className="text-xs px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-500/30">
              Todas as combinações
            </span>
          )}
          <button
            onClick={gerar}
            disabled={loading}
            className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110 disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
            {loading ? 'Gerando...' : 'Gerar'}
          </button>
        </div>
      </div>

      <div className="mb-5">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-[#e0e7ff]">Clique nos números para fixar 🟢 ou excluir 🔴</div>
          <button
            onClick={limparSelecao}
            className="text-xs px-3 py-1 rounded-lg bg-white/5 text-muted hover:text-fg hover:bg-white/10 transition-colors">
            Limpar seleção
          </button>
        </div>
        <div className={`grid ${gridClass} gap-2`} style={{ maxWidth: gridMaxW }}>
          {numeros.map(n => {
            const sorteado = sorteadosAtualSet.has(n);
            return (
              <button
                key={n}
                onClick={() => toggleNumero(n)}
                className={`relative ${btnSize} flex items-center justify-center rounded-lg font-bold border transition-all ${getNumeroClasses(n)}`}>
                {n}
                {sorteado && (
                  <span
                    className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 border border-emerald-600/40 shadow-sm"
                    title="Sorteado no concurso atual"
                  />
                )}
              </button>
            );
          })}
        </div>
        <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted">
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500/30 border border-emerald-500/60" /> Fixo</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-hot/20 border border-hot/40" /> Excluído</span>
          <span className="flex items-center gap-1"><span className="relative w-3 h-3 rounded bg-white/5 border border-white/10"><span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 border border-emerald-600/40" /></span> Sorteado no concurso atual</span>
        </div>
        {(fixos.length > 0 || excluidos.length > 0) && (
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            {fixos.length > 0 && (
              <span className="px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-500/30">
                Fixos: {fixos.join(', ')}
              </span>
            )}
            {excluidos.length > 0 && (
              <span className="px-2 py-1 rounded-full bg-hot/15 text-hot/80 border border-hot/30">
                Excluídos: {excluidos.join(', ')}
              </span>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-sm">
          {error}
        </div>
      )}

      {estatisticas && (
        <div className="mb-5 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Jogos</div>
            <div className="text-lg font-bold text-fg">{estatisticas.total}</div>
          </div>
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Cobertura</div>
            <div className="text-lg font-bold text-fg">{estatisticas.cobertura}/{totalNumeros}</div>
          </div>
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Custo</div>
            <div className="text-lg font-bold text-fg">R$ {(estatisticas.total * precoUnit).toFixed(2)}</div>
          </div>
          <div className="rounded-xl bg-white/5 p-3 text-center">
            <div className="text-xs text-muted">Estimativa total</div>
            <div className="text-lg font-bold text-fg">
              {estimativaTotal === null ? '—' : estimativaTotal.toLocaleString('pt-BR')}
            </div>
          </div>
        </div>
      )}

      {cicloAtual && (
        <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm font-semibold text-[#e0e7ff]">Frequência no ciclo atual</div>
            <div className="text-xs text-muted">
              Média: <strong className="text-fg">{cicloAtual.media_frequencia.toFixed(2)}</strong> sorteios/número
            </div>
          </div>
          <div className={`grid ${cicloGridClass} gap-2`} style={{ maxWidth: cicloMaxW }}>
            {cicloAtual.numero.sort((a, b) => a.numero - b.numero).map(({ numero, qtd }) => {
              let classes = 'bg-white/5 text-muted border-white/10';
              if (qtd === 0) classes = 'bg-amber-500/25 text-amber-100 border-amber-500/40';
              else if (qtd === 1) classes = 'bg-amber-500/10 text-amber-200/80 border-amber-500/20';
              else if (qtd >= 4) classes = 'bg-emerald-500/15 text-emerald-200 border-emerald-500/30';
              return (
                <div key={numero} className={`flex flex-col items-center justify-center rounded-lg border p-1 ${classes}`}>
                  <span className="text-sm font-bold">{numero}</span>
                  <span className="text-[10px] opacity-80">{qtd}x</span>
                </div>
              );
            })}
          </div>
          <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-500/25 border border-amber-500/40" /> 0 sorteios (faltante)</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-500/10 border border-amber-500/20" /> 1 sorteio</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500/15 border border-emerald-500/30" /> 4+ sorteios</span>
          </div>
        </div>
      )}

      {jogos && (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <button
              onClick={() => {
                const texto = jogos.map(j => j.numeros.join(',')).join('\n');
                navigator.clipboard.writeText(texto);
              }}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
              Copiar todos (CSV)
            </button>
            <button
              onClick={() => {
                const texto = jogos.map(j => j.numeros.join(',')).join('\n');
                const blob = new Blob([texto], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `jogos-${loteria}-${new Date().toISOString().slice(0, 10)}.txt`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold text-[#e0e7ff] bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              Baixar .txt
            </button>
            {(modoTodas || jogos.length >= 50) && (
              <button
                onClick={exportarTodas}
                disabled={exporting}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg,#10b981,#34d399)' }}>
                {exporting ? 'Exportando...' : 'Exportar todas'}
              </button>
            )}
            <span className="text-xs text-muted">Formato: números separados por vírgula, um jogo por linha</span>
          </div>
          {modoTodas && estimativaTotal !== null && (
            <div className="text-xs text-emerald-200 bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2">
              Modo "todas as combinações": geradas {estimativaTotal.toLocaleString('pt-BR')} apostas.
              Apenas as 50 primeiras são exibidas; use <strong>Exportar todas</strong> para baixar o arquivo completo.
            </div>
          )}
          {!modoTodas && jogos.length >= 50 && (
            <div className="text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
              Exibindo as 50 primeiras apostas. Use <strong>Exportar todas</strong> para baixar o arquivo completo.
            </div>
          )}
          {jogos.slice(0, 50).map((jogo, idx) => (
            <div key={idx} className="rounded-xl bg-white/5 border border-white/10 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-[#e0e7ff]">Jogo {idx + 1}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#818cf8]/15 text-[#a5b4fc]">
                    {ESTRATEGIA_LABEL[jogo.estrategia] || jogo.estrategia}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted">
                  <span>Soma: <strong className="text-fg">{jogo.soma}</strong></span>
                  <span>Pares: <strong className="text-fg">{jogo.pares}</strong></span>
                  <span>Ímpares: <strong className="text-fg">{jogo.impares}</strong></span>
                  <span>Primos: <strong className="text-fg">{jogo.primos}</strong></span>
                  <button
                    onClick={() => navigator.clipboard.writeText(jogo.numeros.join(','))}
                    className="text-[#818cf8] hover:text-[#a5b4fc] transition-colors"
                    title="Copiar jogo">
                    Copiar
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {jogo.numeros.map(n => {
                  const sorteado = sorteadosAtualSet.has(n);
                  const faltante = cicloAtual?.faltantes.includes(n);
                  const classes = sorteado
                    ? 'bg-emerald-500/25 text-emerald-100 border-emerald-500/50 ring-1 ring-emerald-500/30'
                    : faltante
                      ? 'bg-amber-500/20 text-amber-100 border-amber-500/40'
                      : 'bg-[rgba(129,140,248,0.12)] text-accent-2 border-[rgba(129,140,248,0.25)]';
                  return (
                    <span
                      key={n}
                      className={`w-9 h-9 flex items-center justify-center rounded-lg text-sm font-bold border transition-all ${classes}`}
                      title={sorteado ? 'Sorteado no concurso atual' : undefined}>
                      {n}
                    </span>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {!jogos && !loading && (
        <div className="text-center py-8 text-muted text-sm">
          Clique em <strong>Gerar</strong> para criar jogos diversificados.
        </div>
      )}
    </div>
  );
}
