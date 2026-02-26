#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VALIDADOR DE RANKING POR QUINTETOS
Compara previsões do índice de débito com resultados reais

Objetivo: Verificar se o ranking "previsto" tem poder preditivo real
"""

import pyodbc
from collections import Counter
from datetime import datetime

def conectar_banco():
    """Conecta ao banco de dados"""
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def carregar_resultados(limite=500):
    """Carrega últimos N resultados"""
    conn = conectar_banco()
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
    
    conn.close()
    return resultados

def calcular_ranking_debito(resultados_anteriores):
    """
    Calcula ranking usando índice de débito (mesma lógica do super_menu.py)
    
    Retorna lista ordenada: [{'num': N, 'score': S, 'debito': D}, ...]
    """
    FREQ_ESPERADA = 60
    
    def freq_janela(tamanho):
        freq = Counter()
        for r in resultados_anteriores[:min(tamanho, len(resultados_anteriores))]:
            freq.update(r['numeros'])
        return {n: freq.get(n, 0) / min(tamanho, len(resultados_anteriores)) * 100 for n in range(1, 26)}
    
    freq_5 = freq_janela(5)
    freq_50 = freq_janela(50)
    
    ranking = []
    for n in range(1, 26):
        fc = freq_5[n]
        fl = freq_50[n]
        indice_debito = fl - fc
        
        score = 0
        apareceu_recente = any(n in r['numeros'] for r in resultados_anteriores[:3])
        
        if apareceu_recente:
            score += 2
        
        if indice_debito >= 20:
            score += 6
        elif indice_debito >= 10:
            score += 4
        elif indice_debito >= 0:
            score += 2
        elif indice_debito > -15:
            score += 0
        else:
            score -= 3
        
        if fl >= FREQ_ESPERADA:
            score += 1
        
        ranking.append({'num': n, 'score': score, 'debito': indice_debito, 'freq_5': fc, 'freq_50': fl})
    
    ranking.sort(key=lambda x: (-x['score'], x['debito']))
    return ranking

def validar_previsoes(n_concursos=100):
    """
    Valida previsões comparando ranking previsto com resultado real
    
    Para cada concurso:
    1. Usa os 50 anteriores para calcular ranking
    2. Compara com o resultado real
    3. Mede quantos do TOP 5/10/15 acertaram
    """
    print("\n" + "="*70)
    print("🔬 VALIDADOR DE RANKING POR QUINTETOS")
    print("="*70)
    print(f"📊 Analisando {n_concursos} concursos...")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Carregar dados (precisamos de n_concursos + 50 para ter histórico)
    resultados = carregar_resultados(n_concursos + 60)
    
    if len(resultados) < n_concursos + 50:
        print(f"⚠️ Dados insuficientes. Disponíveis: {len(resultados)}")
        n_concursos = len(resultados) - 50
    
    # Estatísticas por quinteto
    stats = {
        'TOP_5': {'total': 0, 'acertos': 0},
        'ALTOS': {'total': 0, 'acertos': 0},
        'MEDIO': {'total': 0, 'acertos': 0},
        'BAIXOS': {'total': 0, 'acertos': 0},
        'PIORES': {'total': 0, 'acertos': 0}
    }
    
    # Para análise detalhada
    acertos_por_quinteto = []
    
    # Iterar sobre concursos (do mais antigo para o mais recente)
    for i in range(n_concursos - 1, -1, -1):
        # Resultado real do concurso atual
        resultado_real = resultados[i]
        concurso = resultado_real['concurso']
        numeros_sorteados = resultado_real['numeros']
        
        # Usar os 50 anteriores para calcular ranking
        historico = resultados[i+1:i+51]  # 50 concursos anteriores
        
        if len(historico) < 50:
            continue
        
        # Calcular ranking previsto
        ranking = calcular_ranking_debito(historico)
        
        # Dividir em quintetos
        top_5 = set(r['num'] for r in ranking[:5])
        altos = set(r['num'] for r in ranking[5:10])
        medio = set(r['num'] for r in ranking[10:15])
        baixos = set(r['num'] for r in ranking[15:20])
        piores = set(r['num'] for r in ranking[20:25])
        
        # Contar acertos por quinteto
        acertos_top5 = len(top_5 & numeros_sorteados)
        acertos_altos = len(altos & numeros_sorteados)
        acertos_medio = len(medio & numeros_sorteados)
        acertos_baixos = len(baixos & numeros_sorteados)
        acertos_piores = len(piores & numeros_sorteados)
        
        # Acumular
        stats['TOP_5']['total'] += 5
        stats['TOP_5']['acertos'] += acertos_top5
        stats['ALTOS']['total'] += 5
        stats['ALTOS']['acertos'] += acertos_altos
        stats['MEDIO']['total'] += 5
        stats['MEDIO']['acertos'] += acertos_medio
        stats['BAIXOS']['total'] += 5
        stats['BAIXOS']['acertos'] += acertos_baixos
        stats['PIORES']['total'] += 5
        stats['PIORES']['acertos'] += acertos_piores
        
        acertos_por_quinteto.append({
            'concurso': concurso,
            'top5': acertos_top5,
            'altos': acertos_altos,
            'medio': acertos_medio,
            'baixos': acertos_baixos,
            'piores': acertos_piores
        })
    
    # Calcular estatísticas
    print("\n" + "─"*70)
    print("📊 RESULTADO DA VALIDAÇÃO")
    print("─"*70)
    print(f"\n📈 Concursos analisados: {len(acertos_por_quinteto)}")
    print(f"   (Cada concurso foi previsto usando os 50 anteriores)\n")
    
    # Expectativa aleatória: 15 números de 25 = 60% por quinteto = 3 de 5
    EXPECTATIVA = 3.0
    
    print("┌────────────┬─────────┬────────────┬───────────┬────────────────┐")
    print("│  Quinteto  │ Acertos │   Taxa %   │ Esperado* │   Diferença    │")
    print("├────────────┼─────────┼────────────┼───────────┼────────────────┤")
    
    for nome, dados in stats.items():
        if dados['total'] > 0:
            taxa = dados['acertos'] / dados['total'] * 100
            media_acertos = dados['acertos'] / len(acertos_por_quinteto)
            diff = media_acertos - EXPECTATIVA
            diff_pct = (media_acertos / EXPECTATIVA - 1) * 100
            
            # Indicador visual
            if diff > 0.3:
                indicador = f"✅ +{diff:.2f} (+{diff_pct:.1f}%)"
            elif diff < -0.3:
                indicador = f"❌ {diff:.2f} ({diff_pct:.1f}%)"
            else:
                indicador = f"➖ {diff:+.2f} ({diff_pct:+.1f}%)"
            
            print(f"│ {nome:^10} │ {dados['acertos']:>7} │ {taxa:>9.1f}% │ {EXPECTATIVA:>9.1f} │ {indicador:^14} │")
    
    print("└────────────┴─────────┴────────────┴───────────┴────────────────┘")
    print("\n* Esperado aleatório: 3.0 acertos por quinteto (15/25 = 60%)")
    
    # Análise de distribuição
    print("\n" + "─"*70)
    print("📊 DISTRIBUIÇÃO DE ACERTOS POR QUINTETO")
    print("─"*70)
    
    for nome_q, idx in [('TOP_5', 'top5'), ('ALTOS', 'altos'), ('MEDIO', 'medio'), ('BAIXOS', 'baixos'), ('PIORES', 'piores')]:
        dist = Counter(a[idx] for a in acertos_por_quinteto)
        total = len(acertos_por_quinteto)
        
        print(f"\n{nome_q}:")
        for acertos in range(6):
            count = dist.get(acertos, 0)
            pct = count / total * 100
            bar = '█' * int(pct / 2)
            print(f"  {acertos} acertos: {count:>4} ({pct:>5.1f}%) {bar}")
    
    # Conclusão
    print("\n" + "="*70)
    print("📋 CONCLUSÃO")
    print("="*70)
    
    # Calcular efetividade
    top5_media = stats['TOP_5']['acertos'] / len(acertos_por_quinteto)
    piores_media = stats['PIORES']['acertos'] / len(acertos_por_quinteto)
    diferenca = top5_media - piores_media
    
    print(f"\n🎯 Média de acertos TOP 5:  {top5_media:.2f} números por concurso")
    print(f"📉 Média de acertos PIORES: {piores_media:.2f} números por concurso")
    print(f"📊 Diferença:               {diferenca:+.2f} números")
    
    if diferenca > 0.5:
        print(f"\n✅ O RANKING TEM PODER PREDITIVO!")
        print(f"   TOP 5 acerta {(diferenca/EXPECTATIVA)*100:.1f}% mais que o esperado vs PIORES")
    elif diferenca > 0.2:
        print(f"\n⚠️ O RANKING TEM LEVE PODER PREDITIVO")
        print(f"   Diferença é pequena mas consistente")
    else:
        print(f"\n❌ O RANKING NÃO TEM PODER PREDITIVO SIGNIFICATIVO")
        print(f"   Diferença entre TOP e PIORES é estatisticamente irrelevante")
    
    return stats, acertos_por_quinteto

def analisar_numeros_extremos(n_concursos=100):
    """
    Analisa números que estavam em extremos do ranking (muito quente/muito frio)
    e verifica se a previsão se confirmou
    """
    print("\n" + "="*70)
    print("🔬 ANÁLISE DE NÚMEROS EM EXTREMOS")
    print("="*70)
    
    resultados = carregar_resultados(n_concursos + 60)
    
    # Rastrear números com débito extremo
    casos_debito_alto = []   # Débito >= 20 (deve sair)
    casos_debito_baixo = []  # Débito <= -15 (não deve sair)
    
    for i in range(min(n_concursos, len(resultados) - 51)):
        resultado_real = resultados[i]
        concurso = resultado_real['concurso']
        numeros_sorteados = resultado_real['numeros']
        
        historico = resultados[i+1:i+51]
        ranking = calcular_ranking_debito(historico)
        
        for r in ranking:
            if r['debito'] >= 20:
                saiu = r['num'] in numeros_sorteados
                casos_debito_alto.append({
                    'concurso': concurso,
                    'num': r['num'],
                    'debito': r['debito'],
                    'saiu': saiu
                })
            elif r['debito'] <= -15:
                saiu = r['num'] in numeros_sorteados
                casos_debito_baixo.append({
                    'concurso': concurso,
                    'num': r['num'],
                    'debito': r['debito'],
                    'saiu': saiu
                })
    
    # Estatísticas
    print(f"\n📈 NÚMEROS COM DÉBITO ALTO (≥ +20) - 'Devem sair'")
    print("─"*50)
    if casos_debito_alto:
        acertos = sum(1 for c in casos_debito_alto if c['saiu'])
        total = len(casos_debito_alto)
        taxa = acertos / total * 100
        print(f"   Casos encontrados: {total}")
        print(f"   Acertaram (saíram): {acertos} ({taxa:.1f}%)")
        print(f"   Esperado aleatório: 60%")
        diff = taxa - 60
        if diff > 5:
            print(f"   ✅ Acima do esperado em {diff:.1f}%")
        elif diff < -5:
            print(f"   ❌ Abaixo do esperado em {abs(diff):.1f}%")
        else:
            print(f"   ➖ Próximo ao esperado ({diff:+.1f}%)")
    
    print(f"\n📉 NÚMEROS COM DÉBITO BAIXO (≤ -15) - 'Não devem sair'")
    print("─"*50)
    if casos_debito_baixo:
        acertos = sum(1 for c in casos_debito_baixo if not c['saiu'])
        total = len(casos_debito_baixo)
        taxa = acertos / total * 100
        taxa_saiu = (total - acertos) / total * 100
        print(f"   Casos encontrados: {total}")
        print(f"   Acertaram (NÃO saíram): {acertos} ({taxa:.1f}%)")
        print(f"   Taxa de saída real: {taxa_saiu:.1f}%")
        print(f"   Esperado aleatório: 60% sair, 40% não sair")
        if taxa_saiu < 55:
            print(f"   ✅ Saíram MENOS que o esperado! Métrica funciona")
        elif taxa_saiu > 65:
            print(f"   ❌ Saíram MAIS que o esperado! Métrica não funciona")
        else:
            print(f"   ➖ Próximo ao esperado")
    
    return casos_debito_alto, casos_debito_baixo

def menu_principal():
    """Menu principal de validação"""
    while True:
        print("\n" + "="*70)
        print("🔬 VALIDADOR DE RANKING POR QUINTETOS")
        print("="*70)
        print("\n1. Validar previsões (100 concursos)")
        print("2. Validar previsões (personalizado)")
        print("3. Analisar números em extremos")
        print("4. Validação completa (todos os testes)")
        print("0. Sair")
        
        opcao = input("\nEscolha: ").strip()
        
        if opcao == '1':
            validar_previsoes(100)
        elif opcao == '2':
            n = input("Quantos concursos? [100]: ").strip()
            n = int(n) if n.isdigit() else 100
            validar_previsoes(n)
        elif opcao == '3':
            analisar_numeros_extremos(100)
        elif opcao == '4':
            print("\n🔄 Executando validação completa...")
            validar_previsoes(200)
            analisar_numeros_extremos(200)
        elif opcao == '0':
            break
        
        input("\n\nPressione ENTER para continuar...")

if __name__ == "__main__":
    # Executar validação completa diretamente
    print("\n🔄 Executando validação completa...")
    validar_previsoes(200)
    analisar_numeros_extremos(200)
