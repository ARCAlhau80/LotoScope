'use client';

import { useDrawnNumbers } from '@/lib/DrawnNumbersContext';

export type NumState = 'neutral' | 'fixed' | 'excluded';

const ESTADO_LABEL: Record<Exclude<NumState, 'neutral'>, string> = {
  fixed: 'fixada',
  excluded: 'excluída',
};

export default function NumBadge({ n, className, state, onClick, isDrawn }: {
  n: number;
  className?: string;
  state?: NumState;
  onClick?: (n: number) => void;
  isDrawn?: boolean;
}) {
  const drawnSet = useDrawnNumbers();
  const drawn = isDrawn ?? (drawnSet?.has(n) ?? false);

  const stateClass = state === 'fixed'
    ? 'bg-emerald/30 text-emerald border-emerald/50 ring-1 ring-emerald/40 scale-110'
    : state === 'excluded'
    ? 'bg-hot/25 text-hot border-hot/40 ring-1 ring-hot/30 line-through decoration-2'
    : '';

  const drawnClass = drawn ? 'text-emerald' : '';

  const base = `w-10 h-10 flex items-center justify-center rounded-lg text-sm font-semibold bg-accent/10 text-accent-2 transition-all duration-200 select-none ${className || ''} ${stateClass} ${drawnClass}`;

  if (onClick) {
    return (
      <button
        type="button"
        onClick={() => onClick(n)}
        aria-pressed={state === 'fixed'}
        aria-label={`Dezena ${n}${state && state !== 'neutral' ? `, ${ESTADO_LABEL[state]}` : ''}`}
        className={`${base} cursor-pointer hover:scale-110 hover:brightness-125 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-2`}
      >
        {n}
      </button>
    );
  }

  return <span className={base}>{n}</span>;
}
