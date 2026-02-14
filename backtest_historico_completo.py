# -*- coding: utf-8 -*-
"""
BACKTEST COMPLETO: Estratégia Superávit v2.0 vs Estratégia Antiga
Testa TODO o histórico disponível no banco (3611 concursos)
"""

import pyodbc
from collections import defaultdict

def get_conexao():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def get_todos_concursos():
    """Retorna todos os concursos com seus resultados"""
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso ASC
    """)
    resultados = []
    for row in cursor.fetchall():
        concurso = row[0]
        numeros = set(row[1:16])
        resultados.append((concurso, numeros))
    conn.close()
    return resultados

def calcular_frequencias_memoria(todos_resultados, idx_alvo, janela_curta=5, janela_longa=50):
    """Calcula frequências usando dados em memória (mais rápido)"""
    if idx_alvo < janela_longa:
        return None  # Dados insuficientes
    
    # Pegar concursos anteriores ao alvo
    inicio = idx_alvo - janela_longa
    fim = idx_alvo
    
    freq_curta = {i: 0 for i in range(1, 26)}
    freq_longa = {i: 0 for i in range(1, 26)}
    
    for i in range(fim - 1, inicio - 1, -1):  # Do mais recente ao mais antigo
        _, numeros = todos_resultados[i]
        dist_do_alvo = fim - 1 - i  # 0 = mais recente
        
        for n in numeros:
            if dist_do_alvo < janela_curta:
                freq_curta[n] += 1
            freq_longa[n] += 1
    
    # Converter para percentuais
    freq_curta_pct = {n: (freq_curta[n] / janela_curta) * 100 for n in range(1, 26)}
    freq_longa_pct = {n: (freq_longa[n] / janela_longa) * 100 for n in range(1, 26)}
    
    return freq_curta_pct, freq_longa_pct

def estrategia_antiga(freq_curta, freq_longa):
    """Estratégia ANTIGA: Excluir números com maior QUEDA"""
    scores = {}
    for n in range(1, 26):
        fc = freq_curta[n]
        fl = freq_longa[n]
        queda = fl - fc
        
        score = 0
        if queda >= 30: score += 5
        elif queda >= 20: score += 4
        elif queda >= 10: score += 3
        if fc <= 40: score += 2
        
        scores[n] = score
    
    ranking = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    excluir = [ranking[0][0], ranking[1][0]]
    return sorted(excluir)

def estrategia_nova_superavit(freq_curta, freq_longa):
    """Estratégia NOVA v2.0: Excluir números em SUPERÁVIT"""
    scores = {}
    for n in range(1, 26):
        fc = freq_curta[n]
        fl = freq_longa[n]
        indice_debito = fl - fc
        
        score = 0
        if indice_debito < -30: score += 5
        elif indice_debito < -15: score += 4
        elif indice_debito < 0: score += 2
        
        if fc >= 100: score += 3
        elif fc >= 80: score += 2
        
        if fc <= 40 and fl >= 55: score -= 4
        
        scores[n] = score
    
    ranking = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    excluir = [ranking[0][0], ranking[1][0]]
    return sorted(excluir)

def main():
    print("=" * 80)
    print("🔬 BACKTEST HISTÓRICO COMPLETO")
    print("   Estratégia Superávit v2.0 vs Estratégia Antiga")
    print("=" * 80)
    print()
    
    print("📥 Carregando todos os concursos...")
    todos = get_todos_concursos()
    print(f"   Total: {len(todos)} concursos ({todos[0][0]} a {todos[-1][0]})")
    print()
    
    # Precisamos de pelo menos 50 concursos anteriores para calcular frequências
    inicio_teste = 50
    
    total_erros_antiga = 0
    total_erros_nova = 0
    vitorias_antiga = 0
    vitorias_nova = 0
    empates = 0
    
    # Estatísticas por período (a cada 500 concursos)
    periodos = defaultdict(lambda: {'antiga': 0, 'nova': 0, 'testes': 0})
    
    print("🔄 Executando backtest...")
    print(f"   Testando concursos {todos[inicio_teste][0]} a {todos[-1][0]}")
    print()
    
    for idx in range(inicio_teste, len(todos)):
        concurso, resultado = todos[idx]
        
        freqs = calcular_frequencias_memoria(todos, idx)
        if freqs is None:
            continue
        
        freq_curta, freq_longa = freqs
        
        excluir_antiga = estrategia_antiga(freq_curta, freq_longa)
        excluir_nova = estrategia_nova_superavit(freq_curta, freq_longa)
        
        erros_antiga = len(set(excluir_antiga) & resultado)
        erros_nova = len(set(excluir_nova) & resultado)
        
        total_erros_antiga += erros_antiga
        total_erros_nova += erros_nova
        
        if erros_antiga < erros_nova:
            vitorias_antiga += 1
        elif erros_nova < erros_antiga:
            vitorias_nova += 1
        else:
            empates += 1
        
        # Agrupar por período de 500 concursos
        periodo = (concurso // 500) * 500
        periodos[periodo]['antiga'] += erros_antiga
        periodos[periodo]['nova'] += erros_nova
        periodos[periodo]['testes'] += 1
        
        # Progresso a cada 500 concursos
        if (idx - inicio_teste + 1) % 500 == 0:
            print(f"   Processados: {idx - inicio_teste + 1} concursos...")
    
    total_testes = len(todos) - inicio_teste
    
    print()
    print("=" * 80)
    print("📊 RESULTADOS POR PERÍODO (a cada 500 concursos)")
    print("=" * 80)
    print()
    print(f"{'Período':^15} | {'Antiga':^12} | {'Nova':^12} | {'Diferença':^12} | {'Melhor':^10}")
    print("-" * 70)
    
    for periodo in sorted(periodos.keys()):
        dados = periodos[periodo]
        diff = dados['antiga'] - dados['nova']
        if diff > 0:
            melhor = "🟢 NOVA"
        elif diff < 0:
            melhor = "🔴 ANTIGA"
        else:
            melhor = "🟡 EMPATE"
        
        media_antiga = dados['antiga'] / dados['testes'] if dados['testes'] > 0 else 0
        media_nova = dados['nova'] / dados['testes'] if dados['testes'] > 0 else 0
        
        print(f"{periodo:>5}-{periodo+499:<5} | {dados['antiga']:>5} ({media_antiga:.2f}/c) | {dados['nova']:>5} ({media_nova:.2f}/c) | {diff:>+5} erros | {melhor:^10}")
    
    print("-" * 70)
    print()
    
    # Resumo final
    print("=" * 80)
    print("📈 RESUMO FINAL DO BACKTEST COMPLETO")
    print("=" * 80)
    print()
    print(f"   📊 Concursos testados: {total_testes}")
    print()
    print(f"   🔴 ESTRATÉGIA ANTIGA:")
    print(f"      Total de erros: {total_erros_antiga}")
    print(f"      Média de erros: {total_erros_antiga/total_testes:.4f} por concurso")
    print(f"      Taxa de erro: {total_erros_antiga/(total_testes*2)*100:.2f}%")
    print(f"      Vitórias: {vitorias_antiga} ({vitorias_antiga/total_testes*100:.1f}%)")
    print()
    print(f"   🟢 ESTRATÉGIA NOVA (SUPERÁVIT v2.0):")
    print(f"      Total de erros: {total_erros_nova}")
    print(f"      Média de erros: {total_erros_nova/total_testes:.4f} por concurso")
    print(f"      Taxa de erro: {total_erros_nova/(total_testes*2)*100:.2f}%")
    print(f"      Vitórias: {vitorias_nova} ({vitorias_nova/total_testes*100:.1f}%)")
    print()
    print(f"   🟡 Empates: {empates} ({empates/total_testes*100:.1f}%)")
    print()
    
    # Conclusão
    diff_total = total_erros_antiga - total_erros_nova
    pct_diff = abs(diff_total) / total_erros_antiga * 100 if total_erros_antiga > 0 else 0
    
    print("=" * 80)
    print("🎯 CONCLUSÃO")
    print("=" * 80)
    print()
    
    if diff_total > 0:
        print(f"   ✅ NOVA ESTRATÉGIA É MELHOR!")
        print(f"      Redução de {diff_total} erros ({pct_diff:.2f}%)")
    elif diff_total < 0:
        print(f"   ❌ ESTRATÉGIA ANTIGA É MELHOR!")
        print(f"      Nova teve {abs(diff_total)} erros a mais ({pct_diff:.2f}%)")
    else:
        print(f"   🟡 EMPATE TÉCNICO PERFEITO!")
    
    print()
    
    # Análise de tendência recente vs antiga
    periodos_lista = sorted(periodos.keys())
    if len(periodos_lista) >= 4:
        # Primeira metade vs segunda metade
        metade = len(periodos_lista) // 2
        
        erros_antiga_inicio = sum(periodos[p]['antiga'] for p in periodos_lista[:metade])
        erros_nova_inicio = sum(periodos[p]['nova'] for p in periodos_lista[:metade])
        testes_inicio = sum(periodos[p]['testes'] for p in periodos_lista[:metade])
        
        erros_antiga_fim = sum(periodos[p]['antiga'] for p in periodos_lista[metade:])
        erros_nova_fim = sum(periodos[p]['nova'] for p in periodos_lista[metade:])
        testes_fim = sum(periodos[p]['testes'] for p in periodos_lista[metade:])
        
        print("   📈 ANÁLISE DE EVOLUÇÃO TEMPORAL:")
        print()
        print(f"      PRIMEIRA METADE ({periodos_lista[0]}-{periodos_lista[metade-1]+499}):")
        print(f"         Antiga: {erros_antiga_inicio/testes_inicio:.3f} erros/conc")
        print(f"         Nova:   {erros_nova_inicio/testes_inicio:.3f} erros/conc")
        diff_inicio = erros_antiga_inicio - erros_nova_inicio
        print(f"         Melhor: {'NOVA' if diff_inicio > 0 else 'ANTIGA'} ({abs(diff_inicio)} erros)")
        print()
        print(f"      SEGUNDA METADE ({periodos_lista[metade]}-{periodos_lista[-1]+499}):")
        print(f"         Antiga: {erros_antiga_fim/testes_fim:.3f} erros/conc")
        print(f"         Nova:   {erros_nova_fim/testes_fim:.3f} erros/conc")
        diff_fim = erros_antiga_fim - erros_nova_fim
        print(f"         Melhor: {'NOVA' if diff_fim > 0 else 'ANTIGA'} ({abs(diff_fim)} erros)")
        print()
        
        if diff_inicio < 0 and diff_fim > 0:
            print("      ⚠️ MUDANÇA DE PADRÃO DETECTADA!")
            print("         A nova estratégia está melhorando com o tempo!")
        elif diff_inicio > 0 and diff_fim < 0:
            print("      ⚠️ MUDANÇA DE PADRÃO DETECTADA!")
            print("         A estratégia antiga está melhorando recentemente!")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
