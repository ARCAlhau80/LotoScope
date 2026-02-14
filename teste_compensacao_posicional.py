#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 TESTE DO FILTRO DE COMPENSAÇÃO POSICIONAL
============================================
Verifica se o filtro está funcionando corretamente
"""

import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def main():
    print("=" * 70)
    print("🔬 TESTE DO FILTRO DE COMPENSAÇÃO POSICIONAL")
    print("=" * 70)
    
    # Carregar últimos resultados
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 3 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            'concurso': row[0],
            'numeros': list(row[1:16])
        })
    conn.close()
    
    print(f"\n📋 Últimos 3 concursos:")
    for r in resultados:
        print(f"   {r['concurso']}: {r['numeros']}")
    
    # Funções
    def encontrar_posicao(resultado, numero):
        for pos in range(15):
            if resultado['numeros'][pos] == numero:
                return pos + 1
        return None
    
    def calcular_saldo_posicional(res_anterior, res_atual):
        nums_ant = set(res_anterior['numeros'])
        nums_atual = set(res_atual['numeros'])
        repetidos = nums_ant & nums_atual
        
        if not repetidos:
            return 0, 0, 0, 0
        
        subiu = desceu = mesma = 0
        for num in repetidos:
            pos_ant = encontrar_posicao(res_anterior, num)
            pos_atual = encontrar_posicao(res_atual, num)
            if pos_atual < pos_ant:
                subiu += 1
            elif pos_atual > pos_ant:
                desceu += 1
            else:
                mesma += 1
        return subiu - desceu, len(repetidos), subiu, desceu
    
    # Calcular saldos
    print("\n📊 ANÁLISE DE SALDO POSICIONAL:")
    
    # Entre concurso -2 e -1
    saldo_ant, rep_ant, sub_ant, desc_ant = calcular_saldo_posicional(resultados[2], resultados[1])
    print(f"\n   Concurso {resultados[2]['concurso']} → {resultados[1]['concurso']}:")
    print(f"   • Repetidos: {rep_ant}")
    print(f"   • Subiram: {sub_ant}, Desceram: {desc_ant}")
    print(f"   • Saldo: {saldo_ant:+d}")
    
    # Entre concurso -1 e último
    saldo_ult, rep_ult, sub_ult, desc_ult = calcular_saldo_posicional(resultados[1], resultados[0])
    print(f"\n   Concurso {resultados[1]['concurso']} → {resultados[0]['concurso']} (ÚLTIMO):")
    print(f"   • Repetidos: {rep_ult}")
    print(f"   • Subiram: {sub_ult}, Desceram: {desc_ult}")
    print(f"   • Saldo: {saldo_ult:+d}")
    
    # Determinar compensação
    print("\n" + "=" * 70)
    print("🎯 RESULTADO PARA PRÓXIMO SORTEIO:")
    print("=" * 70)
    
    if saldo_ult < -2:
        print(f"\n   ✅ COMPENSAÇÃO ATIVA: Tendência SUBIR")
        print(f"   → Saldo {saldo_ult} indica que muitos números DESCERAM")
        print(f"   → Próximo sorteio: espera-se que mais números SUBAM de posição")
        print(f"   → Filtro vai priorizar combinações com saldo POSITIVO")
    elif saldo_ult > 2:
        print(f"\n   ✅ COMPENSAÇÃO ATIVA: Tendência DESCER")
        print(f"   → Saldo +{saldo_ult} indica que muitos números SUBIRAM")
        print(f"   → Próximo sorteio: espera-se que mais números DESÇAM de posição")
        print(f"   → Filtro vai priorizar combinações com saldo NEGATIVO")
    else:
        print(f"\n   ⚖️ Saldo equilibrado ({saldo_ult:+d})")
        print(f"   → Sem compensação forte detectada")
        print(f"   → Filtro de compensação NÃO será aplicado")
    
    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
