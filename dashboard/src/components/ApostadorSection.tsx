'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { getLotteryConfig, LOTERIAS, LOTTERY_IDS, calcularPrecoAposta } from '@/lib/lottery-config';

interface JogoValidado {
  id: number;
  numeros: number[];
}

interface JogoInvalido {
  id: number;
  numeros: number[];
  mensagem: string;
}

interface ParseResult {
  success: boolean;
  loteria: string;
  nome_jogo?: string;
  total_jogos: number;
  validos: JogoValidado[];
  invalids: JogoInvalido[];
  preco_unitario?: number;
  custo_total?: number;
  error?: string;
}

interface ApostadorSectionProps {
  loteria?: string;
}

export default function ApostadorSection({ loteria = 'lotofacil' }: ApostadorSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loteriaSelecionada, setLoteriaSelecionada] = useState<string>(loteria);
  const [quantidade, setQuantidade] = useState<number>(0);
  const [arquivoNome, setArquivoNome] = useState<string>('');
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [parseando, setParseando] = useState(false);
  const [apostando, setApostando] = useState(false);
  const [progresso, setProgresso] = useState<{ jogo: number; total: number; status: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [janelaVisivel, setJanelaVisivel] = useState(true);
  const [modoAttach, setModoAttach] = useState(false);
  const [debugPort, setDebugPort] = useState<number>(9222);

  useEffect(() => {
    setLoteriaSelecionada(loteria);
    setParseResult(null);
    setProgresso([]);
    setError(null);
    setInfo(null);
  }, [loteria]);

  const cfg = getLotteryConfig(loteriaSelecionada);

  const handleArquivoChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setArquivo(f);
    setArquivoNome(f.name);
    setParseResult(null);
    setProgresso([]);
    setError(null);
    setInfo(null);
  }, []);

  const parseArquivo = useCallback(async () => {
    if (!arquivo) {
      setError('Selecione um arquivo com os jogos.');
      return;
    }
    setParseando(true);
    setError(null);
    setInfo(null);
    try {
      const form = new FormData();
      form.append('arquivo', arquivo);
      form.append('loteria', loteriaSelecionada);
      const res = await fetch('/api/apostador/parse', { method: 'POST', body: form });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Erro ao processar arquivo');
      setParseResult(data);
      const validos = (data.validos ?? []) as JogoValidado[];
      if (quantidade > 0 && validos.length > quantidade) {
        setInfo(`Arquivo tem ${validos.length} jogos válidos; serão apostados os ${quantidade} primeiros.`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar arquivo');
    } finally {
      setParseando(false);
    }
  }, [arquivo, loteriaSelecionada, quantidade]);

  const realizarApostas = useCallback(async () => {
    if (!arquivo) {
      setError('Selecione um arquivo com os jogos.');
      return;
    }
    setApostando(true);
    setError(null);
    setInfo(null);
    setProgresso([]);
    try {
      const form = new FormData();
      form.append('arquivo', arquivo);
      form.append('loteria', loteriaSelecionada);
      if (modoAttach) {
        form.append('attach', 'true');
        form.append('debug_port', String(debugPort));
      } else {
        form.append('headless', janelaVisivel ? 'false' : 'true');
      }
      const res = await fetch('/api/apostador/bet', { method: 'POST', body: form });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Erro ao iniciar apostas');
      setProgresso([]);
      setInfo(data.mensagem || 'Automação iniciada. O navegador abrirá e permanecerá aberto — faça login e finalize a compra.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao iniciar apostas');
    } finally {
      setApostando(false);
    }
  }, [arquivo, loteriaSelecionada, modoAttach, debugPort, janelaVisivel]);

  const quantidadeUsada = quantidade > 0 && parseResult ? Math.min(quantidade, (parseResult.validos ?? []).length) : (parseResult?.validos ?? []).length;
  const precoUnit = parseResult?.preco_unitario ?? calcularPrecoAposta(loteriaSelecionada, cfg.numeros_por_jogo);
  const custoTotal = parseResult ? precoUnit * quantidadeUsada : 0;
  const jogosExibidos = parseResult ? (parseResult.validos ?? []).slice(0, quantidade > 0 ? quantidade : undefined) : [];

  return (
    <div className="rounded-2xl border border-[rgba(129,140,248,0.15)] p-5 sm:p-6 mb-6"
      style={{ background: 'linear-gradient(135deg, rgba(129,140,248,0.06), rgba(250,204,21,0.04))' }}>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div>
          <h3 className="text-lg font-semibold text-[#e0e7ff]">Apostador Automático</h3>
          <p className="text-xs text-muted mt-1">
            Suba um arquivo com jogos, escolha a loteria e o número de apostas. O sistema preenche os
            volantes no Portal Loterias CAIXA e <strong>para antes do pagamento</strong> — a conferência e
            a compra ficam por sua conta.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <label className="text-sm text-muted">Loteria:</label>
        <select
          value={loteriaSelecionada}
          onChange={e => { setLoteriaSelecionada(e.target.value); setParseResult(null); setProgresso([]); }}
          className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
        >
          {LOTTERY_IDS.map(id => (
            <option key={id} value={id} className="bg-[#1a1d2e]">
              {LOTERIAS[id]?.nome_jogo ?? id}
            </option>
          ))}
        </select>

        <label className="text-sm text-muted">Quantidade de jogos:</label>
        <input
          type="number"
          min={0}
          value={quantidade}
          onChange={e => setQuantidade(Math.max(0, parseInt(e.target.value, 10) || 0))}
          className="w-24 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
          placeholder="Todos"
        />
        {quantidade === 0 && (
          <span className="text-xs px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-500/30">
            Todos do arquivo
          </span>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.csv,.xlsx"
          onChange={handleArquivoChange}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110"
          style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
          {arquivoNome || 'Escolher arquivo (.txt/.csv/.xlsx)'}
        </button>

        {arquivo && !parseResult && (
          <button
            onClick={parseArquivo}
            disabled={parseando}
            className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110 disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg,#10b981,#34d399)' }}>
            {parseando ? 'Processando...' : 'Ler jogos'}
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-sm">
          {error}
        </div>
      )}
      {info && (
        <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-200 text-sm">
          {info}
        </div>
      )}

      {parseResult && (
        <div className="mb-5">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            <div className="rounded-xl bg-white/5 p-3 text-center">
              <div className="text-xs text-muted">Jogos válidos</div>
              <div className="text-lg font-bold text-fg">{(parseResult.validos ?? []).length}</div>
            </div>
            <div className="rounded-xl bg-white/5 p-3 text-center">
              <div className="text-xs text-muted">Inválidos</div>
              <div className="text-lg font-bold text-hot">{(parseResult.invalids ?? []).length}</div>
            </div>
            <div className="rounded-xl bg-white/5 p-3 text-center">
              <div className="text-xs text-muted">Preço/jogo</div>
              <div className="text-lg font-bold text-fg">R$ {precoUnit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</div>
            </div>
            <div className="rounded-xl bg-white/5 p-3 text-center">
              <div className="text-xs text-muted">Custo total</div>
              <div className="text-lg font-bold text-fg">R$ {custoTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</div>
            </div>
          </div>

          {jogosExibidos.length > 0 && (
            <div className="space-y-2 mb-4 max-h-72 overflow-y-auto pr-1">
              {jogosExibidos.map(jogo => (
                <div key={jogo.id} className="rounded-lg bg-white/5 border border-white/10 p-2.5">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-xs font-semibold text-[#e0e7ff]">Jogo {jogo.id}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {jogo.numeros.map(n => (
                      <span key={n}
                        className="w-7 h-7 flex items-center justify-center rounded-md text-xs font-bold border bg-[rgba(129,140,248,0.12)] text-accent-2 border-[rgba(129,140,248,0.25)]">
                        {n}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {(parseResult.invalids ?? []).length > 0 && (
            <div className="mb-4 p-3 rounded-lg bg-hot/10 border border-hot/20 text-hot text-xs">
              <strong>{parseResult.invalids.length} jogo(s) inválido(s) ignorado(s):</strong>
              <ul className="mt-1 list-disc list-inside">
                {parseResult.invalids.slice(0, 10).map(inv => (
                  <li key={inv.id}>Jogo {inv.id}: {inv.mensagem}</li>
                ))}
              </ul>
            </div>
          )}

          {quantidadeUsada > 0 && (
            <>
              <label className="flex items-center gap-2 text-xs text-muted mb-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={modoAttach}
                  onChange={e => setModoAttach(e.target.checked)}
                  className="accent-[#818cf8]"
                />
                Anexar ao navegador JÁ aberto e logado (CDP) — não abre janela nova, não fecha o seu Chrome
              </label>
              {modoAttach ? (
                <label className="flex items-center gap-2 text-xs text-muted mb-2">
                  Porta de debug do Chrome:
                  <input
                    type="number"
                    value={debugPort}
                    onChange={e => setDebugPort(parseInt(e.target.value, 10) || 9222)}
                    className="w-24 px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-sm text-fg focus:outline-none focus:border-[#818cf8]"
                  />
                </label>
              ) : (
                <label className="flex items-center gap-2 text-xs text-muted mb-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={janelaVisivel}
                    onChange={e => setJanelaVisivel(e.target.checked)}
                    className="accent-[#818cf8]"
                  />
                  Janela visível do navegador (necessária: o anti-bot da Caixa bloqueia headless). Faça login na 1ª vez — a sessão fica salva para as próximas.
                </label>
              )}
              <button
                onClick={realizarApostas}
                disabled={apostando}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition-all hover:brightness-110 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg,#f59e0b,#fbbf24)' }}>
                {apostando ? 'Iniciando automação...' : `Preencher ${quantidadeUsada} aposta(s) no navegador (R$ ${custoTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} no carrinho)`}
              </button>
            </>
          )}
        </div>
      )}

      {progresso.length > 0 && (
        <div className="mb-4 p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="text-sm font-semibold text-[#e0e7ff] mb-3">Progresso</div>
          <div className="space-y-1.5">
            {progresso.map(p => (
              <div key={p.jogo} className="flex items-center gap-2 text-xs">
                <span className="w-6 h-6 flex items-center justify-center rounded-full bg-emerald-500/20 text-emerald-200 border border-emerald-500/40">
                  ✓
                </span>
                <span className="text-fg">Jogo {p.jogo}/{p.total}</span>
                <span className="text-muted">— {p.status}</span>
              </div>
            ))}
          </div>
          <div className="mt-3 text-xs text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2">
            Volantes preenchidos no carrinho da Caixa. <strong>Finalize a compra no site</strong> antes do encerramento das apostas.
          </div>
        </div>
      )}

      {!parseResult && !apostando && (
        <div className="text-center py-6 text-muted text-sm">
          Selecione um arquivo e clique em <strong>Ler jogos</strong> para ver o preview.
        </div>
      )}
    </div>
  );
}