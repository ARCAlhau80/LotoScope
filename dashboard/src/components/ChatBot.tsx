'use client';

import { useState, useRef, useEffect } from 'react';
import { LOTERIAS } from '@/lib/lottery-config';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5 px-1">
      {[0, 1, 2].map(i => (
        <span key={i}
          className="w-1.5 h-1.5 rounded-full bg-muted animate-typing-dot"
          style={{ animationDelay: `${i * 0.2}s` }}
        />
      ))}
    </div>
  );
}

export default function ChatBot({ janela = 30, loteria = 'lotofacil', concurso }: { janela?: number; loteria?: string; concurso?: number }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open && inputRef.current) inputRef.current.focus();
  }, [open]);

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    setError(null);

    const userMsg: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: messages, janela, loteria, concurso }),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.error || 'Erro ao responder');
        setLoading(false);
        return;
      }

      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);

      if (data.rawContent) {
        const blob = new Blob([data.rawContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename || 'combinacoes.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch {
      setError('Erro de conexão');
    }
    setLoading(false);
  }

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-[0_0_30px_rgba(129,140,248,0.3)] active:scale-95"
        style={{ background: 'linear-gradient(135deg,#818cf8,#a78bfa)' }}
        title="Assistente LotoScope"
      >
        <svg className="w-6 h-6 text-white transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"
          style={{ transform: open ? 'rotate(90deg)' : 'rotate(0deg)' }}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d={open ? 'M6 18L18 6M6 6l12 12' : 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z'} />
        </svg>
      </button>

      {open && (
        <div
          className="fixed bottom-24 right-6 z-40 w-80 sm:w-96 rounded-2xl border border-[rgba(129,140,248,0.15)] shadow-2xl animate-slide-up origin-bottom-right"
          style={{ background: 'linear-gradient(135deg,#0f1429,#1a1040)', maxHeight: '520px' }}
        >
          <div className="px-4 py-3 border-b border-[rgba(129,140,248,0.1)] flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-[#e0e7ff]">Assistente LotoScope</h3>
              <p className="text-[10px] text-muted">Especialista em {LOTERIAS[loteria]?.nome_jogo || 'Lotofácil'}</p>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald animate-pulse" title="Online" />
          </div>

          <div ref={listRef} className="overflow-y-auto px-4 py-3 space-y-3" style={{ maxHeight: '320px' }}>
            {messages.length === 0 && (
              <p className="text-xs text-muted text-center py-6 animate-fade-in">
                Pergunte sobre análises, números, estatísticas da {LOTERIAS[loteria]?.nome_jogo || 'Lotofácil'}.
              </p>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                <div className={`max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-[#818cf8]/20 text-[#e0e7ff]'
                    : 'bg-white/5 text-[#c4c9e8]'
                }`}
                  dangerouslySetInnerHTML={{
                    __html: m.content
                      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-[#818cf8] underline hover:brightness-110">$1</a>')
                      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                  }}
                />
              </div>
            ))}
            {loading && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-white/5 rounded-xl px-3 py-2">
                  <TypingDots />
                </div>
              </div>
            )}
            {error && (
              <p className="text-xs text-center text-hot animate-fade-in">{error}</p>
            )}
          </div>

          <div className="px-4 py-3 border-t border-[rgba(129,140,248,0.1)]">
            <form onSubmit={e => { e.preventDefault(); send(); }} className="flex gap-2">
              <input
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Faça uma pergunta..."
                maxLength={2000}
                className="flex-1 bg-white/5 rounded-lg px-3 py-2 text-xs text-white placeholder-muted border border-white/6 outline-none transition-all duration-200 focus:border-accent-2/40 focus:bg-white/[0.07]"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-3 py-2 rounded-lg text-xs font-semibold text-white transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 active:scale-95"
                style={{ background: 'linear-gradient(135deg,#818cf8,#a78bfa)' }}
              >
                Enviar
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
