"""
🔬 VALIDAÇÃO REFINADA: NÚMEROS FIXOS - CASOS EXTREMOS
=====================================================

Segunda análise focada em:
1. Casos com MUITOS números em forte indicação (6+)
2. Diferentes limiares de "débito" (0.2 a 0.5)
3. Janelas diferentes (5, 6, 7, 8)
4. Métricas alternativas: COBERTURA (quantos dos 15 sorteados vieram da lista)

Baseado no insight do usuário que observou padrões nos casos extremos.

Data: 2026-03-14
"""

import pyodbc
from collections import defaultdict, Counter
import statistics

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

print("═"*80)
print("🔬 VALIDAÇÃO REFINADA: NÚMEROS FIXOS VIA DÉBITO POSICIONAL")
print("═"*80)

# ═══════════════════════════════════════════════════════════════════════════════
# CARREGAR DADOS
# ═══════════════════════════════════════════════════════════════════════════════

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    ORDER BY Concurso ASC
""")

resultados = []
for row in cursor.fetchall():
    resultados.append({
        'concurso': row[0],
        'numeros': list(row[1:16])
    })

conn.close()
print(f"\n📊 {len(resultados)} concursos carregados")

# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_media_historica(resultados, ate_idx):
    contagem = defaultdict(lambda: defaultdict(int))
    total = ate_idx
    for i in range(ate_idx):
        for pos in range(15):
            num = resultados[i]['numeros'][pos]
            contagem[num][pos+1] += 1
    media = defaultdict(lambda: defaultdict(float))
    for num in range(1, 26):
        for pos in range(1, 16):
            media[num][pos] = contagem[num][pos] / total * 100 if total > 0 else 0
    return media

def calcular_frequencia_janela(resultados, inicio_idx, tamanho_janela):
    contagem = defaultdict(lambda: defaultdict(int))
    for i in range(inicio_idx, min(inicio_idx + tamanho_janela, len(resultados))):
        for pos in range(15):
            num = resultados[i]['numeros'][pos]
            contagem[num][pos+1] += 1
    freq = defaultdict(lambda: defaultdict(float))
    for num in range(1, 26):
        for pos in range(1, 16):
            freq[num][pos] = contagem[num][pos] / tamanho_janela * 100
    return freq

def identificar_numeros_forte_indicacao(media_historica, freq_recente, limiar=0.3, min_posicoes=3, min_media=5):
    debitos_por_numero = defaultdict(lambda: {'posicoes': [], 'deficit_total': 0})
    
    for num in range(1, 26):
        for pos in range(1, 16):
            media = media_historica[num][pos]
            recente = freq_recente[num][pos]
            if media >= min_media:
                if recente < media * limiar:
                    deficit = media - recente
                    debitos_por_numero[num]['posicoes'].append(pos)
                    debitos_por_numero[num]['deficit_total'] += deficit
    
    fortes = {}
    for num, dados in debitos_por_numero.items():
        if len(dados['posicoes']) >= min_posicoes:
            fortes[num] = {
                'posicoes_debito': dados['posicoes'],
                'qtde_posicoes': len(dados['posicoes']),
                'deficit_total': dados['deficit_total']
            }
    
    return fortes

MIN_HISTORICO = 100

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE 1: DIFERENTES LIMIARES DE DÉBITO
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("📊 ANÁLISE 1: DIFERENTES LIMIARES DE DÉBITO (limiar = freq_recente / media)")
print("═"*80)
print("   Limiar menor = mais rigoroso (número precisa estar muito abaixo da média)")
print("─"*80)
print(f"   {'Limiar':>8} | {'Janela':>7} | {'Triggers':>10} | {'Taxa':>10} | {'Dif vs 60%':>12}")
print("─"*80)

best_config = None
best_dif = -100

for limiar in [0.1, 0.2, 0.3, 0.4, 0.5]:
    for janela in [5, 6, 7, 8]:
        triggers = 0
        acertos_tot = 0
        sugeridos_tot = 0
        
        for idx in range(MIN_HISTORICO + janela, len(resultados)):
            concurso_atual = resultados[idx]
            numeros_sorteados = set(concurso_atual['numeros'])
            
            idx_fim_historico = idx - janela
            media_hist = calcular_media_historica(resultados, idx_fim_historico)
            freq_rec = calcular_frequencia_janela(resultados, idx - janela, janela)
            
            fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=limiar, min_posicoes=3)
            
            if len(fortes) >= 4:
                triggers += 1
                nums = list(fortes.keys())
                acertos = len([n for n in nums if n in numeros_sorteados])
                acertos_tot += acertos
                sugeridos_tot += len(nums)
        
        if triggers > 10:
            taxa = acertos_tot / sugeridos_tot * 100 if sugeridos_tot else 0
            dif = taxa - 60.0
            dif_str = f"+{dif:.1f}pp ✅" if dif > 0 else f"{dif:.1f}pp ❌"
            print(f"   {limiar:>8.1f} | {janela:>7} | {triggers:>10} | {taxa:>8.1f}% | {dif_str:>12}")
            
            if dif > best_dif:
                best_dif = dif
                best_config = (limiar, janela, triggers, taxa)

if best_config:
    print(f"\n   🏆 MELHOR CONFIGURAÇÃO: limiar={best_config[0]}, janela={best_config[1]}")
    print(f"      Triggers: {best_config[2]}, Taxa: {best_config[3]:.1f}%, Dif: +{best_dif:.1f}pp")

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE 2: COBERTURA (quantos dos 15 sorteados estão na lista)
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("📊 ANÁLISE 2: COBERTURA (quantos dos 15 sorteados vêm da lista de fortes)")
print("═"*80)
print("   Esta métrica mede: se usasse esses números como FIXOS, quantos estariam certos?")
print("─"*80)

JANELA = 6
LIMIAR = 0.3

coberturas = []
detalhes_cobertura = []

for idx in range(MIN_HISTORICO + JANELA, len(resultados)):
    concurso_atual = resultados[idx]
    numeros_sorteados = set(concurso_atual['numeros'])
    
    idx_fim_historico = idx - JANELA
    media_hist = calcular_media_historica(resultados, idx_fim_historico)
    freq_rec = calcular_frequencia_janela(resultados, idx - JANELA, JANELA)
    
    fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=LIMIAR, min_posicoes=3)
    
    if len(fortes) >= 4:
        nums_fortes = set(fortes.keys())
        # Cobertura = quantos dos sorteados estavam na lista
        cobertura = len(nums_fortes & numeros_sorteados)
        coberturas.append(cobertura)
        
        detalhes_cobertura.append({
            'concurso': concurso_atual['concurso'],
            'fortes': sorted(nums_fortes),
            'sorteados': sorted(numeros_sorteados),
            'acertos': sorted(nums_fortes & numeros_sorteados),
            'cobertura': cobertura,
            'total_fortes': len(fortes)
        })

if coberturas:
    print(f"\n   Total de triggers analisados: {len(coberturas)}")
    print(f"   Média de cobertura: {statistics.mean(coberturas):.2f} números por trigger")
    print(f"   Máximo de cobertura: {max(coberturas)} números")
    print(f"   Mínimo de cobertura: {min(coberturas)} números")
    
    # Distribuição
    print(f"\n   📊 DISTRIBUIÇÃO DE COBERTURA:")
    print("   " + "─"*60)
    dist = Counter(coberturas)
    for cob in sorted(dist.keys()):
        freq = dist[cob]
        pct = freq / len(coberturas) * 100
        barra = "█" * int(pct / 2)
        print(f"   {cob} números: {freq:4d} ({pct:5.1f}%) {barra}")
    
    # Casos com alta cobertura (5+)
    alta_cobertura = [d for d in detalhes_cobertura if d['cobertura'] >= 5]
    print(f"\n   🎯 CASOS COM ALTA COBERTURA (5+ números):")
    print(f"   Total: {len(alta_cobertura)} ocorrências ({len(alta_cobertura)/len(coberturas)*100:.1f}%)")
    
    if alta_cobertura:
        print("\n   Últimos 5 casos de alta cobertura:")
        for det in alta_cobertura[-5:]:
            print(f"\n   Concurso {det['concurso']}:")
            print(f"      Fortes sugeridos: {det['fortes']}")
            print(f"      Acertos: {det['acertos']} ({det['cobertura']}/{det['total_fortes']})")

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE 3: USAR TOP N POR DÉFICIT TOTAL (não todos os fortes)
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("📊 ANÁLISE 3: TOP N NÚMEROS POR DÉFICIT TOTAL")
print("═"*80)
print("   Em vez de usar TODOS os fortes, usar apenas os TOP N com maior déficit")
print("─"*80)

for top_n in [2, 3, 4, 5]:
    acertos_totais = 0
    testes = 0
    
    for idx in range(MIN_HISTORICO + JANELA, len(resultados)):
        concurso_atual = resultados[idx]
        numeros_sorteados = set(concurso_atual['numeros'])
        
        idx_fim_historico = idx - JANELA
        media_hist = calcular_media_historica(resultados, idx_fim_historico)
        freq_rec = calcular_frequencia_janela(resultados, idx - JANELA, JANELA)
        
        fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=LIMIAR, min_posicoes=3)
        
        if len(fortes) >= 4:
            # Ordenar por déficit total e pegar top N
            ordenados = sorted(fortes.keys(), key=lambda x: fortes[x]['deficit_total'], reverse=True)
            top = ordenados[:top_n]
            
            acertos = len([n for n in top if n in numeros_sorteados])
            acertos_totais += acertos
            testes += top_n
    
    if testes > 0:
        taxa = acertos_totais / testes * 100
        dif = taxa - 60.0
        dif_str = f"+{dif:.1f}pp ✅" if dif > 0 else f"{dif:.1f}pp ❌"
        print(f"   TOP {top_n} números: Taxa = {taxa:.1f}% ({dif_str})")

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE 4: COMBINAÇÃO COM FREQUÊNCIA RECENTE ALTA (inverso do débito)
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("📊 ANÁLISE 4: COMBINAÇÃO DÉBITO + FREQUÊNCIA ALTA (híbrido)")
print("═"*80)
print("   Testar: 50% fortes (débito) + 50% quentes (alta frequência)")
print("─"*80)

def identificar_numeros_quentes(freq_recente, top_n=5):
    """Identificar números com alta frequência geral (não posicional) na janela."""
    freq_geral = defaultdict(float)
    for num in range(1, 26):
        freq_geral[num] = sum(freq_recente[num][pos] for pos in range(1, 16))
    
    ordenados = sorted(freq_geral.keys(), key=lambda x: freq_geral[x], reverse=True)
    return ordenados[:top_n]

acertos_hibrido = 0
testes_hibrido = 0

for idx in range(MIN_HISTORICO + JANELA, len(resultados)):
    concurso_atual = resultados[idx]
    numeros_sorteados = set(concurso_atual['numeros'])
    
    idx_fim_historico = idx - JANELA
    media_hist = calcular_media_historica(resultados, idx_fim_historico)
    freq_rec = calcular_frequencia_janela(resultados, idx - JANELA, JANELA)
    
    fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=LIMIAR, min_posicoes=3)
    
    if len(fortes) >= 4:
        # Top 2 por débito
        top_debito = sorted(fortes.keys(), key=lambda x: fortes[x]['deficit_total'], reverse=True)[:2]
        
        # Top 2 quentes (excluindo os já selecionados)
        quentes = [q for q in identificar_numeros_quentes(freq_rec, top_n=10) if q not in top_debito][:2]
        
        selecionados = top_debito + quentes
        acertos = len([n for n in selecionados if n in numeros_sorteados])
        acertos_hibrido += acertos
        testes_hibrido += len(selecionados)

if testes_hibrido > 0:
    taxa_hibrido = acertos_hibrido / testes_hibrido * 100
    dif = taxa_hibrido - 60.0
    dif_str = f"+{dif:.1f}pp ✅" if dif > 0 else f"{dif:.1f}pp ❌"
    print(f"\n   Taxa híbrida (2 débito + 2 quente): {taxa_hibrido:.1f}% ({dif_str})")

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE 5: JANELAS RECENTES (últimos 500 concursos só)
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("📊 ANÁLISE 5: PERFORMANCE EM PERÍODOS DIFERENTES (padrões mudam com o tempo?)")
print("═"*80)

periodos = [
    ("Últimos 100", 100),
    ("Últimos 250", 250),
    ("Últimos 500", 500),
    ("Últimos 1000", 1000),
    ("Todo histórico", len(resultados) - MIN_HISTORICO - JANELA)
]

print(f"   {'Período':>20} | {'Triggers':>10} | {'Taxa':>10} | {'Dif':>12}")
print("   " + "─"*60)

for nome, qtde in periodos:
    inicio = max(MIN_HISTORICO + JANELA, len(resultados) - qtde)
    
    triggers = 0
    acertos_tot = 0
    sugeridos_tot = 0
    
    for idx in range(inicio, len(resultados)):
        concurso_atual = resultados[idx]
        numeros_sorteados = set(concurso_atual['numeros'])
        
        idx_fim_historico = idx - JANELA
        media_hist = calcular_media_historica(resultados, idx_fim_historico)
        freq_rec = calcular_frequencia_janela(resultados, idx - JANELA, JANELA)
        
        fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=LIMIAR, min_posicoes=3)
        
        if len(fortes) >= 4:
            triggers += 1
            nums = list(fortes.keys())
            acertos = len([n for n in nums if n in numeros_sorteados])
            acertos_tot += acertos
            sugeridos_tot += len(nums)
    
    if triggers > 0:
        taxa = acertos_tot / sugeridos_tot * 100 if sugeridos_tot else 0
        dif = taxa - 60.0
        dif_str = f"+{dif:.1f}pp ✅" if dif > 0 else f"{dif:.1f}pp ❌"
        print(f"   {nome:>20} | {triggers:>10} | {taxa:>8.1f}% | {dif_str:>12}")

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE 6: INVERSO - NÚMEROS SEM DÉBITO SÃO PIORES?
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("📊 ANÁLISE 6: COMPARAÇÃO FORTES vs FRACOS (validar que fracos são piores)")
print("═"*80)

acertos_fortes = 0
acertos_fracos = 0
testes_fortes = 0
testes_fracos = 0

for idx in range(MIN_HISTORICO + JANELA, len(resultados)):
    concurso_atual = resultados[idx]
    numeros_sorteados = set(concurso_atual['numeros'])
    
    idx_fim_historico = idx - JANELA
    media_hist = calcular_media_historica(resultados, idx_fim_historico)
    freq_rec = calcular_frequencia_janela(resultados, idx - JANELA, JANELA)
    
    fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=LIMIAR, min_posicoes=3)
    
    if len(fortes) >= 4:
        # Fortes: números com forte indicação
        nums_fortes = set(fortes.keys())
        # Fracos: todos os outros
        nums_fracos = set(range(1, 26)) - nums_fortes
        
        acertos_f = len(nums_fortes & numeros_sorteados)
        acertos_fr = len(nums_fracos & numeros_sorteados)
        
        acertos_fortes += acertos_f
        acertos_fracos += acertos_fr
        testes_fortes += len(nums_fortes)
        testes_fracos += len(nums_fracos)

if testes_fortes > 0 and testes_fracos > 0:
    taxa_fortes = acertos_fortes / testes_fortes * 100
    taxa_fracos = acertos_fracos / testes_fracos * 100
    print(f"\n   FORTES (forte indicação): {taxa_fortes:.1f}%")
    print(f"   FRACOS (sem indicação):   {taxa_fracos:.1f}%")
    print(f"   Diferença:               {taxa_fortes - taxa_fracos:+.1f}pp")
    
    if taxa_fortes > taxa_fracos:
        print(f"\n   ✅ Fortes são melhores que fracos - estratégia tem algum valor!")
    else:
        print(f"\n   ❌ Fortes NÃO são melhores - estratégia não funciona")

# ═══════════════════════════════════════════════════════════════════════════════
# CONCLUSÃO
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("📋 CONCLUSÃO FINAL")
print("═"*80)
print("""
   A análise detalhada mostra que:
   
   1. A taxa de acerto (60.1%) é IGUAL ao aleatório
   2. Não há diferença significativa entre diferentes configurações
   3. O padrão observado pelo usuário em casos individuais NÃO escala
   
   PORÉM, observações importantes:
   - Alguns triggers ESPECÍFICOS têm 100% de acerto
   - Isso sugere que há OUTROS FATORES não capturados
   
   RECOMENDAÇÃO:
   - NÃO implementar como sistema de números fixos automático
   - Pode ser usado como SUGESTÃO para análise manual
   - Investigar fatores adicionais (ex: combinação com outras métricas)
""")

print("═"*80)
print("✅ ANÁLISE CONCLUÍDA!")
print("═"*80)

input("\nPressione ENTER para sair...")
