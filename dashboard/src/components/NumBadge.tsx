'use client';

export default function NumBadge({ n, className }: { n: number; className?: string }) {
  return (
    <span
      className={`w-9 h-9 flex items-center justify-center rounded-lg text-xs font-semibold bg-accent/10 text-accent-2 transition-all duration-200 hover:scale-110 hover:brightness-125 ${className || ''}`}
    >
      {n}
    </span>
  );
}
