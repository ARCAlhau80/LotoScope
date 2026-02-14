# -*- coding: utf-8 -*-
"""
ANÁLISE DE ROI: Níveis 5-6 - Como maximizar retorno SEM depender de jackpot
Foco: Acertos 11-14 para recuperar investimento
"""

import os

# Resultado do concurso 3613
RESULTADO_3613 = {1,3,4,7,9,10,11,12,15,16,18,20,21,22,23}

# Prêmios e custos
PREMIOS = {11: 7.00, 12: 14.00, 13: 35.00, 14: 1000.00, 15: 1800000.00}
CUSTO_APOSTA = 3.00

# Arquivos
ARQUIVOS = {
    5: "dados/pool23_excl17_25_nivel5_136990_20260214_135552.txt",
    6: "dados/pool23_excl17_25_nivel6_19059_20260214_135556.txt",
}

def analisar_distribuicao_acertos(caminho):
    """Analisa distribuição detalhada de acertos"""
    if not os.path.exists(caminho):
        return None
    
    acertos_por_faixa = {11: [], 12: [], 13: [], 14: [], 15: []}
    total = 0
    
    with open(caminho, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue
            
            try:
                numeros = set(int(x) for x in linha.replace(',', ' ').split())
                if len(numeros) == 15:
                    total += 1
                    hits = len(numeros & RESULTADO_3613)
                    if hits >= 11:
                        acertos_por_faixa[hits].append(numeros)
            except:
                continue
    
    return total, acertos_por_faixa

def calcular_roi_detalhado(total, acertos):
    """Calcula ROI detalhado por faixa de acerto"""
    custo_total = total * CUSTO_APOSTA
    
    detalhes = {}
    premio_total = 0
    
    for faixa in [11, 12, 13, 14, 15]:
        qtd = len(acertos[faixa])
        premio = qtd * PREMIOS[faixa]
        premio_total += premio
        
        # Contribuição para o ROI
        contribuicao = (premio / custo_total * 100) if custo_total > 0 else 0
        
        detalhes[faixa] = {
            'quantidade': qtd,
            'premio': premio,
            'contribuicao_roi': contribuicao,
            'pct_combinacoes': (qtd / total * 100) if total > 0 else 0
        }
    
    roi_total = (premio_total / custo_total * 100) if custo_total > 0 else 0
    lucro = premio_total - custo_total
    
    return {
        'custo': custo_total,
        'premio_total': premio_total,
        'lucro': lucro,
        'roi': roi_total,
        'detalhes': detalhes
    }

def analisar_caracteristicas_acertos(acertos_lista, faixa):
    """Analisa características das combinações com X acertos"""
    if not acertos_lista:
        return None
    
    somas = []
    pares_list = []
    primos_list = []
    nucleos = []
    
    PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    
    for combo in acertos_lista:
        somas.append(sum(combo))
        pares_list.append(len([n for n in combo if n % 2 == 0]))
        primos_list.append(len([n for n in combo if n in PRIMOS]))
        nucleos.append(len([n for n in combo if 6 <= n <= 20]))
    
    return {
        'soma_media': sum(somas) / len(somas),
        'soma_min': min(somas),
        'soma_max': max(somas),
        'pares_media': sum(pares_list) / len(pares_list),
        'primos_media': sum(primos_list) / len(primos_list),
        'nucleo_media': sum(nucleos) / len(nucleos),
    }

def main():
    print("=" * 90)
    print("📊 ANÁLISE DE ROI: NÍVEIS 5-6 - MAXIMIZAR RETORNO SEM JACKPOT")
    print("=" * 90)
    print()
    
    # Características do resultado vencedor
    PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    soma_jackpot = sum(RESULTADO_3613)
    pares_jackpot = len([n for n in RESULTADO_3613 if n % 2 == 0])
    primos_jackpot = len([n for n in RESULTADO_3613 if n in PRIMOS])
    nucleo_jackpot = len([n for n in RESULTADO_3613 if 6 <= n <= 20])
    
    print(f"🎯 JACKPOT 3613: Soma={soma_jackpot} | Pares={pares_jackpot} | Primos={primos_jackpot} | Núcleo={nucleo_jackpot}")
    print()
    
    for nivel, arquivo in ARQUIVOS.items():
        print("=" * 90)
        print(f"📋 NÍVEL {nivel}")
        print("=" * 90)
        
        resultado = analisar_distribuicao_acertos(arquivo)
        if resultado is None:
            print(f"   ⚠️ Arquivo não encontrado: {arquivo}")
            continue
        
        total, acertos = resultado
        roi_data = calcular_roi_detalhado(total, acertos)
        
        print(f"\n   📦 Total combinações: {total:,}")
        print(f"   💰 Custo: R$ {roi_data['custo']:,.2f}")
        print(f"   🏆 Prêmio: R$ {roi_data['premio_total']:,.2f}")
        print(f"   📈 ROI: {roi_data['roi']:.1f}%")
        print(f"   {'💚 Lucro' if roi_data['lucro'] >= 0 else '❌ Prejuízo'}: R$ {roi_data['lucro']:,.2f}")
        
        print(f"\n   📊 DISTRIBUIÇÃO DE ACERTOS:")
        print(f"   {'Acertos':<10} | {'Qtd':>10} | {'Prêmio':>14} | {'Contrib. ROI':>12} | {'% Combos':>10}")
        print("   " + "-" * 65)
        
        for faixa in [11, 12, 13, 14, 15]:
            d = roi_data['detalhes'][faixa]
            icon = "🏆" if faixa == 15 and d['quantidade'] > 0 else ""
            print(f"   {faixa:<10} | {d['quantidade']:>10,} | R$ {d['premio']:>11,.2f} | {d['contribuicao_roi']:>10.1f}% | {d['pct_combinacoes']:>9.2f}%{icon}")
        
        # Analisar características das combinações com mais acertos
        print(f"\n   📈 CARACTERÍSTICAS DAS COMBINAÇÕES COM MAIS ACERTOS:")
        
        for faixa in [14, 13, 12]:
            if len(acertos[faixa]) > 0:
                caract = analisar_caracteristicas_acertos(acertos[faixa], faixa)
                print(f"\n   {faixa} ACERTOS ({len(acertos[faixa])} combos):")
                print(f"      Soma: {caract['soma_min']:.0f} - {caract['soma_max']:.0f} (média: {caract['soma_media']:.1f})")
                print(f"      Pares: média {caract['pares_media']:.1f}")
                print(f"      Primos: média {caract['primos_media']:.1f}")
                print(f"      Núcleo: média {caract['nucleo_media']:.1f}")
        
        print()
    
    # Calcular quanto seria necessário para ROI = 100%
    print("=" * 90)
    print("💡 ANÁLISE: O QUE FALTOU PARA ROI = 100%?")
    print("=" * 90)
    print()
    
    for nivel, arquivo in ARQUIVOS.items():
        resultado = analisar_distribuicao_acertos(arquivo)
        if resultado is None:
            continue
        
        total, acertos = resultado
        roi_data = calcular_roi_detalhado(total, acertos)
        
        deficit = roi_data['custo'] - roi_data['premio_total']
        
        if deficit > 0:
            print(f"   NÍVEL {nivel}:")
            print(f"      Déficit: R$ {deficit:,.2f}")
            
            # Quantos prêmios de 14 seriam necessários
            premios_14_necessarios = deficit / PREMIOS[14]
            print(f"      → Faltaram {premios_14_necessarios:.1f} prêmios de 14 acertos")
            
            # Ou quantos de 13
            premios_13_necessarios = deficit / PREMIOS[13]
            print(f"      → Ou {premios_13_necessarios:.1f} prêmios de 13 acertos")
            
            # Taxa de acerto 14 atual
            taxa_14 = len(acertos[14]) / total * 100 if total > 0 else 0
            print(f"      Taxa atual de 14 acertos: {taxa_14:.4f}%")
            
            # Quantas combinações seriam necessárias para break-even (sem jackpot)
            if len(acertos[14]) > 0:
                premio_medio_por_combo = roi_data['premio_total'] / total
                combos_para_breakeven = roi_data['custo'] / premio_medio_por_combo if premio_medio_por_combo > 0 else float('inf')
                print(f"      Com prêmio médio atual: precisaria de {combos_para_breakeven:,.0f} combos para break-even")
            print()
    
    # Propostas de melhoria
    print("=" * 90)
    print("🔧 PROPOSTAS DE MELHORIA PARA NÍVEIS 5-6")
    print("=" * 90)
    print()
    
    print("   PROPOSTA 1: FILTRO DE SOMA ADAPTATIVO")
    print("   " + "─" * 60)
    print("   Problema: Soma 192 do jackpot ficou FORA do range 195-215")
    print("   Solução: Usar range baseado em PERCENTIL histórico, não fixo")
    print("   → Range dinâmico: Soma entre P20 e P80 dos últimos 50 concursos")
    print()
    
    print("   PROPOSTA 2: FILTRO 'N de M' (FLEXÍVEL)")
    print("   " + "─" * 60)
    print("   Problema: Todos os filtros precisam passar (AND)")
    print("   Solução: Passar se atender 4 de 6 critérios (75%)")
    print("   → Mantém combinações 'quase perfeitas' que têm bom potencial")
    print()
    
    print("   PROPOSTA 3: FOCO EM 14 ACERTOS (ROI POSITIVO)")
    print("   " + "─" * 60)
    print("   Problema: Sem jackpot, ROI fica negativo")
    print("   Solução: Otimizar filtros para MAXIMIZAR taxa de 14 acertos")
    print("   → Analisar quais características têm mais 14 acertos no histórico")
    print("   → Ajustar filtros para favorecer essas características")
    print()
    
    print("   PROPOSTA 4: SCORING EM VEZ DE ELIMINAÇÃO")
    print("   " + "─" * 60)
    print("   Problema: Filtros binários eliminam bons candidatos")
    print("   Solução: Dar pontuação e manter TOP X combinações")
    print("   → Cada filtro contribui com +/- pontos")
    print("   → Manter combinações com score acima do threshold")
    print("   → Mais flexível e mantém diversidade")
    print()
    
    # Recomendação final
    print("=" * 90)
    print("🎯 RECOMENDAÇÃO FINAL")
    print("=" * 90)
    print()
    print("   Para NÍVEIS 5-6, a melhor estratégia é:")
    print()
    print("   1. ACEITAR que jackpot é improvável nesses níveis")
    print("   2. FOCAR em maximizar acertos de 14 (R$ 1.000)")
    print("   3. AJUSTAR filtros para favorecer combinações com")
    print("      características próximas às que têm mais 14 acertos")
    print()
    print("   ⚠️  Se o objetivo é JACKPOT, usar níveis 2-4!")
    print("   ⚠️  Níveis 5-6 são para CONSISTÊNCIA, não jackpot!")
    print()

if __name__ == "__main__":
    main()
