using System.Diagnostics;
using System.Numerics;
using System.Text.Json;

namespace CoverGen;

/// <summary>
/// Gerador offline de covering designs C(v,k,t) para a Lotofácil (v=25,k=15,t=9..14).
///
/// Algoritmo: greedy exato de máxima cobertura com CSR reverso (target -> candidatos)
/// e buckets por ganho. Complexidade ~ O(P * C(k,t)), com P = tamanho do pool.
///
/// Uso:
///   dotnet run -c Release -- --t 9 --pool 79000 --improve 60 --out ..\..\c9.json
///   dotnet run -c Release -- --t 14 --pool 0 --out ..\..\c14.json   (pool 0 = todos)
///   --improve N roda um LNS (ruin & recreate) por N segundos após o greedy.
/// </summary>
internal static class Program
{
    private static int Main(string[] args)
    {
        var o = Options.Parse(args);
        if (o is null) { Console.Error.WriteLine("argumentos inválidos"); return 2; }

        int v = o.V, k = o.K, t = o.T;
        if (!(1 <= t && t <= k && k <= v && v <= 25)) { Console.Error.WriteLine("deve valer 1<=t<=k<=v<=25"); return 2; }

        long ckt = Binom(k, t);
        long totalTargets = Binom(v, t);
        long totalBlocks = Binom(v, k);
        long pool = o.Pool == 0 || o.Pool >= totalBlocks ? totalBlocks : o.Pool;
        long incidence = pool * ckt;
        if (incidence > 400_000_000)
        {
            Console.Error.WriteLine($"incidência {incidence:N0} > 400M; reduza --pool (sugestão: {400_000_000 / ckt:N0})");
            return 2;
        }

        Console.WriteLine($"C({v},{k},{t})  targets={totalTargets:N0}  blocos possíveis={totalBlocks:N0}  pool={pool:N0}  incidência={incidence:N0}");
        var sw = Stopwatch.StartNew();

        // ---------- candidatos ----------
        int p = checked((int)pool);
        var candPos = new byte[(long)p * k];
        var candMask = new uint[p];
        GerarCandidatos(v, k, p, totalBlocks, o.Seed, candPos, candMask);
        Console.WriteLine($"candidatos: {p:N0} ({sw.Elapsed.TotalSeconds:F1}s)");

        // ---------- CSR reverso: target mask -> candidatos que o cobrem ----------
        int nMask = 1 << v;
        var end = new int[nMask];
        var buf = new uint[ckt];
        for (int c = 0; c < p; c++)
        {
            int n = Combos(candPos.AsSpan(c * k, k), t, buf);
            for (int i = 0; i < n; i++) end[buf[i]]++;
        }
        for (int m = 1; m < nMask; m++) end[m] += end[m - 1];

        var cursor = (int[])end.Clone();
        var rev = new int[incidence];
        for (int c = 0; c < p; c++)
        {
            int n = Combos(candPos.AsSpan(c * k, k), t, buf);
            for (int i = 0; i < n; i++) rev[--cursor[buf[i]]] = c;
        }
        cursor = null!;
        GC.Collect();
        Console.WriteLine($"CSR reverso: {sw.Elapsed.TotalSeconds:F1}s");

        // ---------- greedy exato ----------
        int maxGain = checked((int)ckt);
        var head = Enumerable.Repeat(-1, maxGain + 1).ToArray();
        var prev = Enumerable.Repeat(-1, p).ToArray();
        var next = Enumerable.Repeat(-1, p).ToArray();
        var gain = Enumerable.Repeat(maxGain, p).ToArray();
        var selecionado = new bool[p];

        void Inserir(int c, int g)
        {
            next[c] = head[g];
            if (head[g] != -1) prev[head[g]] = c;
            head[g] = c;
            prev[c] = -1;
        }

        void Remover(int c, int g)
        {
            int pv = prev[c], nx = next[c];
            if (pv != -1) next[pv] = nx; else head[g] = nx;
            if (nx != -1) prev[nx] = pv;
            prev[c] = -1;
            next[c] = -1;
        }

        for (int c = 0; c < p; c++) Inserir(c, maxGain);

        var covered = new bool[nMask];
        long cobertos = 0;
        var solucao = new List<uint>();
        // Índices de candidatos escolhidos pelo greedy (para o LNS poder removê-los).
        var solucaoIdx = new List<int>();

        void Cobrir(uint m)
        {
            int mi = (int)m;
            if (covered[mi]) return;
            covered[mi] = true;
            cobertos++;
            int ini = mi == 0 ? 0 : end[mi - 1];
            int fim = end[mi];
            for (int j = ini; j < fim; j++)
            {
                int d = rev[j];
                if (selecionado[d]) continue;
                int g = gain[d];
                if (g <= 0) continue;
                Remover(d, g);
                gain[d] = g - 1;
                if (g - 1 > 0) Inserir(d, g - 1);
            }
        }

        // warm start: reaproveita um cover menor (ex.: t-1) como base
        if (o.Warm is not null)
        {
            using var doc = JsonDocument.Parse(File.ReadAllText(o.Warm));
            var arr = doc.RootElement.GetProperty("blocos");
            var pos = new byte[k];
            foreach (var bloco in arr.EnumerateArray())
            {
                uint m = 0;
                foreach (var x in bloco.EnumerateArray()) m |= 1u << (x.GetInt32() - 1);
                int np = Posicoes(m, v, pos);
                if (np != k) throw new InvalidDataException($"bloco warm com {np} dezenas (esperado {k})");
                solucao.Add(m);
                int n = Combos(pos, t, buf);
                for (int i = 0; i < n; i++) Cobrir(buf[i]);
            }
            Console.WriteLine($"warm start: {solucao.Count:N0} blocos, {cobertos:N0}/{totalTargets:N0} cobertos");
        }
        // Blocos do warm start são fixos: o LNS só mexe nos escolhidos pelo greedy.
        int warmCount = solucao.Count;

        int atual = maxGain;
        while (cobertos < totalTargets)
        {
            while (atual > 0 && head[atual] == -1) atual--;
            if (atual <= 0) break;

            int c = head[atual];
            Remover(c, atual);
            selecionado[c] = true;
            solucao.Add(candMask[c]);
            solucaoIdx.Add(c);

            int n = Combos(candPos.AsSpan(c * k, k), t, buf);
            for (int i = 0; i < n; i++) Cobrir(buf[i]);
        }
        Console.WriteLine($"greedy: {solucao.Count:N0} blocos, {cobertos:N0}/{totalTargets:N0} cobertos ({sw.Elapsed.TotalSeconds:F1}s)");

        // ---------- completa alvos que o pool deixou de fora ----------
        var extras = new List<uint>();
        if (cobertos < totalTargets)
        {
            var pos = new byte[k];
            var rng = new Random(o.Seed + 12345);
            for (int m = 0; m < nMask && cobertos < totalTargets; m++)
            {
                if (covered[m] || BitOperations.PopCount((uint)m) != t) continue;
                int np = 0;
                for (int b = 0; b < v; b++) if ((m & (1 << b)) != 0) pos[np++] = (byte)b;
                var usados = new HashSet<byte>(pos.AsSpan(0, np).ToArray());
                while (np < k)
                {
                    byte x = (byte)rng.Next(v);
                    if (usados.Add(x)) pos[np++] = x;
                }
                uint bloco = 0;
                for (int i = 0; i < k; i++) bloco |= 1u << pos[i];
                extras.Add(bloco);

                int n = Combos(pos, t, buf);
                for (int i = 0; i < n; i++)
                {
                    int mi = (int)buf[i];
                    if (!covered[mi]) { covered[mi] = true; cobertos++; }
                }
            }
            Console.WriteLine($"completado com {extras.Count} bloco(s) extra(s)");
        }

        if (cobertos != totalTargets)
        {
            Console.Error.WriteLine($"FALHA: cobertura {cobertos:N0}/{totalTargets:N0}");
            return 1;
        }

        // ---------- LNS / --improve ----------
        // Ruin & recreate: remove alguns blocos, repara com o candidato de maior
        // ganho (buckets incrementais) e aceita se o total diminuiu (ou empatou,
        // com 25% de chance, para diversificar). Custo por iteração é proporcional
        // aos alvos afetados, não ao pool inteiro.
        int lnsIteracoes = 0, lnsMelhorias = 0;
        if (o.ImproveSeconds > 0 && extras.Count == 0 && solucaoIdx.Count > 0)
        {
            var fixosLns = new List<uint>(solucao.Take(warmCount));
            var bestList = new List<int>(solucaoIdx);
            var atualList = new List<int>(solucaoIdx.Count);
            var covCount = new int[nMask];
            var uncovered = new Stack<int>();
            var removidos = new List<int>();
            var adicionados = new List<int>();
            // Tabu: impede re-adicionar os blocos removidos nesta iteração, forçando
            // o reparo a usar combinações diferentes (senão ele reconstrói o mesmo).
            // Array bool (indexado por candidato) é muito mais rápido que HashSet no laço.
            var proibidos = new bool[p];
            var rng = new Random(o.Seed + 909090);
            var tgt = new uint[maxGain];
            var posBuf = new byte[v];

            int EnumerarBloco(uint mask)
            {
                int np = Posicoes(mask, v, posBuf);
                return Combos(posBuf.AsSpan(0, np), t, tgt);
            }

            foreach (var mask in fixosLns)
            {
                int n = EnumerarBloco(mask);
                for (int i = 0; i < n; i++) covCount[(int)tgt[i]]++;
            }
            foreach (var c in bestList)
            {
                int n = EnumerarBloco(candMask[c]);
                for (int i = 0; i < n; i++) covCount[(int)tgt[i]]++;
            }

            // Ganho = quantos alvos ainda descobertos cada candidato cobre.
            // Não usamos mais os buckets do greedy: o reparo é direcionado ao alvo.
            Array.Fill(gain, 0);

            void AjustarGanho(int c, int delta)
            {
                gain[c] += delta;
            }

            void Descoberto(int tm)
            {
                covered[tm] = false;
                uncovered.Push(tm);
                int ini = tm == 0 ? 0 : end[tm - 1];
                int fim = end[tm];
                for (int j = ini; j < fim; j++)
                {
                    int d = rev[j];
                    if (selecionado[d]) continue;
                    AjustarGanho(d, +1);
                }
            }

            void Coberto(int tm)
            {
                if (covered[tm]) return;
                covered[tm] = true;
                int ini = tm == 0 ? 0 : end[tm - 1];
                int fim = end[tm];
                for (int j = ini; j < fim; j++)
                {
                    int d = rev[j];
                    if (selecionado[d]) continue;
                    AjustarGanho(d, -1);
                }
            }

            void RemoverSolucao(int c)
            {
                selecionado[c] = false;
                gain[c] = 0;
                int n = EnumerarBloco(candMask[c]);
                for (int i = 0; i < n; i++)
                {
                    int tm = (int)tgt[i];
                    if (--covCount[tm] == 0) Descoberto(tm);
                }
            }

            void AdicionarSolucao(int c)
            {
                selecionado[c] = true;
                int g = gain[c];
                if (g > 0) Remover(c, g);
                gain[c] = 0;
                int n = EnumerarBloco(candMask[c]);
                for (int i = 0; i < n; i++)
                {
                    int tm = (int)tgt[i];
                    if (covCount[tm]++ == 0) Coberto(tm);
                }
            }

            // Escolhe, entre os candidatos que cobrem `tm`, o de maior ganho.
            // Garante que o alvo retirado da pilha é efetivamente coberto.
            int MelhorParaAlvo(int tm)
            {
                int ini = tm == 0 ? 0 : end[tm - 1];
                int fim = end[tm];
                int melhor = -1, melhorG = 0, segundo = -1, segundoG = 0;
                for (int j = ini; j < fim; j++)
                {
                    int c = rev[j];
                    if (selecionado[c] || proibidos[c]) continue;
                    int g = gain[c];
                    if (g > melhorG)
                    {
                        segundo = melhor; segundoG = melhorG;
                        melhor = c; melhorG = g;
                    }
                    else if (g > segundoG)
                    {
                        segundo = c; segundoG = g;
                    }
                }
                // 20% das vezes usa o segundo melhor: diversifica o reparo.
                if (segundo >= 0 && rng.NextDouble() < 0.2) return segundo;
                return melhor;
            }

            // Sorteia um t-subconjunto uniforme de 1..v (máscara de bits).
            uint RandomMask()
            {
                Span<int> idx = stackalloc int[v];
                for (int i = 0; i < v; i++) idx[i] = i;
                for (int i = 0; i < t; i++)
                {
                    int j = rng.Next(i, v);
                    (idx[i], idx[j]) = (idx[j], idx[i]);
                }
                uint m = 0;
                for (int i = 0; i < t; i++) m |= 1u << idx[i];
                return m;
            }

            var deadline = DateTime.UtcNow.AddSeconds(o.ImproveSeconds);
            int iteracoes = 0, melhorias = 0, iguais = 0, piores = 0;
            int maxRemover = Math.Max(2, Math.Min(32, bestList.Count / 4));
            // Solução corrente (pode piorar para escapar de mínimos locais) e a melhor já vista.
            var currentList = new List<int>(bestList);
            double temperatura = 2.0;

            while (DateTime.UtcNow < deadline)
            {
                iteracoes++;
                int m = rng.Next(1, maxRemover + 1);

                var escolhidos = new HashSet<int>();
                // Dois destroys: alvo único (fino) e multi-alvo (grosso).
                if (rng.NextDouble() < 0.5)
                {
                    for (int tent = 0; tent < 8 && escolhidos.Count == 0; tent++)
                    {
                        int tm = (int)RandomMask();
                        int ini = tm == 0 ? 0 : end[tm - 1];
                        int fim = end[tm];
                        int qtd = 0;
                        for (int j = ini; j < fim; j++)
                            if (selecionado[rev[j]]) qtd++;
                        if (qtd == 0 || qtd > 16) continue;
                        for (int j = ini; j < fim; j++)
                        {
                            int c = rev[j];
                            if (selecionado[c]) escolhidos.Add(c);
                        }
                    }
                }
                else
                {
                    // Multi-alvo: sorteia vários alvos e remove todos os blocos que
                    // os cobrem. Força uma re-cobertura maior, permitindo trocar um
                    // conjunto de blocos por outro menor.
                    int qAlvos = Math.Max(2, Math.Min(16, currentList.Count / 100));
                    for (int tq = 0; tq < qAlvos; tq++)
                    {
                        int tm = (int)RandomMask();
                        int ini = tm == 0 ? 0 : end[tm - 1];
                        int fim = end[tm];
                        for (int j = ini; j < fim; j++)
                        {
                            int c = rev[j];
                            if (selecionado[c]) escolhidos.Add(c);
                        }
                        if (escolhidos.Count > 256) break;
                    }
                }
                if (escolhidos.Count == 0)
                {
                    while (escolhidos.Count < m && escolhidos.Count < currentList.Count)
                        escolhidos.Add(currentList[rng.Next(currentList.Count)]);
                }

                removidos.Clear();
                adicionados.Clear();
                uncovered.Clear();

                atualList.Clear();
                for (int i = 0; i < currentList.Count; i++)
                    if (!escolhidos.Contains(currentList[i])) atualList.Add(currentList[i]);

                foreach (var c in escolhidos)
                {
                    RemoverSolucao(c);
                    removidos.Add(c);
                    proibidos[c] = true;
                }

                // Reparo guloso direcionado: cobre todos os alvos descobertos.
                while (uncovered.Count > 0)
                {
                    int tm = uncovered.Pop();
                    if (covered[tm]) continue;
                    int c = MelhorParaAlvo(tm);
                    if (c < 0) { uncovered.Push(tm); break; }
                    AdicionarSolucao(c);
                    atualList.Add(c);
                    adicionados.Add(c);
                }

                bool completo = true;
                foreach (var tm in uncovered)
                {
                    if (!covered[tm]) { completo = false; break; }
                }

                int delta = atualList.Count - currentList.Count;
                bool aceitar = completo
                    && (delta <= 0 || rng.NextDouble() < Math.Exp(-delta / temperatura));

                if (aceitar)
                {
                    currentList = new List<int>(atualList);
                    if (atualList.Count < bestList.Count)
                    {
                        bestList = new List<int>(atualList);
                        melhorias++;
                        Console.WriteLine(
                            $"  LNS melhoria #{melhorias}: {bestList.Count:N0} blocos " +
                            $"(iter {iteracoes:N0}, T={temperatura:F3})");
                    }
                    else if (delta == 0) iguais++;
                    else piores++;
                }
                else
                {
                    // Reverte as mudanças líquidas: remove os novos, re-adiciona os removidos.
                    var addSet = new HashSet<int>(adicionados);
                    var remSet = new HashSet<int>(removidos);
                    for (int i = adicionados.Count - 1; i >= 0; i--)
                    {
                        int c = adicionados[i];
                        if (!remSet.Contains(c)) RemoverSolucao(c);
                    }
                    foreach (var c in removidos)
                    {
                        if (!addSet.Contains(c)) AdicionarSolucao(c);
                    }
                }

                foreach (var c in removidos) proibidos[c] = false;

                double restante = (deadline - DateTime.UtcNow).TotalSeconds;
                temperatura = Math.Max(0.05, 2.0 * restante / Math.Max(1, o.ImproveSeconds));
            }

            // Verificação exaustiva final do LNS.
            Array.Fill(covered, false);
            foreach (var mask in fixosLns)
            {
                int n = EnumerarBloco(mask);
                for (int i = 0; i < n; i++) covered[(int)tgt[i]] = true;
            }
            foreach (var c in bestList)
            {
                int n = EnumerarBloco(candMask[c]);
                for (int i = 0; i < n; i++) covered[(int)tgt[i]] = true;
            }
            long ver = 0;
            for (int mi = 0; mi < nMask; mi++) if (covered[mi]) ver++;
            if (ver != totalTargets)
            {
                Console.Error.WriteLine($"FALHA LNS: cobertura {ver:N0}/{totalTargets:N0}");
                int mostrados = 0;
                for (int mi = 0; mi < nMask && mostrados < 12; mi++)
                {
                    if (BitOperations.PopCount((uint)mi) != t) continue;
                    if (covered[mi]) continue;
                    Console.Error.WriteLine($"  alvo faltando mask={mi} covCount={covCount[mi]}");
                    mostrados++;
                }
                return 1;
            }

            solucao = fixosLns.Concat(bestList.Select(c => candMask[c])).ToList();
            extras.Clear();
            lnsIteracoes = iteracoes;
            lnsMelhorias = melhorias;
            Console.WriteLine(
                $"LNS: {iteracoes:N0} iterações, {melhorias} melhoria(s), {iguais} empate(s) aceito(s) " +
                $"-> {solucao.Count:N0} blocos ({sw.Elapsed.TotalSeconds:F1}s)");
        }

        // ---------- saída ----------
        var blocos = new int[solucao.Count + extras.Count][];
        int w = 0;
        foreach (var mask in solucao.Concat(extras))
        {
            var arr = new int[k];
            int np = 0;
            for (int b = 0; b < v && np < k; b++) if ((mask & (1u << b)) != 0) arr[np++] = b + 1;
            Array.Sort(arr);
            blocos[w++] = arr;
        }

        long lb = LimiteInferior(v, k, t);
        var dto = new
        {
            v, k, t,
            blocos,
            fonte = o.ImproveSeconds > 0
                ? "LotoScope covergen (.NET, greedy exato + CSR + LNS)"
                : "LotoScope covergen (.NET, greedy exato + CSR)",
            limiteInferior = lb,
            verificado = true,
            pool,
            improveSegundos = o.ImproveSeconds,
            iteracoesLns = lnsIteracoes,
            melhoriasLns = lnsMelhorias,
            tempoSegundos = Math.Round(sw.Elapsed.TotalSeconds, 1),
        };
        var json = JsonSerializer.Serialize(dto);
        if (o.Out is not null) File.WriteAllText(o.Out, json);
        else Console.WriteLine(json);

        Console.WriteLine($"OK: {blocos.Length:N0} blocos | LB={lb:N0} | {blocos.Length / (double)lb:F2}x | {sw.Elapsed.TotalSeconds:F1}s");
        return 0;
    }

    // ---------------- helpers ----------------

    private static int Posicoes(uint mask, int v, Span<byte> pos)
    {
        int np = 0;
        for (int b = 0; b < v; b++) if ((mask & (1u << b)) != 0) pos[np++] = (byte)b;
        return np;
    }

    private static int Combos(ReadOnlySpan<byte> pos, int t, Span<uint> outBuf)
    {
        int k = pos.Length;
        Span<int> comb = stackalloc int[t];
        for (int i = 0; i < t; i++) comb[i] = i;
        int idx = 0;
        while (true)
        {
            uint m = 0;
            for (int i = 0; i < t; i++) m |= 1u << pos[comb[i]];
            outBuf[idx++] = m;
            int j = t - 1;
            while (j >= 0 && comb[j] == k - t + j) j--;
            if (j < 0) break;
            comb[j]++;
            for (int i = j + 1; i < t; i++) comb[i] = comb[i - 1] + 1;
        }
        return idx;
    }

    private static void GerarCandidatos(int v, int k, int p, long totalBlocks, int seed, byte[] candPos, uint[] candMask)
    {
        if (p >= totalBlocks)
        {
            // todos os k-subconjuntos
            var comb = new int[k];
            for (int i = 0; i < k; i++) comb[i] = i;
            int c = 0;
            while (c < p)
            {
                uint m = 0;
                for (int i = 0; i < k; i++) { candPos[(long)c * k + i] = (byte)comb[i]; m |= 1u << comb[i]; }
                candMask[c] = m;
                c++;
                int j = k - 1;
                while (j >= 0 && comb[j] == v - k + j) j--;
                if (j < 0) break;
                comb[j]++;
                for (int i = j + 1; i < k; i++) comb[i] = comb[i - 1] + 1;
            }
            return;
        }

        var rng = new Random(seed);
        var perm = new int[v];
        for (int i = 0; i < v; i++) perm[i] = i;
        var vistos = new HashSet<uint>();
        int n = 0;
        while (n < p)
        {
            for (int i = 0; i < k; i++)
            {
                int j = rng.Next(i, v);
                (perm[i], perm[j]) = (perm[j], perm[i]);
            }
            uint m = 0;
            for (int i = 0; i < k; i++) m |= 1u << perm[i];
            if (!vistos.Add(m)) continue;
            for (int i = 0; i < k; i++) candPos[(long)n * k + i] = (byte)perm[i];
            candMask[n] = m;
            n++;
        }
    }

    private static long Binom(int n, int r)
    {
        if (r < 0 || r > n) return 0;
        long x = 1;
        for (int i = 0; i < r; i++) x = x * (n - i) / (i + 1);
        return x;
    }

    private static long LimiteInferior(int v, int k, int t)
    {
        if (t <= 0 || k <= 0 || v <= 0 || k > v) return 0;
        if (t == 1) return (v + k - 1) / k;
        return (long)Math.Ceiling((double)v / k * LimiteInferior(v - 1, k - 1, t - 1));
    }

    private sealed record Options(int V, int K, int T, int Pool, int Seed, int ImproveSeconds, string? Warm, string? Out)
    {
        public static Options? Parse(string[] a)
        {
            int v = 25, k = 15, t = 9, pool = 15000, seed = 1, improve = 0;
            string? warm = null, output = null;
            for (int i = 0; i < a.Length; i++)
            {
                string key = a[i];
                string Next() => i + 1 < a.Length ? a[++i] : throw new ArgumentException(key);
                switch (key)
                {
                    case "--v": v = int.Parse(Next()); break;
                    case "--k": k = int.Parse(Next()); break;
                    case "--t": t = int.Parse(Next()); break;
                    case "--pool": pool = int.Parse(Next()); break;
                    case "--seed": seed = int.Parse(Next()); break;
                    case "--improve": improve = Math.Max(0, int.Parse(Next())); break;
                    case "--warm": warm = Next(); break;
                    case "--out": output = Next(); break;
                    default: return null;
                }
            }
            return new Options(v, k, t, pool, seed, improve, warm, output);
        }
    }
}
