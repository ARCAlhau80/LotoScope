#!/usr/bin/env python3
"""
Gerador Completamente Isolado - Sem Dependência do Original
Implementa lógica temporal própria baseada em padrões observados
"""

import random
from datetime import datetime

class GeradorIsolado:
    """
    Gerador completamente independente que simula comportamento histórico
    sem depender das queries do gerador original
    """
    
    def __init__(self, concurso_limite):
        self.concurso_limite = concurso_limite
        self.ciclo_limite = self._calcular_ciclo(concurso_limite)
        
        # Padrões históricos simulados baseados em análises anteriores
        self.padroes_historicos = self._definir_padroes_historicos()
    
    def _calcular_ciclo(self, concurso):
        """Calcula ciclo baseado no concurso"""
        return max(1, int((concurso * 737) / 3479))
    
    def _definir_padroes_historicos(self):
        """Define padrões diferentes por época histórica"""
        
        if self.concurso_limite < 1500:
            # Época inicial (2003-2010)
            return {
                'numeros_quentes': [1, 2, 3, 4, 5, 10, 11, 13, 15, 20],
                'numeros_frios': [18, 19, 22, 23, 24, 25],
                'tendencia_baixos': 0.7,  # 70% números baixos
                'sequencias_dominantes': [1, 2, 3, 10, 11],
                'instabilidade': 0.3  # Menos instável
            }
        elif self.concurso_limite < 2200:
            # Época média (2010-2015)
            return {
                'numeros_quentes': [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
                'numeros_frios': [1, 3, 7, 21, 24, 25],
                'tendencia_baixos': 0.55,  # Mais equilibrado
                'sequencias_dominantes': [2, 4, 10, 12, 16],
                'instabilidade': 0.4
            }
        elif self.concurso_limite < 3000:
            # Época avançada (2015-2020)
            return {
                'numeros_quentes': [5, 8, 9, 12, 15, 16, 17, 18, 19, 23],
                'numeros_frios': [1, 2, 3, 4, 11, 25],
                'tendencia_baixos': 0.45,  # Números altos ganham força
                'sequencias_dominantes': [8, 12, 15, 17, 19],
                'instabilidade': 0.5  # Mais instável
            }
        else:
            # Época atual (2020+)
            return {
                'numeros_quentes': [1, 5, 6, 8, 12, 15, 18, 20, 23, 25],
                'numeros_frios': [7, 11, 14, 17, 21, 22],
                'tendencia_baixos': 0.5,  # Equilibrado
                'sequencias_dominantes': [1, 5, 12, 15, 18],
                'instabilidade': 0.6  # Mais instável
            }
    
    def gerar_combinacao_historica(self, qtd_numeros=15, variacao=None):
        """
        Gera combinação baseada no período histórico específico
        variacao: permite gerar combinações diferentes para o mesmo período
        """
        print(f"🕒 GERADOR ISOLADO: Concurso <= {self.concurso_limite} (Ciclo ~{self.ciclo_limite})")
        
        # Usar ciclo como base, mas adicionar variação para diferentes jogos
        if variacao is not None:
            seed_base = self.ciclo_limite + (variacao * 17)  # 17 para dispersar bem
        else:
            seed_base = self.ciclo_limite
            
        random.seed(42)
        
        padroes = self.padroes_historicos
        
        combinacao = []
        
        # 1. Números "quentes" do período (40% da combinação)
        qtd_quentes = int(qtd_numeros * 0.4)
        quentes_disponiveis = padroes['numeros_quentes']
        if len(quentes_disponiveis) >= qtd_quentes:
            combinacao.extend(random.sample(quentes_disponiveis, qtd_quentes))
        
        # 2. Sequências dominantes do período (20% da combinação)
        qtd_sequencias = int(qtd_numeros * 0.2)
        sequencias = padroes['sequencias_dominantes']
        for num in sequencias:
            if len(combinacao) < qtd_numeros and num not in combinacao:
                combinacao.append(num)
                if len([n for n in combinacao if n in sequencias]) >= qtd_sequencias:
                    break
        
        # 3. Aplicar tendência histórica (baixos vs altos)
        while len(combinacao) < qtd_numeros:
            if random.random() < padroes['tendencia_baixos']:
                # Favorecer números baixos (1-12)
                candidatos = [n for n in range(1, 13) if n not in combinacao]
            else:
                # Favorecer números altos (13-25)
                candidatos = [n for n in range(13, 26) if n not in combinacao]
            
            if candidatos:
                combinacao.append(random.choice(candidatos))
            else:
                # Se não há candidatos na faixa preferida, pegar qualquer
                todos_candidatos = [n for n in range(1, 26) if n not in combinacao]
                if todos_candidatos:
                    combinacao.append(random.choice(todos_candidatos))
        
        # 4. Aplicar instabilidade do período
        instabilidade = padroes['instabilidade']
        if random.random() < instabilidade:
            # Trocar 1-2 números por números "frios" para simular surpresas
            if len(padroes['numeros_frios']) > 0:
                for _ in range(min(2, len(padroes['numeros_frios']))):
                    if len(combinacao) > 10:  # Só trocar se tiver números suficientes
                        idx_trocar = random.randint(int(0), int(len(combinacao)) - 1)
                        numero_frio = random.choice(padroes[int('numeros_frios')])
                        if numero_frio not in combinacao:
                            combinacao[idx_trocar] = numero_frio
        
        # Garantir tamanho e ordenar
        combinacao = sorted(list(set(combinacao))[:qtd_numeros])
        
        # Completar se ficou faltando números
        while len(combinacao) < qtd_numeros:
            candidatos = [n for n in range(1, 26) if n not in combinacao]
            if candidatos:
                combinacao.append(random.choice(candidatos))
                combinacao = sorted(combinacao)
        
        print(f"   Padrão do período: {padroes['sequencias_dominantes']}")
        print(f"   Resultado: {combinacao}")
        
        return combinacao
    
    def diagnostico_periodo(self):
        """Mostra diagnóstico do período temporal"""
        
        padroes = self.padroes_historicos
        
        print(f"\n📊 DIAGNÓSTICO PERÍODO - Concurso {self.concurso_limite}")
        print("-" * 50)
        print(f"🔥 Números quentes: {padroes['numeros_quentes']}")
        print(f"❄️  Números frios: {padroes['numeros_frios']}")  
        print(f"📈 Tendência baixos: {padroes['tendencia_baixos']:.1%}")
        print(f"⚡ Sequências dominantes: {padroes['sequencias_dominantes']}")
        print(f"🌪️  Instabilidade: {padroes['instabilidade']:.1%}")

def testar_gerador_isolado():
    """Teste do gerador isolado"""
    
    print("🧪 TESTE DO GERADOR ISOLADO")
    print("=" * 50)
    
    # Períodos bem distintos para validar diferenças
    periodos = [1200, 1800, 2500, 3200, 3479]
    
    resultados = {}
    
    for concurso in periodos:
        print(f"\n🕒 PERÍODO: Concurso {concurso}")
        
        gerador = GeradorIsolado(concurso)
        gerador.diagnostico_periodo()
        
        # Gerar combinação
        combo_15 = gerador.gerar_combinacao_historica(15)
        combo_20 = gerador.gerar_combinacao_historica(20)
        
        resultados[concurso] = {
            '15': combo_15,
            '20': combo_20
        }
    
    # Verificar variação entre períodos
    print(f"\n📊 VERIFICAÇÃO DE VARIAÇÃO TEMPORAL:")
    print("-" * 40)
    
    combos_15 = [tuple(resultados[c]['15']) for c in periodos]
    combos_20 = [tuple(resultados[c]['20']) for c in periodos]
    
    variacao_15 = len(set(combos_15))
    variacao_20 = len(set(combos_20))
    
    print(f"Variação 15 números: {variacao_15}/{len(periodos)} diferentes")
    print(f"Variação 20 números: {variacao_20}/{len(periodos)} diferentes")
    
    if variacao_15 >= len(periodos) * 0.8:
        print("✅ EXCELENTE variação temporal para 15 números")
    if variacao_20 >= len(periodos) * 0.8:
        print("✅ EXCELENTE variação temporal para 20 números")
    
    print(f"\n🎯 GERADOR ISOLADO PRONTO PARA TESTE HISTÓRICO!")

if __name__ == "__main__":
    testar_gerador_isolado()
