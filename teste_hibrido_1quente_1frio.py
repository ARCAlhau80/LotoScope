# -*- coding: utf-8 -*-
"""
Teste HÍBRIDO: 1 INVERTIDA + 1 Q5
==================================
Hipótese: Excluir 1 número quente (INVERTIDA) + 1 número frio (Q5)
pode diversificar o risco e superar ambas estratégias isoladas.

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

def estrategia_q5_frios(freq_dict, n=2):
    """Retorna os N menos frequentes"""
    ordenado = sorted(range(1, 26), key=lambda x: freq_dict.get(x, 0))
    return ordenado[:n]

def estrategia_invertida_quentes(freq_dict, consecutivas, n=2):
    """Retorna os N mais quentes"""
    max_freq = max(freq_dict.values()) if freq_dict else 1
    scores = {}
    for num in range(1, 26):
        freq_norm = freq_dict.get(num, 0) / max_freq
        consec = consecutivas.get(num, 0)
        if consec >= 10:
            scores[num] = -1  # Proteção anomalia
        else:
            scores[num] = freq_norm + (consec / 10)
    ordenado = sorted(range(1, 26), key=lambda x: scores[x], reverse=True)
    return ordenado[:n]

def estrategia_hibrida(freq_dict, consecutivas):
    """1 quente (INVERTIDA) + 1 frio (Q5)"""
    quentes = estrategia_invertida_quentes(freq_dict, consecutivas, n=1)
    frios = estrategia_q5_frios(freq_dict, n=1)
    return quentes + frios

def backtest_estrategias(concursos, janela, n_teste):
    """Compara as 3 estratégias"""
    resultados = {
        '2_QUENTES (INV)': 0,
        '2_FRIOS (Q5)': 0,
        '1_QUENTE+1_FRIO (HÍBRIDO)': 0,
    }
    
    for i in range(n_teste):
        idx_teste = i
        historico = concursos[idx_teste+1:idx_teste+1+janela]
        
        if len(historico) < janela:
            continue
        
        atual = concursos[idx_teste]
        sorteio = set([atual[j] for j in range(1, 16)])
        
        freq = calcular_frequencia(historico)
        consec = calcular_consecutivas(historico)
        
        # Estratégia 1: 2 quentes (INVERTIDA atual)
        excluir_inv = estrategia_invertida_quentes(freq, consec, n=2)
        jackpot_inv = len(set(excluir_inv) & sorteio) == 0
        
        # Estratégia 2: 2 frios (Q5)
        excluir_q5 = estrategia_q5_frios(freq, n=2)
        jackpot_q5 = len(set(excluir_q5) & sorteio) == 0
        
        # Estratégia 3: HÍBRIDO (1 quente + 1 frio)
        excluir_hib = estrategia_hibrida(freq, consec)
        jackpot_hib = len(set(excluir_hib) & sorteio) == 0
        
        resultados['2_QUENTES (INV)'] += int(jackpot_inv)
        resultados['2_FRIOS (Q5)'] += int(jackpot_q5)
        resultados['1_QUENTE+1_FRIO (HÍBRIDO)'] += int(jackpot_hib)
    
    return resultados

def main():
    print("=" * 70)
    print("🔬 TESTE HÍBRIDO: 1 QUENTE + 1 FRIO vs ESTRATÉGIAS PURAS")
    print("=" * 70)
    
    concursos = obter_todos_concursos()
    print(f"\n📊 Total de concursos: {len(concursos)}")
    
    # Configurações
    janelas = [30, 50, 100]
    periodos = [50, 100, 200]
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS:")
    print("=" * 70)
    
    todos_resultados = []
    
    for janela in janelas:
        print(f"\n📈 JANELA = {janela} concursos:")
        print("-" * 60)
        
        for n_teste in periodos:
            r = backtest_estrategias(concursos, janela, n_teste)
            
            taxa_inv = r['2_QUENTES (INV)'] / n_teste * 100
            taxa_q5 = r['2_FRIOS (Q5)'] / n_teste * 100
            taxa_hib = r['1_QUENTE+1_FRIO (HÍBRIDO)'] / n_teste * 100
            
            # Determina vencedor
            taxas = {'INV': taxa_inv, 'Q5': taxa_q5, 'HIB': taxa_hib}
            vencedor = max(taxas, key=taxas.get)
            
            # Emojis
            emoji_inv = "🥇" if vencedor == 'INV' else ""
            emoji_q5 = "🥇" if vencedor == 'Q5' else ""
            emoji_hib = "🥇" if vencedor == 'HIB' else ""
            
            print(f"   T={n_teste:>3}: INV={taxa_inv:>5.1f}%{emoji_inv} | Q5={taxa_q5:>5.1f}%{emoji_q5} | HÍBRIDO={taxa_hib:>5.1f}%{emoji_hib}")
            
            todos_resultados.append({
                'janela': janela,
                'periodo': n_teste,
                'inv': taxa_inv,
                'q5': taxa_q5,
                'hib': taxa_hib,
                'vencedor': vencedor
            })
    
    # Contagem de vitórias
    print("\n" + "=" * 70)
    print("🏆 CONTAGEM DE VITÓRIAS:")
    print("=" * 70)
    
    vitorias = {'INV': 0, 'Q5': 0, 'HIB': 0}
    for r in todos_resultados:
        vitorias[r['vencedor']] += 1
    
    total = len(todos_resultados)
    print(f"\n   2 QUENTES (INVERTIDA): {vitorias['INV']:>2}/{total} ({vitorias['INV']/total*100:.0f}%)")
    print(f"   2 FRIOS (Q5):          {vitorias['Q5']:>2}/{total} ({vitorias['Q5']/total*100:.0f}%)")
    print(f"   1+1 HÍBRIDO:           {vitorias['HIB']:>2}/{total} ({vitorias['HIB']/total*100:.0f}%)")
    
    # Médias gerais
    print("\n" + "=" * 70)
    print("📊 MÉDIAS GERAIS:")
    print("=" * 70)
    
    media_inv = sum(r['inv'] for r in todos_resultados) / len(todos_resultados)
    media_q5 = sum(r['q5'] for r in todos_resultados) / len(todos_resultados)
    media_hib = sum(r['hib'] for r in todos_resultados) / len(todos_resultados)
    
    print(f"\n   INVERTIDA (2 quentes): {media_inv:.1f}%")
    print(f"   Q5 (2 frios):          {media_q5:.1f}%")
    print(f"   HÍBRIDO (1+1):         {media_hib:.1f}%")
    print(f"\n   Baseline RANDOM:       15.0%")
    
    # Conclusão
    print("\n" + "=" * 70)
    print("🎯 CONCLUSÃO:")
    print("=" * 70)
    
    melhor = max([('INV', media_inv), ('Q5', media_q5), ('HIB', media_hib)], key=lambda x: x[1])
    
    if melhor[0] == 'HIB':
        print(f"\n   ✅ HÍBRIDO é SUPERIOR! ({media_hib:.1f}%)")
        print("   → Vale implementar como opção no Pool 23!")
    elif melhor[0] == 'INV':
        print(f"\n   ✅ INVERTIDA continua sendo a melhor ({media_inv:.1f}%)")
        print("   → Manter como default")
    else:
        print(f"\n   ✅ Q5 surpreende ({media_q5:.1f}%)")
    
    # Análise de consistência do híbrido
    print("\n" + "=" * 70)
    print("📋 ANÁLISE DE CONSISTÊNCIA DO HÍBRIDO:")
    print("=" * 70)
    
    # Híbrido vs Invertida
    hib_melhor_inv = sum(1 for r in todos_resultados if r['hib'] > r['inv'])
    hib_melhor_q5 = sum(1 for r in todos_resultados if r['hib'] > r['q5'])
    
    print(f"\n   HÍBRIDO > INVERTIDA: {hib_melhor_inv}/{total} vezes")
    print(f"   HÍBRIDO > Q5:        {hib_melhor_q5}/{total} vezes")
    
    if hib_melhor_inv >= total * 0.6:
        print("\n   💡 HÍBRIDO consistentemente supera INVERTIDA")
    elif hib_melhor_inv >= total * 0.4:
        print("\n   🟡 HÍBRIDO empata/varia com INVERTIDA")
    else:
        print("\n   ❌ INVERTIDA continua superior")
    
    print("\n✅ Análise concluída!")

if __name__ == '__main__':
    main()
