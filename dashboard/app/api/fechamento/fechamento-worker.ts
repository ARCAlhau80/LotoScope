/**
 * Web Worker para fechamento combinatório em paralelo.
 * Uso:
 *   const worker = new Worker(new URL('./fechamento-worker.ts', import.meta.url));
 *   worker.postMessage({ tipo: 'GERAR', ...parametros });
 *   worker.onmessage = (e) => { ...resultado... };
 */

// Re-exportar funções necessárias do lib (embrulhadas para worker)
import {
  gerarFechamentoComRestricoes,
  gerarFechamentoComWheel,
  verificarCobertura,
  relatorioCusto,
} from '@/lib/fechamento-combinatorio';

function parseNumero(valor: string | null, padrao: number): number {
  if (valor === null || valor === undefined || valor === "") return padrao;
  const n = parseInt(valor, 10);
  return Number.isNaN(n) ? padrao : n;
}

function montarResposta(opts: any, apostas: number[][], cobertura: any, custo: any, modo: string, wheelUsado: boolean) {
  const universoEfetivo = opts.universo ?? Array.from({ length: 25 }, (_, i) => i + 1);
  return {
    sucesso: true,
    universo: universoEfetivo,
    fixos: opts.fixos,
    excluidos: opts.excluidos,
    k: opts.k,
    t: opts.t,
    modo,
    wheelUsado,
    totalApostas: apostas.length,
    apostas,
    cobertura,
    custo,
  };
}

self.onmessage = async (e: MessageEvent<any>) => {
  const { tipo, ...parametros } = e.data;

  try {
    if (tipo === 'GERAR_FECHAMENTO') {
      const {
        universo, fixos, excluidos, k, t, maxApostas, seed, otimizado,
        maxIteracoes, buscaSeed, candidatosPool, amostraPorPasso, usarWheel,
        removerRedundantes, limiteTempoMs,
      } = parametros;

      const universoEfetivo = universo ?? Array.from({ length: 25 }, (_, i) => i + 1);

      let apostas: number[][] = [];
      let modo = '';
      let wheelUsado = false;

      if (usarWheel && !fixos.length && !excluidos.length) {
        const wheelResult = gerarFechamentoComWheel(universoEfetivo.length, k, t, maxApostas, seed);
        apostas = wheelResult.apostas;
        modo = wheelResult.modo;
        wheelUsado = wheelResult.wheelUsado;
      }

      if (!apostas.length) {
        const gerados = gerarFechamentoComRestricoes({
          universo: universoEfetivo,
          fixos,
          excluidos,
          filtrosCategorias: [],
          k, t, maxApostas, seed, otimizado, maxIteracoes, buscaSeed, candidatosPool, amostraPorPasso,
          removerRedundantes: Boolean(removerRedundantes),
          limiteTempoMs: Number(limiteTempoMs) || 0,
        });
        apostas = gerados;
        modo = otimizado ? 'guloso_amostrado + busca_local' : 'guloso_amostrado';
      }

      const cobertura = verificarCobertura(apostas, universoEfetivo, k, t);
      const custo = relatorioCusto(apostas, k);

      self.postMessage({
        id: parametros.id,
        tipo: 'RESULTADO',
        ...montarResposta({ universo: universoEfetivo, fixos, excluidos, k, t, maxApostas, seed, otimizado }, apostas, cobertura, custo, modo, wheelUsado),
      });
    } else {
      self.postMessage({ id: parametros.id, tipo: 'ERRO', erro: `Tipo desconhecido: ${tipo}` });
    }
  } catch (error: any) {
    self.postMessage({ id: parametros.id, tipo: 'ERRO', erro: error?.message || 'Erro no worker' });
  }
};

// Marcar como worker para bundlers
export {};
