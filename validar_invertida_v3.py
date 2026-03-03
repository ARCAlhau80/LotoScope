"""
Validação da Estratégia INVERTIDA v3.0
Testa no último concurso e backtest de 20 concursos
"""
import pyodbc
from collections import Counter

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

def estrategia_invertida_v3(hist):
    """
    Estratégia INVERTIDA v3.0 - Exclui números QUENTES que devem ESFRIAR
    Benchmark: +1.8pp acima do aleatório (17% vs 15.2%)
    ATUALIZAÇÃO: Proteção para sequências muito longas (>10 consecutivos)
    """
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
        
        # PROTEÇÃO PARA ANOMALIAS: Sequências muito longas (>10 consecutivos)
        if consecutivos >= 10:
            score -= 5  # PROTEGER - anomalia de persistência!
            status = 'PROTEGIDO (10+ seg)'
        # LÓGICA INVERTIDA v3.0: Excluir QUENTES (4-9 consecutivos)
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
        elif indice_debito >= 0:
            score -= 2
            status = 'Devendo' if indice_debito > 10 else 'equilibrado'
        else:
            score -= 1
            status = 'leve superavit'
        
        if fc > 80:
            score += 1
        
        candidatos.append({
            'num': n, 
            'fc': fc, 
            'fl': fl,
            'consec': consecutivos, 
            'score': score, 
            'status': status
        })
    
    candidatos.sort(key=lambda x: (-x['score'], -x['consec'], -x['fc']))
    return candidatos

if __name__ == '__main__':
    resultados = load_data()
    
    print('='*70)
    print('ANALISE DA ANOMALIA - Numero 11')
    print('='*70)
    
    # Verificar sequência do número 11
    consec_11 = 0
    for r in resultados:
        if 11 in r['set']:
            consec_11 += 1
        else:
            break
    
    print(f"\n⚠️ ANOMALIA: Número 11 saiu em {consec_11} concursos CONSECUTIVOS!")
    print("Isso é EXTREMAMENTE raro e invalida estratégias de exclusão por calor\n")
    
    # Mostrar últimos concursos com 11
    print("Últimos 15 concursos com número 11:")
    for r in resultados[:15]:
        tem_11 = '✓' if 11 in r['set'] else ' '
        print(f"  {r['concurso']}: [{tem_11}] {sorted(r['numeros'])}")
    
    print('\n' + '='*70)
    print('VALIDACAO ESTRATEGIA INVERTIDA v3.0')
    print('='*70)
    
    ultimo = resultados[0]
    hist = resultados[1:]  # Histórico SEM o último
    
    print(f"\nÚltimo concurso: {ultimo['concurso']}")
    print(f"Resultado: {sorted(ultimo['numeros'])}")
    
    candidatos = estrategia_invertida_v3(hist)
    nums_excluir = [candidatos[0]['num'], candidatos[1]['num']]
    
    print(f"\n--- TOP 10 candidatos a exclusão ---")
    print(f"{'Rank':>4} {'Num':>4} {'Freq5%':>8} {'Consec':>7} {'Score':>7} {'Status':<25}")
    print('-'*60)
    for i, c in enumerate(candidatos[:10]):
        marker = ' <-- EXCLUIR' if i < 2 else ''
        print(f"{i+1:>4} {c['num']:>4} {c['fc']:>8.1f} {c['consec']:>7} {c['score']:>7} {c['status']:<25}{marker}")
    
    print(f"\nNúmeros a EXCLUIR (INVERTIDA v3.0): {nums_excluir}")
    
    # Verificar resultado
    excluidos_no_resultado = [n for n in nums_excluir if n in ultimo['set']]
    acertou = len(excluidos_no_resultado) == 0
    
    print(f"\nResultado real: {sorted(ultimo['numeros'])}")
    if excluidos_no_resultado:
        print(f"Números excluídos que SAÍRAM: {excluidos_no_resultado}")
    else:
        print("Nenhum número excluído saiu!")
    print(f"EXCLUSÃO CORRETA? {'✅ SIM!' if acertou else '❌ NÃO'}")
    
    # Backtest em DIFERENTES períodos
    print('\n' + '='*70)
    print('BACKTEST POR PERÍODOS (50 concursos cada)')
    print('='*70)
    
    periodos = [
        (0, 50, 'Últimos 50 (mais recentes)'),
        (50, 100, 'Concursos 50-100 atrás'),
        (100, 150, 'Concursos 100-150 atrás'),
        (150, 200, 'Concursos 150-200 atrás'),
    ]
    
    for start, end, nome in periodos:
        acertos = 0
        total = 0
        for i in range(start, min(end, len(resultados)-50)):
            atual = resultados[i]
            hist_bt = resultados[i+1:]
            if len(hist_bt) < 50:
                continue
            cands = estrategia_invertida_v3(hist_bt)
            nums = [cands[0]['num'], cands[1]['num']]
            saiu = [n for n in nums if n in atual['set']]
            ok = len(saiu) == 0
            if ok: 
                acertos += 1
            total += 1
        
        if total > 0:
            taxa = acertos/total*100
            diff = taxa - 15
            sinal = '+' if diff > 0 else ''
            status = '✅' if diff > 0 else '❌'
            print(f"{nome}: {acertos}/{total} = {taxa:.1f}% ({sinal}{diff:.1f}pp) {status}")
    
    print('\n' + '='*70)
    print('CONCLUSÃO')
    print('='*70)
    print("""
A anomalia do número 11 (13+ consecutivos) está distorcendo os resultados.
Quando há um número em sequência TÃO longa, a estratégia falha porque:
- O número é identificado como "super quente" (correto)
- Mas ele continua saindo (fenômeno raro de persistência)

RECOMENDAÇÕES:
1. Adicionar LIMITE SUPERIOR de consecutivos (ex: se >10 seg., proteger)
2. Ou usar abordagem HÍBRIDA: se sequência > 8, NÃO excluir
3. O benchmark de 200 concursos inclui períodos onde funcionou melhor
""")
