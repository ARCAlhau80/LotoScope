#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 INTEGRADOR DE PADRÕES OCULTOS PARA GERADORES
================================================
Este módulo fornece funções para integrar os padrões ocultos
descobertos na tabela COMBINACOES_LOTOFACIL20_COMPLETO nos
geradores existentes (7.9, 7.10, 7.11, 21, etc).

Uso:
    from integracao_padroes_ocultos import PadroesOcultosIntegrador
    
    integrador = PadroesOcultosIntegrador()
    
    # Obter números recomendados
    numeros = integrador.obter_numeros_prioritarios(15)
    
    # Aplicar padrões a uma combinação
    combo_melhorada = integrador.melhorar_combinacao(combo_original)
    
    # Filtrar combinações usando padrões
    combos_filtradas = integrador.filtrar_por_padroes(lista_combos)

Autor: LotoScope
Data: 20/01/2026
"""

import os
import json
from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field
import random


@dataclass
class PadroesOcultosIntegrador:
    """
    Integrador de padrões ocultos para uso nos geradores.
    
    Carrega os padrões descobertos e fornece métodos para
    aplicá-los na geração de combinações.
    """
    
    # Padrões carregados
    padroes: Dict = field(default_factory=dict)
    
    # Cache de dados processados
    numeros_vencedores: Dict[int, float] = field(default_factory=dict)
    pares_recomendados: List[Tuple[int, int]] = field(default_factory=list)
    trios_recomendados: List[Tuple[int, int, int]] = field(default_factory=list)
    caracteristicas_ideais: Dict[str, float] = field(default_factory=dict)
    melhores_por_posicao: Dict[int, int] = field(default_factory=dict)
    
    # Flag de carregamento
    carregado: bool = False
    
    def __post_init__(self):
        """Carrega padrões automaticamente."""
        self.carregar_padroes()
    
    def carregar_padroes(self, arquivo: str = None) -> bool:
        """
        Carrega os padrões ocultos de um arquivo JSON.
        
        Args:
            arquivo: Caminho do arquivo. Se None, busca o mais recente.
            
        Returns:
            bool: True se carregou com sucesso
        """
        try:
            # Diretório dos analisadores
            diretorio = os.path.dirname(os.path.abspath(__file__))
            
            if arquivo is None:
                # Buscar arquivo mais recente
                arquivos = [f for f in os.listdir(diretorio) 
                           if f.startswith('padroes_ocultos_') and f.endswith('.json')]
                if not arquivos:
                    print("⚠️ Nenhum arquivo de padrões encontrado")
                    return False
                arquivo = sorted(arquivos)[-1]
            
            caminho = os.path.join(diretorio, arquivo)
            
            if not os.path.exists(caminho):
                print(f"⚠️ Arquivo não encontrado: {caminho}")
                return False
            
            with open(caminho, 'r', encoding='utf-8') as f:
                self.padroes = json.load(f)
            
            # Processar dados
            self._processar_padroes()
            
            self.carregado = True
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar padrões: {e}")
            return False
    
    def _processar_padroes(self):
        """Processa os padrões carregados para uso rápido."""
        # Números vencedores
        for num_str, freq in self.padroes.get('numeros_vencedores', {}).items():
            self.numeros_vencedores[int(num_str)] = freq
        
        # Pares recomendados
        for par in self.padroes.get('padroes_pares', []):
            nums = par.get('numeros', [])
            if len(nums) >= 2:
                self.pares_recomendados.append(tuple(nums[:2]))
        
        # Trios recomendados
        for trio in self.padroes.get('padroes_trios', []):
            nums = trio.get('numeros', [])
            if len(nums) >= 3:
                self.trios_recomendados.append(tuple(nums[:3]))
        
        # Características ideais
        for carac in self.padroes.get('padroes_caracteristicas', []):
            desc = carac.get('descricao', '')
            if 'QtdePares' in desc:
                self.caracteristicas_ideais['pares'] = carac.get('acertos_medios', 10)
            elif 'QtdeImpares' in desc:
                self.caracteristicas_ideais['impares'] = carac.get('acertos_medios', 10)
            elif 'QtdePrimos' in desc:
                self.caracteristicas_ideais['primos'] = carac.get('acertos_medios', 7)
            elif 'QtdeConsecutivos' in desc:
                self.caracteristicas_ideais['consecutivos'] = carac.get('acertos_medios', 15)
            elif 'SomaTotal' in desc:
                self.caracteristicas_ideais['soma'] = carac.get('acertos_medios', 260)
        
        # Melhores por posição
        for pos_info in self.padroes.get('padroes_posicionais', []):
            desc = pos_info.get('descricao', '')
            nums = pos_info.get('numeros', [])
            if nums and 'Posição N' in desc:
                try:
                    pos = int(desc.split('N')[1].split(':')[0])
                    self.melhores_por_posicao[pos] = nums[0]
                except:
                    pass
    
    def obter_numeros_prioritarios(self, quantidade: int = 15) -> List[int]:
        """
        Obtém os números mais recomendados baseado nos padrões.
        
        Args:
            quantidade: Quantidade de números a retornar
            
        Returns:
            Lista de números ordenados por prioridade
        """
        if not self.carregado:
            self.carregar_padroes()
        
        scores = defaultdict(float)
        
        # Score baseado em frequência nas vencedoras
        for num, freq in self.numeros_vencedores.items():
            scores[num] += freq * 10
        
        # Score baseado em trios (mais peso)
        for trio in self.trios_recomendados[:10]:
            for num in trio:
                scores[num] += 3
        
        # Score baseado em posicionais
        for pos, num in self.melhores_por_posicao.items():
            scores[num] += 1
        
        # Ordenar e retornar
        sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [num for num, score in sorted_nums[:quantidade]]
    
    def obter_pares_prioritarios(self, quantidade: int = 10) -> List[Tuple[int, int]]:
        """Retorna os pares mais recomendados."""
        if not self.carregado:
            self.carregar_padroes()
        return self.pares_recomendados[:quantidade]
    
    def obter_trios_prioritarios(self, quantidade: int = 5) -> List[Tuple[int, int, int]]:
        """Retorna os trios mais recomendados."""
        if not self.carregado:
            self.carregar_padroes()
        return self.trios_recomendados[:quantidade]
    
    def obter_caracteristicas_ideais(self) -> Dict[str, float]:
        """Retorna as características ideais descobertas."""
        if not self.carregado:
            self.carregar_padroes()
        return self.caracteristicas_ideais.copy()
    
    def obter_melhores_por_posicao(self) -> Dict[int, int]:
        """Retorna os melhores números por posição."""
        if not self.carregado:
            self.carregar_padroes()
        return self.melhores_por_posicao.copy()
    
    def calcular_score_combinacao(self, combinacao: List[int]) -> float:
        """
        Calcula um score para uma combinação baseado nos padrões.
        
        Args:
            combinacao: Lista de 15 ou 20 números
            
        Returns:
            Score (quanto maior, melhor)
        """
        if not self.carregado:
            self.carregar_padroes()
        
        score = 0.0
        nums_set = set(combinacao)
        nums_sorted = sorted(combinacao)
        
        # 1. Score por números vencedores
        for num in combinacao:
            score += self.numeros_vencedores.get(num, 0) * 10
        
        # 2. Score por trios presentes
        for trio in self.trios_recomendados[:20]:
            if all(n in nums_set for n in trio):
                score += 5
        
        # 3. Score por pares presentes
        for par in self.pares_recomendados[:30]:
            if all(n in nums_set for n in par):
                score += 2
        
        # 4. Score por características (se aplicável para 15 números)
        if len(combinacao) == 15:
            # Pares
            qtd_pares = len([n for n in combinacao if n % 2 == 0])
            ideal_pares = self.caracteristicas_ideais.get('pares', 7)
            score -= abs(qtd_pares - ideal_pares) * 0.5
            
            # Soma
            soma = sum(combinacao)
            ideal_soma = self.caracteristicas_ideais.get('soma', 200)
            score -= abs(soma - ideal_soma) * 0.01
        
        return score
    
    def melhorar_combinacao(self, combinacao: List[int], max_trocas: int = 3) -> List[int]:
        """
        Tenta melhorar uma combinação usando os padrões descobertos.
        
        Args:
            combinacao: Combinação original
            max_trocas: Máximo de números a trocar
            
        Returns:
            Combinação melhorada
        """
        if not self.carregado:
            self.carregar_padroes()
        
        melhorada = list(combinacao)
        nums_set = set(melhorada)
        
        # Obter números prioritários não presentes
        prioritarios = [n for n in self.obter_numeros_prioritarios(25) if n not in nums_set]
        
        # Identificar números fracos (não prioritários)
        scores_nums = {n: self.numeros_vencedores.get(n, 0) for n in melhorada}
        fracos = sorted(scores_nums.items(), key=lambda x: x[1])[:max_trocas]
        
        # Trocar fracos por prioritários
        for (fraco, _), prioritario in zip(fracos, prioritarios[:max_trocas]):
            if prioritario:
                idx = melhorada.index(fraco)
                melhorada[idx] = prioritario
        
        return sorted(melhorada)
    
    def filtrar_por_padroes(self, combinacoes: List[List[int]], 
                           top_percentual: float = 0.3) -> List[List[int]]:
        """
        Filtra combinações mantendo apenas as melhores segundo os padrões.
        
        Args:
            combinacoes: Lista de combinações
            top_percentual: Percentual das melhores a manter (0.3 = 30%)
            
        Returns:
            Lista filtrada de combinações
        """
        if not combinacoes:
            return []
        
        # Calcular score de cada combinação
        scored = [(combo, self.calcular_score_combinacao(combo)) for combo in combinacoes]
        
        # Ordenar por score
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Manter top percentual
        quantidade = max(1, int(len(scored) * top_percentual))
        return [combo for combo, score in scored[:quantidade]]
    
    def gerar_combinacao_otimizada(self, tamanho: int = 15) -> List[int]:
        """
        Gera uma combinação otimizada usando os padrões descobertos.
        
        Args:
            tamanho: Quantidade de números (15 ou 20)
            
        Returns:
            Combinação gerada
        """
        if not self.carregado:
            self.carregar_padroes()
        
        combinacao = set()
        
        # 1. Adicionar números de um trio recomendado
        if self.trios_recomendados:
            trio = random.choice(self.trios_recomendados[:5])
            combinacao.update(trio)
        
        # 2. Completar com números prioritários
        prioritarios = self.obter_numeros_prioritarios(25)
        for num in prioritarios:
            if len(combinacao) >= tamanho:
                break
            combinacao.add(num)
        
        # 3. Se ainda falta, completar aleatoriamente
        while len(combinacao) < tamanho:
            num = random.randint(1, 25)
            if num not in combinacao:
                combinacao.add(num)
        
        return sorted(list(combinacao))[:tamanho]
    
    def exibir_resumo_padroes(self):
        """Exibe um resumo dos padrões carregados."""
        if not self.carregado:
            self.carregar_padroes()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS PADRÕES OCULTOS CARREGADOS")
        print("=" * 60)
        
        print(f"\n🏆 Top 10 Números Vencedores:")
        top_nums = sorted(self.numeros_vencedores.items(), key=lambda x: x[1], reverse=True)[:10]
        for num, freq in top_nums:
            print(f"   Número {num:2d}: {freq*100:.1f}%")
        
        print(f"\n🎲 Top 5 Trios Recomendados:")
        for trio in self.trios_recomendados[:5]:
            print(f"   {trio[0]:2d} - {trio[1]:2d} - {trio[2]:2d}")
        
        print(f"\n📈 Características Ideais:")
        for carac, valor in self.caracteristicas_ideais.items():
            print(f"   {carac}: {valor:.1f}")
        
        print("\n" + "=" * 60)


# Instância global para uso rápido
_integrador_global = None

def obter_integrador() -> PadroesOcultosIntegrador:
    """Obtém instância global do integrador."""
    global _integrador_global
    if _integrador_global is None:
        _integrador_global = PadroesOcultosIntegrador()
    return _integrador_global


def obter_numeros_padroes_ocultos(quantidade: int = 15) -> List[int]:
    """Função de conveniência para obter números prioritários."""
    return obter_integrador().obter_numeros_prioritarios(quantidade)


def obter_trios_padroes_ocultos(quantidade: int = 5) -> List[Tuple[int, int, int]]:
    """Função de conveniência para obter trios prioritários."""
    return obter_integrador().obter_trios_prioritarios(quantidade)


def calcular_score_padroes(combinacao: List[int]) -> float:
    """Função de conveniência para calcular score de uma combinação."""
    return obter_integrador().calcular_score_combinacao(combinacao)


def filtrar_por_padroes_ocultos(combinacoes: List[List[int]], 
                                 top_percentual: float = 0.3) -> List[List[int]]:
    """Função de conveniência para filtrar combinações."""
    return obter_integrador().filtrar_por_padroes(combinacoes, top_percentual)


if __name__ == "__main__":
    # Teste
    integrador = PadroesOcultosIntegrador()
    integrador.exibir_resumo_padroes()
    
    print("\n🎯 Combinação Otimizada Gerada:")
    combo = integrador.gerar_combinacao_otimizada(15)
    print(f"   {combo}")
    print(f"   Score: {integrador.calcular_score_combinacao(combo):.2f}")
    
    input("\n⏸️ Pressione ENTER para sair...")
