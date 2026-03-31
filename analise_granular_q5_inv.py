# -*- coding: utf-8 -*-
"""
Análise Granular: Q5 vs INVERTIDA em períodos CURTOS
=====================================================
Testa: 5, 10, 15, 20, 30, 50 concursos

Data: 28/03/2026
"""

import pyodbc
from collections import defaultdict

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def obter_todos_concursos():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def calcular_frequencia(concursos):
    freq = defaultdict(int)
    for row in concursos:
        nums = [row[i] for i in range(1, 16)]
        for n in nums:
            freq[n] += 1
    return dict(freq)

def calcular_consecutivas(concursos):
    """Quantas vezes consecutivas cada número apareceu (do mais recente)"""
    consecutivas = {}
    for n in range(1, 26):
        count = 0
        for row in concursos:
            nums = set([row[i] for i in range(1, 16)])
            if n in nums:
                count += 1
            else:
                break
        consecutivas[n] = count
    return consecutivas

def estrategia_q5_frios(freq_dict):
    """Exclui os 2 MENOS frequentes"""
    ordenado = sorted(range(1, 26), key=lambda x: freq_dict.get(x, 0))
    return ordenado[:2]

def estrategia_invertida_quentes(freq_dict, consecutivas):
    """Exclui os 2 MAIS quentes (freq alta + consecutivas)"""
    max_freq = max(freq_dict.values()) if freq_dict else 1
    
    scores = {}
    for n in range(1, 26):
        freq_norm = freq_dict.get(n, 0) / max_freq
        consec = consecutivas.get(n, 0)
        # Proteção anomalia: se >10 consecutivas, score negativo (protege)
        if consec >= 10:
            scores[n] = -1
        else:
            scores[n] = freq_norm + (consec / 10)
    
    ordenado = sorted(range(1, 26), key=lambda x: scores[x], reverse=True)
    return ordenado[:2]

def backtest_periodo(concursos, n_teste, janela=100):
    """
    Walk-forward backtest para período específico
    """
    resultados = {
        'Q5_frios': 0,
        'INVERTIDA': 0,
    }
    
    for i in range(n_teste):
        # Concurso a testar (do mais recente para trás)
        idx_teste = i
        
        # Histórico = concursos anteriores a este
        historico = concursos[idx_teste+1:idx_teste+1+janela]
        
        if len(historico) < 30:
            continue
        
        # Resultado real
        atual = concursos[idx_teste]
        sorteio = set([atual[j] for j in range(1, 16)])
        
        # Calcula estratégias
        freq = calcular_frequencia(historico)
        consec = calcular_consecutivas(historico)
        
        # Q5: exclui menos frequentes
        excluir_q5 = estrategia_q5_frios(freq)
        jackpot_q5 = len(set(excluir_q5) & sorteio) == 0
        
        # INVERTIDA: exclui mais quentes
        excluir_inv = estrategia_invertida_quentes(freq, consec)
        jackpot_inv = len(set(excluir_inv) & sorteio) == 0
        
        resultados['Q5_frios'] += int(jackpot_q5)
        resultados['INVERTIDA'] += int(jackpot_inv)
    
    return resultados, n_teste

def main():
    print("=" * 70)
    print("🔬 ANÁLISE GRANULAR: Q5 vs INVERTIDA (períodos curtos)")
    print("=" * 70)
    
    concursos = obter_todos_concursos()
    print(f"\n📊 Total de concursos: {len(concursos)}")
    print(f"   Mais recente: {concursos[0][0]}")
    
    # Períodos a testar
    periodos = [5, 10, 15, 20, 30, 50, 100, 200]
    
    print("\n" + "=" * 70)
    print(f"{'Período':<12} {'Q5 (frios)':>12} {'INVERTIDA':>12} {'Vencedor':>15} {'Diff':>10}")
    print("=" * 70)
    
    resumo = []
    
    for n in periodos:
        resultados, total = backtest_periodo(concursos, n)
        
        taxa_q5 = resultados['Q5_frios'] / total * 100
        taxa_inv = resultados['INVERTIDA'] / total * 100
        diff = taxa_q5 - taxa_inv
        
        if taxa_q5 > taxa_inv:
            vencedor = "Q5 ✅"
        elif taxa_inv > taxa_q5:
            vencedor = "INVERTIDA ✅"
        else:
            vencedor = "EMPATE"
        
        print(f"Últimos {n:<4} {taxa_q5:>10.1f}% ({resultados['Q5_frios']}) {taxa_inv:>10.1f}% ({resultados['INVERTIDA']}) {vencedor:>15} {diff:>+9.1f}pp")
        
        resumo.append({
            'periodo': n,
            'q5': taxa_q5,
            'inv': taxa_inv,
            'vencedor': 'Q5' if taxa_q5 > taxa_inv else ('INV' if taxa_inv > taxa_q5 else 'EMP')
        })
    
    # Análise de tendência
    print("\n" + "=" * 70)
    print("📊 ANÁLISE DE TENDÊNCIA:")
    print("=" * 70)
    
    vitorias_q5 = sum(1 for r in resumo if r['vencedor'] == 'Q5')
    vitorias_inv = sum(1 for r in resumo if r['vencedor'] == 'INV')
    empates = sum(1 for r in resumo if r['vencedor'] == 'EMP')
    
    print(f"\n   Q5 (frios) venceu:    {vitorias_q5}/{len(periodos)} períodos")
    print(f"   INVERTIDA venceu:     {vitorias_inv}/{len(periodos)} períodos")
    print(f"   Empates:              {empates}/{len(periodos)} períodos")
    
    # Tendência: períodos curtos vs longos
    curtos = [r for r in resumo if r['periodo'] <= 20]
    longos = [r for r in resumo if r['periodo'] > 20]
    
    media_curtos_q5 = sum(r['q5'] for r in curtos) / len(curtos) if curtos else 0
    media_curtos_inv = sum(r['inv'] for r in curtos) / len(curtos) if curtos else 0
    
    media_longos_q5 = sum(r['q5'] for r in longos) / len(longos) if longos else 0
    media_longos_inv = sum(r['inv'] for r in longos) / len(longos) if longos else 0
    
    print(f"\n   📈 Períodos CURTOS (5-20 concursos):")
    print(f"      Q5:       {media_curtos_q5:.1f}%")
    print(f"      INVERTIDA:{media_curtos_inv:.1f}%")
    print(f"      Diff:     {media_curtos_q5 - media_curtos_inv:+.1f}pp")
    
    print(f"\n   📈 Períodos LONGOS (30-200 concursos):")
    print(f"      Q5:       {media_longos_q5:.1f}%")
    print(f"      INVERTIDA:{media_longos_inv:.1f}%")
    print(f"      Diff:     {media_longos_q5 - media_longos_inv:+.1f}pp")
    
    # Conclusão
    print("\n" + "=" * 70)
    print("🎯 CONCLUSÃO:")
    print("=" * 70)
    
    if media_curtos_inv > media_curtos_q5 and media_longos_q5 > media_longos_inv:
        print("\n   ⚡ DESCOBERTA: Comportamentos DIFERENTES!")
        print("   📈 Curto prazo (5-20): INVERTIDA melhor")
        print("   📈 Longo prazo (30+): Q5 (frios) melhor")
        print("\n   💡 SUGESTÃO: Usar HÍBRIDO baseado em contexto")
    elif vitorias_q5 > vitorias_inv:
        print(f"\n   ✅ Q5 (frios) CONSISTENTEMENTE superior em {vitorias_q5}/{len(periodos)} períodos")
    elif vitorias_inv > vitorias_q5:
        print(f"\n   ✅ INVERTIDA CONSISTENTEMENTE superior em {vitorias_inv}/{len(periodos)} períodos")
    else:
        print("\n   🟰 Sem vencedor claro - ambas estratégias similares")
    
    # Baseline (15% = random)
    print(f"\n   📋 Baseline RANDOM: 15%")
    print(f"   📋 Média geral Q5: {sum(r['q5'] for r in resumo)/len(resumo):.1f}%")
    print(f"   📋 Média geral INV: {sum(r['inv'] for r in resumo)/len(resumo):.1f}%")
    
    print("\n✅ Análise concluída!")

if __name__ == '__main__':
    main()
