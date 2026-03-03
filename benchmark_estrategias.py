"""
Benchmark de Estratégias Alternativas de Exclusão
Compara várias abordagens para identificar qual funciona melhor nos últimos concursos
"""
import pyodbc
import random
from collections import Counter
from math import comb

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def load_data():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute('SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 FROM Resultados_INT ORDER BY Concurso ASC')
    resultados = {}
    for row in cursor.fetchall():
        resultados[row[0]] = {'concurso': row[0], 'numeros': list(row[1:16]), 'set': set(row[1:16])}
    conn.close()
    return resultados

def freq_janela(dados, tam):
    freq = Counter()
    for r in dados[:min(tam, len(dados))]:
        freq.update(r['numeros'])
    return {n: freq.get(n, 0) / min(tam, len(dados)) * 100 for n in range(1, 26)}

def estrategia_atual(hist):
    """Estrategia SUPERAVIT v2.0 atual"""
    freq_5 = freq_janela(hist, 5)
    freq_50 = freq_janela(hist, 50)
    cand = []
    for n in range(1, 26):
        fc, fl = freq_5[n], freq_50[n]
        idx = fl - fc
        score = 0
        rec = any(n in r['numeros'] for r in hist[:3])
        if rec: score -= 10
        elif idx < -40 and fc >= 80: score += 5
        elif idx < -30 and not rec: score += 4
        elif idx < -20 and not rec: score += 3
        elif idx < -10: score += 2
        elif idx > 35: score += 4
        elif idx > 20 and fc < 40: score += 3
        cand.append((n, score, fc))
    cand.sort(key=lambda x: (-x[1], x[2]))
    return [c[0] for c in cand[:2]]

def estrategia_invertida(hist):
    """INVERSO: excluir numeros QUENTES que devem esfriar"""
    freq_5 = freq_janela(hist, 5)
    freq_50 = freq_janela(hist, 50)
    cand = []
    for n in range(1, 26):
        fc, fl = freq_5[n], freq_50[n]
        idx = fl - fc
        score = 0
        rec = any(n in r['numeros'] for r in hist[:3])
        # Preferir numeros QUENTES (que devem esfriar)
        if rec and fc >= 80: score += 5  # saiu recente E muito frequente
        elif fc >= 100: score += 4  # saiu em todos os ultimos 5
        elif idx < -30: score += 3  # superavitario extremo
        elif idx < -20: score += 2
        cand.append((n, score, fc))
    cand.sort(key=lambda x: (-x[1], -x[2]))
    return [c[0] for c in cand[:2]]

def estrategia_freq_alta(hist):
    """Excluir numeros com frequencia MUITO alta recente"""
    freq_5 = freq_janela(hist, 5)
    cand = [(n, freq_5[n]) for n in range(1, 26)]
    cand.sort(key=lambda x: -x[1])
    return [c[0] for c in cand[:2]]

def estrategia_consecutivo(hist):
    """Excluir numeros que sairam 3+ vezes consecutivas"""
    consec = {}
    for n in range(1, 26):
        count = 0
        for r in hist[:10]:
            if n in r['numeros']:
                count += 1
            else:
                break
        consec[n] = count
    cand = [(n, consec[n]) for n in range(1, 26)]
    cand.sort(key=lambda x: (-x[1], x[0]))
    return [c[0] for c in cand[:2]]

def estrategia_neutro(hist):
    """Excluir numeros com frequencia mais NEUTRA (sem tendencia clara)"""
    freq_5 = freq_janela(hist, 5)
    freq_50 = freq_janela(hist, 50)
    cand = []
    for n in range(1, 26):
        fc, fl = freq_5[n], freq_50[n]
        idx = abs(fl - fc)
        cand.append((n, idx, fc))
    cand.sort(key=lambda x: (x[1], x[2]))
    return [c[0] for c in cand[:2]]

def estrategia_combinada_v2(hist):
    """Nova estrategia: combina consecutivo + inversao"""
    freq_5 = freq_janela(hist, 5)
    freq_50 = freq_janela(hist, 50)
    cand = []
    for n in range(1, 26):
        fc, fl = freq_5[n], freq_50[n]
        idx = fl - fc
        
        consec = 0
        for r in hist[:10]:
            if n in r['numeros']:
                consec += 1
            else:
                break
        
        score = 0
        if consec >= 4: score += 5
        elif consec >= 3 and fc >= 80: score += 4
        elif idx < -35 and consec >= 2: score += 3
        
        cand.append((n, score, consec, fc))
    cand.sort(key=lambda x: (-x[1], -x[2], -x[3]))
    return [c[0] for c in cand[:2]]

def estrategia_ausencia_longa(hist):
    """Excluir numeros com ausencia MUITO longa (>8 concursos)"""
    ausencia = {}
    for n in range(1, 26):
        for i, r in enumerate(hist[:15]):
            if n in r['numeros']:
                ausencia[n] = i
                break
        else:
            ausencia[n] = 15  # Nao apareceu nos ultimos 15
    
    cand = [(n, ausencia[n]) for n in range(1, 26)]
    cand.sort(key=lambda x: -x[1])  # maior ausencia primeiro
    return [c[0] for c in cand[:2]]

def estrategia_ciclo_retorno(hist):
    """Baseado em ciclos: numeros que acabaram de voltar tendem a sair de novo"""
    # Excluir numeros que NAO voltaram recentemente
    freq_3 = freq_janela(hist, 3)
    freq_10 = freq_janela(hist, 10)
    freq_30 = freq_janela(hist, 30)
    
    cand = []
    for n in range(1, 26):
        f3, f10, f30 = freq_3[n], freq_10[n], freq_30[n]
        
        # Score alto = candidato a exclusao
        score = 0
        
        # Numero que NAO saiu recente e esta abaixo da media
        if f3 == 0 and f10 < 50:
            score += 3
        if f10 < 40 and f30 < 50:
            score += 2
        # Numero que saiu muito e deve esfriar
        if f3 >= 100:  # saiu em todos os ultimos 3
            score += 1
            
        cand.append((n, score, f3))
    cand.sort(key=lambda x: (-x[1], x[2]))
    return [c[0] for c in cand[:2]]

if __name__ == '__main__':
    random.seed(42)
    resultados = load_data()
    concursos = sorted(resultados.keys())
    
    estrategias = {
        'ATUAL (superavit)': estrategia_atual,
        'INVERTIDA (quentes)': estrategia_invertida,
        'FREQ ALTA (top 2)': estrategia_freq_alta,
        'CONSECUTIVO (3+)': estrategia_consecutivo,
        'NEUTRO': estrategia_neutro,
        'COMBINADA v2': estrategia_combinada_v2,
        'AUSENCIA LONGA': estrategia_ausencia_longa,
        'CICLO RETORNO': estrategia_ciclo_retorno,
    }
    
    print('='*75)
    print('BENCHMARK DE ESTRATEGIAS ALTERNATIVAS - Ultimos 200 concursos')
    print('='*75)
    print(f'Prob. Teorica: {comb(10,2)/comb(25,2)*100:.1f}%')
    print()
    
    testes = concursos[-200:]
    results = {name: {'ok': 0, 'total': 0} for name in estrategias}
    
    for c in testes:
        if c not in resultados:
            continue
        dados_hist = [resultados[x] for x in concursos if x < c]
        dados_hist.sort(key=lambda x: x['concurso'], reverse=True)
        if len(dados_hist) < 50:
            continue
        
        res_real = resultados[c]['set']
        
        for name, func in estrategias.items():
            excl = func(dados_hist)
            results[name]['total'] += 1
            if not any(n in res_real for n in excl):
                results[name]['ok'] += 1
    
    # Aleatorio
    ale_ok = 0
    ale_total = results['ATUAL (superavit)']['total']
    for c in testes:
        if c not in resultados:
            continue
        dados_hist = [resultados[x] for x in concursos if x < c]
        if len(dados_hist) < 50:
            continue
        res_real = resultados[c]['set']
        ok = sum(1 for _ in range(100) if not any(n in res_real for n in random.sample(range(1,26),2)))
        ale_ok += ok/100
    
    print(f'{"Estrategia":<30} {"Acertos":>10} {"Taxa":>10} {"vs Ale":>10}')
    print('-'*75)
    
    taxa_ale = ale_ok / ale_total * 100
    print(f'{"ALEATORIO (baseline)":<30} {ale_ok:.0f}/{ale_total:>6} {taxa_ale:>9.1f}%        --')
    
    for name in sorted(results.keys(), key=lambda x: -results[x]['ok']/max(1,results[x]['total'])):
        r = results[name]
        taxa = r['ok'] / r['total'] * 100 if r['total'] > 0 else 0
        dif = taxa - taxa_ale
        sinal = '+' if dif > 0 else ''
        print(f'{name:<30} {r["ok"]:>4}/{r["total"]:>6} {taxa:>9.1f}% {sinal}{dif:>8.1f}pp')
    
    print()
    print('='*75)
    print('ANALISE TEMPORAL - Por periodos de 50 concursos')
    print('='*75)
    
    # Analisar por janelas temporais
    for start_offset in [200, 150, 100, 50]:
        end_offset = start_offset - 50
        window = concursos[-start_offset:-end_offset] if end_offset > 0 else concursos[-start_offset:]
        
        w_results = {name: {'ok': 0, 'total': 0} for name in estrategias}
        
        for c in window:
            if c not in resultados:
                continue
            dados_hist = [resultados[x] for x in concursos if x < c]
            dados_hist.sort(key=lambda x: x['concurso'], reverse=True)
            if len(dados_hist) < 50:
                continue
            
            res_real = resultados[c]['set']
            
            for name, func in estrategias.items():
                excl = func(dados_hist)
                w_results[name]['total'] += 1
                if not any(n in res_real for n in excl):
                    w_results[name]['ok'] += 1
        
        print(f'\nPeriodo: -{start_offset} a -{end_offset if end_offset > 0 else 0} ({window[0]}-{window[-1]})')
        best = max(w_results.items(), key=lambda x: x[1]['ok']/max(1,x[1]['total']))
        worst = min(w_results.items(), key=lambda x: x[1]['ok']/max(1,x[1]['total']))
        
        best_taxa = best[1]['ok']/best[1]['total']*100
        worst_taxa = worst[1]['ok']/worst[1]['total']*100
        
        print(f'  MELHOR:  {best[0]:<25} {best[1]["ok"]}/{best[1]["total"]} = {best_taxa:.1f}%')
        print(f'  PIOR:    {worst[0]:<25} {worst[1]["ok"]}/{worst[1]["total"]} = {worst_taxa:.1f}%')
