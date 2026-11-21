'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getValidadorEstatistico } from '@/lib/api';
import { LOTERIAS } from '@/lib/lottery-config';
import type {
  ValidadorBadge,
  ValidadorEstatisticoData,
  ValidadorGrupo,
  ValidadorRepeticao,
  ValidadorTeste,
} from '@/lib/validador-tipos';

interface Props {
  loteria: string;
  /** Valida o histórico até este concurso; vazio = todos. */
  concursoBase?: number;
}

const JANELAS = [
  { value: 10, label: 'Últimos 10' },
  { value: 30, label: 'Últimos 30' },
  { value: 100, label: 'Últimos 100' },
  { value: 300, label: 'Últimos 300' },
  { value: 500, label: 'Últimos 500' },
  { value: 1000, label: 'Últimos 1.000' },
  { value: 0, label: 'Todo o histórico' },
];

const BADGES = [5, 7, 10, 15, 20];

function fmt(v: number, digits = 1): string {
  if (!Number.isFinite(v)) return '—';
  return v.toLocaleString('pt-BR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function fmtPct(v: number, digits = 1): string {
  return `${fmt(v, digits)}%`;
}

function fmtP(p: number): string {
  if (!Number.isFinite(p)) return '—';
  if (p < 0.0001) return '< 0,0001';
  return p.toFixed(4).replace('.', ',');
}

function fmtZ(z: number): string {
  if (!Number.isFinite(z)) return '—';
  return `${z >= 0 ? '+' : ''}${fmt(z, 2)}`;
}

function statusTeste(t: ValidadorTeste): {
  texto: string;
  classe: string;
} {
  if (t.df <= 0) {
    return { texto: 'amostra insuficiente', classe: 'text-muted border-white/10 bg-white/5' };
  }
  if (t.significativoAjustado) {
    return {
      texto: 'significativo (aj.)',
      classe: 'text-hot border-hot/30 bg-hot/10',
    };
  }
  if (t.significativoBruto) {
    return {
      texto: 'bruto; não resiste',
      classe: 'text-amber-200 border-amber-400/30 bg-amber-500/10',
    };
  }
  return {
    texto: 'compatível',
    classe: 'text-emerald-200 border-emerald-400/25 bg-emerald-500/10',
  };
}

function corNumero(z: number): string {
  if (z >= 2) return 'bg-emerald-500/25 border-emerald-400/45 text-emerald-50';
  if (z <= -2) return 'bg-hot/20 border-hot/40 text-hot';
  return 'bg-white/[0.04] border-white/10 text-fg';
}

function TabelaGrupos({
  titulo,
  grupos,
  descricao,
}: {
  titulo: string;
  grupos: ValidadorGrupo[];
  descricao: string;
}) {
  return (
    <div>
      <div className="text-xs font-semibold text-fg mb-2">{titulo}</div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-[11px] border-collapse">
          <thead>
            <tr className="text-muted">
              <th className="pb-2 pr-2 font-normal">Grupo</th>
              <th className="pb-2 pr-2 font-normal">Dezenas</th>
              <th className="pb-2 pr-2 font-normal text-right">Obs</th>
              <th className="pb-2 pr-2 font-normal text-right">Esp</th>
              <th className="pb-2 font-normal text-right">z</th>
            </tr>
          </thead>
          <tbody>
            {grupos.map(g => (
              <tr key={g.id} className="border-t border-white/5">
                <td className="py-1.5 pr-2 text-fg font-medium">{g.rotulo}</td>
                <td className="py-1.5 pr-2 text-muted text-[10px]">
                  <span className="block max-w-[190px] truncate" title={g.dezenas.join(', ')}>
                    {g.dezenas.join(', ')}
                  </span>
                </td>
                <td className="py-1.5 pr-2 text-right text-fg">{g.observado}</td>
                <td className="py-1.5 pr-2 text-right text-muted">{fmt(g.esperado)}</td>
                <td
                  className={`py-1.5 text-right font-medium ${
                    Math.abs(g.z) >= 2 ? 'text-amber-200' : 'text-muted'
                  }`}
                  title={Math.abs(g.z) >= 2 ? 'Desvio > 2σ; exploratório, sem correção individual' : undefined}
                >
                  {fmtZ(g.z)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-[10px] text-muted leading-relaxed">{descricao}</p>
    </div>
  );
}

function TabelaBadges({ badges }: { badges: ValidadorBadge[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-[11px] border-collapse">
        <thead>
          <tr className="text-muted">
            <th className="pb-2 pr-2 font-normal">Badge</th>
            <th className="pb-2 pr-2 font-normal text-right">Pool</th>
            <th className="pb-2 pr-2 font-normal text-right">Acertos</th>
            <th className="pb-2 pr-2 font-normal text-right">Obs</th>
            <th className="pb-2 pr-2 font-normal text-right">Esp</th>
            <th className="pb-2 font-normal text-right">z</th>
          </tr>
        </thead>
        <tbody>
          {badges.map(b => (
            <tr key={b.badge} className="border-t border-white/5">
              <td className="py-1.5 pr-2 text-fg">{b.rotulo}</td>
              <td className="py-1.5 pr-2 text-right text-muted">{fmtPct(b.percentualPool)}</td>
              <td className="py-1.5 pr-2 text-right text-fg">{fmtPct(b.percentualAcertos)}</td>
              <td className="py-1.5 pr-2 text-right text-fg">{b.observado}</td>
              <td className="py-1.5 pr-2 text-right text-muted">{fmt(b.esperado)}</td>
              <td
                className={`py-1.5 text-right font-medium ${
                  Math.abs(b.z) >= 2 ? 'text-amber-200' : 'text-muted'
                }`}
                title={Math.abs(b.z) >= 2 ? 'Desvio > 2σ; exploratório, sem correção individual' : undefined}
              >
                {fmtZ(b.z)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TabelaRepeticao({ distribuicao }: { distribuicao: ValidadorRepeticao[] }) {
  const limite = 8;
  const principais = distribuicao.filter(d => d.repetidas <= limite);
  const resto = distribuicao.filter(d => d.repetidas > limite);
  const linhas = [...principais];
  if (resto.length > 0) {
    linhas.push({
      repetidas: limite + 1,
      observado: resto.reduce((s, d) => s + d.observado, 0),
      esperado: resto.reduce((s, d) => s + d.esperado, 0),
      probabilidade: resto.reduce((s, d) => s + d.probabilidade, 0),
    });
  }
  const totalObs = distribuicao.reduce((s, d) => s + d.observado, 0);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-[11px] border-collapse">
        <thead>
          <tr className="text-muted">
            <th className="pb-2 pr-2 font-normal">Repetidas</th>
            <th className="pb-2 pr-2 font-normal text-right">Obs</th>
            <th className="pb-2 pr-2 font-normal text-right">Obs %</th>
            <th className="pb-2 pr-2 font-normal text-right">Esp</th>
            <th className="pb-2 font-normal text-right">Esp %</th>
          </tr>
        </thead>
        <tbody>
          {linhas.map(d => (
            <tr key={d.repetidas} className="border-t border-white/5">
              <td className="py-1.5 pr-2 text-fg">
                {d.repetidas > limite ? `${limite}+` : d.repetidas}
              </td>
              <td className="py-1.5 pr-2 text-right text-fg">{d.observado}</td>
              <td className="py-1.5 pr-2 text-right text-muted">
                {fmtPct(totalObs > 0 ? (d.observado / totalObs) * 100 : 0)}
              </td>
              <td className="py-1.5 pr-2 text-right text-muted">{fmt(d.esperado)}</td>
              <td className="py-1.5 text-right text-muted">{fmtPct(d.probabilidade * 100)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ValidadorEstatisticoSection({ loteria, concursoBase }: Props) {
  const cfg = LOTERIAS[loteria];
  const [janela, setJanela] = useState<number>(100);
  const [badgeJanela, setBadgeJanela] = useState<number>(7);
  const [data, setData] = useState<ValidadorEstatisticoData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const abortRef = useRef<AbortController | null>(null);
  const loteriaRef = useRef(loteria);

  useEffect(() => {
    if (loteriaRef.current !== loteria) {
      loteriaRef.current = loteria;
      setData(null);
      setError(null);
    }
  }, [loteria]);

  const carregar = useCallback(
    (signal: AbortSignal) => {
      setLoading(true);
      setError(null);
      getValidadorEstatistico(loteria, janela, badgeJanela, concursoBase, signal)
        .then(res => {
          if (!signal.aborted) setData(res);
        })
        .catch(err => {
          if ((err as any)?.name === 'AbortError') return;
          if (!signal.aborted) {
            setError(err instanceof Error ? err.message : 'Erro ao validar estatisticamente.');
          }
        })
        .finally(() => {
          if (!signal.aborted) setLoading(false);
        });
    },
    [loteria, janela, badgeJanela, concursoBase],
  );

  useEffect(() => {
    if (cfg?.is_positional) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const timer = setTimeout(() => carregar(controller.signal), 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [carregar, refreshKey, cfg?.is_positional]);

  const topNumeros = useMemo(() => {
    if (!data) return { quentes: [], frios: [] };
    const ordenados = [...data.numeros].sort((a, b) => b.z - a.z);
    return {
      quentes: ordenados.slice(0, 5),
      frios: ordenados.slice(-5).reverse(),
    };
  }, [data]);

  if (cfg?.is_positional) return null;

  const totalTestes = data?.testes.length ?? 0;
  const verdicto = data
    ? data.significativosAjustados > 0
      ? {
          classe: 'border-amber-400/30 bg-amber-500/[0.07] text-amber-100',
          texto: `${data.significativosAjustados} de ${totalTestes} teste(s) resistiram à correção de Bonferroni. Antes de usar como filtro, valide em outra janela/out-of-sample.`,
        }
      : data.significativosBrutos > 0
        ? {
            classe: 'border-emerald-400/25 bg-emerald-500/[0.06] text-emerald-100',
            texto: `Nenhum teste sobrevive à correção, mas ${data.significativosBrutos} ${
              data.significativosBrutos === 1 ? 'apareceu' : 'apareceram'
            } no bruto — exatamente o esperado em comparações múltiplas.`,
          }
        : {
            classe: 'border-emerald-400/25 bg-emerald-500/[0.06] text-emerald-100',
            texto: 'Nenhum desvio significativo. O histórico é compatível com sorteio uniforme nesta janela.',
          }
    : null;

  return (
    <div className="rounded-2xl border border-[rgba(129,140,248,0.15)] p-4 sm:p-5"
      style={{ background: 'linear-gradient(135deg, rgba(129,140,248,0.05), rgba(16,185,129,0.03))' }}>
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="text-lg font-semibold text-ink flex items-center gap-2">
            Validador Estatístico
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent/15 text-accent-2 border border-accent/20 font-normal">
              {cfg?.nome_jogo ?? loteria}
            </span>
          </h3>
          <p className="text-xs text-muted mt-0.5 max-w-3xl">
            Compara o observado com o esperado em sorteio uniforme. Mede se o padrão é compatível com aleatoriedade;
            não prova vantagem. P-valores aproximados, com correção de Bonferroni para os testes principais.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-3 mb-4">
        <label className="flex flex-col gap-1">
          <span className="text-xs text-muted">Janela</span>
          <select
            value={janela}
            onChange={e => setJanela(Number(e.target.value))}
            className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
          >
            {JANELAS.map(j => (
              <option key={j.value} value={j.value} className="bg-[#1a1d2e]">
                {j.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-xs text-muted">Badge (últimos)</span>
          <select
            value={badgeJanela}
            onChange={e => setBadgeJanela(Number(e.target.value))}
            className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
          >
            {BADGES.map(b => (
              <option key={b} value={b} className="bg-[#1a1d2e]">
                {b} sorteios
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() => setRefreshKey(k => k + 1)}
          disabled={loading}
          className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
        >
          {loading ? 'Calculando...' : 'Atualizar'}
        </button>
        {data && (
          <span className="text-[11px] text-muted">
            Concursos {data.primeiroConcurso ?? '—'}–{data.ultimoConcurso ?? '—'} · {data.janelaEfetiva} sorteio(s) ·{' '}
            {data.totalAcertos} acerto(s)
          </span>
        )}
      </div>

      {error && (
        <div className="mb-3 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-sm">{error}</div>
      )}

      {loading && !data && (
        <div className="py-8 text-center text-sm text-muted">Calculando testes estatísticos...</div>
      )}

      {data && (
        <div className="space-y-5">
          {verdicto && (
            <div className={`rounded-xl border p-3 text-xs leading-relaxed ${verdicto.classe}`}>
              {verdicto.texto}
            </div>
          )}

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <div className="text-[10px] text-muted">Sorteios</div>
              <div className="text-xl font-bold text-fg">{data.janelaEfetiva}</div>
              <div className="text-[10px] text-muted">
                de {data.totalSorteios} · até {data.concursoBase ?? 'último'}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <div className="text-[10px] text-muted">Acertos analisados</div>
              <div className="text-xl font-bold text-fg">{data.totalAcertos}</div>
              <div className="text-[10px] text-muted">{data.numerosPorJogo} por sorteio</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <div className="text-[10px] text-muted">Testes significativos</div>
              <div className="text-xl font-bold text-fg">
                {data.significativosAjustados}
                <span className="text-xs text-muted font-normal"> aj. · {data.significativosBrutos} bruto</span>
              </div>
              <div className="text-[10px] text-muted">Bonferroni em {totalTestes} testes</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <div className="text-[10px] text-muted">Linhas vazias</div>
              <div className="text-xl font-bold text-fg">{fmtPct(data.linhasVazias.percentualComPeloMenosUma)}</div>
              <div className="text-[10px] text-muted">
                esperado {fmtPct(data.linhasVazias.probabilidadeEsperada * 100)} · média{' '}
                {fmt(data.linhasVazias.mediaObservada, 2)} vs {fmt(data.linhasVazias.mediaEsperada, 2)}
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs font-semibold text-fg mb-2">Testes</div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[11px] border-collapse">
                <thead>
                  <tr className="text-muted">
                    <th className="pb-2 pr-2 font-normal">Teste</th>
                    <th className="pb-2 pr-2 font-normal text-right">χ²</th>
                    <th className="pb-2 pr-2 font-normal text-right">gl</th>
                    <th className="pb-2 pr-2 font-normal text-right">p</th>
                    <th className="pb-2 pr-2 font-normal text-right">p ajustado</th>
                    <th className="pb-2 font-normal">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.testes.map(t => {
                    const st = statusTeste(t);
                    return (
                      <tr key={t.id} className="border-t border-white/5">
                        <td className="py-1.5 pr-2 text-fg">
                          {t.nome}
                          {t.detalhe && (
                            <span className="block text-[10px] text-muted font-normal">{t.detalhe}</span>
                          )}
                        </td>
                        <td className="py-1.5 pr-2 text-right text-muted">{fmt(t.chi2, 2)}</td>
                        <td className="py-1.5 pr-2 text-right text-muted">{t.df || '—'}</td>
                        <td className="py-1.5 pr-2 text-right text-fg">{fmtP(t.p)}</td>
                        <td className="py-1.5 pr-2 text-right text-fg">{fmtP(t.pAjustado)}</td>
                        <td className="py-1.5">
                          <span className={`inline-block px-2 py-0.5 rounded-full border text-[10px] ${st.classe}`}>
                            {st.texto}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <TabelaGrupos
              titulo="Linhas (faixas da grade)"
              grupos={data.linhas}
              descricao={`Esperado por linha = sorteios × ${data.numerosPorJogo} × (dezenas da linha ÷ ${data.totalNumeros}). z é exploratório.`}
            />
            <TabelaGrupos
              titulo="Colunas (posição na grade)"
              grupos={data.colunas}
              descricao={
                data.colunasGrade === 10
                  ? 'Colunas da grade com dezenas de mesmo final. z é exploratório, sem correção individual.'
                  : 'Colunas da grade (posição na matriz). z é exploratório, sem correção individual.'
              }
            />
          </div>

          <div>
            <div className="flex flex-wrap items-baseline justify-between gap-2 mb-2">
              <div className="text-xs font-semibold text-fg">
                Badges (frequência nos últimos {data.badgeJanela} sorteios)
              </div>
              <div className="text-[10px] text-muted">
                {data.badgeSorteios} sorteio(s) com histórico completo · pool = % do universo; acertos = % dos acertos
              </div>
            </div>
            <TabelaBadges badges={data.badges} />
            <p className="mt-2 text-[10px] text-muted leading-relaxed">
              O ponto de comparação é <strong className="text-fg">Pool vs Acertos</strong>. Se forem parecidos, a badge
              não está superrepresentada. Badge 3+ = 3 ou mais aparições na janela.
            </p>
          </div>

          <div>
            <div className="flex flex-wrap items-baseline justify-between gap-2 mb-2">
              <div className="text-xs font-semibold text-fg">Repetição do concurso anterior</div>
              <div className="text-[10px] text-muted">
                {data.repeticao.pares} par(es) · média obs {fmt(data.repeticao.mediaObservada, 2)} vs esp{' '}
                {fmt(data.repeticao.mediaEsperada, 2)}
              </div>
            </div>
            <TabelaRepeticao distribuicao={data.repeticao.distribuicao} />
          </div>

          <div>
            <div className="flex flex-wrap items-baseline justify-between gap-2 mb-2">
              <div className="text-xs font-semibold text-fg">Mapa de calor por dezena</div>
              <div className="text-[10px] text-muted">
                cores descritivas por z; o teste formal é a “Uniformidade das dezenas” acima
              </div>
            </div>
            <div
              className="grid gap-1.5"
              style={{ gridTemplateColumns: `repeat(${data.colunasGrade}, minmax(0, 1fr))` }}
            >
              {data.numeros.map(n => (
                <div
                  key={n.numero}
                  className={`rounded-md border px-1 py-1 text-center ${corNumero(n.z)}`}
                  title={`${n.numero}: ${n.observado} observado(s) · ${fmt(n.esperado)} esperado(s) · z ${fmtZ(n.z)}`}
                >
                  <div className="text-[10px] font-semibold leading-tight">{n.numero}</div>
                  <div className="text-[9px] leading-tight opacity-85">{n.observado}</div>
                </div>
              ))}
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-[10px] text-muted">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-emerald-500/25 border border-emerald-400/45" /> z ≥ +2
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-hot/20 border border-hot/40" /> z ≤ −2
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-white/[0.04] border border-white/10" /> dentro de ±2
              </span>
              <span>
                Mais acima: {topNumeros.quentes.map(n => n.numero).join(', ') || '—'} · mais abaixo:{' '}
                {topNumeros.frios.map(n => n.numero).join(', ') || '—'}
              </span>
            </div>
          </div>

          {data.avisos.length > 0 && (
            <div className="rounded-xl border border-white/10 bg-white/[0.02] p-3">
              <div className="text-[11px] font-semibold text-fg mb-1">Avisos</div>
              <ul className="list-disc pl-4 space-y-0.5 text-[10px] text-muted leading-relaxed">
                {data.avisos.map((aviso, i) => (
                  <li key={i}>{aviso}</li>
                ))}
              </ul>
            </div>
          )}

          <p className="text-[10px] text-muted leading-relaxed">
            Leitura correta: p alto = compatível com aleatoriedade; p baixo no bruto pode ser comparação múltipla. Com
            janelas grandes, desvios minúsculos podem gerar p baixo — olhe também a diferença observado − esperado
            (efeito), não só o p. O teste de uniformidade por dezena assume sorteios independentes e é aproximado.
            Nenhum resultado aqui aumenta o EV; no máximo, ajuda a evitar filtros que são só ruído.
          </p>
        </div>
      )}
    </div>
  );
}
