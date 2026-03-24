"""
Diagnóstico: Como funciona o filtro de Posições Frias
Exercício: Janela 6 concursos (3495-3500) → Prever para 3501
"""
import pyodbc
from collections import defaultdict

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Buscar concursos 3495 a 3501
cursor.execute('''
    SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT 
    WHERE Concurso BETWEEN 3495 AND 3501
    ORDER BY Concurso ASC
''')
rows = cursor.fetchall()

# Buscar TODO o histórico até 3500 (para calcular média histórica)
cursor.execute('''
    SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT 
    WHERE Concurso <= 3500
    ORDER BY Concurso DESC
''')
historico_completo = cursor.fetchall()
conn.close()

print("=" * 90)
print("CONCURSOS 3495-3501 (números ordenados por posição N1..N15)")
print("=" * 90)
for r in rows:
    nums = [r[i] for i in range(1, 16)]
    marcador = " ← ALVO (3501)" if r[0] == 3501 else ""
    print(f"  Concurso {r[0]}: {nums}{marcador}")

janela_rows = [r for r in rows if 3495 <= r[0] <= 3500]
resultado_3501 = next((r for r in rows if r[0] == 3501), None)
resultado_nums = [resultado_3501[i] for i in range(1, 16)] if resultado_3501 else []

print(f"\n{'=' * 90}")
print(f"JANELA = 6 concursos (3495-3500) → Prever para 3501")
print(f"{'=' * 90}")

# ═══════════════════════════════════════════════════════════════
# 1. O QUE A JANELA VÊ (frequência recente por posição)
# ═══════════════════════════════════════════════════════════════
freq_por_pos = defaultdict(lambda: defaultdict(int))
for r in janela_rows:
    for pos in range(1, 16):
        num = r[pos]
        freq_por_pos[pos][num] += 1

print(f"\n--- Números que apareceram em cada posição (janela 6) ---")
for pos in range(1, 16):
    nums_vistos = sorted(freq_por_pos[pos].keys())
    freqs = {n: freq_por_pos[pos][n] for n in nums_vistos}
    # Marcar se o resultado real do 3501 naquela posição está ou não
    num_real = resultado_nums[pos - 1] if resultado_nums else None
    viu = "✅" if num_real in freq_por_pos[pos] else "❌"
    print(f"  Pos N{pos:02d}: {freqs}  ({len(nums_vistos)} distintos) | Real 3501: {num_real} {viu}")

# ═══════════════════════════════════════════════════════════════
# 2. SIMULAR _calcular_debitos_posicionais(janela=6, limiar=0.3)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'=' * 90}")
print(f"SIMULAÇÃO: _calcular_debitos_posicionais(janela=6, limiar=0.3)")
print(f"{'=' * 90}")

# Historico = tudo exceto janela recente
janela = 6
limiar = 0.3

# resultados = historico_completo (DESC = mais recentes primeiro)
resultados = [{'numeros': [r[i] for i in range(1, 16)]} for r in historico_completo]

historico = resultados[janela:]  # Excluir janela recente
recentes = resultados[:janela]

contagem_hist = defaultdict(lambda: defaultdict(int))
for r in historico:
    for pos in range(15):
        num = r['numeros'][pos]
        contagem_hist[num][pos + 1] += 1

total_hist = len(historico)

contagem_rec = defaultdict(lambda: defaultdict(int))
for r in recentes:
    for pos in range(15):
        num = r['numeros'][pos]
        contagem_rec[num][pos + 1] += 1

# Identificar débitos
debitos = {}
for num in range(1, 26):
    for pos in range(1, 16):
        media = contagem_hist[num][pos] / total_hist * 100 if total_hist > 0 else 0
        recente = contagem_rec[num][pos] / janela * 100
        if media >= 5:
            if recente < media * limiar:
                deficit = media - recente
                debitos[(num, pos)] = {
                    'numero': num, 'posicao': pos,
                    'media_historica': round(media, 1),
                    'freq_recente': round(recente, 1),
                    'deficit': round(deficit, 1)
                }

# Montar posicoes_frias_rejeitar
posicoes_frias_rejeitar = {}
for (num, pos), dados in debitos.items():
    if pos not in posicoes_frias_rejeitar:
        posicoes_frias_rejeitar[pos] = set()
    posicoes_frias_rejeitar[pos].add(num)

print(f"\nHistórico usado: {total_hist} concursos (excluída janela de {janela})")
print(f"Total de (num, pos) em débito: {len(debitos)}")

print(f"\n--- Números FRIOS (rejeitados) por posição ---")
total_frios = 0
violacoes_resultado = 0
for pos in range(1, 16):
    frios = sorted(posicoes_frias_rejeitar.get(pos, set()))
    total_frios += len(frios)
    # Verificar se o número real do 3501 naquela posição seria rejeitado
    num_real = resultado_nums[pos - 1] if resultado_nums else None
    rejeitado = "🔴 REJEITADO" if num_real in posicoes_frias_rejeitar.get(pos, set()) else "🟢 OK"
    if num_real in posicoes_frias_rejeitar.get(pos, set()):
        violacoes_resultado += 1
    print(f"  Pos N{pos:02d}: {frios} ({len(frios)} frios) | Real 3501: N{num_real} → {rejeitado}")

print(f"\n{'=' * 90}")
print(f"DIAGNÓSTICO FINAL")
print(f"{'=' * 90}")
print(f"  Total de números frios em todas posições: {total_frios}")
print(f"  Média de frios por posição: {total_frios / 15:.1f}")
print(f"  Posições onde o resultado REAL seria rejeitado: {violacoes_resultado}/15")
print(f"  → Com tolerância 0: {'❌ REJEITADO (precisa 0 violações)' if violacoes_resultado > 0 else '✅ ACEITO'}")
print(f"  → Com tolerância 3: {'❌ REJEITADO' if violacoes_resultado > 3 else '✅ ACEITO'}")
print(f"  → Com tolerância 5: {'❌ REJEITADO' if violacoes_resultado > 5 else '✅ ACEITO'}")
print(f"  → Com tolerância 7: {'❌ REJEITADO' if violacoes_resultado > 7 else '✅ ACEITO'}")
print(f"  → Com tolerância 10: {'❌ REJEITADO' if violacoes_resultado > 10 else '✅ ACEITO'}")

# ═══════════════════════════════════════════════════════════════
# 3. TESTAR MÚLTIPLOS CONCURSOS para encontrar padrão
# ═══════════════════════════════════════════════════════════════
print(f"\n{'=' * 90}")
print(f"TESTE EM 20 CONCURSOS: Quantas violações o resultado real tem?")
print(f"{'=' * 90}")

cursor2 = pyodbc.connect(conn_str).cursor()
cursor2.execute('''
    SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT 
    WHERE Concurso <= 3520
    ORDER BY Concurso DESC
''')
all_data = cursor2.fetchall()
all_results = [{'concurso': r[0], 'numeros': [r[i] for i in range(1, 16)]} for r in all_data]

violacoes_por_concurso = []
for idx in range(20):
    # Concurso alvo = all_results[idx]
    # Dados anteriores = all_results[idx+1:]
    alvo = all_results[idx]
    dados_anteriores = all_results[idx + 1:]
    
    # Calcular debitos com janela=6
    hist = dados_anteriores[6:]
    rec = dados_anteriores[:6]
    total_h = len(hist)
    
    if total_h == 0:
        continue
    
    ch = defaultdict(lambda: defaultdict(int))
    for r in hist:
        for p in range(15):
            ch[r['numeros'][p]][p + 1] += 1
    
    cr = defaultdict(lambda: defaultdict(int))
    for r in rec:
        for p in range(15):
            cr[r['numeros'][p]][p + 1] += 1
    
    frias = {}
    for num in range(1, 26):
        for pos in range(1, 16):
            media = ch[num][pos] / total_h * 100
            recente = cr[num][pos] / 6 * 100
            if media >= 5 and recente < media * 0.3:
                if pos not in frias:
                    frias[pos] = set()
                frias[pos].add(num)
    
    # Contar violações do resultado real
    viol = 0
    for pos in range(1, 16):
        if alvo['numeros'][pos - 1] in frias.get(pos, set()):
            viol += 1
    
    total_f = sum(len(s) for s in frias.values())
    violacoes_por_concurso.append(viol)
    print(f"  Concurso {alvo['concurso']}: {viol}/15 violações (total frios: {total_f})")

if violacoes_por_concurso:
    media_v = sum(violacoes_por_concurso) / len(violacoes_por_concurso)
    min_v = min(violacoes_por_concurso)
    max_v = max(violacoes_por_concurso)
    print(f"\n  📊 Média de violações: {media_v:.1f}/15")
    print(f"  📊 Mínimo: {min_v} | Máximo: {max_v}")
    print(f"  📊 Tolerância sugerida: {int(media_v)} a {int(media_v) + 2}")
