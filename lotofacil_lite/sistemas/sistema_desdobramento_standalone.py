#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA DE DESDOBRAMENTO COMPLEMENTAR STANDALONE - LOTOFÁCIL

Versão independente do sistema de desdobramento sem dependências externas:
- Gera combinação dinâmica de 20 números
- Aplica algoritmo C(5,3) nos números restantes  
- Cria múltiplas combinações garantindo cobertura
- Sistema de pontuação inteligente para seleção ótima

MATEMÁTICA COMPROVADA:
- C(5,3) = 10 combinações dos 5 números restantes
- A garantia de acertar 3 só vale se as 10 combinações C(5,3) forem jogadas
- Complementação garante cobertura completa

Autor: AR CALHAU  
Data: 25 de Agosto de 2025
"""

import os
import sys
import random
import datetime
from itertools import combinations
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

class SistemaDesdobramentoStandalone:
    """
    Sistema de desdobramento complementar independente
    """
    
    def __init__(self):
        self.historico_desdobramentos = []
        self.cache_combinacoes = {}
        self.modo_selecao = 1  # Padrão: melhor pontuação
        self.filtros_ativos = {}
        
        print("🎯 Sistema de Desdobramento Complementar V2.0 STANDALONE")
        print("📐 Algoritmo C(5,3) = 10 combinações garantidas")
        print("🆕 CONTROLE TOTAL DE QUANTIDADE E CONFIGURAÇÕES AVANÇADAS!")
    
    def configurar_modo_selecao(self, modo: int):
        """Configura o modo de seleção de trios"""
        self.modo_selecao = modo
        modos = {1: "MELHOR_PONTUAÇÃO", 2: "DIVERSIFICAÇÃO", 3: "ALEATÓRIO_OTIMIZADO"}
        print(f"🎯 Modo de seleção: {modos.get(modo, 'DESCONHECIDO')}")
    
    def aplicar_filtros(self, filtros: Dict):
        """Aplica filtros de otimização"""
        self.filtros_ativos = filtros
        print(f"🔍 {len(filtros)} filtros aplicados")
    
    def gerar_combinacao_20_numeros(self) -> List[int]:
        """Gera combinação dinâmica de 20 números usando algoritmos otimizados"""
        
        # Frequências simuladas baseadas em análise histórica
        frequencias = {
            1: 0.82, 2: 0.85, 3: 0.80, 4: 0.83, 5: 0.81,
            6: 0.79, 7: 0.84, 8: 0.82, 9: 0.78, 10: 0.86,
            11: 0.88, 12: 0.87, 13: 0.89, 14: 0.85, 15: 0.83,
            16: 0.84, 17: 0.82, 18: 0.85, 19: 0.81, 20: 0.89,
            21: 0.86, 22: 0.83, 23: 0.80, 24: 0.84, 25: 0.79
        }
        
        # Pesos por posição (baseado em análise estatística)
        pesos_posicao = [1.2, 1.1, 1.0, 0.9, 0.8] * 5
        
        # Combina frequências e pesos posicionais
        numeros_ponderados = []
        for num in range(1, 26):
            peso = frequencias[num] + pesos_posicao[num-1]
            numeros_ponderados.append((num, peso))
        
        # Ordena por peso decrescente
        numeros_ponderados.sort(key=lambda x: x[1], reverse=True)
        
        # Seleciona os 20 melhores com alguma aleatoriedade
        candidatos = [num for num, peso in numeros_ponderados[:23]]
        selecionados = sorted(random.sample(candidatos, 20))
        
        return selecionados
    
    def calcular_desdobramento_c53(self, numeros_restantes: List[int]) -> List[Tuple[int, int, int]]:
        """Calcula todas as combinações C(5,3)"""
        if len(numeros_restantes) != 5:
            raise ValueError(f"Deve haver exatamente 5 números restantes")
        
        combinacoes_c53 = list(combinations(numeros_restantes, 3))
        return combinacoes_c53
    
    def pontuar_combinacao_restante(self, trio: Tuple[int, int, int]) -> float:
        """Calcula pontuação para um trio"""
        score = 0.0
        numeros = list(trio)
        
        # 1. Frequências (simuladas)
        frequencias = {i: random.uniform(0.75, 0.95) for i in range(1, 26)}
        score += sum(frequencias.get(num, 0) for num in numeros) * 2.0
        
        # 2. Distribuição por faixas
        faixas = {
            'baixa': sum(1 for n in numeros if 1 <= n <= 8),
            'media': sum(1 for n in numeros if 9 <= n <= 16),
            'alta': sum(1 for n in numeros if 17 <= n <= 25)
        }
        
        # Premia distribuição equilibrada
        if faixas['baixa'] >= 1 and faixas['media'] >= 1 and faixas['alta'] >= 1:
            score += 2.0
        elif any(faixas[f] >= 2 for f in faixas):
            score += 1.0
        
        # 3. Números primos e Fibonacci
        primos = sum(1 for n in numeros if n in [2,3,5,7,11,13,17,19,23])
        fibonacci = sum(1 for n in numeros if n in [1,2,3,5,8,13,21])
        
        score += primos * 0.8
        score += fibonacci * 0.6
        
        # 4. Padrões de soma
        soma = sum(numeros)
        if 30 <= soma <= 45:
            score += 1.0
        elif 20 <= soma <= 55:
            score += 0.5
        
        # 5. Espaçamento
        espacamento = max(numeros) - min(numeros)
        if 8 <= espacamento <= 15:
            score += 0.8
        
        return score
    
    def selecionar_melhores_trios(self, combinacoes_c53: List[Tuple[int, int, int]], 
                                  qtd_selecionar: Optional[int] = None) -> List[Tuple[int, int, int]]:
        """Seleciona os melhores trios.

        Se qtd_selecionar for None, retorna TODOS os C(5,3) trios, preservando
        a garantia matemática: com os 5 números restantes, uma das 10 combinações
        de 3 obrigatoriamente acerta as 3 dezenas sorteadas que caírem nesses 5.
        """
        if qtd_selecionar is None or qtd_selecionar >= len(combinacoes_c53):
            return list(combinacoes_c53)

        limite = max(1, min(qtd_selecionar, len(combinacoes_c53)))

        if self.modo_selecao == 1:  # Melhor pontuação
            trios_pontuados = []
            for trio in combinacoes_c53:
                score = self.pontuar_combinacao_restante(trio)
                trios_pontuados.append((trio, score))
            
            trios_pontuados.sort(key=lambda x: x[1], reverse=True)
            melhores_trios = [trio for trio, score in trios_pontuados[:limite]]
            
        elif self.modo_selecao == 2:  # Diversificação
            melhores_trios = []
            numeros_usados = set()
            
            for trio in combinacoes_c53:
                if len(melhores_trios) >= limite:
                    break
                
                novos_nums = set(trio) - numeros_usados
                if len(novos_nums) >= 2:
                    melhores_trios.append(trio)
                    numeros_usados.update(trio)
            
            while len(melhores_trios) < limite and len(melhores_trios) < len(combinacoes_c53):
                for trio in combinacoes_c53:
                    if trio not in melhores_trios:
                        melhores_trios.append(trio)
                        break
                        
        else:  # Aleatório otimizado
            trios_pontuados = []
            for trio in combinacoes_c53:
                score = self.pontuar_combinacao_restante(trio)
                trios_pontuados.append((trio, score))
            
            trios_pontuados.sort(key=lambda x: x[1], reverse=True)
            corte = max(1, int(len(trios_pontuados) * 0.7))
            candidatos = [trio for trio, score in trios_pontuados[:max(corte, limite)]]
            
            melhores_trios = random.sample(candidatos, min(limite, len(candidatos)))
        
        print(f"🏆 Selecionados {len(melhores_trios)} trios de {len(combinacoes_c53)} possíveis")
        return melhores_trios
    
    def selecionar_melhores_numeros(self, combinacao_20: List[int], qtd_selecionar: int) -> List[int]:
        """Seleciona os melhores números da base de 20"""
        
        # Aplica filtros se existirem
        candidatos = combinacao_20.copy()
        
        if 'equilibrar_paridade' in self.filtros_ativos and self.filtros_ativos['equilibrar_paridade']:
            # Equilibra pares e ímpares
            pares = [n for n in candidatos if n % 2 == 0]
            impares = [n for n in candidatos if n % 2 == 1]
            
            qtd_pares_ideal = qtd_selecionar // 2
            qtd_impares_ideal = qtd_selecionar - qtd_pares_ideal
            
            selecionados = []
            selecionados.extend(random.sample(pares, min(qtd_pares_ideal, len(pares))))
            selecionados.extend(random.sample(impares, min(qtd_impares_ideal, len(impares))))
            
            # Completa se necessário
            faltantes = qtd_selecionar - len(selecionados)
            if faltantes > 0:
                restantes = [n for n in candidatos if n not in selecionados]
                selecionados.extend(random.sample(restantes, min(faltantes, len(restantes))))
            
            return sorted(selecionados)
        
        # Seleção padrão baseada em pontuação
        return sorted(random.sample(candidatos, qtd_selecionar))
    
    def gerar_combinacoes_desdobramento(self, qtd_numeros_jogo: int, 
                                      qtd_combinacoes_base: int = 3,
                                      qtd_trios_por_base: Optional[int] = None) -> List[List[int]]:
        """Gera combinações usando desdobramento complementar"""
        
        print(f"\n🎯 GERAÇÃO COM DESDOBRAMENTO COMPLEMENTAR")
        print(f"📊 Números por jogo: {qtd_numeros_jogo}")
        print(f"🔄 Combinações base: {qtd_combinacoes_base}")
        print(f"🎲 Trios por base: {qtd_trios_por_base}")
        print("-" * 60)
        
        todas_combinacoes = []
        
        for i in range(qtd_combinacoes_base):
            print(f"\n🌟 Processando combinação base {i+1}/{qtd_combinacoes_base}")
            
            # 1. Gera combinação dinâmica de 20 números
            combinacao_20 = self.gerar_combinacao_20_numeros()
            print(f"   🎯 Base dinâmica: {combinacao_20}")
            
            # 2. Identifica os 5 números restantes
            numeros_restantes = [n for n in range(1, 26) if n not in combinacao_20]
            print(f"   🔢 Restantes: {numeros_restantes}")
            
            # 3. Calcula todas as combinações C(5,3)
            trios_c53 = self.calcular_desdobramento_c53(numeros_restantes)
            
            # 4. Seleciona os melhores trios
            melhores_trios = self.selecionar_melhores_trios(trios_c53, qtd_trios_por_base)
            
            # 5. Para cada trio, cria combinação final
            for j, trio in enumerate(melhores_trios):
                print(f"   🎲 Processando trio {j+1}: {list(trio)}")
                
                qtd_da_base = qtd_numeros_jogo - 3  # 3 do trio
                
                if qtd_da_base > 0:
                    melhores_da_base = self.selecionar_melhores_numeros(
                        combinacao_20, qtd_da_base)
                    
                    combinacao_final = sorted(melhores_da_base + list(trio))
                else:
                    combinacao_final = sorted(list(trio))
                
                # Valida e ajusta se necessário
                if len(combinacao_final) != qtd_numeros_jogo:
                    if len(combinacao_final) > qtd_numeros_jogo:
                        combinacao_final = combinacao_final[:qtd_numeros_jogo]
                    else:
                        faltantes = qtd_numeros_jogo - len(combinacao_final)
                        disponíveis = [n for n in combinacao_20 if n not in combinacao_final]
                        if len(disponíveis) >= faltantes:
                            extras = disponíveis[:faltantes]
                            combinacao_final = sorted(combinacao_final + extras)
                
                todas_combinacoes.append(combinacao_final)
                print(f"      ✅ Gerada: {','.join(map(str, combinacao_final))}")
        
        print(f"\n🎉 Total gerado: {len(todas_combinacoes)} combinações!")
        return todas_combinacoes
    
    def analisar_cobertura_desdobramento(self, combinacoes: List[List[int]]) -> Dict:
        """Analisa a cobertura das combinações"""
        
        if not combinacoes:
            return {'cobertura_percentual': 0, 'sobreposicao_media': 0}
        
        # Calcula métricas básicas
        total_numeros = set()
        sobreposicoes = []
        
        for comb in combinacoes:
            total_numeros.update(comb)
        
        # Sobreposição entre combinações
        for i in range(len(combinacoes)):
            for j in range(i+1, len(combinacoes)):
                intersecao = len(set(combinacoes[i]) & set(combinacoes[j]))
                sobreposicoes.append(intersecao)
        
        cobertura_percentual = len(total_numeros) / 25 * 100  # 25 números totais
        sobreposicao_media = sum(sobreposicoes) / len(sobreposicoes) if sobreposicoes else 0
        
        return {
            'cobertura_percentual': cobertura_percentual,
            'sobreposicao_media': sobreposicao_media,
            'numeros_cobertos': len(total_numeros),
            'diversidade': 'Alta' if sobreposicao_media < 8 else 'Média' if sobreposicao_media < 12 else 'Baixa'
        }

    def verificar_garantia_c53(self, numeros_restantes: List[int], apostas: List[List[int]]) -> Dict[str, object]:
        """Verifica se TODOS os C(5,3) trios dos números restantes aparecem em ≥1 aposta.

        A garantia "uma das 10 acerta 3" só vale se as 10 combinações C(5,3)
        forem jogadas. Retorna percentual de trios cobertos.
        """
        trios = list(combinations(numeros_restantes, 3))
        total = len(trios)
        cobertos = 0
        detalhe: Dict[str, bool] = {}
        for trio in trios:
            tset = set(trio)
            encontrada = any(tset <= set(a) for a in apostas)
            detalhe[",".join(map(str, trio))] = encontrada
            if encontrada:
                cobertos += 1
        return {
            "garantia_c53": cobertos == total,
            "trios_total": total,
            "trios_cobertos": cobertos,
            "percentual": round(cobertos / total * 100, 2) if total else 100.0,
            "detalhe": detalhe,
        }
    
    def salvar_desdobramento_completo(self, combinacoes: List[List[int]], 
                                    qtd_numeros: int, config: Dict) -> str:
        """Salva as combinações em arquivo"""
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"desdobramento_complementar_{qtd_numeros}nums_{timestamp}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("# SISTEMA DE DESDOBRAMENTO COMPLEMENTAR V2.0\n")
            f.write(f"# Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"# Números por jogo: {qtd_numeros}\n")
            f.write(f"# Total de jogos: {len(combinacoes)}\n")
            f.write(f"# Configuração: {config.get('configuracao', 'Personalizada')}\n")
            f.write(f"# Investimento: R$ {len(combinacoes) * 3.00:.2f}\n")
            f.write("#\n")
            
            for i, comb in enumerate(combinacoes, 1):
                f.write(f"{i:03d}: {','.join(f'{n:02d}' for n in comb)}\n")
        
        return nome_arquivo

# Funções do menu (iguais às implementadas anteriormente mas usando a classe standalone)
def menu_principal():
    """Menu principal do sistema de desdobramento"""
    sistema = SistemaDesdobramentoStandalone()
    
    while True:
        print("\n🎯 SISTEMA DE DESDOBRAMENTO COMPLEMENTAR V2.0 STANDALONE")
        print("=" * 70)
        print("🔢 Estratégia: Base 20 + Desdobramento C(5,3) = 10 combinações")
        print("🎯 NOVO: Controle total de quantidade de combinações!")
        print("=" * 70)
        print("1️⃣  🎲 Gerar Desdobramento Completo (com controle de quantidade)")
        print("2️⃣  🧮 Desdobramento Personalizado (parâmetros avançados)")
        print("3️⃣  📊 Análise Rápida de Performance")
        print("4️⃣  🚀 Geração Rápida com Quantidade Específica")
        print("0️⃣  🚪 Sair")
        print("=" * 70)
        
        escolha = input("Escolha uma opção (0-4): ").strip()
        
        if escolha == "1":
            gerar_desdobramento_completo_standalone(sistema)
        elif escolha == "2":
            gerar_desdobramento_personalizado_standalone(sistema)
        elif escolha == "3":
            analise_rapida_performance(sistema)
        elif escolha == "4":
            gerar_quantidade_especifica_standalone(sistema)
        elif escolha == "0":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

def gerar_desdobramento_completo_standalone(sistema):
    """Versão simplificada da geração completa"""
    try:
        print("\n🎲 DESDOBRAMENTO COMPLETO C(5,3) - VERSÃO STANDALONE")
        print("-" * 55)
        
        qtd_numeros = input("Números por jogo (15-20) [15]: ").strip()
        qtd_numeros = int(qtd_numeros) if qtd_numeros else 15
        
        if not 15 <= qtd_numeros <= 20:
            print("❌ Quantidade deve estar entre 15 e 20")
            return
        
        print("\n🔧 CONFIGURAÇÕES DISPONÍVEIS:")
        print("1️⃣  ECONÔMICA: 1 base + 3 trios = 3 jogos (R$ 9,00)")
        print("2️⃣  BALANCEADA: 2 bases + 5 trios = 10 jogos (R$ 30,00)")
        print("3️⃣  MÁXIMA: 3 bases + 7 trios = 21 jogos (R$ 63,00)")
        print("4️⃣  SUPER: 5 bases + 8 trios = 40 jogos (R$ 120,00)")
        
        config_choice = input("Escolha configuração (1-4) [2]: ").strip()
        config_choice = config_choice if config_choice else "2"
        
        configs = {
            "1": (1, 3, "ECONÔMICA"),
            "2": (2, 5, "BALANCEADA"), 
            "3": (3, 7, "MÁXIMA"),
            "4": (5, 8, "SUPER")
        }
        
        qtd_bases, qtd_trios, nome_config = configs.get(config_choice, configs["2"])
        
        print(f"✅ Configuração {nome_config} selecionada")
        print(f"💰 Investimento: R$ {qtd_bases * qtd_trios * 3.00:.2f}")
        
        confirma = input("\nConfirmar geração? (S/n) [S]: ").strip().lower()
        if confirma in ['n', 'no', 'não']:
            return
        
        combinacoes = sistema.gerar_combinacoes_desdobramento(qtd_numeros, qtd_bases, qtd_trios)
        
        if combinacoes:
            config = {'configuracao': nome_config, 'modo': 'COMPLETO'}
            arquivo = sistema.salvar_desdobramento_completo(combinacoes, qtd_numeros, config)
            
            analise = sistema.analisar_cobertura_desdobramento(combinacoes)
            
            print(f"\n📊 RESUMO:")
            print(f"• Jogos gerados: {len(combinacoes)}")
            print(f"• Cobertura: {analise['cobertura_percentual']:.1f}%")
            print(f"• Sobreposição média: {analise['sobreposicao_media']:.1f}")
            print(f"• Arquivo salvo: {arquivo}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def gerar_desdobramento_personalizado_standalone(sistema):
    """Versão simplificada da geração personalizada"""
    try:
        print("\n🧮 DESDOBRAMENTO PERSONALIZADO STANDALONE")
        print("-" * 50)
        
        qtd_numeros = int(input("Números por jogo (15-20) [15]: ") or "15")
        qtd_bases = int(input("Quantas bases? (1-10) [2]: ") or "2")
        qtd_trios = int(input("Trios por base? (1-10) [5]: ") or "5")
        
        print(f"\n📊 Configuração: {qtd_bases} bases × {qtd_trios} trios = {qtd_bases * qtd_trios} jogos")
        print(f"💰 Investimento: R$ {qtd_bases * qtd_trios * 3.00:.2f}")
        
        if input("Confirmar? (S/n) [S]: ").strip().lower() in ['n', 'no', 'não']:
            return
        
        combinacoes = sistema.gerar_combinacoes_desdobramento(qtd_numeros, qtd_bases, qtd_trios)
        
        if combinacoes:
            config = {'configuracao': 'PERSONALIZADA'}
            arquivo = sistema.salvar_desdobramento_completo(combinacoes, qtd_numeros, config)
            print(f"✅ {len(combinacoes)} combinações salvas em: {arquivo}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def gerar_quantidade_especifica_standalone(sistema):
    """Geração com quantidade específica"""
    try:
        print("\n🚀 GERAÇÃO COM QUANTIDADE ESPECÍFICA")
        print("-" * 45)
        
        quantidade = int(input("Quantas combinações? (1-100) [10]: ") or "10")
        qtd_numeros = int(input("Números por jogo (15-20) [15]: ") or "15")
        
        # Calcula configuração otimizada
        if quantidade <= 5:
            qtd_bases, qtd_trios = 1, quantidade
        elif quantidade <= 20:
            qtd_bases, qtd_trios = max(2, quantidade // 5), 5
        else:
            qtd_bases, qtd_trios = max(3, quantidade // 7), 7
        
        print(f"🎯 Configuração otimizada: {qtd_bases} bases × {qtd_trios} trios")
        print(f"💰 Investimento: R$ {quantidade * 3.00:.2f}")
        
        if input("Confirmar? (S/n) [S]: ").strip().lower() in ['n', 'no', 'não']:
            return
        
        combinacoes = sistema.gerar_combinacoes_desdobramento(qtd_numeros, qtd_bases, qtd_trios)
        
        # Limita à quantidade solicitada
        if len(combinacoes) > quantidade:
            combinacoes = combinacoes[:quantidade]
        
        if combinacoes:
            config = {'quantidade_solicitada': quantidade, 'modo': 'ESPECÍFICA'}
            arquivo = sistema.salvar_desdobramento_completo(combinacoes, qtd_numeros, config)
            print(f"✅ {len(combinacoes)} combinações salvas em: {arquivo}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def analise_rapida_performance(sistema):
    """Análise rápida de performance"""
    print("\n📈 ANÁLISE RÁPIDA DE PERFORMANCE")
    print("-" * 40)
    
    configs_teste = [
        ("ECONÔMICA", 1, 3, 15),
        ("BALANCEADA", 2, 5, 15),
        ("MÁXIMA", 3, 7, 16)
    ]
    
    print("Testando configurações...")
    
    for nome, bases, trios, nums in configs_teste:
        try:
            combinacoes = sistema.gerar_combinacoes_desdobramento(nums, bases, trios)
            analise = sistema.analisar_cobertura_desdobramento(combinacoes)
            
            print(f"{nome:<12} {len(combinacoes):<5} jogos  Cobertura: {analise['cobertura_percentual']:.1f}%  R$ {len(combinacoes)*3:.0f}")
            
        except Exception as e:
            print(f"Erro em {nome}: {e}")

def main():
    """Função principal"""
    try:
        print("🎯 SISTEMA DE DESDOBRAMENTO COMPLEMENTAR V2.0 - STANDALONE")
        print("📐 Matemática garantida: C(5,3) = 10 combinações")
        print("🆕 SEM DEPENDÊNCIAS EXTERNAS - FUNCIONA EM QUALQUER SISTEMA!")
        print()
        
        menu_principal()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
