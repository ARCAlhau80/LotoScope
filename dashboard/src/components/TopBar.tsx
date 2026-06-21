'use client';

import { LOTERIAS, LOTTERY_IDS } from '@/lib/lottery-config';

interface TopBarProps {
  loteria: string;
  onLoteriaChange: (id: string) => void;
}

function LotteryTab({ id, active, onClick }: { id: string; active: boolean; onClick: () => void }) {
  const cfg = LOTERIAS[id];
  return (
    <button
      onClick={onClick}
      className={`relative flex flex-col items-center px-4 sm:px-5 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 whitespace-nowrap ${
        active
          ? 'text-white shadow-lg shadow-[rgba(129,140,248,0.15)]'
          : 'text-muted hover:text-[#c4c9e8] hover:bg-white/[0.04]'
      }`}
      style={active ? { background: 'linear-gradient(135deg, rgba(129,140,248,0.18), rgba(167,139,250,0.1))', border: '1px solid rgba(129,140,248,0.2)' } : { border: '1px solid transparent' }}
    >
      <span className="text-[13px] font-semibold tracking-tight">{cfg.nome_jogo}</span>
      <span className="text-[9px] opacity-50 mt-0.5 font-mono">{cfg.total_numeros} números · {cfg.numeros_por_jogo}/jogo</span>
      {active && (
        <span className="absolute -bottom-[7px] left-1/2 -translate-x-1/2 w-6 h-[3px] rounded-full bg-[#818cf8] shadow-sm shadow-[#818cf8]" />
      )}
    </button>
  );
}

export default function TopBar({ loteria, onLoteriaChange }: TopBarProps) {
  return (
    <>
      <div className="w-full text-center py-2 px-4 text-[12px] leading-tight font-medium tracking-wide"
        style={{ background: 'linear-gradient(135deg, rgba(239,68,68,0.12), rgba(251,146,60,0.08))', borderBottom: '1px solid rgba(239,68,68,0.2)' }}>
        <span style={{ color: '#fca5a5' }}>⚠ Não incentivamos apostas</span>
        <span className="mx-2" style={{ color: 'rgba(148,163,184,0.4)' }}>·</span>
        <span className="text-muted">Conteúdo informativo e de entretenimento</span>
        <span className="mx-2" style={{ color: 'rgba(148,163,184,0.4)' }}>·</span>
        <span className="text-muted">Jogue com moderação</span>
        <span className="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-bold" style={{ background: 'rgba(239,68,68,0.2)', color: '#fca5a5' }}>+18</span>
      </div>
      <header
        className="sticky top-0 z-30 flex items-center gap-4 sm:gap-8 px-3 sm:px-8 py-2.5 border-b border-[rgba(129,140,248,0.12)] backdrop-blur-xl overflow-x-auto"
        style={{ background: 'linear-gradient(135deg,rgba(15,20,41,0.9),rgba(26,16,64,0.9))' }}
      >
        <div className="flex items-center gap-2.5 shrink-0">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#818cf8] via-[#a78bfa] to-[#34d399] flex items-center justify-center text-[#070b1a] font-extrabold text-xs shadow-md shadow-[rgba(129,140,248,0.2)]">
            LS
          </div>
          <div className="hidden sm:block">
            <h1 className="text-sm font-bold bg-gradient-to-r from-[#818cf8] via-[#a78bfa] to-[#34d399] bg-clip-text text-transparent">
              LotoScope
            </h1>
          </div>
        </div>

        <nav className="flex items-center gap-1 sm:gap-1.5 mx-auto">
          {LOTTERY_IDS.map(id => (
            <LotteryTab
              key={id}
              id={id}
              active={loteria === id}
              onClick={() => onLoteriaChange(id)}
            />
          ))}
        </nav>

        <div className="flex items-center gap-2 shrink-0">
          <span className="hidden sm:inline px-2 py-0.5 rounded-md text-[9px] font-semibold uppercase tracking-wider bg-accent/10 text-accent-2 border border-accent/20">
            Beta
          </span>
        </div>
      </header>
    </>
  );
}
