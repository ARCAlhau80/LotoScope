'use client';

import { useState, useCallback, useEffect, useMemo } from 'react';
import { getLotteryConfig, dezenasValidas, calcularPrecoAposta } from '@/lib/lottery-config';
import type { PrevisaoItem, PrevisaoTendenciaComparativo, PrevisaoColunaRange } from '@/types';
import GeneratingOverlay from '@/components/GeneratingOverlay';

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
  previsaoPosicional?: Record<string, PrevisaoItem[]> | null;
  previsaoTendencia?: PrevisaoTendenciaComparativo;
  previsaoColunas?: PrevisaoColunaRange[];
}

const ESTRATEGIA_LABEL: Record<string, string> = {
  atraso: 'Atrasados',
  'hot7-9': 'Quentes',
  persistencia: 'Persistência',
  aleatorio: 'Aleatório',
  ciclo: 'Ciclo',
  colunas: 'Colunas',
  comparativo: 'Comparativo',
};

type NumeroEstado = 'normal' | 'fixo' | 'excluido';

export default function JogosDiversosSection({ loteria = 'lotofacil', concursoBase, numerosSorteadosAtual = [], previsaoPosicional, previsaoTendencia, previsaoColunas }: JogosDiversosSectionProps) {
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
  const [progresso, setProgresso] = useState(0);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [colunasInputs, setColunasInputs] = useState<string[]>(['', '', '', '', '']);
  const [comparativoInputs, setComparativoInputs] = useState<string[]>(['', '', '']);
  const [fixosPosicoes, setFixosPosicoes] = useState<Record<number, number[]>>({});
  const [excluidosPosicoes, setExcluidosPosicoes] = useState<Record<number, number[]>>({});

  const colunasSets = useMemo(() => {
    if (!previsaoPosicional) return null;
    const sets: number[][] = [[], [], [], [], []];
    for (const pos of Object.keys(previsaoPosicional)) {
      const preds = previsaoPosicional[pos] || [];
      preds.slice(0, 5).forEach((x, c) => sets[c].push(x.numero));
    }
    return sets.map(s => [...new Set(s)]);
  }, [previsaoPosicional]);

  useEffect(() => {
    const novoCfg = getLotteryConfig(loteria);
    setEstados({});
    setJogos(null);
    setEstatisticas(null);
    setCicloAtual(null);
    setEstimativaTotal(null);
    setDezenas(novoCfg.numeros_por_jogo);
    setColunasInputs(['', '', '', '', '']);
    setComparativoInputs(['', '', '']);
    setFixosPosicoes({});
    setExcluidosPosicoes({});
  }, [loteria]);

  useEffect(() => {
    setJogos(null);
    setEstatisticas(null);
    setEstimativaTotal(null);
    setError(null);
  }, [colunasInputs, comparativoInputs]);

  useEffect(() => {
    if (!loading) return;
    setProgresso(0);
    const id = setInterval(() => {
      setProgresso(p => (p >= 90 ? p : Math.min(90, Math.round(p + Math.max(1, (90 - p) * 0.09)))));
    }, 130);
    return () => clearInterval(id);
  }, [loading]);

  const fixos = Object.entries(estados).filter(([, e]) => e === 'fixo').map(([n]) => Number(n));
  const excluidos = Object.entries(estados).filter(([, e]) => e === 'excluido').map(([n]) => Number(n));
  const sorteadosAtualSet = new Set(numerosSorteadosAtual);

  const colunasPosicionaisStr = colunasInputs.map(v => v.trim().replace(/\s+/g, '')).join(',');
  const colunasSetsStr = colunasSets ? colunasSets.map(s => s.join(',')).join(';') : '';
  const temColunas = colunasInputs.some(v => v.trim() !== '') && colunasSets !== null;

  const comparativoStr = comparativoInputs.map(v => v.trim()).join(',');
  const temComparativo = comparativoInputs.some(v => v.trim() !== '');

  const numeroMaximo = cfg.numero_minimo + cfg.total_numeros - 1;
  const posicoesValidas = (n: number) => {
    const lo = Math.max(1, n - numeroMaximo + dezenas);
    const hi = Math.min(dezenas, n - cfg.numero_minimo + 1);
    const res: number[] = [];
    for (let p = lo; p <= hi; p++) res.push(p);
    return res;
  };
  const fixosPosicoesStr = Object.entries(fixosPosicoes)
    .filter(([, ps]) => ps.length > 0)
    .map(([n, ps]) => `${n}:${ps.join(',')}`)
    .join(';');
  const excluidosCompletos = excluidos.filter(n => !(excluidosPosicoes[n] ?? []).length);
  const excluidosPosicoesStr = Object.entries(excluidosPosicoes)
    .filter(([, ps]) => ps.length > 0)
    .map(([n, ps]) => `${n}:${ps.join(',')}`)
    .join(';');

  const usarPrevisaoTendencia = () => {
    if (!previsaoTendencia) {
      setError('Previsão da Tendência Posicional indisponível. Recarregue o dashboard.');
      return;
    }
    const cats = previsaoTendencia.categorias;
    setComparativoInputs([
      `${cats.maiores.p25}-${cats.maiores.p75}`,
      `${cats.iguais.p25}-${cats.iguais.p75}`,
      `${cats.menores.p25}-${cats.menores.p75}`,
    ]);
  };

  const usarPrevisaoColunas = () => {
    if (!previsaoColunas || previsaoColunas.length < 5) {
      setError('Faixas da Previsão Posicional indisponíveis. Recarregue o dashboard.');
      return;
    }
    setColunasInputs(previsaoColunas.map(r => `${r.p25}-${r.p75}`));
  };

  const validarColunas = (): string | null => {
    if (!colunasInputs.some(v => v.trim() !== '')) return null;
    if (!colunasSets) return 'Dados de previsão posicional indisponíveis. Recarregue o dashboard.';
    const pattern = /^\d+(-\d+)?$/;
    for (const v of colunasInputs) {
      if (v.trim() === '') continue;
      if (!pattern.test(v.trim())) return 'Formato inválido nas colunas posicionais. Use "min" ou "min-max", ex.: 7-8';
    }
    return null;
  };

  const toggleNumero = useCallback((n: number) => {
    setEstados(prev => {
      const atual = prev[n] || 'normal';
      let proximo: NumeroEstado;
      if (atual === 'normal') proximo = 'fixo';
      else if (atual === 'fixo') proximo = 'excluido';
      else proximo = 'normal';
      return { ...prev, [n]: proximo };
    });
    setFixosPosicoes(prev => {
      if (!(n in prev)) return prev;
      const copy = { ...prev };
      delete copy[n];
      return copy;
    });
    setExcluidosPosicoes(prev => {
      if (!(n in prev)) return prev;
      const copy = { ...prev };
      delete copy[n];
      return copy;
    });
  }, []);

  const togglePosicaoFixo = useCallback((n: number, p: number) => {
    setFixosPosicoes(prev => {
      const atuais = prev[n] || [];
      const proximas = atuais.includes(p) ? atuais.filter(x => x !== p) : [...atuais, p];
      return { ...prev, [n]: proximas };
    });
  }, []);

  const toggleExclusaoPosicao = useCallback((n: number, p: number) => {
    setExcluidosPosicoes(prev => {
      const atuais = prev[n] || [];
      const proximas = atuais.includes(p) ? atuais.filter(x => x !== p) : [...atuais, p];
      return { ...prev, [n]: proximas };
    });
  }, []);

  const limparSelecao = useCallback(() => {
    setEstados({});
    setFixosPosicoes({});
    setExcluidosPosicoes({});
  }, []);

  const gerar = useCallback(async () => {
    const colunasErr = validarColunas();
    if (colunasErr) {
      setError(colunasErr);
      return;
    }
    if (temComparativo && comparativoInputs.some(v => v.trim() !== '' && !/^\d+(-\d+)?$/.test(v.trim()))) {
      setError('Formato inválido no filtro comparativo. Use "min-max" ou "min", ex.: 2-5');
      return;
    }
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
      if (excluidosCompletos.length > 0) params.set('excluidos', excluidosCompletos.join(','));
      if (concursoBase !== undefined) params.set('concurso', String(concursoBase));
      if (fixos.length > 0 && fixosPosicoesStr) params.set('fixos_posicoes', fixosPosicoesStr);
      if (excluidosPosicoesStr) params.set('excluidos_posicoes', excluidosPosicoesStr);
      if (temColunas) {
        params.set('colunas_posicionais', colunasPosicionaisStr);
        params.set('colunas_sets', colunasSetsStr);
      }
      if (temComparativo) params.set('comparativo', comparativoStr);

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
      setProgresso(100);
      setTimeout(() => setLoading(false), 450);
    }
  }, [loteria, quantidade, dezenas, fixos, excluidos, excluidosCompletos, concursoBase, temColunas, colunasPosicionaisStr, colunasSetsStr, validarColunas, temComparativo, comparativoStr, fixosPosicoesStr, excluidosPosicoesStr]);

  const exportarTodas = useCallback(async () => {
    const colunasErr = validarColunas();
    if (colunasErr) {
      setError(colunasErr);
      return;
    }
    if (temComparativo && comparativoInputs.some(v => v.trim() !== '' && !/^\d+(-\d+)?$/.test(v.trim()))) {
      setError('Formato inválido no filtro comparativo. Use "min-max" ou "min", ex.: 2-5');
      return;
    }
    setExporting(true);
    setError(null);
    try {
      const seed = Date.now();
      const params = new URLSearchParams();
      params.set('loteria', loteria);
      params.set('seed', String(seed));
      params.set('dezenas', String(dezenas));
      if (fixos.length > 0) params.set('fixos', fixos.join(','));
      if (excluidosCompletos.length > 0) params.set('excluidos', excluidosCompletos.join(','));
      if (concursoBase !== undefined) params.set('concurso', String(concursoBase));
      if (fixos.length > 0 && fixosPosicoesStr) params.set('fixos_posicoes', fixosPosicoesStr);
      if (excluidosPosicoesStr) params.set('excluidos_posicoes', excluidosPosicoesStr);
      if (temColunas) {
        params.set('colunas_posicionais', colunasPosicionaisStr);
        params.set('colunas_sets', colunasSetsStr);
      }
      if (temComparativo) params.set('comparativo', comparativoStr);

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
  }, [loteria, dezenas, fixos, excluidos, excluidosCompletos, concursoBase, temColunas, colunasPosicionaisStr, colunasSetsStr, validarColunas, temComparativo, comparativoStr, comparativoInputs, fixosPosicoesStr, excluidosPosicoesStr]);

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

      {previsaoPosicional && (
        <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="text-sm font-semibold text-[#e0e7ff]">Colunas Posicionais (Previsão Posicional)</div>
            <div className="text-xs text-muted">
              min-max de números de cada coluna <strong className="text-fg">#1..#5</strong> por jogo. Ex.: <strong className="text-fg">7-8</strong> (min 7, máx 8) ou <strong className="text-fg">3</strong> (mínimo 3, sem limite). Vazio = sem restrição.
            </div>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            {colunasInputs.map((v, i) => (
              <label key={i} className="flex flex-col items-center gap-1">
                <span className="text-[11px] text-muted">
                  #{i + 1}
                  {colunasSets && <span className="ml-1 text-accent-2">({colunasSets[i]?.length ?? 0} nºs)</span>}
                </span>
                <input
                  type="text"
                  inputMode="numeric"
                  value={v}
                  onChange={e => setColunasInputs(prev => prev.map((x, j) => (j === i ? e.target.value : x)))}
                  placeholder="min-max"
                  className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] text-center placeholder:text-muted/50"
                />
              </label>
            ))}
            <button
              onClick={usarPrevisaoColunas}
              disabled={!previsaoColunas || previsaoColunas.length < 5}
              className="px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg,#10b981,#34d399)' }}
              title={previsaoColunas && previsaoColunas.length >= 5
                ? 'Preenche com as faixas P25–P75 de acerto histórico de cada coluna'
                : 'Faixas indisponíveis para esta loteria'}
            >
              Usar previsão da Posicional
            </button>
            <button
              onClick={() => setColunasInputs(['', '', '', '', ''])}
              className="px-3 py-2 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
            >
              Limpar
            </button>
            <div className="flex-1 text-[11px] text-muted leading-relaxed">
              A soma dos mínimos nunca pode ultrapassar as <strong className="text-fg">{dezenas}</strong> dezenas por jogo (a distribuição é adaptada
              automaticamente). Se a soma for menor que o jogo, os números restantes são preenchidos <strong className="text-fg">aleatoriamente</strong>.
              O botão <strong className="text-fg">"Usar previsão da Posicional"</strong> preenche com a faixa central (P25–P75) de quantos
              números de cada coluna costumaram sair nos últimos 100 sorteios.
            </div>
          </div>
        </div>
      )}

      <div className="mb-5 p-4 rounded-xl bg-white/5 border border-white/10">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="text-sm font-semibold text-[#e0e7ff]">Filtro Comparativo (Tendência Posicional)</div>
          <div className="text-xs text-muted">
            Cada jogo é comparado posição a posição com o último sorteio: quantas posições ficam ▲ maiores / ▼ menores / = iguais.
            Ex.: <strong className="text-fg">2-5</strong> = a quantidade de iguais no jogo deve ficar entre 2 e 5.
          </div>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          {comparativoInputs.map((v, i) => (
            <label key={i} className="flex flex-col items-center gap-1">
              <span className="text-[11px] text-muted">{['▲ Maiores', '= Iguais', '▼ Menores'][i]}</span>
              <input
                type="text"
                inputMode="numeric"
                value={v}
                onChange={e => setComparativoInputs(prev => prev.map((x, j) => (j === i ? e.target.value : x)))}
                placeholder="min-max"
                className="w-20 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8] text-center placeholder:text-muted/50"
              />
            </label>
          ))}
          <button
            onClick={usarPrevisaoTendencia}
            className="px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all hover:brightness-110"
            style={{ background: 'linear-gradient(135deg,#10b981,#34d399)' }}
            title="Preenche com as faixas P25–P75 da previsão da Tendência Posicional"
          >
            Usar previsão da Tendência
          </button>
          <button
            onClick={() => setComparativoInputs(['', '', ''])}
            className="px-3 py-2 rounded-lg text-xs bg-white/5 border border-white/10 text-muted hover:text-fg hover:bg-white/10 transition-colors"
          >
            Limpar
          </button>
          <div className="flex-1 text-[11px] text-muted leading-relaxed">
            Vazio = sem restrição na categoria. O botão <strong className="text-fg">"Usar previsão"</strong> usa as faixas
            centrais (P25–P75) calculadas na Tendência Posicional.
            {dezenas !== cfg.numeros_por_jogo && (
              <div className="mt-1 text-amber-200/80">
                Jogo com {dezenas} dezenas: o comparativo é aplicado às primeiras {cfg.numeros_por_jogo} posições
                (o sorteio tem {cfg.numeros_por_jogo} dezenas).
              </div>
            )}
          </div>
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
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-muted">Fixos:</span>
                {fixos.map(n => {
                  const validas = posicoesValidas(n);
                  const selecionadas = fixosPosicoes[n] || [];
                  return (
                    <div
                      key={n}
                      className="flex flex-wrap items-center gap-1 px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-500/30"
                      title={selecionadas.length > 0
                        ? `Restrito às posições N${selecionadas.join(', N')}`
                        : 'Usado em qualquer posição válida'}
                    >
                      <span className="font-semibold">{n}</span>
                      <div className="flex items-center gap-0.5">
                        {validas.map(p => {
                          const ativo = selecionadas.includes(p);
                          return (
                            <button
                              key={p}
                              onClick={() => togglePosicaoFixo(n, p)}
                              title={`Restringir ${n} à posição N${p}`}
                              className={`text-[10px] px-1.5 py-0.5 rounded-full border leading-none transition-colors ${
                                ativo
                                  ? 'bg-emerald-400 text-emerald-950 border-emerald-300 font-bold'
                                  : 'bg-transparent text-emerald-200/60 border-emerald-500/25 hover:bg-emerald-400/15'
                              }`}
                            >
                              N{p}
                            </button>
                          );
                        })}
                      </div>
                      {selecionadas.length === 0 && (
                        <span className="text-[10px] text-emerald-200/50">(qualquer)</span>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
            {excluidos.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-muted">Excluídos:</span>
                {excluidos.map(n => {
                  const validas = posicoesValidas(n);
                  const proibidas = excluidosPosicoes[n] || [];
                  const completa = proibidas.length === 0;
                  return (
                    <div
                      key={n}
                      className="flex flex-wrap items-center gap-1 px-2 py-1 rounded-full bg-hot/15 text-hot/80 border border-hot/30"
                      title={completa
                        ? 'Excluído completamente'
                        : `Excluído das posições N${proibidas.join(', N')}`}
                    >
                      <span className="font-semibold">{n}</span>
                      {validas.length > 0 && (
                        <div className="flex items-center gap-0.5">
                          {validas.map(p => {
                            const proibido = proibidas.includes(p);
                            return (
                              <button
                                key={p}
                                onClick={() => toggleExclusaoPosicao(n, p)}
                                title={`Excluir ${n} da posição N${p}`}
                                className={`text-[10px] px-1.5 py-0.5 rounded-full border leading-none transition-colors ${
                                  proibido
                                    ? 'bg-hot/40 text-hot border-hot/60 font-bold'
                                    : 'bg-transparent text-hot/50 border-hot/25 hover:bg-hot/20'
                                }`}
                              >
                                N{p}
                              </button>
                            );
                          })}
                        </div>
                      )}
                      {completa && (
                        <span className="text-[10px] text-hot/60">(completa)</span>
                      )}
                    </div>
                  );
                })}
              </div>
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
          {jogos.length === 0 ? (
            <div className="text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
              Nenhum jogo atende às restrições de colunas posicionais. Ajuste os mínimos/máximos ou remova exclusões.
            </div>
          ) : jogos.length < quantidade && !modoTodas ? (
            <div className="text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
              Pedidos {quantidade} jogo(s), mas apenas <strong>{jogos.length}</strong> atendem às restrições de colunas posicionais.
              Os demais foram descartados.
            </div>
          ) : null}
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

      <GeneratingOverlay show={loading} progress={progresso} />
    </div>
  );
}
