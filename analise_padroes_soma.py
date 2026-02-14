#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 ANÁLISE DE PADRÕES DE SOMA - LOTOFÁCIL
==========================================
Analisa:
1. Quando soma é alta (>200), ela sobe, desce ou mantém?
2. Existe padrão cíclico de somas altas/baixas?
3. Correlação soma vs saldo posicional
4. Correlação soma vs ímpares/pares
"""

import pyodbc
import numpy as np
from collections import Counter, defaultdict

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def carregar_dados():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso ASC
    """)
    
    resultados = []
    for row in cursor.fetchall():
        nums = list(row[1:16])
        resultados.append({
            'concurso': row[0],
            'numeros': nums,
            'soma': sum(nums),
            'impares': sum(1 for n in nums if n % 2 == 1),
            'pares': sum(1 for n in nums if n % 2 == 0)
        })
    conn.close()
    return resultados

def calcular_saldo_posicional(res_ant, res_atual):
    """Calcula saldo posicional entre dois sorteios consecutivos."""
    nums_ant = set(res_ant['numeros'])
    nums_atual = set(res_atual['numeros'])
    repetidos = nums_ant & nums_atual
    
    if not repetidos:
        return 0
    
    subiu = desceu = 0
    for num in repetidos:
        try:
            pos_ant = res_ant['numeros'].index(num) + 1
            pos_atual = res_atual['numeros'].index(num) + 1
        except:
            continue
        if pos_atual < pos_ant:
            subiu += 1
        elif pos_atual > pos_ant:
            desceu += 1
    return subiu - desceu

def main():
    print("=" * 78)
    print("🔬 ANÁLISE DE PADRÕES DE SOMA - LOTOFÁCIL")
    print("=" * 78)
    
    resultados = carregar_dados()
    print(f"✅ {len(resultados)} concursos carregados")
    
    # Calcular saldo posicional para cada concurso
    for i in range(1, len(resultados)):
        resultados[i]['saldo_pos'] = calcular_saldo_posicional(resultados[i-1], resultados[i])
    resultados[0]['saldo_pos'] = 0
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE 1: ÚLTIMOS CONCURSOS
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ÚLTIMOS 10 CONCURSOS")
    print("=" * 78)
    
    print(f"\n   {'Conc':<6} {'Soma':>6} {'Δ Soma':>8} {'Ímpares':>8} {'Saldo Pos':>10} {'Movimento'}")
    print("   " + "-" * 60)
    
    for i in range(-10, 0):
        r = resultados[i]
        r_ant = resultados[i-1]
        delta_soma = r['soma'] - r_ant['soma']
        
        if delta_soma > 5:
            mov = "↑ SUBIU"
        elif delta_soma < -5:
            mov = "↓ DESCEU"
        else:
            mov = "≈ estável"
        
        print(f"   {r['concurso']:<6} {r['soma']:>6} {delta_soma:>+8} {r['impares']:>8} {r['saldo_pos']:>+10} {mov}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE 2: MOVIMENTO DA SOMA APÓS VALORES ALTOS/BAIXOS
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 2: MOVIMENTO DA SOMA APÓS EXTREMOS")
    print("=" * 78)
    
    # Usar últimos 500 concursos
    dados = resultados[-500:]
    
    # Após soma ALTA (>205)
    apos_alta = {'subiu': 0, 'desceu': 0, 'manteve': 0}
    # Após soma MUITO ALTA (>210)
    apos_muito_alta = {'subiu': 0, 'desceu': 0, 'manteve': 0}
    # Após soma BAIXA (<195)
    apos_baixa = {'subiu': 0, 'desceu': 0, 'manteve': 0}
    # Após soma MUITO BAIXA (<190)
    apos_muito_baixa = {'subiu': 0, 'desceu': 0, 'manteve': 0}
    
    for i in range(1, len(dados)):
        soma_ant = dados[i-1]['soma']
        soma_atual = dados[i]['soma']
        delta = soma_atual - soma_ant
        
        def classificar(delta):
            if delta > 3:
                return 'subiu'
            elif delta < -3:
                return 'desceu'
            else:
                return 'manteve'
        
        if soma_ant > 205:
            apos_alta[classificar(delta)] += 1
        if soma_ant > 210:
            apos_muito_alta[classificar(delta)] += 1
        if soma_ant < 195:
            apos_baixa[classificar(delta)] += 1
        if soma_ant < 190:
            apos_muito_baixa[classificar(delta)] += 1
    
    def mostrar_stats(nome, stats):
        total = sum(stats.values())
        if total == 0:
            return
        print(f"\n   {nome} ({total} ocorrências):")
        print(f"      → Subiu:   {stats['subiu']:3d} ({stats['subiu']/total*100:5.1f}%)")
        print(f"      → Desceu:  {stats['desceu']:3d} ({stats['desceu']/total*100:5.1f}%)")
        print(f"      → Manteve: {stats['manteve']:3d} ({stats['manteve']/total*100:5.1f}%)")
        
        # Conclusão
        if stats['desceu'] > stats['subiu'] * 1.3:
            print(f"      ✅ TENDE A DESCER!")
        elif stats['subiu'] > stats['desceu'] * 1.3:
            print(f"      ✅ TENDE A SUBIR!")
        else:
            print(f"      ≈ Sem tendência clara")
    
    mostrar_stats("Após SOMA ALTA (>205)", apos_alta)
    mostrar_stats("Após SOMA MUITO ALTA (>210)", apos_muito_alta)
    mostrar_stats("Após SOMA BAIXA (<195)", apos_baixa)
    mostrar_stats("Após SOMA MUITO BAIXA (<190)", apos_muito_baixa)
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE 3: SEQUÊNCIAS DE SOMA ALTA/BAIXA
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 3: SEQUÊNCIAS DE SOMA ALTA/BAIXA")
    print("=" * 78)
    
    LIMITE_ALTA = 200
    LIMITE_BAIXA = 200
    
    # Encontrar sequências
    seq_altas = []  # Lista de tamanhos de sequências altas
    seq_baixas = []
    
    seq_atual = 0
    tipo_atual = None
    
    for r in dados:
        if r['soma'] >= LIMITE_ALTA:
            if tipo_atual == 'alta':
                seq_atual += 1
            else:
                if tipo_atual == 'baixa' and seq_atual > 0:
                    seq_baixas.append(seq_atual)
                seq_atual = 1
                tipo_atual = 'alta'
        else:
            if tipo_atual == 'baixa':
                seq_atual += 1
            else:
                if tipo_atual == 'alta' and seq_atual > 0:
                    seq_altas.append(seq_atual)
                seq_atual = 1
                tipo_atual = 'baixa'
    
    # Finalizar última sequência
    if tipo_atual == 'alta':
        seq_altas.append(seq_atual)
    else:
        seq_baixas.append(seq_atual)
    
    print(f"\n   SEQUÊNCIAS DE SOMA ≥{LIMITE_ALTA}:")
    if seq_altas:
        print(f"      • Total de sequências: {len(seq_altas)}")
        print(f"      • Tamanho médio: {np.mean(seq_altas):.1f} concursos")
        print(f"      • Tamanho máximo: {max(seq_altas)} concursos")
        print(f"      • Distribuição: {Counter(seq_altas).most_common(5)}")
    
    print(f"\n   SEQUÊNCIAS DE SOMA <{LIMITE_BAIXA}:")
    if seq_baixas:
        print(f"      • Total de sequências: {len(seq_baixas)}")
        print(f"      • Tamanho médio: {np.mean(seq_baixas):.1f} concursos")
        print(f"      • Tamanho máximo: {max(seq_baixas)} concursos")
        print(f"      • Distribuição: {Counter(seq_baixas).most_common(5)}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE 4: CORRELAÇÃO SOMA vs SALDO POSICIONAL
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 4: CORRELAÇÃO SOMA vs SALDO POSICIONAL")
    print("=" * 78)
    
    # Quando soma é alta, o saldo posicional é positivo ou negativo?
    soma_alta_saldo = []
    soma_baixa_saldo = []
    
    for r in dados:
        if r['soma'] > 205:
            soma_alta_saldo.append(r['saldo_pos'])
        elif r['soma'] < 195:
            soma_baixa_saldo.append(r['saldo_pos'])
    
    if soma_alta_saldo:
        print(f"\n   Quando SOMA > 205:")
        print(f"      • Saldo posicional médio: {np.mean(soma_alta_saldo):+.2f}")
        print(f"      • % com saldo positivo: {sum(1 for s in soma_alta_saldo if s > 0)/len(soma_alta_saldo)*100:.1f}%")
        print(f"      • % com saldo negativo: {sum(1 for s in soma_alta_saldo if s < 0)/len(soma_alta_saldo)*100:.1f}%")
    
    if soma_baixa_saldo:
        print(f"\n   Quando SOMA < 195:")
        print(f"      • Saldo posicional médio: {np.mean(soma_baixa_saldo):+.2f}")
        print(f"      • % com saldo positivo: {sum(1 for s in soma_baixa_saldo if s > 0)/len(soma_baixa_saldo)*100:.1f}%")
        print(f"      • % com saldo negativo: {sum(1 for s in soma_baixa_saldo if s < 0)/len(soma_baixa_saldo)*100:.1f}%")
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE 5: CORRELAÇÃO SOMA vs ÍMPARES
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 5: CORRELAÇÃO SOMA vs ÍMPARES/PARES")
    print("=" * 78)
    
    impares_por_faixa = defaultdict(list)
    for r in dados:
        if r['soma'] < 190:
            impares_por_faixa['<190'].append(r['impares'])
        elif r['soma'] < 200:
            impares_por_faixa['190-199'].append(r['impares'])
        elif r['soma'] < 210:
            impares_por_faixa['200-209'].append(r['impares'])
        else:
            impares_por_faixa['≥210'].append(r['impares'])
    
    print(f"\n   {'Faixa Soma':<12} {'Qtd':>6} {'Ímpares Médio':>14} {'Pares Médio':>12}")
    print("   " + "-" * 50)
    for faixa in ['<190', '190-199', '200-209', '≥210']:
        if faixa in impares_por_faixa:
            imp = impares_por_faixa[faixa]
            media_imp = np.mean(imp)
            media_par = 15 - media_imp
            print(f"   {faixa:<12} {len(imp):>6} {media_imp:>14.1f} {media_par:>12.1f}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE 6: REVERSÃO À MÉDIA DA SOMA
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 6: REVERSÃO À MÉDIA DA SOMA")
    print("=" * 78)
    
    soma_media = np.mean([r['soma'] for r in dados])
    print(f"\n   Soma média histórica: {soma_media:.1f}")
    
    # Após soma muito acima da média
    acima_reversao = 0
    acima_continua = 0
    
    for i in range(1, len(dados)):
        if dados[i-1]['soma'] > soma_media + 10:  # >10 acima da média
            if dados[i]['soma'] < dados[i-1]['soma']:  # Desceu
                acima_reversao += 1
            else:
                acima_continua += 1
    
    total_acima = acima_reversao + acima_continua
    if total_acima > 0:
        print(f"\n   Após soma >10 acima da média (>{soma_media+10:.0f}):")
        print(f"      • Reverte (desce): {acima_reversao} ({acima_reversao/total_acima*100:.1f}%)")
        print(f"      • Continua alta: {acima_continua} ({acima_continua/total_acima*100:.1f}%)")
    
    # Após soma muito abaixo da média
    abaixo_reversao = 0
    abaixo_continua = 0
    
    for i in range(1, len(dados)):
        if dados[i-1]['soma'] < soma_media - 10:  # >10 abaixo da média
            if dados[i]['soma'] > dados[i-1]['soma']:  # Subiu
                abaixo_reversao += 1
            else:
                abaixo_continua += 1
    
    total_abaixo = abaixo_reversao + abaixo_continua
    if total_abaixo > 0:
        print(f"\n   Após soma >10 abaixo da média (<{soma_media-10:.0f}):")
        print(f"      • Reverte (sobe): {abaixo_reversao} ({abaixo_reversao/total_abaixo*100:.1f}%)")
        print(f"      • Continua baixa: {abaixo_continua} ({abaixo_continua/total_abaixo*100:.1f}%)")
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE 7: CICLOS DE SOMA
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 7: PADRÃO CÍCLICO DA SOMA")
    print("=" * 78)
    
    # Verificar se há padrão após 2, 3, 4 sorteios altos consecutivos
    for n_altos in [2, 3, 4]:
        conta_desce = 0
        conta_continua = 0
        
        for i in range(n_altos, len(dados)):
            # Verificar se os últimos n sorteios foram altos
            todos_altos = all(dados[i-j-1]['soma'] >= 200 for j in range(n_altos))
            if todos_altos:
                if dados[i]['soma'] < 200:
                    conta_desce += 1
                else:
                    conta_continua += 1
        
        total = conta_desce + conta_continua
        if total > 10:
            print(f"\n   Após {n_altos} concursos consecutivos com SOMA ≥200:")
            print(f"      • Desce (<200): {conta_desce} ({conta_desce/total*100:.1f}%)")
            print(f"      • Continua alta: {conta_continua} ({conta_continua/total*100:.1f}%)")
            if conta_desce > conta_continua * 1.2:
                print(f"      ✅ PADRÃO: Após {n_altos} altas, tende a CAIR!")
    
    # ═══════════════════════════════════════════════════════════════════════
    # CONCLUSÕES
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("🎯 CONCLUSÕES PARA ESTRATÉGIA")
    print("=" * 78)
    
    # Verificar situação atual
    ultimos = resultados[-3:]
    print(f"\n   SITUAÇÃO ATUAL (últimos 3 concursos):")
    for r in ultimos:
        status = "ALTA" if r['soma'] >= 200 else "BAIXA"
        print(f"      • {r['concurso']}: soma={r['soma']} ({status})")
    
    # Contar sequência atual
    seq_alta_atual = 0
    for r in reversed(resultados[-10:]):
        if r['soma'] >= 200:
            seq_alta_atual += 1
        else:
            break
    
    if seq_alta_atual >= 2:
        print(f"\n   ⚠️ {seq_alta_atual} concursos consecutivos com soma ≥200")
        print(f"   → Baseado na análise, próximo sorteio pode ter soma MENOR")
    
    print("\n" + "=" * 78)
    print("✅ ANÁLISE CONCLUÍDA!")
    print("=" * 78)

if __name__ == "__main__":
    main()
