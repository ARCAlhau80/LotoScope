#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ESTRATÉGIAS ADAPTATIVAS DE SOBREPOSIÇÃO

Sistema inteligente que aplica diferentes estratégias de sobreposição
baseado na quantidade de números escolhida:

• 15-16 números: ALTA sobreposição (12-15 números comuns)
• 17-18 números: MÉDIA sobreposição (9-12 números comuns)  
• 19-20 números: BAIXA sobreposição (8-11 números comuns)

Autor: AR CALHAU
Data: 25 de Agosto de 2025
"""

import random
from typing import List, Dict, Any

class EstrategiaAltaSobreposicao:
    """Estratégia de alta sobreposição para 15-16 números"""
    
    def __init__(self):
        self.min_comum = 12
        self.max_comum = 15
        self.historico_combinacoes = []
        self.nome = "Alta Sobreposição"
        
    def resetar_historico(self):
        """Reseta o histórico de combinações"""
        self.historico_combinacoes = []
    
    def aplicar_alta_sobreposicao(self, nova_combinacao: List[int], combinacoes_existentes: List[List[int]]) -> List[int]:
        """
        Aplica estratégia de alta sobreposição
        Garante que tenha entre 12-15 números comuns com combinações existentes
        """
        if not combinacoes_existentes:
            return nova_combinacao
            
        # Pega a última combinação como referência
        referencia = combinacoes_existentes[-1]
        
        # Calcula sobreposição atual
        sobreposicao_atual = len(set(nova_combinacao) & set(referencia))
        
        if self.min_comum <= sobreposicao_atual <= self.max_comum:
            return nova_combinacao
            
        # Ajusta para ter alta sobreposição
        combinacao_ajustada = nova_combinacao.copy()
        numeros_comuns = list(set(nova_combinacao) & set(referencia))
        numeros_referencia = [n for n in referencia if n not in numeros_comuns]
        numeros_nao_comuns = [n for n in nova_combinacao if n not in numeros_comuns]
        
        target_comum = random.randint(int(self.min_comum), int(self.max_comum))
        
        if len(numeros_comuns) < target_comum:
            # Precisa adicionar mais números da referência
            adicionar = target_comum - len(numeros_comuns)
            if len(numeros_referencia) >= adicionar:
                for i in range(adicionar):
                    if numeros_referencia and numeros_nao_comuns:
                        idx_remove = random.randint(int(0), int(len(numeros_nao_comuns)) - 1)
                        idx_add = random.randint(int(0), int(len(numeros_referencia)) - 1)
                        
                        numero_remover = numeros_nao_comuns.pop(idx_remove)
                        numero_adicionar = numeros_referencia.pop(idx_add)
                        
                        combinacao_ajustada.remove(numero_remover)
                        combinacao_ajustada.append(numero_adicionar)
                        
        elif len(numeros_comuns) > target_comum:
            # Precisa remover alguns números comuns
            remover = len(numeros_comuns) - target_comum
            for i in range(remover):
                if numeros_comuns:
                    numero_remover = random.choice(numeros_comuns)
                    numeros_comuns.remove(numero_remover)
                    
                    # Substitui por número não usado
                    numeros_disponiveis = [n for n in range(1, 26) if n not in combinacao_ajustada]
                    if numeros_disponiveis:
                        numero_adicionar = random.choice(numeros_disponiveis)
                        combinacao_ajustada.remove(numero_remover)
                        combinacao_ajustada.append(numero_adicionar)
        
        return sorted(combinacao_ajustada)
    
    def gerar_sequencia_alta_sobreposicao(self, gerador_base, quantidade: int) -> List[List[int]]:
        """Gera sequência de combinações com alta sobreposição"""
        combinacoes = []
        
        for i in range(quantidade):
            combinacao = gerador_base()
            
            if i > 0:
                combinacao = self.aplicar_alta_sobreposicao(combinacao, combinacoes)
                
            combinacoes.append(combinacao)
            
        return combinacoes
    
    def validar_sobreposicao(self, combinacoes: List[List[int]]) -> Dict[str, Any]:
        """Valida se as combinações seguem a estratégia de alta sobreposição"""
        if len(combinacoes) < 2:
            return {"status": "Insuficiente", "media_sobreposicao": 0, "conformidade": "N/A"}
            
        sobreposicoes = []
        
        for i in range(1, len(combinacoes)):
            sobreposicao = len(set(combinacoes[i]) & set(combinacoes[i-1]))
            sobreposicoes.append(sobreposicao)
        
        media = sum(sobreposicoes) / len(sobreposicoes)
        dentro_range = sum(1 for s in sobreposicoes if self.min_comum <= s <= self.max_comum)
        conformidade = (dentro_range / len(sobreposicoes)) * 100
        
        status = "✅ Conforme" if conformidade >= 80 else "⚠️ Parcial" if conformidade >= 50 else "❌ Fora do padrão"
        
        return {
            "status": status,
            "media_sobreposicao": media,
            "conformidade": f"{conformidade:.1f}%",
            "range_esperado": f"{self.min_comum}-{self.max_comum}",
            "sobreposicoes": sobreposicoes
        }

class EstrategiaMediaSobreposicao:
    """Estratégia de média sobreposição para 17-18 números"""
    
    def __init__(self):
        self.min_comum = 9
        self.max_comum = 12
        self.historico_combinacoes = []
        self.nome = "Média Sobreposição"
        
    def resetar_historico(self):
        """Reseta o histórico de combinações"""
        self.historico_combinacoes = []
    
    def aplicar_media_sobreposicao(self, nova_combinacao: List[int], combinacoes_existentes: List[List[int]]) -> List[int]:
        """
        Aplica estratégia de média sobreposição
        Garante que tenha entre 9-12 números comuns com combinações existentes
        """
        if not combinacoes_existentes:
            return nova_combinacao
            
        # Pega a última combinação como referência
        referencia = combinacoes_existentes[-1]
        
        # Calcula sobreposição atual
        sobreposicao_atual = len(set(nova_combinacao) & set(referencia))
        
        if self.min_comum <= sobreposicao_atual <= self.max_comum:
            return nova_combinacao
            
        # Ajusta para ter média sobreposição
        combinacao_ajustada = nova_combinacao.copy()
        numeros_comuns = list(set(nova_combinacao) & set(referencia))
        numeros_referencia = [n for n in referencia if n not in numeros_comuns]
        numeros_nao_comuns = [n for n in nova_combinacao if n not in numeros_comuns]
        
        target_comum = random.randint(int(self.min_comum), int(self.max_comum))
        
        if len(numeros_comuns) < target_comum:
            # Precisa adicionar mais números da referência
            adicionar = target_comum - len(numeros_comuns)
            if len(numeros_referencia) >= adicionar:
                for i in range(adicionar):
                    if numeros_referencia and numeros_nao_comuns:
                        idx_remove = random.randint(int(0), int(len(numeros_nao_comuns)) - 1)
                        idx_add = random.randint(int(0), int(len(numeros_referencia)) - 1)
                        
                        numero_remover = numeros_nao_comuns.pop(idx_remove)
                        numero_adicionar = numeros_referencia.pop(idx_add)
                        
                        combinacao_ajustada.remove(numero_remover)
                        combinacao_ajustada.append(numero_adicionar)
                        
        elif len(numeros_comuns) > target_comum:
            # Precisa remover alguns números comuns
            remover = len(numeros_comuns) - target_comum
            for i in range(remover):
                if numeros_comuns:
                    numero_remover = random.choice(numeros_comuns)
                    numeros_comuns.remove(numero_remover)
                    
                    # Substitui por número não usado
                    numeros_disponiveis = [n for n in range(1, 26) if n not in combinacao_ajustada]
                    if numeros_disponiveis:
                        numero_adicionar = random.choice(numeros_disponiveis)
                        combinacao_ajustada.remove(numero_remover)
                        combinacao_ajustada.append(numero_adicionar)
        
        return sorted(combinacao_ajustada)
    
    def gerar_sequencia_media_sobreposicao(self, gerador_base, quantidade: int) -> List[List[int]]:
        """Gera sequência de combinações com média sobreposição"""
        combinacoes = []
        
        for i in range(quantidade):
            combinacao = gerador_base()
            
            if i > 0:
                combinacao = self.aplicar_media_sobreposicao(combinacao, combinacoes)
                
            combinacoes.append(combinacao)
            
        return combinacoes
    
    def validar_sobreposicao(self, combinacoes: List[List[int]]) -> Dict[str, Any]:
        """Valida se as combinações seguem a estratégia de média sobreposição"""
        if len(combinacoes) < 2:
            return {"status": "Insuficiente", "media_sobreposicao": 0, "conformidade": "N/A"}
            
        sobreposicoes = []
        
        for i in range(1, len(combinacoes)):
            sobreposicao = len(set(combinacoes[i]) & set(combinacoes[i-1]))
            sobreposicoes.append(sobreposicao)
        
        media = sum(sobreposicoes) / len(sobreposicoes)
        dentro_range = sum(1 for s in sobreposicoes if self.min_comum <= s <= self.max_comum)
        conformidade = (dentro_range / len(sobreposicoes)) * 100
        
        status = "✅ Conforme" if conformidade >= 80 else "⚠️ Parcial" if conformidade >= 50 else "❌ Fora do padrão"
        
        return {
            "status": status,
            "media_sobreposicao": media,
            "conformidade": f"{conformidade:.1f}%",
            "range_esperado": f"{self.min_comum}-{self.max_comum}",
            "sobreposicoes": sobreposicoes
        }

def selecionar_estrategia_por_quantidade(qtd_numeros: int):
    """
    Seleciona a estratégia de sobreposição baseada na quantidade de números
    
    15-16 números: ALTA sobreposição (12-15 comuns)
    17-18 números: MÉDIA sobreposição (9-12 comuns)
    19-20 números: BAIXA sobreposição (8-11 comuns)
    """
    if qtd_numeros <= 16:
        return EstrategiaAltaSobreposicao(), "ALTA"
    elif qtd_numeros <= 18:
        return EstrategiaMediaSobreposicao(), "MÉDIA"
    else:
        # Importa a estratégia baixa existente
        from estrategia_baixa_sobreposicao import EstrategiaBaixaSobreposicao
        return EstrategiaBaixaSobreposicao(), "BAIXA"
