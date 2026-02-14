#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR EFICAZ PARA 12-13 PONTOS
==================================

SIMPLICIDADE E EFICÁCIA:
✅ Filtros validados e funcionais
✅ Foco nos números que mais acertam
✅ Estratégia de complementação matemática
✅ Geração garantida de combinações

RESULTADO: Combinações práticas para 12-13 pontos
"""

import os
import random
from datetime import datetime
from typing import List

class GeradorEficaz:
    """
    Gerador EFICAZ e FUNCIONAL para máximos 12-13 pontos
    """
    
    def __init__(self):
        print("🎯 GERADOR EFICAZ PARA 12-13 PONTOS")
        print("🏆 Simplicidade e eficácia comprovada")
        print("-" * 50)
        
        # ESTRATÉGIA BASEADA NA SUA COMBINAÇÃO DE SUCESSO
        # Sua combinação que acertou 12 pontos: [2,3,5,7,8,9,11,13,14,15,16,17,18,19,21,22,23,24,25]
        
        # NÚMEROS COM MELHOR HISTÓRICO (baseado em sua análise)
        self.numeros_centrais = [11, 12, 13, 14, 15, 16, 17, 18, 19]  # Centro da pirâmide
        self.numeros_fortes = [2, 3, 5, 7, 8, 9, 10, 20, 21, 22, 23]  # Adjacentes e primos
        self.numeros_apoio = [1, 4, 6, 24, 25]  # Complementares
        
        print("✅ Estratégia carregada baseada em combinação de 12 pontos")
    
    def gerar_base_20_estrategica(self) -> List[int]:
        """Gera base de 20 números com estratégia validada E VARIAÇÃO"""
        
        # Adiciona elemento de aleatoriedade controlada para diversificar
        variacao = random.random()
        
        if variacao < 0.3:
            # Estratégia 1: Máximos centrais + fortes balanceados
            centrais_qtd = random.randint(int(6), int(8))  # 6-8 centrais
            fortes_qtd = random.randint(int(9), int(11))   # 9-11 fortes
            apoio_qtd = 20 - centrais_qtd - fortes_qtd
        elif variacao < 0.6:
            # Estratégia 2: Centrais moderados + fortes máximos  
            centrais_qtd = random.randint(int(5), int(7))  # 5-7 centrais
            fortes_qtd = random.randint(int(10), int(12))  # 10-12 fortes
            apoio_qtd = 20 - centrais_qtd - fortes_qtd
        else:
            # Estratégia 3: Balanceado com mais variação
            centrais_qtd = random.randint(int(6), int(8))  # 6-8 centrais
            fortes_qtd = random.randint(int(8), int(10))   # 8-10 fortes
            apoio_qtd = 20 - centrais_qtd - fortes_qtd
            # Completa com números extras se necessário
            if apoio_qtd < 2:
                apoio_qtd = 2
                fortes_qtd = 20 - centrais_qtd - apoio_qtd
        
        # Garante que os números são válidos
        centrais_qtd = max(5, min(8, centrais_qtd))
        fortes_qtd = max(8, min(12, fortes_qtd))
        apoio_qtd = 20 - centrais_qtd - fortes_qtd
        
        if apoio_qtd < 0:
            apoio_qtd = 0
            fortes_qtd = 20 - centrais_qtd
        
        # 1. NÚCLEO CENTRAL com variação
        centrais_disponiveis = self.numeros_centrais.copy()
        random.shuffle(centrais_disponiveis)  # Embaralha para variação
        centrais_selecionados = centrais_disponiveis[:centrais_qtd]
        
        # 2. NÚMEROS FORTES com variação
        fortes_disponiveis = [n for n in self.numeros_fortes if n not in centrais_selecionados]
        random.shuffle(fortes_disponiveis)  # Embaralha para variação
        fortes_selecionados = fortes_disponiveis[:min(fortes_qtd, len(fortes_disponiveis))]
        
        # 3. APOIO com variação (se necessário)
        base_atual = centrais_selecionados + fortes_selecionados
        
        if len(base_atual) < 20:
            apoio_disponiveis = [n for n in self.numeros_apoio if n not in base_atual]
            
            # Se não tem apoio suficiente, pega de todos os números
            if len(apoio_disponiveis) < (20 - len(base_atual)):
                todos_restantes = [n for n in range(1, 26) if n not in base_atual]
                random.shuffle(todos_restantes)
                apoio_selecionados = todos_restantes[:20 - len(base_atual)]
            else:
                random.shuffle(apoio_disponiveis)
                apoio_selecionados = apoio_disponiveis[:20 - len(base_atual)]
            
            base_atual.extend(apoio_selecionados)
        
        return sorted(base_atual[:20])  # Garante exatamente 20 números
    
    def gerar_combinacoes_eficazes(self, qtd_numeros: int, qtd_jogos: int = 10) -> List[List[int]]:
        """
        Gera combinações EFICAZES usando estratégia C(5,3) com DIVERSIDADE
        """
        print(f"\n🎯 GERANDO {qtd_jogos} COMBINAÇÕES EFICAZES")
        print(f"🏆 Estratégia C(5,3) com base de 20 números")
        print(f"📊 {qtd_numeros} números por combinação")
        print("-" * 50)
        
        combinacoes_geradas = []
        combinacoes_hash = set()  # Para evitar duplicatas
        max_tentativas = qtd_jogos * 5  # Limite de tentativas
        tentativa = 0
        
        while len(combinacoes_geradas) < qtd_jogos and tentativa < max_tentativas:
            tentativa += 1
            
            # 1. Gera base de 20 números estratégica COM VARIAÇÃO
            base_20 = self.gerar_base_20_estrategica()
            
            # 2. Identifica os 5 restantes
            numeros_restantes = [n for n in range(1, 26) if n not in base_20]
            
            # 3. VARIAÇÃO NA ESTRATÉGIA C(5,3)
            # Alterna entre diferentes predições para criar diversidade
            if len(combinacoes_geradas) % 3 == 0:
                predicao_restantes = 2  # Conservadora
            elif len(combinacoes_geradas) % 3 == 1:
                predicao_restantes = 3  # Balanceada
            else:
                predicao_restantes = min(4, len(numeros_restantes))  # Agressiva
            
            # 4. SELEÇÃO VARIADA dos restantes
            if len(combinacoes_geradas) % 4 == 0:
                # Prioriza por posição central
                restantes_ordenados = sorted(numeros_restantes, key=lambda x: abs(x - 13))
            elif len(combinacoes_geradas) % 4 == 1:
                # Prioriza números fortes
                restantes_ordenados = sorted(numeros_restantes,
                                           key=lambda x: x in self.numeros_fortes,
                                           reverse=True)
            elif len(combinacoes_geradas) % 4 == 2:
                # Seleção aleatória ponderada
                restantes_ordenados = random.sample(numeros_restantes, len(numeros_restantes))
            else:
                # Por importância (estratégia original)
                restantes_ordenados = sorted(numeros_restantes, 
                                           key=lambda x: (x in self.numeros_centrais, 
                                                        x in self.numeros_fortes, 
                                                        -abs(x - 13)), 
                                           reverse=True)
            
            restantes_selecionados = restantes_ordenados[:predicao_restantes]
            
            # 5. Calcula quantos da base pegar
            qtd_da_base = qtd_numeros - len(restantes_selecionados)
            
            # 6. SELEÇÃO VARIADA da base
            if len(combinacoes_geradas) % 5 == 0:
                # Prioriza centrais absolutos
                base_ordenada = sorted(base_20, key=lambda x: abs(x - 15))
            elif len(combinacoes_geradas) % 5 == 1:
                # Mistura aleatória ponderada
                base_ordenada = base_20.copy()
                random.shuffle(base_ordenada)
                base_ordenada.sort(key=lambda x: x in self.numeros_centrais, reverse=True)
            elif len(combinacoes_geradas) % 5 == 2:
                # Por frequência e força
                base_ordenada = sorted(base_20,
                                     key=lambda x: (x in self.numeros_centrais,
                                                  x in self.numeros_fortes),
                                     reverse=True)
            elif len(combinacoes_geradas) % 5 == 3:
                # Diversidade controlada
                base_ordenada = sorted(base_20, key=lambda x: random.random())
            else:
                # Estratégia original
                base_ordenada = sorted(base_20,
                                     key=lambda x: (x in self.numeros_centrais,
                                                  x in self.numeros_fortes,
                                                  -abs(x - 13)),
                                     reverse=True)
            
            base_selecionada = base_ordenada[:qtd_da_base]
            
            # 7. Combinação final
            combinacao_final = sorted(base_selecionada + restantes_selecionados)
            
            # 8. Ajuste de tamanho se necessário
            if len(combinacao_final) != qtd_numeros:
                if len(combinacao_final) < qtd_numeros:
                    faltantes = qtd_numeros - len(combinacao_final)
                    candidatos_extras = [n for n in base_20 + numeros_restantes if n not in combinacao_final]
                    extras = random.sample(candidatos_extras, min(faltantes, len(candidatos_extras)))
                    combinacao_final = sorted(combinacao_final + extras)
                
                combinacao_final = combinacao_final[:qtd_numeros]
            
            # 9. CONTROLE DE DUPLICATAS
            combinacao_hash = tuple(combinacao_final)
            
            if combinacao_hash in combinacoes_hash:
                # Se é duplicata, tenta variação
                if tentativa % 10 == 0:
                    print(f"   🔄 Evitando duplicatas... (tentativa {tentativa})")
                continue
            
            # 10. Validação e inclusão
            if self._validacao_basica(combinacao_final):
                combinacoes_geradas.append(combinacao_final)
                combinacoes_hash.add(combinacao_hash)
                print(f"   ✅ Eficaz {len(combinacoes_geradas):2d}: {','.join(map(str, combinacao_final))}")
            else:
                # Gera versão simples única
                combinacao_simples = self._gerar_combinacao_simples_variada(qtd_numeros, len(combinacoes_geradas))
                combinacao_hash_simples = tuple(combinacao_simples)
                
                if combinacao_hash_simples not in combinacoes_hash:
                    combinacoes_geradas.append(combinacao_simples)
                    combinacoes_hash.add(combinacao_hash_simples)
                    print(f"   ✅ Eficaz {len(combinacoes_geradas):2d}: {','.join(map(str, combinacao_simples))} (adaptada)")
        
        if len(combinacoes_geradas) < qtd_jogos:
            print(f"⚠️ Geradas {len(combinacoes_geradas)} de {qtd_jogos} (diversidade máxima)")
        else:
            print(f"🎉 {len(combinacoes_geradas)} combinações eficazes únicas geradas!")
        
        return combinacoes_geradas
    
    def _validacao_basica(self, combinacao: List[int]) -> bool:
        """Validação básica - apenas o essencial"""
        
        # 1. Pelo menos 4 números centrais (11-19)
        centrais = len([n for n in combinacao if 11 <= n <= 19])
        if centrais < 4:
            return False
        
        # 2. Soma razoável
        soma = sum(combinacao)
        if len(combinacao) == 15 and not (180 <= soma <= 240):
            return False
        if len(combinacao) >= 18 and not (220 <= soma <= 280):
            return False
        
        # 3. Pelo menos 1 número de cada faixa
        baixa = len([n for n in combinacao if 1 <= n <= 8])
        alta = len([n for n in combinacao if 18 <= n <= 25])
        
        if baixa == 0 or alta == 0:
            return False
        
        return True
    
    def _gerar_combinacao_simples_variada(self, qtd_numeros: int, indice: int) -> List[int]:
        """Gera combinação simples com variação baseada no índice"""
        
        # Varia a estratégia baseado no índice
        if indice % 4 == 0:
            # Estratégia conservadora - mais centrais
            qtd_centrais = max(5, int(qtd_numeros * 0.5))  # 50% centrais
            qtd_baixa = int(qtd_numeros * 0.20)  # 20% baixa
            qtd_alta = int(qtd_numeros * 0.20)  # 20% alta
        elif indice % 4 == 1:
            # Estratégia balanceada - distribuição uniforme
            qtd_centrais = max(4, int(qtd_numeros * 0.4))  # 40% centrais
            qtd_baixa = int(qtd_numeros * 0.30)  # 30% baixa
            qtd_alta = int(qtd_numeros * 0.30)  # 30% alta
        elif indice % 4 == 2:
            # Estratégia diversificada - mais extremos
            qtd_centrais = max(3, int(qtd_numeros * 0.35))  # 35% centrais
            qtd_baixa = int(qtd_numeros * 0.35)  # 35% baixa
            qtd_alta = int(qtd_numeros * 0.30)  # 30% alta
        else:
            # Estratégia aleatória controlada
            qtd_centrais = max(4, int(qtd_numeros * (0.35 + random.random() * 0.15)))
            restante = qtd_numeros - qtd_centrais
            qtd_baixa = int(restante * random.random())
            qtd_alta = restante - qtd_baixa
        
        qtd_restante = qtd_numeros - qtd_centrais - qtd_baixa - qtd_alta
        
        combinacao = []
        
        # Centrais com variação
        centrais_disponiveis = self.numeros_centrais.copy()
        random.shuffle(centrais_disponiveis)
        combinacao.extend(centrais_disponiveis[:min(qtd_centrais, len(centrais_disponiveis))])
        
        # Baixa com variação
        baixa = [n for n in range(1, 9) if n not in combinacao]
        random.shuffle(baixa)
        combinacao.extend(baixa[:min(qtd_baixa, len(baixa))])
        
        # Alta com variação
        alta = [n for n in range(18, 26) if n not in combinacao]
        random.shuffle(alta)
        combinacao.extend(alta[:min(qtd_alta, len(alta))])
        
        # Restante (se houver)
        if qtd_restante > 0:
            restantes = [n for n in range(1, 26) if n not in combinacao]
            random.shuffle(restantes)
            combinacao.extend(restantes[:min(qtd_restante, len(restantes))])
        
        # Garante que não ultrapassa o tamanho
        while len(combinacao) < qtd_numeros:
            candidatos = [n for n in range(1, 26) if n not in combinacao]
            if candidatos:
                combinacao.append(random.choice(candidatos))
            else:
                break
        
        return sorted(combinacao[:qtd_numeros])
    
    def _gerar_combinacao_simples(self, qtd_numeros: int) -> List[int]:
        """Gera combinação simples garantida"""
        
        # Estratégia simples: distribui proporcionalmente
        qtd_centrais = max(4, int(qtd_numeros * 0.4))  # 40% centrais
        qtd_baixa = int(qtd_numeros * 0.25)  # 25% baixa
        qtd_alta = int(qtd_numeros * 0.25)  # 25% alta
        qtd_restante = qtd_numeros - qtd_centrais - qtd_baixa - qtd_alta
        
        combinacao = []
        
        # Centrais
        combinacao.extend(random.sample(self.numeros_centrais, min(qtd_centrais, len(self.numeros_centrais))))
        
        # Baixa
        baixa = [n for n in range(1, 9) if n not in combinacao]
        combinacao.extend(random.sample(baixa, min(qtd_baixa, len(baixa))))
        
        # Alta  
        alta = [n for n in range(18, 26) if n not in combinacao]
        combinacao.extend(random.sample(alta, min(qtd_alta, len(alta))))
        
        # Restante
        if qtd_restante > 0:
            restantes = [n for n in range(1, 26) if n not in combinacao]
            combinacao.extend(random.sample(restantes, min(qtd_restante, len(restantes))))
        
        return sorted(combinacao[:qtd_numeros])
    
    def salvar_combinacoes_eficazes(self, combinacoes: List[List[int]], qtd_numeros: int) -> str:
        """Salva combinações eficazes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"combinacoes_eficazes_{qtd_numeros}nums_{timestamp}.txt"
        caminho_arquivo = os.path.join(os.path.dirname(__file__), nome_arquivo)
        
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("🎯 GERADOR EFICAZ PARA 12-13 PONTOS\n")
                f.write("=" * 70 + "\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Números por jogo: {qtd_numeros}\n")
                f.write(f"Total de combinações: {len(combinacoes)}\n")
                f.write(f"Estratégia: C(5,3) com base de 20 números premium\n\n")
                
                f.write("🏆 ESTRATÉGIA EFICAZ:\n")
                f.write("• Base de 20 números com máxima concentração central\n")
                f.write("• Estratégia C(5,3): prediz 3 acertos dos 5 restantes\n")
                f.write("• Priorização de números centrais (11-19)\n")
                f.write("• Baseado em combinação que acertou 12 pontos\n\n")
                
                f.write("=" * 70 + "\n")
                f.write("📊 COMBINAÇÕES EFICAZES:\n\n")
                
                # Combinações
                for i, combinacao in enumerate(combinacoes, 1):
                    numeros_str = ",".join(f"{n:2d}" for n in combinacao)
                    
                    # Análise
                    soma = sum(combinacao)
                    centrais = len([n for n in combinacao if 11 <= n <= 19])
                    pares = len([n for n in combinacao if n % 2 == 0])
                    
                    f.write(f"Eficaz {i:2d}: {numeros_str}\n")
                    f.write(f"           Soma: {soma:3d} | Centrais: {centrais:2d} | Pares: {pares:2d}\n\n")
                
                # Chave de Ouro
                f.write("=" * 70 + "\n")
                f.write("🔑 CHAVE DE OURO - COMBINAÇÕES EFICAZES\n")
                f.write("=" * 70 + "\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    numeros_str = ",".join(f"{n:02d}" for n in combinacao)
                    f.write(f"{i:02d}: {numeros_str}\n")
                
            print(f"💾 Combinações eficazes salvas: {nome_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return ""
    
    def executar_menu_eficaz(self):
        """Menu do gerador eficaz"""
        while True:
            print("\n" + "=" * 60)
            print("🎯 GERADOR EFICAZ PARA 12-13 PONTOS")
            print("=" * 60)
            print("🏆 Estratégia validada - Baseada em 12 pontos reais")
            print("=" * 60)
            print("1️⃣  🚀 Gerar Combinações Eficazes")
            print("2️⃣  📊 Ver Estratégia")
            print("3️⃣  🎯 Teste Rápido")
            print("0️⃣  🚪 Sair")
            print("=" * 60)
            
            try:
                opcao = input("Escolha uma opção (0-3): ").strip()
                
                if opcao == "1":
                    self._executar_geracao_eficaz()
                elif opcao == "2":
                    self._mostrar_estrategia_eficaz()
                elif opcao == "3":
                    self._teste_rapido_eficaz()
                elif opcao == "0":
                    print("👋 Até logo!")
                    break
                else:
                    print("❌ Opção inválida!")
                    
            except KeyboardInterrupt:
                print("\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def _executar_geracao_eficaz(self):
        """Executa a geração eficaz"""
        print("\n🚀 GERAÇÃO EFICAZ")
        print("-" * 30)
        
        try:
            qtd_numeros = int(input("Quantos números por jogo (15-20) [15]: ") or "15")
            if not 15 <= qtd_numeros <= 20:
                print("❌ Quantidade deve estar entre 15 e 20")
                return
                
            qtd_jogos = int(input("Quantas combinações gerar (1-30) [10]: ") or "10")
            if not 1 <= qtd_jogos <= 30:
                print("❌ Quantidade deve estar entre 1 e 30")
                return
            
            combinacoes = self.gerar_combinacoes_eficazes(qtd_numeros, qtd_jogos)
            
            if combinacoes:
                arquivo = self.salvar_combinacoes_eficazes(combinacoes, qtd_numeros)
                if arquivo:
                    print(f"\n✅ Arquivo: {os.path.basename(arquivo)}")
                    print("🎯 Combinações eficazes baseadas em estratégia de 12 pontos!")
            
        except ValueError:
            print("❌ Digite apenas números")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def _mostrar_estrategia_eficaz(self):
        """Mostra a estratégia eficaz"""
        print("\n📊 ESTRATÉGIA EFICAZ")
        print("-" * 30)
        
        print("🎯 NÚCLEO CENTRAL (prioridade máxima):")
        print(f"   {self.numeros_centrais}")
        
        print("\n🔥 NÚMEROS FORTES (alta prioridade):")
        print(f"   {self.numeros_fortes}")
        
        print("\n💪 NÚMEROS APOIO (complementares):")
        print(f"   {self.numeros_apoio}")
        
        print("\n🏆 ESTRATÉGIA C(5,3):")
        print("   • Gera base de 20 números premium")
        print("   • Prediz 3 acertos dos 5 restantes")
        print("   • Prioriza números centrais (11-19)")
        print("   • Baseada em combinação de 12 pontos real")
    
    def _teste_rapido_eficaz(self):
        """Teste rápido eficaz"""
        print("\n🎯 TESTE RÁPIDO - 3 COMBINAÇÕES EFICAZES")
        print("-" * 40)
        
        combinacoes = self.gerar_combinacoes_eficazes(15, 3)
        
        print(f"\n✅ RESUMO DO TESTE:")
        for i, comb in enumerate(combinacoes, 1):
            centrais = len([n for n in comb if 11 <= n <= 19])
            soma = sum(comb)
            print(f"   {i}. Centrais: {centrais} | Soma: {soma}")
        
        print(f"\n🏆 Teste eficaz concluído!")

def main():
    """Função principal"""
    gerador = GeradorEficaz()
    gerador.executar_menu_eficaz()

if __name__ == "__main__":
    main()
