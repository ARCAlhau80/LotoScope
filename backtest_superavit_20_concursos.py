# -*- coding: utf-8 -*-
"""
BACKTEST: Estratégia Superávit v2.0 vs Estratégia Antiga
Testa os últimos 20 concursos para validar a melhoria
"""

import pyodbc

def get_conexao():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def get_ultimos_concursos(n=20):
    """Retorna os últimos N concursos com seus resultados"""
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {n} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados
        ORDER BY Concurso DESC
    """)
    resultados = []
    for row in cursor.fetchall():
        concurso = row[0]
        numeros = set(int(x) for x in row[1:16])
        resultados.append((concurso, numeros))
    conn.close()
    return resultados

def calcular_frequencias(concurso_alvo, janela_curta=5, janela_longa=50):
    """Calcula frequências curta e longa para cada número ANTES do concurso alvo"""
    conn = get_conexao()
    cursor = conn.cursor()
    
    # Pegar concursos anteriores ao alvo
    cursor.execute(f"""
        SELECT TOP {janela_longa} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados
        WHERE Concurso < {concurso_alvo}
        ORDER BY Concurso DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) < janela_longa:
        return None  # Dados insuficientes
    
    # Contar frequências
    freq_curta = {i: 0 for i in range(1, 26)}
    freq_longa = {i: 0 for i in range(1, 26)}
    
    for idx, row in enumerate(rows):
        numeros = set(int(x) for x in row[1:16])
        for n in numeros:
            if idx < janela_curta:
                freq_curta[n] += 1
            freq_longa[n] += 1
    
    # Converter para percentuais
    freq_curta_pct = {n: (freq_curta[n] / janela_curta) * 100 for n in range(1, 26)}
    freq_longa_pct = {n: (freq_longa[n] / janela_longa) * 100 for n in range(1, 26)}
    
    return freq_curta_pct, freq_longa_pct

def estrategia_antiga(freq_curta, freq_longa):
    """
    Estratégia ANTIGA: Excluir números com maior QUEDA (curta << longa)
    Score baseado em queda forte
    """
    scores = {}
    for n in range(1, 26):
        fc = freq_curta[n]
        fl = freq_longa[n]
        queda = fl - fc  # Quanto maior, mais "queda"
        
        score = 0
        # Critério antigo: queda forte = candidato à exclusão
        if queda >= 30:
            score += 5
        elif queda >= 20:
            score += 4
        elif queda >= 10:
            score += 3
        
        # Tendência de baixa
        if fc <= 40:
            score += 2
        
        scores[n] = score
    
    # Ordenar por score (maior = excluir)
    ranking = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    excluir = [ranking[0][0], ranking[1][0]]
    return sorted(excluir)

def estrategia_nova_superavit(freq_curta, freq_longa):
    """
    Estratégia NOVA v2.0: Excluir números em SUPERÁVIT (curta > longa)
    Números em DÉBITO (curta < longa) tendem a RETORNAR!
    """
    scores = {}
    for n in range(1, 26):
        fc = freq_curta[n]
        fl = freq_longa[n]
        indice_debito = fl - fc  # Positivo = débito, Negativo = superávit
        
        score = 0
        
        # SUPERÁVIT ALTO (curta >> longa) = EXCLUIR
        if indice_debito < -30:
            score += 5
        elif indice_debito < -15:
            score += 4
        elif indice_debito < 0:
            score += 2
        
        # Curta muito alta = número "quente demais", pode esfriar
        if fc >= 100:
            score += 3
        elif fc >= 80:
            score += 2
        
        # DÉBITO ALTO (curta << longa) = NÃO EXCLUIR!
        if fc <= 40 and fl >= 55:
            score -= 4  # Penalidade forte
        
        scores[n] = score
    
    # Ordenar por score (maior = excluir)
    ranking = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    excluir = [ranking[0][0], ranking[1][0]]
    return sorted(excluir)

def main():
    print("=" * 80)
    print("🔬 BACKTEST: SUPERÁVIT v2.0 vs ESTRATÉGIA ANTIGA")
    print("=" * 80)
    print()
    
    concursos = get_ultimos_concursos(20)
    
    if not concursos:
        print("❌ Erro: Não foi possível obter os concursos")
        return
    
    print(f"📊 Testando {len(concursos)} concursos: {concursos[-1][0]} a {concursos[0][0]}")
    print("-" * 80)
    print(f"{'Concurso':^10} | {'Antiga':^15} | {'Erros':^6} | {'Nova':^15} | {'Erros':^6} | {'Vencedor':^12}")
    print("-" * 80)
    
    total_erros_antiga = 0
    total_erros_nova = 0
    vitorias_antiga = 0
    vitorias_nova = 0
    empates = 0
    
    detalhes = []
    
    for concurso, resultado in concursos:
        freqs = calcular_frequencias(concurso)
        
        if freqs is None:
            print(f"{concurso:^10} | {'DADOS INSUF.':^15} | {'-':^6} | {'DADOS INSUF.':^15} | {'-':^6} | {'-':^12}")
            continue
        
        freq_curta, freq_longa = freqs
        
        # Aplicar estratégias
        excluir_antiga = estrategia_antiga(freq_curta, freq_longa)
        excluir_nova = estrategia_nova_superavit(freq_curta, freq_longa)
        
        # Calcular erros (excluídos que saíram)
        erros_antiga = len(set(excluir_antiga) & resultado)
        erros_nova = len(set(excluir_nova) & resultado)
        
        total_erros_antiga += erros_antiga
        total_erros_nova += erros_nova
        
        # Determinar vencedor
        if erros_antiga < erros_nova:
            vencedor = "🔴 ANTIGA"
            vitorias_antiga += 1
        elif erros_nova < erros_antiga:
            vencedor = "🟢 NOVA"
            vitorias_nova += 1
        else:
            vencedor = "🟡 EMPATE"
            empates += 1
        
        # Formatar exclusões com indicador de erro
        excl_antiga_str = str(excluir_antiga)
        excl_nova_str = str(excluir_nova)
        
        if erros_antiga > 0:
            excl_antiga_str += " ❌"
        if erros_nova > 0:
            excl_nova_str += " ❌"
        
        print(f"{concurso:^10} | {excl_antiga_str:^15} | {erros_antiga:^6} | {excl_nova_str:^15} | {erros_nova:^6} | {vencedor:^12}")
        
        detalhes.append({
            'concurso': concurso,
            'resultado': resultado,
            'excluir_antiga': excluir_antiga,
            'excluir_nova': excluir_nova,
            'erros_antiga': erros_antiga,
            'erros_nova': erros_nova
        })
    
    print("-" * 80)
    print()
    
    # Resumo
    print("=" * 80)
    print("📈 RESUMO DO BACKTEST")
    print("=" * 80)
    print()
    print(f"   Concursos testados: {len(detalhes)}")
    print()
    print(f"   🔴 ESTRATÉGIA ANTIGA:")
    print(f"      Total de erros: {total_erros_antiga}")
    print(f"      Média de erros: {total_erros_antiga/len(detalhes):.2f} por concurso")
    print(f"      Vitórias: {vitorias_antiga}")
    print()
    print(f"   🟢 ESTRATÉGIA NOVA (SUPERÁVIT v2.0):")
    print(f"      Total de erros: {total_erros_nova}")
    print(f"      Média de erros: {total_erros_nova/len(detalhes):.2f} por concurso")
    print(f"      Vitórias: {vitorias_nova}")
    print()
    print(f"   🟡 Empates: {empates}")
    print()
    
    # Conclusão
    melhoria = ((total_erros_antiga - total_erros_nova) / total_erros_antiga * 100) if total_erros_antiga > 0 else 0
    
    if total_erros_nova < total_erros_antiga:
        print(f"   ✅ CONCLUSÃO: Nova estratégia é MELHOR!")
        print(f"      Redução de erros: {total_erros_antiga - total_erros_nova} ({melhoria:.1f}%)")
        print(f"      Taxa de vitória: {vitorias_nova}/{len(detalhes)} ({vitorias_nova/len(detalhes)*100:.1f}%)")
    elif total_erros_nova > total_erros_antiga:
        print(f"   ❌ CONCLUSÃO: Estratégia antiga é melhor!")
        print(f"      A nova estratégia teve {total_erros_nova - total_erros_antiga} erros a mais")
    else:
        print(f"   🟡 CONCLUSÃO: Empate técnico (mesma quantidade de erros)")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
