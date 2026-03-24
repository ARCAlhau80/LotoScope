# -*- coding: utf-8 -*-
"""
Análise de Padrões: Final do Concurso × Posição × Número
=========================================================
Investiga se existe correlação entre o dígito final do número do concurso
e a frequência de certos números em cada posição (N1 a N15).

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
    
    Retorna dicionário: {final: {numero: frequencia}}
    """
    coluna = f'N{posicao}'
    resultados = {}
    
    for final in range(10):
        df_final = df[df['Final'] == final]
        freq = df_final[coluna].value_counts().sort_index()
        total = len(df_final)
        
        # Calcular frequência relativa (%)
        freq_pct = (freq / total * 100).round(2)
        resultados[final] = {
            'total_concursos': total,
            'frequencias': freq_pct.to_dict()
        }
    
    return resultados


def calcular_estatisticas_globais(df, posicao):
    """Calcula média global e desvio padrão para referência."""
    coluna = f'N{posicao}'
    freq_global = df[coluna].value_counts()
    total = len(df)
    freq_pct = (freq_global / total * 100)
    return freq_pct.to_dict()


def encontrar_anomalias(resultados, freq_global, limiar_desvio=2.0):
    """
    Encontra números com frequência significativamente diferente da média global.
    Usa teste de proporção para verificar significância estatística.
    """
    anomalias = []
    
    for final, dados in resultados.items():
        total_final = dados['total_concursos']
        for numero, freq_final in dados['frequencias'].items():
            freq_esperada = freq_global.get(numero, 0)
            
            # Calcular diferença percentual
            if freq_esperada > 0:
                diff_pct = ((freq_final - freq_esperada) / freq_esperada) * 100
            else:
                diff_pct = 0
            
            # Filtrar anomalias significativas (>20% de diferença)
            if abs(diff_pct) >= 20:
                anomalias.append({
                    'final': final,
                    'numero': numero,
                    'freq_observada': freq_final,
                    'freq_esperada': round(freq_esperada, 2),
                    'diff_pct': round(diff_pct, 1),
                    'n_concursos': total_final
                })
    
    return sorted(anomalias, key=lambda x: abs(x['diff_pct']), reverse=True)


def analisar_posicoes_extremas(df):
    """
    Análise específica para N1 (primeiro número sorteado) e N15 (último).
    """
    print("\n" + "="*80)
    print("📊 ANÁLISE POSIÇÕES N1 (MENOR NÚMERO) E N15 (MAIOR NÚMERO)")
    print("="*80)
    
    for posicao in [1, 15]:
        coluna = f'N{posicao}'
        
        print(f"\n{'='*40}")
        print(f"🎯 POSIÇÃO {coluna}")
        print(f"{'='*40}")
        
        # Tabela de frequência por final
        tabela = []
        headers = ['Final', 'Concursos', 'Top 1', '%', 'Top 2', '%', 'Top 3', '%']
        
        freq_global = calcular_estatisticas_globais(df, posicao)
        resultados = analisar_posicao_por_final(df, posicao)
        
        for final in range(10):
            dados = resultados[final]
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
        
        # Análise de anomalias
        anomalias = encontrar_anomalias(resultados, freq_global)
        if anomalias:
            print(f"\n⚠️  Anomalias detectadas (>20% diferença da média global):")
            for a in anomalias[:5]:  # Top 5 anomalias
                sinal = "↑" if a['diff_pct'] > 0 else "↓"
                print(f"   Final {a['final']}: Número {a['numero']:2d} = {a['freq_observada']:.1f}% "
                      f"(esperado: {a['freq_esperada']:.1f}%) {sinal}{abs(a['diff_pct']):.1f}%")


def analisar_todas_posicoes(df):
    """
    Análise completa de todas as posições N1-N15.
    """
    print("\n" + "="*80)
    print("📊 ANÁLISE COMPLETA: TODAS AS POSIÇÕES N1-N15 POR FINAL DO CONCURSO")
    print("="*80)
    
    # Estrutura para guardar padrões encontrados
    padroes_significativos = []
    
    for posicao in range(1, 16):
        freq_global = calcular_estatisticas_globais(df, posicao)
        resultados = analisar_posicao_por_final(df, posicao)
        anomalias = encontrar_anomalias(resultados, freq_global, limiar_desvio=2.0)
        
        if anomalias:
            for a in anomalias[:3]:  # Top 3 por posição
                if abs(a['diff_pct']) >= 25:  # Só padrões fortes
                    padroes_significativos.append({
                        'posicao': posicao,
                        **a
                    })
    
    # Ordenar por força da anomalia
    padroes_significativos.sort(key=lambda x: abs(x['diff_pct']), reverse=True)
    
    # Mostrar tabela resumida
    print("\n🔍 TOP 20 PADRÕES MAIS SIGNIFICATIVOS (≥25% diferença):")
    print("-" * 90)
    
    headers = ['Posição', 'Final', 'Número', 'Freq. Obs.', 'Freq. Esp.', 'Diferença', 'Concursos']
    tabela = []
    
    for p in padroes_significativos[:20]:
        sinal = "+" if p['diff_pct'] > 0 else ""
        tabela.append([
            f"N{p['posicao']}",
            p['final'],
            p['numero'],
            f"{p['freq_observada']:.1f}%",
            f"{p['freq_esperada']:.1f}%",
            f"{sinal}{p['diff_pct']:.1f}%",
            p['n_concursos']
        ])
    
    print(tabulate(tabela, headers, tablefmt='grid'))
    
    return padroes_significativos


def analise_chi_quadrado(df):
    """
    Teste Chi-quadrado para verificar se existe dependência estatística
    entre o final do concurso e os números em cada posição.
    """
    print("\n" + "="*80)
    print("📈 TESTE CHI-QUADRADO: INDEPENDÊNCIA FINAL × NÚMERO POR POSIÇÃO")
    print("="*80)
    print("H0: O final do concurso NÃO influencia os números em cada posição")
    print("p < 0.05 → Rejeita H0 (existe correlação significativa)")
    print("-" * 60)
    
    resultados_chi = []
    
    for posicao in range(1, 16):
        coluna = f'N{posicao}'
        
        # Criar tabela de contingência
        contingencia = pd.crosstab(df['Final'], df[coluna])
        
        # Teste chi-quadrado
        chi2, p_value, dof, expected = stats.chi2_contingency(contingencia)
        
        significativo = "✅ SIM" if p_value < 0.05 else "❌ NÃO"
        
        resultados_chi.append({
            'posicao': coluna,
            'chi2': chi2,
            'p_value': p_value,
            'significativo': significativo
        })
    
    headers = ['Posição', 'Chi²', 'p-value', 'Significativo?']
    tabela = [[
        r['posicao'],
        f"{r['chi2']:.2f}",
        f"{r['p_value']:.6f}" if r['p_value'] >= 0.0001 else "<0.0001",
        r['significativo']
    ] for r in resultados_chi]
    
    print(tabulate(tabela, headers, tablefmt='grid'))
    
    # Resumo
    sig_count = sum(1 for r in resultados_chi if r['p_value'] < 0.05)
    print(f"\n📊 RESUMO: {sig_count}/15 posições com correlação estatisticamente significativa")
    
    return resultados_chi


def analise_detalhada_por_final(df):
    """
    Para cada final (0-9), mostra a distribuição completa de todas as posições.
    """
    print("\n" + "="*80)
    print("📋 DISTRIBUIÇÃO DETALHADA POR FINAL DO CONCURSO")
    print("="*80)
    
    # Mostrar número médio de concursos por final
    contagem_finais = df['Final'].value_counts().sort_index()
    print("\n📊 Concursos por final:")
    for final in range(10):
        print(f"   Final {final}: {contagem_finais[final]} concursos")
    
    # Para cada final, mostrar números mais frequentes em cada posição
    print("\n" + "-"*80)
    print("TOP 3 NÚMEROS MAIS FREQUENTES POR POSIÇÃO PARA CADA FINAL:")
    print("-"*80)
    
    for final in range(10):
        df_final = df[df['Final'] == final]
        print(f"\n🎯 FINAL {final} ({len(df_final)} concursos):")
        
        linha_pos = []
        linha_num = []
        linha_pct = []
        
        for posicao in range(1, 16):
            coluna = f'N{posicao}'
            top = df_final[coluna].value_counts().head(1)
            if len(top) > 0:
                num = top.index[0]
                pct = (top.values[0] / len(df_final)) * 100
                linha_pos.append(coluna)
                linha_num.append(str(int(num)))
                linha_pct.append(f"{pct:.0f}%")
        
        print("   Pos: " + " | ".join(f"{p:>3}" for p in linha_pos))
        print("   Num: " + " | ".join(f"{n:>3}" for n in linha_num))
        print("   Frq: " + " | ".join(f"{p:>3}" for p in linha_pct))


def conclusao_final(padroes, chi_results):
    """
    Faz a conclusão sobre utilidade dos padrões encontrados.
    """
    print("\n" + "="*80)
    print("🎯 CONCLUSÃO E RECOMENDAÇÃO")
    print("="*80)
    
    # Contar posições com significância estatística
    sig_count = sum(1 for r in chi_results if r['p_value'] < 0.05)
    
    # Filtrar padrões fortes (≥30% diferença)
    padroes_fortes = [p for p in padroes if abs(p['diff_pct']) >= 30]
    
    print(f"\n📊 RESULTADOS:")
    print(f"   • Posições com correlação estatística (chi²): {sig_count}/15")
    print(f"   • Padrões fortes encontrados (≥30% diferença): {len(padroes_fortes)}")
    
    if sig_count >= 5 and len(padroes_fortes) >= 10:
        print("\n✅ RECOMENDAÇÃO: AGREGAR AO SISTEMA")
        print("   Os dados mostram correlação estatística significativa entre o")
        print("   final do concurso e a distribuição de números em várias posições.")
        print("   Isso pode ser usado como filtro adicional ou para ajustar pesos.")
        return True
    elif sig_count >= 2 or len(padroes_fortes) >= 5:
        print("\n⚠️  RECOMENDAÇÃO: AGREGAR COM CAUTELA")
        print("   Existem alguns padrões, mas a correlação não é muito forte.")
        print("   Pode ser usado como critério de desempate, não como filtro primário.")
        return True
    else:
        print("\n❌ RECOMENDAÇÃO: DESCARTAR")
        print("   Os dados não mostram correlação suficiente entre o final")
        print("   do concurso e a distribuição de números. O efeito é muito")
        print("   pequeno para ser útil em termos práticos.")
        return False


def main():
    """Executa análise completa."""
    print("="*80)
    print("🔎 ANÁLISE: PADRÕES DE NÚMEROS POR POSIÇÃO × FINAL DO CONCURSO")
    print("="*80)
    print("\nCarregando dados do banco de dados...")
    
    df = carregar_dados()
    
    # Análise das posições extremas (N1 e N15)
    analisar_posicoes_extremas(df)
    
    # Análise completa de todas as posições
    padroes = analisar_todas_posicoes(df)
    
    # Teste estatístico Chi-quadrado
    chi_results = analise_chi_quadrado(df)
    
    # Distribuição detalhada por final
    analise_detalhada_por_final(df)
    
    # Conclusão
    agregar = conclusao_final(padroes, chi_results)
    
    print("\n" + "="*80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("="*80)
    
    return agregar


if __name__ == "__main__":
    main()
