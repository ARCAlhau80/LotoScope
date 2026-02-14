# -*- coding: utf-8 -*-
"""
ANÁLISE DE PERFORMANCE: Pool 23 Híbrido com Estratégia SUPERÁVIT v2.0
Resultado 3613: 1,3,4,7,9,10,11,12,15,16,18,20,21,22,23
Excluídos: [17, 25] - NENHUM no resultado! ✅
"""

import os

# Resultado do concurso 3613
RESULTADO_3613 = {1,3,4,7,9,10,11,12,15,16,18,20,21,22,23}

# Prêmios Lotofácil
PREMIOS = {
    11: 7.00,
    12: 14.00,
    13: 35.00,
    14: 1000.00,
    15: 1800000.00
}
CUSTO_APOSTA = 3.00

# Arquivos por nível
ARQUIVOS = [
    ("Nível 0 (Sem filtros)", "dados/pool23_excl17_25_nivel0_490314_20260214_135510.txt"),
    ("Nível 1 (Soma)", "dados/pool23_excl17_25_nivel1_310890_20260214_135519.txt"),
    ("Nível 2 (Básico)", "dados/pool23_excl17_25_nivel2_283645_20260214_135526.txt"),
    ("Nível 3 (Balanceado)", "dados/pool23_excl17_25_nivel3_276716_20260214_135535.txt"),
    ("Nível 4 (Moderado)", "dados/pool23_excl17_25_nivel4_172562_20260214_135544.txt"),
    ("Nível 5 (Agressivo)", "dados/pool23_excl17_25_nivel5_136990_20260214_135552.txt"),
    ("Nível 6 (Ultra)", "dados/pool23_excl17_25_nivel6_19059_20260214_135556.txt"),
]

def analisar_arquivo(caminho):
    """Analisa um arquivo de combinações"""
    if not os.path.exists(caminho):
        return None
    
    acertos = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
    total_combinacoes = 0
    
    with open(caminho, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue
            
            try:
                numeros = set(int(x) for x in linha.replace(',', ' ').split())
                if len(numeros) == 15:
                    total_combinacoes += 1
                    hits = len(numeros & RESULTADO_3613)
                    if hits >= 11:
                        acertos[hits] += 1
            except:
                continue
    
    return total_combinacoes, acertos

def main():
    print("=" * 90)
    print("📊 ANÁLISE DE PERFORMANCE - POOL 23 HÍBRIDO (ESTRATÉGIA SUPERÁVIT v2.0)")
    print("=" * 90)
    print()
    print(f"   🎯 Resultado 3613: {sorted(RESULTADO_3613)}")
    print(f"   🚫 Excluídos: [17, 25] → NENHUM saiu no resultado! ✅")
    print()
    print("-" * 90)
    
    resultados = []
    
    for nome, arquivo in ARQUIVOS:
        resultado = analisar_arquivo(arquivo)
        if resultado is None:
            print(f"   ⚠️ Arquivo não encontrado: {arquivo}")
            continue
        
        total, acertos = resultado
        
        # Calcular financeiro
        custo = total * CUSTO_APOSTA
        premio = sum(acertos[a] * PREMIOS[a] for a in acertos)
        lucro = premio - custo
        roi = (premio / custo * 100) if custo > 0 else 0
        
        resultados.append({
            'nome': nome,
            'arquivo': arquivo,
            'total': total,
            'acertos': acertos,
            'custo': custo,
            'premio': premio,
            'lucro': lucro,
            'roi': roi
        })
    
    # Exibir tabela de resultados
    print()
    print(f"{'Nível':<25} | {'Combinações':>12} | {'Custo':>14} | {'Prêmio':>14} | {'Lucro':>14} | {'ROI':>8}")
    print("-" * 90)
    
    for r in resultados:
        roi_icon = "🟢" if r['roi'] >= 100 else "🔴"
        print(f"{r['nome']:<25} | {r['total']:>12,} | R$ {r['custo']:>11,.2f} | R$ {r['premio']:>11,.2f} | R$ {r['lucro']:>11,.2f} | {roi_icon} {r['roi']:>5.1f}%")
    
    print("-" * 90)
    print()
    
    # Detalhamento por acertos
    print("=" * 90)
    print("📈 DETALHAMENTO DE ACERTOS POR NÍVEL")
    print("=" * 90)
    print()
    print(f"{'Nível':<25} | {'11 ac':>8} | {'12 ac':>8} | {'13 ac':>8} | {'14 ac':>8} | {'15 ac':>8}")
    print("-" * 90)
    
    for r in resultados:
        ac = r['acertos']
        jackpot = "🏆" if ac[15] > 0 else ""
        print(f"{r['nome']:<25} | {ac[11]:>8,} | {ac[12]:>8,} | {ac[13]:>8,} | {ac[14]:>8,} | {ac[15]:>8,} {jackpot}")
    
    print("-" * 90)
    print()
    
    # Análise de Jackpots
    print("=" * 90)
    print("🏆 ANÁLISE DE JACKPOTS (15 ACERTOS)")
    print("=" * 90)
    print()
    
    for r in resultados:
        if r['acertos'][15] > 0:
            print(f"   ✅ {r['nome']}: {r['acertos'][15]} JACKPOT(s)!")
            print(f"      Custo total: R$ {r['custo']:,.2f}")
            print(f"      Prêmio: R$ {r['premio']:,.2f}")
            print(f"      ROI: {r['roi']:.1f}%")
            print()
    
    # Resumo final
    print("=" * 90)
    print("📊 RESUMO FINAL")
    print("=" * 90)
    print()
    
    # Níveis com ROI >= 100%
    niveis_positivos = [r for r in resultados if r['roi'] >= 100]
    niveis_negativos = [r for r in resultados if r['roi'] < 100]
    
    print(f"   🟢 Níveis com ROI >= 100%: {len(niveis_positivos)}")
    for r in niveis_positivos:
        print(f"      • {r['nome']}: ROI {r['roi']:.1f}%")
    
    print()
    print(f"   🔴 Níveis com ROI < 100%: {len(niveis_negativos)}")
    for r in niveis_negativos:
        print(f"      • {r['nome']}: ROI {r['roi']:.1f}%")
    
    print()
    
    # Melhor nível
    if resultados:
        melhor = max(resultados, key=lambda x: x['roi'])
        print(f"   🏆 MELHOR NÍVEL: {melhor['nome']}")
        print(f"      ROI: {melhor['roi']:.1f}%")
        print(f"      Combinações: {melhor['total']:,}")
        print(f"      Lucro: R$ {melhor['lucro']:,.2f}")
    
    print()
    print("=" * 90)

if __name__ == "__main__":
    main()
