import { NextResponse } from 'next/server';
import { validateInput } from '@/lib/chat-security';
import { buildSystemPrompt } from '@/lib/chat-prompt';
import { analiseCompleta } from '@/lib/analise-completa';

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

const comboStorage = new Map<string, string>();

const TODAS_RE = /todas|todas\s*as|all|many|muitas|1000|[5-9]\d{2,}/i;

function extrairQtdCombo(msg: string, jogosPorNumero: number = 15): { qtd: number; q: number; f: number; m: number } | null {
  const qtdMatch = msg.match(/(?:^|\D)(\d{1,3})\s*(?:combina|conjunto|jogo|aposta)s?/i);
  const qtd = qtdMatch ? parseInt(qtdMatch[1], 10) : 3;

  const q = msg.match(/(\d+)\s*(?:numeros\s*)?quentes?/i);
  const f = msg.match(/(\d+)\s*(?:numeros\s*)?frios?/i);
  const m = msg.match(/(\d+)\s*(?:numeros\s*)?mornos?/i);

  if (!q || !f || !m) return null;

  const qv = parseInt(q[1], 10);
  const fv = parseInt(f[1], 10);
  const mv = parseInt(m[1], 10);

  if (qv + fv + mv !== jogosPorNumero || qv < 1 || fv < 1 || mv < 1) return null;

  return { qtd, q: qv, f: fv, m: mv };
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
  qtdQ: number, qtdF: number, qtdM: number,
  quantidade: number,
  dashboardData?: any,
  repetidosNumeros: number[] = [],
  repetidosCadeia: number[] = []
): string[] {
  const scoreMap = dashboardData ? calcularScoreNumeros(dashboardData) : new Map();
  const palpiteSet = dashboardData ? new Set(dashboardData.palpite) : new Set();
  const medias = dashboardData?.medias_historicas;

  const cadeiaSet = new Set(repetidosCadeia);
  const repSimplesSet = new Set(repetidosNumeros);

  const pool: { combo: number[]; score: number }[] = [];
  const vistos = new Set<string>();

  const maxIter = Math.min(Math.max(quantidade * 100, 10000), 500000);

  for (let c = 0; c < maxIter; c++) {
    const qSel = [...qSet].sort(() => Math.random() - 0.5).slice(0, qtdQ);
    const fSel = [...fSet].sort(() => Math.random() - 0.5).slice(0, qtdF);
    const mSel = [...mSet].sort(() => Math.random() - 0.5).slice(0, qtdM);
    const combo = [...qSel, ...fSel, ...mSel].sort((a, b) => a - b);
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
  for (const item of pool) {
    if (selecionados.length >= quantidade) break;
    const maxOverlap = dashboardData ? Math.floor((dashboardData.numeros_por_jogo || 15) * 0.8) : 12;
  if (selecionados.some(s => {
      const overlap = s.filter(n => item.combo.includes(n)).length;
      return overlap >= maxOverlap;
    })) continue;
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
    const { message, history, janela: janelaParam, loteria: loteriaParam } = body as { message?: string; history?: Message[]; janela?: number; loteria?: string };

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

    const comboReq = extrairQtdCombo(message, dashboardData.numeros_por_jogo || 15);
    if (comboReq) {
      const todas = TODAS_RE.test(message);
      const total = todas ? 100000 : Math.min(comboReq.qtd, 100000);
      const combos = gerarCombinacoes(qSet, mSet, fSet, comboReq.q, comboReq.f, comboReq.m, total, dashboardData,
        dashboardData.ultimo_sorteio.repetidos_numeros, dashboardData.repetidos_cadeia);

      if (combos.length > 10) {
        const token = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        comboStorage.set(token, combos.join('\n'));
        setTimeout(() => comboStorage.delete(token), 300000);
        const url = `/api/chat?token=${token}`;
        return NextResponse.json({
          download: url,
          reply: `Foram geradas **${combos.length}** combinacoes.\n\n[📥 Baixar arquivo TXT](${url})`
        });
      }

      return NextResponse.json({ reply: combos.join('\n') });
    }

    const lastDraw = dashboardData.ultimo_sorteio;
    const quentesStr = qSet.join(', ');
    const mornosStr = mSet.join(', ');
    const friosStr = fSet.join(', ');

    const contextData = `
## DADOS ATUAIS
Ultimo: #${dashboardData.ultimo_concurso} | Janela: ${dashboardData.janela_usada} sorteios
Ultimo sorteio: ${lastDraw.numeros.join(', ')}

## CATEGORIAS OFICIAIS - USE SOMENTE ESTES NUMEROS
QUENTES = [${quentesStr}]
MORNOS  = [${mornosStr}]
FRIOS   = [${friosStr}]

## REGRA DE COMBINACAO
- Cada combinacao tem ${dashboardData.numeros_por_jogo || 15} numeros = X QUENTES + Y FRIOS + Z MORNOS
- Ex: 6 QUENTES + 6 FRIOS + 3 MORNOS = ${dashboardData.numeros_por_jogo || 15}
- ESCOLHA os numeros DENTRO dos colchetes acima.
- NAO crie suas proprias categorias.
- NAO use numeros que nao estejam nas listas acima.
- Sempre ordene do menor para o maior.
`.trim();

    const systemPrompt = buildSystemPrompt(dashboardData.nome_jogo, dashboardData.numeros_por_jogo);
    const messages = [
      { role: 'system', content: systemPrompt + '\n\n' + contextData },
      ...(history || []).slice(-10),
      { role: 'user', content: message },
    ];

    const ollamaModel = process.env.OLLAMA_MODEL;

    if (ollamaModel) {
      const res = await fetch('http://localhost:11434/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: ollamaModel,
          messages,
          stream: false,
          options: { num_predict: 1024, temperature: 0.3 },
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        console.error('Ollama error:', res.status, errText);
        return NextResponse.json({ error: 'Erro ao consultar o assistente local.' }, { status: 502 });
      }

      const data = await res.json();
      const reply = data.message?.content;
      if (!reply) {
        return NextResponse.json({ error: 'Resposta vazia do assistente local.' }, { status: 502 });
      }
      return NextResponse.json({ reply });
    }

    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: 'API nao configurada.' }, { status: 500 });
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

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const token = searchParams.get('token');
  if (!token || !comboStorage.has(token)) {
    return NextResponse.json({ error: 'Token invalido ou expirado.' }, { status: 404 });
  }
  const content = comboStorage.get(token)!;
  comboStorage.delete(token);
  return new NextResponse(content, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Content-Disposition': 'attachment; filename="combinacoes.txt"',
    },
  });
}
