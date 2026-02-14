#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔬 MÓDULO DE INTEGRAÇÃO UNIVERSAL - DESCOBERTAS COMPARAÇÃO
Módulo que qualquer sistema pode importar para usar as descobertas
dos campos de comparação menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
"""

class IntegracaoDescobertasComparacao:
    """Classe utilitária para integrar descobertas em qualquer sistema"""
    
    def __init__(self):
        self.correlacoes = {
            'menor_soma': -0.652,
            'maior_soma': 0.648,
            'igual_amplitude': 0.183
        }
        
        self.estados_extremos = {
            (15,0,0): {'proximo': (0,15,0), 'prob': 0.182},
            (0,15,0): {'proximo': (15,0,0), 'prob': 0.195},
            (0,14,1): {'proximo': (13,0,2), 'prob': 0.098},
            (14,0,1): {'proximo': (0,14,1), 'prob': 0.115}
        }
    
    def estimar_soma_por_estado(self, menor: int, maior: int, igual: int) -> float:
        """Estima soma dos números baseado no estado de comparação"""
        soma_media = 270
        ajuste_menor = (menor - 5.9) * -8
        ajuste_maior = (maior - 5.94) * 8
        return max(150, min(400, soma_media + ajuste_menor + ajuste_maior))
    
    def prever_proximo_estado(self, estado_atual: tuple) -> tuple:
        """Prevê próximo estado baseado nas descobertas"""
        if estado_atual in self.estados_extremos:
            return self.estados_extremos[estado_atual]['proximo']
        
        # Lógica de predição baseada em correlações
        menor, maior, igual = estado_atual
        soma_atual = self.estimar_soma_por_estado(menor, maior, igual)
        
        if soma_atual < 240:  # Soma baixa -> números devem subir
            return (max(0, menor-1), min(15, maior+2), igual)
        elif soma_atual > 300:  # Soma alta -> números devem descer  
            return (min(15, menor+2), max(0, maior-1), igual)
        else:
            return estado_atual  # Manter estável
    
    def calcular_confianca_predicao(self, estado_atual: tuple) -> float:
        """Calcula confiança da predição baseada no estado"""
        if estado_atual in self.estados_extremos:
            return self.estados_extremos[estado_atual]['prob'] * 100
        return 25.0  # Confiança base para outros estados
    
    def eh_momento_inversao(self, estado_atual: tuple) -> bool:
        """Verifica se é momento provável de inversão"""
        menor, maior, igual = estado_atual
        return menor >= 12 or maior >= 12  # Estados extremos tendem a inverter

# Função utilitária para uso direto

    def calcular_campos_comparacao_posicao_por_posicao(self, concurso_anterior: list, concurso_atual: list) -> tuple:
        """
        Calcula campos de comparação POSIÇÃO POR POSIÇÃO - MÉTODO CORRETO VALIDADO
        
        Args:
            concurso_anterior: Lista dos 15 números do concurso anterior (ordenados)
            concurso_atual: Lista dos 15 números do concurso atual (ordenados)
        
        Returns:
            Tuple (menor_que_anterior, maior_que_anterior, igual_ao_anterior)
        """
        if len(concurso_anterior) != 15 or len(concurso_atual) != 15:
            return (5, 5, 5)  # Fallback em caso de erro
        
        menor_que_anterior = 0
        maior_que_anterior = 0
        igual_ao_anterior = 0
        
        for i in range(15):
            num_anterior = concurso_anterior[i]
            num_atual = concurso_atual[i]
            
            if num_atual < num_anterior:
                menor_que_anterior += 1
            elif num_atual > num_anterior:
                maior_que_anterior += 1
            else:
                igual_ao_anterior += 1
        
        return (menor_que_anterior, maior_que_anterior, igual_ao_anterior)
    
    def exemplo_validado_3504_3505(self) -> tuple:
        """Exemplo validado que retorna (11, 0, 4)"""
        concurso_3504 = [1, 2, 4, 6, 7, 9, 10, 12, 15, 16, 17, 21, 22, 23, 25]
        concurso_3505 = [1, 2, 3, 4, 6, 7, 8, 9, 11, 14, 16, 20, 21, 23, 25]
        return self.calcular_campos_comparacao_posicao_por_posicao(concurso_3504, concurso_3505)


def aplicar_descobertas_comparacao(objeto_sistema):
    """Aplica descobertas a qualquer objeto/sistema"""
    integrador = IntegracaoDescobertasComparacao()
    
    # Injetar métodos úteis
    objeto_sistema.descobertas_comparacao = integrador
    objeto_sistema.estimar_soma_por_estado = integrador.estimar_soma_por_estado
    objeto_sistema.prever_proximo_estado = integrador.prever_proximo_estado
    objeto_sistema.calcular_confianca_predicao = integrador.calcular_confianca_predicao
    objeto_sistema.eh_momento_inversao = integrador.eh_momento_inversao
    
    return objeto_sistema
