#!/usr/bin/env python3
"""
Correção do Gerador Dinâmico - Balanceamento Inteligente
Corrige os problemas identificados na análise de performance
"""

import random
from collections import defaultdict

class GeradorDinamicoCorrigido:
    def __init__(self):
        self.numeros_fixos_evitar = [1, 5, 6, 12, 15, 18, 25]  # Números que apareceram em 100% dos jogos
        self.faixas_peso = {
            "1-5": 0.18,    # Reduzido de 25.7%
            "6-10": 0.20,   # Aumentado ligeiramente
            "11-15": 0.22,  # Reduzido de 24.8%
            "16-20": 0.22,  # Aumentado de 14.8%
            "21-25": 0.18   # Aumentado ligeiramente de 16.2%
        }
    
    def gerar_combinacao_balanceada(self):
        """Gera combinação com distribuição equilibrada"""
        combinacao = []
        
        # Distribuir por faixas de forma balanceada
        faixas = {
            "1-5": list(range(1, 6)),
            "6-10": list(range(6, 11)),
            "11-15": list(range(11, 16)),
            "16-20": list(range(16, 21)),
            "21-25": list(range(21, 26))
        }
        
        # Número target por faixa (para 15 números)
        nums_por_faixa = {
            "1-5": 3,    # ~20%
            "6-10": 3,   # ~20%  
            "11-15": 3,  # ~20%
            "16-20": 3,  # ~20%
            "21-25": 3   # ~20%
        }
        
        for faixa, quantidade in nums_por_faixa.items():
            nums_faixa = faixas[faixa].copy()
            
            # Reduzir probabilidade dos números "viciados"
            nums_ponderados = []
            for num in nums_faixa:
                if num in self.numeros_fixos_evitar:
                    # 30% de chance para números "fixos"
                    if random.random() < 0.3:
                        nums_ponderados.append(num)
                else:
                    # 70% de chance para outros números
                    nums_ponderados.extend([num] * 2)
            
            # Selecionar números da faixa SEM duplicatas
            nums_disponiveis = list(set(nums_ponderados))  # Remove duplicatas
            if len(nums_disponiveis) >= quantidade:
                selecionados = random.sample(nums_disponiveis, quantidade)
            else:
                selecionados = nums_disponiveis
            
            # Adicionar apenas números que ainda não estão na combinação
            for num in selecionados:
                if num not in combinacao:
                    combinacao.append(num)
        
        # Completar se necessário (raramente vai acontecer)
        while len(combinacao) < 15:
            num_adicional = random.randint(int(1), int(25))
            if num_adicional not in combinacao:
                combinacao.append(num_adicional)
        
        # Reduzir se excedeu
        if len(combinacao) > 15:
            combinacao = random.sample(combinacao, 15)
        
        return sorted(combinacao)
    
    def evitar_sequencias_longas(self, combinacao):
        """Evita sequências consecutivas muito longas"""
        combinacao_sorted = sorted(combinacao)
        sequencia_atual = 1
        max_sequencia = 0
        
        for i in range(len(combinacao_sorted) - 1):
            if combinacao_sorted[i+1] - combinacao_sorted[i] == 1:
                sequencia_atual += 1
                max_sequencia = max(max_sequencia, sequencia_atual)
            else:
                sequencia_atual = 1
        
        # Se sequência muito longa, trocar alguns números
        if max_sequencia > 4:  # Máximo 4 consecutivos
            return self.quebrar_sequencia(combinacao_sorted)
        
        return combinacao_sorted
    
    def quebrar_sequencia(self, combinacao):
        """Quebra sequências muito longas"""
        # Estratégia simples: trocar alguns números por outros aleatórios
        nova_combinacao = combinacao.copy()
        
        # Trocar 2-3 números aleatoriamente
        nums_trocar = random.sample(range(len(nova_combinacao)), min(3, len(nova_combinacao)//3))
        
        for idx in nums_trocar:
            tentativas = 0
            while tentativas < 10:
                novo_num = random.randint(int(1), int(25))
                if novo_num not in nova_combinacao:
                    nova_combinacao[idx] = novo_num
                    break
                tentativas += 1
        
        return sorted(set(nova_combinacao))
    
    def gerar_multiplas_combinacoes(self, quantidade=10):
        """Gera múltiplas combinações diversificadas"""
        combinacoes = []
        tentativas_max = quantidade * 3
        
        while len(combinacoes) < quantidade and tentativas_max > 0:
            combo = self.gerar_combinacao_balanceada()
            combo = self.evitar_sequencias_longas(combo)
            
            # Garantir 15 números exatos
            if len(combo) != 15:
                if len(combo) < 15:
                    # Adicionar números aleatórios
                    nums_faltando = 15 - len(combo)
                    candidatos = [n for n in range(1, 26) if n not in combo]
                    if len(candidatos) >= nums_faltando:
                        combo.extend(random.sample(candidatos, nums_faltando))
                else:
                    # Remover números aleatórios
                    combo = random.sample(combo, 15)
                
                combo = sorted(combo)
            
            # Verificar duplicatas
            if combo not in combinacoes:
                combinacoes.append(combo)
            
            tentativas_max -= 1
        
        return combinacoes

def testar_correcoes():
    """Testa as correções implementadas"""
    print("🧪 TESTANDO CORREÇÕES DO GERADOR")
    print("="*50)
    
    gerador = GeradorDinamicoCorrigido()
    combinacoes_teste = gerador.gerar_multiplas_combinacoes(10)
    
    # Análise das correções
    frequencia = defaultdict(int)
    total_jogos = len(combinacoes_teste)
    
    for combo in combinacoes_teste:
        for num in combo:
            frequencia[num] += 1
    
    print(f"📊 Geradas {total_jogos} combinações corrigidas")
    print(f"📊 Números mais frequentes APÓS correção:")
    
    nums_ordenados = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)
    
    for num, freq in nums_ordenados[:10]:
        percentual = (freq / total_jogos) * 100
        status = "🔥" if freq == total_jogos else "✅" if freq < total_jogos * 0.8 else "⚠️"
        print(f"   {status} {num:2d}: {freq:2d} vezes ({percentual:.1f}%)")
    
    # Verificar distribuição por faixas
    print(f"\n📈 DISTRIBUIÇÃO POR FAIXAS CORRIGIDA:")
    
    faixas_corrigidas = {"1-5": 0, "6-10": 0, "11-15": 0, "16-20": 0, "21-25": 0}
    
    for combo in combinacoes_teste:
        for num in combo:
            if 1 <= num <= 5:
                faixas_corrigidas["1-5"] += 1
            elif 6 <= num <= 10:
                faixas_corrigidas["6-10"] += 1
            elif 11 <= num <= 15:
                faixas_corrigidas["11-15"] += 1
            elif 16 <= num <= 20:
                faixas_corrigidas["16-20"] += 1
            elif 21 <= num <= 25:
                faixas_corrigidas["21-25"] += 1
    
    total_nums_corrigido = sum(len(combo) for combo in combinacoes_teste)
    
    for faixa, count in faixas_corrigidas.items():
        percentual = (count / total_nums_corrigido) * 100
        print(f"   {faixa}: {count:3d} números ({percentual:.1f}%)")
    
    # Mostrar algumas combinações
    print(f"\n🎯 EXEMPLOS DE COMBINAÇÕES CORRIGIDAS:")
    for i, combo in enumerate(combinacoes_teste[:5], 1):
        combo_str = ", ".join(f"{n:2d}" for n in combo)
        print(f"   {i}: {combo_str}")
    
    return combinacoes_teste

if __name__ == "__main__":
    testar_correcoes()
    print(f"\n💡 PRÓXIMO PASSO: Use estas combinações no próximo concurso!")
    print(f"📊 Compare os resultados com as antigas para validar melhorias")
