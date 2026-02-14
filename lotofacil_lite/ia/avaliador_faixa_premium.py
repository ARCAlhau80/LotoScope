"""
Avaliador Faixa Premium 11-13 - Estratégia Assimétrica Refinada
===============================================================
Foco na faixa de maior valor/probabilidade: 11-13 acertos
"""

import json
import random
from collections import Counter
from datetime import datetime

class AvaliadorFaixaPremium:
    def __init__(self):
        print("🎯 INICIALIZANDO AVALIADOR FAIXA PREMIUM (11-13)")
        print("Foco estratégico: Máximo valor com probabilidade realista")
        
        self.historico_acertos = self.carregar_historico_acertos()
        self.padroes_faixa_premium = self.extrair_padroes_faixa_premium()
        self.pesos_caracteristicas = self.calcular_pesos_caracteristicas()
        self.faixa_alvo = (11, 13)  # NOVA FAIXA: 11-13
        
    def carregar_historico_acertos(self):
        """Carrega dados históricos focando na faixa 11-13"""
        try:
            with open('resultados_teste_historico.json', 'r') as f:
                dados = json.load(f)
                
            # Filtra apenas resultados na faixa 11-13 (mais restritiva)
            acertos_faixa_premium = {}
            for concurso, resultado in dados.items():
                if isinstance(resultado, dict) and 'acertos' in resultado:
                    acertos = resultado['acertos']
                    if 11 <= acertos <= 13:  # FAIXA PREMIUM
                        acertos_faixa_premium[concurso] = resultado
                        
            print(f"✓ Carregados {len(acertos_faixa_premium)} resultados na faixa PREMIUM 11-13")
            return acertos_faixa_premium
            
        except FileNotFoundError:
            print("⚠️ Arquivo histórico não encontrado. Usando padrões premium.")
            return {}
    
    def extrair_padroes_faixa_premium(self):
        """Extrai padrões específicos da faixa 11-13 (mais refinados)"""
        padroes = {
            'distribuicao_regioes': Counter(),
            'sequencias_consecutivas': Counter(),
            'paridade': Counter(),
            'soma_total': [],
            'distribuicao_dezenas': Counter(),
            'espacamento_numeros': Counter(),  # NOVO: análise de espaçamento
            'densidade_regioes': Counter()     # NOVO: densidade por região
        }
        
        for concurso, resultado in self.historico_acertos.items():
            if 'combinacao_gerada' in resultado:
                combinacao = resultado['combinacao_gerada']
                acertos = resultado['acertos']
                
                # Peso aumentado para acertos na faixa premium
                peso_acertos = acertos * 2 if acertos >= 12 else acertos
                
                # Análise de distribuição por regiões (mais refinada)
                regiao1 = sum(1 for n in combinacao if 1 <= n <= 5)
                regiao2 = sum(1 for n in combinacao if 6 <= n <= 10)
                regiao3 = sum(1 for n in combinacao if 11 <= n <= 15)
                regiao4 = sum(1 for n in combinacao if 16 <= n <= 20)
                regiao5 = sum(1 for n in combinacao if 21 <= n <= 25)
                
                distribuicao = f"{regiao1}-{regiao2}-{regiao3}-{regiao4}-{regiao5}"
                padroes['distribuicao_regioes'][distribuicao] += peso_acertos
                
                # Densidade por região (números por área)
                densidades = [regiao1/5, regiao2/5, regiao3/5, regiao4/5, regiao5/5]
                densidade_pattern = f"{densidades[0]:.1f}-{densidades[1]:.1f}-{densidades[2]:.1f}-{densidades[3]:.1f}-{densidades[4]:.1f}"
                padroes['densidade_regioes'][densidade_pattern] += peso_acertos
                
                # Sequências consecutivas (refinado para faixa 11-13)
                consecutivas = self.contar_consecutivas(combinacao)
                padroes['sequencias_consecutivas'][consecutivas] += peso_acertos
                
                # Paridade (pares/ímpares) - mais preciso para 11-13
                pares = sum(1 for n in combinacao if n % 2 == 0)
                impares = 15 - pares
                paridade = f"{pares}p-{impares}i"
                padroes['paridade'][paridade] += peso_acertos
                
                # Soma total - ajustada para faixa 11-13
                padroes['soma_total'].append((sum(combinacao), peso_acertos))
                
                # Espaçamento entre números (NOVO)
                sorted_comb = sorted(combinacao)
                espacamentos = [sorted_comb[i+1] - sorted_comb[i] for i in range(len(sorted_comb)-1)]
                espacamento_medio = sum(espacamentos) / len(espacamentos)
                padroes['espacamento_numeros'][round(espacamento_medio, 1)] += peso_acertos
                
                # Distribuição de dezenas por posição
                for pos, num in enumerate(sorted(combinacao)):
                    padroes['distribuicao_dezenas'][(pos, num//5)] += peso_acertos
        
        return padroes
    
    def calcular_pesos_caracteristicas(self):
        """Calcula pesos otimizados para faixa 11-13"""
        if not self.padroes_faixa_premium['soma_total']:
            # Pesos otimizados para faixa premium 11-13
            return {
                'distribuicao_regioes': 0.30,    # Aumentado - mais crítico para 11-13
                'sequencias_consecutivas': 0.20,
                'paridade': 0.15,               # Diminuído - menos crítico
                'soma_total': 0.20,             # Aumentado - importante para 11-13
                'espacamento_numeros': 0.10,    # NOVO - espaçamento
                'densidade_regioes': 0.05       # NOVO - densidade
            }
        
        # Calcula pesos baseado na eficácia histórica para faixa 11-13
        total_acertos = sum(acertos for _, acertos in self.padroes_faixa_premium['soma_total'])
        
        pesos = {
            'distribuicao_regioes': len(self.padroes_faixa_premium['distribuicao_regioes']) / 80,
            'sequencias_consecutivas': len(self.padroes_faixa_premium['sequencias_consecutivas']) / 40,
            'paridade': len(self.padroes_faixa_premium['paridade']) / 25,
            'soma_total': len(self.padroes_faixa_premium['soma_total']) / 800,
            'espacamento_numeros': len(self.padroes_faixa_premium['espacamento_numeros']) / 50,
            'densidade_regioes': len(self.padroes_faixa_premium['densidade_regioes']) / 100
        }
        
        # Normaliza para somar 1
        total_peso = sum(pesos.values())
        for chave in pesos:
            pesos[chave] = pesos[chave] / total_peso
            
        return pesos
    
    def contar_consecutivas(self, combinacao):
        """Conta sequências consecutivas (ajustado para faixa 11-13)"""
        sorted_comb = sorted(combinacao)
        consecutivas = 0
        sequencia_atual = 1
        
        for i in range(1, len(sorted_comb)):
            if sorted_comb[i] == sorted_comb[i-1] + 1:
                sequencia_atual += 1
            else:
                if sequencia_atual >= 2:
                    consecutivas += sequencia_atual
                sequencia_atual = 1
                
        if sequencia_atual >= 2:
            consecutivas += sequencia_atual
            
        return consecutivas
    
    def calcular_espacamento_medio(self, combinacao):
        """Calcula espaçamento médio entre números"""
        sorted_comb = sorted(combinacao)
        espacamentos = [sorted_comb[i+1] - sorted_comb[i] for i in range(len(sorted_comb)-1)]
        return sum(espacamentos) / len(espacamentos)
    
    def avaliar_combinacao_premium(self, combinacao):
        """
        Avalia uma combinação especificamente para faixa 11-13
        Score de 0 a 100, otimizado para maior probabilidade na faixa PREMIUM
        """
        if len(combinacao) != 15 or len(set(combinacao)) != 15:
            return 0
        
        score = 0
        
        # 1. Avalia distribuição por regiões (PESO AUMENTADO para 11-13)
        regiao1 = sum(1 for n in combinacao if 1 <= n <= 5)
        regiao2 = sum(1 for n in combinacao if 6 <= n <= 10)
        regiao3 = sum(1 for n in combinacao if 11 <= n <= 15)
        regiao4 = sum(1 for n in combinacao if 16 <= n <= 20)
        regiao5 = sum(1 for n in combinacao if 21 <= n <= 25)
        
        distribuicao = f"{regiao1}-{regiao2}-{regiao3}-{regiao4}-{regiao5}"
        
        # Score baseado em padrões históricos para 11-13
        if distribuicao in self.padroes_faixa_premium['distribuicao_regioes']:
            freq = self.padroes_faixa_premium['distribuicao_regioes'][distribuicao]
            max_freq = max(self.padroes_faixa_premium['distribuicao_regioes'].values()) if self.padroes_faixa_premium['distribuicao_regioes'] else 1
            score += (freq / max_freq) * 30 * self.pesos_caracteristicas['distribuicao_regioes']
        
        # Bonificação para distribuições equilibradas (ideal para 11-13)
        if 2 <= regiao1 <= 4 and 2 <= regiao2 <= 4 and 2 <= regiao3 <= 4 and 2 <= regiao4 <= 4 and 2 <= regiao5 <= 4:
            score += 5
        
        # 2. Avalia sequências consecutivas (refinado para 11-13)
        consecutivas = self.contar_consecutivas(combinacao)
        if consecutivas in self.padroes_faixa_premium['sequencias_consecutivas']:
            freq = self.padroes_faixa_premium['sequencias_consecutivas'][consecutivas]
            max_freq = max(self.padroes_faixa_premium['sequencias_consecutivas'].values()) if self.padroes_faixa_premium['sequencias_consecutivas'] else 1
            score += (freq / max_freq) * 20 * self.pesos_caracteristicas['sequencias_consecutivas']
        
        # Bonificação para faixa ideal de consecutivos para 11-13
        if 5 <= consecutivas <= 8:
            score += 3
        
        # 3. Avalia paridade (menos crítico para 11-13)
        pares = sum(1 for n in combinacao if n % 2 == 0)
        impares = 15 - pares
        paridade = f"{pares}p-{impares}i"
        
        if paridade in self.padroes_faixa_premium['paridade']:
            freq = self.padroes_faixa_premium['paridade'][paridade]
            max_freq = max(self.padroes_faixa_premium['paridade'].values()) if self.padroes_faixa_premium['paridade'] else 1
            score += (freq / max_freq) * 15 * self.pesos_caracteristicas['paridade']
        
        # 4. Avalia soma total (CRÍTICO para faixa 11-13)
        soma = sum(combinacao)
        if self.padroes_faixa_premium['soma_total']:
            somas_historicas = [s for s, a in self.padroes_faixa_premium['soma_total']]
            media_soma = sum(somas_historicas) / len(somas_historicas)
            desvio = abs(soma - media_soma) / media_soma
            score_soma = max(0, (1 - desvio) * 20)
            score += score_soma * self.pesos_caracteristicas['soma_total']
        else:
            # Faixa ideal para 11-13 acertos (mais restritiva)
            if 190 <= soma <= 215:
                score += 15
            elif 185 <= soma <= 220:
                score += 10
        
        # 5. NOVO: Avalia espaçamento médio
        espacamento = self.calcular_espacamento_medio(combinacao)
        # Espaçamento ideal para 11-13: nem muito denso, nem muito esparso
        if 1.5 <= espacamento <= 2.0:
            score += 8 * self.pesos_caracteristicas['espacamento_numeros']
        elif 1.2 <= espacamento <= 2.5:
            score += 5 * self.pesos_caracteristicas['espacamento_numeros']
        
        # 6. NOVO: Avalia densidade por região
        densidades = [regiao1/5, regiao2/5, regiao3/5, regiao4/5, regiao5/5]
        # Densidade equilibrada é ideal para 11-13
        densidade_balanceada = all(0.2 <= d <= 0.8 for d in densidades)
        if densidade_balanceada:
            score += 3 * self.pesos_caracteristicas['densidade_regioes']
        
        return min(100, score)
    
    def filtrar_melhores_para_faixa_premium(self, combinacoes, top_n=10):
        """
        Filtra as melhores combinações para a faixa PREMIUM 11-13
        """
        print(f"🔍 Avaliando {len(combinacoes)} combinações para faixa PREMIUM 11-13...")
        
        combinacoes_com_score = []
        
        for i, combinacao in enumerate(combinacoes):
            score = self.avaliar_combinacao_premium(combinacao)
            combinacoes_com_score.append((combinacao, score))
            
            if (i + 1) % 10 == 0:
                print(f"   Avaliadas: {i + 1}/{len(combinacoes)}")
        
        # Ordena por score decrescente
        combinacoes_com_score.sort(key=lambda x: x[1], reverse=True)
        
        print(f"✓ Selecionando top {top_n} para faixa PREMIUM 11-13")
        return combinacoes_com_score[:top_n]
    
    def relatorio_avaliacao_premium(self, combinacoes_scores):
        """Gera relatório da avaliação para faixa premium"""
        print("\n" + "="*60)
        print("RELATÓRIO FAIXA PREMIUM (11-13 acertos)")
        print("="*60)
        
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Combinações avaliadas: {len(combinacoes_scores)}")
        print(f"Faixa alvo: {self.faixa_alvo[0]} a {self.faixa_alvo[1]} acertos")
        print(f"Dados históricos: {len(self.historico_acertos)} resultados na faixa premium")
        
        print("\nPesos otimizados para faixa 11-13:")
        for caracteristica, peso in self.pesos_caracteristicas.items():
            print(f"  {caracteristica}: {peso:.2%}")
        
        print(f"\nTop {len(combinacoes_scores)} combinações para faixa PREMIUM 11-13:")
        for i, (combinacao, score) in enumerate(combinacoes_scores, 1):
            soma = sum(combinacao)
            pares = sum(1 for n in combinacao if n % 2 == 0)
            espacamento = self.calcular_espacamento_medio(combinacao)
            
            print(f"{i:2d}. Score: {score:5.1f} | Soma: {soma} | Pares: {pares} | Espaç: {espacamento:.1f}")
            print(f"     Combinação: {sorted(combinacao)}")
        
        # Análise dos scores para faixa premium
        scores = [score for _, score in combinacoes_scores]
        print(f"\nAnálise dos scores (faixa PREMIUM 11-13):")
        print(f"  Maior score: {max(scores):.1f}")
        print(f"  Menor score: {min(scores):.1f}")
        print(f"  Score médio: {sum(scores)/len(scores):.1f}")
        
        # Classificação dos resultados
        excelentes = sum(1 for s in scores if s >= 75)
        bons = sum(1 for s in scores if 60 <= s < 75)
        regulares = sum(1 for s in scores if s < 60)
        
        print(f"\nClassificação para faixa PREMIUM:")
        print(f"  Excelentes (75+): {excelentes}")
        print(f"  Boas (60-74): {bons}")
        print(f"  Regulares (<60): {regulares}")
        
        return {
            'total_avaliadas': len(combinacoes_scores),
            'faixa_alvo': self.faixa_alvo,
            'dados_historicos': len(self.historico_acertos),
            'melhor_score': max(scores) if scores else 0,
            'score_medio': sum(scores)/len(scores) if scores else 0,
            'classificacao': {'excelentes': excelentes, 'boas': bons, 'regulares': regulares}
        }

# Exemplo de uso
if __name__ == "__main__":
    print("🎯 AVALIADOR FAIXA PREMIUM 11-13")
    print("Testando com combinações exemplo...")
    
    avaliador = AvaliadorFaixaPremium()
    
    # Combinações de teste otimizadas para 11-13
    combinacoes_teste = [
        [1, 2, 6, 7, 8, 11, 12, 15, 16, 17, 19, 21, 22, 24, 25],  # Distribuição equilibrada
        [3, 4, 5, 9, 10, 11, 13, 14, 16, 18, 19, 20, 22, 23, 25], # Soma próxima do ideal
        [1, 3, 6, 8, 9, 12, 13, 14, 15, 17, 18, 20, 21, 24, 25]   # Espaçamento balanceado
    ]
    
    melhores = avaliador.filtrar_melhores_para_faixa_premium(combinacoes_teste, 3)
    relatorio = avaliador.relatorio_avaliacao_premium(melhores)
    
    print(f"\n🏆 TESTE CONCLUÍDO! Melhor score: {relatorio['melhor_score']:.1f}")
    print("Sistema pronto para faixa PREMIUM 11-13!")
