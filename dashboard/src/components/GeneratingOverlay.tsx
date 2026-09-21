'use client';

export default function GeneratingOverlay({ show, progress }: { show: boolean; progress: number }) {
  if (!show) return null;

  const pct = Math.max(0, Math.min(100, Math.round(progress)));
  const etapa = pct < 25
    ? 'Analisando histórico e estratégias...'
    : pct < 50
      ? 'Gerando combinações...'
      : pct < 85
        ? 'Aplicando filtros posicionais...'
        : 'Finalizando...';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="w-80 rounded-2xl border border-white/10 bg-[#12162a] p-6 shadow-2xl">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 flex items-center justify-center">
            <div className="w-8 h-8 rounded-full border-2 border-[rgba(129,140,248,0.15)] border-t-[#818cf8] animate-spin" />
          </div>
          <div>
            <div className="text-sm font-semibold text-[#e0e7ff]">Gerando combinações</div>
            <div className="text-[11px] text-muted">{etapa}</div>
          </div>
        </div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-muted">Progresso</span>
          <span className="text-sm font-bold text-accent-2">{pct}%</span>
        </div>
        <div className="h-2.5 rounded-full bg-white/5 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-200 ease-out"
            style={{ width: `${pct}%`, background: 'linear-gradient(90deg,#6366f1,#34d399)' }}
          />
        </div>
        <div className="text-[10px] text-muted mt-3">Isso pode levar alguns segundos — não feche a janela.</div>
      </div>
    </div>
  );
}