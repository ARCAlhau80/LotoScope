"""
🔬 VALIDAÇÃO: NÚMEROS FIXOS VIA DÉBITO POSICIONAL
=================================================

Hipótese do usuário:
- Janela de análise: 6 concursos anteriores
- Condição de "forte indicação": Números com 3+ posições em débito
- Trigger: Quando há 4+ números com forte indicação
- Validação: Verificar se esses números são sorteados no concurso seguinte

Objetivo: Validar se esse padrão pode ser usado para sugerir NÚMEROS FIXOS
(similar à estratégia de exclusão TOP 10)

Autor: Análise gerada por IA para LotoScope
Data: 2026-03-14
"""

import pyodbc
from collections import defaultdict, Counter
from datetime import datetime
import statistics

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

print("═"*80)
print("🔬 VALIDAÇÃO: NÚMEROS FIXOS VIA DÉBITO POSICIONAL")
print("═"*80)
print("   Hipótese: Números com 3+ posições em débito numa janela de 6 concursos")
print("             tendem a sair no concurso seguinte")
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
print(f"\n📊 {len(resultados)} concursos carregados (Concurso {resultados[0]['concurso']} a {resultados[-1]['concurso']})")

# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_media_historica(resultados, ate_idx):
    """Calcula frequência média de cada número em cada posição até um ponto."""
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
    """Calcula frequência de cada número em cada posição numa janela."""
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

def identificar_numeros_forte_indicacao(media_historica, freq_recente, limiar=0.3, min_posicoes=3):
    """
    Identifica números com "forte indicação" (múltiplas posições em débito).
    
    Args:
        media_historica: Frequência média histórica por número/posição
        freq_recente: Frequência recente por número/posição
        limiar: Fator de corte (freq_recente < media * limiar = débito)
        min_posicoes: Mínimo de posições em débito para "forte indicação"
    
    Returns:
        dict: {numero: {'posicoes_debito': [pos1, pos2, ...], 'deficit_total': X}}
    """
    debitos_por_numero = defaultdict(lambda: {'posicoes': [], 'deficit_total': 0})
    
    for num in range(1, 26):
        for pos in range(1, 16):
            media = media_historica[num][pos]
            recente = freq_recente[num][pos]
            
            # Só considerar posições com presença histórica significativa (>=5%)
            if media >= 5:
                if recente < media * limiar:  # Está em débito
                    deficit = media - recente
                    debitos_por_numero[num]['posicoes'].append(pos)
                    debitos_por_numero[num]['deficit_total'] += deficit
    
    # Filtrar apenas números com forte indicação (3+ posições em débito)
    fortes = {}
    for num, dados in debitos_por_numero.items():
        if len(dados['posicoes']) >= min_posicoes:
            fortes[num] = {
                'posicoes_debito': dados['posicoes'],
                'qtde_posicoes': len(dados['posicoes']),
                'deficit_total': dados['deficit_total']
            }
    
    return fortes

# ═══════════════════════════════════════════════════════════════════════════════
# PARÂMETROS DE ANÁLISE
# ═══════════════════════════════════════════════════════════════════════════════

JANELA_ANALISE = 6       # Janela de 6 concursos (conforme insight do usuário)
MIN_HISTORICO = 100      # Começar após 100 concursos (base estatística)
MIN_POSICOES_DEBITO = 3  # Mínimo de posições em débito para "forte indicação"
MIN_NUMEROS_TRIGGER = 4  # Mínimo de números com forte indicação para gerar trigger

print(f"\n📋 PARÂMETROS:")
print(f"   • Janela de análise: {JANELA_ANALISE} concursos")
print(f"   • Mínimo histórico: {MIN_HISTORICO} concursos")
print(f"   • Forte indicação: {MIN_POSICOES_DEBITO}+ posições em débito")
print(f"   • Trigger: {MIN_NUMEROS_TRIGGER}+ números com forte indicação")

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDAÇÃO NO HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("🔍 VALIDANDO NO HISTÓRICO COMPLETO")
print("═"*80)

# Estatísticas gerais
triggers_detectados = 0
total_numeros_sugeridos = 0
total_acertos = 0
acertos_por_concurso = []
taxa_acerto_por_trigger = []

# Detalhes por trigger
detalhes_triggers = []

# Para cada ponto no tempo onde podemos fazer análise
for idx in range(MIN_HISTORICO + JANELA_ANALISE, len(resultados)):
    # Índice do concurso a ser previsto
    concurso_atual = resultados[idx]
    concurso_num = concurso_atual['concurso']
    numeros_sorteados = set(concurso_atual['numeros'])
    
    # Calcular média histórica até antes da janela
    idx_fim_historico = idx - JANELA_ANALISE
    media_hist = calcular_media_historica(resultados, idx_fim_historico)
    
    # Calcular frequência na janela recente (6 concursos antes do atual)
    freq_rec = calcular_frequencia_janela(resultados, idx - JANELA_ANALISE, JANELA_ANALISE)
    
    # Identificar números com forte indicação
    fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=0.3, min_posicoes=MIN_POSICOES_DEBITO)
    
    # Verificar se atingiu o trigger (4+ números com forte indicação)
    if len(fortes) >= MIN_NUMEROS_TRIGGER:
        triggers_detectados += 1
        
        # Ordenar por quantidade de posições em débito (decrescente)
        nums_ordenados = sorted(fortes.keys(), key=lambda x: (fortes[x]['qtde_posicoes'], fortes[x]['deficit_total']), reverse=True)
        
        # Verificar quantos acertaram
        acertos = [n for n in nums_ordenados if n in numeros_sorteados]
        erros = [n for n in nums_ordenados if n not in numeros_sorteados]
        
        total_numeros_sugeridos += len(nums_ordenados)
        total_acertos += len(acertos)
        
        taxa = len(acertos) / len(nums_ordenados) * 100 if nums_ordenados else 0
        taxa_acerto_por_trigger.append(taxa)
        acertos_por_concurso.append(len(acertos))
        
        detalhes_triggers.append({
            'concurso': concurso_num,
            'sugeridos': nums_ordenados,
            'acertos': acertos,
            'erros': erros,
            'taxa': taxa,
            'detalhes_fortes': {n: fortes[n] for n in nums_ordenados}
        })

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n📊 RESULTADOS DA VALIDAÇÃO:")
print("─"*80)

if triggers_detectados == 0:
    print("   ⚠️ Nenhum trigger detectado com os parâmetros atuais!")
    print("   💡 Tente reduzir MIN_NUMEROS_TRIGGER ou MIN_POSICOES_DEBITO")
else:
    print(f"   ✅ Triggers detectados: {triggers_detectados}")
    print(f"   📊 Total de números sugeridos: {total_numeros_sugeridos}")
    print(f"   🎯 Total de acertos: {total_acertos}")
    
    taxa_geral = total_acertos / total_numeros_sugeridos * 100 if total_numeros_sugeridos else 0
    media_acertos = statistics.mean(acertos_por_concurso) if acertos_por_concurso else 0
    media_taxa = statistics.mean(taxa_acerto_por_trigger) if taxa_acerto_por_trigger else 0
    
    print(f"\n   📈 TAXA DE ACERTO GERAL: {taxa_geral:.1f}%")
    print(f"   📈 Média de acertos por trigger: {media_acertos:.2f} números")
    print(f"   📈 Média de taxa por trigger: {media_taxa:.1f}%")
    
    # Comparação com o aleatório
    # Probabilidade aleatória: 15/25 = 60%
    print(f"\n   🎲 COMPARAÇÃO COM ALEATÓRIO:")
    print(f"   • Probabilidade aleatória (15/25): 60.0%")
    print(f"   • Nossa taxa de acerto: {taxa_geral:.1f}%")
    diferenca = taxa_geral - 60.0
    if diferenca > 0:
        print(f"   • Vantagem: +{diferenca:.1f}pp ✅")
    else:
        print(f"   • Desvantagem: {diferenca:.1f}pp ❌")
    
    # Distribuição de acertos
    print(f"\n   📊 DISTRIBUIÇÃO DE ACERTOS POR TRIGGER:")
    print("   " + "─"*60)
    contagem_acertos = Counter(acertos_por_concurso)
    for qtde in sorted(contagem_acertos.keys()):
        freq = contagem_acertos[qtde]
        pct = freq / triggers_detectados * 100
        barra = "█" * int(pct / 2)
        print(f"   {qtde} acertos: {freq:4d} ocorrências ({pct:5.1f}%) {barra}")
    
    # Mostrar últimos 10 triggers
    print(f"\n   🔍 ÚLTIMOS 10 TRIGGERS (mais recentes):")
    print("   " + "─"*80)
    print(f"   {'Concurso':>10} | {'Sugeridos':>30} | {'Acertos':>20} | {'Taxa':>8}")
    print("   " + "─"*80)
    
    for det in detalhes_triggers[-10:]:
        sug_str = ','.join(f"{n:02d}" for n in det['sugeridos'][:6])
        if len(det['sugeridos']) > 6:
            sug_str += f"... (+{len(det['sugeridos'])-6})"
        acertos_str = ','.join(f"{n:02d}" for n in det['acertos'])
        print(f"   {det['concurso']:10d} | {sug_str:>30} | {acertos_str:>20} | {det['taxa']:6.1f}%")
    
    # Análise por quantidade de números sugeridos
    print(f"\n   📊 ANÁLISE POR QUANTIDADE DE NÚMEROS COM FORTE INDICAÇÃO:")
    print("   " + "─"*80)
    
    por_quantidade = defaultdict(lambda: {'triggers': 0, 'acertos_total': 0, 'sugeridos_total': 0})
    for det in detalhes_triggers:
        qtde = len(det['sugeridos'])
        por_quantidade[qtde]['triggers'] += 1
        por_quantidade[qtde]['acertos_total'] += len(det['acertos'])
        por_quantidade[qtde]['sugeridos_total'] += len(det['sugeridos'])
    
    print(f"   {'Qtde Fortes':>12} | {'Triggers':>10} | {'Taxa Média':>12} | {'Média Acertos':>14}")
    print("   " + "─"*80)
    for qtde in sorted(por_quantidade.keys()):
        dados = por_quantidade[qtde]
        taxa = dados['acertos_total'] / dados['sugeridos_total'] * 100 if dados['sugeridos_total'] else 0
        media = dados['acertos_total'] / dados['triggers'] if dados['triggers'] else 0
        print(f"   {qtde:12d} | {dados['triggers']:10d} | {taxa:10.1f}% | {media:14.2f}")
    
    # Recomendação
    print(f"\n   {'═'*80}")
    print("   📋 CONCLUSÃO E RECOMENDAÇÃO:")
    print("   " + "─"*80)
    
    if taxa_geral >= 70:
        print(f"   ✅✅ EXCELENTE! Taxa de {taxa_geral:.1f}% é muito acima do aleatório!")
        print(f"   💡 RECOMENDAÇÃO: Implementar como sistema de NÚMEROS FIXOS!")
    elif taxa_geral >= 65:
        print(f"   ✅ BOM! Taxa de {taxa_geral:.1f}% é acima do aleatório.")
        print(f"   💡 RECOMENDAÇÃO: Usar como sugestão, mas validar com outros filtros.")
    elif taxa_geral >= 60:
        print(f"   ⚠️ NEUTRO. Taxa de {taxa_geral:.1f}% é similar ao aleatório.")
        print(f"   💡 RECOMENDAÇÃO: Testar com parâmetros diferentes.")
    else:
        print(f"   ❌ FRACO. Taxa de {taxa_geral:.1f}% é abaixo do aleatório.")
        print(f"   💡 RECOMENDAÇÃO: Não usar esta estratégia.")

# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE DETALHADA DOS MELHORES CASOS
# ═══════════════════════════════════════════════════════════════════════════════

if triggers_detectados > 0 and len(detalhes_triggers) >= 5:
    print(f"\n{'═'*80}")
    print("🏆 TOP 10 MELHORES TRIGGERS (maior taxa de acerto):")
    print("═"*80)
    
    melhores = sorted(detalhes_triggers, key=lambda x: (x['taxa'], len(x['acertos'])), reverse=True)[:10]
    
    for i, det in enumerate(melhores, 1):
        print(f"\n   {i}. Concurso {det['concurso']} - Taxa: {det['taxa']:.0f}%")
        print(f"      Sugeridos: {det['sugeridos']}")
        print(f"      Acertos:   {det['acertos']} ({len(det['acertos'])}/{len(det['sugeridos'])})")
        
        # Mostrar detalhes das posições em débito
        print(f"      Detalhes:")
        for num in det['sugeridos'][:3]:  # Top 3
            info = det['detalhes_fortes'][num]
            pos_str = ', '.join(f"N{p}" for p in info['posicoes_debito'])
            status = "✅" if num in det['acertos'] else "❌"
            print(f"         {status} Nº {num:02d}: {info['qtde_posicoes']} posições ({pos_str})")

# ═══════════════════════════════════════════════════════════════════════════════
# TESTE COM DIFERENTES PARÂMETROS
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'═'*80}")
print("🧪 TESTE COM DIFERENTES PARÂMETROS")
print("═"*80)

print(f"\n   Testando combinações de MIN_POSICOES x MIN_TRIGGER:")
print("   " + "─"*80)
print(f"   {'Min Pos':>8} | {'Min Trigger':>12} | {'Triggers':>10} | {'Taxa Acerto':>12} | {'Diferença':>12}")
print("   " + "─"*80)

for min_pos in [2, 3, 4, 5]:
    for min_trigger in [3, 4, 5, 6]:
        triggers = 0
        acertos_tot = 0
        sugeridos_tot = 0
        
        for idx in range(MIN_HISTORICO + JANELA_ANALISE, len(resultados)):
            concurso_atual = resultados[idx]
            numeros_sorteados = set(concurso_atual['numeros'])
            
            idx_fim_historico = idx - JANELA_ANALISE
            media_hist = calcular_media_historica(resultados, idx_fim_historico)
            freq_rec = calcular_frequencia_janela(resultados, idx - JANELA_ANALISE, JANELA_ANALISE)
            
            fortes = identificar_numeros_forte_indicacao(media_hist, freq_rec, limiar=0.3, min_posicoes=min_pos)
            
            if len(fortes) >= min_trigger:
                triggers += 1
                nums = list(fortes.keys())
                acertos = len([n for n in nums if n in numeros_sorteados])
                acertos_tot += acertos
                sugeridos_tot += len(nums)
        
        if triggers > 0:
            taxa = acertos_tot / sugeridos_tot * 100 if sugeridos_tot else 0
            dif = taxa - 60.0
            dif_str = f"+{dif:.1f}pp ✅" if dif > 0 else f"{dif:.1f}pp ❌"
            print(f"   {min_pos:8d} | {min_trigger:12d} | {triggers:10d} | {taxa:10.1f}% | {dif_str:>12}")
        else:
            print(f"   {min_pos:8d} | {min_trigger:12d} | {'N/A':>10} | {'N/A':>12} | {'N/A':>12}")

print(f"\n{'═'*80}")
print("✅ ANÁLISE CONCLUÍDA!")
print("═"*80)

input("\nPressione ENTER para sair...")
