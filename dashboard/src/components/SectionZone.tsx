'use client';

import { useEffect, useState } from 'react';

export interface ZoneDef {
  id: string;
  label: string;
}

export const ZONES: ZoneDef[] = [
  { id: 'zona-analise', label: 'Análise' },
  { id: 'zona-geracao', label: 'Previsão & Geração' },
  { id: 'zona-conferencia', label: 'Conferência' },
  { id: 'zona-automacao', label: 'Automação' },
];

export function ZoneNav() {
  const [active, setActive] = useState<string>(ZONES[0].id);

  useEffect(() => {
    const els = ZONES
      .map(z => document.getElementById(z.id))
      .filter((el): el is HTMLElement => el !== null);
    if (!els.length) return;

    const obs = new IntersectionObserver(
      entries => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: '-120px 0px -60% 0px', threshold: 0 }
    );
    els.forEach(el => obs.observe(el));
    return () => obs.disconnect();
  }, []);

  const go = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <nav
      aria-label="Navegação de seções"
      className="sticky top-[52px] z-20 -mx-4 sm:-mx-5 px-4 sm:px-5 py-2 mb-5 backdrop-blur-xl border-b border-[rgba(129,140,248,0.12)]"
      style={{ background: 'rgba(7,11,26,0.85)' }}
    >
      <ul className="flex items-center gap-1.5 overflow-x-auto">
        {ZONES.map(z => (
          <li key={z.id}>
            <button
              type="button"
              onClick={() => go(z.id)}
              aria-current={active === z.id ? 'true' : undefined}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors border ${
                active === z.id
                  ? 'bg-accent/15 text-accent-2 border-accent/20'
                  : 'text-muted border-transparent hover:text-fg hover:bg-white/[0.04]'
              }`}
            >
              {z.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export function Zone({ id, label, description, children }: {
  id: string;
  label: string;
  description?: string;
  children: React.ReactNode;
}) {
  const storageKey = `lotoscope:zone:${id}`;
  const [open, setOpen] = useState(true);

  useEffect(() => {
    try {
      if (localStorage.getItem(storageKey) === '0') setOpen(false);
    } catch { /* localStorage indisponível */ }
  }, [storageKey]);

  const toggle = () => {
    setOpen(prev => {
      const next = !prev;
      try { localStorage.setItem(storageKey, next ? '1' : '0'); } catch { /* noop */ }
      return next;
    });
  };

  return (
    <section id={id} aria-labelledby={`${id}-title`} className="mb-8 scroll-mt-[120px]">
      <div className="flex items-center justify-between gap-3 mb-4 pb-2 border-b border-white/6">
        <div>
          <h2 id={`${id}-title`} className="text-xl font-bold text-ink">{label}</h2>
          {description && <p className="text-xs text-muted mt-0.5">{description}</p>}
        </div>
        <button
          type="button"
          onClick={toggle}
          aria-expanded={open}
          aria-controls={`${id}-content`}
          className="shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium text-muted border border-white/8 hover:text-fg hover:bg-white/[0.04] transition-colors"
        >
          {open ? 'Recolher' : 'Expandir'}
        </button>
      </div>
      <div id={`${id}-content`} hidden={!open}>
        {children}
      </div>
    </section>
  );
}
