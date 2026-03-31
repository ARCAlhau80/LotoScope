# -*- coding: utf-8 -*-
"""
Análise de Estabilidade: Impacto da JANELA de Cálculo
======================================================
Testa diferentes janelas históricas: 30, 50, 100, 150, 200 concursos
para calcular frequência e determinar exclusões.

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
    ordenado = sorted(range(1, 26), key=lambda x: freq_dict.get(x, 0))
    return ordenado[:2]

def estrategia_invertida_quentes(freq_dict, consecutivas):
    max_freq = max(freq_dict.values()) if freq_dict else 1
    scores = {}
    for n in range(1, 26):
        freq_norm = freq_dict.get(n, 0) / max_freq
        consec = consecutivas.get(n, 0)
        if consec >= 10:
            scores[n] = -1
        else:
            scores[n] = freq_norm + (consec / 10)
    ordenado = sorted(range(1, 26), key=lambda x: scores[x], reverse=True)
    return ordenado[:2]

def backtest_com_janela(concursos, janela, n_teste=100):
    """
    Walk-forward backtest usando janela específica
    """
    resultados = {'Q5': 0, 'INV': 0}
    
    for i in range(n_teste):
        idx_teste = i
        historico = concursos[idx_teste+1:idx_teste+1+janela]
        
        if len(historico) < janela:
            continue
        
        atual = concursos[idx_teste]
        sorteio = set([atual[j] for j in range(1, 16)])
        
        freq = calcular_frequencia(historico)
        consec = calcular_consecutivas(historico)
        
        excluir_q5 = estrategia_q5_frios(freq)
        jackpot_q5 = len(set(excluir_q5) & sorteio) == 0
        
        excluir_inv = estrategia_invertida_quentes(freq, consec)
        jackpot_inv = len(set(excluir_inv) & sorteio) == 0
        
        resultados['Q5'] += int(jackpot_q5)
        resultados['INV'] += int(jackpot_inv)
    
    return resultados

def main():
    print("=" * 80)
    print("🔬 ANÁLISE DE ESTABILIDADE: IMPACTO DA JANELA DE CÁLCULO")
    print("=" * 80)
    
    concursos = obter_todos_concursos()
    print(f"\n📊 Total de concursos: {len(concursos)}")
    
    # Janelas a testar
    janelas = [20, 30, 50, 100, 150, 200]
    # Períodos de teste
    periodos_teste = [50, 100, 200]
    
    print("\n" + "=" * 80)
    print("📊 MATRIZ: JANELA (colunas) x PERÍODO DE TESTE (linhas)")
    print("=" * 80)
    
    # Cabeçalho
    header = f"{'Período':<12}"
    for j in janelas:
        header += f"{'J=' + str(j):>12}"
    print(f"\n{header}")
    print("-" * 80)
    
    resultados_matriz = {}
    
    for n_teste in periodos_teste:
        resultados_matriz[n_teste] = {}
        
        linha_q5 = f"T={n_teste} Q5   "
        linha_inv = f"T={n_teste} INV  "
        linha_diff = f"T={n_teste} Diff "
        
        for janela in janelas:
            r = backtest_com_janela(concursos, janela, n_teste)
            taxa_q5 = r['Q5'] / n_teste * 100
            taxa_inv = r['INV'] / n_teste * 100
            diff = taxa_q5 - taxa_inv
            
            resultados_matriz[n_teste][janela] = {
                'q5': taxa_q5,
                'inv': taxa_inv,
                'diff': diff
            }
            
            linha_q5 += f"{taxa_q5:>10.1f}% "
            linha_inv += f"{taxa_inv:>10.1f}% "
            
            if diff > 0:
                linha_diff += f"{'+' + str(round(diff,1)):>10}pp"
            else:
                linha_diff += f"{round(diff,1):>10}pp"
        
        print(linha_q5)
        print(linha_inv)
        print(linha_diff)
        print()
    
    # Análise de estabilidade
    print("=" * 80)
    print("📈 ANÁLISE DE ESTABILIDADE POR JANELA:")
    print("=" * 80)
    
    for janela in janelas:
        diffs = [resultados_matriz[p][janela]['diff'] for p in periodos_teste]
        media_diff = sum(diffs) / len(diffs)
        variancia = sum((d - media_diff)**2 for d in diffs) / len(diffs)
        desvio = variancia ** 0.5
        
        # Consistência: quantas vezes a mesma estratégia venceu
        vitorias_q5 = sum(1 for d in diffs if d > 0)
        vitorias_inv = sum(1 for d in diffs if d < 0)
        
        vencedor = "Q5" if vitorias_q5 > vitorias_inv else ("INV" if vitorias_inv > vitorias_q5 else "EMPATE")
        
        print(f"\n   Janela {janela} concursos:")
        print(f"      Média diff Q5-INV: {media_diff:+.1f}pp")
        print(f"      Desvio padrão:     {desvio:.1f}pp")
        print(f"      Vencedor:          {vencedor} ({vitorias_q5}/{len(periodos_teste)} períodos Q5)")
        
        # Classificação
        if desvio < 3:
            print(f"      Estabilidade:      ✅ ALTA (desvio < 3)")
        elif desvio < 6:
            print(f"      Estabilidade:      🟡 MÉDIA (desvio 3-6)")
        else:
            print(f"      Estabilidade:      ❌ BAIXA (desvio > 6)")
    
    # Conclusão: melhor janela
    print("\n" + "=" * 80)
    print("🎯 CONCLUSÃO: MELHOR JANELA")
    print("=" * 80)
    
    melhor_janela = None
    melhor_score = -999
    
    for janela in janelas:
        diffs = [resultados_matriz[p][janela]['diff'] for p in periodos_teste]
        media_diff = sum(diffs) / len(diffs)
        variancia = sum((d - media_diff)**2 for d in diffs) / len(diffs)
        desvio = variancia ** 0.5
        
        # Score = consistência do vencedor + baixa variância
        vitorias_q5 = sum(1 for d in diffs if d > 0)
        vitorias_inv = sum(1 for d in diffs if d < 0)
        consistencia = max(vitorias_q5, vitorias_inv) / len(periodos_teste)
        
        # Score favorece: alta consistência, baixo desvio, maior diferença absoluta
        score = consistencia * 100 - desvio * 5 + abs(media_diff)
        
        if score > melhor_score:
            melhor_score = score
            melhor_janela = janela
    
    print(f"\n   🏆 Melhor janela: {melhor_janela} concursos")
    
    # Mostra resultado final para a melhor janela
    print(f"\n   Resultados com janela {melhor_janela}:")
    for p in periodos_teste:
        r = resultados_matriz[p][melhor_janela]
        venc = "Q5 ✅" if r['diff'] > 0 else ("INV ✅" if r['diff'] < 0 else "EMPATE")
        print(f"      T={p}: Q5={r['q5']:.1f}% | INV={r['inv']:.1f}% | {venc}")
    
    # Recomendação final
    print("\n" + "=" * 80)
    print("💡 RECOMENDAÇÃO FINAL:")
    print("=" * 80)
    
    # Conta vitórias totais
    total_q5 = 0
    total_inv = 0
    for p in periodos_teste:
        for j in janelas:
            if resultados_matriz[p][j]['diff'] > 0:
                total_q5 += 1
            elif resultados_matriz[p][j]['diff'] < 0:
                total_inv += 1
    
    total = len(periodos_teste) * len(janelas)
    
    print(f"\n   Q5 (frios) venceu:    {total_q5}/{total} combinações ({total_q5/total*100:.0f}%)")
    print(f"   INVERTIDA venceu:     {total_inv}/{total} combinações ({total_inv/total*100:.0f}%)")
    
    if total_q5 > total_inv * 1.5:
        print(f"\n   ✅ RECOMENDAÇÃO: Usar Q5 (excluir FRIOS)")
    elif total_inv > total_q5 * 1.5:
        print(f"\n   ✅ RECOMENDAÇÃO: Manter INVERTIDA (excluir QUENTES)")
    else:
        print(f"\n   🟡 RESULTADO INCONCLUSIVO: Ambas estratégias similares")
        print(f"      → Manter INVERTIDA (default atual) por segurança")
    
    print("\n✅ Análise concluída!")

if __name__ == '__main__':
    main()
