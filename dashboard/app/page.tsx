'use client';

import { Suspense, useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { getDashboardData, getAnaliseGrupos } from '@/lib/api';
import type { DashboardData } from '@/types';
import type { AnaliseGruposData } from '@/lib/analise-grupos';
import { LOTERIAS } from '@/lib/lottery-config';
import { DrawnNumbersProvider } from '@/lib/DrawnNumbersContext';
import TopBar from '@/components/TopBar';
import HeroSection from '@/components/HeroSection';
import PalpiteSection from '@/components/PalpiteSection';
import QmfSection from '@/components/QmfSection';
import TransicaoSection from '@/components/TransicaoSection';
import CiclosSection from '@/components/CiclosSection';
import PrevisaoSection from '@/components/PrevisaoSection';
import AtrasadosSection from '@/components/AtrasadosSection';
import TrevoSection from '@/components/TrevoSection';
import GruposSection from '@/components/GruposSection';
import ChatBot from '@/components/ChatBot';
import ReentradasSection from '@/components/ReentradasSection';
import ConcursoSelector from '@/components/ConcursoSelector';
import ConferidorSection from '@/components/ConferidorSection';
import SuperSeteSection from '@/components/SuperSeteSection';
import QuarantineMatrixLotofacil from '@/components/QuarantineMatrixLotofacil';
import ComparativoSection from '@/components/ComparativoSection';
import AiAnalysis from '@/components/AiAnalysis';
import RankingCombinacoesSection from '@/components/RankingCombinacoesSection';

function LoadingSkeleton() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
      <div className="relative mb-8">
        <div className="w-20 h-20 rounded-full border-4 border-[rgba(129,140,248,0.15)] border-t-[#818cf8] animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#818cf8] to-[#a78bfa] animate-pulse" />
        </div>
      </div>
      <div className="flex gap-1.5 mb-4">
        {[0, 1, 2].map(i => (
          <div key={i}
            className="w-2.5 h-2.5 rounded-full bg-[#818cf8] animate-bounce"
            style={{ animationDelay: `${i * 0.15}s`, animationDuration: '0.8s' }}
          />
        ))}
      </div>
      <p className="text-sm text-[#818cf8] font-medium tracking-wide animate-pulse">
        CARREGANDO DADOS
      </p>
      <div className="mt-6 flex gap-3">
        {[0, 1, 2, 3].map(i => (
          <div key={i}
            className="w-16 h-3 rounded-full bg-white/5 animate-shimmer"
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense>
      <HomePage />
    </Suspense>
  );
}

function HomePage() {
  const searchParams = useSearchParams();
  const [data, setData] = useState<DashboardData | null>(null);
  const [grupos, setGrupos] = useState<AnaliseGruposData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [janela, setJanela] = useState<number>(30);
  const [loteria, setLoteria] = useState<string>('lotofacil');
  const [concurso, setConcurso] = useState<number | undefined>(undefined);
  const [concursosDisponiveis, setConcursosDisponiveis] = useState<number[]>([]);

  useEffect(() => {
    const l = searchParams.get('loteria');
    if (l && LOTERIAS[l]) setLoteria(l);
  }, [searchParams]);

  const fetchData = useCallback((jan?: number, lot?: string, conc?: number) => {
    const ctrl = new AbortController();
    setLoading(true);
    setError(null);
    const promises: Promise<any>[] = [getDashboardData(jan, ctrl.signal, lot, conc)];
    if (!lot || lot === 'lotofacil') {
      promises.push(getAnaliseGrupos(ctrl.signal));
    } else {
      promises.push(Promise.resolve(null));
    }
    Promise.all(promises)
      .then(([d, g]) => { setData(d); setGrupos(g); setConcursosDisponiveis(d.concursos_disponiveis); })
      .catch(err => {
        if (err.name !== 'AbortError') setError(err.message);
      })
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, []);

  useEffect(() => fetchData(janela, loteria, concurso), [fetchData, janela, loteria, concurso]);

  const handleJanelaChange = useCallback((valor: number) => {
    setJanela(valor);
  }, []);

  const handleLoteriaChange = useCallback((id: string) => {
    const url = new URL(window.location.href);
    if (id === 'lotofacil') url.searchParams.delete('loteria');
    else url.searchParams.set('loteria', id);
    window.history.pushState({}, '', url.toString());
    setLoteria(id);
    setConcurso(undefined);
    setConcursosDisponiveis([]);
  }, []);

  return (
    <DrawnNumbersProvider numeros={data?.ultimo_sorteio?.numeros ?? []}>
    <div className="min-h-screen bg-base">
      <TopBar loteria={loteria} onLoteriaChange={handleLoteriaChange} />
      <main className="max-w-[1360px] mx-auto px-4 sm:px-5 py-4 sm:py-6">
        {loading && <LoadingSkeleton />}

        {error && (
          <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
            <div className="w-14 h-14 rounded-full bg-hot/15 flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-hot" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-[#fca5a5] text-sm mb-4">Erro ao carregar dados: {error}</p>
            <button
              onClick={() => fetchData(janela, loteria, concurso)}
              className="px-5 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
            >
              Tentar novamente
            </button>
          </div>
        )}

        {data && (
          <div className="animate-fade-in">
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <label className="text-sm text-muted">Concurso base:</label>
              <ConcursoSelector
                concursos={concursosDisponiveis}
                value={concurso}
                onChange={setConcurso}
                totalSorteios={data.total_sorteios}
              />
              {concurso ? (
                <span className="text-xs text-accent-2">
                  análise até concurso <strong>{data.concurso_analisado}</strong> ({concursosDisponiveis.indexOf(concurso) + 1} sorteios)
                </span>
              ) : (
                <span className="text-xs text-muted">
                  todos os {concursosDisponiveis.length} sorteios
                </span>
              )}
            </div>
            <HeroSection
              u={data.ultimo_sorteio}
              concurso={data.ultimo_concurso}
              total={data.total_sorteios}
              medias={data.medias_historicas}
              nomeJogo={data.nome_jogo || LOTERIAS[loteria]?.nome_jogo}
              numerosPorJogo={data.numeros_por_jogo}
              totalNumeros={data.total_numeros}
              comparativo={data.comparativo_posicional}
            />
            {data.supersete && (
              <div className="animate-slide-up stagger-1 mt-6">
                <SuperSeteSection data={data.supersete} />
              </div>
            )}
            {loteria === 'lotofacil' && (
              <div className="mb-6">
                <ReentradasSection />
              </div>
            )}
            {data.tendencia_comparativo && data.tendencia_comparativo.length > 0 && loteria === 'lotofacil' && (
              <div className="mb-6">
                <ComparativoSection data={data.tendencia_comparativo} />
              </div>
            )}
            {data.tem_trevos && data.frequencia_trevos_total && (
              <div className="animate-slide-up stagger-1">
                <TrevoSection
                  trevosUltimo={data.ultimo_sorteio.trevos ?? []}
                  frequenciaTotal={data.frequencia_trevos_total}
                  frequenciaRecente={data.frequencia_trevos_recente!}
                  gaps={data.gaps_trevos!}
                  quentes={data.trevos_quentes!}
                  frios={data.trevos_frios!}
                  mornos={data.trevos_mornos!}
                  ciclos={data.ciclos_trevos!}
                  janela={data.janela_usada}
                />
              </div>
            )}
            <div className="animate-slide-up stagger-2">
              <PalpiteSection palpite={data.palpite} previsao_combinada={data.previsao_combinada} loteria={loteria} />
            </div>
            <div className="animate-slide-up stagger-2">
              <QmfSection
                quentes={data.numeros_quentes}
                mornos={data.numeros_mornos}
                frios={data.numeros_frios}
                janela={data.janela_usada}
                totalSorteios={data.total_sorteios}
                numerosPorJogo={data.numeros_por_jogo}
                totalNumeros={data.total_numeros}
                loteria={loteria}
                onJanelaChange={handleJanelaChange}
                quarentenaPosicoes={data.quarentena_posicoes}
              />
            </div>
            <div className="animate-slide-up stagger-3">
              <TransicaoSection t={data.transicao_qmf} janela={data.janela_usada} numerosPorJogo={data.numeros_por_jogo} />
            </div>
            <div className="animate-slide-up stagger-4">
              <CiclosSection ciclos={data.ciclos} />
            </div>
            <div className="animate-slide-up stagger-5">
              <PrevisaoSection previsao={data.previsao_posicional} />
            </div>
            <div className="animate-slide-up stagger-6">
              <AtrasadosSection atrasados={data.atrasados_posicionais} />
            </div>
            {data.quarentena_posicoes && loteria !== 'supersete' && (
              <div className="animate-slide-up stagger-6">
                <QuarantineMatrixLotofacil quarentena={data.quarentena_posicoes} />
              </div>
            )}
            {grupos && (
              <div className="animate-slide-up stagger-7">
                <GruposSection data={grupos} />
              </div>
            )}
            {loteria === 'lotofacil' && data.ranking_combinacoes && (
              <div className="animate-slide-up stagger-8">
                <RankingCombinacoesSection ranking={data.ranking_combinacoes} />
              </div>
            )}
            <div className="animate-slide-up stagger-8">
              <AiAnalysis loteria={loteria} />
            </div>
            <div className="animate-slide-up stagger-8">
              <ConferidorSection
                sorteioAtual={data.ultimo_sorteio.numeros}
                numerosPorJogo={data.numeros_por_jogo}
                loteria={loteria}
              />
            </div>
          </div>
        )}
      </main>
      <ChatBot janela={janela} loteria={loteria} concurso={concurso} />
    </div>
    </DrawnNumbersProvider>
  );
}
