#!/usr/bin/env node
// -*- coding: utf-8 -*-
/*
 * MONITOR DE JANELA DE EV POSITIVO — Lotofácil
 *
 * Lê o estado atual da Lotofácil na API pública da Caixa e calcula o
 * valor esperado de uma aposta simples (15 números, R$ 3,50) dado o
 * prêmio acumulado/estimado do 15 pontos.
 *
 * EV = P(11)*R$7 + P(12)*R$14 + P(13)*R$35 + P(14)*prêmio14 + P(15)*J
 *
 * Jogar tem EV > 0 quando o prêmio estimado do 15 pontos (J) supera o
 * break-even. Com o preço atual R$3,50 e os prêmios fixos vigentes,
 * o break-even fica em torno de R$ 8,1 milhões.
 *
 * Também calcula o break-even da LOTOFÁCIL DA INDEPENDÊNCIA (regras
 * específicas do comunicado Caixa 2026): prêmios fixos diferenciados
 * (11→R$3,50 · 12→R$7,00 · 13→R$17,50), 87% p/ 15 acertos e 13% p/ 14,
 * e um modelo com RATEIO (EV por aposta ≈ pool/tickets vendidos), pois
 * o prêmio especial é dividido entre muitos ganhadores.
 *
 * Uso:
 *   node monitor_ev_jackpot.cjs [--json]
 *   node monitor_ev_jackpot.cjs --watch 60        (re-checa a cada 60s)
 *   Opções p/ Independência:
 *     --ind-arrecadacao R$   arrecadação estimada (default 600M)
 *     --ind-tickets N        nº de apostas vendidas (default arrec./3,50)
 *     --ind-pool15 R$        pool estimado p/ 15 pts (default 300M)
 *     --ind-premio14 R$      prêmio 14 usado no EV indiviso (default 2000)
 */
'use strict';

const API_BASE = 'https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil';

// Probabilidades exatas de acertar k pontos em 15-de-25 (C(25,15)=3.268.760)
const COMB = (n, k) => {
  if (k < 0 || k > n) return 0;
  let r = 1;
  for (let i = 1; i <= k; i++) r = (r * (n - k + i)) / i;
  return Math.round(r);
};
const TOTAL_COMB = COMB(25, 15);
const P = (k) => COMB(15, k) * COMB(10, 15 - k) / TOTAL_COMB;

// Valores oficiais vigentes (reajuste jul/2025) — confirmados na API da Caixa
const PRECO = 3.5;
const PRECO_FIXO = { 11: 7, 12: 14, 13: 35 };   // fixos
const PERCENT_14 = 0.13;                        // 13% do saldo pós-fixos
const PERCENT_15 = 0.62;                        // 62% do saldo pós-fixos (regular)

// Lotofácil da Independência — regras específicas (comunicado Caixa 2026)
const PRECO_FIXO_IND = { 11: 3.5, 12: 7, 13: 17.5 };  // fixos diferenciados
const PERCENT_14_IND = 0.13;                           // 13% do saldo pós-fixos
const PERCENT_15_IND = 0.87;                           // 87% do saldo pós-fixos

function brl(v) {
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function evFixoSemJackpot(premio14) {
  let ev = 0;
  for (const [k, v] of Object.entries(PRECO_FIXO)) ev += P(Number(k)) * v;
  ev += P(14) * (premio14 ?? 2400);
  return ev;
}

function breakEven(premio14) {
  return (PRECO - evFixoSemJackpot(premio14)) / P(15);
}

// ---- Lotofácil da Independência -----------------------------------------
function evFixoSemJackpotInd(premio14) {
  let ev = 0;
  for (const [k, v] of Object.entries(PRECO_FIXO_IND)) ev += P(Number(k)) * v;
  ev += P(14) * (premio14 ?? 2000);
  return ev;
}

// Break-even indiviso: quanto o prêmio do 15 pts precisaria ser (se fosse
// entregue a um único ganhador) para o EV cobrir o custo da aposta.
function breakEvenInd(premio14) {
  return (PRECO - evFixoSemJackpotInd(premio14)) / P(15);
}

// Modelo com rateio: quando o prêmio é dividido entre N ganhadores, o EV
// esperado por aposta na faixa 15 ≈ pool15 / tickets, independente de P(15)
// (pois E[ganhadores] = tickets * P(15) cancela P(15)). Mesma lógica p/ faixa 14.
function calcularIndependencia(d, opts) {
  const premio14 = opts.premio14 ?? 2000;
  const evFixo = evFixoSemJackpotInd(premio14);
  const jbe = breakEvenInd(premio14);

  const acumulado = d.especial || 0;
  const pool15 = opts.pool15 ?? 300_000_000;              // estimativa oficial Caixa
  const arrecadacao = opts.arrecadacao ?? 600_000_000;    // arrecadação estimada do especial
  const tickets = opts.tickets ?? Math.max(1, Math.round(arrecadacao / PRECO));

  // Pool da faixa 14: razão histórica observada no especial 2025
  // (pool14 ≈ 8,4% do pool15: 19,4M / 231,9M).
  const pool14 = pool15 * 0.084;
  const ev14Rateio = pool14 / tickets;
  const ev15Rateio = pool15 / tickets;

  // EV fixo (11/12/13) não é diluído — valores fixos por aposta vencedora.
  let evFixoNaoDiluido = 0;
  for (const [k, v] of Object.entries(PRECO_FIXO_IND)) evFixoNaoDiluido += P(Number(k)) * v;

  const evTotalRateio = evFixoNaoDiluido + ev14Rateio + ev15Rateio;
  const janelaAberta = evTotalRateio > PRECO;

  // Teto de apostas: menor nº de tickets que mantém EV>0 dado o pool estimado.
  // EV = evFixo + (pool14 + pool15)/tickets > PRECO  →  tickets < (pool14+pool15)/(PRECO-evFixo)
  const maxTicketsEV = (pool14 + pool15) / (PRECO - evFixoNaoDiluido);

  return {
    acumulado: acumulado,
    estimativaOficial15: pool15,
    breakEvenIndiviso: jbe,
    evFixoIndiviso: evFixo,
    // cenário indiviso (acumulado atual)
    evTotalIndivisoAcumulado: evFixo + P(15) * acumulado,
    // cenário com rateio (pool estimado / tickets)
    arrecadacao: arrecadacao,
    tickets: tickets,
    pool15: pool15,
    evFixoNaoDiluido: evFixoNaoDiluido,
    ev14Rateio: ev14Rateio,
    ev15Rateio: ev15Rateio,
    evTotalRateio: evTotalRateio,
    janelaAberta: janelaAberta,
    pctDaJanela: evTotalRateio / PRECO * 100,
    maxTicketsEV: maxTicketsEV,
    arrecadacaoMaxEV: maxTicketsEV * PRECO,
  };
}

async function buscarCaixa() {
  const res = await fetch(API_BASE, { headers: { accept: 'application/json' } });
  if (!res.ok) throw new Error(`Caixa HTTP ${res.status}`);
  return res.json();
}

function extrairDados(j) {
  const rateio = (j.listaRateioPremio || []).reduce((acc, f) => {
    acc[f.faixa] = { ganhadores: f.numeroDeGanhadores, premio: f.valorPremio };
    return acc;
  }, {});
  return {
    concurso: j.numero,
    proximoConcurso: j.numeroConcursoProximo,
    dataProximo: j.dataProximoConcurso,
    estimado15: j.valorEstimadoProximoConcurso,          // prêmio estimado do 15 pts no próximo
    acumulado15: j.valorAcumuladoProximoConcurso,        // acumulado regular
    acumuladoFinal0: j.valorAcumuladoConcurso_0_5 || 0,  // acumulado p/ concursos final 0
    especial: j.valorAcumuladoConcursoEspecial || 0,     // Lotofácil da Independência
    arrecadado: j.valorArrecadado,
    premio14Ultimo: rateio[2]?.premio ?? null,
    premio15Ultimo: rateio[1]?.premio ?? null,
  };
}

function calcular(d) {
  // prêmio 14 usado no EV: último sorteado (proxy), senão estimativa 2400
  const premio14 = d.premio14Ultimo ?? 2400;
  const evFixo = evFixoSemJackpot(premio14);
  const jbe = breakEven(premio14);

  // prêmio 15 "efetivo" = estimado do próximo + acumulados que alimentam a faixa 15
  const jEfetivo = (d.estimado15 ?? 0) + (d.acumulado15 ?? 0) + d.acumuladoFinal0;

  const evTotal = evFixo + P(15) * jEfetivo;
  const janelaAberta = evTotal > PRECO;

  return {
    ...d,
    premio14Usado: premio14,
    evFixo: evFixo,
    evJackpot: P(15) * jEfetivo,
    evTotal: evTotal,
    breakEven: jbe,
    jEfetivo: jEfetivo,
    janelaAberta,
    pctDaJanela: jEfetivo / jbe * 100,
  };
}

function relatorio(d) {
  const lines = [];
  lines.push('==========================================================');
  lines.push('  JANELA DE EV POSITIVO — LOTOFÁCIL');
  lines.push('==========================================================');
  lines.push(`  Último concurso       : ${d.concurso}  (sorteado ${d.dataProximo ? '—' : ''})`);
  lines.push(`  Próximo concurso      : ${d.proximoConcurso}  (${d.dataProximo || '?'})`);
  lines.push(`  Prêmio 15 estimado    : ${brl(d.estimado15 ?? 0)}`);
  lines.push(`  Acumulado regular     : ${brl(d.acumulado15 ?? 0)}`);
  lines.push(`  Acumulado (final 0)   : ${brl(d.acumuladoFinal0)}`);
  lines.push(`  Acumulado Especial    : ${brl(d.especial)}  (Independência)`);
  lines.push(`  Prêmio 14 (último)    : ${brl(d.premio14Ultimo ?? 2400)}`);
  lines.push('----------------------------------------------------------');
  lines.push(`  EV fixo (11-14)       : ${brl(d.evFixo)}`);
  lines.push(`  EV do 15 pts (J)      : ${brl(d.evJackpot)}`);
  lines.push(`  EV total por aposta   : ${brl(d.evTotal)}  (custo ${brl(PRECO)})`);
  lines.push(`  Break-even (J*)       : ${brl(d.breakEven)}`);
  lines.push(`  J efetivo             : ${brl(d.jEfetivo)}  (${d.pctDaJanela.toFixed(1)}% do break-even)`);
  lines.push('----------------------------------------------------------');
  if (d.janelaAberta) {
    lines.push('  ✓ JANELA ABERTA — EV POSITIVO. Jogar é matematicamente favorável.');
  } else {
    lines.push(`  ✗ Janela fechada — EV negativo (${brl(d.evTotal - PRECO)} por aposta).`);
    lines.push(`    Faltam ${brl(Math.max(0, d.breakEven - d.jEfetivo))} para abrir a janela.`);
  }
  lines.push('==========================================================');
  return lines.join('\n');
}

function relatorioInd(ind) {
  const lines = [];
  lines.push('==========================================================');
  lines.push('  LOTOFÁCIL DA INDEPENDÊNCIA — concurso especial');
  lines.push('==========================================================');
  lines.push(`  Regras 2026: fixos 11→R$3,50 · 12→R$7,00 · 13→R$17,50`);
  lines.push(`              15 acertos → 87% · 14 acertos → 13%`);
  lines.push(`  Acumulado especial   : ${brl(ind.acumulado)}`);
  lines.push(`  Estimativa oficial   : ${brl(ind.estimativaOficial15)} (15 pts)`);
  lines.push('----------------------------------------------------------');
  lines.push(`  Break-even indiviso   : ${brl(ind.breakEvenIndiviso)}`);
  lines.push(`  EV indiviso (acum.)   : ${brl(ind.evTotalIndivisoAcumulado)}  (custo ${brl(PRECO)})`);
  lines.push('  ── cenário com rateio ──');
  lines.push(`  Apostas estimadas     : ${ind.tickets.toLocaleString('pt-BR')}`);
  lines.push(`  Pool 15 (estimado)    : ${brl(ind.pool15)}  → EV ${brl(ind.ev15Rateio)}/aposta`);
  lines.push(`  Pool 14 (proxy 8,4%)  : ${brl(ind.pool15 * 0.084)}  → EV ${brl(ind.ev14Rateio)}/aposta`);
  lines.push(`  EV fixo (11-13)       : ${brl(ind.evFixoNaoDiluido)}`);
  lines.push(`  EV total c/ rateio    : ${brl(ind.evTotalRateio)}  (${ind.pctDaJanela.toFixed(1)}% do custo)`);
  lines.push('----------------------------------------------------------');
  if (ind.janelaAberta) {
    lines.push('  ✓ EV POSITIVO mesmo dividindo o prêmio.');
  } else {
    lines.push('  ✗ EV negativo sob rateio — a divisão entre muitos ganhadores');
    lines.push('    anula a vantagem do acumulado (número alto de apostas).');
    lines.push(`    Teto p/ EV>0: ${ind.maxTicketsEV.toLocaleString('pt-BR')} apostas`);
    lines.push(`    (arrecadação ≤ ${brl(ind.arrecadacaoMaxEV)}).`);
  }
  lines.push('==========================================================');
  return lines.join('\n');
}

async function main() {
  const args = process.argv.slice(2);
  const jsonOut = args.includes('--json');
  const watchIdx = args.indexOf('--watch');
  const watchSec = watchIdx >= 0 && args[watchIdx + 1] ? Number(args[watchIdx + 1]) : 0;

  const opt = (name, dft) => {
    const i = args.indexOf(name);
    return i >= 0 && args[i + 1] ? Number(args[i + 1]) : dft;
  };
  const optsInd = {
    premio14: opt('--ind-premio14', 2000),
    arrecadacao: opt('--ind-arrecadacao', 600_000_000),
    tickets: opt('--ind-tickets', 0) || null,
    pool15: opt('--ind-pool15', 300_000_000),
  };

  do {
    try {
      const j = await buscarCaixa();
      const d = calcular(extrairDados(j));
      const ind = calcularIndependencia(d, optsInd);
      if (jsonOut) {
        console.log(JSON.stringify({ ok: true, data: { regular: d, independencia: ind } }));
      } else {
        console.log(relatorio(d));
        console.log();
        console.log(relatorioInd(ind));
      }
    } catch (e) {
      if (jsonOut) {
        console.log(JSON.stringify({ ok: false, error: e.message }));
      } else {
        console.error('ERRO ao consultar a Caixa:', e.message);
      }
      if (!watchSec) process.exitCode = 1;
    }
    if (watchSec > 0) {
      await new Promise(r => setTimeout(r, watchSec * 1000));
    }
  } while (watchSec > 0);
}

main().catch(e => {
  console.error(e.message);
  process.exit(1);
});
