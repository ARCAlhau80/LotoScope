"""
Análise de Alternância entre Estratégias QUENTES e FRIOS
=========================================================
Objetivo: Verificar se existe padrão previsível de quando usar cada estratégia
Data: 04/03/2026
"""

import pyodbc
from collections import Counter
from datetime import datetime

def conectar():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def obter_resultados(conn, limite=200):
    """Obtém últimos N resultados ordenados por concurso DESC"""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {limite} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            'concurso': row[0],
            'numeros': set(row[1:16])
        })
    return resultados

def calcular_rankings(resultados_anteriores):
    """
    Calcula os rankings QUENTES e FRIOS baseado nos resultados anteriores.
    Simula exatamente a lógica do super_menu.py
    """
    # Janelas de frequência
    def freq_janela(tamanho):
        freq = Counter()
        for r in resultados_anteriores[:min(tamanho, len(resultados_anteriores))]:
            freq.update(r['numeros'])
        return {n: freq.get(n, 0) / min(tamanho, len(resultados_anteriores)) * 100 for n in range(1, 26)}
    
    freq_5 = freq_janela(5)
    freq_15 = freq_janela(15)
    freq_50 = freq_janela(50)
    
    # Calcular aparições CONSECUTIVAS
    def contar_consecutivos(n):
        count = 0
        for r in resultados_anteriores[:15]:
            if n in r['numeros']:
                count += 1
            else:
                break
        return count
    
    FREQ_ESPERADA = 60
    
    candidatos = []
    for n in range(1, 26):
        fc = freq_5[n]
        fm = freq_15[n]
        fl = freq_50[n]
        
        indice_debito = fl - fc
        consecutivos = contar_consecutivos(n)
        apareceu_recente = any(n in r['numeros'] for r in resultados_anteriores[:3])
        
        # LÓGICA INVERTIDA v3.0
        score = 0
        
        if consecutivos >= 10:
            score -= 5
            status = 'PROTEGIDO'
        elif consecutivos >= 5:
            score += 6
            status = 'SUPER QUENTE'
        elif consecutivos >= 4:
            score += 5
            status = 'MUITO QUENTE'
        elif consecutivos >= 3 and fc >= 80:
            score += 4
            status = 'QUENTE 3+freq'
        elif consecutivos >= 3:
            score += 3
            status = 'QUENTE 3seg'
        elif fc >= 100:
            score += 4
            status = '100% ult5'
        elif fc >= 80 and apareceu_recente:
            score += 3
            status = 'Freq alta'
        elif indice_debito < -35:
            score += 2
            status = 'Superávit ext'
        elif indice_debito < -25:
            score += 1
            status = 'Superávit'
        elif indice_debito >= 0:
            score -= 2
            status = 'Devendo'
        else:
            score -= 1
            status = 'Leve super'
        
        candidatos.append({
            'num': n,
            'freq_curta': fc,
            'consecutivos': consecutivos,
            'indice_debito': indice_debito,
            'status': status,
            'score': score
        })
    
    # QUENTES: maior score primeiro (para excluir)
    quentes = sorted(candidatos, key=lambda x: (-x['score'], -x['consecutivos'], -x['freq_curta']))
    
    # FRIOS: menor score primeiro (para excluir - estratégia antiga)
    frios = sorted(candidatos, key=lambda x: (x['score'], x['consecutivos'], x['freq_curta']))
    
    return quentes, frios

def analisar_alternancia(num_concursos=100):
    """
    Analisa se existe padrão de alternância entre QUENTES e FRIOS
    """
    print("=" * 80)
    print("ANÁLISE DE ALTERNÂNCIA QUENTES vs FRIOS")
    print("=" * 80)
    print(f"\nAnalisando últimos {num_concursos} concursos...")
    print()
    
    conn = conectar()
    # Buscar mais resultados para ter histórico suficiente
    todos_resultados = obter_resultados(conn, limite=num_concursos + 60)
    conn.close()
    
    # Estatísticas
    stats = {
        'quentes_acertou': 0,  # Ambos excluídos NÃO saíram
        'quentes_parcial': 0,  # 1 de 2 não saiu
        'quentes_errou': 0,    # Ambos saíram
        'frios_acertou': 0,
        'frios_parcial': 0,
        'frios_errou': 0,
        'empate': 0,
        'quentes_melhor': 0,
        'frios_melhor': 0,
    }
    
    # Histórico de resultados por concurso
    historico = []
    
    # Sequência de vitórias
    sequencia_atual = None
    sequencia_count = 0
    sequencias = []
    
    print(f"{'Conc':>6} {'Resultado':^50} {'QUENTES':^15} {'FRIOS':^15} {'Melhor':^10}")
    print("-" * 100)
    
    for i in range(num_concursos):
        if i + 51 >= len(todos_resultados):
            break
            
        # Resultado do concurso atual
        resultado_atual = todos_resultados[i]
        concurso = resultado_atual['concurso']
        numeros_sorteados = resultado_atual['numeros']
        
        # Calcular rankings com dados ANTERIORES ao concurso
        resultados_anteriores = todos_resultados[i+1:i+51]  # 50 concursos anteriores
        quentes, frios = calcular_rankings(resultados_anteriores)
        
        # TOP 2 de cada estratégia
        top2_quentes = [quentes[0]['num'], quentes[1]['num']]
        top2_frios = [frios[0]['num'], frios[1]['num']]
        
        # Verificar precisão: quantos NÃO saíram (sucesso na exclusão)
        quentes_nao_saiu = sum(1 for n in top2_quentes if n not in numeros_sorteados)
        frios_nao_saiu = sum(1 for n in top2_frios if n not in numeros_sorteados)
        
        # Estatísticas QUENTES
        if quentes_nao_saiu == 2:
            stats['quentes_acertou'] += 1
        elif quentes_nao_saiu == 1:
            stats['quentes_parcial'] += 1
        else:
            stats['quentes_errou'] += 1
        
        # Estatísticas FRIOS
        if frios_nao_saiu == 2:
            stats['frios_acertou'] += 1
        elif frios_nao_saiu == 1:
            stats['frios_parcial'] += 1
        else:
            stats['frios_errou'] += 1
        
        # Quem foi melhor?
        if quentes_nao_saiu > frios_nao_saiu:
            melhor = 'QUENTES'
            stats['quentes_melhor'] += 1
        elif frios_nao_saiu > quentes_nao_saiu:
            melhor = 'FRIOS'
            stats['frios_melhor'] += 1
        else:
            melhor = 'EMPATE'
            stats['empate'] += 1
        
        # Rastrear sequência
        if melhor != 'EMPATE':
            if sequencia_atual == melhor:
                sequencia_count += 1
            else:
                if sequencia_atual is not None and sequencia_count >= 1:
                    sequencias.append((sequencia_atual, sequencia_count))
                sequencia_atual = melhor
                sequencia_count = 1
        
        # Formatar resultado
        resultado_str = ','.join(str(n) for n in sorted(numeros_sorteados))
        
        # Indicadores visuais
        q_mark = '✅' if quentes_nao_saiu == 2 else ('🔶' if quentes_nao_saiu == 1 else '❌')
        f_mark = '✅' if frios_nao_saiu == 2 else ('🔶' if frios_nao_saiu == 1 else '❌')
        
        quentes_str = f"{top2_quentes} {q_mark}"
        frios_str = f"{top2_frios} {f_mark}"
        
        # Mostrar últimos 30 para não poluir
        if i < 30:
            print(f"{concurso:>6} {resultado_str:^50} {quentes_str:^15} {frios_str:^15} {melhor:^10}")
        
        historico.append({
            'concurso': concurso,
            'resultado': numeros_sorteados,
            'quentes': top2_quentes,
            'frios': top2_frios,
            'quentes_acertos': quentes_nao_saiu,
            'frios_acertos': frios_nao_saiu,
            'melhor': melhor
        })
    
    # Finalizar última sequência
    if sequencia_atual is not None:
        sequencias.append((sequencia_atual, sequencia_count))
    
    print("-" * 100)
    print(f"\n{'=' * 80}")
    print("RESUMO ESTATÍSTICO")
    print("=" * 80)
    
    total = len(historico)
    
    print(f"\n📊 ESTRATÉGIA QUENTES (Excluir números hot):")
    print(f"   ✅ Acertou 2/2: {stats['quentes_acertou']:>4} ({stats['quentes_acertou']/total*100:.1f}%)")
    print(f"   🔶 Acertou 1/2: {stats['quentes_parcial']:>4} ({stats['quentes_parcial']/total*100:.1f}%)")
    print(f"   ❌ Errou 0/2:   {stats['quentes_errou']:>4} ({stats['quentes_errou']/total*100:.1f}%)")
    taxa_quentes = (stats['quentes_acertou'] * 2 + stats['quentes_parcial']) / (total * 2) * 100
    print(f"   📈 Taxa geral:  {taxa_quentes:.1f}%")
    
    print(f"\n❄️ ESTRATÉGIA FRIOS (Excluir números cold):")
    print(f"   ✅ Acertou 2/2: {stats['frios_acertou']:>4} ({stats['frios_acertou']/total*100:.1f}%)")
    print(f"   🔶 Acertou 1/2: {stats['frios_parcial']:>4} ({stats['frios_parcial']/total*100:.1f}%)")
    print(f"   ❌ Errou 0/2:   {stats['frios_errou']:>4} ({stats['frios_errou']/total*100:.1f}%)")
    taxa_frios = (stats['frios_acertou'] * 2 + stats['frios_parcial']) / (total * 2) * 100
    print(f"   📈 Taxa geral:  {taxa_frios:.1f}%")
    
    print(f"\n⚔️ COMPARAÇÃO DIRETA:")
    print(f"   🔥 QUENTES melhor: {stats['quentes_melhor']:>4} ({stats['quentes_melhor']/total*100:.1f}%)")
    print(f"   ❄️ FRIOS melhor:   {stats['frios_melhor']:>4} ({stats['frios_melhor']/total*100:.1f}%)")
    print(f"   🤝 Empate:         {stats['empate']:>4} ({stats['empate']/total*100:.1f}%)")
    
    # Análise de alternância
    print(f"\n{'=' * 80}")
    print("ANÁLISE DE ALTERNÂNCIA (Sequências)")
    print("=" * 80)
    
    # Contar tamanhos de sequências
    seq_quentes = [s[1] for s in sequencias if s[0] == 'QUENTES']
    seq_frios = [s[1] for s in sequencias if s[0] == 'FRIOS']
    
    print(f"\n📊 Sequências QUENTES (vezes consecutivas que foi melhor):")
    if seq_quentes:
        print(f"   Tamanhos: {seq_quentes[:20]}{'...' if len(seq_quentes) > 20 else ''}")
        print(f"   Média: {sum(seq_quentes)/len(seq_quentes):.1f} concursos")
        print(f"   Máxima: {max(seq_quentes)} concursos")
        print(f"   Mínima: {min(seq_quentes)} concurso(s)")
    
    print(f"\n❄️ Sequências FRIOS (vezes consecutivas que foi melhor):")
    if seq_frios:
        print(f"   Tamanhos: {seq_frios[:20]}{'...' if len(seq_frios) > 20 else ''}")
        print(f"   Média: {sum(seq_frios)/len(seq_frios):.1f} concursos")
        print(f"   Máxima: {max(seq_frios)} concursos")
        print(f"   Mínima: {min(seq_frios)} concurso(s)")
    
    # Verificar se há padrão de alternância
    print(f"\n{'=' * 80}")
    print("🔍 ANÁLISE DE PREVISIBILIDADE")
    print("=" * 80)
    
    # Calcular autocorrelação simples (se anterior foi X, próximo é Y?)
    transicoes = {'Q->Q': 0, 'Q->F': 0, 'F->Q': 0, 'F->F': 0}
    for i in range(len(historico) - 1):
        atual = historico[i]['melhor']
        proximo = historico[i+1]['melhor']
        if atual != 'EMPATE' and proximo != 'EMPATE':
            key = f"{atual[0]}->{proximo[0]}"
            transicoes[key] = transicoes.get(key, 0) + 1
    
    total_trans = sum(transicoes.values())
    if total_trans > 0:
        print(f"\n📈 Matriz de Transição (se anterior foi X, próximo é Y?):")
        print(f"\n   {'':>15} {'Próximo':^20}")
        print(f"   {'Anterior':>15} {'QUENTES':>10} {'FRIOS':>10}")
        print(f"   {'-'*35}")
        
        q_total = transicoes['Q->Q'] + transicoes['Q->F']
        f_total = transicoes['F->Q'] + transicoes['F->F']
        
        if q_total > 0:
            print(f"   {'QUENTES':>15} {transicoes['Q->Q']/q_total*100:>9.1f}% {transicoes['Q->F']/q_total*100:>9.1f}%")
        if f_total > 0:
            print(f"   {'FRIOS':>15} {transicoes['F->Q']/f_total*100:>9.1f}% {transicoes['F->F']/f_total*100:>9.1f}%")
        
        # Interpretação
        print(f"\n💡 INTERPRETAÇÃO:")
        
        if q_total > 0 and f_total > 0:
            q_continua = transicoes['Q->Q'] / q_total
            f_continua = transicoes['F->F'] / f_total
            
            if q_continua > 0.6:
                print(f"   ⚠️ QUENTES tende a PERSISTIR ({q_continua*100:.0f}% de chance de repetir)")
            elif q_continua < 0.4:
                print(f"   🔄 QUENTES tende a ALTERNAR ({(1-q_continua)*100:.0f}% de chance de mudar para FRIOS)")
            else:
                print(f"   ❓ QUENTES é IMPREVISÍVEL ({q_continua*100:.0f}% de repetir)")
            
            if f_continua > 0.6:
                print(f"   ⚠️ FRIOS tende a PERSISTIR ({f_continua*100:.0f}% de chance de repetir)")
            elif f_continua < 0.4:
                print(f"   🔄 FRIOS tende a ALTERNAR ({(1-f_continua)*100:.0f}% de chance de mudar para QUENTES)")
            else:
                print(f"   ❓ FRIOS é IMPREVISÍVEL ({f_continua*100:.0f}% de repetir)")
    
    # Análise por período (últimos 20, 20-40, 40-60, etc)
    print(f"\n{'=' * 80}")
    print("📊 ANÁLISE POR PERÍODO (últimos vs mais antigos)")
    print("=" * 80)
    
    periodos = [
        ('Últimos 20', historico[:20]),
        ('21-40', historico[20:40]),
        ('41-60', historico[40:60]),
        ('61-80', historico[60:80]),
        ('81-100', historico[80:100])
    ]
    
    print(f"\n{'Período':>15} {'QUENTES':>12} {'FRIOS':>12} {'Empate':>12} {'Melhor':>12}")
    print("-" * 65)
    
    for nome, periodo in periodos:
        if not periodo:
            continue
        q = sum(1 for h in periodo if h['melhor'] == 'QUENTES')
        f = sum(1 for h in periodo if h['melhor'] == 'FRIOS')
        e = sum(1 for h in periodo if h['melhor'] == 'EMPATE')
        total_p = len(periodo)
        
        melhor = 'QUENTES' if q > f else ('FRIOS' if f > q else 'EMPATE')
        print(f"{nome:>15} {q:>4} ({q/total_p*100:>4.0f}%) {f:>4} ({f/total_p*100:>4.0f}%) {e:>4} ({e/total_p*100:>4.0f}%) {melhor:>12}")
    
    # Conclusão
    print(f"\n{'=' * 80}")
    print("🎯 CONCLUSÃO")
    print("=" * 80)
    
    diff = abs(stats['quentes_melhor'] - stats['frios_melhor'])
    diff_pct = diff / total * 100
    
    if stats['quentes_melhor'] > stats['frios_melhor'] * 1.3:
        print(f"\n✅ QUENTES é CLARAMENTE superior ({stats['quentes_melhor']/total*100:.0f}% vs {stats['frios_melhor']/total*100:.0f}%)")
        print(f"   Recomendação: Manter estratégia QUENTES (INVERTIDA v3.0)")
    elif stats['frios_melhor'] > stats['quentes_melhor'] * 1.3:
        print(f"\n✅ FRIOS é CLARAMENTE superior ({stats['frios_melhor']/total*100:.0f}% vs {stats['quentes_melhor']/total*100:.0f}%)")
        print(f"   Recomendação: Considerar voltar para estratégia FRIOS")
    else:
        print(f"\n⚠️ DIFERENÇA PEQUENA entre estratégias ({diff_pct:.1f}%)")
        print(f"   QUENTES: {stats['quentes_melhor']/total*100:.0f}% | FRIOS: {stats['frios_melhor']/total*100:.0f}%")
        
        # Ver se há padrão por período
        ult20 = historico[:20]
        q_ult = sum(1 for h in ult20 if h['melhor'] == 'QUENTES')
        f_ult = sum(1 for h in ult20 if h['melhor'] == 'FRIOS')
        
        if q_ult > f_ult * 1.5:
            print(f"   📈 Porém nos últimos 20, QUENTES dominou ({q_ult} vs {f_ult})")
            print(f"   Recomendação: Manter QUENTES por enquanto")
        elif f_ult > q_ult * 1.5:
            print(f"   📈 Porém nos últimos 20, FRIOS dominou ({f_ult} vs {q_ult})")
            print(f"   ⚠️ Considerar usar FRIOS temporariamente!")
        else:
            print(f"   Nos últimos 20: QUENTES={q_ult}, FRIOS={f_ult}")
            print(f"   Recomendação: Escolher baseado em outros fatores ou alternar")
    
    return historico, stats, sequencias

if __name__ == "__main__":
    historico, stats, sequencias = analisar_alternancia(100)
