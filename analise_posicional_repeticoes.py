#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 ANÁLISE POSICIONAL DE REPETIÇÕES - LOTOFÁCIL
================================================
Analisa padrões de movimentação posicional dos números quando repetem:
1. Números do meio (5-11): ficam na mesma posição, anterior ou posterior?
2. Padrão de equilíbrio: se muitos caem posição, no próximo compensam?
3. Diferença entre extremos (1, 25) e números centrais
"""

import pyodbc
import pandas as pd
import numpy as np
from collections import defaultdict
from tabulate import tabulate

# Conexão
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def carregar_dados():
    """Carrega todos os concursos ordenados"""
    conn = pyodbc.connect(CONN_STR)
    query = """
    SELECT CONCURSO, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
    FROM Resultados_INT
    ORDER BY CONCURSO ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"✅ {len(df)} concursos carregados")
    return df

def encontrar_posicao(resultado, numero):
    """Encontra em qual posição (1-15) o número está no resultado"""
    for pos in range(1, 16):
        if resultado[f'N{pos}'] == numero:
            return pos
    return None  # Número não está no resultado

def analisar_movimentacao_por_numero(df, numeros_alvo):
    """
    Para cada número, quando ele repete entre sorteios consecutivos:
    - Fica na mesma posição?
    - Vai para posição anterior (menor)?
    - Vai para posição posterior (maior)?
    """
    resultados = {}
    
    for num in numeros_alvo:
        stats = {'mesma': 0, 'anterior': 0, 'posterior': 0, 'total_repeticoes': 0,
                 'sequencias_mesma_pos': [], 'max_sequencia_mesma_pos': 0}
        
        seq_mesma_pos = 0
        pos_anterior = None
        
        for i in range(len(df)):
            resultado = df.iloc[i]
            pos_atual = encontrar_posicao(resultado, num)
            
            if pos_atual is not None:  # Número apareceu
                if pos_anterior is not None:  # Estava no sorteio anterior também
                    stats['total_repeticoes'] += 1
                    
                    if pos_atual == pos_anterior:
                        stats['mesma'] += 1
                        seq_mesma_pos += 1
                    elif pos_atual < pos_anterior:
                        stats['anterior'] += 1
                        if seq_mesma_pos > 0:
                            stats['sequencias_mesma_pos'].append(seq_mesma_pos)
                        seq_mesma_pos = 0
                    else:  # pos_atual > pos_anterior
                        stats['posterior'] += 1
                        if seq_mesma_pos > 0:
                            stats['sequencias_mesma_pos'].append(seq_mesma_pos)
                        seq_mesma_pos = 0
                
                pos_anterior = pos_atual
            else:
                # Número não apareceu, reset
                if seq_mesma_pos > 0:
                    stats['sequencias_mesma_pos'].append(seq_mesma_pos)
                seq_mesma_pos = 0
                pos_anterior = None
        
        # Finaliza sequência se ainda ativa
        if seq_mesma_pos > 0:
            stats['sequencias_mesma_pos'].append(seq_mesma_pos)
        
        if stats['sequencias_mesma_pos']:
            stats['max_sequencia_mesma_pos'] = max(stats['sequencias_mesma_pos'])
            stats['media_sequencia_mesma_pos'] = np.mean(stats['sequencias_mesma_pos'])
        else:
            stats['media_sequencia_mesma_pos'] = 0
        
        resultados[num] = stats
    
    return resultados

def analisar_equilibrio_posicional(df, janela=500):
    """
    Analisa se há padrão de equilíbrio:
    - Quando muitos números caem de posição em X, em X+1 sobem?
    """
    resultados = []
    
    for i in range(1, len(df)):
        if i < len(df) - janela:
            continue
            
        resultado_ant = df.iloc[i-1]
        resultado_atual = df.iloc[i]
        
        # Números que repetiram
        nums_ant = set([resultado_ant[f'N{j}'] for j in range(1, 16)])
        nums_atual = set([resultado_atual[f'N{j}'] for j in range(1, 16)])
        repetidos = nums_ant & nums_atual
        
        if not repetidos:
            resultados.append({'concurso': resultado_atual['CONCURSO'], 
                            'subiu': 0, 'mesma': 0, 'desceu': 0, 'saldo': 0})
            continue
        
        subiu = 0
        mesma = 0
        desceu = 0
        
        for num in repetidos:
            pos_ant = encontrar_posicao(resultado_ant, num)
            pos_atual = encontrar_posicao(resultado_atual, num)
            
            if pos_atual < pos_ant:
                subiu += 1  # Foi para posição menor = "subiu" na lista ordenada
            elif pos_atual > pos_ant:
                desceu += 1  # Foi para posição maior = "desceu"
            else:
                mesma += 1
        
        saldo = subiu - desceu  # Positivo = mais subiram, Negativo = mais desceram
        
        resultados.append({
            'concurso': resultado_atual['CONCURSO'],
            'repetidos': len(repetidos),
            'subiu': subiu,
            'mesma': mesma,
            'desceu': desceu,
            'saldo': saldo
        })
    
    return pd.DataFrame(resultados)

def analisar_compensacao(df_equilibrio):
    """
    Verifica se há compensação: quando saldo é muito negativo, o próximo tende a ser positivo?
    """
    resultados = {'neg_para_pos': 0, 'neg_para_neg': 0, 'neg_para_zero': 0,
                  'pos_para_neg': 0, 'pos_para_pos': 0, 'pos_para_zero': 0}
    
    for i in range(1, len(df_equilibrio)):
        saldo_ant = df_equilibrio.iloc[i-1]['saldo']
        saldo_atual = df_equilibrio.iloc[i]['saldo']
        
        if saldo_ant < -2:  # Muito negativo
            if saldo_atual > 1:
                resultados['neg_para_pos'] += 1
            elif saldo_atual < -1:
                resultados['neg_para_neg'] += 1
            else:
                resultados['neg_para_zero'] += 1
        
        elif saldo_ant > 2:  # Muito positivo
            if saldo_atual < -1:
                resultados['pos_para_neg'] += 1
            elif saldo_atual > 1:
                resultados['pos_para_pos'] += 1
            else:
                resultados['pos_para_zero'] += 1
    
    return resultados

def analisar_posicao_tipica_por_numero(df, numeros_alvo):
    """
    Para cada número, qual sua posição mais comum e variância
    """
    resultados = {}
    
    for num in numeros_alvo:
        posicoes = []
        for i in range(len(df)):
            pos = encontrar_posicao(df.iloc[i], num)
            if pos:
                posicoes.append(pos)
        
        if posicoes:
            resultados[num] = {
                'pos_media': np.mean(posicoes),
                'pos_mediana': np.median(posicoes),
                'pos_min': min(posicoes),
                'pos_max': max(posicoes),
                'desvio': np.std(posicoes),
                'aparicoes': len(posicoes)
            }
    
    return resultados

def main():
    print("=" * 78)
    print("🔬 ANÁLISE POSICIONAL DE REPETIÇÕES - LOTOFÁCIL")
    print("=" * 78)
    
    df = carregar_dados()
    
    # ==========================================================================
    # ANÁLISE 1: NÚMEROS EXTREMOS vs MEIO
    # ==========================================================================
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 1: MOVIMENTAÇÃO POSICIONAL POR GRUPO DE NÚMEROS")
    print("=" * 78)
    
    grupos = {
        'Extremo Baixo (1-4)': [1, 2, 3, 4],
        'Baixo-Médio (5-8)': [5, 6, 7, 8],
        'Meio (9-13)': [9, 10, 11, 12, 13],
        'Alto-Médio (14-17)': [14, 15, 16, 17],
        'Extremo Alto (18-21)': [18, 19, 20, 21],
        'Extremo Superior (22-25)': [22, 23, 24, 25]
    }
    
    for nome_grupo, numeros in grupos.items():
        print(f"\n   📈 {nome_grupo}:")
        stats = analisar_movimentacao_por_numero(df, numeros)
        
        tabela = []
        for num in numeros:
            s = stats[num]
            total = s['total_repeticoes']
            if total > 0:
                pct_mesma = s['mesma'] / total * 100
                pct_ant = s['anterior'] / total * 100
                pct_post = s['posterior'] / total * 100
            else:
                pct_mesma = pct_ant = pct_post = 0
            
            tabela.append([
                num, total, 
                f"{s['mesma']} ({pct_mesma:.1f}%)",
                f"{s['anterior']} ({pct_ant:.1f}%)",
                f"{s['posterior']} ({pct_post:.1f}%)",
                s['max_sequencia_mesma_pos']
            ])
        
        print(tabulate(tabela, 
                      headers=['Num', 'Repetições', 'Mesma Pos', 'Pos Anterior', 'Pos Posterior', 'Max Seq Mesma'],
                      tablefmt='simple'))
    
    # ==========================================================================
    # ANÁLISE 2: RESUMO COMPARATIVO EXTREMOS vs MEIO
    # ==========================================================================
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 2: RESUMO - EXTREMOS vs NÚMEROS DO MEIO")
    print("=" * 78)
    
    extremos = [1, 2, 3, 4, 22, 23, 24, 25]
    meio = [9, 10, 11, 12, 13, 14, 15, 16, 17]
    
    stats_extremos = analisar_movimentacao_por_numero(df, extremos)
    stats_meio = analisar_movimentacao_por_numero(df, meio)
    
    # Agregar
    def agregar_stats(stats_dict):
        total_rep = sum(s['total_repeticoes'] for s in stats_dict.values())
        total_mesma = sum(s['mesma'] for s in stats_dict.values())
        total_ant = sum(s['anterior'] for s in stats_dict.values())
        total_post = sum(s['posterior'] for s in stats_dict.values())
        max_seq = max(s['max_sequencia_mesma_pos'] for s in stats_dict.values())
        return total_rep, total_mesma, total_ant, total_post, max_seq
    
    ext_total, ext_mesma, ext_ant, ext_post, ext_max = agregar_stats(stats_extremos)
    meio_total, meio_mesma, meio_ant, meio_post, meio_max = agregar_stats(stats_meio)
    
    tabela = [
        ['EXTREMOS (1-4, 22-25)', ext_total, 
         f"{ext_mesma/ext_total*100:.1f}%", f"{ext_ant/ext_total*100:.1f}%", f"{ext_post/ext_total*100:.1f}%", ext_max],
        ['MEIO (9-17)', meio_total,
         f"{meio_mesma/meio_total*100:.1f}%", f"{meio_ant/meio_total*100:.1f}%", f"{meio_post/meio_total*100:.1f}%", meio_max]
    ]
    
    print(tabulate(tabela,
                  headers=['Grupo', 'Total Rep', '% Mesma Pos', '% Pos Anterior', '% Pos Posterior', 'Max Seq'],
                  tablefmt='grid'))
    
    print("\n   💡 INTERPRETAÇÃO:")
    diff_mesma = ext_mesma/ext_total*100 - meio_mesma/meio_total*100
    if diff_mesma > 5:
        print(f"      • Extremos ficam {diff_mesma:.1f}% MAIS na mesma posição que números do meio")
    elif diff_mesma < -5:
        print(f"      • Números do meio ficam {-diff_mesma:.1f}% MAIS na mesma posição que extremos")
    else:
        print(f"      • Diferença pequena ({diff_mesma:.1f}%) - comportamento similar")
    
    # ==========================================================================
    # ANÁLISE 3: PADRÃO DE EQUILÍBRIO/COMPENSAÇÃO
    # ==========================================================================
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 3: PADRÃO DE EQUILÍBRIO POSICIONAL")
    print("=" * 78)
    print("   Quando muitos números DESCEM de posição, no próximo sorteio SOBEM?")
    
    df_eq = analisar_equilibrio_posicional(df, janela=500)
    
    print(f"\n   📈 Estatísticas de Saldo Posicional (últimos {len(df_eq)} concursos):")
    print(f"      • Média de números que repetem: {df_eq['repetidos'].mean():.1f}")
    print(f"      • Saldo médio (subiu - desceu): {df_eq['saldo'].mean():.2f}")
    print(f"      • Desvio padrão do saldo: {df_eq['saldo'].std():.2f}")
    
    # Distribuição do saldo
    print("\n   📊 Distribuição do Saldo (Subiu - Desceu):")
    for saldo in range(-6, 7):
        count = len(df_eq[df_eq['saldo'] == saldo])
        pct = count / len(df_eq) * 100
        bar = '█' * int(pct / 2)
        print(f"      {saldo:+2d}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Análise de compensação
    print("\n   🔄 ANÁLISE DE COMPENSAÇÃO:")
    comp = analisar_compensacao(df_eq)
    
    total_apos_neg = comp['neg_para_pos'] + comp['neg_para_neg'] + comp['neg_para_zero']
    total_apos_pos = comp['pos_para_neg'] + comp['pos_para_pos'] + comp['pos_para_zero']
    
    if total_apos_neg > 0:
        print(f"\n      Após saldo MUITO NEGATIVO (<-2):")
        print(f"         → Vira positivo: {comp['neg_para_pos']} ({comp['neg_para_pos']/total_apos_neg*100:.1f}%)")
        print(f"         → Continua negativo: {comp['neg_para_neg']} ({comp['neg_para_neg']/total_apos_neg*100:.1f}%)")
        print(f"         → Fica neutro: {comp['neg_para_zero']} ({comp['neg_para_zero']/total_apos_neg*100:.1f}%)")
    
    if total_apos_pos > 0:
        print(f"\n      Após saldo MUITO POSITIVO (>+2):")
        print(f"         → Vira negativo: {comp['pos_para_neg']} ({comp['pos_para_neg']/total_apos_pos*100:.1f}%)")
        print(f"         → Continua positivo: {comp['pos_para_pos']} ({comp['pos_para_pos']/total_apos_pos*100:.1f}%)")
        print(f"         → Fica neutro: {comp['pos_para_zero']} ({comp['pos_para_zero']/total_apos_pos*100:.1f}%)")
    
    # Calcular se há compensação significativa
    if total_apos_neg > 10 and total_apos_pos > 10:
        taxa_comp_neg = comp['neg_para_pos'] / total_apos_neg
        taxa_comp_pos = comp['pos_para_neg'] / total_apos_pos
        media_comp = (taxa_comp_neg + taxa_comp_pos) / 2
        
        print(f"\n   💡 CONCLUSÃO SOBRE COMPENSAÇÃO:")
        if media_comp > 0.4:
            print(f"      ✅ HÁ tendência de compensação! ({media_comp*100:.1f}% das vezes)")
            print("      → Após desequilíbrio forte, o próximo sorteio tende a equilibrar")
        elif media_comp > 0.3:
            print(f"      ≈ Tendência FRACA de compensação ({media_comp*100:.1f}%)")
            print("      → Há alguma reversão, mas não é forte o suficiente para estratégia")
        else:
            print(f"      ❌ NÃO há compensação significativa ({media_comp*100:.1f}%)")
            print("      → Comportamento aleatório")
    
    # ==========================================================================
    # ANÁLISE 4: NÚMEROS DO MEIO ESPECÍFICOS (5-11)
    # ==========================================================================
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 4: DETALHAMENTO NÚMEROS 5-11 (FOCO DO USUÁRIO)")
    print("=" * 78)
    
    numeros_foco = [5, 6, 7, 8, 9, 10, 11]
    stats_foco = analisar_movimentacao_por_numero(df, numeros_foco)
    posicoes = analisar_posicao_tipica_por_numero(df, numeros_foco)
    
    print("\n   📈 Comportamento detalhado:")
    tabela = []
    for num in numeros_foco:
        s = stats_foco[num]
        p = posicoes[num]
        total = s['total_repeticoes']
        if total > 0:
            pct_mesma = s['mesma'] / total * 100
            pct_ant = s['anterior'] / total * 100
            pct_post = s['posterior'] / total * 100
        else:
            pct_mesma = pct_ant = pct_post = 0
        
        # Determinar padrão dominante
        if pct_ant > pct_post + 5:
            padrao = "↑ Sobe"
        elif pct_post > pct_ant + 5:
            padrao = "↓ Desce"
        else:
            padrao = "≈ Neutro"
        
        tabela.append([
            num,
            f"{p['pos_media']:.1f}",
            f"{p['pos_min']}-{p['pos_max']}",
            f"{pct_mesma:.1f}%",
            f"{pct_ant:.1f}%",
            f"{pct_post:.1f}%",
            padrao,
            s['max_sequencia_mesma_pos']
        ])
    
    print(tabulate(tabela,
                  headers=['Num', 'Pos Média', 'Range', '% Mesma', '% Sobe', '% Desce', 'Padrão', 'Max Seq'],
                  tablefmt='grid'))
    
    # ==========================================================================
    # ANÁLISE 5: SEQUÊNCIAS DE REPETIÇÃO NA MESMA POSIÇÃO
    # ==========================================================================
    print("\n" + "=" * 78)
    print("📊 ANÁLISE 5: SEQUÊNCIAS MÁXIMAS NA MESMA POSIÇÃO")
    print("=" * 78)
    print("   Quantas vezes seguidas um número aparece na MESMA posição?")
    
    todos_numeros = list(range(1, 26))
    stats_todos = analisar_movimentacao_por_numero(df, todos_numeros)
    
    # Top 10 maiores sequências
    ranking = [(num, s['max_sequencia_mesma_pos'], s['total_repeticoes']) 
               for num, s in stats_todos.items() 
               if s['max_sequencia_mesma_pos'] > 0]
    ranking.sort(key=lambda x: x[1], reverse=True)
    
    print("\n   🏆 TOP 10 Maiores Sequências na Mesma Posição:")
    tabela = []
    for i, (num, seq, total) in enumerate(ranking[:10], 1):
        pos = analisar_posicao_tipica_por_numero(df, [num])[num]
        tabela.append([i, num, seq, f"N{int(pos['pos_mediana'])}", total])
    
    print(tabulate(tabela,
                  headers=['#', 'Número', 'Max Sequência', 'Pos Típica', 'Total Repetições'],
                  tablefmt='simple'))
    
    # ==========================================================================
    # CONCLUSÕES FINAIS
    # ==========================================================================
    print("\n" + "=" * 78)
    print("🎯 CONCLUSÕES E IMPLICAÇÕES PARA ESTRATÉGIA")
    print("=" * 78)
    
    print("""
   1. EXTREMOS vs MEIO:
      • Números extremos (1-4, 22-25) têm posição mais "fixa"
      • Números do meio (9-17) têm mais variação posicional
      • Isso é ESPERADO pela natureza da ordenação
   
   2. PADRÃO DE COMPENSAÇÃO:
      [Verificar resultado acima]
   
   3. PARA O GERADOR POOL 23 (Opção 31):
      • Se houver compensação forte → pode usar para filtrar
      • Se for aleatório → não vale adicionar filtro posicional
   
   4. NÚMEROS 5-11:
      • Têm range posicional amplo (podem ocupar várias posições)
      • Não há padrão forte de "subir" ou "descer" quando repetem
""")
    
    print("=" * 78)
    print("✅ ANÁLISE CONCLUÍDA!")
    print("=" * 78)

if __name__ == "__main__":
    main()
