#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 HIPÓTESE: POSIÇÕES-CHAVE N5/N10/N12 EM JANELAS DE 6 CONCURSOS
=================================================================
Objetivo: Verificar se certas posições (N5, N10, N12) têm números
que se REPETEM dentro de janelas de 6 concursos consecutivos.

Se sim → viável como filtro para Pool 23 níveis > N0.

Método:
1. Dividir histórico em janelas de 6 concursos
2. Para cada janela, registrar quais números aparecem em cada posição
3. Calcular taxa de repetição (mesmo número 2+ vezes na janela)
4. Comparar com baseline aleatório esperado
5. Verificar se há números que NUNCA aparecem nessas posições

Sem implementação - apenas análise estatística.
"""

import pyodbc
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
POSICOES_CHAVE = [5, 10, 12]   # N5, N10, N12
TAMANHO_JANELA = 6
JANELAS_RECENTES = 10  # Quantas das últimas janelas destacar


def carregar_dados():
    """Carrega todos os concursos ordenados"""
    conn = pyodbc.connect(CONN_STR)
    query = """
    SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
    FROM Resultados_INT
    ORDER BY Concurso ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def calcular_baseline_esperado(total_concursos_por_janela=6):
    """
    Calcula o baseline esperado se os números fossem aleatórios.
    Em cada posição N_k, o mesmo número aparecer 2+ vezes em 6 sorteios
    """
    # Para N5 (5ª menor posição em conjunto ordenado):
    # O número na posição N5 varia em torno de ~5 a ~15 (valores mais comuns)
    # Vamos calcular isso empiricamente nos dados
    pass


def analisar_repeticoes_por_janela(df, posicao):
    """
    Para uma posição, analisa repetições dentro de janelas de 6 concursos.
    
    Retorna dict com:
    - taxa_repeticao: % de janelas onde houve repetição (mesmo número 2x)
    - taxa_repeticao_3: % de janelas onde houve número 3+ vezes
    - distribuicao_numeros: quais números mais aparecem na posição nas janelas
    - top_repetidores: números que mais se repetem dentro de janelas
    """
    col = f'N{posicao}'
    todos_valores = df[col].tolist()
    total_janelas = 0
    janelas_com_repeticao = 0      # ≥1 número repetido 2x
    janelas_com_tripla = 0          # ≥1 número repetido 3x+
    
    numeros_repetidos_por_janela = []
    frequencia_global_posicao = Counter()
    frequencia_repeticao_numero = Counter()
    
    # Janelas sobrepostas vs não-sobrepostas
    # Vamos usar janelas NÃO-sobrepostas primeiro (pureza estatística)
    for inicio in range(0, len(df) - TAMANHO_JANELA + 1, TAMANHO_JANELA):
        fim = inicio + TAMANHO_JANELA
        janela_vals = df[col].iloc[inicio:fim].tolist()
        janela_concursos = df['Concurso'].iloc[inicio:fim].tolist()
        
        contagem = Counter(janela_vals)
        frequencia_global_posicao.update(janela_vals)
        
        # Registrar repetições
        repetidos = {num: cnt for num, cnt in contagem.items() if cnt >= 2}
        total_janelas += 1
        
        if repetidos:
            janelas_com_repeticao += 1
            for num, cnt in repetidos.items():
                frequencia_repeticao_numero[num] += 1
        
        if any(cnt >= 3 for cnt in contagem.values()):
            janelas_com_tripla += 1
        
        numeros_repetidos_por_janela.append({
            'inicio': janela_concursos[0],
            'fim': janela_concursos[-1],
            'numeros': janela_vals,
            'contagem': contagem,
            'repetidos': repetidos
        })
    
    taxa_rep = janelas_com_repeticao / total_janelas * 100 if total_janelas else 0
    taxa_tripla = janelas_com_tripla / total_janelas * 100 if total_janelas else 0
    
    return {
        'posicao': posicao,
        'total_janelas': total_janelas,
        'janelas_com_repeticao': janelas_com_repeticao,
        'taxa_repeticao': taxa_rep,
        'janelas_com_tripla': janelas_com_tripla,
        'taxa_repeticao_3x': taxa_tripla,
        'frequencia_global': frequencia_global_posicao,
        'frequencia_repeticao': frequencia_repeticao_numero,
        'historico_janelas': numeros_repetidos_por_janela
    }


def calcular_baseline_simulado(df, posicao, n_simulacoes=5000):
    """
    Simula embaralhamento aleatório para calcular o baseline:
    se os números fossem aleatórios, qual seria a taxa de repetição?
    """
    col = f'N{posicao}'
    valores = df[col].tolist()
    
    taxas_sim = []
    for _ in range(n_simulacoes):
        shuffled = np.random.permutation(valores)
        janelas_rep = 0
        total_jan = 0
        for i in range(0, len(shuffled) - TAMANHO_JANELA + 1, TAMANHO_JANELA):
            janela = shuffled[i:i+TAMANHO_JANELA]
            if len(set(janela)) < TAMANHO_JANELA:
                janelas_rep += 1
            total_jan += 1
        taxas_sim.append(janelas_rep / total_jan * 100 if total_jan else 0)
    
    return {
        'media': np.mean(taxas_sim),
        'std': np.std(taxas_sim),
        'percentil_95': np.percentile(taxas_sim, 95),
        'percentil_5': np.percentile(taxas_sim, 5)
    }


def analisar_persistencia_ultima_janela(df, posicao, historico_janelas):
    """
    Para o FILTRO prático:
    Dado que estamos na próxima janela, qual N% dos números da janela atual
    vai aparecer na próxima posição?
    
    Ou seja: se na janela atual (últimos 6) o número X apareceu em N5,
    qual probabilidade de X aparecer em N5 na próxima janela?
    """
    col = f'N{posicao}'
    
    # Para cada par de janelas consecutivas (treino → teste)
    acertos_predicao_repetido = []
    acertos_predicao_nao_repetido = []
    
    for i in range(1, len(historico_janelas)):
        janela_atual = historico_janelas[i-1]
        janela_proxima = historico_janelas[i]
        
        nums_atual = set(janela_atual['numeros'])
        nums_proxima = set(janela_proxima['numeros'])
        
        # Números que se "previram" ficar (repetidos na janela atual)
        previstos_persistentes = set(janela_atual['repetidos'].keys())
        
        # Qual % dos previstos realmente apareceu na próxima janela?
        if previstos_persistentes:
            encontrados = previstos_persistentes & nums_proxima
            acertos_predicao_repetido.append(len(encontrados) / len(previstos_persistentes))
        
        # Controle: números NÃO-repetidos — qual % persistiu?
        nao_repetidos = nums_atual - previstos_persistentes
        if nao_repetidos:
            encontrados_nr = nao_repetidos & nums_proxima
            acertos_predicao_nao_repetido.append(len(encontrados_nr) / len(nao_repetidos))
    
    media_pred = np.mean(acertos_predicao_repetido) * 100 if acertos_predicao_repetido else 0
    media_ctrl = np.mean(acertos_predicao_nao_repetido) * 100 if acertos_predicao_nao_repetido else 0
    
    return {
        'taxa_predicao_repetido': media_pred,
        'taxa_predicao_controle': media_ctrl,
        'ganho_predicao': media_pred - media_ctrl
    }


def analisar_exclusividade_posicional(df, posicoes_chave):
    """
    Analisa quais números NUNCA ou RARAMENTE aparecem em N5, N10, N12.
    Estes são candidatos a EXCLUÍDOS pelo filtro.
    
    Retorna: por posição, os números abaixo da média de frequência
    """
    resultado = {}
    total = len(df)
    
    for pos in posicoes_chave:
        col = f'N{pos}'
        contagem = Counter(df[col].tolist())
        media = total / 25  # Baseline se fosse uniforme
        
        # Todos os números de 1-25
        tabela = []
        for num in range(1, 26):
            freq = contagem.get(num, 0)
            pct = freq / total * 100
            tabela.append({'numero': num, 'freq': freq, 'pct': pct})
        
        # Ordenar por frequência
        tabela.sort(key=lambda x: x['freq'])
        
        # Separar em quintis
        df_tab = pd.DataFrame(tabela)
        q20 = df_tab['freq'].quantile(0.20)  # 20% mais raros
        q80 = df_tab['freq'].quantile(0.80)  # 20% mais comuns
        
        resultado[pos] = {
            'media_freq': media,
            'media_real': df_tab['freq'].mean(),
            'tabela': tabela,
            'raros_20pct': df_tab[df_tab['freq'] <= q20]['numero'].tolist(),
            'comuns_80pct': df_tab[df_tab['freq'] >= q80]['numero'].tolist(),
            'zeros': [num for num in range(1, 26) if contagem.get(num, 0) == 0]
        }
    
    return resultado


def analisar_janelas_sobrepostas(df, posicao, passo=1):
    """
    Janelas sobrepostas (rolling window) para ver padrão mais contínuo.
    Útil para o filtro real: "na janela atual dos últimos 6, quais números se repetiram?"
    """
    col = f'N{posicao}'
    n = len(df)
    
    repeticoes_por_posicao = []
    for i in range(n - TAMANHO_JANELA + 1):
        janela = df[col].iloc[i:i+TAMANHO_JANELA].tolist()
        concurso_base = df['Concurso'].iloc[i+TAMANHO_JANELA-1]
        contagem = Counter(janela)
        repetidos = [num for num, cnt in contagem.items() if cnt >= 2]
        repeticoes_por_posicao.append({
            'concurso_target': concurso_base,
            'repetidos_na_janela': repetidos,
            'qtde': len(repetidos)
        })
    
    return repeticoes_por_posicao


def calcular_taxa_restricao_viavel(df, posicoes_chave, historico_exc, window_sobrepostas):
    """
    Se usarmos o filtro: "excluir combos onde o número em N5 é um dos raros (20% piores)",
    quanto reduzimos o espaço e quantos jackpots perdemos?
    
    Simulação retroativa simples.
    """
    col_map = {pos: f'N{pos}' for pos in posicoes_chave}
    
    taxa_restricao = {}
    for pos in posicoes_chave:
        col = f'N{pos}'
        raros = set(historico_exc[pos]['raros_20pct'])
        
        # % dos resultados reais onde o número sorteado estava nos "raros"
        resultados_reais = df[col].tolist()
        bloqueados = sum(1 for x in resultados_reais if x in raros)
        taxa_restricao[pos] = {
            'pct_jackpots_bloqueados': bloqueados / len(resultados_reais) * 100,
            'numeros_raros': list(raros)
        }
    
    return taxa_restricao


def imprimir_separador(titulo):
    print(f"\n{'='*70}")
    print(f"  {titulo}")
    print('='*70)


def main():
    print("🔬 HIPÓTESE: POSIÇÕES-CHAVE N5/N10/N12 EM JANELAS DE 6 CONCURSOS")
    print("="*70)
    print(f"  Posições analisadas : N{POSICOES_CHAVE}")
    print(f"  Tamanho da janela   : {TAMANHO_JANELA} concursos")
    print(f"  Base histórica      : Todos os concursos (3.642+)")
    print("="*70)
    
    print("\n⏳ Carregando dados...")
    df = carregar_dados()
    total = len(df)
    print(f"✅ {total} concursos carregados ({df['Concurso'].min()} → {df['Concurso'].max()})")

    # ─────────────────────────────────────────────────────────────────────
    # BLOCO 1: Frequência histórica raw em N5, N10, N12
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("BLOCO 1 — FREQUÊNCIA HISTÓRICA POR POSIÇÃO (N5 / N10 / N12)")
    
    exclusividade = analisar_exclusividade_posicional(df, POSICOES_CHAVE)
    
    for pos in POSICOES_CHAVE:
        info = exclusividade[pos]
        print(f"\n📍 POSIÇÃO N{pos}")
        print(f"   Média freq esperada (uniforme): {info['media_freq']:.1f} vezes em {total}")
        print(f"   Média freq real               : {info['media_real']:.1f} vezes")
        
        # Top 5 mais frequentes e 5 mais raros
        tab = info['tabela']
        print(f"   ▲ Mais comuns (top 5)    : ", end='')
        for t in sorted(tab, key=lambda x: -x['freq'])[:5]:
            print(f"N{t['numero']:2d}={t['pct']:.1f}%", end='  ')
        print()
        
        print(f"   ▼ Mais raros (bottom 5)  : ", end='')
        for t in sorted(tab, key=lambda x: x['freq'])[:5]:
            print(f"N{t['numero']:2d}={t['pct']:.1f}%", end='  ')
        print()
        
        print(f"   Números com 0 ocorrências: {info['zeros'] if info['zeros'] else 'Nenhum'}")
        print(f"   Raros (quintil 20%)       : {sorted(info['raros_20pct'])}")
        print(f"   Comuns (quintil 80%)      : {sorted(info['comuns_80pct'])}")
    
    # ─────────────────────────────────────────────────────────────────────
    # BLOCO 2: Taxa de repetição em janelas de 6 (não-sobrepostas)
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("BLOCO 2 — REPETIÇÃO DE NÚMERO NA MESMA POSIÇÃO (janelas de 6)")
    
    print(f"\n  Baseline esperado (aleatório):")
    print(f"  Se valores fossem uniformes 1-25 com reposição:")
    print(f"  P(repetição em 6 draws) ≈ calculado por simulação...\n")
    
    analises = {}
    for pos in POSICOES_CHAVE:
        print(f"  ⏳ Analisando N{pos}...")
        analises[pos] = analisar_repeticoes_por_janela(df, pos)
        baseline = calcular_baseline_simulado(df, pos, n_simulacoes=2000)
        analises[pos]['baseline'] = baseline
    
    print(f"\n{'Posição':<10} {'Janelas':<10} {'Repetições':<12} {'Taxa Real':<12} "
          f"{'Baseline':<12} {'Diferença':<12} {'Significativo?'}")
    print("-"*80)
    
    for pos in POSICOES_CHAVE:
        a = analises[pos]
        b = a['baseline']
        diff = a['taxa_repeticao'] - b['media']
        z_score = diff / b['std'] if b['std'] > 0 else 0
        sig = "✅ SIM" if abs(z_score) > 2 else "❌ NÃO"
        print(f"  N{pos:<7} {a['total_janelas']:<10} {a['janelas_com_repeticao']:<12} "
              f"{a['taxa_repeticao']:<12.1f} {b['media']:<12.1f} {diff:<12.1f} {sig} (z={z_score:.1f})")
    
    # ─────────────────────────────────────────────────────────────────────
    # BLOCO 3: Números que mais se repetem DENTRO das janelas
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("BLOCO 3 — TOP NÚMEROS REPETIDORES POR POSIÇÃO (dentro das janelas)")
    
    for pos in POSICOES_CHAVE:
        a = analises[pos]
        top = a['frequencia_repeticao'].most_common(10)
        total_janelas = a['total_janelas']
        
        print(f"\n  📍 N{pos} — números que mais repetiram na mesma posição dentro de janelas {TAMANHO_JANELA}:")
        for num, cnt in top:
            pct_janelas = cnt / total_janelas * 100
            print(f"     Número {num:2d}: repetiu em {cnt:4d} janelas ({pct_janelas:.1f}% das janelas)")
    
    # ─────────────────────────────────────────────────────────────────────
    # BLOCO 4: Poder preditivo — repetido na janela anterior → aparece na próxima?
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("BLOCO 4 — PODER PREDITIVO (repetido na janela atual → reaparece na próxima?)")
    
    print(f"\n  Lógica: Se o número X se repetiu em N{POSICOES_CHAVE} na janela atual,")
    print(f"  qual a chance de aparece de novo nessa posição na próxima janela?")
    print(f"  Comparado com números NÃO-repetidos (controle).\n")
    
    print(f"  {'Posição':<10} {'Taxa Repetido→Próx':<22} {'Taxa Controle':<20} {'Ganho'}")
    print("  " + "-"*65)
    
    for pos in POSICOES_CHAVE:
        a = analises[pos]
        pred = analisar_persistencia_ultima_janela(df, pos, a['historico_janelas'])
        print(f"  N{pos:<8} {pred['taxa_predicao_repetido']:<22.1f}%"
              f"{pred['taxa_predicao_controle']:<20.1f}%"
              f"{pred['ganho_predicao']:+.1f}pp")
    
    # ─────────────────────────────────────────────────────────────────────
    # BLOCO 5: Custo do filtro — % de jackpots que bloquearia
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("BLOCO 5 — CUSTO DO FILTRO (se excluir raros 20% da posição)")
    
    custo = calcular_taxa_restricao_viavel(df, POSICOES_CHAVE, exclusividade, None)
    
    print(f"\n  Filtro proposto: Excluir combinações onde o número em N5/N10/N12")
    print(f"  pertence ao quintil inferior de frequência histórica nessa posição.\n")
    
    for pos in POSICOES_CHAVE:
        c = custo[pos]
        print(f"  N{pos}: bloquearia {c['pct_jackpots_bloqueados']:.1f}% dos resultados reais")
        print(f"        Números excluídos: {c['numeros_raros']}")
    
    # ─────────────────────────────────────────────────────────────────────
    # BLOCO 6: Análise das últimas janelas (janela atual)
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("BLOCO 6 — ÚLTIMAS 5 JANELAS (análise recente)")
    
    for pos in POSICOES_CHAVE:
        a = analises[pos]
        ultimas = a['historico_janelas'][-5:]
        print(f"\n  📍 N{pos} — últimas {len(ultimas)} janelas:")
        for j in ultimas:
            nums_str = " ".join(f"{n:2d}" for n in j['numeros'])
            if j['repetidos']:
                rep_str = f"  🔁 REPETE: {list(j['repetidos'].keys())}"
            else:
                rep_str = "  ─ sem repetição"
            print(f"   Conc. {j['inicio']}-{j['fim']}: [{nums_str}]{rep_str}")
    
    # ─────────────────────────────────────────────────────────────────────
    # BLOCO 7: Janela atual (para Concurso 3643 — próximo sorteio)
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("BLOCO 7 — JANELA ATUAL (últimos 6 concursos → candidatos para 3643)")
    
    ultimos_6 = df.tail(TAMANHO_JANELA)
    print(f"\n  Concursos: {ultimos_6['Concurso'].iloc[0]} → {ultimos_6['Concurso'].iloc[-1]}")
    print(f"\n  {'Conc.':<8}", end='')
    for pos in POSICOES_CHAVE:
        print(f"  N{pos:<5}", end='')
    print()
    print("  " + "-"*35)
    
    for _, row in ultimos_6.iterrows():
        print(f"  {int(row['Concurso']):<8}", end='')
        for pos in POSICOES_CHAVE:
            print(f"  {int(row[f'N{pos}']):<7}", end='')
        print()
    
    print(f"\n  → Repetições na janela atual:")
    for pos in POSICOES_CHAVE:
        col = f'N{pos}'
        vals = ultimos_6[col].tolist()
        cnt = Counter(vals)
        repetidos = {num: c for num, c in cnt.items() if c >= 2}
        if repetidos:
            print(f"     N{pos}: {repetidos}  → candidatos a PERSISTIR em 3643")
        else:
            print(f"     N{pos}: sem repetição na janela atual")
    
    # ─────────────────────────────────────────────────────────────────────
    # RESUMO EXECUTIVO
    # ─────────────────────────────────────────────────────────────────────
    imprimir_separador("RESUMO EXECUTIVO — VIABILIDADE DO FILTRO")
    
    print("""
  VIABILIDADE DO FILTRO POR POSIÇÃO-CHAVE EM JANELAS DE 6:
  
  Para ser VIÁVEL o filtro precisa de:
    1. Taxa de repetição real > baseline (número aparece mais do que aleatório)
    2. Poder preditivo > 0 (se repetiu → maior chance de aparecer de novo)
    3. Custo aceitável (não bloquear >20% dos jackpots reais)
  
  Análise completa acima. Veja z-scores no Bloco 2 para significância estatística.
  
  PRÓXIMO PASSO (se aprovado):
    Implementar filtro em Pool 23 a partir do Nível 1 ou Nível 2,
    com tolerance (falhas permitidas) = 1 para segurança.
""")


if __name__ == '__main__':
    main()
