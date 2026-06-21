'use client';

import { getLotteryConfig } from '@/lib/lottery-config';

const PRIMOS_LF = new Set([2, 3, 5, 7, 11, 13, 17, 19, 23]);

function PalpiteCard({ titulo, badge, numeros, primosSet = PRIMOS_LF }: { titulo: string; badge: string; numeros: number[]; primosSet?: Set<number> }) {
  const soma = numeros.reduce((a, b) => a + b, 0);
  const pares = numeros.filter(n => n % 2 === 0).length;
  const impares = numeros.filter(n => n % 2 === 1).length;
  const primos = numeros.filter(n => primosSet.has(n)).length;

  return (
    <div className="relative rounded-2xl p-6 text-center border border-[rgba(129,140,248,0.15)] animate-pulse-glow"
      style={{ background: 'linear-gradient(135deg, rgba(129,140,248,0.08), rgba(52,211,153,0.05))' }}>
      <div className="flex flex-wrap gap-2 justify-center mb-3">
        {numeros.map((n, i) => (
          <span key={i}
            className="w-10 h-10 flex items-center justify-center rounded-xl text-sm font-bold
              bg-[rgba(129,140,248,0.15)] text-accent-2 border border-[rgba(129,140,248,0.25)]
              animate-slide-up transition-all duration-200 hover:scale-110 hover:brightness-125"
            style={{ animationDelay: `${i * 0.04}s` }}>
            {n}
          </span>
        ))}
      </div>
      <div className="flex flex-wrap gap-x-6 gap-y-1 justify-center text-sm text-muted">
        <span>Soma: <strong className="text-fg">{soma}</strong></span>
        <span>Pares: <strong className="text-fg">{pares}</strong></span>
        <span>Ímpares: <strong className="text-fg">{impares}</strong></span>
        <span>Primos: <strong className="text-fg">{primos}</strong></span>
      </div>
    </div>
  );
}

export default function PalpiteSection({ palpite, previsao_combinada, loteria }: { palpite: number[]; previsao_combinada: number[]; loteria?: string }) {
  const primosSet = loteria ? new Set(getLotteryConfig(loteria).primos) : PRIMOS_LF;
  if (!palpite || palpite.length === 0) return null;

  return (
    <div className="mb-8 space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
          Previsão para o Próximo Sorteio
          <span className="text-[11px] bg-accent/15 text-accent-2 px-2 py-0.5 rounded font-normal">Poisson blend</span>
        </h3>
        <PalpiteCard titulo="" badge="" numeros={palpite} primosSet={primosSet} />
      </div>
      {previsao_combinada && previsao_combinada.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-[#e0e7ff] flex items-center gap-2">
            Previsão Combinada
            <span className="text-[11px] bg-emerald/15 text-emerald px-2 py-0.5 rounded font-normal">Poisson + Pool23</span>
          </h3>
          <PalpiteCard titulo="" badge="" numeros={previsao_combinada} primosSet={primosSet} />
        </div>
      )}
    </div>
  );
}
