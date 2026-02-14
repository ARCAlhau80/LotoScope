#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 INTERFACE DE SELEÇÃO INTERATIVA V4.0
=======================================
Interface amigável para o Sistema de Análise Escalonada Inteligente.
Permite configurar filtros, escolher TOP combinações e ver análises detalhadas.

Autor: AR CALHAU
Data: 18/09/2025
"""

import sys
import os
from pathlib import Path

# Adicionar diretório base ao path para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'validadores'))

from sistema_filtro_redutor_v4 import SistemaFiltroRedutorV4
from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import datetime

class InterfaceSistemaV4:
    """Interface interativa para o Sistema de Análise Escalonada V4.0"""
    
    def __init__(self):
        self.sistema = SistemaFiltroRedutorV4()
        self.resultados_cache = None
        
    def exibir_cabecalho(self):
        """Exibe cabeçalho do sistema"""
        print("🚀 SISTEMA DE ANÁLISE ESCALONADA INTELIGENTE V4.0")
        print("=" * 70)
        print("🎯 3 FASES: Filtro Redutor → Análise Neural → Ranking Inteligente")
        print("💡 Conceito: De 3,2 milhões para TOP combinações ordenadas!")
        print("=" * 70)
    
    def menu_configuracao(self):
        """Menu de configuração do filtro"""
        print("\n🔧 CONFIGURAÇÃO DO FILTRO REDUTOR")
        print("-" * 40)
        
        # Nível de restrição
        print("📊 NÍVEL DE RESTRIÇÃO (1-10):")
        print("   1-3: Muito restritivo (menos combinações, mais precisão)")
        print("   4-6: Moderado (equilíbrio)")
        print("   7-10: Flexível (mais combinações, mais cobertura)")
        
        while True:
            try:
                nivel = int(input("\n🎯 Escolha o nível (1-10): "))
                if 1 <= nivel <= 10:
                    break
                else:
                    print("❌ Nível deve ser entre 1 e 10!")
            except ValueError:
                print("❌ Digite um número válido!")
        
        # Máximo de combinações para análise
        print(f"\n📈 MÁXIMO DE COMBINAÇÕES PARA ANÁLISE:")
        print("   Recomendado: 500-1000 (boa precisão + velocidade)")
        print("   Máximo: 5000 (análise mais demorada)")
        
        while True:
            try:
                max_comb = int(input("\n🔢 Máximo de combinações (100-5000): "))
                if 100 <= max_comb <= 5000:
                    break
                else:
                    print("❌ Valor deve ser entre 100 e 5000!")
            except ValueError:
                print("❌ Digite um número válido!")
        
        return nivel, max_comb
    
    def executar_analise_completa(self, nivel, max_combinacoes):
        """Executa análise completa e armazena resultados"""
        print(f"\n🚀 EXECUTANDO ANÁLISE COMPLETA...")
        print("=" * 50)
        
        # Executar sistema com TOP 50 para ter opções
        self.resultados_cache = self.sistema.executar_sistema_completo(
            nivel_restricao=nivel,
            max_combinacoes=max_combinacoes,
            top_selecionar=50
        )
        
        if not self.resultados_cache:
            print("❌ Nenhum resultado encontrado! Tente nível menos restritivo.")
            return False
            
        print(f"\n✅ ANÁLISE CONCLUÍDA!")
        print(f"🎯 {len(self.resultados_cache)} combinações analisadas e ordenadas")
        return True
    
    def menu_selecao_top(self):
        """Menu para seleção de TOP combinações"""
        if not self.resultados_cache:
            print("❌ Execute a análise primeiro!")
            return
            
        print(f"\n🏆 SELEÇÃO DE TOP COMBINAÇÕES")
        print("-" * 40)
        print(f"📊 Disponíveis: TOP 1 até TOP {len(self.resultados_cache)}")
        
        # Mostrar preview das TOP 5
        print(f"\n📋 PREVIEW - TOP 5:")
        for i in range(min(5, len(self.resultados_cache))):
            resultado = self.resultados_cache[i]
            numeros_str = " ".join([f"{n:2d}" for n in resultado['combinacao']])
            print(f"   #{i+1} | Score: {resultado['score']:5.1f}% | [{numeros_str}]")
        
        while True:
            try:
                top_escolhido = int(input(f"\n🎯 Quantas TOP combinações usar (1-{len(self.resultados_cache)}): "))
                if 1 <= top_escolhido <= len(self.resultados_cache):
                    break
                else:
                    print(f"❌ Valor deve ser entre 1 e {len(self.resultados_cache)}!")
            except ValueError:
                print("❌ Digite um número válido!")
        
        return top_escolhido
    
    def exibir_resultados_detalhados(self, top_quantidade):
        """Exibe resultados detalhados das TOP combinações"""
        print(f"\n🏆 TOP {top_quantidade} COMBINAÇÕES SELECIONADAS")
        print("=" * 80)
        
        combinacoes_selecionadas = self.resultados_cache[:top_quantidade]
        
        for i, resultado in enumerate(combinacoes_selecionadas, 1):
            numeros = resultado['combinacao']
            score = resultado['score']
            detalhes = resultado['detalhes']
            
            numeros_str = " ".join([f"{n:2d}" for n in numeros])
            
            print(f"\n🥇 #{i:2d} | SCORE: {score:5.1f}%")
            print(f"🎯 COMBINAÇÃO: [{numeros_str}]")
            print(f"📊 ANÁLISE:")
            print(f"   • Primos: {detalhes['primos']}/15")
            print(f"   • Soma: {detalhes['soma']} (ideal: 180-220)")
            print(f"   • Sequências: {detalhes['sequencias']}")
            print(f"   • Gap médio: {detalhes['gap_medio']:.1f}")
            print(f"   • Extremos: {detalhes['extremos']} (ideal: 20-24)")
            
            # Análise de probabilidade
            prob_individual = 1 / 3268760
            prob_melhorada = score / 100 * 0.01  # Estimativa baseada no score
            melhoria = prob_melhorada / prob_individual
            
            print(f"📈 PROBABILIDADE ESTIMADA:")
            print(f"   • Normal: {prob_individual:.8f} (1/{3268760:,})")
            print(f"   • Melhorada: {prob_melhorada:.8f} ({melhoria:.1f}x melhor)")
            
            if i <= 3:  # Destaque para TOP 3
                print(f"⭐ DESTAQUE TOP {i}!")
            
            print("-" * 80)
    
    def salvar_resultados(self, top_quantidade):
        """Salva resultados em arquivo"""
        if not self.resultados_cache:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"top_combinacoes_v4_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("🚀 SISTEMA DE ANÁLISE ESCALONADA INTELIGENTE V4.0\n")
                f.write("=" * 70 + "\n")
                f.write(f"⏰ Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"🎯 TOP {top_quantidade} Combinações Selecionadas\n")
                f.write("=" * 70 + "\n\n")
                
                # Seção detalhada
                f.write("📋 ANÁLISE DETALHADA:\n")
                f.write("-" * 50 + "\n")
                for i, resultado in enumerate(self.resultados_cache[:top_quantidade], 1):
                    numeros = resultado['combinacao']
                    score = resultado['score']
                    detalhes = resultado['detalhes']
                    
                    numeros_str = " ".join([f"{n:2d}" for n in numeros])
                    
                    f.write(f"#{i:2d} | Score: {score:5.1f}% | [{numeros_str}]\n")
                    f.write(f"     Primos:{detalhes['primos']} Soma:{detalhes['soma']} ")
                    f.write(f"Seq:{detalhes['sequencias']} Gap:{detalhes['gap_medio']:.1f} ")
                    f.write(f"Extremos:{detalhes['extremos']}\n\n")
                
                # ✨ SEÇÃO ESPECIAL: COMBINAÇÕES APENAS COM VÍRGULAS
                f.write("\n" + "🗝️" * 20 + " CHAVE DE OURO " + "🗝️" * 20 + "\n")
                f.write("COMBINAÇÕES TOP PARA JOGAR (formato vírgula):\n")
                f.write("-" * 60 + "\n")
                
                for resultado in self.resultados_cache[:top_quantidade]:
                    numeros = resultado['combinacao']
                    f.write(f"{','.join(map(str, numeros))}\n")
                
                f.write("\n" + "🗝️" * 55 + "\n")
                f.write(f"📊 Total: {top_quantidade} combinações TOP selecionadas\n")
                f.write("💡 Use estas combinações diretamente para seus jogos!\n")
            
            print(f"✅ Resultados salvos em: {filename}")
            print(f"🗝️ CHAVE DE OURO incluída: Combinações apenas com vírgulas!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
    
    def menu_opcoes_finais(self, top_quantidade):
        """Menu de opções finais"""
        while True:
            print(f"\n🎮 OPÇÕES:")
            print("1. 💾 Salvar resultados completos em arquivo")
            print("2. �️ Salvar APENAS combinações (formato vírgula)")
            print("3. �🔄 Nova análise com configurações diferentes")
            print("4. 📊 Ver estatísticas resumidas")
            print("5. 🚪 Sair")
            
            opcao = input("\n👉 Escolha uma opção (1-5): ").strip()
            
            if opcao == "1":
                self.salvar_resultados(top_quantidade)
            elif opcao == "2":
                self.salvar_apenas_combinacoes(top_quantidade)
            elif opcao == "3":
                return "nova_analise"
            elif opcao == "4":
                self.exibir_estatisticas_resumidas(top_quantidade)
            elif opcao == "5":
                return "sair"
            else:
                print("❌ Opção inválida!")
    
    def salvar_apenas_combinacoes(self, top_quantidade):
        """Salva apenas as combinações em formato vírgula"""
        if not self.resultados_cache:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"combinacoes_puras_v4_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# TOP {top_quantidade} COMBINAÇÕES - SISTEMA V4.0\n")
                f.write(f"# Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"# Formato: número,número,número...\n")
                f.write("#" + "="*50 + "\n")
                
                for resultado in self.resultados_cache[:top_quantidade]:
                    numeros = resultado['combinacao']
                    f.write(f"{','.join(map(str, numeros))}\n")
            
            print(f"✅ Combinações puras salvas em: {filename}")
            print(f"🎯 {top_quantidade} combinações no formato vírgula prontas para uso!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
    
    def exibir_estatisticas_resumidas(self, top_quantidade):
        """Exibe estatísticas resumidas"""
        if not self.resultados_cache:
            return
            
        print(f"\n📊 ESTATÍSTICAS RESUMIDAS - TOP {top_quantidade}")
        print("=" * 50)
        
        combinacoes = self.resultados_cache[:top_quantidade]
        
        # Scores
        scores = [r['score'] for r in combinacoes]
        score_medio = sum(scores) / len(scores)
        melhor_score = max(scores)
        pior_score = min(scores)
        
        print(f"🎯 SCORES:")
        print(f"   • Melhor: {melhor_score:.1f}%")
        print(f"   • Pior: {pior_score:.1f}%")
        print(f"   • Média: {score_medio:.1f}%")
        
        # Análise de somas
        somas = [r['detalhes']['soma'] for r in combinacoes]
        soma_media = sum(somas) / len(somas)
        
        print(f"\n📈 SOMAS:")
        print(f"   • Média: {soma_media:.1f}")
        print(f"   • Faixa: {min(somas)} - {max(somas)}")
        
        # Análise de primos
        primos = [r['detalhes']['primos'] for r in combinacoes]
        primos_medio = sum(primos) / len(primos)
        
        print(f"\n🔢 PRIMOS:")
        print(f"   • Média: {primos_medio:.1f}")
        print(f"   • Faixa: {min(primos)} - {max(primos)}")
        
        print(f"\n💡 RECOMENDAÇÃO:")
        print(f"   Use as TOP 5-10 combinações para maximizar chances!")
    
    def executar_interface(self):
        """Executa interface completa"""
        self.exibir_cabecalho()
        
        while True:
            # Configuração
            nivel, max_comb = self.menu_configuracao()
            
            # Análise completa
            if not self.executar_analise_completa(nivel, max_comb):
                continue
            
            # Seleção de TOP
            top_quantidade = self.menu_selecao_top()
            
            # Resultados detalhados
            self.exibir_resultados_detalhados(top_quantidade)
            
            # Opções finais
            acao = self.menu_opcoes_finais(top_quantidade)
            
            if acao == "sair":
                break
            elif acao == "nova_analise":
                continue
        
        print("\n🎯 Obrigado por usar o Sistema de Análise Escalonada V4.0!")
        print("🚀 Boa sorte com suas combinações inteligentes!")

if __name__ == "__main__":
    interface = InterfaceSistemaV4()
    interface.executar_interface()