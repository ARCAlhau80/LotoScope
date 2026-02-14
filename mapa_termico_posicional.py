# -*- coding: utf-8 -*-
"""
MAPA TÉRMICO POSICIONAL - Números Menos Prováveis por Posição
==============================================================
Mostra para cada posição (N1-N15) os 3 números MENOS PROVÁVEIS de sair,
baseado em indicadores dinâmicos validados:
- Repetição na mesma posição (69% assertividade)
- Frequência recente na posição (até 84% assertividade)
- Soma + Saldo combinados (60-62% assertividade)
"""

import pyodbc
from collections import Counter, defaultdict
from tabulate import tabulate
from colorama import init, Fore, Back, Style

init()

# Conexão com banco
CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'


def carregar_resultados(n_concursos=30):
    """Carrega os últimos N concursos"""
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {n_concursos} Concurso, SomaTotal,
               N1, N2, N3, N4, N5, N6, N7, N8, 
               N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def obter_amplitude_posicao():
    """Retorna a amplitude P10-P90 de cada posição baseado no histórico"""
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    amplitudes = {}
    for i in range(1, 16):
        cursor.execute(f"""
            SELECT N{i} FROM Resultados_INT ORDER BY Concurso
        """)
        valores = [row[0] for row in cursor.fetchall()]
        valores.sort()
        p10 = valores[int(len(valores) * 0.10)]
        p90 = valores[int(len(valores) * 0.90)]
        amplitudes[i] = (p10, p90)
    
    conn.close()
    return amplitudes


def calcular_score_improbabilidade(resultados, amplitudes):
    """
    Calcula score de improbabilidade para cada número em cada posição.
    Retorna dict: {posicao: {numero: score, ...}, ...}
    
    Indicadores usados:
    1. Repetição na mesma posição (peso 30%)
    2. Frequência recente na posição (peso 40%)
    3. Tendência soma/saldo (peso 30%)
    """
    scores = defaultdict(lambda: defaultdict(float))
    
    ultimo = resultados[0]  # Mais recente
    concurso_atual = ultimo[0]
    soma_atual = ultimo[1]
    posicoes_atuais = [ultimo[i+2] for i in range(15)]  # N1 a N15
    
    # Calcular saldo (variação média da soma)
    somas = [r[1] for r in resultados[:10]]
    media_soma = sum(somas) / len(somas)
    saldo = soma_atual - media_soma
    
    print(f"\n📊 Concurso {concurso_atual} | Soma: {soma_atual} | Saldo: {saldo:+.1f}")
    
    # Para cada posição
    for pos in range(1, 16):
        p10, p90 = amplitudes[pos]
        
        # 1. INDICADOR: Repetição na mesma posição
        numero_atual = posicoes_atuais[pos-1]
        repeticoes = 0
        for r in resultados[:5]:
            if r[pos+1] == numero_atual:
                repeticoes += 1
            else:
                break
        
        # Se repetiu 3+ vezes, esse número é MENOS provável (70% chance de mudar)
        if repeticoes >= 3:
            scores[pos][numero_atual] += 40  # Peso alto
        elif repeticoes >= 2:
            scores[pos][numero_atual] += 20
        
        # 2. INDICADOR: Frequência recente na posição
        freq_recente = Counter()
        for r in resultados[:10]:
            freq_recente[r[pos+1]] += 1
        
        # Números muito frequentes tendem a não repetir
        for num, freq in freq_recente.items():
            if freq >= 5:
                scores[pos][num] += 50  # Muito frequente
            elif freq >= 4:
                scores[pos][num] += 35
            elif freq >= 3:
                scores[pos][num] += 20
        
        # 3. INDICADOR: Tendência soma/saldo
        # Se soma alta + saldo positivo → números ALTOS menos prováveis
        # Se soma baixa + saldo negativo → números BAIXOS menos prováveis
        
        if soma_atual > 210 and saldo > 0:
            # Números altos menos prováveis
            for num in range(p90, 26):
                if num <= 25:
                    scores[pos][num] += 25
        elif soma_atual > 200 and saldo > 2:
            for num in range(p90-1, 26):
                if num <= 25:
                    scores[pos][num] += 15
                    
        if soma_atual < 180 and saldo < 0:
            # Números baixos menos prováveis
            for num in range(1, p10+1):
                scores[pos][num] += 25
        elif soma_atual < 190 and saldo < -2:
            for num in range(1, p10+2):
                scores[pos][num] += 15
        
        # 4. BÔNUS: Número que saiu agora E é extremo (fora P10-P90) tende a compensar
        if numero_atual < p10:
            # Número baixo saiu, números baixos menos prováveis no próximo
            scores[pos][numero_atual] += 15
        elif numero_atual > p90:
            # Número alto saiu, números altos menos prováveis
            scores[pos][numero_atual] += 15
    
    return scores, concurso_atual, soma_atual, saldo


def obter_top3_menos_provaveis(scores, amplitudes):
    """
    Para cada posição, retorna os 3 números MENOS PROVÁVEIS (maior score).
    Só considera números dentro da amplitude viável.
    """
    top3_por_posicao = {}
    
    for pos in range(1, 16):
        p10, p90 = amplitudes[pos]
        # Expandir amplitude para incluir casos extremos mas possíveis
        min_val = max(1, p10 - 2)
        max_val = min(25, p90 + 2)
        
        # Criar lista de (numero, score) para números na amplitude
        candidatos = []
        for num in range(min_val, max_val + 1):
            score = scores[pos].get(num, 0)
            candidatos.append((num, score))
        
        # Ordenar por score (maior = menos provável)
        candidatos.sort(key=lambda x: -x[1])
        
        # Top 3
        top3 = candidatos[:3]
        top3_por_posicao[pos] = top3
    
    return top3_por_posicao


def exibir_mapa_termico(top3, concurso, soma, saldo):
    """Exibe o mapa térmico visual dos números menos prováveis"""
    
    print("\n" + "=" * 80)
    print(f"🔥 MAPA TÉRMICO - NÚMEROS MENOS PROVÁVEIS POR POSIÇÃO")
    print(f"   Baseado no Concurso {concurso} | Soma: {soma} | Saldo: {saldo:+.1f}")
    print("=" * 80)
    
    # Preparar tabela
    headers = ["Posição", "Menos Provável", "2º Menos", "3º Menos", "Scores"]
    rows = []
    
    for pos in range(1, 16):
        top = top3[pos]
        
        # Formatação com cores baseada no score
        nums = []
        scores_str = []
        for num, score in top:
            if score >= 50:
                nums.append(f"{Fore.RED}{num:2d}{Style.RESET_ALL}")
            elif score >= 30:
                nums.append(f"{Fore.YELLOW}{num:2d}{Style.RESET_ALL}")
            elif score >= 15:
                nums.append(f"{Fore.CYAN}{num:2d}{Style.RESET_ALL}")
            else:
                nums.append(f"{num:2d}")
            scores_str.append(f"{score:.0f}")
        
        rows.append([
            f"N{pos:02d}",
            nums[0] if len(nums) > 0 else "-",
            nums[1] if len(nums) > 1 else "-",
            nums[2] if len(nums) > 2 else "-",
            ", ".join(scores_str)
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Legenda
    print("\n📋 LEGENDA:")
    print(f"   {Fore.RED}■{Style.RESET_ALL} Score ≥50 = MUITO improvável (alta confiança)")
    print(f"   {Fore.YELLOW}■{Style.RESET_ALL} Score 30-49 = Improvável (média confiança)")
    print(f"   {Fore.CYAN}■{Style.RESET_ALL} Score 15-29 = Levemente improvável")
    print(f"   □ Score <15 = Sem indicação forte")


def exibir_tabela_visual_compacta(top3, amplitudes, concurso, soma, saldo):
    """
    Exibe tabela visual compacta no estilo do usuário:
    Linhas = Posições (N1-N15)
    Colunas = Números da amplitude
    Destaque nos menos prováveis
    """
    print("\n" + "=" * 100)
    print(f"📊 VISUALIZAÇÃO COMPACTA - NÚMEROS MENOS PROVÁVEIS")
    print(f"   Concurso {concurso} | Soma: {soma} | Tendência: {'↑ SUBIR' if saldo < 0 else '↓ DESCER' if saldo > 2 else '→ NEUTRO'}")
    print("=" * 100)
    
    # Para cada grupo de 5 posições (3 grupos: N1-N5, N6-N10, N11-N15)
    grupos = [(1, 5), (6, 10), (11, 15)]
    
    for inicio, fim in grupos:
        print(f"\n┌─────────────────────────────────────────────────────────────────────────────────┐")
        print(f"│ POSIÇÕES N{inicio:02d} a N{fim:02d}                                                             │")
        print(f"├─────────────────────────────────────────────────────────────────────────────────┤")
        
        # Encontrar amplitude máxima do grupo
        nums_range = set()
        for pos in range(inicio, fim + 1):
            p10, p90 = amplitudes[pos]
            for n in range(max(1, p10-1), min(26, p90+2)):
                nums_range.add(n)
        nums_sorted = sorted(nums_range)
        
        # Header com números
        header = "│ Pos  │"
        for n in nums_sorted:
            header += f" {n:2d} │"
        print(header)
        print("├──────┼" + "────┼" * len(nums_sorted))
        
        # Cada posição
        for pos in range(inicio, fim + 1):
            row = f"│ N{pos:02d}  │"
            top_nums = {t[0]: t[1] for t in top3[pos]}
            p10, p90 = amplitudes[pos]
            
            for n in nums_sorted:
                # Verificar se número está na amplitude desta posição
                if n < p10 - 1 or n > p90 + 1:
                    row += "  · │"  # Fora da amplitude
                elif n in top_nums:
                    score = top_nums[n]
                    if score >= 50:
                        row += f"{Fore.RED}{Back.WHITE} ✗ {Style.RESET_ALL}│"
                    elif score >= 30:
                        row += f"{Fore.YELLOW} ✗ {Style.RESET_ALL}│"
                    elif score >= 15:
                        row += f"{Fore.CYAN} ○ {Style.RESET_ALL}│"
                    else:
                        row += "  - │"
                else:
                    row += "    │"
            
            print(row)
        
        print(f"└──────┴" + "────┴" * len(nums_sorted))
    
    print("\n📋 SÍMBOLOS:")
    print(f"   {Fore.RED}✗{Style.RESET_ALL} = EVITAR (muito improvável)")
    print(f"   {Fore.YELLOW}✗{Style.RESET_ALL} = Cuidado (improvável)")  
    print(f"   {Fore.CYAN}○{Style.RESET_ALL} = Atenção (levemente improvável)")
    print(f"   · = Fora da amplitude usual")


def gerar_filtro_combinacoes(top3):
    """
    Gera função de filtro que pode ser usada para eliminar combinações
    onde números muito improváveis aparecem nas posições erradas.
    """
    def filtro(combo):
        """
        combo: tupla de 15 números ordenados
        Retorna True se a combinação é VÁLIDA (não tem números muito improváveis)
        """
        for pos in range(1, 16):
            num = combo[pos-1]
            top_nums = {t[0]: t[1] for t in top3[pos]}
            
            # Se o número está entre os muito improváveis (score >= 50), rejeitar
            if num in top_nums and top_nums[num] >= 50:
                return False
        
        return True
    
    return filtro


def main():
    """Função principal"""
    print("=" * 80)
    print("🔥 MAPA TÉRMICO POSICIONAL - NÚMEROS MENOS PROVÁVEIS")
    print("=" * 80)
    
    # Carregar dados
    print("\n⏳ Carregando dados...")
    resultados = carregar_resultados(30)
    amplitudes = obter_amplitude_posicao()
    
    # Calcular scores
    print("⏳ Calculando indicadores...")
    scores, concurso, soma, saldo = calcular_score_improbabilidade(resultados, amplitudes)
    
    # Obter top 3 menos prováveis
    top3 = obter_top3_menos_provaveis(scores, amplitudes)
    
    # Exibir mapa térmico
    exibir_mapa_termico(top3, concurso, soma, saldo)
    
    # Exibir visualização compacta
    exibir_tabela_visual_compacta(top3, amplitudes, concurso, soma, saldo)
    
    # Exportar para uso no filtro
    print("\n" + "=" * 80)
    print("📤 EXPORTAÇÃO PARA FILTROS")
    print("=" * 80)
    
    print("\n📋 Lista de números a EVITAR por posição (score ≥ 30):")
    evitar = {}
    for pos in range(1, 16):
        nums_evitar = [t[0] for t in top3[pos] if t[1] >= 30]
        if nums_evitar:
            evitar[pos] = nums_evitar
            print(f"   N{pos:02d}: {nums_evitar}")
    
    # Salvar em arquivo
    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    dados_path = os.path.join(base_path, "dados", "mapa_termico_atual.txt")
    
    with open(dados_path, "w", encoding="utf-8") as f:
        f.write(f"# Mapa Térmico - Concurso {concurso}\n")
        f.write(f"# Soma: {soma} | Saldo: {saldo:+.1f}\n")
        f.write(f"# Números a EVITAR por posição (score >= 30)\n\n")
        for pos, nums in evitar.items():
            f.write(f"N{pos:02d}: {nums}\n")
    
    print(f"\n✅ Salvo em: dados/mapa_termico_atual.txt")
    
    return top3, evitar


if __name__ == "__main__":
    top3, evitar = main()
    print("\n✅ Mapa térmico gerado com sucesso!")
