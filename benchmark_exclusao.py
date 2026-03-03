# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           BENCHMARK: ESTRATÉGIA DE EXCLUSÃO vs ALEATÓRIO                     ║
║                                                                              ║
║  Compara a performance da estratégia SUPERÁVIT com exclusões aleatórias      ║
║  para verificar se a estratégia realmente supera o acaso.                    ║
║                                                                              ║
║  Criado: 03/03/2026                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pyodbc
import json
import random
from collections import Counter
from datetime import datetime
import os

# Conexão com banco
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def carregar_resultados():
    """Carrega todos os resultados do banco"""
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso ASC
    """)
    
    resultados = {}
    for row in cursor.fetchall():
        resultados[row[0]] = {
            'concurso': row[0],
            'numeros': list(row[1:16]),
            'set': set(row[1:16])
        }
    
    conn.close()
    return resultados


def calcular_exclusao_estrategia(dados_historicos, qtd_excluir=2):
    """
    Calcula exclusões usando a estratégia SUPERÁVIT v2.0
    (mesma lógica do Pool 23 Híbrido)
    """
    def freq_janela(tamanho):
        freq = Counter()
        for r in dados_historicos[:min(tamanho, len(dados_historicos))]:
            freq.update(r['numeros'])
        return {n: freq.get(n, 0) / min(tamanho, len(dados_historicos)) * 100 for n in range(1, 26)}
    
    freq_5 = freq_janela(5)
    freq_50 = freq_janela(50)
    
    candidatos = []
    for n in range(1, 26):
        fc = freq_5[n]
        fl = freq_50[n]
        indice_debito = fl - fc
        
        score = 0
        apareceu_recente = any(n in r['numeros'] for r in dados_historicos[:3])
        
        if apareceu_recente:
            score -= 10
        elif indice_debito < -40 and fc >= 80:
            score += 5
        elif indice_debito < -30 and not apareceu_recente:
            score += 4
        elif indice_debito < -20 and not apareceu_recente:
            score += 3
        elif indice_debito < -10:
            score += 2
        elif indice_debito > 20 and fc < 40:
            score += 3
        elif indice_debito > 35:
            score += 4
        
        candidatos.append((n, score, indice_debito, fc))
    
    candidatos.sort(key=lambda x: (-x[1], x[3]))
    excluir = [c[0] for c in candidatos[:qtd_excluir]]
    
    return sorted(excluir)


def calcular_exclusao_aleatoria(qtd_excluir=2):
    """Exclui números aleatoriamente"""
    return sorted(random.sample(range(1, 26), qtd_excluir))


def executar_benchmark(concurso_inicio, concurso_fim, qtd_excluir=2, n_simulacoes_aleatorio=100):
    """
    Executa benchmark comparando estratégia vs aleatório
    """
    print("\n" + "═"*70)
    print("🔬 BENCHMARK: ESTRATÉGIA SUPERÁVIT vs ALEATÓRIO")
    print("═"*70)
    
    # Carregar dados
    print("\n📥 Carregando dados...")
    todos_resultados = carregar_resultados()
    concursos_disponiveis = sorted(todos_resultados.keys())
    
    # Validar range
    concurso_inicio = max(concurso_inicio, concursos_disponiveis[0] + 100)
    concurso_fim = min(concurso_fim, concursos_disponiveis[-1])
    
    print(f"   ✅ {len(concursos_disponiveis)} concursos disponíveis")
    print(f"   📅 Testando: {concurso_inicio} a {concurso_fim}")
    print(f"   🎯 Excluindo: {qtd_excluir} números por concurso")
    print(f"   🎲 Simulações aleatórias: {n_simulacoes_aleatorio}")
    
    # Resultados
    resultados_estrategia = {'corretos': 0, 'errados': 0, 'detalhes': []}
    resultados_aleatorio = {'corretos': [], 'media': 0}
    
    total_testes = 0
    
    print("\n" + "─"*70)
    print("🔄 Executando benchmark...")
    print("─"*70)
    
    for concurso in range(concurso_inicio, concurso_fim + 1):
        if concurso not in todos_resultados:
            continue
        
        resultado_real = todos_resultados[concurso]['set']
        
        # Preparar dados históricos (até concurso anterior)
        dados_ate_anterior = [todos_resultados[c] for c in sorted(todos_resultados.keys()) 
                              if c < concurso]
        dados_ate_anterior.sort(key=lambda x: x['concurso'], reverse=True)
        
        if len(dados_ate_anterior) < 50:
            continue
        
        total_testes += 1
        
        # ═══════════════════════════════════════════════════════════════════
        # TESTE 1: ESTRATÉGIA SUPERÁVIT
        # ═══════════════════════════════════════════════════════════════════
        exclusao_estrategia = calcular_exclusao_estrategia(dados_ate_anterior, qtd_excluir)
        
        # Verificar se NENHUM dos excluídos saiu no resultado
        errou = any(n in resultado_real for n in exclusao_estrategia)
        
        if errou:
            resultados_estrategia['errados'] += 1
        else:
            resultados_estrategia['corretos'] += 1
        
        resultados_estrategia['detalhes'].append({
            'concurso': concurso,
            'excluidos': exclusao_estrategia,
            'correto': not errou,
            'numeros_errados': [n for n in exclusao_estrategia if n in resultado_real]
        })
        
        # ═══════════════════════════════════════════════════════════════════
        # TESTE 2: EXCLUSÃO ALEATÓRIA (múltiplas simulações)
        # ═══════════════════════════════════════════════════════════════════
        corretos_aleatorio = 0
        for _ in range(n_simulacoes_aleatorio):
            exclusao_aleatoria = calcular_exclusao_aleatoria(qtd_excluir)
            errou_aleatorio = any(n in resultado_real for n in exclusao_aleatoria)
            if not errou_aleatorio:
                corretos_aleatorio += 1
        
        resultados_aleatorio['corretos'].append(corretos_aleatorio / n_simulacoes_aleatorio)
        
        # Progresso
        if total_testes % 20 == 0:
            print(f"   Progresso: {total_testes} concursos testados...")
    
    # ═══════════════════════════════════════════════════════════════════
    # CALCULAR ESTATÍSTICAS
    # ═══════════════════════════════════════════════════════════════════
    taxa_estrategia = resultados_estrategia['corretos'] / total_testes * 100
    taxa_aleatorio_media = sum(resultados_aleatorio['corretos']) / len(resultados_aleatorio['corretos']) * 100
    
    # Probabilidade teórica (excluir N números e nenhum sair)
    # P = C(10, qtd_excluir) / C(25, qtd_excluir)
    # Para qtd_excluir=2: C(10,2)/C(25,2) = 45/300 = 15%
    from math import comb
    prob_teorica = comb(10, qtd_excluir) / comb(25, qtd_excluir) * 100
    
    # ═══════════════════════════════════════════════════════════════════
    # EXIBIR RESULTADOS
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "═"*70)
    print("📊 RESULTADOS DO BENCHMARK")
    print("═"*70)
    
    print(f"\n   Total de concursos testados: {total_testes}")
    print(f"   Números excluídos por concurso: {qtd_excluir}")
    
    print("\n" + "─"*70)
    print("   COMPARAÇÃO DE TAXAS DE ACERTO (exclusão correta = nenhum excluído saiu)")
    print("─"*70)
    
    print(f"\n   📐 PROBABILIDADE TEÓRICA: {prob_teorica:.1f}%")
    print(f"       (excluir {qtd_excluir} dos 10 que NÃO saem, de 25 possíveis)")
    
    print(f"\n   🎲 ALEATÓRIO (média de {n_simulacoes_aleatorio} simulações):")
    print(f"       Taxa de acerto: {taxa_aleatorio_media:.1f}%")
    print(f"       Status: {'≈ esperado' if abs(taxa_aleatorio_media - prob_teorica) < 3 else '⚠️ desvio'}")
    
    print(f"\n   🎯 ESTRATÉGIA SUPERÁVIT:")
    print(f"       Taxa de acerto: {taxa_estrategia:.1f}%")
    print(f"       Corretos: {resultados_estrategia['corretos']}/{total_testes}")
    print(f"       Errados: {resultados_estrategia['errados']}/{total_testes}")
    
    # Comparação
    diferenca = taxa_estrategia - taxa_aleatorio_media
    diferenca_teorica = taxa_estrategia - prob_teorica
    
    print("\n" + "─"*70)
    print("   ANÁLISE COMPARATIVA")
    print("─"*70)
    
    if diferenca > 3:
        print(f"\n   ✅ ESTRATÉGIA MELHOR que aleatório por {diferenca:.1f} pontos percentuais")
    elif diferenca < -3:
        print(f"\n   ❌ ESTRATÉGIA PIOR que aleatório por {abs(diferenca):.1f} pontos percentuais")
    else:
        print(f"\n   ⚠️ DIFERENÇA MARGINAL ({diferenca:+.1f}pp) - estatisticamente insignificante")
    
    print(f"\n   vs Teórico: {diferenca_teorica:+.1f}pp")
    print(f"   vs Aleatório: {diferenca:+.1f}pp")
    
    # Análise de erros
    print("\n" + "─"*70)
    print("   ANÁLISE DE ERROS DA ESTRATÉGIA")
    print("─"*70)
    
    numeros_errados_freq = Counter()
    for d in resultados_estrategia['detalhes']:
        for n in d['numeros_errados']:
            numeros_errados_freq[n] += 1
    
    if numeros_errados_freq:
        print("\n   Números que a estratégia exclui mas SAEM frequentemente:")
        for num, freq in numeros_errados_freq.most_common(10):
            pct = freq / total_testes * 100
            print(f"      • Número {num:2d}: {freq}x ({pct:.1f}%)")
    
    # Salvando resultados
    resultado_final = {
        'data': datetime.now().isoformat(),
        'config': {
            'concurso_inicio': concurso_inicio,
            'concurso_fim': concurso_fim,
            'qtd_excluir': qtd_excluir,
            'n_simulacoes': n_simulacoes_aleatorio
        },
        'resultados': {
            'total_testes': total_testes,
            'estrategia': {
                'corretos': resultados_estrategia['corretos'],
                'errados': resultados_estrategia['errados'],
                'taxa': taxa_estrategia
            },
            'aleatorio': {
                'taxa_media': taxa_aleatorio_media
            },
            'teorico': {
                'taxa': prob_teorica
            },
            'comparacao': {
                'estrategia_vs_aleatorio': diferenca,
                'estrategia_vs_teorico': diferenca_teorica
            }
        }
    }
    
    print("\n" + "═"*70)
    
    return resultado_final


def analisar_historico_existente():
    """Analisa o histórico de aprendizado existente"""
    historico_path = os.path.join(os.path.dirname(__file__), '..', 'dados', 'historico_aprendizado.json')
    
    print("\n" + "═"*70)
    print("📋 ANÁLISE DO HISTÓRICO DE APRENDIZADO EXISTENTE")
    print("═"*70)
    
    try:
        with open(historico_path, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    except:
        print("   ❌ Não foi possível carregar o histórico")
        return
    
    total = historico.get('total_backtests', 0)
    corretos = historico.get('exclusao_correta', 0)
    errados = historico.get('exclusao_errada', 0)
    
    print(f"\n   📊 ESTATÍSTICAS DO HISTÓRICO:")
    print(f"      Total de backtests: {total}")
    print(f"      Exclusões corretas: {corretos}")
    print(f"      Exclusões erradas: {errados}")
    
    if total > 0:
        taxa = corretos / total * 100
        print(f"      Taxa de acerto: {taxa:.1f}%")
        
        # Comparar com teórico (assumindo 2 exclusões)
        from math import comb
        prob_teorica = comb(10, 2) / comb(25, 2) * 100  # 15%
        
        print(f"\n   📐 COMPARAÇÃO:")
        print(f"      Probabilidade teórica (excluir 2): {prob_teorica:.1f}%")
        print(f"      Taxa observada: {taxa:.1f}%")
        print(f"      Diferença: {taxa - prob_teorica:+.1f}pp")
        
        if taxa > prob_teorica + 3:
            print(f"\n   ✅ A estratégia está ACIMA do esperado!")
        elif taxa < prob_teorica - 3:
            print(f"\n   ❌ A estratégia está ABAIXO do esperado")
        else:
            print(f"\n   ⚠️ A estratégia está PRÓXIMA do esperado (sem vantagem clara)")
    
    # Jackpots por nível
    niveis = historico.get('niveis_jackpot', {})
    if niveis:
        print(f"\n   🏆 JACKPOTS POR NÍVEL:")
        for nivel, qtd in sorted(niveis.items(), key=lambda x: int(x[0])):
            print(f"      Nível {nivel}: {qtd} jackpots")
    
    print("\n" + "═"*70)


if __name__ == "__main__":
    print("\n" + "🔬"*35)
    print("   BENCHMARK DE EXCLUSÃO - LOTOSCOPE")
    print("🔬"*35)
    
    # Primeiro, analisar histórico existente
    analisar_historico_existente()
    
    # Perguntar se quer executar benchmark
    print("\n   OPÇÕES:")
    print("   [1] Executar benchmark completo (últimos 100 concursos)")
    print("   [2] Executar benchmark customizado")
    print("   [0] Sair")
    
    opcao = input("\n   Escolha: ").strip()
    
    if opcao == '1':
        resultado = executar_benchmark(
            concurso_inicio=3500,  # Últimos ~120 concursos
            concurso_fim=3620,
            qtd_excluir=2,
            n_simulacoes_aleatorio=1000
        )
    elif opcao == '2':
        try:
            inicio = int(input("   Concurso inicial: ").strip())
            fim = int(input("   Concurso final: ").strip())
            qtd = int(input("   Quantidade a excluir [2]: ").strip() or "2")
            resultado = executar_benchmark(inicio, fim, qtd, 1000)
        except:
            print("   ❌ Entrada inválida")
    
    input("\n   Pressione ENTER para sair...")
