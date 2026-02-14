#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR DE COMBINAÇÕES 15 NÚMEROS - RANKEADAS
===============================================

Sistema que lê suas 252 combinações de 20 números e gera
todas as combinações possíveis de 15 números, rankeadas
pela probabilidade baseada em intersecções.

Entrada: arquivo TXT com suas 252 combinações
Saída: combinações de 15 números ordenadas por probabilidade

Autor: AR CALHAU
Data: 12 de Setembro 2025
"""

import itertools
import time
from pathlib import Path
from collections import Counter

class GeradorRankeado15:
    """
    Gerador de combinações de 15 números rankeadas por probabilidade
    """
    
    def __init__(self):
        self.combinacoes_20 = []
        self.combinacoes_15_scores = {}
        self.total_combinacoes_15 = 0
        
    def carregar_combinacoes_20(self, arquivo_txt):
        """
        Carrega as 252 combinações de 20 números do arquivo TXT
        
        Args:
            arquivo_txt: Caminho para o arquivo com as combinações
        """
        print(f"📁 Carregando combinações de {arquivo_txt}...")
        
        try:
            with open(arquivo_txt, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            self.combinacoes_20 = []
            
            for i, linha in enumerate(linhas, 1):
                linha = linha.strip()
                if not linha or linha.startswith('#'):  # Pular linhas vazias e comentários
                    continue
                
                try:
                    # Tentar diferentes formatos
                    if '\t' in linha:  # Separado por TAB
                        partes = linha.split('\t')
                        # Pular primeira coluna se não for número válido
                        if len(partes) > 20:
                            numeros = [int(x.strip()) for x in partes[1:21]]  # Pegar colunas 1-20 
                        else:
                            numeros = [int(x.strip()) for x in partes[1:] if x.strip().isdigit()]
                    elif ',' in linha:
                        numeros = [int(x.strip()) for x in linha.split(',')]
                    elif ';' in linha:
                        numeros = [int(x.strip()) for x in linha.split(';')]
                    elif ' ' in linha:
                        partes = linha.split()
                        # Se primeira parte não é número válido de 1-25, pular
                        try:
                            primeiro = int(partes[0])
                            if primeiro < 1 or primeiro > 25:
                                numeros = [int(x.strip()) for x in partes[1:] if x.strip().isdigit() and 1 <= int(x.strip()) <= 25]
                            else:
                                numeros = [int(x.strip()) for x in partes if x.strip().isdigit() and 1 <= int(x.strip()) <= 25]
                        except:
                            numeros = [int(x.strip()) for x in partes[1:] if x.strip().isdigit() and 1 <= int(x.strip()) <= 25]
                    else:
                        print(f"⚠️ Linha {i}: Formato não reconhecido - {linha[:50]}...")
                        continue
                    
                    # Validar
                    if len(numeros) == 20 and all(1 <= n <= 25 for n in numeros):
                        self.combinacoes_20.append(sorted(numeros))
                    else:
                        print(f"⚠️ Linha {i}: Combinação inválida (deve ter 20 números de 1-25)")
                        
                except ValueError as e:
                    print(f"⚠️ Linha {i}: Erro ao converter números - {e}")
                    continue
            
            print(f"✅ {len(self.combinacoes_20)} combinações de 20 números carregadas")
            
            if len(self.combinacoes_20) == 0:
                print("❌ Nenhuma combinação válida encontrada!")
                print("💡 Formato esperado: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20")
                return False
            
            return True
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {arquivo_txt}")
            print("💡 Certifique-se de que o arquivo existe na pasta atual")
            return False
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
            return False
    
    def calcular_score_combinacao_15(self, combo_15):
        """
        Calcula o score de uma combinação de 15 números
        baseado em quantas das 252 combinações de 20 ela intersecta
        
        Args:
            combo_15: Lista com 15 números
            
        Returns:
            float: Score da combinação (quanto maior, melhor)
        """
        set_combo_15 = set(combo_15)
        score = 0
        intersecoes = []
        
        for combo_20 in self.combinacoes_20:
            set_combo_20 = set(combo_20)
            intersecao = len(set_combo_15 & set_combo_20)
            intersecoes.append(intersecao)
            
            # Sistema de pontuação ponderado
            if intersecao == 15:    # Combinação perfeita (subset)
                score += 1000
            elif intersecao == 14:  # Muito próxima
                score += 500
            elif intersecao == 13:  # Boa intersecção
                score += 250
            elif intersecao == 12:  # Intersecção razoável
                score += 100
            elif intersecao == 11:  # Intersecção básica
                score += 50
            elif intersecao >= 10:  # Intersecção mínima
                score += 20
        
        # Bonus por consistência (se tem muitas intersecções altas)
        intersecoes_altas = sum(1 for x in intersecoes if x >= 12)
        if intersecoes_altas > 50:  # Mais de 20% das combinações
            score += intersecoes_altas * 10
        
        return score
    
    def gerar_e_rankear_combinacoes_15(self):
        """
        Gera todas as combinações possíveis de 15 números e rankeia por score
        """
        print("\n🔄 GERANDO E RANKEANDO COMBINAÇÕES DE 15 NÚMEROS...")
        print("⚠️ ATENÇÃO: Este processo pode demorar alguns minutos...")
        
        inicio = time.time()
        
        # Gerar todas as combinações de 15 números de 1 a 25
        print("📊 Gerando combinações de 15 números de 1 a 25...")
        todas_combinacoes_15 = list(itertools.combinations(range(1, 26), 15))
        self.total_combinacoes_15 = len(todas_combinacoes_15)
        
        print(f"✅ {self.total_combinacoes_15:,} combinações de 15 números geradas")
        print("🧮 Calculando scores...")
        
        # Calcular score para cada combinação
        combinacoes_com_score = []
        
        for i, combo_15 in enumerate(todas_combinacoes_15):
            score = self.calcular_score_combinacao_15(combo_15)
            combinacoes_com_score.append((score, combo_15))
            
            # Progress a cada 10%
            if (i + 1) % (self.total_combinacoes_15 // 10) == 0:
                progresso = ((i + 1) / self.total_combinacoes_15) * 100
                tempo_decorrido = time.time() - inicio
                estimativa_total = tempo_decorrido * (100 / progresso)
                tempo_restante = estimativa_total - tempo_decorrido
                
                print(f"⏱️ {progresso:5.1f}% | "
                      f"Processadas: {i+1:,}/{self.total_combinacoes_15:,} | "
                      f"Tempo: {tempo_decorrido:.0f}s | "
                      f"Restante: ~{tempo_restante:.0f}s")
        
        # Ordenar por score (maior para menor)
        print("📈 Ordenando por score...")
        combinacoes_com_score.sort(key=lambda x: x[0], reverse=True)
        
        fim = time.time()
        tempo_total = fim - inicio
        
        print(f"\n✅ RANKING CONCLUÍDO!")
        print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
        print(f"🚀 Velocidade: {self.total_combinacoes_15 / tempo_total:,.0f} combinações/segundo")
        
        return combinacoes_com_score
    
    def salvar_ranking(self, combinacoes_rankeadas, nome_arquivo=None):
        """
        Salva o ranking das combinações em arquivo TXT
        
        Args:
            combinacoes_rankeadas: Lista de (score, combinacao) ordenada
            nome_arquivo: Nome do arquivo de saída (opcional)
        """
        if nome_arquivo is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_15_rankeadas_{timestamp}.txt"
        
        caminho_arquivo = Path(__file__).parent / nome_arquivo
        
        print(f"\n💾 Salvando ranking em: {nome_arquivo}")
        
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("COMBINAÇÕES DE 15 NÚMEROS - RANKEADAS POR PROBABILIDADE\n")
                f.write("=" * 60 + "\n")
                f.write(f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de combinações: {len(combinacoes_rankeadas):,}\n")
                f.write(f"Baseado em {len(self.combinacoes_20)} combinações de 20 números\n")
                f.write("Formato: SCORE | COMBINAÇÃO (separada por vírgulas)\n")
                f.write("=" * 60 + "\n\n")
                
                # Top 100 com scores para análise
                f.write("TOP 100 COMBINAÇÕES (com scores):\n")
                f.write("-" * 40 + "\n")
                
                for i, (score, combo) in enumerate(combinacoes_rankeadas[:100], 1):
                    combo_str = ','.join(map(str, combo))
                    f.write(f"{i:3d}. {score:6.0f} | {combo_str}\n")
                
                f.write("\n" + "=" * 60 + "\n")
                f.write("TODAS AS COMBINAÇÕES (apenas números, ordenadas por probabilidade):\n")
                f.write("=" * 60 + "\n")
                
                # Todas as combinações, apenas números
                for score, combo in combinacoes_rankeadas:
                    combo_str = ','.join(map(str, combo))
                    f.write(f"{combo_str}\n")
            
            print(f"✅ Arquivo salvo: {caminho_arquivo}")
            
            # Estatísticas do ranking
            scores = [score for score, _ in combinacoes_rankeadas]
            print(f"\n📊 ESTATÍSTICAS DO RANKING:")
            print(f"   🥇 Melhor score: {max(scores):,.0f}")
            print(f"   🥉 Pior score: {min(scores):,.0f}")
            print(f"   📊 Score médio: {sum(scores)/len(scores):,.0f}")
            print(f"   📈 Top 10% acima de: {scores[len(scores)//10]:,.0f}")
            print(f"   🎯 Top 1% acima de: {scores[len(scores)//100]:,.0f}")
            
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return None
    
    def mostrar_preview_top(self, combinacoes_rankeadas, num_top=10):
        """
        Mostra preview das top combinações
        """
        print(f"\n🏆 PREVIEW - TOP {num_top} COMBINAÇÕES:")
        print("-" * 70)
        print("RANK  SCORE    COMBINAÇÃO")
        print("-" * 70)
        
        for i, (score, combo) in enumerate(combinacoes_rankeadas[:num_top], 1):
            combo_str = ','.join(f"{n:2d}" for n in combo)
            print(f"{i:3d}. {score:6.0f}  {combo_str}")
    
    def executar_processo_completo(self, arquivo_entrada):
        """
        Executa o processo completo de geração e ranking
        
        Args:
            arquivo_entrada: Caminho para arquivo com as 252 combinações
        """
        print("🎯" * 25)
        print("🎯 GERADOR DE COMBINAÇÕES 15 NÚMEROS - RANKEADAS")
        print("🎯" * 25)
        
        # 1. Carregar combinações de 20 números
        if not self.carregar_combinacoes_20(arquivo_entrada):
            return None
        
        # 2. Gerar e rankear combinações de 15
        combinacoes_rankeadas = self.gerar_e_rankear_combinacoes_15()
        
        # 3. Mostrar preview
        self.mostrar_preview_top(combinacoes_rankeadas)
        
        # 4. Salvar resultado
        arquivo_saida = self.salvar_ranking(combinacoes_rankeadas)
        
        print("\n" + "=" * 60)
        print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"📁 Arquivo de entrada: {arquivo_entrada}")
        print(f"💾 Arquivo de saída: {arquivo_saida}")
        print(f"📊 {len(combinacoes_rankeadas):,} combinações rankeadas")
        print("🎯 Combinações ordenadas da MAIS para MENOS provável!")
        
        return arquivo_saida

def main():
    """
    Função principal
    """
    gerador = GeradorRankeado15()
    
    print("🎯 GERADOR DE COMBINAÇÕES 15 NÚMEROS - RANKEADAS")
    print("=" * 55)
    print("💡 Este sistema lê suas 252 combinações de 20 números")
    print("   e gera TODAS as combinações de 15 números possíveis,")
    print("   rankeadas da MAIS para MENOS provável!")
    print()
    
    # Solicitar arquivo de entrada
    arquivo_entrada = input("📁 Digite o nome do arquivo com suas 252 combinações de 20 números: ").strip()
    
    if not arquivo_entrada:
        print("❌ Nome do arquivo não fornecido!")
        return
    
    # Verificar se arquivo existe
    if not Path(arquivo_entrada).exists():
        print(f"❌ Arquivo '{arquivo_entrada}' não encontrado!")
        print("💡 Certifique-se de que o arquivo está na mesma pasta deste script")
        return
    
    # Executar processo
    try:
        gerador.executar_processo_completo(arquivo_entrada)
    except KeyboardInterrupt:
        print("\n\n⏹️ Processo interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
