import { NextResponse } from 'next/server';
import { validateInput } from '@/lib/chat-security';
import { buildSystemPrompt } from '@/lib/chat-prompt';
import { analiseCompleta } from '@/lib/analise-completa';
import { loadLoteriaSkill, buildEnrichedContext } from '@/lib/loteria-skill';
import { gerarCombinacoesSuperSete } from '@/lib/gerador-supersete-lib';

function combinacoesExaustivasFixos(fixos: number[], totalNumeros: number = 15): number[][] {
  const fixoSet = new Set(fixos.sort((a, b) => a - b));
  const restantes: number[] = [];
  for (let n = 1; n <= 25; n++) {
    if (!fixoSet.has(n)) restantes.push(n);
  }
  const precisamos = totalNumeros - fixos.length;
  if (precisamos < 1 || precisamos > restantes.length) return [];

  function combinar(arr: number[], k: number): number[][] {
    if (k === 0) return [[]];
    if (arr.length < k) return [];
    const resultado: number[][] = [];
    for (let i = 0; i <= arr.length - k; i++) {
      for (const sub of combinar(arr.slice(i + 1), k - 1)) {
        resultado.push([arr[i], ...sub]);
      }
    }
    return resultado;
  }

  return combinar(restantes, precisamos).map(sel =>
    [...fixos, ...sel].sort((a, b) => a - b)
  );
}

export const dynamic = 'force-dynamic';
export const maxDuration = 60;

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const RATE_LIMIT = 20;
const requests = new Map<string, { count: number; resetAt: number }>();

function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const entry = requests.get(ip);
  if (!entry || now > entry.resetAt) {
    requests.set(ip, { count: 1, resetAt: now + 60000 });
    return true;
  }
  if (entry.count >= RATE_LIMIT) return false;
  entry.count++;
  return true;
}

const TODAS_RE = /todas|todas\s*as|all|many|muitas|1000|[5-9]\d{2,}/i;

function extrairFixos(msg: string): number[] {
  const fixos: number[] = [];

  const suffixMatch = msg.match(/(?:MAIS\s+)?(?:OS\s+)?NUMEROS?\s+((?:\d{1,2}\s*(?:E|,|\s)\s*)+\d{1,2})\s+FIXOS?/i);
  if (suffixMatch) {
    return suffixMatch[1].split(/\s*(?:E|,)\s*|\s+/).map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= 1 && n <= 25);
  }

  const listMatch = msg.match(/(?:com\s+)?(?:os\s+)?fixos?\s*[:\s]*((?:\d{1,2}\s*[,\s]\s*)+\d{1,2})/i);
  if (listMatch) {
    return listMatch[1].split(/[,\s]+/).map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= 1 && n <= 25);
  }

  const re = /(\d{1,2})\s*(?:numeros?\s*)?fixos?|numero\s+(\d{1,2})\s*fixo/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(msg)) !== null) {
    const v = parseInt(m[1] || m[2], 10);
    if (!isNaN(v) && v >= 1 && v <= 25) fixos.push(v);
  }
  return [...new Set(fixos)];
}

interface GrupoConstraint {
  qtd: number;
  numeros: number[];
}

function extrairMultiGrupo(msg: string): { grupos: GrupoConstraint[]; fixos: number[] } | null {
  const grupos: GrupoConstraint[] = [];
  const re = /(\d{1,2})\s*(?:NUMEROS?\s+)?DESSES?(?:\s+NUMEROS?)?\s*(?:\d{1,3}\s*)?\(([^)]+)\)/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(msg)) !== null) {
    const qtd = parseInt(m[1], 10);
    const numeros = m[2].split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= 1 && n <= 25);
    if (numeros.length === 0) continue;
    grupos.push({ qtd, numeros });
  }
  if (grupos.length < 2) return null;

  const fixos = extrairFixos(msg);
  return { grupos, fixos };
}

function combinacoesMultiGrupo(grupos: GrupoConstraint[], fixos: number[], totalNumeros: number = 15): number[][] {
  if (grupos.length === 0) return [];

  function combinar(arr: number[], k: number): number[][] {
    if (k === 0) return [[]];
    if (arr.length < k) return [];
    const r: number[][] = [];
    for (let i = 0; i <= arr.length - k; i++) {
      for (const sub of combinar(arr.slice(i + 1), k - 1)) {
        r.push([arr[i], ...sub]);
      }
    }
    return r;
  }

  const fixoSet = new Set(fixos);
  const gruposAjustados = grupos.map(g => {
    const overlap = g.numeros.filter(n => fixoSet.has(n)).length;
    return {
      qtd: Math.max(0, g.qtd - overlap),
      pool: g.numeros.filter(n => !fixoSet.has(n))
    };
  });

  const picksPorGrupo = gruposAjustados.map(g => combinar(g.pool, g.qtd));
  if (picksPorGrupo.some(p => p.length === 0)) return [];

  const totalPick = gruposAjustados.reduce((s, g) => s + g.qtd, 0);
  if (fixos.length + totalPick !== totalNumeros) return [];

  const todosFixos = [...fixos].sort((a, b) => a - b);
  const vistos = new Set<string>();
  const resultado: number[][] = [];

  function produtoCartesiano(idx: number, acum: number[]): void {
    if (idx === picksPorGrupo.length) {
      const combo = [...todosFixos, ...acum].sort((a, b) => a - b);
      const key = combo.join(',');
      if (!vistos.has(key)) {
        vistos.add(key);
        resultado.push(combo);
      }
      return;
    }
    for (const pick of picksPorGrupo[idx]) {
      produtoCartesiano(idx + 1, [...acum, ...pick]);
    }
  }

  produtoCartesiano(0, []);
  return resultado;
}

function extrairGruposInline(msg: string, maxNumeros: number = 80): GrupoConstraint[] | null {
  const grupos: GrupoConstraint[] = [];
  const re = /(\d{1,2})\s*(?:numeros?\s+)?(?:dos?|das?)\s+(?:aquecendo|esfriando|quentes?|frios?|mornos?)\s*(?:[🟢🟠🔴]\w*)?\s*([\s\S]+?)(?=\s*e\s+\d+\s*(?:numeros?\s+)?(?:do|da|dos|das)|$)/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(msg)) !== null) {
    const qtd = parseInt(m[1], 10);
    const numsStr = m[2].trim();
    const numeros = numsStr.split(/[\s,]+/).map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n >= 1 && n <= maxNumeros);
    if (numeros.length > 0) grupos.push({ qtd, numeros });
  }
  return grupos.length >= 2 ? grupos : null;
}

function gerarCombinacoesComGrupos(
  grupos: GrupoConstraint[], fixos: number[], allNums: number[],
  quantidade: number, maxOverlap: number, totalNumeros: number
): string[] {
  const fixoSet = new Set(fixos);
  const usadoGrupos = new Set(grupos.flatMap(g => g.numeros));
  const gruposAdj = grupos.map(g => ({
    qtd: Math.max(0, g.qtd - g.numeros.filter(n => fixoSet.has(n)).length),
    pool: g.numeros.filter(n => !fixoSet.has(n))
  }));
  const totalPick = gruposAdj.reduce((s, g) => s + g.qtd, 0);
  const precisamos = totalNumeros - fixos.length;
  const restante = precisamos - totalPick;
  if (restante < 0) return [];
  const freePool = allNums.filter(n => !fixoSet.has(n) && !usadoGrupos.has(n));
  const maxIter = Math.min(Math.max(quantidade * 100, 10000) * (maxOverlap <= 1 ? 5 : 1), 500000);
  const pool: number[][] = [];
  const vistos = new Set<string>();
  for (let c = 0; c < maxIter; c++) {
    const combo: number[] = [...fixos];
    let ok = true;
    for (const g of gruposAdj) {
      const pick = [...g.pool].sort(() => Math.random() - 0.5).slice(0, g.qtd);
      if (pick.length < g.qtd) { ok = false; break; }
      combo.push(...pick);
    }
    if (!ok) continue;
    if (restante > 0) {
      const pick = [...freePool].sort(() => Math.random() - 0.5).slice(0, restante);
      if (pick.length < restante) continue;
      combo.push(...pick);
    }
    const sorted = combo.sort((a, b) => a - b);
    const key = sorted.join(',');
    if (vistos.has(key)) continue;
    vistos.add(key);
    pool.push(sorted);
  }
  const selecionados: number[][] = [];
  for (const combo of pool) {
    if (selecionados.length >= quantidade) break;
    if (selecionados.some(s => {
      const overlap = s.filter(n => combo.includes(n)).length;
      return overlap >= maxOverlap;
    })) continue;
    selecionados.push(combo);
  }
  return selecionados.map(c => c.join(','));
}

function extrairRepetidosAnterior(msg: string): { min: number; max: number } | null {
  const range = msg.match(/entre\s+(\d+)\s*(?:e|a)\s*(\d+)\s*(?:numeros?\s*)?repetidos?\s*(?:do\s*)?sorteio\s*anterior/i);
  if (range) return { min: parseInt(range[1], 10), max: parseInt(range[2], 10) };
  const single = msg.match(/(\d+)\s*(?:numeros?\s*)?repetidos?\s*(?:do\s*)?sorteio\s*anterior/i);
  if (single) { const v = parseInt(single[1], 10); return { min: v, max: v }; }
  return null;
}

function extrairGrupo(msg: string): { min: number; max: number; numeros: number[] } | null {
  const m = msg.match(/entre\s+(\d+)\s*(?:e|a)\s*(\d+)\s*(?:numeros?\s*)?(?:do\s*)?(?:seguinte\s+)?grupo\s*(?::)?\s*\(([^)]+)\)/i);
  if (!m) return null;
  const numeros = m[3].split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
  return { min: parseInt(m[1], 10), max: parseInt(m[2], 10), numeros };
}

function extrairMinComum(msg: string): number | null {
  const m = msg.match(/(\d{1,2})\s*(?:numeros?\s*)?em\s*comum\s*(?:entre\s*)?elas/i);
  return m ? parseInt(m[1], 10) : null;
}

function extrairMaxOverlapJogos(msg: string): number | null {
  if (/sem\s+(?:nenhum|nhum|n\s*enhum)?\s*(?:numeros?\s+)?repetidos?/i.test(msg)) return 0;
  if (/(?:n[aã]o\s+(?:deve|pode)?\s*ter?\s+|nenhum|zero|0)\s+(?:numeros?\s+)?repetidos?/i.test(msg)) return 0;
  if (/(?:nenhum|sem|zero|0)\s+(?:numeros?\s+)?(?:em\s+comum)/i.test(msg)) return 0;
  if (/numeros?\s+diferentes?\s+entre\s+si/i.test(msg)) return 0;
  if (/cada\s+numero\s+aparece\s+uma\s+vez/i.test(msg)) return 0;
  const m = msg.match(/(?:(?:no\s+)?maximo|ate|max)\s+(\d{1,2})\s*(?:numeros?\s+)?(?:repetidos?|em\s+comum)/i);
  if (m) { const v = parseInt(m[1], 10); return v >= 0 ? v : null; }
  return null;
}

interface PosicaoConstraint {
  pos: number;
  numero: number;
}

function extrairPosicoes(msg: string, maxPos: number): PosicaoConstraint[] | null {
  const constraints: PosicaoConstraint[] = [];
  const re = /n[aã]o?\s*posi[cç][aã]o\s*(?:n)?(\d+)\s*(?:o\s+)?n[uú]meros?\s*(\d{1,2})|n[uú]meros?\s*(\d{1,2})\s*(?:n[aã]o?\s*)?posi[cç][aã]o\s*(?:n)?(\d+)/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(msg)) !== null) {
    const pos = parseInt(m[1] || m[4], 10);
    const num = parseInt(m[2] || m[3], 10);
    if (pos >= 1 && pos <= maxPos && num >= 1) {
      constraints.push({ pos, numero: num });
    }
  }
  if (constraints.length === 0) {
    const alt = msg.match(/numeros?\s+(\d{1,2})\s+e\s+(\d{1,2})\s+.*?posi[cç][aã]o\s*(?:n)?(\d+)/i);
    if (alt) {
      const num1 = parseInt(alt[1], 10);
      const num2 = parseInt(alt[2], 10);
      const pos = parseInt(alt[3], 10);
      if (pos >= 1 && pos <= maxPos) {
        constraints.push({ pos, numero: num1 });
        constraints.push({ pos, numero: num2 });
      }
    }
  }
  return constraints.length > 0 ? constraints : null;
}

function extrairCategoriaRange(msg: string, cat: string): { min: number; max: number } | null {
  const range = new RegExp(`entre\\s+(\\d+)\\s*(?:e|a)\\s*(\\d+)\\s*(?:numeros?\\s*)?${cat}`, 'i');
  const rm = msg.match(range);
  if (rm) return { min: parseInt(rm[1], 10), max: parseInt(rm[2], 10) };
  const single = new RegExp(`(\\d+)\\s*(?:numeros?\\s*)?${cat}`, 'i');
  const sm = msg.match(single);
  if (sm) { const v = parseInt(sm[1], 10); return { min: v, max: v }; }
  return null;
}

function pickQMF(qr: { min: number; max: number }, mr: { min: number; max: number }, fr: { min: number; max: number }, total: number, fixos: number): [number, number, number] {
  const slots = total - fixos;
  const valid: [number, number, number][] = [];
  for (let qv = qr.min; qv <= qr.max; qv++) {
    for (let mv = mr.min; mv <= mr.max; mv++) {
      const fv = slots - qv - mv;
      if (fv >= fr.min && fv <= fr.max) valid.push([qv, mv, fv]);
    }
  }
  if (valid.length === 0) {
    const fv = Math.max(fr.min, Math.min(fr.max, slots - qr.min - mr.min));
    const qv = Math.min(qr.max, slots - mr.min - fv);
    const mv = slots - qv - fv;
    return [qv, mv, fv];
  }
  return valid[Math.floor(Math.random() * valid.length)];
}

function extrairQtdCombo(msg: string, jogosPorNumero: number = 15, qSet?: number[], mSet?: number[], fSet?: number[]): {
  qtd: number; qRange: { min: number; max: number }; mRange: { min: number; max: number }; fRange: { min: number; max: number };
  overlap: number; fixos: number[]; repetidosRange: { min: number; max: number } | null;
  grupoConstraint: { min: number; max: number; numeros: number[] } | null; minComum: number | null; totalNumeros: number;
  posicoes: PosicaoConstraint[] | null
} | null {
  const ehTodasCollection = TODAS_RE.test(msg) && !/(?:em|a|de)\s+todas\s+(?:as\s+)?combina/i.test(msg);
  const qtdMatch = msg.match(/(?:^|\D)(\d{1,3})\s*(?:combina|conjunto|jogo|aposta)s?/i);
  const qtd = ehTodasCollection ? 100000 : (qtdMatch ? parseInt(qtdMatch[1], 10) : 3);

  const explSize = msg.match(/(?:combina[cç][oõ]es\s+)?de\s+(\d{1,2})\s*(?:n[uú]meros?|dezenas?)/i);
  const totalNumeros = explSize ? parseInt(explSize[1], 10) : jogosPorNumero;

  const temQFM = /quentes?|frios?|mornos?/i.test(msg);
  const qRange = extrairCategoriaRange(msg, 'quentes?');
  const fRange = extrairCategoriaRange(msg, 'frios?');
  const mRange = extrairCategoriaRange(msg, 'mornos?');

  const fixos = extrairFixos(msg);
  const repetidosRange = extrairRepetidosAnterior(msg);
  const grupoConstraint = extrairGrupo(msg);
  const minComum = extrairMinComum(msg);
  const posicoes = extrairPosicoes(msg, totalNumeros);

  const userMaxOverlap = extrairMaxOverlapJogos(msg);
  const defaultOverlap = Math.max(1, Math.floor(totalNumeros * 0.8));

  if (!qRange || !fRange || !mRange) {
    if (temQFM) return null;
    if (!qtdMatch && !ehTodasCollection) return null;
    const total = (qSet?.length || 0) + (mSet?.length || 0) + (fSet?.length || 0);
    if (total === 0) return null;
    const slots = totalNumeros - fixos.length;
    if (slots < 1) return null;
    const qv = Math.max(1, Math.round((slots * (qSet?.length || 0)) / total));
    const mv = Math.max(1, Math.round((slots * (mSet?.length || 0)) / total));
    const fv = Math.max(1, slots - qv - mv);
    const def = { min: Math.min(qv, totalNumeros), max: Math.min(qv, totalNumeros) };
    const overlap = userMaxOverlap !== null ? userMaxOverlap : defaultOverlap;
    return { qtd, qRange: def, mRange: def, fRange: def, overlap, fixos, repetidosRange, grupoConstraint, minComum, totalNumeros, posicoes };
  }

  const overlap = userMaxOverlap !== null ? userMaxOverlap : defaultOverlap;
  return { qtd, qRange, mRange, fRange, overlap, fixos, repetidosRange, grupoConstraint, minComum, totalNumeros, posicoes };
}

function calcularScoreNumeros(
  dashboardData: any
): Map<number, number> {
  const score = new Map<number, number>();
  const palpiteSet = new Set(dashboardData.palpite);
  const freq30 = dashboardData.frequencia_30;
  const ciclos = dashboardData.ciclos;

  const maxFreq = Math.max(...Object.values(freq30).map(Number), 1);

  for (let n = 1; n <= (dashboardData.total_numeros || 25); n++) {
    let s = 0;
    if (palpiteSet.has(n)) s += 5;
    const f = Number(freq30[String(n)] || 0);
    s += (f / maxFreq) * 3;
    const ciclo = ciclos[String(n)];
    if (ciclo) {
      if (ciclo.estado === 'aquecendo') s += 2;
      else if (ciclo.estado === 'estavel') s += 1;
    }
    score.set(n, Math.round(s * 100) / 100);
  }
  return score;
}

function gerarCombinacoes(
  qSet: number[], mSet: number[], fSet: number[],
  qRange: { min: number; max: number }, mRange: { min: number; max: number }, fRange: { min: number; max: number },
  quantidade: number,
  dashboardData?: any,
  repetidosNumeros: number[] = [],
  repetidosCadeia: number[] = [],
  maxOverlap?: number,
  fixos: number[] = [],
  repetidosRange: { min: number; max: number } | null = null,
  grupoConstraint: { min: number; max: number; numeros: number[] } | null = null,
  minComum: number | null = null,
  totalNumeros: number = 15,
  posicoes: PosicaoConstraint[] = []
): string[] {
  const fixoSet = new Set(fixos);
  const qFiltrado = qSet.filter(n => !fixoSet.has(n));
  const mFiltrado = mSet.filter(n => !fixoSet.has(n));
  const fFiltrado = fSet.filter(n => !fixoSet.has(n));

  const ultimoSorteioSet = new Set(dashboardData?.ultimo_sorteio?.numeros || []);
  const grupoSet = grupoConstraint ? new Set(grupoConstraint.numeros) : null;

  const scoreMap = dashboardData ? calcularScoreNumeros(dashboardData) : new Map();
  const medias = dashboardData?.medias_historicas;

  const cadeiaSet = new Set(repetidosCadeia);
  const repSimplesSet = new Set(repetidosNumeros);

  const pool: { combo: number[]; score: number }[] = [];
  const vistos = new Set<string>();

  const maxIter = Math.min(Math.max(quantidade * 100, 10000) * (maxOverlap !== undefined && maxOverlap <= 1 ? 5 : 1), 500000);

  for (let c = 0; c < maxIter; c++) {
    const [qP, mP, fP] = pickQMF(qRange, mRange, fRange, totalNumeros, fixos.length);
    let qtdQF = qP;
    let qtdMF = mP;
    let qtdFF = fP;
    for (const f of fixos) {
      if (qSet.includes(f)) qtdQF = Math.max(0, qtdQF - 1);
      else if (mSet.includes(f)) qtdMF = Math.max(0, qtdMF - 1);
      else if (fSet.includes(f)) qtdFF = Math.max(0, qtdFF - 1);
    }
    if (qtdQF > qFiltrado.length || qtdMF > mFiltrado.length || qtdFF > fFiltrado.length) continue;

    const qSel = [...qFiltrado].sort(() => Math.random() - 0.5).slice(0, qtdQF);
    const fSel = [...fFiltrado].sort(() => Math.random() - 0.5).slice(0, qtdFF);
    const mSel = [...mFiltrado].sort(() => Math.random() - 0.5).slice(0, qtdMF);
    const combo = [...qSel, ...fSel, ...mSel, ...fixos].sort((a, b) => a - b);

    if (repetidosRange && ultimoSorteioSet.size > 0) {
      const r = combo.filter(n => ultimoSorteioSet.has(n)).length;
      if (r < repetidosRange.min || r > repetidosRange.max) continue;
    }

    if (grupoSet && grupoSet.size > 0) {
      const g = combo.filter(n => grupoSet.has(n)).length;
      if (g < grupoConstraint!.min || g > grupoConstraint!.max) continue;
    }

    const key = combo.join(',');
    if (vistos.has(key)) continue;
    vistos.add(key);

    if (scoreMap.size > 0) {
      let s = 0;
      for (const n of combo) {
        let ns = scoreMap.get(n) || 0;
        if (cadeiaSet.has(n)) ns += 3;
        else if (repSimplesSet.has(n)) ns += 1.5;
        s += ns;
      }
      if (medias) {
        const soma = combo.reduce((a, b) => a + b, 0);
        s += Math.max(0, 3 - Math.abs(soma - medias.soma) / 10);
        const pares = combo.filter(n => n % 2 === 0).length;
        s += Math.max(0, 1 - Math.abs(pares - medias.pares) / 5);
      }
      pool.push({ combo, score: Math.round(s * 100) / 100 + Math.random() * 0.5 });
    } else {
      pool.push({ combo, score: Math.random() });
    }
  }

  pool.sort((a, b) => b.score - a.score);

  const selecionados: number[][] = [];
  const posSatisfeitas = new Set<number>();
  const gameSz = dashboardData ? (dashboardData.numeros_por_aposta || dashboardData.numeros_por_jogo || 15) : 15;
  const maxOverlapVal = maxOverlap ?? (dashboardData ? Math.floor(gameSz * 0.8) : 12);

  for (const item of pool) {
    if (selecionados.length >= quantidade) break;

    const sortedCombo = [...item.combo].sort((a, b) => a - b);

    if (minComum !== null && selecionados.length > 0) {
      if (selecionados.some(s => {
        const overlap = s.filter(n => item.combo.includes(n)).length;
        return overlap < minComum;
      })) continue;
    } else {
      if (selecionados.some(s => {
        const overlap = s.filter(n => item.combo.includes(n)).length;
        return overlap >= maxOverlapVal;
      })) continue;
    }

    if (posicoes.length > 0 && posSatisfeitas.size < posicoes.length) {
      const matched = posicoes.some((pc, i) => {
        if (posSatisfeitas.has(i)) return false;
        if (sortedCombo[pc.pos - 1] === pc.numero) {
          posSatisfeitas.add(i);
          return true;
        }
        return false;
      });
      if (!matched) continue;
    }

    selecionados.push(item.combo);
  }

  return selecionados.map((c, i) => {
    const sorted = [...c].sort((a, b) => a - b);
    return sorted.join(',');
  });
}

export async function POST(req: Request) {
  try {
    const ip = req.headers.get('x-forwarded-for') || 'unknown';
    if (!checkRateLimit(ip)) {
      return NextResponse.json({ error: 'Limite de requisicoes atingido. Aguarde 1 minuto.' }, { status: 429 });
    }

    const body = await req.json();
    const { message, history, janela: janelaParam, loteria: loteriaParam, concurso: concursoParam } = body as { message?: string; history?: Message[]; janela?: number; loteria?: string; concurso?: number };

    if (!message) {
      return NextResponse.json({ error: 'Mensagem nao fornecida.' }, { status: 400 });
    }

    const validation = validateInput(message);
    if (!validation.valid) {
      return NextResponse.json({ error: validation.error }, { status: 400 });
    }

    const janela = typeof janelaParam === 'number' && janelaParam >= 2 ? janelaParam : undefined;

    const loteria = loteriaParam || undefined;
    const dashboardData = await analiseCompleta(janela, loteria);

    const qSet = [...new Set(dashboardData.numeros_quentes.map(n => n[0]))].sort((a, b) => a - b);
    const mSet = [...new Set(dashboardData.numeros_mornos.map(n => n[0]))].sort((a, b) => a - b);
    const fSet = [...new Set(dashboardData.numeros_frios.map(n => n[0]))].sort((a, b) => a - b);

    const apostaSize = () => dashboardData?.numeros_por_aposta || dashboardData?.numeros_por_jogo || 15;

    const multiGrupo = extrairMultiGrupo(message);
    if (multiGrupo) {
      const totalJogo = apostaSize();
      const exaustivas = combinacoesMultiGrupo(multiGrupo.grupos, multiGrupo.fixos, totalJogo);
      if (exaustivas.length === 0) {
        return NextResponse.json({ reply: 'Nao foi possivel gerar combinacoes com essas restricoes — total de numeros nao fecha com 15.' });
      }
      const nFixos = multiGrupo.fixos.length;
      if (exaustivas.length > 10) {
        const rawContent = exaustivas.map(c => c.join(',')).join('\n');
        const gruposDesc = multiGrupo.grupos.map((g, i) => `${g.qtd} do grupo ${i + 1}`).join(', ');
        return NextResponse.json({
          rawContent,
          filename: `combinacoes_${exaustivas.length}.txt`,
          reply: `Foram geradas **${exaustivas.length}** combinacoes (${gruposDesc}${nFixos > 0 ? ` + ${nFixos} fixo${nFixos > 1 ? 's' : ''}` : ''}).\n\n⬇️ Gerando download...`
        });
      }
      return NextResponse.json({ reply: exaustivas.map(c => c.join(',')).join('\n') });
    }

    const gruposInline = extrairGruposInline(message, dashboardData.total_numeros || 80);
    if (gruposInline) {
      const totalJogo = apostaSize();
      const allNums = Array.from({ length: dashboardData.total_numeros || 80 }, (_, i) => i + 1);
      const userMaxOverlap = extrairMaxOverlapJogos(message);
      const overlap = userMaxOverlap !== null ? userMaxOverlap : Math.max(1, Math.floor(totalJogo * 0.8));
      const qtdMatch = message.match(/(?:^|\D)(\d{1,3})\s*(?:combina|conjunto|jogo|aposta)s?/i);
      const qtd = qtdMatch ? parseInt(qtdMatch[1], 10) : 3;
      const combos = gerarCombinacoesComGrupos(gruposInline, [], allNums, Math.min(qtd, 100000), overlap, totalJogo);
      if (combos.length > 10) {
        const rawContent = combos.join('\n');
        return NextResponse.json({
          rawContent,
          filename: `combinacoes_${combos.length}.txt`,
          reply: `Foram geradas **${combos.length}** combinacoes (${gruposInline.map(g => `${g.qtd} do grupo`).join(', ')}${combos.length < qtd ? ` — foram solicitadas ${qtd}, mas as demais nao atendem as condicoes.` : '.'}\n\n⬇️ Gerando download...`
        });
      }
      return NextResponse.json({ reply: combos.join('\n') });
    }

    const comboReq = extrairQtdCombo(message, apostaSize(), qSet, mSet, fSet);
    if (comboReq) {
      const fixos = comboReq.fixos;
      const hasQFM = /quentes?|frios?|mornos?|repetidos?\s*(?:do\s*)?sorteio|grupo|em\s+comum|entre/i.test(message);
      const isSimpleFixos = fixos.length > 0 && !hasQFM && !comboReq.repetidosRange && !comboReq.grupoConstraint && comboReq.minComum === null;

      if (isSimpleFixos) {
        const exaustivas = combinacoesExaustivasFixos(fixos, comboReq.totalNumeros);
        const totalExato = exaustivas.length;
        if (totalExato > 10) {
          const rawContent = exaustivas.map(c => c.join(',')).join('\n');
          return NextResponse.json({
            rawContent,
            filename: `combinacoes_${totalExato}.txt`,
            reply: `Foram geradas **${totalExato}** combinacoes com os numeros fixos [${fixos.join(', ')}].\n\n⬇️ Gerando download...`
          });
        }
        return NextResponse.json({ reply: exaustivas.map(c => c.join(',')).join('\n') });
      }

      const total = Math.min(comboReq.qtd, 100000);
      const combos = gerarCombinacoes(qSet, mSet, fSet, comboReq.qRange, comboReq.mRange, comboReq.fRange, total, dashboardData,
        dashboardData.ultimo_sorteio.repetidos_numeros, dashboardData.repetidos_cadeia, comboReq.overlap, fixos,
        comboReq.repetidosRange, comboReq.grupoConstraint, comboReq.minComum, comboReq.totalNumeros, comboReq.posicoes || []);

      if (combos.length > 10) {
        const rawContent = combos.join('\n');
        const msg = combos.length < total
          ? `Foram geradas **${combos.length}** combinacoes (das **${total}** solicitadas — as demais nao atendem as condicoes).`
          : `Foram geradas **${combos.length}** combinacoes.`;
        return NextResponse.json({
          rawContent,
          filename: `combinacoes_${combos.length}.txt`,
          reply: `${msg}\n\n⬇️ Gerando download...`
        });
      }

      return NextResponse.json({ reply: combos.join('\n') });
    }

    const ehSuperSete = /super\s*sete|supersete/i.test(message) && /combin|jogo|aposta/i.test(message);
    if (ehSuperSete) {
      const qtdMatch = message.match(/(\d{1,3})\s*(?:combin|jogo|aposta)/i);
      const quantidade = qtdMatch ? Math.min(parseInt(qtdMatch[1], 10), 500) : 5;

      const restricoes: Record<string, any> = {};
      if (/n[aã]o.*repetir.*mesma\s*coluna|coluna.*n[aã]o.*repetir|nenhum.*repetido.*coluna/i.test(message)) {
        restricoes.coluna_nao_repetir_anterior = true;
        if (concursoParam) {
          const concursoData = await analiseCompleta(janela, loteria, concursoParam);
          restricoes.ultimo_sorteio = concursoData.ultimo_sorteio.numeros;
        }
      }
      const maxQuentes = message.match(/n[aã]o\s+mais\s+que\s+(\d)\s*colunas?\s*com\s*(?:numeros?\s+)?quentes?|max(?:imo)?\s*(\d)\s*colunas?\s*quentes?/i);
      if (maxQuentes) {
        restricoes.max_colunas_quentes = parseInt(maxQuentes[1] || maxQuentes[2], 10);
      }
      const somaRange = message.match(/soma\s*(?:entre|de)?\s*(\d+)\s*(?:e|a)\s*(\d+)/i);
      if (somaRange) {
        restricoes.soma_min = parseInt(somaRange[1], 10);
        restricoes.soma_max = parseInt(somaRange[2], 10);
      }

      const result = await gerarCombinacoesSuperSete(quantidade, restricoes);
      if (result.combinacoes.length === 0) {
        return NextResponse.json({ reply: `Não foi possível gerar combinações — apenas ${result.total_sorteios} sorteios disponíveis para Super Sete.` });
      }
      const rawContent = result.combinacoes.map(j => j.join(',')).join('\n');
      return NextResponse.json({
        rawContent,
        filename: `supersete_${result.combinacoes.length}.txt`,
        reply: `**${result.combinacoes.length}** combinações Super Sete geradas via lambda blend.\n\n⬇️ Download automático...`,
      });
    }

    const skillContent = loadLoteriaSkill(loteria || 'lotofacil');
    const enrichedContext = buildEnrichedContext(dashboardData, skillContent);

    const systemPrompt = buildSystemPrompt(dashboardData.nome_jogo, dashboardData.numeros_por_jogo);
    const messages = [
      { role: 'system', content: systemPrompt + '\n\n' + enrichedContext },
      ...(history || []).slice(-10),
      { role: 'user', content: message },
    ];

    const ollamaModel = process.env.OLLAMA_MODEL;

    if (ollamaModel) {
      try {
        const res = await fetch('http://localhost:11434/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: ollamaModel,
            messages,
            stream: false,
            options: { num_predict: 1024, temperature: 0.3 },
          }),
          signal: AbortSignal.timeout(55000),
        });

        if (!res.ok) {
          const errText = await res.text();
          console.error('Ollama error:', res.status, errText);
          throw new Error(`Ollama: ${res.status}`);
        }

        const data = await res.json();
        const reply = data.message?.content;
        if (!reply) {
          return NextResponse.json({ error: 'Resposta vazia do assistente local.' }, { status: 502 });
        }
        return NextResponse.json({ reply });
      } catch (ollamaErr) {
        console.error('Ollama unavailable, falling back to OpenRouter:', ollamaErr);
      }
    }

    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: 'Nenhum modelo de IA disponivel (Ollama offline e OpenRouter sem chave).' }, { status: 503 });
    }

    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'http://localhost:3003',
        'X-Title': 'LotoScope',
      },
      body: JSON.stringify({
        model: process.env.OPENROUTER_MODEL || 'google/gemini-2.5-pro',
        messages,
        max_tokens: 1024,
        temperature: 0.3,
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error('OpenRouter error:', res.status, errText);
      return NextResponse.json({ error: 'Erro ao consultar o assistente.' }, { status: 502 });
    }

    const data = await res.json();
    const reply = data.choices?.[0]?.message?.content;
    if (!reply) {
      return NextResponse.json({ error: 'Resposta vazia do assistente.' }, { status: 502 });
    }

    return NextResponse.json({ reply });
  } catch (err) {
    console.error('Chat error:', err);
    return NextResponse.json({ error: 'Erro interno.' }, { status: 500 });
  }
}


