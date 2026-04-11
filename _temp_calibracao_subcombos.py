# -*- coding: utf-8 -*-
"""
Calibração do filtro de sub-combos quentes.
Compara: sorteios reais vs combos aleatórios de Pool 23.
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lotofacil_lite', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lotofacil_lite', 'interfaces'))

from database_config import DatabaseConfig
from filtro_subcombos_quentes import FiltroSubcombosQuentes
from itertools import combinations
import random

print("=" * 70)
print("CALIBRAÇÃO DO FILTRO SUB-COMBOS QUENTES")
print("=" * 70)

# Testar diferentes thresholds de QTDE_ACERTOS
for min_ac in [6, 7, 8, 9, 10]:
    filtro = FiltroSubcombosQuentes()
    filtro.carregar(min_acertos=min_ac, verbose=True)
    
    # Pegar últimos 50 sorteios reais
    db = DatabaseConfig()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    # Analisar últimos 50 reais
    reais_hot = []
    for row in rows[:50]:
        combo = list(row[1:16])
        hot = filtro.contar_hot(combo)
        reais_hot.append(hot)
    
    # Gerar 50 combos aleatórios (pool 23 = excluir 2 dos 25)
    random.seed(42)
    aleatorios_hot = []
    for _ in range(50):
        pool = list(range(1, 26))
        excluir = random.sample(pool, 2)
        pool23 = [n for n in pool if n not in excluir]
        combo = sorted(random.sample(pool23, 15))
        hot = filtro.contar_hot(combo)
        aleatorios_hot.append(hot)
    
    avg_real = sum(reais_hot) / len(reais_hot)
    avg_alea = sum(aleatorios_hot) / len(aleatorios_hot)
    min_real = min(reais_hot)
    max_real = max(reais_hot)
    min_alea = min(aleatorios_hot)
    max_alea = max(aleatorios_hot)
    
    # Percentis
    reais_sorted = sorted(reais_hot)
    p10_real = reais_sorted[4]   # 10th percentile
    p25_real = reais_sorted[12]  # 25th percentile
    p50_real = reais_sorted[24]  # median
    
    print(f"\n   --- min_acertos={min_ac} | hot_set={filtro.hot_count:,} ---")
    print(f"   REAIS (50):      avg={avg_real:.0f}  min={min_real}  p10={p10_real}  p25={p25_real}  med={p50_real}  max={max_real}")
    print(f"   ALEATÓRIOS (50): avg={avg_alea:.0f}  min={min_alea}  max={max_alea}")
    print(f"   LIFT: {avg_real/avg_alea:.2f}x" if avg_alea > 0 else "   LIFT: N/A")
    
    # Testar thresholds
    for thr in [p10_real, p25_real]:
        reais_pass = sum(1 for h in reais_hot if h >= thr)
        alea_pass = sum(1 for h in aleatorios_hot if h >= thr)
        print(f"   threshold>={thr}: reais={reais_pass}/50 ({reais_pass*2}%) | "
              f"aleat={alea_pass}/50 ({alea_pass*2}%)")

print("\n✅ Calibração concluída!")
