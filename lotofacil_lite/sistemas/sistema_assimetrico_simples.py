"""
Sistema Assimétrico Simplificado - LotoScope
Versão otimizada com foco na estratégia de duplo filtro
"""

import random
from collections import Counter
from datetime import datetime
import json
import os

class GeradorSimples:
    """Gerador simplificado para testes rápidos"""
    
    def __init__(self):
        self.numeros = list(range(1, 26))
        
    def gerar_combinacao(self):
        """Gera combinação aleatória ponderada"""
        # Pesos baseados em frequências típicas da Lotofácil
        pesos = {
            1: 0.85, 2: 0.90, 3: 0.88, 4: 0.92, 5: 0.87,
            6: 0.89, 7: 0.91, 8: 0.86, 9: 0.93, 10: 0.88,
            11: 0.90, 12: 0.87, 13: 0.94, 14: 0.89, 15: 0.85,
            16: 0.91, 17: 0.88, 18: 0.86, 19: 0.92, 20: 0.90,
            21: 0.87, 22: 0.89, 23: 0.85, 24: 0.91, 25: 0.88
        }
        
        combinacao = []
        numeros_disponiveis = self.numeros.copy()
        
        for _ in range(15):
            # Aplica pesos na seleção
            pesos_atuais = [pesos[n] for n in numeros_disponiveis]
            numero = random.choices(numeros_disponiveis, weights=pesos_atuais)[0]
            combinacao.append(numero)
            numeros_disponiveis.remove(numero)
            
        return sorted(combinacao)

class AvaliadorFaixaMediaSimples:
    """Avaliador simplificado para faixa 9-13"""
    
    def __init__(self):
        # Padrões baseados em análise estatística prévia
        self.padroes_otimos = {
            'distribuicao_ideal': [3, 3, 3, 3, 3],  # Distribuição equilibrada por região
            'pares_ideal': 7,  # 7 pares, 8 ímpares
            'soma_ideal': 195,  # Soma próxima da média histórica
            'consecutivos_ideal': 4  # Números consecutivos moderados
        }
        
    def avaliar_combinacao(self, combinacao):
        """Avalia probabilidade para faixa 9-13"""
        score = 0
        
        # 1. Distribuição por regiões (25 pontos)
        regioes = [0] * 5
        for num in combinacao:
            regiao = (num - 1) // 5
            regioes[regiao] += 1
            
        # Penaliza desequilíbrios extremos
        desvio_distribuicao = sum(abs(r - 3) for r in regioes)
        score_distribuicao = max(0, 25 - desvio_distribuicao * 3)
        score += score_distribuicao
        
        # 2. Paridade (20 pontos)
        pares = sum(1 for n in combinacao if n % 2 == 0)
        desvio_paridade = abs(pares - self.padroes_otimos['pares_ideal'])
        score_paridade = max(0, 20 - desvio_paridade * 3)
        score += score_paridade
        
        # 3. Soma total (25 pontos)
        soma = sum(combinacao)
        desvio_soma = abs(soma - self.padroes_otimos['soma_ideal']) / 20
        score_soma = max(0, 25 - desvio_soma)
        score += score_soma
        
        # 4. Números consecutivos (15 pontos)
        consecutivos = self.contar_consecutivos(combinacao)
        desvio_consecutivos = abs(consecutivos - self.padroes_otimos['consecutivos_ideal'])
        score_consecutivos = max(0, 15 - desvio_consecutivos * 2)
        score += score_consecutivos
        
        # 5. Bonus faixa específica (15 pontos)
        # Combinações com características que favorecem 9-13 acertos
        bonus = 0
        
        # Evita extremos que tendem a 14-15 acertos
        if 4 <= consecutivos <= 6:
            bonus += 5
        if 6 <= pares <= 9:
            bonus += 5
        if 180 <= soma <= 210:
            bonus += 5
            
        score += bonus
        
        return min(100, score)
    
    def contar_consecutivos(self, combinacao):
        """Conta números consecutivos"""
        sorted_comb = sorted(combinacao)
        consecutivos = 0
        sequencia = 1
        
        for i in range(1, len(sorted_comb)):
            if sorted_comb[i] == sorted_comb[i-1] + 1:
                sequencia += 1
            else:
                if sequencia >= 2:
                    consecutivos += sequencia
                sequencia = 1
                
        if sequencia >= 2:
            consecutivos += sequencia
            
        return consecutivos
    
    def filtrar_melhores(self, combinacoes, top_n=5):
        """Filtra as melhores para faixa 9-13"""
        combinacoes_com_score = []
        
        for combinacao in combinacoes:
            score = self.avaliar_combinacao(combinacao)
            combinacoes_com_score.append((combinacao, score))
        
        combinacoes_com_score.sort(key=lambda x: x[1], reverse=True)
        return combinacoes_com_score[:top_n]

class SistemaAssimetricoSimples:
    """Sistema simplificado de geração assimétrica"""
    
    def __init__(self):
        self.gerador = GeradorSimples()
        self.avaliador = AvaliadorFaixaMediaSimples()
        
    def gerar_otimizadas(self, quantidade_inicial=30, quantidade_final=5):
        """Processo completo: gera → avalia → filtra"""
        print(f"\n{'='*50}")
        print("SISTEMA ASSIMÉTRICO SIMPLIFICADO")
        print(f"{'='*50}")
        print(f"Objetivo: Otimizar para faixa 9-13 acertos")
        print(f"Processo: {quantidade_inicial} → filtro → {quantidade_final}")
        
        # Etapa 1: Geração inicial
        print(f"\n1. Gerando {quantidade_inicial} combinações...")
        combinacoes = []
        for i in range(quantidade_inicial):
            combinacao = self.gerador.gerar_combinacao()
            combinacoes.append(combinacao)
            if (i + 1) % 10 == 0:
                print(f"   Geradas: {i + 1}")
        
        # Etapa 2: Avaliação e filtro
        print(f"\n2. Aplicando filtro assimétrico...")
        melhores = self.avaliador.filtrar_melhores(combinacoes, quantidade_final)
        
        # Etapa 3: Relatório
        print(f"\n3. Resultado final:")
        print(f"   Top {len(melhores)} combinações para faixa 9-13:")
        
        for i, (combinacao, score) in enumerate(melhores, 1):
            pares = sum(1 for n in combinacao if n % 2 == 0)
            soma = sum(combinacao)
            
            print(f"\n   {i}. SCORE: {score:.1f}")
            print(f"      Números: {combinacao}")
            print(f"      Soma: {soma} | Pares: {pares}")
        
        # Análise comparativa
        scores = [score for _, score in melhores]
        print(f"\n4. Análise dos scores:")
        print(f"   Melhor: {max(scores):.1f}")
        print(f"   Pior: {min(scores):.1f}")
        print(f"   Médio: {sum(scores)/len(scores):.1f}")
        
        # Salva resultado
        resultado = {
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'configuracao': {
                'quantidade_inicial': quantidade_inicial,
                'quantidade_final': quantidade_final,
                'foco': 'faixa_9_13_acertos'
            },
            'combinacoes': [
                {
                    'posicao': i,
                    'combinacao': combinacao,
                    'score': score,
                    'soma': sum(combinacao),
                    'pares': sum(1 for n in combinacao if n % 2 == 0)
                }
                for i, (combinacao, score) in enumerate(melhores, 1)
            ]
        }
        
        arquivo = f"resultado_assimetrico_simples_{datetime.now().strftime('%H%M%S')}.json"
        with open(arquivo, 'w') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Resultado salvo em: {arquivo}")
        
        return melhores
    
    def teste_rapido(self):
        """Teste rápido com 10 combinações"""
        print("\n🔍 TESTE RÁPIDO - 10 combinações")
        return self.gerar_otimizadas(10, 3)

def main():
    """Execução principal"""
    sistema = SistemaAssimetricoSimples()
    
    print("Opções:")
    print("1. Teste rápido (10 → 3)")
    print("2. Geração normal (30 → 5)")
    print("3. Análise extensa (50 → 10)")
    
    try:
        opcao = input("\nEscolha (1-3): ").strip()
        
        if opcao == "1":
            resultado = sistema.teste_rapido()
        elif opcao == "2":
            resultado = sistema.gerar_otimizadas(30, 5)
        elif opcao == "3":
            resultado = sistema.gerar_otimizadas(50, 10)
        else:
            print("Executando teste rápido...")
            resultado = sistema.teste_rapido()
            
        print(f"\n✅ Sistema executado com sucesso!")
        print(f"   {len(resultado)} combinações otimizadas geradas")
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()
