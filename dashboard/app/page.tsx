'use client';

import { useEffect, useState, useCallback } from 'react';
import { getDashboardData, getAnaliseGrupos } from '@/lib/api';
import type { DashboardData } from '@/types';
import type { AnaliseGruposData } from '@/lib/analise-grupos';
import TopBar from '@/components/TopBar';
import HeroSection from '@/components/HeroSection';
import PalpiteSection from '@/components/PalpiteSection';
import QmfSection from '@/components/QmfSection';
import TransicaoSection from '@/components/TransicaoSection';
import CiclosSection from '@/components/CiclosSection';
import PrevisaoSection from '@/components/PrevisaoSection';
import AtrasadosSection from '@/components/AtrasadosSection';
import GruposSection from '@/components/GruposSection';
import ChatBot from '@/components/ChatBot';

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
  const [data, setData] = useState<DashboardData | null>(null);
  const [grupos, setGrupos] = useState<AnaliseGruposData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [janela, setJanela] = useState<number>(30);

  const fetchData = useCallback((jan?: number) => {
    const ctrl = new AbortController();
    setLoading(true);
    setError(null);
    Promise.all([
      getDashboardData(jan, ctrl.signal),
      getAnaliseGrupos(ctrl.signal),
    ])
      .then(([d, g]) => { setData(d); setGrupos(g); })
      .catch(err => {
        if (err.name !== 'AbortError') setError(err.message);
      })
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, []);

  useEffect(() => fetchData(janela), [fetchData, janela]);

  const handleJanelaChange = useCallback((valor: number) => {
    setJanela(valor);
  }, []);

  return (
    <div className="min-h-screen bg-base">
      <TopBar />
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
              onClick={() => fetchData(janela)}
              className="px-5 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110"
              style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}
            >
              Tentar novamente
            </button>
          </div>
        )}

        {data && (
          <div className="animate-fade-in">
            <HeroSection
              u={data.ultimo_sorteio}
              concurso={data.ultimo_concurso}
              total={data.total_sorteios}
              medias={data.medias_historicas}
            />
            <div className="animate-slide-up stagger-1">
              <PalpiteSection palpite={data.palpite} previsao_combinada={data.previsao_combinada} />
            </div>
            <div className="animate-slide-up stagger-2">
              <QmfSection
                quentes={data.numeros_quentes}
                mornos={data.numeros_mornos}
                frios={data.numeros_frios}
                janela={data.janela_usada}
                totalSorteios={data.total_sorteios}
                onJanelaChange={handleJanelaChange}
              />
            </div>
            <div className="animate-slide-up stagger-3">
              <TransicaoSection t={data.transicao_qmf} janela={data.janela_usada} />
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
            {grupos && (
              <div className="animate-slide-up stagger-7">
                <GruposSection data={grupos} />
              </div>
            )}
          </div>
        )}
      </main>
      <ChatBot janela={janela} />
    </div>
  );
}
