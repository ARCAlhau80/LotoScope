# -*- coding: utf-8 -*-
"""
Análise de Padrões: Final do Concurso × Posição × Número
=========================================================
VERSÃO 2: Comparação por Janelas Temporais (100, 50, 30 concursos)

Verifica se padrões recentes são mais significativos que o histórico completo.

Autor: LotoScope AI Analysis
Data: 13/03/2026
"""

import pyodbc
import pandas as pd
import numpy as np
from collections import defaultdict
from tabulate import tabulate
from scipy import stats

# Conexão com banco de dados
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'

def carregar_dados():
    """Carrega todos os concursos do banco de dados."""
    query = """
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso
    """
    with pyodbc.connect(CONN_STR) as conn:
        df = pd.read_sql(query, conn)
    
    # Adicionar coluna com o final do concurso (0-9)
    df['Final'] = df['Concurso'] % 10
    
    print(f"✅ Carregados {len(df)} concursos")
    print(f"   Primeiro: {df['Concurso'].min()} | Último: {df['Concurso'].max()}")
    return df


def analisar_posicao_por_final(df, posicao):
    """
    Para uma posição específica (N1-N15), analisa frequência dos números
    agrupados pelo final do concurso.
    """
    coluna = f'N{posicao}'
    resultados = {}
    
    for final in range(10):
        df_final = df[df['Final'] == final]
        freq = df_final[coluna].value_counts().sort_index()
        total = len(df_final)
        
        if total > 0:
            freq_pct = (freq / total * 100).round(2)
            resultados[final] = {
                'total_concursos': total,
                'frequencias': freq_pct.to_dict()
            }
        else:
            resultados[final] = {
                'total_concursos': 0,
                'frequencias': {}
            }
    
    return resultados


def calcular_estatisticas_globais(df, posicao):
    """Calcula média global e desvio padrão para referência."""
    coluna = f'N{posicao}'
    freq_global = df[coluna].value_counts()
    total = len(df)
    freq_pct = (freq_global / total * 100)
    return freq_pct.to_dict()


def encontrar_anomalias(resultados, freq_global, limiar_pct=20):
    """
    Encontra números com frequência significativamente diferente da média global.
    """
    anomalias = []
    
    for final, dados in resultados.items():
        total_final = dados['total_concursos']
        if total_final == 0:
            continue
            
        for numero, freq_final in dados['frequencias'].items():
            freq_esperada = freq_global.get(numero, 0)
            
            # Calcular diferença percentual
            if freq_esperada > 0:
                diff_pct = ((freq_final - freq_esperada) / freq_esperada) * 100
            else:
                diff_pct = 0
            
            # Filtrar anomalias significativas
            if abs(diff_pct) >= limiar_pct:
                anomalias.append({
                    'final': final,
                    'numero': numero,
                    'freq_observada': freq_final,
                    'freq_esperada': round(freq_esperada, 2),
                    'diff_pct': round(diff_pct, 1),
                    'n_concursos': total_final
                })
    
    return sorted(anomalias, key=lambda x: abs(x['diff_pct']), reverse=True)


def analisar_janela(df, janela_nome, n_concursos=None):
    """
    Analisa uma janela específica de concursos.
    """
    if n_concursos:
        df_janela = df.tail(n_concursos).copy()
    else:
        df_janela = df.copy()
    
    print(f"\n{'='*80}")
    print(f"📊 JANELA: {janela_nome}")
    print(f"   Concursos: {df_janela['Concurso'].min()} a {df_janela['Concurso'].max()} ({len(df_janela)} concursos)")
    print(f"{'='*80}")
    
    # Contar concursos por final
    contagem_finais = df_janela['Final'].value_counts().sort_index()
    print("\n📊 Distribuição por final:")
    for final in range(10):
        count = contagem_finais.get(final, 0)
        print(f"   Final {final}: {count} concursos")
    
    # Análise para N1 e N15
    resultados_posicoes = {}
    
    for posicao in [1, 15]:
        coluna = f'N{posicao}'
        
        print(f"\n{'─'*60}")
        print(f"🎯 POSIÇÃO {coluna}")
        print(f"{'─'*60}")
        
        # Tabela de frequência por final
        tabela = []
        headers = ['Final', 'N', 'Top 1', '%', 'Top 2', '%', 'Top 3', '%']
        
        freq_global = calcular_estatisticas_globais(df_janela, posicao)
        resultados = analisar_posicao_por_final(df_janela, posicao)
        
        for final in range(10):
            dados = resultados[final]
            if dados['total_concursos'] == 0:
                continue
                
            # Ordenar por frequência
            freq_sorted = sorted(dados['frequencias'].items(), key=lambda x: -x[1])[:3]
            
            row = [
                final,
                dados['total_concursos']
            ]
            for num, pct in freq_sorted:
                row.extend([int(num), f"{pct:.1f}%"])
            
            # Preencher se houver menos de 3 números
            while len(row) < 8:
                row.extend(['-', '-'])
            
            tabela.append(row)
        
        print(tabulate(tabela, headers, tablefmt='grid'))
        
        # Análise de anomalias FORTES (≥50% diferença)
        anomalias = encontrar_anomalias(resultados, freq_global, limiar_pct=50)
        if anomalias:
            print(f"\n⚠️  Anomalias FORTES (≥50% diferença):")
            for a in anomalias[:5]:
                sinal = "↑" if a['diff_pct'] > 0 else "↓"
                print(f"   Final {a['final']}: Número {a['numero']:2d} = {a['freq_observada']:.1f}% "
                      f"(esperado: {a['freq_esperada']:.1f}%) {sinal}{abs(a['diff_pct']):.1f}%")
        else:
            print(f"\n✅ Sem anomalias fortes (≥50% diferença)")
        
        resultados_posicoes[posicao] = resultados
    
    # Teste Chi-quadrado para todas as posições
    print(f"\n{'─'*60}")
    print(f"📈 TESTE CHI-QUADRADO (p < 0.05 = correlação significativa)")
    print(f"{'─'*60}")
    
    chi_results = []
    for posicao in range(1, 16):
        coluna = f'N{posicao}'
        
        # Criar tabela de contingência
        contingencia = pd.crosstab(df_janela['Final'], df_janela[coluna])
        
        # Verificar se há dados suficientes
        if contingencia.shape[0] < 2 or contingencia.shape[1] < 2:
            chi_results.append({
                'posicao': coluna,
                'chi2': 0,
                'p_value': 1.0,
                'significativo': "❓ INSUF."
            })
            continue
        
        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingencia)
            significativo = "✅ SIM" if p_value < 0.05 else "❌ NÃO"
        except:
            chi2, p_value = 0, 1.0
            significativo = "❓ ERRO"
        
        chi_results.append({
            'posicao': coluna,
            'chi2': chi2,
            'p_value': p_value,
            'significativo': significativo
        })
    
    # Mostrar apenas posições significativas
    sig_positions = [r for r in chi_results if r['p_value'] < 0.05]
    if sig_positions:
        headers = ['Posição', 'Chi²', 'p-value', 'Significativo?']
        tabela = [[
            r['posicao'],
            f"{r['chi2']:.2f}",
            f"{r['p_value']:.4f}",
            r['significativo']
        ] for r in sig_positions]
        print(tabulate(tabela, headers, tablefmt='grid'))
    else:
        print("   Nenhuma posição com correlação significativa (p < 0.05)")
    
    sig_count = sum(1 for r in chi_results if r['p_value'] < 0.05)
    
    return {
        'janela': janela_nome,
        'n_concursos': len(df_janela),
        'posicoes_significativas': sig_count,
        'chi_results': chi_results
    }


def comparar_numeros_top_por_final(df, janelas):
    """
    Compara os números top de cada posição por final entre janelas.
    """
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO: NÚMEROS TOP POR FINAL ENTRE JANELAS")
    print("="*80)
    
    for posicao in [1, 15]:
        coluna = f'N{posicao}'
        print(f"\n{'─'*70}")
        print(f"🎯 POSIÇÃO {coluna}")
        print(f"{'─'*70}")
        
        headers = ['Final'] + [f'{j["nome"]} (n={j["n"]})' for j in janelas]
        tabela = []
        
        for final in range(10):
            row = [final]
            for j in janelas:
                if j['n']:
                    df_j = df.tail(j['n'])
                else:
                    df_j = df
                
                df_final = df_j[df_j['Final'] == final]
                if len(df_final) > 0:
                    top = df_final[coluna].value_counts().head(1)
                    num = int(top.index[0])
                    pct = (top.values[0] / len(df_final)) * 100
                    row.append(f"{num} ({pct:.0f}%)")
                else:
                    row.append("-")
            tabela.append(row)
        
        print(tabulate(tabela, headers, tablefmt='grid'))


def encontrar_padroes_emergentes(df, janelas):
    """
    Busca padrões que aparecem mais fortes em janelas recentes.
    """
    print("\n" + "="*80)
    print("🔍 PADRÕES EMERGENTES (mais fortes em janelas recentes)")
    print("="*80)
    
    padroes_emergentes = []
    
    for posicao in range(1, 16):
        coluna = f'N{posicao}'
        
        for final in range(10):
            # Calcular frequências em cada janela para cada número
            freq_por_janela = {}
            
            for j in janelas:
                if j['n']:
                    df_j = df.tail(j['n'])
                else:
                    df_j = df
                
                df_final = df_j[df_j['Final'] == final]
                if len(df_final) > 0:
                    freq = df_final[coluna].value_counts()
                    total = len(df_final)
                    freq_pct = (freq / total * 100).to_dict()
                    freq_por_janela[j['nome']] = freq_pct
                else:
                    freq_por_janela[j['nome']] = {}
            
            # Verificar se algum número tem tendência crescente
            for numero in range(1, 26):
                freqs = []
                for j in janelas:
                    f = freq_por_janela.get(j['nome'], {}).get(numero, 0)
                    freqs.append(f)
                
                # Padrão emergente: frequência aumenta nas janelas mais recentes
                if len(freqs) >= 3:
                    # Comparar TODOS vs últimos 30
                    if freqs[0] > 0 and freqs[-1] > 0:
                        crescimento = ((freqs[-1] - freqs[0]) / freqs[0]) * 100
                        
                        # Se cresceu mais de 50% na janela recente
                        if crescimento > 50 and freqs[-1] > 15:  # E freq > 15%
                            padroes_emergentes.append({
                                'posicao': posicao,
                                'final': final,
                                'numero': numero,
                                'freq_todos': freqs[0],
                                'freq_30': freqs[-1],
                                'crescimento': crescimento
                            })
    
    # Ordenar por crescimento
    padroes_emergentes.sort(key=lambda x: x['crescimento'], reverse=True)
    
    if padroes_emergentes:
        print("\nTop 15 padrões com maior crescimento (TODOS → Últimos 30):")
        headers = ['Posição', 'Final', 'Número', 'Freq TODOS', 'Freq Últ.30', 'Crescimento']
        tabela = []
        for p in padroes_emergentes[:15]:
            tabela.append([
                f"N{p['posicao']}",
                p['final'],
                p['numero'],
                f"{p['freq_todos']:.1f}%",
                f"{p['freq_30']:.1f}%",
                f"+{p['crescimento']:.0f}%"
            ])
        print(tabulate(tabela, headers, tablefmt='grid'))
    else:
        print("\n❌ Nenhum padrão emergente encontrado")
    
    return padroes_emergentes


def conclusao_comparativa(resultados_janelas, padroes_emergentes):
    """
    Conclusão comparativa entre todas as janelas.
    """
    print("\n" + "="*80)
    print("🎯 CONCLUSÃO COMPARATIVA")
    print("="*80)
    
    # Tabela resumo
    headers = ['Janela', 'Concursos', 'Posições c/ Correlação', 'Avaliação']
    tabela = []
    
    for r in resultados_janelas:
        sig = r['posicoes_significativas']
        if sig >= 3:
            avaliacao = "🟢 FORTE"
        elif sig >= 1:
            avaliacao = "🟡 FRACO"
        else:
            avaliacao = "🔴 NENHUM"
        
        tabela.append([
            r['janela'],
            r['n_concursos'],
            f"{sig}/15",
            avaliacao
        ])
    
    print(tabulate(tabela, headers, tablefmt='grid'))
    
    # Análise final
    max_sig = max(r['posicoes_significativas'] for r in resultados_janelas)
    n_emergentes = len(padroes_emergentes)
    
    print(f"\n📊 MÉTRICAS FINAIS:")
    print(f"   • Máximo de posições com correlação: {max_sig}/15")
    print(f"   • Padrões emergentes detectados: {n_emergentes}")
    
    if max_sig >= 3 or n_emergentes >= 10:
        print("\n⚠️  CONCLUSÃO: AGREGAR COM CAUTELA")
        print("   Existem alguns padrões em janelas recentes que podem ser explorados")
        print("   como critério TERCIÁRIO de desempate, mas NÃO como filtro primário.")
        return "CAUTELA"
    else:
        print("\n❌ CONCLUSÃO: DESCARTAR")
        print("   Mesmo em janelas recentes, não há correlação estatística suficiente")
        print("   entre o final do concurso e os números sorteados por posição.")
        print("   O efeito é muito pequeno/aleatório para ser útil.")
        return "DESCARTAR"


def main():
    """Executa análise comparativa por janelas."""
    print("="*80)
    print("🔎 ANÁLISE COMPARATIVA: FINAL × POSIÇÃO POR JANELAS TEMPORAIS")
    print("="*80)
    
    df = carregar_dados()
    
    # Definir janelas de análise
    janelas = [
        {'nome': 'TODOS', 'n': None},
        {'nome': 'Últimos 15', 'n': 15},
        {'nome': 'Últimos 10', 'n': 10},
        {'nome': 'Últimos 5', 'n': 5}
    ]
    
    # Analisar cada janela
    resultados_janelas = []
    for j in janelas:
        resultado = analisar_janela(df, j['nome'], j['n'])
        resultados_janelas.append(resultado)
    
    # Comparar números top entre janelas
    comparar_numeros_top_por_final(df, janelas)
    
    # Buscar padrões emergentes
    padroes = encontrar_padroes_emergentes(df, janelas)
    
    # Conclusão
    decisao = conclusao_comparativa(resultados_janelas, padroes)
    
    print("\n" + "="*80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("="*80)
    
    return decisao


if __name__ == "__main__":
    main()
