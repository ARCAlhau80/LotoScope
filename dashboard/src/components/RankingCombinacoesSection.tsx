'use client';

import { useState } from 'react';
import type { RankingCombinacaoItem } from '@/types';

interface RankingCombinacoesSectionProps {
  ranking?: RankingCombinacaoItem[];
}

const perfis = {
  altovalor: 'Alto valor (13-14)',
  equilibrado: 'Equilibrado',
  foco11: 'Foco em 11 acertos',
};

export default function RankingCombinacoesSection({ ranking: rankingInicial }: RankingCombinacoesSectionProps) {
  const [ranking, setRanking] = useState<RankingCombinacaoItem[] | undefined>(rankingInicial);
  const [perfil, setPerfil] = useState<keyof typeof perfis>('altovalor');
  const [top, setTop] = useState<number>(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function carregar() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`/api/ranking-combinacoes?perfil=${perfil}&top=${top}`);
      const data = await r.json();
      if (data.error) throw new Error(data.error);
      setRanking(data.ranking || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar ranking');
    } finally {
      setLoading(false);
    }
  }

  function exportarTxt() {
    if (!ranking || ranking.length === 0) return;
    const linhas = ranking.map(item =>
      item.numeros.map(n => n.toString().padStart(2, '0')).join(',')
    );
    const cabecalho = `# Ranking COMBINACOES_LOTOFACIL - Perfil: ${perfis[perfil]} - Top ${ranking.length}\n`;
    const conteudo = cabecalho + linhas.join('\n') + '\n';
    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ranking_lotofacil_${perfil}_${ranking.length}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  if (!ranking) return null;

  return (
    <div className="mb-8 p-5 rounded-2xl border border-[rgba(129,140,248,0.15)] bg-[rgba(129,140,248,0.03)]">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h3 className="text-lg font-semibold text-[#e0e7ff] flex items-center gap-2">
          Ranking de Combinações Históricas
          <span className="text-[11px] bg-[rgba(129,140,248,0.15)] text-[#a5b4fc] px-2 py-0.5 rounded font-normal">
            COMBINACOES_LOTOFACIL
          </span>
        </h3>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={perfil}
            onChange={e => setPerfil(e.target.value as keyof typeof perfis)}
            className="bg-[rgba(129,140,248,0.08)] border border-[rgba(129,140,248,0.2)] rounded-lg px-2 py-1 text-sm text-[#e0e7ff]"
          >
            {Object.entries(perfis).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
          <input
            type="number"
            min={1}
            max={50}
            value={top}
            onChange={e => setTop(Math.min(50, Math.max(1, Number(e.target.value))))}
            className="w-16 bg-[rgba(129,140,248,0.08)] border border-[rgba(129,140,248,0.2)] rounded-lg px-2 py-1 text-sm text-[#e0e7ff] text-center"
          />
          <button
            onClick={carregar}
            disabled={loading}
            className="px-3 py-1 rounded-lg text-xs font-medium bg-[rgba(129,140,248,0.15)] text-[#a5b4fc] hover:bg-[rgba(129,140,248,0.25)] transition-all disabled:opacity-50"
          >
            {loading ? 'Carregando...' : 'Atualizar'}
          </button>
          <button
            onClick={exportarTxt}
            disabled={!ranking || ranking.length === 0}
            className="px-3 py-1 rounded-lg text-xs font-medium bg-[rgba(52,211,153,0.15)] text-[#34d399] hover:bg-[rgba(52,211,153,0.25)] transition-all disabled:opacity-50"
          >
            Exportar .txt
          </button>
        </div>
      </div>

      {error && (
        <div className="text-sm text-[#fca5a5] bg-[rgba(248,113,113,0.1)] rounded-xl p-3 mb-3">
          {error}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted border-b border-[rgba(129,140,248,0.15)]">
              <th className="py-2 pr-2">#</th>
              <th className="py-2 pr-2">Combinação</th>
              <th className="py-2 pr-2 text-center">11</th>
              <th className="py-2 pr-2 text-center">12</th>
              <th className="py-2 pr-2 text-center">13</th>
              <th className="py-2 pr-2 text-center">14</th>
              <th className="py-2 pr-2 text-right">Atraso 14</th>
              <th className="py-2 text-right">Score</th>
            </tr>
          </thead>
          <tbody>
            {ranking.map((item, idx) => (
              <tr
                key={item.id}
                className="border-b border-[rgba(129,140,248,0.08)] hover:bg-[rgba(129,140,248,0.05)]"
              >
                <td className="py-2 pr-2 text-muted">{idx + 1}</td>
                <td className="py-2 pr-2 font-medium text-[#e0e7ff] whitespace-nowrap">
                  {item.numeros.map(n => n.toString().padStart(2, '0')).join(' ')}
                </td>
                <td className="py-2 pr-2 text-center text-[#a5b4fc]">{item.acertos_11}</td>
                <td className="py-2 pr-2 text-center text-[#818cf8]">{item.acertos_12}</td>
                <td className="py-2 pr-2 text-center text-[#6366f1]">{item.acertos_13}</td>
                <td className="py-2 pr-2 text-center text-[#4f46e5]">{item.acertos_14}</td>
                <td className="py-2 pr-2 text-right text-muted">{item.atraso_14}</td>
                <td className="py-2 text-right text-[#34d399] font-medium">{item.score.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-muted mt-3">
        Score pondera frequência de acertos e atraso nas categorias 11, 12, 13 e 14. 
        Perfil <strong>{perfis[perfil]}</strong>.
      </p>
    </div>
  );
}
