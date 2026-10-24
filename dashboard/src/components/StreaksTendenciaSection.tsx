'use client';

import type { StreaksTendencia, CategoriaComparativo } from '@/types';

const CAT_META: Record<CategoriaComparativo, { label: string; cor: string; bg: string }> = {
  maiores: { label: '▲ Maiores', cor: '#34d399', bg: 'rgba(52,211,153,0.12)' },
  menores: { label: '▼ Menores', cor: '#ef4444', bg: 'rgba(239,68,68,0.10)' },
  iguais: { label: '= Iguais', cor: '#818cf8', bg: 'rgba(129,140,248,0.12)' },
};

function nivelAlerta(media: number, atual: number): { texto: string; cor: string } {
  const razao = media > 0 ? atual / media : 0;
  if (atual === 0) return { texto: 'zerou agora', cor: '#fca5a5' };
  if (razao >= 3) return { texto: 'muito acima do normal', cor: '#fca5a5' };
  if (razao >= 2) return { texto: 'acima do normal', cor: '#fbbf24' };
  if (razao >= 1.5) return { texto: 'levemente acima', cor: '#fbbf24' };
  return { texto: 'dentro do normal', cor: '#6ee7b7' };
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-lg bg-white/4 border border-white/6 px-2.5 py-2">
      <div className="text-[10px] text-muted uppercase tracking-wide">{label}</div>
      <div className="text-base font-bold text-fg mt-0.5">{value}</div>
      {sub && <div className="text-[10px] text-muted mt-0.5">{sub}</div>}
    </div>
  );
}

export default function StreaksTendenciaSection({ data }: { data?: StreaksTendencia }) {
  if (!data) return null;

  const categorias = (['maiores', 'menores', 'iguais'] as CategoriaComparativo[]).filter(k => data[k]);

  return (
    <div className="rounded-2xl border border-[rgba(129,140,248,0.15)] p-5 sm:p-6 mb-6 animate-slide-up"
      style={{ background: 'linear-gradient(135deg, rgba(129,140,248,0.05), rgba(52,211,153,0.02))' }}>
      <h3 className="text-lg font-semibold text-ink mb-1">Streaks do Tendência Posicional</h3>
      <p className="text-xs text-muted mb-4">
        Sequência de concursos sem zerar cada categoria (▲/▼/=/ vs. concurso anterior), no histórico completo.
        Ajuda a estimar quando a probabilidade de zerar se aproxima.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {categorias.map(k => {
          const s = data[k];
          const meta = CAT_META[k];
          const alerta = nivelAlerta(s.media_len, s.streak_atual_len);
          const pctStreak = s.max_streak > 0 ? Math.round(s.streak_atual_len / s.max_streak * 100) : 0;
          return (
            <div key={k} className="rounded-xl border p-4" style={{ borderColor: `${meta.cor}30`, background: meta.bg }}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold" style={{ color: meta.cor }}>{meta.label}</span>
                <span className="text-[11px] text-muted">
                  zera em <strong className="text-fg">{s.pct_zeros}%</strong> dos concursos
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-3">
                <Stat label="Streak atual" value={String(s.streak_atual_len)} sub={s.streak_atual_inicio ? `desde #${s.streak_atual_inicio}` : 'zerado no último'} />
                <Stat label="Média" value={s.media_len.toFixed(1)} sub={`mediana ${s.mediana_len}`} />
                <Stat label="Máx. histórico" value={String(s.max_streak)} sub={`soma ${s.max_soma}`} />
                <Stat label="Streaks" value={String(s.streaks)} sub={`${s.zeros} zeros`} />
              </div>

              <div className="mb-2">
                <div className="flex items-center justify-between text-[11px] mb-1">
                  <span className="text-muted">Streak atual vs. máximo</span>
                  <span className="font-mono text-muted">{s.streak_atual_len}/{s.max_streak}</span>
                </div>
                <div className="h-2 rounded-full bg-white/6 overflow-hidden">
                  <div className="h-full rounded-full transition-all"
                    style={{ width: `${Math.min(100, pctStreak)}%`, background: meta.cor, opacity: 0.8 }} />
                </div>
              </div>

              <div className="text-[11px] mb-3" style={{ color: alerta.cor }}>
                {s.streak_atual_len === 0
                  ? `● zerou no último concurso — recomeçou o ciclo`
                  : `● streak atual ${alerta.texto} (média ${s.media_len.toFixed(1)})`}
              </div>

              {s.ultimos_zeros.length > 0 && (
                <div className="text-[10px] text-muted">
                  últimos zeros: <span className="font-mono text-fg/80">{s.ultimos_zeros.join(', ')}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <p className="text-[11px] text-muted mt-4 leading-relaxed">
        Interpretação: ▲ e ▼ zeram com frequência (streaks curtos, média ~4–6 concursos); = é mais estável (média ~12).
        Quando o streak atual passa de ~2× a média, a chance de zerar cresce significativamente.
      </p>
    </div>
  );
}