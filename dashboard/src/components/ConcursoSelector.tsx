'use client';

import { useState, useRef, useCallback, useEffect, useMemo } from 'react';

export default function ConcursoSelector({
  concursos,
  value,
  onChange,
  totalSorteios,
}: {
  concursos: number[];
  value: number | undefined;
  onChange: (c: number | undefined) => void;
  totalSorteios: number;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [highlightIdx, setHighlightIdx] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const filtered = useMemo(() => {
    if (!query) return concursos;
    const q = query.replace(/\D/g, '');
    if (!q) return concursos;
    return concursos.filter(c => String(c).startsWith(q));
  }, [concursos, query]);

  useEffect(() => {
    setHighlightIdx(-1);
  }, [filtered.length]);

  const select = useCallback((c: number | undefined) => {
    onChange(c);
    setOpen(false);
    setQuery('');
  }, [onChange]);

  const navAnterior = useCallback(() => {
    if (value === undefined) {
      if (concursos.length > 0) select(concursos[concursos.length - 2]);
    } else {
      const idx = concursos.indexOf(value);
      if (idx > 0) select(concursos[idx - 1]);
    }
  }, [concursos, value, select]);

  const navProximo = useCallback(() => {
    if (value === undefined) return;
    const idx = concursos.indexOf(value);
    if (idx < concursos.length - 1) select(concursos[idx + 1]);
    else select(undefined);
  }, [concursos, value, select]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setOpen(false);
      inputRef.current?.blur();
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightIdx(i => Math.min(i + 1, filtered.length - 1));
      return;
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightIdx(i => Math.max(i - 1, 0));
      return;
    }
    if (e.key === 'Enter' && highlightIdx >= 0 && filtered[highlightIdx]) {
      select(filtered[highlightIdx]);
      return;
    }
    if (e.key === 'Enter' && filtered.length === 1) {
      select(filtered[0]);
      return;
    }
  }, [filtered, highlightIdx, select]);

  useEffect(() => {
    if (!open || highlightIdx < 0 || !listRef.current) return;
    const items = listRef.current.querySelectorAll<HTMLElement>('[data-idx]');
    const el = items[highlightIdx];
    if (el) el.scrollIntoView({ block: 'nearest' });
  }, [highlightIdx, open]);

  const displayText = value ? `Concurso ${value}` : `Último (${totalSorteios} sorteios)`;

  return (
    <div className="flex items-center gap-1.5">
      <button
        onClick={navAnterior}
        disabled={value === undefined && concursos.length <= 1}
        className="w-7 h-7 flex items-center justify-center rounded-lg bg-white/10 text-muted hover:text-fg hover:bg-white/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed text-sm"
        title="Concurso anterior"
      >
        −
      </button>

      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={open ? query : displayText}
          onFocus={() => { setOpen(true); setQuery(''); }}
          onBlur={() => setTimeout(() => setOpen(false), 200)}
          onChange={e => { setQuery(e.target.value); setOpen(true); }}
          onKeyDown={handleKeyDown}
          placeholder="Digite o concurso..."
          className="w-44 px-3 py-1.5 rounded-lg text-sm text-[#e0e7ff] bg-white/5 border border-white/10 focus:border-accent-2/50 focus:outline-none focus:ring-1 focus:ring-accent-2/30"
        />
        {open && (
          <div
            ref={listRef}
            className="absolute top-full left-0 right-0 mt-1 max-h-60 overflow-y-auto rounded-lg border border-white/10 bg-[#1a1a2e] shadow-xl z-50"
          >
            <button
              onMouseDown={() => select(undefined)}
              className={`w-full text-left px-3 py-2 text-xs transition-colors ${value === undefined ? 'bg-accent/20 text-accent-2' : 'text-muted hover:bg-white/5'}`}
            >
              Último concurso ({totalSorteios} sorteios)
            </button>
            {filtered.length === 0 && (
              <div className="px-3 py-2 text-xs text-muted">Nenhum concurso encontrado</div>
            )}
            {filtered.map((c, i) => (
              <button
                key={c}
                data-idx={i}
                onMouseDown={() => select(c)}
                onMouseEnter={() => setHighlightIdx(i)}
                className={`w-full text-left px-3 py-2 text-xs transition-colors ${
                  highlightIdx === i ? 'bg-accent/15 text-accent-2' : ''
                } ${value === c ? 'bg-accent/20 text-accent-2 font-semibold' : 'text-fg hover:bg-white/5'}`}
              >
                Concurso {c.toLocaleString()}
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={navProximo}
        disabled={value === undefined}
        className="w-7 h-7 flex items-center justify-center rounded-lg bg-white/10 text-muted hover:text-fg hover:bg-white/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed text-sm"
        title="Próximo concurso"
      >
        +
      </button>

      {value && (
        <button
          onClick={() => onChange(undefined)}
          className="text-xs px-2 py-1.5 rounded-lg bg-white/10 text-muted hover:text-fg transition-colors"
          title="Voltar ao concurso atual"
        >
          ✕
        </button>
      )}
    </div>
  );
}
