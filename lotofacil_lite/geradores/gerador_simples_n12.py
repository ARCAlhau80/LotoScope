#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR SIMPLES COM INTELIGÊNCIA N12
Sistema simples para gerar combinações para o próximo concurso
baseado no último resultado da base de dados

Baseado em:
• Último concurso da base
• Teoria de oscilação contrária
• N12 como indicador de distribuição
• Zero hardcoded - tudo dinâmico

Autor: AR CALHAU
Data: 19/09/2025
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'sistemas'))

from sistema_inteligencia_n12 import SistemaInteligenciaDistribuicaoN12
import random
from datetime import datetime

def gerar_combinacao_aleatoria():
    """Gera uma combinação aleatória de 15 números"""
    return sorted(random.sample(range(1, 26), 15))

def calcular_distribuicao(combinacao):
    """Calcula a distribuição de uma combinação"""
    baixos = len([n for n in combinacao if 1 <= n <= 8])
    medios = len([n for n in combinacao if 9 <= n <= 17])
    altos = len([n for n in combinacao if 18 <= n <= 25])
    
    if baixos > medios and baixos > altos:
        return "BAIXA", baixos, medios, altos
    elif medios > baixos and medios > altos:
        return "MEDIA", baixos, medios, altos
    elif altos > baixos and altos > medios:
        return "ALTA", baixos, medios, altos
    else:
        return "EQUILIBRADA", baixos, medios, altos

def gerar_combinacoes_inteligentes_n12(quantidade=30):
    """Gera combinações inteligentes baseadas na estratégia N12"""
    print("🎯 GERADOR SIMPLES COM INTELIGÊNCIA N12")
    print("=" * 60)
    
    # Inicializar sistema N12
    sistema = SistemaInteligenciaDistribuicaoN12()
    
    if not sistema.analisar_situacao_atual():
        print("❌ Erro ao analisar situação atual")
        return []
    
    # Fazer previsão
    previsao = sistema.prever_proxima_distribuicao()
    
    print(f"\n🎲 GERANDO {quantidade} COMBINAÇÕES INTELIGENTES...")
    print("-" * 50)
    
    combinacoes_geradas = []
    tentativas = 0
    max_tentativas = quantidade * 100  # Evitar loop infinito
    
    while len(combinacoes_geradas) < quantidade and tentativas < max_tentativas:
        tentativas += 1
        
        # Gerar combinação aleatória
        combinacao = gerar_combinacao_aleatoria()
        n12 = combinacao[11]  # N12 é a posição 12 (índice 11)
        
        distribuicao, baixos, medios, altos = calcular_distribuicao(combinacao)
        
        # Aplicar critérios da estratégia
        score = 0
        
        if sistema.predicao_proxima:
            estrategia = sistema.predicao_proxima['estrategia']
            
            if estrategia == 'PRIVILEGIAR_BAIXOS_MEDIOS':
                # Priorizar baixos e médios
                if distribuicao in ['BAIXA', 'MEDIA']:
                    score += 3
                if n12 <= sistema.limites_n12['limite_baixo']:
                    score += 2
                    
            elif estrategia == 'PRIVILEGIAR_MEDIOS_ALTOS':
                # Priorizar médios e altos
                if distribuicao in ['MEDIA', 'ALTA']:
                    score += 3
                if n12 >= sistema.limites_n12['limite_equilibrio']:
                    score += 2
                    
            elif estrategia == 'PRIVILEGIAR_EXTREMOS':
                # Priorizar baixos e altos
                if distribuicao in ['BAIXA', 'ALTA']:
                    score += 3
                if n12 <= sistema.limites_n12['limite_baixo'] or n12 >= sistema.limites_n12['limite_alto']:
                    score += 2
            else:
                # Outras estratégias - aceitar qualquer
                score += 1
        
        # Aceitar combinações com score positivo
        if score > 0:
            combinacao_info = {
                'numeros': combinacao,
                'n12': n12,
                'distribuicao': distribuicao,
                'baixos': baixos,
                'medios': medios,
                'altos': altos,
                'score': score
            }
            
            # Evitar duplicatas
            if combinacao not in [c['numeros'] for c in combinacoes_geradas]:
                combinacoes_geradas.append(combinacao_info)
    
    # Ordenar por score (melhores primeiro)
    combinacoes_geradas.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"✅ {len(combinacoes_geradas)} combinações geradas em {tentativas} tentativas")
    
    return combinacoes_geradas

def salvar_combinacoes(combinacoes, sistema):
    """Salva as combinações em arquivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"apostas_n12_proximo_concurso_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("🎯 APOSTAS INTELIGENTES N12 - PRÓXIMO CONCURSO\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"📊 SITUAÇÃO ATUAL:\n")
        f.write(f"   🎯 Último concurso: {sistema.ultimo_concurso}\n")
        f.write(f"   📍 N12 atual: {sistema.ultimo_n12}\n")
        f.write(f"   📊 Distribuição atual: {sistema.distribuicao_atual}\n\n")
        
        if sistema.predicao_proxima:
            f.write(f"🔮 PREVISÃO PRÓXIMO CONCURSO:\n")
            f.write(f"   🔧 Estratégia: {sistema.predicao_proxima['estrategia']}\n")
            for i, opcao in enumerate(sistema.predicao_proxima['opcoes']):
                prob = sistema.predicao_proxima['probabilidades'][i]
                if prob > 0:
                    f.write(f"   • {opcao}: {prob}% de probabilidade\n")
            f.write("\n")
        
        f.write(f"🎲 COMBINAÇÕES GERADAS ({len(combinacoes)}):\n")
        f.write("-" * 50 + "\n")
        
        for i, comb in enumerate(combinacoes, 1):
            numeros_str = ','.join([f"{n:02d}" for n in comb['numeros']])
            f.write(f"{i:2d}: {numeros_str} ")
            f.write(f"| N12={comb['n12']:2d} | {comb['distribuicao']:<4} ")
            f.write(f"| {comb['baixos']}-{comb['medios']}-{comb['altos']} ")
            f.write(f"| Score={comb['score']}\n")
        
        f.write(f"\n📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("🧠 Baseado na teoria de oscilação contrária N12\n\n")
        
        # SEÇÃO FINAL: APENAS AS COMBINAÇÕES LIMPAS
        f.write("COMBINAÇÕES PARA APOSTAS:\n")
        f.write("-" * 30 + "\n")
        for comb in combinacoes:
            numeros_str = ','.join([f"{n:02d}" for n in comb['numeros']])
            f.write(f"{numeros_str}\n")
    
    return filename

def main():
    """Função principal"""
    try:
        print("🚀 INICIANDO GERADOR SIMPLES N12...")
        
        # Gerar combinações
        combinacoes = gerar_combinacoes_inteligentes_n12(30)
        
        if not combinacoes:
            print("❌ Nenhuma combinação gerada!")
            return
        
        # Mostrar primeiras 10
        print(f"\n📊 PRIMEIRAS 10 COMBINAÇÕES:")
        print("-" * 70)
        for i, comb in enumerate(combinacoes[:10], 1):
            numeros_str = ','.join([f"{n:02d}" for n in comb['numeros']])
            print(f"{i:2d}: {numeros_str} | N12={comb['n12']:2d} | {comb['distribuicao']:<4} | {comb['baixos']}-{comb['medios']}-{comb['altos']} | Score={comb['score']}")
        
        # Salvar em arquivo
        sistema = SistemaInteligenciaDistribuicaoN12()
        sistema.analisar_situacao_atual()
        
        filename = salvar_combinacoes(combinacoes, sistema)
        
        print(f"\n💾 ARQUIVO SALVO: {filename}")
        print(f"✅ {len(combinacoes)} combinações prontas para o próximo concurso!")
        
        # Estatísticas
        distribuicoes = {}
        for comb in combinacoes:
            dist = comb['distribuicao']
            distribuicoes[dist] = distribuicoes.get(dist, 0) + 1
        
        print(f"\n📊 ESTATÍSTICAS:")
        for dist, count in distribuicoes.items():
            perc = (count / len(combinacoes)) * 100
            print(f"   {dist}: {count} ({perc:.1f}%)")
        
        n12_medio = sum(comb['n12'] for comb in combinacoes) / len(combinacoes)
        print(f"   N12 médio: {n12_medio:.1f}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()