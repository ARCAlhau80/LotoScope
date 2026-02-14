#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ESTRATÉGIA DOS 7 PARÂMETROS DINÂMICOS
=========================================
Integração do analisador dinâmico no sistema de auto-treino
"""

from analisador_parametros_dinamicos import AnalisadorParametrosDinamicos
import random
import time
from datetime import datetime
from typing import List, Dict, Tuple

class EstrategiaParametrosDinamicos:
    """
    Estratégia que usa análise dinâmica de histórico para otimizar
    os 7 parâmetros críticos identificados
    """
    
    def __init__(self):
        self.nome = "7_Parametros_Dinamicos"
        self.analisador = AnalisadorParametrosDinamicos()
        self.parametros_atuais = {}
        self.historico_predicoes = []
        self.ultima_analise = None
        
        # Estatísticas da estratégia
        self.stats = {
            'tentativas': 0,
            'sucessos': 0,
            'melhor_resultado': 0,
            'tempo_total': 0,
            'parametros_usados': []
        }
    
    def carregar_dados_historicos(self, dados_historicos: List[Dict] = None):
        """Carrega dados históricos para análise"""
        if dados_historicos:
            # Adapta dados para formato do analisador
            dados_adaptados = []
            for concurso in dados_historicos:
                if 'numeros' in concurso:
                    dados_adaptados.append(self._adaptar_concurso(concurso))
            
            self.analisador.carregar_historico(dados_adaptados)
        else:
            # Usa dados simulados
            self.analisador.carregar_historico()
        
        print(f"[ESTRATEGIA] Dados carregados: {len(self.analisador.historico_completo)} concursos")
    
    def _adaptar_concurso(self, concurso: Dict) -> Dict:
        """Adapta formato do concurso para o analisador"""
        numeros = concurso['numeros']
        
        # Simula cálculo dos parâmetros (em produção, viria do banco)
        return {
            'concurso': concurso.get('concurso', 0),
            'numeros': numeros,
            'n1': numeros[0] if len(numeros) > 0 else 1,
            'n15': numeros[-1] if len(numeros) > 0 else 25,
            'maior_que_ultimo': random.randint(5, 12),  # Simulated
            'menor_que_ultimo': random.randint(3, 10),  # Simulated
            'qtde_6_a_25': sum(1 for n in numeros if 6 <= n <= 25),
            'qtde_6_a_20': sum(1 for n in numeros if 6 <= n <= 20),
            'melhores_posicoes': random.randint(4, 10),  # Simulated
            'soma_total': sum(numeros)
        }
    
    def atualizar_parametros(self, forcar_atualizacao: bool = False):
        """Atualiza parâmetros baseado na análise mais recente"""
        agora = time.time()
        
        # Atualiza a cada 5 minutos ou se forçado
        if (not self.ultima_analise or 
            agora - self.ultima_analise > 300 or 
            forcar_atualizacao):
            
            print(f"[DINAMICOS] Atualizando parametros...")
            
            # Executa análise dinâmica
            self.analisador.analisar_todas_janelas()
            self.parametros_atuais = self.analisador.calcular_parametros_otimos()
            
            # Registra predição
            self.historico_predicoes.append({
                'timestamp': datetime.now().isoformat(),
                'parametros': self.parametros_atuais.copy()
            })
            
            self.ultima_analise = agora
            
            print(f"[ATUALIZADOS] Novos parametros:")
            for param, valor in self.parametros_atuais.items():
                print(f"   {param}: {valor}")
    
    def gerar_combinacao(self, concurso_alvo: int = None) -> List[int]:
        """
        Gera combinação usando os parâmetros dinâmicos otimizados
        """
        inicio = time.time()
        
        # Atualiza parâmetros se necessário
        self.atualizar_parametros()
        
        if not self.parametros_atuais:
            # Fallback para valores padrão
            self.parametros_atuais = {
                'n1': 2, 'n15': 25, 'maior_que_ultimo': 8,
                'menor_que_ultimo': 6, 'qtde_6_a_25': 13,
                'qtde_6_a_20': 9, 'melhores_posicoes': 7
            }
        
        # Gera combinação respeitando os 7 parâmetros
        combinacao = self._gerar_com_parametros()
        
        # Atualiza estatísticas
        self.stats['tentativas'] += 1
        self.stats['tempo_total'] += time.time() - inicio
        self.stats['parametros_usados'].append(self.parametros_atuais.copy())
        
        return combinacao
    
    def _gerar_com_parametros(self) -> List[int]:
        """Gera combinação respeitando os 7 parâmetros dinâmicos"""
        
        max_tentativas = 1000
        tentativa = 0
        
        while tentativa < max_tentativas:
            tentativa += 1
            
            # Inicia com N1 e N15 fixos
            combinacao = []
            
            # Parâmetro 1: N1
            n1 = self.parametros_atuais.get('n1', 2)
            combinacao.append(n1)
            
            # Parâmetro 2: N15  
            n15 = self.parametros_atuais.get('n15', 25)
            
            # Gera números intermediários
            numeros_disponiveis = list(range(1, 26))
            numeros_disponiveis.remove(n1)
            if n15 in numeros_disponiveis:
                numeros_disponiveis.remove(n15)
            
            # Seleciona 13 números intermediários
            numeros_intermediarios = random.sample(numeros_disponiveis, 13)
            combinacao.extend(numeros_intermediarios)
            combinacao.append(n15)
            
            combinacao.sort()
            
            # Verifica se atende aos 7 parâmetros
            if self._valida_parametros(combinacao):
                return combinacao
        
        # Se não conseguir gerar respeitando os parâmetros, retorna combinação válida
        return sorted(random.sample(range(1, 26), 15))
    
    def _valida_parametros(self, combinacao: List[int]) -> bool:
        """Valida se combinação atende aos 7 parâmetros dinâmicos"""
        
        # 1. N1
        if combinacao[0] != self.parametros_atuais.get('n1', 2):
            return False
        
        # 2. N15
        if combinacao[-1] != self.parametros_atuais.get('n15', 25):
            return False
        
        # 5. Qtde 6 a 25
        qtde_6_a_25 = sum(1 for n in combinacao if 6 <= n <= 25)
        if qtde_6_a_25 != self.parametros_atuais.get('qtde_6_a_25', 13):
            return False
        
        # 6. Qtde 6 a 20
        qtde_6_a_20 = sum(1 for n in combinacao if 6 <= n <= 20)
        if qtde_6_a_20 != self.parametros_atuais.get('qtde_6_a_20', 9):
            return False
        
        # 7. Melhores posições (simplificado)
        posicoes_otimas = [1, 2, 4, 6, 8, 9, 11, 13, 15, 16, 19, 20, 22, 24, 25]
        melhores_posicoes = sum(1 for i, num in enumerate(combinacao) 
                               if i < len(posicoes_otimas) and num == posicoes_otimas[i])
        
        target_posicoes = self.parametros_atuais.get('melhores_posicoes', 7)
        if abs(melhores_posicoes - target_posicoes) > 2:  # Tolerância de 2
            return False
        
        # Parâmetros 3 e 4 (maior/menor_que_ultimo) seriam validados 
        # com dados do concurso anterior em produção
        
        return True
    
    def avaliar_resultado(self, combinacao: List[int], resultado_esperado: List[int]) -> int:
        """Avalia resultado e atualiza estatísticas"""
        acertos = len(set(combinacao) & set(resultado_esperado))
        
        if acertos > self.stats['melhor_resultado']:
            self.stats['melhor_resultado'] = acertos
        
        if acertos >= 13:  # Consideramos sucesso
            self.stats['sucessos'] += 1
        
        return acertos
    
    def gerar_relatorio(self) -> str:
        """Gera relatório da estratégia"""
        if self.stats['tentativas'] == 0:
            return "Estratégia ainda não foi executada"
        
        taxa_sucesso = (self.stats['sucessos'] / self.stats['tentativas']) * 100
        tempo_medio = self.stats['tempo_total'] / self.stats['tentativas']
        
        relatorio = f"""
RELATORIO - ESTRATEGIA 7 PARAMETROS DINAMICOS
==============================================

ESTATISTICAS:
   - Tentativas: {self.stats['tentativas']:,}
   - Sucessos (>=13 acertos): {self.stats['sucessos']:,}
   - Taxa de sucesso: {taxa_sucesso:.2f}%
   - Melhor resultado: {self.stats['melhor_resultado']} acertos
   - Tempo medio por combinacao: {tempo_medio:.4f}s

PARAMETROS ATUAIS:
"""
        for param, valor in self.parametros_atuais.items():
            relatorio += f"   - {param}: {valor}\n"
        
        relatorio += f"""
HISTORICO DE PREDICOES: {len(self.historico_predicoes)}
ULTIMA ANALISE: {self.ultima_analise or 'Nunca'}

Estrategia otimizada dinamicamente baseada em analise historica
"""
        return relatorio

def testar_estrategia():
    """Função para testar a estratégia"""
    print("[TESTE] ESTRATEGIA 7 PARAMETROS DINAMICOS")
    print("=" * 60)
    
    # Cria estratégia
    estrategia = EstrategiaParametrosDinamicos()
    
    # Carrega dados
    estrategia.carregar_dados_historicos()
    
    # Gera algumas combinações
    print(f"\n[TESTE] Gerando combinacoes...")
    
    for i in range(3):
        print(f"\n--- Combinacao {i+1} ---")
        combinacao = estrategia.gerar_combinacao()
        print(f"Gerada: {combinacao}")
        
        # Simula avaliação
        resultado_simulado = sorted(random.sample(range(1, 26), 15))
        acertos = estrategia.avaliar_resultado(combinacao, resultado_simulado)
        print(f"Acertos simulados: {acertos}/15")
    
    # Mostra relatório
    print(f"\n{estrategia.gerar_relatorio()}")

if __name__ == "__main__":
    testar_estrategia()