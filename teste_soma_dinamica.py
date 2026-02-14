#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 TESTE DO SISTEMA DE SOMA DINÂMICA
=====================================
Mostra como a soma será ajustada baseado no último sorteio
"""

import pyodbc

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def main():
    print("=" * 70)
    print("🔬 TESTE DO SISTEMA DE SOMA DINÂMICA")
    print("=" * 70)
    
    # Carregar últimos resultados
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 5 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
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
    
    print(f"\n📋 Últimos 5 concursos:")
    for r in resultados:
        status = "🔴 ALTA" if r['soma'] > 205 else ("🟢 BAIXA" if r['soma'] < 190 else "🟡 MÉDIA")
        print(f"   {r['concurso']}: soma={r['soma']:3d} {status}")
    
    # Analisar último
    soma_ultimo = resultados[0]['soma']
    
    print("\n" + "=" * 70)
    print("🎯 AJUSTE DE SOMA PARA PRÓXIMO SORTEIO")
    print("=" * 70)
    
    print(f"\n   Soma do último sorteio: {soma_ultimo}")
    
    # Determinar ajustes - OTIMIZADO com base em 3610 concursos
    if soma_ultimo < 170:
        tendencia = 'ALTA_FORTE'
        soma_ajuste = (180, 215)
        soma_ajuste_ultra = (190, 210)
        assertividade = "97% (270 casos)"
    elif soma_ultimo < 180:
        tendencia = 'ALTA'
        soma_ajuste = (185, 215)
        soma_ajuste_ultra = (190, 212)
        assertividade = "92.7% (449 casos)"
    elif soma_ultimo < 190:
        tendencia = 'ALTA_MODERADA'
        soma_ajuste = (185, 212)
        soma_ajuste_ultra = (188, 210)
        assertividade = "86.3% (1019 casos)"
    elif soma_ultimo >= 220:
        tendencia = 'BAIXA_FORTE'
        soma_ajuste = (175, 208)
        soma_ajuste_ultra = (180, 200)
        assertividade = "95% (278 casos)"
    elif soma_ultimo >= 210:
        tendencia = 'BAIXA'
        soma_ajuste = (178, 205)
        soma_ajuste_ultra = (180, 200)
        assertividade = "89.9% (759 casos)"
    elif soma_ultimo > 205:
        tendencia = 'BAIXA_MODERADA'
        soma_ajuste = (182, 208)
        soma_ajuste_ultra = (185, 203)
        assertividade = "85.4% (1060 casos)"
    elif soma_ultimo > 200:
        tendencia = 'BAIXA_LEVE'
        soma_ajuste = (185, 210)
        soma_ajuste_ultra = (185, 205)
        assertividade = "80.4% (1395 casos)"
    else:
        tendencia = None
        soma_ajuste = None
        soma_ajuste_ultra = None
        assertividade = "N/A - zona equilibrada"
    
    if tendencia:
        print(f"\n   ✅ REVERSÃO DETECTADA: tendência {tendencia}")
        print(f"   📊 Assertividade histórica: {assertividade}")
        
        print(f"\n   📋 AJUSTES POR NÍVEL:")
        print(f"   ┌─────────┬───────────────┬─────────────────┐")
        print(f"   │ Nível   │ Soma Original │ Soma Ajustada   │")
        print(f"   ├─────────┼───────────────┼─────────────────┤")
        
        niveis_originais = {
            1: (180, 230),
            2: (185, 225),
            3: (190, 220),
            4: (195, 215),
            5: (195, 215),
            6: (200, 210)
        }
        
        for nivel, orig in niveis_originais.items():
            if nivel == 6:
                ajust = soma_ajuste_ultra
            else:
                ajust = soma_ajuste
            
            print(f"   │   {nivel}     │   {orig[0]}-{orig[1]}     │   {ajust[0]}-{ajust[1]}         │")
        
        print(f"   └─────────┴───────────────┴─────────────────┘")
    else:
        print(f"\n   ⚖️ Soma equilibrada ({soma_ultimo}) - sem reversão forte")
        print(f"   → Filtros de soma usarão valores padrão")
    
    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
