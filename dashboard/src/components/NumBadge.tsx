'use client';

import { useDrawnNumbers } from '@/lib/DrawnNumbersContext';

export type NumState = 'neutral' | 'fixed' | 'excluded';

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
    ? 'bg-emerald/30 text-emerald border-emerald/50 ring-1 ring-emerald/40 cursor-pointer scale-110'
    : state === 'excluded'
    ? 'bg-hot/25 text-hot border-hot/40 ring-1 ring-hot/30 cursor-pointer line-through decoration-2'
    : '';

  const drawnClass = drawn
    ? 'text-emerald'
    : '';

  return (
    <span
      onClick={() => onClick?.(n)}
      className={`w-9 h-9 flex items-center justify-center rounded-lg text-xs font-semibold bg-accent/10 text-accent-2 transition-all duration-200 hover:scale-110 hover:brightness-125 select-none ${className || ''} ${stateClass} ${drawnClass} ${onClick ? 'cursor-pointer' : ''}`}
    >
      {n}
    </span>
  );
}
