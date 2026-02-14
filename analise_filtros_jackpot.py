# -*- coding: utf-8 -*-
"""
ANÁLISE DETALHADA: Por que os níveis 5 e 6 perderam o jackpot?
Identifica exatamente quais filtros eliminaram a combinação vencedora
"""

import os

# Resultado do concurso 3613 (a combinação vencedora)
RESULTADO_3613 = [1,3,4,7,9,10,11,12,15,16,18,20,21,22,23]
RESULTADO_SET = set(RESULTADO_3613)

# Pool 23 (excluídos 17 e 25)
POOL_23 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,18,19,20,21,22,23,24]

# Primos de 1-25
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

def analisar_combinacao(combo):
    """Analisa uma combinação e retorna suas características"""
    combo_set = set(combo)
    
    # Soma
    soma = sum(combo)
    
    # Pares/Ímpares
    pares = len([n for n in combo if n % 2 == 0])
    impares = 15 - pares
    
    # Primos
    primos = len([n for n in combo if n in PRIMOS])
    
    # Sequências consecutivas (maior sequência)
    combo_sorted = sorted(combo)
    max_seq = 1
    seq_atual = 1
    for i in range(1, len(combo_sorted)):
        if combo_sorted[i] == combo_sorted[i-1] + 1:
            seq_atual += 1
            max_seq = max(max_seq, seq_atual)
        else:
            seq_atual = 1
    
    # Repetidos (usando último resultado como referência - simplificado)
    # Para análise real precisaria do resultado anterior
    
    # Núcleo (6-20)
    nucleo = len([n for n in combo if 6 <= n <= 20])
    
    # Favorecidos (números mais frequentes - simplificado)
    # Para análise real precisaria do histórico
    
    return {
        'soma': soma,
        'pares': pares,
        'impares': impares,
        'primos': primos,
        'max_seq': max_seq,
        'nucleo': nucleo
    }

def verificar_filtros(caracteristicas, filtros):
    """Verifica quais filtros a combinação passaria/falharia"""
    resultado = {}
    
    # Soma
    if 'soma_min' in filtros or 'soma_max' in filtros:
        soma_min = filtros.get('soma_min', 0)
        soma_max = filtros.get('soma_max', 400)
        passou = soma_min <= caracteristicas['soma'] <= soma_max
        resultado['SOMA'] = {
            'passou': passou,
            'valor': caracteristicas['soma'],
            'range': f"{soma_min}-{soma_max}",
            'motivo': f"Soma {caracteristicas['soma']} {'dentro' if passou else 'fora'} de {soma_min}-{soma_max}"
        }
    
    # Pares
    if 'pares_min' in filtros or 'pares_max' in filtros:
        pares_min = filtros.get('pares_min', 0)
        pares_max = filtros.get('pares_max', 15)
        passou = pares_min <= caracteristicas['pares'] <= pares_max
        resultado['PARES'] = {
            'passou': passou,
            'valor': caracteristicas['pares'],
            'range': f"{pares_min}-{pares_max}",
            'motivo': f"Pares {caracteristicas['pares']} {'dentro' if passou else 'fora'} de {pares_min}-{pares_max}"
        }
    
    # Primos
    if 'primos_min' in filtros or 'primos_max' in filtros:
        primos_min = filtros.get('primos_min', 0)
        primos_max = filtros.get('primos_max', 15)
        passou = primos_min <= caracteristicas['primos'] <= primos_max
        resultado['PRIMOS'] = {
            'passou': passou,
            'valor': caracteristicas['primos'],
            'range': f"{primos_min}-{primos_max}",
            'motivo': f"Primos {caracteristicas['primos']} {'dentro' if passou else 'fora'} de {primos_min}-{primos_max}"
        }
    
    # Sequência máxima
    if 'seq_max' in filtros:
        seq_max = filtros['seq_max']
        passou = caracteristicas['max_seq'] <= seq_max
        resultado['SEQ'] = {
            'passou': passou,
            'valor': caracteristicas['max_seq'],
            'range': f"≤{seq_max}",
            'motivo': f"Seq máx {caracteristicas['max_seq']} {'≤' if passou else '>'} {seq_max}"
        }
    
    # Núcleo mínimo
    if 'nucleo_min' in filtros:
        nucleo_min = filtros['nucleo_min']
        passou = caracteristicas['nucleo'] >= nucleo_min
        resultado['NUCLEO'] = {
            'passou': passou,
            'valor': caracteristicas['nucleo'],
            'range': f"≥{nucleo_min}",
            'motivo': f"Núcleo {caracteristicas['nucleo']} {'≥' if passou else '<'} {nucleo_min}"
        }
    
    return resultado

def main():
    print("=" * 90)
    print("🔍 ANÁLISE DETALHADA: POR QUE NÍVEIS 5 E 6 PERDERAM O JACKPOT?")
    print("=" * 90)
    print()
    
    # Analisar a combinação vencedora
    caract = analisar_combinacao(RESULTADO_3613)
    
    print("📊 CARACTERÍSTICAS DA COMBINAÇÃO VENCEDORA (3613):")
    print(f"   Números: {RESULTADO_3613}")
    print()
    print(f"   • Soma: {caract['soma']}")
    print(f"   • Pares: {caract['pares']} | Ímpares: {caract['impares']}")
    print(f"   • Primos: {caract['primos']}")
    print(f"   • Sequência máxima: {caract['max_seq']}")
    print(f"   • Núcleo (6-20): {caract['nucleo']}")
    print()
    
    # Definir filtros de cada nível (baseado no código)
    FILTROS = {
        4: {
            'soma_min': 190, 'soma_max': 220,
            'pares_min': 6, 'pares_max': 9,
            'primos_min': 4, 'primos_max': 7,
            'seq_max': 6,
        },
        5: {
            'soma_min': 195, 'soma_max': 215,
            'pares_min': 6, 'pares_max': 9,
            'primos_min': 4, 'primos_max': 7,
            'seq_max': 5,
            'nucleo_min': 9,
        },
        6: {
            'soma_min': 200, 'soma_max': 210,
            'pares_min': 7, 'pares_max': 8,
            'primos_min': 5, 'primos_max': 6,
            'seq_max': 4,
            'nucleo_min': 10,
        },
    }
    
    print("=" * 90)
    print("🔎 ANÁLISE POR NÍVEL")
    print("=" * 90)
    
    for nivel in [4, 5, 6]:
        print(f"\n{'─'*90}")
        print(f"📋 NÍVEL {nivel}:")
        print(f"{'─'*90}")
        
        filtros = FILTROS[nivel]
        resultado = verificar_filtros(caract, filtros)
        
        passou_todos = True
        filtros_falhos = []
        
        for filtro, dados in resultado.items():
            status = "✅" if dados['passou'] else "❌"
            print(f"   {status} {filtro}: {dados['motivo']}")
            
            if not dados['passou']:
                passou_todos = False
                filtros_falhos.append(filtro)
        
        if passou_todos:
            print(f"\n   🏆 NÍVEL {nivel}: PASSOU EM TODOS OS FILTROS!")
        else:
            print(f"\n   ❌ NÍVEL {nivel}: FALHOU EM: {', '.join(filtros_falhos)}")
    
    # Propor melhorias
    print()
    print("=" * 90)
    print("💡 PROPOSTAS DE MELHORIA (sem aumentar combinações)")
    print("=" * 90)
    
    print()
    print("🔧 NÍVEL 5 - FILTROS ATUAIS vs PROPOSTOS:")
    print("─" * 60)
    print(f"   SOMA: 195-215 (jackpot tem {caract['soma']})")
    
    if caract['soma'] < 195 or caract['soma'] > 215:
        novo_min = min(195, caract['soma'] - 5)
        novo_max = max(215, caract['soma'] + 5)
        print(f"   → PROPOSTA: {novo_min}-{novo_max}")
    else:
        print(f"   → OK (mantém)")
    
    if caract['primos'] < 4 or caract['primos'] > 7:
        print(f"   PRIMOS: 4-7 (jackpot tem {caract['primos']})")
        novo_min = min(4, caract['primos'])
        novo_max = max(7, caract['primos'])
        print(f"   → PROPOSTA: {novo_min}-{novo_max}")
    else:
        print(f"   PRIMOS: 4-7 (jackpot tem {caract['primos']}) → OK")
    
    if caract['max_seq'] > 5:
        print(f"   SEQ MAX: 5 (jackpot tem {caract['max_seq']})")
        print(f"   → PROPOSTA: {caract['max_seq']}")
    else:
        print(f"   SEQ MAX: 5 (jackpot tem {caract['max_seq']}) → OK")
    
    print()
    print("🔧 NÍVEL 6 - FILTROS ATUAIS vs PROPOSTOS:")
    print("─" * 60)
    print(f"   SOMA: 200-210 (jackpot tem {caract['soma']})")
    
    if caract['soma'] < 200 or caract['soma'] > 210:
        print(f"   → ⚠️ Jackpot FORA do range! Ampliar ou usar estratégia diferente")
    
    print(f"   PARES: 7-8 (jackpot tem {caract['pares']})")
    if caract['pares'] < 7 or caract['pares'] > 8:
        print(f"   → ⚠️ Jackpot FORA do range!")
    
    print(f"   PRIMOS: 5-6 (jackpot tem {caract['primos']})")
    if caract['primos'] < 5 or caract['primos'] > 6:
        print(f"   → ⚠️ Jackpot FORA do range!")
    
    print(f"   SEQ MAX: 4 (jackpot tem {caract['max_seq']})")
    if caract['max_seq'] > 4:
        print(f"   → ⚠️ Jackpot FORA do range!")
    
    print(f"   NÚCLEO MIN: 10 (jackpot tem {caract['nucleo']})")
    if caract['nucleo'] < 10:
        print(f"   → ⚠️ Jackpot FORA do range!")
    
    print()
    print("=" * 90)
    print("📈 ESTRATÉGIA ALTERNATIVA PARA NÍVEIS 5-6")
    print("=" * 90)
    print()
    print("   PROBLEMA: Filtros muito rígidos eliminam jackpots")
    print()
    print("   SOLUÇÃO 1: FILTROS POR 'ZONA DE CONFIANÇA' (não binário)")
    print("   ─────────────────────────────────────────────────────")
    print("   Em vez de eliminar, dar SCORE baseado em proximidade:")
    print("   • Dentro do ideal: +2 pontos")
    print("   • Margem 1: +1 ponto")
    print("   • Margem 2: 0 pontos")
    print("   • Fora: -1 ponto")
    print("   → Manter apenas combinações com score total ≥ X")
    print()
    print("   SOLUÇÃO 2: FILTROS 'OR' EM VEZ DE 'AND'")
    print("   ─────────────────────────────────────────────────────")
    print("   Passar se atender N de M critérios (ex: 4 de 6)")
    print("   → Mais flexível, mantém mais jackpots potenciais")
    print()
    print("   SOLUÇÃO 3: PRIORIZAR ROI COM ACERTOS MENORES")
    print("   ─────────────────────────────────────────────────────")
    print("   Níveis 5-6 focam em CONSISTÊNCIA (11-14 acertos)")
    print("   Não esperar jackpot, mas maximizar retorno pequeno")
    print()

if __name__ == "__main__":
    main()
