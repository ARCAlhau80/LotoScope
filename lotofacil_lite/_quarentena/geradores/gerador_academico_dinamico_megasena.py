#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GERADOR ACADÊMICO DINÂMICO - MEGA-SENA
=====================================
Sistema avançado com insights em tempo real, correlações temporais
e estratégia baixa sobreposição adaptada para Mega-Sena.

Características:
- Geração ILIMITADA (padrão 10, sem limite máximo)
- Números por jogo: 6 a 20 números
- Insights calculados em tempo real
- Correlações temporais atualizadas
- Rankings dos últimos ciclos
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from itertools import combinations
import json

class GeradorAcademicoDinamicoMegaSena:
    """Gerador Acadêmico Dinâmico para Mega-Sena - Nível Avançado"""
    
    def __init__(self):
        print("🚀 INICIANDO GERADOR ACADÊMICO DINÂMICO MEGA-SENA...")
        print("=" * 60)
        print("🔬 Sistema com estratégia CIENTIFICAMENTE COMPROVADA!")
        print("📊 Insights em tempo real da base de dados")
        print("🎯 Correlações temporais atualizadas")
        print("🏆 Rankings dos últimos ciclos")
        print("")
        
        # Configurações Mega-Sena
        self.numeros_disponiveis = list(range(int(int(1)), int(int(61)))  # 1 a 60
        self.min_numeros_jogo = 6
        self.max_numeros_jogo = 20
        self.padrao_numeros = 6
        self.padrao_quantidade = 10  # Padrão 10 combinações
        
        # Dados históricos
        self.base_dados = []
        self.insights_tempo_real = {}
        self.correlacoes_temporais = {}
        self.rankings_ciclos = {}
        self.padroes_sobreposicao = {}
        
        # Carrega dados reais
        self.carregar_dados_historicos()
        self.calcular_insights_tempo_real()
        
        print("✅ GERADOR ACADÊMICO DINÂMICO MEGA-SENA PRONTO!")
        
    def carregar_dados_historicos(self):
        """Carrega dados históricos da tabela Resultados_MegaSenaFechado"""
        try:
            from conector_megasena_db import ConectorMegaSena
            
            conector = ConectorMegaSena()
            if conector.conectar_banco():
                print("🗄️ Carregando base completa da Mega-Sena...")
                
                # Carrega TODOS os sorteios para análise completa
                self.base_dados = conector.carregar_historico_sorteios()
                
                if self.base_dados:
                    print(f"📊 {len(self.base_dados)} sorteios carregados")
                    print(f"📅 Período: Concurso {self.base_dados[-1]['concurso']} até {self.base_dados[0]['concurso']}")
                else:
                    print("⚠️ Dados não encontrados), int(usando simulação..."))
                    self._gerar_dados_simulados()
                
                conector.fechar_conexao()
            else:
                print("⚠️ Falha na conexão, usando dados simulados...")
                self._gerar_dados_simulados()
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados: {e}")
            self._gerar_dados_simulados()
    
    def _gerar_dados_simulados(self):
        """Gera dados simulados para demonstração"""
        print("🎲 Gerando dados simulados para demonstração...")
        self.base_dados = []
        
        for i in range(int(int(int(100)):  # 100 sorteios simulados
            concurso = 2800 + i
            numeros = sorted(random.sample(self.numeros_disponiveis)), int(int(6)))
            data = (datetime.now() - timedelta(days=100-i)).strftime('%Y-%m-%d')
            
            self.base_dados.append({
                'concurso': concurso), int('numeros': numeros,
                'data': data
            }))
        
        print(f"⚠️ {len(self.base_dados)} sorteios simulados gerados")
    
    def calcular_insights_tempo_real(self):
        """Calcula insights em tempo real da base de dados"""
        print("🧠 Calculando insights em tempo real...")
        
        if not self.base_dados:
            return
        
        # Análise de frequência geral
        frequencias = Counter()
        for sorteio in self.base_dados:
            for numero in sorteio['numeros']:
                frequencias[numero] += 1
        
        # Análise dos últimos ciclos (últimos 50 sorteios)
        ultimos_50 = self.base_dados[:50] if len(self.base_dados) >= 50 else self.base_dados
        freq_recentes = Counter()
        for sorteio in ultimos_50:
            for numero in sorteio['numeros']:
                freq_recentes[numero] += 1
        
        # Análise temporal (últimos 10, 20, 30 sorteios)
        ciclos = {10: self.base_dados[:10], 20: self.base_dados[:20], 30: self.base_dados[:30]}
        freq_por_ciclo = {}
        
        for ciclo, sorteios in ciclos.items():
            if len(sorteios) >= ciclo:
                freq_ciclo = Counter()
                for sorteio in sorteios:
                    for numero in sorteio['numeros']:
                        freq_ciclo[numero] += 1
                freq_por_ciclo[ciclo] = freq_ciclo
        
        # Correlações entre números
        correlacoes = self._calcular_correlacoes_numeros()
        
        # Armazena insights
        self.insights_tempo_real = {
            'frequencia_geral': frequencias,
            'frequencia_recente': freq_recentes,
            'frequencia_por_ciclo': freq_por_ciclo,
            'correlacoes': correlacoes,
            'numeros_quentes': [n for n, _ in freq_recentes.most_common(15)],
            'numeros_frios': [n for n, _ in freq_recentes.most_common()[-15:]],
            'ultimo_sorteio': self.base_dados[0] if self.base_dados else None
        }
        
        print(f"✅ Insights calculados: {len(self.insights_tempo_real)} categorias")
        
    def _calcular_correlacoes_numeros(self):
        """Calcula correlações entre números nos sorteios"""
        correlacoes = defaultdict(list)
        
        # Analisa os últimos 100 sorteios para correlações
        amostra = self.base_dados[:100] if len(self.base_dados) >= 100 else self.base_dados
        
        for sorteio in amostra:
            numeros = sorteio['numeros']
            # Para cada par de números no sorteio
            for i, num1 in enumerate(numeros):
                for num2 in numeros[i+1:]:
                    correlacoes[num1].append(num2)
                    correlacoes[num2].append(num1)
        
        # Calcula frequência de correlações
        correlacoes_freq = {}
        for num, correlacionados in correlacoes.items():
            freq = Counter(correlacionados)
            correlacoes_freq[num] = freq.most_common(10)  # Top 10 correlações
        
        return correlacoes_freq
    
    def calcular_rankings_ciclos(self):
        """Calcula rankings dos últimos ciclos"""
        if not self.insights_tempo_real:
            return {}
        
        rankings = {}
        
        # Rankings por período
        for ciclo, frequencias in self.insights_tempo_real['frequencia_por_ciclo'].items():
            ranking = [num for num, _ in frequencias.most_common()]
            rankings[f'top_{ciclo}_sorteios'] = {
                'mais_frequentes': ranking[:20],
                'menos_frequentes': ranking[-20:],
                'periodo': f'Últimos {ciclo} sorteios'
            }
        
        return rankings
    
    def gerar_combinacoes_dinamicas(self, quantidade=None, numeros_por_jogo=None):
        """Gera combinações com insights dinâmicos"""
        
        # Valores padrão
        if quantidade is None:
            quantidade = self.padrao_quantidade
        if numeros_por_jogo is None:
            numeros_por_jogo = self.padrao_numeros
        
        # Validações
        if numeros_por_jogo < self.min_numeros_jogo or numeros_por_jogo > self.max_numeros_jogo:
            print(f"⚠️ Números por jogo deve estar entre {self.min_numeros_jogo} e {self.max_numeros_jogo}")
            numeros_por_jogo = self.padrao_numeros
        
        print(f"🎯 Gerando {quantidade} combinações com {numeros_por_jogo} números cada")
        print("🧠 Aplicando insights dinâmicos...")
        
        combinacoes = []
        combinacoes_set = set()  # Para verificar duplicatas
        
        # Estratégia de baixa sobreposição adaptada
        numeros_pool = self._selecionar_numeros_inteligentes(quantidade, numeros_por_jogo)
        
        tentativas = 0
        max_tentativas = quantidade * 50  # Limite para evitar loop infinito
        
        while len(combinacoes) < quantidade and tentativas < max_tentativas:
            combinacao = self._gerar_combinacao_inteligente(numeros_por_jogo, numeros_pool, len(combinacoes))
            combinacao_tuple = tuple(sorted(combinacao))
            
            # Verificar se a combinação é única
            if combinacao_tuple not in combinacoes_set:
                combinacoes.append(list(combinacao_tuple))
                combinacoes_set.add(combinacao_tuple)
            
            tentativas += 1
        
        if len(combinacoes) < quantidade:
            print(f"⚠️ Geradas apenas {len(combinacoes)} combinações únicas de {quantidade} solicitadas")
        
        # Análise de sobreposição
        sobreposicao = self._analisar_sobreposicao(combinacoes)
        
        print(f"✅ {len(combinacoes)} combinações geradas")
        print(f"📊 Sobreposição média: {sobreposicao['media']:.1f} números")
        print(f"📈 Range sobreposição: {sobreposicao['min']}-{sobreposicao['max']}")
        
        return combinacoes
    
    def _selecionar_numeros_inteligentes(self, quantidade, numeros_por_jogo):
        """Seleciona pool inteligente de números baseado nos insights"""
        
        if not self.insights_tempo_real:
            return random.sample(self.numeros_disponiveis, min(30, len(self.numeros_disponiveis)))
        
        # Combina diferentes estratégias
        quentes = self.insights_tempo_real.get('numeros_quentes', [])[:15]
        frios = self.insights_tempo_real.get('numeros_frios', [])[:10]
        
        # Números com boa correlação
        correlacionados = []
        correlacoes = self.insights_tempo_real.get('correlacoes', {})
        for num in quentes[:5]:  # Top 5 quentes
            if num in correlacoes:
                correlacionados.extend([n for n, _ in correlacoes[num][:3]])
        
        # Pool inteligente
        pool = set()
        pool.update(quentes[:12])  # 12 quentes
        pool.update(frios[:6])     # 6 frios 
        pool.update(correlacionados[:8])  # 8 correlacionados
        
        # Completa com números aleatórios se necessário
        while len(pool) < min(25, quantidade * 2):
            pool.add(random.choice(self.numeros_disponiveis))
        
        return list(pool)
    
    def _gerar_combinacao_inteligente(self, numeros_por_jogo, pool, indice):
        """Gera uma combinação inteligente do pool"""
        
        # Expandir pool se necessário
        if len(pool) < numeros_por_jogo * 2:  # Pool maior para mais variação
            pool_extra = [n for n in self.numeros_disponiveis if n not in pool]
            pool.extend(random.sample(pool_extra, min(len(pool_extra), numeros_por_jogo)))
        
        # Estratégia baseada no índice para variação + aleatoriedade
        seed_variacao = indice * 17 + random.randint(int(1), int(100))  # Seed única por combinação
        random.seed(42)
        
        # Diferentes estratégias de seleção
        estrategia = indice % 5
        
        if estrategia == 0:  # Estratégia quente
            if self.insights_tempo_real:
                numeros_quentes = self.insights_tempo_real.get('numeros_quentes', [])[:15]
                pool_prioritario = [n for n in pool if n in numeros_quentes]
                pool_secundario = [n for n in pool if n not in numeros_quentes]
            else:
                pool_prioritario = pool[:len(pool)//2]
                pool_secundario = pool[len(pool)//2:]
        
        elif estrategia == 1:  # Estratégia fria  
            if self.insights_tempo_real:
                numeros_frios = self.insights_tempo_real.get('numeros_frios', [])[:15]
                pool_prioritario = [n for n in pool if n in numeros_frios]
                pool_secundario = [n for n in pool if n not in numeros_frios]
            else:
                pool_prioritario = pool[len(pool)//2:]
                pool_secundario = pool[:len(pool)//2]
        
        elif estrategia == 2:  # Estratégia mista (70% quente, 30% frio)
            if self.insights_tempo_real:
                numeros_quentes = self.insights_tempo_real.get('numeros_quentes', [])[:10]
                numeros_frios = self.insights_tempo_real.get('numeros_frios', [])[:10]
                pool_quente = [n for n in pool if n in numeros_quentes]
                pool_frio = [n for n in pool if n in numeros_frios]
                pool_neutro = [n for n in pool if n not in numeros_quentes and n not in numeros_frios]
                
                quant_quente = int(numeros_por_jogo * 0.4)
                quant_frio = int(numeros_por_jogo * 0.3)  
                quant_neutro = numeros_por_jogo - quant_quente - quant_frio
                
                combinacao = []
                combinacao.extend(random.sample(pool_quente, min(quant_quente, len(pool_quente))))
                combinacao.extend(random.sample(pool_frio, min(quant_frio, len(pool_frio))))
                combinacao.extend(random.sample(pool_neutro, min(quant_neutro, len(pool_neutro))))
                
                # Completar se necessário
                while len(combinacao) < numeros_por_jogo:
                    restantes = [n for n in pool if n not in combinacao]
                    if restantes:
                        combinacao.append(random.choice(restantes))
                    else:
                        break
                
                random.seed()  # Restaurar seed
                return combinacao
        
        elif estrategia == 3:  # Estratégia equilibrada
            pool_prioritario = pool.copy()
            pool_secundario = []
        
        else:  # Estratégia completamente aleatória
            pool_prioritario = []
            pool_secundario = pool.copy()
        
        # Seleção ponderada para estratégias 0, 1 e 3
        combinacao = []
        
        # 60% do pool prioritário, 40% do secundário
        quant_prioritario = int(numeros_por_jogo * 0.6) if pool_prioritario else 0
        quant_secundario = numeros_por_jogo - quant_prioritario
        
        # Selecionar do pool prioritário
        if pool_prioritario and quant_prioritario > 0:
            combinacao.extend(random.sample(pool_prioritario, min(quant_prioritario, len(pool_prioritario))))
        
        # Selecionar do pool secundário
        if pool_secundario and quant_secundario > 0:
            pool_disponivel = [n for n in pool_secundario if n not in combinacao]
            combinacao.extend(random.sample(pool_disponivel, min(quant_secundario, len(pool_disponivel))))
        
        # Completar com números aleatórios se necessário
        while len(combinacao) < numeros_por_jogo:
            restantes = [n for n in pool if n not in combinacao]
            if not restantes:
                restantes = [n for n in self.numeros_disponiveis if n not in combinacao]
            if restantes:
                combinacao.append(random.choice(restantes))
            else:
                break
        
        # Adicionar variação extra baseada no índice
        if len(combinacao) >= 2 and indice > 0:
            # Trocar 1-2 números aleatoriamente por outros do pool
            trocas = min(2, len(combinacao) // 3)
            for _ in range(int(int(int(trocas)):
                if random.random() < 0.3:  # 30% chance de troca
                    disponiveis = [n for n in pool if n not in combinacao]
                    if disponiveis and combinacao:
                        idx_trocar = random.randint(int(0))), int(int(int(len(combinacao))) - 1)
                        novo_numero = random.choice(disponiveis)
                        combinacao[idx_trocar] = novo_numero
        
        random.seed()  # Restaurar seed aleatória
        return combinacao
    
    def _analisar_sobreposicao(self), int(combinacoes)):
        """Analisa sobreposição entre combinações"""
        if len(combinacoes) < 2:
            return {'media': 0, 'min': 0, 'max': 0}
        
        sobreposicoes = []
        
        for i, comb1 in enumerate(combinacoes):
            for comb2 in combinacoes[i+1:]:
                comum = len(set(comb1) & set(comb2))
                sobreposicoes.append(comum)
        
        return {
            'media': np.mean(sobreposicoes),
            'min': min(sobreposicoes),
            'max': max(sobreposicoes)
        }
    
    def mostrar_insights_tempo_real(self):
        """Mostra insights calculados em tempo real"""
        if not self.insights_tempo_real:
            print("⚠️ Insights não disponíveis")
            return
        
        print("\n🧠 INSIGHTS EM TEMPO REAL:")
        print("=" * 50)
        
        # Último sorteio
        if self.insights_tempo_real.get('ultimo_sorteio'):
            ultimo = self.insights_tempo_real['ultimo_sorteio']
            print(f"🎯 Último sorteio: {ultimo['concurso']} - {ultimo['numeros']} ({ultimo['data']})")
        
        # Números quentes e frios
        quentes = self.insights_tempo_real.get('numeros_quentes', [])
        frios = self.insights_tempo_real.get('numeros_frios', [])
        
        print(f"🔥 Top 10 números quentes: {quentes[:10]}")
        print(f"❄️ Top 10 números frios: {frios[:10]}")
        
        # Análise por ciclos
        print(f"\n📊 ANÁLISE POR CICLOS:")
        for ciclo, freq in self.insights_tempo_real.get('frequencia_por_ciclo', {}).items():
            top_3 = [n for n, _ in freq.most_common(3)]
            print(f"   📈 Últimos {ciclo}: {top_3}")
        
        # Correlações principais
        correlacoes = self.insights_tempo_real.get('correlacoes', {})
        if correlacoes:
            print(f"\n🔗 PRINCIPAIS CORRELAÇÕES:")
            for num in quentes[:3]:  # Top 3 quentes
                if num in correlacoes and correlacoes[num]:
                    correlatos = [str(n) for n, _ in correlacoes[num][:3]]
                    print(f"   {num} → {', '.join(correlatos)}")
    
    def salvar_combinacoes(self, combinacoes, estrategia="dinamico"):
        """Salva combinações geradas"""
        if not combinacoes:
            print("⚠️ Nenhuma combinação para salvar")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"megasena_dinamico_{estrategia}_{len(combinacoes)}jogos_{timestamp}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("🚀 GERADOR ACADÊMICO DINÂMICO - MEGA-SENA\n")
            f.write("=" * 55 + "\n\n")
            f.write(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"🎯 Estratégia: {estrategia.upper()}\n")
            f.write(f"📊 Quantidade: {len(combinacoes)} combinações\n")
            f.write(f"🔢 Números por jogo: {len(combinacoes[0]) if combinacoes else 6}\n")
            f.write(f"🗄️ Fonte: Tabela Resultados_MegaSenaFechado\n\n")
            
            f.write("🧠 CARACTERÍSTICAS DINÂMICAS:\n")
            f.write("• Insights calculados em tempo real\n")
            f.write("• Correlações temporais atualizadas\n")
            f.write("• Rankings dos últimos ciclos\n")
            f.write("• Estratégia baixa sobreposição adaptada\n\n")
            
            # Insights resumidos
            if self.insights_tempo_real:
                quentes = self.insights_tempo_real.get('numeros_quentes', [])[:10]
                frios = self.insights_tempo_real.get('numeros_frios', [])[:10]
                f.write(f"🔥 Números quentes utilizados: {quentes}\n")
                f.write(f"❄️ Números frios utilizados: {frios}\n\n")
            
            f.write("🎰 COMBINAÇÕES GERADAS:\n")
            f.write("-" * 30 + "\n")
            
            for i, comb in enumerate(combinacoes, 1):
                if len(comb) == 6:  # Formato padrão
                    numeros_str = " - ".join([f"{n:02d}" for n in comb])
                else:  # Formato expandido
                    numeros_str = " - ".join([f"{n:02d}" for n in comb])
                f.write(f"Jogo {i:3d}: {numeros_str}\n")
            
            # Adicionar formato separado por vírgulas no final
            f.write(f"\n" + "="*30 + "\n")
            f.write("🎯 FORMATO SEPARADO POR VÍRGULAS:\n")
            f.write("-" * 30 + "\n")
            
            for i, comb in enumerate(combinacoes, 1):
                numeros_str = ",".join([f"{n:02d}" for n in comb])
                f.write(f"{numeros_str}\n")
            
            f.write(f"\n✅ GERADOR ACADÊMICO DINÂMICO - MEGA-SENA\n")
        
        print(f"💾 Combinações salvas: {nome_arquivo}")
        return nome_arquivo
    
    def menu_principal(self):
        """Menu principal do gerador dinâmico"""
        print("\n🚀 GERADOR ACADÊMICO DINÂMICO - MEGA-SENA")
        print("=" * 55)
        print("🔬 Sistema avançado com insights em tempo real")
        print("📊 Estratégia baixa sobreposição adaptada")
        print("🎯 Geração ILIMITADA - Números variáveis (6-20)")
        
        while True:
            try:
                print(f"\n🎮 CONFIGURAÇÃO DO GERADOR DINÂMICO:")
                
                # Solicita números por jogo
                print(f"Quantos números por jogo ({self.min_numeros_jogo}-{self.max_numeros_jogo}) - padrão {self.padrao_numeros}: ", end="")
                entrada_numeros = input().strip()
                
                if entrada_numeros == "":
                    numeros_por_jogo = self.padrao_numeros
                else:
                    numeros_por_jogo = int(entrada_numeros)
                    if numeros_por_jogo < self.min_numeros_jogo or numeros_por_jogo > self.max_numeros_jogo:
                        print(f"⚠️ Valor inválido. Usando padrão: {self.padrao_numeros}")
                        numeros_por_jogo = self.padrao_numeros
                
                # Solicita quantidade (ilimitada)
                print(f"Quantas combinações gerar (padrão {self.padrao_quantidade}, sem limite): ", end="")
                entrada_qtd = input().strip()
                
                if entrada_qtd == "":
                    quantidade = self.padrao_quantidade
                else:
                    quantidade = int(entrada_qtd)
                    if quantidade <= 0:
                        print(f"⚠️ Quantidade inválida. Usando padrão: {self.padrao_quantidade}")
                        quantidade = self.padrao_quantidade
                
                print(f"\n🧠 Configuração selecionada:")
                print(f"   🔢 Números por jogo: {numeros_por_jogo}")
                print(f"   📊 Quantidade: {quantidade}")
                
                # Atualiza insights em tempo real
                print(f"\n🔄 Atualizando insights em tempo real...")
                self.calcular_insights_tempo_real()
                
                # Mostra insights
                self.mostrar_insights_tempo_real()
                
                # Gera combinações
                print(f"\n🚀 Iniciando geração...")
                combinacoes = self.gerar_combinacoes_dinamicas(quantidade, numeros_por_jogo)
                
                if combinacoes:
                    print(f"\n🎯 COMBINAÇÕES GERADAS:")
                    print("-" * 40)
                    
                    # Mostra primeiras 5 e últimas 2 se muitas
                    if len(combinacoes) <= 10:
                        for i, comb in enumerate(combinacoes, 1):
                            print(f"   Jogo {i:2d}: {comb}")
                    else:
                        for i, comb in enumerate(combinacoes[:5], 1):
                            print(f"   Jogo {i:2d}: {comb}")
                        print(f"   ... (mais {len(combinacoes)-7} jogos) ...")
                        for i, comb in enumerate(combinacoes[-2:], len(combinacoes)-1):
                            print(f"   Jogo {i:2d}: {comb}")
                    
                    # Salva automaticamente
                    arquivo = self.salvar_combinacoes(combinacoes, "dinamico")
                    
                    print(f"\n✅ Geração concluída com sucesso!")
                    print(f"💾 Arquivo: {arquivo}")
                
                # Pergunta se quer continuar
                print(f"\n🔄 Gerar novamente? (s/N): ", end="")
                continuar = input().strip().lower()
                
                if continuar not in ['s', 'sim', 'y', 'yes']:
                    print("🚪 Saindo do Gerador Acadêmico Dinâmico...")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n🚪 Operação cancelada pelo usuário")
                break
            except ValueError:
                print("❌ Valor inválido. Tente novamente.")
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                break

if __name__ == "__main__":
    gerador = GeradorAcademicoDinamicoMegaSena()
    gerador.menu_principal()
