"""
Benchmark: Estratégia HÍBRIDA (1 Quente + 1 Frio)
Compara com estratégia atual (2 Quentes) e aleatório
"""
import pyodbc
from collections import Counter
from math import comb

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def load_data():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute('SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 FROM Resultados_INT ORDER BY Concurso DESC')
    resultados = []
    for row in cursor.fetchall():
        resultados.append({'concurso': row[0], 'numeros': list(row[1:16]), 'set': set(row[1:16])})
    conn.close()
    return resultados

def freq_janela(dados, tam):
    freq = Counter()
    for r in dados[:min(tam, len(dados))]:
        freq.update(r['numeros'])
    return {n: freq.get(n, 0) / min(tam, len(dados)) * 100 for n in range(1, 26)}

def contar_consecutivos(n, hist):
    count = 0
    for r in hist[:15]:
        if n in r['numeros']:
            count += 1
        else:
            break
    return count

def contar_ausencias(n, hist):
    """Conta quantos concursos seguidos o número está AUSENTE"""
    count = 0
    for r in hist[:15]:
        if n not in r['numeros']:
            count += 1
        else:
            break
    return count

def ranking_quentes(hist):
    """Ranking de números QUENTES (candidatos a esfriar) - INVERTIDA v3.0"""
    freq_5 = freq_janela(hist, 5)
    freq_50 = freq_janela(hist, 50)
    
    candidatos = []
    for n in range(1, 26):
        fc = freq_5[n]
        fl = freq_50[n]
        indice_debito = fl - fc
        consecutivos = contar_consecutivos(n, hist)
        apareceu_recente = any(n in r['numeros'] for r in hist[:3])
        
        score = 0
        status = ''
        
        # PROTEÇÃO: Sequências muito longas (>10)
        if consecutivos >= 10:
            score -= 5
            status = 'PROTEGIDO (10+ seg)'
        elif consecutivos >= 5:
            score += 6
            status = 'SUPER QUENTE (5+ seg)'
        elif consecutivos >= 4:
            score += 5
            status = 'MUITO QUENTE (4 seg)'
        elif consecutivos >= 3 and fc >= 80:
            score += 4
            status = 'QUENTE (3+ seg, freq)'
        elif consecutivos >= 3:
            score += 3
            status = 'QUENTE (3 seg)'
        elif fc >= 100:
            score += 4
            status = '100% ultimos 5'
        elif fc >= 80 and apareceu_recente:
            score += 3
            status = 'Freq muito alta'
        elif indice_debito < -35:
            score += 2
            status = 'Superavit extremo'
        elif indice_debito < -25:
            score += 1
            status = 'Superavit'
        else:
            score -= 1
            status = 'normal'
        
        if fc > 80:
            score += 1
        
        candidatos.append({
            'num': n, 
            'score': score, 
            'consec': consecutivos,
            'fc': fc,
            'status': status,
            'tipo': 'QUENTE'
        })
    
    candidatos.sort(key=lambda x: (-x['score'], -x['consec'], -x['fc']))
    return candidatos

def ranking_frios(hist):
    """Ranking de números FRIOS (antigo SUPERÁVIT - candidatos a NÃO sair)"""
    freq_5 = freq_janela(hist, 5)
    freq_50 = freq_janela(hist, 50)
    
    candidatos = []
    for n in range(1, 26):
        fc = freq_5[n]
        fl = freq_50[n]
        indice_debito = fl - fc  # positivo = devendo, negativo = adiantado
        ausencias = contar_ausencias(n, hist)
        apareceu_recente = any(n in r['numeros'] for r in hist[:3])
        
        score = 0
        status = ''
        
        # Números FRIOS (muito tempo sem sair + baixa freq recente)
        if ausencias >= 8:
            score += 5
            status = 'MUITO FRIO (8+ ausente)'
        elif ausencias >= 5 and fc <= 20:
            score += 4
            status = 'FRIO (5+ aus, freq baixa)'
        elif ausencias >= 4:
            score += 3
            status = 'FRIO (4 ausente)'
        elif fc == 0:  # Não saiu nos últimos 5
            score += 4
            status = '0% últimos 5'
        elif fc <= 20 and not apareceu_recente:
            score += 2
            status = 'Freq muito baixa'
        # Números em débito alto que deveriam voltar - PROTEGER
        elif indice_debito > 30:
            score -= 3
            status = 'DÉBITO ALTO (vai voltar)'
        elif indice_debito > 15:
            score -= 2
            status = 'Débito (provável volta)'
        else:
            score -= 1
            status = 'normal'
        
        candidatos.append({
            'num': n, 
            'score': score, 
            'ausencias': ausencias,
            'fc': fc,
            'indice': indice_debito,
            'status': status,
            'tipo': 'FRIO'
        })
    
    candidatos.sort(key=lambda x: (-x['score'], -x['ausencias'], x['fc']))
    return candidatos

def estrategia_2_quentes(hist):
    """Estratégia atual: excluir 2 QUENTES"""
    rank = ranking_quentes(hist)
    return [rank[0]['num'], rank[1]['num']]

def estrategia_hibrida(hist):
    """NOVA: Excluir 1 QUENTE + 1 FRIO"""
    quentes = ranking_quentes(hist)
    frios = ranking_frios(hist)
    
    # Pegar o mais quente (que não seja o mesmo que o mais frio)
    quente = quentes[0]['num']
    
    # Pegar o mais frio (que não seja o mesmo que o quente)
    for f in frios:
        if f['num'] != quente:
            frio = f['num']
            break
    else:
        frio = frios[0]['num']
    
    return [quente, frio]

def estrategia_2_frios(hist):
    """Estratégia antiga: excluir 2 FRIOS"""
    rank = ranking_frios(hist)
    return [rank[0]['num'], rank[1]['num']]

if __name__ == '__main__':
    import random
    random.seed(42)
    
    resultados = load_data()
    
    print('='*75)
    print('BENCHMARK: ESTRATÉGIA HÍBRIDA (1 Quente + 1 Frio)')
    print('='*75)
    print(f'Probabilidade teórica de acerto: {comb(10,2)/comb(25,2)*100:.1f}%')
    print()
    
    # Mostrar o que seria excluído AGORA
    hist = resultados[1:]
    
    quentes = ranking_quentes(hist)
    frios = ranking_frios(hist)
    
    print('─'*75)
    print('SITUAÇÃO ATUAL (dados até concurso', resultados[0]['concurso'], ')')
    print('─'*75)
    
    print('\n📈 TOP 5 QUENTES (candidatos a exclusão - vão esfriar):')
    print(f"{'#':>3} {'Num':>4} {'Freq5%':>8} {'Consec':>7} {'Score':>7} {'Status':<25}")
    for i, c in enumerate(quentes[:5]):
        print(f"{i+1:>3} {c['num']:>4} {c['fc']:>8.1f} {c['consec']:>7} {c['score']:>7} {c['status']:<25}")
    
    print('\n📉 TOP 5 FRIOS (candidatos a exclusão - vão continuar fora):')
    print(f"{'#':>3} {'Num':>4} {'Freq5%':>8} {'Ausênc':>7} {'Score':>7} {'Status':<25}")
    for i, c in enumerate(frios[:5]):
        print(f"{i+1:>3} {c['num']:>4} {c['fc']:>8.1f} {c['ausencias']:>7} {c['score']:>7} {c['status']:<25}")
    
    excl_atual = estrategia_2_quentes(hist)
    excl_hibrida = estrategia_hibrida(hist)
    excl_frios = estrategia_2_frios(hist)
    
    print('\n' + '─'*75)
    print('COMPARAÇÃO DE ESTRATÉGIAS:')
    print('─'*75)
    print(f'  🔥 2 QUENTES (atual):  {excl_atual}')
    print(f'  🔀 HÍBRIDA (1+1):      {excl_hibrida}')
    print(f'  ❄️  2 FRIOS (antigo):   {excl_frios}')
    
    # Benchmark por períodos
    print('\n' + '='*75)
    print('BACKTEST POR PERÍODOS (50 concursos cada)')
    print('='*75)
    
    estrategias = {
        '2 QUENTES (atual)': estrategia_2_quentes,
        'HÍBRIDA (1+1)': estrategia_hibrida,
        '2 FRIOS (antigo)': estrategia_2_frios,
    }
    
    periodos = [
        (0, 50, 'Últimos 50'),
        (50, 100, '50-100 atrás'),
        (100, 150, '100-150 atrás'),
        (150, 200, '150-200 atrás'),
    ]
    
    resultados_por_periodo = {nome: {} for nome in estrategias}
    
    for start, end, periodo_nome in periodos:
        print(f'\n{periodo_nome}:')
        print(f"  {'Estratégia':<20} {'Acertos':>10} {'Taxa':>10} {'vs Ale':>10}")
        print('  ' + '-'*55)
        
        # Aleatório primeiro
        ale_ok = 0
        ale_total = 0
        for i in range(start, min(end, len(resultados)-50)):
            atual = resultados[i]
            hist_bt = resultados[i+1:]
            if len(hist_bt) < 50:
                continue
            ale_total += 1
            ok = sum(1 for _ in range(100) if not any(n in atual['set'] for n in random.sample(range(1,26),2)))
            ale_ok += ok/100
        
        taxa_ale = ale_ok / ale_total * 100 if ale_total > 0 else 15
        print(f"  {'ALEATÓRIO':<20} {ale_ok:.0f}/{ale_total:>6} {taxa_ale:>9.1f}%        --")
        
        # Cada estratégia
        for nome, func in estrategias.items():
            acertos = 0
            total = 0
            for i in range(start, min(end, len(resultados)-50)):
                atual = resultados[i]
                hist_bt = resultados[i+1:]
                if len(hist_bt) < 50:
                    continue
                total += 1
                excl = func(hist_bt)
                if not any(n in atual['set'] for n in excl):
                    acertos += 1
            
            if total > 0:
                taxa = acertos / total * 100
                diff = taxa - taxa_ale
                sinal = '+' if diff > 0 else ''
                status = '✅' if diff > 2 else ('⚠️' if diff > 0 else '❌')
                print(f"  {nome:<20} {acertos:>4}/{total:>6} {taxa:>9.1f}% {sinal}{diff:>8.1f}pp {status}")
                resultados_por_periodo[nome][periodo_nome] = taxa
    
    # Resumo geral
    print('\n' + '='*75)
    print('RESUMO GERAL (média de todos os períodos)')
    print('='*75)
    
    for nome in estrategias:
        taxas = list(resultados_por_periodo[nome].values())
        if taxas:
            media = sum(taxas) / len(taxas)
            diff = media - 15
            sinal = '+' if diff > 0 else ''
            print(f"  {nome:<20}: {media:.1f}% ({sinal}{diff:.1f}pp vs aleatório)")
    
    print('\n' + '='*75)
    print('CONCLUSÃO')
    print('='*75)
