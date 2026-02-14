#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 ANÁLISE COMPLETA DE SOMA - BASE HISTÓRICA TOTAL
==================================================
Valida os thresholds de reversão usando TODOS os concursos
"""

import pyodbc
import numpy as np
from collections import Counter

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def main():
    print("=" * 78)
    print("🔬 ANÁLISE COMPLETA DE SOMA - BASE HISTÓRICA TOTAL")
    print("=" * 78)
    
    # Carregar TODOS os resultados
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
            'soma': sum(nums)
        })
    conn.close()
    
    total = len(resultados)
    print(f"\n✅ {total} concursos carregados (BASE COMPLETA)")
    
    # Estatísticas gerais
    somas = [r['soma'] for r in resultados]
    print(f"\n📊 ESTATÍSTICAS GERAIS DE SOMA:")
    print(f"   • Mínima: {min(somas)}")
    print(f"   • Máxima: {max(somas)}")
    print(f"   • Média: {np.mean(somas):.1f}")
    print(f"   • Mediana: {np.median(somas):.1f}")
    print(f"   • Desvio padrão: {np.std(somas):.1f}")
    
    # Percentis
    print(f"\n   Percentis:")
    for p in [5, 10, 25, 50, 75, 90, 95]:
        print(f"      P{p}: {np.percentile(somas, p):.0f}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE DE REVERSÃO - BASE COMPLETA
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 ANÁLISE DE REVERSÃO - BASE COMPLETA ({} concursos)".format(total))
    print("=" * 78)
    
    thresholds_alta = [200, 205, 210, 215, 220]
    thresholds_baixa = [195, 190, 185, 180, 175]
    
    print("\n   🔴 APÓS SOMA ALTA (tendência de BAIXAR):")
    print(f"   {'Threshold':>10} {'Ocorr.':>8} {'Baixou':>8} {'Subiu':>8} {'%Baixou':>10}")
    print("   " + "-" * 50)
    
    for threshold in thresholds_alta:
        baixou = subiu = 0
        for i in range(1, total):
            if resultados[i-1]['soma'] > threshold:
                if resultados[i]['soma'] < resultados[i-1]['soma']:
                    baixou += 1
                else:
                    subiu += 1
        
        total_casos = baixou + subiu
        if total_casos > 0:
            pct = baixou / total_casos * 100
            print(f"   >{threshold:>8} {total_casos:>8} {baixou:>8} {subiu:>8} {pct:>9.1f}%")
    
    print("\n   🟢 APÓS SOMA BAIXA (tendência de SUBIR):")
    print(f"   {'Threshold':>10} {'Ocorr.':>8} {'Subiu':>8} {'Baixou':>8} {'%Subiu':>10}")
    print("   " + "-" * 50)
    
    for threshold in thresholds_baixa:
        subiu = baixou = 0
        for i in range(1, total):
            if resultados[i-1]['soma'] < threshold:
                if resultados[i]['soma'] > resultados[i-1]['soma']:
                    subiu += 1
                else:
                    baixou += 1
        
        total_casos = subiu + baixou
        if total_casos > 0:
            pct = subiu / total_casos * 100
            print(f"   <{threshold:>8} {total_casos:>8} {subiu:>8} {baixou:>8} {pct:>9.1f}%")
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANÁLISE DETALHADA POR FAIXA
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📊 MOVIMENTO DA SOMA POR FAIXA - BASE COMPLETA")
    print("=" * 78)
    
    faixas = [
        ("<170", lambda s: s < 170),
        ("170-179", lambda s: 170 <= s < 180),
        ("180-189", lambda s: 180 <= s < 190),
        ("190-199", lambda s: 190 <= s < 200),
        ("200-209", lambda s: 200 <= s < 210),
        ("210-219", lambda s: 210 <= s < 220),
        ("≥220", lambda s: s >= 220),
    ]
    
    print(f"\n   {'Faixa':<12} {'Casos':>8} {'Subiu':>8} {'Desceu':>8} {'=':>6} {'%Sub':>8} {'%Des':>8} {'Tend.':>8}")
    print("   " + "-" * 80)
    
    for nome, condicao in faixas:
        subiu = desceu = igual = 0
        for i in range(1, total):
            if condicao(resultados[i-1]['soma']):
                delta = resultados[i]['soma'] - resultados[i-1]['soma']
                if delta > 3:
                    subiu += 1
                elif delta < -3:
                    desceu += 1
                else:
                    igual += 1
        
        total_casos = subiu + desceu + igual
        if total_casos > 0:
            pct_sub = subiu / total_casos * 100
            pct_des = desceu / total_casos * 100
            
            if pct_des > pct_sub + 10:
                tend = "↓ DESCE"
            elif pct_sub > pct_des + 10:
                tend = "↑ SOBE"
            else:
                tend = "≈"
            
            print(f"   {nome:<12} {total_casos:>8} {subiu:>8} {desceu:>8} {igual:>6} {pct_sub:>7.1f}% {pct_des:>7.1f}% {tend:>8}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # VALIDAR THRESHOLDS ESCOLHIDOS
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("🎯 VALIDAÇÃO DOS THRESHOLDS ESCOLHIDOS")
    print("=" * 78)
    
    # Threshold >205 para detectar alta
    print("\n   📌 THRESHOLD >205 (SOMA ALTA):")
    casos_205 = sum(1 for i in range(1, total) if resultados[i-1]['soma'] > 205)
    baixou_205 = sum(1 for i in range(1, total) if resultados[i-1]['soma'] > 205 and resultados[i]['soma'] < resultados[i-1]['soma'])
    if casos_205 > 0:
        print(f"      • Casos: {casos_205}")
        print(f"      • Baixou: {baixou_205} ({baixou_205/casos_205*100:.1f}%)")
        print(f"      ✅ VALIDADO: {baixou_205/casos_205*100:.1f}% de assertividade")
    
    # Threshold <190 para detectar baixa
    print("\n   📌 THRESHOLD <190 (SOMA BAIXA):")
    casos_190 = sum(1 for i in range(1, total) if resultados[i-1]['soma'] < 190)
    subiu_190 = sum(1 for i in range(1, total) if resultados[i-1]['soma'] < 190 and resultados[i]['soma'] > resultados[i-1]['soma'])
    if casos_190 > 0:
        print(f"      • Casos: {casos_190}")
        print(f"      • Subiu: {subiu_190} ({subiu_190/casos_190*100:.1f}%)")
        print(f"      ✅ VALIDADO: {subiu_190/casos_190*100:.1f}% de assertividade")
    
    # Threshold <170 (muito baixa)
    print("\n   📌 THRESHOLD <170 (SOMA MUITO BAIXA):")
    casos_170 = sum(1 for i in range(1, total) if resultados[i-1]['soma'] < 170)
    subiu_170 = sum(1 for i in range(1, total) if resultados[i-1]['soma'] < 170 and resultados[i]['soma'] > resultados[i-1]['soma'])
    if casos_170 > 0:
        print(f"      • Casos: {casos_170}")
        print(f"      • Subiu: {subiu_170} ({subiu_170/casos_170*100:.1f}%)")
        print(f"      ✅ VALIDADO: {subiu_170/casos_170*100:.1f}% de assertividade")
    
    # ═══════════════════════════════════════════════════════════════════════
    # RECOMENDAÇÃO DE FAIXAS IDEAIS
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 78)
    print("📋 RECOMENDAÇÃO DE FAIXAS PARA FILTRO DINÂMICO")
    print("=" * 78)
    
    # Calcular faixa ideal após soma muito baixa (<170)
    somas_apos_muito_baixa = []
    for i in range(1, total):
        if resultados[i-1]['soma'] < 170:
            somas_apos_muito_baixa.append(resultados[i]['soma'])
    
    if somas_apos_muito_baixa:
        p10 = np.percentile(somas_apos_muito_baixa, 10)
        p90 = np.percentile(somas_apos_muito_baixa, 90)
        media = np.mean(somas_apos_muito_baixa)
        print(f"\n   Após SOMA <170 (como o 3611 com 162):")
        print(f"      • Próxima soma média: {media:.0f}")
        print(f"      • Faixa P10-P90: {p10:.0f}-{p90:.0f}")
        print(f"      ➡️ RECOMENDAÇÃO: Filtrar soma {int(p10)}-{int(p90)}")
    
    # Calcular faixa ideal após soma muito alta (>210)
    somas_apos_muito_alta = []
    for i in range(1, total):
        if resultados[i-1]['soma'] > 210:
            somas_apos_muito_alta.append(resultados[i]['soma'])
    
    if somas_apos_muito_alta:
        p10 = np.percentile(somas_apos_muito_alta, 10)
        p90 = np.percentile(somas_apos_muito_alta, 90)
        media = np.mean(somas_apos_muito_alta)
        print(f"\n   Após SOMA >210:")
        print(f"      • Próxima soma média: {media:.0f}")
        print(f"      • Faixa P10-P90: {p10:.0f}-{p90:.0f}")
        print(f"      ➡️ RECOMENDAÇÃO: Filtrar soma {int(p10)}-{int(p90)}")
    
    print("\n" + "=" * 78)
    print("✅ ANÁLISE COMPLETA FINALIZADA!")
    print("=" * 78)

if __name__ == "__main__":
    main()
