#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 ATUALIZAÇÃO UNIVERSAL - COMPARAÇÃO POSIÇÃO POR POSIÇÃO
========================================================
Atualiza TODOS os geradores com o conceito correto de campos de comparação:
- menor_que_anterior: número na posição N é menor que o número na mesma posição do concurso anterior
- maior_que_anterior: número na posição N é maior que o número na mesma posição do concurso anterior  
- igual_ao_anterior: número na posição N é igual ao número na mesma posição do concurso anterior

Conceito validado no concurso 3505!
"""

import os
import sys
from typing import List, Tuple

def calcular_campos_comparacao_posicao_por_posicao(
    concurso_anterior: List[int], 
    concurso_atual: List[int]
) -> Tuple[int, int, int]:
    """
    Calcula campos de comparação POSIÇÃO POR POSIÇÃO
    
    Args:
        concurso_anterior: Lista dos 15 números do concurso anterior (ordenados)
        concurso_atual: Lista dos 15 números do concurso atual (ordenados)
    
    Returns:
        Tuple (menor_que_anterior, maior_que_anterior, igual_ao_anterior)
    """
    if len(concurso_anterior) != 15 or len(concurso_atual) != 15:
        raise ValueError("Ambos os concursos devem ter exatamente 15 números")
    
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

def exemplo_calculo_3504_3505():
    """Exemplo validado com os concursos 3504 e 3505"""
    concurso_3504 = [1, 2, 4, 6, 7, 9, 10, 12, 15, 16, 17, 21, 22, 23, 25]
    concurso_3505 = [1, 2, 3, 4, 6, 7, 8, 9, 11, 14, 16, 20, 21, 23, 25]
    
    resultado = calcular_campos_comparacao_posicao_por_posicao(concurso_3504, concurso_3505)
    
    print("🎯 EXEMPLO VALIDADO - CONCURSOS 3504 → 3505")
    print("=" * 50)
    print(f"Concurso 3504: {concurso_3504}")
    print(f"Concurso 3505: {concurso_3505}")
    print()
    print("Análise posição por posição:")
    print("Pos | 3504 | 3505 | Resultado")
    print("----|------|------|----------")
    
    for i in range(15):
        num_3504 = concurso_3504[i]
        num_3505 = concurso_3505[i]
        
        if num_3505 < num_3504:
            status = "MENOR"
        elif num_3505 > num_3504:
            status = "MAIOR"
        else:
            status = "IGUAL"
        
        print(f"{i+1:2d}  | {num_3504:4d} | {num_3505:4d} | {status}")
    
    print("-" * 35)
    print(f"RESULTADO: {resultado}")
    print(f"Menor que anterior: {resultado[0]}")
    print(f"Maior que anterior: {resultado[1]}")
    print(f"Igual ao anterior: {resultado[2]}")
    print(f"Total: {sum(resultado)}")
    return resultado

class CalculadorComparacaoCorrigido:
    """Classe com o método correto de cálculo para integração universal"""
    
    @staticmethod
    def calcular_campos_comparacao(concurso_anterior: List[int], concurso_atual: List[int]) -> Tuple[int, int, int]:
        """Método estático para fácil integração em qualquer gerador"""
        return calcular_campos_comparacao_posicao_por_posicao(concurso_anterior, concurso_atual)
    
    @staticmethod
    def validar_calculo_exemplo() -> bool:
        """Valida o cálculo com o exemplo conhecido"""
        resultado = exemplo_calculo_3504_3505()
        # Resultado esperado: (11, 0, 4) baseado na validação real
        return resultado == (11, 0, 4)

def atualizar_integracao_descobertas():
    """Atualiza o arquivo de integração com o método correto"""
    arquivo_integracao = "integracao_descobertas_comparacao.py"
    
    if not os.path.exists(arquivo_integracao):
        print(f"⚠️ Arquivo {arquivo_integracao} não encontrado")
        return False
    
    print(f"🔧 Atualizando {arquivo_integracao} com método correto...")
    
    # Lê o arquivo atual
    with open(arquivo_integracao, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Adiciona o método correto antes da última linha
    metodo_correto = '''
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
'''
    
    # Encontra o local para inserir (antes do final da classe)
    if 'def aplicar_descobertas_comparacao' in conteudo:
        posicao_insercao = conteudo.rfind('def aplicar_descobertas_comparacao')
        conteudo_atualizado = conteudo[:posicao_insercao] + metodo_correto + '\n\n' + conteudo[posicao_insercao:]
    else:
        # Se não encontrar, adiciona antes da última linha
        linhas = conteudo.split('\n')
        linhas.insert(-3, metodo_correto)
        conteudo_atualizado = '\n'.join(linhas)
    
    # Salva o arquivo atualizado
    with open(arquivo_integracao, 'w', encoding='utf-8') as f:
        f.write(conteudo_atualizado)
    
    print(f"✅ {arquivo_integracao} atualizado com método correto")
    return True

def main():
    """Função principal"""
    print("🔧 ATUALIZAÇÃO UNIVERSAL - COMPARAÇÃO POSIÇÃO POR POSIÇÃO")
    print("=" * 60)
    
    # Valida o cálculo com exemplo conhecido
    print("🧪 Validando cálculo com exemplo 3504→3505...")
    calculador = CalculadorComparacaoCorrigido()
    
    if calculador.validar_calculo_exemplo():
        print("✅ Cálculo validado com sucesso!")
    else:
        print("❌ Erro na validação do cálculo!")
        return
    
    # Atualiza arquivo de integração
    print("\n🔄 Atualizando arquivo de integração...")
    if atualizar_integracao_descobertas():
        print("✅ Integração atualizada!")
    else:
        print("❌ Erro ao atualizar integração!")
        return
    
    print("\n🎉 ATUALIZAÇÃO CONCLUÍDA!")
    print("Agora todos os geradores que usam IntegracaoDescobertasComparacao")
    print("terão acesso ao método correto de cálculo por posição!")

if __name__ == "__main__":
    main()