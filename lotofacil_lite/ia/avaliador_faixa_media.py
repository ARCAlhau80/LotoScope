"""
Avaliador Assimétrico - Faixa Média (9-13 acertos)
Estratégia de segundo filtro para identificar combinações com maior probabilidade 
de acertar entre 9 e 13 números na Lotofácil.
"""

import json
import random
from collections import Counter
from datetime import datetime

class AvaliadorFaixaMedia:
    def __init__(self):
        self.historico_acertos = self.carregar_historico_acertos()
        self.padroes_faixa_media = self.extrair_padroes_faixa_media()
        self.pesos_caracteristicas = self.calcular_pesos_caracteristicas()
        
    def carregar_historico_acertos(self):
        """Carrega dados históricos de acertos na faixa 9-13"""
        try:
            with open('resultados_teste_historico.json', 'r') as f:
                dados = json.load(f)
                
            # Filtra apenas resultados na faixa 9-13
            acertos_faixa_media = {}
            for concurso, resultado in dados.items():
                if isinstance(resultado, dict) and 'acertos' in resultado:
                    acertos = resultado['acertos']
                    if 9 <= acertos <= 13:
                        acertos_faixa_media[concurso] = resultado
                        
            print(f"Carregados {len(acertos_faixa_media)} resultados na faixa 9-13")
            return acertos_faixa_media
            
        except FileNotFoundError:
            print("Arquivo histórico não encontrado. Usando padrões padrão.")
            return {}
    
    def extrair_padroes_faixa_media(self):
        """Extrai padrões das combinações que acertaram 9-13"""
        padroes = {
            'distribuicao_regioes': Counter(),
            'sequencias_consecutivas': Counter(),
            'paridade': Counter(),
            'soma_total': [],
            'distribuicao_dezenas': Counter()
        }
        
        for concurso, resultado in self.historico_acertos.items():
            if 'combinacao_gerada' in resultado:
                combinacao = resultado['combinacao_gerada']
                acertos = resultado['acertos']
                
                # Análise de distribuição por regiões
                regiao1 = sum(1 for n in combinacao if 1 <= n <= 5)
                regiao2 = sum(1 for n in combinacao if 6 <= n <= 10)
                regiao3 = sum(1 for n in combinacao if 11 <= n <= 15)
                regiao4 = sum(1 for n in combinacao if 16 <= n <= 20)
                regiao5 = sum(1 for n in combinacao if 21 <= n <= 25)
                
                distribuicao = f"{regiao1}-{regiao2}-{regiao3}-{regiao4}-{regiao5}"
                padroes['distribuicao_regioes'][distribuicao] += acertos  # Peso por acertos
                
                # Sequências consecutivas
                consecutivas = self.contar_consecutivas(combinacao)
                padroes['sequencias_consecutivas'][consecutivas] += acertos
                
                # Paridade (pares/ímpares)
                pares = sum(1 for n in combinacao if n % 2 == 0)
                impares = 15 - pares
                paridade = f"{pares}p-{impares}i"
                padroes['paridade'][paridade] += acertos
                
                # Soma total
                padroes['soma_total'].append((sum(combinacao), acertos))
                
                # Distribuição de dezenas por posição
                for pos, num in enumerate(sorted(combinacao)):
                    padroes['distribuicao_dezenas'][(pos, num//5)] += acertos
        
        return padroes
    
    def calcular_pesos_caracteristicas(self):
        """Calcula pesos para cada característica baseado no desempenho histórico"""
        if not self.padroes_faixa_media['soma_total']:
            # Pesos padrão se não há dados históricos
            return {
                'distribuicao_regioes': 0.25,
                'sequencias_consecutivas': 0.20,
                'paridade': 0.20,
                'soma_total': 0.15,
                'distribuicao_dezenas': 0.20
            }
        
        # Calcula pesos baseado na eficácia histórica
        total_acertos = sum(acertos for _, acertos in self.padroes_faixa_media['soma_total'])
        
        # Normaliza os pesos
        pesos = {
            'distribuicao_regioes': len(self.padroes_faixa_media['distribuicao_regioes']) / 100,
            'sequencias_consecutivas': len(self.padroes_faixa_media['sequencias_consecutivas']) / 50,
            'paridade': len(self.padroes_faixa_media['paridade']) / 30,
            'soma_total': len(self.padroes_faixa_media['soma_total']) / 1000,
            'distribuicao_dezenas': len(self.padroes_faixa_media['distribuicao_dezenas']) / 200
        }
        
        # Normaliza para somar 1
        total_peso = sum(pesos.values())
        for chave in pesos:
            pesos[chave] = pesos[chave] / total_peso
            
        return pesos
    
    def contar_consecutivas(self, combinacao):
        """Conta sequências consecutivas na combinação"""
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
    
    def avaliar_combinacao(self, combinacao):
        """
        Avalia uma combinação e retorna score de probabilidade para faixa 9-13
        Score de 0 a 100, onde 100 = máxima probabilidade na faixa 9-13
        """
        if len(combinacao) != 15 or len(set(combinacao)) != 15:
            return 0
        
        score = 0
        
        # 1. Avalia distribuição por regiões
        regiao1 = sum(1 for n in combinacao if 1 <= n <= 5)
        regiao2 = sum(1 for n in combinacao if 6 <= n <= 10)
        regiao3 = sum(1 for n in combinacao if 11 <= n <= 15)
        regiao4 = sum(1 for n in combinacao if 16 <= n <= 20)
        regiao5 = sum(1 for n in combinacao if 21 <= n <= 25)
        
        distribuicao = f"{regiao1}-{regiao2}-{regiao3}-{regiao4}-{regiao5}"
        
        # Score baseado em padrões históricos bem-sucedidos
        if distribuicao in self.padroes_faixa_media['distribuicao_regioes']:
            freq = self.padroes_faixa_media['distribuicao_regioes'][distribuicao]
            max_freq = max(self.padroes_faixa_media['distribuicao_regioes'].values()) if self.padroes_faixa_media['distribuicao_regioes'] else 1
            score += (freq / max_freq) * 25 * self.pesos_caracteristicas['distribuicao_regioes']
        
        # 2. Avalia sequências consecutivas
        consecutivas = self.contar_consecutivas(combinacao)
        if consecutivas in self.padroes_faixa_media['sequencias_consecutivas']:
            freq = self.padroes_faixa_media['sequencias_consecutivas'][consecutivas]
            max_freq = max(self.padroes_faixa_media['sequencias_consecutivas'].values()) if self.padroes_faixa_media['sequencias_consecutivas'] else 1
            score += (freq / max_freq) * 20 * self.pesos_caracteristicas['sequencias_consecutivas']
        
        # 3. Avalia paridade
        pares = sum(1 for n in combinacao if n % 2 == 0)
        impares = 15 - pares
        paridade = f"{pares}p-{impares}i"
        
        if paridade in self.padroes_faixa_media['paridade']:
            freq = self.padroes_faixa_media['paridade'][paridade]
            max_freq = max(self.padroes_faixa_media['paridade'].values()) if self.padroes_faixa_media['paridade'] else 1
            score += (freq / max_freq) * 20 * self.pesos_caracteristicas['paridade']
        
        # 4. Avalia soma total
        soma = sum(combinacao)
        if self.padroes_faixa_media['soma_total']:
            somas_historicas = [s for s, a in self.padroes_faixa_media['soma_total']]
            media_soma = sum(somas_historicas) / len(somas_historicas)
            desvio = abs(soma - media_soma) / media_soma
            score_soma = max(0, (1 - desvio) * 15)
            score += score_soma * self.pesos_caracteristicas['soma_total']
        
        # 5. Avalia distribuição de dezenas
        distribuicao_score = 0
        for pos, num in enumerate(sorted(combinacao)):
            chave = (pos, num//5)
            if chave in self.padroes_faixa_media['distribuicao_dezenas']:
                freq = self.padroes_faixa_media['distribuicao_dezenas'][chave]
                max_freq = max(self.padroes_faixa_media['distribuicao_dezenas'].values()) if self.padroes_faixa_media['distribuicao_dezenas'] else 1
                distribuicao_score += freq / max_freq
                
        score += (distribuicao_score / 15) * 20 * self.pesos_caracteristicas['distribuicao_dezenas']
        
        return min(100, score)
    
    def filtrar_melhores_para_faixa_media(self, combinacoes, top_n=10):
        """
        Filtra as melhores combinações para a faixa 9-13
        """
        combinacoes_com_score = []
        
        for combinacao in combinacoes:
            score = self.avaliar_combinacao(combinacao)
            combinacoes_com_score.append((combinacao, score))
        
        # Ordena por score decrescente
        combinacoes_com_score.sort(key=lambda x: x[1], reverse=True)
        
        return combinacoes_com_score[:top_n]
    
    def relatorio_avaliacao(self, combinacoes_scores):
        """Gera relatório da avaliação"""
        print("\n" + "="*60)
        print("RELATÓRIO DE AVALIAÇÃO - FAIXA MÉDIA (9-13 acertos)")
        print("="*60)
        
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Combinações avaliadas: {len(combinacoes_scores)}")
        print(f"Dados históricos: {len(self.historico_acertos)} resultados na faixa 9-13")
        
        print("\nPesos das características:")
        for caracteristica, peso in self.pesos_caracteristicas.items():
            print(f"  {caracteristica}: {peso:.2%}")
        
        print(f"\nTop {len(combinacoes_scores)} combinações para faixa 9-13:")
        for i, (combinacao, score) in enumerate(combinacoes_scores, 1):
            print(f"{i:2d}. Score: {score:5.1f} | Combinação: {sorted(combinacao)}")
        
        # Análise dos scores
        scores = [score for _, score in combinacoes_scores]
        print(f"\nAnálise dos scores:")
        print(f"  Maior score: {max(scores):.1f}")
        print(f"  Menor score: {min(scores):.1f}")
        print(f"  Score médio: {sum(scores)/len(scores):.1f}")
        
        return {
            'total_avaliadas': len(combinacoes_scores),
            'dados_historicos': len(self.historico_acertos),
            'melhor_score': max(scores) if scores else 0,
            'score_medio': sum(scores)/len(scores) if scores else 0
        }

# Exemplo de uso
if __name__ == "__main__":
    print("Inicializando Avaliador de Faixa Média...")
    avaliador = AvaliadorFaixaMedia()
    
    # Exemplo com combinações de teste
    combinacoes_teste = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 2, 4],
        [5, 10, 15, 20, 25, 1, 6, 11, 16, 21, 2, 7, 12, 17, 22]
    ]
    
    melhores = avaliador.filtrar_melhores_para_faixa_media(combinacoes_teste, 3)
    relatorio = avaliador.relatorio_avaliacao(melhores)
