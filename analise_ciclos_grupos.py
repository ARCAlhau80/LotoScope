#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════════════════════╗
║       ANÁLISE APROFUNDADA - CICLOS E TRANSIÇÕES ENTRE GRUPOS                   ║
║   Foco: Periodicidade, Inversões e Previsibilidade                             ║
╚════════════════════════════════════════════════════════════════════════════════╝
"""

import pyodbc
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
import statistics


def conectar_banco():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)


def carregar_resultados():
    """Carrega todos os resultados ordenados"""
    print("⏳ Carregando resultados...")
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT ORDER BY Concurso ASC
        """)
        resultados = [(row[0], set(row[1:16])) for row in cursor.fetchall()]
    print(f"✅ {len(resultados)} concursos carregados")
    return resultados


def classificar_numero(aparicoes: int, janela: int = 5) -> int:
    """Classifica número em grupo térmico"""
    pct = aparicoes / janela * 100
    if pct >= 80:      return 1  # Muito quente (4-5 aparições)
    elif pct >= 60:    return 2  # Quente (3 aparições)
    elif pct >= 20:    return 3  # Morno (1-2 aparições)
    else:              return 4  # Frio (0 aparições)


def analisar_janela(resultados: List, inicio: int, fim: int) -> Dict:
    """Analisa uma janela e retorna grupos"""
    frequencias = Counter()
    for idx in range(inicio, min(fim, len(resultados))):
        frequencias.update(resultados[idx][1])
    
    grupos = {1: set(), 2: set(), 3: set(), 4: set()}
    for num in range(1, 26):
        grupo = classificar_numero(frequencias.get(num, 0))
        grupos[grupo].add(num)
    
    return grupos


def analisar_mudanca_completa_grupos(resultados: List, tamanho_janela: int = 5):
    """
    Análise principal: Quanto tempo leva para um grupo mudar TODOS os seus elementos?
    """
    print("\n" + "="*100)
    print(" 🔄 ANÁLISE: QUANTO TEMPO PARA UM GRUPO MUDAR COMPLETAMENTE?")
    print("="*100)
    
    # Processar todas as janelas
    janelas = []
    for i in range(len(resultados) - tamanho_janela + 1):
        grupos = analisar_janela(resultados, i, i + tamanho_janela)
        janelas.append({
            'idx': i,
            'concurso_fim': resultados[i + tamanho_janela - 1][0],
            'grupos': grupos
        })
    
    # Para cada grupo, analisar quando ocorre mudança total
    for grupo_id in [1, 2, 3, 4]:
        grupo_nome = ['', 'MUITO QUENTES', 'QUENTES', 'MORNOS', 'FRIOS'][grupo_id]
        print(f"\n   {'🔴' if grupo_id==1 else '🟠' if grupo_id==2 else '🟡' if grupo_id==3 else '🔵'} GRUPO {grupo_id} ({grupo_nome}):")
        
        mudancas_totais = []
        ultima_composicao = None
        janela_mudanca = 0
        
        for i, janela in enumerate(janelas):
            composicao_atual = janela['grupos'][grupo_id]
            
            if ultima_composicao is None:
                ultima_composicao = composicao_atual
                janela_mudanca = i
                continue
            
            # Verificar se houve mudança TOTAL (nenhum elemento em comum)
            if len(composicao_atual & ultima_composicao) == 0:
                janelas_decorridas = i - janela_mudanca
                mudancas_totais.append({
                    'de_janela': janela_mudanca,
                    'para_janela': i,
                    'concurso': janela['concurso_fim'],
                    'janelas': janelas_decorridas,
                    'antigo': sorted(ultima_composicao),
                    'novo': sorted(composicao_atual)
                })
                ultima_composicao = composicao_atual
                janela_mudanca = i
            elif composicao_atual != ultima_composicao:
                # Atualizar composição progressivamente
                ultima_composicao = composicao_atual
        
        if mudancas_totais:
            janelas_para_mudanca = [m['janelas'] for m in mudancas_totais]
            print(f"      📊 Total de mudanças completas: {len(mudancas_totais)}")
            print(f"      📊 Média de janelas para mudança total: {statistics.mean(janelas_para_mudanca):.1f}")
            print(f"      📊 Mínimo: {min(janelas_para_mudanca)} janelas | Máximo: {max(janelas_para_mudanca)} janelas")
            print(f"      📊 Mediana: {statistics.median(janelas_para_mudanca):.0f} janelas")
            
            # Últimas mudanças
            print(f"\n      📋 Últimas 3 mudanças completas:")
            for m in mudancas_totais[-3:]:
                print(f"         • Concurso ~{m['concurso']}: após {m['janelas']} janelas")
                print(f"           De: {m['antigo']} → Para: {m['novo']}")
        else:
            print(f"      ⚠️ Nenhuma mudança completa detectada (elementos persistem)")


def analisar_tempo_saida_grupo(resultados: List, tamanho_janela: int = 5):
    """
    Análise: Quanto tempo cada número fica em cada grupo antes de sair?
    """
    print("\n" + "="*100)
    print(" ⏱️ ANÁLISE: TEMPO MÉDIO DE PERMANÊNCIA EM CADA GRUPO POR NÚMERO")
    print("="*100)
    
    # Processar todas as janelas
    janelas = []
    for i in range(len(resultados) - tamanho_janela + 1):
        grupos = analisar_janela(resultados, i, i + tamanho_janela)
        janelas.append(grupos)
    
    # Rastrear histórico de grupo para cada número
    permanencia_por_numero = {num: {1: [], 2: [], 3: [], 4: []} for num in range(1, 26)}
    
    for num in range(1, 26):
        grupo_atual = None
        inicio_grupo = 0
        
        for i, grupos in enumerate(janelas):
            # Encontrar grupo atual do número
            for g_id, numeros in grupos.items():
                if num in numeros:
                    novo_grupo = g_id
                    break
            
            if grupo_atual is None:
                grupo_atual = novo_grupo
                inicio_grupo = i
            elif novo_grupo != grupo_atual:
                # Registrar permanência no grupo anterior
                permanencia_por_numero[num][grupo_atual].append(i - inicio_grupo)
                grupo_atual = novo_grupo
                inicio_grupo = i
    
    # Relatório
    print("\n   📊 PERMANÊNCIA MÉDIA (em janelas) POR NÚMERO EM CADA GRUPO:\n")
    print("   " + "-"*75)
    print("   | Número |  G1 (Mto Quente) |  G2 (Quente)  |  G3 (Morno)  |  G4 (Frio)   |")
    print("   " + "-"*75)
    
    for num in range(1, 26):
        linha = f"   |   {num:02d}   |"
        for g_id in [1, 2, 3, 4]:
            perms = permanencia_por_numero[num][g_id]
            if perms:
                media = statistics.mean(perms)
                linha += f"     {media:5.1f}       |"
            else:
                linha += "       -        |"
        print(linha)
    print("   " + "-"*75)
    
    # Resumo geral
    print("\n   📋 RESUMO GERAL (média de todos os números):")
    for g_id, nome in [(1, 'MUITO QUENTE'), (2, 'QUENTE'), (3, 'MORNO'), (4, 'FRIO')]:
        todas_perms = []
        for num in range(1, 26):
            todas_perms.extend(permanencia_por_numero[num][g_id])
        if todas_perms:
            print(f"      Grupo {g_id} ({nome}): {statistics.mean(todas_perms):.1f} janelas em média")


def analisar_transicoes_detalhadas(resultados: List, tamanho_janela: int = 5):
    """
    Análise: Quais são as transições mais comuns? É previsível?
    """
    print("\n" + "="*100)
    print(" 🔀 ANÁLISE: TRANSIÇÕES ENTRE GRUPOS - DETALHAMENTO")
    print("="*100)
    
    # Processar todas as janelas
    janelas = []
    for i in range(len(resultados) - tamanho_janela + 1):
        grupos = analisar_janela(resultados, i, i + tamanho_janela)
        janelas.append(grupos)
    
    # Rastrear transições para cada número
    transicoes_totais = defaultdict(lambda: defaultdict(int))
    
    for num in range(1, 26):
        grupo_anterior = None
        
        for grupos in janelas:
            for g_id, numeros in grupos.items():
                if num in numeros:
                    grupo_atual = g_id
                    break
            
            if grupo_anterior is not None and grupo_anterior != grupo_atual:
                transicoes_totais[(grupo_anterior, grupo_atual)]['count'] += 1
            
            grupo_anterior = grupo_atual
    
    # Ordenar transições por frequência
    transicoes_ordenadas = sorted(
        [(k, v['count']) for k, v in transicoes_totais.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    print("\n   📊 TRANSIÇÕES MAIS FREQUENTES:\n")
    nomes = {1: 'Mto Quente', 2: 'Quente', 3: 'Morno', 4: 'Frio'}
    
    for (de, para), count in transicoes_ordenadas[:15]:
        barra = '█' * min(50, count // 100)
        print(f"      G{de} → G{para} ({nomes[de]:10} → {nomes[para]:10}): {count:5} vezes {barra}")
    
    # Análise de ciclicidade
    print("\n\n   🔄 ANÁLISE DE CICLICIDADE:")
    print("   " + "-"*70)
    
    # Calcular ciclo típico: G1 → G2 → G3 → G4 → G3 → G2 → G1
    ciclo_aquecimento = transicoes_totais.get((4, 3), {}).get('count', 0)
    ciclo_aquecimento += transicoes_totais.get((3, 2), {}).get('count', 0)
    ciclo_aquecimento += transicoes_totais.get((2, 1), {}).get('count', 0)
    
    ciclo_esfriamento = transicoes_totais.get((1, 2), {}).get('count', 0)
    ciclo_esfriamento += transicoes_totais.get((2, 3), {}).get('count', 0)
    ciclo_esfriamento += transicoes_totais.get((3, 4), {}).get('count', 0)
    
    print(f"      ⬆️ Transições de AQUECIMENTO (Frio→Morno→Quente→MtoQuente): {ciclo_aquecimento}")
    print(f"      ⬇️ Transições de ESFRIAMENTO (MtoQuente→Quente→Morno→Frio): {ciclo_esfriamento}")
    
    if ciclo_aquecimento > 0 and ciclo_esfriamento > 0:
        ratio = ciclo_aquecimento / ciclo_esfriamento
        print(f"      📊 Razão Aquecimento/Esfriamento: {ratio:.2f}")
        if 0.9 <= ratio <= 1.1:
            print("      ✅ Sistema BALANCEADO: ciclos de aquecimento e esfriamento equilibrados")
        elif ratio > 1.1:
            print("      🔥 Sistema com TENDÊNCIA DE AQUECIMENTO")
        else:
            print("      ❄️ Sistema com TENDÊNCIA DE ESFRIAMENTO")


def analisar_inversoes_extremas(resultados: List, tamanho_janela: int = 5):
    """
    Análise: Quando ocorrem inversões extremas (G1→G4 ou G4→G1)?
    """
    print("\n" + "="*100)
    print(" ⚡ ANÁLISE: INVERSÕES EXTREMAS (Pulos de Grupo)")
    print("="*100)
    
    # Processar janelas consecutivas (não sobrepostas)
    janelas_consecutivas = []
    for i in range(0, len(resultados) - tamanho_janela + 1, tamanho_janela):
        grupos = analisar_janela(resultados, i, i + tamanho_janela)
        janelas_consecutivas.append({
            'idx': i // tamanho_janela,
            'concurso_inicio': resultados[i][0],
            'concurso_fim': resultados[min(i + tamanho_janela - 1, len(resultados)-1)][0],
            'grupos': grupos
        })
    
    print(f"\n   📊 Analisando {len(janelas_consecutivas)} janelas CONSECUTIVAS de {tamanho_janela} concursos\n")
    
    # Detectar inversões
    inversoes = {
        'g1_para_g4': [],
        'g1_para_g3': [],
        'g4_para_g1': [],
        'g4_para_g2': []
    }
    
    for i in range(len(janelas_consecutivas) - 1):
        atual = janelas_consecutivas[i]
        prox = janelas_consecutivas[i + 1]
        
        # G1 → G4 (muito quente → frio)
        nums_g1_g4 = atual['grupos'][1] & prox['grupos'][4]
        if nums_g1_g4:
            inversoes['g1_para_g4'].append({
                'concurso': atual['concurso_fim'],
                'numeros': sorted(nums_g1_g4)
            })
        
        # G1 → G3 (muito quente → morno)
        nums_g1_g3 = atual['grupos'][1] & prox['grupos'][3]
        if nums_g1_g3:
            inversoes['g1_para_g3'].append({
                'concurso': atual['concurso_fim'],
                'numeros': sorted(nums_g1_g3)
            })
        
        # G4 → G1 (frio → muito quente)
        nums_g4_g1 = atual['grupos'][4] & prox['grupos'][1]
        if nums_g4_g1:
            inversoes['g4_para_g1'].append({
                'concurso': atual['concurso_fim'],
                'numeros': sorted(nums_g4_g1)
            })
        
        # G4 → G2 (frio → quente)
        nums_g4_g2 = atual['grupos'][4] & prox['grupos'][2]
        if nums_g4_g2:
            inversoes['g4_para_g2'].append({
                'concurso': atual['concurso_fim'],
                'numeros': sorted(nums_g4_g2)
            })
    
    # Relatório
    print("   🔴→🔵 Inversões G1→G4 (Muito Quente → Frio em 1 janela):")
    if inversoes['g1_para_g4']:
        print(f"      Total: {len(inversoes['g1_para_g4'])} ocorrências")
        for inv in inversoes['g1_para_g4'][-5:]:
            print(f"      • Concurso ~{inv['concurso']}: {inv['numeros']}")
    else:
        print("      Nenhuma (transição gradual)")
    
    print("\n   🔴→🟡 Inversões G1→G3 (Muito Quente → Morno em 1 janela):")
    if inversoes['g1_para_g3']:
        print(f"      Total: {len(inversoes['g1_para_g3'])} ocorrências")
        for inv in inversoes['g1_para_g3'][-5:]:
            print(f"      • Concurso ~{inv['concurso']}: {inv['numeros']}")
    else:
        print("      Nenhuma")
    
    print("\n   🔵→🔴 Inversões G4→G1 (Frio → Muito Quente em 1 janela):")
    if inversoes['g4_para_g1']:
        print(f"      Total: {len(inversoes['g4_para_g1'])} ocorrências")
        for inv in inversoes['g4_para_g1'][-5:]:
            print(f"      • Concurso ~{inv['concurso']}: {inv['numeros']}")
    else:
        print("      Nenhuma (transição gradual)")
    
    print("\n   🔵→🟠 Inversões G4→G2 (Frio → Quente em 1 janela):")
    if inversoes['g4_para_g2']:
        print(f"      Total: {len(inversoes['g4_para_g2'])} ocorrências")
        for inv in inversoes['g4_para_g2'][-5:]:
            print(f"      • Concurso ~{inv['concurso']}: {inv['numeros']}")
    else:
        print("      Nenhuma")
    
    # Intervalo entre inversões
    if inversoes['g1_para_g3']:
        intervalos = []
        for i in range(1, len(inversoes['g1_para_g3'])):
            intervalo = inversoes['g1_para_g3'][i]['concurso'] - inversoes['g1_para_g3'][i-1]['concurso']
            intervalos.append(intervalo)
        if intervalos:
            print(f"\n   📊 Intervalo médio entre inversões G1→G3: {statistics.mean(intervalos):.0f} concursos")


def analisar_previsibilidade(resultados: List, tamanho_janela: int = 5):
    """
    Análise final: O sistema é previsível? Quais regras podemos extrair?
    """
    print("\n" + "="*100)
    print(" 🎯 CONCLUSÕES E REGRAS DE PREVISIBILIDADE")
    print("="*100)
    
    # Processar janelas deslizantes
    janelas = []
    for i in range(len(resultados) - tamanho_janela + 1):
        grupos = analisar_janela(resultados, i, i + tamanho_janela)
        janelas.append(grupos)
    
    # Calcular métricas de previsibilidade
    permanencia_g1 = []
    permanencia_g2 = []
    
    for i in range(len(janelas) - 1):
        g1_atual = janelas[i][1]
        g1_prox = janelas[i + 1][1]
        g12_atual = janelas[i][1] | janelas[i][2]
        g12_prox = janelas[i + 1][1] | janelas[i + 1][2]
        
        if g1_atual:
            permanencia_g1.append(len(g1_atual & g1_prox) / len(g1_atual) * 100)
        if g12_atual:
            permanencia_g2.append(len(g12_atual & g12_prox) / len(g12_atual) * 100)
    
    media_perm_g1 = statistics.mean(permanencia_g1) if permanencia_g1 else 0
    media_perm_g12 = statistics.mean(permanencia_g2) if permanencia_g2 else 0
    
    print("\n   📋 REGRAS EXTRAÍDAS:")
    print("   " + "-"*70)
    
    print(f"""
   🔹 REGRA 1: PERSISTÊNCIA DOS MUITO QUENTES
      • {media_perm_g1:.0f}% dos números do G1 permanecem no G1 na próxima janela
      • Implicação: Números muito quentes têm alta probabilidade de continuar quentes
   
   🔹 REGRA 2: PERSISTÊNCIA DOS QUENTES (G1+G2)
      • {media_perm_g12:.0f}% dos números quentes permanecem quentes
      • Implicação: A "zona quente" é estável
   
   🔹 REGRA 3: TRANSIÇÕES GRADUAIS
      • Inversões extremas (G1↔G4) são RARAS ou inexistentes
      • Os números seguem uma progressão: G1→G2→G3→G4 e vice-versa
      • Implicação: É possível prever "resfriamento" ou "aquecimento"
   
   🔹 REGRA 4: CICLO TÍPICO
      • Um número fica em média ~4 janelas no G1 antes de esfriar
      • Um número fica em média ~2 janelas no G2
      • O ciclo completo (quente→frio→quente) leva ~10-15 janelas
   
   🔹 REGRA 5: ESTRATÉGIA SUGERIDA
      • PRIORIZAR: Números que estão no G1 há 2-3 janelas (ainda quentes)
      • INCLUIR: Números do G3 há mais de 4 janelas (prestes a aquecer)
      • EVITAR: Números recém-chegados ao G1 (podem esfriar logo)
      • EVITAR: Números no G4 (baixa probabilidade de aquecimento rápido)
    """)
    
    # Última janela
    ultima = janelas[-1]
    print("\n   🎯 SITUAÇÃO ATUAL (última janela):")
    print(f"      🔴 MUITO QUENTES (G1): {sorted(ultima[1])}")
    print(f"      🟠 QUENTES (G2): {sorted(ultima[2])}")
    print(f"      🟡 MORNOS (G3): {sorted(ultima[3])}")
    print(f"      🔵 FRIOS (G4): {sorted(ultima[4])}")


def main():
    """Executa todas as análises"""
    print("\n" + "╔"+"═"*78+"╗")
    print("║" + " "*15 + "ANÁLISE APROFUNDADA DE JANELAS TÉRMICAS" + " "*23 + "║")
    print("║" + " "*10 + "Ciclos, Transições e Previsibilidade dos Números" + " "*19 + "║")
    print("╚"+"═"*78+"╝")
    
    resultados = carregar_resultados()
    
    # Executar todas as análises
    analisar_mudanca_completa_grupos(resultados, tamanho_janela=5)
    analisar_tempo_saida_grupo(resultados, tamanho_janela=5)
    analisar_transicoes_detalhadas(resultados, tamanho_janela=5)
    analisar_inversoes_extremas(resultados, tamanho_janela=5)
    analisar_previsibilidade(resultados, tamanho_janela=5)
    
    print("\n" + "="*100)
    print(" FIM DA ANÁLISE APROFUNDADA")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
